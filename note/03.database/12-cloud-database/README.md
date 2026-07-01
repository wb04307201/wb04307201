<!--
module:
  parent: database
  slug: database/cloud-database
  type: index
  category: 主模块子文章
  summary: 云数据库是云厂商提供的托管关系/NoSQL/NewSQL 服务,主流产品包括 AWS RDS/Aurora、阿里云 RDS/PolarDB、TiDB Cloud,核心价值是免运维与弹性扩缩容。
-->

# 云数据库

> 云数据库(Cloud Database)是云厂商提供的关系型、NoSQL、NewSQL 等托管服务,具备自动备份、容灾、监控、扩缩容等开箱即用能力;主流产品包括 AWS RDS/Aurora、阿里云 RDS/PolarDB、Azure Database、Google Cloud SQL、TiDB Cloud 等。

> 最后更新: 2026-07-01

---

## 📚 核心内容

| 主题 | 内容 | 关键点 |
|------|------|--------|
| 一、云数据库的价值与挑战 | 6 大价值 vs 5 大挑战 | 免运维 vs 厂商锁定 |
| 二、AWS RDS 与 Aurora | 6 大引擎 + 实例规格 + Aurora 6 副本 3 AZ | Aurora 性能 5x RDS |
| 三、阿里云 RDS 与 PolarDB | 5 大引擎 + 存储计算分离 + RDMA | 5 分钟内新增只读节点 |
| 四、Azure SQL 与 Google Cloud SQL | Azure 3 模式 + GCP Spanner 99.999% SLA | Spanner 适合全球金融 |
| 五、TiDB Cloud(NewSQL) | 兼容 MySQL + HTAP + 多云 | 100K+ QPS / 节点 |
| 六、托管 Redis 与 MongoDB | ElastiCache / Tair / DocumentDB / Atlas | MemoryDB 强一致 |
| 七、自建 vs 云数据库决策 | 8 维度决策矩阵 | 核心库自建 + 周边上云 |
| 八、迁移与最佳实践 | 4 策略 + 5 安全措施 + 6 上云坑 | 优先标准 SQL 避免锁定 |

---

## 一、云数据库的价值与挑战

### 1. 核心价值

| 价值 | 描述 |
|------|------|
| **免运维** | 自动备份、自动 failover、补丁升级 |
| **弹性扩缩容** | 一键升级实例规格、只读副本横向扩展 |
| **高可用** | 同城多 AZ、跨地域灾备 |
| **安全合规** | VPC 隔离、KMS 加密、审计日志 |
| **监控告警** | 内置 CloudWatch(云监控)对接 |
| **节省成本** | 按需付费、预留实例优惠 |

### 2. 主要挑战

| 挑战 | 说明 |
|------|------|
| **厂商锁定** | 数据库内核定制化,迁移成本高 |
| **成本不可控** | 大规模场景下单价可能高于自建 |
| **性能黑盒** | 共享底层资源,极端场景下有性能波动 |
| **网络依赖** | 与应用同 Region 部署,跨 Region 延迟 |
| **功能受限** | 部分高级特性(自定义插件)不支持 |

---

## 二、AWS RDS 与 Aurora

### 1. AWS RDS(Relational Database Service)

AWS 托管的关系型数据库服务,支持多种引擎。

| 引擎 | 版本 | 适用 |
|------|------|------|
| MySQL | 5.7 / 8.0 | 通用 OLTP |
| PostgreSQL | 14 / 15 / 16 | 复杂查询、GIS、JSON |
| MariaDB | 10.6 / 11.4 | MySQL 兼容 |
| Oracle | 19c | 企业级传统 |
| SQL Server | 2017 / 2019 / 2022 | .NET 生态 |
| Db2 | 11.5 | 大型机场景 |

#### 实例规格

| 类型 | 适用 |
|------|------|
| `db.t3.micro` ~ `db.t3.2xlarge` | 突发型,小型应用 |
| `db.m5.large` ~ `db.m5.24xlarge` | 通用型,中大型 |
| `db.r5.large` ~ `db.r5.24xlarge` | 内存优化,大数据 |
| `db.x2iedn` | 内存密集(4TB RAM) |

#### 关键特性

- **Multi-AZ 部署**:主备跨可用区,自动故障转移(60-120s)
- **只读副本(Read Replica)**:最多 5 个,跨 Region 复制
- **自动备份**:保留 1-35 天,Point-in-Time Recovery
- **加密**:KMS 静态加密 + TLS 传输加密
- **Performance Insights**:SQL 性能分析工具

#### 典型架构

```
应用层
  ↓
RDS Proxy(连接池,减少连接数)
  ↓
Primary(写)  ── 同步复制 ──  Standby(多 AZ 灾备)
  ↓ 异步复制
Read Replica 1(读,同 Region)
Read Replica 2(读,跨 Region)
```

