# Part 4: Frameworks & Tools (Framework và Công cụ)

## 4.1. Spring Framework

### 4.1.1. Spring Basics

#### Spring Framework là gì?

**Spring** là **open-source, lightweight Java development framework** giúp tăng productivity và maintainability.

**Core features:**
*   **IoC (Inversion of Control)**: Container quản lý object lifecycle
*   **AOP (Aspect-Oriented Programming)**: Cross-cutting concerns
*   **Transaction Management**: Declarative transactions
*   **Data Access**: JDBC, ORM (Hibernate, JPA) support
*   **MVC Framework**: Spring MVC for web applications
*   **Integration**: Email, scheduling, caching, third-party libraries

**Spring Modules:**

| Module Category | Modules | Purpose |
|----------------|---------|---------|
| **Core Container** | spring-core, spring-beans, spring-context, spring-expression | IoC/DI foundation |
| **AOP** | spring-aop, spring-aspects | Aspect-oriented programming |
| **Data Access** | spring-jdbc, spring-tx, spring-orm | Database access, transactions |
| **Web** | spring-web, spring-webmvc, spring-webflux | Web applications |
| **Test** | spring-test | Unit & integration testing |

#### ⭐ Spring vs Spring MVC vs Spring Boot

| | Spring Framework | Spring MVC | Spring Boot |
|---|-----------------|------------|-------------|
| **Định nghĩa** | Core framework | Web MVC module của Spring | Convention-over-configuration wrapper |
| **Mục đích** | IoC, DI, AOP foundation | Build MVC web apps | Simplify Spring development |
| **Configuration** | Nhiều XML/Java config | Cần config DispatcherServlet | Auto-configuration, minimal config |
| **Dependency** | Core only | Depends on Spring Core | Includes Spring + Spring MVC + starters |
| **Use case** | Foundation for all | Web layer (Controller, View) | Rapid development, microservices |

**Mối quan hệ:**
```
Spring Boot
    └── Spring MVC (Web layer)
        └── Spring Framework (Core: IoC, AOP, etc.)
```

---

### 4.1.2. ⭐ IoC (Inversion of Control)

#### IoC là gì?

**IoC = Inversion of Control** - **Đảo ngược quyền kiểm soát**

**Traditional approach:**
```java
// Class A tự tạo dependency
public class UserService {
    private UserDao userDao = new UserDaoImpl();  // Tight coupling!
}
```

**IoC approach:**
```java
// Spring container inject dependency
@Service
public class UserService {
    @Autowired
    private UserDao userDao;  // Injected by Spring!
}
```

**Lợi ích:**
1.  **Loose coupling**: Class không phụ thuộc vào concrete implementation
2.  **Easy to manage**: Spring container quản lý object lifecycle
3.  **Testability**: Dễ dàng mock dependencies trong unit tests

#### ⭐ DI (Dependency Injection)

**DI = Dependency Injection** - Cách implement IoC, Spring inject dependencies vào object.

**3 cách Dependency Injection:**

**1. Constructor Injection (Recommended ✅)**
```java
@Service
public class UserService {
    private final UserRepository userRepository;

    // Spring tự động inject qua constructor
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

**Ưu điểm:**
*   **Immutability**: `final` fields → thread-safe
*   **Mandatory dependencies**: Compile-time guarantee
*   **Testability**: Dễ dàng test với mock objects

**2. Setter Injection**
```java
@Service
public class UserService {
    private UserRepository userRepository;

