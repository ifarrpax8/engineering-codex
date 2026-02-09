# Changelog

All notable changes to the Engineering Codex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to date-based versioning.

## [2026-02-09] - Checklists, Evolution Guides, and Reading Paths

### Added

- **Security Review Checklist** — auth, input validation, secrets, data protection, browser security, dependencies, multi-tenancy
- **Accessibility Audit Checklist** — WCAG 2.1 AA compliance covering perceivable, operable, understandable, robust, automated and manual testing
- **API Design Review Checklist** — naming, request/response, security, documentation, performance, backwards compatibility
- **Evolution: Manual to Automated Testing** — 5-stage testing maturity model with triggers, transitions, and anti-patterns
- **Evolution: Component Library to Design System** — 5-stage design system maturity model from no system to platform-level governance
- **Reading Paths** — role-based navigation guides for new developers, QA engineers, architects, product managers, DevOps engineers, and tech leads

### Fixed

- Stale links in code-review and new-feature checklists pointing to old `facets/refactoring/` (now `facets/refactoring-and-extraction/`)

---

## [2026-02-09] - Full Content Population

### Added

- Full content for all 19 engineering facets (7 files each: product, architecture, testing, best-practices, gotchas, options)
- Full content for all 17 user-centric experiences (7 files each: product, architecture, testing, best-practices, gotchas, options)
- TL;DR sections on every facet and experience README for quick reference
- Table of contents on every perspective file for navigation
- QA and Test Engineer Perspective section in every testing.md file
- `operations.md` for 7 select facets: data-persistence, backend-architecture, event-driven-architecture, observability, security, ci-cd, configuration-management
- `gotchas.md` added to all facets and experiences as the 7th perspective file
- `work-management` facet covering ticket systems, types, workflows, estimation, and sprints
- `design-consistency-and-visual-identity` experience covering design tokens, component libraries, theming, and MFE consistency
- Azure DevOps Pipelines added as a CI/CD platform option in ci-cd/options.md
- `search-and-discovery` experience enhanced with retroactive TL;DR, TOC, gotchas, and QA perspective
- Expanded glossary with additional terms

### Facets Populated (19)

1. Authentication -- session/JWT/OAuth, RBAC/ABAC/FGA
2. API Design -- REST/GraphQL/gRPC, pagination, HATEOAS, search vs filtering
3. Frontend Architecture -- SPA/MFE/SSR, Module Federation, Propulsion
4. Backend Architecture -- Monolith/Modulith/Microservices, Hexagonal, DDD
5. Data Persistence -- PostgreSQL, Event Sourcing, Flyway, Redis caching
6. State Management -- Pinia/Zustand, TanStack Query, MFE state
7. Testing -- Test Pyramid/Diamond, TDD/BDD, Mutation Testing
8. Security -- OWASP Top 10, secrets management, dependency scanning
9. Observability -- OpenTelemetry, structured logging, SLOs, alerting
10. CI/CD -- GitHub Actions, Azure DevOps, deployment strategies, DORA
11. Performance -- Core Web Vitals, k6, Redis caching, JVM tuning
12. Internationalization -- vue-i18n, react-intl, Spring MessageSource, RTL
13. Accessibility -- WCAG 2.1 AA, ARIA, axe-core, Propulsion
14. Error Handling -- RFC 7807, circuit breakers, error boundaries, Sentry
15. Event-Driven Architecture -- Kafka/RabbitMQ, Axon sagas, idempotency
16. Feature Toggles -- categories, lifecycle, OpenFeature, database-backed
17. Configuration Management -- Twelve-Factor, Spring profiles, Vault
18. Refactoring & Extraction -- Strangler Fig, characterization tests, code smells
19. Work Management -- Jira/GitHub/Azure Boards, estimation, sprint management

### Experiences Populated (17)

1. Onboarding -- activation funnels, guided tours, progressive disclosure
2. Navigation -- wayfinding, breadcrumbs, MFE routing, mobile nav
3. Search & Discovery -- OpenSearch, PostgreSQL FTS, autocomplete
4. Notifications -- multi-channel delivery, real-time transport, fatigue
5. Settings & Preferences -- hierarchy, real-time propagation, themes
6. Data Visualization -- Chart.js, dashboards, export, responsive charts
7. Forms & Data Entry -- multi-page wizards, validation, draft persistence
8. Responsive Design -- mobile-first, container queries, touch targets
9. Content Strategy -- microcopy, empty states, error messages, tone
10. Feedback & Support -- in-app widgets, knowledge base, session replay
11. Multi-Tenancy UX -- tenant switching, white-labeling, impersonation
12. Workflows & Tasks -- state machines, approval chains, bulk operations
13. Tables & Data Grids -- TanStack Table, server-side pagination, virtual scroll
14. Permissions UX -- hide vs disable, request access, RBAC/FGA in UI
15. Real-Time & Collaboration -- WebSocket/STOMP, presence, CRDTs
16. Loading & Perceived Performance -- skeleton screens, optimistic updates
17. Design Consistency & Visual Identity -- design tokens, Propulsion/MUI, MFE consistency

## [2026-02-09] - Initial Scaffolding

### Added

- Repository scaffolding with full directory structure
- 4 Cursor skills: evaluate-options, facet-deep-dive, architecture-review, create-facet
- 2 Cursor commands: compare-options, generate-adr
- 5 checklists: new-project, production-readiness, new-feature, code-review, incident-response
- Decision frameworks with 5 evaluation criteria, templates, and decision documentation guides
- 3 evolution guides: monolith-to-microservices, spa-to-mfe, scaling-triggers
- Stack context, glossary, and contributing guidelines
