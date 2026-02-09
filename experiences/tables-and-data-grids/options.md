# Options: Tables & Data Grids

## Contents

- [Table Libraries](#table-libraries)
- [Pagination Strategies](#pagination-strategies)
- [Filtering Approaches](#filtering-approaches)
- [Export Strategies](#export-strategies)
- [Recommendations](#recommendations)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Table Libraries

### TanStack Table (Vue + React)

**Description**: Headless table library providing table logic and state management. You provide the UI/styling.

**Strengths**:
- Framework agnostic (works with Vue 3, React, Solid, Svelte)
- Full control over UI/styling (works with any design system)
- Excellent TypeScript support
- Lightweight (core logic only, no UI dependencies)
- Highly customizable (sorting, filtering, pagination, column management)
- Active community and good documentation
- Free and open source

**Weaknesses**:
- Requires more setup/configuration than opinionated libraries
- No built-in UI components (you build the table markup)
- Steeper learning curve for complex features
- No built-in virtual scrolling (requires separate library)

**Best For**:
- Projects using custom design systems (Propulsion, internal components)
- Teams that want full control over table appearance
- Applications needing highly customized table behavior
- Vue 3 or React projects

**Avoid When**:
- You need a quick, out-of-the-box solution with minimal configuration
- Team lacks time/resources to build custom table UI
- You need enterprise features like Excel export, advanced filtering UI built-in

**Example**:

```vue
<script setup>
import { useVueTable, getCoreRowModel, getSortedRowModel } from '@tanstack/vue-table'

const table = useVueTable({
  data: users.value,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel()
})
</script>
```

### ag-Grid (Vue + React)

**Description**: Feature-rich commercial data grid with built-in UI, virtual scrolling, Excel export, and enterprise features.

**Strengths**:
- Comprehensive feature set (sorting, filtering, grouping, pivoting, Excel export)
- Built-in virtual scrolling (handles millions of rows)
- Excellent performance out of the box
- Professional UI with minimal styling needed
- Strong documentation and support
- Free community edition available (with some limitations)

**Weaknesses**:
- Commercial license required for enterprise features
- Larger bundle size (~500KB+)
- Opinionated styling (harder to customize to match design system)
- Can be overkill for simple tables
- Learning curve for advanced features

**Best For**:
- Enterprise applications needing advanced grid features
- Large datasets requiring virtual scrolling
- Teams that need Excel export, advanced filtering UI built-in
- Applications where grid is core to the product

**Avoid When**:
- Simple tables with basic sorting/filtering needs
- Tight bundle size constraints
- Need to match specific design system exactly
- Budget constraints (enterprise features require license)

**Example**:

```vue
<template>
  <ag-grid-vue
    :columnDefs="columnDefs"
    :rowData="users"
    :pagination="true"
    :paginationPageSize="20"
  />
</template>
```

### Propulsion DataTable (Internal)

**Description**: Pax8 internal design system component for tables (if available).

**Strengths**:
- Matches Propulsion design system out of the box
- Consistent with other Pax8 applications
- Likely includes Pax8-specific patterns and best practices
- Internal support and documentation

**Weaknesses**:
- Only available for Pax8 projects
- May have limited features compared to third-party libraries
- Dependent on Propulsion design system updates
- May not support all use cases

**Best For**:
- Pax8 internal projects
- Applications using Propulsion design system
- Teams wanting consistency across Pax8 products

**Avoid When**:
- Non-Pax8 projects
- Need features not available in Propulsion DataTable
- Propulsion DataTable doesn't exist or is deprecated

### MUI DataGrid (React)

**Description**: Material-UI's data grid component for React applications.

**Strengths**:
- Integrates seamlessly with MUI design system
- Good feature set (sorting, filtering, pagination, inline editing)
- Professional appearance
- Good documentation
- Free (MUI Core) and Pro (paid) versions

**Weaknesses**:
- React only (no Vue support)
- Requires MUI design system (not suitable for non-MUI projects)
- Pro features (advanced filtering, Excel export) require paid license
- Less customizable than headless solutions

**Best For**:
- React applications already using MUI
- Teams wanting Material Design appearance
- Applications needing good balance of features and ease of use

**Avoid When**:
- Vue projects
- Not using MUI design system
- Need highly customized appearance
- Budget constraints (Pro features require license)

**Example**:

```tsx
import { DataGrid } from '@mui/x-data-grid'

function UserTable() {
  return (
    <DataGrid
      rows={users}
      columns={columns}
      pageSize={20}
      pagination
    />
  )
}
```

## Pagination Strategies

### Offset-Based (Spring Data Pageable)

**Description**: Pagination using `page` and `size` parameters. Server returns specific page of results.

**Strengths**:
- Simple to implement and understand
- Works well with Spring Data `Pageable`
- Users can jump to specific pages
- Standard REST pattern
- Good for datasets up to ~1M rows

**Weaknesses**:
- Performance degrades on very large datasets (offset 10,000+ is slow)
- Inconsistent results if data changes during pagination (rows shift)
- `COUNT(*)` queries can be slow on large tables

**Best For**:
- Most B2B SaaS applications
- Datasets < 1M rows
- When users need to jump to specific pages
- Standard REST APIs

**Avoid When**:
- Very large datasets (> 1M rows) where offset becomes slow
- Real-time data that changes frequently (inconsistent pagination)
- Infinite scroll implementations (cursor-based better)

**Example**:

```kotlin
@GetMapping("/api/users")
fun getUsers(@PageableDefault(size = 20) pageable: Pageable): Page<UserDto> {
    return userRepository.findAll(pageable).map { it.toDto() }
}
```

### Cursor-Based

**Description**: Pagination using a cursor (typically ID or timestamp). Server returns results after the cursor.

**Strengths**:
- Consistent results even if data changes
- Fast performance on very large datasets (no offset calculation)
- Good for infinite scroll
- No `COUNT(*)` query needed

**Weaknesses**:
- More complex to implement
- Users can't jump to specific pages (only next/previous)
- Requires sortable, unique cursor field
- Less intuitive for users expecting page numbers

**Best For**:
- Very large datasets (> 1M rows)
- Real-time data feeds
- Infinite scroll implementations
- Social media feeds, activity logs

**Avoid When**:
- Users need to jump to specific pages
- Datasets are small-medium (< 100K rows)
- Team lacks experience with cursor pagination

**Example**:

```kotlin
@GetMapping("/api/users/cursor")
fun getUsersCursor(
    @RequestParam(required = false) cursor: Long?,
    @RequestParam(defaultValue = "20") limit: Int
): CursorPage<UserDto> {
    val users = if (cursor == null) {
        userRepository.findFirstNOrderedById(limit)
    } else {
        userRepository.findAfterCursor(cursor, limit)
    }
    val nextCursor = users.lastOrNull()?.id
    return CursorPage(users, nextCursor)
}
```

### Infinite Scroll

**Description**: Automatically load more data as user scrolls near bottom. Can use offset or cursor pagination.

**Strengths**:
- Smooth, continuous browsing experience
- No pagination controls needed (saves UI space)
- Good for mobile interfaces
- Users can browse large datasets without clicking

**Weaknesses**:
- Hard to jump to specific content
- No sense of progress ("how much more?")
- Can cause performance issues if not implemented carefully
- Accessibility challenges (keyboard navigation, screen readers)

**Best For**:
- Social media feeds, activity logs
- Mobile-first applications
- Browsing/exploration use cases (not finding specific items)

**Avoid When**:
- Users need to find specific records quickly
- Accessibility is critical
- Dataset is small (pagination buttons are clearer)

**Example**:

```vue
<script setup>
const loadMore = async () => {
  if (loading.value || !hasMore.value) return
  loading.value = true
  const data = await fetchNextPage()
  users.value.push(...data.items)
  hasMore.value = data.hasNext
  loading.value = false
}

const handleScroll = () => {
  if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
    loadMore()
  }
}
</script>
```

### Client-Side Pagination

**Description**: Load all data client-side, paginate in browser memory.

**Strengths**:
- Fast pagination (no server requests)
- Simple to implement
- Works offline (if data already loaded)

**Weaknesses**:
- Only suitable for small datasets (< 100 rows)
- Slow initial load for larger datasets
- High memory usage
- Doesn't scale

**Best For**:
- Small, static datasets (< 100 rows)
- Data already loaded for other purposes
- Offline-first applications with limited data

**Avoid When**:
- Datasets > 100 rows
- Data changes frequently
- Need to scale to larger datasets

**Example**:

```vue
<script setup>
const allUsers = ref([])
const page = ref(0)
const size = ref(20)

const paginatedUsers = computed(() => {
  const start = page.value * size.value
  return allUsers.value.slice(start, start + size.value)
})
</script>
```

## Filtering Approaches

### URL Query Params + Spring Data Specification

**Description**: Filters encoded in URL query parameters, converted to Spring Data JPA Specifications on backend.

**Strengths**:
- Shareable filtered views (users can share URLs)
- Bookmarkable state
- Works with browser back/forward
- Type-safe with Specifications
- Standard REST pattern

**Weaknesses**:
- URL can become long with many filters
- Requires Specification implementation for each filter type
- More complex than simple query params

**Best For**:
- Most B2B SaaS applications
- When filters need to be shareable
- RESTful API design
- Type-safe filtering requirements

**Avoid When**:
- Very complex filters that don't fit in URL
- Need for filter presets/saved views (though can combine with this approach)

**Example**:

```kotlin
@GetMapping
fun getUsers(
    @RequestParam(required = false) name: String?,
    @RequestParam(required = false) status: UserStatus?,
    pageable: Pageable
): Page<UserDto> {
    val spec = UserSpecifications.hasName(name)
        .and(UserSpecifications.hasStatus(status))
    return userRepository.findAll(spec, pageable).map { it.toDto() }
}
```

### Dedicated Filter API

**Description**: Separate endpoint for applying filters, returns filter results. Filters stored server-side.

**Strengths**:
- Can handle very complex filters
- Filter presets/saved views easy to implement
- Can optimize filter queries separately
- Filters don't clutter URL

**Weaknesses**:
- Not shareable via URL
- More complex architecture
- Requires session/state management
- Less RESTful

**Best For**:
- Very complex filtering requirements
- Applications with saved filter presets
- When URL length is a concern

**Avoid When**:
- Simple filtering needs
- Want shareable filtered views
- Prefer RESTful design

### Client-Side Filtering

**Description**: Filter data in browser after loading (all or paginated data).

**Strengths**:
- Instant filtering (no server requests)
- Works offline
- Simple to implement

**Weaknesses**:
- Only works for small datasets (< 1000 rows)
- Requires loading all filterable data
- Can't filter on server-side only fields
- Performance issues with large datasets

**Best For**:
- Small datasets already loaded client-side
- Offline-first applications
- Quick prototypes

**Avoid When**:
- Datasets > 1000 rows
- Need server-side filtering
- Data changes frequently

## Export Strategies

### Client-Side CSV (Small Datasets)

**Description**: Generate CSV file in browser from loaded data.

**Strengths**:
- Instant export (no server request)
- Works offline
- Simple to implement
- No server load

**Weaknesses**:
- Only works for small datasets (< 1000 rows)
- Limited to data already loaded
- Browser memory limitations
- Can't export server-side only fields

**Best For**:
- Small datasets (< 1000 rows)
- Quick exports of current page/filtered view
- Offline-first applications

**Avoid When**:
- Large datasets (> 1000 rows)
- Need to export all filtered data (not just current page)
- Export is frequent/performance critical

**Example**:

```vue
<script setup>
const exportToCSV = () => {
  const headers = columns.value.map(c => c.label).join(',')
  const rows = users.value.map(user => 
    columns.value.map(c => `"${user[c.id]}"`).join(',')
  ).join('\n')
  
  const csv = `${headers}\n${rows}`
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'users.csv'
  a.click()
}
</script>
```

### Server-Side CSV/Excel (Large)

**Description**: Generate export file on server, stream to client.

**Strengths**:
- Handles large datasets (millions of rows)
- Can export all filtered data (not just current page)
- Server-side processing (no browser memory issues)
- Can include server-side only fields/calculations
- Supports Excel format with formatting

**Weaknesses**:
- Requires server request (slower for large exports)
- Server load for large exports
- More complex implementation
- May need async processing for very large exports

**Best For**:
- Large datasets (> 1000 rows)
- Exporting all filtered data
- Enterprise reporting needs
- Excel format requirements

**Avoid When**:
- Small datasets (< 100 rows) where client-side is sufficient
- Need instant export

**Example**:

```kotlin
@GetMapping("/export")
fun exportUsers(
    @RequestParam(required = false) name: String?,
    response: HttpServletResponse
) {
    val spec = UserSpecifications.hasName(name)
    val users = userRepository.findAll(spec)
    
    response.contentType = "text/csv"
    response.setHeader("Content-Disposition", "attachment; filename=users.csv")
    
    val writer = response.writer
    writer.println("Name,Email,Status")
    users.forEach { user ->
        writer.println("${user.name},${user.email},${user.status}")
    }
}
```

### Async Export with Notification

**Description**: Large exports processed asynchronously, user notified when ready.

**Strengths**:
- Handles very large exports (millions of rows) without blocking
- Better user experience (no long wait)
- Can process exports in background/queue
- User can continue working while export processes

**Weaknesses**:
- More complex implementation (job queue, status tracking)
- Requires notification system
- User must return to download (can't leave page)

**Best For**:
- Very large exports (> 100K rows)
- Frequent exports that could impact server performance
- Enterprise reporting scenarios

**Avoid When**:
- Small exports (< 10K rows) where synchronous is fine
- Team lacks infrastructure for async jobs

**Example**:

```kotlin
@PostMapping("/export")
fun requestExport(@RequestBody filters: ExportFilters): ResponseEntity<ExportJob> {
    val jobId = exportService.queueExport(filters)
    return ResponseEntity.accepted().body(ExportJob(jobId, "PENDING"))
}

@GetMapping("/export/{jobId}/status")
fun getExportStatus(@PathVariable jobId: String): ResponseEntity<ExportStatus> {
    val status = exportService.getStatus(jobId)
    return ResponseEntity.ok(status)
}

@GetMapping("/export/{jobId}/download")
fun downloadExport(@PathVariable jobId: String, response: HttpServletResponse) {
    val file = exportService.getExportFile(jobId)
    // Stream file to response
}
```

## Recommendations

### Default Recommendation

**For most B2B SaaS applications**:

1. **Table Library**: **TanStack Table** (Vue or React)
   - Headless, flexible, works with any design system
   - Good balance of features and customization
   - Free, active community

2. **Pagination**: **Offset-based (Spring Data Pageable)**
   - Standard, well-supported pattern
   - Works for most datasets (< 1M rows)
   - Users can jump to specific pages

3. **Filtering**: **URL Query Params + Spring Data Specification**
   - Shareable filtered views
   - Type-safe, RESTful
   - Works with browser navigation

4. **Export**: **Server-side CSV** (synchronous for < 10K rows, async for larger)
   - Handles filtered data correctly
   - Works for datasets of any size
   - Can upgrade to async for very large exports

### When to Deviate

- **Very large datasets (> 1M rows)**: Consider cursor-based pagination
- **Need advanced grid features**: Consider ag-Grid or MUI DataGrid Pro
- **Using Propulsion design system**: Use Propulsion DataTable if available
- **Mobile-first app**: Consider infinite scroll
- **Real-time data**: Use cursor-based pagination or WebSocket updates

## Synergies

### API Design (Pagination)

Table pagination patterns align with [api-design](../../facets/api-design/) pagination standards:
- Use consistent pagination parameters (`page`, `size`, `sort`)
- Return standard pagination response format (`Page<T>` or `Slice<T>`)
- Document pagination behavior in API specs

### Search and Discovery

Tables integrate with [search-and-discovery](../search-and-discovery/) experience:
- Table filters complement search functionality
- Search results can be displayed in table format
- Filter state can be combined with search queries

### Performance

Table performance considerations align with [performance](../../facets/performance/) best practices:
- Virtual scrolling for large datasets
- Server-side pagination to reduce data transfer
- Lazy loading and code splitting for table components
- Query optimization for sortable/filterable columns

## Evolution Triggers

### When to Upgrade from Simple Table

Upgrade to sortable table when:
- Users request ability to find records by sorting
- Dataset grows beyond scan-able size (< 50 rows)

### When to Add Filtering

Add filtering when:
- Users complain about too many results
- Dataset exceeds 100-200 rows
- Users need to narrow results by specific criteria

### When to Add Pagination

Add pagination when:
- Dataset exceeds 100-200 rows
- Table load time becomes slow (> 1 second)
- Users complain about scrolling through many rows

### When to Add Inline Editing

Add inline editing when:
- Users frequently update individual records
- Users request "quick edit" functionality
- Bulk editing is overkill for use case

### When to Upgrade to Full Data Grid

Upgrade to data grid when:
- Users need column customization
- Users need bulk operations
- Users need advanced filtering UI
- Dataset exceeds 10K rows (virtual scrolling needed)
- Power users request enterprise features (grouping, pivoting, Excel export)

### When to Switch Pagination Strategies

Switch from offset to cursor-based when:
- Dataset exceeds 1M rows and offset becomes slow
- Data changes frequently (inconsistent pagination issues)
- Implementing infinite scroll for very large datasets

Switch from client-side to server-side when:
- Dataset exceeds 100 rows
- Initial load time becomes slow
- Memory usage becomes concern
