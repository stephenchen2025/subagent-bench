#!/usr/bin/env python3
"""LH34 -- vet 52 transit candidates: planet, eclipsing binary, or no signal.

stars/KOI-NNNN/ holds one star's detected dips (dips.csv: mid-time in BJD,
depth in ppm, duration, signal-to-noise) and a note (star.md) with the star's
radius -- in solar radii or in km -- and, for some, a warning that a nearby
star shares the photometric aperture. docs/VETTING.md fixes the procedure:

- only dips with SNR >= 7.1 count;
- the period comes from the first and last dip and the number of orbits
  between them, which is not the number of dips: observing gaps hide transits;
- depths are corrected for the light of a contaminating star;
- an eclipsing binary shows odd and even eclipses of different depths, or an
  eclipse too deep for a planet;
- a planet's radius follows from the corrected depth and the star's radius.

    python3 lh34_transit_vetting.py --seed 1 --out /fixture
"""

import csv
import io
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_STARS = 52
DESIGN = {"planet": 28, "eb_oddeven": 10, "eb_deep": 8, "no_signal": 6}
SNR_MIN = 7.1
TOL_D = 0.02
R_SUN_KM = 695700
R_EARTH_PER_R_SUN = 109.08
BJD0 = 2460000.0


# ------------------------------------------------------------------ the procedure

def vet(rows, star):
    """docs/VETTING.md, exactly."""
    dips = sorted((float(r["time_bjd"]), float(r["depth_ppm"])) for r in rows if float(r["snr"]) >= SNR_MIN)
    if len(dips) < 3:
        return {"class": "no_signal"}
    t0 = dips[0][0]
    period = best_period([t for t, _ in dips])
    n = [round((t - t0) / period) for t, _ in dips]
    period = (dips[-1][0] - t0) / n[-1]
    dilution = 1 - star["contamination"]
    depths = [d / dilution for _, d in dips]
    odd = [d for d, k in zip(depths, n) if k % 2]
    even = [d for d, k in zip(depths, n) if k % 2 == 0]
    mean = statistics.fmean(depths)
    if odd and even:
        mo, me = statistics.fmean(odd), statistics.fmean(even)
        if abs(mo - me) / ((mo + me) / 2) > 0.10:
            return {"class": "eclipsing_binary", "period_days": period}
    if mean > 30000:
        return {"class": "eclipsing_binary", "period_days": period}
    radius = star["radius_rsun"] * R_EARTH_PER_R_SUN * math.sqrt(mean / 1e6)
    return {"class": "planet", "period_days": period, "radius_earth": radius}


def best_period(times):
    """The largest P for which every dip is within TOL_D of t0 + nP."""
    t0 = times[0]
    cands = sorted({(t - t0) / k for t in times[1:] for k in range(1, 200) if (t - t0) / k > 0.3}, reverse=True)
    for p in cands:
        if all(abs((t - t0) / p - round((t - t0) / p)) * p <= TOL_D for t in times):
            return p
    raise ValueError("no period")


# ------------------------------------------------------------------ one star

def build_star(rng, kind):
    radius = round(rng.uniform(0.55, 1.6), 2)
    contamination = rng.choice([0.0, 0.0, 0.0, 0.2, 0.3, 0.5]) if kind != "eb_deep" else rng.choice([0.0, 0.4, 0.5])
    for _ in range(200):
        period = round(rng.uniform(1.2, 9.5), 4)
        n_orbits = int(rng.uniform(40, 90) / period)
        kept = sorted(k for k in range(n_orbits + 1) if rng.random() < 0.55)
        # enough transits, and two consecutive ones, so the period is unambiguous
        if len(kept) >= (6 if kind != "no_signal" else 0) and any(b - a == 1 for a, b in zip(kept, kept[1:])):
            break
    true_depth = {"planet": rng.uniform(300, 9000), "eb_oddeven": rng.uniform(2000, 15000),
                  "eb_deep": rng.uniform(22000, 60000), "no_signal": 500}[kind]
    observed = true_depth * (1 - contamination)
    if kind == "eb_deep" and observed / (1 - contamination) <= 30000:
        observed = 31000 * (1 - contamination)
    rows = []
    if kind != "no_signal":
        ratio = rng.uniform(0.55, 0.8)
        for k in kept:
            d = observed * (ratio if (kind == "eb_oddeven" and k % 2) else 1) * rng.uniform(0.985, 1.015)
            rows.append({"time_bjd": BJD0 + 3.1 + k * period + rng.uniform(-0.004, 0.004), "depth_ppm": round(d),
                         "duration_h": round(rng.uniform(1.5, 5.5), 2), "snr": round(rng.uniform(8, 40), 1)})
    else:
        for _ in range(rng.randint(0, 2)):
            rows.append({"time_bjd": BJD0 + rng.uniform(1, 70), "depth_ppm": rng.randint(200, 900),
                         "duration_h": round(rng.uniform(1, 4), 2), "snr": round(rng.uniform(7.2, 9), 1)})
    for _ in range(rng.randint(1, 4)):  # spurious low-SNR detections
        rows.append({"time_bjd": BJD0 + rng.uniform(1, 80), "depth_ppm": rng.randint(150, 2500),
                     "duration_h": round(rng.uniform(0.8, 4), 2), "snr": round(rng.uniform(4.0, 7.0), 1)})
    rows.sort(key=lambda r: r["time_bjd"])
    for r in rows:
        r["time_bjd"] = f"{r['time_bjd']:.4f}"
    star = {"radius_rsun": radius, "contamination": contamination}
    return rows, star


