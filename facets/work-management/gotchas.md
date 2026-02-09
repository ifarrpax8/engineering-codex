# Gotchas: Work Management Pitfalls

Work management systems can create value or waste depending on how they're used. Common pitfalls turn ticket systems into bureaucratic overhead rather than delivery enablers. Recognizing these gotchas helps teams avoid them and maintain effective work management practices.

## Vague Tickets

A ticket that says "improve performance" with no context, acceptance criteria, or scope forces developers to guess what's needed. They might optimize the wrong endpoint, build something that doesn't meet the actual need, or spend time researching when they should be implementing. The result is wasted effort and potential rework.

Vague tickets lack boundaries. Without clear acceptance criteria, every enhancement seems reasonable, and scope creeps. A ticket to "improve performance" might expand to include caching, database optimization, API refactoring, and frontend optimization because the original ticket didn't specify what was in scope.

Vague tickets also create communication overhead. Developers must schedule clarification meetings, ask questions in Slack, or make assumptions that might be wrong. This back-and-forth wastes time and fragments focus.

Every ticket needs clear acceptance criteria that define what "done" means. "Improve API response time from 500ms to under 200ms for the invoice list endpoint" is specific and testable. "Improve performance" is not.

## Story Point Inflation

Velocity goes up but delivery doesn't improve. Teams unconsciously inflate estimates to look more productive. A story that was 3 points last sprint becomes 5 points this sprint, not because it's more complex, but because the team wants to show higher velocity.

Story point inflation breaks velocity as a planning tool. If points don't represent relative complexity, velocity becomes meaningless. A team that completes 30 points per sprint might actually be delivering less value than a team that completes 20 points, if the first team is inflating estimates.

Inflation often happens when velocity is used for performance evaluation. If managers compare teams based on velocity, teams feel pressure to show higher numbers. This creates perverse incentives that undermine estimation accuracy.

Focus on consistent sizing, not increasing numbers. Velocity should stabilize after a few sprints as teams calibrate. If velocity keeps increasing without corresponding delivery improvement, investigate inflation.

## Sprint Scope Creep

Adding tickets mid-sprint "because it's urgent" undermines sprint commitment. Every addition pushes something else out, but teams often don't explicitly remove work, leading to overcommitment and missed sprint goals.

Sprint scope creep breaks the time-box. Sprints are time-boxed iterations with committed scope. Adding work mid-sprint changes the commitment without adjusting the time box, making the sprint goal unachievable.

Urgent work should replace existing work, not add to it. If something is truly urgent, it should bump lower-priority work out of the sprint. This trade-off should be explicit and discussed, not implicit and unacknowledged.

Protect sprint scope. Once a sprint is planned and committed to, resist adding work unless it's truly critical and replaces existing work. This discipline ensures sprint goals are achievable and velocity is meaningful.

## Tickets as Task Lists

A ticket that reads "Step 1: create database table. Step 2: add API endpoint. Step 3: write tests. Step 4: update frontend" micromanages the developer and conflates the "what" with the "how." Tickets should define what to achieve (acceptance criteria), not how to achieve it (implementation steps).

Task-list tickets reduce developer autonomy. They tell developers exactly what to do rather than what to achieve. This prevents creative problem-solving and makes tickets feel like assignments rather than goals.

Task-list tickets also create maintenance overhead. If the implementation approach changes (which it often does as understanding deepens), the ticket must be updated. This creates busywork without value.

Tickets should focus on outcomes: "user can download invoice as PDF." The developer determines how to achieve this outcome. Technical notes in refinement can capture approach decisions, but the ticket itself should focus on what, not how.

## Stale Backlog

A backlog with hundreds of tickets that will never be worked on becomes a graveyard instead of a planning tool. It's impossible to identify what's actually prioritized when the backlog is cluttered with stale tickets from months or years ago.

Stale backlogs indicate poor prioritization or refinement discipline. If tickets sit untouched for 90+ days, they're either not prioritized or the backlog isn't being actively managed. Regular pruning is essential to maintain backlog health.

Stale tickets also create noise. When planning sprints, teams must wade through hundreds of irrelevant tickets to find what's actually prioritized. This overhead slows planning and reduces effectiveness.

Regularly prune the backlog. Close or archive tickets that have been inactive for 90+ days or won't be prioritized. A healthy backlog has 1-2 sprints of refined work ready for planning, not hundreds of stale tickets.

## Missing Spike Before Complex Work

Committing to a 13-point story without understanding the technical approach is risky. Unknowns discovered during implementation can derail the sprint. The story drags across multiple sprints as scope changes with each new discovery.

