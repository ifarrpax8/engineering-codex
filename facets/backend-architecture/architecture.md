# Backend Architecture -- Architecture

Backend architecture encompasses both deployment architecture (how code is packaged and deployed) and internal architecture (how code is organized within each deployment unit). These decisions are independent but complementary.

## Contents

- [Deployment Architectures](#deployment-architectures)
- [Internal Architecture Patterns](#internal-architecture-patterns)
- [Domain-Driven Design Tactical Patterns](#domain-driven-design-tactical-patterns)
- [Architecture Evolution](#architecture-evolution)

## Deployment Architectures

### Monolith

A monolith is a single deployment unit containing all application code in one codebase. All features share the same database, runtime, and deployment pipeline. This simplicity makes monoliths ideal for small teams and early-stage products.

**When It's Right**: Small teams (typically 2-5 developers), early product development, tight coupling between features, simple operational requirements, rapid iteration needs.

**Package Structure**: Two common approaches exist:

**Package-by-Layer** (traditional):
```
com.company.product/
├── controller/
│   ├── UserController.kt
│   └── OrderController.kt
├── service/
│   ├── UserService.kt
│   └── OrderService.kt
├── repository/
│   ├── UserRepository.kt
│   └── OrderRepository.kt
└── domain/
    ├── User.kt
    └── Order.kt
```

**Package-by-Feature** (preferred):
```
com.company.product/
├── user/
│   ├── UserController.kt
│   ├── UserService.kt
│   ├── UserRepository.kt
│   └── User.kt
└── order/
    ├── OrderController.kt
    ├── OrderService.kt
    ├── OrderRepository.kt
    └── Order.kt
```

Package-by-feature groups related code together, making features easier to understand and extract later. It also naturally enforces some boundaries—code in the `user` package shouldn't directly reference `order` package internals.

**Shared Database**: All features share the same database schema. This enables ACID transactions across features but creates coupling. Schema changes require coordination, and data access patterns can't be optimized per feature.

### Modular Monolith (Modulith)

A modular monolith maintains a single deployment unit but enforces strict module boundaries. Modules communicate through well-defined internal APIs rather than direct class references. This provides architectural benefits of microservices without operational complexity.

**Module Boundaries**: Each module exposes a public API (interfaces or public classes) while keeping implementation details package-private. Modules can't directly access each other's internals, forcing explicit contracts.

**Package Structure**:
```
com.company.product/
├── user/
│   ├── api/
│   │   └── UserService.kt          // Public API
│   ├── internal/
│   │   ├── UserServiceImpl.kt      // Implementation (package-private)
│   │   ├── UserRepository.kt
│   │   └── User.kt
│   └── UserModule.kt                // Module configuration
├── order/
│   ├── api/
│   │   └── OrderService.kt
│   ├── internal/
│   │   ├── OrderServiceImpl.kt
│   │   ├── OrderRepository.kt
│   │   └── Order.kt
│   └── OrderModule.kt
└── application/
    └── ProductApplication.kt        // Spring Boot application
```

**Boundary Enforcement**: Use ArchUnit to enforce module boundaries:

```kotlin
@ArchTest
val modulesShouldNotAccessOtherModulesInternals = 
    noClasses()
        .that().resideInAPackage("..user.internal..")
        .should().accessClassesThat()
        .resideInAPackage("..order.internal..")
```

**Spring Modulith**: Spring Modulith provides runtime support for modular monoliths, including module events, application module tests, and documentation generation. It enforces boundaries at runtime and provides tooling for module interaction analysis.

**Database Schema**: Each module should own its database schema (separate schemas or tables with clear prefixes). This enables future extraction to microservices without data migration.

**When to Use**: Teams of 5-15 developers, need for team autonomy without operational complexity, preparing for future microservices extraction, want to avoid distributed system complexity.

### Microservices

Microservices decompose applications into independently deployable services, each owning a bounded context and its data. Services communicate through well-defined APIs (REST, gRPC, or messaging) and maintain independent databases.

**Service Boundaries**: Each service represents a bounded context from Domain-Driven Design. Services own their data and expose operations through APIs. Changes to one service's database don't affect others.

**Service Discovery**: Services need to find each other. Options include:
- Service registry (Eureka, Consul)
- Kubernetes service discovery
- API Gateway with routing rules
- DNS-based discovery

**Independent Databases**: Each service has its own database (or database schema). This enables independent schema evolution and technology choices but requires careful handling of distributed transactions and data consistency.

**API Contracts**: Services communicate through versioned APIs. Breaking changes require coordination or versioning strategies. Contract testing (Pact, Spring Cloud Contract) ensures compatibility.

**Prerequisites**: Microservices require mature CI/CD pipelines, comprehensive observability (distributed tracing, metrics, logging), team experience with distributed systems, and platform teams to provide shared infrastructure.

**When to Use**: Large teams (15+ developers), need for independent scaling, different technology requirements per domain, mature DevOps practices, clear domain boundaries.

## Internal Architecture Patterns

These patterns apply within each service or module, regardless of deployment architecture.

### Layered Architecture

Layered architecture organizes code into horizontal layers: presentation, service/application, domain, and infrastructure. Each layer depends only on layers below it.

**Layer Responsibilities**:
- **Presentation**: HTTP controllers, request/response DTOs, input validation
- **Service/Application**: Use case orchestration, transaction boundaries, application-level validation
- **Domain**: Business logic, domain models, domain services
- **Infrastructure**: Database access, external service clients, messaging

**Package Structure** (Kotlin/Spring Boot):
```
com.company.product.user/
├── presentation/
│   ├── UserController.kt
│   └── dto/
│       ├── CreateUserRequest.kt
│       └── UserResponse.kt
├── service/
│   └── UserService.kt
├── domain/
│   ├── User.kt
│   ├── UserRepository.kt              // Interface
│   └── Email.kt                        // Value object
└── infrastructure/
    ├── JpaUserRepository.kt            // Implementation
    └── UserEntity.kt                   // JPA entity
```

**Strengths**: Simple, well-understood, easy to onboard new developers, works well for CRUD applications.

**Weaknesses**: Risk of anemic domain models (logic in service layer instead of domain), can lead to "god services" that orchestrate everything, layer boundaries can become porous.

**When to Use**: Simple CRUD applications, teams new to domain modeling, straightforward business logic.

### Hexagonal Architecture (Ports & Adapters)

Hexagonal architecture isolates the domain core from infrastructure concerns. The domain defines ports (interfaces) that infrastructure implements as adapters. This keeps domain logic pure and testable without infrastructure.

**Core Concepts**:
- **Domain Core**: Pure business logic, no framework dependencies
- **Ports**: Interfaces defined by the domain (inbound: use cases, outbound: repositories, external services)
- **Adapters**: Infrastructure implementations (inbound: controllers, outbound: JPA repositories, HTTP clients)

**Package Structure** (Kotlin/Spring Boot):
```
com.company.product.user/
├── domain/
│   ├── model/
│   │   ├── User.kt                    // Aggregate root
│   │   └── Email.kt                   // Value object
│   ├── port/
│   │   ├── inbound/
│   │   │   └── CreateUserUseCase.kt  // Inbound port (use case)
│   │   └── outbound/
│   │       ├── UserRepository.kt     // Outbound port
│   │       └── EmailService.kt        // Outbound port
│   └── service/
│       └── UserDomainService.kt       // Domain service
├── application/
│   └── UserService.kt                 // Use case implementation
└── adapter/
    ├── inbound/
    │   └── web/
    │       └── UserController.kt      // Inbound adapter
    └── outbound/
        ├── persistence/
        │   └── JpaUserRepository.kt    // Outbound adapter
        └── messaging/
            └── KafkaUserEventPublisher.kt
```

**Dependency Direction**: Domain has no dependencies on Spring, JPA, or any framework. Adapters depend on domain ports. Application layer orchestrates domain logic through ports.

**Testing**: Domain logic can be tested without Spring or database. Adapters can be tested in isolation with mocks. Integration tests verify adapter implementations.

**When to Use**: Complex domain logic, need for framework independence, multiple infrastructure implementations (different databases, messaging systems), long-term maintainability focus.

### CQRS (Command Query Responsibility Segregation)

CQRS separates command (write) and query (read) models. Commands modify state through aggregates. Queries read from optimized read models (projections). This enables independent optimization of read and write paths.

**Command Side**: Commands are handled by aggregates that enforce business rules and emit domain events. Axon Framework provides `@Aggregate`, `@CommandHandler`, and `@EventSourcingHandler` annotations.

**Query Side**: Read models are built from events (event sourcing) or updated synchronously (traditional CQRS). Projections optimize for specific query patterns.

**When to Use**: Different read/write patterns (many reads, few writes, or vice versa), complex read queries that would complicate write model, need for independent scaling of read/write, event sourcing adoption.

**Without Event Sourcing**: CQRS can be used with traditional databases. Write model updates database directly. Read model is updated synchronously or asynchronously. Simpler but loses event history.

**With Event Sourcing**: Commands produce events stored in event store. Read models built from events. Provides complete audit trail and time travel. Axon Framework provides event store (Axon Server) and projection building.

**Axon Framework Example**:
```kotlin
@Aggregate
class UserAggregate {
    @AggregateIdentifier
    private var userId: UserId? = null
    
    @CommandHandler
    fun handle(command: CreateUserCommand) {
        // Validate and emit event
        AggregateLifecycle.apply(UserCreatedEvent(command.userId, command.email))
    }
    
    @EventSourcingHandler
    fun on(event: UserCreatedEvent) {
        this.userId = event.userId
        // Rebuild state from event
    }
}
```

## Domain-Driven Design Tactical Patterns

These patterns help model complex domains effectively:

**Aggregates**: Clusters of entities and value objects with a single aggregate root that enforces invariants. Aggregates are consistency boundaries—transactions should not span aggregates.

**Entities**: Objects with identity (e.g., User with userId). Two entities are equal if their IDs match, even if other attributes differ.

**Value Objects**: Immutable objects defined by their attributes (e.g., Email, Money). Two value objects are equal if all attributes match.

**Domain Events**: Events that represent something that happened in the domain. Other aggregates or bounded contexts react to events.

**Repositories**: Abstractions for aggregate persistence. Domain defines repository interfaces (ports), infrastructure provides implementations (adapters).

**Domain Services**: Operations that don't naturally belong to a single aggregate. Stateless services that operate on domain objects.

These patterns work together: aggregates contain entities and value objects, emit domain events, and are persisted through repositories. Domain services handle cross-aggregate operations.

## Architecture Evolution

Start with a monolith or modulith. Enforce boundaries early (package structure, ArchUnit rules, module APIs). Extract to microservices when scaling triggers are reached: team size, deployment conflicts, independent scaling needs, or different technology requirements.

The key is recognizing when current architecture impedes progress and having a clear evolution path. Moduliths provide an excellent stepping stone, maintaining operational simplicity while preparing for future extraction.
