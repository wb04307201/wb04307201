# Spring Cache

## 一、Spring Cache 概述

### 1. 什么是 Spring Cache
Spring Cache 是 Spring Framework 提供的一个抽象层，用于简化应用程序中的缓存操作。它允许开发者在不修改业务逻辑代码的情况下，通过简单的注解实现方法调用结果的缓存和检索。

### 2. 核心特性
- **基于注解的配置**：使用 `@Cacheable`, `@CacheEvict` 等注解
- **统一抽象层**：支持多种缓存实现（如 Ehcache, Redis, Caffeine 等）
- **透明集成**：与 Spring 事务管理类似，对业务代码透明
- **细粒度控制**：支持条件缓存、过期时间等配置

## 二、基本使用

### 1. 启用缓存支持
在 Spring Boot 应用中，只需在主类或配置类上添加 `@EnableCaching` 注解：

```java
@SpringBootApplication
@EnableCaching
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

### 2. 常用注解

#### @Cacheable
标记方法的结果需要被缓存：

```java
@Cacheable(value = "users", key = "#id")
public User getUserById(Long id) {
    // 实际数据库查询逻辑
    return userRepository.findById(id);
}
```

#### @CachePut
更新缓存中的内容（方法总是会被执行）：

```java
@CachePut(value = "users", key = "#user.id")
public User updateUser(User user) {
    // 更新数据库逻辑
    return userRepository.save(user);
}
```

#### @CacheEvict
从缓存中移除数据：

```java
@CacheEvict(value = "users", key = "#id")
public void deleteUser(Long id) {
    // 删除数据库记录逻辑
    userRepository.deleteById(id);
}
```

#### @Caching
组合多个缓存操作：

```java
@Caching(
    evict = {
        @CacheEvict(value = "users", key = "#user.id"),
        @CacheEvict(value = "usersByEmail", key = "#user.email")
    }
)
public void updateUser(User user) {
    // 更新逻辑
}
```

#### @CacheConfig
类级别的缓存配置：

```java
@CacheConfig(cacheNames = "users")
public class UserService {
    
    @Cacheable(key = "#id")
    public User getUserById(Long id) {
        // ...
    }
}
```

### 3. SpEL 表达式支持
Spring Cache 支持使用 SpEL 表达式定义 key 和 condition：

```java
@Cacheable(value = "users", 
           key = "#root.methodName + #id",
           condition = "#id > 10",
           unless = "#result == null")
public User getUserById(Long id) {
    // ...
}
```

常用 SpEL 变量：
- `#result`：方法返回值
- `#root.methodName`：当前方法名
- `#arg0`, `#p0`, `#a0`：第一个参数（不同索引方式）

## 三、缓存实现选择

### 1. 常见缓存实现

#### Caffeine (Spring Boot 默认)
- 内存缓存，高性能
- 适合单机应用
- 配置示例：

```properties
spring.cache.type=caffeine
spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=10m
```

#### Redis
- 分布式缓存
- 适合集群环境
- 配置示例：

```properties
spring.cache.type=redis
spring.redis.host=localhost
spring.redis.port=6379
```

#### Ehcache
- 成熟的缓存解决方案
- 支持持久化和分布式（通过 Terracotta）
- 配置示例：

```xml
<!-- ehcache.xml -->
<cache name="users"
       maxEntriesLocalHeap="1000"
       timeToLiveSeconds="600"/>
```

### 2. 自定义缓存实现
可以通过实现 `CacheManager` 接口来集成其他缓存系统。

## 四、高级配置

### 1. 条件缓存
使用 `condition` 和 `unless` 属性控制缓存行为：

```java
@Cacheable(value = "products", 
           condition = "#name.length() < 32",
           unless = "#result == null || #result.price < 10")
public Product findProductByName(String name) {
    // ...
}
```

### 2. 同步缓存
使用 `sync` 属性避免缓存击穿：

```java
@Cacheable(value = "hotProducts", key = "#category", sync = true)
public List<Product> getHotProducts(String category) {
    // 模拟耗时操作
    Thread.sleep(1000);
    return productRepository.findHotByCategory(category);
}
```

### 3. 自定义 Key 生成器
实现 `KeyGenerator` 接口自定义 key 生成逻辑：

```java
@Configuration
public class CacheConfig {
    
    @Bean("customKeyGenerator")
    public KeyGenerator keyGenerator() {
        return (target, method, params) -> {
            StringBuilder sb = new StringBuilder();
            sb.append(target.getClass().getSimpleName());
            sb.append(".");
            sb.append(method.getName());
            for (Object param : params) {
                sb.append(".").append(param.toString());
            }
            return sb.toString();
        };
    }
}

// 使用自定义 key 生成器
@Cacheable(value = "customCache", keyGenerator = "customKeyGenerator")
public Object customCacheMethod(String param1, Integer param2) {
    // ...
}
```

## 五、优缺点分析

### 1. 优点
- **简化开发**：通过注解即可实现缓存，减少样板代码
- **解耦**：业务代码与缓存实现解耦，便于切换缓存后端
- **声明式**：配置驱动，易于理解和维护
- **集成性好**：与 Spring 生态无缝集成
- **性能提升**：显著减少重复计算或数据库查询

### 2. 缺点
- **调试困难**：缓存行为可能使调试变得复杂
- **一致性挑战**：在分布式环境中维护缓存一致性较难
- **内存消耗**：不当的缓存配置可能导致内存溢出
- **过期策略**：需要手动管理缓存过期，否则可能导致数据不一致
- **不适合所有场景**：对于频繁更新的数据，缓存可能适得其反

## 六、最佳实践

1. **合理设置过期时间**：根据业务特点设置适当的缓存过期策略
2. **避免缓存过大对象**：大对象会消耗大量内存
3. **考虑缓存穿透**：对不存在的数据也进行适当缓存或使用布隆过滤器
4. **处理缓存雪崩**：使用随机过期时间或分级缓存策略
5. **监控缓存命中率**：通过监控了解缓存效果
6. **测试缓存行为**：编写单元测试验证缓存逻辑
7. **考虑分布式锁**：在高并发更新场景下使用分布式锁

## 七、示例项目结构

```
src/main/java/
├── com.example.demo
│   ├── config
│   │   └── CacheConfig.java  # 自定义缓存配置
│   ├── model
│   │   └── User.java         # 实体类
│   ├── repository
│   │   └── UserRepository.java # 数据访问层
│   └── service
│       └── UserService.java  # 业务逻辑层，使用缓存注解
```

## 八、常见问题解决

1. **缓存不生效**：
    - 检查是否添加了 `@EnableCaching`
    - 确认方法是否被 Spring 管理（有 `@Service` 等注解）
    - 检查缓存名称是否正确

2. **序列化问题**：
    - 确保缓存的对象实现 `Serializable` 接口
    - 或配置自定义的序列化方式

3. **多参数 key 问题**：
    - 使用 SpEL 表达式明确指定 key 生成规则
    - 或实现自定义 `KeyGenerator`

4. **缓存更新问题**：
    - 确保更新操作使用了 `@CachePut` 或 `@CacheEvict`
    - 注意方法的调用顺序（AOP 代理特性）

通过以上内容，您应该能够对 Spring Cache 的基本功能、使用方式和优缺点有全面的了解。在实际项目中，建议从小规模开始使用，逐步扩大缓存范围，同时密切监控缓存效果和系统性能。