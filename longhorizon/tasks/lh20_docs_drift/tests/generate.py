#!/usr/bin/env python3
"""LH20 -- bring 56 CLI reference pages back in line with the code.

tools/<name>.py are the team's command-line tools (argparse). docs/cli/<name>.md
each carry an options table that has drifted: options added since are missing,
removed ones are still listed, defaults and choices are stale, and hidden
options have leaked in. docs/CONVENTIONS.md fixes the table format.

The code is the truth, and reading it is the work:

- a default may be a module constant, an expression over one
  (`default=2 * DEFAULT_RETRIES`), or an environment variable with a fallback;
- `store_true` defaults to `false`, and `--no-color` (store_false into
  `color`) defaults to `true`;
- `help=argparse.SUPPRESS` options must NOT be documented;
- choices are appended to the description in a fixed form.

The grader builds each tool's expected table from its parser and compares the
agent's table row by row.

    python3 lh20_docs_drift.py --seed 1 --out /fixture
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_TOOLS = 56
OPTION_POOL = [
    ("--retries", "-r", "int", "How many times to retry a failed request."),
    ("--timeout", "-t", "float", "Seconds to wait for each request."),
    ("--output", "-o", "str", "Where to write the report."),
    ("--format", "-f", "choice", "Output format."),
    ("--region", None, "choice", "Which region to target."),
    ("--dry-run", "-n", "flag", "Show what would change without changing anything."),
    ("--verbose", "-v", "flag", "Print progress while running."),
    ("--no-color", None, "negflag", "Disable coloured output."),
    ("--batch-size", "-b", "int", "Records per batch."),
    ("--since", None, "str", "Only consider records after this ISO date."),
    ("--workers", "-w", "int", "Parallel workers."),
    ("--cache-dir", None, "env", "Directory for cached responses."),
    ("--token-file", None, "env", "File holding the API token."),
    ("--chunk-size", None, "post", "Bytes per upload chunk."),
    ("--parallelism", "-p", "post", "Concurrent jobs."),
    ("--max-memory", None, "post", "Memory ceiling in MiB."),
    ("--debug-dump", None, "hidden", "Dump internal state (support only)."),
    ("--legacy-mode", None, "hidden", "Old behaviour (deprecated)."),
]
CHOICES = {"--format": ["json", "csv", "table"], "--region": ["eu", "us", "apac"]}

CONVENTIONS = """# CLI reference conventions

Every page under `docs/cli/` has one options table:

| option | default | description |
|---|---|---|

- **option**: the short form first if there is one, then the long form, each in
  backticks, separated by `, ` -- e.g. `` `-r`, `--retries` ``.
- **default**: the value the option has when it is not given, in backticks.
  Flags that are off by default are `` `false` ``; `--no-...` flags leave their
  setting on, so their default is `` `true` ``. A default read from the
  environment is written `` `$NAME` or `<fallback>` ``. No default: `` `none` ``.
  If the code fills the value in after parsing (a `None` default that `main`
  replaces), write `` `auto: <expression>` `` with the expression exactly as the
  code assigns it.
- **description**: the option's help text, verbatim. If the option has choices,
  append ` One of: a, b, c.` in the order the code lists them.
