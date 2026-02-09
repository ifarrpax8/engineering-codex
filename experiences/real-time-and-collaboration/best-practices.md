# Real-Time & Collaboration — Best Practices

## Contents

- [Not Everything Needs to Be Real-Time](#not-everything-needs-to-be-real-time)
- [Always Show Connection Status](#always-show-connection-status)
- [Graceful Degradation](#graceful-degradation)
- [Debounce/Throttle Real-Time UI Updates](#debouncethrottle-real-time-ui-updates)
- [Presence Should Have a Timeout](#presence-should-have-a-timeout)
- [Optimistic + Real-Time](#optimistic--real-time)
- [Show "What Changed" Not Just "Something Changed"](#show-what-changed-not-just-something-changed)
- [Connection Management](#connection-management)
- [Stack-Specific Implementation](#stack-specific-implementation)
- [Accessibility in Real-Time Features](#accessibility-in-real-time-features)
- [Mobile Considerations](#mobile-considerations)
- [Conflict Communication](#conflict-communication)

## Not Everything Needs to Be Real-Time

Real-time updates add complexity and resource usage. Only use real-time when it genuinely improves the user experience.

### When Real-Time Makes Sense

**Use Real-Time For**:
- Collaborative editing (Google Docs-style)
- Live chat and messaging
- Presence indicators (who's online)
- Live notifications (new comments, mentions)
- Shared dashboards with live data
- Multi-user forms (prevent conflicts)
- Live activity feeds
- Real-time collaboration features

**Example**: Collaborative document editing
```tsx
// Real-time cursor positions and edits
function CollaborativeEditor({ documentId }: { documentId: string }) {
  const { socket, updates } = useWebSocket(`/documents/${documentId}`);
  
  // Real-time is essential here - users need to see others' edits immediately
  useEffect(() => {
    socket.on('user-edit', (edit) => {
      applyRemoteEdit(edit);
    });
  }, [socket]);
}
```

### When Polling Is Sufficient

**Use Polling For**:
- Status updates (every 30-60 seconds is fine)
- Notification counts (poll every 30s)
- Data that changes infrequently
- Background job status
- Non-critical updates
- When real-time adds little value

**Example**: Notification badge
```tsx
// Polling is sufficient - notifications don't need to be instant
function useNotificationCount() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/api/notifications/count');
      const data = await response.json();
      setCount(data.count);
    }, 30000); // Poll every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  return count;
}
```

### Decision Framework

**Ask**:
1. Does the user need to see changes within 1-2 seconds?
2. Are multiple users editing the same thing simultaneously?
3. Would polling every 30s be acceptable?
4. Is the data critical for immediate action?

**If answers are Yes/Yes/No/Yes → Use Real-Time**
**Otherwise → Consider Polling**

## Always Show Connection Status

Users need to know if real-time features are working. Show connection status subtly but visibly.

### Visual Indicators

**Pattern**: Subtle indicator that doesn't distract but is always visible.

**Status States**:
- 🟢 **Connected**: Green dot, "Live" badge, or subtle indicator
- 🟡 **Reconnecting**: Yellow/yellow dot, "Reconnecting..." message
- 🔴 **Disconnected**: Red dot, "Offline" badge, show last sync time
- ⚪ **Connecting**: Gray/spinner, "Connecting..." message

**Implementation**:
```tsx
function ConnectionStatus({ status }: { status: 'connected' | 'reconnecting' | 'disconnected' }) {
  const statusConfig = {
    connected: { color: 'green', label: 'Live', icon: '🟢' },
    reconnecting: { color: 'yellow', label: 'Reconnecting...', icon: '🟡' },
    disconnected: { color: 'red', label: 'Offline', icon: '🔴' }
  };
  
  const config = statusConfig[status];
  
  return (
    <div className={`connection-status ${status}`} aria-live="polite">
      <span className="status-dot" style={{ color: config.color }}>{config.icon}</span>
      <span className="status-label">{config.label}</span>
    </div>
  );
}
```

**Vue 3 Implementation**:
```vue
<template>
  <div :class="['connection-status', status]" aria-live="polite">
    <span class="status-dot" :style="{ color: statusConfig[status].color }">
      {{ statusConfig[status].icon }}
    </span>
    <span class="status-label">{{ statusConfig[status].label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useWebSocket } from '@vueuse/core';

const { status } = useWebSocket('ws://localhost:3000');

const statusConfig = {
  OPEN: { color: 'green', label: 'Live', icon: '🟢' },
  CONNECTING: { color: 'yellow', label: 'Connecting...', icon: '🟡' },
  CLOSED: { color: 'red', label: 'Offline', icon: '🔴' }
};
</script>
```

### Placement

**Best Locations**:
- Top-right corner (common pattern)
- Header bar
- Near relevant content (e.g., in collaborative editor toolbar)
- Status bar (if application has one)

**Avoid**:
- Obtrusive modals for status changes
- Hiding status completely
- Only showing on error

## Graceful Degradation

If WebSocket fails, fall back to SSE, then polling. The app should still work, just less "live".

### Fallback Strategy

**Tier 1**: WebSocket (best, bidirectional, low latency)
**Tier 2**: Server-Sent Events (SSE) (good, server-to-client only, still real-time)
**Tier 3**: Polling (acceptable, works everywhere, higher latency)

**Implementation**:
```typescript
class RealTimeConnection {
  private ws: WebSocket | null = null;
  private eventSource: EventSource | null = null;
  private pollInterval: number | null = null;
  private mode: 'websocket' | 'sse' | 'polling' = 'websocket';
  
  async connect(url: string) {
    try {
      await this.connectWebSocket(url);
      this.mode = 'websocket';
    } catch (wsError) {
      console.warn('WebSocket failed, trying SSE', wsError);
      try {
        await this.connectSSE(url);
        this.mode = 'sse';
      } catch (sseError) {
        console.warn('SSE failed, falling back to polling', sseError);
        this.connectPolling(url);
        this.mode = 'polling';
      }
    }
  }
  
  private connectWebSocket(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);
      this.ws.onopen = () => resolve();
      this.ws.onerror = reject;
      this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    });
  }
  
  private connectSSE(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.eventSource = new EventSource(url.replace('ws://', 'http://').replace('wss://', 'https://'));
      this.eventSource.onopen = () => resolve();
      this.eventSource.onerror = reject;
      this.eventSource.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    });
  }
  
  private connectPolling(url: string) {
    this.pollInterval = window.setInterval(async () => {
      try {
        const response = await fetch(url.replace('ws://', 'http://').replace('wss://', 'https://'));
        const data = await response.json();
        this.handleMessage(data);
      } catch (error) {
        console.error('Polling error', error);
      }
    }, 5000); // Poll every 5 seconds
  }
  
  private handleMessage(data: any) {
    // Handle incoming message regardless of transport
    this.onMessage?.(data);
  }
  
  onMessage?: (data: any) => void;
  
  disconnect() {
    this.ws?.close();
    this.eventSource?.close();
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }
}
```

**Spring Boot Backend - Multiple Transport Support**:
```kotlin
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureMessageBroker(config: MessageBrokerRegistry) {
        config.enableSimpleBroker("/topic", "/queue")
        config.setApplicationDestinationPrefixes("/app")
    }
    
    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("*")
            .withSockJS() // Enables fallback transports
    }
}

@RestController
class SSEController {
    @GetMapping(value = ["/events"], produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
    fun streamEvents(): SseEmitter {
        val emitter = SseEmitter(Long.MAX_VALUE)
        
        // Send events
        eventService.subscribe { event ->
            emitter.send(SseEmitter.SseEventBuilder()
                .data(event)
                .build())
        }
        
        return emitter
    }
}

@RestController
class PollingController {
    @GetMapping("/updates")
    fun getUpdates(@RequestParam since: Long?): ResponseEntity<List<Update>> {
        val updates = updateService.getUpdatesSince(since ?: 0)
        return ResponseEntity.ok(updates)
    }
}
```

## Debounce/Throttle Real-Time UI Updates

Rapid-fire updates at 100/sec cause UI jank. Batch updates to ~60fps or meaningful intervals.

### When to Debounce vs Throttle

**Debounce**: Wait for pause in updates, then apply (good for search, typing indicators)
**Throttle**: Apply updates at fixed interval (good for position updates, progress)

**Implementation**:
```typescript
// Debounce: Wait for pause, then update
function useDebouncedUpdate<T>(value: T, delay: number = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, delay]);
  
  return debouncedValue;
}

// Throttle: Update at fixed interval
function useThrottledUpdate<T>(value: T, interval: number = 100) {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastUpdate = useRef(Date.now());
  
  useEffect(() => {
    const now = Date.now();
    if (now - lastUpdate.current >= interval) {
      setThrottledValue(value);
      lastUpdate.current = now;
    } else {
      const timer = setTimeout(() => {
        setThrottledValue(value);
        lastUpdate.current = Date.now();
      }, interval - (now - lastUpdate.current));
      
      return () => clearTimeout(timer);
    }
  }, [value, interval]);
  
  return throttledValue;
}
```

**Vue 3 Implementation**:
```vue
<script setup lang="ts">
import { ref, watch } from 'vue';
import { useDebounceFn, useThrottleFn } from '@vueuse/core';

const cursorPosition = ref({ x: 0, y: 0 });

// Throttle cursor updates to 60fps (~16ms)
const throttledCursor = useThrottleFn((pos) => {
  updateCursorDisplay(pos);
}, 16);

watch(cursorPosition, (newPos) => {
  throttledCursor(newPos);
});

// Debounce typing indicator
const isTyping = ref(false);
const debouncedTypingStop = useDebounceFn(() => {
  isTyping.value = false;
  broadcastTypingStop();
}, 1000);

function onUserTyping() {
  isTyping.value = true;
  broadcastTypingStart();
  debouncedTypingStop();
}
</script>
```

### Batching Multiple Updates

**Pattern**: Collect updates and apply in batch:

```typescript
class UpdateBatcher {
  private updates: any[] = [];
  private batchTimer: number | null = null;
  private readonly batchInterval = 100; // 10 batches per second max
  
  addUpdate(update: any) {
    this.updates.push(update);
    
    if (!this.batchTimer) {
      this.batchTimer = window.setTimeout(() => {
        this.flush();
      }, this.batchInterval);
    }
  }
  
  private flush() {
    if (this.updates.length > 0) {
      // Apply all updates at once
      this.onBatch?.(this.updates);
      this.updates = [];
    }
    this.batchTimer = null;
  }
  
  onBatch?: (updates: any[]) => void;
}
```

## Presence Should Have a Timeout

Don't show "online" for a user who closed their laptop 30 minutes ago. Use heartbeat with 30-60s timeout.

### Heartbeat Pattern

**Pattern**: Client sends heartbeat every 30 seconds. Server marks user offline if no heartbeat for 60 seconds.

**Frontend Implementation**:
```tsx
function usePresence(userId: string) {
  const { socket } = useWebSocket();
  const [isOnline, setIsOnline] = useState(false);
  
  useEffect(() => {
    if (!socket) return;
    
    // Send heartbeat every 30 seconds
    const heartbeatInterval = setInterval(() => {
      socket.emit('heartbeat', { userId, timestamp: Date.now() });
    }, 30000);
    
    // Listen for presence updates
    socket.on('presence-update', (data: { userId: string; online: boolean }) => {
      if (data.userId === userId) {
        setIsOnline(data.online);
      }
    });
    
    return () => {
      clearInterval(heartbeatInterval);
      socket.off('presence-update');
    };
  }, [socket, userId]);
  
  return isOnline;
}
```

**Spring Boot Backend**:
```kotlin
@Service
class PresenceService(
    private val redisTemplate: RedisTemplate<String, String>
) {
    private val HEARTBEAT_TIMEOUT_SECONDS = 60L
    private val HEARTBEAT_INTERVAL_SECONDS = 30L
    
    fun recordHeartbeat(userId: String) {
        val key = "presence:$userId"
        redisTemplate.opsForValue().set(key, "online", HEARTBEAT_TIMEOUT_SECONDS, TimeUnit.SECONDS)
    }
    
    fun isUserOnline(userId: String): Boolean {
        val key = "presence:$userId"
        return redisTemplate.hasKey(key) ?: false
    }
    
    fun getOnlineUsers(): List<String> {
        val keys = redisTemplate.keys("presence:*")
        return keys?.map { it.removePrefix("presence:") } ?: emptyList()
    }
    
    @Scheduled(fixedRate = HEARTBEAT_INTERVAL_SECONDS * 1000)
    fun cleanupStalePresence() {
        // Redis TTL handles this automatically, but we can also check explicitly
        val keys = redisTemplate.keys("presence:*")
        keys?.forEach { key ->
            val ttl = redisTemplate.getExpire(key)
            if (ttl == null || ttl <= 0) {
                val userId = key.removePrefix("presence:")
                notifyPresenceChange(userId, online = false)
            }
        }
    }
}

@MessageMapping("/heartbeat")
fun handleHeartbeat(message: HeartbeatMessage, principal: Principal) {
    presenceService.recordHeartbeat(principal.name)
    
    // Broadcast presence update
    messagingTemplate.convertAndSend("/topic/presence", PresenceUpdate(
        userId = principal.name,
        online = true
    ))
}
```

### Last Seen vs Online

**Pattern**: Show "online" only if heartbeat received within last 60s. Otherwise show "last seen X minutes ago".

```tsx
function UserPresence({ userId }: { userId: string }) {
  const { online, lastSeen } = usePresence(userId);
  
  if (online) {
    return <span className="online">🟢 Online</span>;
  }
  
  if (lastSeen) {
    const minutesAgo = Math.floor((Date.now() - lastSeen) / 60000);
    return <span className="offline">Last seen {minutesAgo} minutes ago</span>;
  }
  
  return <span className="offline">Offline</span>;
}
```

## Optimistic + Real-Time

Apply user's own changes immediately (optimistic), receive confirmation and others' changes via real-time channel.

### Optimistic Updates Pattern

**Pattern**:
1. User makes change → Apply immediately (optimistic)
2. Send change to server
3. Receive confirmation → Keep or adjust
4. Receive others' changes → Apply on top

**Implementation**:
```tsx
function useOptimisticCollaboration<T>(initialValue: T) {
  const [localValue, setLocalValue] = useState(initialValue);
  const [pendingChanges, setPendingChanges] = useState<Map<string, any>>(new Map());
  const { socket } = useWebSocket();
  
  // Apply local change optimistically
  const applyLocalChange = (change: Change) => {
    const changeId = UUID.randomUUID();
    const optimisticValue = applyChange(localValue, change);
    
    setLocalValue(optimisticValue);
    setPendingChanges(prev => new Map(prev).set(changeId, change));
    
    // Send to server
    socket.emit('change', { id: changeId, change });
  };
  
  // Handle server confirmation
  useEffect(() => {
    socket.on('change-confirmed', (data: { id: string }) => {
      setPendingChanges(prev => {
        const next = new Map(prev);
        next.delete(data.id);
        return next;
      });
    });
    
    // Handle remote changes
    socket.on('remote-change', (data: { change: Change }) => {
      setLocalValue(prev => applyChange(prev, data.change));
    });
    
    return () => {
      socket.off('change-confirmed');
      socket.off('remote-change');
    };
  }, [socket]);
  
  return { value: localValue, applyChange: applyLocalChange };
}
```

**Vue 3 Implementation**:
```vue
<script setup lang="ts">
import { ref, watch } from 'vue';
import { useWebSocket } from '@vueuse/core';

const localValue = ref(initialValue);
const pendingChanges = ref(new Map<string, any>());

const { send, status } = useWebSocket('ws://localhost:3000', {
  onMessage(ws, event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'change-confirmed') {
      pendingChanges.value.delete(data.changeId);
    } else if (data.type === 'remote-change') {
      localValue.value = applyChange(localValue.value, data.change);
    }
  }
});

function applyLocalChange(change: Change) {
  const changeId = crypto.randomUUID();
  
  // Optimistic update
  localValue.value = applyChange(localValue.value, change);
  pendingChanges.value.set(changeId, change);
  
  // Send to server
  send(JSON.stringify({ type: 'change', id: changeId, change }));
}
</script>
```

## Show "What Changed" Not Just "Something Changed"

Highlight updated cells, show diffs, animate new entries. Users need to see what specifically changed.

### Visual Change Indicators

**Patterns**:
- Highlight changed cells/fields briefly (yellow flash, then fade)
- Show diff indicators (green for added, red for removed)
- Animate new entries (slide in, fade in)
- Show "X changed Y" messages

**Implementation**:
```tsx
function useChangeTracking<T>(value: T) {
  const [previousValue, setPreviousValue] = useState(value);
  const [changedFields, setChangedFields] = useState<Set<string>>(new Set());
  
  useEffect(() => {
    const changes = findChangedFields(previousValue, value);
    if (changes.size > 0) {
      setChangedFields(changes);
      
      // Clear highlights after 2 seconds
      setTimeout(() => {
        setChangedFields(new Set());
      }, 2000);
      
      setPreviousValue(value);
    }
  }, [value]);
  
  return { changedFields, isFieldChanged: (field: string) => changedFields.has(field) };
}

function DataTable({ data }: { data: Row[] }) {
  const { isFieldChanged } = useChangeTracking(data);
  
  return (
    <table>
      {data.map(row => (
        <tr key={row.id}>
          {row.fields.map(field => (
            <td
              key={field.name}
              className={isFieldChanged(field.name) ? 'changed' : ''}
            >
              {field.value}
            </td>
          ))}
        </tr>
      ))}
    </table>
  );
}
```

**CSS for Change Highlighting**:
```css
.changed {
  background-color: #fff3cd;
  animation: highlight-fade 2s ease-out;
}

@keyframes highlight-fade {
  0% { background-color: #fff3cd; }
  100% { background-color: transparent; }
}

.new-entry {
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Diff Display

**Pattern**: Show what changed in a readable format:

```tsx
function ChangeNotification({ change }: { change: Change }) {
  return (
    <div className="change-notification">
      <span className="actor">{change.actor}</span>
      <span className="action">{change.action}</span>
      {change.field && (
        <span className="field">{change.field}</span>
      )}
      {change.oldValue && change.newValue && (
        <div className="diff">
          <span className="old-value">{change.oldValue}</span>
          <span>→</span>
          <span className="new-value">{change.newValue}</span>
        </div>
      )}
    </div>
  );
}
```

## Connection Management

Share one WebSocket across tabs, reconnect with exponential backoff, resume subscriptions on reconnect.

### Shared WebSocket Across Tabs

**Pattern**: Use SharedWorker or BroadcastChannel to share WebSocket connection.

**BroadcastChannel Implementation**:
```typescript
class SharedWebSocketManager {
  private ws: WebSocket | null = null;
  private channel: BroadcastChannel;
  private subscribers: Set<(data: any) => void> = new Set();
  
  constructor(url: string) {
    this.channel = new BroadcastChannel('websocket-channel');
    
    // Only create WebSocket in one tab
    if (this.isPrimaryTab()) {
      this.connect(url);
    } else {
      // Listen for messages from primary tab
      this.channel.onmessage = (event) => {
        this.subscribers.forEach(sub => sub(event.data));
      };
    }
  }
  
  private isPrimaryTab(): boolean {
    // Use sessionStorage to coordinate
    if (!sessionStorage.getItem('websocket-primary')) {
      sessionStorage.setItem('websocket-primary', 'true');
      return true;
    }
    return false;
  }
  
  private connect(url: string) {
    this.ws = new WebSocket(url);
    
    this.ws.onmessage = (event) => {
      // Broadcast to all tabs
      this.channel.postMessage(JSON.parse(event.data));
      this.subscribers.forEach(sub => sub(JSON.parse(event.data)));
    };
    
    this.ws.onclose = () => {
      // Reconnect with exponential backoff
      this.reconnect(url);
    };
  }
  
  subscribe(callback: (data: any) => void) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }
  
  private reconnect(url: string, attempt: number = 1) {
    const delay = Math.min(1000 * Math.pow(2, attempt), 30000);
    
    setTimeout(() => {
      this.connect(url);
    }, delay);
  }
}
```

### Exponential Backoff Reconnection

**Pattern**: Reconnect with increasing delays: 1s, 2s, 4s, 8s, 16s, max 30s.

**Implementation**:
```typescript
class ReconnectingWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimer: number | null = null;
  
  constructor(url: string) {
    this.url = url;
    this.connect();
  }
  
  private connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.onOpen?.();
      };
      
      this.ws.onmessage = (event) => {
        this.onMessage?.(JSON.parse(event.data));
      };
      
      this.ws.onclose = () => {
        this.onClose?.();
        this.scheduleReconnect();
      };
      
      this.ws.onerror = (error) => {
        this.onError?.(error);
      };
    } catch (error) {
      this.scheduleReconnect();
    }
  }
  
  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }
    
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    
    this.reconnectTimer = window.setTimeout(() => {
      this.connect();
    }, delay);
  }
  
  onOpen?: () => void;
  onMessage?: (data: any) => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  
  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
  
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
  }
}
```

### Resume Subscriptions on Reconnect

**Pattern**: Store active subscriptions, resubscribe after reconnection.

**Implementation**:
```typescript
class SubscriptionManager {
  private subscriptions: Set<string> = new Set();
  private ws: ReconnectingWebSocket;
  
  constructor(ws: ReconnectingWebSocket) {
    this.ws = ws;
    
    // Resume subscriptions on reconnect
    this.ws.onOpen = () => {
      this.resubscribeAll();
    };
  }
  
  subscribe(topic: string) {
    this.subscriptions.add(topic);
    
    if (this.ws.isConnected()) {
      this.ws.send({ type: 'subscribe', topic });
    }
  }
  
  unsubscribe(topic: string) {
    this.subscriptions.delete(topic);
    
    if (this.ws.isConnected()) {
      this.ws.send({ type: 'unsubscribe', topic });
    }
  }
  
  private resubscribeAll() {
    this.subscriptions.forEach(topic => {
      this.ws.send({ type: 'subscribe', topic });
    });
  }
}
```

## Stack-Specific Implementation

### Vue 3

**useWebSocket Composable from VueUse**:
```vue
<script setup lang="ts">
import { useWebSocket } from '@vueuse/core';

const { status, data, send, open, close } = useWebSocket('ws://localhost:3000', {
  autoReconnect: {
    retries: 10,
    delay: 1000,
    onFailed() {
      console.error('Failed to reconnect WebSocket');
    }
  },
  onMessage(ws, event) {
    const message = JSON.parse(event.data);
    handleMessage(message);
  }
});

function handleMessage(message: any) {
  switch (message.type) {
    case 'update':
      // Handle update
      break;
    case 'presence':
      // Handle presence
      break;
  }
}

function sendUpdate(update: any) {
  send(JSON.stringify({ type: 'update', data: update }));
}
</script>
```

**Pinia Store for Real-Time State**:
```typescript
// stores/realtime.ts
export const useRealtimeStore = defineStore('realtime', {
  state: () => ({
    connectionStatus: 'disconnected' as 'connected' | 'disconnecting' | 'disconnected',
    presence: {} as Record<string, boolean>,
    updates: [] as Update[]
  }),
  
  actions: {
    setConnectionStatus(status: 'connected' | 'disconnecting' | 'disconnected') {
      this.connectionStatus = status;
    },
    
    updatePresence(userId: string, online: boolean) {
      this.presence[userId] = online;
    },
    
    addUpdate(update: Update) {
      this.updates.push(update);
      // Keep only last 100 updates
      if (this.updates.length > 100) {
        this.updates.shift();
      }
    }
  },
  
  getters: {
    isUserOnline: (state) => (userId: string) => {
      return state.presence[userId] ?? false;
    }
  }
});
```

**Watch for Reactive Updates**:
```vue
<script setup lang="ts">
import { watch } from 'vue';
import { useRealtimeStore } from '@/stores/realtime';

const realtimeStore = useRealtimeStore();

// Reactively update UI when presence changes
watch(
  () => realtimeStore.presence,
  (newPresence) => {
    // Update UI based on presence
    updatePresenceUI(newPresence);
  },
  { deep: true }
);
</script>
```

### React

**useWebSocket Custom Hook**:
```tsx
function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setStatus('connected');
      setReconnectAttempts(0);
      setSocket(ws);
    };
    
    ws.onclose = () => {
      setStatus('disconnected');
      setSocket(null);
      
      // Exponential backoff reconnect
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      setTimeout(() => {
        setReconnectAttempts(prev => prev + 1);
        // Reconnect will happen via effect
      }, delay);
    };
    
    ws.onerror = () => {
      setStatus('disconnected');
    };
    
    return () => {
      ws.close();
    };
  }, [url, reconnectAttempts]);
  
  const send = useCallback((data: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    }
  }, [socket]);
  
  return { socket, status, send };
}
```

**Zustand Store for Real-Time State**:
```tsx
import create from 'zustand';

