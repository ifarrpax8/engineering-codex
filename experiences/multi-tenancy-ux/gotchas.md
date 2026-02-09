# Gotchas: Multi-Tenancy UX

## Contents

- [Cross-Tenant Data Leakage](#cross-tenant-data-leakage)
- [Tenant Switch Not Clearing Browser State](#tenant-switch-not-clearing-browser-state)
- [Impersonation Without Clear Indicator](#impersonation-without-clear-indicator)
- [White-Label CSS Bleeding Across Tenants](#white-label-css-bleeding-across-tenants)
- [JWT Claims Not Including Tenant](#jwt-claims-not-including-tenant)
- [Tenant-Specific Permissions Cached Across Switch](#tenant-specific-permissions-cached-across-switch)
- [Deep Links Without Tenant Context](#deep-links-without-tenant-context)
- [Subdomain-Based Tenancy and CORS Issues](#subdomain-based-tenancy-and-cors-issues)
- [Report/Export Including Cross-Tenant Data](#reportexport-including-cross-tenant-data)
- [White-Label Email Templates Not Using Tenant Branding](#white-label-email-templates-not-using-tenant-branding)

## Cross-Tenant Data Leakage

**The worst possible bug:** Data from Tenant A appears in Tenant B's UI. This is a critical security incident.

### Symptoms

- User switches from Tenant A to Tenant B, but still sees Tenant A's data
- API responses include data from multiple tenants
- Cache returns data from wrong tenant
- Reports/exports include cross-tenant data

### Root Causes

**1. Cache not cleared on tenant switch:**
```typescript
// ❌ BAD: Cache key doesn't include tenant ID
const { data } = useQuery({
  queryKey: ['orders'], // Missing tenant ID!
  queryFn: () => ordersApi.getOrders()
})

// ✅ GOOD: Tenant ID in cache key
const { data } = useQuery({
  queryKey: ['orders', tenantId.value],
  queryFn: () => ordersApi.getOrders()
})
```

**2. API not filtering by tenant:**
```kotlin
// ❌ BAD: Query doesn't filter by tenant
@Query("SELECT o FROM Order o")
fun findAll(): List<Order> // Returns ALL orders!

// ✅ GOOD: Tenant filter applied
@Query("SELECT o FROM Order o WHERE o.tenantId = :tenantId")
fun findByTenantId(tenantId: String): List<Order>
```

**3. Frontend storing data without tenant scope:**
```typescript
// ❌ BAD: localStorage key doesn't include tenant
localStorage.setItem('orders', JSON.stringify(orders))

// ✅ GOOD: Tenant ID in storage key
localStorage.setItem(`tenant:${tenantId}:orders`, JSON.stringify(orders))
```

### Prevention

- Always include tenant ID in cache keys
- Server-side filtering is mandatory (never trust frontend)
- Clear all tenant-specific data on switch
- Comprehensive tenant isolation tests

## Tenant Switch Not Clearing Browser State

**Problem:** User switches tenants, but browser storage (localStorage, sessionStorage, IndexedDB) still contains previous tenant's data.

### Symptoms

- After switching tenants, old data appears briefly
- Form autocomplete suggests previous tenant's data
- Cached API responses from previous tenant shown

### Root Cause

```typescript
// ❌ BAD: Not clearing browser storage on switch
async function switchTenant(tenantId: string) {
  await tenantStore.switchTenant(tenantId)
  // Missing: Clear localStorage, sessionStorage, IndexedDB
}

// ✅ GOOD: Comprehensive clearing
async function switchTenant(tenantId: string) {
  const previousTenantId = tenantStore.tenantId
  
  await tenantStore.switchTenant(tenantId)
  
  // Clear all browser storage
  clearTenantLocalStorage(previousTenantId)
  clearTenantSessionStorage(previousTenantId)
  await clearTenantIndexedDB(previousTenantId)
}
```

### Prevention

- Create a `clearTenantData()` function that clears everything
- Call it on every tenant switch
- Use tenant-prefixed keys in storage: `tenant:${tenantId}:key`

## Impersonation Without Clear Indicator

**Problem:** Platform admin starts impersonating a tenant but forgets they're impersonating, takes destructive action in wrong tenant context.

### Symptoms

- Admin performs actions thinking they're in their own context
- No clear visual indication of impersonation state
- Impersonation banner hidden or easy to miss

### Root Cause

```vue
<!-- ❌ BAD: Impersonation indicator hidden or subtle -->
<div v-if="isImpersonating" class="subtle-indicator">
  Impersonating
</div>

<!-- ✅ GOOD: Persistent, obvious banner -->
<div v-if="isImpersonating" class="impersonation-banner" role="alert">
  <strong>Viewing as {{ tenant.name }}</strong>
  <button @click="exitImpersonation">Exit</button>
</div>
```

### Prevention

- **Sticky banner:** Always visible at top of page
- **High contrast:** Orange/red background, impossible to miss
- **Persistent:** Never hidden, even when scrolling
- **Exit action:** Prominent button to exit impersonation
- **Audit logging:** Log all actions during impersonation

## White-Label CSS Bleeding Across Tenants

**Problem:** One tenant's custom CSS (colors, fonts) briefly appears for another tenant during switch or page load.

### Symptoms

- Tenant A's red primary color flashes for Tenant B
- Custom fonts from Tenant A appear for Tenant B
- Theme not fully applied on initial load

### Root Cause

```typescript
// ❌ BAD: CSS variables set asynchronously, race condition
async function switchTenant(tenantId: string) {
  await tenantStore.switchTenant(tenantId)
  // CSS variables set later, old values still active
  applyTenantTheme(tenantStore.currentTenant)
}

// ✅ GOOD: Set CSS variables synchronously before render
async function switchTenant(tenantId: string) {
  const newTenant = await tenantApi.getTenant(tenantId)
  
  // Set CSS variables IMMEDIATELY
  applyTenantTheme(newTenant)
  
  // Then update store
  tenantStore.setCurrentTenant(newTenant)
}
```

### Prevention

- Set CSS custom properties synchronously before UI updates
- Use CSS scoping or namespacing for tenant-specific styles
- Load tenant theme before rendering components
- Test theme switching with visual regression tests

## JWT Claims Not Including Tenant

**Problem:** JWT token doesn't include current tenant ID, forcing frontend to send tenant in header—security hole if frontend is compromised.

### Symptoms

- Frontend must manually include `X-Tenant-Id` header
- Backend can't validate tenant context from token
- User could potentially manipulate tenant header

### Root Cause

```kotlin
// ❌ BAD: JWT doesn't include tenant
data class JwtClaims(
    val sub: String,
    val email: String
    // Missing: tenantId
)

// ✅ GOOD: Tenant ID in JWT claims
data class JwtClaims(
    val sub: String,
    val email: String,
    val tenantId: String, // Current active tenant
    val tenantRoles: Map<String, List<String>> // Roles per tenant
)
```

### Prevention

- Always include `tenantId` in JWT claims
- Backend validates tenant from JWT first, header as fallback
- On tenant switch, issue new JWT with updated tenant claim

## Tenant-Specific Permissions Cached Across Switch

**Problem:** User has admin permissions in Tenant A, switches to Tenant B (viewer role), but admin permissions from Tenant A are still active.

### Symptoms

- User sees admin actions in tenant where they're only a viewer
- Permissions don't update on tenant switch
- UI shows wrong role/permissions

### Root Cause

```typescript
// ❌ BAD: Permissions not refreshed on tenant switch
async function switchTenant(tenantId: string) {
  await tenantStore.switchTenant(tenantId)
  // Missing: Refresh permissions
}

// ✅ GOOD: Always refresh permissions on switch
async function switchTenant(tenantId: string) {
  await tenantStore.switchTenant(tenantId)
  await permissionsStore.refresh() // Reload permissions for new tenant
  await navigationStore.refresh() // Update navigation based on permissions
}
```

### Prevention

- Always refresh permissions on tenant switch
- Clear permission cache when switching tenants
- Show loading state while permissions refresh
- Validate permissions match current tenant

## Deep Links Without Tenant Context

**Problem:** User shares a URL like `/products/123`, recipient opens it in their default tenant—wrong data shown or access denied.

### Symptoms

- Shared URLs don't work for recipients
- Users see "Access Denied" when opening shared links
- Deep links lose tenant context

### Root Cause

```typescript
// ❌ BAD: URL doesn't include tenant context
const shareUrl = `/products/123` // Missing tenant slug!

// ✅ GOOD: Tenant context in URL
const shareUrl = `/${tenantSlug}/products/123`
// Or subdomain: `https://acme.platform.com/products/123`
```

### Prevention

- Always include tenant context in URLs (path or subdomain)
- Route guards validate tenant access
- Handle missing tenant context gracefully (redirect to user's default tenant)

## Subdomain-Based Tenancy and CORS Issues

**Problem:** Each tenant subdomain (`acme.platform.com`, `beta.platform.com`) requires separate CORS configuration.

### Symptoms

- API requests fail with CORS errors
- Cookies not shared across subdomains
- Authentication tokens not working across subdomains

### Root Cause

```kotlin
// ❌ BAD: CORS only configured for main domain
@CrossOrigin(origins = ["https://platform.com"])
@RestController
class ApiController {
    // Fails for acme.platform.com, beta.platform.com
}

// ✅ GOOD: CORS configured for all subdomains
@CrossOrigin(origins = ["https://*.platform.com", "https://platform.com"])
@RestController
class ApiController {
    // Works for all tenant subdomains
}
```

### Prevention

- Configure CORS for wildcard subdomains: `*.platform.com`
- Use same-site cookies with domain: `.platform.com`
- Test CORS with multiple tenant subdomains

## Report/Export Including Cross-Tenant Data

**Problem:** Report or export query missing tenant filter, includes data from all tenants.

### Symptoms

- Exported CSV includes data from multiple tenants
- Reports show aggregated data across tenants
- Platform admin sees all data, but regular user sees cross-tenant data (bug)

### Root Cause

```kotlin
// ❌ BAD: Report query missing tenant filter
@Query("""
    SELECT p.name, SUM(o.quantity) as total
    FROM products p
    JOIN orders o ON o.product_id = p.id
    GROUP BY p.name
""")
fun getProductSalesReport(): List<SalesReport>
// Returns data from ALL tenants!

// ✅ GOOD: Tenant filter included
@Query("""
    SELECT p.name, SUM(o.quantity) as total
    FROM products p
    JOIN orders o ON o.product_id = p.id
    WHERE p.tenant_id = :tenantId
    GROUP BY p.name
""")
fun getProductSalesReport(@Param("tenantId") tenantId: String): List<SalesReport>
```

### Prevention

- Always include tenant filter in aggregation queries
- Test reports/exports with multiple tenants
- Use Hibernate filters for automatic tenant filtering
- Code review checklist: "Does this query filter by tenant?"

## White-Label Email Templates Not Using Tenant Branding

**Problem:** White-labeled tenant receives platform-branded emails instead of their custom branding.

### Symptoms

- Email "From" name shows "Platform" instead of tenant name
- Email logo is platform logo, not tenant logo
- Email colors are platform colors, not tenant colors

### Root Cause

```kotlin
// ❌ BAD: Email service doesn't use tenant branding
fun sendWelcomeEmail(user: User) {
    val email = Email.builder()
        .from("noreply@platform.com", "Platform") // Hardcoded!
        .subject("Welcome to Platform")
        .template("welcome-email") // No tenant branding
        .build()
    emailService.send(email)
}

// ✅ GOOD: Email uses tenant branding
fun sendWelcomeEmail(user: User, tenant: Tenant) {
    val branding = tenant.branding ?: defaultBranding
    
    val email = Email.builder()
        .from(branding.fromEmail, branding.fromName)
        .subject("Welcome to ${tenant.name}")
        .template("welcome-email")
        .variables(mapOf(
            "logoUrl" to branding.logoUrl,
            "primaryColor" to branding.primaryColor,
            "tenantName" to tenant.name
        ))
        .build()
    emailService.send(email)
}
```

### Prevention

- Always pass tenant context to email service
- Email templates use tenant branding variables
- Test email rendering with multiple tenant brands
- Fallback to platform branding if tenant branding not configured
