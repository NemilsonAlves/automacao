"""Manifesto dos módulos de domínio e suas dependências.

O manifesto é a fonte de verdade das fronteiras arquiteturais. Os testes
estruturais garantem unicidade, existência das dependências e ausência de
ciclos. Nenhum módulo implementa negócio na FASE 1.
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_PHASE = 12


@dataclass(frozen=True, slots=True)
class ModuleSpec:
    """Metadados de um módulo de domínio."""

    key: str
    name: str
    responsibility: str
    phase: int
    depends_on: tuple[str, ...] = ()

    @property
    def package(self) -> str:
        """Caminho de importação do pacote do módulo."""
        return f"{__package__}.{self.key}"


class ModuleRegistryError(ValueError):
    """Manifesto de módulos inconsistente."""


MODULES: tuple[ModuleSpec, ...] = (
    ModuleSpec(
        key="identity_access",
        name="Identity & Access",
        responsibility="Usuários, credenciais, sessões, JWT/refresh e RBAC.",
        phase=2,
    ),
    ModuleSpec(
        key="audit_logs",
        name="Audit Logs",
        responsibility="Trilha de auditoria imutável de operações sensíveis.",
        phase=2,
    ),
    ModuleSpec(
        key="ai_providers",
        name="AI Providers",
        responsibility="Porta e adaptadores para provedores de LLM.",
        phase=6,
    ),
    ModuleSpec(
        key="tenants",
        name="Tenants",
        responsibility="Cadastro e ciclo de vida da empresa contratante.",
        phase=2,
        depends_on=("identity_access", "audit_logs"),
    ),
    ModuleSpec(
        key="modules_permissions",
        name="Modules & Permissions",
        responsibility="Catálogo de módulos, habilitação e permissões por tenant.",
        phase=8,
        depends_on=("identity_access",),
    ),
    ModuleSpec(
        key="segments",
        name="Segments",
        responsibility="Segmentos de mercado, configuração e versionamento.",
        phase=4,
        depends_on=("audit_logs",),
    ),
    ModuleSpec(
        key="business_models",
        name="Business Models",
        responsibility="Modelos operacionais por segmento.",
        phase=4,
        depends_on=("segments",),
    ),
    ModuleSpec(
        key="dynamic_fields",
        name="Dynamic Fields",
        responsibility="Campos, formulários e validações configuráveis.",
        phase=4,
        depends_on=("segments",),
    ),
    ModuleSpec(
        key="business_rules",
        name="Business Rules",
        responsibility="Regras versionadas e motor controlado de avaliação.",
        phase=5,
        depends_on=("segments", "dynamic_fields"),
    ),
    ModuleSpec(
        key="workflows",
        name="Workflows",
        responsibility="Estados operacionais, transições e ações permitidas.",
        phase=5,
        depends_on=("business_rules",),
    ),
    ModuleSpec(
        key="knowledge_base",
        name="Knowledge Base",
        responsibility="Fontes de conhecimento isoladas por tenant.",
        phase=6,
        depends_on=("tenants", "identity_access"),
    ),
    ModuleSpec(
        key="tools_integrations",
        name="Tools & Integrations",
        responsibility="Registro de ferramentas e integrações autorizadas.",
        phase=6,
        depends_on=("tenants", "identity_access"),
    ),
    ModuleSpec(
        key="agent_management",
        name="Agent Management",
        responsibility="Definições, instâncias, prompts versionados, simulador e publicação.",
        phase=6,
        depends_on=(
            "segments",
            "business_models",
            "business_rules",
            "ai_providers",
            "knowledge_base",
            "tools_integrations",
        ),
    ),
    ModuleSpec(
        key="agent_memory",
        name="Agent Memory",
        responsibility="Configuração e ciclo de vida de memória por agente e tenant.",
        phase=6,
        depends_on=("agent_management",),
    ),
    ModuleSpec(
        key="ai_usage_costs",
        name="AI Usage & Costs",
        responsibility="Medição de tokens, custo, limites e rentabilidade.",
        phase=11,
        depends_on=("agent_management",),
    ),
    ModuleSpec(
        key="plans_subscriptions",
        name="Plans & Subscriptions",
        responsibility="Planos, componentes de cobrança e assinaturas.",
        phase=9,
        depends_on=("segments",),
    ),
    ModuleSpec(
        key="contracts",
        name="Contracts",
        responsibility="Contratos, vigência, reajustes e vínculo com planos.",
        phase=9,
        depends_on=("tenants", "plans_subscriptions"),
    ),
    ModuleSpec(
        key="billing",
        name="Billing",
        responsibility="Ciclos, faturas, itens, eventos faturáveis e inadimplência.",
        phase=10,
        depends_on=("contracts", "plans_subscriptions", "tenants"),
    ),
    ModuleSpec(
        key="payments",
        name="Payments",
        responsibility="Recebimento, estornos, conciliação e adaptadores de pagamento.",
        phase=10,
        depends_on=("billing",),
    ),
    ModuleSpec(
        key="financial_management",
        name="Financial Management",
        responsibility="Visão financeira consolidada, créditos, descontos e conciliação.",
        phase=11,
        depends_on=("billing", "payments", "ai_usage_costs"),
    ),
    ModuleSpec(
        key="analytics",
        name="Analytics",
        responsibility="Indicadores agregados e relatórios.",
        phase=11,
        depends_on=("tenants", "billing", "ai_usage_costs", "audit_logs"),
    ),
    ModuleSpec(
        key="notifications",
        name="Notifications",
        responsibility="Notificações internas e para tenants.",
        phase=12,
        depends_on=("identity_access", "tenants"),
    ),
    ModuleSpec(
        key="dynamic_dashboards",
        name="Dynamic Dashboards",
        responsibility="Composição de painéis por módulo, segmento e permissão.",
        phase=8,
        depends_on=("modules_permissions", "segments"),
    ),
    ModuleSpec(
        key="platform_administration",
        name="Platform Administration",
        responsibility="Administração central da plataforma (SuperAdmin).",
        phase=3,
        depends_on=("identity_access", "tenants", "audit_logs"),
    ),
)


def validate_registry(modules: tuple[ModuleSpec, ...] = MODULES) -> None:
    """Valida unicidade, dependências, fases e ausência de ciclos."""
    keys = [spec.key for spec in modules]
    if len(keys) != len(set(keys)):
        raise ModuleRegistryError("Chaves de módulo duplicadas.")
    known = set(keys)
    for spec in modules:
        if not spec.key or not spec.name or not spec.responsibility:
            raise ModuleRegistryError(f"Módulo incompleto: {spec.key!r}.")
        if not 1 <= spec.phase <= MAX_PHASE:
            raise ModuleRegistryError(f"Fase inválida para {spec.key}: {spec.phase}.")
        for dependency in spec.depends_on:
            if dependency == spec.key:
                raise ModuleRegistryError(f"Módulo {spec.key} depende de si mesmo.")
            if dependency not in known:
                raise ModuleRegistryError(
                    f"Módulo {spec.key} depende de inexistente: {dependency}."
                )
    topological_order(modules)


def topological_order(modules: tuple[ModuleSpec, ...] = MODULES) -> tuple[str, ...]:
    """Retorna a ordem topológica das dependências ou falha em caso de ciclo."""
    pending: dict[str, set[str]] = {
        spec.key: set(spec.depends_on) for spec in modules
    }
    order: list[str] = []
    while pending:
        ready = sorted(key for key, deps in pending.items() if not deps)
        if not ready:
            raise ModuleRegistryError(
                "Ciclo de dependências detectado entre módulos: "
                + ", ".join(sorted(pending))
            )
        for key in ready:
            order.append(key)
            del pending[key]
        for dependencies in pending.values():
            dependencies.difference_update(ready)
    return tuple(order)


def modules_by_key(
    modules: tuple[ModuleSpec, ...] = MODULES,
) -> dict[str, ModuleSpec]:
    """Indexa os módulos pela chave."""
    return {spec.key: spec for spec in modules}


validate_registry()
