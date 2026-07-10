<!--
module:
  parent: ai
  slug: ai/05-agent-evaluation/08-practical-cases
  type: article
  category: Agent 评测实战
  summary: Agent 评测实战案例：客服 Agent 评估体系搭建 + 代码生成 Agent 评估 + CI/CD 集成 + 评估报告模板
-->

# Agent 评测实战案例 + CI/CD 集成

> 本篇是 [Agent Evaluation 系列](README.md) 的实战补充，聚焦 **真实案例** + **CI/CD 配置** + **评估报告模板**。

← [返回: Agent Evaluation 总目录](README.md)

---

## 1. 案例 1：客服 Agent 评估体系搭建

**背景**：某电商公司搭建客服 Agent，处理订单查询、退款、投诉。

### 1.1 评估体系设计

```text
黄金集：50 条（10 查询 + 20 退款 + 20 投诉）
LLM-as-Judge：GPT-4（Cohen's Kappa 0.68）
用户模拟：100 场景
人工抽检：每月 100 条
A/B Test：新版本上线前
```

### 1.2 各维度指标详解

#### 任务完成度

| 任务类型 | 成功率 | 评估 |
|---------|--------|------|
| 查询订单（简单） | 95% | 达标 |
| 退款申请（中等） | 78% | 需优化 |
| 投诉处理（复杂） | 62% | 不达标 |
| **加权平均** | **78%** | 接近阈值 |

**关键洞察**：
- 简单任务成功率应 > 95%
- 复杂任务成功率 > 70% 即可接受
- 复杂任务 < 50% 说明 Agent 设计有问题

#### 步骤效率

```text
任务：查询订单状态

Agent A（DAG 模式）：
Step 1: 意图识别 → 订单查询
Step 2: 调用 get_order API
Step 3: 格式化输出
总步数：3 步

Agent B（ReAct 模式）：
Step 1: 思考 → 需要查询订单
Step 2: 调用 get_order API
Step 3: 观察 → 订单状态已支付
Step 4: 思考 → 需要返回给用户
Step 5: 返回结果
总步数：5 步

最优步数比：A = 3/3 = 1.0，B = 5/3 = 1.67
```

- DAG 模式通常比 ReAct 步骤效率更高
- 最优步数比 > 2.0 说明 Agent 在"绕路"

#### 工具使用效果

```text
Agent 有 10 个工具，月度统计：

工具                调用次数  成功率  选择准确率
───────────────  ────────  ──────  ──────────
search_orders       500      98%     95%
get_order_detail    450      99%     97%
refund_request      120      85%     88%  ← 成功率低
send_email          80       92%     90%

整体工具成功率：94%
整体工具选择准确率：93%
```

- 工具成功率 < 90% → 检查 API 稳定性
- 工具选择准确率 < 85% → 检查工具描述

#### 成本效益

```text
月度成本分析：
总任务数：10,000
总 Token 消耗：50,000,000
总成本：$5,000

单任务成本：$0.5
Token 效率：5000 Token / 任务

任务价值估算：
- 每个任务节省人工客服 10 分钟
- 人工客服成本：$0.5 / 分钟
- 每任务价值：$5
成本效益比：$5 / $0.5 = 10 ✅
```

### 1.3 优化效果（3 个月）

```text
初始版本：
  - 任务成功率：68%
  - 工具选择准确率：82%
  - 平均成本：$0.85 / 任务

优化后：
  - 任务成功率：85%（+17%）
  - 工具选择准确率：93%（+11%）
  - 平均成本：$0.42 / 任务（-50%）

优化手段：
  - 重写工具描述（工具选择准确率 +11%）
  - 加分支逻辑（复杂任务成功率 +15%）
  - Prompt 压缩（成本 -50%）
```

---

## 2. 案例 2：代码生成 Agent 评估

**背景**：某公司搭建代码生成 Agent（类似 GitHub Copilot）。

### 2.1 评估维度

