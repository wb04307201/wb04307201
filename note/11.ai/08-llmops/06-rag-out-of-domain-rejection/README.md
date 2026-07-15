<!--
module:
  parent: ai/llmops
  slug: ai/llmops/rag-out-of-domain-rejection
  type: deep-dive
  category: RAG 质量治理
  summary: RAG 超范围检测与拒答策略深度 —— 6 大检测机制 + 5 大拒答模式 + 4 步阈值调优 + 监控体系 + OSS 实战。
-->

# RAG 超范围检测与拒答策略 · 深度专章

> 一句话定位：**没有拒答机制的 RAG = 强答 = 幻觉 = 信任崩塌**。完整体系基于 [主模块 · RAG vs Fine-tuning 主章节](../01-rag-vs-finetuning/README.md) + [LLM 幻觉防御专题](../../../13.split-hairs/11.ai/hallucination/README.md)。面试速查版见 [13.split-hairs · rag-out-of-domain-rejection](../../../13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md)。

---

## 一、为什么必须能做"拒答"？

### 1.1 没有拒答机制的 RAG 会发生什么？

```text
用户：阿明的爷爷是谁？
RAG 检索：top_k 全是无关文档（分数都 < 0.4）
LLM：收到空上下文 → 强行"生成"
输出："根据知识库，阿明的爷爷叫张三，1920 年..."   ← 幻觉！

→ 用户被误导
→ 信任崩塌 → 用户流失
→ 高风险领域（医疗/法律）→ 法律风险
```

### 1.2 三大业务驱动力

| # | 驱动力 | 后果（无拒答） |
|---|--------|---------------|
| 1 | **用户信任** | 用户被一次幻觉误导，永远离开 |
| 2 | **法律合规** | 医疗/法律/金融领域强答 → 法律诉讼 |
| 3 | **成本控制** | 强答 = 错误答案 = 客服成本 × 10 |

---

## 二、6 大检测机制（深度详解）

### 2.1 机制 1：检索分数阈值

```python
def detect_via_score(results, threshold=0.5):
    if not results:
        return True  # 空结果 = OOD
    
    top_score = max(r.score for r in results)
    return top_score < threshold
```

| 优 | 缺 |
|---|---|
| 最简单 | 阈值难调（依赖 embedding 模型） |
| 易部署 | 不同 query 类型阈值不一样 |

### 2.2 机制 2：检索数量阈值

```python
def detect_via_count(results, min_count=3):
    return len(results) < min_count
```

| 优 | 缺 |
|---|---|
| 防止"只有 1 个相关文档"时强答 | 太粗，可能误伤（高密度查询） |

### 2.3 机制 3：向量空间距离（**推荐**）

```python
def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

def detect_via_distance(query_emb, results, threshold=0.5):
    if not results:
        return True
    
    avg_distance = np.mean([
        cosine_distance(query_emb, r.embedding) for r in results[:5]
    ])
    return avg_distance > threshold
```

| 优 | 缺 |
|---|---|
| 比分数更稳定（归一化无关）| 计算稍贵（需 query + 文档 embedding）|

### 2.4 机制 4：OOD 分类器

```python
class OODClassifier:
    """专用 ML 模型判 in/out"""
    
    def __init__(self):
        self.model = load_model("ood_classifier_v1")
    
    def predict(self, query):
        # 特征：query + 检索结果
        features = self.extract_features(
            query, retrieved_docs=[r for r in results]
        )
        prob_in_domain = self.model.predict_proba(features)[0]
        return prob_in_domain < 0.5  # out of domain
```

**优点**：准确率高，可结合 retriever score + query features
**缺点**：需要标注数据训练

### 2.5 机制 5：NLI Entailment（**最准**）

```python
def nli_check(output_text, source_docs):
    """检查输出是否被源文档支持"""
    entailment_model = load_nli("deberta-mnli")
    
    for source in source_docs:
        score = entailment_model.predict(
            premise=source.text,
            hypothesis=output_text
        )
        # entailment 意味着输出被源支持
        if score.label == "entailment" and score.prob > 0.8:
            return True  # 输出被支持 = 可信
    return False  # 无源支撑 = 幻觉
```

| 优 | 缺 |
|---|---|
| 最准确，直接判断"是否被支持" | 慢（每个 NLI 调用 100-300ms）+ 贵 |
| 适合关键决策 | 不适合高 QPS |

### 2.6 机制 6：Self-Consistency

