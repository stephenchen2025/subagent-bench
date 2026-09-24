#!/usr/bin/env bash
# Grades /workspace against /tests/ground_truth.json; writes /logs/verifier/reward.json.
set -uo pipefail
mkdir -p /logs/verifier
cd /workspace
python3 /tests/verify.py
