---
name: Generate Opportunity Brief
description: Draft a Pax8 Opportunity Brief for a feature idea, informed by Engineering Codex content and the standard template.
---

# Generate Opportunity Brief Skill

Draft a Pax8 Opportunity Brief for a feature idea, enriched with Engineering Codex insights about user flows, risks, and best practices.

## When to Use

- You have a feature idea and need to draft an Opportunity Brief for Pax8's Engineering Operations process
- You want to ensure your brief considers user experience patterns, technical risks, and architectural implications
- You need to align your feature proposal with Engineering Codex best practices

## Invocation

```
Generate an opportunity brief for [feature idea]
```

Or with context:
```
Generate an opportunity brief for a new payment method feature, targeting enterprise customers
```

## Workflow

### Phase 1: Gather Feature Context

1. Ask the user for essential information using AskQuestion:
   - **Feature idea**: What is the core feature or capability you're proposing?
   - **Target users**: Who will use this feature? (e.g., end users, internal teams, partners)
   - **Strategic alignment**: How does this align with Pax8's strategic goals? (prompt for business context)
   - **Known constraints**: Are there any technical, timeline, or resource constraints?
   - **Executive Sponsor**: Who is the executive sponsor for this opportunity?
   - **Idea Owner**: Who owns this idea?
   - **Requesting Department**: Which department is requesting this?

2. Capture the responses for use in the brief

### Phase 2: Identify Relevant Codex Content

1. Map the feature to relevant Engineering Codex facets and experiences:
   - Use the feature description to identify facets (e.g., authentication, api-design, state-management)
   - Identify user experiences that apply (e.g., forms-and-data-entry, search-and-filtering)
   
2. Read relevant `product.md` files from facets and experiences:
   - Extract user flow patterns
   - Identify KPIs and success metrics
   - Note product considerations

3. Read relevant `gotchas.md` files:
   - Identify technical risks
   - Note common pitfalls to address in the brief

4. Read relevant `architecture.md` files if architectural implications are significant:
   - Note system design considerations
   - Identify integration points

### Phase 3: Draft the Opportunity Brief

Fill in the Pax8 Opportunity Brief template structure:

#### Template Structure

```markdown
# Opportunity Brief: [Feature Name]

## Metadata
- **Executive Sponsor**: [Name]
- **Idea Owner**: [Name]
- **Requesting Department**: [Department]
- **Date**: [Current Date]
- **Status**: Draft

## Problem Alignment

[Describe the problem this feature addresses, informed by user input and codex product perspectives]

### User Impact
[Who is affected and how, based on target users identified]

### Business Impact
[Strategic alignment and business value]

## Hypothesis

**If** we [build/implement/change] [feature/component/capability],
**then** [expected outcome/behavior],
**because** [rationale/assumption].

[Informed by codex product.md user flow patterns and best practices]

## Projected ROI

### Benefits
- [Quantified benefit 1] — [Source/assumption]
- [Quantified benefit 2] — [Source/assumption]

### Costs
- [Estimated cost 1] — [Source/assumption]
- [Estimated cost 2] — [Source/assumption]

### ROI Calculation
[If user provides estimates, structure them here]

## Technical Considerations

### Relevant Facets
- [Facet 1]: [Brief note on relevance]
- [Facet 2]: [Brief note on relevance]

### Key Risks (from Codex Gotchas)
- [Risk 1 from gotchas.md] — [Mitigation approach]
- [Risk 2 from gotchas.md] — [Mitigation approach]

### Architecture Implications
[If applicable, note significant architectural considerations from codex]

## Next Steps

1. [Next step 1]
2. [Next step 2]
```

**Note**: The full template is available at: https://pax8.atlassian.net/wiki/spaces/EO/pages/2446131237

### Phase 4: Review and Refine

1. Present the draft Opportunity Brief to the user
2. Ask for feedback on:
   - Problem alignment accuracy
   - Hypothesis clarity and testability
   - ROI estimates (if provided)
   - Missing considerations
3. Iterate based on feedback
4. Ensure the brief is complete and ready for submission

### Phase 5: Output

Ask the user how they'd like to save the Opportunity Brief:

```
How would you like to save this Opportunity Brief?
1. Save as markdown file
2. Copy to clipboard
3. Create Confluence page (if Confluence MCP available)
4. Display for manual copy
```

- If markdown → save to a file (suggest filename: `opportunity-brief-[feature-name].md`)
- If clipboard → format and copy
- If Confluence → create page in the Engineering Operations space
- If display → present formatted markdown

## Error Handling

### Missing Information

If essential information is missing (e.g., executive sponsor, target users):
- Prompt the user to provide it
- Offer to proceed with placeholders marked as "[TODO: fill in]"

### No Relevant Codex Content

If the feature doesn't map to existing facets or experiences:
- Note this in the brief
- Suggest relevant facets that might be added in the future
- Proceed with the brief using general best practices

## Related Resources

- [Pax8 Opportunity Brief Template](https://pax8.atlassian.net/wiki/spaces/EO/pages/2446131237) — Official template
- [Engineering Codex Facets](../../facets/README.md) — Available technical facets
- [Engineering Codex Experiences](../../experiences/README.md) — Available user experiences
- [Generate PRD Skill](../generate-prd/SKILL.md) — Next step after approval
