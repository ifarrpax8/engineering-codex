# Feature Toggles: Architecture

This document covers the architectural patterns, implementation approaches, and technical trade-offs for feature toggle systems. It addresses both simple implementations suitable for teams without budget for commercial services and sophisticated implementations using commercial platforms.

## Toggle Categories

Feature toggles can be classified into four primary categories based on their purpose and lifecycle, following Martin Fowler's classification system.

### Release Toggles

Release toggles hide incomplete features behind flags, allowing code to be merged and deployed to production before the feature is ready for users. These are short-lived, typically existing for days to weeks, and should be removed promptly after the feature is fully released.

**Characteristics**:
- Short lifespan (days to weeks)
- Evaluated at request time
- Simple boolean or percentage-based evaluation
- No user targeting required (typically all-or-nothing)
- Removed after feature release

**Architecture Considerations**: Release toggles need fast evaluation with minimal overhead. They're checked frequently, so performance is critical. Simple boolean checks are sufficient—complex targeting isn't needed.

### Experiment Toggles

Experiment toggles enable A/B testing and experimentation by showing different experiences to different user segments. These support data-driven decision making and require consistent evaluation per user session.

**Characteristics**:
- Short lifespan (days to weeks, until experiment concludes)
- Consistent per-user evaluation (same user sees same variant)
- Percentage-based rollouts or explicit user targeting
- Statistical analysis of outcomes
- Removed after experiment concludes

**Architecture Considerations**: Experiment toggles require consistent user assignment. The same user must see the same variant throughout their session. This typically requires hashing user identifiers to ensure deterministic assignment. Evaluation must be fast enough to not impact request latency.

### Ops Toggles

Ops toggles provide operational control over system behavior, allowing teams to disable expensive features during high load, implement kill switches, or expose circuit breakers as toggles. These are long-lived and critical for system reliability.

**Characteristics**:
- Long lifespan (weeks to months or permanent)
- Evaluated at request time
- Simple boolean evaluation
- Changed infrequently but need instant effect when changed
- Critical for system reliability

**Architecture Considerations**: Ops toggles must support instant changes without code deployment. When a system is under stress, teams need immediate control. These toggles should default to "on" (safe state is to keep features enabled) and should be highly available—if the toggle service is down, features should remain enabled.

### Permission Toggles

Permission toggles control feature access based on user roles, plans, tenants, or other business rules. These enable product differentiation, early access programs, and tiered feature availability.

**Characteristics**:
- Long lifespan (weeks to months or permanent)
- Evaluated at request time with user context
- Complex targeting rules (user attributes, roles, plans, tenants)
- Tied to business rules and product strategy
- Changed based on business needs

**Architecture Considerations**: Permission toggles require rich context (user ID, role, plan, tenant ID, custom attributes). Evaluation logic can be complex, involving multiple conditions. These toggles are often integrated with authorization systems and may cache user attributes for performance.

## Toggle Architecture: Without Commercial Services

For teams without budget for commercial feature flag platforms, several implementation approaches are viable, ranging from simple configuration-based systems to custom database-backed services.

### Database-Backed Toggles

A common approach for teams needing more than simple configuration files is to store toggle definitions and states in a database, typically PostgreSQL. This provides persistence, auditability, and the ability to change toggles without code deployment.

**Database Schema**:

The toggle entity includes name, enabled status, targeting rules, description, and audit fields. Targeting rules are stored as JSON to support flexible evaluation logic.

```sql
CREATE TABLE feature_toggles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT false,
    targeting_rules JSONB,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE INDEX idx_feature_toggles_name ON feature_toggles(name);
CREATE INDEX idx_feature_toggles_enabled ON feature_toggles(enabled);
```

**Targeting Rules Structure**:

Targeting rules support various evaluation strategies:
- Boolean: simple on/off
- Percentage: rollout to X% of users
- User targeting: specific user IDs or user attributes
- Tenant targeting: specific tenant IDs
- Role-based: user roles that have access

```json
{
  "type": "percentage",
  "percentage": 25,
  "seed": "user_id"
}
```

```json
{
  "type": "targeting",
  "users": ["user-123", "user-456"],
  "roles": ["premium", "beta"],
  "tenants": ["tenant-789"]
}
```

**Application-Level Toggle Service**:

A ToggleService evaluates toggles by checking the database, applying targeting rules, and caching results for performance. The service checks toggle state on each request, using context (user ID, tenant ID, role) to evaluate targeting rules.

