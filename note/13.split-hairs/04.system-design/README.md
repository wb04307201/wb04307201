<!--
module:
  parent: split-hairs
  slug: 04.system-design
  type: article
  category: 高频面试题
  summary: 系统设计高频面试题与难点深挖（MQ / 缓存 / 分布式 / 限流 / 幂等）
question:
  id: 04.system-design-04.system-design
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构困境
  tags: [04.system-design, design]
-->

# 系统设计咬文嚼字

> 系统设计高频面试题与难点深挖，对齐主模块 [`04.system-design`](../../04.system-design/)。**19** 篇真题覆盖 MQ / 缓存一致性 / 缓存热点 Key / 限流 / 秒杀 / 分布式 ID / 事务 / CAP / 锁 / 幂等 / 熔断 / **微服务 vs 单体** / **搜索系统** / **文件上传** / **短链系统** / **分库分表** / **排查与运维** 17 大方向（find 校对 2026-07-19）。

---

## 文章清单（共 19 题，find 校对 2026-07-19）

### 分布式
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [分布式 ID 生成方案](distributed-id/) | ⭐⭐⭐⭐ | UUID / 数据库 / 雪花算法 / Leaf |
| [分布式事务](distributed-transaction/) | ⭐⭐⭐⭐⭐ | 2PC / TCC / Saga / 本地消息表 |
| [CAP 定理实际应用](cap-theorem/) | ⭐⭐⭐⭐ | CP vs AP 选型决策 |
| [分布式锁](distributed-lock/) | ⭐⭐⭐⭐⭐ | Redis SETNX / Redisson / ZooKeeper |

### 高性能
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [缓存与数据库双写一致性](cache-consistency/) | ⭐⭐⭐⭐⭐ | 延迟双删 vs 监听 binlog |
| [缓存热点 Key 问题](cache-hot-key/) | ⭐⭐⭐⭐ | 本地缓存 + 分布式锁 + Key 拆分 + 热点探测 |
| [限流算法](rate-limiting/) | ⭐⭐⭐⭐ | 计数器 / 滑动窗口 / 漏桶 / 令牌桶 |
| [无 Redis 秒杀](seckill-without-redis/) | ⭐⭐⭐⭐ | 主流方案被禁用时的单机秒杀策略 |
| [商品搜索系统设计](product-search/) | ⭐⭐⭐⭐ | 倒排索引 + BM25 + 多阶段排序 + 数据同步一致性 |
| [大文件上传系统](file-upload/) | ⭐⭐⭐⭐ | 分片 + 断点续传 + 秒传 + 对象存储 |

### 消息队列
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [MQ 消息积压](mq-backlog/) | ⭐⭐⭐⭐ | 原因分析 + 紧急止血 + 长期优化 |
| [为什么还要 RocketMQ](still-need-rocketmq/) | ⭐⭐⭐ | Kafka vs RocketMQ vs RabbitMQ 选型 |

### 高并发与架构
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [幂等性设计 6 大方案](idempotency/) | ⭐⭐⭐⭐⭐ | Token / 状态机 / 唯一索引 / 去重表 |
| [熔断降级实战](circuit-breaker/) | ⭐⭐⭐⭐ | Sentinel / Resilience4j 落地 |
| [微服务 vs 单体](microservices-vs-monolith/) | ⭐⭐⭐⭐⭐ | 6 大核心优势 + 6 大反模式 + Spring Cloud 全套 + 何时该拆决策 |
| [短链系统设计](url-shortener/) | ⭐⭐⭐⭐ | Base62 + 发号器 + 302 重定向 + 缓存 + 统计 |
| [多租户 SaaS 系统设计](multi-tenant-saas/) | ⭐⭐⭐⭐⭐ | 6 大隔离模型 + 4 大应用层关注点 + 5 反模式 + PostgreSQL RLS + noisy neighbor 防御 |

### 数据库扩展
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [分库分表策略](sharding-strategy/) | ⭐⭐⭐⭐⭐ | 垂直拆分 / 水平分片 / ShardingSphere / 跨库查询 / 数据迁移 |

### 排查与运维
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [支付消息丢失排查](payment-message-lost/) | ⭐⭐⭐⭐ | 全链路 5 段排查 + 6 种根因 + 短期止血 + 长期方案 |

### 项目管理（已全部迁走，split-hairs 不再收此分类）

> 2026-06-30 路径整理：本类目的 3 题已**全部迁移**：
> - `app-quote-breakdown` / `outsourcing-pitfalls` → 新主模块 [`note/14.project-management/`](../../14.project-management/README.md)
> - `mobile-tech-stack` → 主模块 [`09.front-end/08-cross-platform/mobile-tech-stack/`](../../09.front-end/08-cross-platform/mobile-tech-stack/README.md)
>
> 本分类及其目录 `project-management/` 已删除，split-hairs 不再收"项目管理"类内容。

---

## 待补充的高频面试题

### 缓存
- **缓存穿透 / 击穿 / 雪崩**（三件套必问，已移至 [`03.database/cache-penetration-breakdown-avalanche`](../03.database/cache-penetration-breakdown-avalanche/README.md)）
- **缓存预热策略**

### 高并发
- **异步化方案**（CompletableFuture / 消息队列）

### 数据库扩展
- **读写分离方案**
- **数据迁移方案**

---

## 学习路径

1. **入门**（3 天）：MQ 积压处理 + 选型对比
2. **进阶**（2 周）：缓存一致性 + 限流算法 + 分布式 ID + 分布式锁 + 幂等性设计
3. **冲刺面试**：重点看"分布式事务"、"熔断降级"、"分布式锁"、"幂等性设计"

> 📌 **2026-06-30 路径整理**：原项目管理的 3 题全部迁走（"5万 vs 50万 App 报价"、"外包避坑指南"→ [`note/14.project-management/`](../../14.project-management/README.md)；"App 技术栈选型"→ [`09.front-end/08-cross-platform/mobile-tech-stack/`](../../09.front-end/08-cross-platform/mobile-tech-stack/README.md)）。split-hairs 不再收"项目管理"类内容。

## 相关章节

- 主模块：[`note/04.system-design`](../../04.system-design/) — 系统设计知识体系
- 相关章节：[`03.database`](../03.database/)（数据库细节）/ [`06.spring`](../06.spring/)（框架实现）/ 🆕 [`05.security`](../05.security)（SSO 单点登录）
- 待补充主题的深度阅读：
  - 缓存穿透/击穿/雪崩 → [`03.database/06-cache`](../../03.database/06-cache/README.md)
  - 分库分表 → [`03.database`](../../03.database/README.md) 数据迁移与同步
  - 异步化方案 → [`01.java/concurrency`](../../01.java/concurrency/README.md) CompletableFuture
  - 🆕 单点登录 SSO → [`05.security/sso`](../05.security/sso/README.md)（7 道精选 Q&A）

← [返回咬文嚼字（高频面试题）](../README.md)
