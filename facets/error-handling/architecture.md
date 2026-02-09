# Error Handling -- Architecture

Error handling architecture spans backend exception management, frontend error boundaries, API error responses, messaging retry patterns, and cross-cutting concerns like correlation IDs and error logging. This architecture ensures errors are caught, handled gracefully, and provide actionable information to users and operators.

## Backend Error Architecture

### Exception Hierarchy

Use domain-specific exceptions instead of generic RuntimeException. Create a clear exception hierarchy that maps to HTTP status codes and error categories.

**Base Exception Structure**:

```kotlin
sealed class ApplicationException(
    message: String,
    cause: Throwable? = null
) : RuntimeException(message, cause)

sealed class BusinessException(
    message: String,
    cause: Throwable? = null
) : ApplicationException(message, cause) {
    class ValidationException(
        val fieldErrors: Map<String, String>,
        message: String = "Validation failed"
    ) : BusinessException(message)
    
    class NotFoundException(
        val resourceType: String,
        val resourceId: String,
        message: String = "$resourceType not found: $resourceId"
    ) : BusinessException(message)
    
    class ConflictException(
        message: String,
        cause: Throwable? = null
    ) : BusinessException(message, cause)
    
    class UnauthorizedException(
        message: String = "Unauthorized"
    ) : BusinessException(message)
    
    class ForbiddenException(
        val requiredPermission: String? = null,
        message: String = "Forbidden"
    ) : BusinessException(message)
}

sealed class SystemException(
    message: String,
    cause: Throwable? = null
) : ApplicationException(message, cause) {
    class ServiceUnavailableException(
        val serviceName: String,
        message: String = "Service unavailable: $serviceName",
        cause: Throwable? = null
    ) : SystemException(message, cause)
    
    class TimeoutException(
        val operation: String,
        message: String = "Operation timed out: $operation",
        cause: Throwable? = null
    ) : SystemException(message, cause)
    
    class InternalServerException(
        message: String = "Internal server error",
        cause: Throwable? = null
    ) : SystemException(message, cause)
}
```

**Benefits**:
- Type-safe exception handling—catch specific exception types
- Clear mapping to HTTP status codes in exception handlers
- Domain language in exception names (InvoiceNotFoundException vs RuntimeException)
- Compiler-enforced handling (sealed classes require exhaustive when expressions)

### Global Exception Handler

Use Spring's `@RestControllerAdvice` to create a single global exception handler that maps exceptions to HTTP responses consistently across all endpoints.

**Spring Boot Exception Handler**:

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler(
    private val errorMapper: ErrorResponseMapper
) {
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
    
    @ExceptionHandler(BusinessException.NotFoundException::class)
    fun handleNotFoundException(
        ex: BusinessException.NotFoundException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            ex.message ?: "${ex.resourceType} not found"
        )
        problemDetail.setProperty("resourceType", ex.resourceType)
        problemDetail.setProperty("resourceId", ex.resourceId)
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(404).body(problemDetail)
    }
    
    @ExceptionHandler(BusinessException.UnauthorizedException::class)
    fun handleUnauthorizedException(
        ex: BusinessException.UnauthorizedException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.UNAUTHORIZED,
            ex.message ?: "Unauthorized"
        )
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(401).body(problemDetail)
    }
    
    @ExceptionHandler(BusinessException.ForbiddenException::class)
    fun handleForbiddenException(
        ex: BusinessException.ForbiddenException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.FORBIDDEN,
            ex.message ?: "Forbidden"
        )
        if (ex.requiredPermission != null) {
            problemDetail.setProperty("requiredPermission", ex.requiredPermission)
        }
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(403).body(problemDetail)
    }
    
    @ExceptionHandler(BusinessException.ConflictException::class)
    fun handleConflictException(
        ex: BusinessException.ConflictException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.CONFLICT,
            ex.message ?: "Conflict"
        )
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(409).body(problemDetail)
    }
    
    @ExceptionHandler(SystemException.ServiceUnavailableException::class)
    fun handleServiceUnavailableException(
        ex: SystemException.ServiceUnavailableException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.SERVICE_UNAVAILABLE,
            ex.message ?: "Service unavailable"
        )
        problemDetail.setProperty("serviceName", ex.serviceName)
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        problemDetail.setProperty("retryAfter", 60)
        return ResponseEntity.status(503).body(problemDetail)
    }
    
    @ExceptionHandler(SystemException.TimeoutException::class)
    fun handleTimeoutException(
        ex: SystemException.TimeoutException,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.REQUEST_TIMEOUT,
            ex.message ?: "Request timeout"
        )
        problemDetail.setProperty("operation", ex.operation)
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        return ResponseEntity.status(408).body(problemDetail)
    }
    
    @ExceptionHandler(Exception::class)
    fun handleGenericException(
        ex: Exception,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        log.error("Unhandled exception", ex)
        val problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred"
        )
        problemDetail.setProperty("instance", request.requestURI)
        problemDetail.setProperty("traceId", MDC.get("traceId"))
        if (environment.activeProfiles.contains("dev")) {
            problemDetail.setProperty("detail", ex.message)
            problemDetail.setProperty("stackTrace", ex.stackTraceToString())
        }
        return ResponseEntity.status(500).body(problemDetail)
    }
}
```

**Key Principles**:
- Single place for exception-to-HTTP mapping
- Consistent error response format (RFC 7807 Problem Details)
- Include correlation IDs for tracing
- Hide stack traces in production, show in development
- Map domain exceptions to appropriate HTTP status codes

### Error Response Format (RFC 7807 Problem Details)

Use RFC 7807 Problem Details for HTTP APIs. This standard format provides consistent error responses across all endpoints.

**Problem Details Structure**:

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
    },
    {
      "field": "quantity",
      "message": "must be greater than 0"
    }
  ],
  "traceId": "abc-123-def-456",
  "timestamp": "2026-02-09T10:30:00Z"
}
```

