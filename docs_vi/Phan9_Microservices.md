# Phần 9: Microservices Architecture (Kiến trúc vi dịch vụ)

Tài liệu này bổ sung các kiến thức về thiết kế và triển khai kiến trúc microservices, bao gồm Spring Cloud ecosystem và các best practices.

---

## 9.1. Microservices Fundamentals (Cơ bản về Vi dịch vụ)

### 9.1.1. ⭐ Microservices vs Monolith

**Monolith (Đơn khối):**
- Toàn bộ ứng dụng là **1 deployable unit** (1 WAR/JAR)
- Tất cả modules chạy trong cùng process
- **Ưu điểm**: Đơn giản, dễ debug, transaction dễ
- **Nhược điểm**: Khó scale từng phần, technology lock-in, deployment rủi ro cao

**Microservices (Vi dịch vụ):**
- Ứng dụng được chia thành **nhiều services độc lập**
- Mỗi service có database riêng, deploy riêng
- **Ưu điểm**: Scale độc lập, technology diversity, fault isolation
- **Nhược điểm**: Phức tạp (network, distributed tx), overhead cao

**So sánh:**

| Tiêu chí | Monolith | Microservices |
|----------|----------|--------------|
| **Deployment** | 1 unit | Nhiều units |
| **Scaling** | Scale toàn bộ | Scale từng service |
| **Technology** | 1 stack | Polyglot (đa ngôn ngữ) |
| **Database** | Shared DB | Database per service |
| **Transaction** | ACID local | Distributed tx (phức tạp) |
| **Communication** | In-process calls | Network calls (REST/RPC) |
| **Complexity** | Thấp | Cao |

### 9.1.2. Khi nào nên dùng Microservices?

**✅ Nên dùng khi:**
- Team lớn (10+ developers)
- Services có lifecycle khác nhau (một số update thường xuyên, một số ít)
- Cần scale từng phần độc lập
- Cần technology diversity

**❌ Không nên dùng khi:**
- Team nhỏ (< 5 developers)
- Ứng dụng đơn giản, ít thay đổi
- Không có kinh nghiệm distributed systems
- Chưa có infrastructure (monitoring, CI/CD)

**Lời khuyên**: **Bắt đầu với Monolith**, sau đó refactor sang Microservices khi cần.

---

## 9.2. ⭐ Spring Cloud Ecosystem

### 9.2.1. Spring Cloud Overview

**Spring Cloud** là bộ công cụ giúp xây dựng distributed systems (microservices) dễ dàng hơn.

**Core Components:**

| Component | Chức năng | Alternative |
|-----------|-----------|-------------|
| **Eureka / Nacos** | Service Discovery & Registry | Consul, Zookeeper |
| **Ribbon / LoadBalancer** | Client-side Load Balancing | Nginx, HAProxy |
| **Feign / OpenFeign** | Declarative HTTP Client | RestTemplate, WebClient |
| **Hystrix / Sentinel** | Circuit Breaker | Resilience4j |
| **Zuul / Gateway** | API Gateway | Kong, Traefik |
| **Config Server / Nacos Config** | Centralized Configuration | Apollo, Consul |
| **Sleuth / Zipkin** | Distributed Tracing | Jaeger, SkyWalking |
| **Bus** | Event Bus (Config refresh) | Kafka, RabbitMQ |

### 9.2.2. ⭐ Service Discovery (Eureka vs Nacos)

**Vấn đề**: Làm sao service A biết địa chỉ IP:Port của service B?

**Giải pháp**: **Service Registry** - Nơi các services đăng ký và tìm kiếm nhau.

#### Eureka (Netflix)

**Architecture:**
- **Eureka Server**: Registry server
- **Eureka Client**: Services đăng ký và tìm kiếm

**Features:**
- **AP System** (Eventual Consistency)
- **Peer-to-peer replication** (Eureka servers replicate với nhau)
- **Self-preservation mode**: Bảo vệ registry khi network partition

**Flow:**
1. Service A khởi động → Đăng ký với Eureka Server (IP, Port, Health check URL)
2. Service B cần gọi A → Hỏi Eureka Server → Nhận danh sách instances của A
3. Service B cache danh sách, định kỳ refresh

**Configuration:**
```yaml
# Eureka Server
server:
  port: 8761
eureka:
  client:
    register-with-eureka: false  # Server không đăng ký chính nó
    fetch-registry: false

# Eureka Client (Service)
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    lease-renewal-interval-in-seconds: 30
    lease-expiration-duration-in-seconds: 90
```

