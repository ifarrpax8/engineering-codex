---
title: Loading and Perceived Performance -- Architecture
type: experience
last_updated: 2026-02-09
---

# Loading and Perceived Performance -- Architecture

## Contents

- [Skeleton Screens](#skeleton-screens)
- [Optimistic Updates](#optimistic-updates)
- [Progressive Loading](#progressive-loading)
- [Streaming SSR and Progressive Hydration](#streaming-ssr-and-progressive-hydration)
- [Suspense Boundaries](#suspense-boundaries)
- [Prefetching Strategies](#prefetching-strategies)
- [Service Worker Caching](#service-worker-caching)
- [Above-the-Fold Prioritization](#above-the-fold-prioritization)
- [Lazy Loading vs Eager Loading](#lazy-loading-vs-eager-loading)
- [Stale-While-Revalidate Pattern](#stale-while-revalidate-pattern)

## Skeleton Screens

Skeleton screens are content-shaped placeholders that appear while data loads. They set user expectations about what content is coming and reduce perceived loading time.

**Implementation Patterns**

**Vue 3 Example:**
```vue
<template>
  <div v-if="loading" class="skeleton-container">
    <div class="skeleton-header shimmer"></div>
    <div class="skeleton-content">
      <div class="skeleton-line shimmer" v-for="i in 3" :key="i"></div>
    </div>
  </div>
  <div v-else>
    <!-- Actual content -->
  </div>
</template>

<style scoped>
.shimmer {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
```

**React Example:**
```tsx
function UserProfileSkeleton() {
  return (
    <div className="skeleton-container">
      <div className="skeleton-avatar shimmer" />
      <div className="skeleton-content">
        <div className="skeleton-line shimmer" style={{ width: '60%' }} />
        <div className="skeleton-line shimmer" style={{ width: '80%' }} />
      </div>
    </div>
  );
}

function UserProfile({ userId }) {
  const { data, isLoading } = useUser(userId);
  
  if (isLoading) return <UserProfileSkeleton />;
  return <div>{/* Actual content */}</div>;
}
```

**Key Principles:**
- Match actual content layout exactly (same dimensions, spacing)
- Use subtle shimmer animation (not distracting)
- Show skeleton immediately (don't wait for network request)
- Replace skeleton smoothly (fade transition, not instant swap)

## Optimistic Updates

Optimistic updates modify the UI immediately, before server confirmation. If the server request fails, rollback the change and show an error.

**Pattern Structure:**
1. Update UI optimistically (immediate)
2. Send request to server (background)
3. Reconcile with server response (update if needed)
4. Rollback on failure (show error, revert UI)

**Vue 3 Example:**
```vue
<script setup>
import { ref } from 'vue';

const items = ref([{ id: 1, name: 'Item 1' }]);
const optimisticIds = ref(new Set());

async function addItem(name) {
  // 1. Optimistic update
  const tempId = `temp-${Date.now()}`;
  items.value.push({ id: tempId, name });
  optimisticIds.value.add(tempId);
  
  try {
    // 2. Server request
    const response = await api.createItem({ name });
    
    // 3. Reconcile
    const index = items.value.findIndex(item => item.id === tempId);
    items.value[index] = response.data;
    optimisticIds.value.delete(tempId);
  } catch (error) {
    // 4. Rollback
    items.value = items.value.filter(item => item.id !== tempId);
    optimisticIds.value.delete(tempId);
    showError('Failed to add item');
  }
}
</script>
```

**React Example with TanStack Query:**
```tsx
function TodoList() {
  const queryClient = useQueryClient();
  
  const addTodo = useMutation({
    mutationFn: api.createTodo,
    onMutate: async (newTodo) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      
      // Snapshot previous value
      const previousTodos = queryClient.getQueryData(['todos']);
      
      // Optimistically update
      queryClient.setQueryData(['todos'], (old) => [
        ...old,
        { ...newTodo, id: `temp-${Date.now()}` }
      ]);
      
      return { previousTodos };
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      queryClient.setQueryData(['todos'], context.previousTodos);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    }
  });
  
  return <div>{/* UI */}</div>;
}
```

**When to Use:**
- High-frequency actions (likes, favorites, toggles)
- Actions with high success probability
- Actions where rollback is straightforward
- Actions that benefit from instant feedback

**When to Avoid:**
- Critical financial transactions
- Actions with complex validation
- Actions where rollback is difficult
- Actions with low success probability

## Progressive Loading

Progressive loading prioritizes above-the-fold content, loading below-the-fold content lazily or after initial render.

**Above-the-Fold First:**
```tsx
// React: Load critical content first
function ProductPage({ productId }) {
  const { data: product } = useProduct(productId); // Critical
  const { data: reviews } = useReviews(productId, { 
    enabled: false // Load after initial render
  });
  
  useEffect(() => {
    // Load reviews after page is interactive
    setTimeout(() => {
      queryClient.prefetchQuery(['reviews', productId]);
    }, 100);
  }, [productId]);
  
  return (
    <div>
      <ProductHeader product={product} />
      <ProductDetails product={product} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews reviews={reviews} />
      </Suspense>
    </div>
  );
}
```

**Below-the-Fold Lazy:**
```vue
<!-- Vue 3: Lazy load below-the-fold -->
<template>
  <div>
    <ProductHeader :product="product" />
    <ProductDetails :product="product" />
    
    <!-- Lazy load reviews when in viewport -->
    <LazyReviews 
      v-if="showReviews"
      :product-id="productId"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useIntersectionObserver } from '@vueuse/core';

const showReviews = ref(false);
const reviewsSection = ref(null);

onMounted(() => {
  useIntersectionObserver(
    reviewsSection,
    ([{ isIntersecting }]) => {
      if (isIntersecting) showReviews.value = true;
    },
    { rootMargin: '200px' } // Start loading 200px before visible
  );
});
</script>
```

## Streaming SSR and Progressive Hydration

Streaming Server-Side Rendering sends HTML in chunks, allowing the browser to render content progressively. Progressive hydration hydrates components as they become interactive.

**Next.js Streaming Example:**
```tsx
// app/product/[id]/page.tsx
import { Suspense } from 'react';

export default function ProductPage({ params }) {
  return (
    <div>
      <ProductHeader productId={params.id} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews productId={params.id} />
      </Suspense>
    </div>
  );
}

// Reviews component streams separately
async function Reviews({ productId }) {
  const reviews = await fetchReviews(productId); // Can be slow
  return <div>{/* Reviews */}</div>;
}
```

**Nuxt 3 Streaming Example:**
```vue
<!-- pages/product/[id].vue -->
<template>
  <div>
    <ProductHeader :product="product" />
    <LazyReviews :product-id="productId" />
  </div>
</template>

<script setup>
const { id } = useRoute().params;
const { data: product } = await useFetch(`/api/products/${id}`);
</script>
```

**Benefits:**
- Faster Time to First Byte (TTFB)
- Progressive content rendering
- Better perceived performance
- Improved Core Web Vitals

## Suspense Boundaries

Suspense boundaries define fallback UI for async components. They prevent loading waterfalls and enable progressive rendering.

**React Suspense:**
```tsx
function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Router>
        <Routes>
          <Route path="/products" element={
            <Suspense fallback={<ProductListSkeleton />}>
              <ProductList />
            </Suspense>
          } />
        </Routes>
      </Router>
    </Suspense>
  );
}

// Lazy-loaded route
const ProductList = lazy(() => import('./ProductList'));

// Component with async data
function ProductList() {
  const { data } = useSuspenseQuery(['products'], fetchProducts);
  return <div>{/* Products */}</div>;
}
```

**Vue 3 Suspense:**
```vue
<template>
  <Suspense>
    <template #default>
      <AsyncComponent />
    </template>
    <template #fallback>
      <LoadingSkeleton />
    </template>
  </Suspense>
</template>

<script setup>
import { defineAsyncComponent } from 'vue';

const AsyncComponent = defineAsyncComponent(() => 
  import('./HeavyComponent.vue')
);
</script>
```

**Avoiding Waterfalls:**
```tsx
// ❌ Bad: Sequential loading (waterfall)
function ProductPage({ id }) {
  const { data: product } = useQuery(['product', id], () => 
    fetchProduct(id)
  );
  // This waits for product to load first
  const { data: reviews } = useQuery(['reviews', product?.id], () =>
    fetchReviews(product.id),
    { enabled: !!product }
  );
}

// ✅ Good: Parallel loading
function ProductPage({ id }) {
  const { data: product } = useQuery(['product', id], () => 
    fetchProduct(id)
  );
  // Load in parallel, not sequentially
  const { data: reviews } = useQuery(['reviews', id], () =>
    fetchReviews(id)
  );
}
```

## Prefetching Strategies

Prefetching loads resources before users need them, making navigation feel instant.

**Route Prefetch:**
```tsx
// Next.js automatic prefetching
<Link href="/products" prefetch>Products</Link>

// React Router with prefetch
<Link 
  to="/products"
  onMouseEnter={() => {
    queryClient.prefetchQuery(['products'], fetchProducts);
  }}
>
  Products
</Link>
```

**Hover-Based Prefetch:**
```vue
<!-- Vue 3: Prefetch on hover -->
<template>
  <router-link
    to="/products"
    @mouseenter="prefetchProducts"
  >
    Products
  </router-link>
</template>

<script setup>
import { useQueryClient } from '@tanstack/vue-query';

const queryClient = useQueryClient();

function prefetchProducts() {
  queryClient.prefetchQuery({
    queryKey: ['products'],
    queryFn: fetchProducts
  });
}
</script>
```

**Viewport-Based Prefetch (Intersection Observer):**
```tsx
function usePrefetchOnViewport(queryKey, queryFn, options = {}) {
  const ref = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          queryClient.prefetchQuery({ queryKey, queryFn });
          observer.disconnect();
        }
      },
      { rootMargin: options.rootMargin || '200px' }
    );
    
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  
  return ref;
}

// Usage
function ProductCard({ productId }) {
  const ref = usePrefetchOnViewport(
    ['product', productId],
    () => fetchProduct(productId)
  );
  
  return <div ref={ref}>{/* Card content */}</div>;
}
```

**Prefetch Considerations:**
- Prefetch on hover (not on page load) to avoid wasting bandwidth
- Use `rootMargin` to prefetch before element is visible
- Cancel prefetch if user navigates away
- Respect user preferences (data saver mode, slow connections)

## Service Worker Caching

Service workers enable offline-first experiences and instant loading of cached content.

**Cache-First for Static Assets:**
```javascript
// service-worker.js
self.addEventListener('fetch', (event) => {
  if (event.request.destination === 'image' || 
      event.request.destination === 'script' ||
      event.request.destination === 'style') {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request).then((response) => {
          const responseClone = response.clone();
          caches.open('static-v1').then((cache) => {
            cache.put(event.request, responseClone);
          });
          return response;
        });
      })
    );
  }
});
```

**Network-First for Dynamic Content:**
```javascript
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const responseClone = response.clone();
          caches.open('api-v1').then((cache) => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
  }
});
```

**Stale-While-Revalidate:**
```javascript
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open('cache-v1').then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });
        return cachedResponse || fetchPromise;
      });
    })
  );
});
```

## Above-the-Fold Prioritization

Prioritize critical resources needed for initial render.

**Critical CSS Inlining:**
```html
<head>
  <!-- Inline critical CSS -->
  <style>
    /* Above-the-fold styles only */
    .header { ... }
    .hero { ... }
  </style>
  
  <!-- Load full CSS asynchronously -->
  <link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
</head>
```

**Resource Hints:**
```html
<head>
  <!-- Preconnect to external domains -->
  <link rel="preconnect" href="https://api.example.com">
  
  <!-- Preload critical resources -->
  <link rel="preload" href="/hero-image.jpg" as="image">
  <link rel="preload" href="/critical-font.woff2" as="font" crossorigin>
  
  <!-- Prefetch likely next page -->
  <link rel="prefetch" href="/products">
</head>
```

**Code Splitting:**
```tsx
// React: Split by route
const ProductPage = lazy(() => import('./ProductPage'));
const AboutPage = lazy(() => import('./AboutPage'));

// Vue 3: Split by route
const ProductPage = () => import('./ProductPage.vue');
const AboutPage = () => import('./AboutPage.vue');
```

## Lazy Loading vs Eager Loading

**Lazy Loading:** Load resources when needed (on-demand)
**Eager Loading:** Load resources immediately (upfront)

**When to Lazy Load:**
- Below-the-fold images
- Non-critical JavaScript (analytics, chat widgets)
- Routes user may not visit
- Heavy components (charts, editors)
- Third-party embeds

**When to Eager Load:**
- Above-the-fold content
- Critical path JavaScript
- Frequently visited routes
- Small, essential components

**Image Lazy Loading:**
```html
<!-- Native lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description">

<!-- Intersection Observer for older browsers -->
<img 
  data-src="image.jpg" 
  class="lazy"
  alt="Description"
>

<script>
const images = document.querySelectorAll('img.lazy');
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      imageObserver.unobserve(img);
    }
  });
});

images.forEach(img => imageObserver.observe(img));
</script>
```

**Component Lazy Loading:**
```tsx
// React: Lazy load heavy components
const Chart = lazy(() => import('./Chart'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <Chart data={data} />
    </Suspense>
  );
}
```

```vue
<!-- Vue 3: Lazy load components -->
<template>
  <Suspense>
    <Chart :data="data" />
  </Suspense>
</template>

<script setup>
import { defineAsyncComponent } from 'vue';

const Chart = defineAsyncComponent(() => import('./Chart.vue'));
</script>
```

## Stale-While-Revalidate Pattern

Show cached (stale) data immediately, then update in the background with fresh data.

**TanStack Query (React):**
```tsx
function ProductList() {
  const { data } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: true, // Revalidate on focus
  });
  
  return <div>{/* Products */}</div>;
}
```

**VueQuery (Vue 3):**
```vue
<script setup>
import { useQuery } from '@tanstack/vue-query';

const { data } = useQuery({
  queryKey: ['products'],
  queryFn: fetchProducts,
  staleTime: 5 * 60 * 1000,
  gcTime: 10 * 60 * 1000,
  refetchOnWindowFocus: true,
});
</script>
```

**Benefits:**
- Instant loading (cached data)
- Always fresh (background updates)
- Reduced server load (fewer requests)
- Better offline experience

**Configuration:**
- `staleTime`: How long data is considered fresh (no refetch)
- `gcTime`: How long unused data stays in cache
- `refetchOnWindowFocus`: Revalidate when window regains focus
- `refetchOnReconnect`: Revalidate when network reconnects
