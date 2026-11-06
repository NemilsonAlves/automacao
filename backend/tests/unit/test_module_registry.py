"""Testes estruturais do manifesto de módulos."""

from __future__ import annotations

import importlib

import pytest
from app.modules.registry import (
    MODULES,
    ModuleRegistryError,
    ModuleSpec,
    modules_by_key,
    topological_order,
    validate_registry,
)


def test_manifesto_tem_24_modulos() -> None:
    assert len(MODULES) == 24


def test_chaves_sao_unicas() -> None:
    keys = [spec.key for spec in MODULES]
    assert len(keys) == len(set(keys))


def test_dependencias_existem() -> None:
    known = set(modules_by_key())
    for spec in MODULES:
        assert set(spec.depends_on) <= known, spec.key


def test_grafo_e_aciclico_e_ordem_respeita_dependencias() -> None:
    order = topological_order()
    position = {key: index for index, key in enumerate(order)}
    for spec in MODULES:
        for dependency in spec.depends_on:
            assert position[dependency] < position[spec.key]


def test_registry_rejeita_modulo_duplicado() -> None:
    duplicated = (MODULES[0], MODULES[0])
    with pytest.raises(ModuleRegistryError):
        validate_registry(duplicated)


def test_registry_rejeita_dependencia_inexistente() -> None:
    invalid = ModuleSpec(
        key="invalido",
        name="Inválido",
        responsibility="Teste",
        phase=2,
        depends_on=("modulo_que_nao_existe",),
    )
    with pytest.raises(ModuleRegistryError):
        validate_registry((*MODULES, invalid))


def test_pacotes_dos_modulos_sao_importaveis() -> None:
    for spec in MODULES:
        assert importlib.import_module(spec.package) is not None
