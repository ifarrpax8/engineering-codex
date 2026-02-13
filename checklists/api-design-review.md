# API Design Review Checklist

Use this checklist before publishing a new API or making a breaking change to an existing one. Cross-reference with the [API Design facet](../facets/api-design/) for deeper guidance.

## Naming & Structure

- [ ] **Resource-oriented URLs** (nouns, not verbs: /orders not /getOrders) → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Consistent naming conventions** (kebab-case URLs, camelCase JSON fields) → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Pluralized collection endpoints** (/users, /orders) → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Logical nesting** (max 2 levels: /users/{id}/orders, not deeper) → [api-design/gotchas.md](../facets/api-design/gotchas.md)
- [ ] **API versioning strategy in place** (URL path, header, or query param) → [api-design/options.md](../facets/api-design/options.md)

## Request & Response

- [ ] **HTTP methods used correctly** (GET reads, POST creates, PUT replaces, PATCH updates, DELETE removes) → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **HTTP status codes are accurate** (201 for create, 204 for no content, 404 vs 400 vs 422) → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Error responses follow RFC 9457 Problem Details format** (or organisational standard) → [error-handling/architecture.md](../facets/error-handling/architecture.md)
- [ ] **Pagination implemented for list endpoints** (never return unbounded collections) → [api-design/architecture.md](../facets/api-design/architecture.md)
- [ ] **Filtering, sorting, and field selection use consistent query parameter conventions** → [api-design/architecture.md](../facets/api-design/architecture.md)
- [ ] **Response envelope is consistent across all endpoints** → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Related entities returned as nested objects** (not bare IDs) where consumers need display data → [api-design/best-practices.md](../facets/api-design/best-practices.md#response-object-depth)

## Idempotency & Reliability

- [ ] **Idempotency-Key header supported on POST** (and other mutation endpoints if organisational standard requires it) → [api-design/best-practices.md](../facets/api-design/best-practices.md#idempotency)
- [ ] **Duplicate requests return cached response** (same key + same payload = same result) → [api-design/best-practices.md](../facets/api-design/best-practices.md#idempotency)
- [ ] **Concurrent requests with same key handled** (409 Conflict with Retry-After) → [api-design/best-practices.md](../facets/api-design/best-practices.md#idempotency)

## Audit & Tracing

- [ ] **Audit fields use consistent format** (structured action-based or flat — pick one and apply across all endpoints) → [api-design/best-practices.md](../facets/api-design/best-practices.md#audit-action-fields)
- [ ] **W3C Trace Context supported** (`traceparent`/`tracestate` headers propagated) → [api-design/architecture.md](../facets/api-design/architecture.md#distributed-tracing-headers)
- [ ] **Trace ID included in error responses** for debugging correlation → [error-handling/best-practices.md](../facets/error-handling/best-practices.md)

## Security

- [ ] **Authentication required on all non-public endpoints** → [authentication/best-practices.md](../facets/authentication/best-practices.md)
- [ ] **Authorization enforced** (user can only access their own resources) → [authentication/architecture.md](../facets/authentication/architecture.md)
- [ ] **Rate limiting configured** → [security/architecture.md](../facets/security/architecture.md)
- [ ] **Input validated and sanitized server-side** → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **No sensitive data in URLs** (tokens, passwords, PII) → [security/gotchas.md](../facets/security/gotchas.md)

## Contract & Documentation

- [ ] **API spec exists and matches implementation** (OpenAPI, TypeSpec, or equivalent) → [api-design/best-practices.md](../facets/api-design/best-practices.md#api-first-design)
- [ ] **Spec designed before implementation** (API-first workflow) → [api-design/best-practices.md](../facets/api-design/best-practices.md#api-first-design)
- [ ] **Breaking changes documented and versioned** → [api-design/options.md](../facets/api-design/options.md)
- [ ] **Example requests and responses provided** → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Error catalog documented** (all possible error codes and meanings) → [error-handling/best-practices.md](../facets/error-handling/best-practices.md)

## Performance

- [ ] **Pagination default and max page size set** (e.g., default 20, max 100) → [api-design/architecture.md](../facets/api-design/architecture.md)
- [ ] **No N+1 queries behind list endpoints** → [performance/gotchas.md](../facets/performance/gotchas.md)
- [ ] **Expensive operations are async** (return 202 Accepted, poll or notify) → [api-design/architecture.md](../facets/api-design/architecture.md)
- [ ] **Appropriate caching headers** (ETag, Cache-Control) → [performance/best-practices.md](../facets/performance/best-practices.md)

## Backwards Compatibility

- [ ] **New fields are additive** (don't remove or rename existing fields) → [api-design/gotchas.md](../facets/api-design/gotchas.md)
- [ ] **Deprecated fields marked with sunset timeline** → [api-design/best-practices.md](../facets/api-design/best-practices.md)
- [ ] **Client doesn't break if server adds new fields** (open/closed principle) → [api-design/gotchas.md](../facets/api-design/gotchas.md)
