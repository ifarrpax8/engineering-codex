# Architecture: Refactoring & Extraction Patterns

## Types of Refactoring

Refactoring occurs at multiple levels of abstraction, each with different risks and techniques. Understanding these levels helps choose the right approach and manage risk appropriately.

### Code-Level Refactoring

Code-level refactoring operates within a single method or class. These refactorings are the safest and most common. Modern IDEs provide automated support for many code-level refactorings, reducing the risk of errors.

Rename refactoring changes the name of a variable, method, or class. IDEs update all references automatically. This refactoring is safe when the codebase is well-tested and the IDE can find all usages. However, dynamic language features or reflection may bypass IDE analysis, requiring manual verification.

Extract method selects a block of code and moves it to a new method with a descriptive name. The original code is replaced with a call to the new method. This refactoring improves readability by giving a name to a concept. It's safe when the extracted code has no side effects or when side effects are intentional and well-understood.

Extract class splits a large class into two classes. Fields and methods that belong together are moved to a new class. The original class delegates to the new class. This refactoring addresses the Large Class code smell. It's safe when the extracted class has clear responsibilities and minimal coupling to the original class.

Inline refactoring does the opposite of extract: it moves the body of a method into its callers and removes the method. This refactoring is useful when a method is no longer needed or when its abstraction adds no value. It's safe when the method has few callers.

Move refactoring relocates a method or field to a different class. This refactoring addresses Feature Envy: when a method uses more data from another class than its own, it probably belongs in that other class. It's safe when the method's new location is clear and dependencies are minimal.

Simplify conditionals replaces complex conditional logic with clearer alternatives. This includes replacing nested if statements with guard clauses, replacing conditionals with polymorphism, and extracting complex boolean expressions into well-named methods. This refactoring improves readability and reduces cognitive load.

### Module-Level Refactoring

Module-level refactoring reorganizes packages, extracts modules, defines boundaries, and introduces interfaces between modules. These refactorings require understanding of dependencies and have medium risk.

Reorganize packages groups related classes into logical packages. This refactoring improves discoverability and enforces logical boundaries. It's safe when package boundaries align with natural code organization and when dependencies flow in one direction.

Extract modules creates a new module from existing code. The module has a defined API, and internal classes are hidden (package-private or internal visibility). This refactoring enables independent evolution and testing. It's safe when module boundaries are clear and dependencies are well-understood.

Define boundaries establishes explicit interfaces between modules. This refactoring prevents modules from accessing each other's internals. It's safe when boundaries align with business domains or technical concerns. Architecture tests can enforce these boundaries and prevent regression.

Introduce interfaces between modules creates abstraction layers that enable dependency inversion. Modules depend on interfaces, not concrete implementations. This refactoring improves testability and enables swapping implementations. It's safe when interfaces capture stable contracts.

### Architecture-Level Refactoring

Architecture-level refactoring extracts services from monoliths, splits frontends into micro-frontends, and introduces event-driven communication. These refactorings are high risk and require careful planning, feature flags, and parallel running.

Extract service from monolith is the most complex extraction. The Strangler Fig Pattern enables incremental migration: new functionality goes to the new service, old functionality gradually migrates, and both run in parallel. Data migration is often the hardest part, requiring careful planning and validation.

Split frontend into micro-frontends breaks a monolithic single-page application into independently deployable frontend modules. Each micro-frontend owns a portion of the user interface and can be developed and deployed independently. This refactoring improves team autonomy and deployment frequency.

Introduce event-driven communication replaces synchronous request-response patterns with asynchronous events. This refactoring decouples services and improves scalability. However, it introduces complexity: eventual consistency, event ordering, and error handling become concerns.

## Code Smells

Code smells are indicators that refactoring may be needed. They are not bugs—the code works—but they suggest structural problems that will make future changes difficult.

### Long Methods

Methods over approximately 20 lines are hard to understand, test, and reuse. Long methods often do multiple things, violating the Single Responsibility Principle. Extract smaller methods with descriptive names. Each method should do one thing and do it well.

