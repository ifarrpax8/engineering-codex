# Permissions UX -- Options

## Contents

- [Unauthorized Content Strategy](#unauthorized-content-strategy)
- [Frontend Permission Patterns](#frontend-permission-patterns)
- [Permission Storage](#permission-storage)
- [Authorization Models (UI Perspective)](#authorization-models-ui-perspective)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Unauthorized Content Strategy

How to handle UI elements when user lacks permission.

### Hide Element

**Description**: Completely remove element from DOM (not rendered).

**Strengths**:
- Cleaner UI, reduces noise
- Better for navigation items user will never access
- Prevents confusion about inaccessible features

**Weaknesses**:
- User doesn't know feature exists
- Can't request access to hidden features
- May reduce feature discovery

**Best For**:
- Navigation items for different role tiers
- Features user will never access (different tenant scope)
- Admin-only sections

**Avoid When**:
- User might need to request access
- Feature is part of upgrade path
- User should know feature exists

**Example**:
```vue
<nav-item v-if="hasPermission('admin:settings')">Settings</nav-item>
```

### Disable with Tooltip

**Description**: Show element but disable interaction, explain why with tooltip.

**Strengths**:
- User knows feature exists
- Clear explanation of why disabled
- Can show path to access

**Weaknesses**:
- Can clutter UI if overused
- Requires hover to see explanation
- May frustrate if many disabled elements

**Best For**:
- Actions within accessible features
- Features user can partially access
- When user should know what's possible

**Avoid When**:
- User will never access (use hide instead)
- Too many disabled elements (clutters UI)
- No clear path to access

**Example**:
```vue
<button 
  :disabled="!canDelete"
  :title="!canDelete ? 'Only admins can delete' : ''"
>
  Delete
</button>
```

### Show with "Request Access"

**Description**: Show element with "Request access" button or prompt.

**Strengths**:
- Provides path to access
- Educational (shows what's available)
- Reduces support tickets

**Weaknesses**:
- Requires approval workflow
- May increase admin burden
- User may not get immediate access

**Best For**:
- Features user might need access to
- When approval workflow exists
- Team/collaborative contexts

**Avoid When**:
- No approval workflow implemented
- Access requires payment (use upgrade instead)
- User will never get access

**Example**:
```vue
<div v-if="!hasPermission('project:delete')" class="request-access">
  <p>You need delete permission to remove projects</p>
  <button @click="requestAccess('project:delete')">Request Access</button>
</div>
```

### Show with "Upgrade Plan"

**Description**: Show feature with upgrade/plan change prompt.

**Strengths**:
- Clear monetization path
- Shows value before restriction
- Can increase conversions

**Weaknesses**:
- Only works for paid features
- May frustrate if upgrade is expensive
- Requires payment integration

**Best For**:
- Premium/paid features
- Tiered subscription models
- Features tied to plan level

**Avoid When**:
- Feature is role-based (not plan-based)
- No payment system
- Free tier should have access

**Example**:
```vue
<div v-if="!hasPermission('analytics:advanced')" class="upgrade-prompt">
  <p>Advanced analytics requires a Pro plan</p>
  <button @click="navigateToUpgrade">Upgrade to Pro</button>
</div>
```

## Frontend Permission Patterns

How to implement permission checks in frontend code.

### Directive-Based (Vue v-permission)

**Description**: Custom Vue directive for permission checks.

**Strengths**:
- Declarative, clean template syntax
- Easy to use: `v-permission="'permission:name'"`
- Supports modifiers (hide, disable)

**Weaknesses**:
- Vue-specific (not portable)
- Less flexible than component/hook approach
- Harder to test in isolation

**Best For**:
- Vue 3 applications
- Simple show/hide/disable patterns
- Template-heavy components

**Avoid When**:
- Need complex permission logic
- React applications
- Permission checks in JavaScript logic

**Example**:
```vue
<button v-permission="'project:delete'">Delete</button>
<nav-item v-permission:hide="'admin:settings'">Settings</nav-item>
```

### Component Wrapper (PermissionGate)

**Description**: Wrapper component that conditionally renders children.

**Strengths**:
- Works in Vue and React
- Composable, reusable
- Easy to test

**Weaknesses**:
- More verbose than directive
- Requires wrapping elements
- Can create wrapper divs

**Best For**:
- React applications
- Complex permission logic
- When you need fallback UI

**Avoid When**:
- Simple show/hide (directive is cleaner)
- Many nested permission checks (can get verbose)

**Example**:
```tsx
<PermissionGate permission="project:delete" mode="disable">
  <Button>Delete</Button>
</PermissionGate>
```

### Hook-Based (usePermission)

**Description**: React hook or Vue composable for permission checks.

**Strengths**:
- Flexible, use anywhere
- Easy to test
- Can combine multiple checks

**Weaknesses**:
- More code than directive
- Requires importing hook
- Can be overused (check in every component)

**Best For**:
- Complex permission logic
- Permission checks in JavaScript
- When you need computed permissions

**Avoid When**:
- Simple template checks (directive is cleaner)
- Performance-critical (memoize checks)

**Example**:
```tsx
const DeleteButton = () => {
  const { hasPermission } = usePermission()
  const canDelete = hasPermission('project:delete')
  
  return <Button disabled={!canDelete}>Delete</Button>
}
```

### Route-Level Guards

**Description**: Check permissions at route level, redirect if unauthorized.

**Strengths**:
- Prevents unauthorized page access
- Centralized permission logic
- Better UX (redirect before render)

**Weaknesses**:
- Only works for route-level permissions
- Doesn't help with component-level permissions
- Can cause redirect loops if not careful

**Best For**:
- Page-level access control
- Entire routes that require permission
- Navigation protection

**Avoid When**:
- Component-level permissions needed
- Partial access to page (some features, not all)

**Example**:
```typescript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresPermission && !hasPermission(to.meta.requiresPermission)) {
    next({ name: 'access-denied' })
  } else {
    next()
  }
})
```

## Permission Storage

Where and how to store permissions client-side.

### Pinia/Zustand Store

**Description**: State management store (Pinia for Vue, Zustand for React).

**Strengths**:
- Reactive/observable updates
- Centralized permission state
- Easy to access from any component
- DevTools support

**Weaknesses**:
- Lost on page refresh (unless persisted)
- Requires state management library
- Can be overkill for simple apps

**Best For**:
- Vue 3 (Pinia) or React (Zustand) apps
- Complex apps with state management
- When permissions need to be reactive

**Avoid When**:
- Simple apps without state management
- Need persistence across refreshes (combine with localStorage)

**Example**:
```typescript
// Pinia store
export const usePermissionStore = defineStore('permissions', {
  state: () => ({ permissions: [] }),
  actions: {
    async loadPermissions() {
      this.permissions = await api.get('/auth/permissions')
    }
  }
})
```

### React Context

**Description**: React Context API for permission state.

**Strengths**:
- Built into React (no extra library)
- Works with any React version
- Simple for small apps

**Weaknesses**:
- Can cause unnecessary re-renders
- Less performant than Zustand
- No DevTools support

**Best For**:
- React apps without state management library
- Small to medium apps
- Simple permission needs

**Avoid When**:
- Large apps (use Zustand instead)
- Need advanced features (middleware, DevTools)
- Performance-critical

**Example**:
```tsx
const PermissionContext = createContext<PermissionContextValue>(null)

export const PermissionProvider = ({ children }) => {
  const [permissions, setPermissions] = useState([])
  return (
    <PermissionContext.Provider value={{ permissions }}>
      {children}
    </PermissionContext.Provider>
  )
}
```

### localStorage Cache with TTL

**Description**: Cache permissions in localStorage with time-to-live.

**Strengths**:
- Persists across page refreshes
- Faster initial load (if cache valid)
- Reduces server requests

**Weaknesses**:
- Can go stale (permissions revoked)
- Not reactive (need to check expiry)
- Security risk if token stolen

**Best For**:
- Performance optimization
- Reducing server load
- Offline-first apps

**Avoid When**:
- Permissions change frequently
- High security requirements
- Need real-time updates

**Example**:
```typescript
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

const getCachedPermissions = () => {
  const cached = localStorage.getItem('permissions')
  if (!cached) return null
  
  const data = JSON.parse(cached)
  if (Date.now() - data.timestamp > CACHE_TTL) {
    return null // Expired
  }
  
  return data.permissions
}
```

## Authorization Models (UI Perspective)

How authorization models affect UI implementation.

### RBAC (Role-Based Show/Hide)

**Description**: Show/hide UI elements based on user's role.

**Strengths**:
- Simple to implement
- Easy to understand
- Good for clear role tiers

**Weaknesses**:
- Less granular (role-level, not resource-level)
- Can't handle complex scenarios
- Role explosion problem

**Best For**:
- Clear role tiers (viewer, editor, admin)
- Simple permission needs
- Small to medium apps

**Avoid When**:
- Need resource-level permissions
- Complex permission scenarios
- Many roles with overlapping permissions

**Example**:
```typescript
const rolePermissions = {
  viewer: ['project:view'],
  editor: ['project:view', 'project:edit'],
  admin: ['project:*']
}
```

### ABAC (Attribute-Based Granular)

**Description**: Show/hide based on resource attributes (department, status, etc.).

**Strengths**:
- More granular than RBAC
- Handles complex scenarios
- Flexible permission rules

**Weaknesses**:
- More complex to implement
- Harder to reason about
- Performance considerations

**Best For**:
- Complex permission scenarios
- Attribute-based access (department, location)
- Enterprise applications

**Avoid When**:
- Simple role-based needs
- Small apps
- Performance-critical

**Example**:
```typescript
const canEditProject = (project: Project) => {
  return (
    hasPermission('project:edit') &&
    project.department === currentUser.department &&
    !project.archived
  )
}
```

### FGA (Relationship-Based Per-Resource)

**Description**: Check relationship to specific resource (owner, writer, viewer).

**Strengths**:
- Most granular (per-resource)
- Handles complex relationships
- Good for collaborative apps

**Weaknesses**:
- Most complex to implement
- Requires relationship checks
- Can be slow if not optimized

**Best For**:
- Collaborative applications
- Document/resource sharing
- Fine-grained access control

**Avoid When**:
- Simple permission needs
- Performance-critical
- Small apps

**Example**:
```typescript
const canDeleteDocument = async (docId: string) => {
  const relationship = await fgaClient.check({
    user: `user:${currentUserId}`,
    relation: 'owner',
    object: `document:${docId}`
  })
  return relationship.allowed
}
```

## Recommendation Guidance

### Default Recommendation

**For most B2B SaaS applications**:
- **Unauthorized content**: Hide navigation, disable actions, show upgrade prompts
- **Frontend pattern**: Hook-based (usePermission) for flexibility, directive for Vue templates
- **Storage**: Pinia/Zustand store with localStorage cache (TTL: 5 minutes)
- **Authorization model**: Start with RBAC, evolve to ABAC/FGA as needed

### When to Choose Alternatives

**Choose "Hide" over "Disable"**:
- Navigation items user will never access
- Different role tiers
- Different tenant scopes

**Choose "Disable" over "Hide"**:
- Actions within accessible features
- User should know feature exists
- Partial access to feature

**Choose "Request Access" over "Upgrade"**:
- Team/collaborative contexts
- Approval workflow exists
- Role-based (not plan-based) permissions

**Choose "Upgrade" over "Request Access"**:
- Premium/paid features
- Tiered subscription models
- Monetization opportunity

**Choose ABAC/FGA over RBAC**:
- Need resource-level permissions
- Complex permission scenarios
- Collaborative/sharing features

## Synergies

### Directive + Store
- Directive for template checks, store for state management
- Clean templates, centralized state

### Hook + Context/Store
- Hook for permission logic, Context/Store for state
- Flexible, works anywhere

### Route Guards + Component Checks
- Route guards for page-level, component checks for feature-level
- Defense in depth

### RBAC + ABAC
- RBAC for role-based navigation, ABAC for resource-level actions
- Best of both worlds

## Evolution Triggers

### When to Evolve from RBAC to ABAC

**Triggers**:
- Need department/location-based access
- Resource attributes affect permissions
- Role explosion (too many roles)

**Migration path**:
1. Keep RBAC for navigation
2. Add ABAC for resource-level checks
3. Gradually migrate resource checks to ABAC

### When to Evolve from Hide to Disable

**Triggers**:
- Users requesting access to hidden features
- Need to show upgrade paths
- Feature discovery issues

**Migration path**:
1. Audit hidden features
2. Identify upgrade/request opportunities
3. Change hide to disable + upgrade prompt

### When to Add Request Access Workflow

**Triggers**:
- Many support tickets asking for access
- Need approval process
- Team collaboration features

**Migration path**:
1. Implement backend approval workflow
2. Add "Request access" buttons
3. Add notifications for approvals

### When to Add Permission Caching

**Triggers**:
- Performance issues (slow permission checks)
- Too many permission API calls
- Need offline support

**Migration path**:
1. Add localStorage cache with TTL
2. Implement cache invalidation
3. Add WebSocket/SSE for real-time updates
