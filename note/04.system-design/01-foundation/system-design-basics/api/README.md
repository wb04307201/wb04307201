# API 设计

> API 是系统对外交互的接口，良好的 API 设计直接影响系统的可用性和可维护性。

## 设计方式对比

| 特性 | RESTful | GraphQL | RPC |
|------|---------|---------|-----|
| 协议 | HTTP | HTTP | 多种(HTTP/2, TCP) |
| 数据格式 | JSON/XML | JSON | Protobuf/Thrift |
| 资源模型 | 资源导向 | 查询导向 | 方法导向 |
| 性能 | 中等 | 灵活(按需) | 高(二进制) |
| 适用场景 | 公开 API | 前端数据聚合 | 内部服务调用 |

## 子章节

- [RESTful API](rest/README.md) — 资源建模、HTTP 方法、状态码、版本控制
- [GraphQL](graphql/README.md) — Schema、Query/Mutation、Resolver
- [RPC API](rpc/README.md) — gRPC、Protobuf、服务存根
