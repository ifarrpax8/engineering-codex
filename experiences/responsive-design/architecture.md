# Responsive Design -- Architecture

Technical implementation patterns, component architecture, and system-level considerations for building responsive interfaces.

## Contents

- [CSS-Based Responsive Design](#css-based-responsive-design)
- [Responsive Component Architecture](#responsive-component-architecture)
- [Breakpoint System](#breakpoint-system)
- [Responsive Images](#responsive-images)
- [Responsive Tables](#responsive-tables)
- [Responsive Navigation](#responsive-navigation)
- [MFE Responsive Coordination](#mfe-responsive-coordination)
- [SSR Considerations](#ssr-considerations)

## CSS-Based Responsive Design

### Media Queries (Mobile-First)
Mobile-first means starting with styles for the smallest viewport, then adding styles for larger screens using `min-width` media queries.

```css
/* Mobile-first: Base styles for mobile */
.container {
  padding: 1rem;
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
  }
}
```

**Why mobile-first**: 
- Progressive enhancement (works on all devices)
- Smaller initial CSS payload (mobile gets base styles only)
- Easier to add complexity than remove it

### Container Queries (Component-Level Responsiveness)
Container queries allow components to respond to their container's width, not just the viewport. This enables truly modular, reusable components.

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  display: flex;
  flex-direction: column;
}

/* When container is wider than 400px */
@container card (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

**Use cases**:
- Card components that adapt to grid column width
- Sidebar components that respond to sidebar width
- Dashboard widgets that adapt to their allocated space

**Browser support**: Modern browsers (2023+). Provide fallback with media queries.

### Fluid Typography
Use `clamp()` to create typography that scales smoothly between minimum and maximum sizes.

```css
/* Scales from 1rem (mobile) to 2rem (desktop) */
h1 {
  font-size: clamp(1rem, 2.5vw + 0.5rem, 2rem);
}

/* More readable version with explicit breakpoints */
h1 {
  font-size: clamp(1.25rem, 0.5rem + 2vw, 2rem);
}
```

**Formula**: `clamp(min, preferred, max)`
- `min`: Minimum size (mobile)
- `preferred`: Fluid calculation (viewport-relative)
- `max`: Maximum size (desktop)

### Fluid Spacing
Apply fluid spacing to padding, margins, and gaps.

```css
.section {
  padding: clamp(1rem, 4vw, 3rem);
  gap: clamp(0.5rem, 2vw, 2rem);
}
```

**Benefits**: Smooth scaling without hard breakpoints, reduces need for multiple media queries.

## Responsive Component Architecture

### CSS-Only Responsiveness
Components that adapt purely through CSS, without JavaScript conditional rendering.

**When to use**:
- Layout changes (flex direction, grid columns)
- Visibility changes (hide/show with CSS)
- Spacing and sizing adjustments
- Simple content reordering

**Example (Vue 3)**:
```vue
<template>
  <div class="card">
    <img :src="image" alt="" class="card-image" />
    <div class="card-content">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .card {
    flex-direction: row;
  }
}
</style>
```

**Example (React)**:
```jsx
function Card({ image, title, description }) {
  return (
    <div className="card">
      <img src={image} alt="" className="card-image" />
      <div className="card-content">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}
```

```css
.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .card {
    flex-direction: row;
  }
}
```

### Conditional Rendering
Using JavaScript to conditionally render different components or content based on viewport size.

**When to use**:
- Significantly different component structures per breakpoint
- Different data or functionality per device
- Performance optimization (lazy load heavy components on desktop only)

**Example (Vue 3 with Composition API)**:
```vue
<template>
  <div>
    <!-- Mobile: Drawer navigation -->
    <MobileNav v-if="isMobile" />
    
    <!-- Desktop: Sidebar navigation -->
    <SidebarNav v-else />
    
    <!-- Conditional content -->
    <component :is="mobileView ? MobileTable : DesktopTable" :data="tableData" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isMobile = ref(false);
const mobileView = ref(false);

function checkViewport() {
  isMobile.value = window.innerWidth < 768;
  mobileView.value = window.innerWidth < 1024;
}

onMounted(() => {
  checkViewport();
  window.addEventListener('resize', checkViewport);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkViewport);
});
</script>
```

**Example (React with Hook)**:
```jsx
import { useState, useEffect } from 'react';

function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => 
    typeof window !== 'undefined' && window.matchMedia(query).matches
  );

  useEffect(() => {
    const media = window.matchMedia(query);
    const handler = (event) => setMatches(event.matches);
    
    media.addEventListener('change', handler);
    return () => media.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

function Navigation() {
  const isMobile = useMediaQuery('(max-width: 767px)');
  
  return (
    <>
      {isMobile ? <MobileNav /> : <SidebarNav />}
    </>
  );
}
```

**Performance consideration**: Conditional rendering can cause layout shifts and component remounting. Prefer CSS-only when possible.

## Breakpoint System

### Tailwind CSS Default Breakpoints
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',   // Small devices (landscape phones)
      'md': '768px',   // Medium devices (tablets)
      'lg': '1024px',  // Large devices (desktops)
      'xl': '1280px',  // Extra large devices
      '2xl': '1536px', // 2X large devices
    },
  },
}
```

**Usage**:
```vue
<!-- Vue with Tailwind -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="p-4 md:p-6 lg:p-8">Content</div>
</div>
```

```jsx
// React with Tailwind
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div className="p-4 md:p-6 lg:p-8">Content</div>
</div>
```

### Custom Breakpoints
Add custom breakpoints when default ones don't fit your design system.

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
      '3xl': '1920px', // Ultra-wide monitors
    },
  },
}
```

### MUI Breakpoints
Material-UI uses a different breakpoint system:

```javascript
// MUI breakpoints
xs: 0px      // Extra small devices
sm: 600px    // Small devices
md: 900px    // Medium devices
lg: 1200px   // Large devices
xl: 1536px   // Extra large devices
```

**Usage with MUI `useMediaQuery`**:
```jsx
import { useMediaQuery, useTheme } from '@mui/material';

function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));

  return (
    <div>
      {isMobile ? <MobileView /> : <DesktopView />}
    </div>
  );
}
```

### When to Add Custom Breakpoints
Add custom breakpoints when:
- Your design system has specific breakpoints that don't align with defaults
- You need to target specific device categories (e.g., large tablets at 1024px)
- You're coordinating with design team's breakpoint system
- You need to support ultra-wide monitors (2560px+)

**Avoid**: Adding breakpoints for every minor layout adjustment. Use fluid layouts (`clamp()`) instead.

## Responsive Images

### srcset and sizes Attributes
Serve appropriately-sized images based on viewport and device pixel ratio.

```html
<img 
  srcset="
    image-400w.jpg 400w,
    image-800w.jpg 800w,
    image-1200w.jpg 1200w,
    image-1600w.jpg 1600w
  "
  sizes="
    (max-width: 768px) 100vw,
    (max-width: 1024px) 50vw,
    33vw
  "
  src="image-800w.jpg"
  alt="Description"
/>
```

**How it works**:
- Browser calculates needed image size based on `sizes` attribute
- Selects appropriate image from `srcset` based on device pixel ratio
- Falls back to `src` for older browsers

### Picture Element for Art Direction
Use `<picture>` when you need different images (not just sizes) per breakpoint.

```html
<picture>
  <source 
    media="(min-width: 1024px)" 
    srcset="desktop-image.jpg"
  />
  <source 
    media="(min-width: 768px)" 
    srcset="tablet-image.jpg"
  />
  <img 
    src="mobile-image.jpg" 
    alt="Description"
  />
</picture>
```

**Use cases**:
- Different crops for mobile vs desktop
- Horizontal image on desktop, vertical on mobile
- Different focal points per device

### Image CDN Transforms
Use CDN services (Cloudinary, imgix, Vercel Image) for automatic responsive images.

**Cloudinary**:
```vue
<template>
  <img 
    :src="`https://res.cloudinary.com/demo/image/upload/w_auto,c_scale,f_auto,q_auto/${imageId}`"
    alt="Description"
  />
</template>
```

**Vercel Image (Next.js)**:
```jsx
import Image from 'next/image';

<Image
  src="/image.jpg"
  width={800}
  height={600}
  alt="Description"
  sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
/>
```

**Benefits**: Automatic optimization, format conversion (WebP, AVIF), lazy loading, bandwidth savings.

### Lazy Loading
Defer loading images until they're about to enter the viewport.

```html
<!-- Native lazy loading -->
<img 
  src="image.jpg" 
  alt="Description"
  loading="lazy"
/>

<!-- With Intersection Observer (for more control) -->
<img 
  data-src="image.jpg" 
  alt="Description"
  class="lazy-image"
/>
```

```javascript
// Intersection Observer implementation
const images = document.querySelectorAll('.lazy-image');

const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy-image');
      imageObserver.unobserve(img);
    }
  });
});

