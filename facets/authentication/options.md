---
recommendation_type: decision-matrix
---

# Authentication & Authorization -- Options

Authentication strategy is a foundational architectural decision that impacts security, scalability, user experience, and operational complexity. This decision matrix helps you choose the right authentication approach for your application's needs.

## Contents

- [Options](#options)
  - [Session-Based Authentication](#1-session-based-authentication)
  - [JWT (Self-Contained Tokens)](#2-jwt-self-contained-tokens)
  - [OAuth 2.0 / OpenID Connect](#3-oauth-20--openid-connect)
- [Authorization Model Options](#authorization-model-options)
  - [RBAC (Role-Based Access Control)](#rbac-role-based-access-control)
  - [ABAC (Attribute-Based Access Control)](#abac-attribute-based-access-control)
  - [FGA/ReBAC (Fine-Grained / Relationship-Based Access Control)](#fgarebac-fine-grained--relationship-based-access-control)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Options

### 1. Session-Based Authentication

**Description**: Server-side session storage maintains authentication state. Users receive a session identifier (session ID) stored in an httpOnly cookie. The server validates session IDs against a session store (Redis or database) to determine authenticated users.

**Strengths**:
- Immediate revocation: delete session record to instantly invalidate access
- Server-side state: can store additional session data beyond user identity
- Security: httpOnly cookies prevent XSS token theft
- Familiar pattern: well-understood by developers and frameworks
- Fine-grained control: complete control over session lifecycle

**Weaknesses**:
- Server-side storage: requires Redis or database for session storage
- Scalability: shared session storage needed for horizontal scaling
- Stateful: complicates stateless load balancing
- Infrastructure dependency: session store becomes critical component

**Best For**:
- Traditional server-rendered web applications
- Applications requiring immediate session revocation
- Single-region deployments with shared session storage
- Applications that need server-side session state

**Avoid When**:
- Building stateless microservices architectures
- Need to scale across multiple regions without shared storage
- Building APIs consumed by mobile or third-party clients
- Statelessness is a primary architectural goal

### 2. JWT (Self-Contained Tokens)

**Description**: Stateless tokens (JWTs) encode user identity and claims in the token itself. Clients store tokens (localStorage, memory, or httpOnly cookies) and include them in requests. Servers validate token signatures without querying a database.

**Strengths**:
- Stateless: no server-side storage required
- Scalability: any server can validate tokens independently
- Performance: no database lookup for authentication
- Cross-service: tokens work across multiple services
- Mobile-friendly: works well for mobile and native applications

**Weaknesses**:
- Revocation challenges: cannot revoke stateless tokens without blacklist
- Token size: larger than session IDs, impacts request size
- Storage risks: localStorage vulnerable to XSS attacks
- Expiration only: revocation relies on token expiration

**Best For**:
- APIs and microservices architectures
- Single Page Applications (SPAs)
- Mobile and native applications
- Cross-service authentication in distributed systems
- High-scale applications where statelessness is valuable

**Avoid When**:
- Immediate revocation is a hard requirement
- Token storage must be XSS-resistant (prefer httpOnly cookies)
- Need to store large amounts of session data
- Building traditional server-rendered web applications

### 3. OAuth 2.0 / OpenID Connect

**Description**: Delegated authentication offloads identity verification to a trusted identity provider (IdP). Users authenticate with the IdP, which issues tokens that your application trusts. Your application never handles user passwords directly.

**Strengths**:
- Security: no password storage or handling
- SSO: enables single sign-on across multiple applications
- Standards-based: OAuth 2.0 and OIDC are industry standards
- User experience: users authenticate once, access multiple apps
- Compliance: reduces compliance burden (no password storage)
- Third-party integrations: enables secure API access delegation

**Weaknesses**:
- Complexity: requires IdP integration and flow handling
- Dependency: depends on external identity provider
- User experience: redirect flows can be disruptive
- Cost: enterprise IdPs may have licensing costs

**Best For**:
- Enterprise applications requiring SSO
- Applications integrating with third-party services
- Multi-application ecosystems
- Applications wanting to avoid password management
- B2B applications where customers have existing identity systems

**Avoid When**:
- Building consumer applications without existing IdP
- Need complete control over authentication UX
- Small applications where IdP integration overhead isn't justified
- Applications requiring custom authentication flows

## Authorization Model Options

### RBAC (Role-Based Access Control)

Assign users to roles, and roles have associated permissions. Authorization checks whether the user's role includes the required permission. Simple, well-understood, and suitable for many applications. Best when authorization needs align with organizational roles and permissions are relatively coarse-grained.

### ABAC (Attribute-Based Access Control)

Make authorization decisions based on attributes of user, resource, action, and environment. Provides fine-grained, context-aware authorization. Best when authorization rules are complex, depend on multiple factors, or need to be highly dynamic.

### FGA/ReBAC (Fine-Grained / Relationship-Based Access Control)

Model authorization as relationships between entities in a graph. Permissions are defined as relationships (user is member of organization, user owns document). Best for applications with rich relationship models, collaborative features, complex sharing scenarios, and multi-tenant applications.

## Evaluation Criteria

| Criteria | Weight Guidance | Session-Based | JWT | OAuth 2.0/OIDC |
|----------|----------------|---------------|-----|----------------|
| **Immediate Revocation** | High for sensitive apps | ✅ Excellent | ❌ Challenging | ✅ Good (refresh tokens) |
| **Stateless Scalability** | High for microservices | ❌ Requires shared storage | ✅ Excellent | ✅ Excellent |
| **Security (XSS Resistance)** | Critical | ✅ httpOnly cookies | ⚠️ Depends on storage | ✅ httpOnly cookies |
| **User Experience** | High for consumer apps | ✅ Seamless | ⚠️ Varies | ✅ Excellent (SSO) |
| **Implementation Complexity** | Medium | ✅ Low | ⚠️ Medium | ❌ High |
| **Mobile/Native Support** | High for mobile apps | ⚠️ Limited | ✅ Excellent | ✅ Excellent |
| **Cross-Service Auth** | High for microservices | ❌ Requires shared storage | ✅ Excellent | ✅ Excellent |
| **Infrastructure Dependency** | Medium | ❌ Session store required | ✅ None | ⚠️ IdP dependency |
| **Standards Compliance** | High for enterprise | ⚠️ Custom implementation | ✅ JWT standard | ✅ Industry standard |
| **Password Management** | Medium | ❌ You manage passwords | ❌ You manage passwords | ✅ IdP manages |
| **SSO Capability** | High for multi-app | ❌ Not natively | ❌ Not natively | ✅ Native support |
| **Token Size** | Low | ✅ Small (session ID) | ⚠️ Larger (claims) | ⚠️ Varies |

## Recommendation Guidance

### Choose Session-Based Authentication When:

- Building traditional server-rendered web applications
- You need immediate session revocation capabilities
- Your application runs in a single region or can easily share session storage
- You need to store server-side session state beyond user identity
- Your team is most familiar with session-based patterns

**Example Use Cases**: E-commerce platforms, content management systems, internal business applications, applications with strict revocation requirements.

### Choose JWT When:

- Building APIs or microservices architectures
- Statelessness is a primary architectural goal
- You're building SPAs, mobile apps, or native applications
- You need cross-service authentication without shared state
- Scale requirements make statelessness valuable

**Example Use Cases**: REST APIs, microservices backends, mobile applications, high-scale consumer applications, serverless architectures.

### Choose OAuth 2.0 / OIDC When:

- You need single sign-on across multiple applications
- You're building enterprise or B2B applications
- You want to avoid password management and storage
- You're integrating with third-party services that require OAuth
- Your customers have existing identity providers

**Example Use Cases**: Enterprise SaaS applications, multi-application platforms, B2B integrations, applications requiring SSO, third-party API integrations.

### Hybrid Approaches

Many applications use hybrid approaches:
- **Short-lived JWT access tokens + stateful refresh tokens**: Combines stateless access tokens with revocable refresh tokens
- **OAuth 2.0 with JWT tokens**: Uses OAuth flows but issues JWTs as access tokens
- **Session-based for web + JWT for APIs**: Different authentication for web UI vs API consumers

Hybrid approaches can provide the benefits of multiple strategies while mitigating their weaknesses.

## Synergies

### Frontend Architecture

**If you chose MFE (Micro-Frontend)**: Token-based authentication (JWT) simplifies cross-MFE authentication. A single token can be shared across multiple MFEs, and each MFE can validate tokens independently without shared session storage. OAuth 2.0 with JWT tokens works particularly well for MFE architectures.

**If you chose SPA**: JWT tokens stored in httpOnly cookies (with CORS configuration) or localStorage provide good authentication for SPAs. OAuth 2.0 authorization code flow with PKCE is recommended for SPAs to prevent authorization code interception attacks.

### Backend Architecture

**If you chose Microservices**: OAuth 2.0 with gateway-level token validation is preferred. The API gateway validates tokens once, and downstream services trust the gateway's authentication. JWT tokens enable stateless service-to-service authentication without shared session storage.

**If you chose Monolith**: Session-based authentication works well for monolithic applications. Sessions can be stored in the application database or Redis, and the monolith has full control over session lifecycle.

### Data Persistence

**If you chose Event Sourcing**: Authentication events (login, logout, password change, permission modification) can be part of your event stream. This provides comprehensive audit trails and enables event-driven downstream processing of authentication events.

**If you chose CQRS**: Authentication commands (login, logout) can be separate from queries (who is logged in, what are user permissions). This separation aligns well with CQRS patterns.

### API Design

**If you chose REST**: Bearer token authentication (JWT or OAuth access tokens) aligns naturally with REST APIs. Tokens are included in the Authorization header, and REST endpoints can validate tokens independently. OAuth 2.0 is the standard for REST API authentication.

**If you chose GraphQL**: JWT tokens work well with GraphQL. Tokens can be included in HTTP headers or GraphQL context, and resolvers can access authenticated user information. OAuth 2.0 client credentials flow enables service-to-service GraphQL queries.

## Evolution Triggers

### Moving from Single Service to Multiple Services

When your application evolves from a monolith to microservices, session-based authentication becomes challenging due to shared session storage requirements. Consider migrating to JWT tokens or OAuth 2.0 to enable stateless authentication across services. The gateway can validate tokens once, and services can operate independently.

### Adding Third-Party Integrations That Need API Access

When you need to provide API access to third-party applications, OAuth 2.0 becomes essential. Third parties expect OAuth 2.0 flows for secure API access. This may require migrating from session-based or simple JWT authentication to full OAuth 2.0 implementation.

### Compliance Requirements Mandating Specific Auth Standards

Regulatory requirements (SOC 2, HIPAA, PCI-DSS) or customer requirements may mandate specific authentication standards. Some enterprises require SAML for SSO, while others require OAuth 2.0. Compliance drivers may force migration from custom authentication to standards-based approaches.

### Need for Fine-Grained Authorization Beyond Simple Roles

When authorization requirements evolve beyond simple role-based checks (e.g., "user can edit documents they own or documents shared with their team"), consider migrating from RBAC to ABAC or ReBAC. This may require changes to how authorization claims are encoded in tokens or how authorization decisions are made.

### Security Incidents Requiring Immediate Revocation

If you experience security incidents that require immediate revocation of compromised credentials, session-based authentication or OAuth 2.0 with stateful refresh tokens provides better revocation capabilities than stateless JWTs. This may trigger migration from stateless to stateful authentication.

### Scale Requirements Exceeding Session Storage Capacity

If your application scales beyond what your session storage (Redis cluster) can handle, migrating to stateless JWT authentication eliminates session storage requirements. This is a scalability-driven migration trigger.

### User Demand for SSO

When users or customers request single sign-on capabilities, OAuth 2.0 / OpenID Connect becomes necessary. This enables integration with identity providers and SSO across multiple applications.
