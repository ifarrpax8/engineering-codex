# Testing: Repository Governance

## Contents

- [Testing Branch Protection](#testing-branch-protection)
- [PR Validation Gates](#pr-validation-gates)
- [Pre-commit Hooks vs CI Checks](#pre-commit-hooks-vs-ci-checks)
- [Automated Repository Compliance](#automated-repository-compliance)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

Repository governance testing ensures that protection rules, CODEOWNERS, and quality gates work as intended. This includes validating branch protection enforcement, PR validation workflows, and automated compliance checking. Testing governance prevents configuration drift, ensures security controls are effective, and maintains code quality standards.

## Testing Branch Protection

Branch protection rules must be tested to ensure they actually prevent unsafe merges. Manual testing is insufficient—automated tests validate protection rules across all repositories and catch configuration drift.

### Protection Rule Validation

Test that required reviews actually block merges. Create a test PR without required approvals and verify it cannot be merged. Test that the required number of approvals (1, 2, etc.) is enforced. Test that CODEOWNERS approvals satisfy requirements.

Test that required status checks block merges. Create a PR with failing CI and verify it cannot be merged. Test that all required checks must pass, not just some. Test that optional checks don't block merges.

Test that force push prevention works. Attempt to force push to a protected branch and verify it's rejected. Test that administrator override works when needed (but document and audit overrides).

Test linear history requirements. Attempt to merge with a merge commit when linear history is required and verify it's rejected. Test that squash merge is allowed when linear history is required.

### Protection Rule Coverage

Test protection rules across all repositories. A script that checks every repository's branch protection ensures consistency. Repositories missing protection rules should be flagged for configuration.

Test that protection rules match organizational standards. If the standard is "main branch requires 2 approvals," verify all repositories follow this standard. Exceptions should be documented and justified.

Test protection rule changes. When protection rules are updated, verify the changes work as intended. A change that relaxes requirements should be reviewed for security impact. A change that tightens requirements should be communicated to teams.

### Protection Rule Regression Testing

Protection rules can regress when repositories are reconfigured or migrated. Automated tests that validate protection rules prevent regression. These tests should run in CI and alert on failures.

Test protection rules after repository migrations. When repositories are moved between organizations or renamed, protection rules might be lost. Migration scripts should preserve protection rules, and tests should validate preservation.

Test protection rules after GitHub updates. GitHub occasionally changes behavior or adds new features. Tests ensure protection rules continue working after updates. However, tests might need updates to accommodate new GitHub features.

## PR Validation Gates

PR validation gates ensure code quality before merge. These gates include linting, type checking, test execution, security scanning, and coverage requirements. Testing these gates ensures they catch issues without creating false positives that block legitimate merges.

### Linting and Type Checking

Test that linting gates catch violations. Create a PR with linting errors and verify it's blocked. Test that linting passes for valid code. Test that linting rules are consistent across repositories.

Test that type checking gates catch type errors. Create a PR with TypeScript errors and verify it's blocked. Test that type checking passes for valid code. Test that type checking is fast enough to not slow PR cycles.

Test linting and type checking consistency. Different repositories shouldn't have conflicting rules. A shared linting configuration ensures consistency. Tests validate that all repositories use the same configuration.

### Test Execution Gates

Test that test gates require passing tests. Create a PR with failing tests and verify it's blocked. Test that all test suites must pass, not just some. Test that flaky tests don't create false blocks.

Test test execution performance. Slow tests slow PR cycles. Tests should complete in under 10 minutes for fast feedback. If tests are slow, optimize or parallelize them. Test execution time should be monitored and optimized.

Test test coverage gates. If coverage requirements are enforced, test that low coverage blocks merges. Test that coverage calculations are accurate and consistent. However, coverage gates can be gamed—focus on test quality, not just coverage percentage.

### Security Scanning Gates

Test that security scanning gates catch vulnerabilities. Create a PR with known vulnerabilities (in a test repository) and verify it's blocked. Test that scanning tools are configured correctly and up-to-date.

Test security scanning performance. Security scans can be slow, especially dependency scans of large projects. Test that scans complete in reasonable time. If scans are too slow, consider running them asynchronously or on a schedule rather than blocking every PR.

Test security scanning false positives. Security scanners sometimes flag false positives. Test that false positives don't block legitimate merges. Teams should be able to dismiss false positives with justification.

### Coverage and Quality Gates

Test coverage gates carefully. Coverage requirements can be gamed with low-quality tests. Test that coverage gates don't encourage test gaming. Consider requiring coverage for new code only, not entire codebase.

Test quality gates (complexity, duplication, etc.). If code quality metrics are enforced, test that they catch actual quality issues. Test that quality gates don't block legitimate code. Quality gates should guide improvement, not block delivery.

Test that gates are appropriately strict. Gates that are too strict block legitimate merges and frustrate developers. Gates that are too lenient don't catch issues. Test gates with real PRs to find the right balance.

## Pre-commit Hooks vs CI Checks

Pre-commit hooks run checks before code is committed. CI checks run after code is pushed. Both approaches have trade-offs, and testing ensures they work effectively.

### Pre-commit Hook Testing

Test that pre-commit hooks catch issues locally. Developers should see linting errors, type errors, and test failures before pushing. This enables fast feedback without waiting for CI.

Test pre-commit hook performance. Slow hooks frustrate developers and encourage bypassing them. Hooks should complete in seconds, not minutes. Test hook execution time and optimize slow hooks.

Test pre-commit hook consistency. All developers should have the same hooks installed. A setup script or package manager ensures consistency. Tests validate that hooks are installed and configured correctly.

Test that hooks can be bypassed when needed. Sometimes developers need to commit work-in-progress code. Hooks should allow bypass with `--no-verify`, but this should be rare and documented.

### CI Check Testing

Test that CI checks run on every PR. Automated tests ensure CI is configured and running. PRs without CI checks should be flagged.

Test CI check reliability. Flaky CI checks create false blocks and frustrate developers. Test that checks are stable and don't fail randomly. Monitor CI check failure rates and fix flaky checks.

Test CI check performance. Slow CI slows PR cycles. Test that checks complete in reasonable time. If CI is slow, optimize or parallelize checks. CI performance should be monitored and optimized.

### Hybrid Approach Testing

Many teams use both pre-commit hooks and CI checks. Hooks catch issues early, CI ensures nothing is missed. Test that this hybrid approach works effectively.

Test that hooks and CI checks are consistent. Hooks and CI should check the same things. Inconsistency creates confusion—hooks pass but CI fails, or vice versa. Shared configuration ensures consistency.

Test that hooks don't duplicate CI unnecessarily. If CI runs comprehensive checks, hooks can focus on fast checks (formatting, simple linting). Test that the division of labor is appropriate.

## Automated Repository Compliance

Automated compliance checking ensures all repositories follow organizational standards. This includes checking for required files (README, LICENSE, CODEOWNERS), validating branch protection, and ensuring consistent structure.

### Repository Structure Compliance

Test that all repositories have required files. A script that checks for README.md, LICENSE, CODEOWNERS, and .gitignore ensures consistency. Repositories missing required files should be flagged.

Test that README files meet quality standards. READMEs should explain purpose, setup, testing, and contribution. Automated checks can validate README length, required sections, and links. However, quality assessment requires human review.

Test that repository descriptions are clear and consistent. Descriptions should explain what the repository does. Automated checks can validate description presence and length, but quality requires human review.

### Branch Protection Compliance

Test that all repositories have branch protection on main. A script that checks branch protection across all repositories ensures consistency. Repositories missing protection should be flagged and configured.

Test that branch protection rules match organizational standards. If the standard is "2 required approvals," verify all repositories follow this standard. Exceptions should be documented and justified.

Test that branch protection rules are up-to-date. As standards evolve, protection rules should be updated. Automated checks validate that rules match current standards. Migration scripts can update rules automatically.

### CODEOWNERS Compliance

Test that CODEOWNERS files are present and valid. Repositories with multiple contributors should have CODEOWNERS. Automated checks validate CODEOWNERS syntax and that owners exist (teams or users).

Test that CODEOWNERS patterns are specific, not overly broad. Broad patterns (`*` matches everything) create bottlenecks. Automated checks can flag overly broad patterns for review.

Test that CODEOWNERS ownership is current. As teams change and code moves, CODEOWNERS becomes stale. Regular audits (quarterly) ensure ownership matches reality. Automated checks can flag CODEOWNERS that haven't been updated recently.

### Compliance Reporting

Compliance checks should produce reports for review. Reports should highlight non-compliant repositories, missing configurations, and exceptions. These reports enable systematic compliance improvement.

Compliance reports should be actionable. Instead of just listing issues, reports should include remediation steps. "Repository X is missing CODEOWNERS—add CODEOWNERS file with team ownership" is more actionable than "Repository X is non-compliant."

Compliance should be measured over time. Tracking compliance metrics (percentage of repositories with protection, CODEOWNERS coverage, etc.) shows improvement trends. These metrics enable data-driven governance improvement.

## QA and Test Engineer Perspective

QA and test engineers have unique perspectives on repository governance. They need visibility into changes, ability to validate quality gates, and confidence that governance enables rather than blocks quality work.

### Visibility into Changes

QA engineers need visibility into what's changing. PR descriptions should explain changes clearly, including what's being tested and how. QA engineers shouldn't need to read code to understand changes.

PR templates should include QA sections. A section for "Testing Notes" and "QA Checklist" ensures QA engineers have the information they need. This visibility enables effective testing and prevents surprises.

CODEOWNERS should include QA teams for critical paths. QA engineers should review PRs that affect testing infrastructure, test utilities, or quality gates. This ensures QA perspective is included in development decisions.

### Quality Gate Validation

QA engineers should validate that quality gates work. If tests are required to pass, QA should verify that failing tests actually block merges. If coverage is required, QA should verify that low coverage blocks merges.

QA engineers should test quality gates with real scenarios. Create test PRs with various issues (failing tests, low coverage, security vulnerabilities) and verify gates catch them. This validation ensures gates are effective.

QA engineers should monitor quality gate effectiveness. If gates frequently block legitimate merges (false positives) or miss issues (false negatives), gates need adjustment. QA feedback helps tune gates appropriately.

### Governance That Enables Quality

Governance should enable quality work, not block it. If governance creates bottlenecks that prevent thorough testing, governance needs adjustment. QA engineers should advocate for governance that supports quality.

Small, focused PRs enable better testing. Large PRs are difficult to test thoroughly. QA engineers should advocate for PR size limits and clear acceptance criteria that enable effective testing.

Fast feedback loops enable quality. If CI is slow, developers get feedback late, and issues are discovered late. QA engineers should advocate for fast CI that enables rapid testing cycles.

### Test Infrastructure Ownership

QA engineers often own test infrastructure. CODEOWNERS should reflect this ownership—QA teams should own test directories, test utilities, and quality gate configurations. This ownership ensures QA perspective in infrastructure decisions.

Test infrastructure changes should require QA review. Changes to test frameworks, CI configurations, or quality gates affect testing effectiveness. CODEOWNERS should route these changes to QA teams.

QA engineers should have input into governance design. When branch protection rules or quality gates are designed, QA perspective ensures testing needs are considered. Governance designed without QA input might not support effective testing.
