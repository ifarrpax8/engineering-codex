# Feature Toggles: Options

## Contents

- [Feature Toggle Implementation Options](#feature-toggle-implementation-options)
- [Open-Source Alternatives](#open-source-alternatives)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)
- [Decision Framework](#decision-framework)
- [Summary](#summary)

This document provides a decision matrix comparing different feature toggle implementation approaches, evaluation criteria, and recommendations for when to use each option. It covers both simple implementations suitable for teams without commercial service budgets and sophisticated commercial platforms.

## Feature Toggle Implementation Options

### 1. Database-Backed Custom Service

A custom toggle service that stores toggle definitions and states in a database (typically PostgreSQL), evaluated by application code with caching for performance. Includes an admin UI for non-engineers to manage toggles.

**Description**: Toggles are stored in a database table with fields for name, enabled status, targeting rules (JSON), description, and audit fields. A ToggleService evaluates toggles at request time, applying targeting rules based on user context. Results are cached to avoid per-request database queries. An admin UI allows product managers and operations teams to change toggles without code deployment.

**Strengths**:
- Full control over implementation and data
- No per-evaluation costs (unlike some commercial platforms)
- Customizable to specific team needs
- Toggle data stored in your own database (data sovereignty)
- Can integrate with existing admin tools and workflows
- Supports basic targeting (user, tenant, percentage rollouts)
- Audit trail via database change tracking
- Works offline (cached values if database unavailable)

**Weaknesses**:
- Requires development and maintenance effort
- Must build and maintain admin UI
- Caching complexity (invalidation, distributed systems)
- No built-in experimentation analytics
- Limited targeting capabilities compared to commercial platforms
- Must handle scaling and performance yourself
- No built-in A/B testing statistical analysis
- Requires database schema migrations for changes

**Best For**:
- Teams with 5-20 active toggles
- Need basic targeting (user, tenant, percentage)
- Want data sovereignty (toggle data in own database)
- Have development resources to build and maintain
- No budget for commercial services
- Need integration with existing admin tools
- Simple use cases (release toggles, basic ops toggles)

**Avoid When**:
- Need advanced targeting (geographic, custom attributes, complex rules)
- Running many experiments requiring analytics
- Need instant toggle changes across distributed systems
- Want managed infrastructure (no ops overhead)
- Have budget for commercial platform
- Need compliance-ready audit trails out of the box
- Team lacks resources to build/maintain custom solution

### 2. Configuration-File Toggles

Toggles stored in application configuration files (application.yml, environment variables), changed via configuration update and application restart. Simple boolean evaluation with no targeting.

**Description**: Toggles are defined in configuration files (YAML, properties, environment variables) and loaded at application startup. Toggle evaluation is simple boolean checks against configuration values. Changes require configuration update and application restart. No database or external service required.

**Strengths**:
- Simplest implementation (no infrastructure)
- No external dependencies
- Fast evaluation (in-memory lookups)
- Version controlled (toggles in git)
- Easy to understand and debug
- No operational overhead
- Works in any environment (dev, staging, prod)
- No costs (no services to pay for)

**Weaknesses**:
- Requires application restart for changes
- No targeting capabilities (all-or-nothing)
- No admin UI (requires code/config changes)
- No audit trail (unless custom logging added)
- Can't change toggles instantly (must restart)
- Not suitable for frequent toggle changes
- No experimentation capabilities
- Configuration drift risk (different values in different environments)

**Best For**:
- Teams with < 5 toggles
- Ops toggles that change rarely
- Simple use cases (release toggles, kill switches)
- No targeting needed (all-or-nothing)
- Want simplest possible solution
- Can tolerate application restarts for toggle changes
- Early stage projects with minimal toggle needs

**Avoid When**:
- Need to change toggles without restarting
- Require user/tenant targeting
- Need percentage rollouts
- Running experiments or A/B tests
- Have many toggles (> 5)
- Need instant toggle changes
- Want admin UI for non-engineers
- Need audit trail for compliance

### 3. Commercial Platform (LaunchDarkly / Unleash Cloud)

Managed feature flag platform with SDKs, user targeting, analytics, and audit trails. Handles infrastructure, scaling, and provides sophisticated capabilities out of the box.

**Description**: Commercial platforms provide managed infrastructure for feature toggles with SDKs for multiple languages. Toggles are managed through web UIs, evaluated locally by SDKs (no API calls per evaluation), and support advanced targeting, experimentation, and analytics. Changes propagate instantly via streaming updates. Includes audit trails, user management, and integration capabilities.

**Strengths**:
- Managed infrastructure (no ops overhead)
- Advanced targeting (user attributes, geographic, custom rules)
- Built-in experimentation and A/B testing analytics
- Instant toggle changes (streaming updates to SDKs)
- Comprehensive audit trails (compliance-ready)
- SDKs for multiple languages and frameworks
- Professional admin UI for non-engineers
- Statistical analysis for experiments
- Integration with analytics platforms
- User management and permissions
- High availability and reliability

**Weaknesses**:
- Ongoing costs (subscription fees)
- Vendor lock-in (must migrate to change providers)
- External dependency (requires internet connectivity)
- Learning curve for team
- May have more features than needed (overkill for simple use cases)
- Per-evaluation costs in some pricing models
- Requires SDK integration in codebase
- Less control over data storage and infrastructure

**Best For**:
- Teams with 20+ active toggles
- Need advanced targeting and experimentation
- Running A/B testing programs
- Need compliance-ready audit trails
- Want managed infrastructure (no ops)
- Have budget for commercial services
- Need instant toggle changes
- Want professional admin UI
- Multiple teams/services using toggles
- Need integration with analytics platforms

**Avoid When**:
- Budget constraints (no money for commercial services)
- Simple use cases (< 5 toggles, no targeting)
- Want data sovereignty (toggle data in own systems)
- Prefer open-source solutions
- Need offline operation (no internet connectivity)
- Want full control over implementation
- Early stage projects with minimal needs

## Open-Source Alternatives

### Unleash (Open-Source)

Open-source feature flag platform that can be self-hosted or used via Unleash Cloud. Provides SDKs, targeting, and experimentation capabilities similar to commercial platforms.

**Description**: Unleash is an open-source feature flag platform with a server component (self-hosted or cloud) and SDKs for multiple languages. Supports targeting, percentage rollouts, A/B testing, and includes a web UI. Can be deployed on your own infrastructure or used via Unleash Cloud (managed option).

**Strengths**:
- Open-source (no licensing costs for self-hosted)
- Self-hosted option (data sovereignty)
- Similar capabilities to commercial platforms
- Active community and development
- SDKs for multiple languages
- Can start self-hosted, migrate to cloud later
- No vendor lock-in (open source)

**Weaknesses**:
- Self-hosting requires ops overhead
- Must maintain infrastructure yourself (if self-hosted)
- Smaller ecosystem than commercial platforms
- Less polished than commercial alternatives
- Community support (not commercial support)
- Requires technical expertise to deploy/maintain

**When to Use**:
- Want open-source solution
- Need capabilities of commercial platform
- Have ops resources for self-hosting
- Want to avoid vendor lock-in
- Budget constraints but need advanced features
- Want data sovereignty with advanced features

### Flagsmith (Open-Source)

Open-source feature flag and remote config platform, available as self-hosted or cloud service. Combines feature flags with remote configuration management.

**Description**: Flagsmith provides feature flags and remote configuration in a single platform. Supports targeting, A/B testing, and includes SDKs. Available as open-source (self-hosted) or managed cloud service. Combines feature toggles with configuration management.

**Strengths**:
- Open-source option available
- Combines feature flags with remote config
- Self-hosted or cloud options
- SDKs for multiple languages
- Active development and community
- No vendor lock-in (open source)

**Weaknesses**:
- Self-hosting requires ops overhead
- Smaller ecosystem than commercial leaders
- Less mature than some alternatives
- Community support for open-source version

**When to Use**:
- Want feature flags + remote config in one platform
- Prefer open-source solutions
- Have ops resources for self-hosting
- Want to avoid vendor lock-in

### OpenFeature (Vendor-Neutral Standard)

Vendor-neutral API standard for feature flags, allowing teams to swap implementations without code changes. Provides abstraction layer over different toggle providers.

**Description**: OpenFeature is a vendor-neutral specification and SDK for feature flags. It provides a standard API that works with multiple providers (LaunchDarkly, Unleash, custom implementations). Teams write code against OpenFeature API and can swap providers without code changes.

**Strengths**:
- Vendor-neutral (no lock-in)
- Swap providers without code changes
- Standard API across languages
- Works with multiple providers
- Future-proof (new providers automatically supported)
- Reduces risk of vendor lock-in

**Weaknesses**:
- Additional abstraction layer (slight overhead)
- Newer standard (less mature ecosystem)
- May not support all provider-specific features
- Requires provider-specific configuration

**When to Use**:
- Want to avoid vendor lock-in from day one
- May need to change providers in future
- Want standard API across services
- Adopting feature toggles for first time
- Multiple teams may use different providers
- Want future flexibility

## Evaluation Criteria

| Criteria | Weight | Database-Backed | Config-File | Commercial Platform |
|----------|--------|----------------|-------------|---------------------|
| **Cost** | High | 4 (one-time dev, no ongoing) | 5 (free) | 2 (ongoing subscription) |
| **Targeting Capabilities** | High | 3 (basic targeting) | 1 (none) | 5 (advanced targeting) |
| **Operational Overhead** | Medium | 3 (must maintain) | 5 (minimal) | 5 (managed) |
| **Audit Trail** | Medium | 3 (custom implementation) | 2 (manual logging) | 5 (built-in) |
| **Developer Experience** | High | 3 (custom code) | 4 (simple) | 5 (polished SDKs) |
| **Instant Changes** | Medium | 4 (with caching invalidation) | 1 (requires restart) | 5 (streaming updates) |
| **Experimentation** | Low | 2 (custom implementation) | 1 (none) | 5 (built-in analytics) |
| **Data Sovereignty** | Low | 5 (your database) | 5 (your config) | 2 (vendor database) |
| **Scalability** | Medium | 3 (must handle yourself) | 4 (application scaling) | 5 (managed scaling) |

**Scoring**: 1 = Poor, 2 = Below Average, 3 = Average, 4 = Good, 5 = Excellent

**Weighted Scores**:
- Database-Backed: (4×3 + 3×3 + 3×2 + 3×2 + 3×3 + 4×2 + 2×1 + 5×1 + 3×2) / 19 = 3.3
- Config-File: (5×3 + 1×3 + 5×2 + 2×2 + 4×3 + 1×2 + 1×1 + 5×1 + 4×2) / 19 = 3.1
- Commercial Platform: (2×3 + 5×3 + 5×2 + 5×2 + 5×3 + 5×2 + 5×1 + 2×1 + 5×2) / 19 = 4.4

## Recommendation Guidance

### Start Simple

**Configuration-File Toggles** are recommended for:
- Teams new to feature toggles
- < 5 toggles, no targeting needed
- Simple use cases (release toggles, ops toggles)
- Can tolerate application restarts for changes
- Want zero infrastructure and costs

Start here to learn feature toggle concepts without complexity. Evolve to database-backed or commercial platform as needs grow.

### Evolve to Database-Backed

**Database-Backed Custom Service** is recommended when:
- 5-20 active toggles
- Need basic targeting (user, tenant, percentage rollouts)
- Want data sovereignty (toggle data in own database)
- Have development resources to build/maintain
- No budget for commercial services
- Need admin UI for non-engineers
- Want to avoid vendor lock-in

This is the sweet spot for teams that need more than config files but don't want commercial platform costs or vendor lock-in.

### Consider Commercial Platform

**Commercial Platform (LaunchDarkly/Unleash Cloud)** is recommended when:
- 20+ active toggles
- Need advanced targeting and experimentation
- Running A/B testing programs
- Need compliance-ready audit trails
- Have budget for commercial services
- Want managed infrastructure (no ops overhead)
- Need instant toggle changes
- Multiple teams/services using toggles

The operational benefits and advanced capabilities justify costs for teams at scale.

### Adopt OpenFeature Standard

**OpenFeature** should be adopted as abstraction layer from day one if:
- May need to change providers in future
- Want to avoid vendor lock-in
- Multiple teams may use different providers
- Adopting feature toggles for first time
- Want future flexibility

Using OpenFeature allows teams to start with one provider and migrate to another without code changes, reducing risk of vendor lock-in.

## Synergies

Feature toggles work well with other engineering practices:

**Trunk-Based Development**: Release toggles enable merging incomplete work to main branch, supporting continuous integration. Teams can deploy to production multiple times per day while controlling feature exposure.

**Canary Deployments**: Toggles provide additional release control beyond deployment strategy. Canary deployments control which instances run new code; toggles control which users see new features. Combined, they provide fine-grained release control.

**RBAC/ABAC**: Permission toggles can leverage existing authorization infrastructure. User roles and attributes from authentication systems can be used for toggle evaluation, avoiding duplicate user data.

**Multi-Tenancy**: Tenant-specific toggle evaluation enables per-customer feature availability. Toggles can control which features are available to which tenants, supporting customization and tiered offerings.

**Configuration Management**: Toggle storage and evaluation integrate with configuration management systems. Toggles can be managed alongside other configuration, and configuration changes can trigger toggle updates.

**Testing**: Toggle-aware testing strategies enable testing features in both states. Combinatorial testing verifies toggle interactions, and toggle state management ensures test isolation.

## Evolution Triggers

Teams should evolve their toggle implementation when:

**Config-File → Database-Backed**:
- More than 5 config-file toggles
- Need to change toggles without restarting
- Need basic targeting (user, tenant, percentage)
- Want admin UI for non-engineers
- Need audit trail

**Database-Backed → Commercial Platform**:
- More than 20 active toggles
- Need advanced targeting (geographic, custom attributes, complex rules)
- Running experimentation programs requiring analytics
- Need compliance-ready audit trails
- Want managed infrastructure (reduce ops overhead)
- Have budget for commercial services

**Any → OpenFeature**:
- Adopting feature toggles for first time
- May need to change providers in future
- Want to avoid vendor lock-in
- Multiple teams may use different providers

**Commercial Platform → Self-Hosted (Unleash/Flagsmith)**:
- Budget constraints but need advanced features
- Want data sovereignty with advanced capabilities
- Have ops resources for self-hosting
- Want to avoid vendor lock-in while keeping advanced features

## Decision Framework

When choosing a feature toggle implementation:

1. **Assess Current Needs**:
   - How many toggles do you need?
   - Do you need targeting?
   - Do you need experimentation?
   - What's your budget?

2. **Consider Future Growth**:
   - Will toggle count grow?
   - Will needs become more complex?
   - Will you need advanced capabilities?

3. **Evaluate Constraints**:
   - Budget limitations?
   - Ops resources available?
   - Data sovereignty requirements?
   - Compliance/audit needs?

4. **Choose Starting Point**:
   - Start simple (config-file) if new to toggles
   - Database-backed if need more than config but no commercial budget
   - Commercial platform if have budget and need advanced features

5. **Plan Evolution Path**:
   - How will you migrate as needs grow?
   - What are the evolution triggers?
   - How will you avoid vendor lock-in?

6. **Consider OpenFeature**:
   - Adopt as abstraction layer from day one
   - Provides flexibility to change providers
   - Reduces risk of vendor lock-in

## Summary

The choice of feature toggle implementation depends on team needs, budget, and scale:

- **Start Simple**: Config-file toggles for < 5 toggles, no targeting
- **Evolve**: Database-backed service for 5-20 toggles, basic targeting, no commercial budget
- **Scale**: Commercial platform for 20+ toggles, advanced targeting, experimentation, budget available
- **Future-Proof**: Adopt OpenFeature standard as abstraction layer to avoid vendor lock-in

All approaches can evolve—teams can start with config files and migrate to database-backed or commercial platforms as needs grow. The key is to choose an approach that matches current needs while planning for future growth. OpenFeature provides a path to avoid vendor lock-in regardless of initial choice.
