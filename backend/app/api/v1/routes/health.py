"""Endpoints de saúde da aplicação."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.db.session import get_session_factory

router = APIRouter(prefix="/health", tags=["health"])
logger = structlog.get_logger(__name__)


@router.get("/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    """Indica que o processo está em execução."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def ready(response: Response) -> dict[str, Any]:
    """Verifica a conectividade com o banco de dados."""
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning(
            "database_readiness_check_failed",
            error_type=type(exc).__name__,
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "unavailable"}
    return {"status": "ready", "database": "ok"}
