<!--
module:
  parent: ai
  slug: ai/08-llmops/agent-evaluation
  type: deep-dive
  category: Agent 评测
  summary: Agent Evaluation 评测系统设计 —— 6 大评测指标（任务完成率/步骤效率/工具使用/成本/满意度/稳定性）+ 5 种评测方法 + 阿里一面实战 + 7 反模式
-->

# Agent Evaluation（评测系统）· 完整落地方案

> **一句话答案**：Agent Evaluation = **6 大评测维度（任务完成率 / 步骤效率 / 工具使用 / 成本 / 满意度 / 稳定性）+ 5 种评测方法（自动化指标 / 黄金集 / LLM-as-Judge / A/B Test / 用户模拟）+ 持续集成 + 7 反模式**。

← [返回: LLMOps](../README.md) · 兄弟：[LLM 评估](../04-llm-evaluation/README.md) · 面试题：[13.split-hairs Agent 性能评估](../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)

---

## 🆕 新增专章

### 专题 09 · Agent A/B Test 系统设计（独立深度专章）

**位置**：[02-ab-testing-design/README.md](02-ab-testing-design/README.md)

**一句话**：**AI 场景 A/B Test = 多指标 + 流量分层 + 离线/在线双轨 + 显著性检验 + 自动决策**——5 大组件 + 4 流量分配 + Bonferroni/Sequential 检验 + 5/10/50/100 灰度 + 3 OSS 实战 + 6 大监控指标。

**适用场景**：新 Planner / Prompt / Model 版本上线 A/B 对照。

**面试速查版**：[13.split-hairs · agent-ab-testing](../../../13.split-hairs/11.ai/agent-ab-testing/README.md)

---

## 0. 面试高频拷问

```
阿里一面：如果让你设计一个 Agent Evaluation（评测系统），你会如何设计
         评测指标与评测流程？
```

**回答框架（4 层递进）**：

1. **场景区分**：Agent 是多步任务（vs LLM 单次调用）—— 6 大评测维度
2. **核心方法**：5 种评测方法组合（自动化 + LLM-as-Judge + 用户模拟）
3. **持续流程**：黄金集 + CI 集成 + 漂移检测 + 灰度发布
4. **反模式**：单一指标 / 离线一次性 / 忽略用户

完整 5-7 道精选面试题见 [13.split-hairs/11.ai/agent-performance-evaluation](../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)。

---

## 1. Agent 评测 vs LLM 评测

| 维度 | LLM 评测（已有）| **Agent 评测（本专题）** |
|------|----------------|----------------------|
| 输入 | 单次 prompt | 多轮 / 多工具调用 |
| 输出 | 文本响应 | **多个 + 工具 + 状态** |
| 评估 | 输出文本质量 | **任务完成度 + 步骤 + 工具 + 成本** |
| 难度 | 中（5 方法）| **高（6 维 + 5 方法 + 流程）** |
| 典型 | BLEU / GPT-judge | **任务完成率 / 工具选择准确率 / TS / 用户满意度** |

**核心区别**：Agent 是**多步任务 + 工具调用 + 状态维护**——LLM 评测那套"GPT-judge 输出文本质量"不够，必须有 **任务级别的成功判官**。

---

## 2. 6 大评测维度

| # | 维度 | 核心指标 | 评估方式 | 重要性 |
|---|------|----------|----------|--------|
| 1 | **任务完成率** | 任务成功率 / 部分完成率 | 黄金集 + 自动化断言 | ⭐⭐⭐⭐⭐ |
| 2 | **步骤效率** | 平均步骤数 / 完成率 / 步数方差 | Trajectory 分析 | ⭐⭐⭐⭐ |
| 3 | **工具使用** | 工具选择准确率 / 调用错误率 / 参数错误率 | Tool log + 断言 | ⭐⭐⭐⭐ |
| 4 | **成本** | 单任务 token / 任务成本 / ROAS | Token 统计 | ⭐⭐⭐ |
| 5 | **满意度** | 用户评分 / CSAT / NPS | 用户反馈 | ⭐⭐⭐⭐ |
| 6 | **稳定性** | 同任务多次成功率方差 / 异常退出率 | A/B + 多次跑 | ⭐⭐⭐ |

详细见 [01-six-metrics.md](01-six-metrics.md)。

### 2.1 6 维评分函数示例

```python
def agent_score(trajectory, outcome, cost, feedback):
    return (
        0.40 * task_completion(outcome)        # 任务完成
        + 0.20 * step_efficiency(trajectory)    # 步骤效率
        + 0.10 * tool_accuracy(trajectory)     # 工具使用
        + 0.10 * cost_score(cost, SLA)          # 成本
        + 0.15 * user_satisfaction(feedback)    # 满意度
        + 0.05 * stability_score(trajectory)    # 稳定性
    )
```

---

## 3. 5 种评测方法

| # | 方法 | 适用 | 成本 |
|---|------|------|------|
| 1 | **自动化指标** | 任务成功率 / 工具调用正确性 | 低 |
| 2 | **黄金集评估** | 已知正确答案场景 | 中 |
| 3 | **LLM-as-Judge** | 开放式输出 / Agent 整体行为 | 中高 |
| 4 | **A/B Test** | 生产环境对比 | 高 |
| 5 | **用户模拟** | 大规模并发压测 | 中高 |

