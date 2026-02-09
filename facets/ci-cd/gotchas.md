---
title: CI/CD - Gotchas
type: perspective
facet: ci-cd
last_updated: 2026-02-09
---

# CI/CD: Gotchas

## Slow CI Killing Developer Velocity

Slow CI pipelines create a cascade of negative behaviors that reduce team productivity. When pipelines take 30 minutes or more, developers naturally adapt their workflow in ways that harm code quality and collaboration.

Context switching becomes inevitable. A developer submits a pull request and waits for CI feedback. Rather than staying focused on the current change, they switch to other work. When CI completes, they must reacquaint themselves with the original context, losing mental momentum and increasing the likelihood of overlooking important feedback.

Batching changes becomes a coping mechanism. If each CI run takes 30 minutes, developers combine multiple unrelated changes into a single pull request to minimize wait time. This creates larger, harder-to-review changes that increase the risk of bugs and make code review less effective.

Avoiding small PRs becomes a rational choice. When CI feedback takes too long, the overhead of creating a pull request outweighs the benefits of early feedback. Developers work in isolation for longer periods, accumulating technical debt and increasing the risk of integration conflicts.

The solution requires profiling pipeline stages to identify bottlenecks, then optimizing through parallelization, caching, and infrastructure improvements. The target is pipelines that complete in under 10 minutes, with critical path stages completing even faster. Fast CI transforms developer behavior, enabling small focused pull requests and continuous integration.

## Flaky Tests Eroding Trust

Flaky tests—tests that pass or fail non-deterministically—create a crisis of confidence in CI pipelines. When developers see a test failure, they must determine whether it represents a real bug or a flaky test. This uncertainty slows down development and can cause real bugs to be dismissed as flakes.

The problem compounds over time. If tests fail 5% of the time, developers learn to re-run failed builds "just in case." Real failures get dismissed as flakes. The pipeline loses its value as a quality gate because developers don't trust its results.

Flaky tests have many causes: timing issues, race conditions, shared state, external dependencies, or resource constraints. Some flaky tests only fail under specific conditions that are difficult to reproduce. Fixing flaky tests requires investigation and often significant refactoring.

The solution requires a systematic approach: detect flaky tests through failure rate tracking, quarantine them to prevent blocking development, fix root causes through proper synchronization and isolation, and track flake rates to prioritize fixes. Some flaky tests cannot be fixed within reasonable time constraints and should be removed rather than left to erode CI trust.

## Long-Lived Feature Branches

Feature branches that live for weeks or months create integration problems that compound over time. As branches diverge from main, merge conflicts accumulate. Integration happens at the worst possible time—right before release, when pressure is highest and time is most constrained.

Long-lived branches prevent continuous integration. Code written weeks ago may conflict with recent changes to main. The integration work becomes a separate, stressful task rather than a routine part of development. This increases the risk of bugs and delays delivery.

The solution is trunk-based development with short-lived branches. Branches should live for less than one day ideally, merging to main multiple times per day. Incomplete work hides behind feature flags, allowing frequent merges without affecting users. This requires discipline but enables high deployment frequency and reduces integration risk.

## Manual Deployment Steps

Manual deployment processes introduce delay, variability, and human error. Each manual step is a potential failure point: "run this script, then update this config, then restart that service." Documentation becomes outdated, team members forget steps, and deployments become inconsistent.

Manual processes don't scale. As teams grow or deployment frequency increases, manual deployments become a bottleneck. They require human attention that could be directed toward higher-value activities. They prevent rapid response to production issues.

The solution is complete automation of the deployment process. Every step should be automated: building artifacts, updating configurations, deploying to environments, running health checks, monitoring deployments. Automation ensures consistency, enables scaling, and reduces human error.

## Secrets in CI Logs

Accidentally logging secrets in CI output creates security risks that are difficult to mitigate. Once secrets appear in logs, they may be accessible to anyone with log access. Revoking and rotating secrets is disruptive and may not immediately address the exposure.

