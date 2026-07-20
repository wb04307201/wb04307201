<!--
question:
  id: 11.ai-long-context-agent-strategy
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: Agent 架构选型
  tags: [11.ai, Agent, 长上下文, Context Engineering, RAG, Memory, Sub-Agents]
-->

# Agent 长上下文处理：6 大策略选型深挖

> 一句话定位：Agent 长上下文不是单一策略能解决——必须 Chunking / RAG / Memory / Sliding Window / Sub-Agents / Long-Context Models 6 大策略组合。完整深度见 [主模块 agent-context 深度专题](../../../11.ai/04-architecture/agent-context/README.md)。

> **系列定位**：经典 AI Agent 架构面试题（字节 / 阿里 / 美团 / Anthropic 高频）。考察的不是「哪个策略最好」，而是 **6 策略场景化组合能力** + **Lost in Middle 等 5 大反模式** + **何时反选 RAG / Long-Context**。

---

## 引子：1M 文档塞进 LLM 的 3 个崩溃现场

```text
场景：2024 Q3 某 AI 公司要做"全文档问答"——
- 上下文：用户上传 1M token 的代码库 / 法律文档 / 学术论文
- 问题：如何让 LLM 准确回答？
- 候选：①RAG  ②Long-Context  ③Multi-Agent  ④Fine-tuning
```

**决策现场**：
1. **初创会问**：「Gemini 1.5 不是 1M 上下文吗？直接塞不就行了？」
2. **资深会问**：「Lost in the Middle 怎么破？4-7k 的位置准确率掉 30%，怎么处理？」
3. **架构师会问**：「RAG 和 Long-Context 怎么组合？什么时候用 Sub-Agents？Memory 模块怎么设计？」

普通候选人会答："用 RAG"——踩中"**理由模糊、缺反模式、缺策略组合**" 3 大雷区。
高分候选人会答：**场景区分（先分类：长输入 / 长会话 / 长检索）→ 6 大策略对比 → 5 个反模式 → 何时反选 + 实施 checklist**。

---

## 一、核心原理（必选）

### 1.1 长上下文的 3 类场景

| 场景 | 特征 | 典型长度 | 主流策略 |
|------|------|---------|---------|
| **A. 长输入** | 用户一次性粘 100k token | 100k-1M | Sliding Window / Long-Context |
| **B. 长会话** | 多轮对话累积 | 1M+ | Memory + Summary + Sliding Window |
| **C. 长检索** | 外部知识库 | 1M+ | RAG + Chunking + Re-rank |

**反直觉**：3 类可以组合，不是单选。

### 1.2 6 大策略全景

| # | 策略 | 核心思想 | 成本 |
|---|------|---------|------|
| 1 | **Chunking 切片** | 按语义切短块，按块传 LLM | 低 |
| 2 | **RAG 按需检索** | 向量化匹配，只传 top-k | 中 |
| 3 | **Memory 分层记忆** | working/episodic/semantic/procedural 分层 | 中 |
| 4 | **Sliding Window 滑窗** | 只保留最近 N token 到 attention | 低 |
| 5 | **Sub-Agents 任务拆分** | 拆子任务给子 Agent | 高 |
| 6 | **Long-Context LLMs 直塞** | 用 100k+ 上下文模型 | 中 |

完整对比见 [07-decision-tree](../../../11.ai/04-architecture/agent-context/07-decision-tree.md)。

### 1.3 Lost in the Middle 现象

| 位置 | 准确率 |
|------|--------|
| Prompt 开头 | 85% |
| Prompt 中间 | **58%** |
| Prompt 结尾 | 80% |

> 不是"上下文越长越准"——是"重要信息放两端最准"。

### 1.4 6 策略的边界

| 策略 | 解决 | 不能解决 |
|------|------|---------|
| Chunking | 长输入切分 | 跨块语义关联 |
| RAG | 外部知识检索 | 会话上下文 / 推理状态 |
| Memory | 跨会话/跨任务持久 | 全局检索 |
| Sliding Window | KV cache 显存 | 早期信息回忆 |
| Sub-Agents | 单 Agent 上下文压力 | 子 Agent 间通信 |
| Long-Context | 直接喂长输入 | Lost in Middle + 成本 |

---

## 二、面试话术（90 秒版本 / 高分答案模板）

> ⚠️ **模板不是背答案**，而是当大脑空白时的"骨架"——面试现场结合题目微调。

### 题目 A：1M token 文档如何让 LLM 准确回答？

**高分答案**（4 层递进，60-90 秒）：

