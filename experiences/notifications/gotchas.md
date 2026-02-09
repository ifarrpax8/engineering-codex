# Notifications -- Gotchas

## Contents

- [Notification Spam from Cascading Events](#notification-spam-from-cascading-events)
- [Email Deliverability Issues](#email-deliverability-issues)
- [Timezone-Naive Scheduling](#timezone-naive-scheduling)
- [Missing Unsubscribe Mechanism](#missing-unsubscribe-mechanism)
- [Stale Notification Badges](#stale-notification-badges)
- [WebSocket Connection Dropped Without Reconnect](#websocket-connection-dropped-without-reconnect)
- [Template Variables Missing or Null](#template-variables-missing-or-null)
- [Notification Ordering Issues](#notification-ordering-issues)
- [Push Notification Permission Denied with No Fallback](#push-notification-permission-denied-with-no-fallback)

## Notification Spam from Cascading Events

### The Problem

A single user action triggers multiple domain events, each of which sends a notification. The user receives 5 notifications for what they perceive as one action.

**Example Scenario**:
```
User places order
  → OrderCreatedEvent → "Order created" notification
  → PaymentProcessedEvent → "Payment received" notification  
  → InventoryReservedEvent → "Inventory reserved" notification
  → ShippingLabelCreatedEvent → "Shipping label created" notification
  → OrderStatusChangedEvent → "Order status updated" notification
```

User receives 5 notifications for placing one order!

### The Solution

**1. Event Deduplication**:
```kotlin
@Service
class NotificationDeduplicationService {
    private val recentNotifications = CacheBuilder.newBuilder()
        .expireAfterWrite(1, TimeUnit.MINUTES)
        .build<String, Boolean>()
    
    fun shouldSend(userId: String, eventType: String, entityId: String): Boolean {
        val key = "$userId:$eventType:$entityId"
        if (recentNotifications.getIfPresent(key) != null) {
            return false // Already sent recently
        }
        recentNotifications.put(key, true)
        return true
    }
}
```

**2. Notification Grouping**:
```kotlin
fun sendOrderNotifications(order: Order) {
    // Instead of sending 5 separate notifications, send one grouped notification
    sendNotification(
        NotificationRequest(
            userId = order.userId,
            templateId = "order-placed-summary",
            data = mapOf(
                "orderNumber" to order.number,
                "paymentStatus" to order.paymentStatus,
                "shippingStatus" to order.shippingStatus
            )
        )
    )
}
```

**3. Event Filtering**:
```kotlin
@EventListener
fun handleOrderEvent(event: OrderEvent) {
    // Only send notification for final state, not intermediate states
    if (event.isFinalState) {
        notificationService.sendNotification(createNotification(event))
    }
}
```

## Email Deliverability Issues

### The Problem

Emails are sent successfully from your application but land in spam folders or bounce, never reaching users.

### Common Causes

**1. Missing SPF/DKIM/DMARC Records**:
- Emails appear unauthenticated
- Receiving servers reject or spam-filter them

**Solution**: Configure DNS records:
```
SPF: v=spf1 include:_spf.sendgrid.net ~all
DKIM: (configured by email provider)
DMARC: v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com
```

**2. High Bounce Rate**:
- Sending to invalid email addresses
- Damages sender reputation

**Solution**: Validate emails and handle bounces:
```kotlin
@RestController
class EmailWebhookController {
    @PostMapping("/webhooks/email/bounce")
    fun handleBounce(@RequestBody bounce: EmailBounce) {
        if (bounce.isPermanent) {
            // Remove invalid email
            userRepository.markEmailInvalid(bounce.recipient)
        } else {
            // Temporary bounce, retry later
            retryQueue.scheduleRetry(bounce.notificationId, Duration.ofHours(1))
        }
    }
}
```

**3. Spam Trigger Words**:
- Using words like "FREE", "URGENT", excessive exclamation marks
- Triggering spam filters

**Solution**: Use professional language, avoid spam triggers:
```kotlin
// Bad
subject = "URGENT!!! FREE MONEY!!! CLICK NOW!!!"

// Good
subject = "Your order confirmation"
```

**4. Sending from New Domain/IP**:
- New sending domains need "warm-up" period
- Sending high volume immediately triggers spam filters

**Solution**: Gradually increase sending volume:
```kotlin
class EmailWarmupService {
    fun getMaxEmailsPerDay(domainAge: Duration): Int {
        return when {
            domainAge < Duration.ofDays(7) -> 100
            domainAge < Duration.ofDays(30) -> 1000
            else -> 10000
        }
    }
}
```

## Timezone-Naive Scheduling

### The Problem

Notifications are scheduled using server timezone instead of user's timezone, causing notifications to arrive at inconvenient times (e.g., 3 AM user's local time).

**Example**:
```kotlin
// BAD: Using server timezone
val scheduledTime = LocalDateTime.of(2026, 2, 10, 9, 0) // 9 AM server time
// If server is UTC and user is PST, this is 1 AM user's time!
```

### The Solution

**Always Use User Timezone**:
```kotlin
fun scheduleNotification(request: NotificationRequest, userTimezone: String) {
    val userLocalTime = LocalDateTime.of(2026, 2, 10, 9, 0) // 9 AM user's local time
    val scheduledUtc = userLocalTime
        .atZone(ZoneId.of(userTimezone))
        .toInstant()
    
    scheduler.schedule(request, scheduledUtc)
}
```

**Quiet Hours in User Timezone**:
```kotlin
fun isInQuietHours(userId: String): Boolean {
    val preferences = preferenceRepository.findByUserId(userId)
    val userTimezone = preferences.timezone ?: "UTC"
    val now = LocalTime.now(ZoneId.of(userTimezone))
    
    return now.isAfter(preferences.quietHoursStart) && 
           now.isBefore(preferences.quietHoursEnd)
}
```

**Store Timezone with User**:
```kotlin
@Entity
data class User(
    @Id val id: String,
    val email: String,
    val timezone: String = "UTC" // Always store user timezone
)
```

## Missing Unsubscribe Mechanism

### The Problem

No way for users to opt out of notifications, violating legal requirements (CAN-SPAM, GDPR) and damaging user trust.

### Legal Requirements

- **CAN-SPAM Act** (US): Requires unsubscribe mechanism in commercial emails
- **GDPR** (EU): Requires easy opt-out for marketing communications
- **CASL** (Canada): Requires unsubscribe in commercial emails

### The Solution

**1. Unsubscribe Link in Every Email**:
```kotlin
fun addUnsubscribeLink(htmlBody: String, userId: String): String {
    val token = generateSecureToken(userId)
    val unsubscribeUrl = "${baseUrl}/unsubscribe?token=$token"
    
    return htmlBody + """
        <footer>
            <p>
                <a href="$unsubscribeUrl">Unsubscribe</a> from these emails
                or <a href="${baseUrl}/preferences">manage preferences</a>.
            </p>
        </footer>
    """
}
```

**2. One-Click Unsubscribe**:
```kotlin
@GetMapping("/unsubscribe")
fun unsubscribe(@RequestParam token: String): ResponseEntity<String> {
    val userId = validateToken(token)
    preferenceRepository.disableAllChannels(userId)
    
    return ResponseEntity.ok("You have been unsubscribed from all notifications.")
}
```

**3. Preference Management Page**:
```kotlin
@GetMapping("/preferences")
fun getPreferences(@RequestParam userId: String): UserPreferences {
    return preferenceService.getUserPreferences(userId)
}

@PostMapping("/preferences")
fun updatePreferences(
    @RequestParam userId: String,
    @RequestBody preferences: UpdatePreferencesRequest
) {
    preferenceService.updatePreferences(userId, preferences)
}
```

## Stale Notification Badges

### The Problem

Badge count shows "3 unread" but user has already read all notifications. Count doesn't update in real-time.

### Common Causes

**1. No Real-Time Updates**:
- Badge count fetched on page load only
- Doesn't update when notifications are read

**2. Race Conditions**:
- Multiple tabs open, one tab marks as read
- Other tabs still show old count

**3. Caching Issues**:
- Badge count cached and not invalidated

### The Solution

**Real-Time Badge Updates**:
```typescript
// Frontend: Subscribe to unread count changes
function useUnreadCount() {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    const eventSource = new EventSource('/api/notifications/unread-count/stream')
    eventSource.onmessage = (event) => {
      setCount(JSON.parse(event.data).count)
    }
    return () => eventSource.close()
  }, [])
  
  return count
}
```

**WebSocket Updates**:
```kotlin
fun markAsRead(notificationId: String, userId: String) {
    notificationRepository.markAsRead(notificationId)
    
    // Broadcast updated count
    val unreadCount = notificationRepository.countUnreadByUserId(userId)
    webSocketHandler.sendToUser(userId, UnreadCountUpdate(unreadCount))
}
```

**Optimistic Updates**:
```typescript
function markAsRead(notificationId: string) {
  // Optimistically update UI
  setUnreadCount(prev => Math.max(0, prev - 1))
  
  // Then sync with server
  fetch(`/api/notifications/${notificationId}/read`, { method: 'PATCH' })
    .catch(() => {
      // Rollback on error
      setUnreadCount(prev => prev + 1)
    })
}
```

## WebSocket Connection Dropped Without Reconnect

### The Problem

WebSocket connection drops (network issue, server restart) and notifications stop appearing. No automatic reconnection.

### The Solution

**Automatic Reconnection with Exponential Backoff**:
```typescript
class NotificationWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  
  connect(userId: string) {
    this.ws = new WebSocket(`wss://api.example.com/ws/notifications?userId=${userId}`)
    
    this.ws.onopen = () => {
      this.reconnectAttempts = 0 // Reset on successful connection
    }
    
    this.ws.onclose = () => {
      this.reconnect()
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached')
      return
    }
    
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    this.reconnectAttempts++
    
    setTimeout(() => {
      console.log(`Reconnecting (attempt ${this.reconnectAttempts})...`)
      this.connect(this.userId)
    }, delay)
  }
}
```

**Vue 3 Composable**:
```typescript
export function useNotificationWebSocket(userId: string) {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  
  function connect() {
    ws.value = new WebSocket(`wss://api.example.com/ws/notifications?userId=${userId}`)
    
    ws.value.onopen = () => {
      connected.value = true
      reconnectAttempts.value = 0
    }
    
    ws.value.onclose = () => {
      connected.value = false
      reconnect()
    }
    
    ws.value.onmessage = (event) => {
      const notification = JSON.parse(event.data)
      // Handle notification
    }
  }
  
  function reconnect() {
    if (reconnectAttempts.value >= 10) return
    
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
    reconnectAttempts.value++
    
    setTimeout(connect, delay)
  }
  
  onMounted(() => connect())
  onUnmounted(() => ws.value?.close())
  
  return { connected, connect }
}
```

**Fallback to Polling**:
```typescript
function useNotificationsWithFallback(userId: string) {
  const { connected } = useNotificationWebSocket(userId)
  const pollInterval = ref<NodeJS.Timeout | null>(null)
  
  watch(connected, (isConnected) => {
    if (!isConnected) {
      // Fallback to polling when WebSocket disconnected
      pollInterval.value = setInterval(() => {
        fetchNotifications(userId)
      }, 30000) // Poll every 30 seconds
    } else {
      // Stop polling when WebSocket reconnects
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
      }
    }
  })
}
```

## Template Variables Missing or Null

### The Problem

Template variables are null or missing, causing broken notifications like "Hello null" or "Order #undefined confirmed".

### Common Causes

**1. Missing Data in Request**:
```kotlin
// BAD: Missing orderNumber in data
notificationService.sendNotification(
    NotificationRequest(
        templateId = "order-confirmed",
        data = mapOf("orderTotal" to "$99.99") // Missing orderNumber!
    )
)
```

**2. Null Values Not Handled**:
```kotlin
// Template renders as "Order #null confirmed"
val orderNumber: String? = null
data = mapOf("orderNumber" to orderNumber) // null value
```

### The Solution

**1. Validate Required Variables**:
```kotlin
fun render(templateId: String, data: Map<String, Any>): RenderedNotification {
    val template = templateRepository.findById(templateId)
    val requiredVars = template.variables
    
    val missing = requiredVars.filter { it !in data }
    if (missing.isNotEmpty()) {
        throw TemplateException("Missing required variables: $missing")
    }
    
    // Check for null values
    val nullVars = data.filter { it.value == null }
    if (nullVars.isNotEmpty()) {
        throw TemplateException("Null values for variables: ${nullVars.keys}")
    }
    
    return renderTemplate(template, data)
}
```

**2. Provide Default Values**:
```kotlin
fun renderWithDefaults(template: Template, data: Map<String, Any>): String {
    val defaults = mapOf(
        "orderNumber" to "N/A",
        "userName" to "Customer",
        "orderTotal" to "$0.00"
    )
    
    val mergedData = defaults + data // data overrides defaults
    return renderTemplate(template, mergedData)
}
```

**3. Use Optional Template Syntax**:
```kotlin
// Template supports optional variables
subject = "Order #{{orderNumber?}} Confirmed"
// If orderNumber is null/missing, renders as "Order # Confirmed" (or skip variable)
```

**4. Type-Safe Template Data**:
```kotlin
data class OrderConfirmationData(
    val orderNumber: String, // Non-nullable, required
    val orderTotal: String,
    val deliveryDate: String? = null // Optional
)

fun sendOrderConfirmation(order: Order) {
    val data = OrderConfirmationData(
        orderNumber = order.number, // Compiler ensures not null
        orderTotal = formatCurrency(order.total),
        deliveryDate = order.estimatedDelivery?.toString()
    )
    notificationService.sendNotification(
        NotificationRequest(templateId = "order-confirmed", data = data.toMap())
    )
}
```

## Notification Ordering Issues

### The Problem

Newer notifications appear below older ones, or notifications are displayed in random order instead of chronological.

### Common Causes

**1. Incorrect Sort Order**:
```kotlin
// BAD: No explicit ordering
val notifications = repository.findByUserId(userId)
// Order is undefined/database-dependent
```

**2. Timestamp Precision Issues**:
- Multiple notifications created in same millisecond
- No secondary sort key

**3. Frontend Sorting Issues**:
- Not sorting after fetching
- Sorting by wrong field

### The Solution

**Backend: Explicit Ordering**:
```kotlin
@Repository
interface NotificationRepository : JpaRepository<InAppNotification, String> {
    @Query("SELECT n FROM InAppNotification n WHERE n.userId = :userId ORDER BY n.createdAt DESC, n.id DESC")
    fun findByUserIdOrderByCreatedAtDesc(userId: String): List<InAppNotification>
}
```

**Frontend: Sort After Fetch**:
```typescript
function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  
  useEffect(() => {
    fetch('/api/notifications')
      .then(res => res.json())
      .then(data => {
        // Sort by createdAt descending (newest first)
        const sorted = data.sort((a, b) => 
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        )
        setNotifications(sorted)
      })
  }, [])
  
  return notifications
}
```

**Vue 3 Computed Sort**:
```vue
<script setup lang="ts">
const notifications = ref<Notification[]>([])

const sortedNotifications = computed(() => {
  return [...notifications.value].sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
})
</script>
```

**Secondary Sort Key**:
```kotlin
// Sort by createdAt DESC, then by id DESC for tie-breaking
@Query("""
    SELECT n FROM InAppNotification n 
    WHERE n.userId = :userId 
    ORDER BY n.createdAt DESC, n.id DESC
""")
fun findByUserIdOrdered(userId: String): List<InAppNotification>
```

## Push Notification Permission Denied with No Fallback

### The Problem

User denies push notification permission, and application has no fallback mechanism. User misses important notifications.

### The Solution

**1. Graceful Degradation**:
```typescript
async function requestPushPermission() {
  if (!('Notification' in window)) {
    // Not supported, use email/in-app only
    return { supported: false, granted: false }
  }
  
  if (Notification.permission === 'denied') {
    // Show alternative: email or in-app notifications
    showAlternativeOptions()
    return { supported: true, granted: false }
  }
  
  const permission = await Notification.requestPermission()
  
  if (permission === 'granted') {
    registerPushSubscription()
    return { supported: true, granted: true }
  } else {
    // Fallback to email/in-app
    showAlternativeOptions()
    return { supported: true, granted: false }
  }
}

function showAlternativeOptions() {
  // Show UI: "Enable email notifications instead" or "Check in-app notifications"
  showDialog({
    message: "Push notifications are disabled. Enable email notifications?",
    actions: [
      { label: "Enable Email", action: () => enableEmailNotifications() },
      { label: "Use In-App Only", action: () => {} }
    ]
  })
}
```

**2. Check Permission State**:
```typescript
function getNotificationStrategy() {
  if (!('Notification' in window)) {
    return 'email' // Not supported
  }
  
  switch (Notification.permission) {
    case 'granted':
      return 'push'
    case 'denied':
      return 'email' // Fallback
    case 'default':
      return 'prompt' // Can ask
  }
}
```

**3. Provide Settings Link**:
```typescript
if (Notification.permission === 'denied') {
  // Show: "Push notifications are disabled. 
  // You can enable them in your browser settings: [Link]"
  showSettingsPrompt()
}
```

**4. Multi-Channel Strategy**:
```kotlin
fun determineChannels(userId: String, request: NotificationRequest): List<ChannelType> {
    val preferences = preferenceService.getUserPreferences(userId)
    val pushPermission = pushService.getPermissionStatus(userId)
    
    val channels = mutableListOf<ChannelType>()
    
    // Try push first
    if (preferences.isChannelEnabled(ChannelType.PUSH) && pushPermission == PermissionStatus.GRANTED) {
        channels.add(ChannelType.PUSH)
    }
    
    // Fallback to email
    if (preferences.isChannelEnabled(ChannelType.EMAIL)) {
        channels.add(ChannelType.EMAIL)
    }
    
    // Always available: in-app
    channels.add(ChannelType.IN_APP)
    
    return channels
}
```
