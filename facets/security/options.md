# Security -- Options

## Contents

- [Secrets Management](#secrets-management)
  - [HashiCorp Vault](#hashicorp-vault)
  - [Cloud Provider Secrets Managers](#cloud-provider-secrets-managers)
  - [Kubernetes Secrets with Encryption](#kubernetes-secrets-with-encryption)
- [Dependency Scanning](#dependency-scanning)
  - [Dependabot / Renovate](#dependabot--renovate)
  - [Snyk](#snyk)
  - [OWASP Dependency-Check](#owasp-dependency-check)
- [Application Security Testing](#application-security-testing)
  - [SAST (Static Application Security Testing)](#sast-static-application-security-testing)
  - [DAST (Dynamic Application Security Testing)](#dast-dynamic-application-security-testing)
  - [Both (SAST + DAST)](#both-sast-dast)

Decision matrices for security technology choices. Each option is evaluated against criteria relevant to security, operational complexity, and integration with existing infrastructure.

## Secrets Management

Secrets management systems provide secure storage, access control, audit logging, and rotation capabilities for passwords, API keys, database credentials, encryption keys, and OAuth client secrets. The choice of secrets management system impacts security posture, operational overhead, and integration complexity.

### HashiCorp Vault

**Description**: Comprehensive secrets management platform with dynamic secrets, encryption as a service, and extensive integration capabilities. Vault can generate database credentials on-demand with automatic expiration, encrypt data using various backends, and integrate with cloud providers, Kubernetes, and applications via APIs.

**Strengths**: 
- Dynamic secrets generation eliminates long-lived credentials, reducing attack surface
- Encryption as a service provides centralized encryption key management
- Extensive ecosystem with integrations for databases, cloud providers, and applications
- Open source with enterprise features available
- Supports multiple authentication methods (AppRole, Kubernetes, AWS IAM, etc.)
- Audit logging provides comprehensive access trails

**Weaknesses**:
- Requires infrastructure to operate (Vault servers, high availability setup)
- Operational complexity increases with scale (clustering, performance tuning)
- Learning curve for teams unfamiliar with Vault concepts
- Dynamic secrets require application changes to support credential rotation
- Initial setup and configuration can be time-consuming

**Best For**:
- Organizations requiring dynamic secrets and encryption as a service
- Multi-cloud or hybrid cloud environments
- Applications with complex secret rotation requirements
- Teams with operational expertise to manage Vault infrastructure
- Compliance requirements mandating comprehensive audit logging

**Avoid When**:
- Simple use cases that don't require dynamic secrets or encryption as a service
- Small teams without operational capacity to manage Vault
- Single-cloud deployments where cloud-native solutions are simpler
- Applications that cannot be modified to support dynamic secret retrieval

### Cloud Provider Secrets Managers

**Description**: Managed secrets management services provided by cloud providers: AWS Secrets Manager, Azure Key Vault, Google Cloud Secret Manager. These services provide secure storage, access control via cloud IAM, and integration with cloud services.

**Strengths**:
- Fully managed—no infrastructure to operate
- Integrated with cloud IAM for access control
- Automatic backups and high availability
- Cloud-native integrations (RDS credential rotation, Lambda environment variables)
- Simple APIs and SDKs for common languages
- Pay-per-use pricing scales with usage

**Weaknesses**:
- Vendor lock-in—secrets are tied to specific cloud providers
- Limited features compared to Vault (no dynamic secrets for all backends)
- Cross-cloud deployments require multiple systems
- Cost can accumulate with many secrets and frequent access
- Less flexibility than self-hosted solutions

**Best For**:
- Single-cloud deployments where cloud-native integration is valuable
- Teams preferring managed services over self-hosted infrastructure
- Applications already using cloud provider services (RDS, Lambda, etc.)
- Organizations with cloud-first strategies
- Use cases where simplicity outweighs feature richness

**Avoid When**:
- Multi-cloud or hybrid cloud deployments requiring unified secrets management
- Requirements for advanced features like encryption as a service or dynamic secrets for all backends
- Organizations avoiding vendor lock-in
- Use cases requiring extensive customization or integration with non-cloud services

### Kubernetes Secrets with Encryption

**Description**: Kubernetes native secrets storage with encryption at rest enabled via encryption providers. Kubernetes Secrets are base64-encoded by default but can be encrypted using encryption providers that integrate with key management services.

**Strengths**:
- No additional infrastructure—uses existing Kubernetes clusters
- Integrated with Kubernetes RBAC for access control
- Simple API familiar to Kubernetes users
- Works with any Kubernetes distribution
- Encryption at rest protects against storage compromise

**Weaknesses**:
- Base64 encoding is not encryption—encryption must be explicitly enabled
- Limited features compared to dedicated secrets managers (no rotation, no dynamic secrets)
- Secrets are visible in etcd to cluster administrators
- Manual secret creation and updates
- No audit logging beyond Kubernetes audit logs
- Encryption provider configuration can be complex

**Best For**:
- Simple use cases with static secrets that don't require rotation
- Teams already heavily invested in Kubernetes tooling
- Applications running entirely within Kubernetes
- Use cases where simplicity is more important than advanced features
- Development and testing environments

**Avoid When**:
- Requirements for automatic secret rotation or dynamic secrets
- Compliance requirements mandating comprehensive audit logging
- Secrets that need to be accessed outside Kubernetes clusters
- Use cases requiring advanced features like encryption as a service

### Evaluation Criteria

**Security**: How well does the solution protect secrets? Consider encryption at rest and in transit, access controls, audit logging, and protection against common attack vectors.

**Operational Complexity**: How much effort is required to operate and maintain the solution? Consider infrastructure requirements, configuration complexity, monitoring needs, and troubleshooting difficulty.

**Integration**: How easily does the solution integrate with existing infrastructure and applications? Consider APIs, SDKs, cloud provider integrations, and required application changes.

**Features**: What capabilities does the solution provide? Consider secret rotation, dynamic secrets, encryption as a service, and audit logging.

**Cost**: What are the total costs of ownership? Consider licensing, infrastructure, operational overhead, and scaling costs.

### Recommendation Guidance

**Start with cloud provider secrets managers** if you're deploying to a single cloud and prefer managed services. The operational simplicity and cloud-native integration provide immediate value with minimal overhead.

**Choose HashiCorp Vault** if you need advanced features (dynamic secrets, encryption as a service), operate in multi-cloud environments, or require extensive customization. Be prepared to invest in operational expertise and infrastructure.

**Use Kubernetes Secrets with encryption** for simple use cases within Kubernetes, especially in development environments or for non-sensitive configuration. Upgrade to dedicated secrets managers as requirements grow.

**Evolution triggers**: Move from Kubernetes Secrets to cloud providers or Vault when you need secret rotation, dynamic secrets, or comprehensive audit logging. Move from cloud providers to Vault when you need multi-cloud support or advanced features.

## Dependency Scanning

Dependency scanning identifies known vulnerabilities in application dependencies by comparing versions against vulnerability databases. The choice of dependency scanning tool impacts detection capabilities, developer experience, and integration complexity.

### Dependabot / Renovate

**Description**: Automated dependency update tools that scan repositories for outdated dependencies and create pull requests with updates. Dependabot is GitHub-native, while Renovate supports multiple Git hosting platforms.

**Strengths**:
- Automated pull requests reduce manual dependency management overhead
- Integrates with GitHub's dependency graph and security advisories
- Configurable update schedules and grouping strategies
- Supports multiple package managers (npm, Maven, Gradle, etc.)
- Free for open source and GitHub repositories
- Creates separate pull requests per dependency for easy review

**Weaknesses**:
- Primarily focused on updates rather than comprehensive vulnerability scanning
- Limited vulnerability intelligence compared to dedicated SCA tools
- Requires repository access to create pull requests
- May create many pull requests requiring review
- Less suitable for organizations not using GitHub

**Best For**:
- Teams wanting to automate dependency updates
- GitHub-based workflows
- Organizations preferring pull request-based workflows
- Use cases where keeping dependencies updated is the primary goal

**Avoid When**:
- Requirements for comprehensive vulnerability intelligence and fix suggestions
- Non-GitHub Git hosting platforms (for Dependabot)
- Organizations preferring centralized vulnerability management over distributed pull requests

### Snyk

**Description**: Software Composition Analysis platform providing vulnerability scanning, fix suggestions, and developer-friendly interfaces. Snyk scans dependencies, container images, and infrastructure as code.

**Strengths**:
- Comprehensive vulnerability database with intelligence beyond CVEs
- Developer-friendly interfaces (IDE plugins, CLI, web dashboard)
- Fix suggestions and automated pull requests
- Scans dependencies, containers, and IaC in unified platform
- License compliance checking
- Integration with CI/CD pipelines and IDEs

**Weaknesses**:
- Commercial product with licensing costs
- Requires account setup and configuration
- May produce false positives requiring tuning
- Less suitable for organizations preferring open source tools

**Best For**:
- Organizations wanting comprehensive SCA with developer-friendly UX
- Teams requiring unified scanning across dependencies, containers, and IaC
- Use cases where developer experience is prioritized
- Organizations with budget for commercial security tools

**Avoid When**:
- Budget constraints requiring free/open source solutions
- Simple use cases that don't require advanced features
- Organizations preferring distributed pull request workflows over centralized dashboards

### OWASP Dependency-Check

**Description**: Open source dependency scanning tool that identifies known vulnerabilities in project dependencies. Dependency-Check supports Maven, Gradle, npm, and other package managers.

**Strengths**:
- Free and open source
- Supports multiple package managers
- Integrates with build processes (Maven plugin, Gradle plugin)
- Can fail builds when critical vulnerabilities are detected
- No vendor lock-in or account requirements

**Weaknesses**:
- Less developer-friendly than commercial alternatives
- Requires build integration rather than pull request workflows
- Limited vulnerability intelligence compared to commercial tools
- May require more tuning to reduce false positives
- Less suitable for organizations wanting automated remediation

**Best For**:
- Organizations preferring open source tools
- Build-integrated workflows
- Budget-conscious teams
- Use cases where basic vulnerability detection is sufficient

**Avoid When**:
- Requirements for developer-friendly interfaces and automated remediation
- Organizations preferring pull request-based workflows
- Use cases requiring comprehensive vulnerability intelligence

### Recommendation Guidance

**Use Dependabot or Renovate** for automated dependency updates, especially in GitHub-based workflows. These tools reduce the burden of keeping dependencies current and can be configured to create pull requests for security updates automatically.

**Choose Snyk** if you want comprehensive SCA with excellent developer experience and have budget for commercial tools. Snyk's unified platform and fix suggestions provide immediate value.

**Use OWASP Dependency-Check** if you prefer open source tools and want build-integrated scanning. Dependency-Check provides basic vulnerability detection without licensing costs.

**Combine tools**: Use Dependabot/Renovate for automated updates and Snyk or Dependency-Check for comprehensive vulnerability scanning. The tools complement each other—automated updates keep dependencies current, while SCA tools provide comprehensive vulnerability intelligence.

## Application Security Testing

Application security testing validates that security controls function correctly and identifies vulnerabilities. The choice between SAST, DAST, or both impacts vulnerability coverage, false positive rates, and operational overhead.

### SAST (Static Application Security Testing)

**Description**: Analyzes source code for security vulnerabilities without executing the application. SAST tools parse code and apply security rules to identify patterns indicating vulnerabilities.

**Strengths**:
- Finds vulnerabilities early in development lifecycle
- Provides fast feedback (minutes, not hours)
- Can analyze entire codebase, including unreachable code
- Identifies code-level issues (SQL injection, XSS, hardcoded secrets)
- Integrates with IDEs for real-time feedback
- No running application required

**Weaknesses**:
- Cannot find runtime vulnerabilities or configuration issues
- Produces false positives requiring tuning
- Limited understanding of application context and business logic
- Cannot detect issues requiring execution (authentication bypasses, logic flaws)
- May require source code access

**Best For**:
- Early vulnerability detection in development
- Code-level security issue identification
- Fast feedback requirements
- Use cases where source code is available

**Tools**: SonarQube, Semgrep, SpotBugs with FindSecBugs

### DAST (Dynamic Application Security Testing)

**Description**: Analyzes running applications for vulnerabilities by sending requests and analyzing responses. DAST tools don't require source code access.

**Strengths**:
- Finds runtime vulnerabilities and configuration issues
- Tests actual deployed applications
- Can find issues SAST misses (authentication bypasses, business logic flaws)
- No source code access required
- Tests applications as attackers see them

**Weaknesses**:
- Requires running applications (staging or production-like environments)
- Slower than SAST (hours, not minutes)
- Limited code coverage (only tests reachable code paths)
- May impact application performance during scanning
- Less suitable for early development stages

**Best For**:
- Runtime vulnerability detection
- Configuration and deployment security validation
- Testing applications where source code isn't available
- Post-deployment security validation

**Tools**: OWASP ZAP, Burp Suite

### Both (SAST + DAST)

**Description**: Combining SAST and DAST provides comprehensive coverage by finding both code-level and runtime vulnerabilities.

**Strengths**:
- Comprehensive vulnerability coverage
- Finds issues that either tool alone would miss
- SAST provides early feedback, DAST validates runtime security
- Defense in depth for security testing

**Weaknesses**:
- Higher operational overhead (two tools to configure and maintain)
- Higher cost (licensing, infrastructure, time)
- May produce overlapping findings requiring deduplication
- Requires both source code access and running applications

**Best For**:
- Critical applications requiring comprehensive security validation
- Compliance requirements mandating both SAST and DAST
- Organizations with resources to operate both tools
- Use cases where security is a primary concern

### Recommendation Guidance

**Start with SAST** for most applications. SAST provides fast feedback and finds common vulnerabilities early. Integrate SAST into CI/CD pipelines to scan every pull request.

**Add DAST** for critical applications or when compliance requires it. DAST complements SAST by finding runtime vulnerabilities. Run DAST against staging environments after deployments.

**Use both** for high-security applications or when compliance mandates comprehensive testing. The combination provides defense in depth, though operational overhead increases.

**Evolution triggers**: Add DAST when SAST coverage is insufficient, compliance requires runtime testing, or applications have complex runtime configurations. Consider both when security is a primary concern and resources allow.

### Synergies with Other Facets

**CI/CD Integration**: All security testing tools should integrate with CI/CD pipelines. SAST runs on every pull request, DAST runs after deployments to staging, and dependency scanning runs continuously.

**Observability**: Security testing findings should be tracked and monitored. Security metrics (vulnerability counts, remediation times) provide visibility into security posture and help prioritize investments.

**Authentication**: Security testing validates authentication and authorization controls. SAST can identify missing authorization checks, while DAST can test authentication bypasses and privilege escalation.

These decision matrices provide guidance for common security technology choices. However, specific requirements may override general recommendations. Evaluate options against your organization's security requirements, operational capabilities, and constraints.
