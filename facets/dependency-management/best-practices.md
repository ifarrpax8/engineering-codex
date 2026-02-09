# Dependency Management -- Best Practices

## Contents

- [Evaluate Before You Add](#evaluate-before-you-add)
- [Prefer Widely-Adopted Over Niche](#prefer-widely-adopted-over-niche)
- [Pin Production Dependencies, Use Ranges in Libraries](#pin-production-dependencies-use-ranges-in-libraries)
- [Automate Dependency Upgrades](#automate-dependency-upgrades)
- [Review Transitive Dependencies](#review-transitive-dependencies)
- [Maintain Lock File Hygiene](#maintain-lock-file-hygiene)
- [Monitor Dependency Health](#monitor-dependency-health)
- [Stack-Specific Practices](#stack-specific-practices)

Dependency management best practices balance the benefits of leveraging existing libraries against the risks and maintenance burden they introduce. These practices apply across technologies and frameworks, providing a foundation for effective dependency management.

## Evaluate Before You Add

Before adding a dependency, evaluate its maintenance status, security posture, license compatibility, bundle size impact, and alternatives. A quick evaluation prevents future problems and ensures dependencies are added intentionally, not casually.

**Maintenance Checklist**: Check recent commits (active maintenance), issue resolution (responsive maintainers), release frequency (regular updates), and community size (GitHub stars, npm downloads). Abandoned dependencies become security risks and maintenance burdens. Prefer dependencies with active maintainers and regular releases.

**Security Posture**: Review known vulnerabilities (GitHub Advisory Database, Snyk), security practices (security policy, responsible disclosure), and dependency health (dependency scanning results). Dependencies with known vulnerabilities or poor security practices introduce risk. Prefer dependencies with good security track records.

**License Compatibility**: Verify license compatibility with organizational policies. Check for copyleft licenses (GPL, AGPL) that might affect commercial software. Use license scanning tools to identify all licenses, including transitive dependencies. Prefer permissive licenses (MIT, Apache 2.0) when possible.

**Bundle Size Impact**: For frontend dependencies, consider bundle size impact. Large dependencies increase load times and impact user experience. Use bundle analysis tools (webpack-bundle-analyzer, source-map-explorer) to understand size impact. Consider alternatives or code splitting for large dependencies.

**Alternatives**: Research alternatives before adding dependencies. Sometimes built-in language features or smaller libraries suffice. Evaluate alternatives based on maintenance, security, license, and bundle size. Prefer standard library solutions when available.

**Example: Dependency Evaluation Checklist**

```typescript
// Before adding a dependency, ask:
// 1. Is it actively maintained? (check GitHub commits, releases)
// 2. Are there known vulnerabilities? (check GitHub Advisory, Snyk)
// 3. Is the license compatible? (check license file, use license scanner)
// 4. What's the bundle size? (check bundlephobia.com for npm packages)
// 5. Are there alternatives? (research similar libraries)
// 6. Is it widely adopted? (check GitHub stars, npm downloads)
```

## Prefer Widely-Adopted Over Niche

Widely-adopted dependencies have larger communities, more maintainers, better documentation, and faster security response. Niche dependencies may have fewer users, slower updates, and higher abandonment risk. Prefer widely-adopted dependencies when alternatives exist.

**Community Size Indicators**: GitHub stars, npm weekly downloads, Stack Overflow questions, and blog posts indicate adoption. Large communities provide more support, better documentation, and faster bug fixes. However, don't choose based solely on popularity—evaluate other factors too.

**Maintenance Benefits**: Widely-adopted dependencies are more likely to have active maintainers, regular updates, and security patches. Popular dependencies attract contributors and maintainers, reducing abandonment risk. Niche dependencies may have single maintainers who can become unavailable.

**Documentation and Support**: Popular dependencies have better documentation, tutorials, and community support. When issues arise, you're more likely to find solutions online or get help from the community. Niche dependencies may have limited documentation and support.

**Security Response**: Popular dependencies receive faster security patches because vulnerabilities affect more users and attract security researcher attention. Niche dependencies may have slower security response or unpatched vulnerabilities.

**When Niche is Acceptable**: Sometimes niche dependencies are necessary for specific requirements or better fit than popular alternatives. Evaluate niche dependencies more carefully, but don't avoid them entirely if they're the best fit. Consider maintaining forks or contributing to niche dependencies to ensure their health.

## Pin Production Dependencies, Use Ranges in Libraries

Production applications should pin dependencies to exact versions (or use narrow ranges with lock files) to ensure reproducible builds and prevent unexpected updates. Libraries should use version ranges to allow consumers flexibility.

**Production Applications**: Pin dependencies to exact versions (e.g., `"lodash": "4.17.21"`) or use narrow ranges with lock files (e.g., `"lodash": "^4.17.21"` with package-lock.json). Pinned versions ensure all environments (development, CI/CD, production) use the same dependency versions, preventing "works on my machine" problems.

**Libraries**: Use version ranges (e.g., `"lodash": "^4.17.21"`) to allow consumers to use compatible versions. Ranges provide flexibility while maintaining compatibility. However, test libraries against multiple dependency versions to ensure compatibility across the range.

**Lock Files**: Always commit lock files (package-lock.json, gradle.lockfile) for applications. Lock files pin exact versions of all dependencies, including transitive ones, ensuring reproducible builds. Don't commit lock files for libraries—libraries need flexibility.

**Version Strategy Examples**:

```json
// package.json for production application
{
  "dependencies": {
    "lodash": "^4.17.21",  // Narrow range with lock file
    "axios": "1.6.0"        // Pinned for critical dependency
  }
}
```

```kotlin
// build.gradle.kts for production application
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3") // Pinned
    implementation("com.fasterxml.jackson.core:jackson-databind") {
        version {
            strictly("2.15.2") // Strict version with lock file
        }
    }
}
```

## Automate Dependency Upgrades

Automated dependency upgrade tools (Renovate, Dependabot) reduce manual overhead and keep dependencies current with security patches. Configure automation to create pull requests for updates, run CI/CD pipelines, and auto-merge low-risk updates.

**Renovate Configuration**: Renovate provides extensive configuration options for update schedules, grouping strategies, and auto-merge rules. Configure Renovate to group patch updates, create separate PRs for major versions, and auto-merge when CI passes.

**Example: Renovate Configuration (renovate.json)**

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "groupName": "patch updates",
      "automerge": true,
      "automergeType": "pr",
      "schedule": ["before 10am on monday"]
    },
    {
      "matchUpdateTypes": ["minor"],
      "groupName": "minor updates",
      "automerge": false,
      "schedule": ["before 10am on monday"]
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "schedule": ["before 10am on monday"],
      "prTitle": "🚀 {{depName}} major update"
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true,
      "automergeType": "pr"
    }
  ],
  "dependencyDashboard": true,
  "lockFileMaintenance": {
    "enabled": true,
    "schedule": ["before 10am on monday"]
  }
}
```

**Dependabot Configuration**: Dependabot is GitHub-native and provides simpler configuration than Renovate. Configure Dependabot for update frequency, grouping, and auto-merge.

**Example: Dependabot Configuration (.github/dependabot.yml)**

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    groups:
      production-dependencies:
        patterns:
          - "*"
        update-types:
          - "patch"
    ignore:
      - dependency-name: "eslint"
        update-types: ["version-update:semver-major"]
    commit-message:
      prefix: "chore"
      include: "scope"
  
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
```

**Auto-merge Strategy**: Enable auto-merge for patch updates when CI passes, but require manual review for major versions and critical dependencies. Auto-merge reduces manual overhead while maintaining safety through automated testing. Configure branch protection rules to ensure reviews are required when appropriate.

## Review Transitive Dependencies

Transitive dependencies (dependencies of dependencies) form the majority of an application's dependency tree. Review transitive dependencies to understand security risks, license obligations, and maintenance burden.

**Inspecting Transitive Dependencies**: Use `npm ls --depth=10` (npm), `gradle dependencies` (Gradle), or `yarn list` (Yarn) to view the full dependency tree. Understanding transitive dependencies helps identify security vulnerabilities, license issues, and opportunities to reduce dependencies.

**Security Scanning**: Dependency scanning tools (Snyk, Dependabot) identify vulnerabilities in transitive dependencies. Review scan results to understand which transitive dependencies have vulnerabilities and how to fix them. Fixing transitive vulnerabilities often requires updating direct dependencies.

**License Compliance**: Transitive dependencies carry license obligations. License scanning tools identify licenses for all dependencies, including transitive ones. Ensure license policies account for transitive dependencies, not just direct dependencies.

**Dependency Reduction**: Sometimes transitive dependencies can be reduced by choosing different direct dependencies or using alternatives. Review transitive dependencies to identify opportunities to reduce the dependency tree, which reduces maintenance burden and security risk.

**Example: Inspecting Transitive Dependencies**

```bash
# npm
npm ls --depth=10

# Gradle
./gradlew dependencies --configuration runtimeClasspath

# Yarn
yarn list --depth=10
```

## Maintain Lock File Hygiene

Lock files ensure reproducible builds but require maintenance. Keep lock files up to date, resolve merge conflicts promptly, and regenerate lock files when dependency resolution changes.

**Commit Lock Files**: Always commit lock files (package-lock.json, gradle.lockfile) for applications. Lock files pin exact dependency versions, ensuring reproducible builds. Don't commit lock files for libraries—libraries need flexibility.

**Resolve Lock File Conflicts**: Lock file merge conflicts require regenerating lock files by running package managers (npm install, gradle dependencies --write-locks). Resolve conflicts promptly to avoid blocking other developers. Automated tools (Renovate, Dependabot) can reduce conflicts by creating separate PRs for updates.

**Regenerate Lock Files**: Regenerate lock files when dependency resolution changes (e.g., after updating package manager versions, changing resolution strategies). Regeneration ensures lock files reflect current resolution behavior.

**Lock File Maintenance**: Some tools (Renovate) can maintain lock files automatically, updating them when dependencies change. Enable lock file maintenance to reduce manual overhead while ensuring lock files stay current.

## Monitor Dependency Health

Monitor dependency health to identify abandoned dependencies, security vulnerabilities, and maintenance issues. Regular monitoring enables proactive dependency management and prevents problems from accumulating.

**Dependency Health Metrics**: Track metrics like: last update date, open issue count, vulnerability count, and download trends. Declining metrics indicate dependency health issues. Set up alerts for dependencies that haven't been updated in 6+ months or have increasing vulnerability counts.

**Security Monitoring**: Monitor security advisories for dependencies. Subscribe to security feeds (GitHub Advisory Database, Snyk) and set up alerts for vulnerabilities in your dependencies. Rapid response to security advisories reduces risk.

**Maintenance Monitoring**: Monitor dependency maintenance status. Dependencies with inactive maintainers, unresolved issues, or declining downloads may become abandoned. Identify alternatives before dependencies become unmaintained.

**Automated Monitoring**: Use tools (Renovate, Snyk) that monitor dependency health automatically and create alerts or PRs when issues are detected. Automated monitoring reduces manual effort and ensures issues are detected promptly.

## Stack-Specific Practices

### Gradle (Kotlin/Java)

**Version Catalogs**: Use version catalogs to centralize version management across projects. Version catalogs provide a single source of truth for dependency versions, making upgrades easier and ensuring consistency.

**Example: Gradle Version Catalog (gradle/libs.versions.toml)**

```toml
[versions]
kotlin = "1.9.20"
spring-boot = "3.2.0"
jackson = "2.15.2"
coroutines = "1.7.3"

[libraries]
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }

[bundles]
spring = ["spring-boot-starter-web", "spring-boot-starter-validation"]
```

**Example: Using Version Catalog (build.gradle.kts)**

```kotlin
dependencies {
    val libs = versionCatalogs.named("libs")
    
    implementation(libs.findLibrary("kotlin-stdlib").get())
    implementation(libs.findBundle("spring").get())
    implementation(libs.findLibrary("jackson-databind").get())
    implementation(libs.findLibrary("kotlinx-coroutines-core").get())
}
```

**Dependency Locking**: Enable dependency locking for reproducible builds. Lock files pin exact versions of all dependencies, including transitive ones.

**Example: Enabling Dependency Locking**

```kotlin
// settings.gradle.kts
dependencyLocking {
    lockAllConfigurations()
}

// build.gradle.kts
configurations {
    all {
        resolutionStrategy {
            activateDependencyLocking()
        }
    }
}
```

### npm/package.json (Vue/React)

**Pinned Versions with Lock Files**: Use pinned versions or narrow ranges (^) with package-lock.json for production applications. Lock files ensure reproducible builds.

**Example: package.json with Pinned Versions**

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "4.2.5",
    "axios": "^1.6.0",
    "lodash": "4.17.21"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  },
  "overrides": {
    "lodash": "4.17.21"
  }
}
```

**Overrides for Transitive Dependencies**: Use `overrides` (npm) or `resolutions` (Yarn) to force specific versions of transitive dependencies when needed. Use overrides sparingly—prefer updating direct dependencies.

**Example: Overrides Configuration**

```json
{
  "overrides": {
    "lodash": "4.17.21",
    "axios": {
      ".": "^1.6.0",
      "follow-redirects": "^1.15.0"
    }
  }
}
```

These best practices provide a foundation for effective dependency management across technologies. Adapt practices to your organization's needs, but maintain core principles: evaluate before adding, automate upgrades, monitor health, and maintain lock files.
