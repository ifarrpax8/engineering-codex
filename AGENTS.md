# Engineering Codex

The authoritative reference guide for building modern web applications. A living document of best practices, architectural patterns, decision frameworks, and user experience guidance.

## Structure

The codex is organised into three content types:

- **Facets** (21 topics) -- Engineering concerns like authentication, API design, testing, security, observability
- **Experiences** (17 topics) -- User-centric concerns like navigation, forms, tables, notifications, responsive design
- **Checklists** -- Actionable lists that link to deeper content (production readiness, security, accessibility)

Each facet and experience has seven perspectives: product, architecture, testing, best-practices, gotchas, options, and (for select facets) operations.

## Skills

This repository provides 10 interactive skills for navigating and applying codex content. They are available in `.cursor/skills/` (Cursor) and `.agents/skills/` (Augment).

- **facet-deep-dive** -- Explore any topic interactively from all angles
- **evaluate-options** -- Walk through a decision matrix with weighted criteria
- **architecture-review** -- Compare your codebase against codex recommendations
- **checklist-runner** -- Run a codex checklist against your project
- **experience-audit** -- Audit frontend components against UX guidelines
- **create-facet** -- Scaffold a new facet or experience
- **onboarding-guide** -- Generate a personalised reading path for your project
- **content-freshness-audit** -- Check content age and technology references
- **refresh-tech-radar** -- Regenerate the tech radar from current content
- **sync-pax8-adrs** -- Diff ADR repo against standards map

## Navigation

- **By role**: See `reading-paths.md` for curated routes (developer, QA, architect, product, DevOps, tech lead)
- **Quick reference**: See `checklists/` for actionable lists
- **Making a decision**: Find the relevant facet, read `options.md`, use the `evaluate-options` skill
- **Learning a topic**: Use the `facet-deep-dive` skill or read through the seven perspectives directly

## Pax8 Context

The `pax8-context/` directory contains Pax8-specific overlays: ADR standards map, deprecated technologies, and organisation-specific guidance. This content is optional and only relevant for Pax8 projects.
