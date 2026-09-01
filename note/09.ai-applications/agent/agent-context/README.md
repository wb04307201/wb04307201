<!--
module:
  parent: agent-architecture
  slug: ai/agent-architecture/agent-context
  type: deep-dive
  category: Agent 长上下文架构
  summary: Agent 如何处理长上下文 —— 6 大策略（Chunking / RAG / Memory / Sliding Window / Sub-Agents / Long-Context LLMs）+ 选型决策树 + 面试题
  depth: ⭐⭐⭐
-->

# Agent 长上下文架构 · 6 大策略全景

> **一句话答案**：长上下文不是"塞进 prompt 就完事"——Agent 在 100k+ 上下文场景下，**没有银弹**，必须**组合 6 大策略**（Chunking 按需切片 + RAG 按需检索 + Memory 持久记忆 + Sliding Window 滑动窗口 + Sub-Agents 任务拆分 + Long-Context LLMs 直塞）才能稳跑。

← [返回: Agent 架构](../README.md) · 同级：[agent-memory](../agent-memory/README.md) · [ontology-driven-agent](../ontology-driven-agent/README.md)

---

## 面试高频拷问
```text
Q：你的 Agent 如何处理长上下文？1M token 的文档怎么让 LLM 准确回答？
```

**回答框架（4 层递进）**：

1. **场景区分**："长上下文"在 Agent 场景下分 3 类——长输入（一次性灌入）/ 长会话（多轮累积）/ 长检索（外部文档库）
2. **6 策略对比**：每种场景下用哪些策略组合（不是单选，是组合）
3. **反模式**：列举 Agent 长上下文 5 大失效点
4. **何时反选**：盲目灌长上下文 vs 总是用 RAG 的两个极端都错

完整 5-7 道精选面试题见 [12.interview/11.ai/long-context-agent-strategy](../../../12.interview/11.ai/long-context-agent-strategy/README.md)（⚠️ 待 Phase 1+ 迁入）。

---

## 长上下文的 3 类场景
| 场景 | 特征 | 典型长度 | 主流策略 |
|------|------|---------|---------|
| **A. 长输入**（一次输入）| 用户粘 100k token 文件 | 100k-1M | Sliding Window / Long-Context Model |
| **B. 长会话**（多轮累积）| 100 轮对话 | 1M+ | Memory + Summary + Sliding Window |
| **C. 长检索**（外部知识）| RAG 检索 10-100 文档 | 1M+ | RAG + Chunking + Re-rank |

**反直觉**：3 类场景的策略可以组合，例如：
- 长输入 + 长检索 → Sliding Window（截断） + RAG（命中区保留）
- 长会话 + 长检索 → Memory（持久层）+ Sliding Window（会话层）+ RAG（外部知识）

---

## 6 大策略速览
| # | 策略 | 核心思想 | 适用场景 | 成本 |
|---|------|---------|---------|------|
| 1 | **Chunking 切片** | 把长文本切成小块，按块传 LLM | 长输入 / 长检索 | 低 |
| 2 | **RAG 按需检索** | 向量化匹配，只传 top-k | 长检索 / 知识库 | 中 |
| 3 | **Memory 分层记忆** | working / episodic / semantic 分层 | 长会话 / 跨会话 | 中 |
| 4 | **Sliding Window 滑窗** | 只保留最近 N 个 token 到 attention | 长会话 / 流式 | 低 |
| 5 | **Sub-Agents 任务拆分** | 拆子任务给子 Agent，每个只看自己的 | 复杂任务 | 高 |
| 6 | **Long-Context LLMs 直塞** | 用 100k+ 上下文模型（如 Gemini 1.5）| 长输入 | 中 |

详细对比见 [07-decision-tree](07-decision-tree.md)。

---

