---
name: checklist-runner
description: Audit your project against any Engineering Codex checklist with gap analysis and remediation links.
---

# Checklist Runner Skill

Interactive audit of your project against any Engineering Codex checklist. Walks through each item, inspects your codebase for evidence of compliance, and produces a gap report with links to relevant codex content for remediation.

## When to Use

- Preparing for a production launch and need to verify readiness
- Running a security review before a release
- Auditing accessibility compliance on a frontend project
- Reviewing API design before publishing a new version
- Periodic health checks against any checklist

## When NOT to Use

- **Open-ended architecture review** without a pre-defined checklist — use [Architecture Review](../architecture-review/SKILL.md)
- **Evaluating technology options** — use [Evaluate Options](../evaluate-options/SKILL.md)
- **Reviewing a specific PR** — use the Code Review skill in workspace-standards
- **Learning about a topic** — use [Facet Deep Dive](../facet-deep-dive/SKILL.md)

## Invocation

```
Run the security review checklist against finance-mfe
```

Or for a specific checklist:
```
Run production-readiness checklist for order-handler
```

Or for multiple:
```
Run security and accessibility checklists against currency-manager
```

## Workflow

### Phase 1: Identify Checklist and Project

1. Parse the user's request to identify:
   - Which checklist(s) to run — match against available checklists in `@engineering-codex/checklists/`
   - Which project/repository to audit — must be in the current workspace
2. If ambiguous, list available checklists using AskQuestion:
   ```
   Which checklist would you like to run?
   1. New Project
   2. Production Readiness
   3. New Feature
   4. Code Review
   5. Incident Response
   6. Security Review
   7. Accessibility Audit
   8. API Design Review
   ```
3. Confirm the target project by checking the workspace for the repository

### Phase 2: Project Context Scan

1. Read `@engineering-codex/stack-context.md` for stack assumptions
2. Explore the target project to determine:
   - Project type (frontend-only, backend-only, fullstack, MFE)
   - Tech stack signals (package.json, build.gradle.kts, pom.xml, etc.)
   - Key directories and configuration files
3. Use this context to skip inapplicable checklist items (e.g., skip browser security items for a backend-only service)

### Phase 3: Item-by-Item Audit

For each checklist item:

1. Read the item's requirement
2. Search the project codebase for evidence of compliance:
   - Configuration files (e.g., security headers in nginx.conf or helmet config)
   - Code patterns (e.g., input validation in controllers)
   - Test coverage (e.g., security tests exist)
   - Documentation (e.g., runbooks in docs/)
3. Classify the item:
   - **Pass** — clear evidence the item is addressed
   - **Fail** — evidence the item is missing or incorrectly implemented
   - **Partial** — partially addressed but incomplete
   - **N/A** — not applicable to this project type
   - **Unable to verify** — requires runtime/infrastructure inspection beyond code
4. For each non-pass item, note:
   - What's missing or incorrect
   - The codex link from the checklist item for remediation guidance

### Phase 4: Gap Report

Present the results in a structured format:

```markdown
## Checklist Audit: [Checklist Name] — [Project Name]

**Date:** [Today's date]
**Items checked:** [Count]
**Pass:** [Count] | **Fail:** [Count] | **Partial:** [Count] | **N/A:** [Count]

### Summary
| Section | Pass | Fail | Partial | N/A |
|---------|------|------|---------|-----|
| [Section 1] | X | Y | Z | W |

### Failures and Gaps

#### [Section Name]
- **[Item name]** — [What's missing]
  → Remediation: [Link to relevant codex content]

### Partial Items

#### [Section Name]
- **[Item name]** — [What's incomplete]
  → Next step: [Specific action needed]
```

### Phase 5: Follow-Up

Ask the user how to proceed:

```
What would you like to do with these findings?
1. Create Jira tickets for the gaps
2. Save as a markdown report in the project
3. Deep dive into a specific gap
4. Start fixing a specific issue
5. Re-run after making changes
```

- If Jira → use Atlassian MCP to create tickets with checklist item details
- If save → write report to the project's docs/ directory
- If deep dive → invoke `facet-deep-dive` for the relevant facet
- If fix → begin implementing the remediation
- If re-run → restart from Phase 3

## Verification

- **Phase 1**: Confirm the checklist file exists in `@engineering-codex/checklists/`. If not found, list available checklists before proceeding.
- **Phase 2**: Confirm the target project was found in the workspace. If missing, list available repos.
- **Phase 3**: After each item classification, verify evidence was cited (file path, config key, or "no evidence found"). Do not classify items without explaining why.
- **Phase 4**: Confirm the gap report counts match (Pass + Fail + Partial + N/A = total items).

## Worked Example

**Input:** `Run the security review checklist against currency-manager`

**Key steps:**
1. Loaded `checklists/security-review.md` — 18 items across 5 sections
2. Scanned currency-manager: Kotlin Spring Boot project, detected Spring Security config
3. Audited each item: found CORS config in `SecurityConfig.kt`, input validation via `@Valid`, no hardcoded secrets
4. Failed: no rate limiting on public endpoints, no Content-Security-Policy header

**Output excerpt:**
```markdown
## Checklist Audit: Security Review — currency-manager

**Items checked:** 18
**Pass:** 14 | **Fail:** 2 | **Partial:** 1 | **N/A:** 1

### Failures and Gaps
#### API Security
- **Rate limiting on public endpoints** — No rate limiter configured
  → Remediation: facets/api-design/best-practices.md#rate-limiting
- **Content-Security-Policy header** — Not present in response headers
  → Remediation: facets/security/best-practices.md#security-headers
```

## Error Handling

### Checklist Not Found

If the requested checklist doesn't exist:
- List all available checklists
- Ask the user to select one

### Project Not in Workspace

If the target project isn't accessible:
- List available workspace repositories
- Ask the user to specify the correct project

### Insufficient Codebase Evidence

Some items may require infrastructure or runtime verification:
- Mark these as "Unable to verify — requires manual check"
- Note what to look for (e.g., "Verify TLS configuration in your deployment manifests")

## Related Resources

- [Checklists Index](../../../checklists/README.md) — All available checklists
- [Architecture Review Skill](../architecture-review/SKILL.md) — Broader architecture comparison
- [Facet Deep Dive Skill](../facet-deep-dive/SKILL.md) — Deep dive into a specific topic
