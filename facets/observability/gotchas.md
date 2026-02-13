# Gotchas: Observability

## Contents

- [Alert Fatigue](#alert-fatigue)
- [Logging Sensitive Data](#logging-sensitive-data)
- [Excessive Logging in Hot Paths](#excessive-logging-in-hot-paths)
- [Swallowing Exceptions](#swallowing-exceptions)
- [Inconsistent Log Formats Across Services](#inconsistent-log-formats-across-services)
- [String Concatenation in Log Statements](#string-concatenation-in-log-statements)
- [Metric Cardinality Explosion](#metric-cardinality-explosion)
- [Missing Trace Context in Async Flows](#missing-trace-context-in-async-flows)
- [Log Volume Cost](#log-volume-cost)
- [Dashboard Rot](#dashboard-rot)
- [Observing the Wrong Thing](#observing-the-wrong-thing)
- [Not Correlating Deployments with Metrics](#not-correlating-deployments-with-metrics)
- [Sampling Bias](#sampling-bias)
- [Health Check That Always Passes](#health-check-that-always-passes)

Common pitfalls in observability implementation lead to alert fatigue, excessive costs, missing data, and ineffective debugging. Recognizing these gotchas enables avoiding them and building effective observability from the start.

## Alert Fatigue

Too many alerts, too many false positives, and the team starts ignoring alerts. Then a real incident goes unnoticed because alerts have become noise. Every alert must be actionable. If an alert fires and the response is "ignore it," the alert should be removed or tuned.

**Real-world scenario:** A team sets up 50 alerts across their microservices—CPU usage, memory usage, disk usage, error count, latency, request rate for each service. During peak traffic, 30 alerts fire simultaneously. The on-call engineer can't determine which alerts are critical. They start ignoring alerts, assuming they're false positives. One night, a real payment processing failure occurs, but the alert is lost in the noise. The incident goes undetected for 2 hours, affecting 500 transactions.

Alert fatigue often starts with alerting on every metric. CPU usage, memory usage, disk usage, request rate, error count—each gets its own alert. Most of these alerts fire during normal operations, creating constant noise. The solution is to alert on symptoms (user impact) not causes (infrastructure metrics).

**When alert fatigue bites:** A team has 100+ alerts configured. During a deployment, 20 alerts fire. The team ignores them, assuming they're deployment-related noise. The deployment introduces a bug that causes 5% error rate increase. The error rate alert fires, but it's ignored along with the other 19 alerts. The bug goes undetected for 6 hours, affecting thousands of users.

Review and prune alerts regularly. If an alert hasn't required action in 30 days, consider removing it. If an alert fires frequently but never requires action, tune the threshold or remove it. A few high-quality alerts are more valuable than many low-quality ones.

Consolidate related alerts. Instead of separate alerts for "error rate high" and "latency high," create a single alert for "service degradation" that considers both metrics. This reduces noise while maintaining coverage.

**Prevention strategies:**
- Start with 5-10 critical alerts, add more only when needed
- Every alert must have a runbook describing investigation and resolution steps
- Quarterly alert review: remove unused alerts, tune thresholds, consolidate duplicates
- Use alert grouping to reduce notification volume
- Implement alert deduplication to prevent duplicate notifications

**SLO-Based Alerting to Prevent Fatigue:**

Replace metric-based alerts with SLO-based alerts. Instead of "error rate > 1%" (fires constantly), use "error budget burning 10x faster than expected" (fires only when users are affected).

**Alert consolidation example:**
- **Before:** 15 separate alerts (CPU high, memory high, disk high, error rate high, latency high, request rate low, etc.)
- **After:** 3 SLO-based alerts (availability SLO burn rate, latency SLO burn rate, error rate SLO burn rate)
- **Result:** 80% reduction in alert volume, all alerts are actionable

**Alert runbook requirement:** Every alert must have a runbook. If you can't write a runbook describing how to investigate and resolve the alert, the alert isn't actionable and should be removed. Runbooks should include:
- What the alert means (in business terms, not just technical)
- How to investigate (which dashboards to check, which logs to search)
- How to resolve (step-by-step resolution procedures)
- When to escalate (if resolution isn't possible within time limits)

**Alert review process:** Quarterly alert review meeting:
1. List all alerts that fired in the past quarter
2. For each alert, ask: "Did this alert require action?" If no action was taken, remove or tune the alert
3. For alerts that fired frequently but never required action, significantly tune thresholds or remove
4. For alerts that required action, verify runbooks are up-to-date
5. Document new alerts added and rationale

**Real-world example:** A team has 50 alerts. During quarterly review, they discover:
- 20 alerts never fired (removed)
- 15 alerts fired but never required action (removed or tuned)
- 10 alerts fired and required action (kept, updated runbooks)
- 5 alerts are new and need runbooks (assigned owners)

Result: 50 alerts → 15 actionable alerts. Alert fatigue eliminated, team responds faster to real incidents.

## Logging Sensitive Data

Accidentally logging PII, passwords, or tokens in request/response bodies creates security and compliance risks. GDPR requires knowing what's in your logs and having processes to handle data subject requests. Logging sensitive data violates these requirements. Use masking or redaction for objects that may contain sensitive fields—never log raw request/response payloads.

Configure log scrubbing rules to automatically remove sensitive patterns. Common patterns include credit card numbers (Luhn algorithm validation), SSNs (XXX-XX-XXXX format), and email addresses (if PII concerns exist). However, scrubbing is not foolproof—prevention is better.

Review log output during code review. Look for log statements that include request bodies, query parameters, or user input. These often contain sensitive data. Use structured logging with explicit fields rather than logging entire objects.

Test log scrubbing in staging environments. Inject test data containing sensitive patterns and verify that logs are scrubbed. However, remember that scrubbing cannot catch all cases—the best approach is to not log sensitive data in the first place.

## Excessive Logging in Hot Paths

Logging inside tight loops or high-throughput code paths can severely impact performance. Each log call—even when the level is disabled—can incur overhead from parameter evaluation, formatting, and framework processing. Use appropriate log levels and guard expensive log statements with level checks or lazy evaluation (e.g., `logger.debug { "Expensive: ${expensiveCall()}" }`).

## Swallowing Exceptions

Catching exceptions and only logging `e.message` without the stack trace, then not re-throwing, makes production debugging nearly impossible. The stack trace shows where the failure occurred and the call path that led to it; without it, engineers are left guessing. Always log the full exception and either re-throw or handle meaningfully—never log and continue as if nothing happened.

## Inconsistent Log Formats Across Services

When different services use different log formats (plain text vs. JSON, different field names, different nesting), centralized log aggregation and searching becomes unreliable. Queries that work for one service fail for another. Standardize on a single structured format with consistent field names across all services.

## String Concatenation in Log Statements

Using string concatenation (`"User " + userId + " failed"`) instead of structured logging parameters evaluates the concatenation even when the log level is disabled. If the concatenation involves method calls or expensive operations, you pay the cost without any benefit. Use parameterized logging or lazy evaluation so string building only happens when the log entry is actually written.

## Metric Cardinality Explosion

Using user ID or request path as a metric label creates millions of time series. With millions of users, you create millions of time series. Prometheus runs out of memory, query performance degrades, and costs escalate.

**Real-world scenario:** A team adds user ID as a label to track API request metrics: `http_requests_total{user_id="12345", endpoint="/api/orders"}`. With 1 million users, this creates 1 million time series per endpoint. With 10 endpoints, that's 10 million time series. Prometheus runs out of memory, queries timeout, and the metrics backend becomes unusable. The team spends 2 days identifying and fixing the cardinality explosion, losing observability during that time.

High-cardinality labels are unbounded. User ID, request ID, full URLs, email addresses—these can have millions of unique values. Each unique combination of label values creates a new time series.

**When cardinality explosion causes outages:** A service adds request ID as a metric label to track individual request performance. During peak traffic (1000 requests/second), this creates 1000 new time series per second. After 1 hour, Prometheus has 3.6 million time series. Prometheus crashes, all dashboards break, and alerts stop firing. The team loses observability during a critical period.

Use bounded label values. HTTP method (GET, POST, PUT, DELETE) is bounded—only a few possible values. HTTP status code (200, 404, 500) is bounded. Endpoint template ("/users/{id}") is bounded. User ID is not bounded.

**Correct approach:** Use endpoint templates, not full paths:
```kotlin
// Wrong - high cardinality
meterRegistry.counter("http.requests", "path", "/users/12345").increment()

// Correct - bounded cardinality
meterRegistry.counter("http.requests", "path", "/users/{id}", "method", "GET").increment()
```

If you need to track metrics per user, use a different approach. Log user IDs in structured logs and aggregate in log analysis. Or use a separate metrics system designed for high cardinality (though this adds complexity). Don't use Prometheus-style metrics for high-cardinality data.

Test metric cardinality under load. Run load tests and verify that the number of time series remains manageable. If cardinality explodes, identify the high-cardinality labels and replace them with bounded values. Monitor Prometheus cardinality metrics (`prometheus_tsdb_head_series`) to detect cardinality growth early.

## Missing Trace Context in Async Flows

Trace context propagates automatically for synchronous HTTP calls but can be lost in message queues, thread pool hand-offs, and async operations. Without trace context, async operations appear as orphaned spans with no connection to the originating request.

**Real-world scenario:** A team implements an order processing flow: HTTP request → message queue → background worker → database update. Trace context propagates through HTTP but is lost at the message queue. When an error occurs in the background worker, the trace shows only the worker span with no connection to the original HTTP request. Debugging takes hours because engineers can't trace the complete flow. They must manually correlate logs across services using timestamps and correlation IDs.

Message queue consumers must extract trace context from message metadata (Kafka headers, AMQP properties) and create child spans. If trace context is not included in message metadata, consumer spans cannot be linked to producer spans.

**When missing trace context causes debugging delays:** A payment processing service publishes payment events to Kafka. The consumer processes payments asynchronously. When a payment fails, the trace shows only the consumer span. Engineers can't see the original HTTP request that triggered the payment. They spend 4 hours manually correlating logs to understand the complete flow. With proper trace context propagation, debugging would take 10 minutes.

Thread pool hand-offs require explicit trace context propagation. When submitting work to an ExecutorService, capture the current trace context and restore it in the worker thread. OpenTelemetry provides context propagation utilities for this.

**Example of correct trace context propagation:**

```kotlin
// Wrong - trace context lost
executorService.submit {
    processOrder(order) // New trace, not linked to original
}

// Correct - trace context preserved
val context = tracer.currentTraceContext().context()
executorService.submit {
    tracer.currentTraceContext().with(context).use {
        processOrder(order) // Same trace, linked to original
    }
}
```

Coroutines in Kotlin require explicit trace context propagation. Launch coroutines with the current trace context, or configure OpenTelemetry coroutine context propagation. Without this, coroutine operations appear as separate traces.

**Coroutine trace context propagation:**

```kotlin
// Wrong - trace context lost
launch {
    processOrder(order) // New trace
}

// Correct - trace context preserved
val context = tracer.currentTraceContext().context()
launch(context.asContextElement()) {
    processOrder(order) // Same trace
}
```

Test trace context propagation through async boundaries. Make a request that triggers async operations (message publishing, scheduled tasks, coroutines) and verify that all operations appear in the same trace. This validation catches missing context propagation.

## Log Volume Cost

Logging everything at DEBUG level in production generates terabytes of data. Storage costs escalate quickly. A service handling 1000 requests per second with DEBUG logging might generate 100 MB per second of logs—8.6 TB per day. At cloud storage prices, this costs thousands of dollars per month.

Set production log level to INFO or WARN. DEBUG logs are for development and staging, not production. The volume and potential sensitive data in DEBUG logs make them unsuitable for production.

Use dynamic log level adjustment for temporary debugging. Rather than changing configuration to DEBUG for all services, enable DEBUG logging for a specific service or operation temporarily. This enables targeted debugging without affecting log volume across all services.

Implement log retention policies. Recent logs are most valuable for debugging. Older logs are primarily useful for compliance and trend analysis. Retain detailed logs for 7-30 days, then archive or delete. Retain aggregated metrics indefinitely.

Review log volume regularly. If log volume increases significantly, investigate the cause. New services, increased traffic, or log level changes can cause unexpected cost increases.

## Dashboard Rot

Dashboards created for a specific incident are never updated. Over time, queries break (services renamed, metrics deprecated), panels show stale data, and nobody trusts the dashboards. Broken dashboards are worse than no dashboards—they provide false confidence.

Assign dashboard ownership. Every dashboard should have an owner responsible for maintaining it. Owners review dashboards quarterly, fix broken queries, update visualizations, and remove unused panels.

Review dashboards regularly. If a dashboard hasn't been viewed in 30 days, consider archiving it. If a dashboard's queries are broken, fix them or delete the dashboard. Broken dashboards create confusion and waste time.

Test dashboard queries. When services are renamed or metrics are deprecated, update dashboard queries. Don't leave broken queries—they provide misleading information. Consider automated testing of dashboard queries to catch breakage early.

Consolidate similar dashboards. Multiple dashboards showing the same data create maintenance burden. Consolidate into a single high-quality dashboard with multiple panels. This reduces maintenance while improving consistency.

## Observing the Wrong Thing

Building extensive infrastructure monitoring (CPU, memory, disk) but not monitoring business outcomes (orders per minute, payment success rate, user signups) is a common mistake. Infrastructure metrics are important, but business metrics tell you if users are happy.

Infrastructure metrics indicate system health, but they don't indicate user satisfaction. A service might have perfect infrastructure metrics (low CPU, plenty of memory) but fail business operations (payment processing errors, order creation failures). Business metrics reveal these issues; infrastructure metrics do not.

Start with business outcomes. What does the business care about? Orders, revenue, user satisfaction. Work backward from these outcomes to the metrics that measure them. Then add infrastructure metrics to understand system health.

Include business metrics on service dashboards. A payment service dashboard should show payment success rate, not just request rate and error rate. Payment success rate directly indicates user satisfaction; request rate does not.

## Not Correlating Deployments with Metrics

An error spike starts at 2:15 PM. Was there a deployment? Without deployment markers on dashboards, this correlation requires manual investigation. Deployment markers enable immediate correlation between deployments and metric changes.

Automatically annotate metric dashboards with deployment events from CI/CD pipelines. When a deployment completes, add a marker to relevant dashboards showing deployment time and version. This enables immediate correlation during incidents.

Include deployment information in traces and logs. Add deployment version as a resource attribute in OpenTelemetry. Include deployment version in log context. This enables filtering traces and logs by deployment version, making it easy to identify issues introduced by specific deployments.

Test deployment correlation. Deploy a test change and verify that deployment markers appear on dashboards. Verify that traces and logs include deployment version. This validation ensures that deployment correlation works correctly.

## Sampling Bias

Aggressive trace sampling (1% of requests) means you miss rare but important errors. If an error occurs in 0.1% of requests, sampling 1% of requests means you'll only capture 10% of errors. Rare errors are often the most important—they might indicate security issues or edge cases that affect specific user segments.

Use tail-based sampling to keep all error traces and a sample of successful ones. Tail-based sampling decides after seeing all spans, enabling keeping interesting traces (errors, slow requests) while sampling successful ones. This provides better coverage of important events.

Adjust sampling rates based on traffic volume. High-traffic services can use lower sampling rates (1-5%) because they generate enough traces even at low rates. Low-traffic services might need higher sampling rates (50-100%) to ensure adequate coverage.

Monitor sampling coverage. Track the percentage of errors that are sampled. If error sampling rate is too low, increase sampling rate for error traces. Some observability platforms allow different sampling rates for different conditions (100% for errors, 1% for successes).

## Health Check That Always Passes

A /health endpoint that returns 200 without checking actual dependencies (database, message broker, downstream services) is useless. The service reports healthy while its dependencies are down, leading to false confidence and delayed incident detection.

Health checks must include dependency checks. Verify database connectivity, message broker connectivity, and critical downstream service availability. If any critical dependency is unavailable, return a non-200 status code.

Distinguish between liveness and readiness. Liveness indicates that the service process is running (should always return 200 unless the process is dead). Readiness indicates that the service can handle requests (should check dependencies). Kubernetes uses these distinctions for pod management.

Test health check behavior. Stop the database and verify that the health check returns a failure status. Stop a downstream service and verify that readiness check fails. This validation ensures that health checks actually check dependencies.

Don't expose health checks publicly without authentication. Health checks might reveal internal service information (dependency names, versions). Use network restrictions or authentication to limit access to health check endpoints.
