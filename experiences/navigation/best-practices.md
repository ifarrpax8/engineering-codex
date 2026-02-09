# Navigation — Best Practices

## Contents

- [Consistent Navigation Position](#consistent-navigation-position)
- [Current Location Indication](#current-location-indication)
- [Breadcrumb Guidelines](#breadcrumb-guidelines)
- [Desktop Navigation Visibility](#desktop-navigation-visibility)
- [Navigation Item Limits](#navigation-item-limits)
- [Mega-Menu Anti-Patterns](#mega-menu-anti-patterns)
- [Skip-to-Content Links](#skip-to-content-links)
- [Focus Management on Route Change](#focus-management-on-route-change)
- [URL Design Conventions](#url-design-conventions)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Stack-Specific Patterns](#stack-specific-patterns)
- [MFE Navigation](#mfe-navigation)
- [Mobile Navigation Patterns](#mobile-navigation-patterns)

## Consistent Navigation Position

Navigation should appear in the same location across all pages. Moving navigation between sections confuses users and breaks muscle memory.

**✅ Good:**
- Top navigation bar always at the top
- Sidebar always on the left (or right, but consistent)
- Footer navigation always at the bottom

**❌ Bad:**
- Navigation moves from top to sidebar between sections
- Navigation disappears on certain pages
- Navigation position changes based on screen size inconsistently

```vue
<!-- Vue: Consistent AppShell layout -->
<template>
  <AppShell>
    <template #header>
      <TopNav />
    </template>
    <template #sidebar>
      <SideNav />
    </template>
    <template #main>
      <router-view />
    </template>
  </AppShell>
</template>
```

```tsx
// React: Consistent layout wrapper
function App() {
  return (
    <AppShell
      header={<TopNav />}
      sidebar={<SideNav />}
    >
      <Routes>
        <Route path="*" element={<PageLayout />} />
      </Routes>
    </AppShell>
  );
}
```

## Current Location Indication

Always highlight the current location in navigation. Users need clear visual and programmatic indication of where they are.

### Active State Styling

```vue
<!-- Vue Router: Active class binding -->
<template>
  <nav>
    <router-link
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      :class="{ 'nav-active': $route.path.startsWith(item.path) }"
    >
      {{ item.label }}
    </router-link>
  </nav>
</template>
```

```tsx
// React Router: useLocation for active state
function NavItem({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);
  
  return (
    <Link
      to={to}
      className={isActive ? 'nav-active' : ''}
      aria-current={isActive ? 'page' : undefined}
    >
      {children}
    </Link>
  );
}
```

### ARIA Current Attribute

Always include `aria-current="page"` on the active navigation item:

```html
<!-- HTML: ARIA current for screen readers -->
<nav aria-label="Main navigation">
  <a href="/dashboard" aria-current="page">Dashboard</a>
  <a href="/orders">Orders</a>
  <a href="/settings">Settings</a>
</nav>
```

## Breadcrumb Guidelines

Breadcrumbs provide navigation context and should appear when navigation depth exceeds 2 levels.

### When to Show Breadcrumbs

- **Show:** Navigation depth > 2 levels (e.g., `/settings/notifications/email`)
- **Hide:** Top-level pages (e.g., `/dashboard`, `/orders`)
- **Show:** Detail pages with parent context (e.g., `/orders/123`)

### Breadcrumb Structure

```vue
<!-- Vue: Breadcrumb component -->
<template>
  <nav aria-label="Breadcrumb" v-if="breadcrumbs.length > 1">
    <ol class="breadcrumb">
      <li v-for="(crumb, index) in breadcrumbs" :key="index">
        <router-link
          v-if="index < breadcrumbs.length - 1"
          :to="crumb.path"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else aria-current="page">{{ crumb.label }}</span>
        <span v-if="index < breadcrumbs.length - 1" aria-hidden="true">/</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(r => r.meta?.breadcrumb);
  return matched.map(r => ({
    path: r.path,
    label: r.meta.breadcrumb
  }));
});
</script>
```

```tsx
// React: Breadcrumb component
function Breadcrumbs() {
  const location = useLocation();
  const breadcrumbs = useMemo(() => {
    const paths = location.pathname.split('/').filter(Boolean);
    return paths.map((path, index) => ({
      label: formatBreadcrumbLabel(path),
      path: '/' + paths.slice(0, index + 1).join('/')
    }));
  }, [location.pathname]);

  if (breadcrumbs.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb">
      <ol>
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.path}>
            {index < breadcrumbs.length - 1 ? (
              <Link to={crumb.path}>{crumb.label}</Link>
            ) : (
              <span aria-current="page">{crumb.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

## Desktop Navigation Visibility

Don't hide primary navigation behind a hamburger menu on desktop. Research shows this reduces discoverability by approximately 50%.

**✅ Good:**
- Desktop: Always-visible top nav or sidebar
- Mobile: Hamburger menu for space efficiency

**❌ Bad:**
- Hamburger menu on desktop (>1024px screens)
- Hidden navigation requiring hover to reveal
- Navigation only accessible via keyboard shortcut

```css
/* Responsive navigation visibility */
.desktop-nav {
  display: flex;
}

.mobile-nav-toggle {
  display: none;
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
  
  .mobile-nav-toggle {
    display: block;
  }
}
```

## Navigation Item Limits

Follow the 7±2 rule: limit top-level navigation items to 5-9 items. Use grouping or sections for additional items.

**✅ Good:**
- 5-7 primary navigation items
- Grouped secondary items in dropdowns or sections
- Clear hierarchy: primary → secondary → tertiary

**❌ Bad:**
- 15+ top-level navigation items
- Flat structure with no grouping
- All items given equal visual weight

```vue
<!-- Vue: Grouped navigation -->
<template>
  <nav>
    <div class="nav-primary">
      <router-link v-for="item in primaryNav" :key="item.path" :to="item.path">
        {{ item.label }}
      </router-link>
    </div>
    <div class="nav-secondary">
      <NavDropdown :items="secondaryNav" />
    </div>
  </nav>
</template>
```

## Mega-Menu Anti-Patterns

Mega-menus (large dropdown menus with multiple columns) have several anti-patterns to avoid:

### Complexity Issues

**❌ Too Complex:**
- Multiple columns with dozens of links
- Nested categories within mega-menu
- Requires horizontal scrolling

**✅ Better Approach:**
- Limit to 2-3 columns maximum
- Use clear categorization
- Provide search within menu if needed

### Touch Device Failures

**❌ Hover-Triggered:**
- Mega-menu opens on hover (desktop-only pattern)
- Fails completely on touch devices
- No alternative for mobile users

**✅ Better Approach:**
- Click/tap to open on all devices
- Or use hover on desktop with click fallback
- Mobile: Use drawer or accordion pattern

### Performance Impact

**❌ Heavy Mega-Menus:**
- Loads all content on page load
- Includes images, complex layouts
- Blocks rendering

**✅ Better Approach:**
- Lazy load menu content
- Use lightweight markup
- Consider virtual scrolling for long lists

```tsx
// React: Lazy-loaded mega-menu
function MegaMenu({ items }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loadedContent, setLoadedContent] = useState(null);

  const handleOpen = async () => {
    if (!loadedContent) {
      const content = await import('./mega-menu-content');
      setLoadedContent(content.default);
    }
    setIsOpen(true);
  };

  return (
    <div onMouseEnter={handleOpen} onClick={handleOpen}>
      {isOpen && loadedContent && <MegaMenuContent content={loadedContent} />}
    </div>
  );
}
```

## Skip-to-Content Links

Skip-to-content links are an accessibility requirement. They must be the first focusable element on the page.

```html
<!-- HTML: Skip link as first element -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<header>
  <nav>...</nav>
</header>

<main id="main-content">
  <!-- Page content -->
</main>
```

```css
/* CSS: Skip link styling */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

```vue
<!-- Vue: Skip link component -->
<template>
  <a href="#main-content" class="skip-link" @click.prevent="skipToContent">
    Skip to main content
  </a>
</template>

<script setup>
function skipToContent() {
  const main = document.getElementById('main-content');
  main?.focus();
  main?.scrollIntoView({ behavior: 'smooth' });
}
</script>
```

## Focus Management on Route Change

When routes change, manage focus appropriately for accessibility and UX.

### Screen Reader Announcements

```vue
<!-- Vue Router: Announce route changes -->
<script setup>
import { watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

watch(() => route.path, (newPath) => {
  // Update document title for screen readers
  document.title = `${route.meta.title} - My App`;
  
  // Announce to screen readers
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = `Navigated to ${route.meta.title}`;
  document.body.appendChild(announcement);
  
  setTimeout(() => document.body.removeChild(announcement), 1000);
});
</script>
```

```tsx
// React: useEffect for focus management
function App() {
  const location = useLocation();
  
  useEffect(() => {
    // Update document title
    document.title = `${getPageTitle(location.pathname)} - My App`;
    
    // Move focus to main content
    const main = document.querySelector('main');
    if (main) {
      main.focus();
      main.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Announce to screen readers
    announceToScreenReader(`Navigated to ${getPageTitle(location.pathname)}`);
  }, [location.pathname]);
  
  return <Routes>...</Routes>;
}
```

### Vue Router afterEach Hook

```typescript
// Vue Router: Focus management in afterEach
router.afterEach((to, from) => {
  // Move focus to main content area
  const mainContent = document.querySelector('main') || document.querySelector('[role="main"]');
  if (mainContent) {
    mainContent.focus();
    // Or focus the h1 of the new page
    const h1 = mainContent.querySelector('h1');
    if (h1) {
      h1.focus();
    }
  }
  
  // Update page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - My App`;
  }
});
```

## URL Design Conventions

Well-designed URLs are readable, shareable, and maintainable.

### Naming Conventions

**✅ Good URLs:**
- `/settings/notifications` (lowercase, hyphens)
- `/orders/12345` (meaningful segments)
- `/users/john-doe` (slug-based, not ID)

**❌ Bad URLs:**
- `/Settings/Notifications` (mixed case)
- `/settings?tab=3` (opaque query params)
- `/users/12345` (exposed database IDs where possible)

### URL Structure

```typescript
// Vue Router: Clean URL structure
const routes = [
  {
    path: '/settings',
    children: [
      {
        path: 'notifications',
        meta: { breadcrumb: 'Notifications' }
      },
      {
        path: 'profile',
        meta: { breadcrumb: 'Profile' }
      }
    ]
  },
  {
    path: '/orders/:orderId',
    // Use slug instead of ID when possible
    props: true
  }
];
```

```tsx
// React Router: Meaningful URL segments
<Routes>
  <Route path="/settings">
    <Route path="notifications" element={<Notifications />} />
    <Route path="profile" element={<Profile />} />
  </Route>
  <Route path="/orders/:orderSlug" element={<OrderDetail />} />
</Routes>
```

## Keyboard Shortcuts

Provide keyboard shortcuts for power users, following the Cmd+K / Ctrl+K command palette pattern.

```vue
<!-- Vue: Command palette -->
<template>
  <CommandPalette v-if="isOpen" @close="isOpen = false" />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

const isOpen = ref(false);

function handleKeyDown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault();
    isOpen.value = !isOpen.value;
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>
```

```tsx
// React: Command palette hook
function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setIsOpen(prev => !prev);
      }
    }
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  return { isOpen, setIsOpen };
}
```

## Stack-Specific Patterns

### Vue Router

**beforeEach Guards:**
```typescript
router.beforeEach((to, from, next) => {
  // Authentication check
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }
  
  // Permission check
  if (to.meta.requiredPermission && !hasPermission(to.meta.requiredPermission)) {
    next({ name: 'forbidden' });
    return;
  }
  
  next();
});
```

**Meta Fields for Breadcrumbs/Titles:**
```typescript
{
  path: '/settings/notifications',
  meta: {
    title: 'Notification Settings',
    breadcrumb: 'Notifications',
    requiresAuth: true
  }
}
```

**scrollBehavior:**
```typescript
const router = createRouter({
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else if (to.hash) {
      return { el: to.hash };
    } else {
      return { top: 0 };
    }
  }
});
```

### React Router

**Loader Pattern for Data:**
```tsx
// React Router v6.4+ loaders
export async function orderLoader({ params }) {
  const order = await fetchOrder(params.orderId);
  if (!order) {
    throw new Response('Not Found', { status: 404 });
  }
  return order;
}

<Route path="/orders/:orderId" loader={orderLoader} element={<OrderDetail />} />
```

**useLocation for Active State:**
```tsx
function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link to={to} className={isActive ? 'active' : ''}>
      {children}
    </Link>
  );
}
```

**ScrollRestoration Component:**
```tsx
import { ScrollRestoration } from 'react-router-dom';

