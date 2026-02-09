---
title: Refactoring & Extraction
type: facet
last_updated: 2026-02-09
---

# Refactoring & Extraction

When to refactor, when to extract, code smells, technical debt management, safe refactoring techniques.

## TL;DR

- **Default choice**: Continuous small refactoring following the Boy Scout Rule (improve code as you touch it), dedicated refactoring PRs for larger work, Strangler Fig Pattern for architectural extractions
- **Key principle**: Refactor when code blocks current work or bugs are hard to fix; don't refactor stable, rarely-changed code without concrete benefit
- **Watch out for**: Refactoring without adequate test coverage, premature extraction before seeing a pattern 3+ times, scope creep in refactoring efforts
- **Start here**: [Options](options.md) — contains the recommended refactoring approach, trigger decision guide, and extraction readiness checklist

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Backend Architecture](../backend-architecture/) -- Monolith to microservices extraction
- [Frontend Architecture](../frontend-architecture/) -- SPA to MFE extraction
- [Testing](../testing/) -- Test coverage as a safety net for refactoring
- [CI/CD](../ci-cd/) -- Continuous integration enabling safe refactoring
- [Observability](../observability/) -- Monitoring during and after refactoring

## Related Experiences

- [Developer Experience](../../experiences/developer-experience/) -- Codebase health affects DX
