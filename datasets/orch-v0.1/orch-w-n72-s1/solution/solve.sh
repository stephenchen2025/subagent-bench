#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1129",
      "order": "ORD-10359"
    },
    {
      "ticket": "T-2078",
      "order": "ORD-67521"
    },
    {
      "ticket": "T-3061",
      "order": "ORD-81042"
    },
    {
      "ticket": "T-3579",
      "order": "ORD-90827"
    },
    {
      "ticket": "T-4418",
      "order": "ORD-13894"
    },
    {
      "ticket": "T-4488",
      "order": "ORD-34079"
    },
    {
      "ticket": "T-4558",
      "order": "ORD-85323"
    },
    {
      "ticket": "T-5277",
      "order": "ORD-55530"
    },
    {
      "ticket": "T-5554",
      "order": "ORD-97809"
    },
    {
      "ticket": "T-5555",
      "order": "ORD-28723"
    },
    {
      "ticket": "T-6750",
      "order": "ORD-39885"
    },
    {
      "ticket": "T-7515",
      "order": "ORD-41170"
    },
    {
      "ticket": "T-7617",
      "order": "ORD-71488"
    },
    {
      "ticket": "T-7818",
      "order": "ORD-53704"
    },
    {
      "ticket": "T-8723",
      "order": "ORD-97831"
    },
    {
      "ticket": "T-8982",
      "order": "ORD-80091"
    },
    {
      "ticket": "T-9052",
      "order": "ORD-13928"
    },
    {
      "ticket": "T-9280",
      "order": "ORD-76673"
    }
  ]
}
EOF
