<!--
question:
  id: 11.ai-rag-out-of-domain-rejection
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: RAG 落地追问
  tags: [11.ai, RAG, OOD, threshold, refusal, hallucination, 知识库边界, NLI]
-->

# RAG 如何检测超范围并拒答？—— 6 大检测机制 + 5 大拒答模式 + 4 步阈值调优

> 一句话定位：**拒答 = 检索分数 < 阈值 + OOD 检测 + 5 大拒答模式 + 兜底话术**。完整深度 + 6 OSS 实战 + 4 步阈值调优见 [主模块 · 08-llmops/06-rag-out-of-domain-rejection 专章](../../../11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md)。

> **系列定位**：RAG 落地经典追问（Anthropic / OpenAI / 阿里 / 字节 / 美团 工程师高频）。考察的不是"RAG 是什么"，而是 **6 大检测机制 + 5 大拒答模式 + 4 步阈值调优 + 5 反模式 + 90 秒话术**。

---

⭐⭐⭐⭐⭐ 深度级别（高级 RAG 应用工程师 / 架构师）
📚 前置知识：RAG 基础 / 向量检索 / Embedding / Cosine 距离 / NLI

---

## 引子：3 个崩溃现场

```text
场景：2025 阿里 RAG 产品一面追问——

Q1：「用户问'阿明的爷爷是谁'，但知识库没收录，怎么办？」
    → 初级："RAG 检索不到，系统自动答'不知道'"    ❌
    → 高分："检索分数 < 阈值 → 5 大拒答模式 →
            兜底话术 + 用户跳转选项
            反而变成'AI 一本正经地编爷爷是谁'"   ❌

Q2：「阈值怎么定？错了怎么办？」
    → 初级："设为 0.5"           ❌
    → 高分："4 步调优：收集测试集 → 跑检索 →
            划 ROC 曲线 → 选 optimal threshold
            + 持续监控漂移"

Q3：「拒答太多，用户流失了，怎么办？」
    → 初级："降低阈值"           ❌
    → 高分："5 大拒答模式分级 —
            Hard 拒答 / Soft / Partial / Deflect /
            Escalate，不同风险用不同模式"
```

---

## 一、核心原理（必选）

### 1.1 为什么 RAG 必须能"拒答"？

```text
没有拒答机制的 RAG 会发生什么？

用户：阿明的爷爷是谁？
RAG 检索：top_k 全是无关文档（分数都 < 0.4）
LLM：收到空上下文 → 强行"生成"
输出："根据知识库，阿明的爷爷叫张三，1920 年..."   ← 幻觉！

→ 用户被误导 → 信任危机 → 法律风险（医疗/法律）
```

**核心矛盾**：

```text
知识库覆盖       知识库覆盖
   外     ←→→→   内
没答案     ←→→→   有答案
  ↓                ↓
必须拒答         可信回答

模糊地带（部分覆盖）：
  ↓
- 部分答 + 提醒
- Deflect 转人工
- Escalate 兜底模型
```

### 1.2 6 大检测机制（**核心考点**）

| # | 机制 | 实现 | 优缺点 |
|---|------|------|--------|
| 1 | **检索分数阈值** | `top_score < 0.5` 拒答 | 最简单，阈值难调 |
| 2 | **检索数量阈值** | `len(results) < N` 拒答 | 太粗，可能误伤 |
| 3 | **向量空间距离** | `cosine(query, results) > 0.6` | 比分数稳定 |
| 4 | **OOD 分类器** | 专门 ML 模型判 in/out | 准确但需数据 |
| 5 | **NLI Entailment** | 模型判断"输出被源文档支持" | 最准但慢 + 贵 |
| 6 | **Self-Consistency** | 多次采样 + 一致性投票 | 防幻觉，非拒答 |

---

## 二、5 大拒答模式（**核心考点**）

| # | 模式 | 适用 | 示例话术 |
|---|------|------|---------|
| 1 | **Hard 拒答** | 完全没答案 | "知识库暂未收录此问题" |
| 2 | **Soft 拒答** | 高风险领域（医疗/法律） | "建议咨询专业人士" |
| 3 | **Partial 答** | 部分有答案 | "部分答案：...可能不全，请验证" |
| 4 | **Deflect 转人工** | 重要业务 / 高价值客户 | "已将您的问题转给人工客服" |
| 5 | **Escalate 升级** | 高难度问题 | 退到更大模型 / 兜底模型 |

### 选型决策树

