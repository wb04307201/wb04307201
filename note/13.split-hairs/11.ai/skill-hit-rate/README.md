<!--
question:
  id: 11.ai-skill-hit-rate
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 工程权衡
  tags: [11.ai, Claude Code, Skill, Agent, Harness, Routing, 命中率]
-->

# Skill 数量一多，Agent 命中率怎么保证？

> 一句话定位：**Skills 越多 ≠ 越好用**。当 Skill 数量从 5 个膨胀到 50 个，Agent 选择错 / 加载错 / 撞描述冲突的概率指数级上升。面试官追问的不是"Skill 怎么写"，而是"**怎么在 50 个候选里稳定挑对**"。

> **系列定位**：高频 AI 工程面试题（考察 Agent 工程化能力，非"Skill 是什么"基础题）。深度原理见 [主模块深度章节](../../../11.ai/03-engineering/claude-code-practices/skill-hit-rate.md)。

---

⭐⭐⭐⭐ 深度级别（高级 AI 工程师级）
📚 前置知识：Claude Code / Skills 概念、RAG / Agentic Search、Harness Engineering、Token 预算

---

## 引子：面试官的"工程化"陷阱

面试官："你们 Agent 用了多少个 Skill？"

阿明答："60 多个，覆盖了我们公司所有的内部工具。"

面试官追问："**60 多个 Skill 一起挂在 Prompt 里，Agent 怎么保证每次都挑对？命中率多少？**"

阿明答："……我们没统计过，但应该挺高的。"

面试官："**没统计过就是没保证**。如果 Agent 10 次里有 3 次挑错 Skill，要么用户信任崩塌，要么你们被迫把 Prompt 越堆越大，Token 成本失控。"

阿明愣住。

**这道题的陷阱**：面试官考察的不是 Skill **数量**（越多越好是错觉），而是 Skill **调度工程化**（描述/路由/加载/评估四层模型 + 量化指标）。

今天讲清楚：
1. Skill 数量爆炸后，命中率会怎样退化？
2. 四层模型怎么分别优化？
3. 五大反模式怎么避？
4. 怎么用评测集量化？

---

## Q1：Skill 数量从 5 涨到 50，命中率会怎么退化？

**答**：**非线性退化**。经验曲线大致：

```
Skill 数  命中率  退化原因
───────  ──────  ──────────────────────────────
 5      95%     描述够清楚，Agent 一眼选对
10      90%     偶有重叠，Agent 偶尔选错
20      80%     描述冲突 / 关键词撞车
50      65%     Token 压力大，描述互相干扰
100     <50%    Prompt 装不下所有描述，必须摘要
```

**核心原因**：
1. **描述冲突**：两个 Skill 都含 "API" 关键词 → Agent 随机选
2. **Token 压力**：50 个 Skill 描述全塞 Prompt → 模型注意力分散
3. **LLM 漂移**：同一 query，上下文不同时选不同 Skill

**反直觉点**：**Skill 数量 ≠ 能力**。盲目堆 Skill 反而降低可用性。

---

## Q2：四层模型具体怎么拆？

**答**：把"Agent 怎么选 Skill"拆成 4 层独立优化：

| 层 | 问题 | 失败模式 | 优化手段 |
|---|------|---------|---------|
| **L1 描述层** | Skill 的"自我介绍"清不清楚？| 描述雷同 / 关键词缺失 | YAML frontmatter + when_not_to_use |
| **L2 路由层** | Agent 用什么逻辑选？| LLM 漂移 / 向量召回错 | **规则 + LLM 兜底** |
| **L3 加载层** | Skill 上下文怎么进 Prompt？| Token 爆炸 / 上下文污染 | **分层加载**（描述→摘要→全量）|
| **L4 评估层** | 怎么知道命中率真实水平？| 无埋点 / 无回归 | **离线评测集**（≥50 query）|

**关键 trade-off**：
- **L1 + L2** 是基础（80% 命中率靠这两层）
- **L3** 决定能不能 scale 到 50+ Skill
- **L4** 是长期保障（没有 L4 = 盲飞）

---

## Q3：规则路由 vs LLM 自由选择，怎么选？

**答**：**规则 + LLM 兜底**，不要单押 LLM 自由选择。

| 方案 | 命中率 | 维护成本 | 稳定性 |
|------|-------|---------|-------|
| **纯 LLM 自由选** | 70-80% | 零维护 | 漂移 |
| **纯规则路由** | 85-90% | 高（每 Skill 写规则）| 极稳 |
| **规则 + LLM 兜底**（推荐）| **90-95%** | 中（30 条规则覆盖 80% 长尾给 LLM）| 稳定 |