```python
def detect_via_consistency(query, n_samples=5):
    """多次采样 → 投票 → 不一致率"""
    samples = [llm.invoke(query) for _ in range(n_samples)]
    
    # 算 pairwise cosine
    embeddings = encoder.encode(samples)
    sim_matrix = cosine_sim(embeddings)
    
    # 排除自己
    np.fill_diagonal(sim_matrix, 1.0)
    consistency = sim_matrix[~np.eye(n_samples, dtype=bool)].mean()
    
    return consistency < 0.6  # 不一致率太高 = 模型在瞎编
```

**优点**：无需外部信息，纯模型输出检测
**缺点**：成本 × N（采样 5 次）

### 2.7 6 机制选型矩阵

| 机制 | 实现成本 | 准确率 | 延迟 | 适合 |
|------|---------|--------|------|------|
| 检索分数 | 🟢 极低 | ⭐⭐ | 0 ms | 起步方案 |
| 数量阈值 | 🟢 极低 | ⭐ | 0 ms | 兜底 |
| 向量距离 | 🟢 低 | ⭐⭐⭐ | 10 ms | **生产首选** |
| OOD 分类器 | 🟡 中 | ⭐⭐⭐⭐ | 20 ms | 进阶方案 |
| NLI Entailment | 🔴 高 | ⭐⭐⭐⭐⭐ | 200 ms | 关键决策兜底 |
| Self-Consistency | 🔴 高 | ⭐⭐⭐⭐ | ×N ms | 高风险问题 |

**实战组合**：`向量距离 + NLI` —— 向量距离做快速兜底，NLI 做关键决策二次校验。

---

## 三、5 大拒答模式深度对比

### 3.1 5 大模式选型矩阵

| 模式 | 适用 | 兜底话术模板 | 用户体验 |
|------|------|-----------|---------|
| **Hard 拒答** | 完全没答案（top_score < 0.3）| "知识库暂未收录此问题。可换个问法或联系我们补充" | ⭐⭐⭐⭐⭐ |
| **Soft 拒答** | 高风险领域（医疗/法律/金融）| "此问题涉及专业领域，建议咨询专业人士获取准确答案" | ⭐⭐⭐⭐ |
| **Partial 答** | 部分有答案（0.3 < score < 0.5）| "基于部分信息：...可能不完整，请验证" | ⭐⭐⭐ |
| **Deflect 转人工** | 高价值客户 / 重要业务 | "已将您的问题提交人工客服" | ⭐⭐⭐⭐ |
| **Escalate 升级** | 高难度问题 | 退到更大模型 / fallback | ⭐⭐ |

### 3.2 决策树

```python
def route_rejection(query, results, user_context):
    score = top_score(results)
    risk = classify_risk(query)  # medical/legal/financial?
    
    if score >= 0.7:
        return "direct"
    elif score >= 0.5:
        return "partial"
    elif score >= 0.3:
        if risk == "high":
            return "soft"
        elif is_vip(user_context):
            return "deflect"
        else:
            return "partial"  # 部分答 + 强提醒
    else:
        # score < 0.3
        if risk == "high":
            return "soft"
        else:
            return "hard"
```

### 3.3 实战兜底话术库

```python
REFUSAL_TEMPLATES = {
    "hard": [
        "知识库暂未收录此问题。建议您换个问法或联系我们补充。",
        "抱歉，这个问题不在我们知识库范围内。",
    ],
    "soft": [
        "此问题涉及{topic}领域，建议咨询专业人士获取准确答案。",
        "{topic}问题需要专业判断，我无法提供准确信息。",
    ],
    "partial": [
        "基于现有知识，部分信息：...\n\n_此答案基于部分知识库信息，可能不完整_",
        "找到部分相关内容：...\n\n_信息可能不全，建议再次核实_",
    ],
    "deflect": [
        "已将您的问题提交人工客服（订单号：u{user_id}），稍后回复。",
        "让我们的人工客服协助您，已为您创建工单。",
    ],
    "escalate": [
        "（用更大模型重试）",
        "（调用 fallback 模型）",
    ],
}
```

---

## 四、4 步阈值调优法（核心生产方法）

### 4.1 完整 4 步流程

