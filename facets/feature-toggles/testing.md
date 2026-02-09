# Feature Toggles: Testing

## Contents

- [Testing Both Toggle States](#testing-both-toggle-states)
- [Default State Testing](#default-state-testing)
- [Combinatorial Testing](#combinatorial-testing)
- [Testing Progressive Rollout](#testing-progressive-rollout)
- [Integration Testing with Toggles](#integration-testing-with-toggles)
- [Testing Toggle Cleanup](#testing-toggle-cleanup)
- [Load Testing Toggle Evaluation](#load-testing-toggle-evaluation)
- [Testing Commercial Platform Integration](#testing-commercial-platform-integration)
- [Toggle State Management in Tests](#toggle-state-management-in-tests)
- [Testing Strategy Summary](#testing-strategy-summary)

Testing feature toggles requires strategies that account for multiple toggle states, toggle interactions, and the fact that both toggle-on and toggle-off paths are production code. This document covers comprehensive testing approaches for toggle-enabled features.

## Testing Both Toggle States

Every feature toggle creates two code paths: one when the toggle is enabled and one when it's disabled. Both paths are production code, and bugs in either path affect users. Testing must cover both states.

**Toggle-On Testing**: Verify that the feature works correctly when the toggle is enabled. This includes functionality, performance, integration with other systems, and user experience. This is typically the primary test case since it represents the new feature.

**Toggle-Off Testing**: Verify that the system behaves correctly when the toggle is disabled. This includes:
- The legacy code path still works (if applicable)
- No errors or exceptions are thrown
- UI doesn't show broken elements or missing components
- API endpoints return appropriate responses (404, fallback data, etc.)
- No performance degradation from toggle checks

**Example Test Structure**:

```kotlin
@SpringBootTest
class InvoiceServiceTest {
    
    @Autowired
    private lateinit var toggleService: ToggleService
    
    @Autowired
    private lateinit var invoiceService: InvoiceService
    
    @Test
    fun `invoice service works with toggle enabled`() {
        toggleService.setEnabled("release-billing-v2-invoice-page", true)
        
        val invoices = invoiceService.getInvoices()
        
        assertThat(invoices).isNotEmpty()
        assertThat(invoices[0].format).isEqualTo("v2")
    }
    
    @Test
    fun `invoice service works with toggle disabled`() {
        toggleService.setEnabled("release-billing-v2-invoice-page", false)
        
        val invoices = invoiceService.getInvoices()
        
        assertThat(invoices).isNotEmpty()
        assertThat(invoices[0].format).isEqualTo("legacy")
    }
}
```

**Frontend Testing**:

```typescript
// Vue component test
describe('InvoicePage', () => {
  it('renders v2 page when toggle is enabled', async () => {
    const mockSession = {
      features: { 'release-billing-v2-invoice-page': true }
    }
    vi.mocked(useSession).mockReturnValue(mockSession)
    
    const wrapper = mount(InvoicePage)
    
    expect(wrapper.findComponent(InvoicePageV2).exists()).toBe(true)
    expect(wrapper.findComponent(InvoicePageLegacy).exists()).toBe(false)
  })
  
  it('renders legacy page when toggle is disabled', async () => {
    const mockSession = {
      features: { 'release-billing-v2-invoice-page': false }
    }
    vi.mocked(useSession).mockReturnValue(mockSession)
    
    const wrapper = mount(InvoicePage)
    
    expect(wrapper.findComponent(InvoicePageV2).exists()).toBe(false)
    expect(wrapper.findComponent(InvoicePageLegacy).exists()).toBe(true)
  })
})
```

## Default State Testing

When toggle evaluation fails (service unavailable, configuration missing, network error), the system must default to a safe state. Testing must verify that default behavior is correct and doesn't expose incomplete features or disable critical functionality.

**Safe Defaults by Toggle Category**:
- **Release toggles**: Default to `false` (off). Don't expose incomplete features if toggle service fails.
- **Ops toggles**: Default to `true` (on). Don't disable working features if toggle service fails.
- **Permission toggles**: Default to `false` (off). Don't grant access if authorization can't be verified.

**Testing Toggle Service Failure**:

```kotlin
@Test
fun `release toggle defaults to off when service unavailable`() {
    val toggleService = MockToggleService()
    toggleService.simulateFailure()
    
    val result = toggleService.isEnabled("release-billing-v2-invoice-page")
    
    assertThat(result).isFalse()
}

@Test
fun `ops toggle defaults to on when service unavailable`() {
    val toggleService = MockToggleService()
    toggleService.simulateFailure()
    
    val result = toggleService.isEnabled("ops-disable-email-notifications")
    
    assertThat(result).isTrue()
}
```

**Testing Missing Configuration**:

```kotlin
@Test
fun `unknown toggle defaults to safe state`() {
    val toggleService = ToggleService(emptyRepository)
    
    val releaseResult = toggleService.isEnabled("release-unknown-feature")
    val opsResult = toggleService.isEnabled("ops-unknown-feature")
    
    assertThat(releaseResult).isFalse()
    assertThat(opsResult).isTrue()
}
```

**Testing Network Failures**:

For commercial platforms, test behavior when the SDK can't connect:

```kotlin
@Test
fun `launchdarkly defaults to safe state on network failure`() {
    val ldClient = LDClient.builder("sdk-key")
        .offline(true) // Simulate network failure
        .build()
    
    val result = ldClient.boolVariation("release-feature", user, false)
    
    assertThat(result).isFalse() // Returns default value
}
```

## Combinatorial Testing

With N toggles, there are 2^N possible combinations. Testing all combinations becomes impractical quickly (10 toggles = 1,024 combinations). Use risk-based testing to focus on critical combinations.

**Critical Combinations**:
- **All toggles off**: Baseline state, all legacy code paths
- **All toggles on**: All new features enabled, maximum complexity
- **Individual toggles**: Each toggle enabled independently, others off
- **Known interactions**: Toggles that are known to interact (e.g., both billing v2 and payment v2 enabled)

**Example Combinatorial Test**:

```kotlin
@ParameterizedTest
@MethodSource("toggleCombinations")
fun `invoice service works with toggle combinations`(
    billingV2Enabled: Boolean,
    paymentV2Enabled: Boolean
) {
    toggleService.setEnabled("release-billing-v2-invoice-page", billingV2Enabled)
    toggleService.setEnabled("release-payment-v2-checkout", paymentV2Enabled)
    
    val invoices = invoiceService.getInvoices()
    
    assertThat(invoices).isNotEmpty()
    // Verify behavior for this combination
}

companion object {
    @JvmStatic
    fun toggleCombinations() = listOf(
        Arguments.of(false, false), // All off
        Arguments.of(true, false),  // Billing v2 only
        Arguments.of(false, true),  // Payment v2 only
        Arguments.of(true, true)    // All on
    )
}
```

**Risk-Based Selection**:

Focus testing on combinations that:
- Are likely to be active simultaneously in production
- Have known interactions or dependencies
- Control critical user flows
- Have high business impact

**Property-Based Testing**:

For complex toggle interactions, use property-based testing to generate combinations:

```kotlin
@Property
fun `invoice service never throws exception regardless of toggle state`(
    @ForAll toggles: Map<String, Boolean>
) {
    toggles.forEach { (name, enabled) ->
        toggleService.setEnabled(name, enabled)
    }
    
    assertThatNoException().isThrownBy {
        invoiceService.getInvoices()
    }
}
```

## Testing Progressive Rollout

Percentage-based rollouts require testing to verify that:
- The distribution matches the configured percentage
- Users are consistently assigned (same user always sees same variant)
- The hash function produces expected distribution

**Testing Distribution**:

```kotlin
@Test
fun `percentage rollout produces expected distribution`() {
    val toggleName = "release-billing-v2-invoice-page"
    toggleService.configurePercentageRollout(toggleName, 25)
    
    val results = (1..1000).map { userId ->
        val context = ToggleContext(userId = "user-$userId")
        toggleService.isEnabled(toggleName, context)
    }
    
    val enabledCount = results.count { it }
    val percentage = (enabledCount.toDouble() / 1000) * 100
    
    assertThat(percentage).isBetween(20.0, 30.0) // Allow 5% variance
}
```

**Testing Consistency**:

```kotlin
@Test
fun `same user always sees same toggle state`() {
    val toggleName = "release-billing-v2-invoice-page"
    val userId = "user-123"
    val context = ToggleContext(userId = userId)
    
    val results = (1..100).map {
        toggleService.isEnabled(toggleName, context)
    }
    
    val uniqueResults = results.distinct()
    assertThat(uniqueResults).hasSize(1) // All results should be the same
}
```

**Testing Hash Function**:

```kotlin
@Test
fun `hash function produces consistent results`() {
    val userId = "user-123"
    val hash1 = userId.hashCode() % 100
    val hash2 = userId.hashCode() % 100
    
    assertThat(hash1).isEqualTo(hash2)
}
```

## Integration Testing with Toggles

Integration tests should verify that features work correctly with toggles in their expected production state. CI should test both the current state (toggles as configured in production) and upcoming states (toggles flipped to their next state).

**Testing Current Production State**:

```kotlin
@SpringBootTest
@TestPropertySource(properties = [
    "feature-toggles.release-billing-v2-invoice-page=false",
    "feature-toggles.release-payment-v2-checkout=false"
])
class InvoiceIntegrationTest {
    
    @Test
    fun `invoice flow works with current production toggles`() {
        // Test with toggles as they are in production
        val response = restTemplate.getForEntity("/api/invoices", InvoiceList::class.java)
        
        assertThat(response.statusCode).isEqualTo(HttpStatus.OK)
        assertThat(response.body?.invoices).isNotEmpty()
    }
}
```

**Testing Upcoming State**:

```kotlin
@Test
fun `invoice flow works with toggles flipped for next release`() {
    toggleService.setEnabled("release-billing-v2-invoice-page", true)
    toggleService.setEnabled("release-payment-v2-checkout", true)
    
    val response = restTemplate.getForEntity("/api/invoices", InvoiceList::class.java)
    
    assertThat(response.statusCode).isEqualTo(HttpStatus.OK)
    assertThat(response.body?.invoices).isNotEmpty()
    // Verify v2 behavior
}
```

**End-to-End Testing**:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class InvoiceE2ETest {
    
    @Autowired
    private lateinit var mockMvc: MockMvc
    
    @Test
    fun `end-to-end invoice flow with toggle enabled`() {
        toggleService.setEnabled("release-billing-v2-invoice-page", true)
        
        mockMvc.perform(get("/invoices"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].format").value("v2"))
    }
    
    @Test
    fun `end-to-end invoice flow with toggle disabled`() {
        toggleService.setEnabled("release-billing-v2-invoice-page", false)
        
        mockMvc.perform(get("/invoices"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].format").value("legacy"))
    }
}
```

## Testing Toggle Cleanup

After a toggle is removed, verify that:
- The feature works without the toggle check
- No dead code remains
- No references to the removed toggle exist

**Testing Toggle Removal**:

```kotlin
@Test
fun `feature works after toggle removal`() {
    // Simulate toggle removal by not checking toggle
    val invoices = invoiceService.getInvoicesWithoutToggle()
    
    assertThat(invoices).isNotEmpty()
    assertThat(invoices[0].format).isEqualTo("v2") // Should always be v2 now
}
```

**Static Analysis for Toggle References**:

Use lint rules or static analysis to detect references to removed toggles:

```kotlin
// Custom lint rule
class RemovedToggleDetector : Detector() {
    override fun visitMethodCall(context: JavaContext, node: UCallExpression) {
        if (node.methodName == "isEnabled") {
            val toggleName = node.valueArguments[0].evaluate() as? String
            if (toggleName in removedToggles) {
                context.report(
                    ISSUE,
                    node,
                    context.getLocation(node),
                    "Reference to removed toggle: $toggleName"
                )
            }
        }
    }
}
```

**Testing Toggle Removal Process**:

```kotlin
@Test
fun `toggle removal process works correctly`() {
    // 1. Verify toggle exists
    assertThat(toggleService.isEnabled("release-billing-v2-invoice-page")).isTrue()
    
    // 2. Remove toggle code
    // (Manual step: remove toggle checks from code)
    
    // 3. Verify feature works without toggle
    val invoices = invoiceService.getInvoices()
    assertThat(invoices).isNotEmpty()
    
    // 4. Verify no toggle references remain
    val codebase = scanCodebaseForToggleReferences("release-billing-v2-invoice-page")
    assertThat(codebase).isEmpty()
}
```

## Load Testing Toggle Evaluation

Toggle evaluation happens on every request, so it must not add significant latency. Load testing verifies that toggle evaluation doesn't become a bottleneck.

**Performance Testing**:

```kotlin
@Test
fun `toggle evaluation adds minimal latency`() {
    val iterations = 10_000
    val startTime = System.nanoTime()
    
    repeat(iterations) {
        toggleService.isEnabled("release-billing-v2-invoice-page", context)
    }
    
    val duration = System.nanoTime() - startTime
    val averageLatency = duration / iterations
    
    assertThat(averageLatency).isLessThan(1_000_000) // Less than 1ms
}
```

**Database Query Testing**:

For database-backed toggles, verify that caching prevents per-request database queries:

```kotlin
@Test
fun `toggle evaluation uses cache not database`() {
    val queryCount = countDatabaseQueries()
    
    repeat(100) {
        toggleService.isEnabled("release-billing-v2-invoice-page", context)
    }
    
    val finalQueryCount = countDatabaseQueries()
    assertThat(finalQueryCount - queryCount).isLessThan(5) // Only initial load queries
}
```

**P99 Latency Testing**:

```kotlin
@Test
fun `toggle evaluation p99 latency is acceptable`() {
    val latencies = (1..10_000).map {
        val start = System.nanoTime()
        toggleService.isEnabled("release-billing-v2-invoice-page", context)
        System.nanoTime() - start
    }.sorted()
    
    val p99Index = (latencies.size * 0.99).toInt()
    val p99Latency = latencies[p99Index]
    
    assertThat(p99Latency).isLessThan(5_000_000) // P99 less than 5ms
}
```

## Testing Commercial Platform Integration

When using commercial platforms like LaunchDarkly, use test SDKs or mocks rather than calling the actual API from CI. This avoids flakiness, slowness, and costs.

**LaunchDarkly Test SDK**:

```kotlin
@Test
fun `feature works with launchdarkly test SDK`() {
    val testData = TestData.dataSource()
        .flag("release-billing-v2-invoice-page")
        .variationForUser("user-123", true)
        .build()
    
    val ldClient = LDClient.builder("test-sdk-key")
        .updateProcessor(testData)
        .build()
    
    val toggleService = LaunchDarklyToggleService(ldClient)
    val result = toggleService.isEnabled("release-billing-v2-invoice-page", context)
    
    assertThat(result).isTrue()
}
```

**Mocking Commercial SDKs**:

```kotlin
@Test
fun `feature works with mocked launchdarkly`() {
    val mockLdClient = mock<LDClient>()
    whenever(mockLdClient.boolVariation(any(), any(), any())).thenReturn(true)
    
    val toggleService = LaunchDarklyToggleService(mockLdClient)
    val result = toggleService.isEnabled("release-billing-v2-invoice-page", context)
    
    assertThat(result).isTrue()
}
```

**Testing SDK Failure Handling**:

```kotlin
@Test
fun `feature handles launchdarkly SDK failure gracefully`() {
    val mockLdClient = mock<LDClient>()
    whenever(mockLdClient.boolVariation(any(), any(), any()))
        .thenThrow(RuntimeException("SDK failure"))
    
    val toggleService = LaunchDarklyToggleService(mockLdClient)
    val result = toggleService.isEnabled("release-billing-v2-invoice-page", context)
    
    assertThat(result).isFalse() // Defaults to safe state
}
```

## Toggle State Management in Tests

Tests must reset toggle state between runs to avoid test pollution. Toggle state from one test shouldn't affect another test.

**Test Isolation**:

```kotlin
@SpringBootTest
class ToggleAwareTest {
    
    @Autowired
    private lateinit var toggleService: ToggleService
    
    @BeforeEach
    fun resetToggles() {
        toggleService.resetAllToggles()
    }
    
    @AfterEach
    fun cleanupToggles() {
        toggleService.resetAllToggles()
    }
}
```

**Toggle Fixtures**:

```kotlin
object ToggleFixtures {
    fun withToggleEnabled(toggleName: String, block: () -> Unit) {
        val originalState = toggleService.isEnabled(toggleName)
        try {
            toggleService.setEnabled(toggleName, true)
            block()
        } finally {
            toggleService.setEnabled(toggleName, originalState)
        }
    }
}

// Usage
ToggleFixtures.withToggleEnabled("release-billing-v2-invoice-page") {
    // Test code
}
```

**Database Rollback**:

For database-backed toggles, use transactions to roll back changes:

```kotlin
@SpringBootTest
@Transactional
class ToggleDatabaseTest {
    
    @Test
    @Rollback
    fun `toggle changes are rolled back after test`() {
        toggleRepository.save(FeatureToggle(name = "test-toggle", enabled = true))
        // Changes are rolled back automatically
    }
}
```

## Testing Strategy Summary

A comprehensive testing strategy for feature toggles includes:

1. **Unit Tests**: Test toggle evaluation logic, targeting rules, percentage calculations
2. **Integration Tests**: Test features with toggles enabled and disabled
3. **E2E Tests**: Test complete user flows with different toggle states
4. **Combinatorial Tests**: Test critical toggle combinations
5. **Performance Tests**: Verify toggle evaluation doesn't add latency
6. **Cleanup Tests**: Verify toggle removal doesn't break features
7. **Failure Tests**: Verify safe defaults when toggle service fails

All tests should be deterministic, isolated, and fast. Use mocks for commercial platforms, and verify both toggle states for every feature. Track toggle coverage metrics to ensure both code paths are tested.
