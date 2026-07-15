<!--
module:
  parent: system-design
  slug: system-design/multi-tenant-architecture
  type: article
  category: 主模块子文章
  summary: 多租户 SaaS 架构深度原理，6 大数据隔离模型 + 4 大应用层关注点 +
          5 大反模式 + PostgreSQL RLS + 飞书/钉钉/Salesforce/阿里云生产实践
-->

# 多租户 SaaS 架构 —— 从"6 大隔离模型"到生产级实现

> 一句话定位：**多租户的难点不在"隔离"，在"隔离强度 × 规模 × 成本"的三角权衡**。面试速查版见 [13.split-hairs · multi-tenant-saas](../../../../13.split-hairs/04.system-design/multi-tenant-saas/README.md)。

> **关联章节**：架构演进终局（[12.story · 19-saas-multitenant](../../../../12.story/18-saas-multitenant.md) — 阿明从单店到加盟帝国）、单租户决策 ([14.project-management/self-vs-saas-vs-outsourcing](../../../../14.project-management/self-vs-saas-vs-outsourcing/README.md))、架构演进整体路径 ([02-evolution](../../02-evolution/01-monolith-to-microservices/README.md))。

---

## 一、为什么需要多租户架构

### 1.1 商业驱动力（5 个推手）

```text
1. 复用基础设施：1 套代码服务 N 客户，边际成本趋零
2. 集中运维升级：1 次发布 = N 客户受益（vs N 次私有部署）
3. 数据驱动迭代：A/B 测试可跨租户观察，快速 PMF
4. 网络效应：客户在平台上互用（marketplace / 协作）
5. 计费灵活：按订阅 / 按用量 / 按席位定价
```

**反面**：单租户（私有部署）在某些场景反而更优 —— **小客户 < 50 / 高合规要求 / 客户要数据独占**。详见 [14.project-management · self-vs-saas-vs-outsourcing](../../../../14.project-management/self-vs-saas-vs-outsourcing/README.md)。

### 1.2 多租户的核心矛盾

```
共享基础设施（成本低）
       ↓
必须逻辑隔离（合规 + 安全）
       ↓
隔离越强 → 成本越高 → 失去 SaaS 优势
隔离越弱 → 风险越大 → 数据泄露/失控

→ 解法：在不同阶段选不同隔离强度
```

---

## 二、6 大数据隔离模型（核心章节）

### 2.1 模型 1：独立数据库（每租户一库）

```text
┌─────────────────────────────────────┐
│         Application Server          │
└──┬─────────┬─────────┬─────────┬────┘
   │         │         │         │
   ▼         ▼         ▼         ▼
DB_A        DB_B      DB_C      DB_D
(Tenant A)  (Tenant B)(Tenant C)(Tenant D)

配置：每租户独立 connection string
```

| 维度 | 评价 |
|------|------|
| 隔离强度 | ⭐⭐⭐⭐⭐（物理隔离 + 单独备份 / 恢复 / 审计）|
| 成本 | 高（连接池 × N / DBA × N 工作量 / 数据库 license × N）|
| 适合 | < 50 租户 / 高合规 / 大客户独立库 |
| 不适合 | 100+ 租户（运维爆炸）|

**典型案例**：阿里云给金融大客户的独立 VPC + 独立 DB。

### 2.2 模型 2：共享 DB + 独立 Schema

```text
┌─────────────────────────────────────┐
│         Application Server          │
└──┬─────────┬─────────┬─────────┬────┘
   │         │         │         │
   ▼         ▼         ▼         ▼
PG_DB (共享库)
├── schema_a (Tenant A)
├── schema_b (Tenant B)
├── schema_c (Tenant C)
└── schema_d (Tenant D)
```

| 维度 | 评价 |
|------|------|
| 隔离强度 | ⭐⭐⭐⭐（DDL 隔离 + 命名空间隔离）|
| 成本 | 中（共享连接池 / 共享 DB 升级）|
| 适合 | 50-500 租户 / 业务方有 schema 定制需求 |
| 不适合 | 超大规模（schema 数量过万）|

**典型案例**：早期 Salesforce（2000 年代初）；PostgreSQL 原生支持 schema 概念。

