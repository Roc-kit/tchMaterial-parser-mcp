#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    echo "Missing .venv. Run scripts/setup.sh first." >&2
    exit 1
fi

"$PYTHON" - <<'PY'
import asyncio

from mcp import Client
from mcp.client.stdio import StdioServerParameters


async def main() -> None:
    params = StdioServerParameters(
        command="/home/cislunar/App/tchMaterial-parser-mcp/scripts/run-mcp.sh"
    )
    async with Client(params) as client:
        search = await client.call_tool(
            "search_materials",
            {"query": "小学 数学 人教版 五年级 上册", "limit": 1},
        )
        assert not search.is_error
        material = search.structured_content["materials"][0]
        resolved = await client.call_tool(
            "resolve_material",
            {"resource_id_or_url": material["resource_id"]},
        )
        assert not resolved.is_error
        assert resolved.structured_content["resource_count"] >= 1
        print(material["title"])
        print(resolved.structured_content["resources"][0]["file_format"])


asyncio.run(main())
PY

