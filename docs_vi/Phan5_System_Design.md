# Part 5: System Design (Thiết kế hệ thống)

## 5.1. Design Patterns (Mẫu thiết kế)

**Design Pattern** là các giải pháp tiêu chuẩn cho các vấn đề thường gặp trong thiết kế phần mềm.

Có 3 nhóm chính:
1.  **Creational (Khởi tạo)**: Singleton, Factory, Builder...
2.  **Structural (Cấu trúc)**: Adapter, Decorator, Proxy...
3.  **Behavioral (Hành vi)**: Strategy, Observer, Template Method...

### 5.1.1. ⭐ Singleton Pattern

**Mục đích**: Đảm bảo class chỉ có **1 instance duy nhất** và cung cấp điểm truy cập toàn cục.

**Use cases**: ConfigManager, ConnectionPool, ApplicationContext.

#### 1. Lazy Loading (Không an toàn thread)
```java
public class Singleton {
    private static Singleton instance;
    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

#### 2. ⭐ Double-Checked Locking (An toàn, Hiệu suất cao)
Cách chuẩn nhất để implement Singleton lười biếng (lazy).

```java
public class Singleton {
    // volatile ngăn chặn instruction reordering
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

#### 3. Static Inner Class (Recommended ✅)
Tận dụng cơ chế class loading của JVM để đảm bảo thread-safety và lazy loading.

```java
public class Singleton {
    private Singleton() {}

    private static class SingletonHolder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return SingletonHolder.INSTANCE;
    }
}
```

#### 4. Enum (Recommended for prevention of reflection attack)
Cách an toàn nhất, ngăn chặn tấn công qua Reflection và Serialization.

```java
public enum Singleton {
    INSTANCE;
    public void doSomething() { ... }
}
```

---

### 5.1.2. Factory Pattern

**Mục đích**: Tạo objects mà không để lộ logic khởi tạo cho client.

#### Simple Factory
```public class ShapeFactory {
    public Shape getShape(String shapeType) {
        if (shapeType.equalsIgnoreCase("CIRCLE")) return new Circle();
        if (shapeType.equalsIgnoreCase("SQUARE")) return new Square();
        return null;
    }
}
```

#### Spring Bean Factory
Spring sử dụng Factory pattern cho **BeanFactory** và **ApplicationContext** để tạo và quản lý beans.

---

### 5.1.3. ⭐ Proxy Pattern

**Mục đích**: Cung cấp **đại diện** (placeholder) cho object khác để kiểm soát truy cập hoặc thêm chức năng (logging, transaction) mà không sửa code gốc.

#### Static Proxy
Tạo class Proxy implement cùng interface với Target.
*   *Nhược điểm*: Phải viết class proxy cho mỗi class target → Code duplication.

#### Dynamic Proxy (JDK)
Tạo proxy tại **runtime** dùng Reflection. Chỉ proxy được Interface.

```java
InvocationHandler handler = new MyInvocationHandler(target);
MyInterface proxy = (MyInterface) Proxy.newProxyInstance(
    target.getClass().getClassLoader(),
    target.getClass().getInterfaces(),
    handler
);
```

#### CGLIB Proxy
Tạo subclass của Target class tại runtime. Proxy được cả Class (trừ final). Spring Boot dùng cách này mặc định.

**Ứng dụng**: Spring **AOP** (Transaction, Security, Logging).

---

### 5.1.4. Behavioral Patterns

#### ⭐ Strategy Pattern (Chiến lược)
Định nghĩa một họ thuật toán, đóng gói từng thuật toán lại, và làm chúng thay thế lẫn nhau.

**Ví dụ**: PaymentService (CreditCard, PayPal, COD).
```java
// Interface
public interface PaymentStrategy { void pay(int amount); }

// Strategy A
public class CreditCardStrategy implements PaymentStrategy { ... }

// Strategy B
public class PaypalStrategy implements PaymentStrategy { ... }

// Context dùng strategy
public class ShoppingCart {
    public void pay(PaymentStrategy strategy) {
        strategy.pay(calculateTotal());
    }
}
```
**Ứng dụng**: Thay thế `if-else` phức tạp.

#### Observer Pattern (Quan sát)
Defines one-to-many dependency. Khi object trạng thái thay đổi, tất cả dependents được thông báo.

**Ứng dụng**: Event Listener, Message Queue (Pub/Sub).

#### Template Method Pattern
Định nghĩa khung của thuật toán, để subclass implement các bước cụ thể.

**Ứng dụng**: `JdbcTemplate`, `RedisTemplate` trong Spring.

---

## 5.2. System Design Basics

### 5.2.1. ⭐ RESTful API Design

**REST** (Representational State Transfer) là phong cách kiến trúc cho web services.

**1. Resource Naming (Danh từ, số nhiều)**
*   ✅ `GET /users` (Lấy list user)
*   ✅ `GET /users/1` (Lấy user ID 1)
*   ✅ `POST /users` (Tạo user)
*   ✅ `DELETE /users/1` (Xóa user ID 1)
*   ❌ `/getUsers`, `/createUser` (Không dùng động từ trong URL!)

**2. HTTP Methods (Verbs)**
*   **GET**: Retrieve resource (Safe, Idempotent).
*   **POST**: Create resource (Not idempotent).
*   **PUT**: Update/Replace resource (Idempotent).
*   **PATCH**: Partial update (Not idempotent theoretically, but usually is).
*   **DELETE**: Delete resource (Idempotent).

**3. HTTP Status Codes**
*   **200 OK**: Thành công.
*   **201 Created**: Tạo thành công (POST).
*   **204 No Content**: Xóa thành công (DELETE).
*   **400 Bad Request**: Lỗi input client.
*   **401 Unauthorized**: Chưa đăng nhập.
*   **403 Forbidden**: Đã đăng nhập nhưng không có quyền.
*   **404 Not Found**: Không tìm thấy resource.
*   **500 Internal Server Error**: Lỗi server.

**4. Idempotency (Tính lũy đẳng)**
Thực hiện 1 lần hay N lần đều cho cùng kết quả server state (Resource side).
*   `GET`, `PUT`, `DELETE`: Idempotent.
*   `POST`: **Non-idempotent** (gọi 2 lần tạo 2 resources).

### 5.2.2. Naming Conventions (Quy ước đặt tên)

| Style | Example | Use Case (Java/System) |
|-------|---------|------------------------|
| **UpperCamelCase** | `OrderService`, `User` | Class name, Interface |
| **lowerCamelCase** | `userService`, `userId` | Method, Variable |
| **snake_case** | `order_service`, `user_id` | Database column, JSON field (đôi khi) |
| **kebab-case** | `order-service`, `api/v1/users` | URL, Message Queue topic |
| **UPPER_SNAKE** | `MAX_RETRY`, `STATUS_OK` | Constant, Enum |

### 5.2.3. Monolith vs Microservices

| Feature | Monolith (Đơn khối) | Microservices (Vi dịch vụ) |
|---------|---------------------|----------------------------|
| **Deployment** | 1 file (WAR/JAR) duy nhất | Nhiều services deploy riêng lẻ |
| **Scalability** | Scale toàn bộ app (nặng nề) | Scale từng service (linh hoạt) |
| **Complexity** | Đơn giản ban đầu | Phức tạp (network, distributed tx) |
| **Tech Stack** | Fix cứng 1 ngôn ngữ/framework | Đa dạng (Polyglot) |
| **Fault Tolerance** | Lỗi 1 phần có thể sập cả app | Lỗi service nào cách ly service đó |
| **Phù hợp** | Startups, team nhỏ, app đơn giản | Enterprise, team lớn, app phức tạp |

---

*Kết thúc Design Pattern & System Basics. Tiếp tục Security & Scheduling...*

## 5.3. Authentication & Security (Xác thực & Bảo mật)

### 5.3.1. ⭐ Cookie vs Session vs Token

#### 1. Cookie & Session (Stateful)
*   **Cookie**: File nhỏ lưu ở **Browser**, gửi kèm mỗi request. Dùng để lưu Session ID.
*   **Session**: Dữ liệu lưu ở **Server** (Memory/Redis), ánh xạ qua Session ID.

**Flow:**
1.  Client login → Server tạo Session, lưu UserInfo → Trả về `JESSIONID` trong Cookie.
2.  Client request + Cookie(`JSESSIONID`) → Server check Session → OK.

**Nhược điểm:**
*   ❌ **Scalability**: Khó scale ngang (Session sticky hoặc phải dùng Distributed Session với Redis).
*   ❌ **Mobile App**: Cookie kém tương thích với native mobile apps.
*   ❌ **CSRF**: Dễ bị tấn công CSRF.

#### 2. Token-Based Authentication (Stateless - JWT)
**JWT (JSON Web Token)** chứa thông tin user (payload) được ký (signed) bởi server.

**Flow:**
1.  Client login → Server verify → Tạo JWT (Header.Payload.Signature) → Trả về Client.
2.  Client lưu JWT (LocalStorage/Cookie).
3.  Client request + Header `Authorization: Bearer <token>` → Server verify signature → OK.

**Ưu điểm:**
*   ✅ **Stateless**: Server không lưu trạng thái → Dễ scale.
*   ✅ **Cross-domain**: Dễ dàng dùng cho SSO, Mobile App.
*   ✅ **Performance**: Giảm tải Server (không cần tra cứu session DB/Redis liên tục).

**Nhược điểm:**
*   ❌ **Invalidation**: Khó thu hồi (ban) token trước khi hết hạn (trừ khi dùng blacklist).
*   ❌ **Size**: Token lớn hơn Cookie ID → Tăng bandwidth.

### 5.3.2. ⭐ JWT Structure

JWT gồm 3 phần tách nhau bởi dấu chấm (`.`): `aaaaaa.bbbbbb.cccccc`

**1. Header** (Algorithm & Type)
```json
{ "alg": "HS256", "typ": "JWT" }
```

**2. Payload** (Data - Claims)
Chứa thông tin user (không để mật khẩu!).
```json
{ "sub": "1234567890", "name": "John Doe", "role": "admin", "iat": 1516239022 }
```

**3. Signature** (Chữ ký an toàn)
```javascript
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  "secret_key"
)
```

⚠️ **Lưu ý quan trọng**: Payload chỉ được **Base64 encoded**, không phải encrypted. **Ai cũng đọc được payload!** → Không để data nhạy cảm (password) trong payload.

### 5.3.3. ⭐ SSO (Single Sign-On) & OAuth 2.0

**SSO**: Đăng nhập 1 lần, truy cập được nhiều hệ thống (Google, Facebook logins).

**OAuth 2.0**: Giao thức ủy quyền (Authorization).

**Các Role trong OAuth 2.0:**
1.  **Resource Owner**: User.
2.  **Client**: App muốn truy cập data (Website/Mobile App).
3.  **Authorization Server**: Server cấp token (Google Auth).
4.  **Resource Server**: Server chứa data (Google Photos).

**Authorization Code Flow (Chuẩn nhất):**
1.  User click "Login with Google".
2.  Redirect đến Google Auth Page.
3.  User login & approve.
4.  Google redirect về Client với **Authorization Code**.
5.  Client gửi Code + ClientSecret lên Google để đổi lấy **Access Token**.
6.  Client dùng Token gọi API.

### 5.3.4. Common Security Attacks

#### 1. SQL Injection
Attacker chèn mã SQL vào input để thao tác DB.
*   *Attack*: `username = "admin' --"`
*   *Tác hại*: Bypass login, xóa data.
*   *Fix*: Dùng **Prepared Statement** (`#{}` trong MyBatis).

#### 2. XSS (Cross-Site Scripting)
Attacker chèn script độc hại (JavaScript) vào web để chạy trên browser nạn nhân.
*   *Attack*: Comment chứa `<script>stealCookie()</script>`.
*   *Tác hại*: Ăn cắp Cookie, Session, Redirect user.
*   *Fix*: **HTML Escape** output (chuyển `<` thành `&lt;`).

#### 3. CSRF (Cross-Site Request Forgery)
Attacker lừa user (đang login) click link thực hiện hành động ngoài ý muốn.
*   *Attack*: User truy cập web lạ → Web lạ gửi request `POST banking.com/transfer` (kèm cookie thật của user).
*   *Fix*: Sử dụng **CSRF Token** (hidden field trong form) hoặc dùng `SameSite` Cookie attribute.

---

## 5.4. Scheduled Tasks (Tác vụ định kỳ)

### 5.4.1. Single-node Scheduling

**1. Java Timer / ScheduledExecutorService**
*   Cơ bản của JDK.

**2. Spring @Scheduled** (Phổ biến nhất)
```java
@Component
public class ScheduledTasks {

    // Chạy mỗi 5s (fixedRate: tính từ lúc bắt đầu)
    @Scheduled(fixedRate = 5000)
    public void reportCurrentTime() { ... }

    // Cron expression (Giây Phút Giờ Ngày Tháng Thứ)
    // Chạy lúc 10:15 AM mỗi ngày
    @Scheduled(cron = "0 15 10 * * ?")
    public void cronJob() { ... }
}
```

*   **Nhược điểm**: Chỉ chạy trên **1 server**. Nếu deploy 2 instances → job chạy 2 lần (trùng lặp)!

### 5.4.2. Distributed Scheduling

Khi có nhiều server (Cluster), cần đảm bảo job **chỉ chạy trên 1 node** hoặc scanr data không trùng lặp.

**Giải pháp:**

**1. Redis / DB Lock (Tự chế)**
*   Dùng `@Scheduled` + Redis `SETNX` (Distributed Lock).
*   Ai lấy được lock thì chạy.
*   *Đơn giản nhưng thiếu tính năng monitoring/retry.*

**2. Quartz Cluster**
*   Framework lâu đời, mạnh mẽ.
*   Dùng **Database** để đồng bộ trạng thái giữa các nodes.
*   *Hơi nặng nề (Heavyweight).*

**3. XXL-JOB / Elastic-Job (Phổ biến tại TQ/VN)**
*   **XXL-JOB**: Có Admin Dashboard quản lý job, log, retry, sharding. Rất nhẹ và dễ dùng.
*   **Cơ chế**: Admin center trigger job → gửi request đến Executor (Service của bạn).

---

## 5.5. ⭐ High Concurrency System Design (Thiết kế hệ thống high concurrency)

### 5.5.1. Tại sao cần High Concurrency Design?

**Vấn đề:**
- Database chỉ chịu được **2,000-3,000 QPS**
- Traffic thực tế: **5,000-10,000+ QPS** (peak: 100,000+)
- → Database bị quá tải → System crash

**Solution: High Concurrency Architecture** với 6 thành phần chính:

### 5.5.2. ⭐ 6 Thành phần chính

**1. System Split (Chia nhỏ hệ thống)**

**Mục đích**: Tách monolith thành microservices, mỗi service có database riêng.

**Ví dụ:**
```
Monolith (1 DB) → User Service (DB1) + Order Service (DB2) + Product Service (DB3)
```

**Lợi ích:**
- Mỗi service scale độc lập
- Database load được phân tán
- Fault isolation (lỗi service này không ảnh hưởng service kia)

**Tools**: Dubbo, Spring Cloud

**2. Caching (Đa tầng cache)**

**Mục đích**: Giảm tải database bằng cách cache data nóng.

**Cache Strategy:**
- **L1 Cache**: Local cache (Caffeine, Guava) - Nhanh nhất, memory
- **L2 Cache**: Distributed cache (Redis) - Shared giữa các servers
- **L3 Cache**: Database - Source of truth

**Use case**: **Read-heavy** scenarios (80% read, 20% write)

**Cache Patterns:**
- **Cache-Aside**: App check cache → miss → query DB → update cache
- **Write-Through**: Write DB + cache cùng lúc
- **Write-Back**: Write cache → async flush to DB

**3. Message Queue (Async processing)**

**Mục đích**: Decouple producers và consumers, buffer writes.

**Use case:**
- **High write traffic**: Order creation, Payment processing
- **Async tasks**: Email sending, Logging, Analytics

**Flow:**
```
User Request → MQ → Consumer (async) → Database
```

**Benefits:**
- **Peak shaving**: Smooth traffic spikes
- **Reliability**: Retry mechanism
- **Scalability**: Multiple consumers

**4. Database Sharding (Phân mảnh database)**

**Mục đích**: Chia database/table thành nhiều shards.

**Sharding Strategies:**
- **Horizontal Sharding**: Split by range (user_id 1-1M → DB1, 1M-2M → DB2)
- **Hash Sharding**: `hash(user_id) % N` → Shard N
- **Directory-based**: Lookup table (user_id → shard_id)

**Challenges:**
- **Cross-shard queries**: Khó join giữa shards
- **Rebalancing**: Migrate data khi scale
- **Transaction**: Distributed transaction phức tạp

**5. Read-Write Separation (Tách đọc-ghi)**

**Mục đích**: Master-Slave architecture, Master write, Slaves read.

**Architecture:**
```
Write → Master DB
Read  → Slave DBs (multiple replicas)
```

**Benefits:**
- **Read scaling**: Thêm slaves để tăng read capacity
- **Load distribution**: Read traffic không ảnh hưởng write

**Challenges:**
- **Replication lag**: Slave data có thể cũ hơn Master (eventual consistency)
- **Route logic**: App phải biết route read/write

**6. Elasticsearch (Search & Analytics)**

**Mục đích**: Offload search queries từ database.

**Use cases:**
- **Full-text search**: Product search, User search
- **Analytics**: Aggregations, Statistics
- **Log analysis**: ELK stack

**Benefits:**
- **Distributed**: Auto-scale
- **Fast**: Inverted index, optimized for search
- **Flexible**: Schema-less, easy to add fields

### 5.5.3. ⭐ How to Design a Message Queue?

**Interview Question**: "Nếu bạn thiết kế một Message Queue, bạn sẽ làm như thế nào?"

**Key Design Points:**

**1. Scalability (Partition-based)**
```
Topic → Partitions → Machines
```
- Mỗi partition trên 1 machine
- Scale: Thêm partitions → Thêm machines
- Data migration: Rebalance partitions

**2. Persistence (Disk Storage)**
- **Sequential Write**: Fast (10x faster than random write)
- **Append-only log**: Simple, reliable
- **Segment files**: Rotate khi đầy

**3. High Availability (Replication)**
- **Leader-Follower**: 1 leader, N followers
- **Leader election**: Follower → Leader khi leader down
- **Replication factor**: 3 (1 leader + 2 followers)

**4. Zero Data Loss**
- **Producer**: `acks=all` (wait for all replicas)
- **Broker**: Sync flush to disk
- **Consumer**: Manual commit offset (after processing)

**5. Performance Optimization**
- **Batch**: Send multiple messages in one request
- **Compression**: Gzip, Snappy
- **Zero-copy**: Direct memory transfer

### 5.5.4. ⭐ Rate Limiting (Giới hạn lưu lượng)

**Mục đích**: Bảo vệ system khỏi traffic spikes, prevent DDoS.

**4 Algorithms:**

**1. Fixed Window Counter**
```java
// Limit: 100 requests/minute
if (requests_in_current_minute < 100) {
    allow();
} else {
    reject();
}
```

**Vấn đề**: **Boundary burst**
- 00:59: 100 requests
- 01:00: 100 requests
- → 200 requests trong 2 giây!

**2. Sliding Window**
```java
// Chia 1 phút thành 6 windows (mỗi window 10s)
// Count requests trong 6 windows gần nhất
if (sum(requests_in_last_6_windows) < 100) {
    allow();
}
```

**Ưu điểm**: Smooth hơn, giảm boundary burst

**3. Leaky Bucket**
```java
// Bucket có capacity cố định
// Water (requests) chảy ra với rate cố định
if (bucket.hasSpace()) {
    bucket.add(request);
    allow();
} else {
    reject();
}
```

**Đặc điểm**: **Smooth output rate** (nhưng có thể drop requests)

**4. Token Bucket (Khuyến nghị)**
```java
// Bucket chứa tokens
// Tokens được thêm vào với rate cố định
// Mỗi request lấy 1 token
if (bucket.hasToken()) {
    bucket.takeToken();
    allow();
} else {
    reject();
}
```

**Ưu điểm**: 
- **Burst support**: Cho phép burst trong giới hạn
- **Smooth**: Rate limiting linh hoạt

**Implementation (Redis):**
```java
// Spring Cloud Gateway
spring:
  cloud:
    gateway:
      routes:
        - filters:
          - name: RequestRateLimiter
            args:
              redis-rate-limiter.replenishRate: 10  # Tokens/second
              redis-rate-limiter.burstCapacity: 20  # Max tokens
```

### 5.5.5. System Design Interview Framework

**4-Step Approach:**

**Step 1: Requirements Clarification**
- **Functional**: What features?
- **Non-functional**: Scale (QPS, users), Latency, Availability

**Step 2: High-Level Design**
- **Architecture**: Components, Data flow
- **APIs**: Endpoints, Request/Response
- **Database Schema**: Tables, Relationships

**Step 3: Detailed Design**
- **Scaling**: Horizontal vs Vertical
- **Caching**: Strategy, Invalidation
- **Load Balancing**: Algorithm
- **Database**: Sharding, Replication

**Step 4: Optimization**
- **Bottlenecks**: Identify và fix
- **Trade-offs**: Consistency vs Availability
- **Monitoring**: Metrics, Alerts

**Example: Design URL Shortener (TinyURL)**

**Requirements:**
- Shorten long URL → Short URL
- Redirect short URL → Original URL
- Scale: 100M URLs, 1000:1 read:write ratio

**Design:**
1. **Encoding**: Base62 (0-9, a-z, A-Z) → 7 chars = 62^7 = 3.5 trillion
2. **Storage**: Key-Value (short_url → long_url)
3. **Database**: Shard by hash(short_url)
4. **Cache**: Redis (hot URLs)
5. **Load Balancer**: Round-robin

---

## Tổng kết Part 5: System Design

Đã hoàn thành **Part 5: System Design** với các kiến thức nền tảng:

✅ **5.1. Design Patterns** (~400 lines in memory):
- **Singleton**: Lazy, Double-Check Locking, Static Inner Class, Enum.
- **Factory, Proxy** (Static vs Dynamic).
- **Behavioral**: Strategy, Observer, Template Method.

✅ **5.2. System Basics**:
- **RESTful API**: Verbs, Status codes, Idempotency.
- **Naming**: CamelCase, Snake_case.
- **Architecture**: Monolith vs Microservices.

✅ **5.3. Authentication & Security**:
- **Cookie vs Session vs Token (JWT)**.
- **JWT Structure**: Header, Payload, Signature.
- **OAuth 2.0**: Authorization Code flow.
- **Attacks**: SQL Injection, XSS, CSRF & Prevention.

✅ **5.4. Scheduled Tasks**:
- Spring `@Scheduled` & Cron expressions.
- Distributed Scheduling problems & XXL-JOB solution.

✅ **5.5. High Concurrency System Design**:
- **6 Components**: System Split, Caching, MQ, Sharding, Read-Write Separation, Elasticsearch.
- **Message Queue Design**: Scalability, Persistence, HA, Zero Data Loss.
- **Rate Limiting**: 4 Algorithms (Fixed Window, Sliding Window, Leaky Bucket, Token Bucket).
- **Interview Framework**: 4-step approach với example (URL Shortener).

**Tổng cộng: ~1,200+ lines** tài liệu System Design chi tiết với High Concurrency patterns, code examples và interview strategies!

---

*Kết thúc Part 5 - System Design*

