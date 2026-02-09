# State Management -- Gotchas

Common pitfalls in state management create bugs, performance issues, and maintenance problems. Recognizing these patterns helps avoid them.

## Putting Everything in Global State

Treating the store like a database where every piece of data goes into the global store creates unnecessary coupling and re-renders. Most state is local. API data belongs in a server state manager, not a global store.

The symptom is a store that grows indefinitely, containing form inputs, API responses, UI toggles, computed values, and everything else. Components become tightly coupled to the store, making changes risky and testing difficult.

The fix is to use the right tool for each type of state. Local component state for component-specific data. Server state libraries for API data. Global stores only for truly shared client state. This creates clear boundaries and reduces coupling.

Developers often reach for global state to avoid prop drilling, but prop drilling through 2-3 levels is perfectly fine and more explicit than global state. Use provide/inject (Vue) or context (React) for deeper trees before considering a global store.

## Not Distinguishing Server State from Client State

Manually managing loading/error/data for every API call with `useState` or `ref` leads to boilerplate, stale data, missing loading states, and no caching. This is one of the most common mistakes in state management.

The symptom is components with multiple state variables: `isLoading`, `error`, `data`, `isRefreshing`, etc., repeated for every API call. Cache invalidation is manual and error-prone. Request deduplication doesn't happen. Background revalidation doesn't happen.

The fix is to use a server state library (TanStack Query, VueQuery) for all API data. These libraries handle loading states, error states, caching, revalidation, and deduplication automatically. They eliminate most of the boilerplate and provide better user experience.

Developers sometimes avoid server state libraries because they seem like "another dependency," but they eliminate far more code than they add. The reduction in boilerplate and improvement in user experience justifies the dependency.

## Stale Closures in React

Event handlers and effects capture stale state values when they're created. This is common when using `setTimeout`, event listeners, or async operations inside `useEffect`. The closure captures the state value at effect creation time, not the current value.

The symptom is handlers that use old state values. A click handler might use a count value from when the component first rendered, not the current count. An effect might use a user ID from when it was created, not the current user ID.

The fix depends on the situation. For values that need to be current, use refs (`useRef`) which always hold the latest value. For effects, include all dependencies in the dependency array so the effect re-runs when values change. For event handlers, use functional updates (`setState(prev => prev + 1)`) when possible.

The React ESLint plugin's `exhaustive-deps` rule helps catch missing dependencies. However, sometimes you intentionally want to capture a value at a specific time—in those cases, the linter warning can be disabled with a comment explaining why.

## Reactivity Pitfalls in Vue

Destructuring a Pinia store loses reactivity. `const { count } = store` creates a non-reactive value. Updating `count` in the store won't update the component. This is a common mistake when migrating from Options API to Composition API.

The fix is to use `storeToRefs()` when destructuring: `const { count } = storeToRefs(store)`. This maintains reactivity for all destructured properties. For actions, regular destructuring is fine since actions don't need to be reactive.

Replacing a reactive object instead of mutating its properties breaks reactivity tracking. `state.user = newUser` replaces the entire object, which Vue's reactivity system may not track correctly. Instead, mutate properties: `state.user.name = newUser.name` and `state.user.email = newUser.email`, or use `Object.assign(state.user, newUser)`.

Vue's reactivity system uses Proxies to track property access. Replacing entire objects can break this tracking. Mutating properties ensures the reactivity system can track changes correctly.

## Over-Rendering

Updating global state that many components subscribe to causes all of them to re-render, even if they don't use the changed data. This creates performance issues, especially with large component trees.

The symptom is components re-rendering unnecessarily. A component that only displays a user's name re-renders when the user's email changes. A component that only uses a count re-renders when unrelated state changes.

The fix is to use selectors (Zustand) or computed properties (Pinia) to narrow subscriptions to only the data each component needs. `useStore(state => state.user.name)` in Zustand ensures the component only re-renders when `user.name` changes, not when other user properties change.

In React, `useMemo` and `useCallback` can help, but selectors are more effective. In Vue, computed properties automatically narrow reactivity, but be careful with object destructuring as mentioned above.

Performance profiling tools (React DevTools Profiler, Vue DevTools) help identify unnecessary re-renders. Regular profiling during development catches these issues before they become problems.

## Forgetting to Clean Up

Subscriptions, event listeners, and timers created in components or stores that aren't cleaned up on unmount cause memory leaks and ghost updates. Components that are unmounted continue to receive updates, causing errors and memory leaks.

