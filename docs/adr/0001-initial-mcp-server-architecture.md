# ADR 0001: Initial MCP Server Architecture For habitpie-mcp

## Status

Accepted

## Context

`habitipie` already provides a typed Python client for Habitify API v2, including:

- resource-oriented entry points through `HabitipyClient`
- request and response models based on Pydantic
- `httpx` transport setup
- `X-API-Key` authentication handling
- Habitify-specific error mapping

This repository exists to expose that client through the Model Context Protocol.

The main design question is whether `habitpie-mcp` should:

1. re-implement the Habitify API directly, or
2. wrap `habitipie` as the integration layer and focus on MCP concerns

## Decision

`habitpie-mcp` will be a thin MCP adapter over `habitipie`.

This repository will not duplicate Habitify HTTP endpoint logic unless there is a proven gap in `habitipie` that blocks the MCP surface.

## Rationale

Wrapping `habitipie` keeps the responsibilities clear:

- `habitipie` owns HTTP transport, request serialization, response validation, and API-specific errors
- `habitpie-mcp` owns MCP tool design, argument normalization, result shaping, and runtime packaging

This reduces maintenance cost, keeps behavior aligned with the existing client, and avoids creating two independent integrations with the same upstream API.

## Goals

- provide a useful MCP server for Habitify with a small and predictable tool surface
- keep the server strongly typed and easy for LLM clients to call
- ship value incrementally, starting with read-only operations
- preserve a clear mapping between MCP tools and `habitipie` resource methods

## Non-Goals

- re-generating a full server from the Habitify OpenAPI document
- exposing every upstream endpoint in the first release
- designing a custom transport or bespoke HTTP wrapper around Habitify
- creating a broad natural-language orchestration layer inside the server itself

## High-Level Architecture

The server should be organized into a thin set of layers.

### 1. MCP entrypoint

Responsibilities:

- initialize `FastMCP`
- define server metadata and instructions
- register tools
- expose `stdio` first, with optional `streamable-http` later

### 2. Configuration

Responsibilities:

- load required environment variables such as `HABITIFY_API_KEY`
- validate startup configuration early
- optionally allow base URL and timeout overrides for development

### 3. Client factory

Responsibilities:

- create and close `HabitipyClient`
- centralize dependency construction
- keep transport ownership explicit

This should stay small. The server should not create a second API abstraction on top of `habitipie` unless repeated logic proves it necessary.

### 4. Tool modules

Responsibilities:

- define MCP-facing tool arguments
- perform lightweight normalization, such as converting ISO date strings into `date` objects
- call the corresponding `habitipie` resource methods
- return structured results suitable for MCP clients

### 5. Error translation

Responsibilities:

- surface `habitipie` and `httpx` exceptions with MCP-friendly tool errors
- preserve the reason for authentication, not found, rate limit, validation, and timeout failures

## Tool Design Principles

### Keep the MCP surface narrower than the underlying client

The MCP layer is for model-driven use. It should not blindly mirror every method on day one.

Initial emphasis:

- tools that are easy to call correctly
- tools that give immediate value in assistant workflows
- tools with small, legible schemas

### Prefer flattened, MCP-friendly arguments

LLM-facing tools should accept simple inputs where possible.

Examples:

- accept `start_date: str | None` and `end_date: str | None` rather than raw Python `date` objects
- accept small scalar parameters before introducing deeply nested payloads

Nested request models should be introduced later only when they remain understandable and necessary.

### Preserve structured outputs

When possible, tools should return structured data derived from `habitipie` models rather than only freeform text.

This improves:

- downstream tool chaining
- client rendering
- agent reliability

### Treat destructive operations carefully

Delete, archive, or irreversible actions should be introduced later and should require explicit confirmation arguments instead of relying on ambiguous natural-language intent.

## Initial Public Surface

The first implementation slice should expose the following read-only tools:

- `list_habits`
- `get_habit`
- `list_areas`
- `get_habit_journal`
- `get_habit_statistics`

These map directly onto already clear `habitipie` resource behavior and provide broad read access without destructive side effects.

## Deferred Surface

The next slice should focus on small write operations with simple request shapes:

- `create_log`
- `complete_log`
- `fail_log`
- `skip_log`
- `list_notes`
- `create_note`

More complex mutations should be deferred until the simpler operations establish the server conventions:

- habit create and update
- area create and update
- note update and delete
- archive and delete flows

## Suggested Package Shape

The exact file tree can evolve, but the initial shape should stay close to this:

```text
habitpie_mcp/
  __init__.py
  server.py
  config.py
  client.py
  errors.py
  tools/
    __init__.py
    habits.py
    areas.py
    journal.py
    statistics.py
    logs.py
    notes.py
tests/
  test_server.py
  test_tools_habits.py
  test_tools_areas.py
```

If this proves too granular for the first slice, combine nearby tool modules, but do not collapse everything into one large `server.py`.

## Runtime Strategy

### Initial runtime

- use `FastMCP`
- run through `stdio`
- support local development with `mcp dev`

### Later runtime

- add `streamable-http` when deployment requirements justify it
- keep the same tool contracts across transports

## Dependency Strategy

- use `habitipie` as a dependency, not vendored source
- pin a compatible version once the first implementation is stable
- only use a Git dependency temporarily if required client changes have not yet shipped

## Validation Strategy

The server should be validated at three levels.

### 1. Unit tests

Mock `HabitipyClient` or its resource methods to verify:

- tool argument normalization
- tool-to-client method mapping
- error translation
- confirmation handling for destructive actions

### 2. Lightweight integration tests

Exercise the MCP server registration and selected tool calls end-to-end where practical.

### 3. Manual MCP verification

Use local MCP development tooling to confirm:

- tool discovery
- input schema clarity
- output structure
- error readability

## Delivery Order

Implementation should proceed in small slices.

1. project scaffold and packaging
2. configuration and client factory
3. read-only tools for habits, areas, journal, and statistics
4. tests for the first tool set
5. write tools for logs and notes
6. destructive actions with explicit confirmations
7. optional HTTP transport and deployment packaging

## Workflow Decision

This repository should use an issue-first workflow.

Rules:

- architecture and delivery decisions land on `main` first
- implementation work is split into focused GitHub issues
- each issue is implemented on a dedicated branch
- branches should stay narrow and independently reviewable

Suggested branch naming:

- `feat/issue-<number>-scaffold`
- `feat/issue-<number>-read-tools`
- `feat/issue-<number>-logs-notes`

## Consequences

### Positive

- less duplicated API logic
- faster initial delivery
- clearer alignment with `habitipie`
- smaller reviewable implementation slices

### Tradeoffs

- `habitpie-mcp` depends on `habitipie` release cadence for some API changes
- some `habitipie` request models may be too rich for direct MCP exposure and will need wrapper schemas
- the MCP layer still needs careful error and confirmation design even if transport logic is reused

## Follow-Up

After this ADR lands, the next actions are:

1. create implementation issues from the delivery order
2. scaffold the package and local development workflow
3. implement the first read-only tool slice on a feature branch