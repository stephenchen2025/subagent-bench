#!/usr/bin/env python3
"""LH17 -- clean up 48 feature flags, deciding each from its rollout history.

app/ checks 30 feature flags through `flags.enabled("<name>")`. flags.yaml
records each flag's rollout history. docs/FLAGS.md sets the policy, as of
2026-09-26:

- a flag whose LAST event set it to 100% on or before 2026-08-27 is done:
  delete the flag and keep the enabled code path;
- a flag whose last event set it to 0% on or before 2026-08-27 is dead:
  delete the flag and keep the disabled code path;
- anything else (still ramping, or changed within 30 days) stays exactly as is.

Every flag is its own small decision plus a refactor. Traps:

- `status:` in flags.yaml is a cached label and is stale for some flags; the
  history decides;
- the check comes in five shapes: if/else, `if not`, a ternary, combined with
  another condition (`enabled(x) and order.get("beta")` must become just the
  other condition), and hidden behind a helper function;
- a flag that must stay has to keep working both ways.

    python3 lh17_flag_cleanup.py --seed 1 --out /fixture
"""

import datetime as dt
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, rng_for, run_pytest, standard_main, write  # noqa: E402

N_FLAGS = 48
TODAY = dt.date(2026, 9, 26)
CUTOFF = TODAY - dt.timedelta(days=30)  # 2026-08-27
KINDS = {"remove_on": 17, "remove_off": 13, "keep_recent": 10, "keep_ramping": 8}
SHAPES = ["ifelse", "negated", "ternary", "combined", "helper"]
EXPRS = [("round(order[\"total\"] * 0.95, 2)", "order[\"total\"]"),
         ("order[\"total\"] + 4.99", "order[\"total\"]"),
         ("sorted(order[\"items\"])", "list(order[\"items\"])"),
         ("len(order[\"items\"]) * 2", "len(order[\"items\"])"),
         ("order[\"total\"] > 100", "order[\"total\"] > 150"),
         ("\"express\"", "\"standard\"")]
NAMES = ["new_checkout", "fast_search", "smart_pricing", "one_click", "bulk_edit", "dark_mode_email",
         "async_invoices", "geo_tax", "cart_v2", "promo_engine", "lazy_images", "split_payments",
         "wishlist_share", "loyalty_boost", "returns_portal", "instant_refund", "fraud_rules_v3",
         "rich_receipts", "address_autofill", "express_lane", "gift_wrap", "subscriptions_v2",
         "live_chat", "reorder_button", "price_alerts", "store_pickup", "multi_currency",
         "saved_carts", "vendor_portal", "bundle_offers", "smart_sort", "quick_view", "guest_checkout",
         "order_notes", "tax_preview", "cart_reminders", "size_guide", "image_zoom", "wallet_pay", "coupon_stack",
         "fast_refunds", "b2b_pricing", "photo_reviews", "stock_alerts", "eco_shipping", "voice_search",
         "trial_plans", "annual_billing", "pickup_slots", "compare_view", "bulk_import", "team_seats"]

FLAGS_PY = '''"""Feature flag client. In production this calls the flag service."""

_OVERRIDES = {}


def enabled(name):
    return _OVERRIDES.get(name, False)
'''


def source(shape, flag, fn, on, off):
    if shape == "ifelse":
        return f'''def {fn}(order):
    if flags.enabled("{flag}"):
        return {on}
    return {off}
'''
    if shape == "negated":
        return f'''def {fn}(order):
    if not flags.enabled("{flag}"):
        return {off}
    return {on}
'''
    if shape == "ternary":
        return f'''def {fn}(order):
    return {on} if flags.enabled("{flag}") else {off}
'''
    if shape == "combined":
        return f'''def {fn}(order):
    if flags.enabled("{flag}") and order.get("beta"):
        return {on}
    return {off}
'''
    return f'''def _use_{flag}():
    return flags.enabled("{flag}")


def {fn}(order):
    return {on} if _use_{flag}() else {off}
'''


def expected_value(shape, on_val, off_val, flag_on, beta):
    if shape == "combined":
        return on_val if (flag_on and beta) else off_val
    return on_val if flag_on else off_val


def history(rng, kind):
    d = dt.date(2026, 3, 1) + dt.timedelta(days=rng.randint(0, 60))
    events = []
    for pct in (1, 10, 50):
        events.append((d, pct))
        d += dt.timedelta(days=rng.randint(5, 20))
    if kind == "remove_on":
        events.append((min(d, CUTOFF - dt.timedelta(days=rng.randint(0, 40))), 100))
    elif kind == "remove_off":
        if rng.random() < 0.5:
            events.append((d, 100))
            d += dt.timedelta(days=5)
        events.append((min(d, CUTOFF - dt.timedelta(days=rng.randint(0, 40))), 0))
    elif kind == "keep_recent":
        events.append((CUTOFF + dt.timedelta(days=rng.randint(1, 25)), rng.choice([0, 100])))
    else:
        events.append((CUTOFF - dt.timedelta(days=rng.randint(10, 60)), rng.choice([20, 50, 75])))
    # Dates must be non-decreasing.
    fixed, last = [], dt.date(2026, 1, 1)
    for day, pct in events:
        day = max(day, last)
        fixed.append((day, pct))
        last = day
    return fixed


