# Redis 缓存序列化

> 最后更新: 2026-06-14
> ⬅️ [返回缓存总览](README.md) | [缓存模式](patterns.md) | [多级缓存](multi-level.md)

Redis 是 K-V 存储，**Key/Value 的序列化方式**直接影响可读性、跨语言兼容性、Schema 演进能力。Spring Data Redis 提供 5+ 种序列化器，选错会踩"反序列化失败"、"类型信息丢失"等坑。

---

## 🎯 一句话定位

**Key 用 `StringRedisSerializer`**（可读 + 跨语言）；**Value 用 `GenericJackson2JsonRedisSerializer`**（默认推荐，自带类型信息 + JSON 可读）。**key/value 序列化器要分离**，避免 Key 被二进制化。

---

## 一、5 大序列化器对比

| 序列化器 | 数据格式 | 可读性 | 类型信息 | 性能 | 跨语言 | 适用 |
|---------|---------|:------:|:-------:|:----:|:------:|------|
| **`JdkSerializationRedisSerializer`** | Java 二进制 | ❌ | ✅ | ⭐⭐⭐⭐⭐ | ❌ | 默认（不推荐） |
| **`StringRedisSerializer`** | UTF-8 字符串 | ✅ | ❌ | ⭐⭐⭐⭐⭐ | ✅ | Key / 简单字符串 |
| **`Jackson2JsonRedisSerializer<T>`** | JSON | ✅ | ⚠️ 需指定 Class | ⭐⭐⭐⭐ | ✅ | 固定类型 Value |
| **`GenericJackson2JsonRedisSerializer`** | JSON（带 `@class`） | ✅ | ✅ | ⭐⭐⭐⭐ | ✅ | **多类型 Value（推荐）** |
| **`GenericToStringSerializer<T>`** | toString 字符串 | ⚠️ | ❌ | ⭐⭐⭐⭐⭐ | ❌ | 简单类型（数字/枚举） |

---

## 二、各序列化器详解

### 1. `JdkSerializationRedisSerializer`（Spring 默认）

```java
@Bean
public RedisTemplate<String, User> redisTemplate(RedisConnectionFactory cf) {
    RedisTemplate<String, User> template = new RedisTemplate<>();
    template.setConnectionFactory(cf);
    template.setDefaultSerializer(new JdkSerializationRedisSerializer());
    return template;
}
```

> ⚠️ **问题**：Java 二进制、不可读、跨语言不可用。**生产环境不推荐**作为默认。

### 2. `StringRedisSerializer`（Key 必备）

```java
template.setKeySerializer(new StringRedisSerializer());
template.setHashKeySerializer(new StringRedisSerializer());
```

> ✅ **优点**：可读、跨语言（任何语言都能读 Redis）、节省空间。
> 📌 **Key 一律用这个**。

### 3. `Jackson2JsonRedisSerializer<T>`（固定类型）

```java
Jackson2JsonRedisSerializer<User> serializer =
    new Jackson2JsonRedisSerializer<>(User.class);

template.setValueSerializer(serializer);
```

> ⚠️ **限制**：必须**指定 Class**——存 `User` 读出来仍是 `User`，存 `Order` 读出来**报错**（类型不匹配）。

### 4. `GenericJackson2JsonRedisSerializer`（**推荐**）

```java
@Bean
public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory cf) {
    RedisTemplate<String, Object> template = new RedisTemplate<>();
    template.setConnectionFactory(cf);

    StringRedisSerializer keySer = new StringRedisSerializer();
    GenericJackson2JsonRedisSerializer valSer = new GenericJackson2JsonRedisSerializer();

    template.setKeySerializer(keySer);
    template.setValueSerializer(valSer);
    template.setHashKeySerializer(keySer);
    template.setHashValueSerializer(valSer);
    return template;
}
```

**优势**：写入时**自动添加 `@class` 字段**，反序列化时按类型还原：

```json
{
  "@class": "com.example.User",
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com"
}
```

> ✅ 一个 `RedisTemplate<String, Object>` 通吃所有类型。
> ⚠️ 多态 / 抽象类 / 接口：JSON 默认丢失子类信息，需配合 `DefaultTyping` 或 jackson 多态配置。

### 5. `GenericToStringSerializer<T>`

```java
GenericToStringSerializer<Integer> serializer =
    new GenericToStringSerializer<>(Integer.class);
```

> 适用：纯数字、枚举等 `toString()` 安全的简单类型。

---

## 三、Key / Value 序列化器分离

> ❗ **最佳实践**：Key 和 Value 用**不同的**序列化器（Key 必须 `StringRedisSerializer`，Value 按需）。

```java
@Bean
public RedisTemplate<String, User> userRedisTemplate(RedisConnectionFactory cf) {
    RedisTemplate<String, User> template = new RedisTemplate<>();
    template.setConnectionFactory(cf);

    // Key 用 String
    template.setKeySerializer(new StringRedisSerializer());
    template.setHashKeySerializer(new StringRedisSerializer());

    // Value 用 JSON
    template.setValueSerializer(new Jackson2JsonRedisSerializer<>(User.class));
    template.setHashValueSerializer(new Jackson2JsonRedisSerializer<>(User.class));

    template.afterPropertiesSet();
    return template;
}
```

