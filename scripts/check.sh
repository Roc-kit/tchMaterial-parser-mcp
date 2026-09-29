#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    echo "Missing .venv. Run scripts/setup.sh first." >&2
    exit 1
fi

"$PYTHON" -m compileall -q src tests
"$PYTHON" -m pytest
git diff --check
git -C upstream/tchMaterial-parser diff --check

