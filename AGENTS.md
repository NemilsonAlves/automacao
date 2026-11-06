# AGENTS.md — Convenções da AgencIA NTM

Este arquivo orienta qualquer agente ou pessoa que trabalhe no repositório.

## 1. Contexto do produto

AgencIA NTM (Neural Tech minds) é uma plataforma SaaS multi-tenant para criar, configurar, comercializar e operar agentes de IA para empresas de qualquer segmento. **Não é um chatbot isolado nem um conjunto de apps por segmento.**

Entidades que nunca se misturam: Segmento, Modelo Operacional, Agente, Tenant e Plano Comercial.

## 2. Disciplina de fases

- A FASE 1 (fundação arquitetural) está concluída.
- **Não iniciar a FASE 2 nem fases seguintes sem autorização expressa do usuário.**
- Cada fase tem escopo próprio, deve ser implementada isoladamente, testada, revisada e reportada.
- Não criar funcionalidades fictícias, dados simulados apresentados como reais ou botões sem ação.

## 3. Idioma e estilo

- Comunicar-se em português do Brasil.
- Nomes de código (tabelas, colunas, classes, funções, rotas) em inglês.
- Nomes de produto e textos de interface em português.
- Docstrings explicativas são bem-vindas; evitar comentários óbvios e ruído.

## 4. Ambiente

- Python **3.12** (não usar 3.14). Runtime disponível:
  `C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe`
- Node.js 24 e pnpm 9.
- **Docker não está instalado**: o Compose existe, mas não foi executado.
- Não instalar dependências globalmente; usar `.venv` (backend) e `node_modules` (frontend).
- Não alterar arquivos `.env` de outros projetos. Não versionar `.env`.

## 5. Comandos

Backend (a partir da raiz):

```powershell
& "C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --require-hashes -r ".\backend\requirements-dev.lock"
.\.venv\Scripts\python.exe -m pip install --no-deps -e ".\backend"

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
.\.venv\Scripts\python.exe -m pytest backend
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy --config-file backend/pyproject.toml backend/app
```

Frontend:

```powershell
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
pnpm --dir frontend typecheck
pnpm --dir frontend lint
pnpm --dir frontend build
```

Docker (somente quando Docker estiver disponível):

```powershell
docker compose config
docker compose up --build
```

Instalação do Docker no Windows e regeração dos lockfiles: `docs/DESENVOLVIMENTO.md`.

## 6. Arquitetura

- Monólito modular. Grafo de módulos em `backend/app/modules/registry.py`, acíclico e validado por teste.
- Cada módulo segue `api → application → domain`; `infrastructure` implementa portas do domínio.
- O domínio não importa FastAPI, SQLAlchemy, SDKs de provedores ou HTTP.
- Não acessar tabelas de outro módulo diretamente: usar casos de uso/contratos internos.
- `shared` é kernel mínimo, sem regra de negócio.

## 7. Segurança multi-tenant (invariantes)

1. `tenant_id` vem da sessão autenticada no backend, **nunca** do frontend.
2. Toda tabela de cliente possui `tenant_id UUID NOT NULL`.
3. RLS habilitada e forçada; role da aplicação sem `BYPASSRLS`.
4. Contexto RLS via `set_config(..., true)` (`SET LOCAL`) dentro de transação.
5. Toda operação escopada por tenant deve ter teste de isolamento.
6. Operações de SuperAdmin sobre dados de tenant exigem contexto explícito e auditoria.
7. Nunca interpolar `tenant_id` em SQL; usar parâmetros vinculados.

## 8. Regras de dados e finanças

- Dinheiro em `numeric` + `currency`; nunca `float`.
- **Preço contratado ≠ valor faturado ≠ dinheiro recebido.**
- Eventos faturáveis e de uso são append-only, com `idempotency_key` única.
- Pagamentos passam por adaptadores; nenhum dado de cartão é armazenado.
- Cálculos financeiros são determinísticos no backend; a IA nunca calcula valores.
- Configurações dinâmicas em JSONB com validação Pydantic e `schema_version`.
- Versões publicadas são imutáveis; rollback republica versão anterior.

## 9. IA

- Provedores atrás de `AIProviderPort`; domínio não importa SDKs.
- Prompts e instruções não são código; proibido `eval`, `exec`, `os.system` e similares.
- Ferramentas só rodam se registradas e autorizadas para o tenant.
- Toda execução registra `execution_id`, tokens e custo estimado.

## 10. Frontend

- Next.js App Router + TypeScript estrito; Server Components por padrão.
- Navegação derivada de `src/lib/navigation.ts`.
- Permissões são enforceadas no backend; o frontend apenas ajusta UX.
- Não exibir indicadores sem dados reais; usar estados vazios explícitos.
- Manter identidade: **AgencIA NTM / Neural Tech minds**.

## 11. Testes e qualidade

- Backend: pytest (`unit`, `integration`, `security`, `tenant_isolation`), Ruff e Mypy.
- Frontend: `tsc --noEmit`, ESLint e build Next.js.
- Toda fase deve entregar testes executáveis; não declarar testes aprovados sem execução.
- Não executar migrações em bancos externos ou produção.
- Dependências Python são fixadas em `backend/requirements.lock` e `backend/requirements-dev.lock`; não editar os locks manualmente.
- Regenerar locks somente com justificativa técnica e revisão; usar `uv` local no `.venv`.

## 12. Preservação e segurança operacional

- Não excluir arquivos, não resetar Git, não limpar diretórios, não remover stashes.
- Não acessar produção, não fazer deploy, push ou PR sem autorização.
- Não expor segredos em código, logs, commits ou relatórios.

## 13. Documentação obrigatória

- `docs/ARQUITETURA.md` — arquitetura e fronteiras.
- `docs/MODELO_DE_DADOS.md` — modelo de dados.
- `docs/DESENVOLVIMENTO.md` — ambiente local, Docker no Windows e lockfiles.
- `docs/adr/` — decisões arquiteturais.
- `docs/RELATORIO_FASE_1.md` — relatório da fase atual.
- Atualizar a documentação ao alterar decisões estruturais.
