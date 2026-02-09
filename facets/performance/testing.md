---
title: Performance - Testing
type: perspective
facet: performance
last_updated: 2026-02-09
---

# Performance: Testing

Performance testing validates that applications meet user experience and scalability goals under realistic conditions. This perspective covers load testing, performance benchmarking, frontend performance testing, database query performance testing, API latency testing, stress testing, soak testing, profiling, and regression testing.

## Load Testing

Load testing simulates realistic user traffic to validate system behavior under expected load conditions. Load tests reveal bottlenecks, validate scalability assumptions, and ensure systems can handle peak traffic without degradation.

Load testing tools simulate multiple concurrent users making requests to the application. k6 provides a JavaScript-based approach that's developer-friendly and excellent for CI integration. Gatling offers a JVM-based solution with Scala/Java/Kotlin DSLs and detailed reports. Apache JMeter provides a GUI-based approach that's widely known but less developer-friendly.

Load tests should simulate realistic user behavior, not just hitting endpoints repeatedly. User journeys should include think time between actions, variable request patterns, and realistic data usage. Scripting realistic scenarios ensures tests validate actual user experience, not just theoretical throughput.

Testing at expected load validates that the system meets performance requirements under normal conditions. This baseline establishes current performance and identifies any immediate problems. If the system fails at expected load, it will certainly fail under peak conditions.

Testing at 2x expected load validates headroom and identifies bottlenecks before they impact users. Systems should handle 2x load with graceful degradation rather than complete failure. This testing reveals where the system will fail first, enabling proactive optimization.

Testing at breaking point identifies absolute limits and failure modes. Understanding where and how the system fails enables better capacity planning and incident response. Breaking point tests should be run in isolated environments to avoid impacting production.

Load testing requires production-like infrastructure to provide meaningful results. Testing against a development environment with a single database instance doesn't represent production with multiple replicas and load balancers. Infrastructure differences can mask performance problems or create false bottlenecks.

## Performance Benchmarking

Performance benchmarking establishes baseline performance metrics and tracks changes over time. Benchmarks enable comparison between releases, detection of regressions, and validation of optimization efforts.

Baseline benchmarks establish current performance before making changes. These baselines should include key metrics like API latency percentiles, throughput, error rates, and resource utilization. Without baselines, it's impossible to measure improvement or detect regression.

Tracking benchmarks over time reveals performance trends. Gradual degradation may not be noticeable in individual releases but becomes apparent over months. Tracking enables proactive optimization before performance becomes a user-facing problem.

Benchmarking in CI ensures consistent measurement conditions. Running benchmarks against every commit or pull request detects regressions immediately, before they reach production. Consistent environments eliminate variables that could affect benchmark results.

Benchmarking requires statistical rigor to account for variability. Multiple runs with statistical analysis (mean, median, percentiles) provide confidence in results. Outliers should be investigated but may not represent typical performance.

Comparing benchmarks between releases quantifies the impact of changes. A 10% improvement in latency or a 20% increase in throughput provides concrete evidence of optimization success. Without comparison, optimizations may not be recognized or may introduce regressions.

## Frontend Performance Testing

Frontend performance testing validates that web applications meet Core Web Vitals targets and provide responsive user experiences. Testing encompasses bundle size, rendering performance, and real user metrics.

Lighthouse CI integrates automated performance audits into CI pipelines, failing builds that don't meet score thresholds. Lighthouse measures Core Web Vitals (LCP, INP, CLS), performance score, accessibility, best practices, and SEO. CI integration ensures performance regressions are caught before production deployment.

Bundle size checks prevent gradual size creep by failing builds when bundles exceed defined budgets. Tools like bundlesize and size-limit compare bundle sizes against budgets, enabling teams to make informed decisions about new dependencies. Budgets should be set based on target network conditions and device capabilities.

Core Web Vitals monitoring captures real user metrics (RUM) to understand actual user experience. Synthetic tests validate that performance is possible, but RUM validates that performance is delivered. RUM data reveals performance differences across devices, networks, and geographic locations.

