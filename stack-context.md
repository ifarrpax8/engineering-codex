# Stack Context

This codex is language-agnostic in its principles but acknowledges the technology landscape of the teams that use it. When a best practice or option is materially affected by framework or language choice, stack-specific callouts are included.

## Assumed Technology Landscape

### Frontend

- **Language:** JavaScript / TypeScript
- **Frameworks:** Vue 3 (Composition API) or React
- **Styling:** Tailwind CSS, component library (Propulsion)
- **Build Tooling:** Vite
- **State Management:** Pinia (Vue) or Zustand/TanStack Query (React)
- **Testing:** Vitest, Playwright, Testing Library
- **Architecture Pattern:** Micro-Frontend (MFE) or Single Page Application (SPA)

### Backend

- **Language:** Java or Kotlin
- **Framework:** Spring Boot
- **Build Tool:** Gradle
- **Architecture Patterns:** Layered, Hexagonal, CQRS + Event Sourcing (Axon Framework)
- **Testing:** JUnit 5, MockK (Kotlin) / Mockito (Java), Testcontainers
- **API Style:** REST (primary), event-driven messaging

### Infrastructure

- **Containerization:** Docker
- **Infrastructure as Code:** Terraform
- **CI/CD:** GitHub Actions
- **Observability:** Structured logging, metrics, distributed tracing
- **Feature Toggles:** LaunchDarkly (when budget allows), environment-based flags (baseline)

### Data

- **Primary Database:** PostgreSQL
- **Event Store:** Axon Server (for event-sourced services)
- **Caching:** Redis (when applicable)
- **Message Broker:** Kafka / RabbitMQ

## How Stack Context is Used

Throughout the codex, you will see callouts like:

> **Vue:** Prefer `<script setup>` with Composition API for component definitions.
>
> **React:** Prefer function components with hooks. Avoid class components.

> **Kotlin:** Use data classes for DTOs and sealed classes for domain state.
>
> **Java:** Use records for DTOs (Java 16+). Prefer sealed interfaces for domain state (Java 17+).

These callouts appear only when the framework or language choice materially changes the recommendation. If a best practice is truly universal, no callout is needed.

## Updating This File

If the team adopts new technologies or retires existing ones, update this file and add a CHANGELOG entry. Review any facet `best-practices.md` files that may reference the changed technology.
