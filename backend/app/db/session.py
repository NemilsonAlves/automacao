"""Criação preguiçosa do engine e fábrica de sessões assíncronas."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


def _build_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Retorna o engine assíncrono do processo (criado sob demanda)."""
    return _build_engine(get_settings())


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Retorna a fábrica de sessões assíncronas."""
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependência do FastAPI que fornece uma sessão por requisição."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def dispose_engine() -> None:
    """Descarta o engine e libera o pool no encerramento da aplicação."""
    if get_engine.cache_info().currsize == 0:
        return
    await get_engine().dispose()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
