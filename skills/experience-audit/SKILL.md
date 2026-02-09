---
name: Experience Audit
description: Review your frontend implementation against an Engineering Codex experience's guidelines, identifying UX gaps and improvement opportunities.
---

# Experience Audit Skill

Reviews your frontend code and components against a specific user experience's guidelines from the Engineering Codex. Identifies UX gaps, missing patterns, accessibility issues, and improvement opportunities with links to relevant best practices.

## When to Use

- Building a new feature and want to ensure it follows UX best practices
- Reviewing an existing feature's user experience quality
- Preparing for a UX review or design critique
- Checking whether common gotchas have been avoided in a specific area
- Validating that forms, tables, navigation, or other UX patterns are well-implemented

## Invocation

```
Audit our forms against forms-and-data-entry
```

Or with a specific component:
```
Audit the ScheduledOrders table against tables-and-data-grids
```

Or broadly:
```
Experience audit of finance-mfe for notifications and loading patterns
```

## Workflow

### Phase 1: Identify Experience and Scope

1. Parse the user's request to identify:
   - Which experience(s) to audit against — match against `@engineering-codex/experiences/`
   - Which project or specific component to audit
2. If ambiguous, list available experiences using AskQuestion
3. Ask about scope:
   ```
   What scope would you like to audit?
   1. Entire project (scan all relevant components)
   2. Specific feature or directory (e.g., src/components/Orders/)
   3. Single component (e.g., ScheduledOrders/TableView.vue)
   ```

### Phase 2: Load Experience Guidelines

For the selected experience, read all 7 perspective files:
1. `product.md` — expected user flows and personas
2. `architecture.md` — implementation patterns
3. `testing.md` — what should be tested and how
4. `best-practices.md` — principles to follow
5. `gotchas.md` — pitfalls to check for
6. `options.md` — approach options and recommendations

Extract key checkpoints from each file:
- Required UX patterns (from product.md)
- Recommended implementation approaches (from architecture.md)
- Known gotchas to scan for (from gotchas.md)
- Best practice violations to detect (from best-practices.md)

### Phase 3: Codebase Analysis

1. Read `@engineering-codex/stack-context.md` for framework context (Vue/React)
2. Explore the target scope in the project:
   - Component structure and organization
   - State management patterns used
   - User interaction handling
   - Error and loading states
   - Accessibility attributes (aria-*, roles, labels)
   - Responsive design implementation
   - i18n/l10n usage
3. For each checkpoint from Phase 2, search for evidence of implementation

### Phase 4: Findings Report

Present findings organized by perspective:

```markdown
## Experience Audit: [Experience Name] — [Project/Component]

**Date:** [Today's date]
**Experience:** [Name with link to experience README]
**Scope:** [What was audited]

### Product Alignment
| Expected Flow/Pattern | Status | Notes |
|----------------------|--------|-------|
| [Pattern from product.md] | Implemented / Missing / Partial | [Details] |

### Architecture Patterns
| Recommended Pattern | Status | Current Approach |
|--------------------|--------|------------------|
| [Pattern from architecture.md] | Aligned / Divergent | [What's actually used] |

### Best Practice Compliance
- **[Practice 1]** — Pass / Fail — [Evidence]
- **[Practice 2]** — Pass / Fail — [Evidence]

### Gotcha Check
- **[Gotcha 1]** — Clear / At Risk — [Why]
- **[Gotcha 2]** — Clear / At Risk — [Why]

### Testing Coverage
| What Should Be Tested | Status |
|-----------------------|--------|
| [Test from testing.md] | Covered / Missing |

### Improvement Opportunities
1. **[Priority 1]** — [What to improve] → [Link to codex]
2. **[Priority 2]** — [What to improve] → [Link to codex]
```

### Phase 5: Follow-Up

Ask the user how to proceed:

```
What would you like to do with these findings?
1. Deep dive into a specific finding
2. Start implementing an improvement
3. Save as a report
4. Audit against a different experience
5. Run a related checklist (e.g., accessibility-audit)
```

## Error Handling

### Experience Not Found
- List all available experiences
- Suggest the closest match based on the user's query

### Frontend-Only Scope
Some experience guidelines touch backend concerns (e.g., API pagination for tables):
- Note these as "Backend concern — verify with backend team"
- Focus the audit on frontend implementation

### Component Not Found
If the specified component path doesn't exist:
- Search for similar component names
- Present matches for the user to select

## Related Resources

- [Experiences Index](../../experiences/README.md) — All available experiences
- [Architecture Review Skill](../architecture-review/SKILL.md) — Architecture-focused review (complementary)
- [Checklist Runner Skill](../checklist-runner/SKILL.md) — Run a formal checklist
- [Accessibility Audit Checklist](../../checklists/accessibility-audit.md) — WCAG compliance check
