# Security

Evaluation criterion for decision matrices across the Engineering Codex.

## Definition

The degree to which the chosen approach minimises attack surface, protects sensitive data, and supports compliance requirements without introducing unnecessary risk.

## What to Evaluate

- **Attack surface** -- Does the approach increase or decrease exposure to potential threats (open ports, public endpoints, third-party dependencies)?
- **Data protection** -- How well does it handle sensitive data at rest and in transit (encryption, masking, access controls)?
- **Authentication and authorization** -- Does it integrate cleanly with identity providers and permission models?
- **Dependency risk** -- Does it introduce third-party dependencies with known vulnerabilities or poor maintenance track records?
- **Compliance alignment** -- Does it support regulatory requirements relevant to your domain (GDPR, SOC 2, PCI-DSS)?
- **Auditability** -- Can actions be traced and logged for forensic analysis?

## Scoring Guide

- **High** -- Minimal attack surface by design. Built-in encryption, auth integration, and audit logging. Active security community and regular CVE patching.
- **Medium** -- Reasonable security posture with some configuration required. Dependencies are well-maintained but may need manual review. Compliance achievable with effort.
- **Low** -- Large attack surface or immature security model. Requires significant custom hardening. Dependencies have known unpatched vulnerabilities or sparse maintenance.

## Related Resources

- [Security Facet](../../facets/security/) -- Deep dive into security best practices
- [Security Review Checklist](../../checklists/security-review.md) -- Pre-deployment security audit
- [Authentication Facet](../../facets/authentication/) -- Auth-specific security concerns
