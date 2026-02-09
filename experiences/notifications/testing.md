# Notifications -- Testing

## Contents

- [Testing Channel Delivery](#testing-channel-delivery)
- [Testing Preference Enforcement](#testing-preference-enforcement)
- [Testing Template Rendering](#testing-template-rendering)
- [Testing Timing and Scheduling](#testing-timing-and-scheduling)
- [Testing Rate Limiting](#testing-rate-limiting)
- [Testing Real-Time Delivery](#testing-real-time-delivery)
- [End-to-End Notification Flows](#end-to-end-notification-flows)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Testing Channel Delivery

Verify that notifications are successfully delivered through each channel.

### Email Delivery Testing

**Unit Test**:
```kotlin
@Test
fun `should send email notification`() {
    // Given
    val emailClient = mockk<EmailClient>()
    val emailChannel = EmailChannel(emailClient)
    val notification = RenderedNotification(
        subject = "Test Subject",
        body = "Test Body",
        recipient = Recipient(email = "test@example.com"),
        metadata = NotificationMetadata()
    )
    
    // When
    emailChannel.send(notification)
    
    // Then
    verify { emailClient.send(match { 
        it.to == "test@example.com" && 
        it.subject == "Test Subject" 
    }) }
}
```

**Integration Test with Test Containers**:
```kotlin
@Testcontainers
class EmailChannelIntegrationTest {
    @Container
    val mailServer = GenericContainer("mailhog/mailhog")
        .withExposedPorts(1025, 8025)
    
    @Test
    fun `should deliver email to mail server`() {
        val emailClient = EmailClient(
            host = mailServer.host,
            port = mailServer.getMappedPort(1025)
        )
        val channel = EmailChannel(emailClient)
        
        val result = channel.send(testNotification)
        
        assertThat(result.status).isEqualTo(DeliveryStatus.SUCCESS)
        
        // Verify email received
        val emails = mailServer.getEmails()
        assertThat(emails).hasSize(1)
        assertThat(emails[0].to).contains("test@example.com")
    }
}
```

**Contract Testing**:
```kotlin
@Test
fun `email should match expected format`() {
    val email = emailChannel.render(testNotification)
    
    assertThat(email.subject).isNotBlank()
    assertThat(email.htmlBody).contains("<!DOCTYPE html>")
    assertThat(email.textBody).isNotBlank() // Plain text fallback
    assertThat(email.to).matches(EMAIL_REGEX)
}
```

### Push Notification Testing

**Mock Push Service**:
```kotlin
@Test
fun `should send push notification`() {
    val pushService = mockk<PushService>()
    val pushChannel = PushChannel(pushService)
    
    val notification = RenderedNotification(
        subject = "New Message",
        body = "You have a new message",
        recipient = Recipient(deviceToken = "device-token-123"),
        metadata = NotificationMetadata()
    )
    
    pushChannel.send(notification)
    
    verify { pushService.send(match { 
        it.deviceToken == "device-token-123" &&
        it.title == "New Message"
    }) }
}
```

**Testing Push Payload**:
```kotlin
@Test
fun `push notification should not exceed length limits`() {
    val notification = createNotificationWithLongBody(500)
    val rendered = pushChannel.render(notification)
    
    assertThat(rendered.body.length).isLessThanOrEqualTo(200) // Push limit
    assertThat(rendered.title?.length).isLessThanOrEqualTo(50)
}
```

### In-App Notification Testing

**Repository Test**:
```kotlin
@DataJpaTest
class InAppNotificationRepositoryTest {
    @Autowired
    lateinit var repository: NotificationRepository
    
    @Test
    fun `should save in-app notification`() {
        val notification = InAppNotification(
            userId = "user-123",
            title = "Test",
            body = "Test body",
            type = NotificationType.INFORMATIONAL
        )
        
        val saved = repository.save(notification)
        
        assertThat(saved.id).isNotNull()
        assertThat(saved.read).isFalse()
        assertThat(saved.createdAt).isNotNull()
    }
    
    @Test
    fun `should find unread notifications`() {
        repository.save(createNotification(userId = "user-1", read = false))
        repository.save(createNotification(userId = "user-1", read = true))
        repository.save(createNotification(userId = "user-2", read = false))
        
        val unread = repository.findUnreadByUserId("user-1")
        
        assertThat(unread).hasSize(1)
        assertThat(unread[0].read).isFalse()
    }
}
```

## Testing Preference Enforcement

Ensure user preferences are correctly enforced.

### Opt-Out Testing

```kotlin
@Test
fun `should not send notification when user opted out`() {
    // Given
    val userId = "user-123"
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            enabled = false
        )
    )
    
    // When
    notificationService.sendNotification(
        NotificationRequest(
            userId = userId,
            channel = ChannelType.EMAIL,
            templateId = "test-template"
        )
    )
    
    // Then
    verify(exactly = 0) { emailChannel.send(any()) }
}
```

### Quiet Hours Testing

```kotlin
@Test
fun `should not send notification during quiet hours`() {
    // Given
    val userId = "user-123"
    val timezone = "America/New_York"
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            quietHoursStart = LocalTime.of(22, 0), // 10 PM
            quietHoursEnd = LocalTime.of(8, 0),   // 8 AM
            timezone = timezone
        )
    )
    
    // Mock current time to 11 PM user's timezone
    mockkStatic(Clock::class)
    val clock = Clock.fixed(
        Instant.parse("2026-02-09T04:00:00Z"), // 11 PM EST
        ZoneId.of(timezone)
    )
    every { Clock.system(ZoneId.of(timezone)) } returns clock
    
    // When
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
    )
    
    // Then
    verify(exactly = 0) { emailChannel.send(any()) }
    // Should be scheduled for later
    verify { scheduler.schedule(any(), any<Instant>()) }
}
```

### Critical Notification Override

```kotlin
@Test
fun `should send critical notification even during quiet hours`() {
    // Given
    val userId = "user-123"
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            quietHoursStart = LocalTime.of(22, 0),
            quietHoursEnd = LocalTime.of(8, 0)
        )
    )
    mockCurrentTime(LocalTime.of(23, 0)) // 11 PM
    
    // When
    notificationService.sendNotification(
        NotificationRequest(
            userId = userId,
            channel = ChannelType.EMAIL,
            templateId = "security-alert",
            isCritical = true // Critical override
        )
    )
    
    // Then
    verify { emailChannel.send(any()) } // Should send despite quiet hours
}
```

### Channel Preference Testing

```kotlin
@Test
fun `should respect channel-specific preferences`() {
    // Given
    val userId = "user-123"
    preferenceRepository.saveAll(listOf(
        NotificationPreference(userId = userId, channel = ChannelType.EMAIL, enabled = true),
        NotificationPreference(userId = userId, channel = ChannelType.PUSH, enabled = false),
        NotificationPreference(userId = userId, channel = ChannelType.SMS, enabled = true)
    ))
    
    // When
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.PUSH, templateId = "test")
    )
    
    // Then
    verify(exactly = 0) { pushChannel.send(any()) }
}
```

## Testing Template Rendering

Verify templates render correctly with various data inputs.

### Template Variable Substitution

```kotlin
@Test
fun `should substitute template variables`() {
    val template = NotificationTemplate(
        id = "order-confirmed",
        channels = mapOf(
            ChannelType.EMAIL to ChannelTemplate(
                subject = "Order #{{orderNumber}} Confirmed",
                body = "Total: {{orderTotal}}"
            )
        )
    )
    
    val rendered = templateEngine.render(
        templateId = "order-confirmed",
        channel = ChannelType.EMAIL,
        data = mapOf(
            "orderNumber" to "12345",
            "orderTotal" to "$99.99"
        )
    )
    
    assertThat(rendered.subject).isEqualTo("Order #12345 Confirmed")
    assertThat(rendered.body).contains("Total: $99.99")
    assertThat(rendered.body).doesNotContain("{{orderNumber}}") // No unsubstituted variables
}
```

### Missing Variable Handling

```kotlin
@Test
fun `should handle missing template variables gracefully`() {
    val rendered = templateEngine.render(
        templateId = "order-confirmed",
        channel = ChannelType.EMAIL,
        data = mapOf("orderNumber" to "12345") // Missing orderTotal
    )
    
    // Should either throw exception or use default
    assertThatThrownBy { rendered }
        .isInstanceOf(TemplateException::class.java)
        .hasMessageContaining("orderTotal")
}
```

### Multi-Channel Template Rendering

```kotlin
@Test
fun `should render different content per channel`() {
    val template = NotificationTemplate(
        id = "test",
        channels = mapOf(
            ChannelType.EMAIL to ChannelTemplate(
                subject = "Email: {{message}}",
                body = "Full email body with {{message}}"
            ),
            ChannelType.PUSH to ChannelTemplate(
                subject = "Push: {{message}}",
                body = "Short: {{message}}"
            )
        )
    )
    
    val emailRendered = templateEngine.render("test", ChannelType.EMAIL, mapOf("message" to "Hello"))
    val pushRendered = templateEngine.render("test", ChannelType.PUSH, mapOf("message" to "Hello"))
    
    assertThat(emailRendered.body.length).isGreaterThan(pushRendered.body.length)
    assertThat(emailRendered.subject).startsWith("Email:")
    assertThat(pushRendered.subject).startsWith("Push:")
}
```

### Locale-Specific Rendering

```kotlin
@Test
fun `should render template in user locale`() {
    val templateEn = NotificationTemplate(
        id = "welcome",
        channels = mapOf(
            ChannelType.EMAIL to ChannelTemplate(
                subject = "Welcome!",
                body = "Hello {{name}}"
            )
        ),
        locale = "en"
    )
    
    val templateEs = templateEn.copy(
        channels = mapOf(
            ChannelType.EMAIL to ChannelTemplate(
                subject = "¡Bienvenido!",
                body = "Hola {{name}}"
            )
        ),
        locale = "es"
    )
    
    val renderedEn = templateEngine.render("welcome", ChannelType.EMAIL, mapOf("name" to "John"), "en")
    val renderedEs = templateEngine.render("welcome", ChannelType.EMAIL, mapOf("name" to "John"), "es")
    
    assertThat(renderedEn.subject).isEqualTo("Welcome!")
    assertThat(renderedEs.subject).isEqualTo("¡Bienvenido!")
}
```

## Testing Timing and Scheduling

Test scheduled notifications and timezone handling.

### Scheduled Notification Testing

```kotlin
@Test
fun `should schedule notification for later delivery`() {
    val request = NotificationRequest(
        userId = "user-123",
        channel = ChannelType.EMAIL,
        templateId = "test",
        scheduledFor = Instant.now().plusSeconds(3600) // 1 hour from now
    )
    
    notificationService.scheduleNotification(request)
    
    // Verify scheduled
    val scheduled = schedulerRepository.findScheduled(request.id)
    assertThat(scheduled).isNotNull()
    assertThat(scheduled.scheduledFor).isAfter(Instant.now())
    
    // Verify not sent immediately
    verify(exactly = 0) { emailChannel.send(any()) }
}
```

### Timezone Handling

```kotlin
@Test
fun `should convert scheduled time to user timezone`() {
    val userTimezone = "America/Los_Angeles" // PST
    val scheduledTime = LocalDateTime.of(2026, 2, 10, 9, 0) // 9 AM PST
    
    val request = NotificationRequest(
        userId = "user-123",
        channel = ChannelType.EMAIL,
        templateId = "test",
        scheduledForLocal = scheduledTime,
        timezone = userTimezone
    )
    
    notificationService.scheduleNotification(request)
    
    val scheduled = schedulerRepository.findScheduled(request.id)
    // Should be stored as UTC
    val expectedUtc = scheduledTime.atZone(ZoneId.of(userTimezone)).toInstant()
    assertThat(scheduled.scheduledFor).isEqualTo(expectedUtc)
}
```

### Quiet Hours Timezone Testing

```kotlin
@Test
fun `should respect quiet hours in user timezone not server timezone`() {
    // Server is in UTC
    // User is in PST (UTC-8)
    val userId = "user-pst"
    val userTimezone = "America/Los_Angeles"
    
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            quietHoursStart = LocalTime.of(22, 0), // 10 PM PST
            quietHoursEnd = LocalTime.of(8, 0),   // 8 AM PST
            timezone = userTimezone
        )
    )
    
    // Current server time: 6 AM UTC = 10 PM PST (previous day) = in quiet hours
    mockCurrentTime(Instant.parse("2026-02-10T06:00:00Z"))
    
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
    )
    
    // Should not send (quiet hours in user's timezone)
    verify(exactly = 0) { emailChannel.send(any()) }
}
```

## Testing Rate Limiting

Verify frequency caps are enforced.

### Frequency Cap Enforcement

```kotlin
@Test
fun `should enforce frequency cap`() {
    val userId = "user-123"
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            frequencyCap = 3 // Max 3 per day
        )
    )
    
    // Send 3 notifications
    repeat(3) {
        notificationService.sendNotification(
            NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
        )
    }
    
    // 4th should be blocked
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
    )
    
    verify(exactly = 3) { emailChannel.send(any()) } // Only 3 sent
}
```

### Per-Channel Frequency Caps

```kotlin
@Test
fun `should enforce frequency cap per channel independently`() {
    val userId = "user-123"
    preferenceRepository.saveAll(listOf(
        NotificationPreference(userId = userId, channel = ChannelType.EMAIL, frequencyCap = 2),
        NotificationPreference(userId = userId, channel = ChannelType.PUSH, frequencyCap = 5)
    ))
    
    // Send 2 emails (at cap)
    repeat(2) {
        notificationService.sendNotification(
            NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
        )
    }
    
    // Send 5 pushes (at cap)
    repeat(5) {
        notificationService.sendNotification(
            NotificationRequest(userId = userId, channel = ChannelType.PUSH, templateId = "test")
        )
    }
    
    // Try to exceed caps
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
    )
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.PUSH, templateId = "test")
    )
    
    verify(exactly = 2) { emailChannel.send(any()) }
    verify(exactly = 5) { pushChannel.send(any()) }
}
```

### Frequency Cap Reset

```kotlin
@Test
fun `should reset frequency cap after time window`() {
    val userId = "user-123"
    preferenceRepository.save(
        NotificationPreference(
            userId = userId,
            channel = ChannelType.EMAIL,
            frequencyCap = 2,
            frequencyCapWindow = Duration.ofHours(24)
        )
    )
    
    // Send 2 notifications
    repeat(2) {
        notificationService.sendNotification(
            NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
        )
    }
    
    // Advance time by 25 hours
    mockCurrentTime(Instant.now().plusSeconds(25 * 3600))
    
    // Should be able to send again
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.EMAIL, templateId = "test")
    )
    
    verify(exactly = 3) { emailChannel.send(any()) }
}
```

## Testing Real-Time Delivery

Test WebSocket and SSE connections for in-app notifications.

### WebSocket Connection Testing

```kotlin
@Test
fun `should establish WebSocket connection`() {
    val userId = "user-123"
    val session = mockk<WebSocketSession>()
    
    notificationWebSocketHandler.afterConnectionEstablished(session)
    
    // Verify session stored
    assertThat(notificationWebSocketHandler.getSession(userId)).isEqualTo(session)
}
```

### WebSocket Message Delivery

```kotlin
@Test
fun `should deliver notification via WebSocket`() {
    val userId = "user-123"
    val session = mockk<WebSocketSession>(relaxed = true)
    notificationWebSocketHandler.afterConnectionEstablished(session)
    
    val notification = InAppNotification(
        userId = userId,
        title = "Test",
        body = "Test body"
    )
    
    notificationWebSocketHandler.sendNotification(userId, notification)
    
    verify { session.sendMessage(any<TextMessage>()) }
}
```

### WebSocket Reconnection Testing

```typescript
// Frontend test (Jest/Vitest)
describe('WebSocket reconnection', () => {
  it('should reconnect on connection close', async () => {
    const { connect, notifications } = useNotifications()
    
    const ws = connect('user-123')
    
    // Simulate connection close
    ws.close()
    
    // Wait for reconnection
    await waitFor(() => {
      expect(ws.readyState).toBe(WebSocket.OPEN)
    }, { timeout: 10000 })
  })
})
```

### SSE Testing

```kotlin
@Test
fun `should stream notifications via SSE`() {
    val userId = "user-123"
    val emitter = SseEmitter(Long.MAX_VALUE)
    
    val controller = NotificationSSEController(notificationService)
    val response = controller.streamNotifications(userId, mockHttpServletResponse())
    
    // Send notification
    notificationService.sendNotification(
        NotificationRequest(userId = userId, channel = ChannelType.IN_APP, templateId = "test")
    )
    
    // Verify SSE event sent
    // (Would need to capture SSE events in test)
}
```

## End-to-End Notification Flows

Test complete notification flows from trigger to delivery.

### E2E Test with Playwright

```typescript
// integration/playwright/tests/notifications.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Notification Flow', () => {
  test('user receives email notification after order', async ({ page, context }) => {
    // Login
    await page.goto('/login')
    await page.fill('[data-testid=email]', 'test@example.com')
    await page.fill('[data-testid=password]', 'password')
    await page.click('[data-testid=login-button]')
    
    // Place order
    await page.goto('/products')
    await page.click('[data-testid=product-123]')
    await page.click('[data-testid=add-to-cart]')
    await page.click('[data-testid=checkout]')
    await page.click('[data-testid=place-order]')
    
    // Verify order confirmation shown
    await expect(page.locator('[data-testid=order-confirmed]')).toBeVisible()
    
    // Check email was sent (via test email service)
    const emails = await fetchTestEmails('test@example.com')
    expect(emails).toHaveLength(1)
    expect(emails[0].subject).toContain('Order Confirmed')
  })
  
  test('user can disable email notifications', async ({ page }) => {
    await page.goto('/settings/notifications')
    
    // Disable email notifications
    await page.click('[data-testid=email-notifications-toggle]')
    await page.click('[data-testid=save-preferences]')
    
    // Trigger notification
    await triggerTestNotification(page)
    
    // Verify email not sent
    const emails = await fetchTestEmails('test@example.com')
    expect(emails).toHaveLength(0)
  })
  
  test('in-app notification appears in real-time', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Trigger notification from another session
    await triggerNotificationFromBackend('user-123', 'Test notification')
    
    // Verify notification appears without refresh
    await expect(page.locator('[data-testid=notification-toast]')).toBeVisible()
    await expect(page.locator('[data-testid=notification-toast]')).toContainText('Test notification')
  })
})
```

### E2E Test with Spring Boot TestContainers

```kotlin
@SpringBootTest
@Testcontainers
class NotificationE2ETest {
    @Container
    val mailServer = GenericContainer("mailhog/mailhog")
    
    @Container
    val kafka = KafkaContainer()
    
    @Autowired
    lateinit var orderService: OrderService
    
    @Autowired
    lateinit var notificationService: NotificationService
    
    @Test
    fun `complete notification flow from order to email`() {
        // Create order
        val order = orderService.createOrder(
            CreateOrderRequest(
                userId = "user-123",
                items = listOf(OrderItem(productId = "prod-1", quantity = 1))
            )
        )
        
        // Verify notification sent
        val emails = mailServer.getEmails()
        assertThat(emails).hasSize(1)
        assertThat(emails[0].to).contains("user-123@example.com")
        assertThat(emails[0].subject).contains(order.id)
    }
}
```

## QA and Test Engineer Perspective

### Test Data Management

**Challenge**: Creating realistic test data for notifications (user preferences, templates, delivery states).

**Approach**:
- Use factories/builders for test data creation
- Create test fixtures for common scenarios (user with all channels enabled, user with quiet hours, etc.)
- Use database seeding for integration tests
- Mock external services (email providers, push services) in unit tests

**Example**:
```kotlin
object NotificationTestFixtures {
    fun userWithAllChannelsEnabled(userId: String) = listOf(
        NotificationPreference(userId = userId, channel = ChannelType.EMAIL, enabled = true),
        NotificationPreference(userId = userId, channel = ChannelType.PUSH, enabled = true),
        NotificationPreference(userId = userId, channel = ChannelType.SMS, enabled = true)
    )
    
    fun userWithQuietHours(userId: String) = NotificationPreference(
        userId = userId,
        channel = ChannelType.EMAIL,
        enabled = true,
        quietHoursStart = LocalTime.of(22, 0),
        quietHoursEnd = LocalTime.of(8, 0)
    )
}
```

### Test Environment Setup

**Challenge**: Setting up test environments that mirror production (email servers, push services, WebSocket servers).

**Approach**:
- Use TestContainers for email servers (MailHog, GreenMail)
- Use local Kafka/RabbitMQ instances or TestContainers
- Mock push notification services
- Use in-memory databases for fast tests
- Separate unit tests (fast, mocked) from integration tests (slower, real services)

### Notification Delivery Verification

**Challenge**: Verifying notifications were actually delivered, not just queued.

**Approach**:
- For email: Use test email servers (MailHog) that expose API to check received emails
- For push: Mock push service and verify method calls
- For in-app: Query notification repository directly
- Add delivery tracking/logging that can be queried in tests
- Use event sourcing or audit logs to verify delivery

**Example**:
```kotlin
@Test
fun `verify email delivered to test server`() {
    notificationService.sendNotification(testRequest)
    
    // Wait for async processing
    await().atMost(5, SECONDS).until {
        mailServer.getEmails().isNotEmpty()
    }
    
    val emails = mailServer.getEmails()
    assertThat(emails).hasSize(1)
}
```

### Testing Asynchronous Flows

**Challenge**: Notifications are often sent asynchronously via queues, making it hard to test synchronously.

**Approach**:
- Use `@Transactional` with `@Commit` annotation to ensure data is committed in tests
- Use `awaitility` or similar libraries to wait for async operations
- Test both synchronous (unit) and asynchronous (integration) paths
- Use test queues that process messages synchronously in tests
- Add test endpoints that trigger immediate processing

**Example**:
```kotlin
@Test
fun `should process queued notification`() {
    // Send to queue
    notificationProducer.sendNotification(testEvent)
    
    // Process queue synchronously in test
    notificationConsumer.processQueue()
    
    // Verify delivery
    verify { emailChannel.send(any()) }
}
```

### Edge Case Testing

**Challenge**: Many edge cases in notifications (missing data, invalid preferences, service failures).

**Approach**:
- Test with null/empty template variables
- Test with invalid user IDs
- Test with missing preferences (default behavior)
- Test with service failures (email service down, push service error)
- Test with malformed data
- Test with concurrent notifications to same user

**Example**:
```kotlin
@Test
fun `should handle email service failure gracefully`() {
    every { emailClient.send(any()) } throws EmailServiceException("Service unavailable")
    
    val result = notificationService.sendNotification(testRequest)
    
    assertThat(result.status).isEqualTo(DeliveryStatus.FAILED)
    // Should be queued for retry
    verify { retryQueue.add(any()) }
}
```

### Performance and Load Testing

**Challenge**: Notification systems need to handle high volumes (thousands of notifications per second).

**Approach**:
- Load test notification sending with realistic volumes
- Test queue processing under load
- Test database queries with large notification histories
- Test WebSocket connections under concurrent load
- Monitor for memory leaks in long-running notification processes
- Test rate limiting under load

**Example**:
```kotlin
@Test
fun `should handle high volume notification sending`() {
    val requests = (1..10000).map { createTestRequest("user-$it") }
    
    val startTime = Instant.now()
    requests.forEach { notificationService.sendNotification(it) }
    val duration = Duration.between(startTime, Instant.now())
    
    assertThat(duration.seconds).isLessThan(10) // Should complete in < 10 seconds
    verify(exactly = 10000) { emailChannel.send(any()) }
}
```
