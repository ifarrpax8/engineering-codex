# Configuration Management — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Configuration management requires careful coordination to ensure consistency across environments and prevent configuration drift. Configuration changes must be applied safely without causing service disruptions.

**Configuration Synchronization**: Configuration should be synchronized across environments (development, staging, production). Use infrastructure-as-code (IaC) and GitOps practices to maintain consistency.

**Secret Management**: Secrets (passwords, API keys, certificates) must be managed separately from non-secret configuration. Use secret management systems (Vault, Kubernetes Secrets) with proper access controls.

**Configuration Drift**: Actual configuration may drift from desired configuration due to manual changes or reconciliation failures. Regular drift detection identifies and corrects inconsistencies.

**Feature Flags**: Feature flags enable gradual rollouts and quick rollbacks. Coordinate feature flag changes with deployments and monitor flag usage.

**Configuration Changes**: Configuration changes should follow the same deployment process as code changes (review, approval, testing, gradual rollout).

## Monitoring and Alerting

### Essential Metrics

**Configuration Synchronization**:
- Configuration drift detected (desired vs. actual)
- Configuration reconciliation failures
- Configuration update success rate
- Alert threshold: Drift detected (immediate), reconciliation failures > 5% (warning)

**Secret Management**:
- Secret rotation status
- Secret expiration (days until expiration)
- Secret access failures
- Alert threshold: Secret expiring in < 7 days (warning), secret access failures (critical)

**Feature Flag Status**:
- Feature flag changes (enabled/disabled, percentage rollouts)
- Feature flag evaluation errors
- Alert threshold: Feature flag evaluation errors (warning)

**Configuration Deployment**:
- Configuration deployment success rate (target: > 98%)
- Configuration deployment duration
- Configuration rollback rate
- Alert threshold: Deployment success rate < 95%, rollback rate > 5%

### Alert Thresholds

- **Critical**: Configuration drift detected, secret access failures, configuration deployment failures causing service issues
- **Warning**: Secret expiring soon, reconciliation failures, feature flag evaluation errors, configuration deployment success rate dropping
- **Info**: Feature flag changes, configuration updates, environment promotion events

### Dashboards

Maintain dashboards showing:
- Configuration drift status (by environment, by service)
- Secret expiration timeline
- Feature flag status (enabled flags, rollout percentages)
- Configuration deployment history (success/failure, rollbacks)
- Environment configuration differences (staging vs. production)

## Incident Runbooks

### Configuration Drift Detected

**Symptoms**: Actual configuration differs from desired configuration, services behaving unexpectedly, reconciliation failures

**Diagnosis**:
1. Identify drifted configuration: Compare desired (Git/ConfigMap) vs. actual (running pods)
2. Determine cause (manual change, reconciliation failure, timing issue)
3. Check reconciliation logs for errors
4. Review recent configuration changes

**Remediation**:
- **Immediate**: Reconcile configuration (apply desired configuration)
- **Short-term**: Fix reconciliation process if broken
- **Long-term**: Prevent manual changes (enforce GitOps, remove manual edit access)
- Document drift cause and prevention measures

**Configuration Reconciliation** (Kubernetes):
```bash
# Check ConfigMap drift
kubectl get configmap my-config -o yaml > actual-config.yaml
# Compare with desired configuration in Git

# Apply desired configuration
kubectl apply -f desired-config.yaml

# Or trigger reconciliation (if using GitOps operator)
# GitOps operator will automatically reconcile
```

### Configuration Change Causing Issues

**Symptoms**: Service errors after configuration update, performance degradation, service unavailable

**Immediate Actions**:
1. **Assess**: Determine severity (can we wait for fix, or need immediate rollback?)
2. **Rollback**: Execute configuration rollback (see below)
3. **Verify**: Verify rollback success (health checks, metrics)
4. **Notify**: Notify team of rollback and reason

**Configuration Rollback**:

**Kubernetes ConfigMap/Secret Rollback**:
```bash
# Rollback to previous revision (if using revision history)
kubectl rollout undo deployment/my-service

# Or restore from Git (GitOps)
git revert <commit-hash>
git push  # GitOps operator will apply change

# Or manually restore ConfigMap
kubectl apply -f configmap-previous-version.yaml
kubectl rollout restart deployment/my-service
```

**Configuration Rollback Decision Criteria**:
- Rollback if: Service unavailable, data corruption, security issue, performance degradation > 50%
- Don't rollback if: Minor issues, fix available quickly, rollback riskier than fix

