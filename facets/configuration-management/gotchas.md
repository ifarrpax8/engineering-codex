# Configuration Management: Gotchas

Configuration management is deceptively simple but full of subtle pitfalls that cause production incidents, security vulnerabilities, and operational headaches. Understanding these common mistakes helps avoid them.

## Secrets Committed to Git

The most dangerous configuration mistake is committing secrets to version control. Once committed, secrets are in Git history forever, even if later removed. Attackers who gain repository access can extract secrets from historical commits.

Common scenarios include committing `.env` files with real credentials, hardcoding API keys in configuration files, and including passwords in `docker-compose.yml` files. Base64 encoding is not encryption—anyone can decode base64-encoded secrets.

Prevention requires multiple layers: `.gitignore` rules for environment files, pre-commit hooks that scan for secrets, and CI/CD pipeline scans. Use `.env.example` files with placeholder values to document required configuration without exposing secrets. Store real secrets in secrets management services, not in files.

If secrets are accidentally committed, rotate them immediately. Removing the file from Git doesn't remove it from history. Consider using tools like `git-filter-repo` to rewrite history, though this is disruptive for shared repositories.

## Configuration Drift Between Environments

Configuration drift occurs when environments have different configuration structures or properties. Staging might have a property that production doesn't, or production might use a different property name. This causes "worked in staging" bugs that don't manifest until production.

Drift often accumulates gradually. A developer adds a new property to staging configuration for testing and forgets to add it to production. Or a production-specific workaround creates a property that doesn't exist in staging. Over time, environments diverge.

Prevention requires maintaining configuration parity. Use template-based approaches where a base configuration is overlaid with environment-specific values. The same properties should exist in all environments, with only values differing. Automated tools can compare configuration structures and alert on drift.

Regular configuration audits help identify and fix drift before it causes incidents. Compare configuration files across environments and resolve differences. Use infrastructure-as-code practices to ensure configuration is defined consistently.

## Hardcoded Values That Should Be Configuration

Values that vary between environments or might need tuning are often hardcoded in application code. A timeout of 30000 milliseconds buried in a service class, a retry count of 3 hardcoded in a utility function, or a feature flag default hardcoded in a component.

These hardcoded values become impossible to tune without code changes and deployments. When production needs different values than development, teams must choose between maintaining separate code branches or accepting suboptimal behavior.

The solution is to externalize anything that might vary. If a value might need to change between environments or over time, it's configuration. When in doubt, externalize it. It's easier to remove unnecessary configuration than to retrofit externalization.

Code reviews should watch for hardcoded values that look like they might need to be configurable. Timeouts, retry counts, limits, and feature flags are common candidates for externalization.

## .env Files Not in .gitignore

The default `.env` file often gets committed to Git because developers forget to add it to `.gitignore`. This exposes local development credentials, API keys, and other secrets to the repository.

Even if `.env` is in `.gitignore`, variations like `.env.local`, `.env.development`, or `.env.production` might not be. Developers might create these files thinking they're safe, only to commit them accidentally.

Prevention requires comprehensive `.gitignore` rules. Use patterns like `.env*` to ignore all environment files, then explicitly allow `.env.example` if needed. Some teams use a more specific pattern like `.env.local` to be more precise.

Pre-commit hooks that scan for `.env` files can catch these mistakes before they're committed. CI/CD pipelines should also scan for environment files and fail builds if they're detected.

## Frontend Secrets Exposed in Bundle

Frontend applications often accidentally expose secrets by including them in environment variables prefixed with `VITE_` or similar build-time variables. Everything in the frontend JavaScript bundle is visible to users—there's no way to hide values in client-side code.

Common mistakes include API keys, authentication tokens, or database credentials set as `VITE_` environment variables. These values are compiled into the bundle and can be extracted by anyone who inspects the JavaScript.

The solution is to never put secrets in frontend configuration. If external APIs require authentication, use a backend-for-frontend pattern where the backend holds credentials and proxies requests. Frontend configuration should only contain non-sensitive values like public API endpoints or feature flags.

Code reviews should verify that no `VITE_` variables contain secrets. Automated scanning can detect common secret patterns in frontend configuration files.

## Missing Configuration Discovered at Runtime

Applications often start successfully but crash when the first request hits a code path that uses unconfigured services. This happens when configuration validation is incomplete or when optional configuration is actually required for certain features.

The problem is that startup validation doesn't catch all configuration issues. A service might start without a database URL if database access is lazy-loaded, only failing when the first database query occurs. Or a feature flag service might be optional at startup but required for certain user flows.

The solution is comprehensive startup validation. All required configuration should be validated at startup, not when first used. Use `@Validated` annotations and required property checks to ensure configuration is complete before the application accepts requests.

For truly optional configuration, applications should handle missing values gracefully. If a feature flag service is unavailable, the application should use safe defaults rather than crashing.