**Fields**:
- `type`: URI identifying the error type (stable, machine-readable)
- `title`: Short, human-readable summary
- `status`: HTTP status code (matches response status)
- `detail`: Human-readable explanation specific to this occurrence
- `instance`: URI identifying the specific occurrence
- `errors`: Array of field-level validation errors (for validation errors)
- `traceId`: Correlation ID for tracing across services
- `timestamp`: When the error occurred

**Spring Boot 6+ Support**:

Spring Boot 6+ includes native `ProblemDetail` support:

```kotlin
val problemDetail = ProblemDetail.forStatusAndDetail(
    HttpStatus.UNPROCESSABLE_ENTITY,
    "Validation failed"
)
problemDetail.setProperty("errors", fieldErrors)
```

### HTTP Status Code Mapping

Map exceptions to appropriate HTTP status codes:

**Client Errors (4xx)**:
- **400 Bad Request**: Malformed request (invalid JSON, missing required headers)
- **401 Unauthorized**: Missing or invalid authentication credentials
- **403 Forbidden**: Authenticated but not authorized for this operation
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Resource state conflict (duplicate creation, optimistic locking failure)
- **422 Unprocessable Entity**: Valid syntax but semantic validation failed (preferred over 400 for validation errors)
- **429 Too Many Requests**: Rate limit exceeded

**Server Errors (5xx)**:
- **500 Internal Server Error**: Unexpected server error (bugs, unhandled exceptions)
- **502 Bad Gateway**: Upstream service returned invalid response
- **503 Service Unavailable**: Service temporarily unavailable (maintenance, overload, dependency failure)
- **504 Gateway Timeout**: Upstream service didn't respond in time

**Guidelines**:
- Use 422 for validation errors (field-level errors)
- Use 400 for malformed requests (syntax errors)
- Use 500 for unexpected errors (bugs)
- Use 503 for planned unavailability or dependency failures
- Never return 200 with an error body—use proper status codes

### Retry Patterns

Implement retry patterns for transient failures. Not all errors should be retried—distinguish between transient errors (timeouts, 503) and permanent errors (400, 401, 403, 404).

**Exponential Backoff with Jitter**:

```kotlin
class RetryConfig(
    val maxRetries: Int = 3,
    val initialDelayMs: Long = 100,
    val maxDelayMs: Long = 5000,
    val multiplier: Double = 2.0,
    val jitter: Boolean = true
)

fun <T> retryWithBackoff(
    config: RetryConfig,
    operation: () -> T
): T {
    var attempt = 0
    var lastException: Exception? = null
    
    while (attempt < config.maxRetries) {
        try {
            return operation()
        } catch (e: Exception) {
            lastException = e
            if (!isRetryable(e) || attempt == config.maxRetries - 1) {
                throw e
            }
            val delay = calculateDelay(config, attempt)
            Thread.sleep(delay)
            attempt++
        }
    }
    throw lastException ?: RuntimeException("Retry failed")
}

fun isRetryable(e: Exception): Boolean {
    return when (e) {
        is SystemException.TimeoutException -> true
        is SystemException.ServiceUnavailableException -> true
        is java.net.SocketTimeoutException -> true
        is java.net.ConnectException -> true
        is BusinessException.ValidationException -> false
        is BusinessException.UnauthorizedException -> false
        is BusinessException.ForbiddenException -> false
        is BusinessException.NotFoundException -> false
        else -> false
    }
}

fun calculateDelay(config: RetryConfig, attempt: Int): Long {
    val exponentialDelay = (config.initialDelayMs * 
        Math.pow(config.multiplier, attempt.toDouble())).toLong()
    val cappedDelay = minOf(exponentialDelay, config.maxDelayMs)
    return if (config.jitter) {
        cappedDelay + Random.nextLong(0, cappedDelay / 2)
    } else {
        cappedDelay
    }
}
```

