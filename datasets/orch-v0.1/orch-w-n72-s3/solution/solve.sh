#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1187",
      "order": "ORD-96535"
    },
    {
      "ticket": "T-1452",
      "order": "ORD-96828"
    },
    {
      "ticket": "T-1926",
      "order": "ORD-87782"
    },
    {
      "ticket": "T-2291",
      "order": "ORD-66924"
    },
    {
      "ticket": "T-2451",
      "order": "ORD-62341"
    },
    {
      "ticket": "T-2513",
      "order": "ORD-86924"
    },
    {
      "ticket": "T-3333",
      "order": "ORD-25413"
    },
    {
      "ticket": "T-3518",
      "order": "ORD-96943"
    },
    {
      "ticket": "T-4343",
      "order": "ORD-30291"
    },
    {
      "ticket": "T-4942",
      "order": "ORD-74191"
    },
    {
      "ticket": "T-5265",
      "order": "ORD-76097"
    },
    {
      "ticket": "T-5773",
      "order": "ORD-17868"
    },
    {
      "ticket": "T-6873",
      "order": "ORD-71231"
    },
    {
      "ticket": "T-7177",
      "order": "ORD-77872"
    },
    {
      "ticket": "T-8646",
      "order": "ORD-77135"
    },
    {
      "ticket": "T-8792",
      "order": "ORD-52797"
    },
    {
      "ticket": "T-9132",
      "order": "ORD-88812"
    },
    {
      "ticket": "T-9291",
      "order": "ORD-51972"
    }
  ]
}
EOF
