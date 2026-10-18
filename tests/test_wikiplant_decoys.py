import json
import random
import re

import pytest

from wikiplant.corpus import apply_manifest
from wikiplant.decoys import contradicts, make_units, new_name, plan, ratio_report, similar_name
from wikiplant.design import TIERS
from wikiplant.names import Registry
from wikiplant.schemas import validate_manifest_entry
from wikiplant.writing import Ledger, WriterPool

FILLER = "the works stood beside the canal and employed men from the surrounding valley towns for many years".split()


def corpus(n=24):
    paras, pages = [], {}
    for i in range(1, n + 1):
        t = f"Mill town {i}"
        pages[i] = {"title": t, "infobox": {}, "views": 100}
        paras.append({"para_id": f"{i}::0", "page_id": i, "title": t, "section_path": [], "para_idx": 0,
                      "text": f"{t} is a town with mills and a railway station opened in 18{40 + i % 50}.", "outlinks": []})
        for s in ("History", "Industry", "Transport"):
            for k in range(2):
                paras.append({"para_id": f"{i}:{s}:{k}", "page_id": i, "title": t, "section_path": [s], "para_idx": k,
                              "text": " ".join(FILLER[(j + k) % len(FILLER)] for j in range(60)), "outlinks": []})
    return paras, pages


PUZZLE = {
    "pid": "p1", "template": "chain",
    "entities": [
        {"eid": "e1", "name": "Mill town 1", "invented": False},
        {"eid": "e2", "name": "Threlfall and Ormerod", "invented": True},
        {"eid": "e3", "name": "Mill town 2", "invented": False},
    ],
    "facts": [
        {"fid": "f0", "s": "e1", "r": "linked_to", "o": "e3", "planted": False, "para_id": "1:History:0"},
        {"fid": "f1", "s": "e2", "r": "supplied_locomotives_to", "o": "e3", "planted": True, "host_page": 2, "when": 1852},
    ],
    "path": ["f0", "f1"], "question": "?", "answer": "1852", "aliases": [],
}


def echo_writer():
    """Stub writer: restates the fact sentence from the prompt, padded to the requested length."""
    def model(prompt):
        fact = re.search(r"State this fact plainly: (.+)", prompt).group(1).strip()
        n = int(re.search(r"about (\d+) words", prompt).group(1))
        words = fact.rstrip(".").replace("_", " ").split() + ["and"]
        text = " ".join(words + [FILLER[i % len(FILLER)] for i in range(max(0, n - len(words)))]) + "."
        reply = {"text": text, "claims": [{"s": "x", "r": "y", "o": "z"}]}
        if "NEW subsection" in prompt:
            reply["heading"] = "Later works"
        return json.dumps(reply)
    return model


@pytest.fixture
def made():
    paras, pages = corpus()
    reg = Registry(max_name=1, max_part=50)
    reg.add("Threlfall and Ormerod")
    counts = {"decoy": 4, "near_miss": 1, "partial_echo": 1}
    entries, log = make_units(PUZZLE, paras, pages, set(range(1, 25)), set(range(1, 9)),
                              WriterPool({"w1": echo_writer(), "w2": echo_writer()}), Ledger(), random.Random(3),
                              registry=reg, counts=counts)
    return paras, entries, log


def test_all_roles_are_written_and_valid(made):
    paras, entries, log = made
    roles = [e["role"] for e in entries]
    assert roles.count("decoy") == 4 and roles.count("near_miss") == 1 and roles.count("partial_echo") == 1, log
    assert all(validate_manifest_entry(e) == [] for e in entries)
    assert len({e["unit_id"] for e in entries}) == len(entries)
    assert {e["generator"]["model"] for e in entries} <= {"w1", "w2"}
    built, units = apply_manifest(paras, entries, "full")
    assert len(units) == len(entries)


def test_near_miss_is_similar_off_path_and_different(made):
    _, entries, _ = made
    nm_ = next(e for e in entries if e["role"] == "near_miss")
    assert nm_["host_page"] not in {1, 2} and nm_["host_page"] <= 8          # off path, in cluster
    assert ("Threlfall" in nm_["fact"]["s"] or "Ormerod" in nm_["fact"]["s"]) and nm_["fact"]["s"] != "Threlfall and Ormerod"
    assert nm_["fact"]["r"] == "supplied_locomotives_to" and nm_["fact"]["when"] != 1852


def test_echo_names_the_bridge_without_the_answer(made):
    _, entries, _ = made
    echo = next(e for e in entries if e["role"] == "partial_echo")
    assert "Threlfall and Ormerod" in echo["text"] and "1852" not in echo["text"]


def test_no_unit_mentions_the_answer_and_density_holds(made):
    _, entries, _ = made
    assert not any(re.search(r"\b1852\b", e["text"]) for e in entries)
    pages = [e["host_page"] for e in entries]
    assert len(pages) == len(set(pages))     # one non-gold unit per page
    assert not any("Threlfall and Ormerod" in e["text"] for e in entries if e["role"] == "decoy")


def test_contradiction_guard():
    ents = {e["eid"]: e for e in PUZZLE["entities"]}
    gold = [PUZZLE["facts"][1]]
    assert contradicts({**gold[0], "when": 1860}, gold, ents)
    assert not contradicts({**gold[0], "r": "advertised_in"}, gold, ents)
    assert not contradicts(dict(gold[0]), gold, ents)


def test_plan_follows_ratios_and_tiers():
    rng = random.Random(0)
    for tier in ("easy", "medium", "hard"):
        c = plan(PUZZLE, TIERS[tier], rng)
        assert 3 <= c["decoy"] <= 5 and c["partial_echo"] in (0, 1)
        assert c["near_miss"] == min(TIERS[tier]["near_misses"], 2)


def test_names_are_unique_and_similar_names_share_a_part():
    rng, reg = random.Random(1), Registry(max_name=1, max_part=100)
    names = {new_name("firm", rng, registry=reg) for _ in range(20)}
    assert len(names) == 20
    s = similar_name("Threlfall and Ormerod", rng)
    assert ("Threlfall" in s or "Ormerod" in s) and s != "Threlfall and Ormerod"


def test_ratio_report():
    m = [{"role": "gold"}] * 2 + [{"role": "decoy"}] * 7 + [{"role": "near_miss"}]
    assert ratio_report(m) == {"by_role": {"gold": 2, "decoy": 7, "near_miss": 1}, "decoys_per_gold": 3.5}
