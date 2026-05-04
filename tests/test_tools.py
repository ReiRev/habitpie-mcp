from __future__ import annotations

import asyncio
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import date

import httpx
import pytest
from habitipie import (
    HabitLogActionRequest,
    HabitLogRequest,
    HabitNoteCreateRequest,
    HabitType,
    MoodLevel,
    UnitSymbol,
)
from habitipie.errors import NotFoundError

from habitpie_mcp import errors
from habitpie_mcp.server import create_server
from habitpie_mcp.tools import areas as area_tools
from habitpie_mcp.tools import habits as habit_tools
from habitpie_mcp.tools import logs as log_tools
from habitpie_mcp.tools import notes as note_tools


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

    def create_log(self, habit_id: str, request: HabitLogRequest) -> dict[str, str]:
        self.calls.append(("create_log", (habit_id, request), {}))
        return {"message": "Habit log created successfully"}

    def complete_log(
        self, habit_id: str, request: HabitLogActionRequest | None = None
    ) -> dict[str, str]:
        self.calls.append(("complete_log", (habit_id, request), {}))
        return {"message": "Habit marked as completed successfully"}

    def fail_log(
        self, habit_id: str, request: HabitLogActionRequest | None = None
    ) -> dict[str, str]:
        self.calls.append(("fail_log", (habit_id, request), {}))
        return {"message": "Habit marked as failed successfully"}

    def skip_log(
        self, habit_id: str, request: HabitLogActionRequest | None = None
    ) -> dict[str, str]:
        self.calls.append(("skip_log", (habit_id, request), {}))
        return {"message": "Habit marked as skipped successfully"}

    def list_notes(self, habit_id: str) -> Sequence[dict[str, str]]:
        self.calls.append(("list_notes", (habit_id,), {}))
        return [{"id": "note_1"}]

    def create_note(
        self, habit_id: str, request: HabitNoteCreateRequest
    ) -> dict[str, object]:
        self.calls.append(("create_note", (habit_id, request), {}))
        return {"id": "note_1", "content": request.content}


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
        "create_log",
        "complete_log",
        "fail_log",
        "skip_log",
        "list_notes",
        "create_note",
    ]


def test_list_habits_forwards_expected_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_create_log_builds_request_model(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        log_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = log_tools.create_log(
        "habit_123",
        unit_symbol="kM",
        value=5,
        target_date="2024-01-05",
    )

    assert result == {"message": "Habit log created successfully"}
    method_name, args, kwargs = stub_client.habits.calls[0]
    assert method_name == "create_log"
    assert kwargs == {}
    assert args[0] == "habit_123"
    assert isinstance(args[1], HabitLogRequest)
    assert args[1].unit_symbol == UnitSymbol.KM
    assert args[1].value == 5
    assert args[1].target_date == date(2024, 1, 5)


def test_complete_log_without_target_date_passes_none(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        log_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = log_tools.complete_log("habit_123")

    assert result == {"message": "Habit marked as completed successfully"}
    assert stub_client.habits.calls[0] == ("complete_log", ("habit_123", None), {})


def test_skip_log_with_target_date_builds_action_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        log_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = log_tools.skip_log("habit_123", target_date="2024-01-08")

    assert result == {"message": "Habit marked as skipped successfully"}
    method_name, args, kwargs = stub_client.habits.calls[0]
    assert method_name == "skip_log"
    assert kwargs == {}
    assert args[0] == "habit_123"
    assert isinstance(args[1], HabitLogActionRequest)
    assert args[1].target_date == date(2024, 1, 8)


def test_list_notes_forwards_to_client(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        note_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = note_tools.list_notes("habit_123")

    assert result == [{"id": "note_1"}]
    assert stub_client.habits.calls[0] == ("list_notes", ("habit_123",), {})


def test_create_note_builds_request_model(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_client = StubClient()
    monkeypatch.setattr(
        note_tools,
        "create_habitipy_client",
        lambda: stub_client_context(stub_client),
    )

    result = note_tools.create_note(
        "habit_123",
        content="Solid run today",
        mood_level="high",
        photos=["https://example.com/photo1.jpg"],
    )

    assert result == {"id": "note_1", "content": "Solid run today"}
    method_name, args, kwargs = stub_client.habits.calls[0]
    assert method_name == "create_note"
    assert kwargs == {}
    assert args[0] == "habit_123"
    assert isinstance(args[1], HabitNoteCreateRequest)
    assert args[1].content == "Solid run today"
    assert args[1].mood_level == MoodLevel.HIGH
    assert args[1].photos == ["https://example.com/photo1.jpg"]
