# Architecture: Internationalization

## i18n vs L10n

Internationalization (i18n) and localization (l10n) are distinct but related concepts. Internationalization is the technical work of making code and architecture support multiple languages and locales. It is done by developers as a one-time investment in the codebase structure. Localization is the process of adapting content for specific languages and locales. It is done by translators and is an ongoing effort that must be repeated for each new locale.

The relationship between i18n and l10n is that of foundation and content. i18n provides the infrastructure—message catalogs, locale resolution, formatting functions, pluralization support. l10n provides the actual translations and cultural adaptations that populate that infrastructure. You cannot localize without internationalization, but internationalization without localization simply means the infrastructure exists but only default-language content is available.

The separation of concerns is important. Developers focus on i18n architecture: ensuring all user-facing strings go through the i18n system, implementing locale resolution, setting up formatting functions, handling RTL support. Translators focus on l10n: creating accurate translations, adapting content for cultural context, ensuring consistency across the application. This division of labor allows each group to work efficiently within their expertise.

The cost structure differs significantly. i18n is a fixed cost—once the architecture is in place, it supports unlimited languages. l10n is a variable cost that scales with the number of languages and the frequency of content updates. Understanding this distinction helps with planning and budgeting. The i18n investment pays off as more languages are added, while l10n costs accumulate with each new locale.

## Frontend i18n Architecture

### Message Catalogs

Message catalogs are the foundation of frontend i18n. They store translations as key-value pairs, typically in JSON files organized by locale. Each locale has its own file: `en.json` for English, `de.json` for German, `fr.json` for French. The structure mirrors the application's feature organization, with namespaced keys like `common.save`, `billing.invoice.title`, `users.profile.editButton`.

Key-based message lookup provides several advantages. Keys are stable identifiers that don't change when translations are updated. They serve as documentation, making it clear what content belongs to which feature. They enable fallback behavior—if a translation is missing, the key can be displayed or a default locale used. Keys also facilitate tooling for finding unused translations and identifying missing translations.

The message catalog structure should mirror the application's feature structure. If the codebase is organized by feature modules, the translation keys should follow the same organization. This makes it easy for developers to find relevant translations and for translators to understand context. Flat key structures with hundreds of keys become unmaintainable; hierarchical structures scale better.

Interpolation allows dynamic content within translated messages. Instead of concatenating strings like "Hello, " + name, use interpolation: "Hello, {name}". The i18n library replaces placeholders with actual values, and translators can reorder the sentence structure as needed for their language. This is critical because word order varies significantly between languages—what works in English may be grammatically incorrect in other languages.

### Vue 3 with vue-i18n

Vue 3 applications use vue-i18n for internationalization. The library integrates deeply with Vue's reactivity system and template compilation. In templates, use `$t('key')` to translate strings: `<button>{{ $t('common.save') }}</button>`. The `$t` function is available globally in all templates and automatically updates when the locale changes.

In the Composition API, use the `useI18n()` composable to access translation functions. This provides type safety and better integration with Vue's reactivity. The composable returns `t` for translations, `locale` for the current locale, and `availableLocales` for supported languages. Use it in setup functions: `const { t, locale } = useI18n()`.

Lazy loading locale files reduces initial bundle size. Instead of importing all translation files at startup, load only the active locale initially. When users switch languages, load the new locale file dynamically. vue-i18n supports this through `defineI18nLocale` and dynamic imports. The performance benefit is significant for applications with many languages or large translation files.

Locale switching without page reload is a key UX feature. vue-i18n updates translations reactively, so changing the locale immediately updates all displayed text without requiring a full page refresh. Store the user's locale preference in localStorage or a user profile, and restore it on subsequent visits. The locale change should be instant and seamless.

vue-i18n supports ICU message format for complex pluralization and formatting. Use it for messages with conditional logic based on counts or other variables. The library handles the complexity of plural rules across languages, so developers don't need to implement language-specific logic.

### React with react-intl or i18next

