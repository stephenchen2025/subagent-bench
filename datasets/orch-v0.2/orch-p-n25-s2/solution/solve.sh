#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "sso-bridge": {
      "component": "peer-resolver",
      "cause": "out-of-memory"
    },
    "feed-builder": {
      "component": "queue-consumer",
      "cause": "out-of-memory"
    },
    "dns-updater": {
      "component": "queue-consumer",
      "cause": "config-typo"
    },
    "cost-reporter": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "thumbnailer": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "key-vault": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "export-worker": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    },
    "backup-rotator": {
      "component": "config-loader",
      "cause": "dns-failure"
    },
    "sms-gateway": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "survey-collector": {
      "component": "token-refresher",
      "cause": "expired-credential"
    },
    "audit-trail": {
      "component": "metrics-shipper",
      "cause": "expired-credential"
    },
    "inventory-sync": {
      "component": "http-frontend",
      "cause": "disk-full"
    },
    "session-store": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "notifier": {
      "component": "peer-resolver",
      "cause": "disk-full"
    },
    "consent-log": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "rate-limiter": {
      "component": "schema-migrator",
      "cause": "dns-failure"
    },
    "ledger": {
      "component": "queue-consumer",
      "cause": "dns-failure"
    },
    "job-reaper": {
      "component": "config-loader",
      "cause": "disk-full"
    },
    "email-digest": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "fraud-score": {
      "component": "config-loader",
      "cause": "out-of-memory"
    },
    "returns-desk": {
      "component": "schema-migrator",
      "cause": "disk-full"
    },
    "geo-lookup": {
      "component": "http-frontend",
      "cause": "expired-credential"
    },
    "promo-engine": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "tax-calc": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    },
    "pdf-stamper": {
      "component": "queue-consumer",
      "cause": "expired-credential"
    }
  }
}
EOF
