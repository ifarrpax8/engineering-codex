# ADR Template

Use this template when creating an Architecture Decision Record. The `generate-adr` command will populate this automatically.

---

```markdown
# ADR-[NUMBER]: [Title]

**Date:** [YYYY-MM-DD]
**Status:** Accepted | Superseded by ADR-[NUMBER] | Deprecated
**Deciders:** [Names or roles involved in the decision]

## Codex Reference

**Facet:** [engineering-codex/facets/<name>/options.md](link)
**Recommendation Type:** Best Practice | Decision Matrix

## Context

[What is the issue that we're seeing that is motivating this decision or change? What is the problem we're trying to solve?]

## Decision

[What is the change that we're proposing and/or doing?]

## Options Considered

### Option 1: [Name]
- **Description:** [Brief description]
- **Pros:** [Key advantages]
- **Cons:** [Key disadvantages]

### Option 2: [Name] (Chosen)
- **Description:** [Brief description]
- **Pros:** [Key advantages]
- **Cons:** [Key disadvantages]

### Option 3: [Name]
- **Description:** [Brief description]
- **Pros:** [Key advantages]
- **Cons:** [Key disadvantages]

## Decision Rationale

[Why was this option chosen? What criteria were weighted most heavily? Reference the codex evaluation criteria if applicable.]

### Criteria Weighting
| Criteria | Weight | Chosen Option Score |
|----------|--------|---------------------|
| [Criteria 1] | High | [Score/Assessment] |
| [Criteria 2] | Medium | [Score/Assessment] |

### Synergies
[How does this decision interact with other decisions? Reference related ADRs if applicable.]

## Consequences

### Positive
- [Positive consequence 1]
- [Positive consequence 2]

### Negative
- [Negative consequence 1 and mitigation]
- [Negative consequence 2 and mitigation]

### Neutral
- [Neutral observation]

## Evolution Triggers

Revisit this decision when:
- [Trigger 1 from the codex facet's options.md]
- [Trigger 2]
- [Project-specific trigger]

## Related Decisions

- [ADR-XXX: Related decision title](link)
- [ADR-YYY: Another related decision](link)
```
