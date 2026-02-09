# Performance -- Gotchas

## Contents

- [Premature Optimization](#premature-optimization)
- [N+1 Queries](#n1-queries)
- [Bundle Size Creep](#bundle-size-creep)
- [Caching Without Invalidation Strategy](#caching-without-invalidation-strategy)
- [Load Testing in the Wrong Environment](#load-testing-in-the-wrong-environment)
- [Ignoring p99 Latency](#ignoring-p99-latency)
- [Memory Leaks in Frontend](#memory-leaks-in-frontend)
- [Synchronous I/O Blocking Threads](#synchronous-io-blocking-threads)
- [Over-Caching](#over-caching)
- [Over-Indexing](#over-indexing)
- [Not Accounting for Cold Starts](#not-accounting-for-cold-starts)
- [Database Connection Exhaustion](#database-connection-exhaustion)
- [Ignoring Mobile and Low-Bandwidth Users](#ignoring-mobile-and-low-bandwidth-users)

Common performance pitfalls that catch teams off guard. These are lessons learned from real projects where performance degraded silently until it became a crisis.

## Premature Optimization

Spending days optimizing code that handles 100 requests per day while ignoring the endpoint that handles 100,000. Profile first, optimize second. Measure the actual bottleneck, not the assumed one. As Knuth said: "The real problem is that programmers have spent far too much time worrying about efficiency in the wrong places and at the wrong times."

**What happens**: a developer rewrites a utility function to be 10x faster. The function accounts for 0.01% of total request time. The real bottleneck -- a missing database index -- remains untouched.

**Better approach**: use profiling tools (async-profiler, JFR for backend; Chrome DevTools Performance tab for frontend) to identify actual hotspots. Optimize the top bottleneck first.

## N+1 Queries

Fetching a list of 100 items, then making a separate database query for each item's relationship. The result is 101 queries instead of 2. ORMs like Hibernate make this easy to create accidentally because lazy loading is the default.

**What happens**: the endpoint works fine in development with 5 records. In production with 10,000 records, it takes 30 seconds. SQL logging reveals thousands of queries.

**Better approach**: enable SQL logging in tests and assert query counts. Use `JOIN FETCH` (JPA), `@EntityGraph`, or batch fetching. For complex cases, consider native queries or projections.

## Bundle Size Creep

Each new dependency adds "just 50KB." Over months, the JavaScript bundle grows from 200KB to 2MB. Initial page load goes from 1 second to 5 seconds. Nobody notices the gradual degradation because each individual addition is small.

**What happens**: the app feels fast in development (served locally, no network latency). In production on a mobile device, initial load takes 8 seconds. Users on slower connections abandon the page.

**Better approach**: monitor bundle size in CI. Set a budget (e.g., 250KB gzipped for the main bundle) and fail builds that exceed it. Review new dependency sizes before adding them. Use bundle analysis tools (rollup-plugin-visualizer) to identify the largest contributors. Consider lighter alternatives (date-fns vs moment.js, preact vs react for lightweight apps).

## Caching Without Invalidation Strategy

Caching aggressively to improve performance, but without a clear plan for when cached data becomes stale. Users see outdated information and lose trust.

**What happens**: an invoice is updated from "pending" to "paid." The list view still shows "pending" because it's cached. The user clicks refresh, still sees "pending" (cache TTL hasn't expired). They contact support.

**Better approach**: every cache entry needs an invalidation strategy. Invalidate explicitly after mutations (using `queryClient.invalidateQueries` in TanStack Query, or explicit cache eviction in Redis). Use short TTLs for frequently changing data. For critical data, consider cache-aside with write-through invalidation.

## Load Testing in the Wrong Environment

Load testing against a development environment with a single database instance and 512MB of RAM. Results show "handles 1000 requests/second easily." Production has different characteristics entirely.

**What happens**: load test passes in dev. In production under real load, the database connection pool exhausts, thread pools saturate, and response times spike. The load test didn't reveal this because the test environment had different resource constraints.

**Better approach**: load test against a production-like environment with similar resource allocations, network topology, and data volumes. If production has a million rows, the load test database should too. Infrastructure-as-code makes replicating production environments feasible.

## Ignoring p99 Latency

Average latency is 50ms, so "performance is fine." But p99 is 5 seconds, meaning 1 in 100 requests takes 100x longer. For a user making 10 requests per session, there's a 10% chance they'll experience the slow path.

**What happens**: dashboards show healthy average latency. Support tickets about "the app is slow sometimes" are dismissed as user error. High-value users churn because they consistently hit the slow tail.

**Better approach**: monitor percentiles (p50, p95, p99), not averages. Set SLOs on percentiles ("p95 latency < 500ms"). Alert on percentile degradation. Investigate and fix the causes of tail latency (GC pauses, connection pool exhaustion, lock contention, cold caches).

## Memory Leaks in Frontend

Event listeners not removed on component unmount, intervals not cleared, closures retaining references to large objects, WebSocket subscriptions not cleaned up. Memory usage grows over time.

**What happens**: the app works fine for a few minutes. After extended use (common in dashboard-style apps that stay open all day), the page becomes sluggish. Eventually the browser tab crashes.

**Better approach**: always clean up in component unmount lifecycle hooks (`onUnmounted` in Vue, return function from `useEffect` in React). Use weak references where appropriate. Profile memory usage over time in Chrome DevTools Memory tab. Watch for detached DOM nodes.

## Synchronous I/O Blocking Threads

A database query or HTTP call that blocks the thread. In a traditional servlet container, each blocked thread is unavailable for other requests. Under load, all threads are blocked waiting on slow I/O.

**What happens**: the service handles 100 concurrent requests fine (100 threads). At 200 concurrent requests, threads exhaust, requests queue, latency spikes, timeouts cascade.

**Better approach**: use connection pooling with appropriate sizing. Consider virtual threads (Java 21+) for I/O-bound workloads. Move long-running I/O to async processing (message queues). Set explicit timeouts on all I/O operations.

## Over-Caching

Caching data that changes every second or is unique per user. Cache hit rate is near zero, but you pay the overhead of serialization, cache writes, cache lookups, and invalidation logic.

**What happens**: every API response is cached in Redis. Cache hit rate is 3%. Redis memory usage is high. Cache writes add 5ms to every request. Net performance is worse with caching than without.

**Better approach**: only cache data that is read significantly more often than it's written. Monitor cache hit rates. If hit rate is below 50%, reconsider whether caching is appropriate for that data. Focus caching on expensive computations and frequently accessed, rarely changing data.

## Over-Indexing

Adding an index for every query pattern. Each index speeds up reads but slows down writes (every INSERT and UPDATE must update all indexes) and consumes storage.

**What happens**: a table with 15 indexes has slow inserts. Bulk data imports that used to take minutes now take hours. Write-heavy workloads degrade.

**Better approach**: index strategically based on actual query patterns. Use `pg_stat_user_indexes` to find unused indexes. Remove indexes that aren't used. Composite indexes can serve multiple query patterns. Partial indexes reduce index size for filtered queries.

## Not Accounting for Cold Starts

The first request after deployment, scaling, or cold start is significantly slower than subsequent requests. JVM warmup (JIT compilation), empty caches, uninitialized connection pools, and class loading all contribute.

**What happens**: after a deployment, the first few users experience 3-5 second response times. Auto-scaled instances serve their first requests slowly before warming up. Health checks pass (basic /health endpoint) but the service isn't truly ready.

**Better approach**: implement warmup endpoints that pre-populate caches and trigger JIT compilation. Use readiness probes in Kubernetes that check actual functionality, not just process liveness. Configure minimum replicas to maintain warm instances. Consider GraalVM native images for services where fast startup is critical (serverless functions, batch jobs).

## Database Connection Exhaustion

Not monitoring database connection pool usage until connections run out. Every request waits for a connection, latency spikes, timeouts cascade, and the service becomes unresponsive.

**What happens**: the connection pool has 10 connections. Under moderate load, all 10 are in use. New requests wait for a connection. If a few queries are slow (missing index, lock contention), connections are held longer, wait times grow, and the system enters a death spiral.

**Better approach**: monitor connection pool metrics (active connections, pending acquisitions, wait time) with Micrometer/Prometheus. Set connection acquisition timeouts. Alert when pool utilization exceeds 80%. Size the pool appropriately for the workload. Ensure queries release connections quickly (keep transactions short).

## Ignoring Mobile and Low-Bandwidth Users

Optimizing for developer hardware (fast MacBook, wired Ethernet, local server). Deployed users on mobile devices with 3G connections have a fundamentally different experience.

**What happens**: the app loads in 500ms on the developer's machine. On a mid-range Android phone on a 3G connection, it takes 15 seconds. The developer never sees this because they never test under realistic conditions.

**Better approach**: test with Chrome DevTools network throttling (Slow 3G, Fast 3G). Test on actual mid-range devices. Set performance budgets based on the 75th percentile user, not the ideal user. Prioritize critical content and lazy load everything else.
