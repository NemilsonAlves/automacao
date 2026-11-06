# AgencIA NTM — Modelo de Dados

**Produto:** AgencIA NTM — Neural Tech minds
**Fase:** 1 — Fundação arquitetural
**Banco:** PostgreSQL 16
**Status:** Modelo-alvo documentado; nenhuma tabela criada e nenhuma migração executada

> Este documento é a referência de modelagem para as fases seguintes. Ele descreve entidades, relacionamentos, cardinalidade, constraints, índices, versionamento, exclusão e isolamento multi-tenant. Nenhuma cobrança, autenticação ou funcionalidade de negócio é implementada na FASE 1.

---

## 1. Convenções gerais

| Tema | Convenção |
|---|---|
| Nome de tabela | `snake_case`, plural (`tenants`, `invoices`) |
| Chave primária | `id UUID` gerado no banco (`gen_random_uuid()`), exceto catálogos com chave natural |
| Chave estrangeira | `<entidade>_id` |
| Datas | `timestamptz`, sempre UTC |
| Dinheiro | `numeric(14,2)` + `currency char(3)` (ISO 4217); nunca `float` |
| Custo de IA | `numeric(18,8)` (precisão alta) + `currency` |
| Quantidades | `numeric(14,4)` quando fracionáveis; `bigint` quando inteiras |
| Configuração dinâmica | `jsonb` validado por schema Pydantic antes da persistência |
| Booleanos | `boolean NOT NULL DEFAULT false` |
| Texto | `text` com `CHECK` de tamanho quando necessário |
| Enums | `text` + `CHECK` ou tipos enum PostgreSQL para baixa cardinalidade e ciclo estável |
| Timestamps | `created_at`, `updated_at`; `deleted_at` quando soft delete |
| Auditoria de autor | `created_by`, `updated_by` (`uuid` de usuário, quando aplicável) |
| Isolamento | `tenant_id UUID NOT NULL` em toda tabela de cliente |
| Migrações | Alembic, versionadas e revisadas; nunca executadas em produção nesta fase |

### 1.1 Identificadores

- UUID v4 (`gen_random_uuid()`) para entidades de negócio.
- Chaves naturais estáveis (`key`, `slug`) para catálogos de plataforma, com `UNIQUE`.
- `execution_id` e `idempotency_key` são `text`/`uuid` únicos, para correlação e deduplicação.

### 1.2 Classificação de escopo

| Escopo | Descrição | Possui `tenant_id`? | RLS? |
|---|---|---|---|
| **Plataforma** | Segmentos, modelos operacionais, catálogo de módulos, planos, catálogo de ferramentas, provedores | Não | Não |
| **Tenant** | Empresa, usuários, agentes instanciados, contratos, assinaturas, faturas, pagamentos, uso, conhecimento | Sim | Sim |
| **Mista** | Usuários de plataforma (`tenant_id` nulo) e de tenant; auditoria com alvo opcional | Conforme caso | Conforme caso |

---

## 2. Núcleo conceitual: as cinco entidades que não se misturam

| Entidade | Pergunta que responde | Escopo | Tabela principal |
|---|---|---|---|
| **Segmento** | Que tipo de negócio é? | Plataforma | `segments` |
| **Modelo Operacional** | Como esse negócio funciona? | Plataforma | `operational_models` |
| **Agente** | Qual é o comportamento da IA? | Plataforma (definição) / Tenant (instância) | `agent_definitions` / `agents` |
| **Tenant** | Quem contrata a plataforma? | Tenant | `tenants` |
| **Plano Comercial** | O que foi contratado e como é cobrado? | Plataforma (catálogo) / Tenant (contrato/assinatura) | `plans` / `contracts` |

Regra: nenhuma dessas entidades é armazenada como campo de outra. Relacionamentos são por chave estrangeira explícita.

---

## 3. Catálogo de entidades

### 3.1 Segmentos e configuração de mercado (escopo plataforma)

#### `segments`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `name` | text | NOT NULL |
| `slug` | text | NOT NULL, UNIQUE, `^[a-z0-9-]+$` |
| `description` | text | NULL |
| `category` | text | NOT NULL |
| `icon` | text | NULL |
| `status` | text | NOT NULL, CHECK em (`draft`,`active`,`inactive`,`archived`) |
| `version` | integer | NOT NULL DEFAULT 1 |
| `config` | jsonb | NOT NULL DEFAULT `{}` |
| `created_by` | uuid | NULL |
| `created_at` / `updated_at` | timestamptz | NOT NULL |
| `archived_at` | timestamptz | NULL |

