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

## 3. Collections Framework Deep Dive

### 3.1. List Implementations

#### ArrayList vs LinkedList

**ArrayList:**
- **Internal**: Array-based, resizable
- **Access**: O(1) random access
- **Insert/Delete**: O(n) (need to shift elements)
- **Memory**: Compact (no pointers)
- **Use Case**: Random access, frequent reads

**LinkedList:**
- **Internal**: Doubly-linked list
- **Access**: O(n) sequential access
- **Insert/Delete**: O(1) (if position known)
- **Memory**: Overhead (pointers)
- **Use Case**: Frequent insertions/deletions at ends

**Performance Comparison:**

| Operation | ArrayList | LinkedList |
|-----------|-----------|------------|
| **Get (by index)** | O(1) ✅ | O(n) ❌ |
| **Add (at end)** | O(1) amortized ✅ | O(1) ✅ |
| **Add (at index)** | O(n) ❌ | O(n) ⚠️ |
| **Remove (by index)** | O(n) ❌ | O(n) ⚠️ |
| **Remove (by value)** | O(n) ❌ | O(n) ⚠️ |

**Example:**
```java
// ✅ Use ArrayList for random access
List<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.add(3);
int value = list.get(1);  // O(1) fast

// ✅ Use LinkedList for frequent insertions/deletions at ends
List<Integer> list = new LinkedList<>();
list.addFirst(1);  // O(1)
list.addLast(2);   // O(1)
list.removeFirst(); // O(1)
```

#### Vector vs ArrayList

**Vector:**
- **Thread-safe**: Synchronized methods
- **Performance**: Slower (synchronization overhead)
- **Legacy**: Java 1.0 (not recommended)

**ArrayList:**
- **Not thread-safe**: Need external synchronization
- **Performance**: Faster
- **Recommended**: Java 1.2+

**Use Collections.synchronizedList() instead of Vector:**
```java
// ✅ GOOD: Use synchronized wrapper
List<String> list = Collections.synchronizedList(new ArrayList<>());

// ❌ BAD: Don't use Vector
Vector<String> vector = new Vector<>();
```

### 3.2. Set Implementations

#### HashSet vs TreeSet vs LinkedHashSet

**HashSet:**
- **Internal**: HashMap (hash table)
- **Order**: No order
- **Performance**: O(1) average
- **Null**: Allows one null
- **Use Case**: Fast lookups, no order needed

**TreeSet:**
- **Internal**: TreeMap (red-black tree)
- **Order**: Sorted order
- **Performance**: O(log n)
- **Null**: Not allowed
- **Use Case**: Sorted set, range queries

**LinkedHashSet:**
- **Internal**: LinkedHashMap (hash table + linked list)
- **Order**: Insertion order
- **Performance**: O(1) average
- **Null**: Allows one null
- **Use Case**: Fast lookups + insertion order

**Comparison:**

| Feature | HashSet | TreeSet | LinkedHashSet |
|---------|---------|---------|---------------|
| **Order** | None | Sorted | Insertion |
| **Performance** | O(1) ✅ | O(log n) | O(1) ✅ |
| **Null** | ✅ Allowed | ❌ Not allowed | ✅ Allowed |
| **Use Case** | Fast lookup | Sorted set | Ordered + Fast |

**Example:**
```java
// ✅ HashSet: Fast lookups, no order
Set<String> set = new HashSet<>();
set.add("zebra");
set.add("apple");
set.add("banana");
// Order: undefined (may be: banana, apple, zebra)

// ✅ TreeSet: Sorted order
Set<String> set = new TreeSet<>();
set.add("zebra");
set.add("apple");
set.add("banana");
// Order: apple, banana, zebra (sorted)

// ✅ LinkedHashSet: Insertion order
Set<String> set = new LinkedHashSet<>();
set.add("zebra");
set.add("apple");
set.add("banana");
// Order: zebra, apple, banana (insertion order)
```

### 3.3. Map Implementations

#### HashMap vs TreeMap vs LinkedHashMap

**HashMap:**
- **Internal**: Hash table (array + buckets)
- **Order**: No order
- **Performance**: O(1) average
- **Null**: Allows one null key
- **Use Case**: Fast lookups, no order needed

**TreeMap:**
- **Internal**: Red-black tree
- **Order**: Sorted by key
- **Performance**: O(log n)
- **Null**: Not allowed
- **Use Case**: Sorted map, range queries

**LinkedHashMap:**
- **Internal**: Hash table + linked list
- **Order**: Insertion order or access order
- **Performance**: O(1) average
- **Null**: Allows one null key
- **Use Case**: LRU cache, ordered map

**Comparison:**

| Feature | HashMap | TreeMap | LinkedHashMap |
|---------|---------|---------|---------------|
| **Order** | None | Sorted | Insertion/Access |
| **Performance** | O(1) ✅ | O(log n) | O(1) ✅ |
| **Null Key** | ✅ Allowed | ❌ Not allowed | ✅ Allowed |
| **Use Case** | Fast lookup | Sorted map | LRU cache |

