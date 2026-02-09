# Data Persistence — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Data persistence systems require constant vigilance for connection health, query performance, and data integrity. In production, watch for:

- **Connection pool exhaustion**: Monitor active connections vs. max pool size (e.g., HikariCP `active` vs `maximum`). Exhaustion causes request timeouts and cascading failures.
- **Replication lag**: Read replicas must stay within acceptable latency (typically < 100ms for PostgreSQL). Lag beyond 1 second indicates replication issues.
- **Transaction deadlocks**: Monitor deadlock detection logs. Frequent deadlocks suggest application-level locking issues or missing indexes.
- **Long-running queries**: Queries exceeding 30 seconds should be investigated. They block resources and can cause connection pool exhaustion.

See [architecture.md](architecture.md) for design decisions around replication and connection pooling.

## Monitoring and Alerting

### Essential Metrics

**Connection Pool Metrics** (HikariCP example):
- `hikari_connections_active` — Alert if > 80% of max pool size
- `hikari_connections_idle` — Should be > 0 for headroom
- `hikari_connections_pending` — Alert if > 0 (requests waiting for connections)
- `hikari_connections_timeout` — Alert on any timeouts

**Database Health**:
- `postgresql_up` — Database availability (0 = down)
- `postgresql_replication_lag_bytes` — Alert if > 10MB or > 1 second
- `postgresql_replication_lag_seconds` — Alert if > 1 second
- `postgresql_connections` — Total connections (alert if approaching max_connections)

**Query Performance**:
- `postgresql_stat_statements_calls` — Query call frequency
- `postgresql_stat_statements_mean_exec_time` — Alert if > 1 second for critical queries
- `postgresql_stat_statements_max_exec_time` — Alert if > 30 seconds

**Storage**:
- `postgresql_database_size_bytes` — Alert at 80% of disk capacity
- `postgresql_table_size_bytes` — Monitor large table growth trends

### Log Aggregation

- **Slow query logs**: Enable `log_min_duration_statement = 1000` (1 second) in PostgreSQL. Aggregate in centralized logging (e.g., ELK, Loki).
- **Connection logs**: Track connection attempts, failures, and terminations.
- **Replication logs**: Monitor WAL shipping errors and replication slot lag.

### Dashboards

- **Connection Pool Dashboard**: Active/idle/pending connections, wait times, timeout rates
- **Replication Dashboard**: Lag (bytes and seconds), replication slot status, WAL shipping status
- **Query Performance Dashboard**: Top 10 slow queries, query frequency, execution time percentiles
- **Storage Dashboard**: Database size, table sizes, index bloat, disk usage

## Incident Runbooks

### Connection Pool Exhaustion

**Symptoms**: High `hikari_connections_pending`, request timeouts, 503 errors

**Diagnosis**:
```bash
# Check active connections
kubectl exec -it <pod> -- curl http://localhost:8080/actuator/metrics/hikari.connections.active

# Check for long-running queries blocking connections
kubectl exec -it <postgres-pod> -- psql -U postgres -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '30 seconds';"
```

**Remediation**:
1. Identify and kill long-running queries: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...`
2. Temporarily increase pool size if justified (monitor for underlying query issues)
3. Check for connection leaks (connections not returned to pool)
4. Review recent deployments for query changes

### Replication Lag

**Symptoms**: Stale reads from replicas, `postgresql_replication_lag_seconds` > 1

**Diagnosis**:
```bash
# Check replication lag
kubectl exec -it <postgres-pod> -- psql -U postgres -c "SELECT client_addr, state, sync_state, pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS lag_bytes FROM pg_stat_replication;"