function App() {
  return (
    <Router>
      <ScrollRestoration />
      <Routes>...</Routes>
    </Router>
  );
}
```

### Propulsion Components

**AppShell:**
```tsx
import { AppShell } from '@pax8/propulsion';

<AppShell
  header={<TopNav />}
  sidebar={<SideNav />}
  footer={<Footer />}
>
  <Routes>...</Routes>
</AppShell>
```

**SideNav:**
```tsx
import { SideNav, SideNavItem } from '@pax8/propulsion';

<SideNav>
  <SideNavItem to="/dashboard" icon={<DashboardIcon />}>
    Dashboard
  </SideNavItem>
  <SideNavItem to="/orders" icon={<OrdersIcon />}>
    Orders
  </SideNavItem>
</SideNav>
```

**TopNav:**
```tsx
import { TopNav, TopNavItem } from '@pax8/propulsion';

<TopNav>
  <TopNavItem to="/dashboard">Dashboard</TopNavItem>
  <TopNavItem to="/orders">Orders</TopNavItem>
</TopNav>
```

### MUI Components

**Drawer:**
```tsx
import { Drawer } from '@mui/material';

<Drawer
  anchor="left"
  open={isOpen}
  onClose={() => setIsOpen(false)}
>
  <nav>
    <MenuItem onClick={() => navigate('/dashboard')}>Dashboard</MenuItem>
    <MenuItem onClick={() => navigate('/orders')}>Orders</MenuItem>
  </nav>
