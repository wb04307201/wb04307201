<!--
module:
  parent: ai/agent-memory
  slug: ai/agent-memory/shared-memory
  type: deep-dive
  category: 主模块子文章
  summary: 多 Agent 共享记忆深度原理 —— 5 大内容维度 + 3 大实现层 + 6 大模式 + 一致性协议。
-->

# 多 Agent 共享记忆 · 深度专章

> 一句话定位：**单 Agent Memory 解决"跨调用"；多 Agent 共享记忆解决"跨进程"，本质是分布式系统问题**。完整体系基于 [主模块 · Agent Memory 架构](README.md)。面试速查版见 [13.split-hairs · multi-agent-shared-memory](../../../../13.split-hairs/11.ai/multi-agent-shared-memory/README.md)。

---

## 一、为什么多 Agent 需要共享记忆

### 1.1 单 Agent Memory 的局限

```text
单 Agent Memory：
  Agent ←→ 私有 Memory（进程内 / 私有 DB）
  问题：跨 Agent 不可见 → 协同任务失败

举例：
  - Agent A 调研 → 结论只有 A 自己知道
  - Agent B 编码 → 拿不到 A 的结论 → 重复调研 / 不一致
  - Agent C review → 看不到 A + B 的中间结果
```

### 1.2 多 Agent 共享的 4 大业务驱动力

| # | 驱动力 | 例子 |
|---|--------|------|
| 1 | **任务连续性** | A → B → C 接力必须看到前序中间结果 |
| 2 | **一致性约束** | 所有 Agent 必须用同一 SOP / 同一规则 |
| 3 | **能力复用** | A 加载了 SQL 工具，B 直接用 |
| 4 | **可观测 + 审计** | 协调者要看到所有 Agent 的状态 |

---

## 二、5 大共享内容维度（**核心考点**）

| # | 维度 | 同步延迟 | 一致性要求 | 实现 |
|---|------|---------|-----------|------|
| 1 | **共享上下文**（对话历史 / System Prompt）| ms | 强一致 | Redis Hash + Kafka |
| 2 | **共享事实知识**（用户偏好 / SOP / 规则）| s | 最终一致 | Vector DB + CDC |
| 3 | **共享任务状态**（黑板）| ms | 强一致（带版本）| Redis + Optimistic Lock |
| 4 | **共享技能注册** | s | 最终一致 | K-V + Kafka publish |
| 5 | **Memory 4 层共享**（Working/Episodic/Semantic/Procedural）| 分级 | 分级 | 分层存储 |

### 2.1 维度 1：共享上下文

```python
# 设计原则：每 Agent 写 + 全 Agent 读 + 协调者收尾
ctx_key = f"ctx:{task_id}"

def write_context(agent_id, task_id, delta):
    redis.hset(ctx_key, "_last_writer", agent_id)
    redis.hset(ctx_key, agent_id, delta)
    redis.expire(ctx_key, 86400)  # 1 天过期

def read_context(task_id, agent_id=None):
    return redis.hgetall(ctx_key)
```

### 2.2 维度 2：共享事实知识

```python
# 语义共享：vector DB 写入 + 检索
def share_fact(agent_id, fact_text, embedding):
    vector_db.insert(
        id=f"{agent_id}:{uuid4()}",
        vector=embedding,
        text=fact_text,
        metadata={"source": agent_id, "ts": time.time()}
    )

def query_shared_knowledge(query_embedding, top_k=5,
                            agent_id_filter=None):
    """ag_id_filter 实现权限隔离（多租户）"""
    return vector_db.search(
        query_embedding,
        top_k=top_k,
        filter=agent_id_filter  # 只有这个 Agent 能读的
    )
```

### 2.3 维度 3：共享任务状态（黑板）

```python
def update_task_state(task_id, agent_id, status, progress):
    # 乐观锁 + CAS
    for retry in range(3):
        with redis.lock(f"task_lock:{task_id}", timeout=1):
            current = redis.hgetall(f"task:{task_id}")
            new = {**current,
                   "status": status,
                   "progress": progress,
                   "_last_agent": agent_id,
                   "_version": current.get("_version", 0) + 1}
            if redis.hset(f"task:{task_id}", mapping=new):
                kafka.send("task_update", {"task_id": task_id, ...})
                return True
    return False
```

### 2.4 维度 4：共享技能注册

```python
def register_skill(agent_id, skill):
    redis.sadd(f"skills:{agent_id}", skill.name)
    redis.hset(f"skill_meta:{skill.name}",
               mapping={"source": agent_id,
                        "version": skill.version,
                        "schema": json.dumps(skill.schema)})
    # 广播：所有 Agent 可订阅
    kafka.send("skill_registered", {"skill": skill.name,
                                      "version": skill.version})

def discover_skills(task_id):
    """任务开始时调度器动态发现可用 skill"""
    return redis.zrange(f"task_skills:{task_id}", 0, -1, withscores=True)
```

