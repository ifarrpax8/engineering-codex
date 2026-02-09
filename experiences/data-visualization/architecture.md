# Architecture: Data Visualization

## Contents

- [Charting Library Integration](#charting-library-integration)
- [Data Aggregation](#data-aggregation)
- [Dashboard Architecture](#dashboard-architecture)
- [Real-time Dashboards](#real-time-dashboards)
- [Export Architecture](#export-architecture)
- [Responsive Charts](#responsive-charts)
- [Performance Optimization](#performance-optimization)

## Charting Library Integration

### Vue 3 with Chart.js

Use `vue-chartjs` wrapper for Chart.js integration:

```vue
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface Props {
  data: Array<{ date: string; value: number }>
  dateRange: { start: string; end: string }
}

const props = defineProps<Props>()

const chartData = computed(() => ({
  labels: props.data.map(d => d.date),
  datasets: [{
    label: 'Revenue',
    data: props.data.map(d => d.value),
    borderColor: 'rgb(75, 192, 192)',
    backgroundColor: 'rgba(75, 192, 192, 0.2)',
    tension: 0.1
  }]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true },
    tooltip: {
      callbacks: {
        label: (context: any) => `$${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: any) => `$${value.toLocaleString()}`
      }
    }
  }
}))
</script>

<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
```

### React with Recharts

Recharts provides declarative chart components:

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface RevenueChartProps {
  data: Array<{ date: string; revenue: number; users: number }>
  dateRange: { start: string; end: string }
}

export function RevenueChart({ data, dateRange }: RevenueChartProps) {
  const formattedData = data.map(d => ({
    ...d,
    revenue: Math.round(d.revenue),
    formattedDate: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }))

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="formattedDate" />
        <YAxis 
          yAxisId="left"
          tickFormatter={(value) => `$${value.toLocaleString()}`}
        />
        <YAxis 
          yAxisId="right" 
          orientation="right"
          tickFormatter={(value) => value.toLocaleString()}
        />
        <Tooltip 
          formatter={(value: number, name: string) => {
            if (name === 'revenue') return `$${value.toLocaleString()}`
            return value.toLocaleString()
          }}
        />
        <Legend />
        <Line 
          yAxisId="left"
          type="monotone" 
          dataKey="revenue" 
          stroke="#8884d8" 
          name="Revenue"
        />
        <Line 
          yAxisId="right"
          type="monotone" 
          dataKey="users" 
          stroke="#82ca9d" 
          name="Users"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

### Wrapper Components Pattern

Create reusable chart wrapper components that handle:
- Loading states (skeleton charts)
- Error states (error message with retry)
- Empty states (no data message)
- Data transformation (API response → chart format)

```typescript
// Vue 3 Composable for Chart Options
import { computed, type Ref } from 'vue'

export function useChartOptions(
  title: string,
  yAxisLabel: string,
  currency: boolean = false
) {
  return computed(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: title
      },
      legend: {
        display: true,
        position: 'top' as const
      },
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

## Data Aggregation

### Server-Side Aggregation

**Never send raw data to the client for large datasets.** Aggregate in SQL/Spring Boot:

```kotlin
// Spring Boot Repository with Aggregation
@Repository
interface RevenueRepository : JpaRepository<Transaction, Long> {
    
    @Query("""
        SELECT 
            DATE_TRUNC('day', created_at) as date,
            SUM(amount) as total_revenue,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE created_at BETWEEN :startDate AND :endDate
        GROUP BY DATE_TRUNC('day', created_at)
        ORDER BY date
    """, nativeQuery = true)
    fun getDailyRevenue(
        @Param("startDate") startDate: LocalDateTime,
        @Param("endDate") endDate: LocalDateTime
    ): List<DailyRevenueProjection>
}

data class DailyRevenueProjection(
    val date: LocalDate,
    val totalRevenue: BigDecimal,
    val transactionCount: Long
)

// Controller Endpoint
@RestController
@RequestMapping("/api/charts")
class ChartDataController(
    private val revenueRepository: RevenueRepository
) {
    @GetMapping("/revenue")
    fun getRevenueData(
        @RequestParam startDate: LocalDate,
        @RequestParam endDate: LocalDate
    ): ResponseEntity<List<DailyRevenueDto>> {
        val data = revenueRepository.getDailyRevenue(
            startDate.atStartOfDay(),
            endDate.atTime(23, 59, 59)
        )
        return ResponseEntity.ok(data.map { it.toDto() })
    }
}
```

### Time-Bucketing Strategy

For different time ranges, use different aggregation buckets:

```kotlin
enum class TimeBucket {
    HOUR, DAY, WEEK, MONTH
}

fun getBucketFunction(bucket: TimeBucket): String {
    return when (bucket) {
        TimeBucket.HOUR -> "DATE_TRUNC('hour', created_at)"
        TimeBucket.DAY -> "DATE_TRUNC('day', created_at)"
        TimeBucket.WEEK -> "DATE_TRUNC('week', created_at)"
        TimeBucket.MONTH -> "DATE_TRUNC('month', created_at)"
    }
}

// Auto-select bucket based on date range
fun selectBucket(startDate: LocalDate, endDate: LocalDate): TimeBucket {
    val days = ChronoUnit.DAYS.between(startDate, endDate)
    return when {
        days <= 1 -> TimeBucket.HOUR
        days <= 30 -> TimeBucket.DAY
        days <= 90 -> TimeBucket.WEEK
        else -> TimeBucket.MONTH
    }
}
```

### API Design for Chart Data

**Option 1: Pre-aggregated Endpoints (Recommended)**

```kotlin
// Dedicated chart data endpoints
GET /api/charts/revenue?startDate=2025-01-01&endDate=2025-01-31
GET /api/charts/users?startDate=2025-01-01&endDate=2025-01-31
GET /api/charts/conversion-rate?startDate=2025-01-01&endDate=2025-01-31

// Returns optimized format:
{
  "labels": ["2025-01-01", "2025-01-02", ...],
  "datasets": [{
    "label": "Revenue",
    "data": [12500, 13200, ...]
  }]
}
```

**Option 2: Raw Data + Client Aggregation (Avoid for Large Datasets)**

Only use when:
- Dataset is small (< 1000 rows)
- User needs raw data for export
- Aggregation logic is user-configurable

### Caching Aggregated Results

Cache expensive aggregation queries:

```kotlin
@Service
class ChartDataService(
    private val revenueRepository: RevenueRepository,
    private val cacheManager: CacheManager
) {
    
    @Cacheable(value = ["chartData"], key = "#startDate.toString() + '-' + #endDate.toString()")
    fun getRevenueData(startDate: LocalDate, endDate: LocalDate): List<DailyRevenueDto> {
        return revenueRepository.getDailyRevenue(
            startDate.atStartOfDay(),
            endDate.atTime(23, 59, 59)
        ).map { it.toDto() }
    }
}

// Redis Cache Configuration
@Configuration
@EnableCaching
class CacheConfig {
    @Bean
    fun cacheManager(redisConnectionFactory: RedisConnectionFactory): CacheManager {
        return RedisCacheManager.builder(redisConnectionFactory)
            .cacheDefaults(
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(5))
            )
            .build()
    }
}
```

## Dashboard Architecture

### Layout System

**Grid-Based Dashboard:**

```vue
<!-- Vue 3 Dashboard Layout -->
<template>
  <div class="dashboard-grid" :style="gridStyle">
    <DashboardWidget
      v-for="widget in widgets"
      :key="widget.id"
      :widget="widget"
      :style="widgetStyle(widget)"
      @update="updateWidget"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Widget {
  id: string
  type: 'chart' | 'kpi' | 'table'
  x: number
  y: number
  width: number
  height: number
  config: any
}

const props = defineProps<{
  widgets: Widget[]
}>()

const gridStyle = computed(() => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(12, 1fr)',
  gap: '16px'
}))

const widgetStyle = (widget: Widget) => ({
  gridColumn: `span ${widget.width}`,
  gridRow: `span ${widget.height}`
})
</script>
```

**Drag-and-Drop Widget Placement:**

```tsx
// React with react-grid-layout
import GridLayout from 'react-grid-layout'
import 'react-grid-layout/css/styles.css'
import 'react-grid-layout/css/resizable.css'

export function Dashboard({ widgets, onLayoutChange }) {
  const layout = widgets.map(w => ({
    i: w.id,
    x: w.x,
    y: w.y,
    w: w.width,
    h: w.height
  }))

  return (
    <GridLayout
      className="layout"
      layout={layout}
      cols={12}
      rowHeight={60}
      onLayoutChange={onLayoutChange}
      isDraggable={true}
      isResizable={true}
    >
      {widgets.map(widget => (
        <div key={widget.id}>
          <WidgetComponent widget={widget} />
        </div>
      ))}
    </GridLayout>
  )
}
```

### Widget Component Architecture

Each widget should:
- Fetch its own data (or receive via props)
- Handle loading/error/empty states
- Accept shared context (date range, filters)
- Emit events for interactions (drill-down, export)

```typescript
// Widget Base Interface
interface WidgetConfig {
  id: string
  type: 'line' | 'bar' | 'pie' | 'kpi' | 'table'
  dataSource: {
    endpoint: string
    params?: Record<string, any>
  }
  title: string
  dateRange?: { start: string; end: string }
  filters?: Record<string, any>
}

// Widget Component Props
interface WidgetProps {
  config: WidgetConfig
  dateRange: { start: string; end: string }
  filters: Record<string, any>
  onDrillDown?: (data: any) => void
  onExport?: () => void
}
```

### Data Fetching Per Widget

**Parallel Requests:**

```typescript
// Vue 3: Fetch all widget data in parallel
import { ref, watch } from 'vue'
import axios from 'axios'

export function useDashboardData(widgets: Widget[], dateRange: Ref<DateRange>) {
  const loading = ref(true)
  const widgetData = ref<Record<string, any>>({})
  const errors = ref<Record<string, Error>>({})

  const fetchAllWidgets = async () => {
    loading.value = true
    const promises = widgets.map(async (widget) => {
      try {
        const response = await axios.get(widget.dataSource.endpoint, {
          params: {
            ...widget.dataSource.params,
            startDate: dateRange.value.start,
            endDate: dateRange.value.end
          }
        })
        widgetData.value[widget.id] = response.data
      } catch (error) {
        errors.value[widget.id] = error as Error
      }
    })
    await Promise.all(promises)
    loading.value = false
  }

  watch(dateRange, fetchAllWidgets, { immediate: true })

  return { loading, widgetData, errors, refetch: fetchAllWidgets }
}
```

**Shared Date Range Context:**

```tsx
// React Context for Dashboard State
const DashboardContext = createContext<{
  dateRange: DateRange
  setDateRange: (range: DateRange) => void
  filters: Record<string, any>
  setFilters: (filters: Record<string, any>) => void
}>()

export function DashboardProvider({ children }) {
  const [dateRange, setDateRange] = useState<DateRange>({
    start: subDays(new Date(), 30),
    end: new Date()
  })
  const [filters, setFilters] = useState({})

  return (
    <DashboardContext.Provider value={{ dateRange, setDateRange, filters, setFilters }}>
      {children}
    </DashboardContext.Provider>
  )
}
```

## Real-time Dashboards

### WebSocket for Live Chart Updates

```kotlin
// Spring Boot WebSocket Configuration
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureMessageBroker(config: MessageBrokerRegistry) {
        config.enableSimpleBroker("/topic")
        config.setApplicationDestinationPrefixes("/app")
    }

    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws/dashboard").setAllowedOrigins("*")
    }
}

// WebSocket Service
@Service
class DashboardUpdateService(
    private val messagingTemplate: SimpMessagingTemplate
) {
    fun broadcastRevenueUpdate(revenue: BigDecimal) {
        messagingTemplate.convertAndSend(
            "/topic/dashboard/revenue",
            RevenueUpdate(revenue, LocalDateTime.now())
        )
    }
}
```

```typescript
// Vue 3 WebSocket Client
import { ref, onMounted, onUnmounted } from 'vue'
import { Client } from '@stomp/stompjs'

export function useRealtimeChart(chartData: Ref<any[]>) {
  const client = ref<Client | null>(null)
  const connected = ref(false)

  onMounted(() => {
    const stompClient = new Client({
      brokerURL: 'ws://localhost:8080/ws/dashboard',
      onConnect: () => {
        connected.value = true
        stompClient.subscribe('/topic/dashboard/revenue', (message) => {
          const update = JSON.parse(message.body)
          // Append new data point
          chartData.value.push({
            date: update.timestamp,
            value: update.revenue
          })
          // Keep only last 100 points
          if (chartData.value.length > 100) {
            chartData.value.shift()
          }
        })
      }
    })
    client.value = stompClient
    stompClient.activate()
  })

  onUnmounted(() => {
    client.value?.deactivate()
  })

  return { connected }
}
```

### Polling for Near-Real-Time

When WebSocket isn't available, use intelligent polling:

```typescript
// Polling with exponential backoff on errors
export function usePollingChartData(
  fetchFn: () => Promise<any[]>,
  intervalMs: number = 5000
) {
  const data = ref<any[]>([])
  const error = ref<Error | null>(null)
  let pollInterval: number | null = null
  let currentInterval = intervalMs

  const poll = async () => {
    try {
      const newData = await fetchFn()
      data.value = newData
      error.value = null
      currentInterval = intervalMs // Reset on success
    } catch (err) {
      error.value = err as Error
      currentInterval = Math.min(currentInterval * 2, 60000) // Max 60s
    }
  }

  const startPolling = () => {
    poll() // Immediate fetch
    pollInterval = setInterval(poll, currentInterval)
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  return { data, error, startPolling, stopPolling }
}
```

### Incremental Data Append

For time-series charts, append new points and scroll axis:

```typescript
// Append new point and auto-scroll
function appendChartData(
  chart: Chart,
  newPoint: { x: string; y: number }
) {
  chart.data.labels.push(newPoint.x)
  chart.data.datasets[0].data.push(newPoint.y)
  
  // Keep only last N points
  const maxPoints = 100
  if (chart.data.labels.length > maxPoints) {
    chart.data.labels.shift()
    chart.data.datasets[0].data.shift()
  }
  
  chart.update('none') // 'none' mode for smooth animation
  
  // Auto-scroll X axis if needed
  const lastIndex = chart.data.labels.length - 1
  chart.setActiveElements([{ datasetIndex: 0, index: lastIndex }])
}
```

## Export Architecture

### Client-Side Export

**Canvas to Image (Chart.js):**

```typescript
// Export chart as PNG
function exportChartAsPNG(chart: Chart, filename: string) {
  const url = chart.toBase64Image('image/png', 1.0)
  const link = document.createElement('a')
  link.download = filename
  link.href = url
  link.click()
}

// Export dashboard as PDF (html2canvas + jsPDF)
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

async function exportDashboardAsPDF(dashboardElement: HTMLElement) {
  const canvas = await html2canvas(dashboardElement, {
    scale: 2,
    useCORS: true
  })
  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF('landscape', 'mm', 'a4')
  const imgWidth = 297 // A4 width in mm
  const imgHeight = (canvas.height * imgWidth) / canvas.width
  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
  pdf.save('dashboard.pdf')
}
```

### Server-Side Export

**Spring Boot PDF Generation (iText/OpenPDF):**

```kotlin
@Service
class ReportExportService(
    private val chartDataService: ChartDataService,
    private val pdfGenerator: PdfGenerator
) {
    fun generateDashboardPDF(
        dashboardId: String,
        dateRange: DateRange,
        userId: String
    ): ByteArray {
        val dashboard = getDashboard(dashboardId)
        val widgets = dashboard.widgets
        
        // Fetch all widget data
        val widgetData = widgets.associate { widget ->
            widget.id to chartDataService.getWidgetData(widget, dateRange)
        }
        
        // Generate PDF
        return pdfGenerator.generatePDF {
            addTitle(dashboard.title)
            addDateRange(dateRange)
            
            widgets.forEach { widget ->
                when (widget.type) {
                    WidgetType.CHART -> {
                        val chartImage = renderChartAsImage(widget, widgetData[widget.id]!!)
                        addImage(chartImage)
                    }
                    WidgetType.KPI -> {
                        addKPI(widget, widgetData[widget.id]!!)
                    }
                    WidgetType.TABLE -> {
                        addTable(widget, widgetData[widget.id]!!)
                    }
                }
            }
        }
    }
    
    private fun renderChartAsImage(widget: Widget, data: Any): ByteArray {
        // Use headless browser (Puppeteer/Playwright) or chart rendering service
        // to generate chart image server-side
        return chartRenderingService.render(widget.type, data)
    }
}

// Excel Export with Apache POI
@Service
class ExcelExportService {
    fun exportChartDataToExcel(data: List<ChartDataPoint>): ByteArray {
        val workbook = XSSFWorkbook()
        val sheet = workbook.createSheet("Chart Data")
        
        // Header row
        val headerRow = sheet.createRow(0)
        headerRow.createCell(0).setCellValue("Date")
        headerRow.createCell(1).setCellValue("Value")
        
        // Data rows
        data.forEachIndexed { index, point ->
            val row = sheet.createRow(index + 1)
            row.createCell(0).setCellValue(point.date.toString())
            row.createCell(1).setCellValue(point.value.toDouble())
        }
        
        val outputStream = ByteArrayOutputStream()
        workbook.write(outputStream)
        workbook.close()
        return outputStream.toByteArray()
    }
}
```

### Async Large Export

For exports that take > 5 seconds, use async job queue:

```kotlin
// Export Job Entity
@Entity
class ExportJob(
    @Id val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val dashboardId: String,
    val format: ExportFormat,
    val status: ExportStatus = ExportStatus.PENDING,
    val fileUrl: String? = null,
    val createdAt: LocalDateTime = LocalDateTime.now(),
    val completedAt: LocalDateTime? = null
)

// Export Service with Queue
@Service
class AsyncExportService(
    private val exportJobRepository: ExportJobRepository,
    private val jobQueue: JobQueue,
    private val storageService: StorageService
) {
    fun requestExport(
        userId: String,
        dashboardId: String,
        format: ExportFormat
    ): ExportJob {
        val job = ExportJob(
            userId = userId,
            dashboardId = dashboardId,
            format = format
        )
        exportJobRepository.save(job)
        
        jobQueue.enqueue(ExportJobTask(job.id))
        
        return job
    }
    
    @Transactional
    fun processExport(jobId: String) {
        val job = exportJobRepository.findById(jobId).orElseThrow()
        
        try {
            job.status = ExportStatus.PROCESSING
            exportJobRepository.save(job)
            
            val fileBytes = generateExport(job)
            val fileUrl = storageService.upload(fileBytes, "${jobId}.${job.format.extension}")
            
            job.status = ExportStatus.COMPLETED
            job.fileUrl = fileUrl
            job.completedAt = LocalDateTime.now()
            exportJobRepository.save(job)
            
            // Notify user (email, WebSocket, etc.)
            notificationService.notifyExportReady(job.userId, job.id)
        } catch (e: Exception) {
            job.status = ExportStatus.FAILED
            exportJobRepository.save(job)
            throw e
        }
    }
}
```

## Responsive Charts

### Chart Resize on Viewport Change

```typescript
// Vue 3: ResizeObserver for chart container
import { ref, onMounted, onUnmounted } from 'vue'

export function useResponsiveChart(chartRef: Ref<Chart | null>) {
  const containerRef = ref<HTMLElement | null>(null)
  let resizeObserver: ResizeObserver | null = null

  onMounted(() => {
    if (containerRef.value) {
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

### Simplified Charts on Mobile

```typescript
// Detect mobile and simplify chart
const isMobile = computed(() => window.innerWidth < 768)

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: !isMobile.value // Hide legend on mobile
    },
    tooltip: {
      enabled: !isMobile.value // Disable tooltips on mobile (use tap instead)
    }
  },
  scales: {
    x: {
      ticks: {
        maxRotation: isMobile.value ? 45 : 0,
        maxTicksLimit: isMobile.value ? 5 : 10
      }
    }
  }
}))
```

### Touch Interactions

```typescript
// Chart.js with chartjs-plugin-zoom
import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(zoomPlugin)

