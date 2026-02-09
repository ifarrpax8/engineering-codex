---
title: Event-Driven Architecture - Testing
type: perspective
facet: event-driven-architecture
last_updated: 2026-02-09
---

# Testing: Event-Driven Systems

## Testing Event Handlers

Event handlers are the core of event-driven systems. They react to events and produce side effects—updating state, dispatching commands, or triggering other events. Testing event handlers requires verifying that given an event, the handler produces the correct side effects.

Unit test each handler in isolation. Mock dependencies. Given a specific event, verify the handler's behavior. Does it update the correct state? Does it dispatch the expected commands? Does it emit the correct events? Keep handlers focused and testable. Complex handlers with multiple responsibilities are harder to test.

For Axon projection handlers, test that events update read models correctly. Given an `OrderPlaced` event, verify that the projection updates the order read model with the correct data. Test idempotency by processing the same event twice and verifying no duplicate side effects. Test schema evolution by processing old event versions and verifying backward compatibility.

For integration event handlers, test that events trigger the correct external actions. Given a `PaymentProcessed` event, verify that the handler calls the correct external API or emits the correct integration event. Mock external dependencies. Verify error handling—what happens when external calls fail?

Handler tests should be fast and isolated. They don't require message brokers or databases. They test business logic, not infrastructure. Use mocks for dependencies. Verify behavior through assertions on state changes, command dispatches, or event emissions.

## Testing Aggregates with Axon

Axon aggregates are event-sourced entities that handle commands and emit events. Testing aggregates requires verifying that given commands and prior events, aggregates emit the correct events. Axon provides `AggregateTestFixture` for given-when-then style testing.

The test fixture enables testing aggregates without Spring context. Create a fixture for your aggregate type. Use `given(events)` to set up prior state. Use `when(command)` to execute a command. Use `expectEvents(resultEvents)` to verify emitted events. This provides fast, isolated aggregate testing.

Test command validation. Given invalid commands, verify that aggregates reject them with appropriate exceptions. Test business rules. Given commands that violate business rules, verify rejection. Test state transitions. Given prior events, verify that commands produce the correct new events.

Test event sourcing by replaying events. Given a sequence of events, verify that the aggregate reconstructs the correct state. This verifies that event handlers correctly update aggregate state. Test that the same events always produce the same state—determinism is essential for event sourcing.

Test idempotency for commands. If the same command is executed twice, verify that the aggregate handles it correctly. Some commands are naturally idempotent. Others require explicit idempotency handling. Test edge cases—commands on aggregates in terminal states, commands with invalid parameters, commands that depend on prior events.

## Testing Sagas

Sagas orchestrate multi-step processes across multiple services. Testing sagas requires verifying that given events, sagas dispatch the correct commands and transition through correct states. Axon provides `SagaTestFixture` for testing saga flows.

The saga test fixture enables testing sagas without Spring context or message brokers. Create a fixture for your saga type. Use `given(events)` to set up saga state. Use `whenPublishing(event)` to simulate an event. Use `expectDispatchedCommands(commands)` to verify command dispatch. Use `expectActive()` or `expectNoMoreCommands()` to verify saga state.

Test saga initiation. Given an initiating event, verify that the saga starts and dispatches the first command. Test saga progression. Given intermediate events, verify that the saga dispatches the correct next commands. Test saga completion. Given completion events, verify that the saga ends and dispatches final commands.

Test compensating transactions. Given failure events, verify that the saga dispatches compensating commands. Test error handling. Given unexpected events or errors, verify that the saga handles them correctly. Test saga association. Verify that events are correctly associated with saga instances using association properties.

Test saga timeouts. Sagas can have timeouts that trigger compensation. Test that timeouts are handled correctly. Test concurrent events. Verify that sagas handle events that arrive out of order or concurrently. Test saga state persistence. Verify that saga state is correctly persisted and restored.

## Integration Testing with Testcontainers

Integration tests verify that events flow correctly through message brokers. They test serialization, deserialization, routing, and delivery. Testcontainers enables spinning up Kafka or RabbitMQ in Docker containers for integration testing.

For Kafka integration tests, start a Kafka container. Create topics. Publish events using Kafka producers. Consume events using Kafka consumers. Verify that events are correctly serialized, routed, and delivered. Test consumer groups, partitions, and offsets. Test exactly-once semantics if configured.

For RabbitMQ integration tests, start a RabbitMQ container. Create exchanges and queues. Publish events to exchanges. Consume events from queues. Verify routing based on exchange types and routing keys. Test acknowledgments, redeliveries, and dead letter queues.

Integration tests verify the actual serialization format. Events are serialized to bytes, sent over the network, and deserialized. This catches serialization bugs that unit tests miss. Test schema evolution by publishing old event versions and verifying that new consumers can process them.

Integration tests are slower than unit tests. Use them for critical paths and complex scenarios. Don't test every handler with integration tests—unit tests are sufficient for most cases. Use integration tests to verify end-to-end flows and infrastructure configuration.

## Contract Testing for Events

Event contracts define the schema and semantics of events. Contract testing verifies that producers emit events matching consumer expectations. This prevents breaking changes and enables independent evolution.

Consumer-driven contract tests verify that producers emit events matching expected schemas. Consumers define their expectations. Producers run contract tests to verify they meet expectations. This ensures backward compatibility and prevents breaking changes.

