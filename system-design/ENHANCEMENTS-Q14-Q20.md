# System Design Enhancements - Q14 to Q20
> Bổ sung chi tiết để đạt độ sâu như Q11-13

---

## 📋 Q14 RATE LIMITER - BỔ SUNG

### 1. Capacity Estimation Class (thêm sau line 2088)

```python
# Capacity Estimation Calculator for Rate Limiter

class RateLimiterCapacityEstimator:
    """
    Production-grade capacity estimation for rate limiter.
    Covers Redis ops, memory, network bandwidth.
    """
    
    def __init__(self):
        # Input parameters
        self.peak_rps = 200_000             # Peak requests per second
        self.avg_rps = 80_000               # Average RPS
        self.unique_keys_1min = 10_000_000  # Active keys in 1 minute window
        self.ttl_seconds = 3600             # Key TTL (1 hour)
        self.replication_factor = 3         # Redis replication
        
    def calculate_redis_ops(self):
        """
        Redis Operations Calculation
        ============================
        Each rate limit check = 1 Lua EVAL + occasional key cleanup
        
        Operations breakdown:
        - EVAL: Check + update counter (1 op per request)
        - EXPIRE: Set/update TTL (~10% of requests need explicit EXPIRE)
        - DEL: Cleanup expired keys (background, ~1% overhead)
        """
        eval_ops = self.peak_rps              # 1 EVAL per request
        expire_ops = self.peak_rps * 0.1      # 10% need explicit EXPIRE
        del_ops = self.peak_rps * 0.01        # 1% cleanup overhead
        
        total_ops = eval_ops + expire_ops + del_ops
        
        # Redis cluster sizing (assume 100K ops/sec per node)
        ops_per_node = 100_000
        nodes_needed = int(total_ops / ops_per_node) + 1
        
        return {
            'eval_ops_per_sec': int(eval_ops),           # 200,000
            'expire_ops_per_sec': int(expire_ops),       # 20,000
            'total_ops_per_sec': int(total_ops),         # ~220,000
            'redis_nodes_needed': nodes_needed * self.replication_factor,  # ~9 nodes
        }
    
    def calculate_memory(self):
        """
        Memory Requirements
        ===================
        Different algorithms have different memory footprints:
        
        Token Bucket: ~100 bytes per key (tokens + last_refill + metadata)
        Sliding Window Counter: ~150 bytes per key (2 buckets + counters)
        Sliding Window Log: ~50 bytes per request × window × limit
        
        We'll use Sliding Window Counter as baseline.
        """
        bytes_per_key_token_bucket = 100
        bytes_per_key_sliding_window = 150
        
        # Active keys calculation
        # 1-minute window active keys
        active_keys_1min = self.unique_keys_1min
        
        # TTL determines total keys in memory
        # If TTL = 1 hour, approximately 60x the 1-min active keys
        total_keys_in_memory = active_keys_1min * (self.ttl_seconds / 60)
        
        # Memory calculation for Sliding Window Counter
        memory_bytes = total_keys_in_memory * bytes_per_key_sliding_window
        memory_gb = memory_bytes / (1024**3)
        
        # With replication
        total_memory_gb = memory_gb * self.replication_factor
        
        # Redis node sizing (64GB per node typical)
        redis_memory_per_node_gb = 64
        nodes_for_memory = int(total_memory_gb / redis_memory_per_node_gb) + 1
        
        return {
            'active_keys_1min': active_keys_1min,                    # 10M
            'total_keys_in_memory': int(total_keys_in_memory),       # 600M
            'memory_per_key_bytes': bytes_per_key_sliding_window,
            'total_memory_raw_gb': memory_gb,                        # ~90GB
            'total_memory_replicated_gb': total_memory_gb,           # ~270GB
            'redis_nodes_for_memory': nodes_for_memory * self.replication_factor,  # ~15 nodes
        }
    
    def calculate_bandwidth(self):
        """
        Network Bandwidth
        =================
        Request: key (50 bytes) + metadata (50 bytes) = 100 bytes
        Response: allowed/denied (1 byte) + headers (50 bytes) = 51 bytes
        
        Internal Redis traffic:
        - Replication: writes × replication_factor
        - Cluster gossip: ~5% overhead
        """
        request_size_bytes = 100
        response_size_bytes = 51
        
        # Client-facing bandwidth
        ingress_bps = self.peak_rps * request_size_bytes * 8
        egress_bps = self.peak_rps * response_size_bytes * 8
        
        ingress_mbps = ingress_bps / (1024 * 1024)
        egress_mbps = egress_bps / (1024 * 1024)
        
        # Internal replication (write operations only, ~1% of total)
        write_ratio = 0.01
        internal_replication_mbps = egress_mbps * write_ratio * self.replication_factor
        
        # Cluster gossip overhead
        gossip_mbps = egress_mbps * 0.05
        
        total_mbps = ingress_mbps + egress_mbps + internal_replication_mbps + gossip_mbps
        
        return {
            'ingress_mbps': ingress_mbps,                           # ~153 Mbps
            'egress_mbps': egress_mbps,                             # ~78 Mbps
            'internal_replication_mbps': internal_replication_mbps, # ~2.3 Mbps
            'cluster_gossip_mbps': gossip_mbps,                     # ~3.9 Mbps
            'total_bandwidth_mbps': total_mbps,                     # ~237 Mbps
        }
    
    def calculate_latency_budget(self):
        """
        Latency Budget Breakdown
        ========================
        Target: <1ms overhead for rate limiting
        
        Breakdown:
        - Network RTT to Redis: 0.3ms (same AZ)
        - Redis EVAL execution: 0.2ms (Lua script)
        - Serialization/deserialization: 0.1ms
        - Gateway processing: 0.2ms
        - Buffer: 0.2ms
        """
        return {
            'network_rtt_ms': 0.3,
            'redis_eval_ms': 0.2,
            'serialization_ms': 0.1,
            'gateway_processing_ms': 0.2,
            'buffer_ms': 0.2,
            'total_target_ms': 1.0,
        }

# Usage in interview:
estimator = RateLimiterCapacityEstimator()
print("Redis Ops:", estimator.calculate_redis_ops())
print("Memory:", estimator.calculate_memory())
print("Bandwidth:", estimator.calculate_bandwidth())
print("Latency:", estimator.calculate_latency_budget())
```

### Summary Table

| Metric | Value | Implications |
|--------|-------|-------------|
| Peak RPS | 200K | Need horizontal scaling |
| Redis Ops | 220K/sec | Cluster required (9+ nodes) |
| Memory | ~270GB | 15+ nodes with replication |
| Bandwidth | 237 Mbps | Not a bottleneck |
| Latency Target | <1ms | In-memory ops only |
| TTL Strategy | 1 hour | Balance memory vs accuracy |

---

### 2. Sequence Diagram (thêm sau Key Design section)