Complex work should be spiked before estimation and commitment. A spike investigates the approach, identifies risks, and produces findings that inform story creation. Estimating after a spike is more accurate than estimating blind.

Spikes are time-boxed (typically 1-3 days) to prevent scope creep. They produce recommendations and next steps, not implementation. The spike findings inform story creation, and the stories are what get estimated and committed to.

If a story encounters unexpected complexity during implementation, it might need to be spiked mid-implementation. This is a signal that the original story was too large or insufficiently understood. The spike should produce a plan for completing the work or breaking it down further.

## Bug vs Feature Confusion

"Bug: the system doesn't support CSV export" is mislabeled. This was never a feature, so it's not a bug—it's a feature request. Bugs are broken promises: documented or expected behavior that doesn't work. Mislabeling inflates defect metrics and confuses prioritization.

Bugs should have steps to reproduce, expected behavior, and actual behavior. If there's no expected behavior (because the feature never existed), it's not a bug. Feature requests should be tracked as stories, not bugs.

This confusion often happens when stakeholders want something labeled as a bug to increase priority. But priority should be based on impact, not label. A critical feature request might be higher priority than a low-severity bug.

Clear definitions prevent confusion. Bugs are defects in existing functionality. Feature requests are new capabilities. Use the right ticket type for the right work.

## Using Velocity for Performance Evaluation

Comparing Team A's velocity to Team B's velocity, or using individual velocity to evaluate developers, breaks estimation. Story points are relative to the team—they're for planning, not performance measurement.

Velocity is team-relative. Team A's 5 points might represent different effort than Team B's 5 points. This is fine because points are calibrated within teams for planning purposes. Comparing across teams is meaningless.

Using velocity for performance evaluation creates perverse incentives. Teams inflate estimates to show higher velocity. Developers avoid large tickets to show higher individual velocity. These behaviors undermine estimation accuracy.

Velocity should be used for capacity planning within a team, not for comparing teams or evaluating individuals. If managers need performance metrics, use delivery outcomes (features shipped, bugs fixed) rather than velocity.

## Subtask Overload

Breaking a 3-point story into 15 subtasks creates overhead that exceeds value. The time spent creating, estimating, and tracking subtasks might exceed the time saved by granular tracking. Subtasks should be used sparingly (3-5 per story maximum) and only when progress tracking is genuinely needed.

Subtasks are useful when multiple developers collaborate on a story or when progress tracking within a story is valuable. But for a story that one developer completes in a day, subtasks are unnecessary overhead.

If a story needs 15 subtasks, it's probably too large and should be broken into separate stories. Subtasks shouldn't be a way to avoid breaking down large stories.

Use subtasks when they provide genuine value: parallel work, progress tracking, or clarity. Don't use them as a default practice for every story.

## Not Linking PRs to Tickets

Code changes without ticket context make it impossible to answer "why was this change made?" months later. When debugging a production issue, tickets linked to the affected code reveal what was intended and what might have gone wrong.

Linking happens through branch names, commit messages, and PR descriptions. Branch names should include ticket IDs. Commit messages should reference tickets. PR descriptions should link to tickets and summarize changes.

This linking enables traceability from code to requirement. It also enables automated tracking: when a PR is merged, the ticket can automatically move to "Done." This automation reduces manual overhead and ensures accuracy.

Always link PRs to tickets. This discipline ensures code changes are traceable to requirements, enabling debugging, compliance, and historical understanding.

## Treating Refinement as Optional

Skipping refinement to "save time" creates problems downstream. Sprint planning takes 2 hours because tickets aren't ready. Developers start tickets and immediately get blocked by unclear requirements. The time "saved" by skipping refinement is lost many times over in clarification and rework.

Refinement should be an ongoing process, not a single meeting. As new tickets are created or priorities change, they should be refined. This continuous refinement prevents backlog decay and ensures tickets are always ready.

Regular refinement prevents the accumulation of vague, unestimated tickets. A backlog with hundreds of unrefined tickets isn't a planning tool—it's a wish list. Regular refinement keeps the backlog useful and current.

Refinement saves more time than it costs. Well-refined tickets enable efficient sprint planning, reduce blockers during implementation, and prevent rework from misunderstood requirements. Treat refinement as essential, not optional.

These gotchas are common pitfalls that undermine work management effectiveness. Recognizing them helps teams avoid them and maintain practices that enable delivery rather than create overhead. The goal is effective work management, not perfect process—but avoiding these pitfalls is essential for effectiveness.