React applications have two primary i18n options: react-intl (part of FormatJS) and i18next. react-intl is specifically designed for React and provides excellent TypeScript support. i18next is framework-agnostic and has a larger ecosystem with plugins for various frameworks.

react-intl uses `<FormattedMessage>` components for translations in JSX. The component handles interpolation, pluralization, and formatting automatically. For imperative translations outside JSX, use the `useIntl()` hook which provides a `formatMessage` function. The hook integrates with React's context system, so locale changes propagate automatically to all components.

Message extraction is critical for React applications. The FormatJS CLI scans code for `<FormattedMessage>` components and `formatMessage` calls, extracting message IDs and default text into JSON files for translation. This ensures no translatable strings are missed and provides a single source of truth for what needs translation.

ICU message format is the standard for react-intl. It provides a rich syntax for pluralization, number formatting, date formatting, and conditional messages. The format is language-agnostic and handles the complexity of different languages' rules automatically. Learning ICU syntax is essential for effective React i18n.

i18next provides similar functionality with a different API. It uses `t()` function calls throughout the codebase and supports namespaces for organizing translations. The library has extensive plugin support for features like language detection, caching, and backend loading. i18next is a good choice for applications that may need to share i18n logic across React and other frameworks.

### Interpolation and Pluralization

Interpolation allows dynamic values within translated messages. The syntax varies by library but generally follows patterns like `{name}` or `{{name}}`. Translators can reorder placeholders as needed for their language's grammar. Never concatenate translated strings—word order differences will break the translation.

Pluralization is one of the most complex aspects of i18n. Different languages have different plural rules. English has two forms: singular and plural. Russian has three forms based on the number's ending digit. Arabic has six plural forms. Polish has complex rules involving the number's last two digits. Simple if/else logic cannot handle this complexity.

ICU message format solves pluralization with a standard syntax: `{count, plural, one {# item} other {# items}}`. The i18n library evaluates the count against the language's plural rules and selects the appropriate form. The `#` symbol represents the formatted number. This approach works across all languages without language-specific code.

Pluralization must be handled in the message itself, not in application logic. Don't write code like "if count === 1 then singular else plural"—this breaks in languages with more than two plural forms. Instead, use the i18n library's pluralization functions and let them handle the language-specific rules.

### Date, Number, and Currency Formatting

Format dates, numbers, and currencies on the frontend using the browser's Intl APIs. `Intl.DateTimeFormat` formats dates according to locale conventions. `Intl.NumberFormat` handles number and currency formatting. `Intl.DisplayNames` provides localized names for languages, regions, and other entities.

The backend should return data in locale-neutral formats: ISO 8601 dates, unformatted numbers, currency amounts with currency codes. The frontend formats these values for display based on the user's locale. This separation ensures consistency and allows the same API to serve users in different locales.

Don't send pre-formatted strings from the backend. Formatted strings cannot be reformatted for different locales, cannot be sorted or filtered correctly, and break the separation of concerns between data and presentation. Always format on the frontend where the user's locale is known.

Currency formatting requires the currency code, not just the symbol. The same symbol may represent different currencies (dollar sign for USD, CAD, AUD, etc.), and the positioning varies by locale. Use `Intl.NumberFormat` with the currency option and the appropriate currency code.

Date formatting must respect locale conventions for date order, separator characters, and whether to include time. Some locales use 24-hour time, others use 12-hour with AM/PM. Some locales include the day of the week, others don't. The Intl API handles all these variations automatically.

### Lazy Loading Locales

Loading all locale files at application startup increases bundle size unnecessarily. Most users only need one language, so loading translations for ten languages wastes bandwidth and slows initial load. Lazy loading loads only the active locale initially, then loads additional locales on demand when users switch languages.

Implement lazy loading using dynamic imports. When the application starts, import only the default locale. When a user switches languages, dynamically import the new locale file and update the i18n instance. Most i18n libraries support this pattern through configuration options or explicit loading functions.

Lazy loading requires handling loading states. While a new locale file loads, the application should show a loading indicator or continue displaying the previous locale until the new one is ready. The transition should be smooth and not disrupt the user experience.

