<!--
module:
  parent: spring
  slug: spring/mybatis-architecture
  type: index
  category: 主模块子文章
  summary: MyBatis 架构与原理
  depth: ⭐⭐
-->

# 01 MyBatis 架构与原理

## 🎯 一句话定位

**MyBatis 框架的架构与原理——框架本质、初始化流程、SQL 执行链路、核心组件、动态 SQL、关联映射、缓存机制、类关系图。这是阅读其他主题的预备知识。**

---
## 引言：01 MyBatis 架构与原理 的关键决策

本篇是「01 MyBatis 架构与原理」的核心章节，聚焦该主题在实际落地时**5 个 trade-off 的取舍与决策轴**。

## 章节导航

| 章节 | 标题 | 核心问题 | 阅读时长 | 难度 |
|------|------|---------|---------|------|
| [01](./01-framework-essence.md) | 框架本质与三层架构 | MyBatis 是什么、为什么用、怎么分层? | 5 min | ⭐ |
| [02](./02-initialization-flow.md) | 初始化流程 | SqlSessionFactory 是怎么构建出来的? | 8 min | ⭐⭐ |
| [03](./03-execution-flow.md) | 执行流程 | 一条 SQL 从接口调用到返回结果,经过了哪些步骤? | 10 min | ⭐⭐ |
| [04](./04-core-components.md) | 核心组件 | SqlSession/Executor/MappedStatement 各司何职? | 15 min | ⭐⭐⭐ |
| [05](./05-dynamic-sql.md) | 动态 SQL | if/where/foreach/choose 如何拼接条件? | 8 min | ⭐⭐ |
| [06](./06-result-mapping.md) | 关联映射 | 一对一、一对多怎么映射到对象? | 8 min | ⭐⭐ |
| [07](./07-cache-mechanism.md) | 缓存机制 | 一级/二级缓存怎么配合,如何防穿透? | 10 min | ⭐⭐⭐ |
| [08](./08-class-diagram.md) | 核心类关系图(附录) | 关键类的依赖关系长什么样? | 3 min | ⭐ |

---

## 知识地图

```mermaid
graph TD
    A[MyBatis 架构] --> B[框架本质]
    A --> C[工作流程]
    A --> D[核心组件]
    A --> E[高级特性]
    A --> F[附录]
    
    B --> B1[ORM 半自动]
    B --> B2[三层架构]
    
    C --> C1[初始化]
    C --> C2[执行流程]
    C2 --> C2a[8 个步骤]
    C2 --> C2b[架构图]
    
    D --> D1[SqlSessionFactory]
    D --> D2[Executor]
    D2 --> D2a[Simple]
    D2 --> D2b[Reuse]
    D2 --> D2c[Batch]
    D --> D3[MappedStatement]
    
    E --> E1[动态 SQL]
    E1 --> E1a[if/where]
    E1 --> E1b[foreach/choose]
    E --> E2[关联映射]
    E2 --> E2a[一对一]
    E2 --> E2b[一对多]
    E --> E3[缓存]
    E3 --> E3a[一级缓存]
    E3 --> E3b[二级缓存]
    E3 --> E3c[缓存穿透]
    
    F --> F1[核心类图]
```

---

## 核心概念速查表

| 概念 | 简述 | 详见 |
|------|------|------|
| SqlSessionFactory | 全局单例,线程安全,负责创建 SqlSession | [04 §3.1](./04-core-components.md#31-sqlsessionfactory) |
| SqlSession | 非线程安全,封装一次数据库会话 | [04 §3.1](./04-core-components.md#31-sqlsessionfactory) |
| Executor | 真正执行 SQL 的执行器,有三种子类型 | [04 §Executor 类型](./04-core-components.md#executor-类型详谈) |
| MappedStatement | SQL 映射信息的封装对象 | [04 §3.3](./04-core-components.md#33-mappedstatement) |
| Configuration | 全局配置对象,持有所有映射元数据 | [08](./08-class-diagram.md) |
| TypeHandler | 自定义类型与 JDBC 类型互转 | [02-extension:TypeHandler 与拦截器](../02-extension/README.md) |
| 缓存穿透 | 查询不存在的数据绕过缓存直击 DB | [07](./07-cache-mechanism.md) |

---

## 跨主题引用

- 扩展能力(TypeHandler / 拦截器 / 数据库厂商):[02-extension](../02-extension/README.md)
- 与 Spring 整合(SqlSessionFactoryBean / MapperScannerConfigurer / 事务管理):[03-spring-integration](../03-spring-integration/README.md)
- MyBatis-Plus 增强:[04-mybatis-plus](../04-mybatis-plus/README.md)

---

## 来源标注

| 章节 | 来源 |
|------|------|
| 01 框架本质与三层架构 | 原 08.mybatis/README.md § 一 |
| 02 初始化流程 | 原 08.mybatis/README.md § 二.2.1 |
| 03 执行流程 | 原 08.mybatis/README.md § 二.2.2 |
| 04 核心组件 | 原 § 三 + § 五.5.3 + § 九(去重合并) |
| 05 动态 SQL | 原 § 四.4.1 |
| 06 关联映射 | 原 § 四.4.2 |
| 07 缓存机制 | 原 § 四.4.3 + § 六.6.2 |
| 08 核心类关系图 | 原 附录 |

---


---

## 跨章节引用

- [01-assembly-and-startup](../03-spring-integration/01-assembly-and-startup.md) — Spring 整合时的启动流程
- [05-secondary-cache-integration](../03-spring-integration/05-secondary-cache-integration.md) — 二级缓存与 Spring 整合

---

## 🔗 兄弟主题

- **[02-extension](../02-extension/README.md)** — 扩展能力
- **[03-spring-integration](../03-spring-integration/README.md)** — Spring 整合
- **[04-mybatis-plus](../04-mybatis-plus/README.md)** — MyBatis-Plus

---

← [返回: MyBatis 架构与原理](README.md)