Rendering performance testing measures frame rates, layout shift, and JavaScript execution time. Chrome DevTools Performance tab provides detailed analysis of rendering bottlenecks, enabling optimization of expensive operations. Profiling identifies functions that consume excessive CPU time or cause layout thrashing.

Visual regression testing ensures that performance optimizations don't introduce visual bugs. Tools like Percy and Chromatic capture screenshots and compare them between releases, detecting unintended visual changes. This is particularly important when optimizing rendering performance, as changes can affect visual output.

## Database Query Performance Testing

Database query performance testing identifies slow queries and validates optimization efforts. Testing requires production-like data volumes and realistic query patterns.

Slow query logs capture queries that exceed threshold execution times, identifying problematic queries in production. Enabling slow query logging in PostgreSQL with log_min_duration_statement reveals queries that need optimization. Regular analysis of slow query logs prevents performance problems from accumulating.

EXPLAIN ANALYZE provides query execution plans and actual execution times, revealing how PostgreSQL executes queries. Sequential scans, expensive sorts, and missing indexes become apparent in execution plans. Running EXPLAIN ANALYZE on critical queries during development prevents slow queries from reaching production.

Testing with production-like data volumes ensures queries perform well with realistic data sizes. A query that's fast with 10 rows may be slow with 10 million rows. Test databases should mirror production data volumes and distributions to provide meaningful performance validation.

Query performance testing should cover all query patterns, not just happy paths. Edge cases, error conditions, and boundary values may trigger different query plans or performance characteristics. Comprehensive testing ensures performance is consistent across all scenarios.

Index effectiveness testing validates that indexes improve query performance. Creating an index should measurably improve query execution time, and the improvement should justify the index's maintenance cost. Testing index effectiveness prevents creating unnecessary indexes that slow writes without improving reads.

## API Latency Testing

API latency testing measures response time percentiles to ensure endpoints meet performance requirements. Latency testing validates that optimizations improve response times and detects regressions.

Measuring p50, p95, and p99 latency provides a complete picture of response time distribution. p50 (median) represents typical performance, p95 represents the experience of most users, and p99 represents edge cases. Monitoring percentiles ensures performance is good for all users, not just the majority.

Setting Service Level Objectives (SLOs) defines acceptable latency thresholds. An SLO of "p95 latency under 500ms" provides a clear target for optimization efforts. SLOs should be based on user experience requirements, not arbitrary technical limits.

Alerting on SLO breaches enables proactive response before users are impacted. Latency alerts should trigger investigation and optimization efforts, not just monitoring. Automated alerting ensures performance problems are addressed promptly.

Testing latency under load reveals how response times degrade as load increases. Latency often degrades non-linearly under load—a system with 50ms latency at low load may have 500ms latency at high load. Understanding this relationship enables better capacity planning.

Latency testing should cover all endpoints, not just critical ones. Non-critical endpoints may not impact primary user flows, but poor performance still affects user experience. Comprehensive latency testing ensures consistent performance across the entire API.

## Stress Testing

Stress testing pushes systems beyond expected limits to identify breaking points and failure modes. Understanding where and how systems fail enables better capacity planning and incident response.

Testing beyond expected limits reveals absolute capacity and failure modes. A system that handles 1000 requests per second may fail at 2000 requests per second, and understanding the failure mode (database connections, thread pool exhaustion, memory limits) enables better planning.

Identifying the weakest link reveals where optimization efforts should focus. If database connections exhaust before CPU or memory limits are reached, connection pooling optimization provides more benefit than CPU optimization. Stress testing reveals these priorities.

Failure mode analysis determines how systems fail—graceful degradation or complete failure. Systems that degrade gracefully (slower responses, reduced functionality) provide better user experience than systems that fail completely (errors, timeouts). Understanding failure modes enables architectural improvements.

Recovery testing validates that systems recover after stress conditions. Systems should return to normal operation after load decreases, without requiring manual intervention. Recovery testing ensures systems are resilient, not just performant.

