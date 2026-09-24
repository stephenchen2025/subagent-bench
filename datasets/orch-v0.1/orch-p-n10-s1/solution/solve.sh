#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "webhook-relay": {
      "component": "blob-writer",
      "cause": "disk-full"
    },
    "email-digest": {
      "component": "queue-consumer",
      "cause": "disk-full"
    },
    "catalog-api": {
      "component": "schema-migrator",
      "cause": "out-of-memory"
    },
    "geo-lookup": {
      "component": "metrics-shipper",
      "cause": "out-of-memory"
    },
    "fraud-score": {
      "component": "blob-writer",
      "cause": "config-typo"
    },
    "rate-limiter": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "media-resizer": {
      "component": "blob-writer",
      "cause": "out-of-memory"
    },
    "authz": {
      "component": "token-refresher",
      "cause": "dns-failure"
    },
    "feed-builder": {
      "component": "token-refresher",
      "cause": "disk-full"
    },
    "search-indexer": {
      "component": "batch-assembler",
      "cause": "expired-credential"
    }
  }
}
EOF
