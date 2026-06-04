# 高性能篇

> 高性能(High Performance)指系统在资源有限的情况下，仍能处理尽可能多的请求。本模块涵盖缓存、数据库优化、消息队列等关键主题。

## 流量与分发

1. [负载均衡](load-balance/README.md) — 四层/七层负载均衡、轮询/哈希/最少连接算法
2. [CDN 加速](cdn/README.md) — 静态资源分发与边缘计算

## 数据库优化

3. [SQL 优化](database-optimization/sql/README.md) — 索引优化、执行计划、慢查询
4. [读写分离](database-optimization/read-write-splitting/README.md) — 主从复制与代理模式
5. [分库分表](database-optimization/db-sharding/README.md) — [ShardingSphere](database-optimization/db-sharding/sharding-sphere/README.md)
6. [冷热数据分离](database-optimization/cold-hot-data-separation/README.md) — 数据分层存储

## 缓存与消息

7. [缓存设计模式](cache-patterns/README.md) — Cache-Aside/Read-Through/Write-Through/Write-Behind 🆕
8. [消息队列](mq/README.md) — ActiveMQ/RabbitMQ/RocketMQ/Kafka/Pulsar 对比

## 运行时优化

9. [Java 性能优化](java/README.md) — JVM 调优与代码级优化
10. [连接池优化](connection-pool/README.md) — HikariCP/连接池参数调优 🆕
11. [序列化优化](serialization/README.md) — Protobuf/Kryo/Hessian 对比 🆕
