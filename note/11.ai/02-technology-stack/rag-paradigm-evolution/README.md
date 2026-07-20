<!--
module:
  parent: ai
  slug: ai/rag-paradigm-evolution
  type: article
  category: 主模块子文章
  summary: RAG 范式演进四阶段（Naive → Advanced → Modular → Agentic）—— 每阶段核心能力 / 关键技术 / 局限 + 对比表 + 选型决策树 + 与 5 阶段 Pipeline 的正交关系澄清
-->

# RAG 范式演进四阶段（Naive → Advanced → Modular → Agentic）

> ⬅️ [返回 L2 技术栈](../README.md)

> **一句话定位**：RAG 不是一种架构，而是**一条演进主线**。四阶段核心能力依次递进：**能跑通（Naive）→ 更精准（Advanced）→ 更灵活（Modular）→ 会思考（Agentic）**。四者是**继承与发展**关系，不是替代关系 —— 工程落地通常以 Advanced + Modular 组合为高性价比基线，必要时引入 Agentic。

> 📖 分类学来源：Gao et al.《Retrieval-Augmented Generation for Large Language Models: A Survey》（2023）定义了 Naive / Advanced / Modular 三代；Agentic RAG 是 2024-2025 的智能体延伸。

---

## 📐 演进主线一图记全

```text
Naive RAG          Advanced RAG         Modular RAG          Agentic RAG
「能跑通」    →    「更精准」      →    「更灵活」     →    「会思考」
─────────────────────────────────────────────────────────────────────
索引→检索→生成      +Pre/Post 优化       组件解耦+编排        Agent 自主决策
单向线性            单轮固定流程          可插拔模块           多步推理+反思
基础连通            检索精度优化          动态编排             任务规划
```

**核心能力递进**（一句话记忆）：

| 阶段 | 核心能力 | 一句话 |
|------|---------|-------|
| **Naive RAG** | 基础连通与快速验证 | **"能跑通"**（跑通检索-生成基线） |
| **Advanced RAG** | 检索精度与生成质量深度优化 | **"更精准"**（查得准、答得稳） |
| **Modular RAG** | 组件解耦与动态编排 | **"更灵活"**（像搭积木般适配） |
| **Agentic RAG** | 自主决策与复杂任务规划 | **"会思考"**（主动思考、多步执行） |

---

## 🔍 四阶段深度

### 1. Naive RAG（朴素 RAG）—— 基础连通

- **核心能力**：用最简单的方式把外部知识库与大模型连起来，跑通 `索引 → 检索 → 生成` 单向线性流程。
- **关键技术**：文档 Chunking + 基础 Embedding + 关键词/基础向量匹配 + 直接拼接 Prompt。
- **优势**：架构极简、开发成本低，适合快速搭原型、验证想法。
- **局限**：
  - 检索精度低、抗干扰差（"照单全收"噪声）
  - 难处理长文档 / 复杂语义查询
  - 无查询理解，口语化/多轮指代直接翻车

### 2. Advanced RAG（高级 RAG）—— 检索精度优化

- **核心能力**：对检索**全流程**做精细化控制，引入检索前（Pre-retrieval）+ 检索后（Post-retrieval）优化机制。
- **关键技术**：
  - **Pre**：查询重写 / 扩展（Multi-Query、HyDE）、混合检索（稠密向量 + 稀疏 BM25，RRF 融合）
  - **Post**：Reranking（Cross-Encoder 重排）、上下文压缩（LLMLingua）
- **目标**：最大化语义对齐、过滤无关信息，显著降低幻觉。
- **局限**：本质仍是**固定的单轮检索流程** —— 无法根据查询动态改变检索策略，遇到需要多跳推理的问题仍会失败。
- 🔗 这一阶段的完整链路见 [RAG Pipeline 5 阶段 SOTA 架构](../rag-pipeline/README.md)（Advanced RAG 的工程化落地）

### 3. Modular RAG（模块化 RAG）—— 组件解耦编排

- **核心能力**：打破固定线性管道，把系统解耦为**具有标准化接口的独立模块**，高度灵活可扩展。
- **关键模块**：Router（路由）/ Memory（记忆）/ Search（搜索）/ Predict（预测）/ Rewrite / Rerank / Read 等。
- **关键技术**：条件编排、并行编排、迭代检索、递归检索 —— 按任务动态组合模块。
- **优势**：
  - 适配多源异构数据（文本 / 表格 / 数据库 / 知识图谱）
  - 针对垂直场景低成本定制与迭代
- **局限**：编排逻辑仍由工程师**预先设计**，模块虽可插拔但"什么时候调哪个模块"是静态规则，尚未真正自主。

### 4. Agentic RAG（智能体 RAG）—— 自主决策规划

