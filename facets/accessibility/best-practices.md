# Accessibility: Best Practices

## Contents

- [Use Semantic HTML First, ARIA Second](#use-semantic-html-first-aria-second)
- [Every Image Needs Alternative Text](#every-image-needs-alternative-text)
- [Every Form Input Needs a Label](#every-form-input-needs-a-label)
- [Manage Focus Intentionally](#manage-focus-intentionally)
- [Design for Keyboard First](#design-for-keyboard-first)
- [Use the Design System](#use-the-design-system)
- [Make Error Messages Accessible](#make-error-messages-accessible)
- [Stack-Specific Best Practices](#stack-specific-best-practices)

## Use Semantic HTML First, ARIA Second

The most effective accessibility practice is to use semantic HTML elements that provide built-in accessibility features. Native HTML elements like `<button>`, `<a>`, `<input>`, and `<nav>` have built-in keyboard support, focus management, and screen reader announcements. They work correctly with assistive technologies without additional code.

When you use a `<button>` element, you get keyboard support (Enter and Space activate it), focus management, and screen reader announcement ("button") automatically. When you use a `<div>` with an onclick handler and `role="button"`, you must implement keyboard handlers, manage focus, and ensure ARIA attributes are correct. The semantic HTML approach is simpler, more maintainable, and less error-prone.

The first rule of ARIA is: don't use ARIA if a native HTML element provides the same semantics. Only use ARIA when you cannot use a native element, such as when building complex custom components that don't map to standard HTML elements. Even then, prefer using native elements as the foundation and enhancing them with ARIA rather than building completely custom components.

Semantic HTML also provides benefits beyond accessibility: better SEO, easier maintenance, and improved performance. Browsers optimize native elements, and semantic markup is more efficient than complex custom markup.

## Every Image Needs Alternative Text

Images must have alternative text that conveys the same information to screen reader users that the image provides to sighted users. The `alt` attribute is required for all `<img>` elements, and the value depends on the image's purpose.

Decorative images that add no information should have empty alt attributes: `alt=""`. This tells screen readers to skip the image, preventing meaningless announcements like "decorative line" or "spacer image". Decorative images include purely visual elements like borders, dividers, and background images.

Informative images that convey content need descriptive alt text that conveys the same information. Alt text should be concise but descriptive—typically a sentence or two. Avoid redundant phrases like "image of" or "picture of" since screen readers already announce that it's an image. Focus on the content and purpose of the image.

Complex images like charts, diagrams, and infographics may need longer descriptions. Provide these through `aria-describedby` pointing to a detailed description, or provide a visible text equivalent. For data visualizations, consider providing the underlying data in a table format that screen reader users can navigate.

Functional images like icons in buttons or links should have alt text that describes their function, not their appearance. An icon button with a trash icon should have alt text like "Delete item" not "Trash icon". The alt text should match the button's function.

## Every Form Input Needs a Label

Every form input must have an associated label that clearly describes its purpose. Labels provide context to all users and are essential for screen reader users who rely on labels to understand form fields.

Use the `<label>` element with a `for` attribute that matches the input's `id`. This creates an explicit association that screen readers understand. When users click the label, focus moves to the associated input, improving usability for all users.

Placeholder text is not a substitute for labels. Placeholder text disappears when users start typing, has insufficient color contrast, and is not consistently announced by screen readers as a label. Placeholders can provide helpful hints, but they must be in addition to visible labels, not instead of them.

Labels should be visible and positioned near their inputs. While it's technically possible to hide labels visually while keeping them accessible to screen readers (using `sr-only` class), visible labels benefit all users and are generally preferred. Only hide labels when the input's purpose is obvious from context, such as search inputs with visible "Search" buttons.

For groups of related inputs like radio buttons or checkboxes, use a `<fieldset>` with a `<legend>` to provide a group label. Individual inputs within the group can have their own labels, but the fieldset legend provides context for the group.

## Manage Focus Intentionally

When content changes dynamically, focus must be managed explicitly to ensure keyboard users can continue their workflow. Dynamic content changes include dialogs opening, content loading asynchronously, sections expanding or collapsing, and page navigation.

When a dialog or modal opens, focus should move to the dialog. Typically, focus moves to the first focusable element in the dialog, or to the dialog container itself (with `tabindex="-1"` to make it focusable). This ensures keyboard users can immediately interact with the dialog without having to tab through background content.

When a dialog closes, focus should return to the element that triggered it. This allows keyboard users to continue their workflow seamlessly. Store a reference to the trigger element when opening the dialog, and restore focus to it when closing.

When content loads asynchronously (like search results or dynamically loaded sections), consider whether focus should move to the new content. For search results, moving focus to the results helps keyboard users access them immediately. For background updates, use aria-live regions to announce changes without moving focus.

When sections expand or collapse, update ARIA attributes (`aria-expanded`) to communicate state changes to screen readers. If the expanded content is focusable, ensure it's reachable via keyboard navigation.

Focus management requires careful consideration of user context and workflow. Test focus management with keyboard navigation to ensure it works correctly and feels natural.

## Design for Keyboard First

If functionality works with a keyboard, it typically works with assistive technology. Keyboard navigation is the foundation of accessibility, and designing for keyboard first ensures that interfaces are accessible to users who cannot use a mouse.

Test every interactive flow using only keyboard input before testing with screen readers or other assistive technologies. If you can complete a task with only keyboard input, it's likely accessible. If keyboard navigation is broken, the interface is inaccessible regardless of other accessibility features.

Keyboard navigation should be logical and predictable. The Tab key should move focus through interactive elements in a logical order that matches the visual layout. Custom keyboard shortcuts should follow established patterns that users expect.

Focus indicators must be visible for keyboard users. Never remove focus outlines entirely—keyboard users need to see where focus is to navigate effectively. Use `:focus-visible` to show focus indicators only for keyboard navigation, maintaining clean aesthetics for mouse users while ensuring accessibility for keyboard users.

All interactive elements must be keyboard accessible. Buttons, links, form controls, and custom components must be reachable and usable via keyboard. Test that every clickable element can be activated with Enter or Space, and that every input can be reached and used with keyboard.

## Use the Design System

Design system components are built with accessibility in mind and provide accessibility by default when used correctly. Using design system components ensures consistent accessibility patterns across the application and reduces the need for custom accessibility implementation.

Propulsion design system components include built-in keyboard support, ARIA attributes, focus management, and screen reader support. Using these components correctly provides accessibility without additional work. Don't override design system focus styles or ARIA attributes unless you have a specific accessibility reason.

Design system components are tested for accessibility, so using them reduces the risk of accessibility bugs. Custom components require extensive accessibility testing, while design system components have already been validated.

When design system components don't meet specific requirements, work with the design system team to enhance components rather than building custom alternatives. This benefits the entire organization and maintains consistency.

If you must build custom components, follow design system patterns and accessibility guidelines. Use design system components as reference implementations for accessibility best practices.

## Make Error Messages Accessible

Error messages must be accessible to screen reader users and provide clear, actionable guidance. Error messages that are only visually indicated (like red borders or icons) are inaccessible to screen reader users who cannot see colors or visual indicators.

Connect error messages to form fields using `aria-describedby` on the input, pointing to the error message element's ID. This creates an explicit association that screen readers understand. When the input receives focus, screen readers announce the error message.

Announce errors when they appear using `aria-live="assertive"` on the error container. This ensures screen reader users are immediately informed of errors, not just when they focus on the field. Use "assertive" for errors that block form submission, and "polite" for warnings or suggestions.

Error messages should be clear and actionable. "Invalid input" is not helpful—"Email must be a valid email address" tells users what's wrong and how to fix it. Error messages should explain the problem and suggest a solution.

Error messages should appear near the associated input, both visually and in the DOM order. This helps all users understand which field has the error. Don't put all error messages at the top of the form—associate them with their specific fields.

For form-level errors (like "Please correct the errors above"), provide a summary that lists all errors with links to the problematic fields. This helps screen reader users navigate to errors efficiently.

## Stack-Specific Best Practices

### Vue 3

Use `<Teleport>` to render modals and dialogs outside the component tree. This ensures proper DOM order for screen reader navigation and prevents focus management issues. Teleported content renders at the end of the body, making it easier to trap focus within dialogs.

Manage focus with template refs and lifecycle hooks. Use `ref()` to create references to focusable elements, and use `onMounted()` and `onUnmounted()` to manage focus when components mount and unmount. When dialogs open, move focus to the dialog using `focus()` on the template ref.

Use vue-announcer or similar libraries for screen reader announcements. These libraries provide a simple API for announcing dynamic content changes to screen reader users via aria-live regions.

Vue's reactivity system makes it easy to update ARIA attributes dynamically. Use computed properties or reactive data to manage ARIA states like `aria-expanded` and `aria-selected` based on component state.

### React

Use Portals for modals and dialogs to render outside the component tree. This ensures proper DOM order and focus management, similar to Vue's Teleport. React's `createPortal` renders content at a different DOM location while maintaining React's component hierarchy.

Use `useRef` and `useEffect` for focus management. Create refs for focusable elements and use effects to manage focus when components mount, update, or unmount. When dialogs open, move focus to the dialog in a `useEffect` that runs when the dialog's open state changes.

Consider using react-aria or similar libraries for accessible component patterns. These libraries provide hooks and components that handle keyboard navigation, ARIA attributes, and focus management automatically.

Use ErrorBoundary with accessible fallback UI. When errors occur, ErrorBoundary can render accessible error messages that screen reader users can understand. Ensure error messages are announced via aria-live regions.

### Tailwind CSS

Use the `sr-only` class for visually hidden text that should be accessible to screen readers. This class hides content visually while keeping it available to assistive technologies. Use it for skip links, additional context, or when visible labels would be redundant but screen reader context is needed.

Use the `focus-visible:` variant for keyboard-only focus indicators. This shows focus styles only when elements are focused via keyboard, not mouse clicks. This provides focus visibility for keyboard users while maintaining clean aesthetics for mouse users.

Validate color contrast for all utility color combinations. Tailwind's default color palette may not meet contrast requirements for all combinations. Use contrast checker tools to validate text-background combinations and document accessible color pairings.

Use responsive utilities to ensure content reflows at different zoom levels. Test that layouts work at 200% zoom and 320px width to meet WCAG reflow requirements.

### Testing

Use vitest-axe for component-level accessibility testing in Vitest test suites. This provides fast feedback during development and catches accessibility issues before code is committed. Run axe checks on every component render.

Use @axe-core/playwright for end-to-end accessibility testing in Playwright tests. This validates accessibility in the full application context, including dynamic content and JavaScript interactions. Run axe checks on critical user flows.

Use eslint-plugin-vuejs-accessibility or eslint-plugin-jsx-a11y for development-time accessibility checks. These linting rules catch common accessibility issues immediately in the editor, providing the fastest feedback loop.

Integrate accessibility testing into CI/CD pipelines to prevent regressions automatically. Configure tests to fail builds when accessibility violations are detected, ensuring accessibility standards are maintained.