Índices: `UNIQUE(slug)`, `(status)`, `GIN(config jsonb_path_ops)` quando consultado.

#### `operational_models`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `segment_id` | uuid | FK → `segments.id`, NOT NULL, `ON DELETE RESTRICT` |
| `name` / `slug` | text | NOT NULL |
| `description` | text | NULL |
| `config` | jsonb | NOT NULL DEFAULT `{}` |
| `version` | integer | NOT NULL DEFAULT 1 |
| `status` | text | CHECK (`draft`,`active`,`inactive`,`archived`) |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraints: `UNIQUE(segment_id, slug)`.
Índices: `(segment_id)`, `(status)`.
Cardinalidade: 1 segmento → N modelos operacionais; 1 modelo → N tenants.

#### `modules` (catálogo de módulos)

| Coluna | Tipo | Regra |
|---|---|---|
| `key` | text | PK, estável (`catalog`, `orders`, `appointments`) |
| `name` / `description` | text | NOT NULL |
| `category` | text | NOT NULL |
| `status` | text | CHECK (`active`,`inactive`) |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

#### `segment_modules`

| Coluna | Tipo | Regra |
|---|---|---|
| `segment_id` | uuid | FK → `segments.id`, PK composta |
| `module_key` | text | FK → `modules.key`, PK composta |
| `is_enabled` | boolean | NOT NULL DEFAULT true |
| `config` | jsonb | NOT NULL DEFAULT `{}` |

#### `custom_field_definitions` e versões

- `custom_field_definitions(id, segment_id, key, label, field_type, is_required, config jsonb, status, current_version, created_at, updated_at)`
- `custom_field_versions(id, field_definition_id, version, schema jsonb, validation jsonb, options jsonb, changelog, created_by, created_at, published_at)`

Constraints: `UNIQUE(segment_id, key)`; `UNIQUE(field_definition_id, version)`.
Cardinalidade: 1 segmento → N campos; 1 campo → N versões imutáveis.

#### `form_definitions` / `workflow_definitions`

Ambos seguem o mesmo padrão versionado:

- `form_definitions(id, segment_id, operational_model_id, key, name, status, current_version, created_at, updated_at)`
- `form_versions(id, form_definition_id, version, schema jsonb, ui_schema jsonb, changelog, created_by, published_at)`
- `workflow_definitions(id, segment_id, key, name, status, current_version, created_at, updated_at)`
- `workflow_versions(id, workflow_definition_id, version, config jsonb, changelog, created_by, published_at)`

O `config` de workflow contém estados, transições permitidas, guardas e ações autorizadas (allowlist). Estados e transições são validados por schema, não executados como código.

### 3.2 Regras de negócio (escopo plataforma)

#### `business_rule_sets`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `segment_id` | uuid | FK → `segments.id`, NOT NULL |
| `key` | text | NOT NULL |
| `name` / `description` | text | NOT NULL / NULL |
| `current_version_id` | uuid | FK → `business_rule_versions.id`, NULL |
| `status` | text | CHECK (`draft`,`published`,`archived`) |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraint: `UNIQUE(segment_id, key)`.

#### `business_rule_versions` (imutável após publicação)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `rule_set_id` | uuid | FK → `business_rule_sets.id`, NOT NULL |
| `version` | integer | NOT NULL |
| `rules` | jsonb | NOT NULL — árvore de condições com operadores enumerados |
| `actions` | jsonb | NOT NULL — ações em allowlist |
| `status` | text | CHECK (`draft`,`published`,`archived`) |
| `changelog` | text | NULL |
| `created_by` / `published_by` | uuid | NOT NULL / NULL |
| `created_at` / `published_at` | timestamptz | NOT NULL / NULL |

Constraints: `UNIQUE(rule_set_id, version)`; versão publicada não sofre `UPDATE` de conteúdo.
Índices: `(rule_set_id, status)`, `(published_at)`.

> O motor de regras só aceita operadores e ações previamente registrados. Não há `eval`, expressão livre executável ou código fornecido pelo usuário.

### 3.3 Agentes de IA

