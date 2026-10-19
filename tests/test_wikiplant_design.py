import copy
import json
import random
from pathlib import Path

import pytest

from wikiplant.design import DesignError, build_brief, check_design, design_puzzle, parse_json, refine_brief
from wikiplant.names import CollisionIndex, Registry, generate
from wikiplant.parse import snapshot

SAMPLE = Path(__file__).resolve().parents[1] / "wikiplant" / "sample"


@pytest.fixture(scope="module")
def world():
    pages, paras, _ = snapshot(SAMPLE / "dump.xml", "2026-10-01")
    cluster = {"seed": 101, "pages": [101, 102, 103]}
    return pages, paras, cluster, build_brief(cluster, paras, pages)


GOOD = {
    "template": "chain",
    "entities": [
        {"eid": "e1", "name": "Marlow Junction railway station", "type": "place", "invented": False},
        {"eid": "e2", "name": "Threlfall and Ormerod", "type": "organization", "invented": True, "from": 1840, "to": 1900},
        {"eid": "e3", "name": "Dunmere Valley Railway", "type": "organization", "invented": False, "from": 1846, "to": 1879},
    ],
    "facts": [
        {"fid": "f0", "s": "e1", "r": "built_by", "o": "e3", "planted": False, "para_id": "101:History:0"},
        {"fid": "f1", "s": "e2", "r": "supplied_locomotives_to", "o": "e3", "planted": True, "host_page": 102, "when": 1852},
    ],
    "path": ["f0", "f1"],
    "question": "The company that built the former station serving a mill town was first supplied with locomotives by a firm. In what year did that supply begin?",
    "answer": "1852", "aliases": [],
}
HOSTS = {101, 102, 103}


def check(d, world, **kw):
    return check_design({**d, "pid": "p"}, world[3], kw.pop("tier", "easy"), kw.pop("hosts", HOSTS), **kw)


def mutated(**patch):
    d = copy.deepcopy(GOOD)
    for k, v in patch.items():
        d[k] = v
    return d


def test_good_design_passes(world):
    assert check(GOOD, world) == []


def test_brief_has_pages_years_and_in_cluster_relations(world):
    brief = world[3]
    p101 = next(p for p in brief["pages"] if p["page_id"] == 101)
    assert p101["years"] == [1851, 1971] and "History/Closure" in p101["sections"]
    assert {"s": "Marlow Junction railway station", "r": "links_to", "o": "Dunmere Valley Railway",
            "para_id": "101::0"} in brief["relations"]
    assert all(r["o"] in {p["title"] for p in brief["pages"]} for r in brief["relations"])


def test_refine_brief_merges_model_output(world):
    reply = json.dumps({"entities": [{"name": "Marlow Bridge", "type": "place"}],
                        "relations": [{"s": "Marlow Bridge", "r": "on_river", "o": "Dunmere"}, {"bad": 1}]})
    out = refine_brief(world[3], lambda prompt: "Sure!\n```json\n" + reply + "\n```")
    assert out["entities"][0]["name"] == "Marlow Bridge"
    assert any(r["r"] == "on_river" for r in out["relations"]) and not any("bad" in r for r in out["relations"])


def test_parse_json_errors():
    assert parse_json('noise {"a": 1} tail') == {"a": 1}
    assert parse_json('{"a": [1, 2,], "b": {"c": 3,},}') == {"a": [1, 2], "b": {"c": 3}}
    with pytest.raises(DesignError):
        parse_json("no object")


@pytest.mark.parametrize("name,patch,expect", [
    ("tier hops", dict(path=["f1"]), "hops"),
    ("ends real", dict(path=["f1", "f0"]), "end at a planted"),
    ("same page", dict(facts=[GOOD["facts"][0], {**GOOD["facts"][1], "host_page": 101}]), "different host page"),
    ("timeline", dict(facts=[GOOD["facts"][0], {**GOOD["facts"][1], "when": 1890}]), "outside"),
    ("answer leak", dict(question="Was it 1852 when the supply began?"), "contains the answer"),
    ("names invented", dict(question="When did Threlfall and Ormerod supply the railway?"), "names invented"),
    ("template", dict(template="aggregation"), "not allowed"),
])
def test_rule_violations(world, name, patch, expect):
    assert any(expect in e for e in check(mutated(**patch), world)), name


