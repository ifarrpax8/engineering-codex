# User Experiences

16 user-centric perspectives on modern application development. While [facets](../facets/) focus on engineering concerns (how things are built), experiences focus on what users see, feel, and interact with.

Every experience provides the same five perspectives as facets: product, architecture, testing, best practices, and options.

## Experience Index

| # | Experience | Description | Category |
|---|------------|-------------|----------|
| 1 | [Onboarding](onboarding/) | First-time user experience, progressive disclosure, activation funnels | User Journey |
| 2 | [Navigation](navigation/) | Information architecture, wayfinding, menu structures, breadcrumbs | Structure |
| 3 | [Search & Discovery](search-and-discovery/) | How users find content/products, filters, sorting, recommendations | Discovery |
| 4 | [Notifications](notifications/) | Alerts, emails, in-app messages, communication preferences | Communication |
| 5 | [Settings & Preferences](settings-and-preferences/) | User configuration, personalization, account management | Personalization |
| 6 | [Data Visualization](data-visualization/) | Charts, dashboards, exports, reporting UX | Data |
| 7 | [Forms & Data Entry](forms-and-data-entry/) | Input patterns, validation, multi-step flows, inline editing | Input |
| 8 | [Responsive Design](responsive-design/) | Mobile, tablet, desktop, progressive enhancement | Layout |
| 9 | [Content Strategy](content-strategy/) | Microcopy, help text, empty states, error messages, tone | Content |
| 10 | [Feedback & Support](feedback-and-support/) | Help systems, feedback collection, support flows | Communication |
| 11 | [Multi-Tenancy UX](multi-tenancy-ux/) | Tenant switching, white-labeling, role-based UI adaptation | Enterprise |
| 12 | [Workflows & Tasks](workflows-and-tasks/) | Task completion patterns, wizards, progress indicators, bulk actions | Interaction |
| 13 | [Tables & Data Grids](tables-and-data-grids/) | Enterprise table patterns, sorting, filtering, pagination | Data |
| 14 | [Permissions UX](permissions-ux/) | Access control communication, disabled states, request access | Security |
| 15 | [Real-Time & Collaboration](real-time-and-collaboration/) | Live updates, presence indicators, WebSocket UX, conflict resolution | Interaction |
| 16 | [Loading & Perceived Performance](loading-and-perceived-performance/) | Skeleton screens, optimistic UI, progressive loading | Performance |

## How Experiences Differ from Facets

| Aspect | Facets | Experiences |
|--------|--------|-------------|
| Focus | How things are built | What users see and feel |
| Perspective | Engineering | User-centric |
| Example | "Use JWT for authentication" | "Show a clear login flow with password recovery" |
| Primary audience | Developers, architects | Developers, designers, product |

## Cross-References

Many experiences connect to engineering facets. For example:
- **Tables & Data Grids** connects to [API Design](../facets/api-design/) (pagination patterns)
- **Permissions UX** connects to [Authentication](../facets/authentication/) (authorization models)
- **Loading & Perceived Performance** connects to [Performance](../facets/performance/) (optimization strategies)
- **Real-Time & Collaboration** connects to [Event-Driven Architecture](../facets/event-driven-architecture/) (messaging patterns)

## Adding New Experiences

Use the `create-facet` skill (it supports both facets and experiences) to scaffold a new experience with all required files.
