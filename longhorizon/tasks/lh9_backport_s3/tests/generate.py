#!/usr/bin/env python3
"""LH9 -- backport a path-traversal fix to every supported release line.

releases/<X.Y>/ holds a snapshot of `pathguard` for each of 32 release lines.
fix/PATHGUARD-2026-004.patch fixes path traversal on main (4.x). The code the
patch touches looks different in each era:

- 1.x: `pathguard/util.py::safe_join(root, user_path)`
- early 2.x: `pathguard/paths.py::PathJoiner.join(*parts)`
- late 2.x and 3.x: `pathguard/_impl/resolve.py::resolve_under`, re-exported
  as `pathguard.safe_join`
- 4.x: `pathguard/core.py::join_under`, the code the patch was written against

and the era boundaries move per seed. So every line has to be read to find the
code the fix belongs in -- there is no single file to patch 32 times.

Two kinds of line must NOT be touched: the end-of-life lines in SUPPORT.md
(a constraint the orchestrator must pass down, like LH2's billing packages),
and the lines that are not affected -- the earliest 1.x predate the feature,
and a run of 3.x already had a containment check. Leaving those unchanged,
and saying so, is part of the answer (DESIGN.md F3, a genuine negative).

A hidden exploit test grades every affected supported line. Each line's own
tests must still pass.

    python3 lh9_backport.py --seed 1 --out /fixture
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_module, rng_for, write  # noqa: E402

VERSIONS = [f"{a}.{b}" for a in (1, 2, 3) for b in range(10)] + ["4.0", "4.1"]

ERA_CODE = {
    "none": ('''"""pathguard: path helpers (this line has no join helper yet)."""

import os


def normalise(path):
    return os.path.normpath(path)
''', None),
    "A": ('''"""pathguard.util"""

import os


def safe_join(root, user_path):
    """Join a user-supplied relative path under root."""
    return os.path.join(root, user_path.lstrip("/"))
''', '''"""pathguard.util"""

import os


def safe_join(root, user_path):
    """Join a user-supplied relative path under root."""
    root_abs = os.path.abspath(root)
    candidate = os.path.abspath(os.path.join(root_abs, user_path.lstrip("/")))
    if os.path.commonpath([root_abs, candidate]) != root_abs:
        raise ValueError(f"path escapes root: {user_path!r}")
    return candidate
'''),
    "B": ('''"""pathguard.paths"""

import os

from pathguard.errors import UnsafePathError


class PathJoiner:
    def __init__(self, root):
        self.root = root

    def join(self, *parts):
        """Join parts under the root. Absolute parts are rejected."""
        for part in parts:
            if os.path.isabs(part):
                raise UnsafePathError(part)
        return os.path.join(self.root, *parts)
''', '''"""pathguard.paths"""

import os

from pathguard.errors import UnsafePathError


class PathJoiner:
    def __init__(self, root):
        self.root = root

    def join(self, *parts):
        """Join parts under the root. Absolute parts are rejected."""
        for part in parts:
            if os.path.isabs(part):
                raise UnsafePathError(part)
        root_abs = os.path.abspath(self.root)
        candidate = os.path.abspath(os.path.join(root_abs, *parts))
        if os.path.commonpath([root_abs, candidate]) != root_abs:
            raise UnsafePathError(os.path.join(*parts))
        return candidate
'''),
    "C": ('''"""pathguard._impl.resolve"""

import os


def resolve_under(root, candidate, *, follow_symlinks=False):
    """Resolve candidate relative to root."""
    joined = os.path.join(root, candidate)
    return os.path.realpath(joined) if follow_symlinks else os.path.normpath(joined)
''', '''"""pathguard._impl.resolve"""

import os

from pathguard.errors import UnsafePath


def resolve_under(root, candidate, *, follow_symlinks=False):
    """Resolve candidate relative to root."""
    joined = os.path.join(root, candidate)
    resolved = os.path.realpath(joined) if follow_symlinks else os.path.normpath(joined)
    base = os.path.realpath(root) if follow_symlinks else os.path.normpath(os.path.abspath(root))
    if os.path.commonpath([base, os.path.abspath(resolved)]) != base:
        raise UnsafePath(candidate)
    return resolved
'''),
    "C_safe": ('''"""pathguard._impl.resolve"""

import os

from pathguard.errors import UnsafePath


def resolve_under(root, candidate, *, follow_symlinks=False):
    """Resolve candidate relative to root, refusing anything outside it."""
    base = os.path.normpath(os.path.abspath(root))
    resolved = os.path.normpath(os.path.join(base, candidate))
    if os.path.commonpath([base, resolved]) != base:
        raise UnsafePath(candidate)
    return os.path.realpath(resolved) if follow_symlinks else resolved
''', None),
    "D": ('''"""pathguard.core"""

import os

from pathguard.errors import UnsafePath


def join_under(root, *parts):
    """Join parts under root."""
    return os.path.normpath(os.path.join(root, *parts))
''', '''"""pathguard.core"""

import os

from pathguard.errors import UnsafePath


def join_under(root, *parts):
    """Join parts under root."""
    base = os.path.normpath(os.path.abspath(root))
    joined = os.path.normpath(os.path.join(base, *parts))
    if os.path.commonpath([base, joined]) != base:
        raise UnsafePath(os.path.join(*parts))
    return joined
'''),
}
MODULE_PATH = {"none": "pathguard/util.py", "A": "pathguard/util.py", "B": "pathguard/paths.py",
               "C": "pathguard/_impl/resolve.py", "C_safe": "pathguard/_impl/resolve.py",
               "D": "pathguard/core.py"}
INIT = {"none": "", "A": "", "B": "",
        "C": "from pathguard._impl.resolve import resolve_under as safe_join  # noqa: F401\n",
        "C_safe": "from pathguard._impl.resolve import resolve_under as safe_join  # noqa: F401\n",
        "D": "from pathguard.core import join_under  # noqa: F401\n"}
ERRORS = '''"""pathguard.errors"""


class UnsafePathError(ValueError):
    pass


UnsafePath = UnsafePathError
'''
LEGIT = {  # a call that must keep working, per era
    "A": ("from pathguard.util import safe_join", "safe_join(root, 'a/b.txt')"),
    "B": ("from pathguard.paths import PathJoiner", "PathJoiner(root).join('a', 'b.txt')"),
    "C": ("from pathguard import safe_join", "safe_join(root, 'a/b.txt')"),
    "D": ("from pathguard import join_under", "join_under(root, 'a', 'b.txt')"),
}
EXPLOIT = {
    "A": "safe_join(root, '../../etc/passwd')",
    "B": "PathJoiner(root).join('a', '../../../etc/passwd')",
    "C": "safe_join(root, '../../etc/passwd')",
    "D": "join_under(root, '..', '..', 'etc', 'passwd')",
}

PATCH = '''--- a/pathguard/core.py
+++ b/pathguard/core.py
@@ def join_under(root, *parts):
     """Join parts under root."""
-    return os.path.normpath(os.path.join(root, *parts))
+    base = os.path.normpath(os.path.abspath(root))
+    joined = os.path.normpath(os.path.join(base, *parts))
+    if os.path.commonpath([base, joined]) != base:
+        raise UnsafePath(os.path.join(*parts))
+    return joined
'''


def plan(seed):
    rng = rng_for(seed, "plan")
    b_end = rng.randint(3, 5)          # 2.0 .. 2.b_end are era B
    safe_start = rng.randint(2, 5)     # 3.safe_start .. +2 already had the check
    none_end = rng.randint(1, 3)       # 1.0 .. 1.none_end predate the join helper
    lines = {}
    for v in VERSIONS:
        major, minor = map(int, v.split("."))
        if major == 1:
            era = "none" if minor <= none_end else "A"
        elif major == 2:
            era = "B" if minor <= b_end else "C"
        elif major == 3:
            era = "C_safe" if safe_start <= minor <= safe_start + 2 else "C"
        else:
            era = "D"
        lines[v] = {"era": era}
    eol = set(rng.sample([v for v in VERSIONS if not v.startswith("4")], 8))
    for v, info in lines.items():
        info["supported"] = v not in eol
        info["affected"] = info["era"] in ("A", "B", "C", "D")
    return lines


def line_files(rng, version, era):
    files = {
        "pathguard/__init__.py": f'"""pathguard {version}"""\n\n__version__ = "{version}"\n' + INIT[era],
        MODULE_PATH[era]: ERA_CODE[era][0],
        "CHANGELOG.md": f"# pathguard {version}\n\n- Maintenance release.\n",
    }
    if era in ("B", "C", "C_safe", "D"):
        files["pathguard/errors.py"] = ERRORS
    if era.startswith("C"):
        files["pathguard/_impl/__init__.py"] = ""
    for k in range(rng.randint(2, 4)):
        files[f"pathguard/{rng.choice(['fs', 'io', 'text', 'glob'])}_{k}.py"] = filler_module(rng, rng.randint(5, 9))
    legit_era = "C" if era == "C_safe" else era
    if legit_era in LEGIT:
        imp, call = LEGIT[legit_era]
        files["tests/test_basic.py"] = (
            f"import os\n\n{imp}\n\n\ndef test_joins_relative_paths(tmp_path):\n"
            f"    root = str(tmp_path)\n    assert {call} == os.path.join(root, 'a', 'b.txt')\n")
    else:
        files["tests/test_basic.py"] = ("from pathguard.util import normalise\n\n\n"
                                        "def test_normalise():\n    assert normalise('a/./b') == 'a/b'\n")
    files["tests/conftest.py"] = ("import sys\nfrom pathlib import Path\n\n"
                                  "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n")
    return files


def exploit_test(era):
    era = "C" if era == "C_safe" else era
    imp, _ = LEGIT[era]
    return (f"import pytest\n\n{imp}\n\n\n@pytest.mark.parametrize('n', [0])\n"
            f"def test_traversal_is_refused(tmp_path, n):\n    root = str(tmp_path / 'srv')\n"
            f"    with pytest.raises(ValueError):\n        {EXPLOIT[era]}\n")


def support_md(lines):
    rows = "\n".join(f"| {v} | {'supported' if i['supported'] else 'end of life -- do not patch'} |"
                     for v, i in lines.items())
    return ("# Supported release lines\n\nSecurity fixes are backported to every supported line. "
            "End-of-life lines are frozen: no changes of any kind.\n\n| line | status |\n|---|---|\n"
            + rows + "\n")


def generate(seed, out=None):
    lines = plan(seed)
    files = {"SUPPORT.md": support_md(lines), "fix/PATHGUARD-2026-004.patch": PATCH,
             "fix/README.md": "Fix for PATHGUARD-2026-004 (path traversal), written against main (4.x).\n"
                              "Backport it to every supported release line under releases/.\n",
             "pytest.ini": "[pytest]\naddopts = -q -p no:cacheprovider --import-mode=importlib\n"}
    truth = {"seed": seed, "lines": {}}
    for v, info in lines.items():
        rng = rng_for(seed, "line", v)
        lf = line_files(rng, v, info["era"])
        for rel, text in lf.items():
            files[f"releases/{v}/{rel}"] = text
        truth["lines"][v] = {**info, "unit_chars": sum(len(t) for t in lf.values())}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


def apply_oracle(seed, workspace):
    truth, _ = generate(seed)
    for v, info in truth["lines"].items():
        if info["supported"] and info["affected"]:
            write(Path(workspace) / "releases" / v, MODULE_PATH[info["era"]], ERA_CODE[info["era"]][1])


def _line_passes(workspace, pristine, v, era):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(Path(workspace) / "releases" / v / "pathguard", tmp / "pathguard")
        for rel, text in pristine.items():
            if rel.startswith(f"releases/{v}/tests/"):
                write(tmp, rel.split(f"releases/{v}/", 1)[1], text)
        write(tmp, "tests/test_exploit.py", exploit_test(era))
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                             cwd=tmp, capture_output=True, text=True, timeout=120)
        return run.returncode == 0


def grade(seed, workspace):
    """Per line. Supported and affected: the hidden exploit test and the line's
    original tests pass against the agent's code. Not affected: every file
    byte-identical. Reward is the mean over all 32 lines -- and 0 if any
    end-of-life line was modified, like LH2's frozen packages."""
    truth, pristine = generate(seed)
    ws = Path(workspace)
    per = {}
    for v, info in truth["lines"].items():
        prefix = f"releases/{v}/"
        mine = {str(p.relative_to(ws)): p.read_text() for p in (ws / "releases" / v).rglob("*")
                if p.is_file() and "__pycache__" not in p.parts} if (ws / "releases" / v).exists() else {}
        theirs = {k: t for k, t in pristine.items() if k.startswith(prefix)}
        if info["supported"] and info["affected"]:
            tests_intact = all(mine.get(k) == t for k, t in theirs.items() if "/tests/" in k)
            per[v] = float(tests_intact and _line_passes(ws, pristine, v, info["era"]))
        else:
            per[v] = float(mine == theirs)
    breaches = [v for v, info in truth["lines"].items() if not info["supported"] and not per[v]]
    reward = 0.0 if breaches else round(sum(per.values()) / len(per), 4)
    return {"reward": reward, "lines": per, "eol_lines_modified": breaches}


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [i["unit_chars"] for i in t["lines"].values()],
            "judgement_turns": 8, "orchestration_turns": 12, "shared_chars": len(PATCH) + 2000}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Backport PATHGUARD-2026-004

`fix/PATHGUARD-2026-004.patch` fixes a path traversal in `pathguard` on main.
Backport it to every supported release line under `/workspace/releases/`.
`SUPPORT.md` says which lines are supported. End-of-life lines are frozen.

The code has moved around between releases, so the patch will not apply as-is.
Put the equivalent fix wherever each line joins paths. A line that does not
have the vulnerable code needs no change. Each line's own tests
(`releases/<line>/tests/`) must keep passing; do not edit them.

When you are done, write `/workspace/BACKPORT_REPORT.md` with one line per
release line: patched, not affected (and why), or end of life.
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out")
    ap.add_argument("--grade")
    ap.add_argument("--solve")
    args = ap.parse_args(argv)
    if args.grade:
        print(json.dumps(grade(args.seed, args.grade), indent=2))
    elif args.solve:
        apply_oracle(args.seed, args.solve)
    else:
        generate(args.seed, args.out)


if __name__ == "__main__":
    main()
