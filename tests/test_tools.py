from __future__ import annotations

import asyncio
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import date

import httpx
import pytest
from habitipie import HabitType
from habitipie.errors import NotFoundError

from habitpie_mcp import errors
from habitpie_mcp.server import create_server
from habitpie_mcp.tools import areas as area_tools
from habitpie_mcp.tools import habits as habit_tools


class StubHabitsResource:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def list(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list", (), kwargs))
        return {"data": [], "pagination": {"total": 0, "limit": 25, "offset": 0}}

    def get(self, habit_id: str) -> dict[str, str]:
        self.calls.append(("get", (habit_id,), {}))
        return {"id": habit_id}

    def journal(self, *, journal_date: date | None = None) -> Sequence[dict[str, str]]:
        self.calls.append(("journal", (), {"journal_date": journal_date}))
        return [{"id": "entry_1"}]

    def statistics(
        self,
        habit_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, object]:
        self.calls.append(
            (
                "statistics",
                (habit_id,),
                {"start_date": start_date, "end_date": end_date},
            )
        )
        return {"id": habit_id, "total_logs": 0}


class StubAreasResource:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def list(self) -> Sequence[dict[str, str]]:
        self.calls.append(("list", (), {}))
        return [{"id": "area_1"}]


class StubClient:
    def __init__(self) -> None:
        self.habits = StubHabitsResource()
        self.areas = StubAreasResource()


@contextmanager
def stub_client_context(stub_client: StubClient) -> Iterator[StubClient]:
    yield stub_client


def test_server_registers_read_only_tools() -> None:
    server = create_server()
    tools = asyncio.run(server.list_tools())

    assert [tool.name for tool in tools] == [
        "list_habits",
        "get_habit",
        "get_habit_journal",
        "get_habit_statistics",
        "list_areas",
    ]


def test_list_habits_forwards_expected_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        habit_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = habit_tools.list_habits(
        archived=False,
        area_id="area_1",
        habit_type="good",
        time_of_day="tod_1",
        limit=25,
        offset=0,
    )

    assert isinstance(result, dict)
    assert isinstance(result["pagination"], dict)
    assert result["pagination"]["limit"] == 25
    assert stub_client.habits.calls == [
        (
            "list",
            (),
            {
                "archived": False,
                "area_id": "area_1",
                "habit_type": HabitType.GOOD,
                "time_of_day": "tod_1",
                "limit": 25,
                "offset": 0,
            },
        )
    ]


def test_get_habit_statistics_parses_iso_dates(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        habit_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = habit_tools.get_habit_statistics(
        "habit_123",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert isinstance(result, dict)
    assert result["id"] == "habit_123"
    assert stub_client.habits.calls == [
        (
            "statistics",
            ("habit_123",),
            {
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 1, 31),
            },
        )
    ]


def test_get_habit_journal_parses_iso_date(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        habit_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = habit_tools.get_habit_journal(journal_date="2024-01-15")

    assert result == [{"id": "entry_1"}]
    assert stub_client.habits.calls == [
        ("journal", (), {"journal_date": date(2024, 1, 15)})
    ]


def test_list_areas_forwards_to_client(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        area_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = area_tools.list_areas()

    assert result == [{"id": "area_1"}]
    assert stub_client.areas.calls == [("list", (), {})]


def test_parse_iso_date_rejects_invalid_date() -> None:
    with pytest.raises(ValueError, match="journal_date must be an ISO date"):
        errors.parse_iso_date("2024/01/15", field_name="journal_date")


def test_translate_tool_error_maps_not_found_error() -> None:
    request = httpx.Request("GET", "https://api.habitify.me/v2/habits/missing")
    response = httpx.Response(404, request=request)
    exc = NotFoundError("missing habit", request=request, response=response)

    translated = errors.translate_tool_error(exc)

    assert isinstance(translated, RuntimeError)
    assert str(translated) == "Habitify resource not found: missing habit"