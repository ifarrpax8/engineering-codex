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

Include trace ID, span ID, service name, and business context in every log line. Trace IDs enable correlating logs with traces. Business context (user ID, order ID, tenant ID) enables filtering logs by business entity. Without this context, logs are difficult to use for debugging.

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

SLO-based alerting focuses on user impact. "Error budget burning 10x faster than expected" indicates users are affected. "CPU usage above 80%" might not indicate a problem if latency and error rate are normal.

Alert on error rate, not error count. A service handling 1000 requests per second with 10 errors has a 1% error rate. A service handling 10 requests per second with 5 errors has a 50% error rate. Error rate provides context that error count cannot.

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

Spring Cloud Sleuth (deprecated) and Micrometer Tracing provide distributed tracing. Prefer Micrometer Tracing with OpenTelemetry exporter for vendor-neutral tracing. Verify that trace context propagates through @Async methods and message listeners.

Logback with LogstashEncoder produces JSON-formatted logs. Configure MDC to automatically include trace IDs and correlation IDs. Use logback-spring.xml for environment-specific configuration (different log levels per environment).

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
