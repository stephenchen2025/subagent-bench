#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-3991",
      "order": "ORD-50045"
    },
    {
      "ticket": "T-4096",
      "order": "ORD-80199"
    },
    {
      "ticket": "T-4139",
      "order": "ORD-11664"
    },
    {
      "ticket": "T-4301",
      "order": "ORD-55472"
    },
    {
      "ticket": "T-7096",
      "order": "ORD-32183"
    },
    {
      "ticket": "T-7583",
      "order": "ORD-35027"
    }
  ]
}
EOF
