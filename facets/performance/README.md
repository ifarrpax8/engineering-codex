---
title: Performance
type: facet
last_updated: 2026-02-09
---

# Performance

Frontend loading, backend throughput, database optimization, caching, profiling, budgets.

## TL;DR

- **Default choice**: k6 for load testing (JavaScript-based, CI-friendly); Lighthouse CI for frontend performance monitoring (automated audits in CI); Redis cache-aside pattern for distributed applications
- **Key principle**: Measure before optimizing—establish performance baselines with automated monitoring, then optimize based on real data
- **Watch out for**: Spring Cache provides per-instance caching that doesn't scale across multiple instances—use Redis for distributed applications requiring shared cache
- **Start here**: [Options](options.md) for load testing tools, frontend monitoring solutions, and backend caching strategies

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Frontend Architecture](../frontend-architecture/) -- Code splitting, lazy loading, bundle size
- [Backend Architecture](../backend-architecture/) -- Service architecture impact on latency
- [Data Persistence](../data-persistence/) -- Query optimization, indexing, caching
- [API Design](../api-design/) -- Pagination, payload optimization, compression
- [State Management](../state-management/) -- Re-render optimization, memoization
- [Observability](../observability/) -- Performance metrics, profiling, alerting

## Related Experiences

- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- User perception of speed
- [Tables & Data Grids](../../experiences/tables-and-data-grids/) -- Large dataset rendering
- [Search & Discovery](../../experiences/search-and-discovery/) -- Search response time
