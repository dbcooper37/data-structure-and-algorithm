# Missing Content: TCC Transaction + Snowflake Solutions

## For Phan6_Distributed_System.md

---

## Section 6.3.2: ⭐ TCC Transaction - Production Implementation

### Overview

TCC (Try-Confirm-Cancel) là pattern cho distributed transactions với 3 phases:
- **Try**: Reserve resources (e.g., freeze balance, reserve stock)
- **Confirm**: Commit changes (e.g., deduct balance, deduct stock)
- **Cancel**: Rollback if any service fails (e.g., unfreeze balance, release stock)

### Complete Production Example: Order Service

**Scenario**: User creates order → Need to:
1. Reserve inventory
2. Freeze user balance
3. Create order record

**Dependency:**
```xml
<!-- TCC Framework: Seata-TCC or Hmily -->
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

**Implementation:**

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderDao orderDao;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private AccountService accountService;
    
    /**
     * Main business method with @GlobalTransactional
     */
    @GlobalTransactional
    public void createOrder(OrderCreateRequest request) {
        // Phase 1: Try - All services reserve resources
        tryCreateOrder(request);
        
        // If all Try succeed → Seata calls Confirm automatically
        // If any Try fails → Seata calls Cancel automatically
    }
    
    /**
     * Try Phase: Reserve all resources
     */
    @TwoPhaseBusinessAction(
        name = "createOrder",
        commitMethod = "confirmCreateOrder",
        rollbackMethod = "cancelCreateOrder"
    )
    public boolean tryCreateOrder(OrderCreateRequest request) {
        Long userId = request.getUserId();
        Long productId = request.getProductId();
        Integer quantity = request.getQuantity();
        BigDecimal amount = request.getAmount();
        
        // Generate business key for idempotency
        String businessKey = "ORDER_" + request.getRequestId();
        
        // Check if already processed (idempotency)
        if (orderDao.existsByBusinessKey(businessKey)) {
            return true;  // Already processed
        }
        
        // 1. Try reserve inventory
        boolean inventoryReserved = inventoryService.tryReserve(productId, quantity, businessKey);
        if (!inventoryReserved) {
            throw new BusinessException("Inventory insufficient");
        }
        
        // 2. Try freeze account balance
        boolean balanceFrozen = accountService.tryFreeze(userId, amount, businessKey);
        if (!balanceFrozen) {
            throw new BusinessException("Balance insufficient");
        }
        
        // 3. Create order with status PENDING
        Order order = new Order();
        order.setUserId(userId);
        order.setProductId(productId);
        order.setQuantity(quantity);
        order.setAmount(amount);
        order.setStatus("PENDING");
        order.setBusinessKey(businessKey);
        order.setCreateTime(new Date());
        orderDao.insert(order);
        
        return true;
    }
    
    /**
     * Confirm Phase: Commit all changes
     */
    public boolean confirmCreateOrder(BusinessActionContext context) {
        String businessKey = context.getActionContext("businessKey");
        
        // Check if already confirmed (idempotency)
        Order order = orderDao.findByBusinessKey(businessKey);
        if (order == null) {
            return true;  // Already confirmed and deleted PENDING record
        }
        
        if ("CONFIRMED".equals(order.getStatus())) {
            return true;  // Already confirmed
        }
        
        try {
            // 1. Confirm inventory deduction
            inventoryService.confirmReserve(order.getProductId(), order.getQuantity(), businessKey);
            
            // 2. Confirm account deduction
            accountService.confirmFreeze(order.getUserId(), order.getAmount(), businessKey);
            
            // 3. Update order status
            order.setStatus("CONFIRMED");
            order.setConfirmTime(new Date());
            orderDao.update(order);
            
            return true;
            
        } catch (Exception e) {
            // Confirm failed → Will retry
            log.error("Confirm order failed: {}", businessKey, e);
            return false;
        }
    }
    
    /**
     * Cancel Phase: Rollback all changes
     */
    public boolean cancelCreateOrder(BusinessActionContext context) {
        String businessKey = context.getActionContext("businessKey");
        
        // Check if already cancelled (idempotency)
        Order order = orderDao.findByBusinessKey(businessKey);
        if (order == null) {
            return true;  // Already cancelled and deleted
        }
        
        if ("CANCELLED".equals(order.getStatus())) {
            return true;  // Already cancelled
        }
        
        try {
            // 1. Cancel inventory reservation
            inventoryService.cancelReserve(order.getProductId(), order.getQuantity(), businessKey);
            
            // 2. Cancel account freeze
            accountService.cancelFreeze(order.getUserId(), order.getAmount(), businessKey);
            
            // 3. Update order status or delete
            order.setStatus("CANCELLED");
            order.setCancelTime(new Date());
            orderDao.update(order);
            
            return true;
            
        } catch (Exception e) {
            // Cancel failed → Will retry
            log.error("Cancel order failed: {}", businessKey, e);
            return false;
        }
    }
}
```

