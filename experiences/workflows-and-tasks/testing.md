# Workflows & Tasks -- Testing

## Contents

- [Workflow Flow Testing](#workflow-flow-testing)
- [Approval Chain Testing](#approval-chain-testing)
- [Bulk Action Testing](#bulk-action-testing)
- [Long-Running Task Testing](#long-running-task-testing)
- [Undo Testing](#undo-testing)
- [Concurrent Workflow Testing](#concurrent-workflow-testing)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

## Workflow Flow Testing

### Complete Happy Path

Test the entire workflow from start to finish:

```typescript
// Playwright test example
test('complete onboarding workflow', async ({ page }) => {
  await page.goto('/onboarding')
  
  // Step 1: Basic info
  await page.fill('[data-testid=name]', 'John Doe')
  await page.fill('[data-testid=email]', 'john@example.com')
  await page.click('[data-testid=next]')
  
  // Step 2: Preferences
  await page.check('[data-testid=preference-email]')
  await page.click('[data-testid=next]')
  
  // Step 3: Review
  await expect(page.locator('[data-testid=review-name]')).toHaveText('John Doe')
  await page.click('[data-testid=complete]')
  
  // Verify completion
  await expect(page.locator('[data-testid=success-message]')).toBeVisible()
})
```

### Testing Each Step Individually

Test each step in isolation to ensure it works independently:

```java
@SpringBootTest
public class WorkflowStepTest {
    
    @Autowired
    private WorkflowService workflowService;
    
    @Test
    public void testStep1Validation() {
        Workflow workflow = new Workflow();
        workflow.setStep("step1");
        
        // Test valid data
        workflow.setData(Map.of("name", "John", "email", "john@example.com"));
        assertTrue(workflowService.canProceedToNextStep(workflow));
        
        // Test invalid data
        workflow.setData(Map.of("name", ""));
        assertFalse(workflowService.canProceedToNextStep(workflow));
    }
    
    @Test
    public void testStep2Processing() {
        Workflow workflow = createWorkflowAtStep("step2");
        workflowService.processStep(workflow);
        
        assertEquals("step3", workflow.getCurrentStep());
    }
}
```

### Skip/Back Navigation Testing

Test that users can navigate backward and that state is preserved:

```typescript
test('workflow back navigation preserves data', async ({ page }) => {
  await page.goto('/workflow')
  
  // Fill step 1
  await page.fill('[data-testid=field1]', 'value1')
  await page.click('[data-testid=next]')
  
  // Go to step 2
  await page.fill('[data-testid=field2]', 'value2')
  
  // Go back
  await page.click('[data-testid=back]')
  
  // Verify step 1 data is preserved
  await expect(page.locator('[data-testid=field1]')).toHaveValue('value1')
  
  // Verify can proceed again
  await page.click('[data-testid=next]')
  await expect(page.locator('[data-testid=field2]')).toHaveValue('value2')
})
```

## Approval Chain Testing

### Approve Scenario

```java
@Test
public void testSequentialApproval() {
    ApprovalChain chain = createApprovalChain("manager", "director", "vp");
    
    // Manager approves
    chain.approve("manager", "Looks good");
    assertEquals("director", chain.getCurrentStep().getApprover());
    
    // Director approves
    chain.approve("director", "Approved");
    assertEquals("vp", chain.getCurrentStep().getApprover());
    
    // VP approves - should complete
    chain.approve("vp", "Final approval");
    assertTrue(chain.isComplete());
}
```

### Reject Scenario

```java
@Test
public void testRejectionStopsChain() {
    ApprovalChain chain = createApprovalChain("manager", "director");
    
    chain.approve("manager", "Approved");
    chain.reject("director", "Needs revision");
    
    assertTrue(chain.isRejected());
    assertEquals("draft", chain.getStatus());
    assertFalse(chain.isComplete());
}
```

### Delegate Scenario

```java
@Test
public void testDelegation() {
    ApprovalChain chain = createApprovalChain("manager");
    
    chain.delegate("manager", "assistant-manager");
    
    ApprovalStep current = chain.getCurrentStep();
    assertEquals("assistant-manager", current.getApprover());
    assertTrue(current.isDelegated());
}
```

### Escalate Scenario

```java
@Test
public void testEscalationOnTimeout() {
    ApprovalChain chain = createApprovalChain("manager");
    chain.getCurrentStep().setCreatedAt(Instant.now().minus(Duration.ofDays(4)));
    
    escalationService.checkAndEscalate(chain);
    
    ApprovalStep current = chain.getCurrentStep();
    assertEquals("senior-manager", current.getApprover()); // Escalated
    assertTrue(current.isEscalated());
}
```

## Bulk Action Testing

### Select All Testing

```typescript
test('select all items in bulk operation', async ({ page }) => {
  await page.goto('/items')
  
  // Verify items exist
  const itemCount = await page.locator('[data-testid=item-row]').count()
  expect(itemCount).toBeGreaterThan(0)
  
  // Select all
  await page.click('[data-testid=select-all]')
  
  // Verify all checkboxes are checked
  const checkedCount = await page.locator('[data-testid=item-checkbox]:checked').count()
  expect(checkedCount).toBe(itemCount)
  
  // Verify bulk actions are enabled
  await expect(page.locator('[data-testid=bulk-delete]')).toBeEnabled()
})
```

### Partial Selection Testing

```typescript
test('partial selection enables bulk actions', async ({ page }) => {
  await page.goto('/items')
  
  // Select first 3 items
  await page.check('[data-testid=item-1]')
  await page.check('[data-testid=item-2]')
  await page.check('[data-testid=item-3]')
  
  // Verify bulk actions enabled
  await expect(page.locator('[data-testid=bulk-actions]')).toBeVisible()
  
  // Verify selection count shown
  await expect(page.locator('[data-testid=selection-count]')).toHaveText('3 selected')
})
```

### Partial Failure Testing

```java
@Test
public void testBulkOperationPartialFailure() {
    List<String> itemIds = Arrays.asList("item1", "item2", "item3");
    
    // Mock: item2 will fail
    when(itemService.delete("item2")).thenThrow(new RuntimeException("Cannot delete"));
    
    BulkResult result = bulkService.deleteItems(itemIds);
    
    assertEquals(2, result.getSuccessCount());
    assertEquals(1, result.getFailureCount());
    assertTrue(result.getFailedItems().contains("item2"));
    assertNotNull(result.getFailureReason("item2"));
}
```

### Empty Selection Testing

```typescript
test('bulk actions disabled when no selection', async ({ page }) => {
  await page.goto('/items')
  
  // Verify no items selected
  await expect(page.locator('[data-testid=bulk-actions]')).not.toBeVisible()
  
  // Select then deselect
  await page.check('[data-testid=item-1]')
  await page.uncheck('[data-testid=item-1]')
  
  // Verify bulk actions hidden again
  await expect(page.locator('[data-testid=bulk-actions]')).not.toBeVisible()
})
```

## Long-Running Task Testing

### Progress Updates Testing

```typescript
test('long-running task shows progress updates', async ({ page }) => {
  await page.goto('/tasks')
  
  // Start task
  await page.click('[data-testid=start-export]')
  
  // Verify initial progress
  await expect(page.locator('[data-testid=progress]')).toHaveText('0%')
  
  // Wait for progress updates (mock server)
  await page.waitForFunction(
    () => document.querySelector('[data-testid=progress]')?.textContent !== '0%'
  )
  
  const progress = await page.locator('[data-testid=progress]').textContent()
  expect(parseInt(progress)).toBeGreaterThan(0)
})
```

### Completion Testing

```java
@Test
public void testTaskCompletion() throws InterruptedException {
    String taskId = taskService.startLongRunningTask(createTaskRequest());
    
    // Poll until complete
    Task task = null;
    for (int i = 0; i < 10; i++) {
        task = taskRepository.findById(taskId);
        if (task.getStatus() == TaskStatus.COMPLETED) {
            break;
        }
        Thread.sleep(1000);
    }
    
    assertNotNull(task);
    assertEquals(TaskStatus.COMPLETED, task.getStatus());
    assertEquals(100, task.getProgress());
}
```

### Failure Testing

```java
@Test
public void testTaskFailureHandling() {
    TaskRequest request = createTaskRequest();
    request.setShouldFail(true); // Configure to fail
    
    String taskId = taskService.startLongRunningTask(request);
    
    // Wait for failure
    await().atMost(30, TimeUnit.SECONDS).until(() -> {
        Task task = taskRepository.findById(taskId);
        return task.getStatus() == TaskStatus.FAILED;
    });
    
    Task task = taskRepository.findById(taskId);
    assertEquals(TaskStatus.FAILED, task.getStatus());
    assertNotNull(task.getErrorMessage());
}
```

### Cancellation Testing

```typescript
test('can cancel long-running task', async ({ page }) => {
  await page.goto('/tasks')
  
  // Start task
  await page.click('[data-testid=start-task]')
  
  // Verify task started
  await expect(page.locator('[data-testid=task-status]')).toHaveText('Processing')
  
  // Cancel task
  await page.click('[data-testid=cancel-task]')
  
  // Confirm cancellation
  await page.click('[data-testid=confirm-cancel]')
  
  // Verify cancelled
  await expect(page.locator('[data-testid=task-status]')).toHaveText('Cancelled')
})
```

### Timeout Testing

```java
@Test
public void testTaskTimeout() {
    TaskRequest request = createTaskRequest();
    request.setTimeout(Duration.ofSeconds(5));
    
    String taskId = taskService.startLongRunningTask(request);
    
    // Wait for timeout
    await().atMost(10, TimeUnit.SECONDS).until(() -> {
        Task task = taskRepository.findById(taskId);
        return task.getStatus() == TaskStatus.TIMEOUT;
    });
}
```

## Undo Testing

### Undo Immediately After Action

```typescript
test('undo immediately after delete', async ({ page }) => {
  await page.goto('/items')
  
  const initialCount = await page.locator('[data-testid=item-row]').count()
  
  // Delete item
  await page.click('[data-testid=delete-item-1]')
  
  // Verify item removed
  await expect(page.locator('[data-testid=item-row]')).toHaveCount(initialCount - 1)
  
  // Undo
  await page.click('[data-testid=undo]')
  
  // Verify item restored
  await expect(page.locator('[data-testid=item-row]')).toHaveCount(initialCount)
})
```

### Undo After Time Delay

```java
@Test
public void testUndoAfterDelay() throws InterruptedException {
    String itemId = "item1";
    itemService.deleteItem(itemId);
    
    // Wait 3 minutes (within 5-minute undo window)
    Thread.sleep(Duration.ofMinutes(3).toMillis());
    
    // Should still be able to undo
    assertTrue(undoService.canUndo(itemId));
    undoService.undoDelete(itemId);
    
    assertFalse(itemRepository.findById(itemId).isDeleted());
}
```

### Undo Unavailable Scenarios

```java
@Test
public void testUndoExpired() throws InterruptedException {
    String itemId = "item1";
    itemService.deleteItem(itemId);
    
    // Wait past undo window (6 minutes > 5-minute window)
    Thread.sleep(Duration.ofMinutes(6).toMillis());
    
    // Should not be able to undo
    assertFalse(undoService.canUndo(itemId));
    
    assertThrows(UndoExpiredException.class, () -> {
        undoService.undoDelete(itemId);
    });
}
```

## Concurrent Workflow Testing

### Two Users in Same Workflow

```java
@Test
public void testConcurrentWorkflowAccess() {
    String workflowId = workflowService.createWorkflow(createWorkflowRequest());
    
    // User 1 starts editing
    Workflow workflow1 = workflowService.lockForEditing(workflowId, "user1");
    workflow1.setData("step1", Map.of("field", "value1"));
    
    // User 2 tries to edit (should fail or get read-only)
    assertThrows(WorkflowLockedException.class, () -> {
        workflowService.lockForEditing(workflowId, "user2");
    });
    
    // User 1 saves and releases lock
    workflowService.saveAndUnlock(workflow1);
    
    // Now user 2 can edit
    Workflow workflow2 = workflowService.lockForEditing(workflowId, "user2");
    assertNotNull(workflow2);
}
```

### Race Condition Testing

```java
@Test
public void testApprovalRaceCondition() {
    ApprovalChain chain = createParallelApprovalChain(2, "approver1", "approver2", "approver3");
    
    // Simulate concurrent approvals
    CompletableFuture<Void> future1 = CompletableFuture.runAsync(() -> {
        chain.approve("approver1", "Approved");
    });
    
    CompletableFuture<Void> future2 = CompletableFuture.runAsync(() -> {
        chain.approve("approver2", "Approved");
    });
    
    CompletableFuture.allOf(future1, future2).join();
    
    // Should be complete (2 approvals received)
    assertTrue(chain.isComplete());
    assertEquals(2, chain.getApprovalCount());
}
```

## QA and Test Engineer Perspective

### Test Data Management

**Challenge**: Workflows often require complex test data setups (multiple steps, approvals, dependencies).

**Solution**: Create test fixtures and builders:

```java
public class WorkflowTestBuilder {
    public static Workflow createOnboardingWorkflow() {
        Workflow workflow = new Workflow();
        workflow.setType("onboarding");
        workflow.setSteps(Arrays.asList("basic-info", "preferences", "review"));
        return workflow;
    }
    
    public static ApprovalChain createSequentialApprovalChain(String... approvers) {
        ApprovalChain chain = new ApprovalChain();
        Arrays.stream(approvers)
            .map(ApprovalStep::new)
            .forEach(chain::addStep);
        return chain;
    }
}
```

### Test Environment Isolation

**Challenge**: Workflows may have side effects (emails, external API calls) that interfere with tests.

**Solution**: Use test doubles and environment isolation:

```java
@TestConfiguration
public class TestConfig {
    @Bean
    @Primary
    public EmailService mockEmailService() {
        return mock(EmailService.class);
    }
    
    @Bean
    @Primary
    public ExternalApiService mockExternalApi() {
        return mock(ExternalApiService.class);
    }
}
```

### Async Operation Testing

**Challenge**: Long-running and async operations are difficult to test synchronously.

**Solution**: Use polling, timeouts, and test-friendly APIs:

```java
@Test
public void testAsyncTask() {
    String taskId = taskService.startTask(request);
    
    // Poll with timeout
    await().atMost(30, TimeUnit.SECONDS)
        .pollInterval(1, TimeUnit.SECONDS)
        .until(() -> {
            Task task = taskRepository.findById(taskId);
            return task.getStatus() == TaskStatus.COMPLETED;
        });
}
```

### State Verification

**Challenge**: Workflows have complex state that must be verified at each step.

**Solution**: Create comprehensive state verification helpers:

```java
public class WorkflowStateVerifier {
    public static void verifyStep(Workflow workflow, String expectedStep) {
        assertEquals(expectedStep, workflow.getCurrentStep());
        assertTrue(workflow.getCompletedSteps().containsAll(
            getPrerequisites(expectedStep)
        ));
    }
    
    public static void verifyApprovalState(ApprovalChain chain, String approver, ApprovalStatus status) {
        ApprovalStep step = chain.getStepForApprover(approver);
        assertEquals(status, step.getStatus());
    }
}
```

### End-to-End Workflow Testing

**Challenge**: Testing complete workflows end-to-end is time-consuming and brittle.

**Solution**: Use Page Object Model and break into composable test steps:

```typescript
// Page Object
class OnboardingPage {
  async fillBasicInfo(name: string, email: string) {
    await this.page.fill('[data-testid=name]', name)
    await this.page.fill('[data-testid=email]', email)
    await this.page.click('[data-testid=next]')
  }
  
  async selectPreferences(preferences: string[]) {
    for (const pref of preferences) {
      await this.page.check(`[data-testid=preference-${pref}]`)
    }
    await this.page.click('[data-testid=next]')
  }
  
  async complete() {
    await this.page.click('[data-testid=complete]')
  }
}

// Test
test('complete onboarding', async ({ page }) => {
  const onboarding = new OnboardingPage(page)
  await onboarding.fillBasicInfo('John', 'john@example.com')
  await onboarding.selectPreferences(['email', 'sms'])
  await onboarding.complete()
})
```

### Regression Testing Strategy

**Challenge**: Workflow changes can break existing flows in unexpected ways.

**Solution**: Maintain a regression test suite covering all workflow types:

```java
@Nested
class WorkflowRegressionTests {
    
    @Test
    void testOnboardingWorkflow() { /* ... */ }
    
    @Test
    void testApprovalWorkflow() { /* ... */ }
    
    @Test
    void testBulkOperationWorkflow() { /* ... */ }
    
    // Add new workflow tests here as workflows are added
}
```
