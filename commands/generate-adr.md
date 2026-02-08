# Generate ADR Command

Generates an Architecture Decision Record from a codex-informed decision.

## Usage

```
Generate ADR for our authentication decision
```

Or with specific details:
```
Generate ADR: we chose JWT-based authentication for the finance-mfe project
```

## Behavior

1. Gather decision context from the user:
   - Which facet/experience was consulted
   - Which option was chosen
   - Key reasons for the choice
   - What alternatives were considered
   - Target project/repository

2. Read the ADR template from `@engineering-codex/decision-frameworks/adr-template.md`

3. Generate the ADR with:
   - Auto-populated codex reference (facet name and link)
   - Decision context from the user
   - Options considered (pulled from the facet's `options.md` if available)
   - Consequences and trade-offs
   - Evolution triggers (from the facet's `options.md`)

4. Present the ADR as formatted markdown

5. Ask where to save:
   ```
   Where should this ADR be saved?
   1. [project]/docs/adr/ (standard location)
   2. Copy to clipboard (I'll place it myself)
   3. Post as a Jira comment on a ticket
   ```

## Output Format

Uses the template from [adr-template.md](../decision-frameworks/adr-template.md) with all fields populated.

## Related Resources

- [ADR Template](../decision-frameworks/adr-template.md) -- The template used
- [Documenting Decisions](../decision-frameworks/documenting-decisions.md) -- When to use ADR vs decision log
- [Evaluate Options Skill](../skills/evaluate-options/SKILL.md) -- Make the decision first
