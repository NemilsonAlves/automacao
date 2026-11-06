# AgencIA NTM — Auditoria Inicial (FASE 0)

**Produto:** AgencIA NTM — Neural Tech minds
**Documento:** Auditoria técnica e de produto do estado atual
**Fase:** 0 (auditoria e diagnóstico) — nenhuma implementação realizada
**Data:** 06/11/2026
**Responsável:** Time multidisciplinar de arquitetura (CTO, arquitetura, backend, frontend, dados, IA, multi-tenant, billing, segurança/LGPD, design)
**Status:** Concluído — aguardando autorização expressa para iniciar a FASE 1

---

## 0. Sumário executivo

O diretório de trabalho da AgencIA NTM **está completamente vazio**: não há código-fonte, configuração, banco de dados, migrações, documentação prévia, dependências instaladas nem repositório Git inicializado.

Consequências diretas:

- **Não existe sistema legado a preservar.** A cláusula de preservação da seção 19 é atendida por vacuidade: não há arquivos para não excluir, branches para não resetar, `.env` para não alterar nem produção a acessar.
- **Não há conflito arquitetural conhecido**, porque não há arquitetura prévia.
- **Não existe "segunda implementação"** da AgencIA NTM neste diretório.
- O projeto é, portanto, **greenfield**. A FASE 1 (arquitetura e modelagem de dados) pode começar do zero, sem trabalho de compatibilidade.
- O ambiente local possui **Python 3.14.7**, **Node.js 24.20.0**, **pnpm**, **Git**; **não possui Docker** nem **psql** no PATH. Isso impacta o setup e precisa de decisão antes da FASE 1.

Risco dominante deste momento **não é técnico e sim de escopo**: o documento de requisitos descreve uma plataforma SaaS de grande porte (12 fases). A recomendação é executar por fases com portões de aprovação, exatamente como solicitado, sem antecipar módulos.

Nenhum código foi escrito. Nenhum comando destrutivo foi executado. Nenhum deploy, migration ou acesso a produção ocorreu.

---

## 1. Escopo e método da auditoria

A auditoria foi limitada à inspeção local, conforme a seção 19. Procedimentos executados:

| Verificação | Comando/ação | Resultado |
|---|---|---|
| Conteúdo do diretório | listagem recursiva, incluindo ocultos | 0 itens |
| Repositório Git | `git status`, `git branch`, `git log` | não é repositório Git |
| Árvore pai | listagem de `Desktop\Programacao` | apenas projetos irmãos não relacionados |
| Ferramentas instaladas | resolução de executáveis no PATH | Python 3.14.7, Node 24.20.0, pnpm, Git |
| Docker | resolução no PATH | não encontrado |
| Cliente PostgreSQL (`psql`) | resolução no PATH | não encontrado |
| Arquivos `.env` | busca no diretório | nenhum |
| Migrações / banco | busca no diretório | nenhuma |

**Fora de escopo desta fase:** análise de código inexistente, revisão de dependências, análise de vulnerabilidades em artefatos, acesso a ambientes remotos e verificação de produção.

---

## 2. Estado atual do projeto

| Aspecto | Situação |
|---|---|
| Código-fonte | inexistente |
| Backend | inexistente |
| Frontend | inexistente |
| Banco de dados | inexistente |
| Migrações | inexistentes |
| Testes | inexistentes |
| CI/CD | inexistente |
| Infraestrutura | inexistente |
| Documentação | este documento é o primeiro artefato |
| Controle de versão | diretório não versionado |
| Dados | nenhum (nem reais, nem fictícios) |

**Conclusão:** não há dívida técnica herdada, mas também não há fundação. Todo o produto será construído a partir da FASE 1.

---

## 3. Arquitetura encontrada

**Nenhuma.** Não há camadas, módulos, rotas, modelos, serviços ou integrações. Não há decisões arquiteturais registradas (ADRs), diagramas ou convenções de código a seguir.

Isso significa que as convenções de código, nomenclatura, estrutura de pastas e padrões de projeto **serão definidos na FASE 1** e passarão a valer para todas as fases seguintes. Recomenda-se registrá-las em `docs/ARQUITETURA.md` e `AGENTS.md`/`CONTRIBUTING.md` antes de escrever código de produção.

