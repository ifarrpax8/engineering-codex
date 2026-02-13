---
title: Event-Driven Architecture - Options
type: perspective
facet: event-driven-architecture
recommendation_type: decision-matrix
last_updated: 2026-02-09
---

# Options: Event-Driven Architecture Decisions

## Contents

- [Communication Pattern Options](#communication-pattern-options)
  - [Synchronous (REST/gRPC)](#synchronous-restgrpc)
  - [Asynchronous Messaging (Events)](#asynchronous-messaging-events)
  - [Hybrid](#hybrid)
- [Message Broker Options](#message-broker-options)
  - [Apache Kafka](#apache-kafka)
  - [RabbitMQ](#rabbitmq)
  - [In-Process (Spring Events / Axon without External Broker)](#in-process-spring-events--axon-without-external-broker)
- [Process Coordination Options](#process-coordination-options)
  - [Choreography](#choreography)
  - [Orchestration (Saga)](#orchestration-saga)
  - [Hybrid](#hybrid)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Communication Pattern Options

### Synchronous (REST/gRPC)

Synchronous communication uses direct request-response patterns between services. Clients send requests and wait for responses. Services call each other directly over HTTP or gRPC. This is the traditional approach for service-to-service communication.

**Strengths:**
- Simple mental model—requests and responses are immediate and predictable
- Easy to debug—requests and responses are visible in logs and traces
- Immediate feedback—errors are returned synchronously, enabling retry logic
- Well-understood patterns—REST and gRPC are mature and widely adopted
- Tooling support—extensive tooling for HTTP/gRPC debugging and monitoring

**Weaknesses:**
- Tight coupling—services must know about each other and be available simultaneously
- Cascading failures—slow or failing services cause cascading failures across call chains
- Blocking operations—services wait for responses, reducing throughput and increasing latency
- Coordinated deployments—changing APIs requires coordinating deployments across services
- Limited scalability—synchronous calls don't scale as well as asynchronous messaging

**Best For:**
- Request-response scenarios where immediate responses are required
- Queries that need current state immediately
- Operations where the caller needs to know success or failure immediately
- Simple service interactions with low coupling requirements
- Systems where simplicity is more important than scalability

**Avoid When:**
- High-throughput scenarios where blocking reduces performance
- Long-running operations where waiting for responses is impractical
- Scenarios where temporal decoupling provides value
- Systems with high coupling that would benefit from decoupling
- Operations where eventual consistency is acceptable

### Asynchronous Messaging (Events)

Asynchronous messaging uses message brokers to decouple producers and consumers. Producers emit events without waiting for consumers. Consumers process events independently. This enables temporal decoupling and improved scalability.

**Strengths:**
- Temporal decoupling—producers don't wait for consumers, improving latency and resilience
- Loose coupling—producers and consumers don't know about each other
- Scalability—message brokers enable horizontal scaling of producers and consumers
- Resilience—slow or failing consumers don't block producers
- Independent evolution—producers and consumers can evolve independently with proper schema management

**Weaknesses:**
- Complexity—asynchronous systems are harder to understand and debug
- Eventual consistency—read models may not reflect writes immediately
- Message loss or duplication—requires careful design to handle delivery guarantees
- Infrastructure overhead—message brokers require additional infrastructure and operations
- Debugging difficulty—tracing events through multiple services requires proper tooling

**Best For:**
- State changes and notifications where immediate responses aren't required
- High-throughput scenarios where blocking reduces performance
- Long-running processes that benefit from temporal decoupling
- Systems with multiple consumers that need to react to the same events
- Scenarios where eventual consistency is acceptable

**Avoid When:**
- Request-response scenarios where immediate responses are required
- Operations where synchronous errors are needed for retry logic
- Simple systems where complexity isn't justified
- Scenarios where message broker infrastructure overhead isn't justified
- Operations that require immediate consistency

### Hybrid

Hybrid approaches combine synchronous and asynchronous patterns. Use synchronous communication for queries and request-response scenarios. Use asynchronous messaging for commands and state changes. This balances simplicity with scalability.

**Strengths:**
- Balanced approach—uses the right pattern for each use case
- Query performance—synchronous queries provide immediate responses
- Command scalability—asynchronous commands enable high throughput
- Reduced complexity—simpler than pure asynchronous for many scenarios
- Flexibility—can evolve toward more asynchrony as needed

**Weaknesses:**
- Pattern complexity—teams must understand when to use which pattern
- Inconsistent patterns—mixing patterns can confuse developers
- Still requires messaging infrastructure—doesn't eliminate infrastructure overhead
- Decision overhead—requires deciding which pattern to use for each scenario

**Best For:**
- Most microservices architectures—queries are synchronous, commands are asynchronous
- Systems transitioning from synchronous to asynchronous
- Scenarios where both patterns provide value
- Systems where CQRS separates reads and writes naturally

**Avoid When:**
- Pure event-sourced systems where everything is asynchronous
- Simple systems where one pattern suffices
- Systems where pattern consistency is more important than optimization

## Message Broker Options

### Apache Kafka

Apache Kafka is a distributed event log designed for high-throughput event streaming. Events are written to topics, which are partitioned for parallelism. Consumers read from topics via consumer groups. Kafka provides long-term retention and replay capabilities.

**Strengths:**
- High throughput—designed for millions of events per second
- Long-term retention—events can be retained for days, weeks, or indefinitely
- Replay capability—consumers can reprocess historical events
- Horizontal scaling—partitions enable parallel processing
- Exactly-once semantics—with proper configuration, Kafka provides exactly-once delivery

**Weaknesses:**
- Complexity—Kafka's distributed architecture requires operational expertise
- Higher latency—batching and log-based architecture increase latency for small messages
- Infrastructure overhead—Kafka clusters require significant resources
- Learning curve—teams must understand partitions, consumer groups, and offsets
- Overkill for simple scenarios—Kafka's features aren't needed for all use cases

**When to Use:**
- Event streaming scenarios where events need to be retained for replay
- High-throughput systems that need to process millions of events per second
- Systems that need fan-out to multiple consumers via consumer groups
- Analytics scenarios that benefit from replaying historical events
- Systems that need exactly-once semantics for critical events

**When to Avoid:**
- Simple task queues where RabbitMQ's simplicity is preferable
- Low-latency scenarios where immediate delivery is critical
- Systems where event retention and replay aren't needed
- Small systems where Kafka's infrastructure overhead isn't justified

### RabbitMQ

RabbitMQ is a traditional message broker with flexible routing. Producers publish to exchanges, which route messages to queues based on routing rules. Consumers consume from queues. RabbitMQ provides fine-grained control over message routing and delivery.

**Strengths:**
- Flexible routing—exchanges support multiple routing patterns (direct, topic, fanout, headers)
- Lower latency—messages are delivered immediately rather than batched
- Simpler mental model—exchanges and queues are easier to understand than Kafka's log model
- Fine-grained control—acknowledgments, dead letter exchanges, message TTL
- Mature and stable—RabbitMQ is well-established with extensive tooling

**Weaknesses:**
- Lower throughput—not designed for the same scale as Kafka
- No built-in replay—messages are deleted after consumption
- Less suitable for event streaming—designed for messaging rather than event streaming
- Single broker limitations—clustering is more complex than Kafka's distributed design
- No exactly-once semantics—requires application-level idempotency

**When to Use:**
- Task distribution scenarios where work needs to be distributed to multiple workers
- Flexible routing requirements where exchanges provide value
- Lower-latency scenarios where immediate delivery is important
- Point-to-point messaging where each message should be processed once
- Systems where RabbitMQ's simplicity is preferable to Kafka's complexity

**When to Avoid:**
- Event streaming scenarios where event retention and replay are needed
- High-throughput scenarios where Kafka's partitioning provides better performance
- Systems that need fan-out to multiple consumers via consumer groups
- Analytics scenarios that benefit from replaying historical events
- Systems where exactly-once semantics are required

### In-Process (Spring Events / Axon without External Broker)

In-process event handling uses framework mechanisms like Spring's `@EventListener` or Axon's in-memory event bus. Events are handled within the same JVM without external message brokers. This simplifies architecture for monoliths and moduliths.

**Strengths:**
- No infrastructure overhead—no message brokers to operate and maintain
- Lower latency—in-process handling is faster than network calls
- Simpler deployment—no additional infrastructure components
- Easier testing—no need for Testcontainers or embedded brokers
- Good for monoliths—enables event-driven patterns within monolithic applications

**Weaknesses:**
- No persistence—events are lost if the process crashes
- No replay—can't reprocess historical events
- Limited scalability—can't scale producers and consumers independently
- No cross-service communication—only works within a single process
- Migration complexity—moving to distributed events requires significant changes

**When to Use:**
- Monolithic applications where in-process events provide sufficient decoupling
- Modulith architectures where modules communicate via events within the same process
- Development and testing scenarios where infrastructure overhead isn't justified
- Simple scenarios where distributed messaging isn't needed
- Systems that can migrate to distributed events later as needed

**When to Avoid:**
- Microservices architectures where services need to communicate across process boundaries
- Systems that need event persistence and replay
- High-availability scenarios where process crashes would lose events
- Systems that need to scale producers and consumers independently
- Scenarios where eventual consistency across services is required

## Process Coordination Options

### Choreography

Choreography distributes process logic across participating services. Each service reacts to events independently. There's no central coordinator. Services know their role and react accordingly. This creates loose coupling and simple services.

**Strengths:**
- Loose coupling—services don't depend on a central orchestrator
- Simple services—each service focuses on its domain
- Independent evolution—services can be developed and deployed independently
- Resilience—if one service fails, others continue operating
- Natural fit for event-driven architecture—events flow naturally between services

**Weaknesses:**
- Hard to understand overall flows—no single place to see the complete process
- Difficult to debug—requires tracing events across multiple services
- No single view of process state—each service knows only its part
- Limited error handling—compensating transactions are difficult to coordinate
- Becomes complex as processes grow—hard to manage multi-step processes

**When to Use:**
- Simple flows with 2-3 steps and clear independent reactions
- Scenarios where services can react independently without coordination
- Systems where loose coupling is more important than process visibility
- Processes that are mostly linear with independent reactions
- Scenarios where the simplicity of choreography outweighs its limitations

**When to Avoid:**
- Complex multi-step processes with error handling and compensating transactions
- Scenarios that require coordination between multiple services
- Processes where process visibility is critical for debugging and operations
- Long-running processes that need state management
- Scenarios where error handling and compensation are complex

### Orchestration (Saga)

Orchestration centralizes process logic in a coordinator—a saga. The saga knows the complete process flow. It sends commands to participants and reacts to their events. The saga decides the next step based on current state and received events.

**Strengths:**
- Clear process visibility—the saga is the single source of truth for process state
- Easier error handling—compensating transactions are centralized in the saga
- Better debugging—inspect saga state to see where the process is stuck
- Handles complex flows—sagas manage multi-step processes with conditional logic
- Explicit coordination—coordination logic is explicit and manageable

**Weaknesses:**
- Orchestrator as single point of logic—the saga becomes a critical component
- Some coupling—the saga must know about all participants
- Can become complex—complex processes create complex sagas
- Centralized logic—process logic is centralized rather than distributed
- Requires saga framework—needs Axon or similar framework support

**When to Use:**
- Complex multi-step processes with 5+ steps and conditional logic
- Scenarios that require error handling and compensating transactions
- Long-running processes that need state management
- Financial transactions where compensation is critical
- Processes where process visibility is important for debugging and operations

**When to Avoid:**
- Simple flows where choreography is simpler
- Scenarios where services can react independently without coordination
- Systems where loose coupling is more important than process visibility
- Processes that are mostly linear with independent reactions
- Scenarios where the complexity of orchestration isn't justified

### Hybrid

Hybrid approaches use choreography for simple flows and orchestration for complex flows. Simple 2-3 step processes use choreography. Complex multi-step processes use sagas. This balances simplicity with structure.

**Strengths:**
- Balanced approach—uses the right pattern for each process
- Simplicity for simple flows—choreography keeps simple flows simple
- Structure for complex flows—sagas provide structure for complex processes
- Flexibility—can evolve processes from choreography to orchestration as needed
- Recognizes that not all processes are the same

**Weaknesses:**
- Pattern complexity—teams must understand when to use which pattern
- Inconsistent patterns—mixing patterns can confuse developers
- Decision overhead—requires deciding which pattern to use for each process
- Requires both patterns—teams must understand choreography and orchestration

**When to Use:**
- Systems with both simple and complex processes
- Scenarios where different processes benefit from different patterns
- Systems transitioning from choreography to orchestration
- Organizations that can manage pattern complexity

**When to Avoid:**
- Systems where all processes are similar in complexity
- Scenarios where pattern consistency is more important than optimization
- Teams that struggle with pattern decisions
- Systems where one pattern suffices for all processes

## Evaluation Criteria

| Criteria | Weight | Synchronous | Async Messaging | Hybrid |
|----------|--------|-------------|-----------------|--------|
| **Decoupling** | High | Low (tight coupling) | High (loose coupling) | Medium (balanced) |
| **Reliability** | High | Medium (cascading failures) | High (resilient) | High (resilient) |
| **Complexity** | Medium | Low (simple) | High (complex) | Medium (moderate) |
| **Debuggability** | Medium | High (easy to debug) | Low (hard to debug) | Medium (moderate) |
| **Performance** | High | Medium (blocking) | High (non-blocking) | High (optimized) |

**Weighted Scoring:**
- Synchronous: Suitable for simple systems where coupling and complexity are acceptable
- Async Messaging: Suitable for scalable systems where decoupling and performance matter
- Hybrid: Recommended default—balances benefits while managing complexity

## Recommendation Guidance

### Default Recommendation: Hybrid Communication Pattern

Use synchronous communication for queries and request-response scenarios. Use asynchronous messaging for commands and state changes. This balances simplicity with scalability. Most microservices architectures benefit from this hybrid approach.

CQRS naturally supports this hybrid pattern. Write models use asynchronous events. Read models use synchronous queries. This separation provides both scalability and immediate query responses.

### Message Broker Selection

**Choose Kafka when:**
- Event streaming and replay are required
- High throughput (millions of events per second) is needed
- Fan-out to multiple consumers is required
- Analytics benefit from replaying historical events

**Choose RabbitMQ when:**
- Task distribution and work queues are the primary use case
- Flexible routing based on patterns is needed
- Lower latency for small messages is important
- Simplicity is preferable to Kafka's complexity

**Choose In-Process when:**
- Working within a monolith or modulith
- No cross-service communication is needed
- Infrastructure overhead isn't justified
- Can migrate to distributed events later

### Process Coordination Selection

**Choose Choreography when:**
- Processes are simple with 2-3 steps
- Services can react independently
- Loose coupling is more important than visibility
- Process is mostly linear

**Choose Orchestration when:**
- Processes are complex with 5+ steps
- Error handling and compensation are required
- Process visibility is critical
- Long-running processes need state management

**Choose Hybrid when:**
- Systems have both simple and complex processes
- Different processes benefit from different patterns
- Teams can manage pattern complexity

## Synergies

### CQRS and Event-Driven Architecture

If using CQRS (from backend-architecture), asynchronous events are essential for projection updates. Write models emit domain events. Projection handlers consume events to update read models. This creates a natural event-driven flow. CQRS and event-driven architecture are synergistic.

### Microservices and Event-Driven Architecture

If using microservices, asynchronous messaging reduces runtime coupling between services. Services communicate via events rather than direct API calls. This improves resilience and enables independent evolution. Microservices and event-driven architecture complement each other.

### Monolith/Modulith and In-Process Events

If using a monolith or modulith, in-process events (Spring `@EventListener`) may suffice initially. Modules communicate via events within the same process. This provides decoupling without infrastructure overhead. Axon abstracts the transition to distributed events when needed.

### Event Sourcing and Event-Driven Architecture

If using event sourcing (from data-persistence), events are already the source of truth. Extend domain events to integration events. The same event stream that drives event sourcing also drives integration with other systems. Event sourcing and event-driven architecture are naturally aligned.

## Evolution Triggers

### From Synchronous to Asynchronous

**Trigger:** Synchronous call chains creating cascading failures. Services calling each other synchronously create tight coupling and cascading failures. Slow or failing services cause failures across call chains.

**Action:** Introduce asynchronous messaging for state changes. Keep synchronous communication for queries. This reduces coupling and improves resilience while maintaining query performance.

### From In-Process to Distributed Events

**Trigger:** Need for cross-service communication or independent scaling. Monoliths that need to communicate with external services or scale components independently benefit from distributed events.

**Action:** Migrate from Spring `@EventListener` to Kafka or RabbitMQ. Use Axon to abstract the transition. The same event handlers can work with in-process or distributed events.

### From Choreography to Orchestration

**Trigger:** Complex multi-step processes with error handling. Simple choreographed flows that grow complex with error handling, compensating transactions, and conditional logic benefit from orchestration.

**Action:** Introduce sagas for complex processes. Keep choreography for simple flows. Use hybrid approach—choreography for simple, orchestration for complex.

### Introducing Message Brokers

**Trigger:** Consumer processing speed varying widely or need for replay. Systems where consumers process events at different speeds or need to replay historical events benefit from dedicated message brokers.

**Action:** Introduce Kafka for event streaming and replay, or RabbitMQ for task distribution. Choose based on requirements—Kafka for streaming, RabbitMQ for tasks.

### Introducing Event Sourcing

**Trigger:** Need for replay, audit trails, or reconstructing state. Systems that need to replay events, maintain audit trails, or reconstruct state at any point in time benefit from event sourcing.

**Action:** Adopt event sourcing with Axon Framework. Use Axon Server as event store and message router. Extend domain events to integration events for cross-service communication.