```text
1. 场景澄清（15 秒）：
   "1M 文档直接塞进 Gemini 1.5 听上去可行，但评测显示有效长度只有 100-200k，
   而且 Lost in the Middle 让 P50 准确率掉 30%。
   我一般先 RAG、再 Long-Context 兜底。"

2. 策略组合（30 秒）：
   "分 3 步：
   - Step 1 用 Chunking 把文档切成 500-1000 token 的块，加 overlap 10-20%，
     加 metadata（source_doc/page/section）
   - Step 2 用 Embedding 模型（BGE-large / text-embedding-3）向量化，
     粗召回 top-50
   - Step 3 用 Cross-Encoder 重排（如 BGE-reranker），取 top-5
   - Step 4 把 top-5 + 问题拼 prompt 给 LLM
   评测召回率从 65% 提到 88%+"

3. 反模式 + 反选（25 秒）：
   "5 个反模式要避开：
   - 盲目长上下文：100k context 没用 Long-Context 是浪费
   - RAG 万能：会话状态 / 推理中间结果必须 prompt 内
   - Sub-Agents 滥用：拆 20 个子 Agent 通信成本爆炸
   - Lost in Middle：关键信息放中间就丢
   - 记忆不清理：向量库膨胀，召回率下降

   反过来：质量要求极高（金融/医疗）才上 Long-Context + RAG 双轨；
   一般业务用 RAG 优先 + Memory 模块。"

4. 反问（10 秒）：
   "贵司是单次文档问答，还是多轮对话会话？
   这两个不同场景策略不一样——前者 RAG 优先，后者需要 Memory。"
```

### 题目 B：Chunking 策略怎么选？chunk size 多少？

**高分答案**（45 秒）：

```text
"4 大 Chunking 策略选型：
1. Fixed：按 500 字切（图省事用，但切断句子）
2. Recursive：按段落/句子回退（Markdown 推荐）
3. Semantic：embedding 检测语义断点（最高质量，但 O(n²) 成本）
4. Agentic：用 LLM 自己判断（最智能，但慢 + 贵）

Chunk size：500-1000 token 最优（实测）
- < 500：召回多但质量低（噪声）
- > 1500：召回率断崖（块太大）

Overlap：10-20%（500 字 → 50-100 字重叠）

工业实操：Recursive Chunking + 500 token + 50 token overlap + 加 4 个 metadata
（source_doc / page / section / created_at）+ 评测集监控召回率。"
```

### 题目 C：RAG vs Long-Context 何时用哪个？

**高分答案**（40 秒）：

```text
"我的决策顺序：

1. 默认 RAG：成本低、召回可控、能用 Re-rank 优化
   - 适用：外部知识查询、文档问答、客服 FAQ

2. RAG 召回不足 → Long-Context 兜底：
   - 适用：单次文档问答（用户粘 100k token），代码库（< 50k 行）
   - 关键：把关键信息放两端（避免 Lost in Middle）

3. 极致准确 → 双轨：
   - RAG 结果 + Long-Context 原文档 同时给 LLM
   - 让 LLM 交叉验证
   - 适用：金融报表 / 医疗诊断 / 法律合同

反模式：用 Long-Context 替代 RAG 是浪费，
     用 RAG 替代所有上下文也是错（会话状态必须 prompt 内）。"
```

### 题目 D：Memory 模块怎么设计？4 层记忆有什么用？

**高分答案**（50 秒）：

```text
"Agent 4 层记忆架构：
1. Working Memory：当前会话激活上下文（prompt 内）
   - 用 Sliding Window + Summary 控制 size
2. Episodic Memory：用户历史交互 / 任务轨迹（向量库）
   - 每次对话结束写入，TTL 90 天
3. Semantic Memory：用户画像 / 偏好 / 知识（KV / 图数据库）
   - 显式 update + 定期从 episodic 提炼
4. Procedural Memory：输出格式 / 工具偏好 / 安全约束（YAML 配置文件）
   - 与代码同 Git

协作模式：
- 当前任务查询 → 查 working
- "我上周问过什么" → 查 episodic
- "用户 John 喜欢什么" → 查 semantic
- Agent 启动 → 加载 procedural

反模式：所有记忆都塞向量库（语义不清）或所有都放 working（成本爆炸）。"
```

### 题目 E：Sub-Agents 何时用？拆几个合理？

**高分答案**（40 秒）：