```python
import numpy as np
from sklearn.metrics import precision_recall_curve, roc_curve

# Step 1: 收集测试集（最关键）
test_set = []  # [(query, ground_truth_ood_label, top_k_results)]
for query in load_real_queries():
    top_k = retriever.search(query, top_k=10)
    label = await human_annotate(query, top_k)  # True=OOD, False=in-domain
    test_set.append((query, label, top_k))

print(f"Test set size: {len(test_set)}")
print(f"OOD ratio: {np.mean([label for _, label, _ in test_set]):.2%}")

# Step 2: 跑检索拿分数
for query, label, top_k in test_set:
    top_score = max(r.score for r in top_k) if top_k else 0.0
    # 关键洞察：OOD 分数 = 1 - 检索分
    ood_score = 1.0 - top_score

y_true = np.array([label for _, label, _ in test_set])  # 1=OOD, 0=in-domain
y_scores = np.array([1.0 - max(r.score for r in top_k) if top_k else 1.0
                       for _, _, top_k in test_set])

# Step 3: 划 ROC 曲线选 threshold
precisions, recalls, thresholds = precision_recall_curve(y_true, y_scores)

# 业务目标：在保证 Precision >= 0.95 的前提下，最大化 Recall
target_precision = 0.95
valid_idx = np.where(precisions[:-1] >= target_precision)[0]
if len(valid_idx) > 0:
    best_idx = valid_idx[np.argmax(recalls[valid_idx])]
    threshold_optimal = 1.0 - thresholds[best_idx]
    
    print(f"Optimal threshold: {threshold_optimal:.3f}")
    print(f"Precision: {precisions[best_idx]:.3f}")
    print(f"Recall: {recalls[best_idx]:.3f}")

# Step 4: 监控线上漂移
def monitor_threshold():
    """每日检查拒答率是否在正常区间"""
    today_rejection = today_rejected_queries()
    today_total = today_total_queries()
    
    rejection_rate = today_rejection / today_total
    
    if rejection_rate < 0.03:
        alert("⚠️ 拒答率过低，可能阈值太松")
    elif rejection_rate > 0.30:
        alert("⚠️ 拒答率过高，可能阈值太严")
    else:
        log(f"✅ 拒答率 {rejection_rate:.2%} 健康")

# 当拒答率变化 > 20% 时，重新跑 Step 3 调优
```

### 4.2 监控指标（生产级）

| 指标 | 健康区间 | 异常动作 |
|------|---------|---------|
| 拒答率 | 5-15% | 偏离 → 重新调优 |
| Partial 答率 | 10-20% | 太高 → 检查 top_k |
| Deflect 率 | 1-5% | 太高 → 工单积压 |
| NLI 拒绝率 | < 5% | 太高 → 检索质量差 |
| 阈值漂移 | < 0.05 | 超 → 重新评估 |

---

## 五、6 OSS 实战对比

| 工具 / OSS | 拒答能力 | 实现 | 局限 |
|-----------|---------|------|------|
| **LangChain** | RetrievalQA + 置信度 | `if score < 0.5: "I don't know"` | 阈值硬编码 |
| **LlamaIndex** | Refine + 自定义 | `Refine.from_query_engine(...)` | 灵活性一般 |
| **Haystack** | ConfidenceFilter | 文档级 filter | 阈值策略单一 |
| **OpenAI Assistants** | File Search 内置 | `tool_choice + retrieval` | 黑盒 |
| **Cohere Rerank** | Rerank 分数阈值 | API 内置 | 依赖 Cohere |
| **Self-RAG / CRAG** | 自反思 | LLM 自评 | 成本高 |

### 5.1 LangChain 实战

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 自定义拒答 prompt
REFUSAL_PROMPT = """
你是 AI 助手。如果提供的上下文不能回答问题，请回复"我不知道"。
否则基于上下文回答。

上下文：{context}
问题：{question}
"""

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,  # 关键：返回检索分数
    chain_type_kwargs={"prompt": REFUSAL_PROMPT}
)

result = qa_chain({"query": query})
top_score = result["source_documents"][0].metadata.get("score", 0)

if top_score < 0.5:
    return REFUSAL_TEMPLATES["hard"][0]
else:
    return result["result"]
```

### 5.2 LlamaIndex 实战

```python
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

# 后处理：过滤低分文档
query_engine = RetrieverQueryEngine.from_args(
    retriever=vector_index.as_retriever(similarity_top_k=10),
    node_postprocessors=[
        SimilarityPostprocessor(similarity_cutoff=0.5)  # 阈值
    ],
)

response = query_engine.query(query)

# 检查检索到的文档数
if len(response.source_nodes) < 3:
    return REFUSAL_TEMPLATES["hard"][0]
```

---

## 六、5 大反模式深度补充

### 6.1 反模式 1：没阈值，所有问题必答（深度）

```python
# ❌ 反例
def rag_answer(query):
    results = vector_db.search(query, top_k=5)
    context = "\n".join(r.text for r in results)
    return llm.invoke(f"基于：{context}\n回答：{query}")
    # 没有拒答机制 → 强答 → 幻觉

