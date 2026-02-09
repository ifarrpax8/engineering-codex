# Gotchas: Repository Governance

## Contents

- [CODEOWNERS Bottlenecks](#codeowners-bottlenecks)
- [Branch Protection Bypasses](#branch-protection-bypasses)
- [Merge Queue Complexity](#merge-queue-complexity)
- [Stale PRs and Review Fatigue](#stale-prs-and-review-fatigue)
- [Monorepo CODEOWNERS Pitfalls](#monorepo-codeowners-pitfalls)
- [Repository Sprawl](#repository-sprawl)
- [Over-Governance](#over-governance)

Repository governance gotchas are common pitfalls that teams encounter when implementing branch protection, CODEOWNERS, and review processes. Understanding these gotchas helps avoid them and design governance that enables rather than blocks development.

## CODEOWNERS Bottlenecks

CODEOWNERS that are too broad or assign ownership to small teams create review bottlenecks. A single team owning everything, or a team of two people owning critical paths, creates delays that slow delivery.

### One Team Owns Everything

When CODEOWNERS assigns all code to one team (`* @company/backend-team`), that team becomes a bottleneck. Every PR requires their review, regardless of whether the change is relevant to their domain. This slows delivery and frustrates developers waiting for reviews.

**Symptoms:**
- PRs sit in review for days waiting for team approval
- Team members are overwhelmed with review requests
- Developers complain about slow reviews

**Solution:**
- Break CODEOWNERS into specific, domain-based patterns
- Assign ownership based on actual domain expertise, not team size
- Use fallback owners (`* @company/engineering-team`) only as last resort, with specific patterns taking precedence

**Example fix:**
```gitignore
# Before: Everything requires backend team review
* @company/backend-team

# After: Specific ownership with fallback
/backend/api/ @company/backend-team
/frontend/ @company/frontend-team
/docs/ @company/docs-team
* @company/engineering-team  # Fallback only
```

### Small Team Owns Critical Paths

When critical paths (security, payments) are owned by a team of 2-3 people, those people become bottlenecks. If they're busy or unavailable, PRs are blocked. This is especially problematic for security-sensitive code that requires expert review.

**Symptoms:**
- Security team of 2 people reviews all security PRs
- PRs blocked when team members are on vacation
- Team members overwhelmed with review volume

**Solution:**
- Expand critical path ownership to include backup reviewers
- Create security champions in other teams who can review non-critical security changes
- Use CODEOWNERS to require security team review only for high-risk changes, not all security-related code

**Example fix:**
```gitignore
# Before: Only security team (2 people)
**/auth/** @company/security-team

# After: Security team + security champions
**/auth/** @company/security-team @company/security-champions
```

### Overly Broad Patterns

Patterns that match too much code create bottlenecks. A pattern like `**/*.ts` matches all TypeScript files, requiring the same team to review everything. This defeats the purpose of CODEOWNERS.

**Symptoms:**
- Pattern matches hundreds of files across multiple domains
- Single team reviews unrelated changes
- CODEOWNERS doesn't provide domain-specific routing

**Solution:**
- Use specific directory patterns instead of file extensions
- Break broad patterns into smaller, domain-specific patterns
- Review CODEOWNERS patterns quarterly to ensure they match code structure

**Example fix:**
```gitignore
# Before: Too broad
**/*.ts @company/typescript-team

# After: Specific directories
/src/payment/**/*.ts @company/payment-team
/src/auth/**/*.ts @company/security-team
/src/utils/**/*.ts @company/platform-team
```

## Branch Protection Bypasses

Branch protection can be bypassed by administrators or through specific workflows. These bypasses are necessary for emergencies but can become crutches that undermine governance if overused.

### Administrator Override

Administrators can bypass branch protection to force-push or merge without reviews. This is necessary for emergencies (fixing corrupted main branch) but becomes a problem when used regularly.

**Symptoms:**
- Administrators frequently bypass protection for "urgent" changes
- Bypasses become routine rather than exceptional
- Developers learn to ask admins to bypass instead of following process

**Solution:**
- Document bypass policy: when bypasses are allowed, who can approve, and audit requirements
- Require bypass justification and audit logs
- If bypasses are frequent, protection rules might be too strict—adjust rules rather than bypassing them
- Review bypass logs quarterly to identify patterns

### Hotfix Branch Bypasses

Some teams create "hotfix" branches that bypass normal protection rules to enable fast emergency fixes. This is reasonable for true emergencies but becomes problematic when hotfixes become the normal workflow.

**Symptoms:**
- Many "hotfix" PRs that aren't actually emergencies
- Hotfix workflow used to avoid normal review process
- Hotfixes accumulate technical debt

**Solution:**
- Define clear hotfix criteria: production incidents, security vulnerabilities, data loss risks
- Require post-hotfix review and documentation
- Limit who can create hotfix branches
- If hotfixes are frequent, normal process might be too slow—optimize normal process instead

### Force Push Workarounds

Developers sometimes work around force push prevention by creating new branches and deleting old ones, or by asking administrators to force push. This indicates that protection rules are creating friction rather than enabling quality.

**Symptoms:**
- Developers frequently need to "fix" branch history
- Complaints about not being able to force push
- Workarounds that bypass protection intent

**Solution:**
- If force push prevention is causing problems, investigate why: are branches diverging? Are developers rebasing incorrectly?
- Provide training on proper git workflows (rebase locally, then push)
- Consider allowing force push on feature branches (not main) if it enables better workflows
- Fix root cause (workflow issues) rather than working around protection

## Merge Queue Complexity

Merge queues (GitHub's feature that serializes merges to prevent conflicts) add complexity that can slow delivery and create confusion. Understanding when merge queues are necessary versus when they add overhead is important.

### Merge Queue Bottlenecks

Merge queues serialize merges, ensuring one PR merges at a time. This prevents conflicts but creates bottlenecks—if one PR has failing CI, all subsequent PRs wait. This can slow delivery significantly.

**Symptoms:**
- PRs wait in merge queue for hours
- One failing PR blocks all other PRs
- Developers frustrated by queue delays

**Solution:**
- Use merge queues only when necessary (high conflict rate, critical main branch)
- Ensure CI is fast and reliable—slow or flaky CI makes merge queues painful
- Consider merge queue only for main branch, not all branches
- Monitor queue length and optimize CI to reduce wait times

### Merge Queue vs Branch Protection

Merge queues and branch protection serve different purposes. Branch protection ensures quality before merge. Merge queues prevent conflicts during merge. Using both adds complexity—ensure the benefits justify the overhead.

**When merge queues help:**
- High conflict rate on main branch
- Critical main branch that must never break
- Need to ensure linear merge order

**When merge queues hurt:**
- Low conflict rate (unnecessary serialization)
- Fast CI (conflicts are rare and easy to resolve)
- Small team (coordination is easier without queues)

### Merge Queue Configuration

Merge queues must be configured correctly. Incorrect configuration (wrong merge method, missing status checks) can cause problems.

**Common issues:**
- Merge queue uses wrong merge method (merge commit instead of squash)
- Merge queue doesn't wait for all required status checks
- Merge queue merges PRs out of order, causing confusion

**Solution:**
- Configure merge queue to use squash merge (if linear history is required)
- Ensure merge queue waits for all required status checks
- Document merge queue behavior so developers understand what to expect

## Stale PRs and Review Fatigue

PRs that sit open for weeks become stale, accumulate conflicts, and are difficult to review. Review fatigue sets in when reviewers are overwhelmed with large, stale PRs.

### Stale PR Symptoms

Stale PRs have multiple problems:
- Code is outdated (conflicts with main)
- Context is lost (why was this change made?)
- Review is difficult (large diff, unclear scope)
- Merge is risky (conflicts, potential regressions)

**Symptoms:**
- PRs open for 2+ weeks
- PRs with many conflicts
- Reviewers avoiding large PRs
- Developers frustrated by review delays

**Solution:**
- Set PR age limits: close PRs inactive for 30+ days (with notification)
- Encourage small PRs that merge quickly
- Break large PRs into smaller, independently mergeable PRs
- Use feature flags to enable incremental delivery

### Review Fatigue

When reviewers are overwhelmed with review requests, review quality suffers. Reviewers skim PRs, miss issues, or delay reviews. This creates a negative cycle: delayed reviews → stale PRs → more difficult reviews → more delays.

**Symptoms:**
- Reviewers have 20+ pending review requests
- Review times increase (days instead of hours)
- Review quality decreases (missed issues, superficial feedback)
- Reviewers avoid reviewing

**Solution:**
- Limit review load: use CODEOWNERS to route PRs to appropriate reviewers, not everyone
- Encourage prompt reviews: set expectations (reviews within 24 hours)
- Rotate reviewers to distribute load
- Use review reminders and automation to prompt timely reviews

### Large PR Review Problems

Large PRs are difficult to review thoroughly. Reviewers struggle to understand full scope, important details get missed, and reviews take hours. This creates review bottlenecks and quality issues.

**Symptoms:**
- PRs with 1000+ lines changed
- Reviewers complaining about PR size
- Important issues missed in reviews
- Reviews taking 4+ hours

**Solution:**
- Enforce PR size limits: reject PRs > 400 lines (require splitting)
- Break large PRs into smaller, focused PRs
- Use feature flags to enable incremental delivery
- Provide PR size guidance in contributing guidelines

## Monorepo CODEOWNERS Pitfalls

Monorepos have unique CODEOWNERS challenges. Shared code, cross-package dependencies, and unclear boundaries create ownership ambiguity.

### Accidental Ownership from Shared Files

In monorepos, shared files (utilities, types, configs) can accidentally trigger CODEOWNERS for teams that don't own the code using those files. A change to a shared utility might require reviews from multiple teams unnecessarily.

**Symptoms:**
- PRs touching shared files require many team reviews
- Teams reviewing code they don't use
- Review bottlenecks from shared file changes

**Solution:**
- Use specific patterns to avoid shared file ownership issues
- Create platform team ownership for truly shared code
- Use CODEOWNERS exceptions for shared utilities
- Document shared file ownership strategy

**Example:**
```gitignore
# Shared utilities owned by platform team (not domain teams)
/shared/utils/** @company/platform-team

# Domain-specific code
/packages/payment/** @company/payment-team
/packages/auth/** @company/security-team
```

### Cross-Package Dependency Reviews

When a PR touches multiple packages, CODEOWNERS might require reviews from multiple teams. This is correct (cross-package changes affect multiple teams) but can create coordination overhead.

**Symptoms:**
- PRs requiring 3+ team approvals
- Coordination delays waiting for all teams
- Teams reviewing code outside their domain

**Solution:**
- Use CODEOWNERS to require reviews only from directly affected teams
- For cross-package changes, require reviews from package owners, not all teams
- Document cross-package change process
- Consider architecture review for large cross-package changes

### Unclear Package Boundaries

In monorepos, package boundaries can be unclear. CODEOWNERS patterns might not match actual package structure, causing incorrect ownership routing.

**Symptoms:**
- CODEOWNERS patterns don't match package structure
- PRs routed to wrong teams
- Ownership gaps (code with no owners)

**Solution:**
- Align CODEOWNERS patterns with actual package structure
- Review CODEOWNERS quarterly to ensure patterns match reality
- Document package structure and ownership
- Use monorepo tools to validate CODEOWNERS patterns

## Repository Sprawl

Without cleanup policies, organizations accumulate hundreds of inactive repositories. This sprawl makes discovery difficult, creates security maintenance burden, and wastes resources.

### Sprawl Symptoms

**Symptoms:**
- Hundreds of repositories, many inactive
- Developers can't find relevant code
- Security updates required for unused repositories
- Maintenance burden for repositories no one uses

**Impact:**
- Discovery difficulty: hard to find relevant repositories
- Security burden: must maintain security for unused repositories
- Resource waste: CI, storage, and tooling costs for unused repositories
- Onboarding confusion: new developers overwhelmed by repository count

### Sprawl Causes

**Common causes:**
- No archival policy for inactive repositories
- Experimental projects never cleaned up
- Deprecated services not archived
- Repository creation without deletion criteria

### Sprawl Prevention

**Solutions:**
- Archival policy: archive repositories inactive for 12+ months
- Repository creation approval: require justification for new repositories
- Regular audits: quarterly review of repository activity
- Clear lifecycle: define repository states (active, maintenance, archived)

**Archival process:**
1. Identify inactive repositories (no commits, PRs, or issues for 12 months)
2. Notify repository owners before archival
3. Archive repositories (read-only, preserved for reference)
4. Update READMEs to explain archival status

## Over-Governance

Too much governance creates bottlenecks that slow delivery without proportional quality benefit. Governance should enable quality and speed, not create unnecessary friction.

### Over-Governance Symptoms

**Symptoms:**
- PRs take days to merge (too many required approvals)
- CI takes hours (too many required checks)
- Developers frustrated by process overhead
- Delivery velocity decreasing despite good code quality

**Impact:**
- Slow delivery: process overhead exceeds value
- Developer frustration: fighting process instead of building features
- Workarounds: developers find ways to bypass governance
- Quality doesn't improve: more process doesn't always mean better quality

### Common Over-Governance Patterns

**Too many required approvals:**
- Requiring 3+ approvals for standard changes
- Requiring approvals from multiple teams for simple changes
- Requiring security review for all changes (not just security-sensitive)

**Too many required checks:**
- Requiring every possible CI check (coverage, linting, type checking, security, performance, etc.)
- Requiring checks that are slow or flaky
- Requiring checks that don't catch real issues

**Too strict requirements:**
- Requiring 100% test coverage (encourages low-quality tests)
- Requiring all linting rules (including stylistic preferences)
- Requiring performance benchmarks for every change

### Finding the Right Balance

**Principles:**
- Governance should enable quality and speed, not create bottlenecks
- Requirements should be based on risk: high-risk changes need more governance
- Automate enforcement: don't rely on manual process compliance
- Measure impact: if governance slows delivery without improving quality, it's too strict

**Balanced approach:**
- 1-2 required approvals (2 for critical paths)
- Essential checks only (tests, linting, security for sensitive code)
- Risk-based requirements (more governance for high-risk changes)
- Fast feedback loops (CI under 10 minutes)

**Regular review:**
- Quarterly governance review: is governance enabling or blocking?
- Measure metrics: PR cycle time, review time, delivery velocity
- Adjust based on data: if metrics show bottlenecks, relax governance
- Solicit developer feedback: are they fighting process or enabled by it?
