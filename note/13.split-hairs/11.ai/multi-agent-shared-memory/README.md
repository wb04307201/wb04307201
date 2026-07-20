<!--
question:
  id: 11.ai-multi-agent-shared-memory
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构设计追问
  tags: [11.ai, Multi-Agent, Shared-Memory, Blackboard, Coordinator, Vector-Store, Kafka]
-->

# 多 Agent 共享记忆 —— 5 大内容维度 + 3 大实现层 + 6 大模式 + 5 大反模式

> 一句话定位：**单 Agent Memory = 私有上下文；多 Agent 共享记忆 = 跨进程的状态/事实/语义同步，本质是分布式系统问题**。完整深度 + 6 大模式 + 一致性协议见 [主模块 · agent-memory 共享专章](../../../11.ai/04-architecture/agent-memory/shared-memory.md)。

> **系列定位**：Multi-Agent 经典跨域追问（Anthropic / OpenAI / 字节 / 阿里 / 美团 高频）。考察的不是"Memory 怎么分类"，而是 **5 大内容维度怎么共享 + 3 层架构怎么选 + 5 反模式怎么避 + 90 秒话术**。

---

⭐⭐⭐⭐⭐ 深度级别（高级 Agent 架构师）
📚 前置知识：单 Agent Memory / 分布式系统（Kafka/Redis）/ 向量数据库 / 一致性协议

---

## 引子：3 个崩溃现场

```text
场景：2025 字节 AI Agent 二面 3 个追问——

Q1：「多 Agent 系统怎么共享记忆？」
    → 初级："共享同一个 Vector DB"   ❌ 0 分
    → 中级："用 Redis 共享 K-V 状态"  60 分
    → 高分："5 大维度（上下文/事实/任务状态/技能/Memory 4 层）
            + 3 实现层（消息/状态/语义）+ 6 大共享模式
            + 5 大反模式"

Q2：「多个 Agent 都读写同一存储，会不会冲突？」
    → 初级："加锁"      ❌
    → 高分："版本号 + 乐观锁；
            黑板模式协调者托管 vs 共享存储竞争读 = 不同取舍；
            数据版本 timestamp 一致性"

Q3：「共享记忆的延迟要求是什么？」
    → 初级："越快越好"   ❌
    → 高分："5 大维度延迟要求不同：
            上下文 = ms
            事实 = s
            任务状态 = ms
            技能注册 = s
            Memory 4 层 = 取决于层"
```

---

## 一、核心原理（必选）

### 1.1 单 Agent Memory vs 多 Agent 共享记忆

```text
单 Agent Memory  =  私有上下文 → 不需要跨进程同步
多 Agent 共享   =  跨进程状态/事实/语义同步 → 分布式系统问题

类比：
- 单 Agent Memory = 进程内局部变量
- 多 Agent 共享   = 分布式 KV / 消息总线 / 共享语义库
```

### 1.2 5 大内容维度（**核心考点**）

| # | 维度 | 例子 | 同步延迟要求 |
|---|------|------|-----------|
| 1 | **共享上下文**（对话历史 / System Prompt）| 全 Agent 看到同一会话上下文 | ms |
| 2 | **共享事实知识**（用户偏好 / 项目规则 / SOP）| "用户喜欢中文简洁回答" | s |
| 3 | **共享任务状态**（黑板：任务进度 + 中间结果）| "步骤 3/7 已完成" | ms |
| 4 | **共享技能注册**（skill / tool / capability）| "新加载了 SQL 工具" | 弱实（秒级）|
| 5 | **共享 Memory 4 层**（Working / Episodic / Semantic / Procedural）| 跨 Agent 一致的 4 层 | 取决于层 |

### 1.3 3 大实现层（架构选型）

| 层 | 技术 | 适合 | 延迟 |
|----|------|------|------|
| **消息层**（最常用）| Kafka / Pulsar / Redis Stream | 事件流 + 异步解耦 | ms |
| **状态层** | Redis Cluster / etcd / Consul | K-V 状态 + 配置 + 锁 | ms |
| **语义层** | Milvus / Qdrant / Neo4j / 内存图 | 共享语义 / 知识图谱 | ms-s |

**最佳实践**：**3 层组合** — 消息层做事件总线 + 状态层做 KV + 语义层做向量。

### 1.4 6 大共享模式