def to_csv(rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["time_bjd", "depth_ppm", "duration_h", "snr"], lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


def star_md(rng, sid, star):
    r = star["radius_rsun"]
    radius = (f"Stellar radius: {r} R_sun." if rng.random() < 0.25 else
              f"Stellar radius: {round(r * R_SUN_KM):,} km.")
    lines = [f"# {sid}", "", f"- {radius}", f"- Teff: {rng.randint(3900, 6600)} K (not needed for vetting)."]
    if star["contamination"]:
        lines.append(f"- A neighbouring star inside the aperture contributes {round(star['contamination'] * 100)}% "
                     "of the measured flux.")
    else:
        lines.append(rng.choice(["- No other star inside the aperture.", "- Aperture is uncontaminated."]))
    return "\n".join(lines) + "\n"


VETTING = f"""# Transit vetting procedure

For every star:

1. **Dips.** Use only dips with SNR >= {SNR_MIN}. Fewer than 3 such dips: class `no_signal`.
2. **Period.** Let t0 be the first dip. The period P is the LARGEST value for
   which every dip lies within {TOL_D} d of t0 + nP for some integer n (observing
   gaps hide transits, so consecutive dips may be several orbits apart). Then
   refine it: P = (t_last - t0) / n_last, where n_last is the last dip's orbit
   number. Report P in days.
3. **Depth.** If a neighbouring star contributes a fraction c of the flux,
   each depth is corrected to depth / (1 - c).
4. **Eclipsing binary** (class `eclipsing_binary`) if the mean corrected depth
   of odd-numbered dips (odd n) and of even-numbered dips differ by more than
   10% of their average, or if the mean corrected depth exceeds 30,000 ppm.
5. **Planet** otherwise. Radius in Earth radii:
   R_p = R_star[R_sun] x 109.08 x sqrt(mean corrected depth / 1e6),
   with 1 R_sun = 695,700 km.
"""


def generate(seed, out=None):
    plan = rng_for(seed, "plan")
    kinds = sum(([k] * n for k, n in DESIGN.items()), [])
    plan.shuffle(kinds)
    ids = plan.sample(range(1000, 9999), N_STARS)
    files = {"docs/VETTING.md": VETTING}
    truth = {"seed": seed, "stars": {}}
    for sid_num, kind in zip(ids, kinds):
        sid = f"KOI-{sid_num}"
        rng = rng_for(seed, "star", sid)
        rows, star = build_star(rng, kind)
        text = to_csv(rows)
        files[f"stars/{sid}/dips.csv"] = text
        files[f"stars/{sid}/star.md"] = star_md(rng, sid, star)
        result = vet(list(csv.DictReader(io.StringIO(text))), star)
        want = {"planet": "planet", "no_signal": "no_signal"}.get(kind, "eclipsing_binary")
        assert result["class"] == want, (sid, kind, result)
        truth["stars"][sid] = dict(result, unit_chars=len(text) + 3000)
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def _close(got, want, rel):
    try:
        return abs(float(got) - want) <= rel * abs(want)
    except (TypeError, ValueError):
        return False


def grade(seed, answer):
    """Per star, all or nothing: the class; for a planet the period within 0.1 %
    and the radius within 2 %."""
    truth = generate(seed)
    per = {}
    for sid, t in truth["stars"].items():
        got = answer.get(sid) if isinstance(answer.get(sid), dict) else {}
        ok = got.get("class") == t["class"]
        if ok and t["class"] == "planet":
            ok = _close(got.get("period_days"), t["period_days"], 0.001) and \
                _close(got.get("radius_earth"), t["radius_earth"], 0.02)
        per[sid] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "stars": per}


def oracle(seed):
    return {sid: {k: v for k, v in t.items() if k != "unit_chars"} for sid, t in generate(seed)["stars"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["stars"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(VETTING) + 300}


ANSWER_PATH = "/workspace/answer/vetting.json"
INSTRUCTION = """\
# Transit candidate vetting

The pipeline flagged every star in `/workspace/stars/`. Vet each candidate by
`docs/VETTING.md` before the follow-up proposal is written.

Write `/workspace/answer/vetting.json`:

```json
{"KOI-NNNN": {"class": "planet", "period_days": 0.0, "radius_earth": 0.0},
 "KOI-MMMM": {"class": "eclipsing_binary"},
 "KOI-LLLL": {"class": "no_signal"}}
```
"""

META = {
    "unit": "star", "kind": "signal vetting", "domain": "exoplanet astronomy",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "per-object physical reasoning where the data hide what the obvious calculation assumes",
    "deliverable": "`/workspace/answer/vetting.json`",
    "grading": "Per star, all or nothing: the class; for a planet, period within 0.1 % and radius within 2 %. "
               "Reward is the mean.",
    "per_unit": "drop low-SNR dips, find the orbit numbers across the gaps, refine the period, correct depths for "
                "contaminating light, compare odd and even eclipses, and convert depth to a radius",
    "traps": [
        "**Missed transits**: dips are not consecutive orbits, so (last - first) / (count - 1) is wrong.",
        "**Low-SNR dips** that break the period if kept.",
        "**Dilution** by a neighbouring star makes eclipses look shallower -- and can turn a planet into an EB.",
        "**Odd/even depths** that differ reveal an eclipsing binary.",
        "**Stellar radius in km** for some stars.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
