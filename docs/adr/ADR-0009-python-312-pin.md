# ADR-0009 — Fixar Python 3.12 para o backend

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Engenheiro Python, CTO
- **Fase:** 1

## Contexto

O ambiente de desenvolvimento possui Python 3.14.7 como versão padrão, além de um runtime 3.12.14 gerenciado pelo `uv` (não registrado no launcher `py`). O briefing aprova Python 3.12 e a compatibilidade do ecossistema (SQLAlchemy, Alembic, psycopg) é mais previsível nessa versão.

## Decisão

Fixar `requires-python = ">=3.12,<3.13"` no backend e usar o interpretador 3.12.14 disponível para criar o ambiente virtual local (`.venv`). Não alterar a instalação global do Python e não instalar dependências globalmente.

Caminho identificado no ambiente:

```
C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe
```

## Consequências

**Positivas**

- Compatibilidade previsível com bibliotecas.
- Isolamento do ambiente via `.venv`.
- Reprodutibilidade no Docker (`python:3.12-slim`).

**Negativas**

- O comando `py -3.12` não funciona no ambiente atual; é necessário usar o caminho absoluto ou criar o venv uma vez.
- Desenvolvedores precisam instalar Python 3.12 caso não o tenham.

## Instruções

Criar o ambiente:

```powershell
& "C:\Users\walbinhoXD\AppData\Roaming\uv\python\cpython-3.12.14-windows-x86_64-none\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e "backend[dev]"
```

## Referências

- `backend/pyproject.toml`
- `README.md`
