# Options: Refactoring & Extraction Decision Framework

## Recommended Refactoring Approach

**Default: Continuous Small Refactoring**

The default approach is continuous small refactoring as part of regular feature work, following the Boy Scout Rule. When you touch code to add a feature, make small improvements: rename unclear variables, extract a method, add missing types. This prevents debt accumulation without requiring dedicated refactoring sprints.

Continuous small refactoring compounds over time. Each developer makes small improvements, and the codebase gradually improves. This approach is low risk: small changes are easy to understand, review, and test. They can be committed frequently and reverted easily if issues arise.

This approach works best when the codebase is generally healthy and technical debt is manageable. Small improvements prevent debt accumulation without requiring significant time investment. They can be done as part of feature work without separate planning.

**For Larger Refactoring: Dedicated Refactoring PRs**

For larger refactorings that exceed the scope of the Boy Scout Rule, use dedicated refactoring pull requests before feature work. These refactorings should be time-boxed and well-scoped. They should be separate from feature work to enable independent review and validation.

Dedicated refactoring PRs enable focused review. Reviewers can evaluate refactoring quality without being distracted by feature logic. After refactoring is merged, feature PRs are simpler and easier to review. This reduces risk and improves code quality.

Time-box refactoring efforts to prevent scope creep. If a refactoring is taking longer than expected, stop and reassess. Create follow-up tasks for additional improvements. Don't let refactoring expand indefinitely.

**For Architectural Extraction: Strangler Fig Pattern**

For architectural extractions (extracting services from monoliths, splitting frontends into micro-frontends), use the Strangler Fig Pattern with feature flags, parallel running, and gradual migration. This approach reduces risk by enabling incremental migration and instant rollback.

The Strangler Fig Pattern enables gradual migration. New functionality goes to the new system. Old functionality gradually migrates. Both systems run in parallel. Feature flags control routing. This approach reduces risk: if the new system has issues, traffic can be routed back to the old system.

Architectural extraction requires careful planning. Identify boundaries, build new systems alongside old ones, route traffic gradually, and remove old code only when migration is complete. This approach takes time but reduces risk significantly.

## Refactoring Trigger Decision Guide

### When to Refactor NOW (Blocking Current Work)

Refactor immediately when code blocks current work. If implementing a feature requires understanding complex, poorly-structured code, refactor that code first. The refactoring enables the feature, and the feature work validates that the refactoring improved maintainability.

Refactor when code has bugs that are difficult to fix due to structure. If fixing a bug requires understanding complex, intertwined code, refactor first. The refactoring makes the bug fix easier and prevents similar bugs in the future.

Refactor when onboarding developers consistently struggle with an area. If new team members consistently ask questions about the same code or make mistakes in the same area, that code needs refactoring. Clear, well-structured code is easier to understand and less error-prone.

### When to Refactor SOON (Schedule It)

Schedule refactoring when code smells are accumulating in a frequently-changed area. If an area is modified frequently and code smells are accumulating, refactoring will provide value. The area is actively used, so improvements will have immediate payoff.

Schedule refactoring when technical debt interest is measurably slowing development. If developer velocity is declining, bug rates are increasing, or time-to-implement is increasing, technical debt is accumulating. Refactoring can reverse these trends.

Schedule refactoring when upcoming features will be significantly harder without it. If planned features will require understanding or modifying complex code, refactoring that code now will make future features easier. However, don't refactor speculatively: ensure features are actually planned.

### When NOT to Refactor

Don't refactor code that works, is rarely changed, and doesn't block anything. Refactoring has risk. Focus that risk on code that's actively being modified, where the investment has immediate payoff. Stable, infrequently-changed code may have technical debt, but refactoring it provides little value.

Don't refactor when you want to "clean it up" but have no concrete benefit. Refactoring should have a purpose: enabling a feature, fixing a bug, or improving maintainability. Refactoring for its own sake introduces risk without providing value.

Don't refactor when you're about to deprecate or replace the system. If a system is scheduled for replacement, refactoring it is wasteful. Focus effort on the replacement system instead.

Don't refactor when you don't have adequate test coverage. Refactoring without tests is risky. Write characterization tests first, then refactor. Tests provide a safety net that enables confident refactoring.

## Extraction Readiness Checklist

Before extracting code, verify readiness using this checklist. Extraction is more complex than refactoring and requires careful planning.

**Pattern Seen at Least 3 Times**

The pattern must be seen at least three times before extraction. The Rule of Three ensures the abstraction is based on real patterns, not speculation. The first occurrence might be coincidence. The second might still be coincidence. The third confirms a pattern.

Extracting after the first or second occurrence creates wrong abstractions. Wait until the pattern is clear. The abstraction will fit naturally because it's derived from actual needs, not anticipated needs.

**Test Coverage Exists**

