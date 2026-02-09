# Best Practices: Feedback & Support

## Contents

- [Make Feedback Easy](#make-feedback-easy)
- [Capture Context Automatically](#capture-context-automatically)
- [Acknowledge Every Submission](#acknowledge-every-submission)
- [Close the Loop](#close-the-loop)
- [Contextual Help Over Generic FAQs](#contextual-help-over-generic-faqs)
- ["What's New" Changelog](#whats-new-changelog)
- [Stack-Specific Guidance](#stack-specific-guidance)
- [Accessibility Considerations](#accessibility-considerations)
- [Information Architecture](#information-architecture)

## Make Feedback Easy

### Always Accessible

Feedback mechanisms should be accessible from anywhere in the application with minimal friction:

**Best Practice**: Provide a persistent feedback button or widget that's always visible (typically in the header, footer, or as a floating button).

```vue
<!-- Vue 3: Persistent feedback button -->
<template>
  <button
    class="feedback-button"
    @click="openFeedbackWidget"
    aria-label="Submit feedback"
  >
    💬 Feedback
  </button>
</template>

<script setup lang="ts">
const openFeedbackWidget = () => {
  // Open feedback widget
}
</script>
```

```tsx
// React: Persistent feedback button
export function FeedbackButton() {
  return (
    <button
      className="feedback-button"
      onClick={() => setShowWidget(true)}
      aria-label="Submit feedback"
    >
      💬 Feedback
    </button>
  )
}
```

### Minimal Friction

**Best Practice**: Limit feedback submission to 1-2 clicks. Pre-fill as much as possible (user context, page URL, browser info).

```typescript
// Pre-fill context automatically
const feedbackContext = {
  userId: currentUser.id,
  email: currentUser.email,
  tenantId: currentUser.tenantId,
  url: window.location.href,
  route: currentRoute.name,
  browser: navigator.userAgent,
  timestamp: new Date().toISOString()
}

// User only needs to provide subject and description
```

### Keyboard Shortcut

**Best Practice**: Provide a keyboard shortcut (e.g., `Cmd/Ctrl + /`) to open feedback widget for power users.

```typescript
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === '/') {
      e.preventDefault()
      openFeedbackWidget()
    }
  }
  
  window.addEventListener('keydown', handleKeyPress)
  return () => window.removeEventListener('keydown', handleKeyPress)
}, [])
```

## Capture Context Automatically

### Don't Make Users Describe Where They Were

**Best Practice**: Automatically capture:
- Current page URL and route
- User information (ID, email, role, tenant)
- Browser and device information
- Console errors (if any)
- Network errors (if any)
- Screenshot (optional, user-initiated)

```kotlin
// Spring Boot: Automatic context capture
data class FeedbackContext(
    val url: String,
    val routeName: String?,
    val userId: String,
    val tenantId: String,
    val userRole: String,
    val browser: String,
    val userAgent: String,
    val screenResolution: String?,
    val consoleErrors: List<String>? = null,
    val networkErrors: List<String>? = null,
    val screenshotUrl: String? = null,
    val sessionReplayId: String? = null,
    val timestamp: Instant = Instant.now()
)

@Service
class FeedbackContextService {
    fun captureContext(request: HttpServletRequest, user: User): FeedbackContext {
        return FeedbackContext(
            url = request.requestURI + if (request.queryString != null) "?${request.queryString}" else "",
            routeName = extractRouteName(request),
            userId = user.id,
            tenantId = user.tenantId,
            userRole = user.role.name,
            browser = extractBrowser(request.getHeader("User-Agent")),
            userAgent = request.getHeader("User-Agent"),
            screenResolution = request.getHeader("X-Screen-Resolution"),
            consoleErrors = extractConsoleErrors(request),
            networkErrors = extractNetworkErrors(request)
        )
    }
}
```

### Screenshot Capture

**Best Practice**: Offer screenshot capture as an option, but don't require it. Use libraries like `html2canvas` for client-side capture.

```typescript
import html2canvas from 'html2canvas'

export async function captureScreenshot(): Promise<string> {
  const canvas = await html2canvas(document.body, {
    useCORS: true,
    logging: false,
    scale: 0.5, // Reduce file size
    backgroundColor: '#ffffff'
  })
  
  return canvas.toDataURL('image/png')
}
```

## Acknowledge Every Submission

### Instant Confirmation

**Best Practice**: Show immediate confirmation when feedback is submitted, even before server response.

```vue
<template>
  <div v-if="submitted" class="feedback-confirmation">
    <h3>Thank you for your feedback!</h3>
    <p>Ticket #{{ ticketNumber }}</p>
    <p>We'll respond within {{ estimatedResponseTime }}</p>
  </div>
</template>
```

### Ticket Number

**Best Practice**: Always provide a ticket number or reference ID so users can track their submission.

```kotlin
@PostMapping("/api/v1/feedback")
fun submitFeedback(@RequestBody request: FeedbackRequest): ResponseEntity<FeedbackResponse> {
    val feedback = feedbackService.createFeedback(request)
    val ticket = supportIntegrationService.createTicket(feedback)
    
    return ResponseEntity.ok(
        FeedbackResponse(
            feedbackId = feedback.id,
            ticketNumber = ticket.number, // Always include
            status = "submitted",
            estimatedResponseTime = "4 hours",
            trackingUrl = "/feedback/${feedback.id}/status"
        )
    )
}
```

### Expected Response Time

**Best Practice**: Set clear expectations for response time based on priority and support tier.

```typescript
const getEstimatedResponseTime = (priority: Priority, tier: SupportTier): string => {
  if (tier === 'enterprise') {
    return priority === 'critical' ? '1 hour' : '4 hours'
  } else if (tier === 'pro') {
    return priority === 'critical' ? '4 hours' : '24 hours'
  } else {
    return '48 hours'
  }
}
```

## Close the Loop

### Notify When Resolved

**Best Practice**: Notify users when their feedback is acted upon—bug fixed, feature shipped, or question answered.

```kotlin
@Service
class FeedbackNotificationService {
    
    fun notifyResolution(feedback: Feedback, resolution: String) {
        notificationService.send(
            userId = feedback.userId,
            type = NotificationType.FEEDBACK_RESOLVED,
            title = "Your feedback has been resolved",
            message = "Ticket #${feedback.ticketId}: $resolution",
            actionUrl = "/feedback/${feedback.id}/status"
        )
    }
    
    fun notifyFeatureShipped(feedback: Feedback, featureName: String) {
        if (feedback.type == FeedbackType.FEATURE_REQUEST) {
            notificationService.send(
                userId = feedback.userId,
                type = NotificationType.FEATURE_SHIPPED,
                title = "Feature you requested is now available",
                message = "$featureName is now live!",
                actionUrl = "/features/$featureName"
            )
        }
    }
}
```

### Status Page

**Best Practice**: Provide a status page where users can check the status of their feedback submissions.

```vue
<template>
  <div class="feedback-status-page">
    <h1>Your Feedback</h1>
    <div v-for="feedback in feedbackList" :key="feedback.id" class="feedback-item">
      <h3>{{ feedback.subject }}</h3>
      <p>Ticket #{{ feedback.ticketNumber }}</p>
      <StatusBadge :status="feedback.status" />
      <p v-if="feedback.resolution">{{ feedback.resolution }}</p>
      <p>Submitted {{ formatDate(feedback.createdAt) }}</p>
    </div>
  </div>
</template>
```

## Contextual Help Over Generic FAQs

### Show Relevant Help Based on Current Page

**Best Practice**: Display help articles relevant to the current page or action, rather than forcing users to search.

```vue
<template>
  <div class="contextual-help">
    <HelpPanel v-if="relevantArticles.length > 0">
      <h3>Related Help</h3>
      <ArticleList :articles="relevantArticles" />
    </HelpPanel>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useHelpService } from '@/composables/useHelpService'

const route = useRoute()
const helpService = useHelpService()

const relevantArticles = computed(() => {
  return helpService.findContextualArticles({
    route: route.path,
    userRole: currentUser.role,
    featureFlags: currentUser.featureFlags
  })
})
</script>
```

### Contextual Tooltips

**Best Practice**: Provide tooltips on complex UI elements that link to relevant help articles.

```tsx
// React: Contextual tooltip with help link
export function HelpTooltip({ articleId, placement }: HelpTooltipProps) {
  return (
    <Tooltip title="Learn more" placement={placement}>
      <IconButton
        size="small"
        onClick={() => openHelpArticle(articleId)}
        aria-label="Help"
      >
        <HelpIcon />
      </IconButton>
    </Tooltip>
  )
}
```

### Smart Help Suggestions

**Best Practice**: Analyze user behavior to suggest help articles proactively (e.g., if user hovers over a feature for 5+ seconds without interacting).

```typescript
// Suggest help if user seems stuck
let hoverTimer: NodeJS.Timeout

element.addEventListener('mouseenter', () => {
  hoverTimer = setTimeout(() => {
    if (!hasInteracted) {
      showHelpSuggestion('This feature helps you...')
    }
  }, 5000) // 5 seconds
})

element.addEventListener('mouseleave', () => {
  clearTimeout(hoverTimer)
})
```

## "What's New" Changelog

### In-App Changelog

**Best Practice**: Display "What's New" content in-app, not just via email. Show changelog entries based on:
- Feature flags (only show if feature is enabled)
- User role (show relevant features)
- Dismissal state (don't show if user dismissed)

```vue
<template>
  <ChangelogModal
    v-if="hasNewFeatures && !dismissed"
    :entries="relevantChangelogEntries"
    @dismiss="handleDismiss"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChangelog } from '@/composables/useChangelog'

const { changelogEntries, dismissedEntries } = useChangelog()

const relevantChangelogEntries = computed(() => {
  return changelogEntries.value.filter(entry => 
    entry.featureFlags.every(flag => currentUser.featureFlags.includes(flag)) &&
    !dismissedEntries.value.includes(entry.id)
  )
})
</script>
```

### Feature Announcements

**Best Practice**: Announce new features contextually when users first encounter them.

```typescript
// Show feature announcement on first use
const hasSeenFeature = localStorage.getItem(`feature-seen-${featureId}`)

if (!hasSeenFeature) {
  showFeatureAnnouncement({
    title: 'New: Bulk Export',
    description: 'You can now export multiple invoices at once',
    featureId: 'bulk-export',
    onDismiss: () => {
      localStorage.setItem(`feature-seen-${featureId}`, 'true')
    }
  })
}
```

## Stack-Specific Guidance

### Vue 3

**Feedback Composable**:

```typescript
// composables/useFeedback.ts
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

export function useFeedback() {
  const route = useRoute()
  const userStore = useUserStore()
  const isSubmitting = ref(false)
  
  const submitFeedback = async (feedback: FeedbackPayload) => {
    isSubmitting.value = true
    
    try {
      const context = {
        user: {
          userId: userStore.userId,
          tenantId: userStore.tenantId,
          role: userStore.role
        },
        page: {
          url: route.fullPath,
          routeName: route.name
        },
        browser: navigator.userAgent
      }
      
      const response = await feedbackApi.submit({
        ...feedback,
        context
      })
      
      return response
    } finally {
      isSubmitting.value = false
    }
  }
  
  return {
    submitFeedback,
    isSubmitting
  }
}
```

**Help Panel Component**:

```vue
<!-- components/HelpPanel.vue -->
<template>
  <Drawer
    :model-value="isOpen"
    @update:model-value="$emit('update:isOpen', $event)"
    anchor="right"
    width="400"
  >
    <div class="help-panel">
      <HelpSearch @search="handleSearch" />
      <HelpArticleList :articles="articles" />
      <ContextualHelp :route="currentRoute" />
    </div>
  </Drawer>
</template>
```

### React

**Feedback Context Provider**:

```tsx
// contexts/FeedbackContext.tsx
const FeedbackContext = createContext<FeedbackContextType | null>(null)

export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const [showWidget, setShowWidget] = useState(false)
  const location = useLocation()
  const user = useUser()
  
  const submitFeedback = async (feedback: FeedbackPayload) => {
    const context = {
      user: {
        userId: user.id,
        tenantId: user.tenantId,
        role: user.role
      },
      page: {
        url: location.pathname + location.search
      },
      browser: navigator.userAgent
    }
    
    return await feedbackApi.submit({ ...feedback, context })
  }
  
  return (
    <FeedbackContext.Provider value={{
      showWidget,
      setShowWidget,
      submitFeedback
    }}>
      {children}
    </FeedbackContext.Provider>
  )
}
```

### Spring Boot

**Feedback REST API**:

```kotlin
@RestController
@RequestMapping("/api/v1/feedback")
class FeedbackController(
    private val feedbackService: FeedbackService
) {
    
    @PostMapping
    fun submitFeedback(
        @RequestBody request: FeedbackRequest,
        @AuthenticationPrincipal user: UserPrincipal,
        httpRequest: HttpServletRequest
    ): ResponseEntity<FeedbackResponse> {
        val context = feedbackContextService.captureContext(httpRequest, user.toUser())
        
        val feedback = feedbackService.createFeedback(
            userId = user.id,
            tenantId = user.tenantId,
            type = request.type,
            subject = request.subject,
            description = request.description,
            context = context,
            attachments = request.attachments
        )
        
        val ticket = supportIntegrationService.createTicket(feedback)
        
        return ResponseEntity.ok(
            FeedbackResponse(
                feedbackId = feedback.id,
                ticketNumber = ticket.number,
                status = "submitted",
                estimatedResponseTime = determineResponseTime(user.tier, feedback.priority)
            )
        )
    }
}
```

**Jira/Zendesk Integration Service**:

```kotlin
@Service
class SupportIntegrationService(
    private val jiraClient: JiraClient,
    private val zendeskClient: ZendeskClient
) {
    
    fun createTicket(feedback: Feedback): SupportTicket {
        return when (supportSystem) {
            SupportSystem.JIRA -> createJiraTicket(feedback)
            SupportSystem.ZENDESK -> createZendeskTicket(feedback)
        }
    }
    
    private fun createJiraTicket(feedback: Feedback): SupportTicket {
        val issue = jiraClient.createIssue(
            projectKey = "SUPPORT",
            issueType = mapFeedbackTypeToIssueType(feedback.type),
            summary = feedback.subject,
            description = buildDescription(feedback),
            customFields = mapOf(
                "customfield_10001" to feedback.tenantId
            )
        )
        
        return SupportTicket(
            number = issue.key,
            url = issue.self,
            status = issue.status.name
        )
    }
}
```

## Accessibility Considerations

### Keyboard Accessibility

**Best Practice**: Feedback widgets must be fully keyboard accessible.

```vue
<template>
  <div
    class="feedback-widget"
    role="dialog"
    aria-labelledby="feedback-title"
    @keydown.esc="close"
  >
    <h2 id="feedback-title">Submit Feedback</h2>
    <form @submit.prevent="handleSubmit">
      <!-- Form fields with proper labels -->
      <button type="submit">Submit</button>
      <button type="button" @click="close">Cancel</button>
    </form>
  </div>
</template>
```

### Screen Reader Compatibility

**Best Practice**: Use proper ARIA labels and live regions for status updates.

```vue
<template>
  <div
    aria-live="polite"
    aria-atomic="true"
    class="sr-only"
  >
    {{ statusMessage }}
  </div>
</template>
```

### Not Overlay Critical Content

**Best Practice**: Ensure feedback widgets don't cover critical UI elements. Use proper z-index management and positioning.

```css
.feedback-widget {
  z-index: 1000; /* Below modals (z-index: 2000) */
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 400px;
}

.modal {
  z-index: 2000; /* Above feedback widget */
}
```

## Information Architecture

### Searchable Help

**Best Practice**: Implement full-text search with relevance ranking, typo tolerance, and category filtering.

```kotlin
@Service
class HelpSearchService {
    
    fun search(query: String, filters: SearchFilters): List<SearchResult> {
        val results = elasticsearchClient.search(
            index = "knowledge_base",
            query = buildQuery(query, filters),
            highlight = true
        )
        
        return results.map { hit ->
            SearchResult(
                article = hit.document,
                relevanceScore = hit.score,
                matchedSnippets = hit.highlights
            )
        }
    }
}
```

### Good Information Architecture

**Best Practice**: Organize help content hierarchically:
- **Categories**: Billing, Integrations, API, etc.
- **Topics**: Within each category
- **Articles**: Individual help articles
- **Tags**: For cross-cutting topics

```kotlin
@Entity
data class HelpCategory(
    val id: String,
    val name: String,
    val slug: String,
    val description: String,
    val order: Int,
    val topics: List<HelpTopic>
)

@Entity
data class HelpTopic(
    val id: String,
    val categoryId: String,
    val name: String,
    val slug: String,
    val articles: List<HelpArticle>
)
```

### Related Articles

**Best Practice**: Show related articles at the bottom of each help article to guide users to additional resources.

```vue
<template>
  <div class="help-article">
    <article v-html="article.content" />
    <RelatedArticles :article-id="article.id" />
  </div>
</template>
```
