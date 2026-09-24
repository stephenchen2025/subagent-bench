"""Orchestrator track: the tasks pose the problem they claim to pose.

Every claim ORCHESTRATOR.md makes about a family is checked here: the oracle
solution scores 1.0, an untouched workspace does not, grep cannot finish W,
any consistent record representation passes C while mixed ones fail, and
nothing in the image knows the answer. No model, no container, no mini.
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch.emit import emit, generate_set, task_toml  # noqa: E402
from orch.families import FAMILIES, coupled, probe, small, wide  # noqa: E402
from orch.task import DELEGATE, OPTIONAL, SOLO, approx_tokens  # noqa: E402

ALL = generate_set(seeds=(1, 2))


def _grade(task_dir, ws):
    env = dict(os.environ, ORCH_WORKSPACE=str(ws), ORCH_TESTS=str(task_dir / "tests"),
               ORCH_REWARD_DIR=str(ws.parent / f"{ws.name}-verifier"))
    out = subprocess.run([sys.executable, str(task_dir / "tests" / "verify.py")], env=env,
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def emitted(tmp_path_factory):
    root = tmp_path_factory.mktemp("orch")
    return {t.id: (t, emit(t, root / t.id)) for t in ALL}


# --- every task -------------------------------------------------------------------

@pytest.mark.parametrize("task", ALL, ids=lambda t: t.id)
def test_oracle_scores_one_and_empty_workspace_does_not(task, emitted, tmp_path):
    _, task_dir = emitted[task.id]
    empty = tmp_path / "empty"
    shutil.copytree(task_dir / "environment" / "workspace", empty)
    assert _grade(task_dir, empty)["reward"] < 1.0

    solved = tmp_path / "solved"
    shutil.copytree(task_dir / "environment" / "workspace", solved)
    body = (task_dir / "solution" / "solve.sh").read_text().replace("cd /workspace", "")
    subprocess.run(["bash", "-c", body], cwd=solved, check=True)
    assert _grade(task_dir, solved)["reward"] == 1.0


@pytest.mark.parametrize("task", ALL, ids=lambda t: t.id)
def test_the_image_never_holds_the_answer(task, emitted):
    _, task_dir = emitted[task.id]
    env_files = [p for p in (task_dir / "environment").rglob("*") if p.is_file()]
    names = {p.name for p in env_files}
    assert "ground_truth.json" not in names and "solve.sh" not in names
    if task.family == "P":
        # The db holds narratives; the menu's labels are the answer, never in it.
        db = json.dumps(probe.decode_db(task.tool_files["/opt/svcctl/db"]))
        assert not any(label in db for label in probe.CAUSES)
    if task.family in ("C", "S"):
        assert "hidden_checks.py" not in names


def test_generation_is_deterministic():
    for name, module in FAMILIES.items():
        size = module.SIZES[0]
        a, b = module.generate(size, 7), module.generate(size, 7)
        assert a.files == b.files and a.truth == b.truth, name


def test_labels_follow_the_design():
    labels = {(t.family, t.size): t.label for t in ALL}
    assert labels[("W", 6)] == OPTIONAL and labels[("W", 72)] == DELEGATE
    assert labels[("P", 3)] == OPTIONAL and labels[("P", 20)] == DELEGATE
    assert labels[("C", 4)] == SOLO and labels[("S", 1)] == SOLO


def test_task_toml_carries_the_track_metadata():
    task = wide.generate(24, 1)
    text = task_toml(task)
    assert 'delegation_label = "delegate"' in text
    assert "[metadata.limits]" in text and "context_tokens = 32000" in text


def test_task_toml_validates_against_real_harbor():
    config = pytest.importorskip("harbor.models.task.config")
    import tomllib

    for task in ALL:
        config.TaskConfig.model_validate(tomllib.loads(task_toml(task)))


# --- W ------------------------------------------------------------------------------

def test_w_largest_size_is_several_context_windows():
    task = wide.generate(72, 1)
    total = sum(approx_tokens(t) for t in task.files.values())
    assert total > 2 * task.limits["context_tokens"]


def test_w_keyword_search_cannot_finish_the_task():
    kw = re.compile(r"twice|two times|duplicate|double|again|second", re.I)
    tp = fp = fn = 0
    for seed in range(1, 6):
        task = wide.generate(72, seed)
        positives = {m["ticket"] for m in task.truth["matches"]}
        for path, text in task.files.items():
            tid = Path(path).stem
            hit = bool(kw.search(text))
            tp += hit and tid in positives
            fp += hit and tid not in positives
            fn += (not hit) and tid in positives
    precision, recall = tp / (tp + fp), tp / (tp + fn)
    assert 2 * precision * recall / (precision + recall) < 0.6


def test_w_has_every_decoy_kind_and_positives():
    kinds = set(wide.generate(24, 1).truth["kinds"].values())
    assert set(wide.KINDS_DECOY) <= kinds
    assert kinds & set(wide.KINDS_POSITIVE)


def test_w_order_needs_the_sentence_not_the_file():
    """Every ticket lists several orders, so a ticket id does not give the order."""
    task = wide.generate(24, 1)
    for match in task.truth["matches"]:
        header = task.files[f"tickets/{match['ticket']}.txt"].split("\n")[2]
        assert header.count("ORD-") == 4


def test_w_merge_reads_json_lines_and_ignores_prose():
    report = 'Found these:\n{"ticket": "T-1", "order": "ORD-9"}\nnot json {\n'
    assert wide.merge_reports([report, None]) == {"matches": [{"ticket": "T-1", "order": "ORD-9"}]}


# --- P ------------------------------------------------------------------------------

def test_p_culprit_is_findable_and_only_it_shows_its_cause():
    task = probe.generate(10, 1)
    db = probe.decode_db(task.tool_files["/opt/svcctl/db"])
    for svc, truth in task.truth["services"].items():
        assert truth["component"] in db[svc]["components"]
        culprit_logs = db[svc]["logs"][truth["component"]]
        assert "ERROR" in culprit_logs
        # the incident notes describe the component, never name it
        notes = db[svc]["status"].split("incident notes")[1]
        assert truth["component"] not in notes
        for component, logs in db[svc]["logs"].items():
            if component != truth["component"]:
                assert not any(line in logs for line in
                               ("ENOSPC", "SERVFAIL", "unknown key", "cgroup limit"))


def test_svcctl_runs_against_its_db(tmp_path):
    task = probe.generate(3, 1)
    tool = tmp_path / "svcctl"
    tool.write_text(task.tool_files["/opt/svcctl/svcctl"])
    db = tmp_path / "db"
    db.write_text(task.tool_files["/opt/svcctl/db"])
    env = dict(os.environ, SVCCTL_DB=str(db), SVCCTL_LATENCY="0")
    svc = task.work_items[0]
    out = subprocess.run([sys.executable, str(tool), "components", svc], env=env,
                         capture_output=True, text=True)
    assert task.truth["services"][svc]["component"] in out.stdout


# --- C ------------------------------------------------------------------------------

def _score_c(task_dir, tmp_path, reps):
    ws = tmp_path / f"ws{random.random()}"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    for module, (key, enc) in reps.items():
        (ws / "jobs" / f"{module}.py").write_text(coupled.render_module(module, key, enc))
    return _grade(task_dir, ws)["reward"]


def test_c_any_consistent_representation_passes(tmp_path):
    task = coupled.generate(7, 1)
    task_dir = emit(task, tmp_path / "c")
    for rep in coupled.REPRESENTATIONS:
        assert _score_c(task_dir, tmp_path, {m: rep for m in task.work_items}) == 1.0


def test_c_independent_choices_usually_break_it(tmp_path):
    task = coupled.generate(4, 1)
    task_dir = emit(task, tmp_path / "c")
    rng = random.Random(0)
    scores = [_score_c(task_dir, tmp_path,
                       {m: rng.choice(coupled.REPRESENTATIONS) for m in task.work_items})
              for _ in range(10)]
    assert sum(scores) / len(scores) < 0.8


def test_c_instruction_never_pins_the_record_format():
    text = coupled.generate(7, 1).instruction
    for word in ("prio\"", "rank", "_KEY", "record format", "store it"):
        assert word not in text


# --- S ------------------------------------------------------------------------------

def test_s_variants_all_fixable(tmp_path):
    for seed in range(1, 10):
        task = small.generate(1, seed)
        task_dir = emit(task, tmp_path / task.id)
        ws = tmp_path / f"{task.id}-ws"
        shutil.copytree(task_dir / "environment" / "workspace", ws)
        visible = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"],
                                 cwd=ws, capture_output=True)
        assert visible.returncode != 0, "the named test must fail before the fix"


# --- verifier robustness ------------------------------------------------------------------

@pytest.mark.parametrize("content", ["", "not json", "[]", '{"matches": "x"}',
                                     '{"matches": [1, {"ticket": 5}]}'])
def test_verifier_scores_malformed_answers_as_zero(content, tmp_path):
    task = wide.generate(6, 1)
    task_dir = emit(task, tmp_path / "w")
    ws = tmp_path / "ws"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    (ws / "answer.json").write_text(content)
    assert _grade(task_dir, ws)["reward"] == 0.0


def test_verifier_exports_the_answer_for_offline_scoring(tmp_path):
    task = wide.generate(6, 1)
    task_dir = emit(task, tmp_path / "w")
    ws = tmp_path / "ws"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    (ws / "answer.json").write_text('{"matches": []}')
    _grade(task_dir, ws)
    assert (tmp_path / "ws-verifier" / "answer.json").exists()


# --- the committed dataset ------------------------------------------------------------

DATASET = ROOT / "datasets" / "orch-v0.1"


def _tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name != "README.md"}


def test_committed_dataset_matches_the_generators(tmp_path):
    """datasets/orch-v0.1 is what `tools/orch_generate.py` emits, byte for byte.

    The dataset is checked in so it can be shared and run without this code; the
    generators remain the source of truth. A generator change that is not
    followed by a regeneration fails here rather than shipping a stale set.
    """
    from orch.emit import emit_set

    emit_set(generate_set(seeds=(1, 2, 3)), tmp_path)
    committed, fresh = _tree(DATASET), _tree(tmp_path)
    assert committed.keys() == fresh.keys()
    stale = [path for path in committed if committed[path] != fresh[path]]
    assert not stale, f"regenerate with tools/orch_generate.py --out {DATASET}: {stale[:5]}"
