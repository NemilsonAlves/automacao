# AgencIA NTM — Ambiente de Desenvolvimento

**Produto:** AgencIA NTM — Neural Tech minds
**Escopo:** instalação do Docker no Windows, ambiente local e dependências reproduzíveis
**Última atualização:** 06/11/2026

> **Limitação atual:** o Docker **não está instalado** na máquina onde este documento foi preparado. Os comandos de Docker abaixo são instruções de instalação e uso, mas **não foram executados nem validados em runtime** neste ambiente. PostgreSQL e `psql` também não estão instalados.

---

## 1. Pré-requisitos do Windows

| Item | Requisito |
|---|---|
| Windows | 10 64-bit (build 19044+) ou Windows 11 |
| Virtualização | Habilitada na BIOS/UEFI |
| WSL | WSL 2 instalado e atualizado |
| Espaço em disco | Recomendado 20 GB livres para imagens e volumes |
| Docker | Docker Desktop com backend WSL 2 |

Verificar virtualização: Gerenciador de Tarefas → Desempenho → CPU → **Virtualização: Habilitada**. Se estiver desabilitada, habilite VT-x/AMD-V na BIOS.

---

## 2. Instalação do Docker Desktop no Windows

Executar em PowerShell **como Administrador**.

### 2.1 Instalar/atualizar o WSL 2

```powershell
wsl --install
wsl --update
wsl --set-default-version 2
wsl --status
```

Reinicie a máquina quando solicitado.

### 2.2 Instalar o Docker Desktop

Opção via `winget`:

```powershell
winget install -e --id Docker.DockerDesktop
```

Alternativa: instalar pelo site oficial do Docker Desktop para Windows.

Após a instalação:

1. Reinicie a máquina.
2. Abra o **Docker Desktop**.
3. Aceite os termos de uso.
4. Confirme que o backend está em **WSL 2** (Settings → General → Use the WSL 2 based engine).
5. Aguarde o status **Engine running**.

### 2.3 Verificar a instalação

```powershell
docker version
docker compose version
docker run --rm hello-world
```

O último comando deve exibir a mensagem de sucesso do Docker.

### 2.4 Problemas comuns

| Sintoma | Ação |
|---|---|
| `docker: command not found` | Reabra o terminal após instalar; confirme o PATH |
| `Cannot connect to the Docker daemon` | Abra o Docker Desktop e aguarde o engine iniciar |
| `WSL update failed` | Execute `wsl --update` como administrador e reinicie |
| Virtualização indisponível | Habilite VT-x/AMD-V na BIOS/UEFI |
| Porta 5432/8000/3000 ocupada | Altere `POSTGRES_PORT`, `BACKEND_PORT` ou `FRONTEND_PORT` no `.env` |
| Erro de memória | Ajuste recursos do Docker Desktop em Settings → Resources |

---

## 3. Configuração do projeto

A partir da raiz do repositório:

```powershell
Copy-Item .env.example .env
```

Edite o `.env`:

- Troque `POSTGRES_PASSWORD` por uma senha local forte.
- Mantenha `JWT_SECRET` vazio apenas enquanto a FASE 2 não estiver implementada.
- Ajuste portas se necessário.

Gerar um segredo local para uso futuro:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> O arquivo `.env` **nunca** deve ser versionado. O `.gitignore` já o exclui.

### 3.1 Caracteres especiais na senha

O `DATABASE_URL` do Compose é montado a partir de `POSTGRES_USER`/`POSTGRES_PASSWORD`. Senhas com `@`, `:`, `/`, `#` ou `%` podem quebrar a URL. Para o ambiente local, prefira caracteres alfanuméricos ou codifique a senha na URL (`%40`, `%3A`, etc.).

---

## 4. Subir o ambiente com Docker Compose

```powershell
docker compose config
docker compose up --build
```

Serviços:

| Serviço | Endereço |
|---|---|
| Frontend | http://localhost:3000/admin |
| Backend (liveness) | http://localhost:8000/api/v1/health/live |
| Backend (prontidão, depende do banco) | http://localhost:8000/api/v1/health/ready |
| Swagger (fora de produção) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Comandos úteis:

```powershell
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
```

> `docker compose down -v` remove o volume do PostgreSQL e **apaga os dados locais**. Use apenas conscientemente.

O Compose atual não monta o código como volume; alterações exigem `docker compose up --build`.

---

## 5. Ambiente nativo (sem Docker)

