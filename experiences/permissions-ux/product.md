# Permissions UX -- Product Perspective

## Contents

- [The Permission Communication Problem](#the-permission-communication-problem)
- [Hide vs Disable vs Show-with-Explanation](#hide-vs-disable-vs-show-with-explanation)
- [Request Access Flows](#request-access-flows)
- [Role-Based UI Adaptation](#role-based-ui-adaptation)
- [Personas](#personas)
- [Success Metrics](#success-metrics)
- [Common Product Mistakes](#common-product-mistakes)

## The Permission Communication Problem

Users encounter features, actions, and content they cannot access. The product challenge is: **How should the UI respond when a user lacks permission?**

This isn't just a technical problem—it's a communication problem. Users need to understand:
- **What exists** (features they might not know about)
- **What they can do** (actions available to them)
- **What they can't do** (and why)
- **How to gain access** (if possible)

Poor permission UX leads to:
- **Confusion**: "Why can't I click this button?"
- **Frustration**: "I see it but can't use it—why show it?"
- **Discovery gaps**: "I didn't know this feature existed"
- **Support burden**: Tickets asking "How do I get access to X?"

## Hide vs Disable vs Show-with-Explanation

The core UX decision for unauthorized content:

### Hide
**When**: Features the user will never access (different role tier, different tenant scope)
**Why**: Reduces UI noise, prevents confusion, cleaner interface
**Example**: A "Billing Admin" role doesn't see "User Management" navigation item

```vue
<!-- Vue: Hide navigation item -->
<nav-item v-if="hasPermission('user:manage')">
  User Management
</nav-item>
```

```tsx
// React: Conditional rendering
{hasPermission('user:manage') && (
  <NavItem>User Management</NavItem>
)}
```

### Disable
**When**: Actions within a feature the user can partially access
**Why**: User knows the feature exists, disabling shows what's possible, provides context
**Example**: User can view a project but can't delete it (delete button is disabled)

```vue
<!-- Vue: Disable with explanation -->
<button 
  :disabled="!canDelete"
  :title="canDelete ? '' : 'Only project admins can delete projects'"
>
  Delete Project
</button>
```

```tsx
// React: Disabled with tooltip
<Button
  disabled={!canDelete}
  title={canDelete ? '' : 'Only project admins can delete projects'}
>
  Delete Project
</Button>
```

### Show-with-Explanation
**When**: User needs to understand why access is restricted and how to get it
**Why**: Educational, provides path forward, reduces support tickets
**Example**: "Upgrade your plan to access advanced analytics" with upgrade button

```vue
<!-- Vue: Show with upgrade CTA -->
<div v-if="!hasPermission('analytics:advanced')" class="upgrade-prompt">
  <p>Advanced analytics requires a Pro plan</p>
  <button @click="navigateToUpgrade">Upgrade Now</button>
</div>
```

## Request Access Flows

When users encounter restricted content, provide a path to access:

1. **User sees restricted feature** (disabled button, hidden content, "Access Denied" message)
2. **User requests access** (clicks "Request access" button, fills form)
3. **Request sent to admin/approver** (notification, email, admin dashboard)
4. **Admin grants/denies** (approval workflow, optional reason)
5. **User notified** (in-app notification, email, permission automatically updated)
6. **UI updates** (feature becomes available, no refresh needed)

**Key product considerations**:
- **Who can approve?** (admin, manager, specific role)
- **Approval workflow**: Single approver vs multi-step
- **Timeout**: Auto-deny after X days if no response
- **Context**: Include reason for request, what user was trying to do
- **Notification**: Real-time updates vs email-only

## Role-Based UI Adaptation

Different roles see different features, navigation, and actions:

- **Navigation**: Role-specific menu items (admin sees "Settings", regular user doesn't)
- **Dashboard widgets**: Role-based dashboard customization
- **Action buttons**: Different actions available per role (view vs edit vs delete)
- **Form fields**: Role-based field visibility/editing
- **Data visibility**: Role-based filtering and scoping

**Example**: A "Project Viewer" role sees:
- Navigation: Projects, Reports (read-only)
- Actions: View, Export (no Create, Edit, Delete)
- Dashboard: Project list widget, read-only reports widget

A "Project Admin" role sees:
- Navigation: Projects, Reports, Settings, User Management
- Actions: View, Create, Edit, Delete, Export, Share
- Dashboard: All widgets, including admin controls

## Personas

### Regular User Encountering Restricted Content
**Scenario**: User tries to delete a project, button is disabled
**Pain points**: 
- No explanation why disabled
- No way to request access
- Unclear if it's a bug or permission issue
**Needs**: Clear explanation, path to access, consistent patterns

### Admin Managing Permissions
**Scenario**: Admin needs to grant access to multiple users
**Pain points**:
- Manual permission assignment is tedious
- Hard to see who has what access
- No audit trail of permission changes
**Needs**: Bulk operations, clear permission matrix, audit logs

### User Requesting Elevated Access
**Scenario**: User needs temporary admin access for a project
**Pain points**:
- Don't know who to ask
- Request gets lost
- No visibility into approval status
**Needs**: Clear request flow, status tracking, automatic notifications

### New User Discovering Features
**Scenario**: New user exploring the application
**Pain points**:
- Don't know what features exist
- Hidden features are invisible
- Unclear what their role enables
**Needs**: Feature discovery, permission education, onboarding guidance

## Success Metrics

### Access-Denied Confusion Rate
**Metric**: Support tickets asking "Why can't I do X?" or "Is this a bug?"
**Target**: < 5% of permission-related interactions result in support tickets
**How to improve**: Better tooltips, consistent patterns, clear error messages

### Request-Access Conversion
**Metric**: % of users who request access after encountering restriction
**Target**: > 30% of restricted interactions lead to access requests
**How to improve**: Make request flow obvious, reduce friction, show value

### Unauthorized Action Attempt Rate
**Metric**: Server-side 403 errors (user tried to perform unauthorized action)
**Target**: < 2% of actions result in 403 (most should be prevented in UI)
**How to improve**: Better frontend permission checks, disable buttons properly

### Permission Discovery Rate
**Metric**: % of users who discover features through permission prompts
**Target**: Track feature adoption after "upgrade to access" prompts
**How to improve**: Show value before restriction, clear upgrade paths

## Common Product Mistakes

### Hiding Everything
**Problem**: User doesn't know features exist, can't request access to unknown features
**Example**: Entire "Advanced Settings" section hidden from non-admins
**Better**: Show section with disabled fields + "Request admin access" button

### Showing Everything Disabled
**Problem**: Frustrating, cluttered UI, user sees many things they can't use
**Example**: All admin actions visible but disabled for regular users
**Better**: Hide navigation items, disable only actions within accessible features

### Inconsistent Hide/Disable Strategy
**Problem**: No clear pattern—users confused about what's hidden vs disabled
**Example**: Some features hidden, others disabled, no explanation
**Better**: Establish pattern: hide navigation, disable actions, always explain

### No Explanation for Disabled State
**Problem**: User clicks disabled button repeatedly, no feedback, frustration
**Example**: Disabled "Delete" button with no tooltip
**Better**: Tooltip explaining "Only project owners can delete" + "Request access" link

### Request Access with No Workflow
**Problem**: "Request access" button exists but nobody receives requests
**Example**: Button sends request to non-existent admin email
**Better**: Proper approval workflow, notifications, status tracking
