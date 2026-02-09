---
title: CI/CD
type: facet
last_updated: 2026-02-09
---

# CI/CD

Pipelines, build automation, deployment strategies, quality gates, artifact management.

## TL;DR

- **Default choice**: Canary deployments for production (data-driven rollouts with automatic rollback); trunk-based development for high-velocity teams; GitHub Actions for GitHub-hosted repositories
- **Key principle**: Frequent small deployments reduce risk and enable rapid iteration—canary deployments validate changes with real traffic before full rollout
- **Watch out for**: Trunk-based development requires feature flag infrastructure to hide incomplete work—without it, you can't merge frequently without impacting users
- **Start here**: [Options](options.md) for deployment strategies, branching approaches, and CI platform selection

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Testing](../testing/) -- Test pyramid integration with CI stages
- [Security](../security/) -- SAST/DAST, dependency scanning, secret scanning in pipelines
- [Observability](../observability/) -- Deployment markers, canary monitoring
- [Performance](../performance/) -- Performance budgets enforced in CI
- [Configuration Management](../configuration-management/) -- Environment-specific configuration
- [Feature Toggles](../feature-toggles/) -- Feature flags enabling trunk-based development

## Related Experiences

- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Bundle size checks in CI
