"""Run a small batch end to end: snapshot -> clusters -> fact graphs -> prose -> decoys -> gates.

    python -m wikiplant.run --snapshot build/sw --out build/wp-run --puzzles 3 --models gemini

Writes clusters.json, puzzles.json, manifest.json and report.md to --out, saving
after every puzzle, so a run stopped by a spent daily quota keeps what it made.
This is a pilot: free-tier models, small samples, no human review.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

from . import clusters as cl
from . import decoys as dc
from .design import TIERS, build_brief, design_puzzle
from .gates import ORDER, Context, pass_rates, run_gates
from .llm import USAGE, QuotaExhausted, fallback, gemini_model
from .names import CollisionIndex, Registry
from .schemas import read_jsonl
from .writing import Ledger, WriterPool, plant_fact

# Free-tier roles. Each role is a chain: the free tier allows ~20 requests a day per Flash model,
# so when one is spent the role moves to the next, ending on Flash-Lite models, which allow more.
# Writers span two model versions so no one fingerprint is on every unit.
FLASH = ["gemini-3-flash-preview", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.6-flash"]
LITE = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]
GEMINI = {
    "designer": FLASH + LITE[:1],
    "writers": {"gemini-3.5-flash-lite": ["gemini-3.5-flash-lite", "gemini-flash-lite-latest"],
                "gemini-3.1-flash-lite": ["gemini-3.1-flash-lite", "gemini-flash-lite-latest"]},
    "closed_book": {"flash": FLASH[::-1], "lite": ["gemini-3.1-flash-lite"]},
    "oracle": FLASH[1:] + LITE[:1],
    "judge": FLASH + LITE[:1],
    "agent": LITE,
    "style_judge": LITE[1:] + LITE[:1],
}
SCHEDULE = [("easy", "chain"), ("medium", "chain"), ("medium", "comparison")]


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def models(spec, interval):
    """Role -> Model, each a fallback chain. One client per model name, shared across roles,
    so pacing and spent quotas are tracked once per model."""
    clients = {}

    def client(name):
        if name not in clients:
            # Flash models get a third of lite's request rate on the free tier.
            clients[name] = gemini_model(name, min_interval_s=interval if "lite" in name else interval * 3)
        return clients[name]
    chain = lambda names: fallback([client(n) for n in names])
    return {
        "designer": chain(spec["designer"]),
        "writers": {k: chain(v) for k, v in spec["writers"].items()},
        "closed_book": {k: chain(v) for k, v in spec["closed_book"].items()},
        "oracle": chain(spec["oracle"]), "judge": chain(spec["judge"]), "agent": chain(spec["agent"]),
        "style_judge": chain(spec["style_judge"]),
    }


def pick_clusters(paras, pages, n, seeds, rng_seed, size_range):
    stats = cl.page_stats(paras)
    hosts = cl.host_pages(stats, pages)
    log(f"{len(pages)} pages, {len(hosts)} host-eligible")
    found = cl.discover(paras, pages, cl.sample_seeds(hosts, seeds, rng_seed), size_range=size_range)
    return cl.diversify(found, stats, n), hosts


def save(out, **parts):
    for name, obj in parts.items():
        (out / f"{name}.json").write_text(json.dumps(obj, indent=1, default=str))


def report(out, puzzles, manifest, failures, gate_results, started):
    rates = pass_rates(puzzles)
    lines = ["# wikiplant pilot run", "",
             f"Puzzles designed: {len(puzzles)}. Design or writing failures: {len(failures)}. "
             f"Manifest units: {len(manifest)} {dc.ratio_report(manifest)['by_role']}.",
             f"Shippable (all nine gates pass): {sum(all(p['gates'].get(g) == 'pass' for g in ORDER) for p in puzzles)}. "
             "Human review is not run in this pilot, so nothing is shippable yet.", "",
             "## Gate pass rates", "", "| gate | pass | tried |", "|---|---|---|"]
    lines += [f"| {g} | {r['pass']} | {r['tried']} |" for g, r in rates.items()]
    lines += ["", "## Puzzles", ""]
    for p in puzzles:
        lines += [f"### {p['pid']} ({p['tier']}, {p['template']})", "", f"**Q:** {p['question']}", "",
                  f"**A:** {p['answer']} (aliases: {', '.join(p.get('aliases', [])) or 'none'})", ""]
        for g, r in gate_results.get(p["pid"], {}).items():
            extra = {k: v for k, v in r.items() if k in ("bm25_rank", "accuracy", "p_value", "distractors")}
            lines.append(f"- {g}: **{r['state']}** {r.get('reason', '')} {extra if extra else ''}".rstrip())
        lines += ["", "Planted units:", ""]
        lines += [f"- `{u['unit_id']}` ({u['role']}, page {u['host_page']}, {u['generator']['model']}): {u['text']}"
                  for u in manifest if u["unit_id"].startswith(p["pid"] + "-")]
        lines.append("")
    if failures:
        lines += ["## Failures before the gates", ""]
        lines += [f"- {f['pid']} ({f['stage']}): {f['reason'][:400]}" for f in failures]
    lines += ["", "## Model usage", "", "| model | calls | tokens | retries |", "|---|---|---|---|"]
    lines += [f"| {m} | {u['calls']} | {u['tokens']} | {u['retries']} |" for m, u in sorted(USAGE.items())]
    lines += ["", f"Wall time: {(time.time() - started) / 60:.1f} min."]
    (out / "report.md").write_text("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wikiplant.run")
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--puzzles", type=int, default=3)
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--rng", type=int, default=0)
    ap.add_argument("--interval", type=float, default=4.0, help="seconds between calls to one model")
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--min-cluster", type=int, default=30)
    ap.add_argument("--gates-only", action="store_true", help="re-run the gates on --out's saved puzzles and manifest")
    a = ap.parse_args(argv)
    started = time.time()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    snap = Path(a.snapshot)
    paras = read_jsonl(snap / "paragraphs.jsonl")
    pages = {int(k): v for k, v in json.loads((snap / "pages.json").read_text()).items()}
    sid = (snap / "snapshot_id").read_text().strip()
    rng = random.Random(a.rng)
    M = models(GEMINI, a.interval)

    if a.gates_only:
        puzzles = json.loads((out / "puzzles.json").read_text())
        manifest = json.loads((out / "manifest.json").read_text())
        fpath = out / "failures.json"
        failures = json.loads(fpath.read_text()) if fpath.exists() else []
        return run_all_gates(out, paras, sid, M, a, puzzles, manifest, failures, started)

    clusters, hosts = pick_clusters(paras, pages, a.puzzles, a.seeds, a.rng, (a.min_cluster, 150))
    log(f"{len(clusters)} clusters: " + "; ".join(
        f"{pages[c['seed']]['title']} ({c['signals']['size']} pages, score {c['score']})" for c in clusters))
    save(out, clusters=[{**c, "titles": [pages[i]["title"] for i in c["pages"]]} for c in clusters])

    collision = CollisionIndex(paras)
    registry = Registry()
    pool = WriterPool(M["writers"])
    ledger = Ledger()
    para_ids = {p["para_id"] for p in paras}
    puzzles, manifest, failures, gate_results = [], [], [], {}
    try:
        for i, c in enumerate(clusters):
            tier, template = SCHEDULE[i % len(SCHEDULE)]
            pid = f"p{i + 1:02d}"
            cluster_hosts = set(c["pages"]) & hosts
            log(f"{pid}: designing {tier} {template} on '{pages[c['seed']]['title']}' ({len(cluster_hosts)} host pages)")
            brief = build_brief(c, paras, pages)
            d, attempts = design_puzzle(brief, M["designer"], tier, template, cluster_hosts, pid, collision, registry,
                                        para_ids=para_ids)
            if d is None:
                failures.append({"pid": pid, "stage": "design", "reason": "; ".join(attempts[-1]["problems"])})
                log(f"{pid}: design failed: {attempts[-1]['problems'][:3]}")
                continue
            log(f"{pid}: Q: {d['question']}  A: {d['answer']}")
            ents = {e["eid"]: e for e in d["entities"]}
            units, ok = [], True
            for f in d["facts"]:
                if not (f.get("planted") and f["fid"] in d["path"]):
                    continue
                uid = f"{pid}-gold-{f['fid']}"
                entry, info = plant_fact(uid, f, ents, paras, [f["host_page"]], pool, ledger, rng, role="gold")
                if entry is None:
                    reason = info.get("error") or "; ".join(info["attempts"][-1]["problems"])
                    failures.append({"pid": pid, "stage": "writing", "reason": reason})
                    log(f"{pid}: writing failed for {f['fid']}: {reason[:200]}")
                    ok = False
                    break
                entry["puzzle"] = pid
                f["unit_id"] = uid
                units.append(entry)
            if not ok:
                continue
            extra, dlog = dc.make_units(d, paras, pages, hosts, set(c["pages"]), pool, ledger, rng, collision, registry,
                                        tier_knobs=TIERS[tier])
            units += extra
            log(f"{pid}: {len(units)} units written ({dc.ratio_report(units)['by_role']}); "
                f"{sum(1 for x in dlog if 'error' in x)} decoys skipped")
            manifest += units
            puzzles.append(d)
            save(out, puzzles=puzzles, manifest=manifest)

    except QuotaExhausted as e:
        log(f"stopped: {e}")
        failures.append({"pid": "-", "stage": "quota", "reason": str(e)})
        save(out, puzzles=puzzles, manifest=manifest)
        report(out, puzzles, manifest, failures, gate_results, started)
        return
    save(out, puzzles=puzzles, manifest=manifest, failures=failures)
    run_all_gates(out, paras, sid, M, a, puzzles, manifest, failures, started)


def run_all_gates(out, paras, sid, M, a, puzzles, manifest, failures, started):
    gate_results = {}
    try:
        log(f"building corpora over {len(paras)} paragraphs and {len(manifest)} units")
        ctx = Context(paragraphs=paras, manifest=manifest, snapshot_id=sid, closed_book_models=M["closed_book"],
                      agent=M["agent"], oracle=M["oracle"], judge=M["judge"], style_judge=M["style_judge"],
                      samples=a.samples, style_repeats=2)
        for d in puzzles:
            log(f"{d['pid']}: gates")
            gate_results[d["pid"]] = {}
            run_gates(d, ctx, stop_on_fail=False, results=gate_results[d["pid"]])
            log(f"{d['pid']}: " + ", ".join(f"{g}={r['state']}" for g, r in gate_results[d["pid"]].items()))
            save(out, puzzles=puzzles, gate_results=gate_results)
    except QuotaExhausted as e:
        log(f"stopped: {e}")
        failures.append({"pid": "-", "stage": "quota", "reason": str(e)})
    finally:
        save(out, puzzles=puzzles, manifest=manifest, gate_results=gate_results)
        report(out, puzzles, manifest, failures, gate_results, started)
        log(f"report: {out / 'report.md'}")


if __name__ == "__main__":
    sys.exit(main())
