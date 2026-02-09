# Accessibility: Testing

## Automated Testing with axe-core

Automated accessibility testing catches approximately 30-40% of accessibility issues and provides fast feedback during development. axe-core is the industry-standard automated accessibility testing engine, powering tools like axe DevTools, Lighthouse, and various testing frameworks.

Integrate axe-core into component tests using vitest-axe for Vue/React component testing or jest-axe for Jest-based test suites. These libraries provide simple APIs to run accessibility checks on rendered components. Run axe checks on every component render to catch issues immediately during development.

For end-to-end testing, use @axe-core/playwright to integrate axe-core into Playwright tests. This enables accessibility testing of full user flows, including dynamic content and JavaScript interactions. Run axe checks on critical pages and user journeys to ensure accessibility throughout the application.

axe-core checks for common issues like missing alt text, insufficient color contrast, missing form labels, invalid ARIA usage, keyboard navigation problems, and heading hierarchy issues. It cannot catch all accessibility problems—issues requiring human judgment like meaningful alt text, logical reading order, and comprehensible link text require manual testing.

Automated tests should fail the build when accessibility violations are detected. Set up CI/CD pipelines to run accessibility tests on every commit and pull request. This prevents accessibility regressions from being merged into the codebase.

Configure axe-core with appropriate rulesets. The WCAG 2.1 AA ruleset is appropriate for most applications. More strict rulesets (WCAG 2.1 AAA) may be too restrictive for some designs. Less strict rulesets (WCAG 2.0 A) may miss important issues. Choose the ruleset that matches your compliance target.

## Linting for Accessibility

Linting provides the fastest feedback loop for accessibility issues, catching problems at development time before code is committed. ESLint plugins for accessibility integrate into the development workflow and provide immediate feedback in the editor.

For React applications, eslint-plugin-jsx-a11y catches common accessibility issues in JSX. It flags missing alt text on images, invalid ARIA attributes, non-interactive elements with event handlers, missing form labels, and other common mistakes. Configure it to error on accessibility violations, not just warn, to enforce accessibility standards.

For Vue applications, eslint-plugin-vuejs-accessibility provides similar functionality for Vue templates. It checks for accessibility issues specific to Vue's template syntax and component patterns. Like the React plugin, configure it to error on violations.

Linting cannot catch all accessibility issues—it focuses on static analysis of code patterns. It cannot verify that ARIA attributes are updated dynamically, that keyboard navigation works correctly, or that color contrast meets requirements. Linting complements but does not replace other testing methods.

Integrate accessibility linting into pre-commit hooks to prevent accessibility violations from being committed. This provides immediate feedback to developers and maintains code quality standards.

## Keyboard Testing

Keyboard testing is manual but essential—it validates that all functionality is accessible without a mouse. Test every interactive flow using only keyboard input: Tab to navigate, Enter and Space to activate, Arrow keys for custom components, Escape to close dialogs.

Verify that all interactive elements are reachable via Tab key. The focus order should follow the visual layout and reading order. Focus should not jump unexpectedly or skip elements. Custom components should have logical keyboard interaction patterns.

Check that focus indicators are visible on all interactive elements. Keyboard users need to see where focus is to navigate effectively. Focus indicators should be clearly visible with sufficient contrast. Test that custom focus styles work correctly and aren't removed or hidden.

Verify that custom keyboard shortcuts work as expected. Arrow keys should navigate within components like menus and tabs. Enter and Space should activate buttons and select items. Escape should close dialogs and cancel operations. Tab should move focus into and out of component groups.

Test focus trapping in modals and dialogs. Focus should be trapped within the dialog when it's open. Tab at the last element should move to the first element, not to background content. When the dialog closes, focus should return to the trigger element.

Keyboard testing should be part of the QA process for every feature. Create keyboard testing checklists for common patterns (forms, navigation, modals, dropdowns) to ensure consistent testing coverage.

## Screen Reader Testing

Screen reader testing validates that content is announced correctly and that semantic HTML and ARIA are properly implemented. Test with at least one screen reader—VoiceOver on macOS/iOS is free and widely used, NVDA on Windows is free and open source, JAWS on Windows is commercial but widely used in enterprise.

Test that content is announced in a logical order that matches the visual layout. Screen readers read content linearly, so the DOM order matters. Use CSS for visual layout, not DOM order manipulation.

Verify that labels are descriptive and provide sufficient context. Screen reader users rely on labels to understand form fields, buttons, and links. "Click here" links are meaningless—use descriptive link text. Icon-only buttons need aria-label to describe their purpose.

Check that dynamic content updates are communicated. When content loads asynchronously, when errors appear, or when notifications show, screen readers should announce these changes. Use aria-live regions for dynamic content announcements.

Verify that heading hierarchy creates a meaningful document outline. Screen reader users navigate by headings to understand page structure and jump to sections. Test that headings are in order and that the headings list makes sense.

Test that form validation is announced correctly. Error messages should be associated with form fields using aria-describedby. Errors should be announced via aria-live when they appear. Required fields should be clearly indicated.

Screen reader testing requires training and practice. Developers should learn basic screen reader navigation (heading navigation, landmark navigation, form navigation) to effectively test accessibility. Consider accessibility training sessions to build team capability.

## Lighthouse Accessibility Audit