### 2.5 维度 5：Memory 4 层共享（最难）

| 层 | 内容 | 共享延迟 | 实现 |
|----|------|---------|------|
| **Working**（实时上下文）| 当前任务的状态/变量 | ms | Redis |
| **Episodic**（事件）| 过去的动作 + 结果 | s | Kafka Stream |
| **Semantic**（事实）| 长期知识 + 概念 | s | Vector DB |
| **Procedural**（流程）| SOP / 规则 | min | LangGraph / 文件 |

**关键挑战**：4 层延迟要求差 6 个数量级，**不要用同一存储**。

---

## 三、3 大实现层

| 层 | 组件 | 延迟 | 强项 | 弱项 |
|----|------|------|------|------|
| **消息层**（事件流）| Kafka / Pulsar / Redis Stream | ms | 异步解耦 + 顺序保证 + Consumer Group | 强一致查询弱 |
| **状态层**（K-V）| Redis Cluster / etcd / Consul | ms | 强一致 + 锁 + 原子操作 | 容量受限 |
| **语义层**（语义）| Milvus / Qdrant / Neo4j | ms-s | 向量检索 / 图遍历 / 知识推理 | 不适合 K-V 强一致 |

### 3.1 最佳实践组合

```text
消息层：Kafka / Pulsar（异步事件总线）
   ↓ CDC 同步
状态层：Redis Cluster（K-V + 锁）
   ↓ 双写
语义层：Milvus / Neo4j（语义 + 知识图谱）
```

**生产架构示意**：

```text
┌──────────────────────────────────────────┐
│  Agent A (researcher)                   │
│  ├── 写：维度 1 共享上下文（Redis HSET） │
│  └── 读：维度 2 共享事实（Milvus query）│
├──────────────────────────────────────────┤
│  Agent B (developer)                    │
│  ├── 读：维度 1 上下文 / 维度 3 任务状态 │
│  └── 写：维度 3 进度（Redis CAS + Kafka） │
├──────────────────────────────────────────┤
│  Agent C (reviewer)                     │
│  └── 读：维度 2 事实 / 维度 3 状态        │
└──────────────────────────────────────────┘
         │           │            │
         └───────────┼────────────┘
                     ↓
   ┌──────────────────────────────────────┐
   │  共享存储层                          │
   │  ├── 消息层：Kafka（CDC + 事件流）   │
   │  ├── 状态层：Redis Cluster          │
   │  └── 语义层：Milvus + Neo4j         │
   └──────────────────────────────────────┘
                     ↓
   ┌──────────────────────────────────────┐
   │  协调者（Orchestrator / Broker）     │
   │  ├── 任务分发                        │
   │  ├── 进度汇总                        │
   │  ├── 冲突解决                        │
   │  └── 终止判断                        │
   └──────────────────────────────────────┘
```

---

## 四、6 大共享模式深度对比

### 4.1 黑板模式（Blackboard）

```python
# 所有 Agent 都读写同一"黑板"
# 优点：解耦
# 缺点：状态一致性 + 写入竞争
def blackboard_read(agent_id, key):
    return blackboard.get(key)

def blackboard_write(agent_id, key, value):
    blackboard.put(key, value, _writer=agent_id,
                   _version=auto_inc())
```

**生产推荐**：**协调者托管**（5.2），不要直连黑板。

### 4.2 协调者中转（Orchestrator Broker）——**生产首选**

```python
class Orchestrator:
    def __init__(self):
        self.broker = MemoryBroker()  # 共享记忆服务
    
    def dispatch(self, task):
        # 1. 解析任务
        # 2. 选 Agent（看 capabilities 注册）
        # 3. 装入上下文
        # 4. 调用 Agent
        # 5. 收集结果
        # 6. 更新共享记忆
        pass
```

**优点**：所有写经过协调者，**审计 + 一致性可控**。
**缺点**：协调者成为单点（需多副本 + leader election）。

### 4.3 共享 Vector Store（语义共享）

适用：所有 Agent 需要查同一知识库（RAG）。

```python
# 写入：所有 Agent 都有写权限
def agent_share_knowledge(agent_id, content):
    vector_db.upsert(
        id=f"{agent_id}:{uuid4()}",
        embedding=embed(content),
        text=content,
        metadata={"source_agent": agent_id, "ts": time.time()}
    )

# 检索：所有 Agent 共享 top_k
def query_knowledge(query, top_k=5, agent_id_filter=None):
    return vector_db.search(query, top_k=top_k,
                           filter=agent_id_filter)
```

### 4.4 共享消息队列（Kafka Stream）

适用：高并发 + 多 Agent 异步解耦 + 事件溯源。

