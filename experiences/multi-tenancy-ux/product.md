# Product Perspective: Multi-Tenancy UX

## Contents

- [Understanding Multi-Tenancy in B2B SaaS](#understanding-multi-tenancy-in-b2b-saas)
- [Tenant Context: Always Know Where You Are](#tenant-context-always-know-where-you-are)
- [Tenant Switching: Fast and Obvious](#tenant-switching-fast-and-obvious)
- [White-Labeling: Partner Branding](#white-labeling-partner-branding)
- [Role-Based UI Per Tenant](#role-based-ui-per-tenant)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Understanding Multi-Tenancy in B2B SaaS

In B2B SaaS platforms like Pax8, users belong to organizations (partners, resellers, customers). Each organization is a **tenant**—an isolated workspace with its own data, users, and configuration. Multi-tenancy is the architecture that allows a single application instance to serve multiple tenants securely.

**Key characteristics:**
- Users belong to one or more tenant organizations
- Some users (e.g., Pax8 platform admins, MSPs managing multiple partners) need access to multiple tenants
- Each tenant has isolated data, users, billing, and configuration
- Tenants may have different feature sets based on subscription plans
- Partners may want white-labeled experiences with their branding

**The UX challenge:** Users must always understand which tenant context they're operating in, switch between tenants seamlessly, and never see data from the wrong tenant.

## Tenant Context: Always Know Where You Are

**Product requirement:** The current tenant must be **always visible** and **unmistakable**. Users should never wonder "which organization am I in right now?"

**Visual indicators:**
- Tenant name and logo in the header (persistent, above the fold)
- Tenant-specific branding (colors, logo) applied throughout the UI
- URL structure that includes tenant context (`/acme-corp/dashboard` or `acme.platform.com`)
- Breadcrumbs or navigation that reflects tenant context

**Example header pattern:**
```
[Platform Logo]  Dashboard  Products  Orders  [Acme Corp ▼]  [User Menu]
                                    ↑ Tenant switcher - always visible
```

**Why this matters:**
- Prevents accidental actions in the wrong tenant
- Builds trust that the system understands organizational boundaries
- Reduces support tickets from confused users
- Critical for compliance and audit requirements

## Tenant Switching: Fast and Obvious

**Product requirement:** Switching tenants should be **instant** and **obvious**—no logout/login, no confusion about which tenant is now active.

**Switching mechanisms:**

1. **Header dropdown** (recommended for 2-5 tenants)
   - Click tenant name in header → dropdown shows available tenants
   - Select tenant → instant switch with visual feedback
   - Shows tenant name, logo, and role in that tenant

2. **Dedicated switcher page** (recommended for 5+ tenants)
   - Click tenant switcher → navigate to `/switch-tenant`
   - Grid/list view of all accessible tenants
   - Search/filter for large tenant lists
   - Shows last accessed time, unread notifications count per tenant

3. **URL-based switching** (for power users)
   - Navigate to `/tenant-slug/dashboard` to switch context
   - Deep links preserve tenant context

**Switching behavior:**
- **Immediate**: No full page reload, no re-authentication
- **Clear feedback**: Loading state, success message, visual transition
- **Data refresh**: All tenant-scoped data reloads (permissions, navigation, cached API responses)
- **State clearing**: Previous tenant's data cleared from cache/localStorage
- **URL update**: URL reflects new tenant context

**Example user flow:**
1. User clicks "Acme Corp" in header
2. Dropdown shows: "Acme Corp (Admin)", "Beta Partners (Viewer)", "Gamma Inc (Member)"
3. User selects "Beta Partners"
4. UI shows loading spinner: "Switching to Beta Partners..."
5. Page refreshes data, navigation updates (different features available), URL changes to `/beta-partners/dashboard`
6. Success toast: "Now viewing Beta Partners"

## White-Labeling: Partner Branding

**Product requirement:** Partners should be able to customize branding (logo, colors, domain) to make the platform feel like their own.

**White-labeling scope:**

1. **Logo and colors** (minimum viable)
   - Partner logo replaces platform logo
   - Primary brand color replaces platform color
   - Applied to header, buttons, links, loading states

2. **Full theme** (enhanced)
   - Custom fonts, spacing, component styling
   - Custom email templates with partner branding
   - Custom domain (`partners.acme.com` instead of `acme.platform.com`)

3. **Custom domain + full branding** (enterprise)
   - Dedicated subdomain or custom domain
   - SSL certificate management
   - Full control over email branding, support portal branding

**Product decisions:**
- **How much customization?** Balance partner needs vs. maintenance burden
- **Defaults for unbranded tenants:** Sensible platform defaults that work for all
- **Validation:** Logo dimensions, color contrast (accessibility), file size limits
- **Edge cases:** What happens when logo fails to load? Fallback to tenant name text

**Example white-label configuration:**
```json
{
  "tenantId": "acme-corp",
  "branding": {
    "logoUrl": "https://cdn.acme.com/logo.png",
    "primaryColor": "#1a73e8",
    "secondaryColor": "#34a853",
    "customDomain": "partners.acme.com",
    "emailBranding": {
      "fromName": "Acme Corp Partner Portal",
      "fromEmail": "noreply@acme.com"
    }
  }
}
```

## Role-Based UI Per Tenant

**Product requirement:** The same user may have different roles (and thus different UI capabilities) in different tenants.

**Example scenario:**
- Sarah is **Admin** in "Acme Corp" → sees all features, can manage users
- Sarah is **Viewer** in "Beta Partners" → sees read-only dashboard, no user management
- Sarah is **Member** in "Gamma Inc" → sees limited features, no admin access

**UI adaptation per tenant:**
- **Navigation**: Different menu items based on role in current tenant
- **Feature flags**: Features enabled/disabled per tenant plan + user role
- **Actions**: Buttons/actions shown/hidden based on permissions in current tenant
- **Data visibility**: Different data sets visible based on role (e.g., admin sees all orders, viewer sees only assigned orders)

**Product challenge:** Users must understand why they see different features when switching tenants. Clear messaging: "You have Viewer access in Beta Partners" in the tenant switcher.

## Personas

### 1. User Working in Single Tenant
**Profile:** Works for one organization, never switches tenants
**Needs:**
- Clear indication of their organization (even if only one)
- No confusion about tenant switching (may not even see switcher if only one tenant)
- Consistent branding of their organization

### 2. User Switching Between Multiple Tenants
**Profile:** MSP managing multiple partners, or Pax8 admin supporting multiple customers
**Needs:**
- Fast tenant switching (header dropdown or dedicated page)
- Clear indication of current tenant at all times
- Different permissions/features per tenant clearly communicated
- No data leakage between tenants (critical security need)

### 3. Partner Admin Managing Their Org
**Profile:** Admin user within a partner organization, managing their team
**Needs:**
- White-labeling to reflect their brand
- User management scoped to their tenant only
- Configuration and settings for their organization
- Clear boundaries (can't see other tenants' data)

### 4. Platform Admin (Pax8) Managing All Tenants
**Profile:** Pax8 internal admin supporting the platform
**Needs:**
- Impersonation capability to view tenant as that tenant's user would see it
- Clear impersonation indicator (never forget they're impersonating)
- Audit trail of impersonation actions
- Ability to switch between tenants quickly for support

## Success Metrics

**Tenant switch success rate:**
- Target: >99% of tenant switches complete without errors
- Measure: Successful switches / total switch attempts
- Track: Errors during switch (permissions failure, data load failure, network error)

**Cross-tenant data leak incidents:**
- Target: **Zero** (this is a critical security metric)
- Measure: Number of incidents where data from Tenant A appears in Tenant B's UI
- Track: Security audits, user reports, automated tests

**Time-to-switch:**
- Target: <2 seconds from click to fully loaded new tenant context
- Measure: Time from tenant selection to last data load completion
- Track: Performance monitoring, user experience surveys

**White-label setup completion rate:**
- Target: >80% of eligible tenants complete white-label setup
- Measure: Tenants with branding configured / total eligible tenants
- Track: Onboarding funnel, feature adoption

**User confusion metrics:**
- Support tickets asking "which org am I in?"
- Users accidentally performing actions in wrong tenant
- Time spent locating tenant switcher

## Common Product Mistakes

**No clear tenant indicator:**
- User can't tell which tenant they're in
- Leads to confusion, wrong actions, support tickets
- **Fix:** Always show tenant name/logo in header

**Tenant switch requiring logout/login:**
- Poor UX, feels broken, users avoid switching
- **Fix:** Instant switch with re-authentication only when security requires it

**Cross-tenant data leakage:**
- Worst possible bug—security incident, compliance violation
- **Fix:** Rigorous testing, clear all state on switch, server-side tenant filtering

**White-labeling breaking on edge cases:**
- Missing logo shows broken image, custom colors break contrast (accessibility)
- **Fix:** Sensible defaults, validation, fallback handling

**Tenant switcher hidden or hard to find:**
- Users don't know they can switch tenants
- **Fix:** Prominent placement in header, discoverable UI

**No indication of role differences per tenant:**
- User confused why they see different features in different tenants
- **Fix:** Show role in tenant switcher, explain permission differences
