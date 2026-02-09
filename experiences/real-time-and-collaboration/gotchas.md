# Gotchas: Real-Time & Collaboration

## Contents

- [WebSocket Connections Not Authenticated](#websocket-connections-not-authenticated)
- [No Reconnection Strategy](#no-reconnection-strategy)
- [Presence Indicators Showing Stale Data](#presence-indicators-showing-stale-data)
- [Real-Time Updates Causing Layout Shift](#real-time-updates-causing-layout-shift)
- [Too Many Subscriptions](#too-many-subscriptions)
- [Memory Leaks from Event Listeners](#memory-leaks-from-event-listeners)
- [Multiple Tabs Opening Separate Connections](#multiple-tabs-opening-separate-connections)
- [Conflict Resolution Showing Confusing UI](#conflict-resolution-showing-confusing-ui)
- [Real-Time Updates Not Respecting Scroll Position](#real-time-updates-not-respecting-scroll-position)
- [WebSocket Through Proxies Dropping Connections](#websocket-through-proxies-dropping-connections)
- [Testing Difficulty](#testing-difficulty)

## WebSocket Connections Not Authenticated

**Problem:** Anyone can connect to your WebSocket endpoint and subscribe to topics, potentially accessing sensitive data.

**Example:**
```kotlin
// BAD: No authentication
@Configuration
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws") // No auth required!
    }
}
```

**Solution:** Authenticate during handshake or validate on each message:
```kotlin
@Component
class AuthChannelInterceptor : ChannelInterceptor {
    override fun preSend(message: Message<*>, channel: MessageChannel): Message<*>? {
        val accessor = StompHeaderAccessor.wrap(message)
        val token = accessor.getFirstNativeHeader("Authorization")
        
        if (token == null || !validateToken(token)) {
            throw AuthenticationException("Invalid token")
        }
        
        // Set user principal
        accessor.user = getUserFromToken(token)
        return MessageBuilder.createMessage(message.payload, accessor.messageHeaders)
    }
}

@Configuration
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureClientInboundChannel(registration: ChannelRegistration) {
        registration.interceptors(authChannelInterceptor)
    }
}
```

## No Reconnection Strategy

**Problem:** One network blip causes permanent disconnection. Users must manually refresh the page.

**Example:**
```typescript
// BAD: No reconnection
const ws = new WebSocket('ws://localhost:8080/ws')
ws.onclose = () => {
  console.log('Connection closed') // That's it - no reconnection!
}
```

**Solution:** Implement exponential backoff reconnection:
```typescript
let reconnectAttempts = 0
const maxAttempts = 10

function connect() {
  const ws = new WebSocket('ws://localhost:8080/ws')
  
  ws.onopen = () => {
    reconnectAttempts = 0 // Reset on success
    // Restore subscriptions
    restoreSubscriptions()
  }
  
  ws.onclose = () => {
    if (reconnectAttempts < maxAttempts) {
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
      reconnectAttempts++
      setTimeout(connect, delay)
    }
  }
  
  ws.onerror = () => {
    // Errors are handled by onclose
  }
}
```

## Presence Indicators Showing Stale Data

**Problem:** "John is online" but John closed his laptop 30 minutes ago. Stale presence breaks trust.

**Example:**
```kotlin
// BAD: No timeout, presence never expires
fun updatePresence(userId: String, resourceId: String) {
    redisTemplate.opsForValue().set("presence:$resourceId:$userId", "online")
    // No TTL - stays forever!
}
```

**Solution:** Use TTL and heartbeat mechanism:
```kotlin
fun updatePresence(userId: String, resourceId: String) {
    val key = "presence:$resourceId:$userId"
    // Set with 2-minute TTL
    redisTemplate.opsForValue().set(key, "online", Duration.ofMinutes(2))
}

// Client sends heartbeat every 30 seconds
@Scheduled(fixedRate = 30000)
fun sendHeartbeat() {
    if (wsConnected) {
        messagingTemplate.convertAndSend("/app/presence/heartbeat", Heartbeat())
    }
}
```

## Real-Time Updates Causing Layout Shift

**Problem:** New data arrives and pushes content around while the user is reading, creating jarring UX.

**Example:**
```tsx
// BAD: Updates cause layout shift
{invoices.map(invoice => (
  <InvoiceCard key={invoice.id} invoice={invoice} />
))}
// New invoice appears, pushes everything down
```

**Solution:** Reserve space, use fixed heights, or smooth transitions:
```tsx
// Reserve space for expected updates
<div style={{ minHeight: '400px' }}>
  {invoices.map(invoice => (
    <InvoiceCard key={invoice.id} invoice={invoice} />
  ))}
</div>

// Or use smooth transitions
<TransitionGroup>
  {invoices.map(invoice => (
    <CSSTransition key={invoice.id} timeout={300}>
      <InvoiceCard invoice={invoice} />
    </CSSTransition>
  ))}
</TransitionGroup>
```

## Too Many Subscriptions

**Problem:** Subscribing to everything overwhelms both client and server with unnecessary messages.

**Example:**
```typescript
// BAD: Subscribe to everything
stompClient.subscribe('/topic/invoices', handleUpdate)
stompClient.subscribe('/topic/users', handleUpdate)
stompClient.subscribe('/topic/products', handleUpdate)
stompClient.subscribe('/topic/orders', handleUpdate)
// ... 50 more subscriptions
// User only viewing invoices page!
```

**Solution:** Subscribe only to what's needed, unsubscribe when leaving:
```typescript
// Subscribe only when component mounts
useEffect(() => {
  const subscription = stompClient.subscribe('/topic/invoices', handleUpdate)
  
  return () => {
    subscription.unsubscribe() // Clean up on unmount
  }
}, [])

// Or use route-based subscriptions
const route = useRoute()
useEffect(() => {
  if (route.path === '/invoices') {
    const sub = stompClient.subscribe('/topic/invoices', handleUpdate)
    return () => sub.unsubscribe()
  }
}, [route.path])
```

## Memory Leaks from Event Listeners

**Problem:** WebSocket event listeners not cleaned up on component unmount cause memory leaks.

**Example:**
```typescript
// BAD: Listener never removed
useEffect(() => {
  ws.onmessage = (event) => {
    handleMessage(event)
  }
  // No cleanup - listener persists after unmount!
}, [])
```

**Solution:** Always clean up listeners:
```typescript
// GOOD: Clean up on unmount
useEffect(() => {
  const handleMessage = (event: MessageEvent) => {
    processMessage(event.data)
  }
  
  ws.addEventListener('message', handleMessage)
  
  return () => {
    ws.removeEventListener('message', handleMessage)
  }
}, [ws])
```

## Multiple Tabs Opening Separate Connections

**Problem:** Each tab opens its own WebSocket connection, multiplying server load unnecessarily.

**Example:**
```typescript
// BAD: Each tab creates new connection
// Tab 1: ws://server/ws (connection 1)
// Tab 2: ws://server/ws (connection 2)
// Tab 3: ws://server/ws (connection 3)
// 3x server load!
```

**Solution:** Use SharedWorker or BroadcastChannel to share connection:
```typescript
// SharedWorker approach
// shared-websocket-worker.js
let ws = null
const ports = []

self.onconnect = (e) => {
  const port = e.ports[0]
  ports.push(port)
  
  if (!ws) {
    ws = new WebSocket('ws://localhost:8080/ws')
    ws.onmessage = (event) => {
      ports.forEach(p => p.postMessage(event.data))
    }
  }
  
  port.onmessage = (e) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(e.data)
    }
  }
}

// In each tab
const worker = new SharedWorker('shared-websocket-worker.js')
worker.port.onmessage = (e) => {
  handleWebSocketMessage(e.data)
}
```

## Conflict Resolution Showing Confusing UI

**Problem:** "Your changes were overwritten" with no details about what changed or why.

**Example:**
```tsx
// BAD: Vague conflict message
{conflict && (
  <Alert severity="error">
    Your changes were overwritten
  </Alert>
)}
// User has no idea what happened!
```

**Solution:** Show detailed diff and resolution options:
```tsx
// GOOD: Detailed conflict resolution
{conflict && (
  <ConflictResolutionDialog
    localChanges={conflict.local}
    remoteChanges={conflict.remote}
    onResolve={(resolution) => {
      // Apply user's choice
      resolveConflict(conflict.id, resolution)
    }}
  >
    <DiffViewer
      original={conflict.local}
      modified={conflict.remote}
    />
    <Button onClick={() => resolveConflict('keep-local')}>
      Keep My Changes
    </Button>
    <Button onClick={() => resolveConflict('keep-remote')}>
      Use Their Changes
    </Button>
    <Button onClick={() => resolveConflict('merge')}>
      Merge Both
    </Button>
  </ConflictResolutionDialog>
)}
```

## Real-Time Updates Not Respecting Scroll Position

**Problem:** Auto-scrolling to new content disrupts users who are reading older content.

**Example:**
```typescript
// BAD: Always scroll to bottom
watch(newMessages, () => {
  messagesContainer.scrollTop = messagesContainer.scrollHeight
  // User reading old message? Too bad!
})
```

**Solution:** Only scroll if user is near bottom:
```typescript
// GOOD: Respect user's scroll position
function shouldAutoScroll() {
  const container = messagesContainerRef.current
  const threshold = 100 // pixels from bottom
  const isNearBottom = 
    container.scrollHeight - container.scrollTop - container.clientHeight < threshold
  return isNearBottom
}

watch(newMessages, () => {
  if (shouldAutoScroll()) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight
  }
  // Otherwise, just show "new messages" indicator
})
```

## WebSocket Through Proxies Dropping Connections

**Problem:** Load balancers and proxies drop WebSocket connections due to timeout or lack of sticky sessions.

**Example:**
```nginx
# BAD: No sticky sessions
upstream backend {
    server backend1:8080;
    server backend2:8080;
}
# WebSocket connection to backend1, but next request goes to backend2 - connection lost!
```

**Solution:** Configure sticky sessions or use Redis pub/sub:
```nginx
# GOOD: Sticky sessions
upstream backend {
    ip_hash; # Sticky sessions
    server backend1:8080;
    server backend2:8080;
}

# Or use Redis pub/sub (better for scaling)
# All servers subscribe to Redis, broadcast to local connections
```

```kotlin
// Redis pub/sub approach (no sticky sessions needed)
@Configuration
class RedisWebSocketConfig {
    @Bean
    fun redisMessageListener(
        messagingTemplate: SimpMessagingTemplate
    ): MessageListener {
        return MessageListener { message, _ ->
            val event = objectMapper.readValue(message.body, InvoiceEvent::class.java)
            // Broadcast to all WebSocket connections on THIS server
            messagingTemplate.convertAndSend("/topic/invoices", event)
        }
    }
}
```

## Testing Difficulty

**Problem:** Real-time behavior is inherently non-deterministic, making tests flaky and unreliable.

**Example:**
```typescript
// BAD: Fixed delays in tests
test('receives update', async () => {
  triggerUpdate()
  await new Promise(resolve => setTimeout(resolve, 1000)) // Hope it arrives in 1s
  expect(receivedUpdate).toBeTruthy() // Flaky!
})
```

**Solution:** Wait for specific states, use test doubles, and be generous with timeouts:
```typescript
// GOOD: Wait for state changes
test('receives update', async ({ page }) => {
  await page.click('[data-testid="trigger-update"]')
  
  // Wait for specific state, not fixed time
  await expect(page.locator('[data-testid="invoice-amount"]'))
    .toHaveText('100.00', { timeout: 10000 })
})

// Use test doubles for unit tests
const mockWebSocket = {
  send: jest.fn(),
  onmessage: null,
  simulateMessage: (data) => mockWebSocket.onmessage({ data })
}

// Integration tests for real behavior
test('WebSocket integration', async () => {
  const client = connectWebSocketClient()
  await waitFor(() => client.isConnected, { timeout: 5000 })
  
  // Test actual behavior
})
```

**Additional Testing Strategies:**
- Use Playwright's `waitForFunction` instead of fixed delays
- Mock WebSocket in unit tests for deterministic behavior
- Use integration tests sparingly for real WebSocket behavior
- Accept that some real-time tests may be flaky - investigate root causes
- Use generous timeouts (10-30 seconds) for real-time operations
- Test connection resilience separately from message delivery
