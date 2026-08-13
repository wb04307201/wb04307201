# SPEC for note-temp/09.ai-applications/rag/

> **Inherits from**: [../../SPEC.md](../../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 子目录定位

RAG（Retrieval-Augmented Generation）MOC：覆盖检索增强生成的全景——流水线 / 范式演进 / 选型 / 评估 / 拒答 / Agentic 替代，强调「检索质量 + 生成忠实度 + 评估指标」三大维度。

## 从 L1 继承

- G1-G6 通用 6 维度评分
- C4 实战部署指导（"X 场景用 Y"）
- C5 框架对比（RAGAS / TruLens / DeepEval）
- C6 性能基准（benchmark 数据）

## 本子目录规则（强特异性）

### 评估维度（追加 L1 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| R1 | 检索质量 | 召回率 / 精度 / MRR / NDCG 至少 2 个指标 + 公式 | 有指标无公式 | 只说「检索相关文档」 |
| R2 | Rerank 必要性 | 明确「何时需要 Rerank」+ 前后 NDCG 对比 | 有 Rerank 无对比 | 默认加 Rerank 不解释 |
| R3 | 评估指标 | 端到端忠实度（Faithfulness）+ 召回率（Recall）+ 至少 1 个工具横评 | 只有忠实度或召回率 | 无量化指标 |

### 写作要求

- **MOC 索引必备**：MOC README 必须包含原子笔记清单表（编号 + 路径 + 一句话摘要）
- **范式演进四阶段**：Naive → Advanced → Modular → Agentic 必须给出选型决策树
- **RAG vs Fine-tuning 决策表**：必须给出「数据更新频率 / 领域专业度 / 成本」三维决策
- **评估指标分层**：
  - 检索质量：Context Precision / Recall / MRR / NDCG
  - 生成质量：Faithfulness / Answer Relevancy / Hallucination Rate
  - 系统质量：端到端任务完成率
- **超范围拒答机制**：6 大检测 + 5 大拒答模式 + 4 步阈值调优
- **Agentic RAG 边界**：明确「AI Coding 等场景 RAG 不适用」的反直觉判断
- **Pipeline 5 阶段**：Query Rewrite → Hybrid Search → Rerank → 上下文压缩 → 生成

### 互链要求

- 必须回链 `../prompts/`（Prompt 工程是 RAG 生成阶段的基础）
- 必须互链 `../eval/`（评估方法论的更深入内容）
- 必须互链 `../agent/`（Agentic RAG 的延伸）
- 评估文章（`04-evaluation.md`）必须横评 RAGAS / TruLens / DeepEval 至少 3 个工具
- 嵌入模型相关章节必须互链 `../../08.ai-foundations/05-tokenization-embedding/`

### 反模式

- ❌ 不分场景直接推荐「RAG + GPT-4」（应先做选型决策）
- ❌ 只讲向量检索不讲 Hybrid Search（BM25 + 向量混合）
- ❌ 不给评估指标就用线上效果说话
- ❌ 忽视 Agentic Search 取代 RAG 的 AI Coding 趋势
- ❌ Rerank 默认开启不调参（成本 +10ms 不一定值得）