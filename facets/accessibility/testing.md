# Accessibility: Testing

## Contents

- [Automated Testing with axe-core](#automated-testing-with-axe-core)
- [Linting for Accessibility](#linting-for-accessibility)
- [Keyboard Testing](#keyboard-testing)
- [Screen Reader Testing](#screen-reader-testing)
- [Lighthouse Accessibility Audit](#lighthouse-accessibility-audit)
- [Manual Accessibility Audits](#manual-accessibility-audits)
- [User Testing with Assistive Technology Users](#user-testing-with-assistive-technology-users)
- [CI/CD Integration](#cicd-integration)
- [Color Contrast Testing](#color-contrast-testing)

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

### VoiceOver (macOS/iOS) Testing

**Getting Started**: Enable VoiceOver with `Cmd + F5` or System Preferences → Accessibility → VoiceOver. Learn basic navigation:
- `VO + Right Arrow`: Move to next element
- `VO + Left Arrow`: Move to previous element
- `VO + U`: Open rotor (quick navigation menu)
- `VO + H`: Navigate by headings
- `VO + L`: Navigate by links
- `VO + R`: Navigate by regions/landmarks
- `VO + Space`: Activate focused element
- `VO + Control + H`: Read from current position to end
- `VO + Shift + Down Arrow`: Enter a group (like a form or table)
- `VO + Shift + Up Arrow`: Exit a group

**Specific Things to Check**:

1. **Landmark Navigation**: Use `VO + U` → Landmarks. Verify all major page regions are announced (navigation, main, search, complementary). When multiple nav elements exist, each should have an `aria-label` to distinguish them.

2. **Heading Navigation**: Use `VO + H` to jump between headings. Verify logical hierarchy (no skipped levels) and descriptive headings. The rotor shows all headings—verify the list makes sense and headings describe their sections.

3. **Form Navigation**: Tab through forms. Verify:
   - Labels are announced before inputs ("Email address, edit text")
   - Required fields are indicated ("Email address, required, edit text")
   - Error messages are associated and announced when fields are invalid
   - Fieldset/legend provides context for grouped inputs
   - Placeholder text is NOT relied upon as the label

4. **Dynamic Content**: Watch for announcements when content changes:
   - Route changes in SPAs should be announced (use `aria-live` or update `document.title`)
   - Loading states should be announced ("Loading search results...")
   - Search results should announce when they load ("5 results found")
   - Error messages should be announced immediately (use `aria-live="assertive"`)
   - Success messages should be announced (use `aria-live="polite"`)

5. **Button Labels**: Icon-only buttons must have `aria-label`. Verify "button, [label]" is announced, not just "button". Test with `VO + B` to navigate by buttons—all should have meaningful names.

6. **Link Context**: Links should make sense out of context. Use `VO + L` to navigate by links. "Click here" is meaningless—verify descriptive link text. Links should indicate their destination or action.

7. **Table Navigation**: Use `VO + Command + Arrow` to navigate tables:
   - Headers should be announced for each cell ("Name, column 1, row 2, John")
   - Complex tables should use `headers` attribute to associate cells with multiple headers
   - Tables should have captions or `aria-label` describing their purpose

8. **Modal/Dialog Testing**:
   - When a modal opens, focus should move to the modal
   - Background content should be hidden from screen readers (`aria-hidden="true"`)
   - Modal should be announced ("Dialog, [title]")
   - Escape key should close the modal
   - Focus should return to trigger element when modal closes

9. **Dropdown/Menu Testing**:
   - Dropdown trigger should announce state ("Menu button, collapsed" or "expanded")
   - Arrow keys should navigate menu items
   - Selected items should be announced ("Option 1, selected")
   - Escape should close the menu
   - Focus should return to trigger when menu closes

10. **Accordion Testing**:
    - Accordion headers should announce expanded/collapsed state
    - Arrow keys should expand/collapse (not navigate between accordions)
    - Panel content should be hidden when collapsed (`aria-hidden="true"`)
    - Multiple accordions should be independently controllable

**Common VoiceOver Issues**:
- Missing landmark labels when multiple nav elements exist
- Buttons announced as "button" without accessible name
- Form fields announced without labels
- Dynamic content changes not announced (SPA route changes, async loading)
- Tables without proper header associations
- Modals not trapping focus or hiding background content
- Dropdowns not announcing state changes
- Accordions not updating `aria-expanded` when toggled

### NVDA (Windows) Testing

**Getting Started**: Download NVDA from nvaccess.org (free, open source). Basic navigation:
- `Insert + N`: Toggle NVDA on/off
- `Insert + F7`: Open elements list
- `H`: Navigate by headings
- `L`: Navigate by links
- `R`: Navigate by regions
- `D`: Navigate by landmarks
- `B`: Navigate by buttons
- `F`: Navigate by form fields
- `T`: Navigate by tables
- `Insert + Space`: Toggle between browse mode and focus mode
- `Insert + Q`: Read current line
- `Insert + Up Arrow`: Read from current position to end

**Specific Things to Check**:

1. **Elements List**: Use `Insert + F7` to see all headings, links, form fields, landmarks. Verify:
   - Completeness (all interactive elements are listed)
   - Proper labeling (no "button" without name, no "link" without text)
   - Logical grouping and organization

2. **Browse Mode vs Focus Mode**: NVDA switches between browse mode (reading) and focus mode (interacting):
   - Browse mode: Use arrow keys to read content, H/L/B to navigate by element type
   - Focus mode: Automatically activates for form fields, comboboxes, and other interactive elements
   - Verify mode switches correctly—entering a text input should switch to focus mode
   - Verify you can return to browse mode with `Insert + Space` when needed

3. **Table Navigation**: Use `T` to navigate tables:
   - Headers should be announced with cell content ("Name, column 1, row 2, John")
   - Use `Insert + Ctrl + Arrow` to navigate cell by cell
   - Verify headers are associated correctly (use `headers` attribute for complex tables)
   - Table purpose should be clear from caption or `aria-label`

4. **ARIA Live Regions**: NVDA announces aria-live changes:
   - Test with `aria-live="polite"` (waits for natural pause)
   - Test with `aria-live="assertive"` (interrupts immediately)
   - Verify timing matches urgency—errors should interrupt, status updates should wait
   - Multiple announcements should not cut each other off

5. **Form Validation**: Tab through forms and verify:
   - Error messages are announced when fields become invalid
   - Errors are associated with fields (`aria-describedby`)
   - Required fields are indicated (`aria-required` or visual indicator)
   - Fieldset/legend provides context for grouped inputs
   - Validation occurs at appropriate times (on blur, not every keystroke)

6. **Focus Indicators**: Verify focus is visible and announced correctly:
   - Focus should be clearly visible (not just announced)
   - Focus order should follow logical reading order
   - Custom focus styles should meet 3:1 contrast requirement
   - Focus should not jump unexpectedly

7. **Dynamic Content in SPAs**:
   - Route changes should be announced (update `document.title` or use `aria-live`)
   - Async content loading should be announced ("Loading...", "5 results found")
   - Search results should announce when they appear
   - Infinite scroll should announce new content

8. **Modal/Dialog Testing**:
   - When modal opens, NVDA should announce "Dialog, [title]"
   - Background should be hidden (`aria-hidden="true"` on backdrop)
   - Focus should be trapped within modal
   - Escape should close modal
   - Focus should return to trigger when modal closes

9. **Dropdown/Menu Testing**:
   - Trigger should announce state ("Menu button, collapsed" or "Menu button, expanded")
   - Arrow keys should navigate menu items
   - `aria-activedescendant` should update as you navigate
   - Selected items should be announced
   - Escape should close menu

**Common NVDA Issues**:
- ARIA attributes not announced correctly (check role, state, properties)
- Form fields missing labels or descriptions
- Dynamic content not announced via aria-live (especially SPA route changes)
- Focus management issues in modals/dialogs (not trapped, not restored)
- Missing skip links or landmarks
- Browse mode not switching to focus mode for interactive elements
- Tables without proper header associations

### Testing Checklist

**Page Structure**:
- [ ] Page title is descriptive and unique
- [ ] One `<h1>` per page, representing main content
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] Landmarks are properly labeled (especially when multiple exist)
- [ ] Skip links work and are the first focusable element

**Navigation**:
- [ ] All navigation links are keyboard accessible
- [ ] Focus order follows visual layout
- [ ] Focus indicators are visible
- [ ] Current page is indicated in navigation (aria-current or visually)

**Forms**:
- [ ] All inputs have associated labels
- [ ] Required fields are indicated (aria-required or visually)
- [ ] Error messages are associated with fields (aria-describedby)
- [ ] Errors are announced when they appear (aria-live)
- [ ] Fieldset/legend used for grouped inputs

**Interactive Components**:
- [ ] Buttons have accessible names (text content or aria-label)
- [ ] Links have descriptive text (not "click here")
- [ ] Modals trap focus and restore focus on close
- [ ] Dropdowns announce state (aria-expanded)
- [ ] Tabs announce selected state (aria-selected)
- [ ] Accordions announce expanded state (aria-expanded)

**Dynamic Content**:
- [ ] Loading states are announced
- [ ] Error messages are announced (aria-live="assertive")
- [ ] Success messages are announced (aria-live="polite")
- [ ] Search results are announced when they load
- [ ] Route changes are communicated (SPA navigation)

**Tables**:
- [ ] Tables have captions or aria-label
- [ ] Headers have scope attributes
- [ ] Complex tables use headers attribute on cells
- [ ] Table navigation works correctly

**Images**:
- [ ] All images have alt text (empty for decorative)
- [ ] Alt text is descriptive and contextual
- [ ] Complex images have longer descriptions

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
