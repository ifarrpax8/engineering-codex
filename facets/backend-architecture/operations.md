# Backend Architecture — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Backend services in production require careful attention to health, readiness, and graceful degradation. Services should expose health endpoints that reflect their true operational state.

**Health Checks**: Spring Boot Actuator provides `/actuator/health` endpoints. Configure separate liveness and readiness probes:
- **Liveness**: Indicates the application process is running. Should be lightweight and fail if the JVM is deadlocked or unresponsive.
- **Readiness**: Indicates the application can accept traffic. Should fail during startup, graceful shutdown, or when critical dependencies (database, message brokers) are unavailable.

**Graceful Shutdown**: Services must handle termination signals (SIGTERM) gracefully:
- Stop accepting new requests
- Complete in-flight requests (with timeout)
- Release resources (close database connections, flush logs)
- Spring Boot's `spring.lifecycle.timeout-per-shutdown-phase` controls shutdown timeout

**Service Dependencies**: Monitor dependency health (databases, message brokers, external APIs). Use circuit breakers (Resilience4j) to prevent cascading failures. See [architecture.md](architecture.md) for circuit breaker patterns.

**Thread Pool Monitoring**: Watch thread pool utilization, queue depths, and rejection rates. High queue depths indicate thread starvation or slow downstream dependencies.

## Monitoring and Alerting

### Essential Metrics

**Service Health**:
- HTTP status codes (2xx, 4xx, 5xx rates)
- Response time percentiles (p50, p95, p99)
- Request rate (requests/second)
- Error rate threshold: Alert if > 1% of requests fail

**Resource Utilization**:
- CPU usage (alert if > 80% sustained)
- Memory usage (alert if > 85% of limit)
- JVM heap usage (alert if > 80% after GC)
- Thread pool active threads vs max threads

**Dependency Health**:
- Database connection pool utilization
- Circuit breaker state (open/closed/half-open)
- Downstream service latency and error rates
- Message broker connection status

**Spring Boot Actuator Metrics**:
```bash
# Check health endpoint
curl http://service:8080/actuator/health

# Get detailed metrics
curl http://service:8080/actuator/metrics
curl http://service:8080/actuator/metrics/jvm.memory.used
```

### Alert Thresholds

- **Critical**: Service unavailable (5xx > 5% for 2 minutes), dependency failure, memory leak detected
- **Warning**: Elevated error rate (5xx > 1% for 5 minutes), high latency (p95 > 1s), resource exhaustion approaching
- **Info**: Deployment events, configuration changes, scaling events

### Dashboards

Maintain dashboards showing:
- Service overview (health, traffic, errors)
- Resource utilization trends
- Dependency health matrix
- Circuit breaker states
- Deployment history and rollback events

## Incident Runbooks

### Service Unavailable (5xx Errors)

**Symptoms**: High 5xx error rate, service health endpoint failing

**Diagnosis**:
1. Check service logs for exceptions: `kubectl logs -f deployment/service-name --tail=100`
2. Verify resource limits: `kubectl top pod -l app=service-name`
3. Check dependency health (database, message broker)
4. Review recent deployments: `kubectl rollout history deployment/service-name`

**Remediation**:
- If resource exhaustion: Scale horizontally or increase resource limits
- If dependency failure: Check dependency status, consider circuit breaker state
- If code issue: Rollback to previous version: `kubectl rollout undo deployment/service-name`
- If database connection pool exhausted: Check for connection leaks, increase pool size temporarily

### High Latency

**Symptoms**: p95/p99 latency spikes, request timeouts

**Diagnosis**:
1. Check thread pool metrics (active threads, queue depth)
2. Review slow query logs if database-related
3. Check downstream service latency
4. Review JVM GC logs for long GC pauses

**Remediation**:
- If thread pool exhaustion: Increase thread pool size or optimize slow operations
- If database slow queries: Add indexes, optimize queries, consider read replicas
- If downstream latency: Check downstream service health, enable circuit breaker
- If GC pauses: Tune JVM GC settings, increase heap size

### Memory Leak

**Symptoms**: Gradual memory increase, frequent GC, eventual OOM kills

**Diagnosis**:
1. Review heap dumps: `kubectl exec pod-name -- jmap -dump:format=b,file=/tmp/heap.hprof <pid>`
2. Analyze GC logs for increasing heap usage
3. Check for unclosed resources (connections, streams)

**Remediation**:
- Restart service to clear leak (temporary)
- Fix root cause (unclosed resources, cache growth, listener leaks)
- Increase memory limits if legitimate growth (with monitoring)

### Circuit Breaker Open

**Symptoms**: Circuit breaker in OPEN state, requests failing fast

**Diagnosis**:
1. Check Resilience4j metrics: `curl http://service:8080/actuator/metrics/resilience4j.circuitbreaker.calls`
2. Review downstream service health
3. Check error rates that triggered circuit breaker

**Remediation**:
- If downstream service recovered: Wait for circuit breaker to transition to HALF_OPEN
- If downstream still failing: Fix downstream service or remove dependency
- Manually reset circuit breaker if needed (via actuator endpoint or restart)

## Scaling

### Horizontal Pod Autoscaling (HPA)

Configure HPA based on CPU, memory, or custom metrics:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: service-name
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Scaling Triggers**:
- CPU > 70% average across pods
- Memory > 80% average across pods
- Custom metrics (request rate, queue depth)

