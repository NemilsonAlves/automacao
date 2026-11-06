# ADR-0007 — Núcleo de billing desacoplado de provedores e ledger append-only

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Especialista em Billing, CTO, Arquiteto de Software
- **Fase:** 1 (decisão); implementação nas Fases 9–10

## Contexto

A plataforma precisa cobrar por recorrência, pedido, atendimento, utilização, operação, modelos híbridos e contratos personalizados. O provedor de pagamento pode variar (Asaas, Stripe, outros) sem que o domínio financeiro dependa dele.

## Decisão

Separar o domínio financeiro em três camadas:

1. **Billing core** — contratos, assinaturas, ciclos, eventos faturáveis, faturas e itens.
2. **Payments** — recebimento, estornos, alocações, conciliação.
3. **Payment provider adapters** — implementações de `PaymentProviderPort` para cada provedor.

Regras:

- Eventos financeiros são **append-only** e imutáveis.
- `idempotency_key` única previne cobrança duplicada.
- Webhooks são assinados, verificados e deduplicados (`webhook_events`).
- Faturamento não depende do provedor para existir.
- **Preço contratado**, **valor faturado** e **dinheiro recebido** são grandezas distintas.
- Nenhum dado sensível de cartão é armazenado.

## Consequências

**Positivas**

- Troca de provedor sem reescrever regras de cobrança.
- Auditoria e conciliação confiáveis.
- Suporte a múltiplos modelos de cobrança e componentes por plano.

**Negativas**

- Mais entidades e fluxos a manter.
- Necessidade de conciliação e tratamento de divergências.
- Complexidade de idempotência e reprocessamento de webhooks.

## Alternativas consideradas

- **Billing nativo do provedor:** rejeitado por acoplamento e limitação de modelos híbridos.
- **Processamento de cartão próprio:** rejeitado por risco e regulação (PCI DSS).

## Referências

- `docs/ARQUITETURA.md`, seção 7
- `docs/MODELO_DE_DADOS.md`, seção 3.6
