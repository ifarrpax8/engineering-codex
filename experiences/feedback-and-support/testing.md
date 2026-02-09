# Testing: Feedback & Support

## Contents

- [Feedback Form Submission Testing](#feedback-form-submission-testing)
- [Help Content Accuracy Testing](#help-content-accuracy-testing)
- [Knowledge Base Search Testing](#knowledge-base-search-testing)
- [Support Widget Behavior Testing](#support-widget-behavior-testing)
- [Feedback Routing Verification](#feedback-routing-verification)
- [Status Update Propagation Testing](#status-update-propagation-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Feedback Form Submission Testing

### Validation Testing

Test all form validation rules:

```typescript
// Playwright test example
import { test, expect } from '@playwright/test'

test.describe('Feedback Form Validation', () => {
  test('requires subject when submitting bug report', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.selectOption('[data-testid="feedback-type"]', 'bug')
    await page.fill('[data-testid="feedback-description"]', 'Something is broken')
    
    // Don't fill subject
    await page.click('[data-testid="submit-feedback"]')
    
    await expect(page.locator('[data-testid="subject-error"]')).toBeVisible()
    await expect(page.locator('[data-testid="subject-error"]')).toContainText('Subject is required')
  })
  
  test('validates email format for contact email', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="contact-email"]', 'invalid-email')
    
    await page.click('[data-testid="submit-feedback"]')
    
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible()
    await expect(page.locator('[data-testid="email-error"]')).toContainText('Invalid email format')
  })
  
  test('enforces maximum description length', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    const longDescription = 'a'.repeat(10001) // Exceeds 10,000 char limit
    await page.fill('[data-testid="feedback-description"]', longDescription)
    
    await page.click('[data-testid="submit-feedback"]')
    
    await expect(page.locator('[data-testid="description-error"]')).toBeVisible()
    await expect(page.locator('[data-testid="description-error"]')).toContainText('Maximum 10,000 characters')
  })
})
```

### File Attachment Testing

Test file upload functionality:

```typescript
test.describe('Feedback File Attachments', () => {
  test('allows image attachments', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    const fileInput = page.locator('[data-testid="file-input"]')
    await fileInput.setInputFiles({
      name: 'screenshot.png',
      mimeType: 'image/png',
      buffer: Buffer.from('fake-image-data')
    })
    
    await expect(page.locator('[data-testid="attachment-preview"]')).toBeVisible()
    await expect(page.locator('[data-testid="attachment-name"]')).toContainText('screenshot.png')
  })
  
  test('rejects files exceeding size limit', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    // Create a file that exceeds 10MB limit
    const largeFile = Buffer.alloc(11 * 1024 * 1024) // 11MB
    const fileInput = page.locator('[data-testid="file-input"]')
    
    await fileInput.setInputFiles({
      name: 'large-file.png',
      mimeType: 'image/png',
      buffer: largeFile
    })
    
    await expect(page.locator('[data-testid="file-error"]')).toBeVisible()
    await expect(page.locator('[data-testid="file-error"]')).toContainText('File size must be less than 10MB')
  })
  
  test('rejects unsupported file types', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    const fileInput = page.locator('[data-testid="file-input"]')
    await fileInput.setInputFiles({
      name: 'script.exe',
      mimeType: 'application/x-msdownload',
      buffer: Buffer.from('fake-exe-data')
    })
    
    await expect(page.locator('[data-testid="file-error"]')).toBeVisible()
    await expect(page.locator('[data-testid="file-error"]')).toContainText('File type not supported')
  })
})
```

### Context Capture Testing

Verify that context is automatically captured:

```typescript
test.describe('Feedback Context Capture', () => {
  test('captures current page URL', async ({ page }) => {
    await page.goto('/billing/invoices')
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="feedback-description"]', 'Test feedback')
    await page.fill('[data-testid="feedback-subject"]', 'Test subject')
    
    // Intercept API call to verify context
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.context.page.url).toBe('/billing/invoices')
  })
  
  test('captures browser information', async ({ page, browserName }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="feedback-description"]', 'Test')
    await page.fill('[data-testid="feedback-subject"]', 'Test')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.context.browser).toContain(browserName)
    expect(requestBody.context.userAgent).toBeTruthy()
  })
  
  test('captures console errors', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Trigger a console error
    await page.evaluate(() => {
      console.error('Test error message')
    })
    
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="feedback-description"]', 'Test')
    await page.fill('[data-testid="feedback-subject"]', 'Test')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.context.consoleErrors).toContain('Test error message')
  })
  
  test('captures screenshot when requested', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.check('[data-testid="include-screenshot"]')
    await page.fill('[data-testid="feedback-description"]', 'Test')
    await page.fill('[data-testid="feedback-subject"]', 'Test')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.context.screenshotUrl).toBeTruthy()
    expect(requestBody.context.screenshotUrl).toMatch(/^data:image\/png;base64,/)
  })
})
```

## Help Content Accuracy Testing

### Link Validation

Test that all links in help content are valid:

```typescript
test.describe('Help Content Links', () => {
  test('all internal links are valid', async ({ page }) => {
    await page.goto('/help/getting-started')
    
    const links = await page.locator('a[href^="/"]').all()
    
    for (const link of links) {
      const href = await link.getAttribute('href')
      const response = await page.goto(href!, { waitUntil: 'networkidle' })
      
      expect(response?.status()).toBe(200)
    }
  })
  
  test('external links open in new tab', async ({ page, context }) => {
    await page.goto('/help/integrations')
    
    const externalLinks = await page.locator('a[href^="http"]').all()
    
    for (const link of externalLinks) {
      const target = await link.getAttribute('target')
      expect(target).toBe('_blank')
      
      const rel = await link.getAttribute('rel')
      expect(rel).toContain('noopener')
      expect(rel).toContain('noreferrer')
    }
  })
  
  test('broken links are detected', async ({ page }) => {
    await page.goto('/help')
    
    // Use a link checker library or custom logic
    const brokenLinks = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a[href]'))
      return Promise.all(
        links.map(async (link: HTMLAnchorElement) => {
          try {
            const response = await fetch(link.href, { method: 'HEAD' })
            return { href: link.href, broken: !response.ok }
          } catch {
            return { href: link.href, broken: true }
          }
        })
      )
    })
    
    const actuallyBroken = brokenLinks.filter(link => link.broken)
    expect(actuallyBroken).toHaveLength(0)
  })
})
```

### Content Accuracy

Verify help content matches current UI:

```typescript
test.describe('Help Content Accuracy', () => {
  test('help article screenshots match current UI', async ({ page }) => {
    await page.goto('/help/bulk-export')
    
    // Extract screenshot from help article
    const helpScreenshot = await page.locator('[data-testid="help-screenshot"]').screenshot()
    
    // Navigate to actual feature
    await page.goto('/exports')
    const actualScreenshot = await page.screenshot()
    
    // Compare screenshots (using pixelmatch or similar)
    const diff = await compareImages(helpScreenshot, actualScreenshot)
    expect(diff.percentage).toBeLessThan(5) // Allow 5% difference
  })
  
  test('help article steps match current workflow', async ({ page }) => {
    await page.goto('/help/create-invoice')
    
    // Extract steps from help article
    const steps = await page.locator('[data-testid="help-step"]').allTextContents()
    
    // Follow steps and verify they work
    await page.goto('/invoices/new')
    
    for (const step of steps) {
      // Parse step and execute
      // Verify UI elements exist and are clickable
    }
  })
  
  test('help article mentions current feature flags', async ({ page }) => {
    await page.goto('/help/advanced-features')
    
    const mentionedFeatures = await page.locator('[data-testid="feature-mention"]').allTextContents()
    
    // Verify all mentioned features are actually available
    for (const feature of mentionedFeatures) {
      const isAvailable = await page.evaluate((featureName) => {
        // Check if feature is enabled for current user
        return window.featureFlags?.includes(featureName)
      }, feature)
      
      expect(isAvailable).toBe(true)
    }
  })
})
```

## Knowledge Base Search Testing

### Search Relevance

Test that search returns relevant results:

```typescript
test.describe('Knowledge Base Search', () => {
  test('returns relevant results for common queries', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'bulk export')
    
    await page.waitForSelector('[data-testid="search-results"]')
    const results = await page.locator('[data-testid="search-result"]').all()
    
    expect(results.length).toBeGreaterThan(0)
    
    // Verify first result is relevant
    const firstResultTitle = await results[0].locator('[data-testid="result-title"]').textContent()
    expect(firstResultTitle?.toLowerCase()).toContain('export')
  })
  
  test('handles typos gracefully', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'bulk exprot') // Typo
    
    await page.waitForSelector('[data-testid="search-results"]')
    const results = await page.locator('[data-testid="search-result"]').all()
    
    // Should still return results (fuzzy matching)
    expect(results.length).toBeGreaterThan(0)
  })
  
  test('filters results by category', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'invoice')
    await page.selectOption('[data-testid="category-filter"]', 'billing')
    
    await page.waitForSelector('[data-testid="search-results"]')
    const results = await page.locator('[data-testid="search-result"]').all()
    
    for (const result of results) {
      const category = await result.locator('[data-testid="result-category"]').textContent()
      expect(category).toBe('Billing')
    }
  })
})
```

### Zero-Result Handling

Test behavior when no results are found:

```typescript
test.describe('Knowledge Base Zero Results', () => {
  test('shows helpful message when no results found', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'nonexistent-feature-xyz-123')
    
    await page.waitForSelector('[data-testid="no-results"]')
    
    await expect(page.locator('[data-testid="no-results"]')).toBeVisible()
    await expect(page.locator('[data-testid="no-results"]')).toContainText('No articles found')
    
    // Should suggest alternatives
    await expect(page.locator('[data-testid="suggested-articles"]')).toBeVisible()
  })
  
  test('suggests similar queries', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'bulk exprot') // Typo
    
    await page.waitForSelector('[data-testid="search-results"]')
    
    // Should show "Did you mean..." suggestion
    const suggestion = await page.locator('[data-testid="search-suggestion"]').textContent()
    expect(suggestion).toContain('bulk export')
  })
  
  test('provides contact support option', async ({ page }) => {
    await page.goto('/help')
    await page.fill('[data-testid="help-search"]', 'very-specific-error-xyz')
    
    await page.waitForSelector('[data-testid="no-results"]')
    
    // Should show option to contact support
    await expect(page.locator('[data-testid="contact-support-link"]')).toBeVisible()
  })
})
```

## Support Widget Behavior Testing

### Widget Interaction

Test widget open/close behavior:

```typescript
test.describe('Support Widget Behavior', () => {
  test('opens and closes widget', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Widget should be closed initially
    await expect(page.locator('[data-testid="feedback-widget"]')).not.toBeVisible()
    
    // Click to open
    await page.click('[data-testid="feedback-button"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).toBeVisible()
    
    // Click close button
    await page.click('[data-testid="close-widget"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).not.toBeVisible()
  })
  
  test('closes widget on Escape key', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).toBeVisible()
    
    await page.keyboard.press('Escape')
    await expect(page.locator('[data-testid="feedback-widget"]')).not.toBeVisible()
  })
  
  test('closes widget when clicking outside', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).toBeVisible()
    
    // Click outside widget
    await page.click('body', { position: { x: 0, y: 0 } })
    await expect(page.locator('[data-testid="feedback-widget"]')).not.toBeVisible()
  })
})
```

### Non-Interference Testing

Verify widget doesn't interfere with app functionality:

```typescript
test.describe('Widget Non-Interference', () => {
  test('does not block critical UI elements', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Open widget
    await page.click('[data-testid="feedback-button"]')
    
    // Verify critical buttons are still clickable
    const saveButton = page.locator('[data-testid="save-button"]')
    await expect(saveButton).toBeVisible()
    await expect(saveButton).not.toBeCoveredBy(page.locator('[data-testid="feedback-widget"]'))
  })
  
  test('does not affect form submissions', async ({ page }) => {
    await page.goto('/invoices/new')
    
    // Fill form
    await page.fill('[data-testid="invoice-number"]', 'INV-001')
    await page.fill('[data-testid="amount"]', '100.00')
    
    // Open widget (should not interfere)
    await page.click('[data-testid="feedback-button"]')
    
    // Submit form
    await page.click('[data-testid="submit-invoice"]')
    
    // Verify submission succeeded
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible()
  })
  
  test('maintains z-index below modals', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    // Open a modal
    await page.click('[data-testid="open-modal"]')
    
    // Widget should be behind modal
    const widgetZIndex = await page.evaluate(() => {
      const widget = document.querySelector('[data-testid="feedback-widget"]')
      return window.getComputedStyle(widget!).zIndex
    })
    
    const modalZIndex = await page.evaluate(() => {
      const modal = document.querySelector('[data-testid="modal"]')
      return window.getComputedStyle(modal!).zIndex
    })
    
    expect(parseInt(modalZIndex)).toBeGreaterThan(parseInt(widgetZIndex))
  })
})
```

### Responsive Behavior

Test widget on different screen sizes:

```typescript
test.describe('Widget Responsive Behavior', () => {
  test('widget is accessible on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }) // iPhone SE
    await page.goto('/dashboard')
    
    await page.click('[data-testid="feedback-button"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).toBeVisible()
    
    // Widget should be full-width or appropriately sized
    const widgetBox = await page.locator('[data-testid="feedback-widget"]').boundingBox()
    expect(widgetBox!.width).toBeLessThanOrEqual(375)
  })
  
  test('widget adapts to tablet size', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }) // iPad
    await page.goto('/dashboard')
    
    await page.click('[data-testid="feedback-button"]')
    await expect(page.locator('[data-testid="feedback-widget"]')).toBeVisible()
    
    // Should use appropriate width
    const widgetBox = await page.locator('[data-testid="feedback-widget"]').boundingBox()
    expect(widgetBox!.width).toBeLessThanOrEqual(600)
  })
})
```

## Feedback Routing Verification

### Category Routing

Verify feedback is routed to correct teams:

```typescript
test.describe('Feedback Routing', () => {
  test('bug reports route to engineering team', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    await page.selectOption('[data-testid="feedback-type"]', 'bug')
    await page.fill('[data-testid="feedback-subject"]', 'Button not working')
    await page.fill('[data-testid="feedback-description"]', 'The save button does nothing')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    // Verify routing metadata
    expect(requestBody.category).toBe('BUG')
    expect(requestBody.routing.team).toBe('ENGINEERING')
  })
  
  test('feature requests route to product team', async ({ page }) => {
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    
    await page.selectOption('[data-testid="feedback-type"]', 'feature')
    await page.fill('[data-testid="feedback-subject"]', 'Add bulk delete')
    await page.fill('[data-testid="feedback-description"]', 'Would be great to delete multiple items at once')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.category).toBe('FEATURE_REQUEST')
    expect(requestBody.routing.team).toBe('PRODUCT')
  })
  
  test('billing questions route to finance team', async ({ page }) => {
    await page.goto('/billing')
    await page.click('[data-testid="feedback-button"]')
    
    await page.selectOption('[data-testid="feedback-type"]', 'question')
    await page.selectOption('[data-testid="feedback-category"]', 'billing')
    await page.fill('[data-testid="feedback-subject"]', 'Invoice question')
    await page.fill('[data-testid="feedback-description"]', 'Why was I charged twice?')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.category).toBe('BILLING')
    expect(requestBody.routing.team).toBe('FINANCE')
  })
})
```

### Priority Assignment

Test that priority is correctly assigned:

```typescript
test.describe('Feedback Priority Assignment', () => {
  test('admin user feedback gets high priority', async ({ page }) => {
    // Login as admin
    await page.goto('/login')
    await page.fill('[data-testid="email"]', 'admin@example.com')
    await page.fill('[data-testid="password"]', 'password')
    await page.click('[data-testid="login"]')
    
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.selectOption('[data-testid="feedback-type"]', 'bug')
    await page.fill('[data-testid="feedback-subject"]', 'Critical issue')
    await page.fill('[data-testid="feedback-description"]', 'This is blocking our workflow')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    expect(requestBody.priority).toBe('HIGH')
  })
  
  test('blocking errors get critical priority', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Trigger console error
    await page.evaluate(() => {
      console.error('Critical error occurred')
    })
    
    await page.click('[data-testid="feedback-button"]')
    await page.selectOption('[data-testid="feedback-type"]', 'bug')
    await page.fill('[data-testid="feedback-subject"]', 'Error occurred')
    await page.fill('[data-testid="feedback-description"]', 'Something broke')
    
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/feedback')
    )
    
    await page.click('[data-testid="submit-feedback"]')
    const request = await requestPromise
    const requestBody = request.postDataJSON()
    
    // Should detect console errors and assign critical priority
    expect(requestBody.priority).toBe('CRITICAL')
  })
})
```

## Status Update Propagation Testing

### Ticket Status Updates

Test that ticket status changes propagate to users:

```typescript
test.describe('Status Update Propagation', () => {
  test('user receives notification when ticket is resolved', async ({ page }) => {
    // Submit feedback
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="feedback-subject"]', 'Test issue')
    await page.fill('[data-testid="feedback-description"]', 'Test description')
    await page.click('[data-testid="submit-feedback"]')
    
    // Get ticket number from confirmation
    const ticketNumber = await page.locator('[data-testid="ticket-number"]').textContent()
    
    // Simulate ticket resolution (via API or admin panel)
    await page.request.post('/api/v1/admin/tickets/resolve', {
      data: { ticketNumber, resolution: 'Fixed in v2.1.0' }
    })
    
    // Verify notification appears
    await expect(page.locator('[data-testid="notification"]')).toBeVisible()
    await expect(page.locator('[data-testid="notification"]')).toContainText('Your ticket has been resolved')
  })
  
  test('feedback status page updates in real-time', async ({ page }) => {
    // Submit feedback and navigate to status page
    await page.goto('/dashboard')
    await page.click('[data-testid="feedback-button"]')
    await page.fill('[data-testid="feedback-subject"]', 'Test issue')
    await page.fill('[data-testid="feedback-description"]', 'Test description')
    await page.click('[data-testid="submit-feedback"]')
    
    const ticketNumber = await page.locator('[data-testid="ticket-number"]').textContent()
    await page.click('[data-testid="view-status"]')
    
    // Verify initial status
    await expect(page.locator('[data-testid="ticket-status"]')).toContainText('Submitted')
    
    // Simulate status change
    await page.request.post('/api/v1/admin/tickets/update-status', {
      data: { ticketNumber, status: 'In Progress' }
    })
    
    // Wait for WebSocket update or poll for change
    await page.waitForTimeout(2000) // Wait for WebSocket message
    
    // Verify status updated
    await expect(page.locator('[data-testid="ticket-status"]')).toContainText('In Progress')
  })
})
```

## QA and Test Engineer Perspective

### Test Coverage Requirements

**Critical Test Areas**:

1. **Feedback Submission Flow**: End-to-end testing of feedback form submission, validation, context capture, and API integration
2. **Help Content Validation**: Automated checks for broken links, outdated screenshots, and content accuracy
3. **Search Functionality**: Relevance testing, zero-result handling, and search performance
4. **Widget Behavior**: Open/close, non-interference, responsive design, accessibility
5. **Routing Logic**: Category-based routing, priority assignment, team assignment
6. **Status Propagation**: Real-time updates, notifications, status page accuracy

### Test Data Management

**Feedback Test Data**:

```typescript
// Test fixtures for feedback testing
export const feedbackFixtures = {
  validBugReport: {
    type: 'bug',
    subject: 'Save button not working',
    description: 'When I click save, nothing happens',
    category: 'ui'
  },
  validFeatureRequest: {
    type: 'feature',
    subject: 'Add dark mode',
    description: 'Would love to have a dark mode option',
    category: 'ui'
  },
  invalidFeedback: {
    type: 'bug',
    subject: '', // Missing required field
    description: 'Test'
  }
}
```

### Regression Testing

**Critical Regression Scenarios**:

1. Feedback widget doesn't break existing workflows
2. Help content links remain valid after deployments
3. Search continues to work after knowledge base updates
4. Status updates propagate correctly after backend changes
5. Multi-tenant isolation maintained after routing changes

### Performance Testing

**Key Performance Metrics**:

- Feedback form submission: < 2 seconds
- Help search results: < 500ms
- Widget load time: < 1 second
- Status page load: < 1 second

### Accessibility Testing

**WCAG Compliance**:

- Feedback widget keyboard accessible
- Screen reader compatible
- Proper ARIA labels
- Color contrast meets WCAG AA standards
- Focus management when widget opens/closes

### Integration Testing

**External System Integration**:

- Jira Service Management ticket creation
- Zendesk ticket creation and status sync
- Email notification delivery
- WebSocket connection for real-time updates