### Secret Rotation Failure

**Symptoms**: Secret rotation not completing, services unable to access secrets, authentication failures

**Diagnosis**:
1. Check secret rotation status (Vault lease, rotation job status)
2. Check service logs for secret access errors
3. Verify new secret is valid and accessible
4. Check if services are using old secret (not restarted)

**Remediation**:
- If rotation incomplete: Complete rotation manually, check rotation job logs
- If services using old secret: Restart services to pick up new secret
- If new secret invalid: Rollback to previous secret, fix rotation process
- If access denied: Check service account permissions, Vault policies

**Zero-Downtime Secret Rotation**:
1. **Phase 1**: Create new secret alongside old secret
2. **Phase 2**: Update services to accept both old and new secret (if supported)
3. **Phase 3**: Update services to use new secret (rolling update)
4. **Phase 4**: Verify all services using new secret
5. **Phase 5**: Remove old secret

### Feature Flag Issues

**Symptoms**: Feature flag not taking effect, incorrect feature flag evaluation, feature flag causing errors

**Diagnosis**:
1. Check feature flag configuration (enabled/disabled, rollout percentage)
2. Check feature flag evaluation logs for errors
3. Verify service is using correct feature flag service/API
4. Check feature flag service health

**Remediation**:
- If flag not taking effect: Verify flag configuration, check service is calling flag service correctly
- If evaluation errors: Check feature flag service logs, restart feature flag service if needed
- If incorrect evaluation: Fix flag configuration, verify flag logic
- Emergency: Disable feature flag if causing critical issues

**Feature Flag Rollback**:
```bash
# Disable feature flag (example for LaunchDarkly)
ldcli flags set my-feature-flag --off

# Or via API
curl -X PATCH https://app.launchdarkly.com/api/v2/flags/project-key/flag-key \
  -H "Authorization: api-key" \
  -d '{"patch": [{"op": "replace", "path": "/environments/production/on", "value": false}]}'
```

### Environment Configuration Mismatch

**Symptoms**: Services behave differently in staging vs. production, configuration values differ unexpectedly

**Diagnosis**:
1. Compare configuration between environments (staging vs. production)
2. Identify configuration differences
3. Determine if differences are intentional or drift
4. Check configuration promotion process (was staging config promoted to production?)

**Remediation**:
- If intentional: Document differences and reasons
- If drift: Align configurations (promote staging to production, or fix staging to match production)
- Review configuration promotion process to prevent future drift

**Configuration Diff** (example):
```bash
# Compare ConfigMaps between environments
kubectl get configmap my-config -n staging -o yaml > staging-config.yaml
kubectl get configmap my-config -n production -o yaml > production-config.yaml
diff staging-config.yaml production-config.yaml
```

## Scaling

### Configuration Distribution Scaling

**Configuration Service Scaling**: If using centralized configuration service (Consul, etcd, Spring Cloud Config):
- Scale configuration service horizontally for high availability
- Use caching to reduce load on configuration service
- Distribute configuration service instances across availability zones

**GitOps Scaling**: GitOps operators (ArgoCD, Flux) scale by:
- Running multiple operator instances (high availability)
- Using Git webhooks for faster change detection
- Caching Git repository state to reduce Git API calls

### Secret Management Scaling

**Vault Scaling**: Scale Vault cluster:
- Run multiple Vault nodes (high availability)
- Use Vault performance replication for read scaling
- Distribute Vault nodes across availability zones

**Kubernetes Secrets Scaling**: Kubernetes Secrets scale automatically:
- Secrets are stored in etcd (Kubernetes control plane)
- Scale etcd cluster for high availability
- Use external secret management (Vault CSI driver) to reduce etcd load

### Feature Flag Service Scaling

**Feature Flag Service Scaling**: Scale feature flag service (LaunchDarkly, custom service):
- Scale feature flag service horizontally
- Use CDN/caching for flag evaluations (reduce load on service)
- Distribute feature flag service instances globally (reduce latency)

## Backup and Recovery

### Configuration Backup

**Git-Based Configuration**: Configuration in Git is backed up with code repository:
- Regular Git repository backups
- Git history provides configuration version history
- Can restore any configuration version from Git history

**Kubernetes ConfigMaps/Secrets Backup**:
```bash
# Backup all ConfigMaps
kubectl get configmap -A -o yaml > configmaps-backup.yaml

# Backup all Secrets (values will be base64 encoded)
kubectl get secret -A -o yaml > secrets-backup.yaml

# Encrypt backup
gpg --encrypt secrets-backup.yaml
```

