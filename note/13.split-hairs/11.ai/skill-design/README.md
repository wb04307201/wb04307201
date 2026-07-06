<!--
question:
  id: 11.ai-skill-design
  topic: 11.ai
  difficulty: ⭐⭐⭐
  frequency: 高频
  scenario_type: 工程权衡
  tags: [11.ai, Claude Code, Skill, Agent, 设计方法论, YAML frontmatter]
-->

# Skill 从 0 到 1：怎么设计一个能用的 Skill？

> 一句话定位：**写 Skill 不是写教程**。面试官考察的不是"Skill 是什么"（基础），而是"**怎么判断该不该写 Skill / 怎么写一个能用的 Skill**"。深度方法论见 [主模块 Skill 设计章节](../../../11.ai/03-engineering/claude-code-practices/skill-design.md)。

> **系列定位**：高频 AI 工程面试题（中级到高级）。考察工程化判断力 + YAML 细节把控。配套姐妹题 [Skill 命中率 5 题](../skill-hit-rate/README.md)——本文讲"**写**"，姐妹题讲"**调**"。

---

⭐⭐⭐ 深度级别（高级 AI 工程师级）
📚 前置知识：Claude Code / Skills 基础、Harness Engineering、YAML 语法、Agent 工程化

---

## 引子：面试官的"工程判断"陷阱

面试官："你们的项目里什么时候会决定写一个 Skill？"

阿明答："需要专业知识的时候就写。"

面试官追问："**那 '提交前必须跑 lint' 也写个 Skill？** 还是 '项目用 React 18' 也写个 Skill？"

阿明答："……也可以写吧？"

面试官："**不对**。'提交前跑 lint' 是行为约束，应该加 Hook；'React 18' 是每次会话都要用的常识，应该放 CLAUDE.md。**写 Skill 之前要先过决策树**，否则你会做出一个 200 行的 God Skill，覆盖率低、命中率差、Token 浪费。"

阿明愣住。

**这道题的陷阱**：面试官考察的是 **"工程判断力"** —— 知道什么时候不该写 Skill 比知道怎么写更重要。

---

## Q1：什么时候该写 Skill，不该改 CLAUDE.md？

**答**：过决策树 —— 三个判断问题。

```
Q1：每次会话都要用 vs 特定场景才用？
├─ 每次都要 → 改 CLAUDE.md（不要写 Skill）
└─ 特定场景 → Q2

Q2：行为约束 vs 专业知识？
├─ 行为约束（"提交前 lint"）→ 加 Hook（不要写 Skill）
└─ 专业知识（"怎么审查 PR 安全性"）→ Q3

Q3：能渐进式披露吗？
├─ 能 → 写 Skill ✅
└─ 不能 → 写 Subagent 或加 MCP server
```

**反例清单**：

| 场景 | 错的选择 | 对的选择 |
|------|---------|---------|
| "提交前必须 lint" | 写 Skill | 加 Hook（PreToolUse 拦截 Bash）|
| "项目用 React 18" | 写 Skill | 放 `CLAUDE.md` 根目录 |
| "查询订单数据库" | 写 Skill | 加 MCP server（结构化查询 + 权限）|
| "审查 PR 安全漏洞" | **写 Skill ✅** | 符合决策树（专业知识 + 按需加载）|

**反直觉点**：**不写 Skill 也是一种能力**。盲目堆 Skill 会让 Agent 注意力分散、Token 爆炸、命中率下降。

---

## Q2：Skill frontmatter 必填哪些字段？

**答**：6 字段 —— `name` / `description` / `when_to_use` / `when_not_to_use` / `inputs` / `outputs`。

