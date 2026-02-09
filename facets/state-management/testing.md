# State Management -- Testing

Testing state management requires strategies at multiple levels: unit testing stores in isolation, testing components with state, testing server state lifecycle, integration testing complete flows, and performance testing to prevent unnecessary re-renders.

## Store Unit Testing

Store unit tests verify that stores work correctly in isolation, without rendering components or making actual API calls. These tests are fast, focused, and easy to debug.

### Testing Store Actions

Store actions should be tested by calling them with various inputs and verifying the resulting state changes. For example, a `increment` action should increase a count value, and a `setUser` action should update the user state. Tests should verify both the direct state changes and any side effects (like localStorage updates).

Actions that perform async operations (like API calls) should be tested with mocked dependencies. Mock the API client or fetch function, call the action, and verify that the state updates correctly when the promise resolves or rejects. Test both success and error paths.

Actions that depend on other stores should be tested with mocked store dependencies. Use dependency injection or a test double for the dependent store to isolate the action under test. This ensures tests don't break when dependent stores change.

### Testing Store Getters/Computed Properties

Getters and computed properties derive values from store state. Tests should verify that getters return correct values for various state configurations. For example, a `fullName` getter should concatenate `firstName` and `lastName` correctly, and a `isAuthenticated` getter should return `true` when a user exists and `false` when it doesn't.

Getters that depend on multiple pieces of state should be tested with various combinations of those state values. Edge cases are particularly important: empty strings, null values, undefined values, and boundary conditions.

Getters that perform calculations should be tested with known inputs and expected outputs. For example, a `totalPrice` getter that sums item prices should be tested with empty arrays, single items, multiple items, and items with zero or negative prices.

### Testing Store State Initialization

Store state should be tested to verify correct initial values. Create a new store instance and verify that all state properties have expected default values. This catches issues where state isn't properly initialized or where initial values are incorrect.

Stores that hydrate state from localStorage or other sources should be tested to verify hydration works correctly. Mock the storage API, set values, create a store instance, and verify that the store state matches the stored values. Test cases where storage is empty, corrupted, or contains invalid data.

### Testing Store Reactivity

In Vue applications, stores should be tested to verify that computed properties update reactively when state changes. Update state directly, then verify that computed properties reflect the changes. This ensures the reactivity system is working correctly.

In React applications with Zustand, test that selectors return updated values when state changes. Update state using actions, then verify that selectors return the new values. This ensures the subscription mechanism works correctly.

## Component + State Testing

Components that use stores should be tested to verify they render correctly based on store state and that user interactions trigger store actions correctly.

### Testing Component Rendering Based on Store State

Mount a component with a pre-configured store and verify that the component renders correctly. For example, if a store has `user: null`, verify that a login form is shown. If the store has `user: { name: 'John' }`, verify that the user's name is displayed.

Test various store states to ensure components handle all cases: loading states, error states, empty states, and populated states. Components should render appropriately for each state, showing loading indicators, error messages, empty placeholders, or data as appropriate.

Components that use multiple stores should be tested with various combinations of store states. Verify that the component renders correctly regardless of which stores have data and which are loading or errored.

### Testing User Interactions Trigger Store Actions

Simulate user interactions (clicks, form submissions, input changes) and verify that store actions are called with correct parameters. Use a spy or mock to capture action calls and verify their arguments. For example, clicking a "Logout" button should call a `logout` action, and submitting a form should call an action with the form data.

Test that actions are called at the right times. Some actions should be called immediately on interaction (like opening a modal). Others should be called after validation passes (like form submission). Verify the timing matches expectations.

