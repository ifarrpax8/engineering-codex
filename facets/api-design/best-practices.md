# API Design -- Best Practices

Language-agnostic principles for designing consistent, maintainable, and developer-friendly APIs.

## Resource Naming

### Use Plural Nouns for Collections

Collections should use plural nouns:

- ✅ `/users`, `/orders`, `/products`
- ❌ `/user`, `/order`, `/product`

Plural nouns clearly indicate a collection endpoint.

### Use Kebab-Case for Multi-Word URIs

Use kebab-case (hyphens) for multi-word resource names:

- ✅ `/order-items`, `/user-preferences`, `/payment-methods`
- ❌ `/orderItems`, `/order_items`, `/orderItems`

Kebab-case is URL-friendly and readable.

### Use Path Parameters for Identity

Use path parameters to identify specific resources:

- ✅ `/users/{id}`, `/orders/{orderId}`, `/users/{userId}/orders/{orderId}`
- ❌ `/users?id=123`, `/getUser/123`

Path parameters are part of the resource identity, not query parameters.

### Use Query Parameters for Filtering

Use query parameters for filtering, sorting, and pagination:

- ✅ `/users?status=active&role=admin&sort=createdAt&limit=20`
- ❌ `/users/filter/active/admin` (filters in path)

Query parameters are for operations on collections, not resource identity.

### Avoid Verbs in URIs

Use HTTP methods instead of verbs in URIs:

- ✅ `POST /users` (create), `DELETE /users/{id}` (delete)
- ❌ `POST /createUser`, `POST /users/{id}/delete`

HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) already convey the action. Verbs in URIs are redundant and violate REST principles.

## Error Response Format

### Adopt RFC 9457 (Problem Details for HTTP APIs)

Use RFC 9457 format for consistent error responses:

```json
{
  "type": "https://example.com/problems/user-not-found",
  "title": "User Not Found",
  "status": 404,
  "detail": "No user exists with ID '123'",
  "instance": "/v1/users/123"
}
```

**Fields**:
- **type**: URI identifying the problem type (can be dereferenced for documentation)
- **title**: Human-readable summary
- **status**: HTTP status code
- **detail**: Human-readable explanation specific to this occurrence
- **instance**: URI identifying the specific occurrence

### Consistent Error Format Across All Endpoints

All endpoints should return errors in the same format:

```json
// 400 Bad Request
{
  "type": "https://example.com/problems/invalid-request",
  "title": "Invalid Request",
  "status": 400,
  "detail": "The request body is malformed",
  "instance": "/v1/users"
}

// 422 Unprocessable Entity
{
  "type": "https://example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Email format is invalid",
  "instance": "/v1/users",
  "errors": [
    {
      "field": "email",
      "message": "Must be a valid email address"
    }
  ]
}
```

### Include Example

**Success response**:
```json
{
  "id": "123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Error response**:
```json
{
  "type": "https://example.com/problems/user-not-found",
  "title": "User Not Found",
  "status": 404,
  "detail": "No user exists with ID '999'",
  "instance": "/v1/users/999"
}
```

Consistent error format enables clients to handle errors uniformly.

## Idempotency

### GET, PUT, DELETE Are Naturally Idempotent

These HTTP methods are idempotent by design:

- **GET**: Retrieving the same resource multiple times has the same effect
- **PUT**: Replacing a resource with the same data multiple times has the same effect
- **DELETE**: Deleting a resource multiple times has the same effect (first delete succeeds, subsequent deletes return 404)

### POST Is Not Idempotent

POST is not idempotent—calling `POST /users` multiple times creates multiple users.

### Use Idempotency Keys for Non-Idempotent Operations

For non-idempotent POST operations, use idempotency keys:

**Client sends unique key**:
```
POST /v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "items": [...],
  "total": 100.00
}
```

**Server deduplicates**:
- Store idempotency key with request
- If key exists, return original response (don't create duplicate)
- Key expires after reasonable time (e.g., 24 hours)

**Critical for**:
- Payment operations (prevent duplicate charges)
- Order creation (prevent duplicate orders)
- Any operation with side effects that shouldn't be repeated

**Idempotency key requirements**:
- Client-generated unique identifier (UUID recommended)
- Sent in header: `Idempotency-Key: <uuid>`
- Server validates and deduplicates
- Response includes idempotency status (new request vs duplicate)

## Pagination by Default

### Never Return Unbounded Collections

Always paginate collection endpoints:

- ✅ `GET /users?limit=20&cursor=...`
- ❌ `GET /users` (returns all users)

Unbounded collections cause:
- Performance problems (large responses)
- Memory issues (client and server)
- Network timeouts
- Poor user experience

### Always Paginate Collection Endpoints

Every collection endpoint should support pagination:

```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "cursor": "eyJpZCI6IjEyMyJ9",
    "hasMore": true
  }
}
```

### Include Total Count (or Indicate "Has More")

Provide pagination metadata:

**Option 1: Total count** (for offset pagination):
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 150
  }
}
```

