<!--
module:
  parent: ai
  slug: ai/tech-stack
  type: index
  category: 主模块子文章
  summary: LLM 技术栈全景（61 核心概念 + 多模态 + Prompt/Context/Harness/Loop 四阶段演进 + RAG 全链路 + 向量检索 3 级规模）
-->

# L2 技术栈

> 从模型架构到应用编排，全景理解大语言模型生态。

## 1. 目录导航

| 目录 | 核心内容 | 一句话定位 |
|------|---------|-----------|
| [concept-map](concept-map/) | **LLM 技术栈全景** — 6大层 61 个核心概念，含 Mermaid 架构图、选型指南、生产部署检查清单 | 全局认知地图 |
| [multimodal](multimodal/) | 多模态感知-认知统一架构、跨模态特征对齐、多模态交互体验优化 | 视觉/音频/视频融合 |
| [memory-estimation](memory-estimation/) | 大模型显存估算指南 — Transformer / MoE / Mamba 三大架构的训练/推理显存公式 | 资源规划必备 |
| [prompt-engineering](prompt-engineering/) | **Prompt 工程** — 8 种核心技巧（Zero-shot/Few-shot/CoT）+ 注入防御 + 调试优化 + 子目录：模板/系统提示/创意注释 | LLM 入门第一道 |
| [context-engineering](context-engineering/) | **Context Engineering** — Prompt → Context 范式转移、4 大原则、Lost in Middle、Context Window 限制 | Agent 时代主流 |
| [function-calling](function-calling/) | **Function Calling / Tool Use** — OpenAI / Claude 协议对比、多轮编排、5 大场景、5 大安全陷阱 | Agent 工具调用基础 |
| 🆕 [structured-output](structured-output/) | **结构化输出（JSON）** — 5 种稳定性策略 + response_format + Instructor/Outlines 框架对比 + 反模式 | 工程落地必备 |
| [token-billing](token-billing/) | **Token 与计费** — BPE / WordPiece / SentencePiece、上下文窗口、计费模型、Token 优化 | 成本控制核心 |
| 🆕 [llm-inference-optimization](llm-inference-optimization/) | **LLM 推理优化大专题** — 10 章：KV Cache / PagedAttention / Continuous Batching / Speculative / 量化 / MoE / 指标 / 框架 | 生产性能核心 |
| 🆕 [kv-cache](kv-cache/) | KV Cache 推理核心机制 | 自回归加速 |
| 🆕 [paged-attention](paged-attention/) | vLLM PagedAttention 解决 KV Cache 碎片 | 显存利用率 40%→96% |
| 🆕 [continuous-batching](continuous-batching/) | Continuous Batching 动态调度 | 吞吐量 23x |
| 🆕 [speculative-decoding](speculative-decoding/) | Speculative Decoding 投机解码 | 加速 2-3x |
| 🆕 [weight-quantization](weight-quantization/) | 权重量化 GPTQ/AWQ/GGUF/NF4 | 显存省 4x |
| 🆕 [moe-inference](moe-inference/) | MoE 推理优化（DeepSeek-V3 实战）| 671B 8x A100 |
| 🆕 [inference-metrics](inference-metrics/) | 推理性能指标 TTFT/TPOT/Throughput | 服务质量金三角 |
| 🆕 [inference-frameworks](inference-frameworks/) | 推理框架对比 vLLM/TGI/SGLang/TRT-LLM | 选型决策树 |

### 1.1 学习路径

建议顺序：concept-map（全局认知）→ multimodal（感知扩展）→ memory-estimation（资源规划）→ **Prompt → Context → Function Calling → Token 计费**（AI 工程 4 阶段演进）。

### 1.2 RAG 与检索技术

