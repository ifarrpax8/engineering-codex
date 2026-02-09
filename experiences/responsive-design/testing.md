# Responsive Design -- Testing

Testing strategies, tools, and approaches for ensuring responsive designs work correctly across devices and viewports.

## Contents

- [Viewport Testing with Playwright](#viewport-testing-with-playwright)
- [Visual Regression Across Breakpoints](#visual-regression-across-breakpoints)
- [Touch Target Size Verification](#touch-target-size-verification)
- [Responsive Image Loading](#responsive-image-loading)
- [Performance on Mobile Networks](#performance-on-mobile-networks)
- [Orientation Testing](#orientation-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Viewport Testing with Playwright

### Device Emulation
Playwright provides built-in device emulation for common devices.

```typescript
import { test, devices } from '@playwright/test';

// Use predefined device
test('mobile view', async ({ page }) => {
  await page.emulate(devices['iPhone 13']);
  await page.goto('https://example.com');
  // Test mobile layout
});

// Available devices: iPhone 13, iPhone 13 Pro, iPad Pro, etc.
```

### Custom Viewports
Define custom viewport sizes for your specific breakpoints.

```typescript
test('tablet view', async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto('https://example.com');
  // Test tablet layout
});

test('desktop view', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto('https://example.com');
  // Test desktop layout
});
```

### --device Flag
Use command-line flag to run tests for specific devices.

```bash
# Run tests for iPhone
npx playwright test --device="iPhone 13"

# Run tests for iPad
npx playwright test --device="iPad Pro"
```

### Viewport Testing Best Practices

```typescript
// Test all breakpoints systematically
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 },
];

viewports.forEach(({ name, width, height }) => {
  test(`layout at ${name} viewport`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('/dashboard');
    
    // Verify layout elements
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    
    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = width;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  });
});
```

## Visual Regression Across Breakpoints

### Snapshot at Multiple Widths
Capture visual snapshots at each breakpoint to detect layout breaks.

```typescript
import { test, expect } from '@playwright/test';

test('visual regression at breakpoints', async ({ page }) => {
  const breakpoints = [375, 768, 1024, 1920];
  
  for (const width of breakpoints) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto('/dashboard');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Capture screenshot
    await expect(page).toHaveScreenshot(`dashboard-${width}px.png`);
  }
});
```

### Detecting Layout Breaks
Test for common layout issues:

```typescript
test('no layout breaks', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');
  
  // Check for horizontal overflow
  const hasHorizontalScroll = await page.evaluate(() => {
    return document.documentElement.scrollWidth > window.innerWidth;
  });
  expect(hasHorizontalScroll).toBe(false);
  
  // Check for overlapping elements
  const overlapping = await page.evaluate(() => {
    const elements = document.querySelectorAll('.card');
    // Check if any cards overlap (simplified check)
    return false; // Implement actual overlap detection
  });
  expect(overlapping).toBe(false);
  
  // Check for text overflow
  const textOverflow = await page.locator('.card-title').evaluate((el) => {
    return el.scrollWidth > el.clientWidth;
  });
  expect(textOverflow).toBe(false);
});
```

### Responsive Visual Testing with Percy/Chromatic
Use visual testing services that support multiple viewports.

```typescript
import percySnapshot from '@percy/playwright';

test('percy visual test', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Snapshot at multiple viewports
  await percySnapshot(page, 'Dashboard - Mobile', { widths: [375] });
  await percySnapshot(page, 'Dashboard - Tablet', { widths: [768] });
  await percySnapshot(page, 'Dashboard - Desktop', { widths: [1920] });
});
```

## Touch Target Size Verification

### Minimum 44x44px (WCAG 2.5.8)
Verify all interactive elements meet minimum touch target size.

```typescript
test('touch targets meet WCAG standards', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');
  
  // Get all interactive elements
  const buttons = await page.locator('button, a, [role="button"]').all();
  
  for (const button of buttons) {
    const box = await button.boundingBox();
    if (box) {
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
    }
  }
});
```

### Testing Tap Targets Don't Overlap
Ensure touch targets have adequate spacing.

```typescript
test('touch targets do not overlap', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');
  
  const buttons = await page.locator('button').all();
  const boxes = await Promise.all(
    buttons.map(btn => btn.boundingBox())
  );
  
  // Check for overlaps (simplified - check if bounding boxes intersect)
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      if (boxes[i] && boxes[j]) {
        const overlap = !(
          boxes[i].x + boxes[i].width < boxes[j].x ||
          boxes[j].x + boxes[j].width < boxes[i].x ||
          boxes[i].y + boxes[i].height < boxes[j].y ||
          boxes[j].y + boxes[j].height < boxes[i].y
        );
        expect(overlap).toBe(false);
      }
    }
  }
});
```

### Spacing Between Targets
Verify adequate spacing between interactive elements.

```typescript
test('adequate spacing between touch targets', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');
  
  const buttons = page.locator('button');
  const count = await buttons.count();
  
  for (let i = 0; i < count - 1; i++) {
    const box1 = await buttons.nth(i).boundingBox();
    const box2 = await buttons.nth(i + 1).boundingBox();
    
    if (box1 && box2) {
      // Check vertical spacing (assuming vertical layout)
      const spacing = Math.abs(box2.y - (box1.y + box1.height));
      expect(spacing).toBeGreaterThanOrEqual(8); // Minimum 8px spacing
    }
  }
});
```

## Responsive Image Loading

### Correct srcset Resolution Served Per Viewport
Verify browser selects appropriate image size based on viewport.

```typescript
test('correct image resolution per viewport', async ({ page }) => {
  // Mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');
  
  const mobileImg = page.locator('img').first();
  const mobileSrc = await mobileImg.getAttribute('src');
  // Verify mobile-appropriate image is loaded
  // (implementation depends on your image strategy)
  
  // Desktop viewport
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.reload();
  
  const desktopImg = page.locator('img').first();
  const desktopSrc = await desktopImg.getAttribute('src');
  // Verify desktop-appropriate image is loaded
  expect(desktopSrc).not.toBe(mobileSrc);
});
```

### Lazy Loading Triggers Correctly
Test that images load as they enter viewport.

```typescript
test('lazy loading works correctly', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/long-page');
  
  // Initially, images below fold should not be loaded
  const belowFoldImg = page.locator('img[loading="lazy"]').nth(2);
  const initialSrc = await belowFoldImg.getAttribute('src');
  expect(initialSrc).toBe(''); // or placeholder
  
  // Scroll to image
  await belowFoldImg.scrollIntoViewIfNeeded();
  await page.waitForTimeout(500); // Wait for lazy load
  
  // Image should now be loaded
  const loadedSrc = await belowFoldImg.getAttribute('src');
  expect(loadedSrc).not.toBe('');
});
```

## Performance on Mobile Networks

### Throttled Network Testing
Test performance under mobile network conditions.

```typescript
import { test } from '@playwright/test';

test('performance on 3G network', async ({ page, context }) => {
  // Throttle network to 3G speeds
  await context.route('**/*', async (route) => {
    // Simulate 3G: 750 Kbps down, 250 Kbps up, 100ms latency
    await route.continue();
  });
  
  await page.setViewportSize({ width: 375, height: 667 });
  
  const startTime = Date.now();
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - startTime;
  
  // Verify load time is acceptable (e.g., < 5 seconds on 3G)
  expect(loadTime).toBeLessThan(5000);
});
```

### Mobile Payload Budgets
Verify page size meets mobile budget requirements.

```typescript
test('mobile payload budget', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  
  const response = await page.goto('/dashboard');
  const contentLength = response?.headers()['content-length'];
  
  if (contentLength) {
    const sizeKB = parseInt(contentLength) / 1024;
    // Mobile budget: < 500KB initial HTML
    expect(sizeKB).toBeLessThan(500);
  }
  
  // Check total resources loaded
  const resources = await page.evaluate(() => {
    return performance.getEntriesByType('resource')
      .reduce((total, entry) => total + entry.transferSize, 0);
  });
  
  const totalMB = resources / (1024 * 1024);
  // Mobile budget: < 2MB total
  expect(totalMB).toBeLessThan(2);
});
```

### Core Web Vitals on Mobile
Measure Core Web Vitals under mobile conditions.

```typescript
test('Core Web Vitals on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  
  await page.goto('/dashboard');
  
  // Measure LCP (Largest Contentful Paint)
  const lcp = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        resolve(lastEntry.renderTime || lastEntry.loadTime);
      }).observe({ entryTypes: ['largest-contentful-paint'] });
    });
  });
  
  // LCP should be < 2.5s on mobile
  expect(lcp).toBeLessThan(2500);
});
```

## Orientation Testing

### Portrait vs Landscape on Tablet
Test layout in both orientations.

```typescript
test('tablet orientation layouts', async ({ page }) => {
  // Portrait
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto('/dashboard');
  await expect(page.locator('.dashboard')).toHaveScreenshot('tablet-portrait.png');
  
  // Landscape
  await page.setViewportSize({ width: 1024, height: 768 });
  await page.reload();
  await expect(page.locator('.dashboard')).toHaveScreenshot('tablet-landscape.png');
});
```

### Orientation Change Handling
Test that layout adapts when orientation changes.

```typescript
test('orientation change handling', async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto('/dashboard');
  
  // Verify portrait layout
  const portraitNav = page.locator('nav');
  await expect(portraitNav).toHaveClass(/portrait/);
  
  // Change to landscape
  await page.setViewportSize({ width: 1024, height: 768 });
  await page.waitForTimeout(100); // Wait for layout recalculation
  
  // Verify landscape layout
  const landscapeNav = page.locator('nav');
  await expect(landscapeNav).toHaveClass(/landscape/);
});
```

## QA and Test Engineer Perspective

### Test Planning for Responsive Design

**Breakpoint Coverage**: Create a test matrix covering all breakpoints:
- Mobile: 320px, 375px, 414px (common mobile widths)
- Tablet: 768px, 1024px (portrait and landscape)
- Desktop: 1280px, 1920px, 2560px (standard, large, ultra-wide)

**Device Testing Priority**:
1. Most common devices per analytics (e.g., iPhone 13, Samsung Galaxy)
2. Edge cases (smallest mobile, largest desktop)
3. Real devices for critical user flows

**Test Scenarios**:
- Layout integrity at each breakpoint
- Navigation patterns (drawer, sidebar, bottom nav)
- Form usability (input types, keyboard behavior)
- Image loading and optimization
- Performance metrics per device category

### Manual Testing Checklist

**Mobile Testing (320px - 768px)**:
- [ ] No horizontal scroll (except intentional carousels)
- [ ] Touch targets minimum 44x44px
- [ ] Navigation accessible (hamburger menu or bottom nav)
- [ ] Forms single-column layout
- [ ] Images load appropriate sizes
- [ ] Text readable without zooming
- [ ] Soft keyboard doesn't break layout
- [ ] Orientation change handled gracefully

**Tablet Testing (768px - 1024px)**:
- [ ] Layout optimized for both orientations
- [ ] Touch interactions work correctly
- [ ] Presentation mode available (if applicable)
- [ ] Navigation pattern appropriate (sidebar or top nav)
- [ ] Content density appropriate (not too sparse, not too dense)

**Desktop Testing (1024px+)**:
- [ ] Full feature set available
- [ ] Hover states work correctly
- [ ] Multi-column layouts function
- [ ] Keyboard shortcuts work
- [ ] Dense information displays correctly
- [ ] Ultra-wide support (2560px+) if applicable

### Automated Testing Strategy

**Visual Regression Testing**:
- Capture screenshots at each breakpoint
- Compare against baseline images
- Flag layout breaks, text overflow, element misalignment

**Functional Testing**:
- Test interactions at each breakpoint
- Verify conditional rendering (mobile vs desktop components)
- Test navigation patterns per device
- Verify form submissions work across devices

**Performance Testing**:
- Measure load times per device category
- Test on throttled networks (3G, 4G)
- Verify Core Web Vitals per breakpoint
- Check payload sizes meet mobile budgets

### Common Issues to Watch For

**Layout Breaks**:
- Elements overlapping at certain breakpoints
- Horizontal scroll appearing unexpectedly
- Text overflow or truncation issues
- Images breaking out of containers

**Interaction Problems**:
- Hover-only features not working on touch devices
- Touch targets too small or overlapping
- Soft keyboard covering form inputs
- Scroll behavior issues (momentum scrolling, scroll chaining)

**Performance Issues**:
- Desktop-sized images loading on mobile
- JavaScript bundles too large for mobile
- Layout shifts (CLS) during load
- Slow interactions on lower-end devices

### Testing Tools and Services

**Browser DevTools**:
- Device emulation for quick checks
- Network throttling for performance testing
- Touch simulation for interaction testing

**Playwright/Cypress**:
- Automated viewport testing
- Visual regression testing
- Performance measurement
- Cross-browser testing

**Real Device Testing**:
- BrowserStack, Sauce Labs for cloud device testing
- Physical device lab for critical flows
- Beta testing with real users on their devices

**Visual Testing Services**:
- Percy, Chromatic for visual regression
- Lighthouse CI for performance monitoring
- WebPageTest for detailed performance analysis

### Reporting and Documentation

**Test Reports Should Include**:
- Screenshots at each breakpoint
- Performance metrics per device category
- List of issues found with severity
- Recommendations for fixes

**Documentation**:
- Test coverage matrix (which breakpoints tested)
- Known issues and workarounds
- Device-specific considerations
- Performance budgets per device category
