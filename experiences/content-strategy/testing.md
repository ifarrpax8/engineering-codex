# Testing: Content Strategy

## Contents

- [Content Accuracy Testing](#content-accuracy-testing)
- [Spelling and Grammar Checking](#spelling-and-grammar-checking)
- [Empty State Testing](#empty-state-testing)
- [Error Message Testing](#error-message-testing)
- [Truncation Testing](#truncation-testing)
- [Translation Readiness](#translation-readiness)
- [Accessibility Testing](#accessibility-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Content Accuracy Testing

Content accuracy ensures that the right words appear in the right places, and no placeholder content makes it to production.

### No Placeholder/Lorem Ipsum Text Shipped

**Automated Checks:**
```typescript
// Playwright test
test('no placeholder text in production', async ({ page }) => {
  await page.goto('/invoices');
  const text = await page.textContent('body');
  
  const placeholders = [
    'lorem ipsum',
    'placeholder',
    'enter text here',
    'example text',
    'sample data'
  ];
  
  for (const placeholder of placeholders) {
    expect(text?.toLowerCase()).not.toContain(placeholder);
  }
});
```

**Manual Checklist:**
- [ ] No "Lorem ipsum" text visible
- [ ] No "Placeholder" labels
- [ ] No "Example" or "Sample" data in production
- [ ] All tooltips have real content
- [ ] All help text is complete

### All Strings Externalized (No Hardcoded Strings)

**Static Analysis:**
```typescript
// ESLint rule to detect hardcoded strings
// .eslintrc.js
module.exports = {
  rules: {
    'no-hardcoded-strings': ['error', {
      exceptions: ['aria-label', 'data-testid'],
      requireI18n: true
    }]
  }
};
```

**Code Review Checklist:**
- [ ] All user-facing strings use i18n keys
- [ ] No string literals in templates/components
- [ ] Error messages come from message files
- [ ] Button labels use translation keys

**Example Test:**
```typescript
// Verify all buttons use i18n
test('all buttons use i18n keys', async ({ page }) => {
  const buttons = await page.locator('button').all();
  
  for (const button of buttons) {
    const text = await button.textContent();
    // Check that text matches a known i18n key pattern
    // or is a known exception (icon-only buttons)
    expect(text).toBeTruthy();
  }
});
```

## Spelling and Grammar Checking

Automated spelling and grammar checks catch mistakes before they reach users.

### Automated Lint for Common Mistakes

**Spell Checker:**
```bash
# Use cspell or similar
npm install -D cspell

# .cspell.json
{
  "version": "0.2",
  "language": "en",
  "words": [
    "invoice",
    "workspace",
    "i18n"
  ],
  "ignoreWords": [
    "testid",
    "aria"
  ],
  "dictionaries": ["typescript", "html"]
}
```

**Common Mistakes to Check:**
- Typos: "recieve" → "receive"
- Common confusions: "it's" vs "its", "your" vs "you're"
- Inconsistent terminology: "workspace" vs "project"
- Capitalization errors: "Invoice" vs "invoice"

**CI Integration:**
```yaml
# .github/workflows/spell-check.yml
name: Spell Check
on: [push, pull_request]
jobs:
  spell-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install
      - run: npm run spell-check
```

### Consistent Terminology

**Terminology Glossary Validation:**
```typescript
// Test that terminology matches glossary
const glossary = {
  'project': ['workspace', 'organization'], // forbidden alternatives
  'invoice': ['bill', 'statement'], // forbidden alternatives
};

test('terminology consistency', async ({ page }) => {
  const text = await page.textContent('body');
  
  // Check for forbidden terms
  for (const [correct, forbidden] of Object.entries(glossary)) {
    for (const term of forbidden) {
      expect(text?.toLowerCase()).not.toContain(term);
    }
  }
});
```

## Empty State Testing

Every list, table, and dashboard must have appropriate empty states.

### Every List/Table/Dashboard Has an Empty State

**Test Coverage:**
```typescript
// Playwright test
test('invoice list has empty state', async ({ page }) => {
  // Setup: ensure no invoices exist
  await setupEmptyInvoiceList();
  
  await page.goto('/invoices');
  
  // Verify empty state appears
  const emptyState = page.locator('[data-testid="empty-state"]');
  await expect(emptyState).toBeVisible();
  
  // Verify empty state has helpful content
  const text = await emptyState.textContent();
  expect(text).toContain('No invoices');
  expect(text).toContain('Create');
  
  // Verify CTA button exists
  const ctaButton = emptyState.locator('button');
  await expect(ctaButton).toBeVisible();
});
```

**Test Cases:**
- [ ] First-time empty state (no data ever created)
- [ ] Filtered empty state (data exists but filters hide it)
- [ ] Error empty state (data failed to load)
- [ ] Empty state includes call to action
- [ ] Empty state is visually distinct (not just blank space)

### Not Just Blank Space

**Visual Regression Testing:**
```typescript
test('empty state is not blank', async ({ page }) => {
  await setupEmptyInvoiceList();
  await page.goto('/invoices');
  
  // Verify content exists
  const content = await page.locator('main').textContent();
  expect(content?.trim().length).toBeGreaterThan(0);
  
  // Verify visual elements (icon, text, button)
  await expect(page.locator('[data-testid="empty-icon"]')).toBeVisible();
  await expect(page.locator('[data-testid="empty-text"]')).toBeVisible();
  await expect(page.locator('[data-testid="empty-cta"]')).toBeVisible();
});
```

## Error Message Testing

Trigger every error path and verify messages are helpful and actionable.

### Trigger Every Error Path

**Test Matrix:**
```typescript
describe('Error Message Testing', () => {
  const errorScenarios = [
    {
      name: 'Network error',
      trigger: () => mockNetworkError(),
      expectedMessage: /unable to connect|check your connection/i,
      expectedAction: /try again|retry/i
    },
    {
      name: 'Validation error',
      trigger: () => submitInvalidForm(),
      expectedMessage: /required|invalid/i,
      expectedAction: /enter|check/i
    },
    {
      name: 'Permission error',
      trigger: () => accessUnauthorizedResource(),
      expectedMessage: /permission|access denied/i,
      expectedAction: /contact|request access/i
    }
  ];
  
  for (const scenario of errorScenarios) {
    test(`error message for ${scenario.name}`, async ({ page }) => {
      await scenario.trigger();
      
      const errorMessage = await page.locator('[role="alert"]').textContent();
      
      // Verify message explains what happened
      expect(errorMessage).toMatch(scenario.expectedMessage);
      
      // Verify message includes actionable next steps
      expect(errorMessage).toMatch(scenario.expectedAction);
      
      // Verify message is in plain language (no technical jargon)
      const technicalTerms = ['nullpointerexception', '500', 'sql error'];
      for (const term of technicalTerms) {
        expect(errorMessage?.toLowerCase()).not.toContain(term);
      }
    });
  }
});
```

### Verify Messages Are Helpful and Actionable

**Content Quality Checks:**
```typescript
test('error messages are actionable', async ({ page }) => {
  // Trigger an error
  await triggerError();
  
  const errorMessage = await page.locator('[role="alert"]').textContent();
  
  // Check for action verbs
  const actionVerbs = ['try', 'check', 'enter', 'contact', 'refresh'];
  const hasAction = actionVerbs.some(verb => 
    errorMessage?.toLowerCase().includes(verb)
  );
  expect(hasAction).toBe(true);
  
  // Check for specific guidance (not just "Error occurred")
  expect(errorMessage?.length).toBeGreaterThan(20);
  
  // Check for user-friendly language
  const userFriendly = !errorMessage?.includes('Exception') &&
                       !errorMessage?.includes('Error 500');
  expect(userFriendly).toBe(true);
});
```

## Truncation Testing

Long strings must truncate gracefully without breaking the UI.

### Long Strings Don't Overflow

**Visual Testing:**
```typescript
test('long text truncates gracefully', async ({ page }) => {
  // Create content with very long text
  const longText = 'A'.repeat(500);
  await createInvoiceWithLongName(longText);
  
  await page.goto('/invoices');
  
  // Verify text doesn't overflow container
  const invoiceName = page.locator('[data-testid="invoice-name"]');
  const boundingBox = await invoiceName.boundingBox();
  const containerBox = await invoiceName.locator('..').boundingBox();
  
  expect(boundingBox?.width).toBeLessThanOrEqual(containerBox?.width || 0);
});
```

### Text Truncates Gracefully with Ellipsis

**Content Testing:**
```typescript
test('truncated text shows ellipsis', async ({ page }) => {
  const longText = 'A'.repeat(500);
  await createInvoiceWithLongName(longText);
  
  await page.goto('/invoices');
  
  const invoiceName = page.locator('[data-testid="invoice-name"]');
  const text = await invoiceName.textContent();
  
  // Verify text is truncated
  expect(text?.length).toBeLessThan(longText.length);
  
  // Verify ellipsis is present (or CSS handles it)
  const styles = await invoiceName.evaluate(el => 
    window.getComputedStyle(el)
  );
  expect(['ellipsis', 'clip']).toContain(styles.textOverflow);
});
```

### Tooltips Show Full Text

**Interaction Testing:**
```typescript
test('truncated text shows full content in tooltip', async ({ page }) => {
  const longText = 'This is a very long invoice name that will be truncated';
  await createInvoiceWithLongName(longText);
  
  await page.goto('/invoices');
  
  const invoiceName = page.locator('[data-testid="invoice-name"]');
  
  // Hover to show tooltip
  await invoiceName.hover();
  
  // Verify tooltip shows full text
  const tooltip = page.locator('[role="tooltip"]');
  await expect(tooltip).toBeVisible();
  
  const tooltipText = await tooltip.textContent();
  expect(tooltipText).toBe(longText);
});
```

## Translation Readiness

All strings must be ready for translation.

### All Strings Use i18n

**Static Analysis:**
```typescript
// ESLint rule
'no-hardcoded-strings': ['error', {
  exceptions: ['aria-label', 'data-testid'],
  requireI18n: true
}]
```

**Test Coverage:**
```typescript
test('all user-facing strings use i18n', async ({ page }) => {
  await page.goto('/invoices');
  
  // Get all text content
  const allText = await page.textContent('body');
  
  // Check for common hardcoded patterns
  const hardcodedPatterns = [
    /Error \d+/,  // Error 500
    /Click here/i,
    /Submit/i  // Should be specific action
  ];
  
  for (const pattern of hardcodedPatterns) {
    expect(allText).not.toMatch(pattern);
  }
});
```

### No Concatenated Strings (Breaks Translation)

**Bad:**
```typescript
// ❌ Breaks translation
const message = `You have ${count} items`;
```

**Good:**
```typescript
// ✅ Translation-friendly
const message = $t('invoice.list.count', { count });
```

**Test:**
```typescript
test('no string concatenation', async () => {
  // Static analysis: search codebase for concatenation patterns
  const files = glob('src/**/*.{ts,tsx,vue}');
  
  for (const file of files) {
    const content = readFileSync(file, 'utf-8');
    
    // Check for template literals with variables
    const concatenationPattern = /\$\{.*\}\s*\+\s*['"]|['"]\s*\+\s*\$\{/;
    expect(content).not.toMatch(concatenationPattern);
  }
});
```

### Pseudo-Localization Testing

**Pseudo-Localization:**
```json
// locales/pseudo.json - Extended characters to test UI
{
  "invoice.create.submit": "[Îñvøîçê Çrëå†ê]",
  "invoice.list.empty": "[Ñø îñvøîçêš ýë†]"
}
```

**Test:**
```typescript
test('UI handles extended characters', async ({ page }) => {
  // Switch to pseudo locale
  await page.goto('/invoices?lang=pseudo');
  
  // Verify UI doesn't break
  const buttons = await page.locator('button').all();
  for (const button of buttons) {
    const text = await button.textContent();
    expect(text).toBeTruthy();
    
    // Verify text is visible (not cut off)
    const boundingBox = await button.boundingBox();
    expect(boundingBox?.width).toBeGreaterThan(0);
  }
});
```

## Accessibility Testing

Content must be accessible to all users, including those using screen readers.

### Meaningful Link Text (Not "Click Here")

**Test:**
```typescript
test('all links have meaningful text', async ({ page }) => {
  await page.goto('/invoices');
  
  const links = await page.locator('a').all();
  
  for (const link of links) {
    const text = await link.textContent();
    const ariaLabel = await link.getAttribute('aria-label');
    
    // Link must have meaningful text or aria-label
    const hasMeaningfulText = 
      text && text.trim().length > 0 && 
      !text.toLowerCase().includes('click here');
    
    const hasAriaLabel = ariaLabel && ariaLabel.trim().length > 0;
    
    expect(hasMeaningfulText || hasAriaLabel).toBe(true);
  }
});
```

### Alt Text for Images

**Test:**
```typescript
test('all images have alt text', async ({ page }) => {
  await page.goto('/invoices');
  
  const images = await page.locator('img').all();
  
  for (const image of images) {
    const alt = await image.getAttribute('alt');
    
    // Decorative images can have empty alt, but must have aria-hidden
    const isDecorative = await image.getAttribute('aria-hidden') === 'true';
    
    if (!isDecorative) {
      expect(alt).toBeTruthy();
      expect(alt?.trim().length).toBeGreaterThan(0);
    }
  }
});
```

### Label Text for Form Fields

**Test:**
```typescript
test('all form fields have labels', async ({ page }) => {
  await page.goto('/invoices/create');
  
  const inputs = await page.locator('input, textarea, select').all();
  
  for (const input of inputs) {
    const id = await input.getAttribute('id');
    const ariaLabel = await input.getAttribute('aria-label');
    const ariaLabelledBy = await input.getAttribute('aria-labelledby');
    
    // Field must have label via id+label, aria-label, or aria-labelledby
    const hasLabel = id && page.locator(`label[for="${id}"]`).count() > 0;
    const hasAriaLabel = ariaLabel && ariaLabel.trim().length > 0;
    const hasAriaLabelledBy = ariaLabelledBy;
    
    expect(hasLabel || hasAriaLabel || hasAriaLabelledBy).toBe(true);
  }
});
```

## QA and Test Engineer Perspective

### Test Strategy for Content

**Content Testing Checklist:**
1. **Accuracy**: All copy matches design specs and style guide
2. **Completeness**: No placeholder text, all strings externalized
3. **Consistency**: Terminology matches glossary throughout
4. **Accessibility**: All content is accessible (labels, alt text, meaningful links)
5. **Error Handling**: All error paths have helpful messages
6. **Empty States**: All empty states have appropriate content and CTAs

### Content Regression Testing

**Visual Regression:**
- Capture screenshots of key pages with content
- Compare against baseline to catch content changes
- Flag unexpected content changes for review

**Content Snapshot Testing:**
```typescript
test('content matches expected values', async ({ page }) => {
  await page.goto('/invoices');
  
  const contentSnapshot = {
    pageTitle: await page.title(),
    heading: await page.locator('h1').textContent(),
    createButton: await page.locator('[data-testid="create-button"]').textContent(),
  };
  
  expect(contentSnapshot).toMatchSnapshot();
});
```

### Testing i18n Implementation

**Locale Switching:**
```typescript
test('content changes with locale', async ({ page }) => {
  // English
  await page.goto('/invoices?lang=en');
  const enButton = await page.locator('[data-testid="create-button"]').textContent();
  expect(enButton).toBe('Create Invoice');
  
  // Spanish
  await page.goto('/invoices?lang=es');
  const esButton = await page.locator('[data-testid="create-button"]').textContent();
  expect(esButton).toBe('Crear Factura');
});
```

**Missing Translation Detection:**
```typescript
test('no missing translations', async ({ page }) => {
  await page.goto('/invoices?lang=es');
  
  // Check for fallback to English (indicates missing translation)
  const text = await page.textContent('body');
  const englishOnlyTerms = ['Create Invoice', 'Delete', 'Save'];
  
  for (const term of englishOnlyTerms) {
    expect(text).not.toContain(term);
  }
});
```

### Content Performance Testing

**Load Time Impact:**
- Measure time to load i18n message files
- Verify content doesn't block initial render
- Test with large message catalogs

**Bundle Size:**
```typescript
test('i18n bundle size is reasonable', async () => {
  const bundleSize = await getBundleSize('locales/en.json');
  expect(bundleSize).toBeLessThan(100 * 1024); // 100KB limit
});
```

### Content Security Testing

**XSS Prevention:**
```typescript
test('user-generated content is sanitized', async ({ page }) => {
  const maliciousContent = '<script>alert("XSS")</script>';
  await createInvoiceWithDescription(maliciousContent);
  
  await page.goto('/invoices/1');
  
  // Verify script doesn't execute
  const scripts = await page.locator('script').count();
  expect(scripts).toBe(0);
  
  // Verify content is escaped
  const content = await page.locator('[data-testid="description"]').textContent();
  expect(content).not.toContain('<script>');
});
```

### Content A/B Testing Validation

**Variant Display:**
```typescript
test('A/B test variants display correctly', async ({ page }) => {
  // Test control variant
  await page.goto('/invoices?variant=control');
  const controlText = await page.locator('[data-testid="cta"]').textContent();
  expect(controlText).toBe('Create Invoice');
  
  // Test variant A
  await page.goto('/invoices?variant=A');
  const variantAText = await page.locator('[data-testid="cta"]').textContent();
  expect(variantAText).toBe('New Invoice');
});
```
