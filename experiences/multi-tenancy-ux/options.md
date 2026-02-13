# Options: Multi-Tenancy UX

## Contents

- [Tenant Identification](#tenant-identification)
  - [URL Path (`/org-slug/...`)](#url-path-org-slug)
  - [Subdomain (`acme.platform.com`)](#subdomain-acmeplatformcom)
  - [Header-Based (`X-Tenant-Id`)](#header-based-x-tenant-id)
  - [JWT Claim](#jwt-claim)
- [Tenant Switching UX](#tenant-switching-ux)
  - [Header Dropdown](#header-dropdown)
  - [Dedicated Switcher Page](#dedicated-switcher-page)
  - [URL-Based (Navigate to Different Path/Subdomain)](#url-based-navigate-to-different-pathsubdomain)
- [White-Labeling Depth](#white-labeling-depth)
  - [Logo + Colors Only](#logo--colors-only)
  - [Full Theme (Colors, Fonts, Layout)](#full-theme-colors-fonts-layout)
  - [Custom Domain + Full Branding](#custom-domain--full-branding)
  - [No White-Labeling](#no-white-labeling)
- [Data Isolation](#data-isolation)
  - [Shared Schema with `tenant_id` Column](#shared-schema-with-tenant_id-column)
  - [Schema-Per-Tenant](#schema-per-tenant)
  - [Database-Per-Tenant](#database-per-tenant)
- [Recommendations](#recommendations)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Tenant Identification

How the system identifies which tenant a request belongs to.

### URL Path (`/org-slug/...`)

**Description:** Tenant identifier included in URL path: `/acme-corp/dashboard`, `/acme-corp/products/123`

**Strengths:**
- Simple to implement—no DNS configuration needed
- Works with single domain and standard SSL certificate
- Easy deep linking and bookmarking
- Clear tenant context in URL (user always sees which tenant)
- SEO-friendly if needed

**Weaknesses:**
- URLs are longer (include tenant slug)
- Tenant slug must be URL-safe (no spaces, special chars)
- Requires route guards to validate tenant access
- Less "white-label" feel (tenant name visible in URL)

**Best For:**
- Starting out with multi-tenancy
- Internal tools or B2B apps where URL structure is acceptable
- When custom domains aren't required
- Teams wanting simplest implementation

**Avoid When:**
- White-labeling is critical (custom domains preferred)
- URLs need to be completely generic
- Tenant names contain special characters that don't URL-encode well

**Implementation:**
```typescript
// Vue Router
const routes = [
  { path: '/:tenantSlug/dashboard', component: Dashboard },
  { path: '/:tenantSlug/products/:id', component: ProductDetail }
]

// Route guard validates tenant access
router.beforeEach(async (to) => {
  const tenantSlug = to.params.tenantSlug
  await validateTenantAccess(tenantSlug)
})
```

### Subdomain (`acme.platform.com`)

**Description:** Tenant identifier in subdomain: `acme.platform.com/dashboard`, `beta.platform.com/products/123`

**Strengths:**
- Clean URLs (no tenant slug in path)
- Strong white-labeling support (can map to custom domains)
- Clear tenant isolation (each subdomain feels separate)
- Cookies can be scoped per subdomain
- Enables custom SSL certificates per tenant

**Weaknesses:**
- Requires DNS wildcard configuration (`*.platform.com`)
- CORS configuration needed for each subdomain
- More complex SSL certificate management (wildcard or multiple certs)
- Subdomain must be URL-safe
- Harder to test locally (requires hosts file or local DNS)

**Best For:**
- White-labeling requirements
- Custom domain support needed
- When tenant isolation should feel strongest
- Enterprise customers expecting custom domains

**Avoid When:**
- Simple internal tool
- Team lacks DevOps resources for DNS/SSL management
- Rapid prototyping phase
- Local development complexity is a blocker

**Implementation:**
```kotlin
// Backend: Resolve tenant from subdomain
@Component
class SubdomainTenantResolver {
    fun resolveTenant(host: String): String? {
        val subdomain = host.substringBefore(".")
        return tenantRepository.findBySubdomain(subdomain)?.id
    }
}
```

### Header-Based (`X-Tenant-Id`)

**Description:** Tenant ID sent in HTTP header: `X-Tenant-Id: acme-corp`

**Strengths:**
- Flexible—works with any URL structure
- Can combine with other methods (JWT + header)
- Simple to implement on backend
- No URL changes needed

**Weaknesses:**
- **Security risk:** Frontend can be compromised, header can be manipulated
- Not visible to users (no tenant context in URL)
- Requires frontend to always include header
- Can't bookmark tenant-specific URLs easily
- Less transparent (harder to debug)

**Best For:**
- Internal APIs only
- When combined with JWT validation
- Legacy systems adding multi-tenancy
- When URL structure can't change

**Avoid When:**
- Primary tenant identification method (use as fallback only)
- Security is critical (prefer JWT claims)
- User-facing URLs need tenant context
- Deep linking is important

**Implementation:**
```typescript
// Frontend: Include tenant header
apiClient.interceptors.request.use((config) => {
  config.headers['X-Tenant-Id'] = tenantStore.tenantId
  return config
})
```

### JWT Claim

**Description:** Tenant ID included in JWT token claims: `{ "tenantId": "acme-corp", ... }`

**Strengths:**
- **Most secure:** Can't be manipulated by frontend
- Backend validates tenant from token
- Single source of truth for tenant context
- Works with stateless authentication
- Can include tenant roles in same token

**Weaknesses:**
- Requires token refresh on tenant switch (new JWT issued)
- Token size increases (if including multiple tenant roles)
- Backend must validate token on every request

**Best For:**
- **Recommended as primary method**
- Security-critical applications
- Stateless architectures
- When tenant context must be cryptographically verified

**Avoid When:**
- Can't issue new tokens on tenant switch (rare)
- Token size is a concern (mitigate by only including current tenant)

**Implementation:**
```kotlin
// JWT includes tenant ID
data class JwtClaims(
    val sub: String,
    val email: String,
    val tenantId: String, // Current active tenant
    val tenantRoles: Map<String, List<String>> // All tenant roles
)

// Backend validates from JWT
fun resolveTenant(request: HttpServletRequest): String {
    val jwt = extractJwt(request)
    return jwt.getClaim("tenantId").asString()
        ?: throw TenantContextMissingException()
}
```

## Tenant Switching UX

How users switch between tenants in the UI.

### Header Dropdown

**Description:** Tenant name/logo in header, clicking opens dropdown with available tenants

**Strengths:**
- Always visible (persistent in header)
- Fast access (one click to switch)
- Shows current tenant context clearly
- Works well for 2-5 tenants

**Weaknesses:**
- Can be cluttered with many tenants (5+)
- Dropdown may need search/filter for large lists
- Limited space for tenant details (logo, role, last accessed)

**Best For:**
- Users with 2-5 tenants
- When tenant switching is frequent
- Header has available space
- Quick switching is priority

**Avoid When:**
- Users have 10+ tenants (use dedicated page instead)
- Header space is limited
- Need to show detailed tenant information

**Implementation:**
```vue
<template>
  <div class="tenant-switcher">
    <button @click="toggleDropdown" class="tenant-button">
      <img :src="currentTenant.logo" />
      <span>{{ currentTenant.name }}</span>
      <Icon name="chevron-down" />
    </button>
    <div v-if="isOpen" class="dropdown">
      <div
        v-for="tenant in availableTenants"
        :key="tenant.id"
        @click="switchTenant(tenant.id)"
        class="tenant-option"
      >
        <img :src="tenant.logo" />
        <div>
          <div>{{ tenant.name }}</div>
          <div class="role">{{ getRoleInTenant(tenant.id) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
```

### Dedicated Switcher Page

**Description:** Clicking tenant switcher navigates to `/switch-tenant` page with grid/list of all tenants

**Strengths:**
- Handles many tenants (10+)
- Can show rich information (logo, role, last accessed, unread count)
- Search/filter for large tenant lists
- Can show tenant status (active, inactive, pending)

**Weaknesses:**
- Extra navigation step (not as fast as dropdown)
- Requires page load/navigation
- Less discoverable (user must know to click)

**Best For:**
- Users with 5+ tenants
- When tenant information is important (role, status, notifications)
- MSPs managing many partners
- Platform admins with many tenants

**Avoid When:**
- Users typically have 1-3 tenants
- Fast switching is critical
- Header space allows dropdown

**Implementation:**
```vue
<template>
  <div class="tenant-switcher-page">
    <h1>Select Organization</h1>
    <input v-model="searchQuery" placeholder="Search organizations..." />
    <div class="tenant-grid">
      <div
        v-for="tenant in filteredTenants"
        :key="tenant.id"
        @click="switchTenant(tenant.id)"
        class="tenant-card"
      >
        <img :src="tenant.logo" />
        <h3>{{ tenant.name }}</h3>
        <p>Role: {{ getRoleInTenant(tenant.id) }}</p>
        <p>Last accessed: {{ formatDate(tenant.lastAccessed) }}</p>
      </div>
    </div>
  </div>
</template>
```

### URL-Based (Navigate to Different Path/Subdomain)

**Description:** User navigates directly to tenant-specific URL to switch context

**Strengths:**
- Works for power users who know tenant slugs
- Supports bookmarking specific tenant contexts
- Can be used programmatically
- No UI component needed

**Weaknesses:**
- Not discoverable (users must know tenant slug)
- Requires typing/remembering tenant identifier
- Easy to make mistakes (wrong tenant slug)
- Not user-friendly for non-technical users

**Best For:**
- Power users
- Programmatic access
- Deep linking from external systems
- As supplement to other methods (not primary)

**Avoid When:**
- Primary switching mechanism
- Non-technical users
- When discoverability is important

## White-Labeling Depth

How much customization partners can apply to their tenant experience.

### Logo + Colors Only

**Description:** Partners can customize logo and primary/secondary colors

**Strengths:**
- Simple to implement (CSS custom properties)
- Low maintenance burden
- Fast to set up (partners upload logo, pick colors)
- Covers 80% of white-labeling needs

**Weaknesses:**
- Limited customization
- May not satisfy enterprise customers wanting full branding
- Can't customize fonts, layout, email templates

**Best For:**
- Starting with white-labeling
- Most B2B SaaS use cases
- When speed to market is important
- Teams with limited design resources

**Avoid When:**
- Enterprise customers require full branding control
- Custom domains are required
- Email branding must match partner brand exactly

**Implementation:**
```typescript
// Simple branding configuration
interface BasicBranding {
  logoUrl: string
  primaryColor: string
  secondaryColor: string
}

// Apply via CSS custom properties
function applyBranding(branding: BasicBranding) {
  document.documentElement.style.setProperty('--primary-color', branding.primaryColor)
  document.documentElement.style.setProperty('--secondary-color', branding.secondaryColor)
  // Logo applied to header component
}
```

### Full Theme (Colors, Fonts, Layout)

**Description:** Partners can customize colors, fonts, spacing, and some layout components

**Strengths:**
- More comprehensive branding
- Can match partner's design system more closely
- Satisfies most enterprise requirements
- Still manageable complexity

**Weaknesses:**
- More complex to implement (theme system needed)
- Higher maintenance (validate fonts, ensure accessibility)
- More support burden (partners may break UI with bad choices)

**Best For:**
- Enterprise customers
- When brand consistency is important
- Teams with design system infrastructure
- Mature white-labeling feature

**Avoid When:**
- Just starting with white-labeling
- Limited engineering resources
- Simple logo + colors meets needs

**Implementation:**
```typescript
// Extended branding configuration
interface FullBranding extends BasicBranding {
  fontFamily: string
  fontSize: string
  spacing: 'compact' | 'normal' | 'comfortable'
  borderRadius: string
  componentOverrides: Record<string, any>
}

// Apply via comprehensive theme system
function applyFullTheme(branding: FullBranding) {
  applyBranding(branding)
  document.documentElement.style.setProperty('--font-family', branding.fontFamily)
  document.documentElement.style.setProperty('--spacing', branding.spacing)
  // Apply component-level overrides
}
```

### Custom Domain + Full Branding

**Description:** Partners get custom domain (`partners.acme.com`) with full branding control

**Strengths:**
- **Strongest white-labeling** (feels like partner's own platform)
- Enterprise-grade feature
- Can include custom email domains
- Highest customer satisfaction for white-labeling

**Weaknesses:**
- **Most complex:** DNS, SSL certificates, domain validation
- Requires DevOps/Infrastructure support
- Higher cost (SSL certs, domain management)
- Longer setup time (DNS propagation)

**Best For:**
- Enterprise customers
- White-labeling is core product feature
- When "own platform" feel is required
- Teams with DevOps/infrastructure support

**Avoid When:**
- Early-stage product
- Limited infrastructure resources
- Logo + colors meets customer needs
- Can't support DNS/SSL management

**Implementation:**
```kotlin
// Custom domain mapping
@Entity
class Tenant {
    var customDomain: String? = null
    var sslCertificateId: String? = null
    var dnsValidated: Boolean = false
}

// Domain resolver
fun resolveTenantFromDomain(host: String): Tenant? {
    return tenantRepository.findByCustomDomain(host)
        ?: tenantRepository.findBySubdomain(extractSubdomain(host))
}
```

### No White-Labeling

**Description:** All tenants see platform branding, no customization

**Strengths:**
- Simplest implementation (no branding system needed)
- Consistent UX across all tenants
- No support burden for branding issues
- Faster to ship

**Weaknesses:**
- May limit sales to enterprise customers
- Partners can't differentiate their brand
- Less "professional" feel for partners

**Best For:**
- Internal tools
- When platform brand is always shown
- MVP phase
- When white-labeling isn't a requirement

**Avoid When:**
- B2B SaaS selling to partners/resellers
- Enterprise customers expect white-labeling
- Competitive advantage requires customization

## Data Isolation

How tenant data is isolated at the database level.

### Shared Schema with `tenant_id` Column

**Description:** All tenants share same database schema, each row has `tenant_id` column

**Strengths:**
- **Simplest to implement** (add column to tables)
- Easy migrations (single schema to manage)
- Efficient for many small tenants
- Simpler backups/restores
- Lower infrastructure cost

**Weaknesses:**
- **Risk of data leakage** if queries miss tenant filter
- Requires discipline (every query must filter by tenant)
- Harder to scale individual tenants
- Can't easily move tenant to separate database

**Best For:**
- **Recommended default** for most cases
- Many small-to-medium tenants
- Teams starting with multi-tenancy
- When simplicity is priority

**Avoid When:**
- Regulatory requirements mandate physical separation
- Tenants need different schemas
- Very large tenants (billions of rows)

**Implementation:**
```kotlin
@Entity
@Table(name = "orders")
class Order {
    @Column(name = "tenant_id", nullable = false)
    var tenantId: String = ""
    
    // Hibernate filter ensures tenant filter always applied
}

// Repository automatically filters by tenant
@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    // Hibernate filter applies tenant_id filter automatically
    fun findAll(): List<Order> // Only returns current tenant's orders
}
```

### Schema-Per-Tenant

**Description:** Each tenant has own database schema within same database

**Strengths:**
- Stronger isolation (schema-level separation)
- Can have different schemas per tenant (flexibility)
- Easier to move tenant to separate database later
- Better for compliance (some regulations prefer schema separation)

**Weaknesses:**
- More complex (schema management, migrations per tenant)
- Higher infrastructure cost (more schemas)
- Harder to query across tenants (if needed)
- Migration complexity (apply to all schemas)

**Best For:**
- Enterprise customers requiring strong isolation
- When tenants need different schemas
- Regulatory compliance requirements
- When planning to move to database-per-tenant later

**Avoid When:**
- Many small tenants (overhead too high)
- Simple use case (shared schema sufficient)
- Team lacks schema management tooling

**Implementation:**
```kotlin
// AbstractRoutingDataSource routes to tenant-specific schema
class TenantRoutingDataSource : AbstractRoutingDataSource() {
    override fun determineCurrentLookupKey(): Any {
        return TenantContextHolder.getTenantId()
    }
}

// Each tenant schema has same structure but separate namespace
// tenant_acme.orders, tenant_beta.orders, etc.
```

### Database-Per-Tenant

**Description:** Each tenant has completely separate database

**Strengths:**
- **Strongest isolation** (physical separation)
- Can scale tenants independently
- Easier compliance (regulations requiring separate databases)
- Can use different database engines per tenant

**Weaknesses:**
- **Most complex** (database management, connection pooling)
- Highest infrastructure cost
- Hardest to query across tenants
- Migration complexity (apply to all databases)

**Best For:**
- Enterprise customers with strict compliance needs
- Very large tenants (billions of rows)
- When tenants need different database engines
- Regulatory requirements (HIPAA, GDPR in some cases)

**Avoid When:**
- Many tenants (cost prohibitive)
- Simple use case
- Team lacks database management infrastructure
- **Not recommended for most B2B SaaS**

## Recommendations

### Default Recommendation

**Tenant Identification:**
- **Primary:** JWT claim (most secure)
- **Fallback:** URL path (`/tenant-slug/...`) for deep linking
- **Header:** `X-Tenant-Id` as additional validation only

**Tenant Switching UX:**
- **Header dropdown** for users with 2-5 tenants
- **Dedicated switcher page** for users with 5+ tenants
- Always show current tenant in header

**White-Labeling Depth:**
- **Start:** Logo + colors only
- **Evolve to:** Full theme when needed
- **Enterprise:** Custom domain + full branding

**Data Isolation:**
- **Default:** Shared schema with `tenant_id` column
- **Enterprise:** Schema-per-tenant if compliance requires
- **Avoid:** Database-per-tenant unless absolutely necessary

### Rationale

- **Security first:** JWT claims can't be manipulated, URL provides user visibility
- **User experience:** Header dropdown is fastest, dedicated page handles scale
- **Pragmatic:** Start simple with white-labeling, evolve based on needs
- **Simplicity:** Shared schema is simplest, sufficient for most cases

## Synergies

### Authentication

- JWT claims include tenant ID → seamless tenant context
- Token refresh on tenant switch → secure tenant switching
- Single sign-on can include tenant selection

### Security

- Tenant isolation is security boundary
- Audit logs include tenant context
- Permission checks scoped to tenant

### Configuration Management

- Tenant-specific feature flags
- Tenant-specific environment variables
- White-label configuration stored per tenant

### Design Consistency

- White-labeling extends design system
- Tenant themes use design tokens
- Branding validation ensures accessibility

## Evolution Triggers

**When to evolve tenant identification:**
- URL path → Subdomain: White-labeling requirements, custom domains needed
- Header → JWT: Security audit requires cryptographically verified tenant context

**When to evolve switching UX:**
- Header dropdown → Dedicated page: Users have 5+ tenants, need search/filter

**When to evolve white-labeling:**
- Logo + colors → Full theme: Enterprise customers request font/layout customization
- Full theme → Custom domain: Enterprise customers require custom domains

**When to evolve data isolation:**
- Shared schema → Schema-per-tenant: Compliance requirements, need stronger isolation
- Schema-per-tenant → Database-per-tenant: Regulatory mandate, very large tenants

**General principle:** Start simple, evolve based on actual requirements, not hypothetical needs.