**Vault Backup**: Backup Vault data regularly:
```bash
# Vault backup
vault operator backup -address=https://vault.example.com backup-file

# Store backup in secure location (encrypted object storage)
```

### Feature Flag Configuration Backup

**Feature Flag Backup**: Backup feature flag configurations:
- Export feature flag configurations via API
- Store in version control (Git) for audit trail
- Regular backups of feature flag service data

### Recovery Procedures

**RPO/RTO**:
- RPO: < 1 hour (configuration changes frequently)
- RTO: < 30 minutes (configuration must be available for services)

**Disaster Recovery**:
1. Restore configuration from backup (Git, ConfigMaps, Secrets)
2. Restore feature flag configurations
3. Verify configuration is correct (compare with Git)
4. Reconcile configuration (apply to running services)
5. Verify services are using correct configuration

**Configuration Recovery from Git**:
```bash
# Restore configuration from Git
git checkout <commit-hash> -- path/to/config.yaml
kubectl apply -f path/to/config.yaml

# Or if using GitOps, push to Git and let operator reconcile
git revert <bad-commit>
git push
```

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily**:
- Monitor configuration drift detection
- Review configuration deployment success rates
- Check secret expiration status

**Weekly**:
- Review configuration changes (audit trail)
- Review feature flag usage (unused flags, flags ready for cleanup)
- Check for configuration drift

**Monthly**:
- Review and update retention policies (for configuration history)
- Audit configuration access (who can change configuration)
- Review configuration promotion process (staging to production)
- Review feature flag cleanup (remove unused flags)

**Quarterly**:
- Configuration management review (process, tools, access)
- Secret rotation schedule review
- Feature flag strategy review
- Configuration drift prevention review

### Configuration Change Procedures

**Configuration Change Process**:
1. **Propose**: Create configuration change request (Git PR, change ticket)
2. **Review**: Review change (peer review, security review if secrets)
3. **Test**: Test change in development/staging
4. **Approve**: Approve change (required approvals based on change type)
5. **Deploy**: Deploy to production (gradual rollout if possible)
6. **Verify**: Verify change success (monitor metrics, health checks)
7. **Document**: Document change in change log

**Configuration Change Types**:
- **Non-breaking**: Can be deployed without service restart (some ConfigMap changes)
- **Breaking**: Requires service restart or coordinated deployment
- **Secret changes**: Always require service restart (to pick up new secret)

### Secret Rotation Procedures

**Secret Rotation Schedules**:
- Database passwords: Quarterly
- API keys: Quarterly or after security incident
- Service account tokens: Annually (or per policy)
- TLS certificates: Per certificate expiration (typically annually)

**Zero-Downtime Secret Rotation Pattern**:
1. **Phase 1**: Generate new secret, store alongside old secret
2. **Phase 2**: Update services to support both secrets (if possible)
3. **Phase 3**: Update services to use new secret (rolling update)
4. **Phase 4**: Verify all services using new secret
5. **Phase 5**: Remove old secret after grace period

**Secret Rotation Automation**:
- Use Vault dynamic secrets (short-lived, auto-rotating)
- Automated rotation scripts with coordination logic
- Rotation notifications and alerts

### Drift Detection

**Drift Detection Methods**:
- **GitOps**: GitOps operators continuously reconcile (detect and fix drift automatically)
- **Configuration audits**: Periodic audits comparing desired vs. actual
- **Monitoring**: Monitor for configuration-related errors or unexpected behavior

**Drift Prevention**:
- Enforce GitOps (no manual changes allowed)
- Remove manual edit access to ConfigMaps/Secrets
- Use read-only configuration in production
- Document and approve all configuration changes

**Drift Remediation**:
- Automatic reconciliation (GitOps operators)
- Manual reconciliation (apply desired configuration)
- Investigate root cause and prevent recurrence

### Environment Promotion

**Configuration Promotion Process**:
1. **Verify**: Verify staging configuration is correct and tested
2. **Diff**: Compare staging vs. production configuration
3. **Promote**: Apply staging configuration to production (via GitOps or manual)
4. **Verify**: Verify production configuration matches staging
5. **Monitor**: Monitor for issues after promotion

