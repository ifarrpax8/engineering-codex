# Pax8 Standards Context

This directory maps Pax8 Architecture Decision Records (ADRs) to Engineering Codex facets. It provides an organisational overlay on top of the codex's industry best practices.

## When to Use

- **Pax8 projects**: Always check the standards map when making technology decisions — Pax8 may have already decided
- **Non-Pax8 projects**: Ignore this directory entirely — the core codex content stands on its own

## How It Works

The [standards map](standards-map.md) lists each active Pax8 ADR alongside:
- A brief summary of the decision
- The codex facet it relates to
- Whether it's a **standard** (follow unless you have a strong reason not to) or **guidance** (recommended but flexible)

The [deprecated technologies](deprecated.md) list highlights tools and approaches Pax8 is actively moving away from.

## Source

These standards are derived from the [Pax8 ADR repository](../adr/). If the ADR repo is in your workspace, links will resolve to the full decision context. The summaries here are self-contained for when it's not available.

## Keeping This Current

When a new ADR is accepted or an existing one is superseded, update the relevant file here and add a CHANGELOG entry. The `pax8-standard` command reads from these files.