```yaml
---
name: pr-review-security
description: |
  审查 PR 中的安全漏洞。覆盖 SQL 注入 / XSS / 鉴权绕过 4 类。
  必须在 pr-review 类任务中显式调用。
when_to_use:
  - "审查 PR 安全性"
  - "检查代码中是否有 SQL 注入 / XSS"
when_not_to_use:
  - "通用代码风格检查（请用 lint-hook）"
  - "性能审查（请用 pr-review-performance）"
inputs:
  - name: pr_diff
    type: string
    required: true
    description: PR 的 diff 内容
  - name: focus_areas
    type: array
    items: { type: string }
    required: false
outputs:
  format: markdown
  schema:
    - name: issues
      type: array
      description: 发现的安全问题列表
---

# 正文
```

**关键字段的作用**：

| 字段 | 作用 | 缺失后果 |
|------|------|---------|
| `name` | 唯一标识 | Skill 加载失败 |
| `description` | Agent 扫描入口 | Agent 不知道怎么用 |
| `when_to_use` | 触发场景 | Agent 不知道何时调用 |
| **`when_not_to_use`** | **拒识路径** | **Agent 在边界场景乱猜** |
| `inputs` | 输入约束 | Agent 传残缺数据 |
| `outputs` | 输出格式 | Agent 不知道输出长什么样 |

**最常被遗漏的是 `when_not_to_use`** —— 没有它，Agent 在"半相关"场景强行调用，命中率雪崩。

---

## Q3：Skill 应该大而全还是小而精？

**答**：**小而精 + 组合**。一个 Skill 覆盖一个明确场景，复杂任务组合多个 Skill。

**反例（God Skill）**：

```yaml
# 错误
name: code-review
description: 审查代码风格、安全、性能、架构、可读性、可维护性...
when_to_use: [审查代码、改进代码、写代码...]
# ❌ 200 字描述，10 条 when_to_use → Agent 选不对、加载慢
```

**正例（Small Skills）**：

```yaml
# code-review-security
name: code-review-security
description: 审查代码安全漏洞
when_to_use: [代码安全审计]
when_not_to_use: [代码风格（请用 code-review-style）]

# code-review-performance
name: code-review-performance
description: 审查代码性能瓶颈
when_to_use: [代码性能审查]
when_not_to_use: [代码安全（请用 code-review-security）]

# code-review-style
name: code-review-style
description: 审查代码风格与可读性
when_to_use: [代码风格审查]
when_not_to_use: [代码安全 / 性能（请用对应 Skill）]
```

**关键 trade-off**：
- 大 Skill：单次加载覆盖全，但 Token 多、Agent 选不准
- 小 Skill：单次加载轻，Agent 选得准，但需要组合调用

**经验法则**：**一个 Skill ≤ 200 行 frontmatter + 正文**，超过就拆。

---

## Q4：怎么测试 Skill 是否有效？

**答**：**离线评测集 + 在线埋点**双轨制。

**离线评测集**（最小 30 条）：

```jsonl
{"query": "审查这个 PR 有没有 SQL 注入", "expected_skill": "pr-review-security"}
{"query": "检查代码风格", "expected_skill": "lint-hook"}
{"query": "看看 PR 的鉴权逻辑", "expected_skill": "pr-review-security"}
```

跑 Agent → 自动判断 → 计算 **命中率（选对 Skill / 总次数）**。

**通过标准**：**命中率 ≥ 90%**。

**在线埋点**（生产环境）：

```yaml
metrics:
  - name: skill_invocation_total
    labels: [skill_name, outcome]  # success / wrong_choice / error
  - name: skill_hit_rate
    labels: [skill_name]  # 人工反馈 30 天均值
```

**通过标准**：**在线 hit_rate ≥ 85%**。

**完整测试流程**：
1. 写完 Skill → 跑离线评测 → 通过才上线
2. 上线后 → 埋点 + 人工反馈 → 30 天均值达标
3. 任何时候 hit_rate 跌破阈值 → 回滚或重新设计

**反模式**：**只写不测** —— Skill 上线后没人知道效果，Agent 默默用错的，积累几个月才发现"命中率 50%"。

---

## Q5：Skill 和 MCP / Tool / Subagent 怎么选？

**答**：**4 维度决策** —— 谁来执行 / 是否需要状态 / 复杂度 / 复用度。

