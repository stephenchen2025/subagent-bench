#!/usr/bin/env python3
"""LH8 -- port 36 plugins to a new API, with two files every port must touch.

Each plugin under plugins/ implements the v1 API: a module with NAME, VERSION
and `run(ctx)`, where ctx is a dict and the dry-run flag's key varies by plugin
(`dry`, `dry_run`, `simulate`, `noop` -- each plugin's docstring says which).
The v2 API (pluginapi/base.py) is a class with `execute(ctx, *, dry_run=False)`
that returns a Result and must not touch the filesystem on a dry run.

This is DESIGN.md F7, parallel siblings over shared state. Every port must also
add its line to two SHARED files: pluginapi/registry.py (kept sorted, one entry
per plugin) and CHANGELOG.md. Subagents that each rewrite those files overwrite
one another, and the plugins whose registration was lost fail their tests. The
orchestrator has to own the shared edits, for example by collecting each
subagent's registry line and writing the file once.

    python3 lh8_plugin_port.py --seed 1 --out /fixture
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, rng_for, write  # noqa: E402

N_PLUGINS = 36
BEHAVIOURS = ["header", "manifest", "cleanup", "rename", "normalize"]
DRY_KEYS = ["dry", "dry_run", "simulate", "noop"]
WORDS = ["stamp", "index", "sweep", "shift", "tidy", "tag", "pack", "prune", "label", "trim",
         "scan", "fold", "mark", "sort", "seal", "sync"]
OBJECTS = ["headers", "assets", "notes", "logs", "drafts", "exports", "reports", "docs", "specs"]

BASE = '''"""Plugin API v2."""

from dataclasses import dataclass, field


@dataclass
class Context:
    workspace: str
    config: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)

    def log(self, message):
        self.messages.append(message)


@dataclass
class Result:
    changed: list            # sorted file names the plugin changed (or would change, on a dry run)
    messages: list = field(default_factory=list)


class Plugin:
    """Subclass per plugin. `name` and `version` are class attributes; keep the
    v1 NAME and VERSION values. The class is named after the plugin in
    CamelCase with a `Plugin` suffix: `stamp-headers` -> `StampHeadersPlugin`."""

    name = None
    version = None

    def execute(self, ctx, *, dry_run=False):
        """Do the work described by ctx.config under ctx.workspace. On a dry
        run, touch nothing on disk but return the same `changed` list."""
        raise NotImplementedError
'''

REGISTRY = '''"""Every v2 plugin, by name. Keep entries sorted by name, one per plugin.

    "stamp-headers": "plugins.stamp_headers.plugin:StampHeadersPlugin",
