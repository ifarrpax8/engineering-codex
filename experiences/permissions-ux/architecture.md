# Permissions UX -- Architecture

## Contents

- [Permission-Aware Component Architecture](#permission-aware-component-architecture)
- [Frontend Permission Loading](#frontend-permission-loading)
- [Permission Caching](#permission-caching)
- [Server-Client Permission Sync](#server-client-permission-sync)
- [Dynamic UI Rendering Based on Permissions](#dynamic-ui-rendering-based-on-permissions)
- [Request Access Architecture](#request-access-architecture)
- [Multi-Tenant Permission Scoping](#multi-tenant-permission-scoping)
- [RBAC in the UI](#rbac-in-the-ui)
- [ABAC/FGA in the UI](#abacfga-in-the-ui)

## Permission-Aware Component Architecture

Components need to check permissions before rendering or enabling actions. Common patterns:

### Directive-Based (Vue 3)

```vue
<!-- Custom v-permission directive -->
<template>
  <button v-permission="'project:delete'">Delete Project</button>
  <nav-item v-permission:hide="'admin:settings'">Settings</nav-item>
</template>

<script setup lang="ts">
// Directive implementation
import { usePermissionStore } from '@/stores/permissions'

const vPermission = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const permissionStore = usePermissionStore()
    const hasPermission = permissionStore.hasPermission(binding.value)
    
    if (!hasPermission) {
      if (binding.modifiers.hide) {
        el.style.display = 'none'
      } else {
        el.setAttribute('disabled', 'true')
        el.setAttribute('aria-disabled', 'true')
        el.setAttribute('title', `Requires permission: ${binding.value}`)
      }
    }
  }
}
</script>
```

### Component Wrapper (React)

```tsx
// PermissionGate component
interface PermissionGateProps {
  permission: string | string[]
  fallback?: React.ReactNode
  mode?: 'hide' | 'disable'
  children: React.ReactNode
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  fallback,
  mode = 'hide',
  children
}) => {
  const { hasPermission } = usePermissions()
  const hasAccess = Array.isArray(permission)
    ? permission.some(p => hasPermission(p))
    : hasPermission(permission)

  if (!hasAccess) {
    if (mode === 'hide') return fallback || null
    if (mode === 'disable') {
      return React.cloneElement(children as React.ReactElement, {
        disabled: true,
        'aria-disabled': true,
        title: `Requires permission: ${permission}`
      })
    }
  }

  return <>{children}</>
}

// Usage
<PermissionGate permission="project:delete" mode="disable">
  <Button>Delete Project</Button>
</PermissionGate>
```

### Hook-Based (React)

```tsx
// usePermission hook
export const usePermission = (permission: string | string[]) => {
  const { permissions } = usePermissions()
  
  const hasPermission = useMemo(() => {
    const perms = Array.isArray(permission) ? permission : [permission]
    return perms.some(p => permissions.includes(p))
  }, [permission, permissions])
  
  return { hasPermission }
}

// Usage
const DeleteButton = () => {
  const { hasPermission } = usePermission('project:delete')
  
  return (
    <Button 
      disabled={!hasPermission}
      title={!hasPermission ? 'Only admins can delete projects' : ''}
    >
      Delete Project
    </Button>
  )
}
```

### Composable (Vue 3)

```typescript
// usePermission composable
export const usePermission = () => {
  const permissionStore = usePermissionStore()
  
  const hasPermission = (permission: string | string[]): boolean => {
    const perms = Array.isArray(permission) ? permission : [permission]
    return perms.some(p => permissionStore.hasPermission(p))
  }
  
  const canAccess = (resource: string, action: string): boolean => {
    return hasPermission(`${resource}:${action}`)
  }
  
  return { hasPermission, canAccess }
}

// Usage
<script setup lang="ts">
const { hasPermission } = usePermission()
const canDelete = computed(() => hasPermission('project:delete'))
</script>

<template>
  <button :disabled="!canDelete" :title="!canDelete ? 'Admin only' : ''">
    Delete
  </button>
</template>
```

## Frontend Permission Loading

Permissions must be loaded early in the application lifecycle:

### On Authentication

```typescript
// Vue 3 + Pinia
// stores/permissions.ts
export const usePermissionStore = defineStore('permissions', {
  state: () => ({
    permissions: [] as string[],
    roles: [] as string[],
    loading: false
  }),
  
  actions: {
    async loadPermissions() {
      this.loading = true
      try {
        const response = await api.get('/auth/permissions')
        this.permissions = response.data.permissions
        this.roles = response.data.roles
      } finally {
        this.loading = false
      }
    },
    
    hasPermission(permission: string): boolean {
      return this.permissions.includes(permission)
    }
  }
})

// main.ts or router guard
router.beforeEach(async (to, from, next) => {
  const permissionStore = usePermissionStore()
  if (!permissionStore.permissions.length) {
    await permissionStore.loadPermissions()
  }
  next()
})
```

```tsx
// React + Context
// contexts/PermissionContext.tsx
interface PermissionContextValue {
  permissions: string[]
  roles: string[]
  hasPermission: (permission: string) => boolean
  loadPermissions: () => Promise<void>
}

export const PermissionContext = createContext<PermissionContextValue | null>(null)

export const PermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([])
  const [roles, setRoles] = useState<string[]>([])
  
  const loadPermissions = async () => {
    const response = await api.get('/auth/permissions')
    setPermissions(response.data.permissions)
    setRoles(response.data.roles)
  }
  
  const hasPermission = (permission: string) => {
    return permissions.includes(permission)
  }
  
  useEffect(() => {
    loadPermissions()
  }, [])
  
  return (
    <PermissionContext.Provider value={{ permissions, roles, hasPermission, loadPermissions }}>
      {children}
    </PermissionContext.Provider>
  )
}
```

### Refresh on Role Change

```typescript
// When user's role changes (admin grants access)
const handleRoleChange = async () => {
  // Refresh permissions from server
  await permissionStore.loadPermissions()
  
  // Update UI immediately
  // Components using permissions will reactively update
}
```

## Permission Caching

Client-side caching improves performance but requires invalidation strategy:

### Cache with TTL

```typescript
// Permission cache with time-to-live
interface PermissionCache {
  permissions: string[]
  roles: string[]
  timestamp: number
  ttl: number // milliseconds
}

const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

export const usePermissionCache = () => {
  const getCachedPermissions = (): PermissionCache | null => {
    const cached = localStorage.getItem('permissions')
    if (!cached) return null
    
    const data: PermissionCache = JSON.parse(cached)
    const age = Date.now() - data.timestamp
    
    if (age > data.ttl) {
      localStorage.removeItem('permissions')
      return null
    }
    
    return data
  }
  
  const setCachedPermissions = (permissions: string[], roles: string[]) => {
    const cache: PermissionCache = {
      permissions,
      roles,
      timestamp: Date.now(),
      ttl: CACHE_TTL
    }
    localStorage.setItem('permissions', JSON.stringify(cache))
  }
  
  return { getCachedPermissions, setCachedPermissions }
}
```

### Event-Based Invalidation

```typescript
// Invalidate cache on specific events
// WebSocket or SSE for real-time updates
const permissionEventSource = new EventSource('/api/permissions/events')

permissionEventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  
  if (data.type === 'PERMISSION_REVOKED' || data.type === 'PERMISSION_GRANTED') {
    // Invalidate cache and reload
    localStorage.removeItem('permissions')
    permissionStore.loadPermissions()
  }
}
```

## Server-Client Permission Sync

**Critical principle**: Frontend permissions are a convenience layer. Server ALWAYS enforces.

### Frontend: Hide/Disable Based on Cached Permissions

```typescript
// Frontend checks cached permissions for UI state
const canDelete = computed(() => {
  return permissionStore.hasPermission('project:delete')
})
```

### Backend: Always Enforce (Spring Security)

```kotlin
// Kotlin + Spring Security
@RestController
@RequestMapping("/api/projects")
class ProjectController {
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasPermission(#id, 'Project', 'DELETE')")
    fun deleteProject(@PathVariable id: Long): ResponseEntity<Void> {
        // This will only execute if user has DELETE permission on this project
        projectService.delete(id)
        return ResponseEntity.noContent().build()
    }
}

// Custom PermissionEvaluator for fine-grained checks
@Component
class CustomPermissionEvaluator : PermissionEvaluator {
    override fun hasPermission(
        authentication: Authentication?,
        targetDomainObject: Any?,
        permission: Any?
    ): Boolean {
        // Check RBAC, ABAC, or FGA based on context
        return when {
            permission == "DELETE" && targetDomainObject is Project -> {
                // Check if user is project owner or admin
                checkProjectPermission(authentication, targetDomainObject, "DELETE")
            }
            else -> false
        }
    }
}
```

```java
// Java + Spring Security
@RestController
@RequestMapping("/api/projects")
public class ProjectController {
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasPermission(#id, 'Project', 'DELETE')")
    public ResponseEntity<Void> deleteProject(@PathVariable Long id) {
        projectService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## Dynamic UI Rendering Based on Permissions

### Conditional Navigation Items

```vue
<!-- Vue: Role-based navigation -->
<template>
  <nav>
    <router-link to="/projects">Projects</router-link>
    <router-link 
      v-if="hasPermission('admin:settings')" 
      to="/settings"
    >
      Settings
    </router-link>
    <router-link 
      v-if="hasPermission('user:manage')" 
      to="/users"
    >
      User Management
    </router-link>
  </nav>
</template>
```

```tsx
// React: Conditional navigation
const Navigation = () => {
  const { hasPermission } = usePermissions()
  
  return (
    <nav>
      <NavLink to="/projects">Projects</NavLink>
      {hasPermission('admin:settings') && (
        <NavLink to="/settings">Settings</NavLink>
      )}
      {hasPermission('user:manage') && (
        <NavLink to="/users">User Management</NavLink>
      )}
    </nav>
  )
}
```

### Conditional Action Buttons

```vue
<!-- Vue: Action buttons with permission checks -->
<template>
  <div class="project-actions">
    <button @click="view">View</button>
    <button 
      v-if="canEdit" 
      @click="edit"
      :disabled="!canEdit"
    >
      Edit
    </button>
    <button 
      v-if="canDelete" 
      @click="delete"
      :disabled="!canDelete"
      title="Only project owners can delete"
    >
      Delete
    </button>
  </div>
</template>

<script setup lang="ts">
const { hasPermission } = usePermission()
const canEdit = computed(() => hasPermission('project:edit'))
const canDelete = computed(() => hasPermission('project:delete'))
</script>
```

### Conditional Form Fields

```tsx
// React: Permission-based form fields
const ProjectForm = () => {
  const { hasPermission } = usePermissions()
  
  return (
    <Form>
      <TextField name="name" label="Project Name" />
      <TextField name="description" label="Description" />
      
      {hasPermission('project:configure:billing') && (
        <TextField name="billingCode" label="Billing Code" />
      )}
      
      {hasPermission('project:configure:advanced') && (
        <AdvancedSettings />
      )}
    </Form>
  )
}
```

## Request Access Architecture

### Request Flow

```typescript
// 1. User requests access
interface AccessRequest {
  permission: string
  resourceId?: string
  reason: string
  requestedBy: string
  requestedAt: Date
}

const requestAccess = async (permission: string, reason: string) => {
  await api.post('/access-requests', {
    permission,
    reason,
    resourceId: currentResourceId
  })
  
  // Show confirmation
  showNotification('Access request submitted')
}

// 2. Backend creates request and notifies approvers
@PostMapping("/access-requests")
@PreAuthorize("isAuthenticated()")
fun createAccessRequest(@RequestBody request: AccessRequestDto): ResponseEntity<AccessRequestDto> {
    val accessRequest = accessRequestService.create(request)
    
    // Notify approvers
    notificationService.notifyApprovers(accessRequest)
    
    return ResponseEntity.ok(accessRequest.toDto())
}

// 3. Admin approves/denies
@PutMapping("/access-requests/{id}/approve")
@PreAuthorize("hasRole('ADMIN')")
fun approveRequest(@PathVariable id: Long): ResponseEntity<Void> {
    accessRequestService.approve(id)
    
    // Grant permission
    permissionService.grantPermission(
        accessRequest.userId,
        accessRequest.permission
    )
    
    // Notify user
    notificationService.notifyUser(accessRequest.userId, "Access granted")
    
    return ResponseEntity.ok().build()
}

// 4. Frontend receives update (WebSocket/SSE)
permissionEventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'PERMISSION_GRANTED') {
    // Refresh permissions
    permissionStore.loadPermissions()
    // Show notification
    showNotification('Access granted! You can now use this feature.')
  }
}
```

## Multi-Tenant Permission Scoping

Users have different permissions in different tenants:

```typescript
// Permission resolution includes tenant context
interface TenantPermission {
  tenantId: string
  permissions: string[]
  roles: string[]
}

// Load permissions for current tenant
const loadTenantPermissions = async (tenantId: string) => {
  const response = await api.get(`/tenants/${tenantId}/permissions`)
  permissionStore.setPermissions(response.data.permissions)
}

// On tenant switch
const switchTenant = async (tenantId: string) => {
  // Clear current permissions
  permissionStore.clearPermissions()
  
  // Load new tenant permissions
  await loadTenantPermissions(tenantId)
  
  // Update UI (navigation, actions, etc. will reactively update)
}
```

```kotlin
// Backend: Tenant-scoped permission check
@GetMapping("/tenants/{tenantId}/permissions")
@PreAuthorize("hasAccessToTenant(#tenantId)")
fun getTenantPermissions(@PathVariable tenantId: String): ResponseEntity<PermissionDto> {
    val permissions = permissionService.getPermissionsForTenant(
        getCurrentUserId(),
        tenantId
    )
    return ResponseEntity.ok(permissions.toDto())
}
```

## RBAC in the UI

Role-Based Access Control: Users have roles, roles have permissions.

```typescript
// Role → Permissions mapping
const rolePermissions: Record<string, string[]> = {
  'viewer': ['project:view', 'report:view'],
  'editor': ['project:view', 'project:edit', 'report:view', 'report:export'],
  'admin': ['project:*', 'user:manage', 'settings:*']
}

// Check if role has permission
const roleHasPermission = (role: string, permission: string): boolean => {
  const permissions = rolePermissions[role] || []
  return permissions.some(p => 
    p === permission || 
    p === `${permission.split(':')[0]}:*` ||
    p === '*'
  )
}
```

### Role-Based Navigation

```vue
<!-- Show navigation based on role -->
<nav-item v-if="hasRole('admin')">Settings</nav-item>
<nav-item v-if="hasRole('editor') || hasRole('admin')">Reports</nav-item>
```

## ABAC/FGA in the UI

Attribute-Based Access Control and Fine-Grained Authorization: Permissions depend on resource attributes or relationships.

### Attribute-Based Checks

```typescript
// Permission depends on resource attributes
const canEditProject = (project: Project): boolean => {
  // User can edit if:
  // 1. They have 'project:edit' permission AND
  // 2. Project is not archived AND
  // 3. User is project owner OR user's department matches project department
  return (
    hasPermission('project:edit') &&
    !project.archived &&
    (project.ownerId === currentUserId || 
     project.department === currentUser.department)
  )
}
```

### Relationship-Based (FGA)

```typescript
// Fine-grained: Check relationship to specific resource
const canDeleteDocument = async (documentId: string): Promise<boolean> => {
  // Check if user has 'writer' or 'owner' relationship to this document
  const relationship = await fgaClient.check({
    user: `user:${currentUserId}`,
    relation: 'writer',
    object: `document:${documentId}`
  })
  
  return relationship.allowed || hasPermission('document:delete:all')
}
```

```vue
<!-- Vue: Resource-specific permission check -->
<template>
  <button 
    v-if="canDeleteDocument(document.id)"
    @click="deleteDocument(document.id)"
  >
    Delete
  </button>
</template>

<script setup lang="ts">
const canDeleteDocument = async (docId: string) => {
  // Check FGA relationship
  const relationship = await checkRelationship('document', docId, 'owner')
  return relationship || hasPermission('document:delete:all')
}
</script>
```
