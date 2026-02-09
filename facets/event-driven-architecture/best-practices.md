---
title: Event-Driven Architecture - Best Practices
type: perspective
facet: event-driven-architecture
last_updated: 2026-02-09
---

# Best Practices: Event-Driven Systems

## Design Events as Facts

Events represent facts that have already happened. They describe what occurred, not what should occur. Name events in past tense: `OrderPlaced`, `PaymentProcessed`, `InventoryReserved`. Avoid imperative names like `ProcessOrder` or `SendNotification`—these are commands, not events.

Events are immutable records of history. Once published, they cannot be changed or retracted. They become part of the permanent record. Design events to capture what happened in business terms. Include enough context for consumers to understand the event without calling back to the producer.

Self-contained events include all necessary data for consumers to process them. Avoid "thin events" that contain only an ID requiring a callback. If a consumer needs order details to process an `OrderPlaced` event, include order details in the event. This reduces coupling and improves resilience—consumers don't depend on producer availability.

Events should be business-meaningful. Domain events represent state changes that matter to the business. Avoid technical events like `DatabaseUpdated` or `CacheInvalidated`—these are implementation details. Focus on business events that other parts of the system need to know about.

## Keep Events Immutable

Events are immutable once published. They cannot be changed, updated, or deleted. This immutability is fundamental to event-driven architecture—it enables replay, audit trails, and eventual consistency. If event data is incorrect, publish a new correcting event rather than modifying the original.

Immutable events enable event sourcing. Systems can replay events to reconstruct state at any point in time. If events were mutable, replay would be impossible—the same events might produce different results. Immutability ensures determinism.

Schema evolution must maintain immutability. Old events remain unchanged. New event versions are published alongside old versions. Systems upcast old events to new formats during replay. This preserves history while enabling evolution.

Design event schemas with immutability in mind. Use immutable data structures. In Kotlin, use data classes with `val` properties. In Java, use final fields and immutable collections. Avoid mutable references that could be modified after event creation.

## Design for Idempotent Consumers

Every consumer must handle receiving the same event multiple times correctly. At-least-once delivery guarantees mean consumers will receive duplicates. Exactly-once guarantees are difficult to achieve end-to-end. Idempotent consumers are essential for reliable event-driven systems.

Idempotency means that processing the same event multiple times has the same effect as processing it once. If an `OrderPlaced` event is processed twice, the order should be created once, not twice. Use idempotency keys, database constraints, or deduplication logic to ensure idempotency.

Idempotency keys uniquely identify events. Consumers track processed idempotency keys. If an event with a known key arrives, it's ignored. Store idempotency keys in a database with unique constraints. Use event IDs as idempotency keys if they're guaranteed unique.

Database constraints provide natural idempotency. If creating an order requires a unique order ID, processing the same `OrderPlaced` event twice will fail on the second attempt due to the constraint. This provides idempotency without explicit tracking.

Deduplication logic compares incoming events to recently processed events. If a duplicate is detected, it's ignored. This works for short time windows but doesn't scale to long retention periods. Use idempotency keys or database constraints for long-term deduplication.

Test idempotency thoroughly. Publish the same event multiple times. Verify that consumers handle duplicates correctly. Test idempotency under concurrency—multiple instances processing the same event simultaneously. Idempotency bugs are hard to detect and fix in production.

## Use Correlation IDs

Every event should carry a correlation ID for distributed tracing. Correlation IDs enable following events through multiple services. When debugging production issues, correlation IDs help trace the complete flow from initial request to final outcome.

Correlation IDs should be propagated through the entire event chain. When a service emits an event in response to another event, it should include the original correlation ID. This creates a traceable chain. Optionally include a causation ID to track the immediate predecessor event.

Generate correlation IDs at system boundaries—HTTP requests, scheduled jobs, user actions. Propagate them through all events and commands. Include them in logs, metrics, and traces. This enables correlating logs across services and understanding complete flows.

Correlation IDs are essential for debugging distributed systems. Without them, tracing events through multiple services is guesswork. With them, operators can follow complete flows and identify bottlenecks or failures. Invest in correlation ID propagation from day one.

## Prefer Choreography for Simple Flows

Choreography suits simple flows with 2-3 steps and clear reactions. If services can react independently without coordination, choreography is simpler than orchestration. Each service remains focused on its domain. The system stays loosely coupled.

In a simple order flow, the Order service emits `OrderPlaced`. The Inventory service reacts by reserving inventory. The Payment service reacts by processing payment. The Fulfillment service reacts when both inventory and payment are complete. No central coordinator is needed. Each service knows its role.

Choreography's simplicity comes from independent reactions. Services don't need to know about the complete process. They react to events they care about. This reduces coupling and improves maintainability. Simple flows benefit from this simplicity.

However, choreography becomes difficult as flows grow complex. If a process involves 5+ steps with error handling, compensating transactions, and conditional logic, orchestration provides structure. Recognize when a flow has outgrown choreography and introduce a saga.

## Use Orchestration for Complex Flows

Orchestration suits complex multi-step processes with error handling, compensating transactions, and conditional logic. If a process requires coordination, use a saga. The explicit coordination is worth the coupling cost for complex flows.

Financial transactions benefit from orchestration. A payment process might involve reserving funds, validating accounts, processing payment, updating balances, and sending notifications. If any step fails, previous steps must be compensated. A saga coordinates this flow and handles errors.

