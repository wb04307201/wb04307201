<!--
module:
  parent: ai
  slug: ai/agent-memory
  type: article
  category: 主模块子文章
  summary: Agent Memory 架构：时间 × 认知 × 工程三维分类 + 业界框架 + 选型决策
-->

# Agent Memory 架构 —— 时间 × 认知 × 工程 三维分类体系

← 返回 [架构设计](../README.md)

> Agent Memory 是 LLM Agent 的核心架构组件。本文从**时间维度**（短期/中期/长期）、**认知科学维度**（情景/语义/程序性）、**工程实现维度**（向量/结构化/文件系统）3 个维度系统讲清楚分类体系，并梳理业界框架（LangChain/LangGraph/Mem0/Letta）的实现差异。

> **面试场景**：这是高频 AI 架构面试题——很多人只想到"对话历史=Memory"，但完整分类是 3 维度、5 大类。面试版（30/60/90 秒话术）见 [咬文嚼字·11.ai/agent-memory-classification](../../../13.split-hairs/11.ai/agent-memory-classification/README.md)。

---

## 一、为什么 Memory 是 Agent 的核心

LLM Agent = **LLM（推理）+ Tools（行动）+ Memory（状态）**

- LLM：负责推理（无状态）
- Tools：负责与外部交互
- **Memory：负责"记住"——没有 Memory 的 Agent 是金鱼（每次对话从零开始）**

Memory 决定 Agent 的 3 大能力：

| 能力 | Memory 的作用 |
|------|--------------|
| **个性化** | 记住用户偏好、历史 |
| **连续性** | 跨会话状态保持 |
| **学习** | 从历史经验中提取模式 |

## 二、3 个维度的分类体系

### 2.1 维度 1：时间维度（最直觉）

```
┌─────────────────────────────────────────────────────────┐
│  短期（Short-term）                                       │
│  - 容量：4K-200K tokens（受 context window 限制）         │
│  - 生命周期：单次会话                                     │
│  - 实现：直接放 prompt                                    │
│  - 例子：当前对话的 10 轮历史                              │
├─────────────────────────────────────────────────────────┤
│  中期（Medium-term）                                       │
│  - 容量：数千 tokens（摘要/压缩后）                        │
│  - 生命周期：单次会话                                     │
│  - 实现：摘要 + 关键事件提取                              │
│  - 例子：1000 轮对话压缩成 100 tokens 的"过去 1 小时摘要"   │
├─────────────────────────────────────────────────────────┤
│  长期（Long-term）                                         │
│  - 容量：几乎无限                                         │
│  - 生命周期：跨会话                                       │
│  - 实现：向量库 / 数据库 / 文件系统                        │
│  - 例子：用户的偏好数据库                                  │
└─────────────────────────────────────────────────────────┘
```

**关键洞察**：3 层不是替代关系，是**叠加关系**——短期最快，中期压缩节省，长期持久化。

### 2.2 维度 2：认知科学维度（最深入）

源自人脑记忆模型（Atkinson-Shiffrin Memory Model）：

| 类型 | 内容 | Agent 例子 | 存储方式 |
|------|------|------------|---------|
| **情景记忆（Episodic）** | 具体事件 / 对话历史 | "用户 3 月 5 日问了 X 问题" | 时间序列 / KV（timestamp → content）|
| **语义记忆（Semantic）** | 通用知识 / 事实 | "用户偏好：中文、简洁风格、VIP" | 实体-属性图谱 / KV |
| **程序性记忆（Procedural）** | 技能 / 操作流程 | "调用天气 API 的步骤" | 工具描述 / 流程定义 / DSL |

**3 类记忆的读取时机完全不同**：

| 类型 | 何时读 | 触发条件 |
|------|--------|---------|
| 情景 | 每次新对话 | 必读（建立连续性）|
| 语义 | 需要做决策时 | "用户说 X 是什么意思？" → 读偏好 |
| 程序性 | 需要执行操作时 | "调 API" → 读工具描述 |

### 2.3 维度 3：工程实现维度（最实用）

| 类型 | 数据结构 | 检索方式 | 适用内容 | 代表工具 |
|------|---------|----------|---------|---------|
| **全量上下文** | Prompt 文本 | 无需检索 | 高频关键信息 | 直接 inline |
| **向量记忆** | Embedding + 向量库 | 相似度检索 | 大量历史对话 / 文档 | Pinecone / Milvus / Qdrant |
| **结构化记忆** | SQL / KV / Graph | 精确查询 | 用户偏好 / 实体属性 | Postgres / Neo4j / Redis |
| **文件系统记忆** | Markdown / JSON | 文件路径 + 全文检索 | 长文档 / 笔记 | Obsidian / Notion |
| **外部记忆** | RAG / 知识库 / API | 实时检索 | 最新信息 / 第三方数据 | LangChain / LlamaIndex |

