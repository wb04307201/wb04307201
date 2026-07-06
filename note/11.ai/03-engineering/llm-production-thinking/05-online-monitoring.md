<!--
module:
  parent: ai/llm-production-thinking
  slug: ai/llm-production-thinking/05-online-monitoring
  type: topic
  category: 线上监控
  summary: Trace + 黄金集回归 + 漂移检测 —— 上线后准确率 / 幻觉率监控 + 5 分钟定位问题实战
-->

# 线上监控与定位 · 准确率 / 幻觉率

> **一句话**：LLM 上线只是开始——**Trace（链路追踪）+ 黄金集回归 + 漂移检测**才能在 5 分钟内定位问题（vs 数天的"昨天还好的"式排查）。

← [返回: 大模型思维工程](../README.md)

---

## 1. 为什么 LLM 上线后"灾难连连"？

**真实数据**：75% 的 LLM 产品上线 30 天内遇到"准确率下降 / 幻觉率飙升"但定位困难（Helicone 2024 报告）。

**5 大常见事故**：
1. 上游模型升级（OpenAI / Anthropic 静默更新权重）
2. Prompt 改动未回归（同事改了一个变量）
3. 用户分布漂移（新场景出现）
4. 数据漂移（外部知识库过期）
5. 第三方依赖（Embedding 模型变化影响 RAG）

---

## 2. 4 维监控体系

| 维度 | 核心指标 | 监控频率 | 工具 |
|------|---------|---------|------|
| **延迟** | P50/P95/P99 latency | 实时秒级 | Prometheus + Grafana |
| **成本** | 单请求 / 日累计 | 实时秒级 | Langfuse / Helicone |
| **质量** | 准确率 / 幻觉率 | 5 分钟 batch | 自建 / DeepEval |
| **一致性** | 重复问题答案漂移率 | 1 小时 | 自建 |

### 2.1 延迟监控（成熟方案）

```python
@track_latency(model_name="gpt-4o", endpoint="/chat")
async def invoke_llm(prompt):
    return await openai.chat(prompt)
```

```yaml
# Grafana 关键 panel
panels:
  - metric: llm_request_latency_bucket
    viz: heatmap
    filters: { model: "gpt-4o" }
  - metric: llm_request_latency_p99
    viz: timeseries
    alert: > 10000  # 10s 告警
```

### 2.2 成本监控（已在第 2 章覆盖）

见 [02-cost-control](02-cost-control-and-degradation.md) — 5 层路由 + 3 道 quota。

### 2.3 质量监控（重点）

**准确率**：人工标注 100 query 黄金集，每 5 分钟跑一次
**幻觉率**：用 RAGAS / DeepEval 自动测

```python
from deepeval import evaluate
from deepeval.metrics import (
    FaithfulnessMetric,    # 幻觉检测
    AnswerRelevancyMetric, # 相关性
    ContextualPrecisionMetric,
)

results = evaluate(
    gold_dataset,        # 50-200 条人工标注 query + 期望答案
    metrics=[
        FaithfulnessMetric(threshold=0.85),
        AnswerRelevancyMetric(threshold=0.80),
    ],
)
```

### 2.4 一致性监控

```python
def consistency_check(query, sample_count=3):
    """同一问题问 3 次，结果应相似"""
    samples = [llm.invoke(query, temperature=0.7) for _ in range(sample_count)]
    
    # 用 embedding 计算平均相似度
    embeddings = [embed(s) for s in samples]
    avg_sim = average_pairwise_cosine(embeddings)
    
    return {
        "consistency_score": avg_sim,
        "alert": avg_sim < 0.7,  # 低于阈值告警
    }
```

---

## 3. Trace 链路追踪（5 分钟定位必备）

### 3.1 Langfuse / Helicone / Phoenix

| 工具 | 类型 | 特点 |
|------|------|------|
| **Langfuse** | 开源 + SaaS | 完整 Trace + 评估 + 黄金集管理 |
| **Helicone** | SaaS | 集成 5 行代码，即开即用 |
| **Phoenix (Arize)** | 开源 | LLM 专精的可观测性平台 |
| **OpenLLMetry** | 开源 | OpenTelemetry 扩展 |

### 3.2 典型 Trace 结构

```
[1] POST /chat (总延迟 1200ms)
   ├─ [2] RAG retrieve (50ms) - top_k=10
   │   └─ embedding (30ms)
   │   └─ vector search (20ms)
   ├─ [3] LLM invoke (1000ms) - gpt-4o
   │   ├─ prompt_tokens: 850
   │   ├─ completion_tokens: 200
   │   └─ cost: $0.015
   ├─ [4] Re-rank (100ms) - cross-encoder
   └─ [5] Format output (50ms)
```

