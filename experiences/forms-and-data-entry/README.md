---
title: Forms and Data Entry
type: experience
last_updated: 2026-02-09
tags: [forms, validation, wizard, multi-step, vuelidate, zod, react-hook-form, input, draft]
---

# Forms and Data Entry

Input patterns, validation, multi-step flows, inline editing, and wizard forms that guide users through complex data entry workflows.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Default approach**: Use controlled components with client-side validation (Zod/Yup) and server-side validation (Spring @Valid), with clear error messaging and progressive disclosure for complex forms
- **Key principle**: Validate on blur (not keystroke), show errors after first submission attempt, and always provide clear feedback about form state and progress
- **Common gotcha**: Multi-page wizard forms lose state on browser back/forward navigation if not properly managed with URL-driven routing and draft persistence
- **Where to start**: Begin with single-page forms using React Hook Form (React) or VeeValidate (Vue), then evolve to multi-page wizards with step state management and draft persistence when complexity demands it

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, multi-page form UX patterns
- [Architecture](architecture.md) -- Form state management, validation architecture, multi-page wizard patterns, schema-driven forms
- [Testing](testing.md) -- Unit testing validation, component testing, E2E flows, multi-page wizard testing, accessibility testing
- [Best Practices](best-practices.md) -- Inline validation timing, error messaging, progressive disclosure, multi-page form patterns
- [Gotchas](gotchas.md) -- Premature validation, state loss, timezone issues, wizard navigation problems
- [Options](options.md) -- Decision matrix for form libraries, validation libraries, multi-page form approaches

## Related Facets

- [Frontend Architecture](../../facets/frontend-architecture/) -- Component patterns, state management strategies
- [API Design](../../facets/api-design/) -- Form submission endpoints, validation error responses
- [Accessibility](../../facets/accessibility/) -- Form accessibility patterns, ARIA attributes, keyboard navigation
- [State Management](../../facets/state-management/) -- Form state patterns, draft persistence strategies

## Related Experiences

- [Workflows and Tasks](../workflows-and-tasks/) -- Multi-step user journeys, task completion flows
- [Tables and Data Grids](../tables-and-data-grids/) -- Inline editing patterns, bulk data entry
- [Design Consistency and Visual Identity](../design-consistency-and-visual-identity/) -- Form styling, design system integration (Propulsion, MUI)
