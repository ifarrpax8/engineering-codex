# Search & Discovery -- Testing

## Testing Search Relevance

Search relevance—ensuring the right results appear at the top—is critical but difficult to test automatically. Use a combination of manual testing, data-driven tests, and user feedback.

### Relevance Test Cases

**Exact Match Priority**:
- Exact matches should rank higher than partial matches
- Test: Search "Invoice 12345" → exact match should be first result
- Test: Search "John Smith" → user named "John Smith" ranks above "John Smithson"

**Field Weighting**:
- Important fields (title, name) should weight more than secondary fields (description, tags)
- Test: Search "backup" → products with "backup" in title rank above those with "backup" only in description

**Recency/Popularity**:
- Recent or popular items may rank higher (depending on business rules)
- Test: Search "cloud storage" → recently updated products appear before outdated ones
- Test: Popular products rank above obscure ones (if popularity is a ranking factor)

**Multi-Field Matching**:
- Documents matching multiple fields should rank higher
- Test: Search "enterprise backup" → products matching both "enterprise" and "backup" rank above single-field matches

### Relevance Testing Strategy

**Manual Test Suite**:
- Maintain a spreadsheet of known-good queries with expected top results
- Run manually during releases or as part of QA process
- Include edge cases: special characters, numbers, long queries, short queries

**Automated Relevance Tests**:
- Create test data with known relationships
- Assert expected ordering for specific queries
- Use test-specific search indexes to avoid polluting production data

```kotlin
// Example: Automated relevance test
@Test
fun `exact match ranks higher than partial match`() {
    val exactMatch = Product(name = "Enterprise Backup Solution", description = "Backup")
    val partialMatch = Product(name = "Backup Tool", description = "Enterprise")
    productRepository.saveAll(listOf(exactMatch, partialMatch))
    searchService.reindex()
    
    val results = searchService.search("Enterprise Backup Solution")
    
    assertThat(results.first().id).isEqualTo(exactMatch.id)
}
```

**User Feedback Loop**:
- Track "result clicked" events to measure relevance
- A/B test ranking algorithm changes
- Monitor search-to-click rate and time-to-first-click metrics

## Testing Autocomplete Behavior

Autocomplete must be fast, accurate, and keyboard-accessible.

### Functional Tests

**Suggestion Appearance**:
- Suggestions appear after user types N characters (typically 2-3)
- Suggestions update as user continues typing
- Suggestions disappear when search box loses focus (or user selects one)

**Suggestion Relevance**:
- Most relevant suggestions appear first
- Suggestions match user input (prefix match or fuzzy match)
- Limit number of suggestions (typically 5-10)

**Keyboard Navigation**:
- Arrow keys navigate through suggestions
- Enter selects highlighted suggestion
- Escape closes suggestions
- Tab moves focus away (closes suggestions)

**Mouse Interaction**:
- Clicking suggestion selects it and triggers search
- Hover highlights suggestion
- Clicking outside closes suggestions

### E2E Testing with Playwright

```typescript
// Example: Playwright autocomplete test
test('autocomplete shows suggestions and allows selection', async ({ page }) => {
  await page.goto('/products');
  
  const searchInput = page.getByTestId('search-input');
  await searchInput.fill('inv');
  
  // Wait for suggestions to appear
  const suggestions = page.getByTestId('autocomplete-suggestions');
  await expect(suggestions).toBeVisible();
  
  // Verify suggestions contain input
  const firstSuggestion = page.getByTestId('suggestion-0');
  await expect(firstSuggestion).toContainText('inv');
  
  // Test keyboard navigation
  await searchInput.press('ArrowDown');
  await expect(firstSuggestion).toHaveClass(/highlighted/);
  
  // Test selection
  await searchInput.press('Enter');
  await expect(page).toHaveURL(/search/);
});
```

