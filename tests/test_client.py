from __future__ import annotations

from habitpie_mcp.client import create_habitipy_client
from habitpie_mcp.config import Settings


def test_create_habitipy_client_uses_explicit_settings() -> None:
    settings = Settings(
        api_key="test-key",
        base_url="https://example.test/v2",
        timeout=12.5,
    )

    with create_habitipy_client(settings) as client:
        assert client.habits is not None
        assert str(client._client.base_url) == "https://example.test/v2/"
        assert client._client.headers["X-API-Key"] == "test-key"
        assert client._client.timeout.connect == 12.5


def test_create_habitipy_client_closes_owned_client() -> None:
    client_ref = None

    with create_habitipy_client(Settings(api_key="test-key")) as client:
        client_ref = client
        assert client._client.is_closed is False

    assert client_ref is not None
    assert client_ref._client.is_closed is True