The symptom is errors about updating unmounted components, memory usage that grows over time, or event handlers firing for components that no longer exist. These issues are subtle and may not be noticed immediately.

The fix is to always clean up resources. In Vue, use `onUnmounted` to clean up subscriptions, event listeners, and timers. In React, return a cleanup function from `useEffect`. In stores, provide cleanup methods that components can call in their unmount hooks.

Server state libraries handle cleanup automatically—unmounting a component unsubscribes it from queries. However, manual subscriptions (like event listeners or custom pub/sub systems) require manual cleanup.

Testing helps catch cleanup issues. Tests that mount and unmount components repeatedly can reveal memory leaks. Memory profiling tools can identify leaks in running applications.

## Cache Invalidation Bugs

After a mutation, forgetting to invalidate related caches causes stale data to persist. A user creates an item, but the list view still shows the old data because the list cache wasn't invalidated.

The symptom is UI that doesn't reflect the latest server state. Users see outdated information, make decisions based on stale data, or wonder why their changes don't appear. This erodes trust in the application.

The fix is to map out which mutations affect which queries and invalidate them explicitly. After creating a user, invalidate `['users']`. After updating a user, invalidate both `['users']` and `['users', userId]`. After deleting a user, invalidate `['users']` and remove `['users', userId]` from cache.

Server state libraries provide `onSuccess` callbacks in mutations for cache invalidation. Use `queryClient.invalidateQueries` to mark queries as stale and trigger refetches. For immediate updates without refetching, use `queryClient.setQueryData` to update cache directly.

Documentation and code reviews help catch missing invalidations. When adding a mutation, document which queries it affects. Code reviews should verify that all affected queries are invalidated.

## Losing State on Navigation

Navigating away from a form loses user input if the form state isn't persisted. Users spend time filling out forms, accidentally navigate away, and lose their work. This is frustrating and reduces trust.

The symptom is forms that reset when users navigate away and return. Users must re-enter all their data, which is time-consuming and error-prone. Users learn to avoid navigation while filling forms, which limits their ability to reference other parts of the application.

The fix depends on requirements. For short forms, warn users before navigating away with unsaved changes. For long forms, persist draft state to localStorage or a store that survives navigation. For critical forms, use `<KeepAlive>` (Vue) to preserve component state across navigation.

Form libraries often provide draft persistence features. React Hook Form can persist to localStorage automatically. VeeValidate (Vue) can integrate with persistence solutions. Consider user expectations—users expect drafts to be saved automatically for long forms.

The browser's `beforeunload` event can warn users about unsaved changes when they try to close the tab, but it can't prevent navigation within the application. For in-app navigation, use route guards or form state persistence.

## Prop Drilling Avoidance Overcorrection

Moving everything to a global store to avoid passing props obscures data flow. Prop drilling through 2-3 levels is perfectly fine and more explicit than global state. Overcorrecting creates unnecessary coupling.

The symptom is a store that contains data only used by a few related components. The data flow becomes unclear—where does this data come from? Where is it used? Changes become risky because it's unclear what depends on the data.

The fix is to use the right tool for the depth. Props for 2-3 levels. Provide/inject (Vue) or context (React) for deeper trees. Global stores only for data used by many unrelated components. This creates clear data flow and reduces coupling.

Explicit prop passing makes data dependencies clear. When reviewing code, it's obvious which components use which data. With global state, dependencies are hidden, making changes riskier.

## Synchronizing State Across Tabs

User logs out in one tab but remains logged in in another tab. User changes theme in one tab but other tabs don't update. This creates inconsistent experiences across browser tabs.

The symptom is state that differs across tabs. Users see different data, different UI states, or different authentication status in different tabs. This confuses users and can cause security issues if authentication state is inconsistent.

The fix is to use cross-tab synchronization mechanisms where needed. The `BroadcastChannel` API allows communication between tabs. The `storage` event fires when localStorage or sessionStorage changes in other tabs. Use these to synchronize critical state like authentication and theme.

For authentication, listen for storage events or use BroadcastChannel to detect logouts in other tabs. When detected, clear local state and redirect to login. For theme and other preferences, sync changes across tabs so users have a consistent experience.

Not all state needs cross-tab synchronization. Form drafts, UI toggles, and temporary state should remain tab-specific. Only synchronize state that users expect to be consistent across tabs: authentication, theme, locale, and similar global preferences.

Server state libraries handle cross-tab synchronization for cached data through storage events, ensuring that data fetched in one tab is available in others. However, this only works if the same cache key is used and if the library is configured for cross-tab synchronization.
