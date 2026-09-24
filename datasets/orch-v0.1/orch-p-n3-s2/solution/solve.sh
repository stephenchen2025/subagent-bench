#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > answer.json <<'EOF'
{
  "services": {
    "authz": {
      "component": "blob-writer",
      "cause": "dns-failure"
    },
    "feed-builder": {
      "component": "schema-migrator",
      "cause": "out-of-memory"
    },
    "search-indexer": {
      "component": "token-refresher",
      "cause": "out-of-memory"
    }
  }
}
EOF
