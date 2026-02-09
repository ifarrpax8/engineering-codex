# Event-Driven Architecture — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Event-driven systems require careful monitoring of consumer lag, message processing rates, and broker health. The primary operational concerns are ensuring events are processed in a timely manner and handling failures gracefully.

**Consumer Lag**: The difference between the latest message offset and the consumer's current position. High lag indicates consumers cannot keep up with producers. Monitor lag per consumer group and per partition.

**Dead Letter Queues (DLQ)**: Failed messages should be routed to DLQs for inspection and potential replay. Regularly monitor DLQ depth and investigate root causes.

**Idempotency**: Ensure consumers handle duplicate messages gracefully. Monitor for duplicate processing indicators (duplicate event IDs, idempotency key violations).

**Partition Rebalancing**: In Kafka, consumer group rebalancing occurs when consumers join or leave. Frequent rebalancing indicates instability. Monitor rebalance frequency and duration.

**Schema Evolution**: Schema Registry manages event schemas. Monitor schema compatibility and version changes. Breaking schema changes require coordinated deployments.

## Monitoring and Alerting

### Essential Metrics

**Consumer Lag**:
- Kafka: Consumer group lag per topic/partition
- RabbitMQ: Queue depth per queue
- Alert threshold: Lag > 10,000 messages or lag increasing > 1,000 messages/minute

**Message Processing**:
- Messages consumed per second
- Processing time per message (p50, p95, p99)
- Error rate (failed messages / total messages)
- Alert threshold: Error rate > 1% sustained for 5 minutes

**Broker Health**:
- Kafka: Broker availability, partition leader elections, under-replicated partitions
- RabbitMQ: Node status, queue depth, connection count
- Alert threshold: Broker unavailable, > 5% partitions under-replicated

**DLQ Depth**:
- Messages in DLQ per topic/queue
- Alert threshold: DLQ depth > 100 messages (investigate), > 1,000 messages (critical)

**Schema Registry**:
- Schema compatibility checks
- Schema version changes
- Alert threshold: Incompatible schema changes, high schema change rate

### Kafka-Specific Monitoring

```bash
# Check consumer group lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group --describe

# Check topic details
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic my-topic

# Check broker status
kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

**Key Metrics**:
- `kafka.consumer.lag` - Consumer lag per partition
- `kafka.consumer.records-consumed-rate` - Consumption rate
- `kafka.server.replication.under-replicated-partitions` - Under-replicated partitions
- `kafka.controller.active-controller-count` - Should be 1

### RabbitMQ-Specific Monitoring

```bash
# Check queue depth
rabbitmqctl list_queues name messages consumers

# Check node status
rabbitmqctl node_health_check

# Check connections
rabbitmqctl list_connections
```

**Key Metrics**:
- Queue depth per queue
- Message publish rate
- Message consumption rate
- Connection count
- Memory usage

### Alert Thresholds

- **Critical**: Consumer lag > 100,000 messages, broker unavailable, DLQ depth > 1,000, schema incompatibility
- **Warning**: Consumer lag > 10,000, error rate > 1%, under-replicated partitions, frequent rebalancing
- **Info**: Schema version changes, partition reassignments, consumer group changes

### Dashboards

Maintain dashboards showing:
- Consumer lag trends (per consumer group, per topic)
- Message throughput (produce vs consume rates)
- Error rates and DLQ depth
- Broker health (Kafka: broker status, under-replicated partitions; RabbitMQ: node status, queue depths)
- Schema Registry activity
- Consumer group membership and rebalancing events

## Incident Runbooks

### High Consumer Lag

**Symptoms**: Consumer lag increasing, messages not being processed, downstream systems stale

**Diagnosis**:
1. Check consumer group lag: `kafka-consumer-groups.sh --group my-group --describe`
2. Identify slow partitions (lag not uniform across partitions)
3. Check consumer application logs for errors or slow processing
4. Check consumer resource utilization (CPU, memory)
5. Review recent deployments that might have introduced performance regression

**Remediation**:
- If consumer application slow: Scale consumers horizontally, optimize processing logic, check for blocking operations
- If partition imbalance: Redistribute partitions, increase partitions if needed (requires careful planning)
- If downstream dependency slow: Check downstream service health, enable circuit breaker
- If resource exhaustion: Increase consumer resources or scale horizontally
- Temporary: Pause producers if lag is critical (coordinate with teams)

### Consumer Group Stuck / Not Processing

**Symptoms**: Consumer lag not decreasing, no messages consumed, consumer group shows no active members

**Diagnosis**:
1. Check consumer group status: `kafka-consumer-groups.sh --group my-group --describe`
2. Check if consumers are running: `kubectl get pods -l app=consumer-service`
3. Check consumer logs for errors
4. Check for rebalancing loops (frequent rebalancing)

**Remediation**:
- If consumers crashed: Restart consumers, check for OOM kills or exceptions
- If rebalancing loop: Check consumer session timeout, increase if needed; check for slow consumers causing rebalancing
- If no consumers running: Restart consumer deployment
- Reset consumer group offsets if needed (use with caution): `kafka-consumer-groups.sh --group my-group --reset-offsets --to-earliest --topic my-topic --execute`

### DLQ Filling Up

**Symptoms**: DLQ depth increasing, messages accumulating in DLQ

**Diagnosis**:
1. Check DLQ depth: `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic dlq-topic --from-beginning --max-messages 10`
2. Sample DLQ messages to identify error patterns
3. Check consumer application logs for the errors causing DLQ routing
4. Identify if issue is transient or systematic

**Remediation**:
- If transient errors: Messages may be replayable after fix, replay from DLQ
- If systematic errors: Fix root cause in consumer application, then replay DLQ messages
- If schema incompatibility: Update consumer to handle new schema version, replay messages
- Purge DLQ only after investigation and if messages are not needed: `kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic dlq-topic` (recreate if needed)

### Schema Incompatibility

**Symptoms**: Consumers failing to deserialize messages, schema registry errors, DLQ filling with deserialization errors

**Diagnosis**:
1. Check Schema Registry for incompatible schemas: `curl http://schema-registry:8081/subjects/my-topic-value/versions`
2. Review recent schema changes
3. Check consumer logs for deserialization errors
4. Verify schema compatibility mode (BACKWARD, FORWARD, FULL)

