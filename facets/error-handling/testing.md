# Error Handling -- Testing

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
