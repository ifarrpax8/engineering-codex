# Testing: Forms and Data Entry

## Contents

- [Unit Testing Validation Logic](#unit-testing-validation-logic)
- [Component Testing Form Interactions](#component-testing-form-interactions)
- [E2E Form Flow Testing](#e2e-form-flow-testing)
- [Multi-Page Form Specific Testing](#multi-page-form-specific-testing)
- [Accessibility Testing for Forms](#accessibility-testing-for-forms)
- [Edge Cases](#edge-cases)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Unit Testing Validation Logic

Validation logic should be thoroughly unit tested independently of UI components.

### Testing Zod Schemas

**Example** (TypeScript/Jest):
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email('Invalid email'),
  age: z.number().min(18, 'Must be 18+'),
});

describe('User Schema Validation', () => {
  it('should accept valid user data', () => {
    const validData = { email: 'test@example.com', age: 25 };
    expect(() => userSchema.parse(validData)).not.toThrow();
  });
  
  it('should reject invalid email', () => {
    const invalidData = { email: 'not-an-email', age: 25 };
    expect(() => userSchema.parse(invalidData)).toThrow();
  });
  
  it('should reject age below 18', () => {
    const invalidData = { email: 'test@example.com', age: 17 };
    const result = userSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    expect(result.error?.issues[0].message).toBe('Must be 18+');
  });
});
```

### Testing Custom Validators

**Spring Boot Custom Validator Testing**:
```kotlin
class UniqueEmailValidatorTest {
    @Test
    fun `should return true for unique email`() {
        val validator = UniqueEmailValidator()
        val context = mock<ConstraintValidatorContext>()
        whenever(userRepository.existsByEmail("new@example.com")).thenReturn(false)
        
        val isValid = validator.isValid("new@example.com", context)
        
        assertTrue(isValid)
    }
    
    @Test
    fun `should return false for duplicate email`() {
        val validator = UniqueEmailValidator()
        val context = mock<ConstraintValidatorContext>()
        whenever(userRepository.existsByEmail("existing@example.com")).thenReturn(true)
        
        val isValid = validator.isValid("existing@example.com", context)
        
        assertFalse(isValid)
    }
}
```

### Testing Async Validation

**Testing Client-Side Async Validation**:
```typescript
describe('Async Email Validation', () => {
  it('should validate unique email', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => ({ available: true })
    });
    
    const result = await validateEmail('test@example.com');
    expect(result).toBe(true);
  });
  
  it('should reject duplicate email', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => ({ available: false })
    });
    
    const result = await validateEmail('taken@example.com');
    expect(result).toBe('Email already taken');
  });
});
```

## Component Testing Form Interactions

Test form components in isolation to verify user interactions and validation behavior.

### React Testing Library

**Example**:
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserForm } from './UserForm';

describe('UserForm', () => {
  it('should show validation error on invalid email', async () => {
    render(<UserForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    });
  });
  
  it('should submit form with valid data', async () => {
    const onSubmit = jest.fn();
    render(<UserForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/age/i), {
      target: { value: '25' }
    });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        age: 25
      });
    });
  });
  
  it('should disable submit button while submitting', async () => {
    const onSubmit = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<UserForm onSubmit={onSubmit} />);
    
    // Fill form...
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
    
    expect(submitButton).toBeDisabled();
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });
});
```

### Vue Test Utils

**Example**:
```typescript
import { mount } from '@vue/test-utils';
import { UserForm } from './UserForm.vue';

describe('UserForm', () => {
  it('should show validation error on invalid email', async () => {
    const wrapper = mount(UserForm);
    
    const emailInput = wrapper.find('input[type="email"]');
    await emailInput.setValue('invalid-email');
    await emailInput.trigger('blur');
    
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Invalid email');
  });
  
  it('should submit form with valid data', async () => {
    const onSubmit = jest.fn();
    const wrapper = mount(UserForm, {
      props: { onSubmit }
    });
    
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="number"]').setValue('25');
    await wrapper.find('button[type="submit"]').trigger('click');
    
    await wrapper.vm.$nextTick();
    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      age: 25
    });
  });
});
```

### Testing Form Libraries Integration

