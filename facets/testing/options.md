---
recommendation_type: decision-matrix
---

# Testing: Options

## Testing Strategy Options

### 1. Test-Driven Development (TDD)

**Description**: Write tests first, then write implementation to make tests pass. Follow the Red-Green-Refactor cycle:
1. **Red**: Write a failing test
2. **Green**: Write minimal code to make test pass
3. **Refactor**: Improve code while keeping tests green

**Strengths**:
- Forces clear requirements before implementation
- Ensures testability (code written with tests in mind)
- High test coverage (tests written for all features)
- Tests serve as design documentation
- Prevents over-engineering (only implement what tests require)

**Weaknesses**:
- Slower initial development (writing tests takes time)
- Steep learning curve (requires discipline and practice)
- Can lead to over-testing (testing trivial code)
- May slow down prototyping (when requirements are unclear)
- Requires team buy-in and discipline

**Best For**:
- Well-understood requirements
- Business logic and algorithms
- API development
- Refactoring existing code
- Teams with TDD experience
- Critical systems requiring high reliability

**Avoid When**:
- Requirements are unclear or rapidly changing
- Prototyping and exploration
- UI design (visual design is hard to test-first)
- Spikes and proof-of-concepts
- Team lacks TDD experience or discipline

### 2. Behavior-Driven Development (BDD)

**Description**: Write specifications in Given-When-Then format, derive tests from specifications. Focus on behavior from user/stakeholder perspective. Often uses tools like Cucumber, SpecFlow, or Jest with BDD syntax.

**Strengths**:
- Business-friendly language (Given-When-Then)
- Aligns tests with user stories and acceptance criteria
- Promotes collaboration between developers, QA, and product
- Executable specifications (tests are the spec)
- Clear behavior documentation

**Weaknesses**:
- Overhead of maintaining BDD syntax
- Can become verbose (too many scenarios)
- Requires discipline to keep scenarios focused
- May slow down development (writing scenarios takes time)
- Can lead to brittle tests if scenarios are too detailed

**Best For**:
- User-facing features
- Complex business workflows
- Cross-functional teams (dev, QA, product)
- Systems with many acceptance criteria
- When specifications need to be executable
- Integration and E2E tests

**Avoid When**:
- Simple, straightforward features
- Internal APIs with no user-facing behavior
- Rapid prototyping
- Teams without BDD experience
- When BDD overhead outweighs benefits

### 3. Test-After Development

**Description**: Write implementation first, then add tests afterward. Tests verify that implementation works correctly.

