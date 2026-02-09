---
title: Event-Driven Architecture - Gotchas
type: perspective
facet: event-driven-architecture
last_updated: 2026-02-09
---

# Gotchas: Common Pitfalls in Event-Driven Systems

## Event Storms

Event storms occur when one event triggers a cascade of events that trigger more events, creating exponential amplification. A single `OrderPlaced` event might trigger `InventoryReserved`, which triggers `InventoryLow`, which triggers `ReorderRequested`, which triggers `SupplierNotified`, and so on. Without careful design, event storms can overwhelm systems and create cascading failures.

Event storms often result from circular event chains. Service A emits an event that Service B consumes and emits another event that Service A consumes, creating a loop. These loops can amplify load exponentially. A single event can trigger thousands of events across the system.

Guard against event storms by designing events carefully. Avoid events that trigger immediate reactions in a chain. Use sagas for complex multi-step processes instead of pure choreography. Monitor event throughput for anomalies—sudden spikes indicate event storms.

Circuit breakers on consumers prevent event storms from cascading. If a consumer is overwhelmed, the circuit breaker opens and stops processing events temporarily. This prevents the consumer from amplifying load. However, circuit breakers must be configured correctly—they shouldn't open under normal load.

Monitor event throughput at the broker level. Set alerts when throughput exceeds thresholds. Identify event sources that emit excessive events. Review event designs to ensure they don't create amplification loops. Event storms are easier to prevent than to fix.

## Eventual Consistency Confusion

Developers accustomed to synchronous systems expect immediate consistency. They write code that assumes that after a command succeeds, the read model immediately reflects the change. In event-driven systems, this assumption is false. Commands emit events that propagate asynchronously. Read models update eventually, not immediately.

This confusion manifests as bugs. A user submits a form, receives confirmation, but refreshing the page shows the old state. The write succeeded, but the read model hasn't updated yet. Developers blame the read model or add artificial delays, missing the root cause—eventual consistency.

Communicate eventual consistency clearly in user interfaces. Show "processing" states while events propagate. Use optimistic UI updates—update the UI immediately, then reconcile with server state. Use WebSocket or Server-Sent Events to push updates when read models converge.

Design APIs to handle eventual consistency. Don't return read models immediately after writes. Return success and let clients poll or subscribe for updates. Or return the write model's state directly rather than querying the read model.

Test eventual consistency explicitly. After publishing events, verify that read models eventually converge. Use polling with timeouts rather than fixed waits. Set SLOs for consistency windows. Monitor consistency windows in production to ensure they meet requirements.

## Ordering Guarantees

Kafka guarantees ordering within a partition, not across partitions. If events for the same entity go to different partitions, they may be processed out of order. An `OrderCancelled` event might be processed before `OrderPlaced` if they're in different partitions, causing errors.

Use entity IDs as partition keys to ensure related events maintain order. Events for the same order ID go to the same partition and maintain order. However, this limits parallelism—all events for an entity are processed sequentially. Balance ordering requirements with parallelism needs.

RabbitMQ queues maintain order, but multiple queues don't guarantee order across queues. If an order process involves multiple queues, events might be processed out of order. Use single queues or routing keys to ensure ordering when needed.

Ordering requirements vary by use case. Financial transactions require strict ordering. E-commerce inventory updates require ordering. Analytics events might not require ordering. Understand ordering requirements and design accordingly.

Test ordering explicitly. Publish events out of order and verify that systems handle them correctly. Some systems can tolerate out-of-order events with idempotency. Others require strict ordering. Design and test accordingly.

## Schema Evolution Breaking Consumers

Adding a required field to an event breaks existing consumers. Old consumers can't deserialize new events without the required field. This causes deserialization errors and consumer failures. Schema evolution must maintain backward compatibility.

Always make new fields optional. Old consumers ignore fields they don't understand. New consumers can handle old events that lack new fields. This enables independent evolution. Use default values for new fields to maintain compatibility.

Use schema registries to enforce compatibility. Schema registries check that new schemas are backward compatible with previous versions. They prevent breaking changes before deployment. However, schema registries require discipline—teams must register schemas and check compatibility.

Test schema evolution explicitly. Publish old event versions and verify that new consumers can process them. Publish new event versions and verify that old consumers can process them. Use contract testing to verify compatibility.

Plan for upcasting old events. When event schemas change, old events remain in the event store. Systems must upcast old events to new formats during replay. Design upcasters to handle version migration. Test upcasting thoroughly.

## Lost Messages

Message loss occurs when consumers crash at the wrong time. If a consumer crashes after processing but before acknowledging, the message is redelivered (at-least-once). If it crashes after acknowledging but before processing, the message is lost (at-most-once). Choose your guarantee deliberately.

At-most-once delivery provides fire-and-forget semantics. Messages are sent once. If delivery fails, the message is lost. This provides the lowest latency but risks message loss. Use it only for non-critical notifications.

At-least-once delivery retries until acknowledgment. If a consumer crashes before acknowledging, the message is redelivered. This ensures no message loss but risks duplicate processing. Consumers must be idempotent to handle duplicates correctly.

Exactly-once delivery is difficult to achieve end-to-end. Kafka provides exactly-once semantics with idempotent producers and transactions, but achieving exactly-once across systems requires careful design. Use it only when duplicates are unacceptable.

