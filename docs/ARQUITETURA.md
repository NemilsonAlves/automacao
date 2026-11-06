# AgencIA NTM — Arquitetura da Plataforma

**Produto:** AgencIA NTM — Neural Tech minds
**Fase:** 1 — Fundação arquitetural
**Status:** Aprovada como base para as fases seguintes
**Última atualização:** 06/11/2026

> Este documento define a arquitetura-alvo. Na FASE 1 apenas a fundação é materializada; os módulos de negócio existem como pacotes vazios, com fronteiras e dependências declaradas. Nenhuma funcionalidade de negócio foi implementada.

---

## 1. Visão geral

A AgencIA NTM é uma plataforma SaaS multi-tenant para criação, configuração, comercialização e operação de agentes de inteligência artificial para empresas de qualquer segmento.

O produto **não é um chatbot** e **não é um conjunto de aplicações por segmento**. É um núcleo único, dirigido por dados de configuração (segmentos, modelos operacionais, campos, regras, workflows, módulos, planos), sobre o qual múltiplos tenants operam com isolamento rigoroso.

### 1.1 Princípios arquiteturais

1. **Monólito modular**: um único deploy, fronteiras internas explícitas por domínio.
2. **Configuração é dado, não código**: novos segmentos e painéis não exigem alteração de código.
3. **Cinco entidades nunca se misturam**: Segmento, Modelo Operacional, Agente, Tenant e Plano.
4. **Isolamento multi-tenant por padrão**: `tenant_id` + Row Level Security + escopo resolvido no servidor.
5. **A IA não decide finanças**: preços, faturas e pagamentos são calculados de forma determinística no backend.
6. **Nenhuma execução arbitrária**: regras, prompts e instruções jamais são executados como código.
7. **Versionamento imutável**: regras e prompts publicados são versões imutáveis com rollback.
8. **Faturamento separado de recebimento**: preço contratado, valor faturado e dinheiro recebido são grandezas distintas.
9. **Provedores são adaptadores**: IA e pagamentos ficam atrás de portas, sem vazar APIs externas para o domínio.
10. **Dados reais**: dashboards exibem métricas derivadas do banco; dados fictícios nunca são apresentados como reais.

---

## 2. Estilo arquitetural

### 2.1 Monólito modular

Um processo de aplicação (`backend`) e um processo de interface (`frontend`), organizados por domínio.

Justificativas:

- O estágio do produto não justifica o custo operacional de microsserviços.
- Transações financeiras e consistência de configuração são mais simples em um único banco.
- As fronteiras modulares preservam a opção de extração futura de serviços, se necessário.

### 2.2 Camadas internas de cada módulo

Cada módulo de domínio segue, internamente, a mesma direção de dependência:

```
api/            → camada de entrada HTTP (routers, schemas de request/response)
application/    → casos de uso, orquestração, transações
domain/         → entidades, value objects, regras invariantes, ports
infrastructure/ → adaptadores concretos (SQLAlchemy, provedores, filas)
```

Regra de dependência: `api → application → domain` e `infrastructure → domain`. O `domain` **não conhece** FastAPI, SQLAlchemy, HTTP ou provedores externos.

Na FASE 1 essa estrutura é apenas documentada e reservada; os pacotes estão vazios.

### 2.3 Estrutura de diretórios

```
backend/
├─ app/
│  ├─ main.py                     # composição da aplicação FastAPI
│  ├─ api/v1/                     # rotas HTTP versionadas
│  ├─ core/                       # configuração, logging, erros, segurança
│  ├─ db/                         # base declarativa, sessão, contexto RLS
│  └─ modules/
│     ├─ registry.py              # manifesto de módulos e dependências
│     ├─ <domínio>/               # pacotes de domínio
│     └─ shared/                  # kernel compartilhado mínimo
├─ alembic/                       # scaffolding de migrações
├─ tests/                         # unit, integration, security, tenant_isolation
└─ pyproject.toml

frontend/
├─ src/
│  ├─ app/                        # App Router (route groups)
│  ├─ components/                 # layout, UI e composições
│  ├─ lib/                        # navegação, permissões, cliente HTTP
│  └─ types/                      # tipos compartilhados
├─ package.json
└─ next.config.ts
```

