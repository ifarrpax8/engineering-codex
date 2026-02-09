# Options: Forms and Data Entry

## Contents

- [Form Libraries](#form-libraries)
- [Validation Libraries](#validation-libraries)
- [Multi-Page Form Approaches](#multi-page-form-approaches)
- [Schema-Driven vs Hand-Rolled Forms](#schema-driven-vs-hand-rolled-forms)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies with Other Facets/Experiences](#synergies-with-other-facetsexperiences)
- [Evolution Triggers](#evolution-triggers)

## Form Libraries

### VeeValidate (Vue 3)

**Description**: Form validation library for Vue 3 with composition API support, Yup/Zod integration, and flexible validation strategies.

**Strengths**:
- Native Vue 3 composition API support
- Excellent TypeScript support
- Integrates with Yup, Zod, or custom validators
- Flexible validation modes (onBlur, onChange, onSubmit)
- Good documentation and community
- Works well with Vue design systems (Vuetify, Quasar)

**Weaknesses**:
- Vue-specific (not useful for React projects)
- Can be verbose for simple forms
- Learning curve for complex validation scenarios

**Best For**:
- Vue 3 projects requiring robust validation
- Forms with complex validation rules
- Projects already using Yup or Zod
- Teams comfortable with composition API

**Avoid When**:
- Using React (use React Hook Form instead)
- Simple forms with minimal validation (native HTML5 may suffice)
- Team unfamiliar with Vue 3 composition API

**Example**:
```vue
<script setup>
import { useForm } from 'vee-validate';
import * as yup from 'yup';

const schema = yup.object({
  email: yup.string().email().required(),
});

const { handleSubmit, defineField } = useForm({
  validationSchema: schema,
});

const [email, emailAttrs] = defineField('email');
</script>
```

### FormKit (Vue)

**Description**: Comprehensive form framework for Vue with schema-driven form generation, built-in components, and validation.

**Strengths**:
- Schema-driven form generation
- Built-in form components (inputs, selects, etc.)
- Built-in validation with Zod/Yup
- Good for rapid form development
- Consistent component API
- Good accessibility defaults

**Weaknesses**:
- More opinionated (less flexible than VeeValidate)
- Larger bundle size
- Vue-specific
- Less control over rendering

**Best For**:
- Rapid form development
- Consistent form UI across application
- Schema-driven form requirements
- Teams wanting "batteries included" solution

**Avoid When**:
- Need fine-grained control over form rendering
- Bundle size is critical concern
- Using React

### React Hook Form (React)

**Description**: Performant, flexible form library for React with minimal re-renders and easy validation integration.

**Strengths**:
- Excellent performance (uncontrolled inputs, minimal re-renders)
- Small bundle size (~9KB)
- Great TypeScript support
- Integrates with Zod, Yup, Joi, or custom validators
- Simple API, easy to learn
- Large community and ecosystem
- Works well with UI libraries (MUI, Chakra UI)

**Weaknesses**:
- React-specific
- Can be verbose for very simple forms
- Less opinionated (more decisions to make)

**Best For**:
- React projects (default choice)
- Performance-critical forms
- Large forms with many fields
- Projects using TypeScript
- Teams wanting flexibility

**Avoid When**:
- Using Vue (use VeeValidate or FormKit)
- Need schema-driven form generation (consider Formik or react-jsonschema-form)
- Very simple forms (native HTML5 may suffice)

**Example**:
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

### Formik (React)

**Description**: Popular form library for React with built-in state management and validation.

**Strengths**:
- Mature and stable
- Good documentation
- Works well with Yup
- Flexible and unopinionated
- Large community

**Weaknesses**:
- More verbose than React Hook Form
- More re-renders (less performant)
- Larger bundle size
- Less TypeScript-friendly than React Hook Form

**Best For**:
- Existing projects already using Formik
- Teams familiar with Formik
- Need schema-driven forms with react-jsonschema-form integration

**Avoid When**:
- Starting new projects (prefer React Hook Form)
- Performance is critical
- Want smallest bundle size

## Validation Libraries

### Zod

**Description**: TypeScript-first schema validation library with excellent type inference and composable schemas.

**Strengths**:
- Excellent TypeScript support and type inference
- Composable and powerful schema definitions
- Good error messages out of the box
- Works for both client and server validation
- Active development and community
- Small bundle size (tree-shakeable)

**Weaknesses**:
- TypeScript-focused (less ideal for pure JavaScript)
- Newer than Yup (smaller ecosystem)
- Some advanced features have learning curve

**Best For**:
- TypeScript projects (default choice)
- Projects wanting type-safe validation
- Both client and server validation
- Modern projects prioritizing type safety

**Avoid When**:
- Pure JavaScript projects (Yup may be better)
- Need Yup's mature ecosystem
- Team unfamiliar with TypeScript

**Example**:
```typescript
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  age: z.number().min(18),
});

type FormData = z.infer<typeof schema>; // Type inference!
```

### Yup

**Description**: JavaScript schema validation library with mature ecosystem and wide adoption.

**Strengths**:
- Mature and stable
- Large ecosystem and community
- Works with JavaScript and TypeScript
- Good documentation
- Widely adopted
- Works well with Formik

**Weaknesses**:
- Less TypeScript-friendly than Zod
- No built-in type inference
- Slightly larger bundle size
- Less composable than Zod

**Best For**:
- JavaScript projects
- Existing projects using Yup
- Need mature ecosystem
- Using Formik (built-in Yup support)

**Avoid When**:
- TypeScript projects wanting type inference (prefer Zod)
- Need smallest bundle size
- Want most modern API

### Valibot

**Description**: Lightweight, tree-shakeable validation library similar to Zod but with smaller bundle size.

**Strengths**:
- Very small bundle size (tree-shakeable)
- Similar API to Zod
- Good TypeScript support
- Fast performance

**Weaknesses**:
- Smaller community than Zod/Yup
- Less mature ecosystem
- Less documentation

**Best For**:
- Bundle size is critical
- Want Zod-like API with smaller size
- Modern projects willing to use newer library

**Avoid When**:
- Need mature ecosystem
- Team prefers battle-tested libraries
- Need extensive documentation/community support

## Multi-Page Form Approaches

### URL-Per-Step (Recommended)

**Description**: Each wizard step has its own route (e.g., `/wizard/step-1`, `/wizard/step-2`).

**Strengths**:
- Browser back/forward works naturally
- Bookmarkable steps
- Shareable URLs
- Better analytics (track step completion)
- SEO-friendly
- Clear separation of concerns

**Weaknesses**:
- More routing setup
- Need to manage URL state
- Slightly more complex initial setup

**Best For**:
- Production applications
- Forms that users might bookmark or share
- Need browser navigation support
- Multi-page wizards with 3+ steps

**Avoid When**:
- Very simple 2-step wizards
- Internal tools where URL structure doesn't matter
- Prototyping (use single route initially)

**Implementation**: See Architecture.md for detailed patterns.

### Single Route with Internal State

**Description**: Single route (`/wizard`) with step managed by component state.

**Strengths**:
- Simpler routing setup
- Faster to implement
- Good for prototyping

**Weaknesses**:
- Browser back/forward breaks wizard
- Not bookmarkable
- Can't share specific step URLs
- State management more complex

**Best For**:
- Prototyping
- Simple internal tools
- Short wizards (2-3 steps)
- Temporary forms

**Avoid When**:
- Production user-facing applications
- Long wizards (>3 steps)
- Need browser navigation support
- Users might bookmark or share

### Dedicated Wizard Library

**Description**: Use libraries like `react-step-wizard`, `vue-form-wizard`, or similar.

**Strengths**:
- Faster initial development
- Handles common wizard patterns
- Less code to write

**Weaknesses**:
- Less flexible
- May not fit all use cases
- Additional dependency
- May have limitations

**Best For**:
- Rapid prototyping
- Standard wizard patterns
- Teams wanting "batteries included"
- Simple wizards without custom requirements

**Avoid When**:
- Need custom behavior
- Complex conditional steps
- Need URL-driven routing
- Want full control over implementation

**Examples**:
- `react-step-wizard` (React)
- `vue-form-wizard` (Vue)
- `react-albus` (React, URL-driven)

## Schema-Driven vs Hand-Rolled Forms

### Schema-Driven Forms

**Description**: Generate forms from JSON Schema or similar definitions.

**Strengths**:
- Single source of truth
- Generate forms for different frameworks
- Easier maintenance
- Non-technical users can configure forms
- Consistent validation rules
- Good for dynamic forms

**Weaknesses**:
- Less flexible than hand-rolled
- Can be harder to customize
- Learning curve for schema definition
- May generate code you don't need

**Best For**:
- Forms with similar patterns
- Need to generate forms dynamically
- Non-technical users configuring forms
- Multiple form types with shared structure
- Admin panels with form builders

**Avoid When**:
- Highly customized forms
- Need fine-grained control
- Forms are mostly static
- Small number of forms

**Tools**:
- `react-jsonschema-form` (React)
- `@rjsf/core` (React)
- `vue-json-schema-form` (Vue)
- FormKit (Vue, built-in schema support)

### Hand-Rolled Forms

**Description**: Build forms manually with form library (React Hook Form, VeeValidate, etc.).

**Strengths**:
- Full control over implementation
- Can optimize for specific use cases
- Easier to customize
- No schema learning curve
- Better for one-off forms

**Weaknesses**:
- More code to write
- Validation rules duplicated
- Harder to maintain consistency
- Can't generate forms dynamically

**Best For**:
- Highly customized forms
- One-off or unique forms
- Need fine-grained control
- Small number of forms
- Forms with complex UI requirements

**Avoid When**:
- Many similar forms
- Need dynamic form generation
- Non-technical users configuring forms
- Want single source of truth for validation

## Recommendation Guidance

### Default Stack Recommendations

**Vue 3 Projects**:
1. **Form Library**: VeeValidate (default) or FormKit (if schema-driven)
2. **Validation**: Zod (TypeScript) or Yup (JavaScript)
3. **Multi-Page**: URL-per-step with Vue Router
4. **Design System**: Propulsion components

**React Projects**:
1. **Form Library**: React Hook Form (default)
2. **Validation**: Zod (TypeScript) or Yup (JavaScript)
3. **Multi-Page**: URL-per-step with React Router
4. **Design System**: MUI components

**Spring Boot Backend**:
1. **Validation**: Bean Validation (`@Valid`, `@NotNull`, etc.)
2. **Custom Validators**: Implement `ConstraintValidator`
3. **Error Responses**: Consistent `ValidationErrorResponse` format

### Decision Matrix

**Choose VeeValidate (Vue) when**:
- ✅ Using Vue 3
- ✅ Need robust validation
- ✅ Want flexibility

**Choose FormKit (Vue) when**:
- ✅ Using Vue 3
- ✅ Want schema-driven forms
- ✅ Need rapid development

**Choose React Hook Form (React) when**:
- ✅ Using React
- ✅ Performance matters
- ✅ Want modern, flexible solution

**Choose Formik (React) when**:
- ✅ Already using Formik
- ✅ Need react-jsonschema-form integration

**Choose Zod when**:
- ✅ Using TypeScript
- ✅ Want type inference
- ✅ Modern project

**Choose Yup when**:
- ✅ Using JavaScript
- ✅ Need mature ecosystem
- ✅ Using Formik

**Choose URL-Per-Step when**:
- ✅ Production application
- ✅ Multi-page wizard (>2 steps)
- ✅ Need browser navigation

**Choose Schema-Driven when**:
- ✅ Many similar forms
- ✅ Dynamic form generation
- ✅ Non-technical form configuration

## Synergies with Other Facets/Experiences

### Frontend Architecture
- **State Management**: Forms benefit from shared state management (Context, Pinia, Zustand) for complex multi-page wizards
- **Component Patterns**: Form components should follow established component patterns (composition, props, etc.)

### API Design
- **Validation Error Responses**: Forms need consistent API error response format
- **Idempotency**: Form submissions should be idempotent to prevent double submissions

### Accessibility
- **ARIA Attributes**: Forms must use proper ARIA for screen readers
- **Keyboard Navigation**: Forms must be fully keyboard navigable
- **Focus Management**: Forms need proper focus management on errors

### State Management
- **Draft Persistence**: Multi-page forms benefit from state management for draft saving
- **Form State**: Complex forms may need shared state across components

### Workflows and Tasks
- **Multi-Step Flows**: Forms are often part of larger workflows
- **Task Completion**: Form submission often completes a task in a workflow

### Tables and Data Grids
- **Inline Editing**: Forms patterns apply to inline table editing
- **Bulk Data Entry**: Forms can be extended for bulk operations

### Design Consistency and Visual Identity
- **Design System Integration**: Forms should use design system components (Propulsion, MUI)
- **Consistent Styling**: Form styling should follow design system patterns

## Evolution Triggers

### When to Evolve from Simple to Complex

**Trigger: Form Complexity Increases**
- **Simple Form** → **Multi-Page Wizard**: When form has 15+ fields or logical groupings
- **Single Page** → **Progressive Disclosure**: When form has 10-15 fields that can be grouped
- **Hand-Rolled** → **Schema-Driven**: When you have 5+ similar forms

**Trigger: User Feedback**
- **Add Validation**: Users report data quality issues
- **Add Draft Saving**: Users report losing progress
- **Add Progress Indicator**: Users abandon long forms
- **Add Review Step**: Users submit incorrect data

**Trigger: Technical Requirements**
- **Add Async Validation**: Need to check uniqueness (email, username)
- **Add File Upload**: Need to accept file attachments
- **Add Conditional Steps**: Business logic requires dynamic form flow
- **Add Draft Persistence**: Forms take >5 minutes to complete

**Trigger: Performance Issues**
- **Optimize Validation**: Validation causing performance problems
- **Add Debouncing**: Too many validation calls
- **Switch Libraries**: Current library doesn't scale (e.g., Formik → React Hook Form)

**Trigger: Accessibility Requirements**
- **Add ARIA Attributes**: Accessibility audit reveals issues
- **Improve Keyboard Navigation**: Users report keyboard navigation problems
- **Add Screen Reader Support**: Need to support assistive technologies

**Trigger: Maintenance Burden**
- **Schema-Driven Forms**: Maintaining many similar forms becomes burdensome
- **Consolidate Validation**: Validation logic duplicated across forms
- **Standardize Patterns**: Inconsistent form implementations causing bugs

### Migration Paths

**Formik → React Hook Form**:
- Gradual migration possible (use both libraries)
- React Hook Form has similar API concepts
- Can migrate form-by-form

**Hand-Rolled → Schema-Driven**:
- Start with new forms using schema
- Gradually migrate existing forms
- Can use schema to generate validation even if not generating UI

**Single Route → URL-Per-Step**:
- Add routes for each step
- Migrate state management to URL-driven
- Test browser navigation thoroughly
