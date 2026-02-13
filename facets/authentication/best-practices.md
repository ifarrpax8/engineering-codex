# Authentication & Authorization -- Best Practices

Authentication and authorization are security-critical concerns that require careful implementation. Mistakes can lead to unauthorized access, data breaches, and compliance violations. These best practices provide guidance for building secure, maintainable authentication systems that balance security requirements with user experience and operational needs.

## Contents

- [Foundational Principles](#foundational-principles)
- [Token and Session Management](#token-and-session-management)
- [Password Handling](#password-handling)
- [API Security](#api-security)
- [Audit and Monitoring](#audit-and-monitoring)
- [Stack-Specific Callouts](#stack-specific-callouts)

## Foundational Principles

### Never Implement Custom Cryptography or Auth Protocols

Cryptography and authentication protocols are complex and easy to get wrong. Never implement your own password hashing algorithms, token signing schemes, or authentication protocols. Use established, well-reviewed libraries and standards.

Use bcrypt or argon2 for password hashing (never MD5, SHA-1, or even SHA-256 without proper key derivation). Use JWT libraries for token handling, OAuth 2.0 libraries for OAuth flows, and established frameworks (Spring Security, Passport.js) for authentication infrastructure.

Custom implementations are likely to have vulnerabilities that attackers can exploit. Established libraries have been reviewed by security experts and have addressed common pitfalls.

### Use Established Libraries and Standards

Leverage industry-standard libraries and frameworks that handle authentication complexity:

**Backend**: Spring Security (Java/Kotlin), Passport.js (Node.js), Devise (Ruby), Django Authentication (Python). These frameworks provide battle-tested authentication flows, password hashing, session management, and security protections.

**Standards**: OAuth 2.0, OpenID Connect, SAML 2.0, JWT (RFC 7519). These standards ensure interoperability, provide security guarantees, and enable integration with identity providers and third-party services.

**Protocols**: Use HTTPS everywhere (never HTTP for authentication). Implement CSRF protection, XSS prevention, and secure cookie attributes. Follow OWASP authentication guidelines.

### Defense in Depth

Implement multiple layers of security controls. Authentication failures should be caught at multiple points: the API gateway, application middleware, service boundaries, and data access layers. Don't rely on a single security check.

Use network-level protections (rate limiting, DDoS mitigation), application-level protections (authentication middleware, authorization checks), and data-level protections (encryption at rest, access logging). Each layer provides defense if another layer is compromised.

## Token and Session Management

### Store Tokens in httpOnly Secure Cookies

Prefer httpOnly cookies for token storage in web applications. Cookies marked httpOnly cannot be accessed by JavaScript, preventing XSS attacks from stealing tokens. The Secure flag ensures cookies are only sent over HTTPS, and SameSite attributes prevent CSRF attacks.

For refresh tokens, always use httpOnly cookies. For access tokens in traditional server-rendered applications, httpOnly cookies are preferred. For SPAs, consider httpOnly cookies with appropriate CORS configuration, or accept the risk of localStorage with very short token lifetimes.

### Set Appropriate Token Lifetimes

Access tokens should be short-lived (15 minutes to 1 hour) to limit exposure if compromised. Refresh tokens can be longer-lived (days to weeks) but should be rotated on each use. Balance security (shorter lifetimes) with user experience (fewer re-authentications) and system load (more refresh requests).

Consider context when setting lifetimes: high-security applications may use 5-minute access tokens, while consumer applications may use 1-hour tokens. Refresh token lifetimes should account for typical user session patterns while enabling revocation when needed.

### Implement Token Rotation for Refresh Tokens

Rotate refresh tokens on each use: when exchanging a refresh token for a new access token, issue a new refresh token and invalidate the old one. This detects token theft—if an attacker uses a stolen refresh token, the legitimate client's next refresh will fail, alerting to compromise.

Token rotation requires server-side tracking of refresh tokens. Maintain a refresh token store (Redis or database) that tracks active tokens, their status, and associated metadata. When a refresh token is used, mark it as consumed and issue a new one.

### Invalidate Sessions on Password Change

When a user changes their password, immediately invalidate all other active sessions. This ensures that if an account was compromised, changing the password revokes the attacker's access. Invalidate both server-side sessions and refresh tokens.

Password change should require the current password for verification. After successful password change, force re-authentication on all devices except the one where the password was changed (if that's the desired UX).

### Include Token Binding or Audience Claims

Include audience (aud) claims in JWTs to specify which services or APIs the token is intended for. Validate audience claims to prevent token misuse across services. Consider including device fingerprints or IP addresses in tokens (as claims, not for validation) to detect suspicious usage.

Token binding ties tokens to specific client characteristics (TLS channel binding, device attestation) making stolen tokens less useful to attackers. While not always practical, token binding provides additional security for high-value applications.

## Password Handling

### Use bcrypt or argon2 for Hashing

Use bcrypt (with cost factor 12 or higher) or argon2 (Argon2id variant) for password hashing. These algorithms are designed for password hashing with built-in salting and configurable computational cost. Never use MD5, SHA-1, SHA-256, or other general-purpose hash functions for passwords.

Bcrypt is widely supported and provides good security with reasonable performance. Argon2 is the winner of the Password Hashing Competition and provides better resistance to specialized hardware attacks. Both algorithms automatically handle salting and are designed to be slow (resistant to brute force).

### Enforce Minimum Complexity Without Overly Restrictive Rules

Require passwords of sufficient length (12+ characters recommended) but avoid overly complex requirements that lead users to predictable patterns or password reuse. NIST guidelines recommend length over complexity: longer passwords are more secure than complex short passwords.

Consider allowing passphrases (multiple words) which are easier to remember and type while providing good security. Don't require frequent password changes unless there's evidence of compromise—forced expiration leads to weaker passwords and user frustration.

### Never Log or Expose Passwords

Never log passwords in any form (plaintext, hashed, or masked). Never include passwords in error messages, stack traces, or API responses. If password validation fails, return generic error messages that don't reveal whether the account exists.

Be careful with password reset flows: don't include passwords in emails, and ensure that reset links are single-use and time-limited. Review all logging statements to ensure passwords aren't accidentally logged.

### Implement Account Lockout with Exponential Backoff

Lock accounts after multiple failed login attempts, but use exponential backoff rather than fixed lockout periods. Start with short lockouts (5 minutes) and increase duration with repeated failures. This prevents brute force attacks while minimizing impact on legitimate users who mistype passwords.

Consider CAPTCHA challenges after a few failed attempts before locking accounts. This distinguishes between automated attacks and human error. Provide clear messaging about lockout status and recovery options.

## API Security

### Authenticate Every API Request

Every API request must include authentication credentials (tokens, API keys, or session cookies). There are no unauthenticated endpoints except those explicitly intended for public access (and even those may benefit from rate limiting).

Authentication middleware should reject requests without valid credentials with 401 Unauthorized responses. Don't allow "optional" authentication—if an endpoint requires auth, enforce it consistently.

### Consider Fine-Grained Authorization (FGA)

Traditional RBAC (Role-Based Access Control) assigns users to roles with broad permissions (e.g., `admin`, `viewer`). Fine-Grained Authorization (FGA) provides more precise control by defining relationships between users, actions, and specific resources.

**RBAC** (coarse-grained):
- User has `admin` role → can access all orders
- Simple, works for many applications

**FGA** (fine-grained):
- User has `read` permission on order `123` → can only access that specific order
- User has `write` permission on orders in organisation `abc` → can modify orders scoped to that org
- More complex, but essential for multi-tenant platforms and resource-level access control

**When to use FGA**:
- Multi-tenant applications where users should only access their own organisation's data
- Resource-level permissions (e.g., "can this user edit this specific document?")
- Complex permission hierarchies (organisation → team → project → resource)
- When RBAC roles become too coarse (too many roles, role explosion)

**When RBAC is sufficient**:
- Single-tenant applications with clear role boundaries
- Simple permission models (admin, editor, viewer)
- Early-stage applications where the permission model is still evolving

**Implementation approach**: Define permission models declaratively (who can do what on which resource), integrate checks at the service layer, and test authorization paths thoroughly.

> **Stack Callout — Pax8**: Pax8 mandates Fine-Grained Authorization for all new APIs. Permission models are defined in the `role-management` repository. Use `@PreAuthorize("@accessChecks.hasPermission('read:orders')")` in Spring controllers. See the [API Security Guide](https://pax8.atlassian.net/wiki/spaces/DD/pages/2444198682) for implementation patterns.

### Use API Keys for Identification, OAuth for Authorization

API keys identify clients (applications or services) but don't represent user identity. Use API keys for service-to-service authentication where user context isn't needed. Use OAuth 2.0 client credentials flow for machine-to-machine authentication with proper scoping.

For user-facing APIs, use OAuth 2.0 access tokens that represent user identity and authorization. API keys alone are insufficient for user authorization—they identify the client application, not the user.

### Rate Limit Authentication Endpoints Aggressively

Authentication endpoints (login, password reset, token refresh) are prime targets for abuse and should be rate-limited more aggressively than other endpoints. Implement per-IP and per-account rate limiting to prevent brute force attacks and credential stuffing.

Rate limits should be low enough to prevent attacks but high enough to allow legitimate use. Consider progressive rate limiting: allow a few requests quickly, then require delays or CAPTCHA challenges. Monitor rate limit violations for security alerts.

### Return Generic Error Messages

Authentication error messages should not reveal whether an account exists. Return the same error message for invalid email and invalid password to prevent email enumeration attacks. Messages like "Invalid email or password" protect user privacy while still being helpful enough for legitimate users.

Don't reveal account status (locked, unverified, disabled) in error messages unless the user is authenticated. Provide account status information through authenticated account management endpoints.

## Audit and Monitoring

### Log All Authentication Events

Log all authentication-related events with sufficient detail for security analysis and compliance:

- Successful logins (user ID, timestamp, IP address, user agent)
- Failed login attempts (email/username attempted, timestamp, IP address, failure reason)
- Logouts (user ID, timestamp, session duration)
- Password changes (user ID, timestamp, IP address)
- Account lockouts (user ID, timestamp, trigger reason)
- Permission changes (user ID, permissions changed, changed by, timestamp)
- Token refresh events (user ID, timestamp, IP address)

Logs should be immutable, tamper-evident, and retained according to compliance requirements. Never log passwords, tokens, or other sensitive credentials.

### Include Correlation IDs for Tracing Auth Flows

Include correlation IDs or request IDs in authentication logs to trace complete authentication flows across services. This enables debugging authentication issues and investigating security incidents.

Correlation IDs should be included in log entries, error responses (without exposing sensitive data), and passed between services in request headers. This provides end-to-end visibility into authentication flows.

### Alert on Anomalous Patterns

Monitor authentication logs for suspicious patterns and generate alerts:

- Multiple failed login attempts from the same IP
- Login attempts from unusual geographic locations
- Rapid account lockouts across multiple accounts
- Unusual token refresh patterns (potential token theft)
- Privilege escalation attempts
- Unusual session durations or access patterns

Use machine learning or rule-based detection to identify anomalies. Tune alert thresholds to minimize false positives while catching real threats.

### Never Log Tokens or Credentials

Never log authentication tokens (JWTs, session IDs, refresh tokens), passwords (even hashed), API keys, or other credentials. Logging credentials creates security risks if logs are compromised. If you need to debug authentication issues, log metadata (token expiration time, user ID from token) but not the token itself.

Review logging code carefully to ensure credentials aren't accidentally logged. Use structured logging libraries that support redaction of sensitive fields.

## Stack-Specific Callouts

### Kotlin/Java: Spring Security

**Filter Chain Configuration**: Configure Spring Security filter chains explicitly rather than relying on defaults. Order filters correctly: authentication filters before authorization filters, CSRF protection before request handlers. Use `SecurityFilterChain` beans to define custom filter chains for different URL patterns.

**SecurityContextHolder**: Use `SecurityContextHolder.getContext().authentication` to access the current authenticated user in your code. The SecurityContext is stored in thread-local storage, so it's automatically available in request-handling threads. Clear the context after request processing to prevent context leakage.

**@PreAuthorize Annotations**: Use method-level security annotations (`@PreAuthorize`, `@PostAuthorize`, `@Secured`) to enforce authorization at the method level. This provides declarative authorization that's easy to read and maintain. Enable method security with `@EnableMethodSecurity` or `@EnableGlobalMethodSecurity`.

```kotlin
// Kotlin: UserService.kt
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.stereotype.Service

@Service
class UserService(
    private val userRepository: UserRepository
) {
    @PreAuthorize("hasRole('ADMIN')")
    fun deleteUser(userId: Long) {
        userRepository.deleteById(userId)
    }

    @PreAuthorize("hasRole('ADMIN') or authentication.name == #userId.toString()")
    fun updateUser(userId: Long, userData: UserUpdateDto) {
        // Only admins or the user themselves can update
        userRepository.save(userData.toEntity(userId))
    }

    @PreAuthorize("@userSecurityService.canAccessUser(authentication.name, #userId)")
    fun getUserDetails(userId: Long): UserDto {
        // Custom authorization logic via bean method
        return userRepository.findById(userId).toDto()
    }
}
```

```java
// Java: UserService.java
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
    }

    @PreAuthorize("hasRole('ADMIN') or authentication.name == #userId.toString()")
    public void updateUser(Long userId, UserUpdateDto userData) {
        // Only admins or the user themselves can update
        userRepository.save(userData.toEntity(userId));
    }

    @PreAuthorize("@userSecurityService.canAccessUser(authentication.name, #userId)")
    public UserDto getUserDetails(Long userId) {
        // Custom authorization logic via bean method
        return userRepository.findById(userId).toDto();
    }
}
```

**Method-Level Security**: Combine method-level security with endpoint-level security for defense in depth. Method security is particularly valuable for service layer authorization where business logic enforces domain-specific permissions.

### Vue: Vue Router and Pinia

**Vue Router Navigation Guards**: Use `beforeEach` navigation guards to check authentication before route access. Redirect unauthenticated users to login, preserving the intended destination for post-login redirect. Use `meta.requiresAuth` route metadata to mark protected routes.

```typescript
// Vue 3: router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      component: () => import('@/views/Login.vue')
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
})

export default router
```

**Pinia Auth Store Pattern**: Create a Pinia store for authentication state (user, token, isAuthenticated). The store manages login, logout, token refresh, and provides reactive authentication state to components. Use the store in navigation guards and components that need auth state.

**Axios Interceptors for Token Refresh**: Configure axios interceptors to automatically refresh expired access tokens using refresh tokens. Intercept 401 responses, attempt token refresh, and retry the original request. Handle refresh failures by redirecting to login.

```typescript
// Vue 3 / React: utils/api.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth' // Vue Pinia
// import { useAuth } from '@/contexts/AuthContext' // React Context

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request interceptor: add access token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const authStore = useAuthStore() // Vue
  // const { token } = useAuth() // React - would need different approach
  
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor: handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const authStore = useAuthStore()

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue requests while refresh is in progress
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await authStore.refreshToken()
        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null)
        authStore.logout()
        // Redirect to login (Vue: router.push('/login'), React: navigate('/login'))
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

### React: Context and Protected Routes

**React Context for Auth State**: Use React Context (or state management libraries like Zustand) to provide authentication state throughout the component tree. Create an AuthContext that provides user, token, login, and logout functions. Wrap your application with the AuthProvider.

**Protected Route Components**: Create a `ProtectedRoute` component that checks authentication before rendering child routes. Redirect unauthenticated users to login. Use this component to wrap routes that require authentication, providing a clean declarative API for route protection.

```typescript
// React: components/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

// Usage in App.tsx
<Routes>
  <Route path="/login" element={<Login />} />
  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    }
  />
</Routes>
```

**Axios/Fetch Interceptors**: Configure request interceptors to add authentication tokens to API requests. Configure response interceptors to handle token expiration: refresh tokens automatically or redirect to login on refresh failure. Use libraries like axios with interceptors or fetch wrappers that handle token management.
