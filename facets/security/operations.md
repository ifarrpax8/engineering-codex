# Security — Operations

## Contents

- [Production Operation](#production-operation)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Incident Runbooks](#incident-runbooks)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance Procedures](#maintenance-procedures)
- [On-Call Considerations](#on-call-considerations)

## Production Operation

Security operations require continuous vigilance and rapid response capabilities. Security controls must be operational 24/7 without impacting legitimate user access.

**Certificate Management**: TLS certificates must be renewed before expiration. Automated renewal (e.g., cert-manager) reduces risk of expired certificates causing outages.

**Secret Rotation**: Secrets (API keys, database passwords, service account tokens) must be rotated regularly. Zero-downtime rotation requires coordination between services.

**Vulnerability Management**: Security vulnerabilities must be patched according to SLAs (critical: 24-48 hours, high: 7 days, medium: 30 days). Automated scanning and alerting enable rapid response.

**Access Control**: Regular access reviews ensure users have appropriate permissions. Automated access reviews reduce risk of privilege creep.

**Incident Response**: Security incidents require rapid containment and investigation. Pre-defined playbooks and communication templates ensure consistent response.

## Monitoring and Alerting

### Essential Metrics

**Certificate Expiration**:
- Days until certificate expiration
- Alert threshold: Expiring in < 30 days (warning), < 7 days (critical)
- Monitor all TLS certificates (ingress, service mesh, API gateways)

**Secret Expiration**:
- Vault lease expiration (if using HashiCorp Vault)
- API key expiration dates
- Alert threshold: Expiring in < 7 days

**Vulnerability Alerts**:
- Critical vulnerabilities detected
- High vulnerabilities detected
- Alert threshold: Critical vulnerabilities (immediate), high vulnerabilities (within 24 hours)

**Security Events**:
- Failed authentication attempts (brute force detection)
- Unauthorized access attempts
- Privilege escalation attempts
- Alert threshold: > 10 failed attempts in 5 minutes, unauthorized access (immediate)

**WAF Events**:
- Blocked requests (by rule, by IP)
- False positive rate
- Alert threshold: Unusual spike in blocked requests, new attack patterns

### Alert Thresholds

- **Critical**: Security incident detected, certificate expired, critical vulnerability, unauthorized access
- **Warning**: Certificate expiring soon, high vulnerability, suspicious activity, WAF rule triggered
- **Info**: Medium vulnerabilities, access review due, secret rotation scheduled

### Dashboards

Maintain dashboards showing:
- Certificate expiration timeline (all certificates)
- Vulnerability status (by severity, by service)
- Security event trends (authentication failures, blocked requests)
- WAF activity (blocked requests, top attack patterns)
- Access review status (pending reviews, overdue reviews)

## Incident Runbooks

### Security Incident Detected

**Symptoms**: Unauthorized access, data breach indicators, malware detection, suspicious network activity

**Immediate Actions** (First 15 minutes):
1. **Contain**: Isolate affected systems (disable access, network isolation)
2. **Assess**: Determine scope of incident (what systems, what data)
3. **Notify**: Alert security team, on-call engineer, management
4. **Document**: Begin incident log with timeline of events

**Investigation**:
1. Review security logs (authentication, authorization, network)
2. Identify attack vector (vulnerability, misconfiguration, compromised credentials)
3. Determine data accessed or exfiltrated
4. Identify affected systems and services

**Remediation**:
1. Patch vulnerabilities or fix misconfigurations
2. Rotate compromised credentials (passwords, API keys, certificates)
3. Remove unauthorized access
4. Restore systems from clean backups if compromised
5. Implement additional monitoring for similar attacks

**Communication**:
- Use pre-defined communication templates
- Notify stakeholders (internal teams, customers if data breach)
- Document incident in post-mortem
- Update security controls based on lessons learned

### Certificate Expired

**Symptoms**: TLS handshake failures, certificate expiration errors in logs, users unable to access services

**Diagnosis**:
1. Check certificate expiration: `openssl x509 -in cert.pem -noout -dates`
2. Verify cert-manager status (if using): `kubectl get certificate`
3. Check certificate renewal logs

**Remediation**:
- **Immediate**: Manually renew certificate if automated renewal failed
- **Short-term**: Fix automated renewal (cert-manager configuration, DNS challenges)
- **Long-term**: Review certificate management process, add monitoring

**Certificate Renewal** (cert-manager):
```bash
# Check certificate status
kubectl describe certificate my-cert

# Force renewal (if needed)
kubectl annotate certificate my-cert cert-manager.io/issue-temporary-certificate=true
```

### Critical Vulnerability Detected

**Symptoms**: Vulnerability scanner alert, security advisory published, CVE assigned

**Immediate Actions**:
1. Assess vulnerability severity and exploitability
2. Identify affected services and systems
3. Check if vulnerability is actively exploited
4. Determine patch availability and deployment timeline

**Remediation Timeline**:
- **Critical**: Patch within 24-48 hours (or implement workaround)
- **High**: Patch within 7 days
- **Medium**: Patch within 30 days

**Patch Deployment**:
1. Test patch in development/staging
2. Deploy patch to production (coordinate with teams)
3. Verify patch is applied: `kubectl describe pod | grep Image`
4. Monitor for issues after patch deployment

**Workarounds**: If patch not immediately available:
- Implement network-level controls (WAF rules, firewall rules)
- Disable affected features if possible
- Increase monitoring for exploitation attempts

### Compromised Credentials

**Symptoms**: Unauthorized access, suspicious activity from user account, credential leak detected

**Immediate Actions**:
1. **Revoke**: Immediately revoke compromised credentials
2. **Rotate**: Rotate all related secrets (passwords, API keys, tokens)
3. **Audit**: Review access logs for unauthorized activity
4. **Notify**: Notify affected user, require password reset

**Credential Rotation**:
```bash
# Rotate Vault secret
vault kv patch secret/my-secret password="new-password"

# Rotate Kubernetes secret
kubectl create secret generic my-secret --from-literal=password=new-password --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/my-service
```

**Investigation**:
1. Determine how credentials were compromised (phishing, data breach, insider threat)
2. Review access logs for unauthorized activity
3. Identify data accessed or systems compromised
4. Update security controls to prevent recurrence

### WAF False Positives

**Symptoms**: Legitimate requests blocked, users unable to access services, high false positive rate

**Diagnosis**:
1. Review WAF logs for blocked requests
2. Identify blocked request patterns
3. Verify if requests are legitimate or attacks
4. Check WAF rule configurations

**Remediation**:
- If false positive: Adjust WAF rules (whitelist IPs, modify rule conditions)
- If legitimate attack: Keep rule, investigate source
- Temporary: Disable rule temporarily if blocking critical traffic (with approval)

**WAF Rule Update** (example):
```yaml
# Whitelist specific IP or path
rules:
  - name: allow-legitimate-path
    conditions:
      - field: path
        operator: equals
        value: /api/legitimate-endpoint
    action: allow
```

## Scaling

### Certificate Management Scaling

**Automated Certificate Management**: Use cert-manager or similar for automatic certificate provisioning and renewal:
- Reduces manual effort
- Prevents certificate expiration
- Scales to hundreds of certificates

**Certificate Storage**: Store certificates in Kubernetes secrets or external secret management (Vault):
- Kubernetes secrets: Simple, integrated with Kubernetes
- External secret management: Centralized, audit trail, rotation capabilities

### Secret Management Scaling

**Centralized Secret Management**: Use HashiCorp Vault or similar for secret management:
- Centralized rotation
- Audit trail
- Dynamic secrets (short-lived credentials)
- Integration with Kubernetes (CSI driver, sidecar injector)

**Secret Rotation Automation**:
- Automated rotation schedules
- Zero-downtime rotation (coordinate with services)
- Rotation notifications and alerts

### Vulnerability Scanning Scaling

**Automated Scanning**:
- CI/CD pipeline scanning (container images, dependencies)
- Runtime scanning (container runtime, host scanning)
- Network scanning (vulnerability assessments)

**Scanning Frequency**:
- Critical services: Daily
- Standard services: Weekly
- Low-risk services: Monthly

### Access Review Automation

**Automated Access Reviews**:
- Scheduled access reviews (quarterly, annually)
- Automated access review requests
- Access review dashboards and reports
- Automated access revocation for inactive users

## Backup and Recovery

### Certificate Backup

**Certificate Storage**: Backup certificates and private keys securely:
```bash
# Backup certificates (encrypted)
kubectl get secret tls-secret -o yaml | gpg --encrypt > cert-backup.gpg

# Store in secure backup location (encrypted object storage)
```

**Certificate Recovery**:
1. Restore certificates from backup
2. Verify certificate validity
3. Update Kubernetes secrets or cert-manager
4. Restart services if needed

### Secret Backup

**Vault Backup**: Backup Vault data regularly:
```bash
# Vault backup (if using Vault)
vault operator backup -address=https://vault.example.com backup-file
```

**Kubernetes Secrets Backup**: Backup Kubernetes secrets (encrypted):
```bash
# Backup secrets (encrypted)
kubectl get secret -A -o yaml | gpg --encrypt > secrets-backup.gpg
```

**Secret Recovery**:
1. Restore secrets from backup
2. Verify secret validity
3. Update Kubernetes secrets or Vault
4. Rotate secrets after recovery (security best practice)

### Security Configuration Backup

**WAF Rules**: Backup WAF rule configurations:
```bash
# Export WAF rules
kubectl get wafpolicy -o yaml > waf-rules-backup.yaml
```

**Network Policies**: Backup network policies:
```bash
# Backup network policies
kubectl get networkpolicy -A -o yaml > network-policies-backup.yaml
```

### Recovery Procedures

**RPO/RTO**:
- RPO: < 1 hour (certificates and secrets change frequently)
- RTO: < 30 minutes (security controls must be operational)

**Disaster Recovery**:
1. Restore certificates and secrets from backup
2. Restore security configurations (WAF rules, network policies)
3. Verify security controls are operational
4. Rotate secrets after recovery (security best practice)
5. Review access logs for unauthorized activity during recovery

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily**:
- Review security alerts and vulnerability scans
- Monitor certificate expiration
- Review failed authentication attempts

**Weekly**:
- Review and triage vulnerability alerts
- Review WAF activity and false positives
- Check secret rotation schedules

**Monthly**:
- Access review (quarterly for most, monthly for privileged access)
- Review and update security policies
- Review and update incident response playbooks
- Security metrics review (vulnerability trends, incident trends)

**Quarterly**:
- Security audit and compliance review
- Penetration testing (if applicable)
- Security training and awareness
- Review and update security controls

### Certificate Rotation

**TLS Certificate Rotation**:
- Automated rotation via cert-manager (preferred)
- Manual rotation if automated rotation fails
- Verify certificate validity after rotation
- Monitor for certificate-related errors

**Certificate Rotation Procedure**:
1. Generate new certificate (via cert-manager or manually)
2. Verify certificate is valid
3. Update Kubernetes secrets or ingress configuration
4. Restart services if needed (some services require restart)
5. Verify TLS handshakes succeed
6. Monitor for certificate errors

### Secret Rotation Procedures

**Zero-Downtime Secret Rotation**:
1. **Phase 1**: Deploy new secret alongside old secret (services can use either)
2. **Phase 2**: Update services to use new secret (rolling update)
3. **Phase 3**: Verify all services using new secret
4. **Phase 4**: Remove old secret

**Rotation Schedules**:
- Database passwords: Quarterly
- API keys: Quarterly or after security incident
- Service account tokens: Annually (or per policy)
- Vault leases: Per lease TTL

**Secret Rotation Automation**:
- Use Vault dynamic secrets (short-lived, auto-rotating)
- Automated rotation scripts with coordination logic
- Rotation notifications and alerts

### Vulnerability Patching SLAs

**Critical Vulnerabilities**:
- Patch within 24-48 hours
- Implement workaround if patch not available
- Continuous monitoring for exploitation

**High Vulnerabilities**:
- Patch within 7 days
- Risk assessment and prioritization
- Monitor for exploit availability

**Medium Vulnerabilities**:
- Patch within 30 days
- Include in regular patching cycle
- Monitor for severity escalation

**Vulnerability Patching Process**:
1. Receive vulnerability alert
2. Assess severity and exploitability
3. Identify affected systems
4. Test patch in development/staging
5. Deploy patch to production
6. Verify patch is applied
7. Monitor for issues

### Dependency Scanning Alerts Triage

**Automated Dependency Scanning**:
- CI/CD pipeline scanning (build-time)
- Container image scanning
- Runtime dependency scanning

**Alert Triage Process**:
1. Review vulnerability details (CVE, severity, exploitability)
2. Check if vulnerable dependency is actually used
3. Check if patch is available
4. Prioritize based on severity and exploitability
5. Create ticket for patching
6. Track patching progress

### Access Review Cadence

**Access Review Frequency**:
- Privileged access: Monthly
- Standard access: Quarterly
- Service accounts: Quarterly
- Inactive users: Immediate revocation

**Access Review Process**:
1. Generate access review report
2. Send review requests to managers/service owners
3. Track review completion
4. Revoke access for users no longer needing access
5. Document access changes

**Automated Access Reviews**:
- Automated review requests
- Access review dashboards
- Automated revocation for inactive users (90+ days inactive)

### WAF Rule Updates

**WAF Rule Maintenance**:
- Review blocked requests weekly
- Adjust rules for false positives
- Add rules for new attack patterns
- Remove obsolete rules

**WAF Rule Update Process**:
1. Identify need for rule update (false positive, new attack)
2. Test rule in staging/preview mode
3. Deploy rule update
4. Monitor for false positives or missed attacks
5. Adjust rule if needed

## On-Call Considerations

### What On-Call Engineers Need to Know

**Security Incident Response**: Know the security incident response playbook and escalation paths.

**Certificate Management**: Know how to check certificate expiration and manually renew if needed.

**Secret Management**: Know how to rotate secrets and verify rotation success.

**Common Commands**:
```bash
# Check certificate expiration
openssl x509 -in cert.pem -noout -dates

# Check cert-manager status
kubectl get certificate
kubectl describe certificate my-cert

# Check Vault secret
vault kv get secret/my-secret

# Rotate Kubernetes secret
kubectl create secret generic my-secret --from-literal=password=new-password --dry-run=client -o yaml | kubectl apply -f -

# Check security events (example)
kubectl logs -l app=security-scanner --tail=100
```

**Escalation Paths**:
1. Assess incident severity (5 minutes)
2. Contain incident if security breach (10 minutes)
3. Notify security team (15 minutes)
4. Escalate to security lead if critical (20 minutes)
5. Escalate to management if data breach (30 minutes)

### Runbook Quick Reference

- **Security Incident**: Contain → Assess → Notify → Investigate → Remediate → Document
- **Certificate Expired**: Check expiration → Renew certificate → Update secrets → Restart services
- **Critical Vulnerability**: Assess severity → Identify affected systems → Patch or workaround → Deploy patch
- **Compromised Credentials**: Revoke credentials → Rotate secrets → Audit access → Notify user
- **WAF False Positives**: Review blocked requests → Adjust rules → Deploy update → Monitor

### Critical Alerts

- **Security incident detected**: Critical, immediate containment required
- **Certificate expired**: Critical, service unavailable
- **Critical vulnerability**: Critical, patch within 24-48 hours
- **Unauthorized access**: Critical, immediate investigation
- **Compromised credentials**: Critical, immediate rotation required

### Security Incident Communication Templates

**Internal Notification** (Slack/Email):
```
SECURITY INCIDENT: [Severity] - [Brief Description]

Time: [Timestamp]
Affected Systems: [List]
Status: [Investigating/Contained/Resolved]
Action Required: [What teams need to do]

Incident Lead: [Name]
```

**Status Update Template**:
```
INCIDENT UPDATE: [Incident ID]

Current Status: [Status]
Findings: [What we've discovered]
Next Steps: [What we're doing next]
ETA: [Expected resolution time]
```
