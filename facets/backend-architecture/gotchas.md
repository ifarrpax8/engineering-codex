# Backend Architecture -- Gotchas

Common pitfalls that trap teams when building backend systems. Recognizing these patterns early prevents costly refactoring later.

## Distributed Monolith

A distributed monolith has the complexity of microservices without the benefits. Services must be deployed together, share a database, or have synchronous call chains that create tight coupling.

**Symptoms**:
- Services can't be deployed independently—deploying Service A requires deploying Service B
- Multiple services read/write the same database tables
- Synchronous call chains: Service A calls B calls C calls D
- Changes to one service require changes to others
- Services share code or libraries that create version conflicts

**Test**: Can you deploy one service without deploying others? If no, you have a distributed monolith.

**Why It Happens**: Teams split codebases into services without establishing proper boundaries. Services share databases for "simplicity." Synchronous calls seem easier than async messaging.

**Fix**: Establish proper service boundaries (bounded contexts). Each service owns its data. Use async messaging for inter-service communication. Accept eventual consistency. If services must be deployed together, consider a modulith instead.

**Prevention**: Start with a modulith. Extract to microservices only when services can be truly independent. Use contract testing to verify independence.

## Premature Decomposition

Splitting into microservices before understanding domain boundaries leads to wrong boundaries that are expensive to fix. Services end up tightly coupled despite being separate deployments.

**Symptoms**:
- Frequent changes require modifying multiple services
- Services have circular dependencies (A needs B, B needs A)
- Data must be joined across services for common queries
- Services share too much context (e.g., UserService and OrderService both need full user details)

**Why It Happens**: Teams assume microservices are always better. They split by technical layers (user service, order service) rather than business capabilities. Domain boundaries aren't understood.

**Fix**: Merge tightly coupled services. Re-discover domain boundaries through usage patterns. Extract services only when boundaries are clear and stable.

**Prevention**: Start with a monolith or modulith. Discover boundaries through usage. Extract when boundaries are stable and teams need independence. Use Domain-Driven Design to identify bounded contexts.

## Shared Database Across Services

Two or more services reading/writing the same database tables creates tight coupling. Schema changes require coordinating deployments across teams.

**Symptoms**:
- Service A and Service B both have repositories accessing the same tables
- Schema changes require deploying multiple services
- One service's data access patterns affect another service's performance
- Can't use different database technologies per service

**Why It Happens**: Shared database seems simpler than data duplication or event-driven updates. Teams want ACID transactions across services.

**Fix**: Each service should own its data. Use events or APIs to share data. Accept eventual consistency. Use database-per-service pattern.

**Prevention**: Establish data ownership from the start. Even in a monolith, use separate schemas per module to prepare for extraction.

## Synchronous Inter-Service Calls Creating Coupling

Service A calls Service B which calls Service C. If C is down, A fails. This creates a distributed system with the failure modes of a monolith.

**Symptoms**:
- Service A fails when Service B is unavailable
- Long call chains: A → B → C → D
- Timeouts cascade through the system
- Can't deploy services independently due to version dependencies

**Why It Happens**: Synchronous calls are familiar (like method calls). Async messaging seems complex. Teams want immediate consistency.

**Fix**: Use async messaging for non-time-critical operations. Accept eventual consistency. Use circuit breakers for synchronous calls that are necessary. Design for failure—assume services will be unavailable.

**Prevention**: Prefer events over direct calls. Use message brokers (Kafka, RabbitMQ) for async communication. Reserve synchronous calls for operations that require immediate response.

## N+1 Service Calls

Fetching a list from Service A, then calling Service B for each item creates performance problems and tight coupling.

**Symptoms**:
- API response times increase linearly with list size
- Service B receives many small requests instead of one batch request
- Service A depends on Service B's availability for list operations

**Why It Happens**: Services expose item-level APIs but not batch APIs. Teams don't consider the calling pattern.

**Fix**: 
- Provide batch APIs: `GET /users?ids=1,2,3` instead of calling `/users/1`, `/users/2`, `/users/3`
- Duplicate data: Service A caches data from Service B locally
- Use CQRS: Build read models that combine data from multiple services

**Prevention**: Design APIs with calling patterns in mind. Provide batch endpoints. Consider data duplication for read-heavy scenarios.

## Not Accounting for Network Failures

In a monolith, method calls always succeed or throw exceptions. In microservices, network calls can timeout, return errors, or return stale data. Assuming network calls work like method calls leads to brittle systems.

