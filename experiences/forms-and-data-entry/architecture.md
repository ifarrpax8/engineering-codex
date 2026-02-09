# Forms & Data Entry — Architecture

## Contents
- [Form State Management](#form-state-management)
- [Validation Architecture](#validation-architecture)
- [Multi-Page/Wizard Forms](#multi-pagewizard-forms)
- [Autosave Patterns](#autosave-patterns)
- [Schema-Driven Forms](#schema-driven-forms)
- [File Upload Architecture](#file-upload-architecture)
- [Server-Side Form Handling](#server-side-form-handling)
- [Integration Points](#integration-points)

## Form State Management

Form state management is fundamental to building robust data entry experiences. The choice between controlled and uncontrolled components affects validation timing, performance, and user experience.

### Controlled Components

Controlled components store form state in component state (or a store) and update it through event handlers. Every keystroke triggers a state update.

**React Example:**
```tsx
const [formData, setFormData] = useState({
  email: '',
  name: ''
});

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setFormData(prev => ({
    ...prev,
    [e.target.name]: e.target.value
  }));
};

<input
  name="email"
  value={formData.email}
  onChange={handleChange}
/>
```

**Vue 3 Example:**
```vue
<script setup>
import { ref } from 'vue';

const formData = ref({
  email: '',
  name: ''
});
</script>

<template>
  <input v-model="formData.email" />
</template>
```

**When to Use Controlled:**
- Immediate validation feedback required
- Form state needs to be shared across components
- Complex validation logic depends on multiple fields
- Form state must be accessible for programmatic manipulation
- Integration with form libraries (React Hook Form, VeeValidate)

### Uncontrolled Components

Uncontrolled components rely on the DOM to manage form state, accessing values via refs when needed.

**React Example:**
```tsx
const emailRef = useRef<HTMLInputElement>(null);

const handleSubmit = () => {
  const email = emailRef.current?.value;
  // Process form data
};

<input ref={emailRef} name="email" />
```

**Vue 3 Example:**
```vue
<script setup>
import { ref } from 'vue';

const emailInput = ref<HTMLInputElement | null>(null);

const handleSubmit = () => {
  const email = emailInput.value?.value;
};
</script>

<template>
  <input ref="emailInput" />
</template>
```

**When to Use Uncontrolled:**
- Simple forms with minimal validation
- Performance-critical scenarios (fewer re-renders)
- File inputs (must be uncontrolled)
- Integration with native HTML5 validation
- Forms that don't need real-time state synchronization

### Hybrid Approach

Many modern form libraries use a hybrid approach: uncontrolled DOM elements with controlled validation state.

**React Hook Form Example:**
```tsx
const { register, handleSubmit, formState: { errors } } = useForm();

<input {...register('email', { required: true })} />
{errors.email && <span>Email is required</span>}
```

## Validation Architecture

Validation must occur at multiple layers: client-side for immediate feedback, server-side for security and data integrity, and async validation for checks requiring server resources.

### Client-Side Validation

Client-side validation provides immediate feedback without server round-trips. Use for:
- Required field checks
- Format validation (email, phone, URL)
- Length constraints
- Basic business rules (e.g., end date after start date)

**React with Zod:**
```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  email: z.string().email('Invalid email'),
  age: z.number().min(18, 'Must be 18+')
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema)
});
```

**Vue 3 with VeeValidate:**
```vue
<script setup>
import { useForm } from 'vee-validate';
import * as yup from 'yup';

const schema = yup.object({
  email: yup.string().email().required(),
  age: yup.number().min(18)
});

const { defineField, errors } = useForm({ validationSchema: schema });
const [email] = defineField('email');
</script>
```

### Server-Side Validation

Server-side validation is mandatory for security. Never trust client-side validation alone.

**Spring Boot with Bean Validation:**
```java
@PostMapping("/users")
public ResponseEntity<?> createUser(@Valid @RequestBody UserCreateRequest request) {
    // Request is validated before reaching this method
    return ResponseEntity.ok(userService.create(request));
}

public class UserCreateRequest {
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;
    
    @NotNull
    @Min(value = 18, message = "Must be 18 or older")
    private Integer age;
}
```

**Error Response Format (RFC 7807):**
```java
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ProblemDetail> handleValidationErrors(
    MethodArgumentNotValidException ex) {
    
    ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
    problem.setTitle("Validation Error");
    
    Map<String, String> errors = ex.getBindingResult()
        .getFieldErrors()
        .stream()
        .collect(Collectors.toMap(
            FieldError::getField,
            FieldError::getDefaultMessage,
            (first, second) -> first
        ));
    
    problem.setProperty("errors", errors);
    return ResponseEntity.badRequest().body(problem);
}
```

**Frontend Error Handling:**
```typescript
interface ValidationError {
  type: string;
  title: string;
  status: number;
  errors: Record<string, string>;
}

const handleSubmit = async (data: FormData) => {
  try {
    await api.post('/users', data);
  } catch (error) {
    if (error.response?.status === 400) {
      const validationError: ValidationError = error.response.data;
      // Map errors to form fields
      Object.entries(validationError.errors).forEach(([field, message]) => {
        setError(field, { message });
      });
    }
  }
};
```

### Async Validation

Async validation checks values against server resources (e.g., unique email, available username).

**React Example:**
```tsx
const validateEmailUnique = async (email: string) => {
  const response = await fetch(`/api/users/check-email?email=${email}`);
  const { available } = await response.json();
  return available || 'Email already taken';
};

const { register } = useForm({
  resolver: zodResolver(schema.extend({
    email: z.string().email().refine(validateEmailUnique)
  }))
});
```

**Vue 3 Example:**
```vue
<script setup>
const validateEmail = async (value: string) => {
  const response = await fetch(`/api/users/check-email?email=${value}`);
  const { available } = await response.json();
  return available || 'Email already taken';
};
</script>
```

### Validation Schema Sharing

Share validation schemas between frontend and backend to ensure consistency.

**Approach 1: JSON Schema**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    }
  }
}
```

**Approach 2: Code Generation**
- Generate TypeScript types from OpenAPI spec
- Use Ajv (JavaScript) or similar to validate against JSON Schema
- Spring Boot can use JSON Schema for validation with libraries like `networknt/json-schema-validator`

## Multi-Page/Wizard Forms

Multi-page forms break complex data entry into manageable steps, improving completion rates and user experience.

### Step State Management

**Store-Based Approach (Vue 3 with Pinia):**
```typescript
// stores/wizard.ts
import { defineStore } from 'pinia';

export const useWizardStore = defineStore('wizard', {
  state: () => ({
    currentStep: 1,
    totalSteps: 4,
    formData: {
      step1: {},
      step2: {},
      step3: {},
      step4: {}
    },
    validationState: {} as Record<number, boolean>
  }),
  
  actions: {
    setStepData(step: number, data: any) {
      this.formData[`step${step}`] = data;
    },
    
    nextStep() {
      if (this.currentStep < this.totalSteps) {
        this.currentStep++;
      }
    },
    
    previousStep() {
      if (this.currentStep > 1) {
        this.currentStep--;
      }
    }
  }
});
```

**Composable Approach (Vue 3):**
```typescript
// composables/useWizard.ts
import { ref, computed } from 'vue';

export function useWizard(totalSteps: number) {
  const currentStep = ref(1);
  const stepData = ref<Record<number, any>>({});
  
  const isFirstStep = computed(() => currentStep.value === 1);
  const isLastStep = computed(() => currentStep.value === totalSteps);
  
  const setStepData = (step: number, data: any) => {
    stepData.value[step] = data;
  };
  
  const nextStep = () => {
    if (currentStep.value < totalSteps) {
      currentStep.value++;
    }
  };
  
  const previousStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--;
    }
  };
  
  return {
    currentStep,
    stepData,
    isFirstStep,
    isLastStep,
    setStepData,
    nextStep,
    previousStep
  };
}
```

**React Hook Approach:**
```tsx
function useWizard(totalSteps: number) {
  const [currentStep, setCurrentStep] = useState(1);
  const [stepData, setStepData] = useState<Record<number, any>>({});
  
  const setDataForStep = (step: number, data: any) => {
    setStepData(prev => ({ ...prev, [step]: data }));
  };
  
  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1);
    }
  };
  
  const previousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };
  
  return {
    currentStep,
    stepData,
    setDataForStep,
    nextStep,
    previousStep,
    isFirstStep: currentStep === 1,
    isLastStep: currentStep === totalSteps
  };
}
```

### Cross-Step Validation

Validate step N using data from step M.

**Example:**
```typescript
// Validate step 3 requires data from step 1
const validateStep3 = (step3Data: any, step1Data: any) => {
  if (step1Data.accountType === 'business' && !step3Data.taxId) {
    return { taxId: 'Tax ID required for business accounts' };
  }
  return {};
};
```

### Draft Persistence

**LocalStorage (Short-Lived):**
```typescript
const WIZARD_DRAFT_KEY = 'wizard-draft';

