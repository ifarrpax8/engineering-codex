# Best Practices: Multi-Tenancy UX

## Contents

- [Always Show Current Tenant Context](#always-show-current-tenant-context)
- [Make Tenant Switching Fast](#make-tenant-switching-fast)
- [Clear ALL Previous Tenant Data on Switch](#clear-all-previous-tenant-data-on-switch)
- [Show Impersonation Clearly](#show-impersonation-clearly)
- [White-Labeling Defaults](#white-labeling-defaults)
- [Tenant-Aware Search](#tenant-aware-search)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Accessibility](#accessibility)
- [URL Strategy](#url-strategy)

## Always Show Current Tenant Context

**Principle:** Users must never wonder "which organization am I in?" The current tenant should be visible at all times.

### Visual Indicators

**Header placement (recommended):**
- Tenant name and logo in the top-right or top-left of header
- Persistent across all pages (never hidden)
- Clickable to open tenant switcher

```vue
<!-- Vue 3: Tenant indicator in header -->
<template>
  <header class="app-header">
    <div class="header-left">
      <img :src="tenantLogo" :alt="tenantName" class="tenant-logo" />
      <span class="tenant-name">{{ tenantName }}</span>
    </div>
    <nav class="header-nav">
      <!-- Navigation items -->
    </nav>
    <div class="header-right">
      <TenantSwitcher />
      <UserMenu />
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTenantStore } from '@/stores/tenant'

const tenantStore = useTenantStore()
const tenantName = computed(() => tenantStore.currentTenant?.name || 'Platform')
const tenantLogo = computed(() => tenantStore.tenantBranding?.logoUrl || '/default-logo.svg')
</script>
```

**Breadcrumb inclusion:**
```vue
<template>
  <nav class="breadcrumbs">
    <span>{{ tenantName }}</span>
    <span>/</span>
    <span>Dashboard</span>
    <span>/</span>
    <span>Products</span>
  </nav>
</template>
```

**URL structure:**
- Path-based: `/acme-corp/dashboard` (tenant slug always visible)
- Subdomain-based: `acme.platform.com/dashboard` (tenant in domain)

### Why This Matters

- **Prevents errors:** User knows they're acting in the correct tenant context
- **Builds trust:** Clear organizational boundaries
- **Compliance:** Audit requirements often mandate tenant context visibility
- **Support reduction:** Fewer "which org am I in?" support tickets

## Make Tenant Switching Fast

**Principle:** Switching tenants should feel instant—no full page reload, no re-authentication (unless security requires it).

### Instant Switch Pattern

```typescript
// Vue 3: Fast tenant switching
async function switchTenant(tenantId: string) {
  // 1. Show loading state (optimistic UI)
  tenantStore.setLoading(true)
  
  // 2. Update JWT token (if needed) - this can be async but non-blocking
  const tokenUpdate = authApi.updateTenantContext(tenantId)
  
  // 3. Immediately update UI state
  tenantStore.setCurrentTenant(tenantId)
  
  // 4. Clear previous tenant data (non-blocking)
  clearTenantData()
  
  // 5. Refresh data in parallel
  await Promise.all([
    tokenUpdate,
    permissionsApi.refresh(),
    navigationApi.refresh(),
    dashboardApi.refresh()
  ])
  
  tenantStore.setLoading(false)
}
```

### Visual Feedback

```vue
<template>
  <div v-if="isSwitchingTenant" class="tenant-switch-overlay">
    <div class="spinner"></div>
    <p>Switching to {{ targetTenantName }}...</p>
  </div>
</template>
```

### Performance Targets

- **Time-to-switch:** <2 seconds from click to fully loaded
- **Perceived performance:** UI updates immediately, data loads in background
- **No blocking:** User can see loading state, not frozen UI

## Clear ALL Previous Tenant Data on Switch

**Principle:** When switching tenants, ALL data from the previous tenant must be cleared—cache, state, localStorage, everything.

### Comprehensive Clearing

```typescript
// Comprehensive tenant data clearing
async function clearTenantData(previousTenantId: string) {
  // 1. Clear API response cache (React Query / Vue Query)
  queryClient.removeQueries({
    predicate: (query) => {
      // Remove all queries that include tenant data
      const key = query.queryKey
      return Array.isArray(key) && key.includes(previousTenantId)
    }
  })
  
  // 2. Clear component state stores
  productsStore.$reset()
  ordersStore.$reset()
  notificationsStore.$reset()
  userPreferencesStore.$reset()
  
  // 3. Clear browser storage
  // localStorage
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith(`tenant:${previousTenantId}:`)) {
      localStorage.removeItem(key)
    }
  })
  
  // sessionStorage
  Object.keys(sessionStorage).forEach(key => {
    if (key.startsWith(`tenant:${previousTenantId}:`)) {
      sessionStorage.removeItem(key)
    }
  })
  
  // IndexedDB
  await clearTenantIndexedDB(previousTenantId)
  
  // 4. Clear route state
  router.replace({
    name: 'dashboard',
    params: { tenantSlug: newTenantSlug }
  })
  
  // 5. Clear any pending API requests
  cancelPendingRequests()
}
```

### Cache Key Strategy

**Always include tenant ID in cache keys:**

```typescript
// ✅ Good: Tenant ID in cache key
const { data } = useQuery({
  queryKey: ['orders', tenantId.value],
  queryFn: () => ordersApi.getOrders()
})

// ❌ Bad: Missing tenant ID
const { data } = useQuery({
  queryKey: ['orders'], // Will mix data across tenants!
  queryFn: () => ordersApi.getOrders()
})
```

## Show Impersonation Clearly

**Principle:** When a platform admin is impersonating a tenant, it must be impossible to forget—persistent banner, clear exit action.

### Impersonation Banner

```vue
<template>
  <div v-if="isImpersonating" class="impersonation-banner" role="alert">
    <div class="banner-content">
      <Icon name="warning" />
      <span>
        You are viewing as <strong>{{ impersonatedTenant.name }}</strong>
        <span v-if="impersonatedUser">
          ({{ impersonatedUser.name }})
        </span>
      </span>
      <button 
        @click="exitImpersonation"
        class="exit-button"
        aria-label="Exit impersonation"
      >
        Exit Impersonation
      </button>
    </div>
  </div>
</template>

<style scoped>
.impersonation-banner {
  position: sticky;
  top: 0;
  z-index: 9999;
  background: #ff9800;
  color: white;
  padding: 12px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.exit-button {
  background: white;
  color: #ff9800;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>
```

### Always Visible

- **Sticky positioning:** Banner stays at top when scrolling
- **High z-index:** Above all other content
- **Persistent:** Visible on every page, never hidden
- **Accessible:** Announced to screen readers

## White-Labeling Defaults

**Principle:** Provide sensible defaults for unbranded tenants, validate brand assets, handle edge cases gracefully.

### Sensible Defaults

```typescript
// Default branding configuration
const DEFAULT_BRANDING = {
  logoUrl: '/default-logo.svg',
  primaryColor: '#1a73e8', // Accessible blue
  secondaryColor: '#34a853', // Accessible green
  fontFamily: 'system-ui, -apple-system, sans-serif',
  fromName: 'Platform',
  fromEmail: 'noreply@platform.com'
}

// Apply defaults when tenant has no branding
function getTenantBranding(tenant: Tenant): Branding {
  return {
    ...DEFAULT_BRANDING,
    ...tenant.branding, // Override with custom branding if present
  }
}
```

### Validation

```typescript
// Validate brand assets before saving
function validateBranding(branding: BrandingInput): ValidationResult {
  const errors: string[] = []
  
  // Logo validation
  if (branding.logoUrl) {
    // Check file extension
    if (!/\.(png|jpg|jpeg|svg)$/i.test(branding.logoUrl)) {
      errors.push('Logo must be PNG, JPG, or SVG')
    }
    
    // Check dimensions (async, would need image load)
    // Logo should be at least 200x50px for header display
  }
  
  // Color validation
  if (branding.primaryColor) {
    // Check color contrast (accessibility)
    const contrast = getContrastRatio(branding.primaryColor, '#ffffff')
    if (contrast < 4.5) {
      errors.push('Primary color must have sufficient contrast for accessibility')
    }
  }
  
  return { valid: errors.length === 0, errors }
}
```

### Fallback Handling

```vue
<template>
  <img
    :src="logoUrl"
    :alt="tenantName"
    @error="handleLogoError"
    class="tenant-logo"
  />
</template>

<script setup lang="ts">
const logoError = ref(false)

const logoUrl = computed(() => {
  if (logoError.value) {
    return '/default-logo.svg' // Fallback on error
  }
  return tenantBranding.value?.logoUrl || '/default-logo.svg' // Fallback if not configured
})

function handleLogoError() {
  logoError.value = true
  // Optionally log to error tracking service
}
</script>
```

## Tenant-Aware Search

**Principle:** Search results must be scoped to the current tenant unless explicitly platform-level.

### Scoped Search

```typescript
// Search API automatically scopes to current tenant
async function searchProducts(query: string) {
  const tenantId = tenantStore.tenantId
  
  // API includes tenant ID in request (via header interceptor)
  return await apiClient.get('/api/products/search', {
    params: { q: query }
    // X-Tenant-Id header automatically included
  })
}

// Backend filters by tenant
@GetMapping("/api/products/search")
fun searchProducts(@RequestParam q: String): List<Product> {
    val tenantId = TenantContextHolder.getTenantId()
    return productRepository.search(q, tenantId) // Tenant filter applied
}
```

### Platform-Level Search (Admin Only)

```typescript
// Platform admin can search across tenants
async function searchAllTenants(query: string) {
  if (!userStore.isPlatformAdmin) {
    throw new Error('Platform admin access required')
  }
  
  // Explicitly request platform-level search
  return await apiClient.get('/api/admin/products/search', {
    params: { q: query, scope: 'all-tenants' }
    // No X-Tenant-Id header, or special admin header
  })
}
```

## Stack-Specific Guidance

### Vue 3

**Tenant composable:**
```typescript
// composables/useTenant.ts
import { computed } from 'vue'
import { useTenantStore } from '@/stores/tenant'

export function useTenant() {
  const tenantStore = useTenantStore()
  
  return {
    currentTenant: computed(() => tenantStore.currentTenant),
    tenantId: computed(() => tenantStore.tenantId),
    tenantSlug: computed(() => tenantStore.tenantSlug),
    switchTenant: tenantStore.switchTenant,
    isLoading: computed(() => tenantStore.isLoading)
  }
}
```

**Pinia tenant store:**
```typescript
// stores/tenant.ts (see architecture.md for full example)
export const useTenantStore = defineStore('tenant', () => {
  // State, getters, actions
})
```

**Route middleware for tenant validation:**
```typescript
// router/middleware/tenantGuard.ts
export function tenantGuard(to: RouteLocationNormalized) {
  const tenantSlug = to.params.tenantSlug as string
  const tenantStore = useTenantStore()
  
  // Validate user has access to this tenant
  const hasAccess = tenantStore.availableTenants.some(
    t => t.slug === tenantSlug
  )
  
  if (!hasAccess) {
    return { name: 'unauthorized' }
  }
  
  // Ensure current tenant matches route
  if (tenantStore.currentTenant?.slug !== tenantSlug) {
    tenantStore.switchTenantBySlug(tenantSlug)
  }
}
```

**CSS custom properties per tenant:**
```typescript
// Apply tenant theme
function applyTenantTheme(tenant: Tenant) {
  const branding = tenant.branding || defaultBranding
  
  document.documentElement.style.setProperty(
    '--primary-color',
    branding.primaryColor
  )
  document.documentElement.style.setProperty(
    '--secondary-color',
    branding.secondaryColor
  )
}
```

### React

**Tenant context provider:**
```typescript
// contexts/TenantContext.tsx (see architecture.md for full example)
export function TenantProvider({ children }) {
  // Provides tenant state to all components
}

export function useCurrentTenant() {
  // Hook to access tenant context
}
```

**useCurrentTenant hook:**
```typescript
// hooks/useCurrentTenant.ts
export function useCurrentTenant() {
  const context = useContext(TenantContext)
  if (!context) {
    throw new Error('useCurrentTenant must be used within TenantProvider')
  }
  return context
}
```

**Tenant-aware router wrapper:**
```typescript
// components/TenantRoute.tsx
export function TenantRoute({ children, tenantSlug }) {
  const { currentTenant, switchTenant } = useCurrentTenant()
  
  useEffect(() => {
    if (currentTenant?.slug !== tenantSlug) {
      switchTenant(tenantSlug)
    }
  }, [tenantSlug, currentTenant])
  
  return <>{children}</>
}
```

### Spring Boot

**TenantContext ThreadLocal:**
```kotlin
// TenantContextHolder.kt (see architecture.md)
object TenantContextHolder {
    private val tenantId = ThreadLocal<String>()
    
    fun setTenantId(id: String) { tenantId.set(id) }
    fun getTenantId(): String = tenantId.get() ?: throw TenantContextMissingException()
    fun clear() { tenantId.remove() }
}
```

**@TenantScoped annotation pattern:**
```kotlin
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class TenantScoped

// Usage in service
@TenantScoped
@Service
class ProductService {
    fun getProducts(): List<Product> {
        val tenantId = TenantContextHolder.getTenantId()
        // Automatically scoped to tenant
    }
}
```

**Hibernate filter:**
```kotlin
// Entity with tenant filter (see architecture.md)
@Entity
@FilterDef(name = "tenantFilter", parameters = [ParamDef(name = "tenantId", type = String::class)])
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
class Order {
    @Column(name = "tenant_id")
    var tenantId: String = ""
}
```

**Tenant-aware @Cacheable key:**
```kotlin
@Cacheable(value = ["products"], key = "#tenantId + ':' + #productId")
fun getProduct(tenantId: String, productId: String): Product {
    // Cache key includes tenant ID
}
```

## Accessibility

**Tenant switcher keyboard accessible:**
```vue
<template>
  <div class="tenant-switcher" role="combobox" aria-label="Select tenant">
    <button
      @click="toggleDropdown"
      @keydown.enter="toggleDropdown"
      @keydown.space.prevent="toggleDropdown"
      aria-expanded="isOpen"
      aria-haspopup="listbox"
    >
      {{ currentTenant.name }}
      <Icon name="chevron-down" />
    </button>
    <ul v-if="isOpen" role="listbox">
      <li
        v-for="tenant in availableTenants"
        :key="tenant.id"
        role="option"
        @click="selectTenant(tenant)"
        @keydown.enter="selectTenant(tenant)"
      >
        {{ tenant.name }}
      </li>
    </ul>
  </div>
</template>
```

**Impersonation banner announced to screen readers:**
```vue
<template>
  <div
    v-if="isImpersonating"
    class="impersonation-banner"
    role="alert"
    aria-live="assertive"
  >
    <!-- Banner content -->
  </div>
</template>
```

## URL Strategy

**Path-based: `/org-slug/resource`**
- Example: `/acme-corp/dashboard`, `/acme-corp/products/123`
- **Pros:** Simple, works with single domain, easy deep linking
- **Cons:** URL includes tenant slug (may be long)

**Subdomain-based: `org.platform.com/resource`**
- Example: `acme.platform.com/dashboard`, `beta.platform.com/products/123`
- **Pros:** Clean URLs, enables custom domains, clear tenant isolation
- **Cons:** Requires DNS configuration, CORS setup per subdomain

**Recommendation:** Start with path-based, migrate to subdomain for white-labeled tenants.

```typescript
// URL generation helper
function getTenantUrl(path: string): string {
  const tenant = useTenantStore().currentTenant
  
  if (tenant?.customDomain) {
    return `https://${tenant.customDomain}${path}`
  } else if (useSubdomainRouting.value) {
    return `https://${tenant.slug}.platform.com${path}`
  } else {
    return `/${tenant.slug}${path}`
  }
}
```
