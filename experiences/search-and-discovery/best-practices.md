# Search & Discovery -- Best Practices

## Contents

- [Don't Make Users Think About Search Syntax](#dont-make-users-think-about-search-syntax)
- [Show Results as Users Type](#show-results-as-users-type)
- [Handle Typos Gracefully](#handle-typos-gracefully)
- [Show Meaningful Zero-Result States](#show-meaningful-zero-result-states)
- [Highlight Matched Terms in Results](#highlight-matched-terms-in-results)
- [Remember Recent Searches](#remember-recent-searches)
- [Provide Clear Filter/Sort Controls](#provide-clear-filtersort-controls)
- [Distinguish Filtering from Searching](#distinguish-filtering-from-searching)
- [Performance Best Practices](#performance-best-practices)
- [Accessibility](#accessibility)
- [Mobile Considerations](#mobile-considerations)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)

## Don't Make Users Think About Search Syntax

Most users expect a simple text box that "just works." They shouldn't need to learn special syntax, boolean operators, or field-specific queries.

**Do**:
- Provide a single, obvious search box
- Accept natural language queries
- Handle the complexity on the backend

**Don't**:
- Require users to know field names (`name:John` syntax)
- Force boolean operators (`AND`, `OR`) for basic queries
- Hide search behind "Advanced Search" that's required for useful results

**Progressive Disclosure**:
- Default: simple text box
- Advanced: optional "Advanced Search" link/button that reveals filters and operators
- Power users can discover and use advanced features, but casual users aren't intimidated

## Show Results as Users Type

Type-ahead/autocomplete provides instant feedback and helps users form better queries.

**Debouncing**:
- Wait 200-300ms after user stops typing before triggering search
- Prevents excessive API calls
- Balances responsiveness with performance

**Implementation**:
```typescript
// Vue 3 Composition API example
import { ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'

const searchQuery = ref('')
const suggestions = ref([])

const debouncedSearch = useDebounceFn(async (query: string) => {
  if (query.length >= 2) {
    suggestions.value = await fetchSuggestions(query)
  } else {
    suggestions.value = []
  }
}, 250)

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery)
})
```

```typescript
// React example
import { useState, useEffect } from 'react'

function useDebounce(value: string, delay: number) {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)
    
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])
  
  return debouncedValue
}

function SearchInput() {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 250)
  
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      fetchSuggestions(debouncedQuery)
    }
  }, [debouncedQuery])
  
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />
}
```

**Minimum Characters**:
- Require 2-3 characters before showing suggestions
- Prevents overwhelming users with too many suggestions
- Reduces backend load

## Handle Typos Gracefully

Users make typos. Search should be forgiving.

**Fuzzy Matching**:
- Use search engine fuzzy matching (Levenshtein distance)
- Configure appropriate fuzziness (typically 1-2 character edits)
- Don't be too fuzzy (avoid irrelevant matches)

**"Did You Mean?" Suggestions**:
- Detect likely typos
- Suggest corrected queries
- Make suggestions clickable for easy correction

**Common Typos**:
- Transpositions: "teh" → "the"
- Missing characters: "invocie" → "invoice"
- Extra characters: "invoicce" → "invoice"
- Wrong characters: "custmer" → "customer"

**Implementation**: Most search engines (OpenSearch, PostgreSQL with pg_trgm) support fuzzy matching out of the box. Configure appropriately for your use case.

## Show Meaningful Zero-Result States

Empty results are opportunities to help users, not dead ends.

**Essential Elements**:
- Clear message: "No results found for '[query]'"
- Query displayed (so user knows what was searched)
- Actionable suggestions

**Suggestions to Include**:
- "Did you mean...?" (if typo detected)
- "Try searching for..." (related/popular queries)
- "Check your spelling"
- "Remove filters" (if filters are active)
- Popular searches
- Browse categories/collections

**Example Zero-Result Page**:
```
No results found for "nonexistentproductxyz"

Suggestions:
• Did you mean "nonexistent product"?
• Try these popular searches:
  - Cloud backup solutions
  - Enterprise storage
  - Data protection
• Browse by category
• Remove active filters
```

**Don't**:
- Show blank page
- Generic "No results" without context
- Dead end with no next steps

## Highlight Matched Terms in Results

Users need to understand why results matched their query.

**Highlighting**:
- Bold or highlight matched terms in result titles
- Highlight matches in descriptions/snippets
- Show which fields matched (if multi-field search)

**Implementation**:
- Search engines (OpenSearch) provide highlighting out of the box
- For PostgreSQL FTS, use `ts_headline()` function
- Frontend can also highlight client-side if backend doesn't support it

**Example**:
```
**Invoice** #12345 - Customer: Acme Corp
Created: 2024-01-15 | Amount: $1,234.56
Description: Monthly **invoice** for services rendered...
```

## Remember Recent Searches

Help users quickly repeat recent searches.

**Implementation**:
- Store recent searches in localStorage (frontend) or user preferences (backend)
- Show recent searches in autocomplete dropdown
- Limit to 5-10 recent searches
- Allow clearing recent searches

**Privacy Consideration**:
- Don't store sensitive queries (SSNs, credit cards, etc.)
- Consider user privacy preferences
- Clear recent searches on logout (if stored client-side)

```typescript
// Example: Recent searches with localStorage
function useRecentSearches() {
  const getRecentSearches = (): string[] => {
    const stored = localStorage.getItem('recentSearches')
    return stored ? JSON.parse(stored) : []
  }
  
  const addRecentSearch = (query: string) => {
    const recent = getRecentSearches()
    const updated = [query, ...recent.filter(q => q !== query)].slice(0, 10)
    localStorage.setItem('recentSearches', JSON.stringify(updated))
  }
  
  return { getRecentSearches, addRecentSearch }
}
```

## Provide Clear Filter/Sort Controls

Search and filtering work together. Make the relationship clear through thoughtful UX design.

### Visual Hierarchy

**Search Box**:
- Primary element (prominent, top of page, large and obvious)
- Always visible and accessible
- Clear placeholder text ("Search products...")
- Search icon or button for clarity

**Filters**:
- Secondary element (sidebar on desktop, accordion/drawer on mobile)
- Collapsible sections for different filter categories
- Clear labels and organization
- Don't overwhelm users (show most important filters first)

**Sort Controls**:
- Tertiary element (dropdown near results, less prominent)
- Common options: Relevance, Price, Date, Name
- Clear current selection
- Mobile-friendly (touch targets, easy to tap)

### Filter Panel Design

**Layout Patterns**:

**Sidebar Pattern** (Desktop):
- Left sidebar with filters (common for e-commerce, content sites)
- Results area on right (70-80% width)
- Filters scroll independently from results
- Sticky sidebar (stays visible while scrolling results)

**Top Filters Pattern** (Mobile/Tablet):
- Horizontal filter bar above results
- Chips/badges for each filter category
- "More filters" button opens drawer/modal
- Good for limited screen space

**Accordion Pattern**:
- Collapsible sections for each filter category
- Shows counts for each category
- Saves space, good for many filters
- Users expand only relevant filters

**Filter Organization**:
- Group related filters together (Category, Price, Brand)
- Order by importance/usage (most used filters first)
- Limit visible filters (show top 5-7, "Show more" for rest)
- Use clear, user-friendly labels (not technical field names)

**Filter Display**:
- Checkboxes for multi-select (categories, tags)
- Radio buttons for single-select (sort order)
- Range sliders for numeric ranges (price, date)
- Dropdowns for many options (brands, locations)
- Clear visual distinction between filter types

### Active Filter Display

**Filter Chips/Badges**:
- Show selected filters as chips above results
- Format: "Category: Software ×" or "Price: $0-$50 ×"
- Visual styling: different color, border, or background
- Group by category or show flat list

**Removal**:
- X button on each chip (one-click removal)
- "Clear all" button to remove all filters at once
- Clicking filter again removes it (toggle behavior)
- Visual feedback on hover (highlight, show remove icon)

**Filter Counts**:
- Show result count with current filters: "68 results"
- Update dynamically as filters change
- Make count prominent (users need to know how many results)

**Example Active Filter Display**:
```
Active Filters: [Software ×] [Price: $0-$50 ×] [Status: Active ×] [Clear All]

Results (23 found)
```

**Best Practices**:
- Always show active filters (users forget what's filtered)
- Make removal obvious and easy (one click)
- Update result count immediately when filters change
- Preserve filter state in URL (shareable, bookmarkable)

### Facet Count Display

**Show Counts**:
- Display count next to each facet value: "Software (45)"
- Update counts when filters change (reflects filtered set)
- Format consistently across all facets

**Count Updates**:
- When user selects "Software" filter:
  - Software count stays visible (shows it's selected)
  - Other category counts update (reflect filtered set)
  - Example: Hardware count goes from 23 → 15 (some Hardware items don't match other filters)

**Zero Count Handling**:
- Hide facet values with 0 count (or show as disabled/grayed out)
- Don't show impossible combinations
- Example: If "Software" filter selected, don't show "Hardware (0)"

**Count Accuracy**:
- Counts must reflect current filter state (not all documents)
- Users confused if counts don't match visible results
- Test facet counts with various filter combinations

### Filter + Search Interaction

**Mental Model**:
- Clear relationship: "Search within these filters" or "Filter these search results"
- Users should understand: search AND filters work together (both apply)
- Don't make users guess how they interact

**Implementation Patterns**:

**Pattern 1: Search Then Filter** (Most Common):
- User searches → sees results
- User applies filters → results narrow down
- Search query + filters both apply
- Facet counts reflect filtered search results

**Pattern 2: Filter Then Search**:
- User applies filters → sees filtered results
- User searches → searches within filtered set
- Less common but valid for some use cases

**Clear Communication**:
- Show both search query and active filters prominently
- Example: "Results for 'backup' with filters: Software, $0-$50"
- Make it obvious what's being searched and what's filtered

**URL State Management**:
- Encode search query and filters in URL
- Example: `/search?q=backup&category=Software&price=0-50`
- Benefits: shareable URLs, bookmarkable, browser back/forward works
- Update URL when search or filters change

**Don't Confuse Users**:
- Don't mix search and filters in unclear ways
- Don't make users guess whether search includes/excludes filtered items
- Don't hide active filters (users forget what's applied)
- Don't break browser back/forward (preserve state in URL)

### Mobile Considerations

**Touch-Friendly Filters**:
- Large touch targets (minimum 44x44px)
- Adequate spacing between filter options
- Easy to tap checkboxes/radio buttons
- Swipeable filter panels

**Filter Drawer/Modal**:
- "Filters" button opens drawer/modal
- Full-screen or slide-over panel
- Easy to close (X button, swipe down, tap outside)
- Show active filters and "Apply" button

**Filter Chips**:
- Horizontal scrolling chips for active filters
- Easy to remove (tap X or swipe away)
- Don't overwhelm small screens (limit visible chips)

**Result Count**:
- Prominent result count (users need to know how many results)
- Update immediately when filters change
- Show loading state during filter updates

### Accessibility

**Keyboard Navigation**:
- Tab through filters (logical order)
- Space/Enter to toggle checkboxes
- Arrow keys for radio buttons
- Escape to close filter panel

**Screen Reader Support**:
- Label all filter controls
- Announce filter state changes ("Software filter selected, 45 results")
- Announce result count updates
- Clear filter removal ("Software filter removed")

**Focus Management**:
- Focus moves logically through filters
- Focus returns to results after applying filters
- Don't trap focus in filter panel

**Example Accessible Filter**:
```html
<fieldset>
  <legend>Category</legend>
  <label>
    <input type="checkbox" name="category" value="Software" />
    Software <span aria-label="45 results">(45)</span>
  </label>
  <label>
    <input type="checkbox" name="category" value="Hardware" />
    Hardware <span aria-label="23 results">(23)</span>
  </label>
</fieldset>
```

## Distinguish Filtering from Searching

Users understand the difference between filtering (narrowing a known set) and searching (finding across all content). Make this distinction clear.

**Filtering**:
- Applied to a known set (e.g., "Products in Electronics category")
- Uses structured data (categories, price ranges, dates)
- Typically exact matches or ranges
- UI: checkboxes, dropdowns, sliders

**Searching**:
- Finds across all content
- Uses free-form text
- Handles typos, synonyms, relevance
- UI: text input

**When to Use Each**:
- **Filtering**: User browsing a category, wants to narrow by attributes
- **Searching**: User looking for specific item or exploring with keywords
- **Both**: User searches, then filters results (common pattern)

**UI Patterns**:
- Separate "Search" and "Filter" sections (clear distinction)
- Or unified interface where search is primary, filters narrow results (make relationship explicit)

## Performance Best Practices

**Debounce Search Input**:
- 200-300ms delay for autocomplete
- Prevents excessive API calls
- Improves perceived performance

**Cache Frequent Queries**:
- Cache autocomplete suggestions (short TTL, e.g., 5 minutes)
- Cache popular search results (longer TTL, e.g., 1 hour)
- Invalidate cache on data updates

**Limit Result Sets**:
- Default to reasonable page size (10-50 results)
- Use pagination or "Load more"
- Don't return thousands of results at once

**Optimize Backend**:
- Use appropriate indexes (database or search engine)
- Monitor query performance
- Scale search infrastructure as needed

## Accessibility

**Keyboard Navigation**:
- Tab to search input
- Arrow keys navigate autocomplete
- Enter selects/submits
- Escape closes autocomplete

**Screen Reader Support**:
- Label search input: `<label for="search">Search</label>` or `aria-label`
- Announce autocomplete: `aria-autocomplete="list"`, `aria-expanded`
- Announce result count: "Found 25 results"
- Announce zero results: "No results found. Suggestions available."

**Focus Management**:
- Clear focus indicator on search input
- Focus management when autocomplete opens/closes
- Don't trap focus in autocomplete (allow Tab to continue)

**Example Accessible Search**:
```html
<label for="search-input">Search products</label>
<input
  id="search-input"
  type="search"
  aria-autocomplete="list"
  aria-expanded="false"
  aria-controls="suggestions"
  aria-activedescendant="suggestion-0"
/>
<ul id="suggestions" role="listbox">
  <li id="suggestion-0" role="option">Backup solutions</li>
  <li id="suggestion-1" role="option">Storage devices</li>
</ul>
```

## Mobile Considerations

**Touch-Friendly**:
- Large enough search input (minimum 44x44px touch target)
- Easy to clear search (clear button, not just backspace)
- Autocomplete suggestions easy to tap

**Keyboard**:
- Show appropriate keyboard type (`type="search"` triggers search keyboard on mobile)
- "Search" button on keyboard submits (not "Go" or "Return")

**Performance**:
- Consider reducing autocomplete delay on mobile (faster feedback)
- Limit number of suggestions (smaller screen)
- Consider infinite scroll instead of pagination for results

## Search Analytics and Tracking

Understanding how users search is critical for improving search quality. Track key metrics to identify problems and opportunities.

### Essential Metrics to Track

**Zero-Result Rate**:
- Percentage of searches returning no results
- Target: <10%
- High rate indicates: missing content, poor typo handling, unclear search scope
- Track by query pattern, user segment, time period

**Search-to-Click Rate**:
- Percentage of searches resulting in at least one result click
- Target: >60% for finding tasks, >40% for discovery tasks
- Low rate indicates: poor relevance, confusing results, wrong content
- Segment by query type, user role, search context

**Time-to-First-Click**:
- Average time from search initiation to first result click
- Target: <10 seconds for finding, <30 seconds for discovery
- Measures search efficiency
- Track distribution (p50, p95, p99)

**Query Refinement Rate**:
- Percentage of searches followed by modified queries
- Healthy: 20-40% (users exploring)
- Very high (>60%): initial results are poor, relevance issues
- Very low (<10%): users finding results immediately (good) or giving up (bad)

**Search Abandonment Rate**:
- Percentage of searches with no result clicks
- Target: <20%
- Indicates frustration or poor relevance
- Track by query length, result count, user segment

**Top Zero-Result Queries**:
- Most common queries that return no results
- Actionable: add content, improve synonyms, fix typos
- Review weekly/monthly to identify content gaps

**Query Patterns**:
- Most common queries (identify popular content needs)
- Query length distribution (single word vs. phrases)
- Query refinement patterns (how users modify queries)
- Seasonal/trending queries

### Implementation

**Backend Tracking**:
```kotlin
// Track search query
data class SearchEvent(
    val query: String,
    val userId: String?,
    val resultCount: Int,
    val timestamp: Instant,
    val filters: Map<String, Any>?,
    val resultIds: List<String>?  // Track which results shown
)

// Track result clicks
data class SearchClickEvent(
    val query: String,
    val resultId: String,
    val position: Int,  // Position in results (1-based)
    val timestamp: Instant,
    val timeToClick: Duration  // Time from search to click
)

// Emit events
fun search(query: String, filters: Map<String, Any>?): SearchResults {
    val results = searchService.search(query, filters)
    
    // Emit search event
    eventPublisher.publish(SearchEvent(
        query = query,
        userId = currentUser?.id,
        resultCount = results.size,
        timestamp = Instant.now(),
        filters = filters,
        resultIds = results.map { it.id }
    ))
    
    return results
}
```

**Frontend Tracking**:
```typescript
// Track search and clicks
function trackSearch(query: string, resultCount: number) {
  analytics.track('search_performed', {
    query,
    result_count: resultCount,
    timestamp: Date.now()
  })
}

function trackResultClick(query: string, resultId: string, position: number, timeToClick: number) {
  analytics.track('search_result_clicked', {
    query,
    result_id: resultId,
    position,
    time_to_click: timeToClick
  })
}

// Track zero results
function trackZeroResults(query: string) {
  analytics.track('search_zero_results', {
    query,
    timestamp: Date.now()
  })
}
```

### Analytics Dashboards

**Key Dashboards to Build**:

**1. Search Health Dashboard**:
- Zero-result rate (trend over time)
- Search-to-click rate (trend)
- Average time-to-first-click
- Search volume (queries per day)
- Alerts for metric degradation

**2. Zero-Result Analysis**:
- Top zero-result queries (table)
- Zero-result rate by query length
- Zero-result rate by user segment
- Trends over time
- Action items (queries to address)

**3. Query Analysis**:
- Most popular queries
- Query length distribution
- Query refinement patterns
- Seasonal trends
- User segment differences

**4. Relevance Analysis**:
- Click-through rate by result position
- Queries with low click-through (relevance issues)
- Time-to-click by query type
- User satisfaction scores (if collected)

### Acting on Analytics

**Content Gaps**:
- High zero-result queries → prioritize adding content
- Popular queries with no results → content gap, high priority

**Relevance Issues**:
- Low click-through rate → tune relevance algorithm
- High refinement rate → initial results poor, improve ranking
- Long time-to-click → results not relevant, users scanning many results

**Typo Handling**:
- Common typos in zero-result queries → improve fuzzy matching
- "Did you mean?" suggestions → track if users click suggestions

**UX Improvements**:
- High abandonment rate → improve zero-result pages, add suggestions
- Query patterns → optimize autocomplete suggestions
- Filter usage → improve faceted search if underused

**Privacy Considerations**:
- Don't log sensitive queries (SSNs, credit cards, personal identifiers)
- Anonymize user data in analytics
- Allow users to opt out
- Comply with data protection regulations (GDPR, CCPA)
- Consider query sanitization (remove PII before logging)

## Stack-Specific Guidance

### Vue 3

**Composables for Search State**:
```typescript
// useSearch.ts
import { ref, watchEffect, computed } from 'vue'
import { useDebounceFn } from '@vueuse/core'

export function useSearch() {
  const query = ref('')
  const results = ref([])
  const suggestions = ref([])
  const loading = ref(false)
  const error = ref(null)
  const selectedIndex = ref(-1)  // For keyboard navigation
  
  const debouncedQuery = useDebounceFn((q: string) => {
    if (q.length >= 2) {
      performSearch(q)
    } else {
      results.value = []
    }
  }, 250)
  
  watchEffect(() => {
    debouncedQuery(query.value)
  })
  
  async function performSearch(q: string) {
    loading.value = true
    error.value = null
    try {
      results.value = await searchService.search(q)
      trackSearch(q, results.value.length)
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }
  
  async function fetchSuggestions(q: string) {
    if (q.length >= 2) {
      suggestions.value = await searchService.autocomplete(q)
    } else {
      suggestions.value = []
    }
  }
  
  const debouncedSuggestions = useDebounceFn(fetchSuggestions, 200)
  
  watchEffect(() => {
    debouncedSuggestions(query.value)
  })
  
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, suggestions.value.length - 1)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
    } else if (event.key === 'Enter' && selectedIndex.value >= 0) {
      event.preventDefault()
      selectSuggestion(suggestions.value[selectedIndex.value])
    } else if (event.key === 'Escape') {
      suggestions.value = []
      selectedIndex.value = -1
    }
  }
  
  function selectSuggestion(suggestion: string) {
    query.value = suggestion
    suggestions.value = []
    selectedIndex.value = -1
    performSearch(suggestion)
  }
  
  return { 
    query, 
    results, 
    suggestions,
    loading, 
    error,
    selectedIndex,
    handleKeyDown,
    selectSuggestion
  }
}
```

**Component with Highlighting and Keyboard Navigation**:
```vue
<template>
  <div class="search-container">
    <label for="search-input">Search products</label>
    <input
      id="search-input"
      v-model="query"
      type="search"
      aria-autocomplete="list"
      :aria-expanded="suggestions.length > 0"
      aria-controls="suggestions"
      :aria-activedescendant="selectedIndex >= 0 ? `suggestion-${selectedIndex}` : undefined"
      @keydown="handleKeyDown"
      @focus="showSuggestions = true"
      @blur="handleBlur"
    />
    
    <!-- Autocomplete Suggestions -->
    <ul
      v-if="showSuggestions && suggestions.length > 0"
      id="suggestions"
      role="listbox"
      class="suggestions"
    >
      <li
        v-for="(suggestion, index) in suggestions"
        :id="`suggestion-${index}`"
        :key="index"
        role="option"
        :class="{ highlighted: index === selectedIndex }"
        @click="selectSuggestion(suggestion)"
        @mouseenter="selectedIndex = index"
        v-html="highlightMatch(suggestion, query)"
      />
    </ul>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading">Searching...</div>
    
    <!-- Error State -->
    <div v-if="error" class="error">Error: {{ error.message }}</div>
    
    <!-- Results -->
    <ul v-if="results.length > 0" class="results">
      <li v-for="result in results" :key="result.id" class="result-item">
        <h3 v-html="highlightMatch(result.title, query)" />
        <p v-html="highlightMatch(result.description, query)" />
        <button @click="trackClick(result)">View Details</button>
      </li>
    </ul>
    
    <!-- Zero Results -->
    <div v-if="!loading && query && results.length === 0" class="zero-results">
      <p>No results found for "{{ query }}"</p>
      <ul class="suggestions">
        <li v-for="suggestion in zeroResultSuggestions" :key="suggestion">
          <a @click="query = suggestion; performSearch(suggestion)">{{ suggestion }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSearch } from './useSearch'

const { query, results, suggestions, loading, error, selectedIndex, handleKeyDown, selectSuggestion } = useSearch()
const showSuggestions = ref(true)

function highlightMatch(text: string, query: string): string {
  if (!query) return text
  const regex = new RegExp(`(${escapeRegex(query)})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function handleBlur() {
  // Delay hiding suggestions to allow clicks
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

function trackClick(result: any) {
  trackResultClick(query.value, result.id, results.value.indexOf(result) + 1)
}

const zeroResultSuggestions = computed(() => {
  // Generate suggestions based on query
  // This would come from backend or local logic
  return ['Try different keywords', 'Check spelling', 'Browse categories']
})
</script>

<style scoped>
.suggestions {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions li {
  padding: 8px 12px;
  cursor: pointer;
}

.suggestions li.highlighted {
  background-color: #f0f0f0;
}

mark {
  background-color: yellow;
  font-weight: bold;
}

.result-item {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
}
</style>
```

### React

**Custom Hook for Search with Advanced Features**:
```typescript
// useSearch.ts
import { useState, useEffect, useCallback, useRef } from 'react'

export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const abortControllerRef = useRef<AbortController | null>(null)
  
  const debouncedQuery = useDebounce(query, 250)
  const debouncedSuggestions = useDebounce(query, 200)
  
  // Cancel previous request when query changes
  useEffect(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }, [query])
  
  // Perform search
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      performSearch(debouncedQuery)
    } else {
      setResults([])
    }
  }, [debouncedQuery])
  
  // Fetch suggestions
  useEffect(() => {
    if (debouncedSuggestions.length >= 2) {
      fetchSuggestions(debouncedSuggestions)
    } else {
      setSuggestions([])
    }
  }, [debouncedSuggestions])
  
  async function performSearch(q: string) {
    setLoading(true)
    setError(null)
    
    abortControllerRef.current = new AbortController()
    
    try {
      const searchResults = await searchService.search(q, {
        signal: abortControllerRef.current.signal
      })
      setResults(searchResults)
      trackSearch(q, searchResults.length)
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        setError(e)
      }
    } finally {
      setLoading(false)
    }
  }
  
  async function fetchSuggestions(q: string) {
    try {
      const suggs = await searchService.autocomplete(q)
      setSuggestions(suggs)
    } catch (e) {
      // Silently fail for suggestions
    }
  }
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setSelectedIndex(prev => Math.max(prev - 1, -1))
    } else if (event.key === 'Enter' && selectedIndex >= 0) {
      event.preventDefault()
      selectSuggestion(suggestions[selectedIndex])
    } else if (event.key === 'Escape') {
      setSuggestions([])
      setSelectedIndex(-1)
    }
  }, [suggestions, selectedIndex])
  
  function selectSuggestion(suggestion: string) {
    setQuery(suggestion)
    setSuggestions([])
    setSelectedIndex(-1)
    performSearch(suggestion)
  }
  
  return {
    query,
    setQuery,
    results,
    suggestions,
    loading,
    error,
    selectedIndex,
    handleKeyDown,
    selectSuggestion
  }
}

// Debounce hook
function useDebounce(value: string, delay: number): string {
  const [debouncedValue, setDebouncedValue] = useState(value)
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)
    
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])
  
  return debouncedValue
}
```

**Component with Highlighting and Keyboard Navigation**:
```tsx
import React, { useState, useEffect } from 'react'
import { useSearch } from './useSearch'

function SearchComponent() {
  const {
    query,
    setQuery,
    results,
    suggestions,
    loading,
    error,
    selectedIndex,
    handleKeyDown,
    selectSuggestion
  } = useSearch()
  
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)
  
  useEffect(() => {
    const input = inputRef.current
    if (input) {
      input.addEventListener('keydown', handleKeyDown as any)
      return () => {
        input.removeEventListener('keydown', handleKeyDown as any)
      }
    }
  }, [handleKeyDown])
  
  function highlightMatch(text: string, query: string): string {
    if (!query) return text
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi')
    return text.replace(regex, '<mark>$1</mark>')
  }
  
  function escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }
  
  function handleBlur() {
    setTimeout(() => setShowSuggestions(false), 200)
  }
  
  function trackClick(result: any, position: number) {
    trackResultClick(query, result.id, position)
  }
  
  return (
    <div className="search-container">
      <label htmlFor="search-input">Search products</label>
      <input
        ref={inputRef}
        id="search-input"
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setShowSuggestions(true)}
        onBlur={handleBlur}
        aria-autocomplete="list"
        aria-expanded={suggestions.length > 0}
        aria-controls="suggestions"
        aria-activedescendant={selectedIndex >= 0 ? `suggestion-${selectedIndex}` : undefined}
      />
      
      {/* Autocomplete Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <ul
          id="suggestions"
          role="listbox"
          className="suggestions"
        >
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              id={`suggestion-${index}`}
              role="option"
              className={index === selectedIndex ? 'highlighted' : ''}
              onClick={() => selectSuggestion(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
              dangerouslySetInnerHTML={{ __html: highlightMatch(suggestion, query) }}
            />
          ))}
        </ul>
      )}
      
      {/* Loading State */}
      {loading && <div className="loading">Searching...</div>}
      
      {/* Error State */}
      {error && <div className="error">Error: {error.message}</div>}
      
      {/* Results */}
      {results.length > 0 && (
        <ul className="results">
          {results.map((result, index) => (
            <li key={result.id} className="result-item">
              <h3 dangerouslySetInnerHTML={{ __html: highlightMatch(result.title, query) }} />
              <p dangerouslySetInnerHTML={{ __html: highlightMatch(result.description, query) }} />
              <button onClick={() => trackClick(result, index + 1)}>View Details</button>
            </li>
          ))}
        </ul>
      )}
      
      {/* Zero Results */}
      {!loading && query && results.length === 0 && (
        <div className="zero-results">
          <p>No results found for "{query}"</p>
          <ul className="suggestions">
            <li><a onClick={() => setQuery('Try different keywords')}>Try different keywords</a></li>
            <li><a onClick={() => setQuery('Check spelling')}>Check spelling</a></li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default SearchComponent
```

**Styling** (CSS):
```css
.suggestions {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions li {
  padding: 8px 12px;
  cursor: pointer;
}

.suggestions li.highlighted {
  background-color: #f0f0f0;
}

mark {
  background-color: yellow;
  font-weight: bold;
}

.result-item {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
}
```

## Common Anti-Patterns to Avoid

**Search as Filter**:
- Don't use search input for exact filtering (use dropdowns/checkboxes instead)
- Example: Don't make users type "Status: Active" when a status filter exists

**Hidden Search**:
- Don't hide search behind menus or require multiple clicks
- Make search prominent and always accessible

**No Feedback**:
- Don't leave users wondering if search is working
- Show loading state, result count, or "no results" message

**Broken Autocomplete**:
- Don't show autocomplete that doesn't work (broken keyboard navigation, doesn't submit)
- If autocomplete is broken, disable it rather than frustrate users

**Ignoring Zero Results**:
- Don't show blank page for zero results
- Always provide helpful next steps

**Over-Complicated Advanced Search**:
- Don't require advanced search for basic use cases
- Keep default simple, advanced optional
