# Accessibility: Options

## Recommended Accessibility Approach

**Target Standard**: WCAG 2.1 Level AA conformance serves as the minimum standard for most applications. This level provides meaningful accessibility improvements while remaining achievable for most development teams and design constraints. WCAG 2.1 AA compliance ensures legal compliance with most accessibility regulations and provides a solid foundation for inclusive design.

**Foundation Strategy**: Build accessibility into the foundation using semantic HTML and design system components. Semantic HTML provides built-in accessibility features without additional code, and design system components (like Propulsion) are pre-built with accessibility in mind. This foundation-first approach ensures that accessibility is integrated rather than retrofitted, reducing cost and technical debt.

**Testing Strategy**: Implement a multi-layered testing approach combining automated testing (axe-core and linting), manual testing (keyboard navigation and screen reader testing), and periodic expert audits. Automated testing provides fast feedback and catches approximately 30-40% of issues. Manual testing catches issues requiring human judgment. Expert audits validate compliance and catch edge cases.

**Process Integration**: Integrate accessibility into the development workflow from the start, not as a separate phase or afterthought. Accessibility should be considered during design, implemented during development, and validated during testing. This requires training, tooling, and cultural commitment, but prevents the exponential cost of retrofitting.

## Accessibility Testing Strategy Decision Matrix

### Option 1: Automated Only (axe-core + Linting)

**Description**: Rely solely on automated accessibility testing tools: axe-core integrated into component and E2E tests, and ESLint plugins for accessibility linting. This approach provides fast, automated feedback during development without requiring manual testing or specialized expertise.

**Coverage**: Automated tools catch approximately 30-40% of accessibility issues. They excel at detecting technical violations like missing alt text, insufficient color contrast, missing form labels, invalid ARIA usage, and heading hierarchy problems. They cannot catch issues requiring human judgment like meaningful alt text, logical reading order, comprehensible link text, or overall usability.

**Strengths**: Fast feedback loop—issues are caught immediately during development. CI/CD integration prevents regressions automatically. No specialized training required—developers can run automated tests without accessibility expertise. Scalable across large codebases—automated tests run consistently without human time investment. Cost-effective for catching common technical violations.

**Weaknesses**: Misses majority of accessibility issues (60-70% remain undetected). Cannot validate keyboard navigation functionality—only checks for keyboard accessibility markers, not actual usability. Cannot validate screen reader experience—only checks ARIA attributes, not how screen readers actually announce content. May produce false positives or miss context-specific issues. Provides compliance checking but not usability validation.

**Best For**: Early-stage projects establishing baseline accessibility, teams with limited accessibility expertise, applications with simple interactions, or as a foundation layer in a comprehensive strategy. Suitable when combined with design system usage that provides built-in accessibility.

### Option 2: Automated + Manual Keyboard/Screen Reader Testing

**Description**: Combine automated testing with manual testing using keyboard navigation and screen reader software. Developers test interactive flows using only keyboard input and validate screen reader announcements. This approach requires developer training but provides significantly better coverage than automated testing alone.

**Coverage**: This combination catches approximately 70-80% of accessibility issues. Automated tools catch technical violations, while manual testing validates actual functionality: keyboard navigation works correctly, focus management is logical, screen readers announce content appropriately, and dynamic content updates are communicated.

**Strengths**: Validates actual user experience, not just technical compliance. Catches keyboard navigation issues that automated tools miss. Validates screen reader experience and ARIA implementation. Catches focus management problems in dynamic interfaces. Provides developers with hands-on understanding of accessibility barriers. Balances coverage with practical implementation.

**Weaknesses**: Requires developer training on keyboard navigation and screen reader usage. Time-intensive—manual testing takes significantly longer than automated testing. May miss edge cases or complex interaction patterns. Developer testing may not match real user experience. Requires maintaining testing expertise as team members change.

**Best For**: Most production applications requiring WCAG 2.1 AA compliance. Teams with committed developers willing to learn accessibility testing. Applications with complex interactions like modals, dropdowns, and dynamic content. This is the recommended minimum for most applications.

### Option 3: Full Accessibility Program (Automated + Manual + Expert Audit + User Testing)

**Description**: Comprehensive accessibility program combining all testing methods: automated testing, manual developer testing, periodic expert accessibility audits, and user testing with people who use assistive technologies. This approach provides the highest level of coverage and validation.

**Coverage**: This comprehensive approach catches 90%+ of accessibility issues. Automated tools catch technical violations, manual testing validates functionality, expert audits catch edge cases and compliance gaps, and user testing reveals real-world usability barriers that technical testing cannot detect.

**Strengths**: Highest coverage and confidence in accessibility. Expert audits provide specialized knowledge and catch issues developers miss. User testing reveals real-world barriers and usability issues. Validates both technical compliance and user experience. Provides documentation and certification for legal compliance. Establishes organization as accessibility leader.

**Weaknesses**: Highest cost in terms of time and resources. Requires ongoing investment in expert audits and user testing. May be overkill for simple applications or early-stage projects. Requires organizational commitment and budget allocation. Expert audits and user testing are typically quarterly or per-release, not continuous.

**Best For**: Enterprise applications with legal compliance requirements, applications serving large user bases including users with disabilities, applications requiring accessibility certifications, or organizations making accessibility a competitive differentiator. Essential for high-stakes applications where accessibility failures have significant legal or reputational risk.

