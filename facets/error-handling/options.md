# Error Handling -- Options

## Contents

- [Recommended Error Handling Stack](#recommended-error-handling-stack)
- [Backend Error Response Format Options](#backend-error-response-format-options)
- [Resilience Pattern Options](#resilience-pattern-options)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)
- [Decision Guidance](#decision-guidance)

Decision matrix and recommended practices for error handling architecture, error response formats, and resilience patterns.

## Recommended Error Handling Stack

**Backend**:
- `@RestControllerAdvice` + domain exceptions + RFC 7807 ProblemDetail (Spring 6+)
- Sealed exception hierarchy (BusinessException, SystemException)
- Correlation ID propagation via MDC
- Structured error logging with sanitization

**Frontend**:
- Error boundaries per feature section
- Centralized API error interceptor (Axios interceptor or fetch wrapper)
- Error tracking (Sentry) with user context and breadcrumbs
- Error state management via TanStack Query/VueQuery

**Messaging**:
- Dead letter queues for failed messages
- Configurable retry with exponential backoff and jitter
- DLQ monitoring and replay tooling

**Cross-Cutting**:
- Correlation IDs in all error responses
- Structured error logging (OpenTelemetry, structured JSON logs)
- Error sanitization (no passwords, tokens, or PII in logs)

## Backend Error Response Format Options

### Option 1: RFC 7807 Problem Details (Recommended)

**Description**: Standard HTTP API error format (RFC 7807). Spring Boot 6+ includes native `ProblemDetail` support.

**Format**:
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request contains invalid fields",
  "instance": "/api/orders/123",
  "errors": [
    {
      "field": "email",
      "message": "must be a valid email address"
    }
  ],
  "traceId": "abc-123-def-456",
  "timestamp": "2026-02-09T10:30:00Z"
}
```

**Pros**:
- Standard format (RFC 7807)
- Spring Boot 6+ native support (`ProblemDetail`)
- Consistent across all endpoints
- Machine-readable error types
- Extensible (custom properties)

**Cons**:
- Requires Spring Boot 6+ for native support (or manual implementation)
- Slightly more verbose than custom formats

**When to Use**: Default choice for all new APIs. Migrate existing APIs when possible.

**Implementation**:
```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.ValidationException::class)
    fun handleValidationException(
        ex: BusinessException.ValidationException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.UNPROCESSABLE_ENTITY,
            ex.message ?: "Validation failed"
        )
        problemDetail.setProperty("errors", ex.fieldErrors)
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(422).body(problemDetail)
    }
}
```

### Option 2: Custom JSON Format

**Description**: Team-defined error response structure.

**Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": "must be a valid email address"
    }
  },
  "requestId": "abc-123"
}
```

**Pros**:
- Flexible structure
- Can be simpler than RFC 7807
- Works with any Spring Boot version

**Cons**:
- Not standardized (each team defines their own)
- Inconsistent across different APIs
- Requires custom exception handler implementation
- Less discoverable (not a standard)

**When to Use**: Legacy systems that can't migrate to RFC 7807, or teams that prefer custom formats for specific reasons.

**Implementation**:
```kotlin
data class ErrorResponse(
    val error: ErrorDetail,
    val requestId: String
)

data class ErrorDetail(
    val code: String,
    val message: String,
    val details: Map<String, String>? = null
)

@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.ValidationException::class)
    fun handleValidationException(
        ex: BusinessException.ValidationException,
        request: HttpServletRequest
    ): ResponseEntity<ErrorResponse> {
        val errorResponse = ErrorResponse(
            error = ErrorDetail(
                code = "VALIDATION_ERROR",
                message = "Validation failed",
                details = ex.fieldErrors
            ),
            requestId = MDC.get("traceId") ?: UUID.randomUUID().toString()
        )
        return ResponseEntity.status(422).body(errorResponse)
    }
}
```

### Option 3: Plain Text / HTML Errors (Spring Boot Defaults)

**Description**: Spring Boot's default error responses (Whitelabel error page, or JSON with basic structure).

**Format**:
```json
{
  "timestamp": "2026-02-09T10:30:00.000+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "No message available",
  "path": "/api/orders/123"
}
```

**Pros**:
- Zero configuration (Spring Boot default)
- Works out of the box

**Cons**:
- Not standardized
- Limited extensibility
- Inconsistent with custom error responses
- Doesn't support field-level validation errors well

**When to Use**: Only for quick prototypes or internal tools. Not recommended for production APIs.

**Evaluation Criteria**:

| Criterion | RFC 7807 | Custom JSON | Plain Text/HTML |
|-----------|----------|-------------|-----------------|
| Standardization | ✅ Standard | ❌ Custom | ❌ Framework default |
| Consistency | ✅ High | ⚠️ Team-dependent | ❌ Low |
| Extensibility | ✅ High | ⚠️ Medium | ❌ Low |
| Spring Boot Support | ✅ Native (6+) | ⚠️ Manual | ✅ Default |
| Field-level Errors | ✅ Yes | ✅ Yes | ❌ Limited |
| Machine-readable | ✅ Yes | ⚠️ Custom | ❌ Limited |

**Recommendation**: Use RFC 7807 Problem Details for all new APIs. Migrate existing APIs when possible. Use custom JSON only for legacy systems that can't migrate.

## Resilience Pattern Options

### Option 1: Retry with Exponential Backoff (Recommended)

