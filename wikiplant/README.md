# wikiplant

`wikiplant` builds a frozen Wikipedia corpus with invented sections planted in it, plus
multi-hop questions whose answers exist only in the planted text. Every planted span is
recorded in a manifest, so every hop of every question has exact ground truth. It
implements the "Planted-Fact Deep Research Pipeline" design doc.

**Status:** the whole pipeline runs end to end, but it does not yet produce puzzles that
pass every gate. Style leakage is the open problem: in the first pilot, a judge model
picked out the planted paragraph far above chance. See
[`results/wikiplant-pilot-gemini/`](../results/wikiplant-pilot-gemini/).

## Setup

```bash
pip install -r requirements-dev.txt   # includes pyarrow, needed only for step 1
export GEMINI_API_KEY=...             # needed only for step 3; a free-tier key works
```

Everything else is standard library. The tests need no network or key:

```bash
python -m pytest tests/test_wikiplant*.py -q
make wikiplant-demo                   # offline: build the sample corpus, run one search
```

## Running it

**1. Snapshot.** Pick one of these two sources.

From Wikimedia's Structured Wikipedia on Hugging Face (English, 2024-09-16), filtered to
one domain. This streams all 86 shards one at a time: about 37 GB downloaded, one shard on
disk at once, roughly 80 minutes. A cut-short download is retried, and a re-run skips
shards that are already done.

```bash
python -m wikiplant.structured --out build/sw --shards 0-85 --domain uk_industry
```

From an official XML dump (`pages-articles`, plain or `.bz2`), if you can reach
dumps.wikimedia.org:

```bash
python -m wikiplant snapshot --dump enwiki-pages-articles.xml.bz2 --date 2026-10-01 --out build/snap
```

Either way the output directory holds `paragraphs.jsonl`, `pages.json` and `snapshot_id`.

**2. Clusters (optional).** Preview the topic clusters without calling a model:

```bash
python -m wikiplant clusters --snapshot build/sw --seeds 40 --keep 5
```

**3. A batch.** Design, write, plant decoys and run all nine gates:

```bash
python -m wikiplant.run --snapshot build/sw --out build/run --puzzles 3
python -m wikiplant.run --snapshot build/sw --out build/run --gates-only   # re-run just the gates
```

The run writes `report.md` (gate pass rates, every question, every planted unit, model
usage), plus `puzzles.json`, `manifest.json`, `gate_results.json` and `clusters.json`.
It saves after each puzzle, so a run stopped by a spent quota keeps what it made.

**4. Search a built corpus** (no model needed):

```bash
python -m wikiplant search --paragraphs build/sw/paragraphs.jsonl \
  --manifest build/run/manifest.json "a question"
```

## Models and quota

Only Gemini is wired in, through `wikiplant/llm.py`. Each role in `run.py` (`GEMINI`) is
a chain of models: Flash models first, Flash-Lite last. When one model's quota is spent,
the role moves to the next model. The free tier allows about 20 requests a day per Flash
model, and a 3-puzzle run uses about 100 calls across the chain. Larger batches need a
paid key or several days.

Any function from a prompt string to a reply string works as a model; tests use stubs.
`design.anthropic_model(model_id)` adapts the Anthropic API, but `run.py` does not use it
yet.

## Modules

| Stage | Module | What it does |
|---|---|---|
| 0 Snapshot | `parse.py`, `structured.py` | XML dump or Structured Wikipedia → paragraph records keyed `page:section/path:idx` |
| 1 Clusters | `clusters.py` | link graph, hub removal, personalized PageRank, Louvain, scoring, diversification |
| 2 Fact graphs | `design.py`, `names.py` | cluster brief, designer loop, `check_design`, invented names and collision checks |
| 3 Prose | `writing.py` | host ranking, placement, writer loop and lint, style classifier, pick-the-planted test |
| 4 Decoys | `decoys.py` | near-misses, partial echoes, background decoys |
| 5 Gates | `gates.py` | the nine validation gates and a minimal search agent |
| 6 Corpus | `corpus.py`, `index.py`, `tools.py` | manifest application, chunking, BM25, logged `search`/`open`/`find_in_page` |
| Driver | `run.py`, `llm.py` | batch runner, Gemini client with pacing and quota fallback |
