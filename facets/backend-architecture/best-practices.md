# Backend Architecture -- Best Practices

Principles and patterns for building maintainable, scalable backend applications. These are language-agnostic where possible, with stack-specific callouts for Kotlin, Spring Boot, and Axon Framework where they materially affect the recommendation.

## Contents

- [Start Simple, Evolve When Needed](#start-simple-evolve-when-needed)
- [Enforce Boundaries Early](#enforce-boundaries-early)
- [Separate Domain Logic from Infrastructure](#separate-domain-logic-from-infrastructure)
- [Package by Feature, Not by Layer](#package-by-feature-not-by-layer)
- [API-First Development](#api-first-development)
- [Idempotent Operations](#idempotent-operations)
- [Consistent Error Handling](#consistent-error-handling)
- [Graceful Degradation](#graceful-degradation)
- [Domain-Driven Design in Microservices](#domain-driven-design-in-microservices)
- [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
- [Aggregate Root Design](#aggregate-root-design)
- [Naming Conventions](#naming-conventions)
- [Event-Driven Patterns in Microservices](#event-driven-patterns-in-microservices)
- [Stack-Specific Callouts](#stack-specific-callouts)

## Start Simple, Evolve When Needed

Begin with a monolith. A well-structured monolith is faster to develop, simpler to deploy, and easier to reason about than a distributed system. The key is structuring the monolith so that extraction is possible when scaling triggers are reached.

The typical evolution path is: Monolith → Modular Monolith (Modulith) → Microservices. Each transition should be driven by concrete pain points (deployment conflicts, scaling bottlenecks, team coordination overhead), not by architecture aspirations. See [evolution/monolith-to-microservices.md](../../evolution/monolith-to-microservices.md).

A well-structured monolith that can be decomposed later is always preferable to a poorly-structured microservice architecture that creates a distributed monolith.

## Enforce Boundaries Early

Even in a monolith, establish clear module boundaries from day one. This makes future extraction possible and keeps the codebase navigable as it grows.

**Package visibility**: make classes package-private by default. Only expose what other modules need through public interfaces. In Kotlin, use `internal` visibility for module-scoped classes.

**ArchUnit enforcement**: write architecture tests that verify boundary rules:

```kotlin
@ArchTest
val moduleBoundaries = slices()
    .matching("com.company.product.(*)..")
    .should().notDependOnEachOther()

@ArchTest
val domainIndependence = noClasses()
    .that().resideInAPackage("..domain..")
    .should().dependOnClassesThat()
    .resideInAnyPackage("..infrastructure..", "..controller..")
```

**Module APIs**: define explicit interfaces between modules. Module A communicates with Module B through B's public API (an interface), not by directly accessing B's internal classes.

**Spring Modulith**: provides module detection, inter-module event publishing, and integration test isolation per module. It formalizes the modulith pattern within Spring Boot.

## Separate Domain Logic from Infrastructure

Domain objects (entities, value objects, aggregates) should contain business logic but have zero dependencies on frameworks, databases, or external services. This keeps the domain testable with fast unit tests and portable across infrastructure changes.

**Domain layer**: pure business logic. No Spring annotations, no JPA annotations, no HTTP concerns.

**Application layer**: orchestrates domain operations. Receives commands, loads domain objects, invokes domain methods, publishes events.

**Infrastructure layer**: implements interfaces defined by the domain. Database repositories, HTTP clients, message publishers, file storage.

The domain defines what it needs (a `UserRepository` interface). Infrastructure provides how (a JPA implementation, a JDBC implementation, or an in-memory implementation for tests).

## Package by Feature, Not by Layer

Group all code for a feature together rather than grouping all controllers, all services, and all repositories separately.

**Package-by-feature** (preferred):
```
com.company.product/
├── billing/
│   ├── BillingController.kt
│   ├── BillingService.kt
│   ├── InvoiceRepository.kt
│   ├── Invoice.kt
│   └── BillingConfig.kt
├── users/
│   ├── UserController.kt
│   ├── UserService.kt
│   ├── UserRepository.kt
│   └── User.kt
```

**Why this matters**: a developer working on billing sees all billing-related code in one place. Adding a new feature means adding a new package, not modifying files scattered across `controller/`, `service/`, and `repository/` packages. Feature packages can use package-private visibility to enforce encapsulation.

## API-First Development

Define API contracts before writing implementation code. Use OpenAPI specifications or TypeSpec to document the API surface, then generate server stubs or validate implementations against the spec.

**Why this matters**: frontend and backend teams can work in parallel. The API contract becomes the single source of truth. Breaking changes are caught before they reach production. Consumer-driven contract tests further validate that consumers and providers agree on the API shape.

## Idempotent Operations

Design operations to be safely retryable. Network failures, message redelivery, and retry logic mean that any operation may be executed more than once.

**Idempotency keys**: clients send a unique key with each request. The server checks if the key has been processed before and returns the cached result instead of re-executing.

**Natural idempotency**: some operations are naturally idempotent (setting a value is idempotent; incrementing is not). Prefer "set to X" over "increment by Y" where possible.

**Database constraints**: use unique constraints to prevent duplicate inserts. An INSERT with ON CONFLICT handles the case where a retry re-sends the same data.

## Consistent Error Handling

Establish a consistent error response format across all services and endpoints. Clients should be able to parse errors uniformly regardless of which service they originated from.

Use domain-specific exceptions that map to appropriate HTTP status codes. Avoid leaking internal implementation details (stack traces, database errors) in error responses. Provide machine-readable error codes alongside human-readable messages.

## Graceful Degradation

Design services to continue functioning (possibly with reduced capability) when dependencies are unavailable.

**Circuit breakers**: stop calling a failing dependency after repeated failures. Return a fallback response or cached data instead of propagating the failure.

**Timeouts**: set explicit timeouts on all external calls. A missing timeout means a single slow dependency can exhaust all threads and bring down the entire service.

**Bulkheads**: isolate connection pools and thread pools per dependency so that a failing dependency doesn't consume resources needed by healthy operations.

## Domain-Driven Design in Microservices

Scope each microservice to a single bounded context. A single microservice should generally represent one domain aggregate (e.g., `/orders`, `/products`, `/users`).

Use techniques like Event-Driven Architecture, Anti-corruption Layers, and CQRS to decouple services across bounded contexts. If another service in another context being down causes your service to fail, revisit your design.

## CQRS (Command Query Responsibility Segregation)

Separate command handling (writes) from query services (reads)—e.g., `OrderCommandHandler` and `OrderQueryService` rather than a single `OrderService`. This avoids 1000+ line transaction script service classes (an anti-pattern known as Anemic Domain Model).

Services should coordinate repositories and infrastructure concerns, not contain all business logic (see hexagonal, onion, and clean architectures).

## Aggregate Root Design

Do NOT create a Service per database table—organize services around aggregates.

Keep business logic in the domain, and application/interface logic decoupled from storage. Repositories focus on aggregate roots as access points, not individual entities. Child entities (e.g., `LineItem`) are owned by their aggregate root (e.g., `Quote`) and do not have their own repository. Use the aggregate root as the transactional boundary where business invariants are enforced.

## Naming Conventions

Name DTOs with intent: Command, Event, View—not generic `*DTO`. `AddLineItem` conveys more meaning than `LineItemDTO`.

Name services with "verb-like" suffixes: handler, adapter, manager—the name should describe what it does. Avoid generic words in service names: api, service, pax8.

## Event-Driven Patterns in Microservices

Emit domain events when commands are handled and aggregate state changes. Use events to: update view/read models, trigger business processes in other aggregates, update caches, emit data to message brokers.

This creates powerful decoupling of domains from each other and from infrastructure.

> **Stack Callout — Pax8**: Pax8 microservices are written in Kotlin using Spring Boot. The [Donut Manager](https://github.com/pax8/donut-manager) repository serves as the reference architecture for all Spring Boot microservices—use it as a learning/guiding tool, not a cargo-cult template. Pax8 uses Spring Data (JPA, Relational, or MongoDB) for repositories and recommends Axon Framework for CQRS/Event Sourcing. See the [Microservices Best Practices](https://pax8.atlassian.net/wiki/spaces/DD/pages/2036761074) for the canonical anatomy of a microservice.

## Stack-Specific Callouts

### Kotlin

- Use **sealed classes** for commands, events, and domain state to get exhaustive `when` expressions. The compiler ensures all cases are handled.
- Use **data classes** for DTOs and value objects. They provide `equals`, `hashCode`, `copy`, and destructuring automatically.
- Use **extension functions** to add behavior to domain types without modifying their class definition. Keep extensions close to the type they extend.
- Use **coroutines** for async operations (non-blocking I/O, parallel calls). Spring WebFlux with coroutines or Spring MVC with virtual threads (Java 21+).
- Prefer **`val`** over `var`. Immutable properties reduce bugs and make code easier to reason about in concurrent contexts.
- Use **`require`** and **`check`** for precondition and state validation instead of manual if/throw blocks.

### Spring Boot

- Use **constructor injection** exclusively. Remove `@Autowired` annotations. Kotlin's primary constructors make this natural.
- Use **`@ConfigurationProperties`** for externalized configuration instead of scattered `@Value` annotations. This provides type-safe, validated configuration with IDE support.
- Use **profile-based configuration** (`application-{profile}.yml`) for environment-specific values. Keep the default profile suitable for local development.
- Use **Spring Modulith** for modular monolith structure. It provides module boundary detection, inter-module event publishing, and module-scoped integration tests.
- Use **`@Transactional(readOnly = true)`** for query methods. This gives Hibernate optimization hints and can route to read replicas.

### Axon Framework

- Use **aggregate annotations** (`@Aggregate`, `@CommandHandler`, `@EventSourcingHandler`) for event-sourced domain objects.
- Use **saga pattern** (`@Saga`, `@SagaEventHandler`) for long-running processes that coordinate across multiple aggregates or services.
- Configure **dead letter queue** handling for failed event processing. Events that fail projection updates should be retried or routed to a DLQ for manual investigation.
- Use **Axon's aggregate test fixture** (`AggregateTestFixture`) for given-when-then style aggregate testing. These tests run without Spring context and are very fast.
- Configure **snapshotting** for aggregates with long event streams. Snapshot every N events (e.g., 100) to keep aggregate loading time constant.