| 目录 | 核心内容 | 一句话定位 |
|------|---------|-----------|
| **RAG 管线** | | |
| [rag-pipeline](rag-pipeline/) | RAG 完整 Pipeline 综述 — 5 阶段 SOTA 架构 | 全链路总览 |
| [chunking-strategies](chunking-strategies/) | 5 大 Chunking 策略对比（固定/递归/语义/滑动/Agentic） | 检索质量 20-40% |
| [query-rewrite](query-rewrite/) | Query Rewrite 查询改写提升 RAG 召回 10-20% | 多轮对话必备 |
| [reranker](reranker/) | Cross-Encoder Reranker 重排序，精确率高 15-30% | 精排核心 |
| [hybrid-search](hybrid-search/) | 向量 + BM25 混合检索，召回率高 15-25% | 生产标配 |
| **向量搜索** | | |
| [vector-search-algorithms](vector-search-algorithms/) | HNSW vs IVF vs DiskANN 3 大算法选型 + 4 维权衡 | 10 亿级选型 |
| [vector-search-at-scale](vector-search-at-scale/) | 千亿级向量检索 5 个架构转变 | 分布式 + GPU |
| [vector-search-trillion](vector-search-trillion/) | 万亿级向量检索多集群联邦 + 专用硬件 | 前沿探索 |
| **上下文与检索** | | |
| [embedding-models](embedding-models/) | BGE / M3E / Qwen / OpenAI 4 大 Embedding 模型横评 | 选对提升 20-30% |
| [lost-in-middle](lost-in-middle/) | Lost In the Middle 现象 + 6 大缓解方案 | 长 Context 必修 |
| [yarn-context-extension](yarn-context-extension/) | YaRN / RoPE 长度扩展 2K → 128K-1M | 长上下文基础 |

---

## 2. 知识脉络

```mermaid
graph LR
    A[concept-map<br/>61 核心概念全景] --> B[multimodal<br/>感知扩展]
    A --> C[memory-estimation<br/>资源规划]
    A --> D[prompt<br/>输入引导]
    D --> E[context<br/>完整上下文]
    E --> F[function-calling<br/>工具调用]
    F --> G[token-billing<br/>成本控制]

    A --> R[rag-pipeline<br/>全链路综述]
    R --> R1[query-rewrite<br/>查询改写]
    R --> R2[hybrid-search<br/>混合检索]
    R --> R3[reranker<br/>重排序]
    R --> R4[chunking-strategies<br/>文档分块]

    V[vector-search-algorithms<br/>10 亿级] --> V2[vector-search-at-scale<br/>千亿级]
    V2 --> V3[vector-search-trillion<br/>万亿级]

    E --> EM[embedding-models<br/>模型横评]
    E --> LM[lost-in-middle<br/>中间遗忘]
    LM --> Y[yarn-context-extension<br/>长度扩展]
```

---

## 3. 速查表

| 概念 | 核心要点 | 典型场景 |
|------|---------|---------|
| **Prompt Engineering** | Zero-shot / Few-shot / CoT / Role / 模板 | 单轮 LLM 调用 |
| **Context Engineering** | 系统提示 + 工具 + 历史 + RAG + 记忆 | Agent 多轮任务 |
| **Function Calling** | OpenAI / Claude 协议；JSON Schema 描述工具 | Agent 工具扩展 |
| **Token** | BPE / WordPiece / SentencePiece 分词 | 计费与上下文窗口 |
| **多模态** | VLM（视觉-语言）/ 音频 / 视频统一表征 | 跨模态任务 |
| **显存估算** | 模型参数 + 优化器 + 激活 + KV Cache | 训练/推理资源规划 |
| **MCP** | Model Context Protocol，标准化工具接入 | 跨厂商 Agent 互操作 |
| **RAG Pipeline** | Query Rewrite → Hybrid Search → Rerank → Generation | 知识检索增强生成 |
| **Query Rewrite** | LLM 改写口语化 / 不完整 query | 多轮对话 RAG |
| **Hybrid Search** | 向量（语义）+ BM25（关键词）RRF 融合 | 生产环境标配 |
| **Reranker** | Cross-Encoder 精排，精确率高 15-30% | Top-100 → Top-10 |
| **Chunking** | 固定 / 递归 / 语义 / 滑动窗口 / Agentic | 检索质量 20-40% |
| **向量检索算法** | HNSW / IVF / DiskANN 4 维权衡 | 10 亿级选型 |
| **Embedding 模型** | BGE-M3 / M3E / Qwen / OpenAI 横评 | 召回率基石 |
| **Lost in Middle** | 长 Context 中间段召回率低，U 型曲线 | 结构化排版缓解 |
| **YaRN** | RoPE 长度扩展 2K → 128K-1M | 长上下文基础 |

