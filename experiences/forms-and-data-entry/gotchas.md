# Gotchas: Forms and Data Entry

## Contents

- [Premature Validation on Blur](#premature-validation-on-blur)
- [Loss of Form State on Accidental Navigation](#loss-of-form-state-on-accidental-navigation)
- [Timezone/Locale Issues in Date Inputs](#timezonelocale-issues-in-date-inputs)
- [File Upload Size Limits Failing Silently](#file-upload-size-limits-failing-silently)
- [Wizard Point of No Return Confusion](#wizard-point-of-no-return-confusion)
- [Back Button Breaking Wizard Step State](#back-button-breaking-wizard-step-state)
- [Draft Data Going Stale](#draft-data-going-stale)
- [Autofill Fighting with Custom Input Components](#autofill-fighting-with-custom-input-components)
- [Double Submission on Slow Networks](#double-submission-on-slow-networks)
- [Validation Messages Not Announced to Screen Readers](#validation-messages-not-announced-to-screen-readers)

## Premature Validation on Blur

**Problem**: Validating immediately on blur before user finishes typing can show errors while they're still editing.

**Example**:
```typescript
// ❌ Bad: Validates immediately on blur
<input 
  onBlur={() => validateField('email')}  // User might still be editing
/>

// ✅ Good: Small delay or validate only after user has left field for a moment
<input 
  onBlur={() => {
    setTimeout(() => validateField('email'), 100); // Small delay
  }}
/>
```

**Better Solution**: Only validate on blur after first submission attempt, or use debouncing.

## Loss of Form State on Accidental Navigation

**Problem**: User fills long form, accidentally clicks link or presses back button, loses all data.

**Solutions**:
1. **Warn Before Navigation**:
```typescript
useEffect(() => {
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = 'You have unsaved changes. Are you sure?';
    }
  };
  window.addEventListener('beforeunload', handleBeforeUnload);
  return () => window.removeEventListener('beforeunload', handleBeforeUnload);
}, [hasUnsavedChanges]);
```

2. **Autosave Drafts**:
```typescript
// Autosave to localStorage or server
useEffect(() => {
  const timer = setTimeout(() => {
    saveDraft(formData);
  }, 500); // Debounce
  return () => clearTimeout(timer);
}, [formData]);
```

3. **Use Controlled Navigation**:
```typescript
// Intercept navigation attempts
const handleLinkClick = (e: MouseEvent) => {
  if (hasUnsavedChanges) {
    e.preventDefault();
    if (confirm('You have unsaved changes. Leave anyway?')) {
      // Clear form state, then navigate
      navigate(targetUrl);
    }
  }
};
```

## Timezone/Locale Issues in Date Inputs

**Problem**: Date inputs can cause confusion with timezones and locales.

**Issues**:
- Date picker shows local time, but server expects UTC
- Date format differs by locale (MM/DD/YYYY vs DD/MM/YYYY)
- Date-only inputs include time component unexpectedly

**Solutions**:
1. **Always Send Dates as ISO Strings**:
```typescript
// ✅ Good: Send ISO string
const dateValue = dateInput.value; // "2026-02-09"
const isoString = new Date(dateValue).toISOString(); // "2026-02-09T00:00:00.000Z"
```

2. **Handle Timezone Explicitly**:
```typescript
// For date-only fields, use date at midnight UTC
const dateOnly = new Date(dateInput.value + 'T00:00:00Z');
```

3. **Use Consistent Format**:
```typescript
// Always use YYYY-MM-DD format for date inputs
<input type="date" /> // Browser handles locale, but value is always YYYY-MM-DD
```

4. **Backend Handling** (Spring Boot):
```kotlin
// Parse date as local date (no time component)
@JsonFormat(pattern = "yyyy-MM-dd")
val birthDate: LocalDate
```

## File Upload Size Limits Failing Silently

**Problem**: User selects large file, upload appears to work but fails silently on server.

**Issues**:
- No client-side size check before upload starts
- Server rejects but doesn't communicate error clearly
- Upload progress shows 100% then fails

**Solutions**:
1. **Validate File Size Client-Side**:
```typescript
const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;
  
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    setError(`File size must be less than ${maxSize / 1024 / 1024}MB`);
    e.target.value = ''; // Clear selection
    return;
  }
  
  // Proceed with upload
};
```

2. **Show Clear Error Messages**:
```typescript
try {
  await uploadFile(file);
} catch (error) {
  if (error.status === 413) { // Payload Too Large
    setError(`File is too large. Maximum size is ${maxSize}MB.`);
  } else {
    setError('Upload failed. Please try again.');
  }
}
```

3. **Validate on Server and Return Clear Errors**:
```kotlin
@PostMapping("/upload")
fun uploadFile(@RequestParam file: MultipartFile): ResponseEntity<*> {
    val maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        return ResponseEntity
            .status(HttpStatus.PAYLOAD_TOO_LARGE)
            .body(ErrorResponse("File size exceeds maximum of 10MB"))
    }
    // Process file
}
```

## Wizard Point of No Return Confusion

**Problem**: Users don't understand what happens when they go back in a wizard, or if they can change previous answers.

**Issues**:
- Users think going back will lose their data
- Users don't know if they can edit previous steps
- No clear indication of what's been "committed" vs "draft"

**Solutions**:
1. **Clear Navigation Labels**:
```tsx
// ✅ Good: Clear labels
<button onClick={handleBack}>← Back to Payment</button>
<button onClick={handleNext}>Continue to Review →</button>

// ❌ Bad: Vague labels
<button onClick={handleBack}>Back</button>
<button onClick={handleNext}>Next</button>
```

2. **Show Data Can Be Edited**:
```tsx
// On review step, show edit buttons
<Section title="Payment Information">
  <p>{paymentInfo.cardLast4}</p>
  <button onClick={() => navigateToStep(2)}>Edit Payment</button>
</Section>
```

3. **Indicate Draft vs Committed State**:
```tsx
// Show which steps are "saved" vs "draft"
<StepIndicator>
  <Step status="saved">Personal Info ✓</Step>
  <Step status="saved">Payment ✓</Step>
  <Step status="draft">Shipping (draft)</Step>
</StepIndicator>
```

4. **Confirmation for Destructive Actions**:
```typescript
// If going back might lose data (e.g., payment processed), confirm
const handleBack = () => {
  if (hasProcessedPayment) {
    if (!confirm('Going back will cancel your payment. Continue?')) {
      return;
    }
  }
  navigateToPreviousStep();
};
```

## Back Button Breaking Wizard Step State

**Problem**: Browser back button breaks wizard state, either going too far back or not updating form state correctly.

**Issues**:
- Wizard uses internal state, browser back goes to previous route entirely
- Step state doesn't sync with URL
- Form data lost when using browser back

**Solutions**:
1. **Use URL-Driven Routing** (Best Solution):
```typescript
// Each step has its own route
/wizard/step-1
/wizard/step-2
/wizard/review

// Browser back/forward works naturally
function WizardStep() {
  const { stepId } = useParams();
  const navigate = useNavigate();
  
  // Step state synced with URL
  useEffect(() => {
    loadStepData(stepId);
  }, [stepId]);
}
```

2. **Handle PopState Events**:
```typescript
useEffect(() => {
  const handlePopState = () => {
    const targetStep = getStepFromUrl();
    loadStepData(targetStep);
  };
  window.addEventListener('popstate', handlePopState);
  return () => window.removeEventListener('popstate', handlePopState);
}, []);
```

3. **Persist Form Data**:
```typescript
// Save form data to sessionStorage or server before navigation
const navigateToStep = (stepId: string) => {
  saveFormData(formData); // Persist before navigation
  navigate(`/wizard/${stepId}`);
};
```

## Draft Data Going Stale

**Problem**: User saves draft, returns days later, but related data has changed (e.g., product prices, availability).

**Issues**:
- Draft contains outdated prices
- Draft references deleted items
- Draft uses old validation rules

**Solutions**:
1. **Validate Draft on Load**:
```typescript
async function loadDraft(draftId: string) {
  const draft = await fetchDraft(draftId);
  
  // Validate draft data against current state
  const validation = await validateDraftData(draft.data);
  if (!validation.valid) {
    showWarning('Some items in your draft are no longer available.');
    // Show which items are invalid
    setInvalidItems(validation.invalidItems);
  }
  
  return draft;
}
```

2. **Expire Drafts**:
```typescript
// Server-side: Expire drafts after 7 days
@Entity
data class FormDraft(
    val expiresAt: Instant = Instant.now().plusDays(7)
)

// Client-side: Check expiry
if (draft.expiresAt < Date.now()) {
  showMessage('Your draft has expired. Please start over.');
  deleteDraft(draftId);
}
```

3. **Show Draft Age**:
```tsx
// Show when draft was saved
<div className="draft-info">
  <p>You have a saved draft from {formatDate(draft.savedAt)}</p>
  <button onClick={loadDraft}>Resume</button>
  <button onClick={startFresh}>Start Fresh</button>
</div>
```

4. **Refresh Related Data**:
```typescript
// When loading draft, refresh related data (prices, availability)
async function loadDraftWithFreshData(draftId: string) {
  const draft = await loadDraft(draftId);
  const freshData = await fetchCurrentPrices(draft.productIds);
  
  // Merge draft with fresh data
  return mergeDraftWithFreshData(draft, freshData);
}
```

## Autofill Fighting with Custom Input Components

**Problem**: Custom-styled input components (e.g., custom date pickers, styled selects) don't work well with browser autofill.

**Issues**:
- Browser autofill doesn't recognize custom components
- Autofill styling conflicts with custom styles
- Autofill data doesn't populate custom components

**Solutions**:
1. **Use Native Inputs When Possible**:
```tsx
// ✅ Good: Use native input, style with CSS
<input 
  type="email"
  className="styled-input"  // Style with CSS, not custom component
  autoComplete="email"
/>

// ❌ Bad: Custom component wrapper that breaks autofill
<CustomEmailInput />  // Browser can't autofill this
```

2. **Preserve Autocomplete Attributes**:
```tsx
// If using custom component, ensure autocomplete passes through
function CustomInput({ autoComplete, ...props }) {
  return (
    <div className="custom-input-wrapper">
      <input 
        {...props}
        autoComplete={autoComplete}  // Preserve autocomplete
      />
    </div>
  );
}
```

3. **Handle Autofill Events**:
```typescript
// Listen for autofill and update component state
useEffect(() => {
  const handleAnimationStart = (e: AnimationEvent) => {
    // Browser autofill triggers animation
    if (e.animationName === 'onAutoFillStart') {
      setAutofilled(true);
      // Update component state with autofilled value
    }
  };
  
  inputRef.current?.addEventListener('animationstart', handleAnimationStart);
  return () => inputRef.current?.removeEventListener('animationstart', handleAnimationStart);
}, []);
```

4. **Test with Real Autofill**:
- Test forms with browser autofill enabled
- Test with password managers (LastPass, 1Password, etc.)
- Test on mobile devices (iOS/Android autofill)

## Double Submission on Slow Networks

**Problem**: User clicks submit button multiple times on slow network, causing duplicate submissions.

**Issues**:
- No visual feedback that submission is in progress
- Submit button not disabled during submission
- Server processes multiple identical requests

**Solutions**:
1. **Disable Submit Button During Submission**:
```tsx
const [isSubmitting, setIsSubmitting] = useState(false);

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  if (isSubmitting) return; // Prevent double submission
  
  setIsSubmitting(true);
  try {
    await submitForm(formData);
  } finally {
    setIsSubmitting(false);
  }
};

<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? 'Submitting...' : 'Submit'}
</button>
```

2. **Show Loading State**:
```tsx
{isSubmitting && (
  <div className="submitting-indicator">
    <Spinner />
    <span>Submitting...</span>
  </div>
)}
```

3. **Idempotent Submissions** (Server-Side):
```kotlin
// Use idempotency keys to prevent duplicate processing
@PostMapping("/orders")
fun createOrder(
    @RequestHeader("Idempotency-Key") idempotencyKey: String?,
    @RequestBody request: CreateOrderRequest
): ResponseEntity<*> {
    // Check if request with this key was already processed
    val existingOrder = orderRepository.findByIdempotencyKey(idempotencyKey)
    if (existingOrder != null) {
        return ResponseEntity.ok(existingOrder) // Return existing result
    }
    
    // Process new order
    val order = orderService.createOrder(request, idempotencyKey)
    return ResponseEntity.ok(order)
}
```

4. **Debounce Submit Handler**:
```typescript
const debouncedSubmit = useMemo(
  () => debounce(handleSubmit, 1000, { leading: true, trailing: false }),
  []
);
```

## Validation Messages Not Announced to Screen Readers

**Problem**: Validation errors appear visually but aren't announced to screen reader users.

**Issues**:
- Errors shown but no ARIA attributes
- Errors not associated with input fields
- Dynamic error insertion not announced

**Solutions**:
1. **Use ARIA Attributes**:
```tsx
<input 
  id="email"
  name="email"
  aria-invalid={!!errors.email}  // Mark as invalid
  aria-describedby={errors.email ? "email-error" : undefined}  // Link to error
/>
{errors.email && (
  <span id="email-error" role="alert" className="error">
    {errors.email}
  </span>
)}
```

2. **Use role="alert"**:
```tsx
// role="alert" causes screen reader to announce immediately
{errors.email && (
  <div role="alert" id="email-error">
    {errors.email}
  </div>
)}
```

3. **Live Regions for Dynamic Updates**:
```tsx
// Use aria-live for dynamic error updates
<div aria-live="polite" aria-atomic="true">
  {errors.email && <span>{errors.email}</span>}
</div>
```

4. **Focus Management**:
```typescript
// Move focus to first error on submit
useEffect(() => {
  if (Object.keys(errors).length > 0) {
    const firstErrorField = formRef.current?.querySelector('[aria-invalid="true"]');
    if (firstErrorField) {
      (firstErrorField as HTMLElement).focus();
    }
  }
}, [errors]);
```

5. **Test with Screen Readers**:
- Test with NVDA (Windows), JAWS (Windows), VoiceOver (Mac/iOS)
- Verify errors are announced
- Verify focus moves to errors
- Verify error messages are clear and actionable
