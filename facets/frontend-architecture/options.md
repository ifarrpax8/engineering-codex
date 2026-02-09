---
recommendation_type: decision-matrix
---

# Frontend Architecture -- Options

## Contents

- [Options](#options)
- [MFE Composition Options](#mfe-composition-options)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Options

### Single Page Application (SPA)

A Single Page Application is a frontend architecture where a single JavaScript bundle manages the entire application. The browser loads the application once, and subsequent navigation happens entirely on the client side through JavaScript routing. All routes, components, and features are part of the same codebase and deployed together as a single unit.

**Strengths:**
- Simple deployment model with a single build and deployment pipeline
- Consistent versions across all features, eliminating compatibility concerns
- Straightforward routing with framework routers (Vue Router, React Router) handling all navigation
- Easier debugging and development with a single codebase and unified tooling
- Lower operational complexity without shell applications or MFE orchestration

**Weaknesses:**
- Deployment coordination required when multiple teams work on the same codebase
- Merge conflicts and coordination overhead as team size grows
- Larger initial bundle size unless aggressive code splitting is implemented
- All features must be compatible with the same dependency versions
- Single point of failure—a bug in one feature can affect the entire application

**Best For:**
- Small to medium teams (1-5 frontend developers) working on a single application
- Applications where features are tightly integrated and share significant code
- Teams that can coordinate deployments and don't need independent release cycles
- Applications where initial bundle size is less critical than development simplicity

**Avoid When:**
- Multiple teams need to deploy independently without coordination
- Team size exceeds 5-7 frontend developers and coordination becomes a bottleneck
- Different parts of the application need different dependency versions or upgrade schedules
- Deployment independence provides significant business value (A/B testing, gradual rollouts)

### Micro-Frontend (MFE)

Micro-Frontend architecture decomposes a frontend application into independently built and deployed applications that compose at runtime. Each MFE is a complete application with its own repository, build process, and deployment pipeline. A shell application orchestrates these MFEs, handling routing, authentication, and shared layout.

**Strengths:**
- Deployment independence enables teams to ship features without coordination
- Team autonomy with each team owning their MFE end-to-end
- Technology flexibility allowing different MFEs to use different frameworks if needed
- Parallel development with teams working independently without merge conflicts
- Independent optimization of bundles per MFE domain

**Weaknesses:**
- Significant operational complexity with shell applications and MFE orchestration
- Shared dependency management requiring version coordination across MFEs
- Cross-MFE communication complexity through events or URL parameters
- Integration testing overhead to verify MFE composition works correctly
- Potential for inconsistent UX if design system governance is weak

**Best For:**
- Large organizations with multiple frontend teams (5+ developers per team)
- Applications where deployment independence provides business value
- Teams that need to work in parallel without coordination overhead
- Domains that are naturally separable with clear boundaries

**Avoid When:**
- Small teams where MFE overhead outweighs benefits
- Tightly integrated features that share significant code and state
- Applications where consistency is more important than team autonomy
- Teams that can't invest in shell application development and MFE tooling

### Server-Side Rendering (SSR)

Server-Side Rendering generates HTML on the server for each request, sending fully-rendered pages to the browser. The browser receives HTML that's immediately renderable, then "hydrates" this HTML by attaching JavaScript event handlers. Frameworks like Nuxt (Vue) and Next.js (React) provide SSR capabilities.

**Strengths:**
- Superior SEO with fully-rendered HTML that search engines can index immediately
- Faster initial load with content visible before JavaScript executes
- Better social media sharing with proper meta tags and Open Graph data in HTML
- Improved performance on slow networks or devices with content-first rendering
- Progressive enhancement where core content works without JavaScript

**Weaknesses:**
- Increased complexity with code running in both server and client environments
- Server rendering overhead that can slow response times for complex pages
- Hydration mismatches if server and client render different HTML
- More complex deployment requiring Node.js servers and SSR infrastructure
- Higher operational cost compared to static SPA hosting

**Best For:**
- Public-facing content where SEO is critical (marketing pages, product listings, blogs)
- Applications where initial load performance significantly impacts user experience
- Content-heavy applications where users consume information more than interact
- Teams that can invest in SSR infrastructure and operational complexity

**Avoid When:**
- Internal applications where SEO is irrelevant
- Highly interactive applications where client-side performance matters more than initial load
- Teams that can't support Node.js server infrastructure
- Applications where simplicity is more valuable than SEO or initial load performance

## MFE Composition Options

### Module Federation

Module Federation is a Webpack 5 and Vite feature that enables runtime sharing of JavaScript modules across independently built applications. The shell application and MFEs are separate builds that share dependencies and expose modules to each other at runtime.

**Strengths:**
- Native bundler support with Webpack 5 or Vite plugins handling complexity
- Runtime module sharing preventing duplicate dependency bundling
- Framework-agnostic approach working with any JavaScript framework
- Good developer experience with standard build tooling and workflows

**Weaknesses:**
- Requires compatible bundler versions across shell and MFEs
- Version management complexity ensuring shared dependencies are compatible
- Learning curve for Module Federation configuration and concepts
- Less flexible than single-spa for non-standard composition patterns

**When to Use:**
- Teams already using Webpack 5 or Vite as build tooling
- MFEs built with the same framework (all Vue or all React)
- Need for runtime dependency sharing to reduce bundle duplication
- Preference for build-time composition over runtime orchestration

### single-spa

single-spa is a framework-agnostic micro-frontend orchestration library that defines a lifecycle API for composing applications. MFEs implement bootstrap, mount, unmount, and update methods, and single-spa coordinates their execution based on routing.

**Strengths:**
- True framework agnosticism enabling Vue, React, Angular, and vanilla JS MFEs
- Flexible composition patterns not limited by bundler capabilities
- Lifecycle-based approach providing fine-grained control over MFE behavior
- Works with any build tooling since it operates at runtime

**Weaknesses:**
- More manual integration work wrapping framework code in lifecycle methods
- Less automatic dependency sharing requiring manual externals configuration
- Steeper learning curve understanding lifecycle methods and orchestration
- More boilerplate compared to Module Federation's automatic handling

**When to Use:**
- Need to compose MFEs built with different frameworks
- Require fine-grained control over MFE lifecycle and mounting
- Prefer runtime orchestration over build-time module sharing
- Building a shell application that needs maximum flexibility

### Web Components

Web Components provide browser-native encapsulation through Custom Elements and Shadow DOM. MFEs built as Web Components are framework-agnostic at the composition layer, with the shell application including custom elements without knowing their internal implementation.

**Strengths:**
- Native browser encapsulation with Shadow DOM providing style and DOM isolation
- Framework agnosticism at the composition layer regardless of internal implementation
- Standard web APIs requiring no special build tooling or frameworks
- Strong isolation preventing CSS and DOM conflicts between MFEs

**Weaknesses:**
- Less integration with framework ecosystems (routing, state management)
- Shadow DOM isolation making global design system styles harder to apply
- More manual work implementing custom elements and lifecycle
- Limited tooling and ecosystem compared to framework-based approaches

**When to Use:**
- Need maximum style and DOM isolation between MFEs
- Building widget-like MFEs with clear boundaries and limited shell integration
- Prefer web standards over framework-specific solutions
- MFEs are relatively independent with minimal cross-MFE communication

## Evaluation Criteria

| Criterion | Weight | SPA | MFE | SSR |
|----------|--------|-----|-----|-----|
| **Team Independence** | High | Low - Single codebase requires coordination | High - Independent repos and deployments | Medium - Single codebase but can organize by route |
| **Performance** | High | Medium - Good with code splitting, but initial bundle can be large | Medium - Per-MFE optimization possible, but total size can be large | High - Fast initial load, but requires server infrastructure |
| **Complexity** | High | Low - Simple deployment and development model | High - Shell apps, orchestration, shared dependencies | Medium - Server/client code, hydration concerns |
| **Developer Experience** | Medium | High - Single codebase, unified tooling | Medium - More moving parts, but team autonomy | Medium - SSR-specific patterns to learn |
| **UX Consistency** | Medium | High - Single codebase ensures consistency | Medium - Requires design system governance | High - Server rendering ensures consistent output |
| **SEO** | Low | Low - Client-side rendering | Low - Client-side rendering | High - Server-rendered HTML |
| **Deployment Flexibility** | Medium | Low - Coordinated deployments | High - Independent deployments | Low - Coordinated deployments |

**Scoring Notes:**
- Team Independence: How easily can teams work and deploy independently?
- Performance: How does the architecture impact load time and runtime performance?
- Complexity: What is the operational and development complexity?
- Developer Experience: How productive are developers working with this architecture?
- UX Consistency: How easy is it to maintain consistent user experience?
- SEO: How well does the architecture support search engine optimization?
- Deployment Flexibility: How independently can features be deployed?

## Recommendation Guidance

**Default Choice: SPA**

For most applications, start with a well-structured Single Page Application. Use feature-based folder organization, route-based code splitting, and shared design system components. This provides excellent developer experience, good performance, and simplicity while supporting team growth through code organization.

**Evolve to MFE When:**
- Team size exceeds 5-7 frontend developers and coordination becomes a bottleneck
- Multiple teams need to deploy independently without coordination
- Deployment independence provides business value (A/B testing, gradual rollouts, faster feature shipping)
- Build times exceed 2 minutes and slow developer feedback loops
- Teams frequently step on each other's code despite good organization

**Choose SSR When:**
- SEO is critical for business success (public marketing pages, product listings)
- Initial load performance significantly impacts user experience and conversion
- Content-heavy applications where users consume information more than interact
- Social media sharing with rich previews is important

**Hybrid Approaches:**
- SPA for internal/admin applications, SSR for public-facing content
- MFE with SSR shell for public pages, client-side MFEs for authenticated areas
- Route-based rendering strategy (SSR for some routes, SPA for others)

## Synergies

### Backend Architecture Alignment

**Microservices → MFE:** When the backend uses microservices architecture, MFE architecture aligns naturally. Each team can own a vertical slice—frontend MFE plus backend microservice—creating true full-stack team autonomy. The finance team owns both the finance MFE and finance microservice, enabling end-to-end feature development without cross-team coordination.

**Monolith → SPA:** When the backend is a monolith, a monolithic SPA frontend is simpler and more appropriate. The coordination overhead of MFE architecture doesn't provide value when the backend requires coordinated deployments anyway. A well-structured SPA with feature-based organization provides team autonomy through code boundaries without operational complexity.

**Modulith → Hybrid:** A modulith backend (modular monolith) can support either SPA or MFE frontend architectures. SPA works well if frontend teams align with backend modules. MFE works if frontend teams need more independence than backend module boundaries provide.

### Data Persistence Patterns

**Event Sourcing → MFE:** Event-sourced backends enable sophisticated MFE data strategies. Each MFE can subscribe to domain events relevant to its functionality, building specialized read models optimized for its UI needs. The finance MFE might maintain a denormalized invoice list optimized for filtering and sorting, while the order management MFE maintains an order timeline optimized for status tracking.

**CQRS → MFE:** Command Query Responsibility Segregation aligns well with MFE architecture. MFEs can consume specialized read models optimized for their specific query patterns, while write operations go through shared command handlers. This enables MFEs to optimize their data access without affecting other MFEs.

**Traditional CRUD → SPA or MFE:** Standard CRUD backends work with either SPA or MFE architectures. The choice depends on team structure and deployment needs rather than data patterns.

### API Design Patterns

**REST → SPA or MFE:** RESTful APIs work well with both SPA and MFE architectures. SPAs consume REST APIs directly, while MFEs might use a Backend-for-Frontend (BFF) pattern where the shell application aggregates API calls to reduce MFE complexity.

**GraphQL → SPA or MFE:** GraphQL's flexible querying works with both architectures. SPAs can query exactly the data needed for each route. MFEs can use GraphQL to fetch domain-specific data without over-fetching or under-fetching.

**BFF Pattern → MFE:** The Backend-for-Frontend pattern aligns naturally with MFE architecture. Each MFE team can own a BFF that aggregates backend services specific to their domain, creating a clean boundary between frontend and backend while maintaining team autonomy.

### State Management Integration

**Centralized Stores → SPA:** Centralized state management (single Pinia store, single Redux store) works best with SPA architecture where state is naturally shared across routes. MFE architectures require distributed state management with each MFE owning its state.

**Distributed State → MFE:** MFE architectures encourage distributed state where each MFE manages its own domain state. Cross-MFE communication happens through events or URL parameters rather than shared stores, maintaining loose coupling.

## Evolution Triggers

Reconsider frontend architecture decisions when these conditions emerge:

**Team Growth:**
- Frontend team size exceeds 5-7 developers and coordination becomes a bottleneck
- Multiple teams need to work on the same codebase simultaneously
- Merge conflicts and code review backlogs slow development velocity
- Teams frequently block each other despite good code organization

**Deployment Pressure:**
- Deployment coordination delays feature releases by days or weeks
- Teams need to deploy on different schedules (finance team monthly, order team weekly)
- A/B testing or gradual rollouts require independent deployment capability
- Hotfixes are delayed waiting for coordinated release cycles

**Performance Degradation:**
- Initial bundle size exceeds 500KB despite code splitting efforts
- Build times exceed 2-3 minutes, slowing developer feedback
- Route-based code splitting isn't sufficient for performance requirements
- Total MFE bundle size indicates dependency duplication issues

**Operational Complexity:**
- MFE overhead (shell development, integration testing) exceeds benefits
- Shared dependency management becomes unmanageable
- Cross-MFE communication patterns create more problems than they solve
- Team would be more productive with simpler SPA architecture

**Business Requirements:**
- SEO becomes critical (shifting from internal to public-facing application)
- Initial load performance impacts conversion rates significantly
- Social media sharing with rich previews becomes important
- Offline capabilities or progressive web app features are required

**Technology Changes:**
- New framework or build tooling provides better MFE support
- Design system evolves to better support MFE composition patterns
- Browser APIs (like Module Federation) become widely supported
- Team expertise grows to support more complex architectures

When triggers indicate architecture evolution is warranted, plan the migration carefully. SPA to MFE migration requires shell application development, MFE extraction, and integration testing strategy. MFE to SPA consolidation requires merging repositories, unifying build processes, and coordinating dependency versions. Both migrations are significant efforts that require team buy-in and dedicated time.
