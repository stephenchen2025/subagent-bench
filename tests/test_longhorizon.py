"""The long-horizon track, checked without a model and without Docker.

Pinned here, for all ten families and all three seeds:

- the generators are pure functions of their seed (the verifier depends on it);
- the reference solution scores 1.0, and doing nothing scores ~0;
- the shortcuts a single agent would reach for under time pressure -- grep,
  find-and-replace, keyword triage, trusting raw timestamps -- score well below
  a passing grade. If one starts passing, the task has stopped needing
  delegation and must be redesigned;
- each family's hard constraint actually bites (frozen packages, end-of-life
  lines, the shared registry);
- every task passes the budget gate, and only because subagents run in PARALLEL.
"""

import importlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "longhorizon"))
sys.path.insert(0, str(ROOT / "longhorizon" / "generators"))
sys.path.insert(0, str(ROOT))

from budget import Assumptions, gate  # noqa: E402
from tools import build_longhorizon as build  # noqa: E402

FAMILIES = list(build.FAMILIES)
SEEDS = list(build.SEEDS)
WORKSPACE_GRADED = {"lh2_migration_fanout", "lh8_plugin_port", "lh9_backport"}
ANSWER_GRADED = [f for f in FAMILIES if f not in WORKSPACE_GRADED]
SHORTCUT_CEILING = 0.75   # a passing grade should be >= 0.9


def mod(family):
    return importlib.import_module(family)


def _truth(family, seed, out=None):
    t = mod(family).generate(seed, out)
    return t[0] if isinstance(t, tuple) else t


def _tree(root):
    return {str(p.relative_to(root)): p.read_text() for p in sorted(Path(root).rglob("*")) if p.is_file()}


@pytest.fixture(scope="module")
def workspaces(tmp_path_factory):
    """One generated workspace per (family, seed), built lazily and reused."""
    cache = {}

    def get(family, seed):
        if (family, seed) not in cache:
            root = tmp_path_factory.mktemp(f"{family}_s{seed}")
            _truth(family, seed, root)
            cache[(family, seed)] = root / "workspace"
        return cache[(family, seed)]
    return get


def _copy(src, dst):
    shutil.copytree(src, dst)
    return dst


# ------------------------------------------------------------------ determinism

@pytest.mark.parametrize("family", FAMILIES)
def test_generator_is_a_pure_function_of_its_seed(family, tmp_path):
    a = _truth(family, 1, tmp_path / "a")
    b = _truth(family, 1, tmp_path / "b")
    assert a == b and _tree(tmp_path / "a") == _tree(tmp_path / "b")
    assert _truth(family, 2) != a


# -------------------------------------------------------- oracle and doing nothing

@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("family", ANSWER_GRADED)
def test_answer_oracle_scores_full_and_silence_zero(family, seed):
    m = mod(family)
    oracle = m.oracle_findings(seed) if family == "lh1_fleet_audit" else m.oracle(seed)
    assert m.grade(seed, oracle)["reward"] == 1.0
    assert m.grade(seed, {})["reward"] == 0.0


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("family", sorted(WORKSPACE_GRADED))
def test_workspace_oracle_scores_full(family, seed, workspaces, tmp_path):
    m = mod(family)
    ws = _copy(workspaces(family, seed), tmp_path / "ws")
    m.apply_oracle(seed, ws)
    assert m.grade(seed, ws)["reward"] == 1.0


@pytest.mark.parametrize("family,ceiling", [("lh2_migration_fanout", 0.0), ("lh8_plugin_port", 0.0),
                                            # LH9's base rate: lines that must stay unchanged
                                            ("lh9_backport", 0.5)])
def test_untouched_workspace_scores_at_most_its_base_rate(family, ceiling, workspaces):
    assert mod(family).grade(1, workspaces(family, 1))["reward"] <= ceiling


# ------------------------------------------------------------ constraints bite

def test_lh2_touching_billing_or_a_test_zeroes_the_task(workspaces, tmp_path):
    m = mod("lh2_migration_fanout")
    ws = _copy(workspaces("lh2_migration_fanout", 1), tmp_path / "a")
    m.apply_oracle(1, ws)
    billing = next((ws / "packages" / "billing-ledger").rglob("client.py"))
    billing.write_text(billing.read_text() + "\n# migrated too\n")
    assert m.grade(1, ws)["reward"] == 0.0

    ws2 = _copy(workspaces("lh2_migration_fanout", 1), tmp_path / "b")
    m.apply_oracle(1, ws2)
    test = next((ws2 / "packages" / "orders" / "tests").glob("test_*.py"))
    test.write_text(test.read_text().replace("assert ", "assert True or ", 1))
    assert m.grade(1, ws2)["reward"] == 0.0


