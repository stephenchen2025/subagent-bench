#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "geo-lookup": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "shipment-tracker": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "webhook-relay": {
      "component": "queue-consumer",
      "cause": "out-of-memory"
    },
    "loyalty-points": {
      "component": "queue-consumer",
      "cause": "config-typo"
    },
    "price-watch": {
      "component": "schema-migrator",
      "cause": "disk-full"
    },
    "rate-limiter": {
      "component": "cache-warmer",
      "cause": "config-typo"
    },
    "ledger": {
      "component": "http-frontend",
      "cause": "expired-credential"
    },
    "session-store": {
      "component": "peer-resolver",
      "cause": "dns-failure"
    },
    "review-moderator": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "catalog-api": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "returns-desk": {
      "component": "queue-consumer",
      "cause": "out-of-memory"
    },
    "cdn-purger": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "quota-keeper": {
      "component": "batch-assembler",
      "cause": "disk-full"
    },
    "pdf-stamper": {
      "component": "blob-writer",
      "cause": "config-typo"
    },
    "key-vault": {
      "component": "token-refresher",
      "cause": "dns-failure"
    },
    "feed-builder": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "audit-trail": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "tax-calc": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "fraud-score": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "sms-gateway": {
      "component": "batch-assembler",
      "cause": "out-of-memory"
    },
    "chat-router": {
      "component": "blob-writer",
      "cause": "expired-credential"
    },
    "inventory-sync": {
      "component": "peer-resolver",
      "cause": "disk-full"
    },
    "notifier": {
      "component": "blob-writer",
      "cause": "out-of-memory"
    },
    "cart-merge": {
      "component": "blob-writer",
      "cause": "disk-full"
    },
    "media-resizer": {
      "component": "metrics-shipper",
      "cause": "disk-full"
    }
  }
}
EOF
