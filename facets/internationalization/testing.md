# Testing: Internationalization

## Visual Testing with Pseudo-localization

Pseudo-localization is a testing technique that replaces characters with accented equivalents or special characters to simulate translation without requiring actual translations. Common transformations include: a→â, e→ê, o→ô, i→î, u→û. This technique reveals hardcoded strings, truncation issues, and layout problems before translations are complete.

The value of pseudo-localization lies in its ability to catch i18n issues early in development. When developers see accented characters throughout the UI, they immediately notice strings that weren't extracted to message catalogs. Layout issues become apparent as pseudo-localized text may be longer or have different character widths than English.

Run pseudo-localization in development environments continuously. Configure the i18n system to use a pseudo-locale (e.g., "en-PSEUDO") that applies character transformations automatically. This ensures developers see i18n issues as they work, not just during dedicated i18n testing phases.

Pseudo-localization reveals several categories of issues. Hardcoded strings appear in their original form, making them easy to spot. Truncation issues become visible when transformed text exceeds container widths. Layout problems emerge when text expansion breaks grid layouts or causes overflow. Character encoding issues surface when special characters don't render correctly.

Advanced pseudo-localization can simulate text expansion by adding padding characters or repeating text. This helps test layouts with longer translations, which is critical because many languages produce longer text than English. German, for example, is approximately 30% longer than English on average.

Pseudo-localization is not a substitute for real translation testing, but it's an excellent early-warning system. It catches architectural issues before translation work begins, saving time and preventing rework. Combine pseudo-localization with real translation testing for comprehensive coverage.

## Translation Completeness Checks

Translation completeness validation ensures that all message keys in the default locale have corresponding translations in all supported locales. Missing translations create poor user experiences—users see message keys instead of translated text, or the application falls back to the default language unexpectedly.

Automate translation completeness checks in CI/CD pipelines. Before each release, validate that every key in the default locale exists in all other locales. Flag missing translations as build failures or warnings, depending on the severity policy. This prevents releases with incomplete translations.

Completeness checks should validate both presence and non-emptiness. A translation key that exists but has an empty value is effectively missing. Check that all translation values are non-empty strings (or appropriate non-string types for structured messages).

Handle intentional missing translations gracefully. Some messages may be intentionally omitted in certain locales due to cultural or legal reasons. Mark these as intentional omissions rather than errors. However, intentional omissions should be rare and well-documented.

Translation completeness tools vary by framework. vue-i18n-extract can find missing translations in Vue applications. FormatJS CLI validates message completeness for React applications. Custom scripts can compare message files across locales for any i18n system. Integrate these tools into the build process.

Track translation completeness metrics over time. Monitor the percentage of complete translations per locale, the number of missing translations, and trends in completeness. This helps prioritize translation work and identifies locales that need attention.

Completeness checks should also validate message structure. Ensure that interpolation placeholders match across locales—if the default locale uses `{name}`, all other locales should use the same placeholder name. Mismatched placeholders cause runtime errors when interpolation fails.

## Layout Testing

Translated text often differs significantly in length from the source language. German text is approximately 30% longer than English on average. Chinese and Japanese text can be shorter but may require different font sizes or line heights. Arabic text may be taller due to different character shapes. These length variations can break layouts that were designed for English text.

Test layouts with the longest translations for each supported language. Identify the languages that produce the longest text and use those for layout testing. This ensures that layouts accommodate text expansion without breaking. Don't assume English is the longest—many languages exceed English in length.

Layout testing should cover all UI components: buttons, form fields, navigation menus, tables, cards, modals, tooltips. Each component type has different constraints—buttons have fixed widths, tables have column constraints, modals have maximum widths. Test each component type with expanded text.

Use visual regression testing to compare layouts across locales. Capture screenshots of key pages in each locale and compare them to detect layout breaks. Automated visual testing tools can flag differences that indicate layout problems. However, some differences are expected—translated text will look different—so configure comparison thresholds appropriately.

Text truncation is a common layout issue. When text is too long for its container, it may be cut off with ellipsis or overflow the container boundaries. Test truncation behavior with long translations. Ensure that truncation is graceful and doesn't hide critical information. Consider using tooltips or expanding containers for long text.

