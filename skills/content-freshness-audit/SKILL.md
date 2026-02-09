---
name: Content Freshness Audit
description: Audit codex content for staleness by checking update dates, referenced technology versions, and industry shifts, producing a prioritised refresh list.
---

# Content Freshness Audit Skill

Scans the Engineering Codex for content that may be out of date — either by age, by referencing outdated technology versions, or by missing recent industry developments. Produces a prioritised list of entries that need refreshing.

## When to Use

- Quarterly maintenance reviews
- Before onboarding a new team or project onto the codex
- After a major technology shift (e.g., new framework version, industry standard change)
- When you suspect content may have drifted from current best practices

## Invocation

```
Audit codex content freshness
```

Or:
```
Which codex content is most out of date?
```

Or with a threshold:
```
Find codex content not updated in the last 3 months
```

Or scoped:
```
Audit freshness of frontend-related facets
```

## Workflow

### Phase 1: Configuration

1. Determine scope — ask if needed using AskQuestion:
   ```
   What would you like to audit?
   1. All facets and experiences (full audit)
   2. Facets only
   3. Experiences only
   4. Specific facets (I'll list them)
   5. Specific category (e.g., Architecture, Security, UX)
   ```
2. Determine staleness threshold — default is 6 months, but ask if the user wants to customise:
   ```
   Flag content older than:
   1. 3 months (aggressive — good for fast-moving areas)
   2. 6 months (balanced — recommended)
   3. 12 months (relaxed — for stable topics)
   ```

### Phase 2: Date-Based Staleness Scan

For each entry in scope:

1. Read the `README.md` and extract the `last_updated` field from YAML frontmatter
2. Calculate age relative to today's date
3. Classify:
   - **Current** — within threshold
   - **Approaching stale** — within 30 days of threshold
   - **Stale** — past threshold
   - **No date** — missing `last_updated` field (treat as stale)

### Phase 3: Technology Reference Check

For each entry, scan its `options.md` and `best-practices.md` for:

1. **Version references** — check if referenced versions are still current:
   - Vue 2 → Vue 3 has been stable since 2022
   - React 17 → React 18/19 patterns
   - Spring Boot 2.x → Spring Boot 3.x
   - Java 11 → Java 17/21
   - Node 16/18 → Node 20/22
   - Gradle 7 → Gradle 8
   - Kotlin 1.x versions
2. **Deprecated tools or patterns** — flag if the content recommends something that has since been deprecated or superseded in the industry (not just at Pax8)
3. **Missing modern alternatives** — flag if a newer, widely-adopted option isn't mentioned (e.g., Bun, Biome, Rspack if they've reached maturity)

### Phase 4: Industry Shift Detection

For key facets, check for significant developments that the content should address:

1. Read each entry's `options.md` to understand what's currently covered
2. Use web search (if available) to check for major releases, new standards, or paradigm shifts in the entry's domain since `last_updated`
3. Flag entries where a significant shift has occurred:
   - New major version of a recommended tool
   - A previously-recommended approach now considered an anti-pattern
   - A new industry standard (e.g., new WCAG version, new HTTP spec)
   - A tool reaching end-of-life

### Phase 5: Freshness Report

Present findings in priority order (most stale / most impactful first):

```markdown
## Content Freshness Audit

**Date:** [Today]
**Scope:** [What was audited]
**Threshold:** [X months]
**Entries audited:** [Count]

### Summary

| Status | Count |
|--------|-------|
| Current | X |
| Approaching stale | X |
| Stale | X |
| Needs technology update | X |
| Needs industry review | X |

### Priority Refresh List

#### High Priority (stale + technology/industry issues)

| Entry | Last Updated | Age | Issues |
|-------|-------------|-----|--------|
| [facets/security/](../../facets/security/) | 2025-08-15 | 6 months | References outdated OWASP Top 10 version |

**What to update:**
- Update OWASP references from 2021 to 2025 edition
- Add coverage of [new concern]

#### Medium Priority (stale by date)

| Entry | Last Updated | Age |
|-------|-------------|-----|
| [facets/frontend-architecture/](../../facets/frontend-architecture/) | 2025-07-01 | 7 months |

#### Low Priority (approaching stale)

| Entry | Last Updated | Age |
|-------|-------------|-----|
| [facets/testing/](../../facets/testing/) | 2025-11-01 | 5 months |

### Current (no action needed)

[Count] entries are within the freshness threshold.
```

### Phase 6: Follow-Up

Ask the user how to proceed:

```
What would you like to do?
1. Start refreshing the highest-priority entry
2. Create Jira tickets for the refresh backlog
3. Save the report as markdown
4. Update all last_updated dates for entries I've just reviewed
5. Deep dive into a specific entry's staleness
```

If refreshing:
1. Open the entry's files and identify specific lines/sections to update
2. Use web search to get current information
3. Apply updates, preserving the existing structure and conventions
4. Update the `last_updated` frontmatter field
5. Regenerate `tag-index.md` if tags changed

If creating Jira tickets:
1. Create one ticket per high/medium priority entry
2. Include the specific issues identified and suggested updates
3. Tag with appropriate labels

## Staleness Heuristics

Some topics age faster than others. Apply these multipliers to the base threshold:

| Category | Multiplier | Rationale |
|----------|-----------|-----------|
| Frontend (frameworks, tooling) | 0.75x | Ecosystem moves fast |
| Security | 0.75x | Threat landscape evolves constantly |
| Backend (patterns, architecture) | 1.0x | More stable, but frameworks update |
| UX/Accessibility | 1.0x | Standards update periodically |
| Process (work management, refactoring) | 1.5x | Process guidance is more durable |
| Data/Persistence | 1.25x | Databases and patterns are relatively stable |

So with a 6-month threshold, frontend content is flagged at 4.5 months while process content isn't flagged until 9 months.

## Error Handling

### Missing Frontmatter

If a README.md lacks `last_updated`:
- Flag as "No date — treat as stale"
- Suggest adding the field during the next update

### Web Search Unavailable

If web search isn't available for Phase 4:
- Skip industry shift detection
- Note in the report: "Industry shift detection skipped — run with web search enabled for full audit"
- Still perform date-based and technology reference checks

## Related Resources

- [Sync Pax8 ADRs Skill](../sync-pax8-adrs/SKILL.md) — Keeps the Pax8 overlay current
- [Tag Index](../../tag-index.md) — Cross-reference of topics and tags
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — Content conventions and frontmatter requirements
