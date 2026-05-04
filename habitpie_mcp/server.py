from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from .config import load_settings
from .tools import register_tools

SERVER_NAME = "habitpie-mcp"
SERVER_INSTRUCTIONS = (
    "Habitify MCP server built on top of the habitipie Python client. "
    "This initial scaffold provides the server runtime and package structure; "
    "tool implementations are added in later issues."
)
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8000
DEFAULT_MOUNT_PATH = "/mcp"
Transport = Literal["stdio", "streamable-http"]


def create_server() -> FastMCP:
    server = FastMCP(
        SERVER_NAME,
        instructions=SERVER_INSTRUCTIONS,
        json_response=True,
    )
    register_tools(server)
    return server


mcp = create_server()


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the habitpie MCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="Transport to expose. Defaults to stdio.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HTTP_HOST,
        help="Host to bind when using streamable HTTP transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_HTTP_PORT,
        help="Port to bind when using streamable HTTP transport.",
    )
    parser.add_argument(
        "--mount-path",
        default=DEFAULT_MOUNT_PATH,
        help="Mount path to use for streamable HTTP transport.",
    )
    return parser


def configure_server_runtime(
    server: FastMCP,
    *,
    transport: Transport,
    host: str,
    port: int,
    mount_path: str,
) -> None:
    if transport != "streamable-http":
        return

    server.settings.host = host
    server.settings.port = port
    server.settings.streamable_http_path = mount_path


def main(argv: Sequence[str] | None = None) -> None:
    load_settings()
    args = build_argument_parser().parse_args(argv)
    transport = cast(Transport, args.transport)
    configure_server_runtime(
        mcp,
        transport=transport,
        host=args.host,
        port=args.port,
        mount_path=args.mount_path,
    )
    mcp.run(
        transport=transport,
        mount_path=args.mount_path if transport == "streamable-http" else None,
    )
