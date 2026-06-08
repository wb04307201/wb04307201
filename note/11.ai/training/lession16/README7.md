# 决策框架与最佳实践：Eval + 数据质量

> ⬅️ [返回目录](README.md) | 上一篇：[Deep Research](README6.md) | 下一篇：[综合示例](README8.md)

---

## 🎯 一句话定位

**5 条路径都讲完了，但 80% 的项目翻车不是架构问题**——是 Eval 缺失、数据质量差。  
本课讲两件事：**①决策清单（5 选 1）②避坑指南（Eval + 数据洗涮）**。

---

## 📋 终极决策清单（5 选 1）

| 场景 | 推荐方案 | 关键依据 |
|:--|:--|:--|
| **① 小数据 + 稳定**（< 200 份文档，知识不常变） | **长 Context + Prompt Caching** | 别折腾，最甜 |
| **② 大数据 + 语义模糊**（10K+ 文档，查询绕） | **生产级 RAG**（Hybrid + Rerank + Contextual） | 别用 baseline |
| **③ 代码 / 结构化 / 多跳**（代码库、数据库、多步推理） | **Agent + grep / SQL / API** | 别建向量索引 |
| **④ 复杂研究 + 用户付得起**（尽调、学术综述、长报告） | **Deep Research 架构** | Planner → Search → Reader → Aggregator |
| **⑤ 以上都不确定**（需求不清、数据脏、没数据） | **先建 Eval · 先洗数据** | 再选架构 |

### 决策树

```mermaid
graph TB
    Start["🤔 接到知识接入需求"]

    Start --> Q1{"Q1: 数据规模？"}
    Q1 -->|"< 200 份"| Q1A{"稳定吗？"}
    Q1 -->|"10K+ 份"| Q1B{"查询类型？"}

    Q1A -->|是| Path1["① 长 Context +<br/>Caching"]
    Q1A -->|否| Path2["② RAG<br/>（含更新）"]

    Q1B -->|精确| Path3["③ Agent +<br/>SQL / grep"]
    Q1B -->|语义| Path4["② 生产级 RAG<br/>Hybrid + Rerank +<br/>Contextual"]

    Q1B -.->|"复杂研究"| Path5["④ Deep Research"]

    Start -.->|"数据脏 / 需求不清"| Eval["⑤ 先建 Eval<br/>先洗数据"]

    classDef primary fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef eval fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class Path1,Path2,Path3,Path4,Path5 primary
    class Eval eval
```

---

## 🚧 避坑 1：没建 Eval（评估体系）

### 真实案例

> 某团队改了一个 prompt，小测试集（5 个 query）+18% 准确率，**全员庆祝**。  
> 下周用户报 bug，真实日志整体召回率 -15%。**没人知道**，因为没人测真实流量。

### 铁律

> **Eval 比换 embedding 模型重要 10x**。没 eval，任何升级都是赌。

### 为什么重要？

| 没 Eval 的项目 | 有 Eval 的项目 |
|:--|:--|
| 改 A 看 B 好坏 | 改 A 看所有指标变化 |
| 凭感觉调优 | 数据驱动迭代 |
| 上线翻车才知道问题 | 灰度阶段就发现 |
| 评估是"玄学" | 评估是"工程" |

### 行动清单

**第一天就开始建 Eval**：

1. **从真实日志挖 100 个 query**
   - 用户真实问过的问题
   - 标注预期答案（人手标 / LLM 辅助标）
   - 覆盖简单 / 中等 / 复杂

2. **建立指标体系**

| 指标 | 计算方式 | 目标 |
|:--|:--|:--|
| 召回率（Recall@K） | 相关文档中出现在 Top-K 的比例 | ≥ 80% |
| 答案准确率 | LLM-as-judge 或人工评分 | ≥ 85% |
| 答案忠实度 | 答案是否仅基于检索内容（无幻觉） | ≥ 90% |
| 延迟 P95 | 第 95 百分位响应时间 | < 3s（在线）/ < 30s（Agent） |
| 成本 / 查询 | Token + API 费用 | 视场景定 |

3. **每次改动都跑一遍**
   - 换 embedding → 跑 eval
   - 调 prompt → 跑 eval
   - 升级 Reranker → 跑 eval
   - 加 RAG 路由 → 跑 eval

### 推荐工具

| 工具 | 特点 | 适合 |
|:--|:--|:--|
| **RAGAS** | RAG 专用指标 | 开箱即用 |
| **Phoenix（Arize）** | 全链路 tracing | 生产监控 |
| **TruLens** | 反馈函数化 | 快速实验 |
| **DeepEval** | 单元测试风格 | CI/CD 集成 |
| **LangSmith** | LangChain 配套 | LangChain 项目 |
| **Braintrust** | 协作式 eval | 团队 |

### 最小 Eval 实现

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
)

# 准备测试集
test_data = [
    {
        "question": "启明 11 的电池多大？",
        "ground_truth": "5800mAh",
        "contexts": [...],  # 检索到的文档
        "answer": "...",     # LLM 生成的答案
    },
    # ... 99 个
]