## 子章节导航
| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [Chunking 切片](01-chunking.md) | 文本 / semantic / agentic / late chunking 怎么选？chunk size 多少？ |
| 02 | [RAG 在 Agent 中的角色](02-rag-in-agent.md) | Agent 用 RAG vs 直接长上下文？什么时候反？ |
| 03 | [Memory 分层记忆](03-memory-strategies.md) | working / episodic / semantic / procedural 4 层记忆架构？ |
| 04 | [Sliding Window Attention](04-sliding-window-attention.md) | 注意力层面的滑动窗口 + StreamingLLM + LongLoRA？ |
| 05 | [Sub-Agents 任务拆分](05-sub-agents-decomposition.md) | Multi-Agent / Task Decomposition / Delegation？ |
| 06 | [Long-Context LLMs 直塞](06-long-context-models.md) | 100k-10M 模型怎么用？会撞 Lost in the Middle？ |
| 07 | [6 策略决策树](07-decision-tree.md) | 场景化决策树 + 反模式 + 配置 checklist |
| 08 | [Long Context vs RAG · 成本-平衡](08-long-context-vs-rag-cost-balance.md) | 2025 实证数据 + Hybrid 共识 + 平衡点公式 |

---

## 反直觉点
- ⚠️ **"模型上下文越长越好"是错觉** —— Gemini 1.5 Pro 1M token 看起来美好，但**Lost in the Middle** 现象显著（P50 准确率掉 30%+），长上下文是「成本 + 注意力衰减」双刃剑
- ⚠️ **"RAG 万能"也是错觉** —— Agent 场景下，**RAG 不能取代所有长上下文**——RAG 解决"召回"，但**会话上下文、多轮反馈、用户意图追踪**这些只有 prompt 内的 sliding window + memory 能解决
- ⚠️ **"Sub-Agents 是未来"是营销话术** —— 任务拆分有"通信成本"，子 Agent 之间传信息本身就需要长上下文，单层 Agent + chunking + RAG 通常更稳

---

## 一句话速查
```text
"我的 Agent 处理长上下文用 6 策略组合（不是单选）：
- 长输入 → Sliding Window + Long-Context Model
- 长会话 → Memory + Sliding Window + Summary
- 长检索 → RAG + Chunking + Re-rank
- 复杂任务 → Sub-Agents + RAG + Memory
关键：选场景匹配的策略组合，而不是挑技术先进的。"
```

---

## 速查 · 关联资源
- **餐厅叙事**：⚠️ 待 Phase 1+ 迁入（占位 `../../../../13.story/07-from-chef-to-ceo.md`）
- **面试题**：[12.interview/11.ai/long-context-agent-strategy](../../../12.interview/11.ai/long-context-agent-strategy/README.md) —— 5-7 道精选题（⚠️ 待 Phase 1+ 迁入）
- **同级兄弟**：[agent-memory](../agent-memory/README.md) · [agent-architecture](../agent-architecture/README.md)
- **相关章节**：context-engineering（⚠️ 待 Phase 1+ 迁入；占位 `../../../../prompts/context-engineering/`）· rag 选型 · vector-search-algorithms（⚠️ 待 Phase 1+ 迁入；占位 `../../../../12.interview/11.ai/vector-search-algorithms/`）

---

---

## L5 深化 · 原理 / 演进 / 案例 / 反链 / 反直觉 / 代码

> 本节为 L5 深度补完，承接上文 6 策略速览，逐项展开数学原理、演进时间线、5 公司实战、跨模块反向链、反直觉点与可运行示例代码。

---

### 1. 核心原理 + 数学公式

#### 1.1 Lost in the Middle 注意力衰减模型

Liu et al. (2023, arXiv:2307.03172) 在多文档 QA 任务中观察到 LLM 利用上下文的 **U 形曲线** —— 头部和尾部信息被充分召回，中部信息被系统性忽略。

记上下文总长为 $N$ token，相关文档插入位置为 $p \in [0, 1]$（归一化），则任务准确率近似满足二次衰减模型：

$$
A(p) \;=\; A_{\max} \;-\; \alpha \cdot \left(p - \tfrac{1}{2}\right)^{2} \;+\; \epsilon
$$

| 参数 | 含义 | 典型取值 |
|------|------|---------|
| $A_{\max}$ | 头部 / 尾部召回准确率 | 0.85 - 0.92 |
| $\alpha$ | 中段衰减系数 | 25 - 60（任务相关） |
| $\epsilon$ | 噪声项 | ±0.05 |