> 这样 Redis 里的 key 是 `"user:1"`（可读），value 是 JSON 字符串（跨语言）。

---

## 四、Spring Cache 序列化配置

```java
@Bean
public CacheManager cacheManager(RedisConnectionFactory cf) {
    RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(Duration.ofMinutes(10))
        .serializeKeysWith(RedisSerializationContext.SerializationPair
            .fromSerializer(new StringRedisSerializer()))           // Key: String
        .serializeValuesWith(RedisSerializationContext.SerializationPair
            .fromSerializer(new GenericJackson2JsonRedisSerializer())); // Value: JSON

    return RedisCacheManager.builder(cf)
        .cacheDefaults(config)
        .build();
}
```

---

## 五、多态类型支持（Polymorphism）

> **问题**：`GenericJackson2JsonRedisSerializer` 默认只支持**具体类**。如果 Value 是接口/抽象类，需开启 `DefaultTyping`。

```java
ObjectMapper om = new ObjectMapper();
om.activateDefaultTyping(
    om.getPolymorphicTypeValidator(),        // 安全校验器
    ObjectMapper.DefaultTyping.NON_FINAL,    // 非 final 类启用
    JsonTypeInfo.As.PROPERTY                 // 用属性记录类型
);

GenericJackson2JsonRedisSerializer serializer =
    new GenericJackson2JsonRedisSerializer(om);
```

**生成的 JSON**：

```json
{
  "@class": "com.example.payment.OrderPayment",
  "amount": 100,
  "currency": "CNY"
}
```

> ⚠️ **安全风险**：开启 `DefaultTyping` 后，反序列化可被利用触发 gadget chain 攻击。生产环境**必须**配置 `PolymorphicTypeValidator` 限制反序列化类型。

```java
PolymorphicTypeValidator validator = BasicPolymorphicTypeValidator.builder()
    .allowIfBaseType(Object.class)
    .allowIfSubType("com.example.domain")  // 只允许特定包
    .allowIfSubType("java.util")           // 集合
    .build();
```

---

## 六、Schema 演进注意事项

> 缓存不是真理来源（DB 才是），但**对象结构变更**仍可能引发反序列化失败。

### 1. 新增字段（向后兼容）

```java
// 旧版本缓存
{"id":1,"name":"Alice"}

// 新版本对象新增 email 字段
public class User {
    private Long id;
    private String name;
    private String email;  // 新增
}
```

> ✅ Jackson 默认**忽略未知字段 / 缺失字段**——可以正常反序列化（email 为 null）。

### 2. 删除字段（可能报错）

> 旧缓存有 `phone`，新对象没 `phone` 字段 → 默认**忽略**，没问题。
> 反之（新对象有 `phone`，旧缓存没）→ `phone = null`，无问题。
> **结论**：删除字段**通常安全**。

### 3. 重命名字段（会丢数据）

```java
// 旧: userName → 新: name
public class User {
    private String name;  // 旧 userName 数据丢
}
```

> ⚠️ 旧缓存反序列化后 `name = null`。**解决方案**：保留字段 + `@JsonAlias("userName")` 兼容。

### 4. 枚举值变更（会报错）

```java
// 旧: STATUS_ACTIVE = 1
// 新: STATUS_ACTIVE = 100
```

> ⚠️ 旧缓存反序列化失败 → `InvalidFormatException`。
> **解决方案**：用 `@JsonEnumDefaultValue` + 兜底逻辑，或全量刷新缓存。

---

## 七、避免反序列化失败的 4 个实践

| 实践 | 说明 |
|------|------|
| **`@JsonIgnoreProperties(ignoreUnknown = true)`** | 忽略未知字段 |
| **`@JsonInclude(Include.NON_NULL)`** | 不序列化 null 字段 |
| **Jackson `DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES = false`** | 全局关闭 |
| **TTL 短 + 异常降级** | 反序列化失败 → 删除 key → 走 DB |

---

## 八、性能对比（量级参考）

| 序列化器 | 序列化 1KB 对象耗时 | 反序列化耗时 |
|---------|:-------------------:|:------------:|
| JDK 二进制 | ~10 μs | ~25 μs |
| String | ~2 μs | ~2 μs |
| Jackson JSON | ~50 μs | ~80 μs |
| Protobuf | ~30 μs | ~40 μs |

> 序列化通常**不是瓶颈**——Redis 网络 IO（毫秒级）>> 序列化 CPU 耗时。

---

## 🤔 思考

1. **为什么 Spring Cache 默认用 JDK 序列化？** 历史原因——最早 Spring Data Redis 就这么写。生产应**显式覆盖**。
2. **`GenericJackson2JsonRedisSerializer` 的 `@class` 字段会影响性能吗？** 影响很小（多 30 字节），收益远大于成本。
3. **Schema 演进时缓存怎么办？** 接受短时间不一致（TTL 过期后重建），或主动批量失效。
4. **为什么 Key 不建议 JSON 序列化？** Key 是定位标识，应该**可读 + 跨语言**——String 最合适。

---

## 相关章节

- ⬅️ [返回缓存总览](README.md)
- [缓存模式](patterns.md) — 4 大模式
- [多级缓存](multi-level.md) — L1+L2 架构
- [缓存实现](implementations-and-best-practices.md) — Redis 配置