interface RealtimeState {
  connectionStatus: 'connected' | 'disconnected' | 'reconnecting';
  presence: Record<string, boolean>;
  updates: Update[];
  setConnectionStatus: (status: RealtimeState['connectionStatus']) => void;
  updatePresence: (userId: string, online: boolean) => void;
  addUpdate: (update: Update) => void;
}

export const useRealtimeStore = create<RealtimeState>((set) => ({
  connectionStatus: 'disconnected',
  presence: {},
  updates: [],
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  updatePresence: (userId, online) => set((state) => ({
    presence: { ...state.presence, [userId]: online }
  })),
  addUpdate: (update) => set((state) => ({
    updates: [...state.updates.slice(-99), update]
  }))
}));
```

**useSyncExternalStore for Subscription**:
```tsx
function useRealtimeSubscription<T>(selector: (state: RealtimeState) => T): T {
  const store = useRealtimeStore();
  
  return useSyncExternalStore(
    (callback) => {
      // Subscribe to store changes
      return store.subscribe(callback);
    },
    () => selector(store.getState()),
    () => selector(store.getState()) // Server snapshot (same for now)
  );
}

// Usage
function PresenceIndicator({ userId }: { userId: string }) {
  const isOnline = useRealtimeSubscription(
    (state) => state.presence[userId] ?? false
  );
  
  return <span>{isOnline ? '🟢 Online' : '🔴 Offline'}</span>;
}
```

### Spring Boot

**WebSocketMessageBrokerConfigurer with STOMP**:
```kotlin
@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {
    override fun configureMessageBroker(config: MessageBrokerRegistry) {
        // Enable simple broker for pub/sub
        config.enableSimpleBroker("/topic", "/queue")
        // Prefix for messages bound to @MessageMapping methods
        config.setApplicationDestinationPrefixes("/app")
    }
    
    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("*")
            .withSockJS() // Enables fallback transports
    }
}