## Component Library Strategy Decision Matrix

### Option 1: Design System Components (Propulsion)

**Description**: Use pre-built accessible components from the Propulsion design system. Components are built with accessibility in mind, tested for WCAG compliance, and provide consistent patterns across the application. Developers use components as provided, with minimal customization of accessibility features.

**Evaluation Criteria**: 
- **Accessibility**: Pre-built with WCAG 2.1 AA compliance, tested with screen readers and keyboard navigation
- **Consistency**: Ensures consistent accessibility patterns across the application
- **Maintenance**: Design system team maintains accessibility as standards evolve
- **Development Speed**: Fastest development—components ready to use
- **Customization**: Limited customization may require design system updates
- **Coverage**: May not cover all use cases, requiring custom components for edge cases

**Recommendation Guidance**: **Best practice for most use cases**. Start with design system components for all standard patterns: buttons, forms, navigation, modals, dropdowns, tables. Design system components provide accessibility by default and reduce development time. Only build custom components when design system doesn't provide needed functionality.

**Synergies**: Works excellently with automated testing (design system components are pre-validated), manual testing (consistent patterns are easier to test), and expert audits (fewer custom components to audit). Reduces training needs since components handle accessibility internally.

**Evolution Triggers**: Move to headless UI or custom components if design system doesn't support required functionality, if design requirements conflict with design system patterns, or if design system components have accessibility bugs that cannot be resolved quickly.

### Option 2: Headless UI Libraries (Headless UI, Radix, React Aria)

**Description**: Use headless UI libraries that provide accessible behavior and keyboard navigation without styling. Developers implement custom designs while libraries handle accessibility concerns: ARIA attributes, keyboard navigation, focus management, and screen reader support.

**Evaluation Criteria**:
- **Accessibility**: Built with accessibility in mind, but requires correct implementation
- **Flexibility**: Full design control while maintaining accessibility behavior
- **Maintenance**: Library maintains accessibility logic, developers maintain styling
- **Development Speed**: Moderate—requires styling implementation but accessibility is handled
- **Customization**: Full design customization possible while maintaining accessibility
- **Coverage**: Covers common patterns but may require custom implementation for unique cases

**Recommendation Guidance**: **Use when design system doesn't meet requirements**. Headless UI libraries are ideal when you need custom designs that don't match design system aesthetics, when design system components are missing required functionality, or when you need more flexibility than design system provides. Provides accessibility foundation with design freedom.

**Synergies**: Complements design system usage—use design system for standard patterns, headless UI for custom patterns. Works well with automated and manual testing since accessibility behavior is built-in. Requires developer understanding of accessibility to use correctly.

**Evolution Triggers**: Move to design system if components become available that meet requirements. Move to custom components only if headless UI libraries don't support required patterns or if you need complete control over accessibility implementation.

### Option 3: Custom Components

**Description**: Build components from scratch with full control over implementation, styling, and accessibility. Developers implement all accessibility features: semantic HTML, ARIA attributes, keyboard navigation, focus management, and screen reader support. Requires deep accessibility expertise.

**Evaluation Criteria**:
- **Accessibility**: Fully dependent on developer implementation—high risk if expertise is lacking
- **Flexibility**: Complete control over all aspects of implementation
- **Maintenance**: Full responsibility for maintaining accessibility as standards evolve
- **Development Speed**: Slowest—requires implementing all accessibility features
- **Customization**: Complete customization possible, including accessibility features
- **Coverage**: Can support any use case but requires significant implementation effort

**Recommendation Guidance**: **Last resort when other options don't meet requirements**. Only build custom components when design system and headless UI libraries cannot support required functionality, when you have specialized accessibility requirements not covered by libraries, or when you have dedicated accessibility expertise on the team. Custom components require extensive testing and maintenance.

**Synergies**: May be necessary for highly specialized use cases. Requires comprehensive testing strategy including automated, manual, and expert validation. Should follow ARIA Authoring Practices Guide patterns. Increases need for accessibility training and expertise.

**Evolution Triggers**: Prefer design system or headless UI if components become available. Custom components should be contributed back to design system if they solve common problems, benefiting the entire organization.

## Recommended Decision Path

**For New Projects**: Start with Propulsion design system components for all standard patterns. Implement automated testing (axe-core + linting) from day one. Train developers on keyboard navigation and basic screen reader testing. Schedule quarterly expert audits for compliance validation. This provides strong foundation with manageable investment.

**For Existing Projects**: Conduct accessibility audit to establish baseline. Prioritize fixing critical issues (keyboard navigation, screen reader barriers). Integrate automated testing to prevent regressions. Gradually migrate to design system components where possible. Train team on manual testing. Schedule expert audit to validate progress.

**For Enterprise/High-Stakes Applications**: Implement full accessibility program: automated testing, manual testing, quarterly expert audits, and user testing with assistive technology users. Use design system components primarily, headless UI for custom patterns, and custom components only when necessary. Maintain accessibility as competitive advantage and compliance requirement.

**For Simple Applications**: Automated testing + design system components may be sufficient if interactions are simple and design system covers all use cases. Add manual keyboard testing for critical flows. This provides good coverage with minimal investment for applications with straightforward requirements.
