# Responsive Design -- Options

Decision matrix for choosing responsive design strategies and implementation approaches.

## Contents

- [Responsive Strategies](#responsive-strategies)
  - [CSS Media Queries](#css-media-queries)
  - [Container Queries](#container-queries)
  - [JavaScript-based (useMediaQuery)](#javascript-based-usemediaquery)
  - [Hybrid](#hybrid)
- [CSS Approaches](#css-approaches)
  - [Tailwind CSS (Utility-First)](#tailwind-css-utility-first)
  - [CSS Modules](#css-modules)
  - [Styled Components / Emotion](#styled-components--emotion)
  - [Plain CSS with Custom Properties](#plain-css-with-custom-properties)
- [Image Optimization](#image-optimization)
  - [Native Lazy Loading + srcset](#native-lazy-loading-srcset)
  - [Intersection Observer](#intersection-observer)
  - [CDN Transforms (Cloudinary, imgix, Vercel Image)](#cdn-transforms-cloudinary-imgix-vercel-image)
- [Table Responsiveness](#table-responsiveness)
  - [Horizontal Scroll](#horizontal-scroll)
  - [Column Stacking](#column-stacking)
  - [Column Hiding (Priority)](#column-hiding-priority)
  - [Card View on Mobile](#card-view-on-mobile)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Responsive Strategies

### CSS Media Queries

**Description**: Use CSS `@media` queries to apply different styles based on viewport width.

**Strengths**:
- Universal browser support
- No JavaScript required
- Works with SSR (server-side rendering)
- Performant (handled by browser)
- Simple to implement

**Weaknesses**:
- Viewport-based only (not container-based)
- Can lead to many breakpoint-specific styles
- Doesn't handle component-level responsiveness well

**Best For**:
- Layout-level responsiveness (page structure, navigation)
- Simple responsive designs
- Projects requiring broad browser support
- SSR applications

**Avoid When**:
- Need component-level responsiveness (use container queries)
- Have many nested components with different breakpoints
- Want to avoid media query complexity

**Example**:
```css
.container {
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}
```

### Container Queries

**Description**: Components respond to their container's width, not just the viewport.

**Strengths**:
- True component-level responsiveness
- Reusable components that adapt to any container
- Better for modular design systems
- Works well in MFE architectures

**Weaknesses**:
- Limited browser support (2023+ browsers)
- Requires fallback with media queries
- More complex setup

**Best For**:
- Component libraries and design systems
- MFE architectures where components fit different containers
- Card grids and dashboard widgets
- Modern applications targeting recent browsers

**Avoid When**:
- Need to support older browsers without fallbacks
- Simple page-level layouts only
- Team unfamiliar with container query concepts

**Example**:
```css
.card-container {
  container-type: inline-size;
}

.card {
  display: flex;
  flex-direction: column;
}

@container (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

### JavaScript-based (useMediaQuery)

**Description**: Use JavaScript hooks (React) or composables (Vue) to conditionally render based on viewport size.

**Strengths**:
- Fine-grained control over rendering
- Can conditionally load components
- Easy to test logic
- Can combine with other state

**Weaknesses**:
- Requires JavaScript (not CSS-only)
- Can cause hydration mismatches in SSR
- May cause layout shifts
- More complex than CSS-only

**Best For**:
- Significantly different component structures per breakpoint
- Conditional feature loading
- Complex responsive logic
- When CSS-only isn't sufficient

**Avoid When**:
- Simple layout changes (use CSS)
- SSR applications without proper hydration handling
- Performance-critical applications (prefer CSS)

**Example (React)**:
```jsx
const isMobile = useMediaQuery('(max-width: 768px)');
return isMobile ? <MobileNav /> : <DesktopNav />;
```

**Example (Vue)**:
```vue
<script setup>
const isMobile = useMediaQuery('(max-width: 768px)');
</script>
<template>
  <MobileNav v-if="isMobile" />
  <DesktopNav v-else />
</template>
```

### Hybrid

**Description**: Combine CSS media queries for layout with JavaScript for functionality.

**Strengths**:
- Best of both worlds
- CSS handles layout (performant, SSR-friendly)
- JavaScript handles complex logic
- Progressive enhancement approach

**Weaknesses**:
- More complex architecture
- Requires coordination between CSS and JS
- Can be overkill for simple cases

**Best For**:
- Complex applications with both layout and functional differences
- Applications requiring fine-grained control
- Teams comfortable with both CSS and JavaScript

**Avoid When**:
- Simple responsive layouts (CSS-only is sufficient)
- Small projects where complexity isn't justified

**Example**:
```vue
<!-- CSS handles layout -->
<div class="grid grid-cols-1 md:grid-cols-2">
  <!-- JavaScript handles functionality -->
  <component :is="isMobile ? MobileTable : DesktopTable" />
</div>
```

## CSS Approaches

### Tailwind CSS (Utility-First)

**Description**: Use Tailwind's responsive utility classes (`sm:`, `md:`, `lg:`, etc.) for responsive design.

**Strengths**:
- Rapid development
- Consistent design system
- No custom CSS needed for most cases
- Excellent documentation
- Easy to maintain

**Weaknesses**:
- Can lead to verbose HTML/JSX
- Learning curve for team
- Less flexible for complex custom designs
- Larger CSS bundle (mitigated with purging)

**Best For**:
- Rapid prototyping
- Teams familiar with utility-first approach
- Projects using Tailwind design system
- Consistent, design-system-driven development

**Avoid When**:
- Highly custom, one-off designs
- Team prefers component-scoped styles
- Existing codebase uses different CSS approach

**Example**:
```vue
<div class="p-4 md:p-6 lg:p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Content
</div>
```

### CSS Modules

**Description**: Scoped CSS modules with responsive styles defined per component.

**Strengths**:
- Component-scoped styles
- No naming conflicts
- Works with any framework
- Familiar CSS syntax

**Weaknesses**:
- More verbose than utilities
- Requires writing custom CSS
- No built-in design system
- Can lead to inconsistent breakpoints

**Best For**:
- Component-focused architectures
- Teams preferring traditional CSS
- Projects requiring highly custom designs
- When avoiding utility-first approach

**Avoid When**:
- Rapid development needed
- Team wants design system consistency
- Prefer utility-first workflow

**Example**:
```css
/* Card.module.css */
.card {
  padding: 1rem;
}

@media (min-width: 768px) {
  .card {
    padding: 2rem;
  }
}
```

### Styled Components / Emotion

**Description**: CSS-in-JS with responsive styles defined in JavaScript.

**Strengths**:
- Dynamic styles based on props/state
- Type-safe (with TypeScript)
- Scoped by default
- Can use JavaScript for responsive logic

**Weaknesses**:
- Runtime overhead
- Larger bundle size
- Not SSR-friendly without setup
- Different mental model from CSS

**Best For**:
- React applications
- Dynamic, prop-based styling
- Teams comfortable with CSS-in-JS
- When needing JavaScript-based responsive logic

**Avoid When**:
- Performance-critical applications
- SSR without proper setup
- Team prefers traditional CSS
- Vue applications (less common)

**Example**:
```jsx
const Card = styled.div`
  padding: 1rem;
  
  @media (min-width: 768px) {
    padding: 2rem;
  }
`;
```

### Plain CSS with Custom Properties

**Description**: Traditional CSS with CSS custom properties (variables) for responsive values.

**Strengths**:
- Universal browser support
- Familiar CSS syntax
- Can be combined with any framework
- Custom properties enable dynamic theming

**Weaknesses**:
- More verbose
- No built-in design system
- Requires discipline for consistency
- More manual work

**Best For**:
- Simple projects
- Teams preferring traditional CSS
- When avoiding framework-specific solutions
- Legacy codebases

**Avoid When**:
- Rapid development needed
- Want design system consistency
- Large teams needing standardization

**Example**:
```css
:root {
  --spacing-sm: 1rem;
  --spacing-md: 2rem;
  --spacing-lg: 3rem;
}

.card {
  padding: var(--spacing-sm);
}

@media (min-width: 768px) {
  .card {
    padding: var(--spacing-md);
  }
}
```

## Image Optimization

### Native Lazy Loading + srcset

**Description**: Use native `loading="lazy"` with `srcset` and `sizes` attributes.

**Strengths**:
- No JavaScript required
- Browser-optimized loading
- Simple to implement
- Good performance

**Weaknesses**:
- Limited control over loading behavior
- `srcset`/`sizes` can be complex
- Requires multiple image sizes

**Best For**:
- Simple image optimization needs
- Projects wanting minimal JavaScript
- Standard use cases
- Good browser support requirements

**Avoid When**:
- Need fine-grained loading control
- Complex art direction requirements
- Want to use modern formats (WebP, AVIF) with fallbacks

**Example**:
```html
<img 
  srcset="image-400w.jpg 400w, image-800w.jpg 800w"
  sizes="(max-width: 768px) 100vw, 50vw"
  src="image-800w.jpg"
  loading="lazy"
  alt="Description"
/>
```

### Intersection Observer

**Description**: Use Intersection Observer API to control when images load.

**Strengths**:
- Fine-grained control
- Can implement custom loading strategies
- Works with any image source
- Can show placeholders

**Weaknesses**:
- Requires JavaScript
- More complex implementation
- Need fallback for older browsers

**Best For**:
- Custom loading strategies
- When need more control than native lazy loading
- Progressive enhancement approaches
- Complex image loading requirements

**Avoid When**:
- Simple use cases (native lazy loading sufficient)
- Want to minimize JavaScript
- Need to support very old browsers

**Example**:
```javascript
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      imageObserver.unobserve(img);
    }
  });
});
images.forEach(img => imageObserver.observe(img));
```

### CDN Transforms (Cloudinary, imgix, Vercel Image)

**Description**: Use CDN services to automatically optimize and transform images.

**Strengths**:
- Automatic optimization
- Format conversion (WebP, AVIF)
- Responsive URLs
- Bandwidth savings
- No build-time processing

**Weaknesses**:
- External dependency
- Cost considerations
- Requires CDN setup
- Vendor lock-in potential

**Best For**:
- Applications with many images
- Need automatic optimization
- Want modern format support
- Dynamic image requirements

**Avoid When**:
- Simple projects with few images
- Want to avoid external dependencies
- Budget constraints
- Need full control over image processing

**Example (Cloudinary)**:
```vue
<img 
  :src="`https://res.cloudinary.com/demo/image/upload/w_auto,c_scale,f_auto,q_auto/${imageId}`"
  alt="Description"
/>
```

**Example (Vercel Image - Next.js)**:
```jsx
<Image
  src="/image.jpg"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Description"
/>
```

## Table Responsiveness

### Horizontal Scroll

**Description**: Allow table to scroll horizontally on mobile while keeping header visible.

**Strengths**:
- Preserves table structure
- Simple to implement
- Works for any table complexity
- Maintains data relationships

**Weaknesses**:
- Poor UX on mobile (horizontal scrolling)
- Can be awkward to use
- May hide important columns

**Best For**:
- Complex tables with many columns
- When data relationships are critical
- Desktop-first applications
- Quick mobile solution

**Avoid When**:
- Mobile is primary use case
- Want better mobile UX
- Simple tables that can be restructured

**Example**:
```css
.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  min-width: 600px;
}
```

### Column Stacking

**Description**: Transform table rows into stacked card-like layouts on mobile.

**Strengths**:
- Better mobile UX
- No horizontal scrolling
- Maintains all data
- Familiar card pattern

**Weaknesses**:
- More complex CSS
- Loses table structure on mobile
- Can be verbose for many columns

**Best For**:
- Mobile-first applications
- Tables with moderate column count
- When data needs to be fully accessible on mobile
- Better UX priority

**Avoid When**:
- Very wide tables (many columns)
- Desktop-only use case
- Need to maintain table structure

**Example**: See [architecture.md](architecture.md#column-stacking-on-mobile) for implementation.

### Column Hiding (Priority)

**Description**: Hide less important columns on smaller screens based on priority.

**Strengths**:
- Maintains table structure
- Shows most important data
- Simple to implement
- Good compromise

**Weaknesses**:
- Hides data (may not be acceptable)
- Requires priority decisions
- May frustrate users needing hidden data

**Best For**:
- Tables with clear priority columns
- When some data is truly secondary
- Quick responsive solution
- Desktop-focused with mobile support

**Avoid When**:
- All columns are important
- Mobile is primary use case
- Need full data access on mobile

**Example**:
```css
.priority-3 {
  display: none;
}

@media (min-width: 768px) {
  .priority-3 {
    display: table-cell;
  }
}
```

### Card View on Mobile

**Description**: Replace table entirely with card component on mobile.

**Strengths**:
- Best mobile UX
- Can optimize layout per device
- Familiar mobile pattern
- Can show different data emphasis

**Weaknesses**:
- Requires maintaining two components
- More complex implementation
- Potential inconsistency between views

**Best For**:
- Mobile-first applications
- When mobile and desktop needs differ significantly
- Better UX is priority
- Have resources for dual implementation

**Avoid When**:
- Simple tables
- Need consistency across devices
- Limited development resources
- Desktop-focused application

**Example**: See [architecture.md](architecture.md#card-view-on-mobile) for implementation.

## Recommendation Guidance

### For New Projects

**Default recommendation**: 
- **Strategy**: CSS Media Queries (mobile-first)
- **CSS Approach**: Tailwind CSS (if using design system) or CSS Modules (if custom design)
- **Images**: Native lazy loading + srcset (simple) or CDN transforms (complex)
- **Tables**: Column stacking or card view (mobile-first) or horizontal scroll (desktop-first)

**Rationale**: 
- Mobile-first CSS media queries provide solid foundation
- Tailwind accelerates development with consistent breakpoints
- Native image loading is simple and performant
- Table approach depends on primary use case

### For Existing Projects

**Migration path**:
1. Assess current responsive approach
2. Identify pain points (too many breakpoints, inconsistent patterns)
3. Gradually adopt mobile-first if desktop-first
4. Standardize breakpoint system
5. Optimize images incrementally

**Considerations**:
- Don't rewrite everything at once
- Maintain existing patterns where they work
- Standardize new development
- Document decisions

### For MFE Architectures

**Recommendation**:
- **Strategy**: Container Queries (with media query fallback)
- **Coordination**: Shared breakpoint tokens
- **Images**: CDN transforms for consistency
- **Tables**: Card view (components adapt to container)

**Rationale**:
- Container queries enable true component-level responsiveness
- Shared tokens ensure consistency across MFEs
- CDN transforms provide consistent image optimization
- Card views work better in variable container widths

## Synergies

### Container Queries + Tailwind
Container queries work well with Tailwind's utility classes for component-level responsiveness.

### CDN Transforms + Native Lazy Loading
Use CDN for optimization and transformation, native lazy loading for performance.

### Media Queries + JavaScript useMediaQuery
Use CSS for layout, JavaScript for functionality differences.

### Mobile-First CSS + Progressive Enhancement
Start with mobile CSS, enhance with JavaScript for advanced features.

## Evolution Triggers

### When to Move from Media Queries to Container Queries

**Triggers**:
- Building component library
- MFE architecture adoption
- Need for reusable responsive components
- Browser support allows (2023+)

**Migration**: Add container queries alongside media queries, gradually replace where beneficial.

### When to Add JavaScript Responsiveness

**Triggers**:
- CSS-only approach insufficient
- Need conditional component rendering
- Different functionality per device
- Complex responsive logic required

**Approach**: Add JavaScript layer while keeping CSS for layout.

### When to Adopt CDN Image Transforms

**Triggers**:
- Many images in application
- Performance issues with current approach
- Need automatic optimization
- Want modern format support

**Migration**: Start with new images, gradually migrate existing.

### When to Change Table Strategy

**Triggers**:
- Mobile usage increases significantly
- User feedback on mobile table UX
- New mobile-first initiative
- Table complexity changes

**Approach**: A/B test new approach, gather feedback, migrate incrementally.
