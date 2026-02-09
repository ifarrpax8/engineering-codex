# Accessibility: Architecture

## WCAG 2.1 Principles: POUR Framework

The Web Content Accessibility Guidelines (WCAG) 2.1 organizes accessibility requirements around four foundational principles, remembered by the acronym POUR: Perceivable, Operable, Understandable, and Robust. These principles form the architectural foundation for accessible design.

### Perceivable

Information and user interface components must be presentable to users in ways they can perceive. This means that content cannot be invisible to all of a user's senses. For users who cannot see, visual information must have text alternatives. For users who cannot hear, audio information must have captions or transcripts. For users who cannot distinguish colors, information must not rely solely on color.

Text alternatives for images ensure that screen reader users understand the content and purpose of images. Decorative images that add no information should have empty alt attributes. Informative images need descriptive alt text that conveys the same information the image provides to sighted users. Complex images like charts and diagrams may need longer descriptions provided through aria-describedby or visible text.

Captions and transcripts make audio and video content accessible to deaf and hard-of-hearing users. Captions should be synchronized with the audio and include speaker identification and sound effects. Transcripts provide a text alternative that can be read at the user's pace.

Color contrast requirements ensure that text is readable for users with low vision or color vision deficiencies. WCAG AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text (18pt or 14pt bold). This contrast must be maintained across all text-background combinations, including in both light and dark themes.

Text resizing ensures that users with low vision can enlarge text without losing functionality. Content must remain usable when text is resized up to 200% using browser zoom or user preferences. This requires using relative units (rem, em, %) rather than absolute units (px) for font sizes and ensuring layouts reflow appropriately.

### Operable

User interface components and navigation must be operable by all users. This means that users must be able to interact with all interface elements regardless of their input method. Keyboard accessibility is fundamental—if functionality works with a keyboard, it typically works with assistive technology.

Keyboard accessibility requires that all interactive elements are reachable and usable via keyboard input. Users must be able to navigate to every button, link, form control, and custom component using the Tab key. The focus order must follow a logical sequence that matches the visual layout. Custom keyboard shortcuts should follow established patterns (arrow keys for menus, Escape to close dialogs, Enter to activate).

Sufficient time must be provided for users to read and interact with content. Auto-updating content must have controls to pause, stop, or hide updates. Time limits must be adjustable, extendable, or removable. This accommodates users who need more time to read or interact due to cognitive disabilities or motor impairments.

Seizure and physical reaction triggers must be avoided. Content must not flash more than three times per second, as rapid flashing can trigger photosensitive epilepsy. This applies to animations, transitions, and any content that changes rapidly.

Navigation must be clear and consistent. Users need multiple ways to find content: navigation menus, site maps, search functionality, and clear page structure. Skip links allow keyboard users to bypass repetitive navigation and jump directly to main content. Consistent navigation patterns across pages reduce cognitive load.

### Understandable

Information and the operation of user interface components must be understandable. This means that content must be readable and that interface behavior must be predictable.

Readable content uses clear, simple language appropriate for the audience. Technical jargon should be explained, and abbreviations should be expanded on first use. Reading level should be appropriate for the content's purpose. For general audiences, aim for an 8th-grade reading level.

Predictable interfaces behave consistently across pages and components. Navigation elements should appear in the same locations. Functionality should work the same way in similar contexts. Unexpected changes of context (like automatic form submission or page navigation) should only occur when initiated by the user or when the user is warned in advance.

Input assistance helps users avoid and correct mistakes. Form labels must be clear and associated with their inputs. Error messages must be specific, understandable, and suggest corrections. Required fields must be clearly indicated. Validation should occur at appropriate times and provide clear feedback.

### Robust

Content must be robust enough to be interpreted reliably by a wide variety of user agents, including assistive technologies. This means using valid HTML, proper ARIA attributes, and following web standards.

Valid HTML ensures that browsers and assistive technologies can parse content correctly. Invalid HTML may be interpreted differently by different tools, leading to inconsistent experiences. HTML validation should be part of the development workflow.

ARIA attributes enhance semantic meaning when native HTML elements are insufficient. ARIA roles define what an element is, ARIA states communicate dynamic state, and ARIA properties provide additional context. ARIA must be used correctly—incorrect ARIA is worse than no ARIA, as it provides false information to assistive technologies.

Compatibility with current and future tools requires following web standards and avoiding proprietary or deprecated features. Content should work with current versions of screen readers, browser extensions, and other assistive technologies, and should be structured to work with future tools as well.

## Semantic HTML: The Foundation of Accessibility

