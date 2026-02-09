# Architecture: Real-Time & Collaboration

## Contents

- [WebSocket Architecture](#websocket-architecture)
- [SSE Architecture](#sse-architecture)
- [Polling as Fallback](#polling-as-fallback)
- [Presence System](#presence-system)
- [Optimistic Updates with Real-Time Reconciliation](#optimistic-updates-with-real-time-reconciliation)
- [Conflict Resolution Patterns](#conflict-resolution-patterns)
- [Real-Time Data Synchronization](#real-time-data-synchronization)
- [Connection Management](#connection-management)
- [Scalability](#scalability)
- [Frontend State Management](#frontend-state-management)

## WebSocket Architecture

Spring WebSocket with STOMP (Simple Text Oriented Messaging Protocol) provides a robust foundation for bidirectional real-time communication.

### Connection Lifecycle

**Connect**: Client establishes WebSocket connection, authenticates during handshake
```kotlin
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureMessageBroker(config: MessageBrokerRegistry) {
        config.enableSimpleBroker("/topic", "/queue")
        config.setApplicationDestinationPrefixes("/app")
    }
    
    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws").setAllowedOrigins("*")
    }
}
```

**Subscribe**: Client subscribes to topics for specific data streams
```typescript
// Vue 3 with useWebSocket
import { useWebSocket } from '@vueuse/core'

const { status, data, send, open, close } = useWebSocket('ws://localhost:8080/ws', {
  onConnected: (ws) => {
    ws.send(JSON.stringify({
      command: 'SUBSCRIBE',
      destination: '/topic/invoices',
      id: 'sub-1'
    }))
  }
})
```

**Message**: Server pushes messages to subscribed clients
```kotlin
@Service
class InvoiceService(
    private val messagingTemplate: SimpMessagingTemplate
) {
    fun notifyInvoiceUpdate(invoiceId: String, invoice: Invoice) {
        messagingTemplate.convertAndSend(
            "/topic/invoices/$invoiceId",
            InvoiceUpdateEvent(invoiceId, invoice)
        )
    }
}
```

**Disconnect**: Client or server closes connection, cleanup occurs

### Topic-Based Subscriptions

STOMP uses topic-based routing. Clients subscribe to topics like `/topic/invoices` or `/topic/invoices/12345`:
- `/topic/*` - Broadcast to all subscribers (pub/sub)
- `/queue/*` - Point-to-point messaging
- `/user/*` - User-specific messages (Spring Security integration)

### Authentication Over WebSocket

**Handshake Authentication**: Validate credentials during WebSocket handshake
```kotlin
@Component
class AuthChannelInterceptor : ChannelInterceptor {
    override fun preSend(message: Message<*>, channel: MessageChannel): Message<*>? {
        val accessor = StompHeaderAccessor.wrap(message)
        val token = accessor.getFirstNativeHeader("Authorization")
        
        if (token == null || !validateToken(token)) {
            throw AuthenticationException("Invalid token")
        }
        
        return message
    }
}
```

**Token-Based**: Pass JWT token in connection headers, validate on each message

## SSE Architecture

Server-Sent Events provide simpler one-way server push, ideal for feeds and notifications.

```kotlin
@RestController
class SseController {
    @GetMapping("/events/invoices", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
    fun streamInvoiceEvents(): SseEmitter {
        val emitter = SseEmitter(Long.MAX_VALUE)
        
        // Send initial connection event
        emitter.send(SseEmitter.event()
            .name("connected")
            .data("Connected to invoice stream"))
        
        // Register for invoice updates
        invoiceEventPublisher.subscribe { event ->
            emitter.send(SseEmitter.event()
                .name("invoice-updated")
                .data(event))
        }
        
        emitter.onCompletion { /* cleanup */ }
        emitter.onTimeout { /* handle timeout */ }
        
        return emitter
    }
}
```

**Automatic Reconnection**: Browsers automatically reconnect SSE connections
**Event IDs**: Use `id` field for resume capability—client can request events after a specific ID

## Polling as Fallback

When WebSocket/SSE fails, fall back to polling strategies.

**Short Polling**: Frequent requests (every 1-5 seconds)
```typescript
// React with useInterval
const usePolling = (url: string, interval: number) => {
  const [data, setData] = useState(null)
  
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(url)
      setData(await response.json())
    }
    
    fetchData()
    const id = setInterval(fetchData, interval)
    return () => clearInterval(id)
  }, [url, interval])
  
  return data
}
```

**Long Polling**: Server holds request open until data available (up to timeout), then client immediately reconnects
**Exponential Backoff**: Increase poll interval when no updates: 1s → 2s → 4s → 8s → max 30s

**When Polling is Right**: Low-frequency updates, simple use cases, when WebSocket overhead isn't justified

## Presence System

Track who's online, viewing pages, or actively editing.

### Heartbeat Mechanism

Clients send periodic heartbeats to indicate they're still active:
```typescript
// Vue 3 presence composable
export function usePresence(userId: string) {
  const { send } = useWebSocket('ws://localhost:8080/ws')
  
  useEffect(() => {
    // Send heartbeat every 30 seconds
    const interval = setInterval(() => {
      send(JSON.stringify({
        destination: '/app/presence/heartbeat',
        body: JSON.stringify({ userId, timestamp: Date.now() })
      }))
    }, 30000)
    
    return () => clearInterval(interval)
  }, [userId])
}
```

### Presence Storage (Redis)

Store presence state in Redis with TTL:
```kotlin
@Service
class PresenceService(
    private val redisTemplate: StringRedisTemplate
) {
    fun updatePresence(userId: String, resourceId: String, resourceType: String) {
        val key = "presence:$resourceType:$resourceId:$userId"
        redisTemplate.opsForValue().set(key, "online", Duration.ofMinutes(2))
    }
    
    fun getPresence(resourceId: String, resourceType: String): List<String> {
        val pattern = "presence:$resourceType:$resourceId:*"
        return redisTemplate.keys(pattern)?.map { it.split(":").last() } ?: emptyList()
    }
}
```

### Broadcasting Presence Changes

When presence changes, notify all viewers:
```kotlin
@MessageMapping("/presence/update")
fun updatePresence(
    @Payload update: PresenceUpdate,
    principal: Principal
) {
    presenceService.updatePresence(principal.name, update.resourceId, update.resourceType)
    
    val currentUsers = presenceService.getPresence(update.resourceId, update.resourceType)
    messagingTemplate.convertAndSend(
        "/topic/presence/${update.resourceType}/${update.resourceId}",
        PresenceEvent(currentUsers)
    )
}
```

### Handling Stale Presence

Users may close laptops without proper disconnect. Implement timeout cleanup:
```kotlin
@Scheduled(fixedRate = 60000) // Every minute
fun cleanupStalePresence() {
    val allPresenceKeys = redisTemplate.keys("presence:*")
    allPresenceKeys?.forEach { key ->
        val ttl = redisTemplate.getExpire(key)
        if (ttl == -1) { // No expiration set
            redisTemplate.expire(key, Duration.ofMinutes(2))
        }
    }
}
```

## Optimistic Updates with Real-Time Reconciliation

Update UI immediately, then reconcile with server confirmation.

**1. Apply Change Immediately**
```typescript
// React with Zustand
const useInvoiceStore = create((set) => ({
  invoices: [],
  updateInvoice: async (id, updates) => {
    // Optimistic update
    set((state) => ({
      invoices: state.invoices.map(inv => 
        inv.id === id ? { ...inv, ...updates, _pending: true } : inv
      )
    }))
    
    // Send to server
    await api.updateInvoice(id, updates)
  }
}))
```

**2. Receive Server Confirmation via WebSocket**
```kotlin
@MessageMapping("/invoices/{id}/update")
fun handleInvoiceUpdate(@DestinationVariable id: String, update: InvoiceUpdate) {
    val updated = invoiceService.update(id, update)
    
    // Broadcast confirmation
    messagingTemplate.convertAndSend(
        "/topic/invoices/$id",
        InvoiceUpdateEvent(id, updated, confirmed = true)
    )
}
```

**3. Handle Conflicts**
```typescript
// Vue 3 conflict handling
watch(() => wsData.value, (event) => {
  if (event.type === 'invoice-updated') {
    const localPending = invoices.value.find(i => i.id === event.id && i._pending)
    
    if (localPending && localPending.version !== event.version) {
      // Conflict detected - show resolution UI
      showConflictResolution(localPending, event.invoice)
    } else {
      // Update confirmed - remove pending flag
      updateInvoice(event.id, { ...event.invoice, _pending: false })
    }
  }
})
```

## Conflict Resolution Patterns

**Last-Write-Wins**: Simplest, but loses data
```kotlin
data class Invoice(
    val id: String,
    val amount: BigDecimal,
    val version: Long // Optimistic locking
)

fun updateInvoice(id: String, update: InvoiceUpdate): Invoice {
    val current = repository.findById(id)
    if (update.version != current.version) {
        throw ConflictException("Version mismatch")
    }
    return repository.save(current.copy(
        amount = update.amount,
        version = current.version + 1
    ))
}
```

**Operational Transforms (OT)**: Transform operations to resolve conflicts
- Complex but powerful
- Used by Google Docs (early versions)
- Requires operation history and transformation rules

**CRDTs (Conflict-Free Replicated Data Types)**: Mathematical structures that merge automatically
```typescript
// Using Yjs for collaborative editing
import * as Y from 'yjs'

const ydoc = new Y.Doc()
const ytext = ydoc.getText('content')

// Changes automatically sync and merge
ytext.insert(0, 'Hello')
// Another client's insert merges conflict-free
```

**Application-Level Merge**: Custom merge logic for your domain
```kotlin
fun mergeInvoices(local: Invoice, remote: Invoice): Invoice {
    return Invoice(
        id = local.id,
        // Merge fields intelligently
        amount = maxOf(local.amount, remote.amount), // Take higher amount
        status = remote.status, // Server wins on status
        notes = mergeNotes(local.notes, remote.notes) // Combine notes
    )
}
```

## Real-Time Data Synchronization

### Subscribing to Entity Changes

Clients subscribe to specific entities or collections:
```typescript
// Subscribe to single invoice
stompClient.subscribe(`/topic/invoices/${invoiceId}`, (message) => {
  const update = JSON.parse(message.body)
  updateInvoiceInStore(update)
})

// Subscribe to collection
stompClient.subscribe('/topic/invoices', (message) => {
  const event = JSON.parse(message.body)
  if (event.type === 'created') {
    addInvoiceToStore(event.invoice)
  } else if (event.type === 'updated') {
    updateInvoiceInStore(event.invoice)
  } else if (event.type === 'deleted') {
    removeInvoiceFromStore(event.id)
  }
})
```

### Partial Updates (Patch)

Send only changed fields to reduce bandwidth:
```kotlin
data class InvoicePatch(
    val id: String,
    val updates: Map<String, Any> // Only changed fields
)

fun applyPatch(invoiceId: String, patch: InvoicePatch): Invoice {
    val invoice = repository.findById(invoiceId)
    val updated = patch.updates.fold(invoice) { acc, (field, value) ->
        acc.copyField(field, value)
    }
    return repository.save(updated)
}
```

### Full Refresh Triggers

Sometimes full refresh is needed (major schema changes, corruption):
```kotlin
messagingTemplate.convertAndSend(
    "/topic/invoices",
    RefreshEvent(type = "full-refresh", reason = "schema-migration")
)
```

## Connection Management

### Reconnection Strategy

Exponential backoff prevents server overload:
```typescript
// Vue 3 reconnection logic
let reconnectAttempts = 0
const maxReconnectAttempts = 10

function reconnect() {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.error('Max reconnection attempts reached')
    return
  }
  
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
  reconnectAttempts++
  
  setTimeout(() => {
    connectWebSocket()
  }, delay)
}

function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8080/ws')
  
  ws.onopen = () => {
    reconnectAttempts = 0 // Reset on successful connection
  }
  
  ws.onerror = reconnect
  ws.onclose = reconnect
}
```

### Connection State UI

Show users connection status:
```tsx
// React connection indicator
function ConnectionStatus() {
  const { status } = useWebSocket()
  
  return (
    <div className="connection-status">
      {status === 'OPEN' && <Badge color="success">Live</Badge>}
      {status === 'CONNECTING' && <Badge color="warning">Connecting...</Badge>}
      {status === 'CLOSED' && <Badge color="error">Disconnected</Badge>}
    </div>
  )
}
```

### Fallback to Polling

When WebSocket fails, gracefully degrade:
```typescript
const useRealTimeData = (url: string) => {
  const { data: wsData, status } = useWebSocket(url)
  const pollData = usePolling(url, 5000) // Fallback polling
  
  return status === 'OPEN' ? wsData : pollData
}
```

### Handling Multiple Tabs

**Shared WebSocket via SharedWorker** (complex but efficient):
```typescript
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
```

**BroadcastChannel** (simpler, but each tab has its own connection):
```typescript
const channel = new BroadcastChannel('websocket-channel')

channel.onmessage = (event) => {
  // One tab receives WebSocket message, broadcasts to others
  if (event.data.type === 'websocket-message') {
    handleMessage(event.data.payload)
  }
}
```

## Scalability

### WebSocket Connection Limits

Each WebSocket connection consumes server resources (memory, file descriptors). Typical limits:
- Single server: 10,000-50,000 connections (depends on hardware)
- Load balancer: May have lower limits

### Sticky Sessions vs Redis Pub/Sub

**Sticky Sessions**: Route same client to same server
- Simpler, but limits horizontal scaling
- Server restart drops connections

**Redis Pub/Sub**: All servers subscribe to Redis, broadcast to local connections
```kotlin
@Configuration
class RedisWebSocketConfig {
    @Bean
    fun redisMessageListenerContainer(
        connectionFactory: RedisConnectionFactory
    ): RedisMessageListenerContainer {
        val container = RedisMessageListenerContainer()
        container.connectionFactory = connectionFactory
        return container
    }
    
    @Bean
    fun redisMessageListener(
        messagingTemplate: SimpMessagingTemplate
    ): MessageListener {
        return MessageListener { message, _ ->
            val event = objectMapper.readValue(message.body, InvoiceEvent::class.java)
            messagingTemplate.convertAndSend("/topic/invoices", event)
        }
    }
}
```

### Horizontal Scaling with Message Broker

Use Kafka or RabbitMQ for message distribution:
```kotlin
@KafkaListener(topics = ["invoice-events"])
fun handleInvoiceEvent(event: InvoiceEvent) {
    // Broadcast to all WebSocket connections on this server
    messagingTemplate.convertAndSend("/topic/invoices", event)
}
```

## Frontend State Management

### Merging Real-Time Updates

**Vue 3 with Pinia**:
```typescript
export const useInvoiceStore = defineStore('invoices', () => {
  const invoices = ref<Invoice[]>([])
  
  const { data: wsData } = useWebSocket('ws://localhost:8080/ws')
  
  watch(wsData, (event) => {
    if (event?.type === 'invoice-updated') {
      const index = invoices.value.findIndex(i => i.id === event.id)
      if (index >= 0) {
        invoices.value[index] = { ...invoices.value[index], ...event.invoice }
      }
    }
  })
  
  return { invoices }
})
```

**React with Zustand**:
```typescript
const useInvoiceStore = create((set, get) => ({
  invoices: [],
  updateFromWebSocket: (event) => {
    set((state) => ({
      invoices: state.invoices.map(inv =>
        inv.id === event.id ? { ...inv, ...event.invoice } : inv
      )
    }))
  }
}))

// Subscribe to WebSocket
useEffect(() => {
  const subscription = stompClient.subscribe('/topic/invoices', (message) => {
    const event = JSON.parse(message.body)
    useInvoiceStore.getState().updateFromWebSocket(event)
  })
  
  return () => subscription.unsubscribe()
}, [])
```

### Avoiding Stale Reads

Use version numbers or timestamps to prevent applying stale updates:
```typescript
interface Invoice {
  id: string
  amount: number
  version: number // Increment on each update
  updatedAt: number // Timestamp
}

function mergeUpdate(local: Invoice, remote: Invoice): Invoice {
  if (remote.version <= local.version) {
    // Stale update, ignore
    return local
  }
  return remote
}
```

### Optimistic Concurrency

Track pending changes to avoid overwriting user edits:
```typescript
interface InvoiceWithPending extends Invoice {
  _pending?: boolean
  _pendingVersion?: number
}

function applyUpdate(invoice: InvoiceWithPending, update: Invoice): InvoiceWithPending {
  if (invoice._pending && invoice._pendingVersion === update.version) {
    // This is the confirmation of our pending change
    return { ...update, _pending: false }
  }
  return { ...update }
}
```