</Drawer>
```

**BottomNavigation:**
```tsx
import { BottomNavigation, BottomNavigationAction } from '@mui/material';

<BottomNavigation value={value} onChange={(e, newValue) => setValue(newValue)}>
  <BottomNavigationAction label="Dashboard" icon={<DashboardIcon />} />
  <BottomNavigationAction label="Orders" icon={<OrdersIcon />} />
</BottomNavigation>
```

**AppBar:**
```tsx
import { AppBar, Toolbar, Button } from '@mui/material';

<AppBar>
  <Toolbar>
    <Button color="inherit" onClick={() => navigate('/dashboard')}>
      Dashboard
    </Button>
    <Button color="inherit" onClick={() => navigate('/orders')}>
      Orders
    </Button>
  </Toolbar>
</AppBar>
```

## MFE Navigation

In micro-frontend architectures, navigation requires coordination between shell and MFEs.

### Shell-Owned Navigation

The shell owns the top-level navigation. MFEs register their routes and the shell coordinates navigation.

```typescript
// Shell: Route registration
interface MFERoute {
  path: string;
  component: () => Promise<any>;
  meta?: RouteMeta;
}

const mfeRoutes: MFERoute[] = [];

function registerMFERoute(route: MFERoute) {
  mfeRoutes.push(route);
  // Rebuild router with new routes
  rebuildRouter();
}
```

### Shared Navigation Events

```typescript
// Shared navigation event bus
class NavigationEventBus {
  private listeners: Map<string, Function[]> = new Map();
  
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }
  
  emit(event: string, data?: any) {
    this.listeners.get(event)?.forEach(cb => cb(data));
  }
}

