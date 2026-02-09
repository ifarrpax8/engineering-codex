# Options: Onboarding

Decision matrix for choosing onboarding patterns, libraries, tracking approaches, and analytics solutions.

## Contents

- [Onboarding Patterns](#onboarding-patterns)
- [Tour Libraries](#tour-libraries)
- [Progress Tracking](#progress-tracking)
- [Analytics Solutions](#analytics-solutions)
- [Recommendations](#recommendations)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Onboarding Patterns

### Guided Tour (Tooltip/Popover)

**Description:** Step-by-step tooltips that highlight UI elements and guide users through features.

**Strengths:**
- Highly interactive, users see exactly what to click
- Works well for feature discovery
- Can be contextual (show when user reaches feature)
- Good for complex UIs with many features

**Weaknesses:**
- Fragile if UI changes (selectors break)
- Can feel intrusive if overused
- Requires stable selectors (data-testid)
- May not work well on mobile/responsive

**Best For:**
- Feature-rich applications
- Complex workflows that need explanation
- First-time user orientation
- Highlighting hidden or non-obvious features

**Avoid When:**
- UI is frequently changing/refactored
- Mobile-first applications (tours harder on small screens)
- Users need to complete actions (tours are informational)

**Implementation:**
```typescript
// Shepherd.js example
const tour = new Shepherd.Tour({
  useModalOverlay: true,
  defaultStepOptions: {
    cancelIcon: { enabled: true }
  }
});

tour.addStep({
  id: 'create-project',
  text: 'Click here to create your first project',
  attachTo: { element: '[data-testid="create-button"]', on: 'bottom' },
  buttons: [
    { text: 'Skip', action: tour.cancel },
    { text: 'Next', action: tour.next }
  ]
});
```

### Checklist/Task List

**Description:** Visible checklist of onboarding tasks users can complete in any order.

**Strengths:**
- Clear progress indication
- Users feel accomplishment as they check items
- Flexible (can complete in any order)
- Non-intrusive (doesn't block UI)
- Works well on all screen sizes

**Weaknesses:**
- Less guided (users might not know how to complete tasks)
- Requires clear task descriptions
- May need tooltips/tours to explain how to complete items

**Best For:**
- Multi-step setup processes
- B2B SaaS org configuration
- User preferences and profile setup
- Tasks that can be completed independently

**Avoid When:**
- Tasks must be completed in specific order
- Users need step-by-step guidance
- Tasks are complex and need explanation

**Implementation:**
```vue
<!-- Vue 3 checklist -->
<template>
  <div class="onboarding-checklist">
    <div class="progress">{{ completedCount }} / {{ totalCount }}</div>
    <ul>
      <li 
        v-for="task in tasks" 
        :key="task.id"
        :class="{ completed: task.completed }"
      >
        <input 
          type="checkbox" 
          :checked="task.completed"
          @change="completeTask(task.id)"
        />
        <span>{{ task.title }}</span>
      </li>
    </ul>
  </div>
</template>
```

### Interactive Walkthrough

**Description:** Users perform actions with guidance, system validates completion.

**Strengths:**
- Most engaging (learn by doing)
- Ensures users actually complete actions
- High activation rate (users do real work)
- Memorable (hands-on learning)

**Weaknesses:**
- Most complex to implement
- Requires validation logic for each step
- Can feel restrictive if too prescriptive
- Harder to skip (defeats purpose)

**Best For:**
- Critical first actions (create first project, send first message)
- Complex workflows that need practice
- High-value features that drive activation
- When "doing" is better than "seeing"

**Avoid When:**
- Users want to explore freely
- Actions are simple and self-explanatory
- You need high skip rates (walkthroughs are harder to skip)

**Implementation:**
```typescript
// Interactive step with validation
const walkthroughStep = {
  id: 'create-project',
  instruction: 'Create a project named "My First Project"',
  validate: async () => {
    const projects = await api.get('/projects');
    return projects.some(p => p.name === 'My First Project');
  },
  onComplete: () => {
    showCelebration();
    proceedToNextStep();
  }
};
```

### Video/Demo

**Description:** Video walkthrough or animated demo showing product usage.

**Strengths:**
- Can show complex workflows visually
- Users can watch at their own pace
- Reusable (same video for all users)
- Good for explaining concepts

**Weaknesses:**
- Passive (users watch, don't do)
- May not reflect current UI (stale videos)
- Lower engagement than interactive
- Requires video production resources

**Best For:**
- Conceptual explanations
- Complex workflows that are hard to demonstrate in-app
- Marketing/sales materials
- Supplemental to other onboarding

**Avoid When:**
- Primary onboarding method (too passive)
- UI changes frequently (videos go stale)
- Users need hands-on practice

### Empty State Guidance

**Description:** Helpful empty states that guide users to take first action.

**Strengths:**
- Contextual (appears when relevant)
- Non-intrusive (doesn't block)
- Natural (feels like part of UI)
- Works on all screen sizes

**Weaknesses:**
- Only appears when state is empty
- Users might miss if they never see empty state
- Less guided (just suggests action)

**Best For:**
- First-time actions (create first item)
- Natural entry points
- Complement to other onboarding patterns
- Ongoing feature discovery

**Avoid When:**
- Primary onboarding method (too passive)
- Users need step-by-step guidance
- Complex multi-step processes

**Implementation:**
```vue
<!-- Empty state with onboarding CTA -->
<template>
  <div v-if="items.length === 0" class="empty-state">
    <Icon name="empty" size="64" />
    <h2>No {{ type }} yet</h2>
    <p>Get started by creating your first {{ type }}</p>
    <Button @click="startOnboardingStep(`create-${type}`)">
      Create {{ type }}
    </Button>
  </div>
</template>
```

## Tour Libraries

### Shepherd.js

**Description:** Framework-agnostic JavaScript library for guided tours.

**Strengths:**
- Works with Vue, React, Angular, vanilla JS
- Highly customizable
- Good documentation
- Active maintenance
- Modal overlay support

**Weaknesses:**
- Requires manual integration with each framework
- No built-in state management
- Need to handle persistence yourself

**Best For:**
- Multi-framework codebases
- Custom styling requirements
- When you need framework flexibility

**Code Example:**
```typescript
import Shepherd from 'shepherd.js';

const tour = new Shepherd.Tour({
  useModalOverlay: true,
  defaultStepOptions: {
    classes: 'shepherd-theme-custom'
  }
});
```

### vue-tour

**Description:** Vue-specific tour library built on top of Vue.

**Strengths:**
- Native Vue integration
- Vue component-based API
- Good TypeScript support
- Easy to use in Vue 3

**Weaknesses:**
- Vue-only (doesn't work with React)
- Smaller community than Shepherd.js
- Less customizable than Shepherd

**Best For:**
- Vue 3 applications
- When you want Vue-native components
- Simpler integration needs

**Code Example:**
```vue
<template>
  <v-tour name="onboarding" :steps="steps" />
</template>

<script setup>
import { VTour } from 'vue-tour';

const steps = [
  {
    target: '[data-testid="create-button"]',
    content: 'Create your first project'
  }
];
</script>
```

### react-joyride

**Description:** Most popular React tour library.

**Strengths:**
- React-native, hooks-based API
- Large community, well-maintained
- Good TypeScript support
- Lots of customization options

**Weaknesses:**
- React-only
- Can be complex for simple use cases
- Requires careful state management

**Best For:**
- React applications
- Complex tour requirements
- When you need React ecosystem integration

**Code Example:**
```tsx
import Joyride from 'react-joyride';

function OnboardingTour() {
  const [run, setRun] = useState(false);
  
  return (
    <Joyride
      steps={steps}
      run={run}
      continuous={true}
    />
  );
}
```

### Intro.js

**Description:** Older, lightweight tour library.

**Strengths:**
- Lightweight, simple API
- Framework-agnostic
- Easy to get started

**Weaknesses:**
- Less modern (older codebase)
- Less customizable
- Smaller community
- Not as actively maintained

**Best For:**
- Simple tour needs
- Legacy applications
- When you need minimal dependencies

**Avoid When:**
- Need modern features
- Complex customization requirements
- Long-term maintenance is important

## Progress Tracking

### Database-Backed (Custom)

**Description:** Store onboarding progress in your application database.

**Strengths:**
- Most reliable (persists across devices)
- Can query and analyze progress
- Works for multi-device users
- Can integrate with user management

**Weaknesses:**
- Requires backend implementation
- More complex than localStorage
- Need to handle sync between frontend/backend

**Best For:**
- Production applications
- Multi-device support needed
- When you need analytics on progress
- B2B SaaS with user management

**Implementation:**
```sql
CREATE TABLE user_onboarding (
  user_id UUID PRIMARY KEY,
  current_step VARCHAR(100),
  status VARCHAR(20),
  completed_steps JSONB,
  updated_at TIMESTAMP
);
```

### localStorage (Simple)

**Description:** Store progress in browser localStorage.

**Strengths:**
- Simple, no backend needed
- Fast (no API calls)
- Works offline
- Easy to implement

**Weaknesses:**
- Device-specific (doesn't sync)
- Can be cleared by user
- Not suitable for multi-device
- Limited analytics capabilities

**Best For:**
- Prototypes and MVPs
- Single-device applications
- When backend isn't available
- Simple onboarding flows

**Implementation:**
```typescript
// Save progress
localStorage.setItem('onboarding', JSON.stringify({
  currentStep: 'profile-setup',
  completedSteps: ['welcome']
}));

// Load progress
const progress = JSON.parse(localStorage.getItem('onboarding') || '{}');
```

### Feature Flag Service (LaunchDarkly/Custom)

**Description:** Use feature flag service to track onboarding variants and progress.

**Strengths:**
- Integrates with A/B testing
- Can control rollout
- Tracks variants automatically
- Good for experimentation

**Weaknesses:**
- Not primary purpose (flags are for features)
- May have limitations for complex progress tracking
- Additional service dependency

**Best For:**
- When you're already using feature flags
- A/B testing onboarding variants
- Graduated rollout needs
- Experimentation-heavy teams

**Implementation:**
```typescript
// LaunchDarkly
const client = LaunchDarkly.initialize('client-id', user);

client.on('ready', () => {
  const onboardingVariant = client.variation('onboarding-variant', 'default');
  const onboardingStatus = client.variation('onboarding-status', 'new');
});
```

## Analytics Solutions

### Custom Events (Spring Boot + Frontend)

**Description:** Build custom analytics tracking in your backend and frontend.

**Strengths:**
- Full control over data
- No third-party dependencies
- Can integrate with existing systems
- Privacy-friendly (your data)

**Weaknesses:**
- Requires building infrastructure
- Need to handle scale yourself
- More development time
- Need to build dashboards

**Best For:**
- Privacy-sensitive applications
- When you have analytics infrastructure
- Custom data requirements
- Enterprise/B2B SaaS

**Implementation:**
```kotlin
// Spring Boot custom tracking
@Service
class OnboardingAnalyticsService {
  
  fun trackStepCompleted(userId: UUID, stepId: String) {
    analyticsRepository.save(
      AnalyticsEvent(
        userId = userId,
        event = "onboarding_step_completed",
        properties = mapOf("step_id" to stepId),
        timestamp = Instant.now()
      )
    )
  }
}
```

### Segment/Mixpanel

**Description:** Third-party analytics platforms with rich features.

**Strengths:**
- Rich dashboards and analysis
- Funnel analysis built-in
- Good documentation
- Handles scale

**Weaknesses:**
- Third-party dependency
- Cost (can be expensive)
- Data leaves your system
- May be blocked by ad blockers

**Best For:**
- When you need rich analytics quickly
- Product-led growth teams
- When you don't want to build analytics
- Consumer applications

**Implementation:**
```typescript
// Segment
analytics.track('onboarding_step_completed', {
  step_id: 'profile-setup',
  user_id: user.id
});
```

### PostHog

**Description:** Open-source, self-hostable analytics platform.

**Strengths:**
- Can self-host (privacy)
- Open source
- Good feature set
- Reasonable pricing if SaaS

**Weaknesses:**
- Self-hosting requires infrastructure
- Smaller community than Segment
- Still third-party if using SaaS

**Best For:**
- Privacy-conscious teams
- When you want open source
- Self-hosting capable teams
- Balance of features and control

## Recommendations

### Default Stack Recommendation

**For Vue 3 + Spring Boot:**
- **Pattern:** Checklist + Contextual Tooltips (hybrid)
- **Library:** Shepherd.js (framework-agnostic, works with Vue)
- **Progress Tracking:** Database-backed (Spring Boot service)
- **Analytics:** Custom events (Spring Boot) + PostHog (if needed)

**For React + Spring Boot:**
- **Pattern:** Checklist + Guided Tour
- **Library:** react-joyride (React-native)
- **Progress Tracking:** Database-backed (Spring Boot service)
- **Analytics:** Custom events + Segment (for dashboards)

### When to Choose What

**Choose Guided Tour when:**
- Complex UI with many features
- Users need to see exactly where things are
- Feature discovery is primary goal

**Choose Checklist when:**
- Multi-step setup process
- Tasks can be completed independently
- Need clear progress indication

**Choose Interactive Walkthrough when:**
- Critical first actions
- High activation value
- Users need hands-on practice

**Choose Database-Backed Tracking when:**
- Production application
- Multi-device support needed
- Need analytics on progress

**Choose Custom Analytics when:**
- Privacy requirements
- Existing analytics infrastructure
- Custom data needs

## Synergies

**Checklist + Empty States:** Checklist shows what to do, empty states provide entry points.

**Guided Tour + Contextual Tips:** Tour for initial orientation, tips for ongoing discovery.

**Database Tracking + Custom Analytics:** Track progress in DB, send events to analytics for analysis.

**Feature Flags + A/B Testing:** Use flags to control variants, measure with analytics.

## Evolution Triggers

**Move from localStorage to Database when:**
- Users report losing progress
- Need multi-device support
- Want to analyze onboarding data
- Application is production-ready

**Move from Simple Tour to Interactive Walkthrough when:**
- Low activation rate (users complete tour but don't use product)
- Need to ensure users complete real actions
- Activation is critical business metric

**Add Contextual Tips when:**
- Users complete initial onboarding but don't discover features
- Feature discovery is important
- Want to reduce support tickets about "where is X?"

**Add A/B Testing when:**
- Onboarding completion/activation rates plateau
- Want to optimize onboarding flow
- Have enough users for statistical significance

**Move from Third-Party to Custom Analytics when:**
- Privacy/compliance requirements
- Cost becomes prohibitive
- Need custom data/analysis
- Want full control over data