**Configuration Promotion Tools**:
- GitOps operators (automatic promotion based on Git branches/tags)
- CI/CD pipelines (promote configuration as part of deployment)
- Manual promotion (for critical changes requiring approval)

**Configuration Promotion Best Practices**:
- Promote configuration with code (same Git commit/tag)
- Test configuration in staging before production
- Use feature flags to coordinate configuration and code changes
- Document configuration differences between environments (if intentional)

### Feature Flag Cleanup Coordination

**Feature Flag Lifecycle**:
1. **Create**: Create feature flag for new feature
2. **Test**: Test feature with flag enabled/disabled
3. **Rollout**: Gradually rollout feature (increase percentage)
4. **Complete**: Enable for 100% of users
5. **Cleanup**: Remove feature flag after feature is stable (typically 30-90 days)

**Feature Flag Cleanup Process**:
1. Identify flags ready for cleanup (enabled 100% for 30+ days, no recent changes)
2. Verify feature works without flag (flag always returns enabled)
3. Remove flag from configuration
4. Update code to remove flag checks (if not already removed)
5. Deploy code and configuration changes
6. Verify feature still works

**Feature Flag Cleanup Coordination**:
- Coordinate flag removal with code deployment (remove flag checks in same deployment)
- Use feature flag service APIs to disable flags before code removal
- Document flag removal in deployment notes

### Configuration Audit Trail

**Audit Trail Requirements**:
- Track all configuration changes (who, what, when, why)
- Store audit trail in immutable storage (Git history, audit logs)
- Review audit trail regularly for unauthorized changes

**Configuration Audit Tools**:
- Git history (for Git-based configuration)
- Kubernetes audit logs (for ConfigMap/Secret changes)
- Vault audit logs (for secret access)
- Feature flag service audit logs

**Audit Trail Review**:
- Review configuration changes weekly
- Investigate unauthorized or suspicious changes
- Document findings and remediation

## On-Call Considerations

### What On-Call Engineers Need to Know

**Configuration Topology**: Understand which services use which configurations, configuration sources (Git, ConfigMaps, Vault), and configuration dependencies.

**Secret Management**: Know how to access secrets (Vault, Kubernetes Secrets), rotate secrets, and verify secret access.

**Feature Flags**: Know how to check feature flag status, enable/disable flags, and coordinate flag changes with deployments.

**Common Commands**:
```bash
# Check ConfigMap
kubectl get configmap my-config -o yaml

# Check Secret (values are base64 encoded)
kubectl get secret my-secret -o yaml
echo "base64-value" | base64 -d

# Check configuration drift (GitOps example)
argocd app diff my-app

# Check Vault secret
vault kv get secret/my-secret

# Check feature flag (example)
curl https://app.launchdarkly.com/api/v2/flags/project/flag-key \
  -H "Authorization: api-key"
```

**Escalation Paths**:
1. Check configuration and verify drift (5 minutes)
2. Check configuration deployment status (10 minutes)
3. Rollback configuration if causing issues (15 minutes)
4. Escalate to configuration management team if unresolved (20 minutes)
5. Escalate to platform/infrastructure if infrastructure issue (30 minutes)

### Runbook Quick Reference

- **Configuration Drift**: Detect drift → Identify cause → Reconcile configuration → Prevent recurrence
- **Configuration Rollback**: Assess severity → Rollback configuration → Verify success → Investigate root cause
- **Secret Rotation Failure**: Check rotation status → Complete rotation → Restart services → Verify access
- **Feature Flag Issues**: Check flag configuration → Check evaluation logs → Fix or disable flag → Verify
- **Environment Mismatch**: Compare configurations → Identify differences → Align configurations → Document

### Critical Alerts

- **Configuration drift detected**: Warning, investigate and reconcile
- **Secret access failures**: Critical, services may be unavailable
- **Configuration deployment failures**: Warning, may cause service issues
- **Secret expiring in < 7 days**: Warning, rotate before expiration
- **Feature flag evaluation errors**: Warning, features may not work correctly

### Configuration Change Approval Matrix

| Change Type | Approval Required | Testing Required | Rollback Plan Required |
|-------------|------------------|------------------|------------------------|
| Non-secret config (non-breaking) | Peer review | Staging test | Yes |
| Non-secret config (breaking) | Team lead | Staging + canary | Yes |
| Secret changes | Security review | Staging test | Yes |
| Feature flag changes | Peer review | Staging test | Yes (can disable flag) |
| Environment promotion | Team lead | Staging verified | Yes |
