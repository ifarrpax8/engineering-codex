# Configuration Management: Options

Configuration management requires choosing tools and patterns that balance simplicity, flexibility, security, and operational requirements. This document provides decision guidance for common configuration management choices.

## Recommended Configuration Stack

For most applications using the assumed tech stack (Java/Kotlin Spring Boot, Vue 3/React, Docker, Kubernetes, GitHub Actions), the following configuration stack is recommended:

**Backend Configuration**: Spring Boot profiles with `application.yml` files, `@ConfigurationProperties` classes for type-safe configuration, and environment variable overrides for containerized deployments. This provides a good balance of simplicity and flexibility without requiring additional infrastructure.

**Frontend Configuration**: Vite `.env` files for build-time configuration (API base URLs, feature flag defaults), with a runtime configuration endpoint for values that must change without rebuilding. This enables both build-time optimization and runtime flexibility.

**Secrets Management**: A dedicated secrets management service (HashiCorp Vault or cloud provider equivalent) integrated with Kubernetes via `external-secrets-operator`. This provides proper encryption, rotation, and audit capabilities while maintaining Kubernetes-native deployment patterns.

**Infrastructure Configuration**: Helm values files per environment for Kubernetes deployments, with Terraform variables for infrastructure provisioning. This enables configuration-as-code practices with environment-specific overrides.

This stack provides good defaults for most scenarios while remaining flexible enough to adapt to specific requirements. Teams should evaluate their specific needs and adjust accordingly.

## Secrets Management Options

Secrets require special handling beyond standard configuration. Three primary approaches are available, each with different trade-offs.

### HashiCorp Vault

**Strengths**: Full-featured secrets management with dynamic secrets generation, encryption as a service, detailed audit logging, and lease-based automatic rotation. Vault can generate database credentials on demand with automatic revocation, eliminating long-lived credentials. It supports multiple authentication backends and integrates well with Kubernetes via the Vault Agent Injector.

**Weaknesses**: Requires operational expertise to run and maintain. Vault clusters need high availability, backup, and monitoring. The learning curve is steeper than managed services. For smaller teams, the operational overhead may outweigh the benefits.

**Best For**: Organizations with dedicated platform teams, multiple applications requiring secrets, compliance requirements for audit logging, or need for dynamic secrets. Also suitable for multi-cloud deployments where cloud-specific services aren't appropriate.

**Integration**: Use `external-secrets-operator` to sync Vault secrets into Kubernetes Secrets, or use Vault Agent Injector for automatic secret injection into pods.

### Cloud Provider Secrets Managers

**AWS Secrets Manager / Azure Key Vault / GCP Secret Manager**: Managed secrets services integrated with their respective cloud platforms. They provide automatic rotation for supported services (like RDS databases), IAM-based access control, and simplified operations compared to self-hosted Vault.

**Strengths**: No infrastructure to operate, automatic rotation for common services, tight cloud platform integration, and pay-per-use pricing. Simpler to adopt than Vault for teams already using a single cloud provider.

**Weaknesses**: Vendor lock-in to a specific cloud provider, less flexible than Vault for custom use cases, and may not support all secret types that Vault does. Cost can add up with many secrets or high access rates.

**Best For**: Organizations heavily invested in a single cloud provider, teams without platform engineering expertise, or applications with straightforward secrets management needs. Ideal when automatic rotation for cloud services (RDS, etc.) is a primary requirement.

**Integration**: Use `external-secrets-operator` with cloud provider backends to sync secrets into Kubernetes, or access secrets directly via cloud SDKs in application code.

### Kubernetes Secrets with Sealed-Secrets

**Sealed-Secrets**: Encrypts secrets for Git storage using public-key cryptography. Secrets are encrypted with a public key and can only be decrypted by the Sealed-Secrets controller with the private key. This enables version-controlled secrets with proper encryption.

**Strengths**: Simple to adopt, no external services required, enables Git-based secret management with encryption. Good for teams already using Kubernetes who want to avoid additional infrastructure.

