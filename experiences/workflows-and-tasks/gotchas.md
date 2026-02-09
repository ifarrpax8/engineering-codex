# Workflows & Tasks -- Gotchas

## Contents

- [Wizard Steps That Can't Be Revisited](#wizard-steps-that-cant-be-revisited)
- [Bulk Operations With No Progress Indicator](#bulk-operations-with-no-progress-indicator)
- [Approval Chains With No Timeout](#approval-chains-with-no-timeout)
- [Long-Running Tasks With No Cancellation Option](#long-running-tasks-with-no-cancellation-option)
- [Partial Bulk Failure With No Retry Mechanism](#partial-bulk-failure-with-no-retry-mechanism)
- [Optimistic Completion Without Rollback Handling](#optimistic-completion-without-rollback-handling)
- [Workflow State Stored Only Client-Side](#workflow-state-stored-only-client-side)
- [Concurrent Modifications in Approval Workflows](#concurrent-modifications-in-approval-workflows)
- [Undo Window Too Short or Too Long](#undo-window-too-short-or-too-long)

## Wizard Steps That Can't Be Revisited

**Problem**: User realizes they made a mistake in step 1 but is currently on step 4. They can't go back to fix it without starting over.

**Example**:
```typescript
// BAD: No back navigation
function WizardStep({ step }: { step: number }) {
  return (
    <div>
      {step === 1 && <Step1 />}
      {step === 2 && <Step2 />}
      {step === 3 && <Step3 />}
      {/* No way to go back! */}
    </div>
  );
}
```

**Solution**: Always allow backward navigation (unless there's a business reason not to):

```typescript
// GOOD: Back navigation enabled
function WizardStep({ step, onStepChange }: Props) {
  return (
    <div>
      <button 
        onClick={() => onStepChange(step - 1)}
        disabled={step === 1}
      >
        Back
      </button>
      {/* Steps can be revisited */}
    </div>
  );
}
```

**Exception**: Some workflows legitimately can't go backward (e.g., payment processing after payment is submitted). In these cases, make it clear upfront and provide a way to start over.

## Bulk Operations With No Progress Indicator

**Problem**: User selects 500 items and clicks "Delete All". The UI shows nothing for 30 seconds, making them think the app is frozen. They refresh the page, potentially causing issues.

**Example**:
```java
// BAD: No progress feedback
@PostMapping("/bulk-delete")
public ResponseEntity<Void> bulkDelete(@RequestBody List<String> ids) {
    ids.forEach(itemService::delete); // Takes 30 seconds, no feedback
    return ResponseEntity.ok().build();
}
```

**Solution**: Provide immediate feedback and progress updates:

```java
// GOOD: Async with progress tracking
@PostMapping("/bulk-delete")
public ResponseEntity<BulkTaskResponse> bulkDelete(@RequestBody List<String> ids) {
    String taskId = UUID.randomUUID().toString();
    
    // Start async processing
    bulkService.deleteItemsAsync(taskId, ids);
    
    // Return immediately with task ID for polling
    return ResponseEntity.ok(new BulkTaskResponse(taskId, "PROCESSING"));
}

// Frontend polls for progress
const pollProgress = async (taskId: string) => {
  const response = await fetch(`/api/tasks/${taskId}`);
  const task = await response.json();
  
  setProgress(task.progress); // Show progress bar
  setStatus(task.status); // Show "Processing 150 of 500..."
  
  if (task.status === 'PROCESSING') {
    setTimeout(() => pollProgress(taskId), 1000);
  }
};
```

## Approval Chains With No Timeout

**Problem**: An approval request sits with an approver for weeks with no escalation or timeout. The requester has no visibility into why it's stuck.

**Example**:
```java
// BAD: No timeout handling
@Entity
public class ApprovalStep {
    private String approver;
    private ApprovalStatus status = PENDING;
    private Instant createdAt;
    // No timeout logic!
}
```

**Solution**: Implement timeouts with escalation:

```java
// GOOD: Timeout with escalation
@Entity
public class ApprovalStep {
    private String approver;
    private ApprovalStatus status = PENDING;
    private Instant createdAt;
    private Duration timeoutDuration = Duration.ofDays(3);
    
    public boolean isOverdue() {
        return status == PENDING && 
               Duration.between(createdAt, Instant.now()).compareTo(timeoutDuration) > 0;
    }
}

@Service
public class ApprovalEscalationService {
    
    @Scheduled(fixedDelay = 3600000) // Check every hour
    public void escalateOverdueApprovals() {
        List<ApprovalStep> overdue = approvalRepository.findOverdue();
        
        overdue.forEach(step -> {
            // Escalate to manager
            String escalatedApprover = getManager(step.getApprover());
            step.escalate(escalatedApprover);
            
            // Notify original approver and requester
            notificationService.notifyEscalation(step);
        });
    }
}
```

## Long-Running Tasks With No Cancellation Option

**Problem**: User starts a data export that will take 10 minutes, then realizes they selected the wrong date range. They can't cancel it and must wait for it to complete or close the browser.

**Example**:
```java
// BAD: No cancellation support
@Async
public void exportData(ExportRequest request) {
    // Long-running operation with no way to cancel
    for (Item item : getAllItems(request)) {
        processItem(item); // Can't be interrupted
    }
}
```

**Solution**: Support cancellation tokens:

```java
// GOOD: Cancellable task
@Service
public class CancellableExportService {
    
    private final Map<String, CancellationToken> activeExports = new ConcurrentHashMap<>();
    
    @Async
    public void exportData(String taskId, ExportRequest request) {
        CancellationToken token = new CancellationToken();
        activeExports.put(taskId, token);
        
        try {
            for (Item item : getAllItems(request)) {
                if (token.isCancelled()) {
                    throw new TaskCancelledException();
                }
                processItem(item);
            }
        } finally {
            activeExports.remove(taskId);
        }
    }
    
    public void cancelExport(String taskId) {
        CancellationToken token = activeExports.get(taskId);
        if (token != null) {
            token.cancel();
        }
    }
}
```

```typescript
// Frontend: Cancel button
function ExportProgress({ taskId }: { taskId: string }) {
  const [canCancel, setCanCancel] = useState(true);
  
  const handleCancel = async () => {
    await fetch(`/api/exports/${taskId}/cancel`, { method: 'POST' });
    setCanCancel(false);
  };
  
  return (
    <div>
      <ProgressBar progress={progress} />
      {canCancel && (
        <Button onClick={handleCancel}>Cancel Export</Button>
      )}
    </div>
  );
}
```

## Partial Bulk Failure With No Retry Mechanism

**Problem**: User performs bulk delete on 100 items. 97 succeed, 3 fail (due to dependencies). The UI shows "3 failed" but provides no way to see which ones failed or retry them.

**Example**:
```java
// BAD: No detailed failure information
public BulkResult bulkDelete(List<String> ids) {
    int successCount = 0;
    int failureCount = 0;
    
    for (String id : ids) {
        try {
            itemService.delete(id);
            successCount++;
        } catch (Exception e) {
            failureCount++;
            // Error details lost!
        }
    }
    
    return new BulkResult(successCount, failureCount);
    // No way to retry failures!
}
```

**Solution**: Track failures with details and provide retry:

```java
// GOOD: Detailed failure tracking
public class BulkResult {
    private int successCount;
    private int failureCount;
    private List<String> succeededItems = new ArrayList<>();
    private Map<String, String> failedItems = new HashMap<>(); // itemId -> error
    
    public BulkResult processBulkDelete(List<String> ids) {
        BulkResult result = new BulkResult();
        
        for (String id : ids) {
            try {
                itemService.delete(id);
                result.addSuccess(id);
            } catch (Exception e) {
                result.addFailure(id, e.getMessage());
            }
        }
        
        return result;
    }
    
    public BulkResult retryFailures() {
        return processBulkDelete(new ArrayList<>(failedItems.keySet()));
    }
}
```

```tsx
// Frontend: Show failures and retry
function BulkOperationResult({ result }: { result: BulkResult }) {
  return (
    <div>
      <Alert>
        {result.successCount} succeeded, {result.failureCount} failed
      </Alert>
      
      {result.failedItems.size > 0 && (
        <div>
          <h3>Failed Items</h3>
          <List>
            {Object.entries(result.failedItems).map(([id, error]) => (
              <ListItem key={id}>
                <ListItemText primary={id} secondary={error} />
                <Button onClick={() => retryItem(id)}>Retry</Button>
              </ListItem>
            ))}
          </List>
          <Button onClick={retryAllFailed}>Retry All Failed</Button>
        </div>
      )}
    </div>
  );
}
```

## Optimistic Completion Without Rollback Handling

**Problem**: UI immediately shows "Task completed" when user clicks complete, but the server request fails. The UI remains in the "completed" state, misleading the user.

**Example**:
```typescript
// BAD: No rollback on failure
function TaskComponent({ taskId }: { taskId: string }) {
  const [status, setStatus] = useState('pending');
  
  const handleComplete = async () => {
    setStatus('completed'); // Optimistic update
    
    try {
      await fetch(`/api/tasks/${taskId}/complete`, { method: 'POST' });
      // If this fails, status stays "completed" incorrectly!
    } catch (error) {
      // No rollback!
    }
  };
  
  return <div>Status: {status}</div>;
}
```

**Solution**: Rollback optimistic updates on failure:

```typescript
// GOOD: Rollback on failure
function TaskComponent({ taskId }: { taskId: string }) {
  const [localStatus, setLocalStatus] = useState('pending');
  const [serverStatus, setServerStatus] = useState('pending');
  
  const handleComplete = async () => {
    const previousStatus = localStatus;
    setLocalStatus('completed'); // Optimistic update
    
    try {
      const response = await fetch(`/api/tasks/${taskId}/complete`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Server rejected completion');
      }
      
      setServerStatus('completed');
    } catch (error) {
      // Rollback optimistic update
      setLocalStatus(previousStatus);
      setServerStatus('failed');
      showError('Failed to complete task. Please try again.');
    }
  };
  
  // Show server status when it differs from local (reconciliation)
  const displayStatus = serverStatus === 'failed' ? serverStatus : localStatus;
  
  return <div>Status: {displayStatus}</div>;
}
```

## Workflow State Stored Only Client-Side

**Problem**: User completes 4 of 5 workflow steps, then their browser crashes or they close the tab. All progress is lost because state was only stored in component state or localStorage.

**Example**:
```typescript
// BAD: Only client-side state
function WorkflowWizard() {
  const [stepData, setStepData] = useState({});
  const [currentStep, setCurrentStep] = useState(1);
  
  // State only in memory - lost on refresh!
  useEffect(() => {
    // Only saves to localStorage, not server
    localStorage.setItem('workflow', JSON.stringify(stepData));
  }, [stepData]);
}
```

**Solution**: Persist to server:

```typescript
// GOOD: Server-side persistence
function WorkflowWizard({ workflowId }: { workflowId: string }) {
  const { data: workflow, mutate } = useSWR(
    `/api/workflows/${workflowId}`,
    fetcher
  );
  
  const saveStep = async (step: number, data: any) => {
    // Save to server immediately
    await fetch(`/api/workflows/${workflowId}/steps/${step}`, {
      method: 'PUT',
      body: JSON.stringify({ data })
    });
    
    // Refresh workflow state
    mutate();
  };
  
  // Auto-save on change
  useEffect(() => {
    const timer = setTimeout(() => {
      if (workflow?.currentStep) {
        saveStep(workflow.currentStep, workflow.stepData[workflow.currentStep]);
      }
    }, 2000); // Debounce 2 seconds
    
    return () => clearTimeout(timer);
  }, [workflow?.stepData]);
}
```

```java
// Backend: Auto-save endpoint
@PutMapping("/workflows/{id}/steps/{step}")
public ResponseEntity<Void> saveStep(
    @PathVariable String id,
    @PathVariable int step,
    @RequestBody StepData data
) {
    Workflow workflow = workflowRepository.findById(id);
    workflow.saveStepData(step, data);
    workflow.setLastSaved(Instant.now());
    workflowRepository.save(workflow);
    return ResponseEntity.ok().build();
}
```

## Concurrent Modifications in Approval Workflows

**Problem**: Approver reviews and approves an item. Meanwhile, the requester modifies the item. The approval goes through for the old version, causing data inconsistency.

**Example**:
```java
// BAD: No version checking
@PostMapping("/approvals/{id}/approve")
public ResponseEntity<Void> approve(@PathVariable String id) {
    Approval approval = approvalRepository.findById(id);
    Item item = itemRepository.findById(approval.getItemId());
    
    // Item may have been modified since approval was created!
    approval.approve();
    item.setStatus("APPROVED"); // Approving potentially stale data
}
```

**Solution**: Use optimistic locking or version checking:

```java
// GOOD: Version checking
@Entity
public class Item {
    @Id
    private String id;
    
    @Version
    private Long version; // Optimistic locking
    
    private String status;
}

@PostMapping("/approvals/{id}/approve")
public ResponseEntity<Void> approve(
    @PathVariable String id,
    @RequestParam Long itemVersion
) {
    Approval approval = approvalRepository.findById(id);
    Item item = itemRepository.findById(approval.getItemId());
    
    // Check version matches
    if (!item.getVersion().equals(itemVersion)) {
        throw new ConcurrentModificationException(
            "Item was modified. Please review the latest version."
        );
    }
    
    approval.approve();
    item.setStatus("APPROVED");
    itemRepository.save(item);
}
```

```typescript
// Frontend: Include version in approval request
const approveItem = async (approvalId: string, itemVersion: number) => {
  const response = await fetch(`/api/approvals/${approvalId}/approve?itemVersion=${itemVersion}`, {
    method: 'POST'
  });
  
  if (response.status === 409) {
    // Conflict - item was modified
    showError('Item was modified. Please refresh and review again.');
    refreshItem();
  }
};
```

## Undo Window Too Short or Too Long

**Problem**: 
- **Too short (5 seconds)**: User completes an action, gets distracted for 10 seconds, comes back and wants to undo but the window expired.
- **Too long (24 hours)**: User deletes something, forgets about it, then 20 hours later accidentally undoes it, causing confusion.

**Example**:
```java
// BAD: Fixed, inappropriate undo window
public boolean canUndo(String itemId) {
    Item item = itemRepository.findById(itemId);
    Duration sinceDeleted = Duration.between(item.getDeletedAt(), Instant.now());
    return sinceDeleted.toSeconds() < 5; // Too short!
}
```

**Solution**: Context-appropriate undo windows:

```java
// GOOD: Context-aware undo windows
public class UndoWindowPolicy {
    public Duration getUndoWindow(ActionType actionType) {
        return switch (actionType) {
            case DELETE -> Duration.ofMinutes(5); // 5 minutes for deletes
            case STATUS_CHANGE -> Duration.ofMinutes(2); // 2 minutes for status changes
            case BULK_DELETE -> Duration.ofMinutes(10); // Longer for bulk operations
            case APPROVAL -> Duration.ofHours(1); // 1 hour for approvals (can be rejected)
        };
    }
}

@Service
public class UndoService {
    
    @Autowired
    private UndoWindowPolicy undoWindowPolicy;
    
    public boolean canUndo(String itemId, ActionType actionType) {
        ActionHistory action = actionHistoryRepository.findLastAction(itemId, actionType);
        if (action == null) return false;
        
        Duration window = undoWindowPolicy.getUndoWindow(actionType);
        Duration sinceAction = Duration.between(action.getTimestamp(), Instant.now());
        
        return sinceAction.compareTo(window) < 0;
    }
}
```

```typescript
// Frontend: Show remaining undo time
function UndoSnackbar({ action, onUndo }: Props) {
  const [timeRemaining, setTimeRemaining] = useState(getUndoWindow(action.type));
  
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        const next = prev - 1;
        if (next <= 0) {
          clearInterval(interval);
          return 0;
        }
        return next;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <Snackbar
      message={`Action completed. Undo available for ${timeRemaining}s`}
      action={<Button onClick={onUndo}>Undo</Button>}
    />
  );
}
```
