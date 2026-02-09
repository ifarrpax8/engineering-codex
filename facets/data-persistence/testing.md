---
title: Data Persistence - Testing
type: perspective
facet: data-persistence
last_updated: 2026-02-09
---

# Data Persistence - Testing

Testing data persistence requires validating schema, queries, migrations, and data integrity. This perspective covers testing strategies and tooling for ensuring data layer correctness and performance.

## Contents

- [Database Integration Tests with Testcontainers](#database-integration-tests-with-testcontainers)
- [Slice Testing with @DataJpaTest](#slice-testing-with-datajpatest)
- [Migration Testing](#migration-testing)
- [Data Integrity Tests](#data-integrity-tests)
- [Repository Testing Patterns](#repository-testing-patterns)
- [Testing Event-Sourced Aggregates](#testing-event-sourced-aggregates)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Database Integration Tests with Testcontainers

Testcontainers spins up real database instances in Docker containers for integration tests. This provides authentic database behavior without mocking, ensuring tests validate actual SQL execution, constraints, and database-specific features.

### Testcontainers Setup

The `@Testcontainers` annotation enables Testcontainers lifecycle management. Define a `@Container` field with a PostgreSQL container configuration. Testcontainers starts the container before tests and stops it after, providing an isolated database for each test run.

```java
@SpringBootTest
@Testcontainers
class UserRepositoryTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
}
```

### Shared Container per Test Class

Starting a database container is slow (several seconds). Sharing a container across tests in the same class improves test performance. Use a static container field: Testcontainers reuses the same container for all tests in the class, only creating a new container if the previous one was stopped.

### Isolated Data per Test

Each test should start with a clean database state. Use `@Transactional` with `@Rollback` to automatically roll back changes after each test. Alternatively, use `@Sql` annotations to set up test data before each test and clean up afterward. Flyway migrations can initialize the schema, and tests insert only the data they need.

Transaction rollback ensures test isolation: one test's data doesn't affect another. This prevents test interdependencies that make tests flaky and hard to debug.

## Slice Testing with @DataJpaTest

`@DataJpaTest` is a Spring Boot slice test that configures only JPA components. It excludes web layers, security, and other non-JPA components, providing a focused test environment for repository testing.

### JPA Component Configuration

`@DataJpaTest` automatically configures an in-memory database (H2) or can use Testcontainers if configured. It sets up `EntityManager`, transaction management, and repository beans, but excludes service and controller layers. This provides fast, focused tests for repository queries.

### Embedded H2 or Testcontainers

By default, `@DataJpaTest` uses H2, an in-memory Java database. H2 is fast but doesn't support all PostgreSQL features. For PostgreSQL-specific features (JSONB, full-text search, specific functions), configure `@DataJpaTest` to use Testcontainers instead.

### Testing Repository Queries

Repository tests validate query correctness: custom query methods return expected results, pagination works correctly, and native SQL queries execute properly. Test both happy paths and edge cases: empty results, null handling, and constraint violations.

## Migration Testing

Migrations are critical infrastructure changes that can cause production outages if incorrect. Testing migrations ensures they execute successfully, maintain data integrity, and can be rolled back if needed.

### Running Migrations Against Clean Database

CI pipelines should run Flyway migrations against a clean database to validate migration scripts. This catches syntax errors, constraint violations, and migration ordering issues before production deployment. Use Testcontainers to spin up a fresh PostgreSQL instance, run all migrations, and verify the final schema state.

### Backward and Forward Compatibility

Test migration compatibility: new code must work with old schema (backward compatibility), and old code must work with new schema during rollout (forward compatibility). Deploy new code that works with both old and new schemas, then deploy the migration, then remove old code that depends on the old schema.

Test this by running migrations incrementally: apply migrations up to version N, verify application works, apply migration N+1, verify application still works, then continue. This validates the expand/contract pattern.

### Validating Migration Scripts Don't Lock Tables

Some migration operations lock tables, causing downtime. Test migrations against production-sized datasets (or at least large test datasets) to identify locking issues. Use `pg_stat_activity` to monitor locks during migration testing. Operations like `CREATE INDEX CONCURRENTLY` avoid locks, while `CREATE INDEX` locks the table.

## Data Integrity Tests

Data integrity ensures constraints, relationships, and business rules are enforced at the database level. Testing integrity validates that the database prevents invalid data, not just that application code checks it.

### Verifying Constraints

Test unique constraints: attempting to insert duplicate values should fail. Test foreign key constraints: inserting a record with a non-existent foreign key should fail. Test not-null constraints: inserting null into a required column should fail. Test check constraints: inserting values that violate check conditions should fail.

These tests validate that database constraints match application expectations. Relying solely on application-level validation is insufficient: bugs or direct database access can bypass application checks.

### Testing Cascade Behaviors

Foreign key cascade behaviors (ON DELETE CASCADE, ON UPDATE CASCADE) must work correctly. Test that deleting a parent record cascades to child records appropriately. Test that updating a parent's primary key cascades if configured. Verify cascade behaviors match business requirements: some relationships should cascade, others should prevent deletion.

### Validating Indexes Exist for Query Patterns

Indexes should exist for all query patterns. Test that queries use indexes by examining query plans with `EXPLAIN ANALYZE`. Missing indexes cause full table scans, degrading performance. Index tests can be assertions: verify that specific indexes exist for critical query columns.

## Repository Testing Patterns

Repository tests validate data access layer correctness. They test custom queries, pagination, and query performance characteristics.

### Testing Custom Query Methods

Custom query methods (`@Query` annotations, method name queries) must return correct results. Test with various inputs: valid data, edge cases, empty results, and invalid inputs. Verify that queries handle null correctly and return expected data types.

### Testing Pagination Queries

Pagination must work correctly: page size limits results, page numbers advance correctly, and total count is accurate. Test edge cases: first page, last page, empty result sets, and page numbers beyond available data. Verify that pagination uses efficient queries (LIMIT/OFFSET or keyset pagination) rather than loading all data.

### Testing Native SQL Queries

Native SQL queries bypass JPA's query translation, so they must be tested carefully. Verify that native queries return expected results, handle parameters correctly, and work with the current schema. Test that native queries don't break when schema changes (though ideally, avoid native queries when JPA queries suffice).

### Verifying N+1 Queries Don't Exist

N+1 queries occur when loading a collection of entities, then accessing a relationship on each entity. The ORM fires one query for the collection, then N queries for the relationships. This is a common performance problem.

Enable SQL logging in tests and assert query counts. When loading 10 users and accessing their orders, there should be 2 queries (one for users, one for orders with a WHERE user_id IN (...)), not 11 queries (one for users, 10 for individual orders).

Use `JOIN FETCH`, `@EntityGraph`, or batch fetching to prevent N+1 queries. Test that these solutions actually reduce query count.

## Testing Event-Sourced Aggregates

Event-sourced aggregates store state as events. Testing them requires validating that commands produce correct events and that event replay reconstructs state correctly.

### AggregateTestFixture

Axon Framework's `AggregateTestFixture` provides a testing framework for aggregates. It supports given-when-then syntax: given these events, when this command, then expect these events. This validates aggregate behavior without requiring a full event store setup.

```java
fixture.givenEvents(new UserCreatedEvent(userId, email))
       .when(new UpdateEmailCommand(userId, newEmail))
       .expectEvents(new EmailUpdatedEvent(userId, newEmail));
```

### Testing Projection Handlers

Projection handlers update read models based on events. Test them by publishing events and verifying read model state. Given these events, verify that the read model contains expected data. Test idempotency: replaying the same events should produce the same result.

Test projection handlers in isolation: use an in-memory database or Testcontainers, publish events, and assert read model state. This validates projection logic without requiring a full event store.

## Cache Behavior Testing

Caching introduces complexity: cache hits, misses, expiration, and invalidation must work correctly. Testing cache behavior ensures caching improves performance without causing correctness issues.

### Testing Cache Hit and Miss Scenarios

Test cache hits: when data exists in cache, it should be returned without querying the database. Verify database query count: cache hits should result in zero database queries. Test cache misses: when data doesn't exist in cache, it should be loaded from the database and stored in cache.

### Testing TTL Expiration

TTL expiration should remove cache entries after the time limit. Test by caching data, waiting for TTL to expire, then verifying that the next access triggers a cache miss and database query. Use test time manipulation or short TTLs in tests to avoid long waits.

### Testing Cache Invalidation

Cache invalidation should remove entries when data changes. Test that writes invalidate relevant cache entries, and subsequent reads reload from the database. Verify that invalidation is selective: updating one user's data shouldn't invalidate another user's cached data.

### Using Embedded Redis (Testcontainers)

Use Testcontainers to spin up Redis for integration tests. This provides authentic Redis behavior without requiring a separate Redis instance. Test cache operations against real Redis to validate client configuration and cache logic.

## Performance Testing Queries

Query performance directly impacts application responsiveness. Testing query performance identifies slow queries and validates index effectiveness.

### EXPLAIN ANALYZE for Query Plans

`EXPLAIN ANALYZE` shows the query execution plan and actual execution statistics. Use it to understand how PostgreSQL executes queries: which indexes are used, how many rows are examined, and execution time. Query plans reveal missing indexes, inefficient joins, and full table scans.

### Identifying Slow Queries

Slow queries degrade user experience and may indicate missing indexes or inefficient query patterns. Enable slow query logging in tests (or use `EXPLAIN ANALYZE` timing) to identify queries that exceed performance thresholds. Set performance budgets: queries should complete within specific time limits, and tests should fail if queries exceed these limits.

### Index Effectiveness Verification

Indexes should actually improve query performance. Test queries with and without indexes to measure improvement. Verify that `EXPLAIN ANALYZE` shows index usage (Index Scan or Index Only Scan) rather than Sequential Scan. Unused indexes waste storage and slow writes, so remove them if queries don't use them.

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize data persistence testing based on data integrity risk and business impact. Critical paths requiring immediate coverage include: data integrity constraints (unique constraints, foreign keys, not-null constraints), transaction boundaries (rollback scenarios, commit failures), and migration scripts (schema changes, data migrations). High-priority areas include: query correctness (results match expectations), performance (queries complete within acceptable time), and concurrency (concurrent transactions don't corrupt data).

Medium-priority areas suitable for later iterations include: index optimization, query tuning, and archive/cleanup operations. Low-priority areas for exploratory testing include: edge case data types, rarely-used database features, and performance optimization opportunities.

Focus on failures with high data integrity risk: data corruption (incorrect updates, lost data), constraint violations (invalid data accepted), and migration failures (schema changes break applications). These represent the highest risk of data loss and application failures.

### Exploratory Testing Guidance

Data integrity exploration: test constraint enforcement (unique constraints, foreign keys, check constraints), cascade behaviors (ON DELETE CASCADE, ON UPDATE CASCADE), and null handling (not-null constraints, nullable fields). Probe edge cases: duplicate values, orphaned records, and invalid relationships.

Transaction boundaries require investigation: test rollback scenarios (exceptions during transactions), commit failures (database errors), and savepoint behavior (nested transactions). Explore what happens with concurrent transactions: lock contention, deadlocks, and isolation level behavior.

Migration testing needs exploration: test forward compatibility (new code with old schema), backward compatibility (old code with new schema), and data migration correctness (data transformed correctly). Probe edge cases: migration failures, partial migrations, and rollback scenarios.

Query performance requires investigation: test query plans (index usage, full table scans), query execution times (slow queries, timeouts), and query optimization (missing indexes, inefficient joins). Explore what happens with large datasets, complex queries, and concurrent queries.

### Test Data Management

Data persistence testing requires realistic test data: entities in various states (active, archived, pending), relationships between entities (users with orders, orders with payments), and historical data (for time-based queries). Create test data factories that generate realistic entities: `createUserWithOrderHistory()`, `createOrderWithPaymentHistory()`.

Sensitive database data must be masked: PII (names, emails, addresses), financial data (account numbers, amounts), and authentication data (password hashes, tokens). Use data masking utilities in test databases and logs. Test data should be clearly identifiable as test data to prevent confusion with production data.

Test data refresh strategies: databases may have data dependencies (users must exist before orders), state dependencies (orders transition through states), and cleanup requirements (test data must be removed). Implement test data setup/teardown that creates dependencies, manages state, and cleans up after tests.

Migration testing requires test data management: test migrations must use realistic data volumes and data distributions. Maintain test datasets that represent production-like data: data volumes, data distributions, and data relationships.

### Test Environment Considerations

Data persistence test environments must match production: same database technology (PostgreSQL, MySQL), same database version, and same schema. Differences can hide bugs or create false positives. Verify that test environments use production-like configurations: database versions, schema definitions, and constraint configurations.

Shared test environments create isolation challenges: concurrent tests may create conflicting data, exhaust connection pools, or interfere with each other. Use isolated test environments per test run (Testcontainers), or implement test data isolation through unique identifiers and cleanup between tests.

Environment-specific risks include: test databases with relaxed constraints, test environments missing production indexes, and test environments with different performance characteristics. Verify that test environments have equivalent constraints and indexes, or explicitly test differences as separate scenarios.

Database version differences: test environments may use different database versions than production. Verify that test database versions match production, or test across multiple versions to catch version-specific issues.

### Regression Strategy

Data persistence regression suites must include: data integrity constraints (unique constraints, foreign keys, not-null constraints), transaction boundaries (rollback scenarios, commit failures), query correctness (results match expectations), and migration scripts (schema changes, data migrations). These represent the core data persistence functionality that must never break.

Automation candidates for regression include: constraint validation (unique constraints, foreign keys), transaction tests (rollback scenarios, commit failures), and query tests (results match expectations). These are deterministic and can be validated automatically.

Manual regression items include: migration testing (schema changes, data migrations), performance testing (query execution times, index usage), and concurrency testing (concurrent transactions, lock contention). These require human judgment or performance testing tools.

Trim regression suites by removing tests for deprecated schemas, obsolete migrations, or rarely-used database features. However, maintain tests for critical data integrity constraints (unique constraints, foreign keys) even if they're simple—data integrity regressions have high impact.

### Defect Patterns

Common data persistence bugs include: data corruption (incorrect updates, lost data), constraint violations (invalid data accepted), transaction bugs (partial commits, rollback failures), and migration failures (schema changes break applications). These patterns recur across applications and should be tested explicitly.

Bugs tend to hide in: edge cases (boundary conditions, null handling), error paths (exception handling, failure modes), and concurrent operations (race conditions, data corruption). Test these scenarios explicitly—they're common sources of data integrity issues.

Historical patterns show that data persistence bugs cluster around: constraint enforcement (unique constraints, foreign keys), transaction management (rollback scenarios, commit failures), and migration scripts (schema changes, data migrations). Focus exploratory testing on these areas.

Triage guidance: data persistence bugs affecting data integrity are typically high severity due to data loss risk. However, distinguish between data corruption bugs (data integrity compromised) and performance issues (slow but correct). Data corruption bugs require immediate attention, while performance issues can be prioritized based on impact.
