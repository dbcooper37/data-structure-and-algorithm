# System Design Interview Guide - NAVER Scale (11-20)

> **Mục tiêu**: Tài liệu này không chỉ cung cấp solutions, mà giúp bạn **TƯ DUY** như một System Design expert.  
> **Cách sử dụng**: Với mỗi câu hỏi, hãy thử tự thiết kế TRƯỚC khi đọc solution.

---

## Mục Lục

| # | System | Độ khó | Core Concepts |
|---|--------|--------|---------------|
| 11 | [Autocomplete](#11-autocomplete-system) | ⭐⭐⭐ | Trie, Caching, Ranking |
| 12 | [Payment Processing](#12-payment-processing) | ⭐⭐⭐⭐⭐ | ACID, Idempotency, Saga |
| 13 | [Distributed Cache](#13-distributed-cache) | ⭐⭐⭐⭐ | Consistent Hashing, Eviction |
| 14 | [Rate Limiter](#14-rate-limiter) | ⭐⭐⭐ | Token Bucket, Sliding Window |
| 15 | [Video Transcoding](#15-video-transcoding) | ⭐⭐⭐⭐ | Queue, Workers, HLS |
| 16 | [Collaborative Editing](#16-collaborative-editing) | ⭐⭐⭐⭐⭐ | OT, CRDT, Conflict Resolution |
| 17 | [Commenting System](#17-commenting-system) | ⭐⭐⭐ | Fan-out, Moderation, Threading |
| 18 | [Location-Based Service](#18-location-based-service) | ⭐⭐⭐⭐ | Geohash, Spatial Index |
| 19 | [Ad Serving](#19-ad-serving) | ⭐⭐⭐⭐⭐ | RTB, Targeting, Fraud |
| 20 | [ML Model Serving](#20-ml-model-serving) | ⭐⭐⭐⭐ | A/B Testing, Feature Store |

---

# Cách Đọc Sâu (Deep Reading Playbook)

> Mục tiêu của phần này: biến việc “đọc tài liệu” thành **quy trình ra quyết định** (decision-making), không phải đọc thuộc kiến trúc.

## 1) 1 trang giấy cho mỗi system (bắt buộc)

Khi đọc bất kỳ câu nào (11–20), bạn luôn trả lời được 7 câu sau (viết ngắn, 1–2 dòng/câu):

1. **SLO/Success metric**: cái gì là “đạt”? (p99 latency, availability, correctness)
2. **Scale**: QPS/TPS peak? data size? concurrency?
3. **Hot path**: request đi qua 3–6 bước nào trên critical path?
4. **State**: state nằm ở đâu? (DB, cache, log, client) và state nào là source-of-truth?
5. **Invariants**: điều gì tuyệt đối không được sai? (idempotency, ordering, dedupe, money never disappears…)
6. **Trade-offs**: 2–3 lựa chọn chính và vì sao chọn cái này (consistency vs latency, sync vs async, precompute vs compute-on-read)
7. **Failures**: 3 failure modes quan trọng nhất + degrade/mitigation

> Quy tắc: Nếu bạn không viết được “1 trang giấy” → bạn đang đọc theo kiểu tham khảo, chưa đọc sâu.

## 2) Checklist đọc sâu theo Phase (đọc là làm)

### Phase 1 (Requirements)
- Có phân biệt **FR** vs **NFR** chưa?
- Có hỏi đúng câu “giết hệ thống” chưa? (latency budget, consistency level, burst/offline/multi-region)

### Phase 2 (Capacity)
- Có ước lượng **peak** (không chỉ average) chưa?
- Có rút ra hệ quả kiến trúc từ số liệu chưa? (cần cache? cần async? cần sharding?)

### Phase 3 (High-level)
- Có nói rõ **điểm đặt trách nhiệm** của từng box chưa (vì sao box tồn tại)?
- Có đường đi request end-to-end (hot path) chưa?

### Phase 4 (Deep dive)
- Deep dive đúng **bottleneck chính** chưa? (đừng dive vào thứ không quyết định SLO)
- Có nói rõ **data structure / algorithm / consistency** liên quan chưa?

### Phase 5 (Scaling/Failure/Obs)
- Có nêu **hot partition**, **retry storm**, **cache stampede**, **regional outage** chưa?
- Có metrics chứng minh đạt SLO chưa (p95/p99, error budget, lag, hit rate)?

## 3) Bài tập “đọc sâu” (làm 10–15 phút/câu)

Sau khi đọc xong 1 câu, làm 3 bài này:

1) **Vẽ lại kiến trúc từ trí nhớ** (không nhìn tài liệu) trong 5 phút.

2) **Nêu 3 trade-offs** (mỗi trade-off 2 phương án, vì sao chọn).

3) **Game Day mini**: giả lập 2 sự cố và trả lời:
- Redis/DB down thì degrade thế nào?
- Một key/doc/content “nóng” đột biến thì xử lý thế nào?

## 4) Ví dụ walkthrough siêu ngắn (Rate Limiter)

- **SLO**: limiter overhead <1ms; không vượt quota; 429 có Retry-After
- **Hot path**: gateway → Lua EVAL Redis → allow/deny
- **Invariant**: atomic update (không race)
- **Trade-off**: Sliding Window Log (accurate) vs Counter (cheaper)
- **Failures**: Redis timeout → fail-open/closed theo endpoint risk
- **Metrics**: blocked_total, redis_latency p99, failopen_total

Nếu bạn đọc mỗi câu theo đúng khung này, cảm giác “chưa sâu” sẽ giảm rất nhanh.

---

# 11. Autocomplete System

> **Ví dụ thực tế**: NAVER Search, Google Search suggestions  
> **Thời gian phỏng vấn**: 45 phút

## 🎯 Phase 1: Understand the Problem (5 phút)

### Clarifying Questions - Những câu hỏi BẮT BUỘC phải hỏi

| Câu hỏi | Tại sao quan trọng | Giả định |
|---------|-------------------|----------|
| "Có bao nhiêu users và queries/ngày?" | Xác định scale → ảnh hưởng architecture | 100M users, 1B queries/day |
| "Latency requirement?" | Real-time cần <100ms, ảnh hưởng caching strategy | p99 < 50ms |
| "Suggestions cần personalized không?" | Nếu có → cần store user history, phức tạp hơn | Có |
| "Hỗ trợ ngôn ngữ nào?" | Ảnh hưởng text processing (CJK phức tạp hơn Latin) | Korean, English, Japanese |
| "Cần handle typos không?" | Edit distance, fuzzy matching | Có nhưng không priority |

### Functional Requirements
- **FR1**: Khi user gõ, show top 10 suggestions
- **FR2**: Suggestions ranked by popularity + personalization
- **FR3**: Hỗ trợ trending queries (real-time)
- **FR4**: Multi-language support

### Non-Functional Requirements
- **NFR1**: p99 latency < 50ms (user expectation)
- **NFR2**: 99.99% availability 
- **NFR3**: Eventually consistent (ok nếu suggestions hơi outdated)

> 💡 **Interview Tip**: Luôn clarify xong requirements TRƯỚC khi vẽ architecture. Interviewers đánh giá cao việc bạn hỏi đúng câu hỏi.

---

## 📊 Phase 2: Capacity Estimation (5 phút)

### Traffic Estimation

```
Daily Active Users (DAU): 100M
Queries per user per day: 10
Total queries/day: 100M × 10 = 1 Billion

QPS = 1B / 86,400 ≈ 11,600 QPS
Peak QPS = 11,600 × 3 ≈ 35,000 QPS (peak hours)
```

### Storage Estimation

```
Số unique queries cần lưu: 100M (estimated)
Average query length: 20 characters × 2 bytes (UTF-8 avg) = 40 bytes
Metadata per query: 20 bytes (frequency, timestamp, etc.)

Storage for queries = 100M × 60 bytes = 6GB

User search history (for personalization):
- 100M users × 100 recent searches × 40 bytes = 400GB
```

### Bandwidth

```
Request size: ~100 bytes (query + metadata)
Response size: 10 suggestions × 50 chars = 500 bytes

Incoming: 35,000 × 100 bytes = 3.5 MB/s
Outgoing: 35,000 × 500 bytes = 17.5 MB/s
```

### 📐 Detailed Capacity Formulas

```python
# Capacity Estimation Calculator

class AutocompleteCapacityEstimator:
    """
    Công thức tính capacity cho Autocomplete System.
    Sử dụng trong interview để show structured thinking.
    """
    
    def __init__(self):
        # Input parameters
        self.dau = 100_000_000           # Daily Active Users
        self.queries_per_user = 10       # Searches per user per day
        self.peak_factor = 3             # Peak vs average ratio
        self.cache_hit_rate = 0.80       # CDN + Redis hit rate
        self.replication_factor = 3      # Data replication
        self.retention_days = 365        # History retention
        
    def calculate_qps(self):
        """
        QPS Calculation
        ===============
        Base: (DAU × queries_per_user) / seconds_per_day
        Peak: Base × peak_factor
        After cache: Peak × (1 - cache_hit_rate)
        """
        seconds_per_day = 86_400
        
        base_qps = (self.dau * self.queries_per_user) / seconds_per_day
        peak_qps = base_qps * self.peak_factor
        backend_qps = peak_qps * (1 - self.cache_hit_rate)
        
        return {
            'base_qps': int(base_qps),           # ~11,600
            'peak_qps': int(peak_qps),           # ~35,000
            'backend_qps': int(backend_qps),     # ~7,000 (sau cache)
        }
    
    def calculate_storage(self):
        """
        Storage Breakdown
        =================
        1. Query corpus: unique queries × avg size
        2. User history: users × history_size × query_size
        3. Trie structure: ~10x raw query size (với pointers)
        4. Indexes: ~20% của data size
        """
        unique_queries = 100_000_000
        avg_query_bytes = 40              # 20 chars × 2 bytes UTF-8
        metadata_bytes = 60               # frequency, language, timestamp
        
        # Base storage
        query_corpus = unique_queries * (avg_query_bytes + metadata_bytes)
        
        # User history
        users = self.dau
        history_per_user = 100
        user_history = users * history_per_user * avg_query_bytes
        
        # Trie overhead (pointers, node metadata)
        trie_multiplier = 10
        trie_storage = unique_queries * avg_query_bytes * trie_multiplier
        
        # Total with replication
        total_raw = query_corpus + user_history + trie_storage
        total_replicated = total_raw * self.replication_factor
        
        return {
            'query_corpus_gb': query_corpus / (1024**3),     # ~10GB
            'user_history_gb': user_history / (1024**3),     # ~400GB
            'trie_storage_gb': trie_storage / (1024**3),     # ~40GB
            'total_raw_gb': total_raw / (1024**3),           # ~450GB
            'total_replicated_gb': total_replicated / (1024**3), # ~1.35TB
        }
    
    def calculate_memory(self):
        """
        Memory Requirements
        ===================
        Hot data cần fit in RAM:
        - Top 10M queries (hot): 10M × 100 bytes = 1GB
        - Trie nodes: ~40GB (đã tính ở trên)
        - User sessions: 1M concurrent × 1KB = 1GB
        """
        hot_queries = 10_000_000
        bytes_per_query = 100
        hot_data = hot_queries * bytes_per_query
        
        concurrent_users = 1_000_000
        session_size = 1024  # 1KB per session
        session_memory = concurrent_users * session_size
        
        trie_memory = 40 * (1024**3)  # 40GB for trie
        
        total_memory = hot_data + session_memory + trie_memory
        
        return {
            'hot_data_gb': hot_data / (1024**3),
            'session_memory_gb': session_memory / (1024**3),
            'trie_memory_gb': trie_memory / (1024**3),
            'total_memory_gb': total_memory / (1024**3),
            'redis_nodes_needed': int(total_memory / (64 * 1024**3)) + 1,  # 64GB per node
        }
    
    def calculate_bandwidth(self):
        """
        Network Bandwidth
        =================
        Ingress: QPS × request_size
        Egress: QPS × response_size
        Internal: Replication traffic between nodes
        """
        peak_qps = 35_000
        request_size = 100     # bytes
        response_size = 500    # 10 suggestions × 50 chars
        
        ingress_mbps = (peak_qps * request_size * 8) / (1024 * 1024)
        egress_mbps = (peak_qps * response_size * 8) / (1024 * 1024)
        
        # Internal replication: 10% of write traffic × replication_factor
        write_ratio = 0.01  # 1% writes
        internal_mbps = egress_mbps * write_ratio * self.replication_factor
        
        return {
            'ingress_mbps': ingress_mbps,      # ~27 Mbps
            'egress_mbps': egress_mbps,        # ~134 Mbps
            'internal_mbps': internal_mbps,    # ~4 Mbps
            'total_mbps': ingress_mbps + egress_mbps + internal_mbps,
        }

# Usage in interview:
estimator = AutocompleteCapacityEstimator()
print("QPS:", estimator.calculate_qps())
print("Storage:", estimator.calculate_storage())
print("Memory:", estimator.calculate_memory())
print("Bandwidth:", estimator.calculate_bandwidth())
```

### Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| QPS | 35K peak | Cần distributed system |
| Storage | ~500GB | Fits in memory cluster |
| Bandwidth | 20 MB/s | Not a bottleneck |
| Latency | <50ms | Cần heavy caching |

### 🗄️ Database Schema

```sql
-- =====================================================
-- AUTOCOMPLETE SYSTEM DATABASE SCHEMA
-- =====================================================

-- 1. Query Statistics Table (source of truth)
CREATE TABLE query_stats (
    id BIGSERIAL PRIMARY KEY,
    query_text VARCHAR(500) NOT NULL,
    query_hash CHAR(32) NOT NULL,           -- MD5 for deduplication
    language VARCHAR(10) NOT NULL DEFAULT 'ko',
    frequency BIGINT NOT NULL DEFAULT 1,
    daily_frequency INT NOT NULL DEFAULT 0,  -- For trending
    last_searched_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Index for prefix search fallback (when Redis unavailable)
    -- Sử dụng text_pattern_ops cho LIKE 'prefix%' queries
    CONSTRAINT uq_query_hash UNIQUE (query_hash)
);

-- Indexes cho query_stats
CREATE INDEX idx_query_prefix ON query_stats 
    USING btree (query_text varchar_pattern_ops);
CREATE INDEX idx_query_frequency ON query_stats (frequency DESC);
CREATE INDEX idx_query_daily ON query_stats (language, daily_frequency DESC);
CREATE INDEX idx_query_updated ON query_stats (updated_at);

-- Partial index cho top queries (most queried)
CREATE INDEX idx_top_queries ON query_stats (frequency DESC) 
    WHERE frequency > 1000;


-- 2. User Search History (for personalization)
CREATE TABLE user_search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    query_text VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,
    clicked_position INT,                    -- Which suggestion was clicked (0-9)
    search_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    device_type VARCHAR(20),                 -- mobile/desktop/tablet
    location_country CHAR(2),                -- ISO country code
    
    -- Partition by month for efficient cleanup
    CONSTRAINT pk_user_history PRIMARY KEY (id, search_timestamp)
) PARTITION BY RANGE (search_timestamp);

-- Create partitions for each month
CREATE TABLE user_search_history_2024_01 
    PARTITION OF user_search_history 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- ... more partitions

-- Indexes cho user history
CREATE INDEX idx_user_history_user ON user_search_history (user_id, search_timestamp DESC);
CREATE INDEX idx_user_history_query ON user_search_history (user_id, query_text);


-- 3. Trending Queries (materialized, updated every hour)
CREATE TABLE trending_queries (
    id SERIAL PRIMARY KEY,
    query_text VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,
    trend_score FLOAT NOT NULL,              -- Calculated score
    hour_bucket TIMESTAMP NOT NULL,          -- Which hour this belongs to
    query_count INT NOT NULL,                -- Raw count for this hour
    velocity FLOAT,                          -- Rate of increase
    
    CONSTRAINT uq_trending UNIQUE (query_text, language, hour_bucket)
);

CREATE INDEX idx_trending_score ON trending_queries (language, hour_bucket, trend_score DESC);


-- 4. Blocked/Offensive Terms (for filtering)
CREATE TABLE blocked_terms (
    id SERIAL PRIMARY KEY,
    term VARCHAR(200) NOT NULL,
    language VARCHAR(10) NOT NULL,
    block_type VARCHAR(20) NOT NULL,         -- 'exact', 'contains', 'regex'
    reason VARCHAR(500),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT uq_blocked_term UNIQUE (term, language)
);

CREATE INDEX idx_blocked_terms ON blocked_terms (language, term);
```

### 🔄 Sequence Diagram - Request Flow

```
┌──────┐          ┌─────┐          ┌───────────┐          ┌───────┐          ┌────────┐
│Client│          │ CDN │          │API Gateway│          │Service│          │  Redis │
└──┬───┘          └──┬──┘          └─────┬─────┘          └───┬───┘          └───┬────┘
   │                 │                    │                    │                  │
   │ GET /auto?q=nav │                    │                    │                  │
   │────────────────>│                    │                    │                  │
   │                 │                    │                    │                  │
   │                 │ Cache check        │                    │                  │
   │                 │ (prefix: "nav")    │                    │                  │
   │                 │                    │                    │                  │
   ├─────────────────┼─ [CACHE HIT] ─────>│                    │                  │
   │                 │                    │                    │                  │
   │<────────────────┼────────────────────┤                    │                  │
   │ 200 OK [cached] │                    │                    │                  │
   │                 │                    │                    │                  │
   ├─────────────────┼─ [CACHE MISS] ────>│                    │                  │
   │                 │                    │                    │                  │
   │                 │                    │ Rate limit check   │                  │
   │                 │                    │───────────────────>│                  │
   │                 │                    │                    │                  │
   │                 │                    │<───────────────────│ OK               │
   │                 │                    │                    │                  │
   │                 │                    │ Forward request    │                  │
   │                 │                    │───────────────────>│                  │
   │                 │                    │                    │                  │
   │                 │                    │                    │ GET autocomplete:│
   │                 │                    │                    │ ko:nav          │
   │                 │                    │                    │─────────────────>│
   │                 │                    │                    │                  │
   │                 │                    │                    │<─────────────────│
   │                 │                    │                    │ [suggestions]    │
   │                 │                    │                    │                  │
   │                 │                    │                    │ GET trending:ko  │
   │                 │                    │                    │─────────────────>│
   │                 │                    │                    │                  │
   │                 │                    │                    │<─────────────────│
   │                 │                    │                    │ [trending]       │
   │                 │                    │                    │                  │
   │                 │                    │                    │ GET user:123:    │
   │                 │                    │                    │ history         │
   │                 │                    │                    │─────────────────>│
   │                 │                    │                    │                  │
   │                 │                    │                    │<─────────────────│
   │                 │                    │                    │ [personalized]   │
   │                 │                    │                    │                  │
   │                 │                    │                    │ Merge & Rank     │
   │                 │                    │                    │ ┌──────────────┐ │
   │                 │                    │                    │ │ 1.personal[0]│ │
   │                 │                    │                    │ │ 2.personal[1]│ │
   │                 │                    │                    │ │ 3.base[0-4]  │ │
   │                 │                    │                    │ │ 4.trending[0]│ │
   │                 │                    │                    │ └──────────────┘ │
   │                 │                    │                    │                  │
   │                 │                    │<───────────────────│ Response         │
   │                 │                    │                    │                  │
   │                 │ Cache response     │                    │                  │
   │                 │<───────────────────│                    │                  │
   │                 │ TTL: 5 min         │                    │                  │
   │                 │                    │                    │                  │
   │<────────────────│                    │                    │                  │
   │ 200 OK          │                    │                    │                  │
   │ [suggestions]   │                    │                    │                  │
```

### ⚠️ Failure Scenarios & Handling

| Failure | Impact | Detection | Mitigation |
|---------|--------|-----------|------------|
| **Redis Down** | No suggestions | Health check fails | Fallback to PostgreSQL LIKE query |
| **Trie Corruption** | Wrong/no suggestions | Checksum mismatch | Rebuild from DB, alert oncall |
| **CDN Outage** | All traffic hits origin | CDN health endpoint | DNS failover to backup CDN |
| **Hot Partition** | One shard overloaded | CPU/latency spike | Replicate hot keys to all nodes |
| **Trending Spike** | Celebrity/news event | QPS anomaly | Auto-scale, rate limit heavy users |

```python
class AutocompleteServiceWithFallback:
    """
    Production-grade service với multiple fallbacks.
    """
    
    def __init__(self):
        self.redis_primary = redis.Redis(host='redis-primary')
        self.redis_replica = redis.Redis(host='redis-replica')
        self.db = PostgresPool()
        self.local_cache = TTLCache(maxsize=10000, ttl=60)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
    
    async def get_suggestions(self, prefix: str, user_id: str) -> List[str]:
        """
        Fallback chain:
        1. Local cache (in-memory)
        2. Redis primary
        3. Redis replica (read-only)
        4. PostgreSQL (degraded mode)
        5. Static popular queries (emergency)
        """
        
        # Level 1: Local cache
        cache_key = f"{prefix}:{user_id}"
        if cache_key in self.local_cache:
            metrics.incr("autocomplete.cache.local_hit")
            return self.local_cache[cache_key]
        
        # Level 2: Redis with circuit breaker
        if self.circuit_breaker.is_closed():
            try:
                result = await self._query_redis(prefix, user_id)
                self.local_cache[cache_key] = result
                return result
            except RedisError as e:
                self.circuit_breaker.record_failure()
                logger.error(f"Redis error: {e}")
        
        # Level 3: PostgreSQL fallback
        try:
            result = await self._query_postgres(prefix)
            metrics.incr("autocomplete.fallback.postgres")
            return result
        except Exception as e:
            logger.error(f"PostgreSQL error: {e}")
        
        # Level 4: Static fallback
        metrics.incr("autocomplete.fallback.static")
        return self._get_static_suggestions(prefix)
    
    async def _query_redis(self, prefix: str, user_id: str) -> List[str]:
        """Query Redis with timeout."""
        async with timeout(50):  # 50ms timeout
            base = await self.redis_primary.zrevrange(
                f"autocomplete:{prefix}", 0, 9
            )
            return base
    
    async def _query_postgres(self, prefix: str) -> List[str]:
        """Fallback to PostgreSQL - slower but reliable."""
        query = """
            SELECT query_text 
            FROM query_stats 
            WHERE query_text LIKE $1 
            ORDER BY frequency DESC 
            LIMIT 10
        """
        rows = await self.db.fetch(query, f"{prefix}%")
        return [row['query_text'] for row in rows]
    
    def _get_static_suggestions(self, prefix: str) -> List[str]:
        """Emergency fallback - hardcoded popular queries."""
        popular = [
            "naver", "naver map", "naver news", 
            "naver webtoon", "naver shopping"
        ]
        return [q for q in popular if q.startswith(prefix)][:10]
```

### 🌍 Real-World Case Study: Google Search Autocomplete

| Aspect | Google's Approach | Learning |
|--------|-------------------|----------|
| **Scale** | 8.5B searches/day | Need extreme caching |
| **Latency** | <100ms global | Edge servers in 200+ locations |
| **Personalization** | Based on search history, location, trending | Balance privacy vs relevance |
| **Offensive filtering** | ML + human review | Can't rely on blocklist alone |
| **Trending** | Real-time với streaming | Kafka/Flink for freshness |

**Key Takeaways:**
1. **Cache at every layer** - CDN, regional, local
2. **Precompute when possible** - Don't compute rankings on every request
3. **Degrade gracefully** - Always have a fallback
4. **Monitor everything** - Latency percentiles, cache hit rates, error rates

> 💡 **Interview Tip**: Không cần tính chính xác 100%. Interviewers muốn thấy bạn có thể estimate reasonable numbers và understand implications.

---

## 🏗️ Phase 3: High-Level Design (10 phút)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│              (Web Browser, Mobile App, API)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CDN / EDGE CACHE                              │
│   • Cache popular prefixes ("nav", "naver", "네이버")            │
│   • 80% hit rate → Giảm load xuống 7K QPS                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Cache miss
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY                                   │
│   • Rate limiting (per user/IP)                                  │
│   • Authentication                                               │
│   • Request routing                                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                AUTOCOMPLETE SERVICE CLUSTER                      │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐                  │
│   │  Service   │ │  Service   │ │  Service   │  (Stateless)     │
│   │  Instance  │ │  Instance  │ │  Instance  │                  │
│   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘                  │
│         │              │              │                          │
│         └──────────────┼──────────────┘                          │
│                        │                                         │
└────────────────────────┼────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   TRIE       │ │  TRENDING    │ │ PERSONALIZE  │
│   SERVICE    │ │  SERVICE     │ │ SERVICE      │
│              │ │              │ │              │
│ • In-memory  │ │ • Streaming  │ │ • ML ranking │
│   Trie       │ │   from Kafka │ │ • User prefs │
│ • Top-K per  │ │ • Sliding    │ │              │
│   prefix     │ │   window     │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │   Redis     │  │   Kafka     │  │  PostgreSQL │               │
│  │   Cluster   │  │   (Events)  │  │  (Source)   │               │
│  │             │  │             │  │             │               │
│  │ • Trie data │  │ • Query     │  │ • Query     │               │
│  │ • User hist │  │   logs      │  │   stats     │               │
│  │ • Trending  │  │ • Click     │  │ • User data │               │
│  └─────────────┘  │   events    │  └─────────────┘               │
│                   └─────────────┘                                 │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Why this design? |
|-----------|---------------|------------------|
| **CDN Edge** | Cache top prefixes | 80% queries là popular → giảm 80% load |
| **API Gateway** | Rate limit, auth | Protect backend từ abuse |
| **Autocomplete Service** | Merge results | Stateless → easy scale |
| **Trie Service** | Prefix matching | O(k) lookup, k = prefix length |
| **Trending Service** | Real-time hot queries | Streaming cho freshness |
| **Personalization** | User-specific ranking | Tăng relevance |

### Data Flow

```
1. User types "nav" 
   → CDN cache check (HIT? return immediately)
   
2. Cache MISS → API Gateway 
   → Rate limit check → Auth

3. Autocomplete Service receives request
   → Parallel calls to:
     a) Trie Service: Get top 20 by frequency for "nav"
     b) Trending Service: Get top 5 trending starting with "nav"
     c) Personalization: Get user's recent "nav*" searches

4. Merge results:
   - 2 personalized (highest priority)
   - 5 from trie (popular)
   - 3 trending
   → Deduplicate → Return top 10

5. Log query to Kafka for analytics
```

> 💡 **Interview Tip**: Giải thích TẠI SAO mỗi component tồn tại. Đừng chỉ vẽ diagram mà không giải thích reasoning.

---

## 🔬 Phase 4: Deep Dive (15 phút)

### 4.1 Trie Data Structure - Tại sao chọn Trie?

**So sánh alternatives:**

| Approach | Time Complexity | Space | Pros | Cons |
|----------|----------------|-------|------|------|
| **Trie** | O(k) lookup | O(n×m) | Fast prefix, easy suggestions | Memory heavy |
| **Hash Table** | O(1) exact | O(n) | Simple | No prefix support |
| **B-Tree / DB Index** | O(log n) | Disk | Persistent | Slower than memory |
| **Elasticsearch** | O(log n) | Varies | Full-text, fuzzy | Complex, slower |

**Quyết định**: Dùng **Trie in Redis** vì:
- Prefix lookup O(k) - đủ nhanh cho <50ms
- Fit in memory (6GB data)
- Redis Sorted Set hỗ trợ ranking tự nhiên

**Trie với Caching tại mỗi node:**

```python
class TrieNode:
    """
    Mỗi node cache top-10 suggestions để tránh DFS mỗi query.
    Trade-off: Memory tăng 10x nhưng lookup O(k) thay vì O(n).
    
    Memory: 100M queries × 10 suggestions × 40 bytes = 40GB
    → Chấp nhận được cho Redis Cluster
    """
    def __init__(self):
        self.children = {}          # char -> TrieNode
        self.is_end = False
        self.frequency = 0
        self.top_suggestions = []   # Cached top 10 for this prefix
        
class Trie:
    def search(self, prefix: str) -> List[str]:
        """
        O(k) complexity - chỉ traverse k characters
        Không cần DFS nhờ cached suggestions
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []  # No matches
            node = node.children[char]
        
        # Return cached suggestions - O(1)
        return node.top_suggestions[:10]
```

### 4.2 Ranking Algorithm

**Scoring Formula:**

```
score = α × popularity + β × recency + γ × personalization

Trong đó:
- popularity = log(query_count + 1)  # Log để giảm bias cho super popular
- recency = exp(-λ × hours_ago)       # Decay function
- personalization = user_affinity     # ML model score

Weights (tunable):
- α = 0.5 (popularity quan trọng nhất)
- β = 0.3 (recency cho trending)
- γ = 0.2 (personalization)
```

**Tại sao dùng log cho popularity?**
- Tránh "winner takes all" - query có 1B searches không nên dominant hoàn toàn
- Google Search cũng dùng logarithmic scaling

### 4.3 Caching Strategy

**Multi-layer caching:**

```
┌────────────────────────────────────────────────────┐
│ Layer 1: CDN Edge Cache                            │
│ TTL: 5 minutes                                     │
│ Keys: Popular prefixes (top 10K)                   │
│ Hit rate: ~80%                                     │
│ WHY: Giảm latency từ 50ms → 5ms cho 80% requests  │
└────────────────────────────────────────────────────┘
                        │
                        ▼ Miss
┌────────────────────────────────────────────────────┐
│ Layer 2: Application Cache (Local)                 │
│ TTL: 1 minute                                      │
│ Keys: Recent queries on this instance              │
│ Hit rate: ~50% của remaining                       │
│ WHY: Avoid network hop to Redis                    │
└────────────────────────────────────────────────────┘
                        │
                        ▼ Miss
┌────────────────────────────────────────────────────┐
│ Layer 3: Redis Cluster                             │
│ TTL: 10 minutes                                    │
│ Keys: All prefixes với suggestions                 │
│ WHY: Shared cache across instances                 │
└────────────────────────────────────────────────────┘
```

**Cache Invalidation Strategy:**

| Trigger | Action | Reason |
|---------|--------|--------|
| New trending query | Invalidate related prefixes | Freshness |
| Hourly batch job | Rebuild top-K per prefix | Accuracy |
| User action | Invalidate user cache only | Personalization |

### 4.4 Handling Korean/CJK Characters

**Vấn đề đặc biệt:**
- Korean: "한글" có thể được gõ partial "ㅎ" hoặc "하"
- Japanese: Hiragana/Katakana conversion

```python
def normalize_korean(text: str) -> List[str]:
    """
    Decompose Hangul để match partial typing.
    
    Example: "한" → ["ㅎ", "ㅏ", "ㄴ"]
    
    Điều này cho phép match khi user mới gõ "ㅎ"
    """
    result = []
    for char in text:
        if is_hangul_syllable(char):
            # Unicode decomposition
            initial, vowel, final = decompose_hangul(char)
            result.extend([initial, vowel, final])
        else:
            result.append(char)
    return result

# Trie cần index cả:
# - Full syllable: "한글"  
# - Decomposed: "ㅎㅏㄴㄱㅡㄹ"
```

---

## 📈 Phase 5: Scaling & Bottlenecks (5 phút)

### Bottleneck Analysis

| Scale | Bottleneck | Solution |
|-------|-----------|----------|
| **10K QPS** | Single server | Add caching layer |
| **100K QPS** | Redis single instance | Redis Cluster (sharding) |
| **1M QPS** | CPU for ranking | Pre-compute rankings |
| **10M QPS** | Network bandwidth | Edge caching, CDN |

### Scaling Strategies

**1. Horizontal Scaling:**
```
Autocomplete Service: Stateless → just add more instances
Load Balancer: Round-robin (no sticky sessions needed)
```

**2. Data Sharding:**
```
Shard by first character of prefix:
- Shard A: a-f
- Shard B: g-m  
- Shard C: n-t
- Shard D: u-z

Korean: Shard by first jamo (ㄱ-ㅎ)
```

**3. Geographic Distribution:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Seoul DC   │     │   Tokyo DC   │     │   US-West DC │
│              │     │              │     │              │
│ • Korean     │     │ • Japanese   │     │ • English    │
│   queries    │     │   queries    │     │   queries    │
│ • Primary    │     │ • Primary    │     │ • Primary    │
│   for KR     │     │   for JP     │     │   for US     │
└──────────────┘     └──────────────┘     └──────────────┘
      ↑                     ↑                    ↑
      └─────── Async replication ────────────────┘
```

### Failure Scenarios

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Redis down | No suggestions | Fallback to DB (degraded) |
| Trending service down | Stale trending | Use cached trending |
| One DC down | Regional outage | Route to nearest DC |
| Trie corruption | Wrong suggestions | Rebuild from DB |

---

## 💡 Phase 6: Interview Tips

### Common Follow-up Questions

1. **"What if a celebrity tweets and suddenly million people search the same thing?"**
   - Hot partition problem
   - Solution: Replicate hot keys to multiple shards

2. **"How do you prevent showing offensive suggestions?"**
   - Blocklist filtering
   - ML-based content moderation
   - Human review for borderline cases

3. **"How do you A/B test ranking algorithms?"**
   - Split traffic by user_id hash
   - Measure CTR, search success rate
   - Gradual rollout (1% → 10% → 50% → 100%)

4. **"Làm sao handle typos?"**
   - Edit distance (Levenshtein)
   - Phonetic matching (Soundex)
   - ML-based correction

### Red Flags - Những điều TRÁNH nói

❌ "Just use Elasticsearch" - Quá generic, không show understanding  
❌ "Cache everything" - Không discuss invalidation  
❌ "Use NoSQL" - Không giải thích tại sao  
❌ Vẽ quá nhiều chi tiết từ đầu - Nên high-level trước  

### Điều Interviewers thích thấy

✅ Trade-off analysis với reasoning  
✅ Back-of-envelope calculations  
✅ Proactive về failures và edge cases  
✅ Biết khi nào đủ chi tiết và move on  

---

# 12. Payment Processing System

> **Ví dụ thực tế**: NAVER Pay, Kakao Pay, Stripe  
> **Thời gian phỏng vấn**: 45 phút  
> **Độ khó**: ⭐⭐⭐⭐⭐ (Highest - vì liên quan đến tiền)

## 🎯 Phase 1: Understand the Problem (5 phút)

### Clarifying Questions - Critical cho Payment

| Câu hỏi | Tại sao CRITICAL | Giả định |
|---------|-----------------|----------|
| "Loại payment nào? Online/Offline/P2P?" | Mỗi loại có flow khác nhau hoàn toàn | Online payments |
| "Cần support những payment methods nào?" | Credit card, bank transfer có latency khác nhau | Cards, Bank, Wallet |
| "Consistency requirement?" | **Payment KHÔNG THỂ eventually consistent** | Strong consistency |
| "Có cần support multi-currency?" | Ảnh hưởng đến precision, FX rates | Có |
| "Compliance requirements?" | PCI-DSS là bắt buộc cho credit cards | PCI-DSS Level 1 |

### Functional Requirements
- **FR1**: Process payments (authorize → capture → settle)
- **FR2**: Support refunds (full and partial)
- **FR3**: Multi-currency support
- **FR4**: Payment history và reporting

### Non-Functional Requirements  
- **NFR1**: **99.999% availability** (5 minutes downtime/year)
- **NFR2**: **Exactly-once processing** - CỰC KỲ quan trọng
- **NFR3**: **Strong consistency** - không thể mất transaction
- **NFR4**: **PCI-DSS compliant** - credit card data handling

> ⚠️ **Critical Point**: Payment khác với các system khác - KHÔNG CÓ CHỖ CHO TRADE-OFF về consistency. Mất tiền = mất user.

---

## 📊 Phase 2: Capacity Estimation (3 phút)

### Traffic

```
Daily transactions: 100M
Peak TPS = 100M / 86400 × 5 (peak factor) ≈ 5,800 TPS

Mỗi transaction có:
- 1 Authorization request
- 1 Capture request  
- 0.05 Refund requests (5% refund rate)

Total API calls = 5,800 × 2.05 ≈ 12,000 TPS peak
```

### Storage

```
Transaction record size: ~1KB
- transaction_id, user_id, merchant_id, amount, currency
- status, timestamps, metadata

Daily: 100M × 1KB = 100GB/day
Yearly: 100GB × 365 = 36.5TB/year

Cần giữ 7 years cho compliance → 250TB
```

### Money Values

```
Use DECIMAL(19, 4) - KHÔNG BAO GIỜ dùng FLOAT
- 19 digits total
- 4 decimal places
- Reason: 0.1 + 0.2 ≠ 0.3 trong floating point!
```

---

## 🏗️ Phase 3: High-Level Design (10 phút)

### Payment Flow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PAYMENT FLOW                                  │
│                                                                      │
│  ┌──────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │ User │───▶│ Merchant │───▶│  NAVER   │───▶│  Card Network    │   │
│  │      │◀───│   App    │◀───│   Pay    │◀───│  (Visa/Master)   │   │
│  └──────┘    └──────────┘    └──────────┘    └──────────────────┘   │
│                                    │                                 │
│                                    ▼                                 │
│                            ┌──────────────┐                         │
│                            │    Bank      │                         │
│                            │   (Issuer)   │                         │
│                            └──────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│   Mobile App ─────┬───── Web App ─────┬───── Merchant API           │
└───────────────────┼───────────────────┼─────────────────────────────┘
                    │                   │
                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                   │
│   • Rate Limiting (per merchant)                                     │
│   • Authentication (API Key + HMAC signature)                        │
│   • Request logging (audit trail)                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PAYMENT ORCHESTRATOR                              │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                  IDEMPOTENCY CHECK                           │   │
│   │   • Check idempotency_key in Redis                          │   │
│   │   • If exists → return cached result                        │   │
│   │   • If not → proceed and store result                       │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   ┌────────────┬─────────────┼─────────────┬────────────┐           │
│   ▼            ▼             ▼             ▼            ▼           │
│ ┌──────┐  ┌────────┐   ┌──────────┐  ┌────────┐  ┌──────────┐      │
│ │Fraud │  │Currency│   │  LEDGER  │  │Payment │  │Notifi-   │      │
│ │Check │  │Convert │   │ SERVICE  │  │Provider│  │cation    │      │
│ │      │  │        │   │          │  │Router  │  │          │      │
│ └──────┘  └────────┘   └──────────┘  └────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  VISA    │        │   Bank   │        │  Other   │
    │  Master  │        │   API    │        │ Providers│
    └──────────┘        └──────────┘        └──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                    │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│   │   PostgreSQL   │  │     Redis      │  │  Event Store   │        │
│   │   (Primary)    │  │   (Idempotency)│  │  (Audit Log)   │        │
│   │                │  │                │  │                │        │
│   │ • Transactions │  │ • Idem keys    │  │ • All events   │        │
│   │ • Ledger       │  │ • Locks        │  │ • Immutable    │        │
│   │ • Users        │  │ • Cache        │  │ • Compliance   │        │
│   └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Phase 4: Deep Dive (15 phút)

### 4.1 Idempotency - Tại sao CỰC KỲ quan trọng?

**Scenario**: Network timeout sau khi submit payment
```
User click "Pay" → Request sent → Server process → Send to card network
                                                 ↓
                              ← ← ← Network timeout ← ← ←
                              
User thấy error → Click "Pay" lại → DOUBLE CHARGE! 💀
```

**Solution: Idempotency Key**

```python
@app.post("/payments")
async def create_payment(request: PaymentRequest):
    """
    Idempotency key = client-generated unique ID per payment attempt.
    
    Flow:
    1. Check Redis for existing result with this key
    2. If exists → return cached result (no double charge)
    3. If not → process and store result
    
    TTL: 24h (đủ để handle retries)
    """
    # 1. Check idempotency
    cache_key = f"idempotency:{request.idempotency_key}"
    cached = redis.get(cache_key)
    
    if cached:
        return json.loads(cached)  # Return same result
    
    # 2. Acquire distributed lock (prevent race condition)
    lock = redis.lock(f"lock:{request.idempotency_key}", timeout=30)
    
    if not lock.acquire(blocking=True, blocking_timeout=5):
        raise ConcurrentRequestError()
    
    try:
        # Double-check after lock
        cached = redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 3. Process payment
        result = await process_payment(request)
        
        # 4. Store result for idempotency
        redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
        
    finally:
        lock.release()
```

### 4.2 Double-Entry Ledger - Tại sao cần?

**Principle**: Mọi transaction đều có 2 entries: DEBIT và CREDIT
- Tổng tất cả debits = Tổng tất cả credits (luôn luôn)
- Nếu không balance → có bug hoặc fraud

```sql
-- Ledger entries table
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL,
    account_id VARCHAR(50) NOT NULL,    -- "user:123" hoặc "merchant:456"
    entry_type VARCHAR(10) NOT NULL,    -- 'DEBIT' hoặc 'CREDIT'
    amount DECIMAL(19, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Mỗi transaction PHẢI có đúng 1 DEBIT và 1 CREDIT
    CONSTRAINT valid_entry_type CHECK (entry_type IN ('DEBIT', 'CREDIT'))
);

-- Ví dụ: User A trả 100 USD cho Merchant B
-- Entry 1: DEBIT from user:A = -100 USD
-- Entry 2: CREDIT to merchant:B = +100 USD
-- Sum = 0 ✓

INSERT INTO ledger_entries (transaction_id, account_id, entry_type, amount, currency)
VALUES
    ('txn_123', 'user:A', 'DEBIT', -100.00, 'USD'),
    ('txn_123', 'merchant:B', 'CREDIT', 100.00, 'USD');
```

### 4.3 Payment State Machine

```
┌─────────┐
│ CREATED │ ─────────────────────────────────────┐
└────┬────┘                                      │
     │ submit()                                  │ timeout/cancel
     ▼                                           │
┌─────────────┐                                  │
│  PENDING    │ ────────────────────────────┐    │
└──────┬──────┘                             │    │
       │ authorize()                        │    │
       ▼                                    │    │
┌─────────────┐    decline()           ┌────▼────▼────┐
│ AUTHORIZED  │ ─────────────────────▶ │   FAILED     │
└──────┬──────┘                        └──────────────┘
       │ capture()
       ▼
┌─────────────┐    refund()     ┌─────────────┐
│  CAPTURED   │ ───────────────▶│  REFUNDED   │
└──────┬──────┘                 └─────────────┘
       │ settle()
       ▼
┌─────────────┐
│   SETTLED   │ (Final state - money transferred)
└─────────────┘
```

**Tại sao cần state machine?**
- Enforce valid transitions (không thể refund trước capture)
- Audit trail (mỗi transition được log)
- Recovery (biết chính xác state khi system crash)

### 4.4 Handling Failures - Saga Pattern

**Scenario**: User mua hàng, cần:
1. Charge payment
2. Reserve inventory
3. Create order

**Vấn đề**: Nếu step 2 fail sau step 1 succeed?

**Solution: Saga với Compensation**

```python
class PaymentSaga:
    """
    Saga = Distributed transaction với compensating actions.
    
    Mỗi step có 2 functions:
    - execute(): làm việc chính
    - compensate(): undo nếu sau đó có failure
    """
    
    async def execute(self, order_request):
        # Step 1: Charge payment
        try:
            payment_result = await self.charge_payment(order_request)
        except PaymentError as e:
            raise  # No compensation needed yet
            
        # Step 2: Reserve inventory
        try:
            inventory_result = await self.reserve_inventory(order_request)
        except InventoryError as e:
            # Compensate step 1
            await self.refund_payment(payment_result.payment_id)
            raise
            
        # Step 3: Create order
        try:
            order_result = await self.create_order(order_request)
        except OrderError as e:
            # Compensate step 2 then step 1
            await self.release_inventory(inventory_result.reservation_id)
            await self.refund_payment(payment_result.payment_id)
            raise
            
        return order_result
```

---

## 💡 Phase 6: Interview Tips

### Payment-Specific Questions

1. **"Làm sao handle partial refunds?"**
   - Track refund_amount per transaction
   - Validation: sum(refunds) <= original_amount
   - State: PARTIALLY_REFUNDED vs FULLY_REFUNDED

2. **"Currency conversion happens at which step?"**
   - At authorization time (rate locked)
   - Store both original and converted amounts
   - Show user both

3. **"PCI-DSS compliance?"**
   - Never store full card number
   - Tokenization pattern
   - Encryption at rest and in transit

### 🗄️ Complete Payment Database Schema

```sql
-- =====================================================
-- PAYMENT PROCESSING SYSTEM DATABASE SCHEMA
-- PostgreSQL with strong consistency guarantees
-- =====================================================

-- 1. Transactions (core payment records)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(64) NOT NULL UNIQUE,  -- Client-provided
    
    -- Parties
    user_id BIGINT NOT NULL,
    merchant_id BIGINT NOT NULL,
    
    -- Money (NEVER use FLOAT!)
    amount DECIMAL(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,                    -- ISO 4217: USD, KRW, JPY
    converted_amount DECIMAL(19, 4),              -- If currency conversion applied
    converted_currency CHAR(3),
    exchange_rate DECIMAL(12, 6),
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    status_reason VARCHAR(500),
    
    -- Payment method (tokenized - no raw card data)
    payment_method_type VARCHAR(20) NOT NULL,     -- card, bank_transfer, wallet
    payment_method_token VARCHAR(100) NOT NULL,   -- Reference to vault
    payment_method_last4 CHAR(4),                 -- Last 4 digits for display
    
    -- External references
    provider VARCHAR(50) NOT NULL,                -- stripe, adyen, bank_api
    provider_transaction_id VARCHAR(100),
    provider_response JSONB,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    authorized_at TIMESTAMP,
    captured_at TIMESTAMP,
    settled_at TIMESTAMP,
    failed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Metadata and audit
    request_ip INET,
    user_agent VARCHAR(500),
    device_fingerprint VARCHAR(100),
    metadata JSONB,
    
    CONSTRAINT valid_status CHECK (status IN (
        'CREATED', 'PENDING', 'AUTHORIZED', 'CAPTURED', 
        'SETTLED', 'FAILED', 'CANCELLED', 'REFUNDED', 'PARTIALLY_REFUNDED'
    ))
);

-- Critical indexes for payment queries
CREATE INDEX idx_txn_user ON transactions (user_id, created_at DESC);
CREATE INDEX idx_txn_merchant ON transactions (merchant_id, created_at DESC);
CREATE INDEX idx_txn_status ON transactions (status) WHERE status NOT IN ('SETTLED', 'FAILED');
CREATE INDEX idx_txn_provider ON transactions (provider, provider_transaction_id);
CREATE INDEX idx_txn_created ON transactions (created_at DESC);

-- Partial index for active transactions (optimization)
CREATE INDEX idx_txn_pending ON transactions (created_at) 
    WHERE status IN ('PENDING', 'AUTHORIZED', 'CAPTURED');


-- 2. Transaction Events (audit log - append only)
CREATE TABLE transaction_events (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    event_type VARCHAR(50) NOT NULL,              -- created, authorized, captured, failed, etc.
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    event_data JSONB,                             -- Additional context
    actor_type VARCHAR(20),                       -- user, system, admin, provider
    actor_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Immutable - no updates allowed
    CONSTRAINT no_update CHECK (TRUE)
);

CREATE INDEX idx_txn_events_txn ON transaction_events (transaction_id, created_at);


-- 3. Refunds
CREATE TABLE refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    idempotency_key VARCHAR(64) NOT NULL UNIQUE,
    
    amount DECIMAL(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,
    reason VARCHAR(500),
    refund_type VARCHAR(20) NOT NULL,             -- full, partial
    
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    provider_refund_id VARCHAR(100),
    
    requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,
    requested_by VARCHAR(100),                    -- user, merchant, admin
    
    CONSTRAINT valid_refund_status CHECK (status IN (
        'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
    ))
);

CREATE INDEX idx_refund_txn ON refunds (transaction_id);


-- 4. Double-Entry Ledger (accounting)
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL,
    entry_id UUID NOT NULL DEFAULT gen_random_uuid(),
    
    account_id VARCHAR(100) NOT NULL,             -- Format: "type:id" e.g. "user:123", "merchant:456"
    account_type VARCHAR(20) NOT NULL,            -- user, merchant, platform, reserve
    
    entry_type VARCHAR(10) NOT NULL,              -- DEBIT or CREDIT
    amount DECIMAL(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,
    
    balance_after DECIMAL(19, 4),                 -- Denormalized for quick lookup
    
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT valid_entry_type CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    
    -- Every transaction must balance: sum(debits) = sum(credits)
    -- This is verified by application logic and periodic reconciliation
);

CREATE INDEX idx_ledger_account ON ledger_entries (account_id, created_at DESC);
CREATE INDEX idx_ledger_txn ON ledger_entries (transaction_id);

-- Materialized view for account balances
CREATE MATERIALIZED VIEW account_balances AS
SELECT 
    account_id,
    currency,
    SUM(CASE WHEN entry_type = 'CREDIT' THEN amount ELSE -amount END) as balance,
    MAX(created_at) as last_updated
FROM ledger_entries
GROUP BY account_id, currency;

CREATE UNIQUE INDEX idx_balance_account ON account_balances (account_id, currency);


-- 5. Payment Methods (tokenized)
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    
    method_type VARCHAR(20) NOT NULL,             -- card, bank_account, wallet
    token VARCHAR(100) NOT NULL UNIQUE,           -- From payment vault
    
    -- Safe to store (not sensitive)
    display_name VARCHAR(100),                    -- "Visa ending 4242"
    last4 CHAR(4),
    expiry_month SMALLINT,
    expiry_year SMALLINT,
    card_brand VARCHAR(20),                       -- visa, mastercard, amex
    
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- NEVER store: full card number, CVV, magnetic stripe data
    CONSTRAINT never_store_sensitive CHECK (
        token IS NOT NULL AND length(last4) <= 4
    )
);

CREATE INDEX idx_payment_method_user ON payment_methods (user_id, is_active);
```

### 🔄 Payment Flow Sequence Diagram

```
┌──────┐      ┌────────┐      ┌────────────┐      ┌────────┐      ┌───────────┐      ┌────────┐
│Client│      │Merchant│      │Payment API │      │  Fraud │      │  Provider │      │Database│
└──┬───┘      └───┬────┘      └─────┬──────┘      └───┬────┘      └─────┬─────┘      └───┬────┘
   │              │                  │                 │                 │                │
   │ Submit Order │                  │                 │                 │                │
   │─────────────>│                  │                 │                 │                │
   │              │                  │                 │                 │                │
   │              │ POST /payments   │                 │                 │                │
   │              │ {idempotency_key,│                 │                 │                │
   │              │  amount, token}  │                 │                 │                │
   │              │─────────────────>│                 │                 │                │
   │              │                  │                 │                 │                │
   │              │                  │ Check idempotency                 │                │
   │              │                  │────────────────────────────────────────────────────>│
   │              │                  │                 │                 │                │
   │              │                  │<───────────────────────────────────────────────────│
   │              │                  │ (not found - new request)         │                │
   │              │                  │                 │                 │                │
   │              │                  │ Fraud check     │                 │                │
   │              │                  │────────────────>│                 │                │
   │              │                  │                 │                 │                │
   │              │                  │<────────────────│                 │                │
   │              │                  │ score: 0.1 (OK) │                 │                │
   │              │                  │                 │                 │                │
   │              │                  │ Create txn record                 │                │
   │              │                  │────────────────────────────────────────────────────>│
   │              │                  │                 │                 │                │
   │              │                  │ Authorize       │                 │                │
   │              │                  │─────────────────────────────────>│                │
   │              │                  │                 │                 │                │
   │              │                  │                 │                 │ Forward to     │
   │              │                  │                 │                 │ card network   │
   │              │                  │                 │                 │──────────>     │
   │              │                  │                 │                 │                │
   │              │                  │                 │                 │ <──────────    │
   │              │                  │                 │                 │ Approved       │
   │              │                  │                 │                 │                │
   │              │                  │<─────────────────────────────────│                │
   │              │                  │ auth_code: ABC123                 │                │
   │              │                  │                 │                 │                │
   │              │                  │ Update txn + ledger entries       │                │
   │              │                  │────────────────────────────────────────────────────>│
   │              │                  │                 │                 │                │
   │              │                  │ Store idempotency result          │                │
   │              │                  │────────────────────────────────────────────────────>│
   │              │                  │                 │                 │                │
   │              │<─────────────────│                 │                 │                │
   │              │ 200 OK           │                 │                 │                │
   │              │ {txn_id, status} │                 │                 │                │
   │              │                  │                 │                 │                │
   │<─────────────│                  │                 │                 │                │
   │ Payment Success                 │                 │                 │                │
```

### 🔒 PCI-DSS Compliance Checklist

| Requirement | Implementation | How We Comply |
|-------------|---------------|---------------|
| **Never store CVV** | No CVV field in DB | CVV only passed to provider API, not logged |
| **Encrypt card data** | Tokenization | We never see raw card numbers - use Stripe tokens |
| **Network security** | TLS 1.3 everywhere | Enforced at load balancer |
| **Access control** | Least privilege | Payment DB on isolated subnet |
| **Audit logging** | All access logged | transaction_events table, immutable |
| **Key rotation** | Every 90 days | AWS KMS with automatic rotation |
| **Vulnerability scanning** | Weekly | Qualys + internal pentests |
| **Incident response plan** | Documented | Notify within 24 hours |

```python
# NEVER do this:
class BadPaymentRequest:
    card_number: str      # ❌ NEVER store
    cvv: str              # ❌ NEVER store
    expiry: str           # ⚠️ Only store encrypted

# DO this instead:
class GoodPaymentRequest:
    payment_token: str    # ✅ Token from Stripe/Adyen
    last4: str            # ✅ Safe for display
    idempotency_key: str  # ✅ For exactly-once
```

### 🌍 Real-World Case Study: Stripe

| Aspect | Stripe's Approach | Learning |
|--------|-------------------|----------|
| **Idempotency** | Required for all mutations | Client must provide `Idempotency-Key` header |
| **Errors** | Structured error codes | `card_declined`, `insufficient_funds`, `expired_card` |
| **Webhooks** | At-least-once delivery | Client must handle duplicate events |
| **Rate limits** | 100 reqs/sec default | Automatic backoff required |
| **Testing** | Test mode with fake cards | `4242424242424242` always succeeds |

**Key Takeaways:**
1. **Idempotency is non-negotiable** - Every payment API must support it
2. **Tokenization >> Encryption** - Don't handle raw card data
3. **Webhooks need deduplication** - Same event can arrive multiple times
4. **Always have a reconciliation job** - Compare with provider daily

### ⚠️ Failure Scenarios & Recovery

| Failure | Detection | Impact | Recovery |
|---------|-----------|--------|----------|
| **Provider timeout** | No response in 30s | Unknown state | Query provider status, set to PENDING_REVIEW |
| **DB write fails after auth** | Exception caught | Money charged but not recorded | Immediate refund via provider API |
| **Ledger imbalance** | Nightly reconciliation | Accounting error | Alert, manual investigation, compensating entry |
| **Fraud after authorization** | Delayed ML review | Potential chargeback | Cancel capture, notify merchant |
| **Provider outage** | Health check fails | All payments fail | Failover to backup provider (Stripe → Adyen) |

```python
class PaymentRecoveryService:
    """
    Background job xử lý các transactions stuck.
    Chạy every 5 minutes.
    """
    
    async def recover_stuck_transactions(self):
        # Find transactions stuck in PENDING/AUTHORIZED for > 30 minutes
        stuck = await self.db.query("""
            SELECT * FROM transactions 
            WHERE status IN ('PENDING', 'AUTHORIZED')
            AND updated_at < NOW() - INTERVAL '30 minutes'
        """)
        
        for txn in stuck:
            try:
                # Query provider for actual status
                provider_status = await self.provider.get_status(
                    txn.provider_transaction_id
                )
                
                if provider_status == 'APPROVED':
                    # Provider approved but we missed callback
                    await self.mark_authorized(txn.id)
                    
                elif provider_status == 'DECLINED':
                    # Provider declined but we missed callback
                    await self.mark_failed(txn.id, 'declined_by_provider')
                    
                elif provider_status == 'NOT_FOUND':
                    # Request never reached provider
                    await self.mark_failed(txn.id, 'never_submitted')
                    
                else:
                    # Still processing - extend timeout
                    await self.extend_timeout(txn.id)
                    
            except Exception as e:
                logger.error(f"Recovery failed for {txn.id}: {e}")
                await self.escalate_to_oncall(txn.id)
```

### Red Flags

❌ Using eventual consistency for ledger  
❌ Storing credit card numbers in your DB  
❌ No idempotency mechanism  
❌ Float instead of Decimal for money  

---

# 13. Distributed Cache System

> **Ví dụ thực tế**: Redis Cluster, Memcached, NAVER internal caching  
> **Thời gian phỏng vấn**: 45 phút

## 🎯 Phase 1: Understand the Problem (5 phút)

### Clarifying Questions

| Câu hỏi | Impact | Giả định |
|---------|--------|----------|
| "Cache pattern nào? Read-heavy hay write-heavy?" | Ảnh hưởng consistency strategy | Read-heavy (100:1) |
| "TTL-based hay explicit invalidation?" | Complexity của invalidation | Cả hai |
| "Single data center hay multi-region?" | Replication strategy | Multi-region |
| "Acceptable stale data window?" | Eventually consistent hay strong | 1-5 seconds ok |

### Requirements
- **FR1**: GET/SET/DELETE operations
- **FR2**: TTL support
- **FR3**: Eviction policies (LRU, LFU)
- **NFR1**: p99 < 10ms
- **NFR2**: 99.99% availability
- **NFR3**: 10M QPS capacity

---

## 📊 Phase 2: Capacity Estimation (3 phút)

```
QPS: 10M reads/sec, 100K writes/sec
Average key size: 100 bytes
Average value size: 1KB
Total items: 1 Billion

Memory needed = 1B × (100 + 1000) bytes = 1.1TB

Per node (64GB max): 1.1TB / 64GB ≈ 18 nodes minimum
With 3x replication: 54 nodes
```

---

## 🏗️ Phase 3: High-Level Design (10 phút)

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      APPLICATION SERVERS                        │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │  App 1   │  │  App 2   │  │  App 3   │  │  App N   │       │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│        │             │             │             │              │
│        └─────────────┼─────────────┼─────────────┘              │
│                      │             │                            │
│              ┌───────▼─────────────▼───────┐                   │
│              │    CACHE CLIENT LIBRARY     │                   │
│              │  • Connection pooling       │                   │
│              │  • Consistent hashing       │                   │
│              │  • Retry logic              │                   │
│              └─────────────┬───────────────┘                   │
└────────────────────────────┼───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │  Shard 1   │  │  Shard 2   │  │  Shard 3   │
       │            │  │            │  │            │
       │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
       │ │ Master │ │  │ │ Master │ │  │ │ Master │ │
       │ └───┬────┘ │  │ └───┬────┘ │  │ └───┬────┘ │
       │     │      │  │     │      │  │     │      │
       │ ┌───▼────┐ │  │ ┌───▼────┐ │  │ ┌───▼────┐ │
       │ │Replica1│ │  │ │Replica1│ │  │ │Replica1│ │
       │ └────────┘ │  │ └────────┘ │  │ └────────┘ │
       │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │
       │ │Replica2│ │  │ │Replica2│ │  │ │Replica2│ │
       │ └────────┘ │  │ └────────┘ │  │ └────────┘ │
       └────────────┘  └────────────┘  └────────────┘
```

---

## 🔬 Phase 4: Deep Dive (15 phút)

### 4.1 Consistent Hashing - Tại sao không dùng modulo?

**Problem với modulo hashing:**
```
hash(key) % N = node_number

Khi thêm 1 node: N → N+1
→ Hầu hết keys phải di chuyển!
→ Cache stampede, system chậm
```

**Solution: Consistent Hashing**
```
┌─────────────────────────────────────────────────────────────┐
│                    HASH RING (0 to 2^32)                    │
│                                                             │
│                           0°                                │
│                          ┌───┐                              │
│                    Node A│   │                              │
│                          └───┘                              │
│                   ╱            ╲                            │
│                 ╱                ╲                          │
│    270°  ┌───┐                      ┌───┐  90°             │
│     Node D│   │                     │   │Node B            │
│          └───┘                      └───┘                   │
│                 ╲                ╱                          │
│                   ╲            ╱                            │
│                          ┌───┐                              │
│                    Node C│   │                              │
│                          └───┘                              │
│                          180°                               │
│                                                             │
│  Key lookup: hash(key) → find next node clockwise          │
│  Add node: Only keys between prev and new node move        │
└─────────────────────────────────────────────────────────────┘
```

```python
class ConsistentHashRing:
    """
    Virtual nodes: Mỗi physical node có 150 virtual nodes
    Tại sao? Để distribution đều hơn
    
    Không có virtual nodes → nodes có thể clustered trên ring
    → Some nodes get 30% traffic, some get 5%
    """
    def __init__(self, nodes, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            for i in range(virtual_nodes):
                virtual_key = hash(f"{node}:{i}")
                self.ring[virtual_key] = node
                self.sorted_keys.append(virtual_key)
        
        self.sorted_keys.sort()
    
    def get_node(self, key):
        """O(log n) với binary search"""
        if not self.ring:
            return None
            
        hash_key = hash(key)
        
        # Binary search for first node >= hash_key
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        
        # Wrap around
        if idx == len(self.sorted_keys):
            idx = 0
            
        return self.ring[self.sorted_keys[idx]]
```

### 4.2 Eviction Policies - Trade-offs

| Policy | When to use | Trade-off |
|--------|-------------|-----------|
| **LRU** | General purpose | May evict freq accessed but not recent |
| **LFU** | Stable access patterns | Slow to adapt to changes |
| **TTL** | Time-sensitive data | May keep stale data until expire |
| **LRU + TTL** | Production choice | Balances both |

### 4.3 Cache Patterns

**Cache-Aside (Read-through)**
```python
def get_user(user_id):
    """
    Pattern phổ biến nhất.
    Pro: Simple, app controls caching logic
    Con: First request always slow (cache miss)
    """
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

**Write-Through**
```python
def update_user(user_id, data):
    """
    Write to cache AND db synchronously.
    Pro: Cache always fresh
    Con: Write latency increases
    """
    db.update("UPDATE users SET ... WHERE id = ?", user_id, data)
    cache.set(f"user:{user_id}", data, ttl=3600)
```

**Write-Behind (Write-Back)**
```python
def update_user(user_id, data):
    """
    Write to cache first, async to db.
    Pro: Fast writes
    Con: Data loss risk if cache crashes
    """
    cache.set(f"user:{user_id}", data)
    queue.publish("user_updates", {"id": user_id, "data": data})
    # Background worker writes to DB
```

---

## 📈 Phase 5: Scaling & Bottlenecks

### Cache Stampede Problem

**Scenario**: Popular key expires → 1000 requests hit DB simultaneously

**Solutions**:
```python
def get_with_lock(key):
    """
    Khi cache miss, chỉ 1 request đi DB, còn lại wait.
    """
    value = cache.get(key)
    if value:
        return value
    
    lock = cache.lock(f"lock:{key}", timeout=5)
    if lock.acquire():
        try:
            # Double check
            value = cache.get(key)
            if value:
                return value
            
            # Only this request hits DB
            value = db.query(key)
            cache.set(key, value, ttl=3600)
            return value
        finally:
            lock.release()
    else:
        # Wait and retry
        time.sleep(0.1)
        return cache.get(key)  # Should exist now
```

---

## 💡 Phase 6: Interview Tips

### Common Questions

1. **"Cache vs Database consistency?"**
   - Accept eventual consistency for most cases
   - For critical data → write-through or invalidate

2. **"Hot key problem?"**
   - Replicate hot keys to multiple nodes
   - Add random suffix to spread: `key:1`, `key:2`

3. **"How to warm cache after restart?"**
   - Lazy loading (gradual)
   - Pre-warming script

### 🔧 Redis Internals - Interview Deep Dive

```python
# Redis Data Structures và Khi Nào Dùng

REDIS_DATA_STRUCTURES = {
    'STRING': {
        'use_case': 'Simple key-value, counters, sessions',
        'example': 'SET user:123:session "abc" EX 3600',
        'complexity': 'O(1)',
    },
    'HASH': {
        'use_case': 'Object storage, user profiles',
        'example': 'HSET user:123 name "John" age 25',
        'complexity': 'O(1) per field',
        'why': 'Memory efficient for small hashes (<512 entries)',
    },
    'LIST': {
        'use_case': 'Queues, recent items, activity feeds',
        'example': 'LPUSH recent:user:123 "action1"',
        'complexity': 'O(1) push/pop, O(n) index',
    },
    'SET': {
        'use_case': 'Unique items, tags, followers',
        'example': 'SADD user:123:followers 456 789',
        'complexity': 'O(1) add/remove/check',
    },
    'SORTED_SET': {
        'use_case': 'Leaderboards, range queries, autocomplete',
        'example': 'ZADD leaderboard 1000 "player1"',
        'complexity': 'O(log n) add, O(log n + m) range',
        'why': 'Best for ranking and top-N queries',
    },
}
```

### 🗄️ Cache Monitoring & Metrics

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| **Hit Rate** | Cache effectiveness | < 80% = investigate |
| **Memory Usage** | Capacity planning | > 80% = add nodes |
| **Eviction Count** | Cache too small | Increasing = bad |
| **Connected Clients** | Load distribution | Spikes = potential issue |
| **Latency p99** | Performance | > 10ms = investigate |

```python
class CacheMonitor:
    """
    Production cache monitoring.
    Integrate with Prometheus/Grafana.
    """
    
    def collect_metrics(self):
        info = self.redis.info()
        
        return {
            # Hit rate
            'hit_rate': info['keyspace_hits'] / (
                info['keyspace_hits'] + info['keyspace_misses']
            ),
            
            # Memory
            'memory_used_gb': info['used_memory'] / (1024**3),
            'memory_peak_gb': info['used_memory_peak'] / (1024**3),
            'memory_fragmentation_ratio': info['mem_fragmentation_ratio'],
            
            # Performance
            'connected_clients': info['connected_clients'],
            'blocked_clients': info['blocked_clients'],
            'ops_per_sec': info['instantaneous_ops_per_sec'],
            
            # Eviction
            'evicted_keys': info['evicted_keys'],
            'expired_keys': info['expired_keys'],
        }
    
    def check_health(self, metrics):
        alerts = []
        
        if metrics['hit_rate'] < 0.80:
            alerts.append(f"Low cache hit rate: {metrics['hit_rate']:.2%}")
        
        if metrics['memory_fragmentation_ratio'] > 1.5:
            alerts.append("High memory fragmentation - restart recommended")
        
        if metrics['evicted_keys'] > self.last_evicted + 1000:
            alerts.append("High eviction rate - increase capacity")
        
        return alerts
```

### ⚠️ Failure Scenarios & Handling

| Failure | Impact | Detection | Recovery |
|---------|--------|-----------|----------|
| **Single node crash** | 1/N keys unavailable | Sentinel detects | Auto-failover to replica |
| **Network partition** | Split brain possible | Health checks fail | Quorum-based leader election |
| **Memory exhaustion** | Evictions or OOM kill | Memory alerts | Vertical scale or shard |
| **Hot key saturation** | One shard overloaded | Latency spike | Key replication or sharding |
| **Full cluster restart** | Cold cache | All nodes down | Pre-warming from DB |

```python
class RedisClusterWithFailover:
    """
    Production Redis cluster client với automatic failover.
    """
    
    def __init__(self):
        self.primary_cluster = RedisCluster(startup_nodes=[
            {'host': 'redis-1', 'port': 6379},
            {'host': 'redis-2', 'port': 6379},
            {'host': 'redis-3', 'port': 6379},
        ])
        
        self.backup_cluster = RedisCluster(startup_nodes=[
            {'host': 'redis-backup-1', 'port': 6379},
        ])
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout_sec=30
        )
    
    async def get(self, key: str):
        # Try primary with circuit breaker
        if self.circuit_breaker.is_closed():
            try:
                return await self.primary_cluster.get(key)
            except RedisClusterException as e:
                self.circuit_breaker.record_failure()
                logger.error(f"Primary cluster error: {e}")
        
        # Fallback to backup
        try:
            return await self.backup_cluster.get(key)
        except RedisClusterException as e:
            logger.error(f"Backup cluster error: {e}")
            return None  # Graceful degradation
```

### 🌍 Real-World Case Study: Twitter (X) Cache Architecture

| Aspect | Twitter's Approach | Learning |
|--------|-------------------|----------|
| **Scale** | 100TB+ cached data | Need horizontal sharding |
| **Cache layers** | L1 (local) + L2 (Redis) + L3 (Memcached) | Multi-tier for hot data |
| **Hot timelines** | Pre-computed fan-out | Trade write cost for read speed |
| **Consistency** | Eventually consistent, ~5s lag | Acceptable for social feed |
| **Eviction** | LRU + TTL | Balance freshness and hit rate |

**Key Takeaways:**
1. **Multi-layer caching** - Local → Redis → Persistent cache
2. **Accept eventual consistency** - Most use cases don't need strong
3. **Pre-compute hot data** - Timeline fan-out on write
4. **Monitor hit rates obsessively** - 1% drop = significant infrastructure cost

# 14. Rate Limiter

> **Ví dụ thực tế**: API Gateway limits, DDoS protection  
> **Thời gian phỏng vấn**: 35 phút (simpler than others)

## 🎯 Phase 1: Understand the Problem (3 phút)

### Requirements
- **FR1**: Limit requests per user/IP/API key
- **FR2**: Different limits for different APIs
- **FR3**: Return clear error when limited
- **NFR1**: Minimal latency overhead (<1ms)
- **NFR2**: Distributed across servers

### Clarifying Questions (ngắn nhưng điểm cao)

| Câu hỏi | Tại sao quan trọng | Giả định |
|--------|---------------------|----------|
| "Limit theo cái gì?" (IP/user/api_key) | Key design quyết định fairness | Support cả 3 |
| "Burst có được phép không?" | Chọn Token Bucket vs Leaky Bucket | Cho phép burst ngắn |
| "Limit global hay per-region?" | Multi-region làm khó consistency | Per-region + optional global |
| "Có tier (free/premium) không?" | Config + cache policy khác | Có |
| "Cần header chuẩn không?" | Client retry/backoff | Có |

> 💡 Key insight: Rate limiter là bài về **atomicity + hot path latency**. Nếu không atomic → vượt limit; nếu chậm → phá SLO của toàn hệ thống.

---

## 📊 Phase 2: Capacity Estimation (3 phút)

### Quick math (đủ dùng trong interview)

Giả sử:
- Peak traffic qua Gateway: **200K RPS**
- Unique keys active trong 1 phút: **~10M** (user + IP + api_key)

**Redis ops**:
- Token Bucket / Sliding Window Counter dùng Lua: ~1 `EVAL`/request
- 200K RPS → 200K `EVAL`/sec → cần **Redis Cluster + sharding**

**Memory cho state** (ước lượng):
- Mỗi key lưu vài counters + timestamp + overhead
- Rough: ~100 bytes/key → 10M keys ≈ ~1GB (chưa tính replication)

> 💡 Hệ quả thiết kế: luôn có **TTL**, luôn **stateless gateway**, và tránh “mỗi request gọi nhiều service”.

---

## 🏗️ Phase 3: High-Level Design

### Where to place rate limiter?

```
Option 1: API Gateway (recommended)
┌────────┐     ┌────────────┐     ┌──────────┐
│ Client │────▶│ API Gateway│────▶│ Backend  │
│        │     │ + Limiter  │     │          │
└────────┘     └────────────┘     └──────────┘

Option 2: Middleware trong mỗi service
Option 3: Sidecar proxy (Envoy, Istio)
```

### Architecture Overview (Recommended)

```
┌────────┐   ┌───────────────────┐   ┌────────────────────────┐   ┌──────────┐
│ Client │──▶│ API Gateway/LB     │──▶│ Rate Limiter Module     │──▶│ Backend  │
└────────┘   │ (auth, routing)    │   │ (stateless, fast)       │   └──────────┘
             └─────────┬─────────┘   └───────────┬────────────┘
                       │                         │
                       │                         ▼
                       │                 ┌──────────────────┐
                       │                 │ Redis Cluster     │
                       │                 │ (atomic via Lua)  │
                       │                 └──────────────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Config Store       │
             │ (DB + cache)       │
             └───────────────────┘

Optional (multi-region):
- Local limit (region Redis) cho latency
- Global limit (async) cho abuse control (eventual)
```

### Key Design (quan trọng hơn thuật toán)

**Key format** (dễ debug, dễ shard):

```
rl:{scope}:{subject}:{route}:{algo}

Examples:
- rl:user:123:/v1/payments:tb
- rl:ip:203.0.113.10:/v1/search:sw
- rl:apikey:abc123:/v1/export:tb
```

**Priority** khi chọn key (đề xuất):
1) `api_key` (B2B)
2) `user_id` (authenticated)
3) `ip` (anonymous)

> 💡 Pitfall: NAT làm IP share giữa nhiều user → IP-limit phải thấp hơn, và nên “đệm” thêm user-limit khi login.

---

## Deep Reading Notes (Q14)

- Hot path: gateway → build key (api_key/user/ip + route + tier) → Redis Lua `EVAL` → allow/deny + headers.
- Invariants:
    - Atomicity: counter/window update phải atomic (Lua/txn), không race.
    - Keying/fairness: đúng “subject” và “scope” (global vs per-route) để không phạt nhầm.
    - Time correctness: window math nhất quán (client time vs Redis `TIME`).
    - Degradation policy: fail-open vs fail-closed theo risk của endpoint.
- Trade-offs:
    - Token Bucket vs Sliding Window Counter: burst control vs simplicity/cost.
    - Per-region limit vs global strict limit: latency vs consistency.
    - Central Redis vs local in-process + sync: accuracy vs availability.
- Failure drills:
    - Redis p99 tăng/timeout: circuit breaker, local fallback, hoặc bypass có kiểm soát.
    - Hot key (1 api_key bị abuse): shard strategy, per-route cap, “shadow ban”/progressive penalties.
    - Retry storm (client retries on 429/5xx): headers + backoff + jitter, protect Redis.

## 🔬 Phase 4: Deep Dive - Algorithms

### 4.0 API Contract & RateLimit Headers (production-grade)

**Request**: mọi request đi qua gateway đều được gắn identity (ưu tiên api_key/user/ip) và route.

**Response headers** (gợi ý theo RFC-like conventions, đủ để client backoff đúng):

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Retry-After: 30
```

Notes:
- `Reset` nên là epoch seconds của thời điểm “cửa sổ” reset (hoặc earliest retry time), để client tính backoff.
- Với Token Bucket, `Retry-After` có thể là thời gian tới khi có 1 token mới (ceil).

### 4.0 Data Model (Redis) theo từng thuật toán

| Algorithm | Redis type | Key example | Stored fields |
|----------|------------|-------------|---------------|
| Token Bucket | HASH | `rl:user:123:/v1/payments:tb` | `tokens`, `last_refill_ms` |
| Sliding Window Log | ZSET | `rl:user:123:/v1/search:swl` | members = request_id, score = timestamp_ms |
| Sliding Window Counter | HASH | `rl:user:123:/v1/search:swc` | bucket fields = `bucket_id` → count |

**Key rule**: luôn set TTL để key tự GC khi user không active.

### 4.0 Config Model (DB) + Cache Strategy

Điểm “giống Q12”: limiter cũng cần **source of truth** cho rules (tier/route/limits) và phải cache để không làm chậm hot path.

```sql
-- Rate limit rules (source of truth)
CREATE TABLE rate_limit_rules (
    id BIGSERIAL PRIMARY KEY,
    scope VARCHAR(32) NOT NULL,           -- global / per_route / per_method
    subject_type VARCHAR(16) NOT NULL,    -- api_key / user / ip
    route_pattern VARCHAR(255) NOT NULL,  -- e.g. /v1/payments/*
    tier VARCHAR(32) NOT NULL,            -- free / premium / internal
    algorithm VARCHAR(16) NOT NULL,       -- tb / swc / swl
    limit_value INT NOT NULL,             -- e.g. 100
    window_ms INT NOT NULL,               -- e.g. 60000 (for window algos)
    burst INT,                            -- for token bucket capacity
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rl_lookup ON rate_limit_rules (subject_type, tier, route_pattern);
```

Serving pattern:
- Gateway loads rules into local cache (e.g., 30–60s TTL) + watches updates (pub/sub) để giảm cache staleness.
- Nếu cache miss: fallback to a safe default rule (thường stricter cho public endpoints).

### 4.1 Token Bucket

```
┌─────────────────────────────────────────────────────────────┐
│                    TOKEN BUCKET                             │
│                                                             │
│  Tokens added:     ●●●●●                                   │
│  at fixed rate     ↓↓↓↓↓                                   │
│                 ┌─────────────┐                            │
│                 │ ● ● ● ● ●  │  Bucket capacity: 10       │
│                 │   Bucket    │                            │
│                 └──────┬──────┘                            │
│                        │                                    │
│                        ▼                                    │
│  Request comes  ──▶ Take 1 token                           │
│                                                             │
│  If bucket empty → REJECT                                  │
│  If has token → ALLOW and remove token                     │
└─────────────────────────────────────────────────────────────┘

Pros: Allows bursts up to bucket size
Cons: Need to track tokens + last_refill_time
```

```python
class TokenBucket:
    """
    Redis-based distributed token bucket.
    
    Dùng Lua script để atomic operation.
    """
    
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now
    
    -- Refill tokens
    local elapsed = now - last_refill
    tokens = math.min(capacity, tokens + elapsed * refill_rate)
    
    -- Try to consume
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        return 1  -- Allowed
    else
        return 0  -- Rejected
    end
    """
    
    def allow_request(self, user_id):
        now = time.time()
        result = redis.eval(
            self.LUA_SCRIPT,
            1,  # Number of keys
            f"ratelimit:{user_id}",  # Key
            10,  # Capacity
            1,   # Refill rate (tokens/sec)
            now
        )
        return result == 1
```

### Token Bucket (Production notes)

- **Atomic**: Luôn dùng Lua (hoặc Redis transaction) để tránh race conditions.
- **TTL**: Key không dùng nữa phải tự hết hạn để tiết kiệm memory.
- **Clock**: Nếu lo time drift, có thể dùng Redis `TIME` trong Lua thay vì client time.

---

### 4.2 Sliding Window Log (accurate nhưng đắt)

**Idea**: Lưu timestamp từng request vào `ZSET`, xoá phần quá hạn, rồi đếm.

Pros: chính xác cao  
Cons: nhiều write + memory cao khi limit lớn

```python
class SlidingWindowLog:
    """Accurate sliding window using Redis ZSET + Lua."""

    LUA = """
        local key = KEYS[1]
        local now_ms = tonumber(ARGV[1])
        local window_ms = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])
        local member = ARGV[4]

        redis.call('ZREMRANGEBYSCORE', key, 0, now_ms - window_ms)
        redis.call('ZADD', key, now_ms, member)

        local count = redis.call('ZCARD', key)
        redis.call('PEXPIRE', key, window_ms + 1000)

        if count <= limit then
            return {1, count}
        else
            return {0, count}
        end
    """

    def __init__(self, redis, limit: int, window_ms: int):
        self.redis = redis
        self.limit = limit
        self.window_ms = window_ms

    def allow(self, key: str, request_id: str, now_ms: int):
        allowed, count = self.redis.eval(
            self.LUA,
            1,
            key,
            now_ms,
            self.window_ms,
            self.limit,
            request_id,
        )
        return allowed == 1, int(count)
```

---

### 4.3 Sliding Window Counter (recommended default)

```
┌─────────────────────────────────────────────────────────────┐
│                SLIDING WINDOW COUNTER                       │
│                                                             │
│  Time:     |-------|-------|-------|-------|              │
│            1:00    1:01    1:02    1:03                    │
│                                                             │
│  Counts:      15      20      18      12                   │
│                                                             │
│  At 1:02:30, limit = 50 requests/min                       │
│                                                             │
│  Current window: 0.5 × 20 (prev) + 0.5 × 18 (current)     │
│                = 10 + 9 = 19                               │
│                                                             │
│  Space left: 50 - 19 = 31 requests                        │
└─────────────────────────────────────────────────────────────┘
```

**Idea**: Chia thời gian thành 2 buckets (current + previous), rồi nội suy.

Ưu điểm:
- O(1) memory per key
- Ít write hơn log
- Mượt hơn Fixed Window

```python
class SlidingWindowCounter:
    """Two-bucket sliding window counter via Redis hash + Lua."""

    LUA = """
        local key = KEYS[1]
        local now_ms = tonumber(ARGV[1])
        local window_ms = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])

        local current_bucket = math.floor(now_ms / window_ms)
        local prev_bucket = current_bucket - 1

        local curr_field = tostring(current_bucket)
        local prev_field = tostring(prev_bucket)

        local curr = redis.call('HINCRBY', key, curr_field, 1)
        local prev = tonumber(redis.call('HGET', key, prev_field)) or 0

        local bucket_start_ms = current_bucket * window_ms
        local elapsed_ms = now_ms - bucket_start_ms
        local prev_weight = (window_ms - elapsed_ms) / window_ms

        local approx = prev * prev_weight + curr

        redis.call('PEXPIRE', key, window_ms * 2)

        if approx <= limit then
            return {1, approx}
        else
            return {0, approx}
        end
    """

    def __init__(self, redis, limit: int, window_ms: int):
        self.redis = redis
        self.limit = limit
        self.window_ms = window_ms

    def allow(self, key: str, now_ms: int):
        allowed, approx = self.redis.eval(
            self.LUA,
            1,
            key,
            now_ms,
            self.window_ms,
            self.limit,
        )
        return allowed == 1, float(approx)
```

### Algorithm Comparison

| Algorithm | Memory | Accuracy | Burst | Use Case |
|-----------|--------|----------|-------|----------|
| **Token Bucket** | Low | High | Allows controlled burst | API limits |
| **Leaky Bucket** | Low | High | Smooth rate | Traffic shaping |
| **Fixed Window** | Very Low | Low | Boundary problem | Simple limits |
| **Sliding Window** | Medium | High | Smooth | Precise limits |

---

## 📈 Phase 5: Scaling, Bottlenecks, Multi-Region

### Bottlenecks & fixes

| Bottleneck | Symptom | Fix |
|------------|---------|-----|
| Redis hotspot | p99 tăng | Redis Cluster sharding + local limiter (L1) |
| Hot key (1 API key abused) | One shard overloaded | Add secondary shard key + global aggregation |
| Retry storm | 429 spike + write spike | `Retry-After`, backoff + jitter |
| Cross-region latency | limiter adds 20-80ms | State per-region, global enforcement async |

### Multi-region strategy (pragmatic)

**Option A (simple)**: Per-region limit only
- Pro: fastest, simplest
- Con: attacker có thể “chia tải” qua nhiều regions

**Option B (hybrid)**: Local hard limit + global soft limit
- Local: enforce strict per-key limit (low latency)
- Global: stream events (Kafka) → detect abuse keys → push “denylist/quota” về regions

### Graceful degradation

Nếu Redis timeout/down:
- **Fail-open** cho low-risk endpoints (search, feed) để tránh outage
- **Fail-closed** cho high-risk endpoints (login, payment, export) để tránh abuse

> 💡 Interview tip: Nêu rõ endpoint nào fail-open vs fail-closed và lý do.

---

## 📊 Observability (điểm cộng lớn)

Metrics nên có:
- `ratelimit_allowed_total{scope,route,tier}`
- `ratelimit_blocked_total{scope,route,tier}`
- `ratelimit_redis_latency_ms` (p50/p95/p99)
- `ratelimit_failopen_total` / `ratelimit_failclosed_total`

Logs/Tracing:
- Log key (anonymized/hash), route, tier, decision, remaining, reset
- Trace span: `rate_limit_check`

---

## 💡 Phase 6: Interview Tips

### HTTP Response cho Rate Limited

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000

{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the limit of 100 requests per minute",
  "retry_after": 30
}
```

### Common Questions

1. **"Rate limit by what? User? IP? API key?"**
   - API key cho B2B
   - User ID cho authenticated
   - IP cho anonymous + fallback

2. **"Distributed rate limiting?"**
   - Centralized Redis (most common)
   - Local + sync (lower latency, less accurate)

---

# 15. Video Transcoding System

> **Ví dụ thực tế**: YouTube, Netflix, NAVER TV  
> **Thời gian phỏng vấn**: 45 phút

## 🎯 Phase 1: Understand the Problem

### Requirements
- **FR1**: Upload video → transcode to multiple formats (1080p, 720p, 480p, 360p)
- **FR2**: Generate HLS/DASH for adaptive streaming
- **FR3**: Extract thumbnails
- **NFR1**: Handle 1000 concurrent uploads
- **NFR2**: Transcode within 2x real-time (1h video → 2h max)
- **NFR3**: Cost effective (spot instances)

### Clarifying Questions (để thiết kế đúng)

| Câu hỏi | Vì sao quan trọng | Giả định |
|--------|--------------------|----------|
| Video length/file size distribution? | Quyết định multipart upload + queue time | Median 5 phút, p95 1 giờ |
| Live streaming hay VOD? | Live cần latency/segment khác hẳn | VOD |
| SLA processing? | HPA/worker sizing | 95% < 30 phút |
| Có DRM/Watermark không? | Pipeline thêm bước, CPU/GPU | Optional |
| Có cần virus scan/content moderation? | Bảo mật/tuân thủ | Có, async |

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- Upload: **1M videos/day**
- Average size: **200MB/video**
- Target profiles: **4 renditions** (1080/720/480/360) + HLS segments

### Storage

```
Raw ingest/day = 1,000,000 × 200MB ≈ 200,000,000MB ≈ 200TB/day

Processed multiplier (rough):
- 4 renditions + audio + container overhead ≈ 1.2x–2.5x raw (tuỳ bitrate ladder)
Assume 1.8x:
Processed/day ≈ 360TB/day

Total new storage/day ≈ 560TB/day
```

### Network bandwidth (ingest)

```
200TB/day / 86,400s ≈ 2.3GB/s average ingest
Peak factor 3x → ~7GB/s peak (CDN/edge ingest + multi-region helps)
```

### Compute (very rough)

```
If 1h video takes 2h CPU time (2x real-time) for 1080p,
and lower renditions are cheaper, assume total ~3x realtime CPU per video.

1M videos/day × 5min average = 5M minutes video/day
CPU minutes/day ≈ 15M CPU-min/day
≈ 250K CPU-hours/day
```

> 💡 Kết luận thiết kế: đây là **batch/async system** với điểm nghẽn là compute + egress, nên cần queue, autoscaling workers, checkpoint/retry, và tối ưu chi phí.

---

## 🏗️ Phase 3: High-Level Design

```
┌───────────────────────────────────────────────────────────────────────┐
│                         VIDEO TRANSCODING PIPELINE                     │
│                                                                        │
│  ┌────────┐    ┌────────────┐    ┌───────────┐    ┌──────────────┐   │
│  │ User   │───▶│  Upload    │───▶│    S3     │───▶│ Transcoding  │   │
│  │        │    │  Service   │    │  (Raw)    │    │   Queue      │   │
│  └────────┘    └────────────┘    └───────────┘    └──────┬───────┘   │
│                                                          │            │
│                                                          ▼            │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  WORKER POOL (Auto-scaling)                    │   │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│  │   │Worker 1 │  │Worker 2 │  │Worker 3 │  │Worker N │          │   │
│  │   │(FFmpeg) │  │(FFmpeg) │  │(FFmpeg) │  │(FFmpeg) │          │   │
│  │   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │   │
│  │        │            │            │            │                 │   │
│  │        └────────────┴────────────┴────────────┘                 │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                   │                                   │
│                                   ▼                                   │
│  ┌───────────┐    ┌────────────────┐    ┌───────────┐               │
│  │    S3     │◀───│  Notification  │───▶│   CDN     │               │
│  │(Processed)│    │    Service     │    │(Delivery) │               │
│  └───────────┘    └────────────────┘    └───────────┘               │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Deep Reading Notes (Q15)

- Hot path (upload): client multipart upload → store raw object → enqueue job → ACK user (async).
- Hot path (processing): worker claim job → download raw → transcode renditions + segments → upload processed → emit completion event.
- Invariants:
    - Idempotency: at-least-once queue ⇒ job must be safe to retry (key = `video_id + profile + step`).
    - Progress/state machine: each step transitions once; avoid double-publish/duplicate outputs.
    - Isolation: one “poison” video shouldn’t block the whole queue (timeouts + DLQ).
- Trade-offs:
    - Single worker per video vs per-rendition parallelism: throughput vs complexity + egress.
    - CPU-only vs GPU: cost vs speed; pick per profile/volume.
    - Spot instances vs on-demand: cost vs interruptions (checkpoint + retry).
- Failure drills:
    - Worker killed mid-transcode: resume strategy (recompute vs checkpoint), cleanup partial outputs.
    - Queue backlog spikes: autoscale by queue age/depth; apply admission control.
    - S3 throttling/egress bottleneck: rate-limit workers, regionalize storage, batch uploads.

## 🔬 Phase 4: Deep Dive

### 4.0 Job Model, State Machine, Idempotency (điểm làm bài “sâu”)

Trong production, queue là **at-least-once**, nên bạn phải chứng minh “retry không tạo output rác/duplicate”.

**State machine** (simplified):

`UPLOADED` → `QUEUED` → `PROCESSING` → (`SUCCEEDED` | `FAILED` | `CANCELLED`)

Mỗi video có nhiều tasks con: `(profile, step)` như `transcode`, `segment`, `thumbnail`.

```sql
-- Job table: 1 row per uploaded video
CREATE TABLE video_jobs (
    job_id UUID PRIMARY KEY,
    video_id UUID NOT NULL,
    uploader_id BIGINT,
    raw_object_key TEXT NOT NULL,
    status VARCHAR(16) NOT NULL,          -- UPLOADED/QUEUED/PROCESSING/SUCCEEDED/FAILED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Task table: idempotency boundary (unique per video/profile/step)
CREATE TABLE video_tasks (
    task_id UUID PRIMARY KEY,
    video_id UUID NOT NULL,
    profile VARCHAR(16) NOT NULL,         -- 1080p/720p/...
    step VARCHAR(16) NOT NULL,            -- transcode/segment/thumbnail
    status VARCHAR(16) NOT NULL,          -- PENDING/RUNNING/SUCCEEDED/FAILED
    attempt INT NOT NULL DEFAULT 0,
    output_prefix TEXT,
    error_code TEXT,
    error_message TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_video_task UNIQUE (video_id, profile, step)
);

CREATE INDEX idx_tasks_status ON video_tasks (status);
```

**Message schema** (queue):

```json
{
    "video_id": "...",
    "profile": "720p",
    "step": "transcode",
    "raw_object_key": "raw/2025/12/..../source.mp4",
    "attempt": 3,
    "idempotency_key": "{video_id}:{profile}:{step}"
}
```

**Storage layout** (debuggable + supports cleanup):

- `raw/{video_id}/source.mp4`
- `processed/{video_id}/{profile}/index.m3u8`
- `processed/{video_id}/{profile}/seg-00001.ts`
- `thumbnails/{video_id}/thumb-0001.jpg`

### 4.1 FFmpeg Transcoding

```python
class TranscodingWorker:
    """
    Worker polls SQS, downloads video, transcodes, uploads.
    
    Tại sao parallel transcoding?
    → CPU-bound task, 1 video có thể dùng hết 1 core
    → Transcode nhiều resolutions parallel = faster
    """
    
    PROFILES = {
        '1080p': {'resolution': '1920x1080', 'bitrate': '5000k'},
        '720p':  {'resolution': '1280x720',  'bitrate': '2800k'},
        '480p':  {'resolution': '854x480',   'bitrate': '1400k'},
        '360p':  {'resolution': '640x360',   'bitrate': '800k'},
    }
    
    def process(self, job):
        # 1. Download from S3
        input_path = download_from_s3(job.s3_key)
        
        # 2. Parallel transcode to all profiles
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for profile_name, settings in self.PROFILES.items():
                future = executor.submit(
                    self.transcode_profile,
                    input_path, 
                    profile_name,
                    settings
                )
                futures.append(future)
            
            # Wait all complete
            results = [f.result() for f in futures]
        
        # 3. Generate HLS master playlist
        master_playlist = self.generate_hls_manifest(results)
        
        # 4. Upload to processed bucket
        upload_to_s3(results, master_playlist)
        
        # 5. Notify completion
        notify_video_ready(job.video_id)
```

### 4.2 HLS Adaptive Streaming

```
Master Playlist (master.m3u8):
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080
1080p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720
720p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=854x480
480p/index.m3u8

Player behavior:
1. Start với quality trung bình
2. Đo bandwidth thực tế
3. Tự động switch quality dựa trên network
```

### 4.3 Cost Optimization

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| **Spot Instances** | 70-90% | Có thể bị interrupt |
| **Reserved capacity** | 30-60% | Commitment |
| **ARM instances** | 20-40% | Compatibility |

---

## 📈 Phase 5: Scaling, Reliability, Bottlenecks

### Queue semantics (must say in interview)

- Queue/worker thường là **at-least-once** → worker phải **idempotent**.
- Idempotency key gợi ý: `video_id + profile + step` (transcode/thumbnail/manifest).
- Có **DLQ** cho job fail vĩnh viễn (corrupt file, unsupported codec).

### Worker autoscaling

- Scale theo **queue depth** + **oldest message age**.
- Tách worker pools theo loại việc:
    - CPU-heavy: transcode
    - I/O-heavy: download/upload
    - lightweight: thumbnails/manifest

### Backpressure (ngăn hệ thống tự sập)

- Nếu queue lag tăng: giảm concurrency per worker (tránh OOM) + tăng workers.
- Nếu storage/egress bottleneck: throttling theo bucket/region.

### Hotspots

| Hotspot | Symptom | Fix |
|--------|---------|-----|
| S3 download/upload chậm | Worker idle / job time tăng | colocate workers gần bucket, use multipart, tuned retry |
| One huge file (p99) | Job chiếm worker lâu | Split pipeline, priority queue, per-tenant quotas |
| Spot interruptions | Job fail giữa chừng | checkpoint, requeue, mixed on-demand baseline |

---

## 📊 Observability

Metrics nên có:
- `transcode_jobs_queued`, `transcode_jobs_processing`, `transcode_jobs_failed`
- `transcode_queue_oldest_age_seconds`
- `transcode_duration_seconds{profile}` (histogram)
- `s3_download_bytes_total`, `s3_upload_bytes_total`
- `worker_cpu_utilization`, `worker_oom_killed_total`

Tracing/Logs:
- Trace per job: `download → transcode(profile*) → upload → manifest`
- Log `video_id`, `profile`, `attempt`, `ffmpeg_exit_code`, `error_category`

---

## 💡 Phase 6: Interview Tips

**Common Questions:**
1. **"Làm sao handle job failure giữa chừng?"**
   - Checkpoint progress
   - Resume từ segment cuối
   - Dead letter queue cho permanent failures

2. **"Priority queue cho premium users?"**
   - Multiple queues (high, normal, low)
   - Weighted polling

### 🎬 FFmpeg Commands - Must Know

```bash
# Basic transcoding to different resolutions
ffmpeg -i input.mp4 \
  -vf "scale=1920:1080" -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k output_1080p.mp4

# Generate HLS segments (for adaptive streaming)
ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -hls_time 6 \                    # 6-second segments
  -hls_playlist_type vod \         # Video on demand
  -hls_segment_filename "seg%03d.ts" \
  output.m3u8

# Generate thumbnail at 10 seconds
ffmpeg -i input.mp4 -ss 10 -vframes 1 thumbnail.jpg

# Extract audio only
ffmpeg -i input.mp4 -vn -c:a mp3 audio.mp3

# Hardware acceleration (if available)
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4
```

### 🗄️ Job Management Schema

```sql
CREATE TABLE transcoding_jobs (
    id UUID PRIMARY KEY,
    video_id UUID NOT NULL,
    
    -- Source
    source_s3_bucket VARCHAR(100) NOT NULL,
    source_s3_key VARCHAR(500) NOT NULL,
    source_format VARCHAR(20),
    source_duration_seconds INT,
    source_size_bytes BIGINT,
    
    -- Target profiles
    target_profiles JSONB NOT NULL,  -- ['1080p', '720p', '480p']
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'QUEUED',
    progress_percent INT DEFAULT 0,
    current_profile VARCHAR(20),
    
    -- Results
    output_s3_prefix VARCHAR(500),
    master_playlist_url VARCHAR(500),
    
    -- Timing
    queued_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Worker info
    worker_id VARCHAR(100),
    attempt_count INT DEFAULT 0,
    last_error TEXT,
    
    -- Priority (0 = highest)
    priority INT DEFAULT 5,
    user_tier VARCHAR(20),  -- premium, standard, free
    
    CONSTRAINT valid_status CHECK (status IN (
        'QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'
    ))
);

-- Index for worker polling
CREATE INDEX idx_jobs_queue ON transcoding_jobs (priority, queued_at) 
    WHERE status = 'QUEUED';

-- Index for status queries
CREATE INDEX idx_jobs_video ON transcoding_jobs (video_id);
```

### ⚠️ Failure Scenarios & Handling

| Failure | Detection | Impact | Recovery |
|---------|-----------|--------|----------|
| **Spot instance termination** | AWS 2-min warning | Job incomplete | Checkpoint, requeue remaining |
| **Corrupt input file** | FFmpeg error | Job fails | Mark failed, notify user |
| **Storage full** | Write error | Job fails | Alert ops, scale storage |
| **Memory OOM** | Process killed | Job hangs | Reduce concurrent profiles |
| **Network timeout** | S3 download fails | Job fails | Retry with backoff |

```python
class TranscodeJobWithCheckpoints:
    """
    Transcoding job with checkpoint/resume capability.
    """
    
    def __init__(self, job_id, redis):
        self.job_id = job_id
        self.redis = redis
        self.checkpoint_key = f"transcode:checkpoint:{job_id}"
    
    async def process(self, input_path, profiles):
        # Check for existing checkpoint
        checkpoint = await self.redis.hgetall(self.checkpoint_key)
        
        completed_profiles = set(checkpoint.get('completed', '').split(','))
        
        for profile in profiles:
            if profile in completed_profiles:
                logger.info(f"Skipping {profile} - already done")
                continue
            
            try:
                await self.transcode_profile(input_path, profile)
                
                # Save checkpoint after each profile
                completed_profiles.add(profile)
                await self.redis.hset(
                    self.checkpoint_key,
                    'completed', ','.join(completed_profiles)
                )
                
            except SpotTerminationWarning:
                # Save state and exit gracefully
                await self.redis.hset(
                    self.checkpoint_key,
                    'interrupted_at', profile
                )
                raise
        
        # Cleanup checkpoint on success
        await self.redis.delete(self.checkpoint_key)
```

### 🌍 Real-World Case Study: Netflix Video Encoding

| Aspect | Netflix's Approach | Learning |
|--------|-------------------|----------|
| **Scale** | 100+ hours uploaded/day | Need massive parallel processing |
| **Per-title encoding** | Custom bitrate ladder per video | Optimize storage per content type |
| **Quality metrics** | VMAF (Video Multi-Method Assessment) | Not just bitrate, but perceived quality |
| **Storage** | Store EVERY resolution | Trade storage cost for compute |
| **Global delivery** | Open Connect CDN | Pre-position popular content |

**Key Takeaways:**
1. **Parallel everything** - Each resolution can be done independently
2. **Checkpoint aggressively** - Spot termination is common
3. **Quality metrics matter** - VMAF > bitrate for user experience
4. **Cost optimization is continuous** - Reserved vs Spot vs On-demand mix

# 16. Collaborative Editing System

> **Ví dụ thực tế**: Google Docs, Notion, Figma  
> **Độ khó**: ⭐⭐⭐⭐⭐ (phức tạp nhất về concurrency)

## 🎯 Phase 1: Understand the Problem

### The Core Challenge

```
User A types "Hello" at position 0
User B types "World" at position 0 (same time)

Result should be: "HelloWorld" or "WorldHello"
NOT: "HWeolrllod" (interleaved mess)
```

### Requirements
- **FR1**: Multiple users edit same document simultaneously
- **FR2**: All users see same final state
- **FR3**: Real-time (<100ms) update propagation
- **NFR1**: Conflict resolution must be deterministic

### Clarifying Questions

| Câu hỏi | Vì sao quan trọng | Giả định |
|--------|--------------------|----------|
| Text docs hay rich-text (formatting, embeds)? | Data model + ops khác nhau | Rich-text (subset) |
| Offline editing có bắt buộc không? | Quyết định CRDT vs OT | Có |
| Concurrent editors/document? | WebSocket fanout + state mgmt | 50 concurrent |
| Cần version history/restore không? | Storage + snapshots | Có |
| Ordering guarantee? | Causality/sequence numbers | Server assigns seq |

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- DAU: 10M
- Concurrent editors peak: 1M
- Avg docs open concurrently: 200K docs
- Mỗi user tạo ~2 ops/sec (typing + cursor) → ~2M ops/sec peak

Hệ quả:
- Hot path phải cực nhẹ: validate + transform/merge + publish.
- Presence/cursor updates phải tách khỏi content ops (vì tần suất cao, độ quan trọng thấp hơn).

**Bandwidth rough**:
- 1 op ~ 100–500 bytes (tuỳ rich-text)
- 2M ops/sec × 200 bytes ≈ 400MB/s internal pub/sub (cần sharding theo doc_id).

---

## 🏗️ Phase 3: High-Level Design

### Architecture Overview

```
┌──────────────┐   WebSocket   ┌──────────────────────┐
│ Clients      │◀────────────▶│ WebSocket Gateway      │
│ (web/mobile) │              │ (auth, fanout)         │
└──────┬───────┘              └──────────┬─────────────┘
    │                                  │
    │ ops (insert/delete/format)       │ pub/sub per doc
    ▼                                  ▼
┌──────────────────────┐        ┌──────────────────────┐
│ Collaboration Engine  │        │ Presence Service      │
│ (OT or CRDT)          │        │ (cursors, users)      │
└──────────┬───────────┘        └──────────┬───────────┘
        │                               │
        │ snapshots + op log            │ ephemeral state
        ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│ Document Store        │        │ Redis (presence)      │
│ (Mongo/Postgres)      │        │ TTL keys              │
└──────────┬───────────┘        └──────────────────────┘
        │
        ▼
┌──────────────────────┐
│ Version History       │
│ (S3 + metadata DB)    │
└──────────────────────┘
```

### Data model choices (tóm tắt)

- **OT**: Centralized engine, transform operations theo thứ tự server.
- **CRDT**: Offline-first mạnh, merge deterministic, nhưng storage overhead.

Trong interview: nói rõ **chọn 1** theo requirements. Nếu offline bắt buộc + multi-region → nghiêng CRDT.

---

## Deep Reading Notes (Q16)

- Hot path (content ops): WS receive → validate/op_id dedupe → transform/merge (OT/CRDT) → append op log → publish to doc room → ack.
- Hot path (presence): WS receive cursor → write Redis TTL → fanout best-effort.
- Invariants:
    - Deterministic convergence: mọi replica phải ra cùng state.
    - Exactly-once apply per `op_id` (retry không làm double-apply).
    - Causality/order tracking: client_seq + server_seq (hoặc vector/lamport).
- 3 trade-offs phải nói được:
    - OT vs CRDT: centralized transform vs offline-first merge.
    - Persist-first vs publish-first: correctness vs latency (thường persist-before-ack).
    - Snapshot frequency: replay nhanh vs chi phí storage/IO.
- Failure drills:
    - Network partition 2 phút rồi reconnect: bạn replay/merge thế nào? user có thấy conflict UI không?
    - Gateway shard crash khi doc đang hot: reconnect routing + resubscribe room + replay from last_ack_seq.

## 🔬 Phase 4: Deep Dive - Conflict Resolution

### 4.1 Operational Transformation (OT)

**Concept**: Transform operations against each other

```
Server state: ""

User A: insert("a", 0) → "a"
User B: insert("b", 0) → should get "ba" or "ab"?

OT transformation:
1. A arrives first: state = "a"
2. B arrives: insert("b", 0) BUT A already inserted at 0
3. Transform B: insert("b", 1) → "ab"
```

```python
def transform(op1, op2):
    """
    Transform op2 given that op1 has already been applied.
    
    Complexity: O(1) per operation
    But: Need to track all pending operations
    """
    if op1.type == 'insert' and op2.type == 'insert':
        if op2.position >= op1.position:
            # Shift op2 right because op1 added a character before
            return Insert(op2.char, op2.position + 1)
        else:
            return op2  # op2 comes before, no change
            
    if op1.type == 'insert' and op2.type == 'delete':
        if op2.position >= op1.position:
            return Delete(op2.position + 1)
        else:
            return op2
    
    # ... more cases for delete × delete, etc.
```

**Pros**: Well-understood, used by Google Docs  
**Cons**: Complex transformation rules, centralized

### 4.2 CRDT (Conflict-free Replicated Data Types)

**Concept**: Design data structure that can merge without conflicts

```python
class RGA:
    """
    Replicated Growable Array - CRDT for text.
    
    Each character has unique ID = (timestamp, node_id)
    Insert: Add between two existing IDs
    Delete: Mark as tombstone (don't actually remove)
    
    Merge: Sort by ID → deterministic order
    """
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.sequence = []  # [(id, char, deleted), ...]
        self.clock = 0
    
    def insert(self, position, char):
        self.clock += 1
        new_id = (self.clock, self.node_id)
        
        # Find position in sequence
        left_id = self.get_id_at(position - 1)
        right_id = self.get_id_at(position)
        
        # Insert with ID
        self.sequence.insert(position, (new_id, char, False))
        
        # Broadcast to other nodes
        return InsertOp(new_id, left_id, right_id, char)
    
    def merge(self, op):
        """
        When receiving op from another node:
        - Find position based on left_id, right_id
        - Insert maintaining ID order
        - Deterministic because IDs are unique and ordered
        """
        # Find correct position
        position = self.find_position(op.left_id, op.right_id, op.id)
        self.sequence.insert(position, (op.id, op.char, False))
```

**Pros**: No central server needed, eventually consistent  
**Cons**: Storage overhead (tombstones), complex

### OT vs CRDT Comparison

| Aspect | OT | CRDT |
|--------|----|----- |
| **Central server** | Required | Optional |
| **Complexity** | In transformation | In data structure |
| **Storage** | Efficient | Tombstones overhead |
| **Real-world** | Google Docs | Figma, Notion |

---

## 📈 Phase 5: Scaling, Consistency, Failure Modes

### Sharding strategy

- Route connections by `doc_id` to keep all ops of a doc on the same shard (sticky routing).
- Hot documents (very popular) → split by **doc_id + room instance** + use CRDT merge (advanced).

### Reliability patterns

- **Op log**: append-only log per document (Kafka topic partitioned by doc_id hoặc DB table).
- **Snapshotting**: periodic snapshot (e.g., every 30s hoặc every N ops) để replay nhanh.
- **Backpressure**: nếu client spam ops → server rate limit per connection.

### Failure scenarios

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Gateway node crash | users reconnect | stateless gateway + reconnect token |
| Partition / high latency | diverged states | CRDT merge, OT rebase on reconnect |
| Message loss | missing ops | op log with ack + replay |
| Duplicate ops (retry) | double-apply | op_id idempotency + dedupe set |

---

## 📊 Observability

Metrics:
- `collab_ops_in_total{type}` / `collab_ops_out_total{type}`
- `collab_op_latency_ms` (p50/p95/p99)
- `ws_connections_active`, `ws_reconnect_total`
- `doc_snapshot_age_seconds`, `oplog_lag_seconds`

Logs/Tracing:
- Trace per op: `receive → validate → transform/merge → persist → publish`
- Log `doc_id`, `user_id` (hashed), `op_id`, `server_seq`, `client_seq`

---

## 💡 Phase 6: Interview Tips

**Key insight**: Đây là bài về distributed systems, không phải về text editing.

**Red flags**:
❌ "Just lock the document" - defeats purpose  
❌ "Last write wins" - loses data  
❌ Not considering network partition  

### 🔄 Presence & Cursor Synchronization

```python
class PresenceManager:
    """
    Real-time presence tracking for collaborative editing.
    Show who's online and where their cursor is.
    """
    
    def __init__(self, redis, document_id):
        self.redis = redis
        self.doc_id = document_id
        self.presence_key = f"presence:{document_id}"
        self.cursor_key = f"cursors:{document_id}"
    
    async def join(self, user_id, user_info):
        """User opens document."""
        await self.redis.hset(
            self.presence_key,
            user_id,
            json.dumps({
                'user_id': user_id,
                'name': user_info['name'],
                'color': self._assign_color(user_id),
                'joined_at': time.time()
            })
        )
        await self.redis.expire(self.presence_key, 3600)
        
        # Broadcast to other users
        await self._broadcast('user_joined', {'user_id': user_id})
    
    async def update_cursor(self, user_id, position):
        """Update cursor position for user."""
        await self.redis.hset(
            self.cursor_key,
            user_id,
            json.dumps({
                'position': position,
                'updated_at': time.time()
            })
        )
        
        # Broadcast cursor update
        await self._broadcast('cursor_moved', {
            'user_id': user_id,
            'position': position
        })
    
    async def get_all_cursors(self):
        """Get all active cursors for rendering."""
        cursors = await self.redis.hgetall(self.cursor_key)
        return {
            user_id: json.loads(data) 
            for user_id, data in cursors.items()
        }
```

### ⚠️ Conflict Resolution Edge Cases

| Scenario | Problem | Solution |
|----------|---------|----------|
| **Same position, same time** | Whose edit wins? | Deterministic tie-breaking (lower node_id first) |
| **Delete + Edit same range** | Edit lost? | Transform delete around edit |
| **Undo with concurrent edits** | Undo what exactly? | Undo transforms against concurrent ops |
| **Network partition heals** | Diverged documents | Merge with CRDT, or server rebases OT |
| **High latency user** | Very stale view | Show "syncing" indicator, batch transforms |

### 🌍 Real-World Case Study: Figma

| Aspect | Figma's Approach | Learning |
|--------|------------------|----------|
| **Data model** | CRDT (custom implementation) | More scalable than OT for design tools |
| **Multiplayer** | WebSocket + operational sync | Real-time with <100ms propagation |
| **Presence** | Cursor colors, avatar on selection | Social presence = engagement |
| **Offline** | Full offline editing, sync on reconnect | CRDT enables true offline-first |
| **Versioning** | Automatic snapshots every 30min | Time travel for design history |

**Key Takeaways:**
1. **CRDT for complex data** - Better for non-linear structures like designs
2. **Presence matters** - Seeing collaborators is half the experience
3. **Offline-first design** - CRDT shines when network is unreliable
4. **Server still useful** - Permissions, history, initial sync

# 17. Commenting System

> **Ví dụ thực tế**: WEBTOON comments, Facebook, Reddit

## 🎯 Phase 1: Requirements

- **FR1**: Post/edit/delete comments
- **FR2**: Nested replies (threading)
- **FR3**: Like/dislike
- **FR4**: Real-time updates
- **NFR1**: 500M comments/day write
- **NFR2**: Content moderation

### Clarifying Questions

| Câu hỏi | Vì sao quan trọng | Giả định |
|--------|--------------------|----------|
| Consistency cho counts (like/reply)? | Denormalization vs realtime count | Eventual OK |
| Sorting cần gì? newest/popular/relevant? | Index + precompute | Có cả 3 |
| Thread depth tối đa? | UX + query complexity | Max 10 |
| Edit window? | Anti-abuse + storage | 5 phút |
| Real-time bắt buộc cho mọi content? | Chi phí WebSocket | Chỉ hot content |

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- 500M comments/day ≈ 5,800 writes/sec average
- Peak 10x → ~58K writes/sec
- Read QPS thường lớn hơn write (feed/timeline) → assume 10x reads

Hệ quả:
- Data model phải tối ưu **append writes** + **pagination reads**.
- Hot content cần cache + fanout/push có kiểm soát.

---

## 🏗️ Phase 3: High-Level Design

```
┌──────────┐   ┌──────────────┐   ┌──────────────────────┐
│ Clients  │──▶│ API Gateway    │──▶│ Comment Service       │
└──────────┘   │ (auth, rate)   │   │ (write/read APIs)     │
         └──────┬────────┘   └──────────┬───────────┘
             │                       │
             │                       ├──────────────┐
             ▼                       ▼              ▼
         ┌──────────────┐      ┌──────────────┐  ┌──────────────┐
         │ Redis Cache   │      │ Primary DB    │  │ Search/Rank   │
         │ (hot threads) │      │ (writes)      │  │ (ES/feature)  │
         └──────────────┘      └──────────────┘  └──────────────┘
                            │
                            ▼
                        ┌──────────────┐
                        │ Replicas      │
                        │ (reads)       │
                        └──────────────┘

Async:
- Moderation pipeline (rules + ML)
- Notifications (replies, mentions)
- Analytics stream (Kafka)
```

> 💡 Design split: write path tối ưu cho throughput; read path tối ưu cho UX (cache + precompute).

---

## Deep Reading Notes (Q17)

- Hot path (write): validate/rate limit → write comment (append) → emit event (Kafka) → async: moderation, counters, notifications.
- Hot path (read): check cache page-1 → DB/query + rank → return + cache.
- Invariants:
    - No duplicate reactions: `(comment_id, user_id)` unique.
    - Soft delete rules: deleted comments không “biến mất” làm hỏng thread shape.
    - Moderation state machine rõ ràng (visible/pending/hidden/deleted).
- 3 trade-offs:
    - Fan-out on write (WS push) vs pull (polling): realtime UX vs write amplification.
    - Materialized path vs adjacency list: read simplicity vs update complexity.
    - Sync moderation vs async moderation: safety vs latency.
- Failure drills:
    - Moderation service down 30 phút: bạn chuyển sang chế độ nào để giảm spam?
    - Hot post 10M viewers: bạn cache/rate-limit/paginate thế nào để DB không chết?

## 🔬 Phase 4: Deep Dive

### 4.0 API Contract + Data Model (để bài “sâu” như Q12)

**Core APIs** (tối thiểu đủ interview):

```http
POST /contents/{content_id}/comments
GET  /contents/{content_id}/comments?sort=newest&limit=50&cursor=...
POST /comments/{comment_id}/reactions
DELETE /comments/{comment_id}
```

**Pagination**: dùng cursor-based (đừng offset cho hot threads).
- Cursor có thể encode `(created_at, comment_id)` hoặc `(rank_score, comment_id)` tuỳ sort.

**Schema (Postgres example)**:

```sql
CREATE TABLE comments (
    comment_id BIGSERIAL PRIMARY KEY,
    content_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_id BIGINT,
    path TEXT,                              -- materialized path (optional)
    body TEXT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'VISIBLE',  -- VISIBLE/PENDING/HIDDEN/DELETED
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comments_content_created ON comments (content_id, created_at DESC, comment_id DESC);
CREATE INDEX idx_comments_parent ON comments (content_id, parent_id, created_at DESC);
CREATE INDEX idx_comments_path_prefix ON comments (content_id, path);

CREATE TABLE comment_reactions (
    comment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction VARCHAR(16) NOT NULL,          -- like/dislike/etc.
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (comment_id, user_id)
);

-- Denormalized counters (avoid COUNT(*) on hot paths)
CREATE TABLE comment_counters (
    comment_id BIGINT PRIMARY KEY,
    reply_count BIGINT NOT NULL DEFAULT 0,
    like_count BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Cursor query (newest)**:

```sql
SELECT *
FROM comments
WHERE content_id = $1
    AND status IN ('VISIBLE','PENDING')
    AND (created_at, comment_id) < ($2, $3)  -- cursor
ORDER BY created_at DESC, comment_id DESC
LIMIT $4;
```

### 4.1 Threading Model

```
Approach 1: Adjacency List
comment_id | parent_id | content
1          | NULL      | "Great episode!"
2          | 1         | "I agree"
3          | 1         | "Same here"
4          | 2         | "Me too"

Pros: Simple
Cons: N+1 queries to build tree

Approach 2: Materialized Path
comment_id | path        | content
1          | "1"         | "Great episode!"
2          | "1.2"       | "I agree"
3          | "1.3"       | "Same here"
4          | "1.2.4"     | "Me too"

Query all replies: WHERE path LIKE '1.%'
Pros: Single query
Cons: Path length limit, update complexity
```

### 4.2 Fan-out cho Hot Content

```
Popular WEBTOON episode:
- 10M readers
- 100K comments in 1 hour

Problem: All 10M users polling for new comments = 10M QPS!

Solution: Fan-out on write
1. New comment posted
2. Push to all active WebSocket connections
3. Cache recent comments in Redis
4. Lazy load older comments

Trade-off:
- Hot content: Push (real-time but high write amplification)
- Cold content: Pull (on-demand, lower cost)
```

### 4.3 Content Moderation

```python
class ModerationPipeline:
    """
    Multi-stage moderation:
    1. Keyword filter (fast, sync)
    2. ML model (medium, async)
    3. Human review (slow, for edge cases)
    """
    
    async def moderate(self, comment):
        # Stage 1: Blocklist check (sync, <1ms)
        if self.contains_blocked_words(comment.text):
            return ModResult.BLOCK_IMMEDIATELY
        
        # Stage 2: Spam detection (sync, <10ms)
        spam_score = self.spam_classifier.predict(comment.text)
        if spam_score > 0.9:
            return ModResult.BLOCK_IMMEDIATELY
        
        # Stage 3: ML toxicity (async, ~100ms)
        # Comment goes live, checked in background
        asyncio.create_task(self.async_ml_check(comment))
        
        return ModResult.ALLOW_PENDING_REVIEW
```

### 🗄️ Comments Database Schema

```sql
-- Comments with threading support
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    content_id VARCHAR(100) NOT NULL,      -- What this comment is on
    content_type VARCHAR(50) NOT NULL,     -- 'webtoon_episode', 'article', 'video'
    
    -- Threading
    parent_id BIGINT REFERENCES comments(id),
    root_id BIGINT,                        -- Top-level comment for this thread
    path LTREE,                            -- Materialized path: '1.2.4'
    depth INT NOT NULL DEFAULT 0,
    
    -- Content
    author_id BIGINT NOT NULL,
    body TEXT NOT NULL,
    body_html TEXT,                        -- Pre-rendered for display
    
    -- Engagement
    like_count INT DEFAULT 0,
    dislike_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    
    -- Moderation
    status VARCHAR(20) DEFAULT 'visible',  -- visible, hidden, deleted, pending
    moderation_score FLOAT,
    moderated_at TIMESTAMP,
    moderated_by VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Index for fetching comments on content
CREATE INDEX idx_comments_content ON comments (content_type, content_id, created_at DESC);

-- Index for threading queries
CREATE INDEX idx_comments_path ON comments USING GIST (path);

-- Index for author's comments
CREATE INDEX idx_comments_author ON comments (author_id, created_at DESC);

-- Comment reactions
CREATE TABLE comment_reactions (
    comment_id BIGINT NOT NULL REFERENCES comments(id),
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(10) NOT NULL,    -- 'like', 'dislike'
    created_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (comment_id, user_id)
);
```

### 📱 Notification Patterns

```python
class CommentNotificationService:
    """
    Notification strategy for comments:
    - Reply to your comment → Push notification
    - Comment on your content → Batched digest
    - Trending discussion → Optional notification
    """
    
    async def on_new_comment(self, comment):
        # 1. Notify parent comment author (high priority)
        if comment.parent_id:
            parent = await self.get_comment(comment.parent_id)
            if parent.author_id != comment.author_id:
                await self.push_realtime(
                    user_id=parent.author_id,
                    type='reply',
                    data={'comment_id': comment.id}
                )
        
        # 2. Notify content owner (batch)
        content = await self.get_content(comment.content_id)
        if content.author_id != comment.author_id:
            await self.queue_batch_notification(
                user_id=content.author_id,
                type='new_comment',
                data={'content_id': comment.content_id}
            )
        
        # 3. Check if this starts a viral thread
        if await self.is_trending_thread(comment.root_id):
            await self.notify_thread_participants(
                thread_id=comment.root_id,
                exclude=[comment.author_id]
            )
```

---

## 📈 Phase 5: Scaling, Reliability, Performance

### Sharding

- Partition/shard by `content_id` (hoặc `content_type + content_id`) để tránh cross-partition reads.
- Hot content: cache “page 1” (top N newest/popular) trong Redis.

### Hot thread handling

- WebSocket chỉ bật cho hot content (threshold theo active viewers).
- Nếu không hot: polling 15–30s hoặc long-polling để giảm chi phí.

### Like/dislike correctness

- Prevent double-like: unique `(comment_id, user_id)` trong `comment_reactions`.
- Update counters bằng async aggregation (event stream) hoặc transactional update (tốn hơn).

### Failure scenarios

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Moderation service down | spam lọt | degrade: strict rule-based, quarantine mode |
| Cache stampede | DB overload | singleflight/locks, stale-while-revalidate |
| Hot partition | p99 tăng | split cache keys, multi-replica reads |

---

## 📊 Observability

Metrics:
- `comments_created_total`, `comments_deleted_total`
- `comment_read_latency_ms` (p95/p99)
- `moderation_blocked_total`, `spam_detected_total`
- `cache_hit_rate{region}`

### 🌍 Real-World Case Study: Reddit

| Aspect | Reddit's Approach | Learning |
|--------|-------------------|----------|
| **Threading** | Infinite nesting | Limit depth for UX (max 10 levels) |
| **Voting** | Up/down affects visibility | Downvoting hides low-quality content |
| **Moderation** | Community mods + AutoMod | AI assists, humans decide edge cases |
| **Load** | Hot posts = millions of comments | Pagination + lazy load essential |
| **Real-time** | Polling, not WebSocket | Simpler at scale, ~30s delay acceptable |

**Key Takeaways:**
1. **Materialized path for threading** - Single query to fetch all replies
2. **Denormalize counts** - Don't COUNT(*) on every page load
3. **Tiered moderation** - Fast blocklist, medium ML, slow human
4. **Accept some delay** - Real-time not always necessary

# 18. Location-Based Service

> **Ví dụ thực tế**: NAVER Maps, Uber, Tinder

## 🎯 Phase 1: Understand the Problem

### Requirements
- **FR1**: Nearby search (POI) theo vị trí hiện tại
- **FR2**: Text search ("cafe near me") + filters
- **FR3**: Routing/ETA (optional trong interview tuỳ scope)
- **FR4**: Map tiles delivery
- **NFR1**: p99 latency thấp (nearby/search)
- **NFR2**: Geo-distribution + high availability

### Clarifying Questions

| Câu hỏi | Vì sao quan trọng | Giả định |
|--------|--------------------|----------|
| Use case chính: search POI hay routing? | Routing phức tạp hơn nhiều | POI search + basic routing |
| Real-time updates (traffic/vehicle)? | Streaming + TTL | Có traffic feed |
| Accuracy yêu cầu? | Geohash vs PostGIS | PostGIS for accuracy |
| Data source POI update frequency? | Ingestion pipeline | Daily + incremental |

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- 1B queries/day → ~11.6K QPS avg, peak 3x → ~35K QPS
- POI records: 200M
- Tile requests thường cao hơn search (map pan/zoom) → cache/CDN là bắt buộc

Hệ quả:
- Split control plane (ingestion/update) và data plane (serving/search).
- Heavy caching cho tiles + popular queries.

---

## 🏗️ Phase 3: High-Level Design

```
┌──────────┐   ┌───────────────┐
│ Clients  │──▶│ CDN (map tiles)│
└────┬─────┘   └──────┬────────┘
    │                 │ (tile hit)
    │ (search/routing)│
    ▼                 ▼
┌──────────────┐   ┌──────────────────┐
│ API Gateway   │──▶│ Location Service  │──┐
│ + rate limit  │   │ (nearby/bbox)     │  │
└──────────────┘   └──────────────────┘  │
                                 │
                                 ▼
                          ┌──────────────────┐
                          │ PostGIS / Geo DB  │
                          │ (spatial index)   │
                          └──────────────────┘

Optional:
- Text search: Elasticsearch (name/address)
- Routing: graph store + precomputed edges
- Traffic: Kafka stream → cache factors
```

## Deep Reading Notes (Q18)

- Hot path (nearby): request → normalize lat/lon + filters → pick candidate cells (geohash/H3) → PostGIS `ST_DWithin` / bbox query → rank → paginate.
- Hot path (tiles): client → CDN (hit) → origin tile render only on miss.
- Invariants:
    - Spatial correctness: SRID/units đúng (meters vs degrees), radius semantics consistent.
    - Privacy: location retention (TTL), access control, avoid logging raw coordinates in app logs.
    - Pagination stability: tránh duplicate/skip khi dữ liệu update (cursor + deterministic sort).
- Trade-offs:
    - Geohash prefilter + PostGIS refine vs PostGIS-only: throughput vs simplicity.
    - Cache TTL ngắn vs dài: freshness vs hit rate.
    - Single geo DB vs geo-shard: vận hành đơn giản vs latency theo region.
- Failure drills:
    - Traffic feed trễ 10 phút: degrade ETA/routing như thế nào (fallback historical, label stale)?
    - Downtown dense hotspot: giới hạn candidate set, top-K ranking, chống timeout.

## 🔬 Phase 4: Deep Dive

### 4.0 API Contract + Query Pattern (điểm để bài “sâu”)

**Serving APIs** (core):

```http
GET /nearby?lat=37.56&lon=126.97&radius_m=1000&category=cafe&limit=50&cursor=...
GET /search?q=cafe%20near%20me&lat=...&lon=...&filters=...&limit=50&cursor=...
GET /tiles/{z}/{x}/{y}.png
```

**Cursor**: tương tự Q17, cursor-based để ổn định và chống hot-page.

**PostGIS query pattern** (bbox prefilter + exact distance):

```sql
-- 1) Pre-filter bằng bounding box để tận dụng index tốt
-- 2) Refine bằng ST_DWithin (geography, meters)
-- 3) Order by distance (KNN nếu cần)

WITH q AS (
    SELECT
        ST_SetSRID(ST_MakePoint($lon, $lat), 4326)::geography AS p,
        $radius_m::double precision AS r
)
SELECT
    place_id,
    name,
    ST_Distance(location, q.p) AS distance_m
FROM places, q
WHERE
    location && ST_Expand(q.p::geometry, q.r / 111320.0)   -- approx deg expansion
    AND ST_DWithin(location, q.p, q.r)
ORDER BY distance_m ASC
LIMIT $limit;
```

**Tile caching key** (CDN/origin):
- `tile:{style}:{z}:{x}:{y}:{version}`
- Versioning cực quan trọng để invalidate khi style/data đổi.

### 4.1 Geohash

**Concept**: Encode lat/long into string → nearby locations have similar prefix

```
Seoul Station: 37.5563, 126.9723
Geohash: "wydm9"

wydm = Seoul area
wydm9 = Smaller area around Seoul Station
wydm9q = Even smaller (few blocks)

Nearby search: SELECT * FROM places 
               WHERE geohash LIKE 'wydm9%'
```

```python
def get_nearby_places(lat, lon, radius_km):
    """
    Use geohash for efficient spatial query.
    
    Precision map:
    - 4 chars: ~20km
    - 5 chars: ~2.4km
    - 6 chars: ~610m
    - 7 chars: ~76m
    """
    precision = calculate_precision(radius_km)
    center_hash = geohash.encode(lat, lon, precision)
    
    # Get neighboring geohashes (handles edge cases)
    neighbors = geohash.neighbors(center_hash)
    all_hashes = [center_hash] + neighbors
    
    # Query with IN clause
    results = db.query(
        "SELECT * FROM places WHERE geohash IN (?)",
        all_hashes
    )
    
    # Post-filter by exact distance
    return [p for p in results if haversine(lat, lon, p.lat, p.lon) <= radius_km]
```

### 4.2 Quadtree vs Geohash

| Feature | Geohash | Quadtree |
|---------|---------|----------|
| **Implementation** | String prefix | Tree structure |
| **Range query** | LIKE 'abc%' | Traverse tree |
| **Update** | O(1) | O(log n) |
| **Best for** | Database index | In-memory |

### 🗄️ Location Database Schema (PostGIS)

```sql
-- PostGIS for spatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE places (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,        -- restaurant, cafe, gas_station
    
    -- Spatial data
    location GEOGRAPHY(POINT, 4326) NOT NULL,  -- Native geo type
    geohash VARCHAR(12) NOT NULL,              -- For simple queries
    
    -- Address
    address VARCHAR(500),
    city VARCHAR(100),
    country CHAR(2),
    
    -- Metadata
    rating FLOAT,
    rating_count INT DEFAULT 0,
    price_level INT,                       -- 1-4 ($-$$$$)
    
    -- Hours (JSON for flexibility)
    opening_hours JSONB,
    
    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PostGIS spatial index (most important!)
CREATE INDEX idx_places_location ON places USING GIST (location);

-- Geohash index for simpler queries
CREATE INDEX idx_places_geohash ON places (geohash varchar_pattern_ops);

-- Category + location for filtered spatial queries
CREATE INDEX idx_places_category ON places (category);
```

```sql
-- PostGIS nearby query (more accurate than geohash)
SELECT id, name, category,
       ST_Distance(
           location,
           ST_SetSRID(ST_MakePoint(126.9723, 37.5563), 4326)
       ) as distance_meters
FROM places
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(126.9723, 37.5563), 4326),
    2000  -- 2km radius
)
AND category = 'restaurant'
AND is_active = TRUE
ORDER BY distance_meters
LIMIT 20;
```

### ⚠️ Failure Scenarios & Handling

| Failure | Impact | Mitigation |
|---------|--------|------------|
| **GPS accuracy** | Wrong location | Use multiple data sources (GPS, WiFi, cell towers) |
| **Stale location** | Show incorrect nearby | TTL on location cache, prompt refresh |
| **High density area** | Too many results | Pagination + relevance ranking |
| **Cross-boundary search** | Miss nearby locations | Query 9 geohash cells (neighbors) |

### 🌍 Real-World Case Study: Uber

| Aspect | Uber's Approach | Learning |
|--------|------------------|----------|
| **Matching** | H3 hexagonal grid | Better than geohash for uniform coverage |
| **Real-time update** | Drivers update every 4 sec | Balance freshness vs cost |
| **Surge pricing** | Per-hexagon demand tracking | Geospatial + time-series |
| **ETA calculation** | Pre-computed road network | Graph algorithms (not straight-line) |
| **Scale** | Millions of active drivers | Geosharding by region |

**Key Takeaways:**
1. **PostGIS for accuracy** - Native spatial types beat string tricks
2. **Geohash for distribution** - Shard by geohash prefix for scale
3. **Pre-compute what you can** - Road network, travel times
4. **Accept approximations** - Perfect accuracy rarely needed

---

## 📈 Phase 5: Scaling, Caching, Multi-Region

### Caching strategy

- Tiles: CDN cache (days-weeks TTL), versioned URLs.
- Nearby search: cache by `(geohash_prefix, category, filters)` TTL ngắn (30–120s).
- Traffic factors: cache TTL rất ngắn (5–30s) tuỳ feed.

### Sharding

- Shard POI DB theo geohash prefix (region shards) để locality.
- Read replicas theo region.

### Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| DB overload | p99 tăng | cache + read replicas + query limits |
| Traffic feed lag | ETA sai | stale-tolerant + fallback historical |
| Region outage | mất khu vực | geo failover + warm standby |

---

## 📊 Observability

Metrics:
- `geo_search_latency_ms` (p95/p99)
- `tiles_cdn_hit_rate`
- `postgis_query_time_ms` + slow query log
- `traffic_feed_lag_seconds`

---

# 19. Ad Serving System

> **Ví dụ thực tế**: Google Ads, Facebook Ads

## 🎯 Phase 1: Key Insight

**Ad serving = Real-time auction running 1B times/day**

Flow:
1. User loads page
2. Ad request sent (user context, page context)
3. Auction among advertisers (<50ms total)
4. Winner's ad displayed
5. Track impression, click, conversion

### Requirements
- **FR1**: Serve ad with low latency (<50ms p99)
- **FR2**: Targeting (geo, device, interests, context)
- **FR3**: Auction (RTB / internal) + pricing
- **FR4**: Budget pacing + frequency capping
- **FR5**: Measurement (impression/click/conversion)
- **NFR1**: High availability + fraud resistance

### Clarifying Questions

| Câu hỏi | Vì sao quan trọng | Giả định |
|--------|--------------------|----------|
| Auction type? (2nd price, 1st price) | Pricing + incentives | GSP/2nd price |
| Latency budget breakdown? | DSP timeout, cache strategy | 50ms end-to-end |
| Frequency cap scope? | storage per user | per user + per campaign |
| Attribution model? | reporting + pipeline | last-click + optional DDA |

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- 1B impressions/day → ~11.6K RPS avg, peak 3x → ~35K RPS
- Mỗi request cần lookup user segment + eligible campaigns

Hệ quả:
- Eligibility + ranking phải nằm trong memory/cache.
- Analytics ingestion phải async (Kafka) để không ảnh hưởng serving.

---

## 🏗️ Phase 3: High-Level Design

```
┌──────────┐   ┌──────────────┐   ┌──────────────────────┐
│ Publisher│──▶│ Ad Gateway     │──▶│ Ad Server             │
│ Page/App │   │ (auth, rate)   │   │ (eligibility+auction) │
└──────────┘   └──────┬───────┘   └──────────┬───────────┘
             │                       │
             │                       ├──────────────┐
             ▼                       ▼              ▼
         ┌──────────────┐      ┌──────────────┐  ┌──────────────┐
         │ User Profile  │      │ Campaign Cache│  │ Fraud Service │
         │ / Segments    │      │ (in-memory)   │  │ (rules+ML)    │
         └──────────────┘      └──────────────┘  └──────────────┘
             │                       │
             └──────────────┬────────┘
                      ▼
                ┌──────────────────┐
                │ Creative Store    │
                │ (CDN + assets)    │
                └──────────────────┘

Async pipeline:
- Kafka events (impression/click/conversion) → stream/batch analytics
- Budget pacing updates → push to caches
```

---

## Deep Reading Notes (Q19)

- Hot path: request → fetch user/context signals (cache) → compute eligible set → apply frequency cap → auction/rank → pick creative → respond (all within ~50ms).
- Latency budget idea: split (gateway + signals + auction + creative fetch). Anything that can’t fit must be precomputed/cached.
- Invariants:
    - Budget never overspends beyond defined tolerance (especially under retries/timeouts).
    - Frequency cap correctness per user (dedupe impressions, handle multi-device if required).
    - Auction determinism enough for debugging (log winning reasons safely).
- Trade-offs:
    - 2nd-price vs 1st-price: simplicity/incentives vs revenue predictability.
    - Strongly consistent pacing counters vs eventual: spend accuracy vs serving latency.
    - On-request feature compute vs precomputed segments: freshness vs tail latency.
- Failure drills:
    - DSP/feature store timeout: fallback to contextual ads / house ads; enforce hard deadline.
    - Cache stale budgets: how do you prevent runaway overspend (circuit breaker, lower caps)?
    - Fraud spike: isolate suspicious traffic, degrade ML → rules, protect p99.

## 🔬 Phase 4: Deep Dive

### 4.0 Core Data Model + Auction Algorithm (điểm ăn trong interview)

Bạn sẽ được đánh giá cao nếu nói được “source of truth” của campaign/budget/targeting nằm ở đâu và serving dùng cache gì.

```sql
-- Campaign entities (simplified)
CREATE TABLE campaigns (
    campaign_id BIGSERIAL PRIMARY KEY,
    advertiser_id BIGINT NOT NULL,
    objective VARCHAR(32) NOT NULL,          -- clicks/conversions/impressions
    daily_budget_cents BIGINT NOT NULL,
    status VARCHAR(16) NOT NULL,             -- ACTIVE/PAUSED/ENDED
    start_at TIMESTAMP,
    end_at TIMESTAMP
);

CREATE TABLE creatives (
    creative_id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    asset_url TEXT NOT NULL,
    width INT, height INT,
    status VARCHAR(16) NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Targeting rules: stored in DB, compiled into in-memory/Redis structures for serving
CREATE TABLE targeting_rules (
    rule_id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    country CHAR(2),
    device VARCHAR(16),
    segments JSONB,                           -- interests, lookalikes, etc.
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Frequency cap key** (serving hot path):
- `fc:{user_id}:{campaign_id}` → count + TTL(window)

**Auction pseudo-code (GSP-like)**:

```python
def serve_ad(req):
    # 0) Hard deadline: stop work at ~45ms, keep 5ms for network
    deadline_ms = 45

    user = get_user_signals(req)                # cache
    candidates = eligible_campaigns(req, user)  # precomputed/in-memory

    # 1) Apply frequency cap + budget allowance
    candidates = [c for c in candidates if freq_ok(req.user_id, c.id)]
    candidates = [c for c in candidates if pacing_allows(c.id)]

    # 2) Score & pick winner
    scored = []
    for c in candidates:
        quality = quality_score(req, c)  # cached model / rules
        scored.append((c.bid * quality, c, quality))
    scored.sort(reverse=True)

    winner = scored[0]
    price = compute_second_price(scored)  # GSP-ish

    # 3) Emit impression event async (must be idempotent)
    emit_impression(winner, price, req.request_id)
    return build_response(winner.creative, price)
```

Key invariants you can say out loud:
- Impression/click events must be idempotent (retry-safe), otherwise spend & caps drift.
- Serving chooses within deadline; “no ad” is better than tail latency.

### 4.1 Real-Time Bidding (RTB)

```
        ┌──────────┐
        │   User   │
        │ loads    │
        │ page     │
        └────┬─────┘
             │
             ▼
        ┌──────────────┐
        │  Publisher   │
        │  (website)   │
        └──────┬───────┘
               │ Ad request
               ▼
        ┌──────────────┐
        │  Ad Server   │ ◀─────────────────────────┐
        │              │                           │
        └──────┬───────┘                           │
               │ Auction request                   │ Winning
               │ (parallel to DSPs)                │ ad
         ┌─────┼─────┐                             │
         ▼     ▼     ▼                             │
      ┌─────┐┌─────┐┌─────┐                        │
      │DSP 1││DSP 2││DSP 3│ (Demand Side          │
      │     ││     ││     │  Platforms)            │
      └──┬──┘└──┬──┘└──┬──┘                        │
         │     │     │                             │
         │ Bid │ Bid │ Bid                         │
         └─────┴─────┴────────────────────────────►│
```

### 4.2 Fraud Detection

```python
class FraudDetector:
    """
    Ad fraud costs industry $100B/year.
    
    Types:
    1. Bot traffic (fake impressions)
    2. Click farms (fake clicks)
    3. Domain spoofing (fake premium sites)
    """
    
    def is_fraud(self, request):
        # 1. IP reputation
        if self.is_datacenter_ip(request.ip):
            return True
        
        # 2. Device fingerprint anomaly
        if self.fingerprint_seen_too_often(request.device_id):
            return True
        
        # 3. Behavior analysis
        if self.click_rate_abnormal(request.user_id):
            return True
            
        # 4. ML model for sophisticated fraud
        fraud_score = self.ml_model.predict(request.features)
        return fraud_score > 0.8
```

### 🗄️ Ad Metrics Database Schema

```sql
-- Ad campaigns and performance tracking
CREATE TABLE campaigns (
    id BIGSERIAL PRIMARY KEY,
    advertiser_id BIGINT NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    -- Targeting
    target_audience JSONB,             -- age, gender, interests
    target_locations JSONB,            -- countries, cities, geohash
    target_keywords TEXT[],
    
    -- Budget
    daily_budget DECIMAL(12, 2) NOT NULL,
    total_budget DECIMAL(12, 2),
    bid_strategy VARCHAR(20) NOT NULL, -- CPC, CPM, CPA
    max_bid DECIMAL(10, 4),
    
    -- Status
    status VARCHAR(20) DEFAULT 'ACTIVE',
    start_date DATE,
    end_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Real-time metrics (time-series)
CREATE TABLE ad_impressions (
    campaign_id BIGINT NOT NULL,
    ad_id BIGINT NOT NULL,
    
    -- When/where
    impression_time TIMESTAMP NOT NULL,
    publisher_id BIGINT NOT NULL,
    placement_id VARCHAR(100),
    
    -- User context (anonymized)
    user_segment VARCHAR(50),
    device_type VARCHAR(20),
    country CHAR(2),
    
    -- Result
    won_auction BOOLEAN,
    winning_bid DECIMAL(10, 6),
    was_clicked BOOLEAN DEFAULT FALSE,
    was_converted BOOLEAN DEFAULT FALSE,
    
    -- Fraud signal
    fraud_score FLOAT,
    is_valid BOOLEAN DEFAULT TRUE
) PARTITION BY RANGE (impression_time);

-- Create daily partitions
CREATE TABLE ad_impressions_2024_01_01 
    PARTITION OF ad_impressions 
    FOR VALUES FROM ('2024-01-01') TO ('2024-01-02');

-- Aggregated metrics (for dashboards)
CREATE MATERIALIZED VIEW campaign_daily_metrics AS
SELECT 
    campaign_id,
    DATE(impression_time) as date,
    COUNT(*) as impressions,
    COUNT(*) FILTER (WHERE was_clicked) as clicks,
    COUNT(*) FILTER (WHERE was_converted) as conversions,
    SUM(winning_bid) as spend,
    AVG(fraud_score) as avg_fraud_score
FROM ad_impressions
WHERE is_valid = TRUE
GROUP BY campaign_id, DATE(impression_time);
```

### ⚠️ Failure Scenarios & Handling

| Failure | Impact | Mitigation |
|---------|--------|------------|
| **DSP timeout** | Lost bid opportunity | 99th percentile timeout (100ms), fallback ads |
| **Budget exhaustion** | Ads stop mid-day | Real-time budget pacing, not first-come |
| **Fraud spike** | Wasted budget | Real-time fraud ML + budget freeze |
| **Publisher outage** | No ad revenue | Multi-publisher strategy, house ads |
| **Targeting data stale** | Wrong audience | TTL on user segments, refresh on login |

### 🌍 Real-World Case Study: Google Ads

| Aspect | Google's Approach | Learning |
|--------|-------------------|----------|
| **Auction type** | Generalized Second Price | Winner pays 2nd highest bid + $0.01 |
| **Quality Score** | CTR × relevance × landing page | High quality = lower cost per click |
| **Pacing** | ML-based budget distribution | Spread evenly, not morning rush |
| **Attribution** | Last-click + data-driven | Multi-touch increasingly important |
| **Scale** | 8.5B searches/day × multiple ads | World's largest real-time auction |

**Key Takeaways:**
1. **Quality > Bid alone** - Incentivize good ads, better user experience
2. **Fraud is war** - Continuous arms race with sophisticated bots
3. **Pacing is crucial** - Don't spend budget by 10am
4. **Attribution is hard** - User sees 7 ads before converting, who gets credit?

---

## 📈 Phase 5: Scaling, Budget Pacing, Reliability

### Budget pacing (core production problem)

- Nếu chỉ deduct budget realtime theo impression/click, chiến dịch sẽ “cháy” sớm.
- Giải pháp: pacing engine tính allowance theo time-of-day + predicted traffic, rồi publish quota vào cache.

### Frequency capping

- Store per-user counters: `(user_id, campaign_id) -> count + TTL` (Redis).
- TTL theo window (e.g., 24h).

### Timeouts & fallbacks

- DSP timeout strict (e.g., 10–20ms per DSP) + parallel requests.
- Nếu timeout: fallback to house ads hoặc cached winner.

---

## 📊 Observability

Serving metrics:
- `adserve_latency_ms` (p95/p99)
- `auction_timeout_total{dsp}`
- `fill_rate` (requests served / requests)
- `invalid_traffic_rate` (fraud)

Business metrics:
- CTR, CVR, eCPM, spend pacing error

---

# 20. ML Model Serving

> **Ví dụ thực tế**: Recommendation systems, fraud detection

## 🎯 Phase 1: Key Challenges

1. **Low latency**: <10ms p99 for real-time inference
2. **A/B testing**: Multiple model versions simultaneously
3. **No downtime**: Deploy new models without interruption
4. **Drift detection**: Models degrade over time

---

## 📊 Phase 2: Capacity Estimation (5 phút)

Giả sử:
- 500M inferences/day → ~5.8K RPS avg, peak 5x → ~30K RPS
- p99 latency target: <10ms (online serving)

Hệ quả:
- Feature fetch + model inference phải nằm trong tight latency budget.
- Cần autoscale + warm models + tránh cold start.

---

## 🏗️ Phase 3: High-Level Design

```
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│ Clients  │──▶│ API Gateway   │──▶│ Model Router  │
└──────────┘   │ (auth, rate)  │   │ (A/B, canary) │
         └──────┬───────┘   └──────┬───────┘
             │                  │
             │                  ▼
             │          ┌──────────────────┐
             │          │ Model Servers     │
             │          │ (GPU/CPU pools)   │
             │          └─────────┬────────┘
             │                    │
             ▼                    ▼
         ┌──────────────┐    ┌──────────────────┐
         │ Online Feature │    │ Model Registry    │
         │ Store (Redis)  │    │ (MLflow/S3)       │
         └──────────────┘    └──────────────────┘

Async:
- Prediction logs → Kafka → monitoring/drift/labels join
```

### Latency budget (example)

```
Total p99: 10ms
- Feature fetch: 2ms
- Deserialize + preprocessing: 1ms
- Inference: 5ms
- Postprocess + response: 2ms
```

---

## Deep Reading Notes (Q20)

- Hot path: request → route (A/B/canary) → fetch features (online store) → preprocess → inference → postprocess → respond; enforce per-step deadlines.
- Invariants:
    - Feature/schema compatibility: model version must match feature definitions (avoid silent feature shift).
    - Experiment assignment stability: same user/entity consistently hits same variant within window (stickiness).
    - Reproducibility: every prediction traceable to `(model_version, feature_version, code_version)`.
    - Safety: PII in logs/feature store handled per policy.
- Trade-offs:
    - Precompute features vs on-demand: freshness vs latency.
    - Batching (GPU) vs tail latency: throughput vs p99/p999.
    - Strong consistency for router/assignment vs eventual: correctness of experiments vs availability.
- Failure drills:
    - Feature store slow/down: fallback defaults / last-known-good / degrade model; circuit breaker.
    - Model regression detected (quality/drift): fast rollback, kill switch per variant.
    - Traffic spike: shed load, prioritize critical endpoints, autoscale + warm pools.

## 🔬 Phase 4: Deep Dive

### 4.0 Serving API + Router Algorithm (để tránh nói chung chung)

**Serving API** (gRPC/HTTP đều được, nhưng phải nêu request/response fields):

```http
POST /predict
```

```json
{
    "request_id": "...",
    "entity_type": "user",
    "entity_id": "123",
    "context": {"device": "mobile", "country": "KR"},
    "features_override": null
}
```

```json
{
    "request_id": "...",
    "score": 0.873,
    "model_version": "fraud-v17",
    "feature_version": "fs-v5",
    "latency_ms": 7
}
```

**Router stickiness** (A/B/canary):

```python
def pick_variant(entity_id: str, rollout):
    # Stable bucketing to keep user in same variant
    bucket = murmur3_32(entity_id) % 10_000
    if bucket < rollout.canary_bp:   # basis points
        return rollout.canary_model
    if bucket < rollout.ab_bp:
        return rollout.ab_model
    return rollout.base_model
```

**Online Feature Store keying**:
- Key: `fs:{entity_type}:{entity_id}:{feature_version}`
- Value: packed vector + timestamp (to measure staleness)

**Prediction logging schema** (for drift + join labels):
- `(request_id, entity_id_hash, model_version, feature_version, prediction, features_digest, served_at)` → Kafka

### 4.1 Model Deployment Patterns

```
Blue-Green Deployment:
┌─────────────────┐         ┌─────────────────┐
│   Model v1      │ ◀──100%──│   Load Balancer │
│   (Blue)        │         │                 │
├─────────────────┤         │                 │
│   Model v2      │ ──0%────│                 │
│   (Green)       │         └─────────────────┘
└─────────────────┘

Switch: 0% → 100% instantly (risky but fast)


Canary Deployment:
┌─────────────────┐         ┌─────────────────┐
│   Model v1      │ ◀──95%───│   Load Balancer │
│                 │         │                 │
├─────────────────┤         │                 │
│   Model v2      │ ◀──5%────│   (gradual)     │
│   (Canary)      │         └─────────────────┘
└─────────────────┘

Switch: 5% → 10% → 25% → 50% → 100%
```

### 4.2 Feature Store

```
Problem: Training và serving dùng feature khác nhau
→ Training/Serving skew → Model performs poorly

Solution: Feature Store
┌──────────────────────────────────────────────────────┐
│                   FEATURE STORE                       │
│                                                       │
│  ┌─────────────┐    ┌─────────────┐                  │
│  │  Offline    │    │   Online    │                  │
│  │  Store      │    │   Store     │                  │
│  │  (S3/Hive)  │    │   (Redis)   │                  │
│  └──────┬──────┘    └──────┬──────┘                  │
│         │                   │                        │
│         ▼                   ▼                        │
│  ┌─────────────┐    ┌─────────────┐                  │
│  │  Training   │    │  Serving    │                  │
│  │  Pipeline   │    │  Pipeline   │                  │
│  └─────────────┘    └─────────────┘                  │
│                                                       │
│  Same feature definitions → No skew                  │
└──────────────────────────────────────────────────────┘
```

### 4.3 Model Drift Detection

```python
class DriftDetector:
    """
    Monitor model performance over time.
    
    Types of drift:
    1. Data drift: Input distribution changes
    2. Concept drift: Relationship between input/output changes
    """
    
    def check_drift(self, model_name):
        # Compare recent predictions vs training distribution
        recent_predictions = get_predictions(model_name, last_24h)
        training_distribution = get_training_distribution(model_name)
        
        # KS test for distribution comparison
        ks_statistic, p_value = ks_test(
            recent_predictions,
            training_distribution
        )
        
        if p_value < 0.05:
            alert(f"Model {model_name} shows significant drift!")
            return True
        
        return False
```

### 🗄️ Model Registry Schema

```sql
-- ML Model Registry - tracks all model versions
CREATE TABLE ml_models (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,            -- 'recommendation_v1'
    version VARCHAR(50) NOT NULL,          -- 'v2.3.1'
    
    -- Model artifacts
    artifact_path VARCHAR(500) NOT NULL,   -- S3/GCS path to model file
    artifact_size_mb INT,
    framework VARCHAR(50) NOT NULL,        -- pytorch, tensorflow, sklearn
    
    -- Training info
    training_dataset VARCHAR(500),
    training_metrics JSONB,                -- {'accuracy': 0.92, 'f1': 0.89}
    hyperparameters JSONB,
    trained_at TIMESTAMP,
    trained_by VARCHAR(100),
    
    -- Deployment status
    status VARCHAR(20) DEFAULT 'REGISTERED', -- registered, staging, production, deprecated
    promoted_at TIMESTAMP,
    deprecated_at TIMESTAMP,
    
    -- A/B test info
    traffic_percent INT DEFAULT 0,          -- 0-100
    ab_test_id VARCHAR(100),
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_model_version UNIQUE (name, version)
);

-- Model deployment history
CREATE TABLE model_deployments (
    id BIGSERIAL PRIMARY KEY,
    model_id BIGINT NOT NULL REFERENCES ml_models(id),
    
    environment VARCHAR(20) NOT NULL,       -- staging, production
    action VARCHAR(20) NOT NULL,            -- deploy, rollback, scale
    
    previous_version VARCHAR(50),
    new_version VARCHAR(50) NOT NULL,
    
    traffic_before INT,
    traffic_after INT,
    
    deployed_by VARCHAR(100),
    deployed_at TIMESTAMP DEFAULT NOW(),
    rollback_at TIMESTAMP,
    rollback_reason TEXT
);

-- Model predictions log (for monitoring)
CREATE TABLE model_predictions (
    model_id BIGINT NOT NULL,
    prediction_time TIMESTAMP NOT NULL,
    
    -- Request
    request_id UUID NOT NULL,
    features_hash VARCHAR(64),              -- Hash of input features
    
    -- Prediction
    prediction JSONB NOT NULL,
    confidence FLOAT,
    latency_ms INT,
    
    -- Ground truth (filled later)
    actual_outcome JSONB,
    labeled_at TIMESTAMP,
    
    -- For drift detection
    feature_stats JSONB                     -- Summary stats of features
) PARTITION BY RANGE (prediction_time);
```

### 📊 A/B Testing Pattern

```python
class ModelABTest:
    """
    A/B test multiple model versions with traffic splitting.
    """
    
    def __init__(self, redis):
        self.redis = redis
        self.models = {}  # version -> model instance
    
    async def predict(self, model_name: str, features: dict, user_id: str):
        """
        Route prediction to appropriate model version based on:
        1. Explicit test assignment
        2. Traffic percentage
        """
        
        # Check if user already assigned to a variant
        assignment_key = f"ab:{model_name}:{user_id}"
        assigned_version = await self.redis.get(assignment_key)
        
        if not assigned_version:
            # Assign based on traffic percentages
            assigned_version = self._select_version(model_name, user_id)
            await self.redis.setex(assignment_key, 86400, assigned_version)
        
        # Get the model and predict
        model = self.models[assigned_version]
        
        start = time.time()
        prediction = model.predict(features)
        latency_ms = (time.time() - start) * 1000
        
        # Log for analysis
        await self._log_prediction(
            model_name=model_name,
            version=assigned_version,
            user_id=user_id,
            features=features,
            prediction=prediction,
            latency_ms=latency_ms
        )
        
        return {
            'prediction': prediction,
            'model_version': assigned_version,
            'latency_ms': latency_ms
        }
    
    def _select_version(self, model_name: str, user_id: str) -> str:
        """
        Deterministic assignment based on user_id hash.
        Ensures same user always gets same variant.
        """
        config = self.get_ab_config(model_name)
        
        # Hash user_id to 0-100
        bucket = hash(user_id) % 100
        
        # Assign to variant based on traffic %
        cumulative = 0
        for version, percent in config.items():
            cumulative += percent
            if bucket < cumulative:
                return version
        
        return config['default']
```

## 📊 Observability (Serving + ML Quality)

Serving SLO metrics:
- `inference_latency_ms{model,version}` (p50/p95/p99)
- `inference_errors_total{model,reason}`
- `feature_fetch_latency_ms` + `feature_cache_hit_rate`
- `gpu_utilization`, `gpu_oom_total`, `container_restarts_total`

Model quality/drift:
- Prediction distribution stats (mean/std/quantiles)
- Drift tests (KS/PSI) per feature + per output
- Online metrics (CTR, conversion, fraud catch rate) split by variant

---

### ⚠️ Failure Scenarios & Handling

| Failure | Detection | Impact | Recovery |
|---------|-----------|--------|----------|
| **Model OOM** | Container killed | Predictions fail | Auto-restart, reduce batch size |
| **Feature service down** | Timeout | No features | Use cached/default features |
| **New model worse** | Metrics drop in A/B | User experience degrades | Auto-rollback when metrics < threshold |
| **Training drift** | KS test fails | Predictions inaccurate | Alert ML team, retrain trigger |
| **GPU unavailable** | Pod pending | No predictions | Fallback to CPU model (slower) |

```python
class ModelServingWithFallback:
    """
    Production model serving with graceful degradation.
    """
    
    def __init__(self):
        self.primary_model = load_model('v2.3.1', device='gpu')
        self.fallback_model = load_model('v2.2.0', device='cpu')
        self.default_predictions = load_defaults()
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
    
    async def predict(self, features: dict):
        # Try primary model
        if self.circuit_breaker.is_closed():
            try:
                return await asyncio.wait_for(
                    self.primary_model.predict(features),
                    timeout=0.1  # 100ms timeout
                )
            except (TimeoutError, GPUError) as e:
                self.circuit_breaker.record_failure()
                logger.warning(f"Primary model failed: {e}")
        
        # Try fallback model
        try:
            return await self.fallback_model.predict(features)
        except Exception as e:
            logger.error(f"Fallback model failed: {e}")
        
        # Return cached/default predictions
        return self.default_predictions.get(
            features.get('category'),
            self.default_predictions['global']
        )
```

### 🌍 Real-World Case Study: Netflix Recommendations

| Aspect | Netflix's Approach | Learning |
|--------|-------------------|----------|
| **Scale** | 250M members, billions of recommendations/day | Need massive parallelization |
| **Latency** | <100ms for personalized row | Pre-compute + real-time hybrid |
| **Models** | 100s of models in production | Each row/ranking is different model |
| **A/B testing** | Always running 100+ tests | Every change is an experiment |
| **Feature store** | Shared features across models | Consistency critical |

**Their Stack:**
- **Metaflow**: ML workflow orchestration  
- **Feature Store**: Centralized feature management  
- **Meson**: A/B testing platform  
- **Model Registry**: Track all model versions  

**Key Takeaways:**
1. **Everything is an experiment** - Never ship without A/B test
2. **Feature store is critical** - Training/serving skew kills models
3. **Monitoring > Training** - Models in production need constant watching
4. **Fallbacks everywhere** - Grace degradation when ML fails
5. **Pre-compute when possible** - Real-time is expensive

### 💡 Interview Tips for ML Systems

**Common Questions:**
1. *"How do you detect model degradation?"*
   - Monitor prediction distribution (KS test)
   - Track business metrics (CTR, conversion)
   - Compare against holdout baseline

2. *"Training vs Serving - what's different?"*
   - Latency requirements
   - Feature availability
   - Batch vs single prediction

3. *"How to roll back a bad model?"*
   - Feature flags for instant switch
   - Model registry with version history
   - Automated rollback on metric drop

**Red Flags:**
❌ No A/B testing for model changes  
❌ Different feature code for training/serving  
❌ No monitoring for model drift  
❌ No fallback for model failures

# Tổng Kết

## Quick Reference Table

| # | System | Core Challenge | Key Concepts |
|---|--------|----------------|--------------|
| 11 | Autocomplete | Low latency search | Trie, Caching, Ranking |
| 12 | Payment | Exactly-once | Idempotency, Saga, Ledger |
| 13 | Cache | Distribution | Consistent Hash, Eviction |
| 14 | Rate Limiter | Fairness | Token Bucket, Sliding Window |
| 15 | Transcoding | Parallel processing | FFmpeg, HLS, Queue |
| 16 | Collab Edit | Conflict resolution | OT, CRDT |
| 17 | Comments | Scale writes | Fan-out, Moderation |
| 18 | Location | Spatial query | Geohash, Quadtree |
| 19 | Ad Serving | Real-time auction | RTB, Fraud detection |
| 20 | ML Serving | Safe deployment | A/B, Feature Store, Drift |

## Universal Interview Tips

1. **Always clarify requirements first**
2. **Do capacity estimation** (QPS, storage, bandwidth)
3. **Start high-level, then deep dive**
4. **Discuss trade-offs for every decision**
5. **Consider failure scenarios**
6. **Know when to stop and move on**

---

> 💡 **Cách học hiệu quả**: Với mỗi system, thử tự thiết kế TRƯỚC khi đọc solution. So sánh approach của bạn với solution để học từ differences.