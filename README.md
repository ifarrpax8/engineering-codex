# Engineering Codex

The authoritative reference guide for building modern web applications. A living document of best practices, architectural patterns, decision frameworks, and user experience guidance.

## Purpose

The Engineering Codex provides a faceted, deep-dive reference for every major concern in modern application development. It is designed to:

- **Inform decisions** with structured options, trade-offs, and evaluation criteria
- **Accelerate onboarding** by giving developers a single place to learn how and why things are done
- **Maintain consistency** across projects by establishing shared vocabulary and patterns
- **Evolve with the industry** as a living document that tracks changing best practices

## How to Use This Codex

### By Role

New to the codex? Start with [Reading Paths](reading-paths.md) for a curated route based on your role: developer, QA engineer, architect, product manager, DevOps engineer, or tech lead.

### Quick Reference

Need a fast answer? Start with [checklists](checklists/) for actionable lists that link to deeper content.

### Making a Decision

1. Find the relevant [facet](facets/) or [experience](experiences/)
2. Read the `options.md` for available approaches
3. Use the `evaluate-options` skill for an interactive walkthrough, or the `compare-options` command for a quick comparison
4. Document your decision using `generate-adr` or the [decision log template](decision-frameworks/decision-log-template.md)

### Learning a Topic

Use the `facet-deep-dive` skill to explore any topic interactively, or read through the seven perspectives directly:

- **product.md** -- Business value, user flows, personas, compliance
- **architecture.md** -- Patterns, diagrams, trade-offs, integration points
- **testing.md** -- Test strategies, what to test, tooling categories, QA perspective
- **best-practices.md** -- Language-agnostic principles with stack-specific callouts
- **gotchas.md** -- Common pitfalls, traps, and lessons learned
- **options.md** -- Decision matrix or recommended practice with alternatives
- **operations.md** -- Day-2 operational concerns (select facets only)

### Reviewing Your Implementation

Use the `architecture-review` skill to compare your current codebase against codex recommendations.

### Adding New Content

Use the `create-facet` skill to scaffold a new facet or experience, then see [CONTRIBUTING.md](CONTRIBUTING.md) for content guidelines.

## Repository Structure

```
engineering-codex/
├── .cursor/
│   ├── skills/              # Interactive Cursor skills (auto-discovered)
│   └── agents/              # Custom subagents (codex-navigator)
├── commands/                # Lightweight Cursor commands
├── checklists/              # Quick-reference actionable checklists
├── decision-frameworks/     # Evaluation criteria, templates, and decision documentation
├── evolution/               # Architecture scaling journeys and inflection points
├── facets/                  # 21 engineering-focused deep dives
├── experiences/             # 17 user-centric UX perspectives
├── pax8-context/            # Pax8-specific ADR overlay (optional, for Pax8 projects)
├── tech-radar.md            # Technology radar (industry-general)
├── tech-radar-pax8.md       # Technology radar (Pax8 overlay)
├── tech-radar.json          # Zalando-compatible radar export
├── reading-paths.md         # Role-based navigation guides
├── tag-index.md             # Auto-generated cross-reference of tags
├── stack-context.md         # Assumed technology landscape
├── glossary.md              # Shared terminology
├── scripts/                 # Utility scripts (tag index, link validation)
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
| 16 | [Feature Toggles](facets/feature-toggles/) | Toggle strategies, lifecycle management, rollout patterns |
| 17 | [Configuration Management](facets/configuration-management/) | Externalized config, secrets, profiles, environment management |
| 18 | [Refactoring & Extraction](facets/refactoring-and-extraction/) | When and how to refactor, extraction patterns, safe migration |
| 19 | [Work Management](facets/work-management/) | Ticket systems, ticket types, workflows, estimation, sprints |
| 20 | [Dependency Management](facets/dependency-management/) | Evaluation, versioning, upgrades, license compliance, scanning |
| 21 | [Repository & Code Governance](facets/repository-governance/) | Branch strategies, CODEOWNERS, PR policies, repo lifecycle |

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
| 17 | [Design Consistency & Visual Identity](experiences/design-consistency-and-visual-identity/) | Design tokens, component libraries, theming, UI cohesion |

## Skills & Commands

### Skills (Interactive Workflows)

- **evaluate-options** -- Walk through a facet's decision matrix interactively
- **facet-deep-dive** -- Explore a facet or experience topic interactively
- **architecture-review** -- Compare your implementation against codex recommendations
- **create-facet** -- Scaffold a new facet or experience
- **checklist-runner** -- Run a codex checklist interactively against your project
- **experience-audit** -- Audit your frontend against an experience's UX guidelines
- **onboarding-guide** -- Generate a personalised reading path for a project
- **sync-pax8-adrs** -- Diff ADR repo against standards map to surface new/changed/superseded ADRs
- **content-freshness-audit** -- Check content age, technology references, and industry shifts
- **refresh-tech-radar** -- Regenerate the tech radar from current codex and Pax8 content

### Commands (Quick Triggers)

- **compare-options** -- Quick side-by-side option comparison
- **generate-adr** -- Generate an ADR from a codex decision
- **gotcha-check** -- Instantly surface gotchas for any facet or experience
- **generate-checklist** -- Create a project-specific checklist tailored to your stack
- **pax8-standard** -- Surface Pax8-specific standards and deprecated technologies for any facet
- **validate-links** -- Scan for broken internal links and anchor references
- **what-should-i-read** -- Map a task description to relevant codex content

## Getting Started

1. Add `~/Development/engineering-codex` to your Cursor workspace
2. (Optional) Add `~/Development/workspace-standards` to the same workspace for implementation skills, scoring, and golden paths
3. Reload the Cursor window — skills and subagents are auto-discovered from `.cursor/skills/` and `.cursor/agents/`
4. (Optional) Run the workspace-standards setup script to install global rules:
   ```bash
   cd ~/Development/workspace-standards
   ./scripts/setup-skills.sh
   ```

### Skills and Subagents

Cursor auto-discovers skills and subagents from `.cursor/` when the repo is in the workspace. No manual registration required.

| Type | Auto-discovered |
|------|-----------------|
| Skills (see `.cursor/skills/`) | Yes |
| Subagents (`codex-navigator`) | Yes |

Invoke the subagent explicitly with `/codex-navigator` or let the agent delegate automatically.

Example prompts:
- "What are the gotchas for event-driven architecture?"
- "Compare options for state management"
- "What's the Pax8 standard for observability?"
- "What should I read before adding pagination?"
- "Generate an ADR for our authentication decision"
- "Generate a production readiness checklist for currency-manager"

## Related Resources

- [workspace-standards](../workspace-standards/) -- Cursor rules, implementation skills, scoring, golden paths
- [Stack Context](stack-context.md) -- Assumed technology landscape
- [Glossary](glossary.md) -- Shared terminology
- [Changelog](CHANGELOG.md) -- Document change history
