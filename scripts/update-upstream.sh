#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBMODULE="$ROOT/upstream/tchMaterial-parser"

cd "$ROOT"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Outer repository has uncommitted changes; refusing to update upstream." >&2
    exit 1
fi

git submodule update --init --recursive
git -C "$SUBMODULE" fetch origin main
git -C "$SUBMODULE" checkout --detach origin/main

if [[ -x "$ROOT/.venv/bin/python" ]]; then
    PYTHON="$ROOT/.venv/bin/python"
else
    PYTHON="python3"
fi

if command -v uv >/dev/null 2>&1 && [[ -x "$ROOT/.venv/bin/python" ]]; then
    uv pip install --python "$PYTHON" -e "$SUBMODULE"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
    "$PYTHON" -m pip install -e "$SUBMODULE"
fi

"$PYTHON" -m pytest tests/test_upstream_compat.py tests/test_layering.py

echo
echo "Upstream is now:"
git -C "$SUBMODULE" log -1 --oneline
echo
echo "Review the submodule pointer change with:"
echo "  git diff --submodule=log"

