# habitpie-mcp

MCP server for Habitify built on top of the `habitipie` Python client.

## Current Status

This repository now includes the first usable MCP server slice for Habitify.

The server will:

- reuse `habitipie` instead of re-implementing the Habitify HTTP API
- expose a small, typed MCP tool surface first
- start with read-only tools, then add write operations in small slices

## Source Of Truth

The primary design record is:

- [docs/adr/0001-initial-mcp-server-architecture.md](docs/adr/0001-initial-mcp-server-architecture.md)

Read that ADR before starting implementation work. It defines:

- scope and non-goals
- server architecture and module boundaries
- tool design principles
- phased delivery order
- testing and release expectations
- issue and branch workflow for this repository

## Runtime Configuration

The server reads these environment variables:

- `HABITIFY_API_KEY`: required API key for Habitify
- `HABITIFY_BASE_URL`: optional API base URL override
- `HABITIFY_TIMEOUT`: optional request timeout override in seconds

Example:

```bash
export HABITIFY_API_KEY="your-api-key"
export HABITIFY_TIMEOUT="10"
```

## Current Tool Surface

Currently implemented tools:

- `list_habits`
- `get_habit`
- `get_habit_journal`
- `get_habit_statistics`
- `list_areas`
- `create_log`
- `complete_log`
- `fail_log`
- `skip_log`
- `list_notes`
- `create_note`
- `archive_habit`
- `delete_habit`
- `delete_area`
- `delete_note`

Destructive tools require `confirm=True` and return structured success payloads instead of bare `None`.

## Tool Notes

- Date inputs are accepted as ISO strings in `YYYY-MM-DD` format.
- Enum-like inputs such as `habit_type`, `unit_symbol`, and `mood_level` are accepted as strings and normalized by the MCP layer.
- Error responses are translated into MCP-friendly runtime errors for auth, missing resources, rate limits, invalid upstream payloads, and timeouts.

## Remaining Work

Still pending from the initial plan:

- streamable HTTP transport
- additional docs and usage examples
- any future expansion beyond the current MCP tool surface

## Development Direction

Implementation should prefer:

- Python 3.10+
- `mcp[cli]` with `FastMCP`
- `habitipie` as the single Habitify API integration point
- typed request and response models
- small issue-sized changes merged incrementally

## Local Bootstrap

Use `uv` for local setup when available:

```bash
uv sync
```

If `uv` is not installed, use a standard editable install instead:

```bash
python -m pip install -e ".[dev]"
```

Run the server over stdio:

```bash
uv run habitpie-mcp
```

Run the server over streamable HTTP:

```bash
uv run habitpie-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Or, without `uv`:

```bash
python -m habitpie_mcp
```

Or, for streamable HTTP without `uv`:

```bash
python -m habitpie_mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

For direct module execution:

```bash
uv run python -m habitpie_mcp
```

Once the server is running, MCP clients should discover the current Habitify tool set automatically.

For streamable HTTP mode, the default MCP endpoint is `http://127.0.0.1:8000/mcp`.

## Example Operations

Typical tool calls look like this at the schema level:

- `list_habits(limit=25, offset=0)`
- `get_habit_statistics(habit_id="habit_123", start_date="2024-01-01", end_date="2024-01-31")`
- `create_log(habit_id="habit_123", unit_symbol="kM", value=5, target_date="2024-01-05")`
- `create_note(habit_id="habit_123", content="Solid run today", mood_level="high")`
- `archive_habit(habit_id="habit_123", confirm=True)`

## Quality Checks

This repository currently uses:

- `ruff` for formatting and linting
- `mypy` for static type checking
- `pytest` for tests

Run the local quality pass with `uv`:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
```

Or, without `uv`:

```bash
python -m ruff format .
python -m ruff check .
python -m mypy
python -m pytest
```

If you want the same checks before commits, install pre-commit hooks:

```bash
python -m pre_commit install
```
