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
from orch.families import FAMILIES, chain, coupled, probe, wide  # noqa: E402
from orch.task import DELEGATE, SOLO, approx_tokens  # noqa: E402

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
    if task.family == "C":
        assert "hidden_checks.py" not in names
    if task.family == "L":
        # the listing says nothing about order: decoys outnumber the chain
        pages = [n for n in names if n.startswith("P-")]
        assert len(pages) == 3 * task.size


def test_generation_is_deterministic():
    for name, module in FAMILIES.items():
        size = module.SIZES[0]
        a, b = module.generate(size, 7), module.generate(size, 7)
        assert a.files == b.files and a.truth == b.truth, name


def test_labels_follow_the_design():
    labels = {(t.family, t.size): t.label for t in ALL}
    for (family, _), label in labels.items():
        assert label == (SOLO if family == "L" else DELEGATE)


def test_task_toml_carries_the_track_metadata():
    task = wide.generate(60, 1)
    text = task_toml(task)
    assert 'delegation_label = "delegate"' in text
    assert "[metadata.limits]" in text and "context_tokens = 32000" in text


def test_task_toml_validates_against_real_harbor():
    config = pytest.importorskip("harbor.models.task.config")
    import tomllib

    for task in ALL:
        config.TaskConfig.model_validate(tomllib.loads(task_toml(task)))


# --- W ------------------------------------------------------------------------------

def test_w_smallest_size_already_overflows_one_context_window():
    task = wide.generate(min(wide.SIZES), 1)
    total = sum(approx_tokens(t) for t in task.files.values())
    assert total > 2 * task.limits["context_tokens"]


def test_w_keyword_search_cannot_finish_the_task():
    kw = re.compile(r"twice|two times|duplicate|double|again|second", re.I)
    tp = fp = fn = 0
    for seed in range(1, 6):
        task = wide.generate(60, seed)
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
    kinds = set(wide.generate(60, 1).truth["kinds"].values())
    assert set(wide.KINDS_DECOY) <= kinds
    assert kinds & set(wide.KINDS_POSITIVE)


def test_w_order_needs_the_sentence_not_the_file():
    """Every ticket lists several orders, so a ticket id does not give the order."""
    task = wide.generate(60, 1)
    for match in task.truth["matches"]:
        header = task.files[f"tickets/{match['ticket']}.txt"].split("\n")[2]
        assert header.count("ORD-") == 4


def test_w_merge_reads_json_lines_and_ignores_prose():
    report = 'Found these:\n{"ticket": "T-1", "order": "ORD-9"}\nnot json {\n'
    assert wide.merge_reports([report, None]) == {"matches": [{"ticket": "T-1", "order": "ORD-9"}]}


# --- P ------------------------------------------------------------------------------

def test_p_culprit_is_findable_and_only_it_shows_its_cause():
    task = probe.generate(15, 1)
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
    task = probe.generate(15, 1)
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

def _score_c(task, task_dir, tmp_path, core_rep, view_reps):
    ws = tmp_path / f"ws{random.random()}"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    for module in ("producer", "scheduler"):
        (ws / "jobs" / f"{module}.py").write_text(coupled.render_core(module, *core_rep))
    for name, params in task.truth["views"].items():
        (ws / "views" / f"{name}.py").write_text(coupled.render_view(name, params, *view_reps[name]))
    return _grade(task_dir, ws)["reward"]


def test_c_any_consistent_representation_passes(tmp_path):
    task = coupled.generate(20, 1)
    task_dir = emit(task, tmp_path / "c")
    for rep in coupled.REPRESENTATIONS:
        assert _score_c(task, task_dir, tmp_path, rep, {n: rep for n in task.work_items}) == 1.0


