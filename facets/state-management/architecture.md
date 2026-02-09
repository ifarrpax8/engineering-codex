# State Management -- Architecture

State management architecture determines how data flows through an application, where state lives, how it's updated, and how components react to changes. The architecture must balance simplicity, performance, maintainability, and developer experience.

## Contents

- [Types of State](#types-of-state)
- [State Management Architectures](#state-management-architectures)
- [State Ownership in MFE](#state-ownership-in-mfe)
- [Server State Caching](#server-state-caching)
- [Persistence](#persistence)

## Types of State

Understanding the different types of state is fundamental to choosing appropriate management strategies. Each type has different lifecycle requirements, sharing patterns, and persistence needs.

### Local Component State

Local component state belongs to a single component and has no meaning outside that component's scope. Examples include form input values, toggle states for dropdowns or modals, hover states, and temporary UI flags. This state lives in the component, is initialized when the component mounts, and is destroyed when the component unmounts.

Local state is managed using framework primitives: `useState` in React or `ref` in Vue. It doesn't require external libraries or complex patterns. The component owns the state completely, making it easy to reason about and test. Local state should be the default choice—only promote state to a higher level when multiple components need it.

The lifecycle of local state is tied to the component lifecycle. When a component unmounts, its local state is garbage collected. This is usually desirable—there's no need to persist a dropdown's open/closed state across navigation. However, if state needs to survive component unmounting (like draft form data), it should be moved to a store or persisted to localStorage.

### Shared Application State

Shared application state is used by multiple unrelated components that don't have a direct parent-child relationship. Examples include authenticated user information, theme preferences, locale settings, tenant context, and feature flags. This state needs to be accessible from anywhere in the application without prop drilling.

Shared state requires a global store mechanism: Pinia in Vue, Zustand or Redux in React, or similar solutions. The store acts as a single source of truth, ensuring all components see the same values. Updates to shared state automatically propagate to all subscribed components through reactivity.

The key decision is when to use shared state versus local state. A good rule: if only one component uses a piece of state, keep it local. If multiple unrelated components need it, use shared state. If components are related (parent-child), consider prop drilling or provide/inject (Vue) or context (React) before reaching for a global store.

### Server State (Remote Data)

Server state represents data fetched from APIs. It has a complex lifecycle: initial loading, success with data, error states, stale data that needs refreshing, and revalidating states. This is the most common source of state management complexity in modern applications.

Server state differs from client state in several ways. It's stored remotely, so fetching it requires network requests. It can become stale—data on the server may have changed since it was fetched. It needs caching to avoid redundant requests. It needs error handling for network failures. It needs loading states to show progress. It needs invalidation strategies to keep it fresh.

Managing server state manually with `useState` or `ref` leads to boilerplate: loading flags, error handling, cache management, deduplication logic, and invalidation strategies. This is why dedicated server state libraries like TanStack Query (React) or VueQuery (Vue) exist. They handle all these concerns automatically.

Server state should be kept separate from client state. Don't put API responses directly into Pinia or Zustand stores unless you have a specific reason. Server state libraries provide better caching, revalidation, and error handling than general-purpose stores.

### URL State

URL state is encoded in the URL through query parameters, path parameters, or hash fragments. Examples include the current page number, active filters, selected tab, sort order, search query, and selected item ID. This state survives page refreshes, is shareable via links, and is bookmarkable.

URL state should be the source of truth for navigation-related state. If a user can bookmark or share a particular view (like a filtered, sorted list), that state must be in the URL. This makes the application more predictable—refreshing the page shows the same view, and sharing a URL shows the same view to others.

URL state is managed through the router: Vue Router in Vue applications, React Router in React applications. Components read URL state through router hooks (`useRoute`, `useRouter` in Vue; `useSearchParams`, `useNavigate` in React) and update it through navigation functions.

The relationship between URL state and component state requires careful consideration. URL state should drive component rendering—components read from the URL and render accordingly. When users interact with filters or pagination, components update the URL, which triggers re-rendering. This creates a unidirectional flow: URL → component state → user interaction → URL update → component re-render.

### Form State

Form state encompasses input values, validation errors, dirty/pristine tracking, touched/untouched states, and submission status. Forms have unique requirements: they need to track which fields have been modified, which have validation errors, and whether the form is currently being submitted.

Form state can be managed at different levels depending on complexity. Simple forms with a few inputs can use local component state. Complex forms with many fields, conditional validation, and nested structures benefit from dedicated form libraries: Formik or React Hook Form in React, VeeValidate in Vue.

Form state often needs persistence for draft saving. Users expect to be able to start filling out a form, navigate away, and return to find their input preserved. This requires either storing form state in a store that persists across navigation or saving drafts to localStorage or a backend API.

Form state also needs coordination with server state. When a form is submitted, it typically triggers a mutation that updates server state. The form state must handle loading states during submission, success states after submission, and error states if submission fails. After successful submission, related server state caches may need invalidation.

## State Management Architectures

Different architectural patterns solve different problems. Choosing the right pattern depends on application complexity, team preferences, and specific requirements.

### Flux/Redux Pattern

The Flux pattern, popularized by Redux, implements unidirectional data flow: actions → reducers → state → view. User interactions dispatch actions, actions are processed by reducers that produce new state, state updates trigger view re-renders, and the cycle repeats. This creates predictable, debuggable state updates.

Redux provides time-travel debugging, where developers can step backward and forward through state changes to understand how the application reached its current state. This is invaluable for debugging complex state transitions. Redux DevTools provide powerful inspection and debugging capabilities.

The Redux pattern can be verbose. Simple state updates require defining action types, action creators, and reducers. For applications that don't need this level of structure, the verbosity isn't justified. However, for applications with complex state transitions, multiple sources of truth, or requirements for time-travel debugging, Redux provides valuable structure.

Modern Redux with Redux Toolkit reduces much of the boilerplate through `createSlice`, which combines actions and reducers. This makes Redux more approachable while retaining its benefits. However, for most applications, lighter-weight solutions are sufficient.

### Reactive Stores

Reactive stores like Pinia (Vue) and Zustand (React) provide a simpler alternative to full Flux architectures. They define stores with state, computed properties (getters), and actions. Components subscribe to stores reactively, automatically re-rendering when relevant state changes.

Pinia stores are defined with `defineStore`, which accepts a setup function or an options object. The setup function approach allows using composables within stores, creating composable stores that use other stores. This enables code reuse and modular store design. Pinia integrates deeply with Vue's reactivity system, making state updates automatic and efficient.

Zustand stores are created with `create`, which accepts a function that returns the store state and actions. Zustand is minimal—the entire library is small and has no dependencies. It supports middleware for features like persistence and Redux DevTools integration. Zustand's selector pattern allows components to subscribe to specific slices of state, minimizing re-renders.

Both Pinia and Zustand are simpler than Redux while providing most of the benefits. They're suitable for the majority of applications that need shared state but don't require the full structure of Flux. They're easier to learn, require less boilerplate, and integrate naturally with their respective frameworks.

### Server State Managers

Server state managers like TanStack Query (React) and VueQuery (Vue wrapper for TanStack Query) handle the entire lifecycle of server data. They manage fetching, caching, background revalidation, request deduplication, pagination, infinite scrolling, and optimistic updates.

TanStack Query uses a query client that manages a cache of server data. Queries are defined with `useQuery`, which accepts a query key and a query function. The query key uniquely identifies the cached data—changing the key creates a new cache entry. Query functions are async functions that fetch data.

TanStack Query automatically handles loading states, error states, and success states. It provides `isLoading`, `isError`, `error`, and `data` properties that components can use to render appropriately. It handles request deduplication—if multiple components request the same data simultaneously, only one request is made.

Background revalidation keeps data fresh. TanStack Query can be configured to refetch data when the window regains focus, when the network reconnects, or on a time interval. The `staleTime` configuration determines how long data is considered fresh before it needs revalidation. The `cacheTime` configuration determines how long unused data remains in cache.

Mutations are handled with `useMutation`, which provides `mutate` and `mutateAsync` functions. Mutations can invalidate related queries after success, ensuring the UI reflects the latest data. Optimistic updates can be implemented by updating the cache immediately and rolling back on error.

VueQuery provides the same capabilities for Vue applications, wrapping TanStack Query with Vue's reactivity system. `useQuery` returns reactive refs that components can use directly in templates. The patterns are identical to TanStack Query, adapted for Vue's composition API.

### Atomic State

Atomic state libraries like Jotai (React) take a bottom-up approach where each piece of state is an independent atom. Components subscribe to specific atoms, and only those components re-render when those atoms change. This creates minimal re-renders and fine-grained reactivity.

Atoms are defined independently and can depend on other atoms through derived atoms. This creates a graph of state dependencies that updates efficiently. When an atom changes, only atoms that depend on it and components subscribed to those atoms update.

Atomic state is particularly useful for applications with many small, independent pieces of state. It avoids the need to structure state into larger stores and allows components to subscribe to exactly the data they need. However, it can be more complex to reason about than traditional stores, especially for developers unfamiliar with the pattern.

## State Ownership in MFE

Micro-frontend architectures require careful consideration of state ownership. Each MFE should own its state independently, with no shared global store across MFEs. This isolation prevents state leakage and ensures MFEs can be developed, tested, and deployed independently.

### Per-MFE State Isolation

Each MFE has its own instance of state management libraries. If using Pinia, each MFE has its own Pinia instance. If using TanStack Query, each MFE has its own query client. This ensures complete isolation—state changes in one MFE don't affect another.

This isolation means that MFEs cannot directly share state through stores. If two MFEs need to share data, they must use other mechanisms: browser events, URL parameters, or a lightweight pub/sub bus provided by the shell application.

### Cross-MFE Communication

When MFEs need to communicate, they use browser events (CustomEvent API) or a message bus provided by the shell. For example, when a user updates their profile in one MFE, that MFE dispatches a custom event. Other MFEs listen for this event and update their local state accordingly.

URL parameters are another mechanism for cross-MFE communication. When one MFE updates the URL (changing filters or selected item), other MFEs can read from the URL and update their state. This creates loose coupling—MFEs don't need direct references to each other.

The shell application can provide a lightweight pub/sub bus for cross-MFE communication. MFEs publish events to the bus and subscribe to events from other MFEs. This centralizes communication patterns while maintaining MFE isolation.

### Shared Context Injection

Some state must be shared across all MFEs: authenticated user information, tenant context, feature flags, and theme preferences. This shared context is provided by the shell application and injected into MFEs at mount time.

The shell fetches shared context (user, tenant, etc.) and passes it to MFEs as props or through a context provider. MFEs receive this context as read-only data—they don't modify it directly. If shared context needs to change, the shell handles the update and re-injects it into MFEs.

This pattern maintains MFE isolation while allowing necessary shared data. MFEs don't need to fetch user information independently—they receive it from the shell. This reduces redundant API calls and ensures consistency across MFEs.

## Server State Caching

Effective server state caching is crucial for performance and user experience. Caching reduces network requests, improves perceived performance, and enables offline capabilities.

### Cache Keys

Cache keys uniquely identify cached data. In TanStack Query, cache keys are arrays that can include strings, numbers, and objects. For example, `['users', { page: 1, status: 'active' }]` uniquely identifies the first page of active users. Changing any part of the key creates a new cache entry.

Cache keys should be deterministic—the same inputs should always produce the same key. They should include all parameters that affect the data returned by the query. Pagination, filters, sort order, and search terms should all be part of the cache key.

Hierarchical cache keys enable partial invalidation. For example, `['users']` can be used to invalidate all user-related queries, while `['users', userId]` invalidates a specific user. This allows fine-grained cache management.

### Stale-While-Revalidate

The stale-while-revalidate pattern serves cached data immediately while fetching fresh data in the background. When fresh data arrives, the UI updates. This provides instant perceived performance while ensuring data freshness.

TanStack Query implements this pattern automatically. When a query is requested, if cached data exists (even if stale), it's returned immediately. A background refetch occurs if the data is stale. When fresh data arrives, components automatically re-render with the new data.

The `staleTime` configuration determines how long data is considered fresh. Data fresher than `staleTime` doesn't trigger a background refetch. Data older than `staleTime` triggers a background refetch but is still served immediately from cache.

This pattern is essential for good user experience. Users see data immediately (from cache) while fresh data loads in the background. The transition from stale to fresh data is seamless, and users rarely notice it happening.

### Cache Invalidation

Cache invalidation ensures the UI reflects the latest server state after mutations. When a user creates, updates, or deletes a resource, related caches must be invalidated to prevent showing stale data.

After a successful mutation, related queries should be invalidated using `queryClient.invalidateQueries`. This marks the queries as stale and triggers refetches if those queries are currently being used. For example, after creating a user, invalidate `['users']` to refresh user lists.

Invalidation can be specific or broad. Invalidating `['users']` refreshes all user list queries. Invalidating `['users', userId]` refreshes only that specific user's data. The granularity depends on the mutation's scope.

Some mutations require updating the cache directly instead of invalidating. For example, after updating a user's name, directly updating the cache for that user avoids an unnecessary network request. However, this requires careful cache key management to ensure the update applies to all relevant cache entries.

### Optimistic Updates

Optimistic updates immediately update the UI when a user acts, before the server confirms the change. If the server request succeeds, the optimistic update becomes the real update. If it fails, the update is rolled back and an error is shown.

Optimistic updates require three steps: update the cache optimistically, perform the mutation, and either confirm the update or roll it back based on the response. TanStack Query's `onMutate` callback allows updating the cache before the mutation, and `onError` allows rolling back on failure.

Optimistic updates make applications feel instant. Users see their changes immediately, creating a responsive feel. However, they require careful error handling—failed mutations must roll back cleanly, and users must be notified of failures.

The complexity of optimistic updates varies by use case. Simple updates (like toggling a boolean) are straightforward. Complex updates (like reordering a list) require more careful implementation to ensure rollback works correctly.

### Deduplication

Request deduplication ensures that multiple components requesting the same data simultaneously result in a single API call. Without deduplication, each component would make its own request, wasting bandwidth and potentially causing race conditions.

TanStack Query automatically deduplicates requests. If multiple components call `useQuery` with the same cache key while a request is in flight, only one request is made. All components receive the same promise and update when the request completes.

Deduplication requires consistent cache keys. Components must use the same key structure to request the same data. This is why cache key design is important—inconsistent keys prevent deduplication.

Deduplication also applies to mutations. If the same mutation is triggered multiple times rapidly (like a user double-clicking a submit button), it should be debounced or deduplicated to prevent duplicate submissions.

## Persistence

State persistence allows applications to survive page refreshes and maintain user preferences across sessions. Different types of state require different persistence strategies.

### localStorage and sessionStorage

localStorage persists data across browser sessions—data survives browser restarts. sessionStorage persists data only for the current session—data is cleared when the browser tab is closed. Both provide key-value storage with string keys and string values (objects must be serialized to JSON).

localStorage is appropriate for user preferences that should persist indefinitely: theme selection, locale preference, collapsed sidebar state, and default filter values. These preferences enhance user experience by remembering user choices.

sessionStorage is appropriate for temporary state that should survive page refreshes but not browser restarts: draft form data, scroll positions, and temporary UI state. This prevents data loss from accidental refreshes while avoiding cluttering localStorage with temporary data.

Both storage APIs are synchronous and blocking, so they shouldn't be used for large amounts of data or frequent writes. For large datasets, consider IndexedDB. For frequent writes, batch updates or use a debounced write strategy.

Store libraries often provide persistence middleware. Zustand's `persist` middleware automatically syncs store state to localStorage. Pinia plugins can provide similar functionality. These solutions handle serialization, deserialization, and hydration automatically.

### URL Parameters

URL parameters persist state that should be shareable and bookmarkable. Filters, pagination, sort order, selected tabs, and search queries are good candidates for URL state. Users can bookmark filtered views, share links to specific pages, and refresh without losing their place.

URL parameters are managed through the router. Components read parameters using router hooks and update them through navigation functions. The router handles encoding, decoding, and browser history management.

URL parameters have limitations: they're visible to users, they have length limits, and they're logged in browser history and server logs. Sensitive data shouldn't be in URLs. Large amounts of data shouldn't be in URLs. However, for navigation-related state, URL parameters are the right choice.

The relationship between URL parameters and component state requires careful management. URL should be the source of truth—components read from URL and render accordingly. When users interact with controls, components update the URL, which triggers re-rendering. This creates predictable, debuggable state flow.

### Cookies

Cookies are appropriate for small pieces of data that need to be sent to the server with every request: authentication tokens, session identifiers, and CSRF tokens. Cookies have size limits (typically 4KB) and are sent with every request, so they shouldn't be used for large amounts of data.

Authentication tokens should be stored in httpOnly cookies when possible, preventing JavaScript access and reducing XSS attack surface. Secure cookies (sent only over HTTPS) protect tokens in transit. SameSite attributes prevent CSRF attacks.

Cookies are managed by the browser and sent automatically with requests. Applications typically don't manage cookies directly—they're set by the server and read by the server. However, applications may need to read cookies for client-side logic (like showing user information).

For state management purposes, cookies are rarely the right choice unless the state needs to be sent to the server. Most application state should use localStorage, sessionStorage, or URL parameters instead.
