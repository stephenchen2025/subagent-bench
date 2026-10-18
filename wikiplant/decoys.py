"""Stage 4: decoys, near-misses and partial echoes.

Every unit here goes through the same writer pool, prompts, lengths and
placement rules as gold units (writing.plant_fact), so gold and decoys are not
two separable classes. Roles:

  decoy         an unrelated invented fact on a random host page, 3-5 per gold unit
  near_miss     a similarly named entity with a different attribute value, on a page the
                question's constraints rule out; up to one per hop, as the tier allows
  partial_echo  mentions an invented bridge entity without the attribute the question needs

No unit may contradict a gold fact: same subject and relation with a different value.
"""

import random

from . import names as nm
from .writing import plant_fact

DECOYS_PER_GOLD = (3, 5)
ECHO_RATE = 0.5

# Relations a background decoy can state about an invented subject and a real object.
DECOY_RELATIONS = {
    "firm": ["supplied_ironwork_to", "repaired_rolling_stock_for", "built_a_warehouse_for", "leased_land_from"],
    "society": ["held_meetings_at", "published_a_survey_of", "raised_a_subscription_for"],
    "company": ["carried_freight_for", "bought_coal_from", "leased_a_wharf_from"],
}
# Relations a partial echo can state about a bridge entity without giving away dates or counts.
ECHO_RELATIONS = ["had_offices_in", "employed_workers_from", "advertised_in", "was_based_near"]


def new_name(kind, rng, collision=None, registry=None, tries=50, **constraints):
    """An invented name that passes collision and repeat caps, registered on return."""
    for _ in range(tries):
        cand = nm.generate(kind, rng=rng, **constraints)
        if collision is not None and collision.collisions(cand):
            continue
        if registry is not None and registry.problems(cand):
            continue
        if registry is not None:
            registry.add(cand)
        return cand
    raise RuntimeError(f"no free {kind} name after {tries} tries; widen the name pools")


def similar_name(name, rng, collision=None, registry=None, tries=50):
    """A near-miss name sharing a distinctive part with `name` (a surname or place)."""
    parts = [w for w in name.replace("&", "and").split() if w[:1].isupper() and w.lower() not in
             {"and", "company", "sons", "brothers", "society", "union", "institute"}]
    pool = nm.POOLS[("north england", "1800s")]
    forms = ["{a} Brothers", "{a} & Sons", "{a} and {b}", "{a}, {b} and Company"]
    for _ in range(tries):
        a = rng.choice(parts) if parts else rng.choice(pool["surnames"])
        b = rng.choice([s for s in pool["surnames"] if s != a])
        cand = rng.choice(forms).format(a=a, b=b)
        if nm.normalize(cand) == nm.normalize(name):
            continue
        if collision is not None and collision.collisions(cand):
            continue
        if registry is not None and nm.normalize(cand) in registry.names:
            continue
        if registry is not None:
            registry.add(cand)
        return cand
    raise RuntimeError(f"no near-miss name for {name!r}")


def contradicts(fact, gold_facts, entities):
    """True if `fact` gives a gold fact's subject and relation a different value."""
    key = lambda f: (entities[f["s"]]["name"].lower(), f["r"])
    for g in gold_facts:
        if key(g) == key(fact) and (entities[g["o"]]["name"] != entities[fact["o"]]["name"] or g.get("when") != fact.get("when")):
            return True
    return False


def plan(puzzle, tier_knobs, rng):
    """How many of each role this puzzle gets."""
    gold = sum(1 for f in puzzle["facts"] if f.get("planted"))
    return {
        "decoy": sum(rng.randint(*DECOYS_PER_GOLD) for _ in range(gold)),
        "near_miss": min(tier_knobs["near_misses"], len(puzzle["path"])),
        "partial_echo": 1 if rng.random() < ECHO_RATE else 0,
    }


def _path_pages(puzzle):
    pages = set()
    for f in puzzle["facts"]:
        if f["fid"] in puzzle["path"]:
            pages.add(f["host_page"] if f.get("planted") else int(str(f["para_id"]).split(":", 1)[0]))
    return pages


def _year_near(when, rng, avoid, lo=3, hi=12):
    while True:
        y = when + rng.choice([-1, 1]) * rng.randint(lo, hi)
        if str(y) not in avoid:
            return y


