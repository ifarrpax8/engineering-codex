# SPA to MFE

A guide for evolving frontend architecture as your application and team grow. Like backend evolution, each stage is valid at the right scale.

## The Journey

```
Single Page Application (SPA) → Multi-Page SPA → Micro-Frontend (MFE)
```

## Stage 1: Single Page Application (SPA)

**What it is:** A single frontend application bundle serving all features, typically with client-side routing.

**When it's right:**
- Small team (1-5 frontend developers)
- Single product or feature area
- Unified user experience with tight feature integration
- Rapid development and iteration phase

**Strengths:**
- Simple build and deployment
- Shared state and routing is straightforward
- Easy to maintain consistent UX
- Fast development with a single codebase

**Watch for these signals:**
- Build times becoming slow (>2 minutes)
- Merge conflicts increasing due to team size
- Bundle size growing beyond reasonable limits
- Teams stepping on each other's code
- Difficulty deploying one feature without risking another

## Stage 2: Multi-Page SPA

**What it is:** A single application with route-based code splitting, lazy loading, and clear feature boundaries within the codebase.

**When to transition from SPA:**
- Bundle size is affecting load performance
- Team needs better code organization
- Features are logically independent but share a shell

**How to transition:**
1. Implement route-based code splitting
2. Organize code by feature (not by type)
3. Define clear boundaries between feature modules
4. Minimize cross-feature dependencies
5. Use lazy loading for non-critical routes

**Strengths:**
- Improved load performance through code splitting
- Better code organization
- Still a single deployment unit (simple operations)
- Gradual migration from SPA patterns

**Watch for these signals:**
- Multiple teams needing independent deployment cadences
- Features needing different framework versions or libraries
- Single deployment pipeline becoming a bottleneck
- Need for independent feature development and release

## Stage 3: Micro-Frontend (MFE)

**What it is:** Multiple independently built and deployed frontend applications composed together at runtime, typically within a shell application.

**When to transition from Multi-Page SPA:**
- Multiple frontend teams need independent deployment
- Features are owned by different teams with different release cadences
- Need for technology diversity (though this should be a last resort)
- Application is large enough that independent scaling of development effort is needed

**Prerequisites:**
- Shared design system / component library (e.g., Propulsion) to maintain UX consistency
- Shell application or composition framework (Module Federation, single-spa, etc.)
- Clear routing and navigation contract between MFEs
- Shared authentication approach → [Authentication](../facets/authentication/options.md)
- Cross-MFE communication patterns defined → [State Management](../facets/state-management/options.md)

**How to transition:**
1. Build a shell application that handles routing and shared concerns
2. Extract one feature area at a time into its own MFE
3. Define communication contracts between MFEs (events, shared state, URL params)
4. Establish shared dependencies strategy (shared vs duplicated)
5. Implement consistent error handling and loading states across MFEs

**Strengths:**
- Independent deployment per feature/team
- Team autonomy and ownership
- Fault isolation (one MFE crashing doesn't take down others)
- Independent technology choices (with caution)

**Risks:**
- UX inconsistency if design system isn't enforced
- Increased bundle size from duplicated dependencies
- Complex integration testing across MFEs
- Shared state and communication patterns add complexity
- User experience seams at MFE boundaries

**Related facets:**
- [Frontend Architecture](../facets/frontend-architecture/options.md) -- Architecture pattern options
- [State Management](../facets/state-management/options.md) -- Cross-MFE state patterns
- [Navigation](../experiences/navigation/options.md) -- Cross-MFE navigation UX
- [Loading & Perceived Performance](../experiences/loading-and-perceived-performance/options.md) -- MFE loading strategies

## Anti-Patterns

- **Premature MFE** -- Splitting into MFEs before the team or product warrants it. The overhead isn't justified for small teams.
- **Shared mutable state** -- MFEs directly sharing state creates tight coupling. Prefer event-based communication.
- **Inconsistent UX** -- Each MFE looking and behaving differently. A shared design system is non-negotiable.
- **MFE per component** -- MFEs should represent meaningful feature areas, not individual components.

## Decision Framework

See [scaling-triggers.md](scaling-triggers.md) for the universal triggers that apply across this journey.
