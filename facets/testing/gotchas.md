# Testing -- Gotchas

Common pitfalls and traps that developers encounter when writing and managing tests. These are the things that seem like good practice at first but create problems over time.

## 100% Code Coverage Doesn't Mean Your Tests Are Good

**The trap**: Targeting 100% code coverage as a quality metric, then writing tests that execute every line without actually verifying behavior.

**Why it's a problem**: Coverage measures which lines were executed, not which behaviors were verified. A test that calls a function but has no assertions achieves coverage while proving nothing. Teams optimizing for coverage often write low-value tests that slow down the suite without catching bugs.

**Mitigation**: Use coverage as a baseline indicator (< 60% is a concern), not a target. Complement with mutation testing to verify that tests actually catch defects. Focus on testing behavior and edge cases, not hitting coverage numbers.

## Mocking Everything

**The trap**: Mocking all dependencies to keep tests "fast" and "isolated." Every test has 10+ mock setups that mirror the implementation.

**Why it's a problem**: Tests that mock everything verify that your code calls mocks in the expected order -- not that it actually works. When the implementation changes, the mocks need updating too, but the tests still pass even if the real integration is broken.

**Mitigation**: Use real dependencies where practical (Testcontainers for databases, in-memory implementations for simple interfaces). Reserve mocks for external services, slow I/O, and non-deterministic behavior. If a test has more mock setup than test code, reconsider the approach.

## Testing Implementation Details

**The trap**: Testing that a specific private method was called, that an internal list has a certain size, or that objects were created in a specific order.

**Why it's a problem**: These tests break on refactoring even when behavior is unchanged. Renaming a private method, changing a data structure, or reordering internal logic shouldn't cause test failures. This makes refactoring expensive and discourages it.

**Mitigation**: Test through the public API. Verify observable behavior (return values, state changes, side effects), not internal mechanics. Ask: "If I refactor the internals without changing behavior, should this test break?" If yes, the test is too coupled.

## Shared Mutable State Between Tests

**The trap**: Tests share a database, a singleton, or a static variable. Tests pass when run individually but fail when run together or in a different order.

**Why it's a problem**: Test ordering dependencies create flaky tests that are extremely hard to debug. The failure depends on which tests ran before, which can change with parallelization, filtering, or adding new tests.

**Mitigation**: Each test should create its own data and clean up after itself. Use transactional rollback, database truncation, or fresh containers per test class. Never rely on data created by another test.

## Sleep-Based Waits in E2E Tests

**The trap**: Adding `sleep(2000)` when waiting for a page to load, an animation to complete, or an API call to return.

**Why it's a problem**: Sleep-based waits are either too long (slow test suite) or too short (flaky tests). They don't adapt to actual conditions -- a slow CI server needs more time than a developer's machine.

**Mitigation**: Use explicit waits that poll for a condition: `waitForSelector`, `waitForResponse`, `toBeVisible()`. Playwright's auto-waiting handles most cases. Only use timeouts as a safety net, not as the primary wait strategy.

## The Ice Cream Cone (Inverted Pyramid)

**The trap**: Most tests are E2E or integration tests, few are unit tests. The team reasons that E2E tests "test more" and are therefore more valuable.

**Why it's a problem**: E2E tests are slow, flaky, and expensive to maintain. A suite dominated by E2E tests takes minutes to hours to run, creates long feedback loops, and breaks for unrelated reasons (network, browser updates, CSS changes). Developers stop trusting and running the tests.

**Mitigation**: Follow the test pyramid (or diamond). Push testing down to the lowest level that can verify the behavior. Unit tests for logic, integration tests for component interactions, E2E tests only for critical user journeys.

## Testing Against a Shared Test Environment

**The trap**: Integration tests run against a shared test database or staging environment that other tests, other developers, or CI pipelines are also using.

**Why it's a problem**: Tests interfere with each other. One pipeline's test data corrupts another pipeline's expectations. Tests are flaky because the shared environment's state is unpredictable.

**Mitigation**: Use isolated test infrastructure per test run. Testcontainers spins up fresh databases per test class. WireMock provides isolated HTTP mocks. If you must share infrastructure, use test data namespacing (unique prefixes per test run).

## Not Testing Error Paths

**The trap**: Every test is a happy-path test. The function is called with valid inputs and produces the expected output. No tests for null inputs, boundary conditions, network failures, or permission denials.

**Why it's a problem**: Most production bugs occur on error paths. The happy path usually works because it's what developers manually test during development. Edge cases and failure modes are where bugs hide.

**Mitigation**: For every happy-path test, write at least one error-path test. What happens with null? Empty string? Maximum value? Unauthorized user? Network timeout? Database constraint violation?

## Assertion-Free Tests

**The trap**: A test that calls a function and checks that it doesn't throw an exception, but doesn't verify the result.

```kotlin
@Test
fun `should process order`() {
    orderService.processOrder(testOrder)  // No assertion
}
```

**Why it's a problem**: This test only verifies that the code doesn't crash. It doesn't verify that the order was actually processed correctly. The implementation could return garbage and this test would pass.

**Mitigation**: Every test must assert something meaningful about the result. If the function has side effects, verify the side effects. If it returns a value, verify the value. If it changes state, verify the state.

## Flaky Tests That Get Ignored

**The trap**: A test fails intermittently. The team adds `@RepeatedTest` or `@Retry` and moves on. Over time, more tests become flaky and are handled the same way.

**Why it's a problem**: Flaky tests erode trust in the test suite. Developers stop investigating failures because "it's probably just that flaky test." Real failures hide among the flaky noise. Eventually, the test suite provides no signal.

**Mitigation**: Treat flaky tests as bugs. Quarantine them immediately (move to a separate suite that doesn't block CI). Fix or delete within a sprint. Track flaky test rate as a quality metric. Never retry without investigating the root cause.

## Over-Specifying Test Data

**The trap**: Every test creates a complete domain object with all 20 fields populated, most of which are irrelevant to the behavior being tested.

**Why it's a problem**: When a field is added or its validation changes, every test that creates that object needs updating. It's also hard to see which fields actually matter for the test.

**Mitigation**: Use factory functions or builders that provide sensible defaults. Tests only specify the fields relevant to the behavior being tested. This makes test intent clear and reduces maintenance.

```kotlin
// Instead of specifying everything:
val user = User("id", "email@test.com", "John", "Doe", "active", "admin", ...)

// Specify only what matters:
val user = testUser(role = "admin")  // Factory provides defaults for everything else
```
