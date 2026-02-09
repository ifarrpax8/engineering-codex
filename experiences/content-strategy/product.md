# Product Perspective: Content Strategy

## Contents

- [Why Words Matter](#why-words-matter)
- [Content Types](#content-types)
- [Tone of Voice](#tone-of-voice)
- [Empty States as Opportunities](#empty-states-as-opportunities)
- [Error Message Principles](#error-message-principles)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Why Words Matter

Microcopy is the UI. While designers craft visual interfaces, content strategists craft the words that guide users through every interaction. A well-placed button label can mean the difference between task completion and abandonment. Tooltips can transform confusion into clarity. Confirmation dialogs can prevent costly mistakes.

Consider the impact:
- **Button labels** shape user expectations: "Save Changes" vs "Submit" — one is clear, the other vague
- **Tooltips** provide context without cluttering the interface: "This will notify all team members" prevents accidental broadcasts
- **Confirmations** reduce errors: "Delete 'Q4 Report'? This cannot be undone." prevents accidental deletions better than "Are you sure?"
- **Error messages** determine recovery: "Payment failed. Check your card details and try again." enables action; "Error 402" does not

In B2B SaaS, where users are often under time pressure and managing complex workflows, every word must earn its place. Poor microcopy generates support tickets, increases training time, and erodes user confidence.

## Content Types

Content strategy encompasses every user-facing string in your application:

**Labels and Form Elements**
- Field labels: "Project Name", "Billing Address"
- Button labels: "Create Invoice", "Save Draft", "Cancel"
- Navigation items: "Dashboard", "Settings", "Reports"

**Placeholders and Help Text**
- Input placeholders: "e.g., invoice-2024-Q1"
- Inline help: "This will be visible to all team members"
- Field descriptions: "Enter your tax ID number (EIN) for US businesses"

**Error Messages**
- Validation errors: "Project name is required"
- API errors: "Unable to connect to payment processor. Please try again."
- System errors: "Something went wrong. We've been notified and will investigate."

**Success Messages**
- Confirmations: "Invoice created successfully"
- Status updates: "3 items deleted"
- Progress indicators: "Uploading... 75% complete"

**Empty States**
- First-time empty: "Create your first project to get started"
- No-results empty: "No invoices match your filters. Try adjusting your search."
- Error empty: "Unable to load invoices. Check your connection and try again."

**Confirmation Dialogs**
- Destructive actions: "Delete 'Q4 Report'? This cannot be undone."
- Irreversible changes: "Archive this project? You can restore it later from Settings."
- Batch operations: "Delete 5 selected invoices? This action cannot be undone."

**Tooltips**
- Icon explanations: "Export to CSV"
- Feature hints: "Use this to filter by date range"
- Status indicators: "Last synced 2 minutes ago"

**Onboarding Copy**
- Welcome messages: "Welcome to Finance Manager! Let's set up your first project."
- Step-by-step guidance: "Step 2 of 4: Configure your billing settings"
- Feature introductions: "This is your dashboard. Here's where you'll track all invoices."

**Notification Text**
- Toast messages: "Invoice #1234 has been paid"
- Email subject lines: "Action Required: Payment Failed for Invoice #1234"
- Push notifications: "New invoice requires your approval"

**Email Content**
- Transactional emails: Invoice receipts, password resets, account confirmations
- Marketing emails: Feature announcements, best practices, product updates
- System notifications: Maintenance windows, security alerts, policy updates

## Tone of Voice

Tone of voice is how your product "speaks" to users. In B2B SaaS, the tone should be:

**Professional but Human**
- Use "you" and "your" — it's conversational without being casual
- Avoid corporate jargon: "leverage" → "use", "utilize" → "use"
- Write like you're helping a colleague, not a customer

**Concise**
- Every word must earn its place: "Please" is usually unnecessary on buttons
- Cut filler: "in order to" → "to", "at this point in time" → "now"
- Front-load important information: "Payment failed" not "We're sorry, but your payment has failed"

**Consistent**
- Use the same term throughout: if it's "workspace" in navigation, it's "workspace" everywhere
- Maintain consistent capitalization: sentence case for UI elements, title case for page headings
- Keep formatting consistent: dates, numbers, currency all follow the same pattern

**Match the User's Emotional State**
- Don't be cheerful in an error message: "Oops! Something went wrong!" feels dismissive
- Don't be formal in a success message: "Your request has been successfully processed" is robotic
- Acknowledge frustration: "We understand this is frustrating. Here's what happened and how to fix it."

**Avoid Jargon**
- Technical terms only when necessary, and always with explanation
- Industry terms are fine if your users are domain experts
- Never assume users know your internal terminology

## Empty States as Opportunities

Empty states are moments of opportunity, not just blank space. Every empty list, table, or dashboard should guide users toward action or understanding.

**First-Time Empty States**
When a user first encounters a feature with no data, guide them to create their first item:
- "No projects yet. Create your first project to get started." [Create Project button]
- Include a brief explanation: "Projects help you organize invoices and track billing by client or department."

**No-Results Empty States**
When filters or searches return nothing, suggest alternatives:
- "No invoices match 'Q4 2024'. Try removing filters or search for a different term."
- Show related actions: "Create a new invoice" or "View all invoices"

**Error Empty States**
When data fails to load, explain and offer recovery:
- "Unable to load invoices. Check your internet connection and try again." [Retry button]
- Provide alternative actions: "You can also create a new invoice offline."

**Informational Empty States**
Sometimes empty is expected — explain why:
- "No archived items. Archived invoices will appear here after 90 days."
- "No notifications. You're all caught up!"

## Error Message Principles

Good error messages follow a simple pattern: **what happened, why it happened, what to do next** — all in plain language.

**What Happened**
- State the problem clearly: "Payment failed" not "Error 402"
- Use user-facing language: "Unable to save invoice" not "Database constraint violation"

**Why It Happened** (when helpful)
- Provide context: "Payment failed because your card has expired"
- Don't blame the user: "Invalid email format" not "You entered an invalid email"
- Sometimes "why" isn't helpful — skip it if it's obvious or technical

**What to Do Next**
- Always provide an action: "Check your card details and try again" or "Contact support if this persists"
- Make actions specific: "Enter a valid email address" not "Fix the error"
- If recovery isn't possible, explain: "This invoice has already been paid and cannot be modified"

**Examples:**
- ❌ "Error: NullPointerException in UserService"
- ✅ "Unable to load your profile. Please refresh the page or contact support if this continues."

- ❌ "Invalid input"
- ✅ "Project name is required. Please enter a name and try again."

- ❌ "Failed"
- ✅ "Unable to delete invoice. This invoice is currently being processed. Please try again in a few minutes."

## Personas

**End User Reading Microcopy**
- **Goals**: Complete tasks quickly, understand what actions do, recover from errors
- **Pain Points**: Unclear button labels, cryptic error messages, missing help text
- **Needs**: Concise, actionable copy that matches their mental model

**Content Writer / UX Writer Crafting Copy**
- **Goals**: Create consistent, helpful copy that reduces support burden
- **Pain Points**: No style guide, inconsistent terminology, copy reviewed by non-writers
- **Needs**: Terminology glossary, content style guide, review process, i18n tools

**Developer Implementing Copy**
- **Goals**: Implement copy efficiently, maintain consistency, support i18n
- **Pain Points**: Hardcoded strings, missing translations, copy changes require code deploys
- **Needs**: i18n message catalogs, clear key naming, easy content updates

**Translator Localizing Content**
- **Goals**: Translate accurately while maintaining tone and context
- **Pain Points**: Concatenated strings, missing context, untranslatable idioms
- **Needs**: Full context, non-concatenated strings, pluralization support, terminology glossary

## Success Metrics

Content strategy success can be measured through:

**Task Completion Rate**
- Good copy helps users complete tasks: clear labels → fewer clicks, helpful errors → faster recovery
- Measure: % of users who complete key flows (onboarding, invoice creation, etc.)
- Target: Increase completion rate by reducing confusion and errors

**Support Ticket Volume**
- Bad copy generates support tickets: unclear errors → "What does this mean?", missing help → "How do I...?"
- Measure: Tickets related to UI confusion, error recovery, feature discovery
- Target: Reduce support burden through self-service clarity

**Error Recovery Rate**
- Actionable error messages enable self-service recovery
- Measure: % of users who successfully recover from errors without support
- Target: Increase recovery rate through better error messaging

**Time-on-Page for Help Content**
- If users spend too long on help pages, the UI copy isn't clear enough
- Measure: Average time on help/documentation pages
- Target: Reduce help-seeking behavior through better inline copy

**User Satisfaction (NPS/CSAT)**
- Content quality affects overall product satisfaction
- Measure: NPS scores, CSAT for specific features
- Target: Improve satisfaction through clearer, more helpful copy

## Common Product Mistakes

**Developer-Written Error Messages**
- Technical jargon shown to users: "NullPointerException in UserService"
- Internal error codes exposed: "Error 500" means nothing to users
- **Fix**: All user-facing errors must be written or reviewed by content writers

**Inconsistent Terminology**
- Same concept called different things: "project" in nav, "workspace" in settings, "organization" in billing
- **Fix**: Create a terminology glossary and enforce it through linting

**Placeholder Text Shipped to Production**
- "Lorem ipsum" or "Enter text here" makes it to production
- Placeholders used as labels (they disappear on focus)
- **Fix**: Content review checklist, automated linting for placeholder text

**Missing Empty States**
- Blank lists/tables with no explanation or call to action
- **Fix**: Every empty state should have copy and a CTA

**Unhelpful Success Messages**
- "Success!" — success at what?
- "Changes saved" — which changes?
- **Fix**: Be specific: "Invoice #1234 created successfully"

**Copy That Doesn't Match Emotional State**
- Cheerful error messages: "Oops! Something went wrong! 😊"
- Formal success messages: "Your request has been successfully processed"
- **Fix**: Match tone to context: acknowledge frustration in errors, celebrate in successes
