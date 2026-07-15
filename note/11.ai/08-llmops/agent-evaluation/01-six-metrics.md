<!--
module:
  parent: ai/08-llmops/agent-evaluation
  slug: ai/08-llmops/agent-evaluation/01-six-metrics
  type: topic
  category: 6 大评测维度
  summary: 6 大评测维度详解 —— 任务完成率 / 步骤效率 / 工具使用 / 成本 / 满意度 / 稳定性
-->

# 6 大评测维度 · Agent 性能量化

> **一句话**：Agent 评测不是"完成率一个指标"——必须 **6 维度量化**（任务 / 步骤 / 工具 / 成本 / 满意度 / 稳定性），每个维度有具体公式与可操作阈值。

← [返回: Agent Evaluation 总目录](../README.md)

---

## 1. 维度 1：任务完成率（最重要）

**核心问题**：Agent 真的完成任务了吗？

### 1.1 公式

```
完成率 = 完成的任务数 / 总任务数

分类：
- 完全完成（全对）：成功
- 部分完成（结果存在但不完美）：半成功
- 完全失败：失败

最终指标 = (完全完成 × 1.0 + 部分完成 × 0.5) / 总任务数
```

### 1.2 评估方式

```python
# 黄金集 + 自动化断言
def task_completion(task, agent_output):
    # 1. 结构化输出检查（JSON Schema）
    if not matches_schema(agent_output, task.expected_schema):
        return 0.0
    
    # 2. 内容匹配（核心字段）
    score = 0.0
    for field, expected in task.expected.items():
        if fuzzy_match(agent_output.get(field), expected):
            score += 1.0 / len(task.expected)
    
    # 3. 部分完成判定（关键字段缺失 = 部分）
    if score < 0.6:
        return 0.0  # 完全失败
    elif score < 1.0:
        return 0.5  # 部分完成
    else:
        return 1.0  # 完全完成
```

---

## 2. 维度 2：步骤效率

**核心问题**：Agent 完成任务的效率如何？

### 2.1 公式

```
步骤效率 = 最优步骤数 / 实际步骤数
           ↑
           baseline（理想情况）

例如：
- 任务"订机票"理论上 5 步（搜 → 比较 → 选 → 支付 → 确认）
- Agent 用了 12 步
- 效率 = 5 / 12 = 0.42
```

### 2.2 评估方式

```python
def step_efficiency(trajectory):
    optimal_steps = task.optimal_step_count  # 人工标注
    actual_steps = len(trajectory.steps)
    
    # 防止除零 + 平滑曲线
    return optimal_steps / max(actual_steps, optimal_steps * 2)
```

**反模式**：
- ⚠️ 死循环检测（最大 50 步超时）
- ⚠️ 重复步骤检测（去重后再算）

---

## 3. 维度 3：工具使用准确率

**核心问题**：Agent 选工具 + 用工具对不对？

### 3.1 公式

```
工具准确率 = 正确的工具调用 / 总工具调用

分类：
- 工具选择正确 ✅
- 工具选择错误，但能从错误中恢复 ⚠️（部分）
- 工具选择错误，无法恢复 ❌（失败）

参数准确率 = 参数完全正确的工具调用 / 总工具调用
```

### 3.2 评估方式

```python
def tool_accuracy(trajectory, expected_tools):
    correct = 0
    for call in trajectory.tool_calls:
        if call.tool_name == expected_tools[call.step_id]:
            correct += 1
    return correct / len(trajectory.tool_calls)

def param_accuracy(trajectory, expected_params):
    correct = 0
    for call in trajectory.tool_calls:
        if call.params == expected_params[call.step_id]:
            correct += 1
    return correct / len(trajectory.tool_calls)
```

---

## 4. 维度 4：成本（Token / $）

**核心问题**：任务成本是否在 SLA 内？

### 4.1 公式

```
单任务成本 = input_tokens × input_price + output_tokens × output_price

总成本 = Σ 所有任务成本
单次任务平均 = 总成本 / 任务数
```

### 4.2 阈值

