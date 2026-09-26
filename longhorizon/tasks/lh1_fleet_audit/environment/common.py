"""Shared, deterministic building blocks for the long-horizon generators.

Every generator must be a pure function of its seed: the Docker build runs it to
lay out the workspace, and the verifier runs the same file again to recover the
ground truth. Nothing here may read the clock, the environment, or global
random state.

This file is copied verbatim next to each generator (see
tools/build_longhorizon.py), because a Docker build context cannot reach outside
its own directory. The copies are checked against this source by the tests.
"""

import json
import random
from pathlib import Path

VERBS = ["load", "build", "resolve", "normalize", "merge", "render", "collect",
         "validate", "index", "encode", "decode", "partition", "reconcile",
         "hydrate", "flush", "compact", "annotate", "schedule", "dispatch", "sample"]
NOUNS = ["batch", "record", "window", "cursor", "payload", "ledger", "segment",
         "manifest", "snapshot", "bucket", "digest", "envelope", "shard", "span",
         "profile", "quota", "lease", "journal", "catalog", "rollup"]
ADJS = ["pending", "stale", "active", "cached", "remote", "local", "partial",
        "primary", "shadow", "legacy", "deferred", "sealed", "draft", "hot", "cold"]

# Claude Code truncates a Bash result at about 30k characters; mini-swe-agent's
# default observation template truncates earlier. A unit larger than this cannot
# be taken in with one call.
TOOL_OUTPUT_CHARS = 30_000


def rng_for(seed, *labels):
    """An independent, reproducible stream per (seed, labels) -- so adding a unit
    never reshuffles the ones generated before it."""
    return random.Random("|".join([str(seed), *map(str, labels)]))


def ident(rng, parts=2):
    pools = [VERBS, ADJS, NOUNS]
    words = [rng.choice(pools[(i + (0 if parts > 2 else 1)) % 3]) for i in range(parts)]
    return "_".join(words)


def filler_function(rng, name=None):
    """A plausible, self-contained helper: docstring, a loop, a branch.

    Filler is what makes a unit expensive to read. It is deliberately inert --
    no network, no auth, no I/O -- so it can never become an accidental answer.
    """
    name = name or ident(rng, 3)
    arg = rng.choice(NOUNS)
    other = rng.choice(ADJS)
    limit = rng.randint(3, 400)
    body = [
        f"def {name}({arg}s, *, {other}_limit={limit}):",
        f'    """{rng.choice(VERBS).capitalize()} {arg}s that are {other}, up to {other}_limit.',
        "",
        f"    Order is preserved. Items without an id are skipped rather than raised on,",
        f"    because upstream {rng.choice(NOUNS)} producers emit them during backfills.",
        '    """',
        "    out = []",
        f"    for item in {arg}s:",
        "        if not item.get(\"id\"):",
        "            continue",
        f"        if len(out) >= {other}_limit:",
        "            break",
        f"        item = dict(item, {rng.choice(NOUNS)}_seen=True)",
    ]
    if rng.random() < 0.5:
        body += [f"        if item.get(\"{rng.choice(ADJS)}\"):",
                 f"            item[\"weight\"] = item.get(\"weight\", 1) * {rng.randint(2, 9)}"]
    body += ["        out.append(item)", "    return out", ""]
    return "\n".join(body)


def filler_module(rng, n_functions, header="", topic=None):
    """`topic` puts a unit's own vocabulary into some filler names, so grepping
    for the resource a unit owns returns many hits, not just the one that matters."""
    parts = [f'"""{header or ident(rng, 2).replace("_", " ").capitalize()} helpers."""', "",
             "import logging", "", "log = logging.getLogger(__name__)", ""]
    for _ in range(n_functions):
        name = None
        if topic and rng.random() < 0.3:
            name = f"{rng.choice(VERBS)}_{topic}_{rng.choice(NOUNS)}"
        parts.append(filler_function(rng, name))
        parts.append("")
    return "\n".join(parts)


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def write_json(root, rel, obj):
    return write(root, rel, json.dumps(obj, indent=2, sort_keys=True) + "\n")


def tree_chars(root, glob="**/*"):
    """Characters a reader must take in to cover everything under root."""
    return sum(p.stat().st_size for p in Path(root).glob(glob) if p.is_file())
