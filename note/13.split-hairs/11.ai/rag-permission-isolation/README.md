<!--
question:
  id: 11.ai-rag-permission-isolation
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 生产 Bug
  tags: [11.ai, RAG, permission, access-control, security, multi-tenant]
-->

# RAG 权限隔离设计：实习生搜到了 CEO 的薪资文档

> 企业 RAG 落地的第一道关 —— 考察的不是"RAG 怎么检索"，而是 **检索结果怎么按权限过滤** + **pre-filtering vs post-filtering** + **ACL 同步机制** + **多租户隔离**。完整 RAG 架构见 [RAG 面试题](../rag/README.md)。

> **系列定位**：AI 工程面试题（企业 RAG 落地必考）。从"权限泄露事故"出发，覆盖 4 种隔离方案的工程权衡。

---

## 引子：一次让 CTO 心脏骤停的搜索

```text
某企业上线了内部 RAG 知识库。
上线第三天，实习生问了一句：

  "公司 CTO 的年薪是多少？"

RAG 回答：
  "根据 2025 年度薪酬报告（HR 部门内部文档），
   CTO 年薪为 XXX 万元，包含期权 XXX..."

这个文档本应只有 HR 和 CEO 能看到。
```

**根因**：RAG 把所有文档都灌进了同一个向量库，检索时没有做权限过滤。

面试官问："RAG 的权限隔离怎么设计？有哪些方案？各自的 trade-off 是什么？"

如果你只能回答"加个权限判断"——面试就结束了。

---

## 一、4 种权限隔离方案

### 方案对比

| 方案 | 原理 | 安全性 | 性能 | 复杂度 | 适用 |
|------|------|--------|------|--------|------|
| **Pre-filtering** | 检索前用权限条件过滤向量库 | ✅ 最高 | ⚠️ 降低召回率 | 中 | 企业级首选 |
| **Post-filtering** | 检索后按权限剔除无权文档 | ⚠️ 可能泄露 | ✅ 不影响检索 | 低 | 简单场景 |
| **Separate Index** | 每个角色/团队独立向量库 | ✅ 物理隔离 | ⚠️ 资源浪费 | 高 | 强合规场景 |
| **Hybrid** | Pre-filter + Post-filter 组合 | ✅✅ 双重保障 | ⚠️ 最复杂 | 最高 | 金融/医疗 |

### 1.1 Pre-filtering（检索前过滤）

```text
原理：在向量检索时，把权限条件作为 metadata filter

示例（Pinecone / Weaviate / Milvus 语法）：
  query: "CTO 薪资"
  filter: {
    "department": {"$in": user.allowed_departments},
    "access_level": {"$lte": user.access_level}
  }

  → 只检索用户有权访问的文档
  → 无权文档根本不进入 Top-K
```

**优点**：
- ✅ 安全性最高 — 无权文档永远不会出现在检索结果中
- ✅ 不浪费 LLM Token — 不会把无权内容塞进 Prompt

**缺点**：
- ⚠️ 降低召回率 — 过滤后文档池变小，可能漏掉相关文档
- ⚠️ 需要向量库支持 metadata filter（不是所有向量库都支持）

### 1.2 Post-filtering（检索后过滤）

```text
原理：先正常检索 Top-K，再剔除无权文档

流程：
  1. 向量检索 Top-20（不过滤）
  2. 逐条检查用户权限
  3. 剔除无权文档
  4. 取剩余文档的前 K 条送给 LLM
```

**优点**：
- ✅ 不影响检索质量 — 全量检索保证召回率
- ✅ 实现简单 — 不需要向量库支持 filter

**缺点**：
- ⚠️ 可能泄露信息 — 检索结果中可能包含无权文档的标题/摘要
- ⚠️ 浪费 Token — 检索了但不用，浪费检索资源
- ⚠️ 结果不稳定 — Top-K 过滤后可能只剩 1-2 条

### 1.3 Separate Index（独立索引）

```text
原理：按角色/部门/团队建立独立的向量库

架构：
  HR 向量库      → 只有 HR 能查
  工程向量库    → 只有工程师能查
  管理层向量库  → 只有管理层能查

  用户查询 → 路由到对应向量库 → 检索
```

**优点**：
- ✅ 物理隔离 — 数据层面完全不交叉
- ✅ 审计友好 — 每个库独立审计

**缺点**：
- ⚠️ 资源浪费 — N 个库 = N 倍存储和计算
- ⚠️ 跨权限查询困难 — 一个查询涉及多个权限域时需要合并
- ⚠️ 维护复杂 — N 个库的同步和更新

### 1.4 Hybrid（混合方案）

```text
原理：Pre-filter 保证安全底线 + Post-filter 做二次校验

流程：
  1. Pre-filter：向量检索时加 metadata filter（粗过滤）
  2. Post-filter：逐条校验细粒度权限（精过滤）
  3. Answer-level gate：LLM 生成后再次校验（防溢出）
```

**Glean 的三层权限模型就是 Hybrid 方案**：
1. 源系统权限镜像（Pre-filter）
2. 实时权限重算（Post-filter）
3. 答案级门控（Answer-level gate）

---

## 二、ACL 同步机制

### 2.1 什么是 ACL 同步

```text
ACL（Access Control List）= 谁可以看什么

RAG 的 ACL 必须与源系统保持一致：
  Google Drive 改了权限 → RAG 的 metadata 必须同步更新
  员工调岗 → RAG 的可访问范围必须分钟级更新
  文档被删除 → RAG 的索引必须同步删除
```

### 2.2 3 种同步策略

