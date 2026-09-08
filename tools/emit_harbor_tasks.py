#!/usr/bin/env python3
"""Emit Harbor task directories for every example spec.

Run: python tools/emit_harbor_tasks.py [out_dir]

Then, with Harbor installed:
    harbor run -d <out_dir> -a handoff-mini -m <model>
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.harbor_task import emit_all


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build" / "harbor")
    written = emit_all(ROOT, out)
    for path in written:
        print(f"  {path.relative_to(Path.cwd()) if path.is_relative_to(Path.cwd()) else path}")
    print(f"\n{len(written)} task(s) in {out}")
    print("The agent sees environment/repo only; checks, spec and baseline live "
          "in environment/_handoff, copied to /opt/handoff at build time.")


if __name__ == "__main__":
    main()
