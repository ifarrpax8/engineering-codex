# Backend Architecture -- Testing

Testing strategies must align with architecture choices. Different architectures require different testing approaches, from unit tests that verify domain logic to integration tests that validate service boundaries.

## Contents

- [Architecture Tests](#architecture-tests)
- [Service-Level Testing](#service-level-testing)
- [Contract Testing](#contract-testing)
- [Integration Testing by Pattern](#integration-testing-by-pattern)
- [Testing Event-Driven Flows](#testing-event-driven-flows)
- [Testing CQRS](#testing-cqrs)
- [Test Strategy Summary](#test-strategy-summary)

## Architecture Tests

Architecture tests enforce structural constraints that code reviews might miss. They run as part of the test suite, failing builds when architectural rules are violated.

### ArchUnit for Boundary Enforcement

ArchUnit provides a fluent API for defining architectural rules. These rules catch violations early, preventing architectural drift.

**Module Boundary Rules**: Prevent modules from accessing each other's internals:

```kotlin
@ArchTest
val modulesShouldNotAccessOtherModulesInternals = 
    noClasses()
        .that().resideInAPackage("..user.internal..")
        .should().accessClassesThat()
        .resideInAPackage("..order.internal..")
```

**Layer Dependency Rules**: Enforce layered architecture dependencies:

```kotlin
@ArchTest
val controllersShouldNotAccessRepositories = 
    noClasses()
        .that().resideInAPackage("..controller..")
        .should().accessClassesThat()
        .resideInAPackage("..repository..")
```

**Naming Conventions**: Ensure consistent naming:

```kotlin
@ArchTest
val repositoriesShouldHaveCorrectNaming = 
    classes()
        .that().resideInAPackage("..repository..")
        .should().haveSimpleNameEndingWith("Repository")
```

**Domain Independence**: Verify domain doesn't depend on infrastructure:

```kotlin
@ArchTest
val domainShouldNotDependOnInfrastructure = 
    noClasses()
        .that().resideInAPackage("..domain..")
        .should().dependOnClassesThat()
        .resideInAPackage("..infrastructure..")
```

**Hexagonal Architecture Rules**: Enforce port/adapter separation:

```kotlin
@ArchTest
val adaptersShouldNotDependOnOtherAdapters = 
    noClasses()
        .that().resideInAPackage("..adapter..")
        .should().dependOnClassesThat()
        .resideInAPackage("..adapter..")
```

ArchUnit rules should be comprehensive but not overly restrictive. Focus on rules that prevent architectural violations that are hard to catch in code reviews.

## Service-Level Testing

Service-level tests verify a single service end-to-end, including all layers from HTTP controllers to database. These tests validate that components work together correctly.

### Spring Boot Test

`@SpringBootTest` loads the full Spring application context, enabling end-to-end testing within a single service:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class UserServiceIntegrationTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Autowired
    lateinit var userRepository: UserRepository
    
    @Test
    fun `should create user`() {
        val request = CreateUserRequest(email = "user@example.com")
        
        mockMvc.post("/users") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(request)
        }.andExpect {
            status { isCreated() }
        }
        
        val user = userRepository.findByEmail("user@example.com")
        assertThat(user).isNotNull()
    }
}
```

### Testcontainers for Database

Testcontainers provides real database instances for integration tests, ensuring tests run against the same database technology as production:

```kotlin
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {
    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:15")
            .apply {
                withDatabaseName("testdb")
                withUsername("test")
                withPassword("test")
            }
    }
    
    @Autowired
    lateinit var userRepository: UserRepository
    
    @Test
    fun `should persist user`() {
        val user = User(email = Email("user@example.com"))
        userRepository.save(user)
        
        val found = userRepository.findById(user.id)
        assertThat(found).isPresent
    }
}
```

### Slice Tests

Spring Boot provides slice tests that load only specific parts of the application context:

**@WebMvcTest**: Tests controllers in isolation, mocking service layer:

```kotlin
@WebMvcTest(UserController::class)
class UserControllerTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @MockBean
    lateinit var userService: UserService
    
    @Test
    fun `should return user`() {
        whenever(userService.getUser(any())).thenReturn(UserResponse(...))
        
        mockMvc.get("/users/123")
            .andExpect { status { isOk() } }
    }
}
```

**@DataJpaTest**: Tests repository layer with in-memory database:

```kotlin
@DataJpaTest
class UserRepositoryTest {
    @Autowired
    lateinit var userRepository: UserRepository
    
    @Test
    fun `should find by email`() {
        val user = User(email = Email("user@example.com"))
        userRepository.save(user)
        
        val found = userRepository.findByEmail("user@example.com")
        assertThat(found).isNotNull()
    }
}
```

Slice tests are faster than full integration tests but don't verify component integration. Use them for focused testing of specific layers.

## Contract Testing

Contract testing ensures compatibility between services without requiring full integration test environments. Services define contracts that consumers verify.

### Pact for Consumer-Driven Contracts

Pact enables consumer-driven contract testing. Consumers define expected interactions, providers verify they satisfy contracts:

**Consumer Side**:
```kotlin
@ExtendWith(PactConsumerTestExt::class)
class UserServiceClientPactTest {
    @Pact(consumer = "order-service", provider = "user-service")
    fun getUserPact(builder: PactDslWithProvider): RequestResponsePact {
        return builder
            .given("user exists")
            .uponReceiving("a request for user")
            .path("/users/123")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(userResponseBody)
            .toPact()
    }
    
    @Test
    @PactTestFor(pactMethod = "getUserPact")
    fun testGetUser(mockServer: MockServer) {
        val client = UserServiceClient(mockServer.getUrl())
        val user = client.getUser("123")
        assertThat(user).isNotNull()
    }
}
```

**Provider Side**:
```kotlin
@Provider("user-service")
@PactFolder("pacts")
class UserServiceProviderPactTest {
    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider::class)
    fun pactVerificationTestTemplate(context: PactVerificationContext) {
        context.verifyInteraction()
    }
    
    @BeforeEach
    fun setUp(context: PactVerificationContext) {
        context.setTarget(HttpTestTarget("localhost", 8080))
    }
}
```

### Spring Cloud Contract

Spring Cloud Contract provides contract testing integrated with Spring Boot:

**Contract Definition** (Groovy DSL):
```groovy
Contract.make {
    request {
        method 'GET'
        url '/users/123'
    }
    response {
        status 200
        body([
            id: '123',
            email: 'user@example.com'
        ])
    }
}
```

Contracts are verified against actual controller implementations, ensuring contracts match reality.

## Integration Testing by Pattern

Different deployment architectures require different integration testing strategies.

### Monolith Integration Testing

Monoliths enable comprehensive integration testing since all components run in the same process:

**Full Stack Test**: Test entire request flow from HTTP to database:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class UserFlowIntegrationTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `should create and retrieve user`() {
        val createRequest = CreateUserRequest(email = "user@example.com")
        
        val createResponse = mockMvc.post("/users") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(createRequest)
        }.andExpect {
            status { isCreated() }
        }.andReturn()
        
        val userId = extractUserId(createResponse)
        
        mockMvc.get("/users/$userId")
            .andExpect {
                status { isOk() }
                jsonPath("$.email") { value("user@example.com") }
            }
    }
}
```

**Database Transactions**: Use `@Transactional` to roll back test data, or use Testcontainers with database cleanup between tests.

### Modulith Integration Testing

Moduliths require testing both module internals and inter-module communication:

**Module Integration Test**: Test a module's public API:

```kotlin
@SpringModulithTest
class UserModuleIntegrationTest {
    @Autowired
    lateinit var userService: UserService  // Module API
    
    @Test
    fun `should create user`() {
        val user = userService.createUser(CreateUserCommand(...))
        assertThat(user).isNotNull()
    }
}
```

**Inter-Module Communication**: Test modules interacting through events or APIs:

```kotlin
@SpringModulithTest
class OrderUserIntegrationTest {
    @Autowired
    lateinit var orderService: OrderService
    
    @Autowired
    lateinit var userService: UserService
    
    @Test
    fun `should create order for existing user`() {
        val user = userService.createUser(...)
        val order = orderService.createOrder(CreateOrderCommand(userId = user.id))
        assertThat(order).isNotNull()
    }
}
```

Spring Modulith provides `@ApplicationModuleTest` for testing module boundaries and interactions.

### Microservices Integration Testing

Microservices require testing individual services and their interactions:

**Service Integration Test**: Test a single service with mocked dependencies:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class PaymentServiceIntegrationTest {
    @MockBean
    lateinit var userServiceClient: UserServiceClient  // External service mock
    
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `should process payment`() {
        whenever(userServiceClient.getUser(any())).thenReturn(User(...))
        
        mockMvc.post("/payments") { ... }
            .andExpect { status { isOk() } }
    }
}
```

**Contract Tests**: Verify service satisfies consumer contracts (see Contract Testing above).

**External Dependency Testing**: Use Testcontainers for real external dependencies (databases, message brokers):

```kotlin
@Testcontainers
class PaymentServiceWithDatabaseTest {
    @Container
    val postgres = PostgreSQLContainer("postgres:15")
    
    @Container
    val kafka = KafkaContainer("confluentinc/cp-kafka:latest")
    
    @Test
    fun `should process payment with real dependencies`() {
        // Test with real database and Kafka
    }
}
```

**End-to-End Tests**: Test multiple services together, either in Docker Compose or test environment. These tests are slower and more brittle but validate real service interactions.

## Testing Event-Driven Flows

Event-driven architectures require testing event production, consumption, and saga orchestration.

### Testing Command Handlers

Axon Framework command handlers can be tested in isolation:

```kotlin
class UserAggregateTest {
    private lateinit var fixture: AggregateTestFixture<UserAggregate>
    
    @BeforeEach
    fun setUp() {
        fixture = AggregateTestFixture(UserAggregate::class.java)
    }
    
    @Test
    fun `should create user`() {
        fixture.givenNoPriorActivity()
            .`when`(CreateUserCommand(userId = "123", email = "user@example.com"))
            .expectEvents(UserCreatedEvent(userId = "123", email = "user@example.com"))
    }
}
```

### Testing Event Handlers

Event handlers (projections) can be tested by providing events:

```kotlin
class UserProjectionTest {
    private lateinit var fixture: TestExecutor
    
    @Test
    fun `should update user read model`() {
        fixture.givenEvents(
            UserCreatedEvent(userId = "123", email = "user@example.com")
        ).whenExecuting { projection ->
            val user = projection.findById("123")
            assertThat(user?.email).isEqualTo("user@example.com")
        }
    }
}
```

### Testing Sagas

Sagas (process managers) orchestrate multi-step processes. Test saga state transitions:

```kotlin
class OrderSagaTest {
    private lateinit var fixture: SagaTestFixture<OrderSaga>
    
    @Test
    fun `should complete order when payment succeeds`() {
        fixture.givenAggregate("order-123")
            .published(OrderCreatedEvent(...))
            .whenAggregate("payment-123")
            .publishes(PaymentSucceededEvent(...))
            .expectActiveSagas(0)
            .expectDispatchedCommands(CompleteOrderCommand(...))
    }
}
```

## Testing CQRS

CQRS requires testing command and query sides independently.

### Testing Command Side

Test aggregates handle commands correctly and emit events:

```kotlin
class UserAggregateCommandTest {
    @Test
    fun `should emit user created event`() {
        fixture.givenNoPriorActivity()
            .`when`(CreateUserCommand(...))
            .expectEvents(UserCreatedEvent(...))
    }
    
    @Test
    fun `should reject duplicate email`() {
        fixture.givenEvents(UserCreatedEvent(email = "user@example.com"))
            .`when`(CreateUserCommand(email = "user@example.com"))
            .expectException(DuplicateEmailException::class.java)
    }
}
```

### Testing Query Side

Test projections build correct read models from events:

```kotlin
class UserProjectionTest {
    @Test
    fun `should build user view from events`() {
        fixture.givenEvents(
            UserCreatedEvent(userId = "123", email = "user@example.com"),
            UserEmailChangedEvent(userId = "123", newEmail = "new@example.com")
        ).whenExecuting { projection ->
            val user = projection.findById("123")
            assertThat(user?.email).isEqualTo("new@example.com")
        }
    }
}
```

### Testing Event Sourcing

With event sourcing, test aggregate state reconstruction:

```kotlin
@Test
fun `should reconstruct state from events`() {
    fixture.givenEvents(
        UserCreatedEvent(userId = "123", email = "user@example.com"),
        UserEmailChangedEvent(userId = "123", newEmail = "new@example.com")
    ).whenExecuting { aggregate ->
        assertThat(aggregate.email).isEqualTo("new@example.com")
    }
}
```

## Test Strategy Summary

- **Unit Tests**: Domain logic, value objects, domain services. Fast, no dependencies.
- **Integration Tests**: Component interactions within a service. Use Testcontainers for real dependencies.
- **Contract Tests**: Service API compatibility. Use Pact or Spring Cloud Contract.
- **Architecture Tests**: Structural constraints. Use ArchUnit.
- **End-to-End Tests**: Full system validation. Use sparingly, focus on critical paths.

Balance test coverage with execution time. Fast feedback loops enable rapid iteration. Comprehensive but slow test suites slow development velocity.
