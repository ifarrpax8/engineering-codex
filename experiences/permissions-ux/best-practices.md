# Permissions UX -- Best Practices

## Contents

- [Server ALWAYS Enforces](#server-always-enforces)
- [Hide vs Disable Guidelines](#hide-vs-disable-guidelines)
- [Always Explain Why](#always-explain-why)
- [Provide a Path to Access](#provide-a-path-to-access)
- [Avoid Flash of Unauthorized Content](#avoid-flash-of-unauthorized-content)
- [Stack-Specific Patterns](#stack-specific-patterns)
- [Accessibility Considerations](#accessibility-considerations)
- [Consistent Permission Patterns](#consistent-permission-patterns)

## Server ALWAYS Enforces

**Golden rule**: Frontend permission checks are a convenience layer for UX. The server is the security boundary.

### Why This Matters

- **Security**: Malicious users can bypass frontend checks
- **Reliability**: Frontend code can have bugs
- **Defense in depth**: Multiple layers of security

### Implementation

```kotlin
// ✅ CORRECT: Server enforces
@DeleteMapping("/projects/{id}")
@PreAuthorize("hasPermission(#id, 'Project', 'DELETE')")
fun deleteProject(@PathVariable id: Long) {
    // Server checks permission before executing
    projectService.delete(id)
}

// ❌ WRONG: Trusting frontend
@DeleteMapping("/projects/{id}")
fun deleteProject(@PathVariable id: Long) {
    // No server-side check - SECURITY RISK
    projectService.delete(id)
}
```

```typescript
// Frontend: Convenience check for UX
const handleDelete = async () => {
  if (!hasPermission('project:delete')) {
    // Show error early (better UX)
    showError('You do not have permission to delete')
    return
  }
  
  // Server will also check (security)
  await api.delete(`/projects/${id}`)
}
```

## Hide vs Disable Guidelines

### Hide Navigation Items

**When**: Features the user will never access (different role tier, different tenant)

**Why**: Reduces UI noise, prevents confusion

```vue
<!-- ✅ CORRECT: Hide navigation for inaccessible features -->
<nav-item v-if="hasPermission('admin:settings')">Settings</nav-item>

<!-- ❌ WRONG: Show but disabled -->
<nav-item disabled>Settings</nav-item>
```

### Disable Actions Within Accessible Features

**When**: User can access the feature but not all actions

**Why**: User knows feature exists, disabling shows what's possible

```vue
<!-- ✅ CORRECT: Disable action within accessible feature -->
<template>
  <div class="project-details">
    <h1>{{ project.name }}</h1>
    <button @click="edit">Edit</button>
    <button 
      :disabled="!canDelete"
      @click="delete"
      :title="!canDelete ? 'Only admins can delete' : ''"
    >
      Delete
    </button>
  </div>
</template>

<!-- ❌ WRONG: Hide delete button entirely -->
<button v-if="canDelete" @click="delete">Delete</button>
```

### Decision Tree

```
Is this a navigation item?
├─ Yes → User will never access?
│   ├─ Yes → HIDE
│   └─ No → Show (user can access)
└─ No → Is this an action within accessible feature?
    ├─ Yes → User can perform action?
    │   ├─ Yes → ENABLE
    │   └─ No → DISABLE with explanation
    └─ No → Show with "Request access" or "Upgrade"
```

## Always Explain Why

**Principle**: Users should understand why something is disabled or hidden.

### Tooltips for Disabled Elements

```vue
<!-- ✅ CORRECT: Explain why disabled -->
<button 
  :disabled="!canDelete"
  :title="!canDelete ? 'Only project owners can delete projects' : ''"
>
  Delete Project
</button>
```

```tsx
// React: Tooltip with explanation
<Button
  disabled={!canDelete}
  title={!canDelete ? 'Only project owners can delete projects' : ''}
  aria-label={!canDelete ? 'Delete project (requires owner permission)' : 'Delete project'}
>
  Delete Project
</Button>
```

### Error Messages

```typescript
// ✅ CORRECT: Clear error message
try {
  await api.delete(`/projects/${id}`)
} catch (error) {
  if (error.status === 403) {
    showError('You do not have permission to delete this project. Only project owners can delete projects.')
  }
}
```

### "Request Access" Explanations

```vue
<!-- ✅ CORRECT: Explain what access is needed -->
<div v-if="!hasPermission('analytics:advanced')" class="upgrade-prompt">
  <p>Advanced analytics requires a Pro plan or Admin role.</p>
  <button @click="requestAccess">Request Access</button>
</div>
```

## Provide a Path to Access

**Principle**: Don't just say "no"—show how to get access.

### Request Access Button

```vue
<!-- ✅ CORRECT: Provide request path -->
<button 
  :disabled="!canDelete"
  @click="!canDelete ? requestAccess('project:delete') : deleteProject()"
>
  {{ canDelete ? 'Delete' : 'Request Delete Permission' }}
</button>
```

### Upgrade Paths

```vue
<!-- ✅ CORRECT: Show upgrade option -->
<div v-if="!hasPermission('feature:premium')" class="upgrade-banner">
  <p>Upgrade to Pro to access this feature</p>
  <button @click="navigateToUpgrade">Upgrade Now</button>
</div>
```

### Contact Admin

```vue
<!-- ✅ CORRECT: Provide admin contact -->
<div v-if="!hasPermission('admin:settings')" class="access-denied">
  <p>This feature requires admin access.</p>
  <a :href="`mailto:${adminEmail}?subject=Access Request`">
    Contact your administrator
  </a>
</div>
```

## Avoid Flash of Unauthorized Content

**Problem**: Permissions load after initial render, user sees content then it disappears.

### Solution: Load Permissions Before Rendering

```typescript
// ✅ CORRECT: Load permissions before app renders
// main.ts (Vue) or App.tsx (React)
const initApp = async () => {
  // Load permissions first
  await permissionStore.loadPermissions()
  
  // Then render app
  app.mount('#app')
}
```

### Loading State

```vue
<!-- ✅ CORRECT: Show loading while permissions load -->
<template>
  <div v-if="permissionStore.loading" class="loading">
    Loading...
  </div>
  <div v-else>
    <!-- App content with permission checks -->
  </div>
</template>
```

### Route Guards

```typescript
// ✅ CORRECT: Check permissions in route guard
router.beforeEach(async (to, from, next) => {
  // Ensure permissions are loaded
  if (!permissionStore.permissions.length) {
    await permissionStore.loadPermissions()
  }
  
  // Check route permission
  if (to.meta.requiresPermission && !permissionStore.hasPermission(to.meta.requiresPermission)) {
    next({ name: 'access-denied' })
    return
  }
  
  next()
})
```

## Stack-Specific Patterns

### Vue 3

#### v-permission Directive

```vue
<!-- Custom directive -->
<button v-permission="'project:delete'">Delete</button>
<nav-item v-permission:hide="'admin:settings'">Settings</nav-item>
```

#### usePermission Composable

```typescript
// composables/usePermission.ts
export const usePermission = () => {
  const permissionStore = usePermissionStore()
  
  const hasPermission = (permission: string) => {
    return permissionStore.hasPermission(permission)
  }
  
  return { hasPermission }
}
```

#### Pinia Permission Store

```typescript
// stores/permissions.ts
export const usePermissionStore = defineStore('permissions', {
  state: () => ({
    permissions: [] as string[],
    roles: [] as string[]
  }),
  
  actions: {
    async loadPermissions() {
      const response = await api.get('/auth/permissions')
      this.permissions = response.data.permissions
    },
    
    hasPermission(permission: string): boolean {
      return this.permissions.includes(permission)
    }
  }
})
```

#### Route Guard Meta

```typescript
// router/index.ts
{
  path: '/settings',
  component: Settings,
  meta: {
    requiresPermission: 'admin:settings'
  }
}
```

### React

#### PermissionGate Component

```tsx
// components/PermissionGate.tsx
export const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  mode = 'hide',
  children
}) => {
  const { hasPermission } = usePermissions()
  const hasAccess = hasPermission(permission)
  
  if (!hasAccess && mode === 'hide') return null
  if (!hasAccess && mode === 'disable') {
    return React.cloneElement(children as React.ReactElement, { disabled: true })
  }
  
  return <>{children}</>
}
```

#### usePermission Hook

```tsx
// hooks/usePermission.ts
export const usePermission = (permission: string) => {
  const { permissions } = usePermissions()
  return useMemo(() => permissions.includes(permission), [permission, permissions])
}
```

#### Context-Based Permission Provider

```tsx
// contexts/PermissionContext.tsx
export const PermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([])
  
  useEffect(() => {
    loadPermissions().then(setPermissions)
  }, [])
  
  return (
    <PermissionContext.Provider value={{ permissions, hasPermission }}>
      {children}
    </PermissionContext.Provider>
  )
}
```

### Spring Security (Backend)

#### @PreAuthorize

```kotlin
@DeleteMapping("/projects/{id}")
@PreAuthorize("hasPermission(#id, 'Project', 'DELETE')")
fun deleteProject(@PathVariable id: Long) {
    projectService.delete(id)
}
```

#### Method Security

```kotlin
@Configuration
@EnableMethodSecurity
class SecurityConfig {
    // Method security enabled
}

@Service
class ProjectService {
    @PreAuthorize("hasRole('ADMIN')")
    fun deleteProject(id: Long) {
        // Only admins can call this method
    }
}
```

#### Custom PermissionEvaluator

```kotlin
@Component
class CustomPermissionEvaluator : PermissionEvaluator {
    override fun hasPermission(
        authentication: Authentication?,
        targetDomainObject: Any?,
        permission: Any?
    ): Boolean {
        // Custom permission logic (RBAC, ABAC, FGA)
        return checkPermission(authentication, targetDomainObject, permission)
    }
}
```

## Accessibility Considerations

### Disabled Elements

**Requirements**:
- `aria-disabled="true"` attribute
- Explanation in `title` or `aria-label`
- Keyboard navigation should skip disabled elements (or announce them)

```vue
<!-- ✅ CORRECT: Accessible disabled button -->
<button 
  :disabled="!canDelete"
  aria-disabled="true"
  :aria-label="!canDelete ? 'Delete project (requires owner permission)' : 'Delete project'"
  :title="!canDelete ? 'Only project owners can delete projects' : ''"
>
  Delete Project
</button>
```

### Hidden Elements

**Requirements**:
- Should not be in tab order
- Should not be announced by screen readers
- Use `display: none` or `visibility: hidden` (not just opacity)

```vue
<!-- ✅ CORRECT: Properly hidden -->
<nav-item 
  v-if="hasPermission('admin:settings')"
  style="display: none"
  aria-hidden="true"
>
  Settings
</nav-item>
```

### Permission Changes Announcements

**Requirement**: When permissions change (role granted, access approved), announce to screen readers.

```typescript
// ✅ CORRECT: Announce permission changes
const handlePermissionGranted = () => {
  // Update UI
  permissionStore.loadPermissions()
  
  // Announce to screen readers
  announceToScreenReader('Access granted. You can now delete projects.')
}
```

## Consistent Permission Patterns

**Principle**: Same permission level should behave consistently across the entire app.

### Establish Patterns

**Document your patterns**:
- Navigation items: Always hide if user can't access
- Action buttons: Always disable (don't hide) if within accessible feature
- Form fields: Hide if user can't access feature, disable if within accessible feature
- Error messages: Always explain why and provide path forward

### Code Review Checklist

- [ ] Permission check matches pattern (hide vs disable)
- [ ] Explanation provided for disabled state
- [ ] Path to access provided (request, upgrade, contact)
- [ ] Server enforces permission (not just frontend)
- [ ] Accessibility attributes present
- [ ] Consistent with other similar features

### Examples of Inconsistency to Avoid

```vue
<!-- ❌ WRONG: Inconsistent patterns -->
<!-- Feature A: Hides delete button -->
<button v-if="canDelete">Delete</button>

<!-- Feature B: Disables delete button -->
<button :disabled="!canDelete">Delete</button>

<!-- Feature C: Shows delete but errors on click -->
<button @click="delete">Delete</button> <!-- No check at all -->
```

```vue
<!-- ✅ CORRECT: Consistent pattern -->
<!-- All features: Disable with explanation -->
<button 
  :disabled="!canDelete"
  :title="!canDelete ? 'Only admins can delete' : ''"
>
  Delete
</button>
```
