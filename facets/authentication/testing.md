# Authentication & Authorization -- Testing

Testing authentication and authorization requires validating identity verification, session management, token handling, and permission enforcement across multiple layers of your application. Security vulnerabilities in authentication can lead to unauthorized access, data breaches, and compliance violations. Comprehensive testing ensures that authentication works correctly under normal conditions and fails securely under attack.

## Contents

- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Security Testing](#security-testing)
- [Test Utilities and Patterns](#test-utilities-and-patterns)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Unit Testing

### Token Generation and Validation Logic

Unit tests verify that token generation produces valid, well-formed tokens with correct claims. Test that expiration times are set correctly, signatures are valid, and custom claims are included. Validation logic should be tested with valid tokens, expired tokens, malformed tokens, and tokens with invalid signatures.

Test edge cases: tokens at the exact expiration boundary, tokens with missing required claims, tokens signed with wrong keys, and tokens with tampered payloads. Verify that validation rejects invalid tokens with appropriate error codes and doesn't leak sensitive information in error messages.

### Permission and Role Evaluation Functions

Authorization logic that evaluates whether a user has required permissions should be thoroughly unit tested. Test role hierarchies (admin inherits user permissions), multiple roles per user, and permission combinations. Verify that permission checks are case-insensitive where appropriate and handle missing permissions gracefully.

Test negative cases: users without required roles, users with wrong roles, and edge cases like empty role lists or null permissions. Ensure that permission evaluation is deterministic and doesn't depend on external state that could change between calls.

### Password Hashing Verification

Unit tests verify that password hashing functions (bcrypt, argon2) produce different hashes for the same password (salt uniqueness), that hashing is consistent (same password + salt produces same hash), and that verification correctly identifies matching and non-matching passwords.

Test that password hashing is sufficiently slow (resistant to brute force) but not so slow as to impact user experience. Verify that common weak passwords are handled appropriately and that hashing functions are called with correct cost parameters.

### Authorization Policy Rules

If using policy engines (OPA, Cedar) or custom policy evaluation, unit test policy rules in isolation. Test that policies correctly evaluate various attribute combinations, that policy logic matches business requirements, and that edge cases are handled (missing attributes, null values, type mismatches).

Test policy composition: multiple policies, policy hierarchies, and policy conflicts. Verify that policy evaluation is performant and that policies fail securely (deny by default) when evaluation errors occur.

## Integration Testing

### Auth Middleware and Filter Chain

Integration tests verify that authentication middleware correctly validates tokens, extracts user context, and either allows requests to proceed or returns 401 Unauthorized responses. Test the complete filter chain with real token validation, including token signature verification, expiration checks, and claim extraction.

Test middleware behavior with various token states: valid tokens, expired tokens, malformed tokens, tokens with missing claims, and requests without tokens. Verify that middleware sets user context correctly (SecurityContextHolder in Spring, request.user in Express) and that downstream code can access authenticated user information.

### Database-Backed Session Lifecycle

Integration tests verify that server-side sessions are created on login, stored correctly in the session store (Redis or database), retrieved on subsequent requests, and deleted on logout or expiration. Test session sharing across multiple application instances when using distributed session storage.

Test session invalidation scenarios: explicit logout, password change, account lockout, and administrative session revocation. Verify that invalidated sessions are immediately ineffective and that session data is properly cleaned up.

### OAuth Flow with Test Identity Provider

Integration tests exercise the complete OAuth authorization code flow with a test identity provider (or mocked IdP). Test successful authentication, authorization code exchange, token refresh, and error handling (user denies authorization, invalid authorization codes, expired codes).

Test PKCE flow: verify that code verifier and challenge are generated correctly, that the challenge is included in the authorization request, and that the verifier is used during token exchange. Test error scenarios: invalid client credentials, redirect URI mismatches, and scope validation failures.

### Permission Boundary Enforcement Across Service Layers

Integration tests verify that authorization checks are enforced at appropriate boundaries: API endpoints, service method calls, and data access layers. Test that users without required permissions receive 403 Forbidden responses and that authorized users can access resources.

Test that authorization is consistently enforced across all entry points and that there are no paths that bypass authorization checks. Verify that permission checks use the correct user context and that impersonation or context switching doesn't leak permissions incorrectly.

## End-to-End Testing

### Full Login and Logout Browser Flows

E2E tests using Playwright or Cypress verify the complete user-facing login and logout experience. Test successful login with email/password, social login flows, logout functionality, and session persistence across page navigations.

Test error scenarios: invalid credentials, account lockout after multiple failures, and expired sessions. Verify that login forms are accessible, error messages are user-friendly, and that users are redirected appropriately after login/logout.

### MFA Enrollment and Verification Flows

E2E tests verify that users can enroll in MFA (scanning QR codes, entering backup codes), that MFA verification is required after enrollment, and that users can disable MFA with proper verification. Test the complete flow: enrollment, verification during login, backup code usage, and MFA removal.

Test error scenarios: invalid verification codes, expired backup codes, and recovery flows when MFA device is lost. Verify that MFA enrollment is secure (requires current password) and that the UI clearly communicates MFA status and requirements.

### SSO Redirect and Callback Flows

E2E tests verify that SSO flows redirect users to the identity provider, that users can authenticate there, and that callbacks return users to the application with valid tokens. Test the complete redirect flow including state parameter validation and CSRF protection.

Test error scenarios: user cancels SSO authentication, identity provider errors, and callback URL tampering. Verify that SSO flows maintain application state and that users are returned to their intended destination after authentication.

### Password Reset Email Flow

E2E tests verify the complete password reset flow: requesting reset, receiving email, clicking reset link, and successfully changing password. Test that reset links expire correctly, are single-use, and that password change invalidates existing sessions.

Test that reset emails are sent to the correct address, that reset links work only once, and that expired links are rejected. Verify that the reset flow doesn't reveal whether an email exists in the system (security requirement to prevent email enumeration).

### Session Expiry and Re-Authentication

E2E tests verify that expired sessions prompt re-authentication, that "remember me" functionality extends session lifetime appropriately, and that users are redirected to login with their intended destination preserved.

Test session timeout behavior: idle timeout, absolute timeout, and activity-based extension. Verify that session expiry is communicated clearly to users and that re-authentication flows work smoothly.

## Security Testing

### Token Expiry Enforcement

Security tests verify that expired tokens are rejected immediately and that token expiration times are enforced correctly. Test tokens at various stages: just issued, near expiration, exactly expired, and long-expired. Verify that clock skew doesn't allow expired tokens to be accepted and that expiration is checked on every request, not cached.

### Brute Force Protection

Security tests verify that rate limiting prevents brute force attacks on login endpoints. Test that multiple failed login attempts trigger account lockout or rate limiting, that lockout periods are enforced, and that legitimate users aren't permanently locked out.

Test that rate limiting is applied per IP address and per account, that lockout messages don't reveal whether an account exists, and that lockout recovery flows work correctly. Verify that CAPTCHA or similar challenges are presented after suspicious activity.

### Session Fixation Prevention

Security tests verify that session identifiers are regenerated after login (preventing session fixation attacks). Test that old session IDs are invalidated when new sessions are created and that session IDs aren't predictable or enumerable.

Test that session cookies have appropriate security attributes (Secure, HttpOnly, SameSite) and that session IDs are sufficiently random and unguessable.

### CSRF Protection Verification

Security tests verify that CSRF protection is enabled and effective. Test that state parameters in OAuth flows prevent CSRF, that SameSite cookie attributes prevent cross-site request forgery, and that CSRF tokens are validated where required.

Test that protected endpoints reject requests without valid CSRF tokens and that CSRF protection doesn't break legitimate same-site requests.

### Token Leakage Detection

Security tests verify that tokens and credentials are never logged, exposed in error messages, or included in URLs. Review application logs, error responses, and browser developer tools to ensure no token leakage. Test that stack traces don't include sensitive authentication data and that error messages are generic (don't reveal whether accounts exist).

### Authorization Bypass Attempts

Security tests attempt to bypass authorization controls through various attack vectors:

**IDOR (Insecure Direct Object Reference)**: Attempt to access resources belonging to other users by manipulating resource IDs in URLs or request bodies. Verify that authorization checks validate resource ownership, not just authentication.

**Privilege Escalation**: Attempt to gain elevated permissions by manipulating role claims in tokens, sending requests with different user contexts, or exploiting authorization logic flaws. Verify that permission checks use server-side validation, not client-provided claims.

**Horizontal and Vertical Authorization**: Test that users cannot access resources at their permission level belonging to others (horizontal) or resources requiring higher permissions (vertical). Verify that multi-tenant applications enforce tenant isolation correctly.

## Test Utilities and Patterns

### Mock Auth Middleware for Non-Auth-Focused Tests

Create test utilities that bypass authentication for tests that focus on other functionality. Mock authentication middleware can set test user context without requiring actual token validation. This keeps tests fast and focused while ensuring that code paths work with authenticated contexts.

In Spring Boot, use `@WithMockUser` or `@WithUserDetails` annotations. In Express, create test middleware that sets `req.user`. Ensure that mocked authentication matches production authentication structure to catch integration issues.

### Test User Factories with Configurable Roles and Permissions

Factory functions or builders create test users with specific roles and permissions for authorization testing. Factories should support creating users with multiple roles, custom permissions, and various account states (verified, locked, expired).

Factories enable readable test code: `createUser({ roles: ['admin'], permissions: ['read_users', 'write_invoices'] })`. They centralize user creation logic and ensure consistent test data.

### Auth Fixtures for Playwright E2E Tests

Use Playwright's `storageState` feature to create authenticated browser contexts for E2E tests. Perform login once, save the browser state (cookies, localStorage), and reuse it across tests. This avoids logging in before every test, improving test performance.

Create fixtures for different user types: `adminUserStorageState.json`, `regularUserStorageState.json`. Tests can start with pre-authenticated contexts, focusing on testing functionality rather than authentication setup.

### JWT Test Token Generators for Integration Tests

Utilities that generate valid test JWTs with configurable claims enable integration testing without requiring a full authentication flow. Test token generators should support setting expiration, custom claims, and signing with test keys.

Test tokens should be clearly identifiable (include a test claim) and should use separate test signing keys to avoid confusion with production tokens. Verify that test tokens are never accepted in production environments.

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize authentication and authorization testing based on security risk and business impact. Critical paths requiring immediate coverage include: login and authentication flows (unauthorized access risk), token validation and expiration (session hijacking risk), and authorization enforcement (privilege escalation risk). High-priority areas include: password reset flows (account takeover risk), MFA enrollment and verification (MFA bypass risk), and session management (session fixation risk).

Medium-priority areas suitable for later iterations include: OAuth/SSO integration edge cases, role hierarchy testing, and administrative authentication features. Low-priority areas for exploratory testing include: deprecated authentication methods, rarely-used permission combinations, and authentication logging.

Focus on authentication failures with high security impact: authentication bypass (unauthorized access possible), privilege escalation (users gain unauthorized permissions), and session hijacking (sessions stolen or reused). These represent the highest risk of security breaches and compliance violations.

### Exploratory Testing Guidance

Authentication flow exploration: test login attempts with various credential combinations (valid credentials, invalid passwords, non-existent users, locked accounts). Probe edge cases: concurrent login attempts, login during password reset, and login with expired sessions. Explore what happens when authentication services are unavailable or slow.

Token lifecycle requires investigation: test token generation (tokens created correctly), token validation (tokens validated correctly), token expiration (tokens expire correctly), and token refresh (tokens refreshed correctly). Probe edge cases: tokens at exact expiration boundary, tokens with tampered signatures, and tokens with missing claims.

Authorization boundary exploration: test permission checks at various boundaries (API endpoints, service methods, data access layers). Probe edge cases: users with multiple roles, role hierarchies, permission combinations, and missing permissions. Explore what happens when authorization checks fail: are errors logged? are users informed? are security events recorded?

Session management needs exploration: test session creation (sessions created on login), session persistence (sessions survive page refreshes), session expiration (sessions expire correctly), and session invalidation (sessions invalidated on logout). Probe edge cases: concurrent sessions, session sharing across devices, and session fixation attempts.

### Test Data Management

Authentication testing requires realistic test data: user accounts with various roles (admin, user, guest), accounts in different states (verified, locked, expired, pending), and accounts with various authentication methods (password, MFA, SSO). Create test data factories that generate realistic authentication scenarios: `createAdminUser()`, `createUserWithMFA()`, `createLockedAccount()`.

Sensitive authentication data must be handled carefully: never commit real credentials, use test credentials that are clearly identifiable, and rotate test credentials regularly. Use test data that mirrors production patterns but is clearly test data (test email domains like `@test.example.com`, test account prefixes). Test passwords should be strong but memorable for manual testing scenarios.

Test data refresh strategies: authentication test data may become stale (expired tokens, locked accounts, rotated credentials). Implement test data refresh that generates new tokens, resets account states, and updates credentials. Authentication test data should be refreshed more frequently than other test data due to security requirements (token expiration, account lockout policies).

Attack payload test data: maintain test datasets of attack payloads (SQL injection in login forms, XSS in error messages, session fixation attempts, token manipulation attempts). These payloads should be safe to use in test environments but representative of real attacks. Update payload datasets as new attack vectors are discovered.

### Test Environment Considerations

Authentication test environments must mirror production security configurations: same authentication mechanisms (same password hashing algorithms, same token signing keys), same authorization rules (same role definitions, same permission checks), and same security policies (same password requirements, same lockout policies). Differences can hide vulnerabilities or create false positives. Verify that test environments use production-like security configurations.

Shared test environments create isolation challenges: concurrent authentication tests may interfere with each other (rate limiting, account lockouts, session conflicts). Use isolated test environments per test run, or implement test isolation through unique user accounts and cleanup between tests. Authentication tests should not share user accounts or sessions.

Environment-specific risks include: test environments with relaxed security (missing rate limiting, permissive password policies), test environments missing production security features (MFA, account lockout), and test environments with different token expiration policies. Verify that test environments have equivalent security controls, or explicitly test security control absence as a separate scenario.

Authentication service dependencies: test environments may depend on external authentication services (OAuth providers, LDAP servers, identity providers). Use test doubles (mocks, stubs) for external services, or use sandbox/test versions. Verify that test doubles behave like production services, or document differences.

### Regression Strategy

Authentication regression suites must include: login and authentication flows (users can authenticate), token validation (tokens validated correctly), authorization enforcement (unauthorized access prevented), and session management (sessions work correctly). These represent the core authentication functionality that must never regress.

Automation candidates for regression include: authentication unit tests (token generation, password hashing), authorization unit tests (permission checks, role evaluation), and authentication integration tests (middleware validation, session lifecycle). These are deterministic and can be validated automatically.

Manual regression items include: OAuth/SSO flows (complex multi-step flows), MFA enrollment flows (requires manual device interaction), and security testing (penetration testing, vulnerability scanning). These require human judgment or specialized security testing tools.

Trim regression suites by removing tests for deprecated authentication methods, obsolete token formats, or rarely-used authentication features. However, maintain tests for critical authentication flows (login, logout, password reset) even if they're complex—authentication regressions have high security impact.

### Defect Patterns

Common authentication bugs include: authentication bypass (unauthorized access possible), privilege escalation (users gain unauthorized permissions), session fixation (sessions can be hijacked), and token leakage (tokens exposed in logs or URLs). These patterns recur across applications and should be tested explicitly.

Bugs tend to hide in: edge cases (token expiration boundaries, concurrent logins, role transitions), error paths (authentication failures, authorization failures, session expiration), and configuration issues (missing security headers, permissive CORS, weak password policies). Test these scenarios explicitly—they're common sources of security vulnerabilities.

Historical patterns show that authentication bugs cluster around: token validation (tokens not validated correctly), authorization enforcement (authorization checks bypassed), and session management (sessions not managed securely). Focus security testing on these areas.

Triage guidance: authentication bugs are typically critical severity due to security implications. However, distinguish between exploitable vulnerabilities (attackers can bypass authentication) and security improvements (defense in depth). Exploitable vulnerabilities require immediate attention, while security improvements can be prioritized based on risk.