#### `agent_definitions` (template reutilizável, escopo plataforma)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `segment_id` | uuid | FK → `segments.id`, NOT NULL |
| `operational_model_id` | uuid | FK → `operational_models.id`, NOT NULL |
| `name` / `slug` | text | NOT NULL |
| `description` | text | NULL |
| `status` | text | CHECK (`draft`,`published`,`archived`) |
| `current_version_id` | uuid | FK → `agent_definition_versions.id`, NULL |
| `created_by` | uuid | NULL |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraint: `UNIQUE(segment_id, slug)`.

#### `agent_definition_versions` (prompt versioning)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `agent_definition_id` | uuid | FK, NOT NULL |
| `version` | integer | NOT NULL |
| `personality` / `tone` | text | NULL |
| `system_instructions` | text | NOT NULL |
| `context` | text | NULL |
| `model_config` | jsonb | NOT NULL (provider, model, temperatura, limites) |
| `memory_config` | jsonb | NOT NULL DEFAULT `{}` |
| `safety_policy` | jsonb | NOT NULL DEFAULT `{}` |
| `handoff_policy` | jsonb | NOT NULL DEFAULT `{}` |
| `changelog` | text | NULL |
| `status` | text | CHECK (`draft`,`published`,`archived`) |
| `created_by` / `published_by` | uuid | NOT NULL / NULL |
| `created_at` / `published_at` | timestamptz | NOT NULL / NULL |

Constraints: `UNIQUE(agent_definition_id, version)`. Versão publicada imutável.
Índices: `(agent_definition_id, status)`, `(published_at)`.

#### `agents` (instância por tenant)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → `tenants.id`, NOT NULL, `ON DELETE RESTRICT` |
| `agent_definition_id` | uuid | FK, NOT NULL |
| `name` | text | NOT NULL |
| `status` | text | CHECK (`draft`,`active`,`paused`,`archived`) |
| `active_version_id` | uuid | FK → `agent_definition_versions.id`, NULL |
| `overrides` | jsonb | NOT NULL DEFAULT `{}` (somente campos permitidos) |
| `limits` | jsonb | NOT NULL DEFAULT `{}` |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Índices: `(tenant_id, status)`, `(agent_definition_id)`.
Constraints: a versão ativa deve pertencer à definição do agente (validação de aplicação + FK composta quando viável).

#### `ai_providers` (catálogo plataforma)

`id, key UNIQUE, name, status, config_schema jsonb, created_at, updated_at`

#### `ai_models`

`id, provider_id FK, key, display_name, context_window, input_price_per_1k numeric(18,8), output_price_per_1k numeric(18,8), currency, status, config jsonb`
Constraint: `UNIQUE(provider_id, key)`.

#### `tool_registry`

`id, key UNIQUE, name, description, input_schema jsonb, output_schema jsonb, risk_level, status, created_at, updated_at`

#### `agent_tools`

`agent_definition_version_id FK, tool_id FK, is_enabled, config jsonb` — PK composta.

#### `knowledge_sources` / `knowledge_documents` / `knowledge_chunks` (tenant)

- `knowledge_sources(id, tenant_id, name, source_type, uri, status, checksum, metadata jsonb, created_at, updated_at, deleted_at)`
- `knowledge_documents(id, tenant_id, knowledge_source_id, title, content_ref, metadata jsonb, status, created_at, deleted_at)`
- `knowledge_chunks(id, tenant_id, document_id, ordinal, content, embedding_ref, tokens, metadata jsonb, created_at)`

Constraints: `UNIQUE(tenant_id, knowledge_source_id, ordinal)` nos chunks.
Índices: `(tenant_id, status)`, `(knowledge_source_id)`, `(document_id)`.
Isolamento: RLS obrigatória; `tenant_id` repetido nas três tabelas para política direta e recuperação escopada.

#### `agent_knowledge_sources`

`agent_id, knowledge_source_id, is_enabled` — PK composta; validação de que ambos pertencem ao mesmo tenant.

#### `agent_memory`

`id, tenant_id, agent_id, conversation_id, scope, content_ref, expires_at, created_at` — retenção configurável; RLS obrigatória.

#### `conversations` / `messages` / `handoffs` (tenant)

