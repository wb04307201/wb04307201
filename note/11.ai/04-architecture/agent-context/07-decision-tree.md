<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/07-decision-tree
  type: topic
  category: 选型决策
  summary: Agent 长上下文 6 策略场景化决策树 + 反模式 + checklist
-->

# 6 策略决策树 · Agent 长上下文选型不迷路

> **一句话**：6 大策略**没有最优解**——只有「场景 × 负载 × 成本」3 维约束下的最优组合。给一张「5 分钟决策树」+「实施 checklist」。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 5 分钟决策树

```
Q1：你的输入是哪种类型？
├─ 长文档 / 代码（用户粘进来的）→ A 长输入
├─ 多轮对话累积 → B 长会话
├─ 外部知识库查询 → C 长检索
└─ 复杂任务流 → D 复杂任务

Q2：上下文总长预估？
├─ < 4k       → 不需要任何策略，prompt 即可
├─ 4k-32k    → 2-3 策略组合
├─ 32k-128k  → 必须 3+ 策略
└─ > 128k    → 强制 RAG 或 sub-agents

Q3：质量要求 vs 成本？
├─ 极致准确（金融/医疗）→ 双轨（Long-Context + RAG）
├─ 一般业务            → RAG 优先 + Memory
├─ 成本敏感            → Chunking + Sliding Window
└─ 研发原型            → 全部用 Long-Context Models

Q4：是否需要跨会话记忆？
├─ 是（个性化 Agent）→ 加 Semantic Memory
└─ 否（任务级）      → Working + Episodic 即可

Q5：任务是否可分解？
├─ 是（流程清晰）→ Sub-Agents Hierarchical
└─ 否（强耦合）   → 单 Agent + 全部上下文
```

---

## 2. 场景化配置矩阵

| 场景 | 推荐策略组合 | 实施要点 |
|------|-------------|---------|
| **客服 Agent** | Memory（用户画像）+ RAG（知识库）+ Sliding Window（会话）| 长期用户偏好 + 实时检索 |
| **代码助手** | Long-Context（10-30k 代码）+ RAG（仓库检索）| IDE 集成 + tree-sitter |
| **文档分析** | Chunking + RAG + Re-rank + Summary | 处理 100k+ PDF |
| **多轮对话机器人** | Sliding Window + StreamingLLM + Memory | 8k-32k 上下文 |
| **研究 Agent** | Sub-Agents + RAG + Memory | 拆解多步研究 |
| **金融分析师** | Long-Context 1M + RAG 双轨 | 财报 + 实时数据 |
| **客服 FAQ** | RAG + 简单 Memory | 低 QPS 高准确 |

---

## 3. 实施 Checklist（部署长上下文 Agent）

### 3.1 评估层

- [ ] 真实场景上下文长度分布（histogram）
- [ ] Lost in Middle 评估：在 prompt 不同位置放关键信息
- [ ] 召回准确率（每 100 query 抽样）
- [ ] 端到端延迟（P50/P95/P99）

### 3.2 工程层

- [ ] **Chunking**
  - [ ] 选择策略（fixed/recursive/semantic/agentic）
  - [ ] chunk size = 500-1000 token
  - [ ] overlap = 10-20%
  - [ ] metadata：source_doc / page / section
- [ ] **RAG**
  - [ ] embedding 模型选型（bge-large / text-embedding-3）
  - [ ] 向量库选型（Qdrant / Milvus / PgVector）
  - [ ] Re-rank 模型（bge-reranker-large）
  - [ ] 粗召回 top-50 → Re-rank top-5
- [ ] **Memory 模块**
  - [ ] 4 层分类（working / episodic / semantic / procedural）
  - [ ] 写入触发点定义
  - [ ] episodic TTL / 清理策略
  - [ ] semantic 冲突解决策略
- [ ] **Sliding Window**
  - [ ] 模型选型（Mistral 7B / Qwen 2.5）
  - [ ] window size（4096-8192）
  - [ ] sink tokens 保留
- [ ] **Sub-Agents**
  - [ ] 选择模式（Hierarchical / Collaborative）
  - [ ] 任务拆分（按步骤/角色/数据源）
  - [ ] 通信协议（结构化摘要）
  - [ ] 终止条件（max_turns）

### 3.3 监控层

- [ ] 每个 query 的 token 数分布
- [ ] Lost in Middle 命中率（线上评估）
- [ ] 召回率 + 重排率
- [ ] Memory 命中率
- [ ] Sub-Agent 调用次数 + 终止原因

---

## 4. 反模式速查（5 个常见错）

| 反模式 | 症状 | 修复 |
|--------|------|------|
| **盲目长上下文** | 全部塞 prompt | 先 RAG，召回不足再上 Long-Context |
| **RAG 万能** | 取代所有上下文 | RAG + Memory + Sliding Window 组合 |
| **Sub-Agents 滥用** | 拆 20 个子 Agent | 3-5 个 sweet spot |
| **Lost in Middle 忽视** | 关键信息放中间 | 重要信息两端 + 标位置 |
| **记忆不清理** | 向量库无限膨胀 | TTL + 重要性评分 |

---

## 5. 反向决策 · 5 个错误信号

| 错误信号 | 含义 |
|---------|------|
| Agent 答非所问持续 3 天+ | 长上下文配置有问题 |
| 每次调用 token > 50k | 应该用 RAG 或 Sub-Agents |
| 显存持续 OOM | 长上下文 + 多并发超容量 |
| Memory 模块崩溃后丢失关键信息 | 没分层备份 |
| Sub-Agents 通信成本 > LLM 推理成本 | 拆太细 |

---

## 6. 一句话总结（决策树精简版）

```
Q1：输入类型 → A 长输入 / B 长会话 / C 长检索 / D 复杂任务
Q2：上下文总长 → < 4k 不动 / 4k-128k 策略组合 / > 128k 强制 RAG+Sub
Q3：质量 vs 成本 → 极致准确 Long-Context+RAG / 一般 RAG+Memory
Q4：跨会话 → 加 Semantic Memory / 否 Working+Episodic
Q5：可分解 → Sub-Agents / 否 单 Agent+全上下文
```

---

## 7. 速查 · 6 策略对比速查表

| 策略 | 复杂度 | 成本 | 适用 |
|------|--------|------|------|
| Chunking | 低 | 低 | 任意长输入/检索 |
| RAG | 中 | 中 | 长检索 / 外部知识 |
| Memory | 中 | 中 | 长会话 / 个性化 |
| Sliding Window | 低 | 低 | 长会话 / 流式 |
| Sub-Agents | 高 | 高 | 复杂任务 |
| Long-Context | 低 | 高 | 单次长输入 |

---

## 8. 一句话总结

> **Agent 长上下文不是「选策略」而是「选组合」——6 大策略按场景组合，按成本权衡，按监控迭代。先评估后实施，先 RAG 后 Long-Context，先简单组合后复杂分拆。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[06-long-context-models](06-long-context-models.md) · 专题结束
