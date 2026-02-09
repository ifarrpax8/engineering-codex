# Product Perspective: Observability

Observability is fundamentally a product concern, not merely an operational one. You cannot fix what you cannot see, and outages directly impact revenue and customer trust. Proactive monitoring enables teams to detect and resolve issues before users report them, transforming reactive firefighting into proactive reliability engineering.

## Business Value

The primary business value of observability manifests through reduced Mean Time to Resolution (MTTR). When incidents occur, comprehensive telemetry data enables engineers to identify root causes in minutes rather than hours. This translates directly to reduced downtime, preserved revenue, and maintained customer trust.

Beyond incident response, observability provides data-driven insights for capacity planning. Understanding actual usage patterns—not assumed patterns—enables accurate infrastructure provisioning. Over-provisioning wastes money; under-provisioning causes outages. Observability data reveals the optimal balance.

Customer-reported issues represent the tip of the iceberg. For every user who reports a problem, dozens more experience it silently and may churn. Real User Monitoring (RUM) captures actual user experience, revealing issues that synthetic monitoring misses. Understanding real user behavior—where they struggle, what errors they encounter, how performance affects conversion—enables product improvements that directly impact business outcomes.

## Service Level Objectives (SLOs)

SLOs define what "good enough" means for a service from a business perspective. They are product contracts that align engineering investment with business priorities. An SLO might state: "99.9% of API requests complete successfully in under 500ms." This is not a technical metric; it is a business commitment.

SLOs force prioritization decisions. If a service consistently meets its SLO, engineering effort can focus on new features. If a service violates its SLO, reliability work takes precedence. This prevents the common trap of optimizing metrics that don't matter while ignoring metrics that do.

SLOs should be defined collaboratively between product, engineering, and business stakeholders. They must reflect actual user expectations, not arbitrary technical targets. A payment processing service might require 99.99% availability, while an internal reporting dashboard might tolerate 99% availability. The business impact determines the target.

## Service Level Indicators (SLIs)

SLIs are measurable metrics that feed SLOs. They quantify the user experience in concrete terms. Common SLIs include:

- **Latency**: Response time percentiles (p50, p95, p99) measure how fast requests complete. p95 latency represents the experience of 95% of users, which is more meaningful than average latency, which can be skewed by outliers.

- **Error Rate**: The percentage of requests that fail. This must include both HTTP errors (4xx, 5xx) and application-level failures (timeouts, business logic errors).

- **Availability**: The percentage of time a service is operational and responding. This requires careful definition: does a degraded response count as available? Does maintenance downtime count?

- **Throughput**: Requests per second, orders per minute, messages processed per hour. Throughput SLIs help identify capacity constraints before they cause failures.

SLIs must be measured from the user's perspective. Measuring internal service health is insufficient if users cannot access the service. A service might report healthy while its load balancer is misconfigured, leaving users unable to connect.

## Error Budgets

An error budget is the allowed amount of unreliability. If an SLO is 99.9% availability, the error budget is 0.1% downtime per month—approximately 43 minutes. When the error budget is exhausted, feature development pauses in favor of reliability work.

Error budgets create a shared understanding of acceptable risk. They prevent perfectionism—100% availability is impossible and prohibitively expensive—while ensuring reliability remains a priority. Teams can spend their error budget on risky deployments or new features, but when it's gone, reliability becomes the focus.

Error budgets should be tracked and visible to the entire organization. Dashboards showing budget consumption help teams make informed decisions about deployment frequency and risk tolerance. A team with 90% of its error budget remaining can afford a risky deployment; a team with 5% remaining cannot.

## User-Centric Monitoring

Real User Monitoring (RUM) captures actual user experience by instrumenting the frontend application. It measures page load times, interaction latency, JavaScript errors, and resource loading performance from real users' browsers. This provides insights that synthetic monitoring—scheduled checks from known locations—cannot.

RUM reveals geographic variations in performance, browser-specific issues, and the impact of slow networks. A service might perform well in synthetic tests from data centers but fail for users on mobile networks. RUM exposes these discrepancies.

Synthetic monitoring remains valuable for availability checks and regression detection, but it cannot replace RUM for understanding actual user experience. Both complement each other: synthetic monitoring ensures services are reachable, while RUM ensures users can successfully complete their tasks.

## Incident Response

Observability data enables faster root cause analysis during incidents. Dashboards show what changed—did error rates spike? Did latency increase? Did throughput drop? Traces show where the failure occurred—which service, which operation, which database query. Logs show why—the exception message, the stack trace, the business context.

Without observability, incident response becomes guesswork. Engineers must reproduce issues manually, check logs across multiple systems, and correlate events manually. With observability, the data tells the story. A trace shows the exact request path that failed. Logs show the exception that caused it. Metrics show when it started and how widespread it is.

Deployment markers on dashboards enable immediate correlation between deployments and incidents. If error rates spike at 2:15 PM and a deployment occurred at 2:14 PM, the correlation is obvious. Without deployment markers, this requires manual investigation and delays resolution.

## Cost Considerations

Observability infrastructure can become expensive at scale. Log storage costs grow with log volume. Metric storage costs grow with cardinality—the number of unique time series. Trace storage costs grow with sampling rate and trace duration. These costs must be budgeted and optimized.

Log retention policies balance cost against utility. Recent logs are most valuable for debugging, while older logs are primarily useful for compliance and trend analysis. Aggressive retention policies reduce costs but limit historical analysis. Most organizations retain detailed logs for 7-30 days and aggregated metrics indefinitely.

Metric cardinality—the number of unique label combinations—directly impacts storage costs. Using high-cardinality values like user IDs or request IDs as metric labels creates millions of time series. This overwhelms metrics backends and increases costs exponentially. Use bounded label values (status codes, endpoint names) instead.

Trace sampling reduces storage costs while preserving visibility into errors and slow requests. Sampling 100% of traces is rarely necessary; sampling 1-10% of successful requests while keeping 100% of error traces provides good coverage at manageable cost.

Observability is an investment, not a cost. The cost of an unobserved outage—lost revenue, customer churn, engineering time spent debugging blindly—far exceeds the cost of observability infrastructure. However, costs must be managed through careful configuration of retention, sampling, and cardinality.