**生产 Agent 的典型组合**：

```python
# 示例：智能客服 Agent 的 Memory 配置
memory_config = {
    "short_term": {
        "type": "in_context",  # 当前对话历史
        "max_tokens": 8000,
    },
    "long_term_episodic": {
        "type": "vector_store",  # 历史对话向量检索
        "backend": "Pinecone",
        "namespace": "user_123_history",
    },
    "long_term_semantic": {
        "type": "structured_kv",  # 用户偏好
        "backend": "Redis",
        "schema": {"language": "zh", "style": "concise", "tier": "VIP"},
    },
    "long_term_procedural": {
        "type": "tool_descriptions",  # API 流程
        "backend": "MCP_server",
        "tools": ["weather_api", "order_api"],
    },
    "external": {
        "type": "rag",  # 最新政策文档
        "backend": "LlamaIndex",
        "index": "policy_docs_2026",
    },
}
```

## 三、Memory 的核心设计问题：何时写、读、忘

### 3.1 何时写（Write Trigger）

| 场景 | 触发条件 | 写到哪 |
|------|---------|--------|
| 用户表达偏好 | "我以后都用中文" | 语义记忆（KV）|
| 完成关键任务 | Agent 解决了 X 问题 | 情景记忆（带结果）|
| 用户纠正错误 | "你刚才说错了" | 语义记忆（更正）|
| 对话自然结束 | 会话结束 hook | 摘要压缩到中期 |

### 3.2 何时读（Read Trigger）

| 场景 | 触发条件 | 读哪些 |
|------|---------|--------|
| 新对话开始 | 必读 | 用户偏好（语义）+ 最近摘要（中期）|
| 决策需要历史 | "上次怎么处理的？" | 检索情景记忆 |
| 执行操作 | "调 API" | 读工具描述（程序性）|
| 回答事实问题 | "我们公司的政策是？" | RAG 外部记忆 |

### 3.3 何时忘（Forget Policy）

**Memory 是有成本的，必须有生命周期**：

| 策略 | 适用场景 |
|------|---------|
| **TTL（过期删除）** | 临时状态（订单号、token）|
| **LRU（最近最少使用）** | 缓存场景 |
| **重要性衰减** | 旧事件逐步降权 |
| **容量上限 + LRU** | 长期记忆有总容量上限 |

**核心原则**：**只存对决策有用的信息**——过度存储会让检索变慢、token 浪费、信号噪声比下降。

## 四、业界框架对比

### 4.1 LangChain Memory 体系

| 类型 | 实现 | 优缺点 |
|------|------|--------|
| `ConversationBufferMemory` | 滑动窗口 | 简单；但受 token 限制 |
| `ConversationSummaryMemory` | LLM 摘要 | 节省 token；但丢失细节 |
| `ConversationEntityMemory` | 实体抽取 | 适合偏好；但抽取不准 |
| `VectorStoreMemory` | 向量检索 | 适合大量历史；但检索不准 |
| `CombinedMemory` | 多 Memory 组合 | 灵活；但复杂度高 |

### 4.2 LangGraph Checkpoint

**核心思想**：每步状态持久化到数据库（SQLite/Postgres），可恢复任意步。

```python
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# thread_id 决定会话
config = {"configurable": {"thread_id": "user-123"}}
```

**适用**：需要"时间旅行"调试 / 多步状态恢复的场景。

### 4.3 Mem0 / Letta / Zep（2024-2026 新晋）

| 框架 | 核心创新 | 适用 |
|------|---------|------|
| **Mem0** | 自动分层 Memory（短期/长期自动判断）| 个人 AI 助手 |
| **Letta** | 类人记忆模型（block-based）| 长会话 Agent |
| **Zep** | 消息级 Memory + 时序图谱 | 客服 / CRM |

**共同特点**：自动管理 Memory 生命周期，开发者只关心"读什么"。

### 4.4 LlamaIndex

**核心思想**：实体抽取 + 关系图谱

```python
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(
    token_limit=3000,
)
```

**适用**：需要复杂实体关系的企业 Agent。

## 五、Memory 在完整 Agent 架构中的位置

### 5.1 与已有架构组件的关系

```
Agent 整体架构：
├── LLM（推理）
├── Tools（行动）
├── Memory ← 本文
├── Planning（任务规划）
└── Reflection（自我反思）
```

### 5.2 Memory × Agent 执行架构（DAG / ReAct / Plan-Execute）

详见 [Agent 执行架构对比](../agent-architecture/README.md)：

| 执行架构 | Memory 的特殊要求 |
|---------|------------------|
| **DAG** | 每个节点需要独立的 Memory 上下文 |
| **ReAct** | ReAct 循环内每步需短期记忆 + 反思结果 |
| **Plan-and-Execute** | Plan 步骤需长期记忆 + Execute 步骤需短期 |

