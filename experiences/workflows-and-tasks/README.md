---
title: Workflows & Tasks
type: experience
last_updated: 2026-02-09
tags: [state-machine, approval, bulk-actions, progress, long-running, undo, saga, spring-statemachine]
---

# Workflows & Tasks

Patterns for guiding users through multi-step processes, managing task completion, and handling bulk operations.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Progress visibility is critical**: Users need clear indicators of where they are in a workflow and how much remains
- **Make workflows resumable**: Save state and allow users to return later without losing progress
- **Handle partial failures gracefully**: In bulk operations, show what succeeded, what failed, and provide retry mechanisms
- **Support cancellation**: Allow users to cancel in-progress operations with appropriate confirmation
- **Prefer undo over confirmation dialogs**: Let users act quickly and provide undo rather than blocking with "are you sure?" prompts

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Implementation patterns, state management, async processing, workflow engines
- [Testing](testing.md) -- Test strategies, workflow flow testing, approval chains, bulk operations
- [Best Practices](best-practices.md) -- Language-agnostic principles and stack-specific guidance
- [Gotchas](gotchas.md) -- Common pitfalls and anti-patterns to avoid
- [Options](options.md) -- Decision matrix for workflow patterns, progress indicators, and engines

## Related Facets

- [event-driven-architecture](../../facets/event-driven-architecture/) -- Event-driven workflows, Axon sagas, async task processing
- [state-management](../../facets/state-management/) -- Workflow state machines, step state persistence
- [error-handling](../../facets/error-handling/) -- Partial failure handling, retry strategies, compensation patterns
- [api-design](../../facets/api-design/) -- Bulk operation endpoints, async task APIs, workflow state APIs

## Related Experiences

- [forms-and-data-entry](../forms-and-data-entry/) -- Multi-step form patterns, validation flows
- [tables-and-data-grids](../tables-and-data-grids/) -- Bulk selection, batch operations on tabular data
- [notifications](../notifications/) -- Task completion notifications, approval request alerts
- [loading-and-perceived-performance](../loading-and-perceived-performance/) -- Progress indicators, optimistic updates, perceived responsiveness
