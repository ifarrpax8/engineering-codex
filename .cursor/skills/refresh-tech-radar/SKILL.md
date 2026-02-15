---
name: refresh-tech-radar
description: Regenerate the Tech Radar from current codex facets, Pax8 standards, and deprecated technologies.
---

# Refresh Tech Radar Skill

Regenerates the tech radar files (`tech-radar.md`, `tech-radar-pax8.md`, and `tech-radar.json`) by scanning the current state of all codex facets and Pax8 context. Ensures the radar accurately reflects the latest recommendations, alternatives, and deprecations.

## When to Use

- After updating any facet's `options.md` or `best-practices.md`
- After running `sync-pax8-adrs` (which may change the Pax8 overlay)
- After adding new facets or experiences
- Periodically (quarterly) to ensure the radar stays current
- After a content freshness audit identifies changes

## When NOT to Use

- **Syncing Pax8 ADRs** — run [Sync Pax8 ADRs](../sync-pax8-adrs/SKILL.md) first, then refresh the radar
- **Auditing content freshness** — use [Content Freshness Audit](../content-freshness-audit/SKILL.md) to check if content needs updating before regenerating
- **Evaluating a single technology** — use [Evaluate Options](../evaluate-options/SKILL.md) for focused decision-making

## Invocation

```
Refresh the tech radar
```

Or:
```
Regenerate tech radar from current codex content
```

Or scoped:
```
Update just the Pax8 overlay on the tech radar
```

## Workflow

### Phase 1: Scan Codex Content

For each facet in `@engineering-codex/facets/`:

1. Read `options.md` and classify each technology/approach:
   - **Adopt**: Marked as "recommended", "default", "best practice", or the top recommendation in best-practice mode
   - **Trial**: Marked as "strong alternative", "viable option", or highly rated in decision-matrix mode
   - **Assess**: Mentioned positively but without a clear recommendation, or labelled as "situational"
   - **Hold**: Marked as "avoid", "not recommended", "escape hatch only", or "migrate away from"

2. Read `best-practices.md` for additional technology signals:
   - Technologies demonstrated in code examples → at least Trial
   - Technologies explicitly warned against → Hold

3. Read `gotchas.md` for anti-pattern signals:
   - Tools or patterns called out as common mistakes → potential Hold

### Phase 2: Classify into Quadrants

Assign each technology to one of the four ThoughtWorks quadrants:

| Quadrant | What Goes Here | Examples |
|----------|---------------|---------|
| **Techniques** | Architectural patterns, methodologies, development approaches | CQRS, TDD, trunk-based development, pagination strategies |
| **Platforms** | Databases, infrastructure, cloud services, runtime environments | PostgreSQL, Kafka, Kubernetes, Redis, OpenSearch |
| **Tools** | Build tools, CI/CD, testing frameworks, linters, dev tools | GitHub Actions, Vitest, Playwright, Terraform, ESLint |
| **Languages & Frameworks** | Programming languages, application frameworks, libraries | Kotlin, Vue 3, Spring Boot, Pinia, Tailwind CSS |

Rules for ambiguous cases:
- If it's a framework that defines how you architect: **Languages & Frameworks**
- If it's a framework that runs in CI/CD: **Tools**
- If it's a service you deploy and connect to: **Platforms**
- If it's a methodology or pattern you follow: **Techniques**

### Phase 3: Build General Radar

For each classified technology:

1. Determine its ring (Adopt/Trial/Assess/Hold)
2. Write a one-line rationale (why this ring?)
3. Link to the source facet
4. Position it in the Mermaid quadrant chart:
   - X-axis (adoption): How widely adopted/recommended across facets (0.0 = niche, 1.0 = universal)
   - Y-axis (confidence): How confident the recommendation is (0.0 = uncertain, 1.0 = definitive)
   - Adopt items: top-right quadrant (>0.65, >0.80)
   - Trial items: bottom-right quadrant (>0.35, 0.60-0.80)
   - Assess items: top-left quadrant (<0.35, 0.45-0.65)
   - Hold items: bottom-left quadrant (<0.25, <0.30)

Generate the `tech-radar.md` file with:
- One Mermaid quadrant chart per quadrant (Techniques, Platforms, Tools, Languages & Frameworks)
- Tables per ring within each quadrant (Adopt, Trial, Assess, Hold)
- Summary counts
- Last generated date

### Phase 4: Build Pax8 Overlay

