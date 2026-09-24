#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-4922",
      "order": "ORD-16080"
    },
    {
      "ticket": "T-6196",
      "order": "ORD-35325"
    },
    {
      "ticket": "T-6362",
      "order": "ORD-77504"
    },
    {
      "ticket": "T-6523",
      "order": "ORD-14789"
    },
    {
      "ticket": "T-7854",
      "order": "ORD-87042"
    },
    {
      "ticket": "T-8963",
      "order": "ORD-64963"
    }
  ]
}
EOF
