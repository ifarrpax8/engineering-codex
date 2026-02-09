# API Design -- Testing

API testing ensures contracts are honored, implementations match specifications, and changes don't break consumers. Test at multiple levels: contracts, integration, performance, and security.

## Contents

- [Contract Testing](#contract-testing)
- [Integration Testing](#integration-testing)
- [Load and Performance Testing](#load-and-performance-testing)
- [Schema and Compatibility Testing](#schema-and-compatibility-testing)
- [Security Testing](#security-testing)
- [API Documentation Testing](#api-documentation-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Contract Testing

Contract testing verifies that API implementations match their specifications and that consumers and providers agree on the contract.

### OpenAPI/TypeSpec Schema Validation

Validate that the implementation matches the spec:

**Provider-side validation**:
- Generate server stubs from OpenAPI/TypeSpec
- Validate request/response schemas in tests
- Ensure all endpoints in the spec are implemented
- Ensure all required fields are present

**Tools**:
- **Spring**: Use `@ParameterizedTest` with OpenAPI schema validation
- **OpenAPI Generator**: Generate test templates from specs
- **TypeSpec**: Compile to OpenAPI, validate against implementation

**Example** (Spring Boot):
```kotlin
@Test
fun `GET /users/{id} returns valid User response`() {
    val response = mockMvc.get("/v1/users/123")
        .andExpect(status().isOk)
        .andExpect(jsonPath("$.id").exists())
        .andExpect(jsonPath("$.email").exists())
        // Validate against OpenAPI schema
}
```

### Consumer-Driven Contracts with Pact

Pact enables consumer-driven contract testing:

**How it works**:
1. Consumer defines expected request/response in a "pact"
2. Consumer tests mock the provider using the pact
3. Provider verification runs against real provider, ensuring it fulfills all consumer pacts
4. CI fails if provider breaks a consumer contract

**Benefits**:
- Prevents breaking changes (provider can't deploy if it breaks consumers)
- Documents actual consumer needs (not just provider assumptions)
- Enables independent deployment (consumer and provider can deploy separately)

**Pact workflow**:
```kotlin
// Consumer test
val pact = ConsumerPactBuilder
    .consumer("UserService")
    .hasPactWith("OrderService")
    .`given`("user exists")
    .uponReceiving("a request for user")
    .path("/users/123")
    .method("GET")
    .willRespondWith()
    .status(200)
    .body("""{"id":"123","email":"user@example.com"}""")
    .toPact()

// Provider verification
@PactVerifyProvider("a user response")
fun verifyUserResponse() {
    // Provider must return this exact format
}
```

### Provider Verification

Provider verification ensures the provider fulfills all consumer contracts:

- **Run in CI**: Fail builds if provider breaks any consumer contract
- **Test against real provider**: Use Testcontainers or test database
- **Coverage**: Ensure all consumer pacts are verified

**Breaking change detection**: If a consumer pact expects a field that the provider removes, verification fails.

### Preventing Breaking Changes

Contract testing prevents breaking changes by:

- **Schema validation**: Reject requests/responses that don't match the spec
- **Pact verification**: Prevent provider changes that break consumer expectations
- **CI integration**: Automated checks before deployment
- **Versioning discipline**: Breaking changes require new API versions

## Integration Testing

Integration testing validates real HTTP endpoints with actual request/response cycles.

### Testing Real HTTP Endpoints

Test actual HTTP endpoints, not just unit tests:

**Spring MVC** (`MockMvc`):
```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class UserApiIntegrationTest {
    @Autowired
    lateinit var mockMvc: MockMvc

    @Test
    fun `GET /v1/users/{id} returns user`() {
        mockMvc.get("/v1/users/123")
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.id").value("123"))
            .andExpect(jsonPath("$.email").value("user@example.com"))
    }
}
```

**Spring WebFlux** (`WebTestClient`):
```kotlin
@SpringBootTest
@AutoConfigureWebTestClient
class UserApiIntegrationTest {
    @Autowired
    lateinit var webTestClient: WebTestClient

    @Test
    fun `GET /v1/users/{id} returns user`() {
        webTestClient.get()
            .uri("/v1/users/123")
            .exchange()
            .expectStatus().isOk
            .expectBody()
            .jsonPath("$.id").isEqualTo("123")
    }
}
```

### Request/Response Validation

Validate request and response formats:

- **Request validation**: Invalid requests return 400/422 with error details
- **Response validation**: Responses match OpenAPI/TypeSpec schema
- **Content-Type**: Correct `Content-Type` headers
- **Status codes**: Appropriate HTTP status codes

### Error Response Format Verification

Test error responses:

```kotlin
@Test
fun `GET /v1/users/{id} returns 404 for non-existent user`() {
    mockMvc.get("/v1/users/999")
        .andExpect(status().isNotFound)
        .andExpect(jsonPath("$.type").value("https://example.com/problems/user-not-found"))
        .andExpect(jsonPath("$.title").value("User Not Found"))
        .andExpect(jsonPath("$.status").value(404))
        .andExpect(jsonPath("$.detail").exists())
}
```

Verify error responses follow RFC 9457 (Problem Details for HTTP APIs).

### Authentication and Authorization Testing

Test auth flows:

**Authentication**:
```kotlin
@Test
fun `GET /v1/users requires authentication`() {
    mockMvc.get("/v1/users")
        .andExpect(status().isUnauthorized)
}

@Test
fun `GET /v1/users succeeds with valid token`() {
    mockMvc.get("/v1/users")
        .header("Authorization", "Bearer $validToken")
        .andExpect(status().isOk)
}
```

**Authorization**:
```kotlin
@Test
fun `DELETE /v1/users/{id} requires admin role`() {
    mockMvc.delete("/v1/users/123")
        .header("Authorization", "Bearer $userToken") // Not admin
        .andExpect(status().isForbidden)
}
```

### Database Integration (Testcontainers)

Use Testcontainers for real database testing:

```kotlin
@Testcontainers
class UserApiIntegrationTest {
    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test")
    }

    @Test
    fun `POST /v1/users creates user in database`() {
        val request = CreateUserRequest(email = "new@example.com")
        
        mockMvc.post("/v1/users") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(request)
        }
            .andExpect(status().isCreated)
        
        // Verify in database
        val user = userRepository.findByEmail("new@example.com")
        assertThat(user).isNotNull()
    }
}
```

Testcontainers provides real database instances for integration tests, ensuring database-specific behavior is tested.

## Load and Performance Testing

Load testing identifies performance bottlenecks and breaking points.

### Establishing Baseline Latency

Measure baseline performance:
- **p50 (median)**: Typical response time
- **p95**: 95% of requests complete within this time
- **p99**: 99% of requests complete within this time

**Tools**: Gatling, k6, Apache JMeter, or simple scripts with `curl` and timing.

**Baseline example**:
```
GET /v1/users/{id}: p50=50ms, p95=100ms, p99=200ms
GET /v1/users: p50=100ms, p95=200ms, p99=500ms
```

### Identifying Breaking Points

Find when the API degrades:
- **Gradual load increase**: Ramp up requests per second until latency spikes
- **Sustained load**: Maintain load to identify memory leaks or connection pool exhaustion
- **Spike testing**: Sudden traffic spikes (e.g., flash sale scenarios)

**Breaking points to identify**:
- Database connection pool exhaustion
- Memory leaks under sustained load
- CPU bottlenecks
- Network bandwidth limits

### Testing Under Realistic Traffic Patterns

Simulate real usage:
- **Traffic distribution**: Mix of GET, POST, PUT, DELETE requests
- **Concurrent users**: Multiple users making requests simultaneously
- **Geographic distribution**: If applicable, test from multiple regions
- **Peak hours**: Test during expected peak traffic times

**Realistic patterns**:
- 80% GET requests, 15% POST, 5% PUT/DELETE
- Bursty traffic (spikes during business hours)
- Long-running requests (reports, exports)

### Pagination Performance with Large Datasets

Test pagination with realistic data volumes:

```kotlin
@Test
fun `GET /v1/users pagination performance with 100k records`() {
    // Seed 100k users
    repeat(100000) { createTestUser() }
    
    // Test first page (should be fast)
    val start = System.currentTimeMillis()
    mockMvc.get("/v1/users?limit=20")
    val firstPageTime = System.currentTimeMillis() - start
    assertThat(firstPageTime).isLessThan(100) // < 100ms
    
    // Test deep page (should still be reasonable with cursor pagination)
    val deepPageStart = System.currentTimeMillis()
    mockMvc.get("/v1/users?cursor=...&limit=20")
    val deepPageTime = System.currentTimeMillis() - deepPageStart
    assertThat(deepPageTime).isLessThan(200) // < 200ms
}
```

**Pagination performance considerations**:
- Offset pagination degrades with deep pages (OFFSET 10000 is slow)
- Cursor/keyset pagination maintains consistent performance
- Index coverage: Ensure pagination queries use indexes

### Connection Pool and Database Load

Test database connection handling:
- **Connection pool size**: Ensure pool is sized for expected load
- **Connection leaks**: Verify connections are returned to pool
- **Database query performance**: Identify slow queries under load
- **Transaction isolation**: Test behavior under concurrent transactions

**Connection pool testing**:
```kotlin
@Test
fun `concurrent requests do not exhaust connection pool`() {
    val poolSize = 10
    val concurrentRequests = 20 // More than pool size
    
    val results = (1..concurrentRequests).map { i ->
        async {
            mockMvc.get("/v1/users/$i") // Each uses a connection
        }
    }.awaitAll()
    
    // All should succeed (pool should handle queuing)
    assertThat(results.all { it.status == 200 }).isTrue()
}
```

## Schema and Compatibility Testing

Schema compatibility testing ensures API changes don't break existing clients.

### Backward Compatibility Checks

Ensure new versions don't break existing clients:

**Additive changes** (backward compatible):
- Adding new optional fields
- Adding new endpoints
- Adding new enum values (if clients handle unknown values)

**Breaking changes** (require new version):
- Removing fields or endpoints
- Changing field types
- Making optional fields required
- Changing field names

**Automated checks**:
```kotlin
@Test
fun `v2 API is backward compatible with v1 clients`() {
    // v1 client request
    val v1Request = """{"email":"user@example.com"}"""
    
    // Should still work with v2 API
    mockMvc.post("/v2/users") {
        contentType = MediaType.APPLICATION_JSON
        content = v1Request
    }
        .andExpect(status().isCreated)
}
```

### Forward Compatibility Considerations

Design APIs to handle unknown fields gracefully:

- **JSON**: Ignore unknown fields (don't fail on extra fields)
- **Protocol Buffers**: Unknown fields are preserved (forward compatible)
- **Version negotiation**: Clients can request specific versions

**Forward compatibility example**:
```kotlin
data class CreateUserRequest(
    val email: String,
    // Unknown fields are ignored (Jackson default)
    @JsonIgnoreProperties(ignoreUnknown = true)
    val extraField: String? = null
)
```

### Breaking Change Detection in CI

Automate breaking change detection:

**OpenAPI diff tools**:
- Compare OpenAPI specs between versions
- Detect breaking changes (removed fields, changed types)
- Fail CI if breaking changes detected without version bump

**TypeSpec diff**:
- TypeSpec compiler can detect breaking changes
- Integrate into CI pipeline

**Example CI check**:
```bash
# Compare current OpenAPI spec with previous version
openapi-diff v1.yaml v2.yaml
# Fail if breaking changes detected
```

### TypeSpec/OpenAPI Diff Tools

Use diff tools to identify changes:

- **openapi-diff**: Compare OpenAPI specs, identify breaking changes
- **TypeSpec**: Compiler warnings for breaking changes
- **Custom scripts**: Parse specs, compare schemas programmatically

**Diff output example**:
```
Breaking Changes:
- Removed field: User.legacyId
- Changed type: User.status (string -> enum)
- Removed endpoint: DELETE /v1/users/{id}/archive

Non-breaking Changes:
- Added field: User.preferences (optional)
- Added endpoint: GET /v1/users/{id}/preferences
```

## Security Testing

Security testing identifies vulnerabilities and ensures proper access controls.

### Authentication Bypass Attempts

Test authentication mechanisms:

```kotlin
@Test
fun `endpoints reject requests without authentication`() {
    listOf(
        "/v1/users",
        "/v1/orders",
        "/v1/products"
    ).forEach { endpoint ->
        mockMvc.get(endpoint)
            .andExpect(status().isUnauthorized)
    }
}

@Test
fun `endpoints reject invalid tokens`() {
    mockMvc.get("/v1/users")
        .header("Authorization", "Bearer invalid-token")
        .andExpect(status().isUnauthorized)
}

@Test
fun `endpoints reject expired tokens`() {
    val expiredToken = generateExpiredToken()
    mockMvc.get("/v1/users")
        .header("Authorization", "Bearer $expiredToken")
        .andExpect(status().isUnauthorized)
}
```

### Injection Attacks

Test for injection vulnerabilities:

**SQL Injection**:
```kotlin
@Test
fun `user input is sanitized to prevent SQL injection`() {
    val maliciousInput = "'; DROP TABLE users; --"
    mockMvc.get("/v1/users?search=$maliciousInput")
        .andExpect(status().isBadRequest) // Should reject, not execute SQL
}
```

**NoSQL Injection**:
```kotlin
@Test
fun `user input prevents NoSQL injection`() {
    val maliciousInput = """{"$ne": null}"""
    mockMvc.post("/v1/users") {
        contentType = MediaType.APPLICATION_JSON
        content = """{"email": "$maliciousInput"}"""
    }
        .andExpect(status().isBadRequest)
}
```

**Command Injection**:
```kotlin
@Test
fun `user input prevents command injection`() {
    val maliciousInput = "; rm -rf /"
    mockMvc.get("/v1/users?export=$maliciousInput")
        .andExpect(status().isBadRequest)
}
```

### Rate Limiting Verification

Test rate limiting:

```kotlin
@Test
fun `rate limiting blocks excessive requests`() {
    val limit = 100
    val requests = (1..limit + 10).map {
        mockMvc.get("/v1/users")
            .header("Authorization", "Bearer $token")
    }
    
    val responses = requests.map { it.andReturn().response }
    val rateLimitedCount = responses.count { it.status == 429 }
    
    assertThat(rateLimitedCount).isGreaterThan(0)
}
```

### CORS Configuration Testing

Test CORS headers:

```kotlin
@Test
fun `CORS headers are correctly configured`() {
    mockMvc.options("/v1/users")
        .header("Origin", "https://example.com")
        .header("Access-Control-Request-Method", "GET")
        .andExpect(header().string("Access-Control-Allow-Origin", "https://example.com"))
        .andExpect(header().string("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE"))
}
```

### Input Validation Boundary Testing

Test input validation boundaries:

```kotlin
@Test
fun `email validation rejects invalid formats`() {
    listOf(
        "not-an-email",
        "@example.com",
        "user@",
        "user@example",
        "user name@example.com" // Space
    ).forEach { invalidEmail ->
        mockMvc.post("/v1/users") {
            contentType = MediaType.APPLICATION_JSON
            content = """{"email": "$invalidEmail"}"""
        }
            .andExpect(status().isUnprocessableEntity)
    }
}

@Test
fun `string length limits are enforced`() {
    val tooLongEmail = "a".repeat(300) + "@example.com"
    mockMvc.post("/v1/users") {
        contentType = MediaType.APPLICATION_JSON
        content = """{"email": "$tooLongEmail"}"""
    }
        .andExpect(status().isUnprocessableEntity)
}
```

## API Documentation Testing

Ensure documentation examples actually work.

### Ensuring Examples Work

Test that documentation examples execute successfully:

```kotlin
@Test
fun `documentation example for GET /v1/users/{id} works`() {
    // Example from docs: GET /v1/users/123
    mockMvc.get("/v1/users/123")
        .andExpect(status().isOk)
        .andExpect(jsonPath("$.id").value("123"))
        // Verify response matches documented example
}
```

**Automated doc testing**:
- Extract examples from OpenAPI/TypeSpec specs
- Execute examples as integration tests
- Fail CI if examples don't work

### Validating Code Samples

Test code samples in documentation:

```kotlin
@Test
fun `JavaScript code sample from docs executes correctly`() {
    // Simulate the documented request
    val documentedRequest = """
        fetch('/v1/users/123', {
            headers: { 'Authorization': 'Bearer token' }
        })
    """
    
    // Test equivalent request
    mockMvc.get("/v1/users/123")
        .header("Authorization", "Bearer token")
        .andExpect(status().isOk)
}
```

### Testing SDK Generated from Specs

If SDKs are generated from specs, test the generated SDK:

```kotlin
@Test
fun `generated TypeScript SDK matches API contract`() {
    // Generate SDK from OpenAPI spec
    // Run SDK tests against real API
    // Ensure SDK methods match API endpoints
}
```

**SDK testing**:
- Generate SDK from latest spec
- Run SDK integration tests against API
- Ensure SDK handles all API features (auth, errors, pagination)

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize API testing based on consumer impact and failure likelihood. Critical paths requiring immediate coverage include: core CRUD operations (create, read, update, delete) for primary resources, authentication and authorization endpoints, and payment/transaction endpoints (financial impact). High-priority areas include: pagination and filtering (data retrieval correctness), error handling (client experience), and contract compliance (consumer compatibility).

Medium-priority areas suitable for later iterations include: bulk operations, export/import endpoints, and administrative endpoints. Low-priority areas for exploratory testing include: deprecated endpoints, edge case query parameters, and optional feature endpoints.

Focus on breaking changes that affect consumers: schema modifications, endpoint removals, and authentication changes. These represent the highest risk of production incidents and consumer outages.

### Exploratory Testing Guidance

API contract exploration should probe: optional vs required fields (what happens when optional fields are omitted? when required fields are missing?), field type coercion (string "123" vs integer 123), and null vs empty vs omitted (different semantics). Test boundary conditions: maximum string lengths, integer ranges, array size limits, and date/time formats.

Pagination requires manual investigation: test cursor pagination with invalid cursors, offset pagination with negative offsets, and limit boundaries (0, 1, maximum, beyond maximum). Explore what happens when pagination state changes during iteration (new items added, items deleted).

Error response exploration: test all error codes (400, 401, 403, 404, 409, 422, 429, 500), verify error message consistency, and check error response schema compliance. Probe error scenarios: malformed JSON, missing required headers, invalid content types, and oversized payloads.

Rate limiting needs exploration: test rate limit boundaries (exactly at limit, one over limit), rate limit reset behavior, and rate limit headers (X-RateLimit-Remaining, Retry-After). Investigate what happens when rate limits are exceeded: are requests queued, rejected immediately, or partially processed?

### Test Data Management

API testing requires realistic test data that mirrors production patterns: user accounts with various roles, resources in different states (active, archived, pending), and relationships between resources (users with orders, orders with payments). Create test data factories that generate realistic entities: `createUserWithOrders()`, `createOrderWithPaymentHistory()`.

Sensitive API data must be masked: PII (names, emails, addresses), financial data (account numbers, amounts), and authentication tokens. Use data masking utilities in test responses and logs. Test data should be clearly identifiable as test data (test email domains, test account prefixes) to prevent confusion with production data.

Test data refresh strategies: APIs may have data dependencies (users must exist before orders can be created), state dependencies (orders transition through states), and cleanup requirements (test data must be removed). Implement test data setup/teardown that creates dependencies, manages state, and cleans up after tests.

API versioning requires test data management: test data for v1 APIs may not be compatible with v2 APIs. Maintain separate test datasets for each API version, or implement data transformation utilities that convert test data between versions.

### Test Environment Considerations

API test environments must match production API behavior: same authentication mechanisms, same rate limiting, same error handling. Differences can hide bugs or create false positives. Verify that test environments use production-like configurations: database schemas, caching layers, and external service integrations.

Shared test environments create isolation challenges: concurrent tests may create conflicting data, exhaust rate limits, or interfere with each other. Use isolated test environments per test run, or implement test data namespacing (unique prefixes, test user isolation) and cleanup between tests.

Environment-specific risks include: test databases with relaxed constraints, test environments missing security middleware, and test environments with different performance characteristics. Verify that test environments have equivalent constraints and security controls, or explicitly test differences as separate scenarios.

External service dependencies in test environments: APIs may depend on payment gateways, identity providers, or other services. Use test doubles (mocks, stubs) for external services, or use sandbox/test versions of external services. Verify that test doubles behave like production services, or document differences.

### Regression Strategy

API regression suites must include: core CRUD operations for all resources, authentication and authorization checks, error response validation, and contract compliance (request/response schemas). These represent the core API functionality that must never break.

Automation candidates for regression include: contract validation (OpenAPI schema compliance), authentication checks, error response format validation, and pagination correctness. These are deterministic and can be validated automatically.

Manual regression items include: complex business logic flows (multi-step operations), integration with external services (payment processing, notifications), and performance characteristics (response times, throughput). These require human judgment or external dependencies.

Trim regression suites by removing tests for deprecated endpoints, obsolete API versions, or rarely-used features. However, maintain tests for security-critical paths (authentication, authorization) even if they're simple—security regressions have high impact.

### Defect Patterns

Common API bugs include: missing input validation (malformed data accepted), incorrect error codes (500 instead of 400), missing authorization checks (unauthorized access), and pagination bugs (duplicate items, missing items). These patterns recur across APIs and should be tested explicitly.

Bugs tend to hide in: edge cases (boundary values, null handling), error paths (exception handling, timeout scenarios), and concurrent operations (race conditions, data corruption). Test these scenarios explicitly—they're common sources of production incidents.

Historical patterns show that API bugs cluster around: input validation (malformed requests), state management (resource state transitions), and integration points (external services, databases). Focus exploratory testing on these areas.

Triage guidance: API bugs affecting consumers are typically high severity due to integration impact. However, distinguish between breaking changes (consumers cannot work around) and non-breaking issues (consumers can work around). Breaking changes require immediate attention, while non-breaking issues can be prioritized based on impact.
