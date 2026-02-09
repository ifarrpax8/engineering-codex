# Best Practices: Forms and Data Entry

## Contents

- [Inline Validation Timing](#inline-validation-timing)
- [Error Message Clarity](#error-message-clarity)
- [Progressive Disclosure](#progressive-disclosure)
- [Sensible Defaults and Smart Placeholders](#sensible-defaults-and-smart-placeholders)
- [Mobile Input Types](#mobile-input-types)
- [Multi-Page Form Best Practices](#multi-page-form-best-practices)
- [Stack-Specific Callouts](#stack-specific-callouts)
- [Accessibility in Forms](#accessibility-in-forms)

## Inline Validation Timing

Validation timing significantly impacts user experience. Get it wrong, and users feel frustrated or confused.

### Validate on Blur, Not on Keystroke

**Why**: Validating on every keystroke interrupts the user's flow and shows errors before they finish typing.

**Good Practice**:
```typescript
// React Hook Form example
const { register, formState: { errors } } = useForm({
  mode: 'onBlur' // Validate when user leaves field
});

<input 
  {...register('email', { 
    required: 'Email is required',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Invalid email address'
    }
  })}
/>
```

**Exception**: Format validation (like email format or password strength) can show helpful hints as user types, but don't show errors until blur.

### Show Errors After First Submission Attempt

**Why**: Don't overwhelm users with errors before they've tried to submit.

**Pattern**:
1. User fills form, no errors shown
2. User clicks submit
3. If validation fails, show all errors
4. As user fixes errors, clear them immediately (validate on blur after first submit attempt)

**Implementation**:
```typescript
const [submitted, setSubmitted] = useState(false);

const handleSubmit = async (e) => {
  e.preventDefault();
  setSubmitted(true);
  
  const errors = validateForm(formData);
  if (Object.keys(errors).length > 0) {
    setFormErrors(errors);
    return;
  }
  
  // Submit form
};

// Show errors only after submission attempt
{submitted && errors.email && (
  <span className="error">{errors.email}</span>
)}
```

### Progressive Error Display

**Pattern**:
- **Before submit**: No errors shown (or only format hints)
- **After submit attempt**: Show all validation errors
- **While fixing**: Clear errors immediately when field becomes valid (validate on blur)

## Error Message Clarity

Error messages must be specific, actionable, and positioned correctly.

### Be Specific and Actionable

**Bad Examples**:
- "Invalid input"
- "Error"
- "This field is required"

**Good Examples**:
- "Email address must include @ symbol"
- "Password must be at least 8 characters and include one number"
- "Age must be 18 or older to create an account"

**Implementation**:
```typescript
const validationMessages = {
  email: {
    required: 'Email address is required',
    pattern: 'Please enter a valid email address (e.g., name@example.com)',
    unique: 'This email address is already registered'
  },
  password: {
    required: 'Password is required',
    minLength: 'Password must be at least 8 characters',
    pattern: 'Password must include at least one number and one uppercase letter'
  }
};
```

### Position Errors Near the Field

**Best Practice**: Show error message directly below or adjacent to the field, not in a list at the top.

**Visual Pattern**:
```
Email Address *
[________________]  ← Input field
⚠ Invalid email format  ← Error directly below
```

**Implementation**:
```tsx
<div className="form-field">
  <label htmlFor="email">Email Address</label>
  <input 
    id="email"
    name="email"
    aria-invalid={!!errors.email}
    aria-describedby={errors.email ? "email-error" : undefined}
  />
  {errors.email && (
    <span id="email-error" className="error" role="alert">
      {errors.email}
    </span>
  )}
</div>
```

### Use Icons and Color Consistently

- Use error icon (⚠️ or ❌) consistently
- Use consistent error color (typically red)
- Ensure sufficient color contrast for accessibility
- Don't rely solely on color (include icon or text)

## Progressive Disclosure

Don't overwhelm users with all fields at once. Show fields as needed.

### Collapsible Sections

For forms with logical groupings, use collapsible sections:

```tsx
<Accordion>
  <AccordionItem title="Personal Information" defaultOpen>
    <NameField />
    <EmailField />
  </AccordionItem>
  <AccordionItem title="Address Information">
    <StreetField />
    <CityField />
  </AccordionItem>
  <AccordionItem title="Preferences (Optional)">
    <NewsletterField />
    <NotificationsField />
  </AccordionItem>
</Accordion>
```

### Conditional Fields

Show fields only when relevant:

```tsx
{accountType === 'business' && (
  <>
    <CompanyNameField />
    <TaxIdField />
  </>
)}
```

### Multi-Step Forms

For complex forms, split into logical steps (see Multi-Page Form Best Practices section).

## Sensible Defaults and Smart Placeholders

Help users complete forms faster with good defaults and helpful placeholders.

### Sensible Defaults

**When to Use Defaults**:
- Pre-fill based on user's previous inputs or profile
- Use most common option as default
- Pre-select "No" for opt-in checkboxes (privacy best practice)

**Examples**:
```tsx
// Pre-fill country based on user's location
<Select name="country" defaultValue={userLocation.country}>
  {/* options */}
</Select>

// Pre-select most common option
<Select name="plan" defaultValue="standard">
  <option value="basic">Basic</option>
  <option value="standard">Standard</option>
  <option value="premium">Premium</option>
</Select>
```

### Smart Placeholders

**Use Placeholders For**:
- Format examples: `name@example.com`
- Hints: `Enter your 10-digit phone number`
- Examples: `e.g., John Doe`

**Don't Use Placeholders For**:
- Field labels (use `<label>` instead)
- Required field indicators (use asterisk or "required" text)
- Instructions (use help text below field)

**Best Practice**:
```tsx
<label htmlFor="phone">Phone Number</label>
<input 
  id="phone"
  name="phone"
  placeholder="(555) 123-4567"
  aria-describedby="phone-help"
/>
<span id="phone-help" className="help-text">
  Include area code
</span>
```

## Mobile Input Types

Use appropriate input types and attributes for mobile devices.

### Input Types

**Use Semantic Input Types**:
```tsx
<input type="email" />      // Shows email keyboard
<input type="tel" />        // Shows numeric keyboard
<input type="number" />     // Shows numeric keyboard
<input type="date" />       // Shows date picker
<input type="url" />        // Shows URL keyboard
<input type="search" />     // Shows search keyboard
```

### Inputmode Attribute

**For Fine-Grained Control**:
```tsx
<input 
  type="text"
  inputMode="numeric"     // Numeric keyboard (no decimals)
  pattern="[0-9]*"
/>

<input 
  type="text"
  inputMode="decimal"     // Numeric keyboard with decimal
/>

<input 
  type="text"
  inputMode="tel"         // Phone number keyboard
/>
```

### Autocomplete Attributes

**Help Browser Autofill**:
```tsx
<input 
  type="text"
  name="full-name"
  autoComplete="name"           // Full name
/>

<input 
  type="email"
  autoComplete="email"          // Email address
/>

<input 
  type="tel"
  autoComplete="tel"            // Phone number
/>

<input 
  type="text"
  autoComplete="address-line1"  // Street address
/>

<input 
  type="text"
  autoComplete="address-line2"  // Apartment, suite, etc.
/>

<input 
  type="text"
  autoComplete="address-level2" // City
/>

<input 
  type="text"
  autoComplete="address-level1" // State/Province
/>

<input 
  type="text"
  autoComplete="postal-code"    // ZIP/Postal code
/>

<input 
  type="text"
  autoComplete="country"        // Country
/>
```

**Complete List**: See [MDN autocomplete values](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete)

## Multi-Page Form Best Practices

Multi-page wizard forms require special attention to UX and state management.

### Validate Per-Step, Not Just on Submit

**Why**: Catch errors early, don't make users fill entire form only to find error on step 1.

**Pattern**:
```typescript
function validateStep(step: number, data: FormData): ValidationResult {
  switch(step) {
    case 1:
      return validatePersonalInfo(data);
    case 2:
      return validatePayment(data);
    case 3:
      return validateShipping(data);
    default:
      return { valid: true };
  }
}

// Before allowing next step
const validation = validateStep(currentStep, formData);
if (!validation.valid) {
  setStepErrors(validation.errors);
  return; // Don't advance
}
navigateToNextStep();
```

### Show Progress Clearly

**Always Include**:
- Step indicator: "Step 2 of 4"
- Progress bar showing completion percentage
- Step labels (not just numbers): "Personal Info → Payment → Review"

**Visual Example**:
```
[████████░░░░░░░░] 50% Complete

✓ Personal Information
→ Payment Details        ← Current step
  Shipping Address
  Review & Submit
```

**Implementation**:
```tsx
function StepIndicator({ currentStep, totalSteps, stepLabels }) {
  return (
    <div className="step-indicator">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>
      <div className="step-labels">
        {stepLabels.map((label, index) => (
          <span 
            key={index}
            className={index < currentStep ? 'completed' : 
                      index === currentStep ? 'current' : 'upcoming'}
          >
            {index + 1}. {label}
          </span>
        ))}
      </div>
    </div>
  );
}
```

### Allow Non-Linear Navigation Where Possible

**Pattern**: Let users jump to specific steps if they need to edit, not just forward/back.

**Implementation**:
- Show step list/navigation menu
- Allow clicking on completed steps to edit
- Disable future steps until current step is valid

```tsx
function StepNavigation({ steps, currentStep, onStepClick }) {
  return (
    <nav>
      {steps.map((step, index) => (
        <button
          key={index}
          onClick={() => onStepClick(index)}
          disabled={index > currentStep && !isStepValid(currentStep)}
          className={index === currentStep ? 'current' : ''}
        >
          {step.label}
        </button>
      ))}
    </nav>
  );
}
```

### Persist Drafts

**For Forms Taking >5 Minutes**:
- Implement autosave (debounced, every 30-60 seconds)
- Or provide explicit "Save Draft" button
- Show clear indication when draft exists
- Send email with resume link if user abandons

**Implementation** (see Architecture.md for detailed patterns):
```typescript
// Autosave on step completion
useEffect(() => {
  if (formData && currentStep > 0) {
    const timer = setTimeout(() => {
      saveDraft(formData, currentStep);
    }, 500); // Debounce
    
    return () => clearTimeout(timer);
  }
}, [formData, currentStep]);
```

### Handle Session Expiry Mid-Form

**Problem**: User fills form for 10 minutes, session expires, they submit and lose everything.

**Solutions**:
1. **Extend Session on Activity**: Refresh session token on form interactions
2. **Warn Before Expiry**: Show warning 2 minutes before session expires
3. **Save Draft on Expiry**: Automatically save draft when session expires
4. **Graceful Recovery**: After re-authentication, restore draft or allow resume

```typescript
// Check session expiry periodically
useEffect(() => {
  const interval = setInterval(async () => {
    const timeUntilExpiry = await checkSessionExpiry();
    if (timeUntilExpiry < 120000) { // 2 minutes
      showSessionWarning(timeUntilExpiry);
    }
  }, 60000); // Check every minute
  
  return () => clearInterval(interval);
}, []);
```

### Review Step Before Submission

**Always Include Review Step**:
- Show all entered data in readable format
- Allow editing (click to go back to specific step)
- Highlight any incomplete or invalid sections
- Show final submission button clearly

```tsx
function ReviewStep({ formData, onEditStep, onSubmit }) {
  return (
    <div className="review-step">
      <h2>Review Your Information</h2>
      
      <Section title="Personal Information">
        <p>{formData.name}</p>
        <p>{formData.email}</p>
        <button onClick={() => onEditStep(1)}>Edit</button>
      </Section>
      
      <Section title="Payment">
        <p>Card ending in {formData.cardLast4}</p>
        <button onClick={() => onEditStep(2)}>Edit</button>
      </Section>
      
      <button onClick={onSubmit} className="submit-button">
        Submit Order
      </button>
    </div>
  );
}
```

## Stack-Specific Callouts

### Vue 3

**VeeValidate** (Recommended):
```vue
<script setup>
import { useForm } from 'vee-validate';
import * as yup from 'yup';

const schema = yup.object({
  email: yup.string().email().required(),
  password: yup.string().min(8).required(),
});

const { handleSubmit, defineField } = useForm({
  validationSchema: schema,
});

const [email, emailAttrs] = defineField('email');
const [password, passwordAttrs] = defineField('password');

const onSubmit = handleSubmit((values) => {
  // Submit form
});
</script>

<template>
  <form @submit="onSubmit">
    <input v-model="email" v-bind="emailAttrs" />
    <span>{{ emailAttrs.errors }}</span>
    
    <input v-model="password" v-bind="passwordAttrs" type="password" />
    <span>{{ passwordAttrs.errors }}</span>
    
    <button type="submit">Submit</button>
  </form>
</template>
```

**FormKit** (Alternative, schema-driven):
```vue
<FormKit
  type="form"
  @submit="handleSubmit"
>
  <FormKit
    type="email"
    name="email"
    label="Email"
    validation="required|email"
  />
  <FormKit
    type="password"
    name="password"
    label="Password"
    validation="required|length:8"
  />
</FormKit>
```

### React

**React Hook Form** (Recommended):
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur',
  });
  
  const onSubmit = (data) => {
    console.log(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      
      <input {...register('password')} type="password" />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

**Formik** (Alternative, more verbose but flexible):
```tsx
import { useFormik } from 'formik';
import * as yup from 'yup';

const validationSchema = yup.object({
  email: yup.string().email().required(),
  password: yup.string().min(8).required(),
});

function MyForm() {
  const formik = useFormik({
    initialValues: { email: '', password: '' },
    validationSchema,
    onSubmit: (values) => {
      // Submit
    },
  });
  
  return (
    <form onSubmit={formik.handleSubmit}>
      <input
        name="email"
        value={formik.values.email}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
      />
      {formik.touched.email && formik.errors.email && (
        <span>{formik.errors.email}</span>
      )}
      {/* ... */}
    </form>
  );
}
```

### Validation Libraries

**Zod** (TypeScript-first, recommended):
- Type-safe schemas
- Great TypeScript inference
- Composable and powerful

**Yup** (JavaScript/TypeScript, widely adopted):
- Mature, stable
- Good documentation
- Works well with Formik

**Valibot** (Lightweight alternative):
- Smaller bundle size
- Similar API to Zod
- Good for bundle-size-conscious projects

### Spring Boot

**Bean Validation**:
```kotlin
data class CreateUserRequest(
    @field:NotBlank(message = "Email is required")
    @field:Email(message = "Invalid email format")
    val email: String,
    
    @field:Size(min = 8, message = "Password must be at least 8 characters")
    val password: String
)

@PostMapping("/users")
fun createUser(@Valid @RequestBody request: CreateUserRequest): ResponseEntity<*> {
    // Request validated automatically
}
```

**Custom ConstraintValidator**:
```kotlin
@Target(AnnotationTarget.FIELD)
@Retention(AnnotationRetention.RUNTIME)
@Constraint(validatedBy = [StrongPasswordValidator::class])
annotation class StrongPassword(val message: String = "Password is too weak")

class StrongPasswordValidator : ConstraintValidator<StrongPassword, String> {
    override fun isValid(password: String?, context: ConstraintValidatorContext?): Boolean {
        // Validation logic
    }
}
```

**BindingResult for Custom Error Handling**:
```kotlin
@PostMapping("/users")
fun createUser(
    @Valid @RequestBody request: CreateUserRequest,
    bindingResult: BindingResult
): ResponseEntity<*> {
    if (bindingResult.hasErrors()) {
        val errors = bindingResult.fieldErrors.associate { 
            it.field to it.defaultMessage 
        }
        return ResponseEntity.badRequest().body(ErrorResponse(errors))
    }
    // Process
}
```

## Accessibility in Forms

Forms must be accessible to all users, including those using assistive technologies.

### Labels

**Always Associate Labels with Inputs**:
```tsx
// Explicit association
<label htmlFor="email">Email Address</label>
<input id="email" name="email" />

// Or implicit (label wraps input)
<label>
  Email Address
  <input name="email" />
</label>
```

**Don't Use Placeholders as Labels**:
```tsx
// ❌ Bad
<input placeholder="Email Address" />

// ✅ Good
<label htmlFor="email">Email Address</label>
<input id="email" name="email" />
```

### Fieldsets and Legends

**Group Related Fields**:
```tsx
<fieldset>
  <legend>Shipping Address</legend>
  <input name="street" />
  <input name="city" />
  <input name="zip" />
</fieldset>
```

### Error Announcements

**Associate Errors with Fields**:
```tsx
<input 
  id="email"
  name="email"
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? "email-error" : undefined}
/>
{errors.email && (
  <span id="email-error" role="alert" className="error">
    {errors.email}
  </span>
)}
```

**Key Attributes**:
- `aria-invalid="true"` on input when error exists
- `aria-describedby` pointing to error message element
- `role="alert"` on error message (announces to screen readers)

### Required Fields

**Indicate Required Fields**:
```tsx
<label htmlFor="email">
  Email Address <span aria-label="required">*</span>
</label>
<input 
  id="email"
  name="email"
  required
  aria-required="true"
/>
```

### Keyboard Navigation

**Ensure Keyboard Accessibility**:
- All form fields must be focusable with Tab
- Submit buttons must be activatable with Enter/Space
- Error messages must be focusable or announced
- Focus management: Move focus to first error on submit failure

```tsx
// Focus first error on submit
const firstErrorField = formRef.current?.querySelector('[aria-invalid="true"]');
if (firstErrorField) {
  (firstErrorField as HTMLElement).focus();
}
```

### Design System Integration

**Propulsion/MUI Components**:
- Use design system form components (they include accessibility by default)
- Ensure custom form components follow same patterns
- Test with screen readers (NVDA, JAWS, VoiceOver)