- **核心能力**：引入 LLM Agent 作为系统"大脑"，从被动响应转为**主动思考**。
- **关键技术**：意图理解 → 任务拆解 → 多步工具调用 → 自我反思与修正（Self-RAG / Corrective RAG / ReAct 循环）。
- **优势**：能处理高度复杂、需多轮推理和动态探索的开放式任务。
- **局限**：延迟高、Token 成本高、稳定性/可控性挑战大，需终止条件 + 死循环防护。
- 🔗 相关：[Agentic Search vs RAG](../../08-llmops/agentic-search-vs-rag/README.md)（AI Coding 场景下 Agentic 检索**取代** RAG 索引的极端案例）

---

## 🧭 关键澄清：演进四阶段 ≠ 5 阶段 Pipeline

> ⚠️ 最常见的混淆：把"四阶段演进"和 [rag-pipeline 的 5 阶段](../rag-pipeline/README.md) 混为一谈。两者是**正交**维度：

| 维度 | 说的是 | 例子 |
|------|-------|------|
| **演进四阶段** | RAG **范式代际**（能力成熟度） | Naive / Advanced / Modular / Agentic |
| **5 阶段 Pipeline** | 单次 RAG 的**执行环节**（机制） | Query Rewrite → Hybrid Search → Rerank → Compression → Generation |

**关系**：5 阶段 Pipeline 正是 **Advanced RAG** 阶段的典型工程实现；Modular RAG 把这 5 个环节**拆成可编排模块**；Agentic RAG 让 Agent 决定"跑不跑 Pipeline、跑几次"。

---

## 📊 四阶段横向对比

| 维度 | Naive | Advanced | Modular | Agentic |
|------|-------|----------|---------|---------|
| **检索轮次** | 单轮 | 单轮（优化） | 可迭代/递归 | 自主多步 |
| **流程** | 固定线性 | 固定线性 | 动态编排 | Agent 决策 |
| **查询理解** | 无 | 重写/扩展 | 路由分发 | 意图拆解 |
| **数据源** | 单一向量库 | 向量+BM25 | 多源异构 | 按需调工具 |
| **精度** | 低 | 高 | 高（可定制） | 最高（复杂任务） |
| **延迟/成本** | 最低 | 中 | 中高 | 最高 |
| **可控性** | 高 | 高 | 中 | 低（需防护） |
| **适用** | 原型验证 | 生产问答 | 垂直定制 | 复杂开放任务 |

---

## 🌲 选型决策树

```text
要做 RAG？
├─ 只是 Demo / 快速验证想法 → Naive RAG（1 天搭起来）
├─ 生产级文档问答，追求"查得准" → Advanced RAG（5 阶段 Pipeline 基线）
├─ 多源数据 / 需要按场景定制编排 → Modular RAG（组件解耦）
└─ 需要多跳推理 / 动态探索 / 自我修正 → Agentic RAG（引入 Agent，注意成本与防护）

💡 工程共识：Advanced + Modular 组合是高性价比基线，Agentic 按需局部引入。
```

---

## ⚠️ 反直觉

| 误区 | 真相 |
|------|------|
| ❌ 四阶段是替代关系，越新越好 | ✅ 继承与发展，Naive 在原型场景仍最优 |
| ❌ Agentic RAG 一定比 Advanced 好 | ✅ 简单问答用 Agentic = 杀鸡用牛刀（延迟/成本翻倍） |
| ❌ 演进四阶段 = Pipeline 五环节 | ✅ 前者是代际，后者是机制，正交（见上文澄清） |
| ❌ Modular RAG 就是自主的 | ✅ 编排规则仍是工程师预设，Agentic 才是自主决策 |
| ❌ 上了 Advanced 就没幻觉了 | ✅ 只解决"有据可依"，忠实性幻觉仍在 |

---

## 🔗 兄弟章节

- **本专题（Advanced 落地）**：[RAG Pipeline 5 阶段](../rag-pipeline/README.md) / [Query Rewrite](../query-rewrite/README.md) / [Hybrid Search](../hybrid-search/README.md) / [Reranker](../reranker/README.md) / [Chunking](../chunking-strategies/README.md)
- **Agentic 方向**：[Agentic Search vs RAG](../../08-llmops/agentic-search-vs-rag/README.md) / [Agent 执行模式](../../04-architecture/agent-execution-patterns/README.md)
- **LLMOps**：[RAG vs Fine-tuning](../../08-llmops/01-rag-vs-finetuning/README.md) / [RAG 评估](../../08-llmops/agent-evaluation/09-rag-evaluation/README.md)
- **咬文嚼字**：[RAG 面试深挖](../../../13.split-hairs/11.ai/rag/README.md)（含演进四阶段面试题）
- **餐厅叙事**：[开卷考试 · RAG](../../../12.story/36-rag-retrieval-augmented-generation.md)

---

← [返回 L2 技术栈](../README.md)
