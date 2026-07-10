<!--
module:
  parent: ai/05-agent-evaluation
  slug: ai/05-agent-evaluation/03-llm-as-judge
  type: topic
  category: LLM-as-Judge
  summary: LLM-as-Judge 详解 —— Judge 4 大维度 + 多模型投票 + 5 反模式
-->

# LLM-as-Judge · GPT-4 当 Agent 裁判

> **一句话**：LLM-as-Judge = 用 GPT-4/Claude 当裁判评估 Agent 输出——但**单一 Judge 有偏见**（位置偏好 / 长度偏好），必须 **多模型投票 + 截尾均值** + 5 反模式。

← [返回: Agent Evaluation 总目录](../README.md)

---

## 1. LLM-as-Judge 4 大评估维度

| 维度 | 评估内容 | 重要性 |
|------|----------|--------|
| **1 任务完成度** | Agent 是否真正完成任务 | ⭐⭐⭐⭐⭐ |
| **2 输出质量** | 结构 / 准确 / 完整 / 逻辑 | ⭐⭐⭐⭐ |
| **3 工具使用** | 工具选对 + 参数正确 + 调用顺序 | ⭐⭐⭐ |
| **4 鲁棒性** | 异常处理 / 边界情况 | ⭐⭐⭐ |

---

## 2. Judge Prompt 模板

### 2.1 基础模板

```python
JUDGE_PROMPT_BASIC = """
你是资深 {领域} 评估专家。请评估以下 Agent 输出：

【任务】
{original_task}

【Agent 输出】
{agent_output}

【参考输出】
{reference}

【评估维度】（10 分制）
1. 任务完成度（40%）：任务是否完成 / 完成度如何
2. 输出质量（30%）：结构 / 准确 / 完整
3. 工具使用（20%）：工具选择正确 / 参数无误
4. 鲁棒性（10%）：异常处理 / 边界处理

【输出格式】
- 每维度评分（0-10）+ 理由
- 总分（加权）
- 改进建议
"""
```

### 2.2 Agent 特有模板（含 trajectory 分析）

```python
JUDGE_PROMPT_AGENT = """
你是 Agent 行为评估专家。请评估以下 Agent 的 trajectory：

【用户任务】
{task}

【Agent Trajectory】
{trajectory.steps}  # 含 Thought / Action / Observation

【评估维度】

1. **任务完成度**：最终输出是否完成任务
2. **思维质量**：每一步的 Thought 是否合理
3. **工具选择**：每个 Action 选的工具是否对
4. **响应观察**：是否合理处理 Observation
5. **效率**：步骤数 / token 是否合理

【输出格式】
- 每维度 0-10 分
- 失败步骤定位（哪一步错了）
- 改进建议
"""
```

---

## 3. 5 大反模式（必避）

### ⚠️ 反模式 1：单一 LLM 评判（最常见）

- **错**：只用 GPT-4 当 judge
- **真**：GPT-4 有位置偏好（喜欢第一个）+ 长度偏好（喜欢长答）
- **改**：**多模型投票 + 截尾均值**

```python
# 错：单一 Judge
score_gpt4 = gpt4_judge(...)

# 对：多模型投票
def multi_judge(trajectory, judges):
    scores = [judge(trajectory) for judge in judges]  # 3-5 个模型
    scores.sort()
    # 去掉最高最低 → 平均（截尾均值）
    return sum(scores[1:-1]) / (len(scores) - 2)
```

### ⚠️ 反模式 2：Judge Prompt 太简单

- **错**："请评估这个回答"
- **对**：明确维度 + 评分标准 + 输出格式

### ⚠️ 反模式 3：Judge 用了被测模型的输出训练

- **错**：用 GPT-4 judge GPT-4 输出（同源偏见）
- **对**：跨模型 judge（GPT-4 judge Claude / 反之）

### ⚠️ 反模式 4：Judge 没有 ground truth

- **错**：纯主观判断
- **对**：提供 reference output，Judge 对比判断

### ⚠️ 反模式 5：Judge 自己也错了

- **错**：完全信任 Judge 输出
- **对**：人工抽查 10% Judge 输出

---

## 4. 实战配置

```python
JUDGE_CONFIG = {
    'judges': ['gpt-4-turbo', 'claude-3-opus', 'gemini-1.5-pro'],
    'rubric': JUDGE_PROMPT_AGENT,
    'aggregation': 'trimmed_mean',  # 截尾均值
    'human_sample_rate': 0.1,  # 10% 人工抽检
    'cost_per_eval': 0.05,  # 美元
}
```

---

## 5. 一句话总结

> **LLM-as-Judge = 用强 LLM 当裁判，4 大维度（任务 / 输出 / 工具 / 鲁棒），多模型投票 + 截尾均值避免偏见，5 反模式必避（单一 Judge / Prompt 简单 / 同源 / 无 ground truth / 不抽检）。**

---

← [返回: Agent Evaluation 总目录](../README.md) · 上一章：[02-five-methods](02-five-methods.md) · 下一章：[04-evaluation-pipeline](04-evaluation-pipeline.md)