### 2. AWS Aurora

Aurora 是 AWS 自研的**云原生关系型数据库**,兼容 MySQL/PostgreSQL 协议,性能是 RDS 的 5 倍。

#### 核心架构

```
         应用层
            ↓
       Aurora Endpoint
            ↓
┌───────────────────────────────────┐
│        共享存储层(集群)            │
│   6 副本跨 3 AZ,Quorum 写入       │
│   存储自动扩容 128TB              │
└───────────────┬───────────────────┘
                │
   ┌────────────┼────────────┐
   ↓            ↓            ↓
Writer        Reader 1     Reader 2
(主写)        (只读)       (只读)
```

#### 关键创新

| 特性 | 价值 |
|------|------|
| **存储自动扩容** | 10GB 起,按需扩到 128TB,无需预估 |
| **6 副本 / 3 AZ** | 单 AZ 故障不影响可用性 |
| **15 个只读副本** | 远多于 RDS 5 个 |
| **毫秒级复制延迟** | Reader 几乎实时同步 |
| **Aurora Serverless** | 按秒计费,无服务器模式(适合低频场景) |
| **Aurora Global Database** | 跨 Region 灾难恢复(1s RPO) |
| **Aurora MySQL Backtrack** | 72 小时内可"回退"数据库状态(⚠️ 2023 年起已 deprecated,推荐使用 PITR) |

#### 适用场景

- 对性能、可用性、扩展性要求极高的 OLTP
- SaaS 应用(多租户,需要强隔离)
- 全球部署(Global Database)

#### 价格

Aurora 价格约为 RDS 的 **1.5-2 倍**,但提供更优性能与可用性。

---

## 三、阿里云 RDS 与 PolarDB

### 1. 阿里云 RDS

覆盖 MySQL、PostgreSQL、SQL Server、MariaDB、Oracle 五大引擎。

| 引擎 | 特点 |
|------|------|
| **RDS MySQL** | 兼容 5.7 / 8.0,**国内市场份额第一** |
| **RDS PostgreSQL** | 兼容 14 / 15,GIS、JSONB 强 |
| **PolarDB** | 阿里自研,100% 兼容 MySQL / PostgreSQL / Oracle,性能 6 倍于 MySQL |
| **PolarDB-X(原 DRDS)** | 分布式版,水平扩展 |

### 2. PolarDB 架构(创新点)

PolarDB 采用**存储计算分离 + RDMA 网络**:

```
应用层
  ↓
PolarProxy(代理,自动读写分离)
  ↓
Writer Node    Reader Node 1   Reader Node 2
   ↓              ↑               ↑
   └──→ PolarStore(共享分布式存储,RDMA) ───┘
        3 副本 + 高速网络
        单实例最大 100TB
```

#### 三大优势

1. **读写分离透明化**:PolarProxy 自动识别 SQL,只读走 Reader,无需业务改代码
2. **快速增减只读节点**:5 分钟内新增 1 个只读节点(Aurora 需 5-10 分钟)
3. **存储计算分离**:计算节点无状态,故障秒级切换

#### 版本选择

| 版本 | 兼容 | 适用 |
|------|------|------|
| **PolarDB MySQL** | MySQL 5.6 / 5.7 / 8.0 | MySQL 业务 |
| **PolarDB PostgreSQL** | PostgreSQL 11 / 14 | PG 业务 |
| **PolarDB Oracle 兼容** | Oracle 语法 | Oracle 去 O |
| **PolarDB-X** | MySQL + 分布式 | 100TB+ 大数据 |

### 3. 关键能力

- **同城双活**:RDS 同 Region 多 AZ 部署
- **跨地域灾备**:异地灾备实例(异步复制,RPO 分钟级)
- **数据加密**:KMS 透明加密
- **审计日志**:SQL 审计、合规分析
- **自治服务**:自动诊断、性能调优、容量预测

---

## 四、Azure SQL 与 Google Cloud SQL

### 1. Azure SQL 系列

| 产品 | 说明 |
|------|------|
| **Azure SQL Database** | 全托管 PaaS,自动扩缩容 |
| **Azure SQL Managed Instance** | 接近 SQL Server 体验,迁移友好 |
| **SQL Server on Azure VMs** | IaaS,自管 SQL Server |

#### Azure SQL Database 亮点

- **无服务器(Serverless)** 模式:按秒计费,自动暂停
- **Hyperscale 服务层级**:支持 100TB 单库,快速 scale up
- **内置 AI**:自动调优(Query Performance Insight)
- **Always Encrypted**:数据加密(密钥永不离开应用)

### 2. Google Cloud SQL