1. Read `@engineering-codex/pax8-context/standards-map.md`
2. Read `@engineering-codex/pax8-context/deprecated.md`
3. For each Pax8 Standard:
   - If the general ring is Trial or Assess → promote to Adopt for Pax8
   - If the general ring is already Adopt → mark as "Adopt (Mandated)"
4. For each Pax8 Guidance:
   - Note it as recommended but not mandated
5. For each deprecated technology:
   - Ensure it's in Hold and mark as "Hold (Deprecated)"
6. Identify Pax8-specific technologies not in the general radar:
   - Add them with their Pax8 ring
7. Generate `tech-radar-pax8.md` with:
   - Ring change table (what moved and why)
   - Pax8-specific additions
   - Mermaid comparison chart
   - Summary counts

### Phase 5: Generate JSON Export

Generate `tech-radar.json` in Zalando Tech Radar format:

```json
[
  {
    "name": "Technology Name",
    "ring": "adopt|trial|assess|hold",
    "quadrant": "techniques|platforms|tools|languages-and-frameworks",
    "isNew": true|false,
    "description": "One-line rationale"
  }
]
```

Rules:
- `isNew` is true if the technology wasn't in the previous radar (compare against existing JSON before overwriting)
- Quadrant names must match Zalando conventions exactly
- Ring names must be lowercase

### Phase 6: Validate and Commit

1. Run link validation on the three radar files
2. Present a summary of changes:
   ```
   Tech Radar refreshed:
   - General: X adopt, Y trial, Z assess, W hold
   - Pax8 overlay: A promotions, B demotions, C additions
   - New since last refresh: [list of newly added technologies]
   - Removed since last refresh: [list of removed technologies]
   - Ring changes: [list of technologies that moved rings]
   ```
3. Ask the user:
   ```
   How would you like to proceed?
   1. Save all changes and commit
   2. Review changes before saving
   3. Adjust specific entries before saving
   ```

## Verification

- **Phase 1**: Confirm every facet with an `options.md` was scanned. List any facets that were skipped and why.
- **Phase 3**: Verify no technology appears in multiple rings. If duplicates detected, flag for resolution.
- **Phase 5**: Confirm `tech-radar.json` is valid JSON by parsing it. Confirm `isNew` flags are accurate by comparing against the previous JSON.
- **Phase 6**: Confirm all source facet links in the radar files resolve to actual files.

## Worked Example

**Input:** `Refresh the tech radar`

**Key steps:**
1. Scanned 18 facets — extracted 64 technologies from `options.md` and `best-practices.md` files
2. Classified: 22 Adopt, 18 Trial, 15 Assess, 9 Hold
3. Built Pax8 overlay: 3 promotions (Trial→Adopt for Pax8 standards), 2 Pax8-specific additions
4. Generated JSON export: 64 entries, 4 marked `isNew` since last refresh

**Output excerpt:**
```
Tech Radar refreshed:
- General: 22 adopt, 18 trial, 15 assess, 9 hold
- Pax8 overlay: 3 promotions, 0 demotions, 2 additions
- New since last refresh: OpenTelemetry, Biome, Spring Boot 3.4, TypeSpec
- Ring changes: Vuex (Trial→Hold), Pinia (Trial→Adopt)
```

## Deduplication Rules

- Each technology appears only once in the radar, even if mentioned across multiple facets
- Use the strongest recommendation (most confident ring) when a technology appears in multiple facets
- If recommendations conflict across facets, prefer the facet most closely related to the technology's primary purpose

## Consistency Checks

After generating, verify:
- Every Adopt technology has a matching entry in at least one `options.md` or `best-practices.md`
- Every Hold technology has a clear warning in at least one `gotchas.md` or `options.md`
- No technology appears in multiple rings
- All source facet links resolve
- Mermaid chart coordinates don't overlap (minimum 0.03 separation)

## Error Handling

### Missing options.md

If a facet lacks `options.md`:
- Skip it and note: "Facet [name] has no options.md — no technologies extracted"

### Conflicting Recommendations

If the same technology is recommended in one facet but warned against in another:
- Flag it for manual review
- Present both perspectives and ask the user to decide

## Related Resources

- [Tech Radar (General)](../../../tech-radar.md) — Industry best practice radar
- [Tech Radar (Pax8)](../../../tech-radar-pax8.md) — Pax8-adjusted overlay
- [Tech Radar (JSON)](../../../tech-radar.json) — Zalando-compatible export
- [Sync Pax8 ADRs](../sync-pax8-adrs/SKILL.md) — Keep Pax8 context current before refreshing
- [Content Freshness Audit](../content-freshness-audit/SKILL.md) — Check if underlying content needs updating first
