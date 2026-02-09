# API Design -- Product Perspective

APIs are products with users—developers. Treating API design as a product discipline ensures better adoption, reduced support burden, and stronger partner relationships.

## Contents

- [API as a Product](#api-as-a-product)
- [Internal vs External APIs](#internal-vs-external-apis)
- [API Versioning and Its Business Impact](#api-versioning-and-its-business-impact)
- [Documentation](#documentation)
- [API Lifecycle](#api-lifecycle)
- [Success Metrics](#success-metrics)

## API as a Product

### Developers Are Users

When designing APIs, developers are your primary users. Their experience determines adoption, support costs, and long-term success. Developer experience (DX) encompasses:

- **Discoverability**: Can developers understand what endpoints exist and what they do?
- **Learnability**: How quickly can a developer make their first successful API call?
- **Predictability**: Do similar operations follow consistent patterns?
- **Debuggability**: When something goes wrong, can developers diagnose the issue?

### Documentation as a Product Feature

Documentation is not an afterthought—it's a core product feature. High-quality API documentation includes:

- **Interactive examples**: Swagger UI, Stoplight, or Postman Collections that developers can execute immediately
- **Code samples**: Real, working examples in multiple languages (at minimum, the languages your consumers use)
- **Error scenarios**: Document what happens when things go wrong, not just success cases
- **Changelog**: Clear communication about what changed, why, and how to migrate

### API Lifecycle Management

APIs have lifecycles that require product management:

1. **Design**: Define the contract before implementation. Use TypeSpec or OpenAPI to specify the API.
2. **Review**: API design reviews should include product managers, architects, and potential consumers.
3. **Build**: Implement against the spec. Generate server stubs from the spec when possible.
4. **Test**: Contract testing ensures the implementation matches the spec.
5. **Deploy**: Version management, feature flags, gradual rollouts.
6. **Monitor**: Track adoption, error rates, latency, developer feedback.
7. **Deprecate**: Communicate deprecation with clear migration paths and timelines.
8. **Retire**: Final sunset with adequate notice and support.

Each stage has different stakeholders: product managers care about adoption and business value, developers care about ease of use, operations cares about reliability and performance.

## Internal vs External APIs

### Internal APIs

Internal APIs serve your own teams and services. They benefit from:

- **Faster iteration**: Breaking changes can be coordinated across teams
- **Higher trust**: Internal consumers can be notified directly about changes
- **Less ceremony**: Versioning can be more flexible, documentation can be lighter
- **Shared context**: Teams understand the domain and can ask questions directly

However, internal APIs still need:
- Clear contracts (TypeSpec or OpenAPI)
- Consistent error handling
- Basic documentation
- Versioning strategy (even if more flexible)

### External/Partner APIs

External APIs serve partners, customers, or third-party developers. They require:

- **Stability guarantees**: Breaking changes require deprecation windows (typically 6-12 months)
- **Versioning contracts**: Clear versioning strategy with long-term support commitments
- **Breaking change policies**: Document what constitutes a breaking change and how they're communicated
- **SLAs**: Uptime guarantees, rate limits, support response times
- **Comprehensive documentation**: Self-service documentation that enables independent integration
- **SDKs and client libraries**: Reduce integration friction with pre-built clients

The cost of breaking an external API is high: partner frustration, lost integrations, reputation damage. External APIs should be designed more conservatively than internal ones.

## API Versioning and Its Business Impact

### Version Strategy Affects Partner Relationships

Your versioning strategy signals how you'll evolve the API:

- **No versioning**: Implies extreme stability or frequent breaking changes (both problematic)
- **URL versioning** (`/v1/`, `/v2/`): Clear, explicit, supports multiple versions simultaneously
- **Header versioning** (`Accept-Version: v2`): Less visible, requires client awareness
- **Semantic versioning**: Communicates change magnitude (major.minor.patch)

Choose a strategy that matches your evolution needs and partner expectations.

### Deprecation Policies and Migration Windows

Deprecation policies protect partners while allowing API evolution:

- **Deprecation notice**: Announce deprecation 6-12 months before removal
- **Migration guide**: Provide clear steps for migrating to the new version
- **Support period**: Continue supporting deprecated versions during the migration window
- **Communication channels**: Email, changelog, API documentation, status page

Shorter migration windows (3 months) work for internal APIs. External APIs typically need 6-12 months.

### Communicating Breaking Changes

Breaking changes include:
- Removing fields or endpoints
- Changing field types (string → number)
- Changing required fields
- Changing authentication requirements
- Changing error response formats

Non-breaking changes include:
- Adding new optional fields
- Adding new endpoints
- Adding new enum values (if consumers handle unknown values gracefully)

Communicate breaking changes through:
- API changelog with clear migration instructions
- Email notifications to registered API consumers
- Deprecation headers in responses (`Deprecation: true`, `Sunset: <date>`)
- Status page announcements

### Supporting Multiple Versions Simultaneously

Supporting multiple API versions allows gradual migration:

- **Separate code paths**: Route `/v1/` and `/v2/` to different handlers
- **Shared business logic**: Extract domain logic so both versions call the same core functions
- **Version-specific adapters**: Transform between version-specific DTOs and shared domain models
- **Monitoring**: Track usage by version to identify when older versions can be retired

The cost of supporting multiple versions is maintenance overhead. Balance this against partner migration timelines.

## Documentation

### Interactive Documentation

Interactive documentation lets developers explore and test APIs without writing code:

- **Swagger UI**: Auto-generated from OpenAPI specs, allows in-browser API calls
- **Stoplight**: Enhanced OpenAPI editor with mock servers and testing
- **Postman Collections**: Importable collections with examples and test scripts
- **GraphQL Playground**: Interactive GraphQL query builder with schema exploration

Interactive docs reduce time-to-first-successful-call, a key onboarding metric.

### Code-Generated Documentation

Generate documentation from API specs (TypeSpec, OpenAPI) to keep docs in sync with implementation:

- **Single source of truth**: The spec is the contract; docs are generated from it
- **Automatic updates**: When the spec changes, docs update automatically
- **Type safety**: Generated docs reflect actual request/response types
- **Version consistency**: Docs match the API version being documented

### Examples and Tutorials

Beyond reference documentation, provide:

- **Getting started guides**: Step-by-step tutorials for common use cases
- **Integration examples**: Complete, working examples for typical integration patterns
- **Error handling examples**: Show how to handle common error scenarios
- **SDK usage**: Examples using your SDKs or client libraries

### SDKs and Client Libraries

SDKs reduce integration friction:

- **Language-specific**: Provide SDKs in languages your consumers use (JavaScript/TypeScript, Python, Java)
- **Type safety**: Generated from API specs, providing compile-time type checking
- **Error handling**: Consistent error handling patterns
- **Authentication**: Built-in auth token management
- **Documentation**: SDK-specific docs with examples

SDKs are especially valuable for external APIs where reducing integration time directly impacts adoption.

## API Lifecycle

### Design → Review → Build → Test → Deploy → Monitor → Deprecate → Retire

Each lifecycle stage has different concerns:

**Design**: 
- Stakeholders: Product managers, architects, potential consumers
- Concerns: Use cases, resource modeling, versioning strategy

**Review**:
- Stakeholders: Cross-functional team (product, engineering, security, operations)
- Concerns: Consistency, security, performance, maintainability

**Build**:
- Stakeholders: Backend engineers
- Concerns: Implementation matches spec, error handling, performance

**Test**:
- Stakeholders: QA, engineers
- Concerns: Contract compliance, integration scenarios, error cases

**Deploy**:
- Stakeholders: DevOps, operations
- Concerns: Versioning, backward compatibility, monitoring

**Monitor**:
- Stakeholders: Operations, product managers
- Concerns: Adoption, error rates, latency, developer feedback

**Deprecate**:
- Stakeholders: Product managers, partner success teams
- Concerns: Migration timelines, communication, support

**Retire**:
- Stakeholders: Operations, product managers
- Concerns: Final sunset date, last-chance migration support

## Success Metrics

### Adoption Rate (External APIs)

For external APIs, track:
- Number of active API keys/consumers
- API call volume growth over time
- New consumer onboarding rate
- Time-to-first-successful-call (onboarding friction)

Low adoption may indicate documentation gaps, integration complexity, or missing use cases.

### Error Rate

Track HTTP status code distributions:
- **4xx errors**: Client errors (400 Bad Request, 401 Unauthorized, 404 Not Found, 422 Unprocessable Entity)
- **5xx errors**: Server errors (500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable)

High 4xx rates suggest documentation or SDK issues. High 5xx rates indicate reliability problems.

### Latency

Measure response time percentiles:
- **p50 (median)**: Typical response time
- **p95**: 95% of requests complete within this time
- **p99**: 99% of requests complete within this time

Track latency by endpoint to identify performance bottlenecks. External APIs often have SLA commitments (e.g., p95 < 200ms).

### Time-to-First-Successful-Call

Measure how long it takes a new developer to make their first successful API call:
- Time from documentation access to first successful call
- Number of failed attempts before success
- Common failure points (authentication, request format, missing fields)

This metric directly measures onboarding friction and documentation effectiveness.

### Breaking Change Frequency

Track how often breaking changes occur:
- Breaking changes per quarter/year
- Deprecation-to-retirement timeline adherence
- Migration success rate (how many consumers successfully migrate)

Frequent breaking changes indicate design instability. Infrequent breaking changes with long migration windows indicate healthy evolution.

### Documentation Coverage

Measure documentation completeness:
- Percentage of endpoints with examples
- Percentage of error responses documented
- Documentation freshness (last updated date)
- Developer feedback on documentation clarity

Documentation is a product feature—measure and improve it like any other feature.