---

## 4. Funcionalidades existentes

**Nenhuma.** Não há telas, endpoints, jobs, integrações ou automações.

---

## 5. Funcionalidades ausentes

Todas as funcionalidades descritas no briefing estão ausentes. Mapeamento por domínio:

| Domínio | Requisito do briefing | Situação |
|---|---|---|
| Administração central | Dashboard SuperAdmin com métricas reais | ausente |
| Segmentos | CRUD dinâmico de segmentos, modelos operacionais, campos, fluxos, módulos | ausente |
| Regras de negócio | Construtor versionado, motor seguro e validado | ausente |
| Agentes de IA | Editor, versionamento de prompts, simulador, publicação, rollback, logs | ausente |
| Multi-tenant | Isolamento, `tenant_id`, RLS, testes de acesso cruzado | ausente |
| Clientes | CRUD, ciclo de vida, aprovação, suspensão, consumo, financeiro | ausente |
| Painéis de cliente | Painel modular por segmento/plano sem duplicar aplicações | ausente |
| Planos e cobrança | Planos, componentes, franquias, excedentes, 8 modelos de cobrança | ausente |
| Billing | Assinaturas, faturas, eventos faturáveis, pagamentos, inadimplência | ausente |
| Custos de IA | Medição de tokens/custo, limites, rentabilidade | ausente |
| Usuários e RBAC | 7 perfis, permissões granulares, auditoria | ausente |
| Segurança e LGPD | Autenticação, JWT + refresh rotativo, rate limit, auditoria, retenção | ausente |
| Design | Dashboard funcional, responsivo, com estados reais | ausente |
| Qualidade | Testes, migrações, observabilidade, tipagem | ausente |

---

## 6. Modelo de dados atual

**Inexistente.** Não há banco, schema ou migração.

### 6.1 Modelo-alvo proposto (alto nível, para validação na FASE 1)

A separação obrigatória entre Segmento, Modelo Operacional, Agente, Tenant e Plano será refletida em entidades distintas. Proposta inicial de agregados:

**Núcleo da plataforma (sem tenant):**
- `segments` — segmento de negócio (id, nome, slug, categoria, ícone, status, versão, config JSONB).
- `operational_models` — modelo operacional vinculado ao segmento.
- `segment_modules` / `modules` — catálogo de módulos e associação por segmento.
- `plans` — plano comercial.
- `plan_components` — componentes de cobrança (recorrência, por pedido, por atendimento, por uso, por operação, híbrido, contrato).
- `custom_field_definitions`, `form_definitions`, `workflow_definitions`.

**Configuração versionada:**
- `rule_sets` + `rule_versions` — regras de negócio versionadas.
- `agents` + `agent_versions` — configuração do agente e versões publicadas.
- `prompt_versions`, `knowledge_sources`, `agent_tools`.

**Tenant e acesso:**
- `tenants` — empresa contratante (dados cadastrais, segmento, modelo operacional, status).
- `users`, `roles`, `permissions`, `role_permissions`, `user_roles`.
- `tenant_modules` — módulos habilitados por tenant/plano.
- `tenant_settings`, `tenant_custom_fields`.

**Comercial e financeiro:**
- `contracts`, `subscriptions`, `subscription_items`.
- `invoices`, `invoice_items`, `billable_events`, `payments`, `refunds`, `credits`, `dunning_events`.
- `usage_records` — tenant, agente, provedor, modelo, tokens in/out, custo estimado, duração, operação, resultado, `execution_id`.

**Governança:**
- `audit_logs`, `consents`, `data_requests` (exportação/exclusão LGPD), `webhook_events` (idempotência), `outbox`.

**Princípios de modelagem:**
- `tenant_id` obrigatório em toda entidade pertencente a cliente.
- Configurações dinâmicas em **JSONB** com validação por schema (Pydantic) na aplicação.
- Eventos financeiros **append-only** (sem update destrutivo), com `idempotency_key` única.
- Versionamento explícito de regras e prompts; publicação por referência a versão imutável.
- Soft delete (`deleted_at`) onde a retenção legal exigir.

---

## 7. Problemas arquiteturais

Não há problemas **existentes** (não há código). Registram-se os riscos arquiteturais **antecipados**, que a FASE 1 deve endereçar por decisão explícita:

