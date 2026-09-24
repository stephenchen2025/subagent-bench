#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "matches": [
    {
      "ticket": "T-2418",
      "order": "ORD-14728"
    },
    {
      "ticket": "T-9561",
      "order": "ORD-76451"
    }
  ]
}
EOF
