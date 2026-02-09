---
name: Onboarding Guide
description: Generate a personalized reading path through the Engineering Codex based on your project's tech stack and architecture.
---

# Onboarding Guide Skill

Scans a project to detect its tech stack, architecture patterns, and key concerns, then generates a personalized reading path through the Engineering Codex. Goes beyond the static reading-paths.md by being project-aware and role-aware.

## When to Use

- Joining a new project and want to understand its architecture through the codex lens
- Onboarding a new team member and want to give them a curated learning path
- Switching between projects and need a quick refresher on the relevant patterns
- Wanting to understand which codex content is most relevant to your current work

## Invocation

```
Onboard me to order-management-mfe
```

Or with a role:
```
Onboard me to currency-manager as a QA engineer
```

Or for a new team member:
```
Generate an onboarding guide for a new developer joining finance-mfe
```

## Workflow

### Phase 1: Identify Project and Role

1. Identify the target project from the user's request
2. Determine the role context using AskQuestion:
   ```
   What's your role or focus area?
   1. New developer (full onboarding)
   2. QA / Test engineer
   3. Architect / Tech lead
   4. Frontend developer
   5. Backend developer
   6. DevOps / Platform engineer
   7. Product manager / Designer
   ```
3. Note any specific interests mentioned (e.g., "especially the authentication parts")

### Phase 2: Project Stack Detection

Scan the target project to identify:

1. **Frontend signals:**
   - package.json → framework (Vue, React), dependencies (Pinia, Zustand, TanStack Query)
   - Component structure (SFC, JSX, TSX)
   - CSS approach (Tailwind, MUI, Propulsion, CSS modules)
   - Build tool (Vite, Webpack)
   - Test runner (Vitest, Jest, Playwright)

2. **Backend signals:**
   - build.gradle.kts / pom.xml → framework (Spring Boot), language (Java, Kotlin)
   - Key dependencies (Axon Framework, Spring Security, Spring Data)
   - Architecture patterns (hexagonal, layered, CQRS)
   - Test frameworks (JUnit 5, MockK, Testcontainers)

3. **Infrastructure signals:**
   - Dockerfile, docker-compose.yml
   - Kubernetes manifests, Helm charts
   - CI/CD configuration (GitHub Actions, Azure Pipelines)
   - Terraform files

4. **Architecture signals:**
   - Event sourcing (Axon aggregates, event handlers)
   - API specs (OpenAPI, TypeSpec)
   - Multi-tenancy patterns
   - Feature flags
   - i18n configuration

### Phase 3: Map to Codex Content

Based on detected signals, map to relevant facets and experiences:

1. **Core facets** (always relevant):
   - testing, error-handling, security
2. **Stack-specific facets** (based on detection):
   - If Spring Boot → backend-architecture, api-design, data-persistence
   - If Vue/React → frontend-architecture, state-management
   - If Axon → event-driven-architecture
   - If MFE → frontend-architecture (MFE sections)
   - If i18n files → internationalization
   - If feature flags → feature-toggles
   - If Kubernetes → ci-cd, observability, configuration-management
3. **Relevant experiences** (based on frontend components found):
   - If table components → tables-and-data-grids
   - If form components → forms-and-data-entry
   - If notification components → notifications
   - If auth flows → permissions-ux

### Phase 4: Generate Reading Path

Produce a personalized, ordered reading path:

```markdown
## Onboarding Guide: [Project Name]

**Generated for:** [Role]
**Date:** [Today's date]

### Project Profile
- **Type:** [Frontend / Backend / Fullstack / MFE]
- **Stack:** [Detected technologies]
- **Key patterns:** [Detected architectural patterns]

### Start Here
1. [Stack Context](engineering-codex/stack-context.md) — our standard tech assumptions
2. [Glossary](engineering-codex/glossary.md) — terminology we use

### Core Reading (do these first)
3. [Facet — TL;DR](link to README) — [Why it's relevant to this project]
4. [Facet — Best Practices](link) — [Specific aspect to focus on]
...

### Project-Specific Reading
X. [Facet/Experience](link) — [Why this is relevant: "this project uses Axon for event sourcing"]
...

### Deep Dives (when you're ready)
Y. [Facet — Architecture](link) — [For understanding the patterns in depth]
...

### Checklists to Know
- [Relevant checklist](link) — [When you'll need it]
```

### Phase 5: Optional Extras

Ask the user:
```
Would you like me to also:
1. Run an architecture review of this project (see how it aligns with the codex)
2. Identify the top 3 gotchas for this project's stack
3. Save this reading path as a markdown file in the project
```

## Error Handling

### Project Not in Workspace
- List available workspace repositories
- Ask the user to specify the correct project

### Minimal Project (few signals)
If the project has very few detectable signals:
- Fall back to the role-based static reading paths from `@engineering-codex/reading-paths.md`
- Note which facets couldn't be confirmed as relevant

### Unknown Framework
If the project uses a framework not covered in stack-context.md:
- Note this in the output
- Still provide the language-agnostic content
- Suggest updating stack-context.md if this framework is standard for the team

## Related Resources

- [Reading Paths](../../reading-paths.md) — Static role-based reading paths
- [Stack Context](../../stack-context.md) — Team's standard tech stack
- [Architecture Review Skill](../architecture-review/SKILL.md) — Deeper review after onboarding
- [Facet Deep Dive Skill](../facet-deep-dive/SKILL.md) — Explore any facet in depth
