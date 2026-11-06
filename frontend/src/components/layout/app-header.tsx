import { StatusBadge } from "@/components/ui/status-badge";

export function AppHeader() {
  return (
    <header className="app-header">
      <div>
        <p className="app-header-eyebrow">Administração</p>
        <h1 className="app-header-title">Painel AgencIA NTM</h1>
      </div>
      <div className="app-header-meta">
        <StatusBadge tone="info">Fundação arquitetural</StatusBadge>
        <StatusBadge tone="neutral">FASE 1</StatusBadge>
      </div>
    </header>
  );
}
