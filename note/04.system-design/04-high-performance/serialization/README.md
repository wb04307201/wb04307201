<!--
module:
  parent: system-design
  slug: system-design/serialization
  type: article
  category: 主模块子文章
  summary: 序列化是将内存中的对象转换为字节流的过程，反序列化则是其逆过程。在 RPC 调用、消息队列、缓存存储等场景中，序列化性能直接影响系统的吞吐量和延迟。
-->

# 序列化优化

> 序列化是将内存中的对象转换为字节流的过程，反序列化则是其逆过程。在 RPC 调用、消息队列、缓存存储等场景中，序列化性能直接影响系统的吞吐量和延迟。
>
## 目录

- [1. 为什么需要关注序列化性能](#1-为什么需要关注序列化性能)
- [2. 主流序列化方案对比](#2-主流序列化方案对比)
- [3. Protobuf 使用指南](#3-protobuf-使用指南)
- [4. Kryo 使用指南](#4-kryo-使用指南)
- [5. 序列化最佳实践](#5-序列化最佳实践)

---
## 引言：性能对比

序列化优化 的关键不是'快'——是**什么时候慢、慢多少、为什么**。

本篇用'常见 vs 极端'两组数字切入，把排查思路和优化边界讲清。

---

## 1. 为什么需要关注序列化性能

### 1.1 序列化在系统中的位置

```
客户端请求 → [反序列化] → 业务逻辑 → [序列化] → 响应/消息/缓存
              ↑                              ↑
           性能损耗                        性能损耗
```

### 1.2 序列化影响性能的场景

| 场景 | 序列化开销占比 | 说明 |
|------|--------------|------|
| **RPC 调用(Dubbo/gRPC)** | 10%~30% | 每次调用都需序列化/反序列化 |
| **消息队列生产消费** | 5%~20% | 高频消息场景下尤为明显 |
| **Redis 缓存读写** | 5%~15% | 大对象序列化成本更高 |
| **分布式 Session** | 3%~10% | Session 序列化影响响应时间 |
| **微服务间通信** | 10%~25% | 服务链越长，累积开销越大 |

### 1.3 性能数据参考

假设序列化一个包含 50 个字段的 Java 对象（1KB 数据）：

| 方案 | 序列化耗时 | 反序列化耗时 | 字节大小 | 压缩率 |
|------|-----------|-------------|---------|--------|
| Java 原生 | ~5μs | ~8μs | ~2KB | 1x |
| Jackson JSON | ~15μs | ~20μs | ~1.5KB | 1.3x |
| Fastjson2 | ~5μs | ~8μs | ~1.5KB | 1.3x |
| Protobuf | ~2μs | ~3μs | ~0.5KB | 4x |
| Kryo | ~1μs | ~2μs | ~0.6KB | 3.3x |
| Hessian | ~8μs | ~12μs | ~0.8KB | 2.5x |

> 数据仅供参考，实际性能取决于对象大小、字段数量和具体版本。

---

## 2. 主流序列化方案对比

### 2.1 综合对比表

| 特性 | JSON(Jackson) | Protobuf | Kryo | Hessian | MessagePack |
|------|--------------|----------|------|---------|-------------|
| **序列化速度** | 中 | 快 | 极快 | 中 | 快 |
| **压缩率** | 差 | 极好 | 好 | 好 | 好 |
| **跨语言** | ✅ 所有语言 | ✅ 所有语言 | ❌ 仅Java | ✅ 多语言 | ✅ 多语言 |
| **可读性** | ✅ 文本可读 | ❌ 二进制 | ❌ 二进制 | ❌ 二进制 | ❌ 二进制 |
| **Schema 要求** | 无 | 需要 .proto | 无 | 无 | 无 |
| **向后兼容** | ✅ | ✅ 版本兼容 | ❌ | ❌ | ❌ |
| **社区生态** | 极大 | 极大 | 中 | 中（Hessian 1.x 已停更；Hessian 2 仍由 Dubbo 维护） | 中 |
| **典型场景** | REST API | gRPC/内部通信 | 内部缓存/MQ | Dubbo2.x | 内部存储 |

### 2.2 选型建议

```
对外 API / 调试友好 → JSON (Jackson/Fastjson2)
内部 RPC / 高性能通信 → Protobuf / Kryo
跨语言 RPC → Protobuf / gRPC
Java 内部缓存/MQ → Kryo
Dubbo 框架 → Hessian2 (默认) / Protobuf (可切换)
```

---

## 3. Protobuf 使用指南

Protocol Buffers 是 Google 开源的二进制序列化方案，以高性能和小体积著称。

### 3.1 .proto 文件定义

```protobuf
syntax = "proto3";

package com.example.user;

option java_package = "com.example.user";
option java_outer_classname = "UserProto";

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  UserType type = 4;
  repeated Address addresses = 5;
  int32 age = 6;
  
  enum UserType {
    USER_TYPE_UNSPECIFIED = 0;
    NORMAL = 1;
    VIP = 2;
    ADMIN = 3;
  }
  
  message Address {
    string city = 1;
    string street = 2;
    int32 zipCode = 3;
  }
}
```

### 3.2 编码与解码

```java
// Maven 依赖
// <dependency>
//     <groupId>com.google.protobuf</groupId>
//     <artifactId>protobuf-java</artifactId>
//     <version>3.25.5</version>
// </dependency>

// 序列化 (编码)
UserProto.User user = UserProto.User.newBuilder()
        .setId(1001L)
        .setName("张三")
        .setEmail("zhangsan@example.com")
        .setType(UserProto.UserType.VIP)
        .addAddresses(UserProto.User.Address.newBuilder()
                .setCity("北京")
                .setStreet("朝阳区")
                .build())
        .build();

byte[] bytes = user.toByteArray();  // 序列化

// 反序列化 (解码)
UserProto.User decoded = UserProto.User.parseFrom(bytes);
System.out.println(decoded.getName());  // 张三
```

### 3.3 Protobuf 编码原理(简要)

Protobuf 使用 **VarInt + Tag** 编码：
- 每个字段用 `(field_number << 3) | wire_type` 作为 tag
- 数值使用 VarInt 压缩（小数字只用 1 个字节）
- 字段按 tag 排序存储，不保证顺序

```
示例: int32 id = 1, 值为 1001
Tag: (1 << 3) | 0 = 0x08  (varint 类型)
Value: 1001 → VarInt 编码为 0xE9 0x07
结果: 08 E9 07 (3 bytes)
```

### 3.4 与 Spring Boot 集成 (gRPC)

```java
// 服务端
@GrpcService
public class UserService extends UserServiceGrpc.UserServiceImplBase {
    @Override
    public void getUser(UserRequest request, StreamObserver<UserProto.User> response) {
        UserProto.User user = findUser(request.getId());
        response.onNext(user);
        response.onCompleted();
    }
}

// 客户端
@GrpcClient("user-service")
private UserServiceGrpc.UserServiceStub userServiceStub;
```

### 3.5 Protobuf 注意事项

| 注意点 | 说明 |
|--------|------|
| **字段编号不要改** | 已发布的 .proto 中，字段编号永久绑定 |
| **required 已废弃** | proto3 中所有字段都是 optional |
| **不支持 null** | 数值默认 0，字符串默认空串 |
| **大数字用 int64** | int32 最大 2^31-1，超过会溢出 |
| **reserved 保留字段** | 删除的字段用 `reserved` 标记，防止误用编号 |

---

## 4. Kryo 使用指南

Kryo 是 Java 专用的快速序列化框架，序列化和反序列化速度极快。

### 4.1 基本使用

```xml
<!-- Maven 依赖 -->
<dependency>
    <groupId>com.esotericsoftware</groupId>
    <artifactId>kryo</artifactId>
    <version>5.6.0</version>
</dependency>
```

```java
// 基本序列化
Kryo kryo = new Kryo();
kryo.setRegistrationRequired(false);  // 关闭强制注册(开发方便)

// 序列化
User user = new User(1001L, "张三", "zhangsan@example.com");
Output output = new Output(new ByteArrayOutputStream());
kryo.writeObject(output, user);
byte[] bytes = output.toBytes();

// 反序列化
Input input = new Input(new ByteArrayInputStream(bytes));
User decoded = kryo.readObject(input, User.class);
```

### 4.2 线程安全 — KryoPool

Kryo 实例**不是线程安全的**，需要使用 KryoPool。

```java
// 使用对象池管理 Kryo 实例
KryoPool pool = new KryoPool.Builder(() -> {
    Kryo kryo = new Kryo();
    kryo.setRegistrationRequired(false);
    return kryo;
}).softReferences().build();

// 使用
Kryo kryo = pool.borrow();
try {
    Output output = new Output(new ByteArrayOutputStream());
    kryo.writeObject(output, user);
    byte[] bytes = output.toBytes();
    // ...
} finally {
    pool.free(kryo);  // 必须归还!
}
```

### 4.3 Kryo 在 Redis 缓存中的应用

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // 使用 Kryo 序列化
        KryoRedisSerializer serializer = new KryoRedisSerializer();
        template.setDefaultSerializer(serializer);
        
        return template;
    }
}

public class KryoRedisSerializer implements RedisSerializer<Object> {
    private final KryoPool pool = new KryoPool.Builder(() -> new Kryo()).build();

    @Override
    public byte[] serialize(Object object) throws SerializationException {
        if (object == null) return new byte[0];
        Kryo kryo = pool.borrow();
        try (Output output = new Output(new ByteArrayOutputStream())) {
            kryo.writeClassAndObject(output, object);
            return output.toBytes();
        } finally {
            pool.free(kryo);
        }
    }

    @Override
    public Object deserialize(byte[] bytes) throws SerializationException {
        if (bytes == null || bytes.length == 0) return null;
        Kryo kryo = pool.borrow();
        try (Input input = new Input(new ByteArrayInputStream(bytes))) {
            return kryo.readClassAndObject(input);
        } finally {
            pool.free(kryo);
        }
    }
}
```

### 4.4 Kryo 注意事项

| 注意点 | 说明 |
|--------|------|
| **不是线程安全** | 必须使用 KryoPool |
| **跨语言不友好** | 仅适合 Java 到 Java 的场景 |
| **版本兼容性差** | 类结构变化可能导致反序列化失败 |
| **安全风险** | 反序列化恶意数据可能触发 RCE，不要反序列化不可信数据 |
| **注册机制** | `setRegistrationRequired(true)` 可提升性能但需预先注册类 |

---

## 5. 序列化最佳实践

### 5.1 选型决策树

```
是否需要跨语言?
  ├── 是 → 是否需要 Schema 管理?
  │         ├── 是 → Protobuf (推荐 gRPC)
  │         └── 否 → MessagePack / Hessian2
  └── 否 → 是否是 Java 内部通信?
            ├── 是 → Kryo (最高性能)
            └── 否 → JSON (开发效率优先)
```

### 5.2 通用最佳实践

1. **避免序列化大对象**: 只序列化必要字段，使用 DTO 而非 Entity
2. **按需选择格式**: 对外用 JSON 可读，内部用 Protobuf/Kryo 高性能
3. **连接复用减少序列化**: 使用 Pipeline/Batch 减少序列化次数
4. **对象池管理**: Kryo/Protobuf 解析器都应使用对象池，避免重复创建
5. **安全加固**: 不反序列化不可信数据，使用白名单机制
6. **监控序列化耗时**: 在 RPC/MQ 链路中埋点监控序列化耗时

### 5.3 反序列化安全

```java
// ❌ 危险: 直接反序列化不可信数据
Object obj = kryo.readClassAndObject(input);  // 可能被注入恶意类

// ✅ 安全: 使用白名单
kryo.setRegistrationRequired(true);
kryo.register(User.class);
kryo.register(Order.class);
// 只有注册的类才能被反序列化
```

### 5.4 性能优化 checklist

- [ ] 使用二进制协议而非 JSON 传输大对象
- [ ] 对象复用序列化/反序列化实例(对象池)
- [ ] 减少不必要的字段（使用专门的 DTO）
- [ ] 对大字段使用压缩（Gzip/Snappy）
- [ ] 避免在序列化逻辑中执行复杂计算
- [ ] 缓存频繁序列化的 Schema（Protobuf 的 Descriptor）
- [ ] 使用 `@JsonPropertyOrder` 或字段排序优化序列化输出

## 相关章节

- [消息队列](../mq/README.md) — MQ 消息的序列化是性能关键路径
- [缓存设计模式](../cache-patterns/README.md) — Redis 缓存值的序列化方案
- [连接池优化](../connection-pool/README.md) — 减少序列化次数依赖连接复用
- [Java 性能优化](../java/README.md) — JVM 层面的序列化对象复用
