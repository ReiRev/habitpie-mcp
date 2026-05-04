from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from habitipie import HabitipyClient

from .config import Settings, load_settings


@contextmanager
def create_habitipy_client(settings: Settings | None = None) -> Iterator[HabitipyClient]:
    runtime_settings = settings or load_settings()

    with HabitipyClient(
        api_key=runtime_settings.api_key,
        base_url=runtime_settings.base_url,
        timeout=runtime_settings.timeout,
    ) as client:
        yield client