- `conversations(id, tenant_id, agent_id, channel, external_ref, status, started_at, ended_at)`
- `messages(id, tenant_id, conversation_id, role, content_ref, input_tokens, output_tokens, created_at)`
- `handoffs(id, tenant_id, conversation_id, reason, status, assigned_to, created_at, resolved_at)`

Índices: `(tenant_id, started_at)`, `(conversation_id, created_at)`.

### 3.4 Tenants, usuários e acesso

#### `tenants`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `legal_name` | text | NOT NULL |
| `trade_name` | text | NULL |
| `document_type` | text | CHECK (`cnpj`,`cpf`,`other`) |
| `document_number` | text | NOT NULL, normalizado (somente dígitos) |
| `segment_id` | uuid | FK → `segments.id`, NOT NULL |
| `operational_model_id` | uuid | FK → `operational_models.id`, NOT NULL |
| `status` | text | CHECK (`pending`,`active`,`suspended`,`cancelled`) |
| `email` / `phone` | text | NULL |
| `timezone` | text | NOT NULL DEFAULT `America/Sao_Paulo` |
| `locale` | text | NOT NULL DEFAULT `pt-BR` |
| `metadata` | jsonb | NOT NULL DEFAULT `{}` |
| `created_at` / `updated_at` | timestamptz | NOT NULL |
| `suspended_at` / `cancelled_at` / `deleted_at` | timestamptz | NULL |

Constraints: `UNIQUE(document_type, document_number)`; `UNIQUE(email)` quando público.
Índices: `(segment_id)`, `(operational_model_id)`, `(status)`.

> O tenant é a raiz de isolamento. Todo dado operacional referencia `tenants.id` e é protegido por RLS.

#### `users`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → `tenants.id`, NULL para usuários de plataforma |
| `name` | text | NOT NULL |
| `email` | text | NOT NULL |
| `password_hash` | text | NOT NULL (Argon2id) |
| `status` | text | CHECK (`pending`,`active`,`suspended`,`disabled`) |
| `email_verified_at` | timestamptz | NULL |
| `last_login_at` | timestamptz | NULL |
| `created_at` / `updated_at` | timestamptz | NOT NULL |
| `deleted_at` | timestamptz | NULL |

Constraints: unicidade de e-mail normalizado (`lower(email)`); `CHECK (tenant_id IS NOT NULL OR is_platform_user)`, onde `is_platform_user` é coluna explícita.
Índices: `UNIQUE(lower(email))`, `(tenant_id, status)`.

#### RBAC

- `permissions(id, key UNIQUE, module_key, action, description)` — ex.: `segments:write`.
- `roles(id, tenant_id NULL, key, name, is_system, description)` — papéis de sistema com `tenant_id` nulo; papéis customizados por tenant.
- `role_permissions(role_id, permission_id)` — PK composta.
- `user_roles(user_id, role_id, tenant_id)` — PK composta; validação de coerência de tenant.
- Papéis de sistema: `SUPER_ADMIN`, `ADMIN`, `FINANCEIRO`, `SUPORTE`, `GERENTE_TENANT`, `OPERADOR`, `VISUALIZADOR`.

#### Sessões e refresh tokens

- `sessions(id, user_id, tenant_id, created_at, last_seen_at, revoked_at, ip, user_agent)`
- `refresh_tokens(id, session_id, user_id, token_hash, family_id, expires_at, revoked_at, replaced_by_id, reuse_detected_at)`

Constraints: `UNIQUE(token_hash)`; rotação obrigatória; detecção de reuso revoga a família.
Índices: `(user_id, revoked_at)`, `(family_id)`.

#### Auditoria e LGPD

- `audit_logs(id, tenant_id NULL, actor_user_id NULL, action, entity_type, entity_id, before jsonb, after jsonb, ip, user_agent, request_id, created_at)` — append-only.
- `consents(id, tenant_id, subject_type, subject_id, purpose, granted, policy_version, created_at, revoked_at)`.
- `data_requests(id, tenant_id, subject_type, subject_id, request_type, status, requested_at, completed_at, result_ref)` — exportação/exclusão.

`audit_logs` não sofre `UPDATE`/`DELETE` pela aplicação; retenção mínima definida por política.

### 3.5 Comercial: planos, contratos e assinaturas