**Example:**
```java
// ✅ HashMap: Fast lookups
Map<String, Integer> map = new HashMap<>();
map.put("zebra", 3);
map.put("apple", 1);
map.put("banana", 2);

// ✅ TreeMap: Sorted by key
Map<String, Integer> map = new TreeMap<>();
map.put("zebra", 3);
map.put("apple", 1);
map.put("banana", 2);
// Order: apple=1, banana=2, zebra=3

// ✅ LinkedHashMap: LRU cache (access order)
Map<String, Integer> cache = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {
        return size() > 100;  // Keep only 100 entries
    }
};
```

#### ConcurrentHashMap

**Thread-safe HashMap without global lock:**
- **Internal**: Segment-based locking (Java 7) or CAS + synchronized (Java 8+)
- **Performance**: Better than Hashtable (no global lock)
- **Null**: Not allowed (concurrent operations)

**Example:**
```java
// ✅ Thread-safe without global lock
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("key", 1);
map.get("key");  // Thread-safe

// Atomic operations
map.computeIfAbsent("key", k -> 1);
map.merge("key", 1, Integer::sum);
```

### 3.4. Queue Implementations

#### PriorityQueue

**Min/Max Heap implementation:**
```java
// ✅ Min heap (default)
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(1);
minHeap.offer(3);
minHeap.poll();  // 1 (smallest)

// ✅ Max heap (reverse comparator)
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
maxHeap.offer(5);
maxHeap.offer(1);
maxHeap.offer(3);
maxHeap.poll();  // 5 (largest)
```

#### BlockingQueue

**Thread-safe queue with blocking operations:**
```java
// ✅ Producer-Consumer pattern
BlockingQueue<String> queue = new LinkedBlockingQueue<>(10);

// Producer
queue.put("item");  // Blocks if full

// Consumer
String item = queue.take();  // Blocks if empty

// Try without blocking
boolean added = queue.offer("item", 1, TimeUnit.SECONDS);
String item = queue.poll(1, TimeUnit.SECONDS);
```

## 4. Stream API Optimization

### 4.1. Stream Performance

#### Parallel vs Sequential Streams

**Sequential Stream:**
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Sequential processing
int sum = numbers.stream()
    .mapToInt(i -> i * 2)
    .sum();  // Single-threaded
```

**Parallel Stream:**
```java
// Parallel processing
int sum = numbers.parallelStream()
    .mapToInt(i -> i * 2)
    .sum();  // Multi-threaded
```

**When to Use Parallel:**
- ✅ Large datasets (> 10,000 elements)
- ✅ CPU-intensive operations
- ✅ Independent operations (no shared state)
- ❌ Small datasets (< 1,000 elements)
- ❌ I/O-bound operations
- ❌ Operations with shared state

**Example:**
```java
// ✅ Good: Large dataset, CPU-intensive
List<Integer> largeList = IntStream.range(0, 1000000)
    .boxed()
    .collect(Collectors.toList());

int sum = largeList.parallelStream()
    .mapToInt(i -> compute(i))  // CPU-intensive
    .sum();

// ❌ Bad: Small dataset
int sum = Arrays.asList(1, 2, 3).parallelStream()
    .mapToInt(i -> i)
    .sum();  // Overhead > benefit
```

### 4.2. Stream Optimization Patterns

#### 1. Filter Early
```java
// ❌ BAD: Process all elements before filtering
List<String> result = list.stream()
    .map(String::toUpperCase)
    .map(s -> s + "!")
    .filter(s -> s.length() > 5)
    .collect(Collectors.toList());

// ✅ GOOD: Filter first to reduce processing
List<String> result = list.stream()
    .filter(s -> s.length() > 3)  // Filter early
    .map(String::toUpperCase)
    .map(s -> s + "!")
    .collect(Collectors.toList());
```

#### 2. Avoid Intermediate Collections
```java
// ❌ BAD: Create intermediate collections
List<String> filtered = list.stream()
    .filter(s -> s.startsWith("A"))
    .collect(Collectors.toList());  // Intermediate collection

List<String> upper = filtered.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());

// ✅ GOOD: Chain operations
List<String> result = list.stream()
    .filter(s -> s.startsWith("A"))
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

#### 3. Use Primitive Streams
```java
// ❌ BAD: Boxed primitives
List<Integer> numbers = IntStream.range(0, 1000000)
    .boxed()  // Boxing overhead
    .collect(Collectors.toList());

// ✅ GOOD: Primitive stream
int[] numbers = IntStream.range(0, 1000000)
    .toArray();  // No boxing
```

#### 4. Collect Once
```java
// ❌ BAD: Multiple terminal operations
long count = stream.count();
List<String> list = stream.collect(Collectors.toList());
// Error: stream already consumed!

// ✅ GOOD: Single terminal operation
List<String> list = stream.collect(Collectors.toList());
long count = list.size();
```

