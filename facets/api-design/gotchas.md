# API Design -- Gotchas

Common pitfalls and traps that developers encounter when designing and implementing APIs. These are the things that seem reasonable at first but cause problems down the road.

## Contents

- [Using POST for Everything](#using-post-for-everything)
- [Returning 200 with an Error Body](#returning-200-with-an-error-body)
- [Using a Filtered Endpoint as a Search Engine](#using-a-filtered-endpoint-as-a-search-engine)
- [Exposing Internal Database Structure](#exposing-internal-database-structure)
- [Ignoring Pagination Until It's Too Late](#ignoring-pagination-until-its-too-late)
- [Inconsistent Naming and Formatting](#inconsistent-naming-and-formatting)
- [Over-Engineering Versioning](#over-engineering-versioning)
- [Not Handling Partial Failures in Aggregation](#not-handling-partial-failures-in-aggregation)
- [Pagination Without Stable Sorting](#pagination-without-stable-sorting)
- [Treating API Keys as Authentication](#treating-api-keys-as-authentication)
- [Synchronous Responses for Long-Running Operations](#synchronous-responses-for-long-running-operations)

## Using POST for Everything

**The trap**: Using POST for all operations because "it's safer" or "GET has URL length limits."

**Why it's wrong**: HTTP methods carry semantic meaning. GET is cacheable and safe. PUT is idempotent. Using POST for everything throws away these guarantees and makes the API harder to understand, cache, and debug.

**Exception**: There are legitimate reasons to use POST for read operations -- when the query is too complex for query parameters (e.g., a search request with a complex body). But this should be explicit and documented, not a default.

## Returning 200 with an Error Body

**The trap**: Always returning HTTP 200 and putting the error in the response body:
```json
{ "status": "error", "message": "User not found" }
```

**Why it's wrong**: HTTP status codes exist for a reason. Clients, proxies, load balancers, and monitoring tools all use status codes. A 200 with an error body bypasses all of these. Use proper status codes (404, 422, 500) with a consistent error body format (RFC 9457).

## Using a Filtered Endpoint as a Search Engine

**The trap**: Adding more and more query parameters to a paginated endpoint until it's expected to do full-text search, fuzzy matching, and relevance ranking.

**Why it's wrong**: Database WHERE clauses are not search engines. They can't do fuzzy matching, relevance scoring, or autocomplete. As the filtering gets more complex, the queries get slower and the UX gets worse. See the [Search vs Filtering](architecture.md#search-vs-filtering) section for the proper approach.

**When to escalate**: If users are asking for "search" functionality, free-text matching across multiple fields, or typo tolerance, it's time for a dedicated search solution.

## Exposing Internal Database Structure

**The trap**: Making your API a thin wrapper over your database tables. Every table gets a CRUD endpoint. The response mirrors the database schema.

**Why it's wrong**: This couples your API to your database schema. Any database change breaks the API. It also exposes implementation details (table names, column names, relationship structure) that consumers shouldn't need to know. Design APIs around use cases, not tables.

## Ignoring Pagination Until It's Too Late

**The trap**: Returning all results from a collection endpoint during development because "we only have 50 records." Then the endpoint breaks in production with 50,000 records.

**Why it's wrong**: Adding pagination to an existing API is a breaking change. Start with pagination from day one. Default to a reasonable page size (20-50) and require explicit requests for more.

## Inconsistent Naming and Formatting

**The trap**: Different endpoints use different conventions -- some use camelCase, others use snake_case. Some return dates as ISO 8601, others as Unix timestamps. Some paginate with `page`/`pageSize`, others with `offset`/`limit`.

**Why it's wrong**: Inconsistency forces consumers to handle each endpoint differently. Establish conventions once and enforce them across all endpoints. Use a linter or code review checklist.

## Over-Engineering Versioning

**The trap**: Creating `/v2/` for every minor change, or implementing complex version negotiation before you have any consumers.

**Why it's wrong**: Most changes can be backward-compatible (additive fields, new endpoints). You only need a new version when you make a genuinely breaking change. Start without versioning, add `/v1/` when you need `/v2/`.

## Not Handling Partial Failures in Aggregation

**The trap**: An API gateway or BFF (Backend for Frontend) calls three services. If one fails, the entire request fails.

**Why it's wrong**: Users would rather see partial data than no data. Design for graceful degradation: return what you can, indicate what failed, let the client decide how to handle it.

## Pagination Without Stable Sorting

**The trap**: Paginating results without a deterministic sort order. Results may appear on different pages across requests.

**Why it's wrong**: Without stable sorting (a unique tie-breaker field), items at page boundaries can appear on multiple pages or be skipped entirely. Always include a unique field (like `id`) as the final sort criterion.

## Treating API Keys as Authentication

**The trap**: Using API keys as the sole authentication mechanism.

**Why it's wrong**: API keys identify the caller but don't authenticate them securely. Keys are often logged, shared in URLs, or committed to source control. Use API keys for identification and rate limiting, but use OAuth 2.0 or JWTs for actual authentication. See [Authentication](../authentication/options.md).

## Synchronous Responses for Long-Running Operations

**The trap**: Making a client wait for a long-running operation (report generation, data export, bulk processing) in a synchronous request/response cycle.

**Why it's wrong**: Long-running requests tie up connections, risk timeouts, and provide no progress feedback. Use the async request pattern: return 202 Accepted with a status URL, let the client poll for completion.

```
POST /reports → 202 Accepted { "statusUrl": "/reports/abc/status" }
GET /reports/abc/status → 200 { "status": "processing", "progress": 45 }
GET /reports/abc/status → 200 { "status": "complete", "downloadUrl": "/reports/abc/download" }
```
