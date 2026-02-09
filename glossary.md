# Glossary

Shared terminology used throughout the Engineering Codex. Terms are listed alphabetically.

## A

- **ABAC** -- Attribute-Based Access Control. Authorization based on attributes of the user, resource, and environment.
- **ADR** -- Architecture Decision Record. A document capturing a significant architectural decision, its context, and consequences.
- **API Contract** -- A formal specification of an API's interface, including endpoints, request/response schemas, and behavior guarantees.
- **Activation Funnel** -- The sequence of steps a new user takes from signup to first meaningful action (the "aha moment").

## B

- **Best Practice (mode)** -- An `options.md` recommendation type where there is a clear industry consensus. Alternatives are listed as escape hatches.
- **Bounded Context** -- A DDD concept defining a boundary within which a particular domain model applies.
- **BroadcastChannel** -- A browser API that allows communication between tabs, windows, and iframes of the same origin.

## C

- **Circuit Breaker** -- A resilience pattern that prevents cascading failures by temporarily stopping requests to a failing downstream service.
- **Container Query** -- A CSS feature that allows styling based on the size of a parent container rather than the viewport.
- **CRDT** -- Conflict-free Replicated Data Type. A data structure that can be replicated across multiple nodes and merged without conflicts.
- **CQRS** -- Command Query Responsibility Segregation. Separating read and write models for a system.
- **Cross-Reference** -- A link from one facet or experience to another, indicating a relationship between concerns.
- **Cursor-Based Pagination** -- Pagination using an opaque cursor (typically an encoded ID or timestamp) rather than page numbers, providing stable results during concurrent writes.

## D

- **Dead Letter Queue (DLQ)** -- A message queue that stores messages that could not be processed successfully after a configured number of retries.
- **Decision Matrix (mode)** -- An `options.md` recommendation type where multiple approaches are genuinely viable and context determines the best choice.
- **DDD** -- Domain-Driven Design. An approach to software design that centers on the core domain and domain logic.
- **Design Token** -- A named value representing a design decision (color, spacing, typography) that can be shared across platforms and tools.
- **DORA Metrics** -- DevOps Research and Assessment metrics: deployment frequency, lead time, change failure rate, and time to restore service.

## E

- **Empty State** -- The UI displayed when a list, table, or dashboard has no data. A well-designed empty state guides the user to take action.
- **Evolution Trigger** -- A specific condition (team size, traffic scale, complexity) that signals a decision should be reconsidered.
- **Experience** -- A user-centric perspective in the codex (e.g., onboarding, navigation). Focuses on what the user sees and feels.

## F

- **Facet** -- An engineering-focused perspective in the codex (e.g., authentication, testing). Focuses on how things are built.
- **Feature Toggle** -- A mechanism to enable or disable features at runtime without deploying new code.
- **FGA** -- Fine-Grained Authorization. Authorization that evaluates access at the individual resource level based on relationships.

## H

- **HATEOAS** -- Hypermedia as the Engine of Application State. A REST constraint where responses include links to related resources and available actions.
- **Hexagonal Architecture** -- Also called Ports and Adapters. An architecture where the domain core is isolated from external concerns via defined interfaces.

## I

- **Idempotent Consumer** -- A message consumer that produces the same result regardless of how many times it processes the same message.
- **Inflection Point** -- A threshold in application growth where the current architecture becomes a bottleneck and evolution is warranted.

## M

- **Microcopy** -- The small pieces of text in a UI: button labels, tooltips, validation messages, empty states. Often the difference between a confusing and a delightful experience.
- **MFE** -- Micro-Frontend. An architectural pattern where a frontend application is decomposed into smaller, independently deployable units.
- **Modulith** -- A modular monolith. A single deployment unit with well-defined internal module boundaries.
- **Multi-Tenancy** -- An architecture where a single application instance serves multiple tenants (organizations/customers), with data isolation between them.

## O

- **Offset-Based Pagination** -- Pagination using page number and page size parameters. Simple but can produce inconsistent results during concurrent writes.
- **OpenFeature** -- A vendor-neutral, open standard for feature flag management, providing a unified API across different feature flag providers.
- **Operational Transform (OT)** -- An algorithm for resolving conflicts in real-time collaborative editing by transforming operations based on concurrent changes.
- **Optimistic UI** -- A UX pattern where the interface assumes an action will succeed and updates immediately, reverting only on failure.

## P

- **Perspective** -- One of the seven files within a facet or experience: product, architecture, testing, best-practices, gotchas, options, and optionally operations.
- **Presence** -- A real-time indication of which users are currently active or viewing a particular resource.
- **Problem Details (RFC 7807)** -- A standard format for machine-readable error responses in HTTP APIs, including type, title, status, detail, and instance fields.
- **Progressive Disclosure** -- A UX pattern that reveals complexity gradually, showing only what the user needs at each stage.

## R

- **RBAC** -- Role-Based Access Control. Authorization based on roles assigned to users.

## S

- **Skeleton Screen** -- A loading placeholder that mimics the shape of content that is being loaded, reducing perceived load time compared to spinners.
- **SLO** -- Service Level Objective. A target value for a service reliability metric.
- **Strangler Fig** -- A migration pattern where a new system is built alongside the old one, gradually replacing functionality until the old system can be removed.
- **Synergy** -- A relationship between decisions in different facets where one choice makes another more or less favorable.

## T

- **Tenant** -- An organization or customer in a multi-tenant system. Each tenant's data is logically (or physically) isolated from others.
- **Three Amigos** -- A collaborative refinement practice involving developer, tester, and product perspectives.

## V

- **Virtual Scrolling** -- A rendering technique that only renders visible rows/items in a list or table, improving performance for large datasets.

## W

- **White-Labeling** -- Customizing a product's branding (logo, colors, domain) for a specific tenant or partner so it appears as their own product.

---

*To add a term, follow alphabetical order and use the format: `- **TERM** -- Definition.`*