Test error handling: when an action throws an error or returns a rejected promise, verify that the component handles it appropriately (shows an error message, doesn't crash, allows retry). Mock actions to throw errors and verify component behavior.

### Testing Component Updates When Store Changes

Update store state (either directly or through actions) and verify that components re-render with the new state. This ensures that component subscriptions to stores are working correctly. In Vue, this happens automatically through reactivity. In React, components using Zustand hooks should update automatically.

Test that components update efficiently—they should only re-render when relevant store state changes. A component subscribed to `user.name` should not re-render when `user.email` changes (if using proper selectors). Verify this by tracking render counts or using testing utilities that detect unnecessary re-renders.

## Server State Testing

Server state has a complex lifecycle: loading, success, error, stale, and revalidating states. Testing must cover all these states and the transitions between them.

### Mocking API Responses

Use MSW (Mock Service Worker) or similar tools to mock API responses. MSW intercepts network requests at the service worker level, allowing realistic testing of server state without actual network calls. Define mock handlers for each API endpoint, including success responses, error responses, and delayed responses to test loading states.

Mock handlers should be flexible enough to test various scenarios: successful responses with data, empty responses, error responses with different status codes, and network failures. Use MSW's `http.get`, `http.post`, etc., to define handlers that return appropriate responses.

Test that components handle all response types correctly. A component using `useQuery` should show loading state initially, show data when the query succeeds, and show an error message when the query fails. Verify each state renders correctly.

### Testing Cache Invalidation

After mutations, verify that related caches are invalidated and queries are refetched. Create a query that fetches a list, perform a mutation that should invalidate that list, and verify that the query refetches automatically. Use MSW to verify that the refetch request is made.

Test that invalidation is scoped correctly. Invalidating `['users']` should invalidate all user list queries but not user detail queries (unless they're also invalidated). Verify that only the intended caches are invalidated.

Test that components update correctly after cache invalidation. After a mutation invalidates a cache, components using that cache should show loading state briefly, then update with fresh data. Verify this flow works smoothly.

### Testing Optimistic Updates

Test optimistic updates by verifying that the UI updates immediately when a mutation is triggered, before the server responds. Mock the API to have a delay, trigger the mutation, and verify that the UI shows the optimistic state immediately.

Test rollback on error: when an optimistic update is followed by a failed API call, verify that the UI rolls back to the previous state and shows an error message. Mock the API to return an error and verify the rollback behavior.

Test that optimistic updates don't cause issues with concurrent updates. If multiple optimistic updates happen simultaneously, verify that they don't conflict and that the final state is correct after all server responses arrive.

### Testing Request Deduplication

Verify that multiple components requesting the same data simultaneously result in a single API call. Render multiple components that use the same query, and verify (using MSW or network mocking) that only one request is made. All components should receive the same data when the request completes.

Test that deduplication works with different cache keys. Components using different keys should make separate requests, while components using the same key should share a request. Verify this behavior.

## Integration Testing

Integration tests verify that complete user flows work correctly: user interaction triggers state changes, state changes trigger API calls, API responses update state, and state updates cause UI changes.

### Testing Complete User Flows

Test flows from user interaction to final UI update. For example, test a flow where a user fills out a form, submits it, sees a loading state, sees a success message, and sees the new data in a list. Use Playwright or similar tools for end-to-end testing, or use Testing Library for component integration testing.

Integration tests should use real (or realistically mocked) APIs, real routing, and real state management. They should verify that all parts of the system work together correctly. These tests are slower than unit tests but catch issues that unit tests miss.

Test error flows as well as success flows. What happens when a form submission fails? What happens when a list fails to load? What happens when the network is offline? Verify that error states are handled gracefully and that users can recover from errors.

### Testing State Persistence

Test that state persists correctly across page refreshes. Set up application state (user logged in, filters applied, form data entered), refresh the page, and verify that the state is restored correctly. This requires testing localStorage reads and writes, URL parameter encoding and decoding, and state hydration on application startup.

Test that persisted state is used correctly. If a user has a preference stored in localStorage, verify that the application uses that preference on startup. If a URL contains parameters, verify that the application reads those parameters and applies them.

Test edge cases: corrupted localStorage data, missing localStorage data, invalid URL parameters, and state that can't be serialized. Verify that the application handles these cases gracefully without crashing.

### Testing Cross-Component State Sharing

Verify that state changes in one component are reflected in other components that use the same state. Update state through one component's interaction, and verify that other components update accordingly. This ensures that shared state is working correctly.

Test that components don't interfere with each other's state when they shouldn't. Components using local state shouldn't affect each other. Components using different stores shouldn't affect each other. Verify isolation where it's expected.

## Performance Testing

Performance testing verifies that state management doesn't cause unnecessary re-renders or performance degradation.

### Verifying Minimal Re-renders

Use React DevTools Profiler or Vue DevTools to identify components that re-render unnecessarily. Trigger a state change and verify that only components that depend on that state re-render. Components that don't depend on the changed state should not re-render.

In tests, track render counts for components. Update state and verify that render counts increase only for components that should re-render. Use testing utilities that provide render tracking, or add render tracking manually in test environments.

Test that selectors (in Zustand) or computed properties (in Pinia) prevent unnecessary re-renders. A component subscribed to `state.user.name` should not re-render when `state.user.email` changes. Verify this behavior.

### Testing State Update Performance

Measure the time taken for state updates and re-renders. Large state updates or complex computed properties can cause performance issues. Profile state updates to identify bottlenecks and verify that updates complete within acceptable timeframes.

Test with large datasets to ensure state management scales. A store containing thousands of items should still update efficiently. A component rendering a large list should not cause performance issues when state updates.

### Testing Memory Leaks

Verify that subscriptions are cleaned up correctly when components unmount. Create components that subscribe to stores, unmount them, and verify that store subscriptions are removed. Use memory profiling tools to detect leaks.

Test that event listeners, timers, and other resources created by state management are cleaned up. Stores that set up intervals, event listeners, or other resources should clean them up when the store is destroyed or when components unsubscribe.

## Testing MFE State Isolation

In micro-frontend architectures, verify that state changes in one MFE don't leak to another MFE.

### Testing Per-MFE State Isolation

Create multiple MFE instances and verify that they have independent state. Update state in one MFE and verify that other MFEs are not affected. Each MFE should have its own store instances and query clients.

Test that MFEs can have different states simultaneously. One MFE might have a user logged in while another has no user. One MFE might be showing data while another is loading. Verify that these states don't conflict.

### Testing Cross-MFE Event Communication

When MFEs communicate through events, test that events are sent and received correctly. One MFE should be able to dispatch an event that other MFEs receive. Verify that event data is passed correctly and that MFEs update their state based on events.

Test that events don't cause issues when MFEs aren't listening. An MFE should be able to dispatch events even if no other MFEs are subscribed. Events should be optional—MFEs shouldn't break if they don't subscribe to events.

Test that event communication is loosely coupled. MFEs shouldn't need direct references to each other. They should communicate through the event system or URL parameters. Verify this decoupling.
