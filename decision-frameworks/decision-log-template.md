# Decision Log Template

Use this template for lightweight decision records that don't warrant a full ADR. Copy this to your project's `docs/decisions/decision-log.md`.

---

```markdown
# Decision Log

Lightweight record of technical decisions. For significant architectural decisions, use a full [ADR](../adr/).

| # | Date | Facet | Decision | Rationale | Decided By | Codex Ref |
|---|------|-------|----------|-----------|------------|-----------|
| 1 | 2026-02-09 | State Management | Use Pinia for global state | Vue 3 project, Pinia is the official recommendation | Team | [options.md](link) |
| 2 | 2026-02-09 | Internationalization | Use vue-i18n with JSON translation files | Existing pattern in other MFEs, team familiarity | Team | [options.md](link) |
| 3 | | | | | | |
```

## Column Definitions

- **#** -- Sequential number for easy reference
- **Date** -- When the decision was made
- **Facet** -- Which Engineering Codex facet or experience informed this decision
- **Decision** -- What was decided (one sentence)
- **Rationale** -- Why this choice was made (one sentence)
- **Decided By** -- Who made or approved the decision
- **Codex Ref** -- Link to the `options.md` that was consulted (for traceability)

## When to Promote to ADR

If a decision log entry starts attracting questions, debates, or has broader implications than initially expected, promote it to a full ADR using the `generate-adr` command.
