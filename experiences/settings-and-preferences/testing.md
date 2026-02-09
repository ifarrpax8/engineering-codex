# Testing: Settings & Preferences

## Contents

- [Default Value Verification](#default-value-verification)
- [Settings Persistence](#settings-persistence)
- [Settings Hierarchy Resolution](#settings-hierarchy-resolution)
- [Settings Migration Testing](#settings-migration-testing)
- [Permission-Gated Settings](#permission-gated-settings)
- [Cross-Tab Settings Propagation](#cross-tab-settings-propagation)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Default Value Verification

Every setting must have a sensible default. New users should get correct defaults without any configuration.

### Unit Tests for Default Values

```kotlin
@Test
fun `new user gets system defaults`() {
    val userId = createTestUser()
    val settings = settingsService.getResolvedSettings(userId)
    
    assertEquals("light", settings.theme)
    assertEquals("en", settings.language)
    assertEquals("comfortable", settings.density)
    assertTrue(settings.emailNotificationsEnabled)
}

@Test
fun `defaults are consistent across user creation`() {
    val user1 = createTestUser()
    val user2 = createTestUser()
    
    val settings1 = settingsService.getResolvedSettings(user1.id)
    val settings2 = settingsService.getResolvedSettings(user2.id)
    
    assertEquals(settings1.theme, settings2.theme)
    assertEquals(settings1.language, settings2.language)
}
```

### Integration Tests for Default Application

```typescript
// Playwright test example
test('new user sees default theme on first visit', async ({ page }) => {
  await page.goto('/signup')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  
  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard')
  
  // Verify default theme is applied
  const theme = await page.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(theme).toBe('light')
  
  // Verify settings page shows defaults
  await page.goto('/settings')
  const themeSelect = page.locator('[name="theme"]')
  await expect(themeSelect).toHaveValue('light')
})
```

### Database-Level Default Constraints

Ensure database enforces defaults even if application code fails:

```sql
CREATE TABLE user_appearance_settings (
    user_id UUID PRIMARY KEY,
    theme VARCHAR(20) NOT NULL DEFAULT 'light',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    density VARCHAR(20) NOT NULL DEFAULT 'comfortable',
    CHECK (theme IN ('light', 'dark', 'system')),
    CHECK (density IN ('compact', 'comfortable', 'spacious'))
);
```

## Settings Persistence

Settings must persist across sessions, page refreshes, and browser restarts.

### Persistence Test Flow

```typescript
test('settings persist after navigation', async ({ page }) => {
  // Navigate to settings
  await page.goto('/settings/appearance')
  
  // Change theme
  await page.selectOption('[name="theme"]', 'dark')
  await page.click('button:has-text("Save")')
  
  // Wait for save confirmation
  await expect(page.locator('.success-message')).toBeVisible()
  
  // Navigate away
  await page.goto('/dashboard')
  
  // Verify theme is still dark
  const theme = await page.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(theme).toBe('dark')
  
  // Reload page
  await page.reload()
  
  // Verify theme persists
  const themeAfterReload = await page.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(themeAfterReload).toBe('dark')
  
  // Verify settings page shows saved value
  await page.goto('/settings/appearance')
  await expect(page.locator('[name="theme"]')).toHaveValue('dark')
})
```

### Backend Persistence Verification

```kotlin
@Test
fun `settings persist in database after update`() {
    val userId = createTestUser()
    
    settingsService.updateAppearanceSettings(userId, mapOf(
        "theme" to "dark",
        "density" to "compact"
    ))
    
    val saved = settingsRepository.getAppearanceSettings(userId)
    
    assertEquals("dark", saved.theme)
    assertEquals("compact", saved.density)
    assertNotNull(saved.updatedAt)
}

@Test
fun `settings persist across sessions`() {
    val userId = createTestUser()
    
    // First session
    settingsService.updateAppearanceSettings(userId, mapOf("theme" to "dark"))
    
    // Simulate new session (new service instance, fresh cache)
    val freshService = createFreshSettingsService()
    val settings = freshService.getResolvedSettings(userId)
    
    assertEquals("dark", settings.theme)
}
```

### localStorage Persistence (for UI-only settings)

```typescript
test('localStorage settings persist across sessions', async ({ context }) => {
  const page1 = await context.newPage()
  await page1.goto('/dashboard')
  
  // Collapse sidebar
  await page1.click('[aria-label="Toggle sidebar"]')
  await page1.waitForTimeout(500) // Wait for localStorage write
  
  // Verify localStorage was written
  const sidebarState = await page1.evaluate(() => 
    localStorage.getItem('sidebarCollapsed')
  )
  expect(sidebarState).toBe('true')
  
  // Close page and create new one (simulates new session)
  await page1.close()
  const page2 = await context.newPage()
  await page2.goto('/dashboard')
  
  // Verify sidebar is still collapsed
  const sidebar = page2.locator('[data-testid="sidebar"]')
  await expect(sidebar).toHaveClass(/collapsed/)
})
```

## Settings Hierarchy Resolution

User overrides must take precedence over org defaults, which take precedence over system defaults.

### Hierarchy Resolution Tests

```kotlin
@Test
fun `user override takes precedence over org default`() {
    val orgId = createTestOrg()
    val userId = createTestUser(orgId = orgId)
    
    // Set org default
    orgSettingsService.updateDefaultTheme(orgId, "dark")
    
    // Set user override
    userSettingsService.updateTheme(userId, "light")
    
    // Resolve settings
    val resolved = settingsResolver.resolveSettings(userId, orgId)
    
    assertEquals("light", resolved.theme) // User override wins
}

@Test
fun `org default used when user has no override`() {
    val orgId = createTestOrg()
    val userId = createTestUser(orgId = orgId)
    
    // Set org default
    orgSettingsService.updateDefaultTheme(orgId, "dark")
    
    // User has no override (null)
    val resolved = settingsResolver.resolveSettings(userId, orgId)
    
    assertEquals("dark", resolved.theme) // Org default used
}

@Test
fun `system default used when org and user have no overrides`() {
    val orgId = createTestOrg()
    val userId = createTestUser(orgId = orgId)
    
    // No org or user overrides
    val resolved = settingsResolver.resolveSettings(userId, orgId)
    
    assertEquals("light", resolved.theme) // System default
}

@Test
fun `removing user override falls back to org default`() {
    val orgId = createTestOrg()
    val userId = createTestUser(orgId = orgId)
    
    // Set org default
    orgSettingsService.updateDefaultTheme(orgId, "dark")
    
    // Set user override
    userSettingsService.updateTheme(userId, "light")
    
    // Remove user override
    userSettingsService.removeOverride(userId, "theme")
    
    // Should fall back to org default
    val resolved = settingsResolver.resolveSettings(userId, orgId)
    assertEquals("dark", resolved.theme)
}
```

### Integration Test for Hierarchy

```typescript
test('user override persists when org default changes', async ({ page, api }) => {
  // Login as org admin
  await page.goto('/login')
  await loginAsOrgAdmin(page)
  
  // Set org default theme to dark
  await api.patch('/api/org/settings', { defaultTheme: 'dark' })
  
  // Login as regular user
  await page.goto('/login')
  await loginAsUser(page)
  
  // User overrides to light
  await page.goto('/settings/appearance')
  await page.selectOption('[name="theme"]', 'light')
  await page.click('button:has-text("Save")')
  
  // Org admin changes org default to system
  await loginAsOrgAdmin(page)
  await api.patch('/api/org/settings', { defaultTheme: 'system' })
  
  // User's override should still be light
  await loginAsUser(page)
  await page.goto('/settings/appearance')
  await expect(page.locator('[name="theme"]')).toHaveValue('light')
  
  // User removes override
  await page.click('button:has-text("Reset to default")')
  
  // Should now use org default (system)
  const theme = await page.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  // System theme depends on OS preference, but should not be 'light'
  expect(theme).not.toBe('light')
})
```

## Settings Migration Testing

When settings schema changes, existing user preferences must migrate correctly without data loss.

### Migration Test Scenarios

```kotlin
@Test
fun `migrates v1 settings to v2 with new field default`() {
    val userId = createTestUser()
    
    // Simulate old v1 settings (no density field)
    repository.saveRawSettings(userId, """
        {
            "version": 1,
            "theme": "dark",
            "language": "en"
        }
    """.trimIndent())
    
    // Access settings (triggers lazy migration)
    val settings = settingsService.getResolvedSettings(userId)
    
    assertEquals("dark", settings.theme)
    assertEquals("en", settings.language)
    assertEquals("comfortable", settings.density) // New field gets default
    
    // Verify migration persisted
    val raw = repository.getRawSettings(userId)
    assertEquals(2, raw.version)
}

@Test
fun `migrates renamed field correctly`() {
    val userId = createTestUser()
    
    // Old schema: "uiTheme"
    repository.saveRawSettings(userId, """
        {
            "version": 1,
            "uiTheme": "dark"
        }
    """.trimIndent())
    
    // New schema: "theme"
    val settings = settingsService.getResolvedSettings(userId)
    
    assertEquals("dark", settings.theme) // Renamed field migrated
}

@Test
fun `migration preserves user overrides`() {
    val userId = createTestUser()
    
    // User had custom theme in v1
    repository.saveRawSettings(userId, """
        {
            "version": 1,
            "theme": "custom-blue"
        }
    """.trimIndent())
    
    val settings = settingsService.getResolvedSettings(userId)
    
    // Custom theme should be preserved (if still valid)
    // Or migrated to closest valid option
    assertNotNull(settings.theme)
}
```

### Backward Compatibility Tests

```kotlin
@Test
fun `handles missing fields gracefully`() {
    val userId = createTestUser()
    
    // Settings with missing optional field
    repository.saveRawSettings(userId, """
        {
            "version": 2,
            "theme": "dark"
            // density field missing
        }
    """.trimIndent())
    
    val settings = settingsService.getResolvedSettings(userId)
    
    assertEquals("dark", settings.theme)
    assertEquals("comfortable", settings.density) // Default for missing field
}

@Test
fun `handles invalid field values`() {
    val userId = createTestUser()
    
    // Invalid theme value
    repository.saveRawSettings(userId, """
        {
            "version": 2,
            "theme": "invalid-theme"
        }
    """.trimIndent())
    
    // Should fall back to default or closest valid value
    val settings = settingsService.getResolvedSettings(userId)
    
    assertTrue(setOf("light", "dark", "system").contains(settings.theme))
}
```

## Permission-Gated Settings

Admin-only settings must not be visible or editable by regular users.

### Permission Tests

```kotlin
@Test
fun `regular user cannot access admin settings`() {
    val userId = createTestUser(role = Role.USER)
    
    val exception = assertThrows<AccessDeniedException> {
        settingsService.updateOrgSettings(userId, orgId, mapOf(
            "ssoEnabled" to true
        ))
    }
    
    assertTrue(exception.message?.contains("permission") == true)
}

@Test
fun `admin can access admin settings`() {
    val orgId = createTestOrg()
    val adminId = createTestUser(orgId = orgId, role = Role.ADMIN)
    
    settingsService.updateOrgSettings(adminId, orgId, mapOf(
        "ssoEnabled" to true
    ))
    
    val orgSettings = orgSettingsService.getOrgSettings(orgId)
    assertTrue(orgSettings.ssoEnabled)
}
```

### UI Permission Tests

```typescript
test('admin-only settings hidden from regular users', async ({ page }) => {
  // Login as regular user
  await page.goto('/login')
  await loginAsUser(page)
  
  await page.goto('/settings')
  
  // Admin section should not be visible
  await expect(page.locator('[data-testid="admin-settings"]')).not.toBeVisible()
  
  // Regular settings should be visible
  await expect(page.locator('[data-testid="appearance-settings"]')).toBeVisible()
})

test('admin sees admin settings section', async ({ page }) => {
  // Login as admin
  await page.goto('/login')
  await loginAsAdmin(page)
  
  await page.goto('/settings')
  
  // Admin section should be visible
  await expect(page.locator('[data-testid="admin-settings"]')).toBeVisible()
  
  // Can update org settings
  await page.click('[data-testid="org-settings-tab"]')
  await expect(page.locator('[name="ssoEnabled"]')).toBeVisible()
})
```

## Cross-Tab Settings Propagation

Settings changes in one browser tab should reflect in other tabs without manual refresh.

### Cross-Tab Propagation Tests

```typescript
test('theme change propagates to other tabs', async ({ context }) => {
  // Open two tabs
  const page1 = await context.newPage()
  const page2 = await context.newPage()
  
  await page1.goto('/dashboard')
  await page2.goto('/dashboard')
  
  // Verify both start with same theme
  const theme1Before = await page1.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  const theme2Before = await page2.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(theme1Before).toBe(theme2Before)
  
  // Change theme in tab 1
  await page1.goto('/settings/appearance')
  await page1.selectOption('[name="theme"]', 'dark')
  await page1.click('button:has-text("Save")')
  await page1.waitForTimeout(1000) // Wait for BroadcastChannel message
  
  // Tab 2 should update automatically
  const theme2After = await page2.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(theme2After).toBe('dark')
  
  // Tab 1 should also be dark
  const theme1After = await page1.evaluate(() => 
    document.documentElement.getAttribute('data-theme')
  )
  expect(theme1After).toBe('dark')
})
```

### BroadcastChannel Implementation Test

```typescript
test('BroadcastChannel sends settings update message', async ({ page }) => {
  await page.goto('/settings/appearance')
  
  // Set up message listener
  const messages: any[] = []
  await page.evaluate(() => {
    const channel = new BroadcastChannel('settings-sync')
    channel.onmessage = (event) => {
      (window as any).testMessages = ((window as any).testMessages || []).concat(event.data)
    }
  })
  
  // Change setting
  await page.selectOption('[name="theme"]', 'dark')
  await page.click('button:has-text("Save")')
  await page.waitForTimeout(500)
  
  // Check message was sent
  const messages = await page.evaluate(() => (window as any).testMessages)
  expect(messages).toHaveLength(1)
  expect(messages[0].type).toBe('SETTINGS_UPDATED')
  expect(messages[0].settings.theme).toBe('dark')
})
```

## QA and Test Engineer Perspective

### Test Coverage Checklist

**Default Values**
- [ ] Every setting has a documented default
- [ ] New users receive correct defaults
- [ ] Defaults are consistent across user creation
- [ ] Database constraints enforce defaults
- [ ] Application code applies defaults when settings are null

**Persistence**
- [ ] Settings persist after page refresh
- [ ] Settings persist after browser restart
- [ ] Settings persist across devices (if synced)
- [ ] Settings persist after logout/login
- [ ] Partial updates don't lose other settings
- [ ] Concurrent updates are handled correctly (last write wins or merge)

**Hierarchy Resolution**
- [ ] User override takes precedence over org default
- [ ] Org default takes precedence over system default
- [ ] Removing user override falls back to org default
- [ ] Removing org default falls back to system default
- [ ] Org default changes affect users without overrides
- [ ] Org default changes don't affect users with overrides

**Migration**
- [ ] Old settings migrate to new schema automatically
- [ ] Migration preserves user preferences
- [ ] Migration handles missing fields gracefully
- [ ] Migration handles invalid values gracefully
- [ ] Migration is idempotent (can run multiple times safely)
- [ ] Migration doesn't cause data loss

**Permissions**
- [ ] Regular users cannot access admin settings
- [ ] Admin users can access admin settings
- [ ] Permission checks happen on both frontend and backend
- [ ] Permission errors are user-friendly
- [ ] Settings visibility matches edit permissions

**Cross-Tab Propagation**
- [ ] Settings changes propagate to other tabs
- [ ] Propagation happens within 1-2 seconds
- [ ] Propagation works for theme/appearance changes
- [ ] Propagation doesn't cause infinite loops
- [ ] Propagation handles closed tabs gracefully

### Test Data Management

**Test Users**: Create users with different roles (regular, admin, org admin) and different setting configurations (defaults, overrides, missing settings).

**Test Organizations**: Create orgs with different default settings to test hierarchy resolution.

**Test Scenarios**: Cover edge cases like concurrent updates, network failures during save, invalid values, missing fields, schema migrations.

### Regression Testing

**Smoke Tests**: After each release, verify that:
- New users get correct defaults
- Existing users' settings are preserved
- Settings page loads without errors
- Common settings (theme, notifications) can be updated

**Full Regression**: Before major releases, test all settings categories, all permission levels, and all hierarchy scenarios.

### Performance Testing

**Settings Load Time**: Settings page should load in under 2 seconds, even with many settings categories.

**Save Performance**: Settings updates should complete in under 1 second and provide immediate feedback.

**Cache Performance**: Verify Redis caching reduces database load for frequently-accessed settings.