### 2.3 模型 3：共享 DB + 共享 Schema + tenant_id 列（**90% 起步选**）

```text
┌─────────────────────────────────────┐
│         Application Server          │
│  WHERE tenant_id = ?   ← 强制过滤   │
└──┬─────────┬─────────┬─────────┬────┘
   │         │         │         │
   └─────────┴─────────┴─────────┘
              │
              ▼
        documents (共享表)
   ┌─────────────────────────────────┐
   │ id │ tenant_id │ title │ ...   │
   ├─────────────────────────────────┤
   │ 1  │ A         │ foo   │       │
   │ 2  │ B         │ bar   │       │
   │ 3  │ A         │ baz   │       │
   └─────────────────────────────────┘
       INDEX (tenant_id, ...)
```

| 维度 | 评价 |
|------|------|
| 隔离强度 | ⭐⭐⭐（应用层强制 + 数据库兜底 [RLS]）|
| 成本 | 低（一套表 + 一套升级 + 一套连接池）|
| 适合 | **1000+ 租户的绝大多数场景** |
| 不适合 | 强合规 + 大客户差异化需求 |

**典型案例**：钉钉、Slack、Notion、GitHub、绝大多数 SaaS 起步选。

**为什么 90% 选这个**：
- 1 套表 + 1 套 schema，**业务迭代速度最快**
- 单租户分库（ShardingSphere / Vitess）可平滑从模型 3 升级
- RLS 让数据库兜底，避免"应用忘 WHERE"导致的数据泄露

### 2.4 模型 4：共享表 + 租户分区（PostgreSQL RLS）

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON documents
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- 应用层设置
SET app.current_tenant = '...';
```

**实现要点**：

| 关键环节 | 说明 |
|---------|------|
| **应用层注入** | 拦截器 / Middleware 中 `SET app.current_tenant = ?` |
| **物理模型** | 每张业务表 `tenant_id` 列 + 索引 `(tenant_id, ...)` |
| **DB 角色** | 应用账户无 BYPASSRLS，确保策略生效 |
| **运维绕过** | DBA 维护用 SUPERUSER（备份 / 迁移）|

详见 [PostgreSQL 官方 RLS 文档](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)。

### 2.5 模型 5：K8s Namespace 隔离（应用层 / 计算资源）

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-a
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-a-quota
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 32Gi
    persistentvolumeclaims: "20"
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: gateway
```

**适用**：计算资源隔离 + 网络隔离 + noisy neighbor 防御。

**典型案例**：阿里云 ACK 多租户、字节火山引擎。

### 2.6 模型 6：Serverless 多租户

```text
请求 → API Gateway → 冷启动 worker
                       ├─ Tenant A (warm)
                       ├─ Tenant B (cold)
                       └─ Tenant C (cold)
                          ↓ 闲置一段时间回收
```

| 维度 | 评价 |
|------|------|
| 隔离强度 | ⭐⭐（进程级 + 短生命周期）|
| 成本 | 极低（按请求计费）|
| 适合 | 边缘场景 / 中小租户 / 突发流量 |
| 不适合 | 长连接 / 大状态 / 严苛冷启动要求 |

**典型案例**：Vercel、Cloudflare Workers、AWS Lambda + API Gateway。

### 2.7 模型选择决策树

```
你的场景？
│
├─ < 50 租户 OR 合规要求强
│   └─ 模型 1（独立 DB）OR 模型 2（独立 Schema）
│
├─ 50-500 租户 + 中等合规
│   └─ 模型 2（独立 Schema）或 模型 3 + RLS
│
├─ 1000+ 租户（绝大多数 SaaS）
│   └─ 模型 3（共享 + tenant_id）← 起步
│       ├─ + RLS        → 模型 4
│       ├─ + K8s Namespace → 模型 5
│       └─ 大客户独立库 → 模型 1
│
└─ 边缘 / 突发流量场景
    └─ 模型 6（Serverless）混合使用
```

---

## 三、4 大应用层关注点

### 3.1 租户识别（Tenant Identification）

