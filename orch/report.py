"""Orchestrator-track report: headline table, scaling charts, process diagnostics.

The required artifact (ORCHESTRATOR.md 5.4) is score against task size, one line
per condition: the gap between solo and delegate is the benefit, the gap between
delegate and oracle-split is the headroom. Charts are static SVGs with a light
and a dark palette, direct labels at line ends, and native <title> tooltips on
every point. The markdown tables beside them are the table view.
"""

import html
from pathlib import Path

from orch.metrics import BASELINES, FAVOURABLE, UNFAVOURABLE, is_delegate, summarise

# Categorical slots in fixed order (dataviz reference palette; validated light
# and dark). Colour follows the condition, never its rank.
LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300"]


def _f(value, digits=2, signed=False):
    if value is None:
        return "–"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _k(value):
    return "–" if value is None else f"{value / 1000:.1f}k"


def condition_order(records):
    conds = {r["condition"] for r in records}
    ordered = [c for c in BASELINES if c in conds]
    return ordered + sorted(c for c in conds if is_delegate(c))


def chart_svg(title, sizes, series, x_label):
    """series: [(name, slot, [score or None per size])]. Scores in [0, 1]."""
    w, h = 600, 300
    left, right, top, bottom = 48, 200, 36, 44
    pw, ph = w - left - right, h - top - bottom
    n = len(sizes)

    def x(i):
        return left + (pw * i / (n - 1) if n > 1 else pw / 2)

    def y(v):
        return top + ph * (1 - v)

    style = ["text{font:12px system-ui,sans-serif;fill:#52514e}",
             ".t{font-weight:600;fill:#0b0b0b}", ".g{stroke:#e8e7e4;stroke-width:1}",
             ".a{stroke:#c3c2b7;stroke-width:1}", "rect.bg{fill:#fcfcfb}",
             "circle{stroke:#fcfcfb !important;stroke-width:2}"]
    for slot, color in enumerate(LIGHT):
        style.append(f".s{slot}{{stroke:{color};fill:{color}}}")
    dark = ["text{fill:#c3c2b7}", ".t{fill:#ffffff}", ".g{stroke:#2f2f2d}",
            ".a{stroke:#52514e}", "rect.bg{fill:#1a1a19}",
            "circle{stroke:#1a1a19 !important}"]
    for slot, color in enumerate(DARK):
        dark.append(f".s{slot}{{stroke:{color};fill:{color}}}")
    style.append("@media (prefers-color-scheme: dark){" + "".join(dark) + "}")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-label="{html.escape(title)}">',
        f"<style>{''.join(style)}</style>",
        f'<rect class="bg" width="{w}" height="{h}" rx="6"/>',
        f'<text class="t" x="{left}" y="22">{html.escape(title)}</text>',
    ]
    for tick in (0, 0.25, 0.5, 0.75, 1.0):
        parts.append(f'<line class="g" x1="{left}" x2="{left + pw}" y1="{y(tick):.1f}" '
                     f'y2="{y(tick):.1f}"/>')
        parts.append(f'<text x="{left - 8}" y="{y(tick) + 4:.1f}" text-anchor="end">'
                     f"{tick:.2f}</text>")
    for i, size in enumerate(sizes):
        parts.append(f'<text x="{x(i):.1f}" y="{top + ph + 18}" text-anchor="middle">{size}</text>')
    parts.append(f'<text x="{left + pw / 2:.1f}" y="{h - 8}" text-anchor="middle">'
                 f"{html.escape(x_label)}</text>")
    parts.append(f'<line class="a" x1="{left}" x2="{left + pw}" y1="{top + ph}" y2="{top + ph}"/>')

    label_y = []
    # Baselines first and dashed, so conditions that tie them stay visible on top:
    # overlapping lines at the same score are the common case, not the exception.
    dashes = {"oracle-split": "6 4", "solo-xl": "2 4"}
    series = sorted(series, key=lambda s: 0 if s[0] in dashes else 1)
    for name, slot, values in series:
        pts = [(x(i), y(v), v) for i, v in enumerate(values) if v is not None]
        if not pts:
            continue
        path = " ".join(f"{'M' if j == 0 else 'L'}{px:.1f},{py:.1f}" for j, (px, py, _) in enumerate(pts))
        dash = f' stroke-dasharray="{dashes[name]}"' if name in dashes else ""
        parts.append(f'<path class="s{slot}" d="{path}" fill="none" stroke-width="2"{dash} '
                     'stroke-linejoin="round" stroke-linecap="round" style="fill:none"/>')
        for (px, py, v), size in zip(pts, [s for s, v in zip(sizes, values) if v is not None]):
            parts.append(f'<circle class="s{slot}" cx="{px:.1f}" cy="{py:.1f}" r="4">'
                         f'<title>{html.escape(name)} '
                         f"at {size}: {v:.2f}</title></circle>")
    for name, slot, values in sorted(series, key=lambda s: -(s[2][-1] or 0)):
        pts = [v for v in values if v is not None]
        if not pts:
            continue
        ly = y(pts[-1])
        while any(abs(ly - other) < 14 for other in label_y):
            ly += 14
        label_y.append(ly)
        style_dash = " (dashed)" if name == "oracle-split" else " (dotted)" if name == "solo-xl" else ""
        parts.append(f'<text x="{left + pw + 10}" y="{ly + 4:.1f}">'
                     f'<tspan class="s{slot}" style="stroke:none">■</tspan> {html.escape(name)}'
                     f"{style_dash} {pts[-1]:.2f}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def render(records, out_dir, title="Orchestrator track", preamble=""):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, table = summarise(records)
    conds = condition_order(records)
    slot = {c: i % len(LIGHT) for i, c in enumerate(conds)}
    systems = sorted({r["system"] for r in records})
    lines = [f"# {title}", ""]
    if preamble:
        lines += [preamble.strip(), ""]

    lines += [
        "## Headline", "",
        "Capture = share of the oracle-split ceiling's gain over solo that delegating recovered "
        "(0 = no better than solo, 1 = matches the scripted ideal). Harm = mean score lost "
        "against solo on delegation-favourable tasks (catches damage capture cannot see where "
        "solo already scores at the ceiling). Tax = score lost by "
        "delegating where the ideal policy is solo (L). Cost ratio = total tokens vs solo on those tasks.",
        "",
        "| system | condition | capture | harm | lift W/P/C | structural lift | headroom | tax L | "
        "cost ratio L | decision acc. | coverage | duplication | synthesis loss | tokens/run |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for (system, cond), s in sorted(summary.items()):
        cells = s["cells"]
        lift = [c["lift"] for c in cells]
        struct = [c["structural_lift"] for c in cells if c["structural_lift"] is not None]
        head = [c["headroom"] for c in cells]
        avg = lambda v: sum(v) / len(v) if v else None  # noqa: E731
        lines.append(
            f"| {system} | {cond} | {_f(s['capture'])} | {_f(s['harm'])} | "
            f"{_f(avg(lift), signed=True)} | "
            f"{_f(avg(struct), signed=True)} | {_f(avg(head))} | {_f(s['mean_tax'], signed=True)} | "
            f"{_f(s['mean_cost_ratio'])}× | {_f(s['decision_balanced_acc'])} | "
            f"{_f(s['coverage'])} | {_f(s['duplication'])} | {_f(s['synthesis_loss'])} | "
            f"{_k(s['total_tokens'])} |"
        )
    lines.append("")

    for system in systems:
        lines += [f"## Scaling: {system}", ""]
        for family in FAVOURABLE + UNFAVOURABLE:
            sizes = sorted({r["size"] for r in records if r["family"] == family
                            and r["system"] == system})
            if not sizes:
                continue
            name = {"W": "W — wide sweep (tickets)", "P": "P — parallel probes (services)",
                    "C": "C — coupled views (views)", "L": "L — ledger chain (hops)"}[family]
            lines += [f"### {name}", ""]
            if len(sizes) > 1:
                series = [(c, slot[c], [table.get((system, c, family, n), {}).get("score")
                                        for n in sizes]) for c in conds]
                svg_name = f"scaling-{_slug(system)}-{family}.svg"
                x_label = {"W": "tickets (N)", "P": "services (K)", "C": "views (M)",
                           "L": "hops (H)"}[family]
                (out_dir / svg_name).write_text(chart_svg(f"{family}: score vs size", sizes,
                                                          series, x_label))
                lines += [f"![{family} score against size, one line per condition]({svg_name})", ""]
            lines.append("| condition | " + " | ".join(f"size {n}" for n in sizes)
                         + " | tokens (largest) | lead exit, largest size |")
            lines.append("|---|" + "---|" * (len(sizes) + 2))
            for cond in conds:
                row = [table.get((system, cond, family, n)) for n in sizes]
                if not any(row):
                    continue
                last = row[-1] or {}
                exits = sorted({r_exit for r_exit in _exits(records, system, cond, family, sizes[-1])})
                lines.append(
                    f"| {cond} | " + " | ".join(_f(c.get("score")) if c else "–" for c in row)
                    + f" | {_k(last.get('total_tokens'))} | {', '.join(exits) or '–'} |"
                )
            lines.append("")

    lines += [
        "## Reading this", "",
        "- **Lift** = delegate − solo. **Structural lift** = delegate − solo-xl, the "
        "compute-matched control: positive means delegation bought more than tokens.",
        "- **Headroom** = oracle-split − delegate (or 1 − delegate where no oracle-split ran).",
        "- **Coverage / duplication** are measured against each task's work items as named in "
        "briefs. **Synthesis loss** is the share of correct worker findings the final answer lost.",
        "- Differences between single runs are not findings. Report seeds and treat gaps "
        "smaller than the seed-to-seed spread as ties.",
        "",
    ]
    report = out_dir / "report.md"
    report.write_text("\n".join(lines))
    return report


def _exits(records, system, cond, family, size):
    for r in records:
        if (r["system"], r["condition"], r["family"], r["size"]) == (system, cond, family, size):
            yield r["telemetry"]["lead"].get("exit_status", "")


def _slug(text):
    return "".join(ch if ch.isalnum() else "-" for ch in text).strip("-").lower()
