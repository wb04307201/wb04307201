# 高性能篇

> 高性能(High Performance)指系统在资源有限的情况下，仍能处理尽可能多的请求。本模块涵盖缓存、数据库优化、消息队列等关键主题。
> 最后更新: 2026-06-09

## 流量与分发

1. [负载均衡](load-balance/README.md) — 四层/七层负载均衡、轮询/哈希/最少连接算法
2. [CDN 加速](cdn/README.md) — 静态资源分发与边缘计算

## 数据库优化

3. [数据库优化概览](database-optimization/README.md) — SQL 优化、读写分离、分库分表、冷热分离四大手段及优化顺序
4. [SQL 优化](database-optimization/sql/README.md) — 索引优化、执行计划、慢查询
5. [读写分离](database-optimization/read-write-splitting/README.md) — 主从复制与代理模式
6. [分库分表](database-optimization/db-sharding/README.md) — [ShardingSphere](database-optimization/db-sharding/sharding-sphere/README.md)
7. [冷热数据分离](database-optimization/cold-hot-data-separation/README.md) — 数据分层存储

## 缓存与消息

8. [缓存设计模式](cache-patterns/README.md) — Cache-Aside/Read-Through/Write-Through/Write-Behind 🆕
9. [消息队列](mq/README.md) — ActiveMQ/RabbitMQ/RocketMQ/Kafka/Pulsar 对比

## 运行时优化

10. [Java 性能优化](java/README.md) — JVM 调优与代码级优化
11. [连接池优化](connection-pool/README.md) — HikariCP/连接池参数调优 🆕
12. [序列化优化](serialization/README.md) — Protobuf/Kryo/Hessian 对比 🆕
