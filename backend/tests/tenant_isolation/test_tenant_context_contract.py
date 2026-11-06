"""Contratos do contexto de tenant.

O teste de acesso cruzado real exige PostgreSQL com RLS aplicada e role de
aplicação sem BYPASSRLS. Ele será implementado e executado na FASE 2.
"""

from __future__ import annotations

import pytest
from app.db.tenant_context import (
    RESET_TENANT_CONTEXT,
    SET_SUPERADMIN_CONTEXT,
    SET_TENANT_CONTEXT,
)
from sqlalchemy import TextClause


def test_contexto_usa_parametros_vinculados() -> None:
    assert isinstance(SET_TENANT_CONTEXT, TextClause)
    assert ":tenant_id" in str(SET_TENANT_CONTEXT)
    assert ":is_superadmin" in str(SET_SUPERADMIN_CONTEXT)


def test_contexto_e_local_a_transacao() -> None:
    for statement in (
        SET_TENANT_CONTEXT,
        SET_SUPERADMIN_CONTEXT,
        RESET_TENANT_CONTEXT,
    ):
        assert ", true)" in str(statement)


@pytest.mark.skip(
    reason="Requer PostgreSQL com RLS e role de aplicação; será implementado na FASE 2"
)
def test_tenant_a_nao_acessa_dados_do_tenant_b() -> None:
    raise AssertionError("Teste de isolamento real pendente da FASE 2")
