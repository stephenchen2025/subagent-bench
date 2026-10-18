import json
from pathlib import Path

import pytest

from wikiplant.corpus import apply_manifest
from wikiplant.index import BM25, chunk_page
from wikiplant.parse import clean_inline, parse_page, snapshot
from wikiplant.schemas import validate_manifest_entry, validate_paragraph, validate_puzzle
from wikiplant.tools import Corpus

SAMPLE = Path(__file__).resolve().parents[1] / "wikiplant" / "sample"
MANIFEST = json.loads((SAMPLE / "manifest.json").read_text())


@pytest.fixture(scope="module")
def snap():
    return snapshot(SAMPLE / "dump.xml", "2026-10-01")


def test_snapshot_drops_lists_disambiguation_and_boilerplate(snap):
    pages, paras, _ = snap
    assert set(pages) == {101, 102, 103}
    assert pages[101]["infobox"] == {"name": "Marlow Junction", "opened": "1851"}
    text = " ".join(p["text"] for p in paras)
    for leak in ("{{", "[[", "<ref", "Smith 1920", "reflist", "'''"):
        assert leak not in text
    assert not any(p["section_path"][:1] == ["See also"] for p in paras if p["section_path"])
    assert all(not validate_paragraph(p) for p in paras)


def test_sections_links_and_paragraph_ids(snap):
    _, paras, _ = snap
    by_id = {p["para_id"]: p for p in paras}
    assert "101:History/Closure:0" in by_id
    assert by_id["101:History:1"]["text"].startswith("The booking hall")
    lead = by_id["101::0"]
    assert lead["outlinks"] == ["Dunmere Valley Railway", "Marlow Bridge", "railway station"]


def test_snapshot_id_is_stable_and_sensitive(snap):
    again = snapshot(SAMPLE / "dump.xml", "2026-10-01")
    assert again[2] == snap[2]
    assert snapshot(SAMPLE / "dump.xml", "2026-11-01")[2] != snap[2]


def test_clean_inline_piped_links():
    text, links = clean_inline("The [[Dunmere|port]] and [[File:x.jpg|thumb|a [[b]] c]] ''today''")
    assert text == "The port and today" and links == ["Dunmere"]


def test_manifest_applies_deterministically_and_by_variant(snap):
    _, paras, _ = snap
    none, u0 = apply_manifest(paras, MANIFEST, "none")
    gold, u1 = apply_manifest(paras, MANIFEST, "gold")
    full, u2 = apply_manifest(paras, MANIFEST, "full")
    assert not u0 and set(u1) == {"u001"} and set(u2) == {"u001", "u002", "u003"}
    base = none[101].render()[0]
    assert "Harland and Pell" not in base
    text, _ = full[101].render()
    s = u2["u001"]
    assert text[s["start"]:s["end"]].startswith("The 1887 rebuilding")
    assert [t for t, _ in apply_manifest(paras, MANIFEST, "full")[0][101].sections] == [t for t, _ in full[101].sections]
    # the new subsection sits inside Operations, after its existing subsections
    paths = ["/".join(sp) for sp, _ in full[102].sections]
    assert paths.index("Operations/Contractors") == paths.index("Operations/Rolling stock") + 1
    # real paragraphs keep their snapshot ids around an insertion
    ids = [p["para_id"] for sp, ps in full[101].sections if sp == ["History"] for p in ps]
    assert ids == ["101:History:0", "plant:u001", "101:History:1"]
    base_ids = {p["para_id"] for pg in none.values() for _, ps in pg.sections for p in ps}
    assert base_ids == {p["para_id"] for p in paras}


@pytest.mark.parametrize("patch,err", [
    ({"role": "silver"}, "role"),
    ({"mode": "subsection"}, "heading"),
    ({"section_path": []}, "lead"),
    ({"text": " "}, "empty"),
])
def test_manifest_validation(patch, err):
    errs = validate_manifest_entry({**MANIFEST[0], **patch})
    assert any(err in e for e in errs)


def test_manifest_rejects_missing_host(snap):
    with pytest.raises(ValueError, match="not in the snapshot"):
        apply_manifest(snap[1], [{**MANIFEST[0], "host_page": 999}], "full")


def test_chunks_respect_sections_and_size(snap):
    pages, _ = apply_manifest(snap[1], MANIFEST, "full")
    for page in pages.values():
        for p in chunk_page(page):
            assert len(p["para_ids"]) >= 1
            assert len({tuple(p["section_path"])}) == 1


def test_search_finds_planted_text_and_logs_it(snap):
    c = Corpus(snap[1], MANIFEST, "full", snap[2])
    hits = c.search("who absorbed the contractor Harland and Pell", 3)
    assert hits[0]["title"] == "Marlow Junction railway station"
    assert c.surfaced() == ["u001"]
    none = Corpus(snap[1], MANIFEST, "none")
    assert not none.search("Harland Pell Cotterill")
    assert not none.units and none.gold_passages() == []
    assert c.corpus_id != none.corpus_id


def test_open_paginates_and_reports_outline(snap):
    c = Corpus(snap[1], MANIFEST, "full")
    r = c.open("marlow junction railway station", "History")
    assert "History/Closure" in r["outline"] and "Harland" in r["text"]
    assert c.open("nope")["error"]
    assert c.find_in_page("Marlow Bridge", "town hall")[0]["section_path"] == ["Landmarks"]


def test_bm25_rank_of_gold(snap):
    c = Corpus(snap[1], MANIFEST, "full")
    assert c.bm25.rank_of("Cotterill Brothers 1902", c.gold_passages()) == 1
    assert c.bm25.rank_of("zzzz", c.gold_passages()) is None


def test_puzzle_validation():
    puzzle = {
        "pid": "p1", "template": "chain",
        "entities": [{"eid": "e1", "name": "Marlow Junction"}, {"eid": "e2", "name": "X", "invented": True},
                     {"eid": "e3", "name": "Y", "invented": True}],
        "facts": [
            {"fid": "f0", "s": "e1", "r": "opened", "o": "e1", "planted": False, "para_id": "101::0"},
            {"fid": "f1", "s": "e2", "r": "built", "o": "e1", "planted": True, "host_page": 101, "unit_id": "u001"},
        ],
        "path": ["f0", "f1"], "question": "?", "answer": "1902", "aliases": [],
        "gates": {"closed_book": "pass"},
    }
    ids = {u["unit_id"] for u in MANIFEST}
    assert validate_puzzle(puzzle, ids) == []
    assert any("memory" in e for e in validate_puzzle({**puzzle, "path": ["f0"]}, ids))
    assert any("missing from the manifest" in e for e in validate_puzzle(puzzle, {"other"}))
    assert any("bad gate" in e for e in validate_puzzle({**puzzle, "gates": {"closed_book": "maybe"}}))
