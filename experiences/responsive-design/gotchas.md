# Responsive Design -- Gotchas

Common pitfalls and anti-patterns to avoid when building responsive interfaces.

## Contents

- [Hover-Only Interactions Breaking on Touch Devices](#hover-only-interactions-breaking-on-touch-devices)
- [Fixed-Width Elements Breaking Fluid Layouts](#fixed-width-elements-breaking-fluid-layouts)
- [Responsive Images Served at Desktop Resolution on Mobile](#responsive-images-served-at-desktop-resolution-on-mobile)
- [z-index Stacking Issues at Different Breakpoints](#z-index-stacking-issues-at-different-breakpoints)
- [Soft Keyboard Pushing Content Up](#soft-keyboard-pushing-content-up)
- [100vh on Mobile Including Browser Chrome](#100vh-on-mobile-including-browser-chrome)
- [Container Queries Not Working in All Browsers](#container-queries-not-working-in-all-browsers)
- [Media Queries in Wrong Order](#media-queries-in-wrong-order)
- [Orientation-Specific Layouts Not Tested](#orientation-specific-layouts-not-tested)
- [Desktop-Designed Modals Becoming Unusable on Mobile](#desktop-designed-modals-becoming-unusable-on-mobile)
- [MFE Components with Hardcoded Widths Breaking in Different Shell Layouts](#mfe-components-with-hardcoded-widths-breaking-in-different-shell-layouts)

## Hover-Only Interactions Breaking on Touch Devices

**Problem**: Dropdown menus, tooltips, or other interactions that only work on hover fail completely on touch devices.

```css
/* ❌ Breaks on mobile */
.dropdown:hover .menu {
  display: block;
}
```

**Impact**: Users cannot access functionality on mobile devices.

**Solution**: Always provide click/tap alternative:

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
/* Desktop: hover enhancement */
@media (hover: hover) {
  .dropdown:hover .menu {
    display: block;
  }
}
</style>
```

**Detection**: Test on real touch devices or use browser DevTools touch simulation.

## Fixed-Width Elements Breaking Fluid Layouts

**Problem**: Tables, images, iframes, or other elements with fixed widths cause horizontal scroll on smaller viewports.

```css
/* ❌ Causes horizontal scroll on mobile */
.table {
  width: 1200px;
}

.image {
  width: 800px;
}
```

**Impact**: Poor mobile UX, horizontal scrolling, content cut off.

**Solution**: Make elements responsive:

```css
/* ✅ Responsive */
.table {
  width: 100%;
  max-width: 100%;
  overflow-x: auto; /* Allow scroll if needed */
}

.image {
  max-width: 100%;
  height: auto;
}

iframe {
  max-width: 100%;
  width: 100%;
}
```

**Prevention**: Always use `max-width: 100%` on media elements and test for horizontal scroll at mobile viewports.

## Responsive Images Served at Desktop Resolution on Mobile

**Problem**: Not using `srcset` and `sizes` attributes, causing mobile devices to download desktop-sized images.

```html
<!-- ❌ Mobile downloads 2000px wide image -->
<img src="large-desktop-image.jpg" alt="Description" />
```

**Impact**: 
- Wasted bandwidth (especially on limited data plans)
- Slower page loads
- Poor Core Web Vitals scores
- Higher bounce rates

**Solution**: Use responsive image attributes:

```html
<!-- ✅ Browser selects appropriate size -->
<img 
  srcset="
    image-400w.jpg 400w,
    image-800w.jpg 800w,
    image-1200w.jpg 1200w,
    image-2000w.jpg 2000w
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

**Detection**: Check Network tab in DevTools to see actual image sizes downloaded per device.

## z-index Stacking Issues at Different Breakpoints

**Problem**: z-index values that work on desktop cause stacking issues on mobile (e.g., mobile drawer overlapping desktop sidebar).

```css
/* ❌ z-index conflict */
.sidebar {
  z-index: 100; /* Desktop sidebar */
}

.drawer {
  z-index: 50; /* Mobile drawer - should be higher! */
}

@media (max-width: 768px) {
  .drawer {
    z-index: 200; /* Fixed, but could conflict elsewhere */
  }
}
```

**Impact**: Elements appearing in wrong order, modals behind other content, navigation not accessible.

**Solution**: Use consistent z-index scale and adjust per breakpoint:

```css
/* ✅ Organized z-index scale */
:root {
  --z-base: 1;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
}

.drawer {
  z-index: var(--z-modal);
}

.sidebar {
  z-index: var(--z-fixed);
}

@media (max-width: 768px) {
  .drawer {
    z-index: var(--z-modal); /* Consistent across breakpoints */
  }
  
  .sidebar {
    z-index: var(--z-base); /* Hidden on mobile */
  }
}
```

**Prevention**: Document z-index scale and use CSS custom properties for consistency.

## Soft Keyboard Pushing Content Up

**Problem**: On mobile, when soft keyboard appears, it pushes content up and can cause layout shifts or cover important elements.

```css
/* ❌ Fixed positioning doesn't account for keyboard */
.form-container {
  position: fixed;
  bottom: 0;
  height: 100vh;
}
```

**Impact**: 
- Submit buttons hidden behind keyboard
- Content jumps unexpectedly
- Poor user experience

**Solution**: Handle keyboard appearance:

```css
/* ✅ Account for safe areas */
.form-container {
  padding-bottom: env(safe-area-inset-bottom);
  max-height: 100vh;
  overflow-y: auto;
}

/* Scroll focused input into view */
input:focus {
  scroll-margin-top: 100px;
}
```

**JavaScript solution**:
```javascript
// Scroll input into view when keyboard appears
input.addEventListener('focus', () => {
  setTimeout(() => {
    input.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'center' 
    });
  }, 300); // Wait for keyboard animation
});
```

**Detection**: Test forms on real mobile devices, especially iOS Safari.

## 100vh on Mobile Including Browser Chrome

**Problem**: `100vh` on mobile includes browser chrome (address bar, toolbar), causing content to be cut off or scrollable when it shouldn't be.

```css
/* ❌ Includes browser chrome on mobile */
.hero {
  height: 100vh;
}
```

**Impact**: 
- Content cut off at bottom
- Unnecessary scrolling
- Layout inconsistencies

**Solution**: Use modern viewport units or JavaScript fallback:

```css
/* ✅ Use new viewport units (modern browsers) */
.hero {
  height: 100dvh; /* Dynamic viewport height */
  /* Fallback for older browsers */
  height: 100vh;
}

/* Or use safe area insets */
.hero {
  height: calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom));
}
```

**JavaScript fallback**:
```javascript
// Set CSS custom property for actual viewport height
function setViewportHeight() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

setViewportHeight();
window.addEventListener('resize', setViewportHeight);
```

```css
.hero {
  height: calc(var(--vh, 1vh) * 100);
}
```

**Browser Support**: `dvh` (dynamic viewport height) supported in modern browsers. Provide fallback for older browsers.

## Container Queries Not Working in All Browsers

**Problem**: Using container queries without checking browser support or providing fallbacks.

```css
/* ❌ No fallback for older browsers */
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

**Impact**: Layout breaks in older browsers (Safari < 16, older Chrome/Firefox).

**Solution**: Provide fallback with media queries:

```css
/* ✅ Fallback for older browsers */
.card {
  display: flex;
  flex-direction: column;
}

/* Fallback: media query */
@media (min-width: 768px) {
  .card {
    flex-direction: row;
  }
}

/* Modern: container query */
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}

/* Container query takes precedence when supported */
@supports (container-type: inline-size) {
  @media (min-width: 768px) {
    .card {
      flex-direction: column; /* Reset media query */
    }
  }
}
```

**Detection**: Test in older browsers or use feature detection.

## Media Queries in Wrong Order

**Problem**: Mixing `min-width` and `max-width` media queries in wrong order causes CSS specificity issues.

```css
/* ❌ Wrong order - later rule overrides earlier */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 3rem;
  }
}

/* At 1024px, both apply, but order matters! */
```

**Impact**: Unexpected styles applied, layout inconsistencies.

**Solution**: Use consistent mobile-first approach:

```css
/* ✅ Mobile-first: min-width only */
.container {
  padding: 1rem; /* Mobile default */
}

@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 3rem;
  }
}
```

**Or if using max-width, order from largest to smallest**:

```css
/* ✅ Desktop-first: max-width, largest to smallest */
.container {
  padding: 3rem; /* Desktop default */
}

@media (max-width: 1024px) {
  .container {
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
}
```

**Prevention**: Choose one approach (mobile-first recommended) and stick to it consistently.

## Orientation-Specific Layouts Not Tested

**Problem**: Designing and testing only in portrait orientation, missing landscape layout issues on tablets.

```css
/* ❌ Only tested in portrait */
.tablet-layout {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .tablet-layout {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Impact**: 
- Poor experience in landscape orientation
- Content too wide or too narrow
- Navigation patterns don't work

**Solution**: Test and design for both orientations:

```css
/* ✅ Handle both orientations */
.tablet-layout {
  display: grid;
  grid-template-columns: 1fr;
}

/* Portrait tablet */
@media (min-width: 768px) and (max-width: 1024px) and (orientation: portrait) {
  .tablet-layout {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Landscape tablet */
@media (min-width: 768px) and (max-width: 1024px) and (orientation: landscape) {
  .tablet-layout {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

**Testing**: Always test tablet layouts in both portrait and landscape orientations.

## Desktop-Designed Modals Becoming Unusable on Mobile

**Problem**: Modals designed for desktop (centered, fixed width) become unusable on mobile (too small, cut off, or covering entire screen awkwardly).

```css
/* ❌ Desktop modal breaks on mobile */
.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  max-height: 80vh;
}
```

**Impact**: 
- Modal unusable on small screens
- Content cut off
- Close button not accessible

**Solution**: Adapt modal for mobile:

```css
/* ✅ Responsive modal */
.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .modal {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    transform: none;
    width: 100%;
    max-width: none;
    max-height: 100vh;
    border-radius: 0;
  }
}
```

**Alternative**: Use bottom sheet pattern on mobile:

```vue
<template>
  <div :class="['modal', { 'mobile-sheet': isMobile }]">
    <!-- Modal content -->
  </div>
</template>

<style scoped>
.modal.mobile-sheet {
  top: auto;
  bottom: 0;
  border-radius: 16px 16px 0 0;
  max-height: 90vh;
}
</style>
```

## MFE Components with Hardcoded Widths Breaking in Different Shell Layouts

**Problem**: MFE components with fixed widths break when shell application has different layout constraints.

```css
/* ❌ Hardcoded width breaks in different shells */
.mfe-component {
  width: 1200px;
  margin: 0 auto;
}
```

**Impact**: 
- Components overflow containers
- Layout breaks in different shell configurations
- Inconsistent experience across applications

**Solution**: Make MFE components responsive to container:

```css
/* ✅ Responsive to container */
.mfe-component {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

/* Use container queries when possible */
.mfe-container {
  container-type: inline-size;
}

.mfe-component {
  width: 100%;
}

@container (min-width: 600px) {
  .mfe-component {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Best Practice**: 
- Use percentage-based widths
- Set max-widths for content readability
- Use container queries for component-level responsiveness
- Test MFE in different shell layouts

**Coordination**: Define shared breakpoint tokens and layout constraints in shared configuration that all MFEs consume.
