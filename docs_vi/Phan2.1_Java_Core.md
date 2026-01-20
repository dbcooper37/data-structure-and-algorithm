# JVM Tuning Content (For Phan2 - Java Core)

## Insertion Point
Add new section after basic JVM concepts in Phan2_Java_Core.md

---

## 2.X. ⭐ JVM Tuning - Production Cases

### 2.X.1. Full GC Frequency Problem

**Production Scenario:**
```
Application: E-commerce Order Service
Environment: Production
Heap: 4GB (-Xms4g -Xmx4g)
GC: G1GC
Problem: Full GC every 10 minutes → STW pause 2-3 seconds!
Impact: Order submission failures, User complaints
```

**Symptoms:**
- Application freezes periodically
- Response time spikes to 3+ seconds
- Throughput drops during GC

**Step 1: Enable GC Logging**

```bash
# Java 8
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xloggc:/var/log/gc.log

# Java 11+
-Xlog:gc*:file=/var/log/gc.log:time,level,tags
```

**Step 2: Analyze GC Log**

```
[2024-01-20T10:00:00.123+0700] GC(245) Pause Full (G1 Evacuation Pause)
[2024-01-20T10:00:00.123+0700] GC(245) Using 4 workers
[2024-01-20T10:00:00.123+0700] GC(245) Eden: 512M(512M) -> 0M(512M)
[2024-01-20T10:00:00.123+0700] GC(245) Survivor: 64M(64M) -> 0M(64M)
[2024-01-20T10:00:00.123+0700] GC(245) Old: 3324M(3520M) -> 3310M(3520M)
[2024-01-20T10:00:00.123+0700] GC(245) Metaspace: 89M(90M) -> 89M(90M)
[2024-01-20T10:00:00.123+0700] GC(245) Pause Full (G1 Evacuation Pause) 3900M->3310M(4096M) 2500ms
```

**Analysis:**
```
Problem indicators:
1. Old gen almost full: 3324M / 3520M = 94% occupancy
2. Full GC barely freed memory: 3324M → 3310M (only 14MB!)
3. Long pause: 2.5 seconds STW
4. Frequency: Every 10 minutes

Conclusion: Memory leak or unbounded cache in Old generation
```

**Step 3: Heap Dump Analysis**

```bash
# Take heap dump
jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>

# Or auto-dump on OOM
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/dumps/

# Analyze with jhat or MAT (Memory Analyzer Tool)
jhat /tmp/heap.hprof
# Browse to http://localhost:7000
```

**Step 4: Root Cause Found**

```java
// Code review revealed the problem:
@RestController
public class OrderController {
    // ❌ BAD: Unbounded static cache
    private static Map<String, Order> orderCache = new HashMap<>();
    
    @GetMapping("/orders/{id}")
    public Order getOrder(@PathVariable String id) {
        // Cache grows indefinitely → Old gen full → Full GC
        return orderCache.computeIfAbsent(id, k -> {
            return orderDao.findById(k);
        });
    }
    
    // Over time:
    // 1M orders cached * 2KB each = 2GB in Old gen
    // Never evicted → GC can't reclaim → Full GC triggered
}
```

**MAT Analysis Screenshot:**
```
Leak Suspects Report:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Problem Suspect 1:
  Object: HashMap
  Retained Heap: 2.1 GB (52% of total heap)
  Path to GC Root:
    OrderController.orderCache (static field)
    → HashMap
    → HashMap$Node[]
    → 1,048,576 Order objects

  Conclusion: Static cache never evicts entries
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Solutions:**

**Solution 1: Bounded LRU Cache**
```java
import com.google.common.cache.CacheBuilder;
import com.google.common.cache.LoadingCache;

@RestController
public class OrderController {
    // ✅ GOOD: Bounded cache with LRU eviction
    private static final LoadingCache<String, Order> orderCache = 
        CacheBuilder.newBuilder()
            .maximumSize(10_000)  // Limit: 10k orders (~20MB)
            .expireAfterWrite(10, TimeUnit.MINUTES)  // TTL
            .recordStats()  // Monitor hit rate
            .build(new CacheLoader<String, Order>() {
                @Override
                public Order load(String id) {
                    return orderDao.findById(id);
                }
            });
    
    @GetMapping("/orders/{id}")
    public Order getOrder(@PathVariable String id) throws ExecutionException {
        return orderCache.get(id);
    }
    
