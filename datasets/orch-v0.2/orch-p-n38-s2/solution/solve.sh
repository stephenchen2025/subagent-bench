#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "fraud-score": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "sms-gateway": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "consent-log": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "tax-calc": {
      "component": "queue-consumer",
      "cause": "disk-full"
    },
    "survey-collector": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "ledger": {
      "component": "schema-migrator",
      "cause": "disk-full"
    },
    "authz": {
      "component": "schema-migrator",
      "cause": "dns-failure"
    },
    "loyalty-points": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "schema-registry": {
      "component": "http-frontend",
      "cause": "expired-credential"
    },
    "sso-bridge": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "quota-keeper": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "price-watch": {
      "component": "batch-assembler",
      "cause": "out-of-memory"
    },
    "cdn-purger": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "rate-limiter": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "payout-batch": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "email-digest": {
      "component": "http-frontend",
      "cause": "dns-failure"
    },
    "cost-reporter": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "chat-router": {
      "component": "cache-warmer",
      "cause": "out-of-memory"
    },
    "dns-updater": {
      "component": "batch-assembler",
      "cause": "config-typo"
    },
    "export-worker": {
      "component": "peer-resolver",
      "cause": "dns-failure"
    },
    "cart-merge": {
      "component": "metrics-shipper",
      "cause": "dns-failure"
    },
    "ledger-archiver": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "inventory-sync": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "job-reaper": {
      "component": "blob-writer",
      "cause": "config-typo"
    },
    "audit-trail": {
      "component": "cache-warmer",
      "cause": "config-typo"
    },
    "search-indexer": {
      "component": "metrics-shipper",
      "cause": "out-of-memory"
    },
    "key-vault": {
      "component": "blob-writer",
      "cause": "expired-credential"
    },
    "label-printer": {
      "component": "batch-assembler",
      "cause": "out-of-memory"
    },
    "feed-builder": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "invoice-render": {
      "component": "http-frontend",
      "cause": "dns-failure"
    },
    "review-moderator": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "returns-desk": {
      "component": "http-frontend",
      "cause": "disk-full"
    },
    "geo-lookup": {
      "component": "peer-resolver",
      "cause": "out-of-memory"
    },
    "catalog-api": {
      "component": "metrics-shipper",
      "cause": "disk-full"
    },
    "shipment-tracker": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "thumbnailer": {
      "component": "token-refresher",
      "cause": "expired-credential"
    },
    "webhook-relay": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "media-resizer": {
      "component": "peer-resolver",
      "cause": "out-of-memory"
    }
  }
}
EOF
