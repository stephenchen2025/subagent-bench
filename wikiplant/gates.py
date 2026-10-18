"""Stage 5: validation gates.

A puzzle ships only if it passes every gate. Gates run cheapest first and stop
at the first failure; the failure's reason and the stage to return to (2 for the
fact graph, 3 for the prose) are recorded on the puzzle. `pass_rates` summarises
a batch, so it is clear where the generator is weak.

Model-backed gates take `Model` callables (str -> str), as in design.py.
"""

import json
import re
from dataclasses import dataclass, field

from .corpus import load_pages
from .design import DesignError, parse_json
from .names import CollisionIndex
from .tools import Corpus
from .writing import pick_the_planted

PROMPT_VERSION = {"closed_book": "cb-v1", "agent": "agent-v1", "oracle": "oracle-v1", "consistency": "judge-v1"}

# Gate order: cheap, deterministic gates first.
ORDER = ["name_collision", "lexical_shortcut", "closed_book", "oracle", "oracle_distractors",
         "consistency", "base_corpus", "style", "human_review"]
RETURN_TO = {"name_collision": 2, "lexical_shortcut": 2, "closed_book": 2, "base_corpus": 2,
             "oracle": 3, "oracle_distractors": 3, "consistency": 3, "style": 3, "human_review": 2}
# Gate 7 band: the BM25 rank of the final-hop gold passage, with the question as the query.
BM25_BAND = {"easy": (2, 10), "medium": (10, 100), "hard": (100, None)}

CLOSED_BOOK_PROMPT = """Answer from memory; you have no tools. If you are not sure, give your best guess.
Question: {question}
Reply with only the short answer."""

ORACLE_PROMPT = """Answer the question using only these passages.

{passages}

Question: {question}
Return only JSON: {{"answer": "<short answer>", "other_defensible": ["<any other answer these passages could
also support>"]}}"""

AGENT_PROMPT = """You are answering a question by searching a Wikipedia snapshot. You have these tools:
  {{"action": "search", "query": "...", "k": 5}}
  {{"action": "open", "title": "...", "section": "<section path or null>"}}
  {{"action": "answer", "answer": "<short answer, or UNKNOWN>"}}
Reply with exactly one JSON action per turn. You have {steps} steps.

Question: {question}

{transcript}"""

CONSISTENCY_PROMPT = """Check these claims from a paragraph inserted into a Wikipedia article against the real
paragraphs below. A conflict is a claim that contradicts a real paragraph, or a date that cannot be right
given them (for example, a firm supplying a railway after it closed).

Claims:
{claims}

Real paragraphs:
{paragraphs}

Return only JSON: {{"conflicts": [{{"claim": "...", "para_id": "...", "why": "..."}}]}}. An empty list if none."""


def _norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s).lower())
    return " ".join(w for w in s.split() if w not in {"the", "a", "an", "in", "of", "year"})


def answer_matches(candidate, gold, aliases=()):
    """True if `candidate` gives the gold answer or an alias, as a whole-token match."""
    cand = f" {_norm(candidate)} "
    return any(_norm(g) and f" {_norm(g)} " in cand for g in [gold, *aliases])


@dataclass
class Context:
    """Everything the gates need besides the puzzle."""
    paragraphs: list
    manifest: list
    snapshot_id: str = "unversioned"
    closed_book_models: dict = field(default_factory=dict)   # name -> Model
    agent: object = None
    oracle: object = None
    judge: object = None
    style_judge: object = None
    samples: int = 3
    oracle_threshold: float = 0.9
    agent_steps: int = 12
    redirects: tuple = ()
    _cache: dict = field(default_factory=dict)

    def corpus(self, variant):
        if variant not in self._cache:
            self._cache[variant] = Corpus(self.paragraphs, self.manifest, variant, self.snapshot_id)
        return self._cache[variant]

    def collision_index(self):
        if "collision" not in self._cache:
            self._cache["collision"] = CollisionIndex(self.paragraphs, self.redirects)
        return self._cache["collision"]

    @property
    def para_by_id(self):
        if "paras" not in self._cache:
            self._cache["paras"] = {p["para_id"]: p for p in self.paragraphs}
        return self._cache["paras"]


