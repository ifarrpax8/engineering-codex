# Observability — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Observability systems must be highly available and performant, as they are critical for understanding system health. The observability stack (metrics, logs, traces) should not become a bottleneck or single point of failure.

**Collector Fleet**: OpenTelemetry collectors or log shippers (Fluentd, Fluent Bit) should be distributed and resilient. Collector failures should not impact application availability.

**Storage Backends**: Metrics (Prometheus), logs (Loki, Elasticsearch), and traces (Jaeger, Tempo) require careful capacity planning and retention policies.

**Sampling**: Trace sampling reduces storage costs but must balance cost vs. observability. Use head-based sampling for high-volume, low-latency services; tail-based sampling for error-focused analysis.

**Cardinality Explosion**: High-cardinality metrics (unique label combinations) can cause storage and query performance issues. Monitor metric cardinality and enforce labeling standards.

**SLO Monitoring**: Service Level Objectives (SLOs) require continuous monitoring and alerting. Burn rate alerts detect SLO violations before error budgets are exhausted.

## Monitoring and Alerting

### Essential Metrics

**Observability Stack Health**:
- Collector uptime and error rates
- Storage backend availability (Prometheus, Loki, Jaeger)
- Ingestion rates (metrics/sec, logs/sec, spans/sec)
- Storage utilization (disk usage, retention)
- Query performance (p95 query latency)

**Cost Metrics**:
- Metric cardinality (unique time series)
- Log ingestion volume (GB/day)
- Trace sampling rate and storage volume
- Storage costs (by backend, by retention tier)

**Alert Thresholds**:
- **Critical**: Collector unavailable, storage backend down, storage > 90% capacity
- **Warning**: Ingestion rate dropping > 50%, query latency > 5s, cardinality > 100k per metric
- **Info**: Retention policy changes, sampling rate adjustments

### Alert Tuning

**Reducing Alert Noise**:
- Use multi-window burn rate alerts instead of simple threshold alerts
- Group related alerts to reduce duplication
- Suppress alerts during known maintenance windows
- Use alert grouping and inhibition rules

**Burn Rate Alerts** (for SLOs):
```yaml
# Example: Alert if error budget will be exhausted in 6 hours
groups:
  - name: slo_burn_rate
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.01
        for: 5m
        annotations:
          summary: "Error rate exceeds SLO threshold"
```

**Escalation Policies**:
- Page on-call for critical alerts (observability stack down)
- Notify team channel for warning alerts
- Create tickets for info-level alerts requiring follow-up

### Dashboards

**Dashboard Maintenance**:
- Assign dashboard owners (review quarterly)
- Review dashboard usage (remove unused dashboards)
- Update dashboards when services change
- Document dashboard purposes and key metrics

**Essential Dashboards**:
- Observability stack health (collectors, storage backends)
- Service overview (health, latency, errors across services)
- SLO dashboards (error budgets, burn rates)
- Cost dashboards (ingestion rates, storage costs, cardinality)

### Log Retention

**Retention Policies**:
- **Hot storage** (frequently accessed): 7-30 days, high-performance storage
- **Warm storage** (occasionally accessed): 30-90 days, standard storage
- **Cold storage** (rarely accessed): 90+ days, object storage (S3), compressed

**Cost vs. Compliance**:
- Balance retention costs with compliance requirements
- Use tiered storage to reduce costs
- Archive critical logs to long-term storage
- Automate log lifecycle management

**Log Volume Management**:
- Monitor log ingestion rates (GB/day)
- Set up alerts for unusual volume spikes
- Review and adjust log levels (reduce verbose logging)
- Use structured logging to enable filtering and reduce noise

## Incident Runbooks

### Observability Stack Down

**Symptoms**: No new metrics/logs/traces, dashboards stale, alerts not firing

**Diagnosis**:
1. Check collector status: `kubectl get pods -l app=otel-collector`
2. Check storage backend status (Prometheus, Loki, Jaeger)
3. Check network connectivity between collectors and backends
4. Review collector logs for errors

**Remediation**:
- If collector down: Restart collector pods, check resource limits
- If storage backend down: Restart storage backend, check disk space
- If network issue: Check network policies, DNS resolution
- Temporary: Increase collector replicas, route to backup storage

### High Cardinality Metrics

**Symptoms**: Prometheus storage growing rapidly, slow queries, high memory usage

**Diagnosis**:
1. Check metric cardinality: `prometheus_tsdb_head_series` metric
2. Identify high-cardinality metrics: `topk(10, count by (__name__)({__name__=~".+"}))`
3. Review metric labeling (avoid high-cardinality labels like user IDs, request IDs)

**Remediation**:
- Remove high-cardinality labels from metrics
- Use exemplars or logs for high-cardinality data
- Aggregate metrics before ingestion
- Drop high-cardinality metrics at collector level

