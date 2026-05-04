from __future__ import annotations

from collections.abc import Sequence

from mcp.server.fastmcp import FastMCP

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.errors import require_confirmation, translate_tool_error


def list_areas() -> Sequence[object]:
    try:
        with create_habitipy_client() as client:
            return client.areas.list()
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def delete_area(area_id: str, *, confirm: bool = False) -> dict[str, object]:
    require_confirmation(confirm=confirm, action_name="delete_area")

    try:
        with create_habitipy_client() as client:
            client.areas.delete(area_id)
            return {"ok": True, "action": "delete_area", "area_id": area_id}
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def register_area_tools(server: FastMCP) -> None:
    server.tool()(list_areas)
    server.tool()(delete_area)
