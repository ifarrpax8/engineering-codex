# Performance -- Best Practices

## Contents

- [Measure Before Optimizing](#measure-before-optimizing)
- [Set Performance Budgets](#set-performance-budgets)
- [Optimize the Critical Path First](#optimize-the-critical-path-first)
- [Cache Aggressively, Invalidate Precisely](#cache-aggressively-invalidate-precisely)
- [Lazy Load Everything Not Immediately Visible](#lazy-load-everything-not-immediately-visible)
- [Paginate All Collections](#paginate-all-collections)
- [Use Async Processing for Non-Critical Work](#use-async-processing-for-non-critical-work)
- [Monitor in Production, Not Just in Tests](#monitor-in-production-not-just-in-tests)
- [Stack-Specific Callouts](#stack-specific-callouts)

Performance optimization is most effective when guided by measurement. These practices apply across the stack, with specific callouts for Vue 3, React, Spring Boot, PostgreSQL, and Vite where the technology materially affects the approach.

## Measure Before Optimizing

Profiling reveals actual bottlenecks. Developer intuition about performance is often wrong -- the code that looks slow may execute in microseconds, while an innocent-looking ORM call may fire hundreds of queries.

Use profiling tools before writing any optimization code:
- **Backend**: async-profiler and Java Flight Recorder (JFR) for CPU and memory hotspots. Flame graphs visualize where time is spent.
- **Frontend**: Chrome DevTools Performance tab for rendering and scripting bottlenecks. Lighthouse for overall page performance scoring.
- **Database**: `EXPLAIN ANALYZE` for query plans. `pg_stat_statements` for identifying the most time-consuming queries across all requests.

Optimize the top bottleneck first. Re-measure after each change. Stop when performance meets the defined budget.

## Set Performance Budgets

Define measurable limits and enforce them in CI. Budgets prevent gradual degradation -- each individual change may be small, but cumulative impact is significant.

Recommended budgets:
- **Bundle size**: main bundle < 200-250KB gzipped. Total JavaScript < 500KB gzipped.
- **API latency**: p95 < 500ms for user-facing endpoints. p99 < 2s.
- **Core Web Vitals**: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- **Time to First Byte (TTFB)**: < 200ms for API responses, < 800ms for page loads.

Fail CI builds when budgets are exceeded. This forces the team to address performance regressions immediately rather than accumulating debt.

## Optimize the Critical Path First

Not all code paths are equally important. Identify the user-facing paths that matter most -- initial page load, primary user workflows, high-traffic endpoints -- and optimize those first.

Background jobs, admin pages, and rarely-used features can be slower without impacting user experience. Focus optimization effort where it has the greatest user impact per engineering hour invested.

## Cache Aggressively, Invalidate Precisely

Caching is the most impactful performance optimization for read-heavy applications. But every cached value needs a clear invalidation strategy.

- **Static assets**: long Cache-Control max-age (1 year) with content-hash filenames for cache busting. Vite handles this automatically.
- **API responses**: short TTL (seconds to minutes) for data that changes frequently. Longer TTL (hours) for reference data. Explicit invalidation after mutations.

**Kotlin (Spring Boot):**
```kotlin
@Service
class ProductService(
    private val productRepository: ProductRepository
) {
    @Cacheable(value = ["products"], key = "#id", unless = "#result == null")
    fun getProduct(id: Long): Product? {
        return productRepository.findById(id)
    }
    
    @CacheEvict(value = ["products"], key = "#product.id")
    fun updateProduct(product: Product) {
        productRepository.save(product)
    }
}

// application.yml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000  # 1 hour in milliseconds
```

**Java (Spring Boot):**
```java
@Service
public class ProductService {
    private final ProductRepository productRepository;
    
    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }
    
    @Cacheable(value = "products", key = "#id", unless = "#result == null")
    public Product getProduct(Long id) {
        return productRepository.findById(id).orElse(null);
    }
    
    @CacheEvict(value = "products", key = "#product.id")
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }
}
```

- **Computed values**: cache expensive computations (reports, aggregations) with TTL appropriate to the data freshness requirement.
- **Database queries**: Redis cache-aside for expensive or frequently repeated queries. Monitor cache hit rate to verify the cache is effective.

Stale data is worse than slow data for most business operations. When in doubt, use shorter TTLs and explicit invalidation.

## Lazy Load Everything Not Immediately Visible

Only load resources the user needs right now. Defer everything else.

- **Routes**: every route should use dynamic imports. This is the single highest-impact code splitting optimization.

**Vue 3:**
```typescript
// router.ts
import { defineAsyncComponent } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/dashboard',
      component: defineAsyncComponent(() => import('./views/Dashboard.vue'))
    },
    {
      path: '/reports',
      component: defineAsyncComponent(() => import('./views/Reports.vue'))
    }
  ]
})
```

**React:**
```typescript
// App.tsx
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

const Dashboard = lazy(() => import('./views/Dashboard'))
const Reports = lazy(() => import('./views/Reports'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
```

- **Components**: heavy components (charts, rich text editors, PDF viewers) should be loaded on demand with `defineAsyncComponent` (Vue) or `React.lazy`.
- **Images**: use `loading="lazy"` for below-the-fold images. Use responsive images with `srcset` to serve appropriately sized images.

```html
<!-- Responsive image with lazy loading -->
<img
  srcset="
    /images/hero-400w.jpg 400w,
    /images/hero-800w.jpg 800w,
    /images/hero-1200w.jpg 1200w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  src="/images/hero-800w.jpg"
  alt="Hero image"
  loading="lazy"
/>
```

- **Data**: don't fetch all data on page load. Fetch data for the current view and prefetch data for likely next navigations.

## Paginate All Collections

Never return unbounded lists from APIs. Default page sizes of 20-50 items are appropriate for most use cases. See the [API Design facet](../api-design/) for pagination patterns.

On the frontend, use virtualization for rendering large lists. Virtual scrolling renders only visible items (typically 20-50) regardless of total list size. Libraries: `@tanstack/react-virtual` (React), `vue-virtual-scroller` (Vue).

## Use Async Processing for Non-Critical Work

Move work off the request path when the user doesn't need an immediate result. Process asynchronously and notify when complete.

Examples: sending emails, generating reports, processing file uploads, syncing data with external systems, updating search indexes.

Return `202 Accepted` with a status URL for long-running operations. Use message queues (Kafka, RabbitMQ) for reliable background processing.

## Monitor in Production, Not Just in Tests

Synthetic tests and load tests don't capture real-world conditions: diverse devices, varying network quality, geographic latency, production data volumes, concurrent users.

Use Real User Monitoring (RUM) to understand actual user experience. Collect Core Web Vitals from real browsers. Monitor API latency percentiles from production traffic. Compare against performance budgets continuously, not just at release time.

## Stack-Specific Callouts

### Vue 3

- Use `computed` properties for derived values -- they're cached and only recalculate when dependencies change.
- Use `v-once` for content that never changes after initial render (static headers, legal text).
- Use `v-memo` to skip re-rendering of expensive list items when their data hasn't changed.
- Use `shallowRef` / `shallowReactive` for large objects where you don't need deep reactivity. Deep reactivity on objects with thousands of properties has measurable overhead.
- Use `<KeepAlive>` to cache component instances when switching between views, preserving state and avoiding re-initialization.

### React

- Use `React.memo` for components that re-render unnecessarily with the same props. Measure with React DevTools Profiler before adding -- not every component benefits.
- Use `useMemo` for expensive computations that shouldn't re-run on every render. Use `useCallback` for callback functions passed to memoized children. Both should be applied based on measurement, not intuition.
- Use virtualization (`@tanstack/react-virtual`) for lists with more than 50-100 items. Don't render 10,000 DOM nodes.
- Use `React.lazy` + `<Suspense>` for code splitting at the route and component level.

### Spring Boot

- Use `@Cacheable` with Spring Cache + Redis for method-level caching of expensive operations. Configure cache names and TTLs explicitly.
- Use `@Async` or message queues to move non-critical work off the request thread.
- Use virtual threads (Java 21+) for I/O-bound workloads. Virtual threads allow millions of concurrent tasks without the overhead of platform threads.
- Use `@Transactional(readOnly = true)` on query methods. This provides Hibernate optimization hints and can route queries to read replicas.
- Use Spring WebFlux with coroutines (Kotlin) for high-concurrency, I/O-bound services where non-blocking is critical.

### PostgreSQL

- Use `EXPLAIN ANALYZE` on every new or modified query during development. Verify the query planner uses indexes as expected.
- Use `pg_stat_statements` to identify the most time-consuming queries in production. Optimize the queries that consume the most total time (frequency × duration).
- Use partial indexes for queries that filter on common conditions (`WHERE status = 'active'`).
- Use materialized views for dashboard and reporting queries that aggregate large datasets. Refresh on a schedule, not on every query.
- Use `CREATE INDEX CONCURRENTLY` to add indexes without locking the table.

### Vite

- Configure code splitting with `build.rollupOptions.output.manualChunks` to control vendor splitting. Separate large vendor libraries into their own chunks for better caching.
- Use `build-plugin-visualizer` (rollup-plugin-visualizer) to analyze the production bundle. Identify large dependencies and evaluate alternatives.
- Enable `build.sourcemap` for production to enable meaningful error stack traces in error tracking tools (Sentry). Use hidden source maps to keep them from being publicly accessible.
- Configure `optimizeDeps` to pre-bundle heavy dependencies for faster development server startup.
