# habitpie-mcp

MCP server for Habitify built on top of the `habitipie` Python client.

## Current Status

This repository currently tracks the architecture, delivery plan, and issue breakdown for the first implementation phase.

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

## Planned Initial Tool Surface

Read-only first:

- `list_habits`
- `get_habit`
- `list_areas`
- `get_habit_journal`
- `get_habit_statistics`

Write tools will follow in later issues:

- log creation and state transitions
- note listing and creation
- eventually richer habit and area mutations

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
python -m pip install -e .
```

Run the server over stdio:

```bash
uv run habitpie-mcp
```

Or, without `uv`:

```bash
python -m habitpie_mcp
```

For direct module execution:

```bash
uv run python -m habitpie_mcp
```

The current scaffold intentionally does not expose the Habitify tool surface yet. That work is tracked in later issues.