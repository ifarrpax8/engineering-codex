# Security -- Testing

## Contents

- [Static Application Security Testing (SAST)](#static-application-security-testing-sast)
- [Dynamic Application Security Testing (DAST)](#dynamic-application-security-testing-dast)
- [Dependency Scanning](#dependency-scanning)
- [Secret Scanning](#secret-scanning)
- [Penetration Testing](#penetration-testing)
- [Security Unit Tests](#security-unit-tests)
- [Infrastructure Security Testing](#infrastructure-security-testing)
- [OWASP ZAP in CI/CD](#owasp-zap-in-cicd)
- [QA and Test Engineer Perspective](#qa-and-test-engineer-perspective)

Security testing validates that security controls function correctly and identifies vulnerabilities before attackers exploit them. Security testing spans multiple categories: static analysis of source code, dynamic analysis of running applications, dependency scanning, secret detection, penetration testing, and infrastructure security validation. Each category provides different coverage and should be integrated into the development lifecycle.

## Static Application Security Testing (SAST)

Static Application Security Testing analyzes source code for security vulnerabilities without executing the application. SAST tools parse code, build abstract syntax trees or control flow graphs, and apply security rules to identify patterns that indicate vulnerabilities. SAST can find issues like SQL injection, XSS, insecure cryptographic usage, hardcoded secrets, and authorization bypasses.

SonarQube includes security rules that detect common vulnerabilities in Java, Kotlin, JavaScript, and TypeScript. SonarQube rules are based on OWASP Top 10 and CWE (Common Weakness Enumeration) classifications, providing comprehensive coverage. Security hotspots are flagged for review, and confirmed vulnerabilities block quality gates, preventing merges until remediation.

Semgrep provides fast, pattern-based static analysis with custom rules. Semgrep rules can detect framework-specific vulnerabilities (Spring Security misconfigurations, React XSS patterns) and custom security patterns. Semgrep integrates with CI/CD pipelines and provides clear, actionable findings with code examples.

SpotBugs with the FindSecBugs plugin detects security issues in Java bytecode. FindSecBugs identifies hardcoded passwords, weak cryptographic algorithms, SQL injection in JDBC code, and insecure random number generation. SpotBugs can be integrated into Gradle and Maven builds, running automatically during compilation.

SAST tools produce false positives—findings that aren't actual vulnerabilities. Tuning SAST tools requires balancing sensitivity (catching real issues) with precision (avoiding false positives). Start with default rules, review findings to understand patterns, then adjust rules or suppress false positives with annotations. However, don't suppress findings without thorough analysis—what appears to be a false positive might be a real vulnerability in a different context.

SAST should run in CI/CD pipelines on every pull request, blocking merges when critical or high-severity vulnerabilities are detected. SAST results should be tracked over time to measure security posture trends. However, SAST cannot find runtime vulnerabilities, configuration issues, or logic flaws that require execution context.

## Dynamic Application Security Testing (DAST)

Dynamic Application Security Testing analyzes running applications for vulnerabilities by sending requests and analyzing responses. DAST tools don't require source code access, making them suitable for testing third-party applications and production-like environments. DAST can find issues like injection vulnerabilities, broken authentication, sensitive data exposure, and security misconfigurations.

OWASP ZAP (Zed Attack Proxy) is an open-source DAST tool that can be used manually or automated in CI/CD pipelines. ZAP performs baseline scans that quickly identify common vulnerabilities, and full scans that comprehensively test applications. ZAP can be integrated into CI/CD pipelines to run automated scans against staging environments after deployments.

Burp Suite provides professional DAST capabilities with advanced scanning, manual testing tools, and extensibility through plugins. Burp Suite is commonly used by penetration testers for manual security testing, but it also supports automated scanning for CI/CD integration.

DAST tools require running applications, so they're typically run against staging or pre-production environments rather than during development. DAST scans can be time-consuming and may impact application performance, so schedule them appropriately (e.g., nightly scans or post-deployment scans).

DAST complements SAST by finding runtime vulnerabilities that static analysis misses. Configuration issues, authentication bypasses, and business logic flaws often require execution to detect. However, DAST has limited code coverage—it can only test code paths that are reachable through the application's public interface.

## Dependency Scanning

Dependency scanning identifies known vulnerabilities in application dependencies by comparing dependency versions against vulnerability databases. The National Vulnerability Database (NVD) and GitHub Advisory Database maintain comprehensive lists of known CVEs (Common Vulnerabilities and Exposures) with severity ratings and affected versions.

Dependabot (GitHub) automatically scans repositories for vulnerable dependencies and creates pull requests with security updates. Dependabot integrates with GitHub's dependency graph, providing visibility into dependency relationships and security advisories. Dependabot can be configured to create pull requests automatically for security updates or to require manual approval.

Snyk provides Software Composition Analysis with developer-friendly interfaces, fix suggestions, and integration with IDEs. Snyk scans dependencies, container images, and infrastructure as code, providing a unified view of security across the stack. Snyk's database includes vulnerability intelligence beyond CVEs, including license compliance and supply chain risk.

OWASP Dependency-Check analyzes project dependencies to identify known vulnerabilities. Dependency-Check supports Maven, Gradle, npm, and other package managers, generating reports with CVE details and severity ratings. Dependency-Check can be integrated into build processes to fail builds when critical vulnerabilities are detected.

Dependency scanning should run in CI/CD pipelines on every pull request and on a schedule to detect newly discovered vulnerabilities in existing dependencies. Scanning should block merges when critical or high-severity vulnerabilities are detected, with exceptions requiring security team approval. Medium and low-severity vulnerabilities can be tracked and remediated over time, but they shouldn't be ignored indefinitely.

Dependency scanning requires accurate dependency information. Lock files (package-lock.json, gradle.lockfile) ensure that scanning analyzes the exact versions that will be deployed, not just declared versions. Without lock files, scanning might miss vulnerabilities in transitive dependencies or report false positives for versions that won't actually be used.

## Secret Scanning

Secret scanning detects accidentally committed secrets (API keys, passwords, tokens, private keys) in source code and commit history. Secrets in repositories are effectively public—even private repositories can be leaked, and anyone with repository access can view history. Secret scanning prevents secrets from entering repositories and identifies existing secrets for rotation.

git-secrets provides pre-commit hooks that scan commits for secret patterns before they're committed. git-secrets can detect AWS access keys, private keys, passwords, and other common secret patterns. Pre-commit hooks provide immediate feedback to developers, preventing secrets from being committed in the first place.

truffleHog scans repositories for high-entropy strings (likely secrets) and known secret patterns. truffleHog can scan entire repository history, identifying secrets that were committed in the past. truffleHog integrates with CI/CD pipelines to scan pull requests and block merges when secrets are detected.

GitHub secret scanning automatically scans repositories for secrets from supported services (AWS, Azure, Google Cloud, etc.) and notifies service providers when secrets are detected, enabling automatic revocation. GitHub Advanced Security provides additional secret scanning capabilities for private repositories.

Secret scanning should be integrated into pre-commit hooks (developer feedback) and CI/CD pipelines (enforcement). When secrets are detected, they must be rotated immediately—simply removing them from the latest commit doesn't remove them from history. Use `git filter-branch` or BFG Repo-Cleaner to remove secrets from history, then rotate the compromised secrets.

Secret scanning tools produce false positives when they detect high-entropy strings that aren't actually secrets (hashes, random IDs, test data). Tune secret scanning rules to reduce false positives while maintaining detection of real secrets. However, when in doubt, treat findings as real secrets until proven otherwise.

## Penetration Testing

Penetration testing involves manual security testing by security specialists who simulate real-world attacks. Penetration testers use a combination of automated tools and manual techniques to identify vulnerabilities, test business logic, and assess the overall security posture. Penetration testing provides depth that automated tools cannot achieve.

Penetration testing should be performed periodically (quarterly or annually) for critical applications, after major changes, or when compliance requirements mandate it. Penetration testers provide detailed reports with vulnerability descriptions, proof-of-concept exploits, risk assessments, and remediation recommendations.

External penetration testing focuses on internet-facing attack surfaces, while internal penetration testing assumes attackers have gained network access. Both perspectives are valuable—external testing validates perimeter defenses, while internal testing validates defense in depth.

Bug bounty programs complement penetration testing by engaging a broader community of security researchers. Bug bounty programs provide financial incentives for finding vulnerabilities, often discovering issues that internal testing misses. However, bug bounty programs require careful scope definition and response processes to manage reports effectively.

Penetration testing findings should be tracked and remediated with the same priority as automated tool findings. Critical vulnerabilities should be remediated immediately, while lower-severity findings can be addressed over time. Regular penetration testing helps measure security improvement over time.

## Security Unit Tests

Security unit tests validate that security controls function correctly at the unit level. Security unit tests verify input validation (rejecting malicious input), authorization rules (preventing unauthorized access), encryption (ensuring data is encrypted), and secure defaults (ensuring insecure configurations fail).

Input validation tests verify that malicious input is rejected. Test SQL injection attempts, XSS payloads, path traversal sequences, and oversized inputs. Assert that validation functions throw exceptions or return errors for malicious input, and that safe input is accepted.

Authorization tests verify that access control rules are enforced. Test that users cannot access resources they shouldn't (user A cannot access user B's data), that role-based permissions are enforced (non-admins cannot perform admin actions), and that unauthenticated requests are rejected. Use test fixtures to create users with different roles and permissions.

Rate limiting tests verify that rate limits are enforced. Send requests exceeding rate limits and assert that requests are rejected with appropriate status codes (429 Too Many Requests). Verify that rate limits reset correctly and that different endpoints have appropriate limits.

Encryption tests verify that sensitive data is encrypted. Test that database encryption is enabled, that encryption keys are managed securely, and that decryption fails with incorrect keys. However, avoid testing encryption algorithm correctness (that's the algorithm's responsibility)—test that encryption is applied correctly.

Security unit tests should be integrated into standard test suites, running on every build. Security unit tests provide fast feedback and prevent regressions in security controls. However, unit tests cannot find integration-level vulnerabilities or configuration issues that require full application context.

## Infrastructure Security Testing

Infrastructure security testing validates that infrastructure components (containers, Kubernetes clusters, cloud resources) are configured securely. Infrastructure misconfigurations can create vulnerabilities even if application code is secure.

Container image scanning identifies vulnerabilities in container images by analyzing installed packages and comparing them against vulnerability databases. Trivy and Grype scan container images for known CVEs in installed packages, providing severity ratings and fix recommendations. Container scanning should be integrated into CI/CD pipelines, blocking deployments when critical vulnerabilities are detected.

Kubernetes security testing validates cluster configurations against security best practices. Tools like kube-score and Polaris check Kubernetes manifests for security misconfigurations (running as root, missing resource limits, insecure capabilities). Kubernetes Pod Security Standards define security policies that can be enforced via admission controllers.

Infrastructure as Code (IaC) security testing validates Terraform, CloudFormation, and other IaC configurations for security misconfigurations. tfsec and checkov scan IaC files for insecure configurations (public S3 buckets, overly permissive security groups, unencrypted storage). IaC security testing should run in CI/CD pipelines before infrastructure is provisioned.

Cloud security posture management (CSPM) tools continuously monitor cloud environments for misconfigurations and compliance violations. CSPM tools provide visibility into security posture across cloud accounts and can automatically remediate some issues. However, CSPM tools complement but don't replace infrastructure security testing in CI/CD.

Infrastructure security testing should be integrated into infrastructure deployment pipelines, blocking deployments when critical misconfigurations are detected. Infrastructure security is as important as application security—a misconfigured Kubernetes cluster or cloud resource can expose entire applications to attack.

## OWASP ZAP in CI/CD

OWASP ZAP can be integrated into CI/CD pipelines to provide automated DAST scanning. ZAP baseline scans quickly identify common vulnerabilities and can complete in minutes, making them suitable for every deployment. ZAP full scans provide comprehensive testing but take longer, making them suitable for scheduled scans or post-deployment validation.

ZAP baseline scans use spidering to discover application endpoints and then test for common vulnerabilities (XSS, SQL injection, insecure headers). Baseline scans are designed to be fast and non-intrusive, suitable for frequent execution. ZAP baseline scans can be configured to fail builds when high-severity vulnerabilities are detected.

ZAP full scans perform comprehensive testing including authenticated scanning, advanced spidering, and active vulnerability testing. Full scans take longer and may impact application performance, so they're typically scheduled (e.g., nightly) or run after deployments to staging environments.

ZAP can be integrated into CI/CD pipelines using Docker containers or GitHub Actions. ZAP scans should target staging or pre-production environments that mirror production configurations. Scanning production environments is possible but requires careful configuration to avoid impacting users.

ZAP findings should be tracked and remediated like other security findings. However, ZAP may produce false positives, especially for applications with complex authentication or custom security controls. Tune ZAP policies and review findings to reduce false positives while maintaining vulnerability detection.

Security testing is not a one-time activity—it's an ongoing process integrated into the development lifecycle. Multiple testing categories provide complementary coverage, and no single category is sufficient. Combine SAST, DAST, dependency scanning, secret scanning, and infrastructure testing to achieve comprehensive security validation.

## QA and Test Engineer Perspective

### Risk-Based Testing Priorities

Prioritize security testing based on attack likelihood and business impact. Critical paths requiring immediate coverage include: authentication and authorization (unauthorized access risk), input validation (injection attack risk), and sensitive data handling (data breach risk). High-priority areas include: session management (session hijacking risk), cryptographic operations (data encryption risk), and API security (API abuse risk).

Medium-priority areas suitable for later iterations include: security headers, CORS configuration, and rate limiting. Low-priority areas for exploratory testing include: security logging, security monitoring, and security documentation.

Focus on attack vectors with high business impact: data breaches (PII exposure, financial data exposure), unauthorized access (privilege escalation, account takeover), and service disruption (DoS attacks, resource exhaustion). These represent the highest risk of security incidents and compliance violations.

### Exploratory Testing Guidance

Authentication and authorization exploration: test authentication bypass attempts (missing tokens, invalid tokens, expired tokens), privilege escalation attempts (role manipulation, permission bypass), and session management (session fixation, session hijacking). Probe edge cases: concurrent logins, session sharing, and session timeout behavior.

Input validation requires investigation: test injection attacks (SQL injection, XSS, command injection), input boundary testing (maximum lengths, special characters), and encoding issues (unicode, encoding bypass). Explore what happens with malformed input, oversized input, and encoded input.

Sensitive data handling needs exploration: test data exposure (logs, error messages, API responses), data encryption (data at rest, data in transit), and data masking (PII masking, sensitive field masking). Probe edge cases: data leakage in error messages, data exposure in logs, and data exposure in API responses.

Security configuration requires investigation: test security headers (CSP, HSTS, X-Frame-Options), CORS configuration (allowed origins, allowed methods), and rate limiting (rate limit enforcement, rate limit bypass). Explore what happens with misconfigured security settings, missing security headers, and overly permissive configurations.

### Test Data Management

Security testing requires realistic test data: user accounts with various roles (admin, user, guest), resources with various access levels (public, private, restricted), and sensitive data (PII, financial data, authentication data). Create test data factories that generate realistic security test scenarios: `createAdminUser()`, `createUserWithRestrictedAccess()`.

Sensitive security test data must be handled carefully: never commit real credentials, use test credentials that are clearly identifiable, and rotate test credentials regularly. Use test data that mirrors production patterns but is clearly test data (test email domains, test account prefixes).

Test data refresh strategies: security test data may become stale (expired tokens, locked accounts, rotated credentials). Implement test data refresh that generates new tokens, resets account states, and updates credentials. Security test data should be refreshed more frequently than other test data due to security requirements.

Attack payload test data: maintain test datasets of attack payloads (SQL injection payloads, XSS payloads, command injection payloads). These payloads should be safe to use in test environments but representative of real attacks. Update payload datasets as new attack vectors are discovered.

### Test Environment Considerations

Security test environments must mirror production security configurations: same authentication mechanisms, same authorization rules, same security headers, and same rate limiting. Differences can hide vulnerabilities or create false positives. Verify that test environments use production-like security configurations.

Shared test environments create isolation challenges: concurrent security tests may interfere with each other (rate limiting, account lockouts, session conflicts). Use isolated test environments per test run, or implement test isolation through unique user accounts and cleanup between tests.

Environment-specific risks include: test environments with relaxed security (missing security headers, permissive CORS), test environments missing production security features (WAF, rate limiting), and test environments with different security configurations. Verify that test environments have equivalent security controls, or explicitly test security control absence as a separate scenario.

Security testing tools: test environments may have different security testing tool configurations than production. Verify that security testing tools are configured correctly and that findings are relevant to production environments.

### Regression Strategy

Security regression suites must include: authentication and authorization checks (unauthorized access prevented), input validation (injection attacks prevented), sensitive data handling (data not exposed), and security configuration (security headers present). These represent the core security functionality that must never regress.

Automation candidates for regression include: security unit tests (input validation, authorization checks), SAST scans (static analysis), dependency scans (vulnerability scanning), and secret scans (secret detection). These are deterministic and can be validated automatically.

Manual regression items include: penetration testing (manual security testing), security configuration review (security headers, CORS), and security monitoring (security event analysis). These require human judgment and security expertise.

Trim regression suites by removing tests for deprecated security features, obsolete attack vectors, or rarely-used security functionality. However, maintain tests for critical security controls (authentication, authorization, input validation) even if they're simple—security regressions have high impact.

### Defect Patterns

Common security bugs include: authentication bypass (unauthorized access possible), injection vulnerabilities (SQL injection, XSS), authorization bypass (privilege escalation), and sensitive data exposure (PII in logs, credentials in error messages). These patterns recur across applications and should be tested explicitly.

Bugs tend to hide in: edge cases (boundary conditions, encoding issues), error paths (error messages leak information), and configuration issues (missing security headers, permissive CORS). Test these scenarios explicitly—they're common sources of security vulnerabilities.

Historical patterns show that security bugs cluster around: input validation (injection attacks), authentication and authorization (unauthorized access), and sensitive data handling (data exposure). Focus security testing on these areas.

Triage guidance: security bugs are typically critical severity due to security implications. However, distinguish between exploitable vulnerabilities (attackers can exploit) and security improvements (defense in depth). Exploitable vulnerabilities require immediate attention, while security improvements can be prioritized based on risk.