// Save draft
const saveDraft = (stepData: Record<number, any>) => {
  localStorage.setItem(WIZARD_DRAFT_KEY, JSON.stringify({
    data: stepData,
    timestamp: Date.now()
  }));
};

// Load draft
const loadDraft = () => {
  const stored = localStorage.getItem(WIZARD_DRAFT_KEY);
  if (stored) {
    const { data, timestamp } = JSON.parse(stored);
    // Expire after 24 hours
    if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
      return data;
    }
  }
  return null;
};
```

**Server-Side (Long-Lived):**
```java
@PostMapping("/wizard/draft")
public ResponseEntity<DraftResponse> saveDraft(
    @RequestBody WizardDraftRequest request,
    @AuthenticationPrincipal User user) {
    
    Draft draft = draftService.saveOrUpdate(
        user.getId(),
        request.getWizardId(),
        request.getStepData()
    );
    
    return ResponseEntity.ok(new DraftResponse(draft.getId(), draft.getExpiresAt()));
}

@GetMapping("/wizard/draft/{wizardId}")
public ResponseEntity<WizardDraftResponse> getDraft(
    @PathVariable String wizardId,
    @AuthenticationPrincipal User user) {
    
    Draft draft = draftService.findByUserAndWizardId(user.getId(), wizardId);
    return ResponseEntity.ok(new WizardDraftResponse(draft.getStepData()));
}
```

### URL-Driven Step Navigation

Use URL parameters or path segments to drive wizard navigation, enabling bookmarking and browser back/forward.

**Vue Router Example:**
```typescript
// router.ts
{
  path: '/wizard/:wizardId/step/:stepNumber',
  component: WizardContainer,
  props: true
}

