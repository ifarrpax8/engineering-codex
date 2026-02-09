# Production Readiness Checklist

Use this checklist before launching a service or feature to production. Each item links to the relevant codex content.

## Security

- [ ] **No hardcoded secrets** -- All secrets in vault/environment variables → [Security](../facets/security/best-practices.md)
- [ ] **Authentication tested** -- Login, logout, session expiry, token refresh → [Authentication Testing](../facets/authentication/testing.md)
- [ ] **Authorization verified** -- Permission boundaries enforced → [Authentication](../facets/authentication/architecture.md)
- [ ] **Input validation in place** -- All user inputs sanitized → [Security](../facets/security/best-practices.md)
- [ ] **HTTPS enforced** → [Security](../facets/security/best-practices.md)
- [ ] **Dependency vulnerabilities scanned** → [Security](../facets/security/architecture.md)
- [ ] **CORS configured correctly** → [Security](../facets/security/best-practices.md)

## Observability

- [ ] **Structured logging implemented** → [Observability](../facets/observability/best-practices.md)
- [ ] **Health check endpoint available** → [Observability](../facets/observability/architecture.md)
- [ ] **Key metrics being collected** → [Observability](../facets/observability/architecture.md)
- [ ] **Alerting configured for critical paths** → [Observability](../facets/observability/options.md)
- [ ] **Dashboards created** → [Data Visualization](../experiences/data-visualization/best-practices.md)

## Performance

- [ ] **Load testing completed** → [Performance Testing](../facets/performance/testing.md)
- [ ] **Database queries optimized** -- No N+1, indexes in place → [Performance](../facets/performance/best-practices.md)
- [ ] **Caching strategy implemented** (if applicable) → [Performance](../facets/performance/architecture.md)
- [ ] **Frontend bundle size reviewed** → [Performance](../facets/performance/best-practices.md)
- [ ] **Loading states implemented** → [Loading & Perceived Performance](../experiences/loading-and-perceived-performance/best-practices.md)

## Error Handling

- [ ] **Error boundaries in place** (frontend) → [Error Handling](../facets/error-handling/architecture.md)
- [ ] **Graceful degradation for service failures** → [Error Handling](../facets/error-handling/best-practices.md)
- [ ] **User-friendly error messages** → [Content Strategy](../experiences/content-strategy/best-practices.md)
- [ ] **Retry and circuit breaker patterns** (where applicable) → [Error Handling](../facets/error-handling/options.md)

## Testing

- [ ] **Unit test coverage meets target** → [Testing](../facets/testing/best-practices.md)
- [ ] **Integration tests passing** → [Testing](../facets/testing/architecture.md)
- [ ] **E2E tests for critical user flows** → [Testing](../facets/testing/options.md)
- [ ] **Edge cases covered** -- Null inputs, boundary conditions, permission scenarios → [Testing](../facets/testing/best-practices.md)

## Accessibility

- [ ] **Keyboard navigation works** → [Accessibility](../facets/accessibility/best-practices.md)
- [ ] **Screen reader tested** → [Accessibility](../facets/accessibility/testing.md)
- [ ] **Color contrast meets WCAG standards** → [Accessibility](../facets/accessibility/best-practices.md)
- [ ] **ARIA attributes used correctly** → [Accessibility](../facets/accessibility/architecture.md)

## Documentation

- [ ] **API documentation available** → [API Design](../facets/api-design/best-practices.md)
- [ ] **Runbook for operational procedures** → [Observability](../facets/observability/operations.md)
- [ ] **Architecture decisions documented** → [Documenting Decisions](../decision-frameworks/documenting-decisions.md)

## Deployment

- [ ] **Rollback plan documented** → [CI/CD](../facets/ci-cd/best-practices.md)
- [ ] **Feature toggles for risky features** → [Feature Toggles](../facets/feature-toggles/best-practices.md)
- [ ] **Database migrations tested** → [Data Persistence](../facets/data-persistence/testing.md)
- [ ] **Environment parity verified** -- Staging matches production → [CI/CD](../facets/ci-cd/best-practices.md)
