# Permissions UX -- Testing

## Contents

- [Permission Enforcement Testing](#permission-enforcement-testing)
- [Hide vs Disable Testing](#hide-vs-disable-testing)
- [Permission Boundary Testing](#permission-boundary-testing)
- [Request Access Flow Testing](#request-access-flow-testing)
- [Multi-Tenant Permission Testing](#multi-tenant-permission-testing)
- [Role-Based Navigation Testing](#role-based-navigation-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Permission Enforcement Testing

**Critical**: Verify server rejects unauthorized requests even if UI allows them. Frontend permission checks are a convenience, not a security boundary.

### Penetration Testing Approach

```typescript
// Playwright: Test that disabled buttons don't actually work
test('disabled delete button should not send request', async ({ page }) => {
  await page.goto('/projects/123')
  
  const deleteButton = page.getByRole('button', { name: 'Delete' })
  
  // Verify button is disabled
  await expect(deleteButton).toBeDisabled()
  
  // Try to force click (bypassing disabled state)
  await deleteButton.evaluate((btn: HTMLButtonElement) => {
    btn.removeAttribute('disabled')
    btn.click()
  })
  
  // Verify no API call was made OR server rejected it
  const response = await page.waitForResponse('**/projects/123', { timeout: 2000 })
    .catch(() => null)
  
  // Should either not exist (button prevented click) or be 403
  if (response) {
    expect(response.status()).toBe(403)
  }
})
```

### API-Level Permission Testing

```kotlin
// Kotlin + JUnit: Test server-side enforcement
@SpringBootTest
@AutoConfigureMockMvc
class ProjectControllerPermissionTest {
    
    @Test
    fun `delete project should return 403 for non-admin`() {
        val nonAdminToken = createTokenForUser("viewer")
        
        mockMvc.perform(
            delete("/api/projects/123")
                .header("Authorization", "Bearer $nonAdminToken")
        )
            .andExpect(status().isForbidden)
    }
    
    @Test
    fun `delete project should succeed for admin`() {
        val adminToken = createTokenForUser("admin")
        
        mockMvc.perform(
            delete("/api/projects/123")
                .header("Authorization", "Bearer $adminToken")
        )
            .andExpect(status().isNoContent)
    }
}
```

```typescript
// Playwright: Test API directly
test('API should reject unauthorized delete', async ({ request }) => {
  const response = await request.delete('/api/projects/123', {
    headers: {
      'Authorization': `Bearer ${viewerToken}`
    }
  })
  
  expect(response.status()).toBe(403)
  expect(await response.json()).toMatchObject({
    error: 'Forbidden',
    message: expect.stringContaining('permission')
  })
})
```

## Hide vs Disable Testing

Verify correct elements are hidden/disabled for each role:

```typescript
// Playwright: Test visibility based on role
test.describe('Permission-based UI visibility', () => {
  test('viewer should not see admin navigation', async ({ page }) => {
    await loginAsRole(page, 'viewer')
    await page.goto('/dashboard')
    
    // Should not see admin nav items
    await expect(page.getByRole('link', { name: 'Settings' })).not.toBeVisible()
    await expect(page.getByRole('link', { name: 'User Management' })).not.toBeVisible()
    
    // Should see viewer nav items
    await expect(page.getByRole('link', { name: 'Projects' })).toBeVisible()
  })
  
  test('editor should see edit button but disabled delete', async ({ page }) => {
    await loginAsRole(page, 'editor')
    await page.goto('/projects/123')
    
    // Edit button should be enabled
    await expect(page.getByRole('button', { name: 'Edit' })).toBeEnabled()
    
    // Delete button should be disabled with tooltip
    const deleteButton = page.getByRole('button', { name: 'Delete' })
    await expect(deleteButton).toBeDisabled()
    await expect(deleteButton).toHaveAttribute('title', expect.stringContaining('admin'))
  })
  
  test('admin should see all actions enabled', async ({ page }) => {
    await loginAsRole(page, 'admin')
    await page.goto('/projects/123')
    
    await expect(page.getByRole('button', { name: 'Edit' })).toBeEnabled()
    await expect(page.getByRole('button', { name: 'Delete' })).toBeEnabled()
  })
})
```

### Visual Regression Testing

```typescript
// Playwright: Visual comparison for different roles
test('admin dashboard should show admin widgets', async ({ page }) => {
  await loginAsRole(page, 'admin')
  await page.goto('/dashboard')
  
  await expect(page).toHaveScreenshot('admin-dashboard.png')
})

test('viewer dashboard should not show admin widgets', async ({ page }) => {
  await loginAsRole(page, 'viewer')
  await page.goto('/dashboard')
  
  await expect(page).toHaveScreenshot('viewer-dashboard.png')
})
```

## Permission Boundary Testing

Test edge cases around permission changes:

### Role Changes Mid-Session

```typescript
// Playwright: Test permission update during session
test('UI should update when role changes mid-session', async ({ page, context }) => {
  await loginAsRole(page, 'viewer')
  await page.goto('/dashboard')
  
  // Verify viewer state
  await expect(page.getByRole('link', { name: 'Settings' })).not.toBeVisible()
  
  // Admin grants admin role (simulate via API)
  await grantRole(context, 'admin')
  
  // Trigger permission refresh (or wait for WebSocket update)
  await page.reload() // Or wait for permission update event
  
  // Verify admin state
  await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible()
})
```

### Permission Revoked While Page Open

```typescript
// Playwright: Test permission revocation
test('disabled button should appear when permission revoked', async ({ page, context }) => {
  await loginAsRole(page, 'admin')
  await page.goto('/projects/123')
  
  // Verify delete button is enabled
  await expect(page.getByRole('button', { name: 'Delete' })).toBeEnabled()
  
  // Revoke permission
  await revokePermission(context, 'project:delete')
  
  // Wait for permission update (WebSocket or polling)
  await page.waitForTimeout(1000) // Or wait for specific event
  
  // Verify button is now disabled
  await expect(page.getByRole('button', { name: 'Delete' })).toBeDisabled()
})
```

### Stale Permission Cache

```typescript
// Test that stale cache doesn't allow unauthorized actions
test('stale permission cache should not bypass server check', async ({ page, context }) => {
  await loginAsRole(page, 'admin')
  await page.goto('/projects/123')
  
  // Manually set stale permissions in localStorage
  await page.evaluate(() => {
    localStorage.setItem('permissions', JSON.stringify({
      permissions: ['project:delete'],
      timestamp: Date.now() - 3600000 // 1 hour ago
    }))
  })
  
  // Revoke permission on server
  await revokePermission(context, 'project:delete')
  
  // Try to delete (should fail on server)
  await page.getByRole('button', { name: 'Delete' }).click()
  
  // Should show error (server rejected)
  await expect(page.getByText('Permission denied')).toBeVisible()
})
```

## Request Access Flow Testing

Test the complete request → approve → grant → notify flow:

```typescript
// Playwright: End-to-end request access flow
test('user can request access and receive approval', async ({ page, context }) => {
  // 1. User sees restricted feature
  await loginAsRole(page, 'viewer')
  await page.goto('/projects/123')
  
  // 2. User clicks "Request access" button
  const requestButton = page.getByRole('button', { name: 'Request access' })
  await expect(requestButton).toBeVisible()
  await requestButton.click()
  
  // 3. Fill request form
  await page.getByLabel('Reason').fill('Need to delete old projects')
  await page.getByRole('button', { name: 'Submit Request' }).click()
  
  // 4. Verify request submitted
  await expect(page.getByText('Request submitted')).toBeVisible()
  
  // 5. Admin approves (simulate via API)
  const requestId = await getLatestRequestId(context)
  await approveRequest(context, requestId)
  
  // 6. User receives notification (or refresh)
  await page.reload()
  await expect(page.getByText('Access granted')).toBeVisible()
  
  // 7. Feature is now available
  await expect(page.getByRole('button', { name: 'Delete' })).toBeEnabled()
})
```

### Request Denial Flow

```typescript
test('user receives notification when request denied', async ({ page, context }) => {
  await loginAsRole(page, 'viewer')
  await page.goto('/projects/123')
  
  // Submit request
  await page.getByRole('button', { name: 'Request access' }).click()
  await page.getByLabel('Reason').fill('Test request')
  await page.getByRole('button', { name: 'Submit Request' }).click()
  
  // Admin denies
  const requestId = await getLatestRequestId(context)
  await denyRequest(context, requestId, 'Insufficient justification')
  
  // User sees denial notification
  await page.reload()
  await expect(page.getByText('Request denied')).toBeVisible()
  await expect(page.getByText('Insufficient justification')).toBeVisible()
})
```

### Request Timeout

```typescript
test('request should timeout after X days', async ({ page, context }) => {
  // Create old request
  const oldRequestId = await createRequest(context, {
    permission: 'project:delete',
    createdAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000) // 8 days ago
  })
  
  // Trigger timeout check
  await processRequestTimeouts(context)
  
  // Request should be auto-denied
  const request = await getRequest(context, oldRequestId)
  expect(request.status).toBe('TIMEOUT')
})
```

## Multi-Tenant Permission Testing

Test that switching tenants changes available actions:

```typescript
// Playwright: Multi-tenant permission testing
test('permissions should change on tenant switch', async ({ page }) => {
  await loginAsRole(page, 'admin', { tenantId: 'tenant-a' })
  await page.goto('/dashboard')
  
  // Verify tenant A permissions
  await expect(page.getByRole('link', { name: 'Billing' })).toBeVisible()
  
  // Switch to tenant B
  await page.getByRole('button', { name: 'Switch Tenant' }).click()
  await page.getByText('Tenant B').click()
  
  // Wait for permission reload
  await page.waitForURL('/dashboard')
  
  // Verify tenant B permissions (different)
  await expect(page.getByRole('link', { name: 'Billing' })).not.toBeVisible()
  await expect(page.getByRole('link', { name: 'Reports' })).toBeVisible()
})
```

### Tenant Permission Isolation

```typescript
test('tenant A permissions should not leak to tenant B', async ({ page, context }) => {
  // User has admin in tenant A, viewer in tenant B
  await loginAsRole(page, 'admin', { tenantId: 'tenant-a' })
  
  // Switch to tenant B
  await switchTenant(page, 'tenant-b')
  
  // Verify admin actions are not available
  await expect(page.getByRole('button', { name: 'Delete' })).toBeDisabled()
  
  // Try to perform admin action (should fail on server)
  await page.goto('/api/projects/123/delete', { waitUntil: 'networkidle' })
  // Should redirect to error page or show 403
})
```

## Role-Based Navigation Testing

Test that each role sees correct navigation items:

```typescript
// Playwright: Role-based navigation matrix
const roleNavigationMatrix = {
  viewer: ['Projects', 'Reports'],
  editor: ['Projects', 'Reports', 'Templates'],
  admin: ['Projects', 'Reports', 'Templates', 'Settings', 'User Management']
}

for (const [role, expectedNavItems] of Object.entries(roleNavigationMatrix)) {
  test(`${role} should see correct navigation items`, async ({ page }) => {
    await loginAsRole(page, role)
    await page.goto('/dashboard')
    
    // Verify expected items are visible
    for (const item of expectedNavItems) {
      await expect(page.getByRole('link', { name: item })).toBeVisible()
    }
    
    // Verify other items are not visible
    const allNavItems = ['Projects', 'Reports', 'Templates', 'Settings', 'User Management']
    const hiddenItems = allNavItems.filter(item => !expectedNavItems.includes(item))
    
    for (const item of hiddenItems) {
      await expect(page.getByRole('link', { name: item })).not.toBeVisible()
    }
  })
}
```

## QA and Test Engineer Perspective

### Test Data Setup

**Challenge**: Creating users with specific permission combinations for testing.

**Solution**: Use test fixtures or API helpers:

```typescript
// test-helpers/permissions.ts
export const createTestUser = async (role: string, permissions?: string[]) => {
  const user = await api.post('/test/users', {
    email: `test-${Date.now()}@example.com`,
    role,
    permissions: permissions || getDefaultPermissions(role)
  })
  return user
}

export const grantPermission = async (userId: string, permission: string) => {
  await api.post(`/test/users/${userId}/permissions`, { permission })
}

export const revokePermission = async (userId: string, permission: string) => {
  await api.delete(`/test/users/${userId}/permissions/${permission}`)
}
```

### Permission Test Coverage

**Matrix approach**: Test all role × permission × action combinations:

```typescript
// Generate test cases for permission matrix
const roles = ['viewer', 'editor', 'admin']
const actions = ['view', 'create', 'edit', 'delete']
const resources = ['project', 'report', 'user']

for (const role of roles) {
  for (const resource of resources) {
    for (const action of actions) {
      test(`${role} ${action} ${resource}`, async ({ page }) => {
        await loginAsRole(page, role)
        const hasPermission = getExpectedPermission(role, resource, action)
        
        if (hasPermission) {
          await expectActionEnabled(page, resource, action)
        } else {
          await expectActionDisabledOrHidden(page, resource, action)
        }
      })
    }
  }
}
```

### Regression Testing

**Focus areas**:
1. **Permission changes don't break existing flows**: When permissions are updated, verify existing user flows still work
2. **New features respect permissions**: New features must check permissions before allowing actions
3. **Permission UI consistency**: Same permission level should behave consistently across the app

### Performance Testing

**Concern**: Permission checks on every render can impact performance.

**Test**: Verify permission checks don't cause performance degradation:

```typescript
test('permission checks should not impact render performance', async ({ page }) => {
  await loginAsRole(page, 'admin')
  
  const startTime = Date.now()
  await page.goto('/dashboard')
  await page.waitForLoadState('networkidle')
  const loadTime = Date.now() - startTime
  
  // Should load within acceptable time (e.g., < 2 seconds)
  expect(loadTime).toBeLessThan(2000)
})
```

### Accessibility Testing

**Critical**: Disabled elements must be accessible:

```typescript
test('disabled buttons should have proper ARIA attributes', async ({ page }) => {
  await loginAsRole(page, 'viewer')
  await page.goto('/projects/123')
  
  const deleteButton = page.getByRole('button', { name: 'Delete' })
  
  // Should have aria-disabled
  await expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
  
  // Should have title/tooltip explaining why
  await expect(deleteButton).toHaveAttribute('title', expect.stringMatching(/permission|admin|access/i))
  
  // Screen reader should announce disabled state
  // (Test with screen reader or accessibility testing tool)
})
```

### Integration with CI/CD

**Automated permission testing in pipeline**:

```yaml
# .github/workflows/permission-tests.yml
- name: Run Permission Tests
  run: |
    npm run test:permissions
    npm run test:e2e:permissions
```

**Test categories**:
- Unit tests: Permission utility functions, permission checks
- Integration tests: API permission enforcement
- E2E tests: UI permission visibility, request access flows
