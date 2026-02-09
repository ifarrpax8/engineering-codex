---
title: Design Consistency & Visual Identity - Testing
type: experience
last_updated: 2026-02-09
---

# Testing: Design Consistency & Visual Identity

## Contents

- [Visual Regression Testing](#visual-regression-testing)
- [Design Token Validation](#design-token-validation)
- [Component Library Compliance](#component-library-compliance)
- [Cross-Browser and Cross-Device Consistency Testing](#cross-browser-and-cross-device-consistency-testing)
- [Responsive Layout Verification](#responsive-layout-verification)
- [Dark Mode / Theme Testing](#dark-mode-theme-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Visual Regression Testing

Visual regression testing captures UI screenshots and compares them against baseline images to detect unintended visual changes.

### Tools

**Chromatic** (Storybook integration):
```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    'chromatic', // Visual regression testing
  ],
};
```

**Percy** (works with any framework):
```javascript
// percy.config.js
module.exports = {
  project: 'my-project',
  widths: [1280, 375], // Desktop and mobile
};
```

```javascript
// In test file
await percy.snapshot(page, 'Homepage');
```

**Playwright Screenshots**:
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
  },
  expect: {
    toHaveScreenshot: {
      threshold: 0.2, // 20% pixel difference tolerance
    },
  },
});

// In test
test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png');
});
```

### Snapshot Strategies

**Component-level snapshots** (Storybook):
```jsx
// Button.stories.jsx
export default {
  title: 'Components/Button',
  component: Button,
};

export const Primary = {
  args: { variant: 'primary', children: 'Click me' },
  play: async ({ canvasElement }) => {
    await expect(canvasElement).toMatchSnapshot();
  },
};
```

**Page-level snapshots** (E2E):
```typescript
// Test critical user flows
test('checkout flow visual regression', async ({ page }) => {
  await page.goto('/products');
  await expect(page).toHaveScreenshot('products-page.png');
  
  await page.click('[data-testid="add-to-cart"]');
  await expect(page).toHaveScreenshot('cart-page.png');
  
  await page.click('[data-testid="checkout"]');
  await expect(page).toHaveScreenshot('checkout-page.png');
});
```

**State-based snapshots**: Capture components in different states (loading, error, success, empty).

### Handling Expected Changes

**Approval workflow**: Visual diffs require manual approval before updating baselines.

**Tolerance thresholds**: Allow small differences (e.g., 0.2% pixel difference) for anti-aliasing variations.

**Ignored regions**: Exclude dynamic content (timestamps, user avatars) from comparison:

```typescript
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [page.locator('[data-testid="timestamp"]')],
});
```

## Design Token Validation

### Automated Checks for Token Usage

**ESLint rule** (prevent magic numbers):
```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'no-magic-numbers': ['error', {
      ignore: [0, 1], // Allow 0 and 1
      ignoreArrayIndexes: true,
    }],
  },
};
```

**Custom lint rule** (enforce design tokens):
```javascript
// eslint-plugin-design-tokens.js
module.exports = {
  rules: {
    'use-design-tokens': {
      create(context) {
        return {
          Literal(node) {
            // Flag raw pixel values like '16px', '24px'
            if (typeof node.value === 'string' && /^\d+px$/.test(node.value)) {
              context.report({
                node,
                message: 'Use design tokens instead of raw pixel values',
              });
            }
          },
        };
      },
    },
  },
};
```

**Stylelint for CSS**:
```javascript
// .stylelintrc.js
module.exports = {
  rules: {
    'declaration-property-value-disallowed-list': {
      '/^(padding|margin|gap)$/': [
        /\d+px/, // Disallow raw px values
      ],
    },
  },
};
```

### Token Existence Validation

**Build-time check**:
```javascript
// scripts/validate-tokens.js
const tokens = require('./design-tokens.json');
const usedTokens = extractTokensFromCodebase();

usedTokens.forEach(token => {
  if (!tokens[token]) {
    throw new Error(`Token ${token} is used but not defined`);
  }
});
```

## Component Library Compliance

### Checking Design System Usage

**Static analysis** (find custom components that should use design system):
```javascript
// scripts/check-design-system-usage.js
const fs = require('fs');
const path = require('path');

function findCustomButtons(dir) {
  const files = fs.readdirSync(dir);
  const customButtons = [];
  
  files.forEach(file => {
    const content = fs.readFileSync(path.join(dir, file), 'utf8');
    // Look for button-like components not using design system
    if (content.includes('<button') && !content.includes('@pax8/propulsion')) {
      customButtons.push(file);
    }
  });
  
  return customButtons;
}
```

**Bundle analysis**: Check that design system components are imported, not reimplemented.

### Component API Compliance

**TypeScript types** enforce consistent component APIs:
```typescript
// Design system button interface
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

