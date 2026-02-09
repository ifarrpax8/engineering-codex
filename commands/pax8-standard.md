# Pax8 Standard Command

Surfaces Pax8-specific technology decisions and standards for any Engineering Codex facet, showing where the organisation has already decided.

## Usage

```
What's the Pax8 standard for observability?
```

Or:
```
Pax8 standards for api-design
```

Or to check deprecated tech:
```
Is NewRelic still used at Pax8?
```

## Behavior

1. Identify the facet from the user's request
2. Read `@engineering-codex/pax8-context/standards-map.md` and filter for the matching facet
3. Read `@engineering-codex/pax8-context/deprecated.md` for any deprecated technologies relevant to the facet
4. Present:
   - Active standards (type: Standard) as "Pax8 has decided:"
   - Guidance items (type: Guidance) as "Pax8 recommends:"
   - Deprecated technologies as "Pax8 is moving away from:"
   - Link to the source ADR for full context (if ADR repo is available)

## Output Format

```markdown
## Pax8 Standards: [Facet Name]

### Decided (Standard)
- **[ADR title]** — [Summary]
  Source: [ADR link]

### Recommended (Guidance)
- **[ADR title]** — [Summary]
  Source: [ADR link]

### Deprecated
- **[Technology]** — [Was used for]. Replace with: [Replacement]

> These are Pax8 organisational standards. For industry best practices, see: `Deep dive into [facet]`
> For non-Pax8 projects, these standards do not apply.
```

## When This Applies

This command is only relevant for Pax8 projects. For non-Pax8 projects, the core codex content applies without this overlay.

## Related Resources

- [Pax8 Standards Map](../pax8-context/standards-map.md) — Full mapping of ADRs to facets
- [Deprecated Technologies](../pax8-context/deprecated.md) — Technologies being phased out
- [Evaluate Options Skill](../skills/evaluate-options/SKILL.md) — Interactive decision-making (includes optional Pax8 context)