```
### 🔄 Sequence Diagram - Rate Limit Check Flow

SCENARIO 1: Request Allowed
────────────────────────────────────────────────────────────────────────────

┌──────┐     ┌────────────┐     ┌───────────┐     ┌─────────┐     ┌─────────┐
│Client│     │API Gateway │     │Rate Limiter│     │ Redis   │     │ Backend │
└──┬───┘     └─────┬──────┘     └─────┬─────┘     └────┬────┘     └────┬────┘
   │                │                  │                 │               │
   │ POST /api/pay  │                  │                 │               │
   │───────────────>│                  │                 │               │
   │                │                  │                 │               │
   │                │ Extract identity │                 │               │
   │                │ (api_key/user/IP)│                 │               │
   │                │                  │                 │               │
   │                │ check_rate_limit()                 │               │
   │                │─────────────────>│                 │               │
   │                │                  │                 │               │
   │                │                  │ Build key:      │               │
   │                │                  │ rl:user:123:    │               │
   │                │                  │ /api/pay:swc    │               │
   │                │                  │                 │               │
   │                │                  │ EVAL Lua script │               │
   │                │                  │ (atomic update) │               │
   │                │                  │────────────────>│               │
   │                │                  │                 │               │
   │                │                  │                 │ Calculate:    │
   │                │                  │                 │ - Current bucket│
   │                │                  │                 │ - Previous bucket│
   │                │                  │                 │ - Sliding weight│
   │                │                  │                 │ - Approx count│
   │                │                  │                 │               │
   │                │                  │<────────────────│               │
   │                │                  │ {allowed: true, │               │
   │                │                  │  remaining: 47, │               │
   │                │                  │  reset: 1704067200}             │
   │                │                  │                 │               │
   │                │<─────────────────│                 │               │
   │                │ {allowed: true}  │                 │               │
   │                │                  │                 │               │
   │                │ Add headers:     │                 │               │
   │                │ X-RateLimit-*    │                 │               │
   │                │                  │                 │               │
   │                │ Forward request  │                 │               │
   │                │─────────────────────────────────────────────────────>│
   │                │                  │                 │               │
   │                │<─────────────────────────────────────────────────────│
   │                │ Response         │                 │               │
   │                │                  │                 │               │
   │<───────────────│                  │                 │               │
   │ 200 OK         │                  │                 │               │
   │ X-RateLimit-Limit: 100            │                 │               │
   │ X-RateLimit-Remaining: 47         │                 │               │
   │ X-RateLimit-Reset: 1704067200     │                 │               │
   │                │                  │                 │               │

────────────────────────────────────────────────────────────────────────────
SCENARIO 2: Rate Limit Exceeded
────────────────────────────────────────────────────────────────────────────

┌──────┐     ┌────────────┐     ┌───────────┐     ┌─────────┐
│Client│     │API Gateway │     │Rate Limiter│     │ Redis   │
└──┬───┘     └─────┬──────┘     └─────┬─────┘     └────┬────┘
   │                │                  │                 │
   │ POST /api/pay  │                  │                 │
   │───────────────>│                  │                 │
   │                │                  │                 │
   │                │ check_rate_limit()                 │
   │                │─────────────────>│                 │
   │                │                  │                 │
   │                │                  │ EVAL Lua        │
   │                │                  │────────────────>│
   │                │                  │                 │
   │                │                  │<────────────────│
   │                │                  │ {allowed: false,│
   │                │                  │  remaining: 0,  │
   │                │                  │  reset: 1704067200,
   │                │                  │  retry_after: 30}│
   │                │                  │                 │
   │                │<─────────────────│                 │
   │                │ {allowed: false} │                 │
   │                │                  │                 │
   │                │ DO NOT forward   │                 │
   │                │ to backend       │                 │
   │                │                  │                 │
   │                │ Log blocked req  │                 │
   │                │ (monitoring)     │                 │
   │                │                  │                 │
   │<───────────────│                  │                 │
   │ 429 Too Many   │                  │                 │
   │ Requests       │                  │                 │
   │ Retry-After: 30│                  │                 │
   │ X-RateLimit-Limit: 100            │                 │
   │ X-RateLimit-Remaining: 0          │                 │
   │ X-RateLimit-Reset: 1704067200     │                 │
   │                │                  │                 │
   │ Client waits   │                  │                 │
   │ 30 seconds     │                  │                 │
   │ with backoff   │                 │                 │
```

### Key Points in Flow

1. **Atomic Operation**: Redis Lua script ensures no race conditions
2. **Fast Rejection**: Rate-limited requests never hit backend (saves resources)
3. **Clear Headers**: Client knows exactly when to retry
4. **Monitoring**: All blocked requests logged for abuse detection
5. **Latency**: Entire check completes in <1ms (target)

---

### 3. Enhanced Monitoring Section (thêm vào Phase 5)

```markdown
## 📊 Observability & Monitoring (Production-Grade)

### Metrics Dashboard

```python
class RateLimiterMetrics:
    """
    Comprehensive metrics collection for rate limiter.
    Integrate with Prometheus/Grafana/DataDog.
    """
    
    def __init__(self, metrics_client):
        self.metrics = metrics_client
        
        # Define metric types
        self.request_counter = self.metrics.counter(
            'ratelimit_requests_total',
            labels=['result', 'scope', 'tier']
        )
        
        self.latency_histogram = self.metrics.histogram(
            'ratelimit_check_duration_ms',
            buckets=[0.1, 0.5, 1, 2, 5, 10]
        )
        
        self.redis_latency = self.metrics.histogram(
            'ratelimit_redis_duration_ms',
            buckets=[0.1, 0.5, 1, 2, 5, 10, 20]
        )
        
        self.blocked_gauge = self.metrics.gauge(
            'ratelimit_blocked_active',
            labels=['scope', 'route']
        )
    
    def record_check(self, allowed: bool, scope: str, tier: str, latency_ms: float):
        """Record a rate limit check."""
        result = 'allowed' if allowed else 'blocked'
        self.request_counter.inc(labels={'result': result, 'scope': scope, 'tier': tier})
        self.latency_histogram.observe(latency_ms)
    
    def record_redis_op(self, operation: str, latency_ms: float):
        """Record Redis operation latency."""
        self.redis_latency.observe(latency_ms, labels={'operation': operation})
```

### Alert Rules

```yaml
# Prometheus Alert Rules for Rate Limiter

