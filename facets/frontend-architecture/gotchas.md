# Frontend Architecture -- Gotchas

Common pitfalls and traps when making frontend architecture decisions. These are lessons learned from real projects that can save significant time and rework.

## Shared State Across MFEs

MFEs should own their state. When multiple MFEs share a global store, changes in one MFE's state requirements ripple across all consumers. This creates the same coupling that MFEs were supposed to eliminate.

**What happens**: Team A adds a field to the shared user store. Team B's MFE breaks because it assumed a different shape. Both teams now need to coordinate releases.

**Better approach**: Each MFE manages its own state. For cross-MFE communication, use browser events (CustomEvent), URL parameters, or a lightweight pub/sub bus. Keep shared data minimal -- user identity and tenant context, not application state.

## CSS Isolation Failures

One MFE's styles leak into another, causing visual breakage that only appears in the composed application, never in isolated development.

**What happens**: MFE A defines a global `.button` class. MFE B also has `.button` elements. In isolation, both look fine. Composed together, one overrides the other depending on CSS load order.

**Better approach**: Use CSS Modules, Vue's scoped styles (`<style scoped>`), Tailwind CSS utility classes (no global class names), or Shadow DOM for hard isolation. Always test MFEs in the composed shell, not just in isolation.

## Duplicated Dependencies Inflating Bundle

Two MFEs each bundle their own copy of Vue or React, doubling (or tripling) the total JavaScript the user downloads.

**What happens**: Total bundle size balloons to several megabytes. Users on slower connections experience noticeably longer load times. Core Web Vitals suffer.

**Better approach**: Use Module Federation's shared modules or externals to ensure framework dependencies are loaded once. Monitor total composed bundle size in CI, not just individual MFE sizes. Set a combined budget and fail builds that exceed it.

## MFE Boundaries That Don't Match Team Boundaries

Splitting by UI region (header MFE, sidebar MFE, footer MFE) instead of by domain or feature. This means a single user story touches multiple MFEs and requires cross-team coordination.

**What happens**: Adding a notification bell to the header requires changes in the header MFE (the bell icon), the notification MFE (the dropdown), and the shell (routing events between them). Three teams coordinate for one feature.

**Better approach**: Align MFE boundaries with team ownership and business domains. A "billing" MFE owned by the billing team includes all billing UI -- the navigation item, the pages, and any billing-specific components. The team can ship independently.

## Premature MFE Adoption

Adopting micro-frontends for a small application with a single frontend team. The operational overhead (separate builds, deployment pipelines, shared dependency management, integration testing) exceeds any benefit.

**What happens**: A team of 3 frontend developers now maintains 4 separate repositories, 4 CI pipelines, a shell application, and shared dependency configuration. Velocity drops. Simple changes require touching multiple repos.

**Better approach**: Start with a well-structured SPA using feature-based folder organization and clear module boundaries. When the team grows beyond 5-7 frontend developers and deployment coordination becomes a bottleneck, consider MFE extraction. See [evolution/spa-to-mfe.md](../../evolution/spa-to-mfe.md).

## Version Conflicts in Shared Libraries

MFE A uses Vue 3.3, MFE B uses Vue 3.4. Subtle behavior differences cause bugs that only appear in the composed application.

**What happens**: A composable works correctly in MFE A's version but has a slightly different reactivity behavior in MFE B's version. The bug is intermittent and nearly impossible to reproduce in isolation.

**Better approach**: Pin shared dependency versions across all MFEs. Use a shared configuration or lockfile for critical dependencies. Coordinate upgrades as a team. Module Federation's `singleton: true` and `requiredVersion` help enforce this.

## Over-Engineering Component Abstraction

Creating "flexible" wrapper components around design system components that add configuration options, prop transformations, and conditional rendering -- all to handle hypothetical future requirements.

**What happens**: The team creates `<AppButton>` that wraps the design system `<PrButton>` with additional props for loading states, icon positioning, and size variants. Over time, `<AppButton>` accumulates dozens of props and becomes harder to maintain than the component it wraps. Design system updates require updating the wrapper too.

**Better approach**: Use design system components (Propulsion) directly. If you need a pattern that combines multiple design system components (e.g., a button with a loading spinner), create a composition component for that specific use case rather than a generic wrapper.

## Route Conflicts Across MFEs

Two MFEs claim the same route prefix, or route changes in one MFE break deep links in another.

**What happens**: MFE A owns `/settings/*` routes. MFE B adds a `/settings/billing` page. Both MFEs try to render at the same URL. The result depends on which MFE loads first.

**Better approach**: Establish a route registry or naming convention in the shell application. Each MFE owns a clearly defined route prefix. The shell is the source of truth for top-level routing. Document route ownership and enforce it in code review.

## Client-Side Routing Without Server Configuration

Deploying an SPA with client-side routing but forgetting to configure the server to handle deep links.

**What happens**: Users bookmark `/dashboard/reports/quarterly`. When they navigate directly to that URL, the server returns 404 because no file exists at that path. Only navigating from the root URL works.

**Better approach**: Configure the web server (nginx, CloudFront, etc.) to serve `index.html` for all routes that don't match a static file. This is a one-time configuration but is missed surprisingly often, especially when deploying to new environments.

## Treating the Frontend as a "Thin Client"

Pushing all logic to the backend and treating the frontend as a pure rendering layer. The frontend becomes a form-to-API translation layer with no domain intelligence.

**What happens**: Every user interaction requires an API call. Form validation only happens server-side, so users wait for a round trip to see validation errors. Optimistic updates are impossible because the frontend has no understanding of business rules.

**Better approach**: Duplicate critical validation rules on the frontend (the backend remains the source of truth, but the frontend provides immediate feedback). Implement optimistic updates for non-critical operations. Cache reference data locally. The frontend should be smart enough to provide a responsive experience without waiting for every API call.

## Ignoring Accessibility Until Late

Treating accessibility (a11y) as a "nice to have" that can be added later, after the core architecture is in place.

**What happens**: The component architecture doesn't account for focus management, keyboard navigation, or screen reader announcements. Retrofitting these into an existing component tree is significantly harder than building them in from the start. MFE transitions lose focus context.

**Better approach**: Include accessibility in component design from the beginning. Use the design system's built-in accessibility features (Propulsion components are designed with a11y in mind). Test with keyboard navigation and screen readers during development, not just before release. Automate a11y checks with axe-core in component tests and CI.
