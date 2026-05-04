from __future__ import annotations

from collections.abc import Sequence

from habitipie import HabitNoteCreateRequest, MoodLevel
from mcp.server.fastmcp import FastMCP

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.errors import translate_tool_error


def list_notes(habit_id: str) -> Sequence[object]:
    try:
        with create_habitipy_client() as client:
            return client.habits.list_notes(habit_id)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def create_note(
    habit_id: str,
    content: str,
    mood_level: str | None = None,
    photos: list[str] | None = None,
) -> object:
    try:
        with create_habitipy_client() as client:
            request = HabitNoteCreateRequest(
                content=content,
                moodLevel=None if mood_level is None else MoodLevel(mood_level),
                photos=photos,
            )
            return client.habits.create_note(habit_id, request)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def register_note_tools(server: FastMCP) -> None:
    server.tool()(list_notes)
    server.tool()(create_note)