```text
"Sub-Agents 是"主 Agent 看摘要，子 Agent 看自己上下文"的拆分。

何时用：
- 任务流程清晰可分解（如研究 = 搜索+计算+写作）
- 单 Agent 上下文爆炸（如 50k+ 任务中间结果）
- 需要专门角色（如 PM + Designer + Engineer）

拆多少：3-5 个 sweet spot
- < 3：拆太粗，没意义
- 5-10：合理任务边界
- > 20：通信成本爆炸

4 大模式：
- Hierarchical：业务流（最常用）
- Collaborative：多视角讨论
- Sequential：流水线
- Mesh：复杂决策

反模式：
- 拆太细（20 个 Agent 通信 > LLM 推理）
- Sub-Agents 替代 RAG（知识检索仍要用 RAG）"
```

### 题目 F：Lost in the Middle 是什么？怎么破？

**高分答案**（35 秒）：

```text
"Lost in the Middle：模型对 prompt 中间信息利用最差（准确率 58%），
两端最好（85% / 80%）。Liu 2023 论文验证。

原因：attention 衰减 + 训练数据分布偏长尾。

6 个缓解技巧：
1. 重要信息放两端（开头 + 结尾）
2. Re-rank 让最相关在两端
3. RAG 替代（避免长 prompt）
4. 多轮 retrieve + 总结
5. 显式标位置 [位置 A] [位置 B]
6. 用 100k+ 模型（Qwen-2.5 实际有效 80k）

反模式：把关键事实放 prompt 中间（必丢）。"
```

### 题目 G：Sliding Window vs Long-Context Models 怎么平衡？

**高分答案**（35 秒）：

```text
"Sliding Window 解决 KV cache 显存问题：
- 100k context 用 sliding w=4k 显存等价 4k context
- 训练技巧：StreamingLLM（sink tokens）+ LongLoRA

工业范式：
- 业务上下文 < 32k：sliding window（Mistral 7B 启发了所有）
- 业务上下文 32-128k：Long-Context Models（Qwen 2.5）
- 业务上下文 > 128k：强制 RAG + Sub-Agents

别忘了：Long-Context 也有 Lost in Middle + 成本高 + 注意力衰减问题。

最佳混合：Long-Context（保留关键信息）+ Sliding Window（裁旧）
+ Memory（持久层）。"
```

---

## 三、常见陷阱（必选，7 个反模式）

### 陷阱 1：盲目用 Long-Context Models 替代 RAG

- **错误**："Gemini 1.5 1M context，所有文档都直接塞"
- **真相**：评测有效长度只有 100-200k；Lost in Middle 让 P50 掉 30%；成本爆炸
- **代价**：每千次调用浪费 $20+（10k token vs 1k token）

### 陷阱 2：Chunking 粒度调很大（2000+）

- **错误**："图省事，chunk size 调 3000"
- **真相**：chunk > 1500 token，RAG 召回率断崖（噪声信息过多）
- **代价**：召回率从 85% 掉到 65%，答非所问

### 陷阱 3：忽略 Re-rank

- **错误**："粗召回 top-5 直接用"
- **真相**：向量相似度 ≠ 真实相关性
- **代价**：粗召回 top-5 错率高，top-5 没用 Re-rank 错失 30% 准确率

### 陷阱 4：所有记忆塞向量库

- **错误**："Episodic + Semantic 全存向量库"
- **真相**：语义查询 vs 精确查询混用，导致 KV 字段也降级成向量
- **代价**：recall 慢 + 不精确

### 陷阱 5：Sub-Agents 拆太细

- **错误**：拆 20 个子 Agent，每个只做 1 步
- **真相**：子 Agent 通信本身耗 token，拆太细成本爆炸
- **代价**：通信 token > LLM 推理 token，总成本反增

### 陷阱 6：忽略 Lost in the Middle

- **错误**：把"关键事实 X"放 prompt 中间
- **真相**：中间位置准确率低至 58%，被模型"忽略"
- **代价**：LLM 答复"没见过" / 答错

### 陷阱 7：不建评测集

- **错误**：RAG 上线后不管召回率
- **真相**：embedding 模型 / chunking 都需要数据驱动调优
- **代价**：3 个月后 RAG 效果下降找不到原因

---

## 四、最佳实践（工业级方案）

### 方案 A：客服 Agent（推荐组合）

```text
Memory（用户画像）+ RAG（知识库）+ Sliding Window（会话）+ 偶尔 Long-Context

实施：
- Memory：KV 存用户偏好，向量存历史对话
- RAG：500 token chunk + semantic + Re-rank
- Sliding Window：w=8192 + sink tokens
- Long-Context：32k 一次性会话足够

效果：跨会话用户体验 + 单次回复准确率 90%+
```

### 方案 B：研究 Agent（推荐 Sub-Agents）

