#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "notifier": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "quota-keeper": {
      "component": "blob-writer",
      "cause": "expired-credential"
    },
    "fraud-score": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "search-indexer": {
      "component": "batch-assembler",
      "cause": "dns-failure"
    },
    "geo-lookup": {
      "component": "schema-migrator",
      "cause": "dns-failure"
    },
    "rate-limiter": {
      "component": "peer-resolver",
      "cause": "disk-full"
    },
    "billing-sync": {
      "component": "config-loader",
      "cause": "out-of-memory"
    },
    "session-store": {
      "component": "peer-resolver",
      "cause": "config-typo"
    },
    "export-worker": {
      "component": "cache-warmer",
      "cause": "out-of-memory"
    },
    "ledger": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    }
  }
}
EOF
