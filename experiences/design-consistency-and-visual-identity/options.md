---
title: Design Consistency & Visual Identity - Options
type: experience
last_updated: 2026-02-09
---

# Options: Design Consistency & Visual Identity

## Contents

- [Design System Approach](#design-system-approach)
  - [Adopt Existing (Propulsion, MUI)](#adopt-existing-propulsion-mui)
  - [Extend Existing (MUI + Custom Theme)](#extend-existing-mui--custom-theme)
  - [Build Custom](#build-custom)
- [Token Management](#token-management)
  - [Style Dictionary](#style-dictionary)
  - [Tailwind Config as Tokens](#tailwind-config-as-tokens)
  - [CSS Custom Properties Only](#css-custom-properties-only)
  - [Figma Tokens Plugin](#figma-tokens-plugin)
- [Visual Regression Tooling](#visual-regression-tooling)
  - [Chromatic](#chromatic)
  - [Percy](#percy)
  - [Playwright Visual Comparisons](#playwright-visual-comparisons)
  - [BackstopJS](#backstopjs)
- [Theming Strategy](#theming-strategy)
  - [CSS Custom Properties (Runtime)](#css-custom-properties-runtime)
  - [Build-Time Theme Injection](#build-time-theme-injection)
  - [Theme Provider (React Context / Vue provide)](#theme-provider-react-context--vue-provide)
  - [Tailwind Dark Mode](#tailwind-dark-mode)
- [Component Documentation](#component-documentation)
  - [Storybook](#storybook)
  - [Histoire (Vue)](#histoire-vue)
  - [Custom Docs Site](#custom-docs-site)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Design System Approach

### Adopt Existing (Propulsion, MUI)

**Description**: Use an established design system with minimal customization.

**Strengths**:
- Fast to implement—components ready to use
- Well-tested, accessible, documented
- Community support and updates
- Consistent with design system's design language

**Weaknesses**:
- Less brand differentiation
- May not fit all use cases perfectly
- Dependency on external project
- Learning curve for team

**Best For**:
- Projects requiring rapid development
- Teams without dedicated design system resources
- Applications where brand differentiation is less critical
- Propulsion: Pax8 projects where it's mandatory
- MUI: React projects needing comprehensive component library

**Avoid When**:
- Strong brand requirements that conflict with design system
- Need for highly unique visual identity
- Design system doesn't support required components

### Extend Existing (MUI + Custom Theme)

**Description**: Use design system as foundation but customize theme, add custom components.

**Strengths**:
- Faster than building from scratch
- Maintains design system benefits (accessibility, testing)
- Allows brand customization
- Can contribute back to design system

**Weaknesses**:
- Customizations may break on updates
- More maintenance than pure adoption
- Risk of over-customization
- Need to understand design system internals

**Best For**:
- Projects needing brand differentiation
- Teams with design system expertise
- Long-term projects with dedicated resources
- When design system covers 80% of needs

**Avoid When**:
- Customizations would be too extensive (consider custom build)
- Team lacks design system knowledge
- Frequent design system updates would break customizations

### Build Custom

**Description**: Create design system from scratch, including tokens, components, documentation.

**Strengths**:
- Complete control over design language
- No external dependencies
- Perfect fit for brand requirements
- Intellectual property ownership

**Weaknesses**:
- Very slow to implement (months/years)
- Requires dedicated design system team
- Must solve accessibility, testing, documentation
- High maintenance burden

**Best For**:
- Large organizations with dedicated design system team
- Unique brand requirements that can't be met by existing systems
- Long-term strategic investment
- When existing systems fundamentally don't fit

**Avoid When**:
- Small teams or tight timelines
- Can achieve goals with existing system
- Lack of design system expertise
- Budget constraints

## Token Management

### Style Dictionary

**Description**: Transform design tokens into platform-specific formats (CSS, JS, iOS, Android) from single JSON source.

**Strengths**:
- Single source of truth
- Multi-platform support
- Well-documented, mature tool
- Integrates with design tools (Figma)

**Weaknesses**:
- Additional build step
- Learning curve
- May be overkill for web-only projects

**Best For**:
- Multi-platform projects (web, iOS, Android)
- Design token-heavy projects
- Teams using Figma Tokens plugin
- Need for automated token generation

**Avoid When**:
- Web-only projects (simpler solutions exist)
- Small projects with few tokens
- Team prefers simpler tooling

### Tailwind Config as Tokens

**Description**: Define design tokens in Tailwind configuration, use as utility classes.

**Strengths**:
- No additional tooling—part of Tailwind
- Utility-first approach (fast development)
- Excellent developer experience
- Tree-shaking built-in

**Weaknesses**:
- Tailwind-specific (not framework-agnostic)
- Less semantic than CSS custom properties
- Can lead to utility class sprawl
- Harder to use tokens outside Tailwind

**Best For**:
- Projects already using Tailwind
- Utility-first development approach
- Rapid prototyping and development
- Teams comfortable with Tailwind

**Avoid When**:
- Not using Tailwind
- Need for runtime theming (limited support)
- Prefer semantic class names
- Multi-framework projects

### CSS Custom Properties Only

**Description**: Define tokens as CSS custom properties, use directly in stylesheets.

**Strengths**:
- Native browser support (no build step)
- Runtime theming support
- Framework-agnostic
- Simple, no tooling required

**Weaknesses**:
- No type safety (TypeScript)
- Manual management (no automated generation)
- No multi-platform support
- Can become disorganized at scale

**Best For**:
- Small to medium projects
- Runtime theming requirements
- Framework-agnostic needs
- Simplicity preference

**Avoid When**:
- Large, complex token systems
- Need for type-safe tokens
- Multi-platform projects
- Want automated token generation

### Figma Tokens Plugin

**Description**: Design tokens defined in Figma, synced to code via plugin.

**Strengths**:
- Design-code parity
- Designers manage tokens directly
- Automated sync from design to code
- Visual token management

**Weaknesses**:
- Requires Figma adoption
- Plugin dependency
- May require Style Dictionary for code generation
- Learning curve for designers

**Best For**:
- Design-heavy teams using Figma
- Strong design-developer collaboration
- Need for design-code sync
- Designers managing tokens

**Avoid When**:
- Not using Figma
- Developers managing tokens
- Simple token systems
- Prefer code-first approach

## Visual Regression Tooling

### Chromatic

**Description**: Visual testing integrated with Storybook. Automatic visual diffs for component changes.

**Strengths**:
- Seamless Storybook integration
- Excellent developer experience
- Automatic baseline management
- Cloud-hosted (no infrastructure)

**Weaknesses**:
- Paid service (costs scale with usage)
- Storybook-specific (less useful for E2E tests)
- Requires Storybook adoption

**Best For**:
- Projects using Storybook
- Component-level visual testing
- Teams wanting managed service
- Budget for tooling

**Avoid When**:
- Not using Storybook
- Tight budget constraints
- Need for E2E visual testing only
- Prefer self-hosted solutions

### Percy

**Description**: Visual testing platform that works with any testing framework (Playwright, Cypress, etc.).

**Strengths**:
- Framework-agnostic
- Works with E2E and component tests
- Good browser coverage
- Cloud-hosted

**Weaknesses**:
- Paid service
- Less integrated than Chromatic (for Storybook)
- Can be slower than self-hosted

**Best For**:
- E2E visual testing
- Multi-framework projects
- Teams wanting managed service
- Need for cross-browser testing

**Avoid When**:
- Tight budget
- Prefer self-hosted
- Only component testing (Chromatic better)
- Simple screenshot comparison needs

### Playwright Visual Comparisons

**Description**: Built-in visual comparison using Playwright's screenshot capabilities.

**Strengths**:
- No additional tooling (part of Playwright)
- Free, open-source
- Good for E2E tests
- CI/CD integration

**Weaknesses**:
- Manual baseline management
- Less polished than dedicated tools
- No cloud storage/history
- Requires infrastructure for storage

**Best For**:
- Projects already using Playwright
- E2E visual testing
- Budget-conscious teams
- Self-hosted CI/CD

**Avoid When**:
- Need for component-level testing
- Want managed service
- Need visual diff history/review UI
- Not using Playwright

### BackstopJS

**Description**: Open-source visual regression testing tool with configuration-based approach.

**Strengths**:
- Free, open-source
- Self-hosted
- Good for E2E testing
- Configurable scenarios

**Weaknesses**:
- Requires more setup than managed services
- Less polished UI
- Manual baseline management
- Smaller community than Playwright

**Best For**:
- Budget-conscious teams
- Self-hosted requirements
- E2E visual testing
- Need for custom scenarios

**Avoid When**:
- Want managed service
- Need component-level testing
- Prefer integrated solutions
- Limited infrastructure resources

## Theming Strategy

### CSS Custom Properties (Runtime)

**Description**: Theme defined via CSS custom properties, switched at runtime via JavaScript.

**Strengths**:
- True runtime theming (no rebuild)
- Framework-agnostic
- Simple implementation
- Good performance

**Weaknesses**:
- No type safety
- Manual management
- Can become complex with many themes

**Best For**:
- User-selectable themes
- Runtime theme switching
- Simple theming needs
- Framework-agnostic projects

**Avoid When**:
- Need for type-safe themes
- Complex theme logic
- Build-time optimization preferred

### Build-Time Theme Injection

**Description**: Theme values injected at build time, separate builds for each theme.

**Strengths**:
- Optimized bundles (only one theme per build)
- Type-safe (TypeScript)
- No runtime theme switching overhead

**Weaknesses**:
- Requires rebuild for theme change
- Multiple builds needed
- Can't switch themes at runtime

**Best For**:
- Single theme per deployment
- White-label products (different builds per brand)
- Performance-critical applications
- Type-safe theme requirements

**Avoid When**:
- User-selectable themes
- Need for runtime switching
- Single deployment with multiple themes

### Theme Provider (React Context / Vue provide)

**Description**: Theme managed via framework's context/provide system, components consume theme values.

**Strengths**:
- Framework-integrated
- Type-safe (TypeScript)
- Good developer experience
- Component-level theme access

**Weaknesses**:
- Framework-specific
- Runtime overhead (context propagation)
- More complex than CSS custom properties

**Best For**:
- React or Vue projects
- Type-safe theme requirements
- Component-level theme logic
- Framework-native approach preferred

**Avoid When**:
- Framework-agnostic needs
- Simple theming (CSS custom properties simpler)
- Performance-critical (CSS custom properties faster)

### Tailwind Dark Mode

**Description**: Tailwind's built-in dark mode using `dark:` variant.

**Strengths**:
- Integrated with Tailwind
- Simple utility classes
- Good developer experience
- No additional setup

**Weaknesses**:
- Tailwind-specific
- Less flexible than custom properties
- Class-based (not CSS custom properties)

**Best For**:
- Projects using Tailwind
- Simple light/dark mode
- Utility-first approach
- Rapid development

**Avoid When**:
- Multiple themes (beyond light/dark)
- Need for runtime theme switching
- Not using Tailwind
- Complex theme logic

## Component Documentation

### Storybook

**Description**: Isolated component development environment with interactive documentation.

**Strengths**:
- Industry standard
- Excellent developer experience
- Visual regression testing integration (Chromatic)
- Rich addon ecosystem
- Works with React, Vue, Angular

**Weaknesses**:
- Additional build step
- Can become stale if not maintained
- Learning curve

**Best For**:
- Component library development
- Design system documentation
- Visual regression testing needs
- Multi-framework support

**Avoid When**:
- Simple projects with few components
- Prefer lighter documentation
- Not building reusable components

### Histoire (Vue)

**Description**: Storybook alternative specifically for Vue 3.

**Strengths**:
- Vue-optimized
- Faster than Storybook (Vite-based)
- Simpler configuration
- Good TypeScript support

**Weaknesses**:
- Vue-only
- Smaller ecosystem than Storybook
- Less mature

**Best For**:
- Vue 3 projects
- Prefer simpler tooling
- Want Vite performance
- Vue-specific features needed

**Avoid When**:
- Multi-framework projects
- Need Storybook ecosystem
- Prefer industry standard
- React/Angular projects

### Custom Docs Site

**Description**: Build custom documentation site (e.g., using Docusaurus, VitePress, Next.js).

**Strengths**:
- Complete control
- Can integrate with existing docs
- Custom features possible
- Branded experience

**Weaknesses**:
- More development time
- Must build component playground
- More maintenance
- Less feature-rich than Storybook

**Best For**:
- Need for integrated documentation (API + components)
- Custom documentation requirements
- Existing docs infrastructure
- Branded documentation needs

**Avoid When**:
- Want component-focused tooling
- Prefer established solutions
- Limited development resources
- Standard documentation needs

## Recommendation Guidance

### For New Projects

1. **Design System**: Adopt Propulsion (if mandatory) or MUI (React) / Vuetify (Vue)
2. **Token Management**: CSS custom properties for simplicity, Style Dictionary if multi-platform
3. **Visual Regression**: Chromatic (if Storybook) or Playwright (if E2E focus)
4. **Theming**: CSS custom properties for runtime theming, Theme Provider for type safety
5. **Documentation**: Storybook for component libraries, custom docs for integrated documentation

### For Existing Projects

1. **Assess current state**: Audit existing components, identify inconsistencies
2. **Gradual migration**: Introduce design system incrementally, don't rewrite everything
3. **Establish governance**: Design system team, review process, adoption metrics
4. **Tooling**: Add visual regression testing, token validation linting
5. **Documentation**: Update Storybook/docs as you migrate components

## Synergies

- **Storybook + Chromatic**: Seamless visual regression testing for components
- **Style Dictionary + Figma Tokens**: Design-to-code token workflow
- **Tailwind + CSS Custom Properties**: Use Tailwind for utilities, custom properties for theming
- **MUI + Custom Theme**: Extend MUI with brand tokens via `createTheme`
- **Playwright + Visual Comparisons**: E2E testing with built-in visual regression

## Evolution Triggers

**Re-evaluate design system approach when**:
- Design system no longer meets needs (consider extending or custom build)
- Team grows significantly (may need dedicated design system team)
- Brand requirements change dramatically
- Design system becomes bottleneck (updates too slow, too restrictive)

**Re-evaluate token management when**:
- Tokens become unmanageable (consider Style Dictionary)
- Need for multi-platform support (Style Dictionary)
- Runtime theming becomes critical (CSS custom properties)

**Re-evaluate visual regression when**:
- Test maintenance becomes burden (consider managed service)
- Need for better diff review (consider Chromatic/Percy)
- Budget allows for tooling investment

**Re-evaluate theming when**:
- User-selectable themes needed (CSS custom properties or Theme Provider)
- Performance becomes concern (build-time injection)
- Multiple brands/white-label needed (build-time or CSS custom properties)
