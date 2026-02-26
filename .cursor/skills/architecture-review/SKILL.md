---
name: architecture-review
description: Compare codebase architecture against Engineering Codex recommendations and identify alignment gaps.
complexity: high
prompt-version: "1.0"
---

# Architecture Review Skill

Compares your current project's implementation against the Engineering Codex recommendations. Identifies alignment, gaps, and actionable improvements across relevant facets.

## When to Use

- Periodic health check on a project's architecture
- Before a major refactoring effort to prioritize what to address
- Onboarding to an existing project to understand its current state
- Preparing for a technical review or architecture discussion

## When NOT to Use

- **Running a specific checklist** (security, accessibility) — use [Checklist Runner](../checklist-runner/SKILL.md)
- **Reviewing a specific PR or diff** — use the Code Review skill in workspace-standards
- **Scoring with numeric metrics** — use the Score skill in workspace-standards
- **Learning about a facet** before reviewing — use [Facet Deep Dive](../facet-deep-dive/SKILL.md)

## Invocation

```
Review architecture of finance-mfe
```

Or with specific facets:
```
Review authentication and state-management in currency-manager
```

Or for a broad review:
```
Full architecture review of order-handler
```

## Workflow

### Phase 1: Scope the Review

1. Identify the target project/repository from the user's request
2. Ask which facets to review using AskQuestion:

```
Which areas would you like to review?
1. All applicable facets (comprehensive review)
2. Specific facets (select from list)
3. Auto-detect (I'll scan the codebase and recommend relevant facets)
```

If auto-detect is selected:
- Explore the project structure to identify which facets are relevant
- For example: if the project has authentication middleware, include authentication; if it has i18n files, include internationalization
- Present the detected facets for confirmation

### Phase 2: Codebase Exploration

For each selected facet:

1. Read the facet's `best-practices.md` and `architecture.md` from the codex
2. Explore the target project codebase:
   - Search for relevant patterns, files, and configurations
   - Identify the current architectural approach
   - Check for testing patterns related to this facet
3. Note the stack context from `@engineering-codex/stack-context.md` to apply appropriate framework-specific guidance

### Phase 3: Gap Analysis

For each facet, produce a finding:

```markdown
### [Facet Name]

**Current State:** [What the project currently does]
**Codex Recommendation:** [What the codex recommends]
**Alignment:** Aligned / Partially Aligned / Divergent / Not Implemented

**Gaps:**
- [Specific gap 1]
- [Specific gap 2]

**Recommended Actions:**
- [ ] [Actionable improvement 1]
- [ ] [Actionable improvement 2]

**Priority:** High / Medium / Low
**Effort:** Small / Medium / Large
```

### Phase 4: Summary Report

Present an overall summary:

```markdown
## Architecture Review: [Project Name]

**Date:** [Today's date]
**Facets Reviewed:** [Count]

### Overview
| Facet | Alignment | Priority | Effort |
|-------|-----------|----------|--------|
| [Name] | [Status] | [Priority] | [Effort] |

### Key Findings
1. [Most important finding]
2. [Second most important finding]
3. [Third most important finding]

### Recommended Next Steps
1. [Highest priority action]
2. [Second priority action]
3. [Third priority action]
```

### Phase 5: Documentation and Follow-Up

Ask the user how to proceed:

```
What would you like to do with these findings?
1. Create Jira tickets for the recommended actions
2. Save as a markdown report
3. Deep dive into a specific finding
4. Start implementing a specific recommendation
```

- If Jira → use Atlassian MCP to create tickets (if available)
- If save → generate a markdown file in the project's docs directory
- If deep dive → invoke `facet-deep-dive` for the selected facet
- If implement → begin working on the recommendation

## Verification

- **Phase 1**: Confirm the target project exists in the workspace and at least one facet is selected for review.
- **Phase 2**: For each facet, confirm the codex file was loaded. If a facet file is still a template, skip and note "content not yet available."
- **Phase 3**: Confirm each facet has an alignment classification and at least one gap or explicit "no gaps found."
- **Phase 4**: Confirm the summary table includes all reviewed facets — no facets silently dropped.

## Worked Example

**Input:** `Full architecture review of order-handler`

**Key steps:**
1. Auto-detected relevant facets: api-design, error-handling, testing, observability (Kotlin Spring Boot project)
2. For each facet, read codex `best-practices.md` and `architecture.md`, then explored order-handler codebase
3. Found: API design aligned (RESTful, proper HTTP status codes), error handling partially aligned (global handler exists but missing structured error body), testing divergent (no integration tests)

**Output excerpt:**
```markdown
## Architecture Review: order-handler

### Overview
| Facet | Alignment | Priority | Effort |
|-------|-----------|----------|--------|
| API Design | Aligned | — | — |
| Error Handling | Partial | Medium | Small |
| Testing | Divergent | High | Medium |
| Observability | Aligned | — | — |

### Key Findings
1. No integration tests — only unit tests exist (Testing: Divergent)
2. Error responses use plain strings instead of structured error body (Error Handling: Partial)
```

## Error Handling

### Project Not Found

If the target project isn't in the current workspace:
- List available workspace repositories
- Ask the user to specify the correct project

### Facet Content Not Written

If a facet's content is still templated:
- Skip that facet in the review
- Note it as "Unable to review -- codex content not yet available"

## Related Resources

- [Facet Deep Dive Skill](../facet-deep-dive/SKILL.md) -- Explore a specific facet in depth
- [Evaluate Options Skill](../evaluate-options/SKILL.md) -- Make decisions for identified gaps
- [Facets Index](../../../facets/README.md) -- All available engineering facets