1. **Acoplamento segmento × código.** Se novos segmentos exigirem código, o produto falha no requisito central. Mitigação: segmentos, campos, formulários, fluxos e módulos são **dados** (JSONB + validação), nunca `switch`/`if` por segmento.
2. **Construtor de regras virando execução arbitrária.** Permitir linguagem natural ou expressão livre executada no servidor é risco crítico de RCE. Mitigação: motor de regras com **operadores e ações enumerados e autorizados**, sem `eval`, sem execução de código fornecido pelo usuário.
3. **Billing acoplado ao provedor.** Mitigação: núcleo de billing próprio (assinatura, ciclo, fatura, evento) e **adaptadores** para Asaas/Stripe; webhooks idempotentes e conciliação.
4. **Cálculos financeiros na IA.** A IA não deve calcular preços/cobranças. Mitigação: toda decisão financeira é determinística no backend.
5. **Multi-tenancy frágil.** Confiar no `tenant_id` do frontend é vazamento de dados. Mitigação: resolução de tenant no servidor (token/sessão), política central de escopo, RLS e testes de acesso cruzado.
6. **Painéis duplicados por segmento.** Mitigação: arquitetura de módulos + permissões + metadados, um único frontend.
7. **Monólito virando "monólito espaguete".** Mitigação: monólito **modular** com fronteiras claras por domínio e contratos internos.
8. **Dashboard com dados fictícios.** Mitigação: métricas derivadas de queries reais; seeds apenas em ambiente de desenvolvimento, nunca em produção.
9. **Versionamento tardio.** Regras e prompts precisam de versão desde o início; retrofitar é caro.

---

## 8. Riscos de segurança

| ID | Risco | Severidade | Mitigação planejada |
|---|---|---|---|
| S1 | Vazamento entre tenants | Crítico | Escopo de tenant no servidor + RLS + testes de isolamento |
| S2 | Execução de código via regras/prompts | Crítico | Motor de regras restrito; nunca `eval`; ações em allowlist |
| S3 | Segredos expostos em log/código | Alto | Segredos só em env/secret manager; logs sem PII/tokens |
| S4 | Senhas/credenciais fracas | Alto | Argon2id, política de senha, bloqueio progressivo |
| S5 | Sessão sequestrada | Alto | JWT curto + refresh rotativo com revogação e detecção de reuso |
| S6 | Força bruta / abuso | Médio/Alto | Rate limiting por IP/usuário/tenant, backoff |
| S7 | SQL injection | Alto | ORM parametrizado; sem SQL concatenado; revisão |
| S8 | Webhooks forjados/repetidos | Alto | Assinatura HMAC, verificação de origem, idempotência |
| S9 | Dados sensíveis de saúde (clínicas) | Crítico | Minimização, criptografia, controle de acesso, retenção, base legal |
| S10 | Ausência de auditoria de ações sensíveis | Alto | `audit_logs` imutável para operações administrativas |
| S11 | LGPD: exportação/exclusão/consentimento | Alto | Fluxos de titular, retenção configurável, consentimentos |
| S12 | Dependências vulneráveis | Médio | Lockfiles, auditoria de dependências no CI |
| S13 | CORS/CSRF mal configurados | Médio | Origens explícitas, cookies `HttpOnly`/`SameSite` quando aplicável |

Observação: dados de saúde e financeiros elevam a classificação de sensibilidade. O design deve assumir **privacidade desde a concepção** e **minimização de dados**.

---

## 9. Riscos multi-tenant

| ID | Risco | Mitigação |
|---|---|---|
| M1 | Query sem filtro de tenant | Repositório/base com escopo obrigatório; lint/revisão; RLS |
| M2 | `tenant_id` vindo do cliente | Tenant resolvido exclusivamente no backend a partir da sessão |
| M3 | IDOR em recursos por `id` | Toda leitura/escrita valida posse do recurso pelo tenant |
| M4 | Vazamento via cache/chaves | Chaves de cache prefixadas por tenant |
| M5 | Vazamento em jobs/async | Contexto de tenant propagado em tarefas e filas |
| M6 | Vazamento em relatórios/exports | Consultas sempre escopadas; testes de exportação |
| M7 | RLS mal configurada (fail-open) | RLS com `FORCE ROW LEVEL SECURITY`; role de app sem `BYPASSRLS` |
| M8 | SuperAdmin acessando dados de cliente sem trilha | Acesso mediado, justificado e auditado |

