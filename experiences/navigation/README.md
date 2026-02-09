---
title: Navigation
type: experience
last_updated: 2026-02-09
tags: [vue-router, react-router, breadcrumbs, deep-linking, sidebar, tabs, mobile-navigation, routing]
---

# Navigation

Information architecture, wayfinding, menu structures, breadcrumbs, and routing patterns that enable users to understand their location and move efficiently through applications.

## TL;DR

- **Default approach**: Use consistent top navigation or sidebar navigation with clear active states, breadcrumbs for depth > 2 levels, and route-based navigation with proper guards
- **Key principle**: Navigation answers three questions: "Where am I?", "Where can I go?", and "How do I get back?"
- **Common gotcha**: Hiding primary navigation behind hamburger menus reduces discoverability—users don't explore what they can't see
- **Where to start**: Establish your information architecture first, then implement route structure, then add navigation UI components with active states and breadcrumbs

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Route architecture, layout patterns, MFE navigation, deep linking
- [Testing](testing.md) -- Route guard testing, accessibility testing, deep link verification, QA perspective
- [Best Practices](best-practices.md) -- Consistent patterns, accessibility, URL design, stack-specific guidance
- [Gotchas](gotchas.md) -- Common pitfalls and anti-patterns to avoid
- [Options](options.md) -- Decision matrix for navigation patterns and routing approaches

## Related Facets

- [Frontend Architecture](../facets/frontend-architecture.md) -- Component structure, state management, routing patterns
- [Accessibility](../facets/accessibility.md) -- Keyboard navigation, screen reader support, focus management
- [Authentication](../facets/authentication.md) -- Route guards, protected routes, permission-based navigation

## Related Experiences

- [Onboarding](../onboarding/README.md) -- First-time user navigation discovery and guidance
- [Search and Discovery](../search-and-discovery/README.md) -- Navigation as complement to search functionality
- [Responsive Design](../responsive-design/README.md) -- Mobile navigation patterns and adaptive layouts
- [Permissions UX](../permissions-ux/README.md) -- Role-based navigation visibility and access control
