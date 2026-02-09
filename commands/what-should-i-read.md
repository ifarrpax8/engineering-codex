# What Should I Read? Command

Maps a task description to the most relevant Engineering Codex content, producing a prioritized reading list.

## Usage

```
I'm adding pagination to the orders API
```

Or more explicitly:
```
What should I read before building a multi-step form?
```

Or for a broad topic:
```
What should I read about security for our new service?
```

## Behavior

1. Parse the user's task description to extract:
   - **Domain signals** — keywords like "pagination", "form", "authentication", "WebSocket"
   - **Action signals** — "adding", "building", "refactoring", "debugging", "reviewing"
   - **Stack signals** — "API", "frontend", "backend", "MFE"
2. Map signals to codex content using this priority order:
   - **Primary facet/experience** — the most directly relevant one (e.g., "pagination" → api-design + tables-and-data-grids)
   - **Supporting facets** — adjacent concerns (e.g., pagination also touches performance, data-persistence)
   - **Relevant checklists** — if the action suggests a review or launch
   - **Gotchas** — always include the gotchas.md for the primary facet
   - **Evolution guides** — if the task involves architectural change
3. For each recommended item, specify the most relevant file (not just the facet):
   - "Adding pagination" → `api-design/architecture.md` (the pagination section), not just "api-design"
   - "Building a form" → `forms-and-data-entry/product.md` (user flows) + `architecture.md` (state management)
4. Order by relevance: most directly useful first, supporting context after

## Output Format

```markdown
## Reading List: "[Task Description]"

### Start Here
1. **[Facet/Experience — Specific File]** — [Why: one sentence explaining relevance]
2. **[Facet/Experience — Specific File]** — [Why]

### Also Relevant
3. **[Facet/Experience — Specific File]** — [Why]
4. **[Facet/Experience — Specific File]** — [Why]

### Watch Out For
5. **[Gotchas File]** — [Key gotcha to be aware of]

### If This Grows
6. **[Evolution Guide or Options File]** — [When you'd need this]

> Ready to dive in? Use: `Deep dive into [primary facet]`
> Need to make a decision? Use: `Evaluate options for [facet]`
```

## Signal Mapping Examples

| Task Keywords | Primary Content | Supporting Content |
|--------------|----------------|-------------------|
| pagination, paging, page size | api-design/architecture.md, tables-and-data-grids | performance, data-persistence |
| form, input, validation, wizard | forms-and-data-entry | accessibility, content-strategy |
| auth, login, JWT, OAuth | authentication | security, permissions-ux |
| WebSocket, real-time, live | real-time-and-collaboration | event-driven-architecture, state-management |
| table, grid, sort, filter | tables-and-data-grids | api-design, performance |
| deploy, launch, release | ci-cd, production-readiness checklist | observability, security-review checklist |
| refactor, extract, split | refactoring-and-extraction | evolution guides, backend/frontend-architecture |
| test, coverage, quality | testing | relevant facet's testing.md |
| i18n, translate, locale | internationalization | content-strategy |
| error, exception, handling | error-handling | observability, content-strategy |
| feature flag, toggle | feature-toggles | configuration-management |

## Related Resources

- [Facets Index](../facets/README.md) — All available engineering facets
- [Experiences Index](../experiences/README.md) — All available user experiences
- [Reading Paths](../reading-paths.md) — Role-based static reading paths
- [Glossary](../glossary.md) — Terminology reference
- [Facet Deep Dive Skill](../skills/facet-deep-dive/SKILL.md) — Deep dive after finding what to read
- [Evaluate Options Skill](../skills/evaluate-options/SKILL.md) — When the reading leads to a decision