Recomendação de estratégia: **schema compartilhado com `tenant_id` + RLS**, por simplicidade operacional e custo, com testes automatizados que tentem acessar dados de outro tenant em todos os recursos. Alternativa (schema/banco por tenant) fica registrada como decisão a validar na FASE 1, considerando custo e isolamento.

---

## 10. Possíveis conflitos

1. **Versão de Python.** O briefing exige "Python 3.12+"; o ambiente tem **3.14.7**. É compatível em tese, mas bibliotecas do ecossistema (SQLAlchemy, Alembic, drivers) podem ter suporte incompleto. **Decisão necessária:** fixar 3.12/3.13 para maturidade ou assumir 3.14 com validação de dependências.
2. **Docker ausente.** O briefing prevê Docker para infraestrutura. Sem Docker no ambiente, o setup local e os testes de integração com PostgreSQL ficam comprometidos. **Decisão necessária:** instalar Docker Desktop ou definir PostgreSQL local/serviço gerenciado.
3. **PostgreSQL ausente (`psql`).** Necessário para desenvolvimento e testes de RLS. **Decisão necessária:** instalação local, container ou instância gerenciada de desenvolvimento.
4. **Escopo vs. fases.** O documento pede "plataforma completa", mas a metodologia exige execução faseada com aprovação. Sem conflito real, desde que o escopo de cada fase seja explicitamente aprovado (o que este documento recomenda).
5. **Provedor de pagamento.** Asaas/Stripe citados como "conforme disponibilidade". A escolha impacta o adaptador, mas **não** o núcleo de billing. Pode ser decidida na FASE 9/10.
6. **Repositório Git.** Não há Git inicializado. Recomenda-se `git init` na FASE 1, com `.gitignore` adequado, **mediante autorização** (não foi feito nesta fase).

Nenhum conflito arquitetural pré-existente foi encontrado, pois não há arquitetura anterior.

---

## 11. Arquivos que precisarão ser modificados

**Nenhum.** Não existe arquivo no projeto. Toda a base será criada.

---

## 12. Arquivos que precisarão ser criados

Proposta de estrutura (a ser refinada e aprovada na FASE 1). Nada foi criado além deste documento.

```
AgencIA NTM/
├─ docs/
│  ├─ AGENCIANTM_AUDITORIA_INICIAL.md      (este documento)
│  ├─ ARQUITETURA.md                        (FASE 1)
│  ├─ MODELO_DE_DADOS.md                    (FASE 1)
│  ├─ ADRs/                                 (FASE 1+)
│  ├─ SEGURANCA_LGPD.md                     (FASE 2/12)
│  └─ RUNBOOK.md                            (FASE 12)
├─ backend/
│  ├─ pyproject.toml
│  ├─ alembic.ini
│  ├─ alembic/versions/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/            (config, security, logging, errors)
│  │  ├─ db/              (session, base, rls)
│  │  ├─ modules/
│  │  │  ├─ auth/
│  │  │  ├─ tenants/
│  │  │  ├─ segments/
│  │  │  ├─ rules/
│  │  │  ├─ agents/
│  │  │  ├─ customers/
│  │  │  ├─ modules_registry/
│  │  │  ├─ plans/
│  │  │  ├─ billing/
│  │  │  ├─ usage/
│  │  │  ├─ rbac/
│  │  │  └─ audit/
│  │  └─ workers/         (jobs, outbox, webhooks)
│  └─ tests/
│     ├─ unit/
│     ├─ integration/
│     ├─ security/
│     └─ tenant_isolation/
├─ frontend/
│  ├─ package.json
│  ├─ next.config.ts
│  ├─ src/
│  │  ├─ app/
│  │  │  ├─ (auth)/
│  │  │  ├─ (superadmin)/
│  │  │  └─ (tenant)/
│  │  ├─ components/
│  │  ├─ lib/
│  │  ├─ hooks/
│  │  └─ types/
│  └─ tests/
├─ infra/
│  ├─ docker-compose.yml
│  ├─ Dockerfile.backend
│  ├─ Dockerfile.frontend
│  └─ .env.example
├─ .gitignore
├─ AGENTS.md
└─ README.md
```

