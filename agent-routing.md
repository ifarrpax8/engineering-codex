# Agent Routing

On-demand lookup table mapping user tasks to the files an agent should read. Skills reference this file in their workflow steps -- it is not loaded automatically.

## Task Routing

| When the user... | Read these files | Complexity |
|------------------|-----------------|------------|
| Asks about authentication or auth patterns | `facets/authentication/` (start with `best-practices.md`) | low |
| Asks about API design or REST conventions | `facets/api-design/` (start with `best-practices.md`) | low |
| Asks about testing strategy or test gaps | `facets/testing/` (start with `options.md`, `best-practices.md`) | low |
| Asks about error handling patterns | `facets/error-handling/` (start with `best-practices.md`, `gotchas.md`) | low |
| Asks about security concerns | `facets/security/`, `checklists/security-review.md` | low |
| Asks about backend architecture | `facets/backend-architecture/` (start with `architecture.md`, `options.md`) | high |
| Asks about frontend architecture or MFEs | `facets/frontend-architecture/`, `experiences/` relevant to UI | high |
| Asks about data persistence or databases | `facets/data-persistence/` (start with `options.md`) | high |
| Asks to evaluate options or make a decision | `.cursor/skills/evaluate-options/SKILL.md`, relevant facet `options.md` | high |
| Asks to review architecture against codex | `.cursor/skills/architecture-review/SKILL.md` | high |
| Asks to run a checklist | `.cursor/skills/checklist-runner/SKILL.md`, relevant `checklists/` file | low |
| Asks to audit a frontend experience | `.cursor/skills/experience-audit/SKILL.md`, relevant `experiences/` directory | low |
| Asks to explore a facet or topic | `.cursor/skills/facet-deep-dive/SKILL.md`, relevant `facets/` or `experiences/` directory | low |
| Asks to create a new facet or experience | `.cursor/skills/create-facet/SKILL.md`, `CONTRIBUTING.md` | low |
| Asks about onboarding or what to read | `.cursor/skills/onboarding-guide/SKILL.md`, `reading-paths.md` | low |
| Asks about production readiness | `checklists/production-readiness.md` | low |
| Asks about accessibility | `checklists/accessibility-audit.md`, `experiences/accessibility/` | low |
| Asks about Pax8 standards or ADRs | `pax8-context/`, `.cursor/skills/sync-pax8-adrs/SKILL.md` | high |
| Asks about evolution or migration patterns | `evolution/` (start with relevant guide) | high |
