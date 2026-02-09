# Security -- Best Practices

## Contents

- [Validate Input on the Server, Always](#validate-input-on-the-server-always)
- [Principle of Least Privilege](#principle-of-least-privilege)
- [Fail Securely](#fail-securely)
- [Keep Dependencies Updated](#keep-dependencies-updated)
- [Use Parameterized Queries](#use-parameterized-queries)
- [Encrypt Sensitive Data at Rest and in Transit](#encrypt-sensitive-data-at-rest-and-in-transit)
- [Log Security Events](#log-security-events)
- [Stack-Specific Security Practices](#stack-specific-security-practices)

Security best practices are principles that apply across technologies and frameworks. These practices provide a foundation for secure application development, complementing framework-specific security features and tooling. While implementation details vary by technology stack, the underlying principles remain constant.

## Validate Input on the Server, Always

Client-side validation improves user experience by providing immediate feedback, but it provides zero security. Attackers can bypass client-side validation by sending requests directly to APIs, using browser developer tools to modify JavaScript, or using tools like curl or Postman. Every API endpoint must validate all input parameters, headers, and body content on the server.

Server-side validation should occur at the API boundary, before data enters application logic. Validate type (ensuring data matches expected types), length (preventing buffer overflows and DoS attacks), format (ensuring data matches expected patterns), and range (ensuring numeric values fall within acceptable bounds). Use allowlist validation (accepting only known-good values) over denylist validation (rejecting known-bad values) when possible.

Input validation failures should return clear error messages to help developers debug issues, but avoid exposing internal implementation details that could aid attackers. Return generic error messages for authentication failures to prevent username enumeration attacks. Log detailed validation failures server-side for debugging while returning user-friendly messages to clients.

## Principle of Least Privilege

Every user, service, and process should have the minimum permissions needed to perform their function. Don't grant admin access when read-only access suffices. Don't run applications as root when a non-privileged user works. Don't grant database users write access when read access is sufficient.

Least privilege reduces the impact of security breaches. If an attacker compromises a low-privilege account, they can only access resources that account is permitted to access. If an attacker compromises an admin account, they can access everything. Limiting privileges limits the blast radius of compromises.

Apply least privilege at multiple levels: operating system users and groups, database users and roles, cloud IAM roles and policies, Kubernetes service accounts and RBAC, and application-level permissions. Review permissions regularly and remove unnecessary access. Automated permission auditing can identify over-privileged accounts and services.

## Fail Securely

When security controls fail, default to deny. If authentication fails, don't grant access. If authorization checks fail, don't allow the operation. If input validation fails, don't process the input. If encryption fails, don't store unencrypted data.

Error handling should not bypass security controls. Don't catch security exceptions and continue processing. Don't log security failures and then grant access anyway. Security failures should stop processing and return appropriate error responses.

Error messages should not expose sensitive information that helps attackers. Don't include stack traces, database error messages, file paths, or internal system details in error responses. Log detailed error information server-side for debugging, but return generic error messages to clients. Error messages should be consistent—don't reveal whether a username exists by returning different messages for "user not found" versus "invalid password."

## Keep Dependencies Updated

Dependencies introduce vulnerabilities. When vulnerabilities are discovered in dependencies, they affect all applications using those dependencies. The Log4Shell vulnerability (CVE-2021-44228) in Apache Log4j affected millions of Java applications worldwide, demonstrating the scale of dependency risk.

Automate dependency updates to keep dependencies current with security patches. Dependabot and Renovate create pull requests for dependency updates, allowing teams to review and test changes before merging. Enable automated updates for patch versions (security fixes) while requiring manual review for minor and major versions (potential breaking changes).

Dependency scanning identifies known vulnerabilities in dependencies. Run dependency scanning in CI/CD pipelines on every pull request, and block merges when critical or high-severity vulnerabilities are detected. Triage and patch critical vulnerabilities within days, not months. Don't let vulnerability backlogs accumulate—they represent unaddressed risk.

Maintain a software inventory listing all dependencies, their versions, and their purposes. Understand why each dependency is needed and whether alternatives exist. Regularly review dependencies and remove unused ones. Fewer dependencies mean fewer vulnerabilities.

## Use Parameterized Queries

Never concatenate user input into SQL queries, LDAP queries, or OS commands. Concatenation enables injection attacks where attackers provide malicious input that modifies query structure or executes arbitrary commands. Parameterized queries (prepared statements) separate query structure from data values, preventing injection attacks.

ORMs like JPA and Hibernate use parameterized queries by default for standard operations. However, native queries (`@Query` with `nativeQuery=true`) require explicit parameter binding. Use named parameters (`:paramName`) or positional parameters (`?`) and bind values explicitly. Never use string concatenation or interpolation in native queries.

If dynamic queries are necessary (e.g., building WHERE clauses based on user input), use query builders that support parameterized queries (JPA Criteria API, JOOQ) rather than string concatenation. Validate and sanitize any user input used to construct query structure, even with query builders.

The same principle applies to other contexts: use parameterized LDAP queries, parameterized OS command execution (when commands are necessary), and parameterized templating engines. Any place where user input influences structure is a potential injection point.

## Encrypt Sensitive Data at Rest and in Transit

Encryption protects data confidentiality by making it unreadable without decryption keys. Encrypt sensitive data both at rest (in databases, file systems, backups) and in transit (over networks). Encryption at rest protects against data theft from compromised storage, while encryption in transit protects against interception during transmission.

Use TLS (Transport Layer Security) for all network communication. TLS 1.2 is the minimum acceptable version, with TLS 1.3 preferred. Configure TLS with strong cipher suites and disable weak ones. Use certificate management to automate certificate provisioning and renewal, ensuring certificates don't expire and create security gaps.

Encrypt databases using Transparent Data Encryption (TDE) or storage-level encryption. Cloud-managed databases typically include encryption at rest by default. For self-managed databases, enable encryption explicitly. Encrypt file storage using server-side encryption (S3, Azure Blob Storage) or client-side encryption for additional protection.

Use strong, current encryption algorithms. Avoid deprecated algorithms (MD5, SHA-1, DES, RC4) and use recommended algorithms (AES-256, SHA-256, RSA-2048 or larger, ECDSA). Encryption algorithms become weaker over time as computing power increases and attacks improve—stay current with cryptographic best practices.

Manage encryption keys securely using key management services (AWS KMS, Azure Key Vault, HashiCorp Vault). Never store encryption keys alongside encrypted data. Rotate encryption keys regularly and use key versioning to support rotation without service interruption.

## Log Security Events

Security event logging enables detection, investigation, and response to security incidents. Log authentication attempts (success and failure), authorization failures, input validation failures, admin actions, and security configuration changes. Logs should include timestamps, user identifiers, IP addresses, request details, and outcomes.

Security logs should be stored securely and protected from tampering. Use append-only log storage or cryptographic signing to detect log tampering. Retain security logs for an appropriate period (compliance requirements may mandate specific retention periods) and ensure logs are searchable for incident investigation.

Don't log sensitive data in security logs. Don't log passwords, authentication tokens, credit card numbers, or full PII. Log enough information to investigate incidents without exposing sensitive data. Implement log scrubbing to remove sensitive data automatically if it's accidentally included.

Security Information and Event Management (SIEM) systems aggregate security logs from multiple sources, correlate events, and detect suspicious patterns. SIEM systems can identify brute force attacks, privilege escalation attempts, and data exfiltration by analyzing log patterns. However, SIEM systems require proper configuration and tuning to reduce false positives.

## Stack-Specific Security Practices

### Spring Security

Use `@PreAuthorize` and `@PostAuthorize` annotations for method-level security, ensuring authorization is enforced even if developers forget to add checks. Configure `SecurityFilterChain` beans explicitly rather than relying on auto-configuration, ensuring all security settings are intentional and documented.

Configure CORS using `CorsConfigurationSource` beans with explicit allowed origins, methods, and headers. Don't use `Access-Control-Allow-Origin: *` for authenticated APIs. Configure CORS at the security filter chain level to ensure consistent application across endpoints.

CSRF protection is essential for stateful session-based authentication but should be disabled for stateless JWT bearer token APIs. Understand why CSRF protection is needed (cookie-based authentication is vulnerable to CSRF) and why it's not needed (bearer tokens in headers are not vulnerable to CSRF) before disabling it.

Use Spring Security's password encoding (BCrypt, Argon2) rather than implementing custom password hashing. Spring Security handles salt generation, iteration counts, and secure comparison automatically. Never store passwords in plain text or use weak hashing algorithms (MD5, SHA-1).

### Kotlin

Use `require()` functions for input validation at function boundaries. `require()` throws `IllegalArgumentException` with clear messages when preconditions aren't met, making validation failures explicit. Use `requireNotNull()` for nullable parameters that must be non-null.

Leverage Kotlin's type system for security. Use sealed classes and enums to represent restricted sets of values, preventing invalid states. Use data classes with validation in constructors or factory functions to ensure data integrity.

Be cautious with `inline` functions and reified type parameters when dealing with sensitive data, as they can affect code obfuscation and security analysis. Prefer explicit type parameters when security is a concern.

### Vue 3 / React

Sanitize dynamic HTML content. Vue's `v-html` directive and React's `dangerouslySetInnerHTML` prop can introduce XSS vulnerabilities if content isn't sanitized. Use HTML sanitization libraries (DOMPurify) or avoid dynamic HTML entirely by using template-based rendering.

Configure Content Security Policy (CSP) headers at the server or CDN level, not in client-side code. CSP headers restrict where resources can load from, preventing XSS attacks. Client-side code cannot reliably enforce CSP—it must be configured server-side.

Store authentication tokens securely. `localStorage` is accessible to any JavaScript on the page, making it vulnerable to XSS attacks. Prefer `httpOnly` cookies for token storage, which are inaccessible to JavaScript. If `localStorage` must be used (e.g., for SPAs without backend cookie support), keep token lifetimes short and implement robust XSS prevention.

Validate input on the client for user experience, but never rely on client-side validation for security. All validation must be enforced server-side. Client-side validation provides immediate feedback but can be bypassed.

### Kubernetes

Use NetworkPolicies to control pod-to-pod traffic, implementing network segmentation and defense in depth. NetworkPolicies define which pods can communicate with which other pods, limiting the blast radius of compromises. Default to deny-all and explicitly allow required communication.

Apply Pod Security Standards to enforce security policies at the pod level. Pod Security Standards restrict running as root, using host namespaces, and accessing host filesystems. Use Pod Security Standards in enforcement mode to block non-compliant pods.

Encrypt Kubernetes Secrets at rest using encryption providers. By default, Kubernetes Secrets are base64-encoded but not encrypted. Enable encryption at rest to protect secrets from storage compromise. Use external key management services (AWS KMS, Azure Key Vault) for key management.

Use RBAC (Role-Based Access Control) to restrict cluster access. Don't grant cluster-admin access unnecessarily. Create ServiceAccounts with minimal permissions for applications. Review RBAC policies regularly and remove unnecessary access.

These stack-specific practices complement language-agnostic security principles. Framework features can simplify secure implementation, but they don't replace understanding underlying security concepts. Use framework features correctly and understand what security they provide and what they don't.