---

## 13. Plano de evolução

Execução por fases independentes, cada uma com escopo, impacto, arquivos, implementação, testes, revisão de diff, relatório e **aprovação explícita** antes da próxima.

| Fase | Escopo | Artefatos principais | Depende de |
|---|---|---|---|
| 0 | Auditoria | este documento | — |
| 1 | Arquitetura e modelagem de dados | `ARQUITETURA.md`, `MODELO_DE_DADOS.md`, ADRs, esqueleto de projeto, `docker-compose`, `.env.example`, `git init` (com autorização) | 0 |
| 2 | Auth, RBAC e multi-tenancy | usuários, papéis, permissões, JWT/refresh, resolução de tenant, RLS inicial, testes de isolamento | 1 |
| 3 | Dashboard SuperAdmin | endpoints de métricas reais + UI do painel central | 2 |
| 4 | Segmentos | CRUD, duplicação, versionamento, modelos operacionais, módulos, campos | 2 |
| 5 | Regras de negócio | motor de regras seguro, versionamento, validação, publicação | 4 |
| 6 | Agentes de IA | CRUD, prompts versionados, simulador, publicação/rollback, logs | 5 |
| 7 | Clientes | CRUD, ciclo de vida, aprovação, consumo, financeiro, histórico | 2,4 |
| 8 | Painéis dinâmicos | renderização por módulos/permissões/segmento | 4,7 |
| 9 | Planos, contratos e assinaturas | planos, componentes, assinaturas, contratos | 4,7 |
| 10 | Billing e pagamentos | núcleo de billing, faturas, eventos, adaptadores, webhooks idempotentes | 9 |
| 11 | Custos e rentabilidade | `usage_records`, limites, dashboard de custos/margem | 6,10 |
| 12 | Auditoria, segurança e testes integrados | LGPD, auditoria completa, hardening, observabilidade, suíte integrada | todas |

Regra de ouro: **não implementar fases simultaneamente**; sem fases futuras não autorizadas.

---

## 14. Estimativa de complexidade

Estimativas **relativas e aproximadas** (não são compromisso de prazo), para dimensionamento de esforço de um time pequeno e sênior:

| Fase | Complexidade | Esforço relativo | Observações |
|---|---|---|---|
| 1 | Média | 2–3 | Decisões estruturais têm alto impacto futuro |
| 2 | Alta | 4–6 | Base de isolamento; erros aqui são caros |
| 3 | Média | 3–4 | Métricas reais exigem modelo estável |
| 4 | Alta | 5–7 | Núcleo da flexibilidade por segmento |
| 5 | Alta | 5–7 | Motor seguro é ponto crítico |
| 6 | Alta | 5–7 | Versionamento, simulador, integração LLM |
| 7 | Média/Alta | 4–5 | Ciclo de vida + integração com fases 4/9 |
| 8 | Alta | 5–6 | Painel dinâmico sem duplicar apps |
| 9 | Média/Alta | 4–5 | Modelagem comercial flexível |
| 10 | Muito Alta | 7–9 | Idempotência, conciliação, webhooks |
| 11 | Média | 3–4 | Medição e rentabilidade |
| 12 | Alta | 5–7 | Hardening, LGPD, testes integrados |

Total: **muito alto**, compatível com um produto SaaS completo. A execução faseada é obrigatória para reduzir risco.

---

## 15. Recomendações técnicas

**Arquitetura**
1. Monólito modular por domínio, com fronteiras explícitas; sem microsserviços prematuros.
2. Segmento, modelo operacional, agente, tenant e plano como entidades **separadas**, conforme seção 2 do briefing.
3. Segmentos/painéis dirigidos por **metadados** (JSONB validado), nunca por código por segmento.
4. Motor de regras com **operadores e ações enumerados**, sem `eval` e sem execução de linguagem natural como código.
5. Publicação por **versão imutável** (regras e prompts) com rollback.

