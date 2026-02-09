# Testing: Refactoring & Extraction Safety

## Contents

- [Test Coverage as a Safety Net](#test-coverage-as-a-safety-net)
- [Characterization Tests](#characterization-tests)
- [Refactoring Should Not Change Test Behavior](#refactoring-should-not-change-test-behavior)
- [Testing Extraction Boundaries](#testing-extraction-boundaries)
- [Testing the Strangler Fig Pattern](#testing-the-strangler-fig-pattern)
- [Architecture Tests for Enforced Boundaries](#architecture-tests-for-enforced-boundaries)
- [Regression Testing](#regression-testing)
- [Test-Driven Refactoring](#test-driven-refactoring)
- [Refactoring Test Code](#refactoring-test-code)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Test Coverage as a Safety Net

Refactoring without tests is risky. You cannot know if you've broken something until it reaches production. Tests provide a safety net: they verify that behavior remains unchanged after refactoring. Before refactoring, ensure the code under change has adequate test coverage.

Adequate test coverage means tests exercise the code's behavior, not just its existence. Line coverage metrics can be misleading: 100% line coverage doesn't guarantee behavior is tested. Focus on behavior coverage: do tests verify that the code does what it's supposed to do?

If test coverage is inadequate, write tests before refactoring. These tests capture current behavior, creating a safety net. Refactoring can then proceed with confidence: if tests pass, behavior is preserved.

## Characterization Tests

When you inherit code without tests, write characterization tests. These tests capture current behavior, even if that behavior is imperfect. The goal is to document what the code does, not what it should do.

**Example: Characterizing Legacy Payment Processing**

```kotlin
// Legacy code - no tests, complex logic
fun processPayment(amount: Double, paymentMethod: String): PaymentResult {
    // 200 lines of complex logic
    // Unknown edge cases, unclear behavior
}

// Characterization test - captures current behavior
@Test
fun `characterize payment processing - valid credit card`() {
    val result = processPayment(100.0, "credit_card")
    // Assert what actually happens, not what should happen
    assertEquals(PaymentStatus.SUCCESS, result.status)
    assertEquals(100.0, result.amount, 0.01)
    // Capture actual behavior, even if it seems wrong
}

@Test
fun `characterize payment processing - invalid amount`() {
    val result = processPayment(-10.0, "credit_card")
    // Document actual behavior - might return error, might throw exception
    // Test reveals current behavior, enabling safe refactoring
}
```

Write characterization tests by running the code and observing the output. Write a test that asserts that output. The test may assert behavior that seems wrong, but that's acceptable for characterization tests. They document current behavior, enabling safe refactoring.

**Test scenarios for characterization:**
- **Happy path:** Normal inputs produce expected outputs
- **Edge cases:** Boundary values (zero, negative, very large)
- **Error cases:** Invalid inputs, missing data, null values
- **Business rules:** Discount calculations, tax applications, fee structures
- **Integration points:** Database interactions, external API calls, message queue operations

After refactoring, characterization tests should still pass. If they fail, either the refactoring changed behavior (it shouldn't) or the tests were testing implementation details (they shouldn't). Good tests test behavior, not implementation.

Characterization tests are temporary. Once refactoring is complete and behavior is verified, improve the tests. Make them test intended behavior, not just current behavior. However, during refactoring, characterization tests provide the safety net needed to proceed confidently.

## Refactoring Should Not Change Test Behavior

Refactoring changes structure, not behavior. If a refactoring changes test outcomes, something is wrong. Either the refactoring changed behavior (it shouldn't) or the tests were testing implementation details (they shouldn't).

Good tests test behavior, not implementation. They verify that the code produces the correct output for given inputs. They don't care how the code produces that output. This makes tests resilient to refactoring: as long as behavior is preserved, tests pass.

If tests fail after refactoring, investigate. Did the refactoring accidentally change behavior? Or are the tests too coupled to implementation? Fix the refactoring if behavior changed. Fix the tests if they're testing implementation details.

Tests that are too coupled to implementation make refactoring difficult. They break when structure changes, even if behavior is preserved. This creates a disincentive to refactor: developers avoid refactoring to avoid breaking tests. This is backwards: tests should enable refactoring, not prevent it.

## Testing Extraction Boundaries

When extracting a module or service, test the boundary thoroughly. The boundary is the API or interface that clients depend on. This contract must remain stable: clients should not need to change when internals are refactored.

**Example: Testing Extracted Payment Service Boundary**

```kotlin
// Extracted PaymentService interface
interface PaymentService {
    fun processPayment(request: PaymentRequest): PaymentResult
    fun refundPayment(paymentId: String): RefundResult
}

// Boundary tests - test from client perspective
class PaymentServiceBoundaryTest {
    @Test
    fun `processPayment - valid request returns success`() {
        val service = PaymentService()
        val request = PaymentRequest(amount = 100.0, method = "credit_card")
        
        val result = service.processPayment(request)
        
        assertEquals(PaymentStatus.SUCCESS, result.status)
        assertNotNull(result.transactionId)
    }
    
    @Test
    fun `processPayment - invalid amount returns error`() {
        val service = PaymentService()
        val request = PaymentRequest(amount = -10.0, method = "credit_card")
        
        val result = service.processPayment(request)
        
        assertEquals(PaymentStatus.ERROR, result.status)
        assertNotNull(result.errorMessage)
    }
    
    @Test
    fun `processPayment - missing payment method returns error`() {
        val service = PaymentService()
        val request = PaymentRequest(amount = 100.0, method = "")
        
        val result = service.processPayment(request)
        
        assertEquals(PaymentStatus.ERROR, result.status)
    }
    
    // Test side effects - verify database updates, message publishing
    @Test
    fun `processPayment - successful payment creates database record`() {
        val service = PaymentService()
        val request = PaymentRequest(amount = 100.0, method = "credit_card")
        
        service.processPayment(request)
        
        // Verify side effect - database record created
        val record = paymentRepository.findByTransactionId(result.transactionId)
        assertNotNull(record)
    }
}
```

Test the boundary from the client's perspective. Write tests that use the boundary API as clients would. These tests verify that the boundary contract is satisfied. They don't test internal implementation details.

**Test scenarios for extraction boundaries:**
- **Valid inputs:** All valid input combinations produce expected outputs
- **Invalid inputs:** All invalid inputs produce appropriate errors
- **Edge cases:** Boundary values, null inputs, empty inputs
- **Error handling:** Network failures, database failures, external service failures
- **Side effects:** Database updates, message publishing, cache invalidation
- **Concurrency:** Multiple concurrent requests, race conditions
- **Performance:** Response time under load, resource usage

The boundary contract includes inputs, outputs, error cases, and side effects. Test all of these. Verify that valid inputs produce expected outputs. Verify that invalid inputs produce appropriate errors. Verify that side effects occur as expected.

Internal refactoring can change as long as the boundary contract is preserved. Tests of the boundary should continue to pass. Tests of internal implementation may need updates, but boundary tests should remain stable.

## Testing the Strangler Fig Pattern

The Strangler Fig Pattern requires running both old and new implementations in parallel. Testing must verify that both produce equivalent results. Compare outputs, log discrepancies, and only remove the old implementation when confidence is high.

Write comparison tests that exercise both implementations with the same inputs and compare outputs. Log any discrepancies. Investigate discrepancies: are they bugs in the new implementation, or are they acceptable differences?

Comparison tests should cover common cases, edge cases, and error cases. They should exercise the full range of inputs that the system handles. If comparison tests pass consistently, confidence in the new implementation increases.

Monitor production metrics during strangler fig migration. Compare metrics between old and new implementations. If metrics diverge significantly, investigate. The new implementation may have performance issues or behavioral differences.

Gradually increase traffic to the new implementation. Start with a small percentage, monitor metrics, and increase gradually. If issues arise, route traffic back to the old implementation. This enables safe migration with instant rollback.

## Architecture Tests for Enforced Boundaries

After extracting modules, use architecture tests to enforce boundaries. These tests verify that the extracted boundaries are not violated. They prevent regression where developers bypass the new module API and access internals directly.

ArchUnit for Java/Kotlin provides architecture testing capabilities. It can verify that classes in one package don't access classes in another package, except through defined APIs. It can verify that certain annotations are used correctly, or that dependencies flow in the correct direction.

Architecture tests catch violations at build time. They fail the build if boundaries are violated, preventing violations from reaching production. This creates a feedback loop: developers learn about boundaries when they violate them, not when bugs are discovered in production.

Write architecture tests immediately after extracting modules. They document the intended boundaries and prevent accidental violations. As the codebase evolves, architecture tests ensure boundaries remain intact.

## Regression Testing

After refactoring, run the full test suite. Unit tests verify that individual components work correctly. Integration tests verify that components work together. End-to-end tests verify that the system works from a user's perspective.

Different test levels catch different issues. Unit tests catch issues in individual components. Integration tests catch issues in component interactions. End-to-end tests catch issues in user workflows. Run all levels to ensure comprehensive coverage.

Integration and end-to-end tests catch issues that unit tests might miss. Unit tests verify components in isolation, but components may interact in unexpected ways. Integration tests verify these interactions. End-to-end tests verify complete workflows.

Monitor production metrics after deploying refactored code. Even if all tests pass, production behavior may differ. Monitor error rates, response times, and business metrics. If metrics degrade, investigate and rollback if necessary.

## Test-Driven Refactoring

Test-driven development can guide refactoring. Write tests first to define desired behavior, then refactor to achieve that behavior. This ensures that refactoring is driven by tests, not by arbitrary code structure preferences.

However, test-driven refactoring requires existing tests. If tests don't exist, write characterization tests first. Capture current behavior, then refactor. After refactoring, improve tests to verify intended behavior.

Test-driven refactoring is most effective for code-level refactorings. For architecture-level refactorings, tests may need to be written after the new architecture is in place. However, tests should still guide the refactoring: write tests for the new architecture's boundaries and contracts.

## Refactoring Test Code

Test code also needs refactoring. Tests accumulate technical debt just like production code. Long test methods, duplicate test setup, and unclear test names make tests hard to understand and maintain.

Refactor test code using the same techniques as production code. Extract test setup into fixtures or builders. Extract common assertions into helper methods. Use descriptive test names that explain what is being tested.

However, test refactoring has different priorities than production refactoring. Test code should prioritize clarity over performance. It's okay for test code to be slower or more verbose if it's clearer. Tests are read more often than they're written, so clarity is paramount.

Test refactoring should preserve test behavior, just like production refactoring. Tests should still verify the same behavior after refactoring. If test behavior changes, ensure it's intentional and documented.

## QA and Test Engineer Perspective

**Risk-Based Testing Priorities**

Prioritize refactoring testing based on change impact and business risk. Critical paths requiring immediate coverage include:

**High-Risk Refactorings:**
- **Payment processing:** Any refactoring affecting payment logic requires comprehensive testing. Test all payment methods, error scenarios, and edge cases. Verify transaction integrity and audit trail preservation.
- **Authentication and authorization:** Security-critical refactorings require extensive testing. Test all authentication flows, session management, token validation, and permission checks. Verify no security regressions.
- **Data migration:** Refactorings that change data structures require migration testing. Test data integrity, backward compatibility, and rollback procedures.

**Medium-Risk Refactorings:**
- **API endpoints:** Refactorings affecting API contracts require contract testing. Verify request/response formats, error codes, and backward compatibility.
- **Business logic:** Refactorings affecting core business rules require business logic testing. Verify calculations, validations, and workflows remain correct.

**Low-Risk Refactorings:**
- **UI components:** Refactorings affecting presentation logic require visual regression testing. Verify UI appearance and behavior remain consistent.
- **Utility functions:** Refactorings affecting helper functions require unit testing. Verify function behavior remains unchanged.

**Test Scenarios for Refactoring**

**Before Refactoring:**
1. **Baseline testing:** Establish test coverage baseline. Run full test suite and document current behavior.
2. **Characterization testing:** Write tests capturing current behavior, especially for untested code.
3. **Integration testing:** Verify end-to-end flows work correctly before refactoring.

**During Refactoring:**
1. **Incremental testing:** After each refactoring step, run tests to verify behavior preserved.
2. **Regression testing:** Run full test suite after each significant change.
3. **Smoke testing:** Quick validation that critical paths still work.

**After Refactoring:**
1. **Comprehensive testing:** Full test suite execution to verify no regressions.
2. **Performance testing:** Verify refactoring didn't introduce performance regressions.
3. **Exploratory testing:** Manual testing to discover edge cases automated tests might miss.

**Specific Test Scenarios**

**Extract Method Refactoring:**
- Verify extracted method produces same output as original code
- Test extracted method independently
- Verify all callers still work correctly
- Test edge cases that might be affected by extraction

**Extract Class Refactoring:**
- Verify extracted class maintains same behavior
- Test extracted class independently
- Verify original class delegates correctly
- Test interaction between original and extracted classes

**Extract Service Refactoring:**
- Verify service API matches original functionality
- Test service independently with mocked dependencies
- Verify all clients still work correctly
- Test service error handling and failure scenarios
- Verify data consistency across service boundaries

**Strangler Fig Pattern Testing:**
- Test both old and new implementations produce equivalent results
- Verify feature flags route correctly
- Test gradual migration scenarios
- Verify rollback procedures work correctly
- Test monitoring and alerting for both implementations
