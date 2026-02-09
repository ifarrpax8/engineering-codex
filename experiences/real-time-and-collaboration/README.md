---
title: Real-Time & Collaboration
type: experience
last_updated: 2026-02-09
---

# Real-Time & Collaboration

Live updates, presence indicators, collaborative editing, and WebSocket UX patterns for real-time user experiences.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Real-time updates** transform user experiences by eliminating stale data and enabling true collaboration, but not everything needs to be real-time—identify what benefits from live updates vs. what can poll
- **WebSocket architecture** with Spring WebSocket/STOMP provides bidirectional communication, while SSE offers simpler one-way server push; always implement graceful degradation to polling
- **Presence systems** require careful timeout handling to avoid showing stale "online" status; use Redis-backed heartbeats with automatic cleanup
- **Conflict resolution** is critical for collaborative editing—choose between last-write-wins, operational transforms, or CRDTs based on your use case complexity
- **Connection management** must handle reconnection with exponential backoff, show connection status to users, and manage multiple tabs efficiently

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- WebSocket patterns, presence systems, conflict resolution, scalability
- [Testing](testing.md) -- WebSocket testing, presence testing, conflict resolution, connection resilience
- [Best Practices](best-practices.md) -- Language-agnostic principles, stack-specific guidance
- [Gotchas](gotchas.md) -- Common pitfalls and how to avoid them
- [Options](options.md) -- Decision matrix for transport, presence, conflict resolution

## Related Facets

- [Event-Driven Architecture](../facets/event-driven-architecture/) -- Real-time systems are inherently event-driven
- [State Management](../facets/state-management/) -- Merging real-time updates into application state
- [Performance](../facets/performance/) -- WebSocket connection limits, message throughput, latency
- [Observability](../facets/observability/) -- Monitoring WebSocket connections, message rates, presence accuracy

## Related Experiences

- [Notifications](../notifications/) -- Real-time notification delivery patterns
- [Tables and Data Grids](../tables-and-data-grids/) -- Live data updates in tabular views
- [Loading and Perceived Performance](../loading-and-perceived-performance/) -- Optimistic updates and real-time feedback
