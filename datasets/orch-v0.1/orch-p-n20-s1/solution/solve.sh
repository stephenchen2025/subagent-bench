#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "session-store": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "fraud-score": {
      "component": "batch-assembler",
      "cause": "config-typo"
    },
    "authz": {
      "component": "http-frontend",
      "cause": "dns-failure"
    },
    "webhook-relay": {
      "component": "peer-resolver",
      "cause": "config-typo"
    },
    "feed-builder": {
      "component": "metrics-shipper",
      "cause": "out-of-memory"
    },
    "payout-batch": {
      "component": "http-frontend",
      "cause": "dns-failure"
    },
    "rate-limiter": {
      "component": "blob-writer",
      "cause": "disk-full"
    },
    "invoice-render": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "billing-sync": {
      "component": "http-frontend",
      "cause": "disk-full"
    },
    "quota-keeper": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "thumbnailer": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "email-digest": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "notifier": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "ledger": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "search-indexer": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "audit-trail": {
      "component": "schema-migrator",
      "cause": "disk-full"
    },
    "media-resizer": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "catalog-api": {
      "component": "config-loader",
      "cause": "expired-credential"
    },
    "export-worker": {
      "component": "peer-resolver",
      "cause": "config-typo"
    },
    "geo-lookup": {
      "component": "config-loader",
      "cause": "out-of-memory"
    }
  }
}
EOF
