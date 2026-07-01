# 缓存注解

> ⬅️ [返回注解速查](../README.md) | [事务注解](transaction.md)

本节是 Spring Cache 注解的速查手册——`@Cacheable` / `@CachePut` / `@CacheEvict` / `@Caching` / `@CacheConfig` 的关键属性与 SpEL 语法。**深读请前往 [03-data/cache](../../README.md)**。

---

## 🎯 一句话定位

**缓存注解 = "方法结果按 key 缓存起来"**——`@Cacheable` 命中即跳过方法，`@CachePut` 总执行并覆盖缓存，`@CacheEvict` 删除缓存，`@CacheConfig` 类级别统一配置。

---

## 一、5 个核心注解速查

| 注解 | 作用 | 关键属性 |
|:-----|:-----|:---------|
| **@Cacheable** | 命中缓存则跳过方法 | `value` / `key` / `condition` / `unless` / `sync` |
| **@CachePut** | 总是执行方法，并更新缓存 | `value` / `key` |
| **@CacheEvict** | 执行方法后删除缓存 | `value` / `key` / `allEntries` / `beforeInvocation` |
| **@Caching** | 组合多个缓存注解 | `cacheable` / `put` / `evict` |
| **@CacheConfig** | 类级别统一缓存配置 | `cacheNames` / `keyGenerator` / `cacheManager` |

### @EnableCaching

⚠️ **Spring Boot 不会自动启用 `@EnableCaching`**——`spring-boot-starter-cache` 的自动装配**只在**用户显式声明 `@EnableCaching` 时才生效；没有这个注解，所有 `@Cacheable` 全部 no-op。

```java
@Configuration
@EnableCaching   // 必须显式声明，不能省略
public class CacheConfig { }
```

---

## 二、@Cacheable / @CachePut / @CacheEvict 属性对照

| 属性 | 默认 | 说明 |
|:-----|:-----|:-----|
| `value` / `cacheNames` | 必填 | 缓存名称（对应 `ConcurrentMapCacheManager` 的 Cache） |
| `key` | `""`（默认 SimpleKey 包含所有参数） | 缓存 key（SpEL 表达式） |
| `keyGenerator` | — | 自定义 KeyGenerator（与 `key` 互斥） |
| `condition` | — | 满足条件才缓存（SpEL，方法调用前后都判断） |
| `unless` | — | 不缓存条件（SpEL，方法返回后判断，可访问 `#result`） |
| `sync` | `false` | 是否同步（多线程下防止击穿，仅 `@Cacheable`） |
| `allEntries` | `false` | `@CacheEvict` 是否清空整个 Cache |
| `beforeInvocation` | `false` | `@CacheEvict` 在方法调用前/后清除（默认在方法成功后清除） |

```java
@Cacheable(value = "users", key = "#id", unless = "#result == null")
public User findById(Long id) { ... }

@CachePut(value = "users", key = "#user.id")
public User update(User user) { ... }

@CacheEvict(value = "users", key = "#id")
public void delete(Long id) { ... }

@CacheEvict(value = "users", allEntries = true)        // 清空整个 cache
public void reload() { ... }
```

---

## 三、SpEL 表达式速查

> `#` 引用参数 / `#root` 引用方法上下文；`#result` 在 `unless` 中可用。

| 表达式 | 含义 | 示例 |
|:-------|:-----|:-----|
| `#参数名` | 按名称引用方法参数 | `#id` / `#userId` |
| `#a0` / `#p0` | 按位置引用参数 | `#a0`（第一个参数） |
| `#root.method` | 当前方法对象 | `#root.method.name` |
| `#root.target` | 目标对象 | `#root.targetClass.simpleName` |
| `#root.args[0]` | 参数数组 | `#root.args[0]` |
| `#result` | 方法返回值（`@Cacheable` / `@CachePut` 的 `unless` 中可用） | `unless = "#result == null"` |
| `#root.caches` | 涉及的 cache 列表 | `#root.caches[0].name` |

### 常用 key 策略

```java
// 1. 简单参数
@Cacheable(value = "user", key = "#id")
public User findById(Long id)

// 2. 多个参数组合
@Cacheable(value = "user", key = "#deptId + ':' + #userId")
public User find(Long deptId, Long userId)

// 3. 对象属性
@Cacheable(value = "user", key = "#user.id")
public User find(UserDTO user)

// 4. 复杂 key
@Cacheable(value = "user", key = "T(java.lang.String).format('%s:%d', #type, #page)")

// 5. 哈希计算
@Cacheable(value = "user", key = "#user.hashCode()")
```

---

## 四、condition vs unless 对比

| 维度 | `condition` | `unless` |
|:-----|:------------|:---------|
| **判断时机** | 方法调用**前** | 方法调用**后** |
| **可访问** | `#参数` / `#root` | `#参数` / `#root` / **`#result`** |
| **命中策略** | 不满足则**不查缓存也不存** | 不满足则**不存缓存**（可查） |
| **典型场景** | 只缓存特定条件的方法 | 过滤掉空值/异常结果 |

```java
// condition: 只缓存 id > 0 的查询
@Cacheable(value = "user", key = "#id", condition = "#id > 0")
public User findById(Long id)

// unless: 不缓存 null 结果
@Cacheable(value = "user", key = "#id", unless = "#result == null")
public User findById(Long id)
```

---

## 五、@Caching 组合用法

> 当一个方法需要同时执行多个缓存操作（可缓存 + 可驱逐 + 可更新）。

```java
@Caching(
    cacheable = @Cacheable(value = "user", key = "#id"),
    evict    = @CacheEvict(value = "userList", allEntries = true)
)
public User findAndEvictList(Long id) { ... }
```

---

## 六、@CacheConfig 类级别配置

> 避免在每个方法上重复 `value = "user"`。

```java
@Service
@CacheConfig(cacheNames = "user", keyGenerator = "myKeyGen")
public class UserService {

    @Cacheable(key = "#id")
    public User findById(Long id) { ... }   // 自动应用 cacheNames="user"

    @CachePut(key = "#user.id")
    public User update(User user) { ... }
}
```

---

## 🤔 思考

1. **@Cacheable 默认 key 是什么？** `SimpleKeyGenerator` 把**所有参数**算 hash——重载方法或参数顺序不一致会导致 key 不同。
2. **为什么 @CacheEvict 默认 beforeInvocation = false？** 默认在方法**成功后**才清缓存，避免"方法失败却清掉缓存"导致下次再查。
3. **@Cacheable 适合写操作吗？** 不适合。写操作请用 `@CachePut`（总执行）或 `@CacheEvict`（清缓存）。
4. **Redis 中 key 怎么写？** Spring Cache 会把 `value + "::" + key` 拼接为 Redis key，例如 `user::1234`。

---

## 深入阅读

- [03-data/cache/README](../../README.md) — 缓存完整指南
- [03-data/cache/patterns](../03-data/cache/patterns.md) — Cache-Aside、Read-Through 等模式
- [03-data/cache/serialization](../03-data/cache/serialization.md) — 缓存序列化
- [03-data/cache/multi-level](../03-data/cache/multi-level.md) — 多级缓存

## 相关章节

- ⬅️ [返回注解速查](../README.md)
- [事务注解](transaction.md) — @Cacheable 与 @Transactional 共存时的事务边界
