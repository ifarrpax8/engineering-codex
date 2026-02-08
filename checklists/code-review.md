# Code Review Checklist

Use this checklist when reviewing a pull request. Focus on the items relevant to the changes being reviewed.

## Correctness

- [ ] **Logic is correct** -- Does the code do what the ticket/requirements ask for?
- [ ] **Edge cases handled** -- Null values, empty collections, boundary conditions
- [ ] **Error handling appropriate** -- Errors caught, logged, and surfaced to users meaningfully → [Error Handling](../facets/error-handling/best-practices.md)
- [ ] **No regression risk** -- Existing functionality isn't broken

## Architecture & Design

- [ ] **Follows existing patterns** -- Consistent with codebase conventions → [Refactoring](../facets/refactoring/best-practices.md)
- [ ] **Appropriate level of abstraction** -- Not over-engineered, not under-designed → [Refactoring](../facets/refactoring/best-practices.md)
- [ ] **Single responsibility** -- Each class/function has a clear purpose
- [ ] **API design consistent** -- Naming, structure, error responses follow conventions → [API Design](../facets/api-design/best-practices.md)
- [ ] **State management appropriate** -- Right tool for the scope (local vs global) → [State Management](../facets/state-management/best-practices.md)

## Security

- [ ] **No hardcoded secrets** → [Security](../facets/security/best-practices.md)
- [ ] **User input validated** -- Both client and server side → [Security](../facets/security/best-practices.md)
- [ ] **Authorization checked** -- Correct permission boundaries enforced → [Authentication](../facets/authentication/best-practices.md)
- [ ] **No sensitive data in logs** → [Observability](../facets/observability/best-practices.md)

## Testing

- [ ] **Tests included** -- New functionality has corresponding tests → [Testing](../facets/testing/best-practices.md)
- [ ] **Tests are meaningful** -- Testing behavior, not implementation details
- [ ] **Edge cases tested** -- Not just the happy path
- [ ] **Test names are descriptive** -- Clear what's being tested and expected outcome

## Performance

- [ ] **No N+1 queries** → [Performance](../facets/performance/best-practices.md)
- [ ] **Appropriate data fetching** -- Not over-fetching or under-fetching
- [ ] **Pagination for list operations** → [Tables & Data Grids](../experiences/tables-and-data-grids/best-practices.md)
- [ ] **No blocking operations on the main thread** (frontend)

## User Experience

- [ ] **Loading states present** → [Loading & Perceived Performance](../experiences/loading-and-perceived-performance/best-practices.md)
- [ ] **Error states handled gracefully** → [Content Strategy](../experiences/content-strategy/best-practices.md)
- [ ] **Accessible** -- Keyboard navigable, screen reader friendly → [Accessibility](../facets/accessibility/best-practices.md)
- [ ] **Translations used** (not hardcoded strings) → [Internationalization](../facets/internationalization/best-practices.md)

## Code Quality

- [ ] **Readable** -- Clear naming, minimal complexity, easy to follow
- [ ] **No dead code** -- Unused imports, unreachable branches, commented-out code removed
- [ ] **Consistent formatting** -- Matches project conventions
- [ ] **Dependencies justified** -- New dependencies are necessary and vetted
