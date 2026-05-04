from __future__ import annotations

from typing import Any

import pytest
from mcp.server.fastmcp import FastMCP

from habitpie_mcp import server
from habitpie_mcp.server import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_MOUNT_PATH,
    SERVER_INSTRUCTIONS,
    SERVER_NAME,
    build_argument_parser,
    configure_server_runtime,
    create_server,
)


def test_create_server_returns_fastmcp_instance() -> None:
    app = create_server()

    assert isinstance(app, FastMCP)
    assert app.name == SERVER_NAME
    assert app.instructions == SERVER_INSTRUCTIONS


def test_build_argument_parser_uses_expected_defaults() -> None:
    args = build_argument_parser().parse_args([])

    assert args.transport == "stdio"
    assert args.host == DEFAULT_HTTP_HOST
    assert args.port == DEFAULT_HTTP_PORT
    assert args.mount_path == DEFAULT_MOUNT_PATH


def test_configure_server_runtime_updates_http_settings() -> None:
    app = create_server()

    configure_server_runtime(
        app,
        transport="streamable-http",
        host="0.0.0.0",
        port=9000,
        mount_path="/habitify",
    )

    assert app.settings.host == "0.0.0.0"
    assert app.settings.port == 9000
    assert app.settings.streamable_http_path == "/habitify"


class DummySettings:
    def __init__(self) -> None:
        self.host = DEFAULT_HTTP_HOST
        self.port = DEFAULT_HTTP_PORT
        self.streamable_http_path = DEFAULT_MOUNT_PATH


class DummyServer:
    def __init__(self) -> None:
        self.settings = DummySettings()
        self.run_calls: list[dict[str, Any]] = []

    def run(self, *, transport: str, mount_path: str | None = None) -> None:
        self.run_calls.append({"transport": transport, "mount_path": mount_path})


def test_main_uses_stdio_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_server = DummyServer()
    monkeypatch.setattr(server, "mcp", dummy_server)
    monkeypatch.setattr(server, "load_settings", lambda: None)

    server.main([])

    assert dummy_server.run_calls == [{"transport": "stdio", "mount_path": None}]


def test_main_configures_streamable_http_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dummy_server = DummyServer()
    monkeypatch.setattr(server, "mcp", dummy_server)
    monkeypatch.setattr(server, "load_settings", lambda: None)

    server.main(
        [
            "--transport",
            "streamable-http",
            "--host",
            "0.0.0.0",
            "--port",
            "9000",
            "--mount-path",
            "/habitify",
        ]
    )

    assert dummy_server.settings.host == "0.0.0.0"
    assert dummy_server.settings.port == 9000
    assert dummy_server.settings.streamable_http_path == "/habitify"
    assert dummy_server.run_calls == [
        {"transport": "streamable-http", "mount_path": "/habitify"}
    ]