- Rows appear in the order the options are defined in the code.
- Options hidden from `--help` are not documented, and neither is `-h`/`--help` itself.
"""


def plan(seed):
    rng = rng_for(seed, "plan")
    verbs = ["sync", "export", "audit", "prune", "backfill", "reindex", "rotate", "migrate", "report",
             "verify", "compact", "archive", "import", "diff", "snapshot", "restore"]
    objs = ["users", "orders", "invoices", "logs", "keys", "events", "assets", "quotas"]
    names = rng.sample([f"{v}_{o}" for v in verbs for o in objs], N_TOOLS)
    tools = []
    for name in names:
        trng = rng_for(seed, "tool", name)
        # Every tool has at least one environment default and one filled in after
        # parsing: the two kinds only reading the code reveals.
        env = trng.choice([o for o in OPTION_POOL if o[2] == "env"])
        post = trng.choice([o for o in OPTION_POOL if o[2] == "post"])
        rest = trng.sample([o for o in OPTION_POOL if o not in (env, post)], trng.randint(4, 6))
        opts = rest[:]
        opts.insert(trng.randrange(len(opts) + 1), env)
        opts.insert(trng.randrange(len(opts) + 1), post)
        specs = []
        for long, short, kind, help_ in opts:
            spec = {"long": long, "short": short, "kind": kind, "help": help_}
            if kind == "int":
                spec["const"] = f"DEFAULT_{long[2:].upper().replace('-', '_')}"
                spec["base"] = trng.choice([2, 3, 4, 5, 8, 10, 50, 100])
                spec["expr"] = trng.choice(["{c}", "2 * {c}", "{c} + 1"])
                spec["default"] = eval(spec["expr"].format(c=spec["base"]))  # noqa: S307
            elif kind == "float":
                spec["default"] = trng.choice([0.5, 2.5, 10.0, 30.0])
            elif kind == "str":
                spec["default"] = trng.choice([None, "report.txt", "-", "2026-01-01"])
            elif kind == "choice":
                spec["choices"] = CHOICES[long]
                spec["default"] = trng.choice(CHOICES[long])
            elif kind == "post":
                spec["expr"] = trng.choice(["4 * 1024 * 1024", "os.cpu_count() or 4", "min(64, 8 * (os.cpu_count() or 1))",
                                            "256 if args.dry_run else 1024" if any(x[0] == "--dry-run" for x in opts) else "512"])
            elif kind == "env":
                spec["env"] = f"{name.split('_')[0].upper()}_{long[2:].upper().replace('-', '_')}"
                spec["fallback"] = trng.choice(["/var/cache/tools", "~/.token", "/tmp/tools"])
            specs.append(spec)
        tools.append({"name": name, "options": specs})
    return tools


def code(tool):
    consts = [f"{o['const']} = {o['base']}" for o in tool["options"] if o["kind"] == "int"]
    lines = [f'"""{tool["name"]} -- internal tool."""', "", "import argparse", "import os", ""] + consts + ["", "",
             "def build_parser():", f'    p = argparse.ArgumentParser(prog="{tool["name"]}")']
    for o in tool["options"]:
        flags = (f'"{o["short"]}", ' if o["short"] else "") + f'"{o["long"]}"'
        k = o["kind"]
        if k == "int":
            extra = f', type=int, default={o["expr"].format(c=o["const"])}'
        elif k == "float":
            extra = f', type=float, default={o["default"]}'
        elif k == "str":
            extra = f', default={o["default"]!r}'
        elif k == "choice":
            extra = f', choices={o["choices"]!r}, default={o["default"]!r}'
        elif k == "flag":
            extra = ', action="store_true"'
        elif k == "negflag":
            extra = ', action="store_false", dest="color"'
        elif k == "post":
            extra = ", type=int, default=None"
        elif k == "env":
            extra = f', default=os.environ.get("{o["env"]}", "{o["fallback"]}")'
        else:
            extra = ', action="store_true"'
        help_ = "argparse.SUPPRESS" if k == "hidden" else repr(o["help"])
        lines.append(f"    p.add_argument({flags}{extra}, help={help_})")
    lines += ["    return p", "", "", "def main(argv=None):", "    args = build_parser().parse_args(argv)"]
    for o in tool["options"]:
        if o["kind"] == "post":
            dest = o["long"][2:].replace("-", "_")
            lines += [f"    if args.{dest} is None:", f"        args.{dest} = {o['expr']}"]
    lines += ["    print(vars(args))", "", "", 'if __name__ == "__main__":', "    main()", ""]
    return "\n".join(lines)


def row(o):
    names = (f"`{o['short']}`, " if o["short"] else "") + f"`{o['long']}`"
    k = o["kind"]
    if k in ("flag",):
        default = "`false`"
    elif k == "negflag":
        default = "`true`"
    elif k == "env":
        default = f"`${o['env']}` or `{o['fallback']}`"
    elif k == "post":
        default = f"`auto: {o['expr']}`"
    elif o.get("default") is None:
        default = "`none`"
    else:
        default = f"`{o['default']}`"
    desc = o["help"] + (f" One of: {', '.join(o['choices'])}." if o.get("choices") else "")
    return f"| {names} | {default} | {desc} |"


def expected_rows(tool):
    return [row(o) for o in tool["options"] if o["kind"] != "hidden"]


def drifted_doc(rng, tool):
    rows = []
    for o in tool["options"]:
        r = row(o)
        roll = rng.random()
        if o["kind"] == "hidden":
            if roll < 0.5:
                rows.append(f"| `{o['long']}` | `false` | {o['help']} |")  # leaked
            continue
        if roll < 0.25:
            continue  # added since: missing from the docs
        if o["kind"] == "post" and roll < 0.7:
            r = r.replace(f"`auto: {o['expr']}`", "`none`")
        elif roll < 0.5 and o["kind"] in ("int", "float", "choice", "str"):
            r = r.replace(f"`{o.get('default')}`", f"`{rng.choice(['3', '10', 'json', '1.0', 'out.txt'])}`", 1)
        elif roll < 0.6 and o.get("choices"):
            r = r.replace(", ".join(o["choices"]), ", ".join(o["choices"][:-1]))
        elif roll < 0.55 and o["kind"] == "negflag":
            r = r.replace("`true`", "`false`")
        rows.append(r)
    if rng.random() < 0.6:
        rows.insert(rng.randrange(len(rows) + 1), "| `--legacy-output` | `none` | Write the old report format. |")
    return (f"# {tool['name']}\n\n{tool['name'].replace('_', ' ').capitalize()}. Run it with "
            f"`python tools/{tool['name']}.py`.\n\n## Options\n\n| option | default | description |\n|---|---|---|\n"
            + "\n".join(rows) + "\n\n## Exit codes\n\n`0` on success, `2` on bad arguments.\n")


def parse_rows(md):
    rows = []
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("|") and not re.match(r"^\|\s*-", line) and "option" not in line.split("|")[1]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append("| " + " | ".join(cells) + " |")
    return rows


def generate(seed, out=None):
    truth = {"seed": seed, "tools": {}}
    files = {"docs/CONVENTIONS.md": CONVENTIONS}
    for tool in plan(seed):
        rng = rng_for(seed, "doc", tool["name"])
        files[f"tools/{tool['name']}.py"] = code(tool)
        files[f"docs/cli/{tool['name']}.md"] = drifted_doc(rng, tool)
        truth["tools"][tool["name"]] = {"rows": expected_rows(tool),
                                       "unit_chars": len(files[f"tools/{tool['name']}.py"]) + 1500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def _lcs(a, b):
    """Length of the longest common subsequence: rows right AND in order, so one
    stray row costs one row, not everything after it."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def grade(seed, workspace):
    """Per tool: the longest in-order run of rows that exactly match the table
    derived from the parser, over the larger of the expected and submitted row
    counts. Reward is the mean."""
    truth = generate(seed)
    per = {}
    for name, t in truth["tools"].items():
        path = Path(workspace) / "docs" / "cli" / f"{name}.md"
        got = parse_rows(path.read_text()) if path.exists() else []
        want = t["rows"]
        right = _lcs(got, want)
        per[name] = round(right / max(len(want), len(got), 1), 4)
    return {"reward": round(sum(per.values()) / len(per), 4), "tools": per}


