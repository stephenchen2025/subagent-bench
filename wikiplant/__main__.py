"""python -m wikiplant snapshot --dump D --date YYYY-MM-DD --out DIR
python -m wikiplant search --paragraphs P --manifest M [--variant full] QUERY
"""

import argparse
import json
import sys
from pathlib import Path

from .parse import snapshot
from .schemas import read_jsonl, write_jsonl
from .tools import Corpus


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wikiplant")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot", help="parse a dump into paragraphs.jsonl, pages.json, snapshot_id")
    s.add_argument("--dump", required=True)
    s.add_argument("--date", required=True)
    s.add_argument("--out", required=True)
    q = sub.add_parser("search", help="search a built corpus")
    q.add_argument("--paragraphs", required=True)
    q.add_argument("--manifest")
    q.add_argument("--variant", default="full", choices=["full", "gold", "none"])
    q.add_argument("--k", type=int, default=5)
    q.add_argument("query")
    a = ap.parse_args(argv)

    if a.cmd == "snapshot":
        pages, paras, sid = snapshot(a.dump, a.date)
        out = Path(a.out)
        write_jsonl(out / "paragraphs.jsonl", paras)
        (out / "pages.json").write_text(json.dumps(pages, indent=1))
        (out / "snapshot_id").write_text(sid + "\n")
        print(f"{len(pages)} pages, {len(paras)} paragraphs, snapshot {sid}")
    else:
        manifest = json.loads(Path(a.manifest).read_text()) if a.manifest else []
        c = Corpus(read_jsonl(a.paragraphs), manifest, a.variant)
        for h in c.search(a.query, a.k):
            print(f"{h['passage_id']}  {h['title']} / {'/'.join(h['section_path'])}\n    {h['snippet']}")


if __name__ == "__main__":
    sys.exit(main())
