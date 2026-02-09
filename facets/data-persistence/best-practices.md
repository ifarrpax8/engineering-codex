---
title: Data Persistence - Best Practices
type: perspective
facet: data-persistence
last_updated: 2026-02-09
---

# Data Persistence - Best Practices

Best practices for data persistence balance correctness, performance, and maintainability. These principles guide day-to-day development decisions and prevent common mistakes.

## Contents

- [Migration Best Practices](#migration-best-practices)
- [Index Strategy](#index-strategy)
- [N+1 Query Prevention](#n1-query-prevention)
- [Connection Pool Sizing](#connection-pool-sizing)
- [Transaction Management](#transaction-management)

## Migration Best Practices

### Migrations Must Be Backward-Compatible

New code must work with old schema, and old code must continue working during deployment. This enables zero-downtime deployments and gradual rollouts. The expand/contract pattern achieves backward compatibility: expand (add new structure), migrate data, update code, contract (remove old structure in a later release).

When adding a column, make it nullable first, backfill data, then add a default or make it non-nullable. This allows new code to write to the column while old code ignores it. When removing a column, deploy code that stops using the column first, then deploy a migration that drops it.

### Never Delete Columns in the Same Release as Code Change

Dropping a column in the same release as code that uses it risks breaking deployments. If new code fails to deploy but the migration succeeds, the application breaks. Always deploy code changes first: deploy code that no longer uses the column, verify it's running in production, then deploy the migration that drops the column.

This two-release process ensures safety: if code deployment fails, the old code still works with the existing schema. Only after code is successfully deployed can the schema change safely proceed.

### Use the Expand/Contract Pattern

The expand/contract pattern enables zero-downtime schema changes. Expand: add new columns or tables without removing old ones. Migrate: copy data from old structure to new structure. Update code: deploy code that uses the new structure but can read the old structure. Contract: in a later release, remove the old structure after all instances are running new code.

This pattern requires discipline: it takes multiple releases to complete a schema change. The benefit is zero downtime and safe rollbacks: if new code has issues, old code still works with the existing schema.

## Index Strategy

### Always Index Foreign Keys

Foreign keys are frequently joined, so indexing them improves join performance. PostgreSQL doesn't automatically index foreign keys (unlike some databases), so explicitly create indexes on all foreign key columns. This prevents full table scans when joining tables.

### Add Indexes for WHERE Clause Columns

Columns used in WHERE clauses should be indexed to avoid full table scans. Analyze query patterns: if queries frequently filter by `status`, `created_at`, or `user_id`, index these columns. Use `EXPLAIN ANALYZE` to verify index usage: queries should show Index Scan, not Sequential Scan.

### Use Partial Indexes for Common Filtered Queries

Partial indexes index only rows matching a condition, reducing index size and maintenance overhead. If most queries filter by `status = 'active'`, create a partial index: `CREATE INDEX ON orders (user_id) WHERE status = 'active'`. This index is smaller and faster than a full index, and it naturally supports the common query pattern.

### Use GIN Indexes for Full-Text Search and JSONB

GIN indexes support full-text search and JSONB queries efficiently. For text search, create a GIN index on the text column with `to_tsvector`. For JSONB queries, create a GIN index on the JSONB column. These indexes enable fast searches that would otherwise require full table scans.

### Don't Over-Index

Each index slows writes and consumes storage. Indexes must be updated on every insert, update, or delete that affects indexed columns. Too many indexes degrade write performance. Only index columns that are actually used in queries: use `EXPLAIN ANALYZE` to verify index usage, and remove unused indexes.

## N+1 Query Prevention

### Use JOIN FETCH (JPA)

`JOIN FETCH` loads related entities in a single query, preventing N+1 queries. When loading users and their orders, use `SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id`. This loads the user and orders in one query instead of N+1 queries.

### Use @EntityGraph

`@EntityGraph` specifies which relationships to fetch, avoiding N+1 queries. Define entity graphs that include commonly accessed relationships, then use them in repository methods. This provides declarative control over fetching without writing custom queries.

### Use Batch Fetching

Batch fetching loads relationships in batches: instead of N queries for N entities, it uses a few queries with IN clauses. Configure batch fetching in entity mappings or use `@BatchSize`. This reduces query count while keeping queries simple.

### Monitor with SQL Logging in Tests

Enable SQL logging in tests to detect N+1 queries. Assert query counts: when loading 10 users and accessing their orders, there should be 2 queries, not 11. SQL logging reveals hidden N+1 queries that ORMs create silently.

### Consider Projections or Native Queries

If ORM fetching is complex or inefficient, consider DTO projections or native queries. Projections select only needed columns and relationships, avoiding over-fetching. Native queries provide full control over SQL, enabling optimizations that ORMs don't support.

## Connection Pool Sizing

### Starting Formula: (core_count * 2) + effective_spindle_count

This formula provides a starting point for connection pool sizing, but actual sizing requires monitoring. The formula accounts for CPU cores (parallel query execution) and disk spindles (I/O parallelism), but modern SSDs and connection patterns may differ from these assumptions.

### Monitor Pool Wait Times

If requests frequently wait for database connections, increase pool size. Pool wait times indicate that the pool is too small: requests are queuing because all connections are in use. Monitor pool metrics: active connections, idle connections, and wait times.

### Don't Set Max Too High

Each connection consumes database server memory and CPU. Setting max pool size too high can overwhelm the database, causing performance degradation. Database connection limits (typically 100-1000 connections) also constrain pool size. Balance pool size: large enough to handle load, small enough to avoid overwhelming the database.

## Transaction Management

### Keep Transactions Short

Long-running transactions hold locks, block other transactions, and increase deadlock risk. Keep transactions focused on a single business operation: load data, perform business logic, save changes. Don't hold transactions across HTTP requests, external API calls, or user interactions.

### Don't Hold Transactions Across HTTP Calls

HTTP calls can take seconds or fail, causing transactions to remain open unnecessarily. Perform HTTP calls before starting transactions or after committing them. If external calls are required within a transaction, make them fast and handle failures gracefully to avoid long-running transactions.

### Use @Transactional at Service Layer, Not Controller

Transactions should encompass business logic, not HTTP handling. Place `@Transactional` on service methods, not controller methods. This ensures transactions include all business operations but exclude HTTP request/response handling, which doesn't need transactional behavior.

## Spring Data JPA Best Practices

### Repository Interfaces

Spring Data JPA repositories are interfaces that extend `JpaRepository`. Define custom query methods using method names (Spring generates queries) or `@Query` annotations. Use repositories for all database access: they provide type safety, pagination support, and transaction management.

```kotlin
// Kotlin: repositories/UserRepository.kt
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface UserRepository : JpaRepository<User, Long> {
    // Method name query (Spring generates SQL)
    fun findByEmail(email: String): User?
    
    // Custom JPQL query
    @Query("SELECT u FROM User u WHERE u.status = :status AND u.createdAt > :since")
    fun findActiveUsersSince(
        @Param("status") status: UserStatus,
        @Param("since") since: LocalDateTime
    ): List<User>
    
    // Native SQL query
    @Query(
        value = "SELECT * FROM users WHERE email LIKE :pattern",
        nativeQuery = true
    )
    fun findByEmailPattern(@Param("pattern") pattern: String): List<User>
}
```

```java
// Java: repositories/UserRepository.java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Method name query (Spring generates SQL)
    Optional<User> findByEmail(String email);
    
    // Custom JPQL query
    @Query("SELECT u FROM User u WHERE u.status = :status AND u.createdAt > :since")
    List<User> findActiveUsersSince(
        @Param("status") UserStatus status,
        @Param("since") LocalDateTime since
    );
    
    // Native SQL query
    @Query(
        value = "SELECT * FROM users WHERE email LIKE :pattern",
        nativeQuery = true
    )
    List<User> findByEmailPattern(@Param("pattern") String pattern);
}
```

### Custom Query Methods (@Query)

`@Query` annotations enable custom JPQL or native SQL queries. Use JPQL for database-agnostic queries, native SQL for database-specific features or performance-critical queries. Parameter binding prevents SQL injection: use `:parameterName` in JPQL or `?1, ?2` in native SQL.

### Paginated Queries

Use Spring Data's `Pageable` interface for pagination and sorting. This provides efficient database-level pagination and consistent API patterns.

```kotlin
// Kotlin: repositories/UserRepository.kt
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface UserRepository : JpaRepository<User, Long> {
    // Paginated query with sorting
    fun findByStatus(status: UserStatus, pageable: Pageable): Page<User>
    
    // Custom paginated query
    @Query("SELECT u FROM User u WHERE u.createdAt >= :since")
    fun findUsersCreatedSince(
        @Param("since") since: LocalDateTime,
        pageable: Pageable
    ): Page<User>
}

// Usage in service
@Service
class UserService(private val userRepository: UserRepository) {
    fun getActiveUsers(page: Int, size: Int, sortBy: String): Page<User> {
        val pageable = PageRequest.of(
            page,
            size,
            Sort.by(Sort.Direction.DESC, sortBy)
        )
        return userRepository.findByStatus(UserStatus.ACTIVE, pageable)
    }
}
```

```java
// Java: repositories/UserRepository.java
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserRepository extends JpaRepository<User, Long> {
    // Paginated query with sorting
    Page<User> findByStatus(UserStatus status, Pageable pageable);
    
    // Custom paginated query
    @Query("SELECT u FROM User u WHERE u.createdAt >= :since")
    Page<User> findUsersCreatedSince(
        @Param("since") LocalDateTime since,
        Pageable pageable
    );
}

// Usage in service
@Service
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public Page<User> getActiveUsers(int page, int size, String sortBy) {
        Pageable pageable = PageRequest.of(
            page,
            size,
            Sort.by(Sort.Direction.DESC, sortBy)
        );
        return userRepository.findByStatus(UserStatus.ACTIVE, pageable);
    }
}
```

### Projections

Projections select only needed columns and relationships, reducing data transfer and memory usage. Interface-based projections define interfaces with getter methods matching query results. DTO-based projections use classes with constructors matching query results. Use projections to avoid loading full entities when only specific fields are needed.

### Specification Pattern for Dynamic Queries

The Specification pattern enables building dynamic queries programmatically. Define specifications that can be combined with AND/OR logic, enabling flexible query construction based on user input or business rules. This avoids writing many similar query methods or building complex query strings.

## Axon Framework Best Practices

### Aggregate Event Sourcing

Aggregates in Axon Framework use event sourcing: state changes are stored as events, and current state is derived by replaying events. Design aggregates to be small and focused: large aggregates with many events are slow to load. Use aggregate boundaries to limit event stream size.

### @EventSourcingHandler

`@EventSourcingHandler` methods handle events during aggregate loading and command processing. Keep handlers focused: each handler updates aggregate state based on one event type. Handlers must be deterministic: same events must produce same state, enabling reliable replay.

### Snapshotting Triggers

Configure snapshotting to create snapshots every N events (e.g., every 100 events) or when event streams exceed a threshold. Snapshots dramatically improve load performance for aggregates with long event streams. Monitor event stream lengths: aggregates with thousands of events benefit from snapshots.

### Dead Letter Queue for Failed Projections

Projection handlers can fail: network issues, database constraints, or bugs can cause failures. Axon's dead letter queue captures failed events for manual investigation and retry. Monitor dead letter queues: frequent failures indicate systemic problems that must be addressed.

## Flyway Best Practices

### V{version}__{description}.sql Naming

Migration files must follow Flyway's naming convention: `V{version}__{description}.sql`. The version number determines execution order: `V1__create_users.sql` runs before `V2__add_email_index.sql`. Use descriptive names that explain the migration's purpose.

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- V2__add_user_profile_table.sql
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
```

### Repeatable Migrations (R__)

Repeatable migrations (`R__{description}.sql`) run every time if their checksum changes. Use them for views, functions, or seed data that should be reapplied when definitions change. Repeatable migrations run after versioned migrations, enabling idempotent updates to database objects.

### Callbacks for Seed Data

Flyway callbacks (`beforeMigrate.sql`, `afterMigrate.sql`) enable running scripts at specific migration lifecycle points. Use callbacks for seed data that must exist for applications to function. Avoid putting seed data in versioned migrations: it makes migrations harder to test and can cause issues in production.

### Multi-Schema Setups

Applications may use multiple schemas: one for application data, one for Flyway's schema history. Configure Flyway to use the correct schema for migrations and history tracking. Multi-schema setups enable separating application schemas while maintaining migration history.

## Alternatives to JPA

### JOOQ (Type-Safe SQL)

JOOQ generates Java code from database schemas, providing type-safe SQL construction. Queries are compile-time checked: typos in column names cause compilation errors. JOOQ excels at complex queries where JPA's query generation is awkward or inefficient.

Use JOOQ when query complexity makes JPA difficult: complex joins, window functions, or database-specific features. JOOQ's code generation ensures queries match the current schema, catching schema mismatches at compile time.

### Exposed (Kotlin DSL for SQL)

Exposed provides a Kotlin DSL for SQL queries, offering type safety and expressiveness. It's similar to JOOQ but designed for Kotlin. Use Exposed in Kotlin projects where JPA feels verbose or when you need more control over SQL generation.

### When to Consider Alternatives

Consider alternatives to JPA when query complexity makes JPA awkward, when you need database-specific features that JPA doesn't support well, or when type safety is critical. JPA is excellent for simple CRUD operations and basic queries, but complex queries may benefit from JOOQ or Exposed.

Don't abandon JPA prematurely: it provides excellent developer experience for common operations. Use alternatives selectively for specific complex queries or performance-critical paths.
