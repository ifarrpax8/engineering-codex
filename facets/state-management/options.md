---
recommendation_type: decision-matrix
---

# State Management -- Options

State management decisions depend on application complexity, team preferences, and specific requirements. This matrix helps evaluate options and make informed choices.

## Contents

- [Client State Management Options](#client-state-management-options)
- [Server State Management Options](#server-state-management-options)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Client State Management Options

### Local Component State Only

**Description**: Using only framework primitives (`useState` in React, `ref` in Vue) for all state. No external state management libraries. State lives in components and is passed via props when needed.

**Strengths**:
- Zero dependencies beyond the framework
- Simple mental model—state lives where it's used
- Easy to understand for developers new to the codebase
- No learning curve for framework-specific state libraries
- Minimal boilerplate for simple use cases

**Weaknesses**:
- Prop drilling becomes painful beyond 2-3 component levels
- No built-in persistence or cross-component sharing
- Difficult to debug state changes across many components
- No time-travel debugging or state inspection tools
- Manual state synchronization when multiple components need the same data

**Best For**:
- Small applications with simple state requirements
- Prototypes and proof-of-concept applications
- Applications where most state is truly local to components
- Teams prioritizing simplicity over advanced features

**Avoid When**:
- Multiple unrelated components need the same state
- State needs to persist across page refreshes
- Complex state transitions require debugging tools
- Application size is growing and prop drilling is becoming painful

### Lightweight Store (Pinia / Zustand)

**Description**: Feature-scoped reactive stores that provide shared state without the full structure of Flux. Pinia for Vue applications, Zustand for React applications. Stores contain state, computed properties (getters), and actions.

**Strengths**:
- Minimal boilerplate compared to full Flux architectures
- Natural integration with framework reactivity systems
- Good developer experience with TypeScript support
- Flexible—can be as simple or complex as needed
- Composable stores enable code reuse and modular design
- Built-in DevTools support for debugging

**Weaknesses**:
- Still requires manual cache management for server state
- No built-in request deduplication or background revalidation
- Can become disorganized without discipline (stores growing indefinitely)
- Less structure than Redux—requires team discipline to maintain organization
- Not ideal for complex state transitions requiring time-travel debugging

**Best For**:
- Applications with shared client state (user preferences, theme, UI state)
- Teams that want reactivity without Redux complexity
- Applications that separate server state management (using TanStack Query/VueQuery)
- Most applications—covers 95% of use cases with minimal overhead

**Avoid When**:
- All state is truly local (use local state instead)
- Need time-travel debugging for complex state transitions (consider Redux)
- Server state is the primary concern (use server state library instead)

### Full Flux Architecture (Redux / Vuex)

**Description**: Centralized state management with unidirectional data flow. Actions dispatch events, reducers process actions to produce new state, state updates trigger view re-renders. Redux for React, Vuex for Vue (though Vuex is being phased out in favor of Pinia).

**Strengths**:
- Predictable state updates through unidirectional flow
- Time-travel debugging with Redux DevTools
- Excellent debugging and inspection capabilities
- Enforces structure and discipline in state management
- Middleware ecosystem for cross-cutting concerns (logging, persistence, etc.)
- Well-documented patterns and best practices

**Weaknesses**:
- Significant boilerplate even with Redux Toolkit
- Steep learning curve for developers new to Flux patterns
- Can be overkill for simple applications
- Verbose for straightforward state updates
- Requires discipline to avoid anti-patterns (putting everything in global state)

**Best For**:
- Applications with complex state transitions requiring debugging
- Teams that need time-travel debugging capabilities
- Applications where state predictability is critical
- Large teams that benefit from enforced structure and patterns

**Avoid When**:
- Application state is simple and mostly local
- Team is small and values simplicity over structure
- Server state is the primary concern (use server state library instead)
- Most modern applications—lightweight stores are usually sufficient

## Server State Management Options

### Manual Fetching (fetch/axios + local state)

**Description**: Using `fetch` or `axios` directly with `useState`/`ref` to manage loading, error, and data states. Manual cache management, request deduplication, and revalidation logic.

**Strengths**:
- Full control over fetching logic
- No additional dependencies
- Can be customized for specific use cases
- Simple for one-off API calls

**Weaknesses**:
- Significant boilerplate for every API call (loading, error, data states)
- No automatic caching or request deduplication
- Manual cache invalidation is error-prone
- No background revalidation or stale-while-revalidate
- Difficult to coordinate multiple components fetching the same data
- Easy to introduce bugs (forgetting loading states, stale data, etc.)

**Best For**:
- Simple applications with very few API calls
- One-off API calls that don't need caching
- Applications where full control is required and boilerplate is acceptable

**Avoid When**:
- Multiple API calls throughout the application
- Need caching, revalidation, or request deduplication
- Multiple components need the same data
- Most applications—server state libraries eliminate most boilerplate

### Server State Library (TanStack Query / VueQuery)

**Description**: Automated server state management with built-in caching, background revalidation, request deduplication, and optimistic updates. TanStack Query for React, VueQuery (wrapper) for Vue.

**Strengths**:
- Eliminates boilerplate for loading/error/data states
- Automatic caching with configurable stale times
- Request deduplication prevents redundant API calls
- Background revalidation keeps data fresh
- Optimistic updates for instant UI feedback
- Excellent TypeScript support and developer experience
- Handles complex scenarios (pagination, infinite scrolling, mutations)

**Weaknesses**:
- Additional dependency to learn and maintain
- Requires understanding cache keys and invalidation strategies
- Can be overkill for applications with very few API calls
- Cache invalidation requires discipline to avoid stale data bugs

**Best For**:
- Applications with multiple API calls
- Need for caching and background revalidation
- Applications where data freshness and performance matter
- Most applications—recommended default for server state

**Avoid When**:
- Very few API calls that don't benefit from caching
- Using GraphQL with a client that handles caching (Apollo, urql)
- Applications where manual control is required for every aspect

### GraphQL Client (Apollo / urql)

**Description**: Schema-driven GraphQL clients with normalized caching, automatic cache updates, and optimistic updates. Apollo Client for React, Apollo with Vue Apollo for Vue, urql as a lighter alternative.

**Strengths**:
- Normalized caching based on GraphQL schema
- Automatic cache updates when mutations return data
- Excellent for GraphQL backends with schema awareness
- Handles complex GraphQL features (subscriptions, fragments, etc.)
- Built-in DevTools for cache inspection

**Weaknesses**:
- Only applicable when using GraphQL backends
- Heavier than REST-focused solutions
- Learning curve for GraphQL concepts and patterns
- Can be overkill for simple GraphQL APIs

**Best For**:
- Applications using GraphQL backends
- Need for normalized caching and automatic cache updates
- Complex data relationships that benefit from GraphQL

**Avoid When**:
- Using REST APIs (use TanStack Query/VueQuery instead)
- Simple GraphQL APIs that don't need advanced features
- Team unfamiliar with GraphQL concepts

## Evaluation Criteria

| Criteria | Weight | Local-Only | Store (Pinia/Zustand) | Full Flux (Redux/Vuex) |
|----------|--------|------------|----------------------|------------------------|
| **Simplicity** | High | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Performance** | High | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Developer Experience** | High | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Scalability** | Medium | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Debuggability** | Medium | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Simplicity**: How easy is it to understand and use? Local state is simplest, stores add moderate complexity, Flux adds significant structure.

**Performance**: How efficiently does it handle updates and re-renders? Stores with selectors perform well, Flux performs well with proper selectors, local state performs well but can cause prop drilling overhead.

**Developer Experience**: How pleasant is it to work with? Stores provide good DX with reactivity and TypeScript support, Flux provides good DX with DevTools but more boilerplate, local state is simple but can become painful.

**Scalability**: How well does it scale to large applications? Flux provides the most structure for large teams, stores scale well with discipline, local state becomes painful at scale.

**Debuggability**: How easy is it to debug state issues? Flux provides excellent debugging with time-travel, stores provide good debugging with DevTools, local state provides minimal debugging support.

## Recommendation Guidance

**Default Recommendation**: Local component state + server state library (TanStack Query/VueQuery) + lightweight store (Pinia/Zustand) for shared client state.

This combination covers 95% of applications with minimal boilerplate. Local state handles component-specific data, server state libraries handle API data with caching and revalidation, and lightweight stores handle shared client state like user preferences and UI state.

**When to Use Full Flux**: Only when complex state transitions require time-travel debugging, or when large teams benefit from enforced structure. Most applications don't need Redux/Vuex—lightweight stores are sufficient.

**When to Use GraphQL Client**: Only when using a GraphQL backend. For REST APIs, TanStack Query/VueQuery is the better choice.

**Evolution Path**: Start with local state. Add a lightweight store when you need shared state. Add a server state library when you have multiple API calls. Consider Flux only if you hit limitations with stores (rare).

## Synergies

**SPA Architecture**: Single-page applications can use a single store instance and straightforward state management. State flows naturally through the application without cross-boundary concerns.

**MFE Architecture**: Micro-frontends require per-MFE state isolation. Each MFE owns its state independently—no shared stores across MFEs. Cross-MFE communication uses events or URL parameters. This affects state management choices—each MFE needs its own store instances.

**REST APIs**: REST APIs work naturally with TanStack Query/VueQuery for server state management. Cache keys map cleanly to REST endpoints and parameters. Mutations map to POST/PUT/DELETE operations with cache invalidation.

**GraphQL APIs**: GraphQL APIs benefit from GraphQL clients (Apollo, urql) that provide normalized caching and automatic cache updates. However, TanStack Query can also work with GraphQL if you prefer its API.

**Real-Time Features**: WebSocket integration works with server state caches through optimistic updates and server push. Update cache optimistically on user action, then reconcile with server push. Server state libraries handle this pattern well.

**Offline-First Applications**: Applications that work offline require persistent stores and cache synchronization. Server state libraries can persist to IndexedDB, and stores can persist to localStorage. Sync logic reconciles local and remote state when connectivity returns.

## Evolution Triggers

**Manual Fetch Boilerplate Growing**: When you find yourself writing the same loading/error/data pattern repeatedly, adopt a server state library. The boilerplate reduction and improved user experience justify the dependency.

**Multiple Components Needing Same Data**: When multiple unrelated components need the same data, introduce a shared store or use a server state library with proper cache keys. Don't prop drill through many levels—lift state appropriately.

**Performance Issues from Re-renders**: When profiling reveals unnecessary re-renders, add selectors (Zustand) or computed properties (Pinia) to narrow subscriptions. Ensure components only re-render when their specific data changes.

**MFE Extraction**: When extracting a feature into a micro-frontend, isolate state per MFE. Each MFE gets its own store instances and query clients. Establish cross-MFE communication patterns (events, URL parameters) before extraction.

**State Management Becoming Unclear**: When developers can't easily answer "where does this data come from?" or "where is this state used?", refactor to clarify ownership. Document state flow, consolidate duplicate state, and establish clear patterns.

**Need for Time-Travel Debugging**: When debugging complex state transitions becomes difficult, consider Redux for its DevTools. However, most applications don't need this—lightweight stores with DevTools are usually sufficient.

**Cache Invalidation Bugs**: When stale data bugs become common, audit cache invalidation strategies. Map mutations to affected queries, document invalidation patterns, and add tests to catch missing invalidations.
