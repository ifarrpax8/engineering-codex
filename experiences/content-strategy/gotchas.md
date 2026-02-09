# Gotchas: Content Strategy

## Contents

- [Developer-Written Error Messages](#developer-written-error-messages)
- [Placeholder Text as Labels](#placeholder-text-as-labels)
- [Inconsistent Terminology](#inconsistent-terminology)
- [Concatenated Strings Breaking Translations](#concatenated-strings-breaking-translations)
- [Truncated Text with No Tooltip](#truncated-text-with-no-tooltip)
- [Empty States That Are Just Blank](#empty-states-that-are-just-blank)
- [Success Messages That Don't Confirm What Happened](#success-messages-that-dont-confirm-what-happened)
- [Toast Messages That Disappear Too Fast](#toast-messages-that-disappear-too-fast)
- [Copy That Doesn't Match the User's Emotional State](#copy-that-doesnt-match-the-users-emotional-state)
- [Markdown Rendering Without Sanitization](#markdown-rendering-without-sanitization)
- ["Click Here" Link Text](#click-here-link-text)

## Developer-Written Error Messages

**The Problem:**
Developers write error messages using technical jargon that means nothing to users.

**Example:**
```java
// ❌ Bad
catch (NullPointerException e) {
    return ResponseEntity.status(500)
        .body("NullPointerException in UserService at line 42");
}
```

**Why It's Bad:**
- Users don't know what "NullPointerException" means
- Internal implementation details exposed
- No actionable next steps
- Creates support burden

**The Fix:**
```java
// ✅ Good
catch (NullPointerException e) {
    logger.error("NullPointerException in UserService", e);
    String message = messageSource.getMessage(
        "user.profile.error.load",
        null,
        locale
    );
    return ResponseEntity.status(500)
        .body(new ErrorResponse(message));
}
```

```properties
# messages_en.properties
user.profile.error.load=Unable to load your profile. Please refresh the page or contact support if this continues.
```

**Prevention:**
- All user-facing error messages must be written or reviewed by UX writers
- Use i18n message files, never hardcode technical errors
- Log technical details server-side, show user-friendly messages client-side

## Placeholder Text as Labels

**The Problem:**
Using placeholder text as the field label. Placeholders disappear on focus, leaving users confused.

**Example:**
```vue
<!-- ❌ Bad -->
<input type="text" placeholder="Enter invoice name" />
<!-- No label - user forgets what field is when placeholder disappears -->
```

**Why It's Bad:**
- Placeholders disappear when user types
- Users forget what the field is for
- Screen readers may not read placeholders consistently
- Placeholders have lower contrast (accessibility issue)

**The Fix:**
```vue
<!-- ✅ Good -->
<label>Invoice Name</label>
<input type="text" placeholder="e.g., Q4-2024-Report" />
<!-- Label always visible, placeholder provides example -->
```

**Prevention:**
- Always use `<label>` elements for form fields
- Use placeholders for examples, not labels
- Test with screen readers to verify labels are announced

## Inconsistent Terminology

**The Problem:**
The same concept called different things throughout the app, creating confusion.

**Example:**
- Navigation says "Projects"
- Settings says "Workspaces"
- Billing says "Organizations"
- All refer to the same thing!

**Why It's Bad:**
- Users think these are different features
- Search doesn't work ("Where's my workspace?" but it's called "project")
- Training and documentation become confusing
- Erodes user confidence

**The Fix:**
1. Create a terminology glossary
2. Pick one term and use it everywhere
3. Enforce through linting

```javascript
// Terminology glossary
const glossary = {
  'project': ['workspace', 'organization', 'space'], // forbidden alternatives
  'invoice': ['bill', 'statement'], // forbidden alternatives
};

// ESLint rule
'content-lint/terminology': ['error', { glossary }]
```

**Prevention:**
- Establish terminology glossary early
- Review all copy for consistency
- Use linting to catch inconsistencies
- Update glossary as product evolves

## Concatenated Strings Breaking Translations

**The Problem:**
Concatenating strings breaks translation because different languages have different word order.

**Example:**
```typescript
// ❌ Bad - breaks translation
const message = `You have ${count} items`;
// English: "You have 5 items"
// Spanish: "Tienes 5 artículos" (different word order)
```

**Why It's Bad:**
- Translation tools can't handle concatenated strings
- Word order differs across languages
- Pluralization rules differ (English: 1 item vs 2 items, some languages have more forms)
- Can't reorder words for proper grammar

**The Fix:**
```typescript
// ✅ Good - translation-friendly
const message = $t('invoice.list.count', { count });

// locales/en.json
{
  "invoice.list.count": "You have {count} invoice | You have {count} invoices"
}

// locales/es.json
{
  "invoice.list.count": "Tienes {count} factura | Tienes {count} facturas"
}
```

**Prevention:**
- Never concatenate user-facing strings
- Always use i18n interpolation
- Test with pseudo-localization to catch concatenation
- Use ESLint to detect string concatenation

## Truncated Text with No Tooltip

**The Problem:**
Long text gets truncated with ellipsis, but users can't see the full content.

**Example:**
```vue
<!-- ❌ Bad -->
<div class="invoice-name">
  {{ invoice.name }} <!-- Truncated to "Very Long Invoice Name Tha..." -->
</div>
<!-- User can't see full name -->
```

**Why It's Bad:**
- Users can't read important information
- Creates confusion ("Which invoice is this?")
- No way to access full content
- Poor user experience

**The Fix:**
```vue
<!-- ✅ Good -->
<div 
  class="invoice-name"
  :title="invoice.name"
>
  {{ truncate(invoice.name, 50) }}
</div>
<!-- Tooltip shows full name on hover -->

<!-- Or better: -->
<div class="invoice-name">
  <span class="truncated">{{ truncate(invoice.name, 50) }}</span>
  <Tooltip>{{ invoice.name }}</Tooltip>
</div>
```

**Prevention:**
- Always provide tooltip for truncated text
- Test with long content to verify tooltips work
- Consider expanding on click for important content
- Use CSS `text-overflow: ellipsis` with `title` attribute

## Empty States That Are Just Blank

**The Problem:**
Empty lists/tables show nothing — just blank space with no explanation or guidance.

**Example:**
```vue
<!-- ❌ Bad -->
<div v-if="invoices.length === 0">
  <!-- Nothing here - just blank space -->
</div>
```

**Why It's Bad:**
- Users don't know if it's loading or empty
- No guidance on what to do next
- Missed opportunity to onboard users
- Looks broken or incomplete

**The Fix:**
```vue
<!-- ✅ Good -->
<div v-if="invoices.length === 0" class="empty-state">
  <Icon name="invoice" size="large" />
  <h3>{{ $t('invoice.list.empty.title') }}</h3>
  <p>{{ $t('invoice.list.empty.description') }}</p>
  <button>{{ $t('invoice.list.empty.cta') }}</button>
</div>
```

```json
{
  "invoice.list.empty.title": "No invoices yet",
  "invoice.list.empty.description": "Create your first invoice to start tracking payments and managing billing.",
  "invoice.list.empty.cta": "Create Invoice"
}
```

**Prevention:**
- Every empty state must have copy and CTA
- Design empty states as part of the design system
- Test all empty states during QA
- Include empty states in content audit

## Success Messages That Don't Confirm What Happened

**The Problem:**
Generic success messages don't tell users what actually succeeded.

**Example:**
```typescript
// ❌ Bad
showToast("Success!");
// User: "Success at what? Did my invoice save? Did it send?"
```

**Why It's Bad:**
- Users don't know what happened
- Creates uncertainty ("Did it work?")
- Can't verify the action completed
- Poor user experience

**The Fix:**
```typescript
// ✅ Good
showToast($t('invoice.create.success', { id: invoice.id }));
// "Invoice #1234 created successfully"
```

```json
{
  "invoice.create.success": "Invoice #{id} created successfully",
  "invoice.delete.success": "{count} invoices deleted",
  "invoice.send.success": "Invoice #{id} sent to {email}"
}
```

**Prevention:**
- Always be specific in success messages
- Include relevant details (ID, count, recipient)
- Match message to the action taken
- Test success messages during QA

## Toast Messages That Disappear Too Fast

**The Problem:**
Toast notifications disappear before users can read them.

**Example:**
```typescript
// ❌ Bad
showToast("Invoice created successfully", { duration: 2000 });
// Disappears too fast for users to read, especially if they're not looking
```

**Why It's Bad:**
- Users miss important confirmations
- Can't verify action completed
- Creates uncertainty
- Poor accessibility (screen reader users need time)

**The Fix:**
```typescript
// ✅ Good
showToast("Invoice #1234 created successfully", { 
  duration: 5000, // Longer duration
  action: "View", // Action button to see details
  persistent: true // Don't auto-dismiss if user is interacting
});
```

**Best Practices:**
- Minimum 5 seconds for important messages
- Longer for complex messages
- Provide action button to see details
- Don't auto-dismiss if user is interacting
- Consider persistent notifications for critical actions

## Copy That Doesn't Match the User's Emotional State

**The Problem:**
Copy tone doesn't match the user's emotional state, feeling dismissive or inappropriate.

**Example:**
```typescript
// ❌ Bad - cheerful error message
showError("Oops! Something went wrong! 😊");
// User just lost their work - not a time for cheerfulness
```

**Why It's Bad:**
- Feels dismissive of user's frustration
- Inappropriate tone for the situation
- Erodes trust ("Do they understand how serious this is?")
- Poor user experience

**The Fix:**
```typescript
// ✅ Good - acknowledges frustration
showError("We understand this is frustrating. Your invoice couldn't be saved. We've saved a draft - you can try again from the Drafts section.");
// Acknowledges emotion, explains problem, provides recovery path
```

**Guidelines:**
- **Errors**: Acknowledge frustration, be empathetic, provide recovery
- **Success**: Celebrate appropriately, confirm what happened
- **Warnings**: Be clear but not alarming
- **Information**: Be helpful and concise

**Prevention:**
- Review copy for emotional appropriateness
- Test with users in context
- Consider user's emotional state when writing
- Match tone to severity

## Markdown Rendering Without Sanitization

**The Problem:**
Rendering user-generated Markdown or HTML without sanitization creates XSS vulnerabilities.

**Example:**
```vue
<!-- ❌ Bad - XSS vulnerability -->
<template>
  <div v-html="userContent" />
  <!-- If userContent contains <script>alert('XSS')</script>, it executes! -->
</template>
```

**Why It's Bad:**
- XSS attacks can steal user data
- Malicious scripts can execute
- Security vulnerability
- Can compromise user accounts

**The Fix:**
```vue
<!-- ✅ Good - sanitized -->
<template>
  <div v-html="sanitizedContent" />
</template>

<script setup>
import DOMPurify from 'dompurify';

const props = defineProps<{ content: string }>();

const sanitizedContent = computed(() => {
  return DOMPurify.sanitize(marked(props.content));
});
</script>
```

**Prevention:**
- Always sanitize user-generated content
- Use libraries like DOMPurify
- Test with XSS payloads
- Review security practices regularly
- Never trust user input

## "Click Here" Link Text

**The Problem:**
Using "click here" or "read more" as link text is meaningless out of context.

**Example:**
```vue
<!-- ❌ Bad -->
<p>To learn more about invoices, <a href="/help">click here</a>.</p>
<!-- Screen reader: "click here" - no context -->
```

**Why It's Bad:**
- Screen reader users can't understand link purpose
- Users scanning page can't tell what link does
- Bad for accessibility
- Poor SEO

**The Fix:**
```vue
<!-- ✅ Good -->
<p>To learn more, read our <a href="/help">invoice creation guide</a>.</p>
<!-- Screen reader: "invoice creation guide" - clear purpose -->
```

**Best Practices:**
- Link text should describe destination
- Can be part of sentence: "Read our [invoice guide]"
- Or standalone: "[Invoice Creation Guide]"
- Never use "click here", "read more", "here"

**Prevention:**
- Review all links for meaningful text
- Test with screen readers
- Use ESLint to catch "click here"
- Include in accessibility audit
