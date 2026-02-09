---
recommendation_type: decision-matrix
---

# Workflows & Tasks — Options

## Contents

- [Workflow Patterns](#workflow-patterns)
- [Progress Indicators](#progress-indicators)
- [Bulk Operation Strategies](#bulk-operation-strategies)
- [Workflow Engines](#workflow-engines)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Workflow Patterns

### Linear Wizard

**Description**: Sequential steps that must be completed in a specific order. Each step depends on the previous step's completion.

**Strengths**:
- Simple to understand and implement
- Clear progression path
- Good for onboarding and guided processes
- Predictable user experience
- Easy to track progress

**Weaknesses**:
- Inflexible - users can't skip steps
- Can be frustrating if user needs to go back multiple steps
- Not suitable for independent tasks
- Can feel slow for experienced users

**Best For**:
- Onboarding flows
- Checkout processes
- Multi-step form wizards
- Guided setup processes
- Processes with clear dependencies between steps

**Avoid When**:
- Steps are independent
- Users need to jump between sections frequently
- Process has conditional paths that branch significantly
- Steps can be completed in any order

**Implementation Example**:
```tsx
function LinearWizard({ steps }: { steps: Step[] }) {
  const [currentStep, setCurrentStep] = useState(0);
  
  const canProceed = steps[currentStep].isValid;
  
  return (
    <Stepper activeStep={currentStep}>
      {steps.map((step, index) => (
        <Step key={index} completed={index < currentStep}>
          <StepLabel>{step.label}</StepLabel>
        </Step>
      ))}
      <div>
        {steps[currentStep].component}
        <Button 
          disabled={!canProceed || currentStep === 0}
          onClick={() => setCurrentStep(s => s - 1)}
        >
          Back
        </Button>
        <Button 
          disabled={!canProceed}
          onClick={() => setCurrentStep(s => s + 1)}
        >
          {currentStep === steps.length - 1 ? 'Complete' : 'Next'}
        </Button>
      </div>
    </Stepper>
  );
}
```

### Non-Linear Wizard

**Description**: Steps that can be completed in any order, often presented as a checklist. Steps may have dependencies but order is flexible.

**Strengths**:
- Flexible - users can choose their path
- Good for complex workflows with multiple entry points
- Allows users to skip optional steps
- Better for experienced users who know what they need
- Can accommodate conditional logic

**Weaknesses**:
- More complex to implement
- Can be confusing for new users
- Harder to track overall progress
- Requires more sophisticated state management
- May lead to incomplete workflows

**Best For**:
- Configuration wizards with independent sections
- Setup processes with optional steps
- Complex workflows with multiple valid paths
- Processes where users have different needs
- Administrative interfaces

**Avoid When**:
- Steps have strict dependencies
- Process is simple and linear
- Target users are primarily novices
- Mobile-first experiences (linear is better on small screens)

**Implementation Example**:
```tsx
function NonLinearWizard({ steps }: { steps: Step[] }) {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [currentStep, setCurrentStep] = useState(0);
  
  const isStepAccessible = (stepIndex: number) => {
    const step = steps[stepIndex];
    return step.dependencies.every(dep => completedSteps.has(dep));
  };
  
  return (
    <div>
      <div className="step-navigation">
        {steps.map((step, index) => (
          <button
            key={index}
            onClick={() => isStepAccessible(index) && setCurrentStep(index)}
            disabled={!isStepAccessible(index)}
            className={completedSteps.has(index) ? 'completed' : ''}
          >
            {step.label}
          </button>
        ))}
      </div>
      {steps[currentStep].component}
    </div>
  );
}
```

### Approval Chain

**Description**: Sequential or parallel approvals required before workflow can proceed. May include escalation rules and timeouts.

**Strengths**:
- Enforces business rules and compliance
- Provides audit trail
- Supports delegation and escalation
- Can handle complex approval hierarchies
- Good for financial and legal processes

**Weaknesses**:
- Can be slow (waiting for approvals)
- Complex to implement correctly
- Requires notification system
- May bottleneck workflows
- Difficult to handle edge cases (unavailable approvers)

**Best For**:
- Purchase orders and expenses
- Content publishing workflows
- Access requests
- Financial transactions
- Compliance-driven processes
- Multi-stakeholder decisions

**Avoid When**:
- Approvals are not required
- Process needs to be fast
- Simple single-person approval
- Low-stakes operations

**Implementation Example**:
```kotlin
@Entity
data class ApprovalWorkflow(
    @Id val id: String,
    val requestId: String,
    val currentStep: Int,
    val steps: List<ApprovalStep>,
    val status: ApprovalStatus
)

data class ApprovalStep(
    val approverId: String,
    val order: Int,
    val required: Boolean,
    val timeoutHours: Int?,
    val status: StepStatus
)

@Service
class ApprovalService {
    fun submitForApproval(requestId: String, steps: List<ApprovalStep>) {
        val workflow = ApprovalWorkflow(
            id = UUID.randomUUID().toString(),
            requestId = requestId,
            currentStep = 0,
            steps = steps,
            status = ApprovalStatus.PENDING
        )
        repository.save(workflow)
        notifyApprover(steps[0].approverId, workflow)
    }
    
    fun approve(workflowId: String, approverId: String) {
        val workflow = repository.findById(workflowId)
        val currentStep = workflow.steps[workflow.currentStep]
        
        if (currentStep.approverId != approverId) {
            throw UnauthorizedException()
        }
        
        if (workflow.currentStep < workflow.steps.size - 1) {
            workflow.currentStep++
            notifyApprover(workflow.steps[workflow.currentStep].approverId, workflow)
        } else {
            workflow.status = ApprovalStatus.APPROVED
            completeWorkflow(workflow)
        }
    }
}
```

### Checklist/Task List

**Description**: Independent tasks with no enforced order. Users can complete tasks in any sequence. Progress is tracked by completion percentage.

**Strengths**:
- Highly flexible
- Clear visual progress (checkmarks)
- Good for independent tasks
- Easy to understand
- Allows parallel work

**Weaknesses**:
- No guidance on order
- Can lead to incomplete workflows
- Harder to enforce dependencies
- May not suit sequential processes

**Best For**:
- Pre-flight checklists
- Setup tasks
- Onboarding checklists
- Project planning
- Quality assurance processes
- Independent configuration tasks

**Avoid When**:
- Tasks have strict dependencies
- Order matters significantly
- Process requires sequential validation
- Tasks are not independent

**Implementation Example**:
```tsx
function ChecklistWorkflow({ tasks }: { tasks: Task[] }) {
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  
  const progress = (completed.size / tasks.length) * 100;
  
  return (
    <div>
      <ProgressBar value={progress} />
      <p>{completed.size} of {tasks.length} tasks completed</p>
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          completed={completed.has(task.id)}
          onToggle={() => {
            setCompleted(prev => {
              const next = new Set(prev);
              if (next.has(task.id)) {
                next.delete(task.id);
              } else {
                next.add(task.id);
              }
              return next;
            });
          }}
        />
      ))}
    </div>
  );
}
```

### Background Job + Notification

**Description**: Long-running async operation that processes in the background. User receives notification when complete.

**Strengths**:
- Doesn't block user interface
- Good for long-running operations
- User can continue working
- Scalable (can queue jobs)
- Better user experience for slow operations

**Weaknesses**:
- No real-time progress (unless implemented separately)
- Requires notification system
- User may forget about operation
- Harder to handle failures
- Requires job queue infrastructure

**Best For**:
- Data exports
- Report generation
- Bulk imports
- File processing
- Long-running calculations
- Email sending
- Image/video processing

**Avoid When**:
- Operation completes quickly (<5 seconds)
- User needs immediate feedback
- Operation requires user input during processing
- Real-time progress is critical

**Implementation Example**:
```kotlin
@Service
class BackgroundJobService(
    private val jobQueue: JobQueue,
    private val notificationService: NotificationService
) {
    fun submitExportJob(userId: String, parameters: ExportParameters): String {
        val jobId = UUID.randomUUID().toString()
        
        jobQueue.enqueue(ExportJob(
            id = jobId,
            userId = userId,
            parameters = parameters,
            status = JobStatus.PENDING
        ))
        
        return jobId
    }
    
    @Async
    fun processExportJob(job: ExportJob) {
        try {
            job.status = JobStatus.PROCESSING
            jobRepository.save(job)
            
            val result = exportService.generateExport(job.parameters)
            
            job.status = JobStatus.COMPLETED
            job.resultUrl = result.url
            jobRepository.save(job)
            
            notificationService.notifyUser(job.userId, 
                "Your export is ready", 
                result.url
            )
        } catch (e: Exception) {
            job.status = JobStatus.FAILED
            job.errorMessage = e.message
            jobRepository.save(job)
            
            notificationService.notifyUser(job.userId,
                "Export failed",
                "Your export job encountered an error: ${e.message}"
            )
        }
    }
}
```

## Progress Indicators

### Stepper Component (Propulsion/MUI Stepper)

**Description**: Visual step indicators showing current position in a multi-step process. Typically displays step numbers, labels, and completion status.

**Strengths**:
- Clear visual representation of progress
- Shows both current and completed steps
- Standard component in design systems
- Accessible (can be made keyboard navigable)
- Works well for linear workflows

**Weaknesses**:
- Less effective for non-linear workflows
- Can be cluttered with many steps (>5-6)
- Doesn't show time estimates
- Not ideal for continuous progress

**Best For**:
- Linear wizards (3-6 steps ideal)
- Multi-step forms
- Onboarding flows
- Processes with distinct phases
- When step labels are meaningful

**Avoid When**:
- More than 7-8 steps (becomes cluttered)
- Non-linear workflows
- Continuous progress needed
- Steps are very similar (hard to distinguish)

**Implementation**:
```tsx
// MUI Stepper
<Stepper activeStep={currentStep} alternativeLabel>
  <Step completed={currentStep > 0}>
    <StepLabel>Personal Info</StepLabel>
  </Step>
  <Step completed={currentStep > 1}>
    <StepLabel>Payment</StepLabel>
  </Step>
  <Step completed={currentStep > 2}>
    <StepLabel>Review</StepLabel>
  </Step>
</Stepper>
```

### Progress Bar

**Description**: Percentage-based progress indicator showing completion as a filled bar. Can be determinate (known total) or indeterminate (unknown duration).

**Strengths**:
- Simple and universally understood
- Good for continuous progress
- Works for any number of items
- Can show percentage or count
- Lightweight UI component

**Weaknesses**:
- Doesn't show which specific steps are done
- Less informative than stepper
- Indeterminate bars can feel endless
- Doesn't indicate what's happening

**Best For**:
- Bulk operations
- File uploads/downloads
- Long-running processes
- When exact steps don't matter
- Continuous progress scenarios
- Background jobs with progress updates

**Avoid When**:
- Steps are distinct and important
- Users need to know specific step names
- Process has clear phases
- Few steps (stepper is better)

**Implementation**:
```tsx
function ProgressBar({ value, max = 100, label }: Props) {
  const percent = (value / max) * 100;
  
  return (
    <div>
      {label && <div>{label}</div>}
      <div className="progress-bar-container">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${percent}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
      <div>{Math.round(percent)}%</div>
    </div>
  );
}
```

### Task List with Checkmarks

**Description**: Checklist-style progress indicator where each task can be checked off independently. Shows completed vs remaining tasks.

**Strengths**:
- Very clear what's done and what's left
- Good for independent tasks
- Satisfying user experience (checking off items)
- Flexible order
- Easy to understand

**Weaknesses**:
- Doesn't show current focus
- Less effective for sequential processes
- Can be long for many tasks
- Doesn't indicate dependencies

**Best For**:
- Checklists
- Independent tasks
- Setup wizards
- Pre-flight checks
- Quality assurance processes
- Non-linear workflows

**Avoid When**:
- Tasks must be sequential
- Process is linear
- Many tasks (>10-15 becomes unwieldy)
- Tasks have complex dependencies

**Implementation**:
```tsx
function TaskList({ tasks }: { tasks: Task[] }) {
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  
  return (
    <div>
      <p>{completed.size} of {tasks.length} tasks completed</p>
      {tasks.map(task => (
        <label key={task.id} className="task-item">
          <input
            type="checkbox"
            checked={completed.has(task.id)}
            onChange={(e) => {
              setCompleted(prev => {
                const next = new Set(prev);
                if (e.target.checked) {
                  next.add(task.id);
                } else {
                  next.delete(task.id);
                }
                return next;
              });
            }}
          />
          <span className={completed.has(task.id) ? 'completed' : ''}>
            {task.label}
          </span>
        </label>
      ))}
    </div>
  );
}
```

### Status Badge/Timeline

**Description**: Event-based progress indicator showing status at each stage. Often used for approval workflows or status tracking.

**Strengths**:
- Good for event-driven processes
- Shows status at each stage
- Works well for approval chains
- Can show timestamps
- Clear status communication

**Weaknesses**:
- Less intuitive for step-by-step processes
- Can be verbose
- Requires more space
- May not show progress percentage

**Best For**:
- Approval workflows
- Order tracking
- Status updates
- Event-driven processes
- Multi-party workflows
- When timestamps matter

**Avoid When**:
- Simple linear wizard
- User-controlled steps
- Progress percentage is more important
- Process is not event-driven

**Implementation**:
```tsx
function StatusTimeline({ events }: { events: StatusEvent[] }) {
  return (
    <div className="timeline">
      {events.map((event, index) => (
        <div key={index} className="timeline-item">
          <div className={`status-badge ${event.status}`}>
            {event.status}
          </div>
          <div className="timeline-content">
            <p>{event.label}</p>
            {event.timestamp && (
              <span className="timestamp">
                {formatDate(event.timestamp)}
              </span>
            )}
            {event.actor && (
              <span className="actor">by {event.actor}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Bulk Operation Strategies

### Synchronous Batch

**Description**: Process all items in a single request. Server processes items sequentially or in parallel, returns when all complete.

**Strengths**:
- Simple to implement
- No job queue needed
- Immediate results
- Easier error handling
- Good for small batches

**Weaknesses**:
- Blocks request (timeout risk)
- Poor UX for large batches
- No progress updates
- Can't cancel mid-process
- Doesn't scale well

**Best For**:
- Small batches (<50 items)
- Fast operations (<1 second per item)
- When immediate results are required
- Simple operations
- Operations that must be atomic

**Avoid When**:
- Large batches (>100 items)
- Slow operations (>1 second per item)
- Operations may timeout
- Progress updates are needed
- User may need to cancel

**Implementation**:
```kotlin
@PostMapping("/bulk/delete")
fun bulkDelete(@RequestBody itemIds: List<String>): ResponseEntity<BulkResult> {
    val results = itemIds.map { id ->
        try {
            itemService.delete(id)
            ItemResult(id, status = "success")
        } catch (e: Exception) {
            ItemResult(id, status = "failed", error = e.message)
        }
    }
    
    return ResponseEntity.ok(BulkResult(
        total = itemIds.size,
        succeeded = results.filter { it.status == "success" },
        failed = results.filter { it.status == "failed" }
    ))
}
```

### Async Queue

**Description**: Queue items for background processing. Process in background, report progress via polling or WebSocket, notify on completion.

**Strengths**:
- Doesn't block request
- Scalable (can process across workers)
- Can show progress
- Can handle very large batches
- Better user experience

**Weaknesses**:
- More complex to implement
- Requires job queue infrastructure
- Requires progress tracking system
- Notification system needed
- Harder to handle failures

**Best For**:
- Large batches (>100 items)
- Slow operations (>1 second per item)
- Long-running processes
- When user can wait
- Operations that benefit from parallel processing

**Avoid When**:
- Small batches (<20 items)
- Immediate results required
- Operation is very fast
- No job queue infrastructure available
- Simple synchronous operation is sufficient

**Implementation**:
```kotlin
@Service
class AsyncBulkService(
    private val jobQueue: JobQueue,
    private val progressTracker: ProgressTracker
) {
    fun submitBulkOperation(operation: BulkOperation): String {
        val jobId = UUID.randomUUID().toString()
        
        jobQueue.enqueue(BulkJob(
            id = jobId,
            operation = operation,
            status = JobStatus.PENDING,
            totalItems = operation.itemIds.size
        ))
        
        return jobId
    }
    
    @Async
    fun processBulkJob(job: BulkJob) {
        job.status = JobStatus.PROCESSING
        jobRepository.save(job)
        
        job.operation.itemIds.forEachIndexed { index, itemId ->
            try {
                processItem(itemId, job.operation)
                progressTracker.updateProgress(job.id, index + 1, job.totalItems)
            } catch (e: Exception) {
                progressTracker.recordFailure(job.id, itemId, e.message)
            }
        }
        
        job.status = JobStatus.COMPLETED
        jobRepository.save(job)
        notificationService.notifyCompletion(job.id)
    }
}
```

### Streaming with Progress

**Description**: Process items and report progress per-item in real-time. Uses Server-Sent Events (SSE) or WebSocket for live updates.

**Strengths**:
- Real-time progress updates
- Best user experience
- Can show per-item status
- User sees progress immediately
- Can cancel mid-process

**Weaknesses**:
- Most complex to implement
- Requires WebSocket/SSE infrastructure
- Higher server resource usage
- More network overhead
- Requires connection management

**Best For**:
- When real-time feedback is critical
- User needs to see per-item progress
- Operations where user may want to cancel
- High-value operations
- When user is waiting and watching

**Avoid When**:
- Background processing is acceptable
- Simple batch is sufficient
- No WebSocket/SSE infrastructure
- Operation is very fast
- User doesn't need to watch progress

**Implementation**:
```kotlin
@RestController
class StreamingBulkController {
    @GetMapping("/bulk/{jobId}/stream", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
    fun streamProgress(@PathVariable jobId: String): SseEmitter {
        val emitter = SseEmitter(Long.MAX_VALUE)
        
        val job = jobRepository.findById(jobId)
        
        // Process items and send progress
        CompletableFuture.runAsync {
            job.itemIds.forEachIndexed { index, itemId ->
                try {
                    processItem(itemId)
                    emitter.send(SseEmitter.SseEventBuilder()
                        .data(ProgressEvent(
                            processed = index + 1,
                            total = job.itemIds.size,
                            currentItem = itemId,
                            status = "processing"
                        ))
                        .build())
                } catch (e: Exception) {
                    emitter.send(SseEmitter.SseEventBuilder()
                        .data(ProgressEvent(
                            processed = index + 1,
                            total = job.itemIds.size,
                            currentItem = itemId,
                            status = "failed",
                            error = e.message
                        ))
                        .build())
                }
            }
            emitter.complete()
        }
        
        return emitter
    }
}
```

## Workflow Engines

### Custom State Machine

**Description**: Hand-rolled state machine implementation using enums, switch statements, or simple state objects. Full control over logic.

**Strengths**:
- Full control over behavior
- No external dependencies
- Simple for basic workflows
- Easy to understand
- Lightweight

**Weaknesses**:
- Must implement all features yourself
- Can become complex for advanced workflows
- No built-in persistence
- Harder to maintain as complexity grows
- No visual modeling

**Best For**:
- Simple workflows (2-4 states)
- When full control is needed
- Minimal dependencies required
- Straightforward state transitions
- When workflow logic is unlikely to change

**Avoid When**:
- Complex workflows (>5 states, many transitions)
- Workflow logic changes frequently
- Need visual modeling
- Multiple workflows to maintain
- Need advanced features (timeouts, retries)

**Implementation**:
```kotlin
enum class WorkflowState {
    INITIAL, PROCESSING, APPROVED, REJECTED, COMPLETED
}

class SimpleWorkflowStateMachine {
    private var currentState = WorkflowState.INITIAL
    
    fun transition(event: WorkflowEvent): WorkflowState {
        currentState = when (currentState to event) {
            WorkflowState.INITIAL to WorkflowEvent.START -> WorkflowState.PROCESSING
            WorkflowState.PROCESSING to WorkflowEvent.APPROVE -> WorkflowState.APPROVED
            WorkflowState.PROCESSING to WorkflowEvent.REJECT -> WorkflowState.REJECTED
            WorkflowState.APPROVED to WorkflowEvent.COMPLETE -> WorkflowState.COMPLETED
            else -> throw IllegalStateException("Invalid transition: $currentState -> $event")
        }
        return currentState
    }
}
```

### Spring Statemachine

**Description**: Framework-backed state machine for Spring applications. Supports hierarchical states, regions, and event-driven transitions.

**Strengths**:
- Framework integration
- Event-driven architecture
- Supports complex state hierarchies
- Good Spring Boot support
- Type-safe state definitions

**Weaknesses**:
- Learning curve
- Can be verbose for simple workflows
- Requires Spring ecosystem
- Less flexible than custom solution
- Configuration can be complex

**Best For**:
- Spring Boot applications
- Event-driven workflows
- Complex state hierarchies
- When framework support is valuable
- Multiple workflows in same application

**Avoid When**:
- Non-Spring application
- Very simple workflows
- Need maximum flexibility
- Don't want framework dependency
- Workflow logic is very custom

**Implementation**: See Spring Boot section in best-practices.md

### Axon Sagas

**Description**: Distributed, event-sourced workflow orchestration using Axon Framework. Coordinates multiple aggregates across services.

**Strengths**:
- Distributed workflow support
- Event-sourced (full audit trail)
- Coordinates across microservices
- Handles long-running processes
- Built-in compensation (rollback)

**Weaknesses**:
- Requires Axon Framework
- Event sourcing complexity
- Steeper learning curve
- Overkill for simple workflows
- Requires event infrastructure

**Best For**:
- Microservices architectures
- Distributed workflows
- Event-sourced systems
- Long-running processes
- When compensation is needed
- Complex multi-service coordination

**Avoid When**:
- Monolithic application
- Simple workflows
- Not using event sourcing
- Don't need distributed coordination
- Want to avoid framework complexity

**Implementation**: See Axon Saga section in best-practices.md

### BPMN (Camunda/Flowable)

**Description**: Business Process Model and Notation engine. Visual workflow modeling, execution engine, and process management.

**Strengths**:
- Visual modeling (non-developers can create workflows)
- Industry standard (BPMN)
- Rich feature set (timers, gateways, etc.)
- Process versioning
- Built-in UI for process management

**Weaknesses**:
- Heavyweight solution
- Significant infrastructure requirements
- Learning curve for BPMN
- Can be overkill for simple workflows
- Requires separate process engine

**Best For**:
- Complex business processes
- When business users need to model workflows
- Processes that change frequently
- Need visual process management
- Enterprise process automation
- Compliance-heavy processes

**Avoid When**:
- Simple workflows
- Technical workflows (not business processes)
- Don't need visual modeling
- Want lightweight solution
- Processes are stable and don't change

**Implementation**:
```kotlin
// Camunda integration example
@Service
class CamundaWorkflowService(
    private val runtimeService: RuntimeService
) {
    fun startProcess(processKey: String, variables: Map<String, Any>): String {
        return runtimeService.startProcessInstanceByKey(processKey, variables)
            .processInstanceId
    }
    
    fun completeTask(taskId: String, variables: Map<String, Any>) {
        val taskService = processEngine.taskService
        taskService.complete(taskId, variables)
    }
}
```

## Recommendation Guidance

### Decision Matrix

When choosing workflow patterns and implementations, consider:

1. **Workflow Complexity**: Simple → Custom/Spring Statemachine, Complex → BPMN
2. **User Type**: Novice → Linear Wizard, Expert → Non-linear/Checklist
3. **Operation Size**: Small (<50) → Synchronous, Large → Async/Streaming
4. **Architecture**: Monolith → Custom/Spring, Microservices → Axon Saga
5. **Change Frequency**: Stable → Custom, Frequent → BPMN
6. **Progress Need**: None → Background Job, Some → Progress Bar, Real-time → Streaming

### Common Combinations

- **Onboarding Flow**: Linear Wizard + Stepper + Custom State Machine
- **Bulk Import**: Async Queue + Progress Bar + Spring Statemachine
- **Approval Process**: Approval Chain + Status Timeline + Axon Saga
- **Setup Wizard**: Non-linear Wizard + Checklist + Custom State Machine
- **Data Export**: Background Job + Notification + Async Queue

## Synergies

### With Notifications Experience
- Approval workflows require notification system
- Background jobs need completion notifications
- Workflow state changes should trigger notifications

### With Forms Experience
- Multi-step workflows often use multi-page forms
- Form validation integrates with workflow step validation
- Form state persistence aligns with workflow state persistence

### With Real-Time Experience
- Streaming bulk operations use WebSocket/SSE
- Real-time progress updates enhance workflow UX
- Collaborative workflows need real-time presence

### With Loading Experience
- Long-running workflows need loading states
- Progress indicators are part of loading patterns
- Skeleton screens can show workflow structure

## Evolution Triggers

Reconsider your workflow approach when:

1. **Workflow becomes too complex**: If custom state machine becomes hard to maintain, consider Spring Statemachine or BPMN
2. **Frequent workflow changes**: If workflows change often, BPMN visual modeling may be better
3. **Performance issues**: If synchronous batch times out, move to async queue
4. **User complaints about progress**: If users don't know where they are, add better progress indicators
5. **Scale requirements**: If moving to microservices, consider Axon Sagas for distributed workflows
6. **Business user needs**: If non-technical users need to modify workflows, BPMN becomes necessary
7. **Workflow failures increase**: May need better error handling, retries, or compensation logic
8. **Mobile usage grows**: Linear workflows work better on mobile than non-linear