---

## 4. 核心内容（按子模块展开）

- **[concept-map](concept-map/)**：6 大层 61 核心概念全景图（模型基础 / 训练优化 / 推理加速 / 检索知识 / 应用编排 / 治理运维）
- **[multimodal](multimodal/)**（+ 2 子）：
  - [cross-modal-alignment](multimodal/cross-modal-alignment/) — 跨模态特征对齐
  - [multi-modal-interaction](multimodal/multi-modal-interaction/) — 多模态交互体验
- **[memory-estimation](memory-estimation/)**：Transformer / MoE / Mamba 三大架构的训练/推理显存公式
- **[prompt-engineering](prompt-engineering/)**（+ 3 子）：
  - [code-comment-styles](prompt-engineering/code-comment-styles/) — 创意注释代码风格
  - [grok-system-prompt](prompt-engineering/grok-system-prompt/) — Grok 系统提示拆解
  - [prompt-templates](prompt-engineering/prompt-templates/) — 提示模板库
- **[context-engineering](context-engineering/)**：Lost in Middle、4 大原则、Context Window 限制
- **[function-calling](function-calling/)**：5 大场景（搜索/计算/API/数据库/文件操作）+ 5 大安全陷阱
- **[token-billing](token-billing/)**：BPE / WordPiece / SentencePiece 对比；Token 优化技巧
- **[rag-pipeline](rag-pipeline/)**：5 阶段 SOTA 架构（Query Rewrite → Hybrid Search → Rerank → Context Compression → Generation）
- **[chunking-strategies](chunking-strategies/)**：5 大策略对比（固定 / 递归 / 语义 / 滑动窗口 / Agentic），直接影响检索质量
- **[query-rewrite](query-rewrite/)**：LLM 改写用户 query，多轮对话指代消解，召回率提升 10-20%
- **[reranker](reranker/)**：Bi-Encoder vs Cross-Encoder 对比，BGE-reranker / Cohere Rerank 选型
- **[hybrid-search](hybrid-search/)**：向量 + BM25 RRF 融合，互补召回，生产环境标配
- **[vector-search-algorithms](vector-search-algorithms/)**：HNSW / IVF / DiskANN 3 大算法原理 + 4 维权衡（内存/磁盘/QPS/Recall）
- **[vector-search-at-scale](vector-search-at-scale/)**：千亿级 5 个架构转变 + 分层索引 + ScANN + GPU + 联邦检索
- **[vector-search-trillion](vector-search-trillion/)**：万亿级多集群联邦 + 专用硬件 + 边缘计算 + 极限压缩
- **[embedding-models](embedding-models/)**：BGE-M3 / M3E / Qwen3-Embedding / OpenAI text-embedding-3 横评
- **[lost-in-middle](lost-in-middle/)**：U 型曲线现象 + 6 大缓解方案（结构化排版 / 重复 / Self-Ask 等）
- **[yarn-context-extension](yarn-context-extension/)**：YaRN = 频率基数 + NTK-aware + 注意力缩放，2K → 128K-1M

---

## 5. 最佳实践