def test_lh2_believing_the_ci_note_costs_the_orders_package(workspaces, tmp_path):
    m = mod("lh2_migration_fanout")
    ws = _copy(workspaces("lh2_migration_fanout", 1), tmp_path / "ws")
    m.apply_oracle(1, ws)
    truth, pristine = m.generate(1)
    rel = f"packages/orders/{truth['packages']['orders']['module']}/client.py"
    (ws / rel).write_text(pristine[rel])
    result = m.grade(1, ws)
    assert not result["poisoned_package_migrated"] and result["migrated"] == result["of"] - 1


def test_lh8_parallel_writers_that_each_rewrite_the_registry_lose_almost_everything(workspaces, tmp_path):
    m = mod("lh8_plugin_port")
    ws = _copy(workspaces("lh8_plugin_port", 1), tmp_path / "ws")
    m.apply_oracle(1, ws)
    reg = (ws / "pluginapi" / "registry.py").read_text()
    lines = [line for line in reg.splitlines() if line.startswith('    "')]
    last_writer = lines[7::8]  # the 8th subagent's lane; it wrote last
    (ws / "pluginapi" / "registry.py").write_text(
        re.sub(r"PLUGINS = \{\n.*?\n\}", "PLUGINS = {\n" + "\n".join(last_writer) + "\n}", reg, flags=re.S))
    assert m.grade(1, ws)["reward"] <= 0.2


def test_lh9_patching_an_end_of_life_line_zeroes_the_task(workspaces, tmp_path):
    m = mod("lh9_backport")
    ws = _copy(workspaces("lh9_backport", 1), tmp_path / "ws")
    truth, _ = m.generate(1)
    for v, info in truth["lines"].items():
        if info["affected"]:  # every vulnerable line, supported or not
            m.write(ws / "releases" / v, m.MODULE_PATH[info["era"]], m.ERA_CODE[info["era"]][1])
    result = m.grade(1, ws)
    assert result["reward"] == 0.0 and result["eol_lines_modified"]


# -------------------------------------------------------------------- shortcuts

def _lh1_shortcuts(ws, truth):
    services = ws / "services"
    all_clean = {n: {"verdict": "clean"} for n in truth["services"]}
    vendor = {n: {"verdict": "insufficient" if "from vendor." in "".join(
        p.read_text() for p in (services / n).rglob("*.py")) else "clean"} for n in truth["services"]}
    grep = {}
    for n in truth["services"]:
        src = "".join(p.read_text() for p in (services / n / "app" / "handlers").glob("*.py"))
        inline = re.search(r"!= user\.tenant_id|not in user\.roles|include_deleted=True, tenant", src)
        grep[n] = {"verdict": "clean" if inline else "violation", "location": "app/handlers/x.py:1"}
    return [all_clean, vendor, grep]


def _lh3_shortcuts(ws, truth, seed):
    m = mod("lh3_incident_timeline")
    hosts, events = m.plan(seed)
    kinds = {e["kind"] for e in events}
    out = []
    for correct_tz in (False, True):
        first = {}
        for h, info in hosts.items():
            for kind, when in info["events"]:
                if kind not in kinds:
                    continue
                raw = (when + m.timedelta(seconds=info["skew_s"])) if correct_tz else \
                    m.raw_time(when, info).replace(tzinfo=m.timezone.utc)
                if kind not in first or raw < first[kind][1]:
                    first[kind] = (h, raw)
        ev = sorted(({"host": h, "kind": k, "utc": t.strftime("%Y-%m-%dT%H:%M:%SZ")}
                     for k, (h, t) in first.items()), key=lambda e: e["utc"])
        out.append({"premise_correct": False, "root_cause": {"host": ev[0]["host"], "kind": ev[0]["kind"]},
                    "events": ev})
    out.append({"premise_correct": True, "root_cause": {"host": "db-primary", "kind": "db_failover"},
                "events": []})
    return out


