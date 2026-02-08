# Compare Options Command

Quick, non-interactive side-by-side comparison of options for any Engineering Codex facet or experience.

## Usage

```
Compare options for api-design
```

Or with specific options:
```
Compare REST vs GraphQL vs gRPC
```

## Behavior

1. Read the `options.md` from the specified facet or experience
2. If `recommendation_type` is `best-practice`:
   - Present the recommended approach
   - List the escape hatch alternatives in a comparison format
3. If `recommendation_type` is `decision-matrix`:
   - Present all options in a side-by-side summary table
   - Include strengths, weaknesses, and "best for" for each
   - Show the synergies section
   - Show the evolution triggers section

## Output Format

```markdown
## Options Comparison: [Facet Name]

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| Description | ... | ... | ... |
| Strengths | ... | ... | ... |
| Weaknesses | ... | ... | ... |
| Best For | ... | ... | ... |
| Avoid When | ... | ... | ... |

### Synergies
- [Cross-facet interactions]

### Evolution Triggers
- [When to reconsider]

> For interactive evaluation with weighted scoring, use the `evaluate-options` skill.
```

## Difference from evaluate-options Skill

This command is a **quick reference**. It does not:
- Ask for criteria weighting
- Check cross-facet decisions you've already made
- Score options
- Help document the decision

Use the `evaluate-options` skill when you need to make and document a real decision. Use this command when you just want a quick refresher on what the options are.
