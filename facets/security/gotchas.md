# Security -- Gotchas

## Contents

- [Storing Secrets in Environment Variables in Source Control](#storing-secrets-in-environment-variables-in-source-control)
- [CORS Misconfiguration](#cors-misconfiguration)
- [Client-Side Authorization](#client-side-authorization)
- [SQL Injection in Native Queries](#sql-injection-in-native-queries)
- [JWT Stored in localStorage](#jwt-stored-in-localstorage)
- [Missing Rate Limiting](#missing-rate-limiting)
- [Logging Sensitive Data](#logging-sensitive-data)
- [Overly Detailed Error Messages](#overly-detailed-error-messages)
- [Ignoring Dependency Vulnerabilities](#ignoring-dependency-vulnerabilities)
- [Disabled CSRF Protection Without Understanding](#disabled-csrf-protection-without-understanding)
- [Hardcoded Cryptographic Keys](#hardcoded-cryptographic-keys)

Common security pitfalls that seem reasonable at first but create vulnerabilities. These are the mistakes that slip through code reviews and seem harmless until they're exploited.

## Storing Secrets in Environment Variables in Source Control

**The trap**: Committing `.env` files to git, or including secrets in `docker-compose.yml` files that are committed. Environment variables feel like configuration, not code, so it's easy to forget they contain secrets.

**Why it's wrong**: Once secrets are in version control, they're effectively public. Even if repositories are private, anyone with access can view history. Repository leaks, insider threats, or accidental public exposure make committed secrets accessible to attackers. Git history is permanent—removing secrets from the latest commit doesn't remove them from history.

**The fix**: Use `.gitignore` to exclude `.env` files and any files containing secrets. Use secrets management systems (HashiCorp Vault, AWS Secrets Manager) for production secrets. For local development, use `.env.example` files with placeholder values, and document that developers must create their own `.env` files. Never commit actual secrets, even in private repositories.

**Detection**: Secret scanning tools (git-secrets, truffleHog, GitHub secret scanning) can detect committed secrets. Integrate secret scanning into pre-commit hooks and CI/CD pipelines to catch secrets before they're committed.

## CORS Misconfiguration

**The trap**: Using `Access-Control-Allow-Origin: *` (allow all origins) with `Access-Control-Allow-Credentials: true` (allow cookies/authentication). This combination is explicitly forbidden by browsers, but sometimes misconfigured server responses attempt it anyway.

**Why it's wrong**: Even if browsers reject this combination, overly permissive CORS configurations allow any website to make authenticated requests to your API. If CORS allows `*` or includes attacker-controlled origins, malicious websites can make requests on behalf of users, potentially accessing sensitive data or performing actions.

**The fix**: Configure CORS with explicit allowed origins. List exact frontend domains that should access the API. Don't use wildcards for authenticated APIs. In Spring Security, use `CorsConfigurationSource` with specific origins. Verify CORS configuration by testing from different origins and ensuring only allowed origins succeed.

**When it's acceptable**: Public APIs that don't require authentication can use `Access-Control-Allow-Origin: *` safely, but even then, consider restricting to known origins if possible. For authenticated APIs, always use specific origins.

## Client-Side Authorization

**The trap**: Hiding UI elements based on user permissions but not enforcing authorization on the server. The UI shows or hides buttons, but the underlying API endpoints don't check permissions.

**Why it's wrong**: Users can call APIs directly, bypassing UI restrictions. Browser developer tools, curl, Postman, or custom scripts can make requests directly to APIs. If authorization isn't enforced server-side, users can access resources they shouldn't.

**The fix**: Enforce all authorization checks on the server. Every API endpoint must verify that the authenticated user has permission to perform the requested operation. Use framework features like Spring Security's `@PreAuthorize` to ensure authorization is enforced even if developers forget to add checks. Client-side authorization is for user experience only—it improves UX by hiding unavailable options, but it provides no security.

**Testing**: Test authorization by making requests with different user accounts and roles. Verify that users cannot access resources they shouldn't, even when making direct API calls. Automated authorization tests should verify server-side enforcement.

## SQL Injection in Native Queries

**The trap**: Using JPA native queries (`@Query` with `nativeQuery=true`) and concatenating user input into the SQL string instead of using parameter binding.

**Why it's wrong**: JPA and Hibernate protect standard queries automatically, but native queries require explicit parameter binding. If you concatenate user input into native SQL strings, you're vulnerable to SQL injection attacks. Attackers can provide malicious input that modifies query structure or executes arbitrary SQL commands.

**The fix**: Always use parameterized native queries. Use named parameters (`:paramName`) or positional parameters (`?`) and bind values using `@Param` annotations or method parameters. Never use string concatenation or interpolation in native queries, even with `String.format()` or template strings.

**Example**: Instead of `@Query("SELECT * FROM users WHERE name = '" + name + "'", nativeQuery=true)`, use `@Query("SELECT * FROM users WHERE name = :name", nativeQuery=true)` and bind the `name` parameter.

## JWT Stored in localStorage

**The trap**: Storing JWTs in `localStorage` for convenience, especially in SPAs where cookie handling can be complex.

**Why it's wrong**: `localStorage` is accessible to any JavaScript running on the page. If your application has an XSS vulnerability (or a third-party script is compromised), attackers can steal JWTs from `localStorage`. Once stolen, JWTs can be used to impersonate users until they expire.

**The fix**: Store JWTs in `httpOnly` cookies, which are inaccessible to JavaScript. `httpOnly` cookies prevent XSS attacks from stealing tokens. Configure CORS appropriately to allow cookie-based authentication. If `localStorage` must be used (e.g., for SPAs without backend cookie support), keep token lifetimes very short (15 minutes or less) and implement robust XSS prevention (CSP headers, input sanitization).

**Trade-off**: `httpOnly` cookies require backend support and CORS configuration, which can be more complex than `localStorage`. However, the security benefit outweighs the complexity. For SPAs, consider using a backend proxy that handles cookie-based authentication and forwards requests to APIs.

## Missing Rate Limiting

**The trap**: No rate limits on login, registration, or password reset endpoints. These endpoints are prime targets for brute force and credential stuffing attacks.

**Why it's wrong**: Without rate limiting, attackers can make unlimited login attempts, trying common passwords or credential lists from data breaches. Credential stuffing attacks use automated tools to test stolen credentials across multiple sites. Rate limiting makes these attacks impractical by limiting the number of attempts.

**The fix**: Implement rate limiting on authentication endpoints. Limit login attempts per IP address (e.g., 5 attempts per 15 minutes) and per username (e.g., 5 attempts per 15 minutes per username). Use exponential backoff or account lockouts after repeated failures. Consider CAPTCHA after a few failed attempts to prevent automated attacks.

**Implementation**: Use rate limiting libraries (Spring Security rate limiting, Redis-based rate limiting) or API gateway rate limiting. Rate limits should be configurable and appropriate for legitimate use cases—don't set limits so low that they impact legitimate users.

## Logging Sensitive Data

**The trap**: Logging passwords, authentication tokens, credit card numbers, or full PII in log files. Logging seems harmless, but logs are often accessible to many people and persist for long periods.

**Why it's wrong**: Once sensitive data is in logs, it's effectively exposed. Logs are often stored in centralized systems accessible to developers, operators, and security teams. Log files can be leaked, backed up to insecure locations, or accessed by attackers who compromise logging systems. Compliance requirements (GDPR, PCI DSS) may be violated if sensitive data is logged.

**The fix**: Never log sensitive data. Don't log passwords, tokens, credit card numbers, or full PII. Log enough information to debug issues without exposing sensitive data. Implement log scrubbing to automatically remove sensitive data if it's accidentally included. Use structured logging with fields that can be filtered or redacted.

**Detection**: Use log analysis tools to scan for patterns matching sensitive data (credit card numbers, SSNs, API keys). Implement automated log scanning to detect accidental sensitive data logging.

## Overly Detailed Error Messages

**The trap**: Returning specific error messages like "User not found" versus "Invalid password" for authentication failures. This seems helpful for debugging, but it enables username enumeration attacks.

**Why it's wrong**: Different error messages for "user not found" versus "invalid password" reveal whether a username exists. Attackers can use this to enumerate valid usernames, then focus brute force attacks on known accounts. Generic error messages prevent username enumeration while still providing useful feedback.

**The fix**: Return generic error messages for authentication failures. Use messages like "Invalid username or password" for both cases. Log detailed error information server-side for debugging, but return consistent, generic messages to clients. The same principle applies to other operations—don't reveal whether resources exist through error messages.

**Balance**: Generic error messages improve security but can make debugging harder. However, the security benefit outweighs the debugging cost. Use detailed server-side logs for debugging while keeping client-facing messages generic.

## Ignoring Dependency Vulnerabilities

**The trap**: Dependabot alerts accumulate, nobody reviews them, and known CVEs remain unpatched for months. "We'll get to it later" becomes "we never got to it," and then a known vulnerability gets exploited.

**Why it's wrong**: Known vulnerabilities are public information. Attackers actively scan for applications using vulnerable dependencies. The longer vulnerabilities remain unpatched, the higher the risk of exploitation. The Log4Shell vulnerability demonstrated how quickly attackers exploit known vulnerabilities once they're public.

**The fix**: Triage dependency vulnerabilities promptly. Critical and high-severity vulnerabilities should be patched within days, not months. Enable automated dependency updates for security patches. Block merges when critical vulnerabilities are detected. Maintain a process for reviewing and applying security updates regularly.

**Prioritization**: Not all vulnerabilities are equally severe. Use CVSS scores and exploitability information to prioritize. However, don't ignore medium-severity vulnerabilities indefinitely—they can become critical as attack techniques improve or when combined with other vulnerabilities.

## Disabled CSRF Protection Without Understanding

**The trap**: Disabling CSRF protection because "it was causing errors" without understanding why CSRF protection is needed or when it's safe to disable.

**Why it's wrong**: CSRF protection prevents cross-site request forgery attacks, where malicious websites make requests to your application on behalf of authenticated users. CSRF protection is essential for cookie-based authentication but not needed for bearer token authentication. Disabling CSRF without understanding when it's safe leaves applications vulnerable.

**The fix**: Understand CSRF protection requirements. CSRF protection is needed for stateful session-based authentication (cookies) because browsers automatically include cookies in cross-origin requests. CSRF protection is not needed for stateless JWT bearer token authentication (tokens in Authorization headers) because browsers don't automatically include custom headers in cross-origin requests.

**Spring Security**: If you're using JWT bearer tokens, disable CSRF explicitly and document why. If you're using session-based authentication, keep CSRF enabled. Don't disable CSRF "to fix errors" without understanding the security implications.

## Hardcoded Cryptographic Keys

**The trap**: Storing encryption keys or signing keys directly in source code or configuration files. Keys feel like configuration, so it's tempting to put them in config files.

**Why it's wrong**: Hardcoded keys cannot be rotated without code changes and deployments. If keys are compromised, rotation becomes difficult and time-consuming. Keys in source control are effectively public, and keys in configuration files are often accessible to many people.

**The fix**: Use key management services (AWS KMS, Azure Key Vault, HashiCorp Vault) to store and manage cryptographic keys. Applications retrieve keys from key management services at runtime, enabling rotation without code changes. Use key versioning to support gradual rotation.

**Key rotation**: Plan for key rotation from the start. Design systems to support key rotation without service interruption. Use key management services that support automatic rotation or provide rotation workflows.

These gotchas represent common security mistakes that seem harmless but create real vulnerabilities. Awareness of these pitfalls helps prevent them during development and code review. When in doubt, default to the more secure option and seek security team guidance.
