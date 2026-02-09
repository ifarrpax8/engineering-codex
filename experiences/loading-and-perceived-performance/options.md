---
title: Loading and Perceived Performance -- Options
type: experience
last_updated: 2026-02-09
---

# Loading and Perceived Performance -- Options

## Contents

- [Loading Indicator Patterns](#loading-indicator-patterns)
- [Optimistic Update Strategies](#optimistic-update-strategies)
- [Prefetching Approaches](#prefetching-approaches)
- [Data Fetching and Caching Libraries](#data-fetching-and-caching-libraries)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Loading Indicator Patterns

### Skeleton Screen

**Description:** Content-shaped placeholders that match the layout of incoming content, often with shimmer animation.

**Strengths:**
- Sets expectations about content structure
- Reduces perceived loading time
- Provides visual context during loading
- Smooth transition to actual content

**Weaknesses:**
- Requires maintaining skeleton that matches content layout
- Can cause layout shift if skeleton doesn't match exactly
- More complex than simple spinner

**Best For:**
- Content loading (lists, cards, profiles, articles)
- Above-the-fold content
- When content structure is predictable
- When loading takes >500ms

**Avoid When:**
- Loading is very fast (<100ms)
- Content structure is highly variable
- Simple operations (button states, inline loading)

**Implementation:**
```vue
<!-- Vue 3 -->
<template>
  <div v-if="loading" class="skeleton-container">
    <div class="skeleton-item shimmer" v-for="i in 3" :key="i"></div>
  </div>
</template>
```

```tsx
// React
function ProductListSkeleton() {
  return (
    <div className="skeleton-container">
      {[1, 2, 3].map(i => (
        <div key={i} className="skeleton-item shimmer" />
      ))}
    </div>
  );
}
```

### Spinner/Loader

**Description:** Animated circular or linear indicator showing indeterminate progress.

**Strengths:**
- Simple to implement
- Universal recognition
- Lightweight
- Works for any loading scenario

**Weaknesses:**
- Provides no context about what's loading
- Doesn't set content expectations
- Can feel generic

**Best For:**
- Quick operations (<1s)
- Button states
- Inline loading
- When content structure is unknown
- Small, focused loading states

**Avoid When:**
- Content loading (use skeleton instead)
- Long operations (use progress bar)
- Above-the-fold content

**Implementation:**
```tsx
// React
function Spinner() {
  return (
    <div className="spinner" role="status" aria-live="polite">
      <span className="sr-only">Loading...</span>
    </div>
  );
}
```

### Progress Bar

**Description:** Linear indicator showing determinate or indeterminate progress, often with percentage.

**Strengths:**
- Shows actual progress (when available)
- Sets expectations about duration
- Provides sense of completion
- Reduces anxiety during long waits

**Weaknesses:**
- Requires progress tracking
- Not suitable for indeterminate operations
- Can be inaccurate if progress calculation is wrong

**Best For:**
- Long operations (>1s)
- File uploads/downloads
- Data exports
- Batch operations
- When progress can be calculated

**Avoid When:**
- Quick operations (<1s)
- Indeterminate duration
- Content loading (use skeleton)

**Implementation:**
```tsx
// React
function ProgressBar({ progress, total }) {
  const percentage = (progress / total) * 100;
  
  return (
    <div className="progress-bar">
      <div 
        className="progress-fill" 
        style={{ width: `${percentage}%` }}
      />
      <span>{percentage.toFixed(0)}%</span>
    </div>
  );
}
```

### Shimmer Effect

**Description:** Animated gradient overlay on skeleton screens that creates a "shimmer" or "pulse" effect.

**Strengths:**
- Draws attention to loading state
- Indicates active loading (not frozen)
- Smooth, professional animation
- Reduces perceived loading time

**Weaknesses:**
- Can be distracting if too intense
- Requires CSS animation
- May not work well for all content types

**Best For:**
- Skeleton screens
- Content loading
- When loading takes >500ms
- Modern, polished UIs

**Avoid When:**
- Very fast loading (<200ms)
- Minimalist design (may be too flashy)
- Low-motion preferences

**Implementation:**
```css
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
```

### Blur-up (Images)

**Description:** Low-quality placeholder image that gradually sharpens as the full image loads.

**Strengths:**
- Immediate visual feedback
- Smooth transition to full image
- Better than blank space
- Works well for image-heavy content

**Weaknesses:**
- Requires generating low-quality placeholders
- Only works for images
- May not work well for all image types

**Best For:**
- Image galleries
- Hero images
- Product images
- When images are critical content

**Avoid When:**
- Non-image content
- When placeholder generation is difficult
- Very fast image loading

**Implementation:**
```tsx
// React
function BlurUpImage({ src, placeholder, alt }) {
  const [loaded, setLoaded] = useState(false);
  
  return (
    <div className="image-container">
      <img 
        src={placeholder} 
        alt={alt}
        className={`blur-placeholder ${loaded ? 'hidden' : ''}`}
      />
      <img 
        src={src} 
        alt={alt}
        onLoad={() => setLoaded(true)}
        className={`full-image ${loaded ? 'loaded' : ''}`}
      />
    </div>
  );
}
```

## Optimistic Update Strategies

### Immediate UI + Reconcile

**Description:** Update UI immediately, send request to server, reconcile with server response, rollback on failure.

**Strengths:**
- Instant user feedback
- Feels very responsive
- Works well for high-frequency actions
- Good user experience

**Weaknesses:**
- Requires rollback logic
- Can show inconsistent state if server fails
- More complex than waiting for server

**Best For:**
- High-frequency actions (likes, favorites, toggles)
- Actions with high success probability (>95%)
- Actions where rollback is straightforward
- Non-critical operations

**Avoid When:**
- Critical financial transactions
- Actions with complex validation
- Actions where rollback is difficult
- Actions with low success probability

**Implementation:** See [Architecture: Optimistic Updates](architecture.md#optimistic-updates)

### Queue-Based

**Description:** Queue user actions, show optimistic UI, process queue in background, update UI as actions complete.

**Strengths:**
- Handles multiple rapid actions
- Can batch requests
- Good for offline scenarios
- Prevents race conditions

**Weaknesses:**
- More complex implementation
- Requires queue management
- Can be confusing if queue gets long
- May need conflict resolution

**Best For:**
- Offline-first applications
- Multiple rapid actions
- Batch operations
- When network is unreliable

**Avoid When:**
- Simple, single actions
- Real-time requirements
- When complexity isn't justified

### Optimistic with Undo

**Description:** Update UI immediately, show undo option, commit after timeout or user confirmation.

**Strengths:**
- User can correct mistakes
- Reduces anxiety about actions
- Good for destructive actions
- Provides safety net

**Weaknesses:**
- Requires undo state management
- More complex UI
- May confuse users if overused

**Best For:**
- Destructive actions (delete, archive)
- Actions that are hard to reverse
- When user might change mind
- High-stakes operations

**Avoid When:**
- Simple, reversible actions
- High-frequency actions
- When undo adds unnecessary complexity

## Prefetching Approaches

### Route-Based

**Description:** Prefetch entire route (HTML, CSS, JS, data) when user is likely to navigate there.

**Strengths:**
- Instant navigation
- Preloads all route resources
- Works well for predictable navigation
- Good for frequently visited routes

**Weaknesses:**
- Wastes bandwidth if user doesn't navigate
- Can slow down current page
- May prefetch unnecessary resources

**Best For:**
- Frequently visited routes
- Predictable user flows
- When bandwidth is not a concern
- Desktop applications

**Avoid When:**
- Mobile (bandwidth constraints)
- Unpredictable navigation
- When prefetching slows current page
- Data saver mode

**Implementation:**
```tsx
// Next.js automatic route prefetching
<Link href="/products" prefetch>Products</Link>

// React Router
<Link 
  to="/products"
  onMouseEnter={() => {
    router.prefetch('/products');
  }}
>
  Products
</Link>
```

### Hover-Based

**Description:** Prefetch resources when user hovers over link or interactive element.

**Strengths:**
- Only prefetches when user shows intent
- Efficient use of bandwidth
- Doesn't slow down current page
- Good balance of speed and efficiency

**Weaknesses:**
- Requires hover interaction (doesn't work on mobile)
- May not prefetch fast enough for instant navigation
- Doesn't work for touch devices

**Best For:**
- Desktop applications
- Navigation menus
- When user intent is clear
- When bandwidth should be conserved

**Avoid When:**
- Mobile-first applications
- Touch-only interfaces
- When instant navigation is critical

**Implementation:** See [Architecture: Prefetching Strategies](architecture.md#prefetching-strategies)

### Viewport-Based (Intersection Observer)

**Description:** Prefetch resources when element enters viewport (with margin).

**Strengths:**
- Works on all devices
- Prefetches just before needed
- Efficient bandwidth usage
- Good for lazy-loaded content

**Weaknesses:**
- May not prefetch fast enough
- Requires Intersection Observer support
- More complex than route-based

**Best For:**
- Lazy-loaded content
- Below-the-fold content
- Image galleries
- Infinite scroll
- Mobile applications

**Avoid When:**
- Above-the-fold content
- When instant load is required
- When prefetching too early is wasteful

**Implementation:** See [Architecture: Prefetching Strategies](architecture.md#prefetching-strategies)

## Data Fetching and Caching Libraries

### TanStack Query (React)

**Description:** Powerful data fetching and caching library for React with built-in stale-while-revalidate, optimistic updates, and more.

**Strengths:**
- Excellent caching and synchronization
- Built-in optimistic updates
- Automatic refetching strategies
- Great DevTools
- Active community and maintenance

**Weaknesses:**
- Learning curve for advanced features
- Can be overkill for simple use cases
- Requires React (not framework-agnostic)

**Best For:**
- React applications
- Complex data fetching needs
- Server state management
- Applications with caching requirements
- Teams needing advanced features

**Avoid When:**
- Simple data fetching (use fetch/axios)
- Non-React applications
- When bundle size is critical

### VueQuery (Vue 3)

**Description:** Vue 3 port of TanStack Query, providing same powerful features for Vue applications.

**Strengths:**
- Same powerful features as TanStack Query
- Vue 3 Composition API integration
- Excellent caching and synchronization
- Built-in optimistic updates

**Weaknesses:**
- Learning curve for advanced features
- Requires Vue 3
- Can be overkill for simple use cases

**Best For:**
- Vue 3 applications
- Complex data fetching needs
- Server state management
- Applications with caching requirements

**Avoid When:**
- Simple data fetching
- Vue 2 applications (use different library)
- When bundle size is critical

### SWR (React)

**Description:** Lightweight data fetching library with stale-while-revalidate pattern.

**Strengths:**
- Lightweight and simple
- Good for basic use cases
- Built-in revalidation
- Good documentation

**Weaknesses:**
- Less features than TanStack Query
- Smaller ecosystem
- Less active development

**Best For:**
- Simple to moderate data fetching needs
- When lightweight is important
- Basic stale-while-revalidate needs
- Smaller applications

**Avoid When:**
- Complex caching requirements
- Need for optimistic updates (limited support)
- Large-scale applications
- Need for advanced features

## Recommendation Guidance

### Choose Skeleton Screens When:
- Loading content (lists, cards, profiles)
- Loading takes >500ms
- Content structure is predictable
- Above-the-fold content

### Choose Optimistic Updates When:
- High-frequency actions (likes, favorites)
- High success probability (>95%)
- Rollback is straightforward
- Instant feedback is important

### Choose Prefetching When:
- Predictable user navigation
- Bandwidth is not a concern (desktop)
- Instant navigation is important
- Frequently visited routes

### Choose TanStack Query/VueQuery When:
- Complex data fetching needs
- Need for caching and synchronization
- Server state management
- Optimistic updates required

## Synergies

**Skeleton Screens + Stale-While-Revalidate:**
- Show skeleton for initial load, cached content for subsequent loads
- Best of both worlds: fast perceived performance and instant cached loads

**Optimistic Updates + Error Boundaries:**
- Optimistic updates provide instant feedback, error boundaries handle failures gracefully
- Creates resilient, fast-feeling UI

**Prefetching + Service Worker:**
- Prefetch resources, cache with service worker for offline access
- Enables offline-first experiences

**Suspense + Code Splitting:**
- Suspense boundaries with lazy-loaded routes
- Progressive loading with clear loading states

## Evolution Triggers

**Move from Spinner to Skeleton Screen When:**
- Loading takes >500ms regularly
- Content structure becomes predictable
- Users complain about generic loading states
- Design system includes skeleton components

**Move from Simple Fetch to TanStack Query/VueQuery When:**
- Need for caching becomes apparent
- Multiple components need same data
- Optimistic updates are needed
- Complex synchronization requirements

**Move from Route-Based to Hover-Based Prefetching When:**
- Bandwidth becomes a concern (mobile)
- Prefetching slows down current page
- Users don't always navigate to prefetched routes
- Need to conserve resources

**Move from Eager to Lazy Loading When:**
- Bundle size becomes too large
- Initial load time increases
- Below-the-fold content is heavy
- Performance budgets are exceeded