def make_units(puzzle, paragraphs, pages, hosts, cluster_pages, pool, ledger, rng,
               collision=None, registry=None, counts=None, tier_knobs=None):
    """Write every decoy-type unit for one puzzle. Returns (manifest entries, log).

    hosts: host-eligible page ids anywhere in the corpus (background decoys go inside and
    outside clusters). cluster_pages: this puzzle's cluster (near-misses stay on topic).
    """
    counts = counts or plan(puzzle, tier_knobs, rng)
    ents = {e["eid"]: dict(e) for e in puzzle["entities"]}
    facts = {f["fid"]: f for f in puzzle["facts"]}
    gold = [facts[x] for x in puzzle["path"] if facts[x].get("planted")]
    answer = str(puzzle["answer"])
    forbid = [answer] + list(puzzle.get("aliases", []))
    off_path = [p for p in sorted(cluster_pages) if p not in _path_pages(puzzle) and p in hosts]
    titles = {i: (pages[i]["title"] if i in pages else str(i)) for i in hosts | set(cluster_pages)}
    entries, log, n = [], [], 0

    def uid(role):
        nonlocal n
        n += 1
        return f"{puzzle['pid']}-{role}-{n:02d}"

    def pick(candidates, role):
        free = [c for c in candidates if ledger.free(c, role)]
        if not free:
            log.append({"role": role, "error": "no free host page left under the density cap"})
            return None
        return rng.choice(free)

    def write(role, fact, candidates, extra_forbid=()):
        u = uid(role)
        if contradicts(fact, gold, ents):
            log.append({"unit_id": u, "error": "would contradict a gold fact"})
            return
        entry, info = plant_fact(u, fact, ents, paragraphs, candidates, pool, ledger, rng, role=role,
                                 forbid=[x for x in forbid + list(extra_forbid) if x])
        log.append({"unit_id": u, **info})
        if entry:
            entry["puzzle"] = puzzle["pid"]
            entry["fact"] = {k: (ents[fact[k]]["name"] if k in ("s", "o") else v) for k, v in fact.items()}
            entries.append(entry)

    # Near-misses: one per planted hop (up to the tier's count), similar subject, different object and year.
    for g in gold[:counts["near_miss"]]:
        page = pick(off_path, "near_miss")
        if page is None:
            break
        e_sub, e_obj = f"nm{n}s", f"nm{n}o"
        ents[e_sub] = {"eid": e_sub, "name": similar_name(ents[g["s"]]["name"], rng, collision, registry), "invented": True}
        ents[e_obj] = {"eid": e_obj, "name": titles[page], "invented": False}
        fact = {"fid": e_sub, "s": e_sub, "r": g["r"], "o": e_obj, "planted": True,
                "when": _year_near(g["when"], rng, forbid) if g.get("when") is not None else None}
        write("near_miss", fact, [page])

    # Partial echo: names an invented bridge entity, says nothing that answers the question.
    bridges = [ents[g["s"]] for g in gold if ents[g["s"]].get("invented")]
    page = pick(off_path, "partial_echo") if counts["partial_echo"] and bridges else None
    if page is not None:
        b = rng.choice(bridges)
        e_obj = f"pe{n}o"
        ents[e_obj] = {"eid": e_obj, "name": titles[page], "invented": False}
        fact = {"fid": "echo", "s": b["eid"], "r": rng.choice(ECHO_RELATIONS), "o": e_obj, "planted": True}
        write("partial_echo", fact, [page])

    # Background decoys: unrelated invented facts on random host pages, inside and outside the cluster.
    others = sorted(hosts)
    for _ in range(counts["decoy"]):
        kind = rng.choice(sorted(DECOY_RELATIONS))
        page = pick(others, "decoy")
        if page is None:
            break
        e_sub, e_obj = f"d{n}s", f"d{n}o"
        ents[e_sub] = {"eid": e_sub, "name": new_name(kind, rng, collision, registry), "invented": True}
        ents[e_obj] = {"eid": e_obj, "name": titles[page], "invented": False}
        when = rng.choice([y for y in range(1840, 1901) if str(y) not in forbid])
        fact = {"fid": e_sub, "s": e_sub, "r": rng.choice(DECOY_RELATIONS[kind]), "o": e_obj, "planted": True, "when": when}
        write("decoy", fact, [page], extra_forbid=[b["name"] for b in bridges])
    return entries, log


def ratio_report(manifest):
    """Counts by role and decoys per gold unit, for the batch summary."""
    from collections import Counter
    c = Counter(u["role"] for u in manifest)
    gold = c.get("gold", 0)
    return {"by_role": dict(c), "decoys_per_gold": round(c.get("decoy", 0) / gold, 2) if gold else None}