Long-running processes benefit from orchestration. An order fulfillment process might take days, involving multiple services and external systems. A saga maintains process state and coordinates steps. It handles timeouts, retries, and compensation. Choreography would make this difficult to manage.

Orchestration provides visibility. The saga is the single source of truth for process state. Developers can read the saga code to understand the complete flow. Operators can inspect saga state to debug issues. This visibility is valuable for complex processes.

## Handle Poison Messages

Poison messages cause repeated processing failures. They might have invalid data, reference non-existent entities, or trigger bugs in consumers. Without proper handling, poison messages consume resources and block processing of other messages.

Dead letter queues capture poison messages after retries are exhausted. Configure retry limits—typically 3-5 retries with exponential backoff. After retries are exhausted, route messages to DLQs. This prevents infinite retries and allows investigation.

Monitor DLQ depth and alert when it grows. DLQ messages indicate systemic issues—schema mismatches, buggy consumers, or infrastructure problems. Investigate root causes. Fix issues and replay DLQ messages. Don't let DLQs accumulate silently.

Provide tooling to inspect and replay DLQ messages. Operators need to understand why messages failed. They need to replay messages after fixes. Build admin interfaces for DLQ management. This enables efficient incident response.

Design consumers to handle poison messages gracefully. Validate event data before processing. Handle missing entities gracefully. Log errors with sufficient context for debugging. Don't let poison messages crash consumers—handle errors and move to DLQ.

## Version Your Events

Event versioning enables schema evolution without breaking existing consumers. Include a version field in events from day one. Use semantic versioning—major versions for breaking changes, minor versions for backward-compatible additions, patch versions for fixes.

Schema registries manage event versions centrally. Register schemas with versions. Enforce compatibility rules—new versions must be backward compatible with previous versions. This prevents accidental breaking changes. Use schema registries for governance.

Plan for upcasting old events. When event schemas change, old events remain in the event store. Systems must upcast old events to new formats during replay. Design upcasters to handle version migration. Test upcasting thoroughly—replay old events and verify correct processing.

Version events from the start. Adding versioning later is difficult—existing events lack versions. Start with version 1.0.0. Increment versions as schemas evolve. Document version changes and migration paths. This enables safe evolution.

## Stack-Specific Guidance

### Kotlin

Use sealed classes for event hierarchies. Sealed classes enable compiler-enforced exhaustive handling. When a new event type is added, the compiler forces handlers to handle it. This prevents bugs from unhandled events.

Use data classes for event payloads. Data classes provide immutability, equality, and toString automatically. They're ideal for events. Use `val` properties to ensure immutability. Avoid mutable properties.

Use coroutines for async event processing. Kotlin coroutines provide structured concurrency for event handlers. They're more readable than callbacks and integrate well with Spring WebFlux and other reactive frameworks.

### Axon Framework

Use `@EventHandler` for projections. Projection handlers consume events and update read models. Keep projections focused and fast. Use `@DisallowReplay` for handlers that should not process replayed events—notification handlers, for example.

Use `@SagaEventHandler` for sagas. Saga handlers react to events and dispatch commands. Use association properties to correlate events to saga instances. Use `@EndSaga` to mark saga completion.

Use tracking processors for projections that need exactly-once processing. Tracking processors track processing progress and enable replay. Use subscribing processors for handlers that don't need replay—notification handlers, for example.

Configure idempotent producers in Axon. Use `IdempotencyConfig` to prevent duplicate events. This is essential for at-least-once delivery guarantees.

### Spring Boot

Use `@EventListener` for in-process events only. Spring's `@EventListener` handles events within the same JVM. It's not for distributed events. Use it for internal event handling within a service.

Use Spring Cloud Stream for Kafka/RabbitMQ abstraction. Spring Cloud Stream provides a simple programming model for message-driven microservices. It abstracts broker-specific details and enables switching brokers.

Configure retry and DLQ handling. Spring Cloud Stream supports retry policies and dead letter topics. Configure retries with exponential backoff. Route failed messages to DLQs after retries are exhausted.

Use Spring's transaction management for event handlers. If event handlers update databases, use `@Transactional` to ensure atomicity. However, be careful with long-running transactions—they can cause consumer lag.

### Kafka

Configure idempotent producers with `enable.idempotence=true`. Idempotent producers prevent duplicate events from producer retries. This is essential for at-least-once delivery guarantees.

Use consumer group IDs for load balancing. Multiple consumers with the same group ID share partitions, distributing load. Use unique group IDs for fan-out—each group receives all events independently.

Set appropriate partition counts for parallelism. More partitions enable more parallel consumers. However, too many partitions can cause overhead. Start with a small number and increase as needed. Consider partition keys to ensure related events maintain order.

Configure retention policies based on business needs. Retain events long enough for replay and analytics, but not so long that storage costs become prohibitive. Use log compaction for keyed topics to retain only the latest value per key.

Monitor consumer lag. Consumer lag indicates how far behind consumers are from producers. Set alerts when lag exceeds thresholds. Scale consumers horizontally to reduce lag. Consumer lag that grows unbounded indicates consumers can't keep up.

Use exactly-once semantics sparingly. Exactly-once reduces throughput and increases latency. Use it only when duplicates are unacceptable—financial transactions, for example. Most systems can use at-least-once with idempotent consumers.
