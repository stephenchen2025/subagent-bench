#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-2045",
      "order": "ORD-64633"
    },
    {
      "ticket": "T-8818",
      "order": "ORD-75804"
    }
  ]
}
EOF
