# Best Practices: Refactoring & Extraction

## Contents

- [Refactor in Small, Safe Steps](#refactor-in-small-safe-steps)
- [Boy Scout Rule](#boy-scout-rule)
- [Refactor What You're Working In](#refactor-what-youre-working-in)
- [Don't Mix Refactoring with Feature Work](#dont-mix-refactoring-with-feature-work)
- [Prefer Composition Over Inheritance](#prefer-composition-over-inheritance)
- [Extract When the Pattern Is Clear](#extract-when-the-pattern-is-clear)
- [Use Feature Flags for Risky Extractions](#use-feature-flags-for-risky-extractions)
- [Stack-Specific Practices](#stack-specific-practices)
- [Refactoring Tools and Automation](#refactoring-tools-and-automation)
- [Documentation and Communication](#documentation-and-communication)

## Refactor in Small, Safe Steps

Each refactoring step should result in a working state. Commit frequently. If a step breaks something, revert to the last working state. Never refactor and add features in the same commit.

Small steps reduce risk. Each step is easy to understand and verify. If something goes wrong, it's clear which step caused the problem. Small steps also make code review easier: reviewers can understand each change independently.

Commit frequently to preserve working states. If a refactoring goes wrong, you can revert to the last commit. Frequent commits also enable incremental code review: reviewers can review small changes rather than large refactorings.

Separate refactoring commits from feature commits. This makes it clear what changed for the feature versus what was cleaned up. It also makes reverts safer: if a feature has issues, you can revert the feature commit without reverting refactoring improvements.

## Boy Scout Rule

Leave the code better than you found it. When you touch a file to add a feature, clean up small issues: rename unclear variables, extract a method, add missing types. This prevents debt accumulation.

The Boy Scout Rule applies to small improvements, not large refactorings. When adding a feature, make small improvements to the code you're modifying. Don't refactor the entire file or module unless that's the task at hand.

Small improvements compound over time. Each developer makes small improvements, and the codebase gradually improves. This prevents debt accumulation without requiring dedicated refactoring sprints.

The Boy Scout Rule requires judgment. Some improvements are too large for a feature commit. If an improvement would require significant changes or testing, create a separate task. Small improvements are safe; large improvements should be planned.

## Refactor What You're Working In

Don't refactor code that works and isn't being changed. Refactoring has risk. Focus that risk on code that's actively being modified, where the investment has immediate payoff.

When you need to modify code for a feature, refactor that code first. The refactoring enables the feature, and the feature work validates that the refactoring improved maintainability. This creates a virtuous cycle: refactoring enables features, and feature work identifies areas that need refactoring.

Refactoring code you're not working in provides little value and introduces unnecessary risk. The code works, it's not being changed, and refactoring it doesn't enable future work. Focus refactoring effort on code that's actively being modified.

However, if code you're working in is too complex to modify safely, refactor it before adding the feature. The refactoring reduces risk and enables the feature. This is different from refactoring unrelated code: you're refactoring code you need to modify.

## Don't Mix Refactoring with Feature Work

Separate refactoring commits from feature commits. This makes code review easier, makes reverts safer, and makes it clear what changed for the feature versus what was cleaned up.

Ideally, refactor first in a separate pull request, then add the feature. This enables independent review and validation. Reviewers can focus on refactoring quality without being distracted by feature logic. After refactoring is merged, the feature pull request is simpler and easier to review.

If refactoring and feature work must be in the same pull request, separate them into distinct commits. This makes it easier to understand what changed and why. It also makes partial reverts possible: if the feature has issues, you can revert the feature commit while keeping refactoring improvements.

Mixing refactoring and feature work makes it impossible to tell if a bug came from the refactoring or the new feature. This slows debugging and increases risk. Separate the two to isolate risk and enable faster debugging.

## Prefer Composition Over Inheritance

When extracting shared behavior, default to composition. Use composables in Vue, hooks in React, or delegation in Kotlin. Inheritance creates rigid hierarchies that are difficult to change later.

Composition is more flexible than inheritance. Components can be combined in different ways without creating deep inheritance hierarchies. Composition also makes testing easier: you can test components independently and compose them in tests.

Inheritance creates coupling between parent and child classes. Changes to parent classes affect all child classes. This makes evolution difficult: changing a parent class requires understanding all child classes.

Composition enables independent evolution. Components can evolve independently as long as their interfaces remain compatible. This makes the codebase more maintainable and easier to change.

## Extract When the Pattern Is Clear

Premature extraction creates wrong abstractions. Wait until you've seen the pattern three times. The first two times, the similarity might be coincidental. The third time confirms the pattern.

The Rule of Three helps decide when to extract. Tolerate duplication twice. On the third occurrence, extract. This ensures the abstraction is based on real patterns, not speculation. The abstraction will fit naturally because it's derived from actual needs.

Extracting after the first occurrence creates an abstraction based on speculation. The abstraction may not fit the second use case, requiring special cases and workarounds. This is more expensive than duplication.

Wait for patterns to emerge from actual usage. Don't anticipate patterns. Real patterns are based on evidence; anticipated patterns are based on speculation. Evidence-based abstractions are more likely to be correct.

### Example: Before/After Refactoring

**Before: Long Function with Multiple Responsibilities**

```kotlin
fun processOrder(order: Order): OrderResult {
    // Validate order
    if (order.items.isEmpty()) {
        return OrderResult.Error("Order must contain at least one item")
    }
    if (order.customerId.isBlank()) {
        return OrderResult.Error("Customer ID is required")
    }
    if (order.totalAmount <= 0) {
        return OrderResult.Error("Total amount must be positive")
    }
    
    // Calculate discounts
    var discount = 0.0
    if (order.totalAmount > 100) {
        discount = order.totalAmount * 0.1
    }
    if (order.customer.isPremium) {
        discount += order.totalAmount * 0.05
    }
    val finalAmount = order.totalAmount - discount
    
    // Apply tax
    val taxRate = when (order.shippingAddress.country) {
        "US" -> 0.08
        "CA" -> 0.13
        else -> 0.0
    }
    val tax = finalAmount * taxRate
    val totalWithTax = finalAmount + tax
    
    // Process payment
    val paymentResult = paymentService.charge(order.customerId, totalWithTax)
    if (!paymentResult.success) {
        return OrderResult.Error("Payment failed: ${paymentResult.message}")
    }
    
    // Update inventory
    order.items.forEach { item ->
        inventoryService.decreaseStock(item.productId, item.quantity)
    }
    
    // Send confirmation
    emailService.sendConfirmation(order.customer.email, order.id)
    
    return OrderResult.Success(order.id, totalWithTax)
}
```

**After: Extracted Functions with Single Responsibilities**

```kotlin
fun processOrder(order: Order): OrderResult {
    val validationResult = validateOrder(order)
    if (validationResult is ValidationResult.Invalid) {
        return OrderResult.Error(validationResult.message)
    }
    
    val pricing = calculatePricing(order)
    val paymentResult = processPayment(order.customerId, pricing.total)
    
    if (!paymentResult.success) {
        return OrderResult.Error("Payment failed: ${paymentResult.message}")
    }
    
    updateInventory(order.items)
    sendConfirmation(order)
    
    return OrderResult.Success(order.id, pricing.total)
}

private fun validateOrder(order: Order): ValidationResult {
    return when {
        order.items.isEmpty() -> 
            ValidationResult.Invalid("Order must contain at least one item")
        order.customerId.isBlank() -> 
            ValidationResult.Invalid("Customer ID is required")
        order.totalAmount <= 0 -> 
            ValidationResult.Invalid("Total amount must be positive")
        else -> ValidationResult.Valid
    }
}

private fun calculatePricing(order: Order): Pricing {
    val discount = calculateDiscount(order)
    val finalAmount = order.totalAmount - discount
    val tax = calculateTax(finalAmount, order.shippingAddress.country)
    return Pricing(finalAmount, tax, finalAmount + tax)
}

private fun calculateDiscount(order: Order): Double {
    var discount = 0.0
    if (order.totalAmount > 100) {
        discount += order.totalAmount * 0.1
    }
    if (order.customer.isPremium) {
        discount += order.totalAmount * 0.05
    }
    return discount
}

private fun calculateTax(amount: Double, country: String): Double {
    val taxRate = when (country) {
        "US" -> 0.08
        "CA" -> 0.13
        else -> 0.0
    }
    return amount * taxRate
}

private fun processPayment(customerId: String, amount: Double): PaymentResult {
    return paymentService.charge(customerId, amount)
}

private fun updateInventory(items: List<OrderItem>) {
    items.forEach { item ->
        inventoryService.decreaseStock(item.productId, item.quantity)
    }
}

private fun sendConfirmation(order: Order) {
    emailService.sendConfirmation(order.customer.email, order.id)
}
```

The refactored version separates concerns into focused functions, making the code easier to understand, test, and maintain.

## Use Feature Flags for Risky Extractions

When extracting a service or major module, use feature flags to route traffic between old and new implementations. This enables gradual migration and instant rollback.

Feature flags control routing without code changes. They can be toggled instantly, enabling rapid response to issues. Start with a small percentage of traffic routed to the new implementation, monitor metrics, and gradually increase.

Feature flags enable A/B testing. Compare metrics between old and new implementations. If metrics diverge significantly, investigate. The new implementation may have performance issues or behavioral differences.

Feature flags also enable canary deployments. Route a small percentage of traffic to the new implementation, validate thoroughly, then increase gradually. If issues arise, route traffic back to the old implementation instantly.

## Stack-Specific Practices

### Kotlin

Sealed classes enable exhaustive refactoring. The compiler catches missing cases when adding or removing variants. This makes refactoring safer: if you add a new variant, the compiler forces you to handle it everywhere.

Extension functions add behavior without modifying classes. This enables adding functionality to existing classes without changing their structure. Extension functions are particularly useful for adding domain-specific behavior to library classes.

Data class copy() enables immutable transformations. Instead of modifying objects, create new objects with changed properties. This makes refactoring safer: immutable code is easier to reason about and test.

### Spring Boot

Spring Modulith enforces module boundaries during extraction. It verifies that modules don't access each other's internals, except through defined APIs. This prevents boundary violations and enables safe module extraction.

@ConditionalOnProperty toggles between old and new implementations. Use feature flags to control which implementation is active. This enables gradual migration and instant rollback.

Spring's dependency injection makes extraction easier. Dependencies are injected, not hardcoded. This enables swapping implementations without changing client code. Extract interfaces to enable implementation swapping.

### Vue 3

Extract component logic into composables before extracting components. Composables encapsulate reusable logic, making it easier to extract into separate components. Composables can be tested independently and reused across components.

defineAsyncComponent enables lazy-loaded extracted features. Large features can be extracted into separate components that load on demand. This improves initial load time and enables independent deployment of features.

Vue's reactivity system makes refactoring safer. Reactive dependencies are tracked automatically, so refactoring reactive code is less error-prone. However, be careful with refactoring reactive code: ensure reactivity is preserved.

### React

Extract component logic into custom hooks before extracting components. Hooks encapsulate reusable logic, making it easier to extract into separate components. Hooks can be tested independently and reused across components.

React.lazy enables lazy-loaded extracted features. Large features can be extracted into separate components that load on demand. This improves initial load time and enables independent deployment of features.

React's component model makes extraction easier. Components are composable, so extracting a component is straightforward. However, be careful with prop drilling: extracted components may need access to data from parent components.

## Refactoring Tools and Automation

Modern IDEs provide automated refactoring support. Use these tools instead of manual refactoring. Automated refactoring is safer and faster than manual refactoring.

Automated refactoring tools understand code structure. They can rename symbols across the entire codebase, extract methods while preserving behavior, and move code while updating references. This reduces the risk of errors.

However, automated refactoring tools are not perfect. They may miss dynamic language features, reflection, or complex dependencies. Always run tests after automated refactoring to verify behavior is preserved.

Use static analysis tools to identify code smells. These tools can detect long methods, large classes, duplicate code, and other issues. However, not all detected issues need immediate fixing. Use judgment to prioritize refactoring opportunities.

## Documentation and Communication

Document refactoring decisions. Explain why code was refactored, what changed, and what the new structure enables. This helps future developers understand the codebase evolution.

Update documentation after refactoring. Outdated documentation misleads developers and creates confusion. Keep documentation in sync with code changes.

Communicate large refactorings to the team. Explain the motivation, the approach, and the expected benefits. This helps the team understand changes and provides opportunities for feedback.

Large refactorings may require team coordination. If multiple developers work in the same area, coordinate refactoring efforts to avoid conflicts. Consider feature flags or branch strategies to enable parallel work.
