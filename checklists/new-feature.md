# New Feature Checklist

Use this checklist when adding a significant feature to an existing project. Not every item applies to every feature -- use judgment on what's relevant.

## Before Starting

- [ ] **Requirements clear** -- Acceptance criteria defined and understood
- [ ] **Architecture approach decided** -- Does this feature fit existing patterns or need something new? → [Refactoring](../facets/refactoring/best-practices.md)
- [ ] **Cross-facet impacts identified** -- Does this feature touch authentication, permissions, i18n, etc.?

## Authentication & Permissions

- [ ] **New permissions needed?** → [Authentication](../facets/authentication/architecture.md)
- [ ] **Permission UX handled** -- Disabled states, hidden elements, access denied flows → [Permissions UX](../experiences/permissions-ux/best-practices.md)
- [ ] **Multi-tenancy implications** -- Data isolation, tenant-specific behavior → [Multi-Tenancy UX](../experiences/multi-tenancy-ux/best-practices.md)

## User Experience

- [ ] **Loading states designed** → [Loading & Perceived Performance](../experiences/loading-and-perceived-performance/best-practices.md)
- [ ] **Empty states handled** → [Content Strategy](../experiences/content-strategy/best-practices.md)
- [ ] **Error states handled** → [Error Handling](../facets/error-handling/best-practices.md)
- [ ] **Form validation in place** (if applicable) → [Forms & Data Entry](../experiences/forms-and-data-entry/best-practices.md)
- [ ] **Responsive design considered** → [Responsive Design](../experiences/responsive-design/best-practices.md)
- [ ] **Accessibility requirements met** → [Accessibility](../facets/accessibility/best-practices.md)

## Internationalization

- [ ] **All user-facing strings translatable** → [Internationalization](../facets/internationalization/best-practices.md)
- [ ] **Date/currency/number formatting locale-aware** → [Internationalization](../facets/internationalization/architecture.md)

## Data & API

- [ ] **API design follows existing conventions** → [API Design](../facets/api-design/best-practices.md)
- [ ] **Pagination implemented** (for list endpoints) → [API Design](../facets/api-design/architecture.md) and [Tables & Data Grids](../experiences/tables-and-data-grids/best-practices.md)
- [ ] **Database migrations backward-compatible** → [Data Persistence](../facets/data-persistence/best-practices.md)

## Testing

- [ ] **Unit tests written** → [Testing](../facets/testing/best-practices.md)
- [ ] **Integration tests for new endpoints/services** → [Testing](../facets/testing/architecture.md)
- [ ] **E2E tests for critical paths** → [Testing](../facets/testing/options.md)
- [ ] **Edge cases covered** -- Null inputs, boundaries, concurrent access

## Observability

- [ ] **Logging added for key operations** → [Observability](../facets/observability/best-practices.md)
- [ ] **Metrics for new business operations** (if applicable) → [Observability](../facets/observability/architecture.md)

## Deployment

- [ ] **Feature toggle wrapping new feature** (if risky) → [Feature Toggles](../facets/feature-toggles/best-practices.md)
- [ ] **Backward-compatible deployment** -- Can be deployed without downtime
- [ ] **Rollback plan identified** → [CI/CD](../facets/ci-cd/best-practices.md)

## Code Quality

- [ ] **Follows existing codebase patterns** → [Refactoring](../facets/refactoring/best-practices.md)
- [ ] **No premature abstraction** -- Extracted only what's proven to be reusable → [Refactoring](../facets/refactoring/best-practices.md)
- [ ] **State management follows established patterns** → [State Management](../facets/state-management/best-practices.md)
