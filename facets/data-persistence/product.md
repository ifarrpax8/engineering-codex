---
title: Data Persistence - Product Perspective
type: perspective
facet: data-persistence
last_updated: 2026-02-09
---

# Data Persistence - Product Perspective

Data persistence decisions have profound business implications that extend far beyond technical implementation. Understanding these product-level concerns ensures engineering teams make data architecture choices that align with business objectives, regulatory requirements, and user expectations.

## Contents

- [Data as a Business Asset](#data-as-a-business-asset)
- [Data Consistency Expectations](#data-consistency-expectations)
- [Regulatory Requirements](#regulatory-requirements)
- [Backup and Recovery](#backup-and-recovery)
- [Data Migration Impact on Users](#data-migration-impact-on-users)
- [Success Metrics](#success-metrics)

## Data as a Business Asset

Data outlives applications. A poorly designed database schema or migration strategy can create technical debt that persists for years, constraining product evolution and increasing maintenance costs. Conversely, well-architected data persistence enables rapid feature development, supports business intelligence initiatives, and provides a foundation for future product capabilities.

The business value of data extends beyond immediate application needs. Historical data enables trend analysis, customer behavior insights, and predictive analytics. Event-sourced systems capture not just what happened, but when and in what sequence—information that becomes invaluable for compliance, debugging, and business intelligence. Data architecture decisions made today determine what questions the business can answer tomorrow.

## Data Consistency Expectations

Users expect writes to be immediately visible. When a customer updates their profile, they expect to see the change reflected immediately in their next page load. When an order is placed, the order confirmation page should show accurate details. These expectations drive the need for strong consistency in critical user-facing flows.

Eventual consistency surprises users when not communicated. If a user updates their account settings and those changes take several seconds to propagate to all read replicas, they may perceive the application as buggy or unreliable. Product teams must understand the consistency guarantees of their data layer and design user experiences accordingly—either by ensuring strong consistency where needed, or by clearly communicating eventual consistency boundaries to users.

Financial operations require absolute consistency. A payment transaction must be atomic: either the money is deducted from the payer and credited to the payee, or neither change occurs. Partial states are unacceptable. This drives the use of database transactions with appropriate isolation levels, and may require distributed transaction patterns or saga orchestration for cross-service operations.

## Regulatory Requirements

### GDPR (General Data Protection Regulation)

The right to erasure requires that personal data can be completely removed from systems. This creates technical challenges: cascading deletes across related tables, handling soft-deleted records, purging data from backups, and ensuring event-sourced systems can handle data removal requests. Product teams must design data models that support deletion workflows without breaking referential integrity or audit requirements.

Data portability mandates that users can export their data in a machine-readable format. This requires query capabilities that can assemble a complete user data export, including relationships and historical records. Event-sourced systems have an advantage here, as they can replay events to reconstruct user data at any point in time.

Consent tracking requires immutable audit trails. When a user grants or revokes consent for data processing, that decision must be recorded with a timestamp and cannot be retroactively modified. Event sourcing naturally supports this, while traditional databases require careful audit table design.

### SOC2 Compliance

Audit trails must capture who accessed what data and when. This requires comprehensive logging of data access patterns, not just writes. Database access logs, application-level audit tables, and event sourcing all contribute to meeting audit requirements. Product teams must balance audit completeness with performance and storage costs.

Access logging extends beyond authentication events. SOC2 requires tracking data access patterns, including read operations on sensitive data. This may require implementing database-level audit logging or application-level access tracking, which can impact query performance.

### Data Residency

Geographic data storage requirements vary by jurisdiction. Some countries require that citizen data remains within national borders. Financial regulations may require transaction data to be stored in specific regions. Product teams must understand these requirements early, as retrofitting data residency controls after launch is expensive and may require architectural changes.

Multi-region deployments introduce complexity: replication lag, conflict resolution, and compliance verification across regions. Event sourcing can simplify this by allowing region-specific projections while maintaining a single source of truth.

## Backup and Recovery

### Recovery Point Objective (RPO)

RPO defines how much data loss is acceptable. A system with hourly backups has an RPO of one hour—in a disaster, up to one hour of data could be lost. Financial systems typically require RPO measured in minutes or seconds, driving continuous replication or synchronous backups. Product requirements should explicitly define RPO, as this drives technical decisions around backup frequency, replication strategies, and transaction log retention.

### Recovery Time Objective (RTO)

RTO defines how quickly systems must be operational after a disaster. A system with an RTO of four hours must be able to restore service within four hours of a failure. This drives decisions around backup storage locations, restoration procedures, and failover mechanisms. Product teams must understand business continuity requirements to set appropriate RTO targets.

### Business Expectations for Disaster Recovery

Business stakeholders often assume zero data loss and instant recovery, but achieving these goals requires significant engineering investment. Product teams must facilitate conversations that balance business needs with technical feasibility and cost. Documented RPO and RTO targets, validated through disaster recovery drills, set realistic expectations and guide engineering investment priorities.

## Data Migration Impact on Users

Schema changes should be invisible to users. When adding a new field to a user profile, the migration should complete without users noticing any disruption. This requires backward-compatible migrations: new code must work with old schema, and old code must continue working during the transition period. The expand/contract pattern enables this by adding new columns before removing old ones.

Migration downtime should be zero or near-zero. Modern applications cannot tolerate maintenance windows for schema changes. Zero-downtime migrations require careful planning: adding columns without defaults, backfilling data in batches, then adding defaults. Dropping columns requires deploying code that no longer uses the column before removing it from the schema.

Backward compatibility during rollout enables gradual code deployments. When changing how data is stored, the migration adds the new structure while preserving the old. Code is deployed that writes to both structures, then reads from the new structure. Only after all instances are running new code can the old structure be removed. This pattern prevents deployment-related outages but requires discipline to execute correctly.

## Success Metrics

### Query Latency

Query latency directly impacts user experience. P50 latency (median) indicates typical performance, while P95 and P99 reveal tail latencies that affect user perception. Slow queries degrade user experience and may indicate missing indexes, inefficient query patterns, or database resource constraints. Product teams should monitor query latency percentiles and set service level objectives (SLOs) based on user experience requirements.

### Data Freshness

Data freshness measures how stale cached or projected data can become. In event-sourced systems, read models are projections that may lag behind the event stream. Users updating their profile expect to see changes immediately, but if the profile read model has a 30-second projection lag, users may see stale data. Product teams must understand freshness requirements and design caching and projection strategies accordingly.

### Migration Success Rate

Failed migrations cause outages. Tracking migration success rate—the percentage of migrations that complete without rollback or manual intervention—indicates the health of the migration process. High success rates require thorough testing, backward compatibility, and careful execution. Low success rates indicate process problems that must be addressed before they cause production incidents.

### Backup Restore Time

Backup restore time validates disaster recovery capabilities. Regular restore drills measure actual RTO and identify bottlenecks in the restoration process. Slow restores may indicate backup storage location issues, network constraints, or inefficient restore procedures. Product teams should schedule regular disaster recovery drills to validate RPO and RTO targets.

### Data Integrity Error Rate

Data integrity errors—constraint violations, orphaned records, inconsistent state—indicate problems in application logic or migration processes. These errors can cause application failures, incorrect business logic, or compliance violations. Monitoring data integrity error rates and investigating root causes prevents small problems from becoming systemic issues.
