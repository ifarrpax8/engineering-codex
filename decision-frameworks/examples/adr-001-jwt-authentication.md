# ADR-001: JWT-Based Authentication for MFE Architecture

**Date:** 2026-01-15
**Status:** Accepted
**Deciders:** Backend Tech Lead, Frontend Tech Lead, Security Engineer

## Codex Reference

**Facet:** [authentication/options.md](../../facets/authentication/options.md)
**Recommendation Type:** Decision Matrix

## Context

We are building a suite of micro-frontends (MFEs) that share a common authentication boundary. Each MFE is independently deployed and may be served from different origins. We need an authentication mechanism that:

- Works across multiple MFEs without requiring each to manage its own session
- Supports a single sign-on (SSO) experience
- Integrates with our existing Keycloak identity provider
- Allows backend services to independently validate identity without calling a central session store

Our current monolith uses server-side sessions with cookies, which doesn't translate well to a distributed MFE architecture where services are stateless.

## Decision

Use JWT (JSON Web Tokens) issued by Keycloak via the Authorization Code Flow with PKCE. Tokens are stored in memory (not localStorage) in the shell application and passed to MFEs via a shared auth module.

## Options Considered

### Option 1: Server-Side Sessions with Shared Cookie

- **Description:** Traditional session cookie approach with a shared domain cookie across MFEs
- **Pros:** Simple mental model, no token management, automatic CSRF protection with SameSite cookies
- **Cons:** Requires all MFEs on the same domain, session store becomes a single point of failure, doesn't work for cross-origin API calls, forces backend to be stateful

### Option 2: JWT with PKCE (Chosen)

- **Description:** Keycloak issues JWTs via Authorization Code Flow + PKCE. Shell app manages token lifecycle. Backend services validate tokens locally using Keycloak's public key.
- **Pros:** Stateless backend validation, works across origins, standard OAuth 2.0/OIDC flow, tokens carry claims for authorization decisions, PKCE eliminates the need for client secrets in SPAs
- **Cons:** Token revocation requires additional mechanisms (short-lived tokens + refresh rotation), larger payload than session IDs, requires careful storage (XSS risk if stored in localStorage)

### Option 3: BFF (Backend for Frontend) Pattern with Opaque Tokens

- **Description:** A server-side BFF handles the OAuth flow, stores tokens server-side, and issues a session cookie to the browser
- **Pros:** Most secure (tokens never touch the browser), cookie-based so simpler frontend code, server-side refresh handling
- **Cons:** Introduces an additional service to maintain, adds latency for every request (proxy hop), more complex deployment, BFF becomes a coupling point between MFEs

## Decision Rationale

JWT with PKCE was chosen because our MFE architecture requires cross-origin compatibility and stateless backend validation. The BFF pattern was a close contender on security grounds, but the operational overhead of maintaining a BFF per MFE (or a shared BFF that becomes a coupling point) outweighed the security benefits — especially since we mitigate the storage risk by keeping tokens in memory rather than localStorage.

### Criteria Weighting

| Criteria | Weight | JWT + PKCE | Server Sessions | BFF Pattern |
|----------|--------|------------|-----------------|-------------|
| Scalability | High | High | Low | Medium |
| Security | High | Medium | Medium | High |
| Developer Experience | Medium | Medium | High | Low |
| Maintainability | Medium | High | Medium | Low |
| Team Familiarity | Medium | Medium | High | Low |

### Synergies

- **State Management** — The shell app's auth module (Pinia store) manages token state and exposes it to MFEs. This aligns with our decision to use Pinia for cross-MFE shared state (see Decision Log #1).
- **API Design** — Backend services extract claims from the JWT for authorization, which aligns with our RBAC model. No additional session lookup needed.

## Consequences

### Positive

- Backend services are fully stateless — no shared session store to maintain or scale
- SSO works naturally across MFEs via Keycloak's session
- Token claims enable fine-grained authorization without additional database queries
- PKCE flow is the current OAuth 2.0 best practice for SPAs

### Negative

- Token revocation is not instant — mitigated by short-lived access tokens (5 min) with silent refresh
- Refresh token rotation adds complexity — mitigated by centralizing refresh logic in the shell app
- Team needs to learn OIDC/PKCE flow — mitigated by Keycloak's well-documented JavaScript adapter

### Neutral

- Token size (~1KB) is larger than a session cookie (~50 bytes), but negligible for modern networks

## Evolution Triggers

Revisit this decision when:
- We need instant token revocation (e.g., regulatory requirement) — consider adding a token introspection endpoint or switching to BFF
- MFE count exceeds 10 and shared auth module becomes a versioning bottleneck — consider a dedicated auth MFE
- We adopt server-side rendering (SSR) for any MFE — BFF pattern becomes more natural in that context

## Related Decisions

- Decision Log #1: Pinia for cross-MFE shared state
- Decision Log #3: Keycloak as identity provider