Long methods accumulate over time. A method starts small, then a feature requires adding a few lines. Over months, these additions accumulate. Regular refactoring prevents this accumulation. When a method grows beyond 20 lines, extract a portion into a well-named method.

### Large Classes

Classes with too many responsibilities violate the Single Responsibility Principle. Large classes are hard to understand, test, and modify. Extract classes by responsibility. Each class should have one reason to change.

Large classes often have many fields and methods. They may have multiple concerns mixed together. Identify cohesive groups of fields and methods, and extract them into separate classes. The original class delegates to the new classes.

### Duplicate Code

The same logic in multiple places creates maintenance burden. Changes require updating every copy, and it's easy to miss one. Extract shared behavior into a function or class. However, wait until the pattern is clear—premature extraction creates wrong abstractions.

Duplicate code often indicates missing abstractions. However, not all duplication is bad. Duplication between services may be preferable to shared libraries that couple services. The Rule of Three helps decide: tolerate duplication twice, extract on the third occurrence.

### Feature Envy

A method that uses more data from another class than its own probably belongs in that other class. Feature envy indicates misplaced behavior. Move the method to the class whose data it primarily uses.

Feature envy creates coupling. The method depends on another class's internal structure. Moving the method reduces coupling and improves cohesion. The method is now with the data it uses, making the code easier to understand.

### Primitive Obsession

Using primitives (String, Int) for domain concepts (EmailAddress, Money, UserId) loses type safety and domain meaning. Wrap primitives in value objects. Value objects encapsulate validation and behavior, making the code more expressive and less error-prone.

Primitive obsession is common in codebases that haven't adopted domain-driven design. Replacing primitives with value objects is a safe refactoring that improves type safety and expressiveness. Modern languages make this easy: Kotlin data classes, Java records, TypeScript branded types.

### Long Parameter Lists

Methods with four or more parameters are hard to understand and call. Group related parameters into an object. This refactoring improves readability and makes it easier to add parameters later without breaking callers.

Long parameter lists often indicate missing abstractions. The parameters might belong together in a value object or configuration class. Extract a parameter object to group related parameters.

### Shotgun Surgery

A single change requires modifications in many classes. This indicates poor cohesion: related code is scattered. Group related code together. Extract shared behavior into a single location that all classes can use.

Shotgun surgery is the opposite of large classes. Instead of one class doing too much, related behavior is scattered across many classes. Identify the common behavior and extract it into a shared location.

## Extraction Patterns

Extraction patterns provide systematic approaches to refactoring. Each pattern addresses specific code smells and has well-defined steps.

### Extract Method

Extract method is the safest refactoring. Select a block of code, extract it to a named method, and replace the original code with a call to the new method. Modern IDEs automate this refactoring, reducing risk.

The extracted method should have a descriptive name that explains what it does, not how it does it. The name should be at a higher level of abstraction than the implementation. If you can't think of a good name, the code might not be ready for extraction.

Extract method improves readability by giving a name to a concept. It enables reuse if the same logic appears elsewhere. It makes testing easier by isolating behavior into testable units.

### Extract Class

Extract class splits a large class into two classes. Identify a cohesive group of fields and methods, move them to a new class, and have the original class delegate to the new class. This refactoring addresses the Large Class code smell.

The extracted class should have a clear responsibility. It should be more cohesive than the original class. The original class should delegate to the new class, not duplicate its functionality.

Extract class improves maintainability by separating concerns. Each class has a single responsibility, making the code easier to understand and modify. It enables independent testing and evolution.

### Extract Interface

Extract interface defines an interface for existing behavior. The interface captures the contract that clients depend on. Concrete implementations can evolve independently as long as they satisfy the interface.

Extract interface enables dependency inversion. Clients depend on the interface, not concrete implementations. This improves testability by allowing mock implementations. It enables swapping implementations without changing clients.

Extract interface is safe when the interface captures a stable contract. If the contract is still evolving, extracting the interface may be premature. Wait until the contract stabilizes.

### Extract Module/Package

Extract module groups related classes into a module with a defined API. Internal classes are hidden (package-private or internal visibility). The module exposes only its public API, hiding implementation details.