**Symptoms**:
- Services fail when dependencies are slow (not just down)
- No retry logic for transient failures
- No circuit breakers—one failing service brings down others
- Assumptions about data freshness that don't hold in distributed systems

**Why It Happens**: Teams treat network calls like method calls. They don't account for partial failures, network partitions, or eventual consistency.

**Fix**: 
- Implement retries with exponential backoff for transient failures
- Use circuit breakers to fail fast when services are down
- Design for eventual consistency—don't assume immediate consistency
- Use timeouts and fallbacks

**Prevention**: Assume network calls will fail. Design for failure from the start. Use resilience patterns (retry, circuit breaker, bulkhead). Test failure scenarios.

## "Just One More Endpoint" on a Monolith

Gradual feature creep until the monolith becomes unmanageable. Each addition seems small, but cumulative complexity makes the system hard to change.

**Symptoms**:
- Monolith has grown to hundreds of endpoints
- Features are tightly coupled—changing one affects others
- Deployment conflicts between teams
- Long build times and test execution
- Unclear ownership of code

**Why It Happens**: Adding features to a monolith is easy initially. Teams don't recognize when complexity has accumulated. No boundaries prevent coupling.

**Fix**: Establish module boundaries. Use ArchUnit to enforce boundaries. Consider extracting to modulith or microservices when scaling triggers are reached.

**Prevention**: Set boundaries early, even in monoliths. Use package-by-feature structure. Establish refactoring triggers (team size, deployment conflicts). Regularly assess architecture fitness.

## Anemic Domain Model

Domain objects are just data holders (getters/setters) with all logic in service classes. This loses the benefits of object-oriented design and makes business rules hard to find.

**Symptoms**:
- Domain classes are mostly properties with getters/setters
- Business logic is in service classes, not domain objects
- Domain objects can be in invalid states (e.g., User with null email)
- Business rules are scattered across multiple service methods

**Why It Happens**: JPA entities encourage anemic models. Teams separate data and behavior. Service layer seems like the right place for logic.

**Fix**: Move behavior into domain objects. Use value objects to encapsulate validation. Make domain objects responsible for their own invariants:

```kotlin
// Anemic (bad)
class User {
    var email: String? = null
}

class UserService {
    fun changeEmail(user: User, newEmail: String) {
        if (!isValidEmail(newEmail)) throw InvalidEmailException()
        user.email = newEmail
    }
}

// Rich domain model (good)
class User(
    private var email: Email  // Value object enforces validity
) {
    fun changeEmail(newEmail: Email) {
        require(newEmail.isValid()) { "Invalid email" }
        this.email = newEmail
    }
}
```

**Prevention**: Design domain objects with behavior, not just data. Use value objects for validated data. Keep services thin—they orchestrate, domain objects execute.

## Ignoring Conway's Law

Architecture doesn't match organizational structure. Teams can't work independently because architecture requires coordination.

**Symptoms**:
- Multiple teams modifying the same codebase
- Deployment requires coordination across teams
- Code ownership is unclear
- Architecture decisions don't align with team structure

**Why It Happens**: Architecture is designed without considering team structure. Teams are organized by technical layers rather than business capabilities.

**Fix**: Align architecture with team structure. If teams own features, architecture should enable feature ownership. If teams are organized by capability, services should match capabilities.

**Prevention**: Design architecture with team structure in mind. Use team structure to guide service boundaries. Reorganize teams or architecture to align.

## Over-Engineering

Adding complexity (microservices, event sourcing, CQRS) before it's needed. Premature optimization at the architecture level.

**Symptoms**:
- Microservices for a team of 3 developers
- Event sourcing for simple CRUD operations
- CQRS when read/write patterns are identical
- Complex architecture slows development without clear benefits

**Why It Happens**: Teams assume complex architectures are always better. They want to use "best practices" without considering context.

**Fix**: Simplify. Remove unnecessary complexity. Extract to simpler patterns. Add complexity only when clear benefits emerge.

**Prevention**: Start simple. Add complexity when scaling triggers are reached. Regularly question whether architecture complexity is justified. Measure the cost of complexity (development speed, operational overhead).

## Summary

These gotchas share a common theme: assuming distributed systems work like monoliths, or adding complexity before it's needed. The antidote is to start simple, enforce boundaries, design for failure, and evolve when scaling triggers are reached. Recognize these patterns early and course-correct before they become expensive to fix.
