# ADR-002: Kafka as the Event Bus for Inter-Service Communication

**Date:** 2026-01-22
**Status:** Accepted
**Deciders:** Platform Team, Backend Tech Lead

## Codex Reference

**Facet:** [event-driven-architecture/options.md](../../facets/event-driven-architecture/options.md)
**Recommendation Type:** Decision Matrix

## Context

Our backend is evolving from a monolith to a set of domain-oriented services (finance, orders, identity). These services need to communicate asynchronously for:

- Domain event propagation (e.g., "OrderPlaced" triggers invoice generation)
- Event sourcing for the finance domain (Axon Framework)
- Eventual consistency between bounded contexts

We need a messaging platform that supports both point-to-point commands and publish-subscribe events, handles high throughput during billing cycles, and provides durability guarantees.

## Decision

Use Apache Kafka as the primary event bus for inter-service communication. Axon Server remains the event store for event-sourced aggregates within the finance domain, with a Kafka extension to bridge Axon events to the broader platform.

## Options Considered

### Option 1: RabbitMQ

- **Description:** Traditional message broker with AMQP protocol, routing exchanges, and queue-based delivery
- **Pros:** Mature, well-understood, excellent Spring AMQP integration, simple to operate at small scale, flexible routing patterns, supports message TTL and dead-letter queues out of the box
- **Cons:** Performance degrades under high throughput with persistent messages, no native log-based replay, clustering is complex at scale, consumers manage their own offset/acknowledgment

### Option 2: Apache Kafka (Chosen)

- **Description:** Distributed log-based streaming platform with partitioned topics, consumer groups, and configurable retention
- **Pros:** Excellent throughput (millions of messages/sec), log-based replay for rebuilding state, built-in partitioning for parallelism, strong Spring Kafka integration, Axon Framework has a Kafka extension, consumer groups enable independent scaling
- **Cons:** More complex to operate (ZooKeeper/KRaft, partition management), steeper learning curve, not ideal for complex routing patterns, ordering only guaranteed within a partition, eventual consistency requires careful design

### Option 3: Axon Server Only

- **Description:** Use Axon Server as both the event store and the inter-service message bus
- **Pros:** Single system for events and commands, tight Axon Framework integration, built-in event replay, simpler topology
- **Cons:** Couples all services to Axon Framework, not designed for non-Axon consumers, limited ecosystem compared to Kafka, harder to integrate with third-party systems, vendor lock-in risk

## Decision Rationale

Kafka was chosen primarily for its throughput characteristics and log-based replay capability. During monthly billing cycles, the finance domain generates a high volume of events that RabbitMQ would struggle with under persistent delivery guarantees. Kafka's log-based architecture also means any new service can replay historical events to build its initial state — a capability we expect to use as we extract more services from the monolith.

Axon Server remains in play for intra-domain event sourcing within finance, but we don't want to couple all services to Axon Framework. Kafka serves as the cross-cutting event bus that any service can consume from, regardless of its internal framework.

### Criteria Weighting

| Criteria | Weight | Kafka | RabbitMQ | Axon Server |
|----------|--------|-------|----------|-------------|
| Scalability | High | High | Medium | Medium |
| Maintainability | High | Medium | High | Medium |
| Developer Experience | Medium | Medium | High | High (for Axon users) |
| Team Familiarity | Medium | Low | Medium | Medium |
| Cost | Low | Medium | High | Medium |

### Synergies

- **Event-Driven Architecture** — Kafka's partitioned topics align with our bounded context boundaries. Each domain owns its topics.
- **Data Persistence** — Kafka's retention policy acts as a short-term event store, complementing Axon Server's long-term event store for the finance domain.
- **Observability** — Kafka's consumer lag metrics integrate with Prometheus/Grafana for monitoring pipeline health.

## Consequences

### Positive

- High throughput handles billing cycle spikes without backpressure issues
- New services can replay topic history to bootstrap their state
- Consumer groups allow independent scaling per service
- Decouples services from any specific framework (unlike Axon Server-only approach)

### Negative

- Operational complexity is higher than RabbitMQ — mitigated by using managed Kafka (MSK/Confluent Cloud) or investing in platform team training
- Team has limited Kafka experience — mitigated by starting with simple produce/consume patterns and adopting Spring Kafka's opinionated defaults
- Message ordering requires careful partition key design — mitigated by using aggregate ID as partition key (natural ordering boundary)

### Neutral

- We'll maintain two messaging systems (Kafka + Axon Server) during the transition period. This is acceptable as they serve different purposes (cross-domain vs intra-domain).

## Evolution Triggers

Revisit this decision when:
- Managed Kafka costs exceed budget — consider consolidating simpler event flows back to RabbitMQ
- All services adopt Axon Framework — Axon Server-only becomes viable again
- We need complex routing patterns (e.g., content-based routing) that Kafka handles poorly — consider a RabbitMQ sidecar for those specific flows
- Kafka Streams or ksqlDB become necessary — evaluate whether the operational overhead is justified

## Related Decisions

- ADR-001: JWT-Based Authentication (stateless services complement event-driven decoupling)
- Decision Log #5: Axon Server for finance domain event sourcing
