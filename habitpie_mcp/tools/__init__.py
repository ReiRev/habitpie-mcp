from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register_tools(server: FastMCP) -> None:
    """Register MCP tools on the provided server.

    Tool modules are added in later issues. Keeping registration here avoids
    growing the entrypoint into the long-term integration surface.
    """

    del server
