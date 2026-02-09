# Architecture: Onboarding

Technical patterns, data models, and implementation approaches for building effective onboarding experiences.

## Contents

- [Onboarding State Machine](#onboarding-state-machine)
- [Step/Checklist Architecture](#stepchecklist-architecture)
- [Progressive Disclosure Implementation](#progressive-disclosure-implementation)
- [Onboarding Data Model](#onboarding-data-model)
- [Feature Flag Integration](#feature-flag-integration)
- [Analytics Integration](#analytics-integration)
- [Empty State Design](#empty-state-design)
- [B2B SaaS Considerations](#b2b-saas-considerations)
- [Server-Side Implementation](#server-side-implementation)

## Onboarding State Machine

Onboarding is fundamentally a state machine. Users move through states: `new` → `in-progress` → `completed` or `skipped`.

### User States

```typescript
enum OnboardingStatus {
  NEW = 'new',              // User hasn't started onboarding
  IN_PROGRESS = 'in-progress', // User is actively onboarding
  COMPLETED = 'completed',   // User finished onboarding
  SKIPPED = 'skipped'        // User explicitly skipped
}
```

### Persisting Progress

**Critical**: Onboarding progress must persist across sessions. Users refresh, close browsers, switch devices. If they lose progress, they'll abandon.

**Implementation approaches:**

**Database-backed (recommended for production):**
```sql
CREATE TABLE user_onboarding (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  current_step VARCHAR(100),
  status VARCHAR(20) NOT NULL,
  progress JSONB, -- Flexible storage for step-specific data
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  skipped_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**localStorage (simple, client-only):**
```typescript
// Vue 3 / Pinia example
interface OnboardingState {
  status: OnboardingStatus;
  currentStep: string;
  completedSteps: string[];
}

// Persist to localStorage on each step change
watch(() => onboardingStore.state, (state) => {
  localStorage.setItem('onboarding', JSON.stringify(state));
}, { deep: true });
```

### Resuming Interrupted Onboarding

When a user returns, check their onboarding status:

```typescript
// Spring Boot service example
@Service
public class OnboardingService {
  
  public OnboardingStatus getOnboardingStatus(UUID userId) {
    return onboardingRepository.findByUserId(userId)
      .map(Onboarding::getStatus)
      .orElse(OnboardingStatus.NEW);
  }
  
  public void resumeOnboarding(UUID userId) {
    Onboarding onboarding = onboardingRepository.findByUserId(userId)
      .orElseThrow();
    
    if (onboarding.getStatus() == OnboardingStatus.IN_PROGRESS) {
      // Return user to their last step
      return onboarding.getCurrentStep();
    }
  }
}
```

## Step/Checklist Architecture

Onboarding consists of discrete steps. Steps can be ordered (sequential) or unordered (checklist), and can be conditional based on user attributes.

### Ordered vs Unordered Steps

**Ordered (sequential):**
```typescript
const onboardingSteps = [
  'welcome',
  'profile-setup',
  'first-project',
  'invite-team',
  'explore-features'
];
// Users must complete in order
```

**Unordered (checklist):**
```typescript
const onboardingChecklist = [
  'complete-profile',
  'create-first-project',
  'invite-team-member',
  'connect-integration'
];
// Users can complete in any order
// Mark complete when all done
```

### Conditional Steps

Steps should appear based on user role, plan, or other attributes:

```typescript
// Vue 3 example with conditional steps
const getOnboardingSteps = (user: User) => {
  const baseSteps = ['welcome', 'profile-setup'];
  
  if (user.role === 'admin') {
    baseSteps.push('org-setup', 'team-invite');
  }
  
  if (user.plan === 'enterprise') {
    baseSteps.push('sso-setup', 'audit-log-config');
  }
  
  return baseSteps;
};
```

### Completion Tracking

Track which steps are completed:

```sql
CREATE TABLE onboarding_step_completion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  step_id VARCHAR(100) NOT NULL,
  completed_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB, -- Step-specific completion data
  UNIQUE(user_id, step_id)
);
```

```typescript
// React example with step completion
const OnboardingContext = createContext();

function OnboardingProvider({ children }) {
  const [completedSteps, setCompletedSteps] = useState(new Set());
  
  const completeStep = async (stepId: string) => {
    await api.post(`/onboarding/steps/${stepId}/complete`);
    setCompletedSteps(prev => new Set([...prev, stepId]));
  };
  
  return (
    <OnboardingContext.Provider value={{ completedSteps, completeStep }}>
      {children}
    </OnboardingContext.Provider>
  );
}
```

## Progressive Disclosure Implementation

Progressive disclosure means revealing features and complexity gradually, based on user readiness and context.

### Feature Gating by Onboarding Stage

Don't show advanced features until users complete foundational onboarding:

```typescript
// Vue 3 composable
export function useFeatureGate() {
  const onboardingStore = useOnboardingStore();
  
  const isFeatureAvailable = (feature: string) => {
    const requiredSteps = featureGates[feature] || [];
    return requiredSteps.every(step => 
      onboardingStore.completedSteps.includes(step)
    );
  };
  
  return { isFeatureAvailable };
}

// Usage in component
const { isFeatureAvailable } = useFeatureGate();
if (!isFeatureAvailable('advanced-analytics')) {
  return <OnboardingPrompt feature="advanced-analytics" />;
}
```

### Tooltip/Popover Tours

Guided tours that highlight UI elements:

```typescript
// React with react-joyride
import Joyride from 'react-joyride';

const steps = [
  {
    target: '.project-list',
    content: 'Your projects appear here. Create your first one!',
    placement: 'bottom'
  },
  {
    target: '.create-button',
    content: 'Click here to create a new project.',
    placement: 'right'
  }
];

function OnboardingTour() {
  const [run, setRun] = useState(false);
  
  useEffect(() => {
    if (shouldShowTour()) {
      setRun(true);
    }
  }, []);
  
  return (
    <Joyride
      steps={steps}
      run={run}
      continuous={true}
      showProgress={true}
      callback={(data) => {
        if (data.status === 'finished') {
          completeStep('feature-tour');
        }
      }}
    />
  );
}
```

### Contextual Help

Show help when users reach relevant features, not all upfront:

```typescript
// Vue 3: Show tooltip when user first hovers over feature
const showContextualTip = (feature: string) => {
  const hasSeenTip = localStorage.getItem(`tip-seen-${feature}`);
  if (!hasSeenTip && isFirstTimeUser()) {
    showTooltip(feature);
    localStorage.setItem(`tip-seen-${feature}`, 'true');
  }
};
```

## Onboarding Data Model

### Core Tables

```sql
-- User onboarding status
CREATE TABLE user_onboarding (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  current_step VARCHAR(100),
  status VARCHAR(20) NOT NULL DEFAULT 'new',
  variant VARCHAR(50), -- For A/B testing
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  skipped_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Step completion tracking
CREATE TABLE onboarding_step_completion (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  step_id VARCHAR(100) NOT NULL,
  completed_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  UNIQUE(user_id, step_id)
);

-- Onboarding configuration (A/B variants)
CREATE TABLE onboarding_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  variant_key VARCHAR(50) UNIQUE NOT NULL,
  steps JSONB NOT NULL, -- Array of step definitions
  target_audience JSONB, -- Role, plan, etc.
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Spring Boot Entity Example

```kotlin
@Entity
@Table(name = "user_onboarding")
data class UserOnboarding(
  @Id
  val userId: UUID,
  
  @Column(name = "current_step")
  var currentStep: String? = null,
  
  @Enumerated(EnumType.STRING)
  @Column(name = "status", nullable = false)
  var status: OnboardingStatus = OnboardingStatus.NEW,
  
  @Column(name = "variant")
  var variant: String? = null,
  
  @Column(name = "started_at")
  var startedAt: Instant? = null,
  
  @Column(name = "completed_at")
  var completedAt: Instant? = null,
  
  @Column(name = "skipped_at")
  var skippedAt: Instant? = null,
  
  @Column(name = "updated_at")
  var updatedAt: Instant = Instant.now()
)
```

## Feature Flag Integration

Use feature flags to control onboarding rollout and A/B testing:

```typescript
// LaunchDarkly integration example
import * as LaunchDarkly from 'launchdarkly-js-client-sdk';

const client = LaunchDarkly.initialize('YOUR_CLIENT_ID', user);

client.on('ready', () => {
  const onboardingVariant = client.variation('onboarding-variant', 'default');
  const showNewOnboarding = client.variation('new-onboarding-flow', false);
  
  if (showNewOnboarding) {
    startOnboardingFlow(onboardingVariant);
  }
});
```

**Graduated rollout:**
1. 10% of new users → measure activation
2. 50% of new users → compare metrics
3. 100% if metrics improve

## Analytics Integration

Track every onboarding interaction to understand drop-off and optimize:

```typescript
// Analytics event tracking
function trackOnboardingEvent(event: string, properties?: Record<string, any>) {
  // Segment, Mixpanel, PostHog, or custom
  analytics.track('onboarding_' + event, {
    userId: user.id,
    step: currentStep,
    timestamp: new Date().toISOString(),
    ...properties
  });
}

// Track step completion
trackOnboardingEvent('step_completed', {
  step_id: 'profile-setup',
  time_spent: 120, // seconds
  skipped: false
});

// Track drop-off
trackOnboardingEvent('step_abandoned', {
  step_id: 'team-invite',
  time_spent: 45,
  reason: 'user_closed_modal'
});
```

**Funnel analysis:**
```sql
-- Query drop-off rates
SELECT 
  step_id,
  COUNT(*) as started,
  COUNT(completed_at) as completed,
  COUNT(*) - COUNT(completed_at) as dropped_off,
  ROUND(100.0 * (COUNT(*) - COUNT(completed_at)) / COUNT(*), 2) as dropoff_rate
FROM onboarding_step_completion
GROUP BY step_id
ORDER BY step_order;
```

## Empty State Design

Every empty list, dashboard, or section is an onboarding opportunity. Empty states should guide action, not just inform.

**Good empty state:**
```vue
<!-- Vue 3 example -->
<template>
  <div class="empty-state">
    <Icon name="project" size="64" />
    <h2>No projects yet</h2>
    <p>Create your first project to get started</p>
    <Button @click="startOnboardingStep('create-project')">
      Create Project
    </Button>
    <a href="#" @click="skip">I'll do this later</a>
  </div>
</template>
```

**Empty states as onboarding triggers:**
- First empty project list → Show project creation guide
- First empty team list → Show team invitation flow
- First empty dashboard → Show data import options
- First empty settings → Show configuration wizard

## B2B SaaS Considerations

Multi-tenant architectures require two-level onboarding:

### Org-Level Onboarding

Admin configures the organization:
- Company settings (name, domain, branding)
- Team invitation and role assignment
- Integration setup (SSO, APIs, webhooks)
- Billing and subscription management
- Security and compliance settings

```typescript
// Org onboarding steps
const orgOnboardingSteps = [
  'company-details',
  'domain-verification',
  'invite-team',
  'configure-sso',
  'setup-billing'
];
```

### User-Level Onboarding

Individual users learn the product:
- Feature discovery tours
- Role-specific guidance
- Personal preferences
- First actions within org context

```typescript
// User onboarding (within org context)
const userOnboardingSteps = [
  'welcome-to-org',
  'your-role',
  'key-features',
  'first-action'
];
```

**Key distinction**: When an admin completes org onboarding, that doesn't mean invited users are onboarded. Each user needs their own onboarding experience.

## Server-Side Implementation

### Spring Boot Onboarding Service

```kotlin
@Service
class OnboardingService(
  private val onboardingRepository: OnboardingRepository,
  private val eventPublisher: ApplicationEventPublisher
) {
  
  fun startOnboarding(userId: UUID, variant: String? = null): Onboarding {
    val onboarding = Onboarding(
      userId = userId,
      status = OnboardingStatus.IN_PROGRESS,
      variant = variant,
      startedAt = Instant.now()
    )
    
    val saved = onboardingRepository.save(onboarding)
    eventPublisher.publishEvent(OnboardingStartedEvent(userId, variant))
    return saved
  }
  
  fun completeStep(userId: UUID, stepId: String, metadata: Map<String, Any>? = null) {
    val onboarding = onboardingRepository.findByUserId(userId)
      ?: throw OnboardingNotFoundException(userId)
    
    // Save step completion
    stepCompletionRepository.save(
      StepCompletion(userId, stepId, metadata)
    )
    
    // Update current step
    onboarding.currentStep = getNextStep(onboarding, stepId)
    onboardingRepository.save(onboarding)
    
    // Publish event for analytics
    eventPublisher.publishEvent(
      OnboardingStepCompletedEvent(userId, stepId, metadata)
    )
  }
  
  fun completeOnboarding(userId: UUID) {
    val onboarding = onboardingRepository.findByUserId(userId)
      ?: throw OnboardingNotFoundException(userId)
    
    onboarding.status = OnboardingStatus.COMPLETED
    onboarding.completedAt = Instant.now()
    onboardingRepository.save(onboarding)
    
    eventPublisher.publishEvent(OnboardingCompletedEvent(userId))
  }
}
```

### REST Endpoints

```kotlin
@RestController
@RequestMapping("/api/onboarding")
class OnboardingController(
  private val onboardingService: OnboardingService
) {
  
  @GetMapping("/status")
  fun getStatus(@AuthenticationPrincipal user: User): OnboardingStatusResponse {
    return onboardingService.getStatus(user.id)
  }
  
  @PostMapping("/start")
  fun startOnboarding(
    @AuthenticationPrincipal user: User,
    @RequestBody request: StartOnboardingRequest
  ): OnboardingStatusResponse {
    return onboardingService.startOnboarding(user.id, request.variant)
  }
  
  @PostMapping("/steps/{stepId}/complete")
  fun completeStep(
    @AuthenticationPrincipal user: User,
    @PathVariable stepId: String,
    @RequestBody metadata: Map<String, Any>?
  ) {
    onboardingService.completeStep(user.id, stepId, metadata)
  }
  
  @PostMapping("/skip")
  fun skipOnboarding(@AuthenticationPrincipal user: User) {
    onboardingService.skipOnboarding(user.id)
  }
}
```

### Event Publishing for Analytics

```kotlin
// Spring Boot events
data class OnboardingStepCompletedEvent(
  val userId: UUID,
  val stepId: String,
  val metadata: Map<String, Any>?
) : ApplicationEvent(userId)

@Component
class OnboardingAnalyticsListener {
  
  @EventListener
  fun handleStepCompleted(event: OnboardingStepCompletedEvent) {
    analyticsService.track(
      event = "onboarding_step_completed",
      userId = event.userId,
      properties = mapOf(
        "step_id" to event.stepId,
        "metadata" to event.metadata
      )
    )
  }
}
```
