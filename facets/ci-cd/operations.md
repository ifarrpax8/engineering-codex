# CI/CD — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

CI/CD pipelines are critical infrastructure that must be highly available and performant. Pipeline failures block deployments and developer productivity.

**Pipeline Availability**: CI/CD systems should have > 99% uptime. Use high-availability deployments for CI/CD infrastructure (GitHub Actions, GitLab CI, Jenkins controllers).

**Pipeline Performance**: Pipeline execution time directly impacts developer productivity. Monitor pipeline duration and optimize slow steps (tests, builds, deployments).

**Artifact Management**: Build artifacts (container images, packages) must be stored securely and retained according to policies. Artifact storage costs can grow quickly.

**Cache Management**: Build caches (dependency caches, Docker layer caches) improve performance but require management (invalidation, size limits, cleanup).

**Flaky Tests**: Flaky tests reduce confidence in pipelines and slow development. Quarantine flaky tests and fix root causes.

## Monitoring and Alerting

### Essential Metrics

**Pipeline Health**:
- Pipeline success rate (target: > 95%)
- Pipeline duration (p50, p95, p99)
- Queue time (time waiting for runners)
- Runner utilization (active runners / total runners)
- Alert threshold: Success rate < 90% for 30 minutes, queue time > 10 minutes

**Runner Health**:
- Runner availability (online runners / total runners)
- Runner error rate
- Runner resource utilization (CPU, memory, disk)
- Alert threshold: < 80% runners available, runner error rate > 5%

**Artifact Storage**:
- Artifact storage usage (GB)
- Artifact retention compliance
- Alert threshold: Storage > 80% capacity, retention violations

**Cache Performance**:
- Cache hit rate (target: > 70%)
- Cache size (GB)
- Cache eviction rate
- Alert threshold: Cache hit rate < 50%, cache size > limit

**Deployment Metrics**:
- Deployment frequency (deployments/day)
- Deployment success rate (target: > 98%)
- Rollback rate
- Deployment duration
- Alert threshold: Deployment success rate < 95%, rollback rate > 5%

### Alert Thresholds

- **Critical**: CI/CD system unavailable, pipeline success rate < 80%, all runners unavailable
- **Warning**: Pipeline success rate < 90%, queue time > 10 minutes, runner utilization > 90%, artifact storage > 80%
- **Info**: Pipeline performance degradation, cache hit rate dropping, flaky test detected

### Dashboards

Maintain dashboards showing:
- Pipeline overview (success rate, duration, queue time)
- Runner status (availability, utilization, errors)
- Artifact storage (usage, retention compliance)
- Cache performance (hit rate, size, eviction)
- Deployment metrics (frequency, success rate, rollback rate)
- Flaky test tracking

## Incident Runbooks

### Pipeline Failures

**Symptoms**: Multiple pipelines failing, builds timing out, tests failing

**Diagnosis**:
1. Check pipeline logs for error patterns
2. Check runner availability and health
3. Check for infrastructure issues (network, storage)
4. Review recent changes (pipeline configuration, code changes)
5. Check for resource exhaustion (disk, memory)

**Remediation**:
- If runner issue: Restart runners, scale runners, check runner logs
- If infrastructure issue: Check network connectivity, storage availability, DNS resolution
- If resource exhaustion: Clean up artifacts/caches, increase runner resources
- If code issue: Fix code, rerun pipeline
- If configuration issue: Fix pipeline configuration, validate syntax

### Runner Unavailable

**Symptoms**: Pipelines queued, no runners available, high queue time

**Diagnosis**:
1. Check runner status: `kubectl get pods -l app=runner` (for self-hosted runners)
2. Check runner logs for errors
3. Check runner resource utilization
4. Check for runner scaling issues (auto-scaling not working)

**Remediation**:
- If runners crashed: Restart runners, check for OOM kills or errors
- If scaling issue: Manually scale runners, fix auto-scaling configuration
- If resource exhaustion: Increase runner resources or scale horizontally
- Temporary: Use cloud runners if self-hosted runners unavailable

### Artifact Storage Full

**Symptoms**: Artifact uploads failing, storage quota exceeded, retention policies not working

**Diagnosis**:
1. Check artifact storage usage: Review storage dashboard or `du -sh /artifact-storage`
2. Check retention policies (are they configured? are they working?)
3. Identify large artifacts or old artifacts not cleaned up
4. Check for storage leaks (artifacts not being cleaned up)

**Remediation**:
- Immediate: Manually clean up old artifacts (if safe)
- Short-term: Adjust retention policies to be more aggressive
- Long-term: Increase storage capacity, implement automated cleanup
- Review artifact usage (are all artifacts needed? can we reduce artifact size?)

