# Navigation — Testing

## Contents

- [Route Guard Testing](#route-guard-testing)
- [Deep Link Verification](#deep-link-verification)
- [Breadcrumb Accuracy](#breadcrumb-accuracy)
- [Navigation Accessibility Testing](#navigation-accessibility-testing)
- [Mobile Navigation Testing](#mobile-navigation-testing)
- [Back Button Behavior](#back-button-behavior)
- [End-to-End Navigation Testing](#end-to-end-navigation-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Route Guard Testing

Route guards are critical security and UX components that control access to routes. Comprehensive testing ensures users are redirected appropriately and unauthorized access is prevented.

### Authentication Redirects

Test that unauthenticated users attempting to access protected routes are redirected to the login page:

```typescript
// Vue Router example
describe('Authentication Route Guards', () => {
  it('redirects unauthenticated users to login', async () => {
    const router = createRouter({ /* ... */ });
    router.beforeEach((to, from, next) => {
      if (to.meta.requiresAuth && !isAuthenticated()) {
        next({ name: 'login', query: { redirect: to.fullPath } });
      } else {
        next();
      }
    });

    await router.push('/dashboard');
    expect(router.currentRoute.value.name).toBe('login');
    expect(router.currentRoute.value.query.redirect).toBe('/dashboard');
  });
});
```

```typescript
// React Router example
describe('Authentication Route Guards', () => {
  it('redirects unauthenticated users to login', () => {
    const { result } = renderHook(() => useNavigate(), {
      wrapper: ({ children }) => (
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={
                <RequireAuth>
                  <Dashboard />
                </RequireAuth>
              } />
            </Routes>
            {children}
          </MemoryRouter>
        </AuthProvider>
      ),
    });

    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });
});
```

### Permission Checks

Verify that users without required permissions cannot access permission-gated routes:

```typescript
// Vue Router with permission meta
it('blocks access when user lacks required permission', async () => {
  const user = { permissions: ['read:orders'] };
  const router = createRouter({
    routes: [{
      path: '/admin/users',
      meta: { requiredPermission: 'admin:users' }
    }]
  });

  router.beforeEach((to, from, next) => {
    if (to.meta.requiredPermission && 
        !user.permissions.includes(to.meta.requiredPermission)) {
      next({ name: 'forbidden' });
    } else {
      next();
    }
  });

  await router.push('/admin/users');
  expect(router.currentRoute.value.name).toBe('forbidden');
});
```

### Programmatic Navigation

Test navigation triggered by code (not user clicks):

```typescript
it('handles programmatic navigation correctly', async () => {
  const router = useRouter();
  
  // Simulate navigation after form submission
  await submitForm();
  await router.push('/success');
  
  expect(router.currentRoute.value.path).toBe('/success');
  expect(screen.getByText('Form submitted successfully')).toBeVisible();
});
```

## Deep Link Verification

Deep links allow users to navigate directly to any URL. Verify that navigating directly to URLs loads the correct content and state.

### Direct URL Navigation

```typescript
// Playwright E2E test
test('deep link to order detail page loads correctly', async ({ page }) => {
  await page.goto('/orders/12345');
  
  await expect(page).toHaveURL('/orders/12345');
  await expect(page.locator('[data-testid="order-id"]')).toContainText('12345');
  await expect(page.locator('[data-testid="order-status"]')).toBeVisible();
});
```

### State Restoration

Test that deep links restore application state correctly:

```typescript
test('deep link restores filter state from query params', async ({ page }) => {
  await page.goto('/orders?status=completed&date=2024-01-01');
  
  await expect(page.locator('[data-testid="status-filter"]')).toHaveValue('completed');
  await expect(page.locator('[data-testid="date-filter"]')).toHaveValue('2024-01-01');
  await expect(page.locator('[data-testid="order-list"]')).toContainText('Completed');
});
```

### Error Handling

Verify graceful handling of invalid deep links:

```typescript
test('invalid deep link shows appropriate error', async ({ page }) => {
  await page.goto('/orders/999999999');
  
  await expect(page.locator('[data-testid="error-message"]')).toContainText(
    'Order not found'
  );
  await expect(page.locator('[data-testid="back-to-orders"]')).toBeVisible();
});
```

## Breadcrumb Accuracy

Breadcrumbs provide navigation context and should accurately reflect the current navigation path.

### Path Matching

```typescript
test('breadcrumbs match navigation path', async ({ page }) => {
  await page.goto('/settings/notifications/email');
  
  const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
  await expect(breadcrumbs).toContainText('Settings');
  await expect(breadcrumbs).toContainText('Notifications');
  await expect(breadcrumbs).toContainText('Email');
});
```

### Dynamic Segment Resolution

Test that dynamic route segments resolve correctly in breadcrumbs:

```typescript
test('breadcrumbs resolve dynamic segments', async ({ page }) => {
  await page.goto('/orders/12345');
  
  const breadcrumb = page.locator('[data-testid="breadcrumb-order"]');
  // Should show order name, not ID
  await expect(breadcrumb).toContainText('Order #12345');
  await expect(breadcrumb).not.toContainText('12345'); // If ID shouldn't be shown
});
```

### Breadcrumb Navigation

Verify breadcrumbs are clickable and navigate correctly:

```typescript
test('breadcrumb navigation works', async ({ page }) => {
  await page.goto('/settings/notifications/email');
  
  await page.click('[data-testid="breadcrumb-settings"]');
  await expect(page).toHaveURL('/settings');
  await expect(page.locator('h1')).toContainText('Settings');
});
```

## Navigation Accessibility Testing

Accessibility is critical for navigation. Test keyboard navigation, screen reader announcements, and focus management.

### Keyboard Navigation

```typescript
test('keyboard navigation through nav items', async ({ page }) => {
  await page.goto('/');
  
  // Tab to first nav item
  await page.keyboard.press('Tab');
  await expect(page.locator('[data-testid="nav-dashboard"]')).toHaveFocus();
  
  // Arrow keys navigate (if supported)
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('[data-testid="nav-orders"]')).toHaveFocus();
  
  // Enter activates
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL('/orders');
});
```

### Screen Reader Announcements

```typescript
test('screen reader announces current page', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Check aria-current on active nav item
  const activeNav = page.locator('[data-testid="nav-dashboard"]');
  await expect(activeNav).toHaveAttribute('aria-current', 'page');
  
  // Check document title
  await expect(page).toHaveTitle(/Dashboard/i);
});
```

### Skip-to-Content Links

```typescript
test('skip-to-content link is first focusable element', async ({ page }) => {
  await page.goto('/');
  
  await page.keyboard.press('Tab');
  const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
  expect(focusedElement).toBe('skip-to-content');
  
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toHaveFocus();
});
```

### Focus Management on Route Change

```typescript
// Vue Router afterEach hook test
test('focus moves to main content on route change', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="nav-orders"]');
  
  // Wait for route change
  await page.waitForURL('/orders');
  
  // Focus should be on main content or h1
  const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
  expect(['MAIN', 'H1', 'ARTICLE']).toContain(focusedElement);
});
```

```typescript
// React useEffect on location test
test('focus management on location change', () => {
  const { rerender } = render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <App />
    </MemoryRouter>
  );
  
  rerender(
    <MemoryRouter initialEntries={['/orders']}>
      <App />
    </MemoryRouter>
  );
  
  expect(document.activeElement).toBe(screen.getByRole('main'));
});
```

## Mobile Navigation Testing

Mobile navigation has unique behaviors that require specific testing.

### Hamburger Menu Toggle

```typescript
test('hamburger menu opens and closes', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile test only');
  
  await page.goto('/');
  
  // Menu should be closed initially
  await expect(page.locator('[data-testid="mobile-nav-drawer"]')).not.toBeVisible();
  
  // Open menu
  await page.click('[data-testid="mobile-nav-toggle"]');
  await expect(page.locator('[data-testid="mobile-nav-drawer"]')).toBeVisible();
  
  // Close menu
  await page.click('[data-testid="mobile-nav-toggle"]');
  await expect(page.locator('[data-testid="mobile-nav-drawer"]')).not.toBeVisible();
});
```

### Focus Trap in Drawer

```typescript
test('focus trap inside mobile drawer', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile test only');
  
  await page.goto('/');
  await page.click('[data-testid="mobile-nav-toggle"]');
  
  // Tab through items
  await page.keyboard.press('Tab');
  await expect(page.locator('[data-testid="nav-item-1"]')).toHaveFocus();
  
  // Tab to last item, then Tab again should wrap to first
  // (implementation dependent)
});
```

### Body Scroll Lock

```typescript
test('body scroll locked when drawer open', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile test only');
  
  await page.goto('/');
  
  const bodyBefore = await page.evaluate(() => document.body.style.overflow);
  
  await page.click('[data-testid="mobile-nav-toggle"]');
  
  const bodyAfter = await page.evaluate(() => document.body.style.overflow);
  expect(bodyAfter).toBe('hidden');
  
  await page.click('[data-testid="mobile-nav-toggle"]');
  const bodyAfterClose = await page.evaluate(() => document.body.style.overflow);
  expect(bodyAfterClose).not.toBe('hidden');
});
```

### Escape Key to Close

```typescript
test('Escape key closes mobile drawer', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile test only');
  
  await page.goto('/');
  await page.click('[data-testid="mobile-nav-toggle"]');
  await expect(page.locator('[data-testid="mobile-nav-drawer"]')).toBeVisible();
  
  await page.keyboard.press('Escape');
  await expect(page.locator('[data-testid="mobile-nav-drawer"]')).not.toBeVisible();
});
```

## Back Button Behavior

In SPAs, browser back/forward buttons must work correctly without breaking application state.

### Browser Back Navigation

```typescript
test('browser back button navigates correctly', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="nav-orders"]');
  await expect(page).toHaveURL('/orders');
  
  await page.goBack();
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
});
```

### Route State Preservation

```typescript
test('route state preserved on back navigation', async ({ page }) => {
  await page.goto('/orders');
  await page.fill('[data-testid="search"]', 'test query');
  await page.click('[data-testid="nav-dashboard"]');
  
  await page.goBack();
  await expect(page).toHaveURL('/orders');
  await expect(page.locator('[data-testid="search"]')).toHaveValue('test query');
});
```

### History Stack Management

```typescript
test('navigation history stack managed correctly', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="nav-orders"]');
  await page.click('[data-testid="order-123"]');
  
  // Back should go to orders list
  await page.goBack();
  await expect(page).toHaveURL('/orders');
  
  // Back again should go to dashboard
  await page.goBack();
  await expect(page).toHaveURL('/dashboard');
});
```

## End-to-End Navigation Testing

E2E tests verify complete navigation flows using Playwright.

### Complete Navigation Flow

```typescript
test('complete navigation flow', async ({ page }) => {
  // Start at home
  await page.goto('/');
  await expect(page).toHaveURL('/');
  
  // Navigate to section
  await page.click('[data-testid="nav-orders"]');
  await expect(page).toHaveURL('/orders');
  await expect(page.locator('h1')).toContainText('Orders');
  
  // Navigate to detail
  await page.click('[data-testid="order-123"]');
  await expect(page).toHaveURL('/orders/123');
  
  // Verify breadcrumbs
  const breadcrumbs = page.locator('[data-testid="breadcrumbs"]');
  await expect(breadcrumbs).toContainText('Orders');
  await expect(breadcrumbs).toContainText('Order #123');
  
  // Navigate via breadcrumb
  await page.click('[data-testid="breadcrumb-orders"]');
  await expect(page).toHaveURL('/orders');
});
```

### URL Verification

```typescript
test('URL reflects navigation state', async ({ page }) => {
  await page.goto('/orders');
  
  // Apply filters
  await page.selectOption('[data-testid="status-filter"]', 'completed');
  await page.fill('[data-testid="date-filter"]', '2024-01-01');
  
  // URL should update
  await expect(page).toHaveURL(/\/orders\?status=completed&date=2024-01-01/);
  
  // Deep link should restore state
  await page.goto('/orders?status=completed&date=2024-01-01');
  await expect(page.locator('[data-testid="status-filter"]')).toHaveValue('completed');
});
```

### Content Verification

```typescript
test('content loads correctly after navigation', async ({ page }) => {
  await page.goto('/orders');
  
  // Wait for content to load
  await expect(page.locator('[data-testid="order-list"]')).toBeVisible();
  await expect(page.locator('[data-testid="order-list"]')).not.toBeEmpty();
  
  // Navigate and verify new content
  await page.click('[data-testid="order-123"]');
  await expect(page.locator('[data-testid="order-detail"]')).toBeVisible();
  await expect(page.locator('[data-testid="order-id"]')).toContainText('123');
});
```

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize testing based on risk and user impact:

1. **Route Guards** (Highest Priority)
   - Authentication redirects prevent unauthorized access
   - Permission checks enforce security boundaries
   - Test all guard combinations: authenticated/unauthenticated, with/without permissions

2. **Deep Links** (High Priority)
   - Users bookmark and share URLs
   - Broken deep links create poor UX
   - Test all public routes, dynamic segments, query parameters

3. **Permission-Gated Routes** (High Priority)
   - Security-critical: users must not access unauthorized content
   - Test edge cases: partial permissions, expired sessions, role changes

4. **Breadcrumbs** (Medium Priority)
   - Navigation context helps users understand location
   - Test accuracy, dynamic resolution, navigation functionality

5. **Mobile Navigation** (Medium Priority)
   - Mobile users represent significant portion of traffic
   - Test hamburger behavior, focus management, scroll lock

6. **Accessibility** (Medium Priority)
   - Legal and ethical requirement
   - Test keyboard navigation, screen readers, focus management

### Exploratory Testing Guidance

Beyond scripted tests, exploratory testing uncovers edge cases:

**Rapid Navigation**
- Quickly click through nav items, back/forward buttons
- Look for: loading states, flickering, broken layouts, state loss

**Browser Back/Forward**
- Navigate forward through several pages, then use browser back
- Look for: broken state, missing data, incorrect URLs, focus issues

**Deep Links with Expired Sessions**
- Bookmark a protected route, wait for session to expire, navigate to bookmark
- Look for: proper redirect to login, redirect URL preservation, session handling

**Concurrent Navigation**
- Open multiple tabs, navigate in one, check others
- Look for: state synchronization, session conflicts, data consistency

**Network Conditions**
- Test navigation with slow 3G, offline mode, intermittent connectivity
- Look for: timeout handling, error states, retry mechanisms

### Test Data Management

Routes may have varying data states that affect navigation:

**Empty States**
- `/orders` with no orders: should show empty state, not error
- `/settings` with no preferences: should show defaults

**Loaded States**
- `/orders` with 100+ orders: pagination, filtering, sorting work
- `/dashboard` with complex data: charts load, widgets render

**Error States**
- `/orders/999999`: 404 handled gracefully
- `/orders` with API error: error message, retry option, fallback navigation

**Dynamic Data**
- Routes that depend on real-time data: WebSocket updates, polling
- Routes with user-specific data: personalization, permissions

### Test Environment Considerations

**MFE vs Monolith Routing**
- MFE environments: shell routes vs MFE routes, route registration timing
- Monolith: simpler routing, but still test route guards, deep links
- Different environments may have different route configurations

**Development vs Production**
- Development: hot reloading may affect route state
- Production: CDN caching, route preloading, code splitting

**Cross-Browser Testing**
- Browser history API differences (Safari vs Chrome)
- Focus management differences
- Mobile browser quirks (iOS Safari, Chrome Mobile)

### Regression Strategy

Focus regression testing on core navigation paths:

**Core Navigation Paths**
- Home → Primary Sections → Detail Pages
- Settings → Sub-settings → Individual Preferences
- Dashboard → Widgets → Drill-down Views

**Route Guard Rules**
- Authentication requirements don't regress
- Permission checks remain enforced
- Redirect URLs preserved correctly

**Breadcrumb Accuracy**
- Breadcrumbs match route hierarchy
- Dynamic segments resolve correctly
- Navigation via breadcrumbs works

### Defect Patterns

Common navigation defects to watch for:

**Stale Breadcrumbs**
- Breadcrumbs don't update after navigation
- Dynamic segments show IDs instead of names
- Breadcrumb trail incomplete or incorrect

**Broken Deep Links After Refactors**
- Route paths changed but deep links not updated
- Query parameter names changed
- Route structure refactored but URLs not migrated

**Focus Not Managed**
- Focus doesn't move to main content on route change
- Focus trapped in closed mobile menu
- Skip-to-content link doesn't work

**Route Guard Bypasses**
- Unauthenticated users can access protected routes
- Users without permissions can access restricted content
- Guard logic has race conditions

**Mobile Navigation Issues**
- Hamburger menu doesn't close on navigation
- Body scroll not unlocked when drawer closes
- Focus escapes drawer when it shouldn't

**Browser History Problems**
- Back button doesn't work correctly
- History stack corrupted
- State lost on back navigation