**Resilience4j Integration**:

Use Resilience4j for production-ready retry and circuit breaker patterns:

```kotlin
@Configuration
class ResilienceConfig {
    @Bean
    fun retryRegistry(): RetryRegistry {
        return RetryRegistry.of(
            RetryConfig.custom()
                .maxAttempts(3)
                .waitDuration(Duration.ofMillis(100))
                .intervalFunction(IntervalFunction.ofExponentialBackoff(
                    Duration.ofMillis(100),
                    2.0
                ))
                .retryOnException { e -> isRetryable(e) }
                .build()
        )
    }
    
    @Bean
    fun circuitBreakerRegistry(): CircuitBreakerRegistry {
        return CircuitBreakerRegistry.of(
            CircuitBreakerConfig.custom()
                .failureRateThreshold(50f)
                .waitDurationInOpenState(Duration.ofSeconds(30))
                .slidingWindowSize(10)
                .build()
        )
    }
}

@Service
class OrderService(
    private val retryRegistry: RetryRegistry,
    private val circuitBreakerRegistry: CircuitBreakerRegistry
) {
    fun createOrder(request: CreateOrderRequest): Order {
        val retry = retryRegistry.retry("orderService")
        val circuitBreaker = circuitBreakerRegistry.circuitBreaker("orderService")
        
        return circuitBreaker.executeSupplier {
            retry.executeSupplier {
                orderRepository.save(Order.from(request))
            }
        }
    }
}
```

**Circuit Breaker Pattern**:

Circuit breakers prevent cascading failures by stopping calls to failing dependencies:

- **Closed**: Normal operation, calls pass through
- **Open**: Dependency is failing, calls fail fast without calling dependency
- **Half-Open**: Testing if dependency recovered, allow limited calls

**Bulkhead Pattern**:

Bulkheads isolate dependency calls to prevent one slow dependency from blocking others:

```kotlin
@Bean
fun bulkheadRegistry(): BulkheadRegistry {
    return BulkheadRegistry.of(
        BulkheadConfig.custom()
            .maxConcurrentCalls(10)
            .maxWaitDuration(Duration.ofMillis(100))
            .build()
    )
}
```

### Dead Letter Queues

Messages that fail processing after N retries should be routed to a dead letter queue (DLQ) for manual inspection and replay.

**Kafka Dead Letter Queue Pattern**:

```kotlin
@KafkaListener(
    topics = ["orders"],
    groupId = "order-processor"
)
fun processOrder(message: ConsumerRecord<String, OrderEvent>) {
    try {
        orderService.processOrder(message.value())
    } catch (e: Exception) {
        if (isRetryable(e) && message.headers().lastHeader("retry-count")?.value()?.let { 
            String(it).toInt() 
        } ?: 0 < MAX_RETRIES) {
            val retryCount = (message.headers().lastHeader("retry-count")?.value()?.let { 
                String(it).toInt() 
            } ?: 0) + 1
            val headers = message.headers().toMutableList()
            headers.add(RecordHeader("retry-count", retryCount.toString().toByteArray()))
            kafkaTemplate.send(
                "orders-retry",
                message.key(),
                message.value(),
                headers
            )
        } else {
            kafkaTemplate.send(
                "orders-dlq",
                message.key(),
                message.value()
            )
            log.error("Message sent to DLQ after retries exhausted", e)
        }
    }
}
```

**DLQ Management**:
- Monitor DLQ depth (alert if growing)
- Provide tooling to inspect DLQ messages
- Support replaying DLQ messages after fixes
- Analyze DLQ messages to identify systemic issues

## Frontend Error Architecture

### Error Boundaries

Error boundaries catch rendering errors in a component subtree and display fallback UI instead of crashing the entire page.

