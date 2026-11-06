"""Configuração de logging estruturado com redação de campos sensíveis."""

from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import EventDict, Processor

SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "password",
        "password_hash",
        "secret",
        "jwt",
        "access_token",
        "refresh_token",
        "api_key",
        "token",
        "card_number",
        "cvv",
    }
)

REDACTED = "[REDACTED]"


def redact_sensitive(
    _logger: object, _method_name: str, event_dict: EventDict
) -> EventDict:
    """Substitui valores de chaves sensíveis antes da emissão do log."""
    for key in list(event_dict):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = REDACTED
    return event_dict


def configure_logging(*, level: str = "INFO", json_logs: bool = False) -> None:
    """Configura structlog para saída JSON ou legível, sempre com redação."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact_sensitive,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=False)
    )
    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