Extract module improves encapsulation. Clients depend only on the public API, not internal details. This enables independent evolution: the module can change its internals without affecting clients.

Extract module requires defining clear boundaries. The module should have a cohesive purpose and minimal dependencies on other modules. Architecture tests can enforce these boundaries and prevent regression.

### Extract Service

Extract service is the most complex extraction. It moves functionality from a monolith to a separate service. The Strangler Fig Pattern enables incremental migration: new functionality goes to the new service, old functionality gradually migrates, and both run in parallel.

Extract service requires careful planning. Identify the boundary of what to extract. Build the new service alongside the old code. Route new traffic to the new service. Gradually migrate existing functionality. Remove the old code when migration is complete.

Data migration is often the hardest part of service extraction. Data must be migrated without downtime. Consider dual-write patterns: write to both old and new systems during migration, then switch reads to the new system, then stop writing to the old system.

## The Strangler Fig Pattern

The Strangler Fig Pattern enables incremental migration from a monolith to microservices or between architectures. It reduces risk by allowing gradual migration and instant rollback.

### Step 1: Identify the Boundary

Identify the boundary of what to extract. This might be a business domain, a technical concern, or a set of related features. The boundary should be clear and well-defined. It should have minimal coupling to the rest of the system.

The boundary defines what belongs in the new system and what stays in the old system. It guides migration planning and helps prevent scope creep.

### Step 2: Build the New System Alongside the Old

Build the new service alongside the old code. Do not attempt to migrate everything at once. Start with new functionality: route new features to the new service. This validates that the new service works and that the boundary is correct.

Building alongside allows the team to learn. They discover issues early, when they're easier to fix. They validate assumptions about the boundary and the new architecture.

### Step 3: Route New Traffic to the New Service

Use feature flags to route new traffic to the new service. This enables gradual rollout and instant rollback. Start with a small percentage of traffic, monitor metrics, and gradually increase.

Feature flags control the routing. They can be toggled without code changes, enabling rapid response to issues. Monitoring compares old and new behavior, detecting regressions early.

### Step 4: Gradually Migrate Existing Functionality

Migrate existing functionality incrementally. Start with low-risk, well-understood functionality. Migrate one feature at a time, validate thoroughly, then move to the next.

Gradual migration reduces risk. Each migration is small and manageable. Issues are caught early, when they're easier to fix. The team learns from each migration, improving the process.

### Step 5: Remove the Old Code

Remove the old code only when migration is complete and confidence is high. Keep the old code until all functionality has been migrated and validated. Even then, consider keeping it for a period as a safety net.

Removing old code is a significant milestone. It represents successful migration and reduced maintenance burden. However, it's irreversible, so ensure confidence is high.

## When to Extract vs When to Duplicate

The decision to extract or duplicate is nuanced. Not all duplication is bad, and not all extraction is good. Understanding when to extract and when to duplicate prevents costly mistakes.

### The Rule of Three

Tolerate duplication twice. On the third occurrence, extract. This ensures the abstraction is based on real patterns, not speculation. The first occurrence might be coincidence. The second might still be coincidence. The third confirms a pattern.

The Rule of Three prevents premature abstraction. It ensures that extraction is based on evidence, not anticipation. The abstraction will fit naturally because it's derived from actual needs.

### Wrong Abstraction Cost

The wrong abstraction is far more costly than duplication. A shared function that sort of fits both use cases requires special cases, flags, and workarounds. It becomes harder to understand than the original duplicated code.

If you find yourself adding if/else branches to handle different use cases in a shared abstraction, consider inlining it back. The abstraction doesn't fit. Duplication would be clearer.

### Shared Libraries Between Services

Think carefully before creating shared libraries between services. A shared library couples services. If Service A and Service B share a library, changing the library requires coordinating deployments across both services.

Sometimes duplication between services is the correct choice. Services can evolve independently if they don't share code. The cost of duplication may be less than the cost of coupling.

Consider the stability of the shared code. If it's stable and unlikely to change, sharing may be acceptable. If it's evolving, duplication may be preferable to coupling.
