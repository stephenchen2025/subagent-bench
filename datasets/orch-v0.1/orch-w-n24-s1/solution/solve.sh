#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1855",
      "order": "ORD-56748"
    },
    {
      "ticket": "T-2642",
      "order": "ORD-83401"
    },
    {
      "ticket": "T-5972",
      "order": "ORD-18596"
    },
    {
      "ticket": "T-7095",
      "order": "ORD-79099"
    },
    {
      "ticket": "T-7362",
      "order": "ORD-61216"
    },
    {
      "ticket": "T-7591",
      "order": "ORD-16888"
    }
  ]
}
EOF
