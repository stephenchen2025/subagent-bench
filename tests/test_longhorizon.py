"""The long-horizon track, checked without a model and without Docker.

Pinned here, for all thirty families (one task each):

- the families are genuinely different: no two share a kind of work or a
  domain, and their briefs barely overlap;
- the generators are pure functions of their seed (the verifier depends on it);
- the reference solution scores 1.0, and doing nothing scores at most a small
  base rate;
- the shortcuts a single agent would reach for under time pressure -- grep,
  find-and-replace, keyword triage, one generic script for every unit, trusting
  labels and reported numbers -- score well below a passing grade. If one starts
  passing, the task has stopped needing per-unit work and must be redesigned;
- each family's hard constraint actually bites (frozen packages, end-of-life
  lines, the shared registry, no shelling out);
- every task passes the budget gate, and only because subagents run in PARALLEL.
"""

import copy
import csv
import datetime as dt
import hashlib
import importlib
import itertools
import json
import re
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "longhorizon" / "generators"
sys.path.insert(0, str(ROOT / "longhorizon"))
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(ROOT))

from budget import Assumptions, gate  # noqa: E402
from tools import build_longhorizon as build  # noqa: E402

FAMILIES = list(build.FAMILIES)
SEED = build.SEED
SHORTCUT_CEILING = 0.75   # a passing grade should be >= 0.9


def mod(family):
    return importlib.import_module(family)


def workspace_graded(family):
    return mod(family).ANSWER_PATH == "/workspace"


def _truth(family, seed=SEED, out=None):
    t = mod(family).generate(seed, out)
    return t[0] if isinstance(t, tuple) else t


