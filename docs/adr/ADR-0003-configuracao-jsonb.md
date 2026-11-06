# ADR-0003 — Configurações dinâmicas em JSONB com validação Pydantic

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Arquiteto de Software, Arquiteto de Banco de Dados, Engenheiro Python
- **Fase:** 1

## Contexto

Segmentos, modelos operacionais, campos, formulários, workflows e políticas variam por cliente. Criar colunas ou tabelas para cada variação geraria migrações constantes e acoplamento do código a segmentos específicos.

## Decisão

Persistir configurações dinâmicas em colunas **JSONB**, com:

- Schema Pydantic explícito por tipo de configuração.
- `schema_version` dentro do JSON para evolução controlada.
- Validação obrigatória antes da gravação.
- Índices GIN apenas onde houver consulta comprovada.
- Dados relacionais e financeiros permanecem em colunas tipadas.

JSONB é usado para **configuração**, não para dados transacionais críticos.

## Consequências

**Positivas**

- Novos segmentos e formulários sem alteração de schema.
- Evolução rápida de configuração.
- Flexibilidade por tenant e por segmento.

**Negativas**

- Integridade depende da validação na aplicação.
- Consultas e relatórios sobre JSON podem ser menos eficientes.
- Risco de esquemas divergentes sem versionamento.

## Mitigações

- Schemas versionados e validados.
- Testes de contrato para cada tipo de configuração.
- Proibição de JSONB para valores financeiros, quantidades e estados críticos.

## Referências

- `docs/MODELO_DE_DADOS.md`, seções 3 e 6