| 维度 | Skill | MCP | Subagent |
|------|-------|-----|----------|
| **执行者** | 当前的 Claude 会话 | 外部服务（API / DB / 文件）| 新的 Claude 实例（独立上下文）|
| **状态** | 无状态（纯函数）| 有状态（连接 / 缓存）| 有独立上下文 |
| **复杂度** | 中（专业知识 + 决策树）| 低（接口调用）| 高（多步任务）|
| **复用度** | 跨项目复用 | 跨项目复用 | 单次任务 |

**典型场景对照**：

| 场景 | 选什么 | 理由 |
|------|--------|------|
| "审查 PR 安全漏洞" | **Skill** | 专业知识 + 无状态 |
| "查询订单数据库" | **MCP** | 需要连接 DB + 权限 |
| "调研 X 库的最新版本" | **Subagent** | 多步搜索 + 独立上下文（避免污染主会话）|
| "生成 OpenAPI 文档" | **Skill** | 专业知识 + 按需加载 |
| "执行数据库 migration" | **MCP + Hook** | MCP 提供工具 + Hook 保证人工确认 |

**反直觉点**：**Subagent 不是 Skill 的替代**。Subagent 是"雇一个临时工"，Skill 是"给现有员工一份 SOP"。前者隔离上下文但开销大，后者轻量但共享上下文。

---

## 总结：面试答这题的 3 层结构

**30 秒简版**：
> "写 Skill 之前先过决策树 —— **每次都用**改 CLAUDE.md，**行为约束**加 Hook，**结构化查询**走 MCP，**多步任务**用 Subagent，剩下才是 Skill。Skill 写的时候**6 字段 frontmatter** 必填（特别是 when_not_to_use），**小而精 + 组合**而不是大而全，**离线评测集 + 在线埋点**验证效果。"

**60 秒扩展版**（如果面试官追问决策树细节）：
> "决策树核心是三个判断：知识使用频率（每次 vs 特定）、性质（行为约束 vs 专业知识）、可披露性（能不能渐进式加载）。判断完了之后还要选 6 字段 frontmatter —— `when_not_to_use` 最关键，没有它 Agent 在边界场景会乱选。测试要双轨制：离线 30 条 query 命中率 ≥ 90% 才能上线，上线后埋点 + 人工反馈 30 天均值 ≥ 85%。"

**踩分点提醒**：
- ✅ 提"决策树" → 显式说明 3 个判断问题
- ✅ 提"`when_not_to_use`" → 强调拒识路径的重要性
- ✅ 提"小而精 + 组合" → 反 God Skill
- ✅ 提"离线 + 在线双轨" → 完整测试方法论

---

## 相关章节

**主模块**：
- [Skill 设计方法论深度章节](../../../11.ai/03-engineering/claude-code-practices/skill-design.md) — 决策树 + 4 阶段 + 5 反模式 + YAML 模板
- [Claude Code 大型代码库实践](../../../11.ai/03-engineering/claude-code-practices/README.md) — Skill 渐进式披露基础
- [Skill 命中率深度章节](../../../11.ai/03-engineering/claude-code-practices/skill-hit-rate.md) — "写"的姐妹篇："调"

**同栏目（11.ai 高频面试题）**：
- [Skill 数量一多，Agent 命中率怎么保证？](../skill-hit-rate/README.md) — "调"的面试题
- [为什么 Claude Code 放弃了 RAG？](../claude-code-agentic-search/README.md) — Agentic Search 取代 RAG
- [Harness Engineering 是什么？](../harness-engineering/README.md) — 上下文工程总论
- [Context Engineering 怎么做？](../context-engineering/README.md) — Token 预算
- [Function Calling 怎么设计？](../function-calling/README.md) — 工具调用工程化

**教学场景**：
- [training/lesson4 · Skill 编写与设计模式](../../../11.ai/training/lesson4/README.md) — 教学场景下怎么教新人写 Skill

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐

← [返回: 咬文嚼字 · skill-design](README.md)
