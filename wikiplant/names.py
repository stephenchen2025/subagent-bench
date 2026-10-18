"""Invented names: generated under era/region constraints, checked for collisions, capped for repeats."""

import difflib
import random
import re
from collections import Counter

FUZZY_RATIO = 0.88
_PHRASE = re.compile(r"\b[A-Z][\w'’-]+(?:\s+(?:and|of|&|the|de|[A-Z][\w'’-]+))*(?:\s+[A-Z][\w'’-]+)*")

# Small starting pools; add eras/regions as the domains grow. Each key is (region, era).
POOLS = {
    ("north england", "1800s"): {
        "surnames": ["Harland", "Pell", "Cotterill", "Ashworth", "Dobson", "Rawsthorne", "Threlfall", "Kershaw",
                     "Holroyd", "Entwistle", "Ormerod", "Tattersall", "Haworth", "Greenhalgh", "Baxendale"],
        "places": ["Dunmere", "Wharfedale", "Calder", "Ribblesdale", "Marlow", "Hesketh", "Stainmoor", "Ormskirk"],
        "firm_forms": ["{a} and {b}", "{a} & Sons", "{a} Brothers", "{a}, {b} and Company"],
        "society_forms": ["{p} Provident Union", "{p} Mechanics' Institute", "{p} Natural History Society",
                          "{p} Literary and Philosophical Society"],
        "company_forms": ["{p} Iron Company", "{p} Coal and Navigation Company", "{p} Mill Company"],
    },
}


def normalize(name):
    return re.sub(r"[^a-z0-9 ]", "", name.lower().replace("&", "and")).strip()


def generate(kind, region="north england", era="1800s", rng=None):
    """One candidate name of `kind` (firm, society, company, person) for the region and era."""
    rng = rng or random.Random()
    pool = POOLS[(region, era)]
    if kind == "firm":
        a, b = rng.sample(pool["surnames"], 2)
        return rng.choice(pool["firm_forms"]).format(a=a, b=b)
    if kind == "society":
        return rng.choice(pool["society_forms"]).format(p=rng.choice(pool["places"]))
    if kind == "company":
        return rng.choice(pool["company_forms"]).format(p=rng.choice(pool["places"]))
    if kind == "person":
        return f"{rng.choice(['John', 'William', 'Thomas', 'James', 'Henry', 'George', 'Samuel'])} {rng.choice(pool['surnames'])}"
    raise ValueError(f"unknown name kind {kind!r}")


class CollisionIndex:
    """Exact and fuzzy match of a candidate against every title, redirect and capitalised phrase in the corpus."""

    def __init__(self, paragraphs, redirects=()):
        self.titles = {normalize(t) for t in {p["title"] for p in paragraphs} | set(redirects)}
        self.blob = " ".join(normalize(p["text"]) for p in paragraphs)
        phrases = {normalize(m.group(0)) for p in paragraphs for m in _PHRASE.finditer(p["text"])}
        self.phrases = sorted(x for x in phrases if len(x) > 3)

    def collisions(self, name):
        n = normalize(name)
        if not n:
            return ["empty"]
        out = []
        if n in self.titles:
            out.append("title")
        if f" {n} " in f" {self.blob} ":
            out.append("text")
        for other in list(self.titles) + self.phrases:
            if other != n and abs(len(other) - len(n)) <= 4 and difflib.SequenceMatcher(None, n, other).ratio() >= FUZZY_RATIO:
                out.append(f"fuzzy:{other}")
                break
        return out


class Registry:
    """Caps how often a name, or a name's parts, repeats across the dataset; LLMs reuse a small set of names."""

    def __init__(self, max_name=1, max_part=3):
        self.names, self.parts = Counter(), Counter()
        self.max_name, self.max_part = max_name, max_part

    @staticmethod
    def _parts(name):
        stop = {"and", "of", "the", "company", "sons", "brothers", "society", "union", "institute"}
        return [w for w in normalize(name).split() if w not in stop and len(w) > 2]

    def problems(self, name):
        out = []
        if self.names[normalize(name)] >= self.max_name:
            out.append(f"name {name!r} already used")
        out += [f"name part {w!r} used {self.parts[w]} times" for w in self._parts(name) if self.parts[w] >= self.max_part]
        return out

    def add(self, name):
        self.names[normalize(name)] += 1
        for w in self._parts(name):
            self.parts[w] += 1
