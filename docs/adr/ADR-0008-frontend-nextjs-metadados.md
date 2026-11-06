# ADR-0008 — Frontend Next.js App Router dirigido por metadados

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** Engenheiro Next.js, Product Designer, CTO
- **Fase:** 1

## Contexto

O produto precisa de um painel administrativo único que atenda segmentos distintos (pizzaria, imobiliária, clínica, etc.) sem duplicar aplicações. As telas devem refletir módulos, campos e permissões configurados no backend.

## Decisão

Usar **Next.js com App Router e TypeScript estrito**, com:

- Route groups `(auth)`, `(superadmin)`, `(tenant)`.
- Server Components por padrão.
- Navegação derivada de um registro de módulos (`lib/navigation.ts`).
- Componentes reutilizáveis e design tokens em CSS.
- Dashboards compostos por módulos habilitados via metadados (Fase 8).
- Enforcement de permissões no backend; o frontend apenas ajusta a UX.

## Consequências

**Positivas**

- Uma única aplicação para todos os segmentos.
- Renderização no servidor e melhor performance inicial.
- Consistência visual e de navegação.

**Negativas**

- Metadados precisam ser estáveis e bem tipados.
- Componentes dinâmicos exigem contratos claros com o backend.
- Risco de complexidade excessiva se o registro de módulos não for disciplinado.

## Regra anti-dados-fictícios

Nenhuma tela exibe números, gráficos ou indicadores inventados. Estados vazios devem ser explícitos. Dados só aparecem quando vindos do backend real.

## Referências

- `docs/ARQUITETURA.md`, seção 9
- `frontend/src/lib/navigation.ts`