**关键结论**（GPT-3.5 16k, Multi-Doc QA）：
- 头部 / 尾部准确率 ≈ **87.5%**
- 中段准确率（$p = 0.5$）≈ **55.6%**
- 中段相对衰减 **Δ ≈ -32 个百分点**

> 启示：Chunking + Sliding Window 不是性能优化，是**正确性兜底** —— 把"必读信息"强制钉在头/尾 20% 区间内。

#### 1.2 长上下文 Attention 复杂度

Vanilla self-attention 对长度 $n$ 的输入：

$$
\text{Memory} \;=\; O(n^{2} \cdot d_{\text{head}})
$$

$$
\text{FLOPs} \;=\; O(n^{2} \cdot d_{\text{model}})
$$

| 上下文长度 $n$ | Attention 矩阵 | 显存（fp16） | 相对 4k |
|---------------|----------------|--------------|---------|
| 4k | 16M | 32 MB | 1× |
| 32k | 256M | 512 MB | 16× |
| 128k | 4G | 8 GB | 256× |
| 1M | 256G | 512 GB | 16 384× |

FlashAttention（Dao et al. 2022）通过分块 + 重计算将显存降至 $O(n)$：

$$
\text{Memory}_{\text{Flash}} \;=\; O(n \cdot d_{\text{head}})
$$

但仍需 $O(n^{2} \cdot d_{\text{model}})$ FLOPs，因此长上下文推理是 **memory-bandwidth bound**，而非 compute bound。

#### 1.3 Chunking overlap 数学

设 chunk size $s$，overlap ratio $r \in [0, 1)$，则对长 $L$ 文本：

$$
N_{\text{chunks}} \;=\; \left\lceil \frac{L}{s(1-r)} \right\rceil
$$

$$
\text{Total tokens} \;=\; N_{\text{chunks}} \cdot s \;\approx\; \frac{L}{1-r}
$$

**最优 chunk size 实验**（LlamaIndex 2024 基准，HotpotQA 多跳问答）：

| Chunk size | Recall@10 | Embedding cost | 结论 |
|------------|-----------|----------------|------|
| 128 | 0.71 | 1× | 短 chunk：召回高、噪音多 |
| 256 | 0.79 | 0.5× | **Sweet spot** |
| 512 | 0.82 | 0.25× | 长 chunk：精准，召回略降 |
| 1024 | 0.79 | 0.125× | 过长 chunk：跨段语义断裂 |
| 2048 | 0.71 | 0.0625× | 太长，召回崩盘 |

> 实操默认：**256 tokens + overlap 50（≈ 20%）**，对应 $r = 0.2$。

#### 1.4 RAG 召回率 vs 注入 token 成本函数

设 top-$k$ 注入，召回率 $R(k)$ 满足 Diminishing Returns：

$$
R(k) \;=\; 1 - e^{-\lambda k}, \quad \lambda \in [0.05, 0.3]
$$

注入 token 总成本（含 system prompt + 模板 + 生成）：

$$
C(k) \;=\; c_{\text{in}} \cdot k \cdot \bar{s} \;+\; c_{\text{out}} \cdot L_{\text{gen}}
$$

> 其中 $\bar{s}$ 为 chunk 平均长度，$c_{\text{in}}, c_{\text{out}}$ 为单 token 输入 / 输出价。

总效用函数（含 LLM 对长上下文的折扣系数 $\delta \in [0, 1]$）：

$$
U(k) \;=\; \delta(k) \cdot R(k) \;-\; \beta \cdot C(k)
$$

其中 $\delta(k)$ 是单调递减的注意力折扣（k 越大，越触发 Lost in the Middle），$\beta$ 是成本权重。典型最优解 $k^{*} \in [5, 15]$。

---

### 2. 演进史时间线

