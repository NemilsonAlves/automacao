# ADR-0002 — Multi-tenancy com schema compartilhado e Row Level Security

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** CTO, Arquiteto de Banco de Dados, Especialista em Segurança
- **Fase:** 1

## Contexto

A plataforma atende empresas de segmentos variados com isolamento rigoroso de dados. É necessário escolher entre banco por tenant, schema por tenant ou schema compartilhado com `tenant_id`.

## Decisão

Adotar **schema compartilhado + coluna `tenant_id` + PostgreSQL Row Level Security (RLS)**, com:

- `tenant_id UUID NOT NULL` em todas as tabelas de cliente.
- `ENABLE` e `FORCE ROW LEVEL SECURITY`.
- Role da aplicação sem `BYPASSRLS` e sem propriedade das tabelas.
- Contexto definido via `set_config('app.tenant_id', :tenant_id, true)` dentro da transação (`SET LOCAL`).
- Tenant derivado da sessão autenticada no backend, nunca do cliente.
- Operações de SuperAdmin com contexto explícito, justificativa e auditoria.

## Consequências

**Positivas**

- Isolamento em profundidade (aplicação + banco).
- Operação e migrações simples com um único schema.
- Custo previsível para muitos tenants pequenos.

**Negativas**

- Exige disciplina em toda query e no gerenciamento de conexões.
- RLS adiciona custo de avaliação por linha.
- Erros de contexto podem causar negação indevida ou exposição se mal configurados.

## Mitigações

- Contexto sempre transacional (`SET LOCAL`), nunca `SET` de sessão.
- Testes de acesso cruzado entre tenants em `tests/tenant_isolation/`.
- Revisão de políticas e teste com role de aplicação real.
- Índices iniciados por `tenant_id`.

## Alternativas consideradas

- **Schema por tenant:** isolamento maior, porém migrações e operação complexas com muitos tenants.
- **Banco por tenant:** custo e operação inviáveis no estágio atual.

## Referências

- `docs/MODELO_DE_DADOS.md`, seção 8
- `backend/app/db/tenant_context.py`