### 5.3 Memory × 驾驭演进主线

Memory 演进是 [驾驭演进主线](../llm-control-evolution/README.md) 的具体展开：

| 驾驭阶段 | Memory 形态 |
|---------|------------|
| Prompt | 无 Memory（单次对话）|
| Context | 短期 Memory（context window）|
| Harness | 长期 Memory + 校验（CLAUDE.md / Skills）|
| Loop | 跨会话 Memory + 自动分层（Mem0 / Letta）|

## 六、Memory 设计的 5 大反模式

### 6.1 反模式 1：把 Memory 当成"对话历史"

只存对话历史会**丢失用户偏好、技能、外部知识**。

### 6.2 反模式 2：全量塞进 prompt

短期 Memory 不是"全量对话历史"，应**摘要压缩或滚动窗口**。

### 6.3 反模式 3：忽视 Memory 一致性

多 Agent 场景下，共享 Memory 需要**版本控制 + 冲突解决**。

### 6.4 反模式 4：Memory 永不过期

无 TTL 会导致**存储爆炸 + 检索变慢 + 噪声污染**。

### 6.5 反模式 5：忽视 Memory 写入成本

每次新信息都写库 → **写入延迟** + **存储成本**——按需写而非全写。

## 七、实战选型决策

### 7.1 决策矩阵

| 场景 | 推荐 Memory 组合 |
|------|-----------------|
| **简单客服 Agent** | 短期（Buffer）+ 长期语义（KV 存偏好）|
| **长会话个人助手** | 短期（Buffer）+ 中期（Summary）+ 长期（Mem0 自动分层）|
| **多 Agent 协作** | LangGraph Checkpoint + 共享 Vector Store |
| **企业知识库** | RAG + 实体图谱（Neo4j）|
| **AI Coding 工具** | LangGraph Checkpoint + 文件系统（CLAUDE.md）|

### 7.2 容量与性能经验值

| 指标 | 经验值 |
|------|--------|
| 短期 token 上限 | 8K-16K（避免爆 context）|
| 中期摘要压缩比 | 10:1（1000 轮 → 100 tokens）|
| 长期记忆检索 top-k | 3-5（避免 prompt 过长）|
| 写入触发频率 | 每 5-10 轮一次（避免写入风暴）|

## 八、相关章节

**面试题**：
- [咬文嚼字·11.ai/agent-memory-classification（30/60/90 秒话术）](../../../13.split-hairs/11.ai/agent-memory-classification/README.md)
- 🆕 **[咬文嚼字·multi-agent-shared-memory 多 Agent 共享记忆](../../../13.split-hairs/11.ai/multi-agent-shared-memory/README.md)** —— 5 大内容维度 + 3 实现层 + 6 模式 + 5 反模式 + 90 秒话术

**同主模块**：
- [Agent 执行架构（DAG/ReAct/Plan）](../agent-architecture/README.md)
- [驾驭演进主线（Prompt→Context→Harness→Loop）](../llm-control-evolution/README.md)
- [智能系统分层架构](../intelligent-system-layers/README.md)

**实战框架**：
- [LangGraph（Checkpoint）](../../03-engineering/ai-platforms/langgraph.md)
- [Context Engineering（Memory 是 Context 三大件之一）](../../02-technology-stack/context-engineering/README.md)
- 🆕 **长上下文全景（Memory 是 6 策略之一）**：[Agent 长上下文架构](../agent-context/README.md) —— Chunking / Memory / RAG / Sliding Window / Sub-Agents / Long-Context LLMs 6 策略组合决策树

**多 Agent 共享专章（跨域交叉）**：
- 🆕 **[shared-memory.md](./shared-memory.md)** —— 多 Agent 共享记忆：5 大内容维度 + 3 实现层（消息/状态/语义）+ 6 共享模式 + 一致性协议 + 6 实战框架（CrewAI/AutoGen/LangGraph/MetaGPT 等）

**同栏目其他面试题**：
- [咬文嚼字·11.ai（RAG / Dropout / Harness 等）](../../../README.md)

---

## 📊 本节统计

- **覆盖深度**：3 个维度（时间 / 认知 / 工程）+ 5 大问题（写/读/忘/一致/成本）
- **业界框架**：4 类（LangChain / LangGraph / Mem0 / LlamaIndex）
- **实战决策**：5 大场景 + 4 项经验值
- **关联章节**：4 大类（面试题 / 主模块 / 框架 / 同栏目）

---

> 📅 2026-07-03 · 11.ai/04-architecture · ⭐⭐⭐⭐

← [返回: AI 知识体系 · agent-memory](README.md)