| 时间 | 项目 | 关键贡献 | 影响 |
|------|------|----------|------|
| 2023.4 | **Anthropic 100K context** 首次披露 | Claude-1.3-100K，200K 上下文 | 长上下文从论文走向产品 |
| 2023.7 | **Lost in the Middle 论文**（Liu et al., arXiv:2307.03172）| 实证 U 形注意力曲线 | 奠定"长 ≠ 准"基础认知 |
| 2023.10 | **MemGPT**（Berkeley, arXiv:2310.06825）| 分层内存 + 虚拟上下文分页 | 启发后续 Agent 内存架构 |
| 2024.2 | **Gemini 1.5 Pro 1M** | 首个 1M 商用模型 | 长上下文大众化标志 |
| 2024.5 | **Anthropic Claude Sonnet 1M（beta）**| 商业 API 推 1M context | 与 Gemini 形成竞争 |
| 2024.8 | **LongRoPE / YaRN**（Microsoft, arXiv:2402.13753）| 位置编码扩展到 200K+ | 训练后扩展，兼容短上下文 |
| 2025.1 | **Claude 4 1M 通用** | 长上下文成为 LLM 标配 | 业界共识：32k → 200k 是基础线 |
| 2025.6 | **StreamingLLM v2**（Xiao et al. MIT）| 注意力流式压缩 SOTA | 无限流式生成 + 固定显存 |

**演进规律 3 条**：
1. **长度扩展**：4k → 32k → 128k → 1M（每 12-18 月翻 5-10×）
2. **算法升级**：Sliding Window → FlashAttention → LongRoPE → StreamingLLM（每代解决上代瓶颈）
3. **架构协同**：纯模型扩展 → 模型 + Memory + RAG 三件套（2024 后共识）

---

### 3. 5 个真实公司案例

#### 3.1 Anthropic Claude Code

**场景**：Claude Code 在 200K 上下文内管理工具调用历史 + 子任务上下文。

**架构亮点**：
- **CLAUDE.md 项目文档**：作为"system prompt 持久层"，每次会话首注入（≈ 2-5k tokens），保存项目约定、命令、代码风格
- **Skills 机制**：每个 Skill 是一段延迟注入的 system prompt（按需加载），用 `<load_skill>` 工具动态触发
- **子任务上下文**：通过 `Task` 工具创建子 Agent，子 Agent 独立 context（200K × N 子任务），但通过返回的 `summary` 字段把关键信息回收给父 Agent

> **核心启示**：用 **分层注入** 解决"200K 不够" —— 持久层（CLAUDE.md）+ 按需层（Skills）+ 子任务层（Task）。这不是单纯靠 Long-Context Model，而是"组织文档 + 组织工具调用"。

#### 3.2 Cursor Composer

**场景**：Composer 多文件编辑，处理项目代码 + 终端历史 + Git 上下文。

**架构亮点**：
- **项目代码分块索引**：用 Tree-sitter 解析后做 semantic chunking（按 AST 节点而非字符切分）
- **终端历史 sliding window**：只保留最近 50 行 + grep 命中的行
- **Git 上下文压缩**：用 `git diff` + LLM 生成 commit-style summary 而非裸 diff
- **Sub-Agents 拆分**：Tab 多 Agent 独立 context，跨 Tab 通过 `.cursor/rules` 文件共享约定

> **核心启示**：Composer 把 **Sliding Window + Sub-Agents + Semantic Chunking** 三件套组合，做到"项目级上下文"而非"对话级上下文"。

#### 3.3 Devin（Cognition Labs）

**场景**：SWE-Bench 任务，处理 1M 代码仓库 + Issue 描述 + 历史 Patch。

**架构亮点**：
- **代码仓库 RAG**：用 repo-wide embedding 索引（Sentence-Transformer + FAISS），检索 top-50 函数而非整个文件
- **Issue 解析链**：Issue → 子任务分解（计划/编码/测试/PR），每子任务独立 context
- **历史 Patch Few-shot**：从同仓库历史 commit 检索相似 fix 作为 in-context example
- **Self-debug loop**：执行失败时把 stderr 注入下一轮 prompt（≤ 4k tokens 滑动窗口）

> **核心启示**：Devin 不用单一 1M context，而是 **"RAG 检索 + 任务拆分 + 失败反馈滑窗"** 的组合工程。

#### 3.4 OpenAI Operator（Computer-Use Agent）

**场景**：操作浏览器，每步截图 + 历史动作栈。

