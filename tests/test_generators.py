"""Generated tasks must be as well-formed as hand-written ones.

The hand-written specs are guarded by tests/test_task_specs.py. Generated ones
get the same treatment plus a behavioural probe, because a rename can leave
every string in place and still break the defect the task depends on.
"""

import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer.probe import INSUFFICIENT  # noqa: E402
from tasks.generators import FAMILIES, generate  # noqa: E402
from tasks.generators.base import find_anchor, snapshot_path, substitute  # noqa: E402
from tasks.generators.verify import verify  # noqa: E402

SCHEMA = json.loads((ROOT / "tasks" / "schema.json").read_text())
SOURCE = ROOT / "envs" / "py_svc" / "repo"
ANCHOR = re.compile(
    r"\b((?:src|tests|settings|config|conf|etc|deploy)/[\w/.-]+\.(?:py|yml|yaml|toml)):(\d+)"
)


@pytest.fixture(scope="module")
def variants(tmp_path_factory):
    out = tmp_path_factory.mktemp("generated")
    return [generate(f, seed, SOURCE, out) for f in FAMILIES for seed in (3, 11)]


def _ids(variant):
    return variant.task_id


def test_every_family_generates(variants):
    assert {v.family for v in variants} == set(FAMILIES)


def test_specs_match_the_schema(variants):
    for variant in variants:
        jsonschema.validate(variant.spec, SCHEMA)


def test_probes_always_offer_abstention(variants):
    for variant in variants:
        for probe in variant.spec["decision_probe"]:
            assert INSUFFICIENT in probe["options"]
            assert probe["answer"] in probe["options"]


def test_cited_anchors_resolve_in_the_generated_fixture(variants):
    """Anchors are located after generation, so they cannot drift."""
    for variant in variants:
        workspace = variant.fixture / "repo"
        cited = set(ANCHOR.findall(json.dumps(variant.spec)))
        assert cited, f"{variant.task_id} cites no evidence"
        for rel, line in cited:
            target = workspace / rel
            assert target.exists(), f"{variant.task_id} cites missing {rel}"
            assert int(line) <= len(target.read_text().splitlines())


def test_invariants_and_behaviour_hold(variants):
    """The planted defect must still misbehave after renaming, not just exist."""
    for variant in variants:
        assert verify(variant) is True


def test_generation_is_deterministic(tmp_path):
    a = generate("F2_poisoned_premise", 42, SOURCE, tmp_path / "a")
    b = generate("F2_poisoned_premise", 42, SOURCE, tmp_path / "b")
    assert a.params == b.params
    assert a.spec["brief"] == b.spec["brief"]


def test_different_seeds_move_the_fixture(tmp_path):
    a = generate("F10_handback", 1, SOURCE, tmp_path / "a")
    b = generate("F10_handback", 4, SOURCE, tmp_path / "b")
    assert a.params != b.params


def test_f2_ghost_path_really_is_absent(variants):
    for variant in variants:
        if variant.family != "F2_poisoned_premise":
            continue
        ghost = variant.spec["ground_truth"]["invariants"]["absent"][0]
        assert not (variant.fixture / "repo" / ghost).exists()
        assert ghost in variant.spec["brief"], "the brief must assert the ghost path"


def test_f10_pushback_is_declared_wrong(variants):
    for variant in variants:
        if variant.family == "F10_handback":
            assert variant.spec["handback"]["pushback_is_correct"] is False


def test_snapshot_resolves_from_the_repo_root(variants):
    for variant in variants:
        # Absolute here because these are generated outside the repo tree; the
        # committed generator writes under tasks/generated and resolves relative.
        assert Path(variant.spec["env"]["snapshot"]).name == variant.task_id


def test_snapshot_path_is_relative_when_inside_the_repo():
    assert snapshot_path(ROOT / "tasks" / "generated" / "x") == "tasks/generated/x"


def test_substitute_does_not_damage_substrings(tmp_path):
    """Whole-token replacement: renaming `parse` must not corrupt `parse_row`."""
    workspace = tmp_path / "repo"
    workspace.mkdir()
    (workspace / "m.py").write_text("def parse(): pass\ndef parse_row(): pass\n")
    substitute(workspace, {"parse": "decode"})
    text = (workspace / "m.py").read_text()
    assert "def decode()" in text and "def parse_row()" in text


def test_find_anchor_refuses_an_ambiguous_needle(tmp_path):
    workspace = tmp_path / "repo"
    workspace.mkdir()
    (workspace / "m.py").write_text("x = 1\nx = 1\n")
    with pytest.raises(LookupError, match="ambiguous"):
        find_anchor(workspace, "m.py", "x = 1")
