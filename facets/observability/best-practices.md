# Best Practices: Observability

## Contents

- [Structured Logging Everywhere](#structured-logging-everywhere)
- [Correlation IDs End-to-End](#correlation-ids-end-to-end)
- [Instrument at Boundaries](#instrument-at-boundaries)
- [Define SLOs Before Building Dashboards](#define-slos-before-building-dashboards)
- [Alert on Symptoms, Not Causes](#alert-on-symptoms-not-causes)
- [Keep Metric Cardinality Under Control](#keep-metric-cardinality-under-control)
- [Log at the Right Level](#log-at-the-right-level)
- [Stack-Specific Practices](#stack-specific-practices)

Observability best practices ensure that telemetry data is useful, actionable, and cost-effective. These practices apply across languages and frameworks, with stack-specific considerations for Spring Boot, Kotlin, and frontend applications.

## Structured Logging Everywhere

Use JSON-formatted logs with consistent field names across all services. Structured logs enable querying and aggregation—finding all logs for a specific user ID, filtering by error type, correlating events across services. Free-form text logs cannot be queried effectively.

**Required Fields in Every Log Entry:**

Every log entry must include these standard fields for correlation and debugging:

- **`timestamp`**: ISO 8601 format with millisecond precision (e.g., `2026-02-09T14:23:45.123Z`). Use UTC to avoid timezone confusion.
- **`level`**: `ERROR`, `WARN`, `INFO`, `DEBUG`. Use consistent casing across all services.
- **`service`**: Service name (e.g., `payment-service`, `order-service`). Use kebab-case for consistency.
- **`traceId`**: Distributed trace ID (W3C Trace Context format: 32 hex characters). Enables correlating logs with traces.
- **`spanId`**: Current span ID (16 hex characters). Identifies the specific operation within a trace.
- **`message`**: Human-readable log message describing the event. Keep messages concise but descriptive.
- **`correlationId`**: Business-level identifier (order ID, user ID, request ID) that enables tracking a business operation across services. Different from traceId—traceId is technical, correlationId is business.
- **`userId`**: User identifier when applicable. Enables filtering logs by user. Use consistent format (UUID, email, numeric ID) across services.
- **`tenantId`**: Tenant identifier in multi-tenant systems. Enables filtering logs by tenant.
- **`environment`**: Deployment environment (`production`, `staging`, `development`). Helps distinguish logs from different environments.

**Optional but Recommended Fields:**

- **`requestId`**: HTTP request ID or message ID. Enables correlating logs for a specific request.
- **`httpMethod`**: HTTP method for HTTP requests (`GET`, `POST`, etc.).
- **`httpPath`**: HTTP path template (e.g., `/users/{id}`, not `/users/12345`) to avoid high cardinality.
- **`httpStatusCode`**: HTTP status code for HTTP requests.
- **`duration`**: Operation duration in milliseconds. Enables performance analysis.
- **`errorType`**: Error type or exception class name for error logs.
- **`errorMessage`**: Error message for error logs.
- **`stackTrace`**: Stack trace for error logs (truncated in production to avoid log volume).

Include trace ID, span ID, service name, and business context in every log line. Trace IDs enable correlating logs with traces. Business context (user ID, order ID, tenant ID) enables filtering logs by business entity. Without this context, logs are difficult to use for debugging.

**Field Naming Standards:**

- Use `camelCase` for field names (e.g., `traceId`, `userId`, `tenantId`).
- Use consistent field names across all services—don't mix `userId` and `user_id`.
- Avoid nested objects when possible—flatten structure for easier querying (e.g., `user.id` instead of `user: { id: ... }`).
- Use bounded values for fields used in queries—avoid high-cardinality values like full URLs or user emails as top-level fields.

Never log sensitive data. Passwords, tokens, credit card numbers, and PII must be excluded or masked. Configure log scrubbing rules to automatically remove sensitive patterns. Review log output during code review to catch accidental sensitive data logging.

Use appropriate log levels. ERROR for failures that need human attention, WARN for handled but unexpected situations, INFO for significant business events (order placed, user created), DEBUG for diagnostic detail (usually disabled in production). Log level should reflect severity, not verbosity.

**Example: Structured Logging with Correlation ID**

```kotlin
// Kotlin example
import mu.KotlinLogging
import org.slf4j.MDC

private val logger = KotlinLogging.logger {}

@Service
class OrderService {
    fun placeOrder(request: CreateOrderRequest): Order {
        // Set correlation ID in MDC for all logs in this request scope
        MDC.put("correlationId", request.correlationId)
        MDC.put("userId", request.userId)
        
        try {
            logger.info { 
                "Placing order" to mapOf(
                    "orderId" to request.orderId,
                    "customerId" to request.customerId,
                    "totalAmount" to request.totalAmount.toString()
                )
            }
            
            val order = processOrder(request)
            
            logger.info { 
                "Order placed successfully" to mapOf(
                    "orderId" to order.id,
                    "status" to order.status.name
                )
            }
            
            return order
        } catch (e: Exception) {
            logger.error(e) { 
                "Failed to place order" to mapOf(
                    "orderId" to request.orderId,
                    "error" to e.message
                )
            }
            throw e
        } finally {
            // Clean up MDC
            MDC.clear()
        }
    }
}
```

```java
// Java example
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@Service
public class OrderService {
    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);
    
    public Order placeOrder(CreateOrderRequest request) {
        // Set correlation ID in MDC for all logs in this request scope
        MDC.put("correlationId", request.getCorrelationId());
        MDC.put("userId", request.getUserId());
        
        try {
            logger.info("Placing order - orderId: {}, customerId: {}, totalAmount: {}", 
                       request.getOrderId(), 
                       request.getCustomerId(), 
                       request.getTotalAmount());
            
            Order order = processOrder(request);
            
            logger.info("Order placed successfully - orderId: {}, status: {}", 
                       order.getId(), 
                       order.getStatus());
            
            return order;
        } catch (Exception e) {
            logger.error("Failed to place order - orderId: {}, error: {}", 
                        request.getOrderId(), 
                        e.getMessage(), 
                        e);
            throw e;
        } finally {
            // Clean up MDC
            MDC.clear();
        }
    }
}
```

## Correlation IDs End-to-End

Generate a correlation ID at the API gateway or frontend for every user request. Propagate this correlation ID through every service, message, and log line. This enables tracing a user action from the UI through the entire system, even across async boundaries and message queues.

Correlation IDs should be included in HTTP headers, message metadata (Kafka headers, AMQP properties), and MDC context. MDC ensures that all log lines within a request scope automatically include the correlation ID without manual propagation.

Use correlation IDs for business operations, not just technical requests. An order placement might generate multiple HTTP requests, but they should share a correlation ID representing the order placement operation. This enables correlating all activity related to a single business transaction.

## Instrument at Boundaries

Trace every incoming HTTP request, outgoing HTTP call, database query, message publish, and message consume. These boundaries are where failures occur and where performance issues manifest. OpenTelemetry auto-instrumentation handles most of this automatically.

Add custom spans for significant business operations. A checkout flow might include spans for "validate_cart", "calculate_tax", "process_payment", "create_order". These business-level spans provide context that technical spans (HTTP requests, database queries) cannot.

Instrument message queue consumers explicitly. Trace context propagation through message queues requires including trace context in message metadata. Verify that consumer spans are linked to producer spans through trace context, enabling end-to-end tracing of async flows.

Database query instrumentation should include query parameters (with sensitive data masked) and query duration. Slow query detection relies on this instrumentation. Verify that database drivers are instrumented—most OpenTelemetry auto-instrumentation covers common drivers.

## Define SLOs Before Building Dashboards

Start with "what does the business care about?" and work backward to the metrics that measure it. Don't build dashboards for metrics nobody looks at. SLOs define what matters; dashboards visualize the metrics that feed SLOs.

Every dashboard should answer a specific question. "Is the payment service healthy?" is a good question. "Show me all metrics" is not. Dashboards that try to show everything end up showing nothing useful.

Include business metrics alongside technical metrics. A service dashboard showing request rate and error rate is useful, but including "orders processed per minute" provides business context. Business metrics indicate user satisfaction; technical metrics indicate system health.

## Alert on Symptoms, Not Causes

Alert when users are affected (high error rate, high latency), not when infrastructure is busy (high CPU). High CPU is not a problem if users aren't affected. Alerting on infrastructure metrics creates noise and misses user-impacting issues.

**SLO-Based Alerting**

SLO-based alerting focuses on user impact, not technical metrics. Instead of alerting on "error rate > 1%", alert on "error budget burning 10x faster than expected". This indicates users are affected and requires immediate attention.

**Error Budget Burn Rate Calculation:**

```
Error budget = 1 - SLO (e.g., 99.9% availability = 0.1% error budget)
Burn rate = error budget consumed / time window
Alert threshold = burn rate exceeds expected consumption rate
```

Example: If SLO is 99.9% availability (43 minutes downtime per month), and 20 minutes of downtime occur in 6 hours, the burn rate is 20/43 = 46% of monthly budget consumed in 6 hours. Expected consumption is 6/720 = 0.83% per 6 hours. Actual consumption (46%) is 55x faster than expected—this warrants an alert.

**Alert Thresholds:**

- **Critical alert:** Error budget burning 10x faster than expected. Users are significantly affected. Requires immediate response.
- **Warning alert:** Error budget burning 2x faster than expected. Degradation detected. Should be addressed during business hours.
- **Info alert:** Error budget consumption normal but approaching limits. Monitor but no action required.

**Alert Fatigue Prevention:**

Alert fatigue occurs when too many alerts desensitize the team. Prevent alert fatigue through:

1. **Alert consolidation:** Instead of separate alerts for error rate, latency, and throughput, create a single "service degradation" alert that considers all metrics.
2. **Alert grouping:** Group related alerts (e.g., all database-related alerts) to reduce notification volume.
3. **Alert deduplication:** Prevent duplicate alerts for the same issue within a time window.
4. **Alert suppression:** Suppress alerts during known maintenance windows or expected degradation periods.
5. **Regular alert review:** Quarterly review of all alerts. Remove alerts that haven't required action in 30 days. Tune thresholds for alerts that fire frequently but never require action.
6. **Alert runbooks:** Every alert must have a runbook describing what the alert means, how to investigate, and how to resolve. Alerts without runbooks are noise.

**Alert Severity Guidelines:**

- **Critical:** User-facing impact requiring immediate response. Wakes someone up at 2 AM. Examples: error budget burning 10x faster, payment processing failures, authentication service down.
- **Warning:** Degradation that should be addressed during business hours. Examples: error budget burning 2x faster, latency increase within acceptable bounds, capacity approaching limits.
- **Info:** Anomalies worth investigating when convenient. Examples: unusual traffic patterns, new error types appearing, performance regression in non-critical paths.

**Alert on error rate, not error count.** A service handling 1000 requests per second with 10 errors has a 1% error rate. A service handling 10 requests per second with 5 errors has a 50% error rate. Error rate provides context that error count cannot. Always include request volume in alert context to enable proper triage.

## Keep Metric Cardinality Under Control

Don't use high-cardinality values (user IDs, request IDs, full URLs) as metric labels. This creates millions of time series and overwhelms the metrics backend. Prometheus, for example, can handle thousands of time series per service, not millions.

Use bounded label values. HTTP status code (200, 404, 500) is bounded—there are only a few possible values. User ID is unbounded—there are millions of possible values. Use status code as a label, not user ID.

Endpoint names should be templated. "/users/12345" creates a new time series for each user ID. "/users/{id}" creates one time series for all user requests. Use endpoint templates in metric labels, not full paths.

Custom business metrics should use bounded dimensions. "Orders by status" (pending, completed, cancelled) is fine. "Orders by user ID" is not—use a counter for total orders and filter by user ID in logs or traces if needed.

## Log at the Right Level

ERROR for failures that need human attention. Exceptions, timeouts, business logic failures that prevent operation completion. These require investigation and potentially immediate response.

WARN for handled but unexpected situations. Retryable failures that were retried successfully, deprecated API usage, configuration issues that don't prevent operation. These are worth noting but don't require immediate action.

INFO for significant business events. Order placed, user created, payment processed. These events represent important state changes that might be needed for auditing or business intelligence.

DEBUG for detailed diagnostic info. Variable values, intermediate calculation results, detailed execution flow. DEBUG logs are usually disabled in production due to volume and potential sensitive data exposure.

Use dynamic log level adjustment for temporary debugging. Rather than changing configuration and redeploying, use an admin endpoint or feature flag to temporarily enable DEBUG logging for a specific service or operation. This enables targeted debugging without affecting all services.

## Stack-Specific Practices

### Spring Boot

Micrometer provides metrics abstraction with annotations (@Timed, @Counted) and programmatic API. Use @Timed on controller methods to automatically record request duration. Use @Counted for business events (orders processed, payments completed).

**Example: Custom Micrometer Metrics for Business Events**

```kotlin
// Kotlin example
import io.micrometer.core.instrument.Counter
import io.micrometer.core.instrument.MeterRegistry
import io.micrometer.core.instrument.Timer

@Service
class OrderMetricsService(
    private val meterRegistry: MeterRegistry
) {
    private val ordersPlacedCounter: Counter = Counter.builder("orders.placed")
        .description("Total number of orders placed")
        .tag("status", "success")
        .register(meterRegistry)
    
    private val ordersFailedCounter: Counter = Counter.builder("orders.placed")
        .description("Total number of failed order placements")
        .tag("status", "failed")
        .register(meterRegistry)
    
    private val orderProcessingTimer: Timer = Timer.builder("orders.processing.duration")
        .description("Time taken to process an order")
        .register(meterRegistry)
    
    fun recordOrderPlaced(orderAmount: BigDecimal) {
        ordersPlacedCounter.increment()
        meterRegistry.counter("orders.placed.amount", 
                             "currency", "USD")
            .increment(orderAmount.toDouble())
    }
    
    fun recordOrderFailed(reason: String) {
        ordersFailedCounter.increment(
            Counter.builder("orders.placed")
                .tag("status", "failed")
                .tag("reason", reason)
                .register(meterRegistry)
        )
    }
    
    fun <T> recordProcessingTime(operation: () -> T): T {
        return orderProcessingTimer.recordCallable(operation)
    }
}
```

```java
// Java example
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

@Service
public class OrderMetricsService {
    private final Counter ordersPlacedCounter;
    private final Counter ordersFailedCounter;
    private final Timer orderProcessingTimer;
    
    public OrderMetricsService(MeterRegistry meterRegistry) {
        this.ordersPlacedCounter = Counter.builder("orders.placed")
            .description("Total number of orders placed")
            .tag("status", "success")
            .register(meterRegistry);
        
        this.ordersFailedCounter = Counter.builder("orders.placed")
            .description("Total number of failed order placements")
            .tag("status", "failed")
            .register(meterRegistry);
        
        this.orderProcessingTimer = Timer.builder("orders.processing.duration")
            .description("Time taken to process an order")
            .register(meterRegistry);
    }
    
    public void recordOrderPlaced(BigDecimal orderAmount) {
        ordersPlacedCounter.increment();
        meterRegistry.counter("orders.placed.amount", "currency", "USD")
            .increment(orderAmount.doubleValue());
    }
    
    public void recordOrderFailed(String reason) {
        Counter.builder("orders.placed")
            .tag("status", "failed")
            .tag("reason", reason)
            .register(meterRegistry)
            .increment();
    }
    
    public <T> T recordProcessingTime(Callable<T> operation) throws Exception {
        return orderProcessingTimer.recordCallable(operation);
    }
}
```

Spring Boot Actuator provides health checks and metrics endpoints (/actuator/health, /actuator/metrics). Customize health checks to include dependency checks (database connectivity, message broker connectivity). Don't expose actuator endpoints publicly—use authentication or network restrictions.

**Spring Cloud Sleuth (deprecated) and Micrometer Tracing** provide distributed tracing. Prefer Micrometer Tracing with OpenTelemetry exporter for vendor-neutral tracing. Verify that trace context propagates through @Async methods and message listeners.

**Trace Context Propagation in Spring Boot:**

```kotlin
// Configure OpenTelemetry for Spring Boot
@Configuration
class ObservabilityConfig {
    @Bean
    fun openTelemetry(): OpenTelemetry {
        return OpenTelemetrySdk.builder()
            .setTracerProvider(
                SdkTracerProvider.builder()
                    .addSpanProcessor(BatchSpanProcessor.builder(
                        OtlpGrpcSpanExporter.builder()
                            .setEndpoint("http://collector:4317")
                            .build()
                    ).build())
                    .setResource(Resource.getDefault()
                        .merge(Resource.builder()
                            .put("service.name", "order-service")
                            .put("service.version", "1.0.0")
                            .build()))
                    .build()
            )
            .build()
    }
}

// Trace context propagation through @Async
@Service
class OrderService {
    @Async
    fun processOrderAsync(order: Order) {
        // Trace context is automatically propagated with @Async
        // if configured correctly
        processOrder(order)
    }
}

// Manual trace context propagation for custom async operations
@Service
class CustomAsyncService(
    private val tracer: Tracer
) {
    fun processAsync(data: Data) {
        val span = tracer.nextSpan().name("process-async").start()
        val context = tracer.currentTraceContext().context()
        
        executorService.submit {
            // Restore trace context in worker thread
            tracer.currentTraceContext().with(context).use {
                try {
                    process(data)
                } finally {
                    span.end()
                }
            }
        }
    }
}
```

**Spring Boot Actuator** provides health checks and metrics endpoints (/actuator/health, /actuator/metrics). Customize health checks to include dependency checks (database connectivity, message broker connectivity). Don't expose actuator endpoints publicly—use authentication or network restrictions.

**Custom Health Indicators:**

```kotlin
@Component
class DatabaseHealthIndicator(
    private val dataSource: DataSource
) : HealthIndicator {
    override fun health(): Health {
        return try {
            dataSource.connection.use { conn ->
                conn.isValid(1)
            }
            Health.up()
                .withDetail("database", "available")
                .build()
        } catch (e: Exception) {
            Health.down()
                .withDetail("database", "unavailable")
                .withException(e)
                .build()
        }
    }
}
```

**Logback with LogstashEncoder** produces JSON-formatted logs. Configure MDC to automatically include trace IDs and correlation IDs. Use logback-spring.xml for environment-specific configuration (different log levels per environment).

**Logback Configuration Example:**

```xml
<configuration>
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <customFields>{"service":"order-service","environment":"${ENV:production}"}</customFields>
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <includeMdcKeyName>correlationId</includeMdcKeyName>
            <includeMdcKeyName>userId</includeMdcKeyName>
        </encoder>
    </appender>
    
    <root level="INFO">
        <appender-ref ref="JSON" />
    </root>
</configuration>
```

**MDC Configuration for Automatic Context Propagation:**

```kotlin
@Component
class TraceContextFilter : Filter {
    override fun doFilter(request: ServletRequest, response: ServletResponse, chain: FilterChain) {
        val traceId = tracer.currentTraceContext().context()?.traceId()
        val spanId = tracer.currentTraceContext().context()?.spanId()
        val correlationId = request.getHeader("X-Correlation-ID") ?: UUID.randomUUID().toString()
        
        MDC.put("traceId", traceId)
        MDC.put("spanId", spanId)
        MDC.put("correlationId", correlationId)
        
        try {
            chain.doFilter(request, response)
        } finally {
            MDC.clear()
        }
    }
}
```

### Kotlin

Structured logging with kotlin-logging (wrapper around SLF4J) provides type-safe logging with lazy evaluation. Use logger.info { "Message with $variable" } to avoid string concatenation when log level is disabled.

Coroutine context propagation for trace IDs requires explicit handling. OpenTelemetry provides coroutine context propagation, but it must be configured. Verify that trace context propagates through coroutine launches and async operations.

Kotlin's data classes work well for structured log context. Create data classes for log context (UserContext, RequestContext) and include them in log statements. This ensures consistent structure and enables type-safe log querying.

### Frontend (Vue/React)

Error boundary components catch render errors and prevent entire application crashes. Log errors to error tracking service (Sentry, Datadog RUM) with user context and stack traces. Error boundaries should log errors but allow the application to continue functioning for other routes.

**Example: Frontend Error Tracking**

```vue
<!-- Vue 3 example -->
<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'
import * as Sentry from '@sentry/vue'

const hasError = ref(false)
const errorMessage = ref<string | null>(null)

onErrorCaptured((err, instance, info) => {
  // Log to error tracking service
  Sentry.captureException(err, {
    tags: {
      component: instance?.$options.name || 'Unknown',
      errorInfo: info
    },
    contexts: {
      vue: {
        componentName: instance?.$options.name,
        propsData: instance?.$props
      }
    },
    user: {
      id: getCurrentUserId(), // Your user context
      email: getCurrentUserEmail()
    }
  })
  
  hasError.value = true
  errorMessage.value = err.message
  
  // Return false to prevent error from propagating
  return false
})

function getCurrentUserId(): string | undefined {
  // Your user context retrieval logic
  return undefined
}

function getCurrentUserEmail(): string | undefined {
  // Your user context retrieval logic
  return undefined
}
</script>

<template>
  <div v-if="hasError" class="error-boundary">
    <h2>Something went wrong</h2>
    <p>{{ errorMessage }}</p>
    <button @click="hasError = false; errorMessage = null">
      Dismiss
    </button>
  </div>
  <slot v-else />
</template>
```

```tsx
// React example
import React, { Component, ErrorInfo, ReactNode } from 'react'
import * as Sentry from '@sentry/react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error tracking service
    Sentry.captureException(error, {
      tags: {
        componentStack: errorInfo.componentStack
      },
      contexts: {
        react: {
          componentStack: errorInfo.componentStack
        }
      },
      user: {
        id: this.getCurrentUserId(),
        email: this.getCurrentUserEmail()
      }
    })
  }

  private getCurrentUserId(): string | undefined {
    // Your user context retrieval logic
    return undefined
  }

  private getCurrentUserEmail(): string | undefined {
    // Your user context retrieval logic
    return undefined
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Dismiss
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

Performance Observer API provides access to Core Web Vitals and custom timing marks. Measure key user flows (checkout completion, search results) and send metrics to observability backend. Include user context (anonymous ID, session ID) to enable filtering by user segment.

Sentry SDK or similar error tracking service provides error capture with source maps. Configure source maps for production builds to enable readable stack traces. Include user context (user ID, email if available) and custom tags (feature flag values, A/B test variants) to enable filtering and correlation.

Frontend errors should include trace IDs from backend requests. When a frontend error occurs, include the trace ID from the most recent backend request in the error report. This enables correlating frontend errors with backend operations.

**Frontend Observability Patterns:**

**Core Web Vitals Monitoring:**

```typescript
// Monitor Core Web Vitals
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

function sendToAnalytics(metric: Metric) {
  // Send to observability backend
  fetch('/api/metrics', {
    method: 'POST',
    body: JSON.stringify({
      name: metric.name,
      value: metric.value,
      id: metric.id,
      delta: metric.delta,
      rating: metric.rating,
      navigationType: metric.navigationType
    })
  })
}

onCLS(sendToAnalytics)
onFID(sendToAnalytics)
onLCP(sendToAnalytics)
onFCP(sendToAnalytics)
onTTFB(sendToAnalytics)
```

**Custom Performance Marks:**

```typescript
// Measure specific user flows
function measureCheckoutFlow() {
  performance.mark('checkout-start')
  
  // ... checkout logic ...
  
  performance.mark('checkout-end')
  performance.measure('checkout-duration', 'checkout-start', 'checkout-end')
  
  const measure = performance.getEntriesByName('checkout-duration')[0]
  sendMetric('checkout.duration', measure.duration)
}
```

**User Session Replay:**

```typescript
// Configure session replay (example with Sentry)
import * as Sentry from '@sentry/vue'

Sentry.init({
  integrations: [
    new Sentry.Replay({
      maskAllText: true, // Mask sensitive text
      blockAllMedia: true, // Block media for privacy
      maskAllInputs: true // Mask all inputs
    })
  ],
  beforeSend(event) {
    // Filter sensitive data before sending
    if (event.request?.cookies) {
      delete event.request.cookies
    }
    return event
  }
})
```

**Frontend Error Tracking with Context:**

```typescript
// Enhanced error tracking
try {
  await apiCall()
} catch (error) {
  Sentry.captureException(error, {
    tags: {
      feature: 'checkout',
      step: 'payment-processing',
      traceId: getCurrentTraceId() // From backend request
    },
    contexts: {
      user: {
        id: getCurrentUserId(),
        email: getCurrentUserEmail()
      },
      browser: {
        name: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      }
    },
    extra: {
      url: window.location.href,
      referrer: document.referrer,
      userAgent: navigator.userAgent
    }
  })
}
```

**Frontend Performance Monitoring:**

```typescript
// Monitor resource loading performance
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.entryType === 'resource') {
      sendMetric('resource.load.time', {
        name: entry.name,
        duration: entry.duration,
        size: entry.transferSize,
        type: entry.initiatorType
      })
    }
  }
})

observer.observe({ entryTypes: ['resource', 'navigation'] })
```

**Vue-Specific Observability:**

```vue
<!-- Vue error boundary with observability -->
<script setup lang="ts">
import { onErrorCaptured } from 'vue'
import * as Sentry from '@sentry/vue'

onErrorCaptured((err, instance, info) => {
  Sentry.captureException(err, {
    tags: {
      component: instance?.$options.name || 'Unknown',
      errorInfo: info
    },
    contexts: {
      vue: {
        componentName: instance?.$options.name,
        propsData: instance?.$props
      }
    }
  })
  
  return false // Prevent error propagation
})
</script>
```

**React-Specific Observability:**

```tsx
// React error boundary with observability
import React, { Component, ErrorInfo, ReactNode } from 'react'
import * as Sentry from '@sentry/react'

class ErrorBoundary extends Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, {
      tags: {
        componentStack: errorInfo.componentStack
      },
      contexts: {
        react: {
          componentStack: errorInfo.componentStack
        }
      }
    })
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />
    }
    return this.props.children
  }
}
```
