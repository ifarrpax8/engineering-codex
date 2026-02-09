# API Design -- Testing

API testing ensures contracts are honored, implementations match specifications, and changes don't break consumers. Test at multiple levels: contracts, integration, performance, and security.

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
