<!--
module:
  parent: ai/08-llmops/agent-evaluation
  slug: ai/08-llmops/agent-evaluation/02-five-methods
  type: topic
  category: 5 种评测方法
  summary: 5 种评测方法详解 —— 自动化指标 / 黄金集 / LLM-as-Judge / A/B Test / 用户模拟
-->

# 5 种评测方法 · Agent 评测完整工具箱

> **一句话**：Agent 评测不是单一方法——必须 **5 种方法组合**（自动化指标 + 黄金集 + LLM-as-Judge + A/B Test + 用户模拟），每种方法解决不同维度的问题。

← [返回: Agent Evaluation 总目录](../README.md)

---

## 1. 方法 1：自动化指标（最低成本、最快）

**适用**：有明确 ground truth 的任务（订机票 / 退款 / 查数据）

```python
class AutomatedEvaluator:
    def evaluate(self, task, agent_output):
        scores = {}
        
        # 1. Schema 验证
        scores['schema'] = 1.0 if matches_schema(agent_output, task.schema) else 0.0
        
        # 2. 字段匹配
        for field, expected in task.expected.items():
            scores[f'field_{field}'] = 1.0 if agent_output.get(field) == expected else 0.0
        
        # 3. 工具调用正确性
        for call in agent_output.tool_calls:
            scores[f'tool_{call.name}'] = 1.0 if matches_expected(call, task) else 0.0
        
        return scores
```

**优点**：极快（毫秒）/ 可重现 / CI 友好
**缺点**：无法评估开放式输出（如"写一段话"）

---

## 2. 方法 2：黄金集评估（离线核心）

**适用**：已知正确答案的测试集

### 2.1 构建黄金集

```python
golden_set = [
    {
        'task_id': 'qa_001',
        'input': '北京人口多少？',
        'expected': {
            'answer': '约 2000 万',  # 模糊匹配
            'tools': ['web_search'],
            'max_steps': 5,
            'max_tokens': 1000,
        },
        'category': 'simple_factual',
        'difficulty': 'easy',
    },
    # ... 500+ 条
]
```

### 2.2 评估流程

```python
def eval_golden_set(agent, golden_set):
    results = []
    for task in golden_set:
        agent_output = await agent.run(task)
        result = {
            'task_id': task['task_id'],
            'completion': task_completion(task, agent_output),
            'steps': len(agent_output.trajectory),
            'cost': agent_output.token_cost,
            'passed': task_completion(task, agent_output) >= 0.85
                    and len(agent_output.trajectory) <= task['max_steps']
                    and agent_output.token_cost <= task['max_tokens']
        }
        results.append(result)
    return aggregate(results)
```

---

## 3. 方法 3：LLM-as-Judge（GPT-4 当裁判）

**适用**：开放式输出 / Agent 整体行为评估

### 3.1 核心 Prompt 模板

```python
JUDGE_PROMPT = """你是资深 {领域} 评估专家。请评估以下 Agent 输出：

【任务】
{original_task}

【Agent 输出】
{agent_output}

【参考标准】
{reference}

【评估维度】（10 分制）
1. 任务完成度（40%）：任务是否完成
2. 输出质量（30%）：结构 / 逻辑 / 准确
3. 工具使用（20%）：选对工具 + 参数正确
4. 效率（10%）：步骤数 / token 消耗

【输出格式】
每维度评分（0-10）+ 总分 + 改进建议
"""
```

### 3.2 多模型投票（避免单一 Judge 偏见）

```python
def multi_judge(task, agent_output, judges=['gpt-4', 'claude', 'gemini']):
    scores = []
    for judge in judges:
        score = await judge_llm(judge, JUDGE_PROMPT, task, agent_output)
        scores.append(score)
    # 移除极值 + 平均
    scores.sort()
    return sum(scores[1:-1]) / (len(scores) - 2)  # 截尾均值
```

---

## 4. 方法 4：A/B Test（生产环境金标准）

**适用**：上线前 / 灰度发布

### 4.1 流量分配

