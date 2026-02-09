# Gotchas: Common Refactoring & Extraction Pitfalls

## Contents

- [Premature Extraction](#premature-extraction)
- [Wrong Abstraction](#wrong-abstraction)
- [Big Bang Rewrite](#big-bang-rewrite)
- [Refactoring Without Tests](#refactoring-without-tests)
- [Refactoring and Adding Features Simultaneously](#refactoring-and-adding-features-simultaneously)
- [Extracting Shared Libraries Between Services](#extracting-shared-libraries-between-services)
- [Over-Engineering Extract](#over-engineering-extract)
- [Not Updating the Mental Model](#not-updating-the-mental-model)
- [Scope Creep During Refactoring](#scope-creep-during-refactoring)
- [Ignoring the Build](#ignoring-the-build)
- [Refactoring During Critical Periods](#refactoring-during-critical-periods)
- [Assuming Refactoring Is Always Safe](#assuming-refactoring-is-always-safe)

## Premature Extraction

Extracting a shared function, component, or service after seeing the pattern only once is premature extraction. The abstraction doesn't fit the second use case. Now you have a leaky abstraction that's worse than duplication.

**Real-world scenario:** A developer sees two similar API validation functions—one validates user registration, another validates password reset. They extract a generic `validateRequest()` function with flags for different validation types. When a third use case (email verification) appears, it doesn't fit the abstraction. The function now has three boolean flags (`isRegistration`, `isPasswordReset`, `isEmailVerification`) and complex conditional logic. Each new use case requires modifying the shared function, affecting all callers. The abstraction is harder to understand than the original three separate functions.

Premature extraction creates abstractions based on speculation, not evidence. The first occurrence might be coincidence. The second might still be coincidence. Extracting after the first occurrence assumes a pattern that may not exist.

The cost of premature extraction is high. The abstraction requires special cases, flags, and workarounds for each use case. It becomes harder to understand than the original duplicated code. Developers spend time working around the abstraction rather than using it naturally.

**When premature extraction bites:** A team extracts a shared authentication utility after seeing it used in two places. Six months later, they need to add OAuth support. The shared utility doesn't fit OAuth's flow, but refactoring it would break 15 services. They end up creating a parallel OAuth utility, duplicating code anyway, but now with the added complexity of maintaining two utilities.

Wait for the pattern to emerge. The Rule of Three: tolerate duplication twice. On the third occurrence, extract. This ensures the abstraction is based on real patterns, not speculation. The abstraction will fit naturally because it's derived from actual needs.

## Wrong Abstraction

An abstraction that sort of fits but requires special cases, flags, and workarounds for each use case is a wrong abstraction. "The wrong abstraction is far more costly than duplication." If you find yourself adding if/else branches to handle different use cases in a shared abstraction, consider inlining it back.

**Real-world scenario:** A team creates a `DataProcessor` class to handle CSV, JSON, and XML parsing. Each format requires different parsing logic, so the class has a `format` parameter and multiple `if (format == CSV)` branches. When they need to add Excel parsing, it doesn't fit—Excel requires different dependencies and error handling. They add more conditionals. The class now has 200 lines with nested conditionals handling four formats. New developers struggle to understand which code path applies to their use case. The abstraction doesn't simplify—it complicates.

Wrong abstractions accumulate over time. Each use case adds another special case. The abstraction becomes a complex conditional that's harder to understand than the original duplicated code. Eventually, the abstraction must be removed or rewritten, costing more than if duplication had been tolerated.

**Signs of wrong abstraction:**
- Multiple boolean flags to control behavior (`isAsync`, `isRetryable`, `isBatch`)
- Type checks to determine which code path to take (`if (data instanceof CSVData)`)
- Comments explaining why the abstraction doesn't quite fit ("Note: This doesn't work for Excel files, see workaround below")
- Methods with many parameters, most optional, controlling behavior
- Callers passing `null` or empty objects to skip parts of the abstraction

**When wrong abstraction causes pain:** A shared `NotificationService` handles email, SMS, and push notifications. Each channel has different requirements: email needs templates, SMS has character limits, push needs device tokens. The service has grown to 500 lines with complex conditionals. Adding Slack notifications requires modifying the shared service, risking breaking existing channels. The team is afraid to touch it, so they create a separate Slack service, duplicating infrastructure but avoiding the shared abstraction's complexity.

If you find yourself fighting the abstraction, consider inlining it. Duplication may be clearer than a wrong abstraction. After inlining, wait for the pattern to emerge naturally. Then extract based on evidence, not speculation. The right abstraction will feel natural—you won't need to work around it.

## Big Bang Rewrite

"Let's rewrite the whole thing from scratch" is a common trap. Big rewrites are high risk, take longer than estimated, and often fail because the team must maintain the old system while building the new one.

Big rewrites attempt to change everything at once while business requirements continue to evolve. The old system must be maintained, which diverts resources from the new system. Requirements change during the rewrite, making the new system outdated before it's complete.

Big rewrites often fail because they try to change too much at once. They require perfect understanding of the old system, which is rarely possible. They assume requirements won't change, which is never true. They create a long period where no new features are delivered, which business stakeholders find unacceptable.

Use the Strangler Fig Pattern for incremental migration instead. New functionality goes to the new system. Old functionality gradually migrates. Both systems run in parallel. This reduces risk and enables continuous delivery of value.

## Refactoring Without Tests

Changing code without a safety net is dangerous. You won't know if you've broken something until it reaches production. Tests provide a safety net: they verify that behavior remains unchanged after refactoring.

**Real-world scenario:** A developer refactors a payment processing function without tests. The function has complex business logic handling discounts, taxes, and fees. During refactoring, they accidentally invert a condition: `if (amount > 100)` becomes `if (amount <= 100)`. The code compiles, but now orders over $100 don't get discounts. The bug reaches production, affects 200 orders before detection, and requires manual refunds. Tests would have caught this immediately.

Refactoring without tests is like walking a tightrope without a net. One misstep, and you fall. Tests catch mistakes before they reach production. They enable confident refactoring: if tests pass, behavior is preserved.

**When refactoring without tests fails:** A team refactors a legacy authentication module without tests. The module handles session management, token validation, and password hashing. During refactoring, they change the password hashing algorithm from bcrypt to a faster hash function, thinking it's an optimization. The change breaks password verification—existing users can't log in. Without tests, they don't discover this until users report login failures. The rollback requires database migrations to restore password hashes.

If code doesn't have tests, write characterization tests first. Capture current behavior, even if that behavior is imperfect. Then refactor with confidence: if tests pass, behavior is preserved. Characterization tests document "what the code does" not "what it should do"—they capture reality, enabling safe refactoring.

Tests also document behavior. They serve as executable documentation that describes what the code does. This is particularly valuable for code that's being refactored: tests help ensure that refactoring preserves behavior. When refactoring legacy code, tests reveal edge cases and implicit behavior that isn't obvious from reading the code.

## Refactoring and Adding Features Simultaneously

Mixing refactoring and feature work makes it impossible to tell if a bug came from the refactoring or the new feature. Separate the two. Refactor first (and merge), then add the feature.

Refactoring changes structure, not behavior. Feature work changes behavior. Mixing the two makes it unclear which changes caused which effects. This slows debugging and increases risk.

Separate refactoring and feature work into distinct commits or pull requests. This makes it clear what changed and why. It also makes reverts safer: if the feature has issues, you can revert the feature commit without reverting refactoring improvements.

Ideally, refactor first in a separate pull request. This enables independent review and validation. After refactoring is merged, the feature pull request is simpler and easier to review. This reduces risk and improves code quality.

## Extracting Shared Libraries Between Services

Creating a shared library that couples multiple services is risky. A change to the library requires coordinating deployments across all consumers. Consider whether the duplication is actually preferable to the coupling.

Shared libraries create coupling between services. If Service A and Service B share a library, changing the library requires coordinating deployments. This slows development and increases risk. A bug in the shared library affects all consumers.

Sometimes duplication between services is the correct choice. Services can evolve independently if they don't share code. The cost of duplication may be less than the cost of coupling. Consider the stability of the shared code: if it's stable, sharing may be acceptable; if it's evolving, duplication may be preferable.

If you must share code between services, make the shared code stable. Define clear versioning and compatibility policies. Consider using semantic versioning and maintaining multiple versions for gradual migration. However, prefer duplication when possible.

## Over-Engineering Extract

Extracting a utility function used in one place into a separate utility class in a shared package is over-engineering. One usage doesn't justify extraction. Wait until there are multiple consumers.

Over-engineering creates unnecessary complexity. A utility function used in one place doesn't need to be extracted. Extraction adds indirection without providing value. It makes the code harder to understand and maintain.

Wait for multiple consumers before extracting. The Rule of Three applies here too: tolerate single usage. On the second or third usage, consider extraction. But even then, consider whether extraction provides value. Sometimes duplication is clearer than premature extraction.

Over-engineering also applies to extracting components or modules. Don't extract a component used in one place. Don't create a module for code that's only used by one service. Wait until there are multiple consumers or clear boundaries.

## Not Updating the Mental Model

Refactoring the code but not updating documentation, diagrams, or team knowledge creates confusion. New team members read outdated documentation and create code that doesn't fit the refactored architecture.

Code and documentation must stay in sync. When code is refactored, update documentation. Update architecture diagrams. Update team knowledge through code reviews and discussions. Outdated documentation misleads developers and creates confusion.

Mental models are important for understanding code. When code structure changes, mental models must change too. If documentation and team knowledge don't reflect the new structure, developers will create code that doesn't fit.

After refactoring, update all relevant documentation. Update README files, architecture diagrams, and API documentation. Communicate changes to the team. Ensure everyone understands the new structure.

## Scope Creep During Refactoring

Starting to refactor one method, then touching the class, then the package, then the module is scope creep. Set a clear scope before starting. Time-box refactoring efforts. If the scope grows, create follow-up tasks.

Scope creep makes refactoring risky. What started as a small, safe refactoring becomes a large, risky change. It's hard to review, hard to test, and hard to revert. Set clear boundaries and stick to them.

Time-box refactoring efforts. If a refactoring is taking longer than expected, stop and reassess. Create follow-up tasks for additional improvements. Don't let refactoring expand indefinitely.

If scope grows, create follow-up tasks. Document what needs to be done later. This enables incremental improvement without risking large changes. It also makes refactoring more manageable: small, focused changes are easier to review and test.

## Ignoring the Build

Refactoring locally without running the full build is dangerous. The refactoring works locally but breaks a downstream module, a test in another package, or a CI check. Run the full build before pushing.

Local environments may differ from CI environments. Dependencies may be different. Tests may be configured differently. What works locally may not work in CI. Always run the full build before pushing refactoring changes.

The full build includes compilation, tests, linting, and other checks. It verifies that refactoring didn't break anything. If the build fails, fix issues before pushing. Don't push broken code and hope CI will catch it.

CI should also run the full build. If CI fails, investigate immediately. Don't ignore CI failures. They indicate real problems that need to be fixed. Fix CI failures before merging refactoring changes.

## Refactoring During Critical Periods

Refactoring during critical periods (launches, incidents, deadlines) is risky. Refactoring has risk, and critical periods require stability. Avoid refactoring when stability is paramount.

During critical periods, focus on stability. Don't introduce unnecessary changes. Refactoring can wait until after the critical period. Focus on delivering value and maintaining stability.

However, if refactoring is necessary to fix a critical issue, proceed carefully. Write tests first. Refactor in small steps. Review thoroughly. But prefer to defer refactoring until after the critical period.

Plan refactoring for low-risk periods. Schedule refactoring sprints when there are no critical deadlines or launches. This enables safe refactoring without risking critical periods.

## Assuming Refactoring Is Always Safe

Refactoring has risk. Every change can introduce bugs. Tests help reduce risk, but they don't eliminate it. Assume refactoring has risk and plan accordingly.

Even with tests, refactoring can introduce bugs. Tests may not cover all cases. Tests may have bugs themselves. Edge cases may not be tested. Refactoring requires careful testing and validation.

Plan for risk. Refactor in small steps. Commit frequently. Review thoroughly. Test extensively. Monitor production metrics after deploying refactored code. Be prepared to rollback if issues arise.

Don't assume refactoring is always safe. Treat it as a change that requires testing and validation. Plan for risk and mitigate it appropriately. This enables safe refactoring without unnecessary risk.

## Stack-Specific Gotchas

### Spring Boot: Breaking Dependency Injection During Extraction

**Real-world scenario:** A team extracts a `PaymentService` from a large controller. During extraction, they change constructor parameters, breaking Spring's dependency injection. The application fails to start with "No qualifying bean" errors. They spend 2 hours debugging before realizing they forgot to add `@Service` annotation or register the bean in configuration.

**Common mistakes:**
- Forgetting `@Service`, `@Component`, or `@Repository` annotations on extracted classes
- Changing constructor parameters without updating `@Autowired` dependencies
- Extracting classes into different packages without updating component scan paths
- Breaking circular dependencies by extracting without considering injection order

**Prevention:** Always verify that extracted classes are properly annotated and registered. Run the application locally after extraction to catch dependency injection issues before pushing.

### Spring Boot: Breaking Transaction Boundaries

**Real-world scenario:** A team extracts a `OrderService` method that updates the database. The original method was in a `@Transactional` controller method. After extraction, the service method isn't transactional, causing partial updates when exceptions occur. Orders are created but inventory isn't decremented, leading to data inconsistency.

**Common mistakes:**
- Extracting transactional code without preserving `@Transactional` annotation
- Changing transaction propagation (REQUIRED vs REQUIRES_NEW) without understanding implications
- Extracting code that depends on transaction context (entity state, lazy loading)

**Prevention:** Verify transaction boundaries after extraction. Test rollback scenarios to ensure transactional behavior is preserved. Use `@Transactional` on service methods, not controllers.

### Vue/React: Breaking Reactivity During Component Extraction

**Real-world scenario:** A Vue developer extracts a computed property into a composable. The composable returns a plain object instead of a reactive object. Components using the composable don't update when the underlying data changes. The developer spends hours debugging why the UI isn't updating.

**Common mistakes:**
- Extracting reactive code without preserving reactivity (`ref`, `reactive`, `computed`)
- Returning plain objects from composables instead of reactive objects
- Breaking reactivity chains by extracting intermediate values
- Extracting code that depends on component context (`this`, component lifecycle)

**Prevention:** Test that extracted composables/hooks maintain reactivity. Verify that components update when composable data changes. Use Vue DevTools or React DevTools to inspect reactivity.

### Vue/React: Breaking Props/Events During Component Extraction

**Real-world scenario:** A React developer extracts a form component. The original component received 15 props. After extraction, they forget to pass 3 props, causing the form to break silently. The bug is discovered in production when users report form submission failures.

**Common mistakes:**
- Extracting components without preserving all props/events
- Changing prop names during extraction without updating callers
- Extracting components that depend on parent component state
- Breaking prop drilling chains by extracting intermediate components

**Prevention:** Use TypeScript interfaces to ensure all props are passed. Test extracted components in isolation. Verify that all callers are updated after extraction.

### Vue/React: Breaking Context/Store Access During Extraction

**Real-world scenario:** A Vue component uses `useStore()` to access Pinia state. The developer extracts a composable that also needs store access. The composable is used in a component that doesn't have access to the store, causing runtime errors.

**Common mistakes:**
- Extracting code that depends on Vuex/Pinia store without ensuring store is available
- Extracting code that uses React Context without ensuring context provider is present
- Extracting code that depends on specific store modules/namespaces
- Breaking store access by extracting into utilities that can't access stores

**Prevention:** Verify that extracted code can access required stores/contexts. Test extracted code in components that don't have store access. Consider passing store/context as parameters instead of accessing globally.

### Spring Boot: Breaking Spring Security During Extraction

**Real-world scenario:** A team extracts authentication logic from a controller to a service. The original controller method had `@PreAuthorize` annotations. After extraction, the service methods aren't secured, allowing unauthorized access. Security vulnerabilities are introduced.

**Common mistakes:**
- Extracting secured code without preserving security annotations
- Moving security checks from controllers to services without proper method security
- Breaking Spring Security's method-level security by extracting to non-Spring-managed classes
- Extracting code that depends on `SecurityContext` without ensuring context is available

**Prevention:** Verify security annotations after extraction. Test authorization scenarios to ensure security is preserved. Use method-level security (`@PreAuthorize`, `@Secured`) on service methods.

### Vue/React: Breaking Error Boundaries During Extraction

**Real-world scenario:** A React developer extracts error handling logic from a component. The original component was wrapped in an ErrorBoundary. After extraction, errors in the extracted code aren't caught by the ErrorBoundary, causing the entire application to crash.

**Common mistakes:**
- Extracting error handling without preserving error boundary coverage
- Extracting code that throws errors outside error boundary scope
- Breaking error propagation by extracting error handlers
- Extracting code that depends on error boundary context

**Prevention:** Test error scenarios after extraction. Verify that errors are caught by error boundaries. Consider error handling strategy when extracting code.

## Refactoring Legacy Code Without Understanding Business Logic

**Real-world scenario:** A developer refactors a 10-year-old payment processing function. The function has complex conditional logic with comments like "don't change this, it handles edge case X." The developer "cleans up" the logic, removing what seems like redundant checks. Six months later, a customer reports that their payment isn't processing. Investigation reveals the removed check handled a specific payment provider's quirk. The fix requires restoring the original logic and understanding the business context.

**Common mistakes:**
- Refactoring code with business-critical comments without understanding them
- Removing "redundant" code that actually handles edge cases
- Simplifying complex business logic without consulting domain experts
- Changing behavior while refactoring (accidentally fixing bugs or introducing bugs)

**Prevention:** Before refactoring legacy code, understand the business context. Talk to domain experts. Write characterization tests that capture current behavior, including edge cases. Don't change behavior while refactoring—refactor first, then improve behavior separately.

## Extracting Code That Depends on Framework Magic

**Real-world scenario:** A Spring Boot developer extracts a method that uses `@Transactional` and entity lazy loading. The extracted method is moved to a utility class that isn't Spring-managed. Lazy loading fails because there's no active transaction or Hibernate session. The code breaks silently, causing `LazyInitializationException` errors.

**Common mistakes:**
- Extracting code that depends on framework features (dependency injection, AOP, transactions)
- Moving framework-dependent code to non-framework classes
- Breaking framework context by extracting code outside framework-managed boundaries
- Extracting code that depends on framework lifecycle (component initialization, bean creation)

**Prevention:** Understand framework dependencies before extraction. Verify that extracted code can access required framework features. Test framework-specific behavior after extraction. Consider keeping framework-dependent code in framework-managed classes.
