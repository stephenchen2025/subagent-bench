#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > textkit/chunks.py <<'PYEOF'
"""Chunking helpers."""


def chunk(seq, size):
    """Split `seq` into lists of `size`; the last chunk may be shorter."""
    if size < 1:
        raise ValueError("size must be positive")
    return [list(seq[i:i + size]) for i in range(0, len(seq), size)]
PYEOF
