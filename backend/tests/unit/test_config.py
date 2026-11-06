"""Testes da configuração da aplicação."""

from __future__ import annotations

import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_defaults_sao_seguros() -> None:
    settings = Settings(_env_file=None)
    assert settings.app_name == "AgencIA NTM API"
    assert settings.environment == "development"
    assert settings.jwt_secret is None
    assert settings.cors_origins == []


def test_cors_origins_aceita_lista_separada_por_virgula() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="http://localhost:3000, https://app.example.com",
    )
    assert settings.cors_origins == [
        "http://localhost:3000",
        "https://app.example.com",
    ]


def test_log_level_invalido_e_rejeitado() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="TRACE")
