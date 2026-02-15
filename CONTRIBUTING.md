# Contributing to the Engineering Codex

This is a living document. Contributions are welcome and encouraged as best practices evolve and new patterns emerge.

## Content Principles

1. **Opinionated but fair** -- Present recommendations clearly, but acknowledge alternatives honestly
2. **Language-agnostic first** -- Lead with principles, add stack-specific callouts where they materially change the recommendation (see [stack-context.md](stack-context.md))
3. **Concise and scannable** -- Use headers, bullet points, and tables. Avoid walls of text
4. **Link, don't duplicate** -- Cross-reference other facets and experiences rather than repeating content
5. **Evergreen over trendy** -- Prefer established patterns. Note emerging approaches but don't over-index on hype

## Directory Conventions

| Content Type | Location | Format |
|-------------|----------|--------|
| Cursor Skills | `.cursor/skills/{skill-name}/SKILL.md` | Markdown with structured workflow |
| Cursor Subagents | `.cursor/agents/{name}.md` | YAML frontmatter + system prompt |
| Cursor Commands | `commands/{name}.md` | Markdown with usage and behavior |
| Facets | `facets/{name}/` | 7 files per facet (see below) |
| Experiences | `experiences/{name}/` | 7 files per experience (see below) |
| Checklists | `checklists/{name}.md` | Markdown with actionable items |
| Evolution Guides | `evolution/{name}.md` | Markdown with scaling journeys |
| Pax8 Context | `pax8-context/` | ADR mappings, deprecated tech, radar overlay |

## Adding a Skill

Skills are interactive Cursor workflows. Each skill is a single file at `.cursor/skills/{name}/SKILL.md`, auto-discovered by Cursor when the repo is in the workspace.

### Required Sections

Every skill must include:

1. **Frontmatter** — `name` and `description` (15-20 words, used by Cursor for routing)
2. **When to Use** — Scenarios for invocation
3. **When NOT to Use** — Disambiguation from overlapping skills (with links to alternatives)
4. **Workflow** — Phased steps with clear instructions
5. **Verification** — Checkpoints after operations that can fail silently
6. **Worked Example** — One condensed input-to-output example
7. **Error Handling** — Graceful handling of missing dependencies or failures

See [SKILLS.md](SKILLS.md) for the full index of available skills.

## Adding a Subagent

Subagents are custom AI agents with focused system prompts. They live directly in `.cursor/agents/{name}.md` (no wrapper needed).

### Required Format

```markdown
---
name: {agent-name}
description: {When to use this agent. Include "use proactively" to encourage automatic delegation.}
model: fast        # fast, inherit, or a specific model ID
readonly: true     # true if the agent only reads, doesn't write
---

{System prompt: what the agent does, how it behaves, what output format to use}
```

### Conventions

- Keep the system prompt focused on a single responsibility
- Include specific instructions for different invocation scenarios
- Use `model: fast` for read-only lookup agents, `model: inherit` for agents that need to write
- Set `readonly: true` for agents that only read and synthesise (no file changes)

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

If creating manually, every facet or experience must include these 7 files:

```
facets/<name>/
├── README.md           # Overview, navigation, quick reference
├── product.md          # Business value, user flows, personas
├── architecture.md     # Patterns, diagrams, trade-offs
├── testing.md          # Test strategies, tooling categories
├── best-practices.md   # Language-agnostic principles
├── gotchas.md          # Common pitfalls and traps
└── options.md          # Decision matrix or best practice
```

### README.md Frontmatter

Every facet/experience README must include:

```yaml
---
title: <Display Name>
type: facet  # or "experience"
last_updated: YYYY-MM-DD
tags: [keyword1, keyword2, keyword3]
---
```

### Tagging Conventions

Tags enable cross-cutting discovery via [tag-index.md](tag-index.md). When adding or updating tags:

- Use lowercase, hyphenated keywords (e.g., `spring-boot`, not `Spring Boot`)
- Include technology names (e.g., `kafka`, `vue-router`), concepts (e.g., `event-sourcing`, `pagination`), and abbreviations (e.g., `a11y`, `i18n`)
- Aim for 5-10 tags per entry — enough for discoverability without noise
- After updating tags, regenerate the index: `python3 ./scripts/generate-tag-index.sh`

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
See [Authentication > Architecture](facets/authentication/architecture.md) for session management patterns.
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
