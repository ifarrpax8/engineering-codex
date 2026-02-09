---
recommendation_type: decision-matrix
---

# Search & Discovery -- Options

## Contents

- [Options](#options)
- [Evaluation Criteria](#evaluation-criteria)
- [Decision Framework](#decision-framework)
- [Synergies](#synergies)
- [Evolution Triggers](#evolution-triggers)

## Options

### Option 1: Database Filtering Only

**Description**: Standard SQL WHERE clauses with query parameters. Simple text matching using LIKE/ILIKE for basic prefix or substring matching. No full-text search capabilities, no relevance ranking, no typo tolerance.

**Strengths**:
- Simplest to implement—no additional infrastructure
- No new dependencies or services to operate
- Works immediately with existing database
- Low operational overhead
- Sufficient for exact-match or simple filtering use cases
- Fast for small datasets with proper indexes

**Weaknesses**:
- No relevance ranking (results ordered by database default, typically ID or creation date)
- No typo tolerance (exact or prefix match only)
- Poor performance for full-text search across long text fields
- No advanced features: autocomplete, faceted search, highlighting
- Doesn't scale well for large datasets or complex queries
- LIKE queries can be slow even with indexes on large tables

**Best For**:
- Small datasets (<10,000 records)
- Exact-match searches (IDs, codes, exact names)
- Simple filtering use cases
- Applications where search is secondary to navigation
- Prototypes or MVPs where speed of implementation matters more than search quality
- Internal tools with technical users who know exact identifiers

**Avoid When**:
- Users expect Google-like search behavior
- Need to search across multiple fields simultaneously with relevance
- Require typo tolerance or fuzzy matching
- Need autocomplete/type-ahead functionality
- Dataset will grow beyond 10,000-50,000 records
- Search is a primary user interaction pattern
- Users are non-technical and rely on natural language queries

**Implementation Complexity**: Low  
**Operational Complexity**: Low  
**Performance**: Good for small datasets, degrades with size  
**Relevance Quality**: Poor (no ranking)  
**Feature Richness**: Minimal

---

### Option 2: PostgreSQL Full-Text Search

**Description**: PostgreSQL's built-in full-text search using `tsvector` and `tsquery` types, with GIN indexes for performance. Supports relevance ranking via `ts_rank()` or `ts_rank_cd()`. Can be enhanced with `pg_trgm` extension for fuzzy matching and similarity search.

**Strengths**:
- No additional infrastructure—uses existing PostgreSQL database
- Built-in relevance ranking (ts_rank functions)
- Good performance for medium-sized datasets (10K-1M records)
- Supports multiple languages (with appropriate text search configurations)
- Can combine full-text search with regular WHERE clauses for filtering
- GIN indexes provide good query performance
- `pg_trgm` extension adds fuzzy matching capabilities
- No new services to operate or monitor
- Lower cost than dedicated search infrastructure

**Weaknesses**:
- Performance can degrade with very large datasets (>1M records, depending on query complexity)
- Limited advanced features compared to dedicated search engines
- Faceted search requires manual implementation (GROUP BY queries)
- Autocomplete requires custom implementation (prefix queries or trigrams)
- Index updates require manual refresh or triggers (not always real-time)
- Less flexible than dedicated search engines for complex relevance tuning
- Highlighting requires `ts_headline()` function (less flexible than search engines)

**Best For**:
- Medium datasets (10,000 - 1,000,000 records)
- Applications already using PostgreSQL
- Need full-text search but want to avoid additional infrastructure
- Good balance of features and simplicity
- Teams familiar with PostgreSQL
- Budget-conscious projects (no additional infrastructure costs)
- Applications where search is important but not the primary feature

**Avoid When**:
- Very large datasets (>1M records) where performance becomes a concern
- Need advanced features: complex faceted search, aggregations, distributed search
- Require real-time search index updates (PostgreSQL FTS can have small delays)
- Need to search across multiple services/data sources
- Complex relevance tuning requirements beyond basic ranking
- High search query volume requiring dedicated search infrastructure

**Implementation Complexity**: Medium  
**Operational Complexity**: Low-Medium (PostgreSQL administration)  
**Performance**: Good for medium datasets, may require optimization for large datasets  
**Relevance Quality**: Good (configurable ranking)  
**Feature Richness**: Moderate

---

### Option 3: OpenSearch (Recommended for Advanced Needs)

**Description**: Open-source, distributed search and analytics engine (fork of Elasticsearch). Full-featured search engine with relevance ranking, typo tolerance, faceted search, aggregations, highlighting, and more. Designed specifically for search workloads.

**Strengths**:
- Excellent performance even with very large datasets (millions to billions of records)
- Advanced features: faceted search, aggregations, highlighting, completion suggesters
- Highly configurable relevance ranking (multiple algorithms, custom scoring)
- Built-in typo tolerance and fuzzy matching
- Distributed architecture scales horizontally
- Real-time or near-real-time index updates
- Rich query DSL for complex search requirements
- Completion suggester optimized for autocomplete
- Can search across multiple indices (unified search across services)
- Active community and extensive documentation
- Open-source (no licensing costs)

**Weaknesses**:
- Additional infrastructure to operate and monitor
- Steeper learning curve (query DSL, index management, cluster operations)
- Requires data synchronization from primary database (event-driven, CDC, or scheduled)
- Resource intensive (memory and disk requirements)
- Operational complexity (cluster management, index lifecycle, backups)
- Eventual consistency considerations (data sync lag)
- Team needs expertise in search engine operations
- Higher infrastructure costs (compute and storage)

**Best For**:
- Large datasets (>1M records)
- Search is a primary user interaction pattern
- Need advanced features: faceted search, aggregations, highlighting
- High search query volume
- Complex relevance tuning requirements
- Applications where search quality directly impacts business metrics
- Teams with search engine expertise or willingness to learn
- Distributed architectures (can search across multiple services)
- E-commerce, content platforms, or applications where search is core to UX

**Avoid When**:
- Small or medium datasets where PostgreSQL FTS is sufficient
- Simple search requirements (exact match, basic filtering)
- Team lacks expertise or resources to operate search infrastructure
- Budget constraints (infrastructure and operational costs)
- Search is a secondary feature
- Prototype or MVP where speed of implementation matters more than search quality

**Implementation Complexity**: High  
**Operational Complexity**: High (cluster management, monitoring, data sync)  
**Performance**: Excellent (scales to very large datasets)  
**Relevance Quality**: Excellent (highly configurable)  
**Feature Richness**: Very High

---

### Option 4: Lightweight Search Engine (Meilisearch or Typesense)

**Description**: Lightweight, easy-to-operate search engines designed for simplicity and developer experience. Meilisearch and Typesense are popular options that provide many search engine features with lower operational complexity than OpenSearch/Elasticsearch.

**Strengths**:
- Easier to operate than OpenSearch (simpler architecture, fewer moving parts)
- Good performance for medium to large datasets
- Many advanced features: typo tolerance, faceted search, highlighting
- Faster to get started (simpler setup and configuration)
- Lower resource requirements than OpenSearch
- Good developer experience (simpler API, better defaults)
- Real-time index updates
- Built-in typo tolerance and relevance ranking
- Good documentation and developer-friendly APIs

**Weaknesses**:
- Less mature ecosystem than OpenSearch (fewer integrations, smaller community)
- May not scale to the same extremes as OpenSearch (billions of records)
- Fewer advanced features compared to OpenSearch (e.g., complex aggregations)
- Still requires additional infrastructure (though simpler than OpenSearch)
- Data synchronization still needed (same patterns as OpenSearch)
- Less flexibility for complex relevance tuning compared to OpenSearch
- Smaller talent pool familiar with these tools

**Best For**:
- Medium to large datasets (100K - 10M records)
- Need search engine features but want simpler operations than OpenSearch
- Teams wanting good search quality without OpenSearch complexity
- Applications where search is important but operational simplicity matters
- Good balance of features and ease of operation
- Teams new to search engines (gentler learning curve)
- Single-server or small-cluster deployments

**Avoid When**:
- Very large datasets (>10M records) where OpenSearch's scalability is needed
- Need advanced OpenSearch-specific features (complex aggregations, ML ranking)
- Require distributed search across many nodes (OpenSearch better suited)
- Enterprise requirements for mature, widely-adopted technology
- Need extensive ecosystem integrations

**Implementation Complexity**: Medium-High  
**Operational Complexity**: Medium (simpler than OpenSearch, more than PostgreSQL)  
**Performance**: Good to Excellent (depends on dataset size)  
**Relevance Quality**: Good (configurable, good defaults)  
**Feature Richness**: High (most features, fewer advanced options than OpenSearch)

---

## Evaluation Criteria

| Criterion | Database Filtering | PostgreSQL FTS | OpenSearch | Lightweight Search |
|-----------|------------------|----------------|------------|-------------------|
| **Implementation Effort** | Low | Medium | High | Medium-High |
| **Operational Complexity** | Low | Low-Medium | High | Medium |
| **Infrastructure Cost** | None | None | High | Medium |
| **Performance (Small <10K)** | Excellent | Excellent | Excellent | Excellent |
| **Performance (Medium 10K-1M)** | Poor | Good | Excellent | Excellent |
| **Performance (Large >1M)** | Poor | Fair | Excellent | Good-Excellent |
| **Relevance Ranking** | None | Good | Excellent | Good |
| **Typo Tolerance** | None | Limited (with pg_trgm) | Excellent | Excellent |
| **Autocomplete** | Manual | Manual | Built-in | Built-in |
| **Faceted Search** | Manual | Manual | Built-in | Built-in |
| **Highlighting** | Manual | Limited | Built-in | Built-in |
| **Real-time Updates** | Immediate | Trigger-based | Real-time | Real-time |
| **Scalability** | Poor | Fair | Excellent | Good |
| **Learning Curve** | Low | Medium | High | Medium |

## Decision Framework

**Start with Database Filtering if**:
- Dataset is small (<10K records)
- Search is secondary to navigation
- Need to ship quickly with minimal complexity
- Users search by exact identifiers

**Upgrade to PostgreSQL FTS when**:
- Dataset grows beyond 10K records
- Users need full-text search across multiple fields
- Want relevance ranking without additional infrastructure
- Already using PostgreSQL

**Move to Dedicated Search Engine (OpenSearch or Lightweight) when**:
- Dataset exceeds 1M records (or PostgreSQL FTS performance degrades)
- Search is a primary user interaction pattern
- Need advanced features: faceted search, autocomplete, highlighting
- Users expect Google-like search quality
- Business metrics depend on search effectiveness

**Choose OpenSearch if**:
- Very large datasets (>10M records)
- Need maximum flexibility and advanced features
- Have team expertise or resources for operational complexity
- Distributed search across multiple services

**Choose Lightweight Search (Meilisearch/Typesense) if**:
- Want search engine features with simpler operations
- Medium to large datasets (100K-10M records)
- Team new to search engines (gentler learning curve)
- Good balance of features and simplicity

## Synergies

### With API Design Facet

**Search Endpoint Design**:
- Database Filtering: Enhance existing list endpoints with query parameters
- PostgreSQL FTS: May use separate `/search` endpoint or enhance list endpoints
- Dedicated Search Engines: Typically separate `/search` endpoint optimized for search

**Pagination Patterns**:
- All options benefit from cursor-based pagination for large result sets
- Search engines support efficient deep pagination better than database OFFSET

**API Versioning**:
- Search algorithm changes may require API versioning
- Relevance tuning changes shouldn't break API contracts

### With Data Persistence Facet

**Database Indexing**:
- Database Filtering: Standard B-tree indexes on filtered columns
- PostgreSQL FTS: GIN indexes on `tsvector` columns
- Dedicated Search Engines: Separate search indexes (read models)

**Data Synchronization**:
- PostgreSQL FTS: Update `tsvector` columns via triggers or application logic
- Dedicated Search Engines: Event-driven indexing, CDC, or scheduled reindex
- See Architecture document for synchronization patterns

**Transactional Considerations**:
- Database Filtering: Immediate consistency (same transaction)
- PostgreSQL FTS: Near-immediate (trigger-based) or eventual (scheduled)
- Dedicated Search Engines: Eventual consistency (seconds to minutes delay)

### With Performance Facet

**Caching Strategies**:
- All options benefit from caching frequent queries
- Search engines may have built-in caching
- Consider CDN caching for public search results

**Query Optimization**:
- Database Filtering: Optimize WHERE clauses and indexes
- PostgreSQL FTS: Tune `tsvector` configuration and GIN indexes
- Search Engines: Tune analyzers, field mappings, and relevance algorithms

**Monitoring**:
- Track search latency (p95, p99) for all options
- Monitor search index size and growth
- Alert on search error rates and zero-result rates

## Evolution Triggers

**Migrate from Database Filtering to PostgreSQL FTS when**:
- Dataset grows beyond 10K-50K records
- Users complain about search quality or performance
- Need relevance ranking or full-text search
- Zero-result rate is high due to exact-match limitations

**Migrate from PostgreSQL FTS to Dedicated Search Engine when**:
- Dataset exceeds 1M records and performance degrades
- Need advanced features: faceted search, autocomplete, highlighting
- Search is core to user experience and business metrics
- Users expect Google-like search quality
- PostgreSQL FTS limitations become blockers

**Consider OpenSearch over Lightweight Search when**:
- Dataset exceeds 10M records
- Need maximum scalability and advanced features
- Have team expertise for operational complexity
- Require distributed search across multiple services

**Consider Lightweight Search over OpenSearch when**:
- Want simpler operations without sacrificing too many features
- Team is new to search engines
- Good-enough performance is sufficient (don't need maximum scale)
- Operational simplicity is a priority

**General Evolution Principles**:
- Start simple, evolve based on actual needs (not anticipated needs)
- Measure search effectiveness before and after migrations
- Consider migration effort vs. benefit
- Don't over-engineer for scale you don't have yet
- Monitor metrics to identify when evolution is needed
