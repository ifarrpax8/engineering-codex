---
title: Responsive Design
type: experience
last_updated: 2026-02-09
---

# Responsive Design

Creating interfaces that adapt seamlessly across mobile, tablet, and desktop devices while maintaining functionality and performance.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Default approach**: Mobile-first CSS with Tailwind breakpoints (sm/md/lg/xl/2xl), container queries for component-level responsiveness, and fluid typography using `clamp()`
- **Key principle**: Design for your actual audience—B2B SaaS users primarily work on desktop, but mobile support enables field workers and on-the-go access
- **Common gotcha**: Hover-only interactions break on touch devices—always provide alternative interaction patterns or use click/tap handlers
- **Where to start**: Establish breakpoint system, implement mobile-first CSS, test on real devices (not just DevTools), and prioritize content per viewport

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- CSS patterns, component architecture, breakpoint systems, MFE coordination
- [Testing](testing.md) -- Viewport testing, visual regression, touch targets, QA perspective
- [Best Practices](best-practices.md) -- Mobile-first CSS, touch targets, fluid layouts, stack-specific guidance
- [Gotchas](gotchas.md) -- Common pitfalls and anti-patterns to avoid
- [Options](options.md) -- Decision matrix for responsive strategies and implementation approaches

## Related Facets

- [Frontend Architecture](../facets/frontend-architecture.md) -- Component structure, state management, MFE patterns
- [Performance](../facets/performance.md) -- Mobile performance budgets, image optimization, Core Web Vitals
- [Accessibility](../facets/accessibility.md) -- Touch target sizes, keyboard navigation, screen reader support

## Related Experiences

- [Navigation](../navigation/README.md) -- Responsive navigation patterns (drawer, bottom nav, collapsible sidebar)
- [Tables and Data Grids](../tables-and-data-grids/README.md) -- Responsive table patterns (stacking, scrolling, card views)
- [Design Consistency and Visual Identity](../design-consistency-and-visual-identity/README.md) -- Maintaining design system consistency across breakpoints
- [Loading and Perceived Performance](../loading-and-perceived-performance/README.md) -- Mobile performance optimization and perceived load times
