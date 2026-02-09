# Decision Log — Example Project

Lightweight record of technical decisions. For significant architectural decisions, use a full [ADR](../adr-template.md).

| # | Date | Facet | Decision | Rationale | Decided By | Codex Ref |
|---|------|-------|----------|-----------|------------|-----------|
| 1 | 2026-01-10 | State Management | Use Pinia for global state in Vue 3 MFEs | Official Vue recommendation, team already uses it in 2 projects, simple API | Frontend Lead | [state-management/options.md](../../facets/state-management/options.md) |
| 2 | 2026-01-10 | Internationalization | Use vue-i18n with JSON translation files | Consistent with other MFEs, lazy-loading per locale supported | Frontend Lead | [internationalization/options.md](../../facets/internationalization/options.md) |
| 3 | 2026-01-12 | Authentication | Keycloak as identity provider | Already deployed for other projects, OIDC compliant, team familiar with admin console | Platform Team | [authentication/options.md](../../facets/authentication/options.md) |
| 4 | 2026-01-15 | API Design | REST with OpenAPI specs, offset-based pagination using Spring Data Pageable | Team expertise is REST, TypeSpec for contract-first, Pageable integrates with Spring Data JPA | Backend Lead | [api-design/options.md](../../facets/api-design/options.md) |
| 5 | 2026-01-18 | Event-Driven | Axon Server for finance domain event sourcing | Finance domain requires full event history and replay, Axon Framework already in use | Backend Lead | [event-driven-architecture/options.md](../../facets/event-driven-architecture/options.md) |
| 6 | 2026-01-20 | Testing | Vitest for unit tests, Playwright for E2E | Vitest native to Vite, fast HMR. Playwright for cross-browser E2E. JUnit 5 + Testcontainers for backend. | Tech Lead | [testing/options.md](../../facets/testing/options.md) |
| 7 | 2026-02-01 | Data Persistence | PostgreSQL with Flyway migrations | Team standard, Flyway over Liquibase for simplicity, Spring Data JPA for repositories | Backend Lead | [data-persistence/options.md](../../facets/data-persistence/options.md) |

## Notes

- Decisions #1 and #2 were made together during the project kickoff — they're low-risk, best-practice choices that didn't warrant full ADRs.
- Decision #3 was straightforward (existing infrastructure), but is referenced by [ADR-001](adr-001-jwt-authentication.md) which covers the more nuanced token strategy decision.
- Decision #4 chose offset-based pagination over cursor-based because the data set is relatively small (<10K records per tenant) and the team is familiar with Spring Data Pageable. If data volume grows significantly, this should be revisited per the [api-design evolution triggers](../../facets/api-design/options.md).
