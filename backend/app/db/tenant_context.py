"""Contexto de tenant para Row Level Security (RLS).

Regras de segurança:

- O contexto é aplicado com ``set_config(..., true)``, isto é, ``SET LOCAL``.
  Assim, o valor vale apenas para a transação corrente e não vaza entre
  requisições que reutilizam conexões do pool.
- O ``tenant_id`` é sempre enviado como parâmetro vinculado, nunca interpolado.
- O chamador deve estar dentro de uma transação antes de invocar
  ``apply_tenant_context``.
- Sem contexto definido, as políticas RLS negam acesso (fail-closed), exceto
  para o contexto explícito de SuperAdmin.

As funções abaixo não executam consultas de negócio e não abrem transações por
conta própria.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SET_TENANT_CONTEXT = text(
    "SELECT set_config('app.tenant_id', :tenant_id, true)"
)
SET_SUPERADMIN_CONTEXT = text(
    "SELECT set_config('app.is_superadmin', :is_superadmin, true)"
)
RESET_TENANT_CONTEXT = text(
    "SELECT set_config('app.tenant_id', '', true), "
    "set_config('app.is_superadmin', 'off', true)"
)


async def apply_tenant_context(
    session: AsyncSession,
    tenant_id: UUID,
    *,
    is_superadmin: bool = False,
) -> None:
    """Define o contexto de tenant na transação corrente."""
    await session.execute(
        SET_TENANT_CONTEXT, {"tenant_id": str(tenant_id)}
    )
    await session.execute(
        SET_SUPERADMIN_CONTEXT,
        {"is_superadmin": "on" if is_superadmin else "off"},
    )


async def clear_tenant_context(session: AsyncSession) -> None:
    """Limpa o contexto de tenant na transação corrente."""
    await session.execute(RESET_TENANT_CONTEXT)