    @Autowired
    public void setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

**Dùng cho:** Optional dependencies

**3. Field Injection (Not Recommended ❌)**
```java
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;  // Direct field injection
}
```

**Nhược điểm:**
*   Khó test (phải dùng reflection)
*   Không thể dùng `final`
*   Hidden dependencies

→ **Best practice**: Dùng **Constructor Injection**

---

### 4.1.3. Spring Bean

#### Bean là gì?

**Bean**: Object được **Spring IoC container** quản lý.

**Cách khai báo Bean:**

**1. Component Scanning + Annotations**
```java
@Component      // Generic component
@Service        // Service layer
@Repository     // DAO layer
@Controller     // MVC controller
public class MyBean { }
```

**2. @Configuration + @Bean**
```java
@Configuration
public class AppConfig {
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource();  // Third-party library
    }
}
```

#### ⭐ @Component vs @Bean

| | @Component | @Bean |
|---|-----------|-------|
| **Target** | Class | Method |
| **Auto-detection** | Component scanning | Manual declaration |
| **Customization** | Limited | Full control |
| **Use case** | Your own classes | Third-party classes, conditional creation |

#### ⭐ @Autowired vs @Resource

| | @Autowired | @Resource |
|---|-----------|-----------|
| **Source** | Spring | Java JSR-250 |
| **Matching** | **byType** first, then byName | **byName** first, then byType |
| **Qualifier** | `@Qualifier("beanName")` | `@Resource(name="beanName")` |
| **Recommendation** | Constructor injection | Name-based injection |

**Example:**
```java
// Multiple implementations of SmsService: SmsServiceImpl1, SmsServiceImpl2

@Autowired
private SmsService smsServiceImpl1;  // Match by name → OK

@Autowired
@Qualifier("smsServiceImpl1")  // Explicit name
private SmsService smsService;  // OK

@Resource(name = "smsServiceImpl1")  // Name-based (recommended)
private SmsService smsService;  // OK
```

---

### 4.1.4. ⭐ Bean Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| **singleton** | 1 instance per Spring container (default) | Stateless beans (Service, DAO) |
| **prototype** | New instance every time | Stateful beans |
| **request** | 1 instance per HTTP request | Web apps |
| **session** | 1 instance per HTTP session | User session data |
| **application** | 1 instance per ServletContext | Web app-wide data |

**Configuration:**
```java
@Bean
@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
public MyBean myBean() {
    return new MyBean();
}
```

#### ⭐ Bean Thread Safety

**Singleton beans** (default) có thread-safe không?

→ **Tùy thuộc vào state!**

**Stateless beans** (không có mutable fields) → **Thread-safe** ✅
```java
@Service
public class UserService {
    public User findById(Long id) { /* stateless */ }
}
```

**Stateful beans** (có mutable fields) → **NOT thread-safe** ❌
```java
@Component
public class ShoppingCart {
    private List<String> items = new ArrayList<>();  // Mutable state → NOT thread-safe!
}
```

**Solutions:**
1.  **Avoid mutable state** (preferred)
2.  **Use `ThreadLocal`**
3.  **Use synchronization** (`synchronized`, `ReentrantLock`)
4.  **Change to prototype scope**

---

### 4.1.5. ⭐ Bean Lifecycle

**4 giai đoạn chính:**

1.  **Instantiation** (Khởi tạo): Spring tạo Bean instance
2.  **Populate Properties** (Đổ dữ liệu): Inject dependencies (`@Autowired`, `@Value`)
3.  **Initialization** (Khởi tạo logic):
    *   `@PostConstruct` / `InitializingBean.afterPropertiesSet()`
    *   `BeanPostProcessor.postProcessBeforeInitialization()`
    *   Custom `init-method`
    *   `BeanPostProcessor.postProcessAfterInitialization()`
4.  **Destruction** (Hủy):
    *   `@PreDestroy` / `DisposableBean.destroy()`
    *   Custom `destroy-method`

**Simplified flow:**
```
1. Constructor
2. @Autowired / Setter injection
3. @PostConstruct
4. Bean ready to use
5. @PreDestroy (on shutdown)
```

**Example:**
```java
@Component
public class MyBean {
    
    @Autowired
    private SomeService service;
    
    @PostConstruct
    public void init() {
        System.out.println("Bean initialized!");
    }
    
    @PreDestroy
    public void cleanup() {
        System.out.println("Bean destroyed!");
    }
}
```

---

*Kết thúc phần Spring Core basics. Tiếp tục với Spring AOP...*

### 4.1.6. ⭐ Spring AOP (Aspect-Oriented Programming)

#### AOP là gì?

**AOP** (Lập trình hướng khía cạnh) giúp tách biệt **cross-cutting concerns** (các mối quan tâm cắt ngang) khỏi business logic chính.

**Ví dụ:** Logging, Transaction management, Security, Caching. Thay vì viết code lặp lại trong mỗi phương thức Service, ta tách chúng ra thành các **Aspects**.

**Các thuật ngữ chính:**

| Thuật ngữ | Ý nghĩa | Ví dụ |
|-----------|---------|-------|
| **Aspect** | Module chứa logic cắt ngang | `LoggingAspect` class |
| **Join Point** | Điểm có thể chèn logic AOP | Method execution |
| **Pointcut** | Expression xác định Join Point nào sẽ được apply | `execution(* com.example.service..*(..))` |
| **Advice** | Logic thực thi tại Pointcut | Code ghi log |
| **Weaving** | Quá trình áp dụng Aspect vào Target object | Runtime weaving (Spring AOP) |
| **Target** | Class được áp dụng AOP | `UserServiceImpl` |

#### ⭐ AOP Proxy: JDK Dynamic Proxy vs CGLIB

Spring AOP sử dụng **Dynamic Proxy** để implement.

| Feature | JDK Dynamic Proxy | CGLIB |
|---------|-------------------|-------|
| **Đối tượng** | Chỉ proxy được **Interface** | Proxy được **Class** (bằng cách tạo subclass) |
| **Mechanism** | `java.lang.reflect.Proxy` | Bytecode generation (ASM) |
| **Performance** | Tốt hơn từ Java 8+ | Tốt, nhưng startup chậm hơn chút |
| **Requirement** | Target object phải implement Interface | Target class không được `final` |
| **Spring Default** | Dùng nếu bean implement interface | Dùng nếu bean không implement interface (hoặc force CGLIB) |

**Spring Boot 2.0+ default**: Sử dụng **CGLIB** mặc định cho tất cả (setting `spring.aop.proxy-target-class=true`).

#### AOP Annotations

*   `@Aspect`: Đánh dấu class là Aspect
*   `@Pointcut`: Định nghĩa expression
*   `@Before`: Chạy trước method
*   `@After`: Chạy sau method (dù thành công hay fail - giống finally)
*   `@AfterReturning`: Chạy sau khi method return thành công
*   `@AfterThrowing`: Chạy khi method ném exception
*   `@Around`: Hùng mạnh nhất! Bao quanh method execution (có thể chặn, sửa input/output)

**Example:**
```java
@Aspect
@Component
public class LoggingAspect {

    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint joinPoint) {
        System.out.println("Executing: " + joinPoint.getSignature().getName());
    }

    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = joinPoint.proceed(); // Execute target method
        long executionTime = System.currentTimeMillis() - start;
        System.out.println("Time: " + executionTime + "ms");
        return result;
    }
}
```

---

## 4.2. Spring Boot

### 4.2.1. Spring Boot Basics

#### Spring Boot là gì?

**Spring Boot** là framework được xây dựng trên Spring Framework, giúp **đơn giản hóa** quá trình khởi tạo và phát triển ứng dụng Spring.

**Triết lý**: **Convention over Configuration** (Quy ước hơn cấu hình).

**Core Features:**
1.  **Auto-configuration**: Tự động cấu hình Spring dựa trên dependencies có trong classpath.
2.  **Starter Dependencies**: Các gói dependency được gom nhóm sẵn (vd: `spring-boot-starter-web`).
3.  **Embedded Server**: Tích hợp sẵn Tomcat, Jetty, Undertow (không cần deploy WAR ra ngoài).
4.  **Production-ready features**: Actuator (metrics, health checks).

#### ⭐ Spring Boot vs Spring Framework

*   **Spring Framework**: Cần config thủ công nhiều (XML hoặc Java Config), setup DispatcherServlet, ViewResolver, TransactionManager...
*   **Spring Boot**: Config sẵn mọi thứ mặc định. Chỉ cần `@SpringBootApplication` và file `application.properties`.

### 4.2.2. ⭐ Auto-configuration Magic

Làm sao Spring Boot biết tự động cấu hình?

**Cơ chế:**
1.  Annotation **`@SpringBootApplication`** thực chất là tổ hợp của 3 annotations:
    *   `@Configuration`: Class cấu hình.
    *   `@ComponentScan`: Scan beans trong package hiện tại và sub-packages.
    *   **`@EnableAutoConfiguration`**: Key magic!

2.  **`@EnableAutoConfiguration`**:
    *   Tìm file `META-INF/spring.factories` (hoặc `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` trong Boot 2.7/3.0+) trong các file jar dependencies.
    *   Load các class AutoConfiguration (vd: `WebMvcAutoConfiguration`, `DataSourceAutoConfiguration`).

3.  **Conditional Annotations** (`@Conditional`):
    *   Các AutoConfig class chỉ chạy khi thỏa mãn điều kiện.
    *   `@ConditionalOnClass`: Có class X trong classpath không?
    *   `@ConditionalOnMissingBean`: Chưa có bean nào loại này do user định nghĩa?
    *   `@ConditionalOnProperty`: Property trong config có bật không?

**Ví dụ**: `DataSourceAutoConfiguration`
*   Check `@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })`: Có thư viện DB không?
*   Check `@ConditionalOnMissingBean(DataSource.class)`: User có tự define DataSource chưa? Nếu chưa → Boot tự tạo DataSource mặc định (HikariCP).

### 4.2.3. Spring Boot Starters

Starters là set các dependencies tiện lợi.

| Starter | Dependencies included |
|---------|-----------------------|
| `spring-boot-starter-web` | Spring MVC, REST, Tomcat, Jackson |
| `spring-boot-starter-data-jpa` | Spring Data JPA, Hibernate, JDBC |
| `spring-boot-starter-test` | JUnit, Mockito, Spring Test, AssertJ |
| `spring-boot-starter-actuator` | Monitoring endpoints (/actuator/health, /metrics) |
| `spring-boot-starter-security` | Spring Security |

---

## 4.3. Spring MVC

### 4.3.1. MVC Architecture Flow

**Luồng xử lý Request trong Spring MVC:**

1.  **Client** gửi request (HTTP GET/POST) → đến **DispatcherServlet** (Front Controller).
2.  **DispatcherServlet** hỏi **HandlerMapping**: "Ai xử lý URL này?" → trả về **Handler** (Controller method) + **Interceptors**.
3.  **DispatcherServlet** gọi **HandlerAdapter** để thực thi Handler.
4.  **Handler** (Controller) xử lý business logic (gọi Service), trả về **ModelAndView** (Data + Logical View Name).
    *   *Note: Với `@RestController`, nó trả về Data trực tiếp (JSON/XML) và bỏ qua bước ViewResolver.*
5.  **DispatcherServlet** hỏi **ViewResolver** (nếu trả về view name): "View name này map với file nào?" (vd: `home` → `home.html`).
6.  **View Engine** (Thymeleaf/JSP) render HTML.
7.  **DispatcherServlet** trả Response về cho Client.

#### Diagram (Simplification)
`Request` → `DispatcherServlet` → `HandlerMapping` → `Controller` → `Service` → `Controller` → `DispatcherServlet` → `Client` (JSON response)

### 4.3.2. Common Annotations

**Controller:**
*   `@Controller`: Trả về view name (dùng cho Server-side rendering).
*   `@RestController`: `@Controller` + `@ResponseBody`. Trả về JSON/XML (dùng cho REST API).

**Request Mapping:**
*   `@RequestMapping`: Base annotation.
*   `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`: Specific HTTP methods.

**Parameter Handling:**
*   `@RequestParam`: Query param (`/users?id=1` → `@RequestParam Long id`)
*   `@PathVariable`: Path variable (`/users/1` → `@GetMapping("/users/{id}")`)
*   `@RequestBody`: JSON body → Java Object.
*   `@ResponseBody`: Java Object → JSON body.

### 4.3.3. Exception Handling

Cách xử lý lỗi tập trung (Global Exception Handling):

```java
@RestControllerAdvice  // @ControllerAdvice + @ResponseBody
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
        return new ErrorResponse(404, ex.getMessage());
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleAll(Exception ex) {
        return new ErrorResponse(500, "Internal Server Error");
    }
}
```

---

*Kết thúc phần Spring MVC. Tiếp tục với Spring Data JPA, MyBatis và Transaction...*


## 4.4. Spring Data JPA & MyBatis

### 4.4.1. Spring Data JPA

**Spring Data JPA** là abstraction layer trên **JPA (Java Persistence API)** và **Hibernate**, giúp đơn giản hóa việc truy cập database.

**Core interfaces:**
*   `Repository`
*   `CrudRepository` (CRUD basic)
*   `PagingAndSortingRepository` (Pagination)
*   `JpaRepository` (JPA specific features)

**Magic methods (Derived Query Methods):**
Tự động sinh SQL dựa trên tên method:
```java
public interface UserRepository extends JpaRepository<User, Long> {
    
    // SELECT * FROM user WHERE email = ?
    User findByEmail(String email);
    
    // SELECT * FROM user WHERE age > ? AND active = true
    List<User> findByAgeGreaterThanAndActiveTrue(int age);
    
    // Custom JPQL
    @Query("SELECT u FROM User u WHERE u.email LIKE %?1%")
    List<User> searchByEmail(String emailChunk);
}
```

**N+1 Problem in JPA:**
*   **Vấn đề**: Query 1 list Cha (1 query), sau đó loop qua để lấy list Con (N queries).
*   **Ví dụ**: Lấy 10 Users. Loop qua mỗi User lấy Address → 1 + 10 = 11 queries.
*   **Giải pháp**:
    *   Sử dụng `@EntityGraph`.
    *   Sử dụng `JOIN FETCH` trong JPQL query.
    *   Sử dụng `@BatchSize`.

### 4.4.2. MyBatis

**MyBatis** là **SQL Mapper Framework** (bán tự động), cho phép kiểm soát hoàn toàn SQL.

**Đặc điểm:**
*   SQL viết trong XML file hoặc Annotation.
*   Mapping kết quả vào POJO (ResultMap).
*   Hỗ trợ **Dynamic SQL** mạnh mẽ.

**Cấu trúc:**
1.  **Mapper Interface** (`UserMapper.java`)
2.  **Mapper XML** (`UserMapper.xml`)

**Dynamic SQL Example:**
```xml
<select id="findActiveUsers" resultType="User">
  SELECT * FROM users
  <where>
    <if test="name != null">
      AND name like #{name}
    </if>
    <if test="age != null">
      AND age = #{age}
    </if>
    AND status = 'ACTIVE'
  </where>
</select>
```

**#{} vs ${} (Interview Question):**
*   **`#{}`**: **Prepared Statement** (Placeholder `?`). An toàn, chống SQL Injection.  
    `WHERE name = #{name}` → `WHERE name = ?`
*   **`${}`**: **String Interpolation** (Direct replacement). Không an toàn, nguy cơ SQL Injection.  
    `WHERE name = '${name}'` → `WHERE name = 'John'`
    Dùng cho dynamic table name hoặc sort column: `ORDER BY ${columnName}`.

### 4.4.3. ⭐ JPA vs MyBatis

| Feature | Spring Data JPA (Hibernate) | MyBatis |
|---------|-----------------------------|---------|
| **Loại** | ORM (Object Relational Mapping) | SQL Mapper |
| **SQL Control** | Tự động sinh SQL (ít control) | Viết SQL tay (full control) |
| **Phát triển** | Nhanh với CRUD cơ bản | Chậm hơn, phải viết SQL |
| **Performance** | Tốt, nhưng cần tối ưu (N+1, caching) | Tốt, dễ tối ưu SQL phức tạp |
| **Độ khó** | Dễ bắt đầu, khó master (Hibernate complexities) | Dễ hiểu SQL, chỉ cần map result |
| **Thích hợp** | Domain logic phức tạp, CRUD chuẩn | Reports, Complex Queries, Legacy DBs |

**Kết luận**:
*   JPA tốt cho hệ thống chuẩn, domain model rõ ràng (Microservices, CRUD).
*   MyBatis tốt cho hệ thống cần SQL tối ưu, reporting, hoặc DB schema lộn xộn (Internet companies ở TQ/VN dùng nhiều).

---

## 4.5. Spring Transaction Management

### 4.5.1. Transaction Basics

**Transaction**: Chuỗi các hành động DB thành công cùng nhau hoặc thất bại cùng nhau (ACID).

**Spring hỗ trợ:**
1.  **Programmatic**: Code thủ công (`TransactionTemplate`). Ít dùng.
2.  **Declarative**: Annotation **`@Transactional`**. Phổ biến nhất.

```java
@Service
public class OrderService {

    @Transactional
    public void placeOrder(Order order) {
        inventoryService.reduceStock(order);
        paymentService.charge(order);
        orderRepository.save(order);
        // Nếu bất kỳ dòng nào ném RuntimeException → Rollback toàn bộ!
    }
}
```

### 4.5.2. ⭐ Transaction Propagation

**Propagation** (Sự lan truyền): Định nghĩa hành vi transaction khi method A gọi method B.

**Các loại chính:**

| Propagation | Ý nghĩa | Hành vi |
|-------------|---------|---------|
| **REQUIRED** (Default) | Cần có transaction | Nếu đang có Tx → dùng tiếp. Nếu chưa có → tạo mới. |
| **REQUIRES_NEW** | Luôn tạo transaction mới | Suspend Tx hiện tại (nếu có) -> tạo Tx mới hoàn toàn độc lập. |
| **SUPPORTS** | Hỗ trợ transaction | Nếu có Tx → dùng. Nếu không → chạy không Tx. |
| **MANDATORY** | Bắt buộc có transaction | Nếu không có Tx → ném Exception. |
| **NESTED** | Transaction lồng nhau | Savepoint trong Tx cha. Cha rollback → Con rollback. Con rollback → Cha không ảnh hưởng (nếu try-catch). |
| **NOT_SUPPORTED** | Không hỗ trợ Tx | Suspend Tx hiện tại → chạy non-transactional. |
| **NEVER** | Cấm dùng Tx | Nếu đang có Tx → ném Exception. |

**Ví dụ `REQUIRES_NEW` (Logging scenario):**
*   `UserService.createUser()` (Tx1) gọi `LogService.log()` (Tx2 - REQUIRES_NEW).
*   Nếu `createUser` fail (rollback Tx1) → `log` (Tx2) vẫn commit thành công (vì độc lập).

### 4.5.3. ⭐ Transaction Isolation Levels

Giống DB Isolation:
*   `DEFAULT`: Theo DB setting.
*   `READ_UNCOMMITTED`
*   `READ_COMMITTED`
*   `REPEATABLE_READ`
*   `SERIALIZABLE`

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
```

### 4.5.4. ⭐ @Transactional Common Pitfalls (Tại sao @Transactional không hoạt động?)

1.  **Method không `public`**: AOP proxy chỉ support public methods.
2.  **Gọi nội bộ (Attributes call)**: Method A gọi Method B trong **cùng 1 class**.
    *   Vấn đề: Gọi qua `this.methodB()` không đi qua Spring Proxy → Tx của B bị ignore.
    *   Fix: Inject chính nó (`@Autowired SelfService`) hoặc tách class.
3.  **Exception bị nuốt (Try-catch)**:
    ```java
    @Transactional
    public void method() {
        try {
            // ... error
        } catch (Exception e) {
            // swallowed exception -> NO ROLLBACK!
        }
    }
    ```
    *   Fix: Throw exception hoặc `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();`
4.  **Checked Exception**: Mặc định `@Transactional` chỉ rollback **RuntimeException** và **Error**.
    *   Fix: `@Transactional(rollbackFor = Exception.class)` cho Checked Exceptions (IOException, SQLException).
5.  **Database Engine không hỗ trợ**: Ví dụ MySQL dùng MyISAM (không support transaction).

---

## 4.6. ⭐ Spring Security (Chi tiết)

### 4.6.1. Spring Security Basics

**Spring Security** là framework bảo mật cho Java applications, cung cấp **authentication** (xác thực) và **authorization** (phân quyền).

**Core Concepts:**

**1. Authentication (Xác thực)**: "Bạn là ai?" - Verify user identity
- Username/Password
- JWT Token
- OAuth 2.0

**2. Authorization (Phân quyền)**: "Bạn được phép làm gì?" - Check permissions
- Role-based (ROLE_ADMIN, ROLE_USER)
- Permission-based (READ_USER, WRITE_USER)

### 4.6.2. ⭐ Spring Security Architecture

**Filter Chain:**

Spring Security sử dụng **Servlet Filter Chain** để intercept requests.

```
Request → Filter 1 → Filter 2 → ... → Filter N → DispatcherServlet → Controller
```

**Key Filters:**
1. **SecurityContextPersistenceFilter**: Restore SecurityContext từ Session
2. **UsernamePasswordAuthenticationFilter**: Xử lý form login
3. **BasicAuthenticationFilter**: Xử lý HTTP Basic Auth
4. **FilterSecurityInterceptor**: Kiểm tra authorization (cuối cùng)

**SecurityContext:**
- Lưu thông tin **Authentication** của user hiện tại
- Thread-local storage (mỗi thread có SecurityContext riêng)

### 4.6.3. ⭐ Configuration (Web Security Config)

**Basic Configuration:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()  // Public access
                .requestMatchers("/admin/**").hasRole("ADMIN")  // Admin only
                .requestMatchers("/user/**").hasAnyRole("USER", "ADMIN")  // User or Admin
                .anyRequest().authenticated()  // Other requests need authentication
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/home")
                .failureUrl("/login?error=true")
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout=true")
            )
            .csrf(csrf -> csrf.disable());  // Disable CSRF for API
        
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();  // Password hashing
    }
}
```

### 4.6.4. ⭐ Authentication Methods

**1. Form-based Authentication (Traditional)**
```java
.formLogin(form -> form
    .loginPage("/login")
    .usernameParameter("username")
    .passwordParameter("password")
    .successHandler((request, response, authentication) -> {
        // Custom success logic
    })
)
```

**2. JWT Authentication (Stateless - Khuyến nghị cho API)**

**JWT Filter:**
```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtTokenProvider tokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String token = extractToken(request);
        
        if (token != null && tokenProvider.validateToken(token)) {
            Authentication auth = tokenProvider.getAuthentication(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        
        filterChain.doFilter(request, response);
    }

    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

**Security Config với JWT:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private JwtAuthenticationFilter jwtFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)  // No session
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

**3. OAuth 2.0 / OIDC**
```java
.oauth2Login(oauth2 -> oauth2
    .loginPage("/login")
    .defaultSuccessUrl("/home")
)
```

### 4.6.5. ⭐ Authorization (Phân quyền)

**Method-level Security:**
```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) {
    // Only ADMIN can call this
}

