# Responsive Design -- Best Practices

Proven patterns and principles for building responsive interfaces that work well across devices.

## Contents

- [Mobile-First CSS](#mobile-first-css)
- [Touch Targets](#touch-targets)
- [Avoid Hover-Only Interactions](#avoid-hover-only-interactions)
- [Fluid Layouts Over Fixed Breakpoints](#fluid-layouts-over-fixed-breakpoints)
- [Responsive Typography](#responsive-typography)
- [Test on Real Devices](#test-on-real-devices)
- [Content Prioritization Per Viewport](#content-prioritization-per-viewport)
- [Don't Just Hide Content on Mobile](#dont-just-hide-content-on-mobile)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Image Optimization](#image-optimization)
- [Avoid Horizontal Scroll on Mobile](#avoid-horizontal-scroll-on-mobile)
- [Form Adaptation](#form-adaptation)

## Mobile-First CSS

Start with mobile layout, then enhance for larger screens. This approach:
- Reduces initial CSS payload (mobile gets base styles)
- Ensures mobile experience is considered from the start
- Makes progressive enhancement natural

```css
/* Mobile-first: Start with mobile styles */
.card {
  padding: 1rem;
  width: 100%;
}

/* Enhance for larger screens */
@media (min-width: 768px) {
  .card {
    padding: 2rem;
    max-width: 600px;
  }
}

@media (min-width: 1024px) {
  .card {
    padding: 3rem;
    max-width: 800px;
  }
}
```

**Tailwind example**:
```vue
<!-- Base classes apply to mobile, prefixed classes enhance for larger screens -->
<div class="p-4 md:p-6 lg:p-8 w-full md:max-w-2xl lg:max-w-4xl">
  Content
</div>
```

## Touch Targets

### Minimum 44x44px
WCAG 2.5.8 requires touch targets to be at least 44x44 pixels. This ensures users can reliably tap targets without accidentally hitting adjacent elements.

```css
/* Ensure buttons meet minimum size */
button, .btn {
  min-width: 44px;
  min-height: 44px;
  padding: 0.75rem 1rem; /* Adequate padding for touch */
}
```

**Tailwind**:
```vue
<button class="min-w-[44px] min-h-[44px] px-4 py-3">
  Tap me
</button>
```

### Adequate Spacing Between Targets
Provide at least 8px spacing between touch targets to prevent accidental taps.

```css
.button-group {
  display: flex;
  gap: 1rem; /* 16px spacing */
}

/* Or with margin */
.button + .button {
  margin-left: 0.5rem; /* 8px minimum */
}
```

## Avoid Hover-Only Interactions

Hover states don't exist on touch devices. Always provide alternative interaction patterns.

**Problem**:
```css
/* ❌ Hover-only dropdown breaks on mobile */
.dropdown:hover .menu {
  display: block;
}
```

**Solution 1: Click/Tap Alternative**:
```vue
<template>
  <div class="dropdown" @click="toggleMenu">
    <button>Menu</button>
    <div v-show="menuOpen" class="menu">
      <!-- Menu items -->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const menuOpen = ref(false);
const toggleMenu = () => menuOpen.value = !menuOpen.value;
</script>

<style scoped>
/* Desktop: hover works */
@media (hover: hover) {
  .dropdown:hover .menu {
    display: block;
  }
}

/* Touch devices: click required */
@media (hover: none) {
  .menu {
    display: none;
  }
  
  .menu.open {
    display: block;
  }
}
</style>
```

**Solution 2: Always Clickable**:
```vue
<!-- Make hover an enhancement, not requirement -->
<div class="dropdown" @click="toggleMenu">
  <button>Menu</button>
  <div :class="['menu', { open: menuOpen }]">
    <!-- Menu items -->
  </div>
</div>
```

## Fluid Layouts Over Fixed Breakpoints

Use fluid calculations (`clamp()`, `min()`, `max()`) to create smooth scaling without hard breakpoints.

```css
/* Fluid container width */
.container {
  width: clamp(320px, 90vw, 1200px);
  margin: 0 auto;
}

/* Fluid typography */
h1 {
  font-size: clamp(1.5rem, 4vw + 1rem, 3rem);
}

/* Fluid spacing */
.section {
  padding: clamp(1rem, 5vw, 4rem);
  gap: clamp(1rem, 3vw, 2rem);
}
```

**Benefits**:
- Smooth scaling across all viewport sizes
- Fewer media queries needed
- Better experience on intermediate sizes
- Less maintenance

## Responsive Typography

Scale type with viewport while maintaining readability.

```css
/* Base font size scales with viewport */
body {
  font-size: clamp(16px, 1.5vw + 14px, 18px);
  line-height: 1.6;
}

/* Headings scale proportionally */
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 3.5rem);
}

h2 {
  font-size: clamp(1.5rem, 3vw + 1rem, 2.5rem);
}

/* Maintain minimum readable size */
p {
  font-size: clamp(1rem, 1.5vw + 0.5rem, 1.125rem);
}
```

**Tailwind with custom values**:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    fontSize: {
      'fluid-sm': 'clamp(0.875rem, 1vw + 0.5rem, 1rem)',
      'fluid-base': 'clamp(1rem, 1.5vw + 0.5rem, 1.125rem)',
      'fluid-lg': 'clamp(1.125rem, 2vw + 0.5rem, 1.5rem)',
      'fluid-xl': 'clamp(1.5rem, 3vw + 1rem, 2.5rem)',
    },
  },
}
```

## Test on Real Devices

Browser DevTools emulation is helpful but insufficient. Real devices reveal:
- Actual touch behavior (momentum scrolling, tap delays)
- Soft keyboard behavior and layout shifts
- Performance differences (especially on lower-end devices)
- Orientation change handling
- Browser chrome affecting viewport (100vh issue)

**Testing strategy**:
1. Use DevTools for initial development and quick checks
2. Test on real devices for critical flows
3. Use cloud device testing (BrowserStack, Sauce Labs) for CI/CD
4. Beta test with real users on their devices

## Content Prioritization Per Viewport

Show what matters most for each device context.

**Mobile**: Quick actions, critical information, primary CTA
```vue
<template>
  <div class="mobile-priority">
    <!-- Most important content visible without scroll -->
    <h1>Quick Status</h1>
    <primary-action />
    <!-- Secondary content below fold -->
    <div class="hidden md:block">Additional info</div>
  </div>
</template>
```

**Desktop**: Full feature set, dense information, power user features
```vue
<template>
  <div class="desktop-layout">
    <!-- All features visible -->
    <sidebar />
    <main-content />
    <secondary-panel />
  </div>
</template>
```

**Principle**: Don't remove functionality on mobile—reorganize and prioritize. Use progressive disclosure (tabs, accordions, "Show more" buttons) rather than hiding.

## Don't Just Hide Content on Mobile

Hiding content with `display: none` doesn't solve the problem—users still need that information.

**Problem**:
```css
/* ❌ Hiding important information */
.desktop-only {
  display: none;
}

@media (min-width: 1024px) {
  .desktop-only {
    display: block;
  }
}
```

**Better patterns**:

**1. Reorganize Layout**:
```vue
<!-- Mobile: Stack vertically -->
<div class="flex flex-col md:flex-row gap-4">
  <primary-content />
  <secondary-content />
</div>
```

**2. Progressive Disclosure**:
```vue
<template>
  <div>
    <summary-content />
    <button @click="showDetails = !showDetails" class="md:hidden">
      {{ showDetails ? 'Show Less' : 'Show More' }}
    </button>
    <details-content v-show="showDetails || isDesktop" />
  </div>
</template>
```

**3. Different Presentation**:
```vue
<!-- Mobile: Card view -->
<div class="md:hidden">
  <card-view :data="items" />
</div>

<!-- Desktop: Table view -->
<table class="hidden md:table">
  <!-- Table content -->
</table>
```

## Stack-Specific Guidance

### Tailwind CSS (Utility-First)

**Responsive Utilities**:
```vue
<!-- Base (mobile), then enhance -->
<div class="
  p-4 md:p-6 lg:p-8
  text-sm md:text-base lg:text-lg
  grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
  gap-4 md:gap-6 lg:gap-8
">
  Content
</div>
```

**Custom Breakpoints**:
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'xs': '475px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
  },
}
```

**Container Queries** (Tailwind v3.3+):
```vue
<div class="@container">
  <div class="@md:grid @md:grid-cols-2">
    <!-- Adapts to container, not viewport -->
  </div>
</div>
```

### Propulsion Responsive Components

**Grid System**:
```vue
<template>
  <!-- Propulsion grid with responsive columns -->
  <PxGrid :columns="{ mobile: 1, tablet: 2, desktop: 3 }">
    <PxCard v-for="item in items" :key="item.id">
      {{ item.content }}
    </PxCard>
  </PxGrid>
</template>
```

**Responsive Utilities**:
- Use Propulsion's responsive prop system
- Follow Propulsion breakpoint conventions
- Leverage Propulsion's responsive typography scale

### MUI (Material-UI)

**Grid System**:
```jsx
import { Grid } from '@mui/material';

<Grid container spacing={2}>
  <Grid item xs={12} sm={6} md={4} lg={3}>
    Content
  </Grid>
</Grid>
```

**useMediaQuery Hook**:
```jsx
import { useMediaQuery, useTheme } from '@mui/material';

function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));

  return (
    <>
      {isMobile ? <MobileView /> : <DesktopView />}
    </>
  );
}
```

**Breakpoint System**:
- xs: 0px
- sm: 600px
- md: 900px
- lg: 1200px
- xl: 1536px

### Container Queries with @container

Modern approach for component-level responsiveness:

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  display: flex;
  flex-direction: column;
}

@container card (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

**Browser Support**: Modern browsers (2023+). Provide fallback with media queries.

## Image Optimization

### Serve Appropriately-Sized Images Per Device

```html
<img 
  srcset="
    image-400w.jpg 400w,
    image-800w.jpg 800w,
    image-1200w.jpg 1200w
  "
  sizes="
    (max-width: 768px) 100vw,
    (max-width: 1024px) 50vw,
    33vw
  "
  src="image-800w.jpg"
  alt="Description"
  loading="lazy"
/>
```

### Use Modern Formats

```html
<picture>
  <source type="image/avif" srcset="image.avif" />
  <source type="image/webp" srcset="image.webp" />
  <img src="image.jpg" alt="Description" />
</picture>
```

**CDN Optimization** (Cloudinary, imgix):
```vue
<template>
  <img 
    :src="`https://res.cloudinary.com/demo/image/upload/w_auto,c_scale,f_auto,q_auto/${imageId}`"
    alt="Description"
  />
</template>
```

## Avoid Horizontal Scroll on Mobile

Horizontal scroll (except intentional patterns like carousels) creates poor UX.

**Common causes**:
- Fixed-width elements (tables, images, iframes)
- Negative margins pushing content out
- Absolute positioning extending beyond viewport
- Overflow not handled

**Solutions**:

```css
/* Prevent horizontal scroll */
html, body {
  overflow-x: hidden;
  max-width: 100vw;
}

/* Make fixed-width elements responsive */
img, iframe, table {
  max-width: 100%;
  height: auto;
}

/* Handle tables */
@media (max-width: 768px) {
  table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
```

**Test**: Always check for horizontal scroll at mobile viewports (320px, 375px, 414px).

## Form Adaptation

### Single-Column on Mobile

```css
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .form {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Appropriate Input Types

Use `inputmode` and proper `type` attributes for better mobile keyboards:

```vue
<template>
  <!-- Numeric keyboard on mobile -->
  <input 
    type="tel" 
    inputmode="numeric"
    pattern="[0-9]*"
    placeholder="Phone number"
  />
  
  <!-- Email keyboard -->
  <input 
    type="email" 
    inputmode="email"
    placeholder="Email"
  />
  
  <!-- URL keyboard -->
  <input 
    type="url" 
    inputmode="url"
    placeholder="Website"
  />
</template>
```

### Comfortable Tap Targets

```css
input, select, textarea, button {
  min-height: 44px;
  padding: 0.75rem 1rem;
  font-size: 16px; /* Prevents zoom on iOS */
}

/* Prevent zoom on focus (iOS) */
input, select, textarea {
  font-size: 16px;
}
```

### Handle Soft Keyboard

```css
/* Ensure inputs aren't covered by keyboard */
.form-container {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Scroll input into view when focused */
input:focus {
  scroll-margin-top: 100px; /* Space above input */
}
```

**JavaScript handling**:
```javascript
// Scroll input into view when keyboard appears
input.addEventListener('focus', () => {
  setTimeout(() => {
    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 300); // Wait for keyboard animation
});
```
