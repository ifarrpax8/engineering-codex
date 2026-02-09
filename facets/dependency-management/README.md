---
title: Dependency Management
type: facet
last_updated: 2026-02-09
tags: [dependencies, npm, gradle, renovate, dependabot, semver, license, vulnerability, transitive, lock-file]
---

# Dependency Management

Evaluating, selecting, versioning, and maintaining third-party dependencies. Covers dependency evaluation criteria, version strategies (pinned vs ranges), upgrade policies, transitive dependency management, license compliance, and security scanning.

## TL;DR

- **Default choice**: Pin production dependencies with lock files (package-lock.json, gradle.lockfile), use automated upgrade tools (Renovate > Dependabot for configurability), and scan for vulnerabilities in CI/CD
- **Key principle**: Evaluate dependencies before adding them—check maintenance status, security posture, bundle size, and alternatives. Prefer widely-adopted libraries over niche solutions
- **Watch out for**: Phantom dependencies (using transitive deps directly), lock file merge conflicts, and major version bumps that break silently (type changes, removed APIs)
- **Start here**: [Options](options.md) for decision matrices on automated upgrade tools and version strategies

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## Perspectives

- [Product Perspective](product.md) -- Business value, security impact, compliance requirements, stakeholder concerns
- [Architecture](architecture.md) -- Dependency resolution, lock files, version strategies, monorepo patterns
- [Testing](testing.md) -- Testing upgrades, automated upgrade testing, breaking change detection
- [Best Practices](best-practices.md) -- Evaluation criteria, version strategies, automation patterns
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix for upgrade tools and version strategies

## Related Facets

- [Security](../security/) -- Dependency vulnerability scanning, supply chain security, CVE management
- [CI/CD](../ci-cd/) -- Automated dependency scanning, upgrade PR workflows, build reproducibility
- [Testing](../testing/) -- Testing dependency upgrades, snapshot testing for visual dependencies
- [Configuration Management](../configuration-management/) -- Dependency version management, environment-specific dependencies

## Related Experiences

- [Forms & Validation](../../experiences/forms-and-data-entry/) -- Form library dependencies, validation library choices
