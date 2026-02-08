# Scaling Triggers

Universal inflection point triggers that signal when an architectural decision should be reconsidered. These apply across all facets and evolution journeys.

## Team Size

| Trigger | Signal | Consider |
|---------|--------|----------|
| 1-5 developers | Single team, tight communication | Monolith + SPA is appropriate |
| 5-10 developers | Sub-teams forming, merge conflicts increasing | Modulith, feature-based code splitting |
| 10-20 developers | Multiple teams, deployment coordination needed | Microservices, MFEs |
| 20+ developers | Teams need full autonomy | Platform team, self-service infrastructure |

## Deployment Frequency

| Trigger | Signal | Consider |
|---------|--------|----------|
| Weekly or less | Comfortable with coordinated releases | Monolith/SPA is fine |
| Multiple times per week | Deployment coordination becoming overhead | Independent deployability per team |
| Daily or continuous | Teams blocked waiting for others to deploy | Must have independent deployment pipelines |

## Codebase Complexity

| Trigger | Signal | Consider |
|---------|--------|----------|
| Any developer can understand the whole codebase | Simple, well-organized | Current architecture is appropriate |
| New developers take weeks to onboard | Growing complexity | Better module boundaries, documentation |
| No one understands the full codebase | Excessive coupling, unclear boundaries | Modulith or service extraction |
| Changes frequently cause unexpected breakages | Hidden dependencies | Architecture boundary enforcement |

## Performance and Scale

| Trigger | Signal | Consider |
|---------|--------|----------|
| Single server handles all traffic | Low scale | No scaling concerns |
| Need for horizontal scaling | Growing traffic | Stateless services, load balancing |
| Hot spots in specific features | Uneven load distribution | Independent scaling of specific components |
| Database becoming bottleneck | Data scale | Read replicas, CQRS, database per service |

## Build and Test Times

| Trigger | Signal | Consider |
|---------|--------|----------|
| Build < 2 minutes | Fast feedback loop | No action needed |
| Build 2-10 minutes | Slowing down | Incremental builds, parallelization |
| Build > 10 minutes | Significantly impacting productivity | Module-level builds, pipeline optimization |
| Full test suite > 30 minutes | Tests becoming a bottleneck | Test parallelization, service-level testing |

## Business Domain

| Trigger | Signal | Consider |
|---------|--------|----------|
| Single bounded context | All features tightly related | Single service/module |
| Emerging bounded contexts | Features becoming logically independent | Module boundaries or service extraction |
| Distinct domain teams | Business organized around domains | Service per bounded context |
| Regulatory boundaries | Different compliance requirements per domain | Physical separation for compliance |

## How to Use These Triggers

1. **Don't act on a single trigger.** Look for a pattern of multiple triggers aligning.
2. **Favor gradual evolution.** Move one step at a time (monolith → modulith → microservices), not in a big bang.
3. **Measure before and after.** Document your current pain points and verify the evolution addressed them.
4. **Check facet-specific triggers.** Each facet's `options.md` has an `## Evolution Triggers` section with more targeted guidance.
5. **Document the decision.** Use an [ADR](../decision-frameworks/adr-template.md) to capture why the evolution was warranted.

## Related Guides

- [Monolith to Microservices](monolith-to-microservices.md)
- [SPA to MFE](spa-to-mfe.md)
- [Refactoring Facet](../facets/refactoring/) -- For code-level evolution guidance
