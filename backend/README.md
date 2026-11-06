# AgencIA NTM — Backend

API FastAPI da plataforma SaaS multi-tenant. Na FASE 1 contém apenas a fundação:
configuração, logging estruturado, sessão de banco, contexto de tenant para RLS,
health checks, manifesto de módulos e testes estruturais.

## Requisitos

- Python 3.12 (não 3.14)
- PostgreSQL 16 (via Docker Compose, quando disponível)

## Instalação

```powershell
# a partir da raiz do repositório
& "C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --require-hashes -r ".\backend\requirements-dev.lock"
.\.venv\Scripts\python.exe -m pip install --no-deps -e ".\backend"
```

Dependências fixas em `requirements.lock` (runtime) e `requirements-dev.lock` (desenvolvimento). Consulte `docs/DESENVOLVIMENTO.md` para regerar os locks.

## Execução

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

API: http://localhost:8000/api/v1/health/live
Docs (fora de produção): http://localhost:8000/docs

## Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest backend
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy --config-file backend/pyproject.toml backend/app
```
