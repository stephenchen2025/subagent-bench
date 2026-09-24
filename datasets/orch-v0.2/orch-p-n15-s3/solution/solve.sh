#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "notifier": {
      "component": "token-refresher",
      "cause": "disk-full"
    },
    "geo-lookup": {
      "component": "cache-warmer",
      "cause": "disk-full"
    },
    "chat-router": {
      "component": "metrics-shipper",
      "cause": "disk-full"
    },
    "cost-reporter": {
      "component": "cache-warmer",
      "cause": "expired-credential"
    },
    "search-indexer": {
      "component": "queue-consumer",
      "cause": "disk-full"
    },
    "backup-rotator": {
      "component": "queue-consumer",
      "cause": "out-of-memory"
    },
    "price-watch": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "cart-merge": {
      "component": "schema-migrator",
      "cause": "out-of-memory"
    },
    "payout-batch": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "email-digest": {
      "component": "config-loader",
      "cause": "disk-full"
    },
    "webhook-relay": {
      "component": "token-refresher",
      "cause": "dns-failure"
    },
    "pdf-stamper": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "key-vault": {
      "component": "schema-migrator",
      "cause": "out-of-memory"
    },
    "export-worker": {
      "component": "queue-consumer",
      "cause": "expired-credential"
    },
    "ledger-archiver": {
      "component": "token-refresher",
      "cause": "dns-failure"
    }
  }
}
EOF
