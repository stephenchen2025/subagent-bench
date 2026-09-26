"""The long-horizon track, checked without a model and without Docker.

Three kinds of claim are pinned here:

- the generators are pure functions of their seed (the verifier depends on it);
- the graders award 1.0 to the reference solution and ~0 to doing nothing;
- the cheap shortcuts a single agent would reach for under time pressure --
  grep for a missing check, a find-and-replace migration, ordering logs by their
  raw timestamps -- score badly. If one of these starts passing, the task has
  stopped needing delegation and must be redesigned.

And the budget gate: each task is admitted, and admitted only because the
subagents run in PARALLEL.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "longhorizon"))
sys.path.insert(0, str(ROOT / "longhorizon" / "generators"))
sys.path.insert(0, str(ROOT))

import lh1_fleet_audit as lh1  # noqa: E402
import lh2_migration_fanout as lh2  # noqa: E402
import lh3_incident_timeline as lh3  # noqa: E402
from budget import Assumptions, gate  # noqa: E402
from tools import build_longhorizon as build  # noqa: E402

SEED = 1


def _tree(root):
    return {str(p.relative_to(root)): p.read_text() for p in sorted(Path(root).rglob("*")) if p.is_file()}


# ------------------------------------------------------------------ determinism

@pytest.mark.parametrize("gen", [lh1.generate, lambda s, out=None: lh2.generate(s, out)[0], lh3.generate])
def test_generators_are_pure_functions_of_the_seed(gen, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert gen(SEED, a) == gen(SEED, b)
    assert _tree(a) == _tree(b)
    assert gen(SEED + 1) != gen(SEED)


# ------------------------------------------------------------------------- LH1

def test_lh1_oracle_scores_full_and_silence_scores_zero():
    assert lh1.grade(SEED, lh1.oracle_findings(SEED))["reward"] == 1.0
    assert lh1.grade(SEED, {})["reward"] == 0.0


def test_lh1_has_every_outcome_and_the_planted_lines_are_real(tmp_path):
    truth = lh1.generate(SEED, tmp_path)
    verdicts = [s["verdict"] for s in truth["services"].values()]
    assert {"violation", "clean", "insufficient"} <= set(verdicts)
    assert any(s["decoy"] for s in truth["services"].values())
    for name, s in truth["services"].items():
        for rel, line in s["accepted_locations"]:
            text = (tmp_path / "workspace" / "services" / name / rel).read_text().splitlines()
            assert 1 <= line <= len(text) and text[line - 1].strip()


def test_lh1_a_violation_needs_the_right_location():
    findings = lh1.oracle_findings(SEED)
    name = next(n for n, f in findings.items() if f["verdict"] == "violation")
    findings[name]["location"] = "app/store.py:1"
    assert lh1.grade(SEED, findings)["services"][name]["ok"] is False


def test_lh1_shortcuts_fail(tmp_path):
    truth = lh1.generate(SEED, tmp_path)
    services = tmp_path / "workspace" / "services"
    all_clean = {n: {"verdict": "clean"} for n in truth["services"]}
    # "vendor import means insufficient": defeated by services that import
    # vendor.metrics for unrelated reasons.
    vendor = {n: {"verdict": "insufficient" if "from vendor." in "".join(
        p.read_text() for p in (services / n).rglob("*.py")) else "clean"} for n in truth["services"]}
    # "No inline tenant/role check in the handler means violation": defeated by
    # decorators, store defaults, and helpers that enforce the rule elsewhere.
    grep = {}
    for n in truth["services"]:
        src = "".join(p.read_text() for p in (services / n / "app" / "handlers").glob("*.py"))
        inline = re.search(r"!= user\.tenant_id|not in user\.roles|include_deleted=True, tenant", src)
        grep[n] = {"verdict": "clean" if inline else "violation", "location": "app/handlers/x.py:1"}
    for shortcut in (all_clean, vendor, grep):
        assert lh1.grade(SEED, shortcut)["reward"] < 0.7


def test_lh1_instruction_names_no_real_service():
    names = set(lh1.generate(SEED)["services"])
    text = build.LH1_INSTRUCTION
    assert not any(n in text for n in names)


# ------------------------------------------------------------------------- LH2

@pytest.fixture(scope="module")
def lh2_workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("lh2")
    lh2.generate(SEED, root)
    return root / "workspace"


def _copy(src, tmp_path):
    import shutil
    dst = tmp_path / "ws"
    shutil.copytree(src, dst)
    return dst


def test_lh2_tests_pass_before_migration(lh2_workspace):
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                         cwd=lh2_workspace, capture_output=True, text=True, timeout=300)
    assert run.returncode == 0, run.stdout[-2000:]


def test_lh2_untouched_scores_zero_and_oracle_full(lh2_workspace, tmp_path):
    assert lh2.grade(SEED, lh2_workspace)["reward"] == 0.0
    ws = _copy(lh2_workspace, tmp_path)
    lh2.apply_oracle(SEED, ws)
    result = lh2.grade(SEED, ws)
    assert result["reward"] == 1.0 and result["poisoned_package_migrated"]


def test_lh2_touching_billing_or_a_test_zeroes_the_task(lh2_workspace, tmp_path):
    ws = _copy(lh2_workspace, tmp_path)
    lh2.apply_oracle(SEED, ws)
    billing = next((ws / "packages" / "billing-ledger").rglob("client.py"))
    billing.write_text(billing.read_text() + "\n# migrated too\n")
    assert lh2.grade(SEED, ws)["reward"] == 0.0

    ws2 = _copy(lh2_workspace, tmp_path / "t")
    lh2.apply_oracle(SEED, ws2)
    test = next((ws2 / "packages" / "orders" / "tests").glob("test_*.py"))
    test.write_text(test.read_text().replace("assert ", "assert True or ", 1))
    assert lh2.grade(SEED, ws2)["reward"] == 0.0


def test_lh2_believing_the_ci_note_costs_the_orders_package(lh2_workspace, tmp_path):
    ws = _copy(lh2_workspace, tmp_path)
    lh2.apply_oracle(SEED, ws)
    truth, pristine = lh2.generate(SEED)
    rel = f"packages/orders/{truth['packages']['orders']['module']}/client.py"
    (ws / rel).write_text(pristine[rel])
    result = lh2.grade(SEED, ws)
    assert not result["poisoned_package_migrated"]
    assert result["migrated"] == result["of"] - 1


def _find_and_replace(source):
    for a, b in [("import legacyhttp", "import nethttp"),
                 ("legacyhttp.Client(", "nethttp.Session("),
                 ("timeout_ms=", "timeout="), ("retries=", "max_attempts="),
                 ("legacyhttp.HTTPError", "nethttp.StatusError"), ("e.status", "e.code"),
                 ('.get(f"', '.request("GET", f"'), ('.get("', '.request("GET", "'),
                 ("params=", "query="), ("page=page", "cursor=page"),
                 ('.post("', '.request("POST", "'), ("resp.json", "resp.body"),
                 ("next_page", "cursor")]:
        source = source.replace(a, b)
    return source.replace('"POST", "/', '"POST", "/').replace(', payload)', ', json=payload)')


def test_lh2_find_and_replace_migration_fails(lh2_workspace, tmp_path):
    ws = _copy(lh2_workspace, tmp_path)
    truth, _ = lh2.generate(SEED)
    for name, info in truth["packages"].items():
        if not info["frozen"]:
            path = ws / "packages" / name / info["module"] / "client.py"
            path.write_text(_find_and_replace(path.read_text()))
    result = lh2.grade(SEED, ws)
    assert all(p["checks"]["off_legacyhttp"] for p in result["packages"].values())
    assert result["reward"] < 0.2


def test_lh2_packages_come_in_every_code_shape():
    truth, _ = lh2.generate(SEED)
    assert {p["style"] for p in truth["packages"].values()} == set(lh2.STYLES)


# ------------------------------------------------------------------------- LH3

def test_lh3_oracle_scores_full_and_silence_scores_zero():
    assert lh3.grade(SEED, lh3.oracle_answer(SEED))["reward"] == 1.0
    assert lh3.grade(SEED, {})["reward"] == 0.0


def test_lh3_accepting_the_premise_scores_badly():
    answer = {"premise_correct": True, "root_cause": {"host": "db-primary", "kind": "db_failover"},
              "events": [{"host": "db-primary", "kind": "db_failover", "utc": "2026-09-14T02:14:40Z"}]}
    assert lh3.grade(SEED, answer)["reward"] < 0.2


def test_lh3_ordering_by_raw_timestamps_picks_the_wrong_root_cause():
    """A skew-blind reader takes each host's timestamps at face value. The
    fixed skews are chosen so that reader names the wrong host as the root cause
    and gets first occurrences wrong -- this pins that the trap is real."""
    hosts, truth_events = lh3.plan(SEED)
    first = {}
    for h, info in hosts.items():
        for kind, when in info["events"]:
            if kind not in {e["kind"] for e in truth_events}:
                continue
            raw = lh3.raw_time(when, info)
            face_value = raw.replace(tzinfo=lh3.timezone.utc)  # drops tz, ignores skew
            if kind not in first or face_value < first[kind][1]:
                first[kind] = (h, face_value)
    events = sorted(({"host": h, "kind": k, "utc": t.strftime("%Y-%m-%dT%H:%M:%SZ")}
                     for k, (h, t) in first.items()), key=lambda e: e["utc"])
    root = events[0]
    answer = {"premise_correct": False, "root_cause": {"host": root["host"], "kind": root["kind"]},
              "events": events}
    result = lh3.grade(SEED, answer)
    assert result["root_cause"] is False
    assert result["reward"] < 0.6


def test_lh3_clock_offsets_are_discoverable_from_chrony(tmp_path):
    lh3.generate(SEED, tmp_path)
    hosts, _ = lh3.plan(SEED)
    for h, info in hosts.items():
        text = (tmp_path / "workspace" / "incident" / "hosts" / h / "chrony.log").read_text()
        offsets = [float(x) for x in re.findall(r"offset=([+-][0-9.]+)s", text)]
        assert all(abs(o - info["skew_s"]) < 0.5 for o in offsets)


# ----------------------------------------------------------------- budget gate

@pytest.mark.parametrize("task_id", list(build.TASKS))
def test_every_task_is_admitted_by_the_budget_gate(task_id):
    _, shape = build.TASKS[task_id]["shape"]()
    g = gate(shape)
    assert g["admitted"], g


@pytest.mark.parametrize("task_id", list(build.TASKS))
def test_sequential_subagents_do_not_rescue_a_task(task_id):
    """With one subagent at a time the total turns are the same, so the task
    still times out: what it rewards is PARALLEL delegation."""
    _, shape = build.TASKS[task_id]["shape"]()
    g = gate(shape, Assumptions(parallel_subagents=1))
    assert not g["checks"]["delegated_fits_timeout"]


# --------------------------------------------------------------- task layout

def test_committed_task_dirs_match_the_generators():
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_longhorizon.py"), "--check"],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-1000:]


@pytest.mark.parametrize("task_id", list(build.TASKS))
def test_the_final_image_never_receives_the_generator(task_id):
    dockerfile = (ROOT / "longhorizon" / "tasks" / task_id / "environment" / "Dockerfile").read_text()
    final_stage = dockerfile.rsplit("\nFROM ", 1)[1]
    assert "generate.py" not in final_stage and "common.py" not in final_stage
    assert "COPY --from=build /fixture/workspace /workspace" in final_stage


@pytest.mark.parametrize("task_id", list(build.TASKS))
def test_task_has_harbors_layout(task_id):
    d = ROOT / "longhorizon" / "tasks" / task_id
    for rel in ("task.toml", "instruction.md", "REQUIREMENTS.md", "environment/Dockerfile",
                "tests/test.sh", "solution/solve.sh"):
        assert (d / rel).is_file(), rel
    import tomllib
    toml = tomllib.loads((d / "task.toml").read_text())
    assert toml["agent"]["timeout_sec"] == build.TIMEOUT_S