#### `plans` (catálogo plataforma)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `name` / `slug` | text | NOT NULL, slug UNIQUE |
| `description` | text | NULL |
| `status` | text | CHECK (`draft`,`active`,`inactive`,`archived`) |
| `trial_days` | integer | NOT NULL DEFAULT 0, CHECK >= 0 |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

#### `plan_versions` (imutável após publicação)

`id, plan_id FK, version, status, config jsonb, changelog, created_by, published_by, created_at, published_at`
Constraint: `UNIQUE(plan_id, version)`.
Índice: `(plan_id, status)`.

#### `plan_components` (composição de cobrança)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `plan_version_id` | uuid | FK → `plan_versions.id`, NOT NULL |
| `billing_model` | text | CHECK (`monthly`,`annual`,`per_order`,`per_service`,`usage`,`per_operation`,`hybrid`,`custom`) |
| `unit` | text | NOT NULL |
| `unit_price` | numeric(14,2) | NOT NULL CHECK >= 0 |
| `currency` | char(3) | NOT NULL |
| `included_quantity` | numeric(14,4) | NOT NULL DEFAULT 0 (franquia) |
| `overage_price` | numeric(14,2) | NULL (excedente) |
| `config` | jsonb | NOT NULL DEFAULT `{}` |

Constraint: `CHECK (billing_model <> 'custom' OR config ? 'custom_terms')`.
Índice: `(plan_version_id)`.

#### `plan_entitlements`

`plan_version_id, module_key, limit_quantity, config jsonb` — PK composta; liga plano a módulos e limites.

#### `contracts` (tenant)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `plan_version_id` | uuid | FK, NOT NULL |
| `status` | text | CHECK (`draft`,`active`,`suspended`,`terminated`,`expired`) |
| `starts_at` / `ends_at` | timestamptz | NOT NULL / NULL |
| `renewal_type` | text | CHECK (`manual`,`monthly`,`annual`) |
| `currency` | char(3) | NOT NULL |
| `contracted_amount` | numeric(14,2) | NOT NULL — **preço contratado** |
| `discount_amount` | numeric(14,2) | NOT NULL DEFAULT 0 |
| `config` | jsonb | NOT NULL DEFAULT `{}` |
| `signed_at` | timestamptz | NULL |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Índices: `(tenant_id, status)`, `(plan_version_id)`.

#### `contract_items`

`id, contract_id, plan_component_id, quantity numeric(14,4), unit_price numeric(14,2), config jsonb`
Índice: `(contract_id)`.

#### `subscriptions` (tenant)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `contract_id` | uuid | FK, NOT NULL |
| `status` | text | CHECK (`trialing`,`active`,`past_due`,`suspended`,`cancelled`,`expired`) |
| `current_period_start` / `current_period_end` | timestamptz | NOT NULL |
| `billing_anchor_day` | integer | CHECK entre 1 e 28 |
| `cancel_at_period_end` | boolean | NOT NULL DEFAULT false |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraint: no máximo uma assinatura `active`/`trialing` por contrato (índice parcial único).
Índices: `(tenant_id, status)`, `(current_period_end)`.

#### `subscription_items`

`id, subscription_id, plan_component_id, quantity, unit_price, config jsonb`

### 3.6 Billing: faturas, eventos e pagamentos

> **Preço contratado ≠ valor faturado ≠ dinheiro recebido.** As três grandezas têm tabelas e ciclos de vida distintos.

#### `invoices`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `contract_id` / `subscription_id` | uuid | FK, NOT NULL |
| `number` | text | NOT NULL, único por tenant |
| `status` | text | CHECK (`draft`,`open`,`paid`,`partially_paid`,`overdue`,`void`,`uncollectible`) |
| `currency` | char(3) | NOT NULL |
| `subtotal` / `discount_total` / `total` | numeric(14,2) | NOT NULL |
| `amount_paid` | numeric(14,2) | NOT NULL DEFAULT 0 — **dinheiro recebido alocado** |
| `issued_at` / `due_at` / `paid_at` | timestamptz | NULL |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraints: `UNIQUE(tenant_id, number)`; `CHECK (amount_paid >= 0 AND amount_paid <= total)`.
Índices: `(tenant_id, status, due_at)`, `(status, due_at)`, `(subscription_id)`.

#### `invoice_items`

