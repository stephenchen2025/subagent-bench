#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "promo-engine": {
      "component": "peer-resolver",
      "cause": "expired-credential"
    },
    "rate-limiter": {
      "component": "queue-consumer",
      "cause": "dns-failure"
    },
    "review-moderator": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "cdn-purger": {
      "component": "http-frontend",
      "cause": "out-of-memory"
    },
    "backup-rotator": {
      "component": "token-refresher",
      "cause": "expired-credential"
    },
    "job-reaper": {
      "component": "schema-migrator",
      "cause": "dns-failure"
    },
    "cost-reporter": {
      "component": "schema-migrator",
      "cause": "expired-credential"
    },
    "feed-builder": {
      "component": "schema-migrator",
      "cause": "disk-full"
    },
    "geo-lookup": {
      "component": "token-refresher",
      "cause": "disk-full"
    },
    "returns-desk": {
      "component": "token-refresher",
      "cause": "config-typo"
    },
    "ledger-archiver": {
      "component": "blob-writer",
      "cause": "out-of-memory"
    },
    "payout-batch": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "media-resizer": {
      "component": "schema-migrator",
      "cause": "config-typo"
    },
    "session-store": {
      "component": "metrics-shipper",
      "cause": "disk-full"
    },
    "sso-bridge": {
      "component": "config-loader",
      "cause": "expired-credential"
    }
  }
}
EOF