@PreAuthorize("hasAuthority('USER_READ') or hasRole('ADMIN')")
public User getUser(Long id) {
    // USER_READ permission OR ADMIN role
}

@PostAuthorize("returnObject.owner == authentication.name")
public User getUser(Long id) {
    // Check after method execution
}
```

**Enable Method Security:**
```java
@Configuration
@EnableMethodSecurity(prePostEnabled = true)
public class MethodSecurityConfig {
}
```

**Common Authorization Methods:**

| Method | Description | Example |
|--------|-------------|---------|
| `permitAll()` | Cho phép tất cả (không cần auth) | `/public/**` |
| `authenticated()` | Cần đăng nhập | `/user/**` |
| `hasRole("ADMIN")` | Cần role ADMIN | `/admin/**` |
| `hasAnyRole("USER", "ADMIN")` | Cần 1 trong các roles | `/dashboard/**` |
| `hasAuthority("READ_USER")` | Cần permission cụ thể | `/api/users/**` |
| `hasIpAddress("192.168.1.0/24")` | Chỉ cho phép IP range | Internal APIs |

### 4.6.6. ⭐ Password Encoding

**BCrypt (Khuyến nghị):**
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);  // Strength = 12 (2^12 rounds)
}

// Usage
String rawPassword = "password123";
String encoded = passwordEncoder.encode(rawPassword);  // Hash
boolean matches = passwordEncoder.matches(rawPassword, encoded);  // Verify
```

**Other Encoders:**
- **Argon2**: Modern, secure (JDK 8+)
- **PBKDF2**: Standard, slower
- **SCrypt**: Memory-hard

**⚠️ NEVER use:**
- MD5, SHA-1, SHA-256 (too fast, vulnerable to brute force)
- Plain text (obviously!)

### 4.6.7. ⭐ Custom UserDetailsService

**Load user từ database:**
```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getUsername())
            .password(user.getPassword())
            .roles(user.getRoles().toArray(new String[0]))
            .authorities(user.getPermissions())
            .accountExpired(!user.isActive())
            .build();
    }
}
```

### 4.6.8. ⭐ CSRF Protection

**CSRF (Cross-Site Request Forgery)**: Attacker lừa user thực hiện action không mong muốn.

**Spring Security CSRF:**
- **Default**: Enabled (bảo vệ form submissions)
- **API**: Nên disable (stateless, dùng JWT)

```java
// Disable CSRF for API
.csrf(csrf -> csrf
    .ignoringRequestMatchers("/api/**")  // Ignore API endpoints
)

// Hoặc disable hoàn toàn
.csrf(csrf -> csrf.disable())
```

### 4.6.9. ⭐ CORS Configuration

**CORS (Cross-Origin Resource Sharing)**: Cho phép browser gọi API từ domain khác.

```java
@Configuration
public class CorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(Arrays.asList("http://localhost:3000"));  // Frontend URL
        config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(Arrays.asList("*"));
        config.setAllowCredentials(true);  // Allow cookies
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}

// In SecurityConfig
.cors(cors -> cors.configurationSource(corsConfigurationSource()))
```

---

## 4.7. Development Tools

### 4.6.1. Maven (Build Tool)

**Maven** là công cụ quản lý dự án và build tự động.

**Cơ chế:**
*   Project Object Model (**POM**): `pom.xml` định nghĩa cấu trúc dự án.
*   **Dependency Management**: Tự động tải jar từ Maven Central Repository.
*   **Life Cycle**:
    1.  `clean`: Dọn dẹp build cũ.
    2.  `validate`: Kiểm tra project đúng đắn.
    3.  `compile`: Biên dịch source code.
    4.  `test`: Chạy unit tests.
    5.  `package`: Đóng gói (JAR/WAR).
    6.  `verify`: Kiểm tra quality packages.
    7.  `install`: Cài package vào local repository (`~/.m2`).
    8.  `deploy`: Upload package lên remote repository.

**Dependency Scope:**
*   `compile` (Default): Có mặt mọi lúc.
*   `test`: Chỉ dùng khi test (JUnit).
*   `provided`: Có khi compile, nhưng runtime do container cung cấp (Servlet API).
*   `runtime`: Không cần khi compile, cần khi run (JDBC Driver).

**Maven vs Gradle:**
*   **Maven**: XML, cứng nhắc, quy ước chặt chẽ, stable.
*   **Gradle**: Groovy/Kotlin DSL, linh hoạt, build nhanh hơn (incremental build), phức tạp hơn.

---

### 4.6.2. Git (Version Control)

**Git** là hệ thống quản lý phiên bản phân tán (Distributed VCS).

**Basic Workflow:**
1.  **Workspace**: Code trên máy.
2.  **Index/Staging Area**: `git add` đưa file vào đây.
3.  **Local Repository**: `git commit` lưu snapshot vào lịch sử local.
4.  **Remote Repository**: `git push` đẩy lên server (GitHub/GitLab).

**Common Commands:**
*   `git init`: Khởi tạo repo.
*   `git clone <url>`: Copy repo về máy.
*   `git status`: Xem trạng thái file.
*   `git add .`: Stage changes.
*   `git commit -m "msg"`: Commit changes.
*   `git pull`: Fetch + Merge từ remote.
*   `git push`: Đẩy commit lên remote.
*   `git branch`: Liệt kê nhánh.
*   `git checkout -b <branch>`: Tạo và chuyển nhánh.
*   `git merge <branch>`: Gộp nhánh.

**⭐ Merge vs Rebase:**

| | Merge | Rebase |
|---|---|---|
| **Cơ chế** | Tạo commit mới (merge commit) nối 2 nhánh | Viết lại lịch sử, dời commit của nhánh này lên đầu nhánh kia |
| **Lịch sử** | Non-linear, giữ nguyên lịch sử thực tế | Linear (tuyến tính), lịch sử sạch đẹp |
| **An toàn** | An toàn, không thay đổi commit ID cũ | **Nguy hiểm** nếu branch đã public (thay đổi history) |
| **Use case** | Integrate feature branch vào main | Update feature branch với main mới nhất (trước khi merge) |

### 4.6.3. Docker (Containerization)

**Docker** giúp đóng gói ứng dụng và environment vào **Container** để chạy nhất quán mọi nơi.

**Concepts:**
*   **Image**: Template (bản thiết kế) read-only. (Ví dụ: Class)
*   **Container**: Instance chạy từ Image. (Ví dụ: Object)
*   **Dockerfile**: File script để build Image.
*   **Volume**: Persist data ra ngoài container.

**Dockerfile Example (Spring Boot):**
```dockerfile
# Base image
FROM openjdk:17-jdk-alpine

# Working directory
WORKDIR /app

# Copy JAR file
COPY target/myapp.jar app.jar

# Expose port
EXPOSE 8080

# Command to run
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Common Commands:**
*   `docker build -t myapp .`: Build image từ Dockerfile.
*   `docker run -p 8080:8080 myapp`: Tạo và chạy container.
*   `docker ps`: Liệt kê container đang chạy.
*   `docker stop <id>`: Dừng container.
*   `docker logs <id>`: Xem log.
*   `docker exec -it <id> sh`: Chui vào shell của container.

**Docker Compose:**
Chạy multi-container application (VD: App + MySQL + Redis) định nghĩa trong `docker-compose.yml`.

```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "8080:8080"
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
```

**Docker Best Practices:**
- **Multi-stage builds**: Giảm image size
- **.dockerignore**: Exclude files không cần thiết
- **Layer caching**: Sắp xếp commands để tận dụng cache
- **Non-root user**: Security best practice

---

### 4.6.4. ⭐ Kubernetes (Container Orchestration)

#### Kubernetes là gì?

**Kubernetes (K8s)** là container orchestration platform để quản lý, deploy và scale containerized applications.

**Core Concepts:**

**1. Pod**
- **Smallest deployable unit** trong K8s
- Chứa 1 hoặc nhiều containers (thường 1)
- Share network và storage

**2. Deployment**
- Quản lý Pods (replicas, rolling updates)
- Đảm bảo số lượng pods mong muốn

**3. Service**
- Expose Pods ra network
- Load balancing giữa Pods
- Stable IP và DNS name

**4. Namespace**
- Logical separation (dev, test, prod)
- Resource isolation

#### ⭐ Kubernetes Architecture

**Master Node (Control Plane):**
- **API Server**: Entry point cho tất cả requests
- **etcd**: Distributed key-value store (cluster state)
- **Scheduler**: Assign Pods to nodes
- **Controller Manager**: Maintain desired state

**Worker Nodes:**
- **kubelet**: Agent chạy trên mỗi node
- **kube-proxy**: Network proxy cho Services
- **Container Runtime**: Docker, containerd, CRI-O

#### ⭐ Basic Kubernetes Resources

**1. Deployment (Quản lý Pods)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3  # 3 Pods
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**2. Service (Expose Pods)**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP  # Internal service
  # type: LoadBalancer  # External service
```

**3. ConfigMap (Configuration)**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.url: "jdbc:mysql://db:3306/mydb"
  cache.host: "redis:6379"
```

**4. Secret (Sensitive Data)**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQ=
```

#### ⭐ Kubernetes Scaling

**1. Manual Scaling**
```bash
kubectl scale deployment user-service --replicas=5
```

**2. Horizontal Pod Autoscaler (HPA)**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**3. Vertical Pod Autoscaler (VPA)**
- Tự động điều chỉnh CPU/Memory requests/limits
- Dựa trên historical usage

#### ⭐ Kubernetes Networking

**Service Types:**
- **ClusterIP**: Internal service (default)
- **NodePort**: Expose trên node IP + port
- **LoadBalancer**: External load balancer (cloud)
- **ExternalName**: External service alias

**Ingress:**
- HTTP/HTTPS routing
- SSL termination
- Path-based routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
```

---

### 4.6.5. ⭐ CI/CD (Continuous Integration / Continuous Deployment)

#### CI/CD là gì?

**CI (Continuous Integration):**
- Developers commit code → **Automated build & test**
- Phát hiện bugs sớm
- **Tools**: Jenkins, GitLab CI, GitHub Actions, CircleCI

**CD (Continuous Deployment/Delivery):**
- **Continuous Delivery**: Code luôn sẵn sàng deploy (manual trigger)
- **Continuous Deployment**: Tự động deploy lên production

**CI/CD Pipeline Flow:**
```
Code Commit → Build → Test → Package → Deploy (Staging) → Deploy (Production)
```

#### ⭐ Jenkins

**Jenkins** là open-source automation server cho CI/CD.

**Jenkinsfile (Pipeline as Code):**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        
        stage('Docker Build') {
            steps {
                sh 'docker build -t myapp:${BUILD_NUMBER} .'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'kubectl set image deployment/myapp myapp=myapp:${BUILD_NUMBER}'
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

**Jenkins Features:**
- **Plugins**: Hàng nghìn plugins (Docker, Kubernetes, Maven, etc.)
- **Distributed builds**: Master + Agents
- **Pipeline**: Declarative/Scripted pipelines

#### ⭐ GitLab CI/CD

**GitLab CI** tích hợp sẵn trong GitLab.

**.gitlab-ci.yml:**
```yaml
stages:
  - build
  - test
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"

build:
  stage: build
  image: maven:3.8-openjdk-17
  script:
    - mvn clean package -DskipTests
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 hour

test:
  stage: test
  image: maven:3.8-openjdk-17
  script:
    - mvn test
  coverage: '/Total.*?([0-9]{1,3})%/'

deploy_staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/myapp myapp=myapp:$CI_COMMIT_SHA
  only:
    - develop

deploy_production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/myapp myapp=myapp:$CI_COMMIT_SHA
  only:
    - main
  when: manual  # Require manual trigger
```

**GitLab CI Features:**
- **Built-in**: Không cần setup server riêng
- **GitLab Runners**: Execute jobs
- **Auto DevOps**: Pre-configured pipelines

#### ⭐ GitHub Actions

**GitHub Actions** là CI/CD platform tích hợp trong GitHub.

**.github/workflows/ci.yml:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Build with Maven
      run: mvn clean package
    
    - name: Run tests
      run: mvn test
    
    - name: Build Docker image
      run: docker build -t myapp:${{ github.sha }} .
    
    - name: Push to Docker Hub
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push myapp:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
```

**GitHub Actions Features:**
- **Free for public repos**: Unlimited minutes
- **Marketplace**: Hàng nghìn actions
- **Matrix builds**: Test trên nhiều versions

#### ⭐ CI/CD Best Practices

**1. Fast Feedback**
- Fail fast: Stop pipeline nếu test fail
- Parallel jobs: Chạy tests song song
- Cache dependencies: Maven, npm, Docker layers

**2. Security**
- **Secrets management**: Không hardcode passwords
- **Scan dependencies**: Check vulnerabilities
- **Image scanning**: Scan Docker images

**3. Quality Gates**
- **Code coverage**: Minimum coverage threshold
- **Code quality**: SonarQube, Checkstyle
- **Security scan**: OWASP Dependency Check

**4. Deployment Strategies**
- **Blue-Green**: Zero downtime
- **Canary**: Gradual rollout
- **Rolling**: Update từng pod

---

### 4.6.6. ⭐ Monitoring & Observability (Chi tiết)

#### Observability là gì?

**3 Pillars of Observability:**
1. **Metrics**: Số liệu (CPU, Memory, Request rate)
2. **Logs**: Nhật ký events
3. **Traces**: Distributed tracing (request flow)

#### ⭐ Prometheus + Grafana

**Prometheus** là metrics collection và alerting system.

**Architecture:**
```
Applications → Export metrics → Prometheus (Pull) → Grafana (Visualize)
```

**Prometheus Metrics Types:**
- **Counter**: Chỉ tăng (total requests)
- **Gauge**: Tăng/giảm (current connections)
- **Histogram**: Distribution (request duration)
- **Summary**: Similar to Histogram

**Spring Boot Actuator + Prometheus:**
```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus,health,metrics
  metrics:
    export:
      prometheus:
        enabled: true
```

**Prometheus Query (PromQL):**
```promql
# Request rate per second
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status="500"}[5m]) / rate(http_requests_total[5m])

# CPU usage
100 - (avg(irate(process_cpu_seconds_total[5m])) * 100)
```

**Grafana Dashboard:**
- Visualize metrics từ Prometheus
- Create dashboards với charts
- Alerting rules

#### ⭐ ELK Stack (Elasticsearch, Logstash, Kibana)

**ELK Stack** cho log aggregation và analysis.

**Architecture:**
```
Applications → Logstash/Filebeat → Elasticsearch → Kibana (Visualize)
```

**1. Elasticsearch**
- Distributed search engine
- Store và index logs
- Full-text search

**2. Logstash**
- Collect, parse, transform logs
- Input → Filter → Output

**Logstash Config:**
```ruby
input {
  file {
    path => "/var/log/app.log"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

**3. Kibana**
- Visualize logs từ Elasticsearch
- Create dashboards
- Search và analyze logs

**Filebeat (Lightweight Alternative):**
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/app.log

output.elasticsearch:
  hosts: ["localhost:9200"]
```

#### ⭐ Distributed Tracing

**Vấn đề**: Request đi qua 5 services → Làm sao trace?

**Solution: Distributed Tracing**

**1. Spring Cloud Sleuth + Zipkin**
```yaml
spring:
  sleuth:
    sampler:
      probability: 1.0
    zipkin:
      base-url: http://zipkin-server:9411
```

**2. Jaeger**
- Open-source distributed tracing
- UI để visualize traces
- Performance tốt hơn Zipkin

**3. SkyWalking (Alibaba)**
- APM (Application Performance Monitoring)
- Distributed tracing + Metrics + Logging
- Rất phổ biến tại Trung Quốc

#### ⭐ APM (Application Performance Monitoring)

**APM Tools:**
- **New Relic**: Commercial, easy setup
- **Datadog**: Commercial, comprehensive
- **SkyWalking**: Open-source, full-featured
- **Pinpoint**: Open-source (Naver)

**APM Features:**
- **Transaction tracing**: Track request flow
- **Performance metrics**: Response time, throughput
- **Error tracking**: Exception monitoring
- **Database monitoring**: Slow queries

#### ⭐ Monitoring Best Practices

**1. Key Metrics (4 Golden Signals)**
- **Latency**: Response time (P50, P95, P99)
- **Traffic**: Requests per second
- **Errors**: Error rate
- **Saturation**: Resource utilization (CPU, Memory)

**2. Alerting Rules**
```yaml
# Prometheus Alerting Rules
groups:
- name: application_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status="500"}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "Error rate is above 5%"
  
  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    annotations:
      summary: "P95 latency is above 1s"
```

**3. Logging Best Practices**
- **Structured logging**: JSON format
- **Log levels**: ERROR, WARN, INFO, DEBUG
- **Context**: Include trace ID, user ID
- **Sensitive data**: Không log passwords, tokens

**4. Dashboard Design**
- **Overview dashboard**: High-level metrics
- **Service dashboard**: Per-service metrics
- **Business dashboard**: Business KPIs

---

## Tổng kết Part 4: Frameworks & Tools

Đã hoàn thành **Part 4: Frameworks & Tools** với nội dung toàn diện:

✅ **4.1. Spring Framework**:
- IoC, DI (Constructor vs Setter), Bean Lifecycle, Scopes.
- AOP concepts, Proxy modes, Annotations.

✅ **4.2. Spring Boot**:
- Auto-configuration magic, Starters.
- Spring Boot vs Spring Framework.

✅ **4.3. Spring MVC**:
- Request processing flow (DispatcherServlet).
- Controller annotations, Global Exception Handling.

✅ **4.4. Spring Data JPA & MyBatis**:
- JPA/Hibernate basics, Derived queries, N+1 problem.
- MyBatis mapper, dynamic SQL, #{} vs ${}.
- Comparison: JPA vs MyBatis.

✅ **4.5. Transaction Management**:
- Declarative transaction (@Transactional).
- ⭐ Propagation behaviors (REQUIRED, REQUIRES_NEW...).
- Isolation levels.
- Common pitfalls (why transaction fails).

✅ **4.6. Spring Security**:
- **Architecture**: Filter Chain, SecurityContext
- **Authentication**: Form-based, JWT, OAuth 2.0
- **Authorization**: Method-level security, Role/Permission-based
- **Password Encoding**: BCrypt, Security best practices
- **CSRF & CORS**: Protection mechanisms

✅ **4.7. Development Tools**:
- **Maven**: Lifecycle, POM, Dependency scopes, Maven vs Gradle.
- **Git**: Workflow, Merge vs Rebase, Best practices.
- **Docker**: Image vs Container, Dockerfile, Docker Compose, Best practices.

✅ **4.8. DevOps & Infrastructure**:
- **Kubernetes**: Pods, Deployments, Services, ConfigMap, Secret, HPA, Networking, Ingress
- **CI/CD**: Jenkins (Pipeline as Code), GitLab CI (.gitlab-ci.yml), GitHub Actions (Workflows)
- **Monitoring & Observability**: 
  - **Prometheus + Grafana**: Metrics collection, PromQL, Dashboards
  - **ELK Stack**: Elasticsearch, Logstash, Kibana, Filebeat
  - **Distributed Tracing**: Sleuth+Zipkin, Jaeger, SkyWalking
  - **APM**: Application Performance Monitoring tools
- **Best Practices**: CI/CD best practices, Monitoring best practices, Alerting rules

**Tổng cộng: ~2,500+ lines** tài liệu Framework & Tools toàn diện với DevOps, Kubernetes, CI/CD, Monitoring chi tiết, code examples và best practices thực tế!

---

*Kết thúc Part 4 - Frameworks & Tools*

