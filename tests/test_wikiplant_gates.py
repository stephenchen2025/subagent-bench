import copy
import json
from pathlib import Path

import pytest

from wikiplant.gates import (Context, answer_matches, gate_lexical_shortcut, pass_rates, record_review, run_agent,
                             run_gates, shippable)
from wikiplant.parse import snapshot
from wikiplant.tools import Corpus

SAMPLE = Path(__file__).resolve().parents[1] / "wikiplant" / "sample"
MANIFEST = json.loads((SAMPLE / "manifest.json").read_text())
for u in MANIFEST:
    if u["role"] == "near_miss":
        u["puzzle"] = "p1"
        u["claims"] = [{"s": "Harland and Pell", "r": "tendered_for", "o": "Dunmere Valley Railway"}]

PUZZLE = {
    "pid": "p1", "template": "chain", "tier": "easy",
    "entities": [{"eid": "e1", "name": "Marlow Bridge", "invented": False},
                 {"eid": "e2", "name": "Harland and Pell", "invented": True},
                 {"eid": "e3", "name": "Marlow Junction railway station", "invented": False}],
    "facts": [{"fid": "f0", "s": "e3", "r": "served", "o": "e1", "planted": False, "para_id": "101:History:0"},
              {"fid": "f1", "s": "e2", "r": "rebuilt", "o": "e3", "planted": True, "host_page": 101, "unit_id": "u001"}],
    "path": ["f0", "f1"],
    "question": "A contractor rebuilt the booking hall of the station serving a cotton mill town after a fire. Which firm later took that contractor over?",
    "answer": "Cotterill Brothers", "aliases": ["Cotterill Bros"],
}


@pytest.fixture(scope="module")
def paras():
    return snapshot(SAMPLE / "dump.xml", "2026-10-01")[1]


def ctx(paras, **kw):
    return Context(paragraphs=paras, manifest=MANIFEST, samples=2, **kw)


def knows(answer):
    return lambda prompt: json.dumps({"answer": answer if "Cotterill" in prompt else "unknown", "other_defensible": []})


def test_answer_matching():
    assert answer_matches("It was Cotterill Brothers.", "Cotterill Brothers")
    assert answer_matches("cotterill bros", "Cotterill Brothers", ["Cotterill Bros"])
    assert answer_matches("in 1902", "1902") and not answer_matches("19021", "1902")
    assert not answer_matches("Cotterill", "Cotterill Brothers")


def test_lexical_shortcut_band(paras):
    p = copy.deepcopy(PUZZLE)
    r = gate_lexical_shortcut(p, ctx(paras))
    rank = r["bm25_rank"]
    assert rank is not None
    for tier, expect in (("easy", 2 <= rank <= 10), ("medium", 10 <= rank <= 100), ("hard", rank >= 100)):
        assert (gate_lexical_shortcut({**p, "tier": tier}, ctx(paras))["state"] == "pass") == expect
    leak = {**p, "question": p["question"] + " (Cotterill Brothers?)"}
    assert "contains the answer" in gate_lexical_shortcut(leak, ctx(paras))["reason"]


def test_name_collision_gate(paras):
    p = copy.deepcopy(PUZZLE)
    assert run_gates(p, ctx(paras), only={"name_collision"})["name_collision"]["state"] == "pass"
    p["entities"][1]["name"] = "Marlow Bridge"
    r = run_gates(p, ctx(paras), only={"name_collision"})["name_collision"]
    assert r["state"] == "fail" and p["return_to"] == 2


def test_closed_book(paras):
    p = copy.deepcopy(PUZZLE)
    c = ctx(paras, closed_book_models={"m1": lambda q: "1902", "m2": lambda q: "Ashworth and Sons"})
    assert run_gates(p, c, only={"closed_book"})["closed_book"]["state"] == "pass"
    c = ctx(paras, closed_book_models={"m1": lambda q: "Cotterill Brothers"})
    r = run_gates(p, c, only={"closed_book"})["closed_book"]
    assert r["state"] == "fail" and "m1#0" in r["reason"]


