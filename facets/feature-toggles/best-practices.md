# Feature Toggles: Best Practices

This document covers language-agnostic best practices for feature toggles, along with stack-specific guidance for Kotlin, Spring Boot, Vue 3, and React. These practices help teams avoid common pitfalls and maintain healthy toggle systems.

## Short-Lived Release Toggles

Release toggles should be short-lived, existing for days to weeks, not months. The longer a toggle exists, the more likely it is to become permanent technical debt. Plan for toggle removal from day one.

**Lifespan Guidelines**:
- **Release toggles**: Days to weeks (typically 1-4 weeks)
- **Experiment toggles**: Days to weeks (until experiment concludes)
- **Ops toggles**: Weeks to months (operational controls)
- **Permission toggles**: Weeks to months (business rules)

**Removal Process**:
1. Create toggle with expiration date
2. Develop feature behind toggle
3. Test and validate feature
4. Release feature (toggle enabled for all users)
5. Monitor for stability period (typically 1-2 weeks)
6. Remove toggle code and toggle definition
7. Verify no references remain

**Expiration Tracking**:

Set expiration dates when creating toggles and alert on toggles that exceed their expected lifespan:

```kotlin
data class FeatureToggle(
    val name: String,
    val enabled: Boolean,
    val category: ToggleCategory,
    val createdAt: Instant,
    val expiresAt: Instant, // Required for release toggles
    val description: String
)

fun alertOnExpiredToggles() {
    val expiredToggles = toggleRepository.findExpiredToggles()
    if (expiredToggles.isNotEmpty()) {
        notifyTeam("Expired toggles need removal: ${expiredToggles.map { it.name }}")
    }
}
```

**Toggle Removal as Part of Feature Work**:

Include toggle removal as a task in the feature ticket. Don't create separate cleanup tickets—they often get deprioritized. The person who added the toggle is responsible for removing it.

## Toggle Naming Conventions

Consistent naming conventions make toggles discoverable, understandable, and manageable. Use descriptive names that indicate category, feature, and purpose.

**Naming Format**: `{category}-{feature}-{description}`

**Categories**:
- `release-`: Release toggles (short-lived)
- `experiment-`: Experiment toggles (A/B tests)
- `ops-`: Ops toggles (operational controls)
- `perm-`: Permission toggles (access control)

**Examples**:
- `release-billing-v2-invoice-page`
- `experiment-checkout-button-color`
- `ops-disable-email-notifications`
- `perm-premium-advanced-reports`

**Naming Rules**:
- Use kebab-case (lowercase with hyphens)
- Be descriptive but concise (aim for 3-5 segments)
- Include feature name and variant (e.g., `v2`, `new-design`)
- Avoid abbreviations unless widely understood
- Avoid personal names (e.g., `johns-experiment`)
- Avoid temporary markers (e.g., `test`, `temp`, `old`)

**Bad Examples**:
- `new_feature` (too vague, wrong separator)
- `test_flag` (temporary marker, unclear purpose)
- `johns_experiment` (personal name, unclear purpose)
- `toggle1` (not descriptive)

**Good Examples**:
- `release-billing-v2-invoice-page` (clear category, feature, variant)
- `experiment-checkout-button-color-blue` (clear experiment and variant)
- `ops-disable-email-notifications` (clear operational control)
- `perm-premium-advanced-reports` (clear permission and feature)

## Toggle Removal Discipline

Toggle removal is critical for maintaining code quality. Toggles that aren't removed become technical debt, making the codebase harder to understand and maintain.

**Removal Checklist**:
1. Feature is fully released and stable
2. Toggle has been enabled for all users for stability period
3. No incidents related to the feature
4. Remove toggle checks from code
5. Remove toggle definition from database/config
6. Verify no references remain (static analysis)
7. Update documentation if needed

**Tracking Toggle Age**:

Monitor toggle age and alert on toggles that exceed expected lifespan:

```kotlin
fun trackToggleAge() {
    val releaseToggles = toggleRepository.findByCategory(ToggleCategory.RELEASE)
    val oldToggles = releaseToggles.filter { 
        it.ageInDays > 30 // Alert on toggles older than 30 days
    }
    
    if (oldToggles.isNotEmpty()) {
        notifyTeam("Old release toggles need removal: ${oldToggles.map { it.name }}")
    }
}
```

**Automated Cleanup**:

Consider automated cleanup for toggles that are clearly obsolete:

```kotlin
fun cleanupObsoleteToggles() {
    val obsoleteToggles = toggleRepository.findObsoleteToggles()
    obsoleteToggles.forEach { toggle ->
        if (toggle.referencesInCode == 0 && toggle.enabledForDays > 90) {
            toggleRepository.delete(toggle)
            log.info("Deleted obsolete toggle: ${toggle.name}")
        }
    }
}
```

## Safe Defaults

When toggle evaluation fails (service unavailable, configuration missing, network error), the system must default to a safe state. The safe state depends on toggle category.

**Default Rules**:
- **Release toggles**: Default to `false` (off). Don't expose incomplete features if toggle service fails.
- **Ops toggles**: Default to `true` (on). Don't disable working features if toggle service fails.
- **Permission toggles**: Default to `false` (off). Don't grant access if authorization can't be verified.
- **Experiment toggles**: Default to `false` (off). Don't expose experiment variants if evaluation fails.

**Implementation**:

```kotlin
fun isEnabled(toggleName: String, context: ToggleContext): Boolean {
    return try {
        evaluateToggle(toggleName, context)
    } catch (e: Exception) {
        log.warn("Toggle evaluation failed for $toggleName, using safe default", e)
        getSafeDefault(toggleName)
    }
}

private fun getSafeDefault(toggleName: String): Boolean {
    return when {
        toggleName.startsWith("release-") -> false
        toggleName.startsWith("ops-") -> true
        toggleName.startsWith("perm-") -> false
        toggleName.startsWith("experiment-") -> false
        else -> false
    }
}
```

**Testing Safe Defaults**:

Always test that safe defaults work correctly:

```kotlin
@Test
fun `release toggle defaults to off on failure`() {
    val toggleService = ToggleService(failingRepository)
    assertThat(toggleService.isEnabled("release-feature")).isFalse()
}

@Test
fun `ops toggle defaults to on on failure`() {
    val toggleService = ToggleService(failingRepository)
    assertThat(toggleService.isEnabled("ops-feature")).isTrue()
}
```

## Minimize Toggle Scope

Keep toggle checks at the highest possible level—route guards, API controllers, top-level components. Don't scatter toggle checks deep in business logic. A single toggle check point is easier to remove and understand.

**Good: Toggle Check at Boundary**:

```kotlin
@RestController
class InvoiceController(
    private val toggleService: ToggleService
) {
    @GetMapping("/invoices")
    fun getInvoices(): List<Invoice> {
        return if (toggleService.isEnabled("release-billing-v2-invoice-page")) {
            invoiceServiceV2.getInvoices()
        } else {
            invoiceServiceLegacy.getInvoices()
        }
    }
}
```

**Bad: Toggle Check Deep in Logic**:

```kotlin
class InvoiceService {
    fun calculateTotal(invoice: Invoice): Money {
        val baseTotal = calculateBaseTotal(invoice)
        val tax = if (toggleService.isEnabled("release-billing-v2-invoice-page")) {
            calculateTaxV2(invoice)
        } else {
            calculateTaxLegacy(invoice)
        }
        val discount = if (toggleService.isEnabled("release-billing-v2-invoice-page")) {
            calculateDiscountV2(invoice)
        } else {
            calculateDiscountLegacy(invoice)
        }
        return baseTotal + tax - discount
    }
}
```

**Frontend: Toggle Check at Component Level**:

```vue
<!-- Good: Toggle check at top level -->
<template>
  <InvoicePageV2 v-if="isEnabled('release-billing-v2-invoice-page')" />
  <InvoicePageLegacy v-else />
</template>

<!-- Bad: Toggle checks scattered throughout component -->
<template>
  <div>
    <div v-if="isEnabled('release-billing-v2-invoice-page')">
      <TaxCalculationV2 />
    </div>
    <div v-else>
      <TaxCalculationLegacy />
    </div>
    <div v-if="isEnabled('release-billing-v2-invoice-page')">
      <DiscountCalculationV2 />
    </div>
    <div v-else>
      <DiscountCalculationLegacy />
    </div>
  </div>
</template>
```

## Don't Nest Toggles

Avoid nested toggles where one toggle only makes sense when another is enabled. Nested toggles create exponential complexity and make testing and reasoning difficult.

**Bad: Nested Toggles**:

```kotlin
if (toggleService.isEnabled("release-billing-v2")) {
    if (toggleService.isEnabled("release-billing-v2-payments")) {
        // Billing v2 with payments
    } else {
        // Billing v2 without payments
    }
} else {
    // Legacy billing
}
```

**Good: Independent Toggles**:

