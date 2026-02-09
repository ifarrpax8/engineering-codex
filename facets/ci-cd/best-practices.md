---
title: CI/CD - Best Practices
type: perspective
facet: ci-cd
last_updated: 2026-02-09
---

# CI/CD: Best Practices

## Contents

- [Keep Pipelines Fast](#keep-pipelines-fast)
- [Fail Fast](#fail-fast)
- [Make Builds Reproducible](#make-builds-reproducible)
- [Trunk-Based Development with Feature Flags](#trunk-based-development-with-feature-flags)
- [Infrastructure as Code](#infrastructure-as-code)
- [Immutable Artifacts](#immutable-artifacts)
- [Automate Everything](#automate-everything)
- [Stack-Specific Optimizations](#stack-specific-optimizations)

## Keep Pipelines Fast

Pipeline duration directly impacts developer productivity. Slow pipelines cause context switching, batching of changes, and avoidance of small pull requests. The target for optimal developer experience is under 10 minutes for the complete CI pipeline, with critical path stages completing even faster.

Achieving fast pipelines requires multiple strategies working together. Parallel execution runs independent stages simultaneously, reducing total duration. Caching stores dependencies and build outputs between runs, avoiding redundant work. Incremental builds only process changed code, skipping unchanged components.

Profiling identifies bottlenecks. Measure each pipeline stage's duration to understand where time is spent. Common bottlenecks include dependency installation, test execution, and artifact building. Once identified, bottlenecks can be optimized through caching, parallelization, or infrastructure improvements.

Splitting slow tests into separate pipelines can help. If end-to-end tests take 30 minutes, they can run in a separate pipeline that doesn't block merges. However, this reduces confidence—code can merge without full test coverage. Use this approach carefully and ensure that slow tests still run before production deployment.

Infrastructure scaling affects pipeline speed. More powerful CI runners execute tests faster. More runners enable greater parallelism. However, infrastructure costs money, so balance speed improvements against cost increases. Monitor runner utilization to ensure that additional capacity is actually used.

## Fail Fast

Fast feedback requires failing quickly when problems are detected. Run the fastest checks first: linting, formatting, compilation. Don't run expensive integration tests if a 30-second lint check would fail. This minimizes wasted CI resources and provides faster feedback to developers.

The fail-fast principle applies to individual checks as well as pipeline stages. Linting should fail on the first error, not continue to find all errors. Compilation should fail immediately on syntax errors. Tests should fail as soon as assertions fail, not continue running other tests in the same suite.

Early failure requires proper error reporting. When a check fails, the error message should clearly indicate what went wrong and how to fix it. Vague error messages force developers to investigate, slowing down the feedback loop. Good error messages include file paths, line numbers, and specific guidance.

Some checks can't fail fast—integration tests may need to run to completion to provide useful diagnostics. However, even slow checks should fail as early as possible when fundamental problems are detected. Health checks, connectivity tests, and setup validation can catch problems before expensive test execution begins.

## Make Builds Reproducible

Reproducible builds produce identical outputs from identical inputs. This enables reliable deployments, easier debugging, and audit compliance. Reproducibility requires locking all variable inputs: dependency versions, build tool versions, environment configurations.

Dependency locking prevents version drift. `package-lock.json` for npm and `gradle.lockfile` for Gradle record exact dependency versions. These lockfiles must be committed to version control and used in CI environments. Installing dependencies without lockfiles allows version resolution to change, breaking reproducibility.

Build tool versions must be consistent. The Gradle wrapper ensures consistent Gradle versions across environments. npm versions should be specified in `.nvmrc` or `package.json` engines field. Docker base images should be pinned by digest, not tag, to prevent changes when tags are updated.

Environment variables and configuration affect build outputs. Builds should be deterministic regardless of environment, or environment differences should be explicitly documented. Time-based or random values in builds break reproducibility unless seeds are controlled.

Reproducible builds enable reliable rollbacks. If a deployment fails, rolling back to a previous version should produce the same artifact that was previously deployed. This requires that builds are reproducible across time, not just across environments.

## Trunk-Based Development with Feature Flags

Trunk-based development keeps the main branch always deployable through frequent merges of small changes. Feature flags enable incomplete work to merge without affecting users, decoupling deployment from release. This combination enables high deployment frequency while maintaining production stability.

Short-lived branches minimize merge conflicts and enable continuous integration. Branches should live for less than one day ideally, merging to main multiple times per day. This requires breaking large features into smaller, independently deployable increments.

Feature flags hide incomplete work behind conditional logic. Code deploys to production disabled, then enables gradually for specific users or percentages. This allows teams to merge frequently while controlling feature exposure. Feature flags require management infrastructure but enable practices that would otherwise be impossible.

Trunk-based development requires discipline. Developers must keep branches short, write comprehensive tests, and use feature flags appropriately. However, the benefits are substantial: fewer merge conflicts, faster integration, higher deployment frequency, and improved code quality through frequent review.

## Infrastructure as Code

All infrastructure should be defined as code: servers, networks, databases, Kubernetes clusters, load balancers. Infrastructure-as-code enables version control, code review, automated testing, and reproducible environments. Manual infrastructure changes are error-prone, undocumented, and difficult to audit.

Terraform, Pulumi, or CloudFormation define cloud infrastructure declaratively. Changes go through code review like application code. Infrastructure can be tested in staging before production. Version control provides a history of changes and the ability to roll back problematic updates.

Kubernetes configurations should be defined in YAML manifests, Helm charts, or Kustomize overlays. These definitions are version controlled and reviewed. Environment-specific configuration comes from values files or ConfigMaps, not hardcoded in manifests.

Infrastructure-as-code enables automation. Provisioning new environments becomes a matter of running terraform apply or helm install, not manually configuring servers. This reduces time-to-environment and eliminates configuration drift between environments.

No manual changes to production should be allowed. All changes should go through the same process: code, review, test, deploy. This ensures that production infrastructure is always defined in code and can be reproduced or audited.

## Immutable Artifacts

Build artifacts should be immutable: built once, deployed to all environments. Environment-specific configuration comes from environment variables, ConfigMaps, or values files, not from rebuilding artifacts. This ensures that what's tested in staging is identical to what's deployed to production.

Rebuilding for each environment introduces risk. Subtle differences between builds can cause issues that only appear in production. Build timestamps, dependency resolution differences, or environment-specific build logic can create artifacts that behave differently despite appearing identical.

Immutable artifacts enable reliable testing. If staging tests pass, production deployment should work because the artifact is identical. This reduces the "works on my machine" problem and increases deployment confidence.

Container images exemplify immutable artifacts. An image built in CI is tagged and deployed to staging, then the same tagged image is deployed to production. No rebuild occurs between environments. Configuration differences come from environment variables or mounted configuration files.

## Automate Everything

Automation reduces human error, accelerates delivery, and enables scaling. If a process is performed more than twice, it should be automated. Manual processes are slow, inconsistent, and don't scale. Automation ensures consistency and frees human attention for higher-value activities.

Dependency updates can be automated through Dependabot or similar tools. These tools monitor dependencies for updates and create pull requests automatically. Teams review and merge updates, but the discovery and preparation work is automated.

Changelog generation can be automated based on commit messages or pull request labels. Version bumping can be automated based on conventional commits or release tags. Deployment can be automated through CD pipelines that deploy after successful CI.

Even processes that seem to require human judgment can often be partially automated. Code review can be assisted by automated checks that catch common issues. Deployment approvals can be automated for low-risk changes while requiring manual approval for high-risk ones.

Automation requires maintenance. Automated processes must be tested, monitored, and updated as requirements change. However, the benefits usually outweigh the costs: automation is more reliable than manual processes and scales better.

## Stack-Specific Optimizations

### Gradle

Gradle builds should leverage several optimization features. The build cache stores task outputs between builds, dramatically reducing build time for incremental changes. Enable with `--build-cache` or in `gradle.properties`.

The configuration cache stores the task graph, reducing configuration time for large projects. This is particularly valuable for multi-module projects where configuration can take significant time. Enable with `--configuration-cache`.

Parallel execution runs independent tasks simultaneously. Enable with `--parallel` or in `gradle.properties`. Gradle automatically determines task dependencies and parallelizes safely, but proper task input/output declarations are required.

The Gradle wrapper ensures consistent Gradle versions. Always use `./gradlew` instead of a globally installed Gradle. Commit the wrapper to version control so all developers and CI use the same version.

Dependency locking prevents dependency resolution changes. Generate `gradle.lockfile` and commit it to version control. Use `--write-locks` when updating dependencies to keep the lockfile current.

### npm and Vite

Use `npm ci` instead of `npm install` in CI environments. The `ci` command installs directly from `package-lock.json` without modifying it, ensuring reproducible installs. It also removes `node_modules` before installing, preventing inconsistencies.

Cache `node_modules` between CI runs to speed up installation. Include `package-lock.json` in the cache key so caches invalidate when dependencies change. npm's cache can be stored in CI platform caches or external storage.

Use the lockfile consistently. `package-lock.json` should be committed to version control and used in all environments. Never run `npm install` without the lockfile, as this allows version resolution to change.

Bundle analysis helps identify optimization opportunities. Tools visualize bundle composition, highlighting large dependencies. Performance budgets enforce size limits, failing builds when thresholds are exceeded.

### GitHub Actions

Composite actions encapsulate reusable workflow steps. Common patterns—building Docker images, running security scans—can be defined once and reused across multiple workflows. This reduces duplication and ensures consistency.

Reusable workflows enable sharing entire workflows across repositories. Organizations can define standard CI pipelines that multiple projects use, ensuring consistent practices. Workflows accept inputs and can be customized per project while maintaining core structure.

Matrix builds test across multiple versions or configurations simultaneously. Test against multiple Node.js versions, Java versions, or operating systems in parallel. This provides comprehensive coverage without sequential execution.

Concurrency groups prevent duplicate workflow runs. When multiple events trigger the same workflow—for example, pushes to a branch and opening a pull request—concurrency groups cancel older runs, saving CI resources and providing clearer results.

### Docker

Multi-stage builds separate build-time and runtime dependencies. Build stages contain full SDKs needed for compilation. Runtime stages contain only what's needed to run the application. This creates smaller, more secure images.

The `.dockerignore` file prevents unnecessary files from being included in build context. Large files or directories that aren't needed slow down builds and increase image size. Proper `.dockerignore` configuration is essential for efficient builds.

Layer ordering affects cache efficiency. Copy dependency files before source code, since dependencies change less frequently. Install dependencies before copying application code. This allows Docker to reuse cached layers when only application code changes.

Runtime images should run as non-root users. Create a dedicated user in the Dockerfile and switch to it before running the application. This follows the principle of least privilege and reduces the impact of potential security issues.
