---
title: Search & Discovery
type: experience
last_updated: 2026-02-09
---

# Search & Discovery

How users find content, products, and information within the application. Covers the spectrum from simple filtering to full-text search with relevance ranking.

## TL;DR

- **Default choice**: Start with Database Filtering for small datasets (<10K records), upgrade to PostgreSQL Full-Text Search for medium datasets (10K-1M records), move to dedicated search engine (OpenSearch or lightweight) for large datasets (>1M records) or advanced features
- **Key principle**: Search should be forgiving (handle typos), relevant (right results first), and helpful (autocomplete, zero-result guidance)
- **Watch out for**: Stale search indexes after data changes, autocomplete overwhelming APIs without debouncing, ignoring zero-result queries and search analytics
- **Start here**: [Options](options.md) for decision framework, [Architecture](architecture.md) for implementation patterns

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- UX principles and guidelines
- [Gotchas](gotchas.md) -- Common pitfalls, traps, and lessons learned
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [API Design](../../facets/api-design/) -- Search vs filtering architecture, pagination patterns
- [Performance](../../facets/performance/) -- Search performance optimization
- [Data Persistence](../../facets/data-persistence/) -- Database full-text search capabilities

## Related Experiences

- [Tables & Data Grids](../tables-and-data-grids/) -- Search results displayed in tables
- [Loading & Perceived Performance](../loading-and-perceived-performance/) -- Search result loading patterns
- [Navigation](../navigation/) -- Search as a navigation mechanism
