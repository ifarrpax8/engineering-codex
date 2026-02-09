# Frontend Architecture -- Best Practices

Principles and patterns for building maintainable, performant frontend applications. These are language-agnostic where possible, with stack-specific callouts for Vue 3 and React where the framework materially affects the recommendation.

## Contents

- [Feature-Based Folder Structure](#feature-based-folder-structure)
- [Component Composition Over Inheritance](#component-composition-over-inheritance)
- [Smart vs Presentational Components](#smart-vs-presentational-components)
- [Prop Drilling Alternatives](#prop-drilling-alternatives)
- [Lazy Loading Routes](#lazy-loading-routes)
- [Shared Design System Usage](#shared-design-system-usage)
- [Code Splitting Strategy](#code-splitting-strategy)
- [Error Boundaries and Resilience](#error-boundaries-and-resilience)
- [Stack-Specific Callouts](#stack-specific-callouts)

## Feature-Based Folder Structure

Group code by feature, not by type. A feature folder contains everything that feature needs: components, composables/hooks, services, types, and tests.

```
src/
├── features/
│   ├── billing/
│   │   ├── components/
│   │   │   ├── InvoiceList.vue
│   │   │   ├── InvoiceDetail.vue
│   │   │   └── PaymentForm.vue
│   │   ├── composables/
│   │   │   └── useInvoices.ts
│   │   ├── services/
│   │   │   └── billingApi.ts
│   │   ├── types/
│   │   │   └── billing.ts
│   │   └── index.ts
│   ├── users/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── services/
│   │   └── types/
│   └── orders/
├── shared/
│   ├── components/
│   ├── composables/
│   ├── utils/
│   └── types/
├── layouts/
├── router/
└── App.vue
```

**Why this matters**: When working on a feature, all relevant code is co-located. Navigating between a component, its data fetching logic, and its types requires moving within one folder instead of jumping across `components/`, `services/`, and `types/` at the root level. Deleting a feature is a single folder deletion.

**When to deviate**: Truly shared utilities (date formatting, HTTP client configuration) belong in a `shared/` directory. The rule of thumb: if only one feature uses it, it belongs in that feature folder. If two or more features use it, promote it to `shared/`.

## Component Composition Over Inheritance

Share behavior through composition (composables in Vue, hooks in React), not through component inheritance or deeply nested higher-order component chains.

**Composable/Hook pattern**: Extract reusable behavior into functions that encapsulate reactive state, side effects, and lifecycle management.

```typescript
function usePagination<T>(fetchFn: (page: number) => Promise<Page<T>>) {
  const items = ref<T[]>([])
  const currentPage = ref(1)
  const totalPages = ref(0)
  const loading = ref(false)

  async function goToPage(page: number) {
    loading.value = true
    const result = await fetchFn(page)
    items.value = result.content
    currentPage.value = result.number
    totalPages.value = result.totalPages
    loading.value = false
  }

  return { items, currentPage, totalPages, loading, goToPage }
}
```

**Why this matters**: Composables/hooks are plain functions. They can be tested independently, composed together, and their dependencies are explicit. Component inheritance creates rigid hierarchies that are difficult to refactor.

## Smart vs Presentational Components

Separate components into two categories:

**Presentational (dumb) components**: receive data via props, emit events, render UI. They know nothing about data fetching, routing, or business logic. They are highly reusable and easy to test.

**Smart (container) components**: manage data fetching, state, and side effects. They pass data down to presentational components and handle events from them. They are tied to specific features and are tested with integration tests.

```
<!-- Smart: fetches data, manages state -->
<InvoiceListPage />
  └── uses useInvoices() composable
  └── renders <InvoiceTable :invoices="invoices" @select="onSelect" />
  └── renders <Pagination :page="page" @change="onPageChange" />

<!-- Presentational: pure rendering -->
<InvoiceTable :invoices="invoices" @select="emit('select', invoice)" />
<Pagination :page="page" :total="total" @change="emit('change', page)" />
```

**When to deviate**: Very simple features don't need this separation. A component that fetches and displays a single piece of data (like a user avatar) doesn't need to be split into two components.

## Prop Drilling Alternatives

When data needs to reach deeply nested components, avoid passing props through every intermediate component.

**State management stores**: Pinia (Vue) or Zustand (React) for application-wide state that multiple unrelated components need.

**Provide/inject (Vue) or Context (React)**: for subtree-scoped state. A parent provides values that any descendant can inject without intermediate components knowing about it. Good for theme data, locale, authenticated user, and feature-scoped shared state.

**URL state**: for state that should survive page refreshes and be shareable via links (active filters, selected tab, current page number). Use query parameters or route params.

**When to just drill props**: If the component hierarchy is shallow (2-3 levels) and the data flows naturally through the tree, prop drilling is simpler and more explicit. Don't optimize for a problem you don't have.

## Lazy Loading Routes

Every route should be lazy loaded. This means the code for a page is only downloaded when the user navigates to it, not on initial page load.

```typescript
const routes = [
  {
    path: '/dashboard',
    component: () => import('./features/dashboard/DashboardPage.vue'),
  },
  {
    path: '/billing',
    component: () => import('./features/billing/BillingPage.vue'),
  },
  {
    path: '/settings',
    component: () => import('./features/settings/SettingsPage.vue'),
  },
]
```

**Why this matters**: Without lazy loading, every route's code is included in the initial bundle. Users downloading the entire application upfront pay the cost for pages they may never visit. Lazy loading routes is the single highest-impact code splitting optimization.

**Suspense boundaries**: wrap lazy-loaded routes with loading fallbacks so users see immediate feedback during code download.

## Shared Design System Usage

Use the design system (Propulsion) components directly. Do not wrap them in application-specific components unless you need to compose multiple design system primitives into a domain-specific pattern.

**Do**: use `<PrButton>`, `<PrTable>`, `<PrModal>` directly in your feature components.

**Don't**: create `<AppButton>` that wraps `<PrButton>` with "convenience" props. This creates a maintenance burden where every design system update requires updating your wrappers too.

**Do**: create domain-specific compositions like `<InvoiceStatusBadge>` that uses design system primitives (`<PrBadge>`) with domain-specific logic (mapping invoice status to badge variant and label).

**Design tokens**: use the design system's spacing, typography, and color tokens. Don't define custom spacing values or colors that drift from the system. Tailwind CSS should be configured with the design system's token values.

## Code Splitting Strategy

Apply code splitting in this order of impact:

1. **Route-level splitting** (highest impact): lazy load every route. This is almost always worth doing and should be the default.
2. **Heavy component splitting**: lazy load components that include large libraries (chart libraries, rich text editors, PDF viewers). Use `defineAsyncComponent` (Vue) or `React.lazy`.
3. **Conditional feature splitting**: lazy load features behind feature flags that only some users see.
4. **Vendor splitting**: configure the bundler to separate vendor code from application code so vendor bundles are cached independently.

**Measure before splitting further**: after route-level splitting, use bundle analysis tools (rollup-plugin-visualizer, webpack-bundle-analyzer) to identify the largest chunks. Don't split small components -- the overhead of additional network requests can outweigh the benefit.

## Error Boundaries and Resilience

Wrap independent sections of the UI in error boundaries so that a failure in one section doesn't crash the entire page.

This is especially important in MFE architectures where one failing micro-frontend should not take down the shell or other micro-frontends. Display a graceful fallback (error message, retry button) instead of a blank page.

## Stack-Specific Callouts

### Vue 3

- Use `<script setup>` with the Composition API as the default component authoring style. Options API is acceptable in existing codebases but should not be used for new components.
- Extract shared logic into composables (`use*.ts` files). Composables are plain functions that use Vue's reactivity system (ref, computed, watch).
- Use Pinia for global state management. Prefer stores scoped to features (`useInvoiceStore`) over a single monolithic store.
- Use `defineAsyncComponent` for lazy loading heavy components within a page.
- Use `<Suspense>` to provide loading states for async components and async setup functions.
- Use `<Teleport>` for rendering modals, tooltips, and popovers outside the component tree (e.g., to `<body>`).

### React

- Use function components with hooks as the default component authoring style. Class components are acceptable in existing codebases but should not be used for new components.
- Extract shared logic into custom hooks (`use*.ts` files). Custom hooks are plain functions that use React's hooks (useState, useEffect, useMemo).
- Use Zustand for lightweight global state or TanStack Query for server state management. TanStack Query handles caching, deduplication, and background refetching -- don't reinvent this with useEffect + useState.
- Use `React.lazy` + `<Suspense>` for lazy loading components.
- Avoid prop spreading (`{...props}`) except for forwarding HTML attributes to the underlying DOM element. Explicit props make component APIs clear.
- Use `React.memo` sparingly and only when profiling shows unnecessary re-renders. Premature memoization adds complexity without measurable benefit.