`id, invoice_id, tenant_id, source_type, source_id, description, quantity numeric(14,4), unit_price numeric(14,2), amount numeric(14,2), metadata jsonb`
Constraints: `CHECK (amount = quantity * unit_price)` (ou tolerância documentada); `CHECK (amount >= 0)`.
Índices: `(invoice_id)`, `(tenant_id, source_type, source_id)`.

#### `billable_events` (append-only, idempotente)

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `event_type` | text | NOT NULL |
| `source_type` / `source_id` | text / uuid | NOT NULL |
| `occurred_at` | timestamptz | NOT NULL |
| `quantity` | numeric(14,4) | NOT NULL CHECK >= 0 |
| `unit` | text | NOT NULL |
| `unit_price` | numeric(14,2) | NOT NULL CHECK >= 0 |
| `currency` | char(3) | NOT NULL |
| `status` | text | CHECK (`pending`,`invoiced`,`void`) |
| `invoice_item_id` | uuid | FK, NULL |
| `idempotency_key` | text | NOT NULL, UNIQUE |
| `payload` | jsonb | NOT NULL DEFAULT `{}` |
| `created_at` | timestamptz | NOT NULL |

Índices: `UNIQUE(idempotency_key)`, `(tenant_id, status, occurred_at)`, `(invoice_item_id)`.
Regra: nunca sofre `UPDATE` de valores; correção é evento de estorno/ajuste.

#### `payments`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `invoice_id` | uuid | FK, NULL |
| `provider` | text | NOT NULL |
| `provider_payment_id` | text | NOT NULL |
| `status` | text | CHECK (`pending`,`authorized`,`paid`,`failed`,`refunded`,`partially_refunded`) |
| `amount` | numeric(14,2) | NOT NULL CHECK > 0 |
| `currency` | char(3) | NOT NULL |
| `method` | text | NULL |
| `paid_at` | timestamptz | NULL |
| `metadata` | jsonb | NOT NULL DEFAULT `{}` |
| `created_at` / `updated_at` | timestamptz | NOT NULL |

Constraint: `UNIQUE(provider, provider_payment_id)`.
Índices: `(tenant_id, status)`, `(invoice_id)`.
Nenhum dado de cartão é armazenado.

#### `payment_allocations`

`payment_id, invoice_id, amount numeric(14,2)` — PK composta; soma alocada ≤ valor do pagamento.

#### `refunds` / `credits` / `credit_applications`

- `refunds(id, tenant_id, payment_id, amount, status, reason, created_at, processed_at)`
- `credits(id, tenant_id, amount, currency, source, remaining_amount, expires_at, status, created_at)`
- `credit_applications(credit_id, invoice_id, amount)` — PK composta.

#### `dunning_events`

`id, tenant_id, invoice_id, step, channel, status, sent_at, metadata jsonb`

#### `webhook_events` (idempotência)

`id, provider, external_event_id, event_type, payload jsonb, signature_valid, status, received_at, processed_at`
Constraint: `UNIQUE(provider, external_event_id)`.

#### `outbox_events`

`id, aggregate_type, aggregate_id, event_type, payload jsonb, status, attempts, available_at, created_at, processed_at`
Índices: `(status, available_at)`.

### 3.7 Utilização e custos de IA

#### `ai_usage_records`

| Coluna | Tipo | Regra |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK, NOT NULL |
| `agent_id` | uuid | FK, NOT NULL |
| `execution_id` | text | NOT NULL, UNIQUE |
| `provider_key` / `model_key` | text | NOT NULL |
| `input_tokens` / `output_tokens` / `cached_tokens` | bigint | NOT NULL DEFAULT 0 |
| `cost_estimate` | numeric(18,8) | NOT NULL DEFAULT 0 |
| `currency` | char(3) | NOT NULL |
| `latency_ms` | integer | NULL |
| `operation_type` | text | NOT NULL |
| `status` | text | CHECK (`success`,`error`,`timeout`) |
| `occurred_at` | timestamptz | NOT NULL |
| `metadata` | jsonb | NOT NULL DEFAULT `{}` |

Índices: `UNIQUE(execution_id)`, `(tenant_id, occurred_at)`, `(agent_id, occurred_at)`, `(provider_key, model_key)`.
Regra: append-only; sem `UPDATE` de custo (correção por novo registro de ajuste).

#### `usage_counters` (agregação de limites)

`tenant_id, period_start, period_end, metric, used_quantity, limit_quantity` — PK composta ou id próprio; atualização concorrente segura (upsert atômico).

