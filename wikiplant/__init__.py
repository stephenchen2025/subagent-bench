"""Planted-fact Wikipedia corpus: snapshot, manifest, build and search.

Stage 0 (parse.py) turns a dump into paragraph records. Stage 6 (corpus.py,
index.py, tools.py) applies a plant manifest to that snapshot and exposes the
search/open tools an agent uses. The LLM stages (clusters, fact graphs, writing,
validation gates) plug in between through the schemas in schemas.py.
"""

PARSER_VERSION = "wikiplant-parse-1"