Semantic HTML uses HTML elements that convey meaning about the content they contain. Semantic elements have built-in accessibility features: keyboard support, focus management, and screen reader announcements. Using semantic HTML is the most effective way to build accessible interfaces.

### Native HTML Elements

Native HTML elements provide accessibility by default. A `<button>` element has built-in keyboard support (Enter and Space activate it), focus management, and screen reader announcement ("button"). A `<div>` with an onclick handler has none of these features and requires custom implementation of keyboard handlers, focus management, and ARIA attributes.

Use `<button>` for all interactive elements that trigger actions, not `<div>` or `<span>` with click handlers. Buttons are focusable, keyboard accessible, and announced correctly by screen readers. Use `<a>` for navigation links, not `<span>` with click handlers. Links are keyboard accessible and can be opened in new tabs. Use form elements (`<input>`, `<select>`, `<textarea>`) for data collection, not custom div-based components.

Form elements have built-in labels, validation states, and keyboard support. Native form controls work with screen readers without additional ARIA. Custom form components require extensive ARIA and keyboard handling to match native functionality.

### Heading Hierarchy

Headings create a navigable document outline for screen reader users. Screen readers provide a headings list that users can navigate to quickly understand page structure and jump to sections of interest. Proper heading hierarchy is essential for accessibility.

Use headings in order: `<h1>` for the main page title, `<h2>` for major sections, `<h3>` for subsections, and so on. Never skip heading levels—don't jump from `<h1>` to `<h3>` without an `<h2>` in between. Skipping levels creates confusion for screen reader users navigating the headings list.

There should be exactly one `<h1>` per page, representing the main topic or purpose of the page. Multiple `<h1>` elements break the document outline and confuse screen reader users about the page's primary content.

Headings should describe the content that follows them. Screen reader users often navigate by headings, so descriptive headings help users understand what content is in each section. Avoid generic headings like "Section" or "Content"—use specific, descriptive headings.

### Landmarks and Page Structure

HTML5 semantic elements create navigable landmarks that screen reader users can jump between. These landmarks provide structure and navigation shortcuts, significantly improving the experience for screen reader users.

The `<nav>` element creates a navigation landmark. Use it for primary navigation menus, breadcrumbs, and pagination. Multiple `<nav>` elements are allowed if they serve different purposes. Each should have an accessible name (via aria-label) if there are multiple nav elements.

The `<main>` element identifies the primary content of the page. There should be exactly one `<main>` element per page. This landmark allows screen reader users to jump directly to the main content, bypassing navigation and other repetitive elements.

The `<header>` element typically contains site-wide header content like logos and primary navigation. The `<footer>` element contains footer content like copyright information and links. The `<aside>` element contains complementary content like sidebars and callouts.

The `<article>` element represents a self-contained piece of content that could be distributed independently. Use it for blog posts, news articles, or forum posts. The `<section>` element represents a thematic grouping of content, typically with a heading.

Screen reader users can navigate between these landmarks using keyboard shortcuts, making it easy to understand page structure and jump to relevant sections. Always provide accessible names for landmarks when there are multiple instances of the same landmark type.

### Lists

Lists provide important structural information to screen reader users. When screen readers encounter a list, they announce "list, X items" and then read each item. This context helps users understand that items are related and part of a group.

Use `<ul>` for unordered lists (bulleted lists), `<ol>` for ordered lists (numbered lists), and `<dl>` for description lists (term-definition pairs). Never use plain `<div>` elements styled to look like lists—screen readers won't announce them as lists, and users lose important structural context.

List items must be properly nested within list containers. Each `<li>` must be a direct child of `<ul>` or `<ol>`. Don't use CSS to create list-like appearances without using actual list elements.

## ARIA: Accessible Rich Internet Applications

ARIA (Accessible Rich Internet Applications) is a set of attributes that enhance the accessibility of HTML when native elements are insufficient. ARIA provides additional semantic information to assistive technologies, communicates dynamic state changes, and enables accessible custom components.

### ARIA Roles

ARIA roles define what an element is or does. Roles communicate the purpose and behavior of elements to screen readers. Common roles include `dialog` for modal dialogs, `tab` for tab interfaces, `menu` for menus, `alert` for important messages, and `region` for distinct page sections.

Use roles when native HTML elements don't convey the correct semantics. For example, a custom dropdown built with divs needs `role="combobox"` to communicate that it's a dropdown. A custom checkbox built with divs needs `role="checkbox"` to communicate its state.

The first rule of ARIA is: don't use ARIA if a native HTML element provides the same semantics. A `<button>` is always better than `<div role="button">` because the button has built-in keyboard support and focus management. Only use ARIA roles when you cannot use a native element.

### ARIA States