**Remediation**:
- If backward incompatible change: Rollback producer to previous schema version
- Update compatibility mode if appropriate (requires Schema Registry admin)
- Update consumers to handle new schema version
- Replay messages from DLQ after consumer update

### Partition Rebalancing Issues

**Symptoms**: Frequent rebalancing, consumers unable to join group, processing pauses during rebalancing

**Diagnosis**:
1. Check rebalance frequency in metrics
2. Check consumer session timeout settings
3. Check for slow consumers (processing time > session timeout)
4. Review consumer group membership: `kafka-consumer-groups.sh --group my-group --describe`

**Remediation**:
- Increase `session.timeout.ms` if consumers are legitimately slow
- Optimize slow consumer processing
- Ensure consumers handle rebalancing gracefully (commit offsets, release resources)
- Check for network issues causing disconnections

### Broker Maintenance / Under-Replicated Partitions

**Symptoms**: Under-replicated partitions, broker unavailable, leader election failures

**Diagnosis**:
1. Check broker status: `kafka-broker-api-versions.sh --bootstrap-server localhost:9092`
2. Check under-replicated partitions: `kafka-topics.sh --bootstrap-server localhost:9092 --describe | grep UnderReplicated`
3. Check broker logs for disk, network, or resource issues
4. Check ZooKeeper/KRaft controller status

**Remediation**:
- If broker down: Restart broker, check for hardware issues
- If disk full: Clean up old logs, increase disk size
- If network partition: Check network connectivity, resolve network issues
- If under-replicated: Wait for replication to catch up, or trigger preferred leader election: `kafka-leader-election.sh --bootstrap-server localhost:9092 --topic my-topic --partition 0 --election-type PREFERRED`

## Scaling

### Consumer Scaling