**Artifact Cleanup** (example):
```bash
# Clean up artifacts older than 30 days (example for container registry)
# Use registry-specific cleanup tools or APIs
```

### Cache Issues

**Symptoms**: Slow builds, cache misses, cache size growing, cache corruption

**Diagnosis**:
1. Check cache hit rate (should be > 70%)
2. Check cache size (may be hitting limits)
3. Check for cache corruption (build failures after cache hits)
4. Review cache invalidation logic (is cache being invalidated too frequently?)

**Remediation**:
- If cache miss rate high: Review cache key strategy, ensure cache keys are stable
- If cache size limit: Increase cache size limit or implement cache eviction
- If cache corruption: Invalidate cache, rebuild cache
- If cache invalidation too frequent: Review invalidation triggers, optimize

**Cache Invalidation**:
```yaml
# Example: Invalidate cache on dependency changes
cache:
  key: ${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
  paths:
    - node_modules/
```

### Flaky Tests

**Symptoms**: Tests passing/failing inconsistently, reduced confidence in pipelines, developers rerunning pipelines

**Diagnosis**:
1. Identify flaky tests (tests that fail intermittently)
2. Review test logs for timing issues, race conditions, external dependencies
3. Check for resource contention (tests competing for resources)
4. Review test isolation (are tests properly isolated?)

**Remediation**:
- **Immediate**: Quarantine flaky tests (skip in main pipeline, run in separate job)
- **Short-term**: Add retries for flaky tests (temporary measure)
- **Long-term**: Fix root cause (timing issues, race conditions, test isolation)
- Track flaky tests and prioritize fixes

**Test Quarantine** (example):
```yaml
# Quarantine flaky test
test:
  script:
    - pytest tests/ --ignore=tests/flaky/
  
# Run flaky tests separately with retries
test-flaky:
  script:
    - pytest tests/flaky/ --maxfail=1
  retry:
    max: 3
```

### Deployment Rollback

**Symptoms**: Deployment causing issues, service degradation, errors after deployment

**Immediate Actions**:
1. **Assess**: Determine severity (can we wait for fix, or need immediate rollback?)
2. **Rollback**: Execute rollback procedure (see below)
3. **Verify**: Verify rollback success (health checks, metrics)
4. **Notify**: Notify team of rollback and reason

**Rollback Procedures**:

**Kubernetes Rollback**:
```bash
# Rollback to previous revision
kubectl rollout undo deployment/my-service

# Rollback to specific revision
kubectl rollout undo deployment/my-service --to-revision=2

# Check rollout status
kubectl rollout status deployment/my-service
```

**Container Image Rollback**:
1. Tag previous image version as `latest` or `stable`
2. Update deployment to use previous image
3. Trigger deployment pipeline with previous image
4. Verify deployment success

**Database Migration Rollback**:
- If backward-compatible: No rollback needed
- If backward-incompatible: Rollback migration script, coordinate with application rollback

**Rollback Decision Criteria**:
- Rollback if: Service unavailable, data corruption, security issue, performance degradation > 50%
- Don't rollback if: Minor issues, fix available quickly, rollback riskier than fix

## Scaling

### Runner Scaling

**Self-Hosted Runner Scaling**:
- **Horizontal**: Add more runner instances (pods, VMs)
- **Vertical**: Increase runner resources (CPU, memory)
- **Auto-Scaling**: Configure auto-scaling based on queue depth

**Auto-Scaling Configuration** (Kubernetes):
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: runner-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: runner
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: External
    external:
      metric:
        name: pipeline_queue_depth
      target:
        type: AverageValue
        averageValue: "5"
```

**Runner Pool Management**:
- **Dedicated pools**: For specific teams or workloads (GPU runners, large memory runners)
- **Shared pools**: For general workloads
- **Spot/Preemptible instances**: For cost optimization (with retry logic)

**When to Scale Runners**:
- Queue time consistently > 5 minutes
- Runner utilization > 80% sustained
- Pipeline duration increasing due to queue time

### Pipeline Performance Optimization

**Parallel Execution**: Run independent steps in parallel:
```yaml
# Example: Run tests in parallel
test:
  parallel:
    matrix:
      - test_suite: [unit, integration, e2e]
  script:
    - pytest tests/${{ matrix.test_suite }}/
