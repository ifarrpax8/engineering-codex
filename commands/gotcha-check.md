# Gotcha Check Command

Instantly surfaces the common pitfalls and traps for any Engineering Codex facet or experience.

## Usage

```
What are the gotchas for event-driven architecture?
```

Or more directly:
```
Gotcha check for state-management
```

Or for an experience:
```
Gotchas for forms-and-data-entry
```

## Behavior

1. Identify the facet or experience from the user's request
2. Read the `gotchas.md` file from `@engineering-codex/facets/<name>/gotchas.md` or `@engineering-codex/experiences/<name>/gotchas.md`
3. Present the content formatted for quick scanning:
   - Group gotchas by category (as they appear in the file)
   - Highlight the most critical ones first
   - Include the "why it matters" and "how to avoid it" for each
4. If the user mentions a specific area of concern (e.g., "gotchas for event-driven architecture around idempotency"), filter and highlight the most relevant gotchas

## Output Format

```markdown
## Gotchas: [Facet/Experience Name]

### [Category 1]
⚠️ **[Gotcha title]** — [Brief description of the trap]
→ Avoid by: [How to avoid it]

⚠️ **[Gotcha title]** — [Brief description]
→ Avoid by: [How to avoid it]

### [Category 2]
...

> For a full deep dive into this topic, use: `Deep dive into [facet-name]`
> To check your project against these gotchas, use: `Audit [project] against [experience]` or `Run checklist against [project]`
```

## When This Is Better Than Reading the File Directly

- Faster than navigating to the file — just ask
- Can filter by a specific concern area
- Includes actionable "avoid by" summaries
- Points to next steps (deep dive, audit, checklist)

## Related Resources

- [Facets Index](../facets/README.md) — All available engineering facets
- [Experiences Index](../experiences/README.md) — All available user experiences
- [Facet Deep Dive Skill](../skills/facet-deep-dive/SKILL.md) — Explore the full facet
- [Experience Audit Skill](../skills/experience-audit/SKILL.md) — Audit your code against an experience
