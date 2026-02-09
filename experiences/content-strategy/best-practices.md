# Best Practices: Content Strategy

## Contents

- [Be Concise](#be-concise)
- [Be Specific](#be-specific)
- [Be Consistent](#be-consistent)
- [Write for Scanning](#write-for-scanning)
- [Error Messages](#error-messages)
- [Empty States](#empty-states)
- [Confirmation Dialogs](#confirmation-dialogs)
- [Help Text](#help-text)
- [Placeholder Text](#placeholder-text)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Accessibility](#accessibility)
- [Content Governance](#content-governance)

## Be Concise

Every word must earn its place. Users scan, they don't read. Cut unnecessary words.

**Cut Filler Words:**
- ❌ "Please click the Submit button"
- ✅ "Submit"

- ❌ "In order to create an invoice, you must first..."
- ✅ "To create an invoice, first..."

- ❌ "You can now proceed to the next step"
- ✅ "Continue"

**Cut Redundancy:**
- ❌ "Click here to delete"
- ✅ "Delete"

- ❌ "Enter your email address in the field below"
- ✅ "Email address"

**Front-Load Important Words:**
- ❌ "An error occurred while attempting to save your invoice"
- ✅ "Unable to save invoice"

Users read the first few words. Put the action or problem first.

## Be Specific

Vague copy creates confusion. Be specific about what will happen.

**Button Labels:**
- ❌ "Submit"
- ✅ "Create Invoice"

- ❌ "Delete"
- ✅ "Delete 3 Items"

- ❌ "Save"
- ✅ "Save Changes"

**Error Messages:**
- ❌ "Error occurred"
- ✅ "Unable to save invoice. Check your connection and try again."

- ❌ "Invalid input"
- ✅ "Invoice amount must be greater than 0"

**Success Messages:**
- ❌ "Success!"
- ✅ "Invoice #1234 created successfully"

- ❌ "Changes saved"
- ✅ "3 invoices updated"

## Be Consistent

Consistency builds user confidence. Inconsistent terminology creates confusion.

**Create a Terminology Glossary:**
```
Terminology Glossary:
- "Project" (not "workspace", "organization", or "space")
- "Invoice" (not "bill" or "statement")
- "Team Member" (not "user", "collaborator", or "member")
- "Archive" (not "delete", "remove", or "hide")
```

**Enforce Through Linting:**
```javascript
// ESLint rule
'content-lint/terminology': ['error', {
  glossary: {
    'project': ['workspace', 'organization', 'space'],
    'invoice': ['bill', 'statement']
  }
}]
```

**Consistent Capitalization:**
- **Sentence case** for UI elements: "Create invoice", "Save changes"
- **Title case** for page headings: "Invoice Management"
- **Lowercase** for placeholders: "e.g., invoice-2024-Q1"

**Consistent Formatting:**
- Dates: Always "MMM DD, YYYY" (e.g., "Jan 15, 2024")
- Currency: Always "$1,234.56" format
- Numbers: Always use commas for thousands

## Write for Scanning

Users don't read — they scan. Structure content for quick comprehension.

**Front-Load Important Information:**
- ❌ "We're sorry, but we were unable to process your payment at this time."
- ✅ "Payment failed. Check your card details and try again."

**Use Short Sentences:**
- ❌ "In order to create an invoice, you must first select a project, then enter the invoice details including the amount and due date, and finally click the Create button."
- ✅ "Select a project. Enter invoice details. Click Create."

**Use Bullet Points:**
- ❌ "To create an invoice, you need to select a project, enter the amount, set a due date, and add line items."
- ✅ "To create an invoice:
  - Select a project
  - Enter the amount
  - Set a due date
  - Add line items"

**Use Visual Hierarchy:**
- Headings for sections
- Bold for important terms
- Lists for steps or options

## Error Messages

Error messages should follow the pattern: **what happened, why it happened, what to do next** — all in plain language.

**Structure:**
1. **Problem**: State what went wrong
2. **Cause** (when helpful): Explain why
3. **Action**: Tell user what to do

**Examples:**

❌ "Error 500"
✅ "Unable to save invoice. Please try again."

❌ "Validation failed"
✅ "Invoice amount is required. Please enter an amount and try again."

❌ "NullPointerException in UserService"
✅ "Unable to load your profile. Please refresh the page or contact support if this continues."

**Don't Blame the User:**
- ❌ "You entered an invalid email"
- ✅ "Invalid email format. Please check and try again."

**Provide Recovery Paths:**
- Always include a "what to do next"
- If recovery isn't possible, explain why
- Offer alternatives when primary action fails

## Empty States

Every empty state is an opportunity. Never leave blank space — always guide users to action.

**First-Time Empty:**
- Explain what's missing
- Show how to create the first item
- Include a clear call to action

Example:
```
No invoices yet
Create your first invoice to start tracking payments and managing billing.

[Create Invoice Button]
```

**No-Results Empty:**
- Explain why nothing is shown
- Suggest alternatives (remove filters, try different search)
- Provide related actions

Example:
```
No invoices match "Q4 2024"
Try removing filters or search for a different term.

[Clear Filters] [View All Invoices]
```

**Error Empty:**
- Explain what went wrong
- Offer recovery (retry, check connection)
- Provide alternatives

Example:
```
Unable to load invoices
Check your internet connection and try again.

[Retry] [Create Invoice Offline]
```

## Confirmation Dialogs

Confirmation dialogs should describe the consequence, not just ask for confirmation.

**Describe the Consequence:**
- ❌ "Are you sure?"
- ✅ "Delete 'Q4 Report'? This cannot be undone."

- ❌ "Confirm deletion"
- ✅ "Delete 5 selected invoices? This action cannot be undone."

**Be Specific:**
- Name the item being affected
- Explain what will happen
- Warn about irreversibility when applicable

**Examples:**

**Destructive Action:**
```
Delete 'Q4 Report'?
This report will be permanently deleted and cannot be recovered.

[Cancel] [Delete Report]
```

**Batch Operation:**
```
Delete 5 selected invoices?
These invoices will be permanently deleted. This action cannot be undone.

[Cancel] [Delete 5 Invoices]
```

**Irreversible Change:**
```
Archive this project?
You can restore it later from Settings. Archived projects are hidden from your main view.

[Cancel] [Archive Project]
```

## Help Text

Show help text inline, near the field — not in a separate help page. Anticipate the question.

**Inline Help:**
- Show help text directly below or next to the field
- Use an info icon with tooltip for secondary help
- Keep help text concise (1-2 sentences)

**Example:**
```vue
<template>
  <div class="form-field">
    <label>Tax ID Number</label>
    <span class="help-text">
      Enter your EIN (Employer Identification Number) for US businesses.
      This is required for tax reporting.
    </span>
    <input type="text" />
  </div>
</template>
```

**Tooltip for Additional Context:**
```vue
<template>
  <label>
    Project Name
    <Icon name="info" :tooltip="$t('project.name.help')" />
  </label>
</template>
```

**When to Use Help Text:**
- Field purpose isn't obvious
- Format requirements (e.g., date format, phone number)
- Business rules (e.g., "Required for invoices over $10,000")
- Examples of valid input

**When to Skip Help Text:**
- Field purpose is obvious (e.g., "Email")
- Help text would be redundant with label
- Field is self-explanatory

## Placeholder Text

Use placeholders as examples, not as labels. The label should always be visible.

**Placeholders as Examples:**
- ✅ "e.g., invoice-2024-Q1"
- ✅ "MM/DD/YYYY"
- ✅ "john@example.com"

**Not as Labels:**
- ❌ "Enter invoice name" (this should be the label)
- ❌ "Your email" (label should say "Email")

**Why:**
- Placeholders disappear on focus
- Users forget what the field is
- Screen readers may not read placeholders consistently
- Placeholders have lower contrast (harder to read)

**Best Practice:**
```vue
<template>
  <div class="form-field">
    <!-- Label always visible -->
    <label>Invoice Number</label>
    
    <!-- Placeholder as example -->
    <input 
      type="text" 
      placeholder="e.g., INV-2024-001"
    />
  </div>
</template>
```

## Stack-Specific Guidance

### Vue 3 (vue-i18n)

**Always Use $t() for Strings:**
```vue
<template>
  <button>{{ $t('invoice.create.submit') }}</button>
  <p>{{ $t('invoice.create.error.save') }}</p>
</template>
```

**Named Interpolation:**
```vue
<template>
  <p>{{ $t('invoice.list.count', { count: invoiceCount }) }}</p>
</template>
```

```json
{
  "invoice.list.count": "You have {count} invoices"
}
```

**Pluralization:**
```vue
<template>
  <p>{{ $tc('invoice.list.count', invoiceCount) }}</p>
</template>
```

```json
{
  "invoice.list.count": "You have {count} invoice | You have {count} invoices"
}
```

**Linked Messages:**
```json
{
  "invoice": {
    "create": {
      "title": "Create Invoice",
      "submit": "@:invoice.create.title"
    }
  }
}
```

### React (react-intl)

**FormattedMessage Component:**
```tsx
import { FormattedMessage } from 'react-intl';

<FormattedMessage id="invoice.create.submit" />
```

**useIntl Hook:**
```tsx
import { useIntl } from 'react-intl';

function InvoiceForm() {
  const intl = useIntl();
  return (
    <button>{intl.formatMessage({ id: 'invoice.create.submit' })}</button>
  );
}
```

**Interpolation:**
```tsx
<FormattedMessage
  id="invoice.list.count"
  values={{ count: invoiceCount }}
/>
```

**Pluralization:**
```tsx
<FormattedMessage
  id="invoice.list.count"
  values={{ count: invoiceCount }}
/>
```

```json
{
  "invoice.list.count": "{count, plural, =0 {No invoices} one {# invoice} other {# invoices}}"
}
```

### Spring Boot (MessageSource)

**Server-Side Error Messages:**
```java
@RestController
public class InvoiceController {
    @Autowired
    private MessageSource messageSource;
    
    @PostMapping("/invoices")
    public ResponseEntity<?> createInvoice(
            @RequestBody InvoiceRequest request,
            Locale locale) {
        try {
            // ... create invoice
        } catch (ValidationException e) {
            String message = messageSource.getMessage(
                "invoice.validation.amount.required",
                null,
                locale
            );
            return ResponseEntity.badRequest()
                .body(new ErrorResponse(message));
        }
    }
}
```

**Message Files:**
```properties
# messages_en.properties
invoice.validation.amount.required=Invoice amount is required. Please enter a valid amount.
invoice.create.success=Invoice {0} created successfully.
```

**Locale Resolution:**
```java
@Configuration
public class LocaleConfig {
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.ENGLISH);
        return resolver;
    }
}
```

## Accessibility

Content must be accessible to all users, including those using assistive technologies.

**Don't Rely on Color Alone:**
- ❌ Red text for errors (colorblind users can't tell)
- ✅ Red text + icon + "Error:" prefix

**Meaningful Link Text:**
- ❌ "Click here"
- ✅ "Read the invoice creation guide"

**Alt Text for Images:**
- Decorative images: `alt=""` and `aria-hidden="true"`
- Informative images: Descriptive alt text

**Label Text for Form Fields:**
- Always use `<label>` elements
- Or `aria-label` for icon-only inputs
- Never rely on placeholder as label

**Screen Reader Support:**
- Use semantic HTML (`<button>`, `<nav>`, `<main>`)
- Provide `aria-label` for icon-only buttons
- Use `aria-describedby` to link help text to fields

**Example:**
```vue
<template>
  <button aria-label="Delete invoice">
    <Icon name="trash" />
  </button>
  
  <input 
    id="invoice-name"
    aria-describedby="invoice-name-help"
  />
  <span id="invoice-name-help" class="help-text">
    Enter a unique name for this invoice
  </span>
</template>
```

## Content Governance

Establish clear ownership and processes for content.

**Who Owns the Copy?**
- **UX Writer / Content Strategist**: Writes and maintains all user-facing copy
- **Developer**: Implements copy in code, ensures i18n compliance
- **Product Manager**: Reviews copy for business alignment
- **Designer**: Ensures copy fits visual design

**Review Process:**
1. UX Writer creates/updates copy
2. Copy reviewed by Product Manager
3. Developer implements in message files
4. Code review includes content review
5. QA verifies copy matches spec

**Content Style Guide:**
- Maintain a style guide document
- Include tone of voice guidelines
- Document terminology glossary
- Provide examples of good/bad copy
- Update style guide as patterns emerge

**Content Audit:**
- Regular audits for consistency
- Check for outdated copy
- Verify all copy uses i18n
- Review error messages for helpfulness
- Test empty states for completeness

**Tools:**
- Terminology glossary (enforced via linting)
- Content style guide (living document)
- i18n message catalogs (source of truth)
- Content review checklist (QA process)
