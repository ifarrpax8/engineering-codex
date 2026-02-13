# Options: Observability

## Contents

- [Observability Stack Options](#observability-stack-options)
  - [Open Source Stack (OpenTelemetry + Prometheus + Grafana + Loki + Tempo/Jaeger)](#open-source-stack-opentelemetry--prometheus--grafana--loki--tempojaeger)
  - [Cloud-Native (CloudWatch / Azure Monitor / GCP Operations)](#cloud-native-cloudwatch--azure-monitor--gcp-operations)
  - [Commercial Platform (Datadog / New Relic / Dynatrace)](#commercial-platform-datadog--new-relic--dynatrace)
- [Instrumentation Standard Options](#instrumentation-standard-options)
  - [OpenTelemetry](#opentelemetry)
  - [Vendor-Specific SDK (Datadog APM, New Relic Agent)](#vendor-specific-sdk-datadog-apm-new-relic-agent)
  - [Micrometer Only](#micrometer-only)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

Observability stack selection depends on scale, budget, operational capabilities, and vendor preferences. This decision matrix evaluates major options and provides guidance for selection.

## Observability Stack Options

### Open Source Stack (OpenTelemetry + Prometheus + Grafana + Loki + Tempo/Jaeger)

**Description**: Self-hosted, vendor-neutral observability stack using open source components. OpenTelemetry for instrumentation, Prometheus for metrics, Grafana for visualization, Loki for logs, Tempo or Jaeger for traces.

**Strengths**:
- Vendor-neutral instrumentation with OpenTelemetry enables switching backends without re-instrumenting
- Full control over data storage, retention, and access
- No per-data-point pricing—costs are infrastructure and operational overhead
- Open source community support and extensibility
- Can be run on-premises for compliance requirements
- Grafana provides unified visualization for all telemetry types

**Weaknesses**:
- Significant operational overhead—requires expertise to operate and maintain
- Scaling requires careful planning (Prometheus federation, Loki clustering, Tempo scaling)
- No managed support—issues require internal expertise or community support
- Initial setup complexity—multiple components to configure and integrate
- Alerting requires separate system (Alertmanager) and on-call integration (PagerDuty) setup
- Cost of operational time can exceed managed service costs for small teams

**Best For**:
- Teams with strong DevOps capabilities and operational expertise
- Organizations requiring data sovereignty or on-premises deployment
- High-scale deployments where per-data-point pricing becomes prohibitive
- Multi-cloud or hybrid cloud environments requiring vendor portability
- Organizations with existing Kubernetes expertise (components run well on K8s)

**Avoid When**:
- Small teams without dedicated DevOps resources
- Rapid scaling where operational overhead becomes a bottleneck
- Compliance requirements that benefit from vendor certifications (SOC 2, etc.)
- Need for advanced features (AI-powered anomaly detection, automated root cause analysis)

### Cloud-Native (CloudWatch / Azure Monitor / GCP Operations)

**Description**: Managed observability services provided by cloud providers. Tightly integrated with other cloud services (Lambda, ECS, RDS) with automatic instrumentation.

**Strengths**:
- Zero operational overhead—fully managed by cloud provider
- Deep integration with cloud services (automatic metrics from RDS, Lambda, ECS)
- Unified billing with other cloud services simplifies cost management
- Native integration with cloud IAM and security services
- Automatic scaling handles traffic growth without configuration
- Vendor support and SLAs for enterprise customers

**Weaknesses**:
- Vendor lock-in—data and queries are cloud-provider specific
- Limited open source compatibility—OpenTelemetry support varies by provider
- Per-data-point pricing can become expensive at scale
- Less flexible than self-hosted solutions—limited customization options
- Multi-cloud deployments require separate observability per cloud
- Feature depth may lag behind specialized observability platforms

**Best For**:
- Teams already committed to a single cloud provider
- Small to medium teams without dedicated DevOps resources
- Applications heavily using cloud-native services (Lambda, ECS, RDS)
- Organizations prioritizing operational simplicity over flexibility
- Rapid prototyping and early-stage products

**Avoid When**:
- Multi-cloud or hybrid cloud deployments
- Requiring vendor-neutral instrumentation for future flexibility
- Very high scale where per-data-point pricing becomes prohibitive
- Need for advanced observability features not available in cloud provider stack
- On-premises deployment requirements

### Commercial Platform (Datadog / New Relic / Dynatrace)

**Description**: Fully managed, unified observability platforms with advanced features. Single platform for logs, metrics, traces, APM, and infrastructure monitoring.

**Strengths**:
- Unified platform eliminates tool sprawl and integration complexity
- Advanced features: AI-powered anomaly detection, automated root cause analysis, service maps
- Excellent developer experience with intuitive UIs and powerful query languages
- Comprehensive auto-instrumentation for common frameworks and languages
- Strong support and professional services for enterprise customers
- Built-in collaboration features (incident management, team dashboards)

**Weaknesses**:
- Significant cost at scale—pricing based on data volume and hosts
- Vendor lock-in—proprietary agents and data formats
- Cost can exceed self-hosted solutions for high-scale deployments
- Less control over data storage and retention policies
- May include features that aren't needed, increasing cost
- Migration to another platform requires re-instrumentation

**Best For**:
- Enterprise organizations with budget for premium observability
- Teams requiring advanced features (anomaly detection, service maps, AI insights)
- Organizations prioritizing developer productivity over cost optimization
- Multi-technology stacks requiring unified observability
- Teams without operational expertise to run self-hosted solutions

**Avoid When**:
- Cost-sensitive deployments where per-data-point pricing is prohibitive
- Requiring data sovereignty or on-premises deployment
- Very high scale where commercial pricing exceeds operational costs of self-hosted
- Preference for open source and vendor-neutral solutions
- Simple deployments where cloud-native solutions are sufficient

## Instrumentation Standard Options

### OpenTelemetry

**Description**: Vendor-neutral, standardized observability instrumentation supporting traces, metrics, and logs. Industry standard with broad vendor and framework support.

**Strengths**:
- Vendor-neutral—instrument once, switch backends without code changes
- Industry standard with broad adoption and community support
- Supports all three pillars (traces, metrics, logs) with unified API
- Excellent auto-instrumentation for Spring Boot, HTTP clients, databases, message queues
- Active development and rapid feature additions
- Future-proof choice as industry moves toward standardization

**Weaknesses**:
- Relatively new compared to vendor-specific SDKs—some edge cases may exist
- Requires OpenTelemetry Collector or compatible backend
- Less deep integration with specific platforms compared to vendor SDKs
- Learning curve for teams new to observability concepts

**When to Use**: Default choice for new projects. Provides maximum flexibility and future-proofing. Use unless specific vendor features are required that aren't available through OpenTelemetry.

### Vendor-Specific SDK (Datadog APM, New Relic Agent)

**Description**: Proprietary instrumentation SDKs provided by commercial observability platforms. Deep integration with platform-specific features.

**Strengths**:
- Deep integration with platform features (service maps, AI insights, automated analysis)
- Optimized for specific platform's data model and query capabilities
- Often includes additional context and metadata automatically
- Platform-specific optimizations and performance improvements
- Strong support from vendor for instrumentation issues

**Weaknesses**:
- Vendor lock-in—switching platforms requires re-instrumenting
- Limited portability—cannot easily switch to open source or other vendors
- May require platform-specific configuration and knowledge
- Less standardized—each vendor has different APIs and concepts

**When to Use**: When committed to a specific commercial platform long-term and require platform-specific features not available through OpenTelemetry. Generally not recommended for new projects due to lock-in risk.

### Micrometer Only

**Description**: Spring Boot's native metrics abstraction. Provides metrics only, no distributed tracing.

**Strengths**:
- Native Spring Boot integration with minimal configuration
- Simple and lightweight for metrics-only use cases
- Good for monolithic applications that don't need distributed tracing
- Exports to multiple backends (Prometheus, Datadog, CloudWatch) without code changes

**Weaknesses**:
- No distributed tracing—insufficient for microservices architectures
- Metrics-only approach misses request flow visibility
- Less comprehensive than full observability stack
- Not suitable for distributed systems requiring trace correlation

**When to Use**: Monolithic applications with simple architectures that don't require distributed tracing. Not suitable for microservices or distributed systems. Consider migrating to OpenTelemetry for future flexibility.

## Evaluation Criteria

| Criteria | Weight | Open Source | Cloud-Native | Commercial |
|----------|--------|-------------|--------------|------------|
| **Cost** | High | Low (infrastructure only) | Medium (per-data-point) | High (per-data-point + hosts) |
| **Vendor Lock-in** | Medium | None | High | High |
| **Feature Depth** | Medium | Good | Good | Excellent |
| **Operational Overhead** | High | High | None | None |
| **DX (Developer Experience)** | Medium | Good | Good | Excellent |
| **Scalability** | High | Excellent (with expertise) | Excellent (automatic) | Excellent (automatic) |
| **Multi-Cloud Support** | Low | Excellent | Poor | Good |
| **On-Premises Support** | Low | Excellent | Limited | Limited |

**Nuanced Trade-offs:**

**Cost vs. Operational Overhead:** Open source stacks have low data costs but high operational overhead. Cloud-native solutions have medium data costs but zero operational overhead. Commercial platforms have high data costs but zero operational overhead. The trade-off depends on team size and expertise: small teams benefit from managed solutions despite higher costs; large teams with DevOps expertise benefit from open source cost savings.

**Cost breakdown example:** A service generating 1M traces/day, 10GB logs/day, and 100K metrics/day:
- **Open source (self-hosted):** ~$500/month infrastructure + 20 hours/month operational time = ~$2,500/month total (assuming $100/hour engineering cost)
- **Cloud-native (CloudWatch):** ~$1,500/month data costs + 0 hours operational = ~$1,500/month total
- **Commercial (Datadog):** ~$3,000/month data costs + 0 hours operational = ~$3,000/month total

**When open source costs less:** Teams with dedicated DevOps (20+ hours/month available), high data volumes (>50M traces/day), or multi-year commitments where operational expertise compounds.

**When managed solutions cost less:** Small teams (<5 engineers), low data volumes (<10M traces/day), or teams where engineering time is better spent on product features.

**Vendor Lock-in vs. Feature Depth:** Vendor-specific solutions (cloud-native, commercial) provide deeper feature integration but create lock-in. Open source solutions provide vendor portability but may lack advanced features. The trade-off depends on long-term strategy: teams committed to a single cloud/provider can accept lock-in for better features; teams requiring flexibility should prioritize open source.

**Scalability vs. Operational Complexity:** Open source stacks scale excellently but require expertise to operate. Managed solutions scale automatically but provide less control. The trade-off depends on operational capabilities: teams with strong DevOps can handle open source complexity; teams without DevOps should prefer managed solutions.

**Feature Depth vs. Cost:** Commercial platforms provide excellent features (AI-powered anomaly detection, automated root cause analysis) but at high cost. Open source provides good features at low cost but requires building advanced features internally. The trade-off depends on feature requirements: teams requiring advanced features may justify commercial costs; teams with basic needs can use open source.

**Multi-Cloud vs. Integration Depth:** Open source provides excellent multi-cloud support but requires integration work. Cloud-native solutions provide deep cloud integration but poor multi-cloud support. The trade-off depends on deployment strategy: multi-cloud deployments require open source; single-cloud deployments benefit from cloud-native integration.

## Recommendation Guidance

**Default Recommendation**: OpenTelemetry for instrumentation (vendor-neutral, portable). Backend choice depends on scale and budget.

**Small Teams / Early Stage**: Start with cloud-native observability (CloudWatch, Azure Monitor, GCP Operations). Use what your cloud provider offers—low operational overhead enables focusing on product development. Migrate to open source or commercial platforms as scale and requirements grow.

**Growing Teams**: Open source stack (OpenTelemetry + Prometheus + Grafana) provides full control and avoids per-data-point pricing. Requires operational investment but provides flexibility and cost control at scale. Consider managed Grafana Cloud as a middle ground—OpenTelemetry instrumentation with managed backend.

**Enterprise / High Scale**: Commercial platforms (Datadog, New Relic) reduce operational burden and provide advanced features. Cost is significant but may be justified by developer productivity and reduced operational overhead. Evaluate cost vs. operational time savings.

**Always Start with OpenTelemetry SDK**: Regardless of backend choice, use OpenTelemetry for instrumentation. This provides vendor portability—you can switch backends without re-instrumenting. OpenTelemetry is the industry standard and future-proof choice.

**Decision Scenarios:**

**Scenario 1: Startup with Limited Budget**
- **Choice:** Cloud-native observability (CloudWatch, Azure Monitor)
- **Rationale:** Zero operational overhead enables focusing on product development. Costs are manageable at low scale. Can migrate to open source or commercial as scale grows.
- **Trade-off:** Accept vendor lock-in for operational simplicity and cost control.

**Scenario 2: Enterprise with Multi-Cloud Strategy**
- **Choice:** Open source stack (OpenTelemetry + Prometheus + Grafana)
- **Rationale:** Vendor portability essential for multi-cloud. Operational overhead acceptable with dedicated DevOps team. Cost control important at scale.
- **Trade-off:** Accept operational complexity for vendor portability and cost control.

**Scenario 3: High-Growth Startup with Budget**
- **Choice:** Commercial platform (Datadog, New Relic)
- **Rationale:** Advanced features (anomaly detection, service maps) provide competitive advantage. Zero operational overhead enables scaling team without DevOps overhead. Cost justified by developer productivity.
- **Trade-off:** Accept high cost for advanced features and operational simplicity.

**Scenario 4: Regulated Industry (Healthcare, Finance)**
- **Choice:** Open source stack with on-premises deployment
- **Rationale:** Data sovereignty requirements prevent cloud solutions. Compliance requirements benefit from open source auditability. Operational overhead acceptable for compliance.
- **Trade-off:** Accept operational complexity for compliance and data sovereignty.

**Migration Paths:**

**Cloud-Native → Open Source:** Migrate when per-data-point costs become prohibitive or multi-cloud requirements emerge. Use OpenTelemetry to maintain instrumentation while switching backends. Gradual migration possible with dual-write patterns.

**Open Source → Commercial:** Migrate when requiring advanced features not available in open source or operational overhead becomes burden. OpenTelemetry enables gradual migration without re-instrumentation.

**Commercial → Open Source:** Migrate when costs become prohibitive or vendor lock-in concerns arise. OpenTelemetry enables migration, but may lose platform-specific features (AI insights, service maps).

## Synergies

**Microservices Architecture**: Distributed tracing is essential, not optional. OpenTelemetry with tail-based sampling provides visibility into request flows across services. Service maps and dependency graphs enable understanding service relationships.

**Event-Driven Architecture**: Trace events through message brokers, monitor consumer lag, and correlate producer and consumer spans. OpenTelemetry provides Kafka and AMQP instrumentation. Message queue observability is critical for event-driven systems.

**Micro Frontend Architecture (MFE)**: Correlate frontend errors with backend traces using trace IDs. Include trace IDs in frontend error reports to enable end-to-end debugging. RUM (Real User Monitoring) provides frontend observability that complements backend traces.

**CI/CD Integration**: Deploy markers on dashboards enable correlating deployments with metric changes. Canary monitoring with SLO-based rollback requires comprehensive observability. OpenTelemetry enables adding deployment version as resource attributes.

## Evolution Triggers

**First Production Incident Without Observability Data**: Add structured logging and basic metrics immediately. This is the minimum viable observability. Use cloud-native solutions for rapid implementation.

**Microservice Adoption**: Add distributed tracing when moving to microservices. OpenTelemetry provides automatic instrumentation for service-to-service communication. This is when observability becomes essential, not optional.

**Customer-Reported Issues Exceeding Internal Detection**: Add Real User Monitoring (RUM) to capture actual user experience. Synthetic monitoring catches availability issues, but RUM catches user-impacting problems that synthetic monitoring misses.

**Alert Fatigue**: Adopt SLO-based alerting with error budgets. Move from metric-based alerts to symptom-based alerts. Focus on user impact, not infrastructure metrics. This requires cultural change as much as technical change.

**SLO-Based Alerting Decision Framework:**

**When to adopt SLO-based alerting:**
- Team has >20 alerts and alert fatigue is occurring (alerts ignored, false positives common)
- Services have defined SLOs (availability, latency, error rate)
- Error budgets are tracked and visible to the team
- Team understands the difference between symptoms (user impact) and causes (infrastructure metrics)

**SLO-based alerting thresholds:**
- **Critical alert:** Error budget burning 10x faster than expected (e.g., 20 minutes downtime in 6 hours when monthly budget is 43 minutes). Users are significantly affected. Requires immediate response.
- **Warning alert:** Error budget burning 2x faster than expected. Degradation detected. Should be addressed during business hours.
- **Info alert:** Error budget consumption normal but approaching limits. Monitor but no action required.

**Example SLO-based alert calculation:**
- SLO: 99.9% availability (43 minutes downtime per month)
- Expected burn rate: 43 minutes / 720 hours = 0.06 minutes per hour
- Actual burn rate: 20 minutes downtime in 6 hours = 3.33 minutes per hour
- Burn rate multiplier: 3.33 / 0.06 = 55x faster than expected → Critical alert

**Migration from metric-based to SLO-based alerting:**
1. Define SLOs for each service (availability, latency, error rate)
2. Calculate error budgets (1 - SLO)
3. Replace metric-based alerts with SLO burn rate alerts
4. Remove infrastructure alerts (CPU, memory) unless they directly impact SLOs
5. Review alerts quarterly—remove unused alerts, tune thresholds

**Trade-off:** SLO-based alerting reduces alert volume by 70-90% but requires upfront SLO definition work. Teams without SLOs should start with symptom-based alerts (error rate, latency) before moving to full SLO-based alerting.

**Observability Costs Growing**: Optimize sampling rates, log retention policies, and metric cardinality. High-cardinality labels create excessive time series. Aggressive log retention increases storage costs. Tail-based sampling reduces trace volume while preserving error visibility.

**Need for Advanced Features**: Consider commercial platforms when requiring AI-powered anomaly detection, automated root cause analysis, or service maps. These features require significant engineering effort to build internally and may justify commercial platform costs.
