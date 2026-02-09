# Authentication -- Gotchas

Common pitfalls and traps that developers encounter when implementing authentication and authorization. These are the things that seem reasonable at first but cause real problems.

## JWTs Can't Be Revoked (Without Defeating Their Purpose)

**The trap**: Choosing JWTs for their "stateless" nature, then realizing you need to revoke them (user logs out, password changed, account compromised).

**Why it's a problem**: JWTs are self-contained -- the server doesn't need to check a database to validate them. But this means you can't invalidate a token before it expires. The common workaround is a revocation list or token blacklist, which requires server-side state -- negating the "stateless" benefit of JWTs.

**Mitigation**: Keep access token lifetimes short (5-15 minutes). Use refresh tokens stored server-side (Redis) that can be revoked. Accept that your "stateless" JWT architecture has a stateful refresh token layer.

## Refresh Token Rotation and Multi-Tab Issues

**The trap**: Implementing refresh token rotation (new refresh token on each use) for security, then discovering that users with multiple browser tabs get logged out randomly.

**Why it happens**: Tab A and Tab B both have the same refresh token. Tab A refreshes and gets a new token, invalidating the old one. Tab B tries to refresh with the old token and gets rejected. User is logged out of Tab B.

**Mitigation**: Use a grace period (allow the old refresh token for a short window after rotation), implement token families (group tokens by session, only invalidate the family on detected reuse), or use a session-based approach for browser clients.

## Storing Tokens in localStorage

**The trap**: Storing JWTs in `localStorage` because it's easy and persists across page reloads.

**Why it's a problem**: `localStorage` is accessible to any JavaScript running on the page, including XSS attacks. A single XSS vulnerability means all tokens are compromised.

**Mitigation**: Store tokens in `httpOnly` secure cookies. They're not accessible to JavaScript and are automatically sent with requests. Use `SameSite=Strict` or `SameSite=Lax` to prevent CSRF.

## Generic Error Messages That Are Too Generic

**The trap**: Returning "Invalid credentials" for all login failures to avoid leaking whether an email exists.

**Why it's a problem**: While this is correct for the login endpoint, the same logic is often not applied to the registration endpoint ("Email already exists") or the password reset endpoint ("If an account exists, we'll send an email"). Attackers can use these other endpoints to enumerate users.

**Mitigation**: Apply consistent information disclosure rules across all auth-related endpoints. Registration should not confirm whether an email is already taken (use email verification instead). Password reset should always say "If an account exists, we'll send an email."

## Permission Checks Only at the UI Level

**The trap**: Hiding buttons and menu items based on permissions but not enforcing permissions on the API.

**Why it's a problem**: UI-level permission checks are a UX convenience, not a security control. Anyone can call the API directly. Every API endpoint must independently verify that the caller has the required permissions.

**Mitigation**: Always enforce authorization at the API level. UI permission checks are for user experience only (hiding unavailable actions). See [Permissions UX](../../experiences/permissions-ux/) for the UX side.

## Hardcoding Roles Instead of Permissions

**The trap**: Checking `if (user.role === 'admin')` throughout the codebase instead of checking specific permissions.

**Why it's a problem**: When you need a new role that has some but not all admin capabilities, you have to audit every role check in the codebase. Role definitions become rigid and scattered.

**Mitigation**: Check permissions, not roles. Roles are collections of permissions. `if (user.hasPermission('users:delete'))` is more flexible than `if (user.role === 'admin')`. Roles map to permissions in a single place.

## Session Fixation

**The trap**: Not regenerating the session ID after authentication.

**Why it happens**: User visits the site, gets a session ID. Attacker captures or sets this session ID. User logs in -- the same session ID is now authenticated. Attacker uses the known session ID to access the authenticated session.

**Mitigation**: Always regenerate the session ID after successful authentication. Spring Security does this by default. If using custom session management, do it explicitly.

## Forgot Password Tokens That Don't Expire

**The trap**: Sending a password reset link with a token that never expires or has a very long expiry.

**Why it's a problem**: Email is not a secure channel. Emails sit in inboxes, get forwarded, are accessed from shared computers. A password reset token that's valid indefinitely is a persistent backdoor.

**Mitigation**: Password reset tokens should expire within 15-60 minutes. Single use only (invalidate after use). Invalidate all outstanding reset tokens when the password is successfully changed.

## Not Rate Limiting Auth Endpoints

**The trap**: Applying rate limiting to your API generally but not specifically to authentication endpoints.

**Why it's a problem**: Auth endpoints are the primary target for brute force attacks. Generic rate limiting (100 req/min per IP) is too lenient for login attempts. A targeted attack can try many credentials within that limit.

**Mitigation**: Apply aggressive rate limiting specifically to auth endpoints: 5-10 login attempts per account per minute, with exponential backoff and account lockout after repeated failures. Consider CAPTCHA after 3 failed attempts.

## OAuth Scopes That Are Too Broad

**The trap**: Requesting `read write admin` scopes for every OAuth client, because "we might need them."

**Why it's a problem**: Broad scopes violate the principle of least privilege. If a client token is compromised, the attacker has maximum access. Users are also less likely to grant broad permissions.

**Mitigation**: Request the minimum scopes needed for each client's use case. Different clients (mobile app, admin dashboard, third-party integration) should have different scope sets.

## Impersonation Without Audit Trail

**The trap**: Implementing admin impersonation (viewing the app as another user) without logging who is impersonating whom.

**Why it's a problem**: Without an audit trail, there's no way to distinguish between actions taken by the real user and actions taken by an admin impersonating them. This is a compliance risk and a debugging nightmare.

**Mitigation**: Log impersonation start/end events. Include the impersonator's identity in all audit logs during impersonation. Consider making impersonation read-only by default (view but not modify).
