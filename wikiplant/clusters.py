"""Stage 1: cluster discovery by seed-and-grow on the link graph.

A cluster is ~30-150 tightly linked pages on one topic. Pipeline per seed:
remove hubs, weight reciprocal links up, grow with personalized PageRank, split
the grown subgraph into communities and keep the seed's, then score it.

Standard library only. Louvain stands in for Leiden (same modularity objective,
no refinement step); tf-idf over lead paragraphs stands in for embeddings. Both
are small, replaceable functions.
"""

import math
import random
import re
import statistics
from collections import Counter, defaultdict

RECIPROCAL_WEIGHT = 3.0   # A<->B counts three times a one-way link
ONE_WAY_WEIGHT = 1.0
HOST_FILTERS = {"min_words": 800, "min_sections": 4, "views_cutoff_pct": 0.90}
GROW_TOP = 300
_YEAR = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9])\b")
_TOKEN = re.compile(r"[a-z]{3,}")


def norm_title(t):
    t = t.strip().replace("_", " ")
    return t[:1].upper() + t[1:]


def build_graph(paragraphs, redirects=None):
    """Directed link counts {(src, dst): n}, from paragraph outlinks resolved to page ids.

    Links are read from the text rather than a pagelinks table, so each knows its section.
    """
    ids = {norm_title(p["title"]): p["page_id"] for p in paragraphs}
    redirects = {norm_title(k): norm_title(v) for k, v in (redirects or {}).items()}
    edges = Counter()
    for p in paragraphs:
        for link in p["outlinks"]:
            t = norm_title(link)
            dst = ids.get(redirects.get(t, t))
            if dst is not None and dst != p["page_id"]:
                edges[(p["page_id"], dst)] += 1
    return edges


def undirected(edges, drop=frozenset()):
    """Symmetric weights {a: {b: w}}; reciprocal links weigh more than one-way ones."""
    adj = defaultdict(dict)
    for (a, b) in edges:
        if a in drop or b in drop or b in adj.get(a, {}):
            continue
        w = RECIPROCAL_WEIGHT if (b, a) in edges else ONE_WAY_WEIGHT
        adj[a][b] = adj[b][a] = w
    return adj


def find_hubs(edges, top_frac=0.01, titles=None, extra=()):
    """Page ids to drop first: the highest in-degree pages, plus named ones (countries, years...)."""
    indeg = Counter(b for (_, b) in edges)
    n = max(1, int(len(indeg) * top_frac)) if indeg else 0
    hubs = {p for p, _ in indeg.most_common(n)}
    by_title = {norm_title(t): i for i, t in (titles or {}).items()}
    hubs.update(by_title[norm_title(t)] for t in extra if norm_title(t) in by_title)
    return hubs


def page_stats(paragraphs):
    stats = {}
    for p in paragraphs:
        s = stats.setdefault(p["page_id"], {"words": 0, "sections": set(), "text": [], "lead": ""})
        s["words"] += len(p["text"].split())
        if p["section_path"]:
            s["sections"].add(tuple(p["section_path"]))
        elif not s["lead"]:
            s["lead"] = p["text"]
        s["text"].append(p["text"])
    return stats


def is_living(infobox):
    keys = {k.lower() for k in infobox}
    return bool(keys & {"birth_date", "born"}) and not (keys & {"death_date", "died"})


def host_pages(stats, pages, filters=HOST_FILTERS):
    """Page ids that may host a planted unit: long, multi-section, not famous, not a living person."""
    views = sorted(pages[i].get("views", 0) for i in stats if i in pages)
    cutoff = views[min(len(views) - 1, int(len(views) * filters["views_cutoff_pct"]))] if views else 0
    return {
        i for i, s in stats.items() if i in pages
        and s["words"] >= filters["min_words"] and len(s["sections"]) >= filters["min_sections"]
        and not (pages[i].get("views", 0) >= cutoff and cutoff > 0 and len(views) >= 10)
        and not is_living(pages[i].get("infobox", {}))
    }


def ppr(adj, seed, alpha=0.15, iters=40):
    """Personalized PageRank scores {page: score}, restarting at `seed`."""
    score = {seed: 1.0}
    for _ in range(iters):
        nxt = defaultdict(float)
        nxt[seed] += alpha
        for a, s in score.items():
            nbrs = adj.get(a)
            if not nbrs:
                nxt[seed] += (1 - alpha) * s
                continue
            total = sum(nbrs.values())
            for b, w in nbrs.items():
                nxt[b] += (1 - alpha) * s * w / total
        score = nxt
    return score


def louvain(adj, seed=0):
    """Communities {node: label}: local moving on modularity, then aggregate, until stable."""
    rng = random.Random(seed)
    nodes = list(adj)
    member = {n: n for n in nodes}          # original node -> current super-node
    graph = {n: dict(nb) for n, nb in adj.items()}
    while True:
        m2 = sum(w for nb in graph.values() for w in nb.values())
        if m2 == 0:
            break
        deg = {n: sum(nb.values()) for n, nb in graph.items()}
        comm = {n: n for n in graph}
        tot = dict(deg)
        moved_any = True
        while moved_any:
            moved_any = False
            order = list(graph)
            rng.shuffle(order)
            for n in order:
                links = defaultdict(float)
                for b, w in graph[n].items():
                    if b != n:
                        links[comm[b]] += w
                tot[comm[n]] -= deg[n]
                best, gain = comm[n], links.get(comm[n], 0.0) - tot[comm[n]] * deg[n] / m2
                for c, k in links.items():
                    g = k - tot[c] * deg[n] / m2
                    if g > gain + 1e-12:
                        best, gain = c, g
                tot[best] += deg[n]
                if best != comm[n]:
                    comm[n], moved_any = best, True
        if len(set(comm.values())) == len(graph):
            break
        for n in member:
            member[n] = comm[member[n]]
        agg = defaultdict(lambda: defaultdict(float))
        for c in set(comm.values()):
            agg[c]                      # keep communities whose members have no edges
        for a, nb in graph.items():
            for b, w in nb.items():
                agg[comm[a]][comm[b]] += w
        graph = {a: dict(nb) for a, nb in agg.items()}
    return member


