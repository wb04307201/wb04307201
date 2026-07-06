<!--
question:
  id: 11.ai-agent-memory
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构辨析
  tags: [11.ai, Agent, Memory, 记忆, 架构]
-->

# Agent 的 Memory 分哪几类？ — 时间×认知×工程三维分类法

> 一句话定位：Agent Memory 是 LLM Agent 的核心架构概念，从**时间维度**（短期/长期）、**认知科学**（情景/语义/程序）、**工程实现**（向量/结构化/文件系统）3 个维度形成完整分类。深度原理见 [主模块 Agent Memory 架构](../../../11.ai/04-architecture/agent-memory/README.md) + [Agent 执行架构对比](../../../11.ai/04-architecture/agent-architecture/README.md)。

> **系列定位**：经典 AI 架构面试题（高频）。考察的不是"Memory 是什么"，而是 **三维分类体系的完整度** + **场景适配的选择能力** + **业界框架的能力边界**。

---

⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：LLM Agent 基本架构、Context Engineering、RAG、向量数据库

---

## 引子：面试官的"维度切换"陷阱

阿明去面试某 Agent 创业公司，面试官问："你们 Agent 怎么管理 Memory？"

阿明答："用 LangChain 的 ConversationBufferMemory，存对话历史。"

面试官追问："那用户的偏好怎么记？比如他喜欢中文、简洁风格——这个也在 buffer 里吗？"

阿明答："也在 buffer 里。"

面试官："但 buffer 是**对话历史**，用户的**偏好**是**事实知识**——这两类东西放一起合理吗？"

阿明答："……好像不太合理。"

面试官再追问："如果用户和 Agent 聊了 1000 轮，buffer 已经 50000 tokens 了，你还全量塞进 prompt 吗？"

阿明答："……应该不会。"

面试官："那你的**短期记忆**怎么和**长期记忆**配合？"

阿明彻底答不上来。

**这道题的陷阱在于**：很多人只想到"对话历史 = Memory"，但 Agent Memory 至少有 3 个维度、5 大类、10+ 业界方案。完整的分类体系是这样的：

| 维度 | 分类 |
|------|------|
| **时间** | 短期（context window）/ 中期（会话内压缩）/ 长期（跨会话持久化） |
| **认知科学** | 情景（episodic）/ 语义（semantic）/ 程序性（procedural） |
| **工程实现** | 全量上下文 / 向量记忆 / 结构化（SQL/KV/Graph）/ 文件系统 / 外部 RAG |

今天我们就讲清楚：**三维分类法 + 业界框架 + 选型决策**。

## 一、核心原理：3 个维度的分类法

### 1.1 维度 1：时间维度（最直觉）

| 类型 | 容量 | 生命周期 | 实现 |
|------|------|----------|------|
| **短期记忆（Short-term / Working Memory）** | 受 context window 限制（4K-200K tokens）| 单次会话 | 直接放 prompt |
| **中期记忆（Medium-term）** | 摘要 / 压缩后的关键信息 | 单次会话 | 摘要 + 关键事件提取 |
| **长期记忆（Long-term）** | 几乎无限 | 跨会话 | 向量库 / 数据库 / 文件系统 |

**关键洞察**：短期是"工作台"，中期是"工作笔记"，长期是"档案柜"。三者配合才能撑起完整 Agent。

### 1.2 维度 2：认知科学维度（最深入）

源自人脑记忆分类：

| 类型 | 内容 | Agent 中的例子 |
|------|------|----------------|
| **情景记忆（Episodic Memory）**| 具体事件 / 对话历史 | "用户 3 月 5 日问了 X 问题，我回答错了" |
| **语义记忆（Semantic Memory）**| 通用知识 / 事实 | "用户偏好：中文、简洁风格、VIP" |
| **程序性记忆（Procedural Memory）**| 技能 / 操作流程 | "调用天气 API 的步骤：参数构造→发送→解析" |

**关键洞察**：这 3 类在 Agent 中有完全不同的存储方式和读取时机。
- 情景记忆 → 时间序列存储（按时间戳索引）
- 语义记忆 → 实体-属性存储（Key-Value 或图谱）
- 程序性记忆 → 流程定义（YAML/DSL/工具描述）

### 1.3 维度 3：工程实现维度（最实用）

| 类型 | 数据结构 | 检索方式 | 适用场景 |
|------|---------|----------|---------|
| **全量上下文（In-context）** | Prompt 文本 | 无需检索 | 短期记忆 / 高频关键信息 |
| **向量记忆（Vector Memory）** | Embedding + 向量库 | 相似度检索 | 大量历史对话 / 文档片段 |
| **结构化记忆（Structured）** | SQL / KV / Graph | 精确查询 | 用户偏好 / 实体属性 |
| **文件系统记忆（File Memory）** | Markdown / JSON / 文件 | 文件路径 + 全文检索 | 长文档 / 笔记 / 知识库 |
| **外部记忆（External）** | RAG / 知识库 / API | 实时检索 | 最新信息 / 第三方数据 |

