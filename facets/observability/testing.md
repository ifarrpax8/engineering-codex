# Testing: Observability

Testing observability ensures that instrumentation works correctly, alerts fire appropriately, and dashboards provide accurate insights. Observability testing spans unit tests for instrumentation, integration tests for trace propagation, and production validation of alerting and monitoring.

## Testing Instrumentation

Instrumentation code must be tested to verify that traces, metrics, and logs are emitted correctly. Unit tests verify custom metric recording—assert that counters increment, gauges update, and histograms record values. Test metric labels to ensure they use bounded values, not high-cardinality identifiers.

Trace context propagation requires special attention in async environments. Test that trace IDs propagate across thread pool boundaries, coroutine contexts, and message queue consumers. Verify that child spans are created correctly and parent-child relationships are maintained. Test that trace context is not lost when crossing async boundaries—a common failure mode.

Log structure testing verifies that log output matches expected JSON schema. Assert that required fields (timestamp, level, message, trace ID, service name) are present. Verify that MDC context (correlation IDs, user IDs) appears in log output. Test log level configuration per environment—production should not emit DEBUG logs, while development should.

Integration tests verify end-to-end observability. Make a request through the API gateway, verify that a trace is created with spans for each service, verify that logs from all services include the same trace ID, and verify that metrics are recorded. These tests catch configuration errors and missing instrumentation.

## Testing Alerts

Alerts must be tested to ensure they fire with correct severity and routing. Simulate failure conditions in staging environments—inject errors, add latency, exhaust resources—and verify that alerts fire. Test alert silence rules to ensure maintenance windows don't trigger false alarms.

Alert routing tests verify that critical alerts reach on-call engineers while warning alerts are logged for review. Test escalation policies—if the primary on-call doesn't acknowledge, does the alert escalate? Test integration with PagerDuty or Opsgenie to ensure alerts are delivered correctly.

Alert content must be actionable. Review alert messages to ensure they include enough context to diagnose the issue. "Error rate high" is not actionable; "Payment service error rate 5% (threshold 1%), affecting 12% of checkout requests" is actionable. Test that alert messages include relevant context (service name, error type, affected user percentage).

False positive testing identifies alerts that fire incorrectly. If an alert fires during normal operations, it needs tuning. Regularly review alert history to identify false positives and adjust thresholds or conditions. An alert that fires weekly but never requires action should be removed or significantly tuned.

## Load Testing with Observability

Load testing provides an opportunity to validate observability under realistic conditions. Run load tests and verify that dashboards show expected patterns—request rate increases, latency may increase but should remain within bounds, error rate should remain low. Identify metric cardinality explosions under load—do high-cardinality labels create excessive time series?

Trace sampling behavior under load is critical. Verify that sampling rates remain stable under high throughput. Head-based sampling should maintain consistent rates; tail-based sampling should prioritize error traces. Test that trace collection doesn't add significant overhead—observability should not degrade application performance.

Log volume under load must be manageable. Verify that log aggregation can handle peak load without dropping logs or experiencing significant delay. Test log retention and archival policies to ensure they function correctly under load.

Metric export under load requires validation. Prometheus scraping, or push-based export to Datadog or CloudWatch, must handle high metric cardinality without dropping data. Verify that metric backends can ingest the volume of metrics generated under load.

## Testing Log Structure

Log structure testing ensures consistency across services. Assert that all services emit logs with the same JSON schema—consistent field names, data types, and nesting structure. Inconsistent log structure makes querying and aggregation difficult.

Correlation ID propagation testing verifies that correlation IDs flow through all services. Generate a correlation ID at the API gateway, make a request that touches multiple services, and verify that all log entries include the same correlation ID. Test that correlation IDs propagate through message queues and async operations.

Log level configuration testing verifies that log levels are set correctly per environment. Production should emit INFO and above, not DEBUG. Development and staging should emit DEBUG logs for detailed diagnostics. Test that log level changes take effect without application restart (if supported).

Sensitive data scrubbing tests verify that passwords, tokens, and PII are not logged. Inject test data containing sensitive information and verify that logs are scrubbed. Test that credit card numbers, SSNs, and email addresses are masked or excluded from logs.

## Synthetic Monitoring Tests

Synthetic monitoring provides external validation of service availability and performance. Health check endpoint tests verify that /health endpoints return correct status codes and include dependency checks. A health check that always returns 200 without checking database connectivity is useless.

Availability monitoring tests verify that services are reachable from external locations. Test from multiple geographic regions to identify regional issues. Verify that monitoring locations match user locations—if most users are in Europe, monitoring from US data centers provides limited value.

SLI measurement accuracy requires validation. If an SLO is "99.9% availability," verify that availability is measured correctly. Does maintenance downtime count? Does degraded performance count as unavailable? Test edge cases—brief network hiccups, planned maintenance, gradual degradation—to ensure SLI calculation matches business expectations.

Synthetic transaction tests verify that critical user flows complete successfully. Test checkout flows, login flows, and key API endpoints from external locations. These tests catch issues that internal health checks miss—configuration errors, DNS issues, firewall rules.

## Chaos Engineering

Chaos engineering introduces controlled failures to validate observability under adverse conditions. Kill a service instance and verify that traces show the failure, metrics show the error rate increase, and alerts fire. Verify that load balancers route around the failure and that remaining instances handle increased load.

Add latency to service calls and verify that traces show the latency, dashboards reflect the degradation, and alerts fire if latency exceeds thresholds. Test that timeout configurations are correct—services should fail fast rather than hanging indefinitely.

Exhaust connection pools or thread pools and verify that observability captures the resource exhaustion. Metrics should show connection pool utilization, traces should show timeouts or rejections, and alerts should fire before complete failure.

Network partition scenarios test distributed tracing. Partition services and verify that traces still capture operations on each side of the partition, even if they cannot complete end-to-end. This validates that observability works even when services cannot communicate.

Chaos experiments should be run regularly in staging environments. They validate that observability catches issues and that incident response procedures work correctly. Document expected observability behavior for each chaos scenario to enable comparison with actual behavior.

## Testing Dashboards

Dashboard testing ensures that queries return data for expected scenarios. Create test scenarios—high load, error conditions, normal operation—and verify that dashboards display expected data. Test that dashboard panels load without errors—broken queries should fail gracefully, not crash the dashboard.

Deployment marker testing verifies that deployments are annotated on dashboards automatically. Deploy a test change and verify that a marker appears at the correct time. This correlation is essential for understanding the impact of deployments.

Dashboard query performance testing ensures that queries complete in reasonable time. Complex queries over large time ranges can be slow. Test query performance and optimize slow queries. Consider pre-aggregating data or using summary tables for historical data.

Data freshness testing verifies that dashboards show recent data. Metrics and logs should appear within seconds of generation. Traces may have slightly longer delay due to batching and processing. Test that data appears in dashboards within expected timeframes.

Access control testing verifies that dashboards are accessible to authorized users only. Sensitive business metrics or infrastructure details may require restricted access. Test that authentication and authorization work correctly for dashboard access.
