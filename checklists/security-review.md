# Security Review Checklist

Use this checklist before deploying any feature that involves authentication, authorization, secrets, user data, or external integrations. Cross-reference with the [Security facet](../facets/security/) for deeper guidance.

## Authentication & Authorization

- [ ] **Token/session security** (no secrets in URLs, secure cookie flags, token expiry) → [authentication/best-practices.md](../facets/authentication/best-practices.md)
- [ ] **Permission enforcement on server** (not just UI) → [authentication/architecture.md](../facets/authentication/architecture.md)
- [ ] **OAuth/OIDC configuration** (redirect URI validation, state parameter, PKCE) → [authentication/options.md](../facets/authentication/options.md)
- [ ] **Session management** (timeout, invalidation on password change, concurrent session limits) → [authentication/gotchas.md](../facets/authentication/gotchas.md)

## Input Validation & Injection

- [ ] **All user input validated server-side** (never trust client) → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **SQL injection prevention** (parameterized queries, no string concatenation) → [security/gotchas.md](../facets/security/gotchas.md)
- [ ] **XSS prevention** (output encoding, CSP headers, sanitize user-generated HTML) → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **Path traversal prevention** (validate file paths, no user-controlled directory access) → [security/gotchas.md](../facets/security/gotchas.md)
- [ ] **Request size limits configured** (prevent DoS via large payloads) → [security/architecture.md](../facets/security/architecture.md)

## Secrets Management

- [ ] **No hardcoded secrets in code, config files, or environment defaults** → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **Secrets stored in Vault/cloud provider/sealed-secrets, not plaintext** → [security/options.md](../facets/security/options.md)
- [ ] **API keys rotatable without deployment** → [configuration-management/best-practices.md](../facets/configuration-management/best-practices.md)
- [ ] **.env files in .gitignore** → [security/gotchas.md](../facets/security/gotchas.md)

## Data Protection

- [ ] **Sensitive data encrypted at rest and in transit** (TLS everywhere) → [security/architecture.md](../facets/security/architecture.md)
- [ ] **PII minimized** (collect only what's needed, mask in logs) → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **Data retention policy applied** (auto-delete old data) → [security/architecture.md](../facets/security/architecture.md)
- [ ] **Backups encrypted** → [data-persistence/operations.md](../facets/data-persistence/operations.md)

## Browser Security

- [ ] **Security headers configured** (CSP, X-Frame-Options, X-Content-Type-Options, HSTS) → [security/architecture.md](../facets/security/architecture.md)
- [ ] **CORS configured correctly** (not wildcard in production) → [security/gotchas.md](../facets/security/gotchas.md)
- [ ] **Cookie flags set** (Secure, HttpOnly, SameSite) → [authentication/best-practices.md](../facets/authentication/best-practices.md)

## Dependencies & Supply Chain

- [ ] **Dependencies scanned for vulnerabilities** (Dependabot, Renovate, Snyk) → [security/options.md](../facets/security/options.md)
- [ ] **Lock files committed** (package-lock.json, gradle.lockfile) → [security/best-practices.md](../facets/security/best-practices.md)
- [ ] **No unnecessary dependencies** (smaller attack surface) → [security/best-practices.md](../facets/security/best-practices.md)

## Multi-Tenancy

(if applicable)

- [ ] **Tenant isolation verified** (no cross-tenant data access) → [multi-tenancy-ux/gotchas.md](../experiences/multi-tenancy-ux/gotchas.md)
- [ ] **Tenant context enforced server-side** (not just frontend) → [multi-tenancy-ux/architecture.md](../experiences/multi-tenancy-ux/architecture.md)
