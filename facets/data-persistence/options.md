---
title: Data Persistence - Options
type: perspective
facet: data-persistence
recommendation_type: decision-matrix
last_updated: 2026-02-09
---

# Data Persistence - Options

This decision matrix guides data persistence technology choices based on application requirements, constraints, and trade-offs.

## Contents

- [Primary Data Store Options](#primary-data-store-options)
  - [Relational Database (PostgreSQL)](#1-relational-database-postgresql)
  - [Document Store (MongoDB)](#2-document-store-mongodb)
  - [Event Sourcing (Axon Server)](#3-event-sourcing-axon-server)
- [Data Access Pattern Options](#data-access-pattern-options)
  - [ORM (Spring Data JPA / Hibernate)](#1-orm-spring-data-jpa--hibernate)
  - [Query Builder (JOOQ / Exposed)](#2-query-builder-jooq--exposed)
  - [Raw SQL (Spring JDBC / JdbcTemplate)](#3-raw-sql-spring-jdbc--jdbctemplate)
- [Caching Options](#caching-options)
  - [Cache-Aside with Redis](#1-cache-aside-with-redis)
  - [Write-Through Cache](#2-write-through-cache)
  - [No Cache (Database Only)](#3-no-cache-database-only)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)

## Primary Data Store Options

### 1. Relational Database (PostgreSQL)

**Description**: ACID-compliant relational database with strong consistency, SQL queries, and rich data types including JSONB for document-like flexibility.

**Strengths**:
- ACID transactions ensure data integrity and consistency
- SQL provides powerful query capabilities with joins, aggregations, and complex filters
- Foreign keys and constraints enforce referential integrity at the database level
- Mature ecosystem with extensive tooling, monitoring, and operational knowledge
- JSONB support provides document-like flexibility within a relational structure
- Excellent performance for structured data with proper indexing
- Strong consistency model ensures immediate visibility of writes
- Rich data types: arrays, JSONB, full-text search, geospatial data

**Weaknesses**:
- Schema changes require migrations, which can be complex for zero-downtime deployments
- Horizontal scaling is more limited than NoSQL alternatives (though read replicas help)
- Complex queries can become slow without proper indexing and query optimization
- Normalized schemas may require joins that impact read performance
- Connection pooling and resource management require careful configuration
- Not ideal for extremely high write throughput scenarios (though sufficient for most applications)

**Best For**:
- Applications requiring ACID transactions and strong consistency
- Structured data with well-defined relationships
- Complex queries with joins and aggregations
- Applications where data integrity is critical (financial systems, user accounts)
- Teams familiar with SQL and relational modeling
- Applications that benefit from PostgreSQL's advanced features (JSONB, full-text search, geospatial)

**Avoid When**:
- Schema flexibility is a genuine requirement that JSONB cannot satisfy
- Horizontal scaling beyond PostgreSQL's capabilities is needed
- Data models are inherently non-relational (graphs, time-series with specific requirements)
- Write throughput exceeds PostgreSQL's capabilities (rare, but possible at extreme scale)

### 2. Document Store (MongoDB)

**Description**: Schema-flexible document database storing JSON-like documents with horizontal scaling through sharding.

**Strengths**:
- Schema flexibility: documents can have varying structures without migrations
- Horizontal scaling through automatic sharding handles very large datasets
- Nested documents reduce need for joins in some scenarios
- Developer-friendly: JSON documents map naturally to application objects
- Good performance for document-based access patterns
- Flexible querying with rich operators for nested data

**Weaknesses**:
- No ACID transactions across documents (though MongoDB 4.0+ supports multi-document transactions with limitations)
- Complex relational queries are difficult or impossible
- No foreign key constraints: data integrity must be enforced in application code
- Schema flexibility can lead to data quality issues if not managed carefully
- Operational complexity: sharding, replica sets, and configuration require expertise
- Query performance depends heavily on proper indexing, which is less obvious than in relational databases
- Eventual consistency in sharded deployments can surprise developers

**Best For**:
- Content management systems with varying document structures
- User-generated content with evolving schemas
- Applications where schema flexibility is more valuable than relational integrity
- Very large datasets requiring horizontal scaling beyond PostgreSQL's capabilities
- Applications with document-centric access patterns (load entire document, save entire document)

**Avoid When**:
- ACID transactions across multiple documents are required
- Complex relational queries are needed
- Data integrity through foreign keys is important
- Schema flexibility isn't actually needed (PostgreSQL JSONB may suffice)
- Team lacks MongoDB operational expertise

### 3. Event Sourcing (Axon Server)

**Description**: Append-only event log storing domain events instead of current state. Current state is derived by replaying events.

**Strengths**:
- Complete audit trail: every change is recorded as an immutable event
- Temporal queries: can query state at any point in time by replaying events
- Natural fit for event-driven architectures and CQRS patterns
- Event replay enables rebuilding state, debugging, and auditing
- Decouples write model from read models: read models can be optimized independently
- Supports complex business logic with event versioning and upcasting
- Excellent for domains requiring full history (finance, billing, compliance)

**Weaknesses**:
- Increased complexity: requires event store, projections, and event handlers
- Storage overhead: storing all events consumes more storage than current state
- Performance requires snapshots: long event streams need snapshot optimization
- Learning curve: team must understand event sourcing patterns and Axon Framework
- Eventual consistency: read models lag behind write model
- Debugging can be more complex: must reason about event sequences
- Not suitable for all domains: adds complexity that may not be justified

**Best For**:
- Domains where audit trail is essential (finance, billing, compliance)
- Applications requiring temporal queries (what was the state at time X?)
- Event-driven architectures with CQRS
- Complex business logic where event history aids understanding
- Domains where event replay is valuable (debugging, analytics, reporting)

**Avoid When**:
- Simple CRUD applications without audit requirements
- Team lacks event sourcing expertise
- Storage overhead is a concern and audit trail isn't needed
- Read performance is critical and eventual consistency is unacceptable
- Application doesn't benefit from event-driven patterns

## Data Access Pattern Options

### 1. ORM (Spring Data JPA / Hibernate)

**Description**: Object-relational mapping framework that maps Java objects to database tables, providing type-safe queries and automatic relationship management.

**Strengths**:
- Type-safe queries reduce SQL injection risk
- Automatic relationship management (lazy/eager loading)
- Repository pattern provides clean abstraction
- Pagination and sorting built-in
- Excellent for CRUD operations and simple queries
- Reduces boilerplate code compared to raw SQL
- Good developer experience for common operations

**Weaknesses**:
- Complex queries can be awkward or inefficient
- N+1 query problems require careful attention
- Lazy loading can cause `LazyInitializationException` if not managed properly
- Less control over generated SQL compared to raw SQL
- Performance optimization may require understanding generated SQL
- Learning curve for advanced features (specifications, projections, entity graphs)

**When to Use**:
- Standard CRUD operations
- Applications with straightforward query patterns
- Teams familiar with JPA/Hibernate
- When type safety and relationship management are valuable
- Most Spring Boot applications (default choice)

### 2. Query Builder (JOOQ / Exposed)

**Description**: Type-safe SQL construction with code generation from database schema, providing compile-time query validation.

**Strengths**:
- Type-safe queries: column name typos cause compilation errors
- Code generation ensures queries match current schema
- Full control over SQL generation
- Excellent for complex queries where JPA is awkward
- Database-specific features are easily accessible
- Good performance: generates efficient SQL
- JOOQ supports multiple databases; Exposed is Kotlin-focused

**Weaknesses**:
- Code generation adds build step complexity
- More verbose than JPA for simple queries
- Requires database schema to be defined first (for code generation)
- Less abstraction: closer to SQL, so database knowledge required
- Smaller ecosystem compared to JPA

**When to Use**:
- Complex queries where JPA query generation is inefficient
- Need for database-specific features
- Type safety is critical
- Performance-critical query paths
- Kotlin projects (Exposed) or Java projects needing more SQL control (JOOQ)

### 3. Raw SQL (Spring JDBC / JdbcTemplate)

**Description**: Direct SQL execution with minimal abstraction, providing full control over queries and results.

**Strengths**:
- Full control over SQL: no ORM translation layer
- Maximum performance: no overhead from ORM
- Simple for developers comfortable with SQL
- Easy to optimize: write exactly the SQL you need
- No learning curve if team knows SQL

**Weaknesses**:
- No compile-time query validation
- Manual result set mapping (error-prone)
- SQL injection risk if not using parameter binding
- More boilerplate code for common operations
- No automatic relationship management
- Database-specific SQL reduces portability

**When to Use**:
- Performance-critical queries where ORM overhead matters
- Complex queries that are difficult in JPA
- Reporting or analytics queries
- When full SQL control is required
- Small, simple applications where ORM complexity isn't justified

## Caching Options

### 1. Cache-Aside with Redis

**Description**: Application manages cache: checks cache first, loads from database on miss, writes to cache after load. Writes go directly to database with cache invalidation.

**Strengths**:
- Simple pattern: easy to understand and implement
- Flexible: application controls what to cache and when to invalidate
- Works well for read-heavy workloads
- Redis provides rich data structures and TTL support
- Can cache complex objects and computed values

**Weaknesses**:
- Cache invalidation logic can be complex
- Possible stale data if invalidation fails
- Requires application code to manage cache
- Cache misses add latency (check cache, then database)

**When to Use**:
- Read-heavy workloads with frequently accessed data
- Data that changes infrequently
- When cache invalidation logic is manageable
- Most common caching pattern (default choice)

### 2. Write-Through Cache

**Description**: Writes go to both cache and database simultaneously, ensuring cache and database stay in sync.

**Strengths**:
- Cache consistency: cache and database always match
- Simpler invalidation: no need to invalidate on writes
- Good for write-heavy workloads where consistency is critical

**Weaknesses**:
- Slower writes: must update both cache and database
- Writes are only as fast as the slower of cache or database
- May not be necessary if cache-aside invalidation works well

**When to Use**:
- Write-heavy workloads where cache consistency is critical
- When write performance is acceptable
- When cache-aside invalidation is complex or unreliable

### 3. No Cache (Database Only)

**Description**: Rely solely on database performance and connection pooling, without a separate caching layer.

**Strengths**:
- Simplicity: no cache to manage or invalidate
- No stale data concerns
- Lower operational complexity
- Database connection pooling provides some performance benefits

**Weaknesses**:
- All queries hit the database
- May not scale for high read loads
- Database becomes a bottleneck for read-heavy workloads

**When to Use**:
- Low to moderate read loads
- When database performance is sufficient
- When caching complexity isn't justified
- Early-stage applications before scaling requirements are clear

## Evaluation Criteria

| Criteria | Weight | PostgreSQL | MongoDB | Event Sourcing |
|----------|--------|------------|---------|----------------|
| **Data Integrity** | High | Excellent (ACID, constraints) | Good (application-enforced) | Excellent (immutable events) |
| **Query Flexibility** | High | Excellent (SQL, joins) | Good (document queries) | Limited (event replay) |
| **Scalability** | Medium | Good (read replicas) | Excellent (sharding) | Good (projections scale) |
| **Operational Complexity** | Medium | Low (mature tooling) | Medium (sharding complexity) | High (event store, projections) |
| **Developer Experience** | High | Excellent (SQL familiarity) | Good (JSON mapping) | Medium (learning curve) |
| **Audit Trail** | Low | Good (audit tables) | Good (change streams) | Excellent (built-in) |
| **Consistency** | High | Strong (immediate) | Eventual (in sharded) | Eventual (projections) |

## Recommendation Guidance

### Default Choice: PostgreSQL

PostgreSQL should be the default choice for most applications. It provides excellent data integrity, query flexibility, and operational simplicity. JSONB support provides document-like flexibility when needed, often eliminating the need for separate document stores. The mature ecosystem, strong consistency, and SQL capabilities make it suitable for the vast majority of use cases.

### Event Sourcing for Audit-Critical Domains

Choose event sourcing (with Axon Server) for domains where audit trail and temporal queries are essential. Finance, billing, and compliance domains benefit from immutable event logs and the ability to query historical state. Event sourcing adds complexity, so use it when the benefits (audit trail, temporal queries, event-driven architecture) justify the cost.

### MongoDB Only When Schema Flexibility is Genuine

Choose MongoDB only when schema flexibility is a genuine requirement that PostgreSQL JSONB cannot satisfy. Many applications choose MongoDB to avoid migrations, but PostgreSQL migrations with proper tooling (Flyway) are manageable. Schema flexibility should be a feature requirement, not an engineering convenience.

### Hybrid Approaches

Applications often use multiple data stores: PostgreSQL for primary data, Redis for caching, and event sourcing for audit-critical domains. This hybrid approach leverages each technology's strengths while accepting the operational complexity of managing multiple systems.

## Synergies

### CQRS + Event Sourcing

If using CQRS (from backend-architecture), event sourcing provides the write model while PostgreSQL projections serve as read models. This combination enables optimized read models while maintaining a complete event history.

### Microservices + Database-per-Service

If using microservices (from backend-architecture), each service should own its database. This enforces service boundaries and enables independent scaling and deployment. Consider event-driven data synchronization for cross-service data needs.

### Monolith + Single Database

If using a monolith (from backend-architecture), a single PostgreSQL database is simplest. Shared database within a monolith is acceptable and reduces operational complexity. Consider read replicas if read load becomes a bottleneck.

### Cursor-Based Pagination + Indexed Queries

If using cursor-based pagination (from api-design), keyset pagination maps naturally to indexed queries in PostgreSQL. Indexed cursor columns enable efficient pagination without OFFSET performance degradation.

### Search + PostgreSQL FTS or OpenSearch

If implementing search (from api-design), PostgreSQL full-text search (FTS) handles moderate search needs. For advanced search (fuzzy matching, faceting, relevance tuning), consider OpenSearch (see search-and-discovery experience). Start with PostgreSQL FTS and evolve to OpenSearch if needed.

## Evolution Triggers

### Single Database Becoming a Bottleneck

When a single database becomes a bottleneck, consider read replicas for read-heavy workloads, caching for frequently accessed data, or service extraction (database-per-service) if the bottleneck indicates service boundaries.

### Need for Full Audit Trail

When audit trail requirements emerge (compliance, debugging, business intelligence), event sourcing provides built-in audit capabilities. Consider event sourcing for new features or services even if the existing system uses traditional persistence.

### Schema Flexibility Needs Beyond JSONB

If PostgreSQL JSONB cannot satisfy schema flexibility requirements, evaluate MongoDB. However, verify that schema flexibility is actually needed: many perceived flexibility needs can be addressed with proper migration strategies.

### Cache Miss Rates Indicating Need for Caching

High cache miss rates or database load from repeated queries indicate a need for caching. Implement cache-aside with Redis, focusing on high-impact, frequently accessed data.

### Query Complexity Making ORM Awkward

When JPA queries become complex or inefficient, consider JOOQ or Exposed for specific query paths. Don't abandon JPA entirely: use alternatives selectively for complex queries while keeping JPA for standard operations.
