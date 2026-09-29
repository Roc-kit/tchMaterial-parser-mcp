#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="$ROOT/.venv/bin/tchmaterial-parser-mcp"

if [[ ! -x "$SERVER" ]]; then
    echo "MCP environment is not ready. Run scripts/setup.sh first." >&2
    exit 1
fi

exec "$SERVER"