### 3.8 Governança e plataforma

- `tenant_modules(tenant_id, module_key, is_enabled, source, config jsonb, updated_at)` — PK composta; `source` em (`plan`,`override`).
- `tenant_settings(tenant_id PK, settings jsonb, updated_at)`.
- `notifications(id, tenant_id NULL, user_id NULL, type, payload jsonb, read_at, created_at)`.
- `feature_flags(key, description, enabled, config jsonb, updated_at)`.

---

## 4. Relacionamentos e cardinalidade (resumo)

```
segments 1─N operational_models
segments 1─N custom_field_definitions 1─N custom_field_versions
segments 1─N business_rule_sets 1─N business_rule_versions
segments 1─N agent_definitions 1─N agent_definition_versions
tenants  N─1 segments
tenants  N─1 operational_models
tenants  1─N users
tenants  1─N agents  N─1 agent_definitions
tenants  1─N knowledge_sources 1─N knowledge_documents 1─N knowledge_chunks
plans     1─N plan_versions 1─N plan_components
tenants  1─N contracts  N─1 plan_versions
contracts 1─N subscriptions 1─N subscription_items
subscriptions 1─N invoices 1─N invoice_items
invoices  1─N payments (via payment_allocations)
tenants   1─N billable_events
tenants   1─N ai_usage_records
roles     1─N role_permissions; users N─N roles (user_roles)
```

Cardinalidades críticas:

- 1 tenant → N usuários; 1 usuário pode ter papéis em mais de um tenant somente se o modelo de identidade permitir (decisão da FASE 2).
- 1 agente (instância) → 1 definição; 1 definição → N instâncias em tenants distintos.
- 1 fatura → N itens; 1 pagamento → N alocações; 1 item → 1 evento faturável, no máximo.
- 1 assinatura → N faturas; 1 contrato → N assinaturas ao longo do tempo (histórico), com no máximo uma ativa.

---

## 5. Constraints e índices

### 5.1 Constraints transversais

- Toda FK possui índice explícito (PostgreSQL não cria automaticamente).
- `ON DELETE RESTRICT` para dados financeiros e contratuais; `CASCADE` apenas em dependências puramente internas e substituíveis.
- Unicidades sempre que possível **escopadas por tenant** (`UNIQUE(tenant_id, ...)`) para evitar colisão entre clientes.
- `CHECK` para valores monetários não negativos, quantidades e estados válidos.
- `CHECK` de coerência de tenant em tabelas com `tenant_id` redundante (documento/chunk) — validado na aplicação e por FK composta quando viável.

### 5.2 Índices padrão

| Padrão | Uso |
|---|---|
| `(tenant_id, created_at DESC)` | listagens cronológicas |
| `(tenant_id, status)` | filtros operacionais |
| `(tenant_id, <data de negócio>)` | relatórios e dashboards |
| `UNIQUE(tenant_id, <chave natural>)` | idempotência e unicidade |
| `GIN(config jsonb_path_ops)` | consultas em configuração JSONB |
| Índice parcial `WHERE status = 'active'` | catálogos e assinaturas |

---

## 6. Estratégia de versionamento

| Entidade | Estratégia |
|---|---|
| Segmento | `version` incremental + histórico em `segment_versions` (a detalhar na FASE 4) |
| Campo/formulário/workflow | definição + tabela de versões imutáveis |
| Regras de negócio | `business_rule_versions`, publicação explícita |
| Agente | `agent_definition_versions` (prompt e configuração) |
| Plano | `plan_versions` + componentes vinculados à versão |
| Contrato | versão por vigência e reajuste; alterações geram novo contrato ou aditivo |
| Config JSONB | schema versionado (`schema_version` dentro do JSON) |

Regras:

1. Versão publicada é imutável.
2. `current_version_id` aponta para a versão ativa.
3. Rollback é a republicação de uma versão anterior, não edição.
4. Toda publicação registra autor, data e changelog.

---

## 7. Políticas de exclusão e retenção

