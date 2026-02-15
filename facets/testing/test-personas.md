# Testing: Test Personas

Test personas are thinking hats for test design. Each persona represents a different intent when exercising the system, ensuring tests cover more than just the happy path.

## The Six Personas

### The Optimist

**Intent**: Verify the feature works as designed under ideal conditions.

**Asks**: "Given valid input and a healthy system, does this produce the correct result?"

**Generates**:
- Standard success flows
- Expected state transitions
- Correct output for typical input
- Happy path user journeys

**Example**: A payment endpoint receives a valid request with sufficient funds and returns a 201 with the correct response body.

**Anti-pattern**: A test suite where every test is an Optimist test. If all tests pass with valid input, you have no confidence in failure handling.

### The Saboteur

**Intent**: Break things deliberately. Verify the system fails gracefully.

**Asks**: "What happens when dependencies fail, input is invalid, or the system is in a bad state?"

**Generates**:
- Exception and error response tests
- Timeout and unavailability scenarios
- Invalid input rejection
- Partial failure handling (one of N steps fails)
- Compensation and rollback behaviour

**Example**: A payment endpoint returns a 502 and logs an error when the downstream payment provider times out, without charging the customer.

**Key principle**: Every external integration should have at least one Saboteur test. Every validation rule should have a rejection test.

### The Boundary Walker

**Intent**: Test at the exact limits of valid input, system capacity, and state transitions.

**Asks**: "What happens at zero, at the maximum, at exactly the limit, and one past it?"

**Generates**:
- Zero, null, empty string, empty collection
- Maximum length, maximum value, maximum count
- Exactly-at-limit (e.g. 100 items when limit is 100)
- Off-by-one (99, 100, 101)
- Type boundaries (Int.MAX_VALUE, negative numbers for unsigned concepts)
- Date boundaries (midnight, DST transitions, leap years, month-end)

**Example**: A pagination endpoint handles `page=0`, `page=1`, `page=MAX_INT`, `size=0`, `size=-1`, and `size=1000` (above the configured max).

**Key principle**: If a method accepts a number, string, or collection, there is a boundary to test.

### The Explorer

**Intent**: Discover unexpected behaviour through unusual but valid scenarios.

**Asks**: "What about combinations, ordering, timing, and states that are valid but uncommon?"

**Generates**:
- Concurrent access to the same resource
- Out-of-order event processing
- Duplicate submissions (idempotency)
- Unicode, emoji, and special characters in text fields
- Rapid repeated actions (double-click, retry storms)
- Valid but unusual combinations (all optional fields omitted, all fields at max length)

**Example**: Two users simultaneously update the same invoice. The system applies optimistic locking and rejects the second update with a 409.

**Key principle**: Explorers find the bugs that pass code review. They are the most creative persona but also the hardest to enumerate systematically.

### The Auditor

**Intent**: Verify security, compliance, and access control.

**Asks**: "Can someone bypass authorisation, access another tenant's data, or escalate privileges?"

**Generates**:
- Authentication bypass attempts (missing token, expired token, malformed token)
- Authorisation checks (user A accessing user B's resource)
- Tenant isolation (cross-tenant data leakage)
- Input injection (SQL, XSS, command injection)
- Sensitive data exposure in responses and logs
- Rate limiting and abuse prevention

**Example**: A request with a valid token for Tenant A attempts to fetch an invoice belonging to Tenant B and receives a 403.

**Key principle**: Every endpoint that requires authentication needs at least one Auditor test for the unauthenticated case. Every multi-tenant resource needs a cross-tenant test.

### The User

**Intent**: Validate the complete user journey, end-to-end.

**Asks**: "Does the feature work from the user's perspective, across all the services and UI involved?"

**Generates**:
- Multi-step workflow tests (create → edit → submit → approve)
- Cross-service integration (command → event → projection → query)
- UI interaction flows (form fill → submit → confirmation → navigation)
- Data consistency across read and write models
- Recovery flows (start → fail → retry → succeed)

**Example**: A user creates an invoice in the MFE, the command is processed by the backend, the event updates the read model, and the invoice appears in the list view with the correct status.

**Key principle**: User persona tests are expensive. Reserve them for critical business flows. They sit at the top of the test pyramid.

## Mapping Personas to the Test Pyramid

| Persona | Primary Layer | Secondary Layer |
|---------|--------------|-----------------|
| The Optimist | Unit | Integration |
| The Saboteur | Unit, Integration | Component |
| The Boundary Walker | Unit | Integration |
| The Explorer | Integration | E2E |
| The Auditor | Integration | E2E |
| The User | E2E | Integration |

## Using Personas for Test Design

### Per-method checklist

For each public method or endpoint, ask:
1. **Optimist**: Does the happy path work?
2. **Saboteur**: What happens when it fails?
3. **Boundary Walker**: What are the input limits?
4. **Explorer**: What unusual-but-valid scenarios exist?
5. **Auditor**: Is access properly controlled?
6. **User**: Is this part of a critical journey? (E2E only for key flows)

### Coverage matrix

Use personas as columns in a coverage matrix:

| Behavior | Optimist | Saboteur | Boundary | Explorer | Auditor |
|----------|----------|----------|----------|----------|---------|
| createInvoice() | PASS | PASS | MISS | MISS | PASS |
| calculateTotal() | PASS | MISS | MISS | N/A | N/A |
| POST /invoices | PASS | PASS | PASS | MISS | PASS |

MISS cells are candidate tests. Not every cell needs to be filled — use judgement based on risk and the method's responsibility.

### When to apply which persona

- **All public methods**: Optimist + Saboteur (minimum viable coverage)
- **Methods with numeric/string/collection input**: + Boundary Walker
- **Methods with external dependencies**: + Explorer (concurrency, ordering)
- **Authenticated endpoints**: + Auditor
- **Critical business workflows**: + User (E2E)

## Related

- [Test Pyramid](architecture.md#test-pyramid) -- Layer definitions and ratio targets
- [Best Practices](best-practices.md) -- Test structure and naming conventions
- [Gotchas](gotchas.md) -- Common testing pitfalls