def test_planted_host_must_be_eligible(world):
    assert any("not a host-eligible" in e for e in check(GOOD, world, hosts={101}))


def test_planted_subject_must_be_invented_and_real_facts_stay_real(world):
    d = mutated()
    d["entities"][1]["invented"] = False
    assert any("subject must be an invented" in e for e in check(d, world))
    d = mutated()
    d["facts"][0] = {**d["facts"][0], "o": "e2"}
    assert any("real fact cannot involve" in e for e in check(d, world))


def test_disconnected_path_is_rejected(world):
    d = mutated()
    d["entities"].append({"eid": "e9", "name": "Other Firm", "invented": True})
    d["facts"][1] = {**d["facts"][1], "s": "e9", "o": "e9"}
    assert any("share no entity" in e for e in check(d, world))


def test_name_collision_and_registry_caps(world):
    idx = CollisionIndex(world[1])
    assert "title" in idx.collisions("Marlow Bridge")
    assert any(h.startswith("fuzzy") for h in idx.collisions("Marlow Brigde"))
    assert "text" in idx.collisions("Dunmere Valley Railway") or "title" in idx.collisions("Dunmere Valley Railway")
    assert idx.collisions("Threlfall and Ormerod") == []
    d = mutated()
    d["entities"][1]["name"] = "Marlow Bridge"
    assert any("collides" in e for e in check(d, world, collision=idx))
    reg = Registry(max_name=1, max_part=2)
    reg.add("Threlfall and Ormerod")
    assert any("already used" in e for e in check(GOOD, world, registry=reg))
    reg.add("Ormerod and Kershaw")
    assert any("'ormerod'" in p for p in reg.problems("Ormerod Brothers"))


def test_generate_is_seeded_and_period_shaped():
    a = [generate("firm", rng=random.Random(3)) for _ in range(2)]
    assert a[0] == a[1] and any(w in a[0] for w in ("and", "&", "Brothers", "Sons"))
    assert generate("society", rng=random.Random(1)).split()[0] in {"Thrushcombe", "Ashlowe", "Carrowdene", "Hollinsbeck", "Stavenholme", "Quarnley", "Brackenworth", "Ellerscar"}
    with pytest.raises(ValueError):
        generate("spaceship")


def test_design_loop_feeds_failures_back_and_registers_names(world):
    prompts, replies = [], [json.dumps(mutated(path=["f1"])), "garbage", json.dumps(GOOD)]

    def model(prompt):
        prompts.append(prompt)
        return replies[len(prompts) - 1]

    reg = Registry()
    d, attempts = design_puzzle(world[3], model, "easy", "chain", HOSTS, "p7", registry=reg)
    assert d and d["pid"] == "p7" and d["tier"] == "easy" and d["gates"]["oracle"] == "pending"
    assert len(attempts) == 3 and attempts[0]["problems"] and attempts[1]["problems"][0].startswith("unparseable")
    assert "failed these checks" in prompts[1] and "hops" in prompts[1]
    assert reg.names["threlfall and ormerod"] == 1


def test_design_gives_up_with_reasons(world):
    d, attempts = design_puzzle(world[3], lambda p: json.dumps(mutated(path=["f1"])), "easy", "chain", HOSTS, "p", max_attempts=2)
    assert d is None and len(attempts) == 2 and attempts[-1]["problems"]


def test_year_strings_are_normalized_or_reported(world):
    from wikiplant.design import normalize_years
    d = mutated()
    d["facts"][1]["when"] = "c. 1852"
    d["entities"][2]["to"] = "1879"
    assert check(normalize_years(d), world) == []
    assert d["facts"][1]["when"] == 1852 and d["entities"][2]["to"] == 1879
    d = mutated()
    d["facts"][1]["when"] = "the 1850s?"
    assert check(d, world)        # no crash
    d["facts"][1]["when"] = "early that decade"
    assert any("must be a year number" in e for e in check(normalize_years(d), world))


def test_design_loop_accepts_string_years(world):
    reply = mutated()
    reply["facts"][1]["when"] = "1852"
    d, attempts = design_puzzle(world[3], lambda p: json.dumps(reply), "easy", "chain", HOSTS, "p9")
    assert d is not None and d["facts"][1]["when"] == 1852, attempts
