"""Stage 2: puzzle design, fact graph first.

Calls 1 (cluster brief) and 2 (fact-graph designer) go through a `Model`, any
callable str -> str, so tests use a stub and runs plug in a real client. The
designer's JSON is checked against every rule in `check_design` before any prose
is written, and failures are fed back to it with their reasons.
"""

import json
import re

from . import clusters as cl
from .schemas import validate_puzzle

PROMPT_VERSION = {"brief": "brief-v1", "designer": "designer-v1"}

TIERS = {
    "easy": {"hops": (2, 2), "planted": (1, 1), "bridges": "name", "near_misses": 0,
             "templates": ("chain",), "max_depth": "early"},
    "medium": {"hops": (3, 3), "planted": (2, 2), "bridges": "mixed", "near_misses": 1,
               "templates": ("chain", "comparison"), "max_depth": "middle"},
    "hard": {"hops": (4, 5), "planted": (3, 5), "bridges": "description", "near_misses": 99,
             "templates": ("intersection", "aggregation"), "max_depth": "late"},
}

BRIEF_PROMPT = """You are preparing a cluster brief. From the page leads and infoboxes below, list the real
entities with a type (person, place, organization, event, work), dates, places, and the relations that
the text states. Use only what the text says. Return JSON: {{"entities": [{{"name","type","dates","places"}}],
"relations": [{{"s","r","o","para_id"}}]}}.

{pages}
"""

DESIGNER_PROMPT = """Design a multi-hop question over a Wikipedia cluster using invented facts.
Return only JSON: {{"template","entities","facts","path","question","answer","aliases"}}.

Rules:
- Entities: {{"eid","name","type","invented","from","to"}}; from/to are the years the entity existed, when known.
- Facts: {{"fid","s","r","o","planted","when"}}. A real fact cites "para_id" from the brief. A planted fact
  gives "host_page", one of {hosts}.
- A planted fact's SUBJECT is an invented entity. Real entities appear only as the object. Say nothing false
  about a real entity.
- The path lists fact ids in hop order. It starts at a real entity the agent can search for and ends at a
  planted fact. Each hop lives on a different host page. Consecutive facts share an entity.
- Hops: {hops}. Planted hops: {planted}. Template: {template}. Bridge references: {bridges}.
- Planted facts must fit the real timeline and every entity's from/to years.
- The answer is short and canonical (a year, number, place or invented name). Give accepted aliases.
- The question never contains the answer or any invented name; it describes bridge entities instead.
- Invented names: {naming}. Do not reuse these: {used}.

Cluster brief:
{brief}
{feedback}"""


class DesignError(Exception):
    pass


def parse_json(text):
    """The first JSON object in a model reply, tolerating code fences and chatter."""
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    if start < 0:
        raise DesignError("no JSON object in the reply")
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def build_brief(cluster, paragraphs, pages, types=None, max_lead=400):
    """Deterministic cluster brief: pages with type, years, lead and section outline, plus link relations."""
    members = set(cluster["pages"])
    by_page = {}
    for p in paragraphs:
        if p["page_id"] in members:
            by_page.setdefault(p["page_id"], []).append(p)
    titles = {i: pages[i]["title"] if i in pages else str(i) for i in members}
    out_pages, relations = [], []
    ids_by_title = {cl.norm_title(t): i for i, t in titles.items()}
    for i in sorted(members):
        ps = by_page.get(i, [])
        lead = next((p["text"] for p in ps if not p["section_path"]), ps[0]["text"] if ps else "")
        years = sorted({int(y) for p in ps for y in cl._YEAR.findall(p["text"])})
        sections = sorted({"/".join(p["section_path"]) for p in ps if p["section_path"]})
        out_pages.append({
            "page_id": i, "title": titles[i], "type": (types or {}).get(i, "unknown"),
            "infobox": (pages.get(i) or {}).get("infobox", {}), "lead": lead[:max_lead],
            "years": [years[0], years[-1]] if years else [], "sections": sections,
            "words": sum(len(p["text"].split()) for p in ps),
        })
        for p in ps:
            for link in p["outlinks"]:
                j = ids_by_title.get(cl.norm_title(link))
                if j is not None and j != i:
                    relations.append({"s": titles[i], "r": "links_to", "o": titles[j], "para_id": p["para_id"]})
    return {"cluster_seed": cluster["seed"], "pages": out_pages, "relations": relations}


def refine_brief(brief, model, max_pages=40):
    """Call 1: ask the model for typed entities and stated relations; merge them into the brief."""
    text = "\n\n".join(f"[{p['title']}] {p['lead']}" for p in brief["pages"][:max_pages])
    reply = parse_json(model(BRIEF_PROMPT.format(pages=text)))
    merged = dict(brief)
    merged["entities"] = reply.get("entities", [])
    merged["relations"] = brief["relations"] + [r for r in reply.get("relations", []) if {"s", "r", "o"} <= set(r)]
    merged["prompt_version"] = PROMPT_VERSION["brief"]
    return merged


def _para_page(para_id):
    return int(str(para_id).split(":", 1)[0])


def _band(n, lo_hi):
    return lo_hi[0] <= n <= lo_hi[1]