```python
# 写入
def agent_emit_event(agent_id, event):
    kafka.send(f"agent:{agent_id}",
              payload=event, key=agent_id)

# 订阅
def agent_subscribe(task_id):
    consumer = kafka.consumer(f"task:{task_id}",
                              group_id=f"agent_{agent_id}")
    for msg in consumer:
        process(msg)
```

### 4.5 共享 Memory Service（统一 API）

适用：多语言 Agent 团队，封装成独立服务。

```python
class MemoryService:
    """统一 API 网关"""
    
    def put(self, namespace, key, value, agent_id):
        # 权限检查
        if not self.check_permission(agent_id, namespace, key):
            raise PermissionError()
        # 多层存储
        redis.set(f"{namespace}:{key}", value)
        if self.needs_vector_index(value):
            vector_db.insert(...)
        # 异步广播
        kafka.send("memory_updated", ...)
    
    def get(self, namespace, key, agent_id):
        if not self.check_permission(agent_id, namespace, key):
            return None  # 权限拒绝而不是抛错（防侧信道）
        return redis.get(f"{namespace}:{key}")
```

### 4.6 共享知识图谱（Graph RAG）

适用：复杂关系网络（人物关系 / 知识依赖 / SOP 链路）。

```python
# Neo4j 示例
def share_relationship(agent_id, subj, pred, obj):
    neo4j.query(
        "MERGE (a:Entity {name: $subj}) "
        "MERGE (b:Entity {name: $obj}) "
        "MERGE (a)-[r:REL {type: $pred, source: $agent_id}]->(b)",
        subj=subj, pred=pred, obj=obj, agent_id=agent_id
    )
```

---

## 五、一致性协议（**易踩的坑**）

### 5.1 三大一致性级别

| 级别 | 实现 | 延迟 | 适合 |
|------|------|------|------|
| **强一致** | Redis + 乐观锁 / etcd | ms | 任务状态 / 配置 |
| **最终一致** | Kafka + CDC / Vector DB | s | 事实 / 知识 |
| **弱一致** | 单写多读 / 缓存 | 异步 | 日志 / 度量 |

### 5.2 5 大生产级一致性陷阱

| # | 陷阱 | 后果 | 修复 |
|---|------|------|------|
| 1 | 写后立即读（没等同步）| 读到旧值 | 显式 await 同步 |
| 2 | 并发写无锁 | 写丢失 / 版本错乱 | 乐观锁 + CAS |
| 3 | 网络分区下脑裂 | 部分 Agent 看不同世界 | quorum + fencing |
| 4 | 缓存过期不一致 | 状态错位 | TTL + 显式失效 |
| 5 | 失败写补偿不到位 | 写半成品 | saga / outbox |

### 5.3 实战：版本号 + 乐观锁（必加）

```python
def safe_update(key, delta_fn, max_retry=3):
    """带版本号的乐观锁 CAS"""
    for attempt in range(max_retry):
        current = redis.get(key)
        if current is None:
            return redis.set(key, delta_fn(None), nx=True)
        
        # 检查版本
        new_version = current.get("_version", 0) + 1
        new_value = {**current, **delta_fn(current),
                     "_version": new_version}
        
        # Lua 脚本保证原子 CAS
        lua = """
        if redis.call('GET', KEYS[1]) and 
           string.sub(redis.call('GET', KEYS[1]), -10) == ARGV[1]
        then
            redis.call('SET', KEYS[1], ARGV[2])
            return 1
        end
        return 0
        """
        old_version_str = f"v{current['_version']}_"
        if redis.eval(lua, 1, key, old_version_str, json.dumps(new_value)):
            return new_value
    raise ConcurrentModificationError()
```

---

## 六、6 大实战框架对比（**加分项**）

| 框架 | 共享模式 | 适用场景 | 关键 API |
|------|---------|---------|---------|
| **CrewAI** | 共享 Vector + 任务流 | 角色化协作快速原型 | `Crew(agents, tasks, memory=True)` |
| **AutoGen** | 消息队列 + GroupChat | 通用多 Agent | `GroupChat(messages, ...)` |
| **LangGraph** | 状态机 + Checkpoint | 生产级强结构化 | `MemorySaver()` |
| **MetaGPT** | 共享知识图谱 + SOP | 软件开发场景 | `SoftwareCompany()` |
| **ChatDev** | 黑板模式 + 阶段式 | 软件开发流水线 | `ChatChain([...])` |
| **OpenAI Assistants** | Vector Store + 共享 Thread | 商业多 Agent | `tool_resources={file_search}` |

### 6.1 实战案例：CrewAI 共享 Vector Store