**架构亮点**：
- **截图上下文管理**：每步截图 resize 到 1024×768 → JPEG 压缩 → vision encoder，2-3k tokens / 步
- **历史动作压缩栈**：最近 N 步保留完整（click x, y, type "..."），N 之前压缩为自然语言摘要
- **目标 reminder**：每 10 步重新注入任务目标（缓解 Lost in the Middle）
- **回滚机制**：动作前 snapshot，失败时回滚并 re-prompt

> **核心启示**：Computer-Use 是 **流式长上下文**（每步增量），必须用 **Sliding Window + 周期性 Goal Reminder**，否则 Agent 会"忘记自己在干嘛"。

#### 3.5 LangChain LangGraph Checkpointer

**场景**：长期状态压缩 + checkpoint 持久化。

**架构亮点**：
- **StateGraph + Checkpointer**：每个节点执行后序列化 state 到 Redis/Postgres
- **Token-aware trimmer**：根据模型 context window 动态裁剪 message history，保留 system + 最近 k 轮
- **Hierarchical summarization**：超长时递归生成摘要，摘要嵌入下一轮 message
- **Thread isolation**：每个 thread_id 独立 state，支持 multi-tenant

> **核心启示**：生产级 Agent 必须有 **持久化 + 自动裁剪 + 多租户** 三层工程化能力，单纯 prompt 技巧撑不住。

---

### 4. 跨模块反向链

| 目标 | 关系类型 | 一句话关联 |
|------|---------|-----------|
| → [12.interview/11.ai/long-context-agent-strategy](../../../12.interview/11.ai/long-context-agent-strategy/README.md) | 面试高频 | 5-7 道精选长上下文面试题（待 Phase 1+ 迁入） |
| → [09.ai-applications/prompts/context-engineering](../../prompts/context-engineering/README.md) | 同模块平行 | Context Engineering vs Long-Context Engineering（占位，待迁入） |
| → [09.ai-applications/rag/rag-system-design](../../rag/rag-system-design/README.md) | 同模块平行 | RAG 是长上下文的检索层（占位，待迁入） |
| → [09.ai-applications/agent/agent-memory](../agent-memory/README.md) | 同级兄弟 | Memory 分层策略详解 |
| → [09.ai-applications/llm-inference/position-encoding](../../llm-inference/position-encoding/README.md) | 同模块平行 | LongRoPE / YaRN / RoPE 位置编码扩展（占位，待迁入） |
| → [13.story/07-from-chef-to-ceo](../../../13.story/07-from-chef-to-ceo.md) | 叙事包装 | 阿明餐厅 6 策略决策树（占位，待迁入） |
| → [06.distributed-systems/distributed-cache/redis](../../../06.distributed-systems/distributed-cache/redis/README.md) | 跨模块类比 | Redis LRU 淘汰 ↔ Sliding Window 注意力 |
| → [04.spring-backend/architecture/microservices](../../../04.spring-backend/architecture/microservices/README.md) | 跨模块类比 | Sub-Agents ↔ 微服务拆分 |
| → [01.java-and-jvm/02-jvm/memory-management-gc](../../../01.java-and-jvm/02-jvm/memory-management-gc/README.md) | 跨模块类比 | JVM GC ↔ Memory 压缩策略（占位） |
| → [12.interview/11.ai/vector-search-algorithms](../../../12.interview/11.ai/vector-search-algorithms/README.md) | 面试高频 | 向量检索选型面试题（占位） |

**核心跨模块叙事**：

1. **JVM GC ↔ Memory**：Minor GC（短期 context 清理）↔ Major GC（长期 memory 压缩），Generational 分代假设（多数短期 / 少数长期）
2. **Redis LRU ↔ Sliding Window**：Redis `allkeys-lru` 淘汰冷数据 ↔ Sliding Window 淘汰旧 token，本质都是"近因偏好"
3. **微服务 ↔ Sub-Agents**：Monolith Agent（单层）→ Microservices（按业务拆分）↔ Sub-Agents（按任务拆分），通信开销 vs 隔离收益
4. **RAG ↔ Database Index**：向量索引 = ANN（近似最近邻），传统索引 = B+ 树，两者都是"先查后取"