**React Error Boundary**:

```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ComponentType<{ error: Error }> },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    Sentry.captureException(error, {
      contexts: { react: errorInfo },
      tags: { errorBoundary: true }
    });
  }

  render() {
    if (this.state.hasError) {
      const Fallback = this.props.fallback || DefaultErrorFallback;
      return <Fallback error={this.state.error!} />;
    }
    return this.props.children;
  }
}

function DefaultErrorFallback({ error }: { error: Error }) {
  return (
    <div className="error-boundary">
      <h2>Something went wrong</h2>
      <p>We're sorry, but something unexpected happened.</p>
      <button onClick={() => window.location.reload()}>
        Reload Page
      </button>
    </div>
  );
}
```

**Vue 3 Error Boundary**:

```typescript
export function useErrorBoundary() {
  const error = ref<Error | null>(null);
  
  const captureError = (err: Error, instance: ComponentPublicInstance | null) => {
    error.value = err;
    console.error('Error caught by boundary:', err);
    Sentry.captureException(err, {
      contexts: { vue: { component: instance?.$options.name } },
      tags: { errorBoundary: true }
    });
  };
  
  return { error, captureError };
}

export default defineComponent({
  setup(_, { slots }) {
    const { error, captureError } = useErrorBoundary();
    
    onErrorCaptured((err, instance, info) => {
      captureError(err, instance);
      return false;
    });
    
    return () => {
      if (error.value) {
        return h(ErrorFallback, { error: error.value });
      }
      return slots.default?.();
    };
  }
});
```

**Error Boundary Placement Strategy**:
- One boundary per major feature/section (not at root, not per button)
- Independent features should have their own boundaries
- Critical paths (checkout, payment) should have tighter boundaries

### API Error Handling

Centralize API error handling with interceptors that handle common errors consistently.

**Axios Interceptor (React/Vue)**:

```typescript
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Redirect to login
          window.location.href = '/login';
          break;
        case 403:
          // Show permission denied page
          router.push('/forbidden');
          break;
        case 429:
          // Retry with exponential backoff
          return retryWithBackoff(() => axios.request(error.config));
        case 500:
        case 502:
        case 503:
          // Show generic error message
          showErrorNotification('Service temporarily unavailable. Please try again.');
          break;
        default:
          // Show error from response
          showErrorNotification(data.detail || 'An error occurred');
      }
    } else if (error.request) {
      // Network error
      showErrorNotification('Network error. Please check your connection.');
    } else {
      // Request setup error
      showErrorNotification('An unexpected error occurred.');
    }
    
    return Promise.reject(error);
  }
);
```

**Fetch Wrapper**:

```typescript
async function apiRequest<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.detail, response.status, error);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      handleApiError(error);
      throw error;
    }
    throw new NetworkError('Network request failed', error);
  }
}
```

### Error State Management

Manage loading/success/error states for every async operation. TanStack Query (React) and VueQuery (Vue) handle this automatically.

**TanStack Query Error Handling**:

```typescript
function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => apiRequest<Order[]>('/api/orders'),
    retry: (failureCount, error) => {
      if (error instanceof ApiError) {
        return error.status >= 500 && failureCount < 3;
      }
      return false;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

function OrdersList() {
  const { data, error, isLoading } = useOrders();
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  return <OrdersTable orders={data} />;
}
```

**VueQuery Error Handling**:

```typescript
function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => apiRequest<Order[]>('/api/orders'),
    retry: (failureCount, error) => {
      if (error instanceof ApiError) {
        return error.status >= 500 && failureCount < 3;
      }
      return false;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
```

### User-Facing Error Messages

Never show technical errors to users. Map error codes to user-friendly messages.

**Error Message Mapping**:

```typescript
const ERROR_MESSAGES: Record<string, string> = {
  'VALIDATION_ERROR': 'Please check your input and try again.',
  'INVOICE_NOT_FOUND': 'This invoice could not be found.',
  'UNAUTHORIZED': 'Please sign in to continue.',
  'FORBIDDEN': 'You don\'t have permission to perform this action.',
  'SERVICE_UNAVAILABLE': 'The service is temporarily unavailable. Please try again in a few minutes.',
  'NETWORK_ERROR': 'Network error. Please check your connection.',
  'TIMEOUT': 'The request timed out. Please try again.',
};

function getUserFriendlyMessage(error: ApiError): string {
  return ERROR_MESSAGES[error.code] || 
    ERROR_MESSAGES[error.status.toString()] || 
    'An unexpected error occurred. Please try again.';
}
```

