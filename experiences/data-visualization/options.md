# Options: Data Visualization

## Contents

- [Charting Libraries](#charting-libraries)
  - [Chart.js](#chartjs)
  - [Recharts (React)](#recharts-react)
  - [ECharts](#echarts)
  - [D3.js](#d3js)
  - [Victory (React)](#victory-react)
  - [vue-chartjs (Vue)](#vue-chartjs-vue)
- [Dashboard Layout Systems](#dashboard-layout-systems)
  - [CSS Grid (Custom)](#css-grid-custom)
  - [react-grid-layout / vue-grid-layout](#react-grid-layout--vue-grid-layout)
  - [Commercial Solutions (Grafana Embedded)](#commercial-solutions-grafana-embedded)
- [Export Approaches](#export-approaches)
  - [Client-Side Export (jsPDF + html2canvas)](#client-side-export-jspdf-html2canvas)
  - [Server-Side Export (Spring Boot + iText/OpenPDF + Apache POI)](#server-side-export-spring-boot-itextopenpdf-apache-poi)
  - [Async Export with Notification](#async-export-with-notification)
- [Recommendations](#recommendations)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Charting Libraries

### Chart.js

**Description:** Canvas-based charting library with simple API and good performance. Works with Vue via `vue-chartjs` and React via `react-chartjs-2`.

**Strengths:**
- Simple API, easy to learn
- Good performance with canvas rendering
- Extensive chart type library (line, bar, pie, radar, etc.)
- Active community and good documentation
- Works well with both Vue and React
- Responsive by default
- Good mobile support

**Weaknesses:**
- Canvas-based (harder to style with CSS)
- Less customizable than SVG-based libraries
- Limited animation control
- File size (~200KB minified)

**Best For:**
- Standard chart types (line, bar, pie)
- Dashboards with multiple charts
- Teams new to data visualization
- Applications needing consistent, polished charts quickly

**Avoid When:**
- You need highly custom visualizations
- You require SVG for styling/accessibility
- You need complex interactions (custom zoom, brush selection)

**Code Example:**
```vue
<!-- Vue 3 with vue-chartjs -->
<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement)

const chartData = {
  labels: ['Jan', 'Feb', 'Mar'],
  datasets: [{
    label: 'Revenue',
    data: [1000, 1200, 1500]
  }]
}
</script>

<template>
  <Line :data="chartData" />
</template>
```

---

### Recharts (React)

**Description:** Composable charting library built on D3 and React. Declarative API with SVG rendering.

**Strengths:**
- Declarative React components (feels native)
- SVG-based (stylable with CSS, better accessibility)
- Composable components (easy to customize)
- Good TypeScript support
- Responsive container component
- Active maintenance

**Weaknesses:**
- React-only (no Vue support)
- SVG can be slower than canvas for many data points
- Less chart types than Chart.js
- Steeper learning curve for complex customizations

**Best For:**
- React applications
- When you need SVG for styling/accessibility
- Composable chart components
- Applications requiring custom chart elements

**Avoid When:**
- You're using Vue (use vue-chartjs instead)
- You need canvas performance with 10K+ points
- You need many chart types out of the box

**Code Example:**
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export function RevenueChart({ data }) {
  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
    </LineChart>
  )
}
```

---

### ECharts

**Description:** Powerful, feature-rich charting library from Apache. Canvas-based with extensive customization options.

**Strengths:**
- Extremely feature-rich (20+ chart types)
- Excellent performance (canvas + WebGL support)
- Highly customizable (themes, animations, interactions)
- Good documentation with examples
- Supports complex visualizations (3D, maps, heatmaps)
- Works with Vue and React

**Weaknesses:**
- Larger bundle size (~500KB minified)
- More complex API than Chart.js
- Steeper learning curve
- Overkill for simple charts

**Best For:**
- Complex dashboards with diverse chart types
- Applications needing advanced features (3D, maps)
- When Chart.js limitations are hit
- Data-heavy applications (10K+ points)

**Avoid When:**
- You only need simple line/bar charts
- Bundle size is a concern
- Team prefers simpler APIs

**Code Example:**
```vue
<script setup lang="ts">
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent])

const option = {
  title: { text: 'Revenue Trend' },
  xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar'] },
  yAxis: { type: 'value' },
  series: [{
    data: [1000, 1200, 1500],
    type: 'line'
  }]
}
</script>

<template>
  <v-chart :option="option" style="height: 400px" />
</template>
```

---

### D3.js

**Description:** Low-level data visualization library. Maximum flexibility but requires building everything from scratch.

**Strengths:**
- Ultimate flexibility (build anything)
- Powerful data transformation utilities
- Industry standard for custom visualizations
- Extensive ecosystem
- No chart type limitations

**Weaknesses:**
- Very steep learning curve
- Requires building chart components from scratch
- More code to write and maintain
- Not ideal for standard charts

**Best For:**
- Highly custom visualizations
- Unique chart types not available elsewhere
- When you need pixel-perfect control
- Data visualization specialists on team

**Avoid When:**
- You need standard charts quickly
- Team lacks D3 expertise
- You want out-of-the-box solutions

**Code Example:**
```tsx
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export function CustomChart({ data }) {
  const svgRef = useRef<SVGSVGElement>(null)
  
  useEffect(() => {
    if (!svgRef.current) return
    
    const svg = d3.select(svgRef.current)
    const margin = { top: 20, right: 20, bottom: 40, left: 40 }
    const width = 800 - margin.left - margin.right
    const height = 400 - margin.top - margin.bottom
    
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, width])
    
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0])
    
    // ... custom implementation
  }, [data])
  
  return <svg ref={svgRef} width={800} height={400} />
}
```

---

### Victory (React)

**Description:** Composable React charting library with good animation support. Mid-level between Recharts and D3.

**Strengths:**
- Composable React components
- Good animation support
- Theming system
- Works well with React Native
- Good for mid-complexity charts

**Weaknesses:**
- React-only
- Smaller community than Recharts/Chart.js
- Less chart types than ECharts
- Can be verbose for simple charts

**Best For:**
- React applications needing animations
- When Recharts doesn't have a feature you need
- Applications requiring React Native support

**Avoid When:**
- You're using Vue
- Simple charts (Chart.js is easier)
- You need maximum customization (use D3)

---

### vue-chartjs (Vue)

**Description:** Vue wrapper for Chart.js. Provides Vue 3 Composition API integration.

**Strengths:**
- Native Vue 3 support
- All Chart.js features available
- Reactive data binding
- Simple API
- Good TypeScript support

**Weaknesses:**
- Vue-only (no React support)
- Inherits Chart.js limitations (canvas-based)
- Smaller community than React charting libraries

**Best For:**
- Vue 3 applications
- Teams familiar with Chart.js
- Standard chart requirements

**Avoid When:**
- You're using React (use react-chartjs-2)
- You need SVG-based charts (consider ECharts Vue wrapper)

---

## Dashboard Layout Systems

### CSS Grid (Custom)

**Description:** Build dashboard layout using native CSS Grid. Full control over layout behavior.

**Strengths:**
- No dependencies
- Full control over layout
- Lightweight
- Native browser support
- Flexible and customizable

**Weaknesses:**
- Must implement drag-and-drop yourself
- Must handle responsive behavior manually
- More code to write and maintain
- No built-in widget management

**Best For:**
- Simple, fixed layouts
- When you don't need drag-and-drop
- When bundle size is critical
- Teams comfortable with CSS Grid

**Avoid When:**
- You need drag-and-drop widget placement
- You want widget persistence/configuration UI
- You need complex responsive behavior

**Code Example:**
```vue
<template>
  <div class="dashboard-grid">
    <Widget 
      v-for="widget in widgets"
      :key="widget.id"
      :style="{
        gridColumn: `span ${widget.width}`,
        gridRow: `span ${widget.height}`
      }"
    />
  </div>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}
</style>
```

---

### react-grid-layout / vue-grid-layout

**Description:** Drag-and-drop grid layout libraries for React and Vue. Handles widget positioning and resizing.

**Strengths:**
- Built-in drag-and-drop
- Responsive breakpoints
- Widget resizing
- Layout persistence
- Active maintenance

**Weaknesses:**
- Additional dependency (~50KB)
- Less flexible than custom CSS Grid
- May have performance issues with 20+ widgets
- Requires learning library API

**Best For:**
- Dashboards requiring user customization
- Applications needing drag-and-drop
- When layout persistence is important

**Avoid When:**
- Fixed layouts only
- Bundle size is critical
- You need maximum performance with many widgets

**Code Example:**
```tsx
import GridLayout from 'react-grid-layout'

export function Dashboard({ widgets }) {
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
      onLayoutChange={(newLayout) => {
        // Save layout
      }}
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

---

### Commercial Solutions (Grafana Embedded)

**Description:** Embed Grafana dashboards in your application. Full-featured dashboard system.

**Strengths:**
- Extremely feature-rich
- Built-in data source connectors
- User-friendly dashboard builder
- Alerting and notifications
- Time-series optimized

**Weaknesses:**
- Commercial licensing costs
- Less customizable than custom solutions
- May not match your application's design system
- Overkill for simple dashboards

**Best For:**
- Time-series heavy applications
- When you need Grafana's data source ecosystem
- Applications requiring advanced alerting
- When budget allows commercial solution

**Avoid When:**
- Simple dashboards
- Budget constraints
- Need tight design system integration

---

## Export Approaches

### Client-Side Export (jsPDF + html2canvas)

**Description:** Generate PDFs/Excel in the browser using JavaScript libraries.

**Strengths:**
- No server load
- Fast for small exports
- Works offline
- No backend changes needed

**Weaknesses:**
- Limited by browser memory
- Can't handle very large exports (10K+ rows)
- Quality may vary across browsers
- Chart rendering may differ from display

**Best For:**
- Small to medium exports (< 5K rows)
- When server resources are limited
- Quick implementation
- Offline-capable applications

**Avoid When:**
- Large exports (10K+ rows)
- You need pixel-perfect chart rendering
- Export quality is critical

**Code Example:**
```typescript
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

async function exportDashboardAsPDF(element: HTMLElement) {
  const canvas = await html2canvas(element, { scale: 2 })
  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF('landscape', 'mm', 'a4')
  const imgWidth = 297
  const imgHeight = (canvas.height * imgWidth) / canvas.width
  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
  pdf.save('dashboard.pdf')
}
```

---

### Server-Side Export (Spring Boot + iText/OpenPDF + Apache POI)

**Description:** Generate PDFs and Excel files on the server using Java libraries.

**Strengths:**
- Handles large exports (100K+ rows)
- Consistent quality across clients
- Can use server-side chart rendering
- Better control over formatting
- Can access database directly

**Weaknesses:**
- Server resource usage
- Slower response time
- More complex implementation
- Requires backend changes

**Best For:**
- Large exports (10K+ rows)
- When export quality is critical
- Applications with server resources
- When you need database-level aggregation

**Avoid When:**
- Small exports only
- Server resources are constrained
- You want to avoid backend work

**Code Example:**
```kotlin
@Service
class PdfExportService {
    fun generateDashboardPDF(dashboard: Dashboard): ByteArray {
        val document = Document()
        val outputStream = ByteArrayOutputStream()
        val writer = PdfWriter.getInstance(document, outputStream)
        
        document.open()
        
        // Add charts as images
        dashboard.widgets.forEach { widget ->
            val chartImage = renderChartAsImage(widget)
            document.add(Image.getInstance(chartImage))
        }
        
        document.close()
        return outputStream.toByteArray()
    }
}
```

---

### Async Export with Notification

**Description:** Queue export jobs, process asynchronously, notify user when complete.

**Strengths:**
- Handles very large exports
- Doesn't block user
- Can retry on failure
- Better user experience

**Weaknesses:**
- More complex architecture
- Requires job queue system
- Requires notification system
- Longer time to completion

**Best For:**
- Very large exports (100K+ rows)
- When exports take > 5 seconds
- Applications with job queue infrastructure
- When user can wait for export

**Avoid When:**
- Small, fast exports
- You don't have job queue infrastructure
- Users need immediate exports

**Code Example:**
```kotlin
@Service
class AsyncExportService {
    fun requestExport(userId: String, dashboardId: String): ExportJob {
        val job = ExportJob(userId = userId, dashboardId = dashboardId)
        exportJobRepository.save(job)
        jobQueue.enqueue(ExportJobTask(job.id))
        return job
    }
    
    @Async
    fun processExport(jobId: String) {
        val job = exportJobRepository.findById(jobId).orElseThrow()
        job.status = ExportStatus.PROCESSING
        exportJobRepository.save(job)
        
        val fileBytes = generateExport(job)
        val fileUrl = storageService.upload(fileBytes, "${jobId}.pdf")
        
        job.status = ExportStatus.COMPLETED
        job.fileUrl = fileUrl
        exportJobRepository.save(job)
        
        notificationService.notifyExportReady(job.userId, job.id)
    }
}
```

---

## Recommendations

### Default Recommendation

**For most B2B SaaS applications:**

1. **Charting Library:** Chart.js via `vue-chartjs` (Vue) or `react-chartjs-2` (React)
   - Simple, performant, covers 90% of use cases
   - Easy for team to learn and maintain

2. **Dashboard Layout:** CSS Grid (custom) for fixed layouts, `react-grid-layout`/`vue-grid-layout` for customizable dashboards
   - Start with CSS Grid if layout is fixed
   - Add drag-and-drop library if users need customization

3. **Export:** Client-side (jsPDF + html2canvas) for small exports, server-side (Spring Boot) for large exports
   - Use client-side for < 5K rows
   - Use server-side for larger exports or when quality is critical

### When to Choose Alternatives

**Choose ECharts when:**
- You need advanced chart types (3D, maps, heatmaps)
- Chart.js limitations are hit
- You have 10K+ data points per chart

**Choose Recharts (React) when:**
- You need SVG-based charts for styling
- You prefer declarative React components
- Accessibility requirements favor SVG

**Choose D3.js when:**
- You need highly custom visualizations
- Standard libraries don't meet requirements
- You have D3 expertise on team

**Choose server-side export when:**
- Exports are > 10K rows
- Export quality is critical
- You need database-level aggregation

**Choose async export when:**
- Exports take > 5 seconds
- You have job queue infrastructure
- Users can wait for completion

---

## Synergies

### Chart.js + CSS Grid
- Simple, lightweight combination
- Good for fixed dashboard layouts
- Easy to learn and maintain

### ECharts + react-grid-layout
- Powerful charts + flexible layout
- Good for complex, customizable dashboards
- Handles diverse visualization needs

### Recharts + Server-Side Export
- SVG charts render well server-side
- Good for high-quality PDF exports
- Consistent rendering across clients

### Chart.js + Client-Side Export
- Fast, simple export implementation
- Good for small to medium exports
- Minimal backend changes

---

## Evolution Triggers

### Migrate from Chart.js to ECharts when:
- You need chart types Chart.js doesn't support
- Performance issues with 10K+ data points
- You need advanced customization (themes, animations)

### Migrate from Client-Side to Server-Side Export when:
- Exports frequently fail (> 5% failure rate)
- Export size exceeds 5K rows regularly
- Users report quality issues
- Browser memory limits hit

### Migrate from CSS Grid to Grid Layout Library when:
- Users request drag-and-drop functionality
- Layout customization becomes requirement
- You need layout persistence across sessions

### Migrate to Async Export when:
- Server-side exports timeout (> 30 seconds)
- Export requests overwhelm server
- Users complain about browser freezing during export
