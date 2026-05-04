# Usage Guide

This guide covers the current `habitpie-mcp` runtime modes and the MCP tool surface that is implemented today.

## Requirements

- Python 3.10+
- a Habitify API key in `HABITIFY_API_KEY`
- dependencies installed with either `uv sync` or `python -m pip install -e ".[dev]"`

Set the minimum required environment variable:

```bash
export HABITIFY_API_KEY="your-api-key"
```

Optional overrides:

```bash
export HABITIFY_BASE_URL="https://api.habitify.me/v2"
export HABITIFY_TIMEOUT="10"
```

## Running Over STDIO

With `uv`:

```bash
uv run habitpie-mcp
```

Without `uv`:

```bash
python -m habitpie_mcp
```

Use this mode when the MCP host launches the server as a subprocess.

## Running Over Streamable HTTP

With `uv`:

```bash
uv run habitpie-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Without `uv`:

```bash
python -m habitpie_mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Defaults:

- host: `127.0.0.1`
- port: `8000`
- mount path: `/mcp`

Default MCP endpoint:

```text
http://127.0.0.1:8000/mcp
```

You can override the mount path:

```bash
python -m habitpie_mcp --transport streamable-http --mount-path /habitify
```

## Implemented Tools

Read and query tools:

- `list_habits`
- `get_habit`
- `get_habit_journal`
- `get_habit_statistics`
- `list_areas`
- `list_notes`

Write tools:

- `create_log`
- `complete_log`
- `fail_log`
- `skip_log`
- `create_note`

Destructive tools:

- `archive_habit`
- `delete_habit`
- `delete_area`
- `delete_note`

## Input Conventions

- Dates use `YYYY-MM-DD` strings.
- `habit_type`, `unit_symbol`, and `mood_level` are string inputs normalized by the MCP layer.
- Destructive tools require `confirm=True`.

## Example Tool Calls

Examples at the schema level:

```text
list_habits(limit=25, offset=0)
get_habit(habit_id="habit_123")
get_habit_statistics(habit_id="habit_123", start_date="2024-01-01", end_date="2024-01-31")
create_log(habit_id="habit_123", unit_symbol="kM", value=5, target_date="2024-01-05")
create_note(habit_id="habit_123", content="Solid run today", mood_level="high")
delete_note(habit_id="habit_123", note_id="note_1", confirm=True)
```

## Behavior Notes

- Tool discovery does not require live Habitify API calls.
- Most read and write tools call the upstream Habitify API through `habitipie`.
- Error messages are normalized for common upstream failures such as auth problems, missing resources, rate limits, timeouts, and invalid payloads.
- Destructive tools return small structured success payloads instead of `None`.# Usage Guide

This document describes how to run `habitpie-mcp`, connect to it, and call the
currently implemented Habitify tools.

## Prerequisites

Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Set your Habitify API key before starting the server:

```bash
export HABITIFY_API_KEY="your-api-key"
```

Optional runtime overrides:

```bash
export HABITIFY_BASE_URL="https://api.habitify.me/v2"
export HABITIFY_TIMEOUT="10"
```

## Run Over STDIO

Start the server for STDIO-based MCP clients:

```bash
python -m habitpie_mcp
```

This is the right mode for clients that spawn the server as a subprocess.

## Run Over Streamable HTTP

Start the server as an HTTP MCP endpoint:

```bash
python -m habitpie_mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

By default, the MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

You can change the mount path if needed:

```bash
python -m habitpie_mcp --transport streamable-http --host 127.0.0.1 --port 8000 --mount-path /habitify
```

That server will then be available at:

```text
http://127.0.0.1:8000/habitify
```

## Inspect With A Python MCP Client

The following snippet lists the available tools from the HTTP server:

```python
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main() -> None:
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([tool.name for tool in tools.tools])


asyncio.run(main())
```

## Current Tool Surface

### Read operations

- `list_habits`
- `get_habit`
- `get_habit_journal`
- `get_habit_statistics`
- `list_areas`
- `list_notes`

### Write operations

- `create_log`
- `complete_log`
- `fail_log`
- `skip_log`
- `create_note`

### Destructive operations

- `archive_habit`
- `delete_habit`
- `delete_area`
- `delete_note`

All destructive operations require `confirm=True`.

## Example Argument Shapes

### List habits

```json
{
  "limit": 25,
  "offset": 0,
  "archived": false,
  "habit_type": "good"
}
```

### Get statistics

```json
{
  "habit_id": "habit_123",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### Create a log

```json
{
  "habit_id": "habit_123",
  "unit_symbol": "kM",
  "value": 5,
  "target_date": "2024-01-05"
}
```

### Create a note

```json
{
  "habit_id": "habit_123",
  "content": "Solid run today",
  "mood_level": "high",
  "photos": ["https://example.com/photo1.jpg"]
}
```

### Archive a habit

```json
{
  "habit_id": "habit_123",
  "confirm": true
}
```

## Input Conventions

- Dates are accepted as ISO strings in `YYYY-MM-DD` format.
- `habit_type`, `unit_symbol`, and `mood_level` are accepted as strings and normalized in the MCP layer.
- Upstream Habitify and `httpx` failures are translated into MCP-friendly runtime errors.

## Notes On Validation

If you want a safe end-to-end smoke check without mutating real Habitify data, call a destructive tool without `confirm=True`.

Example:

```json
{
  "habit_id": "habit_123",
  "confirm": false
}
```

That validates MCP transport and tool execution without reaching the upstream delete or archive call.