---
title: Data Persistence
type: facet
last_updated: 2026-02-09
tags: [postgresql, redis, jpa, hibernate, flyway, liquibase, caching, database, migration, spring-data]
---

# Data Persistence

SQL, NoSQL, event sourcing, migrations, caching, data modeling.

## TL;DR

- **Default choice**: PostgreSQL for most applications—excellent data integrity, SQL flexibility, JSONB for document-like needs, mature ecosystem
- **Key principle**: PostgreSQL's JSONB often eliminates need for separate document stores—use MongoDB only when schema flexibility is genuine requirement
- **Watch out for**: Schema migration complexity (use Flyway/Liquibase), N+1 query problems with ORMs (use DataLoader patterns), event sourcing complexity (only use when audit trail is essential)
- **Start here**: [Options](options.md) — Decision matrix covers PostgreSQL, MongoDB, Event Sourcing, plus data access patterns (ORM, Query Builder, Raw SQL) and caching strategies

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Backend Architecture](../backend-architecture/) -- Architecture patterns that drive data decisions
- [Event-Driven Architecture](../event-driven-architecture/) -- Event sourcing and CQRS
- [API Design](../api-design/) -- Pagination and query patterns tied to data layer
- [Performance](../performance/) -- Query optimization and caching
- [Security](../security/) -- Data encryption, access controls, data masking

## Related Experiences

- [Tables & Data Grids](../../experiences/tables-and-data-grids/) -- How data is displayed to users
- [Search & Discovery](../../experiences/search-and-discovery/) -- Search infrastructure and indexing