// Component
<script setup>
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const currentStep = computed(() => parseInt(route.params.stepNumber as string));

const goToStep = (step: number) => {
  router.push({
    name: 'wizard-step',
    params: {
      wizardId: route.params.wizardId,
      stepNumber: step
    }
  });
};
</script>
```

**React Router Example:**
```tsx
<Route path="/wizard/:wizardId/step/:stepNumber" element={<WizardContainer />} />

function WizardContainer() {
  const { wizardId, stepNumber } = useParams();
  const navigate = useNavigate();
  const currentStep = parseInt(stepNumber || '1');
  
  const goToStep = (step: number) => {
    navigate(`/wizard/${wizardId}/step/${step}`);
  };
}
```

### Conditional/Dynamic Steps

Show steps conditionally based on previous step answers.

```typescript
const getVisibleSteps = (stepData: Record<number, any>): number[] => {
  const steps = [1, 2]; // Always show first two steps
  
  // Show step 3 only if step 1 answer was 'business'
  if (stepData[1]?.accountType === 'business') {
    steps.push(3);
  }
  
  steps.push(4); // Always show final step
  
  return steps;
};
```

### Summary/Review Step

Display all collected data before final submission.

```vue
<template>
  <div v-if="isReviewStep">
    <h2>Review Your Information</h2>
    <div v-for="(data, step) in stepData" :key="step">
      <h3>Step {{ step }}</h3>
      <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
    <button @click="submit">Submit</button>
  </div>
</template>
```

### Back-Button Behavior

Handle browser back vs. in-wizard back navigation.

```typescript
// Prevent browser back from leaving wizard mid-flow
useEffect(() => {
  const handlePopState = (e: PopStateEvent) => {
    if (isInWizard && !confirm('Leave wizard? Progress will be saved.')) {
      window.history.pushState(null, '', window.location.href);
    }
  };
  
  window.addEventListener('popstate', handlePopState);
  return () => window.removeEventListener('popstate', handlePopState);
}, [isInWizard]);
```

## Autosave Patterns

Autosave prevents data loss and improves user experience, especially for long forms.

### Debounced Saves

Debounce autosave to avoid excessive server requests.

```typescript
import { debounce } from 'lodash-es';

const autosave = debounce(async (data: FormData) => {
  try {
    await api.post('/form/autosave', data);
    setSaveStatus('saved');
  } catch (error) {
    setSaveStatus('error');
  }
}, 2000); // Save 2 seconds after last change

