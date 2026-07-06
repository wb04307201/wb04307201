<!--
module:
  parent: agent-architecture
  slug: ai/agent-architecture/agent-context
  type: deep-dive
  category: Agent 长上下文架构
  summary: Agent 如何处理长上下文 —— 6 大策略（Chunking / RAG / Memory / Sliding Window / Sub-Agents / Long-Context LLMs）+ 选型决策树 + 面试题
-->

# Agent 长上下文架构 · 6 大策略全景

> **一句话答案**：长上下文不是"塞进 prompt 就完事"——Agent 在 100k+ 上下文场景下，**没有银弹**，必须**组合 6 大策略**（Chunking 按需切片 + RAG 按需检索 + Memory 持久记忆 + Sliding Window 滑动窗口 + Sub-Agents 任务拆分 + Long-Context LLMs 直塞）才能稳跑。

← [返回: Agent 架构](../README.md) · 同级：[agent-memory](../agent-memory/README.md) · [ontology-driven-agent](../ontology-driven-agent/README.md)

---

## 0. 面试高频拷问

```
Q：你的 Agent 如何处理长上下文？1M token 的文档怎么让 LLM 准确回答？
```

**回答框架（4 层递进）**：

1. **场景区分**："长上下文"在 Agent 场景下分 3 类——长输入（一次性灌入）/ 长会话（多轮累积）/ 长检索（外部文档库）
2. **6 策略对比**：每种场景下用哪些策略组合（不是单选，是组合）
3. **反模式**：列举 Agent 长上下文 5 大失效点
4. **何时反选**：盲目灌长上下文 vs 总是用 RAG 的两个极端都错

完整 5-7 道精选面试题见 [13.split-hairs/11.ai/long-context-agent-strategy](../../../13.split-hairs/11.ai/long-context-agent-strategy/README.md)。

---

## 1. 长上下文的 3 类场景

| 场景 | 特征 | 典型长度 | 主流策略 |
|------|------|---------|---------|
| **A. 长输入**（一次输入）| 用户粘 100k token 文件 | 100k-1M | Sliding Window / Long-Context Model |
| **B. 长会话**（多轮累积）| 100 轮对话 | 1M+ | Memory + Summary + Sliding Window |
| **C. 长检索**（外部知识）| RAG 检索 10-100 文档 | 1M+ | RAG + Chunking + Re-rank |

**反直觉**：3 类场景的策略可以组合，例如：
- 长输入 + 长检索 → Sliding Window（截断） + RAG（命中区保留）
- 长会话 + 长检索 → Memory（持久层）+ Sliding Window（会话层）+ RAG（外部知识）

---

## 2. 6 大策略速览

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

## 3. 子章节导航

| # | 章节 | 核心问题 |
|---|------|---------|
| 01 | [Chunking 切片](01-chunking.md) | 文本 / semantic / agentic / late chunking 怎么选？chunk size 多少？ |
| 02 | [RAG 在 Agent 中的角色](02-rag-in-agent.md) | Agent 用 RAG vs 直接长上下文？什么时候反？ |
| 03 | [Memory 分层记忆](03-memory-strategies.md) | working / episodic / semantic / procedural 4 层记忆架构？ |
| 04 | [Sliding Window Attention](04-sliding-window-attention.md) | 注意力层面的滑动窗口 + StreamingLLM + LongLoRA？ |
| 05 | [Sub-Agents 任务拆分](05-sub-agents-decomposition.md) | Multi-Agent / Task Decomposition / Delegation？ |
| 06 | [Long-Context LLMs 直塞](06-long-context-models.md) | 100k-10M 模型怎么用？会撞 Lost in the Middle？ |
| 07 | [6 策略决策树](07-decision-tree.md) | 场景化决策树 + 反模式 + 配置 checklist |

---

## 4. 反直觉点

- ⚠️ **"模型上下文越长越好"是错觉** —— Gemini 1.5 Pro 1M token 看起来美好，但**Lost in the Middle** 现象显著（P50 准确率掉 30%+），长上下文是「成本 + 注意力衰减」双刃剑
- ⚠️ **"RAG 万能"也是错觉** —— Agent 场景下，**RAG 不能取代所有长上下文**——RAG 解决"召回"，但**会话上下文、多轮反馈、用户意图追踪**这些只有 prompt 内的 sliding window + memory 能解决
- ⚠️ **"Sub-Agents 是未来"是营销话术** —— 任务拆分有"通信成本"，子 Agent 之间传信息本身就需要长上下文，单层 Agent + chunking + RAG 通常更稳

---

## 5. 一句话速查

```
"我的 Agent 处理长上下文用 6 策略组合（不是单选）：
- 长输入 → Sliding Window + Long-Context Model
- 长会话 → Memory + Sliding Window + Summary
- 长检索 → RAG + Chunking + Re-rank
- 复杂任务 → Sub-Agents + RAG + Memory
关键：选场景匹配的策略组合，而不是挑技术先进的。"
```

---

## 6. 速查 · 关联资源

- **餐厅叙事**：[12.story/07-from-chef-to-ceo.md](../../../12.story/07-from-chef-to-ceo.md) —— 阿明餐厅 80 家连锁的"长菜单与多订单管理"实战
- **面试题**：[13.split-hairs/11.ai/long-context-agent-strategy](../../../13.split-hairs/11.ai/long-context-agent-strategy/README.md) —— 5-7 道精选题
- **同级兄弟**：[agent-memory](../agent-memory/README.md) · [agent-architecture](../agent-architecture/README.md)
- **相关章节**：[context-engineering](../../02-technology-stack/context-engineering/README.md) · [rag](../../01-rag-vs-finetuning/) · [vector-search-algorithms](../../../13.split-hairs/11.ai/vector-search-algorithms/README.md)

---

← [返回: Agent 架构](../README.md)
