"""Stage 0: wikitext -> paragraph records.

Standard library only. This is a deliberately small wikitext reader: headings,
links, infoboxes and the markup that would otherwise leak into the text. Swap in
mwparserfromhell or HTML dumps if the spot check of parsed pages shows losses.
"""

import bz2
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from . import PARSER_VERSION
from .schemas import para_id

DROP_SECTIONS = {"see also", "references", "external links", "further reading", "notes", "footnotes", "sources", "bibliography"}
MIN_PARAGRAPH_CHARS = 20

_HEADING = re.compile(r"^(={2,6})\s*(.+?)\s*\1\s*$")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_REF = re.compile(r"<ref\b[^>/]*?/>|<ref\b[^>]*>.*?</ref>", re.S | re.I)
_TAGS = re.compile(r"</?(?:small|big|sup|sub|span|div|center|nowiki|blockquote|gallery|references)\b[^>]*>", re.I)
_TABLE = re.compile(r"\{\|.*?\|\}", re.S)
_INNER_TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
_LINK = re.compile(r"\[\[([^\[\]|#]*)(?:#[^\[\]|]*)?(?:\|([^\[\]]*))?\]\]")
_FILE_LINK = re.compile(r"\[\[(?:File|Image|Category):[^\[\]]*(?:\[\[[^\[\]]*\]\][^\[\]]*)*\]\]", re.I)
_EXT_LINK = re.compile(r"\[(?:https?:)?//\S+(?:\s+([^\]]*))?\]")
_QUOTES = re.compile(r"'{2,5}")


def _balanced(text, start):
    """Index just past the {{...}} that opens at `start`, or -1."""
    depth, i = 0, start
    while i < len(text) - 1:
        pair = text[i:i + 2]
        if pair == "{{":
            depth += 1
            i += 2
        elif pair == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return i
        else:
            i += 1
    return -1


def extract_infobox(text):
    """(infobox key-values, text without the infobox)."""
    m = re.search(r"\{\{\s*Infobox", text, re.I)
    if not m:
        return {}, text
    end = _balanced(text, m.start())
    if end < 0:
        return {}, text
    body = text[m.start() + 2:end - 2]
    fields = {}
    for line in body.split("\n")[1:]:
        if line.lstrip().startswith("|") and "=" in line:
            key, _, val = line.lstrip()[1:].partition("=")
            fields[key.strip()] = clean_inline(val.strip())[0]
    return fields, text[:m.start()] + text[end:]


def strip_templates(text):
    prev = None
    while prev != text:
        prev, text = text, _INNER_TEMPLATE.sub("", text)
    return text


def clean_inline(text):
    """(plain text, outlink titles) for one block of wikitext."""
    links = []

    def link(m):
        target = m.group(1).strip()
        if target:
            links.append(target)
        return m.group(2) if m.group(2) is not None else m.group(1)

    text = _COMMENT.sub("", text)
    text = _REF.sub("", text)
    text = _FILE_LINK.sub("", text)
    text = _LINK.sub(link, text)
    text = _EXT_LINK.sub(lambda m: m.group(1) or "", text)
    text = _TAGS.sub("", text)
    text = _QUOTES.sub("", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text, links


def is_skippable(title, wikitext):
    """Redirects, disambiguation pages and list pages carry no plantable prose."""
    head = wikitext.lstrip()[:200].lower()
    if head.startswith("#redirect"):
        return "redirect"
    if re.search(r"\{\{\s*(disambig|disambiguation|set index|surname|given name)", wikitext, re.I):
        return "disambiguation"
    if re.match(r"(list|lists|index|timeline) of ", title.lower()):
        return "list"
    return None


def parse_page(page_id, title, wikitext):
    """(paragraph records, infobox) for one page, or ([], {}) if skippable."""
    if is_skippable(title, wikitext):
        return [], {}
    infobox, text = extract_infobox(_COMMENT.sub("", wikitext))
    text = _TABLE.sub("", text)
    text = strip_templates(text)

    paragraphs, path, keep, buf = [], [], True, []
    counters = {}

    def flush():
        block = "\n".join(buf).strip()
        buf.clear()
        if not block or not keep:
            return
        plain, links = clean_inline(block)
        if len(plain) < MIN_PARAGRAPH_CHARS or plain.startswith(("*", "#", ":", ";")):
            return
        key = tuple(path)
        idx = counters.get(key, 0)
        counters[key] = idx + 1
        paragraphs.append({
            "para_id": para_id(page_id, path, idx), "page_id": page_id, "title": title,
            "section_path": list(path), "para_idx": idx, "text": plain,
            "outlinks": sorted(set(links)),
        })

    for line in text.split("\n"):
        h = _HEADING.match(line)
        if h:
            flush()
            level, name = len(h.group(1)), clean_inline(h.group(2))[0]
            path = path[:level - 2] + [name]
            keep = not any(p.lower() in DROP_SECTIONS for p in path)
        elif not line.strip():
            flush()
        else:
            buf.append(line)
    flush()
    return paragraphs, infobox


def iter_dump(path):
    """Yield (page_id, title, wikitext) for main-namespace pages of a pages-articles dump."""
    opener = bz2.open if str(path).endswith(".bz2") else open
    with opener(path, "rb") as f:
        title = pid = ns = text = None
        for _, el in ET.iterparse(f):
            tag = el.tag.rsplit("}", 1)[-1]
            if tag == "title":
                title = el.text
            elif tag == "ns":
                ns = el.text
            elif tag == "id" and pid is None:
                pid = int(el.text)
            elif tag == "text":
                text = el.text or ""
            elif tag == "page":
                if ns == "0" and title:
                    yield pid, title, text or ""
                title = pid = ns = text = None
                el.clear()


def snapshot(dump_path, dump_date, pageviews=None):
    """Parse a dump into tables and a snapshot id.

    Returns (pages, paragraphs, snapshot_id). pages: id -> {title, infobox, views}.
    """
    pages, paragraphs = {}, []
    for pid, title, wikitext in iter_dump(dump_path):
        paras, infobox = parse_page(pid, title, wikitext)
        if not paras:
            continue
        pages[pid] = {"title": title, "infobox": infobox, "views": (pageviews or {}).get(title, 0)}
        paragraphs.extend(paras)
    digest = hashlib.sha256()
    digest.update(f"{dump_date}|{PARSER_VERSION}".encode())
    digest.update(json.dumps(paragraphs, sort_keys=True).encode())
    return pages, paragraphs, digest.hexdigest()[:16]