@Controller
class WebSocketController(
    private val messagingTemplate: SimpMessagingTemplate
) {
    @MessageMapping("/chat")
    @SendTo("/topic/messages")
    fun handleMessage(message: ChatMessage): ChatMessage {
        // Broadcast to all subscribers
        return message
    }
    
    @MessageMapping("/presence")
    fun handlePresence(@Payload presence: PresenceMessage, principal: Principal) {
        // Update presence and broadcast
        messagingTemplate.convertAndSend("/topic/presence", PresenceUpdate(
            userId = principal.name,
            online = presence.online
        ))
    }
}
```

**@MessageMapping Handlers**:
```kotlin
@Controller
class RealtimeController(
    private val messagingTemplate: SimpMessagingTemplate
) {
    @MessageMapping("/updates")
    @SendTo("/topic/updates")
    fun handleUpdate(@Payload update: UpdateMessage, principal: Principal): UpdateMessage {
        // Process update
        val processed = processUpdate(update)
        
        // Broadcast to all subscribers
        return processed
    }
    
    @MessageMapping("/subscribe")
    fun handleSubscribe(@Payload subscription: SubscriptionMessage, principal: Principal) {
        // Handle subscription request
        // Could use Redis pub/sub for horizontal scaling
    }
}
```

**SimpMessagingTemplate for Server-Push**:
```kotlin
@Service
class NotificationService(
    private val messagingTemplate: SimpMessagingTemplate
) {
    fun notifyUser(userId: String, notification: Notification) {
        // Send to specific user's queue
        messagingTemplate.convertAndSendToUser(
            userId,
            "/queue/notifications",
            notification
        )
    }
    
    fun broadcastUpdate(update: Update) {
        // Broadcast to all subscribers of topic
        messagingTemplate.convertAndSend("/topic/updates", update)
    }
}
```

**Redis Pub/Sub for Horizontal Scaling**:
```kotlin
@Configuration
class RedisConfig {
    @Bean
    fun redisMessageListenerContainer(
        connectionFactory: RedisConnectionFactory
    ): RedisMessageListenerContainer {
        val container = RedisMessageListenerContainer()
        container.connectionFactory = connectionFactory
        return container
    }
}

