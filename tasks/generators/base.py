"""Procedural task generation (DESIGN.md 7.4).

A fixed task set is a contamination liability and a scale problem: Milestone 1
needs 30 tasks and hand-authoring each fixture does not get there. Each family
is a parameterised generator over the py_svc fixture instead -- one seed yields
a variant with different paths, identifiers and values, but the same planted
defect and the same delegation contract.

The important property is that specs are not written by hand against a fixture
that may drift. Anchors are **located by content after generation**, so a spec's
`path:line` citations are true by construction rather than by maintenance.
"""

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

TEXT_SUFFIXES = {".py", ".yml", ".yaml", ".toml", ".md", ".txt", ".cfg", ".json"}


@dataclass
class Variant:
    """One generated task: a fixture on disk plus the spec that describes it."""

    task_id: str
    family: str
    seed: int
    params: dict
    fixture: Path
    spec: dict = field(default_factory=dict)


def copy_fixture(source_repo, out_dir):
    """Copy the base fixture's workspace into a fresh variant directory."""
    out = Path(out_dir)
    repo = out / "repo"
    if repo.exists():
        shutil.rmtree(repo)
    repo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_repo, repo, ignore=shutil.ignore_patterns("__pycache__"))
    return repo


def substitute(root, mapping):
    """Rewrite identifiers across every text file in the fixture.

    Whole-token substitution: the identifiers these generators vary are
    distinctive, and a bare `str.replace` would corrupt substrings of unrelated
    words. Paths (which contain `/` and `.`) are replaced literally.
    """
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = original = path.read_text()
        for old, new in mapping.items():
            if old == new:
                continue
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", old):
                text = re.sub(rf"\b{re.escape(old)}\b", new, text)
            else:
                text = text.replace(old, new)
        if text != original:
            path.write_text(text)


def rename_paths(root, renames):
    """Move files within the fixture, creating parent directories as needed."""
    root = Path(root)
    for old, new in renames.items():
        if old == new:
            continue
        src, dst = root / old, root / new
        if not src.exists():
            raise FileNotFoundError(f"cannot rename missing fixture file: {old}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


def find_anchor(root, relpath, needle):
    """1-based line number of the unique line containing `needle`.

    Raises rather than guessing: an ambiguous or missing anchor means the
    generated spec would cite the wrong evidence, which is worse than failing.
    """
    lines = (Path(root) / relpath).read_text().splitlines()
    hits = [i + 1 for i, line in enumerate(lines) if needle in line]
    if not hits:
        raise LookupError(f"anchor {needle!r} not found in {relpath}")
    if len(hits) > 1:
        raise LookupError(f"anchor {needle!r} is ambiguous in {relpath}: lines {hits}")
    return hits[0]


def probe(question, options, answer, axis="decision", rationale=""):
    """Build a decision probe, always offering the abstention option."""
    from consumer.probe import INSUFFICIENT

    opts = list(options)
    if INSUFFICIENT not in opts:
        opts.append(INSUFFICIENT)
    entry = {"q": question, "options": opts, "answer": answer}
    if axis != "decision":
        entry["axis"] = axis
    if rationale:
        entry["rationale"] = rationale
    return entry


def pick(rng, pool):
    return pool[rng.randrange(len(pool))]


def repo_root():
    """The repository root, inferred from this file's location."""
    return Path(__file__).resolve().parents[2]


def snapshot_path(out_dir, root=None):
    """`env.snapshot` as a path relative to the repo root.

    Specs are resolved as `<root>/<snapshot>/repo`, so this must be rooted at the
    repository, not at whatever directory the generator happened to write into.
    """
    out_dir = Path(out_dir).resolve()
    base = Path(root or repo_root()).resolve()
    try:
        return str(out_dir.relative_to(base))
    except ValueError:
        return str(out_dir)