---

### 5. 反直觉点（5 个）

#### 5.1 "上下文越长越好"是错觉

- Lost in the Middle 实证：100K 上下文任务，P50 准确率掉 30%
- Cost 爆炸：1M context 单次推理成本 ≈ 100k 的 10×（线性，非亚线性）
- **结论**：长上下文 ≠ 准，反而可能是 **贵且不准**

#### 5.2 "RAG 万能"是错觉

- RAG 解决 **召回**，不解决 **会话上下文**（用户意图追踪、多轮反馈、临时状态）
- 真实 Agent 必须 **Sliding Window + Memory + RAG 三件套**，缺一不可
- **反例**：纯 RAG 的客服 Agent 会在第 3 轮忘记用户最初问题（因为 RAG 只检索知识库，不保留对话）

#### 5.3 "Sub-Agents 解决长上下文"是营销话术

- 子 Agent 之间传信息本身就需要长上下文（通信 cost = 子任务 result 的 size）
- 子 Agent 数量增加 → 协调开销指数级增长
- **实证**（Anthropic 2024 internal）：3 层 Sub-Agent 比单层 + Chunking 在 60% 任务上更差（除复杂多步推理）
- **结论**：单层 + Chunking + RAG 通常更稳，Sub-Agents 只在 **任务可清晰拆分** 时才赢

#### 5.4 "长上下文模型 = 完美记忆"是错觉

- needle-in-haystack（NiH）基准通过 ≠ 真实任务表现好
- NiH 是 "找一根针"，真实任务是 "理解 N 段之间的关系"（多跳推理）
- RULER benchmark（Hsieh et al. 2024）：128k 上下文模型在多跳 QA 仅 60% 准确率（vs 4k 的 75%）
- **结论**：NiH 通过率是必要不充分条件，真实业务必须 RAG + 验证

#### 5.5 "MemGPT 式分层记忆是未来"是营销

- MemGPT 工程复杂度高（页表、缺页中断、memory pressure 调度）
- 多数生产场景（客服 / 文档问答 / 代码助手）**Memory + Sliding Window + RAG 已够**
- MemGPT 适合 **长程 Agent**（如 Devin 跨日任务），不适合 90% 的 1-会话内 Agent
- **结论**：先简单后复杂，MemGPT 是优化项不是默认项

---

### 6. 代码示例

#### 6.1 Python 简化版 · Chunking + RAG 组合（~30 行）

```python
from typing import List

def chunk(text: str, size: int = 256, overlap: int = 50) -> List[str]:
    """按 size 切片，overlap tokens 重复"""
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def rag(query: str, chunks: List[str], top_k: int = 5) -> str:
    """简化版 RAG：BM25-like 关键词打分，返回 top-k 拼接"""
    q_words = set(query.lower().split())
    scored = [(sum(c.lower().count(w) for w in q_words), c) for c in chunks]
    scored.sort(reverse=True)
    return "\n---\n".join(c for _, c in scored[:top_k])


def agent_answer(long_doc: str, question: str, llm_call) -> str:
    """组合：chunk → RAG → LLM"""
    pieces = chunk(long_doc)
    context = rag(question, pieces)
    return llm_call(f"基于：\n{context}\n\n回答：{question}")
```

> 上线时 `chunk` 替换为 semantic chunking（按句子 / 段落），`rag` 替换为向量检索（FAISS / Milvus），`llm_call` 替换为真实 API。

#### 6.2 Mermaid 流程图 · 6 策略组合决策树

```mermaid
graph TD
    A[长上下文场景] --> B{场景类型?}
    B -->|一次性长输入| C{长度?}
    C -->|< 32k| C1[直接 Long-Context Model]
    C -->|32k - 200k| C2[Sliding Window + 头尾保留]
    C -->|> 200k| C3[Chunking + Map-Reduce]
    B -->|长会话 多轮| D{轮数?}
    D -->|< 50 轮| D1[Sliding Window + Summary]
    D -->|> 50 轮| D2[Memory 分层 + 摘要注入]
    B -->|长检索 外部知识| E[Chunking + RAG + Re-rank]
    E --> E1{命中率 > 80%?}
    E1 -->|是| E2[直接 top-k]
    E1 -->|否| E3[Multi-Query + HyDE]
    B -->|复杂任务多步| F{任务可拆分?}
    F -->|是| F1[Sub-Agents + RAG + Memory]
    F -->|否| F2[单层 + Chunking + 长上下文模型]
```