**⚠️ Lưu ý**: Eureka 2.0 đã bị **discontinued**. Nhiều công ty chuyển sang **Nacos**.

#### Nacos (Alibaba)

**Features:**
- **Service Discovery** (giống Eureka)
- **Configuration Management** (giống Config Server)
- **Dynamic DNS** (service routing)
- **CAP Mode**: Có thể chọn **AP** (high availability) hoặc **CP** (strong consistency)

**Nacos vs Eureka:**

| Tiêu chí | Eureka | Nacos |
|----------|--------|-------|
| **CAP** | AP only | AP + CP (lựa chọn) |
| **Config Management** | ❌ Không có | ✅ Có |
| **Health Check** | Client-side heartbeat | Server-side active check |
| **Performance** | Tốt | Tốt hơn (Java, optimized) |
| **Community** | Discontinued | Active (Alibaba) |

**Nacos Configuration:**
```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
        namespace: dev  # Environment isolation
      config:
        server-addr: localhost:8848
        file-extension: yaml
```

### 9.2.3. ⭐ API Gateway (Zuul vs Spring Cloud Gateway)

**API Gateway** là điểm vào duy nhất (single entry point) cho tất cả clients.

**Chức năng:**
1. **Routing**: Route request đến đúng service
2. **Authentication & Authorization**: Xác thực user trước khi vào services
3. **Rate Limiting**: Giới hạn số requests
4. **Load Balancing**: Phân tải requests
5. **Protocol Conversion**: HTTP → gRPC
6. **Request/Response Transformation**: Modify headers, body

#### Zuul (Netflix - Legacy)

**⚠️ Status**: **Deprecated** (Netflix không maintain nữa)

**Features:**
- Filter-based architecture (Pre, Route, Post, Error filters)
- Dynamic routing
- Request/Response modification

#### ⭐ Spring Cloud Gateway (Recommended)

**Features:**
- **Reactive** (WebFlux) - Non-blocking, high performance
- **Predicate-based routing** (flexible routing rules)
- **Filter chain** (Pre, Post, Global filters)
- **Circuit Breaker integration** (Resilience4j)

**Configuration Example:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service  # Load balanced
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=2  # Remove /api/users
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
```

**Custom Filter:**
```java
@Component
public class AuthFilter implements GatewayFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        // Validate token...
        return chain.filter(exchange);
    }
}
```

### 9.2.4. ⭐ Load Balancing (Ribbon vs Spring Cloud LoadBalancer)

**Client-side Load Balancing**: Client tự quyết định gọi instance nào (thay vì dùng Load Balancer riêng).

#### Ribbon (Netflix - Deprecated)

**⚠️ Status**: **Deprecated** (Netflix không maintain)

**Features:**
- Round Robin, Weighted Round Robin, Random, Least Connections
- Zone-aware (ưu tiên instances trong cùng zone)

#### Spring Cloud LoadBalancer (Recommended)

**Features:**
- Reactive (WebFlux)
- Health-check aware
- Service instance caching

**Usage với OpenFeign:**
```java
@FeignClient(name = "user-service")
public interface UserServiceClient {
    @GetMapping("/users/{id}")
    User getUser(@PathVariable Long id);
}

// Spring tự động inject LoadBalancer
// Feign sẽ gọi: http://user-service-instance-1:8080/users/1
```

**Custom Load Balancer:**
```java
@Configuration
public class LoadBalancerConfig {
    @Bean
    public ReactorLoadBalancer<ServiceInstance> customLoadBalancer(
            Environment environment, LoadBalancerClientFactory clientFactory) {
        String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
        return new RoundRobinLoadBalancer(
            clientFactory.getLazyProvider(name, ServiceInstanceListSupplier.class),
            name
        );
    }
}
```

### 9.2.5. ⭐ Feign Client (Declarative HTTP Client)

**Feign** giúp gọi HTTP API như gọi method Java.

**Without Feign:**
```java
RestTemplate restTemplate = new RestTemplate();
String url = "http://user-service/users/1";
User user = restTemplate.getForObject(url, User.class);
```

**With Feign:**
```java
@FeignClient(name = "user-service", path = "/users")
public interface UserServiceClient {
    @GetMapping("/{id}")
    User getUser(@PathVariable Long id);
    
    @PostMapping
    User createUser(@RequestBody User user);
}

// Usage
@Autowired
private UserServiceClient userServiceClient;

