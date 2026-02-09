# Gotchas: Internationalization

## Contents

- [Hardcoded Strings Discovered Late](#hardcoded-strings-discovered-late)
- [Concatenated Translations](#concatenated-translations)
- [Date Format Assumptions](#date-format-assumptions)
- [Text Truncation](#text-truncation)
- [Missing Plural Forms](#missing-plural-forms)
- [Locale Fallback Chain](#locale-fallback-chain)
- [Translation Context](#translation-context)
- [Dynamic Content Not Translated](#dynamic-content-not-translated)
- [RTL Afterthought](#rtl-afterthought)
- [Translation Files Becoming Stale](#translation-files-becoming-stale)

## Hardcoded Strings Discovered Late

The most common i18n gotcha is discovering hundreds of hardcoded strings scattered throughout the codebase when the first translation effort begins. Developers naturally write strings inline: `button.text = "Save"` or `<span>Welcome back</span>`. These work perfectly for single-language applications, but when translation becomes necessary, every hardcoded string must be found, extracted, and replaced—a time-consuming and error-prone process.

The problem compounds over time. Each new feature adds more hardcoded strings. Each refactoring becomes more complex when i18n concerns are added later. The technical debt accumulates, making eventual i18n implementation progressively more expensive. What could have been a small upfront investment becomes a major project requiring weeks or months of work.

Hardcoded strings hide in unexpected places. Error messages, validation messages, log messages that become user-visible, tooltips, placeholder text, button labels, page titles—the list is endless. Finding them all requires comprehensive code audits, which are time-consuming and may miss edge cases.

The solution is to enforce i18n from day one, even for single-language applications. Configure linting rules to flag hardcoded strings in user-facing contexts. Use static analysis tools that detect strings in JSX, template literals, and other user-visible locations. Make i18n usage a non-negotiable code standard enforced in code reviews.

Even when i18n seems unnecessary initially, the architectural discipline pays off. Message catalogs improve code organization. Key-based lookups make content updates easier. The separation of content from code improves maintainability. The incremental cost of i18n-ready architecture is minimal, while the cost of retrofitting is substantial.

## Concatenated Translations

Concatenating translated strings to build messages is a subtle but critical error. The pattern `"You have " + count + " new messages"` works perfectly in English but breaks in languages with different word order. German might require `"Sie haben " + count + " neue Nachrichten"`—completely different word order and adjective agreement. The concatenation approach cannot handle these differences.

Word order varies significantly between languages. What works in English may be grammatically incorrect or confusing in other languages. Adjectives may need to agree with nouns in gender and number. Articles may be required or forbidden. Simple concatenation cannot handle this complexity.

The fix is to use interpolation: `$t('message', { count })` with a message like "You have {count} new messages". Translators can reorder placeholders as needed for their language's grammar. The i18n library handles interpolation, ensuring grammatical correctness across languages.

Concatenation also breaks pluralization. Building messages like `count + " item" + (count !== 1 ? "s" : "")` fails in languages with complex plural rules. Russian has three plural forms based on the number's ending digit. Arabic has six plural forms. Simple conditional logic cannot handle this complexity.

Interpolation handles formatting automatically. Numbers, dates, and other values are formatted according to locale conventions during interpolation. Concatenation requires manual formatting, which is error-prone and may not respect locale conventions.

Avoid building messages conditionally through concatenation. Patterns like `prefix + (condition ? optionA : optionB) + suffix` break in languages where word order differs. Use conditional messages instead: define separate messages for each condition and select the appropriate one.

## Date Format Assumptions

Displaying dates as MM/DD/YYYY confuses users outside the United States, where DD/MM/YYYY is standard. Assuming any particular date format creates problems—different regions use different conventions for date order, separator characters, and inclusion of time components.

Hardcoded date formatting like `date.toLocaleDateString('en-US')` forces US format on all users, regardless of their locale preference. Users in other regions see dates in unfamiliar formats, leading to confusion and errors. A date like "03/04/2023" is ambiguous—is it March 4th or April 3rd?

The solution is to use locale-aware formatting: `Intl.DateTimeFormat(userLocale)` or equivalent APIs. These automatically format dates according to locale conventions, handling date order, separators, and time formats correctly. Always format dates based on the user's locale, not a hardcoded locale.

ISO 8601 format (YYYY-MM-DD) is unambiguous and works well for data exchange, but it's not user-friendly for display. Users expect dates in their local format. Format ISO dates for display using locale-aware formatting, but store and transmit dates in ISO format.

Time zone handling adds complexity. Displaying dates without timezone context can confuse users. A date like "2023-03-04" might represent different moments in time for users in different timezones. Include timezone information when displaying dates with time components, or use relative time ("2 hours ago") when appropriate.

Don't send pre-formatted date strings from the backend. Formatted strings cannot be reformatted for different locales. Always return ISO dates and let the frontend format them based on the user's locale.

## Text Truncation

English text fits perfectly in the UI, but German translation is 40% longer and gets cut off or causes layout overflow. This is a common problem when UI designs don't account for text expansion. Fixed-width containers, rigid layouts, and assumptions about text length all contribute to truncation issues.

The problem manifests in various ways: text cut off with ellipsis when it shouldn't be, text overflowing container boundaries, layouts breaking with longer translations, buttons too small for their labels, table columns too narrow for content. Each of these creates poor user experiences.

Testing with English text doesn't reveal truncation issues. German, Finnish, and other languages produce significantly longer text. Arabic text may be taller due to different character shapes. Chinese and Japanese may require different font sizes. UI designs must accommodate the longest expected translations.

The solution is to design UI for text expansion from the start. Use flexible layouts that adapt to content length. Avoid fixed-width containers for text content. When fixed widths are necessary, ensure they accommodate the longest expected translations or implement horizontal scrolling.

Test layouts with the longest translations for each supported language. Identify languages that produce the longest text and use those for layout testing. This ensures that layouts accommodate text expansion without breaking.

Consider text truncation strategies carefully. Truncation with ellipsis may be appropriate for some content, but ensure that truncated text doesn't hide critical information. Consider tooltips or expanding containers for long text. Test truncation behavior with the longest translations.

## Missing Plural Forms

English has two plural forms: "1 item" and "2 items." Using simple if/else logic like `count === 1 ? 'item' : 'items'` works for English but breaks in languages with more complex plural rules. Russian has three forms: "1 товар," "2 товара," "3 товара," "4 товара," and "5 товаров" with rules based on the number's ending digit.

Arabic has six plural forms. Polish has complex rules involving the last two digits. Simple conditional logic cannot handle this complexity. Using English-style pluralization for all languages produces grammatically incorrect messages that undermine user trust.

The solution is to use ICU message format for pluralization: `{count, plural, one {# item} other {# items}}`. The i18n library evaluates the count against the language's plural rules and selects the appropriate form. This approach works across all languages without language-specific code.

Pluralization must be handled in the message itself, not in application logic. Don't write code that selects singular or plural forms—let the i18n library handle it based on the language's rules. Define all plural forms in message catalogs for each locale.

Test pluralization with various counts in each locale. Don't assume that testing with counts of 1 and 2 covers all cases—languages with more plural forms require testing with additional counts. Verify that all plural forms are defined and work correctly.

Missing plural forms cause fallback behavior that may be grammatically incorrect. Ensure that all required plural forms are defined in message catalogs for each locale. Use extraction and validation tools to identify missing plural forms before release.

## Locale Fallback Chain

A user requests fr-CA (French Canadian). The application has fr (French) but not fr-CA. Does the app fall back to fr, or to the default en? The fallback behavior must be defined and tested explicitly, or users may see unexpected language mixes or fall back to a language they don't understand.

Locale fallback chains determine what happens when an exact locale match isn't available. Common strategies include: fall back to language (fr-CA → fr), fall back to regional variant (fr-CA → fr-FR if available), fall back to default locale (fr-CA → en). Each strategy has trade-offs.

Fallback to language (fr-CA → fr) is usually preferred because it maintains the same language even if regional variants differ. Users who understand French Canadian will understand French, even if some terminology differs. However, regional differences can be significant—currency, date formats, and terminology may differ.

Fallback to default locale (fr-CA → en) is safer but less user-friendly. Users who don't understand the default language see content they can't read. This should be a last resort, used only when no language match is available.

The fallback chain should be: exact locale match → language match → default locale. Configure this behavior explicitly in the i18n system and test it thoroughly. Document the fallback behavior so developers and translators understand what happens when translations are missing.

Test fallback behavior with various locale combinations. Verify that fallbacks work correctly and that users don't see unexpected language mixes. Ensure that fallback behavior is consistent across the application.

Missing translations within a locale also require fallback behavior. If a specific key is missing in fr-CA but exists in fr, should it fall back to fr or to the default locale? Define this behavior explicitly and test it.

## Translation Context

The English word "Save" can mean "save to disk" or "save money." Translators need context to translate correctly. Without context, translators may choose the wrong translation, leading to confusing or incorrect user interfaces. This is especially problematic for short, ambiguous words that have multiple meanings.

Keys like `save`, `cancel`, `delete` provide no context about usage. Is "save" a verb (save the file) or a noun (a discount)? Is "cancel" canceling an operation or canceling a subscription? Translators need context to produce accurate translations.

The solution is to provide descriptive keys and context. Use keys like `billing.invoice.actions.save` or `file.actions.save` that indicate usage context. Include comments or descriptions in message files that explain the intended meaning. Some translation management systems allow attaching context screenshots or usage descriptions to keys.

Avoid overly generic keys that could apply to multiple contexts. Keys like `message`, `text`, `label` provide no context. Use specific keys that indicate the feature and usage context.

Translation management systems can help by allowing context to be attached to keys. Screenshots showing where the text appears, descriptions of usage, and examples all help translators understand context and produce accurate translations.

Review translations for context accuracy. Native speakers or subject matter experts should review translations to ensure they match the intended meaning and usage context. Automated checks can catch some issues, but human review is essential for context accuracy.

## Dynamic Content Not Translated

Static UI strings are translated, but error messages from the API, email templates, and notification content return in English. This creates inconsistent user experiences—users see the UI in their language but error messages and emails in English. This inconsistency confuses users and undermines the i18n effort.

API error messages must be localized. The backend should return error messages in the user's locale, determined from the Accept-Language header, user profile, or other locale resolution mechanism. Use MessageSource or equivalent to look up localized error messages based on the resolved locale.

Email and notification content must be localized because they're sent outside the web application context. The frontend cannot format them, so the backend must determine the recipient's locale and format content accordingly. Use templating engines with i18n support or MessageSource for email content.

Validation messages must be localized. Spring's validation framework integrates with MessageSource, so validation error messages can be translated automatically. Configure validators to use MessageSource for message lookup, ensuring users see validation errors in their language.

Dynamic content from external sources (APIs, third-party services) may not be translatable. In these cases, provide fallback behavior or work with providers to ensure localized content. Document which content is translatable and which is not.

Ensure that all user-facing content goes through i18n, not just static UI strings. Audit error messages, email templates, notification content, and other dynamic content to ensure they're localized. Use extraction tools to find all user-facing strings, not just those in UI components.

## RTL Afterthought

Adding RTL support late requires rewriting CSS from physical (left/right) to logical (start/end) properties throughout the entire codebase. This is a massive undertaking that touches every stylesheet and component. The cost of retrofitting RTL support can be prohibitive, often requiring weeks or months of work.

Physical properties like `margin-left`, `padding-right`, `float: left` don't adapt to text direction. They work for LTR but break RTL layouts. Converting them to logical properties (`margin-inline-start`, `padding-inline-end`) requires finding and replacing every instance throughout the codebase.

The solution is to use logical properties from the start, even for LTR-only applications. Logical properties automatically adapt to text direction, so adding RTL support later is trivial. The incremental cost of using logical properties is minimal, while the cost of retrofitting is substantial.

CSS frameworks may not support RTL well, or may require special configuration. Test RTL support early if RTL languages are planned. Consider frameworks with built-in RTL support or plan for RTL from the beginning.

RTL testing requires actual RTL content, not just `dir="rtl"` on English text. English text in RTL mode doesn't reveal layout issues the same way Arabic or Hebrew text does. Use real translations or pseudo-localization that includes RTL characters to properly test RTL support.

Icon and image mirroring may be needed for RTL. Icons that imply direction (arrows, chevrons) should mirror in RTL. Plan for this from the start rather than retrofitting later.

## Translation Files Becoming Stale

Translations added for features that were later removed accumulate as unused keys. Over time, translation files become bloated with unused translations, making them harder to maintain and increasing the cost of translation updates. Unused keys also confuse translators who don't know whether they're still needed.

The problem occurs when features are removed but their translations remain. Developers remove code but forget to remove translation keys. Over time, hundreds of unused keys accumulate, creating maintenance overhead and increasing translation costs.

The solution is to periodically clean up unused keys. Use extraction tools that identify translation keys that are no longer referenced in code. Remove unused keys from all locale files to keep translation files clean and maintainable.

Automate unused key detection in CI/CD pipelines. Flag unused keys as warnings or errors, depending on policy. This prevents accumulation of unused translations and keeps translation files maintainable.

Coordinate cleanup with translation efforts. Removing unused keys requires updating all locale files, which should be done as part of regular translation maintenance. Don't remove keys unilaterally—coordinate with translators to ensure keys aren't needed for future features.

Document the cleanup process so developers understand how to identify and remove unused keys. Make it part of the regular maintenance workflow rather than a one-time effort.

Some keys may be intentionally kept for future use or backward compatibility. Document these cases so they're not accidentally removed. However, be conservative—unused keys that aren't documented as intentionally kept should be removed.
