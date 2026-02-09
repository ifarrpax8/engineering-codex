# Dependency Management -- Gotchas

## Contents

- [Phantom Dependencies](#phantom-dependencies)
- [Version Conflicts in Monorepos](#version-conflicts-in-monorepos)
- [Lock File Merge Conflicts](#lock-file-merge-conflicts)
- [Renovate/Dependabot Noise](#renovatedependabot-noise)
- [Major Version Bumps Breaking Silently](#major-version-bumps-breaking-silently)
- [License Traps](#license-traps)
- [npm audit False Positives](#npm-audit-false-positives)
- [Transitive Dependency Vulnerabilities](#transitive-dependency-vulnerabilities)

Common dependency management pitfalls that seem harmless but create real problems. These gotchas slip through code reviews and seem minor until they cause production incidents or security vulnerabilities.

## Phantom Dependencies

**The trap**: Using transitive dependencies directly without declaring them as direct dependencies. For example, using `lodash` methods when `lodash` is only a transitive dependency of another package.

**Why it's wrong**: Transitive dependencies can be removed or updated by their parent dependencies, breaking your code. If the parent dependency updates and removes `lodash` as a dependency, your code that uses `lodash` directly will break. Phantom dependencies create fragile code that depends on implementation details of other dependencies.

**The fix**: Always declare dependencies you use directly, even if they're available transitively. If you use `lodash` methods, add `lodash` to your dependencies. This makes your dependency requirements explicit and prevents breakage when transitive dependencies change.

**Detection**: Use tools like `depcheck` (npm) or `unused-deps` to identify phantom dependencies. These tools scan your code for imports and compare them to declared dependencies, identifying missing declarations.

**Example**: 

```javascript
// ❌ Bad: Using lodash without declaring it
// lodash is a transitive dependency of another package
import { debounce } from 'lodash';

// ✅ Good: Declare lodash as a direct dependency
// package.json
{
  "dependencies": {
    "lodash": "^4.17.21"
  }
}
```

## Version Conflicts in Monorepos

**The trap**: Different packages in a monorepo requiring different versions of the same dependency, causing conflicts and duplication.

**Why it's wrong**: Version conflicts in monorepos can result in multiple versions of the same package being installed, increasing bundle size and creating potential compatibility issues. Different packages using different versions of the same dependency can cause subtle bugs when data is passed between packages.

**The fix**: Use version catalogs (Gradle) or shared package.json files to centralize version management. Align dependency versions across packages when possible. Use workspace protocols to ensure packages use compatible versions. When conflicts are unavoidable, document why and ensure compatibility.

**Prevention**: Establish version alignment policies for monorepos. Use tools to detect version conflicts and align versions proactively. Consider using a single version for shared dependencies across packages.

**Example**:

```kotlin
// ❌ Bad: Different versions across packages
// package-a/build.gradle.kts
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.14.0")
}

// package-b/build.gradle.kts  
dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.15.0")
}

// ✅ Good: Use version catalog for consistency
// gradle/libs.versions.toml
[versions]
jackson = "2.15.2"

// Both packages use the same version
```

## Lock File Merge Conflicts

**The trap**: Lock files (package-lock.json, gradle.lockfile) create frequent merge conflicts when multiple developers update dependencies simultaneously.

**Why it's wrong**: Lock file conflicts are tedious to resolve and block developers from merging. Resolving conflicts requires regenerating lock files, which can be time-consuming and error-prone. Frequent conflicts slow down development and create frustration.

**The fix**: Use automated dependency update tools (Renovate, Dependabot) that create separate PRs for updates, reducing simultaneous manual updates. Configure tools to group updates and schedule them to reduce conflict frequency. When conflicts occur, regenerate lock files by running package managers rather than manually editing.

**Prevention**: Establish processes for dependency updates (e.g., scheduled update days, automated updates for patches). Use tools that handle lock file updates automatically. Consider using tools that can resolve conflicts automatically.

**Resolution**: When conflicts occur, regenerate lock files by running `npm install`, `gradle dependencies --write-locks`, or `yarn install`. Don't manually edit lock files—regeneration ensures correctness.

## Renovate/Dependabot Noise

**The trap**: Automated dependency update tools create too many pull requests, overwhelming developers with review work.

**Why it's wrong**: Too many PRs create noise and make it hard to identify important updates. Developers may ignore PRs or merge them without proper review, defeating the purpose of automated updates. PR fatigue reduces the effectiveness of automated tools.

**The fix**: Configure grouping strategies to combine related updates. Group patch updates together, create separate PRs for major versions, and schedule updates (e.g., weekly batches). Use auto-merge for low-risk updates (patches) when CI passes, reducing manual review burden.

**Configuration**: Use Renovate's grouping features or Dependabot's grouping to combine updates. Set `open-pull-requests-limit` to limit concurrent PRs. Schedule updates to reduce frequency.

**Example: Reducing PR Noise**

```json
// renovate.json
{
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "groupName": "patch updates",
      "schedule": ["before 10am on monday"],
      "automerge": true
    }
  ],
  "prConcurrentLimit": 5
}
```

## Major Version Bumps Breaking Silently

**The trap**: Major version upgrades that pass tests but break in production due to subtle behavior changes, type changes, or removed APIs that aren't covered by tests.

**Why it's wrong**: Major versions often introduce breaking changes that tests don't catch. Type changes (TypeScript types that remain compatible but behavior changes), removed APIs (deprecated APIs that were removed), and behavior changes (subtle runtime differences) can break production even when tests pass.

**The fix**: Review changelogs and migration guides before major upgrades. Test critical flows manually, not just with automated tests. Use type checking to catch type-level breaking changes. Plan major upgrades as separate work items with dedicated testing time, not routine maintenance.

**Prevention**: Stay current with dependency updates to avoid large version gaps. Large gaps make upgrades riskier and harder to test. Use automated tools to keep dependencies current, reducing the impact of major upgrades.

**Testing**: For major upgrades, perform comprehensive testing including: full test suite execution, manual testing of critical flows, review of migration guides, and potentially refactoring code to adapt to breaking changes.

**Example**:

```typescript
// ❌ Silent breakage: Type changes that pass type checking
// Old version: function returns string | null
// New version: function returns string | undefined
// TypeScript doesn't catch this, but runtime behavior changes

// ✅ Review migration guide and test manually
// Check changelog for breaking changes
// Test return value handling explicitly
```

## License Traps

**The trap**: Adding dependencies with copyleft licenses (GPL, AGPL) in commercial software, creating legal risks and distribution restrictions.

**Why it's wrong**: Copyleft licenses require derivative works to use the same license, potentially forcing open-sourcing of proprietary code. AGPL extends GPL requirements to software accessed over networks, affecting SaaS applications. License violations can result in legal action or inability to distribute software.

**The fix**: Scan dependencies for licenses before adding them. Use license scanning tools (FOSSA, Snyk) to identify licenses, including transitive dependencies. Establish license policies that prohibit copyleft licenses in commercial software. Block dependencies with prohibited licenses in CI/CD.

**Detection**: Use license scanning tools that identify licenses for all dependencies, including transitive ones. Configure CI/CD to fail builds when prohibited licenses are detected.

**Prevention**: Include license review in dependency approval processes. Document license policies and ensure developers understand them. Use automated license scanning to enforce policies.

**Example**:

```json
// ❌ Bad: GPL dependency in commercial software
{
  "dependencies": {
    "some-gpl-library": "^1.0.0"  // GPL license - legal risk
  }
}

// ✅ Good: Use permissive license alternative
{
  "dependencies": {
    "mit-licensed-alternative": "^1.0.0"  // MIT license - safe
  }
}
```

## npm audit False Positives

**The trap**: `npm audit` reporting vulnerabilities in dependencies that aren't actually used or are in devDependencies that don't affect production.

**Why it's wrong**: npm audit can report vulnerabilities in transitive dependencies that aren't actually used, or in devDependencies that don't affect production. False positives create noise and waste time investigating non-issues. Some vulnerabilities require specific conditions to be exploitable that don't exist in your application.

**The fix**: Review audit findings carefully. Check if vulnerable code paths are actually used in your application. Verify if vulnerabilities affect production dependencies or only devDependencies. Use `npm audit --production` to scan only production dependencies. Suppress false positives with `npm audit fix --force` only after verification.

**Understanding**: Not all vulnerabilities are equally severe. Check CVSS scores and exploitability information. Some vulnerabilities require specific conditions (network access, specific configurations) that don't apply to your application.

**Example**:

```bash
# Check production dependencies only
npm audit --production

# Review specific vulnerability
npm audit lodash

# Suppress false positive (use carefully)
npm audit fix --force
```

## Transitive Dependency Vulnerabilities

**The trap**: Vulnerabilities in transitive dependencies that can't be fixed by updating direct dependencies, requiring overrides or waiting for parent dependencies to update.

**Why it's wrong**: Transitive dependency vulnerabilities are harder to fix because you don't control the direct dependency that depends on the vulnerable transitive dependency. You may need to wait for the parent dependency to update, use overrides (which can cause compatibility issues), or find alternative dependencies.

**The fix**: Use dependency scanning tools (Snyk, Dependabot) that identify transitive vulnerabilities and suggest fixes. Update direct dependencies when possible—they may have updated to versions that use patched transitive dependencies. Use overrides sparingly and test thoroughly when forcing versions. Consider alternative dependencies if fixes aren't available.

**Prevention**: Choose direct dependencies with good security practices and rapid security response. Dependencies that quickly patch transitive vulnerabilities reduce your exposure.

**Example**:

```json
// Vulnerable transitive dependency: axios@1.5.0 depends on follow-redirects@1.14.0
// follow-redirects@1.14.0 has a vulnerability

// Option 1: Update axios (if newer version uses patched follow-redirects)
{
  "dependencies": {
    "axios": "^1.6.0"  // Uses follow-redirects@1.15.0 (patched)
  }
}

// Option 2: Override transitive dependency (use carefully)
{
  "overrides": {
    "follow-redirects": "^1.15.0"
  }
}
```

These gotchas represent common dependency management mistakes that seem minor but create real problems. Awareness of these pitfalls helps prevent them during development and dependency management. When in doubt, be explicit about dependencies, review updates carefully, and test thoroughly.