User user = userServiceClient.getUser(1L);  // Clean!
```

**Feign Features:**
- **Declarative**: Chỉ cần interface, không cần implementation
- **Integration**: Tích hợp với Eureka/Nacos, LoadBalancer
- **Error Handling**: Custom error decoder
- **Request/Response Logging**: Debug dễ dàng

**Configuration:**
```yaml
feign:
  client:
    config:
      default:
        connectTimeout: 5000
        readTimeout: 10000
        loggerLevel: full  # Log requests/responses
  hystrix:
    enabled: true  # Circuit breaker (deprecated, dùng Resilience4j)
```

### 9.2.6. ⭐ Configuration Management (Config Server vs Nacos Config)

**Vấn đề**: Có 10 services, mỗi service có `application.yml`. Muốn đổi 1 config → phải sửa 10 files và restart 10 services!

**Giải pháp**: **Centralized Configuration** - Lưu config ở 1 nơi, services pull về.

#### Spring Cloud Config Server

**Architecture:**
- **Config Server**: Lưu config files (Git repository)
- **Config Client**: Services pull config từ Server

**Features:**
- Support Git, SVN, Local filesystem
- **Refresh**: `/actuator/refresh` để reload config (không cần restart)
- **Encryption**: Encrypt sensitive data (passwords)

**Config Server:**
```yaml
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/company/config-repo
          search-paths: '{application}'
```

**Config Client:**
```yaml
spring:
  application:
    name: user-service
  cloud:
    config:
      uri: http://config-server:8888
      profile: prod
```

#### Nacos Config (Recommended)

**Features:**
- Web UI để quản lý config
- **Namespace**: Environment isolation (dev, test, prod)
- **Group**: Group configs
- **Dynamic Refresh**: Tự động push config mới đến clients
- **Versioning & Rollback**

**Nacos Config Example:**
```yaml
# Nacos Console: Create config
# Data ID: user-service.yaml
# Group: DEFAULT_GROUP
# Content:
server:
  port: 8080
database:
  url: jdbc:mysql://localhost:3306/userdb

# Application
spring:
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        file-extension: yaml
        namespace: prod
        group: DEFAULT_GROUP
```

### 9.2.7. ⭐ Distributed Tracing (Sleuth + Zipkin)

**Vấn đề**: Request đi qua 5 services. Làm sao trace request đó qua tất cả services?

**Giải pháp**: **Distributed Tracing** - Gán mỗi request một **Trace ID** duy nhất, propagate qua tất cả services.

#### Spring Cloud Sleuth

**Sleuth** tự động inject **Trace ID** và **Span ID** vào logs và HTTP headers.

**Trace ID**: Unique cho toàn bộ request (giống nhau qua tất cả services)
**Span ID**: Unique cho mỗi service call

**Example Log:**
```
[user-service,abc123,def456] INFO - Processing request
[order-service,abc123,ghi789] INFO - Received request  # Same trace ID!
```

**Configuration:**
```yaml
spring:
  sleuth:
    sampler:
      probability: 1.0  # 100% sampling (production: 0.1)
    zipkin:
      base-url: http://zipkin-server:9411
```

#### Zipkin (Visualization)

**Zipkin** là tool để visualize traces.

**Features:**
- Timeline view: Xem request đi qua services nào, mất bao lâu
- Dependency graph: Xem service dependencies
- Error tracking: Tìm requests lỗi

**Architecture:**
```
Service A → Service B → Service C
    ↓          ↓          ↓
    └──────────┴──────────┘
              ↓
         Zipkin Server
