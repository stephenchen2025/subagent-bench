"""Stage 6a: base snapshot + plant manifest = corpus.

Applying a manifest is deterministic. Variants are built from the same base:
  full  -- gold, near-misses, partial echoes and decoys
  gold  -- gold units only
  none  -- the unplanted snapshot (gate 2)
"""

import hashlib
import json

from .schemas import validate_manifest_entry

VARIANTS = {
    "full": {"gold", "near_miss", "partial_echo", "decoy"},
    "gold": {"gold"},
    "none": set(),
}


class Page:
    """One page as an ordered list of (section_path, [paragraph dicts])."""

    def __init__(self, page_id, title):
        self.page_id, self.title = page_id, title
        self.sections = []

    def section(self, path, create=False):
        for sp, paras in self.sections:
            if sp == path:
                return paras
        if not create:
            return None
        self.sections.append((list(path), []))
        return self.sections[-1][1]

    def insert_after_parent(self, path, paras):
        """Place a new subsection directly after the last section inside its parent."""
        parent = path[:-1]
        last = max((i for i, (sp, _) in enumerate(self.sections) if sp[:len(parent)] == parent), default=len(self.sections) - 1)
        self.sections.insert(last + 1, (list(path), paras))

    def render(self):
        """(text, {para_id: (start, end)}). Headings use '#' per depth, paragraphs are blank-line separated."""
        out, spans, pos = [], {}, 0

        def emit(s):
            nonlocal pos
            out.append(s)
            pos += len(s)

        emit(f"# {self.title}\n\n")
        for sp, paras in self.sections:
            if sp:
                emit(f"{'#' * (len(sp) + 1)} {sp[-1]}\n\n")
            for p in paras:
                spans[p["para_id"]] = (pos, pos + len(p["text"]))
                emit(p["text"] + "\n\n")
        return "".join(out), spans


def load_pages(paragraphs):
    pages = {}
    for p in paragraphs:
        page = pages.setdefault(p["page_id"], Page(p["page_id"], p["title"]))
        page.section(p["section_path"], create=True).append(dict(p))
    return pages


def apply_manifest(paragraphs, manifest, variant="full"):
    """Build pages with the manifest's units inserted. Returns (pages, units).

    units maps unit_id -> {role, page_id, para_id, start, end}, the span in the
    rendered page text, so gold spans stay addressable.
    """
    roles = VARIANTS[variant]
    pages = load_pages(paragraphs)
    problems = [e for u in manifest for e in validate_manifest_entry(u)]
    if problems:
        raise ValueError("invalid manifest:\n" + "\n".join(problems))
    seen = set()
    placed = {}
    # Fixed order, so the same inputs always give the same pages.
    for u in sorted((u for u in manifest if u["role"] in roles), key=lambda u: u["unit_id"]):
        if u["unit_id"] in seen:
            raise ValueError(f"duplicate unit_id {u['unit_id']}")
        seen.add(u["unit_id"])
        page = pages.get(u["host_page"])
        if page is None:
            raise ValueError(f"unit {u['unit_id']}: host page {u['host_page']} is not in the snapshot")
        path = list(u["section_path"])
        if u["mode"] == "subsection":
            path = path + [u["heading"]]
            if page.section(path) is not None:
                raise ValueError(f"unit {u['unit_id']}: subsection {'/'.join(path)} already exists")
            if page.section(path[:-1]) is None:
                raise ValueError(f"unit {u['unit_id']}: parent section {'/'.join(path[:-1])} does not exist")
            paras = []
            page.insert_after_parent(path, paras)
            at = 0
        else:
            paras = page.section(path)
            if paras is None:
                raise ValueError(f"unit {u['unit_id']}: section {'/'.join(path)} does not exist")
            at = min(u["position"], len(paras))
        paras.insert(at, {
            "para_id": f"plant:{u['unit_id']}", "page_id": page.page_id, "title": page.title,
            "section_path": path, "para_idx": at, "text": u["text"], "outlinks": [],
            "unit_id": u["unit_id"],
        })
        placed[u["unit_id"]] = (u["role"], page.page_id)
    units = {}
    for page in pages.values():
        _, spans = page.render()
        for pid_, (start, end) in spans.items():
            if pid_.startswith("plant:"):
                uid = pid_[len("plant:"):]
                units[uid] = {"role": placed[uid][0], "page_id": page.page_id, "para_id": pid_, "start": start, "end": end}
    # Real paragraphs keep their snapshot ids, even where an insertion shifted their position:
    # puzzles cite them by id, and the same id must name the same text in every variant.
    return pages, units


def corpus_id(snapshot_id, manifest, variant, chunk_cfg):
    blob = json.dumps({"snapshot": snapshot_id, "manifest": sorted(manifest, key=lambda u: u["unit_id"]),
                       "variant": variant, "chunker": chunk_cfg}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
