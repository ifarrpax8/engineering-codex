# Generate Checklist Command

Creates a project-specific checklist from an Engineering Codex checklist template, tailored to the project's tech stack and type.

## Usage

```
Generate a production readiness checklist for currency-manager
```

Or for a specific checklist:
```
Generate security review checklist for finance-mfe
```

Or with explicit project type:
```
Generate API design review checklist for order-handler (backend-only, Kotlin, Spring Boot)
```

## Behavior

1. Identify the checklist template from `@engineering-codex/checklists/`
2. Identify the target project from the user's request
3. Scan the project to determine its type:
   - **Frontend-only** — has package.json but no backend build files
   - **Backend-only** — has build.gradle.kts/pom.xml but no package.json
   - **Fullstack** — has both
   - **MFE** — frontend with module federation or similar configuration
4. Filter the checklist:
   - Remove items that don't apply to the project type (e.g., remove "Browser security headers" for a backend-only service)
   - Remove items for technologies not present (e.g., remove "OAuth/OIDC" items if no auth dependency is found)
   - Keep items marked as "if applicable" only when applicable
5. Add project context to items where possible:
   - Replace generic references with specific file paths (e.g., "Check build.gradle.kts" instead of "Check build file")
   - Note relevant configuration files found during scanning
6. Output the tailored checklist

## Output Format

```markdown
## [Checklist Name]: [Project Name]

**Generated:** [Today's date]
**Project type:** [Frontend / Backend / Fullstack / MFE]
**Items:** [Count] (filtered from [original count] — [removed count] not applicable)

### [Section 1]
- [ ] **[Item]** — [Description, with project-specific notes if any]
- [ ] **[Item]** — [Description]
  💡 Found: `[relevant file or config in the project]`

### [Section 2]
...

---
*Items removed as not applicable: [list of removed items with reasons]*
*Template: [Link to original checklist]*
```

## Difference from Checklist Runner Skill

This command **generates** a tailored checklist. The Checklist Runner skill **runs** the checklist interactively, inspecting your code for each item and producing a pass/fail report.

Typical workflow:
1. `Generate checklist` → get a project-specific checklist
2. `Run checklist` → audit the project against it

## Related Resources

- [Checklists Index](../checklists/README.md) — All available checklist templates
- [Checklist Runner Skill](../skills/checklist-runner/SKILL.md) — Run the checklist interactively
- [Stack Context](../stack-context.md) — Team's standard tech stack assumptions
