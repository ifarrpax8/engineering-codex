# New Project Checklist

Use this checklist when starting a greenfield project or new service. Each item links to the relevant codex content for deeper guidance.

## Architecture Decisions

- [ ] **Backend architecture pattern chosen** -- Layered, hexagonal, CQRS? → [Backend Architecture](../facets/backend-architecture/options.md)
- [ ] **Frontend architecture pattern chosen** -- SPA, MFE, SSR? → [Frontend Architecture](../facets/frontend-architecture/options.md)
- [ ] **API style decided** -- REST, GraphQL, gRPC? → [API Design](../facets/api-design/options.md)
- [ ] **Data persistence approach chosen** -- SQL, NoSQL, event sourcing? → [Data Persistence](../facets/data-persistence/options.md)
- [ ] **State management approach chosen** → [State Management](../facets/state-management/options.md)
- [ ] **Event-driven patterns decided** (if applicable) → [Event-Driven Architecture](../facets/event-driven-architecture/options.md)
- [ ] **Decisions documented** -- ADRs or decision log created → [Documenting Decisions](../decision-frameworks/documenting-decisions.md)

## Authentication & Security

- [ ] **Authentication approach chosen** → [Authentication](../facets/authentication/options.md)
- [ ] **Authorization model defined** (RBAC, ABAC) → [Authentication](../facets/authentication/architecture.md)
- [ ] **Security baseline established** → [Security Best Practices](../facets/security/best-practices.md)
- [ ] **Secrets management configured** → [Security](../facets/security/architecture.md)

## Testing Strategy

- [ ] **Test strategy defined** -- What levels, what coverage targets? → [Testing](../facets/testing/options.md)
- [ ] **Test tooling selected** → [Testing Best Practices](../facets/testing/best-practices.md)
- [ ] **CI pipeline includes tests** → [CI/CD](../facets/ci-cd/best-practices.md)

## Observability

- [ ] **Logging strategy defined** → [Observability](../facets/observability/architecture.md)
- [ ] **Metrics collection planned** → [Observability](../facets/observability/best-practices.md)
- [ ] **Alerting baseline configured** → [Observability](../facets/observability/options.md)

## Developer Experience

- [ ] **Local development setup documented** → [Developer Experience](../facets/developer-experience/best-practices.md)
- [ ] **README with setup instructions** → [Developer Experience](../facets/developer-experience/product.md)
- [ ] **Code formatting and linting configured** → [Developer Experience](../facets/developer-experience/best-practices.md)
- [ ] **Feature toggle approach decided** → [Feature Toggles](../facets/feature-toggles/options.md)

## User Experience

- [ ] **Internationalization planned** (if multi-locale) → [Internationalization](../facets/internationalization/options.md)
- [ ] **Accessibility requirements identified** → [Accessibility](../facets/accessibility/best-practices.md)
- [ ] **Error handling UX defined** → [Error Handling](../facets/error-handling/best-practices.md)
- [ ] **Loading states designed** → [Loading & Perceived Performance](../experiences/loading-and-perceived-performance/best-practices.md)

## Deployment

- [ ] **CI/CD pipeline configured** → [CI/CD](../facets/ci-cd/options.md)
- [ ] **Deployment strategy chosen** (blue/green, canary, rolling) → [CI/CD](../facets/ci-cd/architecture.md)
- [ ] **Environment management planned** → [CI/CD](../facets/ci-cd/best-practices.md)

## Evolution Awareness

- [ ] **Reviewed scaling triggers** → [Evolution Guides](../evolution/)
- [ ] **Documented current scale assumptions** -- Team size, traffic, complexity expectations
