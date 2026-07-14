<!--
question:
  id: 11.ai-ai-code-churn
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 架构困境
  tags: [11.ai, code, churn]
-->

# AI 代码流失率：采纳率 80% vs 有效率 30% 的真相

> AI 时代的代码流失率（Code Churn）问题。考察的是 **代码健康度量能力** + **AI 时代流失率恶化原因 + 改进策略**。

## 引子：6 个月后，AI 写的 1.5 万行代码只剩 20%

```text
你的小李：
- 1 月份开始用 Cursor + Claude
- 提交量 +217%（手工写哪有这么快）
- 老板很满意
- 6 个月后查看 git log

发现：
- **80% 的 AI 代码在 6 周内被改、被删、或者被重写**
- 现在仓库里"仍在生产使用"的 AI 代码只有 20%
- **采纳率 ≠ 留存率**
```

**真相**：AI Coding 加速生产力的同时，也在加速**代码流失率（Code Churn）**。

Waydev 2025 数据：

- 采纳率 80-90%（看着很爽）
- **6 周后留存率 10-30%**
- AI 用户代码修改率 **9.4 倍**于非 AI 用户

代码流失的根因：

1. AI 不懂业务上下文（"看起来对"实际不解决真问题）
2. AI 给出"短期 OK、长期难维护"的代码（缺乏架构视角）
3. 缺少 Harness 约束 → 重复造轮子

**解决**：Harness（规范 + 流程 + 测试）+ Code Review + ADR。

## 一、核心结论（TL;DR）

| 指标 | 数值 | 来源 |
|------|------|------|
| AI 代码初次采纳率 | 80-90% | Waydev |
| AI 代码 6 周留存率 | **10-30%** | Waydev |
| AI 用户代码修改率 | **9.4x** | GitClear |
| 代码变更率上升 | **+861%** | Faros AI |
| AI 时代平均代码流失率 | **40-60%** | 多源数据 |

> 一句话：**"代码流失率"是 AI 时代最被忽视的代码健康指标**——它告诉你的不是"产出了多少"，而是"留下了多少"。

---

## 二、什么是代码流失率（Code Churn Rate）？

### 1. 定义

**代码流失率** = 在一段时间内被修改、重写或删除的代码占总提交代码的比例。

```
代码流失率 = (修改/重写/删除的代码行数) / (总新增代码行数) × 100%
```

### 2. 4 种状态

```
新提交代码 → 在 4-6 周内可能进入以下状态：

  ① 留存（Kept）—— 仍在使用，没有修改
  ② 修改（Modified）—— 被修改但保留
  ③ 重写（Rewritten）—— 被大幅重写
  ④ 删除（Deleted）—— 被完全删除

后 3 种 = "代码流失"
```

### 3. 流失率阈值参考

| 流失率 | 健康度 | 解释 |
|--------|--------|------|
| < 20% | ✅ 健康 | 代码"留下来"的比例高 |
| 20-40% | ⚠️ 一般 | 有修改但基本保留 |
| 40-60% | ❌ 警告 | 大量代码被重写或删除 |
| > 60% | 🚨 危险 | 代码"无效产出"占主导 |

**AI 时代的问题**：平均流失率从 30% 涨到 **50-60%**。

---

## 三、3 大流失来源

### 1. AI 重写（AI Rewrite）

AI 生成的代码不准确，被人工重写：

```
AI 生成代码 → 工程师发现 5 个问题 → 重写 80% → 保留 20%
流失率 = 80%
```

**典型场景**：
- AI 用过时的库版本（`requests` v2 而非 v3）
- AI 引用虚构的 API（幻觉）
- AI 不懂业务上下文，逻辑写错

### 2. 需求变更（Requirement Change）

代码本身没错，但需求变了：

```
AI 生成代码 → 需求变更 → 重写 → 流失率 60%
```

**典型场景**：
- 业务方"加个小功能"→ 实际上改了 8 个页面
- 需求文档不清晰 → AI 写错 → 重写

### 3. 技术债（Tech Debt）

代码能跑，但有质量问题，被后续重构：

```
AI 生成代码 → 能跑 → 1 个月后被重构 → 流失率 50%
```

**典型场景**：
- 没有单元测试
- 命名不规范
- 架构混乱
- 性能问题

---

## 四、AI 时代流失率恶化的 4 个原因

### 1. AI 缺乏"项目上下文"

- AI 不知道项目历史决策
- AI 不知道"为什么这个函数要这样写"
- AI 不知道代码与业务的关系

→ **生成的代码常常"语法对但语义错"**，必须重写

### 2. 初级工程师审查不足

- 看不到 AI 代码的陷阱（安全/性能/幻觉）
- 100% 采纳，没有 review

→ **大量"看似 OK"的代码进入生产**，后续被修改

### 3. 业务方快速变更

