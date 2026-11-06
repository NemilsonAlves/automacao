# ADR-0004 — Versionamento imutável de regras, prompts e planos

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Arquiteto de Software, Especialista em IA, CTO
- **Fase:** 1

## Contexto

Regras de negócio e prompts de agentes mudam com frequência e impactam diretamente o comportamento do sistema. Alterações in-place impedem auditoria, reprodução de incidentes e rollback seguro.

## Decisão

Toda configuração relevante é versionada:

- `business_rule_sets` → `business_rule_versions`
- `agent_definitions` → `agent_definition_versions`
- `plans` → `plan_versions`
- Campos, formulários e workflows seguem o mesmo padrão.

Versões publicadas são **imutáveis**. Alterações criam nova versão em `draft`. Publicação e rollback são operações explícitas, auditadas, com autor, data e changelog. A entidade pai mantém `current_version_id`.

## Consequências

**Positivas**

- Auditoria completa e reprodução de comportamento histórico.
- Rollback simples e seguro.
- Testes e simulações podem fixar versões.

**Negativas**

- Mais tabelas e complexidade de leitura.
- Crescimento de armazenamento.
- Necessidade de política de arquivamento de versões antigas.

## Regras

1. Nunca `UPDATE` no conteúdo de versão publicada.
2. Publicação valida o schema da versão.
3. Rollback republica uma versão anterior elegível.
4. Toda publicação gera evento de auditoria.

## Referências

- `docs/MODELO_DE_DADOS.md`, seção 6