### 3.3 5 分钟定位实战

**场景**：用户反馈"AI 答非所问"

```bash
# Step 1: 在 Trace 平台搜索该用户的请求
filter: user_id=u_12345, time_range=last_1h

# Step 2: 看 Trace 每一步耗时
- RAG retrieve: 50ms ✓
- LLM invoke: 1000ms ✓
- Re-rank: 100ms ✓
总: 1200ms，看似正常

# Step 3: 打开 input/output
input: "北京天气怎么样？"
retrieved_docs: [doc1 (旅行攻略), doc2 (美食推荐)]   ← 召回错了！
expected: [weather_data, news]
LLM output: "北京美食有..."   ← 基于错误 RAG 错误答案

# Step 4: 定位根因
根因：RAG 召回错（Embedding 模型漂移？or 向量库过期？）
```

**没有 Trace 时的排查**：看日志、看监控、猜——**1-3 天**才能定位根因。

---

## 4. 漂移检测（Drift Detection）

### 4.1 5 大漂移类型

| 漂移类型 | 检测方法 | 修复 |
|---------|---------|------|
| **数据漂移**（输入分布变化）| embedding 分布对比（PSI / KS 检验）| 重训 / 调整 |
| **概念漂移**（语义关系变化）| 黄金集回归 | 重训 |
| **模型漂移**（上游升级）| Prompt 模板响应分布对比 | 重跑黄金集 |
| **Embedding 漂移** | RAG 召回率变化 | 重建向量库 |
| **用户期望漂移** | 用户反馈 + 人工复审 | 调整 Prompt |

### 4.2 漂移检测脚本

```python
from scipy.stats import ks_2samp
import numpy as np

def detect_drift(reference_embeddings, current_embeddings, threshold=0.1):
    """KS 检验检测分布漂移"""
    statistic, p_value = ks_2samp(reference_embeddings, current_embeddings)
    
    return {
        "drift_score": statistic,
        "p_value": p_value,
        "is_drifted": p_value < 0.05,  # 5% 显著水平
    }
```

### 4.3 漂移告警

```yaml
# Alertmanager 配置
groups:
  - name: llm_drift
    rules:
      - alert: EmbeddingDistributionDrift
        expr: llm_embedding_drift_score > 0.1
        for: 10m
        annotations:
          summary: "Embedding 分布漂移，建议重建向量库"
      - alert: GoldenSetAccuracyDrop
        expr: llm_gold_set_accuracy < 0.85
        for: 5m
        annotations:
          summary: "黄金集准确率跌破 85%，需排查"
```

---

## 5. 快速定位 Checklist

**问题**：用户反馈"AI 不工作了"

- [ ] **Step 1（30 秒）**: 看监控大盘
  - 延迟正常吗？错误率正常吗？
- [ ] **Step 2（1 分钟）**: 查 Trace
  - 随机抽样 5 个失败请求，看 Trace 哪步耗时异常
- [ ] **Step 3（2 分钟）**: 比对黄金集
  - 跑 50 题黄金集，看准确率
- [ ] **Step 4（5 分钟）**: 定位 + 修复
  - 根因可能是：RAG 召回错 / Prompt 漂移 / 模型升级 / 数据过期

---

## 6. 反模式 · 5 个常见错

### ⚠️ 反模式 1：只监控延迟 / 错误率

- 错：监控 HTTP 200 + latency
- 对：质量 + 延迟 + 成本 + 一致性 4 维

### ⚠️ 反模式 2：上线后没有 Trace

- 错：只在日志里打 prompt 和 response
- 对：完整 Trace（每步耗时、token 数、成本）

### ⚠️ 反模式 3：黄金集跑一次

- 错：上线前跑一次，上线后再也不跑
- 对：每月 / 每次模型升级都跑回归

### ⚠️ 反模式 4：漂移检测从未设置

- 错：等到事故才看数据变化
- 对：主动监控 embedding / prompt / 召回率漂移

### ⚠️ 反模式 5：定位问题全靠"经验感觉"

- 错："我觉得是 X 的问题"
- 对：Trace 数据 + 黄金集回归 + 漂移分数

---

## 7. 一句话总结

> **LLM 线上监控 = Trace（5 分钟定位）+ 黄金集回归（每月）+ 漂移检测（实时）+ 4 维指标（延迟 / 成本 / 质量 / 一致性）。监控盲区就是事故温床。**

---

← [返回: 大模型思维工程](../README.md) · 上一章：[04-circuit-breaker](04-timeout-and-circuit-breaker.md) · 下一章：[06-decision-tree](06-decision-tree.md)