```

**Alternative**: **Jaeger**, **SkyWalking** (Alibaba, có APM features)

---

## 9.3. Service Communication (Giao tiếp giữa Services)

### 9.3.1. ⭐ Synchronous vs Asynchronous

**Synchronous (Đồng bộ):**
- Service A gọi Service B → **Đợi** B trả về kết quả
- **Protocol**: REST, gRPC, RPC
- **Ưu điểm**: Đơn giản, dễ debug
- **Nhược điểm**: Tight coupling, latency cao

**Asynchronous (Bất đồng bộ):**
- Service A gửi message → **Không đợi** → Tiếp tục xử lý
- Service B nhận message → Xử lý → Gửi response (nếu cần)
- **Protocol**: Message Queue (Kafka, RabbitMQ, RocketMQ)
- **Ưu điểm**: Loose coupling, high throughput
- **Nhược điểm**: Phức tạp, eventual consistency

### 9.3.2. REST vs RPC vs Message Queue

| Tiêu chí | REST | RPC (Dubbo/gRPC) | Message Queue |
|----------|------|-----------------|---------------|
| **Communication** | Request-Response | Request-Response | Publish-Subscribe |
| **Coupling** | Loose | Tight | Very Loose |
| **Performance** | Thấp (HTTP overhead) | Cao (Binary) | Trung bình |
| **Language** | Language-agnostic | Language-specific | Language-agnostic |
| **Use Case** | Public API, Web | Internal services | Event-driven, Async |

**Khi nào dùng gì:**
- **REST**: Public API, Web frontend, Mobile apps
- **RPC**: Internal services (high performance), Same language stack
- **MQ**: Event-driven architecture, Async processing, Decoupling

---

## 9.4. Service Governance (Quản trị Services)

### 9.4.1. Service Mesh (Istio, Linkerd)

**Service Mesh** là infrastructure layer quản lý communication giữa services.

**Features:**
- **Traffic Management**: Load balancing, routing, circuit breaking
- **Security**: mTLS (mutual TLS), authentication
- **Observability**: Metrics, logs, traces
- **Policy Enforcement**: Rate limiting, access control

**Architecture:**
- **Data Plane**: Sidecar proxy (Envoy) chạy cùng mỗi service
- **Control Plane**: Quản lý configuration, policies

**Service Mesh vs API Gateway:**
- **API Gateway**: Edge gateway (client → services)
- **Service Mesh**: Service-to-service communication (internal)

### 9.4.2. API Versioning

**Vấn đề**: Service cần update API nhưng vẫn phải support clients cũ.

**Strategies:**

**1. URL Versioning**
```
/api/v1/users
/api/v2/users
```

**2. Header Versioning**
```
GET /api/users
Accept: application/vnd.api.v1+json
```

**3. Query Parameter**
```
/api/users?version=1
```

**Spring Cloud Gateway Example:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service-v1
          uri: lb://user-service-v1
          predicates:
            - Path=/api/v1/users/**
        - id: user-service-v2
          uri: lb://user-service-v2
          predicates:
            - Path=/api/v2/users/**
```

---

## 9.5. Microservices Challenges (Thách thức)

### 9.5.1. Data Consistency

**Vấn đề**: Mỗi service có database riêng → Không thể dùng ACID transaction across services.

**Giải pháp:**
1. **Saga Pattern**: Chia transaction thành các steps, mỗi step có compensating action
2. **Eventual Consistency**: Chấp nhận data tạm thời không nhất quán
3. **Two-Phase Commit (2PC)**: Strong consistency nhưng chậm (ít dùng)

### 9.5.2. Service Decomposition

**Làm sao chia Monolith thành Microservices?**

**Strategies:**
1. **By Business Domain** (DDD - Domain-Driven Design)
   - User Service, Order Service, Payment Service
2. **By Data**
   - Service có database riêng, không share DB
3. **By Team Structure** (Conway's Law)
   - Team nào maintain service đó

**Anti-patterns:**
- ❌ Chia theo technical layers (Controller Service, Business Service)
- ❌ Services quá nhỏ (nanoservices) → Overhead cao
- ❌ Services quá lớn → Vẫn là monolith

### 9.5.3. Testing Microservices

**Challenges:**
- Services phụ thuộc nhau → Khó test isolated
- Network latency → Test chậm
- Distributed state → Khó reproduce bugs

**Testing Strategies:**
1. **Unit Tests**: Test từng service riêng
2. **Integration Tests**: Test service + database
3. **Contract Tests**: Test API contracts (Pact)
4. **End-to-End Tests**: Test toàn bộ flow (chậm, ít dùng)

---

## Tổng kết Phần 9: Microservices

Đã hoàn thành **Phần 9: Microservices Architecture** với nội dung toàn diện:

✅ **9.1. Fundamentals**: Microservices vs Monolith, Khi nào nên dùng
✅ **9.2. Spring Cloud Ecosystem**:
  - Service Discovery: Eureka vs Nacos
  - API Gateway: Zuul vs Spring Cloud Gateway
  - Load Balancing: Ribbon vs LoadBalancer
  - Feign Client: Declarative HTTP client
  - Config Management: Config Server vs Nacos Config
  - Distributed Tracing: Sleuth + Zipkin
✅ **9.3. Service Communication**: Sync vs Async, REST vs RPC vs MQ
✅ **9.4. Service Governance**: Service Mesh, API Versioning
✅ **9.5. Challenges**: Data Consistency, Service Decomposition, Testing

**Tổng cộng: ~800 lines** kiến thức Microservices thực tế với Spring Cloud!

---

*Kết thúc Phần 9 - Microservices Architecture*