**Option 2: Has more** (for cursor pagination):
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "cursor": "eyJpZCI6IjEyMyJ9",
    "hasMore": true
  }
}
```

**Option 3: Next/previous cursors**:
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6IjE0NSJ9",
    "prevCursor": "eyJpZCI6IjEwMSJ9"
  }
}
```

### Provide Consistent Pagination Metadata Format

Use the same pagination format across all endpoints:

```json
// Consistent format
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "cursor": "...",
    "hasMore": true
  }
}
```

Don't mix formats (`page`/`pageSize` vs `limit`/`cursor`). Pick one format and use it consistently.

## API-First Design

### Design the Spec Before Writing Code

Design the API contract first:

1. **Define the spec**: Use TypeSpec or OpenAPI to define endpoints, request/response schemas
2. **Review the design**: Team review of API design before implementation
3. **Generate stubs**: Generate server stubs from spec
4. **Implement**: Implement against the spec

API-first ensures the API is designed for consumers, not constrained by implementation details.

### Use TypeSpec or OpenAPI to Define Contracts

Use specification languages to define contracts:

**TypeSpec**:
```typescript
@service({
  title: "User Service",
  version: "v1"
})
namespace Example;

model User {
  @key id: string;
  email: string;
  name: string;
}

@route("/users")
interface Users {
  @get list(): User[];
  @get get(@path id: string): User;
  @post create(@body user: User): User;
}
```