// Custom buttons must match
function CustomButton(props: ButtonProps) {
  // Implementation
}
```

## Cross-Browser and Cross-Device Consistency Testing

### Browser Testing Matrix

Test critical flows across:
- **Chrome** (latest)
- **Firefox** (latest)
- **Safari** (latest)
- **Edge** (latest)

**Playwright multi-browser**:
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

### Device Testing

**Responsive breakpoints**:
```typescript
test('mobile layout consistency', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 }); // iPhone
  await page.goto('/');
  await expect(page).toHaveScreenshot('mobile-homepage.png');
});
```

**Real device testing**: Use BrowserStack, Sauce Labs, or physical devices for final validation.

## Responsive Layout Verification

### Breakpoint Testing

**Test each breakpoint**:
```typescript
const breakpoints = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 },
};

Object.entries(breakpoints).forEach(([name, size]) => {
  test(`${name} layout`, async ({ page }) => {
    await page.setViewportSize(size);
    await page.goto('/');
    await expect(page).toHaveScreenshot(`${name}-layout.png`);
  });
});
```

### Layout Shift Detection

**CLS (Cumulative Layout Shift) monitoring**:
```javascript
// Monitor layout shifts
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.value > 0.1) { // Significant shift
      console.warn('Layout shift detected', entry);
    }
  }
}).observe({ entryTypes: ['layout-shift'] });
```

## Dark Mode / Theme Testing

### Theme Coverage

**Test every component in every theme**:
```typescript
const themes = ['light', 'dark', 'brand-a', 'brand-b'];

themes.forEach(theme => {
  test(`Button in ${theme} theme`, async ({ page }) => {
    await page.goto(`/?theme=${theme}`);
    await expect(page.locator('[data-testid="button"]'))
      .toHaveScreenshot(`button-${theme}.png`);
  });
});
```

### Contrast Ratio Validation

**Automated contrast checking**:
```javascript
// Check WCAG AA compliance
import { getContrast } from 'polished';

const contrast = getContrast('#ffffff', '#3b82f6'); // Should be >= 4.5:1
if (contrast < 4.5) {
  throw new Error('Contrast ratio too low');
}
```

## QA and Test Engineer Perspective

### Visual Regression Test Strategy

**Establish baseline**: Capture initial screenshots of all critical pages and components after design system implementation.

**Test frequency**: Run visual regression tests on every PR, not just releases. Catch inconsistencies early.

**Component coverage**: Test design system components in isolation (Storybook) and in context (full pages).

**Example workflow**:
1. Developer creates PR
2. CI runs visual regression tests
3. Diffs appear in Chromatic/Percy
4. QA reviews and approves/rejects changes
5. Approved changes update baseline

### Design Token Validation in QA

**Manual verification checklist**:
- [ ] No raw pixel values in CSS (use tokens)
- [ ] Spacing follows 4px/8px scale
- [ ] Colors match design system palette
- [ ] Typography uses design system fonts and sizes

**Automated checks**: Integrate token validation into CI/CD pipeline. Fail builds if tokens are bypassed.

**Token audit**: Periodically audit codebase for design token violations. Create tickets for fixes.

### Component Library Compliance Testing

**Component inventory**: Maintain list of all custom components. Track which should be replaced with design system equivalents.

**Usage tracking**: Monitor design system adoption metrics. Flag features using custom components instead of design system.

**Migration testing**: When migrating custom components to design system, verify:
- Visual appearance matches (visual regression)
- Functionality preserved (functional tests)
- Accessibility maintained (a11y tests)

### Cross-Browser Visual Consistency

**Browser-specific issues to watch**:
- Font rendering differences (especially custom fonts)
- CSS Grid/Flexbox rendering variations
- Color rendering (especially gradients)
- Shadow rendering differences

**Testing approach**: Use visual regression testing across browsers. Flag browser-specific visual differences for investigation.

**Documentation**: Maintain known browser differences document. Update as issues are discovered and resolved.

### Responsive Design Testing

**Breakpoint verification**: Test all breakpoints defined in design system. Verify components adapt correctly.

**Layout consistency**: Ensure same content appears correctly across breakpoints. No horizontal scrolling on mobile.

**Touch target sizes**: Verify interactive elements meet minimum touch target size (44x44px) on mobile.

**Orientation testing**: Test portrait and landscape orientations on mobile devices.

### Theme and Dark Mode Testing

**Theme coverage**: Test all themes (light, dark, brand variants) for every component.

**Contrast validation**: Verify text contrast meets WCAG AA standards in all themes.

**Theme switching**: Test runtime theme switching. Verify smooth transitions, no flash of incorrect theme.

**Component state coverage**: Test components in all states (default, hover, focus, disabled, error) in all themes.

**Accessibility in dark mode**: Ensure focus indicators, error states, and status colors remain visible and accessible in dark mode.