// Call on form change
watch(formData, () => {
  setSaveStatus('saving');
  autosave(formData.value);
}, { deep: true });
```

### Conflict Detection

Detect and handle concurrent edits.

```java
@PutMapping("/form/{formId}")
public ResponseEntity<?> updateForm(
    @PathVariable String formId,
    @RequestBody FormUpdateRequest request,
    @RequestHeader("If-Match") String etag) {
    
    Form form = formService.findById(formId);
    
    // Check ETag for optimistic locking
    if (!form.getVersion().equals(etag)) {
        return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED)
            .body(Map.of("error", "Form was modified by another user"));
    }
    
    formService.update(formId, request);
    return ResponseEntity.ok()
        .eTag(form.getVersion())
        .body(form);
}
```

**Frontend Conflict Handling:**
```typescript
const saveForm = async (data: FormData) => {
  try {
    const response = await api.put(`/form/${formId}`, data, {
      headers: {
        'If-Match': currentVersion
      }
    });
    
    // Update ETag from response
    currentVersion = response.headers['etag'];
  } catch (error) {
    if (error.response?.status === 412) {
      // Conflict detected - show merge UI or reload
      showConflictDialog();
    }
  }
};
```

### Last-Write-Wins vs. Merge

**Last-Write-Wins:** Simple but can lose data.
```java
// Simple timestamp-based approach
if (request.getTimestamp() > form.getLastModified()) {
    formService.update(formId, request);
}
```

**Merge Strategy:** More complex but preserves changes.
```typescript
// Three-way merge: base, local, remote
const mergeChanges = (base: FormData, local: FormData, remote: FormData) => {
  const merged = { ...base };
  
  // Apply non-conflicting changes
  Object.keys(local).forEach(key => {
    if (base[key] === remote[key]) {
      merged[key] = local[key]; // No conflict
    } else {
      // Conflict - require user resolution
      merged[`${key}_conflict`] = { local: local[key], remote: remote[key] };
    }
  });
  
  return merged;
};
```

### Optimistic Save Indicators

Provide visual feedback for save status.

```vue
<template>
  <div class="save-indicator">
    <span v-if="saveStatus === 'saving'">💾 Saving...</span>
    <span v-else-if="saveStatus === 'saved'">✓ Saved</span>
    <span v-else-if="saveStatus === 'error'">✗ Save failed</span>
  </div>
</template>
```

## Schema-Driven Forms

Generate form UI from JSON Schema or OpenAPI specifications, enabling dynamic form rendering.

### JSON Schema to Form

**React with react-jsonschema-form:**
```tsx
import Form from '@rjsf/core';

const schema = {
  type: 'object',
  properties: {
    email: {
      type: 'string',
      format: 'email',
      title: 'Email Address'
    }
  }
};

<Form schema={schema} onSubmit={handleSubmit} />
```

**Vue 3 with vue-form-json-schema:**
```vue
<template>
  <vue-form-json-schema
    v-model="model"
    :schema="schema"
    :ui-schema="uiSchema"
  />
</template>
```

### When Schema-Driven Makes Sense

**Use Schema-Driven For:**
- Admin-configurable forms (non-developers define forms)
- Forms generated from API contracts (OpenAPI → Form)
- Dynamic forms based on user permissions
- Rapid prototyping
- Forms that change frequently without code deployments

**Avoid Schema-Driven For:**
- Complex custom interactions
- Highly optimized, performance-critical forms
- Forms requiring custom validation logic
- Forms with complex conditional logic
- Forms needing pixel-perfect design control

## File Upload Architecture

File uploads require special handling for large files, progress tracking, and security.

### Chunked Uploads

Break large files into chunks for reliable upload.

```typescript
const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB

async function uploadFileInChunks(file: File, onProgress: (progress: number) => void) {
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const uploadId = await initiateUpload(file.name, file.size);
  
  for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
    const start = chunkIndex * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    
    await uploadChunk(uploadId, chunkIndex, chunk);
    
    onProgress(((chunkIndex + 1) / totalChunks) * 100);
  }
  
  await completeUpload(uploadId);
}
```

### Progress Tracking

```vue
<template>
  <div>
    <input type="file" @change="handleFileSelect" />
    <div v-if="uploading">
      <progress :value="progress" max="100" />
      <span>{{ progress }}%</span>
    </div>
  </div>
</template>

<script setup>
const progress = ref(0);
const uploading = ref(false);

