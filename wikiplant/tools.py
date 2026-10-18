"""The agent's view of the corpus: search, open, find_in_page. Every call is logged.

The log of passage ids each call returns, joined with the unit spans, shows
whether gold passages were surfaced, opened and read.
"""

from .corpus import apply_manifest, corpus_id
from .index import BM25, CHUNK_CFG, chunk_page

SNIPPET_WORDS = 40
PAGE_WORDS = 400


def _snippet(text, query_terms):
    words = text.split()
    best = 0
    for i, w in enumerate(words):
        if w.lower().strip(".,;:()") in query_terms:
            best = max(0, i - 8)
            break
    return " ".join(words[best:best + SNIPPET_WORDS])


class Corpus:
    def __init__(self, paragraphs, manifest=(), variant="full", snapshot_id="unversioned"):
        self.manifest = list(manifest)
        self.variant = variant
        self.pages, self.units = apply_manifest(paragraphs, self.manifest, variant)
        self.passages = [p for page in self.pages.values() for p in chunk_page(page)]
        self.bm25 = BM25(self.passages)
        self.by_title = {pg.title.lower(): pg for pg in self.pages.values()}
        self.corpus_id = corpus_id(snapshot_id, self.manifest, variant, CHUNK_CFG)
        self.log = []

    def gold_passages(self):
        gold = {u for u, v in self.units.items() if v["role"] == "gold"}
        return [p["passage_id"] for p in self.passages if gold.intersection(p["unit_ids"])]

    def search(self, query, k=5):
        hits = self.bm25.search(query, k)
        terms = set(query.lower().split())
        self.log.append({"tool": "search", "query": query, "passage_ids": [p["passage_id"] for p, _ in hits]})
        return [{"title": p["title"], "section_path": p["section_path"], "passage_id": p["passage_id"],
                 "snippet": _snippet(p["text"], terms)} for p, _ in hits]

    def open(self, title, section=None, offset=0):
        """Outline of the page, plus up to PAGE_WORDS words of text from `offset` (a word index)."""
        page = self.by_title.get(title.lower())
        if page is None:
            return {"error": f"no page titled {title!r}"}
        outline = ["/".join(sp) for sp, _ in page.sections]
        sections = [(sp, ps) for sp, ps in page.sections if section is None or "/".join(sp) == section]
        if section is not None and not sections:
            return {"error": f"no section {section!r} on {page.title}", "outline": outline}
        words = " ".join(p["text"] for _, ps in sections for p in ps).split()
        chunk = words[offset:offset + PAGE_WORDS]
        seen = [p["passage_id"] for p in self.passages
                if p["page_id"] == page.page_id and (section is None or "/".join(p["section_path"]) == section)]
        self.log.append({"tool": "open", "title": page.title, "section": section, "passage_ids": seen})
        nxt = offset + PAGE_WORDS
        return {"title": page.title, "outline": outline, "text": " ".join(chunk),
                "next_offset": nxt if nxt < len(words) else None}

    def find_in_page(self, title, text):
        page = self.by_title.get(title.lower())
        if page is None:
            return {"error": f"no page titled {title!r}"}
        needle = text.lower()
        hits = [{"section_path": sp, "paragraph": p["text"]} for sp, ps in page.sections for p in ps if needle in p["text"].lower()]
        self.log.append({"tool": "find_in_page", "title": page.title, "passage_ids": [
            p["passage_id"] for p in self.passages if p["page_id"] == page.page_id
            and any(h["paragraph"] in p["text"] for h in hits)]})
        return hits

    def surfaced(self, kind=("search", "open", "find_in_page")):
        """Gold units whose passage some logged call returned."""
        ids = {i for e in self.log if e["tool"] in kind for i in e["passage_ids"]}
        return sorted(u for p in self.passages if p["passage_id"] in ids for u in p["unit_ids"]
                      if self.units[u]["role"] == "gold")