images.forEach(img => imageObserver.observe(img));
```

## Responsive Tables

### Column Stacking on Mobile
Transform table rows into card-like stacked layouts on mobile.

```vue
<template>
  <div class="table-container">
    <table class="responsive-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td data-label="Name">{{ user.name }}</td>
          <td data-label="Email">{{ user.email }}</td>
          <td data-label="Role">{{ user.role }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.responsive-table {
  width: 100%;
  border-collapse: collapse;
}

@media (max-width: 768px) {
  .responsive-table thead {
    display: none;
  }
  
  .responsive-table tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .responsive-table td {
    display: block;
    text-align: right;
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
  }
  
  .responsive-table td::before {
    content: attr(data-label) ": ";
    font-weight: bold;
    float: left;
  }
}
</style>
```

### Horizontal Scroll
Allow table to scroll horizontally on mobile while keeping header visible.

```css
.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.responsive-table {
  min-width: 600px; /* Minimum width to prevent squishing */
}
```

### Column Hiding (Priority-Based)
Hide less important columns on smaller screens.

```vue
<template>
  <table>
    <thead>
      <tr>
        <th class="priority-1">Name</th>
        <th class="priority-1">Status</th>
        <th class="priority-2">Email</th>
        <th class="priority-3">Last Login</th>
      </tr>
    </thead>
  </table>
</template>

<style scoped>
@media (max-width: 768px) {
  .priority-3 {
    display: none;
  }
}

@media (max-width: 480px) {
  .priority-2 {
    display: none;
  }
}
</style>
```

### Card View on Mobile
Replace table entirely with card component on mobile.

```vue
<template>
  <!-- Desktop: Table -->
  <table class="hidden md:table">
    <!-- Table content -->
  </table>
  
  <!-- Mobile: Cards -->
  <div class="md:hidden space-y-4">
    <div 
      v-for="user in users" 
      :key="user.id"
      class="card p-4 border rounded"
    >
      <h3>{{ user.name }}</h3>
      <p>{{ user.email }}</p>
      <span>{{ user.role }}</span>
    </div>
  </div>
</template>
```

## Responsive Navigation

### Drawer/Hamburger Menu
Mobile navigation pattern with slide-out drawer.

```vue
<template>
  <nav>
    <button @click="drawerOpen = !drawerOpen" class="md:hidden">
      <MenuIcon />
    </button>
    
    <div 
      :class="['drawer', { 'drawer-open': drawerOpen }]"
      class="md:hidden"
    >
      <nav-links />
    </div>
    
    <div class="hidden md:block">
      <nav-links />
    </div>
  </nav>
</template>

<style scoped>
.drawer {
  position: fixed;
  top: 0;
  left: -100%;
  width: 80%;
  height: 100vh;
  background: white;
  transition: left 0.3s ease;
  z-index: 1000;
}

.drawer-open {
  left: 0;
}
</style>
```

### Bottom Navigation Bar
Mobile-first navigation pattern with fixed bottom bar.

```vue
<template>
  <nav class="bottom-nav md:hidden">
    <router-link to="/home">
      <HomeIcon />
      <span>Home</span>
    </router-link>
    <router-link to="/search">
      <SearchIcon />
      <span>Search</span>
    </router-link>
    <!-- More items -->
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 0.5rem;
  background: white;
  border-top: 1px solid #ddd;
}
</style>
```

### Collapsible Sidebar
Desktop sidebar that collapses on smaller screens or can be toggled.

```vue
<template>
  <aside :class="['sidebar', { 'collapsed': collapsed }]">
    <button @click="collapsed = !collapsed" class="toggle-btn">
      <ChevronLeftIcon />
    </button>
    <nav-links />
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: -250px;
    height: 100vh;
  }
  
  .sidebar.open {
    left: 0;
  }
}
</style>
```

## MFE Responsive Coordination

### Shared Breakpoint Tokens
Define breakpoints in shared configuration that all MFEs consume.

```javascript
// shared/config/breakpoints.js
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};
```

**Usage in Tailwind config**:
```javascript
// Each MFE's tailwind.config.js
const sharedBreakpoints = require('@shared/config/breakpoints');

