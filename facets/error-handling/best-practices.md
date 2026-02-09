# Error Handling -- Best Practices

## Contents

- [Use Domain-Specific Exceptions](#use-domain-specific-exceptions)
- [Never Swallow Exceptions Silently](#never-swallow-exceptions-silently)
- [Separate Client Errors from Server Errors](#separate-client-errors-from-server-errors)
- [Provide Actionable Error Messages](#provide-actionable-error-messages)
- [Include Error Codes for Machine Consumption](#include-error-codes-for-machine-consumption)
- [Retry Only Transient Errors](#retry-only-transient-errors)
- [Use Circuit Breakers for External Dependencies](#use-circuit-breakers-for-external-dependencies)
- [Stack-Specific Best Practices](#stack-specific-best-practices)
- [Error Handling Checklist](#error-handling-checklist)

Best practices for error handling that apply across languages and frameworks. These principles ensure errors are handled consistently, provide useful information, and don't expose security vulnerabilities.

## Use Domain-Specific Exceptions

Throw domain-specific exceptions instead of generic ones. `InvoiceNotFoundException` is better than `RuntimeException("Invoice not found")`. This makes exception handler mapping clean and error handling explicit.

**Good**:
```kotlin
throw InvoiceNotFoundException(invoiceId = "123")
```

**Bad**:
```kotlin
throw RuntimeException("Invoice not found: 123")
```

**Benefits**:
- Type-safe exception handling—catch specific types
- Clear mapping to HTTP status codes in exception handlers
- Domain language in exception names
- Compiler-enforced handling (with sealed classes)

**Exception Hierarchy**:
- Create a base exception hierarchy (BusinessException, SystemException)
- Use sealed classes (Kotlin) or final classes (Java) to prevent arbitrary exceptions
- Group related exceptions (all validation exceptions, all not-found exceptions)

## Never Swallow Exceptions Silently

Catching an exception and doing nothing (empty catch block) hides bugs. At minimum, log the exception. Better, handle it explicitly or let it propagate.

**Bad**:
```kotlin
try {
    processOrder(order)
} catch (e: Exception) {
    // Silently ignored - bug hidden!
}
```

**Better**:
```kotlin
try {
    processOrder(order)
} catch (e: Exception) {
    log.error("Failed to process order", e)
    // At least we know it failed
}
```

**Best**:
```kotlin
try {
    processOrder(order)
} catch (e: BusinessException) {
    // Handle business exception explicitly
    handleBusinessError(e)
} catch (e: SystemException) {
    // Handle system exception explicitly
    handleSystemError(e)
} catch (e: Exception) {
    // Unexpected exception - log and escalate
    log.error("Unexpected error processing order", e)
    throw InternalServerException("Order processing failed", e)
}
```

**When to Swallow** (rare exceptions):
- Expected, recoverable errors that are already logged elsewhere
- Cleanup operations that shouldn't fail the main operation
- Non-critical features that can degrade gracefully

Even in these cases, log the error for observability.

## Separate Client Errors from Server Errors

4xx errors are the client's fault (bad input, unauthorized). 5xx errors are the server's fault (bug, infrastructure failure). Don't return 500 for validation errors. Don't return 400 for server crashes.

**HTTP Status Code Guidelines**:

**Client Errors (4xx)** - Client's fault:
- **400 Bad Request**: Malformed request (invalid JSON, missing required headers)
- **401 Unauthorized**: Missing or invalid authentication credentials
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource state conflict
- **422 Unprocessable Entity**: Validation errors (preferred over 400)
- **429 Too Many Requests**: Rate limit exceeded

**Server Errors (5xx)** - Server's fault:
- **500 Internal Server Error**: Unexpected server error (bugs)
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily unavailable
- **504 Gateway Timeout**: Upstream service timeout

**Common Mistakes**:
- Returning 500 for validation errors → Use 422
- Returning 400 for server crashes → Use 500
- Returning 200 with error body → Use proper status codes

## Provide Actionable Error Messages

"Invalid email format" is better than "Validation error". "Service temporarily unavailable, please try again in a few minutes" is better than "Internal Server Error".

**Error Message Guidelines**:

**For Users**:
- Use plain language, not technical jargon
- Explain what went wrong
- Provide actionable next steps
- Show empathy ("We're sorry this happened")

**For Developers**:
- Include error codes for programmatic handling
- Include correlation IDs for tracing
- Include field-level details for validation errors
- Hide stack traces in production

**Examples**:

**Bad**:
```
Error: Validation failed
```

**Good**:
```
The email address you entered is invalid. Please check the format and try again.
```

**Better** (with field-level details):
```json
{
  "title": "Validation Error",
  "detail": "The request contains invalid fields",
  "errors": [
    {
      "field": "email",
      "message": "must be a valid email address"
    }
  ]
}
```

## Include Error Codes for Machine Consumption

Human-readable messages for display, machine-readable codes for programmatic handling. Error code "INVOICE_NOT_FOUND" is stable; the message text may change.

**Error Code Structure**:

```json
{
  "type": "https://api.example.com/errors/invoice-not-found",
  "code": "INVOICE_NOT_FOUND",
  "title": "Invoice Not Found",
  "detail": "The invoice with ID 123 could not be found.",
  "status": 404
}
```

**Error Code Guidelines**:
- Use UPPER_SNAKE_CASE for consistency
- Make codes stable (don't change them)
- Group related codes (INVOICE_*, ORDER_*, PAYMENT_*)
- Document all error codes in API documentation

**Benefits**:
- Frontend can handle errors programmatically
- Support can quickly identify issues
- Error codes are stable across API versions
- Messages can be localized without changing codes

## Retry Only Transient Errors

Retry on timeout, 503, connection refused. Don't retry on 400, 401, 403, 404. Retrying a validation error wastes resources and annoys rate limiters.

**Retryable Errors**:
- Timeouts (408, 504)
- Service unavailable (503)
- Connection errors (connection refused, network errors)
- Rate limit errors (429) - with exponential backoff

**Non-Retryable Errors**:
- Validation errors (400, 422)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Conflict errors (409)

**Retry Strategy**:
- Use exponential backoff with jitter
- Limit maximum retries (typically 3)
- Don't retry forever
- Log retry attempts for observability

**Implementation**:
```kotlin
fun isRetryable(e: Exception): Boolean {
    return when (e) {
        is SystemException.TimeoutException -> true
        is SystemException.ServiceUnavailableException -> true
        is java.net.SocketTimeoutException -> true
        is java.net.ConnectException -> true
        is BusinessException -> false
        else -> false
    }
}
```

## Use Circuit Breakers for External Dependencies

If a dependency fails repeatedly, stop calling it (circuit open). Periodically check if it's recovered (half-open). Resume normal calls when recovered (closed).

**Circuit Breaker States**:
- **Closed**: Normal operation, calls pass through
- **Open**: Dependency is failing, calls fail fast without calling dependency
- **Half-Open**: Testing if dependency recovered, allow limited calls

**When to Use Circuit Breakers**:
- External API calls (payment processors, third-party services)
- Database connections (if database is failing)
- Message queue consumers (if queue is unavailable)
- Any dependency that can fail and cause cascading failures

**Configuration**:
- Failure rate threshold (e.g., 50% failures opens circuit)
- Sliding window size (number of calls to evaluate)
- Wait duration in open state (how long before testing recovery)
- Half-open max calls (how many calls to test recovery)

**Benefits**:
- Prevents cascading failures
- Reduces load on failing dependencies
- Fails fast instead of timing out
- Automatic recovery when dependency recovers

## Stack-Specific Best Practices

### Kotlin

**Sealed Classes for Result Types**:
```kotlin
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Failure(val error: Throwable) : Result<Nothing>()
}

fun processOrder(order: Order): Result<Order> {
    return runCatching {
        orderService.save(order)
    }.fold(
        onSuccess = { Result.Success(it) },
        onFailure = { Result.Failure(it) }
    )
}
```

**runCatching for Functional Error Handling**:
```kotlin
val result = runCatching {
    riskyOperation()
}.onFailure { e ->
    log.error("Operation failed", e)
}.getOrElse {
    defaultValue
}
```

**require/check for Preconditions**:
```kotlin
fun createOrder(email: String, quantity: Int): Order {
    require(email.isNotBlank()) { "Email cannot be blank" }
    require(quantity > 0) { "Quantity must be positive" }
    // Proceed with order creation
}
```

### Spring Boot

**@RestControllerAdvice for Global Exception Handling**:
```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.NotFoundException::class)
    fun handleNotFound(ex: BusinessException.NotFoundException): ResponseEntity<ProblemDetail> {
        // Map to 404 response
    }
}
```

**ProblemDetail for RFC 7807 Responses** (Spring 6+):
```kotlin
val problemDetail = ProblemDetail.forStatusAndDetail(
    HttpStatus.NOT_FOUND,
    "Resource not found"
)
problemDetail.setProperty("resourceId", resourceId)
```

**@ResponseStatus on Exception Classes**:
```kotlin
@ResponseStatus(HttpStatus.NOT_FOUND)
class InvoiceNotFoundException(invoiceId: String) : RuntimeException("Invoice not found: $invoiceId")
```

**ResponseStatusException for Quick One-Off Errors**:
```kotlin
throw ResponseStatusException(
    HttpStatus.NOT_FOUND,
    "Invoice not found",
    InvoiceNotFoundException(invoiceId)
)
```

### Vue 3

**onErrorCaptured for Component Error Boundaries**:
```typescript
onErrorCaptured((err, instance, info) => {
    console.error('Error caught:', err, info);
    Sentry.captureException(err);
    return false; // Prevent error from propagating
});
```

**Global Error Handler**:
```typescript
app.config.errorHandler = (err, instance, info) => {
    console.error('Global error:', err, info);
    Sentry.captureException(err, {
        contexts: { vue: info }
    });
};
```

**Async Error Handling in Composables**:
```typescript
async function useOrders() {
    const orders = ref<Order[]>([]);
    const error = ref<Error | null>(null);
    
    try {
        orders.value = await apiRequest<Order[]>('/api/orders');
    } catch (e) {
        error.value = e as Error;
        Sentry.captureException(e);
    }
    
    return { orders, error };
}
```

### React

**ErrorBoundary Class Component** (no hooks equivalent yet):
```typescript
class ErrorBoundary extends React.Component {
    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        Sentry.captureException(error, {
            contexts: { react: errorInfo }
        });
    }
    // ... rest of implementation
}
```

**Error Handling in useEffect Cleanup**:
```typescript
useEffect(() => {
    const controller = new AbortController();
    
    fetch('/api/data', { signal: controller.signal })
        .then(res => res.json())
        .catch(err => {
            if (err.name !== 'AbortError') {
                handleError(err);
            }
        });
    
    return () => {
        controller.abort();
    };
}, []);
```

**Error States from TanStack Query useMutation**:
```typescript
const mutation = useMutation({
    mutationFn: createOrder,
    onError: (error) => {
        Sentry.captureException(error);
        showErrorNotification('Failed to create order');
    },
    onSuccess: () => {
        showSuccessNotification('Order created');
    }
});
```

## Error Handling Checklist

- [ ] Use domain-specific exceptions, not generic ones
- [ ] Never swallow exceptions silently (log at minimum)
- [ ] Separate client errors (4xx) from server errors (5xx)
- [ ] Provide actionable error messages for users
- [ ] Include error codes for machine consumption
- [ ] Retry only transient errors with exponential backoff
- [ ] Use circuit breakers for external dependencies
- [ ] Include correlation IDs in error responses
- [ ] Log errors with full context (but sanitize sensitive data)
- [ ] Hide stack traces in production
- [ ] Test error paths, not just happy paths
- [ ] Document all error codes and their meanings

Following these best practices ensures consistent, secure, and user-friendly error handling across your application.
