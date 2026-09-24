#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1879",
      "order": "ORD-41050"
    },
    {
      "ticket": "T-2863",
      "order": "ORD-88557"
    },
    {
      "ticket": "T-3212",
      "order": "ORD-97644"
    },
    {
      "ticket": "T-3400",
      "order": "ORD-88725"
    },
    {
      "ticket": "T-4055",
      "order": "ORD-47897"
    },
    {
      "ticket": "T-4514",
      "order": "ORD-20044"
    },
    {
      "ticket": "T-4771",
      "order": "ORD-85376"
    },
    {
      "ticket": "T-4810",
      "order": "ORD-95032"
    },
    {
      "ticket": "T-5104",
      "order": "ORD-17384"
    },
    {
      "ticket": "T-5265",
      "order": "ORD-63320"
    },
    {
      "ticket": "T-6258",
      "order": "ORD-10137"
    },
    {
      "ticket": "T-6841",
      "order": "ORD-89568"
    },
    {
      "ticket": "T-7713",
      "order": "ORD-52133"
    },
    {
      "ticket": "T-8027",
      "order": "ORD-44340"
    },
    {
      "ticket": "T-8598",
      "order": "ORD-82535"
    },
    {
      "ticket": "T-9130",
      "order": "ORD-89592"
    },
    {
      "ticket": "T-9686",
      "order": "ORD-48106"
    },
    {
      "ticket": "T-9766",
      "order": "ORD-12893"
    }
  ]
}
EOF