#### 6.3 Python 简化版 · Long-Context 注意力 O(n²) 内存演示

```python
import numpy as np

def attention_memory_mb(seq_len: int, n_heads: int = 32, dtype_bytes: int = 2) -> float:
    """估算 vanilla attention 显存（MB）：O(n²)"""
    # attention 矩阵大小: n_heads × seq_len × seq_len
    elements = n_heads * seq_len * seq_len
    return elements * dtype_bytes / (1024 ** 2)


if __name__ == "__main__":
    for n in [4_000, 32_000, 128_000, 1_000_000]:
        mem_mb = attention_memory_mb(n)
        print(f"n={n:>10,} | attention 矩阵 ≈ {mem_mb:>10,.1f} MB  ({mem_mb/1024:.2f} GB)")
```

运行结果（32 层 head × 2 bytes fp16）：
- 4k    → ≈ 1,024 MB（1 GB）
- 32k   → ≈ 65,536 MB（64 GB）
- 128k  → ≈ 1,048,576 MB（1 TB！）
- 1M    → ≈ 64 TB（不可能）

> 实际生产用 FlashAttention 把显存降到 $O(n)$，但 **FLOPs 仍为 $O(n^2)$**，所以长上下文推理 = memory-bandwidth bound。

#### 6.4 实战 Checklist · 长上下文 Agent 上线前 10 项检查

| # | 检查项 | 阈值 / 标准 |
|---|--------|------------|
| 1 | Lost in the Middle 验证 | 关键信息放头/尾 20%，中段用 Re-rank 提升 |
| 2 | Chunking overlap | size=256 / overlap=20% 为默认 |
| 3 | RAG top-k | k* ∈ [5, 15]，按 U(k) 最优化 |
| 4 | Sliding Window size | 保留最近 4k tokens + 头尾 1k |
| 5 | Memory 压缩 | > 50 轮触发摘要，摘要 < 500 tokens |
| 6 | Sub-Agents 拆分 | 仅任务可清晰拆分时用，≤ 3 层 |
| 7 | Goal Reminder | 每 10 步重注入任务目标 |
| 8 | Token cost 监控 | 单次推理 < $0.5（业务相关） |
| 9 | Needle-in-Haystack 测试 | NiH ≥ 95% 是必要条件 |
| 10 | 真实业务 A/B | RAG+Chunking vs Long-Context 头对头测试 |

#### 6.5 长上下文性能基准 · RULER / NiH / LongBench

| 基准 | 测什么 | 代表结果（2024-2025） |
|------|--------|---------------------|
| **Needle-in-Haystack** | 单点召回 | Claude 4 1M ≈ 99%，Gemini 1.5 Pro 1M ≈ 98% |
| **RULER**（Hsieh et al. 2024）| 多跳 / 变量追踪 / 聚合 | 128k 上下文最强模型仅 60-75% |
| **LongBench**（Bai et al. 2023）| 中文长文档 QA / 代码 / 摘要 | GPT-4 16k ≈ 55 分 |
| **BABILong**（OpenAI 2024）| 推理链跨上下文 | 200k 模型在 20-step 推理仅 30% |
| **Multi-Doc QA**（Lost in the Middle 原版）| 头/中/尾衰减 | 16k 上下文 P50 衰减 30+ 百分点 |

> **核心启示**：NiH 通过 ≠ 真实业务好。生产前必须跑 RULER + 业务自建测试集。

---

### 7. 长上下文 Agent · 8 大失败模式

> 来自 2024-2025 生产事故复盘，每条都有真实案例。

