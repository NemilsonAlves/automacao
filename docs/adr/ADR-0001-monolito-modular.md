# ADR-0001 — Monólito modular como estilo arquitetural

- **Status:** Aceita
- **Data:** 06/11/2026
- **Decisores:** CTO, Arquiteto de Software
- **Fase:** 1

## Contexto

A AgencIA NTM é uma plataforma SaaS com domínios distintos (identidade, segmentos, regras, agentes, billing, uso de IA, auditoria), porém em estágio inicial de produto. Microsserviços introduziriam custo operacional, complexidade transacional e latência de comunicação sem benefício comprovado.

## Decisão

Adotar um **monólito modular**: um único deploy de backend, organizado por domínios com fronteiras explícitas, dependências declaradas e comunicação por casos de uso internos.

Cada módulo segue as camadas `api → application → domain`, com `infrastructure` implementando portas do domínio. O grafo de dependências é acíclico e validado por teste.

## Consequências

**Positivas**

- Transações únicas para operações financeiras e de configuração.
- Menor custo operacional e de infraestrutura.
- Refatoração e evolução mais simples no início.
- Fronteiras preservam a possibilidade de extração futura.

**Negativas**

- Disciplina arquitetural necessária para evitar acoplamento.
- Escala vertical antes de horizontal.
- Um deploy afeta todos os domínios.

## Alternativas consideradas

- **Microsserviços:** rejeitado por complexidade prematura.
- **Monólito sem módulos:** rejeitado por risco de acoplamento e baixa manutenibilidade.

## Referências

- `docs/ARQUITETURA.md`
- `backend/app/modules/registry.py`