Responsive layouts add complexity to layout testing. Text expansion affects layouts differently at different screen sizes. A layout that works on desktop may break on mobile when text is longer. Test layouts across breakpoints with expanded text to ensure responsive behavior remains correct.

Fixed-width containers are particularly problematic for i18n. Avoid fixed widths for text containers when possible. Use flexible layouts that adapt to content length. When fixed widths are necessary (e.g., table columns), ensure they accommodate the longest expected translations or implement horizontal scrolling.

## RTL Testing

Right-to-left language support requires comprehensive testing beyond simple translation. RTL layouts must mirror correctly, navigation must flow naturally, and interactive elements must function properly in RTL contexts. Testing with actual RTL content (Arabic, Hebrew) is essential—testing with `dir="rtl"` on English text doesn't reveal all issues.

Test RTL layouts with real RTL languages, not just direction attributes on English text. Arabic and Hebrew have different character shapes, text flow, and typography than English. These differences affect layout spacing, line breaks, and visual appearance. Pseudo-localization with RTL characters helps, but real languages are best.

Verify that layouts mirror correctly in RTL. Navigation menus should appear on the right side, not the left. Buttons and actions should flow right-to-left. Forms should align labels and inputs appropriately for RTL. Icons that imply direction (arrows, chevrons) should mirror.

Test interactive elements in RTL contexts. Dropdown menus, tooltips, popovers, and modals should position correctly relative to their triggers in RTL. Hover states, focus indicators, and selection highlights should work correctly. Scrollbars should appear on the left side in RTL layouts.

Bidirectional text testing verifies that mixed LTR and RTL content renders correctly. Some strings may contain both LTR and RTL text (e.g., an Arabic sentence with an English product name). The Unicode bidirectional algorithm handles most cases, but complex scenarios may require explicit directional markers. Test edge cases with mixed content.

RTL testing should cover all user flows, not just individual pages. Navigation between pages, form submissions, search functionality, and other workflows must work correctly in RTL. Test the complete user journey in RTL locales to ensure end-to-end functionality.

Accessibility in RTL contexts requires special attention. Screen readers must announce content in the correct order for RTL languages. Focus management should follow RTL reading order. Keyboard navigation should flow naturally in RTL direction. Test with screen readers and keyboard-only navigation in RTL locales.

## Date, Number, and Currency Formatting Tests

Date, number, and currency formatting varies significantly by locale. Testing ensures that formatting functions work correctly for all supported locales and handle edge cases appropriately. Formatting errors create confusion and undermine user trust.

Test date formatting for each supported locale. Verify that date order matches locale conventions (MM/DD/YYYY vs DD/MM/YYYY vs YYYY/MM/DD). Check separator characters (slashes, dashes, periods). Verify inclusion of day names, month names, and time formats (12-hour vs 24-hour). Test edge cases: leap years, month boundaries, timezone handling.

Number formatting tests verify decimal separators (periods vs commas), thousands separators, and digit grouping. Some locales use spaces instead of commas for thousands separators. Some locales don't use thousands separators at all for smaller numbers. Test with various number sizes: small decimals, large integers, negative numbers.

