---
title: Observability
type: facet
last_updated: 2026-02-09
---

# Observability

Logging, metrics, tracing, alerting, dashboards, SLOs.

## TL;DR

- **Default choice**: OpenTelemetry for instrumentation (vendor-neutral, portable); cloud-native observability (CloudWatch, Azure Monitor, GCP Operations) for small teams; open source stack (Prometheus + Grafana + Loki + Tempo) for growing teams
- **Key principle**: Always start with OpenTelemetry SDK regardless of backend—instrument once, switch backends without re-instrumenting
- **Watch out for**: High-cardinality labels create excessive time series in Prometheus, leading to performance issues and increased costs
- **Start here**: [Options](options.md) for observability stack selection and instrumentation standard guidance

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Backend Architecture](../backend-architecture/) -- Distributed systems require distributed observability
- [Event-Driven Architecture](../event-driven-architecture/) -- Tracing event flows across services
- [Error Handling](../error-handling/) -- Error tracking and alerting
- [Performance](../performance/) -- Performance metrics and profiling
- [CI/CD](../ci-cd/) -- Deployment tracking and canary monitoring
- [Security](../security/) -- Audit logging, access monitoring

## Related Experiences

- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Frontend performance monitoring
- [Feedback & Support](../../experiences/feedback-and-support/) -- User-reported issues correlated with telemetry
