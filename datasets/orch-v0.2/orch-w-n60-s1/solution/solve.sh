#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-2450",
      "order": "ORD-80821"
    },
    {
      "ticket": "T-2621",
      "order": "ORD-52894"
    },
    {
      "ticket": "T-3128",
      "order": "ORD-14780"
    },
    {
      "ticket": "T-3422",
      "order": "ORD-40834"
    },
    {
      "ticket": "T-3745",
      "order": "ORD-98541"
    },
    {
      "ticket": "T-4140",
      "order": "ORD-97475"
    },
    {
      "ticket": "T-4869",
      "order": "ORD-56545"
    },
    {
      "ticket": "T-5326",
      "order": "ORD-52090"
    },
    {
      "ticket": "T-6326",
      "order": "ORD-44257"
    },
    {
      "ticket": "T-6622",
      "order": "ORD-42539"
    },
    {
      "ticket": "T-7045",
      "order": "ORD-76382"
    },
    {
      "ticket": "T-7883",
      "order": "ORD-84111"
    },
    {
      "ticket": "T-8647",
      "order": "ORD-67272"
    },
    {
      "ticket": "T-8677",
      "order": "ORD-26973"
    },
    {
      "ticket": "T-9286",
      "order": "ORD-59901"
    }
  ]
}
EOF