```kotlin
val useBillingV2 = toggleService.isEnabled("release-billing-v2-invoice-page")
val usePaymentV2 = toggleService.isEnabled("release-payment-v2-checkout")

when {
    useBillingV2 && usePaymentV2 -> processWithBothV2()
    useBillingV2 -> processWithBillingV2Only()
    usePaymentV2 -> processWithPaymentV2Only()
    else -> processLegacy()
}
```

**Flattening Strategy**:

If toggles are naturally nested, consider flattening them:

- Instead of: `release-billing-v2` + `release-billing-v2-payments`
- Use: `release-billing-v2-invoice-page` + `release-payment-v2-checkout`

This makes toggles independent and easier to reason about.

## Document Every Toggle

Every toggle must have documentation: name, purpose, owner, expected lifespan, safe default, and how to verify it works. A toggle without documentation becomes a mystery nobody wants to touch.

**Toggle Documentation Template**:

```kotlin
data class FeatureToggle(
    val name: String,
    val enabled: Boolean,
    val category: ToggleCategory,
    val description: String, // What does this toggle control?
    val owner: String, // Team or individual responsible
    val createdAt: Instant,
    val expiresAt: Instant,
    val safeDefault: Boolean, // What happens if evaluation fails?
    val verificationSteps: String, // How to verify it works
    val relatedTickets: List<String> // JIRA tickets or issues
)
```

**Documentation Requirements**:
- **Purpose**: What feature or behavior does this toggle control?
- **Owner**: Who is responsible for this toggle? (team or individual)
- **Lifespan**: When should this toggle be removed?
- **Safe Default**: What happens if toggle evaluation fails?
- **Verification**: How can someone verify the toggle works correctly?
- **Dependencies**: Are there other toggles or features this depends on?

**Example Documentation**:

```
Name: release-billing-v2-invoice-page
Category: Release
Owner: Billing Team
Created: 2026-01-15
Expires: 2026-02-15
Description: Controls access to the new v2 invoice page design. When enabled, users see the redesigned invoice page with improved layout and performance.
Safe Default: false (don't expose incomplete feature)
Verification: 
  1. Enable toggle for test user
  2. Navigate to /invoices
  3. Verify v2 design is displayed
  4. Verify all invoice data is correct
Related Tickets: BILLING-123
```

## Stack-Specific Best Practices

### Kotlin

**Sealed Classes for Toggle Definitions**:

Use sealed classes to define toggle categories, allowing the compiler to catch missing cases:

```kotlin
sealed class ToggleCategory {
    object Release : ToggleCategory()
    object Experiment : ToggleCategory()
    object Ops : ToggleCategory()
    object Permission : ToggleCategory()
}

fun getSafeDefault(category: ToggleCategory): Boolean {
    return when (category) {
        is ToggleCategory.Release -> false
        is ToggleCategory.Ops -> true
        is ToggleCategory.Permission -> false
        is ToggleCategory.Experiment -> false
    }
}
```

**Extension Functions for Toggle Evaluation**:

Create extension functions to make toggle evaluation more ergonomic:

```kotlin
fun ToggleContext.isFeatureEnabled(toggleName: String): Boolean {
    return toggleService.isEnabled(toggleName, this)
}

// Usage
val context = ToggleContext(userId = "user-123")
if (context.isFeatureEnabled("release-billing-v2-invoice-page")) {
    // Use v2
}
```

### Spring Boot

**@ConditionalOnProperty for Startup-Time Toggles**:

Use Spring Boot's conditional configuration for toggles that control bean creation:

```kotlin
@Configuration
class FeatureConfiguration {
    
    @Bean
    @ConditionalOnProperty(
        name = "feature-toggles.release-billing-v2-invoice-page",
        havingValue = "true",
        matchIfMissing = false
    )
    fun billingV2Service(): BillingV2Service {
        return BillingV2Service()
    }
}
```

**Custom @FeatureToggle Annotation**:

Create a custom annotation for controller methods:

```kotlin
@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureToggle(
    val name: String,
    val defaultEnabled: Boolean = false
)

@Aspect
@Component
class FeatureToggleAspect(
    private val toggleService: ToggleService
) {
    @Around("@annotation(featureToggle)")
    fun checkToggle(
        joinPoint: ProceedingJoinPoint, 
        featureToggle: FeatureToggle
    ): Any? {
        val context = buildContextFromRequest()
        return if (toggleService.isEnabled(featureToggle.name, context)) {
            joinPoint.proceed()
        } else {
            throw FeatureDisabledException(featureToggle.name)
        }
    }
}

@RestController
class InvoiceController {
    
    @GetMapping("/invoices")
    @FeatureToggle("release-billing-v2-invoice-page")
    fun getInvoicesV2(): List<Invoice> {
        return invoiceServiceV2.getInvoices()
    }
}
```

