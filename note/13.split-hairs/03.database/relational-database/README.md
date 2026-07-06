<!--
question:
  id: 03.database-relational-database
  topic: 03.database
  difficulty: ⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [03.database, relational, database]
-->

# 关系型数据库 — 咬文嚼字

> 关系型数据库细节深挖，聚焦面试中那些"以为懂但说不清"的问题。
>
> 关系型数据库（RDBMS）以行（Row）和列（Column）的二维表组织数据，通过 SQL 进行查询，依靠事务（Transaction）保证 ACID。但"会写 SQL" 与"懂 RDBMS"之间，隔着索引原理、事务隔离、锁机制、MVCC、查询优化器等大量深水区。本板块聚焦 MySQL 这个面试出场率最高的 RDBMS。

---

## 文章导航

| 分类 | 核心话题 | 入口 |
|------|---------|------|
| **MySQL** | 7 篇深度文章 | [mysql/](mysql/README.md) |

### MySQL 文章清单

| 主题 | 核心问题 | 难度 |
|------|---------|:----:|
| [COUNT(*) vs COUNT(1) vs COUNT(字段)](mysql/count/README.md) | 性能差异与最佳实践 | ⭐⭐ |
| [INT(4) 的含义](mysql/int(4)-define/README.md) | 显示宽度 vs 存储范围 | ⭐⭐ |
| [事务隔离级别](mysql/isolation/README.md) | RU / RC / RR / Serializable 详解 | ⭐⭐⭐⭐ |
| [快速加索引](mysql/quickly-add-index/README.md) | 大表在线加索引的方案 | ⭐⭐⭐ |
| [时间类型选择](mysql/time-types/README.md) | DATETIME / TIMESTAMP / DATE | ⭐⭐ |
| [SQL 调优](mysql/tuning/README.md) | Explain + 索引优化 | ⭐⭐⭐⭐ |
| [什么情况下会锁表](mysql/what-lock/README.md) | 行锁 / 表锁 / 间隙锁 | ⭐⭐⭐⭐ |

### 其他深入文章

| 主题 | 核心问题 | 难度 |
|------|---------|:----:|
| [MVCC 实现原理](../mvcc/README.md) | Read View + Undo Log | ⭐⭐⭐⭐⭐ |
| [B+ Tree 为什么适合数据库索引](../bplus-tree/README.md) | vs B-Tree / Hash | ⭐⭐⭐⭐⭐ |
| [MySQL 主从复制延迟](../replication-lag/README.md) | 延迟原因与解决方案 | ⭐⭐⭐⭐ |
| [MySQL JOIN 算法](../mysql-join/README.md) | NLJ / BNL / Hash Join | ⭐⭐⭐⭐ |

---

## RDBMS 核心概念速查

```
关系型数据库
├── 存储引擎
│   ├── InnoDB     ← MySQL 默认，支持事务、行锁、外键
│   ├── MyISAM     ← 不支持事务，全文索引（MySQL 5.5 前默认）
│   └── 其他       ← PostgreSQL、Oracle、SQL Server
├── 索引
│   ├── B+ Tree    ← 最常用，聚簇 / 非聚簇
│   ├── Hash       ← 等值查询 O(1)，不支持范围
│   ├── Full-Text  ← 全文检索
│   └── 空间索引   ← GIS
├── 事务
│   ├── ACID       ← 原子性、一致性、隔离性、持久性
│   └── 隔离级别   ← RU / RC / RR / Serializable
├── 锁
│   ├── 粒度       ← 表锁 / 行锁 / 间隙锁 / 临键锁
│   └── 模式       ← 共享锁（S）/ 排他锁（X）/ 意向锁（IS/IX）
└── MVCC
    └── Read View + Undo Log → 实现 RC / RR 隔离级别
```

## 相关章节

- 返回：[`03.database 总览`](../README.md)
- 主模块：[`03.database`](../../../03.database/README.md) — 数据库知识体系
- 咬文嚼字：[`NoSQL`](../nosql/README.md) — 非关系型数据库细节

← [返回: 咬文嚼字 · relational-database](README.md)