CI platforms mask known secrets in logs, but custom scripts may leak them. Environment variables containing API keys or tokens may be printed in error messages or debug output. Build scripts that echo variables for debugging can expose secrets.

The solution requires careful code review of CI scripts and build processes. Never log environment variables directly. Use secret management tools that integrate with CI platforms. Review CI logs regularly for sensitive data. Educate team members about the risks of logging secrets.

## No Rollback Strategy

Deployments fail, and teams scramble to figure out how to revert. Without a defined rollback strategy, recovery takes too long, extending production incidents. Teams may attempt manual fixes that make situations worse, or they may be unable to roll back at all.

Rollback strategies must be defined before the first deployment. They should be tested regularly—not just documented, but actually executed in staging or production-like environments. Automated rollback mechanisms provide the fastest recovery, but even manual rollback procedures must be well-documented and practiced.

The solution requires defining rollback procedures as part of initial deployment planning. Rollbacks should be tested regularly to ensure they work when needed. Automated rollback based on health checks or SLO violations provides the fastest recovery. Manual rollback procedures should be documented and accessible to all team members.

## Rebuilding for Each Environment

Building different artifacts for staging and production creates subtle differences between environments. What's tested in staging may not match what's deployed to production. Build timestamps, dependency resolution differences, or environment-specific build logic can create artifacts that behave differently despite appearing identical.

Rebuilding also wastes time and resources. The same code is compiled multiple times, tests run multiple times, and artifacts are built multiple times. This slows down delivery and increases the risk of environment-specific issues.

The solution is immutable artifacts: build once, deploy to all environments. Environment-specific configuration comes from environment variables, ConfigMaps, or values files, not from rebuilding. This ensures that what's tested in staging is identical to what's deployed to production.

## CI Cache Poisoning

Corrupted or stale caches cause mysterious build failures that are difficult to diagnose. Caches that don't properly invalidate when dependencies change can cause builds to use outdated dependencies, leading to inconsistent behavior or failures that don't reproduce locally.

Cache poisoning can be subtle. A cache might work correctly for weeks, then suddenly cause failures when a dependency is updated but the cache isn't invalidated. Developers spend time debugging code when the real issue is a stale cache.

The solution requires careful cache key design. Cache keys should include dependency lockfile hashes so caches invalidate when dependencies change. Teams should provide a way to bust caches when needed—either through manual cache clearing or by including a cache version in cache keys that can be incremented.

## Not Testing the Deployment Process

Teams test application code thoroughly but neglect testing deployment processes. Deployment scripts, Helm charts, Terraform configurations, and Kubernetes manifests may contain errors that only appear during actual deployment. These errors cause production deployment failures that would have been caught by testing deployment processes in staging.

Deployment processes are code and should be tested like any other code. Helm charts should be validated and tested against staging Kubernetes clusters. Terraform plans should be reviewed and applied to staging before production. Deployment scripts should be tested in staging environments.

The solution requires treating deployment code with the same rigor as application code. Test deployment processes in staging before using them in production. Validate configuration syntax, test rollback procedures, and verify that deployments work correctly. Include deployment testing in CI pipelines where possible.

## Over-Gating

Too many manual approvals and quality gates slow deployment to a crawl. Every gate should prevent a specific, likely failure. If a gate has never blocked a bad deployment, it may not be providing value. Gates that always pass or that block deployments for reasons unrelated to quality reduce deployment frequency without improving outcomes.

Over-gating creates bottlenecks. When multiple people must approve every deployment, deployments wait for availability. When quality gates are too strict, they block deployments for minor issues that don't affect production. This reduces deployment frequency and slows down delivery.

The solution requires regular review of quality gates. Each gate should have a clear purpose and should actually prevent problems. Gates that never block bad deployments should be removed or modified. Manual approvals should be reserved for high-risk changes, with low-risk changes deploying automatically after automated checks pass.