### Storage Capacity Exceeded

**Symptoms**: Storage backend rejecting writes, disk full alerts, retention shorter than configured

**Diagnosis**:
1. Check storage utilization: `df -h` on storage nodes
2. Check retention policies vs. actual retention
3. Review ingestion rates (may have increased)
4. Check for storage leaks (metrics/logs not being cleaned up)

**Remediation**:
- Increase storage capacity (disk size, nodes)
- Reduce retention periods temporarily
- Reduce ingestion (sampling, log level reduction)
- Clean up old data: `promtool tsdb clean` (Prometheus)

### Query Performance Degradation

**Symptoms**: Dashboard load times increasing, query timeouts, high CPU on storage backends

**Diagnosis**:
1. Check query latency: `histogram_quantile(0.95, rate(prometheus_engine_query_duration_seconds_bucket[5m]))`
2. Identify slow queries (review query logs)
3. Check storage backend resource utilization
4. Review query complexity (too many time series, long time ranges)

**Remediation**:
- Optimize queries (reduce time range, use recording rules)
- Add query timeouts and limits
- Scale storage backend horizontally
- Use query caching where appropriate

### Missing Logs or Metrics

**Symptoms**: Expected logs/metrics not appearing, gaps in time series

**Diagnosis**:
1. Check collector ingestion rates
2. Check application instrumentation (verify metrics/logs are being emitted)
3. Check for sampling filters (may be dropping data)
4. Review collector configuration for drop rules

**Remediation**:
- Verify application is emitting metrics/logs (check application logs)
- Review collector configuration (filters, sampling)
- Check network connectivity (collector to application, collector to storage)
- Verify storage backend is accepting writes

## Scaling

### Collector Scaling

**Horizontal Scaling**: Scale collectors based on ingestion load:
- Monitor ingestion rate per collector
- Scale when ingestion rate > 80% of capacity
- Use load balancing (round-robin) for collector endpoints

**Resource Scaling**: Increase CPU/memory when:
- Collector CPU > 70% sustained
- Collector memory > 80%
- Ingestion rate limited by resources

**Auto-Scaling Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: otel-collector-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: otel-collector
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Storage Backend Scaling

**Prometheus Scaling**:
- Vertical: Increase memory/CPU for single instance
- Horizontal: Use Prometheus federation or Thanos for long-term storage
- Sharding: Split metrics by service/team to reduce per-instance load

**Log Storage Scaling** (Loki/Elasticsearch):
- Horizontal: Add nodes to cluster
- Index management: Adjust index sharding and retention
- Use object storage backend (S3) for long-term storage

**Trace Storage Scaling** (Jaeger/Tempo):
- Horizontal: Scale trace storage backends
- Sampling: Increase sampling rate reduction to manage volume
- Use object storage for long-term trace storage

### Cost Management

**Metric Cardinality Control**:
- Enforce labeling standards (avoid high-cardinality labels)
- Drop high-cardinality metrics at collector
- Use recording rules to pre-aggregate metrics

**Trace Sampling Budgets**:
- Head-based sampling: Sample 1-10% of traces (adjust based on volume)
- Tail-based sampling: Sample 100% of error traces, sample success traces
- Use sampling decisions consistently across services

**Log Volume Reduction**:
- Reduce log verbosity (INFO → WARN for non-critical logs)
- Use structured logging for better filtering
- Drop noisy logs at collector level
- Archive old logs to cheaper storage

## Backup and Recovery

### Configuration Backup

**Alert Rules**: Backup Prometheus alert rules, Grafana dashboards, and alertmanager configurations:
```bash
# Backup Prometheus rules
kubectl get prometheusrule -o yaml > prometheus-rules-backup.yaml

# Backup Grafana dashboards (export via API)
curl http://grafana:3000/api/dashboards/db/my-dashboard > dashboard.json
```

**Collector Configuration**: Backup OpenTelemetry collector configurations:
```bash
kubectl get configmap otel-collector-config -o yaml > collector-config-backup.yaml
```

### Storage Backend Backup

**Prometheus**: Prometheus data is typically not backed up (stateless, can rebuild from metrics). For long-term retention, use Thanos or similar.

**Logs**: Log storage (Loki, Elasticsearch) may require backups for compliance:
- Export logs to object storage (S3) for long-term retention
- Use snapshot/restore features if available

**Traces**: Trace storage typically not backed up (high volume, can rebuild). Archive critical traces to object storage if needed.

### Recovery Procedures

**RPO/RTO**:
- RPO: Near-zero (observability data is continuously generated)
- RTO: < 30 minutes (restore collectors, verify ingestion)