**Inventory Service Implementation:**

```java
@Service
public class InventoryService {
    
    @Autowired
    private InventoryDao inventoryDao;
    
    @Autowired
    private InventoryFreezeDao freezeDao;
    
    /**
     * Try: Reserve inventory
     */
    public boolean tryReserve(Long productId, Integer quantity, String businessKey) {
        // Check if already reserved
        if (freezeDao.existsByBusinessKey(businessKey)) {
            return true;
        }
        
        // Check available stock
        Inventory inventory = inventoryDao.selectForUpdate(productId);
        if (inventory.getAvailable() < quantity) {
            return false;
        }
        
        // Reduce available, increase frozen
        inventory.setAvailable(inventory.getAvailable() - quantity);
        inventory.setFrozen(inventory.getFrozen() + quantity);
        inventoryDao.update(inventory);
        
        // Record freeze
        InventoryFreeze freeze = new InventoryFreeze();
        freeze.setProductId(productId);
        freeze.setQuantity(quantity);
        freeze.setBusinessKey(businessKey);
        freeze.setStatus("FROZEN");
        freeze.setCreateTime(new Date());
        freezeDao.insert(freeze);
        
        return true;
    }
    
    /**
     * Confirm: Actually deduct stock
     */
    public void confirmReserve(Long productId, Integer quantity, String businessKey) {
        InventoryFreeze freeze = freezeDao.findByBusinessKey(businessKey);
        if (freeze == null || "CONFIRMED".equals(freeze.getStatus())) {
            return;  // Already confirmed
        }
        
        // Reduce frozen count
        Inventory inventory = inventoryDao.selectForUpdate(productId);
        inventory.setFrozen(inventory.getFrozen() - quantity);
        inventoryDao.update(inventory);
        
        // Mark as confirmed
        freeze.setStatus("CONFIRMED");
        freeze.setConfirmTime(new Date());
        freezeDao.update(freeze);
    }
    
    /**
     * Cancel: Release reserved stock
     */
    public void cancelReserve(Long productId, Integer quantity, String businessKey) {
        InventoryFreeze freeze = freezeDao.findByBusinessKey(businessKey);
        if (freeze == null || "CANCELLED".equals(freeze.getStatus())) {
            return;  // Already cancelled
        }
        
        // Return to available
        Inventory inventory = inventoryDao.selectForUpdate(productId);
        inventory.setAvailable(inventory.getAvailable() + quantity);
        inventory.setFrozen(inventory.getFrozen() - quantity);
        inventoryDao.update(inventory);
        
        // Mark as cancelled
        freeze.setStatus("CANCELLED");
        freeze.setCancelTime(new Date());
        freezeDao.update(freeze);
    }
}
```

### Common Production Pitfalls

#### Pitfall 1: Network Timeout

**Problem:**
```
Timeline:
1. Try phase succeeds
2. Network timeout before response returns
3. TCC framework thinks Try failed → Calls Cancel
4. But Try actually succeeded → Resources frozen but cancelled!
```

**Solution:**
```java
// Idempotency check in all phases
public boolean tryReserve(...) {
    // Check if already processed
    if (freezeDao.existsByBusinessKey(businessKey)) {
        return true;  // Already done, return success
    }
    // ... rest of logic
}
```

#### Pitfall 2: Partial Failure

**Problem:**
```
Scenario:
- Inventory.confirmReserve() succeeds
- Account.confirmFreeze() fails
→ Inventory already deducted but balance not deducted!
```

**Solution:**
```java
// TCC framework handles this automatically
// If any Confirm fails:
// 1. Framework retries Confirm (with exponential backoff)
// 2. If retry exhausted → Manual intervention needed
// 3. Log error for admin to check

// Implement compensate log
@Slf4j
public boolean confirmCreateOrder(BusinessActionContext context) {
    try {
        inventoryService.confirmReserve(...);
        accountService.confirmFreeze(...);
        return true;
    } catch (Exception e) {
        // Log for manual fix
        compensateLogDao.insert(new CompensateLog(
            businessKey,
            "CONFIRM_FAILED",
            e.getMessage(),
            context
        ));
        return false;
    }
}
```

#### Pitfall 3: Duplicate Cancel

**Problem:**
```
Scenario:
- Cancel called 2 times due to retry
- First Cancel: Unfreeze 100 (correct)
- Second Cancel: Unfreeze 100 again (wrong - double unfreeze!)
```

**Solution:**
```java
public void cancelReserve(...) {
    // Check status first
    InventoryFreeze freeze = freezeDao.findByBusinessKey(businessKey);
    if (freeze == null || "CANCELLED".equals(freeze.getStatus())) {
        return;  // Already cancelled, do nothing
    }
    
    // Only cancel if status is FROZEN
    if (!"FROZEN".equals(freeze.getStatus())) {
        log.warn("Unexpected freeze status: {}", freeze.getStatus());
        return;
    }
    
    // Safe to cancel
    // ... unfreeze logic
}
```

