---
recommendation_type: decision-matrix
---

# Navigation — Options

## Contents

- [Navigation Layout Patterns](#navigation-layout-patterns)
- [Routing Libraries](#routing-libraries)
- [Breadcrumb Strategies](#breadcrumb-strategies)
- [MFE Routing Approaches](#mfe-routing-approaches)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Navigation Layout Patterns

### Sidebar Navigation

**Description:** Persistent left (or right) sidebar navigation that remains visible across pages. Typically used for applications with deep navigation hierarchies.

**Strengths:**
- Always visible, no need to open/close
- Accommodates many navigation items
- Clear hierarchy with nested items
- Familiar pattern for admin/dashboard applications
- Good for desktop applications

**Weaknesses:**
- Consumes horizontal screen space
- Less efficient on mobile (requires drawer pattern)
- Can feel cluttered with too many items
- May compete with main content for attention

**Best For:**
- Admin panels and dashboards
- Applications with 5+ primary sections
- Deep navigation hierarchies (3+ levels)
- Desktop-first applications
- Applications where navigation context is critical

**Avoid When:**
- Mobile-first applications (use bottom nav instead)
- Simple applications with <5 navigation items
- Applications requiring maximum content width
- Public-facing websites (use top nav)

**Code Example:**
```tsx
// React: Sidebar navigation
<AppShell
  sidebar={
    <SideNav>
      <SideNavItem to="/dashboard">Dashboard</SideNavItem>
      <SideNavItem to="/orders">Orders</SideNavItem>
      <SideNavItem to="/settings">
        Settings
        <SideNavSubItem to="/settings/profile">Profile</SideNavSubItem>
        <SideNavSubItem to="/settings/notifications">Notifications</SideNavSubItem>
      </SideNavItem>
    </SideNav>
  }
>
  <Routes>...</Routes>
</AppShell>
```

### Top Bar Navigation

**Description:** Horizontal navigation bar at the top of the page. Typically contains primary navigation items in a horizontal layout.

**Strengths:**
- Maximizes vertical content space
- Familiar pattern for websites
- Works well for flat navigation structures
- Easy to make responsive (hamburger on mobile)
- Good for public-facing applications

**Weaknesses:**
- Limited horizontal space (7±2 items max)
- Difficult to show deep hierarchies
- May require dropdowns for sub-navigation
- Less space-efficient than sidebar

**Best For:**
- Public-facing websites
- Applications with flat navigation (<5 primary items)
- Content-heavy applications needing vertical space
- Marketing sites and landing pages
- Applications where horizontal space is premium

**Avoid When:**
- Deep navigation hierarchies (>2 levels)
- Applications with 10+ navigation items
- Admin panels requiring persistent context
- Mobile-first applications (use bottom nav)

**Code Example:**
```tsx
// React: Top bar navigation
<AppBar>
  <Toolbar>
    <TopNav>
      <TopNavItem to="/dashboard">Dashboard</TopNavItem>
      <TopNavItem to="/orders">Orders</TopNavItem>
      <TopNavItem to="/settings">Settings</TopNavItem>
    </TopNav>
  </Toolbar>
</AppBar>
```

### Combined (Top + Sidebar)

**Description:** Top bar for primary sections, sidebar for sub-navigation within sections. Provides both high-level navigation and contextual sub-navigation.

**Strengths:**
- Best of both worlds: primary nav + contextual sub-nav
- Excellent for complex applications
- Clear separation of primary vs secondary navigation
- Scalable to many navigation items
- Good for applications with distinct sections

**Weaknesses:**
- More complex to implement and maintain
- Consumes both horizontal and vertical space
- Can be overwhelming for simple applications
- Requires careful information architecture

**Best For:**
- Enterprise applications with distinct modules
- Applications with clear section boundaries
- Complex applications requiring both global and contextual nav
- Applications where users work within sections for extended periods
- MFE architectures (shell nav + MFE nav)

**Avoid When:**
- Simple applications (<5 sections)
- Mobile-first applications
- Applications with flat navigation structure
- Small screen applications

**Code Example:**
```tsx
// React: Combined navigation
<AppShell
  header={<TopNav primarySections={sections} />}
  sidebar={<SideNav currentSection={currentSection} />}
>
  <Routes>...</Routes>
</AppShell>
```

### Bottom Navigation (Mobile)

**Description:** Navigation bar fixed at the bottom of mobile screens. Thumb-friendly pattern for primary mobile actions.

**Strengths:**
- Thumb-friendly placement (easy to reach)
- Always visible without scrolling
- Familiar mobile pattern (iOS/Android)
- Good for primary actions (max 5 items)
- Doesn't consume content space

**Weaknesses:**
- Limited to 5 items maximum
- Mobile-only pattern (not suitable for desktop)
- Requires drawer for secondary navigation
- Can be obscured by mobile keyboards
- Less discoverable than top navigation

**Best For:**
- Mobile-first applications
- Applications with 3-5 primary actions
- Consumer mobile applications
- Applications requiring quick access to primary features
- iOS/Android native-like experiences

**Avoid When:**
- Desktop applications
- Applications with >5 primary navigation items
- Applications requiring deep navigation hierarchies
- Applications where navigation is secondary to content

**Code Example:**
```tsx
// React: Bottom navigation (mobile)
<BottomNavigation value={currentPath} onChange={handleNavigation}>
  <BottomNavigationAction
    label="Home"
    value="/"
    icon={<HomeIcon />}
  />
  <BottomNavigationAction
    label="Orders"
    value="/orders"
    icon={<OrdersIcon />}
  />
  <BottomNavigationAction
    label="Profile"
    value="/profile"
    icon={<ProfileIcon />}
  />
</BottomNavigation>
```

## Routing Libraries

### Vue Router

**Description:** Official routing solution for Vue.js applications. Provides declarative routing with guards, lazy loading, and history modes.

**Strengths:**
- Official Vue.js solution (first-party support)
- Excellent TypeScript support
- Powerful route guards (beforeEach, afterEach)
- Lazy loading with code splitting
- Multiple history modes (hash, history, abstract)
- Meta fields for route metadata
- Scroll behavior control
- Active route matching with multiple modes

**Weaknesses:**
- Vue-specific (not framework-agnostic)
- Learning curve for complex guard logic
- Some patterns require composition API for best experience
- Less flexible than some alternatives for edge cases

**Best For:**
- Vue 3 applications
- Applications requiring route guards
- Applications needing lazy loading
- Applications with complex navigation logic
- Applications using Vue ecosystem

**Avoid When:**
- React applications (use React Router)
- Framework-agnostic requirements
- Applications requiring advanced type safety (consider TanStack Router)
- Simple single-page applications without routing needs

**Code Example:**
```typescript
// Vue Router: Route configuration
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue'),
    meta: { requiresAuth: true, title: 'Dashboard' }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('./views/OrderDetail.vue'),
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  }
});

// Route guard
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'login' });
  } else {
    next();
  }
});
```

### React Router

**Description:** De facto standard routing library for React applications. Provides declarative routing with loaders, nested routes, and data loading patterns.

**Strengths:**
- De facto React standard (widely adopted)
- Excellent documentation and community
- Loader pattern for data fetching (v6.4+)
- Nested routing support
- Search params management
- Location state management
- Scroll restoration component
- Active route detection hooks

**Weaknesses:**
- Less type-safe than TanStack Router
- Loader pattern requires React Router v6.4+
- Some patterns require specific React Router versions
- Less flexible for non-standard routing needs

**Best For:**
- React applications
- Applications using React ecosystem
- Applications requiring data loading with routes
- Applications with nested route structures
- Applications needing broad community support

**Avoid When:**
- Vue applications (use Vue Router)
- Applications requiring maximum type safety (consider TanStack Router)
- Applications with unconventional routing needs
- Simple applications where routing overhead isn't needed

**Code Example:**
```tsx
// React Router: Route configuration
<Routes>
  <Route path="/dashboard" element={<Dashboard />} loader={dashboardLoader} />
  <Route path="/orders">
    <Route index element={<OrderList />} loader={orderListLoader} />
    <Route path=":id" element={<OrderDetail />} loader={orderDetailLoader} />
  </Route>
</Routes>

// Loader function
export async function dashboardLoader() {
  const data = await fetchDashboardData();
  return { data };
}

// Component using loader data
function Dashboard() {
  const { data } = useLoaderData();
  return <div>{/* Render dashboard */}</div>;
}
```

### TanStack Router

**Description:** Type-safe, file-based routing solution for React applications. Provides compile-time route validation and type-safe search params.

**Strengths:**
- Excellent TypeScript support (type-safe routes)
- File-based routing (convention over configuration)
- Type-safe search params and route params
- Built-in data loading patterns
- Code splitting by default
- Modern React patterns (hooks, suspense)
- Strong developer experience

**Weaknesses:**
- Newer library (less mature than React Router)
- Smaller community and ecosystem
- File-based routing may not fit all projects
- Learning curve for file-based conventions
- Less documentation and examples

**Best For:**
- TypeScript-first React applications
- Applications requiring maximum type safety
- Applications preferring convention over configuration
- New projects (not migrations)
- Applications with complex route params/search params

**Avoid When:**
- Applications requiring mature ecosystem
- Applications with existing React Router setup
- Applications preferring programmatic route configuration
- Applications needing extensive community examples
- Non-TypeScript projects

**Code Example:**
```typescript
// TanStack Router: File-based routes
// routes/dashboard.tsx
export const Route = createFileRoute('/dashboard')({
  component: Dashboard,
  loader: async () => {
    const data = await fetchDashboardData();
    return { data };
  }
});

// routes/orders/$orderId.tsx
export const Route = createFileRoute('/orders/$orderId')({
  component: OrderDetail,
  loader: async ({ params }) => {
    const order = await fetchOrder(params.orderId);
    return { order };
  }
});
```

## Breadcrumb Strategies

### Route-Meta-Based (Auto)

**Description:** Automatically generate breadcrumbs from route tree metadata. Breadcrumbs are derived from route configuration without manual definition.

**Strengths:**
- Minimal manual configuration
- Consistent with route structure
- Easy to maintain (single source of truth)
- Reduces duplication
- Works well for hierarchical routes

**Weaknesses:**
- Less flexible for complex cases
- May not handle all edge cases
- Requires route structure to match breadcrumb needs
- Can be limiting for non-hierarchical navigation

**Best For:**
- Applications with clear route hierarchy
- Applications where routes map directly to breadcrumbs
- Applications preferring convention over configuration
- Simple to moderate complexity applications
- Applications with consistent route patterns

**Avoid When:**
- Complex breadcrumb requirements
- Non-hierarchical navigation structures
- Applications requiring dynamic breadcrumb generation
- Applications with many edge cases

**Code Example:**
```typescript
// Vue Router: Auto breadcrumbs from route meta
const routes = [
  {
    path: '/settings',
    meta: { breadcrumb: 'Settings' },
    children: [
      {
        path: 'notifications',
        meta: { breadcrumb: 'Notifications' }
      }
    ]
  }
];

// Component automatically generates breadcrumbs
const breadcrumbs = computed(() => {
  return route.matched
    .filter(r => r.meta.breadcrumb)
    .map(r => ({ label: r.meta.breadcrumb, path: r.path }));
});
```

### Manual/Configured

**Description:** Explicitly define breadcrumb chains per page. Each route or page has its breadcrumb configuration defined manually.

**Strengths:**
- Full control over breadcrumb content
- Handles complex cases easily
- Can include dynamic content (e.g., entity names)
- Flexible for non-hierarchical structures
- Works for any navigation pattern

**Weaknesses:**
- More maintenance overhead
- Potential for inconsistency
- Requires updates when routes change
- More code to maintain
- Can become verbose

**Best For:**
- Applications with complex breadcrumb requirements
- Applications requiring dynamic breadcrumb content
- Applications with non-hierarchical navigation
- Applications where routes don't map cleanly to breadcrumbs
- Applications needing fine-grained control

**Avoid When:**
- Simple applications with clear hierarchy
- Applications preferring minimal configuration
- Applications where routes map directly to breadcrumbs
- Applications with many routes (maintenance burden)

**Code Example:**
```typescript
// Manual breadcrumb configuration
const breadcrumbConfig = {
  '/orders/123': [
    { label: 'Orders', path: '/orders' },
    { label: 'Order #123', path: '/orders/123' }
  ],
  '/settings/notifications/email': [
    { label: 'Settings', path: '/settings' },
    { label: 'Notifications', path: '/settings/notifications' },
    { label: 'Email', path: '/settings/notifications/email' }
  ]
};

// Component uses configuration
const breadcrumbs = computed(() => {
  return breadcrumbConfig[route.path] || [];
});
```

### Hybrid

**Description:** Auto-generate breadcrumbs from route metadata with manual overrides for complex cases. Combines convenience of auto-generation with flexibility of manual configuration.

**Strengths:**
- Best of both worlds
- Default behavior with escape hatches
- Reduces configuration for simple cases
- Handles complex cases when needed
- Good balance of maintenance and flexibility

**Weaknesses:**
- More complex implementation
- Requires understanding both approaches
- Can be confusing which approach applies
- May require documentation

**Best For:**
- Applications with mostly hierarchical routes
- Applications with occasional complex breadcrumb needs
- Applications preferring defaults with overrides
- Medium to large applications
- Applications balancing convenience and flexibility

**Avoid When:**
- Simple applications (auto is sufficient)
- Very complex applications (manual may be clearer)
- Applications with inconsistent patterns
- Applications preferring single approach

**Code Example:**
```typescript
// Hybrid: Auto with manual overrides
const breadcrumbOverrides = {
  '/orders/:id': async (route) => {
    const order = await fetchOrder(route.params.id);
    return [
      { label: 'Orders', path: '/orders' },
      { label: order.name, path: route.path }
    ];
  }
};

function getBreadcrumbs(route) {
  // Check for override first
  if (breadcrumbOverrides[route.path]) {
    return breadcrumbOverrides[route.path](route);
  }
  
  // Fall back to auto-generation
  return route.matched
    .filter(r => r.meta.breadcrumb)
    .map(r => ({ label: r.meta.breadcrumb, path: r.path }));
}
```

## MFE Routing Approaches

### Shell-Owned Single Router

**Description:** Shell application owns and controls all routing. MFEs are route targets that the shell navigates to, but the shell maintains routing authority.

**Strengths:**
- Single source of truth for routing
- Consistent navigation behavior
- Easier to implement global route guards
- Centralized route configuration
- Simpler mental model

**Weaknesses:**
- Shell must know all routes upfront
- Less flexible for MFE route changes
- Tight coupling between shell and MFEs
- Shell becomes bottleneck for route changes
- Harder for MFEs to add routes dynamically

**Best For:**
- Applications with stable route structure
- Applications where shell needs routing control
- Applications with global route guards
- Smaller MFE architectures (<5 MFEs)
- Applications preferring centralized control

**Avoid When:**
- Applications requiring dynamic route registration
- Applications where MFEs need routing autonomy
- Large MFE architectures (>5 MFEs)
- Applications with frequently changing routes
- Applications preferring decentralized control

**Code Example:**
```typescript
// Shell: Owns all routes
const routes = [
  { path: '/dashboard', component: DashboardMFE },
  { path: '/orders', component: OrdersMFE },
  { path: '/settings', component: SettingsMFE }
];

// MFE: Just renders content, doesn't control routing
function OrdersMFE() {
  return <OrdersApp />; // No routing logic
}
```

### Federated Routing

**Description:** Each MFE owns its routes and routing logic. Shell stitches routes together, but each MFE manages its own routing internally.

**Strengths:**
- MFEs have routing autonomy
- MFEs can add routes without shell changes
- Better separation of concerns
- Scales well with many MFEs
- MFEs can use their preferred routing library

**Weaknesses:**
- More complex to implement
- Requires coordination between routers
- Potential for route conflicts
- Harder to implement global guards
- More complex debugging

**Best For:**
- Large MFE architectures (>5 MFEs)
- Applications where MFEs need routing autonomy
- Applications with independent MFE teams
- Applications requiring dynamic route registration
- Applications preferring decentralized control

**Avoid When:**
- Small MFE architectures (<3 MFEs)
- Applications requiring tight routing control
- Applications with global route guards
- Applications preferring simplicity
- Applications with stable route structure

**Code Example:**
```typescript
// MFE: Owns its routes
const ordersRoutes = [
  { path: '/orders', component: OrderList },
  { path: '/orders/:id', component: OrderDetail }
];

// Shell: Stitches routes together
const shellRoutes = [
  { path: '/dashboard', component: DashboardMFE },
  ...ordersRoutes.map(r => ({ ...r, path: `/orders${r.path}` }))
];
```

### Route Registry Pattern

**Description:** MFEs register their routes at startup. Shell builds router dynamically based on registered routes. Combines flexibility with coordination.

**Strengths:**
- Dynamic route registration
- MFEs can add routes without shell code changes
- Shell coordinates but doesn't own routes
- Good balance of flexibility and control
- Scales well

**Weaknesses:**
- More complex implementation
- Requires route registration protocol
- Timing issues (routes registered before router ready)
- Potential for route conflicts
- Requires careful coordination

**Best For:**
- Applications requiring dynamic route registration
- Applications with multiple MFE teams
- Applications where routes change frequently
- Medium to large MFE architectures
- Applications balancing flexibility and control

**Avoid When:**
- Simple MFE architectures
- Applications with stable routes
- Applications preferring simplicity
- Small teams (coordination overhead)
- Applications with static route requirements

**Code Example:**
```typescript
// MFE: Registers routes at startup
window.registerMFERoutes('orders', [
  { path: '/orders', component: OrderList },
  { path: '/orders/:id', component: OrderDetail }
]);

// Shell: Builds router from registry
const registeredRoutes = window.getRegisteredRoutes();
const router = createRouter({
  routes: [
    { path: '/dashboard', component: DashboardMFE },
    ...registeredRoutes
  ]
});
```

## Recommendation Guidance

### Default Recommendations

**Navigation Layout:**
- **Default:** Sidebar navigation for admin/dashboard applications
- **Alternative:** Top bar for public-facing websites
- **Mobile:** Bottom navigation for primary actions, drawer for secondary

**Routing Library:**
- **Vue Apps:** Vue Router (official, well-supported)
- **React Apps:** React Router (de facto standard, mature ecosystem)
- **TypeScript-First React:** Consider TanStack Router for type safety

**Breadcrumb Strategy:**
- **Default:** Route-meta-based (auto) for hierarchical routes
- **Complex Cases:** Hybrid approach with manual overrides
- **Very Complex:** Manual configuration for full control

**MFE Routing:**
- **Default:** Route registry pattern (flexibility + coordination)
- **Small MFEs:** Shell-owned single router (simpler)
- **Large MFEs:** Federated routing (autonomy + scale)

### When to Deviate

- **Mobile-First Apps:** Use bottom navigation instead of sidebar
- **Simple Apps:** Top bar sufficient, no need for sidebar
- **Type Safety Critical:** Consider TanStack Router over React Router
- **Static Routes:** Shell-owned router simpler than registry
- **Dynamic Routes:** Registry or federated routing necessary

## Synergies

### Frontend Architecture

Navigation decisions interact with frontend architecture:
- **MFE Architecture:** Requires route registry or federated routing
- **Monolith:** Simpler routing, can use any pattern
- **Component Structure:** Navigation components should be reusable across routes

### Authentication

Navigation integrates with authentication:
- **Route Guards:** Require routing library with guard support (Vue Router, React Router)
- **Permission Checks:** Navigation visibility depends on user permissions
- **Session Management:** Navigation state must handle session expiration

### Permissions UX

Navigation reflects permission structure:
- **Permission-Based Visibility:** Hide/show nav items based on permissions
- **Route Guards:** Enforce permissions at route level
- **Breadcrumb Security:** Don't expose unauthorized routes in breadcrumbs

## Evolution Triggers

Reconsider navigation approach when:

1. **User Feedback:** Users report navigation confusion or difficulty finding features
2. **Scale Changes:** Adding many new routes requires different navigation pattern
3. **Mobile Growth:** Mobile traffic increases require mobile-optimized navigation
4. **MFE Migration:** Moving to MFE architecture requires route coordination
5. **Accessibility Issues:** Navigation fails accessibility audits
6. **Performance Problems:** Navigation causes performance issues (e.g., heavy mega-menus)
7. **Team Structure:** Multiple teams working on navigation requires different coordination
8. **Route Complexity:** Routes become too complex for current breadcrumb strategy
