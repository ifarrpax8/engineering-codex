# Search & Discovery -- Best Practices

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

Search and filtering work together. Make the relationship clear.

**Visual Hierarchy**:
- Search box is primary (prominent, top of page)
- Filters are secondary (sidebar or below search)
- Sort is tertiary (dropdown near results)

**Filter State Visibility**:
- Show active filters clearly (chips, badges, or list)
- Make filters easy to remove (X button, "Clear all")
- Indicate result count with current filters

**Filter + Search Interaction**:
- Filters apply to search results (narrow down)
- Search applies to filtered set (search within filters)
- Make this relationship clear in UI

**Don't Confuse Users**:
- Don't mix search and filters in unclear ways
- Don't make users guess whether search includes/excludes filtered items
- Provide clear mental model: "Search within these filters" or "Filter these search results"

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

## Stack-Specific Guidance

### Vue 3

**Composables for Search State**:
```typescript
// useSearch.ts
export function useSearch() {
  const query = ref('')
  const results = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const debouncedQuery = useDebounceFn(query, 250)
  
  watchEffect(async () => {
    if (debouncedQuery.value.length >= 2) {
      loading.value = true
      try {
        results.value = await searchService.search(debouncedQuery.value)
      } catch (e) {
        error.value = e
      } finally {
        loading.value = false
      }
    }
  })
  
  return { query, results, loading, error }
}
```

**Component Usage**:
```vue
<template>
  <input v-model="query" />
  <div v-if="loading">Searching...</div>
  <div v-if="error">Error: {{ error }}</div>
  <ul v-if="results.length">
    <li v-for="result in results" :key="result.id">
      {{ result.name }}
    </li>
  </ul>
</template>

<script setup>
import { useSearch } from './useSearch'
const { query, results, loading, error } = useSearch()
</script>
```

### React

**Custom Hook for Search**:
```typescript
// useSearch.ts
export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const debouncedQuery = useDebounce(query, 250)
  
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      setLoading(true)
      searchService.search(debouncedQuery)
        .then(setResults)
        .catch(setError)
        .finally(() => setLoading(false))
    }
  }, [debouncedQuery])
  
  return { query, setQuery, results, loading, error }
}
```

**Component Usage**:
```tsx
function SearchComponent() {
  const { query, setQuery, results, loading, error } = useSearch()
  
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      {loading && <div>Searching...</div>}
      {error && <div>Error: {error.message}</div>}
      {results.length > 0 && (
        <ul>
          {results.map(result => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
    </>
  )
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