**关键洞察**：没有银弹——**生产 Agent 通常组合 3-4 种实现**，按内容类型分库存储。

### 1.4 业界框架视角

| 框架 | Memory 类型 | 特点 |
|------|-------------|------|
| **LangChain BufferMemory** | 滑动窗口 | 简单，但容量受限 |
| **LangChain SummaryMemory** | 摘要压缩 | 节省 token，但丢失细节 |
| **LangChain EntityMemory** | 实体-属性 | 适合用户偏好 |
| **LangChain VectorStoreMemory** | 向量检索 | 适合大量历史 |
| **LangGraph Checkpoint** | 状态持久化 | 每步状态可恢复 |
| **Mem0 / Letta / Zep** | 多层 Memory | 2024-2026 新晋，自动分层管理 |
| **LlamaIndex** | 实体 + 关系抽取 | 适合复杂知识图谱 |

## 二、常见陷阱（面试必踩）

### 陷阱 1：把 Memory 当成"对话历史"

错。Memory 是**多维度多层**的，对话历史只是"情景记忆"的一部分。

### 陷阱 2：以为"长期记忆 = 向量库"

错。长期记忆可以是向量库 / 数据库 / 文件系统 / Graph——按内容类型选。

### 陷阱 3：把"短期"和"长期"搞混

半对。准确说法：
- 短期 → context window（必填）
- 中期 → 摘要/压缩（可选，节省 token）
- 长期 → 跨会话持久化（按需）

### 陷阱 4：以为 Memory 越多越好

错。**Memory 是有成本的**：
- 写入成本（每次新信息都要判断写到哪层）
- 读取成本（检索 token 消耗）
- 一致性成本（多源冲突解决）

**核心原则**：**只存对决策有用的信息**。

### 陷阱 5：把"Context Engineering"和"Memory"混为一谈

错。Context 是"当前要给 LLM 看的信息"，Memory 是"持久化的状态"。**Context 包含 Memory 的子集**。

### 陷阱 6：忽视多 Agent 共享 Memory 的复杂性

错。多 Agent 场景下：
- 共享 Memory（协作需要）vs 私有 Memory（隔离需要）
- 一致性 / 冲突解决
- 权限控制

## 三、面试话术（90 秒版本）

面试官："Agent 的 Memory 分哪几类？"

**30 秒简版**：

> "我习惯从 3 个维度看 Memory 分类：
> 第一，**时间维度**：短期（context window）/ 中期（会话内摘要）/ 长期（跨会话持久化）；
> 第二，**认知科学维度**：情景（具体事件）/ 语义（事实知识）/ 程序性（技能流程）；
> 第三，**工程实现维度**：全量上下文 / 向量 / 结构化（SQL/KV/Graph）/ 文件系统 / 外部 RAG。
> 生产 Agent 通常按内容类型**组合 3-4 种实现**——比如用户偏好用 KV，文档用向量，对话历史用时间序列索引。"

**60 秒扩展版**（如果面试官追问）：

> "具体来说，Agent Memory 的核心设计问题是**'何时写、读、忘'**：
> **写**：每次 Agent 行动后，决定哪些信息值得持久化（不能全存，会爆炸）
> **读**：根据当前任务，召回相关 Memory 子集（不能用全量，会爆 token）
> **忘**：Memory 应该有生命周期——过期信息自动清理（避免污染决策）
>
> 业界框架各有侧重：LangChain 偏 Buffer/Summary 简单实现，LangGraph 偏 Checkpoint 状态持久化，Mem0/Letta/Zep 是 2024-2026 新晋的**自动分层 Memory** 框架。
>
> 最后强调一点：**Memory 是 Context Engineering 的核心子集**，但 Memory 是持久化状态，Context 是当前给 LLM 看的信息——两者有交集但不等同。"

## 四、相关章节

**主模块**：
- [11.ai/04-architecture/agent-memory（深度原理）](../../../11.ai/04-architecture/agent-memory/README.md)
- [11.ai/04-architecture/agent-architecture（执行架构对比）](../../../11.ai/04-architecture/agent-architecture/README.md)
- [11.ai/04-architecture/llm-control-evolution（驾驭演进）](../../../11.ai/04-architecture/llm-control-evolution/README.md)
- [11.ai/02-technology-stack/context-engineering（Context Engineering）](../../../11.ai/02-technology-stack/context-engineering/README.md)

**同栏目（11.ai 高频面试题）**：
- [Transformer 架构深挖](../transformer/README.md)
- [RAG 架构设计](../rag/README.md)
- [Harness Engineering 概念辨析](../harness-engineering/README.md)
- [大模型中为什么不用 Dropout](../dropout-in-llm/README.md)
- [Claude Code 放弃 RAG 的反直觉](../claude-code-agentic-search/README.md)

**实战框架**：
- [11.ai/03-engineering/ai-platforms/langgraph（MemorySaver）](../../../11.ai/03-engineering/ai-platforms/langgraph.md)

---

> 📅 2026-07-03 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · agent-memory-classification](README.md)
