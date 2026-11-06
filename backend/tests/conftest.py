"""Fixtures compartilhadas da suíte de testes."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    """Evita que configuração memoizada vaze entre testes."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
