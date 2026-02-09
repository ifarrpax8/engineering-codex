---
title: Notifications
type: experience
last_updated: 2026-02-09
tags: [toast, push-notification, websocket, sse, email, in-app, notification-center, real-time]
---

# Notifications

Alerts, emails, in-app messages, and communication preferences that keep users informed and engaged.

## Contents

- [TL;DR](#tldr)
- [Perspectives](#perspectives)
- [Related Facets](#related-facets)
- [Related Experiences](#related-experiences)

## TL;DR

- **Default approach**: Centralized notification service with channel abstraction (email, push, in-app, SMS) and user preference management
- **Key principle**: Respect user preferences always—never override opt-outs, provide granular control, and honor quiet hours
- **Common gotcha**: Notification spam from cascading events (one action triggers multiple notifications) and email deliverability issues landing messages in spam
- **Where to start**: Implement preference storage first, then build a single notification channel (typically email), and add channels incrementally

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas, notification taxonomy, success metrics
- [Architecture](architecture.md) -- Service design, channel abstraction, delivery pipeline, queuing, real-time delivery
- [Testing](testing.md) -- Channel delivery testing, preference enforcement, template rendering, E2E flows
- [Best Practices](best-practices.md) -- User preference respect, progressive onboarding, actionable notifications, accessibility
- [Gotchas](gotchas.md) -- Common pitfalls: spam, deliverability, timezone issues, stale badges
- [Options](options.md) -- Decision matrix: notification patterns, email providers, real-time transport, orchestration platforms

## Related Facets

- [Event-Driven Architecture](../../facets/event-driven-architecture/) -- Notifications are often triggered by domain events
- [API Design](../../facets/api-design/) -- Notification service APIs and webhook integrations
- [Observability](../../facets/observability/) -- Monitoring notification delivery rates, open rates, and failures
- [Security](../../facets/security/) -- Secure notification channels, preference data protection, unsubscribe mechanisms

## Related Experiences

- [Settings and Preferences](../settings-and-preferences/README.md) -- User notification preferences and controls
- [Real-Time and Collaboration](../real-time-and-collaboration/README.md) -- Real-time notification delivery via WebSocket/SSE
- [Feedback and Support](../feedback-and-support/README.md) -- Support notifications and user communication