| Dado | Política |
|---|---|
| Segmento, plano, agente (definição) | Arquivar (`status=archived`), não excluir fisicamente |
| Tenant | Soft delete + anonimização após retenção legal; nunca exclusão física imediata |
| Usuário | Desativar; anonimizar mediante solicitação LGPD quando não houver base legal de retenção |
| Contrato, fatura, pagamento, evento faturável | Nunca excluir; estornar/retificar com novos registros |
| `ai_usage_records` | Append-only; retenção configurável para relatórios |
| `audit_logs` | Append-only; retenção mínima definida por política |
| Base de conhecimento | Exclusão física permitida após retenção, com purge agendado e trilha |
| Conversas/mensagens | Retenção configurável por tenant; anonimização |
| Consentimentos | Preservar histórico de concessão/revogação |

Soft delete usa `deleted_at` e índices parciais `WHERE deleted_at IS NULL`. Consultas padrão filtram registros excluídos.

---

## 8. Isolamento multi-tenant e RLS

### 8.1 Regras

1. Toda tabela de tenant possui `tenant_id UUID NOT NULL`.
2. RLS habilitada e forçada (`ENABLE` + `FORCE ROW LEVEL SECURITY`).
3. A role da aplicação não é proprietária das tabelas e não possui `BYPASSRLS`.
4. O contexto é definido com `SET LOCAL` dentro da transação.
5. O tenant nunca é aceito do frontend; é derivado da sessão assinada.

### 8.2 Política de referência (não executada nesta fase)

```sql
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents FORCE ROW LEVEL SECURITY;

CREATE POLICY agents_tenant_isolation ON agents
USING (
    current_setting('app.is_superadmin', true) = 'on'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
)
WITH CHECK (
    current_setting('app.is_superadmin', true) = 'on'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
);
```

### 8.3 Contexto de sessão

```sql
SELECT set_config('app.tenant_id', :tenant_id, true);
SELECT set_config('app.is_superadmin', :is_superadmin, true);
```

- `true` = escopo local à transação.
- `NULLIF(..., '')` evita erro de cast quando a variável não foi definida.
- Sem contexto definido, a política nega acesso (fail-closed), exceto superadmin explícito.
- Ao final da transação, o PostgreSQL descarta os valores locais; o pool não herda contexto.

### 8.4 Tabelas de plataforma

Não usam RLS. O acesso é controlado por RBAC e por casos de uso administrativos, com auditoria. Escritas de plataforma exigem papel `SUPER_ADMIN`.

---

## 9. Integridade financeira

1. Valores monetários em `numeric`, com moeda explícita; nunca `float`.
2. Eventos faturáveis e registros de uso são append-only.
3. `idempotency_key` única previne cobrança duplicada.
4. `payments` e `payment_allocations` conciliam dinheiro recebido com faturas.
5. `amount_paid` é derivado de alocações, não digitado livremente.
6. Estornos e créditos são movimentos próprios; nunca `UPDATE` destrutivo.
7. A IA não escreve nessas tabelas; somente casos de uso determinísticos.
8. Webhooks só aplicam efeito após verificação de assinatura e deduplicação.

---

## 10. Máquinas de estado (referência)

| Entidade | Estados |
|---|---|
| Tenant | `pending → active → suspended → active`; `active/suspended → cancelled` |
| Assinatura | `trialing → active → past_due → suspended → active`; `→ cancelled/expired` |
| Fatura | `draft → open → paid/partially_paid/overdue → void/uncollectible` |
| Pagamento | `pending → authorized → paid`; `paid → refunded/partially_refunded`; `pending → failed` |
| Versão de agente/regra | `draft → published → archived` |
| Evento faturável | `pending → invoiced`; `pending → void` |

Transições inválidas são rejeitadas no backend e cobertas por testes.

---

## 11. Decisões em aberto para fases seguintes

| # | Decisão | Fase |
|---|---|---|
| 1 | Unicidade de e-mail global vs. por tenant | 2 |
| 2 | Usuário com acesso a múltiplos tenants (membership) | 2 |
| 3 | Estratégia de retenção por segmento (saúde) | 12 |
| 4 | Versionamento de segmento em tabela própria vs. JSONB | 4 |
| 5 | Modelo de indexação vetorial da base de conhecimento (pgvector vs. externo) | 6 |
| 6 | Granularidade de `usage_counters` (diário/mensal) | 11 |
| 7 | Emissão fiscal (NFS-e) — fora do escopo inicial | 10 |
| 8 | Provedor de pagamento inicial e formato de conciliação | 10 |

---

**Fim do Modelo de Dados — FASE 1.**
