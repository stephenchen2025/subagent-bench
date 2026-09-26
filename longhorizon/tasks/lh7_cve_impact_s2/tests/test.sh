#!/usr/bin/env bash
# Harbor verifier. Regenerates the ground truth from the image's seed -- the
# answers were never in the image -- grades, and writes the reward.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /logs/verifier
python3 "$HERE/generate.py" --seed 2 --grade /workspace/impact/impact.json > /logs/verifier/grade.json
python3 -c "import json; print(json.load(open('/logs/verifier/grade.json'))['reward'])" \
  > /logs/verifier/reward.txt
cat /logs/verifier/reward.txt
