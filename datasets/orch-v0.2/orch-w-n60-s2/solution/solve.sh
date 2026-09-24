#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1210",
      "order": "ORD-18355"
    },
    {
      "ticket": "T-2237",
      "order": "ORD-56781"
    },
    {
      "ticket": "T-3436",
      "order": "ORD-44341"
    },
    {
      "ticket": "T-4263",
      "order": "ORD-78424"
    },
    {
      "ticket": "T-5031",
      "order": "ORD-64979"
    },
    {
      "ticket": "T-5933",
      "order": "ORD-66766"
    },
    {
      "ticket": "T-5975",
      "order": "ORD-57540"
    },
    {
      "ticket": "T-6339",
      "order": "ORD-72697"
    },
    {
      "ticket": "T-6640",
      "order": "ORD-58705"
    },
    {
      "ticket": "T-8899",
      "order": "ORD-35487"
    },
    {
      "ticket": "T-8958",
      "order": "ORD-94911"
    },
    {
      "ticket": "T-9240",
      "order": "ORD-80086"
    },
    {
      "ticket": "T-9631",
      "order": "ORD-86000"
    },
    {
      "ticket": "T-9691",
      "order": "ORD-44897"
    },
    {
      "ticket": "T-9786",
      "order": "ORD-76488"
    }
  ]
}
EOF