```text
Sub-Agents Hierarchical + RAG + Memory

子 Agent 拆分：
- Search Agent：搜索 + 检索
- Compute Agent：计算 + 分析
- Write Agent：撰写 + 润色
- 主 Agent：汇总 + 决策

效果：单 Agent 50k+ token → 主 Agent 5k + 子 Agent 各 10k
```

### 方案 C：金融分析师（极致准确）

```text
Long-Context 1M + RAG 双轨 + Sub-Agents + Memory

- RAG 先检索 top-10
- 同时塞入原文档（100k+）
- Sub-Agent 验证（3 个独立判断）
- Memory 记录研报历史

效果：P99 准确率 95%+（多源交叉验证）
```

### 关键决策表

| 场景 | 主策略 | 副策略 | 实施 |
|------|--------|--------|------|
| 客服 Agent | RAG + Memory | Sliding Window | < 30 LOC |
| 代码助手 | Long-Context + RAG | Chunking | tree-sitter |
| 文档分析 | RAG + Re-rank | Summary | 100-500 doc |
| 多轮对话 | Memory + Sliding | Long-Context 32k | StreamingLLM |
| 研究任务 | Sub-Agents + RAG | Memory | LangGraph |
| 金融分析 | 双轨 + Sub-Agents | Memory | Gemini 1.5 |

---

## 五、相关章节（强制）

### 主模块深度专题

- [11.ai agent-context 总目录](../../../11.ai/04-architecture/agent-context/README.md)
- [01-chunking](../../../11.ai/04-architecture/agent-context/01-chunking.md) —— 文本切片 4 大策略
- [02-rag-in-agent](../../../11.ai/04-architecture/agent-context/02-rag-in-agent.md) —— RAG 在 Agent 角色
- [03-memory-strategies](../../../11.ai/04-architecture/agent-context/03-memory-strategies.md) —— 4 层记忆架构
- [04-sliding-window-attention](../../../11.ai/04-architecture/agent-context/04-sliding-window-attention.md) —— Sliding Window Attention
- [05-sub-agents-decomposition](../../../11.ai/04-architecture/agent-context/05-sub-agents-decomposition.md) —— Multi-Agent 拆分
- [06-long-context-models](../../../11.ai/04-architecture/agent-context/06-long-context-models.md) —— Long-Context Models 实测
- [07-decision-tree](../../../11.ai/04-architecture/agent-context/07-decision-tree.md) —— 6 策略决策树

### 同栏目（11.ai）姐妹篇

- [context-engineering](../../11.ai/context-engineering-interview/README.md) —— Context Engineering 4 大原则
- [agent-memory-classification](../../11.ai/agent-memory-classification/README.md) —— Agent 记忆分类
- [rag](../../11.ai/rag/README.md) —— RAG 面试深挖
- [transformer](../../11.ai/transformer/README.md) —— Self-Attention 原理
- [function-calling](../../11.ai/function-calling/README.md) —— Tool Use

### 主模块兄弟

- [11.ai/02-technology-stack/context-engineering](../../../11.ai/02-technology-stack/context-engineering/README.md) —— Context Engineering 综述
- [11.ai/04-architecture/agent-memory](../../../11.ai/04-architecture/agent-memory/README.md) —— Agent 记忆架构
- [11.ai/04-architecture/agent-architecture](../../../11.ai/04-architecture/agent-architecture/README.md) —— Agent 架构总览

### 实战姐妹（12.story）

- [12.story/07-from-chef-to-ceo](../../../12.story/07-from-chef-to-ceo.md) —— 阿明餐厅 80 家连锁"长菜单与多订单"管理实战
- [12.story/39-ai-private-deployment](../../../12.story/39-ai-private-deployment.md) —— 私有化部署决策
- [12.story/30-agent-harness](../../../12.story/30-agent-harness.md) —— Agent Harness 工程

---

## 六、面试反问（让候选人反客为主）

```text
Q1：贵司 Agent 是客服 / 研究 / 代码 / 数据分析哪种？
    → 不同场景策略侧重不同
Q2：贵司对延迟的 P99 SLO 是多少？
    → < 500ms 必须用 Sliding Window + RAG
    → > 2s 可上 Long-Context
Q3：贵司是否跨会话记忆用户偏好？
    → 是：Memory 模块是必备
    → 否：可以简化
Q4：贵司对答案准确性要求？
    → 金融/医疗用 Long-Context + RAG 双轨
    → 一般业务用 RAG 即可
```

---

> 📅 2026-07-06 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 7 道精选 Q&A · 含 90 秒话术模板

← [返回: 咬文嚼字 · long-context-agent-strategy](../README.md)