def _tree(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def _oracle_answer(family):
    m = mod(family)
    return m.oracle_findings(SEED) if family == "lh1_fleet_audit" else m.oracle(SEED)


def _apply_oracle(family, ws):
    m = mod(family)
    (m.apply_oracle if hasattr(m, "apply_oracle") else m.solve)(SEED, ws)


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    """One generated workspace per family, built lazily and never modified."""
    cache = {}

    def get(family):
        if family not in cache:
            root = tmp_path_factory.mktemp(family)
            _truth(family, SEED, root)
            cache[family] = root / "workspace"
        return cache[family]
    return get


@pytest.fixture
def fresh(pristine, tmp_path):
    """A private, writable copy of a family's workspace."""
    counter = itertools.count()

    def get(family):
        return Path(shutil.copytree(pristine(family), tmp_path / f"ws{next(counter)}"))
    return get


# ------------------------------------------------------------------ distinctness

def _trigrams(text):
    words = re.findall(r"[a-z]+", text.lower())
    return {tuple(words[i:i + 3]) for i in range(len(words) - 2)}


def test_thirty_distinct_families_one_task_each():
    assert len(FAMILIES) == len(set(FAMILIES)) == 30
    kinds = [mod(f).META["kind"] for f in FAMILIES]
    domains = [mod(f).META["domain"] for f in FAMILIES]
    assert len(set(kinds)) == 30, sorted(k for k in kinds if kinds.count(k) > 1)
    assert len(set(domains)) == 30, sorted(d for d in domains if domains.count(d) > 1)


def test_no_two_briefs_are_near_duplicates():
    grams = {f: _trigrams(mod(f).INSTRUCTION) for f in FAMILIES}
    worst = max(((len(grams[a] & grams[b]) / len(grams[a] | grams[b]), a, b)
                 for a, b in itertools.combinations(FAMILIES, 2)))
    assert worst[0] < 0.15, worst


# ------------------------------------------------------------------ determinism

@pytest.mark.parametrize("family", FAMILIES)
def test_generator_is_a_pure_function_of_its_seed(family, tmp_path):
    a = _truth(family, SEED, tmp_path / "a")
    b = _truth(family, SEED, tmp_path / "b")
    assert a == b and _tree(tmp_path / "a") == _tree(tmp_path / "b")
    _truth(family, SEED + 1, tmp_path / "c")
    assert _tree(tmp_path / "a") != _tree(tmp_path / "c")


# -------------------------------------------------------- oracle and doing nothing

@pytest.mark.parametrize("family", FAMILIES)
def test_oracle_scores_full(family, fresh):
    m = mod(family)
    if workspace_graded(family):
        ws = fresh(family)
        _apply_oracle(family, ws)
        assert m.grade(SEED, ws)["reward"] == 1.0
    else:
        assert m.grade(SEED, _oracle_answer(family))["reward"] == 1.0


# Doing nothing earns only what is already right in the workspace: LH9's lines
# that must stay unpatched, LH17's flags that must stay, LH20's rows that have
# not drifted.
BASE_RATE = {"lh9_backport": 0.5, "lh17_flag_cleanup": 0.4, "lh20_docs_drift": 0.55}


@pytest.mark.parametrize("family", FAMILIES)
def test_doing_nothing_scores_at_most_the_base_rate(family, pristine):
    m = mod(family)
    if family == "lh15_perf_fixes":
        pytest.skip("covered by test_lh15_the_slow_originals_fail_the_budget (grading all 40 takes minutes)")
    got = m.grade(SEED, pristine(family) if workspace_graded(family) else {})["reward"]
    assert got <= BASE_RATE.get(family, 0.0)


def test_lh15_the_slow_originals_fail_the_budget(fresh):
    """Untouched functions are correct but slow: they must fail on time alone."""
    m = mod("lh15_perf_fixes")
    ws = fresh("lh15_perf_fixes")
    keep = {"dedupe_00", "pair_count_01"}
    for p in (ws / "perf").glob("*_*.py"):
        if p.stem not in keep:
            p.unlink()
    per = m.grade(SEED, ws)["modules"]
    assert all(per[k] == 0.0 for k in keep)


# ------------------------------------------------------------ constraints bite

def test_lh2_touching_billing_or_a_test_zeroes_the_task(fresh):
    m = mod("lh2_migration_fanout")
    ws = fresh("lh2_migration_fanout")
    m.apply_oracle(SEED, ws)
    billing = next((ws / "packages" / "billing-ledger").rglob("client.py"))
    billing.write_text(billing.read_text() + "\n# migrated too\n")
    assert m.grade(SEED, ws)["reward"] == 0.0

    ws2 = fresh("lh2_migration_fanout")
    m.apply_oracle(SEED, ws2)
    test = next((ws2 / "packages" / "orders" / "tests").glob("test_*.py"))
    test.write_text(test.read_text().replace("assert ", "assert True or ", 1))
    assert m.grade(SEED, ws2)["reward"] == 0.0


def test_lh2_believing_the_ci_note_costs_the_orders_package(fresh):
    m = mod("lh2_migration_fanout")
    ws = fresh("lh2_migration_fanout")
    m.apply_oracle(SEED, ws)
    truth, pristine_files = m.generate(SEED)
    rel = f"packages/orders/{truth['packages']['orders']['module']}/client.py"
    (ws / rel).write_text(pristine_files[rel])
    result = m.grade(SEED, ws)
    assert not result["poisoned_package_migrated"] and result["migrated"] == result["of"] - 1


def test_lh8_parallel_writers_that_each_rewrite_the_registry_lose_almost_everything(fresh):
    m = mod("lh8_plugin_port")
    ws = fresh("lh8_plugin_port")
    m.apply_oracle(SEED, ws)
    reg = (ws / "pluginapi" / "registry.py").read_text()
    lines = [line for line in reg.splitlines() if line.startswith('    "')]
    last_writer = lines[7::8]  # the 8th subagent's lane; it wrote last
    (ws / "pluginapi" / "registry.py").write_text(
        re.sub(r"PLUGINS = \{\n.*?\n\}", "PLUGINS = {\n" + "\n".join(last_writer) + "\n}", reg, flags=re.S))
    assert m.grade(SEED, ws)["reward"] <= 0.2


def test_lh9_patching_an_end_of_life_line_zeroes_the_task(fresh):
    m = mod("lh9_backport")
    ws = fresh("lh9_backport")
    truth, _ = m.generate(SEED)
    for v, info in truth["lines"].items():
        if info["affected"]:  # every vulnerable line, supported or not
            m.write(ws / "releases" / v, m.MODULE_PATH[info["era"]], m.ERA_CODE[info["era"]][1])
    result = m.grade(SEED, ws)
    assert result["reward"] == 0.0 and result["eol_lines_modified"]


def test_lh16_a_port_that_shells_out_to_the_original_earns_nothing(fresh):
    m = mod("lh16_shell_port")
    ws = fresh("lh16_shell_port")
    for name in _truth("lh16_shell_port")["scripts"]:
        m.write(ws / "py", f"{name}.py",
                "import subprocess, sys\n"
                f"sys.stdout.write(subprocess.run(['bash', {str(ws / 'scripts' / f'{name}.sh')!r}, *sys.argv[1:]],"
                " capture_output=True, text=True).stdout)\n")
    assert m.grade(SEED, ws)["reward"] < 0.25  # only the cases whose expected output is empty


# -------------------------------------------------------------------- shortcuts
#
# Each function takes a fresh-workspace factory and returns the scores of one
# or more shortcut strategies.

def _grade_all(family, answers):
    return [mod(family).grade(SEED, a)["reward"] for a in answers]


def _lh1(fresh):
    truth = _truth("lh1_fleet_audit")
    services = fresh("lh1_fleet_audit") / "services"
    all_clean = {n: {"verdict": "clean"} for n in truth["services"]}
    vendor = {n: {"verdict": "insufficient" if "from vendor." in "".join(
        p.read_text() for p in (services / n).rglob("*.py")) else "clean"} for n in truth["services"]}
    grep = {}
    for n in truth["services"]:
        src = "".join(p.read_text() for p in (services / n / "app" / "handlers").glob("*.py"))
        inline = re.search(r"!= user\.tenant_id|not in user\.roles|include_deleted=True, tenant", src)
        grep[n] = {"verdict": "clean" if inline else "violation", "location": "app/handlers/x.py:1"}
    return _grade_all("lh1_fleet_audit", [all_clean, vendor, grep])


def _lh2(fresh):
    m = mod("lh2_migration_fanout")
    ws = fresh("lh2_migration_fanout")
    truth, _ = m.generate(SEED)
    for name, info in truth["packages"].items():
        if not info["frozen"]:
            path = ws / "packages" / name / info["module"] / "client.py"
            text = path.read_text()
            for a, b in [("import legacyhttp", "import nethttp"), ("legacyhttp.Client(", "nethttp.Session("),
                         ("timeout_ms=", "timeout="), ("retries=", "max_attempts="),
                         ("legacyhttp.HTTPError", "nethttp.StatusError"), ("e.status", "e.code"),
                         ('.get(f"', '.request("GET", f"'), ('.get("', '.request("GET", "'),
                         ("params=", "query="), ("page=page", "cursor=page"),
                         ('.post("', '.request("POST", "'), ("resp.json", "resp.body"), ("next_page", "cursor")]:
                text = text.replace(a, b)
            path.write_text(text.replace(", payload)", ", json=payload)"))
    result = m.grade(SEED, ws)
    assert all(p["checks"]["off_legacyhttp"] for p in result["packages"].values())
    return [result["reward"]]


def _lh3(fresh):
    m = mod("lh3_incident_timeline")
    hosts, events = m.plan(SEED)
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
    return _grade_all("lh3_incident_timeline", out)


def _lh4(fresh):
    m = mod("lh4_license_review")
    ws = fresh("lh4_license_review")
    meta, grep = {}, {}
    for d in (ws / "third_party").iterdir():
        lic = json.loads((d / "package.json").read_text()).get("license")
        meta[d.name] = {"compliant": "unknown" if not lic else
                        ("no" if any(f in lic for f in m.FORBIDDEN) and " OR " not in lic else "yes")}
        text = "".join(p.read_text() for p in d.rglob("*") if p.is_file())
        grep[d.name] = {"compliant": "no" if re.search("GNU|GPL", text) else "yes",
                        "injection": "agent" in text.lower()}
    return _grade_all("lh4_license_review", [meta, grep])


def _lh5(fresh):
    m = mod("lh5_config_layering")
    ws = fresh("lh5_config_layering")

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
    return _grade_all("lh5_config_layering", [base_only])


def _lh6(fresh):
    truth = _truth("lh6_flake_triage")
    ws = fresh("lh6_flake_triage")
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
    return _grade_all("lh6_flake_triage", [src_first, kw])


def _lh7(fresh):
    """A generic checker: one/other plurals for every language, byte-counted
    limits, no do-not-translate list; and 'no errors anywhere'."""
    m = mod("lh7_i18n_qa")
    loc_dir = fresh("lh7_i18n_qa") / "locales"
    src = json.loads((loc_dir / "en.json").read_text())
    limits = json.loads((loc_dir / "ui_limits.json").read_text())
    saved = copy.deepcopy(m.PLURALS)
    generic = {}
    try:
        for k in m.PLURALS:
            m.PLURALS[k] = ["one", "other"]
        for loc in _truth("lh7_i18n_qa")["locales"]:
            tr = json.loads((loc_dir / f"{loc}.json").read_text())
            errs = [e for e in m.check(src, tr, loc.split("-")[0], limits, []) if not e.endswith(":E3")]
            generic[loc] = errs + [f"{k}:E3" for k, v in tr.items() if k in limits and len(v.encode()) > limits[k]]
    finally:
        m.PLURALS.clear()
        m.PLURALS.update(saved)
    return _grade_all("lh7_i18n_qa", [generic, {loc: [] for loc in generic}])


def _lh10(fresh):
    m = mod("lh10_column_drop")
    ws = fresh("lh10_column_drop")
    grep, filtered = {}, {}
    for key in _truth("lh10_column_drop")["columns"]:
        table, col = key.split(".")
        hits = subprocess.run(["grep", "-rn", col, "app/services", "app/settings.py",
                               "db/external_consumers.yaml"], cwd=ws, capture_output=True,
                              text=True).stdout.splitlines()
        grep[key] = {"verdict": "unsafe" if hits else "safe",
                     "location": ":".join(hits[0].split(":")[:2]) if hits else None}
        good = [h for h in hits if (table in h or m.model_name(table) in h or "row." in h) and "#" not in h]
        filtered[key] = {"verdict": "unsafe" if good else "safe",
                         "location": ":".join(good[0].split(":")[:2]) if good else None}
    return _grade_all("lh10_column_drop", [grep, filtered])


SMOKE_ARGS = {"clamp": "5, 1, 10", "roman": "4", "luhn": "'79927398713'", "semver": "'1.0.0', '1.0.0'",
              "duration": "'1h'", "business_days": "__import__('datetime').date(2026, 9, 21), 1",
              "money": "'1.5'", "slug": "'Hello World'", "chunk": "[1, 2, 3], 2", "pct": "50, 75"}


def _lh11(fresh):
    """Coverage-style smoke tests: one call per module, asserting it returns."""
    m = mod("lh11_test_authoring")
    ws = fresh("lh11_test_authoring")
    truth, _ = m.generate(SEED)
    for module, info in truth["modules"].items():
        fn = info["fn"]
        m.write(ws / "tests", f"test_{module}.py", f"from lib.{module} import {fn}\n\n\ndef test_smoke():\n"
                                                   f"    assert {fn}({SMOKE_ARGS[info['template']]}) is not None\n")
    return [m.grade(SEED, ws)["reward"]]


def _lh12(fresh):
    """Call every issue 'fixed': with no code change, and with correct code."""
    m = mod("lh12_issue_fixes")
    truth, _ = m.generate(SEED)
    all_fixed = json.dumps({i: {"resolution": "fixed"} for i in truth["issues"]})
    ws = fresh("lh12_issue_fixes")
    (ws / "triage.json").write_text(all_fixed)
    lazy = m.grade(SEED, ws)["reward"]
    m.solve(SEED, ws)
    (ws / "triage.json").write_text(all_fixed)
    return [lazy, m.grade(SEED, ws)["reward"]]


def _lh13(fresh):
    """Hard-code the numbers from the visible database; or write the right
    queries but bucket days in UTC."""
    m = mod("lh13_sql_reports")
    ws = fresh("lh13_sql_reports")
    questions = m.generate(SEED)["questions"]
    for qid, q in questions.items():
        rows = m._rows(ws / "warehouse.db", q["oracle_sql"])
        lit = " UNION ALL ".join("SELECT " + ", ".join(repr(v) for v in r) for r in rows) or "SELECT NULL"
        (ws / "answers" / f"{qid}.sql").write_text(lit + ";\n")
    hardcoded = m.grade(SEED, ws)["reward"]
    berlin = re.compile(r"\(CASE WHEN (\w+\.created_at) >= '[^']+' AND \1 < '[^']+' "
                        r"THEN datetime\(\1, '\+2 hours'\) ELSE datetime\(\1, '\+1 hours'\) END\)")
    for qid, q in questions.items():
        (ws / "answers" / f"{qid}.sql").write_text(berlin.sub(r"\1", q["oracle_sql"]) + ";\n")
    return [hardcoded, m.grade(SEED, ws)["reward"]]


def _lh14(fresh):
    """Split the fields right but keep timestamps and levels as written."""
    m = mod("lh14_log_parsers")
    ws = fresh("lh14_log_parsers")
    for name, info in m.generate(SEED)["formats"].items():
        src = (m.ORACLE.replace("__SPEC__", repr(info["spec"]))
               .replace('return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"', "return s")
               .replace("LEVEL[", "str.upper("))
        src = src.replace('str.upper(o["severity"]]', 'str.upper(o["severity"])').replace(
            "str.upper(m.group(2)]", "str.upper(m.group(2))")
        m.write(ws / "parsers", f"{name}.py", src)
    return [m.grade(SEED, ws)["reward"]]


def _lh15(fresh):
    """One fast rewrite per function shape, ignoring each copy's variant."""
    m = mod("lh15_perf_fixes")
    ws = fresh("lh15_perf_fixes")
    for u in m.plan(SEED):
        fields = dict(m.T[u["template"]][3][0], fn=u["fields"]["fn"])
        m.write(ws / "perf", f"{u['module']}.py", m._fmt(m.T[u["template"]][1], fields))
    return [m.grade(SEED, ws)["reward"]]


def _lh16(fresh):
    """Plausible ports of two pipeline kinds that ignore the tools' edge cases
    (tie order in `sort | uniq -c`, awk's number formatting), scored on the
    scripts of those kinds only."""
    m = mod("lh16_shell_port")
    ws = fresh("lh16_shell_port")
    ported = []
    for name, info in m.generate(SEED)["scripts"].items():
        fields = info["unit"]["fields"]
        if info["unit"]["template"] == "top_ips":
            m.write(ws / "py", f"{name}.py", "import sys\nfrom collections import Counter\n"
                    "c = Counter(line.split(' ')[0] for line in open(sys.argv[1]).read().splitlines())\n"
                    f"for ip, n in c.most_common({fields['n']}):\n    print(f'{{n:7d}} {{ip}}')\n")
        elif info["unit"]["template"] == "csv_sum":
            m.write(ws / "py", f"{name}.py", "import sys\ns = {}\n"
                    "for line in open(sys.argv[1]).read().splitlines()[1:]:\n    p = line.split(',')\n"
                    f"    s[p[0]] = s.get(p[0], 0) + float(p[{fields['col'] - 1}])\n"
                    "for k in sorted(s):\n    print(k, s[k])\n")
        else:
            continue
        ported.append(name)
    per = m.grade(SEED, ws)["scripts"]
    assert ported
    return [sum(per[n] for n in ported) / len(ported)]


def _lh17(fresh):
    """Trust the status label in flags.yaml instead of the rollout history."""
    m = mod("lh17_flag_cleanup")
    ws = fresh("lh17_flag_cleanup")
    truth, files = m.generate(SEED)
    keep = []
    for name, info in truth["flags"].items():
        label = re.search(rf"- name: {name}\n.*\n    status: (\S+)", files["flags.yaml"]).group(1)
        fake = dict(info, kind={"on": "remove_on", "off": "remove_off", "ramping": "keep_ramping"}[label])
        if fake["kind"].startswith("remove"):
            text = files[f"app/{info['module']}.py"]
            orig = m.source(info["shape"], name, info["fn"], info["on"], info["off"])
            m.write(ws / "app", f"{info['module']}.py", text.replace(orig, m._cleaned(fake)))
        else:
            keep.append(name)
    out, skip = [], False
    for line in files["flags.yaml"].splitlines():
        hit = re.match(r"\s*- name: (\S+)", line)
        if hit:
            skip = hit.group(1) not in keep
        if not skip:
            out.append(line)
    (ws / "flags.yaml").write_text("\n".join(out) + "\n")
    return [m.grade(SEED, ws)["reward"]]


def _lh18(fresh):
    """Generic hardening: pin whatever tag is there, add USER and a /health
    check on 8080, drop every ENV/ARG with a secret-sounding name."""
    m = mod("lh18_docker_hardening")
    ws = fresh("lh18_docker_hardening")
    for name in m.generate(SEED)["services"]:
        p = ws / "services" / name / "Dockerfile"
        out = []
        for line in p.read_text().splitlines():
            if line.startswith("FROM "):
                img = line.split()[1]
                line = line.replace(img, f"{img}@{m.digest(img)}", 1)
            if line.split(" ")[0] in ("ENV", "ARG") and re.search("KEY|TOKEN|SECRET|PASSWORD", line):
                continue
            out.append(line)
        tail = out.pop()
        out += ["USER app", "HEALTHCHECK CMD curl -fsS http://localhost:8080/health || exit 1", tail]
        p.write_text("\n".join(out) + "\n")
    return [m.grade(SEED, ws)["reward"]]


def _lh19(fresh):
    """Regex fixes: lang="en" everywhere, alt from data attributes, aria-label
    from data-action; no heading or label repairs."""
    m = mod("lh19_a11y_fixes")
    ws = fresh("lh19_a11y_fixes")
    for page in m.generate(SEED)["pages"]:
        f = ws / "site" / "pages" / f"{page}.html"
        s = f.read_text().replace("<html>", '<html lang="en">')
        s = re.sub(r'<img ([^>]*?)data-description="([^"]*)"', r'<img \1data-description="\2" alt="\2"', s)
        s = s.replace('class="decorative"', 'class="decorative" alt="image"')
        s = re.sub(r'data-action="([^"]*)"', r'data-action="\1" aria-label="\1"', s)
        f.write_text(s)
    return [m.grade(SEED, ws)["reward"]]


def _lh20(fresh):
    """Regenerate every table by introspecting the parsers at runtime: misses
    environment defaults and values filled in after parsing."""
    import argparse
    import importlib.util
    m = mod("lh20_docs_drift")
    ws = fresh("lh20_docs_drift")
    for name in m.generate(SEED)["tools"]:
        spec = importlib.util.spec_from_file_location(f"tool_{name}", ws / "tools" / f"{name}.py")
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        rows = []
        for a in tool.build_parser()._actions:
            if a.help in (None, argparse.SUPPRESS) or not a.option_strings or "--help" in a.option_strings:
                continue
            d = a.default
            ds = "`none`" if d is None else f"`{str(d).lower() if isinstance(d, bool) else d}`"
            choices = (" One of: " + ", ".join(a.choices) + ".") if a.choices else ""
            rows.append(f"| {', '.join(f'`{o}`' for o in a.option_strings)} | {ds} | {a.help}{choices} |")
        doc = ws / "docs" / "cli" / f"{name}.md"
        head, _, rest = doc.read_text().partition("|---|---|---|\n")
        doc.write_text(head + "|---|---|---|\n" + "\n".join(rows) + "\n\n" + rest.partition("\n\n")[2])
    return [m.grade(SEED, ws)["reward"]]


def _lh21(fresh):
    """One cleaner for every dataset, ignoring each spec's parameters."""
    m = mod("lh21_data_cleaning")
    ws = fresh("lh21_data_cleaning")
    cfg = {"cc": "31", "date_fmt": "dmy", "money_fmt": "eu", "synonyms": m.SYNONYMS[0],
           "steps": ["trim", "key_upper", "phone", "date", "name", "money", "email", "dedupe", "sort"],
           "sort": ["customer_id"]}
    for name in m.generate(SEED)["datasets"]:
        rows = list(csv.DictReader(open(ws / "data" / name / "raw.csv")))
        try:
            header, cleaned = m.clean(rows, cfg)
        except Exception:  # a dataset the generic cleaner cannot handle at all
            continue
        m.write(ws / "clean", f"{name}.csv", m.to_csv(header, cleaned))
    return [m.grade(SEED, ws)["reward"]]


def _lh22(fresh):
    """Match ledger and bank by reference only; no batch or amount checks."""
    ws = fresh("lh22_reconciliation")
    ans = {}
    for n in _truth("lh22_reconciliation")["merchants"]:
        led = {r["id"] for r in csv.DictReader(open(ws / "recon" / n / "ledger.csv"))}
        bank = [r["ref"] for r in csv.DictReader(open(ws / "recon" / n / "bank.csv"))]
        ans[n] = {"unsettled": sorted(led - set(bank)) if not any(b.startswith("BATCH") for b in bank) else [],
                  "unexpected": sorted(b for b in bank if b not in led and not b.startswith("BATCH")),
                  "bad_batches": []}
    return _grade_all("lh22_reconciliation", [ans, {n: {} for n in ans}])


def _lh23(fresh):
    """Naive statistics (bots kept, equal split assumed, no correction, no
    metric check), and trusting every write-up."""
    m = mod("lh23_experiment_audit")
    ws = fresh("lh23_experiment_audit")
    exps = _truth("lh23_experiment_audit")["experiments"]
    ans = {}
    for e in exps:
        d = ws / "experiments" / e
        pre = (d / "PREREG.md").read_text()
        metric = re.search(r"column `(\w+)`", pre).group(1)
        arms = re.search(r"Arms: ([^(]+)\(", pre).group(1).strip().split(", ")
        minimum = int(re.search(r"Minimum sample: (\d+)", pre).group(1))
        rows = list(csv.DictReader(open(d / "assignments.csv")))
        counts = [sum(1 for r in rows if r["arm"] == a) for a in arms]
        v = ("srm" if m.srm_p(counts, [1 / len(arms)] * len(arms)) < 0.001
             else "underpowered" if min(counts) < minimum else None)
        if not v:
            c = [r for r in rows if r["arm"] == arms[0]]
            b = [r for r in rows if r["arm"] == arms[-1]]
            p, z = m.z_p(sum(int(r[metric]) for r in c), len(c), sum(int(r[metric]) for r in b), len(b))
            v = "supported" if p < 0.05 and z > 0 else "not_significant"
        ans[e] = {"verdict": v}
    return _grade_all("lh23_experiment_audit", [ans, {e: {"verdict": "supported"} for e in exps}])


def _lh24(fresh):
    """Read the base contract only, with simple regexes: amendments ignored."""
    ws = fresh("lh24_contract_terms")
    ans = {}
    for slug in _truth("lh24_contract_terms")["contracts"]:
        txt = (ws / "contracts" / slug / "CONTRACT.md").read_text()

        def num(p, txt=txt):
            hit = re.search(p, txt)
            return int(hit.group(1)) if hit else None
        cap = re.search(r"capped at EUR ([\d,]+)\.", txt)
        ans[slug] = {"term_months": num(r"Initial Term is .*?\((\d+)\) months"),
                     "auto_renew": "renews automatically" in txt,
                     "notice_days": num(r"giving .*?\((\d+)\)"),
                     "governing_law": re.search(r"governed by the laws of (.+)\.", txt).group(1),
                     "liability_cap_eur": float(cap.group(1).replace(",", "")) if cap else None}
    return _grade_all("lh24_contract_terms", [ans])


def _lh25(fresh):
    """Keyword triage, plan assumed 'pro', no KB lookup, no duplicate check."""
    m = mod("lh25_ticket_triage")
    ws = fresh("lh25_ticket_triage")
    ans = {}
    for tid in _truth("lh25_ticket_triage")["tickets"]:
        txt = (ws / "tickets" / f"{tid}.md").read_text().lower()
        cat = ("security" if re.search("security|token|login alert", txt) else
               "data_loss" if "missing" in txt or "gone" in txt else
               "billing" if "charge" in txt or "refund" in txt else
               "account_access" if "password" in txt or "locked" in txt else
               "bug" if re.search("error|broken|fail|410|pending|blank", txt) else
               "how_to" if "how" in txt or "?" in txt else "feature_request")
        route = {"security": "security", "data_loss": "security", "bug": "engineering"}.get(cat, "support")
        ans[tid] = {"category": cat, "priority": m.MATRIX["pro"][m.SEVERITY[cat]], "route": route,
                    "kb_article": None, "duplicate_of": None}
    return _grade_all("lh25_ticket_triage", [ans])


def _lh26(fresh):
    """Reimburse everything at the trip-start exchange rate; flag nothing."""
    m = mod("lh26_expense_audit")
    ws = fresh("lh26_expense_audit")
    fx = m.rates(SEED)
    ans = {}
    for rid in _truth("lh26_expense_audit")["reports"]:
        rep = json.loads((ws / "reports" / f"{rid}.json").read_text())
        start = dt.date.fromisoformat(rep["start"])
        total = sum(m.to_eur(Decimal(ln["amount"]), ln["currency"], start, fx) for ln in rep["lines"])
        ans[rid] = {"reimbursable_eur": str(total), "broken": []}
    return _grade_all("lh26_expense_audit", [ans])


def _lh27(fresh):
    """The full mechanical scanner: patterns, tracked files, placeholders and
    the revocation list -- but no reading of assembled or encoded values."""
    ws = fresh("lh27_secret_leaks")
    revoked = set((ws / "security" / "revoked_sha256.txt").read_text().split())
    pat = re.compile(r"(ghp_[0-9a-fx]{36}|AKIA[A-Z2-7]{16}|xoxb-\d{12}-[0-9a-f]{24}|sk_(live|test)_[0-9a-f]{24}"
                     r"|-----BEGIN RSA PRIVATE KEY-----)")
    ans = {}
    for n in _truth("lh27_secret_leaks")["repos"]:
        root = ws / "repos" / n
        tracked = set((root / "TRACKED_FILES.txt").read_text().split())
        hits = []
        for f in sorted(root.rglob("*")):
            if not f.is_file() or f.name == "TRACKED_FILES.txt":
                continue
            rel = str(f.relative_to(root))
            for i, line in enumerate(f.read_text().splitlines(), 1):
                hit = pat.search(line)
                if (hit and rel in tracked and "EXAMPLE" not in line and "sk_test" not in line
                        and "x" * 20 not in line
                        and hashlib.sha256(hit.group(0).encode()).hexdigest() not in revoked):
                    hits.append(f"{rel}:{i}")
        ans[n] = hits
    return _grade_all("lh27_secret_leaks", [ans, {n: [] for n in ans}])


def _lh28(fresh):
    """An evaluator without conditions or boundaries; one that folds resource
    case; and 'deny everything'."""
    m = mod("lh28_iam_access")
    ws = fresh("lh28_iam_access")
    pols = {p.stem: json.loads(p.read_text()) for p in (ws / "iam" / "policies").glob("*.json")}
    groups = json.loads((ws / "iam" / "groups.json").read_text())
    prins = json.loads((ws / "iam" / "principals.json").read_text())
    naive, folded = {}, {}
    for n, pr in prins.items():
        docs = [pols[x] for x in pr["policies"]] + [pols[x] for g in pr["groups"] for x in groups[g]]
        qs = re.findall(r"`([^`]+)` on `([^`]+)` from `([^`]+)` at `([^`]+)`",
                        (ws / "questions" / f"{n}.md").read_text())
        stm = [dict(s, Condition=None) for d in docs for s in d["Statement"]]
        naive[n] = [m.evaluate([{"Statement": stm}], None, a, r, {"ip": ip, "time": tm, "tags": pr["tags"]})
                    for a, r, ip, tm in qs]
        boundary = pols.get(pr["permission_boundary"]) if pr["permission_boundary"] else None
        lowered = [{"Statement": [dict(s, Resource=[x.lower() for x in s["Resource"]]) for s in d["Statement"]]}
                   for d in docs]
        folded[n] = [m.evaluate(lowered, boundary, a, r.lower(), {"ip": ip, "time": tm, "tags": pr["tags"]})
                     for a, r, ip, tm in qs]
    return _grade_all("lh28_iam_access", [naive, folded, {n: ["deny"] * 5 for n in prins}])


def _lh29(fresh):
    """Schedules computed while ignoring one calendar rule, or all of them."""
    m = mod("lh29_fictional_calendars")
    orig = copy.deepcopy(m.REGIONS)
    patches = [lambda r: r.update(dst=None), lambda r: r.update(weekend=(5, 6)),
               lambda r: r.update(fixed=[], rules=[]),
               lambda r: r.update(dst=None, weekend=(5, 6), fixed=[], rules=[])]
    scores = []
    try:
        for patch in patches:
            m.REGIONS.clear()
            m.REGIONS.update(copy.deepcopy(orig))
            for region in m.REGIONS.values():
                patch(region)
            runs = {n: t["runs"] for n, t in m.generate(SEED)["jobs"].items()}
            m.REGIONS.clear()
            m.REGIONS.update(copy.deepcopy(orig))
            scores.append(m.grade(SEED, runs)["reward"])
    finally:
        m.REGIONS.clear()
        m.REGIONS.update(orig)
    return scores


def _lh30(fresh):
    """Always valid, always invalid, and 'right shape, any check character'."""
    m = mod("lh30_spec_validators")
    ws = fresh("lh30_spec_validators")
    formats = m.generate(SEED)["formats"]
    scores = []
    for val in ("True", "False"):
        for name in formats:
            m.write(ws / "validators", f"{name}.py", f"def is_valid(text):\n    return {val}\n")
        scores.append(m.grade(SEED, ws)["reward"])
    for name, x in formats.items():
        m.write(ws / "validators", f"{name}.py", f"""import sys
sys.path.insert(0, {str(GEN)!r})
import lh30_spec_validators as g
P = {dict(x["params"])!r}


def is_valid(text):
    if P["kind"] in ("weighted", "mod97", "luhn_sep", "dated"):
        for c in "0123456789XK":
            cand = text[:-1] + c if P["kind"] != "mod97" else text[:2] + (c * 2 if c.isdigit() else "00") + text[4:]
            if g.validate(P, cand):
                return True
        return False
    return g.validate(P, text)
""")
    scores.append(m.grade(SEED, ws)["reward"])
    return scores


SHORTCUTS = {f: globals()["_" + f.split("_")[0]] for f in FAMILIES if "_" + f.split("_")[0] in globals()}


def test_every_family_has_a_shortcut_check():
    """LH8's and LH9's shortcuts are their constraint tests above: parallel
    writers clobbering the registry, one patch applied to every line."""
    assert set(FAMILIES) - set(SHORTCUTS) == {"lh8_plugin_port", "lh9_backport"}


@pytest.mark.parametrize("family", sorted(SHORTCUTS))
def test_shortcuts_score_well_below_a_pass(family, fresh):
    scores = SHORTCUTS[family](fresh)
    assert scores and max(scores) < SHORTCUT_CEILING, scores


def test_lh3_every_seed_is_a_different_incident():
    """Hosts, timings and skews are drawn per seed, not just the filler."""
    m = mod("lh3_incident_timeline")
    seeds = (1, 2, 3)
    scenarios = {json.dumps(m.scenario(s), sort_keys=True, default=str) for s in seeds}
    chains = {tuple((e["host"], e["utc"]) for e in m.generate(s)["events"]) for s in seeds}
    assert len(scenarios) == len(chains) == len(seeds)


def test_lh13_hidden_database_answers_are_not_trivial(tmp_path):
    """No question's answer on the grading database is empty or zero."""
    m = mod("lh13_sql_reports")
    db = m._hidden_db(SEED, tmp_path)
    for q in m.generate(SEED)["questions"].values():
        rows = m._rows(db, q["oracle_sql"])
        assert rows and rows not in ([(None,)], [(0,)])


# ----------------------------------------------------------------- budget gate

@pytest.mark.parametrize("family", FAMILIES)
def test_every_task_is_admitted_by_the_budget_gate(family):
    g = gate(build.task_shape(family, SEED))
    assert g["admitted"], g


@pytest.mark.parametrize("family", FAMILIES)
def test_sequential_subagents_do_not_rescue_a_task(family):
    """One subagent at a time pays for every unit in sequence; the task rewards
    PARALLEL delegation."""
    g = gate(build.task_shape(family, SEED), Assumptions(parallel_subagents=1))
    assert not g["checks"]["delegated_fits_timeout"]


# ------------------------------------------------------------------ task layout

def test_there_are_thirty_tasks_and_they_match_the_generators():
    dirs = sorted(d.name for d in (ROOT / "longhorizon" / "tasks").iterdir() if d.is_dir())
    assert dirs == sorted(FAMILIES)
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_longhorizon.py"), "--check"],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-1000:]


@pytest.mark.parametrize("family", FAMILIES)
def test_task_layout_and_the_final_image_never_receives_the_generator(family):
    import tomllib
    d = ROOT / "longhorizon" / "tasks" / family
    for rel in ("task.toml", "instruction.md", "REQUIREMENTS.md", "environment/Dockerfile",
                "tests/test.sh", "solution/solve.sh"):
        assert (d / rel).is_file(), rel
    final = (d / "environment" / "Dockerfile").read_text().rsplit("\nFROM ", 1)[1]
    assert "generate.py" not in final and "common.py" not in final
    toml = tomllib.loads((d / "task.toml").read_text())
    assert toml["agent"]["timeout_sec"] == build.TIMEOUT_S and toml["metadata"]["seed"] == SEED


@pytest.mark.parametrize("family", FAMILIES)
def test_task_toml_follows_harbor_schema(family):
    """The fields Harbor's TaskConfig validates or silently drops, as DeepSWE
    lays them out: `org/name`, a top-level [metadata] (a nested
    [task.metadata] is ignored without an error), no network for the agent or
    the verifier (Harbor defaults to public), and pinned CPU and memory, since
    the timeout argument depends on speed. `tools/check_harbor.py` runs
    Harbor's own validator."""
    import tomllib
    toml = tomllib.loads((ROOT / "longhorizon" / "tasks" / family / "task.toml").read_text())
    assert toml["schema_version"] == build.HARBOR_SCHEMA_VERSION
    assert set(toml["task"]) <= {"name", "version", "description", "authors", "keywords"}
    assert re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", toml["task"]["name"])
    assert toml["task"]["name"] == f"{build.ORG}/{family}" and toml["task"]["description"]
    assert toml["metadata"]["family"] == family
    for phase in ("agent", "verifier", "environment"):
        assert toml[phase]["network_mode"] == "no-network", phase
    env = toml["environment"]
    assert env["cpus"] == build.CPUS and env["memory_mb"] == build.MEMORY_MB and env["workdir"] == "/workspace"


def test_task_toml_passes_harbors_own_validator():
    harbor_config = pytest.importorskip("harbor.models.task.config", reason="harbor needs Python >= 3.12")
    for family in FAMILIES:
        text = (ROOT / "longhorizon" / "tasks" / family / "task.toml").read_text()
        harbor_config.TaskConfig.model_validate_toml(text)


def _unit_keys(truth):
    """The per-unit ids: the largest dict in the ground truth."""
    return max((v for v in truth.values() if isinstance(v, dict)), key=len)


@pytest.mark.parametrize("family", [f for f in FAMILIES if f != "lh3_incident_timeline"])
def test_instruction_names_no_unit(family):
    """An example in the brief must not be a real unit (or its answer)."""
    text = mod(family).INSTRUCTION
    leaked = [k for k in _unit_keys(_truth(family)) if len(k) >= 4 and re.search(rf"\b{re.escape(k)}\b", text)]
    assert not leaked