**React Hook Form**:
```typescript
import { renderHook, act } from '@testing-library/react';
import { useForm } from 'react-hook-form';

describe('React Hook Form Integration', () => {
  it('should validate on submit', async () => {
    const { result } = renderHook(() => useForm({
      resolver: zodResolver(userSchema)
    }));
    
    act(() => {
      result.current.setValue('email', 'invalid-email');
    });
    
    const submitResult = await act(async () => {
      return result.current.handleSubmit(() => {})({ preventDefault: () => {} } as any);
    });
    
    expect(result.current.formState.errors.email).toBeDefined();
  });
});
```

## E2E Form Flow Testing

End-to-end tests verify complete form workflows from user perspective.

### Playwright Form Testing

**Basic Form Fill and Submit**:
```typescript
import { test, expect } from '@playwright/test';

test('should complete registration form', async ({ page }) => {
  await page.goto('/register');
  
  // Fill form fields
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123!');
  await page.fill('[name="confirmPassword"]', 'SecurePass123!');
  await page.check('[name="terms"]');
  
  // Submit form
  await page.click('button[type="submit"]');
  
  // Verify success
  await expect(page).toHaveURL('/register/success');
  await expect(page.locator('text=Registration successful')).toBeVisible();
});

test('should show validation errors on invalid input', async ({ page }) => {
  await page.goto('/register');
  
  // Submit without filling required fields
  await page.click('button[type="submit"]');
  
  // Verify error messages
  await expect(page.locator('text=Email is required')).toBeVisible();
  await expect(page.locator('text=Password is required')).toBeVisible();
});
```

**Testing Form State Persistence**:
```typescript
test('should preserve form data on page reload', async ({ page }) => {
  await page.goto('/long-form');
  
  // Fill some fields
  await page.fill('[name="field1"]', 'value1');
  await page.fill('[name="field2"]', 'value2');
  
  // Reload page
  await page.reload();
  
  // Verify data persisted (if using localStorage/autosave)
  await expect(page.locator('[name="field1"]')).toHaveValue('value1');
  await expect(page.locator('[name="field2"]')).toHaveValue('value2');
});
```

**Testing File Upload**:
```typescript
test('should upload file and show progress', async ({ page }) => {
  await page.goto('/upload');
  
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('test-fixtures/sample.pdf');
  
  // Wait for upload to complete
  await expect(page.locator('text=Upload complete')).toBeVisible({ timeout: 10000 });
  
  // Verify file appears in list
  await expect(page.locator('text=sample.pdf')).toBeVisible();
});
```

## Multi-Page Form Specific Testing

Multi-page wizard forms require specialized testing strategies.

### Step Navigation Testing

**Testing Step Progression**:
```typescript
test('should navigate through wizard steps', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Fill step 1
  await page.fill('[name="name"]', 'John Doe');
  await page.click('button:has-text("Next")');
  
  // Verify step 2 loaded
  await expect(page).toHaveURL('/wizard/step-2');
  await expect(page.locator('text=Step 2 of 4')).toBeVisible();
  
  // Fill step 2
  await page.fill('[name="email"]', 'john@example.com');
  await page.click('button:has-text("Next")');
  
  // Verify step 3 loaded
  await expect(page).toHaveURL('/wizard/step-3');
});
```

**Testing Back Navigation**:
```typescript
test('should preserve data when navigating back', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Fill and proceed
  await page.fill('[name="name"]', 'John Doe');
  await page.click('button:has-text("Next")');
  
  // Go back
  await page.click('button:has-text("Back")');
  
  // Verify data preserved
  await expect(page.locator('[name="name"]')).toHaveValue('John Doe');
});
```

### Draft Recovery Testing

**Testing Draft Save and Load**:
```typescript
test('should save draft and allow recovery', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Fill partial data
  await page.fill('[name="name"]', 'John Doe');
  await page.fill('[name="email"]', 'john@example.com');
  
  // Save draft (if explicit save button exists)
  await page.click('button:has-text("Save Draft")');
  await expect(page.locator('text=Draft saved')).toBeVisible();
  
  // Navigate away
  await page.goto('/');
  
  // Return to wizard
  await page.goto('/wizard/step-1');
  
  // Verify draft loaded
  await expect(page.locator('[name="name"]')).toHaveValue('John Doe');
  await expect(page.locator('[name="email"]')).toHaveValue('john@example.com');
});
```