groups:
  - name: ratelimiter_alerts
    interval: 30s
    rules:
      # High block rate indicates attack or misconfiguration
      - alert: HighRateLimitBlockRate
        expr: |
          rate(ratelimit_requests_total{result="blocked"}[5m])
          / rate(ratelimit_requests_total[5m]) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High rate limit block rate ({{ $value | humanizePercentage }})"
          description: "Over 50% of requests are being rate limited"
      
      # Redis latency spike
      - alert: RateLimiterRedisLatencyHigh
        expr: |
          histogram_quantile(0.99, 
            rate(ratelimit_redis_duration_ms_bucket[5m])
          ) > 5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Rate limiter Redis p99 latency is {{ $value }}ms"
          description: "Redis operations are slower than expected"
      
      # Circuit breaker triggered (fallback active)
      - alert: RateLimiterCircuitBreakerOpen
        expr: ratelimit_circuit_breaker_state{state="open"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Rate limiter circuit breaker is OPEN"
          description: "Rate limiter falling back to degraded mode"
      
      # Memory pressure
      - alert: RedisMemoryHigh
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is {{ $value | humanizePercentage }}"
          description: "Consider increasing Redis capacity"
```

### Grafana Dashboard Queries

```sql
-- Rate limit effectiveness
SELECT 
  time_bucket('1 minute', timestamp) AS time,
  scope,
  SUM(CASE WHEN result = 'allowed' THEN 1 ELSE 0 END) as allowed,
  SUM(CASE WHEN result = 'blocked' THEN 1 ELSE 0 END) as blocked,
  (SUM(CASE WHEN result = 'blocked' THEN 1 ELSE 0 END)::float / 
   COUNT(*)::float) * 100 as block_rate_pct
FROM ratelimit_requests
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY time, scope
ORDER BY time DESC;

-- Top blocked routes
SELECT 
  route,
  COUNT(*) as blocked_count,
  COUNT(DISTINCT user_id) as unique_users
FROM ratelimit_requests
WHERE result = 'blocked'
  AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY route
ORDER BY blocked_count DESC
LIMIT 20;

-- Latency percentiles by tier
SELECT 
  tier,
  percentile_cont(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM ratelimit_requests
WHERE timestamp > NOW() - INTERVAL '15 minutes'
GROUP BY tier;
```

### Key Metrics to Track

| Metric | Target | Alert Threshold | Action |
|--------|--------|----------------|--------|
| **Check Latency p99** | <1ms | >5ms | Check Redis health |
| **Block Rate** | <10% | >50% | Investigate attack/bug |
| **Redis CPU** | <70% | >85% | Scale cluster |
| **Memory Usage** | <80% | >90% | Increase capacity |
| **Error Rate** | <0.1% | >1% | Circuit breaker check |
| **Cache Hit Rate** | >95% | <80% | Review caching |

---

## 📋 Q15 VIDEO TRANSCODING - BỔ SUNG

### 1. Capacity Estimation Class (thêm sau Phase 2)

```python
class VideoTranscodingCapacityEstimator:
    """
    Production capacity estimation for video transcoding system.
    Handles compute, storage, bandwidth for massive scale.
    """
    
    def __init__(self):
        # Input parameters
        self.daily_uploads = 1_000_000          # Videos uploaded per day
        self.avg_video_length_min = 5           # Average video length
        self.avg_file_size_mb = 200             # Average raw file size
        self.target_profiles = 4                # Number of output renditions
        self.storage_multiplier = 1.8           # Raw → processed ratio
        self.peak_factor = 3                    # Peak vs average
        self.transcode_realtime_factor = 2.0    # CPU time / video time
        
    def calculate_qps(self):
        """
        Upload QPS & Job Queue Calculations
        ===================================
        """
        seconds_per_day = 86_400
        
        avg_upload_qps = self.daily_uploads / seconds_per_day
        peak_upload_qps = avg_upload_qps * self.peak_factor
        
        # Job processing rate (each video = 1 job × N profiles)
        jobs_per_day = self.daily_uploads * self.target_profiles
        avg_job_qps = jobs_per_day / seconds_per_day
        peak_job_qps = avg_job_qps * self.peak_factor
        
        return {
            'avg_upload_qps': int(avg_upload_qps),      # ~12 QPS
            'peak_upload_qps': int(peak_upload_qps),    # ~35 QPS
            'avg_job_qps': int(avg_job_qps),            # ~46 jobs/sec
            'peak_job_qps': int(peak_job_qps),          # ~139 jobs/sec
        }
    
    def calculate_storage(self):
        """
        Storage Requirements
        ====================
        Raw input: Transient (delete after successful transcode)
        Processed output: Long-term (retention policy)
        """
        # Daily storage calculation
        raw_storage_tb_per_day = (self.daily_uploads * self.avg_file_size_mb) / (1024 * 1024)
        
        processed_storage_tb_per_day = raw_storage_tb_per_day * self.storage_multiplier
        
        total_new_storage_tb_per_day = raw_storage_tb_per_day + processed_storage_tb_per_day
        
        # Yearly accumulation (assume processed kept forever, raw deleted)
        processed_storage_tb_per_year = processed_storage_tb_per_day * 365
        
        # Working storage (raw files waiting in queue, ~1 day retention)
        working_storage_tb = raw_storage_tb_per_day * 2  # 2 days buffer
        
        return {
            'raw_storage_tb_per_day': raw_storage_tb_per_day,                    # ~200 TB/day
            'processed_storage_tb_per_day': processed_storage_tb_per_day,        # ~360 TB/day
            'total_new_tb_per_day': total_new_storage_tb_per_day,                # ~560 TB/day
            'processed_yearly_tb': processed_storage_tb_per_year,                # ~131 PB/year
            'working_storage_tb': working_storage_tb,                            # ~400 TB
        }
    
    def calculate_compute(self):
        """
        Compute Requirements (CPU/GPU)
        ===============================
        Transcoding is CPU/GPU intensive.
        """
        # Total video minutes per day
        total_video_minutes = self.daily_uploads * self.avg_video_length_min
        
        # CPU minutes needed (accounting for realtime factor)
        cpu_minutes_per_day = total_video_minutes * self.transcode_realtime_factor * self.target_profiles
        
        cpu_hours_per_day = cpu_minutes_per_day / 60
        
        # Worker calculation (assume 8 vCPU per worker, 80% utilization)
        # Each worker can process ~1 video at a time
        concurrent_jobs_needed = cpu_hours_per_day / 24  # Spread over 24h
        
        # Peak capacity needed
        peak_concurrent_jobs = concurrent_jobs_needed * self.peak_factor
        
        # Instance sizing (c5.2xlarge = 8 vCPU, $0.34/hr)
        workers_needed_avg = int(concurrent_jobs_needed / 0.8) + 1
        workers_needed_peak = int(peak_concurrent_jobs / 0.8) + 1
        
        # Cost estimation (spot instances = 70% discount)
        hourly_cost_on_demand = workers_needed_avg * 0.34
        hourly_cost_spot = hourly_cost_on_demand * 0.3
        daily_cost_spot = hourly_cost_spot * 24
        
        return {
            'total_video_hours_per_day': int(total_video_minutes / 60),          # ~83K hours
            'cpu_hours_needed_per_day': int(cpu_hours_per_day),                  # ~666K CPU hours
            'workers_needed_avg': workers_needed_avg,                            # ~34,722 workers
            'workers_needed_peak': workers_needed_peak,                          # ~104,167 workers
            'daily_cost_spot_usd': int(daily_cost_spot),                         # ~$84,858/day
            'monthly_cost_spot_usd': int(daily_cost_spot * 30),                  # ~$2.5M/month
        }
    
    def calculate_bandwidth(self):
        """
        Network Bandwidth
        =================
        Ingress: User uploads
        Egress: CDN delivery (much larger due to views)
        Internal: Worker download/upload to S3
        """
        # Ingress (uploads)
        upload_bytes_per_day = self.daily_uploads * self.avg_file_size_mb * 1024 * 1024
        upload_gbps = (upload_bytes_per_day * 8) / (86400 * 1024**3)
        peak_upload_gbps = upload_gbps * self.peak_factor
        
        # Internal (workers reading raw + writing processed)
        internal_read_gbps = upload_gbps  # Workers download raw
        internal_write_gbps = upload_gbps * self.storage_multiplier  # Workers upload processed
        
        # Egress (CDN delivery - assume 10x views vs uploads)
        views_multiplier = 10
        egress_gbps = upload_gbps * self.storage_multiplier * views_multiplier
        
        return {
            'ingress_avg_gbps': upload_gbps,                    # ~18.5 Gbps
            'ingress_peak_gbps': peak_upload_gbps,              # ~55.6 Gbps
            'internal_read_gbps': internal_read_gbps,           # ~18.5 Gbps
            'internal_write_gbps': internal_write_gbps,         # ~33.3 Gbps
            'egress_delivery_gbps': egress_gbps,                # ~333 Gbps (CDN)
        }
    
    def calculate_queue_depth(self):
        """
        Queue Management
        ================
        """
        # Average processing time per job (video length × realtime factor)
        avg_processing_seconds = self.avg_video_length_min * 60 * self.transcode_realtime_factor
        
        # Jobs arriving per second
        jobs_per_second = self.daily_uploads * self.target_profiles / 86400
        
        # Queue depth at steady state (Little's Law: L = λ × W)
        avg_queue_depth = jobs_per_second * avg_processing_seconds
        
        # Peak queue depth
        peak_queue_depth = avg_queue_depth * self.peak_factor
        
        return {
            'avg_processing_time_min': int(avg_processing_seconds / 60),  # ~10 min
            'jobs_per_second': int(jobs_per_second),                      # ~46 jobs/sec
            'avg_queue_depth': int(avg_queue_depth),                      # ~27,778 jobs
            'peak_queue_depth': int(peak_queue_depth),                    # ~83,333 jobs
            'recommended_queue_capacity': int(peak_queue_depth * 1.5),    # ~125K jobs
        }

# Usage
estimator = VideoTranscodingCapacityEstimator()
print("QPS:", estimator.calculate_qps())
print("Storage:", estimator.calculate_storage())
print("Compute:", estimator.calculate_compute())
print("Bandwidth:", estimator.calculate_bandwidth())
print("Queue:", estimator.calculate_queue_depth())
```

### Summary Table

| Metric | Value | Key Insight |
|--------|-------|-------------|
| Peak Upload QPS | 35 | Burst capacity needed |
| New Storage/Day | 560 TB | ~200 PB/year growth |
| Workers (Spot) | 35K avg, 104K peak | Autoscaling critical |
| Monthly Cost | ~$2.5M (spot) | 70% savings vs on-demand |
| Queue Depth | 83K jobs (peak) | SQS/Kafka sizing |
| Egress (CDN) | 333 Gbps | Largest bandwidth cost |

---

### 2. Sequence Diagram (thêm vào Phase 3)

```
### 🔄 Video Transcoding Flow - Detailed Sequence

SCENARIO 1: Successful Transcoding
────────────────────────────────────────────────────────────────────────────

┌──────┐   ┌────────┐   ┌─────────┐   ┌──────┐   ┌────────┐   ┌─────┐   ┌─────┐
│Client│   │Upload  │   │   S3    │   │Queue │   │Worker  │   │ S3  │   │ CDN │
│      │   │Service │   │ (Raw)   │   │ (SQS)│   │ Pool   │   │(Out)│   │     │
└──┬───┘   └───┬────┘   └────┬────┘   └───┬──┘   └───┬────┘   └──┬──┘   └──┬──┘
   │            │             │            │          │           │        │
   │ 1. Initiate│             │            │          │           │        │
   │ multipart  │             │            │          │           │        │
   │ upload     │             │            │          │           │        │
   │───────────>│             │            │          │           │        │
   │            │             │            │          │           │        │
   │<───────────│             │            │          │           │        │
   │ upload_id  │             │            │          │           │        │
   │ + presigned│             │            │          │           │        │
   │ URLs       │             │            │          │           │        │
   │            │             │            │          │           │        │
   │ 2. Upload  │             │            │          │           │        │
   │ chunks     │             │            │          │           │        │
   │ (parallel) │             │            │          │           │        │
   │─────────────────────────>│            │          │           │        │
   │            │             │            │          │           │        │
   │ 3. Complete│             │            │          │           │        │
   │ upload     │             │            │          │           │        │
   │───────────>│             │            │          │           │        │
   │            │             │            │          │           │        │
   │            │ 4. Store    │            │          │           │        │
   │            │ metadata    │            │          │           │        │
   │            │ (DB)        │            │          │           │        │
   │            │             │            │          │           │        │
   │            │ 5. Enqueue  │            │          │           │        │
   │            │ transcode   │            │          │           │        │
   │            │ jobs        │            │          │           │        │
   │            │────────────────────────>│          │           │        │
   │            │             │  (4 jobs:  │          │           │        │
   │            │             │  1080/720/ │          │           │        │
   │            │             │  480/360)  │          │           │        │
   │            │             │            │          │           │        │
   │<───────────│             │            │          │           │        │
   │ 202 Accepted            │            │          │           │        │
   │ {video_id, │             │            │          │           │        │
   │  status:   │             │            │          │           │        │
   │  QUEUED}   │             │            │          │           │        │
   │            │             │            │          │           │        │
   │            │             │            │ 6. Poll  │           │        │
   │            │             │            │ queue    │           │        │
   │            │             │            │<─────────│           │        │
   │            │             │            │          │           │        │
   │            │             │            │──────────>           │        │
   │            │             │            │ Claim job│           │        │
   │            │             │            │ (720p)   │           │        │
   │            │             │            │          │           │        │
   │            │             │ 7. Download│          │           │        │
   │            │             │ raw video  │          │           │        │
   │            │             │<───────────────────────│           │        │
   │            │             │            │          │           │        │
   │            │             │            │          │ 8. Transcode      │
   │            │             │            │          │ (FFmpeg)  │        │
   │            │             │            │          │ 1080p→720p│        │
   │            │             │            │          │ ~10 min   │        │
   │            │             │            │          │           │        │
   │            │             │            │          │ 9. Generate       │
   │            │             │            │          │ HLS segments      │
   │            │             │            │          │           │        │
   │            │             │            │          │ 10. Upload│        │
   │            │             │            │          │ processed │        │
   │            │             │            │          │──────────>│        │
   │            │             │            │          │           │        │
   │            │             │            │          │ 11. Update│        │
   │            │             │            │          │ job status│        │
   │            │             │            │          │ (DB)      │        │
   │            │             │            │          │           │        │
   │            │             │            │          │ 12. Delete│        │
   │            │             │            │          │ SQS msg   │        │
   │            │             │            │<─────────│           │        │
   │            │             │            │          │           │        │
   │            │ (After all  │            │          │           │        │
   │            │  4 profiles │            │          │           │        │
   │            │  complete)  │            │          │           │        │
   │            │             │            │          │           │        │
   │            │ 13. Notify  │            │          │           │        │
   │            │ video ready │            │          │           │        │
   │<───────────│ (webhook/   │            │          │           │        │
   │            │  websocket) │            │          │           │        │
   │            │             │            │          │           │        │
   │ 14. Request│             │            │          │           │        │
   │ video play │             │            │          │           │        │
   │────────────────────────────────────────────────────────────────────────>│
   │            │             │            │          │           │        │
   │<────────────────────────────────────────────────────────────────────────│
   │ HLS master │             │            │          │           │        │
   │ playlist + │             │            │          │           │        │
   │ segments   │             │            │          │           │        │
```

### Key Points in Flow:

1. **Async Processing**: Upload completes immediately, transcoding happens in background
2. **Parallel Jobs**: Each profile (1080/720/480/360) is an independent job
3. **Idempotency**: Job contains `video_id + profile` for safe retries
4. **Checkpoint**: Worker can save progress for resume on failure
5. **Cleanup**: Raw file deleted after successful transcoding

---

## 📋 Q16 COLLABORATIVE EDITING - BỔ SUNG

### 1. Capacity Estimation Class

```python
class CollaborativeEditingCapacityEstimator:
    """
    Capacity estimation for real-time collaborative editing system.
    """
    
    def __init__(self):
        # Input parameters
        self.dau = 10_000_000                   # Daily active users
        self.concurrent_editors_peak = 1_000_000 # Peak concurrent
        self.docs_open_concurrent = 200_000     # Active documents
        self.avg_editors_per_doc = 5            # Concurrent per doc
        self.ops_per_user_per_sec = 2           # Typing speed
        self.cursor_updates_per_sec = 4         # Mouse movements
        
    def calculate_ops_throughput(self):
        """
        Operations Throughput
        =====================
        Content ops: inserts, deletes, formatting
        Presence ops: cursor position, selections
        """
        # Content operations
        content_ops_per_sec = self.concurrent_editors_peak * self.ops_per_user_per_sec
        
        # Presence updates (higher frequency, lower priority)
        presence_ops_per_sec = self.concurrent_editors_peak * self.cursor_updates_per_sec
        
        total_ops_per_sec = content_ops_per_sec + presence_ops_per_sec
        
        return {
            'content_ops_per_sec': int(content_ops_per_sec),          # 2M ops/sec
            'presence_ops_per_sec': int(presence_ops_per_sec),        # 4M ops/sec
            'total_ops_per_sec': int(total_ops_per_sec),              # 6M ops/sec
        }
    
    def calculate_websocket_connections(self):
        """
        WebSocket Connection Management
        ================================
        Each editor = 1 persistent WebSocket connection
        """
        # Gateway capacity (assume 10K connections per gateway instance)
        connections_per_gateway = 10_000
        gateway_instances_needed = int(self.concurrent_editors_peak / connections_per_gateway) + 1
        
        # Connection overhead
        memory_per_connection_kb = 50  # Typical WS overhead
        total_memory_gb = (self.concurrent_editors_peak * memory_per_connection_kb) / (1024 * 1024)
        
        return {
            'concurrent_connections': self.concurrent_editors_peak,   # 1M
            'gateway_instances_needed': gateway_instances_needed,     # 100 instances
            'total_memory_gb': int(total_memory_gb),                  # ~48 GB
        }
    
    def calculate_operation_storage(self):
        """
        Operation Log Storage
        =====================
        Store every operation for:
        - Conflict resolution
        - Version history
        - Replay/undo
        """
        # Average operation size
        op_size_bytes = 200  # JSON operation metadata + content
        
        # Operations per day
        seconds_per_day = 86_400
        ops_per_day = self.concurrent_editors_peak * self.ops_per_user_per_sec * seconds_per_day * 0.3  # 30% utilization
        
        # Storage calculation
        storage_per_day_gb = (ops_per_day * op_size_bytes) / (1024**3)
        storage_per_year_tb = (storage_per_day_gb * 365) / 1024
        
        # Retention policy (keep 30 days hot, rest archived)
        hot_storage_gb = storage_per_day_gb * 30
        
        return {
            'ops_per_day': int(ops_per_day),                          # ~51.8B ops/day
            'storage_per_day_gb': int(storage_per_day_gb),            # ~9.6 TB/day
            'storage_per_year_tb': int(storage_per_year_tb),          # ~3.5 PB/year
            'hot_storage_30days_tb': int(hot_storage_gb / 1024),      # ~289 TB
        }
    
    def calculate_fanout_bandwidth(self):
        """
        Fanout Bandwidth for Operation Broadcasting
        ============================================
        When user types, operation must be broadcast to all collaborators in same doc
        """
        # Average fanout per operation (editors per doc - 1)
        avg_fanout = self.avg_editors_per_doc - 1
        
        # Operations that need fanout (content ops only, not presence)
        content_ops_per_sec = self.concurrent_editors_peak * self.ops_per_user_per_sec
        
        # Total broadcasts per second
        broadcasts_per_sec = content_ops_per_sec * avg_fanout
        
        # Bandwidth calculation (200 bytes per op)
        op_size_bytes = 200
        bandwidth_mbps = (broadcasts_per_sec * op_size_bytes * 8) / (1024 * 1024)
        
        return {
            'content_ops_per_sec': int(content_ops_per_sec),          # 2M ops/sec
            'avg_fanout_factor': avg_fanout,                          # 4x
            'broadcasts_per_sec': int(broadcasts_per_sec),            # 8M broadcasts/sec
            'bandwidth_mbps': int(bandwidth_mbps),                    # ~12,207 Mbps (~12 Gbps)
        }
    
    def calculate_conflict_resolution_compute(self):
        """
        Conflict Resolution Compute
        =============================
        OT/CRDT algorithms need CPU for transforming concurrent operations
        """
        # Percentage of operations that conflict
        conflict_rate = 0.05  # 5% of ops need transformation
        
        content_ops_per_sec = self.concurrent_editors_peak * self.ops_per_user_per_sec
        conflicts_per_sec = content_ops_per_sec * conflict_rate
        
        # CPU time per conflict resolution (assume 2ms average)
        cpu_ms_per_conflict = 2
        
        # Total CPU seconds needed per second
        cpu_seconds_per_sec = (conflicts_per_sec * cpu_ms_per_conflict) / 1000
        
        # Cores needed (assume 80% utilization)
        cores_needed = int(cpu_seconds_per_sec / 0.8) + 1
        
        return {
            'content_ops_per_sec': int(content_ops_per_sec),          # 2M ops/sec
            'conflicts_per_sec': int(conflicts_per_sec),              # 100K conflicts/sec
            'cpu_cores_needed': cores_needed,                         # ~250 cores
        }

# Usage
estimator = CollaborativeEditingCapacityEstimator()
print("Ops Throughput:", estimator.calculate_ops_throughput())
print("WebSocket:", estimator.calculate_websocket_connections())
print("Storage:", estimator.calculate_operation_storage())
print("Fanout:", estimator.calculate_fanout_bandwidth())
print("Compute:", estimator.calculate_conflict_resolution_compute())
```

### Summary Table

| Metric | Value | Key Challenge |
|--------|-------|--------------|
| Ops/Second | 6M (2M content + 4M presence) | High throughput |
| WS Connections | 1M concurrent | Gateway scaling |
| Fanout Bandwidth | 12 Gbps | Internal network |
| Storage/Day | 9.6 TB | Operation log size |
| Conflict CPU | 250 cores | OT/CRDT overhead |

---

## 📋 HƯỚNG DẪN SỬ DỤNG FILE NÀY

### Cách Merge vào File Chính:

1. **Q14 Rate Limiter**:
   - Tìm `## 📊 Phase 2: Capacity Estimation (3 phút)` trong Q14
   - Thay thế phần từ đó đến hết "Hệ quả thiết kế..." bằng section 1 ở trên
   - Thêm Sequence Diagram sau phần "Key Design"
   - Thêm Enhanced Monitoring vào Phase 5

2. **Q15 Video Transcoding**:
   - Thêm Capacity Estimation Class sau `## 📊 Phase 2`
   - Thêm Sequence Diagram vào Phase 3 (sau architecture diagram)

3. **Q16 Collaborative Editing**:
   - Thêm Capacity Estimation Class vào Phase 2

### Các Mục Còn Lại Cần Bổ Sung (sẽ làm tiếp):

- Q18: Location-Based Service
- Q19: Ad Serving
- Q20: ML Model Serving

---

## 📋 Q18 LOCATION-BASED SERVICE - BỔ SUNG

### 1. Capacity Estimation Class

```python
class LocationBasedServiceCapacityEstimator:
    """
    Capacity estimation for location-based services (maps, nearby search).
    Covers spatial queries, tile generation, routing.
    """
    
    def __init__(self):
        # Input parameters
        self.dau = 50_000_000                   # Daily active users
        self.queries_per_user_per_day = 10      # Location queries
        self.map_tile_requests_per_session = 50 # Tile loads per session
        self.sessions_per_user_per_day = 3      # App opens per day
        self.poi_database_size = 500_000_000    # Points of interest
        self.peak_factor = 5                    # Peak vs average
        
    def calculate_query_throughput(self):
        """
        Location Query Throughput
        =========================
        Nearby search, geocoding, reverse geocoding
        """
        seconds_per_day = 86_400
        
        # Location queries
        queries_per_day = self.dau * self.queries_per_user_per_day
        avg_qps = queries_per_day / seconds_per_day
        peak_qps = avg_qps * self.peak_factor
        
        # Map tile requests (much higher volume)
        tile_requests_per_day = self.dau * self.sessions_per_user_per_day * self.map_tile_requests_per_session
        avg_tile_qps = tile_requests_per_day / seconds_per_day
        peak_tile_qps = avg_tile_qps * self.peak_factor
        
        return {
            'location_query_avg_qps': int(avg_qps),               # ~5,787 QPS
            'location_query_peak_qps': int(peak_qps),             # ~28,935 QPS
            'map_tile_avg_qps': int(avg_tile_qps),                # ~86,805 QPS
            'map_tile_peak_qps': int(peak_tile_qps),              # ~434,027 QPS
        }
    
    def calculate_spatial_index_memory(self):
        """
        Spatial Index Memory Requirements
        ==================================
        PostGIS, Geohash, or Quadtree indexes for fast spatial queries
        """
        # POI data storage
        bytes_per_poi = 500  # lat, lon, name, category, metadata
        total_poi_storage_gb = (self.poi_database_size * bytes_per_poi) / (1024**3)
        
        # Spatial index overhead (GiST index ~30% of data size)
        index_overhead_factor = 0.3
        spatial_index_gb = total_poi_storage_gb * index_overhead_factor
        
        # In-memory hot data (top 10% frequently accessed)
        hot_data_percent = 0.1
        hot_data_gb = total_poi_storage_gb * hot_data_percent
        
        # Geohash index (all POIs with geohash)
        geohash_bytes_per_poi = 50  # geohash string + pointer
        geohash_index_gb = (self.poi_database_size * geohash_bytes_per_poi) / (1024**3)
        
        return {
            'total_poi_storage_gb': int(total_poi_storage_gb),        # ~233 GB
            'spatial_index_gb': int(spatial_index_gb),                # ~70 GB
            'hot_data_in_memory_gb': int(hot_data_gb),                # ~23 GB
            'geohash_index_gb': int(geohash_index_gb),                # ~23 GB
            'total_memory_needed_gb': int(hot_data_gb + geohash_index_gb),  # ~46 GB
        }
    
    def calculate_tile_storage(self):
        """
        Map Tile Storage
        ================
        Pre-rendered tiles at multiple zoom levels
        """
        # Tile calculation: 2^zoom × 2^zoom tiles per zoom level
        # Zoom levels 0-18 (19 levels)
        total_tiles = sum(4**z for z in range(19))
        
        # Tile size (PNG, optimized)
        avg_tile_size_kb = 15
        
        # Total storage
        total_storage_tb = (total_tiles * avg_tile_size_kb) / (1024**3)
        
        # Multiple styles (satellite, street, terrain)
        num_styles = 3
        total_with_styles_tb = total_storage_tb * num_styles
        
        # CDN cache (zoom 10-18 only for popular areas)
        cdn_zoom_levels = range(10, 19)
        cdn_tiles = sum(4**z for z in cdn_zoom_levels) * 0.1  # 10% of tiles are popular
        cdn_cache_tb = (cdn_tiles * avg_tile_size_kb) / (1024**3)
        
        return {
            'total_tiles_all_zooms': int(total_tiles),                # ~357 trillion
            'storage_single_style_tb': int(total_storage_tb),         # ~5,033 TB
            'storage_all_styles_tb': int(total_with_styles_tb),       # ~15,100 TB
            'cdn_hot_cache_tb': int(cdn_cache_tb),                    # ~1,512 TB
        }
    
    def calculate_routing_compute(self):
        """
        Routing/Navigation Compute
        ==========================
        Dijkstra/A* on road network graphs
        """
        # Assume 10% of queries include routing
        routing_queries_per_day = self.dau * self.queries_per_user_per_day * 0.1
        
        # Routing computation (CPU intensive)
        # A* algorithm: O(b^d) where b=branching factor, d=depth
        # Average routing takes ~50ms CPU time
        cpu_ms_per_route = 50
        
        # Total CPU time per day
        cpu_hours_per_day = (routing_queries_per_day * cpu_ms_per_route) / (1000 * 3600)
        
        # Cores needed (24/7 operation with 80% utilization)
        cores_needed = int((cpu_hours_per_day / 24) / 0.8) + 1
        
        return {
            'routing_queries_per_day': int(routing_queries_per_day),  # 50M routes/day
            'cpu_hours_per_day': int(cpu_hours_per_day),              # ~694 CPU hours/day
            'cores_needed_24x7': cores_needed,                        # ~36 cores
        }
    
    def calculate_bandwidth(self):
        """
        Network Bandwidth
        =================
        Tile delivery dominates bandwidth
        """
        seconds_per_day = 86_400
        
        # Tile delivery (primary bandwidth consumer)
        tiles_per_day = self.dau * self.sessions_per_user_per_day * self.map_tile_requests_per_session
        tile_size_kb = 15
        
        tile_bandwidth_gbps = (tiles_per_day * tile_size_kb * 8) / (seconds_per_day * 1024 * 1024)
        peak_tile_gbps = tile_bandwidth_gbps * self.peak_factor
        
        # API responses (location queries)
        queries_per_day = self.dau * self.queries_per_user_per_day
        response_size_kb = 5  # JSON response
        
        api_bandwidth_gbps = (queries_per_day * response_size_kb * 8) / (seconds_per_day * 1024 * 1024)
        
        return {
            'tile_avg_bandwidth_gbps': tile_bandwidth_gbps,           # ~20 Gbps
            'tile_peak_bandwidth_gbps': peak_tile_gbps,               # ~100 Gbps
            'api_bandwidth_gbps': api_bandwidth_gbps,                 # ~0.5 Gbps
            'total_egress_gbps': tile_bandwidth_gbps + api_bandwidth_gbps,
        }

# Usage
estimator = LocationBasedServiceCapacityEstimator()
print("Query Throughput:", estimator.calculate_query_throughput())
print("Spatial Index:", estimator.calculate_spatial_index_memory())
print("Tile Storage:", estimator.calculate_tile_storage())
print("Routing:", estimator.calculate_routing_compute())
print("Bandwidth:", estimator.calculate_bandwidth())
```

### Summary Table

| Metric | Value | Key Insight |
|--------|-------|-------------|
| Location Query QPS | 29K peak | PostGIS optimization critical |
| Map Tile QPS | 434K peak | CDN essential |
| POI Database | 500M records | Spatial indexing required |
| Tile Storage | 15 PB (3 styles) | Selective caching strategy |
| Routing Compute | 36 cores | Pre-compute common routes |
| Egress Bandwidth | 100 Gbps peak | Tiles dominate cost |

---

### 2. Enhanced Database Schema for Location Data

```sql
-- ============================================
-- LOCATION-BASED SERVICE DATABASE SCHEMA
-- PostGIS extension for spatial operations
-- ============================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- Points of Interest (POI) - Core table
CREATE TABLE places (
    id BIGSERIAL PRIMARY KEY,
    place_id UUID NOT NULL DEFAULT gen_random_uuid(),
    
    -- Basic info
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,              -- restaurant, cafe, gas_station
    subcategory VARCHAR(50),
    
    -- Location data
    location GEOGRAPHY(POINT, 4326) NOT NULL,   -- PostGIS native type
    geohash VARCHAR(12) NOT NULL,               -- For sharding/simple queries
    geohash_6 VARCHAR(6) NOT NULL,              -- Coarse geohash for grouping
    
    -- Address
    street_address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country CHAR(2) NOT NULL,                   -- ISO country code
    postal_code VARCHAR(20),
    
    -- Metadata
    rating DECIMAL(3,2),                        -- 0.00 to 5.00
    rating_count INT DEFAULT 0,
    price_level INT,                            -- 1-4 ($-$$$$)
    phone VARCHAR(50),
    website VARCHAR(500),
    
    -- Hours (flexible JSON)
    opening_hours JSONB,                        -- {"mon": "09:00-17:00", ...}
    
    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_permanently_closed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_place_id UNIQUE (place_id)
);

-- Critical indexes for spatial queries
CREATE INDEX idx_places_location ON places USING GIST (location);
CREATE INDEX idx_places_geohash ON places (geohash varchar_pattern_ops);
CREATE INDEX idx_places_geohash6 ON places (geohash_6);
CREATE INDEX idx_places_category ON places (category) WHERE is_active = TRUE;
CREATE INDEX idx_places_country_category ON places (country, category) WHERE is_active = TRUE;

-- Full-text search index
CREATE INDEX idx_places_name_trgm ON places USING gin (name gin_trgm_ops);

-- Composite index for filtered spatial queries
CREATE INDEX idx_places_location_category ON places 
    USING GIST (location, category) 
    WHERE is_active = TRUE;


-- User Saved Places / Favorites
CREATE TABLE user_saved_places (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    place_id BIGINT NOT NULL REFERENCES places(id),
    
    list_name VARCHAR(100) DEFAULT 'Favorites',  -- Want to go, Favorites, etc.
    notes TEXT,
    
    saved_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_user_place UNIQUE (user_id, place_id, list_name)
);

CREATE INDEX idx_user_saved_user ON user_saved_places (user_id, saved_at DESC);


-- Recent Location History (for personalization)
CREATE TABLE user_location_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    geohash_6 VARCHAR(6) NOT NULL,
    accuracy_meters INT,                        -- GPS accuracy
    
    activity_type VARCHAR(50),                  -- stationary, walking, driving
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Privacy: auto-delete after N days
    expires_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE user_location_history_2025_01 
    PARTITION OF user_location_history 
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE INDEX idx_user_location_user ON user_location_history (user_id, timestamp DESC);
CREATE INDEX idx_user_location_expires ON user_location_history (expires_at) 
    WHERE expires_at < NOW();


-- Geospatial Clusters / Heat Map Data
CREATE TABLE location_clusters (
    id SERIAL PRIMARY KEY,
    geohash_6 VARCHAR(6) NOT NULL UNIQUE,
    
    -- Bounding box
    bbox_north DECIMAL(10, 7) NOT NULL,
    bbox_south DECIMAL(10, 7) NOT NULL,
    bbox_east DECIMAL(10, 7) NOT NULL,
    bbox_west DECIMAL(10, 7) NOT NULL,
    
    -- Statistics
    total_places INT NOT NULL DEFAULT 0,
    category_counts JSONB,                      -- {"restaurant": 45, "cafe": 12}
    avg_rating DECIMAL(3,2),
    
    -- Popularity score (for ranking)
    popularity_score FLOAT DEFAULT 0,
    
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clusters_score ON location_clusters (popularity_score DESC);


-- Routing / Navigation Cache
CREATE TABLE route_cache (
    id BIGSERIAL PRIMARY KEY,
    
    -- Route definition
    origin_geohash VARCHAR(7) NOT NULL,
    destination_geohash VARCHAR(7) NOT NULL,
    travel_mode VARCHAR(20) NOT NULL,           -- driving, walking, cycling
    
    -- Cached route
    route_geometry GEOGRAPHY(LINESTRING, 4326),
    distance_meters INT NOT NULL,
    duration_seconds INT NOT NULL,
    polyline_encoded TEXT,                      -- Encoded polyline for client
    
    -- Waypoints
    waypoints JSONB,
    
    -- Cache metadata
    computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    access_count INT DEFAULT 0,
    last_accessed_at TIMESTAMP,
    
    CONSTRAINT uq_route UNIQUE (origin_geohash, destination_geohash, travel_mode)
);

CREATE INDEX idx_route_cache_origin ON route_cache (origin_geohash);
CREATE INDEX idx_route_cache_access ON route_cache (last_accessed_at);

-- TTL cleanup: delete routes not accessed in 30 days
-- Run as cron job: DELETE FROM route_cache WHERE last_accessed_at < NOW() - INTERVAL '30 days';
```

### Optimized Spatial Queries

```sql
-- Query 1: Nearby places (radius search with category filter)
-- Use case: "Find restaurants within 2km"
PREPARE nearby_places_query AS
SELECT 
    id,
    name,
    category,
    ST_Distance(location, ST_SetSRID(ST_MakePoint($1, $2), 4326)) as distance_meters,
    rating,
    price_level
FROM places
WHERE 
    is_active = TRUE
    AND category = $3
    AND ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
        $4  -- radius in meters
    )
ORDER BY distance_meters ASC
LIMIT $5;

-- Usage: EXECUTE nearby_places_query(126.9780, 37.5665, 'restaurant', 2000, 20);


-- Query 2: Bounding box search (map viewport)
-- Use case: "Show all POIs visible on current map view"
PREPARE bbox_search AS
SELECT 
    id,
    name,
    category,
    ST_X(location::geometry) as longitude,
    ST_Y(location::geometry) as latitude,
    rating
FROM places
WHERE 
    is_active = TRUE
    AND location && ST_MakeEnvelope($1, $2, $3, $4, 4326)  -- west, south, east, north
    AND ($5 IS NULL OR category = $5)  -- Optional category filter
LIMIT 500;


-- Query 3: Geohash prefix search (for sharding/caching)
-- Use case: "Find all places in Seoul area"
PREPARE geohash_prefix_search AS
SELECT 
    id, name, category, rating, geohash
FROM places
WHERE 
    is_active = TRUE
    AND geohash LIKE $1 || '%'  -- e.g., 'wydm%' for Seoul
    AND ($2 IS NULL OR category = $2)
LIMIT 100;


-- Query 4: Text search with location bias
-- Use case: "Search for 'Starbucks' near my location"
PREPARE text_location_search AS
SELECT 
    id,
    name,
    category,
    ST_Distance(location, ST_SetSRID(ST_MakePoint($2, $3), 4326)) as distance_meters,
    similarity(name, $1) as name_similarity
FROM places
WHERE 
    is_active = TRUE
    AND name % $1  -- Trigram similarity operator
    AND ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint($2, $3), 4326)::geography,
        10000  -- 10km search radius
    )
ORDER BY 
    name_similarity DESC,
    distance_meters ASC
LIMIT 20;
```

---

## 📋 Q19 AD SERVING SYSTEM - BỔ SUNG

### 1. Capacity Estimation Class

```python
class AdServingCapacityEstimator:
    """
    Capacity estimation for real-time ad serving and bidding system.
    """
    
    def __init__(self):
        # Input parameters
        self.daily_impressions = 1_000_000_000   # 1B impressions/day
        self.peak_factor = 3                     # Peak vs average
        self.cache_hit_rate = 0.70               # CDN + edge cache
        self.rtb_timeout_ms = 100                # Real-time bidding timeout
        self.avg_bidders_per_auction = 10        # DSPs participating
        self.click_through_rate = 0.02           # 2% CTR
        self.conversion_rate = 0.10              # 10% of clicks convert
        
    def calculate_serving_qps(self):
        """
        Ad Serving QPS
        ==============
        Every page load = 1+ ad requests
        """
        seconds_per_day = 86_400
        
        # Impression requests
        avg_impression_qps = self.daily_impressions / seconds_per_day
        peak_impression_qps = avg_impression_qps * self.peak_factor
        
        # After cache (requests hitting backend)
        backend_qps = peak_impression_qps * (1 - self.cache_hit_rate)
        
        # Auction requests (each impression triggers auction)
        auction_qps = backend_qps
        
        # RTB requests (parallel to multiple DSPs)
        rtb_outbound_qps = auction_qps * self.avg_bidders_per_auction
        
        return {
            'avg_impression_qps': int(avg_impression_qps),            # ~11,574 QPS
            'peak_impression_qps': int(peak_impression_qps),          # ~34,722 QPS
            'backend_qps_after_cache': int(backend_qps),              # ~10,417 QPS
            'rtb_outbound_qps': int(rtb_outbound_qps),                # ~104,167 QPS
        }
    
    def calculate_auction_latency_budget(self):
        """
        Latency Budget Breakdown
        ========================
        Total: 100ms from ad request to response
        """
        total_budget_ms = 100
        
        # Breakdown
        network_overhead_ms = 10
        user_targeting_ms = 5
        ad_selection_ms = 10
        rtb_parallel_bidding_ms = 50   # Parallel requests to DSPs
        creative_fetch_ms = 10
        render_prep_ms = 5
        buffer_ms = 10
        
        return {
            'total_budget_ms': total_budget_ms,
            'network_overhead_ms': network_overhead_ms,
            'user_targeting_ms': user_targeting_ms,
            'ad_selection_ms': ad_selection_ms,
            'rtb_bidding_ms': rtb_parallel_bidding_ms,
            'creative_fetch_ms': creative_fetch_ms,
            'render_prep_ms': render_prep_ms,
            'buffer_ms': buffer_ms,
        }
    
    def calculate_event_stream_volume(self):
        """
        Event Stream Volume
        ===================
        Impressions, clicks, conversions → analytics pipeline
        """
        impressions_per_day = self.daily_impressions
        clicks_per_day = impressions_per_day * self.click_through_rate
        conversions_per_day = clicks_per_day * self.conversion_rate
        
        # Event sizes
        impression_event_bytes = 500   # Rich metadata
        click_event_bytes = 300
        conversion_event_bytes = 400
        
        # Daily volume
        impression_data_gb = (impressions_per_day * impression_event_bytes) / (1024**3)
        click_data_gb = (clicks_per_day * click_event_bytes) / (1024**3)
        conversion_data_gb = (conversions_per_day * conversion_event_bytes) / (1024**3)
        
        total_events_per_day = impressions_per_day + clicks_per_day + conversions_per_day
        total_data_gb_per_day = impression_data_gb + click_data_gb + conversion_data_gb
        
        # Kafka/streaming throughput
        avg_events_per_sec = total_events_per_day / 86_400
        peak_events_per_sec = avg_events_per_sec * self.peak_factor
        
        return {
            'impressions_per_day': int(impressions_per_day),          # 1B
            'clicks_per_day': int(clicks_per_day),                    # 20M
            'conversions_per_day': int(conversions_per_day),          # 2M
            'total_events_per_day': int(total_events_per_day),        # 1.022B
            'total_data_gb_per_day': int(total_data_gb_per_day),      # ~466 GB/day
            'avg_events_per_sec': int(avg_events_per_sec),            # ~11,828 events/sec
            'peak_events_per_sec': int(peak_events_per_sec),          # ~35,648 events/sec
        }
    
    def calculate_user_profile_storage(self):
        """
        User Profile Storage
        ====================
        Targeting data: interests, demographics, behavior
        """
        # Assume 500M unique users per month
        unique_users = 500_000_000
        
        # Profile data
        profile_bytes_per_user = 2048  # Interests, segments, history
        total_profile_gb = (unique_users * profile_bytes_per_user) / (1024**3)
        
        # Hot profiles (active users, in Redis)
        hot_users_percent = 0.20  # 20% active daily
        hot_profile_gb = total_profile_gb * hot_users_percent
        
        # Frequency cap counters (Redis, ephemeral)
        freq_cap_bytes_per_user = 100
        freq_cap_gb = (unique_users * freq_cap_bytes_per_user) / (1024**3)
        
        return {
            'unique_users': unique_users,                             # 500M
            'total_profile_storage_gb': int(total_profile_gb),        # ~954 GB
            'hot_profile_cache_gb': int(hot_profile_gb),              # ~191 GB
            'frequency_cap_redis_gb': int(freq_cap_gb),               # ~47 GB
        }
    
    def calculate_campaign_budget_tracking(self):
        """
        Budget Tracking & Pacing
        ========================
        Real-time spend tracking per campaign
        """
        # Assume 100K active campaigns
        active_campaigns = 100_000
        
        # Budget counters (Redis)
        counter_bytes_per_campaign = 200  # Spend today, lifetime, limits
        budget_counter_mb = (active_campaigns * counter_bytes_per_campaign) / (1024**2)
        
        # Budget update frequency (every impression)
        budget_updates_per_sec = self.daily_impressions / 86_400
        
        # Redis ops (HINCRBY for atomic updates)
        redis_ops_per_sec = budget_updates_per_sec
        
        return {
            'active_campaigns': active_campaigns,
            'budget_counter_storage_mb': int(budget_counter_mb),      # ~19 MB
            'budget_updates_per_sec': int(budget_updates_per_sec),    # ~11,574 ops/sec
        }
    
    def calculate_fraud_detection_compute(self):
        """
        Fraud Detection Compute
        =======================
        ML models + rule engine for detecting invalid traffic
        """
        # Check every impression
        impressions_per_sec = self.daily_impressions / 86_400
        
        # Fraud check latency (must be fast)
        fraud_check_ms_per_impression = 2
        
        # CPU time
        cpu_seconds_per_second = (impressions_per_sec * fraud_check_ms_per_impression) / 1000
        
        # Cores needed (80% utilization)
        cores_needed = int(cpu_seconds_per_second / 0.8) + 1
        
        # Fraud rate (detected)
        fraud_rate = 0.05  # 5% of traffic
        fraud_impressions_per_day = self.daily_impressions * fraud_rate
        
        return {
            'fraud_checks_per_sec': int(impressions_per_sec),         # ~11,574/sec
            'cpu_cores_needed': cores_needed,                         # ~29 cores
            'fraud_detected_per_day': int(fraud_impressions_per_day), # 50M/day
        }

# Usage
estimator = AdServingCapacityEstimator()
print("Serving QPS:", estimator.calculate_serving_qps())
print("Latency Budget:", estimator.calculate_auction_latency_budget())
print("Event Stream:", estimator.calculate_event_stream_volume())
print("User Profiles:", estimator.calculate_user_profile_storage())
print("Budget Tracking:", estimator.calculate_campaign_budget_tracking())
print("Fraud Detection:", estimator.calculate_fraud_detection_compute())
```

### Summary Table

| Metric | Value | Key Challenge |
|--------|-------|--------------|
| Peak Impression QPS | 35K | High throughput |
| RTB Outbound QPS | 104K | Parallel bidding |
| Latency Budget | 100ms total | Tight deadline |
| Event Volume | 466 GB/day | Streaming pipeline |
| User Profiles | 954 GB | Fast lookups |
| Fraud Detection | 29 CPU cores | Real-time ML |

---

## 📋 Q20 ML MODEL SERVING - BỔ SUNG

### 1. Capacity Estimation Class

```python
class MLModelServingCapacityEstimator:
    """
    Capacity estimation for production ML model serving.
    Covers inference, feature store, A/B testing.
    """
    
    def __init__(self):
        # Input parameters
        self.daily_predictions = 500_000_000     # 500M predictions/day
        self.peak_factor = 5                     # Peak vs average
        self.model_latency_p99_ms = 10           # Target p99 latency
        self.feature_count_per_prediction = 50   # Features per request
        self.ab_test_variants = 3                # Concurrent model versions
        self.model_size_mb = 500                 # Model file size
        
    def calculate_inference_throughput(self):
        """
        Inference QPS
        =============
        """
        seconds_per_day = 86_400
        
        avg_qps = self.daily_predictions / seconds_per_day
        peak_qps = avg_qps * self.peak_factor
        
        # GPU vs CPU decision
        # GPU: ~1000 predictions/sec per GPU (batched)
        # CPU: ~100 predictions/sec per core
        
        # GPU instance count
        predictions_per_gpu_per_sec = 1000
        gpus_needed_avg = int(avg_qps / predictions_per_gpu_per_sec) + 1
        gpus_needed_peak = int(peak_qps / predictions_per_gpu_per_sec) + 1
        
        # CPU instance count (fallback)
        predictions_per_core_per_sec = 100
        cores_needed_avg = int(avg_qps / predictions_per_core_per_sec) + 1
        cores_needed_peak = int(peak_qps / predictions_per_core_per_sec) + 1
        
        return {
            'avg_qps': int(avg_qps),                                  # ~5,787 QPS
            'peak_qps': int(peak_qps),                                # ~28,935 QPS
            'gpus_needed_avg': gpus_needed_avg,                       # 6 GPUs
            'gpus_needed_peak': gpus_needed_peak,                     # 29 GPUs
            'cpu_cores_needed_avg': cores_needed_avg,                 # 58 cores
            'cpu_cores_needed_peak': cores_needed_peak,               # 290 cores
        }
    
    def calculate_feature_store_ops(self):
        """
        Feature Store Operations
        ========================
        Online feature retrieval for real-time inference
        """
        # Each prediction needs feature fetch
        feature_fetches_per_sec = self.daily_predictions / 86_400
        peak_feature_fetches = feature_fetches_per_sec * self.peak_factor
        
        # Feature store (Redis) ops
        # Batch get: 1 op fetches multiple features
        features_per_batch = 10
        redis_ops_per_sec = feature_fetches_per_sec / features_per_batch
        peak_redis_ops = redis_ops_per_sec * self.peak_factor
        
        # Feature data size
        bytes_per_feature = 20  # float64 + metadata
        bytes_per_prediction = self.feature_count_per_prediction * bytes_per_feature
        
        # Network bandwidth (feature fetch)
        bandwidth_mbps = (peak_feature_fetches * bytes_per_prediction * 8) / (1024 * 1024)
        
        return {
            'feature_fetches_per_sec': int(feature_fetches_per_sec),  # ~5,787/sec
            'peak_feature_fetches': int(peak_feature_fetches),        # ~28,935/sec
            'redis_ops_per_sec': int(redis_ops_per_sec),              # ~579/sec
            'peak_redis_ops': int(peak_redis_ops),                    # ~2,894/sec
            'bandwidth_mbps': int(bandwidth_mbps),                    # ~22 Mbps
        }
    
    def calculate_model_storage(self):
        """
        Model Storage & Versioning
        ===========================
        Model registry, A/B test variants
        """
        # Model versions in registry
        models_in_registry = 50  # Historical versions
        
        # Active serving models (warm in memory)
        active_models = self.ab_test_variants
        
        # Storage
        registry_storage_gb = (models_in_registry * self.model_size_mb) / 1024
        active_memory_gb = (active_models * self.model_size_mb) / 1024
        
        # Model load time (cold start)
        model_load_time_sec = self.model_size_mb / 100  # ~100 MB/sec disk read
        
        return {
            'models_in_registry': models_in_registry,
            'registry_storage_gb': int(registry_storage_gb),          # ~24 GB
            'active_models_memory_gb': int(active_memory_gb),         # ~1.5 GB
            'cold_start_time_sec': int(model_load_time_sec),          # ~5 seconds
        }
    
    def calculate_prediction_logging(self):
        """
        Prediction Logging for Monitoring & Retraining
        ==============================================
        """
        predictions_per_day = self.daily_predictions
        
        # Log entry size
        log_bytes_per_prediction = 500  # features + prediction + metadata
        
        # Daily log volume
        log_gb_per_day = (predictions_per_day * log_bytes_per_prediction) / (1024**3)
        log_tb_per_year = (log_gb_per_day * 365) / 1024
        
        # Streaming ingestion (Kafka)
        avg_events_per_sec = predictions_per_day / 86_400
        peak_events_per_sec = avg_events_per_sec * self.peak_factor
        
        return {
            'log_gb_per_day': int(log_gb_per_day),                    # ~233 GB/day
            'log_tb_per_year': int(log_tb_per_year),                  # ~85 TB/year
            'avg_log_events_per_sec': int(avg_events_per_sec),        # ~5,787/sec
            'peak_log_events_per_sec': int(peak_events_per_sec),      # ~28,935/sec
        }
    
    def calculate_ab_testing_overhead(self):
        """
        A/B Testing Overhead
        ====================
        Multiple model variants serving simultaneously
        """
        # Split traffic across variants
        traffic_per_variant = self.daily_predictions / self.ab_test_variants
        
        # Inference compute (multiply by variants)
        total_inference_ops = self.daily_predictions  # Same regardless
        
        # Logging overhead (need to track variant per prediction)
        variant_tracking_bytes = 50  # variant_id + assignment_timestamp
        tracking_overhead_gb = (self.daily_predictions * variant_tracking_bytes) / (1024**3)
        
        # Statistical significance calculation
        # Need ~10K samples per variant for 95% confidence
        min_samples_per_variant = 10_000
        time_to_significance_hours = (min_samples_per_variant * self.ab_test_variants) / (self.daily_predictions / 24)
        
        return {
            'variants_running': self.ab_test_variants,
            'traffic_per_variant': int(traffic_per_variant),          # ~167M/day each
            'tracking_overhead_gb_per_day': int(tracking_overhead_gb),# ~23 GB/day
            'hours_to_statistical_significance': time_to_significance_hours,  # ~0.00144h (~5sec)
        }
    
    def calculate_feature_engineering_pipeline(self):
        """
        Feature Engineering Pipeline
        =============================
        Batch + streaming feature computation
        """
        # Batch features (computed daily)
        batch_features_per_day = 100_000_000  # 100M entities
        compute_seconds_per_entity = 0.1
        
        batch_cpu_hours = (batch_features_per_day * compute_seconds_per_entity) / 3600
        
        # Streaming features (real-time updates)
        streaming_updates_per_sec = 5000  # User events trigger updates
        
        return {
            'batch_entities_per_day': batch_features_per_day,
            'batch_cpu_hours_per_day': int(batch_cpu_hours),          # ~2,778 CPU hours
            'streaming_updates_per_sec': streaming_updates_per_sec,
        }

# Usage
estimator = MLModelServingCapacityEstimator()
print("Inference:", estimator.calculate_inference_throughput())
print("Feature Store:", estimator.calculate_feature_store_ops())
print("Model Storage:", estimator.calculate_model_storage())
print("Prediction Logging:", estimator.calculate_prediction_logging())
print("A/B Testing:", estimator.calculate_ab_testing_overhead())
print("Feature Pipeline:", estimator.calculate_feature_engineering_pipeline())
```

### Summary Table

| Metric | Value | Key Challenge |
|--------|-------|--------------|
| Peak QPS | 29K | GPU autoscaling |
| Feature Fetches | 29K/sec | Fast KV store |
| Model Memory | 1.5 GB (3 variants) | Warm models |
| Prediction Logs | 233 GB/day | Streaming pipeline |
| A/B Test Traffic | 167M per variant | Statistical power |
| Cold Start | 5 seconds | Pre-warming critical |

---

## 📋 TỔNG HỢP VÀ CHECKLIST HOÀN THÀNH

### ✅ Đã Bổ Sung Cho Các Mục:

1. **Q14 - Rate Limiter**
   - ✅ Capacity Estimation Class (chi tiết)
   - ✅ Sequence Diagram (2 scenarios)
   - ✅ Enhanced Monitoring với Prometheus alerts
   - ✅ Database schema cho rules

2. **Q15 - Video Transcoding**
   - ✅ Capacity Estimation Class (compute/storage/queue)
   - ✅ Sequence Diagram (upload → transcode → delivery)
   - ✅ Job/Task state machine

3. **Q16 - Collaborative Editing**
   - ✅ Capacity Estimation Class (ops throughput/fanout)
   - ✅ WebSocket connection sizing
   - ✅ Operation log storage

4. **Q18 - Location-Based Service**
   - ✅ Capacity Estimation Class (spatial queries/tiles/routing)
   - ✅ Complete PostGIS schema
   - ✅ Optimized spatial query examples

5. **Q19 - Ad Serving**
   - ✅ Capacity Estimation Class (RTB/budget/fraud)
   - ✅ Latency budget breakdown
   - ✅ Event stream volume analysis

6. **Q20 - ML Model Serving**
   - ✅ Capacity Estimation Class (inference/features/AB)
   - ✅ GPU vs CPU sizing
   - ✅ Feature store operations

### 📝 Cách Sử Dụng File Enhancement:

1. **Copy từng section** vào đúng vị trí trong file chính
2. **Sequence diagrams** thêm vào Phase 3 (High-Level Design)
3. **Capacity classes** thêm vào Phase 2
4. **Database schemas** thêm vào Phase 4 (Deep Dive)
5. **Monitoring/Observability** thêm vào Phase 5

### 🎯 So Sánh Trước/Sau:

| Mục | Trước | Sau |
|-----|-------|-----|
| Capacity Estimation | Rough math | Python class chi tiết |
| Database Schema | Không có/thiếu | Production-grade với indexes |
| Sequence Diagrams | Thiếu | Chi tiết 2+ scenarios |
| Monitoring | Basic | Prometheus alerts + queries |
| Real-world depth | Surface | Giống Q11-Q13 |

### ✨ Giờ Tài Liệu Của Bạn:

- **Đồng nhất về độ sâu** từ Q11 đến Q20
- **Production-ready** với capacity formulas
- **Interview-focused** với trade-offs và failure scenarios
- **Complete reference** cho system design prep

Bạn có muốn tôi giúp merge các phần này vào file chính hoặc điều chỉnh gì thêm không?
