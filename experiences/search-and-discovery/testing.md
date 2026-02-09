# Search & Discovery -- Testing

## Contents

- [Testing Search Relevance](#testing-search-relevance)
- [Testing Autocomplete Behavior](#testing-autocomplete-behavior)
- [Testing Zero-Result States](#testing-zero-result-states)
- [Testing Filter Combinations](#testing-filter-combinations)
- [Performance Testing Search](#performance-testing-search)
- [E2E Testing Search Flows](#e2e-testing-search-flows)
- [Testing Search Index Synchronization](#testing-search-index-synchronization)
- [Accessibility Testing](#accessibility-testing)
- [Test Data Management](#test-data-management)
- [Continuous Testing](#continuous-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

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

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

**High-Risk Areas** (Test First, Test Thoroughly):
- **Index Synchronization**: Data changes not appearing in search is a critical user-facing bug. Test create/update/delete synchronization with realistic SLAs (event-driven: <5 seconds, scheduled: <1 hour).
- **Zero-Result Handling**: Poor zero-result pages frustrate users and indicate content gaps. Test typo detection, query suggestions, and helpful messaging.
- **Relevance Ranking**: Wrong results appearing first breaks user trust. Test exact matches, field weighting, and multi-field matching with real user query patterns.
- **Autocomplete Performance**: Slow or broken autocomplete degrades perceived performance. Test debouncing, request cancellation, and response times under load.
- **Filter Combinations**: Filters breaking or producing incorrect results when combined is a common regression. Test all filter combinations, especially high-cardinality facets.

**Medium-Risk Areas**:
- **Cross-Browser Compatibility**: Search UI and autocomplete behavior varies across browsers. Test keyboard navigation, autocomplete interactions, and result rendering.
- **Mobile Search Experience**: Touch interactions, keyboard types, and screen sizes affect search usability. Test on real devices, not just emulators.
- **Accessibility**: Screen reader support and keyboard navigation are required for compliance. Test with NVDA/VoiceOver and verify ARIA attributes.

**Lower-Risk Areas** (Still Important):
- **Edge Cases**: Very long queries, special characters, empty queries, Unicode handling.
- **Performance Under Load**: Search endpoint handling concurrent requests, autocomplete rate limiting.
- **Error Handling**: Network failures, search engine outages, malformed queries.

**Risk Assessment Framework**:
- **Impact**: How many users affected? How critical is search to user workflow?
- **Likelihood**: How often does this scenario occur? How complex is the code path?
- **Detectability**: Will users notice? Will it be caught in production monitoring?

### Exploratory Testing Guidance

**Search Query Exploration**:
- **Natural Language Queries**: Test how users actually search, not how developers think they search. Try "unpaid invoices", "things I worked on last week", "that backup product".
- **Typo Patterns**: Systematically test common typos: transpositions ("teh" → "the"), missing characters ("invocie" → "invoice"), extra characters ("invoicce" → "invoice").
- **Vague Queries**: Test ambiguous searches like "backup", "recent", "my stuff" to see how the system handles intent.
- **Multi-Language**: If content spans languages, test queries in each language, test accent handling (café, résumé), test mixed-language queries.

**User Journey Exploration**:
- **Finding Flow**: User knows what they want (exact identifier). Test: Can they find it quickly? Does autocomplete help? Are results accurate?
- **Discovery Flow**: User exploring content. Test: Are results relevant? Do filters help narrow down? Can they discover unexpected but useful content?
- **Recovery Flow**: User gets zero results. Test: Are suggestions helpful? Can they refine query easily? Do they understand why no results?

**Edge Case Exploration**:
- **Empty States**: No content indexed yet, empty search query, all filters applied resulting in zero results.
- **Boundary Conditions**: Single character queries, very long queries (100+ characters), queries with only special characters.
- **Timing Issues**: Search immediately after creating content (index sync lag), rapid query refinement, autocomplete while typing quickly.
- **Concurrent Operations**: Search while content is being updated, multiple users searching simultaneously, bulk data imports affecting search.

**Exploratory Test Charter Template**:
```
Charter: Explore [search scenario] to discover [potential issues]
Time: [X minutes]
Focus Areas:
- [Specific aspect to explore]
- [User behavior to simulate]
- [Edge cases to investigate]

Notes: [Document findings, bugs, usability issues]
```

### Test Data Management

**Search-Specific Test Data Requirements**:
- **Relevance Test Data**: Create products/documents with known relationships for relevance testing. Example: Product A has "backup" in title, Product B has "backup" only in description → Product A should rank higher.
- **Typo Test Data**: Include common misspellings in test data to verify fuzzy matching and "Did you mean?" suggestions work correctly.
- **Facet Test Data**: Create data with known facet distributions (categories, price ranges, statuses) to verify facet counts and filtering accuracy.
- **Multi-Language Test Data**: Include content in multiple languages if application supports it, with proper language tags and analyzers.

**Test Data Isolation**:
- **Separate Search Indexes**: Use `products_test`, `documents_test` indexes separate from production. Prevents test data pollution and allows test-specific optimizations.
- **Test Data Factories**: Use builders/factories to create test data with realistic relationships. Example: `ProductFactory.createBackupProduct()` creates product with appropriate category, tags, and pricing.
- **Data Cleanup**: Clean up test data after tests complete. For search indexes, this may mean deleting test documents or resetting entire test index.

**Test Data Scenarios**:
- **Small Dataset**: <100 records for fast test execution, basic functionality verification.
- **Medium Dataset**: 1,000-10,000 records for performance testing, relevance testing with realistic data distribution.
- **Large Dataset**: 100,000+ records for scalability testing, index performance under load (may use synthetic data generators).

**Test Data Synchronization**:
- **Index Sync Testing**: Create test data, verify it appears in search index within expected timeframe. Test event-driven, CDC, and scheduled sync patterns.
- **Stale Data Testing**: Intentionally create stale scenarios (data updated but index not refreshed) to verify handling and user messaging.

### Test Environment Considerations

**Search Infrastructure Setup**:
- **Dedicated Test Search Engine**: Use separate OpenSearch/Elasticsearch cluster or lightweight search engine instance for tests. Don't share with production or staging.
- **Test-Specific Configuration**: Configure analyzers, field mappings, and relevance settings specifically for tests. May differ from production to optimize for test speed.
- **Index Lifecycle**: Create fresh test indexes for each test run or test class. Ensures test isolation and prevents test pollution.

**Test Environment Constraints**:
- **Resource Limitations**: Test environments may have less memory/CPU than production. Monitor test performance and adjust expectations or test data volume accordingly.
- **Network Latency**: Test environments may have higher latency. Account for this in performance test assertions, or run performance tests in production-like environments.
- **Data Volume**: Test environments typically have less data than production. Use synthetic data generators or data subsets for realistic testing.

**Test Environment Maintenance**:
- **Index Health**: Monitor test search index health (cluster status, disk usage, query performance). Unhealthy indexes cause flaky tests.
- **Version Alignment**: Keep test search engine versions aligned with production to catch version-specific issues early.
- **Configuration Drift**: Document and version control search engine configurations. Prevent configuration drift between test and production.

**CI/CD Integration**:
- **Test Environment Provisioning**: Automate test search engine setup in CI pipelines. Use Docker containers or infrastructure-as-code for consistent environments.
- **Parallel Test Execution**: If running tests in parallel, ensure each test uses isolated search indexes or test data namespaces to prevent conflicts.
- **Test Environment Cleanup**: Clean up test indexes and data after test runs to prevent resource exhaustion and test pollution.

### Regression Strategy

**Search Regression Test Suite**:
- **Core Functionality**: Maintain a suite of tests covering basic search, autocomplete, filtering, and zero-result handling. These should pass on every build.
- **Relevance Regression Tests**: Maintain known-good queries with expected top results. Run after any relevance algorithm changes. Fail build if expected results change unexpectedly.
- **Performance Regression Tests**: Baseline performance metrics (p95 latency, throughput). Alert on degradation, fail build if performance degrades beyond threshold.

**Regression Test Categories**:
- **Smoke Tests**: Critical search flows (basic search, autocomplete, zero results) run on every commit. Fast execution (<5 minutes).
- **Full Regression Suite**: Comprehensive search tests run before releases or on schedule (nightly). Includes edge cases, performance tests, accessibility tests.
- **Relevance Regression Suite**: Specific tests for relevance ranking run after algorithm changes. May require manual verification for complex relevance scenarios.

**Regression Test Maintenance**:
- **Query Evolution**: Update regression test queries based on actual user queries from analytics. Remove obsolete queries, add new common queries.
- **Expected Results Updates**: When relevance legitimately changes (intentional algorithm improvements), update expected results in regression tests. Document why changes were made.
- **Test Data Updates**: Keep test data realistic and aligned with production data patterns. Update test data when production schema or content patterns change.

**Preventing Regressions**:
- **Code Review**: Require review of search algorithm changes, index configuration changes, and search endpoint modifications.
- **Feature Flags**: Use feature flags for search improvements to enable gradual rollout and quick rollback if regressions detected.
- **A/B Testing**: Test search improvements with real users before full rollout. Measure impact on search metrics (click-through rate, zero-result rate).

### Defect Patterns

**Common Search Defects and How to Identify Them**:

**Index Synchronization Defects**:
- **Symptom**: Newly created content doesn't appear in search results.
- **How to Reproduce**: Create a product/document, immediately search for it. Verify it appears within expected SLA (event-driven: <5 seconds, scheduled: <1 hour).
- **Root Causes**: Event processing failures, CDC lag, scheduled reindex not running, search index update errors.
- **Test Strategy**: Test create/update/delete synchronization with realistic timing. Monitor index lag metrics.

**Relevance Ranking Defects**:
- **Symptom**: Wrong results appear first, relevant results buried.
- **How to Reproduce**: Search for known content, verify expected result appears in top 3-5 results. Test with various query patterns (exact match, partial match, multi-field).
- **Root Causes**: Incorrect field weighting, broken relevance algorithm, stale relevance configuration, missing searchable fields.
- **Test Strategy**: Maintain relevance test suite with known-good queries and expected results. Test field weighting, exact vs. partial matches, multi-field matching.

**Autocomplete Defects**:
- **Symptom**: Autocomplete doesn't appear, shows wrong suggestions, or is slow.
- **How to Reproduce**: Type in search box, verify suggestions appear after 2-3 characters. Test keyboard navigation, selection, and performance.
- **Root Causes**: Missing debouncing (too many requests), broken request cancellation, slow backend queries, incorrect prefix matching.
- **Test Strategy**: Test autocomplete appearance, suggestion relevance, keyboard navigation, performance under rapid typing.

**Filter Combination Defects**:
- **Symptom**: Filters don't work together correctly, produce wrong result counts, or break search.
- **How to Reproduce**: Apply multiple filters, verify result counts and results are correct. Test filter + search combinations.
- **Root Causes**: Incorrect filter logic (AND vs. OR), filter state management bugs, high-cardinality facet performance issues.
- **Test Strategy**: Test all filter combinations systematically. Test filter + search interaction. Test high-cardinality facets.

**Zero-Result Handling Defects**:
- **Symptom**: Zero-result page is unhelpful, shows no suggestions, or doesn't detect typos.
- **How to Reproduce**: Search for non-existent content, verify helpful zero-result page with suggestions and guidance.
- **Root Causes**: Missing zero-result handling, broken typo detection, no query suggestions implemented.
- **Test Strategy**: Test zero-result pages with various query types (typos, vague queries, filtered searches). Verify suggestions and guidance.

**Performance Defects**:
- **Symptom**: Search is slow, autocomplete lags, or search times out.
- **How to Reproduce**: Perform searches under load, test with large datasets, monitor response times.
- **Root Causes**: Missing indexes, inefficient queries, no caching, autocomplete not debounced, high-cardinality facets.
- **Test Strategy**: Performance testing under load, volume testing with large datasets, monitoring query latency.

**Accessibility Defects**:
- **Symptom**: Search not usable with keyboard or screen readers.
- **How to Reproduce**: Test with keyboard only (Tab, Arrow keys, Enter), test with screen reader (NVDA/VoiceOver).
- **Root Causes**: Missing ARIA attributes, broken keyboard navigation, focus management issues.
- **Test Strategy**: Keyboard navigation testing, screen reader testing, ARIA attribute verification.

**Defect Reporting Template**:
```
Title: [Brief description]
Severity: [Critical/High/Medium/Low]
Steps to Reproduce:
1. [Step 1]
2. [Step 2]
Expected: [What should happen]
Actual: [What actually happens]
Search Query: [The query used]
Environment: [Test/Staging/Production]
Search Backend: [Database Filtering/PostgreSQL FTS/OpenSearch/etc.]
Attachments: [Screenshots, logs, network traces]
```
