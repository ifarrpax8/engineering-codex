---
title: Frontend Architecture
type: facet
last_updated: 2026-02-09
---

# Frontend Architecture

SPA, MFE, SSR, component design, routing, build tooling.

## TL;DR

- **Default choice**: SPA (Single Page Application) for most applications—simple deployment, unified codebase, excellent developer experience
- **Key principle**: Start simple with SPA, evolve to MFE when team size exceeds 5-7 developers and deployment independence provides value
- **Watch out for**: Deployment coordination overhead as teams grow (MFE solves this but adds complexity), initial bundle size without code splitting, merge conflicts in shared codebase
- **Start here**: [Options](options.md) — Decision matrix helps choose between SPA, MFE, and SSR based on team size, deployment needs, and SEO requirements

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Backend Architecture](../backend-architecture/) -- Frontend-backend alignment (MFE ↔ microservices)
- [State Management](../state-management/) -- Client state patterns tied to architecture
- [API Design](../api-design/) -- How frontend consumes APIs
- [Performance](../performance/) -- Bundle size, loading, rendering
- [Authentication](../authentication/) -- Auth flows in SPA/MFE contexts
- [Internationalization](../internationalization/) -- i18n integration patterns

## Related Experiences

- [Navigation](../../experiences/navigation/) -- Routing and wayfinding patterns
- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Code splitting impact
- [Responsive Design](../../experiences/responsive-design/) -- Layout architecture