---

## 3. Catálogo de módulos (fronteiras e dependências)

Cada módulo possui um slug estável, uma responsabilidade única e dependências explícitas. O manifesto executável está em `backend/app/modules/registry.py` e é validado por testes estruturais (unicidade, dependências existentes e ausência de ciclos).

| # | Módulo | Responsabilidade | Depende de | Fase |
|---|---|---|---|---|
| 1 | `identity_access` | Usuários, credenciais, sessões, JWT/refresh, RBAC | — | 2 |
| 2 | `audit_logs` | Trilha de auditoria imutável de operações sensíveis | — | 2 |
| 3 | `ai_providers` | Porta e adaptadores para provedores de LLM | — | 6 |
| 4 | `tenants` | Cadastro e ciclo de vida da empresa contratante | `identity_access`, `audit_logs` | 2 |
| 5 | `modules_permissions` | Catálogo de módulos, habilitação por segmento/plano/tenant e permissões | `identity_access` | 8 |
| 6 | `segments` | Segmentos de mercado, configuração e versionamento | `audit_logs` | 4 |
| 7 | `business_models` | Modelos operacionais (venda, serviço, agendamento, etc.) | `segments` | 4 |
| 8 | `dynamic_fields` | Campos, formulários e validações configuráveis | `segments` | 4 |
| 9 | `business_rules` | Regras versionadas e motor controlado de avaliação | `segments`, `dynamic_fields` | 5 |
| 10 | `workflows` | Estados operacionais, transições e ações permitidas | `business_rules` | 5 |
| 11 | `knowledge_base` | Fontes de conhecimento isoladas por tenant | `tenants`, `identity_access` | 6 |
| 12 | `tools_integrations` | Registro de ferramentas e integrações autorizadas | `tenants`, `identity_access` | 6 |
| 13 | `agent_management` | Definição, instâncias, prompts versionados, publicação e simulador | `segments`, `business_models`, `business_rules`, `ai_providers`, `knowledge_base`, `tools_integrations` | 6 |
| 14 | `agent_memory` | Configuração e ciclo de vida de memória por agente/tenant | `agent_management` | 6 |
| 15 | `ai_usage_costs` | Medição de tokens, custo, limites e rentabilidade | `agent_management` | 11 |
| 16 | `plans_subscriptions` | Planos, componentes de cobrança e assinaturas | `segments` | 9 |
| 17 | `contracts` | Contratos, vigência, reajustes e vínculo com planos | `tenants`, `plans_subscriptions` | 9 |
| 18 | `billing` | Ciclos, faturas, itens, eventos faturáveis e inadimplência | `contracts`, `plans_subscriptions`, `tenants` | 10 |
| 19 | `payments` | Recebimento, estornos, conciliação e adaptadores de pagamento | `billing` | 10 |
| 20 | `financial_management` | Visão financeira consolidada, créditos, descontos e conciliação | `billing`, `payments`, `ai_usage_costs` | 11 |
| 21 | `analytics` | Indicadores agregados e relatórios | `tenants`, `billing`, `ai_usage_costs`, `audit_logs` | 11 |
| 22 | `notifications` | Notificações internas e para tenants | `identity_access`, `tenants` | 12 |
| 23 | `dynamic_dashboards` | Composição de painéis por módulo, segmento e permissão | `modules_permissions`, `segments` | 8 |
| 24 | `platform_administration` | Administração central da plataforma (SuperAdmin) | `identity_access`, `tenants`, `audit_logs` | 3 |

### 3.1 Regras de dependência

- O grafo de módulos é **acíclico** (DAG) e validado por teste.
- Módulos não acessam tabelas de outros módulos diretamente; comunicam-se por casos de uso publicados e contratos internos.
- `shared` contém apenas utilidades neutras (dinheiro, datas, IDs, resultados). Não contém regra de negócio.
- Dependências são declaradas no manifesto, não inferidas por imports.

