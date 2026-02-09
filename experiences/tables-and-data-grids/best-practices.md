# Best Practices: Tables & Data Grids

## Contents

- [Start Simple, Add Complexity](#start-simple-add-complexity)
- [Server-Side Pagination](#server-side-pagination)
- [URL State Encoding](#url-state-encoding)
- [Sticky Headers](#sticky-headers)
- [Loading States](#loading-states)
- [Empty States](#empty-states)
- [Column Width Strategy](#column-width-strategy)
- [Keyboard Navigation](#keyboard-navigation)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Filter Over Pagination](#filter-over-pagination)
- [Density Options](#density-options)
- [Accessibility](#accessibility)

## Start Simple, Add Complexity

Begin with the simplest table implementation that meets your current needs. Add features incrementally as requirements emerge.

**Progression**:
1. **HTML table** → Basic data display
2. **Sortable columns** → When users need to find records
3. **Filtering** → When datasets grow beyond scan-able size
4. **Pagination** → When datasets exceed 100-200 rows
5. **Inline editing** → When users need quick updates
6. **Full data grid** → When power users need advanced features

**Anti-pattern**: Building a full-featured data grid when a simple sortable table would suffice. This adds unnecessary complexity, maintenance burden, and potential performance issues.

**Example**: Start with a basic table:

```vue
<template>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.name }}</td>
        <td>{{ user.email }}</td>
      </tr>
    </tbody>
  </table>
</template>
```

Only add sorting when users request it:

```vue
<template>
  <table>
    <thead>
      <tr>
        <th @click="sortBy('name')">
          Name
          <span v-if="sortField === 'name'">
            {{ sortDirection === 'asc' ? '↑' : '↓' }}
          </span>
        </th>
        <!-- ... -->
      </tr>
    </thead>
  </table>
</template>
```

## Server-Side Pagination

**Rule**: Always use server-side pagination for datasets larger than 100 rows. Never load unbounded data client-side.

**Why**:
- Performance: Loading 10,000 rows into the browser causes slow initial load, high memory usage, and poor user experience
- Scalability: As data grows, client-side pagination becomes unusable
- Network efficiency: Only fetch what's needed

**Implementation (Spring Boot)**:

```kotlin
@GetMapping("/api/users")
fun getUsers(
    @PageableDefault(size = 20, sort = ["name"]) pageable: Pageable
): ResponseEntity<Page<UserDto>> {
    return ResponseEntity.ok(userRepository.findAll(pageable).map { it.toDto() })
}
```

**Frontend (Vue 3)**:

```vue
<script setup>
const page = ref(0)
const size = ref(20)
const users = ref([])
const totalElements = ref(0)

const fetchUsers = async () => {
  const response = await fetch(`/api/users?page=${page.value}&size=${size.value}`)
  const data = await response.json()
  users.value = data.content
  totalElements.value = data.totalElements
}

const goToPage = (newPage) => {
  page.value = newPage
  fetchUsers()
}
</script>
```

**Exception**: Client-side pagination is acceptable for:
- Small, static datasets (< 100 rows)
- Data already loaded for other purposes (e.g., for filtering)
- Offline-first applications with limited data

## URL State Encoding

Encode table state (page, sort, filters) in URL query parameters. This enables:
- **Shareable URLs**: Users can share filtered/sorted table views
- **Bookmarkable state**: Users can bookmark specific table configurations
- **Browser navigation**: Back/forward buttons work correctly
- **Deep linking**: Direct links to specific table states

**Implementation**:

```vue
<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tableState = computed(() => ({
  page: parseInt(route.query.page?.toString() || '0'),
  size: parseInt(route.query.size?.toString() || '20'),
  sort: route.query.sort?.toString() || null,
  filters: {
    name: route.query.name?.toString() || '',
    status: route.query.status?.toString() || null
  }
}))

const updateURL = (updates) => {
  router.push({
    query: {
      ...route.query,
      ...updates
    }
  })
}

// Update URL when filters change
const applyFilters = () => {
  updateURL({
    ...filters.value,
    page: 0 // Reset to first page
  })
  fetchUsers()
}

// Watch URL changes to sync state
watch(() => route.query, (newQuery) => {
  page.value = parseInt(newQuery.page?.toString() || '0')
  filters.value.name = newQuery.name?.toString() || ''
  fetchUsers()
}, { immediate: true })
</script>
```

**URL Example**: `/users?page=2&size=50&sort=-createdDate&status=ACTIVE&name=john`

## Sticky Headers

For scrollable tables, make headers sticky so column labels remain visible while scrolling.

**CSS Implementation**:

```css
.table-container {
  max-height: 600px;
  overflow-y: auto;
}

table thead {
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

**Vue/React**: Use CSS `position: sticky` on `<thead>` element. Ensure proper z-index and background color to prevent content showing through.

**Why**: Users lose context of what each column represents when headers scroll out of view, especially for wide tables with many columns.

## Loading States

Show skeleton rows or a loading indicator during data fetch. Never show a blank table or spinner overlay that blocks interaction.

**Skeleton Rows (Preferred)**:

```vue
<template>
  <tbody v-if="loading">
    <tr v-for="i in 5" :key="i" class="skeleton-row">
      <td v-for="j in columns.length" :key="j">
        <div class="skeleton" />
      </td>
    </tr>
  </tbody>
  <tbody v-else>
    <!-- Actual rows -->
  </tbody>
</template>

<style>
.skeleton {
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

**Why Skeleton Rows**:
- Maintains table structure (users see what's coming)
- Perceived performance is better (feels faster)
- Doesn't block other UI elements
- More professional appearance

**Anti-pattern**: Spinner overlay that blocks the entire table. Users can't interact with other parts of the page while waiting.

## Empty States

Distinguish between "no data matches your filters" and "no data exists yet." Provide actionable guidance in each case.

**No Results (Filters Applied)**:

```vue
<template>
  <tbody v-if="hasFilters && users.length === 0">
    <tr>
      <td :colspan="columns.length" class="empty-state">
        <div>
          <p>No results match your filters.</p>
          <button @click="clearFilters">Clear all filters</button>
        </div>
      </td>
    </tr>
  </tbody>
</template>
```

**No Data Yet**:

```vue
<template>
  <tbody v-if="!hasFilters && users.length === 0">
    <tr>
      <td :colspan="columns.length" class="empty-state">
        <div>
          <p>No users yet.</p>
          <button @click="createUser">Create your first user</button>
        </div>
      </td>
    </tr>
  </tbody>
</template>
```

**Why**: Users need different actions based on context. If filters are applied, they should clear filters. If no data exists, they should create data.

## Column Width Strategy

Use a combination of fixed, flexible, and resizable column widths:

- **Fixed width**: Key columns (ID, status icons, actions) that should always be visible
- **Flexible width**: Content columns that adapt to available space
- **Resizable**: Allow power users to customize column widths

**CSS Implementation**:

```css
table {
  table-layout: fixed; /* Enables column width control */
  width: 100%;
}

table th:nth-child(1) { width: 80px; } /* ID - fixed */
table th:nth-child(2) { width: 200px; min-width: 150px; } /* Name - fixed with min */
table th:nth-child(3) { width: auto; } /* Email - flexible */
table th:nth-child(4) { width: 100px; } /* Status - fixed */
```

**Resizable Columns**:

```vue
<template>
  <th
    v-for="col in columns"
    :key="col.id"
    :style="{ width: col.width || 'auto' }"
    @mousedown="startResize(col, $event)"
  >
    {{ col.label }}
    <div class="resize-handle" />
  </th>
</template>

<script setup>
const startResize = (column, event) => {
  const startX = event.clientX
  const startWidth = column.width ? parseInt(column.width) : 200
  
  const handleMouseMove = (e) => {
    const diff = e.clientX - startX
    column.width = `${startWidth + diff}px`
  }
  
  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    saveColumnPreferences()
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}
</script>
```

## Keyboard Navigation

Implement comprehensive keyboard navigation for power users:

- **Arrow keys**: Move between cells (← → ↑ ↓)
- **Enter**: Enter edit mode (if cell is editable)
- **Tab**: Move to next editable cell
- **Escape**: Cancel edit, exit edit mode
- **Home/End**: Navigate to first/last cell in row
- **Page Up/Down**: Navigate between pages (if paginated)

**Implementation**:

```vue
<script setup>
const handleKeyDown = (event, rowIndex, cellIndex) => {
  switch (event.key) {
    case 'ArrowRight':
      event.preventDefault()
      focusCell(rowIndex, cellIndex + 1)
      break
    case 'ArrowLeft':
      event.preventDefault()
      focusCell(rowIndex, cellIndex - 1)
      break
    case 'ArrowDown':
      event.preventDefault()
      focusCell(rowIndex + 1, cellIndex)
      break
    case 'ArrowUp':
      event.preventDefault()
      focusCell(rowIndex - 1, cellIndex)
      break
    case 'Enter':
      if (isEditable(rowIndex, cellIndex)) {
        startEdit(rowIndex, cellIndex)
      }
      break
    case 'Escape':
      cancelEdit()
      break
  }
}

const focusCell = (rowIndex, cellIndex) => {
  const cell = document.querySelector(
    `tbody tr:nth-child(${rowIndex + 1}) td:nth-child(${cellIndex + 1})`
  )
  cell?.focus()
}
</script>

<template>
  <td
    :tabindex="isEditable(rowIndex, cellIndex) ? 0 : -1"
    @keydown="handleKeyDown($event, rowIndex, cellIndex)"
  >
    <!-- Cell content -->
  </td>
</template>
```

**Why**: Power users rely on keyboard navigation for efficiency. Mouse-only interaction slows them down significantly.

## Stack-Specific Guidance

### Vue 3

**Libraries**:
- **TanStack Table (Vue)**: Headless table library, full control over UI
- **Propulsion DataTable**: Internal design system component (if available)
- **ag-Grid Vue**: Feature-rich commercial option for complex grids

**Example (TanStack Table Vue)**:

```vue
<script setup>
import { useVueTable, getCoreRowModel } from '@tanstack/vue-table'

const columns = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'email', header: 'Email' }
]

const table = useVueTable({
  data: users.value,
  columns,
  getCoreRowModel: getCoreRowModel()
})
</script>

<template>
  <table>
    <thead>
      <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
        <th v-for="header in headerGroup.headers" :key="header.id">
          {{ header.column.columnDef.header }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in table.getRowModel().rows" :key="row.id">
        <td v-for="cell in row.getVisibleCells()" :key="cell.id">
          {{ cell.getValue() }}
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

### React

**Libraries**:
- **TanStack Table (React)**: Headless, most popular choice
- **MUI DataGrid**: Material-UI component, good for MUI-based apps
- **ag-Grid React**: Commercial option for enterprise features

**Example (TanStack Table React)**:

```tsx
import { useReactTable, getCoreRowModel } from '@tanstack/react-table'

function UserTable({ users }) {
  const columns = [
    { accessorKey: 'name', header: 'Name' },
    { accessorKey: 'email', header: 'Email' }
  ]

  const table = useReactTable({
    data: users,
    columns,
    getCoreRowModel: getCoreRowModel()
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id}>{header.column.columnDef.header}</th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>{cell.getValue()}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

### Spring Boot

**Pagination**:
- Use `Pageable` interface for offset-based pagination
- Use `Page<T>` response wrapper
- Use `@PageableDefault` for default pagination parameters

**Filtering**:
- Use Spring Data JPA Specifications for dynamic, type-safe filters
- Use Criteria API for complex queries
- Consider query DSL (Querydsl, JOOQ) for very complex filtering

**Example**:

```kotlin
@GetMapping
fun getUsers(
    @RequestParam(required = false) name: String?,
    @RequestParam(required = false) status: UserStatus?,
    @PageableDefault(size = 20, sort = ["name"]) pageable: Pageable
): ResponseEntity<Page<UserDto>> {
    val spec = UserSpecifications.hasName(name)
        .and(UserSpecifications.hasStatus(status))
    
    return ResponseEntity.ok(
        userRepository.findAll(spec, pageable).map { it.toDto() }
    )
}
```

## Filter Over Pagination

When possible, help users narrow results through filtering rather than forcing them to paginate through hundreds of pages.

**Anti-pattern**: User searches for "John" and gets 500 results across 25 pages. They must click through pages to find the right John.

**Better**: Provide robust filtering (name, status, date range, etc.) so users can narrow to 10-20 relevant results, eliminating the need for pagination.

**Implementation**: Prioritize filter UI/UX. Make filters discoverable, easy to use, and powerful enough to narrow datasets effectively.

## Density Options

Provide density options (compact, comfortable, spacious) for different user preferences and screen sizes.

**Implementation**:

```vue
<script setup>
const density = ref('comfortable') // 'compact' | 'comfortable' | 'spacious'

const densityClasses = computed(() => ({
  'table-compact': density.value === 'compact',
  'table-comfortable': density.value === 'comfortable',
  'table-spacious': density.value === 'spacious'
}))
</script>

<template>
  <div class="density-selector">
    <button @click="density = 'compact'">Compact</button>
    <button @click="density = 'comfortable'">Comfortable</button>
    <button @click="density = 'spacious'">Spacious</button>
  </div>
  <table :class="densityClasses">
    <!-- Table content -->
  </table>
</template>

<style>
.table-compact td { padding: 4px 8px; font-size: 12px; }
.table-comfortable td { padding: 8px 16px; font-size: 14px; }
.table-spacious td { padding: 12px 24px; font-size: 16px; }
</style>
```

**Why**: Different users have different preferences. Power users may prefer compact to see more data, while others prefer spacious for readability.

## Accessibility

Ensure tables are accessible to screen reader users and keyboard-only users:

1. **Proper markup**: Use semantic HTML (`<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>`)
2. **Column headers**: Use `scope="col"` on `<th>` elements
3. **Row headers**: Use `scope="row"` if first column acts as row identifier
4. **Sortable columns**: Use `aria-sort` attribute (`ascending`, `descending`, `none`)
5. **Row selection**: Use `aria-checked` on checkboxes, `aria-selected` on rows
6. **Loading states**: Use `aria-busy="true"` during data fetch
7. **Empty states**: Provide descriptive text, not just visual indicators

**Example**:

```vue
<template>
  <table>
    <thead>
      <tr>
        <th scope="col" aria-sort="none">
          <button @click="sortBy('name')">
            Name
            <span aria-hidden="true">{{ sortIndicator }}</span>
          </button>
        </th>
      </tr>
    </thead>
    <tbody aria-busy="loading">
      <tr v-for="user in users" :key="user.id" :aria-selected="isSelected(user.id)">
        <td>{{ user.name }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
const sortIndicator = computed(() => {
  if (sortField.value !== 'name') return ''
  return sortDirection.value === 'asc' ? '↑' : '↓'
})

const sortBy = (field) => {
  // Update sortField and sortDirection
  // Update aria-sort attribute
}
</script>
```

**Testing**: Use screen readers (NVDA, JAWS, VoiceOver) and keyboard-only navigation to verify accessibility.