def solve(seed, workspace):
    truth = generate(seed)
    for name, t in truth["tools"].items():
        path = Path(workspace) / "docs" / "cli" / f"{name}.md"
        text = path.read_text()
        head, _, rest = text.partition("|---|---|---|\n")
        _, _, tail = rest.partition("\n\n")
        path.write_text(head + "|---|---|---|\n" + "\n".join(t["rows"]) + "\n\n" + tail)


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["tools"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(CONVENTIONS)}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Fix the CLI reference

The option tables in `docs/cli/` have drifted from the tools in `tools/`.
Update every page so its options table matches its tool exactly, following
`docs/CONVENTIONS.md`. The code is the source of truth. Leave the rest of each
page as it is.
"""

META = {
    "unit": "tool", "kind": "doc correction", "domain": "CLI documentation", "output_tokens": 1300, "needs_pytest": False,
    "failure_mode": "documentation made exactly true to code, including values the code computes",
    "deliverable": "updated `docs/cli/<tool>.md` for 56 tools",
    "grading": "Per tool: the longest in-order sequence of rows matching the table derived from the parser, "
               "over the larger of the expected and submitted row counts. Reward is the mean.",
    "per_unit": "read the parser, resolve every default (constants, expressions, environment fallbacks, "
                "inverted flags), drop hidden options, and rewrite the table in the house format",
    "traps": [
        "**Computed defaults**: `default=2 * DEFAULT_RETRIES` must be documented as the number.",
        "**Environment defaults** use the `$NAME` or `fallback` form.",
        "**`--no-color` defaults to `true`**; `store_true` flags to `false`.",
        "**Hidden options** have leaked into some pages and must be removed; so must the long-gone `--legacy-output`.",
        "**Stale choices and defaults** look plausible; only the code says which are wrong.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