### 3.2 O que cada fronteira proíbe

| Fronteira | Proibição |
|---|---|
| `segments` × `business_models` | Modelo operacional não pode virar código por segmento |
| `business_rules` × execução | Nenhum `eval`, `exec` ou código fornecido pelo usuário |
| `agent_management` × `billing` | Agente não altera preço, contrato ou pagamento |
| `billing` × `payments` | Faturamento não depende do provedor para existir |
| `ai_usage_costs` × `billing` | Uso de IA é medido antes de virar evento faturável |
| `identity_access` × `tenants` | Tenant é resolvido no servidor, nunca aceito do frontend |

---

## 4. Multi-tenancy

### 4.1 Estratégia aprovada

**Schema compartilhado + `tenant_id` + Row Level Security (RLS).**

- Todas as tabelas pertencentes a clientes possuem `tenant_id UUID NOT NULL`.
- Tabelas de plataforma (segmentos, planos, catálogo de módulos) não possuem `tenant_id`.
- RLS habilitada com `FORCE ROW LEVEL SECURITY` nas tabelas de tenant.
- A role da aplicação **não** possui `BYPASSRLS` nem é proprietária das tabelas.

### 4.2 Resolução de tenant

1. O tenant é derivado da sessão autenticada (claim assinado do JWT), nunca de `tenant_id` enviado pelo cliente.
2. Operações de plataforma (SuperAdmin) exigem contexto explícito e auditado.
3. O contexto é propagado para jobs assíncronos e workers; nenhuma tarefa roda sem tenant definido.

### 4.3 Contexto de sessão e pool de conexões

O RLS depende de variáveis de sessão no PostgreSQL:

```sql
SET LOCAL app.tenant_id = '<uuid>';
SET LOCAL app.is_superadmin = 'off';
```

Decisões:

- Usar `SET LOCAL` (escopo de transação) e não `SET` de sessão, para evitar vazamento entre requisições no pool.
- Toda operação de tenant ocorre dentro de uma transação que define o contexto antes da primeira query.
- Ao devolver a conexão ao pool, o estado é descartado (`RESET ALL`/`DISCARD ALL` conforme política) como defesa em profundidade.
- Se houver PgBouncer em modo transação, `SET LOCAL` continua válido porque a transação é mantida na mesma conexão.
- A aplicação **nunca** interpola o UUID em SQL; usa `set_config('app.tenant_id', :tenant_id, true)` com bind parameter.

### 4.4 Operações privilegiadas

Acesso de SuperAdmin a dados de tenant:

- Exige permissão explícita e elevação de contexto.
- Gera registro de auditoria com autor, tenant alvo, motivo e correlação de requisição.
- Não é silencioso nem permanente.

### 4.5 Testes de isolamento

A suíte `tests/tenant_isolation/` é reservada para testes que tentam, por todos os recursos, ler e escrever dados de outro tenant. Esses testes exigem PostgreSQL real e serão implementados a partir da FASE 2. Nenhum resultado é declarado aprovado sem execução.

---

## 5. Identidade, autenticação e RBAC

Planejado para a FASE 2, com a fundação já representada:

- **Senhas:** hash Argon2id, nunca reversível.
- **Acesso:** JWT de curta duração.
- **Refresh:** rotação a cada uso, com revogação e detecção de reuso.
- **Sessões:** registro de sessões ativas e revogação.
- **Perfis:** `SUPER_ADMIN`, `ADMIN`, `FINANCEIRO`, `SUPORTE`, `GERENTE_TENANT`, `OPERADOR`, `VISUALIZADOR`.
- **Permissões:** granulares por módulo e operação, com princípio do menor privilégio.
- **Auditoria:** toda operação administrativa sensível gera evento imutável.

A FASE 1 define apenas configuração e contratos; não há autenticação funcional.

---

## 6. Arquitetura de agentes de IA

