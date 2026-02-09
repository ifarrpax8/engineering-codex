---
title: Data Visualization
type: experience
last_updated: 2026-02-09
tags: [chart-js, echarts, d3, recharts, dashboard, aggregation, export, responsive-charts]
---

# Data Visualization

Charts, dashboards, data exports, and reporting UX patterns for presenting complex data clearly.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Start with a charting library, not custom SVG** — Chart.js, Recharts, or ECharts provide battle-tested solutions for common chart types
- **Choose the right chart type for the data** — Bar charts for comparisons, line charts for trends, pie charts only for parts-of-whole with few categories
- **Server-side aggregation for large datasets** — Don't send 100K rows to the client; aggregate in SQL/Spring Boot before rendering
- **Start with best-practices.md** — Follow established patterns for accessibility, color palettes, and responsive design
- **Provide data table alternatives** — Every chart needs a table fallback for accessibility and data export

## Perspectives

- [Product Perspective](product.md) — Business value, user flows, personas, success metrics
- [Architecture](architecture.md) — Charting library integration, data aggregation patterns, dashboard architecture, export systems
- [Testing](testing.md) — Chart rendering tests, dashboard layout tests, export validation, accessibility testing
- [Best Practices](best-practices.md) — Chart type selection, accessibility, color palettes, loading states, stack-specific guidance
- [Gotchas](gotchas.md) — Common pitfalls: pie chart overload, Y-axis truncation, memory leaks, timezone issues
- [Options](options.md) — Decision matrix: Chart.js vs Recharts vs ECharts, client-side vs server-side export, layout libraries

## Related Facets

- [API Design](../../facets/api-design/) — Chart data endpoints, aggregation API patterns, pagination for large datasets
- [Performance](../../facets/performance/) — Chart rendering optimization, lazy loading, data sampling strategies
- [Data Persistence](../../facets/data-persistence/) — Time-series data storage, aggregation query optimization, caching strategies
- [Observability](../../facets/observability/) — Dashboard load time monitoring, export job tracking, chart render performance

## Related Experiences

- [Tables and Data Grids](../tables-and-data-grids/) — Complementary data presentation patterns, when to use tables vs charts
- [Loading and Perceived Performance](../loading-and-perceived-performance/) — Skeleton states for charts, progressive data loading
- [Responsive Design](../responsive-design/) — Mobile chart simplification, touch interactions, responsive dashboard layouts
- [Search and Discovery](../search-and-discovery/) — Filtering dashboards, date range selection, drill-down navigation patterns