**Performance Testing**:
- Measure autocomplete response time (target: <200ms)
- Test with slow network (throttle to 3G)
- Verify debouncing works (rapid typing doesn't trigger excessive requests)

## Testing Zero-Result States

Zero-result pages are opportunities to help users, not dead ends.

### Test Cases

**Helpful Messaging**:
- Clear message: "No results found for '[query]'"
- Suggestions: "Did you mean...?", "Try searching for...", "Check your spelling"
- Related content: "Popular searches", "Browse categories"

**Query Suggestions**:
- If typo detected, suggest corrected query
- Suggest related or popular queries
- Suggest removing filters if filters are active

**Spell Checking**:
- Common typos trigger "Did you mean?" suggestions
- Test: "invocie" → suggests "invoice"
- Test: "custmer" → suggests "customer"

**Filter Awareness**:
- If filters are active, suggest removing filters
- Show message: "No results with current filters. Try removing some filters."

### E2E Testing

```typescript
test('zero results shows helpful suggestions', async ({ page }) => {
  await page.goto('/products');
  await page.getByTestId('search-input').fill('nonexistentproductxyz');
  await page.getByTestId('search-button').click();
  
  // Verify zero-result message
  await expect(page.getByTestId('zero-results-message')).toBeVisible();
  await expect(page.getByTestId('zero-results-message')).toContainText('No results');
  
  // Verify suggestions appear
  await expect(page.getByTestId('search-suggestions')).toBeVisible();
  
  // Verify related content
  await expect(page.getByTestId('popular-searches')).toBeVisible();
});
```

## Testing Filter Combinations

Filters must work correctly individually and in combination.

### Test Cases

**Individual Filters**:
- Each filter works independently
- Filter state persists during search
- Filter can be cleared

**Filter Combinations**:
- Multiple filters combine with AND logic (typically)
- Filters from different categories work together
- Result counts update correctly with multiple filters

**Filter + Search**:
- Search and filters work together
- Filters apply to search results
- Clearing search doesn't clear filters (or vice versa, depending on UX)

**Filter State Management**:
- URL reflects active filters (for shareability)
- Browser back/forward works with filters
- Filters persist across page navigation (if intended)

### Test Implementation

```kotlin
@Test
fun `multiple filters combine correctly`() {
    val software = Category("Software")
    val hardware = Category("Hardware")
    val product1 = Product(name = "Backup Tool", category = software, price = BigDecimal("50"))
    val product2 = Product(name = "Backup Drive", category = hardware, price = BigDecimal("50"))
    val product3 = Product(name = "Storage Tool", category = software, price = BigDecimal("100"))
    // ... save products
    
    val results = productService.search(
        query = "backup",
        filters = mapOf(
            "category" to "Software",
            "maxPrice" to "75"
        )
    )
    
    // Should return product1 only (matches search + both filters)
    assertThat(results).hasSize(1)
    assertThat(results.first().id).isEqualTo(product1.id)
}
```

## Performance Testing Search

Search must remain fast under load and as data grows.

### Response Time Testing

**Target Latencies**:
- Autocomplete: <200ms (p95)
- Full search: <500ms (p95)
- Faceted search: <800ms (p95)

**Load Testing**:
- Simulate concurrent search queries
- Measure response times under load
- Identify bottlenecks (database, search engine, network)

**Volume Testing**:
- Test search performance with large datasets (1M+, 10M+ records)
- Measure index size and query performance
- Verify performance doesn't degrade linearly with data size

### Tools

- **k6** or **Gatling** for load testing search endpoints
- **Apache JMeter** for complex search scenarios
- Monitor search engine metrics (OpenSearch cluster health, query latency)

```kotlin
// Example: Performance test
@Test
fun `search responds within SLA under load`() {
    val queries = listOf("backup", "storage", "cloud", "enterprise")
    
    val results = runBlocking {
        (1..100).map { 
            async {
                val query = queries.random()
                measureTimeMillis {
                    searchService.search(query)
                }
            }
        }.awaitAll()
    }
    
    val p95 = results.sorted()[95]
    assertThat(p95).isLessThan(500) // 500ms p95 target
}
```

## E2E Testing Search Flows

End-to-end tests verify the complete search user journey.

### Critical User Flows

**Basic Search Flow**:
1. User navigates to search page
2. User types query
3. Autocomplete appears
4. User selects suggestion or submits query
5. Results appear with correct count
6. User clicks result
7. User navigates to detail page

**Filtered Search Flow**:
1. User performs search
2. User applies filter
3. Results update, count changes
4. User applies additional filter
5. Results update again
6. User clears filter
7. Results update, previous filter still active

**Zero-Result Recovery Flow**:
1. User searches for non-existent item
2. Zero-result page appears
3. User clicks suggested query
4. Results appear for suggested query

### Playwright Test Examples

```typescript
test('complete search flow', async ({ page }) => {
  // Navigate and search
  await page.goto('/products');
  await page.getByTestId('search-input').fill('backup');
  
  // Verify autocomplete
  await expect(page.getByTestId('autocomplete-suggestions')).toBeVisible();
  await page.getByTestId('suggestion-0').click();
  
  // Verify results
  await expect(page.getByTestId('search-results')).toBeVisible();
  const resultCount = await page.getByTestId('result-count').textContent();
  expect(parseInt(resultCount!)).toBeGreaterThan(0);
  
  // Click result
  await page.getByTestId('result-0').click();
  await expect(page).toHaveURL(/\/products\/\d+/);
});

test('filtered search flow', async ({ page }) => {
  await page.goto('/products');
  await page.getByTestId('search-input').fill('storage');
  await page.getByTestId('search-button').click();
  
  // Apply filter
  await page.getByTestId('filter-category-Software').click();
  await expect(page.getByTestId('search-results')).toBeVisible();
  
  // Verify filter is active
  await expect(page.getByTestId('active-filter-category-Software')).toBeVisible();
  
  // Apply second filter
  await page.getByTestId('filter-price-0-50').click();
  
  // Verify both filters active
  await expect(page.getByTestId('active-filter-category-Software')).toBeVisible();
  await expect(page.getByTestId('active-filter-price-0-50')).toBeVisible();
});
```

## Testing Search Index Synchronization

Verify that data changes are reflected in search results within acceptable timeframes.

### Test Cases

**Create Synchronization**:
- Create new record
- Verify it appears in search within expected time (immediate for event-driven, seconds for CDC, minutes for scheduled)

**Update Synchronization**:
- Update record (change searchable fields)
- Verify search results reflect changes
- Verify old values no longer match

**Delete Synchronization**:
- Delete (or soft-delete) record
- Verify it no longer appears in search results

**Bulk Operations**:
- Bulk create/update/delete
- Verify all changes reflected in search
- Measure synchronization time for bulk operations

### Test Implementation

```kotlin
@Test
fun `new product appears in search index within SLA`() {
    val product = Product(name = "New Product", description = "Searchable text")
    productRepository.save(product)
    
    // Trigger indexing (event-driven or manual)
    eventPublisher.publish(ProductCreatedEvent(product))
    
    // Wait for synchronization (with timeout)
    await().atMost(5, SECONDS).until {
        val results = searchService.search("New Product")
        results.any { it.id == product.id }
    }
    
    val results = searchService.search("New Product")
    assertThat(results).anyMatch { it.id == product.id }
}

@Test
fun `updated product reflects changes in search`() {
    val product = productRepository.save(Product(name = "Old Name"))
    searchService.reindex() // Ensure indexed
    
    product.name = "New Name"
    productRepository.save(product)
    eventPublisher.publish(ProductUpdatedEvent(product))
    
    await().atMost(5, SECONDS).until {
        val oldResults = searchService.search("Old Name")
        val newResults = searchService.search("New Name")
        oldResults.none { it.id == product.id } && 
        newResults.any { it.id == product.id }
    }
}
```

## Accessibility Testing

Search must be accessible to all users.

### Keyboard Navigation
- Tab navigates to search input
- Search input receives focus indicator
- Autocomplete navigable with arrow keys
- Enter submits search or selects suggestion
- Escape closes autocomplete

### Screen Reader Support
- Search input has accessible label
- Autocomplete suggestions announced
- Result count announced
- Zero-result message announced
- Filter state announced

### Test with Screen Readers
- Test with NVDA (Windows) or VoiceOver (macOS)
- Verify all interactive elements are announced
- Verify search state changes are communicated

## Test Data Management

**Test-Specific Search Indexes**:
- Use separate search index for tests (e.g., `products_test`)
- Avoid polluting production search data
- Faster test execution (smaller index)

**Test Data Fixtures**:
- Create known test data for relevance tests
- Use factories/builders for test data generation
- Clean up test data after tests

**Isolation**:
- Each test should be independent
- Don't rely on test execution order
- Reset search index between test classes if needed

## Continuous Testing

**CI/CD Integration**:
- Run search tests in CI pipeline
- Fail build if search functionality broken
- Performance tests can run less frequently (nightly)

**Monitoring in Production**:
- Track search error rates
- Monitor search latency (p95, p99)
- Alert on degradation
- Track zero-result rate trends

**Regression Testing**:
- Maintain test suite of known-good search queries
- Run after search algorithm changes
- Catch relevance regressions early