Currency formatting requires testing symbol placement (before vs after amount), decimal precision (some currencies don't use decimals), and currency code display. Test with various currency amounts and verify that formatting matches locale conventions. Some locales display currency codes, others use symbols only.

Edge cases in formatting testing include very large numbers, very small decimals, negative values, zero values, and null/undefined handling. Ensure that formatting functions handle these cases gracefully without errors or confusing output. Formatting should never crash or produce invalid output.

Test formatting consistency across the application. The same value should format identically wherever it appears. Inconsistent formatting confuses users and looks unprofessional. Use centralized formatting functions rather than ad-hoc formatting throughout the codebase.

Formatting tests should be automated unit tests, not just manual verification. Write tests that verify formatting output for each locale and edge case. These tests catch regressions when formatting logic changes and ensure consistency across refactorings.

## Pluralization Testing

Pluralization rules vary dramatically between languages, making comprehensive testing essential. English has two plural forms (singular and plural), but many languages have more complex rules. Russian has three forms based on the number's ending digit. Arabic has six plural forms. Polish has complex rules involving the last two digits.

Test all plural forms for each supported language. Don't assume that testing with counts of 1 and 2 covers all cases—languages with more plural forms require testing with additional counts. For Russian, test with counts ending in 1, 2-4, and 5-9 to verify all three forms work correctly.

Pluralization testing should verify that the correct form is selected for various counts. Test with counts of 0, 1, 2, and higher numbers to ensure all plural forms are triggered correctly. Test edge cases: very large numbers, negative numbers (if applicable), decimal numbers (if applicable).

ICU message format handles pluralization automatically, but testing verifies that messages are written correctly. Ensure that all plural forms are defined in message catalogs for each locale. Missing plural forms cause fallback behavior that may be grammatically incorrect.

Test pluralization in context, not just in isolation. A message like "You have {count} items" may work correctly in isolation, but when embedded in a longer sentence, the plural form must still be correct. Test pluralization within complex message structures.

Pluralization testing should cover all messages that use counts or quantities. This includes item counts, time periods, quantities, and other numeric values that affect grammar. Don't limit testing to obvious cases—review all messages for potential pluralization needs.

Automate pluralization testing where possible. Write tests that verify plural form selection for various counts in each locale. These tests catch errors in message definitions and ensure consistency across the application.

## Snapshot Testing

Snapshot testing compares UI screenshots across locales to catch visual regressions from translation changes. When translations are updated, visual differences may indicate layout breaks, truncation issues, or other problems that automated tests might miss.

Capture screenshots of key pages and components in each locale. Store these as baseline images for comparison. When translations are updated, capture new screenshots and compare them to baselines. Flag significant differences for manual review.

Snapshot testing requires careful configuration. Some differences are expected—translated text will look different, and that's correct. Configure comparison thresholds to ignore minor differences while catching significant layout breaks. Use perceptual diff algorithms that account for human visual perception.

Focus snapshot testing on critical user flows and high-traffic pages. Testing every page in every locale creates maintenance overhead. Prioritize pages where layout issues would have the most impact: checkout flows, forms, dashboards, navigation.

Snapshot testing complements other testing approaches. It catches visual issues that functional tests miss, but it doesn't verify that translations are correct or that functionality works. Combine snapshot testing with translation completeness checks, layout testing, and functional testing.

Maintain snapshot baselines carefully. When intentional design changes occur, update baselines accordingly. When layout improvements are made, update all locale baselines to reflect the changes. Outdated baselines create false positives that reduce the value of snapshot testing.

## End-to-End Testing

End-to-end testing verifies that the complete user journey works correctly in non-default locales. This includes locale persistence, language switching, and localized content throughout the application. E2E tests catch integration issues that unit tests and component tests miss.

Test locale persistence across sessions. When a user selects a language, that choice should persist when they return to the application. Verify that locale preferences are stored correctly (in cookies, localStorage, or user profiles) and restored on subsequent visits.

Test language switching functionality. Users should be able to change languages at any time, and the change should be immediate and complete. All text should update, not just some portions. Navigation should remain functional, and users shouldn't lose their place in the application.

Test localized content throughout user flows. Don't just test that translations exist—verify that they appear in the correct places at the correct times. Test that error messages are localized, that validation messages are translated, that notifications use the correct language.

Test locale-specific functionality. Some features may behave differently in different locales: date pickers should use locale-appropriate formats, number inputs should accept locale-appropriate separators, currency inputs should validate against locale conventions.

E2E tests should cover critical user journeys in each supported locale. Don't test every flow in every locale—that's impractical. Focus on high-value flows: user registration, checkout, account management, content creation. Test these flows in a representative sample of locales, prioritizing locales with the most users or highest business value.

Use E2E testing tools that support locale configuration. Playwright, Cypress, and Selenium can be configured to test in different locales. Set up test suites that run the same flows in different locales to ensure consistent functionality across languages.

Combine E2E testing with visual testing for comprehensive coverage. E2E tests verify functionality, while visual tests verify appearance. Together, they ensure that internationalized applications work correctly and look correct in all supported locales.
