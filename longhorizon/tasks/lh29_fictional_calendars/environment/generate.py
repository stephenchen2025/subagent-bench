#!/usr/bin/env python3
"""LH29 -- compute the next runs of 50 scheduled jobs under fictional calendars.

jobs/<job>.md describe recurring jobs in prose, each in one of eight fictional
regions. docs/regions/<region>.md define that region's calendar: its UTC offset
(some on the half hour), its summer-time rule (or none -- and some regions'
summer spans the new year), which days are the weekend (Saturday-Sunday,
Friday-Saturday, Thursday-Friday or Sunday-Monday), and its public holidays (fixed dates and rules like "the
second Monday of October").

For every job the deliverable is its next three run times in UTC strictly after
2026-09-26T00:00:00Z. Because the regions are invented, no timezone database
or cron library knows them: each job has to be worked through from its
region's rules, and several cross a summer-time change in October.

    python3 lh29_fictional_calendars.py --seed 1 --out /fixture
"""

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_JOBS = 50
REF = dt.datetime(2026, 9, 26, 0, 0)
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
ORD = {1: "first", 2: "second", 3: "third", 4: "fourth", -1: "last"}


def nth_weekday(year, month, weekday, n):
    if n > 0:
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    nxt = dt.date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


REGIONS = {
    "Alvoria": {"offset": (3, 30), "dst": ((4, 6, -1), (10, 6, 1)), "weekend": (4, 5),
                "fixed": [(1, 1), (9, 28), (10, 3), (12, 25)], "rules": [(10, 0, 2)]},
    "Brisca": {"offset": (-4, 0), "dst": ((3, 6, 2), (11, 6, 1)), "weekend": (5, 6),
               "fixed": [(7, 4), (9, 30), (10, 15), (12, 25)], "rules": [(10, 0, 2), (11, 3, 4)]},
    "Corvel": {"offset": (5, 30), "dst": None, "weekend": (4, 5), "fixed": [(9, 30), (10, 2), (11, 14)], "rules": []},
    "Drenmark": {"offset": (1, 0), "dst": ((3, 6, -1), (10, 6, -1)), "weekend": (5, 6),
                 "fixed": [(10, 3), (12, 24), (12, 25)], "rules": [(9, 0, -1)]},
    "Esperi": {"offset": (10, 0), "dst": ((10, 6, 1), (4, 6, 1)), "weekend": (3, 4),
               "fixed": [(1, 26), (9, 27), (11, 16), (12, 25)], "rules": [(10, 0, 1)]},
    "Faloria": {"offset": (-3, 30), "dst": ((4, 6, 1), (10, 6, 2)), "weekend": (4, 5),
                "fixed": [(10, 12)], "rules": [(9, 1, -1), (10, 0, 3)]},
    "Gantis": {"offset": (8, 0), "dst": None, "weekend": (6, 0), "fixed": [(9, 29), (10, 1), (10, 2), (10, 7)], "rules": []},
    "Halvenn": {"offset": (0, 0), "dst": ((3, 6, -1), (10, 6, -1)), "weekend": (5, 6),
                "fixed": [(9, 29), (10, 15), (12, 25), (12, 26)], "rules": [(10, 0, -1)]},
}


def region_md(name, r):
    h, m = r["offset"]
    sign = "+" if h >= 0 else "-"
    lines = [f"# {name}", "", f"- Standard time: UTC{sign}{abs(h):02d}:{abs(m):02d}."]
    if r["dst"]:
        (m1, wd1, n1), (m2, wd2, n2) = r["dst"]
        lines.append(f"- Summer time (one hour ahead of standard time) starts at 02:00 local time on the "
                     f"{ORD[n1]} {DAYS[wd1]} of {MONTHS[m1 - 1]} and ends at 03:00 local time on the "
                     f"{ORD[n2]} {DAYS[wd2]} of {MONTHS[m2 - 1]}.")
    else:
        lines.append("- No summer time.")
    lines.append(f"- Weekend: {DAYS[r['weekend'][0]]} and {DAYS[r['weekend'][1]]}.")
    hol = [f"{d} {MONTHS[m - 1]}" for m, d in r["fixed"]] + [f"the {ORD[n]} {DAYS[wd]} of {MONTHS[m - 1]}" for m, wd, n in r["rules"]]
    lines.append(f"- Public holidays: {'; '.join(hol)}.")
    lines.append("- A business day is a day that is neither a weekend day nor a public holiday.")
    return "\n".join(lines) + "\n"


