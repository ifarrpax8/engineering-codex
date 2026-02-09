---
title: Testing
type: facet
last_updated: 2026-02-09
---

# Testing

Unit, integration, e2e, contract, performance, TDD, BDD, test architecture

## TL;DR

- **Default choice**: Test-After for rapid development, evolve to TDD for business logic and BDD for user-facing features—use the right strategy for each scenario
- **Key principle**: Test distribution follows architecture—Pyramid for monoliths (many unit tests), Diamond/Trophy for microservices (focus on integration tests)
- **Watch out for**: Over-testing trivial code (TDD can lead to this), brittle E2E tests (keep them focused on critical user journeys), flaky tests slowing CI/CD (target < 1% flakiness)
- **Start here**: [Options](options.md) — Decision matrix covers TDD, BDD, Test-After, ATDD strategies plus test distribution patterns (Pyramid, Diamond, Trophy)

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [CI/CD](../ci-cd/README.md) -- Testing is integral to continuous integration pipelines; fast test suites enable continuous deployment
- [Developer Experience](../developer-experience/README.md) -- Testing tools and practices directly impact developer productivity and confidence
- [Security](../security/README.md) -- Security testing, vulnerability scanning, and penetration testing are critical testing concerns
- [Performance](../performance/README.md) -- Performance testing, load testing, and benchmarking validate non-functional requirements
- [Backend Architecture](../backend-architecture/README.md) -- Testing strategies differ for microservices vs monoliths; contract testing for service boundaries
- [Frontend Architecture](../frontend-architecture/README.md) -- Component testing, E2E testing, and visual regression testing for frontend codebases
- [API Design](../api-design/README.md) -- API contract testing, schema validation, and integration testing for API boundaries
- [Data Persistence](../data-persistence/README.md) -- Database testing strategies, transaction rollback, test data management
- [State Management](../state-management/README.md) -- Testing state transitions, side effects, and state consistency
- [Error Handling](../error-handling/README.md) -- Testing error paths, exception handling, and failure scenarios
- [Observability](../observability/README.md) -- Test observability, test reporting, and debugging test failures

## Related Experiences

- [Forms and Data Entry](../../experiences/forms-and-data-entry/README.md) -- Form validation testing, input sanitization, multi-step flow testing
- [Tables and Data Grids](../../experiences/tables-and-data-grids/README.md) -- Sorting, filtering, pagination testing; performance testing for large datasets
- [Onboarding](../../experiences/onboarding/README.md) -- User journey testing, progressive disclosure testing, tutorial flow validation
- [Search and Discovery](../../experiences/search-and-discovery/README.md) -- Search result accuracy testing, relevance testing, autocomplete testing
- [Workflows and Tasks](../../experiences/workflows-and-tasks/README.md) -- Multi-step workflow testing, state machine testing, task completion flows
- [Real-time and Collaboration](../../experiences/real-time-and-collaboration/README.md) -- WebSocket testing, race condition testing, concurrent user scenarios
- [Notifications](../../experiences/notifications/README.md) -- Notification delivery testing, timing validation, user preference testing
- [Settings and Preferences](../../experiences/settings-and-preferences/README.md) -- Preference persistence testing, configuration validation, migration testing
