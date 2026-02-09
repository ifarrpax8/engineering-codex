# Testing: Data Visualization

## Contents

- [Chart Rendering Testing](#chart-rendering-testing)
- [Dashboard Layout Testing](#dashboard-layout-testing)
- [Export Testing](#export-testing)
- [Interaction Testing](#interaction-testing)
- [Performance Testing](#performance-testing)
- [Accessibility Testing](#accessibility-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Chart Rendering Testing

### Verify Correct Chart Type Renders

```typescript
// Vue 3 Component Test
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import RevenueChart from './RevenueChart.vue'

describe('RevenueChart', () => {
  it('renders a line chart for revenue data', () => {
    const wrapper = mount(RevenueChart, {
      props: {
        data: [
          { date: '2025-01-01', revenue: 1000 },
          { date: '2025-01-02', revenue: 1200 }
        ],
        chartType: 'line'
      }
    })
    
    // Verify Chart.js line chart is rendered
    const canvas = wrapper.find('canvas')
    expect(canvas.exists()).toBe(true)
    
    // Verify chart instance is line type
    const chartInstance = wrapper.vm.chart
    expect(chartInstance.config.type).toBe('line')
  })
})
```

```tsx
// React Component Test
import { render, screen } from '@testing-library/react'
import { RevenueChart } from './RevenueChart'

describe('RevenueChart', () => {
  it('renders bar chart when chartType is bar', () => {
    const data = [
      { date: '2025-01-01', revenue: 1000 },
      { date: '2025-01-02', revenue: 1200 }
    ]
    
    render(<RevenueChart data={data} chartType="bar" />)
    
    // Verify Recharts BarChart component is rendered
    const chart = screen.getByRole('img', { name: /revenue chart/i })
    expect(chart).toBeInTheDocument()
  })
})
```

### Data Points Match Source Data

```typescript
// Test that chart data matches input
describe('Chart Data Accuracy', () => {
  it('displays all data points from source', () => {
    const sourceData = [
      { date: '2025-01-01', value: 1000 },
      { date: '2025-01-02', value: 1200 },
      { date: '2025-01-03', value: 1500 }
    ]
    
    const wrapper = mount(RevenueChart, { props: { data: sourceData } })
    const chartInstance = wrapper.vm.chart
    
    // Verify chart has correct number of data points
    expect(chartInstance.data.datasets[0].data).toHaveLength(3)
    expect(chartInstance.data.datasets[0].data).toEqual([1000, 1200, 1500])
    expect(chartInstance.data.labels).toEqual(['2025-01-01', '2025-01-02', '2025-01-03'])
  })
  
  it('handles empty data array', () => {
    const wrapper = mount(RevenueChart, { props: { data: [] } })
    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.find('.empty-state').text()).toContain('No data')
  })
})
```

### Axes Labels Correct

```typescript
describe('Chart Axes', () => {
  it('displays correct X-axis labels', () => {
    const data = [
      { date: '2025-01-01', revenue: 1000 },
      { date: '2025-01-02', revenue: 1200 }
    ]
    
    const wrapper = mount(RevenueChart, { props: { data } })
    const chartInstance = wrapper.vm.chart
    
    // Verify X-axis scale configuration
    const xScale = chartInstance.scales.x
    expect(xScale.ticks).toHaveLength(2)
    expect(xScale.ticks[0].label).toBe('2025-01-01')
  })
  
  it('formats Y-axis with currency', () => {
    const wrapper = mount(RevenueChart, { 
      props: { 
        data: [{ date: '2025-01-01', revenue: 1000 }],
        currency: true
      }
    })
    
    const chartInstance = wrapper.vm.chart
    const yScale = chartInstance.scales.y
    
    // Verify Y-axis tick formatter includes dollar sign
    const tick = yScale.ticks[0]
    expect(tick.label).toMatch(/^\$/)
  })
})
```

## Dashboard Layout Testing

### Widgets Render in Correct Positions

```typescript
// Test dashboard grid layout
describe('Dashboard Layout', () => {
  it('renders widgets in correct grid positions', () => {
    const widgets = [
      { id: '1', x: 0, y: 0, width: 6, height: 4 },
      { id: '2', x: 6, y: 0, width: 6, height: 4 }
    ]
    
    const wrapper = mount(Dashboard, { props: { widgets } })
    
    const widget1 = wrapper.find('[data-widget-id="1"]')
    const widget2 = wrapper.find('[data-widget-id="2"]')
    
    // Verify CSS grid positioning
    expect(widget1.attributes('style')).toContain('grid-column: span 6')
    expect(widget2.attributes('style')).toContain('grid-column: span 6')
  })
})
```

### Responsive Behavior

```typescript
describe('Dashboard Responsive Behavior', () => {
  it('stacks widgets vertically on mobile', async () => {
    // Mock window.innerWidth
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 600
    })
    
    const wrapper = mount(Dashboard, { props: { widgets } })
    
    // Trigger resize event
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()
    
    // Verify mobile layout (single column)
    const dashboard = wrapper.find('.dashboard-grid')
    expect(dashboard.attributes('style')).toContain('grid-template-columns: 1fr')
  })
})
```

### Filter/Date Range Propagation

```typescript
describe('Dashboard Filters', () => {
  it('propagates date range to all widgets', async () => {
    const wrapper = mount(Dashboard)
    
    // Set date range
    await wrapper.setData({
      dateRange: {
        start: '2025-01-01',
        end: '2025-01-31'
      }
    })
    
    // Verify all widgets receive date range
    const widgets = wrapper.findAllComponents(WidgetComponent)
    widgets.forEach(widget => {
      expect(widget.props('dateRange')).toEqual({
        start: '2025-01-01',
        end: '2025-01-31'
      })
    })
  })
  
  it('refetches widget data when date range changes', async () => {
    const fetchSpy = vi.fn()
    const wrapper = mount(Dashboard, {
      global: {
        provide: {
          fetchWidgetData: fetchSpy
        }
      }
    })
    
    await wrapper.setData({
      dateRange: { start: '2025-02-01', end: '2025-02-28' }
    })
    
    await wrapper.vm.$nextTick()
    
    // Verify fetch was called for each widget
    expect(fetchSpy).toHaveBeenCalledTimes(wrapper.vm.widgets.length)
  })
})
```

## Export Testing

### PDF Contains Correct Data and Charts

```typescript
// E2E test with Playwright
import { test, expect } from '@playwright/test'

test('PDF export contains correct chart data', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Wait for chart to load
  await page.waitForSelector('canvas')
  
  // Click export button
  await page.click('button[aria-label="Export as PDF"]')
  
  // Wait for download
  const downloadPromise = page.waitForEvent('download')
  const download = await downloadPromise
  
  // Save file temporarily
  const path = await download.path()
  
  // Verify PDF contains expected content (using pdf-parse or similar)
  const pdf = require('pdf-parse')
  const data = await pdf(fs.readFileSync(path))
  
  expect(data.text).toContain('Revenue Dashboard')
  expect(data.text).toContain('2025-01-01')
  expect(data.text).toContain('$1,000')
})
```

### CSV Matches Displayed Data

```typescript
test('CSV export matches displayed chart data', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Get displayed data from chart
  const chartData = await page.evaluate(() => {
    const chart = window.chartInstance
    return chart.data.datasets[0].data
  })
  
  // Export CSV
  await page.click('button[aria-label="Export as CSV"]')
  const download = await page.waitForEvent('download')
  const csvContent = await download.text()
  
  // Parse CSV and verify data matches
  const rows = csvContent.split('\n').slice(1) // Skip header
  const csvValues = rows.map(row => parseFloat(row.split(',')[1]))
  
  expect(csvValues).toEqual(chartData)
})
```

### Large Export Completes Successfully

```typescript
// Integration test for async export
describe('Large Export', () => {
  it('completes export job for 100K+ rows', async () => {
    const exportJob = await exportService.requestExport(
      userId: 'test-user',
      dashboardId: 'test-dashboard',
      format: ExportFormat.CSV
    )
    
    expect(exportJob.status).toBe(ExportStatus.PENDING)
    
    // Process export (simulate job queue)
    await exportService.processExport(exportJob.id)
    
    // Verify job completed
    const completedJob = await exportJobRepository.findById(exportJob.id)
    expect(completedJob.status).toBe(ExportStatus.COMPLETED)
    expect(completedJob.fileUrl).toBeDefined()
    
    // Verify file exists and has correct size
    const fileBytes = await storageService.download(completedJob.fileUrl)
    expect(fileBytes.length).toBeGreaterThan(0)
  }, 30000) // 30 second timeout for large export
})
```

## Interaction Testing

### Drill-Down Navigation

```typescript
test('clicking chart navigates to detail view', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Click on a data point
  const canvas = page.locator('canvas')
  await canvas.click({ position: { x: 100, y: 200 } })
  
  // Verify navigation to detail page
  await expect(page).toHaveURL(/\/dashboard\/revenue\/detail/)
  await expect(page.locator('h1')).toContainText('Revenue Detail')
})
```

### Tooltip Content on Hover

```typescript
test('tooltip displays correct data on hover', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  const canvas = page.locator('canvas')
  
  // Hover over chart
  await canvas.hover({ position: { x: 150, y: 250 } })
  
  // Wait for tooltip
  const tooltip = page.locator('.chartjs-tooltip')
  await expect(tooltip).toBeVisible()
  
  // Verify tooltip content
  await expect(tooltip).toContainText('2025-01-15')
  await expect(tooltip).toContainText('$1,500')
})
```

### Zoom/Pan Interactions

```typescript
test('zoom and pan work correctly', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  const canvas = page.locator('canvas')
  
  // Zoom in (wheel event)
  await canvas.dispatchEvent('wheel', {
    deltaY: -100,
    clientX: 200,
    clientY: 300
  })
  
  await page.waitForTimeout(500) // Wait for zoom animation
  
  // Verify chart is zoomed (check scale)
  const chartScale = await page.evaluate(() => {
    return window.chartInstance.scales.x.min
  })
  
  expect(chartScale).toBeGreaterThan(0) // Should be zoomed in
  
  // Pan (drag)
  await canvas.dragTo(canvas, {
    sourcePosition: { x: 200, y: 300 },
    targetPosition: { x: 100, y: 300 }
  })
  
  // Verify pan worked
  const newScale = await page.evaluate(() => {
    return window.chartInstance.scales.x.min
  })
  
  expect(newScale).not.toBe(chartScale)
})
```

### Legend Toggle (Show/Hide Series)

```typescript
test('toggling legend hides/shows data series', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Click legend item
  const legendItem = page.locator('[data-legend="Revenue"]')
  await legendItem.click()
  
  // Verify series is hidden
  const chartData = await page.evaluate(() => {
    return window.chartInstance.getDatasetMeta(0).hidden
  })
  
  expect(chartData).toBe(true)
  
  // Click again to show
  await legendItem.click()
  
  const chartDataVisible = await page.evaluate(() => {
    return window.chartInstance.getDatasetMeta(0).hidden
  })
  
  expect(chartDataVisible).toBe(false)
})
```

## Performance Testing

### Dashboard Load Time with Many Widgets

```typescript
// Performance test
test('dashboard loads within 5 seconds with 8 widgets', async ({ page }) => {
  const startTime = Date.now()
  
  await page.goto('/dashboard/complex')
  
  // Wait for all widgets to render
  await page.waitForSelector('[data-widget]:nth-child(8)')
  
  const loadTime = Date.now() - startTime
  
  expect(loadTime).toBeLessThan(5000)
  
  // Verify all charts are rendered
  const charts = await page.locator('canvas').count()
  expect(charts).toBe(8)
})
```

### Chart Render Time with 10K+ Data Points

```typescript
test('chart renders 10K points within 2 seconds', async ({ page }) => {
  await page.goto('/dashboard/large-dataset')
  
  const startTime = Date.now()
  
  // Wait for chart to render
  await page.waitForSelector('canvas', { state: 'visible' })
  
  const renderTime = Date.now() - startTime
  
  expect(renderTime).toBeLessThan(2000)
  
  // Verify data points are rendered (check chart instance)
  const dataPointCount = await page.evaluate(() => {
    return window.chartInstance.data.datasets[0].data.length
  })
  
  expect(dataPointCount).toBeGreaterThanOrEqual(10000)
})
```

## Accessibility Testing

### Chart Alt Text

```typescript
test('chart has descriptive alt text', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  const chart = page.locator('canvas[role="img"]')
  const ariaLabel = await chart.getAttribute('aria-label')
  
  expect(ariaLabel).toContain('Revenue chart')
  expect(ariaLabel).toContain('January 2025')
})
```

### Keyboard Navigation of Data Points

```typescript
test('keyboard navigation works for chart data points', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Focus chart
  const chart = page.locator('canvas[role="img"]')
  await chart.focus()
  
  // Navigate with arrow keys
  await page.keyboard.press('ArrowRight')
  
  // Verify focus moved to next data point
  const focusedPoint = await page.evaluate(() => {
    return document.activeElement?.getAttribute('aria-label')
  })
  
  expect(focusedPoint).toContain('2025-01-02')
})
```

### Color Contrast in Charts

```typescript
test('chart colors meet WCAG contrast requirements', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Get chart colors
  const colors = await page.evaluate(() => {
    const chart = window.chartInstance
    return chart.data.datasets.map(d => d.borderColor)
  })
  
  // Verify contrast ratios (using a11y library)
  colors.forEach(color => {
    const contrast = getContrastRatio(color, '#ffffff')
    expect(contrast).toBeGreaterThanOrEqual(4.5) // WCAG AA
  })
})
```

### Screen Reader Data Table Alternative

```typescript
test('chart has data table alternative for screen readers', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  
  // Verify table exists
  const dataTable = page.locator('[role="table"][aria-label="Chart data table"]')
  await expect(dataTable).toBeVisible()
  
  // Verify table has correct data
  const rows = dataTable.locator('tr')
  await expect(rows).toHaveCount(31) // 31 days in January
  
  // Verify first row
  const firstRow = rows.first()
  await expect(firstRow.locator('td').first()).toContainText('2025-01-01')
  await expect(firstRow.locator('td').last()).toContainText('$1,000')
})
```

## QA and Test Engineer Perspective

### Visual Regression Testing

**Purpose:** Ensure chart rendering doesn't change unexpectedly after code updates.

**Tools:** Percy, Chromatic, or Playwright Visual Comparisons

```typescript
test('chart visual regression', async ({ page }) => {
  await page.goto('/dashboard/revenue')
  await page.waitForSelector('canvas')
  
  // Take screenshot and compare to baseline
  await expect(page.locator('canvas')).toHaveScreenshot('revenue-chart.png')
})
```

**Test Scenarios:**
- Chart renders identically across browsers (Chrome, Firefox, Safari)
- Chart scales correctly at different viewport sizes
- Colors match design system specifications
- Fonts and labels render correctly

### Data Accuracy Validation

**Purpose:** Verify that displayed chart data matches source database data.

**Approach:**
1. Query database directly for expected values
2. Extract data from chart (via API or DOM)
3. Compare values with tolerance for rounding

```typescript
test('chart data matches database', async ({ page, db }) => {
  // Query database
  const dbData = await db.query(`
    SELECT date, SUM(amount) as revenue
    FROM transactions
    WHERE date BETWEEN '2025-01-01' AND '2025-01-31'
    GROUP BY date
    ORDER BY date
  `)
  
  // Load dashboard
  await page.goto('/dashboard/revenue?startDate=2025-01-01&endDate=2025-01-31')
  
  // Extract chart data
  const chartData = await page.evaluate(() => {
    return window.chartInstance.data.datasets[0].data
  })
  
  // Compare (allow for rounding differences)
  dbData.forEach((row, index) => {
    expect(Math.abs(chartData[index] - row.revenue)).toBeLessThan(0.01)
  })
})
```

### Cross-Browser Compatibility

**Purpose:** Ensure charts work consistently across all supported browsers.

**Test Matrix:**
- Chrome (latest, latest-1)
- Firefox (latest, latest-1)
- Safari (latest)
- Edge (latest)

**Key Areas:**
- Canvas rendering (Chart.js)
- SVG rendering (Recharts, D3)
- CSS Grid layout for dashboards
- Touch events on mobile browsers

### Export Functionality Testing

**Purpose:** Verify exports generate correct files with accurate data.

**Test Cases:**
- PDF export contains all dashboard widgets
- CSV export includes all columns and rows
- Excel export has proper formatting (currency, dates)
- Large exports (>10K rows) complete without timeout
- Export respects current filters and date range
- Export file downloads successfully

```typescript
test('export respects dashboard filters', async ({ page }) => {
  // Set filters
  await page.selectOption('[data-testid="region-filter"]', 'North America')
  await page.fill('[data-testid="date-start"]', '2025-01-01')
  await page.fill('[data-testid="date-end"]', '2025-01-31')
  
  // Export
  await page.click('button[aria-label="Export"]')
  const download = await page.waitForEvent('download')
  const csv = await download.text()
  
  // Verify exported data matches filtered view
  const rows = csv.split('\n').slice(1)
  rows.forEach(row => {
    const [date, region] = row.split(',')
    expect(region).toBe('North America')
    expect(new Date(date) >= new Date('2025-01-01')).toBe(true)
    expect(new Date(date) <= new Date('2025-01-31')).toBe(true)
  })
})
```

### Performance Benchmarking

**Purpose:** Establish performance baselines and catch regressions.

**Metrics to Track:**
- Time to first chart render (TTFCR)
- Dashboard load time (all widgets)
- Chart interaction responsiveness (hover, click)
- Export generation time
- Memory usage with long-running dashboards

```typescript
test('dashboard performance benchmark', async ({ page }) => {
  const metrics = {
    navigationStart: 0,
    firstChartRender: 0,
    dashboardInteractive: 0
  }
  
  await page.goto('/dashboard/complex')
  
  // Track performance
  const perfData = await page.evaluate(() => {
    const perf = performance.getEntriesByType('navigation')[0]
    return {
      domContentLoaded: perf.domContentLoadedEventEnd - perf.fetchStart,
      loadComplete: perf.loadEventEnd - perf.fetchStart
    }
  })
  
  // Wait for first chart
  await page.waitForSelector('canvas', { state: 'visible' })
  metrics.firstChartRender = Date.now()
  
  // Wait for all widgets
  await page.waitForSelector('[data-widget]:last-child')
  metrics.dashboardInteractive = Date.now()
  
  // Assert performance thresholds
  expect(perfData.domContentLoaded).toBeLessThan(2000)
  expect(metrics.dashboardInteractive - metrics.navigationStart).toBeLessThan(5000)
})
```

### Error Handling and Edge Cases

**Purpose:** Verify graceful handling of error states and edge cases.

**Test Scenarios:**
- Empty data sets (no data for date range)
- API errors (network failure, 500 error)
- Malformed data (null values, invalid dates)
- Extremely large datasets (100K+ points)
- Concurrent user interactions (rapid filter changes)
- Browser tab backgrounding (pause updates)

```typescript
test('handles API error gracefully', async ({ page }) => {
  // Mock API failure
  await page.route('/api/charts/revenue', route => route.abort())
  
  await page.goto('/dashboard/revenue')
  
  // Verify error state displayed
  await expect(page.locator('.error-state')).toBeVisible()
  await expect(page.locator('.error-state')).toContainText('Failed to load chart data')
  
  // Verify retry button works
  await page.click('button[aria-label="Retry"]')
  await page.waitForSelector('canvas', { timeout: 5000 })
})
```
