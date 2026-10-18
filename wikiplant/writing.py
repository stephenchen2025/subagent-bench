"""Stage 3: host ranking, placement, section writing, lint and style checks.

Each planted fact becomes one paragraph (default) or a short new subsection, in
the host page's voice, where an editor would plausibly have put it. Calls 3
(host ranker) and 4 (section writer) go through a `Model` (str -> str), as in
design.py. Writers rotate per unit, so no one model's fingerprint is on every
planted paragraph.
"""

import json
import math
import random
import re
from collections import Counter

from .corpus import load_pages
from .design import DesignError, parse_json
from .index import tokenize

PROMPT_VERSION = {"ranker": "ranker-v1", "writer": "writer-v1"}
SUBSECTION_SHARE = 0.30
LENGTH_TOLERANCE = 0.40

# Phrases that mark LLM prose. Extend from the style classifier's top features.
BLOCKLIST = [
    "notably", "pivotal role", "a testament to", "testament to", "played a crucial role", "played a key role",
    "rich history", "rich tapestry", "tapestry", "delve", "nestled", "boasts", "stands as", "serves as a reminder",
    "it is worth noting", "in conclusion", "furthermore", "moreover", "showcasing", "underscores", "highlighting",
    "vibrant", "renowned for", "a significant", "seamlessly", "landscape of", "realm", "ever-evolving",
]
_CITATION = re.compile(r"\[\d+\]|\[citation needed\]", re.I)

_DMY = re.compile(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}")
_MDY = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}")
TO_AMERICAN = {
    "colour": "color", "harbour": "harbor", "labour": "labor", "neighbour": "neighbor", "honour": "honor",
    "favour": "favor", "centre": "center", "theatre": "theater", "organise": "organize", "organised": "organized",
    "organisation": "organization", "recognised": "recognized", "authorised": "authorized",
    "travelled": "traveled", "programme": "program", "metre": "meter",
}
TO_BRITISH = {v: k for k, v in TO_AMERICAN.items()}

RANKER_PROMPT = """Would this fact appear on any of these Wikipedia pages, and in which section?
Fact: {fact}

Candidate pages (title, then section outline):
{outlines}

Return only JSON: {{"ranked": [{{"page_id": <id>, "section": "<section path as shown>", "why": "<short>"}}]}},
best first. Never choose the lead. Leave out pages where the fact would look out of place."""

WRITER_PROMPT = """You are adding one paragraph to the Wikipedia article "{title}", in its section "{section}".
Write it so a reader could not tell it from the paragraphs around it.

Article outline:
{outline}

Paragraph before the insertion point:
{before}

Paragraph after the insertion point:
{after}

Other paragraphs from this article, for voice and style:
{exemplars}

State this fact plainly: {fact}
Also include these minor details, as real paragraphs carry several facts: {padding}
Refer to entities exactly like this: {surface}
Length: about {words} words. Spelling: {spelling}. Dates: {dates}. Past tense, encyclopedic, no citations,
no links, no evaluative adjectives.{heading_rule}

Return only JSON: {{"text": "...", {heading_key}"claims": [{{"s": "...", "r": "...", "o": "...", "when": <year or null>}}]}}
listing EVERY factual claim the text makes, padding included.
{feedback}"""


def conventions(paragraphs):
    """The host page's spelling, date format, paragraph lengths and heading case."""
    text = " ".join(p["text"] for p in paragraphs)
    words = Counter(w.lower() for w in re.findall(r"[A-Za-z]+", text))
    brit = sum(words[w] for w in TO_AMERICAN)
    amer = sum(words[w] for w in TO_BRITISH)
    dmy, mdy = len(_DMY.findall(text)), len(_MDY.findall(text))
    lengths = [len(p["text"].split()) for p in paragraphs if p["section_path"]] or [len(p["text"].split()) for p in paragraphs]
    headings = [p["section_path"][-1] for p in paragraphs if p["section_path"]]
    title_case = sum(1 for h in headings if len(h.split()) > 1 and all(w[:1].isupper() for w in h.split() if len(w) > 3))
    multi = sum(1 for h in headings if len(h.split()) > 1)
    return {
        "spelling": "American" if amer > brit else "British",
        "dates": "month day, year" if mdy > dmy else "day month year",
        "lengths": lengths or [80],
        "heading_case": "title" if multi and title_case > multi / 2 else "sentence",
    }


def sample_length(conv, rng):
    return max(25, int(rng.choice(conv["lengths"])))


