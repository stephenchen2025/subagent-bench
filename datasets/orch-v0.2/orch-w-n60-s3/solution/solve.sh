#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1608",
      "order": "ORD-27397"
    },
    {
      "ticket": "T-2049",
      "order": "ORD-22201"
    },
    {
      "ticket": "T-2482",
      "order": "ORD-31853"
    },
    {
      "ticket": "T-2535",
      "order": "ORD-27930"
    },
    {
      "ticket": "T-2586",
      "order": "ORD-96847"
    },
    {
      "ticket": "T-2909",
      "order": "ORD-34391"
    },
    {
      "ticket": "T-4116",
      "order": "ORD-52537"
    },
    {
      "ticket": "T-4861",
      "order": "ORD-54098"
    },
    {
      "ticket": "T-4962",
      "order": "ORD-33510"
    },
    {
      "ticket": "T-5207",
      "order": "ORD-57807"
    },
    {
      "ticket": "T-5346",
      "order": "ORD-41128"
    },
    {
      "ticket": "T-6230",
      "order": "ORD-34281"
    },
    {
      "ticket": "T-6420",
      "order": "ORD-16358"
    },
    {
      "ticket": "T-7380",
      "order": "ORD-15607"
    },
    {
      "ticket": "T-8582",
      "order": "ORD-60044"
    }
  ]
}
EOF