| 方式 | 实现 | 优缺点 |
|------|------|--------|
| **Subdomain** | `a.example.com` | 直观 / 自定义域名灵活，需 DNS 泛解析 |
| **JWT claim** | token.tenant_id | 无状态 / 跨服务传递，但 JWT 需旋转 |
| **Header** | `X-Tenant-Id` | 简单，但调试友好度低 |
| **Path** | `/api/v1/{tenant}/docs` | URL 直观但耦合业务 |

**最佳实践**：subdomain 做主识别 + JWT 做跨服务传递 + Header 做调试兜底。

### 3.2 租户上下文传递（Tenant Context Propagation）

| 场景 | 同步请求 | 异步任务 |
|------|---------|---------|
| **实现** | ThreadLocal / RequestScope | OpenTelemetry Baggage / Kafka Header |
| **陷阱** | 子线程丢上下文 | 跨服务调用丢上下文 |

```java
// OpenTelemetry Baggage 传递示例
Baggage.current()
  .toBuilder()
  .put("tenant.id", "tenant-a")
  .build()
  .makeCurrent();
```

### 3.3 租户级限流与配额

```java
// Sentinel 租户级限流
FlowRule rule = new FlowRule("listDocs")
  .setControlBehavior(RuleConstant.CONTROL_BEHAVIOR_RATE_LIMITER)
  .setCount(100);  // QPS
FlowRuleManager.loadRules(Collections.singletonList(rule));

// 进阶：动态规则，每个租户独立规则
SentinelApiClient.registerDynamicRule(...);
```

**3 层防御**：
1. **租户级限流**（Sentinel）→ 防止一个租户把整个应用的线程池耗尽
2. **资源配额**（K8s ResourceQuota）→ 防止一个租户把节点的 CPU / 内存吃光
3. **全局配额**（网关层令牌桶）→ 防止所有租户总流量超过容量

### 3.4 计费与计量（Metering）

```text
  业务事件 → Kafka → Flink 聚合 → ClickHouse 汇总
                                              ↓
                                       对账系统
                                              ↓
                                       计费 / 报表
```

**核心要点**：
- **埋点不可丢失**（业务事件 id 唯一去重）
- **跨服务一致性**（用 outbox 模式 / Saga）
- **租户级独立计量**（每租户每日 / 每 API 聚合）
- **定期对账**（防止计量漂移 → 收入流失）

---

## 四、5 大反模式（生产事故重灾区）

| # | 反模式 | 后果 | 防御 |
|---|--------|------|------|
| 1 | **忘写 WHERE tenant_id** | 数据跨租户泄露（重罪 / GDPR / 用户流失）| 中间件拦截器强制 + RLS 兜底 + 单元 / 集成测试覆盖 |
| 2 | **跨租户 JOIN** | 性能爆炸 + 合规风险 + 故障扩散 | 禁止跨租户 JOIN（约定 + Code Review + 静态扫描）|
| 3 | **noisy neighbor**（噪声邻居）| 大租户拖垮小租户 | 租户级限流 + K8s Namespace 隔离 + 监控告警 |
| 4 | **升级爆炸** | schema 升级要做 N 次 | 单库共享 + Liquibase/Flyway 集中 + 灰度发布 |
| 5 | **审计日志不分租户** | 合规追溯失败 + 调试困难 | 每个日志 / 审计事件打 `tenant_id` tag |

### 4.1 noisy neighbor 真实案例

```text
2024 Q4 某协作 SaaS：
- 某大租户批量导入 50 万员工 → 写入并发激增
- 整库写延迟从 5ms 涨到 800ms
- 所有租户的列表查询超时
- 9 点 CTO 被叫醒紧急止血

止血方案：
1. K8s Namespace 隔离（计算资源隔离）
2. 租户级限流（写入 QPS 限制）
3. 异步批量写入（削峰填谷）
4. 热数据 Redis 缓存（减少 DB 压力）
```

---

## 五、生产实践（3 大厂真实方案）

### 5.1 Salesforce

| 维度 | 方案 |
|------|------|
| 早期 | 独立 Schema（2000 年代）|
| 当下 | 大客户独立 DB + 中小客户共享 DB + Metadata 驱动 |
| 核心 | 元数据 + 平台层（APEX / Lightning Platform）支持租户定制 |

