---
title: Repository & Code Governance
type: facet
last_updated: 2026-02-09
tags: [github, git, codeowners, branch-protection, pr-review, monorepo, repository, rulesets, naming-conventions]
---

# Repository & Code Governance

Branch strategies, protection rules, CODEOWNERS, PR review policies, repository templates, naming conventions, and repository lifecycle management.

## TL;DR

- **Default choice**: Trunk-based development with branch protection, CODEOWNERS for critical paths, squash merge for linear history, and repository templates for consistency
- **Key principle**: Governance should enable speed and quality, not create bottlenecks. Clear conventions reduce friction and accelerate onboarding
- **Watch out for**: Over-governance slowing delivery, CODEOWNERS bottlenecks, branch protection bypasses, repository sprawl without cleanup policies
- **Start here**: [Options](options.md) — contains decision matrix comparing branch strategies, merge approaches, and governance complexity

- [Product Perspective](product.md) -- Business value, developer experience, repository lifecycle
- [Architecture](architecture.md) -- Branch strategies, protection rules, CODEOWNERS patterns, diagrams
- [Testing](testing.md) -- Branch protection validation, PR gates, compliance checking
- [Best Practices](best-practices.md) -- Repository standards, PR practices, naming conventions
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix and recommended practices

## Related Facets

- [CI/CD](../ci-cd/) -- Branch protection integrates with CI status checks, deployment gates
- [Work Management](../work-management/) -- Branch naming tied to tickets, PR review workflows
- [Testing](../testing/) -- PR validation gates, test coverage requirements
- [Security](../security/) -- CODEOWNERS for security-sensitive paths, branch protection prevents force push

## Related Experiences