    // Monitor cache stats
    @GetMapping("/cache/stats")
    public CacheStats getStats() {
        return orderCache.stats();
        // Output: hitRate=0.85, missRate=0.15, evictionCount=5000
    }
}
```

**Solution 2: Offload to Redis**
```java
@Service
public class OrderService {
    @Autowired
    private RedisTemplate<String, Order> redis;
    
    // ✅ GOOD: Use Redis (off-heap)
    @Cacheable(value = "orders", key = "#id", unless = "#result == null")
    public Order getOrder(String id) {
        return orderDao.findById(id);
    }
    
    // Benefits:
    // 1. No JVM heap pressure
    // 2. Shared across instances
    // 3. Survives restarts
    // 4. Built-in TTL
}
```

**Solution 3: Tune G1GC Parameters**
```bash
# If cache is necessary, tune GC to handle it better
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200          # Target pause time (200ms)
-XX:G1HeapRegionSize=16M          # Larger regions for big objects
-XX:InitiatingHeapOccupancyPercent=45  # Start mixed GC earlier (default 45%)
-XX:G1MixedGCCountTarget=8        # More mixed GC cycles
-XX:G1HeapWastePercent=5          # Reduce waste

# Monitor results
-Xlog:gc*:file=/var/log/gc.log:time,level,tags
```

**Results After Fix:**
```
Before:
- Full GC: Every 10 minutes
- Pause time: 2.5 seconds
- Heap usage: 3.9GB / 4GB (97%)

After (Solution 1 - LRU Cache):
- Full GC: Never (only young GC)
- Pause time: <50ms (young GC)
- Heap usage: 1.2GB / 4GB (30%)
- Cache hit rate: 85%

Performance improvement: 50x better GC pause
```

---

### 2.X.2. Memory Leak Detection

**Common Memory Leak Patterns in Java:**

#### Pattern 1: ThreadLocal Not Cleaned

**Problem:**
```java
public class UserContext {
    private static ThreadLocal<User> userHolder = new ThreadLocal<>();
    
    // Called by authentication filter
    public static void setUser(User user) {
        userHolder.set(user);
        // ❌ MISSING: userHolder.remove();
    }
    
    public static User getUser() {
        return userHolder.get();
    }
}

// In servlet environment with thread pool:
// 1. Request 1: Thread-1 sets User A → userHolder stores User A
// 2. Request 1 completes: Thread-1 returns to pool (User A still in ThreadLocal!)
// 3. Request 2: Thread-1 reused, User A leaks (not related to Request 2)
// 4. Over time: 200 threads * 1KB User object = 200KB leak (per request cycle)
```

**Detection:**
```bash
# Heap dump
jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>

# Analyze with MAT
# Look for: ThreadLocal$ThreadLocalMap → Entry[] → Many User objects
```

**Solution:**
```java
public class UserContext {
    private static ThreadLocal<User> userHolder = new ThreadLocal<>();
    
    public static void setUser(User user) {
        userHolder.set(user);
    }
    
    public static User getUser() {
        return userHolder.get();
    }
    
    // ✅ MUST call in finally block
    public static void clear() {
        userHolder.remove();
    }
}

// In Filter
@Override
public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
    try {
        User user = authenticate(request);
        UserContext.setUser(user);
        chain.doFilter(request, response);
    } finally {
        UserContext.clear();  // ✅ Always cleanup
    }
}
```

#### Pattern 2: Event Listeners Not Unregistered

**Problem:**
```java
public class EventBus {
    private static List<EventListener> listeners = new ArrayList<>();
    
    public void register(EventListener listener) {
        listeners.add(listener);
        // ❌ Leak: Listener never removed, even after object destroyed
    }
    
    public void fire(Event event) {
        listeners.forEach(l -> l.onEvent(event));
    }
}

// Usage in UI component
public class OrderPanel extends JPanel {
    public OrderPanel() {
        EventBus.getInstance().register(this::onOrderUpdate);
        // When panel closed → Object destroyed
        // But listener reference still in EventBus → Memory leak!
    }
}
```

**Solution 1: Explicit Unregister**
```java
public class EventBus {
    private static List<EventListener> listeners = new ArrayList<>();
    
    public void register(EventListener listener) {
        listeners.add(listener);
    }
    
