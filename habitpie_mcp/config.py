from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from os import environ

DEFAULT_HABITIFY_BASE_URL = "https://api.habitify.me/v2"
DEFAULT_HABITIFY_TIMEOUT = 10.0


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    api_key: str | None
    base_url: str = DEFAULT_HABITIFY_BASE_URL
    timeout: float = DEFAULT_HABITIFY_TIMEOUT


def load_settings(
    env: Mapping[str, str] | None = None,
    *,
    require_api_key: bool = True,
) -> Settings:
    values = env or environ
    api_key = values.get("HABITIFY_API_KEY") or None
    base_url = (values.get("HABITIFY_BASE_URL") or DEFAULT_HABITIFY_BASE_URL).strip()
    timeout_raw = values.get("HABITIFY_TIMEOUT")

    if not base_url:
        raise ConfigurationError("HABITIFY_BASE_URL must not be empty.")

    timeout = DEFAULT_HABITIFY_TIMEOUT
    if timeout_raw:
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ConfigurationError(
                "HABITIFY_TIMEOUT must be a valid number."
            ) from exc

    if timeout <= 0:
        raise ConfigurationError("HABITIFY_TIMEOUT must be greater than 0.")

    if require_api_key and api_key is None:
        raise ConfigurationError("HABITIFY_API_KEY is required.")

    return Settings(api_key=api_key, base_url=base_url, timeout=timeout)
