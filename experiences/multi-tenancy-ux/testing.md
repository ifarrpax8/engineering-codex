# Testing: Multi-Tenancy UX

## Contents

- [Tenant Isolation Testing](#tenant-isolation-testing)
- [Tenant Switching Testing](#tenant-switching-testing)
- [White-Label Testing](#white-label-testing)
- [Cross-Tenant Permission Testing](#cross-tenant-permission-testing)
- [Impersonation Testing](#impersonation-testing)
- [URL/Deep Link Testing](#urldeep-link-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Tenant Isolation Testing

**Critical security test:** Data from Tenant A must never be visible to users of Tenant B. This is the most important test in multi-tenant systems.

### Test: User Cannot See Other Tenant's Data

```typescript
// Playwright test: Verify tenant data isolation
import { test, expect } from '@playwright/test'

test('user cannot see data from other tenants', async ({ page }) => {
  // Login as user with access to Tenant A
  await loginAsUser(page, 'user-a@example.com', 'password')
  await selectTenant(page, 'tenant-a')
  
  // Create an order in Tenant A
  const orderId = await createOrder(page, { productId: 'prod-123', quantity: 5 })
  
  // Switch to Tenant B (user also has access)
  await selectTenant(page, 'tenant-b')
  
  // Verify order from Tenant A is NOT visible
  await page.goto('/tenant-b/orders')
  await expect(page.locator(`[data-order-id="${orderId}"]`)).not.toBeVisible()
  
  // Verify API doesn't return Tenant A's order
  const response = await page.request.get('/api/orders')
  const orders = await response.json()
  expect(orders).not.toContainEqual(expect.objectContaining({ id: orderId }))
})
```

### Test: API Filters by Tenant Automatically

```kotlin
// Spring Boot integration test
@SpringBootTest
@AutoConfigureMockMvc
class TenantIsolationTest {
    
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Autowired
    lateinit var orderRepository: OrderRepository
    
    @Test
    fun `API returns only tenant-scoped data`() {
        // Create orders for two tenants
        val tenantAOrder = Order(tenantId = "tenant-a", productId = "prod-1")
        val tenantBOrder = Order(tenantId = "tenant-b", productId = "prod-2")
        orderRepository.saveAll(listOf(tenantAOrder, tenantBOrder))
        
        // Request as Tenant A user
        val response = mockMvc.perform(
            get("/api/orders")
                .header("X-Tenant-Id", "tenant-a")
                .header("Authorization", "Bearer ${tenantAToken}")
        )
            .andExpect(status().isOk)
            .andReturn()
        
        val orders = objectMapper.readValue<List<Order>>(response.response.contentAsString)
        
        // Verify only Tenant A's order is returned
        assertThat(orders).hasSize(1)
        assertThat(orders[0].tenantId).isEqualTo("tenant-a")
        assertThat(orders).noneMatch { it.tenantId == "tenant-b" }
    }
}
```

### Test: Cache Does Not Mix Tenant Data

```typescript
// Test: Verify cache keys include tenant ID
test('cache does not mix tenant data', async ({ page }) => {
  // Load products in Tenant A
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/products')
  const tenantAProducts = await page.locator('[data-product]').count()
  
  // Load products in Tenant B
  await selectTenant(page, 'tenant-b')
  await page.goto('/tenant-b/products')
  const tenantBProducts = await page.locator('[data-product]').count()
  
  // Switch back to Tenant A
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/products')
  
  // Verify Tenant A's products are still correct (not mixed with Tenant B)
  const productsAfterSwitch = await page.locator('[data-product]').count()
  expect(productsAfterSwitch).toBe(tenantAProducts)
  
  // Verify no Tenant B products appear
  const productIds = await page.locator('[data-product]').allTextContents()
  expect(productIds).not.toContain(expect.stringContaining('tenant-b'))
})
```

## Tenant Switching Testing

Switching tenants must work smoothly with proper state management and data refresh.

### Test: Tenant Switch Clears Previous Data

```typescript
test('tenant switch clears previous tenant data', async ({ page }) => {
  // Load data in Tenant A
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/dashboard')
  
  // Verify Tenant A data is loaded
  await expect(page.locator('[data-tenant="tenant-a"]')).toBeVisible()
  const tenantAData = await page.locator('[data-testid="dashboard-data"]').textContent()
  
  // Switch to Tenant B
  await selectTenant(page, 'tenant-b')
  
  // Verify Tenant A data is cleared
  await expect(page.locator('[data-tenant="tenant-a"]')).not.toBeVisible()
  
  // Verify Tenant B data is loaded
  await expect(page.locator('[data-tenant="tenant-b"]')).toBeVisible()
  const tenantBData = await page.locator('[data-testid="dashboard-data"]').textContent()
  
  expect(tenantBData).not.toBe(tenantAData)
})
```

### Test: Permissions Update on Tenant Switch

```typescript
test('permissions update when switching tenants', async ({ page }) => {
  // User is Admin in Tenant A
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/users')
  
  // Verify admin actions are visible
  await expect(page.locator('[data-action="create-user"]')).toBeVisible()
  await expect(page.locator('[data-action="delete-user"]')).toBeVisible()
  
  // Switch to Tenant B (user is Viewer)
  await selectTenant(page, 'tenant-b')
  await page.goto('/tenant-b/users')
  
  // Verify admin actions are hidden
  await expect(page.locator('[data-action="create-user"]')).not.toBeVisible()
  await expect(page.locator('[data-action="delete-user"]')).not.toBeVisible()
  
  // Verify read-only message is shown
  await expect(page.locator('text=You have read-only access')).toBeVisible()
})
```

### Test: Navigation Updates on Tenant Switch

```typescript
test('navigation updates based on tenant plan', async ({ page }) => {
  // Tenant A has Enterprise plan (all features)
  await selectTenant(page, 'tenant-a')
  
  await expect(page.locator('nav >> text=Advanced Analytics')).toBeVisible()
  await expect(page.locator('nav >> text=Custom Reports')).toBeVisible()
  
  // Tenant B has Basic plan (limited features)
  await selectTenant(page, 'tenant-b')
  
  await expect(page.locator('nav >> text=Advanced Analytics')).not.toBeVisible()
  await expect(page.locator('nav >> text=Custom Reports')).not.toBeVisible()
  await expect(page.locator('nav >> text=Dashboard')).toBeVisible()
})
```

## White-Label Testing

White-labeling must work correctly with proper fallbacks and validation.

### Test: Custom Branding Renders Correctly

```typescript
test('custom branding renders correctly', async ({ page }) => {
  // Tenant with custom branding
  await selectTenant(page, 'tenant-branded')
  
  // Verify custom logo is displayed
  const logo = page.locator('[data-testid="tenant-logo"]')
  await expect(logo).toHaveAttribute('src', expect.stringContaining('custom-logo.png'))
  
  // Verify custom colors are applied
  const header = page.locator('header')
  await expect(header).toHaveCSS('background-color', 'rgb(26, 115, 232)') // Custom primary color
  
  // Verify custom font is applied (if configured)
  const body = page.locator('body')
  const fontFamily = await body.evaluate(el => getComputedStyle(el).fontFamily)
  expect(fontFamily).toContain('Custom Font')
})
```

### Test: Fallback to Default When Branding Not Configured

```typescript
test('falls back to default branding when not configured', async ({ page }) => {
  // Tenant without custom branding
  await selectTenant(page, 'tenant-unbranded')
  
  // Verify default logo is shown
  const logo = page.locator('[data-testid="tenant-logo"]')
  await expect(logo).toHaveAttribute('src', '/default-logo.svg')
  
  // Verify default colors are applied
  const header = page.locator('header')
  await expect(header).toHaveCSS('background-color', 'rgb(25, 118, 210)') // Default primary
})
```

### Test: Logo Error Handling

```typescript
test('handles logo load errors gracefully', async ({ page }) => {
  // Tenant with invalid logo URL
  await selectTenant(page, 'tenant-broken-logo')
  
  // Trigger logo error
  await page.route('**/logo.png', route => route.abort())
  await page.reload()
  
  // Verify fallback is shown (tenant name text or default logo)
  const logo = page.locator('[data-testid="tenant-logo"]')
  await expect(logo).toHaveAttribute('src', '/default-logo.svg')
  
  // Or verify tenant name is shown as text
  await expect(page.locator('text=Acme Corp')).toBeVisible()
})
```

## Cross-Tenant Permission Testing

Same user must have different permissions in different tenants.

### Test: Role Differences Per Tenant

```typescript
test('user has different roles in different tenants', async ({ page }) => {
  // Login as user with multi-tenant access
  await loginAsUser(page, 'multi-tenant-user@example.com', 'password')
  
  // Check Tenant A role
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/profile')
  await expect(page.locator('[data-role="admin"]')).toBeVisible()
  
  // Check Tenant B role
  await selectTenant(page, 'tenant-b')
  await page.goto('/tenant-b/profile')
  await expect(page.locator('[data-role="viewer"]')).toBeVisible()
  
  // Verify UI adapts to role
  await page.goto('/tenant-b/users')
  await expect(page.locator('[data-action="create-user"]')).not.toBeVisible() // Viewer can't create
})
```

### Test: Permission Caching Does Not Leak

```typescript
test('permissions are not cached across tenants', async ({ page }) => {
  // Load Tenant A (Admin permissions)
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/users')
  
  // Verify admin permissions are active
  await expect(page.locator('[data-action="delete-user"]')).toBeVisible()
  
  // Switch to Tenant B (Viewer permissions)
  await selectTenant(page, 'tenant-b')
  await page.goto('/tenant-b/users')
  
  // Verify admin permissions from Tenant A are NOT active
  await expect(page.locator('[data-action="delete-user"]')).not.toBeVisible()
  
  // Switch back to Tenant A
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/users')
  
  // Verify admin permissions are restored
  await expect(page.locator('[data-action="delete-user"]')).toBeVisible()
})
```

## Impersonation Testing

Impersonation must work correctly with clear indicators and proper audit trails.

### Test: Impersonation Works Correctly

```typescript
test('platform admin can impersonate tenant', async ({ page }) => {
  // Login as platform admin
  await loginAsUser(page, 'admin@pax8.com', 'password')
  
  // Start impersonation
  await page.goto('/admin/impersonate')
  await page.selectOption('[data-testid="tenant-select"]', 'tenant-a')
  await page.click('[data-testid="start-impersonation"]')
  
  // Verify impersonation banner is visible
  await expect(page.locator('[data-testid="impersonation-banner"]')).toBeVisible()
  await expect(page.locator('text=Viewing as Tenant A')).toBeVisible()
  
  // Verify UI shows tenant context
  await expect(page.locator('[data-tenant="tenant-a"]')).toBeVisible()
  
  // Verify can perform actions as that tenant
  await page.goto('/tenant-a/dashboard')
  await expect(page.locator('[data-testid="dashboard"]')).toBeVisible()
})
```

### Test: Impersonation Indicator Always Visible

```typescript
test('impersonation indicator persists across navigation', async ({ page }) => {
  await loginAsPlatformAdmin(page)
  await startImpersonation(page, 'tenant-a')
  
  // Navigate to different pages
  await page.goto('/tenant-a/dashboard')
  await expect(page.locator('[data-testid="impersonation-banner"]')).toBeVisible()
  
  await page.goto('/tenant-a/products')
  await expect(page.locator('[data-testid="impersonation-banner"]')).toBeVisible()
  
  await page.goto('/tenant-a/users')
  await expect(page.locator('[data-testid="impersonation-banner"]')).toBeVisible()
})
```

### Test: Exit Impersonation

```typescript
test('can exit impersonation', async ({ page }) => {
  await loginAsPlatformAdmin(page)
  await startImpersonation(page, 'tenant-a')
  
  // Verify impersonation is active
  await expect(page.locator('[data-testid="impersonation-banner"]')).toBeVisible()
  
  // Exit impersonation
  await page.click('[data-testid="exit-impersonation"]')
  
  // Verify impersonation banner is gone
  await expect(page.locator('[data-testid="impersonation-banner"]')).not.toBeVisible()
  
  // Verify redirected to admin area
  await expect(page).toHaveURL(/\/admin\/dashboard/)
})
```

### Test: Audit Trail Captured

```kotlin
// Backend test: Verify impersonation actions are logged
@Test
fun `impersonation actions are audited`() {
    val adminUser = createUser(role = Role.PLATFORM_ADMIN)
    val tenant = createTenant("tenant-a")
    
    impersonationService.startImpersonation(
        adminUserId = adminUser.id,
        tenantId = tenant.id
    )
    
    val auditLogs = auditLogRepository.findByAction("IMPERSONATION_START")
    
    assertThat(auditLogs).hasSize(1)
    assertThat(auditLogs[0].adminUserId).isEqualTo(adminUser.id)
    assertThat(auditLogs[0].tenantId).isEqualTo(tenant.id)
    assertThat(auditLogs[0].timestamp).isNotNull()
}
```

## URL/Deep Link Testing

URLs must preserve tenant context and work correctly when shared.

### Test: Tenant Context Preserved in URLs

```typescript
test('tenant context preserved in URL', async ({ page }) => {
  await selectTenant(page, 'tenant-a')
  await page.goto('/tenant-a/products/123')
  
  // Verify URL includes tenant slug
  await expect(page).toHaveURL(/\/tenant-a\/products\/123/)
  
  // Navigate to different page
  await page.click('[href="/tenant-a/orders"]')
  await expect(page).toHaveURL(/\/tenant-a\/orders/)
})
```

### Test: Deep Links Work for Authorized Users

```typescript
test('deep link works for authorized user', async ({ page }) => {
  // User has access to Tenant A
  await loginAsUser(page, 'user@example.com', 'password')
  
  // Direct navigation to tenant-specific URL
  await page.goto('/tenant-a/products/123')
  
  // Verify page loads correctly
  await expect(page.locator('[data-product-id="123"]')).toBeVisible()
  await expect(page.locator('[data-tenant="tenant-a"]')).toBeVisible()
})
```

### Test: Deep Links Fail for Unauthorized Users

```typescript
test('deep link fails for unauthorized user', async ({ page }) => {
  // User does NOT have access to Tenant B
  await loginAsUser(page, 'tenant-a-only-user@example.com', 'password')
  
  // Attempt to access Tenant B URL
  await page.goto('/tenant-b/products/123')
  
  // Verify unauthorized error or redirect
  await expect(page.locator('text=Access Denied')).toBeVisible()
  // OR redirect to user's default tenant
  await expect(page).toHaveURL(/\/tenant-a\//)
})
```

## QA and Test Engineer Perspective

### Test Strategy: Tenant Isolation

**Priority:** Critical (P0)
**Test coverage:** Every data access point must be tested for tenant isolation
**Automation:** Automated tests in CI/CD pipeline, manual security audits quarterly

**Test cases:**
- API endpoints return only tenant-scoped data
- Frontend cache does not mix tenant data
- Database queries include tenant filter
- Reports/exports are tenant-scoped
- Search results are tenant-scoped

### Test Strategy: Tenant Switching

**Priority:** High (P1)
**Test coverage:** All switching mechanisms, state clearing, permission updates
**Automation:** E2E tests for switching flows

**Test cases:**
- Header dropdown switching works
- Dedicated switcher page works
- URL-based switching works
- State is cleared on switch
- Permissions update on switch
- Navigation updates on switch
- Performance: switch completes in <2 seconds

### Test Strategy: White-Labeling

**Priority:** Medium (P2)
**Test coverage:** Branding rendering, fallbacks, edge cases
**Automation:** Visual regression tests for branded tenants

**Test cases:**
- Custom logo displays correctly
- Custom colors apply throughout UI
- Fallback to default when not configured
- Logo error handling
- Email branding uses tenant colors/logo
- Custom domain routing works

### Test Strategy: Cross-Tenant Permissions

**Priority:** High (P1)
**Test coverage:** Permission differences per tenant, caching behavior
**Automation:** Permission matrix tests

**Test cases:**
- Same user has different roles in different tenants
- UI adapts to role per tenant
- Permission cache does not leak between tenants
- Feature flags respect tenant plan + user role

### Test Strategy: Impersonation

**Priority:** Medium (P2)
**Test coverage:** Impersonation flow, indicators, audit logging
**Automation:** E2E tests for impersonation

**Test cases:**
- Platform admin can start impersonation
- Impersonation banner always visible
- Can exit impersonation
- Audit trail captures all impersonation actions
- Impersonated user cannot perform admin actions on platform

### Test Strategy: URL/Deep Links

**Priority:** Medium (P2)
**Test coverage:** Tenant context in URLs, deep link sharing
**Automation:** URL routing tests

**Test cases:**
- Tenant slug preserved in URL
- Deep links work for authorized users
- Deep links fail for unauthorized users
- Sharing URLs preserves tenant context
- Browser back/forward works with tenant context
