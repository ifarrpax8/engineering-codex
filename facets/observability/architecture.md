# Architecture: Observability

## Contents

- [The Three Pillars of Observability](#the-three-pillars-of-observability)
- [Frontend Observability](#frontend-observability)
- [OpenTelemetry Architecture](#opentelemetry-architecture)
- [Alerting](#alerting)
- [Dashboards](#dashboards)

Observability architecture centers on three pillars: logs, metrics, and traces. Each pillar provides different insights, and together they enable comprehensive understanding of system behavior. Modern observability stacks integrate these pillars through standardized instrumentation and unified backends.

## The Three Pillars of Observability

```mermaid
graph TB
    subgraph Services["Application Services"]
        Service1["Service 1"]
        Service2["Service 2"]
        Service3["Service 3"]
    end
    
    subgraph Pillars["Three Pillars"]
        Logs["Logs - Event Records"]
        Metrics["Metrics - Time Series"]
        Traces["Traces - Request Flow"]
    end
    
    subgraph Collection["Collection Layer"]
        Collector["OpenTelemetry Collector"]
    end
    
    subgraph Storage["Storage Layer"]
        LogStore["Log Storage - Loki/ELK"]
        MetricStore["Metric Storage - Prometheus"]
        TraceStore["Trace Storage - Tempo/Jaeger"]
    end
    
    subgraph Visualization["Visualization Layer"]
        Dashboards["Dashboards - Grafana"]
        Alerts["Alerting - PagerDuty"]
    end
    
    Service1 --> Logs
    Service2 --> Logs
    Service3 --> Logs
    Service1 --> Metrics
    Service2 --> Metrics
    Service3 --> Metrics
    Service1 --> Traces
    Service2 --> Traces
    Service3 --> Traces
    
    Logs --> Collector
    Metrics --> Collector
    Traces --> Collector
    
    Collector --> LogStore
    Collector --> MetricStore
    Collector --> TraceStore
    
    LogStore --> Dashboards
    MetricStore --> Dashboards
    TraceStore --> Dashboards
    MetricStore --> Alerts
```

## The Three Pillars of Observability

### Logs

Logs are structured records of discrete events. They capture what happened, when it happened, and in what context. Structured logging—using JSON format with consistent field names—enables querying and aggregation across services.

Every log entry should include:
- **Timestamp**: Precise time of the event, preferably in UTC with millisecond precision
- **Level**: ERROR (something failed, needs attention), WARN (something unexpected but handled), INFO (significant business events), DEBUG (detailed diagnostic info, not in production by default)
- **Message**: Human-readable description of the event
- **Service Name**: Identifies which service generated the log
- **Trace ID**: Links the log to a distributed trace
- **Span ID**: Identifies the specific operation within the trace
- **Correlation ID**: Business-level identifier (order ID, user ID, request ID) that enables tracking a business operation across services
- **Business Context**: Relevant domain data (user ID, tenant ID, order ID) that enables filtering logs by business entity

Structured logging with Logback and JSON encoding is standard in Spring Boot applications. The LogstashEncoder produces JSON-formatted logs with consistent structure. MDC (Mapped Diagnostic Context) allows adding trace IDs, correlation IDs, and other context to all log lines within a request scope, ensuring every log entry includes the necessary context for correlation.

Log aggregation centralizes logs from all services into a single searchable store. The ELK stack (Elasticsearch, Logstash, Kibana), Loki, or cloud-native solutions (CloudWatch Logs, Azure Monitor Logs) provide this capability. Centralized logging enables searching across services, correlating events, and identifying patterns that span multiple systems.

### Metrics

Metrics are numeric measurements over time. They aggregate events into time-series data, enabling trend analysis and alerting. Metrics fall into three categories:

- **Counters**: Monotonically increasing values (request count, error count, bytes transferred). Counters measure cumulative events and are typically used to calculate rates (requests per second).

- **Gauges**: Point-in-time values (queue depth, active connections, memory usage). Gauges represent the current state and can increase or decrease.

- **Histograms**: Distributions of values (request latency, response size). Histograms enable percentile calculations (p50, p95, p99) which are more meaningful than averages for understanding user experience.

Micrometer is Spring Boot's metrics abstraction layer. It provides annotations (@Timed, @Counted) and a programmatic API for recording metrics. Micrometer exports to multiple backends (Prometheus, Datadog, CloudWatch, InfluxDB) without changing application code, providing vendor portability.

RED metrics (Rate, Errors, Duration) should be applied to every service:
- **Rate**: Requests per second, measuring throughput
- **Errors**: Error rate as a percentage of total requests
- **Duration**: Latency distribution (p50, p95, p99)

USE metrics (Utilization, Saturation, Errors) apply to infrastructure resources:
- **Utilization**: Percentage of resource capacity used (CPU, memory, disk, network)
- **Saturation**: Degree of queuing or contention
- **Errors**: Error rate for the resource

Custom business metrics matter more than infrastructure metrics for business outcomes. Orders processed per minute, payment failures, user registrations, conversion rates—these metrics directly reflect business health. Infrastructure metrics indicate system health, but business metrics indicate user satisfaction.

### Traces

Traces capture end-to-end request flow across services. A trace contains multiple spans, each representing a unit of work (HTTP request, database query, message publish). Spans have parent-child relationships forming a tree structure that shows the complete request path.

Each span includes:
- **Trace ID**: Unique identifier for the entire request flow
- **Span ID**: Unique identifier for this specific operation
- **Parent Span ID**: Links to the parent operation
- **Operation Name**: What operation was performed (e.g., "GET /users/{id}")
- **Start Time and Duration**: When the operation started and how long it took
- **Tags**: Key-value pairs providing context (HTTP method, status code, database name)
- **Logs**: Events within the span (exceptions, important state changes)

OpenTelemetry is the vendor-neutral standard for distributed tracing (and metrics and logs). It provides auto-instrumentation for Spring Boot, HTTP clients, database drivers, and Kafka clients, capturing traces without manual code changes. Manual instrumentation enables adding custom spans for business logic operations.

Trace context propagation follows the W3C Trace Context standard. Trace ID and span ID are propagated via HTTP headers (traceparent) and message metadata (Kafka headers, AMQP properties). This enables correlating operations across service boundaries, message queues, and async boundaries.

```mermaid
sequenceDiagram
    participant User as User Browser
    participant Frontend as Frontend Service
    participant API as API Gateway
    participant Auth as Auth Service
    participant Order as Order Service
    participant Payment as Payment Service
    
    User->>Frontend: HTTP Request
    Frontend->>Frontend: Create Trace - TraceID: abc123 - SpanID: span1
    Frontend->>API: HTTP Request - traceparent: abc123/span1
    API->>API: Create Span - TraceID: abc123 - SpanID: span2 - Parent: span1
    API->>Auth: HTTP Request - traceparent: abc123/span2
    Auth->>Auth: Create Span - TraceID: abc123 - SpanID: span3 - Parent: span2
    Auth-->>API: Response - traceparent: abc123/span2
    API->>Order: HTTP Request - traceparent: abc123/span2
    Order->>Order: Create Span - TraceID: abc123 - SpanID: span4 - Parent: span2
    Order->>Payment: HTTP Request - traceparent: abc123/span4
    Payment->>Payment: Create Span - TraceID: abc123 - SpanID: span5 - Parent: span4
    Payment-->>Order: Response - traceparent: abc123/span4
    Order-->>API: Response - traceparent: abc123/span2
    API-->>Frontend: Response - traceparent: abc123/span1
    Frontend-->>User: HTTP Response
```

Sampling is essential in high-throughput systems. Tracing every request generates massive volumes of data. Head-based sampling decides at request start whether to trace the request. Tail-based sampling decides after seeing all spans, keeping interesting traces (errors, slow requests) while sampling successful ones. Tail-based sampling is more sophisticated but requires buffering spans, which adds latency.

## Frontend Observability

Frontend observability captures user experience from the browser. JavaScript error tracking captures exceptions with stack traces, browser information, and user context. Error tracking services (Sentry, Datadog RUM) provide source map support, enabling readable stack traces from minified production code.

Performance monitoring tracks Core Web Vitals:
- **LCP (Largest Contentful Paint)**: Time until the main content is visible
- **FID/INP (First Input Delay / Interaction to Next Paint)**: Responsiveness to user interactions
- **CLS (Cumulative Layout Shift)**: Visual stability during page load

Custom timing marks enable measuring specific user flows (checkout completion time, search result rendering). The Performance Observer API provides programmatic access to performance metrics.

User session replay records user sessions for debugging. It captures mouse movements, clicks, scrolls, and page changes, enabling engineers to see exactly what users experienced. Privacy considerations require masking sensitive inputs (passwords, credit card numbers) and obtaining user consent where required by regulations.

Frontend observability must correlate with backend traces. Including trace IDs in frontend error reports enables linking frontend errors to backend operations. This correlation is essential for debugging issues that span the frontend-backend boundary.

## OpenTelemetry Architecture

OpenTelemetry provides a unified approach to observability through three components:

**SDK**: Instruments application code through auto-instrumentation and manual instrumentation. Auto-instrumentation hooks into frameworks (Spring Boot, HTTP clients, database drivers) automatically. Manual instrumentation adds custom spans for business logic.

**Collector**: Receives, processes, and exports telemetry data. The collector runs as a sidecar container, standalone service, or agent. It provides filtering, batching, and routing capabilities, enabling sending different data to different backends (traces to Tempo, metrics to Prometheus, logs to Loki).

**Backends**: Storage and visualization systems. Jaeger or Tempo for traces, Prometheus for metrics, Loki for logs. All-in-one platforms (Datadog, Grafana Cloud, New Relic) provide unified storage and visualization.

The collector architecture provides flexibility. Applications send telemetry to the collector, which routes it to appropriate backends. This enables switching backends without changing application code, supporting multi-vendor strategies (e.g., traces to Tempo, metrics to Datadog).

## Alerting

Alerting transforms telemetry data into actionable notifications. Effective alerting requires careful design to avoid alert fatigue while ensuring critical issues are caught.

```mermaid
flowchart TD
    Start([Metrics Collected]) --> Threshold{Threshold Exceeded?}
    Threshold -->|No| Continue([Continue Monitoring])
    Threshold -->|Yes| Evaluate[Evaluate Alert Rule]
    Evaluate --> RuleCheck{Alert Rule Matches?}
    RuleCheck -->|No| Continue
    RuleCheck -->|Yes| Severity{Determine Severity}
    Severity --> Critical[Critical Alert]
    Severity --> Warning[Warning Alert]
    Severity --> Info[Info Alert]
    Critical --> Route[Route to Notification Channel]
    Warning --> Route
    Info --> Route
    Route --> PagerDuty[PagerDuty On-Call]
    Route --> Slack[Slack Channel]
    Route --> Email[Email Notification]
    PagerDuty --> Escalate{Response Received?}
    Escalate -->|No| Escalation[Escalate to Next On-Call]
    Escalate -->|Yes| Resolve[Alert Resolved]
    Escalation --> Resolve
    Slack --> Resolve
    Email --> Resolve
```

Alert on SLO burn rate, not raw metrics. "Error rate > 1%" fires constantly and becomes noise. "Error budget burning 10x faster than expected" is actionable—it indicates a problem that requires immediate attention. SLO-based alerting focuses on user impact, not technical metrics.

Severity levels organize alert response:
- **Critical**: User-facing impact requiring immediate response. Wakes someone up at 2 AM. Examples: service down, error rate exceeding error budget burn rate, payment processing failures.

- **Warning**: Degradation that should be addressed during business hours. Examples: latency increase, error rate increase within acceptable bounds, capacity approaching limits.

- **Info**: Anomalies worth investigating when convenient. Examples: unusual traffic patterns, new error types appearing, performance regression in non-critical paths.

Alert fatigue occurs when too many alerts desensitize the team. If an alert fires and the response is "ignore it," the alert should be removed or tuned. Every alert must be actionable. Regular alert review—removing unused alerts, tuning thresholds, consolidating related alerts—prevents fatigue.

PagerDuty or Opsgenie integration provides on-call routing, escalation policies, and incident management. These tools ensure alerts reach the right person at the right time, with escalation if the primary on-call engineer doesn't respond.

## Dashboards

Dashboards visualize telemetry data for monitoring and analysis. Different dashboard types serve different purposes:

**Service Dashboards**: RED metrics per service—request rate, error rate, latency percentiles, throughput. These dashboards show service health at a glance. Include deployment markers to correlate deployments with metric changes.

**Business Dashboards**: Orders per minute, revenue, conversion rates, user signups. These dashboards show business health, enabling product and business stakeholders to monitor outcomes. Business dashboards are more valuable than technical dashboards for understanding user satisfaction.

**Infrastructure Dashboards**: CPU, memory, disk, network utilization, container health. These dashboards show infrastructure health, enabling capacity planning and identifying resource constraints.

**Incident Dashboards**: Error spike correlation, deployment markers, change events. These dashboards are designed for incident response, showing all relevant data in one place to enable rapid root cause analysis.

Dashboards must be owned and maintained. Unmaintained dashboards accumulate broken queries, stale data, and outdated visualizations. Assign dashboard ownership, review quarterly, and delete unused dashboards. A few high-quality dashboards are more valuable than many low-quality ones.

Deployment markers on dashboards enable immediate correlation between deployments and metric changes. Automatically annotate dashboards with deployment events from CI/CD pipelines. This correlation is essential for understanding the impact of deployments and identifying regressions quickly.
