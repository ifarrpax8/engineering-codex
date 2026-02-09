# Search & Discovery -- Architecture

## Contents

- [The Search Implementation Spectrum](#the-search-implementation-spectrum)
- [Data Synchronization Patterns](#data-synchronization-patterns)
- [Search Architecture Patterns](#search-architecture-patterns)
- [Autocomplete/Type-Ahead Architecture](#autocompletetype-ahead-architecture)
- [Faceted Search](#faceted-search)
- [Cross-Service Search](#cross-service-search)
- [Performance Considerations](#performance-considerations)
- [Integration with API Design](#integration-with-api-design)
- [Integration with Data Persistence](#integration-with-data-persistence)

## The Search Implementation Spectrum

Search capabilities exist on a spectrum from simple database queries to dedicated search infrastructure. Choose the right level based on your requirements, data volume, and user expectations.

### Level 1: Database Filtering

**What it is**: Standard SQL WHERE clauses with query parameters, potentially with LIKE or ILIKE for text matching.

**When it's enough**:
- Small datasets (<10,000 records)
- Exact match or simple prefix matching is sufficient
- Users search by known identifiers (IDs, codes, exact names)
- No need for typo tolerance or relevance ranking
- Simple filtering needs (status, date ranges, categories)

**When it's not enough**:
- Users expect Google-like search behavior
- Need to search across multiple fields simultaneously
- Require typo tolerance or fuzzy matching
- Need relevance ranking (most important results first)
- Full-text search across long documents or descriptions
- Autocomplete/type-ahead requirements

**Implementation**: Standard Spring Boot endpoints with JPA/Hibernate queries. Frontend passes query parameters, backend applies filters.

```kotlin
// Example: Simple filtering endpoint
@GetMapping("/products")
fun getProducts(
    @RequestParam(required = false) name: String?,
    @RequestParam(required = false) category: String?,
    @RequestParam(required = false) minPrice: BigDecimal?
): List<Product> {
    // Build dynamic WHERE clauses based on provided parameters
}
```

### Level 2: PostgreSQL Full-Text Search

**What it is**: PostgreSQL's built-in full-text search using `tsvector` and `tsquery`, with GIN indexes for performance.

**When it's enough**:
- Medium datasets (10,000 - 1M records)
- Need full-text search across multiple columns
- Want relevance ranking without external infrastructure
- Already using PostgreSQL (no new dependencies)
- Moderate typo tolerance needs (can use trigram similarity)
- Autocomplete possible with prefix matching

**When it's not enough**:
- Very large datasets (>1M records) where search performance degrades
- Need advanced features: faceted search, aggregations, highlighting
- Require distributed search across multiple data sources
- Need real-time search index updates (PostgreSQL FTS requires manual refresh)

**Implementation**: 
- Create `tsvector` columns (or computed columns) for searchable text
- Build GIN indexes on `tsvector` columns
- Use `ts_rank()` or `ts_rank_cd()` for relevance scoring
- Combine with regular WHERE clauses for filtering

```kotlin
// Example: PostgreSQL full-text search
@Query("""
    SELECT p, ts_rank(p.search_vector, plainto_tsquery(:query)) as rank
    FROM Product p
    WHERE p.search_vector @@ plainto_tsquery(:query)
    ORDER BY rank DESC
    LIMIT :limit
""")
fun searchProducts(@Param("query") query: String, @Param("limit") limit: Int): List<Product>
```

**Data Synchronization**: Update `tsvector` columns on INSERT/UPDATE via database triggers or application-level logic.

### Level 3: Dedicated Search Engine

**What it is**: Separate search infrastructure optimized for search workloads. OpenSearch (recommended), Elasticsearch, Meilisearch, or Typesense.

**When it's enough** (and often necessary):
- Large datasets (>1M records)
- Need advanced features: faceted search, aggregations, highlighting, typo tolerance
- Require real-time or near-real-time search index updates
- Need distributed search across multiple services/data sources
- Complex relevance tuning requirements
- High search query volume requiring dedicated infrastructure

**When it might be overkill**:
- Small datasets where PostgreSQL FTS is sufficient
- Simple exact-match or filtering use cases
- Team lacks expertise to operate search infrastructure
- Budget constraints (though open-source options help)

**Architecture Pattern**: Search index as a read model, synchronized from primary database via events or CDC.

## Data Synchronization Patterns

Keeping search indexes in sync with source data is critical. Choose based on your consistency requirements and infrastructure.

### Event-Driven Indexing

**Pattern**: Domain events trigger search index updates asynchronously.

**Pros**:
- Decoupled from primary database transactions
- Can handle high write volumes
- Natural fit for event-sourced architectures
- Can batch updates for efficiency

**Cons**:
- Eventual consistency (small delay between data change and search availability)
- Requires event infrastructure
- Must handle event processing failures

**Implementation**: 
- Emit domain events on data changes (e.g., `ProductCreated`, `ProductUpdated`)
- Event handler updates search index
- Use idempotent handlers to handle duplicate events

```kotlin
// Example: Event-driven indexing
@EventListener
fun handleProductCreated(event: ProductCreatedEvent) {
    searchService.indexProduct(event.product)
}

@EventListener
fun handleProductUpdated(event: ProductUpdatedEvent) {
    searchService.updateProduct(event.product)
}
```

### Change Data Capture (CDC)

**Pattern**: Capture database changes (INSERT/UPDATE/DELETE) and stream to search index.

**Pros**:
- No application code changes required
- Captures all changes, including direct database updates
- Works with any application framework

**Cons**:
- Requires CDC infrastructure (e.g., Debezium)
- More complex setup and monitoring
- Must handle schema changes

**Implementation**: Debezium captures PostgreSQL WAL changes, streams to Kafka, consumer updates search index.

### Scheduled Reindex

**Pattern**: Periodic batch job rebuilds search index from source data.

**Pros**:
- Simple to implement
- No real-time infrastructure required
- Can optimize index structure during rebuild

**Cons**:
- Stale data between runs (minutes to hours)
- Full reindex can be expensive for large datasets
- Not suitable for real-time requirements

**Implementation**: Scheduled Spring Boot job queries database and updates search index. Run hourly or daily depending on freshness requirements.

### Hybrid Approach

Combine patterns: event-driven for real-time updates, scheduled reindex for consistency checks and recovery.

## Search Architecture Patterns

### Separate Search Endpoint

**Pattern**: Dedicated `/search` endpoint separate from list/filter endpoints.

**Pros**:
- Clear separation of concerns
- Can optimize specifically for search (caching, indexing)
- Different pagination/ranking strategies

**Cons**:
- Two code paths to maintain
- Frontend must choose between search and list endpoints

**When to use**: When search behavior is meaningfully different from filtering (relevance ranking, typo tolerance, cross-field search).

### Enhanced List Endpoint

**Pattern**: Existing list endpoint accepts optional `q` parameter for search.

**Pros**:
- Single endpoint for frontend
- Simpler API surface
- Consistent pagination/filtering behavior

**Cons**:
- May not optimize well for both use cases
- Can become complex with many parameters

**When to use**: When search is essentially "smart filtering" and results can use same structure as filtered lists.

### Search Index as Read Model

**Pattern**: Search index is a denormalized read model optimized for queries, synchronized from transactional database.

**Pros**:
- Optimize search index structure independently
- Don't impact transactional database performance
- Can combine data from multiple sources

**Cons**:
- Data duplication and synchronization complexity
- Eventual consistency considerations

**When to use**: With dedicated search engines or when search needs differ significantly from transactional queries.

## Autocomplete/Type-Ahead Architecture

Autocomplete provides suggestions as users type, improving UX and reducing query errors.

### Prefix Queries

**Pattern**: Query search index for documents matching prefix of user input.

**Implementation**: 
- User types "inv" → query for documents starting with "inv"
- Use search engine prefix queries or PostgreSQL `LIKE 'inv%'` with index
- Limit results (e.g., top 10 suggestions)

**Pros**: Simple, works with any search backend

**Cons**: Doesn't handle typos, requires exact prefix match

### Edge N-grams

**Pattern**: Index terms broken into n-grams (e.g., "invoice" → "in", "inv", "invo", "invoi", "invoic", "invoice").

**Implementation**: 
- Index time: tokenize and create n-gram tokens
- Query time: match n-grams from user input
- Search engine handles this automatically with appropriate analyzers

**Pros**: Handles partial word matches, works well for autocomplete

**Cons**: Larger index size, more complex configuration

### Completion Suggester (OpenSearch/Elasticsearch)

**Pattern**: Special data structure optimized for autocomplete with fast prefix matching.

**Implementation**: 
- Build completion suggester field in search index
- Query using completion suggester API
- Returns suggestions ranked by relevance/frequency

**Pros**: Very fast, designed specifically for autocomplete, handles large datasets

**Cons**: Requires OpenSearch/Elasticsearch, separate from main search index

**Recommendation**: Use completion suggester for dedicated search engines, edge n-grams for PostgreSQL FTS.

## Faceted Search

Faceted search allows users to filter results by categories, attributes, or dimensions while seeing result counts.

### Architecture

**Pattern**: Search returns both results and aggregations/facets.

**Implementation**:
- Search query includes aggregation requests (e.g., count by category, price ranges)
- Backend returns results + facet data (category: "Software" (45), "Hardware" (23))
- Frontend displays facets with counts, users click to filter
- Subsequent searches include selected facet filters

**Example Response**:
```json
{
  "results": [...],
  "facets": {
    "category": [
      {"value": "Software", "count": 45},
      {"value": "Hardware", "count": 23}
    ],
    "priceRange": [
      {"value": "$0-$50", "count": 30},
      {"value": "$50-$100", "count": 38}
    ]
  }
}
```

**Backend**: Use search engine aggregations (OpenSearch) or PostgreSQL GROUP BY with filtered counts.

**Frontend**: Display facets as checkboxes or links with counts, update search when facets selected.

## Cross-Service Search

When search spans multiple bounded contexts or services:

**Pattern**: Federated search or unified search index.

**Federated Search**:
- Query multiple services in parallel
- Merge and rank results client-side or via aggregator service
- Pros: Services remain independent
- Cons: Complex ranking, potential inconsistency

**Unified Search Index**:
- Each service publishes searchable data to shared search index
- Single search endpoint queries unified index
- Pros: Consistent ranking, single query
- Cons: Cross-service coupling, synchronization complexity

**Recommendation**: Start with federated search for independence, move to unified index if search becomes core to user experience.

## Performance Considerations

**Indexing Performance**:
- Batch index updates for efficiency
- Use async processing to avoid blocking user requests
- Monitor index lag (time between data change and search availability)

**Query Performance**:
- Cache frequent queries (with appropriate invalidation)
- Limit result sets and use pagination
- Optimize search index structure (analyzers, field types)
- Monitor query latency (p95, p99)

**Scalability**:
- Search engines can scale horizontally (add nodes)
- PostgreSQL FTS may require read replicas for high query volume
- Consider search result caching at CDN/edge for public content

## Integration with API Design

See [API Design facet](../../facets/api-design/) for:
- Search endpoint design patterns
- Pagination strategies for search results
- Filter parameter conventions
- API versioning considerations for search

## Integration with Data Persistence

See [Data Persistence facet](../../facets/data-persistence/) for:
- Database indexing strategies for search
- PostgreSQL full-text search configuration
- Transactional considerations when updating search indexes