def plan(seed):
    rng = rng_for(seed, "plan")
    kinds = sum(([k] * v for k, v in KINDS.items()), [])
    rng.shuffle(kinds)
    names = rng.sample(NAMES, N_FLAGS)
    flags = []
    for i, (name, kind) in enumerate(zip(names, kinds)):
        frng = rng_for(seed, "flag", name)
        on, off = frng.choice(EXPRS)
        hist = history(frng, kind)
        last_pct = hist[-1][1]
        label = "on" if last_pct == 100 else "off" if last_pct == 0 else "ramping"
        if frng.random() < 0.3:  # a stale cached label
            label = frng.choice([x for x in ("on", "off", "ramping") if x != label])
        flags.append({"name": name, "kind": kind, "shape": SHAPES[i % len(SHAPES)], "on": on, "off": off,
                      "fn": f"{frng.choice(['price', 'route', 'plan', 'decide'])}_{name}",
                      "module": f"{name}_{i:02d}", "history": hist, "label": label})
    return flags


def generate(seed, out=None):
    flags = plan(seed)
    files = {"app/__init__.py": "", "app/flags.py": FLAGS_PY, "tests/__init__.py": "",
             "tests/conftest.py": "import sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n",
             "pytest.ini": "[pytest]\naddopts = -q -p no:cacheprovider --import-mode=importlib\n"}
    yaml = ["# Rollout history for every flag. `status` is a cached label; `history` is authoritative.", "flags:"]
    truth = {"seed": seed, "flags": {}}
    for f in flags:
        rng = rng_for(seed, "code", f["name"])
        filler = "\n\n".join(filler_function(rng) for _ in range(rng.randint(4, 8)))
        files[f"app/{f['module']}.py"] = (f'"""{f["module"]}."""\n\nfrom app import flags\n\n\n'
                                          + source(f["shape"], f["name"], f["fn"], f["on"], f["off"])
                                          + "\n\n" + filler + "\n")
        yaml += [f"  - name: {f['name']}", f"    owner: team-{rng.choice(['growth', 'payments', 'core', 'search'])}",
                 f"    status: {f['label']}", "    history:"]
        yaml += [f"      - {{date: {d.isoformat()}, percent: {p}}}" for d, p in f["history"]]
        truth["flags"][f["name"]] = {**{k: f[k] for k in ("kind", "shape", "on", "off", "fn", "module")},
                                     "unit_chars": len(files[f"app/{f['module']}.py"]) + 800}
    files["flags.yaml"] = "\n".join(yaml) + "\n"
    files["docs/FLAGS.md"] = FLAGS_MD
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


FLAGS_MD = f"""# Flag cleanup policy (as of {TODAY.isoformat()})

A flag's state is the percentage set by the LAST event in its `history`.
The `status` field is a cached label that is not always up to date.

- Last event 100%, dated {CUTOFF.isoformat()} or earlier: the rollout is done. Remove
  the flag from the code, keeping the enabled behaviour, and remove its entry
  from flags.yaml.
- Last event 0%, dated {CUTOFF.isoformat()} or earlier: the flag is dead. Remove it
  from the code, keeping the disabled behaviour, and remove its entry from
  flags.yaml.
- Anything else: leave the flag, its code and its entry exactly as they are.

Removing a flag must not change what the code does for any order, given the
flag's final state.
"""

TEST_TMPL = '''import pytest

from app import flags
from app.{module} import {fn}

ORDERS = [{{"total": 80.0, "items": ["b", "a"], "beta": True}}, {{"total": 200.0, "items": ["c"], "beta": False}},
          {{"total": 120.0, "items": [], "beta": True}}]


def _on(v):
    return {on_expr}


def _off(v):
    return {off_expr}


@pytest.mark.parametrize("order", ORDERS)
def test_behaviour(monkeypatch, order):
{body}
'''


