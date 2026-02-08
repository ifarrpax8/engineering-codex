# Decision Matrix Template

Use this template when creating a new `options.md` file for a facet or experience. Choose the appropriate `recommendation_type` based on whether there's a clear best practice or genuinely competing approaches.

---

## Best Practice Mode

```markdown
---
recommendation_type: best-practice
---

# [Facet Name] -- Options

## Recommended Approach

**[Approach Name]**

[Description of why this is the recommended approach. What makes it the clear choice in most situations.]

### Key Principles

- [Principle 1]
- [Principle 2]
- [Principle 3]

## Consider Instead If...

### [Alternative 1 Name]

**When to consider:** [Specific conditions under which this alternative is preferable]

**Trade-offs:**
- Gain: [What you gain by choosing this alternative]
- Lose: [What you lose compared to the recommended approach]

### [Alternative 2 Name]

**When to consider:** [Specific conditions]

**Trade-offs:**
- Gain: [What you gain]
- Lose: [What you lose]

## Synergies

- **If you chose [X] in [other-facet]** → [How it interacts with this recommendation]

## Evolution Triggers

- [Condition that would warrant reconsidering this recommendation]
- [Another condition]
```

---

## Decision Matrix Mode

```markdown
---
recommendation_type: decision-matrix
---

# [Facet Name] -- Options

## Context

[Brief description of the decision space. What problem are we solving? Why are there multiple valid approaches?]

## Options

### Option 1: [Name]

- **Description:** [What this approach is and how it works]
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best For:** [Situations where this option excels]
- **Avoid When:** [Situations where this option is a poor fit]

### Option 2: [Name]

- **Description:** [What this approach is]
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best For:** [Situations where this option excels]
- **Avoid When:** [Situations where this option is a poor fit]

### Option 3: [Name]

- **Description:** [What this approach is]
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best For:** [Situations where this option excels]
- **Avoid When:** [Situations where this option is a poor fit]

## Evaluation Criteria

See [decision-frameworks/criteria/](../decision-frameworks/criteria/) for detailed definitions.

| Criteria | Weight | Option 1 | Option 2 | Option 3 |
|----------|--------|----------|----------|----------|
| Scalability | | | | |
| Maintainability | | | | |
| Developer Experience | | | | |
| Cost | | | | |
| Time to Market | | | | |

## Recommendation Guidance

[When to pick which option, based on project characteristics. Avoid declaring a single winner -- instead, describe the conditions that favor each option.]

## Synergies

- **If you chose [X] in [other-facet]** → [How it changes the recommendation here]
- **If you chose [Y] in [other-facet]** → [How it changes the recommendation here]

## Evolution Triggers

- [Condition that would warrant reconsidering this decision]
- [Another condition]
```
