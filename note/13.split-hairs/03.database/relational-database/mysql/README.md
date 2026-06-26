# MySQL 细节 — 咬文嚼字

> MySQL 面试高频细节，每篇聚焦一个"看起来简单但陷阱不少"的问题。

## 文章清单（7 篇）

| 主题 | 核心问题 | 入口 |
|------|---------|------|
| [事务隔离机制](isolation/README.md) | RU / RC / RR / Serializable | ⭐⭐⭐⭐ |
| [INT(4) 的含义](int(4)-define/README.md) | 显示宽度 vs 存储范围 | ⭐⭐ |
| [快速加索引](quickly-add-index/README.md) | 大表在线加索引 | ⭐⭐⭐ |
| [时间类型选择](time-types/README.md) | DATETIME / TIMESTAMP / DATE | ⭐⭐ |
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](count/README.md) | 性能差异与最佳实践 | ⭐⭐ |
| [SQL 调优](tuning/README.md) | Explain + 索引优化 | ⭐⭐⭐⭐ |
| [什么情况下会锁表](what-lock/README.md) | 行锁 / 表锁 / 间隙锁 | ⭐⭐⭐⭐ |

## 相关章节

- 返回：[`关系型数据库`](../README.md) → [`03.database 总览`](../../README.md)
- 主模块：[`03.database/05-mysql`](../../../../03.database/05-mysql/README.md) — MySQL 深度解析
- 索引专题：[`03.database/04-index`](../../../../03.database/04-index/README.md) — 索引原理与优化