| 场景 | 实践要点 |
|------|---------|
| **Prompt → Context 演进** | 单轮 Prompt 已不够；Agent 时代用 Context Engineering 提供完整上下文 |
| **Token 优化** | 系统提示精简 + Few-shot 示例压缩 + 输出长度限制 + 流式响应 |
| **Function Calling 安全** | 工具白名单 + 参数校验 + 输出过滤 + 速率限制 + 审计日志 |
| **多模态选型** | 文本任务用纯 LLM；图文任务用 VLM（GPT-4o / Qwen-VL）；视频任务用专用视频模型 |
| **显存估算** | 训练显存 = 模型 + 优化器(2-8x) + 激活 + Batch；推理显存 = 模型 + KV Cache |
| **RAG 生产部署** | Chunking 策略选语义/递归 → Embedding 选 BGE-M3/Qwen → Hybrid Search → Cross-Encoder Rerank → 结构化排版防 Lost in Middle |

---

## 6. 常见面试题

| 题目 | 核心考点 |
|------|---------|
| BPE / WordPiece / SentencePiece 区别？ | 字节级 vs 词级 vs 字符级分词 |
| Context Engineering 4 大原则？ | 选信息 / 排结构 / 防过载 / 持续更新 |
| Function Calling 协议对比？ | OpenAI tools vs Claude tool_use |
| Token 优化技巧？ | 系统提示精简 + Few-shot 压缩 + 输出限长 |
| 显存估算公式？ | 模型参数 × 精度字节数 + 优化器状态 + 激活 + KV Cache |
| Lost in Middle 问题？ | 长上下文中部信息被忽略，结构化排版可缓解 |
| MCP 协议价值？ | 跨厂商 Agent 工具互操作标准 |
| RAG Pipeline 5 阶段？ | Query Rewrite → Hybrid Search → Rerank → Context Compression → Generation |
| Bi-Encoder vs Cross-Encoder？ | 独立编码快速 vs 联合编码精确，Reranker 用 Cross-Encoder |
| HNSW vs IVF vs DiskANN 选型？ | 内存图高召回 / 聚类省内存 / 磁盘友好，按规模选 |
| Hybrid Search 为什么是标配？ | 向量抓语义 + BM25 抓关键词，互补召回率 +15-25% |

---

## 7. 相关章节

- 上游：[L1 基础概念](../01-fundamentals/) → **L2 技术栈** → [L3 工程实践](../03-engineering/)
- 关联：[04.system-design](../../04.system-design/) — 系统设计（AI 系统也遵循通用设计原则）
- 面试：[13.split-hairs AI 新概念](../../13.split-hairs/11.ai/README.md) — AI 面试深挖（精炼版）

---

## 8. 开源参考

| 类别 | 项目 |
|------|------|
| 概念全景 | [LLM 技术栈全景图 (61 核心概念)](concept-map/) |
| 多模态 | GPT-4o · Gemini 2.0 · Qwen2.5-VL · Whisper |
| Prompt 框架 | LangChain PromptTemplate · Guidance · Outlines |
| Context 框架 | LlamaIndex · LangChain Memory · Mem0 |
| Function Calling | OpenAI Function Calling · Claude Tool Use · MCP |
| Token 工具 | tiktoken (OpenAI) · sentencepiece (Google) · tokenizers (Hugging Face) |
| RAG 框架 | LlamaIndex · LangChain · Haystack · RAGFlow |
| 向量数据库 | Milvus · Qdrant · Weaviate · Pinecone · pgvector |
| Embedding | BGE-M3 (BAAI) · M3E · Qwen3-Embedding · text-embedding-3 (OpenAI) |
| Reranker | BGE-reranker (BAAI) · Cohere Rerank · jina-reranker |

---

## 📊 本节统计

| 维度 | 数字 |
|------|------|
| 一级子目录数 | 28 |
| 一级 leaf README 数 | 28 |
| 二级 leaf README 数 | 5（multimodal:2 + prompt-engineering:3） |
| 总 leaf README 数 | 33 |
| 速查表条目数 | 16 |
| 最佳实践条数 | 6 |
| 常见面试题数 | 11 |
| 开源参考项目数 | 10 类共 25+ 条 |
| frontmatter 覆盖 | 33 / 33 = 100% |
| 文末回链覆盖 | 33 / 33 = 100% |

---

← [返回 AI 知识体系](../README.md)