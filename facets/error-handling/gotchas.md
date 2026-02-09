# Error Handling -- Gotchas

Common pitfalls and traps that developers encounter when handling errors. These are the things that seem reasonable at first but cause problems down the road.

## Empty Catch Blocks

**The trap**: Catching an exception and doing nothing (empty catch block).

**Why it's wrong**: The error disappears silently. Bugs go undetected. Production issues become mysteries because errors were swallowed.

```kotlin
try {
    processOrder(order)
} catch (e: Exception) {
    // Empty - error disappears!
}
```

**The fix**: At minimum, log the error. Better, handle it explicitly or let it propagate.

```kotlin
try {
    processOrder(order)
} catch (e: Exception) {
    log.error("Failed to process order", e)
    // Now we know it failed
}
```

**When it's acceptable** (rare): Expected, recoverable errors that are already logged elsewhere, or cleanup operations that shouldn't fail the main operation. Even then, consider logging for observability.

## Returning 200 with Error Body

**The trap**: The API returns HTTP 200 with `{"success": false, "error": "..."}`.

**Why it's wrong**: HTTP clients treat this as a successful response. Monitoring doesn't catch it. Load balancers don't know it's an error. Retry logic doesn't trigger. You lose all the benefits of HTTP status codes.

```json
HTTP 200 OK
{
  "success": false,
  "error": "Invoice not found"
}
```

**The fix**: Use proper HTTP status codes. Return 404 for not found, 422 for validation errors, 500 for server errors.

```json
HTTP 404 Not Found
{
  "type": "https://api.example.com/errors/invoice-not-found",
  "title": "Invoice Not Found",
  "status": 404,
  "detail": "The invoice with ID 123 could not be found."
}
```

**Exception**: Some legacy systems or SOAP APIs use 200 with error bodies. If you must maintain compatibility, document it clearly and consider migrating to proper status codes.

## Exposing Stack Traces to Users

**The trap**: Spring Boot's default error response includes stack traces in development. If not reconfigured for production, internal implementation details leak to users and attackers.

**Why it's wrong**: Stack traces reveal:
- Internal file paths and directory structure
- Framework versions and dependencies
- Code structure and logic flow
- Database schema details (in some cases)
- Security vulnerabilities (SQL injection points, etc.)

Attackers use this information to craft targeted attacks.

**The fix**: Configure Spring Boot to hide stack traces in production:

```yaml
server:
  error:
    include-stacktrace: on_param  # Only show if ?trace=true
    include-message: always
    include-binding-errors: always
    include-exception: false  # Don't show exception class name
```

Or in code:

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(Exception::class)
    fun handleException(ex: Exception, request: HttpServletRequest): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred"
        )
        
        if (environment.activeProfiles.contains("dev")) {
            problemDetail.setProperty("stackTrace", ex.stackTraceToString())
        }
        
        return ResponseEntity.status(500).body(problemDetail)
    }
}
```

## Catching Exception Instead of Specific Types

**The trap**: `catch (Exception e)` catches everything including `NullPointerException`, `ClassCastException`, and other bugs that should crash loudly.

**Why it's wrong**: Catching `Exception` masks programming errors. `NullPointerException` indicates a bug that should be fixed, not caught and handled. Catching it hides the bug and makes debugging harder.

```kotlin
try {
    val order = orderService.getOrder(orderId)
    processOrder(order)  // NPE if order is null - this is a bug!
} catch (e: Exception) {
    // Catches NPE, hides the bug
    log.error("Error", e)
}
```

**The fix**: Catch specific, expected exceptions. Let programming errors (NPE, ClassCastException) crash loudly so they can be fixed.

```kotlin
try {
    val order = orderService.getOrder(orderId)
        ?: throw OrderNotFoundException(orderId)  // Explicit null handling
    processOrder(order)
} catch (e: BusinessException) {
    // Handle business exceptions
    handleBusinessError(e)
} catch (e: SystemException) {
    // Handle system exceptions
    handleSystemError(e)
}
// Let NPE, ClassCastException, etc. propagate - they're bugs
```

**When catching Exception is acceptable**: Top-level exception handlers (like `@RestControllerAdvice`) that need to catch everything to return a proper error response. Even then, log unexpected exceptions separately.

## Not Handling Async Errors

**The trap**: Errors in Promises, CompletableFutures, or coroutines that are not awaited disappear silently. Unhandled promise rejections crash Node.js.

**Why it's wrong**: Async errors don't propagate automatically. If you don't handle them, they're lost. In Node.js, unhandled promise rejections crash the process.

**JavaScript/Promise Example**:

```typescript
// Bad - error is lost
fetch('/api/orders')
    .then(res => res.json())
    .then(orders => {
        // If fetch fails, error is unhandled
    });