def _units(puzzle, ctx):
    """(gold units on the path in hop order, other units tied to this puzzle)."""
    by_id = {u["unit_id"]: u for u in ctx.manifest}
    facts = {f["fid"]: f for f in puzzle["facts"]}
    gold = [by_id[facts[x]["unit_id"]] for x in puzzle["path"] if facts[x].get("planted") and facts[x].get("unit_id") in by_id]
    others = [u for u in ctx.manifest if u.get("puzzle") == puzzle["pid"] and u["role"] != "gold"]
    return gold, others


def _real_hops(puzzle, ctx):
    facts = {f["fid"]: f for f in puzzle["facts"]}
    return [ctx.para_by_id[facts[x]["para_id"]] for x in puzzle["path"]
            if not facts[x].get("planted") and facts[x]["para_id"] in ctx.para_by_id]


def _result(ok, reason="", **detail):
    return {"state": "pass" if ok else "fail", "reason": reason, **detail}


# --- deterministic gates ----------------------------------------------------------------------------

def gate_name_collision(puzzle, ctx):
    """Gate 6: no invented name matches a title, redirect or corpus text, exactly or fuzzily."""
    idx = ctx.collision_index()
    names = [e["name"] for e in puzzle["entities"] if e.get("invented")]
    names += [u["fact"]["s"] for u in _units(puzzle, ctx)[1] if u.get("fact")]
    hits = {n: idx.collisions(n) for n in names}
    hits = {n: h for n, h in hits.items() if h}
    return _result(not hits, "; ".join(f"{n}: {', '.join(h)}" for n, h in hits.items()), names=len(names))


def gate_lexical_shortcut(puzzle, ctx):
    """Gate 7: the final-hop gold passage is outside the tier's top k, and the answer is not in the question."""
    if answer_matches(puzzle["question"], puzzle["answer"], puzzle.get("aliases", [])):
        return _result(False, "the question contains the answer")
    gold, _ = _units(puzzle, ctx)
    if not gold:
        return _result(False, "no gold unit for the final hop in the manifest")
    corpus = ctx.corpus("full")
    final = [p["passage_id"] for p in corpus.passages if gold[-1]["unit_id"] in p["unit_ids"]]
    rank = corpus.bm25.rank_of(puzzle["question"], final)
    lo, hi = BM25_BAND[puzzle.get("tier", "medium")]
    if rank is None:
        ok = hi is None                      # not retrieved at all only counts for the open-ended hard band
    else:
        ok = rank >= lo and (hi is None or rank <= hi)
    return _result(ok, "" if ok else f"final-hop gold BM25 rank {rank}, tier band {lo}-{hi or 'inf'}", bm25_rank=rank)


# --- model gates ------------------------------------------------------------------------------------

def gate_closed_book(puzzle, ctx):
    """Gate 1: strong models with no tools never produce the gold answer."""
    if not ctx.closed_book_models:
        return {"state": "pending", "reason": "no closed-book models configured"}
    hits = []
    for name, model in sorted(ctx.closed_book_models.items()):
        for i in range(ctx.samples):
            reply = model(CLOSED_BOOK_PROMPT.format(question=puzzle["question"]))
            if answer_matches(reply, puzzle["answer"], puzzle.get("aliases", [])):
                hits.append(f"{name}#{i}")
    return _result(not hits, f"answered from memory by {', '.join(hits)}" if hits else "")


def _ask_oracle(puzzle, ctx, passages):
    block = "\n\n".join(f"[{i}] {t}" for i, t in enumerate(passages, 1))
    out = []
    for _ in range(ctx.samples):
        try:
            out.append(parse_json(ctx.oracle(ORACLE_PROMPT.format(passages=block, question=puzzle["question"]))))
        except (DesignError, ValueError):
            out.append({"answer": "", "other_defensible": []})
    return out


