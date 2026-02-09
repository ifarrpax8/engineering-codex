---
title: CI/CD - Testing
type: perspective
facet: ci-cd
last_updated: 2026-02-09
---

# CI/CD: Testing

## Contents

- [Testing in CI](#testing-in-ci)
- [Test Parallelization](#test-parallelization)
- [Flaky Test Management](#flaky-test-management)
- [Test Result Reporting](#test-result-reporting)
- [Pipeline Testing](#pipeline-testing)
- [Security Testing in CI](#security-testing-in-ci)
- [Performance Testing in CI](#performance-testing-in-ci)
- [Smoke Tests After Deployment](#smoke-tests-after-deployment)

## Testing in CI

Automated testing forms the foundation of continuous integration. Every pull request should trigger a comprehensive test suite that validates code correctness, integration behavior, and end-to-end functionality. The test pyramid guides test distribution: many fast unit tests, fewer slower integration tests, and a small number of expensive end-to-end tests.

Unit tests execute first in the pipeline, providing rapid feedback on code correctness. These tests should be fast—completing in seconds or minutes, not hours. They should be isolated, testing individual components without external dependencies. When unit tests fail, the pipeline should fail immediately, preventing wasted time on integration or end-to-end tests that would also fail.

Integration tests follow unit tests, validating interactions between components. These tests may involve databases, message queues, or external services, making them slower and more complex than unit tests. Test containers provide isolated environments for integration tests, ensuring consistency and preventing interference between test runs. Integration tests should still complete relatively quickly—ideally within 10 minutes for the entire suite.

End-to-end tests validate complete user workflows, typically using browser automation tools like Playwright. These tests are the slowest and most brittle, but they provide the highest confidence that the application works as users expect. End-to-end tests should focus on critical user journeys rather than attempting to test every possible path through the application.

The fail-fast principle applies throughout the test pipeline. If unit tests fail, don't run integration tests. If integration tests fail, don't run end-to-end tests. This minimizes CI duration and provides faster feedback to developers. Parallel execution can help—run unit tests, integration tests, and end-to-end tests simultaneously if they don't depend on each other, but still fail the pipeline if any suite fails.

## Test Parallelization

Large test suites can take hours to execute sequentially. Parallelization splits test execution across multiple CI runners or worker threads, dramatically reducing total execution time. Effective parallelization requires understanding test dependencies and resource requirements.

JUnit 5 supports parallel test execution within a single JVM. Tests can run in parallel by class, by method, or using custom strategies. Parallel execution requires careful attention to shared state—tests must be isolated and not depend on execution order. Thread-safe test fixtures and proper cleanup ensure that parallel tests don't interfere with each other.

Playwright supports test sharding, splitting tests across multiple workers or CI runners. Each shard runs a subset of tests, and results are combined at the end. Sharding works best when tests are independent and have similar execution times. Uneven sharding can leave some workers idle while others complete their work.

Vitest uses worker threads to parallelize test execution. Tests run in isolated worker processes, preventing interference while maximizing CPU utilization. Worker configuration balances parallelism with resource constraints—too many workers can cause memory pressure or resource contention.

Test parallelization requires infrastructure investment. CI platforms charge based on runner minutes, so parallelization increases costs even as it reduces wall-clock time. The trade-off is usually worthwhile—faster feedback improves developer productivity and reduces context switching. However, teams should monitor costs and optimize parallelism based on actual needs.

## Flaky Test Management

Flaky tests—tests that pass or fail non-deterministically—erode trust in CI pipelines. When developers see a test failure, they must determine whether it represents a real bug or a flaky test. This uncertainty slows down development and can cause real bugs to be dismissed as flakes.

Flaky tests have many causes: timing issues, race conditions, shared state, external dependencies, or resource constraints. Identifying the root cause requires investigation—reproducing the failure, examining logs, and understanding test execution context. Some flaky tests only fail under specific conditions: high system load, specific timing, or particular data states.

The first step in managing flaky tests is detection. Track test failure rates over time. Tests that fail occasionally but pass on retry are likely flaky. CI platforms often provide retry mechanisms, but retries mask the underlying problem rather than solving it.

Quarantine provides a temporary solution for flaky tests. Move flaky tests to a separate test suite that runs but doesn't block merges. This prevents flaky tests from blocking development while they're being fixed. However, quarantine should be temporary—flaky tests should be fixed or removed, not ignored indefinitely.

Fixing flaky tests requires addressing root causes. Timing issues may require explicit waits or synchronization. Race conditions may need locks or atomic operations. Shared state may require test isolation or cleanup. External dependencies may need mocking or test doubles. Resource constraints may require test environment optimization.

Some flaky tests cannot be fixed within reasonable time constraints. These tests should be removed rather than left to erode CI trust. However, removal should be deliberate—ensure that the test's coverage is provided elsewhere, or accept the risk of reduced coverage.

Flake rate tracking helps prioritize flaky test fixes. Tests with high flake rates cause more disruption and should be fixed first. Tests that rarely fail may be lower priority. However, even low flake rates accumulate over time—a test that fails 1% of the time will fail multiple times per week in a high-frequency deployment environment.

## Test Result Reporting

Effective test reporting helps developers understand failures quickly and track test health over time. JUnit XML reports provide a standard format that CI platforms can parse and display. These reports include test names, execution times, failure messages, and stack traces.

GitHub Actions annotations display test results inline in pull requests. Failed tests appear as comments on relevant code lines, making it easy to see which changes caused failures. This tight integration between tests and code review accelerates feedback loops.

Test trend visualization shows how test suites evolve over time. Test counts, execution times, and failure rates provide insights into codebase health and CI performance. Increasing test execution time may indicate performance regressions or test suite growth. Increasing failure rates may indicate flaky tests or code quality issues.

Failure categorization helps distinguish between different types of failures. New failures—tests that previously passed but now fail—indicate regressions. Known flakes—tests that fail intermittently—indicate flaky test problems. Infrastructure failures—CI runner issues, network problems—indicate environmental problems rather than code issues.

Test result aggregation becomes important when tests run in parallel or across multiple environments. Results must be collected, combined, and presented coherently. CI platforms typically handle this automatically, but custom reporting may be needed for complex scenarios.

## Pipeline Testing

CI/CD pipelines themselves must be tested to ensure they work correctly. Pipeline syntax errors can prevent workflows from running. Configuration mistakes can cause incorrect behavior. Deployment scripts can fail in unexpected ways.

Workflow syntax validation catches YAML errors before pipelines run. GitHub Actions validates workflow files on commit, providing immediate feedback on syntax issues. However, syntax validation doesn't catch logical errors—workflows can be syntactically correct but functionally wrong.

Local testing tools like `act` enable running GitHub Actions workflows locally before committing. This allows developers to test pipeline changes without waiting for CI feedback. However, local execution may differ from CI execution due to environment differences.

Staging environments provide the most realistic testing for deployment pipelines. Deploying to staging uses the same mechanisms as production deployment, catching environment-specific issues before they affect production. Staging deployments should be routine, not exceptional—every production deployment should first succeed in staging.

Deployment script testing ensures that scripts work correctly across different scenarios. Scripts should handle edge cases: missing environment variables, network failures, partial deployments. Error handling and rollback mechanisms should be tested, not assumed to work.

Pipeline testing should be part of the development process. Changes to CI/CD configuration should go through the same review and testing process as application code. This ensures that pipeline improvements don't introduce regressions.

## Security Testing in CI

Security testing in CI identifies vulnerabilities before they reach production. Multiple testing approaches provide defense in depth: static analysis, dependency scanning, secret detection, and container image scanning.

Static Application Security Testing (SAST) analyzes source code for security vulnerabilities. Tools like SonarQube, Semgrep, or CodeQL identify common security issues: SQL injection, cross-site scripting, insecure random number generation, hardcoded secrets. SAST tools have false positives, but they catch many real issues that would otherwise require manual code review.

Dependency scanning identifies known vulnerabilities in third-party dependencies. Tools like Dependabot, OWASP Dependency-Check, or Snyk check dependencies against vulnerability databases. These tools can automatically create pull requests to update vulnerable dependencies, reducing manual maintenance burden.

Secret scanning detects accidentally committed credentials, API keys, or tokens. Tools like truffleHog, GitGuardian, or GitHub's secret scanning analyze commits for patterns that match secrets. Early detection prevents secrets from being exposed in version control, where they're difficult to revoke.

Container image scanning analyzes built images for known vulnerabilities in base images and installed packages. Tools like Trivy, Clair, or Snyk scan images and report vulnerabilities with severity ratings. Critical vulnerabilities should block image pushes, while lower-severity issues can be tracked and addressed over time.

Security testing should be integrated into CI pipelines, not run separately. Security scans should complete quickly—within minutes—to avoid slowing down development. Critical findings should block merges, but lower-severity issues can be tracked without blocking development.

Security testing requires ongoing maintenance. Vulnerability databases update frequently as new vulnerabilities are discovered. Scanning tools must be kept up to date to detect the latest threats. Teams should review security findings regularly and address them systematically.

## Performance Testing in CI

Performance testing in CI ensures that code changes don't introduce performance regressions. Bundle size checks, API latency comparisons, and Lighthouse scores provide quantitative performance metrics that can be enforced automatically.

Frontend bundle size checks prevent unbounded growth in JavaScript bundles. Performance budgets fail builds when bundles exceed size thresholds. These budgets should be set based on real performance requirements—target load times, network conditions, device capabilities. Bundle analysis helps identify optimization opportunities when budgets are exceeded.

API latency baseline comparison detects performance regressions in backend services. Tests measure endpoint response times and compare them to historical baselines. Significant increases trigger alerts or fail builds, depending on severity. Baseline comparison accounts for normal variation while catching real regressions.

Lighthouse CI runs automated performance audits on web applications. Lighthouse scores measure performance, accessibility, best practices, and SEO. Performance budgets can enforce minimum Lighthouse scores, failing builds when scores drop below thresholds.

Performance testing in CI requires careful calibration. Performance metrics have natural variation—network conditions, system load, and timing can affect measurements. Tests must account for this variation to avoid false positives while catching real regressions.

Performance testing should focus on critical paths rather than comprehensive coverage. Testing every endpoint or every page would be prohibitively expensive. Instead, focus on user-facing critical paths that directly impact user experience.

## Smoke Tests After Deployment

Smoke tests run immediately after deployment to verify that basic functionality works. These tests check critical paths: health endpoints respond correctly, authentication works, primary user journeys complete successfully. Smoke tests should complete quickly—within minutes—to provide rapid feedback on deployment success.

Smoke tests differ from comprehensive test suites. They focus on high-level functionality rather than detailed edge cases. They verify that the deployment succeeded and that the application is operational, not that every feature works perfectly.

Automated smoke tests should be part of the CD pipeline. After deployment completes, smoke tests run automatically. If smoke tests fail, the pipeline should trigger rollback or alert the team. Manual smoke testing is too slow and error-prone for modern deployment practices.

Smoke tests should be stable and reliable. Flaky smoke tests create false alarms that erode trust. Smoke tests should use the same reliability practices as other automated tests: proper waits, isolation, cleanup.

Smoke test coverage should evolve with the application. As new critical features are added, smoke tests should verify them. As features become less critical, their smoke test coverage can be reduced. Regular review ensures that smoke tests remain relevant and valuable.
