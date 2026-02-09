# Gotchas: Settings & Preferences

## Contents

- [Settings Requiring Logout/Refresh](#settings-requiring-logoutrefresh)
- [Settings Migration Breaking User Preferences](#settings-migration-breaking-user-preferences)
- [Permission Escalation Through Settings](#permission-escalation-through-settings)
- [Cached Settings Ignoring Updates](#cached-settings-ignoring-updates)
- [Org-Level Settings Overriding User Intent](#org-level-settings-overriding-user-intent)
- [Settings with No Undo](#settings-with-no-undo)
- [Time Zone Settings Applied Inconsistently](#time-zone-settings-applied-inconsistently)
- [Dark Mode Not Applied to All Components](#dark-mode-not-applied-to-all-components)
- [Settings Page Becoming a Dumping Ground](#settings-page-becoming-a-dumping-ground)
- [localStorage Settings Lost on Browser Change](#localstorage-settings-lost-on-browser-change)

## Settings Requiring Logout/Refresh

**Problem**: Users expect instant application of settings changes. Requiring a page refresh or logout/login breaks the user experience and feels like a bug.

**Why it happens**: Some settings affect server-side session state (like language/locale affecting i18n bundle loading) or require re-authentication (like password changes).

**Solution**: 
- Use CSS custom properties for theme/appearance changes (no refresh needed)
- For language changes, show a clear message: "Language change will take effect after page refresh" with a "Refresh Now" button
- For security-sensitive changes (password, MFA), require re-authentication but don't force logout

```typescript
// Bad: Silent failure, user doesn't know why theme didn't change
const changeLanguage = async (lang: string) => {
  await api.patch('/settings', { language: lang })
  // Theme doesn't apply until refresh, but no indication to user
}

// Good: Clear communication
const changeLanguage = async (lang: string) => {
  await api.patch('/settings', { language: lang })
  showNotification({
    message: 'Language will change after page refresh',
    action: {
      label: 'Refresh Now',
      onClick: () => window.location.reload()
    }
  })
}
```

## Settings Migration Breaking User Preferences

**Problem**: When settings schema evolves (fields renamed, removed, or restructured), existing user preferences can be lost or corrupted if migration logic is incomplete.

**Why it happens**: 
- Migration code doesn't handle all edge cases (null values, invalid values, missing fields)
- Migration runs incorrectly or not at all
- Backward compatibility not maintained

**Solution**:
- Always version your settings schema
- Test migration paths thoroughly with real user data samples
- Provide fallback values for missing or invalid data
- Make migrations idempotent (safe to run multiple times)

```kotlin
// Bad: Assumes field exists, crashes on old data
fun migrateV1ToV2(v1: SettingsV1): SettingsV2 {
    return SettingsV2(
        theme = v1.theme,  // Crashes if v1.theme is null
        density = "comfortable"  // New field
    )
}

// Good: Handles missing/invalid values gracefully
fun migrateV1ToV2(v1: SettingsV1): SettingsV2 {
    return SettingsV2(
        theme = v1.theme?.takeIf { it in VALID_THEMES } ?: "light",
        density = v1.density?.takeIf { it in VALID_DENSITIES } ?: "comfortable"
    )
}
```

## Permission Escalation Through Settings

**Problem**: Users can modify settings they shouldn't have access to, either through API calls, URL manipulation, or UI bugs.

**Why it happens**:
- Backend doesn't validate permissions on settings endpoints
- Frontend hides UI but doesn't prevent API calls
- Org-level settings can be modified by non-admins

**Solution**:
- Always validate permissions on the backend, never trust the frontend
- Use role-based access control (RBAC) or attribute-based access control (ABAC)
- Log all settings changes for audit trails
- Test permission boundaries thoroughly

```kotlin
// Bad: No permission check
@PatchMapping("/api/org/{orgId}/settings")
fun updateOrgSettings(
    @PathVariable orgId: UUID,
    @RequestBody updates: Map<String, Any>
): ResponseEntity<OrgSettings> {
    // Anyone can call this!
    orgSettingsService.update(orgId, updates)
    return ResponseEntity.ok(orgSettingsService.get(orgId))
}

// Good: Permission check on backend
@PatchMapping("/api/org/{orgId}/settings")
@PreAuthorize("hasRole('ORG_ADMIN') and hasPermission(#orgId, 'UPDATE_ORG_SETTINGS')")
fun updateOrgSettings(
    @PathVariable orgId: UUID,
    @RequestBody updates: Map<String, Any>,
    authentication: Authentication
): ResponseEntity<OrgSettings> {
    val userId = (authentication.principal as UserPrincipal).id
    
    // Verify user is admin of this org
    if (!orgService.isAdmin(userId, orgId)) {
        throw AccessDeniedException("Not authorized to update org settings")
    }
    
    orgSettingsService.update(orgId, updates, updatedBy = userId)
    auditLog.logSettingsChange(userId, orgId, updates)
    
    return ResponseEntity.ok(orgSettingsService.get(orgId))
}
```

## Cached Settings Ignoring Updates

**Problem**: Settings changes don't appear immediately because Redis cache isn't invalidated, or cache TTL is too long, or cache key doesn't match.

**Why it happens**:
- Cache invalidation logic is missing or incorrect
- Cache keys are inconsistent between read and write paths
- TTL is too long for frequently-changing settings

**Solution**:
- Always invalidate cache on settings updates
- Use consistent cache key patterns
- Consider shorter TTLs for frequently-changing settings
- Provide cache-busting mechanism for critical updates

```kotlin
// Bad: Updates database but doesn't invalidate cache
fun updateSettings(userId: UUID, updates: Map<String, Any>) {
    repository.update(userId, updates)
    // Cache still has old values!
}

// Good: Invalidate cache on update
fun updateSettings(userId: UUID, updates: Map<String, Any>) {
    repository.update(userId, updates)
    
    // Invalidate user cache
    redisTemplate.delete("settings:resolved:$userId")
    
    // If org settings changed, invalidate all users in org
    if (updates.containsKey("orgDefault")) {
        val orgId = userService.getOrgId(userId)
        redisTemplate.delete("settings:org:$orgId:*") // Pattern delete
    }
}
```

## Org-Level Settings Overriding User Intent

**Problem**: When org admins change org-wide defaults, users with custom settings might be affected unexpectedly, or users might not be notified of changes that affect them.

**Why it happens**:
- Org default changes apply to users without overrides, but users aren't notified
- Users think their custom setting is still active, but it was reset
- No clear indication that a setting is using org default vs user override

**Solution**:
- Clearly indicate when a setting is using org default vs user override
- Notify users when org defaults change (if it affects them)
- Preserve user overrides when org defaults change
- Provide "Reset to org default" option

```typescript
// Bad: User can't tell if setting is custom or inherited
<select value={theme}>
  <option value="light">Light</option>
  <option value="dark">Dark</option>
</select>

// Good: Clear indication of source
<select value={theme}>
  <option value="light">Light</option>
  <option value="dark">Dark</option>
</select>
{isOrgDefault && (
  <span className="badge">Org Default</span>
)}
{isUserOverride && (
  <button onClick={resetToOrgDefault}>Reset to Org Default</button>
)}
```

## Settings with No Undo

**Problem**: Users change a setting, realize it was wrong, but can't easily revert. Common with destructive actions or settings with no "previous value" tracking.

**Why it happens**:
- No undo mechanism
- No history of previous values
- Destructive actions (delete API key) are irreversible
- Settings page doesn't show what the value was before

**Solution**:
- Provide "Reset to default" for all settings
- Show recent changes/history for critical settings
- Require confirmation for irreversible actions
- Consider soft-delete for destructive actions (e.g., deactivate API key instead of delete)

```typescript
// Bad: No way to undo
const revokeApiKey = async (keyId: string) => {
  await api.delete(`/api/keys/${keyId}`)
  // Key is gone forever, no undo
}

// Good: Soft delete with reactivation option
const revokeApiKey = async (keyId: string) => {
  await api.patch(`/api/keys/${keyId}`, { status: 'revoked' })
  // Key can be reactivated within 30 days
  showNotification({
    message: 'API key revoked. You can reactivate it within 30 days.',
    action: {
      label: 'Undo',
      onClick: () => reactivateApiKey(keyId)
    }
  })
}
```

## Time Zone Settings Applied Inconsistently

**Problem**: Some dates/times use the user's timezone setting, others use UTC or server timezone, creating confusion about when events actually occurred.

**Why it happens**:
- Timezone setting stored but not consistently applied
- Some components use browser timezone, others use user setting
- Server-side rendering uses different timezone than client-side
- Date formatting utilities don't all respect user timezone

**Solution**:
- Store user timezone preference
- Always use user timezone for display (convert server UTC to user TZ)
- Use consistent date formatting utilities
- Show timezone indicator (e.g., "2:00 PM PST")

```typescript
// Bad: Inconsistent timezone usage
const formatDate = (date: Date) => {
  // Uses browser timezone, not user setting
  return date.toLocaleString()
}

// Good: Consistent timezone usage
const formatDate = (date: Date, userTimezone: string) => {
  return new Intl.DateTimeFormat('en-US', {
    timeZone: userTimezone,
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

// In component
const FormattedDate = ({ date }) => {
  const { timezone } = useUserSettings()
  return <span>{formatDate(date, timezone)}</span>
}
```

## Dark Mode Not Applied to All Components

**Problem**: Dark mode theme is partially applied—some components are dark, others remain light, creating a jarring experience.

**Why it happens**:
- CSS custom properties not used consistently
- Some components use hardcoded colors
- Third-party components don't respect theme
- Theme not propagated to iframes or shadow DOM

**Solution**:
- Use CSS custom properties for all colors
- Avoid hardcoded color values
- Test all components in both themes
- Provide theme override for third-party components

```css
/* Bad: Hardcoded colors */
.component {
  background-color: #ffffff; /* Always white */
  color: #000000; /* Always black */
}

/* Good: CSS custom properties */
.component {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

/* Theme definitions */
:root {
  --color-bg-primary: #ffffff;
  --color-text-primary: #000000;
}

[data-theme="dark"] {
  --color-bg-primary: #1a1a1a;
  --color-text-primary: #ffffff;
}
```

```typescript
// Also ensure JavaScript-applied styles use theme
const applyComponentStyle = (element: HTMLElement) => {
  // Bad: Hardcoded
  element.style.backgroundColor = '#ffffff'
  
  // Good: Use CSS variable
  element.style.backgroundColor = 'var(--color-bg-primary)'
}
```

## Settings Page Becoming a Dumping Ground

**Problem**: Every new feature adds settings to the settings page, making it overwhelming and hard to navigate. Settings page becomes a catch-all for configuration.

**Why it happens**:
- No clear product strategy for what belongs in settings
- Developers default to adding settings for every configurable option
- No review process for new settings
- Settings page is seen as "safe" place to put anything

**Solution**:
- Establish criteria: Settings should be user preferences, not feature toggles or configuration
- Use progressive disclosure: Hide advanced/rarely-used settings
- Consider separate pages: Account settings vs feature settings vs admin settings
- Regular audit: Remove unused settings, consolidate related settings

```typescript
// Bad: Everything goes in settings
const SettingsPage = () => {
  return (
    <div>
      <ThemeSettings />
      <NotificationSettings />
      <ApiKeySettings />
      <WebhookSettings />
      <IntegrationSettings />
      <FeatureToggleSettings /> {/* Should be admin-only */}
      <DatabaseSettings /> {/* Should not be user-facing */}
      <CacheSettings /> {/* Should not be user-facing */}
    </div>
  )
}

// Good: Organized, progressive disclosure
const SettingsPage = () => {
  return (
    <div>
      <Tabs>
        <Tab label="Appearance">
          <ThemeSettings />
          <LanguageSettings />
        </Tab>
        <Tab label="Notifications">
          <NotificationSettings />
        </Tab>
        <Tab label="Integrations">
          <ApiKeySettings />
          <WebhookSettings />
        </Tab>
        <Tab label="Advanced" collapsed>
          <IntegrationSettings />
        </Tab>
      </Tabs>
    </div>
  )
}
```

## localStorage Settings Lost on Browser Change

**Problem**: Settings stored in localStorage don't sync across devices or browsers. User configures settings on one device, switches to another, and settings are gone.

**Why it happens**:
- Settings stored only in localStorage (browser-specific)
- No server sync for "client-only" settings
- User expects settings to sync (like most modern apps)

**Solution**:
- Sync important settings to server, even if they're UI preferences
- Use localStorage only for truly transient state (sidebar collapsed, temporary UI state)
- Provide clear indication of what syncs vs what doesn't
- Consider "sync settings across devices" option

```typescript
// Bad: Theme only in localStorage
const useTheme = () => {
  const [theme, setTheme] = useState(
    () => localStorage.getItem('theme') || 'light'
  )
  
  const updateTheme = (newTheme: string) => {
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    // Lost if user switches devices/browsers
  }
  
  return { theme, updateTheme }
}

// Good: Sync to server
const useTheme = () => {
  const { data: settings } = useQuery(['appearance-settings'], 
    () => api.get('/settings/appearance')
  )
  
  const updateMutation = useMutation({
    mutationFn: (theme: string) => 
      api.patch('/settings/appearance', { theme }),
    onSuccess: () => {
      // Also update localStorage for instant application
      localStorage.setItem('theme', theme)
      applyTheme(theme)
    }
  })
  
  return {
    theme: settings?.theme || 'light',
    updateTheme: updateMutation.mutate
  }
}
```