```python
# 新版本 5% 流量，剩余 95% 旧版
def assign_bucket(user_id):
    bucket = hash(user_id) % 100
    return 'treatment' if bucket < 5 else 'control'
```

### 4.2 监控指标

```yaml
A/B Test 监控面板：
  treatment: 5% 流量
  control: 95% 流量
  
  primary_metric: 任务完成率
  secondary_metrics:
    - 步骤效率
    - 工具准确率
    - 成本
    - 满意度
  
  duration: 7 天
  显著性检验: p-value < 0.05
```

### 4.3 风险控制

- 灰度时间：3-7 天
- 紧急回滚：一键切换流量 100% 到 control
- Kill Switch：发现异常立即停

---

## 5. 方法 5：用户模拟（大规模压测）

**适用**：并发能力 / 极端场景 / 压力测试

### 5.1 用 LLM 模拟用户

```python
# 用 LLM 模拟 1000 个不同类型的用户
def gen_user_simulator(n=1000):
    users = []
    for _ in range(n):
        # 生成不同性格 / 任务的用户
        users.append(llm.generate(
            "生成一个用户画像：职业 / 性格 / 提问风格 / 任务目标"
        ))
    return users

async def user_simulation_test(agent, users, max_concurrent=100):
    semaphore = asyncio.Semaphore(max_concurrent)
    results = await asyncio.gather(*[
        run_with_semaphore(semaphore, agent, user) for user in users
    ])
    return aggregate(results)
```

### 5.2 评估产出

- 完成率
- P50 / P95 / P99 延迟
- 成本 per user
- 工具错误率
- 异常退出率

---

## 6. 5 种方法对比

| 方法 | 客观度 | 速度 | 成本 | 适用 |
|------|--------|------|------|------|
| **1 自动化指标** | ⭐⭐⭐⭐⭐ | 极快（ms）| 低 | 有 ground truth |
| **2 黄金集** | ⭐⭐⭐⭐⭐ | 快（s）| 中 | 离线核心测试 |
| **3 LLM-as-Judge** | ⭐⭐⭐ | 慢（s-min）| 中高 | 开放式输出 |
| **4 A/B Test** | ⭐⭐⭐⭐⭐ | 慢（天-周）| 高 | 上线决策 |
| **5 用户模拟** | ⭐⭐⭐ | 慢（min）| 中高 | 并发压测 |

**实战组合**：
- 自动化指标（80% 任务）+ 黄金集（核心场景）
- + LLM-as-Judge（开放式任务）
- + A/B Test（上线前）+ 用户模拟（压测）

---

## 7. 反模式 · 5 个常见错

### ⚠️ 反模式 1：只信赖 LLM-as-Judge

- 错：仅用 GPT-4 judge，overfit 到 GPT-4 偏好
- 对：多模型投票 + 截尾均值

### ⚠️ 反模式 2：A/B Test 时间不足

- 错：A/B 跑 1 天就下结论
- 对：≥ 7 天，覆盖工作日 / 周末 / 高峰期

### ⚠️ 反模式 3：黄金集永远不变

- 错：黄金集 1 年没更新
- 对：每月加新失败用例 → 数据漂移检测

### ⚠️ 反模式 4：自动化指标"过拟合"

- 错：黄金集全是 happy path → agent 走过拟合容易过测
- 对：注入对抗样本（乱序字段 / 模糊 query）

### ⚠️ 反模式 5：用户模拟像"机器人"

- 错：模拟用户输入完美 query
- 对：模拟真实用户的拼写错误 / 不完整描述 / 重复追问

---

## 8. 一句话总结

> **5 种方法组合 = 自动化指标（核心）+ 黄金集（核心）+ LLM-as-Judge（开放）+ A/B Test（上线）+ 用户模拟（压测）。实战 80% 自动化，20% LLM-judge 兜底。**

---

← [返回: Agent Evaluation 总目录](../README.md) · 上一章：[01-six-metrics](01-six-metrics.md) · 下一章：[03-llm-as-judge](03-llm-as-judge.md)
