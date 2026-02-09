# Deprecated Technologies at Pax8

Technologies and approaches that Pax8 is actively moving away from. If you encounter these in existing code, plan to migrate. Do not use them in new projects.

## Deprecated

| Technology | Was Used For | Replacement | Source ADR | Notes |
|-----------|-------------|-------------|-----------|-------|
| NewRelic | Application Performance Monitoring, metrics, dashboards | OpenTelemetry + alternative observability platform | ADR-00009 | Migration in progress; do not create new NewRelic dashboards or alerts |
| Legacy Secrets Management | External secrets injection | AWS Secrets Manager with standardised process | ADR-00045 (superseded by ADR-00064) | Old approach deprecated; use the certificate management process defined in ADR-00064 |
| Moment.js | Date/time manipulation in frontend | DayJS | ADR-00049 | Moment.js is in maintenance mode; DayJS is a drop-in replacement with smaller bundle |
| Legacy Branch Protection | Repository branch protection rules | GitHub Repository Rulesets | ADR-00034 | Rulesets offer more granular control and are the organisation standard |
| Axon Server | Event store for CQRS/event sourcing | Axon Framework with Kafka + PostgreSQL | ADR-00060 | Axon Server removed from architecture; use Kafka for event distribution and PostgreSQL for event storage |
| ext dependency variables in Gradle | Sharing dependency versions across modules | Gradle version catalogs (libs.versions.toml) | ADR-00025 | Version catalogs provide better IDE support and type safety |

## Approaching Deprecation

Technologies not yet formally deprecated but trending that direction. Monitor for upcoming ADRs.

| Technology | Concern | Likely Direction |
|-----------|---------|-----------------|
| Manual GitHub team management | Inconsistent access, no audit trail | Full migration to Entra SSO-based team assignment (ADR-00040) |
