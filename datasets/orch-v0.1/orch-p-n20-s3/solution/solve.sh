#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "session-store": {
      "component": "cache-warmer",
      "cause": "config-typo"
    },
    "geo-lookup": {
      "component": "cache-warmer",
      "cause": "expired-credential"
    },
    "media-resizer": {
      "component": "config-loader",
      "cause": "disk-full"
    },
    "audit-trail": {
      "component": "config-loader",
      "cause": "expired-credential"
    },
    "search-indexer": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "ledger": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "email-digest": {
      "component": "metrics-shipper",
      "cause": "disk-full"
    },
    "authz": {
      "component": "config-loader",
      "cause": "expired-credential"
    },
    "notifier": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "webhook-relay": {
      "component": "schema-migrator",
      "cause": "out-of-memory"
    },
    "billing-sync": {
      "component": "token-refresher",
      "cause": "expired-credential"
    },
    "catalog-api": {
      "component": "blob-writer",
      "cause": "disk-full"
    },
    "feed-builder": {
      "component": "config-loader",
      "cause": "expired-credential"
    },
    "invoice-render": {
      "component": "cache-warmer",
      "cause": "out-of-memory"
    },
    "export-worker": {
      "component": "cache-warmer",
      "cause": "out-of-memory"
    },
    "quota-keeper": {
      "component": "cache-warmer",
      "cause": "config-typo"
    },
    "rate-limiter": {
      "component": "blob-writer",
      "cause": "out-of-memory"
    },
    "payout-batch": {
      "component": "queue-consumer",
      "cause": "expired-credential"
    },
    "fraud-score": {
      "component": "blob-writer",
      "cause": "expired-credential"
    },
    "thumbnailer": {
      "component": "peer-resolver",
      "cause": "dns-failure"
    }
  }
}
EOF
