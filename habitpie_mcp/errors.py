from __future__ import annotations

from datetime import date

import httpx
from habitipie.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ResponseDecodeError,
)


def parse_iso_date(value: str | None, *, field_name: str) -> date | None:
    if value is None:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be an ISO date in YYYY-MM-DD format."
        ) from exc


def translate_tool_error(exc: Exception) -> Exception:
    if isinstance(exc, AuthenticationError):
        return RuntimeError(f"Habitify authentication failed: {exc}")
    if isinstance(exc, NotFoundError):
        return RuntimeError(f"Habitify resource not found: {exc}")
    if isinstance(exc, RateLimitError):
        return RuntimeError(f"Habitify rate limit exceeded: {exc}")
    if isinstance(exc, ResponseDecodeError):
        return RuntimeError(f"Habitify returned an invalid response payload: {exc}")
    if isinstance(exc, httpx.TimeoutException):
        return RuntimeError(f"Habitify request timed out: {exc}")

    return exc


def require_confirmation(*, confirm: bool, action_name: str) -> None:
    if not confirm:
        raise ValueError(
            f"{action_name} requires confirm=True because it is a destructive action."
        )
