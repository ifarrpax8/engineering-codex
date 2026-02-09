# Workflows & Tasks -- Product Perspective

## Contents

- [Task Completion Patterns](#task-completion-patterns)
- [Workflow Presentation Patterns](#workflow-presentation-patterns)
- [Progress Indicators](#progress-indicators)
- [Bulk Actions](#bulk-actions)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## Task Completion Patterns

### Single-Action Tasks

Simple, atomic tasks that complete immediately upon user action. Examples include:
- Approving a single invoice
- Deleting a single record
- Sending a notification

These require minimal UI complexity but should still provide feedback (success message, undo option).

### Multi-Step Workflows

Complex processes broken into discrete steps, such as:
- Onboarding flows (account setup → verification → preferences)
- Order processing (cart → shipping → payment → confirmation)
- Configuration wizards (step 1: basic info → step 2: advanced settings → step 3: review)

Each step should be clearly defined, with the ability to navigate backward and save progress.

### Approval Chains

Sequential or parallel approval processes where multiple stakeholders must approve before proceeding:
- **Sequential**: Manager → Director → VP (each must approve in order)
- **Parallel**: Any 2 of 3 approvers can approve (faster, but requires coordination)
- **Hybrid**: Manager approval required, then any Director can approve

Key considerations: delegation, escalation, timeouts, and notification strategies.

### Async Long-Running Tasks

Operations that take significant time (seconds to minutes) and run in the background:
- Data exports (generating large CSV files)
- Bulk imports (processing thousands of records)
- Report generation (complex analytics)
- Integration syncs (syncing with external systems)

These require progress tracking, cancellation support, and completion notifications.

## Workflow Presentation Patterns

### Wizard Pattern

**When to use**: Complex multi-step processes where users need guidance, steps have dependencies, or the process is infrequent.

**Characteristics**:
- Linear progression through steps
- Clear "Next" and "Back" navigation
- Progress indicator showing current step
- Often modal or full-page overlay

**Example**: Account setup wizard, complex configuration flows.

### Inline Pattern

**When to use**: Simple multi-step processes where context is important, or when steps are closely related.

**Characteristics**:
- Steps appear in the same view (expandable sections, tabs, or accordion)
- Users can see all steps or jump between them
- Less guidance, more flexibility

**Example**: Form with multiple sections, settings page with tabs.

### Step-by-Step Pattern

**When to use**: Processes where users need to complete steps in order but may need to reference previous steps.

**Characteristics**:
- Steps are visible but disabled until prerequisites are met
- Can review completed steps
- Clear indication of what's required for each step

**Example**: Checklist-style onboarding, guided setup with prerequisites.

## Progress Indicators

### Determinate Progress

Shows exact position in a workflow:
- **Step-based**: "Step 2 of 5" or "3/5 complete"
- **Percentage**: "60% complete"
- **Item-based**: "Processing item 150 of 500"

Best for workflows with a known number of steps or items.

### Indeterminate Progress

Shows that work is happening but not how much remains:
- Spinner or loading animation
- "Processing..." message
- Pulsing progress bar

Use when the duration is unknown or highly variable.

### Hybrid Approach

Combine determinate and indeterminate:
- "Step 2 of 5" (determinate) + "Validating data..." (indeterminate within step)
- Overall progress bar + current step description

Provides both macro and micro progress visibility.

## Bulk Actions

### Selection Patterns

- **Individual selection**: Checkboxes per item
- **Select all**: Toggle to select/deselect all visible items
- **Select by filter**: Select all items matching current filter criteria
- **Range selection**: Shift-click to select ranges

### Batch Operations

Common bulk operations:
- Bulk delete (with confirmation and undo)
- Bulk status change (approve/reject multiple items)
- Bulk export (generate reports for selected items)
- Bulk assignment (assign multiple items to a user)

### Partial Failure Handling

When bulk operations partially fail:
- Show summary: "150 succeeded, 3 failed"
- List failed items with error reasons
- Provide "Retry failed items" action
- Allow users to modify and retry specific failures

## Personas

### End User Completing a Workflow

**Needs**:
- Clear instructions at each step
- Ability to save and return later
- Progress visibility
- Error messages that help them fix issues

**Pain points**: Losing progress, unclear next steps, inability to go back and fix mistakes.

### Approver in an Approval Chain

**Needs**:
- Clear context about what they're approving
- Quick approve/reject actions
- Ability to delegate or request changes
- Notifications for pending approvals

**Pain points**: Missing context, unclear deadlines, no way to delegate when unavailable.

### Admin Configuring Workflow Rules

**Needs**:
- Visual workflow builder or clear configuration UI
- Ability to test workflows before deployment
- Audit trail of workflow changes
- Clear documentation of workflow behavior

**Pain points**: Complex configuration, unclear rule precedence, difficult to debug workflow issues.

### Power User Doing Bulk Operations

**Needs**:
- Efficient selection mechanisms
- Progress tracking for long operations
- Ability to cancel if needed
- Detailed results (what succeeded, what failed)

**Pain points**: No progress indicator, can't cancel, unclear results, slow performance.

## Success Metrics

### Workflow Completion Rate

Percentage of workflows started that are completed. Low rates may indicate:
- Workflow is too complex
- Users are abandoning due to confusion
- Required information is unavailable

### Time-to-Complete

Average time from workflow start to completion. Track by workflow type to identify bottlenecks.

### Abandonment Points

Identify which steps have the highest abandonment rates:
- Step 1: Users don't understand the workflow
- Step 3: Required information is difficult to obtain
- Final step: Users are hesitant to commit

### Bulk Action Success Rate

Percentage of items in bulk operations that succeed. Track:
- Overall success rate
- Common failure reasons
- Retry success rate

## Common Product Mistakes

### No Progress Visibility for Long Tasks

**Problem**: User clicks "Export" and sees nothing for 30 seconds, thinks the app is frozen.

**Solution**: Show indeterminate progress immediately, then switch to determinate if possible.

### Unclear "What Happens Next"

**Problem**: User completes step 3 but doesn't know if they're done or what step 4 requires.

**Solution**: Always show next step preview, completion criteria, and estimated time remaining.

### No Way to Cancel/Undo

**Problem**: User starts a bulk delete, realizes they selected wrong items, but can't stop it.

**Solution**: Provide cancel button for in-progress operations and undo for completed actions.

### Workflow State Not Persisted

**Problem**: User completes 4 of 5 steps, browser crashes, loses all progress.

**Solution**: Auto-save workflow state after each step, allow resuming from last completed step.

### Approval Chains Without Timeouts

**Problem**: Approval request sits with approver for weeks with no escalation.

**Solution**: Implement timeouts with escalation rules (e.g., after 3 days, notify manager).
