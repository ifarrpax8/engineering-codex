# Gotchas: Data Visualization

## Contents

- [Pie Charts with Too Many Slices](#pie-charts-with-too-many-slices)
- [Y-Axis Not Starting at Zero](#y-axis-not-starting-at-zero)
- [Charts Re-rendering on Every State Change](#charts-re-rendering-on-every-state-change)
- [Client-Side Aggregation Blocking Main Thread](#client-side-aggregation-blocking-main-thread)
- [Color Palettes Not Colorblind-Safe](#color-palettes-not-colorblind-safe)
- [Export Generating Different Data Than Displayed](#export-generating-different-data-than-displayed)
- [Real-Time Chart Memory Leaks](#real-time-chart-memory-leaks)
- [API Storm from Widget Mounting](#api-storm-from-widget-mounting)
- [Responsive Charts Not Resizing Properly](#responsive-charts-not-resizing-properly)
- [Time Zone Mismatches](#time-zone-mismatches)
- [Tooltip Obscuring Data Points](#tooltip-obscuring-data-points)

## Pie Charts with Too Many Slices

**Problem:** Pie charts become unreadable with more than 5-6 slices. Users can't distinguish between similar-sized segments.

**Symptoms:**
- Chart looks like a rainbow-colored circle
- Legend has 10+ items
- Users can't identify which slice is which

**Solution:** Use a bar chart instead for 7+ categories.

```typescript
// ❌ BAD: Pie chart with 12 slices
const pieData = {
  labels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'],
  datasets: [{ data: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0.5, 0.5] }]
}

// ✅ GOOD: Bar chart for many categories
const barData = {
  labels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'],
  datasets: [{
    label: 'Revenue',
    data: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0.5, 0.5]
  }]
}
```

**Prevention:** Enforce maximum slice count in chart configuration:

```typescript
function validatePieChartData(data: PieChartData) {
  if (data.labels.length > 6) {
    throw new Error(
      `Pie charts should have maximum 6 slices. Use bar chart for ${data.labels.length} categories.`
    )
  }
}
```

## Y-Axis Not Starting at Zero

**Problem:** Truncating the Y-axis makes small changes look dramatic, misleading users about the magnitude of change.

**Example:**
- Revenue changes from $95,000 to $100,000 (5% increase)
- Chart with Y-axis from $90,000-$100,000 makes it look like a 50% increase

**Solution:** Always start Y-axis at zero unless there's a compelling reason:

```typescript
// ❌ BAD: Misleading truncation
const misleadingOptions = {
  scales: {
    y: {
      min: 90000, // Truncated!
      max: 100000
    }
  }
}

// ✅ GOOD: Start at zero
const accurateOptions = {
  scales: {
    y: {
      beginAtZero: true // Shows true scale
    }
  }
}

// ✅ ACCEPTABLE: User-controlled truncation with warning
const userControlledOptions = {
  scales: {
    y: {
      beginAtZero: userPreference.startAtZero,
      min: userPreference.startAtZero ? undefined : calculateMin()
    }
  },
  plugins: {
    annotation: {
      annotations: userPreference.startAtZero ? [] : [{
        type: 'line',
        yMin: 0,
        yMax: 0,
        borderColor: 'rgba(0,0,0,0.2)',
        borderDash: [5, 5],
        label: {
          content: 'Zero axis (hidden)',
          enabled: true
        }
      }]
    }
  }
}
```

## Charts Re-rendering on Every State Change

**Problem:** Chart components re-render unnecessarily when unrelated state changes, causing performance issues and flickering.

**Symptoms:**
- Chart flickers when typing in a search box
- Dashboard becomes slow with multiple charts
- Browser DevTools shows excessive chart updates

**Solution:** Memoize chart data and options:

```vue
<!-- Vue 3: Memoize chart data -->
<script setup lang="ts">
import { computed, shallowRef } from 'vue'

// Use shallowRef for chart instance (don't deep watch)
const chartInstance = shallowRef<Chart | null>(null)

// Memoize chart data (only recalculates when data changes)
const chartData = computed(() => {
  return {
    labels: props.data.map(d => d.date),
    datasets: [{
      data: props.data.map(d => d.value)
    }]
  }
})

// Memoize options (only recalculates when options change)
const chartOptions = computed(() => ({
  responsive: true,
  // ... options
}))
</script>
```

```tsx
// React: Memoize with useMemo
import { useMemo } from 'react'

export function RevenueChart({ data, dateRange }) {
  // Memoize chart data
  const chartData = useMemo(() => ({
    labels: data.map(d => d.date),
    datasets: [{
      data: data.map(d => d.value)
    }]
  }), [data]) // Only recalculate when data changes
  
  // Memoize options
  const chartOptions = useMemo(() => ({
    responsive: true,
    // ... options
  }), []) // Options never change
  
  return <Line data={chartData} options={chartOptions} />
}
```

**Prevention:** Use React.memo or Vue's defineComponent with proper prop comparison:

```tsx
// React: Memoize component
export const RevenueChart = React.memo(function RevenueChart({ data }) {
  // Component implementation
}, (prevProps, nextProps) => {
  // Only re-render if data actually changed
  return prevProps.data === nextProps.data
})
```

## Client-Side Aggregation Blocking Main Thread

**Problem:** Aggregating 100K+ rows in JavaScript blocks the UI thread, making the page unresponsive.

**Symptoms:**
- Page freezes for several seconds
- Browser shows "Page unresponsive" warning
- Users can't interact with the page

**Solution:** Use WebWorker for client-side aggregation or move to server-side:

```typescript
// ❌ BAD: Blocking main thread
function aggregateData(rawData: DataPoint[]) {
  const aggregated = []
  for (let i = 0; i < rawData.length; i += 10) {
    const bucket = rawData.slice(i, i + 10)
    const avg = bucket.reduce((sum, d) => sum + d.value, 0) / bucket.length
    aggregated.push({ date: bucket[0].date, value: avg })
  }
  return aggregated // Blocks UI for 100K rows!
}

// ✅ GOOD: WebWorker for aggregation
// aggregator.worker.ts
self.onmessage = function(e) {
  const { data, bucketSize } = e.data
  const aggregated = []
  
  for (let i = 0; i < data.length; i += bucketSize) {
    const bucket = data.slice(i, i + bucketSize)
    const avg = bucket.reduce((sum, d) => sum + d.value, 0) / bucket.length
    aggregated.push({ date: bucket[0].date, value: avg })
  }
  
  self.postMessage(aggregated)
}

// Main thread
const worker = new Worker('/aggregator.worker.ts')
worker.postMessage({ data: rawData, bucketSize: 10 })
worker.onmessage = (e) => {
  chartData.value = e.data // Non-blocking!
}
```

**Better Solution:** Server-side aggregation (preferred):

```kotlin
// Spring Boot: Aggregate in SQL
@Query("""
    SELECT 
        DATE_TRUNC('day', created_at) as date,
        AVG(value) as avg_value
    FROM data_points
    WHERE created_at BETWEEN :start AND :end
    GROUP BY DATE_TRUNC('day', created_at)
    ORDER BY date
""", nativeQuery = true)
fun getAggregatedData(start: LocalDateTime, end: LocalDateTime): List<AggregatedData>
```

## Color Palettes Not Colorblind-Safe

**Problem:** 8% of men are red-green colorblind. Using red/green to distinguish data makes charts unusable for these users.

**Symptoms:**
- Users report they can't distinguish chart series
- Red and green series look identical
- Accessibility audits fail

**Solution:** Use colorblind-safe palettes:

```typescript
// ❌ BAD: Red-green palette
const problematicColors = ['#ff0000', '#00ff00', '#0000ff']

// ✅ GOOD: Colorblind-safe palette
const colorblindSafeColors = [
  '#1f77b4', // Blue
  '#ff7f0e', // Orange
  '#2ca02c', // Green (but distinguishable)
  '#d62728', // Red (with shape differentiation)
  '#9467bd', // Purple
  '#8c564b', // Brown
]

// Use established palettes
import { schemeCategory10 } from 'd3-scale-chromatic'
const safePalette = schemeCategory10 // Pre-tested for colorblind accessibility
```

**Additional Solution:** Combine color with patterns/shapes:

```typescript
const chartOptions = {
  datasets: [
    {
      borderColor: '#3b82f6',
      borderDash: [], // Solid line
      pointStyle: 'circle'
    },
    {
      borderColor: '#10b981', // Green, but also different shape
      borderDash: [5, 5], // Dashed line
      pointStyle: 'square' // Different point shape
    }
  ]
}
```

## Export Generating Different Data Than Displayed

**Problem:** Export uses different filters/date range than what's displayed on the dashboard, confusing users.

**Symptoms:**
- User filters dashboard to "North America"
- Exports CSV
- CSV contains data from all regions
- User reports bug

**Solution:** Pass current filter state to export endpoint:

```typescript
// ❌ BAD: Export doesn't use filters
async function exportDashboard() {
  const response = await fetch('/api/export/dashboard')
  // Missing filters!
}

// ✅ GOOD: Include all current state in export
async function exportDashboard(
  dashboardId: string,
  dateRange: DateRange,
  filters: Record<string, any>
) {
  const params = new URLSearchParams({
    dashboardId,
    startDate: dateRange.start,
    endDate: dateRange.end,
    ...Object.entries(filters).reduce((acc, [key, value]) => {
      acc[key] = String(value)
      return acc
    }, {} as Record<string, string>)
  })
  
  const response = await fetch(`/api/export/dashboard?${params}`)
  return response.blob()
}
```

```kotlin
// Spring Boot: Accept filters in export endpoint
@GetMapping("/export/dashboard")
fun exportDashboard(
    @RequestParam dashboardId: String,
    @RequestParam startDate: LocalDate,
    @RequestParam endDate: LocalDate,
    @RequestParam(required = false) region: String?,
    @RequestParam(required = false) productId: String?
): ResponseEntity<ByteArray> {
    // Apply filters to export query
    val data = dashboardService.getDashboardData(
        dashboardId = dashboardId,
        dateRange = DateRange(startDate, endDate),
        filters = DashboardFilters(region = region, productId = productId)
    )
    
    return ResponseEntity.ok(exportService.generatePDF(data))
}
```

## Real-Time Chart Memory Leaks

**Problem:** Real-time charts accumulate data points without cleanup, causing memory leaks over hours of viewing.

**Symptoms:**
- Browser memory usage grows continuously
- Chart becomes slow after hours
- Browser eventually crashes

**Solution:** Implement data point limits and cleanup:

```typescript
// ❌ BAD: Accumulating data forever
function appendDataPoint(chart: Chart, newPoint: DataPoint) {
  chart.data.labels.push(newPoint.date)
  chart.data.datasets[0].data.push(newPoint.value)
  chart.update() // Keeps growing!
}

// ✅ GOOD: Limit data points and cleanup
function appendDataPoint(chart: Chart, newPoint: DataPoint) {
  const maxPoints = 1000
  
  chart.data.labels.push(newPoint.date)
  chart.data.datasets[0].data.push(newPoint.value)
  
  // Remove old points if over limit
  if (chart.data.labels.length > maxPoints) {
    chart.data.labels.shift()
    chart.data.datasets[0].data.shift()
  }
  
  chart.update('none') // 'none' mode for performance
}

// For WebSocket connections, also cleanup subscriptions
onUnmounted(() => {
  if (stompClient.value) {
    stompClient.value.deactivate()
    stompClient.value = null
  }
})
```

## API Storm from Widget Mounting

**Problem:** All dashboard widgets fetch data simultaneously on mount, overwhelming the API server.

**Symptoms:**
- 8 widgets = 8 simultaneous API requests
- API server rate limiting kicks in
- Some widgets fail to load
- Dashboard load time increases

**Solution:** Stagger or batch widget requests:

```typescript
// ❌ BAD: All widgets fetch at once
function Dashboard({ widgets }) {
  useEffect(() => {
    widgets.forEach(widget => {
      fetchWidgetData(widget.id) // All at once!
    })
  }, [])
}

// ✅ GOOD: Stagger requests
function Dashboard({ widgets }) {
  useEffect(() => {
    widgets.forEach((widget, index) => {
      // Stagger by 100ms
      setTimeout(() => {
        fetchWidgetData(widget.id)
      }, index * 100)
    })
  }, [])
}

// ✅ BETTER: Batch requests
async function fetchAllWidgets(widgets: Widget[]) {
  // Single request for all widget data
  const response = await fetch('/api/dashboard/widgets', {
    method: 'POST',
    body: JSON.stringify({ widgetIds: widgets.map(w => w.id) })
  })
  const data = await response.json()
  
  // Distribute data to widgets
  widgets.forEach(widget => {
    widgetData[widget.id] = data[widget.id]
  })
}
```

```kotlin
// Spring Boot: Batch endpoint
@PostMapping("/dashboard/widgets")
fun getWidgetsData(
    @RequestBody request: WidgetsDataRequest
): ResponseEntity<Map<String, WidgetDataDto>> {
    val widgetData = request.widgetIds.associateWith { widgetId ->
        widgetService.getWidgetData(widgetId, request.dateRange, request.filters)
    }
    return ResponseEntity.ok(widgetData)
}
```

## Responsive Charts Not Resizing Properly

**Problem:** Charts don't resize when viewport changes, or resize incorrectly, causing layout issues.

**Symptoms:**
- Chart overflows container on mobile
- Chart doesn't fill container after window resize
- Dashboard layout breaks on orientation change

**Solution:** Use ResizeObserver and Chart.js responsive option:

```typescript
// ❌ BAD: No resize handling
const chartOptions = {
  responsive: false // Chart doesn't resize!
}

// ✅ GOOD: Proper responsive configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false, // Allow height to change
  onResize: (chart, size) => {
    // Custom resize logic if needed
  }
}

// Vue 3: ResizeObserver for container
import { ref, onMounted, onUnmounted } from 'vue'

export function useResponsiveChart(chartRef: Ref<Chart | null>) {
  const containerRef = ref<HTMLElement | null>(null)
  let resizeObserver: ResizeObserver | null = null

  onMounted(() => {
    if (containerRef.value && chartRef.value) {
      resizeObserver = new ResizeObserver(() => {
        chartRef.value?.resize()
      })
      resizeObserver.observe(containerRef.value)
    }
  })

  onUnmounted(() => {
    resizeObserver?.disconnect()
  })

  return { containerRef }
}
```

```tsx
// React: Handle window resize
import { useEffect, useRef } from 'react'

export function ResponsiveChart({ data }) {
  const chartRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    const handleResize = () => {
      // Chart.js automatically resizes if responsive: true
      // But you may need to manually trigger for other libraries
      if (chartInstance.current) {
        chartInstance.current.resize()
      }
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  
  return <div ref={chartRef}><Chart data={data} /></div>
}
```

## Time Zone Mismatches

**Problem:** Chart shows UTC time but user expects local time, or vice versa, causing confusion.

**Symptoms:**
- User selects "January 1" but chart shows data from "December 31"
- Data points appear at wrong times
- Exports have different timestamps than displayed

**Solution:** Consistently handle timezones:

```typescript
// ❌ BAD: Mixing UTC and local time
const chartData = data.map(d => ({
  date: d.createdAt.toISOString(), // UTC string
  value: d.value
}))
// But user expects local time!

// ✅ GOOD: Convert to user's timezone
function formatDateForChart(date: Date, userTimezone: string) {
  return formatInTimeZone(date, userTimezone, 'yyyy-MM-dd HH:mm')
}

// Or use date-fns-tz
import { format, utcToZonedTime } from 'date-fns-tz'

const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
const chartData = data.map(d => ({
  date: format(
    utcToZonedTime(d.createdAt, userTimezone),
    'yyyy-MM-dd',
    { timeZone: userTimezone }
  ),
  value: d.value
}))
```

```kotlin
// Spring Boot: Return timezone-aware dates
data class ChartDataPoint(
    val date: LocalDateTime,
    val value: BigDecimal
) {
    fun toDto(userTimezone: ZoneId): ChartDataPointDto {
        val zonedDate = date.atZone(ZoneId.of("UTC"))
            .withZoneSameInstant(userTimezone)
        
        return ChartDataPointDto(
            date = zonedDate.toLocalDateTime(),
            value = value
        )
    }
}
```

## Tooltip Obscuring Data Points

**Problem:** Tooltip appears on top of the data point it's describing, making it hard to see the actual value.

**Symptoms:**
- Tooltip covers the data point
- User can't see the point while reading tooltip
- Poor UX on mobile

**Solution:** Position tooltip away from data point:

```typescript
// Chart.js: Custom tooltip positioning
const chartOptions = {
  plugins: {
    tooltip: {
      position: 'nearest', // Or 'average', 'nearest'
      caretPadding: 10, // Space between point and tooltip
      displayColors: true,
      callbacks: {
        title: (items) => {
          return items[0].label
        },
        label: (context) => {
          return `Value: ${context.parsed.y}`
        }
      }
    }
  },
  interaction: {
    intersect: false, // Show tooltip even if not directly over point
    mode: 'index' // Show tooltip for nearest point
  }
}

// Custom tooltip positioning function
const chartOptions = {
  plugins: {
    tooltip: {
      external: (context) => {
        // Custom tooltip positioning logic
        const { chart, tooltip } = context
        const position = chart.canvas.getBoundingClientRect()
        
        // Position tooltip above/below point, not on top
        tooltip.x = position.left + tooltip.caretX
        tooltip.y = position.top + tooltip.caretY - 50 // Offset above point
      }
    }
  }
}
```

```css
/* CSS: Ensure tooltip doesn't cover point */
.chartjs-tooltip {
  pointer-events: none; /* Allow clicks through tooltip */
  z-index: 1000;
  position: absolute;
  transform: translate(-50%, -100%); /* Position above point */
  margin-top: -10px; /* Additional spacing */
}
```