**Testing Autosave**:
```typescript
test('should autosave draft after user stops typing', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Type in field
  await page.fill('[name="name"]', 'John');
  
  // Wait for autosave debounce (e.g., 500ms)
  await page.waitForTimeout(600);
  
  // Verify autosave indicator appears
  await expect(page.locator('text=Saved')).toBeVisible();
  
  // Verify draft persisted
  const draftData = await page.evaluate(() => {
    return localStorage.getItem('wizard-draft');
  });
  expect(JSON.parse(draftData).name).toBe('John');
});
```

### Conditional Step Logic Testing

**Testing Conditional Step Visibility**:
```typescript
test('should skip step based on user selection', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Select option that skips a step
  await page.selectOption('[name="accountType"]', 'individual');
  await page.click('button:has-text("Next")');
  
  // Verify skipped step (e.g., "Company Details" should be skipped)
  await expect(page).not.toHaveURL(/step-company/);
  
  // Verify correct next step loaded
  await expect(page).toHaveURL('/wizard/step-payment');
});
```

**Testing Dynamic Step Order**:
```typescript
test('should show different steps based on path', async ({ page }) => {
  // Path A: Business account
  await page.goto('/wizard/step-1');
  await page.selectOption('[name="accountType"]', 'business');
  await page.click('button:has-text("Next")');
  
  // Should show company details step
  await expect(page.locator('text=Company Details')).toBeVisible();
  
  // Path B: Individual account
  await page.goto('/wizard/step-1');
  await page.selectOption('[name="accountType"]', 'individual');
  await page.click('button:has-text("Next")');
  
  // Should skip company details
  await expect(page.locator('text=Company Details')).not.toBeVisible();
});
```

### Browser Back Button Testing

**Testing Browser Back Button Handling**:
```typescript
test('should handle browser back button correctly', async ({ page }) => {
  await page.goto('/wizard/step-1');
  
  // Navigate forward through steps
  await page.fill('[name="name"]', 'John');
  await page.click('button:has-text("Next")');
  await expect(page).toHaveURL('/wizard/step-2');
  
  await page.fill('[name="email"]', 'john@example.com');
  await page.click('button:has-text("Next")');
  await expect(page).toHaveURL('/wizard/step-3');
  
  // Use browser back button
  await page.goBack();
  await expect(page).toHaveURL('/wizard/step-2');
  
  // Verify data preserved
  await expect(page.locator('[name="email"]')).toHaveValue('john@example.com');
  
  // Go back again
  await page.goBack();
  await expect(page).toHaveURL('/wizard/step-1');
  await expect(page.locator('[name="name"]')).toHaveValue('John');
});
```

### Session Expiry Testing

**Testing Session Expiry Mid-Form**:
```typescript
test('should handle session expiry gracefully', async ({ page, context }) => {
  await page.goto('/wizard/step-1');
  
  // Fill some data
  await page.fill('[name="name"]', 'John Doe');
  
  // Simulate session expiry (clear cookies/storage)
  await context.clearCookies();
  await page.evaluate(() => localStorage.clear());
  
  // Try to proceed
  await page.click('button:has-text("Next")');
  
  // Should show session expiry message and redirect to login
  await expect(page.locator('text=Session expired')).toBeVisible();
  await expect(page).toHaveURL('/login');
  
  // After re-authentication, should restore draft or allow restart
});
```

## Accessibility Testing for Forms

Forms must be accessible to users with disabilities.

### Label Associations

**Testing Label-Input Associations**:
```typescript
test('should have proper label associations', async ({ page }) => {
  await page.goto('/register');
  
  // Verify labels are properly associated with inputs
  const emailInput = page.locator('[name="email"]');
  const emailLabel = page.locator('label[for="email"]');
  
  // Check aria-labelledby or explicit for/id association
  const inputId = await emailInput.getAttribute('id');
  const labelFor = await emailLabel.getAttribute('for');
  expect(labelFor).toBe(inputId);
});
```

### Error Announcements

**Testing Screen Reader Error Announcements**:
```typescript
test('should announce errors to screen readers', async ({ page }) => {
  await page.goto('/register');
  
  // Submit form with errors
  await page.click('button[type="submit"]');
  
  // Verify error has proper ARIA attributes
  const errorMessage = page.locator('[role="alert"]');
  await expect(errorMessage).toBeVisible();
  
  // Verify input has aria-describedby pointing to error
  const emailInput = page.locator('[name="email"]');
  const describedBy = await emailInput.getAttribute('aria-describedby');
  expect(describedBy).toContain('email-error');
});
```

### Keyboard Navigation

