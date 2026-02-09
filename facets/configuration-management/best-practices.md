# Configuration Management: Best Practices

Configuration management best practices ensure that applications are maintainable, secure, and operable across diverse environments. These practices apply across technology stacks, though implementation details vary.

## Externalize Everything That Varies

The fundamental principle of configuration management is to externalize any value that changes between environments. This includes database URLs, API endpoints, feature flags, timeouts, retry counts, log levels, and any parameter that might need adjustment without code changes.

Hardcoded values become technical debt. A timeout of 30000 milliseconds buried in a service class cannot be tuned for production without a code change and deployment. A retry count of 3 hardcoded in a utility function becomes impossible to adjust when external services are unreliable. Externalizing these values enables operational tuning and faster incident response.

The test for whether something should be configuration is simple: if it might need to change between environments or over time without a code change, it's configuration. When in doubt, externalize it. It's easier to remove unnecessary configuration than to retrofit externalization into hardcoded values.

## Use Typed, Validated Configuration

Configuration should be type-safe and validated. Scattering string-based configuration access throughout code makes it easy to introduce typos, type mismatches, and missing configuration that isn't discovered until runtime.

Spring Boot's `@ConfigurationProperties` provides type safety, IDE autocomplete, and runtime validation. Instead of using `@Value("${database.url}")` throughout the codebase, create a `DatabaseProperties` class with a typed `url` property. This enables compile-time checking, IDE support, and centralized validation.

Validation should happen at startup, not at runtime when configuration is first used. Use validation annotations like `@NotNull`, `@Min`, `@Max`, `@Pattern`, and `@Valid` to ensure configuration is correct before the application starts accepting requests. Fail fast with clear error messages rather than discovering problems when the first request hits broken code.

## Fail Fast on Missing Configuration

Applications should validate all required configuration at startup and fail immediately with clear error messages if configuration is missing or invalid. Discovering missing configuration at runtime when the first request hits a code path is too late—the application is already running and potentially serving requests.

Startup validation should check that all required properties are present, that values are within valid ranges, that URLs are well-formed, and that any other constraints are satisfied. Error messages should clearly identify which property is missing or invalid and what values are acceptable.

This principle extends to dependencies on external configuration services. If an application requires a feature flag service to be available, it should fail at startup if the service is unreachable, not when the first feature flag check occurs. This makes configuration problems immediately visible and prevents partial application startup that leads to confusing runtime errors.

## Never Commit Secrets

Secrets must never be committed to version control, even if encrypted or encoded. Once committed, secrets are in Git history forever, even if later removed. Base64 encoding is not encryption—anyone with repository access can decode base64-encoded secrets.

Environment-specific files like `.env.local` should be in `.gitignore`. Use `.env.example` files with placeholder values to document required configuration without exposing real values. Secrets should come from secrets management services like Vault or AWS Secrets Manager, not from environment variables defined in committed configuration files.

Pre-commit hooks should scan for potential secrets using tools like `git-secrets` or `truffleHog`. These tools can detect common secret patterns and prevent accidental commits. CI/CD pipelines should also scan for secrets and fail builds if secrets are detected in committed files.

## Maintain Environment Parity

Environments should differ only in configuration values, not in configuration structure. The same property files, the same configuration classes, and the same validation rules should apply across all environments. Only the actual values should differ: a staging database URL instead of a production database URL, but the same property name and structure.

This parity enables reliable testing. Bugs that exist in production will reproduce in staging if environments have the same configuration structure. Configuration drift—where environments have different properties or structures—causes "worked in staging" bugs that don't manifest until production.

Use template-based configuration approaches where a base configuration is overlaid with environment-specific values. Helm values files, Kustomize overlays, or Spring Boot profiles enable this pattern. The base configuration defines structure; environment-specific files provide values.

## Document Every Configuration Property

Every configuration property should be documented with its description, type, default value, valid range or constraints, and example values. This documentation should be accessible to developers and operators, ideally generated automatically from code annotations.

Spring Boot's configuration processor generates metadata from `@ConfigurationProperties` classes when `spring-boot-configuration-processor` is included as a dependency. This metadata enables IDE autocomplete and can generate documentation. Similar tooling exists for other frameworks.

Documentation should explain not just what a property does, but why it exists and when it might need to be changed. A timeout property should document what operation it controls, what the implications of changing it are, and what typical values look like in different environments.

## Configuration as Code