def is_holiday(r, d):
    return (d.month, d.day) in r["fixed"] or any(nth_weekday(d.year, m, wd, n) == d for m, wd, n in r["rules"])


def business(r, d):
    return d.weekday() not in r["weekend"] and not is_holiday(r, d)


def roll_forward(r, d):
    while not business(r, d):
        d += dt.timedelta(days=1)
    return d


def in_summer(r, d):
    if not r["dst"]:
        return False
    (m1, wd1, n1), (m2, wd2, n2) = r["dst"]
    start, end = nth_weekday(d.year, m1, wd1, n1), nth_weekday(d.year, m2, wd2, n2)
    return start <= d < end if start < end else (d >= start or d < end)


def to_utc(r, d, hh, mm):
    """Local wall time on local date d -> UTC. Job times avoid the 02:00-03:00 changeover."""
    h, m = r["offset"]
    offset = dt.timedelta(hours=h, minutes=m if h >= 0 else -m) + (dt.timedelta(hours=1) if in_summer(r, d) else dt.timedelta(0))
    return dt.datetime(d.year, d.month, d.day, hh, mm) - offset


def runs(job):
    r = REGIONS[job["region"]]
    out = []
    d = dt.date(2026, 9, 24)
    while len(out) < 3:
        cands = []
        k = job["kind"]
        if k == "weekday":
            if business(r, d):
                cands = [(job["hh"], job["mm"])]
        elif k == "biweekly":
            # every 14 days from the anchor, moved to the next business day
            anchor = dt.date.fromisoformat(job["anchor"])
            for back in range(14):
                a = d - dt.timedelta(days=back)
                if a >= anchor and (a - anchor).days % 14 == 0:
                    if roll_forward(r, a) == d:
                        cands = [(job["hh"], job["mm"])]
                    break
        elif k == "last_business":
            nxt = d + dt.timedelta(days=1)
            last = d
            while True:
                probe = nxt
                if probe.month != d.month:
                    break
                if business(r, probe):
                    last = None
                    break
                nxt += dt.timedelta(days=1)
            if last and business(r, d):
                cands = [(job["hh"], job["mm"])]
        elif k == "interval":
            if business(r, d):
                t = job["from"] * 60
                while t <= job["to"] * 60:
                    cands.append(divmod(t, 60))
                    t += job["every"]
        elif k == "fifteenth":
            if d == roll_forward(r, dt.date(d.year, d.month, 15)):
                cands = [(job["hh"], job["mm"])]
        elif k == "quarter_first":
            if d.month in (1, 4, 7, 10) and d == roll_forward(r, dt.date(d.year, d.month, 1)):
                cands = [(job["hh"], job["mm"])]
        for hh, mm in cands:
            u = to_utc(r, d, hh, mm)
            if u > REF and len(out) < 3:
                out.append(u.strftime("%Y-%m-%dT%H:%M:%SZ"))
        d += dt.timedelta(days=1)
    return out