**Strengths**:
- Faster initial development (no test-writing overhead)
- Natural workflow (implement, then verify)
- Easier for developers new to testing
- Flexible (can test what's important)
- Good for prototyping and exploration

**Weaknesses**:
- Lower test coverage (easy to skip tests)
- Tests may test implementation, not behavior
- Code may not be testable (written without tests in mind)
- Tests may be afterthoughts (low quality)
- May miss edge cases (not thinking about them during implementation)

**Best For**:
- Prototyping and exploration
- Rapid development when requirements are unclear
- Legacy code without tests
- When learning a new technology
- Spikes and proof-of-concepts
- Teams new to testing

**Avoid When**:
- Critical systems requiring high reliability
- Complex business logic
- When test coverage is important
- Long-term maintainable codebases
- Teams with testing discipline

### 4. Acceptance-Test-Driven Development (ATDD)

**Description**: Write acceptance tests first from outside-in, drive implementation from acceptance tests. Similar to BDD but focuses on acceptance criteria rather than behavior specifications.

**Strengths**:
- Clear acceptance criteria (tests define "done")
- Outside-in development (tests drive design)
- High confidence (acceptance tests verify features)
- Aligns with user stories and acceptance criteria
- Prevents scope creep (only implement what's accepted)

**Weaknesses**:
- Slower development (writing acceptance tests first)
- Requires clear acceptance criteria upfront
- May require E2E tests (slower feedback)
- Overhead of maintaining acceptance tests
- Can be brittle if acceptance tests are too detailed

**Best For**:
- User-facing features with clear acceptance criteria
- When acceptance criteria are well-defined
- Systems where "done" needs clear definition
- Integration and E2E testing
- When product owners write acceptance criteria

**Avoid When**:
- Internal APIs and services
- Rapid prototyping
- When acceptance criteria are unclear
- Teams without ATDD experience
- When acceptance test overhead is too high

## Test Distribution Options

### 1. Classic Pyramid

**Description**: Many unit tests (fast, isolated), some integration tests (medium speed, real dependencies), few E2E tests (slow, full system).

**Structure**:
```
        /\
       /  \     E2E Tests (5-10%)
      /____\
     /      \   Integration Tests (15-20%)
    /________\
   /          \ Unit Tests (70-80%)
  /____________\
```

**When to Use**:
- Business logic primarily in isolated units
- Fast feedback is critical
- Complex algorithms need thorough unit testing
- Clear boundaries between components
- Traditional layered architectures

### 2. Testing Diamond

**Description**: Focus on integration tests, fewer unit and E2E tests. Business logic lives in component interactions.

**Structure**:
```
    /\
   /  \     E2E Tests (5-10%)
  /____\
 /      \   Integration Tests (60-70%)
/________\
\        /  Unit Tests (20-30%)
 \______/
```

**When to Use**:
- Business logic in component interactions
- Microservices architectures
- Thin controllers, anemic domain models
- Configuration and wiring are complex
- When unit tests provide limited value

### 3. Testing Trophy

**Description**: Emphasize integration tests, include static analysis at base. Popular in frontend/React ecosystem.

**Structure**:
```
    /\
   /  \     E2E Tests (5-10%)
  /____\
 /      \   Integration Tests (50-60%)
/________\
\        /  Unit Tests (20-30%)
 \______/
    ||      Static Analysis (TypeScript, ESLint, SonarQube)
```

**When to Use**:
- Type-safe languages (TypeScript, Kotlin)
- Component-based architectures (React, Vue)
- When static analysis catches many bugs
- When unit testing framework internals provides limited value
- Frontend applications

## Evaluation Criteria

| Criteria | Weight | TDD | BDD | Test-After | ATDD |
|----------|--------|-----|-----|------------|------|
| **Test Coverage** | High | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Development Speed (Initial)** | Medium | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Code Quality** | High | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Test Maintainability** | High | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Business Alignment** | Medium | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Team Collaboration** | Medium | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | Low | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Requirement Clarity Needed** | Medium | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Suitable for Prototyping** | Low | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Documentation Value** | Medium | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**Legend**: ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Average | ⭐⭐ Below Average | ⭐ Poor

## Recommendation Guidance

### Choose TDD When:
- ✅ Requirements are well-understood
- ✅ Building business logic or algorithms
- ✅ Team has TDD experience
- ✅ Code quality and testability are priorities
- ✅ Building APIs or services
- ✅ Refactoring existing code

**Example**: Payment processing service with clear business rules

### Choose BDD When:
- ✅ User-facing features with complex workflows
- ✅ Cross-functional team (dev, QA, product)
- ✅ Need executable specifications
- ✅ Behavior documentation is important
- ✅ Integration and E2E testing focus
- ✅ Team values business-friendly language

**Example**: Multi-step checkout flow with complex business rules

### Choose Test-After When:
- ✅ Prototyping and exploration
- ✅ Requirements are unclear or changing rapidly
- ✅ Learning new technology
- ✅ Legacy code without tests
- ✅ Rapid development needed
- ✅ Team is new to testing

**Example**: Proof-of-concept for new feature, spike to evaluate technology

### Choose ATDD When:
- ✅ User-facing features with clear acceptance criteria
- ✅ Product owners write acceptance criteria
- ✅ Need clear definition of "done"
- ✅ Outside-in development approach
- ✅ Integration and E2E testing focus
- ✅ When acceptance criteria drive development

**Example**: User registration flow with well-defined acceptance criteria

### Hybrid Approach

**Common Pattern**: Use different strategies for different scenarios:
- **TDD** for business logic and algorithms
- **BDD** for user-facing features and workflows
- **Test-After** for prototyping and spikes
- **ATDD** for features with clear acceptance criteria

**Best Practice**: Don't be dogmatic. Use the right strategy for each scenario.

## Synergies

### Microservices Architecture

**If you chose microservices in backend-architecture**:
- ✅ Contract testing becomes essential (Pact, schema validation)
- ✅ Integration tests validate service boundaries
- ✅ E2E tests verify cross-service flows
- ✅ Test distribution: Diamond or Trophy (focus on integration)

**Testing Implications**:
- Consumer-driven contracts prevent breaking changes
- Service-level integration tests validate service behavior
- E2E tests verify end-to-end user journeys across services

### Continuous Deployment

**If you chose continuous deployment in ci-cd**:
- ✅ Fast test suite is critical (< 10 minutes for full suite)
- ✅ Test parallelization essential
- ✅ Flaky test rate must be < 1%
- ✅ Test distribution: Pyramid (many fast unit tests)

**Testing Implications**:
- Optimize slow tests (target < 1s per unit test)
- Parallelize test execution
- Quarantine or fix flaky tests immediately
- Prioritize fast feedback over comprehensive coverage

### Event Sourcing

**If you chose event sourcing in data-persistence**:
- ✅ Event-based test fixtures simplify testing
- ✅ Test event replay and state reconstruction
- ✅ Test event handlers in isolation
- ✅ Test distribution: Diamond (focus on integration)

**Testing Implications**:
- Create test fixtures from events (replay events to reconstruct state)
- Test event handlers independently
- Test event store behavior
- Integration tests verify event sourcing behavior

### Micro Frontends (MFE)

**If you chose MFE in frontend-architecture**:
- ✅ Component-level testing per MFE
- ✅ E2E tests for cross-MFE flows
- ✅ Contract testing for MFE APIs
- ✅ Test distribution: Trophy (component + integration focus)

**Testing Implications**:
- Unit and integration tests within each MFE
- E2E tests verify cross-MFE user journeys
- Contract tests verify MFE API boundaries
- Visual regression tests for MFE UI consistency

## Evolution Triggers

### Defect Escape Rate Increasing

**Trigger**: Defect escape rate > 10% (bugs found in production vs caught in testing)

**Actions**:
- Review test coverage (identify gaps)
- Add integration tests for integration points
- Add E2E tests for critical user journeys
- Review test quality (mutation testing)
- Consider moving from Test-After to TDD/BDD

**Example**: Payment bugs reaching production → Add integration tests for payment flows

### Test Suite Execution Time Exceeding CI Budget

**Trigger**: Test suite execution time > CI time budget (e.g., > 10 minutes)

**Actions**:
- Optimize slow tests (identify and optimize bottlenecks)
- Parallelize test execution (shard tests across runners)
- Move slow tests to separate suite (run less frequently)
- Consider test distribution (more unit tests, fewer E2E tests)
- Use test prioritization (run fast tests first)

**Example**: Test suite takes 30 minutes → Optimize slow integration tests, parallelize execution

### Team Growing and Needing Clearer Testing Contracts

**Trigger**: Team size increasing, inconsistent testing practices

**Actions**:
- Establish testing standards (coverage thresholds, naming conventions)
- Adopt BDD or ATDD for clearer specifications
- Create testing guidelines and best practices
- Implement code review for tests
- Provide testing training and mentorship

**Example**: Team grows from 5 to 20 developers → Establish BDD practices, create testing guidelines

### Moving from Manual QA to Automated Testing Pipeline

**Trigger**: Transitioning from manual QA to automated testing

**Actions**:
- Start with E2E tests for critical user journeys (replace manual QA)
- Add integration tests for API and database interactions
- Gradually add unit tests for business logic
- Establish CI/CD pipeline with automated tests
- Train QA team on test automation

**Example**: Manual QA taking too long → Automate critical user journeys with Playwright, add API integration tests

## Decision Matrix Summary

**For Most Teams**: Start with **Test-After** for rapid development, gradually adopt **TDD** for business logic, use **BDD** for user-facing features, and **ATDD** for features with clear acceptance criteria.

**For Critical Systems**: Use **TDD** for business logic, **BDD** for workflows, and **ATDD** for acceptance criteria. High test coverage and quality are priorities.

**For Rapid Prototyping**: Use **Test-After** to move fast, add tests when requirements stabilize.

**For Cross-Functional Teams**: Use **BDD** or **ATDD** to align developers, QA, and product around executable specifications.

The key is choosing the right strategy for each scenario and evolving your approach as your team and codebase mature.
