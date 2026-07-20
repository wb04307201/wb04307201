<!--
module:
  parent: ai
  slug: ai/rag-evaluation
  type: article
  category: 主模块子文章
  summary: RAG 评估指标（检索×生成×系统 三维度）+ RAGAS / TruLens / DeepEval 工具对比 + Agentic RAG 评估补充
-->

# RAG 评估指标与工具

> ⬅️ [返回 Agent Evaluation](../README.md)

> **一句话定位**：RAG 评估 = **量化 RAG 系统的检索质量 + 生成质量**。**RAGAS / TruLens / DeepEval** 3 大工具横评，帮你选对评估方案。

---

## 📊 评估指标分类

### 检索质量（Retrieval Quality）

| 指标 | 含义 | 公式 |
|------|------|------|
| **Context Precision** | Top-K 中相关文档比例 | 相关的 / K |
| **Context Recall** | 答案所需信息被检索出的比例 | 检索出的相关信息 / 所有相关信息 |
| **Context Relevance** | 检索文档与 query 语义相关度 | 0-1 |
| **MRR** (Mean Reciprocal Rank) | 首个相关文档排名倒数 | 1/rank |
| **NDCG** | 归一化折损累积增益 | 0-1 |

### 生成质量（Generation Quality）

| 指标 | 含义 | 工具 |
|------|------|------|
| **Faithfulness** | 答案是否忠于 context（无幻觉）| RAGAS |
| **Answer Relevancy** | 答案与 query 相关度 | RAGAS |
| **Answer Correctness** | 答案与标准答案匹配度 | RAGAS |
| **Answer Similarity** | 答案与参考答案语义相似度 | DeepEval |
| **Hallucination Rate** | 幻觉比例 | TruLens |

---

## 🛠️ 1. RAGAS（推荐首选）

**2024 最主流 RAG 评估框架**。

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision, context_recall,
    faithfulness, answer_relevancy, answer_correctness
)

# 准备数据
dataset = {
    "question": ["什么是 RAG？"],
    "contexts": [["RAG 是检索增强生成..."]],
    "answer": ["RAG 是一种结合检索和生成的技术..."],
    "ground_truth": ["检索增强生成，结合外部知识..."],
}

# 评估
result = evaluate(
    dataset,
    metrics=[
        context_precision,  # 检索精确率
        context_recall,     # 检索召回率
        faithfulness,       # 答案忠实度
        answer_relevancy,   # 答案相关度
    ],
)

print(result)
# {'context_precision': 0.85, 'context_recall': 0.78,
#  'faithfulness': 0.92, 'answer_relevancy': 0.88}
```

**优势**：
- ✅ 5+ 主流指标开箱即用
- ✅ LLM-as-Judge 自动化评估
- ✅ 与 LangChain / LlamaIndex 集成

---

## 🛠️ 2. TruLens

**适合 Agent + RAG 联合评估**。

```python
from trulens_eval import TruChain, Feedback, OpenAI

# 定义反馈函数
f_qa_relevance = Feedback(
    OpenAI().qa_relevance
).on_input_output()

# 包装 RAG pipeline
tru_rag = TruChain(
    rag_chain,
    feedbacks=[f_qa_relevance, ...],
    app_name="My RAG"
)

# 评估
response, record = tru_rag.query("什么是 RAG？")
tru_rag.get_leaderboard()
```

**特点**：
- ✅ 反馈函数可组合
- ✅ Dashboard 可视化
- ✅ 适合复杂 RAG / Agent

---

## 🛠️ 3. DeepEval

**单元测试风格的 RAG 评估**。

```python
from deepeval import evaluate
from deepeval.metrics import (
    ContextualPrecisionMetric, 
    FaithfulnessMetric,
    AnswerRelevancyMetric
)
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="什么是 RAG？",
    actual_output="RAG 是检索增强生成...",
    retrieval_context=["RAG 是..."],
    expected_output="检索增强生成...",
)

