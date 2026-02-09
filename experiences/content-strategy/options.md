# Options: Content Strategy

## Contents

- [Content Management](#content-management)
- [Content Governance](#content-governance)
- [Empty State Patterns](#empty-state-patterns)
- [Error Message Framework](#error-message-framework)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Content Management

### i18n Message Catalogs (Recommended Default)

**Description:**
Externalize all user-facing strings to message files managed by i18n libraries (vue-i18n, react-intl, Spring MessageSource). Content is versioned with code and goes through standard code review.

**Implementation:**

**Vue 3:**
```vue
<template>
  <button>{{ $t('invoice.create.submit') }}</button>
</template>
```

```json
// locales/en.json
{
  "invoice": {
    "create": {
      "submit": "Create Invoice"
    }
  }
}
```

**React:**
```tsx
import { FormattedMessage } from 'react-intl';

<FormattedMessage id="invoice.create.submit" />
```

**Spring Boot:**
```java
String message = messageSource.getMessage(
    "invoice.create.submit",
    null,
    locale
);
```

**Strengths:**
- Full internationalization support
- Centralized content management
- Enables content review workflow
- Type-safe with TypeScript
- Supports A/B testing
- Versioned with application code
- No external dependencies

**Weaknesses:**
- Content changes require code deployment
- Slower iteration for content updates
- Requires developer involvement for copy changes
- May need to coordinate across multiple repos (monorepo)

**Best For:**
- UI labels, buttons, error messages
- Content that changes infrequently
- Content that needs code review
- Applications requiring full i18n support
- Teams with established content review process

**Avoid When:**
- Marketing content that changes frequently
- Content managed by non-technical team members
- Need for real-time content updates without deployment
- Very large content catalogs (consider CMS)

### Headless CMS (For Marketing/Dynamic Content)

**Description:**
Store frequently updated content (help pages, marketing copy, feature announcements) in a headless CMS. Content can be updated without code deployment.

**Implementation:**
```typescript
// Fetch content from CMS
const helpContent = await cms.getContent('invoice-help', locale);

// Render in component
<div v-html="sanitizedContent" />
```

**Strengths:**
- Non-technical team members can update content
- No deployment needed for content changes
- Supports content review/approval workflows
- Can A/B test content independently
- Good for large content volumes
- Supports rich media content

**Weaknesses:**
- Additional infrastructure cost
- Requires CMS integration
- May need caching strategy
- Slower than hardcoded content (API calls)
- Not suitable for all UI copy (too slow for labels)
- Requires content governance process

**Best For:**
- Marketing landing pages
- Help documentation
- Feature announcements
- Legal/terms content
- Blog posts or articles
- Content that changes frequently
- Content managed by marketing/content team

**Avoid When:**
- Small content volume
- All content is technical (labels, errors)
- Need for instant content loading
- Tight coupling between content and code logic
- Budget constraints

### Hardcoded Strings (Avoid)

**Description:**
Strings written directly in code without externalization.

**Implementation:**
```vue
<!-- ❌ Avoid -->
<button>Submit</button>
<p>Error: Unable to save</p>
```

**Strengths:**
- Simplest to implement
- No setup required
- Fastest to write initially

**Weaknesses:**
- No internationalization support
- Copy changes require code deployment
- Inconsistent terminology
- No content review process
- Can't A/B test copy
- Hard to maintain at scale

**Best For:**
- Prototypes only
- Internal tools with single language
- Proof of concept

**Avoid When:**
- Production applications
- Multi-language requirements
- Content needs review
- Team collaboration
- Long-term maintenance

## Content Governance

### Terminology Glossary

**Description:**
Maintain a centralized glossary of approved terms and forbidden alternatives. Enforce through linting and code review.

**Implementation:**
```json
{
  "glossary": {
    "project": {
      "approved": "project",
      "forbidden": ["workspace", "organization", "space"]
    },
    "invoice": {
      "approved": "invoice",
      "forbidden": ["bill", "statement"]
    }
  }
}
```

**ESLint Rule:**
```javascript
'content-lint/terminology': ['error', {
  glossary: require('./terminology-glossary.json')
}]
```

**Strengths:**
- Ensures consistency across product
- Catches mistakes early (linting)
- Onboards new team members
- Reduces support burden
- Improves search/discoverability

**Weaknesses:**
- Requires maintenance as product evolves
- May need exceptions for legacy content
- Can feel restrictive to writers

**Best For:**
- All production applications
- Teams with multiple writers
- Products with domain-specific terminology
- Long-term maintenance

**Avoid When:**
- Very early prototypes
- Single-person projects
- No content review process

### Content Style Guide

**Description:**
Documented guidelines for tone of voice, capitalization, formatting, and content patterns.

**Contents:**
- Tone of voice guidelines
- Capitalization rules (sentence case for UI, title case for headings)
- Formatting standards (dates, currency, numbers)
- Examples of good/bad copy
- Error message patterns
- Empty state patterns

**Strengths:**
- Ensures consistent tone
- Onboards new writers
- Reduces review cycles
- Improves content quality

**Weaknesses:**
- Requires maintenance
- May need updates as product evolves
- Can become outdated if not maintained

**Best For:**
- All production applications
- Teams with multiple writers
- Products requiring specific tone
- Brand consistency requirements

### Linting/Automation

**Description:**
Automated checks for terminology consistency, forbidden words, capitalization, and content patterns.

**Implementation:**
```javascript
// ESLint rules
'content-lint/forbidden-terms': ['error', {
  forbidden: ['click here', 'submit', 'oops']
}],
'content-lint/capitalization': ['error', {
  'button.*': 'sentence-case'
}],
'content-lint/terminology': ['error', { glossary }]
```

**Strengths:**
- Catches mistakes before code review
- Enforces standards automatically
- Reduces manual review burden
- Consistent across team

**Weaknesses:**
- Requires setup and maintenance
- May need exceptions for edge cases
- Can be noisy if not tuned properly

**Best For:**
- All production applications
- Teams with established standards
- CI/CD pipelines
- Large codebases

**Avoid When:**
- Very early prototypes
- Standards not yet established
- No CI/CD pipeline

## Empty State Patterns

### Action-Oriented (CTA)

**Description:**
Empty state that guides users to create their first item. Includes clear call to action.

**Example:**
```
No invoices yet
Create your first invoice to start tracking payments and managing billing.

[Create Invoice Button]
```

**Strengths:**
- Guides users to action
- Reduces friction
- Onboards new users
- Improves feature discovery

**Weaknesses:**
- May not be appropriate if user can't create items
- Requires user permission check

**Best For:**
- First-time empty states
- User-owned content (invoices, projects)
- Features where creation is primary action

**Avoid When:**
- User doesn't have permission to create
- Content is system-generated
- Empty state is temporary (loading)

### Informational (Explanation)

**Description:**
Empty state that explains why content is missing. Provides context without action.

**Example:**
```
No archived items
Archived invoices will appear here after 90 days of inactivity.
```

**Strengths:**
- Sets expectations
- Reduces confusion
- Explains system behavior
- No pressure on user

**Weaknesses:**
- Doesn't guide to action
- May leave users unsure what to do

**Best For:**
- System-generated content
- Time-based content (archived items)
- Content that appears conditionally
- When no user action is possible

**Avoid When:**
- User can take action to populate
- First-time experience (use action-oriented)

### Error Recovery (Retry/Alternative)

**Description:**
Empty state that appears when content fails to load. Offers retry or alternative actions.

**Example:**
```
Unable to load invoices
Check your internet connection and try again.

[Retry] [Create Invoice Offline]
```

**Strengths:**
- Enables recovery
- Provides alternatives
- Reduces frustration
- Improves resilience

**Weaknesses:**
- Requires error handling logic
- May need offline capabilities

**Best For:**
- Error scenarios
- Network failures
- Temporary failures
- When retry is possible

**Avoid When:**
- Permanent failures (use informational)
- User doesn't have permission (use informational)

## Error Message Framework

### Problem + Cause + Action Pattern

**Description:**
Structure error messages as: what happened, why it happened (when helpful), what to do next.

**Example:**
```
Payment failed because your card has expired.
Update your payment method and try again.
```

**Strengths:**
- Comprehensive information
- Enables self-service recovery
- Reduces support burden
- Builds user confidence

**Weaknesses:**
- Can be verbose
- May not always know "why"
- Requires careful writing

**Best For:**
- User-actionable errors
- Errors with clear recovery paths
- Important operations (payments, data loss)

**Avoid When:**
- Obvious errors (validation)
- Technical errors where "why" isn't helpful
- When cause is unknown

### RFC 7807 for API Errors

**Description:**
Standardized error response format for APIs. Includes type, title, status, detail, and instance.

**Implementation:**
```json
{
  "type": "https://example.com/errors/payment-failed",
  "title": "Payment Failed",
  "status": 402,
  "detail": "Your card has expired. Update your payment method and try again.",
  "instance": "/invoices/123/payment"
}
```

**Strengths:**
- Standardized format
- Machine-readable
- Includes context
- Supports i18n (detail can be localized)

**Weaknesses:**
- More verbose than simple messages
- Requires client-side formatting
- May be overkill for simple apps

**Best For:**
- API-first applications
- Microservices architectures
- Applications with multiple clients
- When error handling needs to be standardized

**Avoid When:**
- Simple applications
- Single client application
- When simplicity is priority

## Recommendation Guidance

**For Most B2B SaaS Applications:**

1. **Content Management**: Use **i18n message catalogs** as the default. This provides full i18n support, enables content review, and integrates with your development workflow.

2. **Content Governance**: Implement **terminology glossary + linting**. This ensures consistency and catches mistakes early.

3. **Empty States**: Use **action-oriented** for first-time empty, **informational** for system content, **error recovery** for failures.

4. **Error Messages**: Use **Problem + Cause + Action** pattern for user-actionable errors. Use **RFC 7807** if building APIs consumed by multiple clients.

**Evolution Path:**
- Start with i18n message catalogs
- Add terminology glossary as team grows
- Add linting as standards mature
- Consider CMS for marketing content as content volume grows
- Add A/B testing framework as you optimize conversion

## Synergies

**Internationalization:**
- Content strategy requires i18n infrastructure
- i18n enables content strategy at scale
- Shared message catalogs and locale management
- See: [Internationalization Facet](../../facets/internationalization/)

**Error Handling:**
- Error messages are core content type
- Error handling patterns inform content structure
- Content strategy improves error recovery
- See: [Error Handling Facet](../../facets/error-handling/)

**Accessibility:**
- Content must be accessible (labels, alt text, meaningful links)
- Accessibility requirements inform content patterns
- Content strategy improves accessibility
- See: [Accessibility Facet](../../facets/accessibility/)

**Design Systems:**
- Content patterns should be part of design system
- Design system components need content guidelines
- Shared terminology and tone
- See: [Design Systems Experience](../design-consistency-and-visual-identity/)

## Evolution Triggers

**When to Add CMS:**
- Marketing team needs to update content frequently
- Help documentation is large and changes often
- Content changes need approval workflows
- Non-technical team members manage content

**When to Add A/B Testing:**
- Optimizing conversion rates
- Testing different copy approaches
- Large user base for statistical significance
- Content changes have measurable impact

**When to Expand Terminology Glossary:**
- Team grows (more writers)
- Product expands (new domains)
- Inconsistencies discovered
- Support burden increases

**When to Add Advanced Linting:**
- Standards are established
- Team is large enough to benefit
- CI/CD pipeline in place
- Content mistakes are frequent

**When to Standardize Error Framework:**
- Multiple services/APIs
- Need for consistent error handling
- Building API consumed by multiple clients
- Error handling becomes complex