Adequate test coverage must exist for the code being extracted. Tests provide a safety net: they verify that behavior remains unchanged after extraction. If test coverage is inadequate, write characterization tests first.

Tests should cover the boundary of what's being extracted. If extracting a module, test the module's API. If extracting a service, test the service's interface. Boundary tests verify that extraction preserves behavior.

**Clear Boundary/Interface Can Be Defined**

A clear boundary or interface must be definable for what's being extracted. The boundary defines what belongs in the extracted code and what stays in the original code. It guides extraction planning and prevents scope creep.

The boundary should be stable. If the boundary is still evolving, extraction may be premature. Wait until the boundary stabilizes. A stable boundary enables safe extraction and prevents frequent changes.

**Extraction Scope Is Well-Defined and Time-Boxed**

The extraction scope must be well-defined and time-boxed. What exactly is being extracted? What stays in the original code? How long will extraction take? Clear scope prevents creep. Time-boxing prevents indefinite expansion.

If scope grows during extraction, stop and reassess. Create follow-up tasks for additional work. Don't let extraction expand indefinitely. Small, focused extractions are easier to review, test, and deploy.

**Feature Flag Infrastructure in Place (For Large Extractions)**

For large extractions (services, major modules), feature flag infrastructure must be in place. Feature flags enable gradual migration and instant rollback. They control routing between old and new implementations.

Feature flags should be configurable without code changes. They should enable rapid response to issues. Start with a small percentage of traffic routed to the new implementation, monitor metrics, and gradually increase.

**Monitoring in Place to Detect Regressions**

Monitoring must be in place to detect regressions after extraction. Compare metrics between old and new implementations. Monitor error rates, response times, and business metrics. If metrics degrade, investigate and rollback if necessary.

Monitoring should be comprehensive. It should cover all aspects of the extracted code's behavior. Set up alerts for significant metric changes. This enables rapid detection and response to issues.

## Synergies with Other Facets

Refactoring and extraction synergize with other engineering facets. Understanding these synergies enables more effective refactoring and extraction.

**Backend Architecture: Monolith to Microservices**

Refactoring and extraction are essential for migrating from monoliths to microservices. The Strangler Fig Pattern enables incremental migration. Module extraction prepares code for service extraction. Clear boundaries enable service extraction.

Backend architecture guides extraction boundaries. Domain boundaries, technical boundaries, and team boundaries inform what to extract. Architecture decisions guide refactoring priorities: refactor code that blocks architectural evolution.

**Frontend Architecture: SPA to Micro-Frontends**

Refactoring and extraction enable migrating from single-page applications to micro-frontends. Component extraction prepares code for micro-frontend extraction. Clear component boundaries enable independent deployment.

Frontend architecture guides extraction boundaries. Feature boundaries, team boundaries, and deployment boundaries inform what to extract. Architecture decisions guide refactoring priorities: refactor code that blocks micro-frontend extraction.

**Testing: Safety Net for Refactoring**

Testing provides a safety net for refactoring. Adequate test coverage enables confident refactoring. Tests verify that behavior remains unchanged after refactoring. Without tests, refactoring is risky.

Testing strategies guide refactoring approaches. Unit tests enable code-level refactoring. Integration tests enable module-level refactoring. End-to-end tests enable architecture-level refactoring. Choose refactoring approaches that are supported by existing tests.

**CI/CD: Enabling Safe Refactoring**

CI/CD enables safe refactoring by providing rapid feedback. Automated tests catch issues before they reach production. Automated deployment enables rapid rollback if issues arise. This reduces refactoring risk.

CI/CD practices guide refactoring practices. Frequent commits enable incremental refactoring. Automated testing enables confident refactoring. Feature flags enable gradual migration. Align refactoring practices with CI/CD capabilities.

**Observability: Monitoring Refactoring Impact**

Observability enables monitoring refactoring impact. Metrics detect regressions after refactoring. Logs help debug issues introduced by refactoring. Tracing helps understand behavior changes. This enables safe refactoring.

Observability practices guide refactoring validation. Monitor metrics after refactoring. Compare metrics before and after. Set up alerts for significant changes. This enables rapid detection and response to issues.

## Decision Matrix Summary

| Scenario | Approach | Risk Level | Time Investment |
|----------|----------|------------|-----------------|
| Code blocks feature | Refactor now | Low | Hours to days |
| Code smells accumulating | Schedule refactoring | Medium | Days to weeks |
| Stable, rarely-changed code | Don't refactor | N/A | N/A |
| Pattern seen 3+ times | Extract | Medium | Days to weeks |
| Pattern seen 1-2 times | Wait, duplicate | Low | N/A |
| Architectural extraction | Strangler Fig Pattern | High | Weeks to months |
| No test coverage | Write tests first | High | Days to weeks |

This decision matrix provides guidance for common scenarios. However, judgment is always required. Consider context, team capabilities, and business priorities when making refactoring and extraction decisions.
