# Gotchas: Feedback & Support

## Contents

- [Feedback Widget Covering Critical UI Elements](#feedback-widget-covering-critical-ui-elements)
- [Screenshot Capture Failing on Complex DOM](#screenshot-capture-failing-on-complex-dom)
- [Feedback Routing Rules Becoming Stale](#feedback-routing-rules-becoming-stale)
- [Knowledge Base Content Becoming Outdated](#knowledge-base-content-becoming-outdated)
- [Support Tickets Created But No Notification](#support-tickets-created-but-no-notification)
- [Users Submitting Feedback But Receiving No Acknowledgment](#users-submitting-feedback-but-receiving-no-acknowledgment)
- [NPS Survey Fatigue](#nps-survey-fatigue)
- [Context Not Captured](#context-not-captured)
- [Multi-Tenant Feedback Leaking](#multi-tenant-feedback-leaking)

## Feedback Widget Covering Critical UI Elements

### The Problem

Feedback widgets positioned as floating buttons or overlays can cover critical UI elements like:
- Submit/save buttons
- Form inputs
- Navigation menus
- Error messages
- Modal dialogs

**Example**: A feedback button in the bottom-right corner covers the "Save Invoice" button on mobile devices.

### The Solution

**Proper Z-Index Management**:

```css
/* Ensure feedback widget is below modals but above regular content */
.feedback-widget {
  z-index: 1000; /* Above regular content */
}

.modal-overlay {
  z-index: 2000; /* Above feedback widget */
}

/* Use CSS to detect if widget would overlap critical elements */
.feedback-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

/* On mobile, position differently if it would cover buttons */
@media (max-width: 768px) {
  .feedback-widget {
    bottom: 80px; /* Above mobile navigation */
  }
}
```

**Dynamic Positioning**:

```typescript
// Detect if widget would cover critical elements
function adjustWidgetPosition() {
  const widget = document.querySelector('.feedback-widget')
  const criticalElements = document.querySelectorAll('[data-critical]')
  
  for (const element of criticalElements) {
    const widgetRect = widget!.getBoundingClientRect()
    const elementRect = element.getBoundingClientRect()
    
    if (isOverlapping(widgetRect, elementRect)) {
      // Reposition widget
      widget!.style.bottom = `${elementRect.bottom + 20}px`
      break
    }
  }
}
```

**Collapsible Widget**:

```vue
<template>
  <div class="feedback-widget" :class="{ collapsed: isCollapsed }">
    <button
      v-if="isCollapsed"
      @click="isCollapsed = false"
      class="feedback-trigger"
    >
      💬
    </button>
    <div v-else class="feedback-form">
      <!-- Form content -->
      <button @click="isCollapsed = true">×</button>
    </div>
  </div>
</template>
```

## Screenshot Capture Failing on Complex DOM

### The Problem

Screenshot capture libraries like `html2canvas` can fail or produce incomplete screenshots when encountering:
- Canvas elements (charts, graphs)
- Iframes (embedded content, third-party widgets)
- Web Components with Shadow DOM
- SVG with external references
- Elements with `transform: scale()` or complex CSS transforms
- Large DOM trees (>10,000 elements)

**Example**: Screenshot shows blank space where a chart should be, or iframe content is missing.

### The Solution

**Handle Canvas Elements**:

```typescript
import html2canvas from 'html2canvas'

async function captureScreenshot() {
  // Convert canvas elements to images before capture
  const canvases = document.querySelectorAll('canvas')
  for (const canvas of canvases) {
    const img = document.createElement('img')
    img.src = canvas.toDataURL('image/png')
    img.style.display = 'none'
    canvas.parentElement?.appendChild(img)
    canvas.style.display = 'none'
  }
  
  const screenshot = await html2canvas(document.body, {
    useCORS: true,
    allowTaint: true,
    logging: false,
    scale: 0.5
  })
  
  // Restore canvases
  canvases.forEach(canvas => {
    canvas.style.display = ''
    canvas.parentElement?.querySelector('img')?.remove()
  })
  
  return screenshot.toDataURL('image/png')
}
```

**Handle Iframes**:

```typescript
// Iframes cannot be captured by html2canvas
// Instead, capture iframe content separately if same-origin
async function captureWithIframes() {
  const iframes = Array.from(document.querySelectorAll('iframe'))
  const iframeScreenshots: Record<string, string> = {}
  
  for (const iframe of iframes) {
    try {
      // Only works for same-origin iframes
      const iframeDoc = iframe.contentDocument
      if (iframeDoc) {
        const iframeCanvas = await html2canvas(iframeDoc.body)
        iframeScreenshots[iframe.id] = iframeCanvas.toDataURL('image/png')
      }
    } catch (e) {
      // Cross-origin iframe - cannot capture
      console.warn('Cannot capture cross-origin iframe:', iframe.src)
    }
  }
  
  // Include iframe screenshots as attachments
  return {
    mainScreenshot: await html2canvas(document.body),
    iframeScreenshots
  }
}
```

**Fallback Strategy**:

```typescript
async function captureScreenshotWithFallback() {
  try {
    return await html2canvas(document.body, {
      useCORS: true,
      timeout: 5000,
      scale: 0.5
    })
  } catch (error) {
    // Fallback: Use browser's native screenshot API if available
    if ('getDisplayMedia' in navigator.mediaDevices) {
      console.warn('html2canvas failed, using fallback method')
      // Prompt user to take screenshot manually
      return null // Return null and let user attach manually
    }
    throw error
  }
}
```

**Provide Manual Screenshot Option**:

```vue
<template>
  <div class="feedback-form">
    <label>
      Screenshot (optional)
      <input
        type="file"
        accept="image/*"
        @change="handleScreenshotUpload"
      />
    </label>
    <p class="help-text">
      If automatic capture fails, you can attach a screenshot manually
    </p>
  </div>
</template>
```

## Feedback Routing Rules Becoming Stale

### The Problem

Feedback routing rules (which team handles which category) become outdated as:
- Team structure changes
- Product areas are reorganized
- New categories are added but routing isn't updated
- Team members leave and tickets go unassigned

**Example**: Feature requests for "API improvements" still route to Product team, but API team was moved to Engineering.

### The Solution

**Centralized Routing Configuration**:

```kotlin
@Entity
@Table(name = "feedback_routing_rules")
data class FeedbackRoutingRule(
    @Id
    val id: String = UUID.randomUUID().toString(),
    
    val category: FeedbackCategory,
    val keywords: List<String>, // Keywords that trigger this rule
    
    val team: String, // Team name or ID
    val priority: Priority,
    
    val active: Boolean = true,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now(),
    val updatedBy: String
)

@Service
class FeedbackRoutingService(
    private val routingRuleRepository: FeedbackRoutingRuleRepository
) {
    
    fun routeFeedback(feedback: Feedback): RoutingDecision {
        val rules = routingRuleRepository.findActiveRules()
        
        // Find matching rule
        val matchingRule = rules.firstOrNull { rule ->
            rule.category == feedback.category ||
            rule.keywords.any { keyword ->
                feedback.description.contains(keyword, ignoreCase = true)
            }
        }
        
        return RoutingDecision(
            team = matchingRule?.team ?: "SUPPORT", // Default fallback
            priority = matchingRule?.priority ?: Priority.MEDIUM,
            ruleId = matchingRule?.id
        )
    }
}
```

**Regular Review Process**:

```kotlin
@Service
class RoutingRuleReviewService {
    
    @Scheduled(cron = "0 0 9 * * MON") // Every Monday at 9 AM
    fun reviewRoutingRules() {
        val rules = routingRuleRepository.findAll()
        
        for (rule in rules) {
            // Check if team still exists
            if (!teamService.teamExists(rule.team)) {
                log.warn("Routing rule ${rule.id} references non-existent team ${rule.team}")
                // Notify admins
                notificationService.notifyAdmins(
                    "Routing rule needs update: ${rule.id}"
                )
            }
            
            // Check if rule is being used
            val usageCount = feedbackRepository.countByRoutingRule(rule.id)
            if (usageCount == 0 && rule.createdAt.isBefore(Instant.now().minus(90, ChronoUnit.DAYS))) {
                log.info("Unused routing rule: ${rule.id}")
                // Flag for review
            }
        }
    }
}
```

**Fallback and Escalation**:

```kotlin
@Service
class FeedbackRoutingService {
    
    fun routeFeedback(feedback: Feedback): RoutingDecision {
        val decision = findRoutingRule(feedback)
        
        // If no rule matches, use intelligent default
        if (decision == null) {
            return RoutingDecision(
                team = determineTeamByCategory(feedback.category),
                priority = determinePriorityByUserRole(feedback.userRole),
                requiresReview = true // Flag for manual review
            )
        }
        
        return decision
    }
    
    private fun determineTeamByCategory(category: FeedbackCategory): String {
        return when (category) {
            FeedbackCategory.BUG -> "ENGINEERING"
            FeedbackCategory.FEATURE_REQUEST -> "PRODUCT"
            FeedbackCategory.BILLING -> "FINANCE"
            else -> "SUPPORT"
        }
    }
}
```

## Knowledge Base Content Becoming Outdated

### The Problem

Help articles become outdated when:
- UI changes but screenshots aren't updated
- Features are deprecated but articles remain
- API changes but documentation isn't updated
- Workflows change but step-by-step guides aren't revised

**Example**: Help article shows old UI with different button labels, confusing users.

### The Solution

**Content Versioning and Review Cadence**:

```kotlin
@Entity
@Table(name = "knowledge_base_articles")
data class KnowledgeBaseArticle(
    @Id
    val id: String = UUID.randomUUID().toString(),
    
    val title: String,
    val content: String,
    
    val lastReviewedAt: Instant?,
    val reviewDueDate: Instant, // Next review date
    
    val published: Boolean = false,
    val deprecated: Boolean = false,
    
    val applicableFeatures: List<String>, // Feature flags
    val applicableVersions: List<String> // App versions this applies to
)

@Service
class KnowledgeBaseReviewService {
    
    @Scheduled(cron = "0 0 9 * * MON") // Weekly review
    fun flagArticlesForReview() {
        val articles = articleRepository.findByReviewDueDateBefore(Instant.now())
        
        for (article in articles) {
            notificationService.notifyContentTeam(
                "Article needs review: ${article.title}",
                articleId = article.id
            )
        }
    }
    
    fun markArticleReviewed(articleId: String, reviewerId: String) {
        val article = articleRepository.findById(articleId)
        article.lastReviewedAt = Instant.now()
        article.reviewDueDate = Instant.now().plus(90, ChronoUnit.DAYS) // Review in 90 days
        article.reviewedBy = reviewerId
        articleRepository.save(article)
    }
}
```

**Automated Outdated Content Detection**:

```kotlin
@Service
class OutdatedContentDetectionService {
    
    fun detectOutdatedArticles(): List<OutdatedArticle> {
        val articles = articleRepository.findPublished()
        val outdated = mutableListOf<OutdatedArticle>()
        
        for (article in articles) {
            // Check if referenced features still exist
            val missingFeatures = article.applicableFeatures.filter { feature ->
                !featureFlagService.featureExists(feature)
            }
            
            if (missingFeatures.isNotEmpty()) {
                outdated.add(OutdatedArticle(
                    article = article,
                    reason = "References deprecated features: ${missingFeatures.joinToString()}",
                    severity = OutdatedSeverity.HIGH
                ))
            }
            
            // Check if screenshots are outdated (compare with current UI)
            if (article.hasScreenshots) {
                val screenshotAge = Duration.between(
                    article.screenshotUpdatedAt,
                    Instant.now()
                )
                
                if (screenshotAge.toDays() > 180) { // 6 months
                    outdated.add(OutdatedArticle(
                        article = article,
                        reason = "Screenshots may be outdated (>6 months old)",
                        severity = OutdatedSeverity.MEDIUM
                    ))
                }
            }
        }
        
        return outdated
    }
}
```

**User Feedback on Help Articles**:

```vue
<template>
  <div class="help-article">
    <article v-html="article.content" />
    
    <div class="article-feedback">
      <p>Was this article helpful?</p>
      <button @click="markHelpful">Yes</button>
      <button @click="markNotHelpful">No</button>
      
      <div v-if="showNotHelpfulForm">
        <textarea
          v-model="notHelpfulReason"
          placeholder="What was wrong or outdated?"
        />
        <button @click="submitFeedback">Submit</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const markNotHelpful = () => {
  showNotHelpfulForm.value = true
}

const submitFeedback = async () => {
  await helpApi.reportOutdated({
    articleId: article.id,
    reason: notHelpfulReason.value
  })
  
  // Trigger review process
}
</script>
```

## Support Tickets Created But No Notification

### The Problem

Tickets are created in external systems (Jira, Zendesk) but:
- Team members aren't notified
- No Slack/email alerts are sent
- Tickets sit unassigned
- SLAs are missed

**Example**: Critical bug report creates Jira ticket, but engineering team never receives notification.

### The Solution

**Notification on Ticket Creation**:

```kotlin
@Service
class SupportNotificationService {
    
    fun createTicket(feedback: Feedback): SupportTicket {
        val ticket = supportIntegrationService.createTicket(feedback)
        
        // Notify team immediately
        notifyTeam(
            team = ticket.assignedTeam,
            title = "New ${feedback.type} ticket: ${feedback.subject}",
            message = feedback.description,
            ticketUrl = ticket.url,
            priority = feedback.priority
        )
        
        return ticket
    }
    
    private fun notifyTeam(
        team: String,
        title: String,
        message: String,
        ticketUrl: String,
        priority: Priority
    ) {
        // Slack notification
        slackService.sendMessage(
            channel = getTeamSlackChannel(team),
            message = buildSlackMessage(title, message, ticketUrl, priority)
        )
        
        // Email notification for high priority
        if (priority >= Priority.HIGH) {
            emailService.sendToTeam(
                team = team,
                subject = "[${priority}] $title",
                body = buildEmailBody(message, ticketUrl)
            )
        }
    }
}
```

**Webhook Integration**:

```kotlin
@RestController
@RequestMapping("/webhooks")
class SupportWebhookController {
    
    @PostMapping("/jira/ticket-created")
    fun handleJiraTicketCreated(@RequestBody event: JiraWebhookEvent) {
        val ticket = event.issue
        
        // Notify assigned team
        if (ticket.assignee != null) {
            notificationService.notifyUser(
                userId = ticket.assignee,
                type = NotificationType.TICKET_ASSIGNED,
                title = "Ticket assigned: ${ticket.summary}",
                ticketUrl = ticket.url
            )
        } else {
            // No assignee - notify team
            notificationService.notifyTeam(
                team = determineTeamFromTicket(ticket),
                title = "Unassigned ticket: ${ticket.summary}",
                ticketUrl = ticket.url
            )
        }
    }
}
```

## Users Submitting Feedback But Receiving No Acknowledgment

### The Problem

Users submit feedback but:
- No confirmation message appears
- No ticket number is provided
- No email confirmation is sent
- Feedback feels like it goes into a void
- Users submit duplicate feedback thinking the first didn't go through

**Example**: User submits bug report, sees no confirmation, submits again 5 minutes later.

### The Solution

**Immediate UI Confirmation**:

```vue
<template>
  <div v-if="submissionState === 'submitting'" class="submitting">
    <Spinner /> Submitting...
  </div>
  
  <div v-else-if="submissionState === 'success'" class="success">
    <h3>Thank you for your feedback!</h3>
    <p>Ticket #{{ ticketNumber }}</p>
    <p>We'll respond within {{ estimatedResponseTime }}</p>
    <a :href="`/feedback/${feedbackId}/status`">Track status</a>
  </div>
  
  <div v-else-if="submissionState === 'error'" class="error">
    <p>Something went wrong. Please try again.</p>
    <button @click="retry">Retry</button>
  </div>
</template>

<script setup lang="ts">
const submitFeedback = async () => {
  submissionState.value = 'submitting'
  
  try {
    const response = await feedbackApi.submit(formData.value)
    ticketNumber.value = response.ticketNumber
    feedbackId.value = response.feedbackId
    submissionState.value = 'success'
    
    // Auto-close after 5 seconds
    setTimeout(() => {
      closeWidget()
    }, 5000)
  } catch (error) {
    submissionState.value = 'error'
  }
}
</script>
```

**Email Confirmation**:

```kotlin
@Service
class FeedbackConfirmationService {
    
    fun sendConfirmation(feedback: Feedback, ticket: SupportTicket) {
        emailService.send(
            to = feedback.userEmail,
            subject = "Feedback received: ${feedback.subject}",
            template = "feedback-confirmation",
            variables = mapOf(
                "ticketNumber" to ticket.number,
                "subject" to feedback.subject,
                "estimatedResponseTime" to determineResponseTime(feedback.priority),
                "statusUrl" to "/feedback/${feedback.id}/status"
            )
        )
    }
}
```

## NPS Survey Fatigue

### The Problem

Asking for NPS or CSAT feedback too frequently:
- Users ignore surveys
- Response rates drop
- Users become annoyed
- Survey data becomes less reliable

**Example**: NPS survey appears after every feature interaction, user starts dismissing without reading.

### The Solution

**Frequency Limits**:

```kotlin
@Entity
@Table(name = "user_survey_history")
data class UserSurveyHistory(
    @Id
    val id: String = UUID.randomUUID().toString(),
    
    val userId: String,
    val surveyType: SurveyType, // NPS, CSAT, CES
    
    val completedAt: Instant,
    val dismissedAt: Instant?
)

@Service
class SurveyFrequencyService {
    
    fun shouldShowSurvey(
        userId: String,
        surveyType: SurveyType,
        trigger: SurveyTrigger
    ): Boolean {
        val lastSurvey = surveyHistoryRepository.findLastSurvey(userId, surveyType)
        
        if (lastSurvey == null) {
            return true // Never shown before
        }
        
        val daysSinceLastSurvey = Duration.between(
            lastSurvey.completedAt ?: lastSurvey.dismissedAt,
            Instant.now()
        ).toDays()
        
        return when (surveyType) {
            SurveyType.NPS -> daysSinceLastSurvey >= 90 // Quarterly
            SurveyType.CSAT -> daysSinceLastSurvey >= 30 // Monthly
            SurveyType.CES -> daysSinceLastSurvey >= 7 // Weekly
        }
    }
}
```

**Contextual Triggers**:

```typescript
// Only show NPS after meaningful interactions
const shouldShowNPS = (userActions: UserAction[]) => {
  const meaningfulActions = userActions.filter(action =>
    ['feature_used', 'workflow_completed', 'support_resolved'].includes(action.type)
  )
  
  // Show NPS only after 3+ meaningful actions in last 30 days
  return meaningfulActions.length >= 3
}
```

## Context Not Captured

### The Problem

Users submit feedback saying "it's broken" with no context:
- No URL
- No browser information
- No steps to reproduce
- No screenshot
- Support team can't reproduce or fix the issue

**Example**: User reports "export doesn't work" but doesn't specify which export feature or what error they see.

### The Solution

**Automatic Context Capture**:

```typescript
// Always capture context automatically
const captureContext = () => {
  return {
    url: window.location.href,
    route: currentRoute.path,
    userAgent: navigator.userAgent,
    browser: detectBrowser(),
    screenResolution: `${window.screen.width}x${window.screen.height}`,
    consoleErrors: captureConsoleErrors(),
    networkErrors: captureNetworkErrors(),
    timestamp: new Date().toISOString()
  }
}

// Include context in every feedback submission
const submitFeedback = async (userInput: FeedbackInput) => {
  await feedbackApi.submit({
    ...userInput,
    context: captureContext() // Always included
  })
}
```

**Required Context Fields**:

```vue
<template>
  <div class="feedback-form">
    <div class="context-preview">
      <h4>We'll automatically include:</h4>
      <ul>
        <li>Current page: {{ currentUrl }}</li>
        <li>Browser: {{ browserInfo }}</li>
        <li>User: {{ userEmail }}</li>
      </ul>
    </div>
    
    <!-- User only needs to provide subject and description -->
    <input v-model="subject" placeholder="What happened?" required />
    <textarea v-model="description" placeholder="Describe the issue" required />
  </div>
</template>
```

## Multi-Tenant Feedback Leaking

### The Problem

Feedback or support tickets from one tenant are visible to another tenant:
- Privacy violation
- Data breach risk
- Compliance issues (SOC 2, GDPR)
- User trust erosion

**Example**: Tenant A's admin sees Tenant B's support ticket in the feedback status page.

### The Solution

**Tenant Isolation at Database Level**:

```kotlin
@Repository
interface FeedbackRepository : JpaRepository<Feedback, String> {
    
    // Always filter by tenantId
    @Query("""
        SELECT f FROM Feedback f 
        WHERE f.id = :id 
        AND f.tenantId = :tenantId
    """)
    fun findByIdAndTenantId(id: String, tenantId: String): Feedback?
    
    fun findByTenantId(tenantId: String): List<Feedback>
    
    // Prevent cross-tenant queries
    @Query("""
        SELECT f FROM Feedback f 
        WHERE f.tenantId = :tenantId
        ORDER BY f.createdAt DESC
    """)
    fun findAllByTenantId(tenantId: String): List<Feedback>
}
```

**API-Level Tenant Validation**:

```kotlin
@RestController
@RequestMapping("/api/v1/feedback")
class FeedbackController {
    
    @GetMapping("/{feedbackId}")
    fun getFeedback(
        @PathVariable feedbackId: String,
        @AuthenticationPrincipal user: UserPrincipal
    ): ResponseEntity<FeedbackResponse> {
        val feedback = feedbackRepository.findByIdAndTenantId(
            feedbackId,
            user.tenantId // Enforce tenant isolation
        ) ?: throw FeedbackNotFoundException()
        
        return ResponseEntity.ok(FeedbackResponse.from(feedback))
    }
    
    @GetMapping
    fun listFeedback(
        @AuthenticationPrincipal user: UserPrincipal
    ): ResponseEntity<List<FeedbackResponse>> {
        // Only return feedback for user's tenant
        val feedbacks = feedbackRepository.findByTenantId(user.tenantId)
        return ResponseEntity.ok(feedbacks.map { FeedbackResponse.from(it) })
    }
}
```

**Support System Integration with Tenant Isolation**:

```kotlin
@Service
class SupportIntegrationService {
    
    fun createTicket(feedback: Feedback): SupportTicket {
        val ticket = jiraClient.createIssue(
            projectKey = "SUPPORT",
            summary = feedback.subject,
            description = feedback.description,
            customFields = mapOf(
                "customfield_10001" to feedback.tenantId, // Tenant ID
                "customfield_10002" to "CONFIDENTIAL" // Mark as confidential
            )
        )
        
        // Set security level to tenant-specific
        jiraClient.setSecurityLevel(ticket.key, feedback.tenantId)
        
        return SupportTicket.from(ticket)
    }
}
```

**Frontend Tenant Validation**:

```typescript
// Always include tenantId in API requests
const feedbackApi = {
  submit: async (feedback: FeedbackPayload) => {
    return await api.post('/api/v1/feedback', {
      ...feedback,
      tenantId: currentUser.tenantId // Always include
    })
  },
  
  getStatus: async (feedbackId: string) => {
    // API will automatically filter by current user's tenantId
    return await api.get(`/api/v1/feedback/${feedbackId}`)
  }
}
```
