from __future__ import annotations

from collections.abc import Sequence

from habitipie import HabitType
from mcp.server.fastmcp import FastMCP

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.errors import (
    parse_iso_date,
    require_confirmation,
    translate_tool_error,
)


def list_habits(
    archived: bool | None = None,
    area_id: str | None = None,
    habit_type: str | None = None,
    time_of_day: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> object:
    try:
        with create_habitipy_client() as client:
            habit_type_value = None if habit_type is None else HabitType(habit_type)
            return client.habits.list(
                archived=archived,
                area_id=area_id,
                habit_type=habit_type_value,
                time_of_day=time_of_day,
                limit=limit,
                offset=offset,
            )
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def get_habit(habit_id: str) -> object:
    try:
        with create_habitipy_client() as client:
            return client.habits.get(habit_id)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def get_habit_journal(journal_date: str | None = None) -> Sequence[object]:
    try:
        with create_habitipy_client() as client:
            return client.habits.journal(
                journal_date=parse_iso_date(journal_date, field_name="journal_date")
            )
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def get_habit_statistics(
    habit_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> object:
    try:
        with create_habitipy_client() as client:
            return client.habits.statistics(
                habit_id,
                start_date=parse_iso_date(start_date, field_name="start_date"),
                end_date=parse_iso_date(end_date, field_name="end_date"),
            )
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def archive_habit(habit_id: str, *, confirm: bool = False) -> dict[str, object]:
    require_confirmation(confirm=confirm, action_name="archive_habit")

    try:
        with create_habitipy_client() as client:
            client.habits.archive(habit_id)
            return {
                "ok": True,
                "action": "archive_habit",
                "habit_id": habit_id,
            }
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def delete_habit(habit_id: str, *, confirm: bool = False) -> dict[str, object]:
    require_confirmation(confirm=confirm, action_name="delete_habit")

    try:
        with create_habitipy_client() as client:
            client.habits.delete(habit_id)
            return {
                "ok": True,
                "action": "delete_habit",
                "habit_id": habit_id,
            }
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def register_habit_tools(server: FastMCP) -> None:
    server.tool()(list_habits)
    server.tool()(get_habit)
    server.tool()(get_habit_journal)
    server.tool()(get_habit_statistics)
    server.tool()(archive_habit)
    server.tool()(delete_habit)
