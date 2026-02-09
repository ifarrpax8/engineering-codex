---
title: Error Handling
type: facet
last_updated: 2026-02-09
tags: [exceptions, rfc-7807, problem-details, error-boundary, retry, circuit-breaker, dead-letter-queue]
---

# Error Handling

Exception strategies, error boundaries, retry patterns, user-facing errors, dead letter queues.

## TL;DR

- **Default choice**: RFC 7807 Problem Details (Spring 6+) for error responses, retry with exponential backoff for transient failures, error boundaries per feature section
- **Key principle**: Always sanitize errors—never log or expose passwords, tokens, or PII in error messages or logs
- **Watch out for**: Leaking sensitive information in error messages, not propagating correlation IDs for distributed tracing
- **Start here**: [Options](options.md) — contains the recommended error handling stack and decision matrix for error response formats and resilience patterns

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Gotchas](gotchas.md) -- Common pitfalls and traps
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

- [API Design](../api-design/) -- Error response formats, status codes
- [Observability](../observability/) -- Error tracking, alerting, log correlation
- [Event-Driven Architecture](../event-driven-architecture/) -- Dead letter queues, poison messages, retry strategies
- [Security](../security/) -- Secure error messages, not leaking internals
- [Frontend Architecture](../frontend-architecture/) -- Error boundaries, fallback UI
- [State Management](../state-management/) -- Error state in UI

## Related Experiences

- [Forms & Validation](../../experiences/forms-and-data-entry/) -- Validation error display
- [Feedback & Support](../../experiences/feedback-and-support/) -- User error reporting
- [Loading & Perceived Performance](../../experiences/loading-and-perceived-performance/) -- Error during loading states
