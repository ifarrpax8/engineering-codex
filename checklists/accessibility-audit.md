# Accessibility Audit Checklist

Use this checklist to verify WCAG 2.1 AA compliance before release. Cross-reference with the [Accessibility facet](../facets/accessibility/) for deeper guidance.

## Perceivable

- [ ] **Text alternatives for all non-text content** (images, icons, charts) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **Color not used as the only means of conveying information** → [accessibility/gotchas.md](../facets/accessibility/gotchas.md)
- [ ] **Sufficient color contrast** (4.5:1 for normal text, 3:1 for large text) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **Content readable and functional at 200% zoom** → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **Video/audio has captions or transcripts** (if applicable) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)

## Operable

- [ ] **All functionality available via keyboard** (Tab, Enter, Escape, Arrow keys) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **No keyboard traps** (user can always Tab away from any component) → [accessibility/gotchas.md](../facets/accessibility/gotchas.md)
- [ ] **Skip-to-content link present** → [navigation/best-practices.md](../experiences/navigation/best-practices.md)
- [ ] **Focus visible and styled** (not removed with outline: none) → [accessibility/gotchas.md](../facets/accessibility/gotchas.md)
- [ ] **Touch targets minimum 44x44px** → [responsive-design/best-practices.md](../experiences/responsive-design/best-practices.md)
- [ ] **No content that flashes more than 3 times per second** → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)

## Understandable

- [ ] **Page language declared** (html lang attribute) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **Form labels associated with inputs** (label for, aria-labelledby) → [forms-and-data-entry/best-practices.md](../experiences/forms-and-data-entry/best-practices.md)
- [ ] **Error messages identify the field and describe the error** → [content-strategy/best-practices.md](../experiences/content-strategy/best-practices.md)
- [ ] **Consistent navigation across pages** → [navigation/best-practices.md](../experiences/navigation/best-practices.md)
- [ ] **Instructions don't rely solely on sensory characteristics** ("click the red button") → [accessibility/gotchas.md](../facets/accessibility/gotchas.md)

## Robust

- [ ] **Valid, semantic HTML** (proper heading hierarchy, landmark regions) → [accessibility/architecture.md](../facets/accessibility/architecture.md)
- [ ] **ARIA used correctly** (roles, states, properties) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)
- [ ] **Custom components have appropriate ARIA roles** → [accessibility/architecture.md](../facets/accessibility/architecture.md)
- [ ] **Dynamic content changes announced** (aria-live regions) → [accessibility/best-practices.md](../facets/accessibility/best-practices.md)

## Automated Testing

- [ ] **axe-core or similar tool passes with no critical/serious violations** → [accessibility/testing.md](../facets/accessibility/testing.md)
- [ ] **Lighthouse accessibility score ≥ 90** → [accessibility/testing.md](../facets/accessibility/testing.md)
- [ ] **ESLint accessibility rules enabled** (eslint-plugin-jsx-a11y, eslint-plugin-vuejs-accessibility) → [accessibility/options.md](../facets/accessibility/options.md)

## Manual Testing

- [ ] **Screen reader tested** (VoiceOver on Mac, NVDA on Windows) → [accessibility/testing.md](../facets/accessibility/testing.md)
- [ ] **Keyboard-only navigation tested end-to-end** → [accessibility/testing.md](../facets/accessibility/testing.md)
- [ ] **High contrast mode tested** → [accessibility/testing.md](../facets/accessibility/testing.md)
