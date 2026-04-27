---
description: API design traps — wrong HTTP methods, missing pagination, N+1 responses, idempotency, long-running ops
globs: ["**/endpoint/**", "**/controller/**", "**/api/**", "**/routes/**", "**/handler/**", "**/*Controller.kt", "**/*Endpoint.kt", "**/*Router.ts"]
alwaysApply: false
type: "auto"
---

# API Design — Gotchas

Quick reference for the most common traps. Full detail: `engineering-codex/facets/api-design/gotchas.md`

- **POST for everything** — HTTP methods carry semantic meaning: GET is cacheable, PUT is idempotent. Using POST for all operations discards these guarantees and makes APIs harder to debug.
- **200 with error body** — Returning `{"success": false}` on HTTP 200 bypasses clients, proxies, load balancers, and monitoring tools. Use 4xx/5xx with RFC 9457 error format.
- **Filtered endpoint as search engine** — WHERE clauses can't do fuzzy matching, relevance scoring, or autocomplete. When users ask for "search" across multiple fields, reach for a dedicated search solution.
- **Exposing database structure** — A CRUD endpoint per table couples the API to the schema. Design around use cases, not tables. Any DB change should be an internal detail.
- **No pagination from day one** — Adding pagination to an existing endpoint is a breaking change. Default to a page size (20–50) from the first version.
- **Inconsistent naming/formatting** — Mixed camelCase/snake_case, inconsistent date formats, different pagination conventions per endpoint. Establish and lint conventions once; enforce them everywhere.
- **Premature versioning** — Most changes are additive and backward-compatible. Don't create `/v2/` for non-breaking additions. Add versioning only when a genuinely breaking change is required.
- **Synchronous long-running ops** — Making a client wait minutes for a report/export ties up connections and risks timeouts. Return 202 Accepted with a status polling URL instead.
- **Returning only IDs** — `partnerId: "abc"` forces N+1 calls to resolve names. Return nested objects with `id`, `name`, and key fields so consumers can render without extra requests.
- **No idempotency key on mutations** — Networks are unreliable. A timed-out POST may have succeeded. Without `Idempotency-Key`, retrying creates duplicates. Add idempotency from day one — retrofitting is hard.
- **Pagination without stable sort** — Without a unique tie-breaker field (e.g. `id`) as final sort criterion, items at page boundaries appear on multiple pages or get skipped entirely.
- **API key as authentication** — API keys identify callers but don't authenticate them securely. Keys get logged, shared, and committed. Use OAuth 2.0 or JWTs for authentication; API keys for rate limiting/identification only.
- **Partial failure in aggregation** — If a BFF/gateway calls three services and one fails, returning nothing is worse than returning partial data. Design for graceful degradation with partial responses.
- **Flat audit fields** — `createdBy: "system"` loses context. Once consumers depend on the shape, migrating to structured audit objects (actor type, id, name) is a breaking change. Model richly from the start.