**Disaster Recovery**:
1. Restore collector configurations
2. Restore storage backends
3. Restore alert rules and dashboards
4. Verify ingestion and alerting
5. Monitor for data gaps

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily**:
- Review alert firing rates (reduce noise)
- Check storage utilization trends
- Monitor ingestion rates for anomalies

**Weekly**:
- Review and tune alert thresholds
- Review dashboard usage (remove unused)
- Check for high-cardinality metrics
- Review SLO burn rates and error budgets

**Monthly**:
- Review and update retention policies
- Audit metric cardinality
- Review and optimize queries (recording rules)
- Review sampling rates and adjust if needed
- Cost analysis (ingestion, storage costs)

**Quarterly**:
- Dashboard ownership review
- SLO review and updates
- Capacity planning (storage, ingestion)
- Observability stack upgrades
- Review and update runbooks

### SLO Review Cadence

**Weekly SLO Reviews**:
- Review error budgets consumed
- Analyze burn rate trends
- Identify services approaching SLO violations
- Plan remediation if needed

**Monthly SLO Reviews**:
- Review SLO targets (are they still appropriate?)
- Update SLOs based on business requirements
- Document SLO changes in ADRs
- Review alerting thresholds

**SLO Documentation**:
- Document SLO targets and error budgets
- Document how SLOs are measured
- Document remediation procedures for SLO violations

### Dashboard Maintenance

**Ownership**: Assign owners to dashboards, review quarterly.

**Staleness Review**: Remove or update dashboards that:
- Reference deprecated services
- Show incorrect or outdated metrics
- Are not accessed for 90+ days

**Dashboard Updates**: Update dashboards when:
- Services are renamed or restructured
- Metrics are renamed or deprecated
- New services are added

### Log Retention Management

**Retention Policy Review**:
- Review retention policies quarterly
- Adjust based on compliance requirements and costs
- Use tiered storage (hot/warm/cold) to optimize costs

**Log Lifecycle Automation**:
- Automate log archival to object storage
- Automate log deletion after retention period
- Monitor and alert on retention policy violations

### Collector Upgrades

**Upgrade Procedure**:
1. Review release notes for breaking changes
2. Test in development/staging
3. Update collector configuration if needed
4. Deploy upgrade (rolling update)
5. Monitor ingestion rates and errors
6. Verify dashboards and alerts still work

**OpenTelemetry Collector Upgrades**:
- Follow semantic versioning (minor versions typically safe)
- Test receiver/processor/exporter compatibility
- Update configuration for deprecated features

## On-Call Considerations

### What On-Call Engineers Need to Know

**Observability Stack Topology**: Understand collector locations, storage backend locations, and how data flows.

**Critical Dashboards**: Know which dashboards are essential for incident response (service health, error rates, latency).

**Common Commands**:
```bash
# Check collector status
kubectl get pods -l app=otel-collector

# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Query Prometheus
curl 'http://prometheus:9090/api/v1/query?query=up'

# Check Loki ingestion
curl http://loki:3100/ready

# Check Grafana
curl http://grafana:3000/api/health
```

**Escalation Paths**:
1. Check observability stack health (5 minutes)
2. Check storage backend status (10 minutes)
3. Check collector logs and configuration (15 minutes)
4. Escalate to platform/infrastructure if infrastructure issue (20 minutes)
5. Escalate to observability team lead if unresolved (30 minutes)

### Runbook Quick Reference

- **No Metrics/Logs**: Check collectors → Check storage backends → Check network → Verify application instrumentation
- **High Cardinality**: Identify high-cardinality metrics → Remove high-cardinality labels → Drop metrics if needed
- **Storage Full**: Check disk usage → Reduce retention → Reduce ingestion → Increase capacity
- **Slow Queries**: Check query complexity → Optimize queries → Scale storage → Use recording rules
- **Alert Noise**: Review alert rules → Tune thresholds → Group alerts → Suppress during maintenance

### Critical Alerts

- **Observability stack down**: Critical, impacts all monitoring
- **Storage > 90% capacity**: Critical, may cause data loss
- **Ingestion rate dropping > 50%**: Warning, may indicate application issues
- **High cardinality detected**: Warning, may cause storage issues
- **SLO error budget exhausted**: Critical, service quality degraded

### Alert Tuning Best Practices

**Multi-Window Burn Rate Alerts**: Use burn rate alerts instead of simple thresholds to detect SLO violations early:
```yaml
# Alert if error budget will be exhausted in 6 hours (short window) or 3 days (long window)
- alert: HighErrorRate
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      /
      sum(rate(http_requests_total[5m]))
    ) > 0.01
  for: 5m
```

**Alert Grouping**: Group related alerts to reduce noise:
```yaml
group_by: ['alertname', 'cluster', 'service']
group_wait: 10s
group_interval: 10s
```

**Alert Inhibition**: Suppress lower-severity alerts when higher-severity alerts fire:
```yaml
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster']
```
