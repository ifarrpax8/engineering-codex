# Options: Feedback & Support

## Contents

- [Feedback Collection Tools](#feedback-collection-tools)
  - [Custom In-App Widget](#custom-in-app-widget)
  - [Canny](#canny)
  - [UserVoice](#uservoice)
  - [Hotjar Feedback](#hotjar-feedback)
- [Support/Ticketing Systems](#supportticketing-systems)
  - [Jira Service Management](#jira-service-management)
  - [Zendesk](#zendesk)
  - [Freshdesk](#freshdesk)
  - [Custom Built](#custom-built)
- [Knowledge Base Platforms](#knowledge-base-platforms)
  - [Confluence (Internal)](#confluence-internal)
  - [GitBook](#gitbook)
  - [Notion](#notion)
  - [Custom Docs Site](#custom-docs-site)
- [In-App Help Solutions](#in-app-help-solutions)
  - [Intercom](#intercom)
  - [Custom Help Panel](#custom-help-panel)
  - [Chatbot (Custom or Commercial)](#chatbot-custom-or-commercial)
- [Session Replay Tools](#session-replay-tools)
  - [Sentry Session Replay](#sentry-session-replay)
  - [LogRocket](#logrocket)
  - [FullStory](#fullstory)
  - [Hotjar](#hotjar)
- [Recommendation Guidance](#recommendation-guidance)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Feedback Collection Tools

### Custom In-App Widget

**Description**: Build your own feedback widget integrated directly into your application.

**Strengths**:
- Full control over UI/UX and branding
- Seamless integration with your app's design system (Propulsion, MUI)
- Complete control over data capture and context
- No third-party dependencies
- Can be tailored to your specific workflows

**Weaknesses**:
- Requires development and maintenance resources
- Must build all features from scratch (screenshot capture, file uploads, etc.)
- No built-in analytics or insights
- Need to build routing and integration logic

**Best For**:
- Teams with strong frontend capabilities
- Applications requiring deep customization
- B2B SaaS with specific feedback workflows
- When feedback needs to integrate tightly with internal systems

**Avoid When**:
- Limited engineering resources
- Need quick time-to-market
- Don't have frontend expertise
- Want out-of-the-box analytics

### Canny

**Description**: Product feedback management platform with roadmap integration.

**Strengths**:
- Beautiful, customizable widget
- Roadmap integration (show users what's planned)
- Voting and prioritization features
- User segmentation and targeting
- Analytics and insights
- Changelog functionality

**Weaknesses**:
- Monthly subscription cost
- Less control over data storage
- May be overkill for simple feedback collection
- Widget styling may not match design system perfectly

**Best For**:
- Product teams wanting roadmap transparency
- Applications with active user communities
- When feedback prioritization is important
- Teams wanting to close the feedback loop publicly

**Avoid When**:
- Simple bug reporting needs
- Tight budget constraints
- Need complete data control/on-premise
- Don't want external widget dependency

### UserVoice

**Description**: Comprehensive feedback and customer engagement platform.

**Strengths**:
- Feature request management
- User voting and prioritization
- Integration with support ticketing systems
- Analytics and reporting
- Mobile SDKs available

**Weaknesses**:
- Higher cost tier
- Can feel heavy/enterprise-focused
- Less flexible than custom solutions
- May include features you don't need

**Best For**:
- Enterprise B2B SaaS applications
- Teams needing comprehensive feedback management
- When integration with support systems is critical
- Applications with mobile apps

**Avoid When**:
- Small teams or startups
- Simple feedback collection needs
- Want lightweight solution
- Budget-conscious projects

### Hotjar Feedback

**Description**: Feedback widget from Hotjar with heatmaps and session recordings.

**Strengths**:
- Integrates with Hotjar's analytics suite
- Visual feedback (users can highlight areas)
- Session replay integration
- Heatmap correlation
- Easy to set up

**Weaknesses**:
- Requires Hotjar subscription
- Less customizable than custom solutions
- Privacy concerns with session replay
- May not fit B2B SaaS context perfectly

**Best For**:
- Teams already using Hotjar
- When visual feedback is important
- Applications needing heatmap insights
- Consumer-facing applications

**Avoid When**:
- B2B SaaS with privacy requirements
- Don't need heatmaps/session replay
- Want standalone feedback solution
- Need deep customization

## Support/Ticketing Systems

### Jira Service Management

**Description**: Atlassian's IT service management platform built on Jira.

**Strengths**:
- Powerful workflow customization
- Integration with Jira Software (if using)
- SLA management
- Knowledge base integration
- Strong reporting and analytics
- Self-service portal capabilities

**Weaknesses**:
- Complex setup and configuration
- Can be overwhelming for small teams
- Requires Jira admin expertise
- Higher cost for larger teams
- UI can feel dated

**Best For**:
- Teams already using Jira Software
- Enterprise B2B SaaS
- Complex support workflows
- When SLA tracking is critical
- Teams needing deep customization

**Avoid When**:
- Small teams or startups
- Simple support needs
- Don't have Jira admin resources
- Want modern, intuitive UI
- Budget constraints

### Zendesk

**Description**: Popular customer service and support ticketing platform.

**Strengths**:
- User-friendly interface
- Strong email integration
- Live chat capabilities
- Knowledge base (Guide)
- Good mobile apps
- Extensive app marketplace
- Multi-channel support (email, chat, phone, social)

**Weaknesses**:
- Can be expensive at scale
- Less flexible than Jira for complex workflows
- Some features require higher tiers
- Customization limitations compared to self-built

**Best For**:
- Customer-facing support teams
- When email support is primary channel
- Teams wanting modern, intuitive UI
- Applications needing multi-channel support
- When knowledge base is important

**Avoid When**:
- Engineering-focused support (bugs, technical issues)
- Need deep workflow customization
- Tight budget
- Simple internal support needs

### Freshdesk

**Description**: Zendesk alternative with competitive pricing.

**Strengths**:
- Lower cost than Zendesk
- Good feature set for price
- Easy to set up
- Multi-channel support
- Knowledge base included
- Good for small to medium teams

**Weaknesses**:
- Less mature than Zendesk
- Smaller app marketplace
- Some advanced features missing
- Less brand recognition

**Best For**:
- Budget-conscious teams
- Small to medium support teams
- When Zendesk is too expensive
- Simple to moderate support needs

**Avoid When**:
- Need advanced features
- Enterprise requirements
- Complex workflows
- Need extensive integrations

### Custom Built

**Description**: Build your own ticketing system integrated with your application.

**Strengths**:
- Complete control over features and workflows
- Seamless integration with your app
- No per-seat costs
- Can tailor to specific needs
- Full data ownership

**Weaknesses**:
- Significant development effort
- Ongoing maintenance burden
- Must build all features (SLA tracking, reporting, etc.)
- No out-of-the-box best practices
- May reinvent the wheel

**Best For**:
- Teams with strong backend capabilities
- Unique support workflows
- When integration is more important than features
- Long-term cost savings is priority
- When data ownership is critical

**Avoid When**:
- Limited engineering resources
- Need quick time-to-market
- Don't have support system expertise
- Want proven best practices
- Small team

## Knowledge Base Platforms

### Confluence (Internal)

**Description**: Atlassian's wiki and documentation platform, often used internally.

**Strengths**:
- Powerful content creation and organization
- Good for internal documentation
- Integration with Jira
- Version control and history
- Team collaboration features
- Search functionality

**Weaknesses**:
- Not designed for customer-facing help
- Requires Confluence license
- Can be complex for simple docs
- UI may not match your app's design
- Less optimized for public help sites

**Best For**:
- Internal team documentation
- When already using Atlassian tools
- Complex documentation needs
- Team collaboration on docs

**Avoid When**:
- Customer-facing help site
- Want modern, branded help portal
- Simple documentation needs
- Don't use Atlassian tools

### GitBook

**Description**: Modern documentation platform with beautiful UI and developer-friendly workflow.

**Strengths**:
- Beautiful, modern UI
- Git-based workflow (version control)
- Easy to set up and maintain
- Good search functionality
- Can be embedded in your app
- Free tier available

**Weaknesses**:
- Less flexible than self-hosted solutions
- May require Git knowledge
- Some advanced features require paid tier
- Less customizable than custom solutions

**Best For**:
- Developer-focused documentation
- Teams comfortable with Git
- Want modern, beautiful docs
- API documentation
- When version control is important

**Avoid When**:
- Non-technical content creators
- Need deep customization
- Want complete control over hosting
- Complex content management needs

### Notion

**Description**: All-in-one workspace that can be used for knowledge bases.

**Strengths**:
- Easy to use, non-technical friendly
- Beautiful UI
- Good for collaborative editing
- Flexible page structure
- Can be made public
- Affordable

**Weaknesses**:
- Not designed specifically for help docs
- Search can be limited
- Less control over public site appearance
- May not scale well for large docs
- Performance can be slow for large sites

**Best For**:
- Small to medium documentation needs
- Non-technical content creators
- Internal documentation
- When collaboration is important
- Quick setup needed

**Avoid When**:
- Large, complex documentation
- Need advanced search
- Want complete control over public site
- Performance-critical help site
- Enterprise documentation needs

### Custom Docs Site

**Description**: Build your own documentation site (e.g., using Docusaurus, Next.js, VuePress).

**Strengths**:
- Complete control over design and branding
- Can match your app's design system
- Full control over features
- No per-seat costs
- Can integrate deeply with your app
- SEO control

**Weaknesses**:
- Requires development resources
- Ongoing maintenance
- Must build search, navigation, etc.
- May take longer to set up

**Best For**:
- Teams with frontend capabilities
- When branding is critical
- Want seamless integration with app
- Long-term cost savings
- Need custom features

**Avoid When**:
- Limited engineering resources
- Need quick setup
- Don't have documentation site expertise
- Simple documentation needs

## In-App Help Solutions

### Intercom

**Description**: Customer messaging platform with help center and chatbot capabilities.

**Strengths**:
- All-in-one solution (chat, help, email)
- Beautiful help center
- Chatbot/AI assistant
- User targeting and segmentation
- Analytics and insights
- Mobile SDKs

**Weaknesses**:
- Expensive at scale
- Can feel heavy for simple help needs
- Less control over help center design
- May include features you don't need

**Best For**:
- Customer-facing applications
- When chat support is important
- Want all-in-one solution
- Teams needing user targeting
- Applications with mobile apps

**Avoid When**:
- Simple help needs
- Budget constraints
- Want complete design control
- B2B internal tools
- Don't need chat/messaging

### Custom Help Panel

**Description**: Build your own in-app help panel integrated with your knowledge base.

**Strengths**:
- Complete design control
- Seamless integration with your app
- Can match design system perfectly
- Full control over features
- No external dependencies
- Can integrate with your knowledge base

**Weaknesses**:
- Requires development effort
- Must build search, navigation, etc.
- Ongoing maintenance
- May take time to build well

**Best For**:
- Teams with frontend capabilities
- When design consistency is critical
- Want deep integration with app
- Have existing knowledge base
- Long-term solution

**Avoid When**:
- Limited engineering resources
- Need quick solution
- Don't have help system expertise
- Simple help needs

### Chatbot (Custom or Commercial)

**Description**: AI-powered chatbot for answering user questions.

**Custom Chatbot**:
- **Strengths**: Full control, can integrate with your data, no per-message costs
- **Weaknesses**: Requires ML/AI expertise, ongoing training, development effort
- **Best For**: Teams with ML capabilities, unique use cases, long-term solution
- **Avoid When**: Limited resources, need quick solution, don't have AI expertise

**Commercial Chatbot** (e.g., Intercom, Drift, Zendesk Answer Bot):
- **Strengths**: Quick setup, pre-trained models, support and updates
- **Weaknesses**: Monthly costs, less control, may not understand domain-specific terms
- **Best For**: Quick implementation, don't have AI expertise, standard use cases
- **Avoid When**: Unique domain, want complete control, budget constraints

## Session Replay Tools

### Sentry Session Replay

**Description**: Session replay integrated with Sentry error tracking.

**Strengths**:
- Integrates with existing Sentry setup
- Privacy-focused (masks PII by default)
- Good for debugging errors
- Replay on error automatically
- Developer-friendly

**Weaknesses**:
- Requires Sentry subscription
- Less feature-rich than dedicated tools
- Primarily for error debugging, not general UX analysis

**Best For**:
- Teams already using Sentry
- When error debugging is primary use case
- Privacy-conscious applications
- Developer-focused teams

**Avoid When**:
- Need general UX analysis
- Don't use Sentry
- Want heatmaps and other analytics
- Consumer-facing applications

### LogRocket

**Description**: Session replay with console logs, network requests, and error tracking.

**Strengths**:
- Comprehensive session data
- Good for debugging
- Console and network logs included
- Good search and filtering
- Privacy controls

**Weaknesses**:
- Can be expensive
- May have performance impact
- Privacy concerns with sensitive data
- Requires careful configuration

**Best For**:
- Complex debugging needs
- When console/network logs are important
- Technical support teams
- Applications with complex state

**Avoid When**:
- Simple applications
- Budget constraints
- Privacy-sensitive data
- Don't need detailed logs

### FullStory

**Description**: Comprehensive digital experience analytics with session replay.

**Strengths**:
- Feature-rich (replay, heatmaps, funnels)
- Good search and analytics
- User-friendly interface
- Good for product teams
- Mobile support

**Weaknesses**:
- Expensive
- Can be overkill for simple needs
- Privacy concerns
- May impact performance

**Best For**:
- Product teams wanting comprehensive analytics
- When heatmaps and funnels are important
- Consumer-facing applications
- Teams needing user behavior insights

**Avoid When**:
- B2B SaaS with privacy requirements
- Simple debugging needs
- Budget constraints
- Don't need comprehensive analytics

### Hotjar

**Description**: User behavior analytics with session replay, heatmaps, and feedback.

**Strengths**:
- All-in-one solution
- Easy to set up
- Good for non-technical users
- Heatmaps and recordings
- Affordable pricing

**Weaknesses**:
- Less technical than developer-focused tools
- Privacy concerns
- May not fit B2B SaaS context
- Less control over data

**Best For**:
- Consumer-facing applications
- Product teams wanting quick insights
- When heatmaps are important
- Non-technical teams

**Avoid When**:
- B2B SaaS with privacy requirements
- Need technical debugging features
- Want complete data control
- Enterprise applications

## Recommendation Guidance

### For B2B SaaS with Vue 3/React + Spring Boot

**Recommended Stack**:

1. **Feedback Collection**: **Custom in-app widget** + **Canny** (if roadmap transparency is important)
   - Custom widget for seamless integration with Propulsion/MUI
   - Canny if you want public roadmap and voting

2. **Support/Ticketing**: **Zendesk** or **Jira Service Management**
   - Zendesk for customer-facing support
   - Jira Service Management if already using Jira Software

3. **Knowledge Base**: **Custom docs site** (Docusaurus/Next.js) or **GitBook**
   - Custom for complete control and branding
   - GitBook for quick setup with modern UI

4. **In-App Help**: **Custom help panel** integrated with knowledge base
   - Seamless integration with your app
   - Can use Propulsion/MUI components

5. **Session Replay**: **Sentry Session Replay** (if using Sentry) or **LogRocket**
   - Sentry if already in use
   - LogRocket for comprehensive debugging

### Decision Matrix Factors

**Consider**:
- **Budget**: Custom solutions have higher upfront cost but lower long-term
- **Engineering Resources**: Custom requires more resources
- **Time-to-Market**: Commercial solutions faster to implement
- **Control**: Custom gives more control, commercial gives less
- **Integration**: How well does it integrate with your stack?
- **Scalability**: Will it scale with your team/user base?

## Synergies

### Recommended Combinations

1. **Custom Widget + Zendesk + Custom Docs + Sentry**
   - Full control, proven support system, integrated help, error-focused replay

2. **Canny + Jira Service Management + GitBook + LogRocket**
   - Public roadmap, engineering-focused support, modern docs, comprehensive replay

3. **Custom Widget + Custom Ticketing + Custom Docs + Custom Help**
   - Complete ownership, seamless integration, long-term cost savings

### Integration Points

- **Feedback → Support**: Auto-create tickets from feedback submissions
- **Help → Support**: "Still need help?" links in help articles
- **Session Replay → Support**: Include replay links in bug reports
- **Support → Knowledge Base**: Create help articles from common support questions

## Evolution Triggers

### When to Upgrade/Change

**From Custom to Commercial**:
- Team can't maintain custom solution
- Need features you can't build (AI chatbot, advanced analytics)
- Support team growing rapidly
- Need faster time-to-market for new features

**From Commercial to Custom**:
- Costs becoming prohibitive
- Need deeper integration with internal systems
- Require features not available commercially
- Have engineering resources available
- Want complete data ownership

**Hybrid Approach**:
- Custom widget + Commercial ticketing (best of both worlds)
- Custom help panel + Commercial knowledge base
- Commercial feedback + Custom routing/integration

### Scaling Considerations

- **Small Team (<10)**: Start with commercial solutions, consider custom later
- **Medium Team (10-50)**: Hybrid approach (custom widget, commercial support)
- **Large Team (50+)**: More custom solutions, commercial for specialized needs
- **Enterprise**: Custom solutions with commercial for specific features
