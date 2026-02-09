# Best Practices: Data Visualization

## Contents

- [Choose the Right Chart Type](#choose-the-right-chart-type)
- [Always Provide Context](#always-provide-context)
- [Don't Truncate Y-Axis to Zero](#dont-truncate-y-axis-to-zero)
- [Provide Data Table Alternative](#provide-data-table-alternative)
- [Loading States](#loading-states)
- [Empty States](#empty-states)
- [Color Best Practices](#color-best-practices)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Dashboard UX](#dashboard-ux)
- [Mobile Considerations](#mobile-considerations)

## Choose the Right Chart Type

### Bar Charts for Comparison

Use bar charts when comparing discrete categories or showing rankings:

```vue
<!-- Vue 3: Bar chart for product comparison -->
<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
const chartData = computed(() => ({
  labels: ['Product A', 'Product B', 'Product C'],
  datasets: [{
    label: 'Revenue',
    data: [50000, 75000, 60000],
    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b']
  }]
}))
</script>
```

**When to use:**
- Comparing 2-10 categories
- Showing rankings (top 10 customers)
- Part-to-whole with few segments

**Avoid when:**
- You have 15+ categories (use horizontal bar or group)
- Data is time-series (use line chart)

### Line Charts for Trends Over Time

Line charts excel at showing trends and continuous data:

```tsx
// React: Line chart for revenue trend
<LineChart data={revenueData}>
  <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
  <XAxis dataKey="date" />
  <YAxis />
</LineChart>
```

**When to use:**
- Time-series data (daily, weekly, monthly)
- Multiple series comparisons (revenue vs users)
- Showing trends and patterns

**Avoid when:**
- Data points are not sequential
- You need precise value comparisons (bar charts are clearer)

### Pie Charts Only for Parts-of-Whole with Few Categories

**Rule of thumb: Maximum 5-6 slices**

```typescript
// Only use pie charts for 5-6 or fewer categories
const pieData = {
  labels: ['Product A', 'Product B', 'Product C', 'Product D'],
  datasets: [{
    data: [40, 30, 20, 10] // 4 categories - OK
  }]
}

// If you have more, use bar chart instead
const tooManyCategories = {
  labels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'], // 10 categories - use bar!
  datasets: [{
    data: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
  }]
}
```

**When to use:**
- 3-6 categories maximum
- Showing parts of a whole
- Percentages sum to 100%

**Avoid when:**
- More than 6 slices (use bar chart)
- Values are very similar (hard to distinguish slices)
- You need precise comparisons

## Always Provide Context

Every chart needs context for interpretation:

### Title, Axis Labels, Units

```vue
<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
const chartOptions = computed(() => ({
  plugins: {
    title: {
      display: true,
      text: 'Monthly Revenue Trend', // Clear title
      font: { size: 16, weight: 'bold' }
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          return `Revenue: $${context.parsed.y.toLocaleString()}` // Units in tooltip
        }
      }
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Month' // X-axis label
      }
    },
    y: {
      title: {
        display: true,
        text: 'Revenue (USD)' // Y-axis label with units
      },
      ticks: {
        callback: (value: any) => `$${value.toLocaleString()}` // Units on axis
      }
    }
  }
}))
</script>
```

### Date Range Display

Always show the selected date range prominently:

```tsx
// React: Date range display
function DashboardHeader({ dateRange, onDateRangeChange }) {
  return (
    <div className="dashboard-header">
      <h1>Revenue Dashboard</h1>
      <DateRangePicker
        value={dateRange}
        onChange={onDateRangeChange}
      />
      <div className="date-range-display">
        {format(dateRange.start, 'MMM d, yyyy')} - {format(dateRange.end, 'MMM d, yyyy')}
      </div>
    </div>
  )
}
```

### Comparison Period Indicator

When showing comparisons, clearly indicate what's being compared:

```typescript
// Show comparison context
const chartOptions = {
  plugins: {
    subtitle: {
      display: true,
      text: 'Compared to previous period (Jan 1-31, 2024)',
      font: { size: 12 }
    }
  },
  datasets: [
    {
      label: 'Current Period',
      borderColor: '#3b82f6',
      data: currentPeriodData
    },
    {
      label: 'Previous Period',
      borderColor: '#94a3b8',
      borderDash: [5, 5], // Dashed line for comparison
      data: previousPeriodData
    }
  ]
}
```

## Don't Truncate Y-Axis to Zero

**Default: Always start Y-axis at zero** unless there's a compelling reason not to.

### Why Starting at Zero Matters

Truncating the Y-axis can be misleading:

```typescript
// ❌ BAD: Y-axis starts at 90, making 5% change look like 50% change
const misleadingOptions = {
  scales: {
    y: {
      min: 90, // Truncated!
      max: 100
    }
  }
}

// ✅ GOOD: Y-axis starts at 0, showing true magnitude
const accurateOptions = {
  scales: {
    y: {
      beginAtZero: true // Shows true scale
    }
  }
}
```

### When Truncation is Acceptable

Only truncate when:
- **Small variations matter** — e.g., stock prices where $0.50 change is significant
- **Data is far from zero** — e.g., temperature readings (50-60°F range)
- **User explicitly requests it** — Provide toggle: "Start Y-axis at zero" checkbox

```typescript
// Allow user control
const chartOptions = computed(() => ({
  scales: {
    y: {
      beginAtZero: props.startAtZero, // User preference
      min: props.startAtZero ? undefined : calculateDataMin()
    }
  }
}))
```

## Provide Data Table Alternative

**Every chart must have a data table fallback** for accessibility and data export.

### Implementation Pattern

```vue
<!-- Vue 3: Chart with data table -->
<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
    
    <!-- Hidden table for screen readers -->
    <table 
      class="sr-only" 
      role="table" 
      aria-label="Revenue data table"
    >
      <thead>
        <tr>
          <th>Date</th>
          <th>Revenue</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="point in data" :key="point.date">
          <td>{{ point.date }}</td>
          <td>${{ point.revenue.toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>
    
    <!-- Visible table toggle -->
    <button @click="showTable = !showTable">
      {{ showTable ? 'Hide' : 'Show' }} Data Table
    </button>
    
    <table v-if="showTable" class="data-table">
      <!-- Same table content, visible -->
    </table>
  </div>
</template>
```

### Screen Reader Optimization

```html
<!-- Proper ARIA attributes -->
<canvas 
  role="img"
  :aria-label="`Revenue chart showing ${data.length} data points from ${dateRange.start} to ${dateRange.end}`"
></canvas>

<!-- Linked table -->
<table 
  id="chart-data-table"
  aria-label="Data table for revenue chart"
>
  <!-- Table content -->
</table>
```

## Loading States

### Skeleton Chart Shapes

Use skeleton loaders that match the chart shape, not generic spinners:

```vue
<!-- Vue 3: Chart skeleton -->
<template>
  <div v-if="loading" class="chart-skeleton">
    <div class="skeleton-axis skeleton-x"></div>
    <div class="skeleton-axis skeleton-y"></div>
    <div class="skeleton-bars">
      <div 
        v-for="i in 12" 
        :key="i" 
        class="skeleton-bar"
        :style="{ height: `${Math.random() * 60 + 20}%` }"
      ></div>
    </div>
  </div>
  <Line v-else :data="chartData" :options="chartOptions" />
</template>

<style scoped>
.chart-skeleton {
  display: flex;
  flex-direction: column;
  height: 400px;
  padding: 20px;
}

.skeleton-bars {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  flex: 1;
}

.skeleton-bar {
  flex: 1;
  background: linear-gradient(
    90deg,
    #e2e8f0 0%,
    #cbd5e1 50%,
    #e2e8f0 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px 4px 0 0;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
```

```tsx
// React: Chart skeleton component
export function ChartSkeleton({ type = 'line' }) {
  if (type === 'bar') {
    return (
      <div className="chart-skeleton">
        <div className="skeleton-bars">
          {Array.from({ length: 8 }).map((_, i) => (
            <div 
              key={i}
              className="skeleton-bar"
              style={{ height: `${Math.random() * 60 + 20}%` }}
            />
          ))}
        </div>
      </div>
    )
  }
  
  // Line chart skeleton
  return (
    <div className="chart-skeleton">
      <svg viewBox="0 0 400 200">
        <path
          d="M 0,150 Q 100,100 200,80 T 400,50"
          stroke="#e2e8f0"
          strokeWidth="2"
          fill="none"
        />
      </svg>
    </div>
  )
}
```

## Empty States

### Meaningful Empty State Messages

```vue
<!-- Vue 3: Empty state component -->
<template>
  <div v-if="!loading && data.length === 0" class="empty-state">
    <EmptyChartIcon />
    <h3>No data for this period</h3>
    <p>There's no revenue data between {{ dateRange.start }} and {{ dateRange.end }}.</p>
    <div class="empty-state-actions">
      <button @click="expandDateRange">Expand Date Range</button>
      <button @click="clearFilters">Clear Filters</button>
    </div>
  </div>
</template>
```

**Empty state should:**
- Explain why there's no data
- Suggest actions (change date range, clear filters)
- Not look like an error (use neutral/informative tone)

## Color Best Practices

### Colorblind-Safe Palettes

**8% of men are red-green colorblind.** Use palettes that work for everyone:

```typescript
// ✅ GOOD: Colorblind-safe palette
const colorblindSafePalette = [
  '#1f77b4', // Blue
  '#ff7f0e', // Orange
  '#2ca02c', // Green (but distinguishable)
  '#d62728', // Red (but with shape differentiation)
  '#9467bd', // Purple
  '#8c564b', // Brown
  '#e377c2', // Pink
  '#7f7f7f'  // Gray
]

// ❌ BAD: Red-green palette (problematic for colorblind users)
const problematicPalette = [
  '#ff0000', // Red
  '#00ff00', // Green - looks similar to red for colorblind users
  '#0000ff'  // Blue
]
```

### Consistent Color-to-Category Mapping

Use the same color for the same category across all charts:

```typescript
// Color mapping service
export const categoryColors = {
  'Product A': '#3b82f6', // Always blue
  'Product B': '#10b981', // Always green
  'Product C': '#f59e0b'  // Always orange
}

// Use across all charts
const chartData = {
  datasets: [{
    label: 'Product A',
    backgroundColor: categoryColors['Product A'], // Consistent!
    data: productAData
  }]
}
```

### Don't Rely Solely on Color

Use patterns, shapes, or labels in addition to color:

```typescript
// Combine color with pattern
const chartOptions = {
  datasets: [
    {
      label: 'Revenue',
      borderColor: '#3b82f6',
      backgroundColor: '#3b82f6',
      borderDash: [] // Solid line
    },
    {
      label: 'Target',
      borderColor: '#94a3b8',
      backgroundColor: '#94a3b8',
      borderDash: [5, 5] // Dashed line (works even in grayscale)
    }
  ]
}
```

## Stack-Specific Guidance

### Vue 3

**Chart.js with vue-chartjs:**

```vue
<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { ref, computed, watch } from 'vue'

// Reactive data binding
const apiData = ref<any[]>([])
const loading = ref(false)

const chartData = computed(() => ({
  labels: apiData.value.map(d => d.date),
  datasets: [{
    label: 'Revenue',
    data: apiData.value.map(d => d.value)
  }]
}))

// Watch for data changes and update chart
watch(apiData, () => {
  // Chart automatically updates via reactive data
}, { deep: true })
</script>
```

**Composable for chart options:**

```typescript
// composables/useChartOptions.ts
import { computed, type Ref } from 'vue'

export function useChartOptions(
  title: string,
  currency: boolean = false
) {
  return computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: { display: true, text: title },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.parsed.y
            return currency 
              ? `$${value.toLocaleString()}` 
              : value.toLocaleString()
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value: any) => {
            return currency 
              ? `$${value.toLocaleString()}` 
              : value.toLocaleString()
          }
        }
      }
    }
  }))
}
```

### React

**Recharts for simple charts:**

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'

export function RevenueChart({ data }) {
  return (
    <LineChart data={data} width={800} height={400}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
    </LineChart>
  )
}
```

**Victory for mid-complexity:**

```tsx
import { VictoryChart, VictoryLine, VictoryAxis } from 'victory'

export function ComplexChart({ data }) {
  return (
    <VictoryChart>
      <VictoryAxis />
      <VictoryAxis dependentAxis />
      <VictoryLine data={data} />
    </VictoryChart>
  )
}
```

**D3.js for custom visualizations:**

```tsx
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export function CustomChart({ data }) {
  const svgRef = useRef<SVGSVGElement>(null)
  
  useEffect(() => {
    if (!svgRef.current) return
    
    const svg = d3.select(svgRef.current)
    // Custom D3 implementation
    // ...
  }, [data])
  
  return <svg ref={svgRef} />
}
```

### Spring Boot

**Aggregation endpoints:**

```kotlin
@RestController
@RequestMapping("/api/charts")
class ChartDataController {
    
    @GetMapping("/revenue")
    fun getRevenueData(
        @RequestParam startDate: LocalDate,
        @RequestParam endDate: LocalDate
    ): ResponseEntity<ChartDataDto> {
        // Server-side aggregation
        val data = revenueRepository.getDailyRevenue(startDate, endDate)
        return ResponseEntity.ok(ChartDataDto.from(data))
    }
}
```

**Caching expensive queries:**

```kotlin
@Service
class ChartDataService {
    
    @Cacheable(
        value = ["chartData"],
        key = "#startDate.toString() + '-' + #endDate.toString()"
    )
    fun getRevenueData(startDate: LocalDate, endDate: LocalDate): List<DailyRevenueDto> {
        // Expensive aggregation query
        return revenueRepository.getDailyRevenue(startDate, endDate)
    }
}
```

**Async export service:**

```kotlin
@Service
class ExportService {
    
    @Async
    fun generateExport(jobId: String) {
        // Long-running export generation
        val pdf = pdfGenerator.generate(dashboardId)
        storageService.upload(pdf, jobId)
        notificationService.notifyComplete(jobId)
    }
}
```

## Dashboard UX

### Limit Widgets Per View

**Best practice: 6-8 widgets maximum per dashboard view**

```typescript
// Enforce widget limit
function addWidget(dashboard: Dashboard, widget: Widget) {
  if (dashboard.widgets.length >= 8) {
    throw new Error('Maximum 8 widgets per dashboard')
  }
  dashboard.widgets.push(widget)
}
```

### KPI Cards at Top

Place most important metrics at the top:

```vue
<template>
  <div class="dashboard">
    <!-- KPIs at top -->
    <div class="kpi-row">
      <KPICard 
        v-for="kpi in kpis" 
        :key="kpi.id"
        :kpi="kpi"
      />
    </div>
    
    <!-- Supporting charts below -->
    <div class="charts-grid">
      <ChartWidget 
        v-for="chart in charts"
        :key="chart.id"
        :chart="chart"
      />
    </div>
  </div>
</template>
```

### User Customization

Allow users to customize and rearrange:

```typescript
// Save user preferences
interface DashboardPreferences {
  widgetOrder: string[]
  widgetPositions: Record<string, { x: number; y: number }>
  hiddenWidgets: string[]
}

function saveDashboardPreferences(
  userId: string,
  dashboardId: string,
  preferences: DashboardPreferences
) {
  localStorage.setItem(
    `dashboard-${dashboardId}-prefs`,
    JSON.stringify(preferences)
  )
  
  // Also save to backend
  api.savePreferences(userId, dashboardId, preferences)
}
```

### Remember User Preferences

```typescript
// Load saved preferences on mount
function useDashboardPreferences(dashboardId: string) {
  const preferences = ref<DashboardPreferences | null>(null)
  
  onMounted(async () => {
    // Try localStorage first (fast)
    const cached = localStorage.getItem(`dashboard-${dashboardId}-prefs`)
    if (cached) {
      preferences.value = JSON.parse(cached)
    }
    
    // Then fetch from backend (authoritative)
    const serverPrefs = await api.getPreferences(dashboardId)
    preferences.value = serverPrefs
  })
  
  return preferences
}
```

## Mobile Considerations

### Simplified Charts

Show fewer data points and simpler visualizations on mobile:

```typescript
// Responsive chart data
const chartData = computed(() => {
  const isMobile = window.innerWidth < 768
  const sourceData = props.data
  
  if (isMobile) {
    // Sample data for mobile (fewer points)
    return sampleData(sourceData, 10) // Max 10 points
  }
  
  return sourceData // Full data for desktop
})
```

### Swipeable Dashboard Pages

Break dashboard into pages on mobile:

```vue
<template>
  <div v-if="isMobile" class="mobile-dashboard">
    <SwipeablePages :pages="dashboardPages">
      <template #page="{ page }">
        <div class="dashboard-page">
          <Widget 
            v-for="widget in page.widgets"
            :key="widget.id"
            :widget="widget"
          />
        </div>
      </template>
    </SwipeablePages>
  </div>
  
  <div v-else class="desktop-dashboard">
    <!-- Full dashboard grid -->
  </div>
</template>
```

### Prioritize KPI Cards

On mobile, show KPI cards first, hide complex charts:

```vue
<template>
  <div class="mobile-dashboard">
    <!-- Always show KPIs -->
    <KPICard 
      v-for="kpi in kpis"
      :key="kpi.id"
      :kpi="kpi"
    />
    
    <!-- Charts below fold, simplified -->
    <CollapsibleSection title="Charts">
      <SimplifiedChart 
        v-for="chart in charts"
        :key="chart.id"
        :chart="chart"
      />
    </CollapsibleSection>
  </div>
</template>
```
