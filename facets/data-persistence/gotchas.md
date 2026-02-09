---
title: Data Persistence - Gotchas
type: perspective
facet: data-persistence
last_updated: 2026-02-09
---

# Data Persistence - Gotchas

Common pitfalls and traps in data persistence can cause performance problems, data corruption, or production outages. Understanding these gotchas helps avoid costly mistakes.

## Contents

- [ORM Lazy Loading Surprises (LazyInitializationException)](#orm-lazy-loading-surprises-lazyinitializationexception)
- [N+1 Queries Hidden by the ORM](#n1-queries-hidden-by-the-orm)
- [Migrations That Lock Tables in Production](#migrations-that-lock-tables-in-production)
- [Shared Database Across Services Creating Coupling](#shared-database-across-services-creating-coupling)
- [Event Sourcing Without Snapshots](#event-sourcing-without-snapshots)
- [Caching Stale Data](#caching-stale-data)
- [Premature Denormalization](#premature-denormalization)

## ORM Lazy Loading Surprises (LazyInitializationException)

### The Problem

Accessing a lazy-loaded relationship outside a transaction throws `LazyInitializationException`. The entity is detached from the persistence context, so Hibernate cannot load the relationship. This commonly occurs when entities are returned from service methods and relationships are accessed in controllers or views.

### Why It Happens

JPA uses lazy loading by default: relationships are loaded only when accessed. Lazy loading requires an active persistence context (transaction). Once the transaction commits, entities become detached, and lazy loading fails.

### The Wrong Fix: EAGER Loading

Setting `FetchType.EAGER` on relationships seems like a solution, but it causes over-fetching everywhere. Every query that loads the entity also loads all eager relationships, even when they're not needed. This creates N+1 queries and performance problems.

### The Right Fixes

Use `JOIN FETCH` in queries to explicitly load needed relationships: `SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id`. This loads the user and orders in one query, and the relationship is initialized before the entity becomes detached.

Use `@EntityGraph` to specify which relationships to fetch declaratively. Define entity graphs for common access patterns and use them in repository methods.

Use DTO projections to select only needed data. Projections avoid entity detachment issues by returning simple objects instead of entities with lazy relationships.

## N+1 Queries Hidden by the ORM

### The Problem

Fetching a list of entities, then accessing a relationship on each one, causes N+1 queries. The ORM fires one query for the list, then N additional queries for the relationships. This happens silently: the ORM doesn't warn about the performance problem.

### Example

Loading 10 users, then accessing `user.getOrders()` for each user, results in 11 queries: one for users, then 10 for individual orders. With 1000 users, this becomes 1001 queries, causing severe performance degradation.

### Detection

Enable SQL logging in tests and assert query counts. When loading N entities and accessing relationships, there should be 2 queries (one for entities, one for relationships with IN clause), not N+1 queries.

### Prevention

Use `JOIN FETCH` to load relationships in the initial query. Use `@EntityGraph` to declaratively specify relationships to fetch. Use batch fetching to load relationships in batches. Monitor SQL logs in development to catch N+1 queries before they reach production.

## Migrations That Lock Tables in Production

### The Problem

`ALTER TABLE` operations can lock tables, causing downtime. Adding a column with a default value, creating an index without `CONCURRENTLY`, or modifying column types can lock large tables for minutes or hours, making the application unavailable.

### Why It Happens

PostgreSQL locks tables during certain schema changes to ensure consistency. For large tables, these locks can take significant time, blocking all reads and writes. Operations that require rewriting the table (changing column types, adding NOT NULL constraints) are particularly slow.

### Solutions

Use `CREATE INDEX CONCURRENTLY` for index creation. This builds the index without locking the table, though it takes longer and requires more careful error handling.

Add columns without defaults, then backfill data in batches, then add the default. This avoids locking the table during column addition. Use `ALTER TABLE ... ADD COLUMN ... DEFAULT NULL` first, backfill, then `ALTER TABLE ... ALTER COLUMN ... SET DEFAULT value`.

Use tools like `pg-osc` (PostgreSQL Online Schema Change) for zero-downtime schema changes on large tables. These tools use triggers and shadow tables to perform changes without locking.

### Prevention

Test migrations against production-sized datasets (or large test datasets) to identify locking issues. Use `pg_stat_activity` to monitor locks during migration testing. Plan migrations carefully: some operations cannot be made non-blocking and may require maintenance windows.

## Shared Database Across Services Creating Coupling

### The Problem

Two services reading and writing the same tables creates tight coupling. Schema changes require coordinating deployments across services. One service's load affects the other. Database failures impact multiple services. This violates microservices principles and creates operational complexity.

### Why It Happens

Services start by sharing a database for convenience: it's easier than setting up separate databases. Over time, this shared database becomes a bottleneck and coupling point. Schema changes require coordination, and one service's queries can slow down others.

### The Solution

Each service should own its database (or at minimum, its own schema). Services don't share tables: each service's data is private. Cross-service data access happens via APIs, not database joins. Data duplication is acceptable: services may cache data from other services.

### Migration Path

Migrating from a shared database to database-per-service requires careful planning. Identify service boundaries and data ownership. Extract service-specific tables into separate databases. Update services to use APIs instead of direct database access. This is a significant refactoring but essential for service autonomy.

## Event Sourcing Without Snapshots

### The Problem

Replaying thousands of events per aggregate on every load degrades performance over time. As event streams grow, aggregate loading becomes slower. Without snapshots, every aggregate load replays the entire event history, causing unacceptable latency.

### Why It Happens

Snapshots are an optimization that's easy to forget. Initially, aggregates have few events, so replay is fast. As events accumulate, replay time grows. Without proactive snapshot configuration, performance degrades gradually until it becomes a problem.

### The Solution

Configure snapshotting triggers: create a snapshot every N events (e.g., every 100 events) or when event streams exceed a threshold. Monitor event stream lengths: aggregates with thousands of events need snapshots. Axon Framework supports snapshotting through snapshot stores and triggers.

### Prevention

Set up snapshotting early, before performance becomes a problem. Monitor aggregate event stream lengths and snapshot frequency. Configure snapshotting as part of initial event sourcing setup, not as an afterthought.

## Caching Stale Data

### The Problem

Serving stale cached data after a write creates user confusion. Users update something and don't see their change because the cache still contains old data. This makes the application feel buggy or unreliable.

### Why It Happens

Cache invalidation is complex: knowing what to invalidate when data changes requires understanding data relationships. If invalidation fails or is delayed, stale data persists. TTL-based expiration can also serve stale data if the TTL hasn't expired.

### Solutions

Invalidate cache on write: when data changes, remove or update relevant cache entries. Use cache keys that include version numbers or timestamps to enable selective invalidation.

Use short TTLs for frequently changing data: if data changes often, short TTLs ensure staleness is limited. Balance TTL duration: too short increases database load, too long increases staleness.

Consider cache-aside with explicit invalidation: application code manages cache reads and writes, ensuring cache and database stay in sync. Write-through caching also ensures consistency but may be slower.

### Prevention

Design cache invalidation strategies upfront: understand what data relationships require invalidation. Test cache behavior: verify that writes invalidate relevant cache entries. Monitor cache hit rates and staleness metrics to detect problems.

## Premature Denormalization

### The Problem

Denormalizing data "for performance" before measuring creates unnecessary complexity. Denormalization trades write complexity for read speed, but if reads aren't actually slow, the complexity isn't justified. Premature denormalization makes the codebase harder to maintain without providing benefits.

### Why It Happens

Developers anticipate performance problems and denormalize preemptively. Without measurements, it's unclear whether denormalization is needed. Normalized schemas are easier to maintain, so denormalization should be a measured optimization, not a default choice.

### The Solution

Measure first: identify actual performance bottlenecks through query analysis and profiling. Denormalize specific hot paths only: if a particular query is slow and frequently executed, denormalize data for that query. Keep the rest of the schema normalized.

### Prevention

Start with normalized schemas: they're easier to maintain and reason about. Denormalize only when measurements show it's necessary. Document denormalization decisions: explain why data is duplicated and how consistency is maintained.

## Forgetting About Data Cleanup

### The Problem

Test data, soft-deleted records, expired sessions, and old audit logs accumulate indefinitely. Without cleanup, databases grow forever, consuming storage and slowing queries. This becomes a problem over time, requiring emergency cleanup operations.

### Why It Happens

Cleanup is easy to forget: it doesn't affect immediate functionality, so it's deferred. Over time, accumulated data becomes a problem, but by then, cleanup is more difficult. Soft deletes, in particular, accumulate because they're never actually removed.

### Solutions

Implement retention policies: define how long data should be retained (e.g., soft-deleted records for 90 days, audit logs for 2 years). Create automated cleanup jobs that run periodically to remove expired data.

Use database partitioning for time-series data: partition tables by time period (e.g., monthly partitions) and drop old partitions instead of deleting rows. This is much faster than row-level deletion.

Schedule regular cleanup: don't wait for data to become a problem. Proactive cleanup prevents issues and keeps databases manageable.

### Prevention

Design data retention into the schema: include expiration timestamps or flags that enable automated cleanup. Document retention policies: specify how long different data types should be retained. Set up monitoring: alert when data volumes exceed thresholds.

## Using UUIDs as Primary Keys Without Considering Performance

### The Problem

Random UUIDs (UUIDv4) cause index fragmentation and poor insert performance with B-tree indexes. Random values don't insert sequentially, causing index pages to split frequently. This degrades insert performance and increases index size.

### Why It Happens

UUIDs provide globally unique identifiers without coordination, making them attractive for distributed systems. However, random UUIDs don't work well with B-tree indexes, which expect sequential or near-sequential values.

### Solutions

Use UUIDv7 (time-ordered UUIDs): these include a timestamp component, making them more sequential and better for B-tree indexes. UUIDv7 provides global uniqueness with better insert performance.

Use sequential IDs with a separate public UUID: use auto-incrementing integers as primary keys (good for indexes) and expose UUIDs as public identifiers (good for APIs). This combines the benefits of both approaches.

Consider other identifier strategies: Snowflake IDs (Twitter's distributed ID generator) provide time-ordered unique identifiers. ULIDs (Universally Unique Lexicographically Sortable Identifiers) are similar to UUIDv7.

### Prevention

Understand the performance implications of primary key choices. If using UUIDs, prefer UUIDv7 or time-ordered variants. If random UUIDs are required, consider using hash indexes or other index types that handle random values better, though this may limit query capabilities.
