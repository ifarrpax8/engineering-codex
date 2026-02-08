# Cost

Evaluation criterion for decision matrices across the Engineering Codex.

## Definition

The total financial impact of the chosen approach, including direct costs (licensing, infrastructure) and indirect costs (development time, operational overhead, opportunity cost).

## What to Evaluate

- **Licensing** -- Is the tool/service free, open source, or commercially licensed? Per-seat, per-usage, or flat fee?
- **Infrastructure** -- What compute, storage, and networking resources does this approach require?
- **Development time** -- How long will it take to implement, including learning curve?
- **Operational overhead** -- How much ongoing effort is needed to maintain and operate?
- **Opportunity cost** -- What could the team be building instead of implementing this approach?
- **Migration cost** -- How expensive would it be to switch away from this approach later?
- **Scaling cost** -- How does cost grow as usage increases (linear, exponential, stepped)?

## Scoring Guide

- **High cost-efficiency** -- Free/open source, minimal infrastructure, low operational overhead, easy to migrate away from.
- **Medium cost-efficiency** -- Reasonable licensing, moderate infrastructure, manageable operational overhead.
- **Low cost-efficiency** -- Expensive licensing, significant infrastructure, high operational overhead, or costly migration path.

## Budget Context

Some projects have more budget than others. When evaluating cost:
- Note whether an option requires a paid service (e.g., LaunchDarkly vs homegrown feature toggles)
- Identify free/open-source alternatives and their trade-offs
- Consider the long-term total cost of ownership, not just initial cost