def grow_cluster(adj, seed, top=GROW_TOP, louvain_seed=0):
    """Pages of the seed's community inside its top-`top` PageRank neighbourhood."""
    if seed not in adj:
        return {seed}
    near = {p for p, _ in sorted(ppr(adj, seed).items(), key=lambda x: (-x[1], x[0]))[:top]} | {seed}
    sub = {a: {b: w for b, w in adj[a].items() if b in near} for a in near if a in adj}
    labels = louvain(sub, louvain_seed)
    return {p for p, c in labels.items() if c == labels[seed]} | {seed}


def _tfidf(docs):
    toks = {k: Counter(_TOKEN.findall(v.lower())) for k, v in docs.items()}
    df = Counter(t for c in toks.values() for t in c)
    n = len(docs)
    vecs = {}
    for k, c in toks.items():
        v = {t: (1 + math.log(f)) * math.log(1 + n / df[t]) for t, f in c.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs[k] = {t: x / norm for t, x in v.items()}
    return vecs


def _cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


def score_cluster(members, adj, stats, pages, hosts, types=None):
    """The Stage 1 signals for one cluster, each in a documented unit."""
    members = sorted(members)
    n = len(members)
    inside = sum(1 for a in members for b in adj.get(a, {}) if b in set(members) and a < b)
    density = inside / (n * (n - 1) / 2) if n > 1 else 0.0
    leads = {i: stats[i]["lead"] or " ".join(stats[i]["text"][:1]) for i in members if i in stats}
    vecs = _tfidf(leads) if len(leads) > 1 else {}
    pairs = [(a, b) for k, a in enumerate(vecs) for b in list(vecs)[k + 1:]]
    coherence = statistics.fmean(_cos(vecs[a], vecs[b]) for a, b in pairs) if pairs else 0.0
    years = [int(y) for i in members if i in stats for t in stats[i]["text"] for y in _YEAR.findall(t)]
    views = [pages[i].get("views", 0) for i in members if i in pages]
    mix = Counter((types or {}).get(i, "unknown") for i in members)
    return {
        "size": n, "link_density": round(density, 4), "coherence": round(coherence, 4),
        "plantable": sum(1 for i in members if i in hosts),
        "median_views": statistics.median(views) if views else 0,
        "year_span": (max(years) - min(years)) if years else 0,
        "type_mix": dict(mix),
    }


def combined(sig, size_range=(30, 150)):
    """One number to rank candidates by; weights are starting values to tune against 20 reviewed clusters."""
    lo, hi = size_range
    if not lo <= sig["size"] <= hi:
        return 0.0
    surface = min(1.0, sig["plantable"] / 20)
    span = min(1.0, sig["year_span"] / 100)
    obscurity = 1.0 / (1.0 + math.log1p(sig["median_views"]) / 5)
    kinds = len([k for k in sig["type_mix"] if k != "unknown"])
    variety = min(1.0, kinds / 3) if kinds else 0.5
    return round(0.30 * min(1.0, sig["coherence"] * 4) + 0.20 * min(1.0, sig["link_density"] * 10)
                 + 0.20 * surface + 0.10 * span + 0.10 * obscurity + 0.10 * variety, 4)


def sample_seeds(candidates, n, rng_seed=0, exclude=frozenset()):
    pool = sorted(set(candidates) - set(exclude))
    return random.Random(rng_seed).sample(pool, min(n, len(pool)))


def discover(paragraphs, pages, seeds, redirects=None, hub_frac=0.01, hub_titles=(), types=None,
             size_range=(30, 150), filters=HOST_FILTERS):
    """Candidate clusters for `seeds`, best first. Each: seed, pages, signals, score."""
    pages = {int(k): v for k, v in pages.items()}
    edges = build_graph(paragraphs, redirects)
    hubs = find_hubs(edges, hub_frac, {i: p["title"] for i, p in pages.items()}, hub_titles)
    adj = undirected(edges, hubs)
    stats = page_stats(paragraphs)
    hosts = host_pages(stats, pages, filters)
    out = []
    for s in seeds:
        members = grow_cluster(adj, s)
        sig = score_cluster(members, adj, stats, pages, hosts, types)
        out.append({"seed": s, "pages": sorted(members), "signals": sig, "score": combined(sig, size_range)})
    out.sort(key=lambda c: (-c["score"], c["seed"]))
    return out


def diversify(clusters, stats, keep, overlap_max=0.3, similarity_max=0.5):
    """Greedy pick of `keep` clusters: skip heavy page overlap or near-identical topic centroids."""
    centroid = lambda c: {k: v for k, v in _tfidf({c["seed"]: " ".join(
        " ".join(stats[i]["text"]) for i in c["pages"] if i in stats)})[c["seed"]].items()}
    chosen, cents = [], []
    for c in clusters:
        if c["score"] <= 0:
            continue
        pset = set(c["pages"])
        if any(len(pset & set(o["pages"])) / len(pset) > overlap_max for o in chosen):
            continue
        cv = centroid(c)
        if any(_cos(cv, o) > similarity_max for o in cents):
            continue
        chosen.append(c)
        cents.append(cv)
        if len(chosen) == keep:
            break
    return chosen
