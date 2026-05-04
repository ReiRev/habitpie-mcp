from __future__ import annotations

from collections.abc import Sequence

from mcp.server.fastmcp import FastMCP

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.errors import translate_tool_error


def list_areas() -> Sequence[object]:
    try:
        with create_habitipy_client() as client:
            return client.areas.list()
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def register_area_tools(server: FastMCP) -> None:
    server.tool()(list_areas)