| # | 模式 | 核心思想 | 适用 |
|---|------|---------|------|
| 1 | **黑板模式**（Blackboard）| 共享状态空间，Agent 读写同一 pool | 探索性 / 任务状态 |
| 2 | **协调者中转**（Orchestrator Broker）| 协调者托管状态，Agent 不直连 | **生产首选** |
| 3 | **共享 Vector Store**（向量检索）| 多 Agent 共写同一向量库 | RAG / 语义共享 |
| 4 | **共享消息队列**（Kafka Stream）| 异步事件流 + Consumer Group | 大规模事件流 |
| 5 | **共享 Memory Service**（统一 API）| 独立服务封装，Agent 调 API | 多语言 Agent |
| 6 | **共享知识图谱**（Graph RAG）| 共享 RAG 知识图谱 | 复杂关系网络 |

---

## 二、5 大反模式（高频陷阱）

| # | 反模式 | 后果 | 修复 |
|---|--------|------|------|
| 1 | **共享 = 传完整上下文** | Token 爆炸 + 延迟爆炸 | 任务 ID + 关键参数 only |
| 2 | **所有 Agent 都读写同一存储** | 数据竞争 + 一致性灾难 | 协调者托管 + 写者隔离 |
| 3 | **没版本 / 锁** | 读到旧值 / 写丢失 | version 字段 + 乐观锁 |
| 4 | **隐私 / 权限边界没设计** | 数据泄露（多租户场景）| RAG + 权限隔离 |
| 5 | **同步阻塞** | QPS 杀手 | 异步 + 缓存 + 乐观 |

---

## 三、5 大实战场景 + 选型

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| **CrewAI 多角色协作** | 黑板 + 共享向量 | 角色化 + 知识共享 |
| **AutoGen 对话式 Agent** | 消息队列 + 协调者 | 对话透明 + 审计 |
| **LangGraph 多 Agent** | 状态机 + DAG | 强结构化生产 |
| **MetaGPT 软件公司** | 共享知识图谱 | 角色化文档 + SOP |
| **生产级多 Agent 平台** | **协调者 + 状态层 + 语义层组合** | 灵活 + 可观测 |

---

## 四、实战代码（协调者中转 + 状态层 + 语义层组合）

```python
class SharedMemory:
    """多 Agent 共享记忆 — 状态层 + 语义层 + 消息层组合"""
    
    def __init__(self):
        # 1. 状态层：Redis Cluster（K-V 任务状态）
        self.redis = RedisCluster()
        # 2. 语义层：Milvus（向量检索 / 共享知识）
        self.vector_db = Milvus()
        # 3. 消息层：Kafka（事件流）
        self.kafka = Kafka()
    
    # ---- 维度 1：共享上下文 ----
    def put_context(self, task_id, key, value):
        self.redis.hset(f"ctx:{task_id}", key, value)
        # 版本号支持乐观锁
        self.redis.hincrby(f"ctx:{task_id}", "_version", 1)
        self.kafka.send("ctx_update", 
                       {"task_id": task_id, "key": key, "v": time.time()})
    
    def get_context(self, task_id, key):
        return self.redis.hget(f"ctx:{task_id}", key)
    
    # ---- 维度 2：共享事实知识 ----
    def share_fact(self, agent_id, fact, embedding):
        self.vector_db.insert(
            fact_id=hash(fact),
            vector=embedding,
            metadata={"source": agent_id, "ts": time.time()}
        )
    
    # ---- 维度 3：共享任务状态 ----
    def update_task(self, task_id, status, progress):
        # 乐观锁：CAS
        while True:
            current = self.redis.hgetall(f"task:{task_id}")
            if self.redis.hset(f"task:{task_id}",
                                mapping={"status": status, "progress": progress},
                                nx=False):
                break
    
    # ---- 维度 4：共享技能 ----
    def register_skill(self, agent_id, skill):
        self.redis.sadd(f"skills:{agent_id}", skill.name)
        self.kafka.send("skill_registered",
                       {"agent_id": agent_id, "skill": skill.name})
    
    # ---- 维度 5：Memory 4 层共享 ----
    def share_memory_layer(self, agent_id, layer, data):
        """layer in {working, episodic, semantic, procedural}"""
        if layer == "working":
            self.redis.set(f"working:{agent_id}", data)        # ms 实时
        elif layer == "episodic":
            self.kafka.send(f"episodic:{agent_id}", data)      # s 准实时
        elif layer == "semantic":
            self.share_fact(agent_id, data.text, data.embedding)
        elif layer == "procedural":
            self.vector_db.insert(rule_id=data.id, vector=data.embedding,
                                  metadata={"type": "procedure"})
```

---

## 五、面试话术（90 秒版本）

### 题目：多 Agent 系统怎么实现共享记忆？

