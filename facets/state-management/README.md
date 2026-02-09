---
title: State Management
type: facet
last_updated: 2026-02-09
tags: [pinia, zustand, tanstack-query, vuex, redux, composables, hooks, reactive, store]
---

# State Management

Client state, server state, global vs local, reactive patterns.

## TL;DR

- **Default choice**: Local component state + TanStack Query/VueQuery (server state) + Pinia/Zustand (shared client state)—covers 95% of applications with minimal boilerplate
- **Key principle**: Separate concerns—local state for component-specific data, server state libraries for API data with caching, lightweight stores for shared UI state
- **Watch out for**: Prop drilling beyond 2-3 levels (lift to store), cache invalidation bugs with server state (map mutations to affected queries), over-using global state (most state should be local)
- **Start here**: [Options](options.md) — Decision matrix covers client state (Local, Pinia/Zustand, Redux) and server state (Manual, TanStack Query/VueQuery, GraphQL clients)

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Frontend Architecture](../frontend-architecture/) -- How architecture choices affect state patterns
- [API Design](../api-design/) -- Server state fetching and caching
- [Performance](../performance/) -- Re-render optimization, memoization
- [Authentication](../authentication/) -- Auth state management patterns
- [Error Handling](../error-handling/) -- Error state patterns in UI

## Related Experiences

- [Forms & Validation](../../experiences/forms-and-validation/) -- Form state management
- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Loading states
- [Navigation](../../experiences/navigation/) -- Route-based state
- [Real-Time & Collaboration](../../experiences/real-time-and-collaboration/) -- Real-time state synchronization
