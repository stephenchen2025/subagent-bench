"""Stage 0 from Wikimedia's Structured Wikipedia (Hugging Face: wikimedia/structured-wikipedia).

An alternative to parse.py for environments that cannot reach dumps.wikimedia.org.
Each row already carries plain-text paragraphs, a section tree, links per
paragraph and infoboxes, so no wikitext parsing is needed. The September 2024
English snapshot is 86 parquet shards (~37 GB); `ingest` streams them one at a
time and keeps only the pages a domain filter selects.

    python -m wikiplant.structured --out build/sw --shards 0-85 --domain uk_industry

Limits versus the XML dump: no redirect table (links to redirect titles are
dropped) and no pageviews (the popularity filter does nothing until views are joined).
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

from . import PARSER_VERSION
from .parse import DROP_SECTIONS, MIN_PARAGRAPH_CHARS, is_skippable
from .schemas import para_id, write_jsonl

BASE = "https://huggingface.co/datasets/wikimedia/structured-wikipedia/resolve/main/enwiki/data/enwiki_namespace_0_{}.parquet"
SNAPSHOT_DATE = "2024-09-16"
WIKI = "https://en.wikipedia.org/wiki/"

DOMAINS = {
    # 19th and early 20th century British industry and transport, and the towns around it.
    "uk_industry": {
        "topic": re.compile(r"\b(railways?|railway station|colliery|collieries|coal mine|canal|cotton mill|woollen mill|"
                            r"mills?\b|ironworks|steelworks|engine shed|locomotives?|tramways?|viaduct|shipyard|"
                            r"shipbuild\w*|wagon works|foundry|navigation company|tunnel|wharf|docks?)\b", re.I),
        "place": re.compile(r"\b(England|English|Scotland|Scottish|Wales|Welsh|Britain|British|United Kingdom|"
                            r"Lancashire|Yorkshire|Cheshire|Derbyshire|Durham|Northumberland|Cumbria|Cumberland|"
                            r"Westmorland|Staffordshire|Nottinghamshire|Lincolnshire|Leicestershire|Midlands|"
                            r"Shropshire|Cornwall|Devon|Somerset|Glamorgan|Monmouthshire|Lanarkshire|Fife)\b"),
        # A settlement counts only when the same sentence places it in Britain.
        "settlement": re.compile(r"\bis an? (?:[\w-]+ ){0,3}(?:town|village|parish|hamlet|suburb)\b[^.]{0,150}?\b"
                                 r"(?:England|Scotland|Wales|Lancashire|Yorkshire|Cheshire|Derbyshire|Durham|"
                                 r"Northumberland|Cumbria|Staffordshire|Nottinghamshire|Lincolnshire|Shropshire|"
                                 r"Cornwall|Devon|Somerset|Glamorgan|Lanarkshire|Fife|Midlands)\b", re.I),
        "exclude": re.compile(r"\b(Australia|Tasmania|New South Wales|Victoria, Australia|Queensland|New Zealand|"
                              r"Canada|Ontario|United States|India|South Africa)\b|\bmay (?:also )?refer to\b|"
                              r"\(disambiguation\)|footballer|cricketer|rugby|politician"),
    },
}


def title_from_url(url):
    if not url or not url.startswith(WIKI):
        return None
    t = urllib.parse.unquote(url[len(WIKI):]).split("#", 1)[0].replace("_", " ")
    if not t or ":" in t.split(" ", 1)[0] and t.split(":", 1)[0] in {"File", "Category", "Template", "Help", "Wikipedia", "Special", "Portal"}:
        return None
    return t


def flatten_infobox(raw):
    """Field name -> value for the first infobox, or {}."""
    if not raw:
        return {}
    try:
        boxes = json.loads(raw)
    except ValueError:
        return {}
    out = {}

    def walk(node):
        for part in node.get("has_parts", []) or []:
            if part.get("type") == "field" and part.get("name") and part.get("value") is not None:
                out.setdefault(part["name"], part["value"])
            else:
                walk(part)
    if boxes:
        walk(boxes[0])
    return out


def to_paragraphs(page_id, title, sections_raw):
    """Paragraph records in the same schema as parse.parse_page."""
    try:
        sections = json.loads(sections_raw or "[]")
    except ValueError:
        return []
    paras, counters = [], {}

    def walk(node, path):
        name = node.get("name") or ""
        if path and any(p.lower() in DROP_SECTIONS for p in path):
            return
        for part in node.get("has_parts", []) or []:
            kind = part.get("type")
            if kind == "section":
                walk(part, path + [part.get("name") or ""])
            elif kind == "paragraph":
                text = re.sub(r"\s+", " ", part.get("value") or "").strip()
                if len(text) < MIN_PARAGRAPH_CHARS:
                    continue
                key = tuple(path)
                idx = counters.get(key, 0)
                counters[key] = idx + 1
                links = sorted({t for t in (title_from_url(l.get("url")) for l in part.get("links") or []) if t and t != title})
                paras.append({"para_id": para_id(page_id, path, idx), "page_id": page_id, "title": title,
                              "section_path": list(path), "para_idx": idx, "text": text, "outlinks": links})

    for top in sections:
        if top.get("type") != "section":
            continue
        name = top.get("name") or ""
        walk(top, [] if name == "Abstract" else [name])
    return paras


def selected(title, abstract, domain):
    d = DOMAINS[domain]
    head = f"{title}. {(abstract or '')[:600]}"
    if d["exclude"].search(head) or not d["place"].search(head):
        return False
    return bool(d["topic"].search(head) or d["settlement"].search(head))


def iter_rows(path, columns=("identifier", "name", "abstract", "sections", "infoboxes")):
    import pyarrow.parquet as pq
    f = pq.ParquetFile(path)
    for batch in f.iter_batches(batch_size=2000, columns=list(columns)):
        cols = {c: batch.column(c).to_pylist() for c in columns}
        for i in range(batch.num_rows):
            yield {c: cols[c][i] for c in columns}


def ingest_shard(path, domain):
    """(pages, paragraphs) kept from one shard."""
    pages, paras = {}, []
    for row in iter_rows(path):
        title, pid = row["name"], row["identifier"]
        if not title or pid is None or not selected(title, row["abstract"], domain):
            continue
        if is_skippable(title, row["abstract"] or ""):
            continue
        ps = to_paragraphs(pid, title, row["sections"])
        if not ps:
            continue
        pages[pid] = {"title": title, "infobox": flatten_infobox(row["infoboxes"]), "views": 0}
        paras.extend(ps)
    return pages, paras


def _shard_list(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def download(url, dest, attempts=6):
    """Fetch to dest via a .part file, retrying transfers the network cuts short."""
    import time
    tmp = dest.with_suffix(".part")
    for i in range(attempts):
        try:
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(dest)
            return
        except (urllib.error.URLError, urllib.error.ContentTooShortError, ConnectionError, TimeoutError) as e:
            if i == attempts - 1:
                raise
            print(f"retrying {url.rsplit('/', 1)[-1]} after: {e}", flush=True)
            time.sleep(5 * 2 ** i)


def ingest(out, shards, domain, workdir=None, keep_download=False):
    out = Path(out)
    workdir = Path(workdir or out / "_download")
    workdir.mkdir(parents=True, exist_ok=True)
    (out / "shards").mkdir(parents=True, exist_ok=True)
    for n in shards:
        done = out / "shards" / f"{n}.done"
        if done.exists():
            continue
        local = workdir / f"enwiki_namespace_0_{n}.parquet"
        if not local.exists():
            download(BASE.format(n), local)
        pages, paras = ingest_shard(local, domain)
        write_jsonl(out / "shards" / f"{n}.paragraphs.jsonl", paras)
        (out / "shards" / f"{n}.pages.json").write_text(json.dumps(pages))
        done.write_text(f"{len(pages)} pages\n")
        if not keep_download:
            local.unlink()
        print(f"shard {n}: {len(pages)} pages, {len(paras)} paragraphs", flush=True)
    return merge(out, domain)


def merge(out, domain):
    """Combine shard outputs into paragraphs.jsonl, pages.json and snapshot_id, as parse.snapshot writes."""
    out = Path(out)
    pages, digest = {}, hashlib.sha256(f"structured-wikipedia|{SNAPSHOT_DATE}|{domain}|{PARSER_VERSION}".encode())
    with open(out / "paragraphs.jsonl", "w") as w:
        for f in sorted((out / "shards").glob("*.paragraphs.jsonl"), key=lambda p: int(p.name.split(".")[0])):
            data = f.read_text()
            w.write(data)
            digest.update(data.encode())
            pages.update(json.loads(f.with_name(f.name.replace("paragraphs.jsonl", "pages.json")).read_text()))
    (out / "pages.json").write_text(json.dumps(pages))
    sid = digest.hexdigest()[:16]
    (out / "snapshot_id").write_text(sid + "\n")
    return len(pages), sid


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wikiplant.structured")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shards", default="0-85")
    ap.add_argument("--domain", default="uk_industry", choices=sorted(DOMAINS))
    ap.add_argument("--workdir")
    a = ap.parse_args(argv)
    n, sid = ingest(a.out, _shard_list(a.shards), a.domain, a.workdir)
    print(f"{n} pages, snapshot {sid}")


if __name__ == "__main__":
    sys.exit(main())