const handleFileSelect = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  
  uploading.value = true;
  await uploadFileInChunks(file, (p) => {
    progress.value = p;
  });
  uploading.value = false;
};
</script>
```

### Drag-and-Drop Zones

```vue
<template>
  <div
    @drop="handleDrop"
    @dragover.prevent
    @dragenter.prevent
    :class="{ 'drag-over': isDragging }"
  >
    Drop files here
  </div>
</template>

<script setup>
const isDragging = ref(false);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  const files = Array.from(e.dataTransfer?.files || []);
  files.forEach(uploadFile);
};
</script>
```

### Server-Side Validation

```java
@PostMapping("/upload")
public ResponseEntity<?> uploadFile(
    @RequestParam("file") MultipartFile file) {
    
    // Type validation
    String contentType = file.getContentType();
    if (!ALLOWED_TYPES.contains(contentType)) {
        return ResponseEntity.badRequest()
            .body(Map.of("error", "File type not allowed"));
    }
    
    // Size validation
    if (file.getSize() > MAX_FILE_SIZE) {
        return ResponseEntity.badRequest()
            .body(Map.of("error", "File too large"));
    }
    
    // Virus scanning (integrate with ClamAV or similar)
    if (!virusScanner.isClean(file.getInputStream())) {
        return ResponseEntity.badRequest()
            .body(Map.of("error", "File failed virus scan"));
    }
    
    // Process upload
    String fileUrl = fileStorageService.store(file);
    return ResponseEntity.ok(Map.of("url", fileUrl));
}
```

### Signed URL Uploads

For direct-to-cloud uploads (S3, GCS), use presigned URLs.

```java
@GetMapping("/upload/presigned-url")
public ResponseEntity<PresignedUrlResponse> getPresignedUrl(
    @RequestParam String fileName,
    @RequestParam String contentType) {
    
    String presignedUrl = s3Service.generatePresignedUrl(fileName, contentType);
    return ResponseEntity.ok(new PresignedUrlResponse(presignedUrl));
}
```

```typescript
// Frontend uploads directly to S3
const uploadToS3 = async (file: File) => {
  // Get presigned URL from backend
  const { presignedUrl } = await api.get('/upload/presigned-url', {
    params: { fileName: file.name, contentType: file.type }
  });
  
  // Upload directly to S3
  await fetch(presignedUrl, {
    method: 'PUT',
    body: file,
    headers: { 'Content-Type': file.type }
  });
};
```

## Server-Side Form Handling

Spring Boot provides robust form handling with Bean Validation.

### Custom ConstraintValidator

```java
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UniqueEmailValidator.class)
public @interface UniqueEmail {
    String message() default "Email already exists";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class UniqueEmailValidator implements ConstraintValidator<UniqueEmail, String> {
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public boolean isValid(String email, ConstraintValidatorContext context) {
        return email == null || !userRepository.existsByEmail(email);
    }
}
```

### Validation Groups for Multi-Step

```java
public interface Step1 {}
public interface Step2 {}

public class UserForm {
    @NotBlank(groups = Step1.class)
    private String email;
    
    @NotBlank(groups = Step2.class)
    private String address;
}

@PostMapping("/wizard/step1")
public ResponseEntity<?> validateStep1(@Validated(Step1.class) @RequestBody UserForm form) {
    // Only Step1 validations run
}
```

## Integration Points

### Form Data Flow to API

```typescript
// Form submission
const handleSubmit = async (formData: FormData) => {
  try {
    setSubmitting(true);
    
    // Client-side validation
    const errors = validateForm(formData);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    // Submit to API
    const response = await api.post('/users', formData);
    
    // Handle success
    router.push('/success');
  } catch (error) {
    // Handle server validation errors
    if (error.response?.status === 400) {
      setFormErrors(error.response.data.errors);
    }
  } finally {
    setSubmitting(false);
  }
};
```

### Error Response Format

Follow RFC 7807 for consistent error responses:

```json
{
  "type": "https://example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "One or more validation errors occurred",
  "errors": {
    "email": "Invalid email format",
    "age": "Must be 18 or older"
  }
}
```

### Optimistic Submission

Provide immediate feedback while request is in flight.

```typescript
const handleSubmit = async (formData: FormData) => {
  // Optimistically update UI
  setSubmitted(true);
  showSuccessMessage('Submitting...');
  
  try {
    await api.post('/users', formData);
    // Confirmation - UI already updated
  } catch (error) {
    // Rollback optimistic update
    setSubmitted(false);
    showErrorMessage('Submission failed');
  }
};
```
