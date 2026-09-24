#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "rate-limiter": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "payout-batch": {
      "component": "batch-assembler",
      "cause": "config-typo"
    },
    "authz": {
      "component": "queue-consumer",
      "cause": "config-typo"
    }
  }
}
EOF
