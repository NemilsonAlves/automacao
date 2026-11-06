"""Verificação estrutural dos lockfiles de dependências."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
RUNTIME_LOCK = BACKEND_DIR / "requirements.lock"
DEV_LOCK = BACKEND_DIR / "requirements-dev.lock"
PYPROJECT = BACKEND_DIR / "pyproject.toml"

PIN_PATTERN = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^ ;\\]+)", re.MULTILINE
)


def _normalize(name: str) -> str:
    base = re.split(r"[\s<>=!~;\[]", name, maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", base).strip().lower()


def _lock_packages(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    packages = {_normalize(m.group(1)): m.group(2) for m in PIN_PATTERN.finditer(text)}
    assert packages, f"Lockfile vazio: {path.name}"
    assert "-e " not in text
    assert "file:///" not in text
    for block in re.split(r"\n(?=[A-Za-z0-9])", text):
        match = PIN_PATTERN.match(block)
        if match:
            assert "--hash=sha256:" in block, f"Sem hash: {match.group(1)}"
    return packages


def _project_requirements() -> tuple[set[str], set[str]]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data["project"]
    runtime = {_normalize(item) for item in project["dependencies"]}
    dev = runtime | {
        _normalize(item) for item in project["optional-dependencies"]["dev"]
    }
    return runtime, dev


def test_lockfiles_existem_e_tem_hashes() -> None:
    assert RUNTIME_LOCK.is_file()
    assert DEV_LOCK.is_file()
    assert _lock_packages(RUNTIME_LOCK)
    assert _lock_packages(DEV_LOCK)


def test_locks_cobrem_dependencias_do_pyproject() -> None:
    runtime, dev = _project_requirements()
    assert runtime <= set(_lock_packages(RUNTIME_LOCK))
    assert dev <= set(_lock_packages(DEV_LOCK))


def test_lock_de_desenvolvimento_inclui_ferramentas() -> None:
    packages = _lock_packages(DEV_LOCK)
    assert {"pytest", "ruff", "mypy", "pytest-asyncio", "httpx"} <= set(packages)


def test_python_alvo_e_312() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    assert data["project"]["requires-python"] == ">=3.12,<3.13"
