---
title: Internationalization
type: facet
last_updated: 2026-02-09
---

# Internationalization

Internationalization (i18n) and localization (l10n) are foundational capabilities that enable software to serve users across different languages, regions, and cultural contexts. Internationalization refers to the architectural work of making code support multiple languages and locales, while localization is the process of adapting content for specific languages and regions. Together, they transform a single-language application into a globally accessible product.

Effective internationalization encompasses far more than translation. It includes proper handling of date and time formats, number and currency formatting, text direction for right-to-left languages, pluralization rules that vary by language, and cultural adaptations in content and imagery. The technical implementation spans frontend message catalogs, backend locale resolution, database storage of multilingual content, and comprehensive testing strategies.

The investment in internationalization pays dividends in market expansion, user satisfaction, and regulatory compliance. However, retrofitting i18n into an existing codebase is exponentially more expensive than building it in from the start. Even applications that initially support only one language benefit from i18n-ready architecture, as it provides flexibility for future growth and makes the codebase more maintainable.

This facet covers the complete spectrum of internationalization concerns, from product strategy and user experience through technical architecture, testing approaches, and operational best practices. It provides guidance for teams working with Java/Kotlin Spring Boot backends, Vue 3 or React frontends, and REST APIs, though many principles apply broadly across technology stacks.

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, market expansion, translation management
- [Architecture](architecture.md) -- Frontend and backend patterns, message catalogs, locale resolution, RTL support, translation workflows
- [Testing](testing.md) -- Visual testing, translation completeness, layout testing, RTL verification, pluralization testing
- [Best Practices](best-practices.md) -- Language-agnostic principles, key organization, interpolation patterns, formatting guidelines
- [Gotchas](gotchas.md) -- Common pitfalls, hardcoded strings, concatenation errors, locale fallback issues
- [Options](options.md) -- Decision matrix for i18n libraries, translation management systems, backend localization approaches

## Related Facets

- [Frontend Architecture](../frontend-architecture/) -- Component architecture patterns that support i18n, reusable i18n-aware components, composition strategies for localized content
- [API Design](../api-design/) -- Locale negotiation via headers and query parameters, localized error responses, content negotiation for multilingual APIs
- [Data Persistence](../data-persistence/) -- Storing multilingual content in databases, translation table patterns, JSONB columns for locale-specific fields, querying localized data
- [Configuration Management](../configuration-management/) -- Locale configuration, default language settings, supported locales registry, environment-specific i18n settings
- [Accessibility](../accessibility/) -- Accessible multilingual content, proper lang attributes, screen reader support for multiple languages, RTL accessibility considerations

## Related Experiences

- [Forms & Validation](../../experiences/forms-and-validation/) -- Localized validation messages, locale-aware input formatting, error message translation, field label internationalization
- [Navigation](../../experiences/navigation/) -- Language switching UX, locale persistence, language selector placement, URL structure for locales
- [Notifications](../../experiences/notifications/) -- Localized notification content, timezone-aware timestamps, culturally appropriate messaging, notification channel preferences by locale
