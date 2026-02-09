---
name: Generate PRD
description: Draft a Pax8 Product Requirements Document from an approved Opportunity Brief, enriched with Engineering Codex insights.
---

# Generate PRD Skill

Draft a Pax8 Product Requirements Document from an approved Opportunity Brief, enriched with Engineering Codex technical insights, standards, and best practices.

## When to Use

- You have an approved Opportunity Brief and need to create a PRD
- You want to ensure your PRD considers Pax8 standards, technical risks, and architectural decisions
- You need to map the feature to Engineering Codex facets and identify required decisions

## Invocation

```
Generate a PRD from this opportunity brief: [paste or reference Opp Brief]
```

Or:
```
Generate PRD for [feature name], approved Opp Brief: [link or content]
```

## Workflow

### Phase 1: Load Opportunity Brief

1. Ask the user to provide their approved Opportunity Brief:
   - Accept markdown content directly
   - Accept a file path reference
   - Accept a Confluence page link (if Confluence MCP available)

2. Extract key information:
   - Problem statement
   - Hypothesis
   - ROI projections
   - Target users
   - Strategic alignment

3. Confirm the brief is approved (if not explicitly stated, ask)

### Phase 2: Identify Technical Scope

1. Map the feature to Engineering Codex facets and experiences:
   - Use the problem statement and hypothesis to identify relevant facets
   - Use `what-should-i-read` logic to determine which content applies
   - Consider both technical facets (e.g., authentication, api-design) and user experiences (e.g., forms-and-data-entry)

2. Read relevant facet and experience files:
   - `product.md` — for user flows, KPIs, success metrics
   - `gotchas.md` — for risks and pitfalls
   - `architecture.md` — for system design considerations
   - `options.md` — for decision points that need to be made

3. Identify cross-facet dependencies:
   - Note which facets interact (e.g., authentication + api-design)
   - Read synergy sections from `options.md` files

### Phase 3: Check Pax8 Standards

1. Read `@engineering-codex/pax8-context/standards-map.md`
2. Filter for facets relevant to this feature
3. Identify:
   - **Standards** (type: Standard) — decisions already made
   - **Guidance** (type: Guidance) — recommendations to consider
4. Read `@engineering-codex/pax8-context/deprecated.md` for deprecated technologies
5. Pre-fill technology decisions in the PRD where Pax8 has already decided

### Phase 4: Draft PRD Sections

Fill in the Pax8 PRD template structure:

#### Template Structure

```markdown
# Product Requirements Document: [Feature Name]

## Metadata
- **Opportunity Brief**: [Link to Opp Brief]
- **Product Owner**: [Name]
- **Engineering Lead**: [Name]
- **Date**: [Current Date]
- **Status**: Draft
- **Version**: 1.0

## Problem Alignment

[Carried from Opportunity Brief, with any refinements]

### User Problem
[Restate the user problem from Opp Brief]

### Business Problem
[Restate the business problem from Opp Brief]

## Expected Outcomes

### Must Have
[Core requirements that must be delivered, informed by codex best practices]

### Nice to Have
[Enhancements that improve the experience but aren't critical]

### Out of Scope
[Explicitly excluded items, informed by codex scope guidance]

## Success Metrics

[Informed by codex product.md KPI guidance for relevant facets/experiences]

### Primary Metrics
- [Metric 1]: [Target value] — [Measurement method]
- [Metric 2]: [Target value] — [Measurement method]

### Secondary Metrics
- [Metric 3]: [Target value]
- [Metric 4]: [Target value]

## User Stories

[If applicable, structured user stories informed by codex product.md user flows]

## Technical Requirements

### Architecture Considerations
[Informed by codex architecture.md files for relevant facets]

### Integration Points
[Systems/services that need to integrate, from codex architecture cross-references]

### Performance Requirements
[If applicable, informed by codex performance facet]

### Security Requirements
[If applicable, informed by codex security facet]

## Risks

[Informed by gotchas.md for each relevant facet + experience]

### Technical Risks
- **[Risk from gotchas.md]** — [Likelihood] — [Impact] — [Mitigation strategy]

### Product Risks
- **[Risk]** — [Likelihood] — [Impact] — [Mitigation strategy]

### Dependencies
[Informed by codex architecture cross-references]

- **[Dependency]** — [Description] — [Status/Blockers]

## Significant Decisions

[List decisions that need to be made, link to codex options.md for each]

### Decisions Needed
- **[Decision 1]** — See: `@engineering-codex/facets/[facet]/options.md`
- **[Decision 2]** — See: `@engineering-codex/facets/[facet]/options.md`

### Decisions Already Made (Pax8 Standards)
- **[Decision]** — [Pax8 Standard: ADR-XXXXX] — [Summary]

### Recommended Approach
[For each decision, provide recommendation based on Pax8 standards or codex best practices]

## Design & Technical Artifacts

[Suggest which artifacts are needed based on scope, informed by codex best practices]

### Required Artifacts
- [ ] [Artifact 1] — [Rationale]
- [ ] [Artifact 2] — [Rationale]

### Recommended Artifacts
- [ ] [Artifact 3] — [Rationale]

## Timeline & Milestones

[If user provides timeline information, structure it here]

## Open Questions

[List any questions that need to be answered before development can begin]

## References

- [Opportunity Brief Link]
- [Relevant ADRs]
- [Engineering Codex Facets Used]: [List facets/experiences referenced]
```

**Note**: The full template is available at: https://pax8.atlassian.net/wiki/spaces/EO/pages/2446327849

### Phase 5: Review and Refine

1. Present the draft PRD to the user
2. Ask for feedback on:
   - Completeness of requirements
   - Accuracy of technical scope
   - Clarity of success metrics
   - Adequacy of risk identification
   - Missing decisions or artifacts
3. Iterate based on feedback
4. Ensure all sections are complete

### Phase 6: Output

Ask the user how they'd like to save the PRD:

```
How would you like to save this PRD?
1. Save as markdown file
2. Copy to clipboard
3. Create Confluence page (if Confluence MCP available)
4. Display for manual copy
```

- If markdown → save to a file (suggest filename: `prd-[feature-name].md`)
- If clipboard → format and copy
- If Confluence → create page in the Engineering Operations space
- If display → present formatted markdown

## Error Handling

### Opportunity Brief Not Found

If the Opp Brief cannot be loaded:
- Ask the user to provide it again or paste the content
- Offer to proceed with manual input of key information

### No Relevant Codex Content

If the feature doesn't map to existing facets:
- Note this in the PRD
- Use general best practices
- Suggest areas where codex content might be expanded

### Missing Pax8 Standards

If no Pax8 standards exist for relevant facets:
- Note that decisions need to be made
- Suggest using the Evaluate Options skill for each decision
- Link to relevant codex options.md files

## Related Resources

- [Pax8 PRD Template](https://pax8.atlassian.net/wiki/spaces/EO/pages/2446327849) — Official template
- [Generate Opportunity Brief Skill](../generate-opportunity-brief/SKILL.md) — Previous step
- [Evaluate Options Skill](../evaluate-options/SKILL.md) — For making technical decisions
- [Pax8 Standards Command](../../commands/pax8-standard.md) — Check Pax8 standards
- [Engineering Codex Facets](../../facets/README.md) — Available technical facets
