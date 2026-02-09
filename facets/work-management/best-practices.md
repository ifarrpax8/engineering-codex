# Best Practices: Work Management

## Contents

- [Write Tickets for Your Future Self](#write-tickets-for-your-future-self)
- [One Ticket, One Concern](#one-ticket-one-concern)
- [Acceptance Criteria Before Implementation](#acceptance-criteria-before-implementation)
- [Keep Tickets Small](#keep-tickets-small)
- [Refine Ahead](#refine-ahead)
- [Use Spikes to Reduce Uncertainty](#use-spikes-to-reduce-uncertainty)
- [Track Technical Debt as Tickets](#track-technical-debt-as-tickets)
- [Link Everything](#link-everything)
- [Sprint Retrospectives Must Produce Action Items](#sprint-retrospectives-must-produce-action-items)
- [Stack-Specific Callouts](#stack-specific-callouts)

Work management best practices are language-agnostic principles that apply regardless of which ticket system or workflow a team uses. These practices emerge from experience and enable effective delivery through disciplined ticket creation, refinement, and execution.

## Write Tickets for Your Future Self

In three months, you should be able to read a ticket and understand what was done and why. This means including context, not just instructions. Link to relevant documentation, Slack threads, design files, or related tickets. A ticket that only says "add user authentication" doesn't explain why authentication was needed, what approach was chosen, or what decisions were made during implementation.

Context makes tickets valuable historical records. When someone asks "why did we build this feature this way?", the ticket should provide the answer. When debugging a production issue, tickets linked to the affected code reveal what was intended and what might have gone wrong.

Include business context: what problem does this solve? Who benefits? What's the user story? This context helps future developers understand the "why" behind the "what." Technical context is also important: what architectural decisions were made? What trade-offs were considered? What dependencies exist?

Comments and refinement notes should capture evolving understanding. As a ticket moves through refinement and implementation, new information emerges. Documenting this information in the ticket (rather than only in Slack or meetings) ensures it's preserved and searchable.

## One Ticket, One Concern

A ticket should represent one coherent piece of work. "Implement invoice download AND fix the user profile page" is two tickets. Splitting them enables independent planning, estimation, and completion. It also enables parallel work if different developers can take different tickets.

Mixing concerns in a single ticket creates problems. If one part is blocked, the entire ticket is blocked. If one part needs rework, the entire ticket needs rework. If one part is ready to deploy but the other isn't, deployment is delayed.

The "one concern" principle applies at all ticket levels. An epic should address one business objective. A story should deliver one user-facing value. A task should accomplish one technical goal. This clarity makes tickets easier to understand, estimate, and complete.

If a ticket feels like it's doing multiple things, split it. It's better to have more, smaller tickets than fewer, larger tickets. Smaller tickets enable faster feedback, easier code review, and more accurate estimation.

## Acceptance Criteria Before Implementation

Define what "done" looks like before writing code. This prevents scope creep and ensures alignment with stakeholders. If acceptance criteria are written after implementation, they tend to describe what was built rather than what was requested.

Acceptance criteria should be specific and testable. "The feature works" isn't specific. "Given a logged-in user, when they click the download button on an invoice detail page, then a PDF file is generated and downloaded" is specific and testable.

Acceptance criteria should be written collaboratively during refinement. Product defines the "what," engineering defines the "how," and QA ensures testability. This collaboration ensures everyone understands what success looks like.

If acceptance criteria change during implementation, that's a signal. Either the original criteria were incomplete (indicating poor refinement) or requirements changed (indicating scope creep). Both should be addressed rather than accepted as normal.

## Keep Tickets Small

Stories should be completable in 1-3 days by one developer. Larger stories are harder to estimate, review, and test. They also increase risk—if a large story encounters unexpected complexity, the entire sprint commitment is at risk.

Small tickets enable faster feedback. A developer completes a 2-day story, opens a PR, gets review feedback, and deploys—all within a few days. This fast cycle enables course correction if something is wrong. A 10-day story doesn't get feedback until it's mostly complete, making changes expensive.

Small tickets are easier to review. A PR for a 2-day story is manageable. A PR for a 10-day story is overwhelming. Reviewers struggle to understand the full scope, and important details get missed.

Small tickets enable more accurate estimation. Estimating a 2-day story is easier than estimating a 10-day story. Uncertainty compounds over time—a 10-day story has more unknowns than a 2-day story.

If a story is too large, break it down. Look for vertical slices of value that can be delivered independently. A story to "implement user authentication" might break into "login with email/password," "password reset flow," and "session management." Each can be delivered independently and provides value.

## Refine Ahead

Maintain 1-2 sprints of refined tickets in the backlog. This prevents sprint planning from becoming a refinement session and ensures developers always have clear work to start. When a developer finishes a ticket, they should be able to pick up the next refined ticket without waiting for clarification.

Refinement should be an ongoing process, not a single meeting. As new tickets are created or priorities change, they should be refined. This continuous refinement prevents backlog decay and ensures tickets are always ready.

Refinement should involve the right people. Technical tickets might need only engineering input. User-facing tickets need product and design input. Involving the right people ensures tickets are complete and accurate.

Refined tickets should meet Definition of Ready: clear acceptance criteria, identified dependencies, technical approach documented, questions answered. If a ticket doesn't meet Definition of Ready, it's not refined.

Regular refinement prevents the accumulation of vague, unestimated tickets. A backlog with hundreds of unrefined tickets isn't a planning tool—it's a wish list. Regular refinement keeps the backlog useful and current.

## Use Spikes to Reduce Uncertainty

Don't estimate or commit to work you don't understand. Create a spike first, time-box it, and use the findings to write informed stories. A spike that investigates "OpenSearch vs PostgreSQL FTS" produces benchmarks, recommendations, and implementation notes that inform story creation.

Spikes should be time-boxed (typically 1-3 days) to prevent scope creep. A spike that drags on becomes a research project rather than a risk-reduction activity. If a spike exceeds its time box, it should produce interim findings and a recommendation for whether to continue.

Spikes should produce actionable outputs: findings, recommendations, and next steps. A spike without a recommendation hasn't completed its purpose. The recommendation should inform story creation—what approach should we take? What stories need to be created?

Spikes enable informed estimation. After a spike investigates a technical approach, stories can be estimated based on understanding rather than guesswork. This reduces estimation risk and improves sprint planning accuracy.

Some teams use spikes for product research as well as technical research. A spike might investigate user needs, market research, or design approaches. The same principles apply: time-box the research, produce findings and recommendations, use outputs to inform story creation.

## Track Technical Debt as Tickets

Don't let refactoring and technical debt live only in developers' heads. Create tickets, link them to the affected area, and prioritize them alongside feature work. This makes technical debt visible and manageable.

Technical debt tickets should be specific: "refactor payment service to use dependency injection" is specific. "improve code quality" is vague. Specific tickets can be estimated, planned, and completed. Vague tickets languish in the backlog.

Technical debt tickets should be linked to the affected area. If a ticket addresses debt in the invoice service, link it to that service or related stories. This traceability helps prioritize: if we're planning to extend the invoice service, we should address its technical debt first.

Technical debt should be prioritized alongside feature work. If technical debt is never prioritized, it accumulates until it blocks feature work. Regular prioritization ensures debt is addressed before it becomes critical.

Some teams allocate a percentage of sprint capacity to technical debt (e.g., 20%). This ensures debt is addressed consistently rather than only when it becomes blocking. The percentage depends on team context and debt levels.

## Link Everything

Tickets should be linked to related work: tickets to PRs, PRs to deployments, epics to stories, stories to subtasks. This traceability makes it possible to answer "why was this change made?" months later.

Linking happens through branch names, commit messages, and PR descriptions. Branch names should include ticket IDs. Commit messages should reference tickets. PR descriptions should link to tickets and summarize changes.

Linking enables automated tracking. When a PR is merged, the ticket can automatically move to "Done." When a deployment occurs, tickets can be automatically linked to the release. This automation reduces manual overhead and ensures accuracy.

Linking also enables reporting. Which tickets are in the current release? Which epics are making progress? Which stories introduced bugs? These questions are answerable when everything is linked.

Some teams use deployment tickets that aggregate all tickets in a release. This provides a single place to see what changed and enables rollback planning. Individual tickets are still linked to the deployment ticket for traceability.

## Sprint Retrospectives Must Produce Action Items

A retrospective without action items is just a venting session. Action items should be specific, assigned, and tracked as tickets. Reviewing action item completion in the next retrospective ensures accountability.

Action items should target root causes, not symptoms. If the problem is "code review bottleneck," the action item shouldn't be "review code faster." It should be "investigate why reviews take so long" or "reduce PR size" or "increase review capacity." Root cause analysis ensures action items address the right problems.

Action items should be reviewed in the next retrospective. Did we complete them? Did they help? If action items aren't being completed, the retrospective process isn't effective. If completed action items don't improve outcomes, they might not address the right problems.

Some teams track retrospective themes over time. Are the same problems appearing repeatedly? This indicates persistent issues that need deeper investigation. A problem that appears in every retrospective for three months needs a different approach.

Retrospectives should be safe spaces for honest feedback. If team members don't feel safe raising problems, retrospectives become perfunctory. Creating psychological safety enables real improvement.

## Stack-Specific Callouts

While work management principles are universal, different ticket systems have specific features that enable best practices.

### Jira

Use structured templates with panels for consistent ticket formatting. Panels for "Overview," "Refinement Notes," and "Success Criteria" ensure all tickets capture the same information in the same way. This consistency makes tickets easier to read and review.

Link tickets to Confluence pages for detailed specifications. Jira tickets should summarize key information, but detailed requirements, designs, or technical specs can live in Confluence with links from tickets. This keeps tickets focused while preserving detail.

Use JQL (Jira Query Language) for backlog queries and reporting. JQL enables complex queries like "show me all stories in Epic X that are missing acceptance criteria" or "show me all tickets that have been in In Progress for more than 5 days." These queries reveal process health and enable targeted improvements.

Use custom fields judiciously. Custom fields can capture important information, but too many custom fields create maintenance burden and reduce adoption. Only add custom fields that provide genuine value.

### GitHub Issues

Use issue templates for consistent formatting. Templates ensure all issues capture the same information (description, acceptance criteria, technical notes) in the same structure. This consistency makes issues easier to read and review.

Use labels for categorization. Labels like "bug," "feature," "tech-debt," "documentation" enable filtering and reporting. Consistent label usage makes the issue list more useful.

Use milestones for sprint/release tracking. Milestones group issues by sprint or release, enabling progress tracking and planning. Link milestones to releases for deployment traceability.

Use Projects (v2) for board views. Projects provide Kanban-style boards with custom fields and filtering. This enables workflow visualization similar to Jira boards.

### Azure Boards

Use work item templates for consistency. Templates ensure all work items capture the same information in the same structure. This consistency makes work items easier to read and review.

Link to Azure Repos for code traceability. Azure Boards integrates with Azure Repos, enabling automatic linking between work items and code changes. This traceability supports change management and incident response.

Use queries for backlog health monitoring. Queries can identify stale work items, missing acceptance criteria, or epics without linked stories. These queries reveal process health and enable targeted improvements.

Use iteration paths for sprint management. Iteration paths group work items by sprint, enabling capacity planning and progress tracking. Link iterations to releases for deployment traceability.

These stack-specific practices complement universal best practices. The principles remain the same regardless of tooling, but each tool has features that enable effective work management when used well.
