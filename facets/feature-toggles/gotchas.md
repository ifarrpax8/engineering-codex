# Feature Toggles: Gotchas

## Contents

- [Toggle Debt](#toggle-debt)
- [Toggle Naming Chaos](#toggle-naming-chaos)
- [Testing Only the Toggle-On Path](#testing-only-the-toggle-on-path)
- [Inconsistent Toggle Evaluation](#inconsistent-toggle-evaluation)
- [Toggle State Leaking Between Tests](#toggle-state-leaking-between-tests)
- [Random Percentage Rollout](#random-percentage-rollout)
- [Too Many Toggles Active at Once](#too-many-toggles-active-at-once)
- [Using Toggles for Permanent Configuration](#using-toggles-for-permanent-configuration)
- [Toggle Checks Deep in Business Logic](#toggle-checks-deep-in-business-logic)
- [No Audit Trail for Toggle Changes](#no-audit-trail-for-toggle-changes)
- [Toggle Evaluation Performance Issues](#toggle-evaluation-performance-issues)
- [Toggle Removal Breaking Features](#toggle-removal-breaking-features)
- [Summary](#summary)

This document covers common pitfalls, traps, and mistakes when implementing and using feature toggles. Understanding these gotchas helps teams avoid costly mistakes and maintain healthy toggle systems.

## Toggle Debt

Toggle debt accumulates when toggles are created but never removed. Over time, the codebase becomes riddled with if/else branches for features that were fully released months or years ago. This makes the code harder to understand, test, and maintain.

**Symptoms**:
- Toggles that have been enabled for all users for months
- Code with toggle checks for features that are always enabled
- Developers unsure whether toggles are still needed
- Toggle definitions in database/config that nobody remembers creating

**Impact**:
- Increased code complexity
- Slower development velocity (developers must understand toggle logic)
- Higher bug risk (unused code paths may have bugs)
- Confusion about which code path is actually used

**Prevention**:
- Set expiration dates when creating toggles
- Track toggle age and alert on old toggles
- Include toggle removal as part of feature work (not separate tickets)
- Regular toggle audits to identify obsolete toggles
- Automated cleanup for clearly obsolete toggles

**Remediation**:
- Audit all toggles and identify which are still needed
- Remove toggles that have been enabled for all users for > 30 days
- Remove toggle checks from code for removed toggles
- Update documentation to reflect current toggle state

## Toggle Naming Chaos

Toggles with unclear names like "new_feature", "test_flag", or "johns_experiment" make it impossible to know what they control, who owns them, or whether they're still needed. This leads to confusion and fear of touching toggles.

**Symptoms**:
- Toggles with vague names (e.g., "feature1", "toggle_test")
- Toggles named after people (e.g., "johns_experiment")
- Toggles with temporary markers (e.g., "old_feature", "temp_flag")
- Multiple toggles with similar names (e.g., "new_feature", "new_feature_v2")

**Impact**:
- Developers avoid touching toggles (fear of breaking things)
- Difficult to understand what code does
- Hard to identify which toggles can be removed
- Confusion about toggle purpose and ownership

**Prevention**:
- Enforce naming conventions (category-feature-description)
- Code review to reject poorly named toggles
- Documentation requirements for toggle creation
- Regular audits to identify poorly named toggles

**Remediation**:
- Rename toggles to follow conventions (with migration plan)
- Update all code references to new names
- Update documentation with new names
- Communicate changes to team

## Testing Only the Toggle-On Path

Teams often test features with toggles enabled but forget to test the toggle-off path. When the toggle is disabled in production (due to issues or gradual rollout), users see broken experiences because the toggle-off path was never tested.

**Symptoms**:
- Tests only run with toggle enabled
- Toggle-off path has bugs or missing error handling
- Users see errors or broken UI when toggle is disabled
- Toggle-off path has performance issues

**Impact**:
- Production bugs when toggles are disabled
- Poor user experience during gradual rollouts
- Incidents when toggles are turned off for mitigation
- Loss of confidence in toggle system

**Prevention**:
- Require tests for both toggle states
- Code review to verify toggle-off path is tested
- CI runs tests with toggles in both states
- Test coverage metrics include toggle-off paths

**Remediation**:
- Add tests for toggle-off paths
- Fix bugs in toggle-off paths
- Verify toggle-off behavior in staging before production
- Document expected toggle-off behavior

## Inconsistent Toggle Evaluation

Toggle evaluation differs between backend and frontend, or between different services. Backend says feature is on, frontend says off. Users see inconsistent state, broken functionality, or confusing experiences.

**Symptoms**:
- Backend returns data for v2 feature, frontend shows v1 UI
- Different services evaluate same toggle differently
- Users see mixed old/new UI elements
- API responses don't match UI state

**Impact**:
- Broken user experiences
- Confusion about feature availability
- Data inconsistencies
- Support tickets and user complaints

**Prevention**:
- Evaluate toggles in one place (preferably backend)
- Include toggle state in API responses
- Use same toggle service/configuration everywhere
- Test toggle consistency across services

**Remediation**:
- Standardize on single source of truth for toggle state
- Update frontend to use toggle state from backend
- Verify consistency in staging
- Monitor for toggle inconsistencies in production

## Toggle State Leaking Between Tests

Test A enables a toggle, test B runs next and sees the toggle enabled (leftover state). Tests are not isolated, leading to flaky tests and false positives/negatives.

**Symptoms**:
- Tests pass individually but fail when run together
- Test results depend on execution order
- Toggle state from one test affects another
- Flaky CI builds

**Impact**:
- Unreliable test results
- False positives hiding real bugs
- False negatives causing unnecessary debugging
- Reduced confidence in test suite

**Prevention**:
- Reset toggle state before/after each test
- Use test fixtures that clean up toggle state
- Isolate tests (separate toggle instances per test)
- Use transactions to roll back toggle changes

**Remediation**:
- Add setup/teardown to reset toggle state
- Use test fixtures for toggle management
- Verify test isolation
- Fix flaky tests

## Random Percentage Rollout

User gets toggle on for one request, off for the next. Random evaluation per request creates confusing, inconsistent experiences. Users see features appear and disappear.

**Symptoms**:
- Same user sees different toggle state on different requests
- Features appear/disappear during user session
- Inconsistent behavior confuses users
- Experiment results are invalid (users in both groups)

**Impact**:
- Poor user experience
- Invalid experiment results
- User confusion and support tickets
- Loss of trust in feature system

**Prevention**:
- Use user ID as hash seed for percentage rollouts
- Ensure consistent evaluation per user
- Test that same user always sees same state
- Document percentage rollout implementation

**Remediation**:
- Fix percentage rollout to use user ID hashing
- Verify consistent evaluation
- Test with multiple requests from same user
- Update documentation

## Too Many Toggles Active at Once

50 active toggles with potential interactions create exponential complexity. Testing all combinations becomes impossible. Teams can't reason about system behavior.

**Symptoms**:
- Large number of active toggles (20+)
- Unknown interactions between toggles
- Difficult to test all combinations
- Developers confused about which toggles affect what

**Impact**:
- Impossible to test all states
- Unknown bugs from toggle interactions
- Slower development (must understand many toggles)
- Higher risk of production issues

**Prevention**:
- Limit number of active toggles (aim for < 10)
- Remove toggles promptly after feature release
- Track active toggle count and alert when high
- Regular toggle audits to identify removable toggles

**Remediation**:
- Audit all toggles and remove obsolete ones
- Prioritize toggle removal
- Reduce active toggle count to manageable level
- Document toggle interactions

## Using Toggles for Permanent Configuration

A toggle that controls which payment provider to use, never intended to be removed. This is configuration, not a toggle. Toggles are temporary; configuration is permanent.

**Symptoms**:
- Toggles that have existed for years
- Toggles that control permanent business rules
- Toggles that are never intended to be removed
- Configuration-like toggles (e.g., "payment-provider-stripe")

**Impact**:
- Toggle system used for wrong purpose
- Confusion about what toggles vs configuration
- Toggle debt from "permanent" toggles
- Harder to manage actual feature toggles

**Prevention**:
- Clearly define what toggles are for (temporary feature control)
- Use configuration management for permanent settings
- Code review to reject configuration-like toggles
- Regular audits to identify configuration masquerading as toggles

**Remediation**:
- Identify configuration-like toggles
- Migrate to configuration management system
- Remove toggle checks, use configuration directly
- Update documentation

## Toggle Checks Deep in Business Logic

Toggle checks scattered throughout domain services, repositories, utility functions. When toggle is removed, cleanup touches dozens of files. Hard to understand and maintain.

**Symptoms**:
- Toggle checks in domain services
- Toggle checks in repositories
- Toggle checks in utility functions
- Toggle checks throughout codebase

**Impact**:
- Difficult toggle removal (many files to change)
- Hard to understand toggle impact
- Business logic coupled to toggle system
- Slower development velocity

**Prevention**:
- Keep toggle checks at boundaries (controllers, route guards, components)
- Single toggle check point per feature
- Code review to reject deep toggle checks
- Architecture guidelines for toggle placement

**Remediation**:
- Refactor to move toggle checks to boundaries
- Consolidate toggle checks
- Update architecture guidelines
- Document toggle check placement rules

## No Audit Trail for Toggle Changes

Someone changed a toggle in production, feature broke, nobody knows who changed it or why. No accountability, difficult debugging, compliance issues.

**Symptoms**:
- No logging of toggle changes
- Unknown who changed toggles
- No reason documented for changes
- Can't track toggle change history

**Impact**:
- Difficult to debug toggle-related issues
- No accountability for changes
- Compliance issues (regulated environments)
- Loss of trust in toggle system

**Prevention**:
- Log all toggle changes (who, what, when, why)
- Require reason/comment for toggle changes
- Store toggle change history
- Regular audits of toggle changes

**Remediation**:
- Add audit logging to toggle system
- Store toggle change history
- Require comments/reasons for changes
- Review toggle change history regularly

## Toggle Evaluation Performance Issues

Toggle evaluation adds significant latency to requests. Database queries on every request, no caching, slow evaluation logic. System performance degrades.

**Symptoms**:
- High latency from toggle evaluation
- Database queries on every request
- No caching of toggle states
- Slow toggle evaluation logic

**Impact**:
- Poor request performance
- Database load from toggle queries
- User experience degradation
- System scalability issues

**Prevention**:
- Cache toggle states with appropriate TTLs
- Use efficient evaluation logic
- Load test toggle evaluation
- Monitor toggle evaluation latency

**Remediation**:
- Add caching to toggle evaluation
- Optimize evaluation logic
- Reduce database queries
- Monitor and alert on toggle latency

## Toggle Removal Breaking Features

Toggle is removed, but feature breaks because toggle-off path had bugs or missing functionality. Removal process didn't catch issues.

**Symptoms**:
- Feature breaks after toggle removal
- Toggle-off path had bugs
- Missing functionality in toggle-off path
- Removal process didn't test properly

**Impact**:
- Production incidents
- Need to re-add toggle
- Loss of confidence in toggle system
- Delayed feature releases

**Prevention**:
- Test toggle removal process
- Verify feature works without toggle
- Gradual toggle removal (disable first, then remove)
- Monitor after toggle removal

**Remediation**:
- Re-add toggle if needed
- Fix bugs in feature
- Improve toggle removal process
- Add tests for toggle removal

## Summary

These gotchas represent common mistakes that teams make with feature toggles. Awareness of these pitfalls helps teams avoid them:

1. **Toggle debt**—remove toggles promptly
2. **Naming chaos**—use consistent naming conventions
3. **Testing only toggle-on**—test both states
4. **Inconsistent evaluation**—single source of truth
5. **State leaking**—isolate tests
6. **Random rollouts**—use user ID hashing
7. **Too many toggles**—limit active count
8. **Configuration masquerading**—use configuration for permanent settings
9. **Deep toggle checks**—keep at boundaries
10. **No audit trail**—log all changes
11. **Performance issues**—cache and optimize
12. **Removal breaking features**—test removal process

Preventing these gotchas requires discipline, tooling, and process. Teams should establish practices to avoid these pitfalls from the start, and regularly audit their toggle systems to catch issues early.
