#!/usr/bin/env python3
"""LH16 -- port 40 shell pipelines to Python, byte for byte.

The ops team is retiring its shell toolbox. scripts/ holds 30 bash pipelines
(sort, uniq, cut, tr, sed, grep, awk, join, paste, head). The deliverable is
py/<name>.py for each: same arguments, same stdout, byte for byte, on inputs
it has never seen.

"Byte for byte" is where the work is. A faithful port must reproduce:

- `uniq -c`'s count padding, and `sort -rn`'s tie order (with -r the
  last-resort whole-line comparison is reversed too);
- awk's default number formatting (`%.6g`, so 1234567.5 prints 1.23457e+06);
- `cut` printing lines that lack the delimiter unchanged;
- `join` dropping unpairable lines and emitting every pairing of duplicates;
- `paste` padding a shorter file with empty fields;
- `grep -c` printing 0 when nothing matches.

Every script sets LC_ALL=C. The grader runs the agent's port on hidden inputs
and compares its stdout with the pipeline's.

    python3 lh16_shell_port.py --seed 1 --out /fixture
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

IPS = [f"10.0.{a}.{b}" for a in range(4) for b in range(1, 9)]
WORDS = ["alpha", "Beta", "gamma", "delta", "Alpha", "beta", "omega", "sigma", "kappa", "Delta"]


# Each template: (bash pipeline, python oracle, input maker). Fields fill {}s.
def t_top_ips(f):
    n = f["n"]
    sh = f"cut -d' ' -f1 \"$1\" | sort | uniq -c | sort -rn | head -{n}"

    def oracle(files):
        from collections import Counter
        lines = files[0].splitlines()
        counts = Counter(line.split(" ")[0] for line in lines)
        rows = [f"{c:7d} {ip}" for ip, c in counts.items()]
        rows.sort(key=lambda r: (int(r.split()[0]), r.encode()), reverse=True)
        return "".join(r + "\n" for r in rows[:n])

    def make(rng, size):
        return [("access.log", "".join(f"{rng.choice(IPS)} - - [14/Sep/2026] \"GET /x\" 200\n" for _ in range(size)))]
    return sh, oracle, make


def t_csv_sum(f):
    sh = "awk -F, 'NR>1 {s[$1]+=$" + str(f["col"]) + "} END {for (k in s) print k, s[k]}' \"$1\" | sort"

    def oracle(files):
        sums = {}
        for line in files[0].splitlines()[1:]:
            parts = line.split(",")
            key = parts[0]
            val = parts[f["col"] - 1] if len(parts) >= f["col"] else ""
            try:
                num = float(val)
            except ValueError:
                num = 0.0
            sums[key] = sums.get(key, 0.0) + num
        rows = [f"{k} {_awk_num(v)}" for k, v in sums.items()]
        return "".join(r + "\n" for r in sorted(rows, key=str.encode))

    def make(rng, size):
        head = "region,units,amount\n"
        rows = "".join(f"{rng.choice(['north', 'south', 'east', 'west', 'central'])},{rng.randint(1, 9)},"
                       f"{rng.choice([rng.randint(1, 900), round(rng.uniform(1, 9000), 2), rng.randint(100000, 400000)])}\n"
                       for _ in range(size))
        return [("sales.csv", head + rows)]
    return sh, oracle, make


def _awk_num(v):
    if v == int(v) and abs(v) < 1e16:
        return str(int(v))
    return "%.6g" % v


def t_first_seen(f):
    field = f["field"]
    sh = "awk '!seen[$" + str(field) + "]++' \"$1\""

    def oracle(files):
        seen, out = set(), []
        for line in files[0].splitlines():
            parts = line.split()
            key = parts[field - 1] if len(parts) >= field else ""
            if key not in seen:
                seen.add(key)
                out.append(line + "\n")
        return "".join(out)

    def make(rng, size):
        return [("events.txt", "".join(f"{rng.choice(WORDS)} {rng.choice(WORDS)} {rng.randint(1, 9)}\n"
                                       + ("\n" if rng.random() < 0.05 else "") for _ in range(size)))]
    return sh, oracle, make


def t_word_freq(f):
    n = f["n"]
    sh = f"tr -cs 'A-Za-z' '\\n' < \"$1\" | tr 'A-Z' 'a-z' | sort | uniq -c | sort -k1,1nr -k2,2 | head -{n}"

    def oracle(files):
        import re
        from collections import Counter
        words = [w.lower() for w in re.split(r"[^A-Za-z]+", files[0]) if w]
        counts = Counter(words)
        text = files[0]
        # tr -cs leaves a leading empty line when the text starts with a non-letter.
        if text and not text[0].isalpha() or (text and not re.match(r"[A-Za-z]", text[0])):
            counts[""] += 1
        rows = [(c, w) for w, c in counts.items()]
        rows.sort(key=lambda r: (-r[0], r[1].encode(), f"{r[0]:7d} {r[1]}".encode()))
        return "".join(f"{c:7d} {w}\n" for c, w in rows[:n])

    def make(rng, size):
        text = " ".join(rng.choice(WORDS) + rng.choice(["", ",", ".", "!"]) for _ in range(size))
        return [("text.txt", rng.choice(["", "-- ", "1. "]) + text + "\n")]
    return sh, oracle, make


def t_cut_fields(f):
    d, fields = f["delim"], f["fields"]
    sh = f"cut -d'{d}' -f{fields} \"$1\""

    def oracle(files):
        idx = [int(x) for x in fields.split(",")]
        out = []
        for line in files[0].splitlines():
            if d not in line:
                out.append(line + "\n")
                continue
            parts = line.split(d)
            out.append(d.join(parts[i - 1] for i in idx if i <= len(parts)) + "\n")
        return "".join(out)

    def make(rng, size):
        rows = []
        for _ in range(size):
            k = rng.randint(1, 5)
            rows.append(d.join(rng.choice(WORDS) for _ in range(k)) if rng.random() > 0.1 else "# comment line")
        return [("table.txt", "\n".join(rows) + "\n")]
    return sh, oracle, make


def t_date_fmt(f):
    sh = "sed -E '/^#/d; s|([0-9]{4})-([0-9]{2})-([0-9]{2})|" + f["out"] + "|g' \"$1\""

    def oracle(files):
        import re
        rep = f["out"].replace("\\1", r"\g<1>").replace("\\2", r"\g<2>").replace("\\3", r"\g<3>")
        out = []
        for line in files[0].splitlines():
            if line.startswith("#"):
                continue
            out.append(re.sub(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", rep, line) + "\n")
        return "".join(out)

    def make(rng, size):
        rows = []
        for _ in range(size):
            if rng.random() < 0.15:
                rows.append("# note 2026-01-01")
            else:
                rows.append(f"{rng.choice(WORDS)} 2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d} "
                            f"and 20261-{rng.randint(10, 99)}-{rng.randint(10, 99)}0 {rng.randint(1, 99)}")
        return [("dates.txt", "\n".join(rows) + "\n")]
    return sh, oracle, make


def t_join(f):
    sh = ("join -t, <(sort -t, -k1,1 \"$1\") <(sort -t, -k1,1 \"$2\")")

    def oracle(files):
        def rows(text):
            rs = [line.split(",", 1) for line in text.splitlines() if line]
            rs = [(r[0], r[1] if len(r) > 1 else None) for r in rs]
            return sorted(rs, key=lambda r: (r[0].encode(), (r[0] + ("," + r[1] if r[1] is not None else "")).encode()))
        a, b = rows(files[0]), rows(files[1])
        out = []
        for key, rest in a:
            for key2, rest2 in b:
                if key == key2:
                    parts = [key] + [x for x in (rest, rest2) if x is not None]
                    out.append(",".join(parts) + "\n")
        return "".join(out)

    def make(rng, size):
        keys = [f"k{rng.randint(1, size // 2 + 2):03d}" for _ in range(size)]
        a = "".join(f"{k},{rng.choice(WORDS)}\n" for k in keys[: size // 2])
        b = "".join(f"{rng.choice(keys)},{rng.randint(1, 99)}\n" for _ in range(size // 2))
        return [("left.csv", a), ("right.csv", b)]
    return sh, oracle, make


def t_grep_count(f):
    pat = f["pat"]
    sh = f"grep -E -c '{pat}' \"$1\""

    def oracle(files):
        import re
        return f"{sum(1 for line in files[0].splitlines() if re.search(pat, line))}\n"

    def make(rng, size):
        levels = ["INFO", "DEBUG", "WARN", "ERROR", "FATAL", "error"]
        return [("app.log", "".join(f"{rng.choice(levels)} {rng.choice(WORDS)}\n" for _ in range(size)))]
    return sh, oracle, make


def t_paste(f):
    d = f["delim"]
    sh = f"paste -d'{d}' \"$1\" \"$2\""

    def oracle(files):
        a, b = files[0].splitlines(), files[1].splitlines()
        return "".join(f"{a[i] if i < len(a) else ''}{d}{b[i] if i < len(b) else ''}\n" for i in range(max(len(a), len(b))))

    def make(rng, size):
        return [("names.txt", "".join(f"{rng.choice(WORDS)}\n" for _ in range(size))),
                ("scores.txt", "".join(f"{rng.randint(0, 100)}\n" for _ in range(size + rng.randint(-3, 3))))]
    return sh, oracle, make


def t_sort_numeric(f):
    k = f["key"]
    sh = f"sort -t' ' -k{k},{k}n -s \"$1\" | tail -n {f['n']}"

    def oracle(files):
        def key(line):
            parts = line.split(" ")
            field = parts[k - 1] if len(parts) >= k else ""
            import re
            m = re.match(r"\s*-?\d+(\.\d+)?", field)
            return float(m.group(0)) if m else 0.0
        lines = files[0].splitlines()
        lines = sorted(lines, key=key)
        return "".join(line + "\n" for line in lines[-f["n"]:])

    def make(rng, size):
        return [("jobs.txt", "".join(f"{rng.choice(WORDS)} {rng.choice([rng.randint(0, 50), rng.randint(0, 50), 'n/a'])} "
                                     f"{rng.randint(0, 9)}\n" for _ in range(size)))]
    return sh, oracle, make


TEMPLATES = {
    "top_ips": (t_top_ips, [{"n": 5}, {"n": 10}, {"n": 3}, {"n": 1}]),
    "csv_sum": (t_csv_sum, [{"col": 3}, {"col": 2}, {"col": 3}, {"col": 2}]),
    "first_seen": (t_first_seen, [{"field": 1}, {"field": 2}, {"field": 3}, {"field": 4}]),
    "word_freq": (t_word_freq, [{"n": 5}, {"n": 8}, {"n": 12}, {"n": 3}]),
    "cut_fields": (t_cut_fields, [{"delim": ":", "fields": "1,3"}, {"delim": ",", "fields": "2"}, {"delim": ";", "fields": "1,2,4"}, {"delim": ":", "fields": "2,3"}]),
    "date_fmt": (t_date_fmt, [{"out": "\\3.\\2.\\1"}, {"out": "\\2/\\3/\\1"}, {"out": "\\1\\2\\3"}, {"out": "\\3-\\2-\\1"}]),
    "join": (t_join, [{}, {}, {}, {}]),
    "grep_count": (t_grep_count, [{"pat": "ERROR|FATAL"}, {"pat": "^WARN"}, {"pat": "rror"}, {"pat": "FATAL$"}]),
    "paste": (t_paste, [{"delim": "\\t"}, {"delim": ","}, {"delim": ":"}, {"delim": ";"}]),
    "sort_numeric": (t_sort_numeric, [{"key": 2, "n": 5}, {"key": 3, "n": 4}, {"key": 2, "n": 8}, {"key": 3, "n": 2}]),
}


def plan(seed):
    rng = rng_for(seed, "plan")
    units = []
    for tpl, (maker, variants) in TEMPLATES.items():
        for v, fields in enumerate(variants):
            if tpl == "paste":
                fields = {"delim": "\t" if fields["delim"] == "\\t" else fields["delim"]}
            name = f"{tpl}_{rng.choice(['daily', 'report', 'ops', 'audit', 'nightly'])}_{v}"
            units.append({"name": name, "template": tpl, "fields": fields})
    return units


def script(unit):
    sh, _, _ = TEMPLATES[unit["template"]][0](unit["fields"])
    return f"#!/usr/bin/env bash\n# {unit['name']}\nset -euo pipefail\nexport LC_ALL=C\n{sh}\n"


def inputs(seed, unit, which, size):
    _, _, make = TEMPLATES[unit["template"]][0](unit["fields"])
    return make(rng_for(seed, which, unit["name"]), size)


def generate(seed, out=None):
    truth = {"seed": seed, "scripts": {}}
    files = {}
    for u in plan(seed):
        files[f"scripts/{u['name']}.sh"] = script(u)
        sample = inputs(seed, u, "sample", 40)
        for fname, text in sample:
            files[f"samples/{u['name']}/{fname}"] = text
        truth["scripts"][u["name"]] = {"unit": u, "unit_chars": len(files[f"scripts/{u['name']}.sh"]) + 4000}
    files["README.md"] = ("# ops toolbox\n\nEach `scripts/<name>.sh` takes its input files as arguments and "
                          "writes to stdout. `samples/<name>/` holds example inputs, in argument order.\n")
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def hidden_cases(seed, unit):
    return [inputs(seed, unit, f"hidden-{k}", size) for k, size in enumerate((0, 1, 7, 60, 300))]


def expected_output(unit, case):
    _, oracle, _ = TEMPLATES[unit["template"]][0](unit["fields"])
    return oracle([text for _, text in case])


# The port runs under an audit hook that refuses to start another process, so
# a "port" that shells out to the original pipeline earns nothing. Audit hooks
# cannot be removed once installed.
NO_SUBPROCESSES = """
import runpy, sys
BLOCKED = ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty")
def hook(event, args):
    if event in BLOCKED:
        raise RuntimeError("ports may not run other programs")
