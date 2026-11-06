import type { Metadata } from "next";

import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge } from "@/components/ui/status-badge";

export const metadata: Metadata = {
  title: "Visão geral",
};

interface FoundationItem {
  readonly title: string;
  readonly description: string;
  readonly phase: number;
}

const foundation: readonly FoundationItem[] = [
  {
    title: "Isolamento multi-tenant",
    description:
      "Tenant resolvido no servidor, RLS com contexto transacional e testes de acesso cruzado previstos.",
    phase: 2,
  },
  {
    title: "Segmentos dinâmicos",
    description:
      "Segmentos, modelos operacionais, campos e regras são configuração validada, não código por cliente.",
    phase: 4,
  },
  {
    title: "Agentes desacoplados",
    description:
      "Definição, versões de prompt e adaptadores de provedores separados do domínio de negócio.",
    phase: 6,
  },
  {
    title: "Billing independente",
    description:
      "Preço contratado, valor faturado e dinheiro recebido tratados como grandezas distintas.",
    phase: 10,
  },
];

export default function AdminOverviewPage() {
  return (
    <div className="page">
      <section className="page-intro">
        <div>
          <StatusBadge tone="positive">FASE 1 concluída</StatusBadge>
          <h2>Fundação da plataforma</h2>
          <p>
            A estrutura arquitetural, o modelo de dados e os esqueletos de
            backend e frontend estão preparados. Nenhum indicador é exibido sem
            dados reais do backend.
          </p>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Indicadores operacionais</h3>
            <p className="panel-subtitle">
              Métricas de clientes, receita e utilização serão exibidas aqui.
            </p>
          </div>
          <StatusBadge tone="warning">FASE 3</StatusBadge>
        </div>
        <EmptyState
          title="Sem dados disponíveis"
          description="Os indicadores serão calculados a partir do banco de dados quando os módulos de tenants, billing e uso estiverem implementados."
          hint="Nenhum dado fictício é apresentado como indicador real."
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Fundamentos entregues</h3>
            <p className="panel-subtitle">
              Decisões estruturais registradas e preparadas para as próximas
              fases.
            </p>
          </div>
        </div>
        <div className="foundation-grid">
          {foundation.map((item) => (
            <article className="foundation-card" key={item.title}>
              <div className="foundation-card-head">
                <h4>{item.title}</h4>
                <StatusBadge tone="info">FASE {item.phase}</StatusBadge>
              </div>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