Lighthouse provides automated accessibility scoring that can be integrated into CI/CD pipelines. Lighthouse accessibility scores range from 0-100, with 100 representing full automated compliance. Scores should be maintained above 90, with 100 as the target.

Lighthouse checks for common issues like missing alt text, insufficient color contrast, missing form labels, invalid ARIA, and other automated checks. It uses axe-core under the hood, so it catches similar issues to direct axe-core integration.

Lighthouse CI can be configured to fail builds when accessibility scores drop below a threshold. This provides automated regression detection for accessibility. However, Lighthouse scores are not comprehensive—they only check automated issues and cannot verify keyboard navigation, screen reader experience, or issues requiring human judgment.

Use Lighthouse as a quick health check and regression detector, not as the sole accessibility testing method. Combine Lighthouse with component-level axe-core testing, linting, and manual testing for comprehensive coverage.

## Manual Accessibility Audits

Manual accessibility audits are essential because automated tools cannot catch all accessibility issues. Issues requiring human judgment include meaningful alt text, logical reading order, comprehensible link text, clear error messages, and overall user experience.

Conduct periodic manual audits against the WCAG 2.1 AA checklist. Review each success criterion and verify compliance through manual testing. This should be done quarterly or for major feature releases. Manual audits catch issues that automated tools miss and validate that accessibility is maintained over time.

Manual audits should test with multiple assistive technologies: screen readers (VoiceOver, NVDA, JAWS), keyboard navigation, screen magnification, and voice control. Different assistive technologies may reveal different issues, so testing with multiple tools provides comprehensive coverage.

Document audit findings and track remediation. Use issue tracking systems to manage accessibility bugs with the same priority as functional bugs. Accessibility issues should not be deprioritized or deferred.

Consider engaging external accessibility consultants for expert audits. External auditors bring specialized expertise and can identify issues that internal teams may miss. Expert audits are particularly valuable before major releases or when preparing for compliance certifications.

## User Testing with Assistive Technology Users

User testing with people who actually use assistive technologies provides the most valuable feedback and reveals issues that developers and automated tools miss. Real users understand how assistive technologies work and can identify usability issues that technical testing cannot detect.

Recruit users with disabilities who represent your target audience. Include users who rely on screen readers, keyboard navigation, voice control, and other assistive technologies. These users can test actual workflows and provide feedback on usability, not just technical compliance.

User testing sessions should cover critical user journeys: account creation, login, primary workflows, form submission, and error handling. Observe how users navigate the interface and where they encounter barriers. Ask users to think aloud as they interact with the application.

User testing reveals issues like confusing navigation patterns, unclear error messages, workflows that are technically accessible but difficult to use, and missing features that assistive technology users need. These insights inform design and development decisions beyond basic compliance.

Schedule user testing sessions quarterly or for major feature releases. Build relationships with accessibility user groups or consultants who can provide ongoing testing. Consider compensating users for their time and expertise.

User testing should inform design decisions from the start, not just validate completed work. Include users with disabilities in design research and usability testing throughout the product development lifecycle.

## CI/CD Integration

Integrate accessibility testing into continuous integration and deployment pipelines to prevent regressions automatically. Automated accessibility tests should run on every commit and pull request, failing builds when violations are detected.

Component-level axe-core tests should run as part of the test suite. Configure vitest-axe or jest-axe to fail tests when accessibility violations are found. This provides immediate feedback to developers and prevents accessibility bugs from being merged.

End-to-end Playwright tests with @axe-core/playwright should run on critical pages and user flows. These tests validate accessibility in the full application context, including dynamic content and JavaScript interactions.

Lighthouse CI can be configured to run accessibility audits and fail builds when scores drop below thresholds. This provides automated regression detection at the page level.

Linting should run in CI to catch accessibility code patterns. Configure ESLint to error on accessibility violations, not just warn. This enforces accessibility standards at the code level.

Accessibility testing in CI should be fast enough to provide quick feedback but comprehensive enough to catch regressions. Balance test coverage with execution time. Run quick checks (linting, component tests) on every commit, and run comprehensive checks (E2E tests, Lighthouse) on pull requests.

Document accessibility testing requirements in CI/CD configuration and make them visible to the team. Ensure that accessibility test failures block merges, just like functional test failures.

## Color Contrast Testing

Color contrast must be validated for all text-background combinations to ensure readability for users with low vision. Automated tools can check contrast, but manual verification is important for complex designs and custom color combinations.

Use contrast checker tools like WebAIM Contrast Checker or Colour Contrast Analyser to validate contrast ratios. WCAG AA requires 4.5:1 for normal text and 3:1 for large text. Test all text colors against their background colors, including hover states, focus states, disabled states, and error states.

Validate contrast in both light and dark themes if the application supports theme switching. Colors that meet contrast requirements in one theme may not meet them in another theme. Test all theme variations.

Design system color palettes should be validated for contrast compliance. Document which color combinations are accessible and provide guidance to designers and developers. Tailwind CSS utility classes should be checked to ensure accessible combinations.

Automated contrast checking can be integrated into component tests using tools that analyze rendered components. However, automated tools may not catch all contrast issues, especially with gradients, images, or complex backgrounds. Manual verification is still important.

Contrast testing should be part of the design review process. Designers should validate contrast before designs are implemented, and developers should verify contrast during implementation. This prevents contrast issues from being introduced in the first place.
