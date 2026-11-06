"""Testes da redação de campos sensíveis em logs."""

from __future__ import annotations

from app.core.logging import REDACTED, redact_sensitive


def test_redige_chaves_sensiveis() -> None:
    event: dict[str, object] = {
        "password": "segredo",
        "Authorization": "Bearer abc",
        "refresh_token": "xyz",
        "safe_field": "ok",
    }
    result = redact_sensitive(None, "info", event)
    assert result["password"] == REDACTED
    assert result["Authorization"] == REDACTED
    assert result["refresh_token"] == REDACTED
    assert result["safe_field"] == "ok"


def test_nao_altera_evento_sem_chaves_sensiveis() -> None:
    event: dict[str, object] = {"tenant_id": "abc", "action": "read"}
    assert redact_sensitive(None, "info", event) == event
