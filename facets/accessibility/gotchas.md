# Accessibility: Gotchas

## Contents

- [Using Div and Span for Everything](#using-div-and-span-for-everything)
- [Removing Focus Outlines](#removing-focus-outlines)
- [Images Without Alt Text](#images-without-alt-text)
- [Placeholder as Label](#placeholder-as-label)
- [Color-Only Status Indicators](#color-only-status-indicators)
- [Inaccessible Custom Components](#inaccessible-custom-components)
- [Auto-Playing Media](#auto-playing-media)
- [Insufficient Color Contrast](#insufficient-color-contrast)
- [Missing Skip Links](#missing-skip-links)
- [Dynamic Content Not Announced](#dynamic-content-not-announced)
- [Form Validation That Only Uses Visual Cues](#form-validation-that-only-uses-visual-cues)

## Using Div and Span for Everything

One of the most common accessibility mistakes is using generic `<div>` and `<span>` elements for interactive components instead of semantic HTML elements. Developers create `<div onclick>` buttons, `<span>` links, and `<div>` navigation menus because they're easier to style or seem more flexible.

These generic elements have no semantic meaning, no built-in keyboard support, and are invisible to screen readers without extensive ARIA attributes. A `<div>` with an onclick handler requires custom keyboard event handlers, custom focus management with `tabindex`, ARIA roles and states, and screen reader announcements. This is significantly more work than using a `<button>` element, which provides all of this functionality automatically.

The problem extends beyond buttons and links. Navigation should use `<nav>` with proper list markup (`<ul>` and `<li>`), not `<div>` elements styled to look like navigation. Forms should use proper form elements, not div-based custom components. Lists should use `<ul>`, `<ol>`, or `<dl>`, not divs styled to look like lists.

Screen reader users rely on semantic HTML to understand page structure. When everything is a div, screen readers can't distinguish between navigation, main content, forms, and other page regions. The page becomes a sea of generic content with no structure or meaning.

Fix this by using semantic HTML elements: `<button>` for actions, `<a>` for navigation, `<nav>` for navigation regions, `<form>` for forms, `<input>` for form controls, and proper list elements for lists. Only use divs and spans when they're truly generic containers with no semantic meaning.

## Removing Focus Outlines

Developers often remove focus outlines because they consider them visually unappealing. CSS like `outline: none` or `* { outline: none }` removes the visible focus indicators that keyboard users depend on to navigate interfaces.

Without focus indicators, keyboard users cannot see where focus is, making navigation impossible. They don't know which element will be activated when they press Enter or Space. This completely breaks keyboard accessibility, excluding users who cannot use a mouse.

The solution is not to remove focus outlines entirely, but to customize them appropriately. Use `:focus-visible` to show focus indicators only for keyboard navigation, not mouse clicks. This provides focus visibility for keyboard users while maintaining clean aesthetics for mouse users. Customize focus styles to match your design system while ensuring they're clearly visible with sufficient contrast.

Never use `outline: none` without providing an alternative focus indicator. If you remove the default outline, you must add a custom focus style that's equally or more visible. Focus indicators should have at least a 2px outline or border with sufficient contrast against the background.

## Images Without Alt Text

Images without alt text are one of the most common accessibility violations. Screen readers announce "image" with no context, or worse, read the filename (like "IMG_20240315_143022.jpg"), providing no useful information to users.

Every image must have an `alt` attribute. Decorative images that add no information should have `alt=""` (empty string) to tell screen readers to skip them. Informative images need descriptive alt text that conveys the same information the image provides to sighted users.

The problem often occurs when images are added dynamically via JavaScript, when alt attributes are forgotten during development, or when developers don't understand the difference between decorative and informative images. Content management systems may also fail to require alt text when images are uploaded.

Alt text should be concise but descriptive—typically a sentence or two. It should focus on the content and purpose of the image, not its appearance. Avoid redundant phrases like "image of" since screen readers already announce that it's an image.

Fix this by always including alt attributes when adding images, validating that alt text is provided in content management systems, and training content creators on writing effective alt text. Automated tools can catch missing alt attributes, but meaningful alt text requires human judgment.

## Placeholder as Label

Using placeholder text instead of visible labels is a common mistake that makes forms inaccessible. Placeholder text disappears when users start typing, has insufficient color contrast (typically light gray), and is not consistently announced by screen readers as a label.

Screen reader users may not hear placeholder text at all, or it may be announced inconsistently across different screen readers. Even when announced, placeholder text doesn't provide the same context as a proper label because it disappears on input, making it impossible to reference while filling out the form.

Placeholder text also causes problems for users with cognitive disabilities who may forget what the field is for after they start typing. Users with motor impairments may click into fields accidentally, causing placeholder text to disappear before they can read it.

The solution is to always use visible `<label>` elements associated with form inputs using the `for` attribute matching the input's `id`. Placeholder text can provide helpful hints in addition to labels, but it must never be the only way to understand what an input is for.

Labels should be positioned near their inputs and should be clearly visible with sufficient color contrast. Only hide labels visually (using `sr-only` class) when the input's purpose is obvious from context, such as search inputs with visible "Search" buttons.

## Color-Only Status Indicators

Using color alone to convey information excludes users with color vision deficiencies, who represent approximately 8% of the male population. Status indicators that rely solely on color (green for success, red for error) are invisible to these users.

The problem occurs in error states, success messages, chart data, status indicators, and form validation. When color is the only way to distinguish between states, color-blind users cannot access that information. This violates WCAG requirements and creates barriers for a significant portion of users.

The solution is to always provide additional visual indicators alongside color. Error states should include icons (like an X or warning symbol) in addition to red color. Success states should include checkmarks in addition to green color. Chart data should use different patterns, shapes, or labels in addition to different colors.

Form validation should not rely solely on colored borders. Include icons, text labels, or other visual indicators that don't depend on color perception. Error messages should be clearly visible and associated with form fields using `aria-describedby`.

Test interfaces using color blindness simulators to identify issues. Tools like Colour Contrast Analyser include color blindness filters that show how interfaces appear to users with different types of color vision deficiencies.

## Inaccessible Custom Components

Building custom interactive components like dropdowns, date pickers, and modals without proper accessibility support is a common mistake that creates significant barriers. These components require extensive keyboard support, ARIA attributes, and focus management to be accessible.

Custom dropdowns need arrow key navigation, Enter/Space to select, Escape to close, proper ARIA attributes (`role="combobox"`, `aria-expanded`, `aria-activedescendant`), and focus management. Custom date pickers need keyboard navigation, proper labeling, and screen reader support. Custom modals need focus trapping, keyboard support, and proper ARIA.

Implementing all of this correctly is complex and error-prone. Many custom components are built with only mouse support, making them completely inaccessible to keyboard and screen reader users. Even when keyboard support is added, it's often incomplete or buggy.

The solution is to use design system components or established accessible component libraries instead of building custom components from scratch. Propulsion design system components are built with accessibility in mind and provide accessible patterns out of the box.

If you must build custom components, follow established patterns from ARIA Authoring Practices Guide and test extensively with keyboard navigation and screen readers. Consider using headless UI libraries that provide accessible behavior without styling, allowing you to customize appearance while maintaining accessibility.

## Auto-Playing Media

Auto-playing video or audio content is disorienting and problematic for screen reader users, whose assistive technology output competes with the media audio. Auto-playing media can also trigger motion sensitivity issues and is generally considered poor user experience.

WCAG requires that auto-playing media can be paused or stopped. However, the better practice is to never auto-play media with audio. If media must auto-play, it should be muted by default with controls to unmute. Auto-playing media without audio (like background videos) is less problematic but should still have controls to pause.

Auto-playing media causes particular problems for screen reader users because the media audio interferes with screen reader output. Users may not realize that media is playing and may struggle to find controls to stop it. This creates a barrier to accessing the rest of the page content.

The solution is to never auto-play media with audio. Provide clear play controls and let users choose when to start media. If media must auto-play for design reasons, ensure it's muted by default and provide prominent controls to play with audio.

For background videos or animations, ensure they can be paused and don't distract from main content. Consider providing a "reduce motion" preference that stops animations for users who prefer reduced motion.

## Insufficient Color Contrast

Light gray text on white backgrounds or dark gray text on dark backgrounds may look aesthetically pleasing to designers but is unreadable for users with low vision. WCAG AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text.

The problem often occurs when designers prioritize aesthetics over accessibility, when color palettes aren't validated for contrast, or when text colors are chosen without considering background colors. Tailwind CSS utility classes may combine in ways that don't meet contrast requirements.

Insufficient contrast affects not just users with visual disabilities but also users viewing screens in bright sunlight, users with older displays, and users who need to reduce eye strain. High contrast benefits all users.

The solution is to validate color contrast for all text-background combinations using contrast checker tools. Design system color palettes should be validated and documented with accessible color combinations. Automated tools can check contrast in component tests, but manual verification is important for complex designs.

Test contrast in both light and dark themes if the application supports theme switching. Colors that meet contrast requirements in one theme may not meet them in another. Ensure sufficient contrast across all theme variations.

## Missing Skip Links

Keyboard users must tab through dozens of navigation items on every page to reach the main content. This creates a significant barrier and wastes time, especially for users who navigate the same site frequently.

Skip links provide a way to bypass repetitive navigation and jump directly to main content. A "Skip to main content" link appears at the top of the page when it receives focus (typically hidden visually until focused). This allows keyboard users to skip navigation efficiently.

Skip links should be the first focusable element on the page, so they're immediately available when users press Tab. They should be visually hidden by default using CSS (like `sr-only` class) and become visible when focused. The link should jump to the main content area using an anchor link.

The solution is to add skip links to all pages, especially pages with extensive navigation. Skip links are simple to implement but provide significant value to keyboard users. They're a WCAG requirement for pages with repetitive navigation.

Consider additional skip links for other repetitive content like sidebars or footer links. The goal is to allow keyboard users to efficiently navigate to the content they need without tabbing through every navigation item.

## Dynamic Content Not Announced

When content loads asynchronously (search results, notifications, form errors, live updates), screen reader users may not know that new content has appeared. Screen readers read content linearly and don't automatically detect dynamic changes.

The problem occurs when developers add content to the DOM without using aria-live regions to announce changes. Screen reader users may miss important updates like error messages, success notifications, or new search results because they're not announced.

The solution is to use aria-live regions to announce dynamic content changes. Use `aria-live="polite"` for non-urgent updates like search results loading. Use `aria-live="assertive"` for urgent updates like error messages that block form submission.

Live regions should be set up once and reused for dynamic content. When content is added to or updated within a live region, screen readers will announce the change. The content should be meaningful and concise—screen readers will read the entire live region content when it updates.

For form validation, connect error messages to inputs using `aria-describedby` and announce errors with aria-live when they appear. This ensures screen reader users are immediately informed of validation errors.

## Form Validation That Only Uses Visual Cues

Form validation that relies solely on visual indicators like colored borders or icons is inaccessible to screen reader users who cannot see these visual cues. Red borders on invalid fields don't help screen reader users understand what's wrong or how to fix it.

The problem occurs when validation feedback is only visual: red borders, error icons, or color-coded messages. Screen reader users may not realize that validation has occurred or what the errors are. They may submit forms with errors because they're unaware of validation failures.

The solution is to make validation messages accessible through multiple channels: visual indicators (colors, icons), text messages, ARIA attributes, and screen reader announcements. Error messages should be associated with form fields using `aria-describedby` and should be announced via aria-live when they appear.

Error messages should be clear and actionable, explaining what's wrong and how to fix it. "Invalid input" is not helpful—"Email must be a valid email address" provides useful guidance. Error messages should appear near their associated inputs, both visually and in the DOM order.

Validation should occur at appropriate times: on blur for individual fields, and on submit for the entire form. Don't validate on every keystroke, as this creates excessive announcements that interfere with screen reader output. Provide clear, timely feedback that helps users correct errors efficiently.