def test_oracle_and_distractors(paras):
    p = copy.deepcopy(PUZZLE)
    c = ctx(paras, oracle=knows("Cotterill Brothers"))
    res = run_gates(p, c, only={"oracle", "oracle_distractors"})
    assert res["oracle"]["state"] == "pass" and res["oracle_distractors"]["state"] == "pass"
    assert res["oracle_distractors"]["distractors"] >= 1           # the near-miss is in the passages
    c = ctx(paras, oracle=lambda pr: json.dumps({"answer": "Cotterill Brothers", "other_defensible": ["Ashworth and Sons"]}))
    r = run_gates(copy.deepcopy(PUZZLE), c, only={"oracle_distractors"})["oracle_distractors"]
    assert r["state"] == "fail" and "second defensible" in r["reason"]
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, oracle=knows("Harland and Pell")), only={"oracle"})["oracle"]
    assert r["state"] == "fail" and r["accuracy"] == 0


def test_consistency(paras):
    seen = []

    def judge(prompt):
        seen.append(prompt)
        bad = "Cotterill" in prompt and "1887" in prompt and "fire" in prompt
        return json.dumps({"conflicts": [{"claim": "x", "para_id": "101:History:1", "why": "test"}] if bad and len(seen) == 1 else []})
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, judge=judge), only={"consistency"})["consistency"]
    assert r["state"] == "fail" and r["conflicts"][0]["unit"] == "u001"
    assert "[101:History:1]" in seen[0]                       # host-page paragraphs are in the judge's context
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, judge=lambda pr: '{"conflicts": []}'), only={"consistency"})
    assert r["consistency"]["state"] == "pass"
    bare = [dict(u, claims=[]) if u["unit_id"] == "u003" else u for u in MANIFEST]
    r = run_gates(copy.deepcopy(PUZZLE), Context(paragraphs=paras, manifest=bare, judge=lambda pr: '{"conflicts": []}'),
                  only={"consistency"})["consistency"]
    assert r["state"] == "fail" and "no claims recorded" in r["reason"]


def scripted_agent():
    """Searches for the answer's distinctive words, answers only if a result shows them."""
    def model(prompt):
        if "RESULT" not in prompt:
            return json.dumps({"action": "search", "query": "contractor absorbed booking hall rebuilding 1887"})
        return json.dumps({"action": "answer", "answer": "Cotterill Brothers" if "Cotterill" in prompt else "UNKNOWN"})
    return model


def test_agent_loop_and_base_corpus_gate(paras):
    ans, transcript = run_agent(scripted_agent(), Corpus(paras, MANIFEST, "full"), PUZZLE["question"])
    assert ans == "Cotterill Brothers" and transcript[0].startswith("ACTION")
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, agent=scripted_agent()), only={"base_corpus"})["base_corpus"]
    assert r["state"] == "pass"


def test_style_gate(paras):
    seer = lambda pr: str(next(i for i, line in enumerate(pr.split("\n\n")[1:-1], 1) if "Harland" in line or "Contractor" in line or "tendered" in line))
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, style_judge=seer), only={"style"})["style"]
    assert r["state"] == "fail" and r["accuracy"] == 1.0
    r = run_gates(copy.deepcopy(PUZZLE), ctx(paras, style_judge=lambda pr: "1"), only={"style"})["style"]
    assert r["state"] == "pass"


def test_run_gates_order_stop_review_and_rates(paras):
    p = copy.deepcopy(PUZZLE)
    c = ctx(paras, closed_book_models={"m": lambda q: "Cotterill Brothers"}, oracle=knows("Cotterill Brothers"))
    res = run_gates(p, c)
    assert "oracle" not in res and p["return_to"] == 2 and p["gate_reason"].startswith(
        ("closed_book", "lexical_shortcut"))
    q = copy.deepcopy(PUZZLE)
    run_gates(q, ctx(paras, oracle=knows("Cotterill Brothers")), only={"oracle"})
    assert q["gates"]["oracle"] == "pass" and not shippable(q)
    assert run_gates(q, ctx(paras), only={"human_review"})["human_review"]["state"] == "pending"
    record_review(q, True, True, False, "reviewer-1", "two firms fit")
    assert run_gates(q, ctx(paras), only={"human_review"})["human_review"]["state"] == "fail"
    rates = pass_rates([p, q])
    assert rates["oracle"] == {"pass": 1, "tried": 1, "rate": 1.0} and rates["base_corpus"]["tried"] == 0