- AI 让代码生成变快 → 业务方变本加厉提需求
- 每个变更都是代码流失

→ **变更频率上升 + 单次变更质量下降**

### 4. Harness 缺失

- 没有 `.claude/rules.md`
- 没有 CI/CD 校验
- 没有 Code Review 规范

→ **AI 代码绕过质量门禁**，直接进入代码库

---

## 五、6 大降低流失率的策略

### 1. Harness 优先

```markdown
# .claude/rules.md 示例

## 编码规范
- 必须使用项目指定的库版本（package.json）
- 不允许使用 AI 推荐的"过时 API"
- 必须写单元测试（覆盖率 > 60%）
- 命名遵循 BEM/驼峰规范

## 必读文档
- 架构决策记录（ADR）
- 项目 README
- 最近 3 个月的变更日志
```

### 2. 强制 Code Review

- 所有 AI 代码必须经过资深工程师 review
- 关键模块（支付/安全/数据）禁止 AI 直接写
- Review 时间计入考核

### 3. 流失率度量

```sql
-- 用 GitClear/Sonar/CodeScene 度量流失率
SELECT 
  author,
  COUNT(*) AS total_commits,
  SUM(CASE WHEN code_status = 'rewritten' THEN 1 ELSE 0 END) AS churn_count,
  churn_count / total_commits AS churn_rate
FROM commits
WHERE created_at > NOW() - INTERVAL '6 weeks'
GROUP BY author
```

### 4. 业务方变更控制

- 需求冻结期（开发启动后冻结 2 周）
- 变更控制委员会（CCB）
- 变更计价表

### 5. AI 代码"先实验后采纳"

- AI 代码先在 feature branch
- 跑 CI/CD 完整测试
- 性能/安全扫描通过后才合并

### 6. 写"为什么"而不是"是什么"

```python
# ❌ 只写代码
def get_user_orders(user_id):
    return db.query("SELECT * FROM orders WHERE user_id = ?", user_id)

# ✅ 写"为什么这样写"
def get_user_orders(user_id):
    """查询用户的订单列表。
    
    为什么这样写：
    1. 使用索引 user_id（性能）
    2. 不分页（业务约定，每个用户最多 50 单）
    3. 返回 dict 而非 ORM（跨服务兼容）
    
    ⚠️ 注意：如果未来订单数 > 50，必须改成分页
    """
    return db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
```

这样 AI 就能理解**决策背景**，生成的代码更准确。

---

## 六、面试陷阱

### 陷阱 1：以为代码流失率是"团队不努力"

- **真相**：流失率高通常是**结构性问题**——Harness 缺失、需求频繁、AI 缺乏上下文

### 陷阱 2：以为流失率越低越好

- **真相**：过低（< 10%）说明代码不演进，可能是过度设计或过度抽象

### 陷阱 3：以为 AI 时代流失率"不可避免"

- **真相**：通过 Harness + Review + 度量 + 教育，可以降到 20-30%

### 陷阱 4：以为只度量"commit 数"就够了

- **真相**：必须度量"留存率"和"修改率"，commit 数本身是误导指标

---

## 七、面试话术（90 秒版本）

> 代码流失率（Code Churn）是 AI 时代最被忽视的代码健康指标。Waydev 数据显示，AI 代码初次采纳率 80-90%，但 6 周后留存率只有 10-30%。
>
> 3 大流失来源：
>
> 1. **AI 重写**：AI 缺乏项目上下文，生成的代码常被重写
> 2. **需求变更**：业务方快速变更，导致代码被替换
> 3. **技术债**：没有单元测试、没有 Harness，后续被重构
>
> 6 大降低策略：Harness 优先 / 强制 Code Review / 流失率度量 / 变更控制 / AI 代码先实验后采纳 / 写"为什么"而不是"是什么"。
>
> 关键反直觉：流失率高通常是**结构性问题**（Harness 缺失），不是"团队不努力"。

---

## 八、相关章节

- 同栏目：[`ai-coding-productivity-paradox`](../ai-coding-productivity-paradox/README.md) — 4 大研究 + DORA
- 同栏目：[`ai-coding-roi`](../ai-coding-roi/README.md) — ROI 度量框架
- 同栏目：[`harness-engineering`](../harness-engineering/README.md) — Harness Engineering
- 同栏目：[`ai-code-review`](../ai-code-review/README.md) — AI 后端代码审核验收 6 层体系（降低流失率的前置门禁）
- 主模块：[`11.ai/05-applications`](../../../11.ai/05-applications/README.md) — AI 行业应用
- 故事：[`12.story/43-ai-productivity-paradox`](../../../12.story/43-ai-productivity-paradox.md)

- Token 成本：[`AI 编程 Token 经济学`](../ai-coding-token-economics/README.md) — Token 悖论 + 4 条省钱实践

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（2026 面试热点）

← [返回: 咬文嚼字 · ai-code-churn](README.md)
