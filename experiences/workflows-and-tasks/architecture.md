# Workflows & Tasks -- Architecture

## Contents

- [Workflow State Management](#workflow-state-management)
- [Approval Chain Architecture](#approval-chain-architecture)
- [Long-Running Task Patterns](#long-running-task-patterns)
- [Bulk Operation Architecture](#bulk-operation-architecture)
- [Undo/Cancel Patterns](#undocancel-patterns)
- [Optimistic Task Completion](#optimistic-task-completion)
- [Event-Driven Workflows](#event-driven-workflows)
- [Background Job Architecture](#background-job-architecture)

## Workflow State Management

### Finite State Machines for Workflow Steps

Workflows can be modeled as finite state machines (FSMs) where each step is a state and transitions represent valid moves between steps.

**Simple FSM Example** (Spring Boot with Spring Statemachine):

```java
@Configuration
@EnableStateMachine
public class WorkflowStateMachineConfig extends StateMachineConfigurerAdapter<String, String> {
    
    @Override
    public void configure(StateMachineStateConfigurer<String, String> states) throws Exception {
        states
            .withStates()
            .initial("DRAFT")
            .states(Set.of("DRAFT", "REVIEW", "APPROVED", "REJECTED", "COMPLETED"));
    }
    
    @Override
    public void configure(StateMachineTransitionConfigurer<String, String> transitions) throws Exception {
        transitions
            .withExternal()
                .source("DRAFT").target("REVIEW").event("SUBMIT")
            .and()
            .withExternal()
                .source("REVIEW").target("APPROVED").event("APPROVE")
            .and()
            .withExternal()
                .source("REVIEW").target("REJECTED").event("REJECT")
            .and()
            .withExternal()
                .source("APPROVED").target("COMPLETED").event("COMPLETE");
    }
}
```

**Vue 3 Composable Example**:

```typescript
// composables/useWorkflow.ts
import { ref, computed } from 'vue'

type WorkflowState = 'draft' | 'review' | 'approved' | 'rejected' | 'completed'

const workflowTransitions: Record<WorkflowState, WorkflowState[]> = {
  draft: ['review'],
  review: ['approved', 'rejected'],
  approved: ['completed'],
  rejected: ['draft'],
  completed: []
}

export function useWorkflow(initialState: WorkflowState = 'draft') {
  const currentState = ref<WorkflowState>(initialState)
  const history = ref<WorkflowState[]>([initialState])
  
  const canTransitionTo = (target: WorkflowState) => {
    return workflowTransitions[currentState.value].includes(target)
  }
  
  const transition = (target: WorkflowState) => {
    if (canTransitionTo(target)) {
      history.value.push(target)
      currentState.value = target
      return true
    }
    return false
  }
  
  const canGoBack = computed(() => history.value.length > 1)
  const goBack = () => {
    if (canGoBack.value) {
      history.value.pop()
      currentState.value = history.value[history.value.length - 1]
    }
  }
  
  return { currentState, transition, canGoBack, goBack, canTransitionTo }
}
```

### Workflow Engine Patterns

**Simple Rule-Based Engine**:

For straightforward workflows, a rule-based approach using configuration or code rules is sufficient:

```kotlin
data class WorkflowRule(
    val currentStep: String,
    val allowedNextSteps: List<String>,
    val conditions: List<(WorkflowContext) -> Boolean> = emptyList()
)

class SimpleWorkflowEngine(private val rules: List<WorkflowRule>) {
    fun canTransition(context: WorkflowContext, from: String, to: String): Boolean {
        val rule = rules.find { it.currentStep == from } ?: return false
        return to in rule.allowedNextSteps && 
               rule.conditions.all { it(context) }
    }
}
```

**BPMN-Style Engine**:

For complex workflows with parallel branches, gateways, and sub-processes, consider BPMN engines like Camunda or Flowable:

```java
@RestController
@RequestMapping("/workflows")
public class WorkflowController {
    
    @Autowired
    private RuntimeService runtimeService;
    
    @PostMapping("/start")
    public ResponseEntity<String> startWorkflow(@RequestBody WorkflowRequest request) {
        ProcessInstance instance = runtimeService.startProcessInstanceByKey(
            "approval-workflow",
            request.getVariables()
        );
        return ResponseEntity.ok(instance.getId());
    }
}
```

## Approval Chain Architecture

### Sequential Approval

Approvals must happen in a specific order:

```java
@Entity
public class ApprovalChain {
    @Id
    private String id;
    
    @OneToMany(cascade = CascadeType.ALL)
    @OrderColumn
    private List<ApprovalStep> steps;
    
    private int currentStepIndex = 0;
    
    public ApprovalStep getCurrentStep() {
        return steps.get(currentStepIndex);
    }
    
    public void approve(String approverId, String comment) {
        ApprovalStep current = getCurrentStep();
        current.approve(approverId, comment);
        
        if (currentStepIndex < steps.size() - 1) {
            currentStepIndex++;
            notifyNextApprover();
        } else {
            complete();
        }
    }
}
```

### Parallel Approval

Multiple approvers can approve simultaneously:

```kotlin
data class ParallelApproval(
    val id: String,
    val requiredApprovals: Int,
    val approvers: List<Approver>,
    val approvals: MutableList<Approval> = mutableListOf()
) {
    fun approve(approverId: String): ApprovalResult {
        if (approvals.size >= requiredApprovals) {
            return ApprovalResult.ALREADY_COMPLETE
        }
        
        val approval = Approval(approverId, Instant.now())
        approvals.add(approval)
        
        return if (approvals.size >= requiredApprovals) {
            ApprovalResult.COMPLETE
        } else {
            ApprovalResult.PENDING
        }
    }
}
```

### Delegation and Escalation

```java
@Service
public class ApprovalService {
    
    public void delegate(String approvalId, String fromApprover, String toApprover) {
        Approval approval = approvalRepository.findById(approvalId);
        approval.delegate(fromApprover, toApprover);
        notificationService.notifyDelegation(toApprover, approval);
    }
    
    @Scheduled(fixedDelay = 3600000) // Check every hour
    public void checkTimeouts() {
        List<Approval> overdue = approvalRepository.findOverdue(
            Duration.ofDays(3)
        );
        
        overdue.forEach(approval -> {
            escalationService.escalate(approval);
        });
    }
}
```

## Long-Running Task Patterns

### Async Task Execution with Kafka

```java
@Service
public class TaskService {
    
    @Autowired
    private KafkaTemplate<String, TaskMessage> kafkaTemplate;
    
    @Autowired
    private TaskRepository taskRepository;
    
    public String startLongRunningTask(TaskRequest request) {
        Task task = new Task(UUID.randomUUID().toString(), TaskStatus.PENDING);
        taskRepository.save(task);
        
        kafkaTemplate.send("task-queue", new TaskMessage(task.getId(), request));
        
        return task.getId();
    }
}

@KafkaListener(topics = "task-queue")
public class TaskProcessor {
    
    @Autowired
    private TaskRepository taskRepository;
    
    public void processTask(TaskMessage message) {
        Task task = taskRepository.findById(message.getTaskId());
        task.setStatus(TaskStatus.PROCESSING);
        taskRepository.save(task);
        
        try {
            // Long-running work
            processTaskWork(message);
            
            task.setStatus(TaskStatus.COMPLETED);
            task.setProgress(100);
        } catch (Exception e) {
            task.setStatus(TaskStatus.FAILED);
            task.setErrorMessage(e.getMessage());
        }
        
        taskRepository.save(task);
    }
}
```

### Task Status Polling vs WebSocket Updates

**Polling Approach** (simpler, works everywhere):

```typescript
// Vue 3 composable
export function useTaskStatus(taskId: string) {
  const status = ref<TaskStatus>('pending')
  const progress = ref(0)
  
  const pollStatus = async () => {
    const response = await fetch(`/api/tasks/${taskId}/status`)
    const data = await response.json()
    status.value = data.status
    progress.value = data.progress
    
    if (data.status === 'processing') {
      setTimeout(pollStatus, 2000) // Poll every 2 seconds
    }
  }
  
  onMounted(() => {
    pollStatus()
  })
  
  return { status, progress }
}
```

**WebSocket Approach** (real-time, more efficient):

```typescript
export function useTaskStatusWebSocket(taskId: string) {
  const status = ref<TaskStatus>('pending')
  const progress = ref(0)
  
  const ws = new WebSocket(`ws://api/tasks/${taskId}/status`)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    status.value = data.status
    progress.value = data.progress
  }
  
  onUnmounted(() => {
    ws.close()
  })
  
  return { status, progress }
}
```

### Task Queue with Progress Reporting

```java
@Service
public class ProgressTrackingTaskService {
    
    @Async
    public CompletableFuture<Void> processWithProgress(String taskId, List<Item> items) {
        Task task = taskRepository.findById(taskId);
        int total = items.size();
        
        for (int i = 0; i < items.size(); i++) {
            processItem(items.get(i));
            
            int progress = (int) ((i + 1) * 100.0 / total);
            task.setProgress(progress);
            taskRepository.save(task);
            
            // Publish progress event
            eventPublisher.publish(new TaskProgressEvent(taskId, progress));
        }
        
        task.setStatus(TaskStatus.COMPLETED);
        taskRepository.save(task);
        
        return CompletableFuture.completedFuture(null);
    }
}
```

## Bulk Operation Architecture

### Batch Processing with Chunked Execution

```java
@Service
public class BulkOperationService {
    
    private static final int CHUNK_SIZE = 100;
    
    @Async
    public CompletableFuture<BulkResult> processBulk(List<String> itemIds, BulkOperation operation) {
        BulkResult result = new BulkResult();
        List<List<String>> chunks = Lists.partition(itemIds, CHUNK_SIZE);
        
        for (List<String> chunk : chunks) {
            BulkChunkResult chunkResult = processChunk(chunk, operation);
            result.merge(chunkResult);
            
            // Update progress
            updateProgress(result);
        }
        
        return CompletableFuture.completedFuture(result);
    }
    
    private BulkChunkResult processChunk(List<String> itemIds, BulkOperation operation) {
        BulkChunkResult result = new BulkChunkResult();
        
        for (String itemId : itemIds) {
            try {
                operation.execute(itemId);
                result.addSuccess(itemId);
            } catch (Exception e) {
                result.addFailure(itemId, e.getMessage());
            }
        }
        
        return result;
    }
}
```

### Partial Failure Handling Strategies

**All-or-Nothing** (Transactional):

```java
@Transactional
public BulkResult processBulkTransactional(List<String> itemIds) {
    try {
        itemIds.forEach(this::processItem);
        return BulkResult.allSuccess(itemIds);
    } catch (Exception e) {
        throw new BulkOperationException("All items failed", e);
    }
}
```

**Best-Effort** (Continue on failure):

```java
public BulkResult processBulkBestEffort(List<String> itemIds) {
    BulkResult result = new BulkResult();
    
    itemIds.forEach(itemId -> {
        try {
            processItem(itemId);
            result.addSuccess(itemId);
        } catch (Exception e) {
            result.addFailure(itemId, e.getMessage());
        }
    });
    
    return result;
}
```

### Server-Side Batch Endpoints

```java
@RestController
@RequestMapping("/api/bulk")
public class BulkOperationController {
    
    @PostMapping("/delete")
    public ResponseEntity<BulkResult> bulkDelete(@RequestBody BulkDeleteRequest request) {
        BulkResult result = bulkService.deleteItems(request.getItemIds());
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/status-change")
    public ResponseEntity<BulkResult> bulkStatusChange(@RequestBody BulkStatusChangeRequest request) {
        BulkResult result = bulkService.changeStatus(
            request.getItemIds(),
            request.getNewStatus()
        );
        return ResponseEntity.ok(result);
    }
}
```

## Undo/Cancel Patterns

### Soft Delete for Undo

```java
@Entity
public class Item {
    @Id
    private String id;
    
    private boolean deleted = false;
    private Instant deletedAt;
    private String deletedBy;
    
    public void softDelete(String userId) {
        this.deleted = true;
        this.deletedAt = Instant.now();
        this.deletedBy = userId;
    }
    
    public void restore() {
        this.deleted = false;
        this.deletedAt = null;
        this.deletedBy = null;
    }
}

@Service
public class UndoService {
    
    @Transactional
    public void undoDelete(String itemId) {
        Item item = itemRepository.findById(itemId);
        if (item.isDeleted() && isWithinUndoWindow(item.getDeletedAt())) {
            item.restore();
            itemRepository.save(item);
        } else {
            throw new UndoExpiredException();
        }
    }
    
    private boolean isWithinUndoWindow(Instant deletedAt) {
        return Duration.between(deletedAt, Instant.now()).toMinutes() < 5;
    }
}
```

### Saga-Based Compensation for Multi-Step Workflows

Using Axon Framework:

```java
@Saga
public class OrderProcessingSaga {
    
    @Autowired
    private transient CommandGateway commandGateway;
    
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(OrderCreatedEvent event) {
        commandGateway.send(new ReserveInventoryCommand(event.getOrderId()));
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(InventoryReservedEvent event) {
        commandGateway.send(new ProcessPaymentCommand(event.getOrderId()));
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PaymentFailedEvent event) {
        // Compensate: release inventory
        commandGateway.send(new ReleaseInventoryCommand(event.getOrderId()));
        end();
    }
}
```

### Cancellation Tokens for In-Progress Operations

```java
@Service
public class CancellableTaskService {
    
    private final Map<String, CancellationToken> activeTasks = new ConcurrentHashMap<>();
    
    public String startCancellableTask(TaskRequest request) {
        String taskId = UUID.randomUUID().toString();
        CancellationToken token = new CancellationToken();
        activeTasks.put(taskId, token);
        
        CompletableFuture.runAsync(() -> {
            processTaskWithCancellation(request, token);
        });
        
        return taskId;
    }
    
    public void cancelTask(String taskId) {
        CancellationToken token = activeTasks.get(taskId);
        if (token != null) {
            token.cancel();
        }
    }
    
    private void processTaskWithCancellation(TaskRequest request, CancellationToken token) {
        for (Item item : request.getItems()) {
            if (token.isCancelled()) {
                throw new TaskCancelledException();
            }
            processItem(item);
        }
    }
}
```

## Optimistic Task Completion

Mark UI as done immediately, reconcile with server:

```typescript
// Vue 3 composable
export function useOptimisticTask() {
  const localStatus = ref<'pending' | 'completed'>('pending')
  const serverStatus = ref<'pending' | 'completed' | 'failed'>('pending')
  
  const completeTask = async (taskId: string) => {
    // Optimistically update UI
    localStatus.value = 'completed'
    
    try {
      const response = await fetch(`/api/tasks/${taskId}/complete`, {
        method: 'POST'
      })
      
      if (!response.ok) {
        throw new Error('Server rejected completion')
      }
      
      serverStatus.value = 'completed'
    } catch (error) {
      // Rollback optimistic update
      localStatus.value = 'pending'
      serverStatus.value = 'failed'
      throw error
    }
  }
  
  return { localStatus, serverStatus, completeTask }
}
```

## Event-Driven Workflows

### Axon Sagas for Orchestrated Workflows

```java
@Saga
public class OnboardingSaga {
    
    @Autowired
    private transient CommandGateway commandGateway;
    
    private String userId;
    private boolean accountCreated = false;
    private boolean emailVerified = false;
    
    @StartSaga
    @SagaEventHandler(associationProperty = "userId")
    public void handle(UserRegisteredEvent event) {
        this.userId = event.getUserId();
        commandGateway.send(new CreateAccountCommand(event.getUserId()));
    }
    
    @SagaEventHandler(associationProperty = "userId")
    public void handle(AccountCreatedEvent event) {
        accountCreated = true;
        commandGateway.send(new SendVerificationEmailCommand(userId));
        checkCompletion();
    }
    
    @SagaEventHandler(associationProperty = "userId")
    public void handle(EmailVerifiedEvent event) {
        emailVerified = true;
        checkCompletion();
    }
    
    private void checkCompletion() {
        if (accountCreated && emailVerified) {
            commandGateway.send(new CompleteOnboardingCommand(userId));
            end();
        }
    }
}
```

### Event-Based Step Transitions

```java
@Component
public class WorkflowEventListener {
    
    @Autowired
    private WorkflowService workflowService;
    
    @EventListener
    public void handleStepCompleted(StepCompletedEvent event) {
        Workflow workflow = workflowService.findById(event.getWorkflowId());
        
        // Determine next step based on event
        String nextStep = determineNextStep(workflow, event);
        
        if (nextStep != null) {
            workflowService.transitionToStep(workflow.getId(), nextStep);
        }
    }
}
```

## Background Job Architecture

### Scheduled Tasks with Spring @Scheduled

```java
@Component
public class ScheduledWorkflowTasks {
    
    @Autowired
    private WorkflowService workflowService;
    
    @Scheduled(cron = "0 0 9 * * *") // Daily at 9 AM
    public void processPendingApprovals() {
        List<Workflow> pending = workflowService.findPendingApprovals();
        pending.forEach(this::processApproval);
    }
    
    @Scheduled(fixedDelay = 300000) // Every 5 minutes
    public void checkStaleWorkflows() {
        List<Workflow> stale = workflowService.findStaleWorkflows(Duration.ofHours(24));
        stale.forEach(this::escalateWorkflow);
    }
}
```

### Job Queue with Redis

```java
@Service
public class RedisJobQueue {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    private static final String QUEUE_KEY = "workflow:jobs";
    
    public void enqueue(WorkflowJob job) {
        redisTemplate.opsForList().rightPush(QUEUE_KEY, job);
    }
    
    public WorkflowJob dequeue() {
        return (WorkflowJob) redisTemplate.opsForList().leftPop(QUEUE_KEY);
    }
}

@Component
public class JobProcessor {
    
    @Autowired
    private RedisJobQueue jobQueue;
    
    @Scheduled(fixedDelay = 1000)
    public void processJobs() {
        WorkflowJob job = jobQueue.dequeue();
        if (job != null) {
            processJob(job);
        }
    }
}
```

### Retry with Backoff

```java
@Service
public class RetryableTaskService {
    
    @Retryable(
        value = {TransientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public void processTaskWithRetry(Task task) {
        // Task processing that may fail transiently
        externalService.process(task);
    }
    
    @Recover
    public void recover(TransientException e, Task task) {
        // Handle final failure after retries exhausted
        task.setStatus(TaskStatus.FAILED);
        notificationService.notifyFailure(task);
    }
}
```