def fact_sentence(fact, entities):
    """A plain statement of one planted fact for the prompts."""
    s, o = entities[fact["s"]]["name"], entities[fact["o"]]["name"]
    when = f" in {fact['when']}" if fact.get("when") is not None else ""
    return f"{s} {fact['r'].replace('_', ' ')} {o}{when}."


def outline(page):
    return "\n".join("  " * (len(sp) - 1) + sp[-1] for sp, _ in page.sections if sp)


def rank_hosts_lexical(fact_text, pages, candidates):
    """Model-free ranking: tf-idf-ish overlap between the fact and each non-lead section. [(page_id, section_path)]."""
    q = Counter(tokenize(fact_text))
    df = Counter(t for pid in candidates for _, ps in pages[pid].sections for t in set(tokenize(" ".join(p["text"] for p in ps))))
    n = sum(len(pages[pid].sections) for pid in candidates) or 1
    scored = []
    for pid in candidates:
        for sp, ps in pages[pid].sections:
            if not sp:
                continue
            toks = Counter(tokenize(" ".join(sp) + " " + " ".join(p["text"] for p in ps)))
            s = sum(math.log(1 + n / (1 + df[t])) for t in q if toks[t])
            scored.append((s, pid, tuple(sp)))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [(pid, list(sp)) for _, pid, sp in scored]


def rank_hosts(fact_text, pages, candidates, model):
    """Call 3. Model ranking, filtered to real non-lead sections of candidate pages."""
    blocks = "\n\n".join(f"[{pid}] {pages[pid].title}\n{outline(pages[pid])}" for pid in sorted(candidates))
    reply = parse_json(model(RANKER_PROMPT.format(fact=fact_text, outlines=blocks)))
    out = []
    for r in reply.get("ranked", []):
        pid = r.get("page_id")
        if pid not in candidates or not r.get("section"):
            continue
        sp = r["section"].split("/")
        if pages[pid].section(sp) is not None:
            out.append((pid, sp))
    return out


class Ledger:
    """Density caps: at most one gold and one decoy-type unit per page."""

    def __init__(self):
        self.used = Counter()

    @staticmethod
    def _kind(role):
        return "gold" if role == "gold" else "other"

    def free(self, page_id, role):
        return self.used[(page_id, self._kind(role))] == 0

    def take(self, page_id, role):
        self.used[(page_id, self._kind(role))] += 1