sys.addaudithook(hook)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def grade(seed, workspace):
    """Per script: the fraction of hidden input sets on which `python3
    py/<name>.py <files...>` prints exactly what the pipeline prints."""
    truth = generate(seed)
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, info in truth["scripts"].items():
            port = Path(workspace) / "py" / f"{name}.py"
            if not port.exists():
                per[name] = 0.0
                continue
            ok = 0
            cases = hidden_cases(seed, info["unit"])
            for k, case in enumerate(cases):
                paths = []
                for fname, text in case:
                    p = Path(tmp) / f"{name}-{k}-{fname}"
                    p.write_text(text)
                    paths.append(str(p))
                try:
                    run = subprocess.run([sys.executable, "-c", NO_SUBPROCESSES, str(port), *paths],
                                         capture_output=True, timeout=30,
                                         env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
                    ok += run.stdout.decode(errors="replace") == expected_output(info["unit"], case)
                except subprocess.TimeoutExpired:
                    pass
            per[name] = round(ok / len(cases), 4)
    return {"reward": round(sum(per.values()) / len(per), 4), "scripts": per}


ORACLE_PORT = '''"""Reference port (generated)."""
import importlib.util
import sys
from pathlib import Path

ref = Path(__file__).resolve().parent / "_ref"
sys.path.insert(0, str(ref))
spec = importlib.util.spec_from_file_location("gen", ref / "generate.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
unit = {unit!r}
_, oracle, _ = g.TEMPLATES[unit["template"]][0](unit["fields"])
sys.stdout.write(oracle([open(p).read() for p in sys.argv[1:]]))
'''


def solve(seed, workspace):
    here = Path(__file__).resolve().parent
    ref = Path(workspace) / "py" / "_ref"
    write(ref, "generate.py", Path(__file__).read_text())
    write(ref, "common.py", (here / "common.py").read_text())
    for name, info in generate(seed)["scripts"].items():
        write(Path(workspace) / "py", f"{name}.py", ORACLE_PORT.format(unit=info["unit"]))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [s["unit_chars"] for s in t["scripts"].values()],
            "judgement_turns": 7, "orchestration_turns": 10, "shared_chars": 500}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Retire the shell toolbox