**HandlerInterceptor for Request-Level Evaluation**:

Use interceptors for toggles that control entire request flows:

```kotlin
@Component
class FeatureToggleInterceptor(
    private val toggleService: ToggleService
) : HandlerInterceptor {
    
    override fun preHandle(
        request: HttpServletRequest,
        response: HttpServletResponse,
        handler: Any
    ): Boolean {
        val toggleName = extractToggleName(request)
        val context = buildContextFromRequest(request)
        
        return if (toggleService.isEnabled(toggleName, context)) {
            true
        } else {
            response.status = HttpStatus.NOT_FOUND.value()
            false
        }
    }
}
```

### Vue 3

**Composable for Toggle Evaluation**:

Create a composable to make toggle evaluation reusable:

```typescript
// composables/useFeatureToggle.ts
export function useFeatureToggle() {
  const session = useSession()
  
  const isEnabled = (toggleName: string): boolean => {
    return session.value?.features?.[toggleName] ?? false
  }
  
  return { isEnabled }
}
```

**Route Guards for Toggle-Controlled Pages**:

```typescript
// router/guards.ts
export function createFeatureToggleGuard(toggleName: string) {
  return (to: RouteLocationNormalized) => {
    const { isEnabled } = useFeatureToggle()
    if (!isEnabled(toggleName)) {
      return { name: 'feature-unavailable' }
    }
  }
}

// router/index.ts
router.beforeEach((to, from, next) => {
  if (to.meta.requiresFeature) {
    const guard = createFeatureToggleGuard(to.meta.requiresFeature)
    const result = guard(to)
    if (result) {
      next(result)
      return
    }
  }
  next()
})
```

**Provide/Inject for Toggle Service**:

```typescript
// plugins/featureToggle.ts
export default {
  install(app: App) {
    const toggleService = new ToggleService()
    app.provide('toggleService', toggleService)
  }
}

// Component usage
<script setup lang="ts">
const toggleService = inject<ToggleService>('toggleService')
const isEnabled = (name: string) => toggleService?.isEnabled(name) ?? false
</script>
```

### React

**useFeatureToggle Hook**:

```typescript
// hooks/useFeatureToggle.ts
export function useFeatureToggle() {
  const session = useSession()
  
  const isEnabled = (toggleName: string): boolean => {
    return session?.features?.[toggleName] ?? false
  }
  
  return { isEnabled }
}
```

**Route Wrappers for Toggle-Controlled Pages**:

```typescript
// components/FeatureRoute.tsx
function FeatureRoute({ 
  feature, 
  children 
}: { 
  feature: string
  children: React.ReactNode 
}) {
  const { isEnabled } = useFeatureToggle()
  
  if (!isEnabled(feature)) {
    return <Navigate to="/feature-unavailable" />
  }
  
  return <>{children}</>
}

// Usage
<Routes>
  <Route 
    path="/invoices" 
    element={
      <FeatureRoute feature="release-billing-v2-invoice-page">
        <InvoicePageV2 />
      </FeatureRoute>
    } 
  />
</Routes>
```

**Context Provider for Toggle Service**:

```typescript
// context/FeatureToggleContext.tsx
const FeatureToggleContext = createContext<ToggleService | null>(null)

export function FeatureToggleProvider({ children }: { children: React.ReactNode }) {
  const toggleService = new ToggleService()
  return (
    <FeatureToggleContext.Provider value={toggleService}>
      {children}
    </FeatureToggleContext.Provider>
  )
}

export function useFeatureToggleContext() {
  const context = useContext(FeatureToggleContext)
  if (!context) {
    throw new Error('useFeatureToggleContext must be used within FeatureToggleProvider')
  }
  return context
}
```

## Summary

Following these best practices helps teams maintain healthy toggle systems:

1. **Keep release toggles short-lived**—plan for removal from day one
2. **Use consistent naming conventions**—make toggles discoverable and understandable
3. **Remove toggles promptly**—include removal as part of feature work
4. **Default to safe states**—release toggles default off, ops toggles default on
5. **Minimize toggle scope**—keep checks at boundaries
6. **Avoid nested toggles**—flatten into independent toggles
7. **Document everything**—name, purpose, owner, lifespan, safe default, verification

Stack-specific practices leverage language and framework features to make toggle evaluation more ergonomic and type-safe. The goal is to make toggles easy to use correctly and hard to use incorrectly.