**Testing Keyboard-Only Navigation**:
```typescript
test('should be navigable with keyboard only', async ({ page }) => {
  await page.goto('/register');
  
  // Tab through form fields
  await page.keyboard.press('Tab');
  await expect(page.locator('[name="email"]')).toBeFocused();
  
  await page.keyboard.press('Tab');
  await expect(page.locator('[name="password"]')).toBeFocused();
  
  // Submit with Enter key
  await page.keyboard.press('Tab'); // Move to submit button
  await page.keyboard.press('Enter');
  
  // Verify form submitted
  await expect(page).toHaveURL('/register/success');
});
```

**Testing Focus Management**:
```typescript
test('should move focus to first error on submit', async ({ page }) => {
  await page.goto('/register');
  
  // Submit invalid form
  await page.click('button[type="submit"]');
  
  // Verify focus moved to first error field
  await expect(page.locator('[name="email"]')).toBeFocused();
});
```

## Edge Cases

Test edge cases that users might encounter.

### Paste and Autofill

**Testing Paste Behavior**:
```typescript
test('should handle pasted content correctly', async ({ page }) => {
  await page.goto('/register');
  
  const emailInput = page.locator('[name="email"]');
  
  // Simulate paste
  await emailInput.click();
  await page.keyboard.press('Meta+v'); // Cmd+V on Mac, Ctrl+V on Windows
  
  // Or use clipboard API
  await page.evaluate(async () => {
    await navigator.clipboard.writeText('test@example.com');
  });
  await emailInput.press('Meta+v');
  
  await expect(emailInput).toHaveValue('test@example.com');
});
```

**Testing Browser Autofill**:
```typescript
test('should work with browser autofill', async ({ page }) => {
  await page.goto('/register');
  
  // Trigger autofill (browser-specific, may require manual setup)
  const emailInput = page.locator('[name="email"]');
  await emailInput.click();
  await page.keyboard.press('ArrowDown'); // Trigger autofill dropdown
  
  // Verify autofilled value is accepted
  // Note: Actual autofill testing may require browser-specific setup
});
```

### Special Characters

**Testing Special Character Handling**:
```typescript
test('should handle special characters in input', async ({ page }) => {
  await page.goto('/register');
  
  const nameInput = page.locator('[name="name"]');
  
  // Test various special characters
  const specialChars = "O'Brien & Co. <test> \"quotes\" 'apostrophes'";
  await nameInput.fill(specialChars);
  
  // Verify no errors and value preserved
  await expect(nameInput).toHaveValue(specialChars);
  
  // Submit and verify server receives correctly
  await page.click('button[type="submit"]');
  // Verify success (server should handle special chars)
});
```

### Network Conditions

**Testing Slow Network Submission**:
```typescript
test('should prevent double submission on slow network', async ({ page }) => {
  // Throttle network
  await page.route('**/api/submit', route => {
    setTimeout(() => route.continue(), 2000); // 2 second delay
  });
  
  await page.goto('/register');
  
  // Fill and submit
  await page.fill('[name="email"]', 'test@example.com');
  const submitButton = page.locator('button[type="submit"]');
  
  // Click submit multiple times rapidly
  await submitButton.click();
  await submitButton.click();
  await submitButton.click();
  
  // Verify only one submission occurred
  // (Check network requests or server logs)
  await expect(submitButton).toBeDisabled(); // Should be disabled after first click
});
```

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

**High-Risk Areas** (Test thoroughly):
1. **Payment/Checkout Forms**: Financial data, must be 100% accurate
2. **Account Creation**: Security implications, user lockout risks
3. **Data Entry with Business Impact**: Orders, invoices, critical business data
4. **Multi-Page Wizards**: Complex state management, high abandonment risk
5. **File Uploads**: Large files, security risks, storage costs

**Medium-Risk Areas**:
1. **Contact Forms**: Lower impact, but still important for lead generation
2. **Search Forms**: User experience impact, but non-critical
3. **Settings Forms**: User preference changes, reversible

**Low-Risk Areas** (Smoke test sufficient):
1. **Newsletter Signups**: Simple, low impact
2. **Feedback Forms**: Non-critical data collection

### Exploratory Testing Guidance

**Form-Specific Exploratory Scenarios**:

1. **Field Interaction Testing**:
   - Fill fields in different orders
   - Use Tab vs Click navigation
   - Test with keyboard only (no mouse)
   - Try rapid field switching