| 策略 | 原理 | 延迟 | 复杂度 |
|------|------|------|--------|
| **实时同步** | Webhook / 事件监听 → 权限变更立即更新 | 秒级 | 高 |
| **定时同步** | 每 N 分钟全量/增量拉取权限 | 分钟级 | 中 |
| **查询时校验** | 每次检索时实时查源系统权限 | 实时 | 低（但慢） |

**生产推荐**：定时同步（5 分钟）+ 查询时校验（兜底）

```text
定时同步（主路径）：
  每 5 分钟：
    1. 拉取源系统的权限变更日志
    2. 更新向量库的 metadata（access_level / department）
    3. 删除已撤销权限的文档索引

查询时校验（兜底）：
  每次检索：
    1. 正常检索 Top-K
    2. 对每条结果实时查询用户权限
    3. 剔除无权文档
```

---

## 三、多租户隔离

### 3.1 三种多租户模型

| 模型 | 隔离级别 | 成本 | 适用 |
|------|---------|------|------|
| **共享库 + metadata filter** | 逻辑隔离 | 低 | SaaS 多租户 |
| **独立 namespace** | 命名空间隔离 | 中 | 企业多部门 |
| **独立向量库实例** | 物理隔离 | 高 | 强合规（金融/医疗） |

### 3.2 SaaS 场景典型设计

```text
SaaS RAG 平台（如 Notion AI / Confluence AI）：

每个租户的文档都存储在同一个向量库
但每条文档的 metadata 包含 tenant_id

检索时：
  filter: { "tenant_id": current_user.tenant_id }

  → 租户 A 永远搜不到租户 B 的文档
  → 向量库层面保证隔离
```

**关键风险**：
- metadata filter 必须是强制的（不能依赖应用层过滤）
- 向量库的 filter 实现必须是确定性的（不能"大概率过滤"）

---

## 四、5 个反模式

### 反模式 1：权限只在应用层做

- 错：向量库不做 filter，全靠应用代码判断"这条文档用户能不能看"
- 对：权限必须在向量库层面强制（metadata filter），应用层只是兜底

### 反模式 2：权限信息不随文档更新

- 错：文档权限改了但向量库 metadata 没同步 → 旧权限生效
- 对：ACL 同步必须自动化（Webhook / 定时拉取），不能依赖手动更新

### 反模式 3：Post-filtering 当唯一方案

- 错：先检索再过滤 → 无权文档的标题/摘要可能已经泄露
- 对：至少用 Pre-filtering 做底线，Post-filtering 做精校验

### 反模式 4：忽略 LLM 的"记忆泄露"

- 错：即使 Post-filtering 剔除了无权文档，LLM 可能从其他文档"推断"出无权信息
- 对：Answer-level gate — 生成后再次校验答案是否包含无权信息

### 反模式 5：测试不覆盖权限场景

- 错：只测"搜得准不准"，不测"不该搜到的是否搜到了"
- 对：必须有权限测试集 — N 个用户 × M 个文档，验证每个用户只能看到有权文档

---

## 五、权限隔离测试方法

```text
测试矩阵：
  用户 A（实习生）: 只能看 公开文档 + 工程部文档
  用户 B（HR）:    能看 公开文档 + HR 文档
  用户 C（CEO）:   能看 所有文档

测试用例：
  1. 用户 A 搜 "薪资报告" → 应该返回空（无权）
  2. 用户 B 搜 "薪资报告" → 应该返回 HR 薪资模板
  3. 用户 C 搜 "薪资报告" → 应该返回 CEO 薪资报告

  4. 用户 A 的权限被提升 → 5 分钟内能搜到新文档
  5. 用户 B 被调离 HR → 5 分钟内搜不到 HR 文档

自动化：
  每次 CI 跑权限测试集 → 失败则阻断部署
```

---

## 六、面试话术（90 秒版本）

> "RAG 权限隔离，我从 4 个层面回答：
>
> **方案选型**：4 种方案——Pre-filtering（检索前 metadata filter，安全性最高）、Post-filtering（检索后剔除，简单但可能泄露）、Separate Index（物理隔离，成本高）、Hybrid（双重保障，最安全）。企业级首选 Pre-filtering + Post-filtering 组合。
>
> **ACL 同步**：权限必须与源系统保持一致。推荐定时同步（5 分钟）+ 查询时校验（兜底）。权限变更必须分钟级反映到向量库的 metadata 上。
>
> **多租户**：SaaS 场景用共享库 + tenant_id metadata filter（逻辑隔离），强合规场景用独立向量库实例（物理隔离）。filter 必须是向量库层面强制的，不能依赖应用层。
>
> **5 个反模式**：权限只在应用层做、权限不随文档更新、Post-filtering 当唯一方案、忽略 LLM 推断泄露、测试不覆盖权限场景。必须有权限测试集，每次 CI 跑。"

---

## 七、相关章节

- RAG 架构：[`RAG 架构设计`](../rag/README.md) — 完整 RAG 流程（Chunking/Embedding/检索/生成）
- 企业案例：[`Glean 企业搜索`](../../../11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md) — 权限模型三层实践（源系统镜像/实时重算/答案门控）
- LLM 安全：[`LLM 安全`](../../../11.ai/07-llmops/05-llm-security/README.md) — Agent 最小权限原则
- Agentic Search：[`Agentic Search vs RAG`](../../../11.ai/07-llmops/agentic-search-vs-rag/README.md) — 权限过滤在不同搜索模式中的差异
- 幻觉问题：[`LLM 幻觉`](../hallucination/README.md) — RAG 减少幻觉，但权限不当会引入"信息泄露"

---

> 📅 2026-07-08 · 咬文嚼字 · RAG 权限隔离设计 · ⭐⭐⭐⭐⭐（高频面试 + 企业 RAG 落地必备）

← [返回 AI 咬文嚼字](../README.md)