```

**Build Optimization**:
- Use build caches (Docker layer cache, dependency cache)
- Optimize Dockerfiles (multi-stage builds, layer ordering)
- Use build tools that support incremental builds

**Test Optimization**:
- Run fast tests first (fail fast)
- Parallelize test execution
- Use test sharding for large test suites
- Skip unnecessary tests (e.g., skip integration tests on docs-only changes)

### Artifact Retention Management

**Retention Policies**:
- **Development builds**: Retain 7-30 days
- **Release builds**: Retain 90-365 days (or indefinitely for releases)
- **Pull request builds**: Retain 7 days
- **Failed builds**: Retain 7 days (for debugging)

**Automated Cleanup**:
- Implement automated cleanup based on retention policies
- Clean up artifacts older than retention period
- Clean up artifacts from deleted branches/PRs
- Monitor cleanup job success

**Storage Cost Optimization**:
- Use object storage with lifecycle policies (move to cheaper storage after X days)
- Compress artifacts where possible
- Remove unnecessary artifacts (intermediate build artifacts)

### Cache Management

**Cache Size Limits**:
- Set cache size limits per runner or per cache key
- Implement cache eviction (LRU, time-based)
- Monitor cache size and eviction rate

**Cache Invalidation Strategy**:
- Invalidate on dependency changes (package.json, requirements.txt)
- Invalidate on tool version changes (Node version, Python version)
- Use stable cache keys for dependencies, volatile keys for build outputs

**Cache Performance Monitoring**:
- Track cache hit rate (target: > 70%)
- Track cache size and eviction rate
- Identify cache misses and optimize cache keys

## Backup and Recovery

### Pipeline Configuration Backup

**GitHub Actions**: Pipeline configurations are in repository (backed up with code).

**GitLab CI**: Pipeline configurations are in repository (backed up with code).

**Jenkins**: Backup Jenkins configuration:
```bash
# Backup Jenkins home directory
tar -czf jenkins-backup.tar.gz /var/jenkins_home/

# Or use Jenkins backup plugin
```

### Artifact Backup

**Artifact Backup Strategy**:
- Critical artifacts (releases): Backup to separate storage (S3, artifact repository)
- Development artifacts: Typically not backed up (can rebuild)
- Container images: Backup to separate registry or object storage

**Artifact Recovery**:
1. Restore artifacts from backup
2. Verify artifact integrity
3. Update pipeline to use restored artifacts if needed

### Runner Configuration Backup

**Self-Hosted Runner Configuration**: Backup runner configuration (if stored outside of code):
```bash
# Backup runner configuration
kubectl get configmap runner-config -o yaml > runner-config-backup.yaml
```

### Recovery Procedures

**RPO/RTO**:
- RPO: < 1 hour (pipeline configurations change frequently)
- RTO: < 30 minutes (CI/CD must be available for deployments)

**Disaster Recovery**:
1. Restore CI/CD system (GitHub Actions, GitLab CI, Jenkins)
2. Restore runner configurations
3. Restore critical artifacts (releases)
4. Verify pipelines can run
5. Test deployment pipeline

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily**:
- Monitor pipeline success rates and queue times
- Review and triage pipeline failures
- Check runner availability

**Weekly**:
- Review pipeline performance (duration trends)
- Review artifact storage usage
- Review cache performance
- Quarantine new flaky tests

**Monthly**:
- Review and update retention policies
- Clean up old artifacts (if automated cleanup not working)
- Review and optimize pipeline configurations
- Review runner resource allocation
- Fix flaky tests (prioritize high-impact flaky tests)

**Quarterly**:
- Pipeline performance review and optimization
- Runner capacity planning
- Artifact storage capacity planning
- Review and update maintenance procedures

### Pipeline Maintenance

**Workflow Syntax Updates**: Update workflow syntax when CI/CD platform releases new features:
- Review release notes for breaking changes
- Test syntax updates in development/staging
- Update pipelines gradually (one at a time)

**Action Version Pinning**: Pin action versions to prevent breaking changes:
```yaml
# Pin to specific version
- uses: actions/checkout@v3

