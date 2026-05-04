from __future__ import annotations

import pytest

from habitpie_mcp.config import (
    DEFAULT_HABITIFY_BASE_URL,
    DEFAULT_HABITIFY_TIMEOUT,
    ConfigurationError,
    load_settings,
)


def test_load_settings_requires_api_key_by_default() -> None:
    with pytest.raises(ConfigurationError, match="HABITIFY_API_KEY is required"):
        load_settings(env={})


def test_load_settings_reads_overrides() -> None:
    settings = load_settings(
        env={
            "HABITIFY_API_KEY": "test-key",
            "HABITIFY_BASE_URL": "https://example.test/v2",
            "HABITIFY_TIMEOUT": "12.5",
        }
    )

    assert settings.api_key == "test-key"
    assert settings.base_url == "https://example.test/v2"
    assert settings.timeout == 12.5


def test_load_settings_uses_defaults_when_optional_values_are_missing() -> None:
    settings = load_settings(env={"HABITIFY_API_KEY": "test-key"})

    assert settings.base_url == DEFAULT_HABITIFY_BASE_URL
    assert settings.timeout == DEFAULT_HABITIFY_TIMEOUT


def test_load_settings_rejects_invalid_timeout() -> None:
    with pytest.raises(ConfigurationError, match="HABITIFY_TIMEOUT must be a valid number"):
        load_settings(env={"HABITIFY_API_KEY": "test-key", "HABITIFY_TIMEOUT": "fast"})


def test_load_settings_rejects_non_positive_timeout() -> None:
    with pytest.raises(ConfigurationError, match="HABITIFY_TIMEOUT must be greater than 0"):
        load_settings(env={"HABITIFY_API_KEY": "test-key", "HABITIFY_TIMEOUT": "0"})
