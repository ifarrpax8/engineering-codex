---
title: Design Consistency & Visual Identity - Gotchas
type: experience
last_updated: 2026-02-09
---

# Gotchas: Design Consistency & Visual Identity

## Contents

- [Design System Divergence Across Teams](#design-system-divergence-across-teams)
- ["Just This One Exception" Snowball](#just-this-one-exception-snowball)
- [Inconsistent Spacing from Mixing px/rem/em](#inconsistent-spacing-from-mixing-pxremem)
- [Dark Mode as an Afterthought](#dark-mode-as-an-afterthought)
- [MFE Teams Drifting from Shared Tokens](#mfe-teams-drifting-from-shared-tokens)
- [Component Library Version Mismatches Across MFEs](#component-library-version-mismatches-across-mfes)
- [Over-Customizing a Design System](#over-customizing-a-design-system)
- [Storybook/Documentation Going Stale](#storybookdocumentation-going-stale)
- [Design Tokens Defined But Not Enforced](#design-tokens-defined-but-not-enforced)
- [Responsive Breakpoints Inconsistent Across Teams](#responsive-breakpoints-inconsistent-across-teams)
- [Z-Index Wars](#z-index-wars)

## Design System Divergence Across Teams

**Problem**: Team A uses Propulsion v2.1, Team B uses v2.3. Visual inconsistencies emerge as components look slightly different.

**Why it happens**: Teams update dependencies independently, or different teams adopt design system at different times.

**Solution**:
- Lock design system version in `package.json` (exact version, not `^2.1.0`)
- Use shared design token package that all teams consume
- Establish design system governance team to coordinate updates
- Use CSS custom properties from shell app to normalize across versions

**Prevention**: Include design system version in dependency review process. Require design system team approval for version bumps.

## "Just This One Exception" Snowball

**Problem**: "This one page needs different spacing" becomes "these 5 pages need exceptions" becomes "we have 20 different spacing patterns."

**Why it happens**: Pressure to ship quickly, lack of design system enforcement, no review process.

**Solution**:
- Establish "no exceptions" policy with clear escalation path
- Require design system team approval for any deviation
- Use visual regression testing to catch exceptions
- Regular design audits to identify and consolidate exceptions

**Prevention**: Build time into estimates for using design system. Make exceptions harder than using the system.

## Inconsistent Spacing from Mixing px/rem/em

**Problem**: Some components use `px`, others use `rem`, others use `em`. Spacing looks inconsistent, especially when users adjust browser font size.

**Why it happens**: Different developers prefer different units, legacy code uses different units, no standard established.

**Solution**:
- Pick one system (recommend `rem` with 16px base, or `px` via tokens)
- Use design tokens exclusively—never raw values
- Lint rule to prevent raw spacing values
- Migrate legacy code gradually

**Example**:
```css
/* ❌ Bad - mixing units */
.card { padding: 16px; margin: 1rem; }

/* ✅ Good - consistent tokens */
.card { 
  padding: var(--spacing-4); /* 16px or 1rem */
  margin: var(--spacing-4);
}
```

## Dark Mode as an Afterthought

**Problem**: Dark mode added later requires retrofitting all components. Some components break (low contrast, invisible borders).

**Why it happens**: Dark mode not considered during initial design system creation, tokens not designed for theming.

**Solution**:
- Design tokens for theming from the start (semantic color tokens, not raw colors)
- Test all components in both themes during development
- Use CSS custom properties for runtime theme switching

**Prevention**: Include dark mode in initial design system design. Test components in both themes from day one.

## MFE Teams Drifting from Shared Tokens

**Problem**: Each MFE develops its own "brand" over time. Shell app looks cohesive, but MFEs look different from each other.

**Why it happens**: MFE teams work independently, no shared token enforcement, each team makes "small improvements."

**Solution**:
- Shared design token npm package (single source of truth)
- Shell app provides CSS custom properties that MFEs inherit
- Visual regression testing across all MFEs
- Regular design reviews across MFE teams

**Prevention**: Make shared tokens easier to use than custom values. Provide clear documentation and examples.

## Component Library Version Mismatches Across MFEs

**Problem**: MFE A uses MUI v5, MFE B uses MUI v6. Components look different, breaking visual consistency.

**Why it happens**: Teams update dependencies independently, breaking changes in design system versions.

**Solution**:
- Coordinate design system updates across all MFEs
- Use CSS custom properties to abstract component library differences
- Gradual migration plan when major versions change
- Consider wrapper components that normalize differences

**Prevention**: Design system version updates require cross-team coordination. Use shared dependency management.

## Over-Customizing a Design System

**Problem**: So many theme overrides and component customizations that the design system is unrecognizable. Updates become impossible.

**Why it happens**: Desire to match exact designs, not understanding design system philosophy, no governance.

**Solution**:
- Limit customization scope—use design system as-is when possible
- Document all customizations and justify each one
- Regular reviews to identify unnecessary customizations
- Consider if customizations should be contributed back to design system

**Prevention**: Establish customization guidelines. Require design system team approval for significant customizations.

## Storybook/Documentation Going Stale

**Problem**: Components updated in code but Storybook stories not updated. Developers use outdated examples.

**Why it happens**: Documentation treated as separate from code, no process to keep it updated, time pressure.

**Solution**:
- Include Storybook updates in definition of done
- Visual regression testing on Storybook
- Automated checks that Storybook builds successfully
- Regular documentation audits

**Prevention**: Make Storybook part of component development workflow, not afterthought.

## Design Tokens Defined But Not Enforced

**Problem**: Design tokens exist but developers use raw values (`color: #3b82f6` instead of `var(--color-primary)`).

**Why it happens**: No linting rules, tokens not easily discoverable, developers don't know tokens exist.

**Solution**:
- ESLint/Stylelint rules to prevent raw values
- IDE autocomplete for design tokens
- Code review checklist includes "using design tokens"
- Regular token usage audits

**Example lint rule**:
```javascript
// Disallow hex colors, require tokens
'color-no-hex': true,
'declaration-property-value-disallowed-list': {
  'color': ['/#[0-9a-f]{3,6}/i'],
}
```

## Responsive Breakpoints Inconsistent Across Teams

**Problem**: Team A uses `768px` for tablet, Team B uses `1024px`. Layouts break inconsistently.

**Why it happens**: No shared breakpoint definitions, teams define breakpoints independently.

**Solution**:
- Shared breakpoint tokens/constants
- Design system defines breakpoints, teams consume them
- Document breakpoint usage guidelines

**Example**:
```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}
```

**Tailwind**:
```javascript
// tailwind.config.js - shared config
screens: {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
}
```

## Z-Index Wars

**Problem**: Components use arbitrary z-index values (`z-index: 9999`, `z-index: 10000`). Overlapping layers break unpredictably.

**Why it happens**: No z-index scale defined, developers pick random high values, no governance.

**Solution**:
- Define z-index scale in design tokens
- Use semantic z-index tokens

**Example**:
```css
:root {
  --z-index-dropdown: 1000;
  --z-index-sticky: 1100;
  --z-index-fixed: 1200;
  --z-index-modal-backdrop: 1300;
  --z-index-modal: 1400;
  --z-index-popover: 1500;
  --z-index-tooltip: 1600;
}
```

**Prevention**: Lint rule to prevent raw z-index values. Use tokens exclusively.