# Or pin to commit SHA for maximum stability
- uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b8
```

**Action Version Updates**: Regularly update actions to get security patches and features:
1. Review action release notes
2. Test updates in development/staging
3. Update actions in production pipelines
4. Monitor for issues after update

### Runner Maintenance

**Runner Updates**: Update runner software regularly:
- Update runner agent software (GitHub Actions runner, GitLab runner)
- Update base images (if using containerized runners)
- Test runner updates in staging before production

**Runner Resource Optimization**: Review and optimize runner resource allocation:
- Analyze runner resource usage (CPU, memory, disk)
- Adjust resource requests/limits based on usage
- Consider dedicated runners for resource-intensive workloads

**Runner Cleanup**: Clean up runner resources regularly:
- Remove unused runner pools
- Clean up runner logs and temporary files
- Remove runners from deleted repositories/projects

### Artifact Retention Management

**Retention Policy Review**: Review retention policies quarterly:
- Adjust based on storage costs and compliance requirements
- Ensure policies are being enforced (automated cleanup working)
- Document retention policies

**Artifact Cleanup**: Implement automated artifact cleanup:
- Clean up artifacts older than retention period
- Clean up artifacts from deleted branches/PRs
- Clean up failed build artifacts (after debugging period)

**Storage Cost Optimization**: Optimize artifact storage costs:
- Use lifecycle policies (move to cheaper storage after X days)
- Compress artifacts
- Remove unnecessary artifacts

### Cache Management

**Cache Invalidation**: Review cache invalidation strategy:
- Ensure cache keys are stable (don't change unnecessarily)
- Invalidate cache on dependency changes
- Monitor cache hit rate and adjust strategy

**Cache Size Management**: Manage cache size:
- Set cache size limits
- Implement cache eviction
- Monitor cache size and eviction rate

**Cache Performance Optimization**: Optimize cache performance:
- Review cache key strategy (too granular vs. too coarse)
- Use cache warming for frequently used caches
- Monitor cache hit rate and optimize

### Flaky Test Management

**Flaky Test Tracking**: Track flaky tests:
- Maintain list of known flaky tests
- Track flaky test frequency and impact
- Prioritize fixes based on impact

**Flaky Test Quarantine**: Quarantine flaky tests:
- Skip flaky tests in main pipeline
- Run flaky tests separately with retries
- Document flaky tests and root causes

**Flaky Test Fixes**: Fix flaky tests:
- Investigate root causes (timing, race conditions, external dependencies)
- Fix root causes (add waits, fix race conditions, mock external dependencies)
- Remove from quarantine after fix verified

### Pipeline Performance Monitoring

**Performance Metrics**: Track pipeline performance:
- Pipeline duration (p50, p95, p99)
- Queue time
- Runner utilization
- Cache hit rate

**Performance Optimization**: Optimize pipeline performance:
- Identify slow steps (builds, tests, deployments)
- Optimize slow steps (parallelization, caching, optimization)
- Monitor performance trends and regressions

## On-Call Considerations

### What On-Call Engineers Need to Know

**Pipeline Topology**: Understand which pipelines exist, what they do, and their dependencies.

**Runner Infrastructure**: Know runner locations, scaling configuration, and how to scale manually if needed.

**Common Commands**:
```bash
# Check pipeline status (GitHub Actions example)
gh run list --limit 10

# Check runner status (Kubernetes)
kubectl get pods -l app=runner

# Check artifact storage
du -sh /artifact-storage

# Restart runners (if needed)
kubectl rollout restart deployment/runner
```

**Escalation Paths**:
1. Check pipeline and runner status (5 minutes)
2. Check for infrastructure issues (10 minutes)
3. Scale runners if queue time high (15 minutes)
4. Escalate to platform/infrastructure if infrastructure issue (20 minutes)
5. Escalate to CI/CD team lead if unresolved (30 minutes)

### Runbook Quick Reference

- **Pipeline Failures**: Check logs → Check runners → Check infrastructure → Fix issue → Rerun pipeline
- **Runner Unavailable**: Check runner status → Restart runners → Scale runners → Check auto-scaling
- **Artifact Storage Full**: Check storage usage → Clean up old artifacts → Adjust retention → Increase capacity
- **Cache Issues**: Check cache hit rate → Review cache keys → Invalidate cache → Optimize strategy
- **Flaky Tests**: Identify flaky test → Quarantine → Investigate root cause → Fix → Remove from quarantine
- **Deployment Rollback**: Assess severity → Execute rollback → Verify success → Notify team → Investigate root cause

### Critical Alerts

- **CI/CD system unavailable**: Critical, blocks all deployments
- **Pipeline success rate < 80%**: Critical, widespread failures
- **All runners unavailable**: Critical, pipelines cannot run
- **Deployment success rate < 95%**: Warning, deployment issues
- **Artifact storage > 90%**: Warning, may cause upload failures

### Deployment Rollback Decision Matrix

| Issue Severity | Rollback? | Notes |
|----------------|-----------|-------|
| Service unavailable | Yes | Immediate rollback |
| Data corruption | Yes | Immediate rollback |
| Security vulnerability | Yes | Immediate rollback |
| Performance degradation > 50% | Yes | Rollback if fix not immediate |
| Minor bugs | No | Fix forward if possible |
| Performance degradation < 20% | No | Monitor, fix if worsens |