def check_design(d, brief, tier, hosts, collision=None, registry=None, used_names=()):
    """Every rule a fact graph must meet before prose is written. Returns problems, empty when it passes."""
    errs = validate_puzzle({**{"pid": d.get("pid", "draft")}, **d})
    if errs:
        return errs
    knobs = TIERS[tier]
    cluster_pages = {p["page_id"] for p in brief["pages"]}
    ents = {e["eid"]: e for e in d["entities"]}
    facts = {f["fid"]: f for f in d["facts"]}
    path = [facts[x] for x in d["path"]]

    if d["template"] not in knobs["templates"]:
        errs.append(f"template {d['template']} not allowed in tier {tier} ({knobs['templates']})")
    if not _band(len(path), knobs["hops"]):
        errs.append(f"{len(path)} hops, tier {tier} needs {knobs['hops']}")
    planted = [f for f in path if f.get("planted")]
    if not _band(len(planted), knobs["planted"]):
        errs.append(f"{len(planted)} planted hops, tier {tier} needs {knobs['planted']}")
    if not any(not ents[f[e]].get("invented") for f in path[:1] for e in ("s", "o")):
        errs.append("the path must start at a real entity the agent can search for")
    if not path[-1].get("planted"):
        errs.append("the path must end at a planted fact, or the answer is not only in planted text")
    if len(planted) == len(path) and tier == "easy":
        errs.append("mix real and planted hops")

    hop_pages = []
    for f in path:
        page = f["host_page"] if f.get("planted") else _para_page(f["para_id"])
        hop_pages.append(page)
        if f.get("planted") and f["host_page"] not in hosts:
            errs.append(f"fact {f['fid']}: host page {f['host_page']} is not a host-eligible page")
        if page not in cluster_pages:
            errs.append(f"fact {f['fid']}: page {page} is outside the cluster")
        if f.get("planted") and not ents[f["s"]].get("invented"):
            errs.append(f"fact {f['fid']}: a planted fact's subject must be an invented entity")
        if not f.get("planted") and (ents[f["s"]].get("invented") or ents[f["o"]].get("invented")):
            errs.append(f"fact {f['fid']}: a real fact cannot involve an invented entity")
    if len(set(hop_pages)) != len(hop_pages):
        errs.append("each hop must live on a different host page")
    for a, b in zip(path, path[1:]):
        if not {a["s"], a["o"]} & {b["s"], b["o"]}:
            errs.append(f"facts {a['fid']} and {b['fid']} share no entity, so the path is not connected")

    for f in path:
        when = f.get("when")
        if when is None:
            continue
        for e in (ents[f["s"]], ents[f["o"]]):
            lo, hi = e.get("from"), e.get("to")
            if (lo is not None and when < lo) or (hi is not None and when > hi):
                errs.append(f"fact {f['fid']}: year {when} is outside {e['name']}'s {lo}-{hi}")
    if d["template"] == "aggregation" and sum(1 for f in path if f.get("when") is not None) < 2:
        errs.append("an aggregation needs at least two dated facts")

    q, ans = d["question"].lower(), str(d["answer"]).lower().strip()
    if re.search(rf"\b{re.escape(ans)}\b", q):
        errs.append("the question contains the answer")
    for e in d["entities"]:
        if e.get("invented") and e["name"].lower() in q:
            errs.append(f"the question names invented entity {e['name']}; describe it instead")
    if knobs["bridges"] == "description":
        bridge = {ents[f[x]]["name"].lower() for f in path[1:-1] for x in ("s", "o") if not ents[f[x]].get("invented")}
        for name in bridge:
            if name in q:
                errs.append(f"tier {tier} describes bridge entity {name!r} instead of naming it")

    for e in d["entities"]:
        if not e.get("invented"):
            continue
        if collision is not None:
            hits = collision.collisions(e["name"])
            if hits:
                errs.append(f"invented name {e['name']!r} collides: {', '.join(hits)}")
        if registry is not None:
            errs += registry.problems(e["name"])
        if e["name"] in used_names:
            errs.append(f"invented name {e['name']!r} was told not to be reused")
    return errs


def design_puzzle(brief, model, tier, template, hosts, pid, collision=None, registry=None,
                  naming="period-appropriate for north England in the 1800s", max_attempts=3, used_names=()):
    """Run call 2 until the fact graph passes `check_design`.

    Returns (puzzle or None, attempts). Each attempt: {"problems": [...]}; the last
    attempt's problems explain a None, and are the reason handed back to Stage 2.
    """
    knobs = TIERS[tier]
    attempts, feedback = [], ""
    for _ in range(max_attempts):
        prompt = DESIGNER_PROMPT.format(
            hosts=sorted(hosts), hops="-".join(map(str, knobs["hops"])), planted="-".join(map(str, knobs["planted"])),
            template=template, bridges=knobs["bridges"], naming=naming, used=sorted(used_names) or "none",
            brief=json.dumps(brief, indent=1)[:30000], feedback=feedback)
        try:
            d = parse_json(model(prompt))
        except (DesignError, ValueError) as e:
            problems = [f"unparseable reply: {e}"]
        else:
            d["pid"], d["template"] = pid, d.get("template", template)
            problems = check_design(d, brief, tier, hosts, collision, registry, used_names)
        attempts.append({"problems": problems})
        if not problems:
            for e in d["entities"]:
                if e.get("invented") and registry is not None:
                    registry.add(e["name"])
            d.update({"tier": tier, "knobs": knobs, "prompt_version": PROMPT_VERSION["designer"],
                      "gates": {g: "pending" for g in ("closed_book", "base_corpus", "oracle")}})
            return d, attempts
        feedback = "\nYour last design failed these checks. Fix all of them:\n- " + "\n- ".join(problems)
    return None, attempts


def anthropic_model(model_id, max_tokens=4000):
    """A `Model` backed by the Anthropic API (needs ANTHROPIC_API_KEY)."""
    import anthropic
    client = anthropic.Anthropic()

    def call(prompt):
        r = client.messages.create(model=model_id, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in r.content if b.type == "text")
    return call