| 引擎 | 特点 |
|------|------|
| MySQL | 5.7 / 8.0 |
| PostgreSQL | 14 / 15 |
| SQL Server | 2017 / 2019 |

#### 优势

- 与 BigQuery、Firestore 等 GCP 服务深度集成
- Cloud SQL Auth Proxy 简化安全连接
- 自动化运维(备份、patch、HA)

#### Cloud Spanner(全球分布式 SQL)

- 全球强一致(外部一致性,基于 TrueTime API)
- 水平扩展到数 PB
- 99.999% SLA
- 适合全球部署的金融、游戏、零售场景
- 价格:~$9/小时起,适合预算充裕的大型企业

---

## 五、TiDB Cloud(NewSQL)

TiDB Cloud 是 PingCAP 提供的**云原生 NewSQL 数据库**,100% 兼容 MySQL 协议。

### 1. 核心能力

| 能力 | 说明 |
|------|------|
| **水平扩展** | 透明分片,数据量增长无感知 |
| **强一致事务** | 分布式 ACID,Raft 共识 |
| **HTAP** | 同时支持 OLTP(行存 TiKV) + OLAP(列存 TiFlash) |
| **MySQL 兼容** | 业务代码无需改 |
| **多云** | AWS / GCP / 阿里云 部署 |

### 2. 部署模式

| 模式 | 说明 |
|------|------|
| **Serverless** | 按需计费,自动扩缩,开发/中小规模 |
| **Dedicated** | 专用集群,生产环境 |
| **Self-Hosted** | 私有化部署(Enterprise) |

### 3. 典型场景

- MySQL 单库容量达到 5TB+,需水平扩展
- 强一致事务 + 海量并发
- 实时 HTAP(交易 + 报表同一系统)

### 4. 性能指标

- 写入 100K+ QPS / 节点
- 延迟 P99 < 10ms
- 延迟敏感业务:金融支付、库存、订单

---

## 六、托管 Redis 与 MongoDB

### 1. 托管 Redis(ElastiCache / 阿里云 Redis / MemoryDB)

| 厂商 | 产品 | 特点 |
|------|------|------|
| AWS | ElastiCache for Redis | 兼容 Redis 7 |
| AWS | MemoryDB for Redis | **强一致** + Redis 兼容 |
| 阿里云 | 云数据库 Redis / Tair | Tair 兼容 Redis + 持久内存版 |
| 阿里云 | 阿里云 KVStore for Redis | 企业级 |
| Azure | Cache for Redis | 企业版支持多可用区 |
| Google | Memorystore | 基础版 + 标准版 |

### 2. 托管 MongoDB

| 厂商 | 产品 | 特点 |
|------|------|------|
| AWS | DocumentDB | 兼容 MongoDB 4.0/5.0 协议 |
| 阿里云 | 云数据库 MongoDB | 三节点副本集 / 分片集群 |
| Azure | Cosmos DB | 多模型 + 多 API + 全球分布 |
| Google | MongoDB Atlas(官方) | 全球部署,最完整 |

#### DocumentDB vs MongoDB Atlas

| 维度 | DocumentDB | Atlas |
|------|-----------|-------|
| MongoDB 兼容 | 4.0(部分特性) | 最新版本 |
| 性能 | 中等 | 高 |
| 全球分布 | ❌ 单 Region | ✅ 全球多 Region |
| 价格 | 中 | 较高 |
| 推荐 | AWS 生态 + 成本敏感 | 多云/全球部署 |

---

## 七、自建 vs 云数据库决策

### 1. 决策矩阵

| 维度 | 自建数据库 | 云数据库 |
|------|----------|---------|
| **初期成本** | 高(需采购服务器) | 低(按需付费) |
| **运维成本** | 高(需 DBA 团队) | 低(云厂商承担) |
| **弹性扩缩容** | 困难(采购周期) | 极快(分钟级) |
| **长期成本(大规模)** | 低 | 高(单价 × 时间) |
| **可控性** | 高 | 低(黑盒) |
| **合规/数据本地化** | 灵活 | 受限(看厂商合规) |
| **厂商锁定** | 无 | 高 |
| **适合阶段** | 中大型成熟期 | 创业期 / 中小型 / 业务波动大 |

### 2. 何时选自建

- 数据规模 > 50TB,云数据库成本无法承受
- 强合规(金融/政府)要求数据物理隔离
- 已有成熟 DBA 团队
- 需深度定制内核(插件、参数)

### 3. 何时选云数据库

- 创业期 / 快速迭代
- 业务波动大(电商大促、SaaS 周期性)
- 无专职 DBA 团队
- 多区域全球部署

### 4. 混合策略

**生产核心库自建 + 周边业务上云** 是大型企业的常见方案:

