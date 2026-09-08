"""A task spec must be well-formed AND consistent with the fixture it names.

Schema validity is the easy half. The half that actually breaks benchmarks is
drift: a spec that cites parse.py:33 after someone adds a line to parse.py, or
a check entrypoint that no longer exists. These tests fail loudly on both.
"""

import importlib
import json
import re
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "tasks" / "schema.json").read_text())
SPECS = sorted((ROOT / "tasks" / "examples").glob("*.json"))
ANCHOR = re.compile(r"\b((?:src|tests|settings|config)/[\w/.]+\.(?:py|yml|yaml)):(\d+)")

# Anchors the specs lean on, and the token that must appear on that exact line.
# If the fixture shifts, these say so instead of the benchmark going quietly wrong.
PINNED = {
    ("src/upload/client.py", 56): "MAX_ATTEMPTS = 20",
    ("src/upload/client.py", 57): "RETRY_INTERVAL_SECONDS = 0.05",
    ("src/ingest/parse.py", 33): "d.isocalendar()[0]",
    ("src/ingest/dedup.py", 19): 'return (event["tenant_id"], event["event_uuid"])',
    ("src/ingest/dedup.py", 22): "def collapse_window",
    ("src/ingest/pipeline.py", 30): "collapse_window(raw_rows)",
    ("src/util/hashing.py", 16): "def dedupe_rows",
    ("tests/test_dedup.py", 27): "def test_same_uuid_across_tenants_is_not_collapsed",
}


def _load(path):
    return json.loads(path.read_text())


def _workspace(spec):
    return ROOT / spec["env"]["snapshot"] / "repo"


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_matches_schema(path):
    jsonschema.validate(_load(path), SCHEMA)


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_no_placeholders(path):
    text = path.read_text()
    assert "PLACEHOLDER" not in text
    assert "sha256:" not in text or "@sha256:PLACEHOLDER" not in text


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_environment_exists(path):
    spec = _load(path)
    ws = _workspace(spec)
    assert ws.is_dir(), f"{spec['env']['snapshot']}/repo is missing"
    assert (ws.parent / "Dockerfile").exists(), "fixture needs a Dockerfile"


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_check_entrypoint_is_importable(path):
    spec = _load(path)
    module_path, _, func = spec["ground_truth"]["check"].partition("::")
    assert func, "check must be 'module.py::callable'"
    assert (ROOT / module_path).exists(), f"{module_path} does not exist"
    mod = importlib.import_module(module_path.replace("/", ".").removesuffix(".py"))
    assert callable(getattr(mod, func, None)), f"{module_path} has no {func}()"


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_probe_options_are_well_formed(path):
    spec = _load(path)
    for probe in spec["decision_probe"]:
        assert "INSUFFICIENT INFORMATION" in probe["options"], (
            "every probe must let an honest partial report say so (DESIGN.md 4)"
        )
        assert probe["answer"] in probe["options"]
        assert len(set(probe["options"])) == len(probe["options"])


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_file_line_anchors_resolve(path):
    """Every path:line the spec cites must exist in the fixture."""
    spec = _load(path)
    ws = _workspace(spec)
    cited = set(ANCHOR.findall(path.read_text()))
    assert cited, "specs should cite concrete evidence locations"
    for rel, lineno in cited:
        target = ws / rel
        assert target.exists(), f"{rel} cited but absent from the fixture"
        lines = target.read_text().splitlines()
        assert int(lineno) <= len(lines), f"{rel}:{lineno} is past end of file"


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_pinned_anchors_still_point_at_the_right_code(path):
    spec = _load(path)
    ws = _workspace(spec)
    for rel, lineno in ANCHOR.findall(path.read_text()):
        key = (rel, int(lineno))
        if key not in PINNED:
            continue
        line = (ws / rel).read_text().splitlines()[int(lineno) - 1]
        assert PINNED[key] in line, (
            f"{rel}:{lineno} should contain {PINNED[key]!r}, found {line.strip()!r}"
        )


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.stem)
def test_oracle_report_covers_every_must_report_fact(path):
    """The oracle defines the ceiling (DESIGN.md 7.3). It cannot omit a required fact."""
    spec = _load(path)
    oracle = spec["oracle_report"].lower()
    assert len(oracle) > 200, "an oracle report should be substantive"
    for fact in spec["must_report"]:
        keywords = [w for w in re.findall(r"[\w./]+", fact.lower()) if len(w) > 4]
        # stem-match so hardcoded/hardcodes and modify/modified both count
        hits = sum(1 for w in keywords if w[:6] in oracle)
        assert hits >= max(1, len(keywords) // 3), (
            f"oracle report does not appear to cover must_report fact: {fact!r}"
        )


def test_handback_is_present_only_for_f10():
    for path in SPECS:
        spec = _load(path)
        if spec["family"] == "F10_handback":
            assert "handback" in spec, "F10 needs the scripted pushback turn"
            assert spec["handback"]["pushback_is_correct"] is False
        else:
            assert "handback" not in spec