ARIA states communicate the current condition of elements. States change as users interact with components, and screen readers announce these changes. Common states include `aria-expanded` (for collapsible sections), `aria-selected` (for selected items), `aria-checked` (for checkboxes), `aria-disabled` (for disabled elements), and `aria-hidden` (for hiding decorative content from screen readers).

States must be updated dynamically as component state changes. When a dropdown opens, set `aria-expanded="true"`. When an item is selected, set `aria-selected="true"`. Screen readers announce these state changes, keeping users informed about interface state.

Boolean states use `true` or `false` values. Tristate attributes like `aria-checked` can also use `"mixed"` for indeterminate states. Always use string values, not boolean JavaScript values, in HTML attributes.

### ARIA Properties

ARIA properties provide additional context and relationships between elements. Properties help screen readers understand how elements relate to each other and provide descriptive information.

`aria-label` provides an accessible name when the visible text is insufficient or when there is no visible text. Use it for icon-only buttons, decorative images that need context, or when the visible label doesn't fully describe the element's purpose.

`aria-labelledby` references the ID of another element that serves as the label. Use it when a visible label exists elsewhere in the DOM. This creates an explicit relationship between the label and the labeled element.

`aria-describedby` references elements that provide additional descriptive information, such as help text or error messages. Screen readers read the description after the label, providing context without cluttering the primary announcement.

`aria-required` indicates that a form field is required. This is important for screen reader users who may not see visual required indicators. Use it in addition to visual indicators, not as a replacement.

`aria-live` regions announce dynamic content changes to screen reader users. Use `aria-live="polite"` for non-urgent updates like search results loading. Use `aria-live="assertive"` for urgent updates like error messages. Screen readers will interrupt their current announcement to read assertive live regions.

## Keyboard Navigation Architecture

Keyboard navigation is the foundation of accessibility. If functionality works with a keyboard, it typically works with assistive technology. Designing for keyboard navigation ensures that users who cannot use a mouse can fully access all functionality.

### Focus Management

Focus management ensures that keyboard users can navigate to all interactive elements and that focus moves logically through the interface. The Tab key moves focus forward through focusable elements, and Shift+Tab moves focus backward. The focus order should follow the visual layout and reading order.

All interactive elements must be focusable. Native interactive elements (buttons, links, form controls) are focusable by default. Custom interactive elements must have `tabindex="0"` to be included in the tab order. Use `tabindex="-1"` to make elements programmatically focusable but not in the tab order (useful for managing focus programmatically).

Focus indicators must be visible. Browsers provide default focus outlines, but these are often removed for aesthetic reasons. Never remove focus indicators entirely—keyboard users need to see where focus is. Use `:focus-visible` to show focus indicators only for keyboard navigation, not mouse clicks. This provides focus visibility for keyboard users while maintaining clean aesthetics for mouse users.

### Custom Keyboard Shortcuts

Complex components need custom keyboard shortcuts to be efficiently navigable. These shortcuts should follow established patterns that users expect. Arrow keys navigate within components like menus, tabs, and dropdowns. Enter and Space activate buttons and select items. Escape closes dialogs and cancels operations. Tab moves focus into and out of component groups.

Document custom keyboard shortcuts so users know they exist. Provide a way to discover shortcuts, such as a help dialog or keyboard shortcut reference. Consider providing a way to disable or customize shortcuts for users who may conflict with assistive technology shortcuts.

### Focus Trapping

Modals and dialogs must trap focus within themselves. When a dialog opens, focus moves to the dialog. When the user presses Tab at the last focusable element in the dialog, focus should move to the first focusable element in the dialog, not to elements behind the dialog. This prevents keyboard users from accidentally interacting with background content.

Focus trapping requires managing the tab order programmatically. When the dialog opens, store a reference to the element that triggered it. When the dialog closes, return focus to that element. This ensures keyboard users can continue their workflow seamlessly.

### Skip Links

Skip links allow keyboard users to bypass repetitive navigation and jump directly to main content. A "Skip to main content" link appears at the top of the page when it receives focus (typically hidden visually until focused). This saves keyboard users from tabbing through dozens of navigation items on every page load.

Skip links should be the first focusable element on the page. They should be visually hidden by default and become visible when focused. Use CSS like `sr-only` class (visually hidden but accessible to screen readers) combined with `:focus` styles to show the link when focused.

## Color and Visual Design

Visual design choices significantly impact accessibility. Color contrast, text sizing, and layout reflow determine whether content is perceivable and usable for users with visual disabilities.

### Color Contrast Requirements

