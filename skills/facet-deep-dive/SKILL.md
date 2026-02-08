---
name: Facet Deep Dive
description: Interactive exploration of any Engineering Codex facet or experience, pulling in relevant context from your codebase.
---

# Facet Deep Dive Skill

Interactive exploration of any Engineering Codex facet or experience. Walks through each perspective (product, architecture, testing, best practices, options) and connects the content to your current codebase.

## When to Use

- Onboarding to a new topic or concern area
- Preparing for a technical discussion or design review
- Wanting to understand a topic from all angles before making decisions
- Learning how a facet applies to your specific project

## Invocation

```
Deep dive into authentication
```

Or with a specific focus:
```
Deep dive into the testing perspective of event-driven-architecture
```

Or targeting your project:
```
Deep dive into state-management for the finance-mfe project
```

## Workflow

### Phase 1: Identify and Load

1. Parse the user's request to identify:
   - The facet or experience name
   - Any specific perspective they want to focus on (product, architecture, testing, best-practices, options)
   - Any target project or repository
2. Read the facet's `README.md` from `@engineering-codex/facets/<name>/README.md` or `@engineering-codex/experiences/<name>/README.md`
3. Present a brief overview of the facet and ask how deep they'd like to go:

```
How would you like to explore this facet?
1. Full walkthrough (all 5 perspectives)
2. Specific perspective (product, architecture, testing, best-practices, or options)
3. Compare against my codebase
```

### Phase 2: Guided Exploration

#### For Full Walkthrough

Walk through each perspective in order:

1. **Product** -- Read and present `product.md`. Ask: "Any questions about the product perspective before we move on?"
2. **Architecture** -- Read and present `architecture.md`. If a target project was specified, search the project codebase for relevant patterns and compare.
3. **Testing** -- Read and present `testing.md`. If a target project was specified, check what testing patterns are currently in use.
4. **Best Practices** -- Read and present `best-practices.md`. Highlight any stack-specific callouts relevant to the user's project (reference `@engineering-codex/stack-context.md`).
5. **Options** -- Read and present `options.md`. Offer to transition to the `evaluate-options` skill if the user needs to make a decision.

#### For Specific Perspective

Read and present only the requested perspective file. Offer to explore related perspectives if relevant connections emerge.

#### For Codebase Comparison

1. Identify the target project/repository
2. Read the facet's `best-practices.md` and `architecture.md`
3. Explore the project codebase to find relevant patterns:
   - Use Grep/Glob to search for related code patterns
   - Identify which architectural approach is currently in use
4. Present a comparison: "Your project currently does X. The codex recommends Y. Here are the gaps..."

### Phase 3: Cross-References

After exploring the requested content:
1. Identify related facets or experiences mentioned in the content
2. Present: "This topic connects to these other areas: [list]. Would you like to explore any of them?"
3. If synergies exist in `options.md`, highlight how decisions in this facet affect other facets

### Phase 4: Summary and Next Steps

Present a summary of key takeaways and suggest next steps:

- If decisions need to be made → suggest `evaluate-options` skill
- If implementation gaps were found → suggest creating tickets or tasks
- If the user wants to review their architecture → suggest `architecture-review` skill
- If content is missing or outdated → suggest contributing updates

## Error Handling

### Facet Not Found

If the requested facet doesn't exist:
- List available facets and experiences from `@engineering-codex/facets/README.md` and `@engineering-codex/experiences/README.md`
- Ask the user to select one

### Content Not Yet Written

If perspective files are still templates:
- Inform the user
- Offer to research the topic using web search and codebase exploration
- Suggest contributing the findings back to the codex

## Related Resources

- [Evaluate Options Skill](../evaluate-options/SKILL.md) -- Make decisions after exploring
- [Architecture Review Skill](../architecture-review/SKILL.md) -- Compare implementation against recommendations
- [Facets Index](../../facets/README.md) -- All available engineering facets
- [Experiences Index](../../experiences/README.md) -- All available UX experiences
