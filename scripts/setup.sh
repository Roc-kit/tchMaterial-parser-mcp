#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

git submodule update --init --recursive

if command -v uv >/dev/null 2>&1; then
    if [[ ! -x ".venv/bin/python" ]]; then
        uv venv .venv
    fi
    uv pip install --python .venv/bin/python -e ./upstream/tchMaterial-parser
    uv pip install --python .venv/bin/python -e ".[dev]"
else
    if [[ ! -x ".venv/bin/python" ]]; then
        python3 -m venv .venv
    fi
    .venv/bin/python -m pip install -e ./upstream/tchMaterial-parser
    .venv/bin/python -m pip install -e ".[dev]"
fi

.venv/bin/python -m pytest

echo
echo "Ready:"
echo "  $ROOT/scripts/run-mcp.sh"


