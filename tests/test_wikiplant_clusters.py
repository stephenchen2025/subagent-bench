import random

from wikiplant.clusters import (build_graph, discover, diversify, find_hubs, grow_cluster, host_pages, is_living,
                                louvain, page_stats, ppr, sample_seeds, undirected)

TOPIC_A = "railway locomotive station mill cotton viaduct junction goods shed coal siding".split()
TOPIC_B = "expedition specimen museum collector herbarium society fossil journal survey cabinet".split()


def make_corpus(per=40, seed=1):
    """Two dense topic groups of `per` pages, one hub linked from everything, plus sparse cross links."""
    rng = random.Random(seed)
    paras, pages = [], {}
    groups = {"A": (range(1, per + 1), TOPIC_A), "B": (range(1001, 1001 + per), TOPIC_B)}
    hub = 9999
    title = lambda i: f"Page {i}"
    for g, (ids, vocab) in groups.items():
        ids = list(ids)
        for i in ids:
            links = rng.sample([j for j in ids if j != i], 8) + [hub]
            if rng.random() < 0.05:
                links.append(rng.choice(range(1, per + 1) if g == "B" else range(1001, 1001 + per)))
            body = " ".join(rng.choice(vocab) for _ in range(900))
            lead = " ".join(rng.choice(vocab) for _ in range(30))
            paras.append({"para_id": f"{i}::0", "page_id": i, "title": title(i), "section_path": [], "para_idx": 0,
                          "text": lead, "outlinks": [title(j) for j in links]})
            for s in range(4):
                paras.append({"para_id": f"{i}:S{s}:0", "page_id": i, "title": title(i), "section_path": [f"S{s}"],
                              "para_idx": 0, "text": body[: 1500], "outlinks": []})
            pages[i] = {"title": title(i), "infobox": {}, "views": rng.randint(50, 500)}
    paras.append({"para_id": f"{hub}::0", "page_id": hub, "title": title(hub), "section_path": [], "para_idx": 0,
                  "text": "A country with a long history of everything and everyone here.", "outlinks": []})
    pages[hub] = {"title": title(hub), "infobox": {}, "views": 10**6}
    return paras, pages, hub


def test_graph_resolves_titles_and_weights_reciprocal_links():
    paras = [
        {"page_id": 1, "title": "Alpha", "outlinks": ["beta", "Gamma_x"], "section_path": [], "text": "x"},
        {"page_id": 2, "title": "Beta", "outlinks": ["Alpha"], "section_path": [], "text": "x"},
        {"page_id": 3, "title": "Gamma x", "outlinks": [], "section_path": [], "text": "x"},
    ]
    edges = build_graph(paras)
    assert set(edges) == {(1, 2), (1, 3), (2, 1)}
    adj = undirected(edges)
    assert adj[1][2] == 3.0 and adj[1][3] == 1.0 and adj[2][1] == 3.0
    assert 3 not in undirected(edges, drop={3})


def test_hub_is_found_and_removed():
    paras, pages, hub = make_corpus()
    edges = build_graph(paras)
    assert hub in find_hubs(edges, 0.01)
    assert hub not in undirected(edges, {hub})


def test_ppr_favours_neighbours_and_louvain_splits_topics():
    paras, pages, hub = make_corpus()
    adj = undirected(build_graph(paras), {hub})
    scores = ppr(adj, 1)
    assert sum(1 for p, _ in sorted(scores.items(), key=lambda x: -x[1])[:30] if p < 1000) >= 28
    labels = louvain(adj)
    assert len({labels[i] for i in range(1, 41)}) == 1
    assert labels[1] != labels[1001]


def test_grow_cluster_stays_in_topic():
    paras, pages, hub = make_corpus()
    adj = undirected(build_graph(paras), {hub})
    cluster = grow_cluster(adj, 1001)
    assert cluster <= set(range(1001, 1041)) and len(cluster) >= 35


def test_host_filters():
    paras, pages, hub = make_corpus()
    stats = page_stats(paras)
    hosts = host_pages(stats, pages)
    assert hub not in hosts
    famous = max((i for i in pages if i != hub), key=lambda i: pages[i]["views"])
    quiet = min(pages, key=lambda i: pages[i]["views"])
    assert famous not in hosts and quiet in hosts       # top ~10% by views are memorized
    pages[quiet]["infobox"] = {"birth_date": "1950"}
    assert quiet not in host_pages(stats, pages)
    assert is_living({"born": "1950"}) and not is_living({"born": "1850", "died": "1920"})


def test_discover_scores_and_diversifies():
    paras, pages, hub = make_corpus()
    stats = page_stats(paras)
    found = discover(paras, pages, [1, 2, 1001, 1002], size_range=(30, 150))
    assert all(c["signals"]["size"] >= 35 and c["score"] > 0 for c in found)
    sig = found[0]["signals"]
    assert sig["coherence"] > 0.3 and sig["plantable"] >= 30
    picked = diversify(found, stats, keep=5)
    assert len(picked) == 2                       # one per topic; same-topic repeats are dropped
    assert {min(c["pages"]) < 1000 for c in picked} == {True, False}
    assert discover(paras, pages, [1], size_range=(500, 600))[0]["score"] == 0.0


def test_sample_seeds_is_reproducible():
    assert sample_seeds(range(100), 5, 7) == sample_seeds(range(100), 5, 7)
    assert 3 not in sample_seeds(range(5), 10, 0, exclude={3})


def test_louvain_keeps_isolated_nodes():
    adj = {1: {2: 1.0}, 2: {1: 1.0, 3: 1.0}, 3: {2: 1.0}, 4: {}, 5: {6: 1.0}, 6: {5: 1.0}}
    labels = louvain(adj)
    assert set(labels) == {1, 2, 3, 4, 5, 6} and labels[1] == labels[2] and labels[4] not in (labels[1], labels[5])


def test_diversify_ignores_words_every_cluster_shares():
    common = "the town was in the county and the parish had a church and the railway " * 20
    stats = {i: {"text": [common + ("cotton spinning weaving loom mill " * 3 if i < 10 else "fossil specimen museum collector " * 3)]}
             for i in range(20)}
    cands = [{"seed": 0, "pages": list(range(0, 5)), "score": 0.9},
             {"seed": 5, "pages": list(range(5, 10)), "score": 0.8},
             {"seed": 10, "pages": list(range(10, 15)), "score": 0.7}]
    picked = diversify(cands, stats, keep=3, similarity_max=0.5)
    assert [c["seed"] for c in picked] == [0, 10]     # same-topic cluster 5 dropped, other topic kept
