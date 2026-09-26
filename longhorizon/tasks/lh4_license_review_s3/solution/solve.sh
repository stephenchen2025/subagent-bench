#!/usr/bin/env bash
# Reference solution for Harbor's oracle agent: proves the task is solvable and
# the grader awards full marks. It reads the answers from the generator, so it
# says nothing about how hard the task is.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/generate.py" --seed 3 --solve /workspace/review/licenses.json
