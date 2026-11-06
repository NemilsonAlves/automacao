"""Testes de integração dos endpoints de saúde (sem banco)."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient


def test_liveness_responde_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_headers_de_seguranca_sao_aplicados() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_docs_disponiveis_em_desenvolvimento() -> None:
    with TestClient(app) as client:
        response = client.get("/docs")
    assert response.status_code == 200
