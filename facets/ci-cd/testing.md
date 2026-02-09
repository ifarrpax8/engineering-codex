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
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

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

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize CI/CD testing based on deployment risk and feedback speed. Critical paths requiring immediate coverage include: test execution (tests run on every commit), test reliability (tests don't flake), and deployment validation (deployments succeed). High-priority areas include: test execution time (tests complete quickly), test result reporting (test results are clear), and security testing (vulnerabilities detected before deployment).

Medium-priority areas suitable for later iterations include: test optimization, test reporting enhancements, and pipeline optimization. Low-priority areas for exploratory testing include: advanced CI/CD features, pipeline visualization, and deployment automation.

Focus on CI/CD failures with high deployment risk: broken deployments (deployments fail in production), missed bugs (tests don't catch bugs), and slow feedback (tests take too long). These represent the highest risk of production incidents and reduced development velocity.

### Exploratory Testing Guidance

Pipeline reliability exploration: test pipeline execution (pipelines run successfully), pipeline failure handling (pipelines fail gracefully), and pipeline recovery (pipelines recover from failures). Probe edge cases: concurrent pipeline runs, resource exhaustion, and infrastructure failures.

Test execution requires investigation: test test execution time (tests complete within acceptable time), test execution reliability (tests don't flake), and test execution parallelization (tests run in parallel). Explore what happens with large test suites, slow tests, and flaky tests.

Deployment validation needs exploration: test deployment success (deployments succeed), deployment rollback (deployments can be rolled back), and deployment smoke tests (deployments validated after completion). Probe edge cases: deployment failures, partial deployments, and deployment conflicts.

Security testing in CI requires investigation: test security scan execution (security scans run), security scan results (security vulnerabilities detected), and security scan blocking (security vulnerabilities block deployments). Explore what happens with security scan failures, security scan false positives, and security scan performance.

### Test Data Management

CI/CD testing requires test execution data: test results (pass/fail), test execution times, test failure history, and pipeline execution history. Collect CI/CD metrics over time to identify trends: increasing execution times, increasing failure rates, increasing flaky test rates.

Test environment data: test environment configurations, test environment availability, and test environment isolation. Maintain test environment data to track environment health and identify environment-related issues.

Deployment data: deployment success rates, deployment failure reasons, and deployment rollback frequency. Track deployment data to identify deployment patterns and improve deployment reliability.

Security scan data: security scan results, security vulnerability counts, and security scan execution times. Maintain security scan data to track security posture and identify security trends.

### Test Environment Considerations

CI/CD test environments must match production: same CI/CD platform (GitHub Actions, GitLab CI, Jenkins), same test execution environment (same runners, same configurations), and same deployment mechanisms. Differences can hide CI/CD issues or create false positives. Verify that CI/CD environments use production-like configurations.

Shared CI/CD environments create isolation challenges: concurrent pipeline runs may interfere with each other (resource conflicts, test data conflicts, deployment conflicts). Use isolated CI/CD environments per pipeline run, or implement pipeline isolation through unique identifiers and cleanup between runs.

Environment-specific risks include: CI/CD environments with different performance characteristics (affects test execution times), CI/CD environments missing production features (affects test coverage), and CI/CD environments with different configurations (affects test behavior). Verify that CI/CD environments have equivalent capabilities, or explicitly test differences as separate scenarios.

CI/CD infrastructure: CI/CD environments may have resource constraints (CPU, memory, network) that affect test execution. Monitor resource usage to identify constraints and optimize test execution.

### Regression Strategy

CI/CD regression suites must include: test execution (tests run on every commit), test reliability (tests don't flake), deployment validation (deployments succeed), and security testing (vulnerabilities detected). These represent the core CI/CD functionality that must never regress.

Automation candidates for regression include: test execution (tests run automatically), test result reporting (results reported automatically), and deployment validation (deployments validated automatically). These are deterministic and can be validated automatically.

Manual regression items include: pipeline configuration review (pipelines configured correctly), test quality assessment (tests catch bugs), and deployment process review (deployments work correctly). These require human judgment and operational expertise.

Trim regression suites by removing tests for deprecated CI/CD features, obsolete pipeline patterns, or rarely-used CI/CD functionality. However, maintain tests for critical CI/CD capabilities (test execution, deployment validation) even if they're simple—CI/CD regressions have high deployment risk.

### Defect Patterns

Common CI/CD bugs include: tests don't run (pipelines broken), tests flake (tests unreliable), deployments fail (deployments broken), and security vulnerabilities missed (security scans don't catch vulnerabilities). These patterns recur across CI/CD pipelines and should be addressed systematically.

Bugs tend to hide in: edge cases (concurrent pipeline runs, resource exhaustion), configuration issues (pipeline misconfiguration, test misconfiguration), and integration issues (CI/CD tools not integrated correctly). Address these issues explicitly—they're common sources of CI/CD failures.

Historical patterns show that CI/CD bugs cluster around: test execution (tests don't run or flake), deployment validation (deployments fail), and security testing (vulnerabilities missed). Focus CI/CD improvement efforts on these areas.

Triage guidance: CI/CD bugs affecting deployment reliability are typically high priority due to deployment risk. However, distinguish between critical issues (deployments fail) and optimization opportunities (tests slow but functional). Critical issues require immediate attention, while optimization opportunities can be prioritized based on impact.
