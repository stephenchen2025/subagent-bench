#!/usr/bin/env bash
# Reference solution for Harbor's oracle agent, written like an agent: it reads
# only /workspace and docs/, never the generator or the answer key. A full score
# proves the task is solvable from what the agent is given.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/solve.py" /workspace