def describe(job):
    t = f"{job['hh']:02d}:{job['mm']:02d}"
    k = job["kind"]
    if k == "weekday":
        return f"Runs at {t} local time on every business day."
    if k == "biweekly":
        a = dt.date.fromisoformat(job["anchor"])
        return (f"Runs at {t} local time every second {DAYS[a.weekday()]}, starting {a.isoformat()}; "
                "if that day is not a business day, on the next business day instead.")
    if k == "last_business":
        return f"Runs at {t} local time on the last business day of each month."
    if k == "interval":
        return (f"Runs every {job['every']} minutes from {job['from']:02d}:00 to {job['to']:02d}:00 local time "
                f"(inclusive) on business days.")
    if k == "fifteenth":
        return f"Runs at {t} local time on the 15th of each month; if that is not a business day, on the next business day."
    return f"Runs at {t} local time on the first business day of January, April, July and October."


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    kinds = ["weekday", "biweekly", "last_business", "interval", "fifteenth", "quarter_first"]
    files = {f"docs/regions/{n}.md": region_md(n, r) for n, r in REGIONS.items()}
    truth = {"seed": seed, "jobs": {}}
    words = ["payroll", "backup", "report", "sync", "invoice", "digest", "cleanup", "rollup", "export", "audit"]
    for i in range(N_JOBS):
        job = {"kind": kinds[i % len(kinds)], "region": rng.choice(list(REGIONS)),
               "hh": rng.randint(6, 21), "mm": rng.choice([0, 15, 30, 45])}
        if job["kind"] == "biweekly":
            job["anchor"] = (dt.date(2026, 8, 3) + dt.timedelta(days=rng.randint(0, 20))).isoformat()
        if job["kind"] == "interval":
            job.update({"every": rng.choice([45, 90, 150]), "from": rng.randint(7, 10), "to": rng.randint(15, 19)})
        name = f"{rng.choice(words)}-{i:02d}"
        files[f"jobs/{name}.md"] = f"# {name}\n\n- Region: {job['region']}\n- Schedule: {describe(job)}\n"
        truth["jobs"][name] = {"runs": runs(job), "unit_chars": 2500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def grade(seed, answer):
    """Per job, all or nothing: its next three runs exactly (UTC, to the minute)."""
    truth = generate(seed)
    per = {}
    for name, t in truth["jobs"].items():
        got = answer.get(name) if isinstance(answer.get(name), list) else []
        norm = [str(g).replace("+00:00", "Z") for g in got]
        norm = [g if g.endswith("Z") else g + "Z" for g in norm]
        norm = [g[:16] + ":00Z" if len(g) == 17 else g for g in norm]
        per[name] = float(norm == t["runs"])
    return {"reward": round(sum(per.values()) / len(per), 4), "jobs": per}


def oracle(seed):
    return {n: t["runs"] for n, t in generate(seed)["jobs"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["jobs"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": 4000}


ANSWER_PATH = "/workspace/answer/runs.json"
INSTRUCTION = """\
# When does each job run next?

Operations is migrating every job in `/workspace/jobs/` to a new scheduler that
only understands UTC timestamps. For each job, work out its next three run
times strictly after 2026-09-26T00:00:00Z, using the calendar of the job's
region in `docs/regions/`.

Write `/workspace/answer/runs.json`:

```json
{"<job>": ["2026-09-28T06:30:00Z", "...", "..."]}
```
"""

META = {
    "unit": "job", "kind": "date computation", "domain": "calendar systems", "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "calendar and time-zone reasoning from written rules no library knows",
    "deliverable": "`/workspace/answer/runs.json`",
    "grading": "Per job, all or nothing: its next three runs exactly right (UTC, to the minute). Reward is the mean.",
    "per_unit": "read the region's offset, summer-time rule, weekend and holidays, expand the job's schedule "
                "day by day from 26 September, and convert each run to UTC",
    "traps": [
        "**Invented regions**: no tz database applies; half-hour offsets.",
        "**Summer time** ends in October in some regions and starts in October in others.",
        "**Weekends differ**: Friday-Saturday, Thursday-Friday, Sunday-Monday.",
        "**Rule holidays** (\"second Monday of October\") and next-business-day roll-forwards.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
