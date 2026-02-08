# Contributing to the Engineering Codex

This is a living document. Contributions are welcome and encouraged as best practices evolve and new patterns emerge.

## Content Principles

1. **Opinionated but fair** -- Present recommendations clearly, but acknowledge alternatives honestly
2. **Language-agnostic first** -- Lead with principles, add stack-specific callouts where they materially change the recommendation (see [stack-context.md](stack-context.md))
3. **Concise and scannable** -- Use headers, bullet points, and tables. Avoid walls of text
4. **Link, don't duplicate** -- Cross-reference other facets and experiences rather than repeating content
5. **Evergreen over trendy** -- Prefer established patterns. Note emerging approaches but don't over-index on hype

## Adding a New Facet or Experience

Use the `create-facet` skill to scaffold the directory structure automatically:

```
Create a new facet called "caching"
```

The skill will:
1. Create the directory with all 6 template files
2. Add an entry to the CHANGELOG
3. Update the relevant index (facets/README.md or experiences/README.md)

### Manual Creation

If creating manually, every facet or experience must include these 6 files:

```
facets/<name>/
├── README.md           # Overview, navigation, quick reference
├── product.md          # Business value, user flows, personas
├── architecture.md     # Patterns, diagrams, trade-offs
├── testing.md          # Test strategies, tooling categories
├── best-practices.md   # Language-agnostic principles
└── options.md          # Decision matrix or best practice
```

### README.md Frontmatter

Every facet/experience README must include:

```yaml
---
title: <Display Name>
type: facet  # or "experience"
last_updated: YYYY-MM-DD
---
```

## Updating Existing Content

1. Update the content in the relevant file
2. Update the `last_updated` field in the facet/experience README.md
3. Add an entry to [CHANGELOG.md](CHANGELOG.md) under the appropriate section

## Options.md Structure

Each `options.md` must declare its recommendation type in frontmatter:

```yaml
---
recommendation_type: best-practice  # or "decision-matrix"
---
```

- **best-practice** -- Lead with the recommended approach. List alternatives as "consider instead if..." escape hatches
- **decision-matrix** -- Present all options with criteria scoring. No single option is universally better

Both modes must include:
- A `## Synergies` section mapping interactions with other facets
- An `## Evolution Triggers` section describing when to reconsider the decision

## Cross-Referencing Convention

When referencing another facet or experience, use relative markdown links:

```markdown
See [Authentication > Architecture](../authentication/architecture.md) for session management patterns.
```

When referencing from a checklist or top-level file:

```markdown
See [Authentication > Architecture](facets/authentication/architecture.md) for details.
```

## Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/) conventions:

- **Added** -- New facets, experiences, checklists, or major new sections
- **Changed** -- Updates to existing content, revised recommendations
- **Deprecated** -- Approaches that are no longer recommended (but still documented)
- **Removed** -- Content that has been deleted

## Review Process

Major changes (new facets, changed recommendations) should be reviewed by at least one other team member via pull request. Minor updates (typo fixes, clarifications, link updates) can be merged directly.