# Check replication slot lag
SELECT slot_name, pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes FROM pg_replication_slots;
```

**Remediation**:
1. Check network connectivity between primary and replica
2. Verify replica disk I/O performance (check `iostat`)
3. Check for large transactions on primary (consider breaking into smaller batches)
4. If lag persists, consider adding more replicas or increasing replica resources
5. For critical lag, temporarily route reads to primary (with capacity monitoring)

### Database Lock Contention

**Symptoms**: Deadlocks in logs, queries timing out, application errors mentioning locks

**Diagnosis**:
```bash
# Check for blocking queries
SELECT blocked_locks.pid AS blocked_pid, blocking_locks.pid AS blocking_pid, blocked_activity.query AS blocked_query, blocking_activity.query AS blocking_query FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation AND blocking_locks.pid != blocked_locks.pid JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid WHERE NOT blocked_locks.granted;
```

**Remediation**:
1. Identify blocking query and evaluate if it can be optimized (add indexes, reduce transaction scope)
2. If safe, terminate blocking query: `SELECT pg_terminate_backend(<blocking_pid>);`
3. Review application code for missing transaction boundaries or long-running transactions
4. Consider advisory locks for application-level coordination

### Migration Rollback

**Symptoms**: Application errors after schema migration, data corruption, constraint violations

**Diagnosis**:
- Check Flyway/Liquibase migration history: `SELECT * FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;`
- Verify current schema matches expected state

**Remediation**:
1. **Flyway**: Use `flyway undo` if undo scripts exist (requires Flyway Teams). Otherwise, manually create rollback migration.
2. **Blue/Green Deployment**: Switch traffic back to previous version with old schema.
3. **Manual Rollback**: Create reverse migration script, test in staging, apply to production:
   ```sql
   -- Example: Rollback adding a column
   ALTER TABLE users DROP COLUMN IF EXISTS new_field;
   ```
4. Update migration version in Flyway history if needed: `UPDATE flyway_schema_history SET success = false WHERE version = 'X.X.X';`

## Scaling

### Horizontal Scaling (Read Replicas)

**When to add replicas**:
- Read replica CPU > 70% sustained
- Replication lag increases with load
- Read query latency > p95 SLO

**Procedure**:
1. Provision new replica instance (match primary specs initially)
2. Configure replication: `pg_basebackup` or streaming replication
3. Verify replication lag < 100ms
4. Update application connection strings to include new replica
5. Monitor connection distribution and query performance

**Connection Pool Configuration**:
- Use read/write splitting in connection pool (e.g., HikariCP with `readOnly` flag)
- Distribute read traffic across replicas (round-robin or weighted)

### Vertical Scaling

**When to scale up**:
- CPU > 80% sustained
- Memory pressure (OOM kills, high swap usage)
- Disk I/O saturation (await > 20ms)

**Procedure**:
1. Scale up instance (CPU/memory) during maintenance window
2. For PostgreSQL, consider `shared_buffers` tuning (typically 25% of RAM)
3. Monitor query performance improvements
4. Consider `work_mem` adjustments for complex queries

### Connection Pool Scaling

**HikariCP Configuration**:
```properties
# Base configuration
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5

# Scale based on application instances
# Formula: (max_pool_size * num_instances) < (database_max_connections * 0.8)
```

**Monitoring**: Alert if `(active_connections / max_connections) > 0.8` across all application instances.

## Backup and Recovery

### Backup Strategy

**Full Backups** (`pg_dump`):
- **Frequency**: Daily at low-traffic window (e.g., 2 AM)
- **Retention**: 30 days locally, 90 days in cold storage (S3, etc.)
- **Command**: `pg_dump -Fc -f backup_$(date +%Y%m%d).dump <database>`

**WAL Archiving** (Point-in-Time Recovery):
- **Enable**: `wal_level = replica`, `archive_mode = on`
- **Archive Command**: `archive_command = 'aws s3 cp %p s3://backups/wal/%f'`
- **Retention**: 7 days of WAL files (adjust based on backup frequency and RPO)

**Continuous Archiving**:
- Stream WAL to object storage (S3, GCS)
- Enable replication slots for logical replication consumers

### Recovery Procedures

**RPO (Recovery Point Objective)**: 15 minutes (WAL archiving every 15 minutes)
**RTO (Recovery Time Objective)**: 1 hour (restore from backup + replay WAL)

**Point-in-Time Recovery**:
```bash
# 1. Restore base backup
pg_restore -d postgres backup_20260209.dump

# 2. Configure recovery
echo "restore_command = 'aws s3 cp s3://backups/wal/%f %p'" > recovery.conf
echo "recovery_target_time = '2026-02-09 14:30:00'" >> recovery.conf

