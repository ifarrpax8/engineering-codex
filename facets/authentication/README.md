---
title: Authentication & Authorization
type: facet
last_updated: 2026-02-09
---

# Authentication & Authorization

AuthN/AuthZ, identity, sessions, tokens, OAuth, RBAC, ABAC

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Security](../security/) -- Authentication is a foundational security concern. Security practices around encryption, secrets management, and vulnerability scanning directly impact auth implementation choices.
- [Event-Driven Architecture](../event-driven-architecture/) -- Authentication events (login, logout, permission changes) can be published to event streams for audit and downstream processing.
- [Feature Toggles](../feature-toggles/) -- Feature flags can gate authentication features like MFA enrollment, SSO availability, or new auth providers.
- [API Design](../api-design/) -- API authentication patterns (bearer tokens, API keys, OAuth client credentials) are core to API design decisions.

## Related Experiences

- [Onboarding](../experiences/onboarding/) -- First-time user authentication flows, account creation, and initial credential setup are critical onboarding touchpoints.
- [Permissions UX](../experiences/permissions-ux/) -- Authorization decisions manifest in the user interface through permission checks, role-based UI rendering, and access denied experiences.
- [Multi-Tenancy UX](../experiences/multi-tenancy-ux/) -- Multi-tenant applications require tenant-scoped authentication and authorization, where user identity includes tenant context.
- [Settings and Preferences](../experiences/settings-and-preferences/) -- User account settings include password management, MFA configuration, connected accounts, and session management preferences.