```
核心交易库(自建 IDC + 异地灾备)
    ↓ Canal/DTS 同步
周边系统(云上 RDS + 只读副本)
    - BI 报表
    - 测试环境
    - 灰度发布
```

---

## 八、迁移与最佳实践

### 1. 上云迁移策略

| 策略 | 说明 | 停机时间 |
|------|------|---------|
| **全量 + 增量** | 先全量同步,后增量追平 | 分钟级 |
| **双写切换** | 业务同时写新老库,稳定后切流量 | 0(灰度) |
| **逻辑复制** | MySQL Replication / PostgreSQL Streaming | 0(实时) |
| **DTS/DMS 商业工具** | 阿里云 DTS、AWS DMS | 0(实时) |

### 2. 成本优化

- **预留实例(RIs)**:1-3 年期优惠 30-60%
- **Savings Plans**(AWS):按用量承诺折扣
- **存储类型分级**:热数据用 SSD,冷数据归档到 OSS/S3
- **只读副本复用**:报表 / BI / ETL 走只读副本
- **弹性扩缩容**:夜间低谷降配(需应用支持)

### 3. 安全最佳实践

| 措施 | 说明 |
|------|------|
| **VPC 隔离** | 数据库仅在私有网络暴露 |
| **KMS 加密** | 静态数据加密,密钥托管 |
| **SSL/TLS** | 传输加密 |
| **最小权限** | 应用账号仅给 SELECT/INSERT/UPDATE,不用 root |
| **审计日志** | 记录所有 DDL/DML,合规分析 |
| **白名单** | 数据库访问限制 IP 段 |
| **敏感数据脱敏** | 手机号 / 身份证 / 邮箱 字段加密 |

### 4. 跨 Region 灾备架构

```
                   主 Region
                ┌──────────┐
                │ RDS 主库 │
                └─────┬────┘
                      │ 异步 Binlog 复制
                      ↓
                ┌──────────┐
                │ 异地灾备 │
                └──────────┘

   切换: 1. 提升灾备为主
        2. 修改应用连接
        3. 业务恢复
   RPO: 分钟级 / RTO: 5-10 分钟
```

### 5. 上云常见坑

| 坑 | 原因 | 避坑 |
|------|------|------|
| 性能不符预期 | 共享底层 + 网络跳数 | 选 Dedicated 实例 + 同 AZ 部署 |
| 成本失控 | 按需付费弹性高 + 监控不足 | 启用费用告警,设硬性预算 |
| 厂商锁定 | 使用厂商专有 API | 优先使用标准 SQL + 通用协议 |
| 备份恢复慢 | 大库 + 跨 Region | 本 Region 备份 + 定期恢复演练 |
| 安全组配置错 | 0.0.0.0/0 开放 | 严格白名单,内网访问 |
| 参数默认值差 | 云数据库默认参数偏保守 | 调优 `innodb_buffer_pool_size` 等 |

---

## 🔗 相关章节

- [MySQL](../05-mysql/README.md) — 自建 MySQL 参数与配置
- [NoSQL](../08-nosql/README.md) — 自建 NoSQL 选型
- [数据迁移与同步](../10-data-migration/README.md) — 上云迁移工具
- [数据库监控告警](../11-monitoring/README.md) — 云监控与自建监控
- [系统设计 · 高可用](../../04.system-design/03-high-availability/README.md) — 多 AZ、异地容灾

---

## 📊 本节统计

- **leaf README 数**：1（本文即为分类 leaf，单 README 长文聚合 8 主题）
- **本节主题数**：8（价值挑战、AWS RDS/Aurora、阿里云 RDS/PolarDB、Azure SQL/GCP、TiDB Cloud、托管 Redis/MongoDB、自建 vs 云、迁移实践）
- **frontmatter 状态**：✅ 已对齐 CONTRIBUTING §12 标准（summary ≤ 80 字 / type=index）
- **统计口径**：本目录无嵌套子目录，所有内容聚合在本 README；最后更新 2026-07-01

---

## 📖 参考资料

- [AWS RDS 官方文档](https://aws.amazon.com/rds/)
- [AWS Aurora 官方文档](https://aws.amazon.com/rds/aurora/)
- [阿里云 RDS 官方文档](https://www.aliyun.com/product/rds)
- [阿里云 PolarDB 官方文档](https://www.aliyun.com/product/polardb)
- [TiDB Cloud 官方文档](https://docs.pingcap.com/tidbcloud/)
- [Google Cloud Spanner 论文](https://research.google/pubs/spanner-globally-distributed-database/)
- [Aurora 论文: The Tail at Store](https://www.allthingsdistributed.com/files/p1041-verbitski.pdf)
- [Azure SQL Database 文档](https://learn.microsoft.com/en-us/azure/azure-sql/)

---

← [返回 03.database 主模块](../README.md)