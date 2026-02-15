# Changelog

All notable changes to the Engineering Codex will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to date-based versioning.

## [2026-02-14] - Skills Suite Consolidation

### Changed

- **Eliminated wrapper hop**: Consolidated all 10 skills from a two-file pattern (`skills/{name}/SKILL.md` + `.cursor/skills/{name}/SKILL.md` wrapper) to a single-file pattern (`.cursor/skills/{name}/SKILL.md` only)
- **Deleted top-level `skills/` directory**: All skill implementations now live exclusively under `.cursor/skills/`
- **Shortened frontmatter descriptions** to under 20 words for faster Cursor routing (all 10 skills)
- **Added "When NOT to Use" sections** with cross-references to sibling skills for disambiguation (all 10 skills)
- **Added Verification sections** with phase-specific checkpoints (all 10 skills)
- **Added Worked Examples** with Input, Key steps, and Output excerpt (all 10 skills)
- **`CONTRIBUTING.md`**: Updated to document single-file skill pattern, removed "Wrappers Over Symlinks" section, added new required sections
- **`README.md`**: Updated directory tree to remove top-level `skills/` and wrapper references

### Added

- **`SKILLS.md`**: Root-level index listing all 10 skills with descriptions and paths

### Fixed

- Fixed `../../facets/` links in content-freshness-audit worked example (should be `../../../facets/`)
- Fixed `engineering-codex/stack-context.md` links in onboarding-guide template (should be `../../../stack-context.md`)
- Fixed experience-audit "7 perspective files" to "6 perspective files" (excluding README)
- Fixed create-facet "6 required template files" to "7" (including README)

---

## [2026-02-13] - Development Practices Alignment

### Changed

- **facets/observability/best-practices.md**: Added Structured Logging (12-factor, JSON format, standard fields), Log Message Quality (specific/actionable messages, no sensitive data), Contextual Logging (MDC with common keys), Exception Handling in Logs (anti-patterns: swallowing, dropping stack traces), Pax8 stack callout for KotlinLogging, lazy evaluation, RFC-0029
- **facets/observability/architecture.md**: Added Logging Architecture section (centralized aggregation pipeline, W3C Trace Context correlation, retention policies), Pax8 stack callout for SumoLogic
- **facets/observability/gotchas.md**: Added 5 gotchas: Logging Sensitive Data, Excessive Logging in Hot Paths, Swallowing Exceptions, Inconsistent Log Formats, String Concatenation in Log Statements
- **facets/backend-architecture/best-practices.md**: Added Domain-Driven Design in Microservices (bounded contexts, aggregate scoping), CQRS (command/query separation), Aggregate Root Design (no service per table, repositories on aggregate roots only), Naming Conventions (Commands/Events/Views not DTOs, verb-like service names), Event-Driven Patterns, Pax8 stack callout for Donut Manager reference architecture and Axon Framework
- **facets/backend-architecture/architecture.md**: Added Microservice Construction Pattern (Controller → Command Handlers + Query Services → Repositories → Domain Model)
- **facets/backend-architecture/gotchas.md**: Added 4 gotchas: One Service Per Database Table, Repositories for Child Entities, Generic DTO Naming, Synchronous Cross-Context Coupling
- **facets/frontend-architecture/best-practices.md**: Added Code Readability Over Brevity, Service Layer Design (object destructuring), Promise and Async Handling, Component Architecture (SFC, feature-based), File Naming Conventions, Build and Bundle Optimisation, Testing Strategy (unit/component/E2E/visual regression, 80% coverage), State Management, Pax8 stack callout for ESLint (Airbnb/Vue Recommended), Vuex/Pinia, Chromatic
- **facets/frontend-architecture/architecture.md**: Added Micro-Frontend Implementation Guidelines, Security in Frontend (CSP, dependency audits)
- **facets/frontend-architecture/gotchas.md**: Added 5 gotchas: Nested Ternary Operators, Parameter Explosion in Service Calls, Nested .then() Chains, Lodash When Native JS Suffices, Console.log in Production
- **facets/ci-cd/best-practices.md**: Added Environment Strategy (dev/staging/prod), Immutable Artifacts (container images, no modification between build and deploy), Continuous Delivery Practices (automate everything, no manual deploys), Release Process (independent vs scheduled), Pax8 stack callout for GitHub Actions, ArgoCD, Atlantis, LaunchDarkly
- **facets/feature-toggles/best-practices.md**: Added Pax8 stack callout for LaunchDarkly
- **facets/data-persistence/best-practices.md**: Added SQL Coding Standards (uppercase keywords, snake_case names, 4-space indent, left-aligned root keywords), Prefer CTEs Over Subqueries, Pax8 stack callout for PostgreSQL and Spring Data
- **facets/data-persistence/gotchas.md**: Added Nested Subqueries Instead of CTEs gotcha
- **facets/repository-governance/best-practices.md**: Added Design Process (Event Storming, Event Modeling, ADRs), Development Practices (TDD, pair/mob programming, trunk-based development), Code Review (mandatory PRs, structured approval), Security in Design (risk assessment, threat modeling), Pax8 stack callout for RFC-0058, Architecture Forum, ADR location
- **pax8-context/standards-map.md**: Added RFC-0003 (Kafka Standards), RFC-0014 (Service Documentation), RFC-0022/0023 (REST API Guidelines), RFC-0029 (Logging), RFC-0058 (Architecture and Design Process)