Stress testing should be run in isolated environments to avoid impacting production. Stress tests can generate significant load and may cause performance degradation or failures. Isolated environments prevent stress testing from affecting real users.

## Soak Testing

Soak testing runs systems at moderate load for extended periods (hours or days) to identify resource leaks and long-term performance degradation. Soak testing reveals problems that only appear under sustained load.

Memory leaks cause memory usage to gradually increase over time, eventually exhausting available memory and causing failures. Soak testing with memory profiling reveals gradual memory growth that may not be apparent in short-duration tests. Identifying and fixing memory leaks prevents production incidents.

Connection leaks cause connection pools to gradually exhaust, eventually preventing new connections and causing failures. Soak testing with connection monitoring reveals connection leaks that may not be apparent in short-duration tests. Proper connection management prevents connection leaks.

Resource exhaustion occurs when systems gradually consume resources (file handles, threads, database connections) without releasing them. Soak testing reveals resource exhaustion that may not be apparent in short-duration tests. Proper resource management prevents exhaustion.

Garbage collection pauses may become problematic under sustained load, causing periodic latency spikes. Soak testing with GC profiling reveals GC pause patterns that may not be apparent in short-duration tests. GC tuning can mitigate problematic pause patterns.

Performance degradation over time may occur due to cache warming, database query plan changes, or resource fragmentation. Soak testing reveals gradual performance changes that may not be apparent in short-duration tests. Monitoring performance trends enables proactive optimization.

## Profiling

Profiling identifies performance bottlenecks by measuring where applications spend CPU time and memory. Profiling enables data-driven optimization by revealing actual bottlenecks rather than assumed ones.

JVM profiling with async-profiler and Java Flight Recorder (JFR) reveals CPU and memory hotspots in Java applications. CPU profiling identifies functions that consume excessive CPU time, enabling optimization of hot paths. Memory profiling identifies memory allocations and leaks, enabling memory optimization.

Flame graphs visualize CPU time distribution, making it easy to identify performance bottlenecks. The width of each function in a flame graph represents CPU time, enabling quick identification of hot paths. Interactive flame graphs enable drilling down into specific functions for detailed analysis.

Browser DevTools Performance tab provides detailed analysis of frontend performance, including rendering, scripting, and network activity. Performance recordings reveal frame drops, layout shifts, and expensive JavaScript operations. Profiling frontend performance enables optimization of rendering and scripting bottlenecks.

Application Performance Monitoring (APM) tools like Datadog APM and New Relic provide continuous profiling in production, identifying performance problems as they occur. APM tools automatically instrument applications to collect performance data without manual profiling setup. Continuous profiling enables proactive performance optimization.

Profiling should be performed on production-like workloads to provide meaningful results. Profiling development workloads may not reveal production bottlenecks, as workload characteristics differ. Production profiling provides the most accurate performance insights.

## Regression Testing

Performance regression testing compares performance metrics between releases to detect when changes degrade performance. Regression testing prevents performance problems from reaching production.

Comparing metrics between releases quantifies the impact of changes. A 10% increase in latency or a 20% decrease in throughput indicates a performance regression that should be investigated. Without comparison, regressions may go unnoticed until users are impacted.

Automated regression testing in CI detects performance regressions before production deployment. Performance tests that fail when metrics degrade prevent regressions from reaching production. CI integration ensures performance is considered in every release.

Establishing performance budgets defines acceptable performance thresholds. Budgets prevent gradual degradation by failing builds that exceed thresholds. Budgets should be based on user experience requirements, not arbitrary technical limits.

Tracking performance trends over time reveals gradual degradation that may not be apparent in individual releases. A 5% performance degradation per release may not be noticeable individually but becomes significant over months. Trend tracking enables proactive optimization.

Performance regression testing should cover all performance-critical paths, not just happy paths. Edge cases and error conditions may have different performance characteristics, and regressions may only appear in specific scenarios. Comprehensive testing ensures performance is maintained across all scenarios.
