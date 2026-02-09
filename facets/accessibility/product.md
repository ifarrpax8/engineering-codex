# Accessibility: Product Perspective

## Contents

- [Accessibility as a Requirement, Not a Feature](#accessibility-as-a-requirement-not-a-feature)
- [Legal Requirements and Compliance](#legal-requirements-and-compliance)
- [Business Value of Accessibility](#business-value-of-accessibility)
- [Cost of Retrofitting Accessibility](#cost-of-retrofitting-accessibility)
- [User Personas and Accessibility Needs](#user-personas-and-accessibility-needs)
- [Success Metrics for Accessibility](#success-metrics-for-accessibility)

## Accessibility as a Requirement, Not a Feature

Accessibility is not an optional enhancement or a nice-to-have feature—it is a fundamental requirement for inclusive software design. Approximately 15-20% of the global population lives with some form of disability, which translates to over one billion people worldwide. When software is inaccessible, it completely excludes these users from participation, creating digital barriers that prevent them from accessing information, services, and opportunities that others take for granted.

This exclusion has both moral and legal implications. From a moral standpoint, building inaccessible software perpetuates inequality and discrimination. From a legal standpoint, inaccessible software violates disability rights laws in many jurisdictions and exposes organizations to significant legal and financial risk.

The impact of inaccessible software extends beyond users with permanent disabilities. Situational disabilities affect everyone at some point: a user with a broken arm cannot use a mouse, a user in a bright environment cannot see low-contrast text, a user in a noisy environment cannot hear audio content, and a user holding a baby cannot use both hands to interact with a device. Accessible design benefits all users, not just those with disabilities.

## Legal Requirements and Compliance

Multiple legal frameworks mandate accessibility compliance, and enforcement is increasing globally. In the United States, the Americans with Disabilities Act (ADA) requires that public accommodations, including websites and digital services, be accessible to people with disabilities. Title III of the ADA has been interpreted by courts to apply to websites and mobile applications, leading to numerous lawsuits against companies with inaccessible digital properties.

Section 508 of the Rehabilitation Act requires that federal agencies and organizations receiving federal funding ensure their electronic and information technology is accessible. This includes websites, software applications, and digital documents. Section 508 compliance is mandatory for federal contractors and agencies.

In the European Union, the European Accessibility Act (EN 301 549) establishes accessibility requirements for products and services, including websites and mobile applications. Member states are required to implement these standards, and non-compliance can result in significant penalties.

The Web Content Accessibility Guidelines (WCAG) 2.1 Level AA has become the de facto international standard for web accessibility. While WCAG itself is not a law, it is referenced by legal frameworks worldwide and is used as the technical standard for determining compliance. Many organizations adopt WCAG 2.1 AA as their minimum accessibility standard to ensure legal compliance and reduce risk.

The number of accessibility-related lawsuits has increased dramatically in recent years, with thousands of cases filed annually in the United States alone. These lawsuits can result in costly settlements, legal fees, and damage to brand reputation. Proactive accessibility compliance is far less expensive than reactive legal defense.

## Business Value of Accessibility

Accessible software creates tangible business value beyond legal compliance. The most direct benefit is market expansion: accessible products reach more users, increasing potential customer base and revenue. The disability community represents a significant market segment with substantial purchasing power, estimated at over $8 trillion globally.

Many accessibility improvements enhance the user experience for all users, not just those with disabilities. Keyboard navigation improvements benefit power users who prefer keyboard shortcuts for efficiency. Captions and transcripts benefit users in noisy environments, users learning a new language, and users who prefer reading to listening. High contrast modes benefit users viewing screens in bright sunlight. Clear, simple language benefits users with varying literacy levels and non-native speakers.

Accessibility improvements often align with search engine optimization (SEO) best practices. Semantic HTML, descriptive alt text for images, and well-structured content improve search engine rankings. Accessible websites tend to have better performance metrics, as semantic HTML is typically more efficient than complex custom markup.

Accessible design reduces support costs. When interfaces are clear, predictable, and easy to navigate, users make fewer mistakes and require less assistance. Accessible error messages and help text reduce confusion and support ticket volume.

Brand reputation benefits from demonstrating commitment to inclusion. Organizations that prioritize accessibility are viewed as socially responsible and customer-focused. This can improve customer loyalty and attract talent who value diversity and inclusion.

## Cost of Retrofitting Accessibility

Adding accessibility after a product is built is exponentially more expensive than building it in from the start. Studies indicate that retrofitting accessibility can cost 10-100 times more than incorporating accessibility during initial development. This cost multiplier exists because accessibility is fundamentally about structure and architecture, not surface-level styling.

Structural accessibility issues require significant rework. Using the wrong HTML elements (divs instead of buttons, spans instead of links) means rebuilding entire component hierarchies. Missing ARIA attributes require auditing every component and adding proper semantics. Inaccessible component patterns (custom dropdowns without keyboard support, modals without focus trapping) require complete rewrites.

When accessibility is retrofitted, it often feels like a bolt-on solution rather than an integrated feature. This can result in inconsistent user experiences, maintenance challenges, and technical debt. Components built with accessibility in mind from the start are more maintainable and robust.

The cost of retrofitting extends beyond development. It includes testing time, training for developers, potential design changes, and the risk of introducing bugs while modifying existing code. It may also require delaying new features while accessibility work is completed.

Building accessibility in from the start requires minimal additional time when developers understand accessibility principles and use accessible design system components. The investment in training and tooling pays for itself by preventing costly retrofits.

## User Personas and Accessibility Needs

Understanding diverse user needs is essential for building accessible software. Different disabilities require different accommodations, and users often have multiple overlapping needs.

Low vision users rely on screen magnification software that enlarges content 2-10x. They need sufficient color contrast to distinguish text from backgrounds, even when magnified. They benefit from high contrast modes and the ability to customize text size. Content must remain readable and functional when magnified, requiring responsive layouts that reflow properly.

Blind users rely on screen reader software that converts visual content into synthesized speech or braille output. Popular screen readers include JAWS (Windows), NVDA (Windows, free), and VoiceOver (macOS and iOS). Screen readers navigate content linearly and rely on semantic HTML and ARIA attributes to understand page structure. These users need descriptive labels, proper heading hierarchies, and announcements for dynamic content changes.

Motor impairment users may use keyboards exclusively, switch devices, voice control, or eye-tracking systems. They need all functionality accessible via keyboard, with logical tab order and sufficient time to complete tasks. They benefit from large click targets, reduced need for precision, and the ability to customize interaction timing.

Cognitive disability users need clear, simple language and predictable navigation patterns. They benefit from consistent layouts, clear error messages, and the ability to undo actions. Complex interfaces with too many options can be overwhelming. These users need content that is easy to understand and processes that are straightforward to follow.

Deaf and hard-of-hearing users need captions for audio content and visual alternatives to audio cues. They benefit from transcripts, visual indicators for important information, and the ability to control media playback. Auto-playing audio is particularly problematic as it can interfere with assistive technology output.

Users with photosensitive epilepsy need interfaces that avoid flashing content. WCAG requires that content does not flash more than three times per second, as rapid flashing can trigger seizures.

## Success Metrics for Accessibility

Measuring accessibility success requires both quantitative automated metrics and qualitative user experience validation. WCAG 2.1 AA conformance level serves as the baseline compliance metric. Automated accessibility testing tools can report conformance percentages, but manual testing is required to verify full compliance.

Automated accessibility test pass rate measures the percentage of automated checks that pass across the application. This metric should trend upward over time and should not regress below a threshold (typically 95% or higher). Automated tests catch approximately 30-40% of accessibility issues, so this metric alone is insufficient but provides valuable regression detection.

Keyboard navigation completeness measures the percentage of interactive features that are fully functional using only keyboard input. This should be 100%—every button, link, form control, and custom component must be keyboard accessible. Testing involves manually navigating the entire application using only keyboard input.

Screen reader test pass rate measures the percentage of user flows that are successfully completable using screen reader software. This requires manual testing with actual screen readers and should cover critical user journeys. Screen reader testing validates that semantic HTML and ARIA are correctly implemented.

Accessibility-related support tickets track user-reported accessibility barriers. A decreasing trend indicates improving accessibility, while an increasing trend may indicate new accessibility regressions or insufficient testing coverage. These tickets provide valuable real-world feedback from users with disabilities.

Time to fix accessibility issues measures how quickly accessibility bugs are resolved. This metric encourages treating accessibility issues with the same priority as other functional bugs. Accessibility issues should not be deprioritized or deferred.

Accessibility audit scores from tools like Lighthouse provide a quick health check, though they should not be the sole metric. Lighthouse accessibility scores range from 0-100, with 100 representing full automated compliance. Scores should be maintained above 90, with 100 as the target.

User testing with assistive technology users provides the most valuable qualitative feedback. Regular sessions with users who rely on screen readers, keyboard navigation, or other assistive technologies reveal issues that automated tools and developer testing miss. These sessions should be scheduled quarterly or for major feature releases.