Choose delivery guarantees based on business requirements. Critical events require at-least-once with idempotent consumers. Non-critical events might tolerate at-most-once for better performance. Financial transactions might require exactly-once.

Test message loss scenarios. Simulate consumer crashes and verify that messages are handled correctly. Test that at-least-once doesn't lose messages. Test that at-most-once doesn't duplicate messages. Understand the trade-offs and choose accordingly.

## Debugging Distributed Flows

Following an event through multiple services is difficult without proper tooling. Events flow through producers, brokers, and consumers. Logs are scattered across services. Without correlation IDs and distributed tracing, debugging production issues becomes guesswork.

Correlation IDs enable tracing events through services. Every event should carry a correlation ID. Services should propagate correlation IDs through all events and commands. Logs should include correlation IDs. This enables correlating logs across services.

Distributed tracing tools like Zipkin or Jaeger provide end-to-end visibility. They trace requests and events through multiple services, showing the complete flow. Invest in distributed tracing from day one. It's essential for debugging distributed systems.

Without observability, debugging is guesswork. Operators can't see where events are stuck. They can't identify bottlenecks or failures. They resort to adding logging and hoping to catch issues. Invest in observability infrastructure—it pays dividends during incidents.

Test observability explicitly. Verify that correlation IDs propagate correctly. Verify that traces can be followed across services. Verify that metrics capture event processing correctly. Observability that doesn't work is worse than no observability—it provides false confidence.

## Dead Letter Queue Neglect

DLQ messages accumulate silently without monitoring. Failed events are routed to DLQs, but without alerts, operators don't know about them. DLQ depth grows, indicating systemic issues, but no one investigates. This leads to degraded system behavior and user impact.

Monitor DLQ depth and alert when it grows. Set thresholds based on normal failure rates. Alert when DLQ depth exceeds thresholds. Investigate root causes. DLQ messages indicate problems that need attention.

Provide tooling to inspect and replay DLQ messages. Operators need to understand why messages failed. They need to replay messages after fixes. Build admin interfaces for DLQ management. This enables efficient incident response.

Don't let DLQs accumulate indefinitely. Investigate failures and fix root causes. Replay messages after fixes. Clear DLQs periodically. DLQs are a safety mechanism, not a permanent storage solution.

Design consumers to handle failures gracefully. Validate event data before processing. Handle missing entities gracefully. Log errors with sufficient context for debugging. Don't let failures crash consumers—handle errors and move to DLQ.

## Tight Coupling Through Events

If Consumer A breaks when Producer B changes event format, you have coupling through events instead of through APIs. Events are supposed to reduce coupling, but without proper schema management, they create hidden coupling that's harder to detect than API coupling.

Schema contracts prevent coupling. Define event schemas as contracts between producers and consumers. Use schema registries to enforce compatibility. Use consumer-driven contract tests to verify compatibility. This prevents breaking changes.

Version events carefully. Breaking changes require coordination. Backward-compatible changes enable independent evolution. Plan for schema evolution from the start. Version events from day one.

Monitor schema compatibility. Track schema changes and compatibility checks. Identify breaking changes before deployment. Schema evolution affects all consumers. Breaking changes require coordination.

Design events to be self-contained. Include enough data for consumers to process without calling back to producers. Avoid "thin events" that require callbacks. This reduces coupling and improves resilience.

## Over-Engineering with Events

Making every method call an event is over-engineering. Internal method calls within a service should be direct function calls. Events are for cross-boundary communication, not intra-service orchestration.

Events add overhead—serialization, network calls, broker processing. Use events when the benefits justify the costs. Cross-service communication benefits from events. Internal service calls don't need events.

Recognize when to use events and when not to. Cross-boundary communication benefits from events. Long-running processes benefit from events. Real-time updates benefit from events. Simple internal method calls don't need events.

Start simple and add events when needed. Don't design everything as event-driven from the start. Use synchronous calls within services. Introduce events when you need decoupling, scalability, or resilience.

Balance event-driven patterns with synchronous patterns. Use synchronous APIs for request-response. Use events for notifications and state changes. Use the right pattern for the right use case.

## Consumer Lag Snowball

A slow consumer falls behind, lag grows, the consumer processes stale data, catches up slowly, and may never catch up during peak load. Consumer lag that grows unbounded indicates consumers can't keep up with producers.

Monitor consumer lag and set alerts. Track lag per consumer group. Set thresholds based on acceptable latency. Alert when lag exceeds thresholds. Consumer lag that grows indicates problems.

Scale consumers horizontally to reduce lag. More consumers process more events in parallel. However, scaling has limits—too many consumers can cause overhead. Balance parallelism with overhead.

Identify slow consumers and optimize them. Profile consumer performance. Identify bottlenecks—slow database queries, external API calls, or complex processing. Optimize slow consumers to reduce lag.

Design consumers for performance. Keep processing fast. Avoid long-running operations in event handlers. Use async processing for slow operations. Batch processing when possible. Performance is critical for event-driven systems.

Set appropriate partition counts for parallelism. More partitions enable more parallel consumers. However, too many partitions can cause overhead. Balance parallelism with overhead. Consumer lag that grows unbounded requires immediate attention.
