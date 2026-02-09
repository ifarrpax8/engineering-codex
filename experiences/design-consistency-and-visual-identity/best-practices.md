---
title: Design Consistency & Visual Identity - Best Practices
type: experience
last_updated: 2026-02-09
---

# Best Practices: Design Consistency & Visual Identity

## Contents

- [Use a Design System, Not Just a Component Library](#use-a-design-system-not-just-a-component-library)
- [Consistent Spacing Scale](#consistent-spacing-scale)
- [Predictable Interaction Patterns](#predictable-interaction-patterns)
- [Page Layout Templates](#page-layout-templates)
- [Consistent Empty States](#consistent-empty-states)
- [Consistent Error States](#consistent-error-states)
- [Motion Principles](#motion-principles)
- [Typography Hierarchy](#typography-hierarchy)
- [Stack-Specific Patterns](#stack-specific-patterns)
- [Contributing to the Design System](#contributing-to-the-design-system)
- [Documentation](#documentation)

## Use a Design System, Not Just a Component Library

A design system includes:
- **Design tokens** (colors, spacing, typography)
- **Component library** (buttons, forms, cards)
- **Patterns and guidelines** (when to use which component, interaction patterns)
- **Documentation** (Storybook, style guide)

**Don't just install a component library**—adopt the full system. Components alone don't ensure consistency if developers don't know when to use them.

**Example**: Installing MUI but not using MUI's spacing scale or theme system means inconsistent spacing and colors across the app.

## Consistent Spacing Scale

### Choose a Base (4px or 8px)

**4px base** (more granular):
```css
:root {
  --spacing-1: 4px;   /* 0.25rem */
  --spacing-2: 8px;   /* 0.5rem */
  --spacing-3: 12px;  /* 0.75rem */
  --spacing-4: 16px;  /* 1rem */
  --spacing-6: 24px;  /* 1.5rem */
  --spacing-8: 32px;  /* 2rem */
}
```

**8px base** (simpler, common):
```css
:root {
  --spacing-1: 8px;   /* 0.5rem */
  --spacing-2: 16px;  /* 1rem */
  --spacing-3: 24px;  /* 1.5rem */
  --spacing-4: 32px;  /* 2rem */
  --spacing-6: 48px;  /* 3rem */
  --spacing-8: 64px;  /* 4rem */
}
```

### Use Tokens, Not Raw Values

**❌ Bad**:
```css
.card {
  padding: 15px; /* Magic number */
  margin-bottom: 23px; /* Inconsistent */
}
```

**✅ Good**:
```css
.card {
  padding: var(--spacing-4); /* 16px */
  margin-bottom: var(--spacing-6); /* 24px or 48px depending on base */
}
```

**Tailwind**:
```html
<!-- ✅ Good -->
<div class="p-4 mb-6">Card content</div>

<!-- ❌ Bad -->
<div class="p-[15px] mb-[23px]">Card content</div>
```

## Predictable Interaction Patterns

### Same Action = Same Affordance

**Destructive actions** should always look the same:
```vue
<!-- Delete button - always red/danger variant -->
<PaxButton variant="danger" @click="handleDelete">
  Delete Item
</PaxButton>
```

**Primary actions** should be consistent:
```jsx
// Save button - always primary variant, same location
<Button variant="contained" color="primary" sx={{ ml: 'auto' }}>
  Save Changes
</Button>
```

**Navigation patterns**: If breadcrumbs are used in one area, use them consistently. If tabs are used for section navigation, don't switch to accordions elsewhere.

### Consistent Form Patterns

**Form layout**:
- Labels above inputs (or consistent left-aligned)
- Error messages below inputs
- Submit button placement (bottom-right or full-width)

**Validation feedback**: Same error styling, same success styling across all forms.

## Page Layout Templates

### Establish 2-3 Standard Layouts

**Layout 1: Sidebar + Content**
```vue
<template>
  <div class="layout-sidebar-content">
    <aside class="sidebar">
      <slot name="sidebar" />
    </aside>
    <main class="content">
      <slot name="content" />
    </main>
  </div>
</template>
```

**Layout 2: Full-Width Dashboard**
```jsx
<div className="dashboard-grid">
  <div className="dashboard-header">Header</div>
  <div className="dashboard-widgets">
    {widgets.map(widget => <Widget key={widget.id} {...widget} />)}
  </div>
</div>
```

**Layout 3: Centered Content**
```vue
<template>
  <div class="layout-centered">
    <div class="centered-content">
      <slot />
    </div>
  </div>
</template>
```

**Don't invent new layouts** for each page. Reuse established templates.

## Consistent Empty States

### Same Illustration Style

Use consistent illustration style (line art, filled, flat) across all empty states.

**Example pattern**:
```vue
<template>
  <div class="empty-state">
    <img src="/illustrations/empty-list.svg" alt="" />
    <h3>No items yet</h3>
    <p>Get started by creating your first item.</p>
    <PaxButton variant="primary" @click="handleCreate">
      Create Item
    </PaxButton>
  </div>
</template>
```

### Same Messaging Pattern

- **Illustration** (consistent style)
- **Heading** (what's missing)
- **Description** (why it's empty, what to do)
- **Action button** (how to fix it)

## Consistent Error States

### Same Error UI Everywhere

**Inline form errors**:
```vue
<template>
  <div class="form-field">
    <label>Email</label>
    <input v-model="email" />
    <span v-if="error" class="error-message">{{ error }}</span>
  </div>
</template>

<style scoped>
.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-1);
}
</style>
```

**Page-level errors**:
```jsx
<Alert severity="error" sx={{ mb: 2 }}>
  {errorMessage}
</Alert>
```

**API error handling**: Same error display pattern for network errors, validation errors, server errors.

## Motion Principles

### Purposeful

Animations should guide attention or provide feedback:

```css
/* ✅ Good - provides feedback */
.button:active {
  transform: scale(0.98);
  transition: transform 0.1s;
}

/* ❌ Bad - distracting */
.button {
  animation: bounce 2s infinite;
}
```

### Consistent

**Same easing and duration** for similar interactions:

```css
:root {
  --easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
}

/* All hover states use same timing */
.card:hover {
  transform: translateY(-2px);
  transition: transform var(--duration-normal) var(--easing-standard);
}
```

### Subtle

Animations should enhance, not distract. Avoid excessive motion:

```css
/* ✅ Good - subtle */
.fade-in {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ❌ Bad - too much */
.bounce-in {
  animation: bounceIn 0.5s ease-out;
}
```

## Typography Hierarchy

### Establish Clear Levels

```css
:root {
  /* Headings */
  --font-size-h1: 2.5rem;   /* 40px */
  --font-size-h2: 2rem;     /* 32px */
  --font-size-h3: 1.5rem;   /* 24px */
  --font-size-h4: 1.25rem;  /* 20px */
  
  /* Body */
  --font-size-body: 1rem;   /* 16px */
  --font-size-body-sm: 0.875rem; /* 14px */
  
  /* Caption */
  --font-size-caption: 0.75rem; /* 12px */
}
```

### Use Tokens

**❌ Bad**:
```css
.title {
  font-size: 28px; /* Magic number */
}
```

**✅ Good**:
```css
.title {
  font-size: var(--font-size-h2);
}
```

**Semantic usage**: Use heading levels semantically (h1, h2, h3), not just for styling.

## Stack-Specific Patterns

### Propulsion Usage Patterns

**When to extend Propulsion**:
- Compose existing Propulsion components
- Use Propulsion tokens for spacing, colors
- Follow Propulsion patterns (button variants, form layouts)

**When to extend**:
```vue
<!-- Compose Propulsion components -->
<template>
  <PaxCard>
    <PaxCardHeader>
      <PaxHeading level="3">Title</PaxHeading>
    </PaxCardHeader>
    <PaxCardContent>
      <slot />
    </PaxCardContent>
  </PaxCard>
</template>
```

**Avoid**: Creating custom components that duplicate Propulsion functionality.

### MUI Theme Customization

**Use `createTheme`** for brand customization:

```jsx
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3b82f6', // Brand color
    },
  },
  typography: {
    fontFamily: '"Inter", sans-serif',
  },
  spacing: 8, // 8px base
});
```

**Component overrides** (use sparingly):
```jsx
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8, // Consistent border radius
        },
      },
    },
  },
});
```

**Avoid**: Overriding too many components—you'll lose MUI's design language.

### Tailwind Design Token Mapping

**Extend theme config**:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      spacing: {
        '18': '72px', // Add to 8px base scale
      },
    },
  },
};
```

**Use semantic tokens**:
```html
<!-- ✅ Good - semantic -->
<div class="bg-primary-500 text-white p-4">

<!-- ❌ Bad - arbitrary values -->
<div class="bg-[#3b82f6] text-white p-[15px]">
```

## Contributing to the Design System

### When to Propose New Components

**Propose new component when**:
- Pattern appears 3+ times across features
- No existing component can be composed to achieve the pattern
- Pattern is complex enough to warrant its own component

**Compose existing components when**:
- Pattern can be built from existing components
- Pattern is feature-specific (not reusable)
- Pattern appears only once or twice

**Example**: Don't create `ProductCard` component—compose `Card`, `Image`, `Button` instead. But do create `DataTable` if tables appear everywhere with same patterns.

### Component Proposal Process

1. **Document use cases**: Where will this component be used?
2. **Check alternatives**: Can existing components be composed?
3. **Design review**: Does it fit design system aesthetic?
4. **Implementation**: Build component with Storybook stories
5. **Documentation**: Add usage guidelines, examples, accessibility notes

## Documentation

### Living Style Guide

**Storybook as source of truth**:
- All components documented in Storybook
- Usage examples for each variant
- Accessibility guidelines
- Design tokens reference

**Keep Storybook updated**: When components change, update Storybook immediately. Stale documentation is worse than no documentation.

### Component Documentation Template

```markdown
## Button

### Usage
Primary action buttons for important user actions.

### Variants
- `primary`: Main action (blue)
- `secondary`: Secondary action (gray)
- `danger`: Destructive action (red)

### Examples
[Storybook stories]

### Accessibility
- Keyboard navigable
- Focus indicator visible
- ARIA labels for icon-only buttons
```

### Design Token Documentation

**Document all tokens**:
```markdown
## Spacing Scale

- `--spacing-1`: 4px - Tight spacing
- `--spacing-2`: 8px - Compact spacing
- `--spacing-4`: 16px - Standard spacing
- `--spacing-8`: 32px - Loose spacing

## Usage
Always use spacing tokens, never raw pixel values.
```

**Keep token docs in sync** with actual token definitions. Automate if possible.
