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

Premature extraction creates abstractions based on speculation, not evidence. The first occurrence might be coincidence. The second might still be coincidence. Extracting after the first occurrence assumes a pattern that may not exist.

The cost of premature extraction is high. The abstraction requires special cases, flags, and workarounds for each use case. It becomes harder to understand than the original duplicated code. Developers spend time working around the abstraction rather than using it naturally.

Wait for the pattern to emerge. The Rule of Three: tolerate duplication twice. On the third occurrence, extract. This ensures the abstraction is based on real patterns, not speculation. The abstraction will fit naturally because it's derived from actual needs.

## Wrong Abstraction

An abstraction that sort of fits but requires special cases, flags, and workarounds for each use case is a wrong abstraction. "The wrong abstraction is far more costly than duplication." If you find yourself adding if/else branches to handle different use cases in a shared abstraction, consider inlining it back.

Wrong abstractions accumulate over time. Each use case adds another special case. The abstraction becomes a complex conditional that's harder to understand than the original duplicated code. Eventually, the abstraction must be removed or rewritten, costing more than if duplication had been tolerated.

Signs of wrong abstraction include: multiple boolean flags to control behavior, type checks to determine which code path to take, or comments explaining why the abstraction doesn't quite fit. These are red flags that the abstraction is wrong.

If you find yourself fighting the abstraction, consider inlining it. Duplication may be clearer than a wrong abstraction. After inlining, wait for the pattern to emerge naturally. Then extract based on evidence, not speculation.

## Big Bang Rewrite

"Let's rewrite the whole thing from scratch" is a common trap. Big rewrites are high risk, take longer than estimated, and often fail because the team must maintain the old system while building the new one.

Big rewrites attempt to change everything at once while business requirements continue to evolve. The old system must be maintained, which diverts resources from the new system. Requirements change during the rewrite, making the new system outdated before it's complete.

Big rewrites often fail because they try to change too much at once. They require perfect understanding of the old system, which is rarely possible. They assume requirements won't change, which is never true. They create a long period where no new features are delivered, which business stakeholders find unacceptable.

Use the Strangler Fig Pattern for incremental migration instead. New functionality goes to the new system. Old functionality gradually migrates. Both systems run in parallel. This reduces risk and enables continuous delivery of value.

## Refactoring Without Tests

Changing code without a safety net is dangerous. You won't know if you've broken something until it reaches production. Tests provide a safety net: they verify that behavior remains unchanged after refactoring.

Refactoring without tests is like walking a tightrope without a net. One misstep, and you fall. Tests catch mistakes before they reach production. They enable confident refactoring: if tests pass, behavior is preserved.

If code doesn't have tests, write characterization tests first. Capture current behavior, even if that behavior is imperfect. Then refactor with confidence: if tests pass, behavior is preserved.

Tests also document behavior. They serve as executable documentation that describes what the code does. This is particularly valuable for code that's being refactored: tests help ensure that refactoring preserves behavior.

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
