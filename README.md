# Engineering Codex

The authoritative reference guide for building modern web applications. A living document of best practices, architectural patterns, decision frameworks, and user experience guidance.

## Purpose

The Engineering Codex provides a faceted, deep-dive reference for every major concern in modern application development. It is designed to:

- **Inform decisions** with structured options, trade-offs, and evaluation criteria
- **Accelerate onboarding** by giving developers a single place to learn how and why things are done
- **Maintain consistency** across projects by establishing shared vocabulary and patterns
- **Evolve with the industry** as a living document that tracks changing best practices

## How to Use This Codex

### Quick Reference

Need a fast answer? Start with [checklists](checklists/) for actionable lists that link to deeper content.

### Making a Decision

1. Find the relevant [facet](facets/) or [experience](experiences/)
2. Read the `options.md` for available approaches
3. Use the `evaluate-options` skill for an interactive walkthrough, or the `compare-options` command for a quick comparison
4. Document your decision using `generate-adr` or the [decision log template](decision-frameworks/decision-log-template.md)

### Learning a Topic

Use the `facet-deep-dive` skill to explore any topic interactively, or read through the five perspectives directly:

- **product.md** -- Business value, user flows, personas, compliance
- **architecture.md** -- Patterns, diagrams, trade-offs, integration points
- **testing.md** -- Test strategies, what to test, tooling categories
- **best-practices.md** -- Language-agnostic principles with stack-specific callouts
- **options.md** -- Decision matrix or recommended practice with alternatives

### Reviewing Your Implementation

Use the `architecture-review` skill to compare your current codebase against codex recommendations.

### Adding New Content

Use the `create-facet` skill to scaffold a new facet or experience, then see [CONTRIBUTING.md](CONTRIBUTING.md) for content guidelines.

## Repository Structure

```
engineering-codex/
├── skills/                  # Interactive Cursor skills
├── commands/                # Lightweight Cursor commands
├── checklists/              # Quick-reference actionable checklists
├── decision-frameworks/     # Evaluation criteria, templates, and decision documentation
├── evolution/               # Architecture scaling journeys and inflection points
├── facets/                  # 18 engineering-focused deep dives
├── experiences/             # 16 user-centric UX perspectives
├── stack-context.md         # Assumed technology landscape
├── glossary.md              # Shared terminology
└── CHANGELOG.md             # Change history
```

## Facets (Engineering)

| # | Facet | Description |
|---|-------|-------------|
| 1 | [Authentication](facets/authentication/) | AuthN/AuthZ, identity, sessions, tokens, OAuth, RBAC, ABAC |
| 2 | [API Design](facets/api-design/) | REST, GraphQL, gRPC, versioning, contracts, documentation |
| 3 | [Frontend Architecture](facets/frontend-architecture/) | SPA, MFE, SSR, component design, routing, build tooling |
| 4 | [Backend Architecture](facets/backend-architecture/) | Layered, hexagonal, CQRS, microservices, monoliths, modulith |
| 5 | [Data Persistence](facets/data-persistence/) | SQL, NoSQL, event sourcing, migrations, caching, data modeling |
| 6 | [State Management](facets/state-management/) | Client state, server state, global vs local, reactive patterns |
| 7 | [Testing](facets/testing/) | Unit, integration, e2e, contract, performance, TDD, BDD |
| 8 | [Security](facets/security/) | OWASP, secrets management, encryption, supply chain |
| 9 | [Observability](facets/observability/) | Logging, metrics, tracing, alerting, dashboards, SLOs |
| 10 | [CI/CD](facets/ci-cd/) | Pipelines, deployment strategies, feature flags, environments |
| 11 | [Performance](facets/performance/) | Frontend perf, backend perf, database optimization, caching |
| 12 | [Internationalization](facets/internationalization/) | i18n, l10n, RTL, currency/date formatting, translation workflows |
| 13 | [Accessibility](facets/accessibility/) | WCAG, ARIA, keyboard navigation, screen readers |
| 14 | [Error Handling](facets/error-handling/) | Error boundaries, retry patterns, circuit breakers, user feedback |
| 15 | [Event-Driven Architecture](facets/event-driven-architecture/) | Messaging, event sourcing, CQRS, choreography vs orchestration |
| 16 | [Developer Experience](facets/developer-experience/) | Tooling, onboarding, documentation, local dev, debugging |
| 17 | [Feature Toggles](facets/feature-toggles/) | Toggle strategies, lifecycle management, rollout patterns |
| 18 | [Refactoring](facets/refactoring/) | When and how to refactor, extraction patterns, safe migration |

## Experiences (User-Centric)

| # | Experience | Description |
|---|------------|-------------|
| 1 | [Onboarding](experiences/onboarding/) | First-time user experience, progressive disclosure, activation |
| 2 | [Navigation](experiences/navigation/) | Information architecture, wayfinding, menus, breadcrumbs |
| 3 | [Search & Discovery](experiences/search-and-discovery/) | Finding content, filters, sorting, recommendations |
| 4 | [Notifications](experiences/notifications/) | Alerts, emails, in-app messages, communication preferences |
| 5 | [Settings & Preferences](experiences/settings-and-preferences/) | User configuration, personalization, account management |
| 6 | [Data Visualization](experiences/data-visualization/) | Charts, dashboards, exports, reporting UX |
| 7 | [Forms & Data Entry](experiences/forms-and-data-entry/) | Input patterns, validation, multi-step flows, inline editing |
| 8 | [Responsive Design](experiences/responsive-design/) | Mobile, tablet, desktop, progressive enhancement |
| 9 | [Content Strategy](experiences/content-strategy/) | Microcopy, help text, empty states, error messages, tone |
| 10 | [Feedback & Support](experiences/feedback-and-support/) | Help systems, feedback collection, support flows |
| 11 | [Multi-Tenancy UX](experiences/multi-tenancy-ux/) | Tenant switching, white-labeling, role-based UI adaptation |
| 12 | [Workflows & Tasks](experiences/workflows-and-tasks/) | Task completion, wizards, progress indicators, bulk actions |
| 13 | [Tables & Data Grids](experiences/tables-and-data-grids/) | Enterprise table patterns, sorting, filtering, pagination |
| 14 | [Permissions UX](experiences/permissions-ux/) | Access control communication, disabled states, request access |
| 15 | [Real-Time & Collaboration](experiences/real-time-and-collaboration/) | Live updates, presence, WebSocket UX, conflict resolution |
| 16 | [Loading & Perceived Performance](experiences/loading-and-perceived-performance/) | Skeleton screens, optimistic UI, progressive loading |

## Skills & Commands

### Skills (Interactive Workflows)

- **evaluate-options** -- Walk through a facet's decision matrix interactively
- **facet-deep-dive** -- Explore a facet or experience topic interactively
- **architecture-review** -- Compare your implementation against codex recommendations
- **create-facet** -- Scaffold a new facet or experience

### Commands (Quick Triggers)

- **compare-options** -- Quick side-by-side option comparison
- **generate-adr** -- Generate an ADR from a codex decision

## Related Resources

- [workspace-standards](../workspace-standards/) -- Cursor rules, implementation skills, scoring, golden paths
- [Stack Context](stack-context.md) -- Assumed technology landscape
- [Glossary](glossary.md) -- Shared terminology
- [Changelog](CHANGELOG.md) -- Document change history