Port every pipeline in `/workspace/scripts/` to Python: `py/<name>.py`, taking
the same file arguments and printing exactly the same bytes to stdout. Example
inputs are in `samples/<name>/` (in argument order), and you can run the
original scripts to compare.

The ports will replace the scripts everywhere they run, on inputs you have not
seen, where the shell tools are not installed: pure Python, standard library
only, and a port may not run other programs.
"""

META = {
    "unit": "script", "kind": "language port", "domain": "shell scripts", "output_tokens": 1800, "needs_pytest": False, "apt": ["gawk"],
    "failure_mode": "faithful translation: reproducing a tool's exact observable behaviour",
    "deliverable": "`py/<name>.py` for each of 40 scripts",
    "grading": "Per script: the fraction of five hidden input sets (including empty and one-line inputs) on "
               "which the port's stdout equals the pipeline's byte for byte. Reward is the mean.",
    "per_unit": "work out exactly what each tool in the pipeline does to edge cases (ties, padding, number "
                "formatting, missing fields, empty input), port it, and diff against the script on samples",
    "traps": [
        "**`uniq -c` padding** and **`sort -rn` ties** (the last-resort comparison reverses too).",
        "**awk number formatting**: large or fractional sums print as `%.6g`.",
        "**`cut`** prints lines without the delimiter unchanged; **`join`** drops unpaired lines and "
        "multiplies duplicates; **`paste`** pads the shorter file.",
        "**Empty input** must print exactly what the pipeline prints (often nothing, `grep -c` prints 0).",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
