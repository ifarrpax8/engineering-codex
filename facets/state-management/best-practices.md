# State Management -- Best Practices

Effective state management balances simplicity, performance, and maintainability. These practices apply across frameworks and libraries, with stack-specific considerations where they materially affect outcomes.

## Contents

- [Separate Server State from Client State](#separate-server-state-from-client-state)
- [Keep State as Local as Possible](#keep-state-as-local-as-possible)
- [URL as Source of Truth for Navigation State](#url-as-source-of-truth-for-navigation-state)
- [Derive State, Don't Duplicate It](#derive-state-dont-duplicate-it)
- [Normalize Complex State](#normalize-complex-state)
- [Optimistic Updates for Perceived Performance](#optimistic-updates-for-perceived-performance)
- [Vue 3 / Pinia Specific Practices](#vue-3--pinia-specific-practices)
- [React / Zustand Specific Practices](#react--zustand-specific-practices)
- [TanStack Query Specific Practices](#tanstack-query-specific-practices)
- [VueQuery (TanStack Query for Vue) Specific Practices](#vuequery-tanstack-query-for-vue-specific-practices)

## Separate Server State from Client State

Server state (data fetched from APIs) has fundamentally different requirements than client state (UI toggles, form inputs, user preferences). Server state needs caching, background revalidation, error handling, and request deduplication. Client state needs reactivity and persistence.

Use dedicated server state libraries (TanStack Query for React, VueQuery for Vue) for all API data. These libraries handle loading states, error states, caching, revalidation, and deduplication automatically. Don't manually manage `loading`, `error`, and `data` flags with `useState` or `ref`—this creates boilerplate and misses important optimizations.

Keep client state in local component state or lightweight stores (Pinia, Zustand). Don't put API responses directly into stores unless you have a specific reason (like offline-first applications that need to sync local and remote state). Server state libraries provide better caching and revalidation than general-purpose stores.

The separation creates clear boundaries: server state libraries handle remote data, stores handle shared client state, and components handle local state. This makes code easier to understand, test, and maintain.

## Keep State as Local as Possible

The default should be local component state. Only promote state to a higher level when multiple unrelated components need it. This is the "lift state up only when needed" principle.

If only one component uses a piece of state, keep it local. A dropdown's open/closed state belongs in the dropdown component. A form's input values belong in the form component (unless the form is used in multiple places). Local state is easier to reason about, test, and maintain.

Promote to shared state only when necessary. If two sibling components need the same data, consider lifting state to their common parent first. If components in different parts of the application need the same data, use a store. If the data comes from an API, use a server state library.

Avoid premature abstraction. Don't create a store for state that might be shared in the future—wait until you actually need to share it. YAGNI (You Aren't Gonna Need It) applies to state management: keep it simple until complexity is justified.

## URL as Source of Truth for Navigation State

Filters, pagination, sort order, selected tabs, search queries, and selected item IDs should be in the URL. This makes states bookmarkable, shareable, and persistent across page refreshes.

Components should read from the URL and render accordingly. When users interact with filters or pagination, components update the URL, which triggers re-rendering. This creates a unidirectional flow: URL → component state → user interaction → URL update → component re-render.

Don't store navigation state in component state or stores when it should be in the URL. If a user can bookmark or share a view, that view's state must be in the URL. Storing it elsewhere creates inconsistencies and prevents bookmarking/sharing.

Use the router's capabilities for URL state management. Vue Router and React Router provide hooks for reading and updating URL parameters. Use these instead of manually parsing `window.location` or managing URL state separately.

## Derive State, Don't Duplicate It

If a value can be computed from other state, use a computed property or getter instead of storing it separately. Duplicated state gets out of sync, creating bugs that are hard to track down.

For example, don't store both `firstName` and `lastName` and also `fullName`. Instead, store `firstName` and `lastName`, and compute `fullName` as a getter. If `fullName` needs to be displayed in multiple places, the getter ensures it's always consistent.

Computed properties are automatically updated when their dependencies change. If `fullName` depends on `firstName` and `lastName`, updating either automatically updates `fullName`. Storing `fullName` separately requires manually updating it whenever `firstName` or `lastName` changes, which is error-prone.

This principle applies to derived lists, filtered data, aggregated values, and any state that can be calculated from other state. Use computed properties liberally—they're free in terms of storage and ensure consistency.

## Normalize Complex State

For collections of entities with relationships, normalize into flat structures with IDs as references. This prevents inconsistent updates where the same entity appears in multiple places.

For example, if you have users and their orders, don't store orders nested within user objects. Instead, store users in a `users` object keyed by ID and orders in an `orders` object keyed by ID. Orders reference users by ID. This ensures that updating a user updates it everywhere, not just in one nested location.

Normalization is particularly important for server state. When fetching a list of items and then fetching details for one item, both should reference the same normalized entity. Server state libraries like TanStack Query can help with normalization, or you can normalize manually before storing.

Denormalization (converting normalized data back to nested structures) should happen at the component level, not in stores. Components can combine normalized data as needed for rendering, but stores should maintain normalized structures.

## Optimistic Updates for Perceived Performance

Update the UI immediately when the user acts. Don't wait for the API response. Roll back if the API call fails. This makes the application feel instant and responsive.

Optimistic updates require three steps: update the cache optimistically, perform the mutation, and either confirm the update or roll it back based on the response. Server state libraries provide hooks for this (`onMutate`, `onError`, `onSettled` in TanStack Query).

Not all updates should be optimistic. Updates that are likely to fail (like complex validations) or updates with significant side effects should wait for server confirmation. Simple updates (like toggling a boolean, incrementing a counter) are good candidates for optimistic updates.

Error handling is critical for optimistic updates. Users must be notified if an optimistic update fails, and the UI must roll back cleanly. Don't leave the UI in an inconsistent state if the server rejects the change.

## Vue 3 / Pinia Specific Practices

Define stores with `defineStore`. Use the setup function syntax for composable stores that use other stores or composables. Use the options API syntax for simpler stores that don't need composition.

Use `storeToRefs()` when destructuring store state in components. Direct destructuring loses reactivity—`const { count } = store` creates a non-reactive value. `const { count } = storeToRefs(store)` maintains reactivity.

Composable stores (stores that use other stores) enable code reuse and modular design. A user store might use an auth store to check permissions. A cart store might use a product store to get product details. This creates clear dependencies and reusable logic.

Use `$reset()` for testing and development. The `$reset()` method resets store state to initial values, which is useful in tests and when developing. However, avoid using it in production code—it can cause unexpected state loss.

Pinia stores are automatically reactive. You can mutate state directly in actions—no need for immutable update patterns like Redux. However, be careful with object and array mutations to ensure Vue's reactivity system tracks changes correctly.

## React / Zustand Specific Practices

Create stores with `create()`, which accepts a function returning state and actions. The function receives `set` and `get` parameters for updating and reading state. This creates a simple, functional API.

Use selectors to minimize re-renders. Instead of `const count = useStore(state => state.count)`, use `const count = useStore(state => state.count)`. The selector function ensures the component only re-renders when the selected value changes, not when any store state changes.

Middleware extends Zustand's capabilities. The `persist` middleware syncs state to localStorage automatically. The `devtools` middleware integrates with Redux DevTools for debugging. The `immer` middleware enables mutable-style updates with immutable results.

Zustand stores can be used outside React components. Import the store directly and call `store.getState()` or `store.setState()` anywhere in your application. This is useful for updating state from event handlers, timers, or other non-React code.

Avoid storing functions in Zustand state. Functions aren't serializable and can cause issues with persistence middleware. Store data and derive functions in actions or outside the store.

## TanStack Query Specific Practices

Use `useQuery` for reads and `useMutation` for writes. Queries are for fetching data, mutations are for creating, updating, or deleting data. Don't use `useQuery` for mutations—it's not designed for that.

Invalidate related queries after mutations using `onSuccess` callbacks. After creating a user, invalidate `['users']` to refresh user lists. After updating a user, invalidate both `['users']` and `['users', userId]` to refresh lists and detail views.

Configure `staleTime` appropriately. Data that changes frequently should have short stale times (seconds or minutes). Data that changes rarely can have long stale times (hours or days). The default (0) means data is always stale and refetches immediately, which may be too aggressive.

Use `queryClient.invalidateQueries` for programmatic cache invalidation. After mutations in one component, invalidate related queries to ensure other components see fresh data. Map out which mutations affect which queries and invalidate them explicitly.

Leverage automatic request deduplication. Multiple components using the same query key will share a single request. This happens automatically—just ensure consistent cache key structures across components.

Use `keepPreviousData: true` for pagination to prevent UI flicker. When moving to the next page, the previous page's data remains visible while new data loads. This creates a smoother pagination experience.

## VueQuery (TanStack Query for Vue) Specific Practices

VueQuery wraps TanStack Query with Vue's reactivity system. `useQuery` returns reactive refs that can be used directly in templates. The API is nearly identical to TanStack Query, adapted for Vue's composition API.

Use `useQuery` and `useMutation` in the same way as TanStack Query. The patterns are identical: `useQuery` for reads, `useMutation` for writes, `onSuccess` for cache invalidation. The main difference is that returned values are reactive refs.

VueQuery integrates with Vue's reactivity system. Computed properties can depend on query results, and they'll update automatically when queries refetch. This creates seamless reactivity throughout the component.

Use `suspense: true` for loading states handled by Suspense boundaries. This enables Vue's Suspense component to handle loading states declaratively, reducing boilerplate in components.

VueQuery provides the same caching, revalidation, and deduplication as TanStack Query. All the same best practices apply: configure `staleTime`, invalidate queries after mutations, use consistent cache keys, and leverage automatic deduplication.
