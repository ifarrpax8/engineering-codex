# Documenting Decisions

Guide for when and how to document technical decisions informed by the Engineering Codex.

## Why Document Decisions?

Decisions are the most perishable form of knowledge. Six months from now, no one will remember why JWT was chosen over sessions, or why the team picked REST over GraphQL. Documenting decisions:

- Prevents relitigating the same debate
- Helps new team members understand the codebase
- Creates traceability from the codex reference to the project implementation
- Makes it clear when evolution triggers warrant revisiting a choice

## When to Use an ADR vs a Decision Log

### Use an ADR (Architecture Decision Record) When:

- The decision is **architecturally significant** -- it affects the structure, non-functional characteristics, or major patterns of the system
- The decision is **hard to reverse** -- changing it later would require significant rework
- The decision involved **evaluating multiple options** with meaningful trade-offs
- The decision will be **referenced by future developers** trying to understand why things are the way they are

**Examples:** Choosing between REST and GraphQL, adopting event sourcing, selecting an authentication strategy, deciding on MFE vs SPA.

### Use a Decision Log Entry When:

- The decision is **smaller in scope** but still worth recording
- The decision was **straightforward** -- clear best practice with minor context-specific considerations
- The decision is **easy to reverse** if needed
- You want a **lightweight record** without the ceremony of a full ADR

**Examples:** Choosing a date formatting library, deciding on a naming convention, selecting a test data generation approach.

### Skip Documentation When:

- The decision is **trivial** -- no one will ever wonder why
- The decision follows an **existing standard** that's already documented elsewhere
- The decision is **temporary** and will be revisited shortly

## Decision Documentation Workflow

```
1. Encounter a decision point
2. Read the relevant facet's options.md in the codex
3. Use evaluate-options skill (interactive) or compare-options command (quick look)
4. Make your decision
5. Document it:
   - Significant → generate-adr command → saves to project's docs/adr/
   - Lightweight → add a row to project's decision log
6. Both formats reference the codex facet that informed them
7. Note evolution triggers for future review
```

## Where to Store Decisions

Decisions live in the **project repository**, not in the codex. The codex is the reference; decisions are project-specific.

### ADR Location

```
<project-root>/
└── docs/
    └── adr/
        ├── 0001-use-jwt-authentication.md
        ├── 0002-adopt-event-sourcing.md
        └── 0003-choose-rest-over-graphql.md
```

### Decision Log Location

```
<project-root>/
└── docs/
    └── decisions/
        └── decision-log.md
```

## Templates

- [ADR Template](adr-template.md) -- Full Architecture Decision Record with codex reference
- [Decision Log Template](decision-log-template.md) -- Lightweight table format

## Revisiting Decisions

Decisions should be revisited when:

1. An **evolution trigger** is reached (documented in the original decision)
2. The **codex is updated** with new recommendations (check CHANGELOG)
3. **Assumptions change** -- team size, traffic, requirements
4. **Pain is felt** -- the current approach is causing friction

When revisiting, create a new ADR that supersedes the original. Don't modify old ADRs -- they're a historical record.