def choose_placement(page, section_path, rng, role="gold"):
    """Mode, position and context for inserting into `section_path` of `page`."""
    paras = page.section(section_path)
    if paras is None or not section_path:
        raise ValueError(f"no plantable section {'/'.join(section_path)} on {page.title}")
    mode = "subsection" if rng.random() < SUBSECTION_SHARE else "paragraph"
    if mode == "subsection":
        return {"page_id": page.page_id, "section_path": list(section_path), "mode": mode, "position": 0,
                "before": paras[-1]["text"] if paras else "", "after": ""}
    position = rng.choice(["start", "middle", "end"])
    at = {"start": 0, "middle": len(paras) // 2, "end": len(paras)}[position]
    return {"page_id": page.page_id, "section_path": list(section_path), "mode": mode, "position": at,
            "before": paras[at - 1]["text"] if at > 0 else "", "after": paras[at]["text"] if at < len(paras) else ""}


def normalize_text(text, conv):
    """Match host formatting: straight quotes, en dashes in year ranges, spaced dashes, spelling."""
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = re.sub(r"\b(\d{4})\s*[-—]\s*(\d{2,4})\b", "\\1–\\2", text)
    text = re.sub(r"\s*—\s*", " – ", text)
    swap = TO_AMERICAN if conv["spelling"] == "American" else TO_BRITISH
    text = re.sub(r"\b[A-Za-z]+\b", lambda m: _swap_case(m.group(0), swap), text)
    return re.sub(r"\s+", " ", text).strip()


def _swap_case(word, table):
    rep = table.get(word.lower())
    if not rep:
        return word
    return rep.capitalize() if word[:1].isupper() else rep


def lint(text, target_words, must_mention=(), heading=None, conv=None, existing_headings=(), forbid=()):
    """Problems with a written unit, empty when it is fit to plant."""
    errs = []
    low = text.lower()
    for phrase in BLOCKLIST:
        if re.search(rf"\b{re.escape(phrase)}\b", low):
            errs.append(f"blocklisted phrase {phrase!r}")
    if _CITATION.search(text) or "[[" in text or "http" in low:
        errs.append("citations, links or URLs in planted text")
    n = len(text.split())
    if abs(n - target_words) > LENGTH_TOLERANCE * target_words:
        errs.append(f"{n} words, target {target_words} ±{int(LENGTH_TOLERANCE * 100)}%")
    for m in must_mention:
        if str(m).lower() not in low:
            errs.append(f"does not state {m!r}")
    for f in forbid:
        if re.search(rf"\b{re.escape(str(f).lower())}\b", low):
            errs.append(f"must not mention {f!r}")
    if heading is not None:
        if heading in existing_headings:
            errs.append(f"heading {heading!r} already exists on the page")
        words = heading.split()
        later = [w for w in words[1:] if w.lower() in _COMMON]
        if conv and conv["heading_case"] == "sentence" and later and all(w[:1].isupper() for w in later):
            errs.append(f"heading {heading!r} should be sentence case like the page's")
        if len(words) > 5:
            errs.append(f"heading {heading!r} is longer than the page's headings")
    return errs


_COMMON = {"history", "later", "years", "early", "closure", "contractors", "suppliers", "rebuilding", "works",
           "operations", "description", "background", "construction", "legacy", "ownership", "services"}


class WriterPool:
    """Rotates writer models per unit, deterministically, so each unit records which model wrote it."""

    def __init__(self, writers):
        if not writers:
            raise ValueError("need at least one writer")
        self.writers = sorted(writers.items())

    def pick(self, unit_id):
        h = sum(ord(c) * (i + 1) for i, c in enumerate(unit_id))
        return self.writers[h % len(self.writers)]


def write_unit(unit_id, fact_text, must_mention, page, placement, conv, pool, rng,
               padding=(), surface=None, role="gold", max_attempts=3, forbid=()):
    """Call 4 until the text passes lint. Returns (manifest entry or None, attempts)."""
    name, model = pool.pick(unit_id)
    paras = [p for _, ps in page.sections for p in ps]
    exemplars = rng.sample([p["text"] for p in paras], min(3, len(paras)))
    target = sample_length(conv, rng)
    sub = placement["mode"] == "subsection"
    existing = {sp[-1] for sp, _ in page.sections if sp}
    attempts, feedback = [], ""
    for _ in range(max_attempts):
        prompt = WRITER_PROMPT.format(
            title=page.title, section="/".join(placement["section_path"]), outline=outline(page),
            before=placement["before"] or "(start of section)", after=placement["after"] or "(end of section)",
            exemplars="\n\n".join(exemplars), fact=fact_text, padding="; ".join(padding) or "none",
            surface=json.dumps(surface or {}), words=target, spelling=conv["spelling"], dates=conv["dates"],
            heading_rule=(f"\nThis goes in a NEW subsection under that section: give it a short {conv['heading_case']}-case "
                          "heading like the page's own." if sub else ""),
            heading_key='"heading": "...", ' if sub else "", feedback=feedback)
        try:
            reply = parse_json(model(prompt))
            text = normalize_text(reply["text"], conv)
            claims = reply.get("claims") or []
            heading = reply.get("heading") if sub else None
        except (DesignError, ValueError, KeyError, TypeError) as e:
            problems = [f"unparseable reply: {e}"]
        else:
            problems = lint(text, target, must_mention, heading if sub else None, conv, existing, forbid)
            if sub and not heading:
                problems.append("a new subsection needs a heading")
            if not claims:
                problems.append("the reply lists no claims; every claim goes through the consistency check")
        attempts.append({"writer": name, "problems": problems})
        if not problems:
            entry = {
                "unit_id": unit_id, "role": role, "host_page": page.page_id,
                "section_path": placement["section_path"], "mode": placement["mode"],
                "position": placement["position"], "text": text, "claims": claims,
                "generator": {"model": name, "prompt_version": PROMPT_VERSION["writer"]},
            }
            if sub:
                entry["heading"] = heading
            return entry, attempts
        feedback = "\nYour last attempt failed these checks. Fix all of them:\n- " + "\n- ".join(problems)
    return None, attempts


def plant_fact(unit_id, fact, entities, paragraphs, candidates, pool, ledger, rng, ranker=None,
               role="gold", padding=(), surface=None, forbid=()):
    """Rank hosts, place, write. Returns (manifest entry or None, log).

    `forbid` lists strings the text must not contain, such as a decoy keeping clear of the answer.
    """
    pages = load_pages(paragraphs)
    text = fact_sentence(fact, entities)
    candidates = [c for c in candidates if c in pages and ledger.free(c, role)]
    ranked = rank_hosts(text, pages, set(candidates), ranker) if ranker else rank_hosts_lexical(text, pages, candidates)
    if not ranked:
        return None, {"error": "no free host page with a plantable section"}
    page_id, section = ranked[0]
    page = pages[page_id]
    conv = conventions([p for _, ps in page.sections for p in ps])
    placement = choose_placement(page, section, rng, role)
    must = [entities[fact["s"]]["name"]] + ([fact["when"]] if fact.get("when") is not None else [])
    entry, attempts = write_unit(unit_id, text, must, page, placement, conv, pool, rng, padding, surface, role,
                                 forbid=forbid)
    if entry:
        ledger.take(page_id, role)
    return entry, {"host": page_id, "section": section, "placement": placement["mode"], "attempts": attempts}


# --- style checks, run on every batch -------------------------------------------------------------

def _features(text):
    toks = tokenize(text)
    return Counter(toks + [a + "_" + b for a, b in zip(toks, toks[1:])])


def _nb_train(docs, labels, alpha=1.0):
    counts = {0: Counter(), 1: Counter()}
    prior = Counter(labels)
    for d, y in zip(docs, labels):
        counts[y].update(_features(d))
    vocab = set(counts[0]) | set(counts[1])
    totals = {y: sum(c.values()) + alpha * len(vocab) for y, c in counts.items()}
    return counts, prior, totals, alpha


def _nb_score(model, text):
    """log P(planted | text) - log P(real | text), up to a constant."""
    counts, prior, totals, alpha = model
    s = math.log((prior[1] + 1) / (prior[0] + 1))
    for f, n in _features(text).items():
        s += n * (math.log((counts[1][f] + alpha) / totals[1]) - math.log((counts[0][f] + alpha) / totals[0]))
    return s


def auroc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return float("nan")
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def _cv_scores(docs, folds, seed):
    """Held-out scores for [(text, label, payload)]: [(score, label, payload)]."""
    docs = list(docs)
    random.Random(seed).shuffle(docs)
    out = []
    for k in range(folds):
        train = [d for i, d in enumerate(docs) if i % folds != k]
        if len({y for _, y, _ in train}) < 2:
            continue
        m = _nb_train([t for t, _, _ in train], [y for _, y, _ in train])
        out += [(_nb_score(m, t), y, u) for i, (t, y, u) in enumerate(docs) if i % folds == k]
    return out


def style_classifier(planted, real, folds=5, seed=0, flag_auroc=0.7):
    """Cross-validated AUROC of planted-vs-real separation, overall and per writer, plus flagged units.

    planted: [{"unit_id", "text", "generator": {"model"}}]; real: [str] from the same pages.
    0.5 is indistinguishable. Each writer gets its own classifier, so one writer's tells do not
    leak onto another's units. A unit is flagged when its writer is separable (AUROC above
    `flag_auroc`) and its held-out score is above every real paragraph's.
    """
    reals = [(t, 0, None) for t in real]
    pooled = _cv_scores([(u["text"], 1, u) for u in planted] + reals, folds, seed)
    per_writer, flagged = {}, []
    for w in sorted({u["generator"]["model"] for u in planted}):
        scored = _cv_scores([(u["text"], 1, u) for u in planted if u["generator"]["model"] == w] + reals, folds, seed)
        per_writer[w] = auroc([s for s, _, _ in scored], [y for _, y, _ in scored])
        top_real = max((s for s, y, _ in scored if not y), default=math.inf)
        if per_writer[w] > flag_auroc:
            flagged += [u["unit_id"] for s, y, u in scored if y and s > top_real]
    return {"auroc": auroc([s for s, _, _ in pooled], [y for _, y, _ in pooled]),
            "per_writer": per_writer, "flagged": sorted(flagged)}


PICK_PROMPT = """One of these paragraphs from the Wikipedia article "{title}" was written recently by a language
model and inserted; the rest are original. Which one was inserted?

{options}

Answer with only the number."""


def pick_the_planted(trials, judge, k=4, seed=0):
    """Gate 8. trials: [{"title", "planted": str, "real": [str, ...]}]. The judge sees k paragraphs, one planted.

    Returns accuracy, chance (1/k) and a one-sided binomial p-value for "better than chance".
    """
    rng = random.Random(seed)
    hits = n = 0
    for t in trials:
        if len(t["real"]) < k - 1:
            continue
        opts = rng.sample(t["real"], k - 1) + [t["planted"]]
        rng.shuffle(opts)
        answer = opts.index(t["planted"]) + 1
        reply = judge(PICK_PROMPT.format(title=t["title"], options="\n\n".join(f"{i}. {o}" for i, o in enumerate(opts, 1))))
        m = re.search(r"\d+", reply)
        hits += bool(m and int(m.group(0)) == answer)
        n += 1
    p = 1 / k
    pval = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(hits, n + 1)) if n else 1.0
    return {"accuracy": hits / n if n else float("nan"), "chance": p, "n": n, "p_value": pval}
