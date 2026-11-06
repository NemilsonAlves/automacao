export type NavigationStatus = "available" | "planned";

export interface NavigationItem {
  readonly key: string;
  readonly label: string;
  readonly description: string;
  readonly phase: number;
  readonly status: NavigationStatus;
  readonly href?: string;
}

export interface NavigationSection {
  readonly title: string;
  readonly items: readonly NavigationItem[];
}

export const navigation: readonly NavigationSection[] = [
  {
    title: "Plataforma",
    items: [
      {
        key: "overview",
        label: "Visão geral",
        description: "Fundação arquitetural da plataforma.",
        phase: 1,
        status: "available",
        href: "/admin",
      },
      {
        key: "platform_administration",
        label: "SuperAdmin",
        description: "Administração central da plataforma.",
        phase: 3,
        status: "planned",
      },
      {
        key: "segments",
        label: "Segmentos",
        description: "Segmentos de mercado e modelos operacionais.",
        phase: 4,
        status: "planned",
      },
      {
        key: "business_rules",
        label: "Regras de negócio",
        description: "Regras, workflows e validações versionadas.",
        phase: 5,
        status: "planned",
      },
      {
        key: "agent_management",
        label: "Agentes de IA",
        description: "Definições, prompts, simulador e publicação.",
        phase: 6,
        status: "planned",
      },
    ],
  },
  {
    title: "Clientes",
    items: [
      {
        key: "tenants",
        label: "Empresas",
        description: "Cadastro e ciclo de vida dos tenants.",
        phase: 2,
        status: "planned",
      },
      {
        key: "dynamic_dashboards",
        label: "Painéis",
        description: "Painéis dinâmicos por segmento e plano.",
        phase: 8,
        status: "planned",
      },
    ],
  },
  {
    title: "Comercial",
    items: [
      {
        key: "plans_subscriptions",
        label: "Planos",
        description: "Planos, componentes e assinaturas.",
        phase: 9,
        status: "planned",
      },
      {
        key: "billing",
        label: "Faturamento",
        description: "Faturas, eventos faturáveis e inadimplência.",
        phase: 10,
        status: "planned",
      },
      {
        key: "ai_usage_costs",
        label: "Custos de IA",
        description: "Tokens, custos e rentabilidade.",
        phase: 11,
        status: "planned",
      },
    ],
  },
  {
    title: "Governança",
    items: [
      {
        key: "audit_logs",
        label: "Auditoria",
        description: "Trilha imutável de operações sensíveis.",
        phase: 2,
        status: "planned",
      },
      {
        key: "analytics",
        label: "Analytics",
        description: "Indicadores agregados e relatórios.",
        phase: 11,
        status: "planned",
      },
    ],
  },
];

export const plannedModules = navigation
  .flatMap((section) => section.items)
  .filter((item) => item.status === "planned");
