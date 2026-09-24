#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1516",
      "order": "ORD-51970"
    },
    {
      "ticket": "T-2600",
      "order": "ORD-11906"
    },
    {
      "ticket": "T-2899",
      "order": "ORD-14677"
    },
    {
      "ticket": "T-3194",
      "order": "ORD-98957"
    },
    {
      "ticket": "T-3254",
      "order": "ORD-45827"
    },
    {
      "ticket": "T-3315",
      "order": "ORD-51946"
    },
    {
      "ticket": "T-3965",
      "order": "ORD-62735"
    },
    {
      "ticket": "T-4134",
      "order": "ORD-92315"
    },
    {
      "ticket": "T-4996",
      "order": "ORD-75107"
    },
    {
      "ticket": "T-5726",
      "order": "ORD-95776"
    },
    {
      "ticket": "T-5742",
      "order": "ORD-53704"
    },
    {
      "ticket": "T-6079",
      "order": "ORD-78697"
    },
    {
      "ticket": "T-6830",
      "order": "ORD-44544"
    },
    {
      "ticket": "T-7333",
      "order": "ORD-96718"
    },
    {
      "ticket": "T-7499",
      "order": "ORD-23197"
    },
    {
      "ticket": "T-7756",
      "order": "ORD-73132"
    },
    {
      "ticket": "T-7940",
      "order": "ORD-95738"
    },
    {
      "ticket": "T-8004",
      "order": "ORD-25171"
    },
    {
      "ticket": "T-8345",
      "order": "ORD-30161"
    },
    {
      "ticket": "T-8381",
      "order": "ORD-15308"
    },
    {
      "ticket": "T-9414",
      "order": "ORD-42051"
    },
    {
      "ticket": "T-9508",
      "order": "ORD-69613"
    },
    {
      "ticket": "T-9555",
      "order": "ORD-27889"
    },
    {
      "ticket": "T-9965",
      "order": "ORD-93371"
    }
  ]
}
EOF