def _test_for(name, info):
    on_expr = info["on"].replace("order[", "v[")
    off_expr = info["off"].replace("order[", "v[")
    beta = ' and order.get("beta")' if info["shape"] == "combined" else ""
    if info["kind"] in ("remove_on", "remove_off"):
        final = info["kind"] == "remove_on"
        body = (f"    def enabled(n):\n        if n == {name!r}:\n            raise AssertionError('flag still checked')\n"
                f"        return False\n    monkeypatch.setattr(flags, 'enabled', enabled)\n"
                f"    want = _on(order) if ({final}{beta}) else _off(order)\n"
                f"    assert {info['fn']}(order) == want\n")
    else:
        body = ("    for state in (True, False):\n"
                f"        monkeypatch.setattr(flags, 'enabled', lambda n, s=state: s if n == {name!r} else False)\n"
                f"        want = _on(order) if (state{beta}) else _off(order)\n"
                f"        assert {info['fn']}(order) == want\n")
    return TEST_TMPL.format(module=info["module"], fn=info["fn"], on_expr=on_expr, off_expr=off_expr, body=body)


def grade(seed, workspace):
    """Per flag: the hidden behaviour test passes against the agent's module --
    for removed flags with the flag no longer consulted, for kept flags in both
    states -- and flags.yaml lists exactly the flags that should remain."""
    truth, pristine = generate(seed)
    ws = Path(workspace)
    yaml = (ws / "flags.yaml").read_text() if (ws / "flags.yaml").exists() else ""
    listed = set(re.findall(r"^\s*- name: (\S+)", yaml, re.M))
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for rel in ("app/__init__.py", "app/flags.py", "tests/__init__.py", "tests/conftest.py", "pytest.ini"):
            write(tmp, rel, pristine[rel])
        for name, info in truth["flags"].items():
            src = ws / "app" / f"{info['module']}.py"
            if not src.exists():
                per[name] = 0.0
                continue
            shutil.copy(src, tmp / "app" / f"{info['module']}.py")
            write(tmp, f"tests/test_{name}.py", _test_for(name, info))
            ok, _ = run_pytest(tmp, f"tests/test_{name}.py", timeout=60)
            should_list = info["kind"].startswith("keep")
            per[name] = float(ok and ((name in listed) == should_list))
    return {"reward": round(sum(per.values()) / len(per), 4), "flags": per}


def _cleaned(info):
    """The module with the flag removed, keeping the given branch."""
    on, off = info["on"], info["off"]
    keep_on = info["kind"] == "remove_on"
    if info["shape"] == "combined":
        body = (f"def {info['fn']}(order):\n    if order.get(\"beta\"):\n        return {on}\n    return {off}\n"
                if keep_on else f"def {info['fn']}(order):\n    return {off}\n")
    else:
        body = f"def {info['fn']}(order):\n    return {on if keep_on else off}\n"
    return body


def solve(seed, workspace):
    truth, pristine = generate(seed)
    ws = Path(workspace)
    keep_names = []
    for name, info in truth["flags"].items():
        if info["kind"].startswith("keep"):
            keep_names.append(name)
            continue
        text = pristine[f"app/{info['module']}.py"]
        original = source(info["shape"], name, info["fn"], info["on"], info["off"])
        write(ws / "app", f"{info['module']}.py", text.replace(original, _cleaned(info)))
    lines = pristine["flags.yaml"].splitlines()
    out, skip = [], False
    for line in lines:
        m = re.match(r"\s*- name: (\S+)", line)
        if m:
            skip = m.group(1) not in keep_names
        if not skip:
            out.append(line)
    write(ws, "flags.yaml", "\n".join(out) + "\n")


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [f["unit_chars"] for f in t["flags"].values()],
            "judgement_turns": 6, "orchestration_turns": 12, "shared_chars": len(FLAGS_MD) + 4000}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Feature flag cleanup

Flag debt is slowing everyone down. Apply the cleanup policy in `docs/FLAGS.md`
to every flag in `flags.yaml`: remove the flags that are finished, keeping the
right behaviour, and leave the rest alone. Update `flags.yaml` to match.

Behaviour must not change for any order.
"""

META = {
    "unit": "flag", "kind": "dead-code removal", "domain": "feature flags", "output_tokens": 1500, "needs_pytest": True,
    "failure_mode": "a per-unit policy decision followed by a behaviour-preserving refactor",
    "deliverable": "edited modules under `app/` and an updated `flags.yaml`",
    "grading": "Per flag: a hidden behaviour test (removed flags: never consulted, final behaviour kept; kept "
               "flags: both states still work) passes, and flags.yaml lists it iff it should remain. "
               "Reward is the mean.",
    "per_unit": "read the flag's history, decide remove-on / remove-off / keep, then remove the check in "
                "whichever of five shapes it takes without changing behaviour",
    "traps": [
        "**Stale `status` labels**; the last history event decides.",
        "**The 30-day line** sits inside some histories.",
        "**Shapes**: `if not`, ternaries, helper functions, and `enabled(x) and order.get(\"beta\")`, "
        "which must become the other condition, not `True`.",
        "**Kept flags must keep working both ways.**",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
