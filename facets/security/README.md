---
title: Security
type: facet
last_updated: 2026-02-09
tags: [csp, cors, xss, csrf, tls, encryption, secrets, vault, dependency-scanning, owasp]
---

# Security

Input validation, secrets management, dependency scanning, encryption, CORS, CSP, OWASP.

## TL;DR

- **Default choice**: Cloud provider secrets managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) for single-cloud deployments; Dependabot/Renovate for automated dependency updates; SAST (Static Application Security Testing) first, then add DAST for critical applications
- **Key principle**: Start with managed services for simplicity, upgrade to advanced solutions (HashiCorp Vault, comprehensive SCA tools) as requirements grow
- **Watch out for**: Kubernetes Secrets are base64-encoded by default—not encrypted. Enable encryption providers for production use
- **Start here**: [Options](options.md) for decision matrices on secrets management, dependency scanning, and application security testing

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Authentication](../authentication/) -- Auth protocols, session management, authorization models
- [API Design](../api-design/) -- API security, rate limiting, input validation
- [Data Persistence](../data-persistence/) -- Data encryption, access controls, data masking
- [Observability](../observability/) -- Audit logging, security monitoring, anomaly detection
- [CI/CD](../ci-cd/) -- Supply chain security, dependency scanning, SAST/DAST
- [Configuration Management](../configuration-management/) -- Secrets management, environment configuration

## Related Experiences

- [Forms & Validation](../../experiences/forms-and-data-entry/) -- Client-side input validation
