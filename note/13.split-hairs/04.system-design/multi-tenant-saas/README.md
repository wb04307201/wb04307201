<!--
question:
  id: 04.system-design-multi-tenant-saas
  topic: 04.system-design
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 系统设计 / SaaS 架构
  tags: [04.system-design, 多租户, SaaS, 数据隔离, 租户路由, PostgreSQL RLS, noisy-neighbor]
-->

# 多租户 SaaS 系统设计 —— 6 大隔离模型 + 4 大应用层关注点 + 5 大陷阱

> 一句话定位：**多租户不是"加分项"——是 SaaS 商业模型的工程前提**。完整深度见 [主模块 multi-tenant-architecture 章节](../../../04.system-design/01-foundation/system-design-basics/multi-tenant-architecture/README.md)。

> **系列定位**：系统设计高频题（阿里云 / 钉钉 / 飞书 / Notion / Salesforce 全部考过）。考察的不是"什么是多租户"，而是 **6 大数据隔离模型选型 + 4 大应用层关注点 + 5 大反模式 + 实生产陷阱**。

---

⭐⭐⭐⭐⭐ 深度级别（高级工程师 / 架构师级）
📚 前置知识：分库分表 / 微服务 / RBAC / PostgreSQL 基础

---

## 引子：飞书 CTO 的"10000 租户"惊魂

```text
场景：2025 Q1 飞书企业版扩容——
- 业务：10000+ 企业租户共用一套系统，每租户 100-10 万用户
- 凌晨 3 点：某大租户批量导入 500 万员工 → 整体慢 5 秒
- 早上 8 点：客户提工单"为什么我开会时别人卡"
- 9 点 CTO 阿明被叫醒："排查一下，看看是不是 noisy neighbor"
```

**三个崩溃现场**：

1. 初创面试：「什么是多租户？」
2. 高级面试：「10000 租户怎么隔离，怎么路由，怎么限流？」
3. 架构师面试：「某租户突然流量 10 倍，怎么不波及其他租户？」

普通候选人会答："用 tenant_id 区分就好"——踩中"**缺隔离模型选型、缺应用层关注点、缺反模式**" 3 大雷区。
高分候选人会答：**6 大数据隔离模型选型 + 4 大应用层关注点（识别/上下文/限流/计费）+ PostgreSQL RLS + 5 个反模式（含 noisy neighbor 防御）+ K8s Namespace 隔离**。

---

## 一、核心原理（必选）

### 1.1 多租户 vs 单租户：商业模型的差异

| 维度 | 单租户（私有部署） | 多租户（SaaS） |
|------|----------------|--------------|
| **部署** | 每客户一套 | 一套系统服务多客户 |
| **数据** | 物理隔离天然支持 | 必须应用层强制隔离 |
| **计费** | 一次性 license | 按 tenant / 按用量订阅 |
| **运维** | 客户自运维 | 厂商统一运维 |
| **隔离需求** | 低（因为物理已隔离） | 高（共享栈，必须逻辑隔离）|

> **核心矛盾**：多租户 = 共享基础设施 + 必须逻辑隔离的强约束。隔离越强成本越高，隔离越弱风险越大。

### 1.2 6 大数据隔离模型（高频考点）

| # | 模型 | 隔离强度 | 成本 | 适合阶段 | 典型案例 |
|---|------|---------|------|---------|---------|
| 1 | **独立数据库**（每租户一库） | ⭐⭐⭐⭐⭐ 最强 | 高（> 1000 租户时数据库爆炸）| 少量大客户 / 合规要求 | 部分金融 SaaS |
| 2 | **共享 DB + 独立 Schema** | ⭐⭐⭐⭐ | 中（PostgreSQL schema 隔离，DDL 可差异化）| 中型 SaaS | Salesforce（早期）|
| 3 | **共享 DB + 共享 Schema + tenant_id 列** | ⭐⭐⭐ | 低（一套表，加 tenant_id 字段）| **90% SaaS 起步选** | 钉钉、Slack、Notion |
| 4 | **共享表 + 租户分区**（PostgreSQL RLS） | ⭐⭐⭐ | 低 | 中型 + 等保合规 | GitHub、GitLab |
| 5 | **K8s Namespace 隔离**（应用层） | ⭐⭐⭐⭐ | 中（计算资源隔离）| 中大型 | 阿里云 ACK 多租户 |
| 6 | **Serverless 多租户** | ⭐⭐ | 低 | 边缘场景 / 中小租户 | Vercel、Cloudflare Workers |

**速记口诀**：从 1 → 6 隔离强度递减，成本降低，规模化能力增强。

