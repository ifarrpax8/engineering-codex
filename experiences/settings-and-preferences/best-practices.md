# Best Practices: Settings & Preferences

## Contents

- [Group Settings Logically](#group-settings-logically)
- [Show Current Value Clearly](#show-current-value-clearly)
- [Provide Sensible Defaults](#provide-sensible-defaults)
- [Instant Preview](#instant-preview)
- [Confirm Destructive Settings](#confirm-destructive-settings)
- [Search Within Settings](#search-within-settings)
- [Stack-Specific Patterns](#stack-specific-patterns)
- [Accessibility](#accessibility)

## Group Settings Logically

Group settings by domain and user mental model, not alphabetically. Users think in terms of "What do I want to change?" not "What letter does it start with?"

### Good Grouping Examples

**By Domain**:
- **Account**: Profile, password, security, MFA
- **Appearance**: Theme, language, density, accessibility
- **Notifications**: Channels, frequency, preferences
- **Privacy**: Data sharing, visibility, export
- **Integrations**: API keys, webhooks, connected services

**By User Journey**:
- **Getting Started**: Essential settings for new users
- **Customization**: Personalization options
- **Advanced**: Power-user configurations

### Implementation Example

```typescript
// Vue 3 example with logical grouping
const settingsSections = [
  {
    id: 'account',
    title: 'Account',
    icon: 'user',
    settings: ['profile', 'password', 'security', 'mfa']
  },
  {
    id: 'appearance',
    title: 'Appearance',
    icon: 'palette',
    settings: ['theme', 'language', 'density', 'accessibility']
  },
  {
    id: 'notifications',
    title: 'Notifications',
    icon: 'bell',
    settings: ['channels', 'frequency', 'preferences']
  }
]
```

### Avoid Alphabetical Grouping

Alphabetical grouping breaks related settings apart. "API Keys" and "Appearance" have nothing in common, but alphabetical sorting might place them next to each other.

## Show Current Value Clearly

Users shouldn't have to guess what's currently set. Display current values prominently and make it obvious when a value differs from the default.

### Visual Indicators

```typescript
// React example showing current value
const ThemeSetting = () => {
  const { theme, defaultTheme } = useAppearanceSettings()
  const isDefault = theme === defaultTheme
  
  return (
    <div className="setting-group">
      <label>Theme</label>
      <select value={theme} onChange={handleChange}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="system">System</option>
      </select>
      {!isDefault && (
        <span className="badge">Custom</span>
      )}
      <button onClick={resetToDefault}>Reset to Default</button>
    </div>
  )
}
```

### Show Applied vs Saved

For settings that apply instantly (like theme), show both the current applied value and whether unsaved changes exist:

```typescript
// Vue 3 example
const AppearanceSettings = () => {
  const savedTheme = ref('light')
  const currentTheme = ref('light')
  const hasUnsavedChanges = computed(() => 
    savedTheme.value !== currentTheme.value
  )
  
  const applyTheme = (theme: string) => {
    currentTheme.value = theme
    applyThemeToDOM(theme) // Instant application
  }
  
  const save = async () => {
    await api.patch('/settings/appearance', { theme: currentTheme.value })
    savedTheme.value = currentTheme.value
  }
  
  return {
    currentTheme,
    hasUnsavedChanges,
    applyTheme,
    save
  }
}
```

## Provide Sensible Defaults

The application should work well without any settings changes. Defaults should reflect the most common use case, not the most permissive or restrictive configuration.

### Default Selection Criteria

1. **Most common use case**: Research user behavior, analytics, support tickets
2. **Safest option**: When in doubt, choose the option that prevents errors
3. **Accessibility**: Defaults should be accessible (e.g., sufficient contrast)
4. **Performance**: Defaults shouldn't impact performance negatively

### Example: Notification Defaults

```kotlin
// Spring Boot: Sensible notification defaults
data class NotificationDefaults(
    // Most users want email notifications
    val emailEnabled: Boolean = true,
    
    // But not too frequent - prevent notification fatigue
    val digestFrequency: DigestFrequency = DigestFrequency.REALTIME,
    
    // Security alerts should always be on
    val securityAlertsEnabled: Boolean = true,
    
    // Marketing emails opt-in by default (compliance)
    val marketingEmailsEnabled: Boolean = false
)
```

### Reset to Defaults

Always provide a way to reset to defaults:

```typescript
// React example
const SettingsSection = ({ sectionId, onReset }) => {
  const handleReset = () => {
    if (confirm('Reset all settings in this section to defaults?')) {
      onReset(sectionId)
    }
  }
  
  return (
    <div>
      <h2>Appearance Settings</h2>
      {/* Settings */}
      <button onClick={handleReset}>Reset to Defaults</button>
    </div>
  )
}
```

## Instant Preview

Theme, layout, and appearance changes should preview immediately, not after clicking "Save". Users expect instant feedback for visual changes.

### CSS Custom Properties for Theme

```css
/* Define theme variables */
:root {
  --color-bg-primary: #ffffff;
  --color-text-primary: #000000;
  --color-accent: #0066cc;
}

[data-theme="dark"] {
  --color-bg-primary: #1a1a1a;
  --color-text-primary: #ffffff;
  --color-accent: #4a9eff;
}

/* Use variables throughout */
.component {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  transition: background-color 0.2s, color 0.2s;
}
```

```typescript
// Vue 3: Apply theme instantly
const applyTheme = (theme: string) => {
  const root = document.documentElement
  
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    root.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
  } else {
    root.setAttribute('data-theme', theme)
  }
}

// Watch for changes and apply immediately
watch(() => settings.theme, (newTheme) => {
  applyTheme(newTheme)
  // Save in background (don't wait for user to click Save)
  debouncedSave({ theme: newTheme })
}, { immediate: true })
```

### Layout Density Preview

```typescript
// React: Instant density preview
const DensitySetting = () => {
  const { density, setDensity } = useAppearanceSettings()
  
  const handleChange = (newDensity: string) => {
    // Apply immediately
    document.documentElement.setAttribute('data-density', newDensity)
    setDensity(newDensity)
    // Save in background
    saveSettings({ density: newDensity })
  }
  
  return (
    <div>
      <label>Layout Density</label>
      <div className="density-preview">
        <button 
          className={density === 'compact' ? 'active' : ''}
          onClick={() => handleChange('compact')}
        >
          Compact
        </button>
        <button 
          className={density === 'comfortable' ? 'active' : ''}
          onClick={() => handleChange('comfortable')}
        >
          Comfortable
        </button>
        <button 
          className={density === 'spacious' ? 'active' : ''}
          onClick={() => handleChange('spacious')}
        >
          Spacious
        </button>
      </div>
    </div>
  )
}
```

## Confirm Destructive Settings

Settings that have irreversible consequences or affect security require confirmation dialogs.

### Destructive Actions Requiring Confirmation

- **Delete account**: Permanent data loss
- **Revoke API key**: Breaks integrations immediately
- **Change org-wide defaults**: Affects all users
- **Disable MFA**: Reduces security
- **Export/Delete data**: GDPR/CCPA compliance

### Confirmation Dialog Pattern

```typescript
// Vue 3 example
const DeleteAccountSetting = () => {
  const showConfirm = ref(false)
  
  const handleDelete = async () => {
    showConfirm.value = true
  }
  
  const confirmDelete = async () => {
    // Require password confirmation for extra security
    const password = prompt('Enter your password to confirm:')
    if (!password) return
    
    try {
      await api.post('/account/delete', { password })
      // Redirect to goodbye page
      router.push('/goodbye')
    } catch (error) {
      showError('Invalid password')
    }
  }
  
  return {
    showConfirm,
    handleDelete,
    confirmDelete
  }
}
```

```tsx
// React example with modal
const RevokeApiKeyButton = ({ keyId }) => {
  const [showConfirm, setShowConfirm] = useState(false)
  const revokeMutation = useMutation({
    mutationFn: () => api.delete(`/api/keys/${keyId}`),
    onSuccess: () => {
      toast.success('API key revoked')
      queryClient.invalidateQueries(['api-keys'])
    }
  })
  
  return (
    <>
      <button onClick={() => setShowConfirm(true)}>Revoke</button>
      
      {showConfirm && (
        <ConfirmDialog
          title="Revoke API Key?"
          message="This will immediately invalidate this key. Any integrations using this key will stop working."
          confirmLabel="Revoke"
          onConfirm={() => {
            revokeMutation.mutate()
            setShowConfirm(false)
          }}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  )
}
```

## Search Within Settings

For applications with many settings (50+), provide search functionality to help users find what they're looking for.

### Search Implementation

```typescript
// Vue 3: Settings search
const useSettingsSearch = (sections: SettingsSection[]) => {
  const searchQuery = ref('')
  
  const filteredSections = computed(() => {
    if (!searchQuery.value) return sections
    
    const query = searchQuery.value.toLowerCase()
    return sections.map(section => ({
      ...section,
      settings: section.settings.filter(setting => 
        setting.label.toLowerCase().includes(query) ||
        setting.description?.toLowerCase().includes(query) ||
        setting.keywords?.some(kw => kw.toLowerCase().includes(query))
      )
    })).filter(section => section.settings.length > 0)
  })
  
  return {
    searchQuery,
    filteredSections
  }
}
```

```tsx
// React: Settings search with highlighting
const SettingsSearch = ({ sections, onSearch }) => {
  const [query, setQuery] = useState('')
  
  useEffect(() => {
    const filtered = filterSections(sections, query)
    onSearch(filtered)
  }, [query, sections, onSearch])
  
  return (
    <div className="settings-search">
      <input
        type="search"
        placeholder="Search settings..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search settings"
      />
      {query && (
        <button onClick={() => setQuery('')}>Clear</button>
      )}
    </div>
  )
}
```

## Stack-Specific Patterns

### Vue 3

**Pinia Store for Client Settings**:

```typescript
// stores/settings.ts
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref(localStorage.getItem('theme') || 'system')
  const density = ref(localStorage.getItem('density') || 'comfortable')
  
  // Watch for changes and apply immediately
  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
  })
  
  watch(density, (newDensity) => {
    localStorage.setItem('density', newDensity)
    document.documentElement.setAttribute('data-density', newDensity)
  })
  
  // Sync with server
  const syncWithServer = async () => {
    await api.patch('/settings/appearance', {
      theme: theme.value,
      density: density.value
    })
  }
  
  return {
    theme,
    density,
    syncWithServer
  }
})
```

**usePreferredColorScheme**:

```typescript
import { usePreferredColorScheme } from '@vueuse/core'

const preferredScheme = usePreferredColorScheme()

watch([theme, preferredScheme], ([theme, scheme]) => {
  if (theme === 'system') {
    applyTheme(scheme === 'dark' ? 'dark' : 'light')
  }
})
```

### React

**Context Provider for Theme**:

```tsx
const ThemeContext = createContext<{
  theme: string
  setTheme: (theme: string) => void
}>({
  theme: 'light',
  setTheme: () => {}
})

export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(() => 
    localStorage.getItem('theme') || 'light'
  )
  
  const setTheme = (newTheme: string) => {
    setThemeState(newTheme)
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
  }
  
  useEffect(() => {
    applyTheme(theme)
  }, [theme])
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

**useMediaQuery for System Preference**:

```tsx
const useSystemTheme = () => {
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)')
  return prefersDark ? 'dark' : 'light'
}

const ThemeSetting = () => {
  const { theme, setTheme } = useTheme()
  const systemTheme = useSystemTheme()
  
  const effectiveTheme = theme === 'system' ? systemTheme : theme
  
  return (
    <select value={theme} onChange={(e) => setTheme(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="system">System ({systemTheme})</option>
    </select>
  )
}
```

### Spring Boot

**@ConfigurationProperties**:

```kotlin
@ConfigurationProperties(prefix = "app.settings")
data class ApplicationSettings(
    val defaultTheme: String = "light",
    val defaultLanguage: String = "en",
    val maxApiKeysPerUser: Int = 10
)

@Configuration
@EnableConfigurationProperties(ApplicationSettings::class)
class SettingsConfiguration
```

**Custom UserPreferenceService**:

```kotlin
@Service
class UserPreferenceService(
    private val repository: UserSettingsRepository,
    private val orgSettingsService: OrgSettingsService
) {
    fun getResolvedSettings(userId: UUID): ResolvedSettings {
        val userSettings = repository.getUserSettings(userId)
        val orgSettings = orgSettingsService.getOrgSettings(getUserOrgId(userId))
        
        return ResolvedSettings(
            theme = userSettings.theme ?: orgSettings.defaultTheme ?: "light",
            language = userSettings.language ?: orgSettings.defaultLanguage ?: "en"
        )
    }
    
    fun updateSetting(userId: UUID, category: String, key: String, value: Any) {
        repository.updateSetting(userId, category, key, value)
        cache.invalidate("settings:$userId")
    }
}
```

**Jackson @JsonMerge for Partial Updates**:

```kotlin
data class AppearanceSettings(
    @JsonMerge
    val theme: String? = null,
    @JsonMerge
    val density: String? = null,
    @JsonMerge
    val language: String? = null
)

@PatchMapping("/api/settings/appearance")
fun updateAppearance(
    @RequestBody @JsonMerge updates: AppearanceSettings,
    authentication: Authentication
): ResponseEntity<AppearanceSettings> {
    val userId = (authentication.principal as UserPrincipal).id
    val current = settingsService.getAppearanceSettings(userId)
    val merged = objectMapper.updateValue(current, updates)
    val saved = settingsService.saveAppearanceSettings(userId, merged)
    return ResponseEntity.ok(saved)
}
```

## Accessibility

Settings pages must be keyboard navigable, screen reader friendly, and support assistive technologies.

### Keyboard Navigation

```typescript
// All interactive elements must be keyboard accessible
const SettingToggle = ({ label, value, onChange }) => {
  return (
    <div className="setting-row">
      <label htmlFor="toggle-1">{label}</label>
      <button
        id="toggle-1"
        role="switch"
        aria-checked={value}
        onClick={() => onChange(!value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onChange(!value)
          }
        }}
      >
        {value ? 'On' : 'Off'}
      </button>
    </div>
  )
}
```

### Toggle Switch Labels

```tsx
// Proper labeling for toggle switches
<fieldset>
  <legend>Notification Preferences</legend>
  
  <div className="setting-row">
    <label htmlFor="email-notifications">
      Email Notifications
      <span className="sr-only">Toggle email notifications</span>
    </label>
    <input
      type="checkbox"
      id="email-notifications"
      checked={emailEnabled}
      onChange={(e) => setEmailEnabled(e.target.checked)}
      aria-describedby="email-notifications-desc"
    />
    <span id="email-notifications-desc" className="sr-only">
      Receive notifications via email
    </span>
  </div>
</fieldset>
```

### Color Theme Contrast Indicators

```tsx
// Show contrast ratio for accessibility
const ThemePreview = ({ theme }) => {
  const contrastRatio = calculateContrast(theme.bg, theme.text)
  const meetsWCAG = contrastRatio >= 4.5 // WCAG AA standard
  
  return (
    <div 
      className="theme-preview"
      style={{ 
        backgroundColor: theme.bg, 
        color: theme.text 
      }}
    >
      <p>Sample text</p>
      <div className="contrast-indicator">
        Contrast: {contrastRatio.toFixed(2)}:1
        {meetsWCAG ? (
          <span className="badge success">WCAG AA</span>
        ) : (
          <span className="badge warning">Low Contrast</span>
        )}
      </div>
    </div>
  )
}
```

### Screen Reader Announcements

```tsx
// Announce settings changes to screen readers
const useSettingsAnnouncement = () => {
  const [announcement, setAnnouncement] = useState('')
  
  const announce = (message: string) => {
    setAnnouncement(message)
    // Clear after screen reader has time to read it
    setTimeout(() => setAnnouncement(''), 1000)
  }
  
  return {
    announcement,
    announce
  }
}

// Usage
const { announcement, announce } = useSettingsAnnouncement()

const handleThemeChange = (newTheme: string) => {
  setTheme(newTheme)
  announce(`Theme changed to ${newTheme}`)
}

return (
  <>
    <div role="status" aria-live="polite" className="sr-only">
      {announcement}
    </div>
    {/* Settings UI */}
  </>
)
```