metric = FaithfulnessMetric(threshold=0.7)
metric.measure(test_case)
print(metric.score, metric.reason)
```

**特点**：
- ✅ 像单元测试一样写评估
- ✅ CI/CD 友好
- ✅ 与 pytest 集成

---

## 📊 3 大工具对比

| 工具 | 指标数 | LLM-as-Judge | CI 集成 | 适合 |
|------|--------|--------------|---------|------|
| **RAGAS** | 5+ | ✅ | 中 | 生产 RAG |
| **TruLens** | 10+ | ✅ | 弱 | Agent + RAG |
| **DeepEval** | 8+ | ✅ | **强** | DevOps 团队 |

**选型建议**：
- 默认 → RAGAS
- Agent → TruLens
- CI/CD → DeepEval

---

## 📈 评估最佳实践

### 1. 准备黄金集

```text
100-500 条 (question, ground_truth, contexts) 黄金集
覆盖：简单 / 复杂 / 边界 / 错误 4 类问题
```

### 2. 多指标评估

```python
metrics = [
    context_precision,  # 检索
    context_recall,     # 检索
    faithfulness,       # 生成
    answer_relevancy,   # 生成
]
```

### 3. 持续监控

```text
每周对线上 100 条 query 跑评估
指标下降 > 5% 告警
```

---

## 🏗️ 系统工程指标（第 3 维度：跑得稳不稳）

> 前两节的检索/生成指标只看"文本质量"，生产落地还要看**工程表现**。RAG 评估的完整拆解是 **检索 × 生成 × 系统** 三维度。

| 指标 | 含义 | 参考位置 |
|------|------|---------|
| **Latency** | 首字响应 TTFT + 端到端总时延 | [推理性能指标](../../../02-technology-stack/inference-metrics/README.md) |
| **Cost** | 单次查询 Token 数（输入上下文 + 输出）及 API 成本 | [Token 与计费](../../../02-technology-stack/token-billing/README.md) |
| **User Feedback** | 显式（👍/👎）+ 隐式（会话中止率 / 追问率） | 线上埋点 |

> 💡 **性价比最高的切入点**：初期优先监控 **Faithfulness（安全底线）** + **Context Recall（能力上限）** 两个指标，再叠加系统工程维度。

---

## 🤖 Agentic RAG 评估补充（多步智能体场景）

> 当 RAG 演进到 [Agentic 阶段](../../../02-technology-stack/rag-paradigm-evolution/README.md)（Agent 自主拆解任务、多步检索），传统 RAG 指标不够用，需叠加**智能体维度**：

| 指标 | 含义 |
|------|------|
| **Task Success Rate（任务完成率）** | 是否通过多步规划 + 工具调用最终达成复杂目标 |
| **Tool Call Accuracy（工具调用准确率）** | 选检索/查库/执行工具及其参数是否正确 |
| **Self-Correction Rate（自我修正率）** | 首次检索/生成失败后，能否通过反思自主调整并输出正确结果 |

> 🔗 这三个指标的通用母体（完整公式 + 阈值）见 [Agent 6 大评测维度](../01-six-metrics.md)；面试话术见 [如何量化 Agent 性能](../../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)。

---

## 🔗 兄弟章节

- **本专题**：[RAG Pipeline 综述](../../../02-technology-stack/rag-pipeline/README.md) / [RAG 范式演进四阶段](../../../02-technology-stack/rag-paradigm-evolution/README.md) / [Hybrid Search](../../../02-technology-stack/hybrid-search/README.md) / [Reranker](../../../02-technology-stack/reranker/README.md) / [Query Rewrite](../../../02-technology-stack/query-rewrite/README.md)
- **评估维度**：[Agent 6 大评测维度](../01-six-metrics.md) / [5 种评估方法](../02-five-methods.md)
- **咬文嚼字**：[RAG 面试](../../../../13.split-hairs/11.ai/rag/README.md) / [Agent 性能量化](../../../../13.split-hairs/11.ai/agent-performance-evaluation/README.md)
- **LLMOps**：[08-llmops](../../README.md) — RAG 安全

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 召回率高 = 系统好 | ✅ 还要看 faithfulness（无幻觉） |
| ❌ LLM-as-Judge 一定准 | ✅ 需与人类评估对齐（> 0.8）|
| ❌ 离线评估好线上也好 | ✅ 线上需持续监控 |
| ❌ RAGAS 工具多就好 | ✅ 选 3-5 个核心指标即可 |

← [返回 Agent Evaluation](../../README.md)