```text
RAG 检索结果：
├─ 分数 > 0.7 → 直接回答（高置信）
├─ 0.5 < 分数 < 0.7 → Partial 答（中等置信）
├─ 分数 < 0.5 但 > 0.3 → Deflect 转人工或 Soft 拒答
└─ 分数 < 0.3 → Hard 拒答
```

---

## 三、4 步阈值调优法

```python
# Step 1: 收集测试集
test_set = load_real_queries_with_ood_label()  # 100+ 问题

# Step 2: 跑检索拿分数
for q, label in test_set:
    scores = retriever.search(q, top_k=10)
    q.top_score = max(scores) if scores else 0.0
    q.is_ood = label  # True/False

# Step 3: 划 ROC 曲线选 threshold
from sklearn.metrics import precision_recall_curve
precisions, recalls, thresholds = precision_recall_curve(
    y_true=[1 if x.is_ood else 0 for x in test_set],
    y_scores=[1 - x.top_score for x in test_set]  # OOD 分数 = 1 - 检索分
)
# 选 precision >= 0.95 的最小 threshold
optimal_idx = np.where(precisions[:-1] >= 0.95)[0][0]
threshold_optimal = 1 - thresholds[optimal_idx]
print(f"Optimal threshold: {threshold_optimal:.3f}")

# Step 4: 监控线上漂移
def monitor_rag_threshold(threshold):
    """监控拒答率是否在 5-15% 区间"""
    rejection_rate = today_rejection_count / today_total
    if rejection_rate < 0.03:
        alert("⚠️ 拒答率过低，可能阈值太松或返回高幻觉")
    elif rejection_rate > 0.30:
        alert("⚠️ 拒答率过高，可能阈值太严或知识库稀疏")
```

---

## 四、5 大反模式（高频陷阱）

| # | 反模式 | 后果 | 修复 |
|---|--------|------|------|
| 1 | ❌ 没阈值，所有问题必答 | 幻觉率爆炸 → 用户信任崩塌 | 必须设阈值 |
| 2 | ❌ 阈值过低 | 50% 问题瞎答 | 用 ROC 曲线选 |
| 3 | ❌ 拒答话术生硬 | 用户流失 30%+ | 5 大模式分级 |
| 4 | ❌ 没 OOD 检测 | 强答 → 法律风险（医疗/法律）| NLI 兜底 |
| 5 | ❌ 不监控阈值漂移 | 模型迭代后召回率突变 | 每日监控 |

---

## 五、实战代码（5 大拒答模式分级）

```python
class RAGRejectionPolicy:
    """RAG 超范围 + 拒答策略"""
    
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        # 阈值（4 步调优法得出）
        self.thresholds = {
            "high":    0.70,  # 高置信：直接答
            "medium":  0.50,  # 中等：Partial
            "low":     0.30,  # 低：Deflect 或 Soft 拒
            # < low    : Hard 拒答
        }
        # 风险分级
        self.high_risk_topics = ["医疗", "法律", "金融"]
    
    def answer_with_rejection(self, query, user_id):
        # 1. 检索
        results = self.retriever.search(query, top_k=10)
        if not results:
            return self._hard_reject(query)
        
        top_score = max(r.score for r in results)
        
        # 2. 按分数分级处理
        if top_score >= self.thresholds["high"]:
            # 高置信 → 直接答
            return self._direct_answer(query, results)
        elif top_score >= self.thresholds["medium"]:
            # 中等 → Partial 答
            return self._partial_answer(query, results)
        elif top_score >= self.thresholds["low"]:
            # 低 → 风险分流
            if self._is_high_risk(query):
                return self._soft_reject(query)
            else:
                return self._deflect(query, user_id)
        else:
            # 极低 → Hard 拒答
            return self._hard_reject(query)
    
    def _direct_answer(self, query, results):
        ctx = "\n".join(r.text for r in results[:5])
        return self.llm.invoke(f"基于：\n{ctx}\n\n回答：{query}")
    
    def _partial_answer(self, query, results):
        ctx = "\n".join(r.text for r in results[:3])
        return self.llm.invoke(
            f"基于部分信息：\n{ctx}\n\n"
            f"若信息不足请明说，回答：{query}"
        ) + "\n\n_此答案基于部分知识库信息，可能不完整_"
    
    def _hard_reject(self, query):
        return "知识库暂未收录此问题。可换个问法或联系我们补充。"
    
    def _soft_reject(self, query):
        return "此问题涉及专业领域，建议咨询专业人士获取准确答案。"
    
    def _deflect(self, query, user_id):
        return f"已将您的问题提交人工客服（订单：u{user_id}）。"
    
    def _is_high_risk(self, query):
        return any(t in query for t in self.high_risk_topics)
```