```kotlin
@Service
class ToggleService(
    private val toggleRepository: ToggleRepository,
    private val cache: Cache<String, Boolean>
) {
    
    fun isEnabled(
        toggleName: String, 
        context: ToggleContext = ToggleContext.default()
    ): Boolean {
        val cacheKey = buildCacheKey(toggleName, context)
        return cache.get(cacheKey) {
            evaluateToggle(toggleName, context)
        }
    }
    
    private fun evaluateToggle(
        toggleName: String, 
        context: ToggleContext
    ): Boolean {
        val toggle = toggleRepository.findByName(toggleName) 
            ?: return getDefaultState(toggleName)
        
        if (!toggle.enabled) {
            return false
        }
        
        return toggle.targetingRules?.let { rules ->
            evaluateTargetingRules(rules, context)
        } ?: true
    }
    
    private fun evaluateTargetingRules(
        rules: JsonNode, 
        context: ToggleContext
    ): Boolean {
        return when (rules["type"].asText()) {
            "percentage" -> evaluatePercentage(rules, context)
            "targeting" -> evaluateTargeting(rules, context)
            else -> true
        }
    }
    
    private fun evaluatePercentage(
        rules: JsonNode, 
        context: ToggleContext
    ): Boolean {
        val percentage = rules["percentage"].asInt()
        val seed = rules["seed"].asText("user_id")
        val hashValue = when (seed) {
            "user_id" -> context.userId?.hashCode() ?: Random.nextInt()
            "tenant_id" -> context.tenantId?.hashCode() ?: Random.nextInt()
            else -> Random.nextInt()
        }
        return (hashValue % 100) < percentage
    }
    
    private fun evaluateTargeting(
        rules: JsonNode, 
        context: ToggleContext
    ): Boolean {
        val users = rules["users"]?.map { it.asText() } ?: emptyList()
        val roles = rules["users"]?.map { it.asText() } ?: emptyList()
        val tenants = rules["tenants"]?.map { it.asText() } ?: emptyList()
        
        return (context.userId in users) ||
               (context.userRole in roles) ||
               (context.tenantId in tenants)
    }
    
    private fun getDefaultState(toggleName: String): Boolean {
        return when {
            toggleName.startsWith("release-") -> false
            toggleName.startsWith("ops-") -> true
            toggleName.startsWith("perm-") -> false
            else -> false
        }
    }
}

data class ToggleContext(
    val userId: String? = null,
    val tenantId: String? = null,
    val userRole: String? = null,
    val customAttributes: Map<String, String> = emptyMap()
) {
    companion object {
        fun default() = ToggleContext()
    }
}
```

**Caching Strategy**:

Toggle evaluation happens on every request, so caching is essential. Cache toggle states with short TTLs (seconds) for release toggles and longer TTLs (minutes) for ops toggles. Implement event-driven invalidation so toggle changes take effect immediately when changed in the admin UI.

```kotlin
@EventListener
fun onToggleChanged(event: ToggleChangedEvent) {
    cache.invalidate(event.toggleName)
    // Optionally broadcast to other instances via message queue
}
```

**Admin UI**:

A simple admin interface allows non-engineers to manage toggles. This can be a basic web UI or integration with existing admin tools. The UI should support creating toggles, changing enabled status, configuring targeting rules, and viewing toggle history.

### Configuration-File Toggles

For simpler cases, toggles can be stored in application configuration files (application.yml, environment variables). These are changed via configuration update and application restart. This approach is suitable for ops toggles that change rarely and don't require complex targeting.

**Spring Boot Implementation**:

```yaml
feature-toggles:
  release-billing-v2-invoice-page: false
  ops-disable-email-notifications: false
  perm-premium-advanced-reports: true
```

```kotlin
@ConfigurationProperties(prefix = "feature-toggles")
data class FeatureToggleConfig(
    val toggles: Map<String, Boolean> = emptyMap()
)

@Service
class ConfigToggleService(
    private val config: FeatureToggleConfig
) {
    fun isEnabled(toggleName: String): Boolean {
        return config.toggles[toggleName] ?: false
    }
}
```

**Startup-Time Toggles**:

For toggles that control which beans are created at startup, use Spring Boot's `@ConditionalOnProperty`:

```kotlin
@Configuration
class FeatureConfiguration {
    
    @Bean
    @ConditionalOnProperty(
        name = "feature-toggles.release-billing-v2-invoice-page",
        havingValue = "true"
    )
    fun billingV2Service(): BillingV2Service {
        return BillingV2Service()
    }
}
```

**Runtime Toggles**:

For toggles evaluated at request time, use a service with custom annotations:

```kotlin
@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureToggle(val name: String, val defaultEnabled: Boolean = false)

@Aspect
@Component
class FeatureToggleAspect(
    private val toggleService: ToggleService
) {
    @Around("@annotation(featureToggle)")
    fun checkToggle(joinPoint: ProceedingJoinPoint, featureToggle: FeatureToggle): Any? {
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
        return invoiceService.getInvoicesV2()
    }
    
    @GetMapping("/invoices")
    fun getInvoicesLegacy(): List<Invoice> {
        return invoiceService.getInvoicesLegacy()
    }
}
```