**Description**: Retry transient failures with exponential backoff and jitter.

**When to Use**: Transient failures (timeouts, 503 Service Unavailable, connection errors).

**Configuration**:
- Max retries: 3
- Initial delay: 100ms
- Multiplier: 2.0
- Max delay: 5 seconds
- Jitter: Yes (randomize delay to prevent thundering herd)

**Pros**:
- Handles transient failures automatically
- Prevents thundering herd with jitter
- Configurable retry logic

**Cons**:
- Adds latency (retries take time)
- Doesn't help with persistent failures

**Implementation**: Use Resilience4j Retry or custom retry logic with exponential backoff.

### Option 2: Circuit Breaker (Resilience4j)

**Description**: Stop calling failing dependencies (circuit open), periodically test recovery (half-open), resume when recovered (closed).

**When to Use**: External dependencies that can fail persistently (payment processors, third-party APIs, databases).

**Configuration**:
- Failure rate threshold: 50%
- Sliding window size: 10 calls
- Wait duration in open state: 30 seconds
- Half-open max calls: 3

**Pros**:
- Prevents cascading failures
- Fails fast instead of timing out
- Automatic recovery when dependency recovers

**Cons**:
- Requires configuration tuning
- Can delay recovery if threshold is too high

**Implementation**: Use Resilience4j CircuitBreaker.

### Option 3: Bulkhead

**Description**: Isolate dependency calls to prevent one slow dependency from blocking others.

**When to Use**: When you have multiple dependencies and want to isolate their failures.

**Configuration**:
- Max concurrent calls: 10 per dependency
- Max wait duration: 100ms

**Pros**:
- Prevents one slow dependency from blocking others
- Provides isolation between dependency calls

**Cons**:
- Requires careful configuration
- May reject calls if bulkhead is full

**Implementation**: Use Resilience4j Bulkhead.

### Option 4: Fallback

**Description**: Return cached data or default values when a dependency fails.

**When to Use**: Non-critical features that can degrade gracefully (recommendations, analytics, non-essential data).

**Pros**:
- Provides graceful degradation
- Users see something instead of errors

**Cons**:
- Requires fallback data/logic
- May show stale data

**Implementation**: Custom fallback logic in service layer.

**Evaluation Criteria**:

| Criterion | Retry | Circuit Breaker | Bulkhead | Fallback |
|-----------|-------|-----------------|----------|----------|
| Transient Failures | ✅ Excellent | ⚠️ Good | ❌ No | ❌ No |
| Persistent Failures | ❌ No | ✅ Excellent | ⚠️ Good | ✅ Excellent |
| Cascading Failure Prevention | ❌ No | ✅ Excellent | ⚠️ Good | ⚠️ Good |
| Graceful Degradation | ❌ No | ❌ No | ❌ No | ✅ Excellent |
| Complexity | ✅ Low | ⚠️ Medium | ⚠️ Medium | ⚠️ Medium |

**Recommendation**: Use retry with exponential backoff for transient failures. Use circuit breakers for external dependencies. Use bulkheads when you need isolation. Use fallbacks for non-critical features.

## Synergies

**Retry + Circuit Breaker**: Retry transient failures, but open circuit if failures persist. Prevents infinite retries on persistent failures.

**Circuit Breaker + Bulkhead**: Isolate dependency calls and prevent cascading failures. One failing dependency doesn't affect others.

**Fallback + Circuit Breaker**: When circuit is open, return fallback data instead of failing. Provides graceful degradation.

**Correlation IDs + Error Logging**: Correlation IDs enable tracing errors across services. Structured error logging provides context for debugging.

**Error Boundaries + Error Tracking**: Error boundaries catch frontend errors. Error tracking (Sentry) captures them with context for debugging.

## Evolution Triggers

**Migrate to RFC 7807 when**:
- Starting a new API
- Major API version bump (opportunity to change format)
- Standardization initiative across teams
- Spring Boot 6+ upgrade (native support)

**Add Circuit Breaker when**:
- External dependency failures cause cascading failures
- Dependency failures are frequent (more than occasional)
- Dependency is critical (payment, authentication)

**Add Retry when**:
- Transient failures are common (timeouts, 503)
- Network instability causes occasional failures
- External services have occasional hiccups

**Add Error Boundaries when**:
- Frontend errors crash entire pages
- Independent features fail and affect whole app
- Error recovery UX needs improvement

**Add Dead Letter Queue when**:
- Message processing failures need manual inspection
- Failed messages need replay after fixes
- Message failure patterns need analysis

## Decision Guidance

**For New Projects**: Start with RFC 7807 Problem Details, retry with exponential backoff, error boundaries per feature, and correlation IDs. Add circuit breakers and DLQs as needed.

**For Existing Projects**: 
1. Add correlation IDs first (low risk, high value)
2. Standardize error response format (migrate to RFC 7807 gradually)
3. Add error boundaries to critical features
4. Add retry logic for transient failures
5. Add circuit breakers for problematic dependencies

**For High-Volume APIs**: Prioritize circuit breakers and bulkheads to prevent cascading failures. Monitor error rates and DLQ depth.

**For User-Facing Applications**: Prioritize error boundaries and user-friendly error messages. Ensure errors don't crash the entire app.

This decision matrix provides guidance for choosing error handling patterns that match your system's needs and constraints.