Define event contracts as schemas—JSON Schema, Avro schemas, or Protobuf schemas. Consumers publish their expected schemas. Producers verify they emit events matching these schemas. Schema registries can enforce compatibility, but contract tests provide additional verification.

Test schema evolution. Verify that new event versions maintain backward compatibility. Test that old consumers can process new events. Test that new consumers can process old events if forward compatibility is required. Contract tests catch compatibility issues before deployment.

Use contract testing tools like Pact or custom test frameworks. Define contracts as code. Run contract tests in CI/CD pipelines. Fail builds if contracts are violated. This ensures that event schemas evolve safely and independently.

## Testing Eventual Consistency

Eventual consistency means that after an event is published, read models eventually reflect the change, but not immediately. Testing eventual consistency requires verifying that after publishing an event, the read model eventually converges to the correct state.

Use polling with timeout rather than fixed waits. After publishing an event, poll the read model until it reflects the change or timeout occurs. Fixed waits are brittle—they fail under load or with slow systems. Polling adapts to actual system performance.

Awaitility library provides "eventually" assertions for Java/Kotlin. Use `await().atMost(Duration.ofSeconds(10)).until(() -> readModel.hasOrder(orderId))` to wait for eventual consistency. This makes tests more reliable and faster—they proceed as soon as consistency is achieved rather than waiting fixed times.

Test consistency windows. Verify that read models converge within acceptable timeframes. Set SLOs for consistency windows. Test that consistency windows don't grow unbounded under load. Monitor consistency windows in production.

Test consistency under failure. If a projection handler fails, verify that it eventually processes events after recovery. Test that retries eventually succeed. Test that dead letter queues handle poison messages correctly. Eventual consistency requires resilience—systems must eventually converge even after failures.

## Testing Dead Letter Queues

Dead letter queues capture messages that repeatedly fail processing. Testing DLQs requires verifying that failed messages are correctly routed to DLQs, that retry behavior works correctly, and that poison messages are handled appropriately.

Publish events that cause processing failures. Verify that messages are retried a configurable number of times. Verify that after retries are exhausted, messages are routed to DLQs. Verify that DLQ messages can be inspected and replayed.

Test retry configuration. Verify that retries happen with correct backoff strategies. Test that retries don't overwhelm systems. Test that retries eventually succeed for transient failures. Test that permanent failures are routed to DLQs without infinite retries.

Test DLQ monitoring. Verify that DLQ depth is monitored and alerts are triggered when depth exceeds thresholds. Test DLQ inspection tools. Verify that operators can view DLQ messages, understand failure reasons, and replay messages after fixes.

Test poison message handling. Poison messages cause repeated failures. Verify that poison messages are identified and routed to DLQs. Verify that poison messages don't block processing of other messages. Provide tooling to fix poison messages and replay them.

## Testing Idempotency

Idempotent consumers handle receiving the same event multiple times without incorrect side effects. Testing idempotency requires publishing the same event multiple times and verifying that consumers handle it correctly.

Publish the same event twice with the same event ID. Verify that the consumer processes it once and ignores the duplicate. Verify that no duplicate side effects occur—no duplicate database records, no duplicate external API calls, no duplicate notifications.

Test idempotency keys. If events include idempotency keys, verify that consumers use them correctly. Test that different events with the same idempotency key are handled correctly. Test that idempotency keys are correctly propagated through event chains.

Test idempotency under concurrency. Publish the same event concurrently from multiple producers. Verify that consumers handle concurrent duplicates correctly. This tests race conditions in idempotency logic. Use database constraints or distributed locks if necessary.

Test idempotency for different event types. Some events are naturally idempotent—processing them multiple times has no effect. Other events require explicit idempotency handling. Test both cases. Verify that idempotency logic doesn't break normal processing.

## End-to-End Event Flow Testing

End-to-end tests verify complete event flows from command to event to projection to consumer reaction. They test the entire system working together. Use `@SpringBootTest` with embedded Axon Server or Testcontainers for end-to-end testing.

Publish a command to an aggregate. Verify that the aggregate emits the expected events. Verify that projections consume events and update read models. Verify that downstream consumers react to events correctly. This tests the complete flow without mocking.

Test complete business processes. For order fulfillment, verify that placing an order emits events, updates projections, triggers inventory reservation, processes payment, and fulfills the order. Test error scenarios—what happens if payment fails? What happens if inventory is unavailable?

End-to-end tests are slow and require full infrastructure. Use them sparingly for critical paths. Don't test every scenario end-to-end—unit and integration tests cover most cases. Use end-to-end tests to verify that components work together correctly.

Test distributed tracing. Verify that correlation IDs propagate through the entire event flow. Verify that traces can be followed across services. This enables debugging production issues. End-to-end tests verify that observability works correctly.

Test performance under load. Publish many commands and verify that events are processed correctly. Verify that consumer lag doesn't grow unbounded. Verify that systems handle peak loads. End-to-end tests can reveal performance issues that unit tests miss.

End-to-end tests provide confidence that systems work correctly together. They catch integration issues that unit tests miss. However, they're expensive to maintain and run. Balance end-to-end test coverage with unit and integration test coverage. Use end-to-end tests for critical paths and complex scenarios.
