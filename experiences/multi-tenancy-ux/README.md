---
title: Multi-Tenancy UX
type: experience
last_updated: 2026-02-09
tags: [tenant, switching, white-labeling, impersonation, data-isolation, tenant-context, branding]
---

# Multi-Tenancy UX

Tenant switching, white-labeling, role-based UI adaptation, and the UX patterns that make multi-tenant B2B SaaS feel personal and secure.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Clear tenant context always visible**: Users must never wonder which organization they're operating in—show tenant name and logo prominently in the header
- **Switching tenants should be fast and obvious**: No logout/login required—instant tenant switch with immediate data refresh and permission updates
- **Never leak data between tenants**: Critical security requirement—clear all cached data, state, and API responses when switching tenants
- **Start with architecture.md**: Understanding tenant context management, data isolation, and white-labeling architecture is foundational
- **Test tenant isolation rigorously**: Cross-tenant data leakage is the worst possible bug—comprehensive testing is non-negotiable

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, success metrics
- [Architecture](architecture.md) -- Tenant context management, data isolation patterns, white-labeling architecture
- [Testing](testing.md) -- Tenant isolation testing, switching flows, cross-tenant security validation
- [Best Practices](best-practices.md) -- Language-agnostic principles and stack-specific guidance
- [Options](options.md) -- Decision matrix for tenant identification, switching UX, white-labeling depth
- [Gotchas](gotchas.md) -- Common pitfalls and critical mistakes to avoid
- [Product](product.md) -- User experience patterns and product requirements

## Related Facets

- [authentication](../facets/authentication.md) -- JWT claims, tenant-aware authentication flows
- [security](../facets/security.md) -- Data isolation, cross-tenant access prevention, audit logging
- [data-persistence](../facets/data-persistence.md) -- Schema-per-tenant vs shared schema patterns, tenant-scoped queries
- [configuration-management](../facets/configuration-management.md) -- Tenant-specific configuration, white-label settings

## Related Experiences

- [permissions-ux](../experiences/permissions-ux.md) -- Role-based UI adaptation per tenant, permission caching
- [settings-and-preferences](../experiences/settings-and-preferences.md) -- Tenant-specific user preferences, notification settings
- [navigation](../experiences/navigation.md) -- Tenant-aware routing, feature visibility per tenant plan
- [design-consistency-and-visual-identity](../experiences/design-consistency-and-visual-identity.md) -- White-labeling, brand consistency, custom themes
