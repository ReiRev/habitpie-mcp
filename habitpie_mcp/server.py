from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import register_tools

SERVER_NAME = "habitpie-mcp"
SERVER_INSTRUCTIONS = (
    "Habitify MCP server built on top of the habitipie Python client. "
    "This initial scaffold provides the server runtime and package structure; "
    "tool implementations are added in later issues."
)


def create_server() -> FastMCP:
    server = FastMCP(
        SERVER_NAME,
        instructions=SERVER_INSTRUCTIONS,
        json_response=True,
    )
    register_tools(server)
    return server


mcp = create_server()


def main() -> None:
    mcp.run(transport="stdio")