def _lh4_shortcuts(ws, truth):
    m = mod("lh4_license_review")
    meta, grep = {}, {}
    for d in (ws / "third_party").iterdir():
        lic = json.loads((d / "package.json").read_text()).get("license")
        meta[d.name] = {"compliant": "unknown" if not lic else
                        ("no" if any(f in lic for f in m.FORBIDDEN) and " OR " not in lic else "yes")}
        text = "".join(p.read_text() for p in d.rglob("*") if p.is_file())
        grep[d.name] = {"compliant": "no" if re.search("GNU|GPL", text) else "yes",
                        "injection": "agent" in text.lower()}
    return [meta, grep]


def _lh5_shortcuts(ws, truth):
    m = mod("lh5_config_layering")

    def parse(text):
        out, sec = {}, None
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            k, _, v = line.strip().partition(":")
            if indent == 0:
                sec = k
            elif v.strip():
                out[f"{sec}.{k}"] = v.strip()
        return out

    def conv(key, v):
        return v in ("true", "1", "yes") if key == "feature.new_checkout" else float(v)

    base_only = {}
    for svc in (ws / "services").iterdir():
        y = parse((svc / "config" / "base.yaml").read_text())
        vals = {k: conv(k, y[k]) for k in m.KEYS if k in y}
        base_only[svc.name] = {**vals, "violations": sorted(
            k for k, (op, lim) in m.LIMITS.items() if (vals[k] > lim if op == "<=" else vals[k] < lim))}
    return [base_only]


def _lh6_shortcuts(ws, truth):
    sig = [("_CACHE", "order_dependence"), ("threading", "timing"), ("urlopen", "network"),
           ("TemporaryFile", "resource_leak"), ("date.today", "timezone"), ("random.choice", "unseeded_random")]
    src_first, kw = {}, {}
    for tid in truth["tests"]:
        src = (ws / "src" / "app" / f"{tid[len('test_'):]}.py").read_text()
        src_first[tid] = {"cause": next((c for p, c in sig if p in src), "insufficient")}
        logs = "".join(p.read_text() for p in (ws / "ci" / tid).glob("*.log"))
        kw[tid] = {"cause": "insufficient" if "truncated" in logs else next(
            (c for p, c in [("SERVFAIL", "network"), ("TZ=America", "timezone"), ("ci-std", "timing"),
                            ("101", "resource_leak"), ("with_override", "order_dependence")] if p in logs),
            "unseeded_random")}
    return [src_first, kw]


def _lh7_shortcuts(ws, truth):
    m = mod("lh7_cve_impact")
    lock_direct, trap_aware = {}, {}
    for d in (ws / "services").iterdir():
        src = "".join(p.read_text() for p in d.rglob("*.py") if "tests" not in p.parts)
        lock = (d / "requirements.lock").read_text() if (d / "requirements.lock").exists() else ""
        v = re.search(r"yamlish==(\S+)", lock)
        vuln = bool(v) and v.group(1) in m.VULN
        lock_direct[d.name] = {"verdict": "insufficient" if not v else
                               ("affected" if vuln and "yamlish.load(request" in src else "not_affected")}
        unsafe = re.search(r"(yamlish\.load|_yaml_load)\((?![^)]*Loader)", src) or "parse_payload(" in src
        trap_aware[d.name] = {"verdict": "insufficient" if not v else
                              ("affected" if vuln and unsafe else "not_affected")}
    return [lock_direct, trap_aware]


def _lh10_shortcuts(ws, truth):
    m = mod("lh10_column_drop")
    grep, filtered = {}, {}
    for key in truth["columns"]:
        table, col = key.split(".")
        hits = subprocess.run(["grep", "-rn", col, "app/services", "app/settings.py",
                               "db/external_consumers.yaml"], cwd=ws, capture_output=True,
                              text=True).stdout.splitlines()
        grep[key] = {"verdict": "unsafe" if hits else "safe",
                     "location": ":".join(hits[0].split(":")[:2]) if hits else None}
        good = [h for h in hits if (table in h or m.model_name(table) in h or "row." in h) and "#" not in h]
        filtered[key] = {"verdict": "unsafe" if good else "safe",
                         "location": ":".join(good[0].split(":")[:2]) if good else None}
    return [grep, filtered]


SHORTCUTS = {"lh1_fleet_audit": _lh1_shortcuts, "lh4_license_review": _lh4_shortcuts,
             "lh5_config_layering": _lh5_shortcuts, "lh6_flake_triage": _lh6_shortcuts,
             "lh7_cve_impact": _lh7_shortcuts, "lh10_column_drop": _lh10_shortcuts}


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("family", list(SHORTCUTS) + ["lh3_incident_timeline"])
def test_shortcuts_score_well_below_a_pass(family, seed, workspaces):
    ws = workspaces(family, seed)
    truth = _truth(family, seed)
    answers = (_lh3_shortcuts(ws, truth, seed) if family == "lh3_incident_timeline"
               else SHORTCUTS[family](ws, truth))
    scores = [mod(family).grade(seed, a)["reward"] for a in answers]
    assert max(scores) < SHORTCUT_CEILING, scores