const chartOptions = {
  plugins: {
    zoom: {
      zoom: {
        wheel: {
          enabled: true
        },
        pinch: {
          enabled: true // Mobile pinch zoom
        },
        mode: 'x'
      },
      pan: {
        enabled: true,
        mode: 'x'
      }
    }
  }
}
```

## Performance Optimization

### Lazy Loading Charts Below the Fold

```vue
<!-- Vue 3: Intersection Observer for lazy loading -->
<template>
  <div ref="chartContainer" class="chart-container">
    <ChartComponent v-if="isVisible" :data="chartData" />
    <ChartSkeleton v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const chartContainer = ref<HTMLElement | null>(null)
const isVisible = ref(false)

onMounted(() => {
  if (chartContainer.value) {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          isVisible.value = true
          observer.disconnect()
        }
      },
      { rootMargin: '100px' } // Start loading 100px before visible
    )
    observer.observe(chartContainer.value)
  }
})
</script>
```

### Virtual Rendering for Large Datasets

```typescript
// Sample data for charts with 10K+ points
function sampleDataForChart(
  data: Array<{ x: number; y: number }>,
  maxPoints: number = 500
): Array<{ x: number; y: number }> {
  if (data.length <= maxPoints) return data
  
  const step = Math.ceil(data.length / maxPoints)
  const sampled: Array<{ x: number; y: number }> = []
  
  for (let i = 0; i < data.length; i += step) {
    sampled.push(data[i])
  }
  
  // Always include last point
  if (sampled[sampled.length - 1] !== data[data.length - 1]) {
    sampled.push(data[data.length - 1])
  }
  
  return sampled
}
```

### WebWorker for Client-Side Aggregation

```typescript
// chart-aggregator.worker.ts
self.onmessage = function(e) {
  const { data, bucketSize } = e.data
  
  const aggregated = []
  let bucket: any[] = []
  
  for (let i = 0; i < data.length; i++) {
    bucket.push(data[i])
    
    if (bucket.length === bucketSize || i === data.length - 1) {
      const avg = bucket.reduce((sum, d) => sum + d.value, 0) / bucket.length
      aggregated.push({
        date: bucket[0].date,
        value: avg
      })
      bucket = []
    }
  }
  
  self.postMessage(aggregated)
}

// Main thread usage
const worker = new Worker('/chart-aggregator.worker.ts')

worker.postMessage({
  data: rawData,
  bucketSize: 10
})

worker.onmessage = (e) => {
  chartData.value = e.data
}
```
