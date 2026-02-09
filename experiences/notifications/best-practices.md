# Notifications — Best Practices

## Contents
- [Respect User Preferences](#respect-user-preferences)
- [Progressive Notification Onboarding](#progressive-notification-onboarding)
- [Actionable Notifications](#actionable-notifications)
- [Grouping and Batching](#grouping-and-batching)
- [Clear Dismiss/Mark-Read UX](#clear-dismissmark-read-ux)
- [In-App Notification Patterns](#in-app-notification-patterns)
- [Email Best Practices](#email-best-practices)
- [Push Notification Best Practices](#push-notification-best-practices)
- [Notification Content](#notification-content)
- [Stack-Specific Callouts](#stack-specific-callouts)
- [Accessibility](#accessibility)
- [Multi-Tenant Considerations](#multi-tenant-considerations)
- [Common Anti-Patterns](#common-anti-patterns)

## Respect User Preferences

**CRITICAL RULE:** Never override user opt-out preferences, even for "important" messages. If a user has disabled notifications, respect that choice. For truly critical alerts that must be delivered, use a separate mandatory channel (e.g., SMS for security alerts, in-app banners for system-wide outages).

### Implementation Pattern

```typescript
interface NotificationPreferences {
  email: boolean;
  push: boolean;
  inApp: boolean;
  sms: boolean; // Mandatory channel for critical alerts only
}

const shouldSendNotification = (
  notification: Notification,
  preferences: NotificationPreferences
): boolean => {
  // Critical security alerts bypass preferences (use SMS)
  if (notification.priority === 'critical' && notification.type === 'security') {
    return true; // Always send via mandatory channel
  }
  
  // Respect user preferences for all other notifications
  const channel = notification.channel;
  return preferences[channel] ?? false;
};
```

### Preference Storage

```java
@Entity
public class UserNotificationPreferences {
    @Id
    private String userId;
    
    private boolean emailEnabled = true;
    private boolean pushEnabled = true;
    private boolean inAppEnabled = true;
    
    // Separate flag for critical-only notifications
    private boolean criticalSmsEnabled = true;
}
```

## Progressive Notification Onboarding

Don't ask for push notification permission on first visit. Explain the value first, then ask in context when the user would benefit.

### Onboarding Flow

1. **First Visit:** No permission request. Show value proposition.
2. **Contextual Trigger:** Request permission when user performs action that would benefit from notifications (e.g., after creating first order, request order status notifications).
3. **Graceful Decline:** If denied, don't ask again. Provide alternative (email digest).

**Vue 3 Example:**
```vue
<script setup>
import { ref, onMounted } from 'vue';

const showPermissionPrompt = ref(false);
const permissionStatus = ref<NotificationPermission>('default');

const checkPermission = () => {
  if ('Notification' in window) {
    permissionStatus.value = Notification.permission;
    
    // Show prompt only if:
    // 1. Permission is default (not asked yet)
    // 2. User has performed value-creating action
    // 3. Not shown in this session
    if (permissionStatus.value === 'default' && 
        hasUserCreatedValue() && 
        !sessionStorage.getItem('permission-prompt-shown')) {
      showPermissionPrompt.value = true;
    }
  }
};

const requestPermission = async () => {
  const permission = await Notification.requestPermission();
  permissionStatus.value = permission;
  sessionStorage.setItem('permission-prompt-shown', 'true');
  showPermissionPrompt.value = false;
  
  if (permission === 'granted') {
    // Show first notification immediately to demonstrate value
    showWelcomeNotification();
  }
};

onMounted(checkPermission);
</script>

<template>
  <div v-if="showPermissionPrompt" class="permission-prompt">
    <p>Get real-time updates on your orders. Enable notifications?</p>
    <button @click="requestPermission">Enable</button>
    <button @click="showPermissionPrompt = false">Not Now</button>
  </div>
</template>
```

**React Example:**
```tsx
function useNotificationPermission() {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [showPrompt, setShowPrompt] = useState(false);
  
  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
      
      if (Notification.permission === 'default' && 
          shouldShowPrompt() &&
          !sessionStorage.getItem('permission-prompt-shown')) {
        setShowPrompt(true);
      }
    }
  }, []);
  
  const requestPermission = async () => {
    const result = await Notification.requestPermission();
    setPermission(result);
    sessionStorage.setItem('permission-prompt-shown', 'true');
    setShowPrompt(false);
  };
  
  return { permission, showPrompt, requestPermission };
}
```

## Actionable Notifications

Every notification should have a clear next step. "Approve request" is better than "New request". "View order #1234" is better than "Order update".

### Notification Structure

```typescript
interface ActionableNotification {
  id: string;
  title: string;
  body: string;
  action: {
    label: string; // "Approve", "View Details", "Dismiss"
    url: string; // Deep link to relevant content
    method?: 'GET' | 'POST'; // For actions that modify state
  };
  metadata: {
    entityType: string; // "order", "request", "message"
    entityId: string;
    priority: 'low' | 'medium' | 'high';
  };
}
```

### Implementation

```vue
<template>
  <div class="notification" @click="handleAction">
    <div class="notification-content">
      <h4>{{ notification.title }}</h4>
      <p>{{ notification.body }}</p>
    </div>
    <button class="action-button">
      {{ notification.action.label }}
    </button>
  </div>
</template>

<script setup>
const handleAction = () => {
  if (notification.action.method === 'POST') {
    // Perform action (e.g., approve request)
    api.post(notification.action.url);
  } else {
    // Navigate to details
    router.push(notification.action.url);
  }
  
  // Mark as read
  markAsRead(notification.id);
};
</script>
```

## Grouping and Batching

For high-volume notifications, use digest mode, collapse similar notifications, and show "and 3 more" summaries.

### Digest Mode

```typescript
interface NotificationDigest {
  type: 'digest';
  period: 'hourly' | 'daily' | 'weekly';
  notifications: Notification[];
  summary: string; // "5 new orders, 3 messages, 2 approvals needed"
}

const createDigest = (notifications: Notification[]): NotificationDigest => {
  const grouped = groupBy(notifications, n => n.type);
  
  const summary = Object.entries(grouped)
    .map(([type, items]) => `${items.length} ${type}`)
    .join(', ');
  
  return {
    type: 'digest',
    period: 'daily',
    notifications,
    summary: `You have ${notifications.length} updates: ${summary}`
  };
};
```

### Collapsing Similar Notifications

```vue
<template>
  <div class="notification-group">
    <div v-if="groupedNotifications.length === 1">
      <NotificationItem :notification="groupedNotifications[0]" />
    </div>
    <div v-else>
      <div class="notification-header">
        <span>{{ groupedNotifications[0].title }}</span>
        <span class="count">+{{ groupedNotifications.length - 1 }} more</span>
      </div>
      <div v-if="expanded" class="notification-list">
        <NotificationItem 
          v-for="n in groupedNotifications" 
          :key="n.id" 
          :notification="n" 
        />
      </div>
      <button @click="expanded = !expanded">
        {{ expanded ? 'Collapse' : 'Expand' }}
      </button>
    </div>
  </div>
</template>

<script setup>
const groupedNotifications = computed(() => {
  // Group by type and entity (e.g., all "order shipped" notifications)
  return groupNotificationsByTypeAndEntity(props.notifications);
});
</script>
```

## Clear Dismiss/Mark-Read UX

Provide intuitive ways to dismiss notifications and mark them as read.

### Swipe to Dismiss

```vue
<template>
  <div 
    class="notification-item"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
    :style="{ transform: `translateX(${swipeOffset}px)` }"
  >
    <NotificationContent :notification="notification" />
    <div class="dismiss-indicator" v-if="swipeOffset < -50">
      Swipe to dismiss
    </div>
  </div>
</template>

<script setup>
const swipeOffset = ref(0);

const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0].clientX;
};

const handleTouchMove = (e: TouchEvent) => {
  const deltaX = e.touches[0].clientX - touchStartX.value;
  if (deltaX < 0) { // Only allow left swipe
    swipeOffset.value = deltaX;
  }
};

const handleTouchEnd = () => {
  if (swipeOffset.value < -100) {
    dismissNotification(notification.id);
  } else {
    swipeOffset.value = 0; // Snap back
  }
};
</script>
```

### Mark All as Read

```typescript
const markAllAsRead = async () => {
  const unreadIds = notifications
    .filter(n => !n.read)
    .map(n => n.id);
  
  await api.post('/notifications/mark-read', { ids: unreadIds });
  
  // Optimistically update UI
  notifications.forEach(n => {
    if (unreadIds.includes(n.id)) {
      n.read = true;
    }
  });
};
```

### Individual vs. Bulk Actions

```vue
<template>
  <div class="notification-center">
    <div class="header">
      <h2>Notifications</h2>
      <div class="actions">
        <button @click="selectAll">Select All</button>
        <button 
          v-if="selectedCount > 0"
          @click="markSelectedAsRead"
        >
          Mark {{ selectedCount }} as Read
        </button>
        <button @click="markAllAsRead">Mark All as Read</button>
      </div>
    </div>
    
    <div class="notification-list">
      <NotificationItem
        v-for="n in notifications"
        :key="n.id"
        :notification="n"
        :selected="selectedIds.has(n.id)"
        @select="toggleSelection(n.id)"
        @mark-read="markAsRead(n.id)"
        @dismiss="dismissNotification(n.id)"
      />
    </div>
  </div>
</template>
```

## In-App Notification Patterns

### Toast/Snackbar (Ephemeral)

For confirmations and low-priority alerts that auto-dismiss.

**Vue 3 with vue-toastification:**
```vue
<script setup>
import { useToast } from 'vue-toastification';

const toast = useToast();

const showSuccess = () => {
  toast.success('Order placed successfully!', {
    timeout: 3000,
    position: 'top-right'
  });
};
</script>
```

**React with react-hot-toast:**
```tsx
import toast from 'react-hot-toast';

const showSuccess = () => {
  toast.success('Order placed successfully!', {
    duration: 3000,
    position: 'top-right'
  });
};
```

### Notification Center (Persistent)

For all notification types with read/unread state.

```typescript
// Vue 3 composable
export function useNotificationCenter() {
  const notifications = ref<Notification[]>([]);
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.read).length
  );
  
  const markAsRead = async (id: string) => {
    await api.post(`/notifications/${id}/read`);
    const notification = notifications.value.find(n => n.id === id);
    if (notification) {
      notification.read = true;
    }
  };
  
  const fetchNotifications = async () => {
    const response = await api.get('/notifications');
    notifications.value = response.data;
  };
  
  return {
    notifications,
    unreadCount,
    markAsRead,
    fetchNotifications
  };
}
```

### Badge for Counts

```vue
<template>
  <button class="notification-button" @click="openCenter">
    <BellIcon />
    <span v-if="unreadCount > 0" class="badge">
      {{ unreadCount > 99 ? '99+' : unreadCount }}
    </span>
  </button>
</template>
```

### Banners (System-Wide)

For system-wide announcements that require acknowledgment.

```vue
<template>
  <div v-if="activeBanner" class="system-banner" :class="banner.type">
    <p>{{ activeBanner.message }}</p>
    <button @click="dismissBanner">Dismiss</button>
  </div>
</template>
```

## Email Best Practices

### Plain Text Fallback

Always include a plain text version alongside HTML.

```java
@Service
public class EmailService {
    public void sendEmail(EmailRequest request) {
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true);
        
        helper.setTo(request.getTo());
        helper.setSubject(request.getSubject());
        
        // HTML version
        helper.setText(request.getHtmlBody(), true);
        
        // Plain text fallback
        helper.setText(request.getPlainTextBody(), false);
    }
}
```

### Meaningful Preview Text

Use preheader text to provide context in email clients.

```html
<!-- Hide preheader in body but show in preview -->
<div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px;">
  Your order #1234 has shipped and will arrive tomorrow.
</div>
```

### Prominent Unsubscribe Link

Legal requirement (CAN-SPAM, GDPR). Make it easy to find.

```html
<div class="footer">
  <p>
    <a href="{{unsubscribeUrl}}">Unsubscribe</a> | 
    <a href="{{preferencesUrl}}">Manage Preferences</a>
  </p>
</div>
```

### Test Across Email Clients

Test in Gmail, Outlook, Apple Mail, and mobile clients. Use tools like Litmus or Email on Acid.

### Avoid Image-Only Emails

Always include text content. Many email clients block images by default.

## Push Notification Best Practices

### Concise Title

Keep titles under 50 characters. Be specific.

```
✅ "Order #1234 Shipped"
❌ "Update"
```

### Meaningful Body

Include enough context to act without opening the app.

```
✅ "Your order will arrive tomorrow. Track delivery →"
❌ "You have an update"
```

### Deep Link to Relevant Content

```typescript
const sendPushNotification = async (userId: string, notification: Notification) => {
  await pushService.send({
    to: userId,
    title: notification.title,
    body: notification.body,
    data: {
      deepLink: `/orders/${notification.metadata.entityId}`,
      action: notification.action.url
    }
  });
};
```

### Respect Quiet Hours

```java
@Service
public class PushNotificationService {
    public void sendNotification(String userId, Notification notification) {
        UserPreferences preferences = preferenceService.get(userId);
        
        LocalTime now = LocalTime.now();
        if (preferences.hasQuietHours() && 
            now.isAfter(preferences.getQuietStart()) &&
            now.isBefore(preferences.getQuietEnd())) {
            // Queue for later delivery
            queueService.enqueue(userId, notification, preferences.getQuietEnd());
            return;
        }
        
        // Send immediately
        pushClient.send(userId, notification);
    }
}
```

## Notification Content

### Be Specific

Include entity identifiers and actionable details.

```
✅ "Order #1234 shipped via FedEx. Tracking: 123456789"
❌ "Your order has been updated"
```

### Include Enough Context

Provide sufficient information to act without additional clicks.

```
✅ "John Doe requested approval for $5,000 purchase order. Review →"
❌ "New approval request"
```

### Link to Details

Always provide a way to access full details.

```typescript
const createNotification = (event: OrderShippedEvent): Notification => {
  return {
    title: `Order #${event.orderId} Shipped`,
    body: `Your order will arrive ${event.estimatedDeliveryDate}. Track your package →`,
    action: {
      label: 'Track Order',
      url: `/orders/${event.orderId}/tracking`
    }
  };
};
```

## Stack-Specific Callouts

### Vue 3

**Toast Libraries:**
- `vue-toastification`: Feature-rich, customizable
- `vue-sonner`: Modern, lightweight alternative

**Notification Center:**
```typescript
// composables/useNotifications.ts
import { defineStore } from 'pinia';

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [] as Notification[],
    unreadCount: 0
  }),
  
  actions: {
    addNotification(notification: Notification) {
      this.notifications.unshift(notification);
      if (!notification.read) {
        this.unreadCount++;
      }
      
      // Announce to screen readers
      this.announceToScreenReader(notification);
    },
    
    announceToScreenReader(notification: Notification) {
      // Use ARIA live region
      const announcement = `${notification.title}: ${notification.body}`;
      // Update aria-live region
    }
  }
});
```

**ARIA Live Regions:**
```vue
<template>
  <div 
    aria-live="polite" 
    aria-atomic="true" 
    class="sr-only"
    :aria-label="announcement"
  >
    {{ announcement }}
  </div>
</template>
```

### React

**Toast Libraries:**
- `react-hot-toast`: Popular, lightweight
- `sonner`: Modern, beautiful design

**Notification Context Provider:**
```tsx
const NotificationContext = createContext<{
  addNotification: (n: Notification) => void;
  notifications: Notification[];
}>({} as any);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev]);
  };
  
  return (
    <NotificationContext.Provider value={{ addNotification, notifications }}>
      {children}
      <NotificationPortal />
    </NotificationContext.Provider>
  );
}

// Portal-based rendering for toasts
function NotificationPortal() {
  return createPortal(
    <ToastContainer />,
    document.body
  );
}
```

### Spring Boot

**@Async Event Listeners:**
```java
@Component
public class NotificationEventListener {
    
    @Autowired
    private NotificationService notificationService;
    
    @Async
    @EventListener
    public void handleOrderShipped(OrderShippedEvent event) {
        Notification notification = Notification.builder()
            .userId(event.getUserId())
            .title("Order Shipped")
            .body("Your order #" + event.getOrderId() + " has shipped")
            .build();
            
        notificationService.send(notification);
    }
}
```

**Email Templates (Thymeleaf):**
```html
<!-- templates/email/order-shipped.html -->
<!DOCTYPE html>
<html>
<body>
    <h1>Order #[[${orderId}]] Shipped</h1>
    <p>Your order will arrive on [[${deliveryDate}]].</p>
    <a th:href="@{/orders/{id}(id=${orderId})}">Track Order</a>
</body>
</html>
```

**Spring Integration for Channel Routing:**
```java
@Configuration
public class NotificationRoutingConfig {
    
    @Bean
    public IntegrationFlow notificationFlow() {
        return IntegrationFlows.from("notificationChannel")
            .route(Notification.class, 
                notification -> notification.getChannel(),
                mapping -> mapping
                    .channelMapping("email", "emailChannel")
                    .channelMapping("push", "pushChannel")
                    .channelMapping("sms", "smsChannel"))
            .get();
    }
}
```

## Accessibility

### ARIA Live Regions for Toasts

```vue
<template>
  <div 
    role="status" 
    aria-live="polite"
    aria-atomic="true"
    class="sr-only"
  >
    {{ currentToast?.title }}: {{ currentToast?.body }}
  </div>
</template>
```

Use `role="alert"` for critical notifications that must interrupt:
```vue
<div role="alert" aria-live="assertive">
  Critical: System maintenance in 5 minutes
</div>
```

### Focus Management

When notification center opens, manage focus appropriately.

```vue
<script setup>
const notificationCenterRef = ref<HTMLElement>();

const openCenter = () => {
  isOpen.value = true;
  nextTick(() => {
    // Focus first unread notification or close button
    const firstUnread = notificationCenterRef.value?.querySelector(
      '.notification:not(.read)'
    ) as HTMLElement;
    firstUnread?.focus();
  });
};
</script>
```

### Don't Auto-Dismiss Critical Notifications

Critical notifications should require user acknowledgment.

```typescript
const showNotification = (notification: Notification) => {
  if (notification.priority === 'critical') {
    // Don't auto-dismiss
    toast(notification, { duration: Infinity });
  } else {
    // Auto-dismiss after 5 seconds
    toast(notification, { duration: 5000 });
  }
};
```

### Text Alternatives for Sounds

Provide visual indicators alongside audio cues.

```vue
<template>
  <div class="notification" :class="{ 'has-sound': playSound }">
    <NotificationIcon />
    <span v-if="playSound" class="sr-only">Notification sound played</span>
  </div>
</template>
```

## Multi-Tenant Considerations

### Tenant-Specific Branding

```java
@Service
public class EmailService {
    public void sendEmail(String tenantId, EmailRequest request) {
        TenantBranding branding = brandingService.get(tenantId);
        
        EmailTemplate template = templateService.getTemplate(
            request.getTemplateId(),
            tenantId
        );
        
        String htmlBody = template.render(Map.of(
            "logoUrl", branding.getLogoUrl(),
            "primaryColor", branding.getPrimaryColor(),
            "companyName", branding.getCompanyName()
        ));
        
        sendEmail(request.getTo(), htmlBody);
    }
}
```

### Tenant Isolation in Queues

```java
@KafkaListener(topics = "notifications", groupId = "notification-service")
public void handleNotification(NotificationEvent event) {
    // Ensure tenant isolation
    String tenantId = event.getTenantId();
    TenantContext.setCurrentTenant(tenantId);
    
    try {
        notificationService.send(event);
    } finally {
        TenantContext.clear();
    }
}
```

### Per-Tenant Preferences

```java
@Entity
public class TenantNotificationSettings {
    @Id
    private String tenantId;
    
    private boolean emailEnabled = true;
    private boolean pushEnabled = true;
    private Duration quietHoursStart;
    private Duration quietHoursEnd;
    private String defaultEmailFrom;
}
```

## Common Anti-Patterns

### Notification as Only Feedback

**Anti-Pattern:** Sending notification but not updating UI state.

```typescript
// ❌ Bad: Only notification, UI doesn't update
const handleOrderShipped = (event: OrderShippedEvent) => {
  sendNotification(event);
  // UI still shows "Processing" - user confused
};

// ✅ Good: Update UI AND send notification
const handleOrderShipped = (event: OrderShippedEvent) => {
  // Update UI immediately
  updateOrderStatus(event.orderId, 'shipped');
  
  // Then send notification
  sendNotification(event);
};
```

### Using Notifications for Known Information

**Anti-Pattern:** Notifying user of actions they just performed.

```typescript
// ❌ Bad: User just clicked "Save", why notify?
const handleSave = async () => {
  await api.post('/save', data);
  showNotification('Document saved'); // User already knows!
};

// ✅ Good: Only notify for async/background actions
const handleSave = async () => {
  await api.post('/save', data);
  // Show inline success indicator instead
  setSaveStatus('saved');
};
```

### Sending Multiple Channels by Default

**Anti-Pattern:** Sending email AND push AND in-app for every event.

```typescript
// ❌ Bad: Spam across all channels
const sendNotification = (event: Event) => {
  sendEmail(event);
  sendPush(event);
  sendInApp(event);
};

// ✅ Good: Respect user preferences and channel appropriateness
const sendNotification = (event: Event, preferences: Preferences) => {
  // Email for detailed information
  if (preferences.email && event.requiresDetail) {
    sendEmail(event);
  }
  
  // Push for time-sensitive
  if (preferences.push && event.isTimeSensitive) {
    sendPush(event);
  }
  
  // In-app for all (user is already in app)
  sendInApp(event);
};
```
