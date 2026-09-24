#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "ledger": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "catalog-api": {
      "component": "peer-resolver",
      "cause": "out-of-memory"
    },
    "fraud-score": {
      "component": "cache-warmer",
      "cause": "expired-credential"
    }
  }
}
EOF
