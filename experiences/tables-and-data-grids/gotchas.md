# Gotchas: Tables & Data Grids

## Contents

- [Loading All Data Client-Side](#loading-all-data-client-side)
- [COUNT(*) Performance Issues](#count-performance-issues)
- [Pagination + Sorting Inconsistency](#pagination-sorting-inconsistency)
- [Filter State Lost on Navigation](#filter-state-lost-on-navigation)
- [Column Reordering Not Persisted](#column-reordering-not-persisted)
- [Inline Editing Without Optimistic Lock](#inline-editing-without-optimistic-lock)
- [Virtual Scrolling Breaking Accessibility](#virtual-scrolling-breaking-accessibility)
- [Export Including Wrong Data](#export-including-wrong-data)
- [Mobile Tables That Are Just Squeezed Desktop Tables](#mobile-tables-that-are-just-squeezed-desktop-tables)
- [Select All Ambiguity](#select-all-ambiguity)
- [Stale Data After Background Changes](#stale-data-after-background-changes)

## Loading All Data Client-Side

**Problem**: Loading 5,000+ rows into the browser causes:
- Slow initial load (5-10+ seconds)
- High memory usage (100MB+)
- Poor scrolling performance
- Browser freezing during render

**Why It Happens**: Developer thinks "it's only 5,000 rows" without considering:
- Each row has multiple cells with complex rendering
- React/Vue overhead for thousands of components
- Browser DOM limitations
- Network transfer time for large payloads

**Solution**: Always use server-side pagination for datasets > 100 rows.

```kotlin
// ❌ Bad: Loading all data
@GetMapping("/api/users")
fun getAllUsers(): List<UserDto> {
    return userRepository.findAll().map { it.toDto() } // Could be 10,000+ rows
}

// ✅ Good: Server-side pagination
@GetMapping("/api/users")
fun getUsers(pageable: Pageable): ResponseEntity<Page<UserDto>> {
    return ResponseEntity.ok(userRepository.findAll(pageable).map { it.toDto() })
}
```

**When It's OK**: Small, static datasets (< 100 rows) that are already loaded for other purposes.

## COUNT(*) Performance Issues

**Problem**: `COUNT(*)` queries on large PostgreSQL tables can take 5-30+ seconds, blocking table load.

**Why It Happens**: PostgreSQL must scan the entire table (or index) to count rows, especially with filters applied.

**Example**:

```kotlin
// ❌ Slow: COUNT(*) on 10M row table with filter
@GetMapping
fun getUsers(
    @RequestParam status: UserStatus?,
    pageable: Pageable
): ResponseEntity<Page<UserDto>> {
    val spec = UserSpecifications.hasStatus(status)
    val page = userRepository.findAll(spec, pageable) // Includes COUNT(*)
    return ResponseEntity.ok(page.map { it.toDto() })
}
```

**Solutions**:

1. **Use `Slice<T>` instead of `Page<T>`** (skip count):

```kotlin
// ✅ Faster: No count query
@GetMapping
fun getUsers(pageable: Pageable): ResponseEntity<Slice<UserDto>> {
    val slice = userRepository.findAll(pageable)
    return ResponseEntity.ok(slice.map { it.toDto() })
}
```

2. **Estimated counts** for very large tables:

```kotlin
// ✅ Estimated count (PostgreSQL)
@Query("SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname = 'users'", nativeQuery = true)
fun getEstimatedCount(): Long
```

3. **Cached counts** that update periodically:

```kotlin
@Service
class UserCountCache {
    private var cachedCount: Long = 0
    private var lastUpdate: Instant = Instant.now()
    
    fun getCount(): Long {
        if (Duration.between(lastUpdate, Instant.now()).toMinutes() > 5) {
            cachedCount = userRepository.count()
            lastUpdate = Instant.now()
        }
        return cachedCount
    }
}
```

4. **Indexed count columns** for filtered counts:

```kotlin
// Add indexed status column count
@Entity
class UserCountByStatus(
    @Id val status: UserStatus,
    val count: Long
)

// Update via scheduled job
@Scheduled(fixedRate = 60000) // Every minute
fun updateCounts() {
    // Batch update counts
}
```

## Pagination + Sorting Inconsistency

**Problem**: User is on page 3, changes sort order, but page doesn't reset to 1. They see page 3 of the newly sorted data, which may be empty or confusing.

**Why It Happens**: Sort change doesn't reset page number.

**Example**:

```vue
// ❌ Bad: Sort doesn't reset page
const handleSort = (field) => {
  sortField.value = field
  fetchUsers() // Still on page 3!
}

// ✅ Good: Reset page when sort changes
const handleSort = (field) => {
  sortField.value = field
  page.value = 0 // Reset to first page
  fetchUsers()
}
```

**Rule**: Reset page to 0/1 when:
- Filters change
- Sort changes
- Search query changes

**Exception**: Don't reset page when only page size changes (user explicitly changed size, they may want to stay on current page if possible).

## Filter State Lost on Navigation

**Problem**: User applies filters, clicks a row to view details, then clicks back button. Filters are gone, user must reapply them.

**Why It Happens**: Filter state stored in component state or memory, not persisted in URL or browser history.

**Solution**: Encode filters in URL query parameters.

```vue
// ❌ Bad: Filters in component state only
const filters = ref({ name: '', status: null })

// ✅ Good: Filters in URL
const route = useRoute()
const filters = computed(() => ({
  name: route.query.name?.toString() || '',
  status: route.query.status?.toString() || null
}))

const applyFilters = () => {
  router.push({
    query: {
      ...route.query,
      ...filters.value,
      page: 0
    }
  })
}
```

**Bonus**: URL-based filters enable shareable filtered views. User can copy URL and share with team.

## Column Reordering Not Persisted

**Problem**: User customizes column order and visibility, refreshes page, and columns revert to default order.

**Why It Happens**: Column preferences stored only in component state or localStorage without user association.

**Solution**: Persist column preferences per user in backend.

```kotlin
// ✅ Backend: Store preferences
@Entity
class UserTablePreferences(
    @Id @GeneratedValue val id: Long,
    val userId: Long,
    val tableName: String,
    val visibleColumns: List<String>,
    val columnOrder: List<String>,
    val columnWidths: Map<String, Int>
)

@GetMapping("/api/users/preferences")
fun getPreferences(@AuthenticationPrincipal user: User): UserTablePreferences {
    return preferencesRepository.findByUserIdAndTableName(user.id, "users")
        ?: UserTablePreferences(0, user.id, "users", defaultColumns, defaultOrder, emptyMap())
}

@PostMapping("/api/users/preferences")
fun savePreferences(
    @AuthenticationPrincipal user: User,
    @RequestBody preferences: UserTablePreferences
) {
    preferencesRepository.save(preferences.copy(userId = user.id))
}
```

**Frontend**:

```vue
<script setup>
const loadPreferences = async () => {
  const prefs = await fetch('/api/users/preferences').then(r => r.json())
  columns.value = reorderColumns(prefs.columnOrder)
  columns.value.forEach(col => {
    col.visible = prefs.visibleColumns.includes(col.id)
    col.width = prefs.columnWidths[col.id]
  })
}

const savePreferences = async () => {
  await fetch('/api/users/preferences', {
    method: 'POST',
    body: JSON.stringify({
      tableName: 'users',
      visibleColumns: columns.value.filter(c => c.visible).map(c => c.id),
      columnOrder: columns.value.map(c => c.id),
      columnWidths: Object.fromEntries(
        columns.value.map(c => [c.id, c.width])
      )
    })
  })
}
</script>
```

## Inline Editing Without Optimistic Lock

**Problem**: Two users edit the same row simultaneously. Last write wins silently, first user's changes are lost without notification.

**Why It Happens**: No version checking or optimistic locking mechanism.

**Example**:

```kotlin
// ❌ Bad: No conflict detection
@PatchMapping("/{id}")
fun updateUser(@PathVariable id: Long, @RequestBody dto: UpdateUserDto): UserDto {
    val user = userRepository.findById(id).orElseThrow()
    user.name = dto.name // Overwrites without checking version
    return userRepository.save(user).toDto()
}
```

**Solution**: Use optimistic locking with `@Version` annotation.

```kotlin
// ✅ Good: Optimistic locking
@Entity
class User(
    @Id val id: Long,
    var name: String,
    @Version val version: Long // Optimistic lock version
)

@PatchMapping("/{id}")
fun updateUser(
    @PathVariable id: Long,
    @RequestBody dto: UpdateUserDto,
    @RequestHeader("If-Match") expectedVersion: Long?
): ResponseEntity<UserDto> {
    val user = userRepository.findById(id).orElseThrow()
    
    if (expectedVersion != null && user.version != expectedVersion) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .body(UserDto(user.id, user.name, user.version)) // Return current state
    }
    
    user.name = dto.name
    val updated = userRepository.save(user)
    
    return ResponseEntity.ok()
        .eTag(updated.version.toString()) // Return new version
        .body(updated.toDto())
}
```

**Frontend**:

```vue
<script setup>
const editUser = async (user) => {
  try {
    const response = await fetch(`/api/users/${user.id}`, {
      method: 'PATCH',
      headers: {
        'If-Match': user.version.toString() // Send expected version
      },
      body: JSON.stringify({ name: newName })
    })
    
    if (response.status === 409) {
      // Conflict - show error, refresh data
      showError('User was modified by another user. Refreshing...')
      await fetchUsers()
    } else {
      const updated = await response.json()
      user.version = response.headers.get('ETag') // Update version
    }
  } catch (error) {
    showError('Failed to update user')
  }
}
</script>
```

## Virtual Scrolling Breaking Accessibility

**Problem**: Virtual scrolling only renders visible rows. Screen readers can't access off-screen rows, breaking accessibility.

**Why It Happens**: Screen readers need all rows in DOM to navigate. Virtual scrolling removes non-visible rows from DOM.

**Solutions**:

1. **Use `aria-rowcount` and `aria-rowindex`**:

```vue
<template>
  <tbody role="rowgroup" :aria-rowcount="totalRows">
    <tr
      v-for="virtualRow in virtualRows"
      :key="virtualRow.key"
      :aria-rowindex="virtualRow.index + 1"
    >
      <!-- Row content -->
    </tr>
  </tbody>
</template>
```

2. **Provide "Show all" option** for screen reader users:

```vue
<template>
  <div>
    <label>
      <input
        type="checkbox"
        v-model="showAllRows"
        @change="toggleVirtualScrolling"
      />
      Show all rows (for screen readers)
    </label>
  </div>
</template>

<script setup>
const showAllRows = ref(false)

const toggleVirtualScrolling = () => {
  if (showAllRows.value) {
    // Disable virtual scrolling, render all rows
    virtualScrollingEnabled.value = false
  } else {
    virtualScrollingEnabled.value = true
  }
}
</script>
```

3. **Consider pagination instead** for accessibility-critical tables. Pagination is more accessible than virtual scrolling.

## Export Including Wrong Data

**Problem**: User filters table to 50 rows, exports, and receives 10,000 rows (all data, not filtered).

**Why It Happens**: Export endpoint doesn't respect filters, or frontend doesn't pass filters to export endpoint.

**Example**:

```kotlin
// ❌ Bad: Export ignores filters
@GetMapping("/export")
fun exportUsers(response: HttpServletResponse) {
    val users = userRepository.findAll() // All users!
    // Export all 10,000 rows
}

// ✅ Good: Export respects filters
@GetMapping("/export")
fun exportUsers(
    @RequestParam(required = false) name: String?,
    @RequestParam(required = false) status: UserStatus?,
    response: HttpServletResponse
) {
    val spec = UserSpecifications.hasName(name)
        .and(UserSpecifications.hasStatus(status))
    val users = userRepository.findAll(spec) // Only filtered users
    // Export filtered rows
}
```

**Frontend**:

```vue
<script setup>
const exportToCSV = async () => {
  // ✅ Pass current filters to export endpoint
  const params = new URLSearchParams()
  if (filters.value.name) params.set('name', filters.value.name)
  if (filters.value.status) params.set('status', filters.value.status)
  
  const response = await fetch(`/api/users/export?${params.toString()}`)
  const blob = await response.blob()
  // Download blob
}
</script>
```

**Clarification**: Make it clear in UI whether export includes:
- Current filtered view only
- All data (ignoring filters)
- Current page only vs. all filtered pages

## Mobile Tables That Are Just Squeezed Desktop Tables

**Problem**: Desktop table displayed on mobile with tiny text, horizontal scrolling, unusable interface.

**Why It Happens**: No responsive design consideration. Table is just CSS-scaled down.

**Solutions**:

1. **Stacked layout** (cards on mobile):

```vue
<template>
  <!-- Desktop: Table -->
  <table v-if="!isMobile" class="desktop-table">
    <!-- Table rows -->
  </table>
  
  <!-- Mobile: Cards -->
  <div v-else class="mobile-cards">
    <div v-for="user in users" :key="user.id" class="user-card">
      <div class="card-row">
        <span class="label">Name:</span>
        <span class="value">{{ user.name }}</span>
      </div>
      <div class="card-row">
        <span class="label">Email:</span>
        <span class="value">{{ user.email }}</span>
      </div>
    </div>
  </div>
</template>

<style>
@media (max-width: 768px) {
  .desktop-table { display: none; }
  .mobile-cards { display: block; }
}

.user-card {
  border: 1px solid #ddd;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 8px;
}

.card-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
</style>
```

2. **Horizontal scroll with sticky header** (if table must remain table-like):

```css
.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  min-width: 800px; /* Ensure table doesn't compress */
}

thead {
  position: sticky;
  top: 0;
  background: white;
}
```

3. **Column prioritization** (hide less important columns on mobile):

```vue
<script setup>
const isMobile = computed(() => window.innerWidth < 768)

const visibleColumns = computed(() => {
  if (isMobile.value) {
    return columns.value.filter(col => col.priority === 'high')
  }
  return columns.value
})
</script>
```

## Select All Ambiguity

**Problem**: "Select all" button is ambiguous. Does it select all rows on current page, or all 10,000 rows across all pages?

**Why It Happens**: No clarification of scope.

**Solutions**:

1. **Clarify scope in UI**:

```vue
<template>
  <div class="select-all-controls">
    <label>
      <input
        type="checkbox"
        :checked="allOnPageSelected"
        @change="toggleSelectAllOnPage"
      />
      Select all on this page ({{ currentPageRows.length }} items)
    </label>
    
    <button
      v-if="hasFilters"
      @click="selectAllFiltered"
      class="select-all-filtered"
    >
      Select all {{ totalFilteredCount }} filtered items
    </button>
  </div>
</template>
```

2. **Separate buttons**:

```vue
<template>
  <button @click="selectAllOnPage">
    Select all on page ({{ currentPageRows.length }})
  </button>
  <button @click="selectAllFiltered" v-if="hasFilters">
    Select all filtered ({{ totalFilteredCount }})
  </button>
</template>
```

3. **Confirmation for large selections**:

```vue
<script setup>
const selectAllFiltered = async () => {
  if (totalFilteredCount.value > 100) {
    const confirmed = confirm(
      `This will select ${totalFilteredCount.value} items. Continue?`
    )
    if (!confirmed) return
  }
  
  // Select all filtered items
  selectedRows.value = new Set(await fetchAllFilteredIds())
}
</script>
```

## Stale Data After Background Changes

**Problem**: User has table open. Another user (or system process) deletes/modifies a record. Table doesn't refresh, showing stale data.

**Why It Happens**: No refresh mechanism or real-time updates.

**Solutions**:

1. **Manual refresh button**:

```vue
<template>
  <button @click="refreshTable" data-testid="refresh-button">
    <Icon name="refresh" />
    Refresh
  </button>
</template>

<script setup>
const refreshTable = async () => {
  loading.value = true
  await fetchUsers()
  loading.value = false
  showSuccess('Table refreshed')
}
</script>
```

2. **Auto-refresh on focus**:

```vue
<script setup>
onMounted(() => {
  window.addEventListener('focus', () => {
    if (document.visibilityState === 'visible') {
      fetchUsers() // Refresh when window regains focus
    }
  })
})
</script>
```

3. **WebSocket/SSE for real-time updates**:

```vue
<script setup>
onMounted(() => {
  const eventSource = new EventSource('/api/users/events')
  
  eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data)
    if (update.type === 'USER_DELETED') {
      users.value = users.value.filter(u => u.id !== update.userId)
    } else if (update.type === 'USER_UPDATED') {
      const index = users.value.findIndex(u => u.id === update.user.id)
      if (index !== -1) {
        users.value[index] = update.user
      }
    }
  }
})
</script>
```

4. **Optimistic updates with background refresh**:

```vue
<script setup>
const deleteUser = async (id) => {
  // Optimistic update
  users.value = users.value.filter(u => u.id !== id)
  
  try {
    await fetch(`/api/users/${id}`, { method: 'DELETE' })
  } catch (error) {
    // Revert on error
    await fetchUsers()
    showError('Failed to delete user')
  }
}
</script>
```

**Best Practice**: Provide manual refresh button as baseline, add auto-refresh or real-time updates for critical data.
