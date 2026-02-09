# Navigation -- Gotchas

## Contents

- [Hamburger Menus Hiding Critical Navigation](#hamburger-menus-hiding-critical-navigation)
- [Breadcrumbs Out of Sync](#breadcrumbs-out-of-sync)
- [MFE Navigation State Conflicts](#mfe-navigation-state-conflicts)
- [Deep Links Breaking After Route Refactors](#deep-links-breaking-after-route-refactors)
- [Mobile Nav Drawer Issues](#mobile-nav-drawer-issues)
- [Route Guard Performance Issues](#route-guard-performance-issues)
- [Scroll Position Not Restored](#scroll-position-not-restored)
- [Active Nav State Lost on Refresh](#active-nav-state-lost-on-refresh)
- [Nested Routes Causing Layout Shifts](#nested-routes-causing-layout-shifts)
- [Browser History Pollution](#browser-history-pollution)

## Hamburger Menus Hiding Critical Navigation

**The Problem:**

Hiding primary navigation behind hamburger menus significantly reduces discoverability. Users don't explore what they can't see, leading to:
- Lower feature discovery
- Increased support requests ("Where is X?")
- Reduced user efficiency
- Poor mobile-to-desktop experience parity

**Why It Happens:**

- Designers prioritize "clean" interfaces
- Mobile-first design applied to desktop
- Assumption that users will explore hidden menus

**The Fix:**

```jsx
// ❌ Bad: All navigation hidden
function Navigation() {
  return (
    <div className="mobile-only-nav">
      <HamburgerMenu>
        <NavItems /> {/* Everything hidden */}
      </HamburgerMenu>
    </div>
  )
}

// ✅ Good: Primary nav visible, secondary in hamburger
function Navigation() {
  return (
    <>
      <TopNav primaryItems={primaryNav} /> {/* Always visible */}
      <HamburgerMenu secondaryItems={secondaryNav} /> {/* Secondary only */}
    </>
  )
}

// ✅ Good: Responsive - visible on desktop, hamburger on mobile
function Navigation() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  
  return isMobile ? (
    <HamburgerMenu><NavItems /></HamburgerMenu>
  ) : (
    <TopNav><NavItems /></TopNav>
  )
}
```

**Best Practice:**

- Desktop: Always show primary navigation
- Mobile: Use bottom nav bar for primary actions, hamburger for secondary
- Never hide critical navigation behind hamburger on desktop

## Breadcrumbs Out of Sync

**The Problem:**

Breadcrumbs show a path that doesn't match the actual route hierarchy or how users navigated. This breaks user trust and mental models.

**Common Causes:**

1. **Manual Breadcrumb Configuration**: Breadcrumbs manually configured and not updated when routes change
2. **History-Based Breadcrumbs**: Breadcrumbs generated from navigation history instead of route structure
3. **Stale Breadcrumb Data**: Breadcrumb data cached and not refreshed

**Example:**

```jsx
// ❌ Bad: Manual configuration that gets out of sync
const breadcrumbMap = {
  '/billing': 'Billing',
  '/billing/invoices': 'Invoices',
  '/billing/invoices/:id': 'Invoice Details'
  // Route changes to /billing/invoices/:invoiceId but breadcrumb map not updated
}

// ✅ Good: Auto-generated from route tree
function generateBreadcrumbs(pathname, routeTree) {
  return routeTree
    .findMatchingRoutes(pathname)
    .filter(route => route.meta?.breadcrumb)
    .map(route => ({
      label: route.meta.breadcrumb,
      path: route.path
    }))
}
```

**The Fix:**

```javascript
// Vue Router - Use route.matched
function useBreadcrumbs() {
  const route = useRoute()
  
  return computed(() => {
    return route.matched
      .filter(record => record.meta?.breadcrumb)
      .map(record => ({
        label: record.meta.breadcrumb,
        path: record.path
      }))
  })
}

// React Router - Generate from route configuration
function useBreadcrumbs() {
  const location = useLocation()
  const routes = useRoutes() // From route config
  
  return useMemo(() => {
    return generateBreadcrumbsFromRouteTree(location.pathname, routes)
  }, [location.pathname, routes])
}
```

**Prevention:**

- Generate breadcrumbs from route configuration, not navigation history
- Use route meta fields for breadcrumb labels
- Test breadcrumbs match route hierarchy after route changes

## MFE Navigation State Conflicts

**The Problem:**

In Micro Frontend architectures, multiple MFEs may try to control the URL simultaneously, causing navigation conflicts, broken deep links, or inconsistent state.

**Common Scenarios:**

1. **Two MFEs Both Navigate**: Billing MFE and Products MFE both try to update the URL
2. **Shell vs MFE Router Conflict**: Shell router and MFE router both handle navigation
3. **Navigation Events Lost**: Navigation events between MFEs not properly coordinated

**Example:**

```javascript
// ❌ Bad: MFE directly manipulates URL
// Billing MFE
function navigateToInvoice(id) {
  window.location.href = `/billing/invoices/${id}` // Conflicts with shell router
}

// Products MFE (simultaneously)
function navigateToProduct(id) {
  window.history.pushState(null, '', `/products/${id}`) // Also conflicts
}
```

**The Fix:**

```javascript
// ✅ Good: Shell owns routing, MFEs communicate via events
// Shell application
class NavigationService {
  navigate(path) {
    router.push(path) // Shell router controls all navigation
  }
  
  onNavigate(handler) {
    window.addEventListener('mf-navigate', (e) => {
      this.navigate(e.detail.path)
    })
  }
}

// MFE - Emit navigation events
function navigateToInvoice(id) {
  window.dispatchEvent(new CustomEvent('mf-navigate', {
    detail: { path: `/billing/invoices/${id}` }
  }))
}

// Shell listens and routes
navigationService.onNavigate((path) => {
  router.push(path)
})
```

**Alternative: Route Registry Pattern:**

```javascript
// Shared route registry
const routeRegistry = {
  'billing-invoice': {
    path: '/billing/invoices/:id',
    mfe: 'billing'
  },
  'product-detail': {
    path: '/products/:id',
    mfe: 'products'
  }
}

// Navigation service uses registry
class NavigationService {
  navigate(routeName, params) {
    const route = routeRegistry[routeName]
    const path = this.buildPath(route.path, params)
    router.push(path) // Shell routes, loads appropriate MFE
  }
}
```

**Best Practice:**

- Shell application owns the router
- MFEs communicate navigation intent via events or service
- Use route registry pattern for cross-MFE navigation
- Test navigation coordination in integrated environment

## Deep Links Breaking After Route Refactors

**The Problem:**

When routes are refactored (renamed, restructured, or removed), existing deep links break. This affects:
- Shared URLs (emails, documentation)
- Bookmarks
- External integrations
- Search engine indexing

**Example:**

```javascript
// Old route structure
/billing/invoices/:id

// Refactored to
/financial/invoices/:id

// Old links break: 404 errors
```

**The Fix:**

**Redirect Strategy:**

```javascript
// Vue Router - Add redirects for old routes
const routes = [
  // New route
  {
    path: '/financial/invoices/:id',
    component: InvoiceDetail
  },
  // Redirect old route to new
  {
    path: '/billing/invoices/:id',
    redirect: to => `/financial/invoices/${to.params.id}`
  },
  // Or redirect entire section
  {
    path: '/billing',
    redirect: '/financial'
  }
]

// React Router
<Route 
  path="/billing/invoices/:id" 
  element={<Navigate to={`/financial/invoices/${useParams().id}`} replace />} 
/>
```

**Permanent Redirects (301):**

For permanent route changes, use HTTP 301 redirects (if using server-side routing):

```javascript
// Server-side redirect (Express example)
app.get('/billing/invoices/:id', (req, res) => {
  res.redirect(301, `/financial/invoices/${req.params.id}`)
})
```

**Route Versioning:**

For major refactors, consider route versioning:

```javascript
// Version routes
/v1/billing/invoices/:id  // Old, deprecated
/v2/financial/invoices/:id // New

// Or use query parameter
/financial/invoices/:id?v=2
```

**Best Practice:**

- Always add redirects when refactoring routes
- Document route changes and deprecation timeline
- Test all external links after refactoring
- Consider route versioning for major changes
- Monitor 404 errors to catch broken links

## Mobile Nav Drawer Issues

**The Problem:**

Mobile navigation drawers can have several issues:
- Content obscured without proper overlay
- No focus trap (keyboard users can tab outside)
- Body scroll not locked (content scrolls behind drawer)
- Drawer doesn't close on navigation
- Touch targets too small

**Common Issues:**

**1. Missing Overlay/Backdrop:**

```jsx
// ❌ Bad: Drawer overlays content without backdrop
<Drawer open={isOpen}>
  <NavMenu />
</Drawer>
// Content behind drawer is still visible and interactive

// ✅ Good: Proper overlay with backdrop
<>
  {isOpen && (
    <div 
      className="drawer-overlay"
      onClick={onClose}
      aria-hidden="true"
    />
  )}
  <Drawer open={isOpen}>
    <NavMenu />
  </Drawer>
</>
```

**2. No Focus Trap:**

```jsx
// ❌ Bad: Focus can escape drawer
function Drawer({ isOpen, children }) {
  return isOpen ? <aside>{children}</aside> : null
}
// Keyboard users can tab outside drawer

// ✅ Good: Focus trap implementation
function Drawer({ isOpen, children }) {
  const drawerRef = useRef(null)
  useFocusTrap(isOpen, drawerRef) // Custom hook
  
  return (
    <aside ref={drawerRef} role="dialog" aria-modal="true">
      {children}
    </aside>
  )
}
```

**3. Body Scroll Not Locked:**

```jsx
// ❌ Bad: Content scrolls behind drawer
function Drawer({ isOpen }) {
  return isOpen ? <aside><NavMenu /></aside> : null
}

// ✅ Good: Lock body scroll when drawer is open
function useBodyScrollLock(isLocked) {
  useEffect(() => {
    if (isLocked) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isLocked])
}

function Drawer({ isOpen }) {
  useBodyScrollLock(isOpen)
  return isOpen ? <aside><NavMenu /></aside> : null
}
```

**4. Drawer Doesn't Close on Navigation:**

```jsx
// ❌ Bad: Drawer stays open after navigation
function NavLink({ to, children }) {
  return <Link to={to}>{children}</Link>
}
// Drawer remains open when link is clicked

// ✅ Good: Close drawer on navigation
function NavLink({ to, children, onNavigate }) {
  const handleClick = () => {
    onNavigate() // Close drawer
  }
  
  return <Link to={to} onClick={handleClick}>{children}</Link>
}

// Or use effect to close on route change
useEffect(() => {
  setIsDrawerOpen(false)
}, [location.pathname])
```

**Best Practice:**

- Always include overlay/backdrop
- Implement focus trap for keyboard users
- Lock body scroll when drawer is open
- Close drawer on navigation or Escape key
- Ensure touch targets are at least 44x44px

## Route Guard Performance Issues

**The Problem:**

Route guards that run on every navigation can cause performance issues, especially if they:
- Make API calls
- Perform expensive permission checks
- Run synchronously blocking navigation

**Example:**

```javascript
// ❌ Bad: API call on every navigation
router.beforeEach(async (to, from, next) => {
  const user = await fetchUser() // Expensive API call
  if (to.meta.requiresAuth && !user) {
    next('/login')
  } else {
    next()
  }
})
// Navigation is slow, especially on slow networks

// ✅ Good: Cache user data, check cache first
let userCache = null
let userCacheTime = 0
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

router.beforeEach(async (to, from, next) => {
  // Use cache if fresh
  if (userCache && Date.now() - userCacheTime < CACHE_TTL) {
    if (to.meta.requiresAuth && !userCache) {
      next('/login')
    } else {
      next()
    }
    return
  }
  
  // Fetch only if cache expired
  userCache = await fetchUser()
  userCacheTime = Date.now()
  
  if (to.meta.requiresAuth && !userCache) {
    next('/login')
  } else {
    next()
  }
})
```

**Optimization Strategies:**

1. **Cache Guard Results**: Cache authentication/permission checks
2. **Lazy Load Guards**: Only load guards for routes that need them
3. **Parallel Checks**: Run multiple checks in parallel
4. **Skip Unnecessary Guards**: Don't run guards if route doesn't require them

```javascript
// ✅ Good: Skip guard if route doesn't require auth
router.beforeEach((to, from, next) => {
  if (!to.meta.requiresAuth) {
    next() // Skip auth check
    return
  }
  
  // Only check auth for protected routes
  if (!isAuthenticated()) {
    next('/login')
  } else {
    next()
  }
})
```

**Best Practice:**

- Cache guard results with appropriate TTL
- Skip guards for routes that don't need them
- Use lazy loading for guard logic
- Monitor guard performance in production

## Scroll Position Not Restored

**The Problem:**

When users navigate back using browser back button, scroll position is not restored, forcing users to scroll back to where they were.

**Why It Happens:**

- SPA routing doesn't automatically restore scroll position
- Scroll position not saved in history state
- Scroll restoration not implemented

**The Fix:**

**Vue Router scrollBehavior:**

```javascript
const router = createRouter({
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition // Restore saved position
    } else if (to.hash) {
      return { el: to.hash } // Scroll to hash
    } else {
      return { top: 0 } // Scroll to top for new routes
    }
  }
})
```

**React Router ScrollRestoration:**

```jsx
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

function ScrollRestoration() {
  const { pathname } = useLocation()
  const scrollPositions = useRef(new Map())
  
  useEffect(() => {
    // Save scroll position before navigation
    return () => {
      scrollPositions.current.set(pathname, window.scrollY)
    }
  }, [pathname])
  
  useEffect(() => {
    // Restore scroll position after navigation
    const savedPosition = scrollPositions.current.get(pathname)
    if (savedPosition !== undefined) {
      window.scrollTo(0, savedPosition)
    } else {
      window.scrollTo(0, 0) // New route, scroll to top
    }
  }, [pathname])
  
  return null
}
```

**Browser Native (if supported):**

```jsx
// Use browser's native scroll restoration
useEffect(() => {
  if ('scrollRestoration' in window.history) {
    window.history.scrollRestoration = 'auto'
  }
}, [])
```

**Best Practice:**

- Implement scroll restoration for back/forward navigation
- Scroll to top for new routes (not back navigation)
- Save scroll position in history state if needed
- Test with browser back/forward buttons

## Active Nav State Lost on Refresh

**The Problem:**

Active navigation state (highlighted current page) is lost on page refresh because it's stored only in client-side state.

**Why It Happens:**

- Active state determined by comparing current pathname to nav items
- On refresh, client-side state is lost
- Active state not determined server-side or from URL

**Example:**

```jsx
// ❌ Bad: Client-side only active state
const [activeItem, setActiveItem] = useState(null)

useEffect(() => {
  // Set active based on current route
  setActiveItem(currentRoute)
}, [currentRoute])
// Lost on refresh until JavaScript loads

// ✅ Good: Determine active state from URL
function NavItem({ to, children }) {
  const location = useLocation()
  const isActive = location.pathname.startsWith(to)
  // Always works, even on initial load
  return <Link to={to} className={isActive ? 'active' : ''}>{children}</Link>
}
```

**Server-Side Rendering (SSR) Fix:**

```jsx
// Server-side: Determine active state from request URL
function NavItem({ to, children, currentPath }) {
  const isActive = currentPath.startsWith(to)
  return (
    <Link to={to} className={isActive ? 'active' : ''}>
      {children}
    </Link>
  )
}

// Server renders with correct active state
<NavItem to="/billing" currentPath={req.path}>Billing</NavItem>
```

**Best Practice:**

- Always determine active state from URL/pathname, not client state
- Works on initial load and refresh
- Consider server-side rendering for instant active state
- Use `aria-current="page"` for accessibility

## Nested Routes Causing Layout Shifts

**The Problem:**

Nested routes can cause unexpected layout shifts when:
- Child routes have different layouts
- Layout components mount/unmount
- Route transitions cause content to jump

**Example:**

```jsx
// ❌ Bad: Different layouts cause shift
<Route path="/billing" element={<BillingLayout />}>
  <Route path="invoices" element={<InvoicesLayout />} /> {/* Different layout! */}
</Route>
// Layout shifts when navigating to invoices

// ✅ Good: Consistent layout structure
<Route path="/billing" element={<BillingLayout />}>
  <Route path="invoices" element={<InvoicesPage />} /> {/* Same layout wrapper */}
</Route>
```

**The Fix:**

**Consistent Layout Structure:**

```jsx
// Use same layout wrapper for all nested routes
function BillingLayout() {
  return (
    <div className="billing-layout">
      <BillingNav />
      <div className="billing-content">
        <Outlet /> {/* Child routes render here, same container */}
      </div>
    </div>
  )
}

// All child routes use same layout
<Route path="/billing" element={<BillingLayout />}>
  <Route path="invoices" element={<InvoicesList />} />
  <Route path="payments" element={<PaymentsList />} />
</Route>
```

**Skeleton Loading:**

```jsx
// Show skeleton during route transition to prevent shift
function BillingLayout() {
  const [isLoading, setIsLoading] = useState(false)
  const location = useLocation()
  
  useEffect(() => {
    setIsLoading(true)
    // Simulate loading
    setTimeout(() => setIsLoading(false), 100)
  }, [location.pathname])
  
  return (
    <div className="billing-layout">
      {isLoading ? <Skeleton /> : <Outlet />}
    </div>
  )
}
```

**Best Practice:**

- Use consistent layout structure for nested routes
- Avoid different layouts for parent/child routes
- Use skeleton loading during transitions
- Test layout stability across route changes

## Browser History Pollution

**The Problem:**

Programmatic navigations (e.g., redirects, replace operations) can pollute browser history, making back button behavior confusing.

**Common Scenarios:**

1. **Redirects Adding History**: Each redirect adds a history entry
2. **Replace Not Used**: Should use `replace` but uses `push`
3. **Multiple Navigations**: Rapid navigations create many history entries

**Example:**

```javascript
// ❌ Bad: Redirect adds unnecessary history entry
router.beforeEach((to, from, next) => {
  if (requiresAuth && !isAuthenticated()) {
    next('/login') // Adds /login to history
    // User clicks back, goes to protected route, redirects again
    // History: /protected -> /login -> /protected -> /login (polluted)
  }
})

// ✅ Good: Use replace for redirects
router.beforeEach((to, from, next) => {
  if (requiresAuth && !isAuthenticated()) {
    next({ path: '/login', replace: true }) // Replace, don't add to history
  }
})
```

**The Fix:**

**Use Replace for Redirects:**

```javascript
// Vue Router
next({ path: '/login', replace: true })

// React Router
navigate('/login', { replace: true })
```

**Clean Up Unnecessary History:**

```javascript
// After login redirect, replace history entry
router.push({ path: '/dashboard', replace: true })
// Instead of adding new entry, replace login entry
```

**Best Practice:**

- Use `replace: true` for redirects (login, unauthorized, etc.)
- Use `push` only for intentional user navigation
- Clean up history after authentication flows
- Test back button behavior after redirects
