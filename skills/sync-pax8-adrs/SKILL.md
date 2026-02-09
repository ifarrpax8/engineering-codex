---
name: Sync Pax8 ADRs
description: Compare the Pax8 ADR repository against the codex standards map, surfacing new, changed, and superseded ADRs that need attention.
---

# Sync Pax8 ADRs Skill

Scans the Pax8 ADR repository and diffs it against `pax8-context/standards-map.md` and `pax8-context/deprecated.md` to identify what's changed since the last sync. Produces a clear action list for keeping the Pax8 overlay current.

## When to Use

- Periodically (monthly, or after a burst of ADR activity)
- When someone mentions new ADRs have been accepted
- Before running `evaluate-options` on a Pax8 project if the overlay might be stale
- After an architecture guild or tech radar session

## Prerequisites

The `adr` repository must be in the current workspace. If it's not, the skill will prompt the user to add it.

## Invocation

```
Sync Pax8 ADRs
```

Or:
```
Are there any new Pax8 ADRs since our last sync?
```

Or:
```
Check if the Pax8 standards map is up to date
```

## Workflow

### Phase 1: Discover ADRs in Repository

1. Check that the `adr` repository is present in the workspace
2. If not found, tell the user: "The `adr` repository needs to be in your workspace. Add it and try again."
3. Scan the `adr/` directory for all ADR folders matching the pattern `000XX-description/`
4. For each ADR, read its `README.md` and extract:
   - ADR number
   - Title
   - Status (Accepted, Deprecated, Superseded, Draft)
   - A brief summary of the Decision section (first 2-3 sentences)
   - Any "Superseded by" or "Supersedes" references

### Phase 2: Load Current Standards Map

1. Read `@engineering-codex/pax8-context/standards-map.md`
2. Parse the ADR table to build a set of currently-mapped ADR numbers
3. Read `@engineering-codex/pax8-context/deprecated.md`
4. Parse the deprecated table to build a set of currently-deprecated entries

### Phase 3: Diff and Classify

Compare the repository state against the map and classify each ADR:

- **New** — ADR exists in the repo but not in `standards-map.md` or `deprecated.md`
- **Superseded** — ADR is in `standards-map.md` as active but the repo shows it as Superseded or Deprecated
- **Changed** — ADR title or decision content has materially changed from the summary in the map
- **Draft** — ADR exists in the repo with Draft status (not yet actionable, but worth noting)
- **Synced** — ADR matches the current map entry, no action needed

For each New ADR, also:
1. Attempt to map it to a codex facet based on its content
2. Suggest a type classification (Standard vs Guidance) based on the language strength ("must", "should", "may", "recommended")

### Phase 4: Present Findings

```markdown
## Pax8 ADR Sync Report

**Last synced:** [date from standards-map.md or "unknown"]
**ADRs in repository:** [count]
**ADRs in standards map:** [count]

### Action Required

#### New ADRs (not yet mapped)

| ADR | Title | Suggested Facet | Suggested Type | Summary |
|-----|-------|----------------|----------------|---------|
| 000XX | [Title] | [facet] | Standard/Guidance | [Brief summary] |

#### Superseded (remove from active map, move to deprecated)

| ADR | Title | Superseded By | Current Facet |
|-----|-------|---------------|---------------|
| 000XX | [Title] | ADR-000YY | [facet] |

#### Changed (summary may need updating)

| ADR | Title | What Changed |
|-----|-------|-------------|
| 000XX | [Title] | [Description of change] |

### Informational

#### Drafts (not yet accepted)

| ADR | Title | Potential Facet |
|-----|-------|----------------|
| 000XX | [Title] | [facet] |

### No Action Needed

[Count] ADRs are synced and current.
```

### Phase 5: Apply Updates

Ask the user how to proceed:

```
What would you like to do?
1. Apply all suggested updates to the standards map
2. Review and selectively apply updates
3. Save the report as markdown
4. Just review — I'll update manually later
```

If applying updates:

1. For **New** ADRs: Add rows to the standards map table and the by-facet grouping
2. For **Superseded** ADRs: Remove from `standards-map.md`, add to `deprecated.md` with the superseding ADR noted
3. For **Changed** ADRs: Update the summary text in the map
4. Update the `last_updated` field or add a sync date comment
5. Stage and commit the changes with message: "Sync Pax8 ADR overlay — [count] updates"

If reviewing selectively:
1. Present each update one at a time using AskQuestion
2. For each, offer: Accept, Skip, Modify
3. Apply only accepted updates

### Phase 6: New Facet Check

After syncing, check if any new ADRs point to topics not covered by existing codex facets:

1. For each new ADR's suggested facet, verify the facet exists in `@engineering-codex/facets/`
2. If a new ADR doesn't map cleanly to any existing facet, flag it:
   ```
   ADR-000XX ([Title]) doesn't map to an existing codex facet.
   Consider creating a new facet for: [suggested topic]
   Use the `create-facet` skill to scaffold it.
   ```

## Error Handling

### ADR Repository Not Found

If the `adr` directory is not in the workspace:
- List workspace directories to confirm
- Instruct: "Clone or add the `adr` repository to your workspace, then re-run this skill"

### Unparseable ADR

If an ADR's README.md doesn't follow the expected format:
- Log it as "Unable to parse" with the file path
- Continue processing other ADRs

### No Changes Found

If everything is synced:
- Report: "All [count] ADRs are current. No updates needed."
- Show the date of the last sync

## Related Resources

- [Pax8 Standards Map](../../pax8-context/standards-map.md) — Current ADR-to-facet mapping
- [Deprecated Technologies](../../pax8-context/deprecated.md) — Technologies being phased out
- [Pax8 Standard Command](../../commands/pax8-standard.md) — Quick lookup of Pax8 standards
- [Create Facet Skill](../create-facet/SKILL.md) — Scaffold new facets for unmapped topics