// Good - error is handled
fetch('/api/orders')
    .then(res => res.json())
    .then(orders => {
        // Handle success
    })
    .catch(error => {
        // Handle error
        Sentry.captureException(error);
        showErrorNotification('Failed to load orders');
    });
```

**Kotlin Coroutines Example**:

```kotlin
// Bad - exception is lost
launch {
    val order = orderService.getOrder(orderId)  // Exception not caught
    processOrder(order)
}

// Good - exception is handled
launch {
    try {
        val order = orderService.getOrder(orderId)
        processOrder(order)
    } catch (e: Exception) {
        log.error("Failed to process order", e)
        Sentry.captureException(e)
    }
}
```

**Java CompletableFuture Example**:

```java
// Bad - exception is lost
CompletableFuture.supplyAsync(() -> {
    return orderService.getOrder(orderId);  // Exception not handled
});

// Good - exception is handled
CompletableFuture.supplyAsync(() -> {
    return orderService.getOrder(orderId);
}).thenApply(order -> {
    return processOrder(order);
}).exceptionally(e -> {
    log.error("Failed to process order", e);
    return null;
});
```

## Retry Without Backoff

**The trap**: Retrying immediately after failure hammers the already-struggling service.

**Why it's wrong**: If a service is failing, retrying immediately adds more load. Without backoff, all retries from all clients hit at the same time (thundering herd problem). The service never recovers.

```kotlin
// Bad - immediate retry
repeat(3) {
    try {
        return externalService.call()
    } catch (e: Exception) {
        // Retry immediately - hammers the service
    }
}
```

**The fix**: Use exponential backoff with jitter. Wait longer between retries, and add randomness to prevent thundering herd.

```kotlin
// Good - exponential backoff with jitter
var attempt = 0
while (attempt < maxRetries) {
    try {
        return externalService.call()
    } catch (e: Exception) {
        if (!isRetryable(e) || attempt == maxRetries - 1) {
            throw e
        }
        val delay = calculateBackoff(attempt)
        Thread.sleep(delay)
        attempt++
    }
}

fun calculateBackoff(attempt: Int): Long {
    val exponentialDelay = initialDelayMs * Math.pow(2.0, attempt.toDouble()).toLong()
    val cappedDelay = minOf(exponentialDelay, maxDelayMs)
    val jitter = Random.nextLong(0, cappedDelay / 2)
    return cappedDelay + jitter
}
```

**Resilience4j** provides built-in retry with exponential backoff:

```kotlin
val retry = Retry.of("externalService", RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(100))
    .intervalFunction(IntervalFunction.ofExponentialBackoff(
        Duration.ofMillis(100),
        2.0
    ))
    .build()
)
```

## Error Messages That Help Attackers

**The trap**: "User admin@company.com not found" reveals that the email is not registered. "Invalid credentials" is the correct generic response for all auth failures.

**Why it's wrong**: Error messages that reveal information help attackers:
- User enumeration (which emails are registered)
- Path traversal hints (file paths in errors)
- SQL injection hints (database errors)
- Authentication bypass attempts (different errors for wrong password vs. user not found)

**Examples of Information Leakage**:

```kotlin
// Bad - reveals user existence
if (!userRepository.exists(email)) {
    throw UserNotFoundException(email)  // "User admin@company.com not found"
}

// Good - generic error
if (!userRepository.exists(email) || !passwordMatches(email, password)) {
    throw UnauthorizedException("Invalid credentials")
}
```

```kotlin
// Bad - reveals file path
throw FileNotFoundException("/etc/passwd not found")

// Good - generic error
throw NotFoundException("File not found")
```

```kotlin
// Bad - reveals SQL structure
catch (e: SQLException) {
    throw InternalServerException("Error executing SELECT * FROM users WHERE id = ?")
}

// Good - generic error
catch (e: SQLException) {
    log.error("Database error", e)
    throw InternalServerException("An error occurred")
}
```

**The fix**: Use generic error messages for security-sensitive operations. Log detailed errors server-side for debugging, but don't expose them to clients.

## Inconsistent Error Format

**The trap**: Different endpoints return errors in different formats. One returns `{"error": "..."}`, another returns `{"message": "...", "code": 123}`.

**Why it's wrong**: Frontend must handle multiple formats. Error handling code becomes complex and error-prone. Users see inconsistent error messages.

```json
// Endpoint 1
{
  "error": "Invoice not found"
}

// Endpoint 2
{
  "message": "Invoice not found",
  "code": 404
}