All non-secret configuration should be stored in version control. This includes Helm values files, Terraform variables, Kubernetes ConfigMaps (as YAML files), and application property files. Configuration changes should go through the same review process as code changes.

Version-controlled configuration provides audit trails, enables rollback, and makes configuration drift visible through diff tools. It also enables infrastructure-as-code practices where configuration changes are tested and validated before deployment.

Configuration should be organized alongside application code when it's application-specific, or in dedicated configuration repositories when it's shared across multiple applications. The key is that configuration is versioned, reviewed, and auditable.

## Stack-Specific Practices

### Spring Boot

Use `@ConfigurationProperties` with `@Validated` for type-safe, validated configuration. Group related properties into dedicated classes rather than scattering `@Value` annotations. Use `spring.config.import` to import configuration from external sources like Spring Cloud Config Server.

Leverage Spring Boot's relaxed binding to support both property file format (`spring.datasource.url`) and environment variable format (`SPRING_DATASOURCE_URL`). Use profile groups to combine related profiles and reduce profile complexity.

Enable configuration metadata generation with `spring-boot-configuration-processor` to provide IDE autocomplete and documentation. Use `@ConfigurationPropertiesScan` to automatically discover configuration classes.

### Vite and Frontend Builds

Prefix client-exposed environment variables with `VITE_` to make it explicit which variables are included in the bundle. Use `import.meta.env` to access configuration values in application code.

Use mode-based `.env` files (`.env.development`, `.env.production`) for environment-specific values. Keep `.env.local` in `.gitignore` for local overrides. Commit `.env.example` with placeholder values to document required configuration.

Never expose secrets in frontend configuration. Everything prefixed with `VITE_` is included in the client bundle and visible to users. Use backend-for-frontend patterns for any functionality requiring secrets.

### Kubernetes

Use ConfigMaps for non-sensitive configuration and Secrets for sensitive data. Mount ConfigMaps and Secrets as environment variables or files based on application needs. Use `external-secrets-operator` to sync secrets from external stores like Vault or AWS Secrets Manager.

Enable encryption at rest for Kubernetes Secrets in production clusters. Consider sealed-secrets for Git-stored encrypted secrets, or external-secrets-operator for syncing from dedicated secret management services.

Use Kustomize overlays or Helm values files for per-environment configuration. Maintain a base configuration with environment-specific overlays to ensure structural consistency while allowing value differences.

### Gradle Build Configuration

Use `gradle.properties` for build configuration that varies between developers or CI environments. Use `buildSrc` for shared build logic and custom tasks. Use version catalogs for centralized dependency version management.

Keep build configuration externalized and documented. Build properties that affect build output (like Java version or build flags) should be configurable without modifying build files.

## Configuration Change Management

Configuration changes should follow the same rigor as code changes: review, test, and gradual rollout. Significant configuration changes should be tested in non-production environments first, then gradually rolled out to production.

Use feature flags or canary deployments for high-risk configuration changes. This enables immediate rollback if the change causes issues. Monitor application metrics after configuration changes to detect regressions.

Maintain change logs or commit messages that explain why configuration was changed. This provides context for future debugging and helps identify configuration changes that might have caused incidents.

## Configuration Monitoring and Alerting

Monitor configuration-related metrics: configuration load failures, validation errors, missing required properties, and configuration change frequency. Alert on configuration problems that indicate potential application issues.

Track configuration drift between environments. Automated tools can compare configuration structures across environments and alert when drift is detected. This enables proactive fixes before drift causes incidents.

Monitor secrets rotation compliance. Track which secrets are approaching expiration and ensure they're rotated according to policy. Stale secrets are a security risk and compliance violation.

## Gradual Configuration Migration

When migrating to new configuration systems or patterns, do so gradually. Support both old and new configuration formats during a transition period, then deprecate old formats with clear migration paths.

Provide migration guides and tooling to help teams adopt new configuration practices. Automate migration where possible to reduce manual effort and errors. Monitor adoption to identify teams that need additional support.

## Configuration Security

Beyond never committing secrets, configuration systems should enforce access controls. Not everyone should be able to change production configuration. Use role-based access control to limit who can modify configuration in each environment.

Audit all configuration changes. Know who changed what configuration, when, and why. This audit trail is essential for compliance and for debugging configuration-related incidents.

Encrypt sensitive configuration at rest and in transit. Use TLS for configuration service communication. Use encryption at rest for secrets storage. Don't rely on base64 encoding or other reversible encoding as security.
