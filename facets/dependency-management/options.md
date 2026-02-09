# Dependency Management -- Options

## Contents

- [Automated Upgrade Tools](#automated-upgrade-tools)
- [Version Strategies](#version-strategies)

Decision matrices for dependency management technology choices. Each option is evaluated against criteria relevant to maintenance burden, security, developer experience, and integration complexity.

## Automated Upgrade Tools

Automated dependency upgrade tools reduce manual overhead and keep dependencies current with security patches. The choice between Renovate, Dependabot, or manual updates impacts developer experience, configurability, and maintenance burden.

### Renovate

**Description**: Highly configurable automated dependency update tool supporting multiple Git hosting platforms (GitHub, GitLab, Bitbucket). Renovate provides extensive configuration options for update schedules, grouping strategies, auto-merge rules, and custom update policies.

**Strengths**:
- Extensive configuration options for fine-grained control
- Supports multiple Git hosting platforms (GitHub, GitLab, Bitbucket, Azure DevOps)
- Advanced grouping strategies (group by update type, ecosystem, path)
- Customizable PR titles, labels, and commit messages
- Dependency dashboard for visibility into all updates
- Supports monorepos with workspace-aware updates
- Can group updates intelligently to reduce PR noise
- Lock file maintenance automation
- Configurable auto-merge based on update type and CI status

**Weaknesses**:
- Steeper learning curve due to extensive configuration options
- Requires configuration file (renovate.json) for advanced features
- Self-hosted option requires infrastructure (though GitHub App is available)
- May require tuning to reduce PR noise in large repositories
- Configuration can become complex for large monorepos

**Best For**:
- Organizations requiring fine-grained control over update policies
- Monorepos requiring workspace-aware updates
- Teams wanting to reduce PR noise through intelligent grouping
- Multi-platform Git hosting (GitHub + GitLab)
- Organizations preferring configuration-as-code for update policies
- Teams wanting dependency dashboards and visibility

**Avoid When**:
- Simple use cases that don't require advanced configuration
- Teams preferring minimal configuration and setup
- GitHub-only workflows where Dependabot's simplicity suffices
- Small projects where manual updates are manageable

### Dependabot

**Description**: GitHub-native automated dependency update tool integrated with GitHub's dependency graph and security advisories. Dependabot provides simpler configuration than Renovate but with less flexibility.

**Strengths**:
- Native GitHub integration with dependency graph and security advisories
- Simple YAML configuration (.github/dependabot.yml)
- Automatic security update PRs for known vulnerabilities
- Free for all GitHub repositories (public and private)
- Low configuration overhead—works out of the box
- Integrated with GitHub's security features
- Supports grouping updates (limited compared to Renovate)
- Auto-merge support when CI passes

**Weaknesses**:
- GitHub-only (doesn't support GitLab, Bitbucket)
- Less configurable than Renovate (fewer grouping options, less customization)
- May create many PRs without careful configuration
- Limited monorepo support compared to Renovate
- Less flexible update scheduling and policies
- No dependency dashboard (relies on GitHub's dependency graph)

**Best For**:
- GitHub-based workflows
- Teams preferring simple configuration
- Organizations wanting GitHub-native integration
- Use cases where basic automated updates suffice
- Teams wanting automatic security update PRs
- Small to medium-sized projects

**Avoid When**:
- Requirements for advanced configuration and grouping
- Multi-platform Git hosting (GitLab, Bitbucket)
- Large monorepos requiring workspace-aware updates
- Teams needing dependency dashboards and advanced visibility
- Use cases requiring fine-grained update policies

### Manual Updates

**Description**: Manually reviewing and updating dependencies without automated tools. Manual updates provide full control but require significant time and effort.

**Strengths**:
- Full control over update timing and process
- No tool configuration or maintenance
- Can review all updates before applying
- No PR noise or automated tool issues
- Works with any Git hosting platform
- No dependency on third-party tools

**Weaknesses**:
- High manual overhead—time-consuming and error-prone
- Dependencies often become stale without regular updates
- Security patches may be delayed or missed
- Requires discipline to maintain update schedule
- Doesn't scale to large dependency lists
- Easy to forget or postpone updates
- No automated detection of available updates

**Best For**:
- Very small projects with few dependencies
- Teams with dedicated dependency management resources
- Use cases requiring strict control over updates
- Projects where automated tools aren't feasible
- Temporary situations while evaluating automated tools

**Avoid When**:
- Projects with many dependencies
- Teams wanting to reduce manual overhead
- Requirements for rapid security patching
- Organizations wanting consistent update processes
- Use cases where automation provides clear value

### Evaluation Criteria

**Configurability**: How much control does the tool provide over update policies, grouping, scheduling, and auto-merge? Renovate provides extensive configurability, Dependabot provides moderate configurability, and manual updates provide full control but no automation.

**Monorepo Support**: How well does the tool handle monorepos with multiple packages and workspace dependencies? Renovate provides excellent monorepo support, Dependabot provides basic support, and manual updates work but require significant effort.

**PR Management**: How does the tool manage pull requests to reduce noise and maintainability? Renovate provides advanced grouping and scheduling, Dependabot provides basic grouping, and manual updates create PRs only when needed.

**Ecosystem Support**: Which package managers and ecosystems does the tool support? Both Renovate and Dependabot support major ecosystems (npm, Maven, Gradle, etc.), while manual updates work with any ecosystem.

**Developer Experience**: How easy is the tool to set up, configure, and use? Dependabot provides the simplest experience, Renovate requires more configuration but offers more power, and manual updates require no setup but significant ongoing effort.

**Security Integration**: How well does the tool integrate with security scanning and vulnerability databases? Dependabot integrates with GitHub's security advisories, Renovate supports security scanning integrations, and manual updates require separate security scanning.

### Recommendation Guidance

**Start with Dependabot** if you're using GitHub and want simple, effective automated updates. Dependabot's GitHub-native integration and simple configuration provide immediate value with minimal overhead. Dependabot is sufficient for most projects.

**Choose Renovate** if you need advanced configuration, monorepo support, or multi-platform Git hosting. Renovate's extensive configurability and grouping strategies reduce PR noise and provide fine-grained control. Renovate is ideal for large projects and monorepos.

**Use manual updates** only for very small projects or when automated tools aren't feasible. Manual updates don't scale and are error-prone, but they provide full control when needed.

**Evolution triggers**: Move from manual updates to Dependabot when dependency count grows or security patching becomes important. Move from Dependabot to Renovate when you need advanced configuration, monorepo support, or multi-platform hosting.

### Synergies with Other Facets

**CI/CD Integration**: Both Renovate and Dependabot integrate with CI/CD pipelines, running tests automatically on update PRs. CI/CD validation ensures updates don't break applications before merging. See the [CI/CD facet](../ci-cd/) for integration patterns.

**Security Scanning**: Automated update tools complement security scanning by keeping dependencies current with security patches. Security scanning identifies vulnerabilities, while update tools apply fixes. See the [Security facet](../security/) for vulnerability management.

**Testing**: Update PRs trigger test suites, validating that upgrades don't break functionality. Comprehensive test coverage increases confidence in automated updates. See the [Testing facet](../testing/) for upgrade testing strategies.

## Version Strategies

Version strategies determine how dependency versions are specified and updated. Different strategies balance stability, security, and maintenance burden.

### Pinned Versions

**Description**: Specify exact dependency versions (e.g., `"lodash": "4.17.21"`), ensuring reproducible builds and preventing unexpected updates.

**Strengths**:
- Maximum stability—no unexpected updates
- Reproducible builds across environments
- Predictable behavior—versions don't change
- Easy to reason about—exact versions are clear
- Prevents "works on my machine" problems

**Weaknesses**:
- Requires manual updates for security patches
- Dependencies can become stale without regular updates
- Security vulnerabilities may remain unpatched
- Higher maintenance burden—manual updates required
- Doesn't benefit from bug fixes and improvements

**Best For**:
- Production applications requiring maximum stability
- Critical dependencies where breaking changes are unacceptable
- Applications with infrequent update cycles
- Use cases where reproducibility is more important than updates
- Core frameworks that define application architecture

**Avoid When**:
- Requirements for rapid security patching
- Dependencies that receive frequent security updates
- Use cases where staying current provides value
- Libraries (should use ranges for consumer flexibility)

### Caret Ranges (^)

**Description**: Allow updates that don't change the leftmost non-zero digit (e.g., `"lodash": "^4.17.21"` allows `4.17.22`, `4.18.0`, but not `5.0.0`).

**Strengths**:
- Balance between stability and updates
- Allows patch and minor updates automatically
- Prevents major breaking changes
- Reduces manual update overhead
- Benefits from bug fixes and security patches
- Works well with lock files for reproducibility

**Weaknesses**:
- Minor versions may introduce breaking changes (rare)
- Requires testing to ensure compatibility
- Less predictable than pinned versions
- May require lock files for reproducibility

**Best For**:
- Production applications wanting updates with stability
- Dependencies where minor updates are generally safe
- Use cases balancing stability and security patching
- Applications with lock files ensuring reproducibility
- Most common strategy for production applications

**Avoid When**:
- Maximum stability requirements (use pinned)
- Dependencies with frequent breaking minor versions
- Use cases where any change is unacceptable

### Tilde Ranges (~)

**Description**: Allow updates that only change the patch version (e.g., `"lodash": "~4.17.21"` allows `4.17.22` but not `4.18.0`).

**Strengths**:
- Maximum stability while allowing security patches
- Only patch updates allowed (lowest risk)
- Prevents minor version changes
- More predictable than caret ranges
- Works well with lock files

**Weaknesses**:
- Doesn't benefit from minor version improvements
- May miss important bug fixes in minor versions
- Still requires testing for patch updates
- Less flexible than caret ranges

**Best For**:
- Production applications requiring maximum stability
- Dependencies where patch updates are sufficient
- Use cases where minor updates aren't needed
- Critical dependencies where any change is risky

**Avoid When**:
- Requirements for minor version updates
- Dependencies that improve significantly in minor versions
- Use cases where flexibility is valuable

### Latest

**Description**: Always use the latest version (e.g., `"lodash": "latest"`), providing maximum updates but maximum risk.

**Strengths**:
- Always current with latest features and fixes
- Maximum updates and improvements
- No version management overhead
- Benefits from all updates immediately

**Weaknesses**:
- Can introduce breaking changes without warning
- Unpredictable behavior—versions change frequently
- High risk of production issues
- Difficult to reproduce builds
- Not suitable for production applications

**Best For**:
- Development tools and build dependencies
- Use cases where latest features are critical
- Projects actively maintaining dependencies
- Non-production dependencies

**Avoid When**:
- Production applications (too risky)
- Requirements for stability and reproducibility
- Dependencies that introduce frequent breaking changes
- Use cases where predictability is important

### Evaluation Criteria

**Stability**: How predictable and stable are dependency versions? Pinned versions provide maximum stability, ranges provide moderate stability, and latest provides minimal stability.

**Security**: How quickly can security patches be applied? Latest provides fastest patching, ranges provide moderate speed, and pinned requires manual updates.

**Maintenance Burden**: How much effort is required to maintain dependencies? Latest requires minimal effort, ranges require moderate effort, and pinned requires significant effort.

**Reproducibility**: How reproducible are builds across environments? Pinned versions provide maximum reproducibility, ranges with lock files provide good reproducibility, and latest provides minimal reproducibility.

**Flexibility**: How flexible are version constraints for consumers (libraries)? Latest provides maximum flexibility, ranges provide moderate flexibility, and pinned provides minimal flexibility.

### Recommendation Guidance

**Use pinned versions with lock files** for production applications requiring maximum stability and reproducibility. Lock files ensure exact versions while allowing flexibility in version declarations.

**Use caret ranges (^) with lock files** for most production applications, balancing stability with security patching. This is the most common strategy and works well with automated update tools.

**Use tilde ranges (~)** for critical dependencies where only patch updates are acceptable. Tilde ranges provide maximum stability while allowing security patches.

**Use latest** only for development tools and non-production dependencies. Latest is too risky for production applications.

**Evolution triggers**: Start with caret ranges for flexibility, move to pinned versions if stability issues occur, or move to latest (carefully) if rapid updates are critical and breaking changes are manageable.

### Synergies with Other Facets

**Lock Files**: Version strategies work best with lock files, which pin exact versions regardless of range specifications. Lock files ensure reproducibility while allowing flexible version declarations. See [Architecture](architecture.md) for lock file details.

**Automated Updates**: Version ranges enable automated update tools to apply patches and minor updates automatically. Pinned versions require manual updates, reducing automation benefits. See automated upgrade tools above.

**Security Scanning**: Version strategies affect how quickly security patches can be applied. Ranges enable faster patching than pinned versions, while latest provides fastest patching but highest risk. See the [Security facet](../security/) for vulnerability management.

These decision matrices provide guidance for common dependency management choices. However, specific requirements may override general recommendations. Evaluate options against your organization's needs, constraints, and risk tolerance.