```python
from crewai import Agent, Task, Crew
from crewai.memory import LongTermMemory

# 1. 创建共享 Vector Store
ltm = LongTermMemory(
    storage_backend="vector_db",
    embedding_model="text-embedding-3-small",
    collection_name="crew_shared"
)

# 2. 多 Agent 共享同一 ltm
researcher = Agent(role="研究员", memory=ltm)
developer = Agent(role="开发员", memory=ltm)
reviewer = Agent(role="评审员", memory=ltm)

# 3. Crew 协调
crew = Crew(
    agents=[researcher, developer, reviewer],
    tasks=[task1, task2, task3],
    memory=ltm,                  # 共享同一 memory 实例
    process=Process.sequential,
)

# 4. A 调研的结果自动进 vector DB
#    B 编码时自动查询并使用
result = crew.kickoff()
```

---

## 七、5 大反模式深度补充

### 7.1 反模式 1：共享 = 传完整上下文（深度分析）

```python
# ❌ 反例：把完整 context 给每个 Agent
def share_context_to_all_agents(full_ctx):
    for agent in agents:
        agent.process(full_ctx)  # 100K tokens × 10 agents = 1M tokens
```

```python
# ✅ 正例：任务 ID + 关键参数 only
def share_context_to_all_agents(task_id):
    return {
        "task_id": task_id,
        "summary": shared_summarizer(task_id),  # 1K tokens
        "key_params": redis.hgetall(f"params:{task_id}")  # 100B
    }
```

### 7.2 反模式 2：读写竞争

```python
# ❌ 反例：所有 Agent 都读写同一 K-V
def update_progress(agent_id, task_id, p):
    redis.set(f"progress:{task_id}", p)  # 后写覆盖先写

# ✅ 正例：版本号 + CAS
def update_progress_v2(agent_id, task_id, p):
    # 协调者托管 + 乐观锁
    return redis.eval(cas_lua, ...)
```

### 7.3 反模式 3：没权限边界（多租户泄露）

```python
# ❌ 反例：所有 Agent 共享同一 RAG
results = vector_db.search(query)  # 看到所有租户的数据！

# ✅ 正例：filter 隔离
results = vector_db.search(query, filter={"tenant_id": tenant})
```

---

## 八、生产级 5 维度延迟矩阵

| 维度 | 典型延迟 | 实现 | 监控 |
|------|---------|------|------|
| 共享上下文 | < 10 ms | Redis Hash | P99 监控 |
| 共享事实知识 | 1-5 s | Vector DB + Kafka CDC | 写入吞吐 |
| 共享任务状态 | < 100 ms | Redis CAS | 乐观锁冲突率 |
| 共享技能 | < 5 s | K-V + publish | 注册数 / 版本 |
| Memory 4 层 | ms-s-min 分级 | 4 种存储 | 分层监控 |

---

## 九、决策树（实战选型）

```text
Q：你的多 Agent 任务是什么类型？
├─ 简单流水线（A → B → C）
│   └─ 协调者托管 + Redis 状态层（够用）
│
├─ 复杂协作（角色分工）
│   └─ 共享 Vector + 协调者（CrewAI 模式）
│
├─ 生产级强结构化
│   └─ LangGraph 状态机 + Checkpoint
│
└─ 跨语言 / 多团队
    └─ Memory Service 统一 API（多存储后端）
```

---

## 十、5 道反问快速参考

| Q | 高分答案 |
|---|---------|
| 共享哪种内容维度？延迟多少？| 5 大维度，按维度分级（ms / s / min）|
| 用什么共享模式？| 协调者托管 + 状态层 + 语义层组合 |
| 怎么处理数据竞争？| 版本号 + CAS / 乐观锁 |
| 怎么隔离权限？| RAG filter + agent_id 标签 |
| 5 维度延迟分别多少？| Working ms / Episodic s / Semantic s / Procedural min |

---

## 📚 相关章节

- [主模块 · Agent Memory 架构](README.md) — 316 行深度：单 Agent Memory 3 维度 + 5 反模式
- [主模块 · Multi-Agent 深度（第 2.3 节黑板模式）](../agent-execution-patterns/06-multi-agent-deep-dive.md#23-黑板模式blackboard--shared-state) — 5 行简述
- [兄弟题 · agent-memory-classification](../../../../13.split-hairs/11.ai/agent-memory-classification/README.md) — 单 Agent Memory 三维分类
- [兄弟题 · multi-agent-system-design](../../../../13.split-hairs/11.ai/multi-agent-system-design/README.md) — 5 大组件 + 死循环防护
- [主模块 · Agent Context 03-memory-strategies](../agent-context/03-memory-strategies.md) — 4 层协作机制

---

> 📅 2026-07-13 · 11.ai/04-architecture · ⭐⭐⭐⭐⭐ · 5 大维度 + 3 层 + 6 模式 + 5 一致性 + 6 实战框架

← [返回: AI 知识体系 · agent-memory](README.md)