**Weaknesses**: Less feature-rich than Vault or cloud secrets managers. No automatic rotation, limited audit capabilities, and requires managing the Sealed-Secrets controller. The private key is a critical secret that must be protected.

**Best For**: Smaller deployments, teams comfortable with Kubernetes but not ready for Vault, or scenarios where Git-based secret management is preferred. Good stepping stone before adopting more sophisticated secrets management.

**Integration**: Encrypt secrets using the Sealed-Secrets CLI, commit encrypted secrets to Git, and the Sealed-Secrets controller decrypts them into Kubernetes Secrets.

### Decision Matrix: Secrets Management

| Criteria | Vault | Cloud Provider | Sealed-Secrets |
|----------|-------|----------------|----------------|
| Operational Complexity | High | Low | Medium |
| Feature Richness | Very High | High | Medium |
| Multi-Cloud Support | Yes | No | Yes |
| Automatic Rotation | Yes (lease-based) | Yes (service-specific) | No |
| Audit Logging | Excellent | Good | Limited |
| Cost | Infrastructure + Operational | Pay-per-use | Infrastructure Only |
| Learning Curve | Steep | Moderate | Moderate |

**Recommendation**: Start with cloud provider secrets managers if heavily invested in a single cloud. Migrate to Vault as needs grow (multiple clouds, dynamic secrets, advanced audit requirements). Use Sealed-Secrets as an intermediate step or for simpler deployments.

## Runtime Configuration Options

Applications need mechanisms to load configuration at runtime. Three primary approaches are available, with different trade-offs between simplicity and capabilities.

### Environment Variables

**Description**: Configuration provided as environment variables, either set directly or injected from Kubernetes ConfigMaps/Secrets. Applications read environment variables at startup.

**Strengths**: Universal support across all languages and frameworks, simple to understand and debug, no additional infrastructure required. Works well with containerized deployments where ConfigMaps and Secrets are naturally exposed as environment variables.

**Weaknesses**: No centralized management, difficult to update without pod restarts, no built-in validation or documentation. Configuration changes require redeployment or pod restarts.

**Best For**: Small to medium deployments, applications with stable configuration, or teams prioritizing simplicity over advanced features. Ideal when configuration changes infrequently.

**Implementation**: Spring Boot supports environment variables via relaxed binding. Frontend applications can use build-time environment variables with Vite's `VITE_` prefix.

### Spring Cloud Config Server

**Description**: Centralized configuration server that stores configuration in Git repositories. Services fetch configuration at startup and can refresh it at runtime via Actuator endpoints.

**Strengths**: Centralized management, version-controlled configuration, runtime refresh without full restarts, encryption support, and profile-based configuration. Good for organizations with many microservices sharing configuration.

**Weaknesses**: Additional infrastructure to operate and maintain, single point of failure if not highly available, and requires applications to be designed for configuration refresh. More complex than environment variables.

**Best For**: Large microservices deployments, organizations needing centralized configuration management, or scenarios where configuration changes frequently and runtime updates are valuable.

**Implementation**: Deploy Spring Cloud Config Server, store configuration in Git, configure services to fetch from Config Server, and use Actuator refresh endpoints for runtime updates.

### Kubernetes ConfigMaps with File Mounting

**Description**: Configuration stored in Kubernetes ConfigMaps and mounted as files in pod filesystems. Applications read configuration files at startup or watch for changes.

**Strengths**: Kubernetes-native, no additional infrastructure, can be updated without redeploying (with application support for file watching), and integrates well with GitOps workflows.

**Weaknesses**: Requires applications to support file-based configuration and file watching for updates. Less flexible than environment variables for some frameworks. Updates may require pod restarts depending on application design.

**Best For**: Kubernetes-native deployments, teams using GitOps practices, or applications that prefer file-based configuration over environment variables.

**Implementation**: Create ConfigMaps from YAML files, mount them as volumes in pod specifications, and configure applications to read from mounted files. Use tools like Reloader for automatic pod restarts on ConfigMap changes.

### Decision Matrix: Runtime Configuration

