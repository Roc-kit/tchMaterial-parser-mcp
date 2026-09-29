"""Local stdio MCP server."""

from __future__ import annotations

from mcp.server import MCPServer

from .tools import download_material, get_material, resolve_material, search_materials


mcp = MCPServer("tchMaterial-parser-mcp")
mcp.tool()(search_materials)
mcp.tool()(get_material)
mcp.tool()(resolve_material)
mcp.tool()(download_material)


def main() -> None:
    """Run the local server over stdio."""

    mcp.run()


if __name__ == "__main__":
    main()