@Service
class RedisPubSubService(
    private val redisTemplate: RedisTemplate<String, String>,
    private val messagingTemplate: SimpMessagingTemplate
) {
    @EventListener
    fun handleRedisMessage(event: RedisMessageEvent) {
        // Forward Redis pub/sub message to WebSocket clients
        messagingTemplate.convertAndSend("/topic/${event.channel}", event.message)
    }
    
    fun publish(channel: String, message: Any) {
        redisTemplate.convertAndSend(channel, message)
    }
}
```

## Accessibility in Real-Time Features

### ARIA Live Regions

**Use aria-live="polite"** for non-critical updates, **aria-live="assertive"** for urgent changes.

**Implementation**:
```tsx
function RealtimeUpdates({ updates }: { updates: Update[] }) {
  return (
    <>
      {/* Non-critical updates - polite */}
      <div aria-live="polite" aria-atomic="false" className="sr-only">
        {updates.map(update => (
          <div key={update.id}>
            {update.message}
          </div>
        ))}
      </div>
      
      {/* Critical updates - assertive */}
      <div aria-live="assertive" aria-atomic="true" className="sr-only">
        {updates.filter(u => u.urgent).map(update => (
          <div key={update.id}>
            Urgent: {update.message}
          </div>
        ))}
      </div>
    </>
  );
}
```

**Vue 3 Implementation**:
```vue
<template>
  <!-- Non-critical updates -->
  <div aria-live="polite" aria-atomic="false" class="sr-only">
    <div v-for="update in updates" :key="update.id">
      {{ update.message }}
    </div>
  </div>
  
  <!-- Critical updates -->
  <div aria-live="assertive" aria-atomic="true" class="sr-only">
    <div v-for="update in urgentUpdates" :key="update.id">
      Urgent: {{ update.message }}
    </div>
  </div>
