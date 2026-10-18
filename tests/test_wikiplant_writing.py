import json
import random
import re
from pathlib import Path

import pytest

from wikiplant.corpus import apply_manifest, load_pages
from wikiplant.parse import snapshot
from wikiplant.schemas import validate_manifest_entry
from wikiplant.writing import (Ledger, WriterPool, choose_placement, conventions, lint, normalize_text,
                               pick_the_planted, plant_fact, rank_hosts, rank_hosts_lexical, style_classifier)

SAMPLE = Path(__file__).resolve().parents[1] / "wikiplant" / "sample"
ENTS = {"e2": {"name": "Threlfall and Ormerod"}, "e3": {"name": "Dunmere Valley Railway"}}
FACT = {"fid": "f1", "s": "e2", "r": "supplied_locomotives_to", "o": "e3", "planted": True, "when": 1852}
FILLER = "the company kept its works beside the canal and employed men from the surrounding valley towns".split()


@pytest.fixture(scope="module")
def paras():
    return snapshot(SAMPLE / "dump.xml", "2026-10-01")[1]


def writer(heading="Locomotive suppliers", bad_first=False):
    """Stub writer: obeys the length in the prompt and states the required facts."""
    calls = []

    def model(prompt):
        calls.append(prompt)
        n = int(re.search(r"about (\d+) words", prompt).group(1))
        lead = "Threlfall and Ormerod supplied the first locomotives in 1852, and"
        if bad_first and len(calls) == 1:
            lead = "Notably, Threlfall and Ormerod played a pivotal role in 1852, and"
        words = lead.split()
        text = " ".join(words + [FILLER[i % len(FILLER)] for i in range(max(0, n - len(words)))]) + "."
        reply = {"text": text, "claims": [{"s": "Threlfall and Ormerod", "r": "supplied", "o": "Dunmere Valley Railway", "when": 1852}]}
        if "NEW subsection" in prompt:
            reply["heading"] = heading
        return json.dumps(reply)
    model.calls = calls
    return model


def test_conventions_detect_spelling_dates_and_heading_case():
    brit = [{"text": "The harbour was authorised on 3 March 1851 by the centre.", "section_path": ["Early history"]}]
    amer = [{"text": "The harbor was authorized on March 3, 1851, near the center.", "section_path": ["Early History"]}]
    assert conventions(brit)["spelling"] == "British" and conventions(brit)["dates"] == "day month year"
    assert conventions(brit)["heading_case"] == "sentence"
    c = conventions(amer)
    assert c["spelling"] == "American" and c["dates"] == "month day, year" and c["heading_case"] == "title"


def test_normalize_matches_host_formatting():
    conv = {"spelling": "British"}
    assert normalize_text("The “Color” Works—built 1851-62 for labor.", conv) == 'The "Colour" Works – built 1851–62 for labour.'
    assert normalize_text("The centre", {"spelling": "American"}) == "The center"


@pytest.mark.parametrize("text,expect", [
    ("Notably, the firm grew.", "blocklisted"),
    ("The firm stands as a testament to industry.", "blocklisted"),
    ("The firm grew.[3]", "citations"),
])
def test_lint_catches_tells(text, expect):
    assert any(expect in e for e in lint(text, len(text.split())))


def test_lint_length_mentions_and_headings():
    assert any("words, target" in e for e in lint("short text", 100))
    assert any("does not state" in e for e in lint("a b c", 3, must_mention=[1852]))
    conv = {"heading_case": "sentence"}
    assert any("sentence case" in e for e in lint("a b c", 3, heading="Locomotive Suppliers", conv=conv))
    assert any("already exists" in e for e in lint("a b c", 3, heading="History", existing_headings={"History"}))
    assert lint("a b c", 3, heading="Locomotive suppliers", conv=conv) == []


def test_lexical_ranker_skips_the_lead_and_prefers_topical_sections(paras):
    pages = load_pages(paras)
    ranked = rank_hosts_lexical("locomotives rolling stock built by small local firms", pages, [101, 102, 103])
    assert ranked[0] == (102, ["Operations", "Rolling stock"])
    assert all(sp for _, sp in ranked)


def test_model_ranker_drops_invalid_choices(paras):
    pages = load_pages(paras)
    reply = {"ranked": [{"page_id": 999, "section": "History"}, {"page_id": 101, "section": "Nope"},
                        {"page_id": 102, "section": "Operations/Rolling stock"}]}
    assert rank_hosts("x", pages, {101, 102}, lambda p: json.dumps(reply)) == [(102, ["Operations", "Rolling stock"])]