    // ✅ Provide unregister
    public void unregister(EventListener listener) {
        listeners.remove(listener);
    }
}

// Usage
public class OrderPanel extends JPanel {
    private EventListener listener = this::onOrderUpdate;
    
    public OrderPanel() {
        EventBus.getInstance().register(listener);
    }
    
    @Override
    public void dispose() {
        EventBus.getInstance().unregister(listener);  // ✅ Cleanup
        super.dispose();
    }
}
```

**Solution 2: Weak References (Automatic Cleanup)**
```java
public class EventBus {
    // ✅ Use WeakReference
    private static List<WeakReference<EventListener>> listeners = new ArrayList<>();
    
    public void register(EventListener listener) {
        listeners.add(new WeakReference<>(listener));
    }
    
    public void fire(Event event) {
        // Clean up dead references + fire event
        listeners.removeIf(ref -> ref.get() == null);
        
        listeners.forEach(ref -> {
            EventListener listener = ref.get();
            if (listener != null) {
                listener.onEvent(event);
            }
        });
    }
}

// Usage
public class OrderPanel extends JPanel {
    public OrderPanel() {
        EventBus.getInstance().register(this::onOrderUpdate);
        // No need to unregister!
        // When OrderPanel GC'd → WeakReference.get() returns null → Auto cleanup
    }
}
```

#### Pattern 3: Unclosed Resources

**Problem:**
```java
public List<Order> getOrders() throws SQLException {
    Connection conn = dataSource.getConnection();
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM orders");
    
    List<Order> orders = new ArrayList<>();
    while (rs.next()) {
        orders.add(mapRow(rs));
    }
    
    return orders;
    // ❌ Leak: Connection, Statement, ResultSet never closed!
    // Connection pool exhausted after ~100 calls
}
```

**Solution: Try-with-resources**
```java
public List<Order> getOrders() throws SQLException {
    // ✅ Auto-close resources
    try (Connection conn = dataSource.getConnection();
         Statement stmt = conn.createStatement();
         ResultSet rs = stmt.executeQuery("SELECT * FROM orders")) {
        
        List<Order> orders = new ArrayList<>();
        while (rs.next()) {
            orders.add(mapRow(rs));
        }
        return orders;
    }
    // Resources auto-closed in reverse order
}
```

---

### 2.X.3. GC Tuning Quick Reference

**当选择 GC Algorithm:**

```bash
# G1GC (Default Java 9+, Recommended for most cases)
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200

# Use when:
# - Heap > 4GB
# - Need predictable pause times
# - Mixed workload (young + old objects)

# ZGC (Java 11+, Ultra-low latency)
-XX:+UseZGC
-XX:ZCollectionInterval=120

# Use when:
# - Need pause < 10ms
# - Heap > 8GB
# - Can spare CPU (ZGC uses more CPU)

# Parallel GC (Java 8 default, Throughput-oriented)
-XX:+UseParallelGC

# Use when:
# - Batch processing
# - Throughput > Latency
# - Heap < 4GB
```

**Common Tuning Parameters:**

```bash
# Heap sizing
-Xms4g -Xmx4g  # Always set same value (avoid resizing)

# Young generation
-XX:NewRatio=2  # Old:Young = 2:1
-XX:SurvivorRatio=8  # Eden:Survivor = 8:1

# Metaspace (Java 8+)
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m

# GC logging
-Xlog:gc*:file=/var/log/gc.log:time,level,tags

# Heap dump on OOM
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/dumps/
```

**Monitoring Commands:**

```bash
# 1. Live GC stats
jstat -gcutil <pid> 1000  # Every 1 second

# Output:
#   S0    S1    E     O     M     CCS   YGC  YGCT   FGC  FGCT   GCT
#  0.00  99.18  45.23  68.45  95.32  92.13  1234  12.45   5   2.15  14.60

# 2. Heap summary
jmap -heap <pid>

# 3. Thread dump (deadlock detection)
jstack <pid> > thread_dump.txt

# 4. Find memory hogs
jmap -histo:live <pid> | head -20

# Output:
# num  #instances  #bytes  class name
# 1:   500000      48000000  java.lang.String
# 2:   200000      32000000  com.example.Order
```

---

This content provides production-ready JVM tuning knowledge with real scenarios and complete solutions.