"""

import importlib

PLUGINS = {
}


def load(name):
    module, cls = PLUGINS[name].split(":")
    return getattr(importlib.import_module(module), cls)()
'''

PORTING_MD = '''# Porting a plugin from API v1 to v2

| v1 | v2 |
|---|---|
| module constants `NAME`, `VERSION` | class attributes `name`, `version` (same values) |
| `run(ctx)` with `ctx` a dict | `execute(self, ctx, *, dry_run=False)` with `ctx` a `Context` |
| `ctx["workspace"]`, `ctx["config"]` | `ctx.workspace`, `ctx.config` |
| `ctx["logger"].info(...)` | `ctx.log(...)` |
| the dry-run key named in the plugin's docstring | the `dry_run` argument |
| returns a list of changed file names | returns `Result(changed=sorted(names))` |

Then, for every plugin:

1. register it in `pluginapi/registry.py` (sorted by name, one entry each);
2. add a line under `## Unreleased` in `CHANGELOG.md`: `- <name>: ported to API v2`.

`tests/` covers the registry and every plugin. Do not edit the tests.
'''


def camel(name):
    return "".join(w.capitalize() for w in name.split("-")) + "Plugin"


def v1_source(p, rng):
    dry, cfg = p["dry_key"], p["config"]
    head = (f'"""{p["name"]} (plugin API v1).\n\nHonours ctx["{dry}"] as its dry-run flag."""\n\n'
            "from pathlib import Path\n\n"
            f'NAME = "{p["name"]}"\nVERSION = "{p["version"]}"\n\n\n')
    b = p["behaviour"]
    if b == "header":
        core = f'''def run(ctx):
    root = Path(ctx["workspace"])
    header = ctx["config"].get("header", "{cfg['header']}")
    changed = []
    for path in sorted(root.glob("*.txt")):
        text = path.read_text()
        if text.startswith(header):
            continue
        changed.append(path.name)
        if not ctx.get("{dry}"):
            path.write_text(header + "\\n" + text)
    ctx["logger"].info("stamped %d files", len(changed))
    return changed
'''
    elif b == "manifest":
        core = f'''def run(ctx):
    import json
    root = Path(ctx["workspace"])
    target = ctx["config"].get("manifest", "{cfg['manifest']}")
    entries = {{p.name: p.stat().st_size for p in sorted(root.iterdir()) if p.is_file() and p.name != target}}
    if not ctx.get("{dry}"):
        (root / target).write_text(json.dumps(entries, sort_keys=True))
    ctx["logger"].info("indexed %d files", len(entries))
    return [target]
'''
    elif b == "cleanup":
        core = f'''def run(ctx):
    root = Path(ctx["workspace"])
    pattern = ctx["config"].get("pattern", "{cfg['pattern']}")
    changed = []
    for path in sorted(root.glob(pattern)):
        changed.append(path.name)
        if not ctx.get("{dry}"):
            path.unlink()
    ctx["logger"].info("removed %d files", len(changed))
    return changed
'''
    elif b == "rename":
        core = f'''def run(ctx):
    root = Path(ctx["workspace"])
    src = ctx["config"].get("from_ext", "{cfg['from_ext']}")
    dst = ctx["config"].get("to_ext", "{cfg['to_ext']}")
    changed = []
    for path in sorted(root.glob("*" + src)):
        new = path.with_suffix(dst)
        changed.append(new.name)
        if not ctx.get("{dry}"):
            path.rename(new)
    ctx["logger"].info("renamed %d files", len(changed))
    return sorted(changed)
'''
    else:
        core = f'''def run(ctx):
    root = Path(ctx["workspace"])
    changed = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text()
        clean = "\\n".join(line.rstrip() for line in text.splitlines()) + "\\n"
        if clean == text:
            continue
        changed.append(path.name)
        if not ctx.get("{dry}"):
            path.write_text(clean)
    ctx["logger"].info("normalised %d files", len(changed))
    return changed
'''
    filler = "\n\n".join(filler_function(rng) for _ in range(rng.randint(5, 9)))
    return head + core + "\n\n" + filler + "\n"


def v2_source(p):
    """The reference port, derived from the v1 `run` body."""
    v1 = v1_source(p, rng_for(0, "oracle", p["name"]))
    run = v1[v1.index("def run(ctx):"):]
    run = run[: run.index("\n\n\n")]
    run = (run.replace("def run(ctx):", "def execute(self, ctx, *, dry_run=False):")
              .replace('ctx["workspace"]', "ctx.workspace").replace('ctx["config"]', "ctx.config")
              .replace(f'ctx.get("{p["dry_key"]}")', "dry_run")
              .replace("return sorted(changed)", "return Result(changed=sorted(changed))")
              .replace("return changed", "return Result(changed=sorted(changed))")
              .replace("return [target]", "return Result(changed=[target])"))
    run = re.sub(r'ctx\["logger"\]\.info\("([^"]*)%d([^"]*)", (.*)\)$', r'ctx.log(f"\1{\3}\2")', run, flags=re.M)
    run = "\n".join("    " + line if line else line for line in run.splitlines())
    return (f'"""{p["name"]} (plugin API v2)."""\n\nfrom pathlib import Path\n\n'
            "from pluginapi.base import Plugin, Result\n\n\n"
            f"class {camel(p['name'])}(Plugin):\n"
            f'    name = "{p["name"]}"\n    version = "{p["version"]}"\n\n' + run + "\n")


def test_source(p):
    pkg = p["name"].replace("-", "_")
    b, cfg = p["behaviour"], p["config"]
    setup = {
        "header": ({"a.txt": "alpha", "b.txt": f"{cfg['header']}\nbeta", "c.md": "gamma"}, ["a.txt"]),
        "manifest": ({"a.txt": "alpha", "b.bin": "bb"}, [cfg["manifest"]]),
        "cleanup": ({"keep.txt": "k", "x" + cfg["pattern"][1:]: "x", "y" + cfg["pattern"][1:]: "y"},
                    sorted(["x" + cfg["pattern"][1:], "y" + cfg["pattern"][1:]])),
        "rename": ({"one" + cfg["from_ext"]: "1", "two" + cfg["from_ext"]: "2", "three.keep": "3"},
                   sorted(["one" + cfg["to_ext"], "two" + cfg["to_ext"]])),
        "normalize": ({"a.md": "x  \ny\n", "b.md": "clean\n", "c.txt": "t  \n"}, ["a.md"]),
    }[b]
    files, expected = setup
    return f'''"""{p["name"]}: behaviour under API v2. Do not edit."""

from pathlib import Path

from pluginapi import registry
from pluginapi.base import Context, Result

FILES = {files!r}
EXPECTED = {expected!r}


def _workspace(tmp_path):
    for name, text in FILES.items():
        (tmp_path / name).write_text(text)
    return tmp_path


def _snapshot(root):
    return {{p.name: p.read_text() for p in sorted(Path(root).iterdir())}}


def test_registered_and_versioned():
    plugin = registry.load("{p["name"]}")
    assert plugin.name == "{p["name"]}" and plugin.version == "{p["version"]}"
    assert type(plugin).__name__ == "{camel(p["name"])}"


def test_execute(tmp_path):
    ctx = Context(workspace=str(_workspace(tmp_path)), config={{}})
    result = registry.load("{p["name"]}").execute(ctx)
    assert isinstance(result, Result) and result.changed == EXPECTED
    assert ctx.messages


def test_dry_run_touches_nothing(tmp_path):
    root = _workspace(tmp_path)
    before = _snapshot(root)
    result = registry.load("{p["name"]}").execute(Context(workspace=str(root)), dry_run=True)
    assert result.changed == EXPECTED
    assert _snapshot(root) == before
'''


REGISTRY_TEST = '''"""The shared registry. Do not edit."""

import ast
from pathlib import Path

from pluginapi import registry

ROOT = Path(__file__).resolve().parents[1]


def test_every_plugin_registered_once_and_sorted():
    names = sorted(p.parent.name.replace("_", "-") for p in (ROOT / "plugins").glob("*/plugin.py"))
    keys = [k.value for k in ast.parse((ROOT / "pluginapi" / "registry.py").read_text()).body[2].value.keys]
    assert keys == sorted(keys), "registry is not sorted"
    assert len(keys) == len(set(keys)), "duplicate registry entries"
    assert sorted(registry.PLUGINS) == names
'''


def plan(seed, n=N_PLUGINS):
    rng = rng_for(seed, "plan")
    names = rng.sample([f"{w}-{o}" for w in WORDS for o in OBJECTS], n)
    plugins = []
    for i, name in enumerate(sorted(names)):
        prng = rng_for(seed, "plugin", name)
        plugins.append({
            "name": name, "version": f"1.{prng.randint(0, 9)}.{prng.randint(0, 9)}",
            "behaviour": BEHAVIOURS[i % len(BEHAVIOURS)], "dry_key": prng.choice(DRY_KEYS),
            "config": {"header": f"# {prng.choice(['generated', 'managed', 'do not edit'])} by {name}",
                       "manifest": prng.choice(["MANIFEST.json", "index.json", "files.json"]),
                       "pattern": prng.choice(["*.tmp", "*.bak", "*.orig"]),
                       "from_ext": prng.choice([".yml", ".jpeg", ".htm"]),
                       "to_ext": prng.choice([".yaml", ".jpg", ".html"])},
        })
    return plugins


def generate(seed, out=None, n=N_PLUGINS):
    plugins = plan(seed, n)
    files = {"pluginapi/__init__.py": "", "pluginapi/base.py": BASE, "pluginapi/registry.py": REGISTRY,
             "plugins/__init__.py": "", "docs/PORTING.md": PORTING_MD,
             "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\n## 3.2.0\n\n- Plugin API v2 introduced.\n",
             "tests/conftest.py": "import sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n",
             "tests/test_registry.py": REGISTRY_TEST,
             "pytest.ini": "[pytest]\naddopts = -q -p no:cacheprovider --import-mode=importlib\n"}
    truth = {"seed": seed, "plugins": {}}
    for p in plugins:
        pkg = p["name"].replace("-", "_")
        rng = rng_for(seed, "files", p["name"])
        files[f"plugins/{pkg}/__init__.py"] = ""
        files[f"plugins/{pkg}/plugin.py"] = v1_source(p, rng)
        files[f"tests/plugins/test_{pkg}.py"] = test_source(p)
        truth["plugins"][p["name"]] = {"package": pkg, "class": camel(p["name"]), "dry_key": p["dry_key"],
                                      "behaviour": p["behaviour"], "oracle": v2_source(p),
                                      "unit_chars": len(files[f"plugins/{pkg}/plugin.py"])
                                      + len(files[f"tests/plugins/test_{pkg}.py"])}
    truth["shared_chars"] = len(BASE) + len(REGISTRY) + len(PORTING_MD)
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


def apply_oracle(seed, workspace):
    truth, _ = generate(seed)
    ws = Path(workspace)
    entries = []
    for name, t in sorted(truth["plugins"].items()):
        write(ws / "plugins" / t["package"], "plugin.py", t["oracle"])
        entries.append(f'    "{name}": "plugins.{t["package"]}.plugin:{t["class"]}",')
    reg = (ws / "pluginapi" / "registry.py").read_text().replace("PLUGINS = {\n}", "PLUGINS = {\n" + "\n".join(entries) + "\n}")
    (ws / "pluginapi" / "registry.py").write_text(reg)
    log = "\n".join(f"- {name}: ported to API v2" for name in sorted(truth["plugins"]))
    cl = (ws / "CHANGELOG.md").read_text().replace("## Unreleased\n", f"## Unreleased\n\n{log}\n", 1)
    (ws / "CHANGELOG.md").write_text(cl)


def grade(seed, workspace):
    """Per plugin: its pristine tests pass against the agent's plugin and the
    agent's registry, and its CHANGELOG line exists. 0.1 of the reward is the
    registry itself being sorted, complete and duplicate-free. Editing a test
    is caught (the pristine copies are what run)."""
    ws = Path(workspace)
    truth, pristine = generate(seed)
    changelog = (ws / "CHANGELOG.md").read_text() if (ws / "CHANGELOG.md").exists() else ""
    unreleased = changelog.split("## Unreleased", 1)[-1].split("\n## ", 1)[0]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for rel, text in pristine.items():
            if rel.startswith(("tests/", "pluginapi/base.py", "pluginapi/__init__.py", "plugins/__init__.py", "pytest.ini")):
                write(tmp, rel, text)
        if (ws / "pluginapi" / "registry.py").exists():
            shutil.copy(ws / "pluginapi" / "registry.py", tmp / "pluginapi" / "registry.py")
        for name, t in truth["plugins"].items():
            src = ws / "plugins" / t["package"]
            if src.exists():
                shutil.copytree(src, tmp / "plugins" / t["package"], dirs_exist_ok=True)
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rA", "tests"], cwd=tmp,
                             capture_output=True, text=True, timeout=600)
    failed = set(re.findall(r"^(?:FAILED|ERROR) tests/(?:plugins/)?(\S+?)\.py", run.stdout, re.M))
    passed_any = set(re.findall(r"^PASSED tests/(?:plugins/)?(\S+?)\.py", run.stdout, re.M))
    per = {}
    for name, t in truth["plugins"].items():
        mod = f"test_{t['package']}"
        per[name] = float(mod in passed_any and mod not in failed
                          and f"- {name}:" in unreleased)
    registry_ok = "test_registry" in passed_any and "test_registry" not in failed
    reward = 0.9 * sum(per.values()) / len(per) + 0.1 * registry_ok
    return {"reward": round(reward, 4), "registry_ok": registry_ok, "plugins": per,
            "ported": int(sum(per.values())), "of": len(per)}


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [p["unit_chars"] for p in t["plugins"].values()],
            "judgement_turns": 7, "orchestration_turns": 14, "shared_chars": t["shared_chars"]}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Port every plugin to API v2

API v1 is removed in the next release. Port every plugin under
`/workspace/plugins/` to the v2 API in `pluginapi/base.py`. `docs/PORTING.md`
says what changes and what else each port must update.

`tests/` defines done: `cd /workspace && python -m pytest`. Do not edit the
tests.
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