**Scaling Considerations**:
- Set appropriate `minReplicas` for high availability (typically 2-3)
- Set `maxReplicas` based on capacity planning and cost constraints
- Consider pod startup time when setting scale-down delays
- Use pod disruption budgets to maintain availability during scaling

### Vertical Scaling

Increase resource requests/limits when:
- Single pod cannot handle load (CPU/memory at limit)
- Application requires more memory for data processing
- JVM needs larger heap for GC efficiency

**Resource Updates**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

**When to Scale Vertically**:
- Application is single-threaded or cannot parallelize
- Memory requirements exceed current limits
- Vertical scaling is more cost-effective than horizontal

### Deployment Coordination

**Rolling Updates**: Kubernetes performs rolling updates by default. Configure:
- `maxSurge`: Number of pods that can be created above desired count (default 25%)
- `maxUnavailable`: Number of pods that can be unavailable during update (default 25%)

**Dependency Ordering**: For services with dependencies:
1. Deploy database migrations first (if backward compatible)
2. Deploy services in dependency order (downstream before upstream)
3. Use feature flags to coordinate breaking changes

**Canary Deployments**: Route small percentage of traffic to new version, monitor metrics, gradually increase traffic.

## Backup and Recovery

### Application State

Backend services are typically stateless. State is stored in:
- Databases (see data-persistence operations)
- Message brokers (see event-driven-architecture operations)
- External storage (S3, etc.)

### Configuration Backup

Backup Kubernetes ConfigMaps and Secrets:
```bash
# Backup ConfigMaps
kubectl get configmap -o yaml > configmaps-backup.yaml

# Backup Secrets (values will be base64 encoded)
kubectl get secret -o yaml > secrets-backup.yaml
```

### Recovery Procedures

**Service Rollback**:
```bash
# Rollback to previous revision
kubectl rollout undo deployment/service-name

# Rollback to specific revision
kubectl rollout undo deployment/service-name --to-revision=2

# Check rollout status
kubectl rollout status deployment/service-name
```

**RPO/RTO**: 
- RPO: Near-zero (stateless services, state in external stores)
- RTO: < 5 minutes (automated rollback, health checks)

## Maintenance Procedures

### Regular Maintenance Tasks

**Weekly**:
- Review error rates and slow queries
- Check for dependency updates (Spring Boot, libraries)
- Review resource utilization trends

**Monthly**:
- Review and update resource requests/limits based on usage
- Audit circuit breaker configurations
- Review and optimize thread pool settings
- Check for memory leaks (heap analysis)

**Quarterly**:
- Dependency upgrades (Spring Boot, JDK)
- Security patches
- Performance testing and capacity planning
- Review and update HPA thresholds

### Upgrade Procedures

**Spring Boot Upgrades**:
1. Review release notes for breaking changes
2. Test in development/staging
3. Update dependencies: `./gradlew dependencies --update-latest-release`
4. Run test suite
5. Deploy to staging, monitor for 24-48 hours
6. Deploy to production with canary deployment

**JDK Upgrades**:
1. Verify application compatibility
2. Test GC behavior with new JDK version
3. Update base image in Dockerfile
4. Follow same deployment process as Spring Boot upgrades

### Cleanup Tasks

**Log Rotation**: Configure log rotation to prevent disk exhaustion:
- Application logs: Rotate daily, retain 7-30 days
- Access logs: Rotate daily, retain 30-90 days
- GC logs: Rotate daily, retain 7 days

**Thread Dump Collection**: Collect thread dumps during incidents, retain for 30 days for analysis.

**Heap Dump Collection**: Collect heap dumps for memory leak analysis, retain for 7 days (large files).

## On-Call Considerations

### What On-Call Engineers Need to Know

**Service Topology**: Understand service dependencies, which services call which, and critical paths.

**Health Check Endpoints**: Know how to check service health:
- `/actuator/health` - Basic health
- `/actuator/health/liveness` - Liveness probe
- `/actuator/health/readiness` - Readiness probe
- `/actuator/metrics` - Detailed metrics

**Common Commands**:
```bash
# Check pod status
kubectl get pods -l app=service-name

# View logs
kubectl logs -f deployment/service-name --tail=100

# Check resource usage
kubectl top pod -l app=service-name

# Describe pod for events
kubectl describe pod pod-name

# Execute into pod
kubectl exec -it pod-name -- /bin/sh
```

**Escalation Paths**:
1. Check service health and logs (5 minutes)
2. Check dependencies (database, message broker) - 10 minutes
3. Check recent deployments and consider rollback - 15 minutes
4. Escalate to team lead if unresolved - 30 minutes
5. Escalate to platform/infrastructure if infrastructure issue - 45 minutes

**When to Rollback**:
- Service unavailable (5xx > 5% for 5 minutes)
- Data corruption or incorrect behavior
- Performance degradation (p95 > 2x baseline)
- Security vulnerability introduced

**When NOT to Rollback**:
- Single pod failure (Kubernetes will restart)
- Transient dependency failure (circuit breaker will handle)
- Expected behavior during deployment (wait for rollout to complete)

### Runbook Quick Reference

- **Service Down**: Check health → Check resources → Check dependencies → Rollback if recent deploy
- **High Errors**: Check logs → Check dependencies → Check circuit breakers → Scale if needed
- **High Latency**: Check thread pools → Check database → Check downstream → Optimize or scale
- **Memory Issues**: Check heap usage → Collect heap dump → Restart if critical → Fix leak
