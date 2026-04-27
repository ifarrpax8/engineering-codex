---
description: Common testing traps — assertion-free tests, shared state, mocking everything, flaky test acceptance
globs: ["**/*.test.ts", "**/*.spec.ts", "**/*Test.kt", "**/*.test.js", "**/*.spec.js"]
alwaysApply: false
type: "auto"
---

# Testing — Gotchas

Quick reference for the most common traps. Full detail: `engineering-codex/facets/testing/gotchas.md`

- **Coverage ≠ quality** — 100% coverage can be achieved with assertion-free tests. Use coverage as a floor indicator (< 60% is a concern), not a target.
- **Mocking everything** — Tests that mock all dependencies verify call order, not behaviour. Use real dependencies (Testcontainers, in-memory impls) where practical.
- **Testing implementation details** — Tests that assert private method calls or internal state break on refactoring. Test through the public API; verify observable behaviour.
- **Shared mutable state between tests** — Shared databases or singletons create order-dependent failures. Each test must create and clean up its own data.
- **Sleep-based waits** — `sleep(2000)` is too long on fast machines, too short on slow CI. Use explicit waits: `waitForSelector`, `waitForResponse`, locator auto-waiting.
- **Ice cream cone (inverted pyramid)** — Mostly E2E tests = slow, flaky, expensive suite. Push testing down: unit for logic, integration for component boundaries, E2E only for critical journeys.
- **Shared test environment** — Tests interfering via shared DB or staging state create unpredictable failures. Use isolated infrastructure (Testcontainers, WireMock) per test run.
- **Not testing error paths** — Happy-path-only suites miss where most bugs hide. Write at least one error-path test per happy-path test.
- **Assertion-free tests** — A test that doesn't throw ≠ a test that passes. Every test must assert something meaningful about result, state, or side effect.
- **Ignoring flaky tests** — Adding `@Retry` to a flaky test hides a real bug and erodes suite trust. Quarantine immediately, fix or delete within a sprint.
- **Over-specifying test data** — Full 20-field objects in every test obscure intent and create maintenance burden. Use factory functions; specify only the fields relevant to the behaviour under test.
