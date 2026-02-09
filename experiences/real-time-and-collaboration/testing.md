# Testing: Real-Time & Collaboration

## Contents

- [WebSocket Connection Testing](#websocket-connection-testing)
- [Presence Testing](#presence-testing)
- [Conflict Resolution Testing](#conflict-resolution-testing)
- [Connection Resilience Testing](#connection-resilience-testing)
- [Performance Testing](#performance-testing)
- [Multi-Tab Testing](#multi-tab-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## WebSocket Connection Testing

Test the complete WebSocket lifecycle: connect, subscribe, receive messages, and reconnect.

### Connect and Subscribe

```typescript
// Playwright WebSocket test
import { test, expect } from '@playwright/test'

test('WebSocket connects and subscribes to invoice updates', async ({ page }) => {
  await page.goto('/invoices')
  
  // Wait for WebSocket connection
  await page.waitForFunction(() => {
    return window.wsStatus === 'connected'
  })
  
  // Subscribe to invoice topic
  await page.evaluate(() => {
    window.stompClient.subscribe('/topic/invoices/123', (message) => {
      window.lastMessage = JSON.parse(message.body)
    })
  })
  
  // Trigger server-side update
  await page.click('[data-testid="update-invoice-btn"]')
  
  // Verify message received
  const message = await page.evaluate(() => window.lastMessage)
  expect(message).toHaveProperty('type', 'invoice-updated')
  expect(message).toHaveProperty('id', '123')
})
```

### Receive Messages

```kotlin
// Spring Boot WebSocket test
@SpringBootTest
@AutoConfigureMockMvc
class WebSocketTest {
    @Autowired
    lateinit var messagingTemplate: SimpMessagingTemplate
    
    @Test
    fun `client receives invoice update message`() {
        val latch = CountDownLatch(1)
        val receivedMessages = mutableListOf<InvoiceUpdateEvent>()
        
        // Simulate client subscription
        val session = mock(WebSocketSession::class.java)
        val subscription = StompSessionHandlerAdapter()
        
        // Send test message
        messagingTemplate.convertAndSend("/topic/invoices/123", 
            InvoiceUpdateEvent("123", Invoice(amount = BigDecimal("100.00")))
        )
        
        // Verify message was sent (integration test would verify client receives it)
        verify(messagingTemplate).convertAndSend(
            eq("/topic/invoices/123"),
            any<InvoiceUpdateEvent>()
        )
    }
}
```

### Reconnect After Disconnect

```typescript
test('WebSocket reconnects after disconnect', async ({ page }) => {
  await page.goto('/invoices')
  
  // Establish connection
  await page.waitForFunction(() => window.wsStatus === 'connected')
  
  // Simulate network failure
  await page.route('ws://localhost:8080/ws', route => route.abort())
  
  // Wait for reconnection attempt
  await page.waitForFunction(() => {
    return window.reconnectAttempts > 0
  }, { timeout: 5000 })
  
  // Restore connection
  await page.unroute('ws://localhost:8080/ws')
  
  // Verify reconnection
  await page.waitForFunction(() => {
    return window.wsStatus === 'connected'
  }, { timeout: 10000 })
})
```

## Presence Testing

Test that presence indicators accurately reflect user online/offline status.

### User Appears Online

```typescript
test('user appears online when connected', async ({ page, context }) => {
  // Open page as User A
  await page.goto('/document/123')
  await page.waitForFunction(() => window.wsStatus === 'connected')
  
  // Open second browser as User B
  const page2 = await context.newPage()
  await page2.goto('/document/123')
  
  // User B should see User A as online
  await expect(page2.locator('[data-testid="presence-indicator"]'))
    .toContainText('1 other user viewing')
})
```

### User Goes Offline

```typescript
test('user disappears from presence when disconnected', async ({ page, context }) => {
  const page1 = await context.newPage()
  const page2 = await context.newPage()
  
  await page1.goto('/document/123')
  await page2.goto('/document/123')
  
  // Both users online
  await expect(page2.locator('[data-testid="presence"]'))
    .toContainText('1 other user viewing')
  
  // Close page1 (simulates disconnect)
  await page1.close()
  
  // Wait for presence cleanup (heartbeat timeout)
  await page2.waitForTimeout(65000) // Slightly more than heartbeat timeout
  
  // User 1 should no longer appear
  await expect(page2.locator('[data-testid="presence"]'))
    .not.toContainText('other user')
})
```

### Stale Presence Cleanup

```kotlin
@Test
fun `stale presence is cleaned up after timeout`() {
    val userId = "user-123"
    val resourceId = "doc-456"
    
    // Set presence
    presenceService.updatePresence(userId, resourceId, "document")
    
    // Verify presence exists
    val presence = presenceService.getPresence(resourceId, "document")
    assertThat(presence).contains(userId)
    
    // Simulate timeout (don't send heartbeat)
    Thread.sleep(130000) // 2 minutes + buffer
    
    // Run cleanup
    presenceService.cleanupStalePresence()
    
    // Verify presence removed
    val updatedPresence = presenceService.getPresence(resourceId, "document")
    assertThat(updatedPresence).doesNotContain(userId)
}
```

## Conflict Resolution Testing

Test that simultaneous edits are handled correctly without data loss.

### Two Users Edit Simultaneously

```typescript
test('conflict resolution handles simultaneous edits', async ({ context }) => {
  const page1 = await context.newPage()
  const page2 = await context.newPage()
  
  await page1.goto('/invoice/123/edit')
  await page2.goto('/invoice/123/edit')
  
  // User 1 edits amount
  await page1.fill('[data-testid="amount-input"]', '100.00')
  await page1.click('[data-testid="save-btn"]')
  
  // User 2 edits amount simultaneously (before seeing User 1's change)
  await page2.fill('[data-testid="amount-input"]', '200.00')
  await page2.click('[data-testid="save-btn"]')
  
  // Wait for conflict resolution
  await page1.waitForTimeout(1000)
  await page2.waitForTimeout(1000)
  
  // Verify conflict UI appears
  await expect(page2.locator('[data-testid="conflict-resolution"]'))
    .toBeVisible()
  
  // Verify both users see resolved state
  const amount1 = await page1.locator('[data-testid="amount-input"]').inputValue()
  const amount2 = await page2.locator('[data-testid="amount-input"]').inputValue()
  
  // Both should see the same resolved value (last-write-wins or merged)
  expect(amount1).toBe(amount2)
})
```

### Correct Merge/Resolution

```kotlin
@Test
fun `last-write-wins conflict resolution works correctly`() {
    val invoice = Invoice(id = "123", amount = BigDecimal("100.00"), version = 1)
    repository.save(invoice)
    
    // User 1 updates
    val update1 = InvoiceUpdate(amount = BigDecimal("150.00"), version = 1)
    val result1 = invoiceService.updateInvoice("123", update1)
    
    // User 2 tries to update with stale version
    val update2 = InvoiceUpdate(amount = BigDecimal("200.00"), version = 1) // Stale!
    
    assertThrows<ConflictException> {
        invoiceService.updateInvoice("123", update2)
    }
    
    // Verify first update succeeded
    val saved = repository.findById("123")
    assertThat(saved.amount).isEqualByComparingTo(BigDecimal("150.00"))
    assertThat(saved.version).isEqualTo(2)
}
```

## Connection Resilience Testing

Test behavior when network fails, server restarts, or connections drop.

### Network Drop

```typescript
test('application handles network drop gracefully', async ({ page }) => {
  await page.goto('/dashboard')
  
  // Verify real-time updates working
  await page.waitForFunction(() => window.wsStatus === 'connected')
  
  // Simulate network failure
  await page.context().setOffline(true)
  
  // Verify fallback to polling
  await expect(page.locator('[data-testid="connection-status"]'))
    .toContainText('Disconnected')
  
  // Verify data still loads via polling
  await expect(page.locator('[data-testid="revenue"]'))
    .toBeVisible({ timeout: 10000 })
  
  // Restore network
  await page.context().setOffline(false)
  
  // Verify reconnection
  await page.waitForFunction(() => window.wsStatus === 'connected', { timeout: 15000 })
})
```

### Server Restart

```kotlin
@Test
fun `clients reconnect after server restart`() {
    // Start server
    val server = startWebSocketServer()
    
    // Connect client
    val client = connectWebSocketClient()
    assertThat(client.isConnected).isTrue()
    
    // Restart server
    server.stop()
    Thread.sleep(2000)
    server.start()
    
    // Client should reconnect
    await().atMost(30, SECONDS).until {
        client.isConnected
    }
    
    // Verify subscription restored
    assertThat(client.subscriptions).isNotEmpty()
}
```

### Reconnection with Message Replay

```typescript
test('missed messages are replayed after reconnection', async ({ page }) => {
  await page.goto('/invoices')
  
  // Disconnect
  await page.evaluate(() => window.ws.close())
  
  // Simulate server sending messages while disconnected
  await page.evaluate(() => {
    // Server would queue these messages
    window.missedMessages = [
      { type: 'invoice-updated', id: '123' },
      { type: 'invoice-updated', id: '456' }
    ]
  })
  
  // Reconnect
  await page.evaluate(() => window.reconnect())
  await page.waitForFunction(() => window.wsStatus === 'connected')
  
  // Verify missed messages received
  const received = await page.evaluate(() => window.receivedMessages)
  expect(received).toHaveLength(2)
})
```

## Performance Testing

Test message throughput, connection limits, and latency under load.

### Message Throughput

```kotlin
@Test
fun `handles high message throughput`() {
    val messageCount = 10000
    val latch = CountDownLatch(messageCount)
    val receivedMessages = ConcurrentLinkedQueue<InvoiceEvent>()
    
    // Connect client
    val client = connectWebSocketClient()
    client.subscribe("/topic/invoices") { message ->
        receivedMessages.add(objectMapper.readValue(message.body, InvoiceEvent::class.java))
        latch.countDown()
    }
    
    // Send messages rapidly
    val startTime = System.currentTimeMillis()
    repeat(messageCount) { i ->
        messagingTemplate.convertAndSend("/topic/invoices", 
            InvoiceEvent(id = "invoice-$i")
        )
    }
    
    // Wait for all messages
    assertThat(latch.await(30, SECONDS)).isTrue()
    
    val duration = System.currentTimeMillis() - startTime
    val throughput = messageCount.toDouble() / (duration / 1000.0)
    
    // Verify throughput > 1000 messages/second
    assertThat(throughput).isGreaterThan(1000.0)
    assertThat(receivedMessages.size).isEqualTo(messageCount)
}
```

### Connection Count Limits

```kotlin
@Test
fun `server handles maximum concurrent connections`() {
    val maxConnections = 1000
    val clients = mutableListOf<WebSocketClient>()
    
    try {
        repeat(maxConnections) {
            val client = connectWebSocketClient()
            clients.add(client)
            assertThat(client.isConnected).isTrue()
        }
        
        // Verify all connected
        assertThat(clients.count { it.isConnected }).isEqualTo(maxConnections)
        
        // Verify server metrics
        val metrics = webSocketMetrics.getConnectionCount()
        assertThat(metrics).isEqualTo(maxConnections)
    } finally {
        clients.forEach { it.disconnect() }
    }
}
```

### Latency Under Load

```typescript
test('message latency remains low under load', async ({ page }) => {
  await page.goto('/dashboard')
  
  const latencies: number[] = []
  
  // Measure latency for 100 messages
  await page.evaluate(() => {
    window.latencies = []
    window.stompClient.subscribe('/topic/metrics', (message) => {
      const event = JSON.parse(message.body)
      const latency = Date.now() - event.timestamp
      window.latencies.push(latency)
    })
  })
  
  // Trigger 100 updates
  for (let i = 0; i < 100; i++) {
    await page.click('[data-testid="trigger-update"]')
    await page.waitForTimeout(10) // Small delay between triggers
  }
  
  // Wait for all messages
  await page.waitForFunction(() => window.latencies.length >= 100, { timeout: 30000 })
  
  const latencies = await page.evaluate(() => window.latencies)
  const avgLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length
  const p95Latency = latencies.sort((a, b) => a - b)[Math.floor(latencies.length * 0.95)]
  
  // Verify latency targets
  expect(avgLatency).toBeLessThan(100) // < 100ms average
  expect(p95Latency).toBeLessThan(200) // < 200ms p95
})
```

## Multi-Tab Testing

Test behavior when the same application is open in multiple browser tabs.

```typescript
test('multiple tabs share connection efficiently', async ({ context }) => {
  // Open first tab
  const tab1 = await context.newPage()
  await tab1.goto('/dashboard')
  await tab1.waitForFunction(() => window.wsStatus === 'connected')
  
  // Open second tab
  const tab2 = await context.newPage()
  await tab2.goto('/dashboard')
  
  // Verify connection sharing (if using SharedWorker)
  const connections1 = await tab1.evaluate(() => window.wsConnectionCount)
  const connections2 = await tab2.evaluate(() => window.wsConnectionCount)
  
  // Should share connection or at least coordinate
  expect(connections1 + connections2).toBeLessThanOrEqual(2)
  
  // Update in tab1, verify tab2 receives it
  await tab1.click('[data-testid="update-data"]')
  
  await expect(tab2.locator('[data-testid="data-display"]'))
    .toContainText('updated', { timeout: 5000 })
})
```

## QA and Test Engineer Perspective

### Test Strategy for Real-Time Features

**1. Connection Lifecycle Testing**
- Test connection establishment, subscription, message receipt, and disconnection
- Verify reconnection logic with exponential backoff
- Test connection state UI indicators (connected/connecting/disconnected)

**2. Presence Accuracy Testing**
- Verify users appear online when connected
- Verify users disappear when disconnected
- Test stale presence cleanup (timeout scenarios)
- Test presence with multiple users viewing same resource

**3. Conflict Resolution Testing**
- Test simultaneous edits from multiple users
- Verify conflict detection and resolution UI
- Test different conflict resolution strategies (last-write-wins, merge, CRDT)
- Verify no data loss during conflicts

**4. Resilience Testing**
- Test network drop scenarios (WiFi disconnect, airplane mode)
- Test server restart scenarios
- Test reconnection with message replay
- Test fallback to polling when WebSocket fails

**5. Performance Testing**
- Test message throughput under load
- Test connection count limits
- Test latency under various load conditions
- Test memory leaks from long-running connections

**6. Multi-Tab Testing**
- Test behavior with multiple tabs open
- Verify connection sharing or coordination
- Test that updates in one tab appear in others
- Test that closing one tab doesn't affect others

### Test Automation Challenges

Real-time behavior is inherently non-deterministic. Strategies to handle this:

- **Use timeouts generously**: Real-time updates may have variable latency
- **Wait for specific states**: Don't rely on fixed delays, wait for UI state changes
- **Mock WebSocket in unit tests**: Use test doubles for deterministic unit testing
- **Use integration tests for real behavior**: Test actual WebSocket connections in integration tests
- **Test flakiness**: Real-time tests may be flaky—investigate root causes (timing, race conditions)

### Tools and Frameworks

- **Playwright**: Browser automation with WebSocket support
- **Spring Test**: WebSocket testing utilities for Spring Boot
- **MockWebSocket**: Mock WebSocket server for testing
- **Artillery**: Load testing for WebSocket connections
- **k6**: Performance testing with WebSocket support
