# Best Practices: Repository Governance

## Contents

- [Essential Repository Files](#essential-repository-files)
- [Conventional Commits](#conventional-commits)
- [Small, Focused PRs](#small-focused-prs)
- [Review Requirements](#review-requirements)
- [Linear History](#linear-history)
- [Repository Naming Conventions](#repository-naming-conventions)
- [Inactive Repository Cleanup](#inactive-repository-cleanup)
- [CODEOWNERS Best Practices](#codeowners-best-practices)
- [Branch Protection Configuration](#branch-protection-configuration)

Repository governance best practices are principles that apply regardless of specific tools or organizational structure. These practices emerge from experience and enable effective collaboration, code quality, and developer productivity through consistent conventions and automated enforcement.

## Essential Repository Files

Every repository should include essential files that enable collaboration, compliance, and consistency. These files provide structure, documentation, and automation that reduce friction and accelerate onboarding.

### README.md

A README should explain what the repository does, how to set it up, how to run tests, and how to contribute. A good README enables developers to start working immediately without asking questions or reverse-engineering the codebase.

**Required sections:**
- **Purpose**: What does this repository do? What problem does it solve?
- **Setup**: How do I get this running locally? What dependencies are needed?
- **Testing**: How do I run tests? What's the test structure?
- **Contributing**: How do I contribute? What are the conventions?
- **Architecture**: High-level architecture overview (for complex repositories)

**Example README structure:**
```markdown
# Service Name

Brief description of what this service does.

## Setup

1. Install dependencies: `npm install`
2. Configure environment: Copy `.env.example` to `.env`
3. Run migrations: `npm run migrate`
4. Start server: `npm start`

## Testing

Run tests: `npm test`
Run linting: `npm run lint`
Run type checking: `npm run type-check`

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.
```

### LICENSE

Every repository should have a LICENSE file that specifies usage rights. Open source repositories need explicit licenses. Internal repositories should specify internal-only usage. Without a license, usage rights are ambiguous.

Common licenses:
- **MIT**: Permissive, allows commercial use
- **Apache 2.0**: Permissive with patent protection
- **GPL**: Copyleft, requires derivative works to be open source
- **Proprietary**: Internal-only, no external use

### CODEOWNERS

Repositories with multiple contributors should have a CODEOWNERS file that defines ownership. CODEOWNERS automatically routes PRs to domain experts, ensuring appropriate review.

**Example CODEOWNERS:**
```gitignore
# Global owners (fallback)
* @company/engineering-team

# Team-based ownership
/backend/ @company/backend-team
/frontend/ @company/frontend-team
/docs/ @company/docs-team

# Path-based ownership (security-sensitive)
**/auth/** @company/security-team
**/payment/** @company/payment-team @company/security-team

# Architecture-level ownership
/api/ @company/api-team
/ui/ @company/ui-team

# Specific file ownership
/package.json @company/platform-team
```

CODEOWNERS should use teams, not individuals. Team ownership provides redundancy and enables knowledge sharing. Individual ownership creates single points of failure.

### .gitignore

A `.gitignore` file prevents committing sensitive files, build artifacts, and dependencies. Language-specific ignores (`.gitignore` for Node.js, Python, etc.) should be included.

**Common patterns:**
```gitignore
# Dependencies
node_modules/
vendor/
__pycache__/

# Build artifacts
dist/
build/
*.class

# Environment files
.env
.env.local
*.pem
*.key

# IDE files
.vscode/
.idea/
*.swp
```

### CI Configuration

Every repository should have CI configuration that runs tests, linting, and type checking. CI ensures code quality before merge and provides fast feedback.

**Example GitHub Actions workflow:**
```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm test
```

## Conventional Commits

Conventional commits provide consistent commit message format that enables automated tooling and clear history. The format is: `type(scope): description`.

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Example commits:**
```
feat(auth): add OIDC authentication
fix(payment): resolve race condition in charge processing
docs(api): update endpoint documentation
refactor(utils): extract common validation logic
```

Conventional commits enable automated changelog generation, semantic versioning, and release notes. Tools like `semantic-release` use conventional commits to automate releases.

Commit messages should be clear and descriptive. "Fix bug" is not helpful. "Fix race condition in payment processing that caused duplicate charges" is helpful. Good commit messages explain what changed and why.

## Small, Focused PRs

PRs should be small and focused on a single concern. Small PRs are easier to review, test, and merge. Large PRs create bottlenecks, increase risk, and delay feedback.

**PR size guidelines:**
- **Ideal**: < 200 lines changed
- **Acceptable**: 200-400 lines changed
- **Too large**: > 400 lines changed (should be split)

Small PRs enable fast review cycles. A 200-line PR can be reviewed in 30 minutes. A 2000-line PR takes hours to review, and important details get missed.

Small PRs reduce merge conflict risk. Long-lived branches accumulate conflicts. Small PRs merge quickly, reducing conflict opportunities.

Small PRs enable incremental delivery. A large feature can be delivered incrementally through multiple small PRs. Each PR delivers value and enables feedback.

**When PRs are too large:**
- Break into smaller, independently valuable PRs
- Use feature flags to enable incomplete features
- Extract shared code into separate PRs
- Split by architectural layer (API, UI, tests)

## Review Requirements

Review requirements ensure code quality and knowledge sharing. However, requirements must balance quality with velocity—too many required reviews create bottlenecks.

### Standard Review Requirements

**Default**: 1 required approval for standard changes. This ensures code is reviewed without creating bottlenecks. Most changes don't need multiple reviewers.

**Critical paths**: 2 required approvals for security-sensitive, payment-related, or data-access code. CODEOWNERS can specify these paths automatically. This ensures expert review for high-risk changes.

**Avoid**: Requiring 3+ approvals for standard changes. This creates bottlenecks without proportional quality benefit. Multiple approvals are justified only for critical paths.

### CODEOWNERS Review Requirements

CODEOWNERS should specify owners for critical paths. Security-sensitive code should require security team approval. Payment code should require payment team approval. This automatic routing ensures expert review.

**Example CODEOWNERS for critical paths:**
```gitignore
# Security team must review authentication changes
**/auth/** @company/security-team

# Payment team and security team must review payment changes
**/payment/** @company/payment-team @company/security-team

# Data team must review data access changes
**/database/** @company/data-team
```

CODEOWNERS enables domain-specific review requirements without manual PR routing. Reviewers are automatically requested based on changed paths.

### Review Best Practices

Reviewers should provide constructive feedback. "This is wrong" is not helpful. "Consider using X instead of Y because Z" is helpful. Good reviews explain reasoning and suggest improvements.

Reviewers should approve promptly. Delayed reviews slow delivery and frustrate developers. If reviewers are busy, CODEOWNERS should include backup reviewers or teams.

Reviewers should focus on correctness, clarity, and maintainability. Nitpicks about style can be handled by automated linting. Reviews should catch logic errors, architectural issues, and maintainability problems.

## Linear History

Linear history (squash merge or rebase) creates clean git log that's easier to navigate, bisect, and rollback. Merge commits create branching history that's cluttered and difficult to work with.

### Squash Merge (Recommended)

Squash merge combines all PR commits into a single commit on main. This creates linear history while preserving PR context (description, comments, linked tickets).

**Benefits:**
- Clean, linear history
- PR context provides detail (more valuable than individual commits)
- Simple workflow (no rebase required)

**Trade-offs:**
- Loses individual commit context (acceptable—PR context is more valuable)
- Commit message should summarize PR, not individual commits

Squash merge is the default recommendation. It provides clean history without requiring developer discipline or tooling support.

### Rebase Merge

Rebase merge replays PR commits onto main, preserving individual commits. This maintains commit context but requires force-push to update branches, which branch protection typically prevents.

**Benefits:**
- Preserves individual commit context
- Linear history

**Trade-offs:**
- Requires developer discipline (rebase locally before opening PR)
- More complex workflow

Rebase merge is useful when commit-level history is important (compliance, detailed change tracking). Most teams prefer squash merge's simplicity.

### Merge Commits (Avoid)

Merge commits preserve branch structure but create cluttered history. A main branch with hundreds of merge commits is difficult to navigate. Avoid merge commits unless there's a specific reason to preserve branch structure.

## Repository Naming Conventions

Consistent repository naming enables discovery and understanding. Naming conventions should reflect organizational structure and repository purpose.

### Naming Patterns

**Bounded context prefix**: `{bounded-context}-{service}`
- Example: `finance-invoice-service`, `order-payment-handler`
- Enables grouping by domain

**Service type suffix**: `{name}-{type}`
- Example: `auth-api`, `payment-worker`, `invoice-ui`
- Clarifies repository purpose

**Kebab-case**: Use kebab-case (lowercase with hyphens) for consistency
- Example: `user-management-service` (not `userManagementService` or `user_management_service`)

### Naming Guidelines

Names should be descriptive but concise. `finance-invoice-pdf-generation-service` is too long. `finance-invoice-service` is better.

Names should avoid abbreviations unless they're widely understood. `fin-inv-svc` is unclear. `finance-invoice-service` is clear.

Names should reflect current purpose. If a repository's purpose changes, consider renaming rather than keeping a misleading name.

## Inactive Repository Cleanup

Repositories that are inactive should be archived to prevent sprawl and reduce maintenance burden. Clear archival policies ensure consistent cleanup.

### Archival Criteria

**Archive repositories inactive for 12+ months**: Repositories with no commits, PRs, or issues for 12 months should be archived. This prevents sprawl while preserving access.

**Archive deprecated services**: When services are deprecated, their repositories should be archived. Deprecated services don't need active maintenance but should remain accessible for reference.

**Archive experimental projects**: Experimental projects that didn't become production should be archived. Keep them for reference but don't maintain them.

### Archival Process

**Archive, don't delete**: Archived repositories are read-only but remain accessible. Deletion loses history and breaks references. Archival preserves access while reducing maintenance.

**Update README**: Archived repositories should have READMEs explaining archival status and pointing to replacements (if any). This helps developers understand why repositories are archived.

**Notify teams**: Before archiving, notify repository owners and teams. They might want to keep repositories active or migrate code elsewhere.

### Repository Lifecycle

**Active**: Regular commits, PRs, and issues. Full maintenance and governance.

**Maintenance**: Infrequent commits (security updates, dependency updates). Reduced governance but still maintained.

**Archived**: Read-only, no active development. Preserved for reference.

Clear lifecycle policies ensure repositories are managed appropriately at each stage.

## CODEOWNERS Best Practices

CODEOWNERS files should be specific, maintainable, and effective. Following best practices ensures CODEOWNERS enables rather than blocks development.

### Use Teams, Not Individuals

Team ownership provides redundancy and enables knowledge sharing. Individual ownership creates single points of failure—if someone is unavailable, reviews are blocked.

**Good:**
```gitignore
/backend/ @company/backend-team
```

**Bad:**
```gitignore
/backend/ @john-doe @jane-smith
```

### Keep Patterns Specific

Broad patterns create ownership bottlenecks. Specific patterns enable targeted review.

**Good:**
```gitignore
/src/payment/** @company/payment-team
/src/auth/** @company/security-team
```

**Bad:**
```gitignore
* @company/engineering-team
```

If patterns are too broad, break them into smaller, more specific patterns.

### Review CODEOWNERS Regularly

As teams change, code moves, and ownership evolves, CODEOWNERS becomes stale. Quarterly audits ensure ownership matches reality.

**Audit checklist:**
- Do all teams/users exist?
- Do patterns match current code structure?
- Are there ownership gaps (code with no owners)?
- Are there overly broad patterns creating bottlenecks?

### Document Ownership Rationale

Comments explaining why teams own paths help future maintainers.

**Example:**
```gitignore
# Payment team owns payment processing for PCI compliance requirements
/src/payment/** @company/payment-team @company/security-team

# Security team owns authentication for security review requirements
/src/auth/** @company/security-team
```

## Branch Protection Configuration

Branch protection should be configured consistently across repositories. Automated configuration ensures consistency and reduces manual overhead.

### GitHub CLI Configuration

**Example branch protection configuration:**
```bash
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

### Terraform Configuration

**Example Terraform configuration:**
```hcl
resource "github_branch_protection" "main" {
  repository_id = github_repository.example.node_id
  
  pattern          = "main"
  enforce_admins   = true
  
  required_status_checks {
    strict   = true
    contexts = ["ci", "lint", "test"]
  }
  
  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
  }
}
```

### Configuration Standards

**Standard protection rules:**
- Require pull request reviews (1-2 approvals)
- Require status checks to pass
- Require branches to be up to date
- Enforce linear history (squash merge)
- Prevent force pushes
- Restrict who can push (if needed)

Configuration should be automated via scripts, Terraform, or GitHub API to ensure consistency across repositories.
