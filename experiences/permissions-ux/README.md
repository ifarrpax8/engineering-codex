---
title: Permissions UX
type: experience
last_updated: 2026-02-09
tags: [rbac, abac, fga, hide-disable, request-access, permission-aware, multi-tenant, role-based]
---

# Permissions UX

How access control decisions are communicated to users through the UI — disabled states, hidden elements, request access flows, and role-based adaptation.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Default approach**: Hide navigation items for features users can't access, disable (don't hide) actions within accessible features, always explain why with tooltips, and provide a "Request access" path
- **Key principle**: Server ALWAYS enforces permissions—UI permissions are a convenience layer, never a security boundary
- **Common gotcha**: Flash of unauthorized content when permissions load after initial render, or stale permission cache after role changes
- **Where to start**: Fetch permissions on authentication, store in state management, wrap components with permission checks, implement consistent hide/disable patterns across the app

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Permission-aware components, frontend permission loading, server-client sync, multi-tenant scoping
- [Testing](testing.md) -- Permission enforcement testing, hide vs disable verification, request access flows, QA perspective
- [Best Practices](best-practices.md) -- Server enforcement, hide vs disable patterns, accessibility, stack-specific guidance
- [Gotchas](gotchas.md) -- Common pitfalls: frontend-only checks, stale cache, inconsistent patterns, over-hiding
- [Options](options.md) -- Decision matrix for unauthorized content strategies, permission patterns, storage approaches

## Related Facets

- [Authentication](../facets/authentication.md) -- User identity and session management
- [Security](../facets/security.md) -- Defense in depth, authorization enforcement
- [Frontend Architecture](../facets/frontend-architecture.md) -- Component patterns, state management, conditional rendering

## Related Experiences

- [Navigation](../navigation/README.md) -- Role-based navigation visibility and menu adaptation
- [Settings and Preferences](../settings-and-preferences/README.md) -- Permission management UI and admin controls
- [Multi-Tenancy UX](../multi-tenancy-ux/README.md) -- Tenant-scoped permissions and role adaptation
- [Onboarding](../onboarding/README.md) -- Permission discovery and feature introduction for new users
