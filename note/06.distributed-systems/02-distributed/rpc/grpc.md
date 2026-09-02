<!--
module:
  parent: distributed-systems
  slug: distributed-systems/rpc/grpc
  type: article
  category: 主模块子文章
  summary: gRPC Google 开源 RPC 框架，基于 HTTP/2 + Protocol Buffers。5 大核心特性 + 4 种通信模式 + Spring Boot 集成示例 + 与 REST/Dubbo 选型对比。
  depth: ⭐⭐⭐⭐
-->

# gRPC（Google RPC）

> **一句话定位**：gRPC = HTTP/2 + Protocol Buffers + 4 种通信模式，**微服务内部通信首选**（比 REST 快 5-10 倍，强类型契约）。

---

## 一、为什么需要 gRPC？

| REST 问题 | gRPC 解决方案 |
|----------|--------------|
| JSON 文本冗长（30-50% 体积）| Protobuf 二进制（紧凑 5-10 倍）|
| HTTP/1.1 队头阻塞 | HTTP/2 多路复用 |
| 运行时类型错误 | .proto 强类型契约（编译期检查）|
| 无流式支持 | 4 种通信模式（Unary/Server/Client/Bidirectional Streaming）|
| 无代码生成 | protoc 自动生成多语言 stub |

## 二、5 大核心特性

| 特性 | 说明 |
|------|------|
| **HTTP/2** | 多路复用、二进制分帧、首部压缩 |
| **Protocol Buffers** | 强类型 + 高压缩比 + 向后兼容 |
| **4 种通信模式** | Unary / Server Streaming / Client Streaming / Bidirectional |
| **多语言支持** | Java/Go/Python/Node/Ruby/C++ 等 12+ 语言 |
| **服务发现 + 负载均衡** | 集成 gRPC Name Resolver |

## 四、4 种通信模式

```protobuf
// 1. Unary（一元）
rpc GetUser(UserRequest) returns (UserResponse);

// 2. Server Streaming（服务端流）
rpc ListUsers(ListRequest) returns (stream UserResponse);

// 3. Client Streaming（客户端流）
rpc UploadLogs(stream LogEntry) returns (UploadStatus);

// 4. Bidirectional（双向流）
rpc Chat(stream Message) returns (stream Message);
```

**适用场景**：

| 模式 | 典型应用 |
|------|---------|
| Unary | CRUD API（替代 REST） |
| Server Streaming | 实时日志推送、股票报价 |
| Client Streaming | IoT 设备上报、批量上传 |
| Bidirectional | 聊天、远程调用、协同编辑 |

## 五、Spring Boot 集成（Java 示例）

```java
// 1. pom.xml
// <dependency>
//   <groupId>net.devh</groupId>
//   <artifactId>grpc-server-spring-boot-starter</artifactId>
// </dependency>

// 2. 定义 .proto
service UserService {
    rpc GetUser(UserRequest) returns (UserResponse);
}

// 3. 实现服务
@GrpcService
public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {
    @Override
    public void getUser(UserRequest req, StreamObserver<UserResponse> response) {
        UserResponse resp = UserResponse.newBuilder()
            .setId(req.getId())
            .setName("Alice")
            .build();
        response.onNext(resp);
        response.onCompleted();
    }
}

// 4. 客户端调用
@GrpcClient("user-service")
private UserServiceGrpc.UserServiceBlockingStub userStub;

public User getUser(int id) {
    return userStub.getUser(
        UserRequest.newBuilder().setId(id).build()
    ).getName();
}
```

## 六、gRPC vs REST vs Dubbo

| 维度 | gRPC | REST | Dubbo |
|------|------|-----|-------|
| 协议 | HTTP/2 | HTTP/1.1 | TCP |
| 序列化 | Protobuf | JSON | Hessian2/JSON |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 类型安全 | ✅（.proto） | ❌ | ✅ |
| 流式 | ✅ | ❌ | ⚠️ |
| 跨语言 | ✅ 12+ 语言 | ✅ | ❌（Java 生态）|
| 浏览器友好 | ❌（需 grpc-web） | ✅ | ❌ |
| 适用 | 微服务内部、强契约 | 公开 API、简单场景 | Java 内部微服务 |

## 七、生产踩坑（4 大常见）

| 坑 | 现象 | 修复 |
|----|------|------|
| **超时未配置** | 客户端卡死 | `deadlineExecutor` + ContextWithTimeout |
| **流未关闭** | 服务端内存泄漏 | `onCompleted`/`onError` 必须调用 |
| **Protobuf 版本不兼容** | 服务端升级客户端报错 | 字段用 `optional`，避免改 tag |
| **HTTP/2 队头** | 单连接复用过度 | 客户端多连接 / 服务端限流 |

## 八、面试高频 Q&A

**Q: gRPC 为什么比 REST 快？**

A：3 大原因：
1. **Protobuf 二进制**：体积小（5-10 倍）、序列化快
2. **HTTP/2 多路复用**：单连接并发多 stream，无队头阻塞
3. **长连接**：无需每次 3 次握手

**Q: gRPC 适合公开 API 吗？**

A：❌ 不适合。gRPC 基于 HTTP/2 + Protobuf，**浏览器/客户端 SDK 难集成**。公开 API 仍用 REST（OpenAPI/Swagger 生态成熟）。**内部微服务用 gRPC，外部 API 用 REST**。

## 九、相关章节

- [Apache Dubbo 协议](./apache-dubbo/README.md) — Java 生态 RPC 替代方案
- [HTTP/2 协议详解](../../../02.cs-foundations/03-network/01-tcp-ip/README.md) — gRPC 底层协议
- [微服务通信总览](../README.md) — gRPC vs REST vs MQ 选型

## 十、参考链接

- [gRPC 官方文档](https://grpc.io/docs/)
- [Protocol Buffers 指南](https://protobuf.dev/)
- [gRPC Java 教程](https://grpc.io/docs/languages/java/)

← [返回 RPC 总览](./README.md)