# 跑评估
results = evaluate(
    test_data,
    metrics=[context_precision, context_recall, faithfulness, answer_relevancy],
)
print(results)
# {'context_precision': 0.82, 'context_recall': 0.78, ...}
```

---

## 🧹 避坑 2：数据质量 < 算法

### 残酷真相

> **三个月的项目，算法工作（embedding / rerank）只需 ~2 周，数据洗涮需要 ~10 周。**  
> 这不是工程师水平差——这是 RAG / Agent / LLM 系统的固有特性：**garbage in, garbage out**。

### Chunking 之前的"脏活"

#### 1. 格式归一

| 源格式 | 归一化策略 |
|:--|:--|
| PDF | 用 `unstructured` / `pymupdf` 抽文本 + 保留结构 |
| HTML | 清洗标签，保留 DOM 结构 |
| Word | 转 markdown |
| 图片（OCR 后） | 进 Embedding 前用 LLM 重新描述 |
| 多源混合 | 统一为 markdown / JSON |

#### 2. 表格单独处理

```mermaid
graph LR
    PDF["📄 PDF 文档"]
    PDF --> Parse["📝 解析"]
    Parse --> Text["📝 文本段落"]
    Parse --> Table["📊 表格"]

    Text --> TextChunk["✂️ 切块 → Embedding"]
    Table -->|"不走 Embedding"| SQL["📊 走 text-to-SQL<br/>或单独索引"]

    classDef special fill:#fff3e0,stroke:#f57c00
    class Table,SQL special
```

**为什么表格不进 Embedding**：
- 表格结构化，行列关系重要
- 切块破坏表格语义
- 走 text-to-SQL 精度 100%

#### 3. Metadata 设计（**比 embedding 还重要**）

每个 chunk 应至少包含：

```json
{
  "content": "营收增长了 3%。",
  "metadata": {
    "source": "ACME_2023Q2_10K.pdf",
    "page": 47,
    "section": "财务摘要",
    "company": "ACME",
    "fiscal_year": 2023,
    "fiscal_quarter": "Q2",
    "version": "v2023-08-01",
    "department": "Finance",
    "tags": ["earnings", "10-K"]
  }
}
```

**强大 metadata 让你无需重训模型就能过滤**：
- "ACME 2023 年的财报" → metadata 过滤
- "财务部门 2024 年后文档" → metadata 过滤
- "v2 之后的技术规范" → metadata 过滤

#### 4. 冲突 / 过时机制

| 情况 | 处理 |
|:--|:--|
| 同一事实，多个版本 | **新版覆盖旧版**，旧版本打 `superseded` 标记 |
| 多源说法矛盾 | 标注矛盾，人工 / Agent 复核 |
| 文档过期 | 加 `expired_at` 字段，过期不进检索 |
| 政策类文档更新 | 维护版本链，`version` + `supersedes` 字段 |

---

## 🆘 逃生舱

**如果不想洗数据**，还有两条退路：

### 退路 1：长 Context + Caching（[第二章](README2.md)）

把原始脏数据直接塞 prompt，让**模型自己消化**：
- ✅ 跳过数据清洗
- ✅ 跳过 chunking
- ❌ 文档量超 200 万 token 时塞不下

### 退路 2：LLM Wiki（[第一章](README1.md)）

让 LLM 帮你整理资料，构建持久化 Wiki：
- ✅ LLM 自动摘要、链接、维护一致性
- ✅ 人类只负责"筛选资料 + 提出好问题"
- ❌ 启动成本：要建 Schema 与工作流

---

## 📊 资源分配建议

一个 3 个月项目的典型时间分配：

```
第 1 周   ███░░░░░░░  Eval 体系搭建 + 100 个测试 query
第 2–3 周 ██████░░░░  数据清洗（归一、表格、metadata）
第 4–5 周 ████░░░░░░  选架构 + 跑 baseline
第 6–9 周 ████████░░  升级优化（Hybrid / Rerank / Contextual）
第 10 周  ███░░░░░░░  真实流量灰度
第 11–12 周 ████░░░░  调优 + 文档
```

**对比常见错误分配**：

```
❌ 错误：
第 1 周  ███░░░░░░░ 调研向量库
第 2 周  ███░░░░░░░ 调研 embedding
第 3 周  ████░░░░░░ 调研 Reranker
... 8 周过去了，没建 Eval，没洗数据
最后 4 周调 prompt 调 embedding，毫无章法
```

---

## 🌟 未来 1-2 年判断

1. **Prompt Caching 继续挤压 RAG 空间**
   - Context 窗口：1M → 2M → 5M
   - 缓存折扣：90% → 95% → 99%
   - 中小规模 RAG 越来越没必要

2. **所有严肃系统 agentic 化**
   - 从 `retrieve-then-generate` 静态流水线
   - 走向 `Agent loop`，vector / SQL / grep / web search 都是工具

3. **Eval 工具被卷**
   - 架构趋同后，比的是谁的评估闭环转得快
   - Eval 平台化（v0 → v1 → v2 持续迭代）

4. **数据治理是终极竞争力**
   - 模型趋同 → 算法趋同 → 数据差异化
   - 未来护城河：高质量私有数据 + metadata 体系

---

## 🤔 思考

1. **你的 Eval 现状**：你有多少真实 query 标注？跑了多少次评估？评估的指标覆盖度？
2. **数据脏活优先级**：你项目里，最该先洗的是格式归一、表格处理、还是 metadata？
3. **逃生舱的判断**：你的项目适合"先洗数据"，还是"塞 prompt 让模型扛"？

---

> ⬅️ [返回目录](README.md) | 上一篇：[Deep Research](README6.md) | 下一篇：[综合示例](README8.md)