---

## Section 6.4.3: ⭐ Snowflake Distributed ID - Clock Rollback Solutions

### Problem

Snowflake generates IDs based on timestamp:
```
ID Structure (64 bits):
[1 bit unused][41 bits timestamp][10 bits machine ID][12 bits sequence]

When clock rolls back (e.g., NTP sync):
- Time goes from 10:00:05 → 10:00:00 (5 seconds back)
- New IDs have SMALLER timestamp than previous IDs
- Can generate duplicate IDs!
```

### Solution 1: Wait for Clock Sync (Conservative)

```java
public class SnowflakeIdGenerator {
    private long lastTimestamp = -1L;
    
    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        
        // Clock rollback detected
        if (timestamp < lastTimestamp) {
            long offset = lastTimestamp - timestamp;
            
            if (offset > 5000) {
                // Rollback > 5s → Serious issue, reject
                throw new ClockRollbackException(
                    "Clock rolled back by " + offset + "ms, refusing to generate ID"
                );
            }
            
            // Small rollback → Wait for clock to catch up
            try {
                Thread.sleep(offset);
                timestamp = System.currentTimeMillis();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
        
        // ... rest of ID generation logic
        lastTimestamp = timestamp;
        return id;
    }
}
```

**Pros:**
- Guaranteed no duplicate IDs
- Simple logic

**Cons:**
- Blocks ID generation during rollback
- High latency spike if large rollback

### Solution 2: Reject and Throw Exception (Fail-Fast)

```java
public class SnowflakeIdGenerator {
    private long lastTimestamp = -1L;
    private static final long MAX_BACKWARD_MS = 5000;  // 5 seconds
    
    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        
        if (timestamp < lastTimestamp) {
            long offset = lastTimestamp - timestamp;
            
            // Always reject on clock rollback
            throw new ClockRollbackException(
                "Clock moved backwards by " + offset + "ms. " +
                "Refusing to generate id for " + offset + "ms"
            );
        }
        
        // ... rest of logic
        lastTimestamp = timestamp;
        return id;
    }
}
```

**Pros:**
- Fail-fast, admin can detect issue immediately
- No risk of duplicate IDs

**Cons:**
- Service unavailable during rollback
- Requires monitoring and alerting

### Solution 3: Use Backup Worker ID (Recommended)

```java
public class SnowflakeIdGenerator {
    private long workerId;
    private final long backupWorkerId;
    private long lastTimestamp = -1L;
    private long sequence = 0L;
    
    public SnowflakeIdGenerator(long workerId, long backupWorkerId) {
        this.workerId = workerId;
        this.backupWorkerId = backupWorkerId;
    }
    
    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        
        // Clock rollback detected
        if (timestamp < lastTimestamp) {
            long offset = lastTimestamp - timestamp;
            
            log.warn("Clock rolled back by {}ms, switching to backup worker ID", offset);
            
            // Switch to backup worker ID
            workerId = backupWorkerId;
            
            // Reset sequence
            sequence = 0L;
            
            // Continue with current timestamp
            // (Different worker ID → No duplicate)
        }
        
        // Normal logic
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & MAX_SEQUENCE;
            if (sequence == 0) {
                // Sequence exhausted, wait for next millisecond
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0L;
        }
        
        lastTimestamp = timestamp;
        
        // Generate ID
        return ((timestamp - EPOCH) << TIMESTAMP_SHIFT)
            | (workerId << WORKER_ID_SHIFT)
            | sequence;
    }
    
    private long waitNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}
```

**Pros:**
- No blocking, high availability
- No duplicate IDs (different worker ID)
- Graceful degradation

**Cons:**
- Requires pre-allocated backup worker IDs
- Slightly more complex logic

### Solution 4: NTP Synchronization (Prevention)

**Best Practice: Prevent clock rollback in first place**

```bash
# Use NTP with gradual clock adjustment (slew mode)
# Instead of stepping (instant jump)

# /etc/ntp.conf
server ntp1.example.com prefer
server ntp2.example.com
server ntp3.example.com

# Use slew mode (gradual adjust, no rollback)
tinker panic 0

# Monitor clock offset
ntpq -p

# Alert if offset > 1 second
```

### Comparison

| Solution | Availability | Duplicate Risk | Complexity | Recommended |
|----------|-------------|---------------|------------|-------------|
| Wait | Low (blocks) | None | Simple | ❌ No |
| Reject | Low (throws) | None | Simple | ⚠️ Dev only |
| Backup Worker ID | High | None | Medium | ✅ Production |
| NTP Slew | High | None | Low (infra) | ✅ Always enable |

**Recommended Approach:**
```
1. Enable NTP slew mode (prevention)
2. Use Backup Worker ID (protection)
3. Monitor clock offset (detection)
4. Alert on clock rollback (response)
```

---

This content completes the missing TCC and Snowflake sections with production-ready implementations.
