# Gotchas: Onboarding

Common pitfalls and anti-patterns to avoid when building onboarding experiences.

## Contents

- [Mandatory Tutorials That Can't Be Skipped](#mandatory-tutorials-that-cant-be-skipped)
- [Onboarding That Doesn't Persist Progress](#onboarding-that-doesnt-persist-progress)
- [Tooltip Tours That Break When UI Changes](#tooltip-tours-that-break-when-ui-changes)
- [Onboarding Coupled to Specific UI Layout](#onboarding-coupled-to-specific-ui-layout)
- [Showing All Features at Once](#showing-all-features-at-once)
- [Onboarding That Only Runs Once](#onboarding-that-only-runs-once)
- [B2B: Org Admin Completes Onboarding, Invited Users Get No Guidance](#b2b-org-admin-completes-onboarding-invited-users-get-no-guidance)
- [A/B Testing Without Measuring Activation](#ab-testing-without-measuring-activation)
- [Stale Onboarding Content](#stale-onboarding-content)
- [Analytics Events Not Firing Due to Ad Blockers](#analytics-events-not-firing-due-to-ad-blockers)

## Mandatory Tutorials That Can't Be Skipped

**Problem:** Forcing users through onboarding without an escape hatch causes abandonment.

**Anti-Pattern:**
```typescript
// BAD: Blocking modal with no skip
function OnboardingModal() {
  return (
    <Modal blocking={true} closable={false}>
      <OnboardingContent />
      {/* No skip button! */}
    </Modal>
  );
}
```

**Impact:** Users who want to explore will leave. High abandonment rate.

**Solution:** Always provide skip option, make it visible but not prominent:

```typescript
// GOOD: Skip always available
function OnboardingModal() {
  return (
    <Modal blocking={false} closable={true}>
      <button className="skip-button">Skip for now</button>
      <OnboardingContent />
    </Modal>
  );
}
```

**Detection:** Monitor onboarding completion rate. If it's 100%, users probably can't skip. If it's <20%, onboarding might not be valuable enough.

## Onboarding That Doesn't Persist Progress

**Problem:** User refreshes page or closes browser, loses all progress, starts over.

**Anti-Pattern:**
```typescript
// BAD: Progress only in component state
function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState(0);
  // No persistence! Lost on refresh.
}
```

**Impact:** Frustrated users abandon after losing progress multiple times.

**Solution:** Persist to database or localStorage:

```typescript
// GOOD: Persist progress
function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState(() => {
    // Load from localStorage or API
    return loadOnboardingProgress();
  });
  
  useEffect(() => {
    // Save on every step change
    saveOnboardingProgress(currentStep);
  }, [currentStep]);
}
```

**Database-backed (production):**
```kotlin
// Spring Boot: Persist to database
@Transactional
fun saveProgress(userId: UUID, step: String) {
  val onboarding = onboardingRepository.findByUserId(userId)
    ?: Onboarding(userId = userId)
  
  onboarding.currentStep = step
  onboardingRepository.save(onboarding)
}
```

## Tooltip Tours That Break When UI Changes

**Problem:** Tours use fragile CSS selectors that break when UI is refactored.

**Anti-Pattern:**
```typescript
// BAD: Fragile selectors
const tourSteps = [
  {
    target: '.dashboard > div:nth-child(2) > button', // Breaks on layout change!
    content: 'Click here to create a project'
  }
];
```

**Impact:** Tours break silently, point to wrong elements, or fail entirely after UI updates.

**Solution:** Use stable data attributes:

```typescript
// GOOD: Stable data-testid selectors
const tourSteps = [
  {
    target: '[data-testid="create-project-button"]', // Stable!
    content: 'Click here to create a project'
  }
];
```

**Best Practice:**
```vue
<!-- Always include data-testid for tours and tests -->
<button 
  data-testid="create-project-button"
  class="btn btn-primary"
>
  Create Project
</button>
```

## Onboarding Coupled to Specific UI Layout

**Problem:** Onboarding assumes desktop layout, breaks on mobile/responsive.

**Anti-Pattern:**
```typescript
// BAD: Assumes desktop layout
const tourSteps = [
  {
    target: '.sidebar .projects-menu', // Doesn't exist on mobile!
    content: 'Your projects are here'
  }
];
```

**Impact:** Mobile users get broken tours or no onboarding at all.

**Solution:** Responsive tour steps:

```typescript
// GOOD: Adapt to screen size
function getTourSteps() {
  const isMobile = window.innerWidth < 768;
  
  return isMobile 
    ? mobileTourSteps  // Hamburger menu, bottom nav
    : desktopTourSteps; // Sidebar, top nav
}
```

**Or use responsive selectors:**
```typescript
const tourSteps = [
  {
    target: isMobile 
      ? '[data-testid="mobile-projects-menu"]'
      : '[data-testid="desktop-projects-menu"]',
    content: 'Your projects are here'
  }
];
```

## Showing All Features at Once

**Problem:** Overwhelming users with 20+ tooltips on first visit.

**Anti-Pattern:**
```typescript
// BAD: Show everything immediately
function showAllOnboardingTips() {
  showTip('feature-1');
  showTip('feature-2');
  showTip('feature-3');
  // ... 20 more tips
  // User overwhelmed, closes everything
}
```

**Impact:** Cognitive overload, users dismiss everything, learn nothing.

**Solution:** Progressive disclosure, contextual tips:

```typescript
// GOOD: Show tips contextually
function showContextualTip(feature: string) {
  // Only show when user reaches that feature
  if (userIsOnFeaturePage(feature) && !hasSeenTip(feature)) {
    showTip(feature);
  }
}

// Or limit to 3-5 tips per session
const MAX_TIPS_PER_SESSION = 3;
let tipsShownThisSession = 0;

function showTip(feature: string) {
  if (tipsShownThisSession < MAX_TIPS_PER_SESSION) {
    displayTip(feature);
    tipsShownThisSession++;
  }
}
```

## Onboarding That Only Runs Once

**Problem:** Users can't replay onboarding or access help after dismissing.

**Anti-Pattern:**
```typescript
// BAD: One-time only flag
const hasSeenOnboarding = localStorage.getItem('onboarding-seen');
if (!hasSeenOnboarding) {
  showOnboarding();
  localStorage.setItem('onboarding-seen', 'true');
}
// No way to see it again!
```

**Impact:** Users who want to learn more have no way to access guidance.

**Solution:** Provide replay option:

```typescript
// GOOD: Allow replay
function OnboardingSettings() {
  return (
    <Settings>
      <Section title="Help & Support">
        <Button onClick={replayOnboarding}>
          Take the Tour Again
        </Button>
        <Button onClick={showHelpCenter}>
          View Help Center
        </Button>
      </Section>
    </Settings>
  );
}
```

**Or show in help menu:**
```vue
<!-- Help menu with onboarding replay -->
<DropdownMenu>
  <MenuItem @click="replayOnboarding">
    <Icon name="tour" />
    Take the Tour
  </MenuItem>
  <MenuItem @click="showTips">
    <Icon name="lightbulb" />
    Show Tips
  </MenuItem>
</DropdownMenu>
```

## B2B: Org Admin Completes Onboarding, Invited Users Get No Guidance

**Problem:** In multi-tenant SaaS, admin completes org setup, but invited users see no onboarding.

**Anti-Pattern:**
```typescript
// BAD: Only check org-level onboarding
if (org.onboardingCompleted) {
  // Skip all user onboarding
  // Invited users get no guidance!
}
```

**Impact:** New team members are lost, don't know how to use the product.

**Solution:** Separate org-level and user-level onboarding:

```typescript
// GOOD: Two-level onboarding
function getOnboardingStatus(user: User, org: Organization) {
  return {
    orgOnboarding: org.onboardingStatus, // Admin completes this
    userOnboarding: user.onboardingStatus // Each user has their own
  };
}

// New user joining existing org
if (org.onboardingCompleted && user.onboardingStatus === 'new') {
  // Show user-level onboarding
  startUserOnboarding(user, {
    context: 'joining-existing-org',
    skipOrgSetup: true
  });
}
```

**Implementation:**
```kotlin
// Spring Boot: Separate tracking
@Entity
class OrganizationOnboarding(
  val orgId: UUID,
  var status: OnboardingStatus
)

@Entity
class UserOnboarding(
  val userId: UUID,
  val orgId: UUID,
  var status: OnboardingStatus
)

// Check both
fun shouldShowOnboarding(user: User): Boolean {
  val orgOnboarding = orgOnboardingRepo.findByOrgId(user.orgId)
  val userOnboarding = userOnboardingRepo.findByUserId(user.id)
  
  // User needs onboarding even if org is set up
  return userOnboarding?.status != OnboardingStatus.COMPLETED
}
```

## A/B Testing Without Measuring Activation

**Problem:** Testing onboarding completion rate but not whether users actually activate.

**Anti-Pattern:**
```typescript
// BAD: Only measure completion
const variantACompletionRate = 0.85; // 85% complete
const variantBCompletionRate = 0.90; // 90% complete
// Choose B! But wait... are they activating?
```

**Impact:** Optimize for wrong metric, users complete onboarding but don't use product.

**Solution:** Measure activation, not just completion:

```typescript
// GOOD: Measure activation
const metrics = {
  variantA: {
    completionRate: 0.85,
    activationRate: 0.45, // 45% activate after completing
    timeToActivate: 8.5 // minutes
  },
  variantB: {
    completionRate: 0.90,
    activationRate: 0.35, // Only 35% activate!
    timeToActivate: 12.3 // Slower
  }
};

// Variant A is better despite lower completion
```

**Analytics Query:**
```sql
-- Measure activation, not just completion
SELECT 
  onboarding_variant,
  COUNT(*) as completed_onboarding,
  COUNT(CASE WHEN activated_within_7_days THEN 1 END) as activated,
  ROUND(100.0 * COUNT(CASE WHEN activated_within_7_days THEN 1 END) / COUNT(*), 2) as activation_rate
FROM user_onboarding
WHERE status = 'completed'
GROUP BY onboarding_variant;
```

## Stale Onboarding Content

**Problem:** Product changes but onboarding still references old UI/features.

**Anti-Pattern:**
```typescript
// BAD: Hardcoded feature references
const onboardingSteps = [
  {
    target: '.old-feature-button', // Feature was removed 6 months ago!
    content: 'Click here to use the old feature'
  }
];
```

**Impact:** Confused users, broken tours, support tickets.

**Solution:** Version onboarding content, review regularly:

```typescript
// GOOD: Versioned onboarding
const onboardingConfig = {
  version: '2.1.0', // Match app version
  steps: [
    {
      id: 'create-project',
      target: '[data-testid="create-project-button"]',
      content: 'Create your first project',
      minAppVersion: '2.0.0' // Only show if app >= 2.0.0
    }
  ]
};

// Validate on load
function validateOnboardingConfig(config, appVersion) {
  if (config.version !== appVersion) {
    console.warn('Onboarding config may be stale');
    // Flag for review
  }
}
```

**Process:**
1. Review onboarding content in every release
2. Update when features change
3. Remove references to deprecated features
4. Test tours after UI changes

## Analytics Events Not Firing Due to Ad Blockers

**Problem:** Ad blockers prevent analytics scripts from loading, onboarding events aren't tracked.

**Anti-Pattern:**
```typescript
// BAD: Assumes analytics always works
function completeStep(stepId: string) {
  // Analytics might be blocked!
  analytics.track('onboarding_step_completed', { stepId });
  // No fallback, no error handling
}
```

**Impact:** Missing data, can't measure onboarding effectiveness, can't optimize.

**Solution:** Graceful degradation, server-side tracking fallback:

```typescript
// GOOD: Fallback to server-side tracking
async function completeStep(stepId: string) {
  try {
    // Try client-side analytics
    analytics.track('onboarding_step_completed', { stepId });
  } catch (error) {
    // Fallback to server-side
    await api.post('/onboarding/analytics', {
      event: 'onboarding_step_completed',
      stepId
    });
  }
}
```

**Server-side tracking (always works):**
```kotlin
// Spring Boot: Server-side event tracking
@PostMapping("/onboarding/steps/{stepId}/complete")
fun completeStep(
  @PathVariable stepId: String,
  @AuthenticationPrincipal user: User
) {
  onboardingService.completeStep(user.id, stepId)
  
  // Always track server-side (can't be blocked)
  analyticsService.track(
    event = "onboarding_step_completed",
    userId = user.id,
    properties = mapOf("step_id" to stepId)
  )
}
```

**Detection:**
```typescript
// Detect if analytics is blocked
function isAnalyticsBlocked(): boolean {
  // Check if analytics library loaded
  if (typeof analytics === 'undefined') {
    return true;
  }
  
  // Try to track test event
  try {
    analytics.track('test');
    return false;
  } catch {
    return true;
  }
}

// Use server-side if blocked
if (isAnalyticsBlocked()) {
  useServerSideTracking();
}
```