**Dados**
6. PostgreSQL com `tenant_id` em todas as entidades de cliente e **RLS** com `FORCE ROW LEVEL SECURITY`; role de aplicação sem `BYPASSRLS`.
7. Eventos financeiros **append-only** e `idempotency_key` único para evitar cobrança duplicada.
8. Migrações versionadas com Alembic; revisão obrigatória antes de aplicar.

**Segurança e LGPD**
9. Argon2id para senhas; JWT curto + refresh rotativo com detecção de reuso.
10. Rate limiting, proteção contra brute force, validação estrita de entrada.
11. Logs estruturados **sem PII/segredos**; auditoria imutável de ações sensíveis.
12. Fluxos de titular (exportação/exclusão) e retenção configurável; atenção a dados de saúde.

**Billing**
13. Núcleo desacoplado do provedor; adaptadores Asaas/Stripe; webhooks assinados e idempotentes; conciliação e auditoria.
14. IA nunca calcula valores financeiros; cálculo é determinístico no backend.

**Qualidade**
15. Tipagem estrita (mypy/pyright), Pydantic, testes unitários, de integração, de autorização, de isolamento multi-tenant, financeiros e de idempotência.
16. Observabilidade: logs estruturados, métricas, health checks; CI com lint, tipos e testes.

**Ambiente (lacunas a resolver antes da FASE 1)**
17. Instalar **Docker** ou definir PostgreSQL de desenvolvimento (Docker Compose recomendado).
18. Definir versão do Python (recomendação: fixar **3.12/3.13** por maturidade do ecossistema, ou validar 3.14 explicitamente).
19. Inicializar **Git** com `.gitignore` (somente com autorização).

---

## 16. Decisões pendentes (necessárias para a FASE 1)

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| D1 | Estratégia multi-tenant | schema compartilhado + RLS / schema por tenant / banco por tenant | schema compartilhado + RLS |
| D2 | Versão do Python | 3.12 / 3.13 / 3.14 | 3.12 ou 3.13 |
| D3 | Banco de desenvolvimento | Docker Compose / instalação local / serviço gerenciado | Docker Compose |
| D4 | Inicializar Git | sim / não | sim, com `.gitignore` |
| D5 | Gerenciador de pacotes frontend | pnpm / npm | pnpm |
| D6 | Estratégia de autenticação | JWT + refresh / sessão server-side | JWT curto + refresh rotativo |
| D7 | Provedor de pagamento inicial | Asaas / Stripe / adiar | adiar para FASE 9/10 (núcleo desacoplado) |
| D8 | Provider(s) de LLM | definir na FASE 6 | decidir na FASE 6 |

---

## 17. Critérios de aceite da FASE 0

- [x] Diretório inspecionado integralmente (incluindo ocultos).
- [x] Situação de Git verificada (não versionado).
- [x] Tecnologias existentes identificadas (nenhuma no projeto; ambiente mapeado).
- [x] Banco e migrações verificados (inexistentes).
- [x] Módulos existentes verificados (inexistentes).
- [x] Dependências verificadas (inexistentes).
- [x] Riscos de integração avaliados (nenhum conflito pré-existente; riscos antecipados documentados).
- [x] Riscos de segurança e multi-tenant documentados.
- [x] Arquivos a criar/modificar mapeados.
- [x] Plano de evolução e complexidade apresentados.
- [x] Nenhum arquivo excluído, sobrescrito ou resetado; nenhum `.env` alterado; nenhum deploy/migration/acesso a produção; nenhum comando destrutivo.

---

## 18. Próximos passos

A FASE 1 **não foi iniciada** e depende de **autorização expressa**. Antes disso, recomenda-se que as decisões **D1–D8** da seção 16 sejam confirmadas (ou aceitas as recomendações padrão).

Após autorização, a FASE 1 entregará:

- `docs/ARQUITETURA.md` (visão de camadas, módulos e fronteiras).
- `docs/MODELO_DE_DADOS.md` (entidades, relacionamentos, índices, constraints, RLS).
- ADRs das decisões estruturais.
- Esqueleto do monólito modular (backend e frontend) **sem funcionalidades de negócio**.
- `docker-compose.yml` e `.env.example` (sem segredos).
- Convenções de código e `AGENTS.md`.
- Relatório de impacto e revisão de diff, aguardando aprovação para a FASE 2.

---

**Fim da Auditoria Inicial (FASE 0).**