**高分答案（4 层递进，60-90 秒）**：

```text
1. 一句话（10 秒）：
   "单 Agent Memory = 私有上下文；
    多 Agent 共享 = 分布式系统问题。
    共享 5 大内容维度，3 层实现，6 大模式，5 反模式。"

2. 5 大内容维度（25 秒）：
   "5 大内容维度同步要求不同：
   ① 共享上下文（对话历史/System Prompt）：ms
   ② 共享事实知识（用户偏好/SOP）：s
   ③ 共享任务状态（黑板）：ms
   ④ 共享技能注册：弱实
   ⑤ Memory 4 层共享：取决于层"

3. 3 大实现层 + 6 模式（25 秒）：
   "3 层实现：
   ① 消息层：Kafka/Pulsar（事件流）
   ② 状态层：Redis Cluster（K-V + 锁）
   ③ 语义层：Milvus/Qdrant（向量）
   6 模式：黑板 / 协调者中转 / 共享向量 / 共享 MQ /
          共享 Memory Service / 共享知识图谱
   生产首选：协调者 + 状态层 + 语义层组合"

4. 5 反模式 + 权衡（30 秒）：
   "5 大反模式：
   - 共享 ≠ 传完整上下文（Token 爆炸）
   - 所有 Agent 都读写 → 数据竞争
   - 没版本/锁 → 一致性灾难
   - 权限边界没设计 → 多租户泄露
   - 同步阻塞 → QPS 杀手
   实战关键：版本号 + 乐观锁 + 异步 + 权限隔离"
```

---

## 六、面试反问（让候选人反客为主）

```text
Q1：贵司多 Agent 用哪种共享模式？为什么？
    → 答协调者中转 + 理由 = 高分
Q2：多个 Agent 写同一存储怎么处理冲突？
    → 答版本号 + 乐观锁 = 高分
Q3：共享记忆的延迟要求是？
    → 答按维度分级（ms/s） = 高分
Q4：贵司怎么做权限隔离？
    → 答 RAG + ACL = 高分
Q5：共享 Memory 的 4 层延迟分别多少？
    → 答 Working ms / Episodic s / Semantic s / Procedural min = 高分
```

---

## 🔗 系列导航表（13.split-hairs · 11.ai 兄弟）

| 章节 | 核心考点 | 频率 |
|------|---------|------|
| [agent-dag-vs-react](../agent-dag-vs-react/README.md) | Agent DAG vs ReAct | ⭐⭐⭐⭐ |
| [agent-memory-classification](../agent-memory-classification/README.md) | Agent Memory 三维分类 | ⭐⭐⭐⭐ |
| [agent-performance-evaluation](../agent-performance-evaluation/README.md) | Agent 6 大评测维度 | ⭐⭐⭐⭐⭐ |
| [claude-code-agentic-search](../claude-code-agentic-search/README.md) | Claude Code 搜索 | ⭐⭐⭐⭐ |
| [function-calling](../function-calling/README.md) | Function Calling | ⭐⭐⭐⭐⭐ |
| [long-context-agent-strategy](../long-context-agent-strategy/README.md) | 长上下文 6 策略 | ⭐⭐⭐⭐⭐ |
| [loop-engineering](../loop-engineering/README.md) | Loop 兜底 | ⭐⭐⭐⭐ |
| [multi-agent-system-design](../multi-agent-system-design/README.md) | Multi-Agent 5 组件 + 死循环 4 兜底 | ⭐⭐⭐⭐⭐ |
| [multi-turn-tool-reasoning](../multi-turn-tool-reasoning/README.md) | 多轮工具推理 | ⭐⭐⭐⭐⭐ |
| [react-vs-plan-execute](../react-vs-plan-execute/README.md) | ReAct vs Plan-Execute | ⭐⭐⭐⭐⭐ |
| **multi-agent-shared-memory**（本篇）| 5 大维度 + 3 层 + 6 模式 + 5 反模式 | ⭐⭐⭐⭐⭐ |

## 🔗 深度版（主模块）

- [11.ai · agent-memory 共享专章](../../../11.ai/04-architecture/agent-memory/shared-memory.md) — 5 大维度详解 + 3 层架构 + 6 模式实战 + 一致性协议 + 选型决策

---

> 📅 2026-07-13 · 咬文嚼字 · 11.ai · ⭐⭐⭐⭐⭐ · 5 维度 + 3 层 + 6 模式 + 5 反模式 + 90 秒话术 + 11 兄弟导航

← [返回: 咬文嚼字 · 11.ai](../README.md)
