---
recommendation_type: decision-matrix
---

# Settings & Preferences — Options

## Contents

- [Settings Storage](#settings-storage)
- [Settings UI Patterns](#settings-ui-patterns)
- [Theme/Appearance Systems](#themeappearance-systems)
- [Notification Preference Models](#notification-preference-models)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Settings Storage

### Database-Backed (PostgreSQL)

**Description:** Store user settings and preferences in a PostgreSQL database. Settings are persisted server-side and can be queried, analyzed, and synchronized across devices.

**Strengths:**
- Persistent across devices and sessions
- Queryable and analyzable (e.g., "how many users use dark mode?")
- Supports complex hierarchies and relationships
- Can be versioned and audited
- Supports multi-user scenarios (team settings, shared preferences)
- Can be backed up and restored
- Supports transactions and consistency guarantees
- Can be accessed from any client (web, mobile, API)

**Weaknesses:**
- Requires server round-trip (latency)
- More complex to implement (API endpoints, database schema)
- Requires authentication/authorization
- Can be slower than client-side storage
- Requires database migrations for schema changes
- May require caching for performance

**Best For:**
- Critical user preferences (theme, language, timezone)
- Settings that need to sync across devices
- Team or organization-level settings
- Settings requiring audit trails
- Settings that need to be queryable/analyzable
- Settings with complex relationships
- Enterprise applications

**Avoid When:**
- UI-only preferences (sidebar collapsed state)
- Temporary preferences (last viewed tab)
- Performance-critical settings (should be instant)
- Settings that don't need persistence
- Offline-first applications

**Code Example:**
```typescript
// Backend: Settings API
@RestController
@RequestMapping("/api/settings")
class SettingsController {
  @GetMapping
  fun getUserSettings(): Settings {
    return settingsService.getUserSettings(getCurrentUser())
  }
  
  @PutMapping
  fun updateSettings(@RequestBody settings: Settings) {
    settingsService.updateUserSettings(getCurrentUser(), settings)
  }
}

// Frontend: Settings service
class SettingsService {
  async getUserSettings(): Promise<UserSettings> {
    const response = await fetch('/api/settings');
    return response.json();
  }
  
  async updateSettings(settings: Partial<UserSettings>): Promise<void> {
    await fetch('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
}
```

### localStorage/sessionStorage

**Description:** Store settings in browser localStorage (persistent) or sessionStorage (session-only). Settings are client-only and don't require server round-trips.

**Strengths:**
- Instant access (no server round-trip)
- Works offline
- Simple to implement (browser API)
- No server infrastructure required
- Good for UI preferences
- Can be very fast (synchronous access)

**Weaknesses:**
- Not synchronized across devices
- Limited storage (~5-10MB)
- Can be cleared by user
- Not queryable/analyzable
- No versioning or audit trail
- Browser-specific (different behavior across browsers)
- Not accessible from server-side rendering
- Security concerns (XSS can access localStorage)

**Best For:**
- UI preferences (sidebar collapsed, table column widths)
- Temporary preferences (last viewed tab, scroll position)
- Client-only settings (theme preference, font size)
- Settings that don't need persistence
- Performance-critical settings (should be instant)
- Offline-first applications
- Settings that are device-specific

**Avoid When:**
- Settings that need to sync across devices
- Critical user preferences (should be in database)
- Settings requiring audit trails
- Settings that need to be queryable
- Team or organization-level settings
- Settings with security implications

**Code Example:**
```typescript
// Frontend: localStorage settings
class LocalStorageSettings {
  private readonly key = 'user-settings';
  
  getSettings(): UserSettings {
    const stored = localStorage.getItem(this.key);
    return stored ? JSON.parse(stored) : this.getDefaults();
  }
  
  updateSettings(settings: Partial<UserSettings>): void {
    const current = this.getSettings();
    const updated = { ...current, ...settings };
    localStorage.setItem(this.key, JSON.stringify(updated));
  }
  
  private getDefaults(): UserSettings {
    return {
      theme: 'light',
      sidebarCollapsed: false,
      tablePageSize: 25
    };
  }
}
```

### Hybrid

**Description:** Store important settings in database, UI preferences in localStorage. Combines persistence of critical settings with performance of client-side storage.

**Strengths:**
- Best of both worlds: persistence + performance
- Critical settings sync across devices
- UI preferences are instant
- Reduces server load (fewer API calls)
- Flexible approach (can optimize per setting type)
- Good user experience (fast UI, persistent data)

**Weaknesses:**
- More complex to implement (two storage systems)
- Requires clear categorization (what goes where?)
- Potential for inconsistency (settings in two places)
- Requires synchronization logic
- More code to maintain

**Best For:**
- Applications with both critical and UI preferences
- Applications requiring fast UI but persistent data
- Applications with many settings (categorize by importance)
- Applications balancing performance and persistence
- Enterprise applications with diverse setting types
- Applications where some settings are device-specific

**Avoid When:**
- Simple applications (one storage method sufficient)
- Applications with only critical settings (use database)
- Applications with only UI preferences (use localStorage)
- Applications preferring simplicity over optimization

**Code Example:**
```typescript
// Frontend: Hybrid settings service
class HybridSettingsService {
  private dbSettings: DatabaseSettings;
  private localSettings: LocalStorageSettings;
  
  // Critical settings (database)
  async getTheme(): Promise<Theme> {
    return this.dbSettings.get('theme');
  }
  
  async updateTheme(theme: Theme): Promise<void> {
    await this.dbSettings.update('theme', theme);
  }
  
  // UI preferences (localStorage)
  getSidebarCollapsed(): boolean {
    return this.localSettings.get('sidebarCollapsed');
  }
  
  updateSidebarCollapsed(collapsed: boolean): void {
    this.localSettings.update('sidebarCollapsed', collapsed);
  }
  
  // Initialize: load DB settings, merge with local
  async initialize(): Promise<UserSettings> {
    const db = await this.dbSettings.getAll();
    const local = this.localSettings.getAll();
    return { ...db, ...local };
  }
}
```

## Settings UI Patterns

### Single Page

**Description:** All settings visible on one scrollable page. No navigation between sections, everything accessible by scrolling.

**Strengths:**
- Simple to implement (single route/component)
- All settings visible at once (no hidden sections)
- Easy to search (browser find works)
- Good for small number of settings (<20)
- Familiar pattern (like mobile settings)
- No navigation overhead

**Weaknesses:**
- Becomes unwieldy with many settings
- Hard to organize large number of settings
- Long scroll can be overwhelming
- Difficult to find specific settings
- Poor for hierarchical settings
- Not scalable

**Best For:**
- Applications with <20 settings
- Simple applications
- Mobile applications (familiar pattern)
- Applications where all settings are equally important
- Applications preferring simplicity
- Applications with flat setting structure

**Avoid When:**
- Applications with many settings (>20)
- Applications with hierarchical settings
- Applications requiring settings organization
- Enterprise applications with complex settings
- Applications where settings have different importance levels

**Code Example:**
```tsx
// React: Single page settings
function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings>();
  
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <section>
        <h2>Appearance</h2>
        <ThemeSelector value={settings.theme} onChange={updateTheme} />
        <FontSizeSelector value={settings.fontSize} onChange={updateFontSize} />
      </section>
      
      <section>
        <h2>Notifications</h2>
        <NotificationToggle value={settings.emailNotifications} onChange={updateEmail} />
        <NotificationToggle value={settings.pushNotifications} onChange={updatePush} />
      </section>
      
      <section>
        <h2>Privacy</h2>
        <PrivacyToggle value={settings.shareAnalytics} onChange={updateAnalytics} />
      </section>
    </div>
  );
}
```

### Tabbed/Sectioned

**Description:** Settings grouped by category with tab navigation. Each tab shows a category of related settings.

**Strengths:**
- Organizes settings into logical groups
- Easy to navigate between categories
- Scalable (can add more tabs)
- Good for medium number of settings (20-50)
- Familiar pattern (desktop applications)
- Reduces cognitive load (one category at a time)

**Weaknesses:**
- Requires navigation (tabs)
- Some settings may not fit categories
- Can be overwhelming with many tabs (>7)
- Requires clear categorization
- May hide related settings in different tabs

**Best For:**
- Applications with 20-50 settings
- Applications with clear setting categories
- Desktop applications
- Applications requiring settings organization
- Applications with medium complexity
- Applications where categories are distinct

**Avoid When:**
- Applications with <10 settings (overhead not worth it)
- Applications with >50 settings (consider sidebar nav)
- Applications with unclear categories
- Applications preferring simplicity
- Mobile applications (tabs less common)

**Code Example:**
```tsx
// React: Tabbed settings
function SettingsPage() {
  const [activeTab, setActiveTab] = useState('appearance');
  
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="appearance" label="Appearance" />
        <Tab value="notifications" label="Notifications" />
        <Tab value="privacy" label="Privacy" />
        <Tab value="account" label="Account" />
      </Tabs>
      
      <TabPanel value={activeTab} tab="appearance">
        <ThemeSelector />
        <FontSizeSelector />
      </TabPanel>
      
      <TabPanel value={activeTab} tab="notifications">
        <EmailNotifications />
        <PushNotifications />
      </TabPanel>
      
      {/* Other tabs */}
    </div>
  );
}
```

### Sidebar Navigation

**Description:** Settings as a mini-app with its own sidebar navigation. Left sidebar shows categories, main area shows settings for selected category.

**Strengths:**
- Excellent for many settings (>50)
- Clear hierarchy and organization
- Scalable (can nest categories)
- Good for complex settings structures
- Familiar pattern (like admin panels)
- Can show sub-categories
- Persistent navigation (always visible)

**Weaknesses:**
- More complex to implement
- Consumes horizontal space
- May be overkill for simple settings
- Requires careful information architecture
- Can be overwhelming for simple applications

**Best For:**
- Applications with >50 settings
- Enterprise applications with complex settings
- Applications with hierarchical settings
- Applications requiring deep organization
- Admin panels and configuration interfaces
- Applications with many setting categories

**Avoid When:**
- Applications with <20 settings
- Simple applications
- Mobile applications (use tabs or single page)
- Applications preferring simplicity
- Applications with flat setting structure

**Code Example:**
```tsx
// React: Sidebar navigation settings
function SettingsPage() {
  const [selectedCategory, setSelectedCategory] = useState('appearance');
  
  return (
    <div className="settings-page">
      <h1>Settings</h1>
      
      <div className="settings-layout">
        <Sidebar>
          <NavItem active={selectedCategory === 'appearance'} onClick={() => setSelectedCategory('appearance')}>
            Appearance
          </NavItem>
          <NavItem active={selectedCategory === 'notifications'} onClick={() => setSelectedCategory('notifications')}>
            Notifications
            <SubNavItem onClick={() => setSelectedCategory('notifications.email')}>
              Email
            </SubNavItem>
            <SubNavItem onClick={() => setSelectedCategory('notifications.push')}>
              Push
            </SubNavItem>
          </NavItem>
          <NavItem active={selectedCategory === 'privacy'} onClick={() => setSelectedCategory('privacy')}>
            Privacy
          </NavItem>
        </Sidebar>
        
        <MainContent>
          {selectedCategory === 'appearance' && <AppearanceSettings />}
          {selectedCategory === 'notifications.email' && <EmailNotificationSettings />}
          {/* Other categories */}
        </MainContent>
      </div>
    </div>
  );
}
```

## Theme/Appearance Systems

### CSS Custom Properties (Runtime)

**Description:** Use CSS custom properties (CSS variables) to toggle themes at runtime. Theme values are stored in CSS variables and swapped by changing variable values.

**Strengths:**
- Runtime theme switching (no page reload)
- Simple to implement (CSS only)
- Good performance (browser-native)
- Works with any CSS framework
- Can have multiple themes
- Easy to override per-component
- Supports smooth transitions

**Weaknesses:**
- Requires CSS custom property support (modern browsers)
- Less type-safe (no TypeScript checking)
- Can be harder to debug
- Requires careful variable naming
- May not work well with some CSS-in-JS solutions

**Best For:**
- Applications requiring runtime theme switching
- Applications using plain CSS or CSS modules
- Applications preferring CSS-based solutions
- Applications with multiple themes
- Applications needing smooth theme transitions
- Applications using Tailwind CSS (works well)

**Avoid When:**
- Applications requiring type-safe theme access
- Applications using CSS-in-JS that doesn't support custom properties
- Applications preferring JavaScript-based theme management
- Applications with very simple theming needs

**Code Example:**
```css
/* CSS: Theme variables */
:root {
  --color-primary: #007bff;
  --color-background: #ffffff;
  --color-text: #000000;
}

[data-theme="dark"] {
  --color-primary: #0d6efd;
  --color-background: #1a1a1a;
  --color-text: #ffffff;
}

.button {
  background-color: var(--color-primary);
  color: var(--color-text);
}
```

```typescript
// TypeScript: Theme toggle
function toggleTheme(theme: 'light' | 'dark') {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}
```

### Tailwind Dark Mode

**Description:** Use Tailwind CSS dark mode feature. Themes are toggled via classes (`dark:` variant) or media query preference.

**Strengths:**
- Integrated with Tailwind CSS
- Simple class-based approach
- Supports media query (system preference)
- Good developer experience
- Type-safe with TypeScript
- Works well with utility classes
- Can combine with custom properties

**Weaknesses:**
- Tailwind-specific (not framework-agnostic)
- Requires Tailwind CSS setup
- Class-based (can be verbose)
- May require configuration
- Less flexible than custom properties alone

**Best For:**
- Applications using Tailwind CSS
- Applications preferring utility classes
- Applications with light/dark themes
- Applications following system preference
- Applications using Tailwind design system
- Applications requiring Tailwind integration

**Avoid When:**
- Applications not using Tailwind CSS
- Applications requiring many themes (>2)
- Applications preferring CSS-only solutions
- Applications with complex theming needs

**Code Example:**
```tsx
// React: Tailwind dark mode
function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <div className="bg-white dark:bg-gray-900 text-black dark:text-white">
        <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          Toggle Theme
        </button>
      </div>
    </div>
  );
}
```

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media' for system preference
  // ...
}
```

### Design System Theme Provider

**Description:** Use design system theme provider (Propulsion or MUI) that wraps the application. Theme is managed by the design system's theme context.

**Strengths:**
- Integrated with design system
- Type-safe theme access
- Consistent with design system patterns
- Good developer experience
- Supports theme customization
- Works with design system components
- Can extend design system themes

**Weaknesses:**
- Design system-specific (Propulsion or MUI)
- Requires design system adoption
- Less flexible than custom solutions
- May require design system updates
- Can be overkill for simple theming

**Best For:**
- Applications using Propulsion or MUI
- Applications requiring design system consistency
- Applications with complex theme needs
- Applications using design system components
- Enterprise applications with design system
- Applications requiring theme customization

**Avoid When:**
- Applications not using design system
- Applications with simple theming needs
- Applications preferring framework-agnostic solutions
- Applications requiring many custom themes

**Code Example:**
```tsx
// React: MUI Theme Provider
import { ThemeProvider, createTheme } from '@mui/material';

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' }
  }
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' }
  }
});