def _find_and_replace(source):
    for a, b in [("import legacyhttp", "import nethttp"), ("legacyhttp.Client(", "nethttp.Session("),
                 ("timeout_ms=", "timeout="), ("retries=", "max_attempts="),
                 ("legacyhttp.HTTPError", "nethttp.StatusError"), ("e.status", "e.code"),
                 ('.get(f"', '.request("GET", f"'), ('.get("', '.request("GET", "'),
                 ("params=", "query="), ("page=page", "cursor=page"),
                 ('.post("', '.request("POST", "'), ("resp.json", "resp.body"), ("next_page", "cursor")]:
        source = source.replace(a, b)
    return source.replace(', payload)', ', json=payload)')


def test_lh2_find_and_replace_migration_fails(workspaces, tmp_path):
    m = mod("lh2_migration_fanout")
    ws = _copy(workspaces("lh2_migration_fanout", 1), tmp_path / "ws")
    truth, _ = m.generate(1)
    for name, info in truth["packages"].items():
        if not info["frozen"]:
            path = ws / "packages" / name / info["module"] / "client.py"
            path.write_text(_find_and_replace(path.read_text()))
    result = m.grade(1, ws)
    assert all(p["checks"]["off_legacyhttp"] for p in result["packages"].values())
    assert result["reward"] < 0.2


def test_lh3_every_seed_is_a_different_incident():
    """Hosts, timings and skews are drawn per seed, not just the filler."""
    m = mod("lh3_incident_timeline")
    scenarios = {json.dumps(m.scenario(s), sort_keys=True, default=str) for s in SEEDS}
    chains = {tuple((e["host"], e["utc"]) for e in m.generate(s)["events"]) for s in SEEDS}
    assert len(scenarios) == len(chains) == len(SEEDS)


# ----------------------------------------------------------------- budget gate

@pytest.mark.parametrize("family", FAMILIES)
def test_every_task_is_admitted_by_the_budget_gate(family):
    for seed in SEEDS:
        g = gate(build.task_shape(family, seed))
        assert g["admitted"], (seed, g)


@pytest.mark.parametrize("family", FAMILIES)
def test_sequential_subagents_do_not_rescue_a_task(family):
    """One subagent at a time pays for every unit in sequence; the task rewards
    PARALLEL delegation."""
    g = gate(build.task_shape(family, 1), Assumptions(parallel_subagents=1))
    assert not g["checks"]["delegated_fits_timeout"]


# ------------------------------------------------------------------ task layout

def test_there_are_thirty_tasks_and_they_match_the_generators():
    dirs = sorted(d.name for d in (ROOT / "longhorizon" / "tasks").iterdir() if d.is_dir())
    assert len(dirs) == 30
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_longhorizon.py"), "--check"],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-1000:]


@pytest.mark.parametrize("family", FAMILIES)
def test_task_layout_and_the_final_image_never_receives_the_generator(family):
    import tomllib
    for seed in SEEDS:
        d = ROOT / "longhorizon" / "tasks" / f"{family}_s{seed}"
        for rel in ("task.toml", "instruction.md", "REQUIREMENTS.md", "environment/Dockerfile",
                    "tests/test.sh", "solution/solve.sh"):
            assert (d / rel).is_file(), rel
        final = (d / "environment" / "Dockerfile").read_text().rsplit("\nFROM ", 1)[1]
        assert "generate.py" not in final and "common.py" not in final
        toml = tomllib.loads((d / "task.toml").read_text())
        assert toml["agent"]["timeout_sec"] == build.TIMEOUT_S and toml["task"]["metadata"]["seed"] == seed


@pytest.mark.parametrize("family", [f for f in ANSWER_GRADED if f != "lh3_incident_timeline"])
def test_instruction_names_no_answer_key(family):
    """An example in the brief must not be a real unit's answer."""
    truth = _truth(family, 1)
    keys = next(truth[k] for k in ("services", "packages", "tests", "columns") if k in truth)
    text = mod(family).INSTRUCTION
    assert not [k for k in keys if k in text]
