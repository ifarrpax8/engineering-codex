# Permissions UX -- Gotchas

## Contents

- [Relying on Frontend-Only Permission Checks](#relying-on-frontend-only-permission-checks)
- [Flash of Unauthorized Content](#flash-of-unauthorized-content)
- [Permission Cache Going Stale](#permission-cache-going-stale)
- [Inconsistent Hide/Disable Strategy](#inconsistent-hidedisable-strategy)
- [Disabled Buttons with No Explanation](#disabled-buttons-with-no-explanation)
- [Role Changes Not Reflected Until Logout](#role-changes-not-reflected-until-logout)
- [Request Access with No Workflow](#request-access-with-no-workflow)
- [Multi-Tenant Permission Leakage](#multi-tenant-permission-leakage)
- [Over-Hiding Features](#over-hiding-features)
- [Performance Issues from Permission Checks](#performance-issues-from-permission-checks)

## Relying on Frontend-Only Permission Checks

**Problem**: Trusting frontend permission checks as security boundary.

**Why it's dangerous**: 
- Malicious users can bypass frontend checks
- Browser DevTools can modify JavaScript
- API calls can be made directly, bypassing UI

**Example of the problem**:

```typescript
// ❌ WRONG: Frontend-only check
const handleDelete = async () => {
  if (!hasPermission('project:delete')) {
    return // Only frontend check
  }
  
  await api.delete(`/projects/${id}`)
  // Server doesn't check - SECURITY RISK
}
```

**Solution**: Server ALWAYS enforces.

```kotlin
// ✅ CORRECT: Server enforces
@DeleteMapping("/projects/{id}")
@PreAuthorize("hasPermission(#id, 'Project', 'DELETE')")
fun deleteProject(@PathVariable id: Long) {
    // Server checks permission
    projectService.delete(id)
}
```

## Flash of Unauthorized Content

**Problem**: Permissions load after initial render, user sees content then it disappears.

**Why it happens**:
- Permissions fetched asynchronously after component mounts
- No loading state while permissions load
- Components render before permission checks complete

**Example of the problem**:

```vue
<!-- ❌ WRONG: Permissions load after render -->
<template>
  <div>
    <button v-if="hasPermission('admin:settings')">Settings</button>
  </div>
</template>

<script setup>
// Permission check happens after render
const hasPermission = computed(() => {
  return permissionStore.hasPermission('admin:settings')
})
// permissionStore.permissions is empty initially, so button shows briefly
</script>
```

**Solution**: Load permissions before rendering.

```typescript
// ✅ CORRECT: Load permissions first
const initApp = async () => {
  await permissionStore.loadPermissions() // Load first
  app.mount('#app') // Then render
}
```

## Permission Cache Going Stale

**Problem**: Admin revokes access, but user still sees feature until refresh.

**Why it happens**:
- Permissions cached client-side (localStorage, state)
- No invalidation strategy
- No real-time updates when permissions change

**Example of the problem**:

```typescript
// ❌ WRONG: Cache never invalidates
const loadPermissions = async () => {
  const cached = localStorage.getItem('permissions')
  if (cached) {
    // Use stale cache
    permissionStore.setPermissions(JSON.parse(cached))
    return
  }
  // Only fetch if not cached
  const response = await api.get('/auth/permissions')
  localStorage.setItem('permissions', JSON.stringify(response.data))
}
```

**Solution**: Implement invalidation strategy.

```typescript
// ✅ CORRECT: Cache with TTL and event-based invalidation
const loadPermissions = async () => {
  const cached = getCachedPermissions()
  if (cached && !isExpired(cached)) {
    permissionStore.setPermissions(cached.permissions)
  }
  
  // Always refresh from server periodically
  const response = await api.get('/auth/permissions')
  permissionStore.setPermissions(response.data.permissions)
  setCachedPermissions(response.data.permissions)
}

// WebSocket for real-time updates
permissionEventSource.onmessage = (event) => {
  if (event.data.type === 'PERMISSION_REVOKED') {
    invalidateCache()
    loadPermissions()
  }
}
```

## Inconsistent Hide/Disable Strategy

**Problem**: No clear pattern—some features hidden, others disabled, no explanation.

**Why it's confusing**:
- Users can't predict behavior
- Some features invisible (can't request access)
- Some features visible but disabled (frustrating)

**Example of the problem**:

```vue
<!-- ❌ WRONG: Inconsistent patterns -->
<!-- Navigation: Hidden -->
<nav-item v-if="hasPermission('admin:settings')">Settings</nav-item>

<!-- Action: Disabled -->
<button :disabled="!hasPermission('project:delete')">Delete</button>

<!-- Another action: Hidden -->
<button v-if="hasPermission('user:create')">Create User</button>

<!-- Form field: No check at all -->
<input type="text" name="billingCode" />
```

**Solution**: Establish and document consistent patterns.

```vue
<!-- ✅ CORRECT: Consistent pattern -->
<!-- Navigation: Always hide -->
<nav-item v-if="hasPermission('admin:settings')">Settings</nav-item>

<!-- Actions: Always disable with explanation -->
<button 
  :disabled="!hasPermission('project:delete')"
  :title="!hasPermission('project:delete') ? 'Admin only' : ''"
>
  Delete
</button>
```

## Disabled Buttons with No Explanation

**Problem**: User clicks disabled button repeatedly, nothing happens, no feedback.

**Why it's frustrating**:
- No visual feedback (button looks clickable but disabled)
- No explanation why disabled
- User doesn't know how to get access

**Example of the problem**:

```vue
<!-- ❌ WRONG: No explanation -->
<button :disabled="!canDelete">Delete</button>
<!-- User clicks, nothing happens, no feedback -->
```

**Solution**: Always provide explanation and path forward.

```vue
<!-- ✅ CORRECT: Explanation and path -->
<button 
  :disabled="!canDelete"
  :title="!canDelete ? 'Only project owners can delete. Request access?' : ''"
  @click="!canDelete ? requestAccess('project:delete') : deleteProject()"
>
  {{ canDelete ? 'Delete' : 'Request Delete Permission' }}
</button>
```

## Role Changes Not Reflected Until Logout

**Problem**: Admin grants role, but user doesn't see new features until logout/login.

**Why it happens**:
- Permissions loaded only on login
- No refresh mechanism when permissions change
- No real-time updates

**Example of the problem**:

```typescript
// ❌ WRONG: Permissions only load on login
const login = async () => {
  const token = await authenticate()
  const permissions = await api.get('/auth/permissions') // Only here
  permissionStore.setPermissions(permissions)
  // No refresh mechanism
}
```

**Solution**: Implement permission refresh mechanism.

```typescript
// ✅ CORRECT: Refresh on role change
const handleRoleChange = async () => {
  // Refresh permissions
  await permissionStore.loadPermissions()
  
  // Or use WebSocket/SSE for real-time updates
}

// WebSocket listener
permissionEventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'ROLE_GRANTED' || data.type === 'PERMISSION_GRANTED') {
    permissionStore.loadPermissions()
    showNotification('Your permissions have been updated')
  }
}
```

## Request Access with No Workflow

**Problem**: "Request access" button exists but nobody receives the request.

**Why it happens**:
- Button added for UX but no backend implementation
- Request sent to non-existent endpoint
- No approval workflow configured

**Example of the problem**:

```vue
<!-- ❌ WRONG: Button does nothing -->
<button @click="requestAccess">Request Access</button>

<script>
const requestAccess = () => {
  // No implementation - button does nothing
  console.log('Request access clicked')
}
</script>
```

**Solution**: Implement complete workflow.

```typescript
// ✅ CORRECT: Full workflow
const requestAccess = async (permission: string) => {
  try {
    await api.post('/access-requests', {
      permission,
      reason: prompt('Why do you need this access?')
    })
    showNotification('Request submitted. You will be notified when approved.')
  } catch (error) {
    showError('Failed to submit request')
  }
}

// Backend: Process requests
@PostMapping("/access-requests")
fun createRequest(@RequestBody request: AccessRequestDto) {
    val accessRequest = accessRequestService.create(request)
    notificationService.notifyApprovers(accessRequest)
    return accessRequest
}
```

## Multi-Tenant Permission Leakage

**Problem**: Permissions from Tenant A leaking into Tenant B view.

**Why it happens**:
- Permissions not scoped to tenant
- Cache not cleared on tenant switch
- Permission check doesn't include tenant context

**Example of the problem**:

```typescript
// ❌ WRONG: Permissions not tenant-scoped
const loadPermissions = async () => {
  const permissions = await api.get('/auth/permissions')
  // No tenant context - same permissions for all tenants
  permissionStore.setPermissions(permissions)
}

const switchTenant = (tenantId: string) => {
  // Permissions not refreshed
  currentTenant.value = tenantId
  // Still using Tenant A permissions
}
```

**Solution**: Scope permissions to tenant.

```typescript
// ✅ CORRECT: Tenant-scoped permissions
const loadTenantPermissions = async (tenantId: string) => {
  const permissions = await api.get(`/tenants/${tenantId}/permissions`)
  permissionStore.setPermissions(permissions, tenantId)
}

const switchTenant = async (tenantId: string) => {
  permissionStore.clearPermissions() // Clear old tenant
  await loadTenantPermissions(tenantId) // Load new tenant
}
```

## Over-Hiding Features

**Problem**: User doesn't know a feature exists, can't request access to something they don't know about.

**Why it's problematic**:
- Reduces feature discovery
- Users can't request access to hidden features
- May reduce upgrade conversions

**Example of the problem**:

```vue
<!-- ❌ WRONG: Everything hidden -->
<div v-if="hasPermission('premium:feature')">
  <h2>Advanced Analytics</h2>
  <p>Premium feature content</p>
</div>
<!-- User never sees this, doesn't know it exists -->
```

**Solution**: Show feature with upgrade/request prompt.

```vue
<!-- ✅ CORRECT: Show with upgrade prompt -->
<div>
  <h2>Advanced Analytics</h2>
  <div v-if="hasPermission('premium:feature')">
    <p>Premium feature content</p>
  </div>
  <div v-else class="upgrade-prompt">
    <p>Upgrade to Pro to access Advanced Analytics</p>
    <button @click="upgrade">Upgrade Now</button>
  </div>
</div>
```

## Performance Issues from Permission Checks

**Problem**: Permission checks on every render causing performance degradation.

**Why it happens**:
- Permission check in computed/render function
- No memoization
- Checking permissions for every component instance

**Example of the problem**:

```vue
<!-- ❌ WRONG: Check on every render -->
<template>
  <div v-for="item in items" :key="item.id">
    <button v-if="hasPermission(`item:${item.id}:delete`)">Delete</button>
  </div>
</template>

<script>
// hasPermission called for every item on every render
const hasPermission = (permission) => {
  return permissionStore.permissions.includes(permission) // Expensive check
}
</script>
```

**Solution**: Memoize permission checks, batch checks.

```typescript
// ✅ CORRECT: Memoized permission checks
const permissionCache = new Map<string, boolean>()

const hasPermission = (permission: string): boolean => {
  if (permissionCache.has(permission)) {
    return permissionCache.get(permission)!
  }
  
  const hasAccess = permissionStore.permissions.includes(permission)
  permissionCache.set(permission, hasAccess)
  return hasAccess
}

// Or use computed properties
const canDeleteItem = computed(() => {
  return permissionStore.hasPermission('item:delete')
})
```