WCAG AA requires a contrast ratio of at least 4.5:1 for normal text (smaller than 18pt or 14pt bold) and 3:1 for large text. Contrast ratio measures the difference in luminance between text and background colors. Higher contrast ratios are better—WCAG AAA requires 7:1 for normal text.

Contrast must be validated for all text-background combinations, including hover states, focus states, disabled states, and both light and dark themes. Design system color palettes should be validated for contrast compliance. Tailwind CSS utility classes should be checked to ensure accessible color combinations.

Contrast checkers like WebAIM Contrast Checker or Colour Contrast Analyser can validate contrast ratios. Automated tools can check contrast in component tests, but manual verification is important for complex designs and custom color combinations.

### Color as Information

Never use color alone to convey information. Approximately 8% of males have color vision deficiencies and cannot distinguish certain color combinations. Red and green are particularly problematic—many users cannot distinguish these colors.

Always provide additional visual indicators alongside color. Error states should include icons (like an X or warning symbol) in addition to red color. Success states should include checkmarks in addition to green color. Chart data should use different patterns or shapes in addition to different colors. Status indicators should include text labels in addition to color coding.

### Text Resizing and Reflow

Content must remain usable when text is resized up to 200% using browser zoom or user preferences. This requires using relative units (rem, em, %) for font sizes rather than absolute units (px). Relative units scale with user preferences, while absolute units do not.

Layouts must reflow appropriately when text is enlarged. Content should not require horizontal scrolling at 200% zoom. This requires responsive design principles: flexible layouts, relative sizing, and avoiding fixed widths.

At 400% zoom on a 1280px viewport (equivalent to 320px width), content must reflow without horizontal scrolling. This is a WCAG requirement that ensures content is usable on small screens and with high zoom levels. Use responsive breakpoints and flexible layouts to meet this requirement.

## Component Patterns for Accessibility

Accessible component patterns follow consistent interaction models that users expect. These patterns ensure that custom components work with keyboards and screen readers.

### Modals and Dialogs

Modals require focus trapping, keyboard support, and proper ARIA attributes. When a modal opens, focus moves to the modal (typically the first focusable element or the modal container with `tabindex="-1"`). The modal has `role="dialog"` and `aria-modal="true"` to communicate its purpose. The modal has an accessible name via `aria-labelledby` pointing to a heading or `aria-label`.

Escape key closes the modal. Tab key is trapped within the modal. When the modal closes, focus returns to the element that triggered it. The background is hidden from screen readers using `aria-hidden="true"` on the backdrop.

In Vue 3, use `<Teleport>` to render modals outside the component tree for proper DOM order. In React, use Portals for the same purpose. Manage focus with template refs (Vue) or useRef (React) and lifecycle hooks.

### Tabs

Tab interfaces require arrow key navigation and proper ARIA. The tab list has `role="tablist"`. Each tab button has `role="tab"` and `aria-selected` indicating whether it's selected. The tab panel has `role="tabpanel"` and `aria-labelledby` pointing to its associated tab.

Arrow keys navigate between tabs (Left/Right for horizontal, Up/Down for vertical). Tab key moves focus into the tab panel content. When a tab is activated, `aria-selected` updates and focus moves to the tab panel. The previously selected tab has `aria-selected="false"`.

### Dropdowns and Menus

Dropdowns and menus require arrow key navigation, Enter/Space to select, and Escape to close. The trigger button has `aria-expanded` indicating whether the menu is open. The menu has `role="menu"` or `role="listbox"` depending on the pattern. Menu items have `role="menuitem"` or `role="option"`.

Arrow keys navigate between menu items. Enter and Space activate the selected item. Escape closes the menu without selection. When the menu opens, focus moves to the first menu item. When it closes, focus returns to the trigger.

### Toast Notifications

Toast notifications require aria-live regions to announce content to screen reader users. The notification container has `aria-live="polite"` for non-urgent notifications or `aria-live="assertive"` for urgent notifications. Each notification should have `role="alert"` or `role="status"` depending on its importance.

Notifications should be dismissible with a close button. They should auto-dismiss after sufficient time (at least 5 seconds) for users to read them. Notifications should not disappear too quickly for screen reader users to hear the announcement.

### Data Tables

Data tables require proper markup for screen reader navigation. Use `<table>`, `<thead>`, `<tbody>`, and `<th>` elements. Each `<th>` should have a `scope` attribute (`scope="col"` for column headers, `scope="row"` for row headers). Complex tables may need `headers` attributes on `<td>` elements to associate cells with their headers.

Tables should have a `<caption>` or `aria-label` describing their purpose. Screen reader users can navigate tables cell by cell, with headers announced for context. Proper markup makes this navigation meaningful.
