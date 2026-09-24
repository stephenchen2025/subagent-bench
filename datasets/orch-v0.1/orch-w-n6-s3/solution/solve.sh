#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-2987",
      "order": "ORD-37399"
    },
    {
      "ticket": "T-8572",
      "order": "ORD-23356"
    }
  ]
}
EOF