Code splitting works well with lazy loading. Each locale file can be its own chunk, loaded only when needed. This reduces the initial bundle size and improves performance, especially for applications with many languages or large translation files.

## Backend i18n Architecture

### Spring MessageSource

Spring Boot applications use MessageSource for internationalization. MessageSource is an interface that provides message lookup based on locale. The most common implementation is ResourceBundleMessageSource, which loads messages from property files in the classpath.

Message files follow naming conventions: `messages.properties` for the default locale, `messages_de.properties` for German, `messages_fr.properties` for French. The files contain key-value pairs matching the frontend message catalogs. Spring loads the appropriate file based on the resolved locale.

Configure MessageSource as a Spring bean with basename and other properties. Set the basename to the base name of your message files (e.g., "messages" for files like `messages.properties`). Configure fallback behavior—whether to use the default locale if a translation is missing, or to display the message key.

MessageSource supports parameterized messages using Java's MessageFormat syntax. Use placeholders like `{0}` for the first parameter, `{1}` for the second, etc. This enables interpolation similar to frontend i18n libraries. MessageSource handles pluralization less elegantly than frontend libraries—often requiring separate message keys for singular and plural forms.

### Locale Resolution

Locale resolution determines which locale to use for a given request. Spring provides several LocaleResolver implementations, each using a different strategy. The choice of resolver depends on the application's requirements and user experience design.

AcceptHeaderLocaleResolver reads the `Accept-Language` HTTP header sent by the browser. This is the most automatic approach—users don't need to explicitly select a language, the application uses their browser's language preference. However, browser language settings may not reflect user preferences accurately, especially on shared devices.

CookieLocaleResolver stores the locale preference in a cookie. This allows users to explicitly select a language, and that choice persists across sessions. The cookie-based approach works well for applications where users can set preferences, but requires cookie support and may not work in all environments.

SessionLocaleResolver stores the locale in the HTTP session. This is similar to cookie-based resolution but uses server-side session storage instead of cookies. It works well for applications with user sessions but doesn't persist across sessions unless combined with user profile storage.

FixedLocaleResolver always uses a fixed locale, ignoring user preferences. This is useful for testing or applications that only support one language. It's not suitable for internationalized applications.

Custom locale resolvers can implement application-specific logic. For example, resolve locale based on user profile preferences stored in a database, or based on URL path patterns like `/en/products` or `/de/products`. Custom resolvers provide maximum flexibility but require more implementation effort.

The precedence order for locale resolution should be: explicit user selection (highest priority), user profile preference, URL path or subdomain, Accept-Language header, default locale (lowest priority). This ensures user choices are respected while providing sensible defaults.

### API Responses

API responses should be localized for user-facing content but locale-neutral for data. Error messages, validation messages, and user guidance should be translated. Dates, numbers, and other data should be returned in neutral formats for frontend formatting.

Return error messages in the user's locale. Use MessageSource to look up error messages based on the resolved locale. Include error codes or keys alongside translated messages so frontends can handle errors programmatically. This dual approach—human-readable translated messages and machine-readable error codes—provides the best of both worlds.

Validation messages must be localized. Spring's validation framework integrates with MessageSource, so validation error messages can be translated automatically. Configure validators to use MessageSource for message lookup, ensuring users see validation errors in their language.

Data should be returned in locale-neutral formats. Return dates as ISO 8601 strings, numbers as unformatted values, currencies as amounts with currency codes. The frontend formats these values for display based on the user's locale. This separation allows the same API to serve users in different locales without duplicating data formatting logic.

Exception: email and notification content should be localized on the backend. These are sent outside the web application context, so the frontend cannot format them. The backend must determine the recipient's locale (from user profile, email preferences, or Accept-Language header) and format content accordingly. Use MessageSource or a templating engine with i18n support for email content.

### Database Storage

Storing translatable content in databases requires careful schema design. Two primary approaches exist: separate translations table or JSONB columns for multilingual fields. Each has trade-offs in query complexity, performance, and flexibility.

