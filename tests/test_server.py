import asyncio

from mcp import Client

from tchmaterial_parser_mcp.server import mcp


def test_server_exposes_expected_tools() -> None:
    async def run() -> set[str]:
        async with Client(mcp) as client:
            listed = await client.list_tools()
            return {tool.name for tool in listed.tools}

    names = asyncio.run(run())
    assert names == {
        "search_materials",
        "get_material",
        "resolve_material",
        "download_material",
    }

