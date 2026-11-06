# ADR-0005 — Abstração de provedores de IA por portas e adaptadores

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Especialista em IA, Arquiteto de Software
- **Fase:** 1

## Contexto

O produto deve suportar diferentes provedores de LLM ao longo do tempo sem acoplar o domínio de agentes a SDKs ou formatos específicos. A troca de provedor não pode exigir reescrita das regras de negócio.

## Decisão

Definir uma porta interna (`AIProviderPort`) no domínio de agentes e implementar adaptadores de infraestrutura para cada provedor (OpenAI, Anthropic, Gemini, locais). O contrato interno cobre:

- Mensagens e papéis.
- Chamadas de ferramentas com schema validado.
- Tokens de entrada/saída e custo estimado.
- Latência, erro e `execution_id`.

O domínio não importa SDKs de provedores. A seleção de modelo é configuração (`ai_models`), não código.

## Consequências

**Positivas**

- Troca e convivência de provedores sem impacto no domínio.
- Testes com adaptadores falsos.
- Medição de custo uniforme.

**Negativas**

- Perda temporária de recursos exclusivos de um provedor.
- Necessidade de normalização de erros e formatos.
- Manutenção de múltiplos adaptadores.

## Regras de segurança

- Instruções e prompts não são código; nunca executados via `eval`/`exec`.
- Ferramentas só são invocadas se registradas e autorizadas para o tenant.
- Cálculos financeiros nunca são delegados ao modelo.
- Toda execução gera registro de uso e auditoria.

## Referências

- `docs/ARQUITETURA.md`, seção 6
- `docs/MODELO_DE_DADOS.md`, seção 3.3
