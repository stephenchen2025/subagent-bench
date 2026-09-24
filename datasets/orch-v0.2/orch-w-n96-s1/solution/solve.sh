#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1659",
      "order": "ORD-46450"
    },
    {
      "ticket": "T-1730",
      "order": "ORD-14881"
    },
    {
      "ticket": "T-1840",
      "order": "ORD-11033"
    },
    {
      "ticket": "T-2010",
      "order": "ORD-96613"
    },
    {
      "ticket": "T-2160",
      "order": "ORD-74665"
    },
    {
      "ticket": "T-2209",
      "order": "ORD-70924"
    },
    {
      "ticket": "T-2272",
      "order": "ORD-59606"
    },
    {
      "ticket": "T-3107",
      "order": "ORD-47404"
    },
    {
      "ticket": "T-3289",
      "order": "ORD-96460"
    },
    {
      "ticket": "T-3340",
      "order": "ORD-74097"
    },
    {
      "ticket": "T-3849",
      "order": "ORD-33332"
    },
    {
      "ticket": "T-4068",
      "order": "ORD-51791"
    },
    {
      "ticket": "T-4318",
      "order": "ORD-99913"
    },
    {
      "ticket": "T-5328",
      "order": "ORD-13957"
    },
    {
      "ticket": "T-5536",
      "order": "ORD-67080"
    },
    {
      "ticket": "T-5649",
      "order": "ORD-24059"
    },
    {
      "ticket": "T-5854",
      "order": "ORD-63704"
    },
    {
      "ticket": "T-6718",
      "order": "ORD-15869"
    },
    {
      "ticket": "T-6960",
      "order": "ORD-47956"
    },
    {
      "ticket": "T-7882",
      "order": "ORD-99541"
    },
    {
      "ticket": "T-8236",
      "order": "ORD-63296"
    },
    {
      "ticket": "T-8254",
      "order": "ORD-68380"
    },
    {
      "ticket": "T-9141",
      "order": "ORD-29107"
    },
    {
      "ticket": "T-9606",
      "order": "ORD-67593"
    }
  ]
}
EOF
