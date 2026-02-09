# Accessibility

Evaluation criterion for decision matrices across the Engineering Codex.

## Definition

The degree to which the chosen approach supports inclusive design, assistive technology compatibility, and WCAG compliance without requiring significant workarounds.

## What to Evaluate

- **Semantic markup** -- Does the approach produce semantic HTML that screen readers and assistive technologies can interpret?
- **Keyboard navigation** -- Does it support full keyboard operability without trapping focus?
- **ARIA support** -- Does it provide correct ARIA roles, states, and properties out of the box, or does it require manual annotation?
- **Component library maturity** -- If using a component library, does it have accessibility built in and tested (e.g., Propulsion, MUI, Headless UI)?
- **Colour and contrast** -- Does the approach support theming with accessible colour contrast ratios?
- **Testing integration** -- Can accessibility be tested automatically (axe-core, Lighthouse) and in CI/CD?

## Scoring Guide

- **High** -- Accessible by default. Semantic HTML, built-in ARIA support, keyboard navigation, and a mature accessibility testing story. Component library has documented accessibility compliance.
- **Medium** -- Accessibility achievable with moderate effort. May require custom ARIA attributes, manual keyboard handling, or additional testing tooling. Component library has partial accessibility coverage.
- **Low** -- Significant accessibility gaps. Relies on non-semantic markup (canvas, custom widgets) that require extensive manual ARIA work. No built-in keyboard support or testing story.

## Related Resources

- [Accessibility Facet](../../facets/accessibility/) -- Deep dive into accessibility architecture and best practices
- [Accessibility Audit Checklist](../../checklists/accessibility-audit.md) -- WCAG 2.1 AA compliance check
- [Design Consistency Experience](../../experiences/design-consistency-and-visual-identity/) -- Component library accessibility
