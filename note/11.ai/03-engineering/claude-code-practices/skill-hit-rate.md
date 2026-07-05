<!--
module:
  parent: ai
  slug: ai/claude-code-practices/skill-hit-rate
  type: article
  category: 主模块子文章
  summary: Skill 数量爆炸后如何保证 Agent 命中率：描述/路由/加载/评估四层模型 + 5 大反模式 + 实战。
-->

# Skill 数量爆炸后，Agent 命中率怎么保证？

> 一句话定位：**Skills（技能）越多 ≠ 越好用**。当 Skill 数量从 5 个膨胀到 50 个时，Agent 选择错 Skill / 加载错上下文 / 撞描述冲突的概率指数级上升。本篇给出一套"四层模型 + 五大反模式 + 一线实战"的命中率保障方法论。

> **同模块兄弟**：[Claude Code 大型代码库实践](README.md) 讲 Skill 是怎么"渐进式披露"的；本文讲 Skill **数量爆炸后**怎么"调得动"。

---

## 一、为什么 Skill 数量会爆炸？

### 1.1 Skill 的"自然增长曲线"

```
项目初期：    3-5 个 Skill （足够覆盖 80% 任务）
├─ git-commit / lint-fix / pr-review / test-gen / doc-update
成长期：      10-20 个 Skill （按业务线 / 技术栈扩）
├─ + k8s-deploy / aws-deploy / graphql-codegen / migration-tool
成熟期：      30-50+ 个 Skill （按团队 / 客户 / 合规再扩）
├─ + partner-onboard-X / regulatory-check-Y / legacy-system-Z
```

**问题不是"该不该有 50 个 Skill"，而是"Agent 在 50 个候选里能不能稳定挑对"。**

### 1.2 命中率（Hit Rate）的定义

```
命中率 = Agent 在正确 Skill 上调用的次数 / Agent 总任务次数
```

**目标命中率**：≥ 90%（每 10 次任务至少 9 次调对 Skill）。**低于 80% 就有工程问题**。

---

## 二、四层模型：命中率的"拆解视角"

把"Agent 怎么选 Skill"拆成 4 层，每层单独优化：

| 层 | 问题 | 失败模式 | 优化手段 |
|---|------|---------|---------|
| **L1 描述层** | Skill 的"自我介绍"清不清楚？| 描述雷同 / 关键词缺失 | 写好 YAML frontmatter + 强制约束 |
| **L2 路由层** | Agent 用什么逻辑选？| LLM 选择漂移 / 向量召回错 | 规则路由 + LLM 兜底 |
| **L3 加载层** | Skill 上下文怎么进入 Prompt？| Token 爆炸 / 上下文污染 | 摘要注入 + 分层加载 |
| **L4 评估层** | 怎么知道命中率真实水平？| 无埋点 / 无回归 | 离线评测集 + 在线 A/B |

### 2.1 L1 描述层（Description Layer）

**核心约束**：每个 Skill 必须有 **结构化 frontmatter**，让 Agent 能"扫一眼就懂"。

```yaml
---
name: skill-name
description: |
  在 X 场景下做 Y 事情。不做 Z。如果用户问 W，请改用 skill-other。
when_to_use:
  - 场景1（动词 + 对象）
  - 场景2
when_not_to_use:
  - 场景A
inputs:
  - name: param1
    type: string
    required: true
---
```

**反模式**：把 description 写成"这是一个处理 X 的工具"，没写 when_not_to_use → Agent 会"猜不准边界"。

### 2.2 L2 路由层（Routing Layer）

**两种主流方案对比**：

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **LLM 自由选择** | 让 Claude 自己读 Skill 列表后选 | 灵活、零维护 | 选择漂移（不同上下文选不同）|
| **规则 + LLM 兜底** | 关键词/正则触发 → 不命中再让 LLM 选 | 稳定、可观测 | 维护规则成本 |
| **向量召回 + LLM 精排** | Skill 描述 embedding → top-K → LLM 选 | 处理长尾 | 召回错就完蛋 |

**推荐方案**：**规则 + LLM 兜底**。规则兜 80% 常见场景，LLM 兜剩下 20%。**关键是要给 LLM"明确拒识"路径**——"如果都不匹配，返回 SKIP"。

### 2.3 L3 加载层（Loading Layer）

Skill 命中后，**怎么把 Skill 上下文喂给 Agent**：

| 加载方式 | Token 成本 | 命中率影响 |
|---------|----------|----------|
| **全量加载**（整个 Skill 文件塞进 Prompt）| 高（每 Skill 几 KB）| 易触发上下文污染 |
| **摘要加载**（只注入 Skill 描述 + 入口）| 低 | Agent 知道有，但不知道细节 |
| **按需加载**（Agent 主动调 `load_skill(name)`）| 最低 | Agent 可能忘记调 |
| **分层加载**（描述 → 摘要 → 全量，三级渐进）| 中 | **推荐** |

