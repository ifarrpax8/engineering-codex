# Engineering Facets

19 engineering-focused deep dives, each covering a critical concern in modern application development. Every facet provides seven perspectives: product, architecture, testing, best practices, gotchas, and options.

## Facet Index

| # | Facet | Description | Type |
|---|-------|-------------|------|
| 1 | [Authentication](authentication/) | AuthN/AuthZ, identity, sessions, tokens, OAuth, RBAC, ABAC | Security |
| 2 | [API Design](api-design/) | REST, GraphQL, gRPC, API versioning, contracts, documentation | Communication |
| 3 | [Frontend Architecture](frontend-architecture/) | SPA, MFE, SSR, component design, routing, build tooling | Architecture |
| 4 | [Backend Architecture](backend-architecture/) | Layered, hexagonal, CQRS, microservices, monoliths, modulith | Architecture |
| 5 | [Data Persistence](data-persistence/) | SQL, NoSQL, event sourcing, migrations, caching, data modeling | Data |
| 6 | [State Management](state-management/) | Client state, server state, global vs local, reactive patterns | Data |
| 7 | [Testing](testing/) | Unit, integration, e2e, contract, performance, TDD, BDD | Quality |
| 8 | [Security](security/) | OWASP, secrets management, encryption, supply chain | Security |
| 9 | [Observability](observability/) | Logging, metrics, tracing, alerting, dashboards, SLOs | Operations |
| 10 | [CI/CD](ci-cd/) | Pipelines, deployment strategies, feature flags, environments | Operations |
| 11 | [Performance](performance/) | Frontend perf, backend perf, database optimization, caching | Quality |
| 12 | [Internationalization](internationalization/) | i18n, l10n, RTL, currency/date formatting, translation workflows | UX |
| 13 | [Accessibility](accessibility/) | WCAG, ARIA, keyboard navigation, screen readers | UX |
| 14 | [Error Handling](error-handling/) | Error boundaries, retry patterns, circuit breakers, user feedback | Resilience |
| 15 | [Event-Driven Architecture](event-driven-architecture/) | Messaging, event sourcing, CQRS, choreography vs orchestration | Architecture |
| 16 | [Feature Toggles](feature-toggles/) | Toggle strategies, lifecycle management, rollout patterns | Operations |
| 17 | [Configuration Management](configuration-management/) | Externalized config, secrets, profiles, environment management | Operations |
| 18 | [Refactoring & Extraction](refactoring-and-extraction/) | When and how to refactor, extraction patterns, safe migration | Process |
| 19 | [Work Management](work-management/) | Ticket systems, ticket types, workflows, estimation, sprints | Process |

## How to Navigate

- **By topic:** Find the facet that matches your concern in the table above
- **By type:** Facets are loosely grouped by type (Architecture, Security, Quality, etc.)
- **By checklist:** Start with a [checklist](../checklists/) and follow links to relevant facets
- **Interactively:** Use the `facet-deep-dive` skill to explore any facet with guided questions

## Each Facet Contains

| File | Perspective | Focus |
|------|------------|-------|
| `product.md` | Product | Business value, user flows, personas, compliance |
| `architecture.md` | Architecture | Patterns, diagrams, trade-offs, integration points |
| `testing.md` | Testing | Strategies, what to test, pyramid, tooling categories |
| `best-practices.md` | Best Practices | Language-agnostic principles, anti-patterns |
| `gotchas.md` | Gotchas | Common pitfalls, traps, and lessons learned |
| `options.md` | Options | Decision matrix or recommended practice with alternatives |

## Adding New Facets

Use the `create-facet` skill to scaffold a new facet with all required files.