module.exports = {
  theme: {
    screens: sharedBreakpoints,
  },
};
```

### Shell-Level Responsive Layout
Shell application manages overall layout structure, MFEs fit within allocated containers.

```vue
<!-- Shell App -->
<template>
  <div class="shell-layout">
    <aside :class="['sidebar', { 'collapsed': sidebarCollapsed }]">
      <navigation-mfe />
    </aside>
    <main class="main-content">
      <router-view /> <!-- MFEs load here -->
    </main>
  </div>
</template>

<style>
.shell-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
}

@media (max-width: 1024px) {
  .shell-layout {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
  }
}
</style>
```

### MFE Content Fitting Container
MFEs should be responsive to their container, not just viewport.

```vue
<!-- Inside an MFE -->
<template>
  <div class="mfe-container">
    <!-- Use container queries when possible -->
    <div class="content-grid">
      <!-- Content adapts to MFE container width -->
    </div>
  </div>
</template>

<style>
.mfe-container {
  container-type: inline-size;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
}

@container (min-width: 600px) {
  .content-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
```

## SSR Considerations

### No Window on Server
Server-side rendering doesn't have `window` object. Handle viewport detection carefully.

**Problem**:
```javascript
// ❌ Breaks on server
const isMobile = window.innerWidth < 768;
```

**Solution (Vue 3)**:
```vue
<script setup>
import { ref, onMounted } from 'vue';

const isMobile = ref(false);

onMounted(() => {
  // Only runs on client
  isMobile.value = window.innerWidth < 768;
});
</script>
```

**Solution (React)**:
```jsx
function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Only runs on client
    setIsMobile(window.innerWidth < 768);
  }, []);

  return isMobile;
}
```

### useMediaQuery Hydration Mismatch
Client and server may render differently if media queries are used in JavaScript.

**Problem**: Server renders desktop view, client hydrates with mobile view (or vice versa), causing layout shift.

**Solution**: 
1. Use CSS-only responsiveness when possible
2. Default to mobile view on server, update on client mount
3. Use CSS classes to hide/show, let JavaScript enhance

```vue
<template>
  <!-- Server renders both, CSS hides one -->
  <MobileNav class="md:hidden" />
  <DesktopNav class="hidden md:block" />
</template>
```

### CSS-First for Initial Render
Ensure initial render uses CSS media queries, not JavaScript.

**Best practice**: 
- Layout and visibility changes: CSS media queries
- Functionality changes: JavaScript with proper SSR handling
- Progressive enhancement: CSS provides base experience, JavaScript enhances

```css
/* CSS handles initial layout */
.responsive-grid {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .responsive-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

```javascript
// JavaScript enhances with interactivity
// But layout is already correct from CSS
```