### 6.1 Portas e adaptadores

```
agent_management (domínio)
        │  depende de
        ▼
AIProviderPort (contrato)
        ▲
        ├── OpenAIAdapter
        ├── AnthropicAdapter
        ├── GeminiAdapter
        └── LocalAdapter (futuro)
```

O domínio desconhece SDKs e formatos de provedor. Cada adaptador traduz um contrato interno (mensagens, ferramentas, tokens, custo) para a API externa correspondente.

### 6.2 Conceitos distintos

| Conceito | Descrição |
|---|---|
| **Agent Definition** | Template reutilizável: instruções, personalidade, tom, ferramentas, políticas, limites |
| **Agent Instance** | Agente publicado e associado a um tenant, com versão ativa |
| **Prompt Version** | Versão imutável do prompt/instruções, com autor, data e changelog |
| **Model Configuration** | Provedor, modelo, temperatura, limites e parâmetros |
| **Tool Registry** | Ferramentas autorizadas, com schema de entrada e validação |
| **Knowledge Source** | Documentos/fontes isolados por tenant, com indexação controlada |
| **Memory Configuration** | Escopo, retenção e política de memória |
| **Usage Record** | Tokens de entrada/saída, custo estimado, duração, resultado, `execution_id` |
| **Human Handoff** | Política e gatilhos de transferência para atendimento humano |
| **Safety Policy** | Limites de conteúdo, dados proibidos, restrições de ferramentas |

### 6.3 Regras de segurança dos agentes

- Instruções e prompts **não são código**; jamais passam por `eval`/`exec`.
- Agentes só executam ferramentas registradas e autorizadas para o tenant.
- Agentes não alteram preço, contrato, pagamento ou dado operacional sem validação do backend.
- Cálculo financeiro é determinístico e ocorre fora do modelo.
- Bases de conhecimento são isoladas por tenant; recuperação sempre escopada.
- Toda execução gera `execution_id` e registro de uso auditável.

---

## 7. Billing e finanças

### 7.1 Separação conceitual obrigatória

| Grandeza | Significado | Onde vive |
|---|---|---|
| **Preço contratado** | O que foi acordado no contrato/plano | `contracts`, `plans`, `plan_components` |
| **Valor faturado** | O que foi emitido em fatura | `invoices`, `invoice_items` |
| **Dinheiro recebido** | O que efetivamente foi pago | `payments`, `payment_allocations` |

Nunca tratar as três como o mesmo campo.

### 7.2 Fluxo

```
Evento faturável → Item de fatura → Fatura → Cobrança no provedor → Pagamento → Conciliação
```

- Eventos financeiros são **append-only** e imutáveis.
- `idempotency_key` única impede cobrança duplicada.
- O núcleo de billing não importa SDK de provedor; usa `PaymentProviderPort`.
- Webhooks são assinados, verificados e idempotentes (`webhook_events`).
- Estornos, créditos e descontos são movimentos próprios, não edições destrutivas.
- Faturamento e recebimento são desacoplados; uma fatura pode existir sem pagamento.

### 7.3 Modelos de cobrança suportados (fases 9–10)

Recorrência mensal, recorrência anual, por pedido, por atendimento, por utilização, por operação, híbrida e contrato personalizado. Um plano pode ter múltiplos componentes.

Nada de billing é implementado na FASE 1.

---

## 8. Configuração dinâmica e versionamento

- Configurações de segmento, campos, formulários, fluxos e módulos são persistidas em **JSONB**, validadas por schemas Pydantic antes da gravação.
- Toda configuração versionada tem `version`, `status` (`draft`, `published`, `archived`), `created_by`, `created_at`, `published_by`, `published_at`.
- Versões publicadas são **imutáveis**; alterações geram nova versão.
- Publicação e rollback são operações auditadas.
- Segmentos e painéis são metadados: o frontend renderiza com base neles, sem código por segmento.

---

## 9. Frontend

### 9.1 Stack e organização