</template>
```

### Don't Auto-Scroll Viewport

**Pattern**: Don't automatically scroll the user's viewport when new content arrives. Let them control scrolling.

```tsx
function LiveFeed({ items }: { items: Item[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [userHasScrolled, setUserHasScrolled] = useState(false);
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      const isAtBottom = container.scrollHeight - container.scrollTop === container.clientHeight;
      setUserHasScrolled(!isAtBottom);
    };
    
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);
  
  useEffect(() => {
    // Only auto-scroll if user hasn't manually scrolled
    if (!userHasScrolled && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [items, userHasScrolled]);
  
  return <div ref={containerRef}>{/* items */}</div>;
}
```

### Pause Live Updates Option

**Pattern**: Provide a way for screen reader users to pause live updates.

```tsx
function LiveUpdatesControls() {
  const [paused, setPaused] = useState(false);
  
  return (
    <div>
      <button onClick={() => setPaused(!paused)}>
        {paused ? 'Resume' : 'Pause'} Live Updates
      </button>
      {paused && (
        <div aria-live="polite">
          Live updates paused. Click "Resume" to continue receiving updates.
        </div>
      )}
      {!paused && <LiveUpdates />}
    </div>
  );
}
```

## Mobile Considerations

### WebSocket Battery Drain

**Pattern**: Consider SSE or intelligent polling on mobile to reduce battery usage.

**Implementation**:
```typescript
function useMobileOptimizedRealtime(url: string) {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  
  if (isMobile) {
    // Use SSE or polling on mobile
    return useSSE(url);
  } else {
    // Use WebSocket on desktop
    return useWebSocket(url);
  }
}
```

### Network Transitions

**Pattern**: Handle WiFi → Cellular transitions gracefully. Reconnect automatically.

```typescript
class NetworkAwareConnection {
  private connection: ReconnectingWebSocket;
  
  constructor(url: string) {
    this.connection = new ReconnectingWebSocket(url);
    
    // Listen for network changes
    window.addEventListener('online', () => {
      this.connection.reconnect();
    });
    
    window.addEventListener('offline', () => {
      this.connection.disconnect();
    });
  }
}
```

### Reduce Update Frequency on Mobile

**Pattern**: Throttle updates more aggressively on mobile.

```typescript
function useMobileThrottledUpdates<T>(value: T) {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const throttleInterval = isMobile ? 500 : 100; // Slower on mobile
  
  return useThrottledUpdate(value, throttleInterval);
}
```

## Conflict Communication

When conflicts happen, explain clearly: "Alex also edited this field — their version: X, your version: Y — which do you want to keep?"

### Conflict Resolution UI

**Pattern**: Show both versions clearly and let user choose.

**Implementation**:
```tsx
interface Conflict {
  field: string;
  localValue: any;
  remoteValue: any;
  remoteUser: string;
}

function ConflictResolver({ conflict, onResolve }: {
  conflict: Conflict;
  onResolve: (choice: 'local' | 'remote' | 'manual') => void;
}) {
  return (
    <Dialog open>
      <DialogTitle>Conflict Detected</DialogTitle>
      <DialogContent>
        <p>
          <strong>{conflict.remoteUser}</strong> also edited <strong>{conflict.field}</strong>
        </p>
        <div className="conflict-comparison">
          <div>
            <h4>Your version:</h4>
            <div className="value local">{conflict.localValue}</div>
          </div>
          <div>
            <h4>{conflict.remoteUser}'s version:</h4>
            <div className="value remote">{conflict.remoteValue}</div>
          </div>
        </div>
        <p>Which version would you like to keep?</p>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onResolve('local')}>Keep Mine</Button>
        <Button onClick={() => onResolve('remote')}>Keep Theirs</Button>
        <Button onClick={() => onResolve('manual')}>Edit Manually</Button>
      </DialogActions>
    </Dialog>
  );
}
```

**Automatic Conflict Resolution**:
```typescript
// Last-write-wins with conflict detection
function applyChangeWithConflictDetection(
  localState: any,
  localChange: Change,
  remoteChange: Change
): { state: any; conflict?: Conflict } {
  // Check if changes conflict
  if (localChange.field === remoteChange.field && 
      localChange.timestamp < remoteChange.timestamp) {
    // Remote change is newer, but we have a local change
    return {
      state: applyChange(localState, remoteChange),
      conflict: {
        field: localChange.field,
        localValue: localChange.value,
        remoteValue: remoteChange.value,
        remoteUser: remoteChange.userId
      }
    };
  }
  
  // No conflict, apply both
  return {
    state: applyChange(applyChange(localState, localChange), remoteChange)
  };
}
```
