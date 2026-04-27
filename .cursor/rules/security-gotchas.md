---
description: Security traps that slip through code review — secrets in source control, client-side auth, SQL injection, logging PII
globs: []
alwaysApply: true
type: "always"
---

# Security — Gotchas

Quick reference for the most common traps. Full detail: `engineering-codex/facets/security/gotchas.md`

- **Secrets in source control** — `.env` files, `docker-compose.yml` credentials, or hardcoded keys committed to git are effectively public, even in private repos. Use `.gitignore` + secrets manager. Git history is permanent.
- **CORS `*` with credentials** — `Allow-Origin: *` combined with `Allow-Credentials: true` is forbidden by browsers and signals a misconfigured CORS policy. Use explicit allowed-origin lists for authenticated APIs.
- **Client-side authorization only** — Hiding a button is UX, not security. Every API endpoint must enforce authorization server-side regardless of what the UI shows.
- **SQL injection in native queries** — JPA/Hibernate protects standard queries; native queries (`nativeQuery=true`) need explicit parameter binding. Never concatenate user input into SQL strings.
- **JWT in localStorage** — JavaScript-accessible storage is XSS-vulnerable. Store JWTs in `httpOnly` cookies. If `localStorage` is unavoidable, keep token lifetime ≤ 15 minutes.
- **No rate limiting on auth endpoints** — Login, registration, and password-reset endpoints without rate limits are open to brute force and credential stuffing. Limit per IP and per username.
- **Logging sensitive data** — Passwords, tokens, card numbers, or full PII in logs violates compliance (GDPR, PCI) and creates breach risk. Log enough to debug; never log the sensitive value itself.
- **Detailed auth error messages** — "User not found" vs "Wrong password" enables username enumeration. Return a single generic message for all auth failures.
- **Ignored dependency CVEs** — Known vulnerabilities are public targets. Critical/high CVEs should be patched within days, not sprints.
- **Disabling CSRF without understanding why** — CSRF protection is needed for cookie-based sessions, not needed for JWT bearer token auth. Document the reason explicitly when disabling.
- **Hardcoded cryptographic keys** — Keys in code or config files can't be rotated without a deployment. Use a key management service (AWS KMS, Vault) from the start.