# 3. Start PostgreSQL (will enter recovery mode)
# 4. Verify data integrity
# 5. Promote to primary: SELECT pg_wal_replay_resume();
```

**Database-Level Recovery**:
- Restore specific database: `pg_restore -d <target_db> backup.dump`
- Verify with application smoke tests

**Table-Level Recovery**:
- Extract table from backup: `pg_restore -t <table_name> backup.dump`
- Restore to temporary database, then copy data back

### Backup Verification

- **Weekly**: Restore backup to test environment, verify schema and sample data
- **Monthly**: Full recovery drill (document RTO achieved)

## Maintenance Procedures

### Vacuum and Analyze

**Autovacuum Tuning** (PostgreSQL):
```sql
-- Check autovacuum activity
SELECT schemaname, tablename, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze 
FROM pg_stat_user_tables 
WHERE last_autovacuum < NOW() - INTERVAL '7 days';

-- Manual vacuum for large tables
VACUUM ANALYZE large_table;
```

**Schedule**: Autovacuum runs automatically. Monitor `pg_stat_progress_vacuum` for long-running vacuums.

**Vacuum Full** (requires downtime):
- Use when table bloat > 30%
- Schedule during maintenance window
- `VACUUM FULL <table>;` (locks table)

### Index Maintenance

**Bloat Detection**:
```sql
-- Check index bloat
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
       pg_size_pretty(pg_relation_size(indexrelid) - pg_relation_size(indexrelid, 'vm')) AS bloat_size
FROM pg_stat_user_indexes
WHERE pg_relation_size(indexrelid) > 100000000  -- > 100MB
ORDER BY bloat_size DESC;
```

**Index Rebuild**:
- `REINDEX INDEX CONCURRENTLY <index_name>;` (non-blocking, PostgreSQL 12+)
- Schedule during low-traffic periods

**Unused Index Detection**:
```sql
-- Find indexes with low usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan < 10  -- Adjust threshold
ORDER BY idx_scan;
```

Review and drop unused indexes (reduces write overhead).

### Migration Maintenance

**Flyway**:
- Review migration history: `SELECT * FROM flyway_schema_history ORDER BY installed_rank DESC;`
- Clean up failed migrations: `flyway repair` (use with caution)
- Version management: Ensure sequential version numbers, no gaps

**Migration Rollback Testing**:
- Test rollback scripts in staging before production deployment
- Document rollback procedures for each migration

### Connection Pool Maintenance

**HikariCP Health Checks**:
- Monitor connection validation: `hikari_connections_validation_time`
- Review connection timeout settings: `connection-timeout`, `validation-timeout`
- Check for connection leaks (connections not closed): Monitor `active` connections that never return to `idle`

**Pool Sizing Review** (Quarterly):
- Analyze peak connection usage
- Adjust `maximum-pool-size` based on actual usage patterns
- Ensure `(max_pool_size * app_instances) < (db_max_connections * 0.8)`

## On-Call Considerations

### Immediate Actions

1. **Connection pool exhaustion**: Check for long-running queries, kill if safe, increase pool size temporarily if needed
2. **Replication lag > 5 seconds**: Route reads to primary, investigate replica I/O or network issues
3. **Database unavailable**: Check primary instance health, failover to replica if configured (verify replication lag first)
4. **Migration failure**: Assess impact (data corruption?), execute rollback procedure if safe

### Escalation Path

- **Level 1 (On-Call)**: Connection issues, replication lag, query performance degradation
- **Level 2 (Database Team)**: Migration failures, data corruption, replication failures, backup/restore
- **Level 3 (Architecture Team)**: Schema design issues, scaling decisions, architectural changes

### Key Commands Cheat Sheet

```bash
# Connection pool status
curl http://localhost:8080/actuator/metrics/hikari.connections.active

# Long-running queries
psql -c "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '30 seconds';"

# Replication lag
psql -c "SELECT client_addr, pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS lag_bytes FROM pg_stat_replication;"

# Kill query
SELECT pg_terminate_backend(<pid>);

# Database size
psql -c "SELECT pg_size_pretty(pg_database_size('mydb'));"

# Table sizes
psql -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Documentation References

- See [architecture.md](architecture.md) for replication and connection pool design
- See [best-practices.md](best-practices.md) for query optimization guidelines
- See [gotchas.md](gotchas.md) for common production issues
