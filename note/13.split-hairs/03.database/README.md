# 数据库咬文嚼字

> 数据库高频面试题与细节深挖，对齐主模块 [`03.database`](../../03.database/)

---

## 文章清单

### MySQL 关系型数据库
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](relational-database/mysql/count/) | ⭐⭐ | 性能差异？最佳实践？ |
| [INT(4) 的含义](relational-database/mysql/int\(4\)-define/) | ⭐⭐ | 括号里的数字是长度还是显示宽度？ |
| [事务隔离级别](relational-database/mysql/isolation/) | ⭐⭐⭐⭐ | RU / RC / RR / Serializable 详解 |
| [快速加索引](relational-database/mysql/quickly-add-index/) | ⭐⭐⭐ | 大表在线加索引的方案 |
| [时间类型选择](relational-database/mysql/time-types/) | ⭐⭐ | DATETIME / TIMESTAMP / DATE 选型 |
| [SQL 调优](relational-database/mysql/tuning/) | ⭐⭐⭐⭐ | Explain 分析 + 索引优化 |
| [什么情况下会锁表](relational-database/mysql/what-lock/) | ⭐⭐⭐⭐ | 行锁 / 表锁 / 间隙锁 |
| [索引失效的 10 种场景](mysql/index-failure/) | ⭐⭐⭐⭐⭐ | LIKE 左通配 / 函数 / 类型转换 / OR / 最左前缀 |

### Redis NoSQL
| 主题 | 难度 | 核心问题 |
|------|------|---------|
| [Redis 搜索能力](nosql/key-value/redis/search/) | ⭐⭐⭐ | Redis 如何做全文搜索？ |
| [缓存穿透 / 击穿 / 雪崩](redis/cache-penetration-breakdown-avalanche/) | ⭐⭐⭐⭐⭐ | 面试必考三件套 |

---

## 待补充的高频面试题

### MySQL 相关（强烈建议补齐）
- **索引失效的 10 种场景**（LIKE 左通配、函数、类型转换...）
- **B+ Tree 为什么适合数据库索引**（vs B-Tree / Hash）
- **MVCC 实现原理**（Read View + Undo Log）
- **JOIN 算法**（NLJ / BNL / Hash Join）
- **SQL 注入原理与防御**（PreparedStatement）
- **主从复制延迟怎么处理**
- **分库分表策略**（ShardingSphere）

### Redis 相关（强烈建议补齐）
- **缓存穿透 / 击穿 / 雪崩**（必考三件套）
- **Redis 持久化对比**（RDB vs AOF vs 混合）
- **Redis 内存淘汰策略**（8 种策略）
- **Redis 集群方案**（Sentinel vs Cluster）
- **Redis 与数据库双写一致性**
- **Redis 大 Key 问题**

---

## 学习路径

1. **入门**（3 天）：COUNT 区别 + INT(4) + 时间类型
2. **进阶**（1 周）：索引 + 锁 + 事务隔离
3. **冲刺面试**：重点看"索引失效"、"缓存三件套"、"MVCC"（待补）

## 交叉引用

- 主模块：[`note/03.database`](../../03.database/) — 数据库知识体系
- 相关章节：[`04.system-design`](../04.system-design/)（高性能设计）
