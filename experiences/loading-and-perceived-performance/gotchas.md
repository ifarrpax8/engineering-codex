---
title: Loading and Perceived Performance -- Gotchas
type: experience
last_updated: 2026-02-09
---

# Loading and Perceived Performance -- Gotchas

## Contents

- [Skeleton Screens That Don't Match Layout](#skeleton-screens-that-dont-match-layout)
- [Optimistic Updates Without Rollback](#optimistic-updates-without-rollback)
- [Infinite Loading Spinners](#infinite-loading-spinners)
- [Layout Shift from Lazy-Loaded Content](#layout-shift-from-lazy-loaded-content)
- [Prefetching Too Aggressively](#prefetching-too-aggressively)
- [Stale-While-Revalidate Showing Very Old Data](#stale-while-revalidate-showing-very-old-data)
- [Suspense Waterfall](#suspense-waterfall)
- [Loading State Flicker](#loading-state-flicker)
- [Service Worker Serving Stale Content](#service-worker-serving-stale-content)

## Skeleton Screens That Don't Match Layout

Skeleton screens that don't match the actual content layout cause jarring layout shifts when content loads.

**❌ Bad: Mismatched Skeleton**
```vue
<template>
  <!-- Skeleton: 3 items in a row -->
  <div v-if="loading" class="skeleton-grid">
    <div v-for="i in 3" :key="i" class="skeleton-item"></div>
  </div>
  
  <!-- Actual: 4 items in a row -->
  <div v-else class="product-grid">
    <div v-for="product in products" :key="product.id" class="product-item">
      {{ product.name }}
    </div>
  </div>
</template>
```

**✅ Good: Matching Skeleton**
```vue
<template>
  <!-- Skeleton matches actual layout exactly -->
  <div v-if="loading" class="product-grid">
    <div v-for="i in 4" :key="i" class="product-item skeleton-item">
      <div class="skeleton-image"></div>
      <div class="skeleton-text"></div>
    </div>
  </div>
  
  <div v-else class="product-grid">
    <div v-for="product in products" :key="product.id" class="product-item">
      <img :src="product.image" />
      <div>{{ product.name }}</div>
    </div>
  </div>
</template>
```

**How to Avoid:**
- Measure actual content dimensions and match skeleton exactly
- Use same CSS classes for skeleton and content containers
- Test skeleton-to-content transition visually
- Use layout shift detection tools (CLS measurement)

## Optimistic Updates Without Rollback

Optimistic updates that don't handle rollback leave the UI in an inconsistent state when server requests fail.

**❌ Bad: No Rollback**
```tsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  
  const addTodo = async (text) => {
    // Optimistic update
    setTodos([...todos, { id: Date.now(), text }]);
    
    // Server request (no error handling)
    await api.createTodo({ text });
    // If this fails, UI shows todo but server doesn't have it
  };
  
  return <div>{/* UI */}</div>;
}
```

**✅ Good: With Rollback**
```tsx
function TodoList() {
  const queryClient = useQueryClient();
  
  const addTodo = useMutation({
    mutationFn: api.createTodo,
    onMutate: async (newTodo) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      const previousTodos = queryClient.getQueryData(['todos']);
      
      queryClient.setQueryData(['todos'], (old) => [
        ...old,
        { ...newTodo, id: `temp-${Date.now()}` }
      ]);
      
      return { previousTodos };
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      queryClient.setQueryData(['todos'], context.previousTodos);
      showError('Failed to add todo');
    }
  });
  
  return <div>{/* UI */}</div>;
}
```

**How to Avoid:**
- Always implement error handling for optimistic updates
- Store previous state for rollback
- Show error messages when rollback occurs
- Test failure scenarios

## Infinite Loading Spinners

Loading spinners that never resolve (no timeout, no error state) leave users stuck with no way to proceed.

**❌ Bad: Infinite Spinner**
```tsx
function ProductList() {
  const { data, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    // No timeout, no error handling
  });
  
  if (isLoading) {
    return <Spinner />; // Could spin forever
  }
  
  return <div>{/* Products */}</div>;
}
```

**✅ Good: With Timeout and Error State**
```tsx
function ProductList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    retry: 2,
    retryDelay: 1000,
    staleTime: 5 * 60 * 1000,
  });
  
  if (isLoading) {
    return (
      <div>
        <Spinner />
        <p>Loading products...</p>
        {/* Show timeout warning after 10 seconds */}
        <TimeoutWarning after={10000} />
      </div>
    );
  }
  
  if (isError) {
    return (
      <div>
        <ErrorMessage error={error} />
        <button onClick={() => refetch()}>Retry</button>
      </div>
    );
  }
  
  return <div>{/* Products */}</div>;
}
```

**How to Avoid:**
- Set timeouts for all loading operations
- Show error states when requests fail
- Provide retry mechanisms
- Show progress indicators for long operations
- Implement request cancellation

## Layout Shift from Lazy-Loaded Content

Lazy-loaded content that doesn't reserve space causes cumulative layout shift (CLS penalty).

**❌ Bad: No Space Reserved**
```tsx
function ProductCard({ product }) {
  return (
    <div>
      {product.image && (
        <img 
          src={product.image} 
          alt="Product"
          loading="lazy"
          // No dimensions, causes layout shift when image loads
        />
      )}
    </div>
  );
}
```

**✅ Good: Space Reserved**
```tsx
function ProductCard({ product }) {
  return (
    <div style={{ minHeight: '400px' }}>
      {product.image ? (
        <img 
          src={product.image} 
          alt="Product"
          loading="lazy"
          width={300}
          height={300}
          style={{ objectFit: 'cover' }}
        />
      ) : (
        <div 
          style={{ 
            width: '300px', 
            height: '300px',
            backgroundColor: '#f0f0f0'
          }}
        >
          {/* Placeholder maintains space */}
        </div>
      )}
    </div>
  );
}
```

**How to Avoid:**
- Set `width` and `height` attributes on images
- Use `aspect-ratio` CSS property
- Reserve space for lazy-loaded content
- Use skeleton screens that match final layout
- Measure CLS and fix layout shifts

## Prefetching Too Aggressively

Prefetching everything wastes bandwidth, especially on mobile, and can slow down the current page.

**❌ Bad: Aggressive Prefetching**
```tsx
function App() {
  useEffect(() => {
    // Prefetch all routes on page load
    prefetchRoute('/products');
    prefetchRoute('/about');
    prefetchRoute('/contact');
    prefetchRoute('/dashboard');
    // Wastes bandwidth, especially on mobile
  }, []);
  
  return <div>{/* App */}</div>;
}
```

**✅ Good: Smart Prefetching**
```tsx
function Navigation() {
  return (
    <nav>
      <Link 
        to="/products"
        onMouseEnter={() => {
          // Prefetch on hover, not on page load
          queryClient.prefetchQuery(['products'], fetchProducts);
        }}
      >
        Products
      </Link>
    </nav>
  );
}

// Or prefetch when near viewport
function ProductCard({ productId }) {
  const ref = usePrefetchOnViewport(
    ['product', productId],
    () => fetchProduct(productId),
    { rootMargin: '200px' }
  );
  
  return <div ref={ref}>{/* Card */}</div>;
}
```

**How to Avoid:**
- Prefetch on user intent (hover, focus) not on page load
- Use viewport-based prefetching (Intersection Observer)
- Respect user preferences (data saver mode)
- Prefetch only likely next pages
- Cancel prefetch if user navigates away

## Stale-While-Revalidate Showing Very Old Data

Stale-while-revalidate can show very old data if `staleTime` is too long or cache isn't invalidated properly.

**❌ Bad: Too Long StaleTime**
```tsx
function ProductList() {
  const { data } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    staleTime: 24 * 60 * 60 * 1000, // 24 hours - too long!
    // Users see day-old data
  });
  
  return <div>{/* Products */}</div>;
}
```

**✅ Good: Appropriate StaleTime**
```tsx
function ProductList() {
  const { data } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    staleTime: 5 * 60 * 1000, // 5 minutes - reasonable
    refetchOnWindowFocus: true, // Revalidate when user returns
    refetchOnReconnect: true, // Revalidate when network reconnects
  });
  
  return <div>{/* Products */}</div>;
}
```

**How to Avoid:**
- Set appropriate `staleTime` based on data freshness requirements
- Use `refetchOnWindowFocus` for frequently changing data
- Invalidate cache after mutations
- Show loading indicator when data is stale and refetching
- Consider data type: static content can be stale longer than user-specific data

## Suspense Waterfall

Nested Suspense boundaries can cause loading waterfalls where components load sequentially instead of in parallel.

**❌ Bad: Sequential Loading (Waterfall)**
```tsx
function ProductPage({ productId }) {
  // This loads first
  const { data: product } = useQuery(['product', productId], () =>
    fetchProduct(productId)
  );
  
  // This waits for product to load first (waterfall)
  const { data: reviews } = useQuery(['reviews', product?.id], () =>
    fetchReviews(product.id),
    { enabled: !!product } // Waits for product
  );
  
  return (
    <div>
      <ProductDetails product={product} />
      <Reviews reviews={reviews} />
    </div>
  );
}
```

**✅ Good: Parallel Loading**
```tsx
function ProductPage({ productId }) {
  // Load in parallel, not sequentially
  const { data: product } = useQuery(['product', productId], () =>
    fetchProduct(productId)
  );
  
  // Load reviews in parallel (don't wait for product)
  const { data: reviews } = useQuery(['reviews', productId], () =>
    fetchReviews(productId) // Use productId directly
  );
  
  return (
    <div>
      <Suspense fallback={<ProductDetailsSkeleton />}>
        <ProductDetails product={product} />
      </Suspense>
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews reviews={reviews} />
      </Suspense>
    </div>
  );
}
```

**How to Avoid:**
- Load data in parallel, not sequentially
- Don't use `enabled` to create dependencies unless necessary
- Use Suspense boundaries for independent loading states
- Prefetch related data together
- Measure loading times and identify waterfalls

## Loading State Flicker

Content that loads faster than the skeleton appears causes a flicker where skeleton briefly appears then disappears.

**❌ Bad: Flicker**
```tsx
function ProductList() {
  const { data, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts, // Fast API, loads in 50ms
  });
  
  if (isLoading) {
    return <ProductListSkeleton />; // Shows for 50ms, causes flicker
  }
  
  return <div>{/* Products */}</div>;
}
```

**✅ Good: Minimum Display Time**
```tsx
function ProductList() {
  const { data, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
  });
  
  const [showSkeleton, setShowSkeleton] = useState(true);
  
  useEffect(() => {
    if (!isLoading) {
      // Minimum display time to prevent flicker
      const timer = setTimeout(() => {
        setShowSkeleton(false);
      }, 300); // Show skeleton for at least 300ms
      
      return () => clearTimeout(timer);
    } else {
      setShowSkeleton(true);
    }
  }, [isLoading]);
  
  if (showSkeleton) {
    return <ProductListSkeleton />;
  }
  
  return <div>{/* Products */}</div>;
}
```

**How to Avoid:**
- Set minimum display time for loading states (200-300ms)
- Use CSS transitions to smooth skeleton-to-content transition
- Don't show skeleton for very fast loads (<100ms)
- Test on fast networks to catch flicker

## Service Worker Serving Stale Content

Service workers can serve stale content after deployment, causing users to see old versions of the app.

**❌ Bad: No Cache Invalidation**
```javascript
// service-worker.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('app-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/app.js',
        '/styles.css'
      ]);
    })
  );
});

// Old cache never invalidated, users see old app after deployment
```

**✅ Good: Cache Versioning and Invalidation**
```javascript
// service-worker.js
const CACHE_VERSION = 'app-v2'; // Update on deployment

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      return cache.addAll([
        '/',
        '/app.js',
        '/styles.css'
      ]);
    }).then(() => {
      // Delete old caches
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_VERSION)
          .map((name) => caches.delete(name))
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});
```

**How to Avoid:**
- Version cache names (include build hash or version)
- Delete old caches on activation
- Use network-first strategy for HTML
- Implement cache-busting for static assets
- Test cache invalidation after deployments
