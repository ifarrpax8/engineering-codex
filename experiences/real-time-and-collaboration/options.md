# Options: Real-Time & Collaboration

## Contents

- [Real-Time Transport](#real-time-transport)
- [Presence Implementation](#presence-implementation)
- [Conflict Resolution](#conflict-resolution)
- [WebSocket Libraries](#websocket-libraries)
- [Recommendations](#recommendations)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Real-Time Transport

### WebSocket (STOMP)

**Description:** Full-duplex communication protocol over TCP, enabling bidirectional real-time messaging. STOMP provides message-oriented semantics on top of WebSocket.

**Strengths:**
- Low latency bidirectional communication
- Efficient for frequent updates
- Standard protocol with good browser support
- Spring WebSocket provides excellent STOMP support
- Can send and receive messages simultaneously

**Weaknesses:**
- More complex than SSE or polling
- Requires connection management (reconnection, heartbeat)
- Higher server resource usage (persistent connections)
- Can be blocked by restrictive firewalls/proxies
- Requires sticky sessions or Redis pub/sub for horizontal scaling

**Best For:**
- Chat and messaging applications
- Collaborative editing
- Interactive real-time dashboards
- Bidirectional real-time features
- When you need to send data from client to server in real-time

**Avoid When:**
- Simple one-way data streams (use SSE instead)
- Low-frequency updates (polling may suffice)
- Mobile applications with battery constraints (consider SSE)
- Very high connection counts without proper scaling strategy

**Example:**
```kotlin
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureMessageBroker(config: MessageBrokerRegistry) {
        config.enableSimpleBroker("/topic", "/queue")
        config.setApplicationDestinationPrefixes("/app")
    }
}
```

### SSE (Server-Sent Events)

**Description:** One-way server-to-client streaming over HTTP. Browser automatically handles reconnection.

**Strengths:**
- Simpler than WebSocket (just HTTP)
- Automatic browser reconnection
- Works through most firewalls/proxies
- Lower server resource usage than WebSocket
- Built-in event ID support for resume capability

**Weaknesses:**
- One-way only (server → client)
- Less efficient than WebSocket for bidirectional communication
- Limited browser support for advanced features
- No built-in message framing (need to implement protocol)

**Best For:**
- Live feeds and activity streams
- Progress updates and notifications
- One-way real-time data streams
- When you only need server-to-client updates
- Mobile applications (better battery life than WebSocket)

**Avoid When:**
- You need bidirectional communication
- Chat or collaborative editing
- When client needs to send frequent real-time messages

**Example:**
```kotlin
@GetMapping("/events/invoices", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
fun streamInvoiceEvents(): SseEmitter {
    val emitter = SseEmitter(Long.MAX_VALUE)
    invoiceEventPublisher.subscribe { event ->
        emitter.send(SseEmitter.event().data(event))
    }
    return emitter
}
```

### Short Polling

**Description:** Client periodically requests updates from server (e.g., every 1-5 seconds).

**Strengths:**
- Simplest to implement
- Works everywhere (no special protocols)
- Easy to debug and test
- No persistent connections
- Stateless (scales horizontally easily)

**Weaknesses:**
- Higher server load (many requests)
- Potential for stale data between polls
- Higher latency than WebSocket/SSE
- Wastes bandwidth when no updates
- Not truly "real-time"

**Best For:**
- Low-frequency updates (< once per minute)
- Simple use cases where real-time isn't critical
- Fallback when WebSocket/SSE fails
- Prototyping and MVP development
- When simplicity is more important than latency

**Avoid When:**
- High-frequency updates (> once per 5 seconds)
- Collaborative editing or chat
- When data freshness is critical
- High-traffic applications (server load concerns)

**Example:**
```typescript
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

### Long Polling

**Description:** Client makes request, server holds it open until data available (up to timeout), then client immediately reconnects.

**Strengths:**
- Lower latency than short polling
- Reduces server load compared to short polling
- Works through firewalls (just HTTP)
- Simpler than WebSocket

**Weaknesses:**
- More complex than short polling
- Still higher latency than WebSocket/SSE
- Server must hold connections open
- Connection management complexity
- Not as efficient as true push

**Best For:**
- When WebSocket/SSE not available
- Moderate update frequency
- Need better latency than short polling
- Fallback strategy

**Avoid When:**
- WebSocket or SSE available
- Very high update frequency
- Simple use case (short polling simpler)

### WebTransport (Emerging)

**Description:** Modern protocol combining benefits of WebSocket and HTTP/3, with better multiplexing and connection migration.

**Strengths:**
- Better performance than WebSocket
- Built on HTTP/3 (QUIC)
- Connection migration support
- Multiple streams per connection

**Weaknesses:**
- Very new (limited browser support)
- Less mature ecosystem
- Spring Boot doesn't have native support yet
- May require polyfills or fallbacks

**Best For:**
- Future-proofing applications
- When cutting-edge performance is needed
- Applications targeting modern browsers only

**Avoid When:**
- Need broad browser support
- Using Spring Boot (no native support yet)
- Production applications requiring stability

## Presence Implementation

### Redis-Backed (Custom)

**Description:** Custom presence system using Redis to store online status with TTL-based expiration.

**Strengths:**
- Full control over presence logic
- Integrates with existing Redis infrastructure
- Flexible timeout and cleanup strategies
- Can customize presence data (viewing, editing, etc.)
- No external dependencies

**Weaknesses:**
- Must implement heartbeat mechanism yourself
- Must handle stale presence cleanup
- More code to maintain
- Potential for bugs in custom logic

**Best For:**
- Applications with existing Redis infrastructure
- Need custom presence features (viewing vs editing)
- Want full control over presence behavior
- Spring Boot applications

**Avoid When:**
- Want off-the-shelf solution
- Don't have Redis infrastructure
- Simple presence needs (Firebase may be simpler)

**Example:**
```kotlin
@Service
class PresenceService(private val redisTemplate: StringRedisTemplate) {
    fun updatePresence(userId: String, resourceId: String) {
        val key = "presence:$resourceId:$userId"
        redisTemplate.opsForValue().set(key, "online", Duration.ofMinutes(2))
    }
}
```

### Firebase Presence

**Description:** Firebase Realtime Database provides built-in presence system with automatic cleanup.

**Strengths:**
- Off-the-shelf solution
- Automatic presence cleanup
- Handles network transitions
- Good documentation and support
- Works across platforms

**Weaknesses:**
- External dependency (Firebase)
- Additional cost
- Less control over behavior
- May be overkill if only using for presence
- Requires Firebase SDK integration

**Best For:**
- Applications already using Firebase
- Want quick presence implementation
- Multi-platform applications
- Don't want to maintain custom presence logic

**Avoid When:**
- Not using Firebase otherwise
- Need custom presence features
- Want to avoid external dependencies
- Cost is a concern

### Custom Heartbeat Service

**Description:** Dedicated microservice for tracking presence with sophisticated heartbeat and cleanup logic.

**Strengths:**
- Can be highly optimized
- Separates concerns (presence as a service)
- Can scale independently
- Reusable across applications

**Weaknesses:**
- Additional service to maintain
- Network calls add latency
- More complex architecture
- Overkill for simple use cases

**Best For:**
- Large-scale applications
- Multiple applications sharing presence
- Need sophisticated presence features
- Microservices architecture

**Avoid When:**
- Simple single-application use case
- Want to minimize services
- Latency is critical

## Conflict Resolution

### Last-Write-Wins

**Description:** Most recent update wins, earlier updates are discarded.

**Strengths:**
- Simplest to implement
- No merge logic needed
- Fast and predictable
- Works for most use cases

**Weaknesses:**
- Loses data (earlier writes discarded)
- Poor UX when conflicts occur
- Not suitable for collaborative editing
- Users may lose work

**Best For:**
- Non-critical data updates
- Single-user editing scenarios
- When conflicts are rare
- Simple use cases

**Avoid When:**
- Collaborative editing
- Data loss is unacceptable
- Conflicts are common
- Users expect to see all changes

**Example:**
```kotlin
fun updateInvoice(id: String, update: InvoiceUpdate): Invoice {
    val current = repository.findById(id)
    if (update.version != current.version) {
        throw ConflictException("Version mismatch - someone else updated this")
    }
    return repository.save(current.copy(amount = update.amount, version = current.version + 1))
}
```

### Operational Transforms (OT)

**Description:** Transform operations to resolve conflicts by applying operations in correct order.

**Strengths:**
- Handles complex conflicts
- Used successfully by Google Docs (early versions)
- Preserves user intent
- Good for text editing

**Weaknesses:**
- Very complex to implement correctly
- Requires operation history
- Difficult to test
- May have edge cases

**Best For:**
- Text editing applications
- When you need precise conflict resolution
- Have resources for complex implementation
- Similar to Google Docs use case

**Avoid When:**
- Simple data updates
- Don't have resources for complex implementation
- CRDTs may be simpler alternative

### CRDTs (Yjs, Automerge)

**Description:** Conflict-free replicated data types that automatically merge changes mathematically.

**Strengths:**
- Automatic conflict resolution
- Handles offline editing
- Mathematically proven to work
- Good libraries available (Yjs, Automerge)

**Weaknesses:**
- Learning curve
- May have performance overhead
- Less control over merge behavior
- Requires specific data structures

**Best For:**
- Collaborative editing (Google Docs style)
- Offline-first applications
- Complex document editing
- When automatic merging is acceptable

**Avoid When:**
- Simple data updates
- Need custom merge logic
- Performance is critical
- Don't need offline editing

**Example:**
```typescript
import * as Y from 'yjs'

const ydoc = new Y.Doc()
const ytext = ydoc.getText('content')

// Changes automatically sync and merge
ytext.insert(0, 'Hello')
// Another client's insert merges conflict-free
```

### Application-Level Merge

**Description:** Custom merge logic tailored to your domain and data structures.

**Strengths:**
- Full control over merge behavior
- Can optimize for your use case
- Understandable to team
- Can provide good UX

**Weaknesses:**
- Must implement yourself
- Potential for bugs
- May miss edge cases
- More code to maintain

**Best For:**
- Domain-specific merge requirements
- When you understand your data well
- Need custom merge UX
- Simple to moderate complexity

**Avoid When:**
- Very complex merge scenarios
- Want proven solution (use CRDTs)
- Don't have resources for implementation

**Example:**
```kotlin
fun mergeInvoices(local: Invoice, remote: Invoice): Invoice {
    return Invoice(
        id = local.id,
        amount = maxOf(local.amount, remote.amount), // Take higher
        status = remote.status, // Server wins
        notes = mergeNotes(local.notes, remote.notes) // Custom merge
    )
}
```

## WebSocket Libraries

### Native WebSocket API

**Description:** Browser's built-in WebSocket API, no dependencies.

**Strengths:**
- No dependencies
- Standard API
- Small bundle size
- Full control

**Weaknesses:**
- Must implement STOMP yourself
- No automatic reconnection
- More boilerplate code
- Must handle all connection management

**Best For:**
- Simple WebSocket use cases
- Want minimal dependencies
- Using STOMP library on top
- Custom protocols

**Avoid When:**
- Want automatic reconnection
- Need STOMP support (use SockJS)
- Want higher-level abstractions

### SockJS (Spring)

**Description:** WebSocket library with fallback support, works well with Spring WebSocket.

**Strengths:**
- Automatic fallback to polling
- Works with Spring WebSocket
- Handles browser compatibility
- Good for Spring Boot applications

**Weaknesses:**
- Spring-specific
- Additional dependency
- May be overkill for simple cases

**Best For:**
- Spring Boot applications
- Need fallback support
- Want Spring integration
- Production applications

**Avoid When:**
- Not using Spring
- Simple use case (native API sufficient)
- Want minimal dependencies

### Socket.IO

**Description:** Popular WebSocket library with rooms, namespaces, and automatic reconnection.

**Strengths:**
- Popular and well-documented
- Automatic reconnection
- Rooms and namespaces
- Good client libraries

**Weaknesses:**
- Requires Socket.IO server (not standard WebSocket)
- More complex than needed for simple cases
- Not compatible with Spring WebSocket STOMP
- Larger bundle size

**Best For:**
- Node.js backend
- Need rooms/namespaces
- Want popular library
- Not using Spring Boot

**Avoid When:**
- Using Spring Boot (use SockJS instead)
- Simple use case
- Want standard WebSocket protocol

### Centrifugo

**Description:** Real-time messaging server with WebSocket support, can work with any backend.

**Strengths:**
- Handles scaling concerns
- Works with any backend
- Good performance
- Handles presence, channels

**Weaknesses:**
- Additional service to run
- External dependency
- May be overkill
- Additional cost/complexity

**Best For:**
- Need scalable real-time infrastructure
- Multiple applications
- Don't want to handle scaling yourself
- High connection counts

**Avoid When:**
- Simple single-application use case
- Want to minimize services
- Small scale application

## Recommendations

### Default Recommendation

**Backend:** Spring WebSocket with STOMP
- Excellent Spring Boot integration
- Mature and well-documented
- Good performance
- Redis pub/sub for horizontal scaling

**Frontend:** Native WebSocket API with composable/hook
- Vue 3: `useWebSocket` from VueUse or custom composable
- React: `react-use-websocket` or custom hook
- Minimal dependencies
- Full control over connection management

**Presence:** Redis-backed custom implementation
- Integrates with existing infrastructure
- Full control over behavior
- Flexible timeout strategies

**Conflict Resolution:** Last-write-wins with optimistic locking
- Simple and sufficient for most cases
- Upgrade to application-level merge if needed
- Consider CRDTs only for collaborative editing

**Transport:** WebSocket (STOMP) with SSE fallback
- WebSocket for bidirectional features
- SSE for one-way streams
- Polling as final fallback

### When to Choose Alternatives

**Choose SSE when:**
- Only need one-way server push
- Mobile application (battery concerns)
- Simpler implementation desired

**Choose CRDTs when:**
- Building collaborative editing (Google Docs style)
- Need offline editing support
- Conflicts are common and complex

**Choose Socket.IO when:**
- Using Node.js backend (not Spring Boot)
- Need rooms/namespaces features
- Want popular, well-documented library

**Choose Firebase Presence when:**
- Already using Firebase
- Want quick implementation
- Multi-platform application

## Synergies

- **WebSocket + Redis Pub/Sub:** Enables horizontal scaling of WebSocket connections
- **Optimistic Updates + Real-Time:** Provides instant feedback with server confirmation
- **Presence + WebSocket:** Presence updates delivered via same WebSocket connection
- **CRDTs + Offline Support:** CRDTs naturally support offline editing and sync
- **SSE + Polling Fallback:** Graceful degradation when SSE unavailable

## Evolution Triggers

**Migrate from Polling to SSE/WebSocket when:**
- Update frequency increases (> once per 10 seconds)
- Users complain about stale data
- Server load from polling becomes concern
- Real-time becomes competitive differentiator

**Migrate from SSE to WebSocket when:**
- Need bidirectional communication
- Client needs to send frequent real-time messages
- Building chat or collaborative editing

**Migrate from Last-Write-Wins to CRDTs when:**
- Building collaborative editing features
- Conflicts become common problem
- Users losing work due to conflicts
- Need offline editing support

**Migrate from Single Server to Redis Pub/Sub when:**
- Connection count exceeds single server capacity
- Need horizontal scaling
- Sticky sessions become problematic
- Multiple server instances required
