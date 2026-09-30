#!/usr/bin/env bash
# Reference solution for Harbor's oracle agent: proves the grader awards full
# marks. It reads the answers from the generator, so it says nothing about
# whether the task can be solved from the workspace alone.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/generate.py" --seed 1 --solve /workspace/answer/expenses.json
