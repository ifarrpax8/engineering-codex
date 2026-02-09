---
recommendation_type: decision-matrix
---

# API Design -- Options

Decision matrix for choosing API styles and pagination strategies.

## Contents

- [API Style Options](#api-style-options)
- [Pagination Options](#pagination-options)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## API Style Options

### 1. REST

**Description**: Resource-oriented architecture using HTTP methods and status codes. Models APIs around resources (nouns) with standard HTTP verbs (GET, POST, PUT, PATCH, DELETE).

**Strengths**:
- Widely understood and familiar to developers
- Excellent tooling ecosystem (OpenAPI, Swagger, Postman)
- HTTP caching works naturally (Cache-Control headers)
- Simple mental model (resources + HTTP methods)
- Works well with browsers (native fetch API)
- Stateless and scalable

**Weaknesses**:
- Can lead to over-fetching (client gets entire resource when only need one field)
- Multiple round trips for related data (N+1 problem)
- Versioning requires explicit version management
- Less flexible than GraphQL for complex queries
- No built-in real-time capabilities (requires polling or webhooks)

**Best For**:
- Public APIs and partner integrations
- Simple CRUD operations
- APIs where HTTP caching is important
- Teams familiar with REST conventions
- Microservices with clear resource boundaries
- APIs consumed by web browsers

**Avoid When**:
- You need fine-grained field selection (GraphQL is better)
- Complex nested data relationships with varying consumer needs
- Real-time subscriptions are central to the use case
- Internal high-performance service-to-service communication (gRPC is better)

### 2. GraphQL

**Description**: Query language for APIs that lets clients request exactly the data they need. Single endpoint with client-specified queries and responses.

**Strengths**:
- Eliminates over-fetching (clients request only needed fields)
- Single endpoint reduces endpoint proliferation
- Strong typing with schema validation
- Introspection enables powerful tooling (GraphQL Playground)
- Flexible queries adapt to different consumer needs
- Subscriptions for real-time updates
- Reduces versioning complexity (additive schema changes)

**Weaknesses**:
- Steeper learning curve than REST
- N+1 query problem requires careful resolver design (DataLoader)
- Caching is more complex (no HTTP caching, need custom solutions)
- Query complexity can cause performance issues (need complexity limits)
- Less familiar to many developers
- Overkill for simple CRUD APIs
- Security considerations (malicious queries can cause DoS)

**Best For**:
- Complex data relationships with multiple consumers
- Mobile apps that need minimal data transfer
- APIs where different consumers need different fields
- Rapid frontend iteration (frontend can request new fields without backend changes)
- Real-time subscriptions are needed
- Reducing API surface area (single endpoint vs many REST endpoints)

**Avoid When**:
- Simple CRUD operations (REST is simpler)
- HTTP caching is critical (REST caching is easier)
- Team lacks GraphQL expertise
- Simple data needs (clients always need same fields)
- High-performance internal service-to-service communication (gRPC is better)

### 3. gRPC

**Description**: High-performance RPC framework using Protocol Buffers for binary serialization. Supports unary, server streaming, client streaming, and bidirectional streaming.

**Strengths**:
- High performance (binary serialization, HTTP/2 multiplexing)
- Strong typing with code generation from `.proto` files
- Streaming support (server, client, bidirectional)
- Language-agnostic (generate clients in multiple languages)
- Backward compatibility built into Protocol Buffers
- Efficient for large payloads
- Built-in support for deadlines, cancellation, load balancing

**Weaknesses**:
- Limited browser support (requires gRPC-Web proxy)
- Less familiar to web developers
- Binary format is not human-readable (harder to debug)
- Requires code generation step
- Less tooling than REST (no Swagger UI equivalent)
- Not suitable for public APIs (complexity, browser limitations)

**Best For**:
- Internal service-to-service communication
- High-throughput microservices
- Streaming data (real-time updates, file uploads)
- Polyglot environments (services in different languages)
- Performance-critical internal APIs
- Long-lived connections with bidirectional communication

**Avoid When**:
- Browser clients (REST or GraphQL are better)
- Public APIs (REST/GraphQL have better DX)
- Simple CRUD (REST is simpler)
- Team lacks gRPC expertise
- Firewall constraints (some firewalls don't handle HTTP/2 well)

## Pagination Options

### 1. Offset-Based Pagination (Spring Data Pageable)

**Description**: Uses `LIMIT` and `OFFSET` with page number and page size. In Spring Boot, this is implemented via `Pageable` / `Page<T>` / `PageRequest`, which provides a standardized request and response format with zero boilerplate.

**Strengths**:
- Simple to implement and understand
- Supports jump-to-page (direct navigation to page 5)
- Easy to show "Page X of Y" to users
- Familiar to developers and users
- Spring Data Pageable handles request parsing, sorting, and response envelope automatically

**Weaknesses**:
- Breaks with concurrent writes (items shift between pages)
- Expensive for deep pages (OFFSET 10000 requires scanning 10000 rows)
- Inconsistent results (same item may appear on multiple pages)
- Performance degrades as offset increases
- Spring Data `Page<T>` response format is opinionated (may need mapping for non-Spring consumers)

**When to Use**:
- Small to medium datasets (< 10,000 records)
- User-facing pagination with page numbers
- Spring Boot APIs (Pageable is the de facto standard)
- When consistency isn't critical
- When you want rich pagination metadata without HATEOAS complexity

### 2. Cursor-Based Pagination

**Description**: Uses opaque cursor tokens for forward/backward traversal. Cursor encodes position (e.g., last seen ID, timestamp). Client requests next page with cursor.

**Strengths**:
- Consistent with concurrent writes (cursor points to specific position)
- Efficient (no OFFSET, uses indexed WHERE clause)
- Works well for large datasets
- Consistent results (no duplicate or missing items)

**Weaknesses**:
- No jump-to-page (must traverse sequentially)
- Cursor format is opaque (harder to debug)
- Requires sortable unique field
- More complex to implement than offset

**When to Use**:
- Large datasets (> 10,000 records)
- APIs with high write volume
- When consistency matters
- Infinite scroll or "load more" patterns
- APIs where performance is critical

### 3. Keyset Pagination

**Description**: Uses WHERE clause on sorted unique key. SQL: `WHERE id > 123 ORDER BY id LIMIT 20`. Cursor is just the key value.

**Strengths**:
- Database-friendly (uses index efficiently)
- Consistent with concurrent writes
- Simple cursor format (just the key value)
- Excellent performance (indexed queries)

**Weaknesses**:
- Requires sortable unique key (ID, timestamp)
- No jump-to-page
- Only works for forward pagination (backward requires different query)
- Less flexible than cursor-based (tied to specific field)

**When to Use**:
- When you have a sortable unique key (ID, created_at timestamp)
- Internal APIs where performance is critical
- High-throughput APIs
- When simple cursor format is preferred

## Evaluation Criteria

| Criteria | Weight | REST | GraphQL | gRPC |
|----------|--------|------|---------|------|
| **Developer Familiarity** | High | High | Medium | Low |
| **Tooling Ecosystem** | High | High | Medium | Medium |
| **Performance (Internal)** | High | Medium | Medium | High |
| **Browser Support** | High | High | High | Low |
| **Caching** | Medium | High | Low | Low |
| **Type Safety** | Medium | Medium | High | High |
| **Flexibility** | Medium | Low | High | Medium |
| **Real-time Support** | Low | Low (polling/webhooks) | High (subscriptions) | High (streaming) |
| **Learning Curve** | Medium | Low | Medium | Medium |
| **Versioning Complexity** | Medium | Medium | Low | Low |
| **API Surface Area** | Low | Medium (many endpoints) | Low (single endpoint) | Medium (many RPCs) |
| **Over-fetching Prevention** | Low | Low | High | Low |

**Scoring Guide**:
- **High**: Excellent fit for this criterion
- **Medium**: Adequate, with some trade-offs
- **Low**: Poor fit or requires workarounds

## Recommendation Guidance

### REST: Default Choice for Most Web APIs

REST is the default choice for most web APIs because:
- **Well-understood**: Most developers are familiar with REST
- **Excellent tooling**: OpenAPI, Swagger UI, Postman, extensive ecosystem
- **Browser-friendly**: Works natively with browsers
- **Caching**: HTTP caching works naturally
- **Simple mental model**: Resources + HTTP methods is easy to understand

**Choose REST when**:
- Building public APIs or partner integrations
- Simple CRUD operations
- Team is familiar with REST
- HTTP caching is important
- Browser clients are primary consumers

### GraphQL: Complex Data Relationships and Multiple Consumers

GraphQL excels when:
- **Complex data relationships**: Clients need related data from multiple sources
- **Multiple consumers with different needs**: Mobile needs minimal fields, web needs full details
- **Reducing over-fetching**: Clients request only needed fields
- **Rapid frontend iteration**: Frontend can request new fields without backend changes

**Choose GraphQL when**:
- You have complex nested data with varying consumer needs
- Over-fetching is a performance concern
- You want to reduce API surface area (single endpoint)
- Real-time subscriptions are needed
- Frontend teams need flexibility to request new fields

### gRPC: High-Performance Internal Service-to-Service Communication

gRPC is ideal for:
- **Internal microservices**: High performance, strong typing, code generation
- **High throughput**: Binary serialization, HTTP/2 multiplexing
- **Streaming**: Real-time data, long-lived connections
- **Polyglot environments**: Generate clients in multiple languages

**Choose gRPC when**:
- Building internal service-to-service APIs
- Performance is critical
- Streaming is needed
- Services are in different languages
- Browser clients are not a concern

### Hybrid: REST for External + gRPC for Internal

A common pattern is:
- **REST for external APIs**: Public APIs, partner integrations, browser clients
- **gRPC for internal communication**: Service-to-service, high performance

This pattern leverages the strengths of each:
- REST's familiarity and tooling for external consumers
- gRPC's performance for internal services

## Synergies

### Frontend Architecture Decisions

**If you chose MFE (Micro-Frontend)**:
- **REST is simplest**: Each MFE can call its own APIs, clear boundaries
- **GraphQL can reduce over-fetching**: Single GraphQL endpoint can serve multiple MFEs, reducing data transfer across MFE boundaries
- **Recommendation**: REST is simpler for MFE architectures. GraphQL can help if MFEs share data needs.

**If you chose SPA (Single Page Application)**:
- **REST works well**: Standard REST APIs with TanStack Query or SWR
- **GraphQL can simplify data fetching**: Single endpoint, flexible queries
- **Recommendation**: Either works. REST is simpler, GraphQL provides more flexibility.

### Backend Architecture Decisions

**If you chose microservices**:
- **gRPC for internal communication**: High performance, strong typing, code generation
- **REST for external APIs**: Familiar to consumers, better tooling
- **Recommendation**: Hybrid pattern (gRPC internal + REST external) is strong for microservices.

**If you chose monolithic architecture**:
- **REST is simplest**: No need for high-performance inter-service communication
- **GraphQL can help**: If you have complex data relationships within the monolith
- **Recommendation**: REST is typically sufficient for monoliths.

### Data Persistence Decisions

**If you chose event sourcing**:
- **Consider CQRS**: Separate read APIs (REST/GraphQL) and write APIs (commands)
- **Read APIs**: REST or GraphQL for querying event-sourced aggregates
- **Write APIs**: Command endpoints (POST) that create events
- **Recommendation**: REST for commands, REST or GraphQL for queries. GraphQL can help if queries are complex.

**If you chose traditional CRUD**:
- **REST maps naturally**: Resources map to database tables
- **GraphQL can help**: If you have complex joins and varying consumer needs
- **Recommendation**: REST is natural fit for CRUD. GraphQL if queries are complex.

### Authentication Decisions

**If you chose JWT**:
- **Bearer token auth works naturally with REST**: `Authorization: Bearer <token>`
- **GraphQL needs auth middleware**: Validate JWT in GraphQL resolvers
- **gRPC uses metadata**: JWT in gRPC metadata headers
- **Recommendation**: All three work with JWT. REST is simplest.

**If you chose OAuth 2.0**:
- **REST**: Standard OAuth flows (authorization code, client credentials)
- **GraphQL**: OAuth tokens in headers, same as REST
- **gRPC**: OAuth tokens in metadata
- **Recommendation**: All three work. REST has most OAuth tooling.

## Evolution Triggers

Reconsider your API style choice when these conditions change:

### Number of Distinct API Consumers Growing

**Trigger**: You have many different consumers with different data needs.

**Consider**: GraphQL to avoid endpoint proliferation. Instead of creating many REST endpoints for different use cases, GraphQL's flexible queries can serve multiple consumers.

**Example**: Mobile app needs minimal user data, web app needs full user profile, admin dashboard needs user + analytics. GraphQL can serve all three with different queries.

### Internal Service Communication Latency Becoming a Concern

**Trigger**: Internal service-to-service calls are slow or consuming too much bandwidth.

**Consider**: gRPC for internal communication. Binary serialization and HTTP/2 can significantly improve performance.

**Example**: REST APIs between services are causing latency issues. Migrate internal APIs to gRPC while keeping external APIs as REST.

### Query Complexity Increasing Beyond Simple CRUD

**Trigger**: REST endpoints are becoming complex with many query parameters, or you're creating many endpoints for different query patterns.

**Consider**: GraphQL for complex queries. GraphQL's flexible query language can replace multiple REST endpoints.

**Example**: `/users?status=active&role=admin&createdAfter=2024-01-01&hasOrders=true&orderStatus=shipped` becomes a GraphQL query.

### Need for Real-Time Streaming Data

**Trigger**: Clients need real-time updates (notifications, live data, chat).

**Consider**: 
- **GraphQL subscriptions**: For query-like real-time data
- **gRPC streaming**: For high-performance streaming (server, client, bidirectional)
- **REST with webhooks**: For event-driven updates (simpler but less efficient)

**Example**: Real-time order status updates, live chat, streaming analytics.

### API Surface Area Becoming Unmanageable

**Trigger**: Too many REST endpoints, difficult to maintain, inconsistent patterns.

**Consider**: 
- **GraphQL**: Single endpoint reduces surface area
- **API Gateway patterns**: Organize and route requests consistently
- **API versioning strategy**: Better versioning to manage evolution

**Example**: 50+ REST endpoints with inconsistent patterns. GraphQL can consolidate to a single endpoint with a consistent schema.

### Performance Requirements Changing

**Trigger**: API performance is no longer meeting requirements (latency, throughput).

**Consider**:
- **gRPC for internal APIs**: If internal service communication is the bottleneck
- **GraphQL query optimization**: If over-fetching is causing performance issues
- **REST caching**: If caching can solve performance problems

**Example**: Internal REST APIs are too slow. Migrate to gRPC for internal communication.

### Browser Support Requirements Changing

**Trigger**: Need to support browser clients (if currently using gRPC internally).

**Consider**: 
- **REST or GraphQL for browser clients**: gRPC requires gRPC-Web proxy
- **Hybrid approach**: gRPC internally, REST/GraphQL for browser clients

**Example**: Currently using gRPC internally, but need to add browser client support. Add REST or GraphQL layer for browsers.