| Criteria | Environment Variables | Spring Cloud Config | Kubernetes ConfigMaps |
|----------|----------------------|---------------------|----------------------|
| Simplicity | Very High | Low | Medium |
| Centralized Management | No | Yes | Partial |
| Runtime Updates | No (restart required) | Yes | Yes (with app support) |
| Infrastructure Overhead | None | High | None |
| Kubernetes Integration | Excellent | Good | Native |
| Multi-Service Sharing | Difficult | Easy | Medium |

**Recommendation**: Start with environment variables for simplicity. Adopt Spring Cloud Config Server if centralized management becomes valuable (many services, shared configuration). Use ConfigMaps for Kubernetes-native deployments preferring file-based configuration.

## Evaluation Criteria

When evaluating configuration management options, consider these criteria:

**Operational Complexity**: How much infrastructure and expertise is required? Simpler solutions reduce operational burden but may lack advanced features.

**Security**: Does the solution properly handle secrets? Are values encrypted at rest and in transit? Does it support access controls and audit logging?

**Flexibility**: Can the solution adapt to changing requirements? Does it support multiple environments, runtime updates, and various configuration types?

**Developer Experience**: Is the solution easy for developers to use? Does it provide good tooling, documentation, and error messages?

**Scalability**: Does the solution work as the number of services and environments grows? Can it handle high rates of configuration access?

**Integration**: How well does it integrate with existing tooling (CI/CD, Kubernetes, cloud providers)? Does it require significant changes to application code?

## Recommendation Guidance

**For New Projects**: Start with the simplest solution that meets requirements. Use environment variables with Spring Boot `@ConfigurationProperties` for backend, Vite `.env` files for frontend, and cloud provider secrets managers for secrets. This provides a solid foundation that can evolve as needs grow.

**For Existing Projects**: Evaluate current pain points. If configuration drift is a problem, invest in template-based approaches and configuration parity. If secrets management is inadequate, prioritize adopting a proper secrets management service. If configuration changes are slow, consider runtime configuration refresh capabilities.

**For Large Organizations**: Consider centralized configuration management (Spring Cloud Config Server) and comprehensive secrets management (Vault) to reduce operational overhead across many services. Invest in tooling and automation to make configuration management scalable.

**For Regulated Industries**: Prioritize audit logging, access controls, and configuration change tracking. Vault provides excellent audit capabilities. Ensure all configuration changes are reviewable and auditable.

## Synergies with Other Facets

Configuration management integrates closely with other engineering facets:

**CI/CD**: Configuration should be promoted through environments alongside code. CI/CD pipelines should validate configuration, test with environment-specific values, and deploy configuration changes. See the [CI/CD facet](../ci-cd/) for pipeline configuration practices.

**Security**: Secrets management is a security concern. Proper secrets handling, rotation, and access controls are essential. See the [Security facet](../security/) for comprehensive security practices.

**Feature Toggles**: Feature flags are a form of configuration. Runtime feature flag services enable configuration changes without deployments. See the [Feature Toggles facet](../feature-toggles/) for feature flag patterns.

**Observability**: Configuration changes should be observable. Track configuration-related metrics, log configuration loading, and monitor for configuration drift. See the [Observability facet](../observability/) for monitoring practices.

## Evolution Triggers

Configuration management approaches should evolve as needs change. Consider these triggers for reassessment:

**Scale Triggers**: When the number of services exceeds what can be managed manually, consider centralized configuration management. When secrets count grows significantly, evaluate dedicated secrets management services.

**Compliance Triggers**: When audit requirements increase, adopt solutions with comprehensive audit logging. When compliance mandates encryption, ensure all secrets are properly encrypted.

**Incident Triggers**: If configuration-related incidents are frequent, invest in better validation, testing, and management practices. If recovery from configuration issues is slow, consider runtime configuration update capabilities.

**Team Growth Triggers**: As teams grow, centralized configuration management becomes more valuable. As expertise increases, more sophisticated solutions become feasible.

**Technology Triggers**: When adopting new technologies (new cloud providers, container orchestration platforms), reassess configuration management to leverage platform-native capabilities.