**关键技巧**：
- 规则覆盖 30-50 个高频关键词 → 直接选 Skill
- 不命中 → 给 LLM "Skill 列表 + 拒识选项" → 让 LLM 选或返回 SKIP
- **必须有"明确拒识"路径**：让 LLM 能说"都不匹配"，避免乱猜

---

## Q4：五大反模式怎么避？

**答**：

| 反模式 | 症状 | 修复 |
|--------|------|------|
| **关键词冲突** | 两个 Skill 都有"API"→ 选错 | 差异化动词 + 对象 |
| **描述雷同** | 两个 Skill 干的事差不多 | 合并 / 明确分工边界 |
| **上下文污染** | Skill 命中后塞无关工具说明 | 只注入入口 + 第一性原理 |
| **LLM 选择漂移** | 同一 query 不同上下文选不同 | 强制规则写进 description 第一句 |
| **Skill 数量爆炸** | 50+ Skill 谁也用不清 | 合并 + 分层 + 退役机制 |

**最严重的反模式是数量爆炸**——3 个月没人用的 Skill 一定要归档，否则 Prompt 会越来越胖。

---

## Q5：怎么量化命中率？没有评测集怎么办？

**答**：**先建 50 条最小评测集**。

**最小可行步骤**：
1. 收集 50 个真实用户 query（从历史日志抽）
2. 人工标注"应该命中的 Skill"（1 人花 1 天）
3. 跑 Agent 100 次（每个 query 跑 2 次，看稳定性）
4. 用另一个 LLM 做 judge（"Agent 选的 Skill 对不对？"）
5. 计算命中率 = 选对次数 / 总次数

**进阶**：跑回归
- 每次 Skill 增删前后跑评测集
- 命中率退化 > 2% → 必须回滚
- 持续 3-6 个月 → 命中率稳定在 90%+

**没有量化 = 没有优化**。面试答不出"我们命中率 92%" = 工程化不达标。

---

## 总结：面试答这题的 3 层结构

**30 秒简版**：
> "Skill 数量从 5 涨到 50，命中率会非线性退化。我们的解法是四层模型——**L1 写好描述**（YAML + when_not_to_use）、**L2 规则+LLM 兜底**、**L3 分层加载**（描述→摘要→全量）、**L4 离线评测集**（≥50 query 跑回归）。通过这套方法把命中率从 65% 拉到 92%。"

**60 秒扩展版**（如果面试官追问细节）：
> "具体来说，我们建了 50 条评测集做 baseline（命中率 65%），然后审计描述层——18 个 Skill 有冲突，合并 5 个、退役 3 个、重写 10 个，命中率到 74%。接着引入规则路由——30 条关键词映射兜 80% 长尾，剩余给 LLM 选但必须有明确拒识路径，命中率到 85%。最后分层加载——默认只注入描述，命中后按需 `load_skill_full`，Token 成本降 60%。"
>
> "避坑上，**最关键的是 L4 评测集**。没评测集就是盲飞——你不知道命中率真实水平，每次改 Skill 都赌运气。我们现在每次改 Skill 跑回归，命中率退化 > 2% 直接回滚。"

---

## 相关章节

**主模块**：
- [Skill 命中率深度章节](../../../11.ai/03-engineering/claude-code-practices/skill-hit-rate.md) — 四层模型 + 五大反模式 + 实战案例
- [Skill 设计方法论深度章节](../../../11.ai/03-engineering/claude-code-practices/skill-design.md) — 「写」的姐妹篇：决策树 + 6 字段 + YAML 模板
- [Claude Code 大型代码库实践](../../../11.ai/03-engineering/claude-code-practices/README.md) — Skill 的"渐进式披露"基础
- [Harness Engineering 概念辨析](../harness-engineering/README.md) — 上下文工程总论

**同栏目（11.ai 高频面试题）**：
- [Skill 从 0 到 1 怎么设计？](../skill-design/README.md) — 「写」的面试题（决策树 + 6 字段 + 测试）
- [为什么 Claude Code 放弃了 RAG？](../claude-code-agentic-search/README.md) — Agentic Search 取代 RAG
- [Harness Engineering 是什么？](../harness-engineering/README.md) — Harness 体系
- [Context Engineering 怎么做？](../context-engineering-interview/README.md) — Token 预算
- [Function Calling 怎么设计？](../function-calling/README.md) — 工具调用工程化

**叙事层（12.story）**：
- [扩招 50 个厨师：Skill 调度的餐厅隐喻](../../../12.story/45-skill-scheduling-restaurant.md) — 餐厅叙事版

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · skill-hit-rate](../README.md)