# ✅ 正例
def rag_answer_with_rejection(query):
    results = vector_db.search(query, top_k=5)
    top_score = max(r.score for r in results) if results else 0
    
    if top_score < 0.5:
        return REFUSAL_TEMPLATES["hard"][0]
    
    context = "\n".join(r.text for r in results[:3])
    return llm.invoke(f"基于：{context}\n回答：{query}")
```

### 6.2 反模式 2：高风险领域强答（深度）

```python
# ❌ 反例
def medical_advice(query):
    return medical_rag(query)  # 没特别处理 → 医疗幻觉 = 法律风险

# ✅ 正例
HIGH_RISK_DOMAINS = ["医疗", "法律", "金融", "医药", "诊断"]
def high_risk_advice(query):
    is_high_risk = any(d in query for d in HIGH_RISK_DOMAINS)
    
    if is_high_risk:
        # 高风险 → 必走 Soft 拒答 + NLI 二次校验
        return SOFT_REFUSAL + "\n（系统判定为高风险问题）"
    
    answer = standard_rag(query)
    
    # NLI 二次校验
    if not nli_supported(answer, source_docs):
        return SOFT_REFUSAL
    
    return answer
```

---

## 七、生产级部署方案

### 7.1 完整 RAG 链路

```text
用户 query
    ↓
[1] Query 预处理（实体识别 / 改写）
    ↓
[2] 向量检索 → top_k=10 候选
    ↓
[3] Rerank（精排） → top_k=3
    ↓
[4] 拒答检测（核心）
    ├─ 向量距离判断 OOD
    ├─ NLI 检查（关键决策）
    └─ 综合评分
    ↓
[5] 路由决策
    ├─ high → 直接答（LLM）
    ├─ medium → Partial（LLM + 提醒）
    ├─ low → Deflect/Soft
    └─ very_low → Hard 拒答
    ↓
[6] 后处理
    ├─ NLI 二次校验（输出）
    ├─ 格式规范化
    └─ 兜底话术
    ↓
返回用户
    ↓
[7] 监控
    ├─ 拒答率
    ├─ Partial 率
    └─ 用户反馈
```

### 7.2 关键监控 Dashboard

| 指标 | 告警阈值 | 关注点 |
|------|---------|--------|
| 总体拒答率 | < 3% 或 > 30% | 阈值漂移 |
| Partial 答率 | > 30% | top_k 太小 |
| NLI 拒绝率 | > 5% | 检索质量差 |
| 平均检索分数 | < 0.4 | embedding 模型问题 |
| Deflect 工单积压 | > 100 | 客服压力大 |

---

## 八、决策树（实战选型）

```text
Q1：业务对幻觉容忍度？
├─ 极低（医疗/法律）→ 必须 NLI + Soft 拒答
├─ 低（金融/电商）→ 向量距离 + Hard/Partial
└─ 普通（聊天）→ 检索分数 + Partial

Q2：用户对延迟要求？
├─ 实时（< 100ms）→ 只用向量距离
└─ 可以慢（> 200ms）→ 向量距离 + NLI

Q3：用户对拒答接受度？
├─ 高（专家用户）→ Hard 拒答没问题
└─ 低（C 端用户）→ Partial + Deflect 多给点
```

---

## 📚 相关章节

**主模块**：
- [主模块 · RAG 体系](../01-rag-vs-finetuning/README.md) —— 351 行深度
- [LLM 幻觉防御专题](../../../13.split-hairs/11.ai/hallucination/README.md) —— 233 行（生产要素）
- [RAG 架构面试题](../../../13.split-hairs/11.ai/rag/README.md) —— RAG 基础

**兄弟专题**：
- [Agent Memory 共享专章](../../04-architecture/agent-memory/shared-memory.md) —— 多 Agent 共享
- [Claude Code Agentic Search 专题](../../../13.split-hairs/11.ai/claude-code-agentic-search/README.md) —— AI Coding 反 RAG

**LLMOps**：
- [LLM Evaluation](../../04-llm-evaluation/README.md)
- [LLM Security](../../05-llm-security/README.md)

**面试速查**：
- [13.split-hairs · rag-out-of-domain-rejection](../../../13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md) —— 5 拒答模式 + 4 步调优

---

> 📅 2026-07-13 · 11.ai/08-llmops · ⭐⭐⭐⭐⭐ · 6 检测机制 + 5 拒答模式 + 4 步阈值 + 6 OSS 实战 + 监控体系

← [返回: AI 知识体系 · 08-llmops](README.md)
