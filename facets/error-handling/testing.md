# Error Handling -- Testing

## Contents

- [Testing Exception Handlers](#testing-exception-handlers)
- [Testing Validation Errors](#testing-validation-errors)
- [Testing Error Boundaries (Frontend)](#testing-error-boundaries-frontend)
- [Testing Retry Logic](#testing-retry-logic)
- [Testing Dead Letter Queue](#testing-dead-letter-queue)
- [Testing Graceful Degradation](#testing-graceful-degradation)
- [Testing Error Reporting](#testing-error-reporting)
- [Testing Error Response Contracts](#testing-error-response-contracts)
- [Negative Testing Patterns](#negative-testing-patterns)

Testing error handling ensures that errors are caught, handled correctly, and provide useful information to users and operators. Error path testing is often neglected but is critical—production issues are frequently error scenarios that weren't tested.

## Testing Exception Handlers

Verify that `@ControllerAdvice` maps exceptions to correct HTTP status codes and response formats. Test each exception type produces the expected error response.

**Spring Boot Exception Handler Tests**:

```kotlin
@WebMvcTest(GlobalExceptionHandler::class)
class GlobalExceptionHandlerTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `handles ValidationException with 422 status`() {
        val fieldErrors = mapOf(
            "email" to "must be a valid email address",
            "quantity" to "must be greater than 0"
        )
        val exception = BusinessException.ValidationException(fieldErrors)
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.status").value(422))
            .andExpect(jsonPath("$.title").value("Validation Error"))
            .andExpect(jsonPath("$.errors").exists())
            .andExpect(jsonPath("$.errors.email").value("must be a valid email address"))
            .andExpect(jsonPath("$.traceId").exists())
    }
    
    @Test
    fun `handles NotFoundException with 404 status`() {
        val exception = BusinessException.NotFoundException("Invoice", "123")
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isNotFound)
            .andExpect(jsonPath("$.status").value(404))
            .andExpect(jsonPath("$.title").value("Not Found"))
            .andExpect(jsonPath("$.resourceType").value("Invoice"))
            .andExpect(jsonPath("$.resourceId").value("123"))
    }
    
    @Test
    fun `handles UnauthorizedException with 401 status`() {
        val exception = BusinessException.UnauthorizedException()
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isUnauthorized)
            .andExpect(jsonPath("$.status").value(401))
            .andExpect(jsonPath("$.title").value("Unauthorized"))
    }
    
    @Test
    fun `handles ForbiddenException with 403 status and requiredPermission`() {
        val exception = BusinessException.ForbiddenException(requiredPermission = "orders:write")
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isForbidden)
            .andExpect(jsonPath("$.status").value(403))
            .andExpect(jsonPath("$.requiredPermission").value("orders:write"))
    }
    
    @Test
    fun `handles ServiceUnavailableException with 503 status and retryAfter`() {
        val exception = SystemException.ServiceUnavailableException("payment-service")
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isServiceUnavailable)
            .andExpect(jsonPath("$.status").value(503))
            .andExpect(jsonPath("$.serviceName").value("payment-service"))
            .andExpect(jsonPath("$.retryAfter").exists())
    }
    
    @Test
    fun `handles generic Exception with 500 status`() {
        val exception = RuntimeException("Unexpected error")
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect(status().isInternalServerError)
            .andExpect(jsonPath("$.status").value(500))
            .andExpect(jsonPath("$.title").value("Internal Server Error"))
            .andExpect(jsonPath("$.traceId").exists())
    }
    
    @Test
    fun `includes stack trace in development mode only`() {
        val exception = RuntimeException("Test error")
        
        mockMvc.perform(get("/test-endpoint"))
            .andExpect {
                if (environment.activeProfiles.contains("dev")) {
                    jsonPath("$.stackTrace").exists()
                } else {
                    jsonPath("$.stackTrace").doesNotExist()
                }
            }
    }
}
```

**Integration Tests for Exception Handling**:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerErrorHandlingTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @MockBean
    lateinit var orderService: OrderService
    
    @Test
    fun `returns 422 when validation fails`() {
        whenever(orderService.createOrder(any()))
            .thenThrow(BusinessException.ValidationException(
                mapOf("email" to "must be a valid email address")
            ))
        
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": "invalid-email"}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").value("must be a valid email address"))
    }
    
    @Test
    fun `returns 404 when order not found`() {
        whenever(orderService.getOrder("123"))
            .thenThrow(BusinessException.NotFoundException("Order", "123"))
        
        mockMvc.perform(get("/api/orders/123"))
            .andExpect(status().isNotFound)
            .andExpect(jsonPath("$.resourceType").value("Order"))
            .andExpect(jsonPath("$.resourceId").value("123"))
    }
}
```

## Testing Validation Errors

Send invalid input and verify 400/422 responses with field-level error messages. Test boundary conditions (empty, too long, wrong format, special characters).

**Validation Error Test Cases**:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class OrderValidationTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `rejects empty email`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": ""}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").exists())
    }
    
    @Test
    fun `rejects invalid email format`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": "not-an-email"}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").value(containsString("email")))
    }
    
    @Test
    fun `rejects negative quantity`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"quantity": -1}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.quantity").exists())
    }
    
    @Test
    fun `rejects quantity exceeding maximum`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"quantity": 10001}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.quantity").value(containsString("maximum")))
    }
    
    @Test
    fun `rejects missing required fields`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").exists())
            .andExpect(jsonPath("$.errors.quantity").exists())
    }
    
    @Test
    fun `rejects special characters in fields that should not have them`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": "test<script>alert('xss')</script>@example.com"}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").exists())
    }
    
    @Test
    fun `returns multiple validation errors at once`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": "invalid", "quantity": -1}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors.email").exists())
            .andExpect(jsonPath("$.errors.quantity").exists())
    }
}
```

## Testing Error Boundaries (Frontend)

Trigger errors in child components and verify error boundaries render fallback UI. Verify errors are reported to error tracking service.

**React Error Boundary Tests**:

```typescript
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';

function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders fallback UI when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('reports error to Sentry', () => {
    const captureExceptionSpy = jest.spyOn(Sentry, 'captureException');
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(captureExceptionSpy).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        tags: { errorBoundary: true }
      })
    );
  });

  it('allows page reload on error', () => {
    const reloadSpy = jest.spyOn(window.location, 'reload').mockImplementation(() => {});
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    const reloadButton = screen.getByText('Reload Page');
    reloadButton.click();
    
    expect(reloadSpy).toHaveBeenCalled();
  });
});
```

**Vue Error Boundary Tests**:

```typescript
import { mount } from '@vue/test-utils';
import ErrorBoundary from './ErrorBoundary.vue';

const ThrowError = defineComponent({
  props: { shouldThrow: Boolean },
  setup(props) {
    if (props.shouldThrow) {
      throw new Error('Test error');
    }
    return () => h('div', 'No error');
  }
});

describe('ErrorBoundary', () => {
  it('renders children when no error occurs', () => {
    const wrapper = mount(ErrorBoundary, {
      slots: {
        default: () => h(ThrowError, { shouldThrow: false })
      }
    });
    expect(wrapper.text()).toBe('No error');
  });

  it('renders fallback UI when error occurs', () => {
    const wrapper = mount(ErrorBoundary, {
      slots: {
        default: () => h(ThrowError, { shouldThrow: true })
      }
    });
    expect(wrapper.text()).toContain('Something went wrong');
  });

  it('reports error to Sentry', () => {
    const captureExceptionSpy = jest.spyOn(Sentry, 'captureException');
    
    mount(ErrorBoundary, {
      slots: {
        default: () => h(ThrowError, { shouldThrow: true })
      }
    });
    
    expect(captureExceptionSpy).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        tags: { errorBoundary: true }
      })
    );
  });
});
```

## Testing Retry Logic

Mock a service that fails N times then succeeds. Verify retry behavior (correct number of retries, backoff timing). Verify circuit breaker opens after threshold.

**Retry Logic Tests**:

```kotlin
class RetryServiceTest {
    @Mock
    lateinit var externalService: ExternalService
    
    @Test
    fun `retries on transient failure and succeeds`() {
        whenever(externalService.call())
            .thenThrow(SystemException.TimeoutException("operation"))
            .thenThrow(SystemException.ServiceUnavailableException("service"))
            .thenReturn(Success("result"))
        
        val result = retryService.executeWithRetry {
            externalService.call()
        }
        
        assertEquals(Success("result"), result)
        verify(externalService, times(3)).call()
    }
    
    @Test
    fun `gives up after max retries`() {
        whenever(externalService.call())
            .thenThrow(SystemException.TimeoutException("operation"))
        
        assertThrows<SystemException.TimeoutException> {
            retryService.executeWithRetry {
                externalService.call()
            }
        }
        
        verify(externalService, times(3)).call()
    }
    
    @Test
    fun `does not retry on non-retryable errors`() {
        whenever(externalService.call())
            .thenThrow(BusinessException.ValidationException(emptyMap()))
        
        assertThrows<BusinessException.ValidationException> {
            retryService.executeWithRetry {
                externalService.call()
            }
        }
        
        verify(externalService, times(1)).call()
    }
    
    @Test
    fun `implements exponential backoff`() {
        val clock = TestClock()
        val delays = mutableListOf<Long>()
        
        whenever(externalService.call())
            .thenThrow(SystemException.TimeoutException("operation"))
            .thenThrow(SystemException.TimeoutException("operation"))
            .thenReturn(Success("result"))
        
        retryService.executeWithRetry(clock = clock) {
            val start = clock.millis()
            externalService.call()
            delays.add(clock.millis() - start)
        }
        
        assertTrue(delays[0] >= 100)
        assertTrue(delays[1] >= 200)
    }
}
```

**Circuit Breaker Tests**:

```kotlin
class CircuitBreakerTest {
    @Test
    fun `opens circuit after failure threshold`() {
        val circuitBreaker = CircuitBreaker.of("test", CircuitBreakerConfig.custom()
            .failureRateThreshold(50f)
            .slidingWindowSize(4)
            .build()
        )
        
        repeat(3) {
            assertThrows<Exception> {
                circuitBreaker.executeSupplier {
                    throw RuntimeException("Failure")
                }
            }
        }
        
        val state = circuitBreaker.state
        assertEquals(CircuitBreaker.State.OPEN, state)
    }
    
    @Test
    fun `fails fast when circuit is open`() {
        val circuitBreaker = CircuitBreaker.of("test", CircuitBreakerConfig.custom()
            .failureRateThreshold(50f)
            .slidingWindowSize(2)
            .waitDurationInOpenState(Duration.ofSeconds(1))
            .build()
        )
        
        repeat(2) {
            assertThrows<Exception> {
                circuitBreaker.executeSupplier {
                    throw RuntimeException("Failure")
                }
            }
        }
        
        assertThrows<CallNotPermittedException> {
            circuitBreaker.executeSupplier {
                "Should not execute"
            }
        }
    }
    
    @Test
    fun `transitions to half-open after wait duration`() {
        val clock = TestClock()
        val circuitBreaker = CircuitBreaker.of("test", CircuitBreakerConfig.custom()
            .failureRateThreshold(50f)
            .slidingWindowSize(2)
            .waitDurationInOpenState(Duration.ofSeconds(1))
            .build()
        )
        
        repeat(2) {
            assertThrows<Exception> {
                circuitBreaker.executeSupplier {
                    throw RuntimeException("Failure")
                }
            }
        }
        
        clock.advance(Duration.ofSeconds(2))
        
        val state = circuitBreaker.state
        assertEquals(CircuitBreaker.State.HALF_OPEN, state)
    }
}
```

## Testing Dead Letter Queue

Publish a message that fails processing. Verify it's routed to DLQ after configured retries. Verify DLQ messages can be inspected and replayed.

**Kafka DLQ Tests**:

```kotlin
@SpringBootTest
@EmbeddedKafka(partitions = 1, topics = ["orders", "orders-dlq"])
class DeadLetterQueueTest {
    @Autowired
    lateinit var kafkaTemplate: KafkaTemplate<String, OrderEvent>
    
    @Autowired
    lateinit var dlqConsumer: KafkaConsumer<String, OrderEvent>
    
    @Test
    fun `routes message to DLQ after retries exhausted`() {
        val orderEvent = OrderEvent(orderId = "123", status = "CREATED")
        
        kafkaTemplate.send("orders", "123", orderEvent)
        
        val dlqRecords = dlqConsumer.poll(Duration.ofSeconds(10))
        assertTrue(dlqRecords.isNotEmpty())
        
        val dlqRecord = dlqRecords.first()
        assertEquals("123", dlqRecord.key())
        assertEquals(orderEvent, dlqRecord.value())
    }
    
    @Test
    fun `includes retry count in DLQ message headers`() {
        val orderEvent = OrderEvent(orderId = "123", status = "CREATED")
        
        kafkaTemplate.send("orders", "123", orderEvent)
        
        val dlqRecords = dlqConsumer.poll(Duration.ofSeconds(10))
        val dlqRecord = dlqRecords.first()
        
        val retryCountHeader = dlqRecord.headers().lastHeader("retry-count")
        assertNotNull(retryCountHeader)
        assertEquals("3", String(retryCountHeader.value()))
    }
    
    @Test
    fun `can replay DLQ message after fix`() {
        val orderEvent = OrderEvent(orderId = "123", status = "CREATED")
        
        kafkaTemplate.send("orders", "123", orderEvent)
        
        val dlqRecords = dlqConsumer.poll(Duration.ofSeconds(10))
        val dlqRecord = dlqRecords.first()
        
        fixProcessingIssue()
        
        kafkaTemplate.send("orders", dlqRecord.key(), dlqRecord.value())
        
        verifySuccessfulProcessing(dlqRecord.value())
    }
}
```

## Testing Graceful Degradation

Mock a dependency failure. Verify the service continues to function (with reduced capability). Verify fallback behavior.

**Graceful Degradation Tests**:

```kotlin
class RecommendationServiceTest {
    @Mock
    lateinit var recommendationClient: RecommendationClient
    
    @Mock
    lateinit var productRepository: ProductRepository
    
    lateinit var recommendationService: RecommendationService
    
    @BeforeEach
    fun setup() {
        recommendationService = RecommendationService(
            recommendationClient,
            productRepository
        )
    }
    
    @Test
    fun `falls back to default recommendations when service fails`() {
        whenever(recommendationClient.getRecommendations("product-123"))
            .thenThrow(SystemException.ServiceUnavailableException("recommendation-service"))
        
        whenever(productRepository.findSimilarProducts("product-123", 5))
            .thenReturn(listOf(
                Product(id = "p1"),
                Product(id = "p2")
            ))
        
        val recommendations = recommendationService.getRecommendations("product-123")
        
        assertEquals(2, recommendations.size)
        verify(productRepository).findSimilarProducts("product-123", 5)
    }
    
    @Test
    fun `returns empty list when both service and fallback fail`() {
        whenever(recommendationClient.getRecommendations("product-123"))
            .thenThrow(SystemException.ServiceUnavailableException("recommendation-service"))
        
        whenever(productRepository.findSimilarProducts("product-123", 5))
            .thenThrow(RuntimeException("Database error"))
        
        val recommendations = recommendationService.getRecommendations("product-123")
        
        assertTrue(recommendations.isEmpty())
    }
}
```

**Frontend Graceful Degradation Tests**:

```typescript
describe('ProductPage graceful degradation', () => {
  it('shows default recommendations when API fails', async () => {
    server.use(
      rest.get('/api/recommendations/:productId', (req, res, ctx) => {
        return res(ctx.status(503));
      })
    );

    render(<ProductPage productId="123" />);

    await waitFor(() => {
      expect(screen.getByText('Default Recommendations')).toBeInTheDocument();
    });
  });

  it('hides recommendations section when both API and fallback fail', async () => {
    server.use(
      rest.get('/api/recommendations/:productId', (req, res, ctx) => {
        return res(ctx.status(503));
      }),
      rest.get('/api/products/:productId/similar', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<ProductPage productId="123" />);

    await waitFor(() => {
      expect(screen.queryByText('Recommendations')).not.toBeInTheDocument();
    });
  });
});
```

## Testing Error Reporting

Verify frontend errors are captured and sent to error tracking service with correct context (user, breadcrumbs, stack trace).

**Sentry Error Reporting Tests**:

```typescript
describe('Error reporting', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('captures unhandled errors with context', () => {
    const error = new Error('Test error');
    
    window.dispatchEvent(new ErrorEvent('error', { error }));
    
    expect(Sentry.captureException).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        tags: { errorType: 'unhandled' },
        contexts: expect.objectContaining({
          browser: expect.objectContaining({
            url: window.location.href
          })
        })
      })
    );
  });

  it('captures unhandled promise rejections', () => {
    const error = new Error('Promise rejection');
    
    window.dispatchEvent(new PromiseRejectionEvent('unhandledrejection', {
      reason: error
    }));
    
    expect(Sentry.captureException).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        tags: { errorType: 'unhandledPromiseRejection' }
      })
    );
  });

  it('includes user context in error reports', () => {
    Sentry.setUser({ id: '123', email: 'user@example.com' });
    
    const error = new Error('Test error');
    window.dispatchEvent(new ErrorEvent('error', { error }));
    
    expect(Sentry.captureException).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        user: { id: '123', email: 'user@example.com' }
      })
    );
  });
});
```

## Testing Error Response Contracts

Consumer-driven contract tests verify error response format matches consumer expectations.

**Contract Tests**:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class ErrorResponseContractTest {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `error response matches RFC 7807 Problem Details format`() {
        mockMvc.perform(get("/api/orders/999"))
            .andExpect(status().isNotFound)
            .andExpect(jsonPath("$.type").exists())
            .andExpect(jsonPath("$.title").exists())
            .andExpect(jsonPath("$.status").value(404))
            .andExpect(jsonPath("$.detail").exists())
            .andExpect(jsonPath("$.instance").exists())
            .andExpect(jsonPath("$.traceId").exists())
    }
    
    @Test
    fun `validation error includes errors array`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"email": "invalid"}""")
        )
            .andExpect(status().isUnprocessableEntity)
            .andExpect(jsonPath("$.errors").isArray())
            .andExpect(jsonPath("$.errors[0].field").exists())
            .andExpect(jsonPath("$.errors[0].message").exists())
    }
}
```

## Negative Testing Patterns

For every happy path test, write corresponding error path tests. Test timeout, network error, invalid input, unauthorized, forbidden, not found, conflict, and server error scenarios.

**Comprehensive Negative Test Suite**:

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerNegativeTests {
    @Autowired
    lateinit var mockMvc: MockMvc
    
    @Test
    fun `handles timeout errors`() {
        // Mock service timeout
        // Verify 408 Request Timeout response
    }
    
    @Test
    fun `handles network errors`() {
        // Mock network failure
        // Verify appropriate error response
    }
    
    @Test
    fun `handles invalid JSON`() {
        mockMvc.perform(
            post("/api/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{invalid json}""")
        )
            .andExpect(status().isBadRequest)
    }
    
    @Test
    fun `handles unauthorized requests`() {
        mockMvc.perform(get("/api/orders"))
            .andExpect(status().isUnauthorized)
    }
    
    @Test
    fun `handles forbidden requests`() {
        // Authenticated but not authorized
        // Verify 403 Forbidden response
    }
    
    @Test
    fun `handles not found resources`() {
        mockMvc.perform(get("/api/orders/999"))
            .andExpect(status().isNotFound)
    }
    
    @Test
    fun `handles conflict errors`() {
        // Duplicate creation, optimistic locking failure
        // Verify 409 Conflict response
    }
    
    @Test
    fun `handles server errors`() {
        // Mock unexpected exception
        // Verify 500 Internal Server Error response
        // Verify no stack trace in production
    }
    
    @Test
    fun `handles concurrent modification errors`() {
        // Optimistic locking failure
        // Verify 409 Conflict with appropriate detail
    }
    
    @Test
    fun `handles rate limiting`() {
        // Exceed rate limit
        // Verify 429 Too Many Requests with Retry-After header
    }
}
```

**Frontend Negative Tests**:

```typescript
describe('API error handling', () => {
  it('handles 401 by redirecting to login', async () => {
    server.use(
      rest.get('/api/orders', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    render(<OrdersPage />);

    await waitFor(() => {
      expect(window.location.pathname).toBe('/login');
    });
  });

  it('handles 403 by showing permission denied', async () => {
    server.use(
      rest.post('/api/orders', (req, res, ctx) => {
        return res(ctx.status(403));
      })
    );

    render(<CreateOrderPage />);
    fireEvent.click(screen.getByText('Create Order'));

    await waitFor(() => {
      expect(screen.getByText('You don\'t have permission')).toBeInTheDocument();
    });
  });

  it('handles 429 with retry', async () => {
    server.use(
      rest.get('/api/orders', (req, res, ctx) => {
        return res(ctx.status(429), ctx.set('Retry-After', '60'));
      })
    );

    render(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText('Too many requests')).toBeInTheDocument();
      expect(screen.getByText('Retry in 60 seconds')).toBeInTheDocument();
    });
  });

  it('handles network errors', async () => {
    server.use(
      rest.get('/api/orders', (req, res) => {
        return res.networkError('Failed to connect');
      })
    );

    render(<OrdersPage />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });
});
```

Comprehensive error testing ensures that error handling works correctly in all scenarios, providing reliable error responses and graceful degradation when things go wrong.

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize testing error scenarios that have the highest business impact. Payment failures, authentication errors, and data loss scenarios should be tested first, as these directly affect user trust and revenue. Critical user journeys should have comprehensive error path coverage.

Test error scenarios that are most likely to occur in production. Network timeouts, service unavailability, and validation errors are common—test these thoroughly. Rare error scenarios (database corruption, disk full) can be tested less frequently but shouldn't be ignored.

Focus on user-facing error handling before internal error handling. Users experience error messages and error pages—ensure these are helpful and don't expose sensitive information. Internal error handling (logging, monitoring) is important but lower priority for user experience.

Defer testing for error scenarios that require complex setup (simulating database failures, network partitions) until after common error scenarios are validated. However, don't skip them entirely—they reveal important failure modes.

Prioritize testing error recovery and graceful degradation. Systems that fail gracefully provide better user experience than systems that crash. Test that errors don't cascade into system-wide failures.

### Exploratory Testing Guidance

Manually probe error boundaries by triggering various failure conditions. Disconnect network, stop services, send invalid data, exceed rate limits. Observe how the system responds—does it fail gracefully or crash? Are error messages helpful or confusing?

Investigate error message quality. Are error messages user-friendly? Do they provide actionable guidance? Do they expose sensitive information (stack traces, internal error codes)? Error messages are part of user experience—test them as such.

Probe error recovery mechanisms. After an error occurs, can users recover? Can they retry failed operations? Do they lose data? Test that errors don't leave systems in inconsistent states that prevent recovery.

Explore edge cases in error scenarios: very long error messages, special characters in error messages, concurrent errors, errors during error handling (meta-errors). These edge cases often reveal error handling bugs.

Session-based test management works well for error handling exploratory testing. Create sessions like "Explore payment failure scenarios" or "Investigate network error handling." Document findings: error messages, recovery mechanisms, system state after errors.

Use error handling heuristics: "Are errors caught and handled?", "Are error messages helpful?", "Can users recover from errors?", "Do errors expose sensitive information?", "Do errors cascade into system failures?". These heuristics guide exploratory testing.

Test error scenarios with realistic data. Error handling might behave differently with production-like data volumes or distributions. Test with realistic data to reveal error handling issues that don't appear with simple test data.

### Test Data Management

Create test data that exercises error scenarios: invalid input data, boundary values, data that triggers validation errors, data that causes business rule violations. Test data should trigger all error paths: validation errors, business errors, system errors.

For error testing, use test data that represents realistic error conditions: malformed JSON, SQL injection attempts, XSS attempts, oversized payloads, missing required fields. This exercises error handling and security measures.

Test data should include edge cases that might trigger errors: empty strings, null values, very long strings, special characters, Unicode characters, negative numbers where positive expected. These edge cases often reveal error handling bugs.

Mask sensitive data in error test data, but ensure error messages don't expose masked data inappropriately. Error messages should be helpful but not expose sensitive information. Test that error handling maintains data privacy.

Generate test data for error scenarios using tools that create invalid or problematic data. However, ensure test data is realistic—testing with completely random data might miss realistic error conditions. Balance realism with coverage.

Refresh error test data when error handling changes, but maintain stable test data for regression testing. Error handling regressions can appear when error handling logic is modified, so stable test data helps identify when error handling breaks.

### Test Environment Considerations

Test environments should support error scenario simulation: network failure simulation, service unavailability simulation, database failure simulation. Use tools like WireMock, Testcontainers, or chaos engineering tools to simulate failures.

Environment parity concerns include error handling configuration (timeout values, retry counts, circuit breaker settings). Test environments should mirror production error handling configuration to catch environment-specific issues.

Use isolated test environments for error testing to prevent interference. Tests that simulate failures can affect other tests running simultaneously. Isolate error tests or coordinate test schedules to prevent interference.

Environment-specific risks include different error handling behavior (test environments might have relaxed timeouts or retry counts), missing error monitoring (test environments might not have error tracking configured), and different error recovery mechanisms (test environments might have different fallback behavior).

Data isolation is important for error testing. Tests that trigger errors shouldn't leave systems in states that affect other tests. Use database transactions that roll back, or use separate test data sets. Error test data should be clearly identified to prevent confusion.

### Regression Strategy

Include error scenarios in regression suites for critical user journeys. Every happy path test should have corresponding error path tests. Automated error tests should run on every commit or pull request to catch error handling regressions.

Automate error regression testing using negative test patterns: invalid input, service failures, timeout scenarios. Automated tests catch regressions quickly, but manual testing validates error messages and user experience.

Trim regression suites by focusing on critical error scenarios and high-impact errors. However, don't trim too aggressively—error handling regressions can appear in unexpected places. Balance coverage with execution time.

Manual regression items include error message review, error recovery testing, and user experience validation. Automated tests catch functional issues, but manual testing validates that errors are handled gracefully from a user perspective.

Regression testing should verify that error handling is maintained as features evolve. New features should handle errors correctly, and modifications to existing features shouldn't break error handling. Track error rates and error handling metrics over time to detect regressions.

### Defect Patterns

Common error handling bug categories include unhandled exceptions (exceptions that crash the application), unhelpful error messages (messages that don't help users understand or recover from errors), error message exposure (stack traces or internal details exposed to users), error cascading (errors that trigger more errors), and missing error recovery (errors that leave systems in unrecoverable states).

Error handling bugs tend to hide in: edge cases (rare error conditions that aren't tested), concurrent scenarios (errors that occur simultaneously), error handling code itself (bugs in error handling logic), and integration points (errors from external services that aren't handled).

Historical patterns reveal that error handling regressions often come from: new features that don't include error handling, dependency upgrades that change error behavior, configuration changes that affect error handling (timeout values, retry counts), and code refactoring that breaks error handling logic.

Triage error handling defects by user impact and error frequency. Errors that affect critical user journeys or occur frequently are higher priority than errors that affect secondary features or occur rarely. However, all errors should be handled—unhandled errors can crash applications.

Error handling defects often require investigation to understand root causes. Error logs, stack traces, and monitoring data help identify error sources. However, not all errors are bugs—some indicate expected failure conditions that need better handling rather than prevention.