**Horizontal Scaling**: Add more consumer instances to increase throughput. Ensure:
- Consumer group has enough partitions (can't scale beyond partition count)
- Processing is stateless or state is externalized
- Idempotency is handled correctly

**Partition Scaling**: Increase partitions to allow more parallel consumers:
- Requires careful planning (partition count affects ordering guarantees)
- Use `kafka-topics.sh --alter --topic my-topic --partitions 10` (increase only, cannot decrease)
- Rebalance consumer group after partition increase

**When to Scale Consumers**:
- Consumer lag consistently > 10,000 messages
- CPU/memory utilization > 70% sustained
- Processing time per message increasing

**When to Scale Partitions**:
- Need more parallelism than current partition count
- Consumer lag persists despite scaling consumers
- Partition count < desired consumer count

### Producer Scaling

**Horizontal Scaling**: Add more producer instances. Monitor:
- Produce rate per producer
- Broker load
- Network bandwidth

**Batching**: Configure producer batching (`batch.size`, `linger.ms`) to increase throughput:
- Larger batches = higher throughput but higher latency
- Balance based on latency requirements

### Broker Scaling

**Kafka Cluster Scaling**:
- Add brokers to increase capacity and fault tolerance
- Reassign partitions to new brokers for load balancing
- Monitor broker resource utilization (CPU, disk, network)

**RabbitMQ Cluster Scaling**:
- Add nodes to cluster for high availability
- Use mirrored queues for redundancy
- Monitor node health and queue distribution

## Backup and Recovery

### Event Replay

**Kafka**: Events are retained based on retention policy (time or size). To replay:
1. Reset consumer group offsets: `kafka-consumer-groups.sh --group my-group --reset-offsets --to-datetime 2024-01-01T00:00:00Z --topic my-topic --execute`
2. Or reset to earliest: `--to-earliest`
3. Or reset to latest: `--to-latest`

**RabbitMQ**: Replay from DLQ or republish messages. No built-in offset management.

### Schema Backup

Backup Schema Registry schemas:
```bash
# Export all schemas
curl http://schema-registry:8081/subjects | jq -r '.[]' | while read subject; do
  curl http://schema-registry:8081/subjects/$subject/versions/latest > schemas/$subject.json
done
```

### Broker Configuration Backup

**Kafka**: Backup broker configuration, topic configurations, and consumer group offsets (stored in `__consumer_offsets` topic).

**RabbitMQ**: Backup definitions (queues, exchanges, bindings):
```bash
rabbitmqctl export_definitions definitions.json
```

### Recovery Procedures

**RPO/RTO**:
- RPO: Depends on retention policy (typically 7-30 days for Kafka)
- RTO: < 15 minutes (restore consumers, replay if needed)

**Disaster Recovery**:
1. Restore broker cluster from backup
2. Restore Schema Registry schemas
3. Verify topic/queue configurations
4. Restart consumers and verify processing
5. Monitor consumer lag and error rates

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily**:
- Monitor consumer lag and DLQ depth
- Review error rates and failed message patterns
- Check broker health (disk usage, under-replicated partitions)

**Weekly**:
- Review and purge DLQ messages (after investigation)
- Analyze consumer performance trends
- Review schema changes and compatibility

**Monthly**:
- Review partition distribution and rebalance if needed
- Audit consumer group configurations
- Review retention policies and adjust if needed
- Check for unused topics/queues and clean up

**Quarterly**:
- Capacity planning (throughput trends, partition needs)
- Broker maintenance (upgrades, disk expansion)
- Schema Registry cleanup (remove old schema versions)
- Review and optimize consumer configurations

### Broker Maintenance

**Kafka Broker Upgrades**:
1. Upgrade one broker at a time (rolling upgrade)
2. Verify broker health after each upgrade
3. Check for under-replicated partitions
4. Monitor consumer lag during upgrade

**Disk Maintenance**:
- Monitor disk usage: `df -h` on broker nodes
- Clean up old logs if retention policy allows: `kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe`
- Increase disk size before reaching 80% capacity

**Partition Reassignment**:
- Reassign partitions for load balancing: `kafka-reassign-partitions.sh`
- Monitor reassignment progress
- Verify data replication after reassignment

### Schema Registry Operations

**Schema Evolution**:
1. Verify compatibility before publishing new schema version
2. Test consumer with new schema version
3. Deploy consumer update before producer update (for backward compatibility)
4. Monitor for deserialization errors

**Schema Cleanup**:
- Remove old schema versions (requires Schema Registry admin)
- Document schema changes in ADRs
- Maintain schema compatibility documentation

### DLQ Operations

**DLQ Inspection**:
```bash
# Sample messages from DLQ
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic dlq-topic --from-beginning --max-messages 100

# Count messages in DLQ
kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic dlq-topic --time -1
```

**DLQ Replay**:
1. Identify root cause of failures
2. Fix consumer application if needed
3. Replay messages: Reset consumer group offset to DLQ topic, or republish messages to original topic
4. Monitor for repeated failures

**DLQ Purge**: Only after investigation and confirmation messages are not needed:
```bash
# Delete DLQ topic (recreate if needed)
kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic dlq-topic
```

### Idempotency Verification

**Monitoring**:
- Track duplicate event IDs in consumer logs
- Monitor idempotency key violations
- Alert on duplicate processing patterns

**Testing**:
- Replay events and verify idempotent handling
- Test duplicate message scenarios
- Verify idempotency keys are properly set by producers

## On-Call Considerations

### What On-Call Engineers Need to Know

**Consumer Topology**: Understand which consumers read from which topics, consumer group names, and processing dependencies.

**Broker Endpoints**: Know broker addresses, Schema Registry URL, and how to access management tools.

**Common Commands**:
```bash
# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --describe

# Check topic details
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic my-topic

# Sample messages
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic my-topic --from-beginning --max-messages 10

# Check broker status
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check Schema Registry
curl http://schema-registry:8081/subjects
```

**Escalation Paths**:
1. Check consumer lag and DLQ depth (5 minutes)
2. Check consumer application health and logs (10 minutes)
3. Check broker health (15 minutes)
4. Escalate to platform/infrastructure if broker issue (20 minutes)
5. Escalate to team lead if unresolved (30 minutes)

### Runbook Quick Reference

- **High Consumer Lag**: Check lag → Identify slow partitions → Check consumer resources → Scale consumers or optimize
- **DLQ Filling**: Sample DLQ messages → Identify error pattern → Fix root cause → Replay messages
- **Consumer Not Processing**: Check consumer status → Check logs → Check rebalancing → Restart if needed
- **Schema Errors**: Check Schema Registry → Verify compatibility → Update consumer → Replay messages
- **Broker Issues**: Check broker status → Check disk/network → Restart broker → Check replication

### Critical Alerts

- **Consumer lag > 100,000**: Critical, scale consumers immediately
- **DLQ depth > 1,000**: Critical, investigate and fix root cause
- **Broker unavailable**: Critical, restart broker, check infrastructure
- **Schema incompatibility**: Critical, rollback producer or update consumer
- **Under-replicated partitions > 5%**: Warning, check broker health