```text
任务完成度：代码能跑通吗？
步骤效率：生成代码用了多少步？
工具使用效果：调用了多少次 LLM？
成本效益：每次代码生成成本多少？
用户满意度：开发者接受率多少？
稳定性：同一任务跑 10 次，结果一致吗？
```

### 2.2 评估结果

```text
黄金集：100 个编程任务
任务成功率：78%
平均步数：2.3 步
平均成本：$0.15 / 次
开发者接受率：82%
一致率：95%（temperature=0.2）
```

---

## 3. CI/CD 集成

### 3.1 GitHub Actions 配置

```yaml
# .github/workflows/agent-eval.yml
name: Agent Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Agent Evaluation
        run: |
          python eval/run_eval.py \
            --goldset=eval/goldset.json \
            --output=eval/results.json
      - name: Check Thresholds
        run: |
          python eval/check_thresholds.py \
            --results=eval/results.json \
            --min-success-rate=0.85 \
            --min-tool-accuracy=0.90
```

### 3.2 GitLab CI 配置

```yaml
# .gitlab-ci.yml
stages:
  - eval
  - test
  - deploy

agent-eval:
  stage: eval
  script:
    - python eval/run_goldset.py --goldset=eval/goldset.json
    - python eval/run_llm_judge.py --samples=50
    - python eval/check_thresholds.py \
        --min-success-rate=0.85 \
        --min-tool-accuracy=0.90 \
        --max-cost-per-task=0.5
  artifacts:
    paths:
      - eval/results/

load-test:
  stage: test
  script:
    - locust -f eval/load_test.py -u 100 -r 10 --run-time 5m
  only:
    - main

deploy:
  stage: deploy
  script:
    - ./deploy.sh
  only:
    - main
  when: on_success
```

---

## 4. 评估报告模板

```text
Agent 评估报告（2026-07-06）
─────────────────────────────────

黄金集评估（50 条）：
  - 任务成功率：88%（阈值 85%）✅
  - 工具选择准确率：93%（阈值 90%）✅
  - 平均步数：4.2 步
  - 平均成本：$0.42 / 任务（阈值 $0.5）✅

LLM-as-Judge（50 条抽样）：
  - 任务完成度：8.5 / 10
  - 输出质量：8.2 / 10
  - 步骤效率：7.8 / 10
  - 成本控制：8.0 / 10

人工抽检（20 条）：
  - 任务完成度：4.3 / 5
  - 输出质量：4.1 / 5
  - Cohen's Kappa（vs LLM Judge）：0.72 ✅

性能压测：
  - P50 延迟：1.2s
  - P99 延迟：4.5s
  - QPS：50

成本分析：
  - 日均任务数：10,000
  - 日均成本：$4,200
  - 成本效益比：12（任务价值 $5 / 成本 $0.42）

结论：
  ✅ 所有指标达标，建议上线
```

---

## 5. 黄金集 JSON 示例

```json
{
  "test_cases": [
    {
      "id": "order-query-001",
      "task": "查询订单 20260706 的状态",
      "expected_output": "订单 20260706 状态：已支付",
      "expected_steps": 3,
      "expected_tools": ["get_order"],
      "tags": ["简单任务", "订单查询"]
    },
    {
      "id": "refund-001",
      "task": "帮我申请退款，订单号 20260705",
      "expected_output": "退款申请已提交，预计 3 个工作日到账",
      "expected_steps": 5,
      "expected_tools": ["get_order", "check_refund_eligibility", "submit_refund"],
      "tags": ["中等任务", "退款"]
    }
  ]
}
```

---

## 相关章节

- [6 大评测维度](01-six-metrics.md)
- [5 种评测方法](02-five-methods.md)
- [评测流程](04-evaluation-pipeline.md)
- [7 大反模式](06-seven-anti-patterns.md)

---

← [返回: Agent Evaluation 总目录](README.md) · 📅 2026-07-10