### 5.2 钉钉 / 飞书

| 维度 | 方案 |
|------|------|
| 数据隔离 | 共享 DB + tenant_id（绝大多数租户）+ 大客户独立 DB |
| 应用隔离 | K8s Namespace 计算资源隔离 |
| 限流 | Sentinel 租户级 + 网关全局两级 |
| 计费 | 用量埋点 → Kafka → ClickHouse 汇总 |
| noisy neighbor | 资源配额 + 熔断 + 降级 |

### 5.3 阿里云

| 维度 | 方案 |
|------|------|
| 控制面 | 共享（一次操作影响全租户）|
| 数据面 | 每租户独立 VPC + 独立 DB |
| 资源 | K8s Namespace + ResourceQuota + NetworkPolicy |
| 计费 | 用量明细 → 日志服务 → 计费引擎 |
| 合规 | 等保三级 / GDPR / HIPAA 必须独立 DB |

### 5.4 GitHub / GitLab

| 维度 | 方案 |
|------|------|
| 数据 | 共享 DB + tenant_id（GitHub）/ RLS（GitLab）|
| 隔离 | RLS + 中间件强制 WHERE |
| 计费 | 按席位 + 按 LFS 流量 |

---

## 六、面试题与陷阱表

详见 [13.split-hairs · multi-tenant-saas](../../../../13.split-hairs/04.system-design/multi-tenant-saas/README.md)（面试速查版）。

核心考点：
1. 6 大隔离模型选型
2. 4 大应用层关注点（识别 / 上下文 / 限流 / 计费）
3. 5 大反模式（忘 WHERE / 跨 JOIN / noisy neighbor / 升级爆炸 / 审计不分租户）
4. PostgreSQL RLS 实操
5. noisy neighbor 防御（K8s + Sentinel + 监控告警）

---

## 七、参考来源

1. **Microsoft Azure Architecture Center** — "Multitenancy in SaaS Applications"（官方权威，定义 6 大隔离模型原型）
2. **AWS SaaS Boost** — 开源参考架构 + 多租户策略模板
3. **PostgreSQL 官方文档** — [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
4. **ThoughtWorks Technology Radar** — 多租户架构白皮书
5. **Kubernetes 官方** — [Namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) + [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) + [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
6. **Sentinel 官方** — [流量控制](https://sentinelguard.io/zh-cn/docs/flow-control.html)（阿里开源，含租户维度示例）

---

## 🔗 系列导航（与本主题相关的章节）

| 主题 | 位置 | 互补关系 |
|------|------|---------|
| **架构演进（单体 → 微服务）** | [02-evolution](../../02-evolution/01-monolith-to-microservices/README.md) | 微服务是 SaaS 化的前置条件 |
| **微服务 vs 单体（面试题）** | [microservices](../microservices/README.md) | 多租户可与微服务结合 |
| **数据一致性** | [microservices/data-consistency](../microservices/data-consistency/README.md) | 多租户的 Saga / TCC 模式 |
| **RBAC + ABAC 访问控制** | [../../../../../04.system-design/05-security/access-control](../../../05-security/access-control/README.md) | 租户级的访问控制 |
| **云设计模式** | [../cloud-design-patterns](../cloud-design-patterns/README.md) | K8s Namespace 是云原生多租户基础 |
| **消费侧决策（买 SaaS vs 自研）** | [../../../../14.project-management/self-vs-saas-vs-outsourcing](../../../../14.project-management/self-vs-saas-vs-outsourcing/README.md) | 与本主题正交互补 |
| **面试速查版（13.split-hairs）** | [multi-tenant-saas](../../../../13.split-hairs/04.system-design/multi-tenant-saas/README.md) | 本章节的浓缩版 |

---

> 📅 2026-07-13 · 主模块 · 04.system-design · ⭐⭐⭐⭐⭐ · 6 隔离模型 + 4 应用层 + 5 反模式 + PostgreSQL RLS + 4 大厂实战 + 6 参考来源

← [返回: 系统设计基础](../README.md)