| 场景 | 成本上限 |
|------|----------|
| 客服 Agent | < $0.05/次 |
| 代码助手 | < $0.50/次 |
| 研究 Agent | < $2.00/次 |
| 文档分析 | < $0.10/次 |

**反模式**：
- ⚠️ 不监控成本 → 一次大任务可以烧 $100
- ⚠️ 压缩 token 数 → 影响质量

---

## 5. 维度 5：满意度

**核心问题**：用户对 Agent 满意吗？

### 5.1 公式

```
CSAT = 满意用户数 / 总用户数 × 100%

Net Promoter Score (NPS):
  推荐者 (9-10) % - 贬损者 (0-6) %
```

### 5.2 评估方式

```python
# 方式 1：用户评分（主动）
def collect_user_rating(session_id):
    return send_survey("1-5 星", session_id)

# 方式 2：行为推断（被动）
def infer_satisfaction(session):
    # 用户多次追问 → 不满意
    # 用户立刻关闭 → 可能不满意
    # 用户点赞 / 反馈 → 满意
    if session.repeat_queries > 3:
        return "dislike"
    if session.duration < 5 and session.goal_completed:
        return "satisfy"
```

---

## 6. 维度 6：稳定性

**核心问题**：同样任务，不同次跑，结果一致吗？

### 6.1 公式

```
成功率方差 = Var([任务 t1 跑 10 次的成功率, 任务 t2 跑 10 次的成功率, ...])

异常退出率 = 异常退出（OOM / 工具超时）次数 / 总次数

稳定性 = 1 - 异常退出率 - 0.5 × 成功率方差
```

### 6.2 评估方式

```python
def stability(task):
    runs = []
    for _ in range(10):
        result = await agent.run(task)
        runs.append(result.success)
    success_rate = sum(runs) / 10
    return success_rate  # 理想 ≥ 0.95
```

---

## 7. 6 维综合评分函数

```python
class AgentEvaluator:
    weights = {
        'task_completion': 0.40,   # 最重要
        'step_efficiency': 0.20,
        'tool_accuracy': 0.10,
        'cost': 0.10,
        'satisfaction': 0.15,
        'stability': 0.05,
    }
    
    def evaluate(self, run_result):
        scores = {
            'task_completion': self.task_score(run_result),
            'step_efficiency': self.efficiency_score(run_result),
            'tool_accuracy': self.tool_score(run_result),
            'cost': self.cost_score(run_result),
            'satisfaction': self.csat_score(run_result),
            'stability': self.stability_score(run_result),
        }
        # 加权
        final = sum(scores[k] * self.weights[k] for k in scores)
        return final, scores
```

**生产阈值**：
- 通过：`final ≥ 0.80` 且 `task_completion ≥ 0.85`
- 灰度：`0.70 ≤ final < 0.80`
- 阻塞：`final < 0.70`

---

## 8. 6 维反模式 · 5 个常见错

### ⚠️ 反模式 1：只看任务完成率

- 错：完成率 100% 但每任务 50 步 / $5
- 对：6 维加权，效率 + 成本 + 体验同样重要

### ⚠️ 反模式 2：用绝对数字（无 baseline）

- 错："完成率 80%"
- 对：跟上次版本 / 竞品对比（+5% 算进步）

### ⚠️ 反模式 3：忽略用户感知

- 错：任务成功但用户觉得"agent 笨"
- 对：CSAT + NPS + 行为推断综合

### ⚠️ 反模式 4：一次性评估（无 CI 持续）

- 错：发版前跑一次评测就发布
- 对：每次 PR 触发 + 灰度 + 全量

### ⚠️ 反模式 5：评测集太"干净"

- 错：黄金集全是 happy path
- 对：注入对抗样本 + 模糊 query + 缺失字段

---

## 9. 一句话总结

> **Agent 6 大评测维度：40% 任务完成率 + 20% 步骤效率 + 10% 工具准确率 + 10% 成本 + 15% 满意度 + 5% 稳定性。生产阈值 ≥ 0.80。5 反模式：单一指标 / 无 baseline / 忽略感知 / 一次性 / 测试集太干净。**

---

← [返回: Agent Evaluation 总目录](../README.md) · 下一章：[02-five-methods](02-five-methods.md)
