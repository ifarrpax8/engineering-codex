---
title: Loading and Perceived Performance -- Testing
type: experience
last_updated: 2026-02-09
---

# Loading and Perceived Performance -- Testing

## Contents

- [Visual Regression for Loading States](#visual-regression-for-loading-states)
- [Lighthouse CI Integration](#lighthouse-ci-integration)
- [Throttled Network Testing](#throttled-network-testing)
- [Skeleton-to-Content Transition Testing](#skeleton-to-content-transition-testing)
- [Optimistic Update Testing](#optimistic-update-testing)
- [Prefetch Verification](#prefetch-verification)
- [Core Web Vitals Testing](#core-web-vitals-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Visual Regression for Loading States

Loading states must be visually consistent and match design specifications. Visual regression testing catches layout shifts, incorrect skeleton screens, and broken loading animations.

**Playwright Visual Regression Example:**
```typescript
import { test, expect } from '@playwright/test';

test('skeleton screen matches design', async ({ page }) => {
  // Intercept API to delay response
  await page.route('**/api/products', async route => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    await route.continue();
  });
  
  await page.goto('/products');
  
  // Wait for skeleton to appear
  await page.waitForSelector('.skeleton-container');
  
  // Visual regression snapshot
  await expect(page).toHaveScreenshot('product-list-skeleton.png', {
    fullPage: true,
    animations: 'disabled'
  });
});

test('shimmer animation renders correctly', async ({ page }) => {
  await page.goto('/products');
  await page.waitForSelector('.shimmer');
  
  // Capture multiple frames of animation
  const frames = [];
  for (let i = 0; i < 5; i++) {
    await page.waitForTimeout(200);
    frames.push(await page.screenshot());
  }
  
  // Verify shimmer effect is present
  expect(frames[0]).not.toEqual(frames[2]);
});
```

**Storybook Visual Testing:**
```tsx
// ProductListSkeleton.stories.tsx
export default {
  title: 'Loading/ProductListSkeleton',
  component: ProductListSkeleton,
};

export const Default = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId('skeleton-container')).toBeVisible();
  },
};

// Visual regression test
export const VisualRegression = {
  parameters: {
    chromatic: { 
      delay: 500, // Wait for animation
      pauseAnimationAtEnd: true 
    }
  }
};
```

**Key Test Cases:**
- Skeleton screens match actual content layout
- Shimmer animations are smooth and not jarring
- Loading spinners are centered and visible
- Progress bars show accurate progress
- Loading states don't cause layout shift

## Lighthouse CI Integration

Automated performance budgets catch regressions before they reach production. Integrate Lighthouse CI into your CI/CD pipeline.

**GitHub Actions Example:**
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [push, pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true
          temporaryPublicStorage: true
```

**Lighthouse CI Configuration:**
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "startServerCommand": "npm run start",
      "url": [
        "http://localhost:3000/products",
        "http://localhost:3000/dashboard"
      ]
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 1800}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "interactive": ["error", {"maxNumericValue": 3800}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

**Performance Budgets:**
```json
{
  "budgets": [
    {
      "path": "/products",
      "timings": [
        {
          "metric": "first-contentful-paint",
          "budget": 1800
        },
        {
          "metric": "largest-contentful-paint",
          "budget": 2500
        }
      ],
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 200
        },
        {
          "resourceType": "image",
          "budget": 500
        }
      ]
    }
  ]
}
```

## Throttled Network Testing

Test loading behavior under realistic network conditions. Simulate 3G, slow 3G, and offline scenarios.

**Playwright Network Throttling:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Loading under slow network', () => {
  test('shows loading state on 3G', async ({ page, context }) => {
    // Throttle to 3G speeds
    await context.setGeolocation({ latitude: 0, longitude: 0 });
    await context.setExtraHTTPHeaders({
      'Network-Conditions': '3G'
    });
    
    // Use Playwright's network throttling
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
      uploadThroughput: 750 * 1024 / 8, // 750 Kbps
      latency: 150
    });
    
    await page.goto('/products');
    
    // Verify loading indicator appears
    await expect(page.locator('.loading-indicator')).toBeVisible();
    
    // Verify content eventually loads
    await expect(page.locator('.product-list')).toBeVisible({ timeout: 30000 });
  });
  
  test('handles offline gracefully', async ({ page, context }) => {
    await context.setOffline(true);
    
    await page.goto('/products');
    
    // Should show cached content or offline message
    const offlineMessage = page.locator('.offline-message');
    const cachedContent = page.locator('.cached-content');
    
    await expect(
      offlineMessage.or(cachedContent)
    ).toBeVisible();
  });
});
```

**Cypress Network Throttling:**
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('throttleNetwork', (preset: '3G' | 'slow-3G' | 'offline') => {
  cy.window().then((win) => {
    const conditions = {
      '3G': { downloadThroughput: 1.5 * 1024 * 1024 / 8, latency: 150 },
      'slow-3G': { downloadThroughput: 400 * 1024 / 8, latency: 400 },
      'offline': { offline: true }
    };
    
    // Use Chrome DevTools Protocol
    cy.task('setNetworkConditions', conditions[preset]);
  });
});

// Usage
it('loads on slow 3G', () => {
  cy.throttleNetwork('slow-3G');
  cy.visit('/products');
  cy.get('.loading-indicator').should('be.visible');
  cy.get('.product-list').should('be.visible', { timeout: 30000 });
});
```

## Skeleton-to-Content Transition Testing

Verify that skeleton screens transition smoothly to actual content without layout shift.

**Layout Shift Testing:**
```typescript
test('no layout shift when content loads', async ({ page }) => {
  await page.goto('/products');
  
  // Wait for skeleton
  await page.waitForSelector('.skeleton-container');
  const skeletonBounds = await page.locator('.skeleton-container').boundingBox();
  
  // Wait for content
  await page.waitForSelector('.product-list', { state: 'visible' });
  const contentBounds = await page.locator('.product-list').boundingBox();
  
  // Verify no significant layout shift
  const widthDiff = Math.abs(skeletonBounds.width - contentBounds.width);
  const heightDiff = Math.abs(skeletonBounds.height - contentBounds.height);
  
  expect(widthDiff).toBeLessThan(10); // Allow 10px tolerance
  expect(heightDiff).toBeLessThan(50); // Allow 50px for content expansion
});

test('CLS score is acceptable', async ({ page }) => {
  await page.goto('/products');
  
  // Measure Cumulative Layout Shift
  const cls = await page.evaluate(() => {
    return new Promise((resolve) => {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        resolve(clsValue);
      });
      observer.observe({ type: 'layout-shift', buffered: true });
      
      // Wait for page to stabilize
      setTimeout(() => resolve(clsValue), 5000);
    });
  });
  
  expect(cls).toBeLessThan(0.1); // Good CLS threshold
});
```

**Transition Animation Testing:**
```typescript
test('smooth fade transition from skeleton to content', async ({ page }) => {
  await page.goto('/products');
  
  // Capture skeleton state
  await page.waitForSelector('.skeleton-container');
  const skeletonOpacity = await page.locator('.skeleton-container').evaluate(
    el => window.getComputedStyle(el).opacity
  );
  expect(skeletonOpacity).toBe('1');
  
  // Wait for content and verify fade
  await page.waitForSelector('.product-list');
  
  // Skeleton should fade out
  await expect(page.locator('.skeleton-container')).toHaveCSS('opacity', '0', { timeout: 1000 });
  
  // Content should fade in
  await expect(page.locator('.product-list')).toHaveCSS('opacity', '1');
});
```

## Optimistic Update Testing

Test both success and rollback paths for optimistic updates.

**Success Path Testing:**
```typescript
test('optimistic update succeeds', async ({ page }) => {
  await page.goto('/todos');
  
  const initialCount = await page.locator('.todo-item').count();
  
  // Add item optimistically
  await page.fill('[data-testid="todo-input"]', 'New todo');
  await page.click('[data-testid="add-todo-button"]');
  
  // UI should update immediately
  await expect(page.locator('.todo-item')).toHaveCount(initialCount + 1);
  await expect(page.locator('text=New todo')).toBeVisible();
  
  // Wait for server confirmation
  await page.waitForResponse(response => 
    response.url().includes('/api/todos') && response.status() === 201
  );
  
  // Item should still be there (reconciled)
  await expect(page.locator('text=New todo')).toBeVisible();
});
```

**Rollback Path Testing:**
```typescript
test('optimistic update rolls back on failure', async ({ page }) => {
  await page.goto('/todos');
  
  // Intercept API to fail
  await page.route('**/api/todos', route => {
    route.fulfill({ status: 500, body: JSON.stringify({ error: 'Server error' }) });
  });
  
  const initialCount = await page.locator('.todo-item').count();
  
  // Add item optimistically
  await page.fill('[data-testid="todo-input"]', 'Failing todo');
  await page.click('[data-testid="add-todo-button"]');
  
  // UI should update immediately
  await expect(page.locator('.todo-item')).toHaveCount(initialCount + 1);
  
  // Wait for error response
  await page.waitForResponse(response => 
    response.url().includes('/api/todos') && response.status() === 500
  );
  
  // Item should be removed (rollback)
  await expect(page.locator('.todo-item')).toHaveCount(initialCount);
  await expect(page.locator('text=Failing todo')).not.toBeVisible();
  
  // Error message should appear
  await expect(page.locator('.error-message')).toBeVisible();
  await expect(page.locator('.error-message')).toContainText('Failed to add todo');
});
```

## Prefetch Verification

Verify that prefetching works correctly and resources are loaded before navigation.

**Prefetch Detection:**
```typescript
test('prefetches route on hover', async ({ page }) => {
  await page.goto('/');
  
  const link = page.locator('a[href="/products"]');
  
  // Monitor network requests
  const prefetchPromise = page.waitForRequest(request => 
    request.url().includes('/products') && 
    request.method() === 'GET'
  );
  
  // Hover over link
  await link.hover();
  
  // Wait for prefetch
  const prefetchRequest = await prefetchPromise;
  expect(prefetchRequest).toBeTruthy();
  
  // Verify prefetch headers
  const headers = prefetchRequest.headers();
  expect(headers['purpose']).toBe('prefetch');
});

test('prefetched content loads instantly on navigation', async ({ page }) => {
  await page.goto('/');
  
  // Prefetch products page
  const link = page.locator('a[href="/products"]');
  await link.hover();
  await page.waitForTimeout(1000); // Wait for prefetch
  
  // Navigate to products
  const startTime = Date.now();
  await link.click();
  
  // Page should load from cache (instant)
  await page.waitForSelector('.product-list');
  const loadTime = Date.now() - startTime;
  
  expect(loadTime).toBeLessThan(500); // Should be <500ms from cache
});
```

**Service Worker Cache Testing:**
```typescript
test('service worker caches resources', async ({ page, context }) => {
  await page.goto('/');
  
  // Wait for service worker registration
  await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    return registration !== null;
  });
  
  // Navigate to products
  await page.goto('/products');
  await page.waitForSelector('.product-list');
  
  // Go offline
  await context.setOffline(true);
  
  // Navigate back - should load from cache
  await page.goto('/products');
  await expect(page.locator('.product-list')).toBeVisible();
  
  // Verify it's from cache
  const cacheStatus = await page.evaluate(() => {
    return (window as any).performance.getEntriesByType('resource')
      .find((entry: any) => entry.name.includes('/api/products'))
      ?.transferSize === 0; // 0 means from cache
  });
  
  expect(cacheStatus).toBe(true);
});
```

## Core Web Vitals Testing

Measure and assert Core Web Vitals metrics in automated tests.

**LCP Testing:**
```typescript
test('LCP is under threshold', async ({ page }) => {
  await page.goto('/products');
  
  const lcp = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        resolve(lastEntry.startTime);
      }).observe({ type: 'largest-contentful-paint', buffered: true });
      
      setTimeout(() => resolve(null), 10000);
    });
  });
  
  expect(lcp).toBeLessThan(2500); // Good LCP threshold
});
```

**CLS Testing:**
```typescript
test('CLS is under threshold', async ({ page }) => {
  await page.goto('/products');
  
  // Wait for page to stabilize
  await page.waitForTimeout(5000);
  
  const cls = await page.evaluate(() => {
    return new Promise((resolve) => {
      let clsValue = 0;
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
      }).observe({ type: 'layout-shift', buffered: true });
      
      setTimeout(() => resolve(clsValue), 5000);
    });
  });
  
  expect(cls).toBeLessThan(0.1); // Good CLS threshold
});
```

**INP Testing:**
```typescript
test('INP is under threshold', async ({ page }) => {
  await page.goto('/products');
  
  // Perform interactions
  await page.click('[data-testid="filter-button"]');
  await page.fill('[data-testid="search-input"]', 'test');
  await page.click('[data-testid="product-card"]');
  
  const inp = await page.evaluate(() => {
    return new Promise((resolve) => {
      const interactions: number[] = [];
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          interactions.push((entry as any).duration);
        }
      }).observe({ type: 'event', buffered: true });
      
      setTimeout(() => {
        const maxInteraction = Math.max(...interactions);
        resolve(maxInteraction);
      }, 5000);
    });
  });
  
  expect(inp).toBeLessThan(200); // Good INP threshold
});
```

## QA and Test Engineer Perspective

### Manual Testing Checklist

**Loading State Verification:**
- [ ] Skeleton screens appear immediately (no blank page)
- [ ] Skeleton layout matches actual content layout
- [ ] Shimmer animations are smooth and not distracting
- [ ] Loading spinners are visible and centered
- [ ] Progress bars show accurate progress
- [ ] Loading states don't cause layout shift

**Network Condition Testing:**
- [ ] Test on 3G, slow 3G, and offline
- [ ] Verify loading indicators appear on slow networks
- [ ] Verify cached content loads offline
- [ ] Verify error states when offline and no cache

**Optimistic Update Testing:**
- [ ] Verify UI updates immediately on user action
- [ ] Verify server reconciliation works correctly
- [ ] Verify rollback on server error
- [ ] Verify error messages appear on failure

**Performance Testing:**
- [ ] Measure Time to First Contentful Paint (FCP)
- [ ] Measure Largest Contentful Paint (LCP)
- [ ] Measure Cumulative Layout Shift (CLS)
- [ ] Measure First Input Delay (FID) / Interaction to Next Paint (INP)
- [ ] Verify metrics meet performance budgets

### Test Data Requirements

**Loading State Test Data:**
- Large datasets (1000+ items) to test pagination loading
- Slow API responses (simulate with delays) to test loading states
- Empty states to test zero-result loading
- Error responses to test error state loading

**Network Simulation:**
- Use browser DevTools network throttling
- Test with Chrome's "Slow 3G" and "Fast 3G" presets
- Test offline mode with service worker
- Test with intermittent connectivity

### Regression Testing Strategy

**Visual Regression:**
- Screenshot skeleton screens on every build
- Compare skeleton layouts to actual content layouts
- Verify loading animations haven't regressed

**Performance Regression:**
- Run Lighthouse CI on every PR
- Compare Core Web Vitals to baseline
- Alert on performance budget violations

**Functional Regression:**
- Test optimistic updates on every build
- Verify prefetching still works after changes
- Test service worker cache invalidation

### Edge Cases to Test

**Loading Edge Cases:**
- Content loads faster than skeleton appears (no flicker)
- Content loads slower than expected (timeout handling)
- Partial content loads (some items fail)
- Content never loads (error state)

**Network Edge Cases:**
- Request timeout
- Network error mid-load
- Partial response (chunked transfer)
- CORS errors

**Cache Edge Cases:**
- Stale cache after deployment
- Cache invalidation
- Cache size limits
- Cache corruption

### Reporting and Metrics

**Test Reports Should Include:**
- Screenshots of loading states
- Performance metrics (LCP, CLS, INP)
- Network condition test results
- Optimistic update test results
- Visual regression comparisons

**Metrics to Track:**
- Loading state coverage (% of pages with loading states)
- Performance budget compliance
- Core Web Vitals trends over time
- Loading-related bug reports