---

## 六、面试话术（90 秒版本）

### 题目：RAG 如何检测超范围 + 拒答？

**高分答案（4 层递进，60-90 秒）**：

```text
1. 一句话（10 秒）：
   "没有拒答机制的 RAG = 强答 = 幻觉 = 信任崩塌。
    需要 6 大检测 + 5 大拒答模式。"

2. 6 大检测机制（25 秒）：
   "6 大检测机制：
   ① 检索分数阈值（< 0.5 拒答）—— 最简单
   ② 检索数量阈值（结果太少）—— 太粗
   ③ 向量空间距离（cosine > 0.6）—— 更稳定
   ④ OOD 分类器（专门 ML 模型）—— 准确
   ⑤ NLI Entailment（输出被源支持）—— 最准
   ⑥ Self-Consistency（多次采样）—— 防幻觉"

3. 5 大拒答模式（25 秒）：
   "5 大拒答模式分级：
   ① Hard：完全没答案 → '知识库暂无'
   ② Soft：高风险（医疗/法律）→ '咨询专业人士'
   ③ Partial：部分有答案 → 答 + 提醒
   ④ Deflect：转人工
   ⑤ Escalate：升级兜底模型

   决策树：高置信 → 直接答
           中等 → Partial
           低 → Deflect 或 Soft
           极低 → Hard 拒答"

4. 4 步阈值调优 + 反模式（30 秒）：
   "4 步调优：收集测试集 → 跑检索 → 划 ROC 曲线
   选 threshold → 监控漂移。
   5 反模式：
   没阈值（幻觉爆炸）/ 阈值过低（瞎答）/ 话术生硬（流失）/
   没 OOD（强答）/ 不监控（漂移）
   实战：拒答率监控 5-15% 正常，
   < 3% 漏拒 / > 30% 严拒"
```

---

## 七、面试反问（让候选人反客为主）

```text
Q1：贵司 RAG 用哪种拒答模式？
    → 答分级 5 模式 + 理由 = 高分
Q2：贵司拒答率是多少？怎么监控？
    → 答 5-15% + 监控体系 = 高分
Q3：贵司怎么定阈值？
    → 答 ROC + 测试集 + 漂移 = 高分
Q4：贵司遇到 OOD 问题怎么转人工？
    → 答 Deflect 模式 + 工单系统 = 高分
Q5：高风险领域（医疗/法律）怎么特别处理？
    → 答 NLI Entailment + Soft 拒答 = 高分
```

---

## 🔗 系列导航表（13.split-hairs · 11.ai 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [agent-dag-vs-react](../agent-dag-vs-react/README.md) | Agent DAG vs ReAct | ⭐⭐⭐⭐ |
| [agent-memory-classification](../agent-memory-classification/README.md) | Memory 三维分类 | ⭐⭐⭐⭐ |
| [claude-code-agentic-search](../claude-code-agentic-search/README.md) | Claude Code 搜索模式 | ⭐⭐⭐⭐ |
| [context-engineering](../context-engineering-interview/README.md) | Context Engineering | ⭐⭐⭐⭐⭐ |
| [hallucination](../hallucination/README.md) | 幻觉分类 + 4 检测 | ⭐⭐⭐⭐⭐ |
| [long-context-agent-strategy](../long-context-agent-strategy/README.md) | 长上下文 6 策略 | ⭐⭐⭐⭐⭐ |
| [multi-agent-shared-memory](../multi-agent-shared-memory/README.md) | 多 Agent 共享记忆 | ⭐⭐⭐⭐⭐ |
| [rag](../rag/README.md) | RAG 架构 | ⭐⭐⭐⭐⭐ |
| [rag-permission-isolation](../rag-permission-isolation/README.md) | RAG 多租户权限 | ⭐⭐⭐⭐ |
| **rag-out-of-domain-rejection**（本篇）| 超范围检测 + 5 拒答模式 + 4 步阈值调优 | ⭐⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [11.ai/08-llmops · 06-rag-out-of-domain-rejection 专章](../../../11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md) —— 完整深度：6 检测 + 5 拒答模式 + 4 步阈值 + 6 OSS 实战 + 监控体系

---

> 📅 2026-07-13 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 6 检测 + 5 拒答 + 4 步阈值 + 5 反模式 + 90 秒话术 + 11 兄弟导航

← [返回: 咬文嚼字 · 11.ai](../README.md)