### 4.3. Common Stream Operations

**Filter and Map:**
```java
List<String> result = list.stream()
    .filter(s -> s.length() > 5)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

**Reduce:**
```java
// Sum
int sum = numbers.stream()
    .reduce(0, Integer::sum);

// Max
Optional<Integer> max = numbers.stream()
    .reduce(Integer::max);
```

**Grouping:**
```java
// Group by length
Map<Integer, List<String>> grouped = list.stream()
    .collect(Collectors.groupingBy(String::length));

// Group by length, count
Map<Integer, Long> countByLength = list.stream()
    .collect(Collectors.groupingBy(String::length, Collectors.counting()));
```

**Partitioning:**
```java
// Partition by predicate
Map<Boolean, List<String>> partitioned = list.stream()
    .collect(Collectors.partitioningBy(s -> s.length() > 5));
```

## 5. Exception Handling Best Practices

### 5.1. Exception Hierarchy

```
Throwable
├── Error (don't catch)
│   ├── OutOfMemoryError
│   └── StackOverflowError
└── Exception
    ├── RuntimeException (unchecked)
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   └── IndexOutOfBoundsException
    └── CheckedException
        ├── IOException
        ├── SQLException
        └── ClassNotFoundException
```

### 5.2. Best Practices

#### 1. Catch Specific Exceptions
```java
// ❌ BAD: Catch generic Exception
try {
    processFile(file);
} catch (Exception e) {
    // Catches everything, hard to debug
}

// ✅ GOOD: Catch specific exceptions
try {
    processFile(file);
} catch (FileNotFoundException e) {
    // Handle file not found
} catch (IOException e) {
    // Handle I/O error
}
```

#### 2. Don't Swallow Exceptions
```java
// ❌ BAD: Swallow exception
try {
    processFile(file);
} catch (IOException e) {
    // Silent failure, hard to debug
}

// ✅ GOOD: Log and rethrow or handle
try {
    processFile(file);
} catch (IOException e) {
    log.error("Failed to process file", e);
    throw new ProcessingException("File processing failed", e);
}
```

#### 3. Use Try-with-Resources
```java
// ❌ BAD: Manual resource management
FileInputStream fis = null;
try {
    fis = new FileInputStream(file);
    // Process file
} finally {
    if (fis != null) {
        try {
            fis.close();
        } catch (IOException e) {
            // Handle
        }
    }
}

// ✅ GOOD: Try-with-resources (auto-close)
try (FileInputStream fis = new FileInputStream(file)) {
    // Process file
} catch (IOException e) {
    // Handle
}
// Resources auto-closed
```

#### 4. Provide Meaningful Messages
```java
// ❌ BAD: Generic message
throw new IllegalArgumentException("Invalid argument");

// ✅ GOOD: Specific message
throw new IllegalArgumentException("Age cannot be negative, got: " + age);
```

#### 5. Preserve Stack Trace
```java
// ❌ BAD: Lose stack trace
catch (IOException e) {
    throw new ProcessingException("Processing failed");
}

// ✅ GOOD: Preserve stack trace
catch (IOException e) {
    throw new ProcessingException("Processing failed", e);
}
```

#### 6. Use Custom Exceptions
```java
// ✅ GOOD: Domain-specific exceptions
public class OrderNotFoundException extends RuntimeException {
    public OrderNotFoundException(Long orderId) {
        super("Order not found: " + orderId);
    }
}

// Usage
if (order == null) {
    throw new OrderNotFoundException(orderId);
}
```

### 5.3. Common Anti-Patterns

**1. Catching and Ignoring:**
```java
// ❌ BAD
try {
    process();
} catch (Exception e) {
    // Ignore
}
```

**2. Catching and Returning Null:**
```java
// ❌ BAD
public User getUser(Long id) {
    try {
        return repository.findById(id);
    } catch (Exception e) {
        return null;  // Hide error
    }
}

// ✅ GOOD: Return Optional
public Optional<User> getUser(Long id) {
    try {
        return Optional.of(repository.findById(id));
    } catch (Exception e) {
        log.error("Failed to get user", e);
        return Optional.empty();
    }
}
```

**3. Throwing Generic Exception:**
```java
// ❌ BAD
public void process() throws Exception {
    // Too generic
}

// ✅ GOOD: Throw specific exceptions
public void process() throws IOException, SQLException {
    // Specific exceptions
}
```

**4. Exception in Finally Block:**
```java
// ❌ BAD: Exception in finally may hide original exception
try {
    process();
} finally {
    cleanup();  // If this throws, original exception lost
}

// ✅ GOOD: Handle exceptions in finally
try {
    process();
} finally {
    try {
        cleanup();
    } catch (Exception e) {
        log.error("Cleanup failed", e);
    }
}
```

---

This content provides production-ready Java Core knowledge including Collections framework deep dive, Stream API optimization, and Exception handling best practices with real scenarios and complete solutions.
