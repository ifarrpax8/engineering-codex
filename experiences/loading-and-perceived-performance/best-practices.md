---
title: Loading and Perceived Performance -- Best Practices
type: experience
last_updated: 2026-02-09
---

# Loading and Perceived Performance -- Best Practices

## Contents

- [Never Show a Blank Page](#never-show-a-blank-page)
- [Skeleton Screens Over Spinners](#skeleton-screens-over-spinners)
- [Optimistic Updates for Instant Feel](#optimistic-updates-for-instant-feel)
- [Progress Indicators for Long Operations](#progress-indicators-for-long-operations)
- [Content-First Loading Order](#content-first-loading-order)
- [Avoid Cumulative Layout Shift](#avoid-cumulative-layout-shift)
- [Use Stale-While-Revalidate](#use-stale-while-revalidate)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Animation and Transitions](#animation-and-transitions)
- [Accessibility of Loading States](#accessibility-of-loading-states)

## Never Show a Blank Page

Always provide visual feedback during loading. A blank page creates uncertainty and makes users think something is broken.

**✅ Good:**
```vue
<template>
  <div v-if="loading" class="skeleton-screen">
    <!-- Skeleton content -->
  </div>
  <div v-else>
    <!-- Actual content -->
  </div>
</template>
```

```tsx
function ProductList() {
  const { data, isLoading } = useProducts();
  
  if (isLoading) {
    return <ProductListSkeleton />;
  }
  
  return <div>{/* Products */}</div>;
}
```

**❌ Bad:**
```tsx
function ProductList() {
  const { data, isLoading } = useProducts();
  
  if (isLoading) {
    return null; // Blank page!
  }
  
  return <div>{/* Products */}</div>;
}
```

**Principles:**
- Show skeleton screens for content loading
- Show spinners for quick operations (<1s)
- Show progress bars for long operations (>1s)
- Show cached content if available (stale-while-revalidate)

## Skeleton Screens Over Spinners

Skeleton screens set expectations about content structure, reducing perceived loading time. Spinners are generic and don't provide context.

**✅ Good: Skeleton Screen**
```vue
<template>
  <div class="skeleton-card">
    <div class="skeleton-avatar shimmer"></div>
    <div class="skeleton-content">
      <div class="skeleton-line shimmer" style="width: 60%"></div>
      <div class="skeleton-line shimmer" style="width: 80%"></div>
    </div>
  </div>
</template>
```

**❌ Bad: Generic Spinner**
```vue
<template>
  <div class="spinner-container">
    <Spinner /> <!-- No context about what's loading -->
  </div>
</template>
```

**When to Use Each:**
- **Skeleton screens:** Content loading (lists, cards, profiles)
- **Spinners:** Quick operations (<1s), button states, inline loading
- **Progress bars:** Long operations (>1s), file uploads, exports

**Skeleton Screen Best Practices:**
- Match actual content layout exactly (same dimensions, spacing)
- Use subtle shimmer animation (not distracting)
- Show skeleton immediately (don't wait for network)
- Replace smoothly (fade transition, not instant swap)

## Optimistic Updates for Instant Feel

Update the UI immediately for user actions, then reconcile with the server response. This makes interactions feel instant.

**✅ Good: Optimistic Update**
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
      showError('Failed to add todo');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    }
  });
  
  return <div>{/* UI */}</div>;
}
```

**When to Use Optimistic Updates:**
- High-frequency actions (likes, favorites, toggles)
- Actions with high success probability (>95%)
- Actions where rollback is straightforward
- Actions that benefit from instant feedback

**When to Avoid:**
- Critical financial transactions
- Actions with complex validation
- Actions where rollback is difficult
- Actions with low success probability

## Progress Indicators for Long Operations

For operations longer than 1 second, show progress indicators with estimated time or percentage complete.

**✅ Good: Progress Bar with Percentage**
```tsx
function FileUpload() {
  const [progress, setProgress] = useState(0);
  
  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    await axios.post('/api/upload', formData, {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setProgress(percentCompleted);
      }
    });
  };
  
  return (
    <div>
      <ProgressBar value={progress} />
      <span>{progress}% complete</span>
    </div>
  );
}
```

**✅ Good: Indeterminate Progress for Unknown Duration**
```tsx
function ExportData() {
  const [isExporting, setIsExporting] = useState(false);
  
  const exportData = async () => {
    setIsExporting(true);
    try {
      await api.exportData();
      showSuccess('Export complete. Check your email.');
    } finally {
      setIsExporting(false);
    }
  };
  
  return (
    <div>
      {isExporting && (
        <div>
          <Spinner />
          <span>Exporting data... This may take a few minutes.</span>
        </div>
      )}
    </div>
  );
}
```

**Best Practices:**
- Show percentage when total size is known
- Show estimated time when duration can be estimated
- Show indeterminate progress when duration is unknown
- Allow cancellation for long operations
- Send email notification for very long operations (>30s)

## Content-First Loading Order

Load meaningful content before chrome (navigation, headers, footers). Users care about content, not UI chrome.

**✅ Good: Content First**
```tsx
function ProductPage() {
  // Load critical content first
  const { data: product } = useProduct(productId);
  
  // Load chrome after
  useEffect(() => {
    // Load navigation, footer, etc. after content
    loadChrome();
  }, []);
  
  return (
    <div>
      <ProductHeader product={product} />
      <ProductDetails product={product} />
      {/* Chrome loads after */}
    </div>
  );
}
```

**Loading Priority:**
1. Above-the-fold content (hero, main content)
2. Critical CSS (above-the-fold styles)
3. Critical JavaScript (interactivity)
4. Below-the-fold content (lazy load)
5. Non-critical CSS and JavaScript

**Resource Hints:**
```html
<head>
  <!-- Preload critical resources -->
  <link rel="preload" href="/hero-image.jpg" as="image">
  <link rel="preload" href="/critical-font.woff2" as="font" crossorigin>
  
  <!-- Prefetch likely next page -->
  <link rel="prefetch" href="/products">
</head>
```

## Avoid Cumulative Layout Shift

Reserve space for async content to prevent layout shifts. Layout shifts hurt user experience and Core Web Vitals (CLS).

**✅ Good: Reserve Space**
```vue
<template>
  <div class="product-card" style="min-height: 400px;">
    <img 
      v-if="product.image" 
      :src="product.image" 
      alt="Product"
      style="width: 100%; height: 300px; object-fit: cover;"
    />
    <div v-else class="image-placeholder" style="width: 100%; height: 300px;">
      <!-- Placeholder maintains space -->
    </div>
  </div>
</template>
```

```tsx
function ProductCard({ product }) {
  return (
    <div style={{ minHeight: '400px' }}>
      {product.image ? (
        <img 
          src={product.image} 
          alt="Product"
          style={{ width: '100%', height: '300px', objectFit: 'cover' }}
        />
      ) : (
        <div style={{ width: '100%', height: '300px' }}>
          {/* Placeholder maintains space */}
        </div>
      )}
    </div>
  );
}
```

**❌ Bad: No Space Reserved**
```tsx
function ProductCard({ product }) {
  return (
    <div>
      {product.image && (
        <img src={product.image} alt="Product" />
        // Image loads later, causes layout shift
      )}
    </div>
  );
}
```

**Best Practices:**
- Set `width` and `height` attributes on images
- Use `aspect-ratio` CSS property
- Reserve space for lazy-loaded content
- Use skeleton screens that match final layout
- Avoid inserting content above existing content

## Use Stale-While-Revalidate

Show cached data immediately, then update in the background. This balances freshness and speed.

**TanStack Query (React):**
```tsx
function ProductList() {
  const { data } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
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

**Configuration Guidelines:**
- **staleTime:** How long data is considered fresh (no refetch)
  - Static content: 1 hour
  - User-specific data: 5 minutes
  - Real-time data: 0 (always refetch)
- **gcTime:** How long unused data stays in cache
  - Default: 5 minutes
  - Increase for frequently accessed data
- **refetchOnWindowFocus:** Revalidate when window regains focus
  - Enable for data that changes frequently
  - Disable for static content

## Stack-Specific Guidance

### Vue 3

**Suspense:**
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

**VueQuery:**
```vue
<script setup>
import { useQuery } from '@tanstack/vue-query';

const { data, isLoading, isFetching } = useQuery({
  queryKey: ['products'],
  queryFn: fetchProducts,
  staleTime: 5 * 60 * 1000,
});
</script>

<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else>{{ data }}</div>
</template>
```

**Image Lazy Loading:**
```vue
<template>
  <img 
    src="image.jpg" 
    loading="lazy" 
    alt="Description"
  />
</template>
```

### React

**Suspense:**
```tsx
import { Suspense, lazy } from 'react';

const ProductList = lazy(() => import('./ProductList'));

function App() {
  return (
    <Suspense fallback={<ProductListSkeleton />}>
      <ProductList />
    </Suspense>
  );
}
```

**TanStack Query:**
```tsx
import { useQuery } from '@tanstack/react-query';

function ProductList() {
  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    staleTime: 5 * 60 * 1000,
  });
  
  if (isLoading) return <ProductListSkeleton />;
  return <div>{data}</div>;
}
```

**Image Lazy Loading:**
```tsx
<img src="image.jpg" loading="lazy" alt="Description" />

// Or with Intersection Observer
function LazyImage({ src, alt }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsLoaded(true);
        observer.disconnect();
      }
    });
    
    if (imgRef.current) observer.observe(imgRef.current);
    return () => observer.disconnect();
  }, []);
  
  return (
    <img 
      ref={imgRef}
      src={isLoaded ? src : undefined}
      alt={alt}
    />
  );
}
```

## Animation and Transitions

Use meaningful motion to enhance perceived performance. Avoid decorative animations that slow things down.

**✅ Good: Meaningful Transitions**
```vue
<template>
  <Transition name="fade">
    <div v-if="showContent" class="content">
      {{ content }}
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
```

```tsx
function Content({ show }) {
  return (
    <CSSTransition
      in={show}
      timeout={200}
      classNames="fade"
      unmountOnExit
    >
      <div className="content">Content</div>
    </CSSTransition>
  );
}
```

**Best Practices:**
- Keep transitions short (<300ms)
- Use easing functions (ease-in-out)
- Animate opacity and transform (GPU-accelerated)
- Avoid animating layout properties (width, height, top, left)
- Respect `prefers-reduced-motion` media query

**Accessibility:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Accessibility of Loading States

Loading states must be accessible to screen readers and keyboard users.

**✅ Good: Accessible Loading State**
```vue
<template>
  <div 
    v-if="loading" 
    role="status" 
    aria-live="polite"
    aria-busy="true"
  >
    <span class="sr-only">Loading products...</span>
    <ProductListSkeleton />
  </div>
  <div v-else role="status" aria-live="polite">
    <span class="sr-only">Products loaded</span>
    <ProductList :products="products" />
  </div>
</template>
```

```tsx
function ProductList() {
  const { data, isLoading } = useProducts();
  
  return (
    <div>
      {isLoading ? (
        <div role="status" aria-live="polite" aria-busy="true">
          <span className="sr-only">Loading products...</span>
          <ProductListSkeleton />
        </div>
      ) : (
        <div role="status" aria-live="polite">
          <span className="sr-only">Products loaded</span>
          <div>{/* Products */}</div>
        </div>
      )}
    </div>
  );
}
```

**ARIA Attributes:**
- **`aria-busy="true"`:** Indicates content is loading
- **`aria-live="polite"`:** Announces updates when ready (doesn't interrupt)
- **`aria-live="assertive"`:** Announces updates immediately (for critical changes)
- **`role="status"`:** Identifies element as a status message

**Screen Reader Announcements:**
```tsx
function useLoadingAnnouncement(isLoading, message) {
  useEffect(() => {
    if (isLoading) {
      // Screen reader will announce this
      const announcement = document.createElement('div');
      announcement.setAttribute('role', 'status');
      announcement.setAttribute('aria-live', 'polite');
      announcement.className = 'sr-only';
      announcement.textContent = message;
      document.body.appendChild(announcement);
      
      return () => document.body.removeChild(announcement);
    }
  }, [isLoading, message]);
}
```

**Best Practices:**
- Always provide text alternative for loading indicators
- Use `aria-live` regions for dynamic content updates
- Set `aria-busy` during loading operations
- Announce completion when loading finishes
- Test with screen readers (NVDA, JAWS, VoiceOver)
