from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from habitpie_mcp.server import SERVER_INSTRUCTIONS, SERVER_NAME, create_server


def test_create_server_returns_fastmcp_instance() -> None:
    server = create_server()

    assert isinstance(server, FastMCP)
    assert server.name == SERVER_NAME
    assert server.instructions == SERVER_INSTRUCTIONS
