# Monolith to Microservices

A guide for evolving backend architecture as your application and team grow. This is a journey, not a destination -- each stage is valid and appropriate for certain scales.

## The Journey

```
Monolith → Modular Monolith (Modulith) → Microservices
```

Each transition has specific triggers, trade-offs, and prerequisites.

## Stage 1: Monolith

**What it is:** A single deployable unit containing all backend functionality.

**When it's right:**
- Small team (1-5 developers)
- Single bounded context or tightly coupled domain
- Rapid prototyping and validation phase
- Simple deployment requirements

**Strengths:**
- Simple to develop, test, and deploy
- Easy to debug (single process, no network boundaries)
- No distributed system complexity
- Fast development feedback loop

**Watch for these signals:**
- Deployment conflicts between teams
- Long build/test times
- Difficulty understanding the codebase
- Changes in one area unexpectedly breaking another
- Team size growing beyond what a single codebase supports

## Stage 2: Modular Monolith (Modulith)

**What it is:** A single deployable unit with well-defined internal module boundaries. Modules communicate through internal APIs, not direct class references.

**When to transition from Monolith:**
- Team size reaches 5-10 developers
- Multiple distinct bounded contexts emerge
- Need for independent module development without deployment conflicts
- Codebase complexity makes it hard for any one person to understand the whole

**How to transition:**
1. Identify bounded contexts within the monolith
2. Define module boundaries (package-level isolation)
3. Replace direct class references with internal module APIs
4. Enforce module boundaries with architecture tests (e.g., ArchUnit)
5. Each module owns its own database tables/schemas

**Strengths:**
- Module isolation without distributed system complexity
- Single deployment simplifies operations
- Easier to later extract modules into services if needed
- Enforced boundaries prevent spaghetti architecture

**Watch for these signals:**
- Need for independent scaling of specific modules
- Independent deployment cadence needed per module
- Different technology requirements per module
- Team autonomy limited by shared deployment pipeline

**Related facets:**
- [Backend Architecture](../facets/backend-architecture/options.md) -- Architecture pattern options
- [Data Persistence](../facets/data-persistence/options.md) -- Database per module considerations
- [Testing](../facets/testing/options.md) -- Module boundary testing strategies

## Stage 3: Microservices

**What it is:** Multiple independently deployable services, each owning its own bounded context, data, and deployment lifecycle.

**When to transition from Modulith:**
- Multiple teams need fully independent deployment cycles
- Specific modules need independent scaling
- Different modules have fundamentally different technology requirements
- Organization has the operational maturity to manage distributed systems

**Prerequisites (non-negotiable):**
- Robust CI/CD pipelines → [CI/CD](../facets/ci-cd/options.md)
- Comprehensive observability → [Observability](../facets/observability/options.md)
- Service discovery and API gateway infrastructure
- Distributed tracing and correlation IDs
- Team understanding of distributed system patterns (eventual consistency, saga, etc.)

**How to transition:**
1. Start with the module that has the strongest case for independence
2. Extract one module at a time (strangler fig pattern) → [Refactoring](../facets/refactoring/architecture.md)
3. Define clear API contracts between services → [API Design](../facets/api-design/options.md)
4. Implement event-driven communication where appropriate → [Event-Driven Architecture](../facets/event-driven-architecture/options.md)
5. Establish per-service data ownership

**Strengths:**
- Independent deployment and scaling per service
- Technology diversity where justified
- Team autonomy and ownership
- Fault isolation

**Risks:**
- Distributed system complexity (network failures, eventual consistency)
- Operational overhead (monitoring, debugging, deployment)
- Data consistency challenges across service boundaries
- Risk of creating a "distributed monolith" without proper boundaries

## Anti-Patterns

- **Premature microservices** -- Adopting microservices before the team or product needs them. Start with a monolith or modulith.
- **Distributed monolith** -- Microservices that are tightly coupled and must be deployed together. If you can't deploy one service without deploying others, you don't have microservices.
- **Nano-services** -- Services that are too small to justify the overhead of being independent. A service should own a meaningful bounded context.

## Decision Framework

See [scaling-triggers.md](scaling-triggers.md) for the universal triggers that apply across this journey.
