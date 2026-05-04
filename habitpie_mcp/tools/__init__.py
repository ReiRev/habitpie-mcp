from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .areas import register_area_tools
from .habits import register_habit_tools
from .logs import register_log_tools
from .notes import register_note_tools


def register_tools(server: FastMCP) -> None:
    register_habit_tools(server)
    register_area_tools(server)
    register_log_tools(server)
    register_note_tools(server)
