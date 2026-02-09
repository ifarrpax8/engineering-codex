# Workflows & Tasks — Best Practices

## Contents

- [Always Show Progress](#always-show-progress)
- [Make Workflows Resumable](#make-workflows-resumable)
- [Handle Partial Failures Gracefully](#handle-partial-failures-gracefully)
- [Provide Clear "What Happens Next"](#provide-clear-what-happens-next)
- [Allow Cancellation of In-Progress Operations](#allow-cancellation-of-in-progress-operations)
- [Undo Over Confirmation Dialogs](#undo-over-confirmation-dialogs)
- [Keep Workflows Linear Where Possible](#keep-workflows-linear-where-possible)
- [Time Estimates for Long Operations](#time-estimates-for-long-operations)
- [Stack-Specific Implementation](#stack-specific-implementation)
- [Accessibility in Workflows](#accessibility-in-workflows)
- [Bulk Operation UX](#bulk-operation-ux)

## Always Show Progress

Users need to know where they are in a workflow and how much work remains. Without progress indicators, users feel lost and uncertain.

### Visual Progress Indicators

**Required Elements**:
- Current step number: "Step 2 of 5"
- Progress percentage: "40% complete"
- Step labels (not just numbers): "Personal Info → Payment → Review"
- Visual progress bar or stepper component

**Implementation Example**:
```tsx
// React with MUI Stepper
import { Stepper, Step, StepLabel } from '@mui/material';

function WorkflowProgress({ currentStep, steps }) {
  return (
    <Stepper activeStep={currentStep} alternativeLabel>
      {steps.map((label, index) => (
        <Step key={label} completed={index < currentStep}>
          <StepLabel>{label}</StepLabel>
        </Step>
      ))}
    </Stepper>
  );
}
```

```vue
<!-- Vue 3 with Propulsion Stepper -->
<template>
  <Stepper :active-step="currentStep" :steps="stepLabels" />
  <div class="progress-info">
    Step {{ currentStep + 1 }} of {{ totalSteps }} ({{ progressPercent }}% complete)
  </div>
</template>
```

### Progress for Long-Running Tasks

For operations that take time (file uploads, data processing, bulk operations):

**Show**:
- Percentage complete (if determinable)
- Items processed: "Processing 45 of 100 items..."
- Estimated time remaining: "About 2 minutes remaining"
- Current operation: "Validating customer data..."

**Implementation**:
```typescript
interface TaskProgress {
  current: number;
  total: number;
  currentOperation: string;
  estimatedSecondsRemaining?: number;
}

function ProgressDisplay({ progress }: { progress: TaskProgress }) {
  const percent = (progress.current / progress.total) * 100;
  const timeRemaining = progress.estimatedSecondsRemaining 
    ? `About ${Math.ceil(progress.estimatedSecondsRemaining / 60)} minutes remaining`
    : '';
  
  return (
    <div>
      <ProgressBar value={percent} />
      <p>{progress.currentOperation}</p>
      <p>{progress.current} of {progress.total} items processed</p>
      {timeRemaining && <p>{timeRemaining}</p>}
    </div>
  );
}
```

## Make Workflows Resumable

Users shouldn't lose progress if they navigate away, close their browser, or encounter an error. Save workflow state server-side and allow users to resume.

### Server-Side State Persistence

**Pattern**: Save workflow state after each step completion, keyed by workflow ID and user.

**Spring Boot Implementation**:
```kotlin
@Entity
data class WorkflowState(
    @Id val id: String,
    val userId: String,
    val workflowType: String,
    val currentStep: Int,
    val data: String, // JSON serialized form data
    val createdAt: Instant,
    val updatedAt: Instant,
    val expiresAt: Instant = Instant.now().plus(7, ChronoUnit.DAYS)
)

@Repository
interface WorkflowStateRepository : JpaRepository<WorkflowState, String> {
    fun findByUserIdAndWorkflowType(userId: String, workflowType: String): WorkflowState?
}

@Service
class WorkflowStateService(
    private val repository: WorkflowStateRepository
) {
    fun saveState(userId: String, workflowType: String, step: Int, data: Any) {
        val state = repository.findByUserIdAndWorkflowType(userId, workflowType)
            ?.copy(
                currentStep = step,
                data = objectMapper.writeValueAsString(data),
                updatedAt = Instant.now()
            )
            ?: WorkflowState(
                id = UUID.randomUUID().toString(),
                userId = userId,
                workflowType = workflowType,
                currentStep = step,
                data = objectMapper.writeValueAsString(data),
                createdAt = Instant.now(),
                updatedAt = Instant.now()
            )
        repository.save(state)
    }
    
    fun getState(userId: String, workflowType: String): WorkflowState? {
        return repository.findByUserIdAndWorkflowType(userId, workflowType)
            ?.takeIf { it.expiresAt.isAfter(Instant.now()) }
    }
}
```

### "Continue Where You Left Off" UI

**Pattern**: Detect existing workflow state and offer to resume.

**Vue 3 Implementation**:
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useWorkflowStore } from '@/stores/workflow';

const workflowStore = useWorkflowStore();
const hasExistingWorkflow = ref(false);
const existingWorkflow = ref(null);

onMounted(async () => {
  const state = await workflowStore.checkForExistingWorkflow('onboarding');
  if (state) {
    hasExistingWorkflow.value = true;
    existingWorkflow.value = state;
  }
});

function resumeWorkflow() {
  workflowStore.resumeWorkflow(existingWorkflow.value);
  router.push(`/onboarding/step/${existingWorkflow.value.currentStep}`);
}

function startFresh() {
  workflowStore.clearWorkflow('onboarding');
  router.push('/onboarding/step/1');
}
</script>

<template>
  <div v-if="hasExistingWorkflow" class="resume-banner">
    <p>You have an incomplete workflow. Last saved: {{ formatDate(existingWorkflow.updatedAt) }}</p>
    <button @click="resumeWorkflow">Continue where you left off</button>
    <button @click="startFresh">Start over</button>
  </div>
</template>
```

**React Implementation**:
```tsx
function OnboardingPage() {
  const [hasExistingWorkflow, setHasExistingWorkflow] = useState(false);
  const [existingState, setExistingState] = useState(null);
  
  useEffect(() => {
    checkForExistingWorkflow().then(state => {
      if (state) {
        setHasExistingWorkflow(true);
        setExistingState(state);
      }
    });
  }, []);
  
  const handleResume = () => {
    resumeWorkflow(existingState);
    navigate(`/onboarding/step/${existingState.currentStep}`);
  };
  
  return (
    <>
      {hasExistingWorkflow && (
        <Alert severity="info">
          <AlertTitle>Continue where you left off?</AlertTitle>
          Last saved: {formatDate(existingState.updatedAt)}
          <Button onClick={handleResume}>Resume</Button>
          <Button onClick={startFresh}>Start Over</Button>
        </Alert>
      )}
      {/* Rest of onboarding flow */}
    </>
  );
}
```

### Auto-Save During Workflow

**Pattern**: Save state automatically after each step completion (debounced).

```typescript
// Vue 3 composable
export function useWorkflowAutoSave(workflowId: string, workflowData: Ref<any>) {
  const saveWorkflowState = useDebounceFn(async (step: number, data: any) => {
    await api.post(`/workflows/${workflowId}/state`, {
      step,
      data,
      timestamp: Date.now()
    });
  }, 1000);
  
  watch(workflowData, (newData) => {
    saveWorkflowState(currentStep.value, newData);
  }, { deep: true });
}
```

## Handle Partial Failures Gracefully

In bulk operations, some items may succeed while others fail. Show what succeeded, what failed, and allow retry of just the failures.

### Failure Reporting Pattern

**Show**:
- Total items processed
- Success count with list
- Failure count with list and error messages
- "Retry Failed Items" button

**Implementation**:
```tsx
interface BulkOperationResult {
  total: number;
  succeeded: Array<{ id: string; name: string }>;
  failed: Array<{ id: string; name: string; error: string }>;
}

function BulkOperationResult({ result, onRetryFailed }: {
  result: BulkOperationResult;
  onRetryFailed: (failedIds: string[]) => void;
}) {
  return (
    <div>
      <h3>Operation Complete</h3>
      <p>{result.total} items processed</p>
      
      {result.succeeded.length > 0 && (
        <div>
          <h4>✓ Succeeded ({result.succeeded.length})</h4>
          <ul>
            {result.succeeded.map(item => (
              <li key={item.id}>{item.name}</li>
            ))}
          </ul>
        </div>
      )}
      
      {result.failed.length > 0 && (
        <div>
          <h4>✗ Failed ({result.failed.length})</h4>
          <ul>
            {result.failed.map(item => (
              <li key={item.id}>
                {item.name}: {item.error}
              </li>
            ))}
          </ul>
          <Button onClick={() => onRetryFailed(result.failed.map(f => f.id))}>
            Retry Failed Items
          </Button>
        </div>
      )}
    </div>
  );
}
```

**Spring Boot Backend**:
```kotlin
data class BulkOperationResult(
    val total: Int,
    val succeeded: List<ItemResult>,
    val failed: List<FailedItem>
)

data class ItemResult(val id: String, val name: String)
data class FailedItem(val id: String, val name: String, val error: String)

@Service
class BulkOperationService {
    fun processBulk(items: List<String>): BulkOperationResult {
        val succeeded = mutableListOf<ItemResult>()
        val failed = mutableListOf<FailedItem>()
        
        items.forEach { itemId ->
            try {
                val item = processItem(itemId)
                succeeded.add(ItemResult(itemId, item.name))
            } catch (e: Exception) {
                failed.add(FailedItem(itemId, itemId, e.message ?: "Unknown error"))
            }
        }
        
        return BulkOperationResult(
            total = items.size,
            succeeded = succeeded,
            failed = failed
        )
    }
}
```

## Provide Clear "What Happens Next"

At every step, users should know what action to take next. Avoid ambiguous states where users don't know if they're done or what to do.

### Explicit Next Actions

**Pattern**: Always show a clear primary action button with descriptive text.

**Good Examples**:
- "Continue to Payment" (not just "Next")
- "Review and Submit Order" (not just "Submit")
- "Save Draft and Continue Later" (not just "Save")

**Implementation**:
```vue
<template>
  <div class="workflow-step">
    <h2>Step {{ currentStep }}: {{ stepTitle }}</h2>
    
    <!-- Step content -->
    <form @submit.prevent="handleNext">
      <!-- Form fields -->
    </form>
    
    <div class="workflow-actions">
      <Button v-if="currentStep > 0" @click="goToPreviousStep">
        Back
      </Button>
      <Button 
        type="primary" 
        @click="handleNext"
        :disabled="!isStepValid"
      >
        {{ nextButtonLabel }}
      </Button>
      <Button variant="text" @click="saveDraft">
        Save Draft
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
const nextButtonLabels = {
  1: 'Continue to Payment Details',
  2: 'Continue to Shipping',
  3: 'Review Order',
  4: 'Place Order'
};

const nextButtonLabel = computed(() => 
  nextButtonLabels[currentStep.value] || 'Next'
);
</script>
```

### Completion States

**Pattern**: Clearly indicate when a workflow is complete.

```tsx
function WorkflowComplete({ workflowType }: { workflowType: string }) {
  return (
    <div className="workflow-complete">
      <CheckCircleIcon className="success-icon" />
      <h2>Workflow Complete!</h2>
      <p>Your {workflowType} has been successfully processed.</p>
      <div className="next-actions">
        <Button href="/dashboard">Go to Dashboard</Button>
        <Button href="/workflows/new">Start Another</Button>
      </div>
    </div>
  );
}
```

## Allow Cancellation of In-Progress Operations

Users should be able to cancel operations that are in progress, with appropriate confirmation for destructive actions.

### Cancellation Pattern

**For Non-Destructive Operations**:
- Show "Cancel" button immediately
- No confirmation needed
- State can be restored if user changes mind

**For Destructive Operations**:
- Show confirmation dialog: "Are you sure? This action cannot be undone."
- Explain consequences clearly
- Require explicit confirmation

**Implementation**:
```tsx
function LongRunningTask({ onCancel }: { onCancel: () => void }) {
  const [isCancelling, setIsCancelling] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  
  const handleCancelClick = () => {
    if (isDestructiveOperation) {
      setShowConfirm(true);
    } else {
      onCancel();
    }
  };
  
  const handleConfirmCancel = () => {
    setIsCancelling(true);
    onCancel();
  };
  
  return (
    <>
      <div className="task-progress">
        {/* Progress display */}
        <Button onClick={handleCancelClick} disabled={isCancelling}>
          Cancel
        </Button>
      </div>
      
      {showConfirm && (
        <Dialog open onClose={() => setShowConfirm(false)}>
          <DialogTitle>Cancel Operation?</DialogTitle>
          <DialogContent>
            This will stop the current operation. Any progress will be lost.
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowConfirm(false)}>Continue</Button>
            <Button onClick={handleConfirmCancel} color="error">
              Cancel Operation
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </>
  );
}
```

**Spring Boot Cancellation**:
```kotlin
@Service
class CancellableTaskService {
    private val cancellations = ConcurrentHashMap<String, AtomicBoolean>()
    
    @Async
    fun processTask(taskId: String, items: List<String>): CompletableFuture<TaskResult> {
        val cancelled = cancellations.computeIfAbsent(taskId) { AtomicBoolean(false) }
        
        return CompletableFuture.supplyAsync {
            items.mapNotNull { item ->
                if (cancelled.get()) {
                    throw TaskCancelledException("Task $taskId was cancelled")
                }
                processItem(item)
            }.let { TaskResult(it) }
        }
    }
    
    fun cancelTask(taskId: String) {
        cancellations[taskId]?.set(true)
    }
}
```

## Undo Over Confirmation Dialogs

For non-destructive actions, prefer undo functionality over confirmation dialogs. Let users act quickly, then provide undo if they made a mistake.

### Undo Pattern

**When to Use Undo**:
- Deleting items (non-critical)
- Archiving items
- Clearing selections
- Bulk operations

**When to Use Confirmation**:
- Permanent deletion (cannot be recovered)
- Financial transactions
- Irreversible actions

**Implementation**:
```tsx
function useUndo() {
  const [undoStack, setUndoStack] = useState<Array<() => void>>([]);
  const [showUndo, setShowUndo] = useState(false);
  
  const performWithUndo = (action: () => void, undo: () => void) => {
    action();
    setUndoStack(prev => [...prev, undo]);
    setShowUndo(true);
    
    // Auto-hide undo after 5 seconds
    setTimeout(() => {
      setShowUndo(false);
      setUndoStack(prev => prev.slice(0, -1));
    }, 5000);
  };
  
  const handleUndo = () => {
    const undo = undoStack[undoStack.length - 1];
    if (undo) {
      undo();
      setUndoStack(prev => prev.slice(0, -1));
      setShowUndo(false);
    }
  };
  
  return { performWithUndo, handleUndo, showUndo };
}

function ItemList({ items, onDelete }: Props) {
  const { performWithUndo, handleUndo, showUndo } = useUndo();
  
  const handleDelete = (itemId: string) => {
    const item = items.find(i => i.id === itemId);
    performWithUndo(
      () => onDelete(itemId),
      () => onRestore(item) // Restore function
    );
  };
  
  return (
    <>
      <Snackbar 
        open={showUndo} 
        message="Item deleted"
        action={<Button onClick={handleUndo}>Undo</Button>}
      />
      {/* Item list */}
    </>
  );
}
```

**Vue 3 Implementation**:
```vue
<script setup lang="ts">
import { ref } from 'vue';

const undoStack = ref<Array<() => void>>([]);
const showUndo = ref(false);

function performWithUndo(action: () => void, undo: () => void) {
  action();
  undoStack.value.push(undo);
  showUndo.value = true;
  
  setTimeout(() => {
    showUndo.value = false;
    undoStack.value.pop();
  }, 5000);
}

function handleUndo() {
  const undo = undoStack.value[undoStack.value.length - 1];
  if (undo) {
    undo();
    undoStack.value.pop();
    showUndo.value = false;
  }
}
</script>

<template>
  <Snackbar v-model="showUndo" message="Action completed">
    <Button @click="handleUndo">Undo</Button>
  </Snackbar>
</template>
```

## Keep Workflows Linear Where Possible

Linear workflows (sequential steps) are easier to understand and navigate than non-linear workflows. Use non-linear patterns only when necessary.

### When to Use Linear Workflows

**Best For**:
- Onboarding flows
- Checkout processes
- Multi-step forms
- Guided setup wizards

**Benefits**:
- Clear progression
- Easier to implement
- Less cognitive load
- Better mobile experience

### When Non-Linear Makes Sense

**Use Non-Linear When**:
- Steps are independent (checklist)
- Users need to jump between sections
- Steps can be completed in any order
- Complex workflows with conditional paths

**Implementation**:
```tsx
// Linear workflow
function LinearWorkflow({ steps }: { steps: Step[] }) {
  const [currentStep, setCurrentStep] = useState(0);
  
  const canGoNext = steps[currentStep].isValid;
  const canGoBack = currentStep > 0;
  
  return (
    <div>
      <Stepper activeStep={currentStep} steps={steps} />
      {steps[currentStep].component}
      <div>
        {canGoBack && <Button onClick={() => setCurrentStep(s => s - 1)}>Back</Button>}
        {canGoNext && <Button onClick={() => setCurrentStep(s => s + 1)}>Next</Button>}
      </div>
    </div>
  );
}

// Non-linear workflow (checklist)
function ChecklistWorkflow({ tasks }: { tasks: Task[] }) {
  const [completed, setCompleted] = useState<Set<string>>(new Set());
  
  return (
    <div>
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

## Time Estimates for Long Operations

Provide time estimates for operations that take more than a few seconds. "This may take 2-5 minutes" is better than an indefinite spinner.

### Estimating Time

**Patterns**:
- Use historical data if available
- Provide ranges: "2-5 minutes" (more honest than exact)
- Update estimates as operation progresses
- Show worst-case: "Up to 10 minutes"

**Implementation**:
```typescript
interface TimeEstimate {
  minSeconds: number;
  maxSeconds: number;
  currentEstimate?: number; // Updated based on progress
}

function useTimeEstimate(operationType: string, itemCount: number): TimeEstimate {
  // Base estimates per operation type
  const estimates = {
    'bulk-import': { perItem: 2, base: 30 },
    'data-export': { perItem: 1, base: 60 },
    'report-generation': { perItem: 0.5, base: 45 }
  };
  
  const estimate = estimates[operationType];
  const totalSeconds = estimate.base + (estimate.perItem * itemCount);
  
  return {
    minSeconds: Math.floor(totalSeconds * 0.7),
    maxSeconds: Math.ceil(totalSeconds * 1.3)
  };
}

function LongOperationDisplay({ operationType, itemCount, progress }: Props) {
  const estimate = useTimeEstimate(operationType, itemCount);
  const [elapsed, setElapsed] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(s => s + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);
  
  const remaining = progress.currentEstimate 
    ? Math.max(0, progress.currentEstimate - elapsed)
    : estimate.maxSeconds - elapsed;
  
  return (
    <div>
      <ProgressBar value={progress.percent} />
      <p>{progress.currentOperation}</p>
      <p>
        Estimated time remaining: {formatDuration(remaining)}
        {!progress.currentEstimate && ` (${formatDuration(estimate.minSeconds)} - ${formatDuration(estimate.maxSeconds)})`}
      </p>
    </div>
  );
}
```

## Stack-Specific Implementation

### Vue 3

**Workflow Composable**:
```typescript
// composables/useWorkflow.ts
export function useWorkflow<T>(workflowId: string, initialData: T) {
  const currentStep = ref(0);
  const workflowData = ref<T>(initialData);
  const isValid = ref(false);
  
  const workflowStore = useWorkflowStore();
  
  // Auto-save on step completion
  watch([currentStep, workflowData], ([step, data]) => {
    workflowStore.saveWorkflowState(workflowId, step, data);
  }, { deep: true });
  
  const goToNextStep = () => {
    if (isValid.value) {
      currentStep.value++;
    }
  };
  
  const goToPreviousStep = () => {
    if (currentStep.value > 0) {
      currentStep.value--;
    }
  };
  
  return {
    currentStep,
    workflowData,
    isValid,
    goToNextStep,
    goToPreviousStep
  };
}
```

**Pinia Store for Workflow Progress**:
```typescript
// stores/workflow.ts
export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    workflows: {} as Record<string, WorkflowState>
  }),
  
  actions: {
    async saveWorkflowState(workflowId: string, step: number, data: any) {
      await api.post(`/workflows/${workflowId}/state`, { step, data });
      this.workflows[workflowId] = { step, data, updatedAt: new Date() };
    },
    
    async checkForExistingWorkflow(workflowId: string) {
      const state = await api.get(`/workflows/${workflowId}/state`);
      if (state) {
        this.workflows[workflowId] = state;
        return state;
      }
      return null;
    }
  }
});
```

**Stepper Component Pattern**:
```vue
<!-- components/WorkflowStepper.vue -->
<template>
  <div class="workflow-stepper">
    <div 
      v-for="(step, index) in steps" 
      :key="index"
      class="step"
      :class="{ active: index === currentStep, completed: index < currentStep }"
    >
      <div class="step-number">{{ index + 1 }}</div>
      <div class="step-label">{{ step.label }}</div>
    </div>
  </div>
</template>
```

### React

**Workflow Reducer**:
```tsx
type WorkflowAction =
  | { type: 'NEXT_STEP' }
  | { type: 'PREVIOUS_STEP' }
  | { type: 'SET_STEP'; step: number }
  | { type: 'UPDATE_DATA'; data: any }
  | { type: 'SET_VALIDITY'; isValid: boolean };

interface WorkflowState {
  currentStep: number;
  data: any;
  isValid: boolean;
}

function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case 'NEXT_STEP':
      return { ...state, currentStep: state.currentStep + 1 };
    case 'PREVIOUS_STEP':
      return { ...state, currentStep: Math.max(0, state.currentStep - 1) };
    case 'SET_STEP':
      return { ...state, currentStep: action.step };
    case 'UPDATE_DATA':
      return { ...state, data: { ...state.data, ...action.data } };
    case 'SET_VALIDITY':
      return { ...state, isValid: action.isValid };
    default:
      return state;
  }
}

function useWorkflow(initialData: any) {
  const [state, dispatch] = useReducer(workflowReducer, {
    currentStep: 0,
    data: initialData,
    isValid: false
  });
  
  return {
    ...state,
    nextStep: () => dispatch({ type: 'NEXT_STEP' }),
    previousStep: () => dispatch({ type: 'PREVIOUS_STEP' }),
    setStep: (step: number) => dispatch({ type: 'SET_STEP', step }),
    updateData: (data: any) => dispatch({ type: 'UPDATE_DATA', data }),
    setValidity: (isValid: boolean) => dispatch({ type: 'SET_VALIDITY', isValid })
  };
}
```

**Step Context Provider**:
```tsx
const WorkflowContext = createContext<WorkflowContextValue | null>(null);

function WorkflowProvider({ children, workflowId }: Props) {
  const workflow = useWorkflow({});
  
  useEffect(() => {
    // Auto-save on changes
    saveWorkflowState(workflowId, workflow.currentStep, workflow.data);
  }, [workflow.currentStep, workflow.data]);
  
  return (
    <WorkflowContext.Provider value={workflow}>
      {children}
    </WorkflowContext.Provider>
  );
}

function useWorkflowContext() {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflowContext must be used within WorkflowProvider');
  }
  return context;
}
```

**MUI Stepper Component**:
```tsx
import { Stepper, Step, StepLabel, StepContent } from '@mui/material';

function WorkflowStepper({ steps, currentStep }: Props) {
  return (
    <Stepper activeStep={currentStep} orientation="vertical">
      {steps.map((step, index) => (
        <Step key={step.label} completed={index < currentStep}>
          <StepLabel>{step.label}</StepLabel>
          <StepContent>{step.content}</StepContent>
        </Step>
      ))}
    </Stepper>
  );
}
```

### Spring Boot

**Spring Statemachine for State Transitions**:
```kotlin
enum class WorkflowState {
    INITIAL, STEP_1, STEP_2, STEP_3, COMPLETED, CANCELLED
}

enum class WorkflowEvent {
    NEXT, PREVIOUS, CANCEL, COMPLETE
}

@Configuration
@EnableStateMachine
class WorkflowStateMachineConfig : StateMachineConfigurerAdapter<WorkflowState, WorkflowEvent>() {
    override fun configure(config: StateMachineStateConfigurer<WorkflowState, WorkflowEvent>) {
        config
            .withStates()
            .initial(WorkflowState.INITIAL)
            .states(enumSetOf(WorkflowState.STEP_1, WorkflowState.STEP_2, WorkflowState.STEP_3))
            .end(WorkflowState.COMPLETED)
            .end(WorkflowState.CANCELLED)
    }
    
    override fun configure(transitions: StateMachineTransitionConfigurer<WorkflowState, WorkflowEvent>) {
        transitions
            .withExternal()
            .source(WorkflowState.INITIAL).target(WorkflowState.STEP_1)
            .event(WorkflowEvent.NEXT)
            .and()
            .withExternal()
            .source(WorkflowState.STEP_1).target(WorkflowState.STEP_2)
            .event(WorkflowEvent.NEXT)
            // ... more transitions
    }
}

@Service
class WorkflowService(
    private val stateMachine: StateMachine<WorkflowState, WorkflowEvent>
) {
    fun advanceStep(): WorkflowState {
        stateMachine.sendEvent(WorkflowEvent.NEXT)
        return stateMachine.state.id
    }
}
```

**@Async for Long Tasks**:
```kotlin
@Service
class AsyncWorkflowService {
    @Async
    fun processLongTask(taskId: String, items: List<String>): CompletableFuture<TaskResult> {
        return CompletableFuture.supplyAsync {
            val results = items.map { processItem(it) }
            TaskResult(results)
        }
    }
    
    fun getTaskStatus(taskId: String): TaskStatus {
        // Check Redis or database for task status
        return taskStatusRepository.findByTaskId(taskId)
    }
}

@Configuration
@EnableAsync
class AsyncConfig : AsyncConfigurer {
    override fun getAsyncExecutor(): Executor {
        val executor = ThreadPoolTaskExecutor()
        executor.corePoolSize = 4
        executor.maxPoolSize = 8
        executor.queueCapacity = 100
        executor.setThreadNamePrefix("workflow-async-")
        executor.initialize()
        return executor
    }
}
```

**Axon Saga for Distributed Workflows**:
```kotlin
@Saga
class OrderWorkflowSaga {
    @Autowired
    lateinit var commandGateway: CommandGateway
    
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    fun handle(event: OrderCreatedEvent) {
        commandGateway.send(CreatePaymentCommand(event.orderId, event.amount))
    }
    
    @SagaEventHandler(associationProperty = "orderId")
    fun handle(event: PaymentProcessedEvent) {
        commandGateway.send(CreateShipmentCommand(event.orderId))
    }
    
    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    fun handle(event: ShipmentCreatedEvent) {
        // Workflow complete
    }
}
```

**CompletableFuture for Async Results**:
```kotlin
@Service
class WorkflowExecutionService {
    fun executeWorkflow(workflowId: String, data: WorkflowData): CompletableFuture<WorkflowResult> {
        return CompletableFuture
            .supplyAsync { validateInput(data) }
            .thenCompose { validatedData ->
                CompletableFuture.allOf(
                    step1(validatedData),
                    step2(validatedData)
                ).thenApply { 
                    WorkflowResult(success = true)
                }
            }
            .exceptionally { ex ->
                WorkflowResult(success = false, error = ex.message)
            }
    }
}
```

## Accessibility in Workflows

### Progress Announcements

**Use aria-live regions** to announce progress changes to screen readers:

```tsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  Step {currentStep + 1} of {totalSteps}: {stepLabels[currentStep]}
</div>
```

```vue
<div aria-live="polite" aria-atomic="true" class="sr-only">
  Step {{ currentStep + 1 }} of {{ totalSteps }}: {{ stepLabels[currentStep] }}
</div>
```

### Keyboard-Navigable Step Indicators

**Pattern**: Allow keyboard navigation between steps (if non-linear):

```tsx
function KeyboardNavigableStepper({ steps, currentStep, onStepClick }: Props) {
  return (
    <nav role="navigation" aria-label="Workflow steps">
      {steps.map((step, index) => (
        <button
          key={index}
          onClick={() => onStepClick(index)}
          aria-current={index === currentStep ? 'step' : undefined}
          disabled={index > currentStep && !isStepAccessible(step)}
        >
          <span className="step-number">{index + 1}</span>
          <span className="step-label">{step.label}</span>
        </button>
      ))}
    </nav>
  );
}
```

### Focus Management Between Steps

**Pattern**: Move focus to the first input of the new step when advancing:

```tsx
function WorkflowStep({ step, onNext }: Props) {
  const firstInputRef = useRef<HTMLInputElement>(null);
  
  useEffect(() => {
    // Focus first input when step becomes active
    firstInputRef.current?.focus();
  }, [step.id]);
  
  return (
    <div>
      <input ref={firstInputRef} />
      {/* Other fields */}
    </div>
  );
}
```

### Meaningful Step Labels

**Avoid**: "Step 1", "Step 2", "Step 3"

**Use**: "Personal Information", "Payment Details", "Review Order"

```tsx
<Stepper activeStep={currentStep}>
  <Step>
    <StepLabel>Personal Information</StepLabel>
  </Step>
  <Step>
    <StepLabel>Payment Details</StepLabel>
  </Step>
  <Step>
    <StepLabel>Review Order</StepLabel>
  </Step>
</Stepper>
```

## Bulk Operation UX

### Show Count of Selected Items

**Pattern**: Always show how many items are selected for bulk operations:

```tsx
function BulkActionBar({ selectedCount, onBulkAction }: Props) {
  return (
    <div className="bulk-action-bar">
      <span>{selectedCount} items selected</span>
      <Button onClick={() => onBulkAction('delete')}>
        Delete Selected
      </Button>
      <Button onClick={() => onBulkAction('archive')}>
        Archive Selected
      </Button>
    </div>
  );
}
```

### Preview Before Execute

**Pattern**: Show what will happen before executing bulk operations:

```tsx
function BulkDeletePreview({ items, onConfirm, onCancel }: Props) {
  return (
    <Dialog open>
      <DialogTitle>Delete {items.length} items?</DialogTitle>
      <DialogContent>
        <p>The following items will be deleted:</p>
        <ul>
          {items.slice(0, 10).map(item => (
            <li key={item.id}>{item.name}</li>
          ))}
          {items.length > 10 && <li>...and {items.length - 10} more</li>}
        </ul>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={onConfirm} color="error">Delete</Button>
      </DialogActions>
    </Dialog>
  );
}
```

### Progress During Execution

**Pattern**: Show real-time progress as items are processed:

```tsx
function BulkOperationProgress({ total, processed, succeeded, failed }: Props) {
  const percent = (processed / total) * 100;
  
  return (
    <div>
      <ProgressBar value={percent} />
      <p>Processing {processed} of {total} items...</p>
      {succeeded > 0 && <p>✓ {succeeded} succeeded</p>}
      {failed > 0 && <p>✗ {failed} failed</p>}
    </div>
  );
}
```

### Summary After Completion

**Pattern**: Show comprehensive summary with ability to retry failures:

```tsx
function BulkOperationSummary({ result }: { result: BulkOperationResult }) {
  return (
    <div>
      <h3>Operation Complete</h3>
      <div>
        <p>Total: {result.total}</p>
        <p className="success">Succeeded: {result.succeeded.length}</p>
        {result.failed.length > 0 && (
          <>
            <p className="error">Failed: {result.failed.length}</p>
            <Button onClick={() => retryFailed(result.failed)}>
              Retry Failed Items
            </Button>
            <details>
              <summary>View Failed Items</summary>
              <ul>
                {result.failed.map(item => (
                  <li key={item.id}>
                    {item.name}: {item.error}
                  </li>
                ))}
              </ul>
            </details>
          </>
        )}
      </div>
    </div>
  );
}
```
