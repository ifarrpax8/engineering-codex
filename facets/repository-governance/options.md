# Options: Repository Governance Decision Matrix

## Contents

- [Branch Strategy Options](#branch-strategy-options)
  - [Trunk-Based Development (Recommended)](#trunk-based-development-recommended)
  - [GitHub Flow](#github-flow)
  - [GitFlow](#gitflow)
- [Monorepo vs Multi-Repo Options](#monorepo-vs-multi-repo-options)
  - [Monorepo](#monorepo)
  - [Multi-Repo](#multi-repo)
- [Merge Strategy Options](#merge-strategy-options)
  - [Squash Merge (Recommended)](#squash-merge-recommended)
  - [Rebase Merge](#rebase-merge)
  - [Merge Commit](#merge-commit)
- [Review Requirement Options](#review-requirement-options)
  - [One Required Approval (Default)](#one-required-approval-default)
  - [Two Required Approvals (Critical Paths)](#two-required-approvals-critical-paths)
  - [CODEOWNERS-Based Requirements](#codeowners-based-requirements)
- [Evaluation Criteria](#evaluation-criteria)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

Repository governance involves multiple decisions: branch strategies, repository structure, merge approaches, and review requirements. Different options suit different team contexts, release cadences, and risk tolerances. This decision matrix evaluates options and provides guidance for selection.

## Branch Strategy Options

### Trunk-Based Development (Recommended)

**Description**: Main branch is always deployable. Developers create short-lived feature branches (hours to days), open PRs, get review, and merge to main. Main is continuously integrated and deployed. Incomplete features use feature flags.

**Strengths**:
- Maximum feedback speed: changes integrate quickly, enabling fast iteration
- Minimal merge conflicts: short-lived branches prevent divergence
- Simple workflow: one main branch, no complex branch management
- Continuous integration: main is always tested and deployable
- Fast deployment: changes merge and deploy quickly

**Weaknesses**:
- Requires discipline: main must always be deployable, incomplete features need flags
- Feature flag overhead: flags must be managed and cleaned up
- Small PRs required: large PRs create bottlenecks
- Fast CI required: slow CI slows the feedback loop

**Best For**:
- Teams with continuous deployment or frequent releases
- Teams with fast CI (< 10 minutes)
- Teams that can maintain deployable main branch
- Teams comfortable with feature flags

**Avoid When**:
- Releases require extensive coordination or regulatory approval
- Teams can't maintain deployable main branch
- CI is slow (> 30 minutes) and can't be optimized
- Feature flags aren't feasible

**Recommendation**: Default choice for most teams. Trunk-based development maximizes velocity and feedback speed with minimal overhead.

### GitHub Flow

**Description**: Extends trunk-based development with explicit release branches. Main is always deployable. Release branches (`release/v1.2.0`) prepare releases, enable final testing, and hotfixes. After release, branch merges back to main and is deleted.

**Strengths**:
- Release coordination: enables final testing and hotfixes without blocking main
- Parallel work: release preparation doesn't block new development
- Simpler than GitFlow: less branch management overhead
- Maintains trunk-based benefits: fast feedback, minimal conflicts

**Weaknesses**:
- Release branch overhead: branches must be maintained and merged back
- Merge complexity: release branches must merge back to main correctly
- Less suitable for continuous deployment: release branches add delay

**Best For**:
- Teams with regular releases (weekly, bi-weekly, monthly) that need coordination
- Teams that need release branches for testing or approval processes
- Teams that want release coordination without GitFlow complexity

**Avoid When**:
- Continuous deployment makes release branches unnecessary
- Release process is simple enough for direct main deployment
- Teams prefer maximum simplicity (use trunk-based instead)

**Recommendation**: Escape hatch for teams that need release coordination. Use when trunk-based development doesn't support release process requirements.

### GitFlow

**Description**: Uses multiple long-lived branches: `main` (production), `develop` (integration), `feature/*` (features), `release/*` (releases), and `hotfix/*` (hotfixes). Provides clear separation between development, release preparation, and production.

**Strengths**:
- Clear structure: explicit phases for development, release, and production
- Release management: supports complex release processes with extensive testing
- Hotfix support: dedicated hotfix branches enable emergency fixes
- Suits regulated environments: clear separation supports compliance requirements

**Weaknesses**:
- Significant overhead: multiple branches to maintain and merge
- Merge complexity: merges between main and develop create conflict opportunities
- Delayed integration: integration happens on develop, not main, delaying feedback
- Slower velocity: feature branches live longer, creating more conflicts

**Best For**:
- Teams with complex release processes requiring extensive testing
- Regulated environments requiring clear change management
- Teams with multi-team release coordination needs
- Teams that truly need the structure (not just prefer it)

**Avoid When**:
- Release process is simple (trunk-based or GitHub Flow is sufficient)
- Teams want maximum velocity (GitFlow overhead slows delivery)
- Continuous deployment makes release branches unnecessary
- Teams can't maintain multiple branches effectively

**Recommendation**: Avoid unless release complexity truly requires it. Most teams don't need GitFlow's structure—trunk-based development or GitHub Flow provides sufficient organization with less overhead.

## Monorepo vs Multi-Repo Options

### Monorepo

**Description**: Single repository containing multiple packages, services, or applications. All code lives in one repository with shared tooling, dependencies, and governance.

**Strengths**:
- Atomic changes: cross-cutting changes can be made atomically across packages
- Shared code: easy to share utilities, types, and libraries
- Consistent tooling: one set of CI, linting, and testing tools
- Easier refactoring: large refactors can span multiple packages safely
- Simplified dependency management: packages can depend on each other directly

**Weaknesses**:
- Scale challenges: large monorepos can be slow (CI, tooling, discovery)
- Ownership complexity: CODEOWNERS becomes critical for ownership clarity
- All-or-nothing access: developers need access to entire repository
- Tooling requirements: requires monorepo-aware tooling (Nx, Turborepo, Bazel)

**Best For**:
- Tightly coupled code that changes together
- Need for atomic cross-cutting changes
- Shared libraries and utilities across packages
- Teams comfortable with monorepo tooling

**Avoid When**:
- Services are independent with different release cadences
- Clear service boundaries make multi-repo structure clearer
- Teams prefer independent repositories
- Monorepo tooling overhead exceeds benefits

**Criteria for Choosing**:
- Code changes together frequently → Monorepo
- Services are independent → Multi-repo
- Need atomic cross-cutting changes → Monorepo
- Different release cadences → Multi-repo

### Multi-Repo

**Description**: Separate repository for each service, package, or application. Each repository has independent governance, CI, and release cycles.

**Strengths**:
- Clear boundaries: each repository has clear ownership and purpose
- Independent releases: services can release independently
- Access control: developers need access only to relevant repositories
- Simpler at small scale: easier to understand and navigate
- Technology flexibility: different repositories can use different stacks

**Weaknesses**:
- Cross-repo changes: require multiple PRs and coordination
- Code sharing: harder to share code across repositories
- Inconsistency risk: repositories can diverge in structure and tooling
- Dependency management: cross-repo dependencies require versioning

**Best For**:
- Independent services with clear boundaries
- Different release cadences or teams
- Need for independent access control
- Teams prefer repository independence

**Avoid When**:
- Code changes together frequently (monorepo enables atomic changes)
- Heavy code sharing would require many cross-repo dependencies
- Teams want maximum consistency (monorepo enforces it)

**Criteria for Choosing**:
- Independent services → Multi-repo
- Code changes together → Monorepo
- Different release cadences → Multi-repo
- Heavy code sharing → Monorepo

**Recommendation**: Choose based on code coupling and change patterns, not team preferences. Tightly coupled code → monorepo. Independent services → multi-repo.

## Merge Strategy Options

### Squash Merge (Recommended)

**Description**: Combines all PR commits into a single commit on the target branch. Creates linear history with PR context providing detail.

**Strengths**:
- Clean, linear history: easy to navigate and understand
- Simple workflow: no rebase required, works with branch protection
- PR context: PR description, comments, and linked tickets provide detail
- Consistent: every PR becomes one commit, predictable structure

**Weaknesses**:
- Loses individual commit context: individual commit messages are squashed
- Commit message must summarize PR: can't rely on individual commit messages

**Best For**:
- Teams that want clean, linear history
- Teams using PRs as primary documentation (PR context is sufficient)
- Teams that prefer simplicity over commit-level detail

**Recommendation**: Default choice. Provides clean history without requiring developer discipline or complex workflows.

### Rebase Merge

**Description**: Replays PR commits onto target branch, preserving individual commits. Maintains commit context but requires force-push to update branches.

**Strengths**:
- Preserves commit context: individual commits remain in history
- Linear history: clean git log without merge commits
- Detailed history: commit-level detail for compliance or tracking

**Weaknesses**:
- Requires discipline: developers must rebase locally before opening PRs
- Force-push issues: branch protection typically prevents force-push
- More complex: requires developer knowledge of rebase workflow

**Best For**:
- Teams that need commit-level history (compliance, detailed tracking)
- Teams comfortable with rebase workflow
- Teams that value commit context over PR context

**Recommendation**: Use when commit-level history is critical. Most teams prefer squash merge's simplicity.

### Merge Commit

**Description**: Preserves branch structure with a merge commit. Creates branching history that shows feature completion.

**Strengths**:
- Preserves branch structure: shows feature branches in history
- Simple: default Git behavior, no special workflow
- Feature tracking: merge commits can indicate feature completion

**Weaknesses**:
- Cluttered history: branching history is harder to navigate
- More complex git log: harder to bisect and understand
- Less common: most teams prefer linear history

**Best For**:
- Teams that want to preserve branch structure
- Teams that don't care about linear history
- Legacy workflows that can't change

**Recommendation**: Avoid unless there's a specific reason to preserve branch structure. Most teams prefer linear history (squash or rebase).

## Review Requirement Options

### One Required Approval (Default)

**Description**: PRs require one approval before merge. Ensures code is reviewed without creating bottlenecks.

**Strengths**:
- Fast review cycles: one approval is quick to obtain
- No bottlenecks: doesn't create review delays
- Sufficient for most changes: catches issues without overhead

**Weaknesses**:
- Might miss issues: single reviewer might not catch all problems
- Less knowledge sharing: fewer reviewers means less team learning

**Best For**:
- Standard changes that don't require expert review
- Teams with good code quality and trust
- Fast-moving teams that prioritize velocity

**Recommendation**: Default for standard changes. Provides quality assurance without bottlenecks.

### Two Required Approvals (Critical Paths)

**Description**: PRs require two approvals before merge. Provides additional review for high-risk changes.

**Strengths**:
- Higher quality: two reviewers catch more issues
- Knowledge sharing: more reviewers means more team learning
- Risk mitigation: appropriate for high-risk changes

**Weaknesses**:
- Slower: requires two approvals, can create delays
- Bottleneck risk: if reviewers are busy, PRs wait longer

**Best For**:
- Security-sensitive code (authentication, authorization)
- Payment processing and financial code
- Data access and database changes
- Critical infrastructure changes

**Recommendation**: Use for critical paths via CODEOWNERS. Don't require two approvals for all changes—only high-risk paths.

### CODEOWNERS-Based Requirements

**Description**: CODEOWNERS automatically routes PRs to domain experts based on changed paths. Review requirements adapt to change context.

**Strengths**:
- Automatic routing: ensures expert review without manual assignment
- Context-aware: requirements adapt to what changed
- Scalable: works across many repositories and teams

**Weaknesses**:
- Requires maintenance: CODEOWNERS must be kept current
- Can create bottlenecks: if CODEOWNERS patterns are too broad

**Best For**:
- Organizations with multiple teams and domains
- Need for domain-specific expert review
- Large codebases with clear ownership boundaries

**Recommendation**: Use CODEOWNERS to route reviews automatically. Combine with branch protection to enforce requirements.

## Evaluation Criteria

When choosing repository governance options, consider:

**Velocity**: How quickly can changes be merged and deployed? Trunk-based development maximizes velocity. GitFlow slows delivery.

**Quality**: How well does governance ensure code quality? CODEOWNERS routes expert reviews. Required status checks prevent broken code.

**Complexity**: How much overhead does governance create? Trunk-based development is simple. GitFlow is complex.

**Risk Tolerance**: How much risk can the team accept? Critical paths need more governance. Standard changes need less.

**Team Size**: How does governance scale? Small teams need minimal governance. Large teams need structured governance.

**Release Cadence**: How frequently are releases? Continuous deployment suits trunk-based. Monthly releases might need GitHub Flow.

## Recommendation Guidance

### Default Recommendation: Trunk-Based Development

**Branch Strategy**: Trunk-based development with short-lived feature branches
**Merge Strategy**: Squash merge for linear history
**Review Requirements**: 1 approval for standard changes, 2 for critical paths (via CODEOWNERS)
**Repository Structure**: Choose based on code coupling (monorepo for coupled code, multi-repo for independent services)

This combination maximizes velocity and feedback speed while maintaining quality through CODEOWNERS routing and branch protection.

### When to Deviate

**Use GitHub Flow** when releases need coordination but not GitFlow complexity.

**Use GitFlow** only when release complexity truly requires it (regulatory requirements, extensive testing, multi-team coordination).

**Use Rebase Merge** when commit-level history is critical (compliance, detailed tracking).

**Require 2 Approvals** for all changes only if team size and review capacity support it without creating bottlenecks.

## Synergies

Repository governance synergizes with other facets:

**CI/CD**: Branch protection integrates with CI status checks. Fast CI enables trunk-based development. Slow CI makes any branch strategy painful.

**Work Management**: Branch naming tied to tickets enables traceability. PR templates link to work items. Review workflows align with ticket workflows.

**Testing**: PR validation gates ensure tests pass before merge. Test coverage requirements enforce quality. Fast tests enable rapid feedback loops.

**Security**: CODEOWNERS routes security-sensitive changes to security experts. Branch protection prevents unauthorized changes. Required security scans catch vulnerabilities before merge.

## Evolution Triggers

Repository governance should evolve as teams and organizations grow:

**Team Growth**: Small teams (1-5) need minimal governance. Medium teams (5-20) need CODEOWNERS. Large teams (20+) need comprehensive governance.

**Repository Growth**: Few repositories need manual governance. Many repositories need templates and automation.

**Release Complexity**: Simple releases suit trunk-based development. Complex releases might need GitHub Flow or GitFlow.

**Security Requirements**: Increased security requirements need stricter CODEOWNERS and branch protection.

**Velocity Issues**: If governance slows delivery, relax requirements. If quality suffers, tighten requirements.

**Compliance Needs**: Regulatory requirements might need GitFlow structure or stricter review requirements.

Regular governance reviews (quarterly) ensure governance matches current needs. Don't let governance become outdated—evolve it as teams and requirements change.
