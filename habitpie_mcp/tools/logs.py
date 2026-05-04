from __future__ import annotations

from habitipie import HabitLogActionRequest, HabitLogRequest, UnitSymbol
from mcp.server.fastmcp import FastMCP

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.errors import parse_iso_date, translate_tool_error


def create_log(
    habit_id: str,
    unit_symbol: str,
    value: float,
    target_date: str | None = None,
) -> object:
    try:
        with create_habitipy_client() as client:
            request = HabitLogRequest(
                unitSymbol=UnitSymbol(unit_symbol),
                value=value,
                targetDate=parse_iso_date(target_date, field_name="target_date"),
            )
            return client.habits.create_log(habit_id, request)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def complete_log(habit_id: str, target_date: str | None = None) -> object:
    try:
        with create_habitipy_client() as client:
            request = _build_log_action_request(target_date)
            return client.habits.complete_log(habit_id, request)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def fail_log(habit_id: str, target_date: str | None = None) -> object:
    try:
        with create_habitipy_client() as client:
            request = _build_log_action_request(target_date)
            return client.habits.fail_log(habit_id, request)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def skip_log(habit_id: str, target_date: str | None = None) -> object:
    try:
        with create_habitipy_client() as client:
            request = _build_log_action_request(target_date)
            return client.habits.skip_log(habit_id, request)
    except Exception as exc:
        raise translate_tool_error(exc) from exc


def register_log_tools(server: FastMCP) -> None:
    server.tool()(create_log)
    server.tool()(complete_log)
    server.tool()(fail_log)
    server.tool()(skip_log)


def _build_log_action_request(target_date: str | None) -> HabitLogActionRequest | None:
    if target_date is None:
        return None

    return HabitLogActionRequest(
        targetDate=parse_iso_date(target_date, field_name="target_date")
    )
