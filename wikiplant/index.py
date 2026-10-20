"""Stage 6b: chunk pages into passages and index them with BM25.

The same chunker runs over planted and real text. BM25 is plain Python so the
scaffold has no dependencies; swap in Pyserini or Tantivy for the full dump.
"""

import math
from array import array
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
    """Okapi BM25 over an inverted index, so a query touches only passages that share a term."""

    def __init__(self, passages, k1=1.2, b=0.75):
        self.passages, self.k1, self.b = passages, k1, b
        self.postings = {}          # term -> (array of passage indices, array of term frequencies)
        self.len = array("I")
        for i, p in enumerate(passages):
            c = Counter(tokenize(p["title"] + " " + " ".join(p["section_path"]) + " " + p["text"]))
            self.len.append(sum(c.values()))
            for t, f in c.items():
                post = self.postings.get(t)
                if post is None:
                    post = self.postings[t] = (array("I"), array("H"))
                post[0].append(i)
                post[1].append(min(f, 65535))
        self.avg = (sum(self.len) / len(self.len)) if self.len else 0.0
        n = len(passages)
        self.idf = {t: math.log(1 + (n - len(ps[0]) + 0.5) / (len(ps[0]) + 0.5)) for t, ps in self.postings.items()}

    def scores(self, query):
        acc = {}
        for t in set(tokenize(query)):
            idf = self.idf.get(t)
            if idf is None:
                continue
            docs, tfs = self.postings[t]
            for i, f in zip(docs, tfs):
                norm = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                acc[i] = acc.get(i, 0.0) + idf * f * (self.k1 + 1) / (f + norm)
        return acc

    def search(self, query, k=10):
        ranked = sorted(self.scores(query).items(), key=lambda x: (-x[1], x[0]))[:k]
        return [(self.passages[i], s) for i, s in ranked]

    def rank_of(self, query, passage_ids):
        """1-based best rank of any passage in `passage_ids` for `query`, or None (gate 7)."""
        ids = set(passage_ids)
        for rank, (i, _) in enumerate(sorted(self.scores(query).items(), key=lambda x: (-x[1], x[0])), 1):
            if self.passages[i]["passage_id"] in ids:
                return rank
        return None
