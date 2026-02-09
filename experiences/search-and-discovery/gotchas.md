# Search & Discovery -- Gotchas

## Contents

- [Over-Engineering Search for Small Datasets](#over-engineering-search-for-small-datasets)
- [Ignoring Search Analytics and Zero-Result Queries](#ignoring-search-analytics-and-zero-result-queries)
- [Stale Search Indexes After Data Changes](#stale-search-indexes-after-data-changes)
- [Autocomplete Overwhelming the API](#autocomplete-overwhelming-the-api)
- [Faceted Search Performance with High-Cardinality Fields](#faceted-search-performance-with-high-cardinality-fields)
- [Search Relevance Tuning Without User Feedback Loops](#search-relevance-tuning-without-user-feedback-loops)
- [Full-Text Search Across Multiple Languages](#full-text-search-across-multiple-languages)
- [Assuming Users Search the Way Developers Do](#assuming-users-search-the-way-developers-do)

## Over-Engineering Search for Small Datasets

**The Problem**: Teams often jump to dedicated search engines (OpenSearch, Elasticsearch) when simple database filtering or PostgreSQL full-text search would suffice. This adds unnecessary operational complexity, infrastructure costs, and maintenance burden.

**Why It Happens**: 
- Anticipating future scale that may never materialize
- Following "best practices" without considering actual requirements
- Overestimating search complexity needs
- Fear of technical debt from starting simple

**Signs You're Over-Engineering**:
- Dataset under 10,000 records but using OpenSearch
- Simple exact-match queries but implementing full-text search
- Low search query volume (<100 queries/day) but dedicated search infrastructure
- No relevance ranking needs but implementing complex scoring algorithms

**The Fix**:
- Start with the simplest solution that meets current needs
- Use database filtering for <10K records with exact-match needs
- Use PostgreSQL FTS for 10K-1M records with full-text search needs
- Only move to dedicated search engines when you hit actual limitations
- Measure before optimizing—don't optimize for problems you don't have

**When to Evolve**:
- Dataset grows beyond current solution's comfort zone
- Users complain about search quality or performance
- Need features that current solution doesn't support (faceted search, advanced typo tolerance)
- Search becomes core to user experience and business metrics

**Cost of Over-Engineering**:
- Higher infrastructure costs (compute, storage, monitoring)
- Increased operational complexity (cluster management, data sync)
- Longer development cycles (learning curve, setup time)
- More failure modes (search infrastructure can fail independently)
- Team time diverted from features that matter

## Ignoring Search Analytics and Zero-Result Queries

**The Problem**: Many teams implement search but never track how users actually use it. Zero-result queries accumulate, users struggle silently, and search quality degrades without anyone noticing.

**Why It Happens**:
- Search "works" (returns results) so it's considered "done"
- No analytics infrastructure in place
- Assumption that users will report problems
- Focus on feature delivery over user experience measurement

**What You're Missing**:
- Zero-result queries (users searching for content that doesn't exist or using wrong terms)
- Query refinement patterns (users modifying searches, indicating initial results were poor)
- Search abandonment (users searching but not clicking results)
- Popular queries that return no results (content gaps)
- Typo patterns (common misspellings that should trigger suggestions)

**Critical Metrics to Track**:
- **Zero-result rate**: Percentage of searches with no results (target: <10%)
- **Search-to-click rate**: Percentage of searches resulting in clicks (target: >60% for finding, >40% for discovery)
- **Query refinement rate**: Percentage of searches followed by modified queries (healthy: 20-40%)
- **Time-to-first-click**: How long users take to find what they need
- **Top zero-result queries**: Most common queries that return nothing

**The Fix**:
- Log all search queries (with user context if privacy allows)
- Track result counts and click-through rates
- Monitor zero-result queries weekly/monthly
- Create alerts for zero-result rate spikes
- Build dashboards showing search effectiveness trends
- Act on insights: add missing content, improve typo handling, tune relevance

**Actionable Insights**:
- High zero-result rate for specific terms → add content or improve synonym handling
- Users refining queries frequently → initial relevance is poor, tune ranking
- Popular queries with no results → content gap, prioritize adding this content
- Common typos → add to spell-check dictionary or improve fuzzy matching

**Privacy Considerations**:
- Don't log sensitive queries (SSNs, credit cards, personal identifiers)
- Anonymize user data in analytics
- Allow users to opt out of search analytics
- Comply with data protection regulations (GDPR, CCPA)

## Stale Search Indexes After Data Changes

**The Problem**: Users search for content that was just created or updated, but it doesn't appear in results. Search indexes are out of sync with source data, creating frustrating user experiences and eroding trust.

**Why It Happens**:
- Event-driven indexing failures (events not processed, handlers crash)
- CDC (Change Data Capture) lag or failures
- Scheduled reindex jobs running too infrequently
- Manual reindex required but forgotten
- Search index updates not transactional with data changes
- Network issues between services
- Search infrastructure outages

**Impact**:
- Users can't find newly created content
- Updated content shows stale information
- Deleted content still appears in results
- Inconsistent experience across application (data exists but search doesn't find it)
- Support tickets: "I just created X but can't find it"

**Detection**:
- Monitor index lag (time between data change and search availability)
- Track search index sync failures
- Alert on stale data (queries for recently created content that don't return results)
- User reports of missing content

**The Fix**:

**Event-Driven Indexing**:
- Make event handlers idempotent (handle duplicate events gracefully)
- Implement retry logic with exponential backoff
- Monitor event processing failures
- Use dead-letter queues for failed events
- Add circuit breakers to prevent cascade failures

**CDC (Change Data Capture)**:
- Monitor CDC lag (Debezium lag metrics)
- Set up alerts for lag spikes
- Handle schema changes gracefully
- Test CDC failure scenarios

**Scheduled Reindex**:
- Run frequently enough for freshness requirements (hourly for most cases)
- Monitor reindex duration and success rate
- Consider incremental reindex for large datasets
- Have manual reindex capability for emergencies

**Hybrid Approach**:
- Event-driven for real-time updates (primary)
- Scheduled reindex for consistency checks and recovery (backup)
- Manual reindex capability for emergencies

**Consistency SLAs**:
- Define acceptable lag (e.g., <5 seconds for event-driven, <1 hour for scheduled)
- Monitor and alert on SLA violations
- Communicate consistency model to users if needed ("Search may take a few seconds to reflect new content")

**Testing**:
- Test index synchronization after create/update/delete operations
- Load test event processing
- Test CDC failure scenarios
- Verify scheduled reindex completes successfully

## Autocomplete Overwhelming the API

**The Problem**: Autocomplete triggers on every keystroke, sending hundreds of requests per user session. Without proper debouncing, rate limiting, and caching, this can overwhelm backend APIs and degrade performance for all users.

**Why It Happens**:
- No debouncing (requests on every keystroke)
- Too aggressive minimum character threshold (triggers on 1-2 characters)
- No request cancellation (abandoned requests still complete)
- Missing caching (same queries hit backend repeatedly)
- No rate limiting on autocomplete endpoint
- Frontend makes requests even when user stops typing

**Impact**:
- Backend API overload (hundreds of requests per user)
- Increased infrastructure costs
- Degraded performance for all users
- Wasted compute resources
- Potential API rate limit violations
- Poor user experience (slow autocomplete responses)

**The Fix**:

**Debouncing**:
- Wait 200-300ms after user stops typing before triggering request
- Cancel pending requests when user continues typing
- Balance responsiveness with backend load

```typescript
// Proper debouncing example
const debouncedSearch = useDebounceFn(async (query: string) => {
  // Cancel previous request if still pending
  if (pendingRequest) {
    pendingRequest.abort()
  }
  
  if (query.length >= 3) { // Minimum 3 characters
    pendingRequest = fetchSuggestions(query)
    suggestions.value = await pendingRequest
  }
}, 250) // 250ms debounce
```

**Minimum Character Threshold**:
- Require 2-3 characters before showing suggestions
- Prevents overwhelming suggestions on single characters
- Reduces backend load significantly

**Request Cancellation**:
- Cancel pending requests when user continues typing
- Use AbortController for fetch requests
- Don't process responses for cancelled requests

**Caching**:
- Cache autocomplete suggestions (short TTL: 5-10 minutes)
- Cache popular queries longer
- Invalidate cache on data updates
- Use HTTP cache headers appropriately

**Rate Limiting**:
- Implement rate limiting on autocomplete endpoint
- More lenient than main search (autocomplete is lighter)
- Return cached results when rate limited
- Consider per-user vs. per-IP rate limiting

**Backend Optimization**:
- Optimize autocomplete queries (use completion suggester in OpenSearch)
- Limit result count (5-10 suggestions max)
- Use dedicated autocomplete endpoint (lighter than full search)
- Monitor autocomplete endpoint performance separately

**Monitoring**:
- Track autocomplete request volume
- Monitor autocomplete endpoint latency
- Alert on unusual spikes
- Track cache hit rates

## Faceted Search Performance with High-Cardinality Fields

**The Problem**: Faceted search (filtering by categories, tags, etc.) performs poorly when fields have many unique values (high cardinality). Computing facet counts becomes expensive, and response times degrade significantly.

**Why It Happens**:
- Facet aggregation requires counting distinct values across all matching documents
- High-cardinality fields (e.g., user IDs, timestamps, unique tags) create many distinct values
- Each distinct value requires a separate count calculation
- No optimization for high-cardinality faceting
- Facets computed on every search query

**Examples of High-Cardinality Fields**:
- User IDs (thousands of unique users)
- Timestamps (millions of unique timestamps)
- Unique tags (each document has unique tags)
- Product SKUs (thousands of unique products)
- Email addresses (highly unique)

**Impact**:
- Slow search response times (seconds instead of milliseconds)
- High backend load (expensive aggregations)
- Poor user experience (slow filter updates)
- Scalability issues (performance degrades with data growth)

**The Fix**:

**Avoid High-Cardinality Facets**:
- Don't facet on unique identifiers (IDs, emails, timestamps)
- Use low-cardinality fields for faceting (categories, status, price ranges)
- Prefer binned/ranged facets for high-cardinality data (date ranges, price ranges)

**Facet Optimization**:
- Limit facet result counts (top 10-20 values only)
- Use approximate counts for high-cardinality facets (faster, less accurate)
- Cache facet counts (they change less frequently than search results)
- Compute facets asynchronously for expensive cases

**Field Design**:
- Create low-cardinality fields specifically for faceting (category, status, type)
- Bin high-cardinality data (price ranges, date ranges, size ranges)
- Use hierarchical facets (category → subcategory) instead of flat high-cardinality

**Search Engine Configuration**:
- Use OpenSearch/Elasticsearch aggregations efficiently
- Configure field data types appropriately (keyword vs. text)
- Use doc_values for efficient aggregations
- Consider separate indices for faceted vs. non-faceted searches

**Alternative Patterns**:
- Pre-compute popular facet combinations
- Load facets separately from search results (different endpoints)
- Use client-side faceting for small result sets
- Lazy-load facets (only compute when user expands facet section)

**Monitoring**:
- Track facet computation time separately from search time
- Monitor high-cardinality facet performance
- Alert on facet performance degradation
- Consider removing slow facets

## Search Relevance Tuning Without User Feedback Loops

**The Problem**: Teams tune search relevance algorithms based on developer intuition or test data, but don't incorporate actual user behavior. Relevance improves in theory but degrades in practice because users don't search the way developers expect.

**Why It Happens**:
- No analytics on which results users actually click
- Tuning based on developer assumptions about relevance
- Test data doesn't reflect real user queries
- No A/B testing framework for relevance changes
- Tuning in isolation without user feedback

**The Gap**:
- Developers think: "Exact matches should rank highest"
- Users actually: Click on partial matches that are more relevant to their context
- Developers think: "Recent content should rank higher"
- Users actually: Prefer popular or frequently accessed content regardless of recency

**What You Need**:
- **Click-through data**: Which results do users actually click?
- **Time-to-click**: How quickly do users find what they need?
- **Query refinement patterns**: Do users modify queries (indicating poor initial results)?
- **Search abandonment**: Do users search but not click anything?
- **User context**: What role, permissions, or history affects relevance?

**The Fix**:

**Implement Feedback Loops**:
- Track result clicks with query context
- Measure time-to-first-click (faster = better relevance)
- Track query refinements (users modifying queries)
- Monitor search abandonment rates
- Segment by user persona/role

**A/B Testing**:
- Test relevance algorithm changes with real users
- Compare metrics: click-through rate, time-to-click, abandonment
- Run tests long enough for statistical significance
- Don't ship changes that degrade user metrics

**User Behavior Analysis**:
- Analyze top queries and their clicked results
- Identify patterns: what makes users click?
- Find queries with poor click-through (relevance issues)
- Discover content gaps (popular queries with no good results)

**Iterative Tuning**:
- Start with baseline relevance algorithm
- Measure user behavior
- Make small, incremental changes
- Measure impact of each change
- Roll back changes that degrade metrics

**Context-Aware Relevance**:
- Consider user role/permissions (show relevant content user can access)
- Consider user history (prefer content user has interacted with)
- Consider business rules (boost featured content, promotions)
- Consider recency vs. popularity balance

**Avoid Over-Tuning**:
- Don't optimize for edge cases at expense of common cases
- Don't tune based on single user complaints
- Don't make changes without measuring impact
- Balance relevance with other factors (diversity, freshness)

**Tools**:
- Search analytics platforms (if available)
- Custom analytics dashboards
- A/B testing frameworks
- Log analysis tools

## Full-Text Search Across Multiple Languages

**The Problem**: Full-text search works well for English but breaks down when content spans multiple languages. Different languages have different word boundaries, stemming rules, and character sets. A single search configuration fails to handle multilingual content effectively.

**Why It Happens**:
- Default search configuration optimized for English
- No language detection or per-language analyzers
- Character encoding issues (accents, special characters)
- Different word segmentation rules (Chinese, Japanese don't use spaces)
- Stemming/lemmatization language-specific
- Stop words language-specific

**Impact**:
- Poor search results for non-English content
- Accented characters not matching (café vs. cafe)
- Asian languages (Chinese, Japanese) not tokenized correctly
- Users can't find content in their language
- Reduced international user satisfaction

**The Fix**:

**Language Detection**:
- Detect document language during indexing
- Detect query language during search
- Use language-specific analyzers per document/field
- Handle mixed-language content (documents with multiple languages)

**Per-Language Analyzers**:
- Configure analyzers for each supported language
- Use appropriate stemmers for each language
- Configure language-specific stop words
- Handle language-specific tokenization (CJK languages)

**Character Normalization**:
- Normalize accented characters (café → cafe for matching)
- Handle Unicode normalization (NFD vs. NFC)
- Preserve original for display but normalize for search
- Consider user expectations (some users want exact accent matching)

**Multi-Field Mapping**:
- Index same content with multiple analyzers (English, Spanish, etc.)
- Query across all language variants
- Boost results matching user's detected language

**CJK Languages (Chinese, Japanese, Korean)**:
- Use specialized tokenizers (no word boundaries)
- Consider n-gram tokenization
- May require different search strategies entirely

**Search Engine Configuration**:

**PostgreSQL FTS**:
- Use language-specific text search configurations
- Create configurations for each language: `CREATE TEXT SEARCH CONFIGURATION spanish ...`
- Specify configuration per query: `to_tsvector('spanish', content)`

**OpenSearch/Elasticsearch**:
- Use language-specific analyzers in field mappings
- Configure analyzers per language
- Use `multi_field` to index with multiple analyzers
- Consider language detection plugins

**User Experience**:
- Allow users to specify search language preference
- Auto-detect query language when possible
- Show language filter in UI if content is multilingual
- Handle language-specific query suggestions

**Testing**:
- Test search with content in all supported languages
- Test accent handling (café, résumé, naïve)
- Test CJK language tokenization
- Test mixed-language queries
- Verify language detection accuracy

**Limitations**:
- Supporting many languages increases complexity significantly
- May need to prioritize languages based on user base
- Some languages require specialized expertise
- Consider using translation APIs for cross-language search

## Assuming Users Search the Way Developers Do

**The Problem**: Developers build search based on how they would search (exact terms, technical language, boolean operators) rather than how actual users search (natural language, typos, vague queries, context-dependent).

**Why It Happens**:
- Developers test with their own queries (technical, precise)
- Assumptions about user knowledge and behavior
- No user research or analytics
- Building for power users instead of casual users
- Not understanding user mental models

**The Gap**:

**Developers Search**:
- Exact terms: "invoice status pending"
- Technical language: "SELECT * FROM invoices WHERE status = 'pending'"
- Boolean operators: "backup AND cloud NOT on-premise"
- Field-specific: "name:John status:active"
- No typos (they know the system)

**Users Actually Search**:
- Natural language: "pending invoices" or "invoices that are pending"
- Business language: "unpaid bills" (not "invoices with status pending")
- Vague queries: "that thing I worked on last week"
- Typos: "invocie", "custmer", "reciept"
- Context-dependent: "my invoices" (user-specific, not global)
- Single words: "backup" (expecting relevant results, not exact matches)

**Impact**:
- Users can't find content (search doesn't match their mental model)
- High zero-result rates
- Users give up and use navigation instead
- Support tickets: "Search doesn't work"
- Reduced user satisfaction and productivity

**The Fix**:

**User Research**:
- Interview users about how they search
- Analyze actual search queries (what do users type?)
- Observe users using search (usability testing)
- Understand user mental models and vocabulary

**Natural Language Support**:
- Accept natural language queries
- Handle synonyms ("invoice" = "bill" = "receipt" in some contexts)
- Understand context ("my" = user-specific, "recent" = time-based)
- Parse intent from vague queries

**Typo Tolerance**:
- Implement fuzzy matching (handle 1-2 character errors)
- Common typo patterns (transpositions, missing characters)
- "Did you mean?" suggestions for likely typos
- Don't require perfect spelling

**Progressive Disclosure**:
- Default: simple search box (natural language)
- Advanced: optional advanced search (boolean operators, field-specific)
- Don't require advanced features for basic use
- Make advanced features discoverable but not required

**Context Awareness**:
- User-specific results when appropriate ("my invoices")
- Role-based filtering (show content user can access)
- Recent/popular content prioritization
- Location/time context when relevant

**Query Understanding**:
- Detect query intent (finding vs. discovering)
- Handle implicit filters (user context, permissions)
- Parse natural language into structured queries
- Handle ambiguous queries gracefully

**Testing with Real Users**:
- Test with actual user queries (from analytics)
- Include non-technical users in testing
- Test with typos and natural language
- Measure success with user metrics, not developer metrics

**Analytics-Driven Improvement**:
- Analyze zero-result queries (what are users searching for?)
- Track query refinement (users modifying queries)
- Identify common query patterns
- Improve search based on actual usage, not assumptions

**Example Improvements**:
- User searches "unpaid" → understand they mean "invoices with status pending payment"
- User searches "last week" → apply time-based filter
- User searches "invocie" → fuzzy match to "invoice" and suggest correction
- User searches "backup" → return relevant backup products, not just exact matches

**Avoid Developer-Centric Defaults**:
- Don't default to exact match (use fuzzy/relevance by default)
- Don't require field-specific syntax (handle natural language)
- Don't assume users know content structure
- Don't optimize for power users at expense of casual users
