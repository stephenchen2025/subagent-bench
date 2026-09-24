#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-1361",
      "order": "ORD-37240"
    },
    {
      "ticket": "T-1429",
      "order": "ORD-39508"
    },
    {
      "ticket": "T-1729",
      "order": "ORD-71646"
    },
    {
      "ticket": "T-1737",
      "order": "ORD-44804"
    },
    {
      "ticket": "T-2095",
      "order": "ORD-60886"
    },
    {
      "ticket": "T-2475",
      "order": "ORD-95195"
    },
    {
      "ticket": "T-2647",
      "order": "ORD-78271"
    },
    {
      "ticket": "T-3016",
      "order": "ORD-51432"
    },
    {
      "ticket": "T-3497",
      "order": "ORD-22863"
    },
    {
      "ticket": "T-3654",
      "order": "ORD-57538"
    },
    {
      "ticket": "T-4562",
      "order": "ORD-39981"
    },
    {
      "ticket": "T-4764",
      "order": "ORD-23448"
    },
    {
      "ticket": "T-4816",
      "order": "ORD-13773"
    },
    {
      "ticket": "T-4826",
      "order": "ORD-37082"
    },
    {
      "ticket": "T-6341",
      "order": "ORD-99723"
    },
    {
      "ticket": "T-6565",
      "order": "ORD-20214"
    },
    {
      "ticket": "T-7200",
      "order": "ORD-69184"
    },
    {
      "ticket": "T-7254",
      "order": "ORD-15003"
    },
    {
      "ticket": "T-7954",
      "order": "ORD-50539"
    },
    {
      "ticket": "T-8509",
      "order": "ORD-73025"
    },
    {
      "ticket": "T-8574",
      "order": "ORD-67675"
    },
    {
      "ticket": "T-8793",
      "order": "ORD-91160"
    },
    {
      "ticket": "T-8821",
      "order": "ORD-78763"
    },
    {
      "ticket": "T-9135",
      "order": "ORD-91504"
    }
  ]
}
EOF
