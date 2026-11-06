# AgencIA NTM

**Neural Tech minds**

Plataforma SaaS multi-tenant para administração, configuração e comercialização de agentes de inteligência artificial para empresas de qualquer segmento.

> **Status:** FASE 1 — Fundação arquitetural concluída. A FASE 2 (autenticação, RBAC e multi-tenancy) não foi iniciada e depende de autorização expressa.

## O que existe hoje

- Documentação de arquitetura, modelo de dados e ADRs.
- Backend FastAPI com fundação transversal: configuração, logging com redação de segredos, sessão assíncrona, contexto de tenant para RLS, health checks e manifesto de módulos.
- Frontend Next.js com layout administrativo, identidade visual, navegação por módulos e estados vazios explícitos.
- Docker Compose (PostgreSQL + backend + frontend) e `.env.example`.
- Testes estruturais e de integração que não exigem banco.

Não há autenticação, CRUDs, billing, dashboards com métricas ou cobrança nesta fase.

## Documentação

- [Auditoria inicial](docs/AGENCIANTM_AUDITORIA_INICIAL.md)
- [Arquitetura](docs/ARQUITETURA.md)
- [Modelo de dados](docs/MODELO_DE_DADOS.md)
- [ADRs](docs/adr/)
- [Ambiente de desenvolvimento](docs/DESENVOLVIMENTO.md)
- [Convenções para agentes](AGENTS.md)

## Estrutura

```
backend/   API FastAPI (Python 3.12), testes e lockfiles
frontend/  Next.js + TypeScript e pnpm-lock.yaml
docs/      arquitetura, modelo de dados, ADRs, ambiente e relatórios
docker-compose.yml
.env.example
```

## Pré-requisitos

- Python 3.12
- Node.js 24 + pnpm 9
- PostgreSQL 16 (via Docker Compose) — **Docker não está instalado no ambiente atual**

O runtime Python 3.12 identificado neste ambiente:

```
C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe
```

## Configuração

```powershell
Copy-Item .env.example .env
```

Edite o `.env` localmente. **Nunca versione o `.env`.** O `JWT_SECRET` vazio é intencional nesta fase; será obrigatório na FASE 2.

## Backend

```powershell
& "C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --require-hashes -r ".\backend\requirements-dev.lock"
.\.venv\Scripts\python.exe -m pip install --no-deps -e ".\backend"

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

Alternativa sem lockfile (não recomendada para validação): `pip install -e ".\backend[dev]"`.

Instruções completas, incluindo Docker Desktop no Windows e regeração dos locks, em [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md).

- Liveness: http://localhost:8000/api/v1/health/live
- Readiness (requer banco): http://localhost:8000/api/v1/health/ready
- Swagger (fora de produção): http://localhost:8000/docs

## Frontend

```powershell
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
```

- Painel: http://localhost:3000/admin

## Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest backend
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy --config-file backend/pyproject.toml backend/app

pnpm --dir frontend typecheck
pnpm --dir frontend lint
pnpm --dir frontend build
```

## Docker

O Compose está pronto, mas **não foi executado nem validado** porque o Docker não está instalado no ambiente. Passo a passo de instalação no Windows em [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md).

```powershell
Copy-Item .env.example .env
docker compose config
docker compose up --build
```

Serviços: `db` (PostgreSQL 16), `backend` (8000) e `frontend` (3000). O backend usa `backend/requirements.lock` com hashes.

## Próxima fase

A FASE 2 implementará identidade, RBAC, JWT com refresh rotativo, resolução de tenant no backend, RLS aplicada e testes de acesso cruzado. **Não iniciar sem autorização.**
