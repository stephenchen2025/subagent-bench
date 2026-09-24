#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "sms-gateway": {
      "component": "http-frontend",
      "cause": "dns-failure"
    },
    "returns-desk": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "review-moderator": {
      "component": "token-refresher",
      "cause": "dns-failure"
    },
    "catalog-api": {
      "component": "cache-warmer",
      "cause": "dns-failure"
    },
    "sso-bridge": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "chat-router": {
      "component": "cache-warmer",
      "cause": "disk-full"
    },
    "webhook-relay": {
      "component": "peer-resolver",
      "cause": "disk-full"
    },
    "email-digest": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "consent-log": {
      "component": "peer-resolver",
      "cause": "out-of-memory"
    },
    "thumbnailer": {
      "component": "batch-assembler",
      "cause": "disk-full"
    },
    "schema-registry": {
      "component": "queue-consumer",
      "cause": "dns-failure"
    },
    "authz": {
      "component": "peer-resolver",
      "cause": "dns-failure"
    },
    "session-store": {
      "component": "metrics-shipper",
      "cause": "out-of-memory"
    },
    "key-vault": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "survey-collector": {
      "component": "peer-resolver",
      "cause": "dns-failure"
    },
    "feed-builder": {
      "component": "cache-warmer",
      "cause": "disk-full"
    },
    "audit-trail": {
      "component": "cache-warmer",
      "cause": "config-typo"
    },
    "quota-keeper": {
      "component": "batch-assembler",
      "cause": "out-of-memory"
    },
    "cost-reporter": {
      "component": "token-refresher",
      "cause": "expired-credential"
    },
    "cart-merge": {
      "component": "queue-consumer",
      "cause": "expired-credential"
    },
    "billing-sync": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "price-watch": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "notifier": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "media-resizer": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "geo-lookup": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "fraud-score": {
      "component": "token-refresher",
      "cause": "disk-full"
    },
    "export-worker": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "backup-rotator": {
      "component": "token-refresher",
      "cause": "config-typo"
    },
    "dns-updater": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "invoice-render": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "cdn-purger": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "loyalty-points": {
      "component": "metrics-shipper",
      "cause": "dns-failure"
    },
    "pdf-stamper": {
      "component": "config-loader",
      "cause": "config-typo"
    },
    "shipment-tracker": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "payout-batch": {
      "component": "cache-warmer",
      "cause": "expired-credential"
    },
    "job-reaper": {
      "component": "http-frontend",
      "cause": "config-typo"
    },
    "search-indexer": {
      "component": "cache-warmer",
      "cause": "disk-full"
    },
    "tax-calc": {
      "component": "queue-consumer",
      "cause": "dns-failure"
    }
  }
}
EOF
