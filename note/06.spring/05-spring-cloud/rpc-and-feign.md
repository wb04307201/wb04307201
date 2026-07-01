# RPC 与 OpenFeign

> ⬅️ [返回 05 Spring Cloud](README.md) | [负载均衡](load-balancer.md) | [熔断降级](circuit-breaker.md)

在微服务架构中，**服务之间如何调用**？HTTP/REST 是最常见的方式——**OpenFeign** 让远程调用像调用本地方法一样简单。

---

## 🎯 一句话定位

**OpenFeign = "声明式 HTTP 客户端"**——用 Java 接口 + 注解定义远程调用，**自动集成** LoadBalancer（负载均衡）、Sentinel/Resilience4j（熔断降级）、HttpMessageConverter（数据转换）。**比 RestTemplate/WebClient 更优雅**。

---

## 一、为什么需要 RPC 框架

### 没有 RPC 框架时

```java
// ❌ 手写 HTTP 调用（RestTemplate）
@Service
public class OrderService {
    @Autowired
    private RestTemplate restTemplate;

    public User getUser(Long id) {
        String url = "http://user-service/users/" + id;  // 硬编码服务名
        return restTemplate.getForObject(url, User.class);
    }
}
```

**痛点**：
- URL 硬编码
- 错误处理繁琐
- 难以维护
- 没有负载均衡集成

### 使用 OpenFeign 后

```java
// ✅ 声明式 Feign Client
@FeignClient(name = "user-service")  // 服务名
public interface UserFeignClient {
    @GetMapping("/users/{id}")
    User getUser(@PathVariable Long id);
}

// 像调用本地方法一样
@Service
public class OrderService {
    @Autowired
    private UserFeignClient userFeignClient;

    public User getUser(Long id) {
        return userFeignClient.getUser(id);  // 自动负载均衡
    }
}
```

**优点**：
- ✅ 声明式（接口 + 注解）
- ✅ 自动集成 LoadBalancer
- ✅ 自动序列化（JSON）
- ✅ 易于测试

---

## 二、OpenFeign 4 大核心特性

| 特性 | 说明 |
|------|------|
| **声明式** | 用 Java 接口定义远程调用 |
| **集成 LoadBalancer** | 自动负载均衡 |
| **集成熔断器** | 可选 Sentinel/Resilience4j |
| **可插拔编码器** | Jackson、Gson、自定义 |

---

## 三、OpenFeign vs Dubbo vs gRPC

| 维度 | OpenFeign | Dubbo | gRPC |
|------|-----------|-------|------|
| **协议** | HTTP/REST | 自定义 TCP | HTTP/2 |
| **性能** | 中（HTTP） | 高（二进制） | 高（HTTP/2） |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **生态** | Spring Cloud | Alibaba | 跨语言 |
| **跨语言** | ❌（仅 Java） | ❌（仅 Java） | ✅ |
| **使用场景** | Spring Cloud 微服务 | 高性能 RPC | 跨语言微服务 |

> 📌 **Spring Cloud 生态首选 OpenFeign**。

---

## 四、OpenFeign 实战

### 1. 添加依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>
```

### 2. 启用 Feign

```java
@SpringBootApplication
@EnableFeignClients
public class OrderServiceApplication { ... }
```

### 3. 定义 Feign Client

```java
@FeignClient(
    name = "user-service",                    // 服务名（注册中心中的名字）
    path = "/api/users",                       // 公共前缀
    fallback = UserFeignClientFallback.class   // 降级处理
)
public interface UserFeignClient {

    @GetMapping("/{id}")
    User getUser(@PathVariable Long id);

    @PostMapping
    User createUser(@RequestBody User user);

    @GetMapping("/search")
    List<User> searchUsers(@RequestParam String name, @RequestParam Integer page);

    @DeleteMapping("/{id}")
    void deleteUser(@PathVariable Long id);
}
```

### 4. 调用

```java
@Service
public class OrderService {
    @Autowired
    private UserFeignClient userFeignClient;

    public User getUser(Long id) {
        return userFeignClient.getUser(id);
    }
}
```

---

## 五、6 大常用配置

### 1. 超时时间

```yaml
feign:
  client:
    config:
      default:
        connectTimeout: 5000        # 连接超时（默认 10s）
        readTimeout: 5000            # 读超时（默认 60s）

      user-service:                  # 针对特定服务
        connectTimeout: 3000
        readTimeout: 3000
