---
title: Backend Architecture
type: facet
last_updated: 2026-02-09
---

# Backend Architecture

Layered, hexagonal, CQRS, microservices, monoliths, modulith.

## TL;DR

- **Default choice**: Monolith for < 5 developers, Modulith for 5-15 developers, Microservices for 15+ developers—match deployment architecture to team size
- **Key principle**: Start simple, evolve when triggers are reached—don't optimize prematurely for scale you don't have yet
- **Watch out for**: Premature microservices (high operational complexity without team size justification), deployment conflicts in monoliths as teams grow, shared database coupling in microservices
- **Start here**: [Options](options.md) — Decision matrix covers deployment architectures (Monolith, Modulith, Microservices) and internal patterns (Layered, Hexagonal, CQRS)

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Frontend Architecture](../frontend-architecture/) -- Frontend-backend alignment
- [API Design](../api-design/) -- How backend exposes APIs
- [Data Persistence](../data-persistence/) -- Storage patterns tied to architecture
- [Event-Driven Architecture](../event-driven-architecture/) -- Messaging and CQRS patterns
- [Authentication](../authentication/) -- Auth at the service level
- [Observability](../observability/) -- Monitoring distributed systems

## Related Experiences

- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Backend response time impact
- [Real-Time & Collaboration](../../experiences/real-time-and-collaboration/) -- WebSocket and event patterns
