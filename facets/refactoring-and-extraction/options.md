# Options: Refactoring & Extraction Decision Framework

## Contents

- [Recommended Refactoring Approach](#recommended-refactoring-approach)
- [Refactoring Trigger Decision Guide](#refactoring-trigger-decision-guide)
  - [When to Refactor NOW (Blocking Current Work)](#when-to-refactor-now-blocking-current-work)
  - [When to Refactor SOON (Schedule It)](#when-to-refactor-soon-schedule-it)
  - [When NOT to Refactor](#when-not-to-refactor)
- [Extraction Readiness Checklist](#extraction-readiness-checklist)
- [Synergies with Other Facets](#synergies-with-other-facets)
- [Decision Matrix Summary](#decision-matrix-summary)

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

**YAGNI (You Aren't Gonna Need It) applies to refactoring too.** Don't refactor code to make it "more extensible" for hypothetical future requirements. If the future requirement never materializes, you've wasted effort and introduced risk. Refactor when you have concrete, current needs, not speculative future needs.

**Premature abstraction is worse than duplication.** If you see similar code twice, resist the urge to extract immediately. The similarity might be coincidental. Wait until you see the pattern three times before extracting. Premature extraction creates abstractions that don't fit, requiring special cases and workarounds that make the code harder to understand than the original duplication.

Don't refactor when you want to "clean it up" but have no concrete benefit. Refactoring should have a purpose: enabling a feature, fixing a bug, or improving maintainability. Refactoring for its own sake introduces risk without providing value. Ask: "What problem does this refactoring solve?" If you can't answer clearly, don't refactor.

Don't refactor when you're about to deprecate or replace the system. If a system is scheduled for replacement within 6-12 months, refactoring it is wasteful. Focus effort on the replacement system instead. However, if replacement is years away, refactoring may still be worthwhile to reduce maintenance burden.

Don't refactor when you don't have adequate test coverage. Refactoring without tests is risky. Write characterization tests first, then refactor. Tests provide a safety net that enables confident refactoring. However, don't let perfect test coverage block necessary refactoring—write tests for the critical paths first, then refactor incrementally.

**Don't refactor during critical periods.** If you're in the middle of a launch, incident response, or tight deadline, refactoring introduces unnecessary risk. Wait until the critical period passes. Stability is more important than code quality during these times.

**Don't refactor code you don't understand.** If you're not confident you understand what the code does and why it works, refactoring is dangerous. First, write characterization tests to document current behavior. Then, refactor incrementally with tests as your safety net. Understanding comes before refactoring.

## Extraction Readiness Checklist

Before extracting code, verify readiness using this checklist. Extraction is more complex than refactoring and requires careful planning.

**Pattern Seen at Least 3 Times**

The pattern must be seen at least three times before extraction. The Rule of Three ensures the abstraction is based on real patterns, not speculation. The first occurrence might be coincidence. The second might still be coincidence. The third confirms a pattern.

Extracting after the first or second occurrence creates wrong abstractions. Wait until the pattern is clear. The abstraction will fit naturally because it's derived from actual needs, not anticipated needs.

**Exception: Extract when duplication blocks a feature.** If you need to add a feature that requires modifying duplicated code in multiple places, and modifying all copies is error-prone, extraction may be justified even after two occurrences. However, extract conservatively—create a minimal abstraction that fits both current uses, not a general-purpose abstraction for hypothetical future uses.

**Decision criteria for extraction:**
- **Extract Method**: When a code block has a clear, single purpose and a descriptive name suggests itself. The extracted method should be reusable or at least improve readability. If you can't think of a good name, the code isn't ready for extraction.
- **Extract Class**: When a class has multiple responsibilities (violates Single Responsibility Principle) and you can identify a cohesive group of fields and methods that belong together. The extracted class should have a clear purpose and minimal coupling to the original class.
- **Extract Service**: When a module has clear boundaries (domain boundaries, team boundaries, or technical boundaries) and can operate independently. The service should have a stable API and minimal synchronous dependencies on other services.

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

| Scenario | Approach | Risk Level | Time Investment | Trade-offs |
|----------|----------|------------|-----------------|------------|
| Code blocks feature | Refactor now | Low | Hours to days | Immediate payoff, validates refactoring value |
| Code smells accumulating | Schedule refactoring | Medium | Days to weeks | Prevents debt accumulation, requires planning |
| Stable, rarely-changed code | Don't refactor | N/A | N/A | Risk without benefit—focus effort elsewhere |
| Pattern seen 3+ times | Extract | Medium | Days to weeks | Reduces duplication, creates abstraction to maintain |
| Pattern seen 1-2 times | Wait, duplicate | Low | N/A | Avoids wrong abstraction, tolerates duplication |
| Architectural extraction | Strangler Fig Pattern | High | Weeks to months | Enables migration, requires parallel systems |
| No test coverage | Write tests first | High | Days to weeks | Enables safe refactoring, delays feature work |
| Premature abstraction risk | Wait for pattern | Low | N/A | Wrong abstraction more costly than duplication |
| Critical period (launch/incident) | Defer refactoring | High | N/A | Stability over code quality during crises |

**Nuanced Trade-offs:**

**Refactoring vs. Feature Velocity:** Refactoring improves long-term velocity but slows short-term feature delivery. The trade-off depends on debt level: high debt requires refactoring to maintain velocity; low debt allows deferring refactoring for feature delivery.

**When to prioritize refactoring over features:**
- Developer velocity has measurably declined (features taking 2x longer than 6 months ago)
- Bug rates are increasing, especially bugs introduced by recent changes
- Code review time is increasing (reviewers spending more time understanding code than evaluating logic)
- New team members take >3 months to become productive in an area
- Technical debt interest payments (time fixing bugs, working around limitations) exceed 30% of development capacity

**When to prioritize features over refactoring:**
- Code quality is acceptable and velocity is stable
- Technical debt is localized and not blocking current work
- Team is small and refactoring would delay critical business features
- System is scheduled for replacement within 6-12 months

**The YAGNI Principle in Refactoring:** "You Aren't Gonna Need It" applies to refactoring too. Don't refactor to make code "more extensible" for hypothetical future requirements. Real-world example: A team refactors a payment processor to support "any payment method" even though only credit cards are used. Six months later, they need PayPal support, but PayPal's flow doesn't fit the abstraction. They spend 2 weeks refactoring the abstraction, then realize they should have waited. The original code would have been easier to extend when the real requirement emerged.

**Extraction vs. Duplication:** Extraction reduces duplication but creates abstractions to maintain. Duplication is clearer but requires updating multiple places. The trade-off depends on abstraction stability: stable patterns benefit from extraction; evolving patterns benefit from duplication.

**When duplication is preferable:**
- Pattern is still evolving—requirements change frequently
- Use cases have subtle differences that would require special cases in shared code
- Services need to evolve independently (microservices architecture)
- Abstraction would require many parameters or flags to handle different cases
- Code is in different domains with different change cadences

**When extraction is preferable:**
- Pattern is stable—requirements haven't changed in 6+ months
- Use cases are genuinely identical, not just similar
- Changes need to be synchronized across all uses (security fixes, business rule updates)
- Abstraction simplifies code without adding complexity
- Code is in the same domain and changes together

**Real-world example:** A team has two similar API validation functions—one for user registration, one for password reset. They extract a shared `validateRequest()` function. Six months later, password reset needs different validation rules (allow expired passwords). The shared function now needs a flag `isPasswordReset` with special logic. The abstraction is harder to understand than the original two functions. They should have waited until seeing a third use case or until the pattern stabilized.

**Test Coverage vs. Refactoring Speed:** Writing tests first slows refactoring but enables safe refactoring. Skipping tests speeds refactoring but increases risk. The trade-off depends on code criticality: critical code requires tests; non-critical code may tolerate risk.

**When to write tests first:**
- Code handles money, security, or user data
- Code has no existing tests and is complex (>100 lines, multiple branches)
- Refactoring is large (extracting service, major architectural change)
- Code is frequently changed (high change frequency = high regression risk)
- Team has experienced bugs from refactoring this code before

**When to refactor without tests first:**
- Code is simple (single responsibility, <50 lines, no branches)
- Code is rarely changed (low change frequency = low regression risk)
- Refactoring is small (extract method, rename variable)
- Code is non-critical (internal utilities, logging helpers)
- Tests would take longer than the refactoring itself

**Characterization tests as a middle ground:** For legacy code without tests, write characterization tests that capture current behavior (even if imperfect). These tests document "what the code does" not "what it should do." They enable safe refactoring without requiring perfect test coverage. Example: A 500-line payment processing function has no tests. Write characterization tests for the 5 most common payment scenarios. Refactor incrementally, ensuring tests still pass. This provides safety without requiring comprehensive test coverage upfront.

**Boy Scout Rule vs. Scope Creep:** Small improvements prevent debt accumulation but can expand into large refactorings. The trade-off requires discipline: limit improvements to code you're already modifying; create separate tasks for larger improvements.

This decision matrix provides guidance for common scenarios. However, judgment is always required. Consider context, team capabilities, and business priorities when making refactoring and extraction decisions.
