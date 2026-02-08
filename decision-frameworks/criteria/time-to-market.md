# Time to Market

Evaluation criterion for decision matrices across the Engineering Codex.

## Definition

The speed at which the chosen approach allows the team to deliver working software to users, both for the initial implementation and for ongoing feature development.

## What to Evaluate

- **Initial setup time** -- How long to go from zero to a working implementation?
- **Prototype speed** -- How quickly can you validate the approach with a working prototype?
- **Iteration speed** -- Once established, how fast can you ship new features?
- **Integration effort** -- How much work is needed to integrate with existing systems?
- **Out-of-the-box features** -- Does the approach provide built-in capabilities that would otherwise need to be built?
- **Community resources** -- Are there starter templates, tutorials, and examples available?

## Scoring Guide

- **High** -- Quick setup, fast iteration, strong out-of-the-box features, abundant community resources.
- **Medium** -- Moderate setup time, reasonable iteration speed, some features need to be built.
- **Low** -- Lengthy setup, slow iteration, most features need to be built from scratch.

## Important Trade-Off

Time to market often trades off against long-term maintainability and scalability. A fast initial delivery with high technical debt may slow down future development. Consider the project's timeline:

- **Short-lived or experimental** -- Weight time to market higher
- **Long-lived or core product** -- Weight maintainability and scalability higher
- **Competitive pressure** -- May justify accepting some technical debt with a plan to address it

## Evolution Consideration

An approach that's fast to market but hard to evolve may create an inflection point sooner. See [evolution/scaling-triggers.md](../../evolution/scaling-triggers.md) for guidance on when initial choices become constraints.
