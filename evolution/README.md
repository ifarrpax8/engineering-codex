# Evolution Guides

Architecture scaling journeys and inflection point guidance. These guides help you recognize when your current architecture is becoming a constraint and what the next step looks like.

## Guides

| Guide | Description |
|-------|-------------|
| [Monolith to Microservices](monolith-to-microservices.md) | Backend evolution from monolith through modulith to microservices |
| [SPA to MFE](spa-to-mfe.md) | Frontend evolution from single-page application to micro-frontends |
| [Scaling Triggers](scaling-triggers.md) | Universal inflection point triggers that apply across all facets |
| [Manual to Automated Testing](manual-to-automated-testing.md) | Testing maturity from manual-only to continuous testing |
| [Component Library to Design System](component-library-to-design-system.md) | From shared components to a governed design system |

## How to Use

1. Review [scaling-triggers.md](scaling-triggers.md) to understand the universal signals that indicate evolution is needed
2. Read the relevant journey guide for your area of concern
3. Check individual facet `options.md` files for facet-specific evolution triggers
4. Use the `evaluate-options` skill to reassess decisions when triggers are reached

## Key Principle

Evolution is not failure. Starting with a simpler architecture and evolving as needs grow is the correct approach. Premature complexity is more harmful than needing to refactor later. The goal of these guides is to help you recognize the right moment to evolve -- not too early, not too late.

## Connection to Facets

Each facet's `options.md` includes an `## Evolution Triggers` section with facet-specific signals. These guides provide the broader, cross-cutting perspective on architectural evolution.
