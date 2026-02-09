# Notifications -- Architecture

## Contents

- [Notification Service Design](#notification-service-design)
- [Channel Abstraction](#channel-abstraction)
- [Template Engine](#template-engine)
- [Delivery Pipeline](#delivery-pipeline)
- [Preference Storage](#preference-storage)
- [Real-Time Delivery](#real-time-delivery)
- [Queuing and Retry](#queuing-and-retry)
- [Multi-Tenant Isolation](#multi-tenant-isolation)
- [Notification Inbox Architecture](#notification-inbox-architecture)
- [Email Deliverability](#email-deliverability)

## Notification Service Design

### Centralized Service Pattern

A centralized notification service acts as a single point of entry for all notification requests. This pattern provides:

**Benefits**:
- Consistent delivery logic across all channels
- Centralized preference management
- Unified monitoring and observability
- Easier to maintain and evolve

**Architecture**:
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Domain   │────▶│  Notification    │────▶│  Channels   │
│  Services  │     │     Service       │     │ (Email/Push)│
└─────────────┘     └──────────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Preferences │
                    │   Storage   │
                    └─────────────┘
```

**Spring Boot Example**:
```kotlin
@Service
class NotificationService(
    private val preferenceRepository: PreferenceRepository,
    private val channelRegistry: ChannelRegistry,
    private val templateEngine: TemplateEngine
) {
    suspend fun sendNotification(request: NotificationRequest) {
        val preferences = preferenceRepository.getUserPreferences(request.userId)
        
        // Check if user has opted out
        if (!preferences.isChannelEnabled(request.channel)) {
            return
        }
        
        // Check quiet hours
        if (preferences.isInQuietHours() && !request.isCritical) {
            scheduleForLater(request)
            return
        }
        
        // Render template
        val rendered = templateEngine.render(request.templateId, request.data)
        
        // Dispatch to channel
        val channel = channelRegistry.getChannel(request.channel)
        channel.send(rendered, request.recipient)
    }
}
```

### Distributed Pattern

In a distributed pattern, each service sends notifications directly to channels. This is simpler but harder to manage at scale.

**When to Use**:
- Small applications with few notification types
- Services that need direct control over delivery
- Microservices with strong domain boundaries

**Trade-offs**:
- Harder to enforce preferences consistently
- Duplicated delivery logic
- More complex monitoring

## Channel Abstraction

Abstract notification channels behind a common interface to enable channel-agnostic notification logic.

### Channel Interface

```kotlin
interface NotificationChannel {
    suspend fun send(notification: RenderedNotification): DeliveryResult
    fun supports(channelType: ChannelType): Boolean
    fun getCapabilities(): ChannelCapabilities
}

data class RenderedNotification(
    val subject: String?,
    val body: String,
    val recipient: Recipient,
    val metadata: NotificationMetadata
)

data class ChannelCapabilities(
    val supportsRichContent: Boolean,
    val supportsAttachments: Boolean,
    val maxLength: Int?,
    val deliverySpeed: DeliverySpeed
)
```

### Channel Implementations

**Email Channel**:
```kotlin
@Component
class EmailChannel(
    private val emailClient: EmailClient
) : NotificationChannel {
    override suspend fun send(notification: RenderedNotification): DeliveryResult {
        val email = EmailMessage(
            to = notification.recipient.email,
            subject = notification.subject ?: "Notification",
            htmlBody = notification.body,
            textBody = extractPlainText(notification.body)
        )
        return emailClient.send(email)
    }
    
    override fun supports(channelType: ChannelType) = channelType == ChannelType.EMAIL
}
```

**Push Notification Channel**:
```kotlin
@Component
class PushChannel(
    private val pushService: PushService
) : NotificationChannel {
    override suspend fun send(notification: RenderedNotification): DeliveryResult {
        val push = PushMessage(
            deviceToken = notification.recipient.deviceToken,
            title = notification.subject ?: "Notification",
            body = truncate(notification.body, 200),
            data = notification.metadata.toMap()
        )
        return pushService.send(push)
    }
    
    override fun supports(channelType: ChannelType) = channelType == ChannelType.PUSH
}
```

**In-App Channel**:
```kotlin
@Component
class InAppChannel(
    private val notificationRepository: NotificationRepository,
    private val realTimeService: RealTimeService
) : NotificationChannel {
    override suspend fun send(notification: RenderedNotification): DeliveryResult {
        val inAppNotification = InAppNotification(
            userId = notification.recipient.userId,
            title = notification.subject,
            body = notification.body,
            type = notification.metadata.type,
            actionUrl = notification.metadata.actionUrl,
            createdAt = Instant.now()
        )
        
        // Persist to database
        val saved = notificationRepository.save(inAppNotification)
        
        // Push via WebSocket/SSE
        realTimeService.pushToUser(notification.recipient.userId, saved)
        
        return DeliveryResult.success(saved.id)
    }
}
```

## Template Engine

Templates enable parameterized notification content that can be rendered differently per channel.

### Template Structure

```kotlin
data class NotificationTemplate(
    val id: String,
    val name: String,
    val channels: Map<ChannelType, ChannelTemplate>,
    val variables: List<TemplateVariable>
)

data class ChannelTemplate(
    val subject: String?,
    val body: String,
    val variables: List<String>
)

// Example template
val orderConfirmationTemplate = NotificationTemplate(
    id = "order-confirmed",
    name = "Order Confirmation",
    channels = mapOf(
        ChannelType.EMAIL to ChannelTemplate(
            subject = "Order #{{orderNumber}} Confirmed",
            body = """
                <h1>Thank you for your order!</h1>
                <p>Your order #{{orderNumber}} for {{orderTotal}} has been confirmed.</p>
                <p>Estimated delivery: {{deliveryDate}}</p>
                <a href="{{orderUrl}}">View Order</a>
            """,
            variables = listOf("orderNumber", "orderTotal", "deliveryDate", "orderUrl")
        ),
        ChannelType.PUSH to ChannelTemplate(
            subject = "Order Confirmed",
            body = "Order #{{orderNumber}} for {{orderTotal}} confirmed",
            variables = listOf("orderNumber", "orderTotal")
        )
    ),
    variables = listOf("orderNumber", "orderTotal", "deliveryDate", "orderUrl")
)
```

### Template Rendering

```kotlin
@Service
class TemplateEngine {
    fun render(
        templateId: String,
        channel: ChannelType,
        data: Map<String, Any>
    ): RenderedNotification {
        val template = templateRepository.findById(templateId)
        val channelTemplate = template.channels[channel] 
            ?: throw IllegalArgumentException("Template not available for channel $channel")
        
        val subject = channelTemplate.subject?.let { renderTemplate(it, data) }
        val body = renderTemplate(channelTemplate.body, data)
        
        return RenderedNotification(
            subject = subject,
            body = body,
            recipient = Recipient.fromData(data),
            metadata = NotificationMetadata.fromData(data)
        )
    }
    
    private fun renderTemplate(template: String, data: Map<String, Any>): String {
        var rendered = template
        data.forEach { (key, value) ->
            rendered = rendered.replace("{{$key}}", value.toString())
        }
        return rendered
    }
}
```

### Spring Boot Template Integration

Spring Boot supports multiple template engines:

**Thymeleaf** (for HTML emails):
```kotlin
@Service
class ThymeleafTemplateEngine(
    private val templateEngine: org.thymeleaf.TemplateEngine
) {
    fun renderEmail(templateName: String, variables: Map<String, Any>): String {
        val context = Context().apply {
            variables.forEach { (key, value) -> setVariable(key, value) }
        }
        return templateEngine.process("emails/$templateName", context)
    }
}
```

**Freemarker** (alternative):
```kotlin
@Service
class FreemarkerTemplateEngine(
    private val configuration: freemarker.template.Configuration
) {
    fun render(templateName: String, variables: Map<String, Any>): String {
        val template = configuration.getTemplate("$templateName.ftl")
        return template.process(variables, StringWriter()).toString()
    }
}
```

## Delivery Pipeline

The delivery pipeline processes notifications from event to delivery:

```
Event → Enrich → Resolve Preferences → Render → Dispatch → Track
```

### Pipeline Stages

**1. Event Reception**:
```kotlin
@EventListener
fun handleOrderConfirmed(event: OrderConfirmedEvent) {
    notificationService.sendNotification(
        NotificationRequest(
            userId = event.userId,
            templateId = "order-confirmed",
            channel = ChannelType.EMAIL,
            data = mapOf(
                "orderNumber" to event.orderNumber,
                "orderTotal" to event.total,
                "deliveryDate" to event.estimatedDelivery
            )
        )
    )
}
```

**2. Enrichment**:
```kotlin
fun enrich(request: NotificationRequest): EnrichedRequest {
    val user = userService.getUser(request.userId)
    val preferences = preferenceRepository.getPreferences(request.userId)
    
    return EnrichedRequest(
        request = request,
        user = user,
        preferences = preferences,
        timezone = user.timezone,
        locale = user.locale
    )
}
```

**3. Preference Resolution**:
```kotlin
fun resolvePreferences(enriched: EnrichedRequest): ResolvedRequest? {
    val prefs = enriched.preferences
    
    // Check opt-out
    if (!prefs.isChannelEnabled(enriched.request.channel)) {
        return null // User opted out
    }
    
    // Check quiet hours
    if (prefs.isInQuietHours(enriched.timezone) && !enriched.request.isCritical) {
        return enriched.request.copy(scheduledFor = calculateNextAllowedTime(prefs, enriched.timezone))
    }
    
    // Check frequency cap
    if (hasExceededFrequencyCap(enriched.request.userId, enriched.request.channel)) {
        return null // Rate limited
    }
    
    return ResolvedRequest(enriched.request, prefs)
}
```

**4. Rendering**:
```kotlin
fun render(resolved: ResolvedRequest): RenderedNotification {
    return templateEngine.render(
        templateId = resolved.request.templateId,
        channel = resolved.request.channel,
        data = resolved.request.data,
        locale = resolved.user.locale
    )
}
```

**5. Dispatch**:
```kotlin
fun dispatch(rendered: RenderedNotification): DeliveryResult {
    val channel = channelRegistry.getChannel(rendered.channel)
    return channel.send(rendered)
}
```

**6. Tracking**:
```kotlin
fun track(result: DeliveryResult, notification: RenderedNotification) {
    notificationRepository.saveDelivery(
        DeliveryRecord(
            notificationId = result.notificationId,
            channel = notification.channel,
            status = result.status,
            deliveredAt = result.deliveredAt,
            error = result.error
        )
    )
    
    // Update metrics
    metrics.increment("notifications.sent", "channel:${notification.channel}")
    if (result.status == DeliveryStatus.FAILED) {
        metrics.increment("notifications.failed", "channel:${notification.channel}")
    }
}
```

## Preference Storage

Store user preferences in a way that supports fast lookups and flexible querying.

### Data Model

```kotlin
@Entity
data class NotificationPreference(
    @Id val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val channel: ChannelType,
    val notificationType: NotificationType,
    val enabled: Boolean = true,
    val quietHoursStart: LocalTime? = null,
    val quietHoursEnd: LocalTime? = null,
    val frequencyCap: Int? = null, // max per day
    val timezone: String = "UTC"
)

@Entity
data class UserNotificationSettings(
    @Id val userId: String,
    val defaultChannel: ChannelType = ChannelType.EMAIL,
    val digestMode: Boolean = false,
    val digestFrequency: DigestFrequency = DigestFrequency.DAILY
)
```

### Preference Lookup

```kotlin
@Repository
interface PreferenceRepository : JpaRepository<NotificationPreference, String> {
    fun findByUserId(userId: String): List<NotificationPreference>
    
    @Query("SELECT p FROM NotificationPreference p WHERE p.userId = :userId AND p.channel = :channel AND p.enabled = true")
    fun findEnabledPreference(userId: String, channel: ChannelType): NotificationPreference?
    
    fun existsByUserIdAndChannelAndNotificationTypeAndEnabled(
        userId: String,
        channel: ChannelType,
        type: NotificationType,
        enabled: Boolean
    ): Boolean
}
```

### Preference Service

```kotlin
@Service
class PreferenceService(
    private val preferenceRepository: PreferenceRepository
) {
    fun getUserPreferences(userId: String): UserPreferences {
        val prefs = preferenceRepository.findByUserId(userId)
        return UserPreferences.fromEntities(prefs)
    }
    
    fun isChannelEnabled(userId: String, channel: ChannelType): Boolean {
        return preferenceRepository
            .findEnabledPreference(userId, channel) != null
    }
    
    fun isInQuietHours(userId: String, timezone: String): Boolean {
        val prefs = preferenceRepository.findByUserId(userId)
        val userPref = prefs.firstOrNull() ?: return false
        
        if (userPref.quietHoursStart == null) return false
        
        val now = LocalTime.now(ZoneId.of(userPref.timezone))
        return now.isAfter(userPref.quietHoursStart) && 
               now.isBefore(userPref.quietHoursEnd ?: LocalTime.MAX)
    }
}
```

## Real-Time Delivery

For in-app notifications, choose a real-time delivery mechanism.

### WebSocket Approach

**Backend (Spring Boot)**:
```kotlin
@Configuration
@EnableWebSocket
class WebSocketConfig : WebSocketConfigurer {
    override fun registerWebSocketHandlers(registry: WebSocketHandlerRegistry) {
        registry.addHandler(NotificationWebSocketHandler(), "/ws/notifications")
            .setAllowedOrigins("*")
    }
}

@Component
class NotificationWebSocketHandler : TextWebSocketHandler() {
    private val sessions = ConcurrentHashMap<String, WebSocketSession>()
    
    override fun afterConnectionEstablished(session: WebSocketSession) {
        val userId = extractUserId(session)
        sessions[userId] = session
    }
    
    fun sendNotification(userId: String, notification: InAppNotification) {
        sessions[userId]?.sendMessage(
            TextMessage(JacksonObjectMapper().writeValueAsString(notification))
        )
    }
}
```

**Frontend (Vue 3)**:
```typescript
// composables/useNotifications.ts
export function useNotifications() {
  const ws = ref<WebSocket | null>(null)
  const notifications = ref<Notification[]>([])
  
  function connect(userId: string) {
    ws.value = new WebSocket(`wss://api.example.com/ws/notifications?userId=${userId}`)
    
    ws.value.onmessage = (event) => {
      const notification = JSON.parse(event.data)
      notifications.value.unshift(notification)
      showToast(notification)
    }
    
    ws.value.onclose = () => {
      // Reconnect with exponential backoff
      setTimeout(() => connect(userId), 5000)
    }
  }
  
  return { connect, notifications }
}
```

### Server-Sent Events (SSE) Approach

**Backend**:
```kotlin
@RestController
class NotificationSSEController(
    private val notificationService: NotificationService
) {
    @GetMapping("/api/notifications/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
    fun streamNotifications(
        @RequestParam userId: String,
        response: HttpServletResponse
    ): SseEmitter {
        val emitter = SseEmitter(Long.MAX_VALUE)
        notificationService.subscribe(userId) { notification ->
            emitter.send(SseEmitter.event()
                .data(notification)
                .name("notification"))
        }
        return emitter
    }
}
```

**Frontend (React)**:
```typescript
function useNotificationStream(userId: string) {
  useEffect(() => {
    const eventSource = new EventSource(`/api/notifications/stream?userId=${userId}`)
    
    eventSource.addEventListener('notification', (event) => {
      const notification = JSON.parse(event.data)
      addNotification(notification)
    })
    
    return () => eventSource.close()
  }, [userId])
}
```

### Polling Approach

Simple but less efficient:

```typescript
// Poll every 30 seconds
setInterval(async () => {
  const response = await fetch('/api/notifications/unread')
  const notifications = await response.json()
  updateNotifications(notifications)
}, 30000)
```

**When to Use**:
- WebSocket/SSE not available
- Low notification frequency
- Simple implementation needed

## Queuing and Retry

Use message queues for reliable, asynchronous notification delivery.

### Kafka Integration

```kotlin
@Service
class NotificationProducer(
    private val kafkaTemplate: KafkaTemplate<String, NotificationEvent>
) {
    fun sendNotification(event: NotificationEvent) {
        kafkaTemplate.send("notifications", event.userId, event)
    }
}

@KafkaListener(topics = ["notifications"])
class NotificationConsumer(
    private val notificationService: NotificationService
) {
    @KafkaHandler
    fun handle(event: NotificationEvent) {
        try {
            notificationService.processNotification(event)
        } catch (e: Exception) {
            // Send to dead letter queue for retry
            throw e
        }
    }
}
```

### RabbitMQ Integration

```kotlin
@Service
class NotificationProducer(
    private val rabbitTemplate: RabbitTemplate
) {
    fun sendNotification(event: NotificationEvent) {
        rabbitTemplate.convertAndSend(
            "notifications.exchange",
            "notifications.routing.key",
            event
        )
    }
}

@RabbitListener(queues = ["notifications.queue"])
class NotificationConsumer(
    private val notificationService: NotificationService
) {
    fun handle(event: NotificationEvent) {
        notificationService.processNotification(event)
    }
}
```

### Retry Strategy

```kotlin
@Service
class RetryableNotificationService(
    private val notificationService: NotificationService,
    private val retryPolicy: RetryPolicy
) {
    suspend fun sendWithRetry(request: NotificationRequest) {
        var attempt = 0
        var lastError: Exception? = null
        
        while (attempt < retryPolicy.maxAttempts) {
            try {
                notificationService.sendNotification(request)
                return // Success
            } catch (e: Exception) {
                lastError = e
                attempt++
                
                if (attempt < retryPolicy.maxAttempts) {
                    val delay = retryPolicy.calculateDelay(attempt)
                    delay(delay.toMillis())
                }
            }
        }
        
        // All retries failed, send to dead letter queue
        deadLetterQueue.send(request, lastError)
    }
}

data class RetryPolicy(
    val maxAttempts: Int = 3,
    val initialDelay: Duration = Duration.ofSeconds(1),
    val multiplier: Double = 2.0
) {
    fun calculateDelay(attempt: Int): Duration {
        val delaySeconds = initialDelay.seconds * Math.pow(multiplier, attempt.toDouble()).toLong()
        return Duration.ofSeconds(delaySeconds)
    }
}
```

## Multi-Tenant Isolation

In multi-tenant systems, ensure notification isolation between tenants.

### Tenant-Aware Preference Storage

```kotlin
@Entity
data class NotificationPreference(
    @Id val id: String,
    val tenantId: String, // Add tenant isolation
    val userId: String,
    // ... other fields
)

@Repository
interface PreferenceRepository : JpaRepository<NotificationPreference, String> {
    @Query("SELECT p FROM NotificationPreference p WHERE p.tenantId = :tenantId AND p.userId = :userId")
    fun findByTenantAndUser(tenantId: String, userId: String): List<NotificationPreference>
}
```

### Tenant-Scoped Templates

```kotlin
@Entity
data class NotificationTemplate(
    @Id val id: String,
    val tenantId: String, // Tenant-specific templates
    val name: String,
    // ... template content
)
```

### Tenant-Aware Channel Configuration

```kotlin
data class TenantChannelConfig(
    val tenantId: String,
    val emailProvider: EmailProvider, // Each tenant can use different provider
    val smsProvider: SmsProvider,
    val pushConfig: PushConfig
)
```

## Notification Inbox Architecture

The notification inbox stores and manages in-app notifications.

### Data Model

```kotlin
@Entity
data class InAppNotification(
    @Id val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val tenantId: String,
    val title: String,
    val body: String,
    val type: NotificationType,
    val actionUrl: String?,
    val read: Boolean = false,
    val readAt: Instant? = null,
    val createdAt: Instant = Instant.now(),
    val metadata: Map<String, String> = emptyMap()
)
```

### Inbox API

```kotlin
@RestController
@RequestMapping("/api/notifications")
class NotificationInboxController(
    private val notificationRepository: NotificationRepository
) {
    @GetMapping
    fun getNotifications(
        @RequestParam userId: String,
        @RequestParam(defaultValue = "0") page: Int,
        @RequestParam(defaultValue = "20") size: Int,
        @RequestParam read: Boolean? = null
    ): Page<InAppNotification> {
        val spec = NotificationSpecifications.forUser(userId)
            .and(NotificationSpecifications.readFilter(read))
        
        return notificationRepository.findAll(spec, PageRequest.of(page, size))
    }
    
    @PatchMapping("/{id}/read")
    fun markAsRead(@PathVariable id: String) {
        notificationRepository.markAsRead(id)
    }
    
    @GetMapping("/unread/count")
    fun getUnreadCount(@RequestParam userId: String): Int {
        return notificationRepository.countUnreadByUserId(userId)
    }
}
```

### Pagination and Grouping

```kotlin
// Group notifications by date
fun groupByDate(notifications: List<InAppNotification>): Map<String, List<InAppNotification>> {
    return notifications.groupBy { notification ->
        notification.createdAt.toLocalDate().toString()
    }
}

// Group by type
fun groupByType(notifications: List<InAppNotification>): Map<NotificationType, List<InAppNotification>> {
    return notifications.groupBy { it.type }
}
```

## Email Deliverability

Email deliverability is critical—emails must reach the inbox, not spam.

### SPF (Sender Policy Framework)

SPF records authorize which servers can send email for your domain:

```
v=spf1 include:_spf.google.com ~all
```

### DKIM (DomainKeys Identified Mail)

DKIM signs emails cryptographically to prove authenticity:

```kotlin
// Most email providers handle DKIM automatically
// Ensure your domain has DKIM records configured
```

### DMARC (Domain-based Message Authentication)

DMARC policy tells receiving servers what to do with emails that fail SPF/DKIM:

```
v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com
```

### Best Practices

1. **Warm up sending domain**: Gradually increase email volume from new domain
2. **Monitor bounce rates**: Remove invalid addresses immediately
3. **Use dedicated IP**: For high volume, use dedicated sending IP
4. **Authenticate properly**: Configure SPF, DKIM, DMARC
5. **Maintain sender reputation**: Avoid spam triggers, honor opt-outs
6. **Use transactional email service**: Services like SendGrid, AWS SES handle deliverability

### Bounce Handling

```kotlin
@RestController
class EmailWebhookController {
    @PostMapping("/webhooks/email/bounce")
    fun handleBounce(@RequestBody bounce: EmailBounce) {
        if (bounce.isPermanent) {
            userRepository.markEmailInvalid(bounce.recipient)
        } else {
            // Temporary bounce, retry later
            retryQueue.scheduleRetry(bounce.notificationId, Duration.ofHours(1))
        }
    }
}
```
