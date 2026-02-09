---
title: Onboarding
type: experience
last_updated: 2026-02-09
tags: [first-run, guided-tour, empty-state, progressive-disclosure, activation, walkthrough, tooltip]
---

# Onboarding

First-time user experience, progressive disclosure, activation funnels, and guided discovery patterns that help users achieve value quickly while learning your product.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Progressive disclosure is key**: Reveal complexity gradually—don't overwhelm users on day one with every feature
- **Don't front-load complexity**: Show value before asking for configuration; let users experience the product before deep setup
- **Track activation metrics**: Define what "activated" means (completed key action), measure time-to-first-value, and monitor funnel drop-off
- **Start with architecture.md**: Understand onboarding state machines, step tracking, and progressive disclosure patterns before implementing
- **Always provide escape hatches**: Users must be able to skip onboarding; the app must work correctly even if they do

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, activation funnels, success metrics
- [Architecture](architecture.md) -- Onboarding state machines, step tracking, progressive disclosure implementation, data models
- [Testing](testing.md) -- E2E flow testing, skip/dismiss verification, conditional step testing, analytics event testing
- [Best Practices](best-practices.md) -- Skip patterns, contextual guidance, checklist patterns, stack-specific implementations
- [Gotchas](gotchas.md) -- Common pitfalls: mandatory tutorials, non-persistent progress, fragile selectors, stale content
- [Options](options.md) -- Decision matrix: guided tours, checklists, walkthroughs, libraries, analytics approaches

## Related Facets

- [Authentication](../../facets/authentication/) -- First-time user registration, role-based onboarding paths, org setup flows
- [Feature Toggles](../../facets/feature-toggles/) -- Graduated rollout of onboarding flows, A/B testing variants, feature gating by onboarding stage
- [Observability](../../facets/observability/) -- Tracking onboarding funnel metrics, drop-off analysis, activation event monitoring

## Related Experiences

- [Navigation](../navigation/README.md) -- Onboarding tours that guide users through navigation structure, wayfinding for new users
- [Forms and Data Entry](../forms-and-data-entry/README.md) -- Onboarding forms for initial setup, progressive form completion, validation patterns
- [Permissions UX](../permissions-ux/README.md) -- Role-based onboarding paths, showing features based on user permissions, admin vs user flows
- [Notifications](../notifications/README.md) -- Onboarding prompts and tips delivered via notifications, contextual help messages
