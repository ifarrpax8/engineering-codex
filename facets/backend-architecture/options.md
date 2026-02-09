# Backend Architecture -- Options

Decision matrix for choosing backend architecture patterns based on team size, domain complexity, and operational maturity.

## Contents

- [Deployment Architecture Options](#deployment-architecture-options)
- [Internal Architecture Options](#internal-architecture-options)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies with Other Facets](#synergies-with-other-facets)
- [Evolution Triggers](#evolution-triggers)
- [Decision Framework](#decision-framework)

## Deployment Architecture Options

### Monolith

**Description**: Single deployment unit containing all application code in one codebase. All features share the same database, runtime, and deployment pipeline.

**Strengths**:
- Simple deployment—one artifact, one database, one pipeline
- Fast feature development for small teams—no coordination overhead
- ACID transactions across all features
- Easy debugging—all code in one process
- Low operational overhead—no service discovery, distributed tracing, or API gateways needed

**Weaknesses**:
- Deployment conflicts as teams grow—multiple teams can't deploy independently
- Scaling is all-or-nothing—can't scale individual features
- Technology lock-in—all features use the same stack
- Blast radius is entire application—bugs affect everything
- Codebase grows large, making navigation and ownership unclear

**Best For**:
- Small teams (2-5 developers)
- Early-stage products discovering domain
- Simple domains with tight coupling between features
- Rapid iteration and market validation phase
- Teams without mature DevOps practices

**Avoid When**:
- Team size exceeds 5-8 developers
- Frequent deployment conflicts between teams
- Need to scale specific features independently
- Different features require different technologies
- Clear domain boundaries have emerged

### Modular Monolith (Modulith)

**Description**: Single deployment unit with enforced internal module boundaries. Modules communicate through well-defined APIs rather than direct class references. Provides architectural benefits of microservices without operational complexity.

**Strengths**:
- Single deployment maintains operational simplicity
- Module boundaries prevent accidental coupling
- Enables parallel development across modules
- Easier to extract modules to microservices later
- Clear module ownership supports team autonomy
- Lower operational overhead than microservices

**Weaknesses**:
- Still requires deployment coordination (single artifact)
- Scaling is still all-or-nothing
- Module boundaries add some complexity vs pure monolith
- Requires discipline to maintain boundaries
- Less isolation than microservices (shared runtime)

**Best For**:
- Teams of 5-15 developers
- Need for team autonomy without operational complexity
- Preparing for future microservices extraction
- Want boundaries without distributed system complexity
- Domain boundaries are becoming clear but not yet stable

**Avoid When**:
- Team size exceeds 15 developers (consider microservices)
- Need for independent scaling of modules
- Different modules require different technologies
- Operational complexity is acceptable (use microservices)

### Microservices

**Description**: Independently deployable services, each owning a bounded context and its data. Services communicate through well-defined APIs (REST, gRPC, messaging) and maintain independent databases.

**Strengths**:
- Independent deployment enables team autonomy
- Isolated failures—bugs don't affect other services
- Independent scaling of services based on load
- Technology diversity—each service can use different stack
- Clear service ownership aligns with team structure
- Enables large teams to work in parallel

**Weaknesses**:
- High operational complexity—service discovery, distributed tracing, API gateways
- Network failures introduce new failure modes
- Eventual consistency challenges—no ACID transactions across services
- Requires mature DevOps practices and platform teams
- Distributed debugging is complex
- Upfront investment in infrastructure and tooling

**Best For**:
- Large teams (15+ developers)
- Clear, stable domain boundaries
- Need for independent scaling of services
- Different services require different technologies
- Mature DevOps practices and platform teams
- Willing to accept operational complexity for team autonomy

**Avoid When**:
- Small teams (< 5 developers)
- Domain boundaries are unclear or changing
- Lack of DevOps maturity
- Can't afford platform team overhead
- Tight coupling between features (use modulith or monolith)

## Internal Architecture Options

These patterns apply within each service or module, regardless of deployment architecture.

### Layered Architecture

**Description**: Horizontal layers (presentation, service/application, domain, infrastructure). Each layer depends only on layers below it.

**Strengths**:
- Simple and well-understood pattern
- Easy to onboard new developers
- Clear separation of concerns
- Works well for CRUD applications
- Natural fit for Spring Boot structure

**Weaknesses**:
- Risk of anemic domain models (logic in service layer)
- Can lead to "god services" that orchestrate everything
- Layer boundaries can become porous over time
- Doesn't enforce domain logic encapsulation
- Can encourage procedural rather than object-oriented design

**When to Use**:
- Simple CRUD applications
- Straightforward business logic
- Teams new to domain modeling
- Rapid prototyping
- Applications where domain complexity is low

### Hexagonal Architecture (Ports & Adapters)

**Description**: Domain core with ports (interfaces) and adapters (implementations). Keeps domain logic pure and testable without infrastructure dependencies.

**Strengths**:
- Domain logic is framework-independent
- Highly testable—domain can be tested without Spring or database
- Enables multiple infrastructure implementations
- Clear dependency direction (domain defines interfaces)
- Long-term maintainability focus
- Supports complex domain logic effectively

**Weaknesses**:
- More complex than layered architecture
- Requires discipline to maintain boundaries
- More boilerplate (interfaces, adapters)
- Steeper learning curve
- Can be overkill for simple CRUD

**When to Use**:
- Complex domain logic requiring careful modeling
- Need for framework independence
- Multiple infrastructure implementations (different databases, messaging)
- Long-term maintainability is priority
- Domain logic is core business value

### CQRS

**Description**: Separate command (write) and query (read) models. Commands modify state through aggregates. Queries read from optimized read models.

**Strengths**:
- Independent optimization of read/write paths
- Enables complex read queries without complicating write model
- Independent scaling of read/write
- Natural fit for event sourcing
- Supports different data models for reads vs writes

**Weaknesses**:
- Increased complexity—two models to maintain
- Eventual consistency between read/write models
- Requires event handling infrastructure
- Can be overkill when read/write patterns are similar
- Learning curve for teams new to CQRS

**When to Use**:
- Read and write patterns differ significantly
- Complex read queries that would complicate write model
- Need for independent scaling of read/write
- Using event sourcing (CQRS becomes natural)
- High read-to-write ratio or vice versa

## Evaluation Criteria

| Criteria | Weight | Monolith | Modulith | Microservices |
|----------|--------|----------|----------|---------------|
| **Team Independence** | High | Low—shared codebase requires coordination | Medium—module ownership with deployment coordination | High—independent services enable autonomy |
| **Operational Complexity** | High | Low—single deployment, one database | Low-Medium—single deployment with module boundaries | High—service discovery, tracing, multiple databases |
| **Developer Experience** | Medium | High—simple, familiar patterns | Medium-High—some complexity from boundaries | Medium—distributed debugging is harder |
| **Scalability** | Medium | Low—scale entire application | Low—scale entire application | High—scale services independently |
| **Maintainability** | High | Low-Medium—becomes hard as codebase grows | Medium-High—boundaries help but single codebase | Medium-High—clear ownership but distributed complexity |
| **Time to Market** | High | High—fast initial development | Medium-High—some overhead from boundaries | Low-Medium—upfront investment required |
| **Technology Flexibility** | Low | Low—single technology stack | Low—single technology stack | High—different stacks per service |
| **Failure Isolation** | Medium | Low—failures affect entire application | Low-Medium—module boundaries help but shared runtime | High—failures isolated to single service |

**Scoring**: For each criterion, rate each option: Low (1), Medium (2), High (3). Multiply by weight, sum scores. Higher is better for positive criteria (team independence, scalability), lower is better for negative criteria (operational complexity).

## Recommendation Guidance

### By Team Size

**< 5 Developers**: Monolith. Fast development, simple operations, no coordination overhead. Focus on product-market fit, not architecture.

**5-15 Developers**: Modulith. Enforce module boundaries to enable parallel work while maintaining deployment simplicity. Prepare for future extraction.

**15+ Developers**: Microservices. Team autonomy requires service independence. Ensure DevOps maturity and platform team support.

### By Domain Complexity

**Simple CRUD**: Layered architecture. Straightforward business logic doesn't need complex patterns.

**Complex Domain**: Hexagonal architecture. Rich domain models require careful separation from infrastructure.

**Different Read/Write Patterns**: CQRS. When reads and writes have different requirements, separate models enable optimization.

### By Operational Maturity

**Early Stage**: Monolith. Simple operations enable focus on product development.

**Growing**: Modulith. Add boundaries without operational complexity.

**Mature**: Microservices. Platform teams and DevOps practices enable independent services.

## Synergies with Other Facets

### Frontend Architecture

**MFE (Micro Frontends)**: Microservices align well—teams own full stack (frontend + backend service). Enables true team autonomy.

**SPA (Single Page Application)**: Monolith or modulith is simpler—single backend API. Microservices require API gateway or BFF (Backend for Frontend) pattern.

### Data Persistence

**Event Sourcing**: CQRS becomes strongly preferred. Event sourcing naturally separates command (events) and query (projections) models.

**Traditional Database**: All internal architectures work. Layered is simplest, Hexagonal provides better separation, CQRS adds complexity unless needed.

### API Design

**REST**: All three deployment patterns work well. REST APIs are stateless and work across service boundaries.

**gRPC**: Microservices benefit most—gRPC performance advantages matter in inter-service communication. Less beneficial in monoliths.

**GraphQL**: Works with all patterns. BFF pattern common with microservices to aggregate data from multiple services.

### Event-Driven Architecture

**Event Sourcing**: Strongly favors CQRS and microservices. Event sourcing provides natural service boundaries and CQRS separation.

**Event Streaming**: Microservices benefit from async communication. Moduliths can use module events. Monoliths can use in-process events.

## Evolution Triggers

Move from monolith to modulith when:
- Team size reaches 5-8 developers
- Codebase is becoming hard to navigate
- Want to prepare for future extraction
- Need clearer module ownership

Move from modulith to microservices when:
- Team size exceeds 15 developers
- Deployment conflicts occur frequently
- Need for independent scaling of modules
- Different modules require different technologies
- Domain boundaries are stable and clear

Move from layered to hexagonal when:
- Domain logic is becoming complex
- Need for framework independence
- Multiple infrastructure implementations required
- Long-term maintainability is priority

Move from traditional to CQRS when:
- Read and write patterns differ significantly
- Complex read queries complicate write model
- Need for independent read/write scaling
- Adopting event sourcing

## Decision Framework

1. **Assess Team Size**: < 5 → Monolith, 5-15 → Modulith, 15+ → Microservices
2. **Evaluate Domain Complexity**: Simple → Layered, Complex → Hexagonal
3. **Consider Read/Write Patterns**: Similar → Traditional, Different → CQRS
4. **Check Operational Maturity**: Early → Simpler patterns, Mature → Complex patterns
5. **Review Synergies**: Align with frontend, data persistence, and API design choices
6. **Plan Evolution**: Start simple, evolve when triggers are reached

The goal is not perfect architecture from day one, but architecture that supports current needs and enables future growth. Start with the simplest pattern that meets current requirements, enforce boundaries early, and evolve when scaling triggers are reached.