### 5.1 Instalações

- Python **3.12** (não 3.14)
- Node.js **24**
- pnpm **9.15.4** via Corepack
- PostgreSQL **16**

```powershell
corepack enable
corepack prepare pnpm@9.15.4 --activate
```

### 5.2 Banco local

Crie a role e o banco (via `psql` ou pgAdmin):

```sql
CREATE ROLE agenciantm LOGIN PASSWORD 'troque-esta-senha';
CREATE DATABASE agenciantm OWNER agenciantm;
```

Ajuste no `.env`:

```
DATABASE_URL=postgresql+psycopg://agenciantm:troque-esta-senha@localhost:5432/agenciantm
```

### 5.3 Backend

```powershell
& "C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --require-hashes -r backend\requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

> O primeiro comando usa o runtime 3.12 gerenciado pelo `uv` nesta máquina. Em outra máquina, use o caminho do Python 3.12 instalado.

### 5.4 Frontend

```powershell
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
```

---

## 6. Dependências reproduzíveis

O backend usa dois lockfiles com versões fixas e hashes SHA-256:

| Arquivo | Conteúdo |
|---|---|
| `backend/requirements.lock` | Dependências de runtime |
| `backend/requirements-dev.lock` | Runtime + ferramentas de desenvolvimento |

Os lockfiles são gerados com **uv** e resolução universal (Windows, Linux e macOS) para Python 3.12.

### 6.1 Instalar a partir do lock

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r backend\requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .\backend
```

### 6.2 Regerar os lockfiles

O `uv` é instalado **apenas no `.venv` local**, nunca globalmente:

```powershell
.\.venv\Scripts\python.exe -m pip install uv

.\.venv\Scripts\uv.exe pip compile backend/pyproject.toml `
  --python-version 3.12 --universal --generate-hashes `
  --no-header --no-annotate -o backend/requirements.lock

.\.venv\Scripts\uv.exe pip compile backend/pyproject.toml `
  --extra dev --python-version 3.12 --universal --generate-hashes `
  --no-header --no-annotate -o backend/requirements-dev.lock
```

Regras:

1. Não editar lockfiles manualmente.
2. Alterações de versão exigem justificativa técnica e revisão.
3. Regenerar e validar os dois lockfiles juntos.
4. O Docker usa `requirements.lock`; o ambiente de desenvolvimento usa `requirements-dev.lock`.

### 6.3 Verificar o lock

```powershell
.\.venv\Scripts\python.exe -m pip install --dry-run --require-hashes --ignore-installed -r backend\requirements.lock
.\.venv\Scripts\python.exe -m pip install --dry-run --require-hashes --ignore-installed -r backend\requirements-dev.lock
.\.venv\Scripts\python.exe -m pytest backend
```

O frontend é travado por `frontend/pnpm-lock.yaml`:

```powershell
pnpm --dir frontend install --frozen-lockfile
```

---

## 7. Testes e qualidade

```powershell
.\.venv\Scripts\python.exe -m pytest backend
.\.venv\Scripts\python.exe -m ruff check backend
.\.venv\Scripts\python.exe -m mypy --config-file backend/pyproject.toml backend/app

pnpm --dir frontend typecheck
pnpm --dir frontend lint
pnpm --dir frontend build
```

Auditoria de dependências:

```powershell
.\.venv\Scripts\uv.exe tool run pip-audit -r backend/requirements.lock
pnpm --dir frontend audit --prod
```

---

## 8. Notas do ambiente atual

- Python padrão: 3.14.7. O projeto exige 3.12 e usa `.venv`.
- `py -3.12` não funciona; use o caminho absoluto do runtime `uv` documentado acima.
- Docker e `psql` ausentes: Compose não executado.
- O aviso de depreciação do `httpx` no `TestClient` do Starlette é conhecido e não bloqueia a FASE 1.
- O ESLint 9.39.5 está marcado como deprecated pelo registro; a atualização será avaliada com justificativa técnica em fase futura.
- Na consolidação da FASE 1.1, `pytest` foi atualizado de 8.4.2 para 9.2.0 e `pytest-asyncio` de 0.26.0 para 1.4.1.post1 para corrigir o advisory **PYSEC-2026-1845** (dev-only). A suíte foi reexecutada com as novas versões.
- O contexto de build do Docker é limitado por `.dockerignore`; `.env`, `.git`, `.venv`, `node_modules` e `.next` não são enviados ao daemon.