**分层加载示意**：
```
Prompt 启动：注入所有 Skill 的「描述」（< 100 tokens / Skill）
Agent 判断命中 → 调用 load_skill_summary(name) → 注入摘要
Agent 需要细节 → 调用 load_skill_full(name) → 全量加载
```

### 2.4 L4 评估层（Evaluation Layer）

**没有评估 = 盲飞**。必须建评测集：

```
eval_set/
├── scenarios.jsonl     # 100+ 用户 query + 期望 Skill
├── judge_prompt.md     # 让另一个 LLM 判断：Agent 选对没
└── regression_log.jsonl # 每次 Skill 变更前后命中率对比
```

**最小可行评测集**：
- 50 个真实用户 query
- 每个 query 标注"应该命中的 Skill"
- 跑 Agent → 自动评分 → 计算命中率

**目标**：每次 Skill 增删，命中率不退化 > 2%。

---

## 三、五大反模式（必避）

### 反模式 1：关键词冲突（Description Collision）

**症状**：两个 Skill 描述里都有 "API" → Agent 选错。

**示例**：
```yaml
# Skill A
description: 生成 REST API 文档
# Skill B
description: 调用第三方 API 获取数据
# 用户问"帮我看看 API 文档" → Agent 随机选一个
```

**修复**：**差异化动词 + 对象**。"生成 X" vs "调用 Y"，避免共用高频词。

### 反模式 2：描述雷同（Description Duplication）

**症状**：两个 Skill 干的事差不多，描述也差不多 → 谁先注册谁被选。

**修复**：**合并 Skill** 或 **明确分工边界**（"Skill A 做只读，Skill B 做写操作"）。

### 反模式 3：上下文污染（Context Pollution）

**症状**：Skill 命中后，把无关的工具说明也塞进 Prompt → Agent 分心。

**修复**：**只注入 Skill 的入口 + 第一性原理**，细节用 `load_skill_full` 按需调。

### 反模式 4：LLM 选择漂移（LLM Routing Drift）

**症状**：同一 query，上下文不同时 Agent 选不同 Skill。

**修复**：
- 把"强制选 X"的规则写进 Skill description 第一句
- 或用**规则路由**（关键词 → Skill 名映射表）

### 反模式 5：Skill 数量爆炸（Skill Proliferation）

**症状**：50+ Skill，谁也用不清。

**修复**：
- **合并**：3 个相似的 merge 成 1 个带"子模式"的 Skill
- **分层**：核心 10 个 Skill + 扩展 40 个 Skill（扩展层默认不注入描述）
- **退役**：3 个月没人用的 Skill → 下线

---

## 四、实战：把命中率从 65% 拉到 92%

### 场景

一个 SaaS 团队的内部 Claude Code，65 个 Skill，命中率 65%（10 次有 3-4 次选错）。

### 优化步骤

**Step 1：建评测集（2 周）**
- 收集 100 个真实 query
- 标注期望 Skill
- 跑 baseline：命中率 65%

**Step 2：审计描述层（1 周）**
- 发现 18 个 Skill 描述雷同或冲突
- 合并 5 个、退役 3 个、重写 10 个 description
- 命中率 → 74%

**Step 3：引入规则路由（1 周）**
- 关键词 → Skill 映射表（30 条规则）
- 不命中再让 LLM 选
- 命中率 → 85%

**Step 4：分层加载（1 周）**
- 默认只注入描述
- 命中后按需 `load_skill_full`
- 命中率 → 90%

**Step 5：上下文审计（持续）**
- 删除 3 个没人用的 Skill
- 命中率 → 92%（稳定 3 个月）

### 最终结构

```
skills/
├── core/         (10 个，描述常驻)
├── extended/     (40 个，描述按需)
└── retired/      (15 个，归档)
```

---

## 五、可复用 Checklist（自查）

- [ ] 每个 Skill 都有 YAML frontmatter，含 `when_not_to_use`
- [ ] 没有 2 个 Skill 共享高频动词 + 对象
- [ ] 路由层有"明确拒识"路径（不命中返回 SKIP）
- [ ] 默认只加载描述，全量用 `load_skill_full` 按需调
- [ ] 有 ≥ 50 条的离线评测集
- [ ] 每次 Skill 增删跑回归，命中率不退化 > 2%
- [ ] 3 个月未使用的 Skill 自动归档

---

## 六、相关章节

**主模块内**：
- [Claude Code 大型代码库实践](README.md) — Skill 的"渐进式披露"基础
- [Harness Engineering](../../03-engineering/harness-engineering/README.md) — 上下文工程的总论
- [Context Engineering](../../02-technology-stack/context-engineering/README.md) — Token 预算与上下文压缩

**面试题层（13.split-hairs）**：
- [Skill 命中率面试 5 题](../../../13.split-hairs/11.ai/skill-hit-rate/README.md) — 配套面试题

**叙事层（12.story）**：
- [扩招 50 个厨师：Skill 调度的餐厅隐喻](../../../12.story/47-skill-scheduling-restaurant.md) — 餐厅叙事版

---

← [返回 Claude Code 实践总览](README.md)