### 1.3 起步选型（绝大多数团队的正解）

```
90% 团队起步：模型 3（共享 DB + tenant_id 列）
进阶路径：模型 3 → 4（加 RLS）→ 5（K8s Namespace）→ 1（大客户独立库）
          └──────→ 直接跳 1（仅适 < 50 租户或合规要求）
```

**为什么 90% 选模型 3**：
- 一套表，开发 / 运维 / 升级成本最低
- 加 `tenant_id` 列 + WHERE 过滤 + 索引前缀 = 满足 80% 场景
- 后续可"按租户分库"平滑升级（ShardingSphere / Vitess）

### 1.4 4 大应用层关注点

| # | 关注点 | 关键实现 | 反模式 |
|---|--------|---------|--------|
| 1 | **租户识别** | Subdomain（a.example.com）/ JWT claim / Header（X-Tenant-Id）| 没有兜底识别 → 访问错数据 |
| 2 | **租户上下文传递** | ThreadLocal / RequestScope / OpenTelemetry Baggage | 异步任务丢上下文 → 数据混淆 |
| 3 | **租户级限流 / 配额** | Sentinel 租户维度 / Redis 滑动窗口 / K8s NetworkPolicy | 全局限流 → 大租户挤压小租户 |
| 4 | **计费 / 计量**（Metering）| 用量埋点 → Kafka → ClickHouse → 出账 | 计费丢失 → 收入流失 |

**关键反例**：模型 3 选好后，4 大应用层任一缺失 = 数据泄露或计费失败。

---

## 二、6 大反模式 + noisy neighbor 防御（5 大陷阱）

| # | 反模式 | 后果 | 防御 |
|---|--------|------|------|
| 1 | **忘记 WHERE tenant_id** | 数据跨租户泄露（重罪）| 中间件强制 + 单元测试 + 集成测试 |
| 2 | **跨租户 JOIN** | 性能差 + 合规风险 | 禁止 JOIN，按租户查询 + 拼装 |
| 3 | **noisy neighbor**（噪声邻居）| 大租户拖垮小租户 | 租户级限流 + 资源隔离（K8s/quota）+ 监控告警 |
| 4 | **升级爆炸** | schema 升级要做 N 次 | 单库共享 + Liquibase/Flyway 集中升级 |
| 5 | **审计日志不分租户** | 合规追溯失败 | 每个日志 / 审计事件打 tenant_id tag |
| 6 | **计费计量失败** | 收入流失 | 异步埋点 + ClickHouse 汇总 + 对账 |

**noisy neighbor 防御详解**（飞书真实场景）：
```java
// Sentinel 租户级限流（伪码）
@SentinelResource(value = "listDocs",
                   blockHandler = "tenantBlockHandler")
public List<Doc> listDocs(String tenantId) {
    // 内部还需按 tenantId 设置限流规则
}

// 资源隔离：K8s
// - namespace-per-tenant（每个大租户独立 ns）
// - ResourceQuota（限制 CPU / 内存 / PVC）
// - NetworkPolicy（限制跨租户网络访问）
```

---

## 三、PostgreSQL RLS（Row-Level Security）实战

**核心思想**：把"WHERE tenant_id = ?" 从应用层下沉到数据库层，**数据库自身保证不漏数据**。

```sql
-- 1. 启用 RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 2. 创建策略（仅允许看自己租户）
CREATE POLICY tenant_isolation_policy ON documents
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- 3. 应用层注入租户上下文（每次连接）
SET app.current_tenant = 'tenant-a-uuid';

-- 4. 查询自动加 WHERE 条件（数据库自己保证）
SELECT * FROM documents;  -- 物理 SQL 不带 WHERE
                              -- 但 RLS 让其等价于
                              -- WHERE tenant_id = 'tenant-a-uuid'
```

**3 大优势**：
- ✅ 应用层忘写 WHERE → 数据库兜底（defense-in-depth）
- ✅ 性能上 RLS 可被 planner 优化（不会每次全表扫）
- ✅ 同一连接池服务多租户（降低连接数开销）

**局限**：
- 跨租户运维动作（备份 / 升级）需 Superuser 绕开 RLS
- 不是所有数据库支持：PostgreSQL ✅ / MySQL 8.0+ ⚠️（弱支持）/ Oracle ✅

---

## 四、面试话术（90 秒版本）

### 题目：如何设计一个支撑 10000 租户的 SaaS 系统？

**高分答案（4 层递进，60-90 秒）**：