## Configuration Override Order Mistakes

Configuration systems have precedence hierarchies that determine which values override others. Mistakes in understanding this hierarchy cause configuration to be applied incorrectly.

For example, Spring Boot's property source precedence means that environment variables override property files, which override code defaults. But if an application reads a property file after setting environment variables, it might overwrite the environment variable values.

Understanding the precedence hierarchy is essential for debugging configuration issues. When a value isn't what's expected, check all configuration sources in precedence order. Use logging or debugging tools to see which values are actually being used.

Document the precedence hierarchy for your configuration system and ensure all team members understand it. This prevents confusion when configuration doesn't behave as expected.

## Kubernetes Secrets Not Actually Encrypted

Kubernetes Secrets are base64 encoded by default, not encrypted. Anyone with cluster access can decode them using `kubectl get secret <name> -o yaml` and base64 decoding. This is a common source of false security confidence.

Base64 encoding is reversible encoding, not encryption. It obfuscates values but provides no security. Secrets should be encrypted at rest using Kubernetes encryption at rest features, or stored in external secret management services.

For Git-stored secrets, use sealed-secrets which provides actual encryption, or external-secrets-operator to sync from encrypted secret stores. Don't rely on base64 encoding as security.

Production clusters should enable encryption at rest for Secrets. This ensures that even if someone gains access to etcd (Kubernetes' data store), secrets remain encrypted.

## Too Many Configuration Profiles

Configuration profiles enable environment-specific configuration, but too many profiles create a configuration matrix that's impossible to manage. Profiles like `local`, `dev`, `test`, `integration`, `staging`, `preprod`, `production`, and `demo` multiply configuration complexity.

Each profile combination needs testing. Each new property might need to be defined in multiple profiles. Configuration drift becomes inevitable as the number of profiles grows.

The solution is to minimize the number of profiles. Use environment variables for truly environment-specific values rather than creating profiles for every variation. Use profile groups or inheritance to combine related profiles.

Consider whether all those environments are necessary. Can `test` and `integration` share configuration? Can `preprod` and `staging` be the same? Reducing the number of environments reduces configuration complexity.

## Configuration Changes Requiring Full Restarts

Some configuration changes require full application restarts, making incident response slow. When configuration is the root cause of an incident, the ability to change it quickly is critical.

Applications that load all configuration at startup and don't support runtime refresh require redeployments for any configuration change. This can take minutes or hours, during which the incident continues.

The solution is to design applications to support runtime configuration changes where possible. Use Spring Boot Actuator refresh endpoints, or design configuration loading to support hot reloading. Not all configuration can be changed at runtime safely, but many values can be.

For configuration that must be changed via deployment, optimize deployment pipelines to enable fast rollbacks. The ability to quickly revert a configuration change is almost as important as the ability to change it quickly.

## Configuration Documentation Missing or Outdated

Configuration properties are often undocumented or documented incorrectly. Developers don't know what a property does, what values are valid, or what the default is. This leads to misconfiguration and debugging difficulties.

Outdated documentation is worse than no documentation—it provides incorrect information that misleads developers. Documentation that says a timeout is in seconds when it's actually in milliseconds causes serious bugs.

The solution is to generate documentation from code annotations where possible. Spring Boot's configuration processor generates metadata from `@ConfigurationProperties` classes. Keep documentation close to code so it's updated when code changes.

For manually maintained documentation, include it in code review checklists. When adding new configuration properties, require documentation updates. Regular audits can identify outdated documentation.

## Configuration Validation Too Permissive

Configuration validation that's too permissive allows invalid values that cause runtime errors. A URL property that accepts any string might allow malformed URLs that cause connection failures. A numeric property without range validation might allow negative values that cause logic errors.

Validation should be strict: reject invalid values at startup with clear error messages. Use type checking, format validation (like URL or email patterns), and range validation to ensure configuration is correct.

The balance is between being too strict (rejecting valid values) and too permissive (allowing invalid values). When in doubt, be strict—it's better to fail at startup with a clear error than to fail at runtime with a confusing error.

Test validation thoroughly. Verify that valid values are accepted, invalid values are rejected, and error messages are helpful. Edge cases like empty strings, null values, and boundary conditions should be tested.

## Configuration in Multiple Places

Configuration that's defined in multiple places creates confusion and inconsistency. A database URL might be defined in a property file, overridden by an environment variable, and also hardcoded as a fallback. When the value is wrong, it's unclear which source is actually being used.

The solution is to have a single source of truth for each configuration value, with a clear override hierarchy. Document which configuration sources are used and in what order. Use logging or debugging tools to show which values are actually loaded.

Avoid defining the same configuration in multiple places. If a value needs to be overridden, use the override mechanism rather than redefining it. This makes configuration behavior predictable and debuggable.