The translations table approach uses a separate table with columns for entity ID, locale, field name, and translated value. This normalizes translations and makes it easy to add new languages without schema changes. However, queries become more complex, requiring joins to retrieve translated content, and performance can suffer with many translations.

JSONB columns store translations as JSON objects with locale keys. This denormalizes translations but simplifies queries—no joins required. JSONB provides good query performance and flexibility for adding languages. However, it's less normalized and may be harder to query across all locales for a specific field.

Choose the approach based on query patterns. If you frequently query translated content for a single locale, JSONB may be simpler. If you need to query or update translations across all locales, a translations table may be better. Many applications use a hybrid approach: JSONB for simple fields, translations table for complex multilingual content.

Consider full-text search requirements. If users need to search content in multiple languages, the storage approach affects search implementation. JSONB allows indexing translations, while translations tables may require separate search indexes per locale.

## Translation Workflow

The translation workflow spans from development through release. It involves extracting translatable strings, sending them to translators, reviewing translations, integrating them back into the codebase, and validating completeness.

Extraction is the process of identifying all translatable strings in code and generating message catalogs. Use tooling specific to your framework: vue-i18n-extract for Vue, FormatJS CLI for React, message extraction plugins for Spring. These tools scan code for i18n function calls and generate or update message files with keys and default text.

Translation can happen through various channels. Professional translation services provide high quality but at high cost. Translation Management Systems (TMS) like Crowdin, Phrase, or Lokalise provide platforms for managing translations with translator interfaces, context screenshots, and workflow management. Manual file editing works for small projects or community translation efforts.

Review ensures translation quality. Native speakers or subject matter experts review translations for accuracy, consistency, and cultural appropriateness. Review catches errors, ensures terminology consistency, and verifies that translations match the application's tone and style. Automated checks can catch some issues, but human review is essential for quality.

Integration merges translated files back into the codebase. This may happen through git commits, CI/CD pipelines, or TMS integrations that automatically sync translations. Validate that all keys have translations before merging—missing translations should block releases or trigger fallback to default locale.

Release deploys updated translations with application code. Consider translation versioning—if translations change independently of code, version them separately. Some applications support A/B testing of translations to measure impact on user engagement.

## RTL Support

Right-to-left (RTL) languages like Arabic and Hebrew require special layout handling. Simply translating content into RTL languages without proper support creates a confusing, broken experience. RTL support must be built into the architecture from the start.

CSS logical properties are the foundation of RTL support. Use `margin-inline-start` instead of `margin-left`, `padding-inline-end` instead of `padding-right`. These properties automatically adapt to text direction—they become left margins/padding for LTR and right margins/padding for RTL. Physical properties like `left` and `right` don't adapt and break RTL layouts.

Set the `dir` attribute on the HTML element based on the current locale. For RTL languages, set `dir="rtl"`. For LTR languages, set `dir="ltr"` or omit it (LTR is the default). The direction attribute affects text flow, layout, and interactive elements automatically when combined with logical properties.

CSS frameworks like Tailwind CSS support RTL variants. Use classes like `rtl:ml-4` for RTL-specific styles. However, prefer logical properties over RTL variants—logical properties work for both directions without duplication.

Bidirectional text occurs when LTR and RTL content mix in the same string. The Unicode bidirectional algorithm handles most cases automatically, but complex scenarios may require explicit directional markers. Use Unicode directional marks sparingly—they're usually unnecessary if the overall text direction is set correctly.

Test RTL support with actual RTL content, not just `dir="rtl"` on English text. English text in RTL mode doesn't reveal layout issues the same way Arabic or Hebrew text does. Use real translations or pseudo-localization that includes RTL characters to properly test RTL support.

Icon and image mirroring may be needed for RTL. Icons that imply direction (arrows, chevrons) should mirror in RTL. Decorative images usually don't need mirroring, but images with text or directional content may. Use CSS transforms or separate RTL image assets as needed.