// Shell emits navigation events
navigationBus.emit('navigate', { path: '/orders', state: {} });

// MFE listens for navigation events
navigationBus.on('navigate', ({ path, state }) => {
  // Update MFE internal state based on navigation
});
```

## Mobile Navigation Patterns

### Bottom Navigation

Use bottom navigation for primary mobile actions (maximum 5 items):

```tsx
// React: Bottom navigation
<BottomNavigation value={currentPath} onChange={handleChange}>
  <BottomNavigationAction
    label="Dashboard"
    value="/dashboard"
    icon={<DashboardIcon />}
  />
  <BottomNavigationAction
    label="Orders"
    value="/orders"
    icon={<OrdersIcon />}
  />
  <BottomNavigationAction
    label="Settings"
    value="/settings"
    icon={<SettingsIcon />}
  />
</BottomNavigation>
```

### Drawer for Secondary Navigation

Use a drawer for secondary navigation items:

```tsx
// React: Drawer navigation
<Drawer
  anchor="left"
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
>
  <List>
    <ListItem button onClick={() => navigate('/profile')}>
      <ListItemText primary="Profile" />
    </ListItem>
    <ListItem button onClick={() => navigate('/help')}>
      <ListItemText primary="Help" />
    </ListItem>
  </List>
</Drawer>
```

### Don't Nest Hamburger Menus

Avoid nesting hamburger menus inside drawers or other menus. This creates poor UX:

**❌ Bad:**
- Hamburger menu opens drawer
- Drawer contains another hamburger menu
- Nested navigation is confusing

**✅ Good:**
- Hamburger opens drawer with all navigation
- Use accordions for sub-navigation
- Clear hierarchy without nested menus
