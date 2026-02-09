---
title: Loading and Perceived Performance
type: experience
last_updated: 2026-02-09
tags: [skeleton, spinner, optimistic-ui, suspense, prefetch, lazy-loading, core-web-vitals, progressive]
---

# Loading and Perceived Performance

Skeleton screens, optimistic UI, progressive loading, stale-while-revalidate

## TL;DR

- **Perceived performance matters more than actual performance** — users judge experience by how fast it *feels*, not milliseconds
- **Never show a blank page** — skeleton screens, spinners, or progress indicators provide essential visual feedback
- **Optimistic updates create instant feel** — update UI immediately, reconcile with server response, rollback on failure
- **Progressive loading prioritizes above-the-fold** — load critical content first, lazy-load below-the-fold
- **Stale-while-revalidate balances freshness and speed** — show cached data immediately, update in background

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and anti-patterns
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Performance](../facets/performance.md) -- Core performance optimization techniques
- [Frontend Architecture](../facets/frontend-architecture.md) -- Component patterns and structure
- [State Management](../facets/state-management.md) -- Data fetching and caching strategies
- [Observability](../facets/observability.md) -- Monitoring and measuring performance

## Related Experiences

- [Search & Discovery](../search-and-discovery/README.md) -- Search results loading and progressive disclosure
- [Tables & Data Grids](../tables-and-data-grids/README.md) -- Large dataset loading and pagination
- [Navigation](../navigation/README.md) -- Route transitions and page loading
- [Design Consistency & Visual Identity](../design-consistency-and-visual-identity/README.md) -- Loading state design patterns