def test_c_workers_choosing_independently_break_it(tmp_path):
    """Groups of views written by isolated workers, each picking its own format."""
    task = coupled.generate(20, 1)
    task_dir = emit(task, tmp_path / "c")
    rng = random.Random(0)
    scores = []
    for _ in range(6):
        reps, names = {}, task.work_items
        for i in range(0, len(names), coupled.VIEWS_PER_WORKER):
            rep = rng.choice(coupled.REPRESENTATIONS)
            reps.update({n: rep for n in names[i:i + coupled.VIEWS_PER_WORKER]})
        scores.append(_score_c(task, task_dir, tmp_path, rng.choice(coupled.REPRESENTATIONS), reps))
    assert sum(scores) / len(scores) < 0.6


def test_c_instruction_never_pins_the_record_format_but_the_plan_does():
    task = coupled.generate(20, 1)
    for word in ("under the key", "'priority' as", "rank", "record format"):
        assert word not in task.instruction
    assert all(coupled.CONTRACT in part["brief"] for part in task.oracle_plan)
    planned = [n for part in task.oracle_plan for n in part["items"]]
    assert sorted(planned) == sorted(task.work_items), "the plan covers every view exactly once"


def test_c_every_view_is_named_in_the_instruction():
    task = coupled.generate(40, 1)
    assert all(f"`{n}`" in task.instruction for n in task.work_items)


# --- L ------------------------------------------------------------------------------

def _follow_by_rules(task):
    """Follow the chain the way an agent must: parse each page and apply its rule."""
    rules = dict(chain.RULES)
    code, path = task.truth["path"][0], []
    while True:
        text = task.files[f"ledger/{code}.txt"]
        path.append(code)
        if "Closing code:" in text:
            return path, text.split("Closing code:")[1].split()[0]
        rows = re.findall(r"^(\w+)\s+([+-]\d+)\s+(P-\d+)$", text, re.M)
        rule = next(line for line in text.splitlines() if line.startswith("Follow"))
        pick = rules[rule]([(a, int(n)) for a, n, _ in rows])
        code = rows[pick][2]


@pytest.mark.parametrize("size", chain.SIZES)
def test_l_rules_on_the_pages_lead_along_the_chain(size):
    task = chain.generate(size, 1)
    path, closing = _follow_by_rules(task)
    assert path == task.truth["path"] and closing == task.truth["closing_code"]


def test_l_a_wrong_turn_leads_to_a_real_page(tmp_path):
    task = chain.generate(60, 1)
    first = task.files[f"ledger/{task.truth['path'][0]}.txt"]
    for target in re.findall(r"(P-\d+)$", first, re.M):
        assert f"ledger/{target}.txt" in task.files


def test_l_scores_the_correct_prefix(tmp_path):
    task = chain.generate(60, 1)
    task_dir = emit(task, tmp_path / "l")
    ws = tmp_path / "ws"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    path = task.truth["path"]
    (ws / "answer.json").write_text(json.dumps({"path": path[:30] + ["P-0000"] + path[31:]}))
    result = _grade(task_dir, ws)
    assert result["reward"] == 0.5 and result["closing_code"] == 0


# --- verifier robustness ------------------------------------------------------------------

@pytest.mark.parametrize("content", ["", "not json", "[]", '{"matches": "x"}',
                                     '{"matches": [1, {"ticket": 5}]}'])
def test_verifier_scores_malformed_answers_as_zero(content, tmp_path):
    task = wide.generate(60, 1)
    task_dir = emit(task, tmp_path / "w")
    ws = tmp_path / "ws"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    (ws / "answer.json").write_text(content)
    assert _grade(task_dir, ws)["reward"] == 0.0


def test_verifier_exports_the_answer_for_offline_scoring(tmp_path):
    task = wide.generate(60, 1)
    task_dir = emit(task, tmp_path / "w")
    ws = tmp_path / "ws"
    shutil.copytree(task_dir / "environment" / "workspace", ws)
    (ws / "answer.json").write_text('{"matches": []}')
    _grade(task_dir, ws)
    assert (tmp_path / "ws-verifier" / "answer.json").exists()


# --- the committed dataset ------------------------------------------------------------

DATASET = ROOT / "datasets" / "orch-v0.2"


def _tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name != "README.md"}


def test_committed_dataset_matches_the_generators(tmp_path):
    """datasets/orch-v0.2 is what `tools/orch_generate.py` emits, byte for byte.

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