```

### 2. 重试机制

```yaml
feign:
  client:
    config:
      default:
        retryer: com.example.CustomRetryer  # 自定义重试
```

```java
public class CustomRetryer implements Retryer {
    @Override
    public void continueOrPropagate(RetryableException e) {
        // 重试 3 次，每次间隔 100ms
        if (attempt++ >= 3) throw e;
    }
}
```

### 3. 日志

```yaml
feign:
  client:
    config:
      default:
        loggerLevel: BASIC  # NONE, BASIC, HEADERS, FULL
```

```java
@Configuration
public class FeignLogConfig {
    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.FULL;
    }
}
```

### 4. 拦截器

```java
@Component
public class AuthInterceptor implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        template.header("Authorization", "Bearer " + getToken());
    }
}
```

### 5. 压缩

```yaml
feign:
  compression:
    request:
      enabled: true
      mime-types: text/xml,application/xml,application/json
      min-request-size: 2048
    response:
      enabled: true
```

### 6. Fallback（降级）

```java
@Component
public class UserFeignClientFallback implements UserFeignClient {
    @Override
    public User getUser(Long id) {
        return new User();  // 降级返回
    }
}

@FeignClient(name = "user-service", fallback = UserFeignClientFallback.class)
public interface UserFeignClient { ... }
```

---

## 六、请求压缩与大数据

### 上传文件

```java
@FeignClient(name = "file-service")
public interface FileFeignClient {

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    String upload(@RequestPart MultipartFile file);
}
```

### 返回 ResponseEntity（需要完整响应）

```java
@GetMapping("/{id}")
ResponseEntity<User> getUser(@PathVariable Long id);
```

---

## 七、与熔断器集成

### 集成 Sentinel

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
```

```java
@FeignClient(
    name = "user-service",
    fallback = UserFeignClientFallback.class
    // 不需要 fallbackFactory，@SentinelResource 在 Feign 中不生效
)
public interface UserFeignClient { ... }
```

### 集成 Resilience4j

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-cloud2</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-resilience4j</artifactId>
</dependency>
```

---

## 八、4 种调用方式对比

| 维度 | OpenFeign | RestTemplate | WebClient | Dubbo |
|------|----------|--------------|----------|-------|
| **风格** | 声明式 | 命令式 | 响应式 | 自定义 |
| **代码量** | 少（接口） | 多（手写） | 中 | 少 |
| **LoadBalancer** | ✅ 内置 | 需 @LoadBalanced | 需配置 | ✅ 内置 |
| **异步** | ❌ | ❌ | ✅ | ✅ |
| **性能** | 中 | 中 | 高 | 高 |
| **学习成本** | 低 | 低 | 中 | 中 |
| **推荐** | 微服务首选 | 简单调用 | 响应式 | 高性能 RPC |

---

## 九、最佳实践

### 1. 命名规范

```
FeignClient 接口名 = 目标服务名 + FeignClient
例：UserFeignClient、OrderFeignClient
```

### 2. 合理设置超时

```yaml
feign:
  client:
    config:
      default:
        connectTimeout: 2000
        readTimeout: 5000
```

> ⚠️ **避免过短超时**（如 1s）——网络抖动容易超时。

### 3. Fallback 必备

> 所有 Feign Client 都要有 Fallback，否则下游服务故障会拖垮上游。

### 4. 监控

> 监控 Feign 调用的 QPS、成功率、延迟——通过 Micrometer + Prometheus。

---

## 🤔 思考

1. **OpenFeign 和 RestTemplate 怎么选？** 优先 OpenFeign（声明式、LoadBalancer 集成），简单场景用 RestTemplate。
2. **OpenFeign 是同步还是异步？** 同步。可考虑用 CompletableFuture 包装。
3. **Feign 调 Feign？** 可以（服务 A → B → C），但要避免长链路（监控难、故障传播）。
4. **为什么 Feign 默认集成 LoadBalancer？** Spring Cloud 设计——"开箱即用"的微服务调用。

---

## 相关章节

- ⬅️ [返回 05 Spring Cloud](README.md)
- [负载均衡](load-balancer.md) — Feign 自动集成 LoadBalancer
- [熔断降级](circuit-breaker.md) — Feign 失败时的熔断
- [服务注册](service-registry/) — Feign 通过服务名找到实例
- [07 可观测性/Micrometer](../07-observability/micrometer.md) — Feign 监控指标
