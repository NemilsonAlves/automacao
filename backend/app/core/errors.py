"""Erros de domínio e handlers HTTP padronizados."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Erro de aplicação com código estável e status HTTP associado."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "app_error",
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class TenantContextError(AppError):
    """Contexto de tenant ausente ou inválido."""

    def __init__(self, message: str = "Contexto de tenant inválido.") -> None:
        super().__init__(message, code="tenant_context_invalid", status_code=403)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra handlers para erros de domínio."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        payload: dict[str, Any] = {
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }
        if exc.details:
            payload["error"]["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=payload)
