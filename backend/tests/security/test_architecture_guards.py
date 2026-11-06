"""Guardas estruturais de segurança arquitetural."""

from __future__ import annotations

import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[2] / "app"

FORBIDDEN_PATTERNS = (
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\bos\.system\s*\("),
    re.compile(r"\bsubprocess\."),
)


def test_codigo_da_aplicacao_nao_executa_codigo_arbitrario() -> None:
    violations: list[str] = []
    for path in APP_DIR.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path.relative_to(APP_DIR)}: {pattern.pattern}")
    assert violations == []


def test_contexto_de_tenant_usa_set_config_local_e_parametros() -> None:
    source = (APP_DIR / "db" / "tenant_context.py").read_text(encoding="utf-8")
    assert "set_config('app.tenant_id', :tenant_id, true)" in source
    assert "set_config('app.is_superadmin', :is_superadmin, true)" in source
    assert "text(f" not in source
