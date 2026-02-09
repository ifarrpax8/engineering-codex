# Options: Internationalization

## Contents

- [Frontend i18n Library Options](#frontend-i18n-library-options)
- [Translation Management Options](#translation-management-options)
- [Backend Localization Options](#backend-localization-options)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Frontend i18n Library Options

### vue-i18n (Vue) / react-intl (React)

**Description:** Framework-specific i18n libraries that integrate deeply with their respective frameworks. vue-i18n is the official i18n solution for Vue 3, providing seamless template integration and Composition API support. react-intl is part of the FormatJS suite and is the most popular i18n solution for React, offering comprehensive ICU message format support and excellent TypeScript integration.

**Strengths:** Deep framework integration enables reactive updates when locales change without page reloads. Template syntax is natural and readable (`$t('key')` in Vue, `<FormattedMessage>` in React). Excellent TypeScript support with type-safe message keys and interpolation. Strong ecosystem with extraction tools (vue-i18n-extract, FormatJS CLI) that automatically find translatable strings. ICU message format support handles complex pluralization and formatting. Lazy loading support reduces initial bundle size. Active maintenance and large community support.

**Weaknesses:** Framework-specific, so code cannot be shared between Vue and React applications. Learning curve for ICU message format syntax. Some setup required for optimal configuration (locale data, fallback behavior). Extraction tools require configuration and may miss some edge cases.

**Best For:** Applications built exclusively with Vue 3 or React. Teams that want framework-native solutions with excellent developer experience. Projects requiring complex pluralization and formatting. Applications with many languages where lazy loading is important.

**Avoid When:** Building applications that need to share i18n logic across multiple frameworks. Preferring framework-agnostic solutions for flexibility. Need for i18n logic outside of web applications (Node.js services, CLI tools).

### i18next

**Description:** Framework-agnostic i18n library with plugins for Vue, React, Angular, and vanilla JavaScript. Provides a consistent API across frameworks and extensive plugin ecosystem. Widely adopted with large community and comprehensive documentation.

**Strengths:** Framework-agnostic design allows sharing i18n logic across Vue, React, and other frameworks. Extensive plugin ecosystem for language detection, caching, backend loading, and more. Mature and stable with large community support. Flexible configuration supports various use cases. Good TypeScript support. Can be used outside of web applications (Node.js, CLI tools).

**Weaknesses:** Less deep framework integration than framework-specific solutions. Requires more configuration for optimal setup. API is more verbose than framework-specific solutions. Some plugins may have compatibility issues or maintenance concerns.

**Best For:** Applications using multiple frameworks or planning to migrate between frameworks. Teams that need i18n logic outside of web applications. Projects requiring extensive plugin functionality (language detection, caching, backend sync). Organizations standardizing on a single i18n solution across multiple projects.

**Avoid When:** Building single-framework applications where framework-specific solutions provide better developer experience. Preferring simpler, more integrated solutions. Teams that don't need framework-agnostic capabilities.

### Custom Solution

**Description:** Lightweight key-value lookup implementation without external dependencies. Typically involves simple JSON message catalogs and basic lookup functions. Minimal implementation that meets basic i18n needs without library overhead.

**Strengths:** No external dependencies, reducing bundle size and avoiding dependency management concerns. Full control over implementation and behavior. Simple for basic use cases with single language or minimal i18n needs. No learning curve for team members unfamiliar with i18n libraries.

**Weaknesses:** Must implement pluralization, interpolation, and formatting manually. No built-in support for complex features like ICU message format. Extraction and validation tools must be built or foregone. More code to maintain and potential for bugs. Missing features that libraries provide (lazy loading, locale detection, fallback chains). Reinventing functionality that libraries solve well.

**Best For:** Applications with minimal i18n needs (2-3 languages, simple messages). Projects where bundle size is extremely critical. Applications with very specific requirements that libraries don't meet. Learning exercises or prototypes.

**Avoid When:** Building production applications with multiple languages or complex i18n needs. Needing pluralization, formatting, or other advanced features. Wanting extraction tools and validation. Planning to scale i18n capabilities over time.

## Translation Management Options

### TMS Platform (Crowdin / Phrase / Lokalise)

**Description:** Managed translation workflow platforms that provide translator interfaces, context screenshots, glossary management, and CI/CD integration. These platforms handle the entire translation workflow from string extraction through translation, review, and integration back into codebases.

**Strengths:** Professional translator interfaces make translation work efficient and consistent. Context screenshots help translators understand where text appears, improving accuracy. Glossary management ensures terminology consistency across translations. CI/CD integration automates translation sync, reducing manual work. Version control for translations tracks changes over time. Collaboration features enable multiple translators and reviewers to work together. Quality assurance tools catch common errors automatically.

**Weaknesses:** Additional cost beyond translation services. Requires setup and configuration. Learning curve for team members using the platform. Dependency on external service for translation workflow. May be overkill for small projects with few languages.

**Best For:** Applications with multiple languages (5+) or frequent content updates. Teams with dedicated translators or translation agencies. Projects requiring terminology consistency and quality assurance. Organizations managing translations across multiple projects or teams.

**Avoid When:** Small projects with 1-2 languages and infrequent updates. Budget constraints that make TMS cost prohibitive. Projects where manual file management is sufficient. Teams without dedicated translation resources.

### Manual File Management

**Description:** Translation files (JSON, properties files) stored in git repository and edited directly by translators or developers. Simple workflow where translators edit files directly or through pull requests. No specialized translation platform required.

**Strengths:** No additional cost beyond translation services. Simple workflow that developers understand (git-based). Full control over translation files and workflow. No dependency on external services. Works well for small projects with few languages.

**Weaknesses:** No translator-friendly interface, making translation work less efficient. Difficult to provide context (screenshots, usage descriptions) to translators. No built-in quality assurance or consistency checking. Manual process for syncing translations back into codebase. Doesn't scale well to many languages or frequent updates. Risk of merge conflicts when multiple translators work simultaneously.

**Best For:** Small projects with 1-3 languages. Teams with technical translators comfortable editing JSON/properties files. Projects with infrequent content updates. Budget-constrained projects where TMS cost is prohibitive.

**Avoid When:** Applications with many languages (5+) or frequent updates. Teams requiring professional translator interfaces. Projects needing terminology consistency and quality assurance. Organizations managing translations across multiple projects.

### Machine Translation + Human Review

**Description:** Initial translations generated by machine translation services (GPT, DeepL, Google Translate), then reviewed by human translators for quality and accuracy. Hybrid approach balancing speed and cost with acceptable quality.

**Strengths:** Fast initial translation generation reduces time to first translation. Lower cost than fully human translation. Good quality for straightforward, non-technical content. Scalable to many languages quickly. Human review ensures quality for critical content.

**Weaknesses:** Machine translation quality varies, especially for technical terminology and context-dependent phrases. Requires human review, which adds time and cost. May produce inconsistent translations without careful review. Cultural nuances may be missed by machine translation. Not suitable for legal, marketing, or highly technical content without extensive review.

**Best For:** Applications with many languages where full human translation is cost-prohibitive. Non-critical content where good-enough quality is acceptable. Rapid prototyping or MVP phases. Technical content with consistent terminology that machine translation handles well.

**Avoid When:** Legal documents, marketing copy, or content where errors have serious consequences. Applications requiring high translation quality and cultural adaptation. Content with significant cultural context or nuance. Projects where human translation cost is acceptable.

## Backend Localization Options

### Spring MessageSource

**Description:** Spring Boot's built-in i18n solution using ResourceBundleMessageSource. Message files stored as properties files in classpath (messages.properties, messages_de.properties). Locale resolution through LocaleResolver implementations. Integrated with Spring's validation framework for localized error messages.

**Strengths:** Native Spring integration requires no additional dependencies. Familiar to Spring developers, reducing learning curve. Integrated with Spring validation for localized error messages. Simple property file format that translators can edit. Good performance with caching support. Well-documented and widely used in Spring ecosystem.

**Weaknesses:** Property file format is less flexible than JSON for complex structures. Pluralization support is less elegant than ICU message format. Requires deployment to update translations (no dynamic updates). File-based approach doesn't scale well to very large message catalogs. Less suitable for non-Spring applications.

**Best For:** Spring Boot applications where native integration is preferred. Teams familiar with Spring ecosystem. Applications with moderate translation needs. Projects where translation updates align with code deployments.

**Avoid When:** Need for dynamic translation updates without deployment. Very large message catalogs where file management becomes cumbersome. Non-Spring applications. Requirements for complex message structures that properties files don't support well.

### Database-Stored Translations

**Description:** Translations stored in database tables (separate translations table or JSONB columns). Dynamic loading allows translation updates without code deployment. Admin UI enables non-technical users to manage translations.

**Strengths:** Dynamic updates without deployment enable rapid translation iteration. Admin UI allows content writers and translators to update translations directly. Centralized storage simplifies translation management across services. Version history and audit trails possible through database features. Suitable for content management systems or applications with frequent content updates.

**Weaknesses:** Database queries add latency compared to in-memory message sources. Requires database schema design and migration management. Caching required for performance, adding complexity. Admin UI must be built and maintained. More complex than file-based approaches.

**Best For:** Applications requiring frequent translation updates without deployment. Content management systems or applications with user-generated content. Multi-tenant applications where translations vary by tenant. Projects with dedicated translation management teams.

**Avoid When:** Simple applications where file-based translations are sufficient. Projects where translation updates align with code deployments. Applications where database latency is a concern. Teams without resources to build and maintain admin UI.

### External i18n Service

**Description:** Centralized i18n service that provides translations via API. Microservices request translations from centralized service. Enables consistent translations across multiple services and centralized translation management.

**Strengths:** Centralized translation management across multiple services ensures consistency. Single source of truth for translations simplifies management. Service can provide advanced features (A/B testing, analytics, dynamic updates). Enables translation updates without deploying individual services.

**Weaknesses:** Additional service to build, deploy, and maintain. Network latency for translation requests (mitigated by caching). Service becomes critical dependency—outages affect all services. More complex architecture than embedded solutions. Overkill for single-service applications.

**Best For:** Microservices architectures where multiple services need translations. Organizations managing translations across many services or applications. Projects requiring advanced translation features (A/B testing, analytics). Applications where centralized translation management provides significant value.

**Avoid When:** Single-service applications where embedded solutions are simpler. Projects where network latency is a concern. Teams without resources to build and maintain translation service. Applications where translation updates align with code deployments.

## Evaluation Criteria

When evaluating i18n options, consider these criteria:

**Framework Alignment:** Does the solution integrate well with your chosen framework? Framework-specific solutions often provide better developer experience than framework-agnostic ones, but framework-agnostic solutions offer more flexibility.

**Team Expertise:** Does your team have experience with the solution? Learning curves vary, and familiar solutions reduce implementation time and errors. However, sometimes learning a better solution is worth the investment.

**Scale Requirements:** How many languages do you need to support? Solutions that work well for 2-3 languages may not scale to 10+ languages. Consider future growth when evaluating options.

**Update Frequency:** How often do translations change? Solutions optimized for frequent updates (database storage, TMS platforms) may be overkill for stable content, while file-based solutions may be cumbersome for frequently changing content.

**Budget Constraints:** What's the budget for i18n tooling and translation services? TMS platforms add cost, while manual file management has no tooling cost. Balance tooling benefits against budget limitations.

**Quality Requirements:** How critical is translation quality? Legal documents and marketing copy require high-quality human translation, while internal tools may accept machine translation with review.

**Performance Requirements:** How important is performance? Database-stored translations add latency, while in-memory message sources are faster. Caching can mitigate performance concerns but adds complexity.

## Recommendation Guidance

For most applications, we recommend:

**Frontend:** Use framework-specific solutions (vue-i18n for Vue, react-intl for React) unless you need framework-agnostic capabilities. These provide the best developer experience and deepest framework integration. Consider i18next if you need framework-agnostic capabilities or plan to use multiple frameworks.

**Translation Management:** Use TMS platforms (Crowdin, Phrase, Lokalise) for applications with 5+ languages or frequent updates. Use manual file management for small projects with 1-3 languages. Consider machine translation with human review for rapid expansion to many languages, but ensure human review for quality.

**Backend:** Use Spring MessageSource for Spring Boot applications unless you need dynamic updates without deployment. Consider database-stored translations if frequent updates without deployment are required. External i18n services are only necessary for microservices architectures with many services.

These recommendations balance developer experience, maintainability, and cost. Adjust based on specific project requirements, team expertise, and constraints.

## Synergies

Certain option combinations work particularly well together:

**vue-i18n + TMS Platform:** vue-i18n-extract integrates with TMS platforms for automated string extraction and sync. This combination provides excellent developer experience and efficient translation workflow.

**react-intl + FormatJS CLI + TMS:** FormatJS CLI extracts messages for react-intl, and many TMS platforms support FormatJS format directly. This creates a smooth workflow from code to translation and back.

**Spring MessageSource + Manual File Management:** Simple combination that works well for Spring applications with few languages. Property files are easy for translators to edit, and Spring integration is straightforward.

**Database-Stored Translations + TMS Platform:** TMS platforms can sync translations directly to databases, enabling dynamic updates without deployment. This combination provides the best of both worlds: professional translation workflow and dynamic updates.

**i18next + External i18n Service:** i18next's backend plugins can load translations from external services, making it a good fit for microservices architectures with centralized translation management.

## Evolution Triggers

Reevaluate i18n options when these conditions change:

**Language Count Growth:** Adding many languages (5+) may justify TMS platform investment. Solutions that work for 2-3 languages may not scale to 10+ languages.

**Update Frequency Increase:** If translations change frequently, consider database-stored translations or TMS platforms that support dynamic updates. File-based solutions become cumbersome with frequent updates.

**Framework Migration:** If migrating between frameworks, consider i18next for framework-agnostic capabilities. Framework-specific solutions require rewriting i18n code during framework migration.

**Microservices Architecture:** If moving to microservices, consider external i18n service for centralized translation management. Embedded solutions become difficult to manage across many services.

**Quality Requirements Increase:** If translation quality becomes more critical (e.g., entering regulated markets), invest in professional translation services and TMS platforms. Manual translation or machine translation may no longer be sufficient.

**Performance Issues:** If translation lookup becomes a performance bottleneck, consider caching strategies or moving to in-memory message sources. Database-stored translations may require optimization or alternative approaches.

**Team Growth:** As translation teams grow, TMS platforms become more valuable for collaboration and workflow management. Manual file management doesn't scale well with large teams.

Regularly reassess i18n options as projects evolve. What works initially may not scale as requirements change. Plan for evolution rather than locking into solutions that don't grow with your needs.
