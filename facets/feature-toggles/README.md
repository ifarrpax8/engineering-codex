---
title: Feature Toggles
type: facet
last_updated: 2026-02-09
---

# Feature Toggles

Feature toggles, also known as feature flags, are a powerful technique that allows teams to modify system behavior without changing code. They enable decoupling deployment from release, reducing risk, enabling progressive rollouts, and supporting experimentation. This facet covers the complete lifecycle of feature toggles from creation through removal, including release toggles, experiment toggles, ops toggles, and permission toggles.

## Core Concepts

**Release Toggles**: Hide incomplete features behind flags, allowing code to be merged and deployed to production before the feature is ready for users. These are short-lived, typically removed within days or weeks after the feature is fully released.

**Experiment Toggles**: Enable A/B testing and experimentation by showing different experiences to different user segments. These support data-driven decision making and are evaluated consistently per user session.

**Ops Toggles**: Provide operational control over system behavior, allowing teams to disable expensive features during high load, implement kill switches, or expose circuit breakers as toggles. These are long-lived and critical for system reliability.

**Permission Toggles**: Control feature access based on user roles, plans, tenants, or other business rules. These enable product differentiation, early access programs, and tiered feature availability.

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Implementation patterns, diagrams, trade-offs, database-backed vs commercial solutions
- [Testing](testing.md) -- Test strategies, combinatorial testing, toggle state management in tests
- [Best Practices](best-practices.md) -- Language-agnostic principles, naming conventions, removal discipline
- [Gotchas](gotchas.md) -- Common pitfalls, toggle debt, inconsistent evaluation, testing failures
- [Options](options.md) -- Decision matrix comparing implementation approaches, evaluation criteria, recommendations

## Related Facets

- [CI/CD](../ci-cd/) -- Trunk-based development, deployment vs release decoupling, canary deployments
- [Configuration Management](../configuration-management/) -- Toggle storage and runtime configuration, environment-specific settings
- [Frontend Architecture](../frontend-architecture/) -- Conditional rendering, code splitting by feature, toggle-aware components
- [Backend Architecture](../backend-architecture/) -- Service-level toggle evaluation, microservice patterns
- [Testing](../testing/) -- Testing toggled features, combinatorial testing, toggle state management
- [Authentication](../authentication/) -- Permission-based toggles, user targeting, role-based access control

## Related Experiences

- [Onboarding & Activation](../../experiences/onboarding-and-activation/) -- Progressive feature rollout, gradual user introduction to capabilities
- [Multi-Tenancy](../../experiences/multi-tenancy/) -- Tenant-specific feature availability, per-customer feature control

## Quick Start

For teams new to feature toggles, start with configuration-file toggles for simple use cases. As needs grow, evolve to a database-backed service or commercial platform. The [Options](options.md) guide provides detailed decision criteria.

Key principles to remember:
1. Toggles are temporary—plan for removal from day one
2. Test both toggle states—the off path is production code
3. Keep toggle checks at boundaries—controllers, route guards, top-level components
4. Document every toggle—name, purpose, owner, expected lifespan
5. Default to safe states—release toggles default off, ops toggles default on