详细见 [02-five-methods.md](02-five-methods.md) + [03-llm-as-judge.md](03-llm-as-judge.md)。

---

## 4. 评测流程全景

```
┌──────────────────────────────────────────────────────────┐
│  1. 黄金集构建（离线）                                    │
│     - 真实业务场景 50-200 条                             │
│     - 已知期望输出 + 期望工具调用                        │
│     - 期望失败用例（边缘 case）                           │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│  2. 离线评估（CI 集成）                                   │
│     - 自动化指标 + LLM-as-Judge                         │
│     - 报告：每维度得分 + 失败样本                        │
│     - 阈值：score ≥ 0.85 通过，否则阻塞发布             │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│  3. 在线 A/B Test                                         │
│     - 新版本 5% 流量                                     │
│     - 监控 6 维指标                                      │
│     - 7 天无显著差异 → 全量                              │
└────────────────────┬─────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────┐
│  4. 用户模拟（回归测试）                                   │
│     - 用 LLM 模拟 1000 用户并发                          │
│     - 跑全量黄金集                                       │
│     - 输出：成功率 + P99 延迟 + 成本                       │
└──────────────────────────────────────────────────────────┘
```

详细见 [04-evaluation-pipeline.md](04-evaluation-pipeline.md)。

---

## 5. 子章节导航

### 系列文章（扁平 .md 文件）

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [6 大评测维度](01-six-metrics.md) | 任务完成率 / 步骤效率 / 工具使用 / 成本 / 满意度 / 稳定性 详解 |
| 02 | [5 种评测方法](02-five-methods.md) | 自动化指标 / 黄金集 / LLM-as-Judge / A/B / 用户模拟 |
| 03 | [LLM-as-Judge 详解](03-llm-as-judge.md) | LLM 当裁判的 4 大维度 + 5 反模式 |
| 04 | [评测流程](04-evaluation-pipeline.md) | 黄金集 → CI 自动化 → A/B → 用户模拟完整 pipeline |
| 05 | [阿里一面实战话术](05-ali-interview.md) | 阿里一面原题回答 + 5 反模式 |
| 06 | [7 大反模式](06-seven-anti-patterns.md) | 单一指标 / 离线一次性 / 忽略工具错误 等 |
| 07 | [选型决策树](07-selection-decision-tree.md) | 按阶段 / 团队 / 预算选评测方案 |
| 08 | [实战案例 + CI/CD](08-practical-cases.md) | 客服 Agent / 代码生成 Agent 评估实战 + CI/CD 配置 + 报告模板 |

### 深度专章（子目录）

| 专章 | 目录 | 核心问题 |
|------|------|---------|
| Agent A/B Test 系统设计 | [02-ab-testing-design/](02-ab-testing-design/README.md) | 多指标 + 流量分层 + 离线/在线双轨 + 显著性检验 + 自动决策 |
| 🆕 RAG 评估 | [09-rag-evaluation/](09-rag-evaluation/README.md) | RAGAS / TruLens / DeepEval 3 大工具横评 + 检索质量 + 生成质量指标 + 黄金集最佳实践 |

> 💡 **编号说明**：系列文章（01-08）为扁平 `.md` 文件，深度专章为独立子目录。`02-ab-testing-design/` 与 `02-five-methods.md` 共用编号 02 但属于不同类型（目录 vs 文件），不会冲突。

---

## 6. 反直觉点

- ⚠️ **"Agent 评测 = LLM 评测"是错觉** —— Agent 是多步任务，必须有 **trajectory + task-level** 评估
- ⚠️ **"GPT-4 Judge 就够"是错觉** —— LLM-as-Judge 有偏见（位置偏好 / 长度偏好），必须 **多模型投票**
- ⚠️ **"一次性评估就够"是错觉** —— Agent 行为有漂移，需 **持续监控 + 漂移告警**
- ⚠️ **"任务成功率就是一切"是错觉** —— 需 **多维度**（效率 / 工具 / 成本）——成功但极慢也不可用

---

## 7. 一句话速查

```
Agent Evaluation 公式：
  Score = 0.4 任务完成率 + 0.2 步骤效率 + 0.1 工具准确 + 0.1 成本 + 0.15 满意度 + 0.05 稳定性
评测流程：黄金集（500 条）→ 自动化 CI 评估 → A/B Test → 用户模拟
关键方法：5 种组合（自动化 + 黄金集 + LLM-as-Judge + A/B + 用户模拟）
反模式：单一指标 / 离线一次性 / 忽略工具错误 / 没用黄金集 / 没 CI 集成
```

---

## 8. 速查 · 关联资源

- **LLM 评估**：[LLM 单次调用评估](../04-llm-evaluation/README.md) —— 331 行深度
- **面试题**：[13.split-hairs/11.ai/agent-performance-evaluation](../../13.split-hairs/11.ai/agent-performance-evaluation/README.md) —— 7 道精选 Q&A
- **真实案例**：[05-applications/case-studies/10-salesforce-agentforce/](../05-applications/case-studies/10-salesforce-agentforce/README.md) —— Salesforce Agentforce 评测实践
- **生产级 Agent**：[03-engineering/production-agent/](../03-engineering/production-agent/README.md) —— Shopify Sidekick 评测流程

---

← [返回: LLMOps](../README.md)
