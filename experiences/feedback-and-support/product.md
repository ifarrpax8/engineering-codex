# Product Perspective: Feedback & Support

## Contents

- [Why Feedback and Support Matter](#why-feedback-and-support-matter)
- [Feedback Taxonomy](#feedback-taxonomy)
- [Support Spectrum](#support-spectrum)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Why Feedback and Support Matter

Feedback and support systems are critical for B2B SaaS products. They serve three primary functions:

**User Retention**: When users encounter issues, quick resolution prevents churn. A study by Zendesk found that 50% of customers will switch to a competitor after one bad support experience. In B2B contexts, where switching costs are high, poor support experiences compound over time and lead to contract non-renewals.

**Product Improvement**: User feedback is the most direct source of product insights. Feature requests, bug reports, and satisfaction surveys inform product roadmaps more accurately than internal assumptions. Companies that close the feedback loop see 2-3x higher feature adoption rates.

**Trust Building**: Transparent support processes and responsive feedback handling build trust. When users see their feedback acknowledged and acted upon, they become advocates. In B2B, this translates to case studies, referrals, and expansion revenue.

## Feedback Taxonomy

Understanding different types of feedback helps design appropriate collection mechanisms:

### Bug Reports
Users reporting broken functionality, errors, or unexpected behavior. These require:
- Context capture (URL, browser, user actions leading to error)
- Screenshot/video capabilities
- Priority classification (blocking vs. minor)
- Routing to engineering teams

### Feature Requests
Users suggesting new functionality or improvements. These need:
- Categorization (UI/UX, API, integration, etc.)
- Voting/prioritization mechanisms
- Status tracking (under consideration, planned, shipped)
- Communication back to requesters

### Satisfaction Surveys
Structured feedback collection:
- **NPS (Net Promoter Score)**: "How likely are you to recommend us?" (0-10 scale)
- **CSAT (Customer Satisfaction)**: "How satisfied are you with [feature/support]?" (1-5 scale)
- **CES (Customer Effort Score)**: "How easy was it to [complete task]?" (1-7 scale)

Best practice: Trigger surveys contextually (after key actions) rather than blanket email campaigns.

### In-App Feedback (Contextual)
Feedback collected at the point of experience:
- "Was this helpful?" buttons on help articles
- Feedback prompts after completing workflows
- "Report an issue" links on error pages
- Quick thumbs up/down on new features

### Support Tickets
Formal requests for assistance:
- Technical support (integration issues, API problems)
- Account/billing questions
- Feature guidance and training requests
- Escalations from self-service channels

## Support Spectrum

Support channels exist on a spectrum from self-service to fully assisted:

### Self-Service
**Documentation**: Comprehensive, searchable docs with code examples, API references, and tutorials. Best for technical users and developers.

**FAQ**: Frequently asked questions addressing common issues. Should be searchable and categorized.

**Knowledge Base**: Structured help articles with rich content (images, videos, step-by-step guides). Often integrated with search and contextual help.

**Success Rate**: 60-80% of users prefer self-service when it's well-executed. Reduces support ticket volume by 30-50%.

### Assisted Support
**Chat**: Real-time or asynchronous chat support. Best for quick questions and guidance. Often powered by chatbots with human escalation.

**Email**: Traditional support channel. Good for complex issues requiring detailed explanations or attachments.

**Phone**: High-touch support for enterprise customers or critical issues. Often reserved for premium tiers.

**Response Time SLAs**: Set expectations (e.g., "We respond within 4 hours during business hours").

### Community Support
**Forums**: User-to-user support, moderated by community managers. Reduces support burden while building community.

**Slack/Discord**: Real-time community channels. Good for developer communities and power users.

**Success Rate**: Community support can handle 20-30% of support volume, with high user satisfaction.

## Personas

### Frustrated User Hitting a Bug
**Scenario**: User encounters an error while processing an invoice. The workflow is blocked.

**Needs**:
- One-click "Report Issue" button
- Automatic context capture (no manual description needed)
- Immediate acknowledgment with ticket number
- Status updates when bug is fixed

**Outcome**: Quick resolution prevents churn and builds trust.

### Power User Requesting a Feature
**Scenario**: Admin user wants bulk export functionality for reporting.

**Needs**:
- Easy feature request submission
- Ability to see request status and voting
- Notification when feature ships
- Recognition for contributing ideas

**Outcome**: Feature gets built, user becomes advocate.

### Admin Reporting Org-Wide Issue
**Scenario**: Organization-level configuration issue affecting all users.

**Needs**:
- Priority escalation path
- Dedicated support channel (not general queue)
- Regular status updates
- Post-resolution review

**Outcome**: Issue resolved quickly, relationship strengthened.

### New User Needing Guidance
**Scenario**: First-time user doesn't understand how to set up integrations.

**Needs**:
- Contextual help on relevant pages
- Step-by-step guides
- "Getting Started" resources
- Ability to ask questions without feeling stupid

**Outcome**: User successfully onboarded, reduces support burden.

## Success Metrics

### Time-to-Resolution
Average time from ticket creation to resolution. Target: <24 hours for standard issues, <4 hours for critical.

### First-Contact Resolution Rate
Percentage of issues resolved in the first interaction. Target: >70%. Indicates quality of self-service and support team knowledge.

### CSAT Score
Customer satisfaction rating after support interactions. Target: >4.5/5.0. Track trends over time.

### Support Ticket Volume Trends
Monitor ticket volume over time. Decreasing volume with stable/growing user base indicates effective self-service and product improvements.

### Self-Service Resolution Rate
Percentage of users who find answers without creating tickets. Target: >60%. Track via knowledge base analytics and search patterns.

### Feedback Response Rate
Percentage of users who engage with feedback prompts. Target: 5-10% for in-app prompts, 20-30% for contextual surveys.

## Common Product Mistakes

### No In-App Feedback Mechanism
**Problem**: Users must navigate to a separate support portal or email support. Friction reduces feedback volume by 70-80%.

**Solution**: Always-accessible feedback widget or button, ideally in the header or footer.

### Feedback Submitted But Never Acknowledged
**Problem**: Users submit feedback and hear nothing. Feels like a void, reduces trust.

**Solution**: Immediate confirmation message, ticket number, and expected response time. Follow up when resolved.

### Support Hidden Behind Too Many Clicks
**Problem**: Help/support requires 3+ clicks to access. Users give up.

**Solution**: Support accessible in 1 click from anywhere in the app. Consider persistent help button or keyboard shortcut.

### Generic FAQs Instead of Contextual Help
**Problem**: Users see generic help articles unrelated to their current task.

**Solution**: Show relevant help based on current page, user role, and recent actions.

### No "What's New" or Changelog
**Problem**: Users don't know about new features or improvements, leading to underutilization.

**Solution**: In-app changelog, "What's New" modal on login, and feature announcement emails.

### Survey Fatigue
**Problem**: Asking for feedback too frequently (every page, every session) annoys users.

**Solution**: Limit surveys to meaningful moments (after key workflows, quarterly NPS, post-support interactions).
