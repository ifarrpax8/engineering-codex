# Best Practices: Internationalization

## Contents

- [Never Hardcode User-Facing Strings](#never-hardcode-user-facing-strings)
- [Use Keys, Not English Text](#use-keys-not-english-text)
- [Keep Message Keys Organized by Feature](#keep-message-keys-organized-by-feature)
- [Don't Concatenate Translated Strings](#dont-concatenate-translated-strings)
- [Format Dates and Numbers on the Frontend](#format-dates-and-numbers-on-the-frontend)
- [Design UI for Text Expansion](#design-ui-for-text-expansion)
- [Use ICU Message Format for Pluralization](#use-icu-message-format-for-pluralization)
- [Stack-Specific Callouts](#stack-specific-callouts)

## Never Hardcode User-Facing Strings

Every user-visible string should go through the i18n system, even if the application initially supports only one language. Hardcoded strings create technical debt that compounds over time. When the first translation effort begins, hundreds of hardcoded strings scattered throughout the codebase must be found, extracted, and replaced—a time-consuming and error-prone process.

The discipline of extracting strings into message catalogs from day one costs almost nothing but provides enormous value. It improves code organization by separating content from logic. It makes content updates easier—translators and content writers can update text without touching code. It forces developers to think about string management, reducing duplication and improving consistency.

Enforce i18n usage through code review and linting rules. Configure ESLint or similar tools to flag hardcoded strings in user-facing contexts. Use static analysis tools that detect strings in JSX, template literals, and other user-visible locations. Make i18n usage a non-negotiable code standard.

Even for single-language applications, i18n architecture provides benefits. Message catalogs serve as a single source of truth for all user-facing text, making content audits and updates easier. The key-based lookup system makes it easy to find where text is used and update it consistently. The separation of content from code improves maintainability.

The only exceptions to the "no hardcoded strings" rule are strings that are truly technical and never user-facing: log messages, internal error codes, technical identifiers. However, be conservative—when in doubt, put it through i18n. It's easier to remove an unnecessary translation key than to retrofit i18n for a string that becomes user-facing later.

## Use Keys, Not English Text

Message keys should be descriptive identifiers like `billing.invoice.downloadButton`, not English text like "Download Invoice". Keys are stable across translations—they don't change when translations are updated or when English wording is refined. Using English text as keys creates fragility—any change to English text breaks lookups in all locales.

Descriptive keys serve multiple purposes. They document intent, making it clear what content belongs to which feature. They enable fallback behavior—if a translation is missing, the key provides context about what should be displayed. They facilitate tooling for finding unused translations and identifying missing translations.

Key naming conventions should mirror the application's feature structure. If the codebase is organized by feature modules (billing, users, settings), keys should follow the same organization (`billing.*`, `users.*`, `settings.*`). This makes it easy for developers to find relevant translations and for translators to understand context.

Keys should be hierarchical and namespaced, not flat. A flat structure with hundreds of keys like `save`, `cancel`, `delete` becomes unmaintainable. Hierarchical structures like `common.actions.save`, `common.actions.cancel`, `billing.invoice.actions.delete` scale better and provide context.

Avoid overly generic keys like `message1`, `text2`, `label3`. These provide no context and make translation difficult. Translators need context to produce accurate translations—the word "Save" can mean "save to disk" or "save money," and translators must know which meaning applies.

Include the default English text as a comment or in a separate default locale file. This helps translators understand the intended meaning and provides fallback text if translations are missing. However, the key itself should remain stable even if the English text changes.

## Keep Message Keys Organized by Feature

Organize message keys to mirror the application's feature-based folder structure. If the codebase has modules for billing, user management, and settings, translation keys should follow the same organization: `billing.*`, `users.*`, `settings.*`. This alignment makes it clear which translations belong to which part of the application.

Feature-based organization provides several benefits. Developers working on a feature can easily find relevant translations. Translators can focus on one feature area at a time, improving consistency within features. Feature-based organization scales better than flat structures as the application grows.

Use consistent naming patterns within features. For example, if billing uses `billing.invoice.title`, `billing.invoice.description`, `billing.invoice.actions.download`, maintain similar patterns across features. Consistency makes keys predictable and easier to remember.

Avoid deep nesting—three or four levels is usually sufficient. Keys like `app.features.billing.invoices.list.actions.download.button.label` are unnecessarily verbose. Prefer `billing.invoice.downloadButton` or `billing.invoice.actions.download`.

Group related keys together logically. Actions (save, cancel, delete) should be grouped. Form labels should be grouped. Error messages should be grouped. This organization helps translators understand relationships between messages and maintain consistency.

Document key organization conventions in the codebase. New developers should understand how keys are structured and where to add new keys. This prevents key sprawl and maintains organization as the application evolves.

## Don't Concatenate Translated Strings

Never concatenate translated strings to build messages. The pattern "Hello " + name + ", you have " + count + " items" works in English but breaks in languages with different word order. German might require "Sie haben " + count + " neue Nachrichten, " + name—completely different word order and adjective agreement.

Use interpolation instead: `$t('greeting', { name, count })` with a message like "Hello {name}, you have {count} items". The i18n library handles interpolation, and translators can reorder placeholders as needed for their language's grammar. This approach works across all languages without language-specific code.

Interpolation also handles formatting automatically. Numbers, dates, and other values are formatted according to locale conventions during interpolation. Concatenation requires manual formatting, which is error-prone and may not respect locale conventions.

Complex messages with multiple variables should use structured interpolation. Instead of building messages through multiple concatenations, define a single message with all variables and let translators arrange them appropriately. This ensures grammatical correctness across languages.

Avoid building messages conditionally through concatenation. Patterns like `prefix + (condition ? optionA : optionB) + suffix` break in languages where word order differs. Use conditional messages instead: define separate messages for each condition and select the appropriate one.

The only exception to the "no concatenation" rule is when combining completely independent, standalone strings that don't form a grammatical unit. For example, combining a page title and a site name might be acceptable if they're always displayed separately. However, even in these cases, consider whether a single interpolated message would be clearer.

## Format Dates and Numbers on the Frontend

The backend should return data in locale-neutral formats: ISO 8601 dates, unformatted numbers, currency amounts with currency codes. The frontend formats these values for display using the browser's Intl APIs based on the user's locale. This separation ensures consistency and allows the same API to serve users in different locales.

Formatting on the frontend provides several advantages. The user's locale is known in the frontend context, allowing accurate formatting. Browser Intl APIs handle all locale-specific formatting rules automatically, reducing backend complexity. Frontend formatting enables real-time updates when users change locales without API calls.

Don't send pre-formatted strings from the backend. Formatted strings cannot be reformatted for different locales, cannot be sorted or filtered correctly, and break the separation of concerns between data and presentation. Always return raw data and format it in the frontend.

Use Intl.DateTimeFormat for date formatting. It handles all locale-specific conventions: date order, separator characters, inclusion of day names and time formats. Configure it with the user's locale and appropriate options for the display context (date only, time only, or both).

Use Intl.NumberFormat for number and currency formatting. It handles decimal separators, thousands separators, and currency symbol placement according to locale conventions. Configure it with the user's locale, currency code, and desired precision.

The exception to frontend formatting is email and notification content sent outside the web application. These must be formatted on the backend because the frontend cannot format them. Determine the recipient's locale from user profile, email preferences, or Accept-Language header, and format content accordingly using backend formatting libraries.

Cache formatted values appropriately. Formatting can be expensive for large datasets, so consider memoization or computed properties. However, ensure that cached formatted values update when the locale changes.

## Design UI for Text Expansion

German text is approximately 30% longer than English on average. Many other languages also produce longer text. Arabic text may be taller due to different character shapes. Chinese and Japanese may require different font sizes. UI designs must accommodate text expansion without breaking layouts.

Avoid fixed-width containers for text content. Use flexible layouts that adapt to content length. CSS Grid and Flexbox provide excellent tools for creating flexible layouts that accommodate varying text lengths. When fixed widths are necessary (e.g., table columns), ensure they accommodate the longest expected translations or implement horizontal scrolling.

Design with the longest translations in mind. Identify languages that produce the longest text (often German, Finnish, or languages with compound words) and design layouts to accommodate them. Testing with expanded text during design prevents layout breaks later.

Consider text truncation strategies. When text is too long for its container, truncation with ellipsis may be appropriate, but ensure that truncated text doesn't hide critical information. Consider tooltips or expanding containers for long text. Test truncation behavior with the longest translations.

Responsive design becomes more important with i18n. Text expansion affects layouts differently at different screen sizes. A layout that works on desktop may break on mobile when text is longer. Test responsive layouts with expanded text across breakpoints.

Form layouts require special attention. Labels, help text, and error messages all expand with translation. Ensure that form layouts accommodate longer labels and messages without crowding inputs or breaking alignment. Consider label placement (above inputs vs beside inputs) based on expected text length.

Navigation menus must handle longer text. Horizontal navigation may not accommodate longer translations—consider vertical navigation or responsive menu patterns. Dropdown menus should expand to fit longer items without truncation.

## Use ICU Message Format for Pluralization

Different languages have different plural rules, making simple conditional logic insufficient. English has two plural forms (singular and plural), but Russian has three forms based on the number's ending digit. Arabic has six plural forms. Polish has complex rules involving the last two digits. ICU message format handles this complexity with a standard syntax.

ICU message format provides a language-agnostic way to handle pluralization: `{count, plural, one {# item} other {# items}}`. The i18n library evaluates the count against the language's plural rules and selects the appropriate form. The `#` symbol represents the formatted number. This approach works across all languages without language-specific code.

Use ICU format for all messages involving counts or quantities. This includes item counts, time periods, quantities, and other numeric values that affect grammar. Don't limit ICU usage to obvious cases—review all messages for potential pluralization needs.

Pluralization must be handled in the message itself, not in application logic. Don't write code like "if count === 1 then singular else plural"—this breaks in languages with more than two plural forms. Instead, use the i18n library's pluralization functions and let them handle the language-specific rules.

Learn ICU message format syntax for your i18n library. While the core syntax is standard, library-specific implementations may have variations. Understanding the syntax enables effective message authoring and debugging.

Test pluralization with various counts in each locale. Don't assume that testing with counts of 1 and 2 covers all cases—languages with more plural forms require testing with additional counts. Verify that all plural forms are defined and work correctly.

## Stack-Specific Callouts

### Vue 3 / vue-i18n

Use `$t()` in templates for translations: `<button>{{ $t('common.save') }}</button>`. The `$t` function is available globally and automatically updates when the locale changes. For dynamic keys or complex interpolation, use computed properties that call `$t()`.

In the Composition API, use `useI18n()` composable to access translation functions. This provides type safety and better integration with Vue's reactivity: `const { t, locale, availableLocales } = useI18n()`. Use `t()` for translations, `locale.value` for the current locale, and update `locale.value` to change languages.

Lazy load locales with `defineI18nLocale` and dynamic imports. Load only the active locale initially, then load additional locales on demand when users switch languages. This reduces initial bundle size significantly for applications with many languages.

Use vue-i18n-extract for finding missing translations and unused keys. This tool scans Vue components and extracts i18n usage, helping maintain translation completeness and identify unused translations for cleanup.

Configure vue-i18n with fallback locale and missing key handling. Define what happens when a translation is missing—display the key, fall back to default locale, or show an error. Configure this behavior consistently across the application.

### React / react-intl

Use `<FormattedMessage>` components for translations in JSX. The component handles interpolation, pluralization, and formatting automatically. For dynamic content, use the `id` prop with message keys and `values` prop for interpolation variables.

For imperative translations outside JSX, use the `useIntl()` hook which provides a `formatMessage` function. The hook integrates with React's context system, so locale changes propagate automatically to all components using it.

Use FormatJS CLI for message extraction. The CLI scans React components for `<FormattedMessage>` components and `formatMessage` calls, extracting message IDs and default text into JSON files for translation. This ensures no translatable strings are missed.

ICU message syntax is the standard for react-intl. Learn the syntax for pluralization, number formatting, date formatting, and conditional messages. The format is language-agnostic and handles complexity automatically.

Configure react-intl with proper locale data. Import locale data for all supported locales to ensure proper pluralization and formatting. Use `@formatjs/intl-locale` polyfill if needed for older browsers.

### Spring Boot

Use MessageSource with ResourceBundleMessageSource implementation. Configure it as a Spring bean with basename pointing to your message files (e.g., "messages" for `messages.properties`). Set fallback behavior for missing translations.

Use LocaleResolver for determining the user's locale. AcceptHeaderLocaleResolver reads the `Accept-Language` header automatically. CookieLocaleResolver stores locale preference in cookies. SessionLocaleResolver uses HTTP sessions. Choose based on your application's requirements.

For validation messages, use `@Validated` with localized messages. Spring's validation framework integrates with MessageSource, so validation error messages are automatically translated based on the resolved locale. Configure validators to use MessageSource for message lookup.

Return localized error messages in API responses. Use MessageSource to look up error messages based on the resolved locale. Include error codes alongside translated messages so frontends can handle errors programmatically.

For email and notification content, determine the recipient's locale and format content accordingly. Use MessageSource or a templating engine with i18n support (like Thymeleaf) for email templates. Format dates and numbers using Java's locale-aware formatters.

### Kotlin

Use string templates for message arguments in a type-safe way. Kotlin's string templates work well with MessageSource parameterized messages. Ensure proper escaping for special characters in message format strings.

Use Locale-aware formatting with `java.text` and `java.time` formatters. Kotlin's extension functions can make these APIs more ergonomic. Create extension functions for common formatting patterns to reduce boilerplate.

Leverage Kotlin's null safety for handling missing translations. When a translation key is missing, MessageSource may return null or the key itself. Handle these cases explicitly rather than allowing null to propagate unexpectedly.

Use data classes for structured message parameters. Instead of passing individual parameters to MessageSource, create data classes that represent message context. This improves type safety and makes message usage more maintainable.

Consider using sealed classes or enums for message keys to ensure type safety. While string-based keys are flexible, type-safe keys prevent typos and enable IDE autocomplete. However, this approach requires more setup and may be overkill for some applications.
