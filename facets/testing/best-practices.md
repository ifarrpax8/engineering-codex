# Testing: Best Practices

## Contents

- [Test Structure](#test-structure)
- [Test Naming](#test-naming)
- [Test Independence](#test-independence)
- [What to Test vs What Not to Test](#what-to-test-vs-what-not-to-test)
- [Anti-Patterns](#anti-patterns)
- [Cloud Integration Testing](#cloud-integration-testing)
- [Stack-Specific Callouts](#stack-specific-callouts)

## Test Structure

### Arrange-Act-Assert (AAA)

The AAA pattern structures unit tests into three clear sections:

```kotlin
@Test
fun `should apply discount when customer has premium membership`() {
    // Arrange: Set up test data and dependencies
    val customer = Customer(role = Role.PREMIUM)
    val order = Order(amount = 100.0)
    val discountService = DiscountService()
    
    // Act: Execute the behavior under test
    val result = discountService.calculateDiscount(customer, order)
    
    // Assert: Verify the expected outcome
    assertEquals(20.0, result)
}
```

**Benefits**:
- Clear separation of concerns
- Easy to understand test flow
- Consistent structure across tests
- Easy to identify what's being tested

**Variations**:
- **Given-When-Then (GWT)**: BDD-style, more narrative
- **Setup-Execute-Verify**: Alternative naming
- **Arrange-Act-Assert-Cleanup**: When cleanup is needed

**Best Practice**: Use AAA for all unit tests. It makes tests readable and maintainable.

### Given-When-Then (GWT)

The GWT pattern structures BDD-style tests:

```kotlin
@Test
fun `should apply discount when customer has premium membership`() {
    // Given: Preconditions
    val customer = Customer(role = Role.PREMIUM)
    val order = Order(amount = 100.0)
    
    // When: Action
    val result = discountService.calculateDiscount(customer, order)
    
    // Then: Expected outcome
    assertEquals(20.0, result)
}
```

**Benefits**:
- More narrative, business-friendly
- Aligns with BDD specifications
- Easy to translate to acceptance criteria

**When to Use**: BDD-style tests, acceptance tests, tests that align with user stories.

### One Logical Assertion Per Test

**Principle**: Each test should verify one behavior or outcome

**Multiple Physical Assertions Are Fine**:
```kotlin
@Test
fun `should create order with correct properties`() {
    val order = orderService.createOrder(items, customer)
    
    // Multiple assertions verifying one logical outcome: order creation
    assertNotNull(order.id)
    assertEquals(customer.id, order.customerId)
    assertEquals(items.size, order.items.size)
    assertTrue(order.createdAt.isBefore(Instant.now()))
}
```

**Multiple Logical Assertions Are Not Fine**:
```kotlin
@Test
fun `should calculate discount and apply tax`() {  // Testing two behaviors!
    val discount = discountService.calculateDiscount(customer, order)
    val tax = taxService.calculateTax(order)
    
    assertEquals(20.0, discount)  // First behavior
    assertEquals(10.0, tax)       // Second behavior - should be separate test
}
```

**Benefits**:
- Clear test purpose
- Easier to identify what failed
- Easier to understand test intent
- Better test reports

**Best Practice**: One logical assertion per test. Multiple physical assertions are fine if they verify one behavior.

### Setup and Teardown Patterns

**JUnit 5 Annotations**:
```kotlin
class OrderServiceTest {
    @BeforeEach
    fun setUp() {
        // Runs before each test
        // Use for test-specific setup
    }
    
    @AfterEach
    fun tearDown() {
        // Runs after each test
        // Use for cleanup (close resources, reset state)
    }
    
    @BeforeAll
    fun setUpAll() {
        // Runs once before all tests
        // Use for expensive setup (database connections, test containers)
    }
    
    @AfterAll
    fun tearDownAll() {
        // Runs once after all tests
        // Use for expensive cleanup
    }
}
```

**Best Practices**:
- Use `@BeforeEach` for test-specific setup (creating test data)
- Use `@AfterEach` for cleanup (closing resources, resetting state)
- Use `@BeforeAll`/`@AfterAll` sparingly (only for expensive operations)
- Prefer test fixtures over `@BeforeEach` when possible (more explicit)

**Alternative: Test Fixtures**:
```kotlin
fun createOrderService(): OrderService {
    val repository = InMemoryOrderRepository()
    return OrderService(repository)
}

@Test
fun `should create order`() {
    val service = createOrderService()  // Explicit setup
    // Test code
}
```

**Benefits**: More explicit, easier to understand test dependencies.

## Test Naming

### Descriptive Names That Explain Behavior

**Good Test Names**:
- `should_apply_discount_when_customer_has_premium_membership()`
- `should_reject_payment_when_card_is_expired()`
- `should_calculate_shipping_based_on_weight_and_distance()`
- `should_throw_exception_when_order_amount_is_negative()`

**Bad Test Names**:
- `testCalculateTotal()` — What scenario? What's expected?
- `testUser()` — Too vague
- `test1()`, `test2()` — Meaningless
- `testOrderService()` — Doesn't describe behavior

### Convention: `should [expected behavior] when [condition]`

**Format**: `should_[expected_behavior]_when_[condition]`

**Examples**:
- `should_return_discount_when_customer_is_premium()`
- `should_throw_validation_error_when_email_is_invalid()`
- `should_apply_free_shipping_when_order_exceeds_threshold()`

**Benefits**:
- Self-documenting
- Easy to understand test purpose
- Better test reports
- Aligns with BDD style

**Alternative Conventions**:
- `[method]_[scenario]_[expected_result]`: `calculateDiscount_premiumCustomer_returns20Percent()`
- `[scenario]_should_[expected_result]`: `premiumCustomer_should_receiveDiscount()`

**Best Practice**: Choose a convention and stick to it. The `should_when` format is most readable.

### Avoid Generic Names

**Generic Names to Avoid**:
- `test1()`, `test2()`
- `testMethod()`
- `testOrder()`
- `testService()`

**Why They're Bad**:
- Don't explain what's being tested
- Don't explain expected outcome
- Hard to find relevant tests
- Hard to understand test failures

**Best Practice**: Every test name should explain what behavior is being tested and what the expected outcome is.

## Test Independence

### No Shared Mutable State Between Tests

**Problem**: Tests that share mutable state interfere with each other

```kotlin
// BAD: Shared mutable state
var globalCounter = 0

@Test
fun test1() {
    globalCounter++
    assertEquals(1, globalCounter)  // Fails if test2 runs first
}

@Test
fun test2() {
    globalCounter++
    assertEquals(1, globalCounter)  // Fails if test1 runs first
}
```

**Solution**: Each test should have its own state

```kotlin
// GOOD: Isolated state
@Test
fun test1() {
    val counter = 0
    val result = counter + 1
    assertEquals(1, result)  // Always passes
}

@Test
fun test2() {
    val counter = 0
    val result = counter + 1
    assertEquals(1, result)  // Always passes
}
```

**Best Practice**: Never share mutable state between tests. Use fresh test data for each test.

### Each Test Must Pass in Isolation

**Requirement**: Tests should pass when run alone, not just when run together

**How to Verify**:
- Run tests individually
- Run tests in random order
- Run tests in parallel

**Red Flags**:
- Test passes in suite but fails alone
- Test requires specific execution order
- Test depends on side effects from other tests

**Best Practice**: Every test should be independent. Use setup/teardown to ensure clean state.

### Avoid Test Ordering Dependencies

**Problem**: Tests that depend on execution order

```kotlin
// BAD: Test order dependency
@Test
@Order(1)
fun testCreateUser() {
    userService.createUser(user)  // Must run first
}

@Test
@Order(2)
fun testUpdateUser() {
    userService.updateUser(userId, updates)  // Depends on testCreateUser
}
```

**Solution**: Each test should set up its own data

```kotlin
// GOOD: Independent tests
@Test
fun testCreateUser() {
    val user = userService.createUser(userData)
    assertNotNull(user.id)
}

@Test
fun testUpdateUser() {
    val user = userService.createUser(userData)  // Setup in test
    val updated = userService.updateUser(user.id, updates)
    assertEquals(updates.name, updated.name)
}
```

**Best Practice**: Never depend on test execution order. Each test should be self-contained.

### Use Fresh Test Data Per Test

**Strategy**: Create new test data for each test, don't reuse

**Benefits**:
- Tests are independent
- No test pollution
- Tests can run in any order
- Tests can run in parallel

**Implementation**:
- Use factories/builders to create test data
- Use `@BeforeEach` to set up fresh data
- Use test fixtures for reusable setup

**Best Practice**: Create fresh test data for each test. Don't rely on data from other tests.

## What to Test vs What Not to Test

### Test Behavior, Not Implementation

**Test Behavior**:
- What the system does (outcomes)
- Public API contracts
- User-visible behavior
- Business rules

**Don't Test Implementation**:
- How the system does it (internal methods)
- Private methods
- Internal state
- Method call order (unless it's the behavior)

**Example**:
```kotlin
// BAD: Testing implementation
@Test
fun testProcessOrder() {
    verify(orderValidator).validate(order)  // Tests internal method call
    verify(orderCalculator).calculate(order)
    service.processOrder(order)
}

// GOOD: Testing behavior
@Test
fun `should create order when valid`() {
    val order = service.processOrder(orderData)
    assertNotNull(order.id)
    assertEquals(OrderStatus.CREATED, order.status)
}
```

**Best Practice**: Test through public APIs. Verify outcomes, not internal implementation.

### Test Public API, Not Private Methods

**Principle**: Private methods are implementation details. Test them indirectly through public APIs.

**If Private Methods Need Testing**:
- They may be too complex (extract to public method or separate class)
- They may contain business logic (make them public or extract)
- They may be doing too much (refactor for single responsibility)

**Best Practice**: Test private methods indirectly through public methods. If you need to test them directly, consider refactoring.

### Don't Test Framework Code

**Don't Test**:
- Spring Boot internals
- Vue/React framework code
- JUnit functionality
- Third-party library internals

**Do Test**:
- Your business logic
- Your component behavior
- Your API contracts
- Your integration points

**Example**:
```kotlin
// BAD: Testing framework
@Test
fun testSpringInjection() {
    assertNotNull(service.orderRepository)  // Testing Spring, not your code
}

// GOOD: Testing your code
@Test
fun `should save order to repository`() {
    service.createOrder(orderData)
    verify(repository).save(any())  // Testing your service behavior
}
```

**Best Practice**: Trust frameworks. Test your code, not framework code.

### Test Edge Cases and Error Paths, Not Just Happy Path

**Happy Path**: Normal, expected flow

**Edge Cases**: Boundary conditions, unusual inputs, extreme values

**Error Paths**: Invalid inputs, failure scenarios, exception handling

**Example**:
```kotlin
// Happy path
@Test
fun `should calculate discount for valid order`() {
    val discount = service.calculateDiscount(Order(amount = 100.0))
    assertEquals(10.0, discount)
}

// Edge cases
@Test
fun `should return zero discount when order amount is zero`() {
    val discount = service.calculateDiscount(Order(amount = 0.0))
    assertEquals(0.0, discount)
}

@Test
fun `should cap discount at maximum threshold`() {
    val discount = service.calculateDiscount(Order(amount = 10000.0))
    assertEquals(100.0, discount)  // Capped at max
}

// Error paths
@Test
fun `should throw exception when order amount is negative`() {
    assertThrows<IllegalArgumentException> {
        service.calculateDiscount(Order(amount = -10.0))
    }
}
```

**Best Practice**: Test happy path, edge cases, and error paths. Don't just test the happy path.

### Test Business Rules Thoroughly

**Business Rules**: Domain logic, validation rules, calculations, state transitions

**Example**:
```kotlin
// Business rule: Premium customers get 20% discount, regular customers get 10%
@Test
fun `should apply 20 percent discount for premium customers`() {
    val customer = Customer(role = Role.PREMIUM)
    val discount = service.calculateDiscount(customer, order)
    assertEquals(20.0, discount)
}

@Test
fun `should apply 10 percent discount for regular customers`() {
    val customer = Customer(role = Role.REGULAR)
    val discount = service.calculateDiscount(customer, order)
    assertEquals(10.0, discount)
}
```

**Best Practice**: Test all business rules thoroughly. These are the most critical tests.

## Anti-Patterns

### Ice Cream Cone (Many E2E, Few Unit Tests)

**Problem**: Inverted pyramid with many slow E2E tests, few fast unit tests

```
    /\
   /  \     Unit Tests (few)
  /____\
 /      \   Integration Tests (some)
/________\
\        /  E2E Tests (many) - WRONG!
 \______/
```

**Symptoms**:
- Slow test suite
- Brittle tests (UI changes break many tests)
- High maintenance cost
- Slow feedback

**Solution**: Invert to pyramid. More unit tests, fewer E2E tests.

**Best Practice**: Follow test pyramid. Most tests should be fast unit tests.

### Testing Implementation Details

**Problem**: Tests that verify how code works, not what it does

**Symptoms**:
- Tests break on refactoring
- Tests verify private method calls
- Tests verify internal state
- Tests verify method call order (when order isn't the behavior)

**Solution**: Test behavior through public APIs

**Best Practice**: Test what the code does, not how it does it.

### Excessive Mocking

**Problem**: Every dependency is mocked, tests don't verify real behavior

**Symptoms**:
- Tests pass but production fails
- Mock interactions verified, not outcomes
- Low confidence in tests

**Solution**: Use real dependencies when possible. Mock only external boundaries.

**Best Practice**: Prefer integration tests with real dependencies over unit tests with excessive mocks.

### Sleep-Based Waits in E2E Tests

**Problem**: Using fixed delays instead of waiting for conditions

```typescript
// BAD: Sleep-based wait
await page.click('button');
await page.waitForTimeout(5000);  // Always waits 5 seconds
await expect(page.locator('.result')).toBeVisible();
```

**Solution**: Use explicit waits for conditions

```typescript
// GOOD: Explicit wait
await page.click('button');
await expect(page.locator('.result')).toBeVisible({ timeout: 10000 });  // Waits up to 10s, proceeds when ready
```

**Best Practice**: Always use explicit waits. Never use sleep-based waits.

### Assertion-Free Tests

**Problem**: Tests that run code but don't verify anything

```kotlin
// BAD: No assertion
@Test
fun testProcessOrder() {
    service.processOrder(order)  // Runs code but doesn't verify outcome
}
```

**Solution**: Always assert expected behavior

```kotlin
// GOOD: With assertion
@Test
fun `should create order when processing`() {
    val result = service.processOrder(order)
    assertNotNull(result.id)
    assertEquals(OrderStatus.CREATED, result.status)
}
```

**Best Practice**: Every test must have at least one assertion that verifies expected behavior.

### Copy-Paste Test Code

**Problem**: Duplicated test setup code across tests

**Solution**: Use factories, builders, fixtures, and helper methods

```kotlin
// BAD: Copy-paste
@Test
fun test1() {
    val customer = Customer(id = "1", email = "test@example.com", role = Role.USER)
    val order = Order(id = "1", customerId = "1", amount = 100.0)
    // Test code
}

@Test
fun test2() {
    val customer = Customer(id = "1", email = "test@example.com", role = Role.USER)
    val order = Order(id = "1", customerId = "1", amount = 100.0)
    // Test code
}

// GOOD: Factory
fun createCustomer(block: Customer.() -> Unit = {}): Customer {
    return Customer(
        id = UUID.randomUUID().toString(),
        email = "test@example.com",
        role = Role.USER
    ).apply(block)
}

@Test
fun test1() {
    val customer = createCustomer()
    val order = createOrder { customerId = customer.id }
    // Test code
}
```

**Best Practice**: Extract common test setup into factories, builders, and fixtures. Don't copy-paste.

## Cloud Integration Testing

### Prefer LocalStack + Testcontainers Over Mocking AWS SDK Clients

**Problem**: Mocking AWS SDK clients only tests that you called the right method, not that your serialization, error handling, and configuration work correctly.

**Solution**: Use LocalStack + Testcontainers to test against real AWS API endpoints locally.

**Why**:
- Tests actual serialization/deserialization of AWS requests/responses
- Tests error handling with real AWS error responses
- Tests configuration (endpoint URLs, credentials, regions)
- Tests integration behavior, not just method calls
- Catches issues that mocks would miss (wrong bucket names, malformed requests, etc.)

**Example**:
```kotlin
// BAD: Mocking AWS client
@Test
fun `should upload file`() {
    val s3Client = mockk<S3Client>()
    every { s3Client.putObject(any()) } returns PutObjectResponse.builder().build()
    
    service.uploadFile("bucket", "key", content)
    
    verify { s3Client.putObject(any()) }  // Only tests method call
}

// GOOD: Using LocalStack
@Testcontainers
@SpringBootTest
class S3UploadServiceTest {
    @Container
    val localStack = LocalStackContainer(DockerImageName.parse("localstack/localstack:latest"))
        .withServices(LocalStackContainer.Service.S3)

    @Autowired
    lateinit var s3UploadService: S3UploadService

    @Test
    fun `should upload file to S3`() {
        val key = s3UploadService.upload("test-bucket", "test-key", fileContent)
        
        assertNotNull(key)
        // Verify file actually exists in LocalStack S3
        val object = s3Client.getObject("test-bucket", "test-key")
        assertNotNull(object)  // Tests real integration
    }
}
```

**Best Practice**: Prefer LocalStack + Testcontainers over mocking AWS SDK clients. You want to test your integration with AWS services, not just that you called the right method.

### Keep LocalStack Containers Shared Across Test Classes

**Pattern**: Use singleton pattern to share LocalStack container across multiple test classes for faster test execution.

**Why**: Starting LocalStack container is expensive. Sharing it across test classes reduces startup time.

**Implementation**:
```kotlin
object LocalStackSingleton {
    val container = LocalStackContainer(DockerImageName.parse("localstack/localstack:latest"))
        .withServices(LocalStackContainer.Service.S3, LocalStackContainer.Service.SQS)
    
    init {
        container.start()
    }
}

@Testcontainers
class S3ServiceTest {
    companion object {
        @Container
        val localStack = LocalStackSingleton.container
    }
}

@Testcontainers
class SQSServiceTest {
    companion object {
        @Container
        val localStack = LocalStackSingleton.container
    }
}
```

**Trade-offs**:
- ✅ Faster test execution (container starts once)
- ✅ Lower resource usage
- ❌ Tests must be careful about shared state (use unique bucket/queue names per test)
- ❌ Risk of test interference if cleanup isn't thorough

**Best Practice**: Keep LocalStack containers shared across test classes for speed, but ensure each test uses unique resource names and cleans up properly.

### Use Real AWS Only for Smoke Tests in Staging

**Principle**: Use LocalStack for integration tests, real AWS only for smoke tests in staging environments.

**Why**:
- LocalStack is fast, free, and isolated (perfect for CI/CD)
- Real AWS is slow, costs money, and requires network access
- Real AWS should validate that LocalStack tests translate to production

**Strategy**:
- **Integration Tests**: Use LocalStack (fast, isolated, free)
- **Smoke Tests**: Use real AWS in staging (validates production-like behavior)
- **E2E Tests**: Use real AWS in staging (full system validation)

**Best Practice**: Use LocalStack for integration tests in CI/CD. Use real AWS only for smoke tests and E2E tests in staging environments.

## Stack-Specific Callouts

### Kotlin/Java

**JUnit 5 Nested Classes**:
```kotlin
class OrderServiceTest {
    @Nested
    inner class `when calculating discount` {
        @Test
        fun `should apply premium discount for premium customers`() {
            // Test
        }
        
        @Test
        fun `should apply regular discount for regular customers`() {
            // Test
        }
    }
}
```

**MockK Relaxed vs Strict**:
- Relaxed mocks: Return default values for unstubbed calls
- Strict mocks: Fail on unstubbed calls (default)

**Testcontainers for Database Tests**:
```kotlin
@Testcontainers
class OrderRepositoryTest {
    @Container
    val postgres = PostgreSQLContainer("postgres:15")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test")
}
```

**Spring Boot Test Slices**:
- `@SpringBootTest`: Full application context (slow)
- `@WebMvcTest`: Web layer only (faster)
- `@DataJpaTest`: Data layer only (faster)
- `@JsonTest`: JSON serialization only (fastest)

**AssertJ for Fluent Assertions**:
```kotlin
assertThat(order)
    .isNotNull()
    .hasFieldOrPropertyWithValue("status", OrderStatus.CREATED)
    .hasFieldOrProperty("id")
```

### Vue

**Vitest for Unit Tests**:
- Fast, Vite-native test runner
- ESM support
- TypeScript support

**@vue/test-utils for Component Tests**:
```typescript
import { mount } from '@vue/test-utils'
import OrderForm from './OrderForm.vue'

test('should submit order', async () => {
  const wrapper = mount(OrderForm)
  await wrapper.find('button').trigger('click')
  expect(wrapper.emitted('submit')).toBeTruthy()
})
```

**Testing Library for Behavior-Focused Tests**:
```typescript
import { render, screen } from '@testing-library/vue'
import OrderForm from './OrderForm.vue'

test('should submit order', async () => {
  render(OrderForm)
  await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
  expect(screen.getByText('Order submitted')).toBeInTheDocument()
})
```

**MSW for API Mocking**:
```typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.post('/api/orders', (req, res, ctx) => {
    return res(ctx.json({ id: '1', status: 'created' }))
  })
)
```

**Playwright for E2E**:
```typescript
import { test, expect } from '@playwright/test'

test('should create order', async ({ page }) => {
  await page.goto('/orders')
  await page.getByRole('button', { name: 'Create Order' }).click()
  await expect(page.getByText('Order created')).toBeVisible()
})
```

### React

**Vitest or Jest**:
- Vitest: Fast, Vite-native, ESM support
- Jest: Mature, widely used, good ecosystem

**React Testing Library**:
- Query by role/text, not implementation
- Focus on user-visible behavior
- Avoid testing implementation details

```typescript
import { render, screen } from '@testing-library/react'
import OrderForm from './OrderForm'

test('should submit order', async () => {
  render(<OrderForm />)
  await userEvent.click(screen.getByRole('button', { name: 'Submit' }))
  expect(screen.getByText('Order submitted')).toBeInTheDocument()
})
```

**MSW for API Mocking**: Same as Vue

**Playwright for E2E**: Same as Vue

**Best Practice**: Use Testing Library for component tests (behavior-focused), Playwright for E2E tests (user journeys).