function App() {
  const [theme, setTheme] = useState(lightTheme);
  
  return (
    <ThemeProvider theme={theme}>
      <AppContent onThemeChange={setTheme} />
    </ThemeProvider>
  );
}
```

```tsx
// React: Propulsion Theme Provider
import { PropulsionThemeProvider } from '@pax8/propulsion';

function App() {
  const [theme, setTheme] = useState('light');
  
  return (
    <PropulsionThemeProvider theme={theme}>
      <AppContent onThemeChange={setTheme} />
    </PropulsionThemeProvider>
  );
}
```

## Notification Preference Models

### Global Opt-In/Opt-Out

**Description:** Single toggle per notification channel (email, push, SMS). User can enable or disable entire channels.

**Strengths:**
- Simple to understand and implement
- Quick to configure (few toggles)
- Good for users who want all or nothing
- Easy to maintain (simple data model)
- Clear user experience

**Weaknesses:**
- Less granular control
- Can't enable some notifications but not others
- May not meet all user needs
- Less flexible

**Best For:**
- Applications with simple notification needs
- Applications with few notification types
- Applications where users prefer simplicity
- Applications with clear channel boundaries
- Consumer applications
- Applications preferring ease of use

**Avoid When:**
- Applications with many notification types
- Applications requiring granular control
- Enterprise applications with complex notifications
- Applications where users need fine-grained control
- Applications with diverse notification categories

**Code Example:**
```tsx
// React: Global opt-in/opt-out
function NotificationSettings() {
  const [preferences, setPreferences] = useState({
    emailEnabled: true,
    pushEnabled: false,
    smsEnabled: false
  });
  
  return (
    <div>
      <Toggle
        label="Email Notifications"
        value={preferences.emailEnabled}
        onChange={(enabled) => setPreferences({ ...preferences, emailEnabled: enabled })}
      />
      <Toggle
        label="Push Notifications"
        value={preferences.pushEnabled}
        onChange={(enabled) => setPreferences({ ...preferences, pushEnabled: enabled })}
      />
      <Toggle
        label="SMS Notifications"
        value={preferences.smsEnabled}
        onChange={(enabled) => setPreferences({ ...preferences, smsEnabled: enabled })}
      />
    </div>
  );
}
```

### Per-Channel Preferences

**Description:** Granular control per notification channel. Each channel can have different preferences (e.g., email for orders but not marketing).

**Strengths:**
- More granular than global toggle
- Good balance of control and simplicity
- Can enable some notifications but not others
- Better user experience for diverse needs
- More flexible than global toggle

**Weaknesses:**
- More complex than global toggle
- Requires more UI (per-channel settings)
- Can be overwhelming with many channels
- More data to manage

**Best For:**
- Applications with multiple notification categories per channel
- Applications where channels have distinct purposes
- Applications requiring moderate granularity
- Applications with 3-5 channels
- Applications balancing control and simplicity

**Avoid When:**
- Applications with simple notification needs (use global toggle)
- Applications with many channels (>5, consider matrix)
- Applications preferring maximum simplicity
- Applications with only one notification type per channel

**Code Example:**
```tsx
// React: Per-channel preferences
function NotificationSettings() {
  const [preferences, setPreferences] = useState({
    email: {
      orders: true,
      marketing: false,
      security: true
    },
    push: {
      orders: true,
      marketing: false,
      security: true
    }
  });
  
  return (
    <div>
      <section>
        <h3>Email Notifications</h3>
        <Toggle label="Order Updates" value={preferences.email.orders} />
        <Toggle label="Marketing" value={preferences.email.marketing} />
        <Toggle label="Security Alerts" value={preferences.email.security} />
      </section>
      
      <section>
        <h3>Push Notifications</h3>
        <Toggle label="Order Updates" value={preferences.push.orders} />
        <Toggle label="Marketing" value={preferences.push.marketing} />
        <Toggle label="Security Alerts" value={preferences.push.security} />
      </section>
    </div>
  );
}
```

### Per-Notification-Type Matrix

**Description:** Full control matrix: channel × notification type. User can configure each combination independently.

**Strengths:**
- Maximum granularity and control
- Handles complex notification needs
- Flexible for any use case
- Good for power users
- Can handle any notification structure

**Weaknesses:**
- Most complex to implement and use
- Can be overwhelming for users
- Requires more UI (matrix table)
- More data to manage and store
- May be overkill for simple needs

**Best For:**
- Enterprise applications with complex notifications
- Applications with many notification types and channels
- Applications requiring maximum control
- Applications with power users
- Applications with diverse notification needs
- Applications where granularity is critical

**Avoid When:**
- Applications with simple notification needs
- Applications preferring simplicity
- Consumer applications (may be too complex)
- Applications with few notification types
- Applications where users prefer simplicity

**Code Example:**
```tsx
// React: Notification matrix
function NotificationSettings() {
  const channels = ['email', 'push', 'sms'];
  const types = ['order_updates', 'marketing', 'security', 'system'];
  
  const [matrix, setMatrix] = useState(() => {
    const m = {};
    channels.forEach(channel => {
      m[channel] = {};
      types.forEach(type => {
        m[channel][type] = false;
      });
    });
    return m;
  });
  
  return (
    <table>
      <thead>
        <tr>
          <th>Notification Type</th>
          {channels.map(channel => <th key={channel}>{channel}</th>)}
        </tr>
      </thead>
      <tbody>
        {types.map(type => (
          <tr key={type}>
            <td>{formatType(type)}</td>
            {channels.map(channel => (
              <td key={channel}>
                <Toggle
                  value={matrix[channel][type]}
                  onChange={(enabled) => {
                    setMatrix({
                      ...matrix,
                      [channel]: { ...matrix[channel], [type]: enabled }
                    });
                  }}
                />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Recommendation Guidance

### Default Recommendations

**Settings Storage:**
- **Default:** Hybrid approach (critical settings in database, UI preferences in localStorage)
- **Simple Apps:** localStorage for all settings
- **Enterprise Apps:** Database for all settings requiring sync/audit

**Settings UI:**
- **Default:** Tabbed/sectioned for 20-50 settings
- **Simple Apps:** Single page for <20 settings
- **Complex Apps:** Sidebar navigation for >50 settings

**Theme System:**
- **Vue/React with Tailwind:** Tailwind dark mode
- **Propulsion/MUI Apps:** Design system theme provider
- **Custom CSS:** CSS custom properties
- **Default:** Tailwind dark mode (if using Tailwind)

**Notification Preferences:**
- **Default:** Per-channel preferences (balance of control and simplicity)
- **Simple Apps:** Global opt-in/opt-out
- **Enterprise Apps:** Per-notification-type matrix

### When to Deviate

- **Offline-First:** Prefer localStorage for all settings
- **Multi-Device Sync:** Use database for all settings
- **Many Settings:** Use sidebar navigation even with <50 settings
- **Simple Theming:** CSS custom properties sufficient
- **Power Users:** Use notification matrix even if complex

## Synergies

### Notifications

Settings storage and notification preferences interact:
- **Notification Preferences:** Should be stored in database (sync across devices)
- **Notification Settings UI:** Can use same pattern as other settings
- **Real-Time Updates:** Notification preferences may need real-time updates

### Design Consistency

Settings UI patterns affect design consistency:
- **Design System:** Use design system components for settings UI
- **Theme System:** Integrates with design system theme provider
- **Consistent Patterns:** Settings should follow same patterns as rest of app

### Configuration Management

Settings relate to configuration management:
- **Feature Toggles:** Some settings may be feature toggles
- **Environment Config:** Some settings may be environment-specific
- **Admin Overrides:** Some settings may have admin overrides

### Feature Toggles

Settings may include feature toggles:
- **User Preferences:** Users can enable/disable features
- **Beta Features:** Settings UI can expose beta features
- **A/B Testing:** Settings can be part of A/B test configuration

## Evolution Triggers

Reconsider settings approach when:

1. **User Feedback:** Users report difficulty finding or configuring settings
2. **Scale Changes:** Adding many new settings requires different UI pattern
3. **Sync Requirements:** Settings need to sync across devices (move to database)
4. **Performance Issues:** Settings access is slow (consider localStorage caching)
5. **Complexity Growth:** Settings become too complex for current pattern
6. **Mobile Growth:** Mobile traffic increases require mobile-optimized settings UI
7. **Enterprise Needs:** Enterprise features require audit trails (move to database)
8. **Theme Requirements:** Need for multiple themes or runtime switching
9. **Notification Complexity:** Notification needs become too complex for current model
10. **Team Structure:** Multiple teams working on settings requires coordination