2. **Validation Timing Exploration**:
   - Type quickly, then blur immediately
   - Type slowly, pause between characters
   - Paste large amounts of text
   - Use autofill, then modify

3. **Multi-Page Wizard Exploration**:
   - Navigate forward, then back multiple times
   - Fill step 1, go to step 3 directly (if possible), then back
   - Fill form, close browser, reopen
   - Fill on mobile, continue on desktop (if cross-device)

4. **Error Recovery Exploration**:
   - Submit with errors, fix one at a time
   - Fix error, then immediately cause another error
   - Submit with network disconnected, then reconnect

5. **Browser-Specific Exploration**:
   - Test in Chrome, Firefox, Safari, Edge
   - Test on mobile browsers (iOS Safari, Chrome Mobile)
   - Test with browser extensions (password managers, autofill tools)

### Test Data Management

**Test Data Strategies**:

1. **Valid Test Data Sets**:
   - Create reusable valid data sets for happy path testing
   - Include edge cases: very long names, special characters, international characters
   - Store in test fixtures or data files

2. **Invalid Test Data Sets**:
   - Test each validation rule with specific invalid data
   - Include boundary values (e.g., age: 17, 18, 19 for min-age validation)
   - Test SQL injection, XSS attempts in text fields

3. **Multi-Page Wizard Test Data**:
   - Create complete wizard data sets for end-to-end testing
   - Create partial data sets for draft recovery testing
   - Create conditional path data sets (e.g., business vs individual account)

4. **Data Cleanup**:
   - Clean up test data after test runs (especially for account creation tests)
   - Use test user accounts that can be safely deleted
   - Isolate test data from production-like environments

### Test Environment Considerations

**Environment-Specific Testing**:

1. **Development Environment**:
   - Test new features, validation changes
   - May have relaxed validation for development ease
   - Use for initial exploratory testing

2. **Staging Environment**:
   - Mirror production as closely as possible
   - Test with production-like data volumes
   - Test integration with external services (payment gateways, email services)

3. **Production-Like Testing**:
   - Test with realistic network conditions (throttling)
   - Test with production-like server load
   - Test with actual third-party service integrations (sandbox modes)

**Form-Specific Environment Needs**:
- Email service for registration/verification testing
- File storage service for upload testing
- Payment gateway sandbox for checkout testing
- Session storage/Redis for draft persistence testing

### Regression Strategy

**Form Regression Testing Checklist**:

1. **Core Functionality** (Run on every release):
   - Basic form submission works
   - Validation errors display correctly
   - Required fields enforced
   - Form submission success handling

2. **Multi-Page Wizard Regression** (Run on wizard-related changes):
   - Step navigation works
   - Data persists between steps
   - Draft save/load works
   - Browser back button works
   - Conditional steps display correctly

3. **Browser Compatibility** (Run periodically, before major releases):
   - Test in all supported browsers
   - Test on mobile devices
   - Test with assistive technologies (screen readers)

4. **Integration Regression** (Run when backend changes):
   - Form submission to API works
   - Validation error responses handled correctly
   - File uploads work
   - Draft persistence API works

### Defect Patterns

**Common Form Defects to Watch For**:

1. **Validation Issues**:
   - Errors shown before user interacts with field
   - Errors not cleared when field becomes valid
   - Server validation errors not displayed to user
   - Async validation shows stale results

2. **State Management Issues**:
   - Form data lost on page refresh
   - Multi-page wizard loses data on browser back
   - Draft not loading correctly
   - Form state conflicts between tabs

3. **UX Issues**:
   - Submit button doesn't show loading state
   - No feedback during async validation
   - Error messages not accessible (no ARIA)
   - Focus not managed correctly (doesn't move to errors)

4. **Multi-Page Wizard Specific**:
   - Progress indicator incorrect
   - Can navigate to invalid steps
   - Conditional steps show when they shouldn't
   - Review step shows incorrect data

5. **Accessibility Issues**:
   - Labels not associated with inputs
   - Errors not announced to screen readers
   - Keyboard navigation broken
   - Focus traps or focus loss

**Defect Reporting Template for Forms**:
- Form name and step (if multi-page)
- Field name and type
- Expected behavior
- Actual behavior
- Steps to reproduce
- Browser/device
- Screenshots/videos
- Console errors (if any)
- Network requests (if relevant)
