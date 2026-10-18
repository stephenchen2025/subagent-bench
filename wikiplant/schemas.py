"""Records that carry the pipeline: paragraph, puzzle, manifest entry.

All three are plain dicts on disk (JSON or JSONL). The validators return a list
of problems, empty when the record is well formed, so callers can report every
fault at once instead of the first one.
"""

import json
from pathlib import Path

ROLES = ("gold", "near_miss", "partial_echo", "decoy")
MODES = ("paragraph", "subsection")
TEMPLATES = ("chain", "intersection", "comparison", "aggregation")
GATES = (
    "closed_book", "base_corpus", "oracle", "oracle_distractors", "consistency",
    "name_collision", "lexical_shortcut", "style", "human_review",
)
GATE_STATES = ("pass", "fail", "pending")

PARAGRAPH_KEYS = ("para_id", "page_id", "title", "section_path", "para_idx", "text", "outlinks")


def para_id(page_id, section_path, para_idx):
    return f"{page_id}:{'/'.join(section_path)}:{para_idx}"


def _missing(rec, keys, what):
    return [f"{what}: missing '{k}'" for k in keys if k not in rec]


def validate_paragraph(rec):
    errs = _missing(rec, PARAGRAPH_KEYS, "paragraph")
    if errs:
        return errs
    if rec["para_id"] != para_id(rec["page_id"], rec["section_path"], rec["para_idx"]):
        errs.append(f"paragraph {rec['para_id']}: para_id does not match page/section/index")
    if not rec["text"].strip():
        errs.append(f"paragraph {rec['para_id']}: empty text")
    return errs


def validate_manifest_entry(rec):
    errs = _missing(rec, ("unit_id", "role", "host_page", "section_path", "mode", "position", "text"), "manifest")
    if errs:
        return errs
    uid = rec["unit_id"]
    if rec["role"] not in ROLES:
        errs.append(f"unit {uid}: role {rec['role']!r} not in {ROLES}")
    if rec["mode"] not in MODES:
        errs.append(f"unit {uid}: mode {rec['mode']!r} not in {MODES}")
    if rec["mode"] == "subsection" and not rec.get("heading"):
        errs.append(f"unit {uid}: a subsection needs a heading")
    if not isinstance(rec["position"], int) or rec["position"] < 0:
        errs.append(f"unit {uid}: position must be a non-negative integer")
    if not rec["section_path"]:
        errs.append(f"unit {uid}: nothing is planted in the lead, section_path must be non-empty")
    if not rec["text"].strip():
        errs.append(f"unit {uid}: empty text")
    return errs


def validate_puzzle(rec, manifest_ids=None):
    errs = _missing(rec, ("pid", "template", "entities", "facts", "path", "question", "answer", "aliases"), "puzzle")
    if errs:
        return errs
    pid = rec["pid"]
    if rec["template"] not in TEMPLATES:
        errs.append(f"puzzle {pid}: template {rec['template']!r} not in {TEMPLATES}")
    eids = {e["eid"] for e in rec["entities"]}
    fids = {f["fid"] for f in rec["facts"]}
    for f in rec["facts"]:
        for end in ("s", "o"):
            if f[end] not in eids:
                errs.append(f"puzzle {pid}: fact {f['fid']} {end} refers to unknown entity {f[end]}")
        if f.get("planted"):
            if "host_page" not in f:
                errs.append(f"puzzle {pid}: planted fact {f['fid']} has no host_page")
        elif "para_id" not in f:
            errs.append(f"puzzle {pid}: real fact {f['fid']} must cite a para_id")
    for step in rec["path"]:
        if step not in fids:
            errs.append(f"puzzle {pid}: path step {step} is not a fact")
    planted = {f["fid"] for f in rec["facts"] if f.get("planted")}
    if not planted.intersection(rec["path"]):
        errs.append(f"puzzle {pid}: path crosses no planted fact, so it is answerable from memory")
    if not str(rec["answer"]).strip():
        errs.append(f"puzzle {pid}: empty answer")
    for g, state in (rec.get("gates") or {}).items():
        if g not in GATES or state not in GATE_STATES:
            errs.append(f"puzzle {pid}: bad gate entry {g}={state}")
    if manifest_ids is not None:
        for f in rec["facts"]:
            if f.get("planted") and f.get("unit_id") and f["unit_id"] not in manifest_ids:
                errs.append(f"puzzle {pid}: fact {f['fid']} cites unit {f['unit_id']} missing from the manifest")
    return errs


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write_jsonl(path, records):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
