---
title: Configuration Management
type: facet
last_updated: 2026-02-09
---

# Configuration Management

Environment configuration, secrets, feature flags, profiles, externalized config.

## TL;DR

- **Default choice**: Spring Boot profiles with `@ConfigurationProperties` for backend, Vite `.env` files for frontend, cloud provider secrets managers (AWS Secrets Manager/Azure Key Vault/GCP Secret Manager) for secrets
- **Key principle**: Never commit secrets to code or config files; use dedicated secrets management services with proper encryption and rotation
- **Watch out for**: Configuration drift between environments, secrets in version control, missing validation leading to runtime failures
- **Start here**: [Options](options.md) — contains the recommended configuration stack and decision matrix for secrets management and runtime configuration approaches

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [CI/CD](../ci-cd/) -- Pipeline configuration, environment promotion
- [Security](../security/) -- Secrets management, credential rotation
- [Feature Toggles](../feature-toggles/) -- Runtime configuration for feature flags
- [Backend Architecture](../backend-architecture/) -- Service configuration patterns
- [Observability](../observability/) -- Configuration change tracking

## Related Experiences

- [Multi-Tenancy](../../experiences/multi-tenancy/) -- Tenant-specific configuration