def gate_oracle(puzzle, ctx):
    """Gate 3: given only the gold and real-hop paragraphs, the model answers correctly in nearly every sample."""
    if ctx.oracle is None:
        return {"state": "pending", "reason": "no oracle model configured"}
    gold, _ = _units(puzzle, ctx)
    passages = [p["text"] for p in _real_hops(puzzle, ctx)] + [u["text"] for u in gold]
    replies = _ask_oracle(puzzle, ctx, passages)
    acc = sum(answer_matches(r.get("answer", ""), puzzle["answer"], puzzle.get("aliases", [])) for r in replies) / len(replies)
    ok = acc >= ctx.oracle_threshold
    return _result(ok, "" if ok else f"oracle accuracy {acc:.2f} < {ctx.oracle_threshold}", accuracy=acc)


def gate_oracle_distractors(puzzle, ctx):
    """Gate 4: with near-misses and same-page decoys added, still correct and no second defensible answer."""
    if ctx.oracle is None:
        return {"state": "pending", "reason": "no oracle model configured"}
    gold, others = _units(puzzle, ctx)
    gold_pages = {u["host_page"] for u in gold}
    same_page = [u for u in ctx.manifest if u["role"] != "gold" and u["host_page"] in gold_pages]
    distractors = {u["unit_id"]: u["text"] for u in others + same_page}
    passages = [p["text"] for p in _real_hops(puzzle, ctx)] + [u["text"] for u in gold] + [distractors[k] for k in sorted(distractors)]
    replies = _ask_oracle(puzzle, ctx, passages)
    gold_ans = (puzzle["answer"], puzzle.get("aliases", []))
    acc = sum(answer_matches(r.get("answer", ""), *gold_ans) for r in replies) / len(replies)
    second = sorted({str(a) for r in replies for a in r.get("other_defensible") or []
                     if str(a).strip() and not answer_matches(a, *gold_ans) and str(a).upper() != "NONE"})
    ok = acc >= ctx.oracle_threshold and not second
    reason = "" if ok else (f"accuracy {acc:.2f}" if acc < ctx.oracle_threshold else f"second defensible answer: {second}")
    return _result(ok, reason, accuracy=acc, distractors=len(distractors))


def gate_consistency(puzzle, ctx, k=5):
    """Gate 5: every claim of every unit for this puzzle, padding included, against real paragraphs."""
    if ctx.judge is None:
        return {"state": "pending", "reason": "no consistency judge configured"}
    gold, others = _units(puzzle, ctx)
    base = ctx.corpus("none")
    pages = load_pages(ctx.paragraphs)
    conflicts = []
    for u in gold + others:
        claims = u.get("claims") or []
        if not claims:
            conflicts.append({"unit": u["unit_id"], "why": "no claims recorded"})
            continue
        real = {p["para_id"]: p["text"] for _, ps in pages[u["host_page"]].sections for p in ps}
        for c in claims:
            for hit, _ in base.bm25.search(f"{c.get('s', '')} {c.get('o', '')}", k):
                for pid in hit["para_ids"]:
                    real.setdefault(pid, ctx.para_by_id[pid]["text"])
        prompt = CONSISTENCY_PROMPT.format(claims=json.dumps(claims, indent=1),
                                           paragraphs="\n\n".join(f"[{pid}] {t}" for pid, t in sorted(real.items())))
        try:
            found = parse_json(ctx.judge(prompt)).get("conflicts", [])
        except (DesignError, ValueError):
            found = [{"why": "judge reply unparseable"}]
        conflicts += [{"unit": u["unit_id"], **c} for c in found]
    return _result(not conflicts, "; ".join(f"{c['unit']}: {c.get('why', '')}" for c in conflicts), conflicts=conflicts)


def run_agent(model, corpus, question, steps=12):
    """A minimal search agent over a corpus. Returns (answer or None, transcript)."""
    transcript = []
    for _ in range(steps):
        reply = model(AGENT_PROMPT.format(steps=steps, question=question, transcript="\n".join(transcript)))
        try:
            act = parse_json(reply)
        except (DesignError, ValueError):
            transcript.append("ERROR: reply with one JSON action")
            continue
        a = act.get("action")
        if a == "answer":
            ans = str(act.get("answer", ""))
            return (None if ans.upper() == "UNKNOWN" else ans), transcript
        if a == "search":
            obs = corpus.search(str(act.get("query", "")), int(act.get("k", 5)))
        elif a == "open":
            obs = corpus.open(str(act.get("title", "")), act.get("section"))
        else:
            obs = {"error": f"unknown action {a!r}"}
        transcript.append(f"ACTION {json.dumps(act)}\nRESULT {json.dumps(obs)[:4000]}")
    return None, transcript


