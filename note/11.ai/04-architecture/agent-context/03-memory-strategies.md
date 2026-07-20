<!--
module:
  parent: ai/agent-architecture/agent-context
  slug: ai/agent-architecture/agent-context/03-memory-strategies
  type: topic
  category: 分层记忆
  summary: Agent 4 层记忆架构：working / episodic / semantic / procedural + 写入时机 + 检索策略 + 反模式
-->

# Memory 分层记忆 · Agent 4 层记忆架构

> **一句话**：Agent 不是 stateless——必须有"持久记忆"才能在长会话跨任务保持连贯。4 层记忆架构（working / episodic / semantic / procedural）是工业级方案。

← [返回: Agent 长上下文架构](../README.md)

---

## 1. 为什么 Agent 需要记忆？

无状态 LLM 在多轮场景的问题：
- 第 10 轮忘了用户在第 1 轮说的偏好
- 跨 session 没法积累用户画像
- 任务执行进度会丢失

记忆的本质：**让 prompt 内的"工作上下文"和"外部持久化层"协作**。

---

## 2. 4 层记忆架构

| 层级 | 时长 | 内容 | 存储 | 写入时机 |
|------|------|------|------|---------|
| **Working**（工作记忆）| 当前会话 | 当前任务上下文 | Prompt context | 实时 |
| **Episodic**（情景记忆）| 短期（天/周）| 用户历史交互 / 任务轨迹 | 向量库 | 每次对话结束 |
| **Semantic**（语义记忆）| 长期（月/年）| 用户画像 / 知识沉淀 | 图数据库 / KV | 显式 update |
| **Procedural**（程序记忆）| 永久 | 工具调用 / 偏好 / 风格 | 配置文件 | 启动时加载 |

---

## 3. Working Memory（工作记忆）

**作用**：当前会话的"激活上下文"。

**实现要点**：
- Token 容量限制（如 32k / 100k / 1M）
- Sliding Window（淘汰旧 token）
- Summary（定期压缩旧信息）

```python
# 简化实现：保留最近 10 轮对话 + 总结更早
def working_memory(messages, max_turns=10):
    if len(messages) <= max_turns:
        return messages
    recent = messages[-max_turns:]
    older_summary = llm.summarize(messages[:-max_turns])
    return [{"role": "system", "content": f"对话历史摘要：{older_summary}"}] + recent
```

**反模式**：
- ⚠️ 把所有历史消息塞进 prompt（成本爆炸）
- ⚠️ 忘记删除 system 中间产物（污染上下文）

---

## 4. Episodic Memory（情景记忆）

**作用**：记录"发生过什么"——用户交互历史、任务执行轨迹。

**数据结构**：
```json
{
  "episode_id": "ep_20240715_001",
  "timestamp": "2024-07-15 10:30",
  "user_id": "u_123",
  "type": "support_ticket",
  "content": {
    "user_query": "...",
    "agent_response": "...",
    "tools_used": ["search_kb", "create_ticket"],
    "outcome": "resolved"
  },
  "embedding": [0.012, 0.045, ...]
}
```

**检索**：
- 按时间倒序（最近）
- 按相似度（语义匹配）

**写入时机**：
- 每次对话结束（自动）
- 用户显式"记住这个"（手动）

---

## 5. Semantic Memory（语义记忆）

**作用**：长期沉淀的"事实"——用户画像、偏好、知识图谱。

**实现方式**：
- KV 存储（如 Redis）
- 图数据库（如 Neo4j）记录实体关系
- 向量库（按语义检索）

```python
# 简化：长期偏好存储
semantic_memory = {
    "user_id": "u_123",
    "expertise_level": "senior_developer",
    "preferred_language": "zh-CN",
    "communication_style": "concise_with_code",
    "domain_expertise": ["AI", "distributed_systems"],
    "last_updated": "2024-07-15"
}
```

**写入时机**：
- 用户显式要求（"记住我喜欢用 PostgreSQL"）
- Agent 推断（高频出现 → 推断为偏好）
- 定期总结（每周从 episodic 提炼）

---

## 6. Procedural Memory（程序记忆）

**作用**：固定的工作方式——输出格式、工具调用偏好、安全约束。

**示例**：
```yaml
agent:
  output_format:
    always_json: true
    schema_version: "1.2"
  tool_preferences:
    search: ["vector_db", "web_search"]
    computation: ["python_repl"]
  safety:
    max_tool_calls_per_turn: 10
    forbidden_topics: ["medical_advice"]
```

**实现方式**：
- YAML / JSON 配置文件
- 与代码一同版本控制（Git）
- 启动时加载到 system prompt

---

## 7. 4 层协作：信息流

```text
       User Query
            ↓
   [Working Memory] ← 当前会话激活上下文
            ↓
     (检索 episodic/semantic)
            ↓
      Agent Decision
            ↓
   [Action / Tool Use]
            ↓
   (更新 episodic)
            ↓
   (定时提炼 semantic)
```

**写入策略**：
| 触发点 | 写入层 |
|--------|-------|
| 每个 tool call 返回 | Working → Episodic |
| 用户说"记住 X" | Semantic（立即）|
| 对话关闭 | Episodic（完整存档）|
| 每周定时任务 | Episodic → Semantic 提炼 |
| Agent 启动 | Procedural 加载 |

---

## 8. 记忆检索策略

### 8.1 何时检索 episodic vs semantic？

| 查询类型 | 检索层 | 例 |
|---------|--------|-----|
| 过去 X 时间我做过什么 | Episodic | "我上周问过什么"|
| 关于 X 用户的事实 | Semantic | "用户 John 喜欢什么"|
| 当前任务的上下文 | Working | 当前 session 内 |

### 8.2 检索工具组合

```python
# Agent 自行决定查哪层
def retrieve_context(query, user_id):
    results = []
    # Working: 当前 session（已在 prompt）
    # Episodic: 向量相似
    ep_hits = episodic_vector.search(query, user_id, top_k=3)
    # Semantic: KV 精确查
    if query mentions entity:
        sem_hit = semantic_kv.get(user_id, entity)
        results.extend([ep_hits, sem_hit])
    return results
```

---

## 9. 反模式 · Agent 记忆的 5 个错

### ⚠️ 反模式 1：所有信息塞进 working memory

- 错：把 100 轮对话全塞 prompt
- 对：旧对话摘要 + 新轮次

### ⚠️ 反模式 2：episodic 无限增长不清理

- 错：所有历史都存向量库
- 对：设 TTL（如 90 天）+ 重要性评分清理

### ⚠️ 反模式 3：semantic 写太多矛盾信息

- 错：semantic 多次 update 同一字段冲突
- 对：用"最近写入覆盖"或显式冲突解决

### ⚠️ 反模式 4：procedural 和代码不同步

- 错：procedural 配置文件与代码不一致
- 对：procedural 入 Git，与代码一同 review

### ⚠️ 反模式 5：不区分 4 层，混着用

- 错：所有记忆都存向量库
- 对：working in prompt / episodic in vector / semantic in KV / procedural in YAML

---

## 10. 一句话总结

> **Agent 记忆 = Working（实时）+ Episodic（事件）+ Semantic（事实）+ Procedural（流程）4 层协作——不是单一存储，是分层架构，每层有自己的写入时机和检索方式。**

---

← [返回: Agent 长上下文架构](../README.md) · 上一章：[02-rag-in-agent](02-rag-in-agent.md) · 下一章：[04-sliding-window-attention](04-sliding-window-attention.md)