---

## [2026-02-13] - API Standards Alignment

### Changed

- **facets/api-design/best-practices.md**: Added Response Object Depth (nested objects vs bare IDs), Audit Action Fields (structured action-based format with actor types), expanded Idempotency section (retry semantics, conflict handling, key expiry), added Pax8 stack callouts for TypeSpec-first (ADR-0057) and idempotency-key requirements (ADR-0080)
- **facets/api-design/architecture.md**: Added Distributed Tracing Headers section (W3C Trace Context, traceparent/tracestate, comparison with idempotency keys), added Pax8 stack callout for REST Query API library (RFC-0039)
- **facets/api-design/options.md**: Added Pax8 stack callout on cursor-based pagination as required standard (ADR-0074)
- **facets/api-design/gotchas.md**: Added 3 new pitfalls: Returning Only IDs When Nested Objects Are Needed, Forgetting Idempotency Keys on Mutations, Using Flat Audit Fields When Richer Context Is Available
- **checklists/api-design-review.md**: Added Idempotency & Reliability section (3 checks), Audit & Tracing section (3 checks), API-first and object depth checks, clarified error format reference to support both RFC 9457 and organisational standards
- **facets/error-handling/best-practices.md**: Added Pax8 stack callout for ADR-0082 custom error format (ErrorType/ErrorCode enums, details array)
- **facets/event-driven-architecture/best-practices.md**: Added Include Required Event Metadata section (id, messageId, updatedTime, events as upserts, audit fields in events), Pax8 stack callout for RFC-0026 event standards, topic naming, and schema registry
- **facets/authentication/best-practices.md**: Added Fine-Grained Authorization (FGA) guidance with RBAC comparison and when-to-use criteria, Pax8 stack callout for mandatory FGA on new APIs
- **pax8-context/standards-map.md**: Added ADR-0057 (API First Development), ADR-0059 (Public API Process), ADR-0082 (API Error Response Format) to complete table and facet summary

---

## [2026-02-10] - Options TOC Enhancement

### Changed

- **38 options.md files** (21 facets + 17 experiences): Expanded `## Contents` table of contents to include nested entries for each individual option, making available choices scannable at a glance without reading the full document
- **create-facet skill**: Updated `options.md` template to include nested TOC pattern and guidance note
- **content-freshness-audit skill**: Added new Phase 3 (TOC Drift Check) that detects when headings and Contents sections are out of sync, renumbered subsequent phases

---

## [2026-02-09] - Tech Radar and Maintenance Skills

### Added

- **Tech Radar**: `tech-radar.md` with 129 classified technologies across 4 quadrants (Techniques, Platforms, Tools, Languages & Frameworks) and 4 rings (Adopt, Trial, Assess, Hold), each with Mermaid quadrant charts and rationale tables
- **Pax8 Tech Radar Overlay**: `tech-radar-pax8.md` showing ring adjustments for Pax8 projects (13 promotions, 6 demotions, 10 Pax8-specific additions)
- **Zalando JSON Export**: `tech-radar.json` for generating an interactive radar via Zalando's open-source tech radar tool
- **3 maintenance skills**: `sync-pax8-adrs` (diffs ADR repo against standards map), `content-freshness-audit` (flags stale content with category-aware thresholds), `refresh-tech-radar` (regenerates radar from codex content)
- **1 maintenance command**: `validate-links` with supporting Python script (`scripts/validate-links.py`) checking all internal markdown links and anchors

