# Pax8 Standards Map

This document maps active Pax8 Architecture Decision Records (ADRs) and Request for Comments (RFCs) to Engineering Codex facets. Each entry indicates whether the decision is a **Standard** (follow unless you have a strong reason not to) or **Guidance** (recommended but flexible).

## Complete ADR/RFC Mapping

| ADR / RFC | Summary | Codex Facet | Type |
|-----|---------|-------------|------|
| [ADR-00001](../adr/00001-use-adrs.md) | All significant architecture decisions must be documented as ADRs | work-management | Standard |
| [ADR-00007](../adr/00007-domain-object-identifiers.md) | Use UUIDs for domain object IDs, avoid sequential integers for external exposure | api-design | Standard |
| [ADR-00016](../adr/00016-adopt-ktlint.md) | Use ktlint for Kotlin code formatting in all microservices | backend-architecture | Standard |
| [ADR-00025](../adr/00025-remove-version-dependency-variables.md) | Use Gradle version catalogs instead of ext variables for dependency versions | dependency-management | Standard |
| [ADR-00026](../adr/00026-span-name-prefix.md) | Prefix distributed trace span names with service name for clarity | observability | Standard |
| [ADR-00027](../adr/00027-frontend-observability.md) | Use Sentry for frontend error tracking and performance monitoring | observability | Standard |
| [ADR-00034](../adr/00034-github-repository-rulesets.md) | Use GitHub Repository Rulesets (not legacy branch protection) to enforce standards | repository-governance | Standard |
| [ADR-00035](../adr/00035-use-feature-flags.md) | Feature flags are approved for use; evaluate per-project whether to use LaunchDarkly or a simpler approach | feature-toggles | Guidance |
| [ADR-00037](../adr/00037-mongodb-usage.md) | MongoDB is approved for specific use cases; PostgreSQL remains the default relational database | data-persistence | Guidance |
| [ADR-00038](../adr/00038-conventional-commits.md) | All repositories must use Conventional Commits format | repository-governance | Standard |
| [ADR-00039](../adr/00039-prefix-ecr-image-tags.md) | ECR image tags must be prefixed with branch/environment context | ci-cd | Standard |
| [ADR-00039](../adr/00039-using-golden-images.md) | Use organisation-approved golden base images for Docker containers | ci-cd | Standard |
| [ADR-00040](../adr/00040-github-team-assignment-via-entra-sso.md) | GitHub team membership managed through Azure Entra SSO, not manual assignment | repository-governance | Standard |
| [ADR-00041](../adr/00041-adopt-slos.md) | Define and measure Service Level Objectives for all production services | observability | Standard |
| [ADR-00042](../adr/00042-frontend-browser-support.md) | Support last 2 versions of Chrome, Firefox, Safari, Edge; no IE11 | frontend-architecture | Standard |
| [ADR-00046](../adr/00046-dependency-tiers.md) | Evaluate dependencies using a tier system (core, utility, convenience) with different approval requirements | dependency-management | Standard |
| [ADR-00047](../adr/00047-atlantis-for-terraform.md) | Use Atlantis for running Terraform plan/apply via pull requests | ci-cd | Standard |
| [ADR-00048](../adr/00048-cms-models-repository.md) | Contentful models managed in a dedicated repository | configuration-management | Guidance |
| [ADR-00049](../adr/00049-use-dayjs.md) | Use DayJS for date/time manipulation in frontend projects (not Moment.js) | frontend-architecture | Standard |
| [ADR-00051](../adr/00051-backfilling-kafka-topics.md) | Use internal endpoints to trigger Kafka topic backfills for data replay | event-driven-architecture | Guidance |
| [ADR-00052](../adr/00052-clean-up-inactive-github-users.md) | Inactive GitHub users are periodically removed from the organisation | repository-governance | Standard |
| [ADR-00056](../adr/00056-code-ownership-with-multiple-teams.md) | Use CODEOWNERS with team-based patterns when multiple teams contribute to a repo | repository-governance | Standard |
| [ADR-00057](../adr/00057-api-first-development.md) | All APIs must be designed in TypeSpec before implementation; TypeSpec is the single source of truth | api-design | Standard |
| [ADR-00058](../adr/00058-rds-shared-bounded-context.md) | Shared PostgreSQL RDS instances scoped to bounded contexts, not per-service | data-persistence | Standard |
| [ADR-00059](../adr/00059-public-api-development-process.md) | Workflow and governance for exposing APIs publicly via the API Gateway | api-design | Standard |
| [ADR-00060](../adr/00060-axon-framework-without-axon-server.md) | Use Axon Framework for CQRS/event sourcing but without Axon Server; use Kafka + PostgreSQL as alternatives | event-driven-architecture | Standard |
| [ADR-00061](../adr/00061-search-spring-boot-starter.md) | Use the Pax8 search Spring Boot starter for OpenSearch integration | search-and-discovery | Standard |
| [ADR-00062](../adr/00062-architecture-codeowners.md) | Architecture team has CODEOWNERS review on repo-specific best practice files | repository-governance | Standard |
| [ADR-00064](../adr/00064-public-certificate-management.md) | Follow the defined process for public certificate rotation and management | security | Standard |
| [ADR-00068](../adr/00068-rfc4180-for-csv-handling.md) | Use RFC4180 standard for all CSV document generation and parsing | api-design | Standard |
| [ADR-00069](../adr/00069-granular-engineering-access.md) | Engineering access follows least-privilege with granular role definitions | security | Standard |
| [ADR-00069](../adr/00069-isolate-axon-deadline-handling.md) | Use Quartz scheduler to isolate Axon deadline handling from aggregate lifecycle | event-driven-architecture | Guidance |
| [ADR-00074](../adr/00074-cursor-based-paging.md) | Prefer cursor-based pagination with infinite scroll for new user-facing list endpoints | api-design | Guidance |
| [ADR-00075](../adr/00075-admin-only-operational-endpoints.md) | Expose operational/admin endpoints via Spring Boot Actuator with restricted access | backend-architecture | Standard |
| [ADR-00076](../adr/00076-monolith-fga-client.md) | Use the fgaclient identity handler for Fine-Grained Authorization in the monolith | authentication | Standard |
| [ADR-00077](../adr/00077-vendor-shadow-entities.md) | Use shadow entities for vendor data in the purchasing domain | event-driven-architecture | Guidance |
| [ADR-00079](../adr/00079-audit-field-format.md) | Standardise audit fields (createdAt, updatedAt, createdBy, updatedBy) in API responses and events | api-design | Standard |
| [ADR-00080](../adr/00080-idempotency-key-header.md) | Use X-Idempotency-Key header for all mutation API endpoints | api-design | Standard |
| [ADR-00081](../adr/00081-api-error-response-format.md) | Use a standardised error response format across all APIs | error-handling | Standard |
| [ADR-00081](../adr/00081-user-multi-account-assignment.md) | Support users belonging to multiple organisations with account switching | multi-tenancy-ux | Guidance |
| [ADR-00082](../adr/00082-api-error-response-format.md) | Standardised error response format with ErrorType/ErrorCode enums and details array | api-design, error-handling | Standard |
| [ADR-00082](../adr/00082-slack-channel-standards.md) | Engineering teams follow naming conventions for Slack channels | work-management | Guidance |
| [ADR-00083](../adr/00083-organization-unified-accounts.md) | Organisations use unified account model for identity | authentication | Guidance |
| [RFC-0003](https://github.com/pax8/rfc/tree/main/0003) | Kafka Standards and Best Practices | event-driven-architecture | Standard |
| [RFC-0014](https://github.com/pax8/rfc/tree/main/0014) | Service Documentation Standards | repository-governance | Standard |
| [RFC-0022](https://github.com/pax8/rfc/tree/main/0022) / [RFC-0023](https://github.com/pax8/rfc/tree/main/0023) | REST API Guidelines | api-design | Standard |
| [RFC-0029](https://github.com/pax8/rfc/tree/main/0029) | Logging Best Practices | observability | Standard |
| [RFC-0058](https://github.com/pax8/rfc/tree/main/0058-architecture-and-design-process) | Architecture and Design Process | repository-governance | Standard |

## Standards by Codex Facet

### API Design
- **RFC-0022/0023**: REST API Guidelines - Standard
- **ADR-00007**: Domain Object Identifiers (UUIDs) - Standard
- **ADR-00057**: API First Development (TypeSpec) - Standard
- **ADR-00059**: Public API Development Process - Standard
- **ADR-00068**: RFC4180 for CSV Handling - Standard
- **ADR-00074**: Cursor-Based Paging - Guidance
- **ADR-00079**: Audit Field Format - Standard
- **ADR-00080**: Idempotency Key Header - Standard
- **ADR-00082**: API Error Response Format - Standard

### Authentication
- **ADR-00076**: Monolith FGA Client - Standard
- **ADR-00083**: Organization Unified Accounts - Guidance

### Backend Architecture
- **ADR-00016**: Adopt ktlint - Standard
- **ADR-00075**: Admin-Only Operational Endpoints - Standard

### CI/CD
- **ADR-00039**: Prefix ECR Image Tags - Standard
- **ADR-00039**: Using Golden Images - Standard
- **ADR-00047**: Atlantis for Terraform - Standard

### Configuration Management
- **ADR-00048**: CMS Models Repository - Guidance

### Data Persistence
- **ADR-00037**: MongoDB Usage - Guidance
- **ADR-00058**: RDS Shared Bounded Context - Standard

### Dependency Management
- **ADR-00025**: Remove version dependency variables - Standard
- **ADR-00046**: Dependency Tiers - Standard

### Error Handling
- **ADR-00081**: API Error Response Format - Standard

### Event-Driven Architecture
- **RFC-0003**: Kafka Standards and Best Practices - Standard
- **ADR-00051**: Backfilling Kafka Topics - Guidance
- **ADR-00060**: Axon Framework without Axon Server - Standard
- **ADR-00069**: Isolate Axon Deadline Handling - Guidance
- **ADR-00077**: Vendor Shadow Entities - Guidance

### Feature Toggles
- **ADR-00035**: Use Feature Flags - Guidance

### Frontend Architecture
- **ADR-00042**: Frontend Browser Support - Standard
- **ADR-00049**: Use DayJS - Standard

### Multi-Tenancy UX
- **ADR-00081**: User Multi-Account Assignment - Guidance

### Observability
- **RFC-0029**: Logging Best Practices - Standard
- **ADR-00026**: Span Name Prefix - Standard
- **ADR-00027**: Frontend Observability - Standard
- **ADR-00041**: Adopt SLOs - Standard

### Repository Governance
- **RFC-0014**: Service Documentation Standards - Standard
- **RFC-0058**: Architecture and Design Process - Standard
- **ADR-00034**: GitHub Repository Rulesets - Standard
- **ADR-00038**: Conventional Commits - Standard
- **ADR-00040**: GitHub Team Assignment via Entra SSO - Standard
- **ADR-00052**: Clean-up Inactive GitHub Users - Standard
- **ADR-00056**: Code Ownership with Multiple Teams - Standard
- **ADR-00062**: Architecture Codeowners - Standard

### Search and Discovery
- **ADR-00061**: Search Spring Boot Starter - Standard

### Security
- **ADR-00064**: Public Certificate Management - Standard
- **ADR-00069**: Granular Engineering Access - Standard

### Work Management
- **ADR-00001**: Use ADRs - Standard
- **ADR-00082**: Slack Channel Standards - Guidance
