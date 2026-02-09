# Product Perspective: Real-Time & Collaboration

## Contents

- [Why Real-Time Matters](#why-real-time-matters)
- [The Real-Time Spectrum](#the-real-time-spectrum)
- [Use Cases](#use-cases)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Why Real-Time Matters

User expectations for real-time experiences have been fundamentally shaped by products like Slack, Google Docs, and modern collaboration tools. When users see data that's seconds or minutes old, it creates confusion, leads to errors, and breaks trust. A finance dashboard showing yesterday's revenue while a colleague sees today's numbers creates coordination problems. A collaborative document where changes don't appear instantly breaks the flow of collaboration.

Real-time capabilities transform applications from static information displays into living, breathing systems that reflect the current state of the world. This is especially critical in domains like finance, where stale data can lead to poor decisions, or in collaborative editing, where conflicts arise from users working with outdated information.

However, real-time is not a binary choice—it's a spectrum. Understanding where your use case falls on this spectrum is crucial for building the right solution without over-engineering.

## The Real-Time Spectrum

**Polling (Simplest)**
- Client periodically requests updates from server
- Simple to implement, works everywhere
- Higher server load, potential for stale data between polls
- Best for: Low-frequency updates, simple dashboards, when real-time isn't critical

**Server-Sent Events (SSE)**
- One-way server push to client
- Automatic reconnection, simpler than WebSocket
- No bidirectional communication
- Best for: Live feeds, notifications, progress updates, one-way data streams

**WebSocket (Bidirectional)**
- Full-duplex communication channel
- Low latency, efficient for frequent updates
- More complex, requires connection management
- Best for: Chat, collaborative editing, live dashboards, interactive real-time features

**CRDT-Based Collaboration (Most Complex)**
- Conflict-free replicated data types enable true collaborative editing
- Handles offline editing, complex merge scenarios
- Significant implementation complexity
- Best for: Google Docs-style editing, complex document collaboration, offline-first apps

## Use Cases

**Live Data Dashboards**
Finance dashboards showing real-time revenue, transaction volumes, or system health metrics. Users expect to see updates within seconds of events occurring. Example: A revenue dashboard that updates as transactions are processed.

**Collaborative Editing**
Multiple users editing the same document, spreadsheet, or form simultaneously. Changes appear instantly for all participants, with presence indicators showing who's viewing or editing. Example: A team editing a shared budget spreadsheet.

**Presence Indicators**
Showing who's currently online, viewing a page, or actively working on a document. "3 users viewing this page" or "Sarah is editing section 2" provides valuable context. Example: A document editor showing "John and Mary are viewing this document."

**Live Notifications**
Real-time alerts for important events—new messages, system alerts, approval requests. Users expect immediate delivery without page refresh. Example: A notification badge updating instantly when a new invoice is approved.

**Real-Time Chat**
Instant messaging within applications, support chat, or team communication. Messages appear immediately for all participants. Example: A support chat widget where messages appear instantly.

**Activity Feeds**
Live streams of user activity, system events, or audit logs. Users can see what's happening in real-time. Example: An activity feed showing recent invoice approvals, payments, or user actions.

## Personas

**The Data-Driven User**
Expects live data dashboards to reflect current state. Frustrated by stale data that leads to incorrect decisions. Needs confidence that what they see is accurate and up-to-date. Success: Sees revenue numbers update within seconds of transactions.

**The Collaborator**
Works simultaneously with team members on shared documents or data. Needs to see others' changes instantly to avoid conflicts. Values presence indicators showing who's working on what. Success: Edits a shared spreadsheet with 3 colleagues without conflicts or confusion.

**The Admin/Monitor**
Monitors real-time dashboards for system health, security events, or business metrics. Needs reliable, low-latency updates to respond quickly to issues. Success: Receives instant alerts when critical thresholds are breached.

**The Mobile User**
Uses the application on unreliable connections—switching between WiFi and cellular, experiencing network drops. Needs graceful degradation when connections fail, with automatic reconnection. Success: App continues working with polling fallback when WebSocket disconnects.

## Success Metrics

**Data Freshness**
Time from event occurrence to UI update. Target: < 1 second for critical updates, < 5 seconds for general updates. Measure: Event timestamp vs. UI update timestamp.

**Collaboration Conflict Rate**
Percentage of collaborative edits that result in conflicts requiring manual resolution. Target: < 5% for simple edits, < 1% with proper conflict resolution. Measure: Track conflicts vs. total edits.

**Connection Reliability**
Percentage of time WebSocket connection is active. Target: > 99% uptime. Measure: Connection uptime monitoring, reconnection frequency.

**Perceived Responsiveness**
User perception of how "live" the application feels. Target: Users report feeling like data is "always current." Measure: User surveys, time-to-perception metrics.

**Presence Accuracy**
Accuracy of presence indicators (online/offline status). Target: > 95% accuracy. Measure: Compare presence state to actual user activity.

## Common Product Mistakes

**Real-Time Everything**
Not all data needs to be real-time. A user's profile picture doesn't need live updates. A historical report from last month doesn't need real-time updates. Over-engineering real-time for everything increases complexity and server load without user benefit. **Solution**: Identify what truly benefits from real-time—data that changes frequently and where staleness causes problems.

**No Offline/Degraded Mode**
When WebSocket connections fail (network issues, server problems), the application becomes unusable. Users expect graceful degradation. **Solution**: Always implement fallback to polling or cached data. Show connection status so users understand when they're working offline.

**Presence Indicators That Lie**
Showing "John is online" when John closed his laptop 30 minutes ago breaks trust. Stale presence data is worse than no presence data. **Solution**: Implement proper timeout mechanisms, heartbeat systems, and cleanup of stale presence data.

**Real-Time Updates Causing Disruption**
Auto-scrolling a user's viewport when new data arrives, or updating content while they're reading, creates poor UX. **Solution**: Respect user's scroll position, batch updates, provide "pause updates" option.

**Ignoring Mobile Constraints**
WebSocket connections drain battery on mobile devices. Constant reconnection attempts on unreliable networks create poor experiences. **Solution**: Use SSE or polling on mobile, implement smart reconnection strategies, handle network transitions gracefully.
