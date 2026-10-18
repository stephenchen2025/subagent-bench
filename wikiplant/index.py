"""Stage 6b: chunk pages into passages and index them with BM25.

The same chunker runs over planted and real text. BM25 is plain Python so the
scaffold has no dependencies; swap in Pyserini or Tantivy for the full dump.
"""

import math
import re
from collections import Counter

CHUNK_CFG = {"min_words": 100, "max_words": 200}
_TOKEN = re.compile(r"\w+")


def tokenize(text):
    return _TOKEN.findall(text.lower())


def chunk_page(page, cfg=CHUNK_CFG):
    """Passages of ~min..max words, never crossing a section boundary.

    A paragraph is never split; one longer than max_words is a passage alone.
    """
    passages = []
    for sp, paras in page.sections:
        group, words = [], 0

        def close():
            nonlocal group, words
            if group:
                passages.append({
                    "passage_id": f"{page.page_id}#{len(passages)}",
                    "page_id": page.page_id, "title": page.title, "section_path": list(sp),
                    "text": "\n\n".join(p["text"] for p in group),
                    "para_ids": [p["para_id"] for p in group],
                    "unit_ids": [p["unit_id"] for p in group if "unit_id" in p],
                })
            group, words = [], 0

        for p in paras:
            n = len(p["text"].split())
            if group and words + n > cfg["max_words"]:
                close()
            group.append(p)
            words += n
            if words >= cfg["min_words"]:
                close()
        close()
    return passages


class BM25:
    def __init__(self, passages, k1=1.2, b=0.75):
        self.passages, self.k1, self.b = passages, k1, b
        self.tf = [Counter(tokenize(p["title"] + " " + " ".join(p["section_path"]) + " " + p["text"])) for p in passages]
        self.len = [sum(c.values()) for c in self.tf]
        self.avg = (sum(self.len) / len(self.len)) if self.len else 0.0
        df = Counter(t for c in self.tf for t in c)
        n = len(passages)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def search(self, query, k=10):
        q = set(tokenize(query))
        scored = []
        for i, c in enumerate(self.tf):
            s = 0.0
            for t in q:
                f = c.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            if s > 0:
                scored.append((s, i))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [(self.passages[i], s) for s, i in scored[:k]]

    def rank_of(self, query, passage_ids):
        """1-based best rank of any passage in `passage_ids` for `query`, or None (gate 7)."""
        ids = set(passage_ids)
        for rank, (p, _) in enumerate(self.search(query, k=len(self.passages)), 1):
            if p["passage_id"] in ids:
                return rank
        return None