// Endpoint 3
{
  "status": "error",
  "data": {
    "message": "Invoice not found"
  }
}
```

**The fix**: Standardize on RFC 7807 Problem Details format across all endpoints. Use a global exception handler to ensure consistency.

```json
// All endpoints
{
  "type": "https://api.example.com/errors/invoice-not-found",
  "title": "Invoice Not Found",
  "status": 404,
  "detail": "The invoice with ID 123 could not be found.",
  "instance": "/api/invoices/123",
  "traceId": "abc-123"
}
```

## Not Testing Error Paths

**The trap**: 90% of tests cover the happy path. The other 10% cover basic validation. Edge cases, timeouts, concurrent modifications, and infrastructure failures go untested.

**Why it's wrong**: Production issues are frequently error scenarios that weren't tested. Timeouts, network errors, and concurrent modifications are common in production but rare in development.

**The fix**: For every happy path test, write corresponding error path tests:

- Test timeout scenarios
- Test network errors
- Test invalid input (boundary conditions, special characters)
- Test unauthorized/forbidden scenarios
- Test not found scenarios
- Test conflict scenarios (optimistic locking)
- Test server error scenarios
- Test concurrent modification scenarios

**Example**:

```kotlin
// Happy path test
@Test
fun `creates order successfully`() {
    val order = orderService.createOrder(createOrderRequest)
    assertNotNull(order.id)
}

// Error path tests
@Test
fun `returns 422 when validation fails`() { /* ... */ }
@Test
fun `returns 404 when product not found`() { /* ... */ }
@Test
fun `returns 409 when order already exists`() { /* ... */ }
@Test
fun `handles timeout when external service is slow`() { /* ... */ }
@Test
fun `handles concurrent modification`() { /* ... */ }
```

## Frontend Error Boundary Too High or Too Low

**The trap**: A single error boundary at the app root catches everything but shows a blank page. Error boundaries per button catch nothing useful.

**Why it's wrong**: Error boundaries that are too high (app root) catch everything but provide poor UX—the entire page is replaced with an error. Error boundaries that are too low (per button) catch nothing useful—errors propagate to parent boundaries anyway.

**The fix**: Place error boundaries around independent features/sections:

- One boundary per major feature (Orders section, Products section, Checkout flow)
- Independent features should have their own boundaries
- Critical paths (checkout, payment) should have tighter boundaries
- Don't put boundaries around every button or form field

**React Example**:

```typescript
// Good - boundary around independent feature
<App>
    <Header />
    <ErrorBoundary fallback={<OrdersErrorFallback />}>
        <OrdersSection />
    </ErrorBoundary>
    <ErrorBoundary fallback={<ProductsErrorFallback />}>
        <ProductsSection />
    </ErrorBoundary>
</App>

// Bad - boundary too high
<ErrorBoundary fallback={<AppErrorFallback />}>
    <App>
        <Header />
        <OrdersSection />
        <ProductsSection />
    </App>
</ErrorBoundary>

// Bad - boundary too low
<OrdersSection>
    {orders.map(order => (
        <ErrorBoundary fallback={<OrderErrorFallback />}>
            <OrderCard order={order} />
        </ErrorBoundary>
    ))}
</OrdersSection>
```

**Vue Example**:

```typescript
// Good - boundary around independent feature
<template>
    <Header />
    <ErrorBoundary>
        <OrdersSection />
    </ErrorBoundary>
    <ErrorBoundary>
        <ProductsSection />
    </ErrorBoundary>
</template>
```

## Not Propagating Correlation IDs

**The trap**: Errors occur but there's no way to trace them across services. Support can't find the related logs.

**Why it's wrong**: Without correlation IDs, debugging distributed systems is nearly impossible. You can't trace a request from frontend through API gateway through backend services.

**The fix**: Generate correlation IDs at the entry point (frontend or API gateway) and propagate them through all service calls. Include them in error responses and logs.

**Frontend**:
```typescript
const correlationId = crypto.randomUUID();
axios.defaults.headers.common['X-Correlation-ID'] = correlationId;
```

**Backend**:
```kotlin
@Component
class CorrelationIdFilter : Filter {
    override fun doFilter(request: ServletRequest, response: ServletResponse, chain: FilterChain) {
        val correlationId = request.getHeader("X-Correlation-ID") ?: UUID.randomUUID().toString()
        MDC.put("traceId", correlationId)
        response.setHeader("X-Correlation-ID", correlationId)
        try {
            chain.doFilter(request, response)
        } finally {
            MDC.remove("traceId")
        }
    }
}
```

**Service-to-Service**:
```kotlin
val headers = HttpHeaders()
headers.set("X-Correlation-ID", MDC.get("traceId"))
```

These gotchas are common sources of production issues. Avoiding them ensures more reliable, secure, and debuggable error handling.
