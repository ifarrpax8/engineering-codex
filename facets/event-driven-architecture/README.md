---
title: Event-Driven Architecture
type: facet
last_updated: 2026-02-09
tags: [kafka, rabbitmq, axon, event-sourcing, cqrs, saga, messaging, async, eventual-consistency]
---

# Event-Driven Architecture

Messaging, event sourcing, CQRS, choreography vs orchestration.

## TL;DR

- **Default choice**: Hybrid communication pattern—synchronous for queries and request-response, asynchronous messaging for commands and state changes
- **Key principle**: Use the right pattern for each use case; CQRS naturally supports hybrid with async writes and sync reads
- **Watch out for**: Eventual consistency issues when reads need immediate consistency, debugging complexity in distributed event flows
- **Start here**: [Options](options.md) — contains the default recommendation and decision matrix for communication patterns, message brokers, and process coordination

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [Backend Architecture](../backend-architecture/) -- CQRS and service decomposition patterns
- [Data Persistence](../data-persistence/) -- Event sourcing, projections, read models
- [API Design](../api-design/) -- Async APIs, webhooks, event-driven API patterns
- [Error Handling](../error-handling/) -- Dead letter queues, retry strategies, poison messages
- [Observability](../observability/) -- Distributed tracing across event flows
- [Security](../security/) -- Event payload encryption, topic authorization

## Related Experiences

- [Real-Time & Collaboration](../../experiences/real-time-and-collaboration/) -- Live updates from event streams
- [Notifications](../../experiences/notifications/) -- Event-triggered notifications
