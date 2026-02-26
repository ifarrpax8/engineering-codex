---
name: create-facet
description: Scaffold a new facet or experience in the Engineering Codex with all required template files.
complexity: low
prompt-version: "1.0"
---

# Create Facet Skill

Scaffolds a new facet or experience directory in the Engineering Codex with all 7 required template files, updates the index, and adds a CHANGELOG entry.

## When to Use

- Adding a new engineering concern that deserves its own facet
- Adding a new user-centric experience perspective
- Expanding the codex with a topic not currently covered

## When NOT to Use

- **Content already exists** for this topic — update the existing facet instead
- **Quick note** or gotcha — add it to an existing facet's `gotchas.md` rather than creating a new facet
- **Experience-specific** content that belongs in an existing experience — update the existing experience

## Invocation

```
Create a new facet called "caching"
```

Or for an experience:
```
Create a new experience called "drag-and-drop"
```

## Workflow

### Phase 1: Gather Information

Ask the user for the required information using AskQuestion:

```
What type of content is this?
1. Facet (engineering-focused)
2. Experience (user-centric)
```

Then ask for:
- **Name** -- kebab-case directory name (e.g., `caching`, `drag-and-drop`)
- **Title** -- Display title (e.g., "Caching", "Drag and Drop")
- **Description** -- One-line description for the index

### Phase 2: Create Directory and Files

1. Create the directory: `facets/<name>/` or `experiences/<name>/`

2. Create `README.md` with frontmatter:

```markdown
---
title: <Title>
type: facet  # or "experience"
last_updated: <today's date>
---

# <Title>

<Description>

## Perspectives

- [Product Perspective](product.md) -- Business value, user flows, personas
- [Architecture](architecture.md) -- Patterns, diagrams, trade-offs
- [Testing](testing.md) -- Test strategies, tooling categories
- [Best Practices](best-practices.md) -- Language-agnostic principles
- [Options](options.md) -- Decision matrix or recommended practice

## Related Facets

<!-- Add cross-references to related facets and experiences -->

## Related Experiences

<!-- Add cross-references to related experiences -->
```

3. Create `product.md`:

```markdown
# <Title> -- Product Perspective

<!-- Business value, user impact, stakeholder concerns, compliance requirements, success metrics -->
<!-- What user flows does this concern affect? -->
<!-- What personas care about this? -->
<!-- What are the business/compliance drivers? -->
```

4. Create `architecture.md`:

```markdown
# <Title> -- Architecture

<!-- Patterns and approaches with diagrams -->
<!-- Trade-offs between approaches -->
<!-- Integration points with other systems -->
<!-- Failure modes and resilience considerations -->
```

5. Create `testing.md`:

```markdown
# <Title> -- Testing

<!-- Testing strategies per layer (unit, integration, e2e) -->
<!-- What to test vs what not to test -->
<!-- Test pyramid considerations for this concern -->
<!-- Tooling categories (not specific tools, but types of tools needed) -->
```

6. Create `best-practices.md`:

```markdown
# <Title> -- Best Practices

<!-- Language-agnostic principles -->
<!-- Anti-patterns to avoid -->
<!-- Code organization recommendations -->
<!-- Stack-specific callouts where they materially affect the recommendation -->
<!-- See stack-context.md for assumed technology landscape -->
```

7. Create `gotchas.md`:

```markdown
# <Title> -- Gotchas

<!-- Common pitfalls and traps developers encounter -->
<!-- Things that seem reasonable at first but cause problems -->
<!-- Specific to the patterns and options in this facet -->
```

8. Create `options.md`:

```markdown
---
recommendation_type: decision-matrix  # or "best-practice"
---

# <Title> -- Options

<!-- If best-practice: Lead with the recommendation, list "consider instead if..." escape hatches -->
<!-- If decision-matrix: Present all options with criteria scoring -->

## Contents

<!-- TOC MUST include nested entries for each individual option under its parent section -->
<!-- Example: -->
<!-- - [Options](#options) -->
<!--   - [Option A](#1-option-a) -->
<!--   - [Option B](#2-option-b) -->
<!-- - [Evaluation Criteria](#evaluation-criteria) -->
<!-- - [Recommendation Guidance](#recommendation-guidance) -->
<!-- - [Synergies](#synergies) -->
<!-- - [Evolution Triggers](#evolution-triggers) -->

## Options

<!-- ### 1. [Name] -->
<!-- - **Description:** -->
<!-- - **Strengths:** -->
<!-- - **Weaknesses:** -->
<!-- - **Best For:** -->
<!-- - **Avoid When:** -->

## Synergies

<!-- How do decisions in this facet interact with decisions in other facets? -->
<!-- Format: **If you chose X here** -> In `other-facet`, Y becomes more/less favorable -->

## Evolution Triggers

<!-- When should this decision be reconsidered? -->
<!-- What changes in scale, team, or requirements would warrant revisiting? -->
```

> **Important:** The `## Contents` section in `options.md` must drill down to list each individual option as a nested entry under its parent section. This makes the available choices scannable at a glance. See any existing facet's `options.md` for examples.

### Phase 3: Update Index

1. Read the relevant index file: `facets/README.md` or `experiences/README.md`
2. Add the new entry in alphabetical order within the table
3. Write the updated index file

### Phase 4: Update Changelog

1. Read `CHANGELOG.md`
2. Add an entry under today's date (create a new date section if needed):
   ```
   ### Added
   - New [facet/experience]: <Title> -- <Description>
   ```
3. Write the updated changelog

### Phase 5: Confirm

Present a summary of what was created:
```
Created new <type> "<Title>":
- facets/<name>/README.md
- facets/<name>/product.md
- facets/<name>/architecture.md
- facets/<name>/testing.md
- facets/<name>/best-practices.md
- facets/<name>/gotchas.md
- facets/<name>/options.md
- Updated facets/README.md index
- Updated CHANGELOG.md

Next steps:
1. Populate the perspective files with content
2. Add cross-references to related facets and experiences
3. Commit the changes
```

## Verification

- **Phase 2**: After creating each file, verify it exists and starts with the expected heading. If any file fails, report which ones.
- **Phase 3**: After updating the index, verify the new entry appears in the file by reading it back.
- **Phase 4**: After updating the changelog, verify the new entry appears under today's date.

## Worked Example

**Input:** `Create a new facet called "caching"`

**Key steps:**
1. Gathered: type = Facet, name = `caching`, title = "Caching", description = "Strategies for data caching across layers"
2. Created `facets/caching/` with 7 files: README.md, product.md, architecture.md, testing.md, best-practices.md, gotchas.md, options.md
3. Updated `facets/README.md` — added "Caching" in alphabetical order
4. Updated `CHANGELOG.md` — added entry under today's date

**Output excerpt:**
```
Created new facet "Caching":
- facets/caching/README.md
- facets/caching/product.md
- facets/caching/architecture.md
- facets/caching/testing.md
- facets/caching/best-practices.md
- facets/caching/gotchas.md
- facets/caching/options.md
- Updated facets/README.md index
- Updated CHANGELOG.md
```

## Error Handling

### Name Already Exists

If a facet or experience with the given name already exists:
- Inform the user
- Ask if they want to choose a different name or update the existing one

### Invalid Name Format

If the name isn't in kebab-case:
- Convert it automatically (e.g., "Drag and Drop" → "drag-and-drop")
- Confirm with the user before proceeding

## Related Resources

- [Contributing Guidelines](../../../CONTRIBUTING.md) -- Content principles and conventions
- [Facets Index](../../../facets/README.md) -- Current engineering facets
- [Experiences Index](../../../experiences/README.md) -- Current UX experiences