**Handler Interceptor for Request-Level Evaluation**:

For toggles that control entire endpoints or request flows, use a HandlerInterceptor:

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

## Toggle Architecture: With Commercial Services

Commercial feature flag platforms like LaunchDarkly provide sophisticated capabilities including SDKs, user targeting, analytics, and audit trails. These platforms handle the infrastructure, allowing teams to focus on using toggles rather than building toggle systems.

### SDK Integration

Commercial platforms provide SDKs that evaluate toggles locally, avoiding API calls on every evaluation. SDKs receive streaming updates when toggles change, providing near-zero latency evaluation with instant toggle changes.

**LaunchDarkly Integration**:

```kotlin
@Configuration
class LaunchDarklyConfig {
    
    @Bean
    fun ldClient(): LDClient {
        val config = LDConfig.Builder()
            .streaming(true)
            .build()
        return LDClient("sdk-key", config)
    }
}

@Service
class LaunchDarklyToggleService(
    private val ldClient: LDClient
) {
    fun isEnabled(
        toggleName: String,
        context: ToggleContext
    ): Boolean {
        val user = LDUser.Builder(context.userId ?: "anonymous")
            .custom("tenantId", context.tenantId)
            .custom("role", context.userRole)
            .build()
        
        return ldClient.boolVariation(toggleName, user, false)
    }
}
```

**Streaming Updates**:

SDKs maintain a persistent connection to receive toggle updates in real-time. When a toggle is changed in the LaunchDarkly UI, all SDK instances receive the update within seconds, making changes effective immediately without code deployment.

### User Targeting

Commercial platforms support sophisticated user targeting based on user attributes, custom attributes, percentage rollouts, and complex rules. This enables precise control over who sees which features.

**Targeting Examples**:
- Percentage rollout: 25% of users
- User attributes: users with role "premium" or plan "enterprise"
- Custom attributes: users in specific geographic regions or with specific account ages
- Complex rules: (role = "premium" OR plan = "enterprise") AND region != "EU"

**Consistent Evaluation**:

Platforms ensure consistent evaluation—the same user always sees the same variant. This is critical for experiments where inconsistent assignment would invalidate results.

### Audit Trail

Commercial platforms provide comprehensive audit trails, logging who changed what toggle, when, and why. This is essential for compliance in regulated environments and for debugging issues related to toggle changes.

**Audit Information**:
- User who made the change
- Timestamp of change
- Previous value and new value
- Reason for change (optional comment)
- IP address and user agent

## Frontend Toggle Integration

Feature toggles must be evaluated in frontend applications to control UI rendering, route access, and feature availability. Two primary approaches exist: server-side evaluation with API communication, and client-side evaluation with SDKs.

### Server-Side Evaluation

The backend evaluates toggles and includes toggle states in API responses. The frontend receives a "features" object in the user session or API responses, avoiding exposure of toggle logic to the client.

**Backend API Response**:

```kotlin
@GetMapping("/api/user/session")
fun getSession(): UserSession {
    val context = buildContextFromRequest()
    return UserSession(
        userId = context.userId,
        features = mapOf(
            "release-billing-v2-invoice-page" to toggleService.isEnabled(
                "release-billing-v2-invoice-page", 
                context
            ),
            "perm-premium-advanced-reports" to toggleService.isEnabled(
                "perm-premium-advanced-reports", 
                context
            )
        )
    )
}
```

**Vue 3 Integration**:

```typescript
// composables/useFeatureToggle.ts
export function useFeatureToggle() {
  const session = useSession()
  
  const isEnabled = (toggleName: string): boolean => {
    return session.value?.features?.[toggleName] ?? false
  }
  
  return { isEnabled }
}

// Component usage
<script setup lang="ts">
import { useFeatureToggle } from '@/composables/useFeatureToggle'

const { isEnabled } = useFeatureToggle()

const showNewInvoicePage = isEnabled('release-billing-v2-invoice-page')
</script>

<template>
  <InvoicePageV2 v-if="showNewInvoicePage" />
  <InvoicePageLegacy v-else />
</template>
```

**React Integration**:

```typescript
// hooks/useFeatureToggle.ts
export function useFeatureToggle() {
  const session = useSession()
  
  const isEnabled = (toggleName: string): boolean => {
    return session?.features?.[toggleName] ?? false
  }
  
  return { isEnabled }
}

// Component usage
function InvoicePage() {
  const { isEnabled } = useFeatureToggle()
  const showNewInvoicePage = isEnabled('release-billing-v2-invoice-page')
  
  return showNewInvoicePage ? <InvoicePageV2 /> : <InvoicePageLegacy />
}
```

**Route Guards**:

```typescript
// Vue Router guard
router.beforeEach((to, from, next) => {
  const { isEnabled } = useFeatureToggle()
  
  if (to.meta.requiresFeature && !isEnabled(to.meta.requiresFeature)) {
    next({ name: 'feature-unavailable' })
  } else {
    next()
  }
})

// React Router guard
function FeatureRoute({ feature, children }) {
  const { isEnabled } = useFeatureToggle()
  
  if (!isEnabled(feature)) {
    return <Navigate to="/feature-unavailable" />
  }
  
  return children
}
```

### Client-Side Evaluation

Commercial platforms provide frontend SDKs that evaluate toggles client-side with streaming updates. This approach is more flexible but exposes toggle configuration to the client.

**LaunchDarkly Vue Integration**:

```typescript
// plugins/launchdarkly.ts
import { LDClient, LDUser } from 'launchdarkly-js-client-sdk'

export default {
  install(app: App) {
    const ldClient = LDClient.initialize('client-id', {
      key: 'user-key',
      anonymous: true
    })
    
    app.provide('ldClient', ldClient)
  }
}

// composables/useLaunchDarkly.ts
export function useLaunchDarkly() {
  const ldClient = inject<LDClient>('ldClient')
  
  const variation = (toggleName: string, defaultValue: boolean): boolean => {
    return ldClient?.variation(toggleName, defaultValue) ?? defaultValue
  }
  
  return { variation }
}
```

**Code Splitting by Feature**:

For large features, use dynamic imports to split code by feature toggle:

```typescript
// Vue
const InvoicePageV2 = defineAsyncComponent(() => 
  isEnabled('release-billing-v2-invoice-page') 
    ? import('./InvoicePageV2.vue')
    : Promise.resolve(null)
)

// React
const InvoicePageV2 = lazy(() => 
  isEnabled('release-billing-v2-invoice-page')
    ? import('./InvoicePageV2')
    : Promise.resolve({ default: () => null })
)
```

## Toggle Storage and Evaluation

### Evaluation at Request Time

Toggles are evaluated at request time, checking toggle state for each incoming request. Context includes user ID, tenant ID, role, and request metadata. This ensures that toggle state reflects current configuration and user context.

**Context Building**:

```kotlin
fun buildContextFromRequest(request: HttpServletRequest): ToggleContext {
    val authentication = SecurityContextHolder.getContext().authentication
    val user = authentication?.principal as? UserDetails
    
    return ToggleContext(
        userId = user?.username,
        tenantId = extractTenantId(request),
        userRole = user?.authorities?.firstOrNull()?.authority,
        customAttributes = extractCustomAttributes(request)
    )
}
```

### Caching Strategy

Toggle evaluation happens frequently, so caching is essential. Cache toggle states with appropriate TTLs based on toggle category:

- **Release toggles**: Short TTL (1-5 seconds) for fast propagation of changes
- **Ops toggles**: Longer TTL (1-5 minutes) since they change infrequently
- **Permission toggles**: Medium TTL (10-30 seconds) balancing freshness and performance

**Event-Driven Invalidation**:

When toggles change, invalidate cache entries immediately. For distributed systems, broadcast invalidation events via message queue:

```kotlin
@EventListener
fun onToggleChanged(event: ToggleChangedEvent) {
    cache.invalidate(event.toggleName)
    messageQueue.publish(ToggleInvalidationEvent(event.toggleName))
}

@KafkaListener(topics = ["toggle-invalidation"])
fun handleToggleInvalidation(event: ToggleInvalidationEvent) {
    cache.invalidate(event.toggleName)
}
```

### Consistency

Users must see consistent toggle state throughout their session. For percentage rollouts, use user ID as the hash seed (not random per request) to ensure deterministic assignment:

```kotlin
fun evaluatePercentage(
    percentage: Int,
    seed: String,
    context: ToggleContext
): Boolean {
    val hashValue = when (seed) {
        "user_id" -> context.userId?.hashCode() ?: 0
        "tenant_id" -> context.tenantId?.hashCode() ?: 0
        else -> Random.nextInt()
    }
    return (Math.abs(hashValue) % 100) < percentage
}
```

This ensures that user-123 always sees the same variant (on or off) throughout their session, regardless of how many requests they make.

## Architecture Patterns Summary

The choice of architecture depends on team needs, budget, and scale:

**Configuration-File Toggles**: Simple, no infrastructure, suitable for < 5 toggles, no targeting needed.

**Database-Backed Service**: Moderate complexity, requires database and admin UI, suitable for 5-20 toggles, basic targeting, no commercial budget.

**Commercial Platform**: Managed service, sophisticated capabilities, suitable for 20+ toggles, advanced targeting, experimentation, audit requirements, budget available.

All approaches can evolve—teams can start with configuration files and migrate to database-backed or commercial platforms as needs grow. The key is to implement toggle evaluation consistently and plan for toggle removal from day one.