def gate_base_corpus(puzzle, ctx):
    """Gate 2: an agent searching the unplanted snapshot cannot reach the answer."""
    if ctx.agent is None:
        return {"state": "pending", "reason": "no agent model configured"}
    hits = 0
    for _ in range(ctx.samples):
        corpus = ctx.corpus("none")
        corpus.log = []
        ans, _ = run_agent(ctx.agent, corpus, puzzle["question"], ctx.agent_steps)
        hits += bool(ans and answer_matches(ans, puzzle["answer"], puzzle.get("aliases", [])))
    return _result(hits == 0, f"base-corpus agent answered {hits}/{ctx.samples}" if hits else "")


def gate_style(puzzle, ctx, k=4, repeats=5, alpha=0.05):
    """Gate 8: a judge picking the planted paragraph among k from each host page does no better than chance."""
    if ctx.style_judge is None:
        return {"state": "pending", "reason": "no style judge configured"}
    gold, others = _units(puzzle, ctx)
    pages = load_pages(ctx.paragraphs)
    trials = []
    for u in gold + others:
        real = [p["text"] for _, ps in pages[u["host_page"]].sections for p in ps]
        trials += [{"title": pages[u["host_page"]].title, "planted": u["text"], "real": real}] * repeats
    r = pick_the_planted(trials, ctx.style_judge, k=k)
    ok = r["n"] == 0 or r["p_value"] >= alpha
    return _result(ok, "" if ok else f"judge picked the planted paragraph {r['accuracy']:.2f} vs chance {r['chance']:.2f}", **r)


def gate_human_review(puzzle, ctx):
    """Gate 9: a person marks the puzzle natural, answerable and unique (see `record_review`)."""
    review = puzzle.get("review")
    if not review:
        return {"state": "pending", "reason": "awaiting human review"}
    ok = all(review.get(k) for k in ("natural", "answerable", "unique"))
    return _result(ok, "" if ok else f"reviewer: {review.get('note', 'rejected')}")


GATES_FN = {
    "name_collision": gate_name_collision, "lexical_shortcut": gate_lexical_shortcut,
    "closed_book": gate_closed_book, "oracle": gate_oracle, "oracle_distractors": gate_oracle_distractors,
    "consistency": gate_consistency, "base_corpus": gate_base_corpus, "style": gate_style,
    "human_review": gate_human_review,
}


def run_gates(puzzle, ctx, only=None, stop_on_fail=True, results=None):
    """Run gates in ORDER on `puzzle` (updated in place). Returns the per-gate results.

    A failure records `puzzle["return_to"]` (stage 2 or 3) and `puzzle["gate_reason"]`.
    Pending gates (no model configured, or awaiting review) do not stop the run. Pass a dict as
    `results` to keep the gates already run if a later one raises (a spent quota, say).
    """
    results = {} if results is None else results
    puzzle.setdefault("gates", {})
    for g in ORDER:
        if only and g not in only:
            continue
        r = GATES_FN[g](puzzle, ctx)
        results[g] = r
        puzzle["gates"][g] = r["state"]
        if r["state"] == "fail":
            puzzle["return_to"], puzzle["gate_reason"] = RETURN_TO[g], f"{g}: {r['reason']}"
            if stop_on_fail:
                break
    return results


def shippable(puzzle):
    return all(puzzle.get("gates", {}).get(g) == "pass" for g in ORDER)


def record_review(puzzle, natural, answerable, unique, reviewer, note=""):
    puzzle["review"] = {"natural": natural, "answerable": answerable, "unique": unique, "reviewer": reviewer, "note": note}
    return puzzle


def pass_rates(puzzles):
    """Per gate: passed / attempted, ignoring pending, so weak spots in the generator show."""
    out = {}
    for g in ORDER:
        states = [p.get("gates", {}).get(g) for p in puzzles]
        tried = [s for s in states if s in ("pass", "fail")]
        out[g] = {"pass": tried.count("pass"), "tried": len(tried),
                  "rate": round(tried.count("pass") / len(tried), 3) if tried else None}
    return out
