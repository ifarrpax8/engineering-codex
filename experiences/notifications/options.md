---
recommendation_type: decision-matrix
---

# Notifications — Options

## Contents
- [In-App Notification Patterns](#in-app-notification-patterns)
- [Email Delivery Services](#email-delivery-services)
- [Real-Time Transport](#real-time-transport)
- [Notification Orchestration](#notification-orchestration)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## In-App Notification Patterns

### Toast/Snackbar

**Description:** Ephemeral notifications that appear temporarily (typically 3-5 seconds) and auto-dismiss. Usually positioned at screen edges (top-right, bottom-center).

**Strengths:**
- Non-intrusive, doesn't block user workflow
- Perfect for confirmations and low-priority feedback
- Lightweight implementation
- Works well for success/error states
- No user interaction required

**Weaknesses:**
- Easy to miss if user isn't looking
- Not suitable for important information requiring action
- Limited space for detailed content
- Can stack/clutter if multiple appear simultaneously

**Best For:**
- Form submission confirmations ("Order placed successfully")
- Error messages ("Failed to save, please try again")
- Quick status updates ("Saved", "Copied to clipboard")
- Low-priority alerts that don't require immediate attention

**Avoid When:**
- Notification requires user action (use notification center)
- Critical information that must be seen (use banner)
- Complex information requiring reading time (use notification center)
- User might not be actively looking at screen (use push notification)

**Implementation:**
```vue
<!-- Vue 3 with vue-toastification -->
<script setup>
import { useToast } from 'vue-toastification';
const toast = useToast();

toast.success('Order placed!', { timeout: 3000 });
</script>
```

```tsx
// React with react-hot-toast
import toast from 'react-hot-toast';
toast.success('Order placed!', { duration: 3000 });
```

### Notification Center/Inbox

**Description:** Persistent list of notifications with read/unread state, typically accessible via a bell icon with badge count. Can be a dropdown, sidebar, or full-page view.

**Strengths:**
- Centralized location for all notifications
- Read/unread state tracking
- Supports rich content and actions
- User can review at their own pace
- Searchable and filterable
- Can group/aggregate similar notifications

**Weaknesses:**
- Requires user to actively check
- More complex to implement (state management, persistence)
- Takes up screen real estate
- May require backend for cross-device sync

**Best For:**
- All notification types (universal pattern)
- Notifications requiring action ("Approve request", "Review comment")
- High-volume notification scenarios
- Notifications that need to be referenced later
- Multi-tenant applications with user-specific notifications

**Avoid When:**
- Very low notification volume (toast might suffice)
- Notifications are always ephemeral (use toast)
- Mobile-only app with limited screen space (consider badge + detail view)

**Implementation:**
```typescript
// Vue 3 with Pinia store
export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [] as Notification[],
    unreadCount: 0
  }),
  actions: {
    async fetchNotifications() {
      this.notifications = await api.get('/notifications');
      this.unreadCount = this.notifications.filter(n => !n.read).length;
    }
  }
});
```

### Badge + Dropdown

**Description:** Compact pattern showing notification count as badge on icon (typically bell), with dropdown showing recent notifications on click.

**Strengths:**
- Space-efficient, doesn't require dedicated UI area
- Clear visual indicator of unread count
- Quick access to recent notifications
- Familiar pattern (most apps use this)
- Good for medium-volume scenarios

**Weaknesses:**
- Limited space for notification content
- Typically shows only recent notifications (need "View All" link)
- Dropdown can be awkward on mobile
- May not scale well for very high volumes

**Best For:**
- Medium-volume notification scenarios (5-50 per day)
- Applications where screen space is premium
- When notification center would be overkill
- Quick access to recent activity

**Avoid When:**
- Very high notification volume (use full notification center)
- Notifications require detailed content (use notification center)
- Mobile-first application (dropdown UX is poor on mobile)

**Implementation:**
```vue
<template>
  <div class="notification-badge-container">
    <button @click="showDropdown = !showDropdown">
      <BellIcon />
      <span v-if="unreadCount > 0" class="badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>
    <div v-if="showDropdown" class="dropdown">
      <NotificationList :notifications="recentNotifications" />
      <a href="/notifications">View All</a>
    </div>
  </div>
</template>
```

### Banner

**Description:** Full-width notification bar, typically at top of page, for system-wide announcements. Usually requires dismissal.

**Strengths:**
- High visibility, impossible to miss
- Good for system-wide announcements
- Can include rich content and actions
- Persistent until dismissed
- Works well for maintenance notices, feature announcements

**Weaknesses:**
- Intrusive, takes up screen space
- Can be annoying if overused
- Not suitable for user-specific notifications
- Requires careful design to not block critical UI

**Best For:**
- System-wide announcements ("Scheduled maintenance tonight")
- Critical alerts affecting all users ("Service degradation")
- Feature announcements ("New feature available")
- Legal/compliance notices ("Terms updated")

**Avoid When:**
- User-specific notifications (use notification center)
- Frequent updates (use toast or notification center)
- Non-critical information (use less intrusive pattern)
- Mobile applications (banners take too much space)

**Implementation:**
```vue
<template>
  <div v-if="activeBanner" class="system-banner" :class="banner.severity">
    <div class="banner-content">
      <p>{{ banner.message }}</p>
      <button v-if="banner.action" @click="handleBannerAction">
        {{ banner.actionLabel }}
      </button>
    </div>
    <button @click="dismissBanner" class="dismiss">×</button>
  </div>
</template>
```

## Email Delivery Services

### SendGrid

**Description:** Feature-rich email delivery platform with template editor, analytics, and strong deliverability.

**Strengths:**
- Excellent deliverability rates
- Built-in template editor (Visual Editor)
- Comprehensive analytics (opens, clicks, bounces)
- Webhook support for real-time events
- Good documentation and SDKs
- Transactional and marketing email support
- IP warmup assistance for new accounts

**Weaknesses:**
- More expensive than AWS SES for high volume
- Template editor can be limiting for complex designs
- Some features require higher-tier plans
- Can be overkill for simple use cases

**Best For:**
- Applications requiring high deliverability
- Need for email analytics and tracking
- Marketing emails alongside transactional
- Teams wanting template management UI
- Applications with moderate to high email volume (10K-1M+ per month)

**Avoid When:**
- Very high volume where cost matters most (use AWS SES)
- Simple use case with minimal requirements (use Mailgun or self-hosted)
- Strict budget constraints for low volume
- Need for complete control over infrastructure

**Implementation:**
```java
@Service
public class SendGridEmailService {
    @Autowired
    private SendGrid sendGrid;
    
    public void sendEmail(String to, String templateId, Map<String, Object> data) {
        Mail mail = new Mail();
        mail.setFrom(new Email("noreply@example.com"));
        mail.setTemplateId(templateId);
        
        Personalization personalization = new Personalization();
        personalization.addTo(new Email(to));
        data.forEach((key, value) -> 
            personalization.addDynamicTemplateData(key, value));
        mail.addPersonalization(personalization);
        
        Request request = new Request();
        request.setMethod(Method.POST);
        request.setEndpoint("mail/send");
        request.setBody(mail.build());
        
        sendGrid.api(request);
    }
}
```

### AWS SES

**Description:** Cost-effective email service from AWS, good for high volume, requires more DIY setup.

**Strengths:**
- Very cost-effective for high volume ($0.10 per 1,000 emails)
- Integrates well with other AWS services (SNS, SQS, Lambda)
- Can use with custom SMTP or AWS SDK
- Good for applications already on AWS
- Supports both sending and receiving emails
- Can use verified domains for better deliverability

**Weaknesses:**
- Requires more setup (domain verification, IP warmup)
- Limited built-in analytics (need to build custom)
- No template editor (must manage templates yourself)
- Account starts in sandbox mode (limited to verified emails)
- Less hand-holding than SendGrid
- Deliverability can require more work

**Best For:**
- High-volume email sending (100K+ per month)
- Applications already using AWS infrastructure
- Cost-sensitive projects
- Teams comfortable with DIY approach
- Need for tight integration with AWS services (SNS, SQS)

**Avoid When:**
- Need for email analytics dashboard out of the box
- Want template management UI
- Low volume where setup overhead isn't worth it
- Team lacks AWS expertise
- Need for marketing email features (use SendGrid)

**Implementation:**
```java
@Service
public class AwsSesEmailService {
    @Autowired
    private AmazonSimpleEmailService sesClient;
    
    public void sendEmail(String to, String subject, String htmlBody, String textBody) {
        SendEmailRequest request = new SendEmailRequest()
            .withDestination(new Destination().withToAddresses(to))
            .withMessage(new Message()
                .withBody(new Body()
                    .withHtml(new Content().withCharset("UTF-8").withData(htmlBody))
                    .withText(new Content().withCharset("UTF-8").withData(textBody)))
                .withSubject(new Content().withCharset("UTF-8").withData(subject)))
            .withSource("noreply@example.com");
        
        sesClient.sendEmail(request);
    }
}
```

### Mailgun

**Description:** Developer-friendly email service with good logging and strong API.

**Strengths:**
- Developer-friendly API and documentation
- Excellent logging and webhook system
- Good for transactional emails
- Competitive pricing
- Easy to get started
- Good deliverability
- Supports both SMTP and REST API

**Weaknesses:**
- Less feature-rich than SendGrid for marketing
- Template management is more basic
- Analytics not as comprehensive as SendGrid
- Smaller ecosystem than SendGrid

**Best For:**
- Developer-focused teams
- Transactional email use cases
- Need for detailed logging and webhooks
- Applications wanting simple, reliable email
- Good balance of features and cost

**Avoid When:**
- Need for marketing email features (use SendGrid)
- Very high volume where AWS SES is cheaper
- Need for visual template editor
- Complex email workflows requiring advanced features

**Implementation:**
```java
@Service
public class MailgunEmailService {
    private final String apiKey = "your-api-key";
    private final String domain = "mg.example.com";
    
    public void sendEmail(String to, String subject, String htmlBody) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.setBasicAuth("api", apiKey);
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);
        
        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("from", "noreply@example.com");
        body.add("to", to);
        body.add("subject", subject);
        body.add("html", htmlBody);
        
        HttpEntity<MultiValueMap<String, String>> request = 
            new HttpEntity<>(body, headers);
        
        restTemplate.postForEntity(
            "https://api.mailgun.net/v3/" + domain + "/messages",
            request,
            String.class
        );
    }
}
```

### Self-Hosted SMTP

**Description:** Running your own SMTP server (Postfix, Sendmail) or using a VPS with SMTP capabilities.

**Strengths:**
- Complete control over infrastructure
- No per-email costs (only server costs)
- Can customize everything
- No vendor lock-in
- Good for very high volume if managed well

**Weaknesses:**
- Significant setup and maintenance overhead
- Deliverability challenges (IP reputation, SPF, DKIM, DMARC)
- Risk of being blacklisted
- Need for monitoring and maintenance
- Requires email infrastructure expertise
- Can be more expensive than managed services at scale

**Best For:**
- Very high volume where managed service costs are prohibitive
- Strict compliance requirements (data residency, etc.)
- Existing email infrastructure expertise
- Need for complete control
- Internal-only email systems

**Avoid When:**
- Team lacks email infrastructure expertise
- Deliverability is critical (use managed service)
- Low to medium volume (managed service is easier)
- Don't want to manage infrastructure
- Need for quick setup

**Implementation:**
```java
@Configuration
public class SmtpConfig {
    @Bean
    public JavaMailSender mailSender() {
        JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
        mailSender.setHost("smtp.example.com");
        mailSender.setPort(587);
        mailSender.setUsername("username");
        mailSender.setPassword("password");
        
        Properties props = mailSender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        
        return mailSender;
    }
}
```

## Real-Time Transport

### WebSocket

**Description:** Bidirectional, persistent connection enabling real-time two-way communication.

**Strengths:**
- True bidirectional communication
- Low latency once connected
- Efficient for high-frequency updates
- Can push data from server anytime
- Good for collaborative features (typing indicators, live updates)
- Single persistent connection

**Weaknesses:**
- More complex to implement and maintain
- Connection management overhead (reconnection, heartbeat)
- Can be resource-intensive on server
- Firewall/proxy issues in some environments
- Requires stateful server infrastructure
- Overkill for one-way notifications

**Best For:**
- High-frequency real-time updates (chat, live data feeds)
- Bidirectional communication needs
- Collaborative features (co-editing, presence)
- Applications requiring instant updates
- When SSE isn't sufficient (need bidirectional)

**Avoid When:**
- One-way notifications only (use SSE)
- Low-frequency updates (use polling)
- Simple use case where complexity isn't justified
- Need for stateless infrastructure
- Firewall restrictions prevent WebSocket connections

**Implementation:**
```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws").withSockJS();
    }
}
```

```typescript
// Frontend
const socket = new SockJS('/ws');
const stompClient = Stomp.over(socket);

stompClient.connect({}, () => {
  stompClient.subscribe('/topic/notifications', (message) => {
    const notification = JSON.parse(message.body);
    handleNotification(notification);
  });
});
```

### SSE (Server-Sent Events)

**Description:** Unidirectional stream from server to client over HTTP, simpler than WebSocket.

**Strengths:**
- Simpler than WebSocket (standard HTTP)
- Automatic reconnection built into browser API
- Works through most firewalls/proxies
- Less server overhead than WebSocket
- Good for one-way server-to-client updates
- No need for special protocols

**Weaknesses:**
- One-way only (server to client)
- Limited browser support (though widely supported now)
- Can't send binary data easily
- Connection limits per browser (typically 6)
- Less efficient than WebSocket for very high frequency

**Best For:**
- One-way notifications (server to client)
- Live updates (stock prices, news feeds)
- Simpler alternative to WebSocket when bidirectional isn't needed
- Applications wanting real-time without WebSocket complexity
- When HTTP-based solution is preferred

**Avoid When:**
- Need bidirectional communication (use WebSocket)
- Very high frequency updates (WebSocket more efficient)
- Need to send data from client frequently
- Binary data requirements

**Implementation:**
```java
@GetMapping(value = "/notifications/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<Notification>> streamNotifications(
    @AuthenticationPrincipal User user) {
    return notificationService.getNotificationStream(user.getId())
        .map(notification -> ServerSentEvent.<Notification>builder()
            .data(notification)
            .event("notification")
            .build());
}
```

```typescript
// Frontend
const eventSource = new EventSource('/api/notifications/stream');

eventSource.addEventListener('notification', (event) => {
  const notification = JSON.parse(event.data);
  handleNotification(notification);
});

eventSource.onerror = () => {
  // Handle reconnection
  eventSource.close();
  setTimeout(() => {
    eventSource = new EventSource('/api/notifications/stream');
  }, 5000);
};
```

### Polling

**Description:** Client periodically requests updates from server via standard HTTP requests.

**Strengths:**
- Simplest to implement (standard HTTP)
- Works everywhere (no special protocols)
- Stateless (no persistent connections)
- Easy to debug and monitor
- Good for low-frequency updates
- No special infrastructure needed

**Weaknesses:**
- Higher latency (depends on poll interval)
- Inefficient (many requests may return no data)
- Server load increases with frequency
- Not truly real-time
- Wastes bandwidth when no updates

**Best For:**
- Low-frequency updates (checking every 30+ seconds)
- Simple use cases where real-time isn't critical
- Applications where simplicity is priority
- When SSE/WebSocket aren't feasible
- Prototyping and MVP stages

**Avoid When:**
- Need for real-time or near-real-time updates
- High-frequency updates (wasteful)
- Many concurrent users (server load)
- User experience requires instant updates

**Implementation:**
```typescript
// Frontend polling
const pollNotifications = () => {
  setInterval(async () => {
    const response = await fetch('/api/notifications?since=' + lastCheckTime);
    const notifications = await response.json();
    notifications.forEach(handleNotification);
    lastCheckTime = Date.now();
  }, 5000); // Poll every 5 seconds
};
```

```java
// Backend with conditional requests (ETag/Last-Modified)
@GetMapping("/notifications")
public ResponseEntity<List<Notification>> getNotifications(
    @RequestHeader(value = "If-None-Match", required = false) String etag,
    @RequestParam(required = false) Long since) {
    
    List<Notification> notifications = notificationService.getSince(since);
    String currentEtag = generateETag(notifications);
    
    if (currentEtag.equals(etag)) {
        return ResponseEntity.status(HttpStatus.NOT_MODIFIED).build();
    }
    
    return ResponseEntity.ok()
        .eTag(currentEtag)
        .body(notifications);
}
```

## Notification Orchestration

### Custom Notification Service

**Description:** Building your own notification service tailored to specific needs.

**Strengths:**
- Complete control over features and behavior
- Tailored to exact requirements
- No vendor lock-in
- Can integrate tightly with existing systems
- No per-notification costs (infrastructure only)
- Full customization

**Weaknesses:**
- Significant development and maintenance effort
- Need to handle all channels yourself (email, push, SMS)
- Must manage deliverability, retries, failures
- Requires ongoing maintenance and updates
- Team needs expertise in notification systems
- Can be more expensive than managed services at scale

**Best For:**
- Unique requirements not met by existing solutions
- Very high volume where managed service costs are prohibitive
- Need for tight integration with existing systems
- Team has expertise and resources
- Strict compliance/security requirements
- Long-term strategic control

**Avoid When:**
- Standard notification needs (use managed service)
- Team lacks resources for development/maintenance
- Want to focus on core product, not infrastructure
- Need for quick time-to-market
- Don't have notification system expertise

### Novu

**Description:** Open-source notification infrastructure with multi-channel support.

**Strengths:**
- Open-source (self-host or cloud)
- Multi-channel (email, push, SMS, in-app, chat)
- Template management
- Workflow builder for complex flows
- Good documentation
- Active community
- Can self-host for control

**Weaknesses:**
- Relatively new (less mature than commercial options)
- Self-hosting requires infrastructure management
- Smaller ecosystem than established players
- May need customization for specific needs

**Best For:**
- Teams wanting open-source solution
- Multi-channel notification needs
- Want to avoid vendor lock-in
- Need for workflow/orchestration features
- Applications requiring self-hosting
- Good balance of features and control

**Avoid When:**
- Need for enterprise support and SLA
- Want fully managed service (use Courier)
- Very simple use case (custom might be simpler)
- Team lacks resources for self-hosting if needed

### Courier

**Description:** Commercial notification platform with template management and delivery tracking.

**Strengths:**
- Fully managed service
- Excellent template management UI
- Multi-channel support
- Good delivery tracking and analytics
- Developer-friendly API
- Good documentation
- Reliable delivery infrastructure

**Weaknesses:**
- Commercial (costs scale with usage)
- Vendor lock-in
- Less control than self-hosted
- May be overkill for simple use cases

**Best For:**
- Teams wanting managed notification infrastructure
- Need for template management UI
- Multi-channel requirements
- Want to focus on product, not infrastructure
- Applications requiring reliable delivery
- Good developer experience priority

**Avoid When:**
- Very high volume where cost matters (custom or self-hosted)
- Need for complete control (custom service)
- Simple single-channel use case (direct integration might suffice)
- Budget constraints for low volume

## Recommendation Guidance

### Default Recommendations

**In-App Notifications:**
- **Start with:** Badge + Dropdown for most applications
- **Upgrade to:** Notification Center when volume increases or actions required
- **Use Toast:** For confirmations and ephemeral feedback
- **Use Banner:** Only for system-wide critical announcements

**Email Delivery:**
- **Start with:** SendGrid for most applications (good balance)
- **Consider AWS SES:** If already on AWS and high volume expected
- **Consider Mailgun:** If developer experience is priority and volume is moderate
- **Avoid self-hosted:** Unless you have email infrastructure expertise

**Real-Time Transport:**
- **Start with:** Polling for MVP/prototyping
- **Upgrade to SSE:** When real-time needed and one-way is sufficient
- **Use WebSocket:** When bidirectional or very high frequency needed
- **Consider:** Hybrid approach (SSE for notifications, WebSocket for collaboration)

**Notification Orchestration:**
- **Start with:** Custom service for simple use cases (single channel)
- **Consider Novu:** If multi-channel and want open-source
- **Consider Courier:** If want managed service and template management
- **Build custom:** Only if unique requirements or very high volume

### When to Deviate

- **High volume (1M+ notifications/month):** Consider AWS SES, custom orchestration
- **Multi-tenant SaaS:** Use notification center, tenant-isolated queues
- **Real-time collaboration:** WebSocket required, not optional
- **Strict compliance:** May require self-hosted email, on-premise solutions
- **Budget constraints:** AWS SES for email, custom service for orchestration
- **Rapid prototyping:** Use managed services (SendGrid, Courier) to move fast

## Synergies

### With Event-Driven Architecture

Notification decisions integrate with event-driven systems:

- **Kafka/RabbitMQ:** Use message queues for reliable notification delivery
- **Event sourcing:** Notifications can be derived from domain events
- **CQRS:** Separate read models for notification state, write models for sending
- **Saga pattern:** Notifications as compensating actions in distributed transactions

**Example:**
```java
@KafkaListener(topics = "order-events")
public void handleOrderEvent(OrderShippedEvent event) {
    // Publish notification event
    notificationEventPublisher.publish(
        new NotificationEvent(event.getUserId(), "order_shipped", event)
    );
}
```

### With Real-Time and Collaboration

- **WebSocket:** Use for real-time notification delivery when collaboration features exist
- **SSE:** Good complement to WebSocket (notifications via SSE, collaboration via WebSocket)
- **Presence:** Notification center can show "user is typing" or "user is online"

### With Settings and Preferences

- **User preferences:** Drive notification channel selection (email vs push vs in-app)
- **Quiet hours:** Respect user-defined quiet hours for push notifications
- **Notification frequency:** Digest mode vs real-time based on preferences
- **Tenant settings:** Multi-tenant applications need tenant-level notification settings

## Evolution Triggers

### When to Upgrade Notification Infrastructure

**From Polling to SSE/WebSocket:**
- User feedback indicates notifications feel slow
- Need for sub-second notification delivery
- High notification volume making polling inefficient

**From Single Channel to Multi-Channel:**
- Users requesting email/push/SMS options
- Need for channel-specific content (rich email, concise push)
- Compliance requirements for multiple channels

**From Custom to Managed Service:**
- Team spending too much time on notification infrastructure
- Deliverability issues (emails going to spam)
- Need for advanced features (analytics, A/B testing, template management)

**From Managed Service to Custom:**
- Costs scaling prohibitively with volume
- Unique requirements not met by managed services
- Need for complete control (compliance, data residency)

**From Simple to Orchestrated:**
- Complex notification workflows (multi-step, conditional)
- Need for notification templates and personalization
- Multiple channels requiring coordination

**From Badge to Notification Center:**
- Notification volume increasing (10+ per day per user)
- Notifications requiring actions
- Need for notification history and search
