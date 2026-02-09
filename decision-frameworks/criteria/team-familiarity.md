# Team Familiarity

Evaluation criterion for decision matrices across the Engineering Codex.

## Definition

The degree to which the team already has (or can readily acquire) the knowledge needed to implement, operate, and maintain the chosen approach effectively.

## What to Evaluate

- **Current expertise** -- How many team members have production experience with this approach?
- **Learning curve** -- How long does it take a competent developer to become productive (days, weeks, months)?
- **Ecosystem maturity** -- Are there quality tutorials, documentation, Stack Overflow answers, and community support?
- **Hiring pool** -- Can you realistically hire developers with this skill, or is it a niche technology?
- **Transferable skills** -- Does it build on patterns the team already knows (e.g., Spring developers picking up Kotlin, React developers picking up Vue)?
- **Operational knowledge** -- Can the team deploy, monitor, and debug this in production, or does it require specialist ops skills?

## Scoring Guide

- **High** -- Team has production experience. Strong ecosystem with abundant documentation. Easy to hire for. Builds on existing skills.
- **Medium** -- Some team members have exposure. Reasonable learning curve (weeks, not months). Decent ecosystem. May require targeted training or pairing.
- **Low** -- No team experience. Steep learning curve with sparse documentation. Niche technology with a small hiring pool. Requires significant investment before the team is productive.

## When to Weight This Highly

Team familiarity should be weighted heavily when:
- Delivery timelines are tight
- The team is small and can't absorb a steep learning curve
- The technology will need to be maintained long-term by the same team
- On-call support is required (debugging unfamiliar tech at 2am is painful)

It should be weighted lower when:
- The team is explicitly investing in learning a new technology
- The approach has a clear long-term strategic advantage that justifies the ramp-up
- The technology is close enough to existing skills that the curve is manageable

## Related Resources

- [Stack Context](../../stack-context.md) -- The team's current technology landscape
- [Onboarding Guide Skill](../../skills/onboarding-guide/SKILL.md) -- Generating learning paths for new technology