```
1. 一句话定位（10 秒）：
   "多租户 SaaS 的核心矛盾是'共享基础设施 + 必须逻辑隔离'，
   关键不在于选哪个模型，而在于 4 大应用层关注点 + 5 个反模式防御。"

2. 6 大隔离模型速览（30 秒）：
   "10000 租户 90% 起步选模型 3：
   - 共享 DB + 共享 Schema + tenant_id 列
   - 加 PostgreSQL RLS 让数据库兜底隔离
   - 大客户独立库（模型 1）做差异化
   - 共享模型 5 K8s Namespace 做计算隔离
   - 模型 6 Serverless 多租户给边缘场景"

3. 4 大应用层关注点 + noisy neighbor 防御（20 秒）：
   "4 大关注点：
   - 租户识别（Subdomain/JWT/Header）
   - 上下文传递（ThreadLocal → 异步时换 Baggage）
   - 租户级限流（Sentinel 租户维度）
   - 计费计量（Kafka → ClickHouse）
   + 5 个反模式：
   - 忘 WHERE / 跨租户 JOIN / noisy neighbor / 升级爆炸 / 审计不分租户
   noisy neighbor 防御：租户级限流 + K8s 资源隔离 + 监控告警"

4. 权衡视角（25 秒）：
   "但多租户不是越强越好：
   - 隔离越强成本越高（独立库成本 10 倍于共享库）
   - 起步共享 + RLS，> 100 大客户再独立库
   - 反例：早期 Salesforce 独立 schema，Notion 始终共享
   - 实战要看合规：GDPR / HIPAA / 等保三级 → 必须独立库
```

---

## 五、面试反问（让候选人反客为主）

```
Q1：贵司当前是哪种隔离模型？为什么？
    → 模型 3：追问"为什么不用 RLS"；模型 1：追问"运维成本"
Q2：贵司 noisy neighbor 怎么防？
    → 答租户级限流 + K8s 隔离 = 高分
Q3：贵司跨租户数据备份怎么做？
    → 全量备份 + 租户级订阅可恢复 = 高分
Q4：贵司租户上下文怎么传到异步任务？
    → ThreadLocal 失效 → OpenTelemetry Baggage
Q5：贵司 SaaS 计费是按订阅还是按用量？
    → 答按用量 → 追问"计量准确度保证"
```

---

## 🔗 系列导航表（13.split-hairs · 04.system-design 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [cap-theorem](../cap-theorem/README.md) | CAP / BASE 一致性权衡 | ⭐⭐⭐⭐ |
| [circuit-breaker](../circuit-breaker/README.md) | 熔断降级与故障隔离 | ⭐⭐⭐⭐ |
| [distributed-id](../distributed-id/README.md) | 雪花 / Leaf / 号段 | ⭐⭐⭐⭐⭐ |
| [distributed-transaction](../distributed-transaction/README.md) | Saga / Seata / TCC | ⭐⭐⭐⭐⭐ |
| [idempotency](../idempotency/README.md) | 幂等键 / 状态机 | ⭐⭐⭐⭐ |
| [microservices-vs-monolith](../microservices-vs-monolith/README.md) | 微服务 6 大优势 | ⭐⭐⭐⭐⭐ |
| [high-performance/product-search](../high-performance/product-search/README.md) | 商品搜索 4 层架构 | ⭐⭐⭐⭐ |
| [high-performance/file-upload](../high-performance/file-upload/README.md) | 大文件上传分片 | ⭐⭐⭐ |
| [payment-message-lost](../payment-message-lost/README.md) | 支付消息不丢 | ⭐⭐⭐⭐ |
| [url-shortener](../url-shortener/README.md) | 短链系统设计 | ⭐⭐⭐⭐ |
| **multi-tenant-saas**（本篇）| 多租户 6 模型 + 4 关注点 | ⭐⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [04.system-design · multi-tenant-architecture](../../../04.system-design/01-foundation/system-design-basics/multi-tenant-architecture/README.md) — 6 大隔离模型 + 4 大应用层 + 5 反模式 + PostgreSQL RLS + 飞书/钉钉/Salesforce 生产实践

## 🔗 餐厅叙事（12.story）

- [12.story · 19-saas-multitenant](../../../../12.story/19-saas-multitenant.md) —— 阿明的加盟帝国：架构从自用到 SaaS 的多租户化

---

> 📅 2026-07-13 · 咬文嚼字 · 04.system-design · ⭐⭐⭐⭐⭐ · 6 隔离模型 + 4 应用层 + 5 反模式 + PostgreSQL RLS + 90 秒话术 + 11 兄弟导航

← [返回: 咬文嚼字 · 04.system-design](README.md)