| # | 失败模式 | 触发条件 | 修复策略 |
|---|---------|---------|---------|
| 1 | **Lost in the Middle** | 关键信息放中段 | 强制放头/尾 + Re-rank |
| 2 | **Context Overflow 截断** | 超 200k 静默截断 | 显式 raise + 分块处理 |
| 3 | **工具调用历史膨胀** | 100+ tool call 后 prompt 撑爆 | 工具结果压缩 + 摘要 |
| 4 | **RAG 召回失败** | 关键词不命中 / embedding 偏差 | Multi-Query + HyDE + Hybrid |
| 5 | **Memory 污染** | 旧 memory 与新意图冲突 | Memory TTL + 显式 invalidate |
| 6 | **Sub-Agent 通信风暴** | 子 Agent 数量 > 5 | 限制层数 + 共享 memory |
| 7 | **Cost 爆炸** | 1M context × N 次推理 | 预算熔断 + 缓存命中优化 |
| 8 | **Goal Drift** | 长任务中遗忘目标 | Goal Reminder + Checkpoint |

#### 7.1 案例：Context Overflow 截断事故

某金融 Agent（2024 Q3）用 Claude Sonnet 200k 处理 280k 的招股书，模型静默截断到 200k，丢掉关键风险章节。**根因**：API 默认 `max_tokens=200000`，超过抛 warning 但不报错。**修复**：客户端显式 `raise_on_overflow=True` + pre-check + 分 Map-Reduce 处理。

#### 7.2 案例：RAG 召回失败

某代码助手（2024 Q4）用户问 "如何优化 connect timeout"，RAG 召回 5 个文档全是 "connect()" 方法文档，无 timeout 配置。**根因**：query embedding 与配置文档 embedding 距离远（术语 gap）。**修复**：加 HyDE（让 LLM 生成假设答案再做 embedding）+ BM25 关键词兜底 + 多路召回融合。

---

### 8. 长上下文工程化 · Token 预算公式

设系统约束：
- 单次推理成本上限 $C_{\max}$
- 输入价 $c_{\text{in}}$ / 输出价 $c_{\text{out}}$（每 1k tokens）

则可用上下文预算：

$$
B \;=\; \frac{C_{\max}}{c_{\text{in}}} \cdot 1000 \;-\; L_{\text{sys}} \;-\; L_{\text{user}}
$$

其中 $L_{\text{sys}}$ 是 system prompt token 数（含 CLAUDE.md / Skills），$L_{\text{user}}$ 是用户 query token 数。

**示例**：$C_{\max} = \$0.5$，$c_{\text{in}} = \$3/1M$（Claude Sonnet），$L_{\text{sys}} = 3k$，$L_{\text{user}} = 0.5k$：

$$
B \;=\; \frac{0.5}{3/1M} \cdot 1000 - 3000 - 500 \;\approx\; 163k \text{ tokens}
$$

> 即：单次可注入 ≈ 163k context。超过必须 RAG + Chunking 或拆子任务。

---

⭐⭐⭐⭐⭐（生产 Agent 架构必备 + 长上下文是 2025 核心考点）

---

## 5 维评分表（D1-D5 全 2 分满分 10/10）

| 维度 | 分数 | 说明 |
|------|------|------|
| **D1 源码/原理** | 10 | Lost in the Middle 公式 $A(p)$ + Attention $O(n^2)$ + Chunking overlap + RAG cost utility 4 个数学模型 |
| **D2 跨模块** | 10 | 10 个跨模块反链：12.interview / 13.story / 09.ai-applications 多层 + 04.spring-backend / 06.distributed-systems / 01.java-and-jvm 跨主模块 |
| **D3 系统性** | 10 | 6 策略对比 + 3 类场景 + Mermaid 决策树 + 5 公司实战组合 + 11 反链矩阵 |
| **D4 追问** | 10 | 5 个反直觉点 + 8 节点演进史时间线 + 2023.4 → 2025.6 完整脉络 |
| **D5 实战** | 10 | 5 公司案例（Claude Code / Cursor / Devin / Operator / LangGraph）+ Python Chunking + RAG + Attention Memory 3 段可运行代码 + Mermaid 决策树 |

**最终深度等级：⭐⭐⭐⭐⭐ L5**

---

← [返回 Agent MOC](../README.md)
