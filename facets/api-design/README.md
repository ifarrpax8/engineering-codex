---
title: API Design
type: facet
last_updated: 2026-02-09
tags: [rest, graphql, grpc, openapi, typespec, pagination, hateoas, http, versioning]
---

# API Design

REST, GraphQL, gRPC, API versioning, contracts, documentation

## TL;DR

- **Default choice**: REST for most web APIs—widely understood, excellent tooling, browser-friendly, natural HTTP caching
- **Key principle**: Choose API style based on consumer needs—REST for simple CRUD, GraphQL for complex queries with multiple consumers, gRPC for high-performance internal services
- **Watch out for**: Over-fetching and N+1 problems in REST (GraphQL helps), query complexity attacks in GraphQL (set complexity limits), browser limitations with gRPC (requires proxy)
- **Start here**: [Options](options.md) — Decision matrix covers REST, GraphQL, and gRPC with pagination strategies (offset vs cursor-based)

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Authentication](../authentication/) -- API authentication patterns, token management, OAuth flows
- [Backend Architecture](../backend-architecture/) -- Service boundaries, microservices communication patterns
- [Data Persistence](../data-persistence/) -- Query patterns, pagination strategies, data modeling for APIs
- [Event-Driven Architecture](../event-driven-architecture/) -- Event APIs, webhooks, async API patterns
- [Performance](../performance/) -- API response times, caching strategies, query optimization
- [Security](../security/) -- API security best practices, input validation, rate limiting

## Related Experiences

- [Tables and Data Grids](../../experiences/tables-and-data-grids/) -- API patterns for data grid pagination, filtering, sorting
- [Search and Discovery](../../experiences/search-and-discovery/) -- Search API design, query language patterns, faceted search
- [Loading and Perceived Performance](../../experiences/loading-and-perceived-performance/) -- API response optimization, progressive loading patterns