### Fixed

- 105 broken links across 30+ files: corrected path depths for experience-to-facet cross-references, fixed anchor slugs with special characters, removed references to nonexistent experiences, corrected relative paths

---

## [2026-02-09] - Move Workflow Skills to Workspace Standards

### Moved

- **generate-opportunity-brief** and **generate-prd** skills moved to `workspace-standards` repository — they are workflow tools that read from the codex, not knowledge content that belongs in it
- These skills now live alongside refine-ticket, spike, and implement-ticket where they can be chained in the full idea-to-implementation pipeline

---

## [2026-02-09] - Pax8 Context Overlay, New Facets, and Product Skills

### Added

- **2 new facets**: Dependency Management (evaluation, versioning, upgrades, license compliance, security scanning) and Repository & Code Governance (branch strategies, CODEOWNERS, PR policies, repo lifecycle) — full 7-file structure with diagrams, code examples, and cross-references
- **Pax8 Standards Overlay** (`pax8-context/`): standards-map.md mapping 40+ active Pax8 ADRs to codex facets with type classification (Standard/Guidance), deprecated.md tracking technologies being phased out (NewRelic, Moment.js, Axon Server, legacy branch protection, etc.)
- **2 new skills**: generate-opportunity-brief (draft Pax8 Opportunity Briefs informed by codex content) and generate-prd (expand approved briefs into full PRDs using codex + Pax8 standards)
- **1 new command**: pax8-standard (surface Pax8-specific standards and deprecated technologies for any facet)

### Changed

- **evaluate-options skill**: Added optional Phase 3b (Pax8 Standards Check) that checks organisational standards before scoring — skipped for non-Pax8 projects
- **Facet index**: Updated to 21 facets (was 19)
- **Root README**: Updated structure, facet table, skills, and commands sections

---

## [2026-02-09] - V1 Improvements: Diagrams, Code, Quality, Tagging

### Added

- **Mermaid diagrams** in all 36 architecture.md files (19 facets + 17 experiences) — sequence diagrams, flowcharts, state diagrams, and component diagrams
- **Code examples** (Vue 3, React, Kotlin, Java) in 12 facet best-practices.md files — auth guards, stores, repositories, migrations, event handlers, logging, validation, accessibility, i18n, CI/CD, and more
- **3 new decision criteria**: security, accessibility, team-familiarity
- **Tagging system**: frontmatter tags on all 36 facet/experience READMEs, auto-generated tag-index.md with 271 cross-referenced tags, generation script
- **Filled-in examples**: 2 complete ADRs (JWT auth, Kafka event bus) and 1 decision log with 7 entries
- **Reading paths** for 6 personas (new developer, QA, architect, PM, DevOps, tech lead)

### Changed

- **Content quality pass** on 8 entries: deepened refactoring-and-extraction, observability, accessibility, internationalization, ci-cd (facets) and onboarding, design-consistency, search-and-discovery (experiences) with nuanced trade-offs, real-world scenarios, and practical guidance

### Fixed

- 6 broken links across 4 files (stale refactoring/ and developer-experience/ paths)
- CONTRIBUTING.md updated with tagging conventions

---

## [2026-02-09] - New Skills and Commands

### Added

- **Skill: Checklist Runner** — interactive audit of any codex checklist against a project, with pass/fail/partial per item and gap reports
- **Skill: Experience Audit** — review frontend code against an experience's UX guidelines, covering product alignment, architecture patterns, best practices, and gotchas
- **Skill: Onboarding Guide** — scan a project's tech stack and generate a personalised reading path through the codex, role-aware
- **Command: Gotcha Check** — instantly surface the gotchas for any facet or experience
- **Command: Generate Checklist** — create a project-specific checklist tailored to the project's stack and type
- **Command: What Should I Read?** — describe a task and get a prioritised reading list of relevant codex content

---

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
