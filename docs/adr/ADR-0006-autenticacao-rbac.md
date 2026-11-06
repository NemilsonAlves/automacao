# ADR-0006 — Autenticação JWT com refresh rotativo e RBAC

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Especialista em Segurança, CTO, Arquiteto de Software
- **Fase:** 1 (decisão); implementação na Fase 2

## Contexto

A plataforma precisa autenticar usuários de plataforma e de tenants, com sessões seguras, revogação e autorização granular por módulo e operação.

## Decisão

- **Senhas:** hash Argon2id.
- **Acesso:** JWT de curta duração (access token), contendo `sub`, `session_id`, `tenant_id` (quando aplicável) e papéis.
- **Refresh:** token opaco ou JWT de refresh com hash armazenado, **rotação a cada uso**, revogação por família e detecção de reuso.
- **Sessões:** registro em `sessions`, com revogação e `last_seen_at`.
- **RBAC:** papéis (`SUPER_ADMIN`, `ADMIN`, `FINANCEIRO`, `SUPORTE`, `GERENTE_TENANT`, `OPERADOR`, `VISUALIZADOR`) e permissões no formato `module:action`.
- **Tenant:** derivado do token/sessão no backend, nunca de parâmetro do cliente.
- **Auditoria:** login, logout, revogação, mudança de papéis e operações sensíveis.

## Consequências

**Positivas**

- Sessões de curta duração reduzem impacto de vazamento.
- Rotação detecta reuso de refresh token.
- Permissões granulares alinhadas ao menor privilégio.

**Negativas**

- Complexidade de revogação e rotação.
- Necessidade de armazenamento seguro do refresh no cliente.
- Claims podem ficar desatualizadas até a expiração; permissões críticas são revalidadas no backend.

## Regras

1. A autorização é sempre aplicada no backend.
2. O frontend pode ocultar ações, mas não é fonte de verdade.
3. Tokens e senhas nunca são registrados em log.
4. Operações de SuperAdmin exigem auditoria e contexto explícito.

## Referências

- `docs/ARQUITETURA.md`, seção 5
- `docs/MODELO_DE_DADOS.md`, seção 3.4
