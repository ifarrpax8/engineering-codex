# Best Practices: Onboarding

Proven patterns and principles for building effective onboarding experiences across different tech stacks.

## Contents

- [Let Users Skip Onboarding](#let-users-skip-onboarding)
- [Show Value Before Asking for Effort](#show-value-before-asking-for-effort)
- [Checklist Pattern](#checklist-pattern)
- [Contextual Over Sequential](#contextual-over-sequential)
- [Celebrate Milestones](#celebrate-milestones)
- [Don't Block Core Functionality](#dont-block-core-functionality)
- [Personalize by Role/Use-Case](#personalize-by-roleuse-case)
- [Stack-Specific Implementations](#stack-specific-implementations)
- [Accessibility](#accessibility)
- [Empty States as Onboarding](#empty-states-as-onboarding)

## Let Users Skip Onboarding

**Always provide an escape hatch.** If onboarding is valuable, users will complete it. Forcing them creates resentment and increases abandonment.

### Implementation Pattern

```vue
<!-- Vue 3: Always show skip option -->
<template>
  <div class="onboarding-modal">
    <button 
      data-testid="onboarding-skip"
      class="skip-button"
      @click="handleSkip"
    >
      Skip for now
    </button>
    <!-- Onboarding content -->
  </div>
</template>

<script setup lang="ts">
const handleSkip = async () => {
  await onboardingService.skipOnboarding();
  emit('skipped');
  // Don't show again unless user explicitly requests it
};
</script>
```

```tsx
// React: Skip button always accessible
function OnboardingModal({ onComplete, onSkip }) {
  return (
    <div className="onboarding-modal">
      <button 
        data-testid="onboarding-skip"
        className="skip-button"
        onClick={onSkip}
        aria-label="Skip onboarding"
      >
        Skip for now
      </button>
      {/* Onboarding content */}
    </div>
  );
}
```

**Key principles:**
- Skip button should be visible but not prominent (don't make it the primary action)
- Skipping should be a one-click action (no "Are you sure?" modals)
- After skipping, provide a way to access onboarding later (settings menu, help center)
- Core functionality must work perfectly even if onboarding is skipped

## Show Value Before Asking for Effort

**Demonstrate before configuring.** Let users experience the product before asking them to set up complex configurations.

### Anti-Pattern

```
Signup → Profile Setup → Company Details → Billing → Integrations → 
SSO Config → Team Invites → Finally see the product
```

Users abandon after 3-4 steps of setup before seeing value.

### Better Pattern

```
Signup → Quick Demo/Preview → "Try it now" → First action → 
Then: "Want to customize? Here's how..."
```

**Example: Project Management Tool**

```typescript
// Show value first
1. Signup (email + password)
2. Immediately show: "Here's a sample project to explore"
3. User interacts with sample project
4. Then: "Create your own project" (activation)
5. Later: "Invite your team" (progressive)

// Instead of:
1. Signup
2. Company name
3. Team size
4. Industry
5. Use case
6. Finally see the product
```

## Checklist Pattern

A checklist provides visible progress and allows users to complete steps in any order (where possible).

### Visual Progress Indicator

```vue
<!-- Vue 3: Checklist with progress -->
<template>
  <div class="onboarding-checklist">
    <h2>Get Started</h2>
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        :style="{ width: `${completionPercentage}%` }"
      />
    </div>
    <ul class="checklist">
      <li 
        v-for="step in steps" 
        :key="step.id"
        :class="{ completed: step.completed }"
      >
        <Icon :name="step.completed ? 'check' : 'circle'" />
        <span>{{ step.title }}</span>
        <button 
          v-if="!step.completed"
          @click="completeStep(step.id)"
        >
          Start
        </button>
      </li>
    </ul>
  </div>
</template>
```

### Unordered Completion

```typescript
// Steps can be completed in any order
const onboardingChecklist = [
  { id: 'profile', title: 'Complete your profile', order: null },
  { id: 'first-project', title: 'Create your first project', order: null },
  { id: 'invite-team', title: 'Invite a team member', order: null }
];

// Mark complete when all done
const allCompleted = checklist.every(step => step.completed);
if (allCompleted) {
  completeOnboarding();
}
```

**Benefits:**
- Users feel progress (visual feedback)
- Less pressure (can skip around)
- Natural completion (finish when ready)

## Contextual Over Sequential

**Show tips when users reach relevant features, not all upfront.** Contextual guidance feels helpful, not intrusive.

### Sequential (Anti-Pattern)

```
Day 1: Show 20 tooltips about features user hasn't seen yet
Day 2: User forgets everything
```

### Contextual (Better)

```
User navigates to Projects page → Show tooltip about creating projects
User clicks Settings → Show tip about key settings
User views Dashboard → Show tip about customizing dashboard
```

**Implementation:**

```typescript
// Vue 3: Contextual tooltip system
export function useContextualTips() {
  const showTip = (feature: string) => {
    const hasSeenTip = localStorage.getItem(`tip-seen-${feature}`);
    if (!hasSeenTip && isFirstTimeUser()) {
      showTooltip(feature);
      markTipAsSeen(feature);
    }
  };
  
  return { showTip };
}

// Usage in component
const { showTip } = useContextualTips();

onMounted(() => {
  // Show tip when user first sees this feature
  showTip('project-creation');
});
```

```tsx
// React: Contextual help hook
function useContextualHelp(feature: string) {
  const [showHelp, setShowHelp] = useState(false);
  
  useEffect(() => {
    const hasSeenHelp = localStorage.getItem(`help-seen-${feature}`);
    if (!hasSeenHelp && isNewUser()) {
      setShowHelp(true);
    }
  }, [feature]);
  
  const dismissHelp = () => {
    setShowHelp(false);
    localStorage.setItem(`help-seen-${feature}`, 'true');
  };
  
  return { showHelp, dismissHelp };
}
```

## Celebrate Milestones

**Micro-interactions on completion create positive reinforcement.** Progress indicators and completion animations make users feel accomplished.

### Progress Indicators

```vue
<!-- Vue 3: Animated progress -->
<template>
  <div class="onboarding-progress">
    <div class="steps">
      <div 
        v-for="(step, index) in steps"
        :key="step.id"
        class="step"
        :class="{ 
          completed: step.completed,
          active: step.id === currentStep 
        }"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-label">{{ step.title }}</div>
      </div>
    </div>
    <div class="progress-bar">
      <div 
        class="progress-fill"
        :style="{ width: `${(completedSteps / totalSteps) * 100}%` }"
      />
    </div>
  </div>
</template>
```

### Completion Celebrations

```typescript
// Celebrate step completion
function celebrateStepCompletion(stepId: string) {
  // Show confetti animation
  showConfetti();
  
  // Play success sound (optional, user preference)
  playSound('success');
  
  // Show completion message
  showToast({
    message: 'Great job! 🎉',
    type: 'success'
  });
  
  // Track for analytics
  trackEvent('onboarding_step_celebrated', { stepId });
}
```

**Balance:** Celebrate without being annoying. Subtle animations > loud confetti on every step.

## Don't Block Core Functionality

**Onboarding should enhance, not restrict.** Users should be able to use the product even if they skip onboarding.

### Anti-Pattern

```typescript
// BAD: Blocking core features
if (!onboardingCompleted) {
  return <OnboardingModal blocking={true} />;
}
// User can't access anything until onboarding is done
```

### Better Pattern

```typescript
// GOOD: Non-blocking guidance
if (!onboardingCompleted && isFirstVisit) {
  return (
    <>
      <Dashboard />
      <OnboardingTooltip 
        target="create-project-button"
        message="Create your first project"
        nonBlocking={true}
      />
    </>
  );
}
```

**Implementation:**

```vue
<!-- Vue 3: Non-blocking onboarding -->
<template>
  <div>
    <!-- Core app functionality always available -->
    <Dashboard />
    
    <!-- Onboarding overlays, doesn't block -->
    <OnboardingTour 
      v-if="showOnboarding"
      :steps="onboardingSteps"
      :nonBlocking="true"
      @skip="handleSkip"
    />
  </div>
</template>
```

## Personalize by Role/Use-Case

**Admin sees org setup, user sees feature tour.** Detect user context and adapt onboarding accordingly.

### Role Detection

```typescript
// Spring Boot: Determine onboarding path
@Service
public class OnboardingPathService {
  
  public List<OnboardingStep> getOnboardingSteps(User user) {
    List<OnboardingStep> steps = new ArrayList<>();
    
    if (user.getRole() == Role.ADMIN) {
      steps.add(new OnboardingStep("org-setup", "Set up your organization"));
      steps.add(new OnboardingStep("team-invite", "Invite your team"));
      steps.add(new OnboardingStep("sso-config", "Configure SSO"));
    } else {
      steps.add(new OnboardingStep("welcome", "Welcome to the team"));
      steps.add(new OnboardingStep("feature-tour", "Explore key features"));
      steps.add(new OnboardingStep("first-action", "Complete your first task"));
    }
    
    return steps;
  }
}
```

### Use-Case Personalization

```typescript
// Detect use case from signup flow
const useCase = detectUseCase(user.signupData);

const onboardingSteps = {
  'project-management': [
    'create-project',
    'add-tasks',
    'invite-team'
  ],
  'analytics': [
    'connect-data-source',
    'create-dashboard',
    'set-up-alerts'
  ],
  'crm': [
    'import-contacts',
    'create-pipeline',
    'set-up-automations'
  ]
}[useCase];
```

## Stack-Specific Implementations

### Vue 3

**Tour Libraries:**
- `vue-tour`: Vue-specific tour library
- `Shepherd.js`: Framework-agnostic, works with Vue

**State Management (Pinia):**

```typescript
// stores/onboarding.ts
import { defineStore } from 'pinia';

export const useOnboardingStore = defineStore('onboarding', {
  state: () => ({
    status: 'new' as OnboardingStatus,
    currentStep: null as string | null,
    completedSteps: [] as string[],
    skipped: false
  }),
  
  actions: {
    async startOnboarding() {
      this.status = 'in-progress';
      this.currentStep = 'welcome';
      await this.persistState();
    },
    
    async completeStep(stepId: string) {
      this.completedSteps.push(stepId);
      this.currentStep = this.getNextStep();
      await this.persistState();
    },
    
    async persistState() {
      localStorage.setItem('onboarding', JSON.stringify(this.$state));
      // Also sync to backend
      await api.post('/onboarding/state', this.$state);
    }
  }
});
```

**Shepherd.js Integration:**

```typescript
import Shepherd from 'shepherd.js';

export function createOnboardingTour() {
  const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: { enabled: true },
      classes: 'shepherd-theme-custom'
    }
  });
  
  tour.addStep({
    id: 'welcome',
    text: 'Welcome! Let\'s get you started.',
    attachTo: { element: '.dashboard', on: 'bottom' },
    buttons: [
      { text: 'Skip', action: tour.cancel },
      { text: 'Next', action: tour.next }
    ]
  });
  
  return tour;
}
```

### React

**Tour Libraries:**
- `react-joyride`: Most popular React tour library
- `Shepherd.js`: Works with React via wrapper

**Context for Onboarding State:**

```tsx
// contexts/OnboardingContext.tsx
const OnboardingContext = createContext<OnboardingContextType | null>(null);

export function OnboardingProvider({ children }) {
  const [state, setState] = useState<OnboardingState>({
    status: 'new',
    currentStep: null,
    completedSteps: []
  });
  
  const completeStep = async (stepId: string) => {
    setState(prev => ({
      ...prev,
      completedSteps: [...prev.completedSteps, stepId]
    }));
    await api.post(`/onboarding/steps/${stepId}/complete`);
  };
  
  return (
    <OnboardingContext.Provider value={{ state, completeStep }}>
      {children}
    </OnboardingContext.Provider>
  );
}
```

**React Joyride Example:**

```tsx
import Joyride from 'react-joyride';

const steps = [
  {
    target: '.create-project-button',
    content: 'Click here to create your first project.',
    placement: 'bottom'
  },
  {
    target: '.project-list',
    content: 'Your projects will appear here.',
    placement: 'top'
  }
];

function OnboardingTour() {
  const [run, setRun] = useState(false);
  
  return (
    <Joyride
      steps={steps}
      run={run}
      continuous={true}
      showProgress={true}
      callback={(data) => {
        if (data.status === 'finished' || data.status === 'skipped') {
          setRun(false);
        }
      }}
    />
  );
}
```

### Spring Boot

**Onboarding Service:**

```kotlin
@Service
class OnboardingService(
  private val onboardingRepository: OnboardingRepository,
  private val eventPublisher: ApplicationEventPublisher
) {
  
  fun getOnboardingSteps(user: User): List<OnboardingStep> {
    return when (user.role) {
      Role.ADMIN -> listOf(
        OnboardingStep("org-setup", "Set up your organization"),
        OnboardingStep("team-invite", "Invite your team")
      )
      Role.USER -> listOf(
        OnboardingStep("welcome", "Welcome to the team"),
        OnboardingStep("feature-tour", "Explore features")
      )
    }
  }
  
  @Transactional
  fun completeStep(userId: UUID, stepId: String) {
    val onboarding = onboardingRepository.findByUserId(userId)
      ?: throw OnboardingNotFoundException()
    
    onboarding.completeStep(stepId)
    onboardingRepository.save(onboarding)
    
    eventPublisher.publishEvent(
      OnboardingStepCompletedEvent(userId, stepId)
    )
  }
}
```

**Event-Driven Step Completion:**

```kotlin
@Component
class OnboardingEventListener {
  
  @EventListener
  fun handleProjectCreated(event: ProjectCreatedEvent) {
    val user = event.user
    if (isNewUser(user)) {
      onboardingService.completeStep(user.id, "first-project")
    }
  }
  
  @EventListener
  fun handleTeamMemberInvited(event: TeamMemberInvitedEvent) {
    val user = event.user
    if (user.role == Role.ADMIN) {
      onboardingService.completeStep(user.id, "team-invite")
    }
  }
}
```

## Accessibility

**Guided tours must be keyboard navigable.** Tooltips shouldn't trap focus. Screen readers must announce step changes.

### Keyboard Navigation

```typescript
// Ensure tours are keyboard accessible
const tour = new Shepherd.Tour({
  keyboardNavigation: true, // Enable keyboard nav
  useModalOverlay: true
});

// Handle keyboard events
tour.on('complete', () => {
  // Return focus to main content
  document.querySelector('.main-content')?.focus();
});
```

### Screen Reader Announcements

```vue
<!-- Vue 3: ARIA live region for announcements -->
<template>
  <div 
    aria-live="polite"
    aria-atomic="true"
    class="sr-only"
  >
    {{ announcement }}
  </div>
</template>

<script setup lang="ts">
const announcement = ref('');

watch(() => onboardingStore.currentStep, (step) => {
  announcement.value = `Onboarding step ${step.title}. ${step.description}`;
});
</script>
```

### Focus Management

```typescript
// Don't trap focus in tooltips
function showTooltip(element: HTMLElement, message: string) {
  const tooltip = createTooltip(message);
  
  // Position tooltip
  positionTooltip(tooltip, element);
  
  // Don't move focus to tooltip (let user tab naturally)
  // Tooltip should be in DOM but not in tab order
  tooltip.setAttribute('tabindex', '-1');
  
  // Announce to screen readers
  announceToScreenReader(message);
}
```

## Empty States as Onboarding

**Every empty list/dashboard is a missed onboarding opportunity.** Empty states should guide action, not just inform.

### Good Empty State

```vue
<!-- Vue 3: Actionable empty state -->
<template>
  <div class="empty-state">
    <Icon name="project" size="64" class="empty-icon" />
    <h2>No projects yet</h2>
    <p>Create your first project to get started with project management</p>
    <Button 
      data-testid="create-project-cta"
      @click="startOnboardingStep('create-project')"
      primary
    >
      Create Your First Project
    </Button>
    <a 
      href="#"
      @click="skip"
      class="skip-link"
    >
      I'll do this later
    </a>
  </div>
</template>
```

### Empty State Integration

```typescript
// Show onboarding when user sees empty state
function EmptyState({ type, onAction }) {
  const { showOnboardingTip } = useOnboarding();
  
  useEffect(() => {
    if (isFirstTimeUser() && isEmpty(type)) {
      // Show contextual tip after a brief delay
      setTimeout(() => {
        showOnboardingTip(type, {
          message: `Get started by creating your first ${type}`,
          cta: onAction
        });
      }, 500);
    }
  }, [type]);
  
  return (
    <div className="empty-state">
      <EmptyStateIllustration type={type} />
      <h2>No {type} yet</h2>
      <Button onClick={onAction}>
        Create Your First {capitalize(type)}
      </Button>
    </div>
  );
}
```

**Key principles:**
- Empty states should have clear CTAs
- CTAs should trigger onboarding flows or direct actions
- Provide skip option ("I'll do this later")
- Don't show empty state guidance if user has data (check first)
