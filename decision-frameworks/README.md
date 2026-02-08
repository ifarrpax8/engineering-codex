# Decision Frameworks

Tools and templates for making and documenting technical decisions informed by the Engineering Codex.

## Contents

| File | Purpose |
|------|---------|
| [template.md](template.md) | Blank decision matrix template for use in facet `options.md` files |
| [documenting-decisions.md](documenting-decisions.md) | Guide on when and how to document decisions (ADR vs decision log) |
| [adr-template.md](adr-template.md) | Architecture Decision Record template with codex reference field |
| [decision-log-template.md](decision-log-template.md) | Lightweight table-based decision log for smaller decisions |

## Evaluation Criteria

Reusable criteria definitions that can be applied across any facet's decision matrix:

| Criterion | Description |
|-----------|-------------|
| [Scalability](criteria/scalability.md) | Ability to handle growth in users, data, and complexity |
| [Maintainability](criteria/maintainability.md) | Ease of understanding, modifying, and extending over time |
| [Developer Experience](criteria/developer-experience.md) | Impact on developer productivity, onboarding, and satisfaction |
| [Cost](criteria/cost.md) | Financial implications including licensing, infrastructure, and labor |
| [Time to Market](criteria/time-to-market.md) | Speed of initial delivery and ongoing feature development |

## How It All Connects

```
┌─────────────────────┐     ┌──────────────────────┐
│   Facet options.md   │────▶│  evaluate-options     │
│   (what to decide)   │     │  skill (interactive)  │
└─────────────────────┘     └──────────┬───────────┘
                                       │
                            ┌──────────▼───────────┐
                            │  Decision Made        │
                            └──────────┬───────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                                      ▼
         ┌──────────────────┐               ┌──────────────────┐
         │  generate-adr    │               │  Decision Log     │
         │  (significant)   │               │  (lightweight)    │
         └──────────────────┘               └──────────────────┘
                    │                                      │
                    ▼                                      ▼
         ┌──────────────────┐               ┌──────────────────┐
         │  Project ADR     │               │  Project Log      │
         │  docs/adr/       │               │  docs/decisions/  │
         └──────────────────┘               └──────────────────┘
```