- Next.js (App Router) + TypeScript estrito.
- Server Components por padrão; Client Components apenas quando há interação.
- Route groups previstos: `(auth)`, `(superadmin)`, `(tenant)`.
- Design tokens em CSS (cores, espaçamento, tipografia), sem dados fictícios.

### 9.2 Estrutura

```
src/
├─ app/
│  ├─ layout.tsx                # shell raiz, marca, metadados
│  ├─ page.tsx                  # entrada (redireciona para /admin)
│  └─ admin/                    # área administrativa (fundação)
├─ components/
│  ├─ layout/                   # AppShell, Sidebar, Header
│  └─ ui/                       # EmptyState, StatusBadge, Brand
├─ lib/
│  ├─ navigation.ts             # navegação por módulo e fase
│  ├─ permissions.ts            # tipos de permissão (sem enforcement ainda)
│  └─ api.ts                    # cliente HTTP tipado (base)
└─ types/                       # tipos compartilhados
```

### 9.3 Navegação e permissões

- A navegação é derivada de um registro de módulos com chave, rótulo, rota e fase.
- Itens de módulos não implementados aparecem como indisponíveis, sem ações falsas.
- O enforcement de permissões ocorre no backend; o frontend apenas oculta/desabilita por UX.
- Dashboards dinâmicos serão compostos por módulos habilitados no tenant (FASE 8).

### 9.4 Regra anti-dados-fictícios

Nenhuma tela pode exibir números, gráficos ou indicadores inventados como se fossem reais. Estados vazios são explícitos ("sem dados", "módulo em preparação"). A FASE 1 entrega apenas a fundação visual.

---

## 10. Transversais

| Tema | Decisão |
|---|---|
| Configuração | Pydantic Settings, variáveis de ambiente, `.env.example` sem segredos |
| Logs | Estruturados (JSON), com redação de chaves sensíveis |
| Erros | Exceções de domínio + handlers HTTP padronizados |
| Banco | SQLAlchemy 2.x, migrações Alembic, constraints e índices explícitos |
| Testes | Pytest, camadas unit/integration/security/tenant_isolation |
| Qualidade | Ruff, Mypy, TypeScript estrito, ESLint |
| Saúde | `/health/live` e `/health/ready` |
| Observabilidade | Correlação de requisição, métricas e logs (evolução nas fases seguintes) |
| Segurança | CORS explícito, headers de segurança, segredos fora do código, LGPD por design |

---

## 11. Infraestrutura local

- `docker-compose.yml` na raiz com PostgreSQL, backend e frontend.
- Dockerfiles separados para backend e frontend.
- Dependências Python fixadas com hashes em `backend/requirements.lock` (runtime) e `backend/requirements-dev.lock` (desenvolvimento); o backend Docker instala a partir do lock de runtime.
- `.dockerignore` na raiz impede que `.env`, `.git`, `.venv`, `node_modules` e artefatos de build entrem no contexto Docker.
- `.env.example` na raiz; o arquivo `.env` real não é versionado e não foi criado.
- Health checks de banco e aplicação.
- Instalação do Docker no Windows e ambiente local documentados em `docs/DESENVOLVIMENTO.md`.
- **Docker não está instalado neste ambiente**: o Compose foi criado, mas não foi executado nem validado em runtime.

---

## 12. Limites desta fase

Implementado:

- Documentação arquitetural, modelo de dados e ADRs.
- Esqueleto executável do backend (configuração, logging, sessão, contexto de tenant, health, manifesto de módulos).
- Esqueleto executável do frontend (layout, navegação, design tokens, estados vazios).
- Compose, `.env.example`, convenções e testes estruturais.

Não implementado (proibido nesta fase):

- Autenticação, usuários, RBAC real, RLS aplicada em tabelas de negócio.
- CRUDs de segmentos, regras, agentes, clientes, planos.
- Billing, pagamentos, medição de uso.
- Qualquer métrica de dashboard com dados reais.
- Migrações de banco em produção.

O avanço para a FASE 2 depende de autorização expressa.
