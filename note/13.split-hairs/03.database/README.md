<!--
module:
  parent: split-hairs
  slug: 03.database
  type: article
  category: 高频面试题
  summary: 数据库高频面试题与细节深挖（MySQL / Redis / NoSQL）
question:
  id: 03.database-03.database
  topic: 03.database
  difficulty: ⭐⭐
  frequency: 高频
  scenario_type: 性能对比
  tags: [03.database]
-->

# 数据库咬文嚼字

> 数据库高频面试题与细节深挖，对齐主模块 [`03.database`](../../03.database/)。聚焦 MySQL（索引 / 锁 / 事务 / MVCC / JOIN）、Redis（持久化 / 淘汰 / 集群 / 大 Key）、NoSQL 三大方向的 22 个高频陷阱。

---

## 文章清单（共 22 篇）

### MySQL 关系型数据库
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](relational-database/mysql/count/) | ⭐⭐ | 性能差异？最佳实践？ |
| [INT(4) 的含义](relational-database/mysql/int(4)-define/README.md) | ⭐⭐ | 括号里的数字是长度还是显示宽度？ |
| [事务隔离级别](relational-database/mysql/isolation/) | ⭐⭐⭐⭐ | RU / RC / RR / Serializable 详解 |
| [快速加索引](relational-database/mysql/quickly-add-index/) | ⭐⭐⭐ | 大表在线加索引的方案 |
| [时间类型选择](relational-database/mysql/time-types/) | ⭐⭐ | DATETIME / TIMESTAMP / DATE 选型 |
| [SQL 调优](relational-database/mysql/tuning/) | ⭐⭐⭐⭐ | Explain 分析 + 索引优化 |
| [什么情况下会锁表](relational-database/mysql/what-lock/) | ⭐⭐⭐⭐ | 行锁 / 表锁 / 间隙锁 |
| [SELECT * 查 2000 万行会炸内存吗](relational-database/mysql/select-all-big-table/README.md) | ⭐⭐⭐⭐ | JDBC 默认一次性 fetch all + 流式读取姿势 |
| [深分页 LIMIT 10000000,10 为什么慢](relational-database/mysql/deep-pagination/README.md) | ⭐⭐⭐⭐ | OFFSET 工作机制 + 主键范围分页 + 延迟关联 |
| [批量插入 batch 性能对比](relational-database/mysql/batch-operation/README.md) | ⭐⭐⭐⭐ | JDBC batch + rewriteBatchedStatements + LOAD DATA |
| [大事务的危害与拆分](relational-database/mysql/large-transaction/README.md) | ⭐⭐⭐⭐ | 5 大危害（锁/Undo/binlog/连接池/MVCC） + 拆分策略 |
| [索引失效的 10 种场景](mysql/index-failure/) | ⭐⭐⭐⭐⭐ | LIKE 左通配 / 函数 / 类型转换 / OR / 最左前缀 |

### MySQL 深入
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [MVCC 实现原理](mvcc/) | ⭐⭐⭐⭐⭐ | Read View + Undo Log |
| [B+ Tree 为什么适合数据库索引](bplus-tree/) | ⭐⭐⭐⭐⭐ | vs B-Tree / Hash |
| [MySQL 主从复制延迟](replication-lag/) | ⭐⭐⭐⭐ | 延迟原因与解决方案 |
| [MySQL JOIN 算法](mysql-join/) | ⭐⭐⭐⭐ | NLJ / BNL / Hash Join |

### Redis NoSQL
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Redis 搜索能力](nosql/key-value/redis/search/) | ⭐⭐⭐ | Redis 如何做全文搜索？ |
| [缓存穿透 / 击穿 / 雪崩](redis/cache-penetration-breakdown-avalanche/) | ⭐⭐⭐⭐⭐ | 面试必考三件套 |

### Redis 深入
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Redis 持久化](redis-persistence/) | ⭐⭐⭐⭐ | RDB / AOF / 混合持久化 |
| [Redis 内存淘汰策略](redis-eviction/) | ⭐⭐⭐⭐ | 8 种淘汰策略详解 |
| [Redis 集群](redis-cluster/) | ⭐⭐⭐⭐ | Sentinel vs Cluster |
| [Redis 大 Key 问题](redis-big-key/) | ⭐⭐⭐⭐ | 发现与治理方案 |

---

## 学习路径

1. **入门**（3 天）：COUNT 区别 + INT(4) + 时间类型
2. **进阶**（1 周）：索引 + 锁 + 事务隔离
3. **冲刺面试**：重点看"索引失效"、"缓存三件套"、"MVCC"、"B+ Tree"、"SELECT * 内存陷阱"、"深分页"、"批量插入"、"大事务"

## 相关章节

- 主模块：[`note/03.database`](../../03.database/) — 数据库知识体系
- 相关章节：[`04.system-design`](../04.system-design/)（高性能设计）

← [返回咬文嚼字（高频面试题）](../README.md)