**Error Display Patterns**:
- **Validation errors**: Inline near the field
- **System errors**: Toast notifications with retry buttons
- **Fatal errors**: Full-page error state with navigation options

### Error Reporting

Capture frontend errors and send to error tracking service (Sentry) with full context.

**Sentry Integration**:

```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.VITE_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

// Capture exceptions
window.addEventListener('error', (event) => {
  Sentry.captureException(event.error, {
    tags: { errorType: 'unhandled' },
    contexts: { browser: { url: window.location.href } },
  });
});

// Capture unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  Sentry.captureException(event.reason, {
    tags: { errorType: 'unhandledPromiseRejection' },
  });
});
```

**Error Context**:
- User ID, email, role
- Breadcrumbs (recent actions)
- Stack traces with source maps
- Request/response data (sanitized)
- Browser/device information

## Cross-Cutting Concerns

### Correlation IDs

Propagate correlation IDs from frontend through API gateway through backend services. Include in error responses so support can trace the full request path.

**Frontend Correlation ID Generation**:

```typescript
const correlationId = crypto.randomUUID();
axios.defaults.headers.common['X-Correlation-ID'] = correlationId;
```

**Backend Correlation ID Propagation**:

```kotlin
@Component
class CorrelationIdFilter : Filter {
    override fun doFilter(
        request: ServletRequest,
        response: ServletResponse,
        chain: FilterChain
    ) {
        val correlationId = request.getHeader("X-Correlation-ID") 
            ?: UUID.randomUUID().toString()
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

**Service-to-Service Propagation**:

```kotlin
@Service
class OrderService(
    private val restTemplate: RestTemplate
) {
    fun createOrder(request: CreateOrderRequest): Order {
        val headers = HttpHeaders()
        headers.set("X-Correlation-ID", MDC.get("traceId"))
        val httpRequest = HttpEntity(request, headers)
        return restTemplate.postForObject("/api/orders", httpRequest, Order::class.java)
    }
}
```

### Error Logging

Log errors with full context (request, user, trace ID) but without sensitive data (passwords, tokens).

**Structured Error Logging**:

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(Exception::class)
    fun handleException(
        ex: Exception,
        request: HttpServletRequest
    ): ResponseEntity<ProblemDetail> {
        log.error(
            "Unhandled exception",
            ex,
            mapOf(
                "traceId" to MDC.get("traceId"),
                "userId" to getCurrentUserId(),
                "path" to request.requestURI,
                "method" to request.method,
                "status" to 500
            )
        )
        // ... return error response
    }
}
```

**Log Levels**:
- **ERROR**: Unhandled exceptions, system failures
- **WARN**: Recoverable errors, retryable failures
- **INFO**: Business exceptions (validation, not found) logged for audit
- **DEBUG**: Detailed error context (only in development)

**Sensitive Data Sanitization**:

```kotlin
fun sanitizeForLogging(data: Any): String {
    val json = objectMapper.writeValueAsString(data)
    return json.replace(
        Regex("""(password|token|secret|apiKey)["\s]*:["\s]*[^,}\]]+""", 
            RegexOption.IGNORE_CASE),
        "$1: [REDACTED]"
    )
}
```

### Graceful Degradation

When a non-critical service fails, degrade gracefully. Show cached data, disable the feature, show a "temporarily unavailable" message. Don't crash the entire page/service.

**Feature Flags for Degradation**:

```kotlin
@Service
class RecommendationService {
    fun getRecommendations(productId: String): List<Product> {
        return try {
            recommendationClient.getRecommendations(productId)
        } catch (e: Exception) {
            log.warn("Recommendation service failed, using fallback", e)
            getDefaultRecommendations(productId)
        }
    }
    
    private fun getDefaultRecommendations(productId: String): List<Product> {
        return productRepository.findSimilarProducts(productId, limit = 5)
    }
}
```

**Frontend Degradation**:

```typescript
function ProductPage({ productId }: { productId: string }) {
  const { data: recommendations, error } = useRecommendations(productId);
  
  return (
    <div>
      <ProductDetails productId={productId} />
      <ErrorBoundary fallback={<RecommendationsUnavailable />}>
        {error ? (
          <DefaultRecommendations productId={productId} />
        ) : (
          <RecommendationsList recommendations={recommendations} />
        )}
      </ErrorBoundary>
    </div>
  );
}
```

This architecture ensures errors are caught at appropriate boundaries, handled gracefully, and provide actionable information to users and operators while maintaining system stability and observability.