def test_placement_modes_and_positions(paras):
    page = load_pages(paras)[101]
    rng = random.Random(0)
    seen = [choose_placement(page, ["History"], rng) for _ in range(200)]
    share = sum(p["mode"] == "subsection" for p in seen) / len(seen)
    assert 0.2 < share < 0.4
    assert {p["position"] for p in seen if p["mode"] == "paragraph"} == {0, 1, 2}
    with pytest.raises(ValueError):
        choose_placement(page, [], rng)


def test_ledger_caps_density():
    led = Ledger()
    led.take(101, "gold")
    assert not led.free(101, "gold") and led.free(101, "decoy")
    led.take(101, "near_miss")
    assert not led.free(101, "decoy")


def test_writer_pool_is_deterministic():
    pool = WriterPool({"a": None, "b": None, "c": None})
    assert pool.pick("u001") == pool.pick("u001")
    assert len({pool.pick(f"u{i:03d}")[0] for i in range(30)}) == 3


def test_plant_fact_end_to_end_builds_a_valid_manifest_entry(paras):
    model = writer(bad_first=True)
    pool, led = WriterPool({"stub-a": model}), Ledger()
    logs = []
    for seed in range(20):   # cover both placement modes
        entry, log = plant_fact(f"u{seed}", FACT, ENTS, paras, [101, 102, 103], pool, Ledger(), random.Random(seed))
        assert entry is not None, log
        logs.append(log)
        assert validate_manifest_entry(entry) == []
        assert entry["generator"] == {"model": "stub-a", "prompt_version": "writer-v1"}
        built, units = apply_manifest(paras, [entry], "full")
        text, _ = built[entry["host_page"]].render()
        u = units[entry["unit_id"]]
        assert text[u["start"]:u["end"]].startswith("Threlfall and Ormerod")
    assert {lg["placement"] for lg in logs} == {"paragraph", "subsection"}
    assert any("blocklisted" in p for p in logs[0]["attempts"][0]["problems"])
    assert "failed these checks" in model.calls[1]
    entry, _ = plant_fact("g1", FACT, ENTS, paras, [102], pool, led, random.Random(1))
    assert entry and not led.free(102, "gold")
    assert plant_fact("g2", FACT, ENTS, paras, [102], pool, led, random.Random(1))[0] is None


def test_style_classifier_separates_an_obvious_writer_and_not_a_good_one():
    rng = random.Random(0)
    vocab = "the mill station railway opened closed built company town goods yard coal line years".split()
    real = [" ".join(rng.choice(vocab) for _ in range(40)) for _ in range(60)]
    good = [{"unit_id": f"g{i}", "text": " ".join(rng.choice(vocab) for _ in range(40)), "generator": {"model": "good"}} for i in range(30)]
    bad = [{"unit_id": f"b{i}", "text": "notably a testament pivotal " + " ".join(rng.choice(vocab) for _ in range(36)),
            "generator": {"model": "bad"}} for i in range(30)]
    r = style_classifier(good + bad, real)
    assert r["per_writer"]["bad"] > 0.95 and r["per_writer"]["good"] < 0.75
    assert any(u.startswith("b") for u in r["flagged"]) and not any(u.startswith("g") for u in r["flagged"])


def test_pick_the_planted_reports_chance_and_significance():
    trials = [{"title": "T", "planted": f"planted {i} notably", "real": [f"real {i} {j}" for j in range(5)]} for i in range(40)]
    oracle = lambda p: str(next(i for i, line in enumerate(p.split("\n\n")[1:-1], 1) if "notably" in line))
    blind = lambda p: "1"
    r = pick_the_planted(trials, oracle)
    assert r["accuracy"] == 1.0 and r["p_value"] < 1e-6
    r = pick_the_planted(trials, blind)
    assert r["accuracy"] < 0.5 and r["p_value"] > 0.05 and r["chance"] == 0.25


def test_lint_rejects_text_copied_from_the_host():
    src = ["Wombwell was mainly a farming area with a small population prior to the opening of Lundhill Colliery."]
    text = "In 1843 a wharf was leased. Wombwell was mainly a farming area with a small population before then."
    assert any("verbatim" in e for e in lint(text, len(text.split()), sources=src))
    assert lint("The wharf was leased in 1843 by a small company.", 10, sources=src) == []
