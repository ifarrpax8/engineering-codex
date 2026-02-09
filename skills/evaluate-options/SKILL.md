---
name: Evaluate Options
description: Interactive walkthrough of a facet's decision matrix, scoring options against weighted criteria to arrive at a documented recommendation.
---

# Evaluate Options Skill

Interactive decision-making walkthrough for any Engineering Codex facet or experience. Guides you through evaluating options, scoring them against criteria, accounting for cross-facet synergies, and documenting the decision.

## When to Use

- Starting a new project and need to make foundational decisions
- Adding a major feature that requires an architectural choice
- Revisiting a previous decision due to an evolution trigger
- Comparing approaches for a specific concern (e.g., REST vs GraphQL)

## Invocation

```
Evaluate options for authentication
```

Or with context:
```
Evaluate options for state-management, we've already chosen Vue and MFE architecture
```

## Workflow

### Phase 1: Load the Facet

1. Identify the facet or experience from the user's request
2. Read the `options.md` file from `@engineering-codex/facets/<name>/options.md` or `@engineering-codex/experiences/<name>/options.md`
3. Check the `recommendation_type` in the frontmatter:
   - If `best-practice` → proceed to Phase 2a
   - If `decision-matrix` → proceed to Phase 2b

### Phase 2a: Best Practice Mode

When the `options.md` declares `recommendation_type: best-practice`:

1. Present the recommended approach clearly
2. List the "consider instead if..." escape hatches
3. Ask the user if any escape hatch conditions apply to their situation
4. If none apply → recommend the best practice and proceed to Phase 4
5. If an escape hatch applies → discuss the alternative and its trade-offs, then proceed to Phase 4

### Phase 2b: Decision Matrix Mode

When the `options.md` declares `recommendation_type: decision-matrix`:

1. Present all available options with a brief summary of each
2. Load evaluation criteria from `@engineering-codex/decision-frameworks/criteria/`
3. Ask the user to identify which criteria matter most for their context using the AskQuestion tool:

```
Which criteria are most important for this decision?
- Scalability
- Maintainability
- Developer Experience
- Cost
- Time to Market
```

4. Allow multiple selections and ask for relative weighting (high/medium/low) for each selected criterion

### Phase 3: Cross-Facet Synergies

1. Read the `## Synergies` section from the facet's `options.md`
2. Ask: "Have you already made decisions in related facets?" using AskQuestion
3. Present the relevant synergies based on their answers
4. Adjust scoring guidance: if a synergy strongly favors one option, note this as a contextual bonus

### Phase 3b: Pax8 Standards Check (Optional)

If the user is working on a Pax8 project:

1. Ask: "Is this a Pax8 project? Would you like to check Pax8 standards?" using AskQuestion
2. If yes, read `@engineering-codex/pax8-context/standards-map.md` and filter for the current facet
3. Check `@engineering-codex/pax8-context/deprecated.md` for any deprecated options
4. Present findings:
   - If Pax8 has a **Standard** for this facet: "Pax8 has already decided: [summary]. This is an organisational standard — adopt unless you have a strong, documented reason to diverge."
   - If Pax8 has **Guidance**: "Pax8 recommends: [summary]. This is guidance, not a mandate — weigh it alongside other criteria."
   - If an option under evaluation is **deprecated** at Pax8: "Note: [technology] is deprecated at Pax8 (ADR-XXXXX). Avoid for Pax8 projects."
5. If Pax8 has already decided, ask whether to accept the standard or evaluate alternatives anyway
6. If accepted, skip to Phase 5 (Document the Decision) with the Pax8 standard as the chosen option

This phase is skipped entirely for non-Pax8 projects.

### Phase 4: Scoring and Recommendation

For decision-matrix mode:
1. Score each option against the weighted criteria
2. Factor in synergy adjustments
3. Present a summary table with scores
4. Provide a clear recommendation with rationale

For best-practice mode:
1. Confirm the recommendation (either the best practice or the escape hatch alternative)
2. Note any caveats

### Phase 5: Document the Decision

Ask the user how they'd like to document this decision:

```
How would you like to document this decision?
1. Generate a full ADR (for significant architectural decisions)
2. Add to decision log (lightweight record)
3. Skip documentation for now
```

- If ADR → invoke the `generate-adr` command with the decision context
- If decision log → present a formatted row for the user's project decision log using the template from `@engineering-codex/decision-frameworks/decision-log-template.md`
- If skip → end the workflow

### Phase 6: Evolution Triggers

1. Read the `## Evolution Triggers` section from the facet's `options.md`
2. Present the triggers relevant to the chosen option: "Revisit this decision when..."
3. Suggest the user note these triggers in their ADR or decision log

## Error Handling

### Facet Not Found

If the requested facet or experience doesn't exist:
- List available facets and experiences
- Ask the user to select one or clarify their request

### Options.md Not Yet Written

If the `options.md` is still a template without real content:
- Inform the user that this facet hasn't been populated yet
- Offer to help research the topic and draft content
- Suggest using the `facet-deep-dive` skill to explore the topic first

## Related Resources

- [Decision Frameworks](../../decision-frameworks/) -- Evaluation criteria definitions
- [Documenting Decisions](../../decision-frameworks/documenting-decisions.md) -- When to use ADR vs decision log
- [Compare Options Command](../../commands/compare-options.md) -- Quick non-interactive comparison
- [Generate ADR Command](../../commands/generate-adr.md) -- Create an ADR from a decision
