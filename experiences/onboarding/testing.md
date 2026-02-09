# Testing: Onboarding

Comprehensive testing strategies for onboarding flows, from end-to-end user journeys to analytics event verification.

## Contents

- [Onboarding Flow E2E Testing](#onboarding-flow-e2e-testing)
- [Skip/Dismiss Testing](#skipdismiss-testing)
- [Conditional Step Testing](#conditional-step-testing)
- [Resume Testing](#resume-testing)
- [Empty State Testing](#empty-state-testing)
- [Analytics Event Testing](#analytics-event-testing)
- [A/B Variant Testing](#ab-variant-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Onboarding Flow E2E Testing

Test the complete onboarding journey from signup to activation, verifying each step works correctly.

### Playwright Example

```typescript
import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow', () => {
  test('complete onboarding from signup to activation', async ({ page }) => {
    // Sign up
    await page.goto('/signup');
    await page.fill('[data-testid="email"]', 'newuser@example.com');
    await page.fill('[data-testid="password"]', 'SecurePass123!');
    await page.click('[data-testid="signup-button"]');
    
    // Verify onboarding modal appears
    await expect(page.locator('[data-testid="onboarding-welcome"]')).toBeVisible();
    
    // Complete welcome step
    await page.click('[data-testid="onboarding-next"]');
    
    // Verify profile setup step
    await expect(page.locator('[data-testid="onboarding-profile"]')).toBeVisible();
    await page.fill('[data-testid="profile-name"]', 'Test User');
    await page.click('[data-testid="onboarding-next"]');
    
    // Verify first project creation step
    await expect(page.locator('[data-testid="onboarding-create-project"]')).toBeVisible();
    await page.fill('[data-testid="project-name"]', 'My First Project');
    await page.click('[data-testid="create-project-button"]');
    
    // Verify onboarding completion
    await expect(page.locator('[data-testid="onboarding-complete"]')).toBeVisible();
    await page.click('[data-testid="onboarding-finish"]');
    
    // Verify user lands on dashboard (activated)
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="project-list"]')).toContainText('My First Project');
  });
});
```

### Step-by-Step Verification

Verify each step transitions correctly and persists state:

```typescript
test('onboarding steps persist and transition correctly', async ({ page }) => {
  await page.goto('/signup');
  // ... signup flow ...
  
  // Step 1: Welcome
  const step1 = page.locator('[data-testid="onboarding-step-1"]');
  await expect(step1).toBeVisible();
  await page.click('[data-testid="onboarding-next"]');
  
  // Step 2: Profile
  const step2 = page.locator('[data-testid="onboarding-step-2"]');
  await expect(step2).toBeVisible();
  await expect(step1).not.toBeVisible();
  
  // Verify progress indicator updates
  const progress = page.locator('[data-testid="onboarding-progress"]');
  await expect(progress).toHaveText('2 of 5');
});
```

## Skip/Dismiss Testing

Critical: Users must be able to skip onboarding, and the app must work correctly if they do.

```typescript
test('user can skip onboarding at any step', async ({ page }) => {
  await page.goto('/signup');
  // ... signup ...
  
  // Skip from welcome step
  await page.click('[data-testid="onboarding-skip"]');
  
  // Verify skip confirmation (if applicable)
  await page.click('[data-testid="confirm-skip"]');
  
  // Verify user lands on dashboard
  await expect(page).toHaveURL('/dashboard');
  
  // Verify core functionality works without onboarding
  await page.click('[data-testid="create-project"]');
  await page.fill('[data-testid="project-name"]', 'Test Project');
  await page.click('[data-testid="save"]');
  
  // Project should be created successfully
  await expect(page.locator('[data-testid="project-list"]')).toContainText('Test Project');
});

test('skip button is always visible', async ({ page }) => {
  const steps = ['welcome', 'profile', 'create-project', 'invite-team'];
  
  for (const step of steps) {
    await page.goto(`/onboarding?step=${step}`);
    await expect(page.locator('[data-testid="onboarding-skip"]')).toBeVisible();
  }
});
```

### Dismiss Testing for Tooltips/Tours

```typescript
test('user can dismiss contextual tooltips', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Tooltip should appear for first-time user
  const tooltip = page.locator('[data-testid="contextual-tooltip"]');
  await expect(tooltip).toBeVisible();
  
  // Dismiss tooltip
  await page.click('[data-testid="tooltip-dismiss"]');
  
  // Verify tooltip doesn't reappear on refresh
  await page.reload();
  await expect(tooltip).not.toBeVisible();
  
  // Verify tooltip doesn't appear again (persisted dismissal)
  await page.goto('/dashboard');
  await expect(tooltip).not.toBeVisible();
});
```

## Conditional Step Testing

Different user roles, plans, and attributes should see different onboarding paths.

```typescript
test.describe('Role-based onboarding', () => {
  test('admin sees org setup steps', async ({ page }) => {
    await signUpAsAdmin(page);
    
    await expect(page.locator('[data-testid="onboarding-org-setup"]')).toBeVisible();
    await expect(page.locator('[data-testid="onboarding-team-invite"]')).toBeVisible();
    await expect(page.locator('[data-testid="onboarding-sso-config"]')).toBeVisible();
  });
  
  test('regular user does not see org setup steps', async ({ page }) => {
    await signUpAsUser(page);
    
    await expect(page.locator('[data-testid="onboarding-org-setup"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="onboarding-feature-tour"]')).toBeVisible();
  });
  
  test('enterprise plan users see advanced setup', async ({ page }) => {
    await signUpWithPlan(page, 'enterprise');
    
    await expect(page.locator('[data-testid="onboarding-sso-setup"]')).toBeVisible();
    await expect(page.locator('[data-testid="onboarding-audit-logs"]')).toBeVisible();
  });
});
```

### Conditional Step Logic Testing

```typescript
test('steps appear based on user attributes', async ({ page, request }) => {
  // Create user with specific attributes
  const user = await createTestUser(request, {
    role: 'admin',
    plan: 'enterprise',
    hasExistingOrg: false
  });
  
  await loginAs(page, user);
  
  // Verify conditional steps appear
  const steps = await page.locator('[data-testid^="onboarding-step"]').all();
  const stepIds = await Promise.all(steps.map(s => s.getAttribute('data-testid')));
  
  expect(stepIds).toContain('onboarding-step-org-setup');
  expect(stepIds).toContain('onboarding-step-sso-setup');
  expect(stepIds).not.toContain('onboarding-step-join-org');
});
```

## Resume Testing

Users should be able to close their browser mid-onboarding and resume where they left off.

```typescript
test('onboarding progress persists across sessions', async ({ page, context }) => {
  await page.goto('/signup');
  // ... signup ...
  
  // Complete first two steps
  await page.click('[data-testid="onboarding-next"]'); // Welcome
  await page.fill('[data-testid="profile-name"]', 'Test User');
  await page.click('[data-testid="onboarding-next"]'); // Profile
  
  // Verify we're on step 3
  await expect(page.locator('[data-testid="onboarding-step-3"]')).toBeVisible();
  
  // Close browser (simulate user leaving)
  await context.close();
  
  // Open new browser session
  const newContext = await browser.newContext();
  const newPage = await newContext.newPage();
  
  // Login as same user
  await loginAs(newPage, testUser);
  
  // Verify onboarding resumes at step 3
  await expect(newPage.locator('[data-testid="onboarding-step-3"]')).toBeVisible();
  await expect(newPage.locator('[data-testid="onboarding-progress"]')).toHaveText('3 of 5');
  
  // Verify previous steps are marked complete
  await expect(newPage.locator('[data-testid="step-1-complete"]')).toBeVisible();
  await expect(newPage.locator('[data-testid="step-2-complete"]')).toBeVisible();
});
```

### Database State Verification

```typescript
test('onboarding state persists in database', async ({ page, request }) => {
  const user = await createTestUser(request);
  await loginAs(page, user);
  
  // Start onboarding
  await page.click('[data-testid="start-onboarding"]');
  await page.click('[data-testid="onboarding-next"]'); // Complete step 1
  
  // Verify database state
  const onboardingStatus = await request.get(`/api/onboarding/status`, {
    headers: { Authorization: `Bearer ${user.token}` }
  });
  
  expect(onboardingStatus.json()).toMatchObject({
    status: 'in-progress',
    currentStep: 'step-2',
    completedSteps: ['step-1']
  });
});
```

## Empty State Testing

Verify that helpful empty states appear for new users and guide them to action.

```typescript
test('empty states guide new users', async ({ page }) => {
  await signUpAsNewUser(page);
  
  // Navigate to projects page (empty)
  await page.goto('/projects');
  
  // Verify empty state appears
  const emptyState = page.locator('[data-testid="empty-state-projects"]');
  await expect(emptyState).toBeVisible();
  await expect(emptyState).toContainText('No projects yet');
  await expect(emptyState).toContainText('Create your first project');
  
  // Verify CTA button is present
  const createButton = emptyState.locator('[data-testid="create-project-cta"]');
  await expect(createButton).toBeVisible();
  
  // Click CTA and verify it starts onboarding or creates project
  await createButton.click();
  await expect(page.locator('[data-testid="create-project-modal"]')).toBeVisible();
});
```

### Empty State Onboarding Integration

```typescript
test('empty states trigger contextual onboarding', async ({ page }) => {
  await signUpAsNewUser(page);
  
  // Empty dashboard should show onboarding prompt
  await page.goto('/dashboard');
  await expect(page.locator('[data-testid="onboarding-empty-dashboard"]')).toBeVisible();
  
  // Empty team list should show invite flow
  await page.goto('/team');
  await expect(page.locator('[data-testid="onboarding-empty-team"]')).toBeVisible();
  await expect(page.locator('[data-testid="invite-team-cta"]')).toBeVisible();
});
```

## Analytics Event Testing

Verify that tracking events fire correctly at each onboarding step.

```typescript
test('onboarding events are tracked correctly', async ({ page }) => {
  // Mock analytics service
  const analyticsEvents: any[] = [];
  await page.route('**/api/analytics/track', route => {
    analyticsEvents.push(route.request().postDataJSON());
    route.fulfill({ status: 200 });
  });
  
  await signUpAsNewUser(page);
  
  // Start onboarding
  await page.click('[data-testid="start-onboarding"]');
  
  // Verify onboarding_started event
  const startedEvent = analyticsEvents.find(e => e.event === 'onboarding_started');
  expect(startedEvent).toBeDefined();
  expect(startedEvent.properties).toMatchObject({
    variant: expect.any(String),
    user_id: expect.any(String)
  });
  
  // Complete a step
  await page.click('[data-testid="onboarding-next"]');
  
  // Verify step_completed event
  const stepEvent = analyticsEvents.find(e => e.event === 'onboarding_step_completed');
  expect(stepEvent).toBeDefined();
  expect(stepEvent.properties).toMatchObject({
    step_id: 'welcome',
    step_number: 1
  });
});
```

### Funnel Drop-off Tracking

```typescript
test('drop-off events are tracked when user abandons', async ({ page }) => {
  const analyticsEvents: any[] = [];
  await page.route('**/api/analytics/track', route => {
    analyticsEvents.push(route.request().postDataJSON());
    route.fulfill({ status: 200 });
  });
  
  await signUpAsNewUser(page);
  await page.click('[data-testid="start-onboarding"]');
  await page.click('[data-testid="onboarding-next"]'); // Complete step 1
  
  // User closes modal (abandons)
  await page.click('[data-testid="modal-close"]');
  
  // Verify abandonment event
  const abandonEvent = analyticsEvents.find(e => e.event === 'onboarding_step_abandoned');
  expect(abandonEvent).toBeDefined();
  expect(abandonEvent.properties).toMatchObject({
    step_id: 'profile-setup',
    time_spent: expect.any(Number)
  });
});
```

## A/B Variant Testing

Verify that different onboarding variants produce the correct experiences.

```typescript
test.describe('A/B variant testing', () => {
  test('variant A shows shorter onboarding', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('onboarding-variant', 'short');
    });
    
    await signUpAsNewUser(page);
    
    const steps = await page.locator('[data-testid^="onboarding-step"]').count();
    expect(steps).toBe(3); // Short variant has 3 steps
  });
  
  test('variant B shows detailed onboarding', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('onboarding-variant', 'detailed');
    });
    
    await signUpAsNewUser(page);
    
    const steps = await page.locator('[data-testid^="onboarding-step"]').count();
    expect(steps).toBe(7); // Detailed variant has 7 steps
  });
  
  test('variant assignment is consistent', async ({ page }) => {
    // User should get same variant on refresh
    await page.addInitScript(() => {
      window.localStorage.setItem('onboarding-variant', 'short');
    });
    
    await signUpAsNewUser(page);
    const variant1 = await page.locator('[data-testid="onboarding-variant"]').textContent();
    
    await page.reload();
    const variant2 = await page.locator('[data-testid="onboarding-variant"]').textContent();
    
    expect(variant1).toBe(variant2);
  });
});
```

## QA and Test Engineer Perspective

### Test Coverage Checklist

**Onboarding Flow Coverage:**
- [ ] Complete flow from signup to activation works end-to-end
- [ ] Each step transitions correctly to the next
- [ ] Progress indicators update accurately
- [ ] Users can navigate backward through steps (if supported)
- [ ] Onboarding completes successfully and user reaches activated state

**Skip/Dismiss Functionality:**
- [ ] Skip button is visible on every step
- [ ] Users can skip at any point
- [ ] Skipped onboarding doesn't break core functionality
- [ ] Tooltips and tours can be dismissed
- [ ] Dismissed tooltips don't reappear

**Conditional Logic:**
- [ ] Admin users see org setup steps
- [ ] Regular users don't see admin-only steps
- [ ] Enterprise plan users see advanced features
- [ ] Steps appear/disappear based on user attributes correctly
- [ ] Conditional step logic is testable and deterministic

**Persistence and Resume:**
- [ ] Onboarding progress persists across browser sessions
- [ ] Users resume at correct step after refresh
- [ ] Completed steps remain marked complete
- [ ] Progress persists across devices (if multi-device supported)
- [ ] Database state matches UI state

**Empty States:**
- [ ] Empty states appear for new users
- [ ] Empty states include clear CTAs
- [ ] Empty state CTAs trigger correct actions
- [ ] Empty states integrate with onboarding flows
- [ ] Empty states don't appear for users with data

**Analytics and Tracking:**
- [ ] All onboarding events fire correctly
- [ ] Step completion events include correct metadata
- [ ] Drop-off events track abandonment accurately
- [ ] Funnel analysis data is accurate
- [ ] Events work even with ad blockers (graceful degradation)

**A/B Testing:**
- [ ] Variants are assigned consistently
- [ ] Different variants produce correct experiences
- [ ] Variant assignment persists across sessions
- [ ] Analytics track which variant users received
- [ ] Variant switching doesn't break existing users

### Test Data Management

**User Creation:**
```typescript
// Helper to create test users with specific attributes
async function createOnboardingTestUser(request: APIRequestContext, overrides = {}) {
  return await request.post('/api/test/users', {
    data: {
      email: `test-${Date.now()}@example.com`,
      role: 'user',
      plan: 'free',
      onboardingStatus: 'new',
      ...overrides
    }
  });
}
```

**Onboarding State Reset:**
```typescript
// Reset onboarding state between tests
async function resetOnboardingState(request: APIRequestContext, userId: string) {
  await request.delete(`/api/test/users/${userId}/onboarding`);
}
```

### Regression Testing

**Critical Paths to Test on Every Release:**
1. New user signup → onboarding → activation
2. Skip onboarding → core functionality works
3. Resume interrupted onboarding
4. Role-based conditional steps
5. Empty state guidance

### Performance Testing

```typescript
test('onboarding loads within performance budget', async ({ page }) => {
  const startTime = Date.now();
  
  await page.goto('/signup');
  await signUpAsNewUser(page);
  await page.click('[data-testid="start-onboarding"]');
  
  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(2000); // 2 second budget
});
```

### Accessibility Testing

```typescript
test('onboarding is keyboard navigable', async ({ page }) => {
  await signUpAsNewUser(page);
  
  // Navigate through onboarding using only keyboard
  await page.keyboard.press('Tab'); // Focus skip button
  await page.keyboard.press('Tab'); // Focus next button
  await page.keyboard.press('Enter'); // Activate next
  
  // Verify step advanced
  await expect(page.locator('[data-testid="onboarding-step-2"]')).toBeVisible();
});
```
