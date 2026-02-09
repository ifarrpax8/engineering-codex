# Product Perspective: Data Visualization

## Contents

- [Why Data Visualization Matters](#why-data-visualization-matters)
- [Chart Type Selection](#chart-type-selection)
- [Dashboard Design](#dashboard-design)
- [Export and Reporting](#export-and-reporting)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Why Data Visualization Matters

In B2B SaaS, data visualization transforms raw data into actionable insights that drive business decisions. Executives need quick summaries to assess health, analysts require detailed views to identify trends, and business users depend on dashboards to monitor KPIs and make operational decisions.

Effective data visualization enables:

- **Faster decision-making** — Visual patterns are recognized faster than scanning tables of numbers
- **Stakeholder reporting** — Executives can quickly understand performance without deep technical knowledge
- **Anomaly detection** — Visual outliers stand out immediately (e.g., sudden revenue drop, spike in error rates)
- **Trend identification** — Time-series charts reveal patterns that might be missed in tabular data
- **Comparative analysis** — Side-by-side charts enable quick comparisons across time periods, regions, or product lines

## Chart Type Selection

Choosing the right chart type is critical for effective communication. Match the chart to the data story you're telling:

### Bar Charts
**Use for:** Comparing discrete categories, showing rankings, part-to-whole comparisons with few categories
**Example:** Revenue by product line, top 10 customers by spend, monthly signups by region
**Avoid when:** You have more than 10-12 categories (use horizontal bar or consider grouping)

### Line Charts
**Use for:** Trends over time, continuous data, multiple series comparisons
**Example:** Daily active users over 30 days, revenue trends month-over-month, error rate over time
**Avoid when:** Data points are not sequential or time-based

### Pie Charts
**Use for:** Parts-of-whole relationships with 5-6 or fewer categories
**Example:** Revenue breakdown by product category (3-4 categories), user distribution by plan tier
**Avoid when:** You have more than 6 slices (use bar chart instead), values are very similar (hard to distinguish)

### Area Charts
**Use for:** Cumulative totals over time, showing composition of a whole over time
**Example:** Cumulative revenue with breakdown by product line, total users with breakdown by acquisition channel
**Avoid when:** You need precise value comparisons (bar charts are better)

### Scatter Plots
**Use for:** Correlation analysis, identifying outliers, distribution patterns
**Example:** Customer lifetime value vs acquisition cost, response time vs request size
**Avoid when:** You need to show exact values (use table or bar chart)

### Heatmaps
**Use for:** Matrix data, showing intensity across two dimensions
**Example:** User activity by hour of day and day of week, error rates by service and region
**Avoid when:** You need precise numeric values (use table)

### Treemaps
**Use for:** Hierarchical data with size relationships, large category sets
**Example:** Revenue by product hierarchy, file system storage usage
**Avoid when:** Users need to compare specific values (bar charts are clearer)

## Dashboard Design

### Information Hierarchy

1. **KPIs at the top** — Most important metrics visible immediately (revenue, users, error rate)
2. **Supporting charts below** — Detailed breakdowns and trends that explain the KPIs
3. **Drill-down patterns** — Click a KPI card to see detailed chart, click chart to see underlying data table

### KPI Cards

KPI cards should show:
- **Current value** — Large, prominent number
- **Change indicator** — Percentage change vs previous period with up/down arrow
- **Trend sparkline** — Mini line chart showing recent trend
- **Clickable** — Navigate to detailed view

```vue
<!-- Vue 3 KPI Card Example -->
<template>
  <div class="kpi-card" @click="navigateToDetail">
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ formattedValue }}</div>
    <div class="kpi-change" :class="changeClass">
      <span>{{ changePercent }}%</span>
      <TrendIcon :direction="changeDirection" />
    </div>
    <MiniSparkline :data="trendData" />
  </div>
</template>
```

### Date Range Selectors

Every dashboard needs date range context:
- **Presets** — "Last 7 days", "Last 30 days", "This month", "Last quarter"
- **Custom range** — Date picker for specific periods
- **Comparison toggle** — "Compare to previous period" checkbox
- **Apply to all widgets** — Single date range controls entire dashboard

### Comparison Views

Enable users to compare:
- **Period-over-period** — This month vs last month
- **Year-over-year** — Q1 2025 vs Q1 2024
- **Target vs actual** — Show target line on charts
- **Multiple series** — Overlay different metrics (e.g., revenue and users)

## Export and Reporting

### PDF Reports

Generate comprehensive PDF reports containing:
- **Executive summary** — High-level KPIs and insights
- **Charts and visualizations** — All dashboard charts rendered as images
- **Data tables** — Detailed breakdowns
- **Metadata** — Report generation date, date range, filters applied

**Use cases:** Monthly business reviews, quarterly board reports, compliance documentation

### CSV/Excel Data Export

Enable users to export underlying data:
- **Filtered data** — Respect current dashboard filters and date range
- **All columns** — Include calculated fields and aggregations
- **Formatted values** — Currency, percentages, dates properly formatted
- **Multiple sheets** — Excel export with separate sheets per chart/widget

### Scheduled Reports

Automated report generation:
- **Schedule configuration** — Daily, weekly, monthly cadence
- **Recipient management** — Email distribution list
- **Format selection** — PDF, Excel, or both
- **Failure notifications** — Alert if report generation fails

### Email Delivery

- **Embedded charts** — Include chart images in email body
- **Summary text** — Key insights and highlights
- **Link to dashboard** — "View full dashboard" CTA
- **Attachment options** — PDF/Excel as attachments

## Personas

### Business User (Glancing at KPIs)

**Needs:** Quick health check, immediate alerts on anomalies
**Usage pattern:** Opens dashboard 2-3 times per day, spends 30 seconds scanning KPIs
**Key features:** KPI cards, color-coded status indicators, mobile-friendly view

### Analyst (Drilling into Trends)

**Needs:** Detailed data exploration, custom date ranges, export capabilities
**Usage pattern:** Deep dives for 30+ minutes, creates custom views, exports data for analysis
**Key features:** Interactive charts, drill-down navigation, data export, custom filters

### Executive (Viewing Summary Dashboards)

**Needs:** High-level overview, trend identification, comparison views
**Usage pattern:** Weekly review sessions, shares dashboards in meetings
**Key features:** Executive summary view, period-over-period comparison, PDF export, presentation mode

### Admin (Configuring Reports)

**Needs:** Dashboard customization, scheduled report setup, user access management
**Usage pattern:** Initial setup, periodic maintenance, troubleshooting
**Key features:** Dashboard builder, widget configuration, scheduled report management, access controls

## Success Metrics

### Dashboard Load Time
**Target:** < 2 seconds for initial render, < 5 seconds for full dashboard with 6-8 widgets
**Measurement:** Time to first chart render, time to interactive

### Export Completion Rate
**Target:** > 95% of export requests complete successfully
**Measurement:** Track export job success/failure, monitor timeout rates

### Time-to-Insight
**Target:** Users find answers within 30 seconds of opening dashboard
**Measurement:** Time from dashboard load to first interaction (filter, drill-down, export)

### Report Usage Frequency
**Target:** Scheduled reports opened/accessed > 70% of the time
**Measurement:** Email open rates, dashboard view frequency, export download rates

## Common Product Mistakes

### Wrong Chart Type for Data

**Problem:** Using pie chart for 12+ categories, using line chart for non-sequential data
**Impact:** Users can't extract insights, data appears confusing
**Solution:** Follow chart type selection guidelines, provide chart type recommendations in UI

### Too Many Charts on One Dashboard

**Problem:** 15+ widgets on a single dashboard view
**Impact:** Cognitive overload, slow load times, users can't focus
**Solution:** Limit to 6-8 widgets per view, use tabs or pages for organization

### No Date Range Context

**Problem:** Charts show data without indicating the time period
**Impact:** Users can't interpret the data, comparisons are meaningless
**Solution:** Always show date range selector, display selected range prominently

### Charts That Don't Answer a Question

**Problem:** Beautiful charts that don't help users make decisions
**Impact:** Low engagement, users abandon dashboards
**Solution:** Start with user questions: "What's our revenue trend?" → line chart, "Which product sells best?" → bar chart

### Missing Empty States

**Problem:** Blank charts with no explanation when no data exists
**Impact:** Users think the feature is broken
**Solution:** Show "No data for this period" message with suggestions (change date range, check filters)

### No Export Capability

**Problem:** Users can see data but can't take it elsewhere
**Impact:** Users resort to screenshots, manual data entry
**Solution:** Provide CSV/Excel export for all chart data, PDF export for dashboards
