# Testing: Tables & Data Grids

## Contents

- [Pagination Testing](#pagination-testing)
- [Sorting Testing](#sorting-testing)
- [Filtering Testing](#filtering-testing)
- [Inline Editing Testing](#inline-editing-testing)
- [Bulk Action Testing](#bulk-action-testing)
- [Responsive Table Testing](#responsive-table-testing)
- [Performance Testing](#performance-testing)
- [Accessibility Testing](#accessibility-testing)
- [Export Testing](#export-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Pagination Testing

### Page Navigation

Test that users can navigate between pages correctly.

**Test Cases**:
- Click "Next" advances to next page
- Click "Previous" returns to previous page
- Click page number navigates directly to that page
- "First" and "Last" buttons work correctly
- Disabled state for "Previous" on first page and "Next" on last page

**Example (Playwright)**:

```typescript
import { test, expect } from '@playwright/test'

test('pagination navigation', async ({ page }) => {
  await page.goto('/users')
  
  // Verify initial state (page 1)
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 1')
  
  // Navigate to next page
  await page.click('[data-testid="next-page"]')
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 2')
  
  // Navigate to previous page
  await page.click('[data-testid="prev-page"]')
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 1')
  
  // Navigate directly to page 3
  await page.click('[data-testid="page-3"]')
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 3')
})
```

### Page Size Change

Test that changing page size updates the table correctly.

**Test Cases**:
- Changing page size reloads data with new size
- Page resets to 1 when size changes
- URL updates with new size parameter
- Selected rows are cleared when size changes

**Example**:

```typescript
test('page size change', async ({ page }) => {
  await page.goto('/users?page=3&size=20')
  
  // Change page size to 50
  await page.selectOption('[data-testid="page-size"]', '50')
  
  // Verify page resets to 1
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 1')
  
  // Verify URL updated
  await expect(page).toHaveURL(/size=50/)
  
  // Verify table shows 50 rows (or fewer if total < 50)
  const rows = page.locator('tbody tr')
  const count = await rows.count()
  expect(count).toBeLessThanOrEqual(50)
})
```

### Total Count Accuracy

Verify that total count matches actual data.

**Test Cases**:
- Total count displayed matches server response
- Total count updates correctly when filters applied
- "Showing X of Y" text is accurate

**Example**:

```typescript
test('total count accuracy', async ({ page }) => {
  await page.goto('/users')
  
  // Get total count from UI
  const totalText = await page.locator('[data-testid="total-count"]').textContent()
  const uiTotal = parseInt(totalText.match(/\d+/)[0])
  
  // Verify with API
  const response = await page.request.get('/api/users?size=1')
  const data = await response.json()
  const apiTotal = data.totalElements
  
  expect(uiTotal).toBe(apiTotal)
})
```

### Boundary Pages

Test edge cases for first and last pages.

**Test Cases**:
- First page (page 0 or 1) displays correctly
- Last page displays correct number of rows (may be < page size)
- Navigating beyond last page handles gracefully
- Empty dataset shows appropriate empty state

**Example**:

```typescript
test('boundary pages', async ({ page }) => {
  // Test first page
  await page.goto('/users?page=0')
  await expect(page.locator('[data-testid="prev-page"]')).toBeDisabled()
  
  // Navigate to last page
  const totalPages = await page.locator('[data-testid="total-pages"]').textContent()
  await page.goto(`/users?page=${parseInt(totalPages) - 1}`)
  await expect(page.locator('[data-testid="next-page"]')).toBeDisabled()
  
  // Verify last page may have fewer rows
  const rows = await page.locator('tbody tr').count()
  expect(rows).toBeLessThanOrEqual(20) // Assuming page size of 20
})
```

## Sorting Testing

### Ascending/Descending Toggle

Test that clicking column headers toggles sort order.

**Test Cases**:
- First click sorts ascending
- Second click sorts descending
- Third click removes sort (optional)
- Sort indicator (arrow) displays correctly
- Only one column sorted at a time (unless multi-sort enabled)

**Example**:

```typescript
test('sort toggle', async ({ page }) => {
  await page.goto('/users')
  
  // Click name column - should sort ascending
  await page.click('[data-testid="sort-name"]')
  await expect(page.locator('[data-testid="sort-name"]')).toHaveAttribute('aria-sort', 'ascending')
  
  // Verify data is sorted
  const firstRow = await page.locator('tbody tr:first-child td:first-child').textContent()
  const secondRow = await page.locator('tbody tr:nth-child(2) td:first-child').textContent()
  expect(firstRow.localeCompare(secondRow)).toBeLessThanOrEqual(0)
  
  // Click again - should sort descending
  await page.click('[data-testid="sort-name"]')
  await expect(page.locator('[data-testid="sort-name"]')).toHaveAttribute('aria-sort', 'descending')
})
```

### Multi-Column Sort

Test sorting by multiple columns (if supported).

**Test Cases**:
- Sorting by second column maintains first column sort
- Sort order is correct (primary sort, then secondary)
- Sort indicators show for all sorted columns

**Example**:

```typescript
test('multi-column sort', async ({ page }) => {
  await page.goto('/users')
  
  // Sort by status first
  await page.click('[data-testid="sort-status"]')
  
  // Sort by name (should maintain status sort)
  await page.click('[data-testid="sort-name"]', { modifiers: ['Shift'] })
  
  // Verify both columns show sort indicators
  await expect(page.locator('[data-testid="sort-status"]')).toHaveAttribute('aria-sort')
  await expect(page.locator('[data-testid="sort-name"]')).toHaveAttribute('aria-sort')
  
  // Verify data is sorted correctly (status first, then name)
  const rows = await page.locator('tbody tr').all()
  // Assertion logic for multi-column sort order
})
```

### Sort Persistence Across Pagination

Test that sort order persists when navigating pages.

**Test Cases**:
- Sort order maintained when changing pages
- Sort order maintained when changing page size
- Sort order encoded in URL

**Example**:

```typescript
test('sort persistence', async ({ page }) => {
  await page.goto('/users')
  
  // Sort by name
  await page.click('[data-testid="sort-name"]')
  
  // Navigate to page 2
  await page.click('[data-testid="next-page"]')
  
  // Verify sort is still applied
  await expect(page.locator('[data-testid="sort-name"]')).toHaveAttribute('aria-sort')
  await expect(page).toHaveURL(/sort=name/)
  
  // Verify data is still sorted
  const firstRow = await page.locator('tbody tr:first-child td:first-child').textContent()
  const secondRow = await page.locator('tbody tr:nth-child(2) td:first-child').textContent()
  expect(firstRow.localeCompare(secondRow)).toBeLessThanOrEqual(0)
})
```

## Filtering Testing

### Filter Application

Test that filters correctly narrow down results.

**Test Cases**:
- Text filter filters rows correctly
- Dropdown filter filters rows correctly
- Date range filter filters rows correctly
- Filter clears when cleared
- Multiple filters combine correctly (AND logic)

**Example**:

```typescript
test('filter application', async ({ page }) => {
  await page.goto('/users')
  
  const initialRowCount = await page.locator('tbody tr').count()
  
  // Apply name filter
  await page.fill('[data-testid="filter-name"]', 'john')
  await page.click('[data-testid="apply-filter"]')
  
  // Wait for table to update
  await page.waitForLoadState('networkidle')
  
  // Verify row count decreased
  const filteredRowCount = await page.locator('tbody tr').count()
  expect(filteredRowCount).toBeLessThanOrEqual(initialRowCount)
  
  // Verify all visible rows match filter
  const rows = await page.locator('tbody tr').all()
  for (const row of rows) {
    const name = await row.locator('td:first-child').textContent()
    expect(name.toLowerCase()).toContain('john')
  }
})
```

### Filter Combination

Test that multiple filters work together correctly.

**Test Cases**:
- Multiple filters combine with AND logic
- Filters persist in URL
- Clearing one filter doesn't clear others

**Example**:

```typescript
test('filter combination', async ({ page }) => {
  await page.goto('/users')
  
  // Apply multiple filters
  await page.fill('[data-testid="filter-name"]', 'john')
  await page.selectOption('[data-testid="filter-status"]', 'ACTIVE')
  await page.click('[data-testid="apply-filter"]')
  
  await page.waitForLoadState('networkidle')
  
  // Verify URL contains both filters
  await expect(page).toHaveURL(/name=john/)
  await expect(page).toHaveURL(/status=ACTIVE/)
  
  // Verify rows match both filters
  const rows = await page.locator('tbody tr').all()
  for (const row of rows) {
    const name = await row.locator('td:first-child').textContent()
    const status = await row.locator('td:nth-child(3)').textContent()
    expect(name.toLowerCase()).toContain('john')
    expect(status).toBe('ACTIVE')
  }
})
```

### Filter Clearing

Test that filters can be cleared individually or all at once.

**Test Cases**:
- Individual filter clear button works
- "Clear all filters" button clears all filters
- Table resets to unfiltered state
- Page resets to 1 when filters cleared

**Example**:

```typescript
test('filter clearing', async ({ page }) => {
  await page.goto('/users?name=john&status=ACTIVE&page=3')
  
  // Clear all filters
  await page.click('[data-testid="clear-all-filters"]')
  
  await page.waitForLoadState('networkidle')
  
  // Verify filters removed from URL
  await expect(page).not.toHaveURL(/name=/)
  await expect(page).not.toHaveURL(/status=/)
  
  // Verify page reset to 1
  await expect(page.locator('[data-testid="page-indicator"]')).toContainText('Page 1')
  
  // Verify more rows visible (unfiltered)
  const rowCount = await page.locator('tbody tr').count()
  expect(rowCount).toBeGreaterThan(0)
})
```

### Filter + Sort + Pagination Interaction

Test that filters, sorting, and pagination work together correctly.

**Test Cases**:
- Filtered data can be sorted
- Sorted filtered data can be paginated
- Changing sort resets page to 1
- Changing filter resets page to 1
- URL contains all state (filters, sort, page)

**Example**:

```typescript
test('filter sort pagination interaction', async ({ page }) => {
  await page.goto('/users')
  
  // Apply filter
  await page.fill('[data-testid="filter-name"]', 'john')
  await page.click('[data-testid="apply-filter"]')
  await page.waitForLoadState('networkidle')
  
  // Sort
  await page.click('[data-testid="sort-name"]')
  await page.waitForLoadState('networkidle')
  
  // Navigate to page 2
  await page.click('[data-testid="next-page"]')
  await page.waitForLoadState('networkidle')
  
  // Verify URL contains all state
  await expect(page).toHaveURL(/name=john/)
  await expect(page).toHaveURL(/sort=name/)
  await expect(page).toHaveURL(/page=1/) // Should reset to 1 after sort
  
  // Verify data is filtered, sorted, and paginated correctly
  const rows = await page.locator('tbody tr').all()
  expect(rows.length).toBeGreaterThan(0)
  
  // Verify rows match filter and are sorted
  for (const row of rows) {
    const name = await row.locator('td:first-child').textContent()
    expect(name.toLowerCase()).toContain('john')
  }
})
```

## Inline Editing Testing

### Edit, Save, Cancel

Test basic inline editing workflow.

**Test Cases**:
- Double-click (or click edit icon) enters edit mode
- Changes can be saved
- Changes can be cancelled (reverts to original)
- Edit mode shows appropriate UI (input field, save/cancel buttons)

**Example**:

```typescript
test('inline edit save cancel', async ({ page }) => {
  await page.goto('/users')
  
  // Get original value
  const originalValue = await page.locator('tbody tr:first-child td:nth-child(2)').textContent()
  
  // Enter edit mode
  await page.dblclick('tbody tr:first-child td:nth-child(2)')
  
  // Verify input field appears
  await expect(page.locator('tbody tr:first-child td:nth-child(2) input')).toBeVisible()
  
  // Change value
  await page.fill('tbody tr:first-child td:nth-child(2) input', 'newemail@example.com')
  
  // Save
  await page.click('[data-testid="save-edit"]')
  await page.waitForLoadState('networkidle')
  
  // Verify value updated
  await expect(page.locator('tbody tr:first-child td:nth-child(2)')).toContainText('newemail@example.com')
  
  // Test cancel
  await page.dblclick('tbody tr:first-child td:nth-child(2)')
  await page.fill('tbody tr:first-child td:nth-child(2) input', 'wrong@example.com')
  await page.click('[data-testid="cancel-edit"]')
  
  // Verify value reverted
  await expect(page.locator('tbody tr:first-child td:nth-child(2)')).toContainText('newemail@example.com')
})
```

### Validation Errors

Test that validation errors display correctly during inline editing.

**Test Cases**:
- Invalid input shows error message
- Save button disabled when validation fails
- Error message clears when input becomes valid
- Multiple validation errors display correctly

**Example**:

```typescript
test('inline edit validation', async ({ page }) => {
  await page.goto('/users')
  
  // Enter edit mode for email field
  await page.dblclick('tbody tr:first-child td:nth-child(2)')
  
  // Enter invalid email
  await page.fill('tbody tr:first-child td:nth-child(2) input', 'invalid-email')
  
  // Try to save (should show error)
  await page.click('[data-testid="save-edit"]')
  
  // Verify error message appears
  await expect(page.locator('[data-testid="validation-error"]')).toBeVisible()
  await expect(page.locator('[data-testid="validation-error"]')).toContainText('Invalid email')
  
  // Fix email
  await page.fill('tbody tr:first-child td:nth-child(2) input', 'valid@example.com')
  
  // Error should clear
  await expect(page.locator('[data-testid="validation-error"]')).not.toBeVisible()
  
  // Save should work now
  await page.click('[data-testid="save-edit"]')
  await page.waitForLoadState('networkidle')
})
```

### Concurrent Edit Conflicts

Test handling of concurrent edits (optimistic locking).

**Test Cases**:
- Editing a row that was modified by another user shows conflict error
- User can refresh to see latest data
- User can overwrite or cancel on conflict

**Example**:

```typescript
test('concurrent edit conflict', async ({ page, context }) => {
  await page.goto('/users')
  
  // Open same page in second browser (simulating another user)
  const page2 = await context.newPage()
  await page2.goto('/users')
  
  // User 1 starts editing
  await page.dblclick('tbody tr:first-child td:nth-child(2)')
  await page.fill('tbody tr:first-child td:nth-child(2) input', 'user1@example.com')
  
  // User 2 saves a change first (simulate via API)
  await page2.request.patch('/api/users/1', {
    data: { email: 'user2@example.com' }
  })
  
  // User 1 tries to save
  await page.click('[data-testid="save-edit"]')
  
  // Verify conflict error appears
  await expect(page.locator('[data-testid="conflict-error"]')).toBeVisible()
  await expect(page.locator('[data-testid="conflict-error"]')).toContainText('modified by another user')
  
  // User can refresh to see latest
  await page.click('[data-testid="refresh-data"]')
  await expect(page.locator('tbody tr:first-child td:nth-child(2)')).toContainText('user2@example.com')
})
```

## Bulk Action Testing

### Select Multiple

Test selecting multiple rows for bulk operations.

**Test Cases**:
- Checkbox selects individual row
- "Select all" selects all rows on current page
- Selected count displays correctly
- Bulk action buttons enabled when rows selected

**Example**:

```typescript
test('select multiple rows', async ({ page }) => {
  await page.goto('/users')
  
  // Select first row
  await page.check('tbody tr:first-child [data-testid="row-checkbox"]')
  
  // Verify selected count
  await expect(page.locator('[data-testid="selected-count"]')).toContainText('1 selected')
  
  // Select second row
  await page.check('tbody tr:nth-child(2) [data-testid="row-checkbox"]')
  
  // Verify selected count updated
  await expect(page.locator('[data-testid="selected-count"]')).toContainText('2 selected')
  
  // Verify bulk action buttons enabled
  await expect(page.locator('[data-testid="bulk-delete"]')).toBeEnabled()
  await expect(page.locator('[data-testid="bulk-export"]')).toBeEnabled()
})
```

### Select All

Test "select all" functionality.

**Test Cases**:
- "Select all" selects all rows on current page
- "Select all" checkbox state reflects selection
- Deselecting one row unchecks "select all"
- "Select all across pages" option (if available)

**Example**:

```typescript
test('select all', async ({ page }) => {
  await page.goto('/users')
  
  // Select all
  await page.check('[data-testid="select-all"]')
  
  // Verify all rows selected
  const checkboxes = await page.locator('tbody [data-testid="row-checkbox"]').all()
  for (const checkbox of checkboxes) {
    await expect(checkbox).toBeChecked()
  }
  
  // Verify selected count
  const rowCount = await page.locator('tbody tr').count()
  await expect(page.locator('[data-testid="selected-count"]')).toContainText(`${rowCount} selected`)
  
  // Unselect one row
  await page.uncheck('tbody tr:first-child [data-testid="row-checkbox"]')
  
  // Verify "select all" unchecked
  await expect(page.locator('[data-testid="select-all"]')).not.toBeChecked()
})
```

### Action Execution

Test that bulk actions execute correctly.

**Test Cases**:
- Bulk delete removes selected rows
- Bulk update updates selected rows
- Bulk export exports selected rows only
- Confirmation dialog appears for destructive actions
- Success/error messages display correctly

**Example**:

```typescript
test('bulk delete', async ({ page }) => {
  await page.goto('/users')
  
  const initialRowCount = await page.locator('tbody tr').count()
  
  // Select two rows
  await page.check('tbody tr:first-child [data-testid="row-checkbox"]')
  await page.check('tbody tr:nth-child(2) [data-testid="row-checkbox"]')
  
  // Click bulk delete
  await page.click('[data-testid="bulk-delete"]')
  
  // Confirm deletion
  await page.click('[data-testid="confirm-delete"]')
  
  await page.waitForLoadState('networkidle')
  
  // Verify rows removed
  const newRowCount = await page.locator('tbody tr').count()
  expect(newRowCount).toBe(initialRowCount - 2)
  
  // Verify success message
  await expect(page.locator('[data-testid="success-message"]')).toContainText('2 items deleted')
})
```

### Partial Failure Handling

Test handling when some bulk operations fail.

**Test Cases**:
- Partial success shows which items succeeded/failed
- Failed items remain selected
- User can retry failed items
- Error details available

**Example**:

```typescript
test('bulk action partial failure', async ({ page }) => {
  await page.goto('/users')
  
  // Select multiple rows (one will fail due to permissions)
  await page.check('tbody tr:first-child [data-testid="row-checkbox"]')
  await page.check('tbody tr:nth-child(2) [data-testid="row-checkbox"]')
  
  // Mock API to return partial failure
  await page.route('/api/users/bulk-delete', route => {
    route.fulfill({
      status: 207, // Multi-Status
      body: JSON.stringify({
        succeeded: [1],
        failed: [{ id: 2, error: 'Permission denied' }]
      })
    })
  })
  
  await page.click('[data-testid="bulk-delete"]')
  await page.click('[data-testid="confirm-delete"]')
  
  // Verify partial failure message
  await expect(page.locator('[data-testid="partial-failure-message"]')).toBeVisible()
  await expect(page.locator('[data-testid="partial-failure-message"]')).toContainText('1 succeeded, 1 failed')
  
  // Verify failed row still selected
  await expect(page.locator('tbody tr:nth-child(2) [data-testid="row-checkbox"]')).toBeChecked()
})
```

## Responsive Table Testing

### Mobile Rendering

Test table rendering on mobile devices.

**Test Cases**:
- Table stacks vertically on mobile (if using stacked layout)
- Horizontal scroll works with sticky headers (if using scrollable layout)
- Touch interactions work (tap to select, swipe to scroll)
- Column visibility adapts to screen size

**Example**:

```typescript
test('mobile table rendering', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 })
  await page.goto('/users')
  
  // Verify table adapts (either stacked or scrollable)
  const table = page.locator('[data-testid="user-table"]')
  
  // If using stacked layout, verify cards appear
  // If using scrollable, verify horizontal scroll available
  const canScroll = await table.evaluate(el => el.scrollWidth > el.clientWidth)
  expect(canScroll).toBe(true) // Or false, depending on design
  
  // Verify sticky header
  const header = page.locator('thead')
  const headerPosition = await header.evaluate(el => {
    const rect = el.getBoundingClientRect()
    return { top: rect.top, position: window.getComputedStyle(el).position }
  })
  expect(headerPosition.position).toBe('sticky')
})
```

### Touch Interactions

Test touch-specific interactions on mobile.

**Test Cases**:
- Tap selects row
- Long press shows context menu (if available)
- Swipe scrolls table
- Pinch zoom doesn't break layout

**Example**:

```typescript
test('touch interactions', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile only test')
  
  await page.setViewportSize({ width: 375, height: 667 })
  await page.goto('/users')
  
  // Tap to select
  await page.tap('tbody tr:first-child')
  await expect(page.locator('tbody tr:first-child')).toHaveClass(/selected/)
  
  // Swipe to scroll
  await page.touchscreen.tap(200, 400)
  await page.mouse.move(200, 400)
  await page.mouse.down()
  await page.mouse.move(200, 200)
  await page.mouse.up()
  
  // Verify table scrolled
  const scrollTop = await page.evaluate(() => window.scrollY)
  expect(scrollTop).toBeGreaterThan(0)
})
```

## Performance Testing

### Table Load Time

Test table performance with different dataset sizes.

**Test Cases**:
- Table loads in < 1 second for 100 rows
- Table loads in < 2 seconds for 1,000 rows (server-side paginated)
- Table loads in < 3 seconds for 10,000 rows (server-side paginated)
- Initial render shows skeleton/loading state

**Example**:

```typescript
test('table load performance', async ({ page }) => {
  // Test with 100 rows
  const startTime = Date.now()
  await page.goto('/users?size=100')
  await page.waitForLoadState('networkidle')
  const loadTime = Date.now() - startTime
  
  expect(loadTime).toBeLessThan(1000)
  
  // Test with 1000 rows (server-side)
  const startTime2 = Date.now()
  await page.goto('/users?size=1000')
  await page.waitForLoadState('networkidle')
  const loadTime2 = Date.now() - startTime2
  
  expect(loadTime2).toBeLessThan(2000)
})
```

### Virtual Scroll Smoothness

Test virtual scrolling performance for large datasets.

**Test Cases**:
- Scrolling is smooth (60 FPS)
- No lag when scrolling quickly
- Rows render correctly during scroll
- Scroll position maintained after data refresh

**Example**:

```typescript
test('virtual scroll performance', async ({ page }) => {
  await page.goto('/users?virtual=true')
  
  // Measure scroll performance
  const scrollMetrics = await page.evaluate(() => {
    return new Promise(resolve => {
      let frameCount = 0
      let lastTime = performance.now()
      
      const measureFrame = () => {
        frameCount++
        const currentTime = performance.now()
        if (currentTime - lastTime >= 1000) {
          resolve({ fps: frameCount, time: currentTime - lastTime })
        } else {
          requestAnimationFrame(measureFrame)
        }
      }
      
      // Start scrolling
      window.scrollTo(0, 1000)
      requestAnimationFrame(measureFrame)
    })
  })
  
  expect(scrollMetrics.fps).toBeGreaterThan(50) // Should be close to 60 FPS
})
```

## Accessibility Testing

### Keyboard Navigation

Test keyboard navigation through table cells.

**Test Cases**:
- Arrow keys move between cells
- Tab moves to next editable cell
- Enter enters edit mode
- Escape exits edit mode
- Home/End navigate to first/last cell in row

**Example**:

```typescript
test('keyboard navigation', async ({ page }) => {
  await page.goto('/users')
  
  // Focus first cell
  await page.keyboard.press('Tab')
  await page.keyboard.press('Tab') // Navigate to table
  await page.keyboard.press('ArrowRight')
  
  // Verify focus moved to next cell
  const focusedElement = await page.evaluate(() => document.activeElement?.tagName)
  expect(focusedElement).toBe('TD')
  
  // Test Enter to edit
  await page.keyboard.press('Enter')
  await expect(page.locator('input:focus')).toBeVisible()
  
  // Test Escape to cancel
  await page.keyboard.press('Escape')
  await expect(page.locator('input')).not.toBeVisible()
})
```

### Screen Reader Support

Test screen reader announcements.

**Test Cases**:
- Column headers announced when navigating
- Row numbers announced
- Sort state announced
- Selection state announced
- Edit mode announced

**Example**:

```typescript
test('screen reader support', async ({ page }) => {
  await page.goto('/users')
  
  // Verify proper table markup
  const table = page.locator('table')
  await expect(table.locator('thead')).toBeVisible()
  await expect(table.locator('tbody')).toBeVisible()
  
  // Verify column headers have scope
  const headers = await table.locator('th').all()
  for (const header of headers) {
    const scope = await header.getAttribute('scope')
    expect(scope).toBe('col')
  }
  
  // Verify sortable columns have aria-sort
  const sortableHeader = page.locator('[data-testid="sort-name"]')
  await expect(sortableHeader).toHaveAttribute('aria-sort')
  
  // Verify row selection announced
  await page.check('tbody tr:first-child [data-testid="row-checkbox"]')
  const checkbox = page.locator('tbody tr:first-child [data-testid="row-checkbox"]')
  await expect(checkbox).toHaveAttribute('aria-checked', 'true')
})
```

### Sort Indicators

Test that sort indicators are accessible.

**Test Cases**:
- Sort direction indicated visually and via ARIA
- Screen readers announce sort state
- Sortable columns identified

**Example**:

```typescript
test('sort indicators accessibility', async ({ page }) => {
  await page.goto('/users')
  
  const sortableColumn = page.locator('[data-testid="sort-name"]')
  
  // Verify initial state (not sorted)
  await expect(sortableColumn).toHaveAttribute('aria-sort', 'none')
  
  // Click to sort ascending
  await sortableColumn.click()
  await expect(sortableColumn).toHaveAttribute('aria-sort', 'ascending')
  
  // Click to sort descending
  await sortableColumn.click()
  await expect(sortableColumn).toHaveAttribute('aria-sort', 'descending')
})
```

## Export Testing

### CSV Accuracy

Test that exported CSV matches table data.

**Test Cases**:
- Exported CSV contains correct data
- Headers match column labels
- Special characters escaped correctly
- Filtered data only (if export respects filters)

**Example**:

```typescript
test('CSV export accuracy', async ({ page }) => {
  await page.goto('/users?name=john')
  
  // Trigger export
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('[data-testid="export-csv"]')
  ])
  
  // Read downloaded file
  const path = await download.path()
  const csvContent = await fs.readFile(path, 'utf-8')
  const lines = csvContent.split('\n')
  
  // Verify headers
  expect(lines[0]).toBe('Name,Email,Status')
  
  // Verify data matches filtered table
  const tableRows = await page.locator('tbody tr').all()
  expect(lines.length - 1).toBe(tableRows.length) // -1 for header
  
  // Verify each row matches
  for (let i = 0; i < tableRows.length; i++) {
    const tableCells = await tableRows[i].locator('td').allTextContents()
    const csvCells = lines[i + 1].split(',')
    expect(csvCells[0]).toContain(tableCells[0])
  }
})
```

### Large Dataset Export

Test export performance for large datasets.

**Test Cases**:
- Export triggers async job for large datasets
- User notified when export ready
- Export file downloadable
- Export includes all filtered data (not just current page)

**Example**:

```typescript
test('large dataset export', async ({ page }) => {
  await page.goto('/users?size=10000')
  
  // Trigger export (should be async)
  await page.click('[data-testid="export-csv"]')
  
  // Verify notification appears
  await expect(page.locator('[data-testid="export-notification"]')).toBeVisible()
  await expect(page.locator('[data-testid="export-notification"]')).toContainText('Export in progress')
  
  // Wait for export completion (poll status)
  await page.waitForFunction(() => {
    const notification = document.querySelector('[data-testid="export-notification"]')
    return notification?.textContent?.includes('ready')
  }, { timeout: 30000 })
  
  // Download export
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('[data-testid="download-export"]')
  ])
  
  expect(download.suggestedFilename()).toMatch(/\.csv$/)
})
```

### Special Characters in Data

Test that special characters export correctly.

**Test Cases**:
- Commas in data properly quoted/escaped
- Quotes in data properly escaped
- Newlines in data handled correctly
- Unicode characters preserved

**Example**:

```typescript
test('export special characters', async ({ page }) => {
  // Create test data with special characters
  await page.goto('/users')
  
  // Add user with special characters
  await page.click('[data-testid="add-user"]')
  await page.fill('[data-testid="user-name"]', 'John "Johnny" O\'Brien, Jr.')
  await page.fill('[data-testid="user-email"]', 'john@example.com')
  await page.click('[data-testid="save-user"]')
  
  // Export
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.click('[data-testid="export-csv"]')
  ])
  
  const path = await download.path()
  const csvContent = await fs.readFile(path, 'utf-8')
  
  // Verify special characters handled correctly
  expect(csvContent).toContain('John "Johnny" O\'Brien, Jr.')
  // Should be quoted: "John ""Johnny"" O'Brien, Jr."
})
```

## QA and Test Engineer Perspective

### Test Strategy

**Approach**: Test tables at multiple levels:
1. **Unit tests**: Table component rendering, state management
2. **Integration tests**: API integration, data fetching, URL state
3. **E2E tests**: Full user workflows (filter → sort → paginate → export)
4. **Visual regression tests**: Table layout, responsive design
5. **Performance tests**: Load time, scroll performance, large dataset handling

**Priority**: Focus E2E tests on critical user paths (filtering, sorting, pagination, export) rather than testing every possible combination.

### Test Data Management

**Challenges**: Tables require diverse test data (various data types, sizes, edge cases).

**Solutions**:
- Use factories/fixtures to generate test data
- Create test datasets of different sizes (100, 1K, 10K rows)
- Include edge cases (empty strings, special characters, null values, very long text)
- Use database seeds for consistent test data

**Example**:

```typescript
// Test data factory
const createUser = (overrides = {}) => ({
  id: faker.datatype.number(),
  name: faker.name.fullName(),
  email: faker.internet.email(),
  status: faker.helpers.arrayElement(['ACTIVE', 'INACTIVE', 'PENDING']),
  ...overrides
})

const testUsers = Array.from({ length: 1000 }, () => createUser())
```

### Automation Tools

**Recommended Tools**:
- **Playwright**: E2E testing, cross-browser, mobile testing
- **Vitest/Jest**: Unit and integration tests for table components
- **Lighthouse CI**: Performance testing
- **axe-core**: Accessibility testing
- **Percy/Chromatic**: Visual regression testing

**Example Playwright Setup**:

```typescript
import { test, expect } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  // Seed test data
  await page.request.post('/api/test/seed', { data: { count: 1000 } })
  await page.goto('/users')
})

test.afterEach(async ({ page }) => {
  // Cleanup
  await page.request.post('/api/test/cleanup')
})
```

### Edge Cases to Test

**Critical Edge Cases**:
1. Empty dataset (no rows)
2. Single row
3. Exactly one page of data
4. Very long text in cells (truncation/ellipsis)
5. Special characters (Unicode, emoji, SQL injection attempts)
6. Rapid user interactions (clicking pagination quickly)
7. Network failures during data fetch
8. Concurrent modifications (optimistic locking conflicts)
9. Very wide tables (horizontal scroll)
10. Very tall tables (vertical scroll, virtual scrolling)

### Performance Benchmarks

**Target Metrics**:
- Initial load: < 1 second (P95)
- Sort/filter/pagination: < 200ms (P95)
- Export (small): < 2 seconds
- Export (large, async): Job queued within 1 second
- Scroll FPS: > 55 FPS for virtual scrolling
- Memory usage: < 100MB for 10K rows (virtual scrolling)

**Monitoring**: Set up performance monitoring in production to track these metrics and alert on degradation.

### Regression Prevention

**Strategies**:
1. **Visual regression tests**: Catch layout breaks automatically
2. **Accessibility regression tests**: Ensure ARIA attributes maintained
3. **API contract tests**: Ensure backend pagination/sorting/filtering contracts don't break
4. **Cross-browser testing**: Test on Chrome, Firefox, Safari, Edge
5. **Mobile testing**: Test on iOS and Android devices

**CI Integration**: Run table tests on every PR, block merges on failures.
