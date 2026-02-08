# Incident Response Checklist

Use this checklist when responding to a production incident. Prioritize containment, then diagnosis, then resolution.

## Immediate (Containment)

- [ ] **Assess severity** -- How many users are affected? Is data at risk?
- [ ] **Check feature toggles** -- Can the impacted feature be disabled? → [Feature Toggles](../facets/feature-toggles/best-practices.md)
- [ ] **Check recent deployments** -- Was anything deployed recently that correlates?
- [ ] **Consider rollback** -- Is rolling back safe and faster than fixing forward? → [CI/CD](../facets/ci-cd/best-practices.md)
- [ ] **Communicate status** -- Inform stakeholders about the issue and expected timeline

## Diagnosis

- [ ] **Check dashboards and metrics** -- Any anomalies in key metrics? → [Observability](../facets/observability/architecture.md)
- [ ] **Review logs** -- Filter by timestamp, service, error level → [Observability](../facets/observability/best-practices.md)
- [ ] **Check distributed traces** -- Follow the request path through services → [Observability](../facets/observability/architecture.md)
- [ ] **Check external dependencies** -- Are third-party services healthy?
- [ ] **Check database** -- Connection pool exhaustion, slow queries, lock contention → [Data Persistence](../facets/data-persistence/best-practices.md)
- [ ] **Check resource utilization** -- CPU, memory, disk, network

## Resolution

- [ ] **Implement fix or workaround** -- Prioritize speed over perfection
- [ ] **Test fix** -- Verify in staging if time allows, or use feature toggle for gradual rollout
- [ ] **Deploy fix** -- Follow deployment procedures → [CI/CD](../facets/ci-cd/best-practices.md)
- [ ] **Verify resolution** -- Confirm metrics return to normal
- [ ] **Communicate resolution** -- Update stakeholders

## Post-Incident

- [ ] **Write incident report** -- Timeline, root cause, impact, resolution
- [ ] **Identify preventive measures** -- What would have caught this earlier?
- [ ] **Update monitoring** -- Add alerts for the failure mode → [Observability](../facets/observability/options.md)
- [ ] **Update error handling** -- Improve resilience for this failure path → [Error Handling](../facets/error-handling/best-practices.md)
- [ ] **Add test coverage** -- Write tests that would catch this regression → [Testing](../facets/testing/best-practices.md)
- [ ] **Update runbook** -- Document the diagnosis and resolution steps
- [ ] **Schedule follow-up work** -- Create tickets for longer-term improvements