**OpenAPI**:
```yaml
paths:
  /users:
    get:
      responses:
        '200':
          description: List users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

### Generate Server Stubs and Client SDKs from Specs

Generate code from specs:

- **Server stubs**: Generate controller interfaces, DTOs from OpenAPI/TypeSpec
- **Client SDKs**: Generate client libraries in multiple languages
- **Documentation**: Generate interactive docs (Swagger UI) from specs

**Benefits**:
- Single source of truth (spec is the contract)
- Type safety (generated types match the spec)
- Consistency (server and clients use same types)
- Documentation always in sync

### Review API Design as a Team Before Implementation

API design reviews should include:
- **Product managers**: Ensure API supports use cases
- **Backend engineers**: Ensure API is implementable
- **Frontend engineers**: Ensure API is consumable
- **Architects**: Ensure API follows patterns and standards

Review before implementation prevents costly changes later.

## Request and Response Design

### Use Consistent Envelope vs Direct Response

Choose one pattern and stick to it:

**Option 1: Direct response** (simpler):
```json
{
  "id": "123",
  "email": "user@example.com"
}
```

**Option 2: Envelope** (more metadata):
```json
{
  "data": {
    "id": "123",
    "email": "user@example.com"
  },
  "meta": {
    "requestId": "req-123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

**Recommendation**: Use direct response for simple APIs. Use envelope if you need metadata (request IDs, pagination, links) consistently.

### Include Timestamps in ISO 8601

Use ISO 8601 format for timestamps:

- ✅ `"2024-01-01T12:00:00Z"` or `"2024-01-01T12:00:00+00:00"`
- ❌ `"2024-01-01 12:00:00"` or `1704110400` (Unix timestamp)

ISO 8601 is unambiguous and timezone-aware.

### Use Consistent ID Formats

Use consistent ID formats across the API:

- **UUIDs**: `"550e8400-e29b-41d4-a716-446655440000"` (recommended for distributed systems)
- **Numeric IDs**: `"123"` (simpler, but can leak information about scale)
- **Slugs**: `"user-john-doe"` (human-readable, but can change)

Pick one format and use it consistently. UUIDs are recommended for external APIs.

### Avoid Leaking Internal Identifiers

Don't expose internal database IDs or implementation details:

- ❌ `"internalId": 12345`, `"dbId": 67890`
- ✅ Use public-facing IDs only

Internal identifiers can leak information about your system (database structure, record counts).

### Include Links/References for Related Resources

Include links to related resources:

```json
{
  "id": "123",
  "email": "user@example.com",
  "_links": {
    "self": "/v1/users/123",
    "orders": "/v1/users/123/orders",
    "profile": "/v1/users/123/profile"
  }
}
```

Or use reference IDs:
```json
{
  "id": "123",
  "email": "user@example.com",
  "orders": [
    { "id": "order-1", "href": "/v1/orders/order-1" },
    { "id": "order-2", "href": "/v1/orders/order-2" }
  ]
}
```

Links enable clients to discover related resources without hardcoding URLs.

## Versioning Discipline

### Prefer Backward-Compatible Changes (Additive Fields)

Make changes backward-compatible when possible:

**Backward-compatible**:
- Adding new optional fields
- Adding new endpoints
- Adding new enum values (if clients handle unknown values gracefully)
- Making optional fields required (only if you handle missing fields)

**Breaking changes** (require new version):
- Removing fields or endpoints
- Changing field types
- Changing required fields to optional (clients may depend on them)
- Changing field names

### When Breaking Changes Are Necessary, Use Proper Deprecation Workflow

When breaking changes are necessary:

1. **Announce deprecation**: 6-12 months before removal
2. **Document migration path**: Clear steps for migrating to new version
3. **Support both versions**: Continue supporting deprecated version during migration window
4. **Add deprecation headers**: `Deprecation: true`, `Sunset: <date>`
5. **Monitor usage**: Track usage of deprecated version
6. **Retire**: Remove deprecated version after migration window

### Communicate Changes to Consumers with Adequate Migration Windows

Communication channels:
- **Email**: Notify registered API consumers
- **Changelog**: Document all changes (breaking and non-breaking)
- **Status page**: Announce major changes
- **Documentation**: Update docs with migration guides

Migration windows:
- **Internal APIs**: 3-6 months (teams can coordinate)
- **External APIs**: 6-12 months (partners need more time)

## Stack-Specific Callouts

### Kotlin/Java (Spring Boot)

**Spring MVC annotations**:
```kotlin
@RestController
@RequestMapping("/v1/users")
class UserController {
    @GetMapping("/{id}")
    fun getUser(@PathVariable id: String): User {
        // ...
    }
    
    @PostMapping
    fun createUser(@RequestBody @Valid request: CreateUserRequest): User {
        // ...
    }
}
```

**OpenAPI Generator for spec-first development**:
- Generate server stubs from OpenAPI spec
- Use `@Operation`, `@ApiResponse` annotations for documentation
- Generate client SDKs from same spec

**Spring HATEOAS for link generation**:
```kotlin
@GetMapping("/{id}")
fun getUser(@PathVariable id: String): EntityModel<User> {
    val user = userService.getUser(id)
    return EntityModel.of(user,
        linkTo<UserController> { getUser(id) }.withSelfRel(),
        linkTo<UserController> { getOrders(id) }.withRel("orders")
    )
}
```

**@ControllerAdvice for global error handling with RFC 9457**:
```kotlin
@ControllerAdvice
class ProblemDetailsExceptionHandler {
    @ExceptionHandler(UserNotFoundException::class)
    fun handleUserNotFound(e: UserNotFoundException): ResponseEntity<ProblemDetail> {
        val problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "User not found: ${e.userId}"
        )
        problem.setProperty("type", "https://example.com/problems/user-not-found")
        problem.setProperty("instance", "/v1/users/${e.userId}")
        return ResponseEntity(problem, HttpStatus.NOT_FOUND)
    }
}
```

### Frontend (JavaScript/TypeScript)

**Axios interceptors for auth token injection and error handling**:
```typescript
// Request interceptor: inject auth token
axios.interceptors.request.use(config => {
    const token = getAuthToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor: handle errors
axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            redirectToLogin();
        }
        // Transform to RFC 9457 format
        return Promise.reject(transformError(error));
    }
);
```

**TypeScript types generated from OpenAPI/TypeSpec specs**:
```typescript
// Generated from OpenAPI spec
import { User, CreateUserRequest } from './generated/api';

async function createUser(request: CreateUserRequest): Promise<User> {
    // TypeScript types ensure type safety
    return axios.post('/v1/users', request);
}
```

**API client abstraction layer** (don't scatter fetch calls):
```typescript
// api/users.ts
export const userApi = {
    get: (id: string) => axios.get<User>(`/v1/users/${id}`),
    list: (params?: UserListParams) => axios.get<User[]>('/v1/users', { params }),
    create: (request: CreateUserRequest) => axios.post<User>('/v1/users', request),
};

// Usage in components
const user = await userApi.get('123');
```

**TanStack Query / SWR for server state management**:
```typescript
// TanStack Query
const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userApi.list(),
});

// SWR
const { data: users, error } = useSWR('/v1/users', userApi.list);
```

These libraries handle caching, refetching, and loading states automatically.
