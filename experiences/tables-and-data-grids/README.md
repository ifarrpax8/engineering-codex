---
title: Tables & Data Grids
type: experience
last_updated: 2026-02-09
---

# Tables & Data Grids

Enterprise table patterns, sorting, filtering, pagination, column management, and data grid implementations for B2B SaaS applications.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- Start with simple HTML tables for basic data display; graduate to TanStack Table or Propulsion DataTable when you need sorting, filtering, or complex interactions
- Implement server-side pagination for datasets larger than 100 rows; never load unbounded data client-side
- Encode table state (page, sort, filters) in URL parameters for shareable, bookmarkable table views
- Begin with [best-practices.md](best-practices.md) for foundational guidance, then reference architecture.md for implementation patterns

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Rendering patterns, data fetching, sorting/filtering architecture, column management, inline editing, virtual scrolling
- [Testing](testing.md) -- Pagination, sorting, filtering, inline editing, bulk actions, accessibility, performance testing strategies
- [Best Practices](best-practices.md) -- Language-agnostic principles, progressive enhancement, accessibility guidelines
- [Options](options.md) -- Decision matrix for table libraries, pagination strategies, filtering approaches, export methods
- [Gotchas](gotchas.md) -- Common pitfalls, performance issues, UX anti-patterns
- [Testing](testing.md) -- Comprehensive testing strategies for tables and data grids

## Related Facets

- [api-design](../facets/api-design.md) -- Pagination patterns, query parameter conventions, RESTful API design
- [data-persistence](../facets/data-persistence.md) -- Database query optimization, indexing strategies for sortable/filterable columns
- [performance](../facets/performance.md) -- Virtual scrolling, lazy loading, query optimization
- [accessibility](../facets/accessibility.md) -- Keyboard navigation, screen reader support, ARIA attributes for tables

## Related Experiences

- [search-and-discovery](../search-and-discovery/) -- Filtering and search integration with tables
- [responsive-design](../responsive-design/) -- Mobile table patterns, stacked layouts, touch interactions
- [loading-and-perceived-performance](../loading-and-perceived-performance/) -- Skeleton loaders, progressive rendering, optimistic updates
- [forms-and-data-entry](../forms-and-data-entry/) -- Inline editing patterns, cell-level validation, bulk form operations
