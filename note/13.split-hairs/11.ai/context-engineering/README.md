# Context Engineering：从 Prompt 到 Context 的范式转移

> 2026 年 AI 工程的核心范式：直接和大模型对话 → 让 Agent 帮你管理对话 → 让 Harness 帮你约束 Agent。本篇讲第二阶段：如何为 LLM 提供"恰到好处"的 Context。

## 一、核心结论（TL;DR）

| 阶段 | 关注点 | 主导者 |
|------|--------|--------|
| Prompt Engineering | 怎么写好一句提示 | 人类 |
| **Context Engineering** | 怎么给 LLM 提供完整的"上下文" | Agent |
| Harness Engineering | 怎么约束 Agent 行为 | 规范/流程 |
| Loop Engineering | 怎么循环调用 Agent 直到任务完成 | Agent + Harness |

> 一句话：**Context Engineering 的核心是"在 Context Window 限制下，把对的信息在对的时间给 LLM"**。

---

## 二、Context 是什么？

Context ≠ Prompt。Prompt 是用户输入的一句话，Context 是 LLM 看到的**所有信息**：

```
Context = 
  + 系统提示（System Prompt）
  + 用户消息历史（Conversation History）
  + 工具定义（Tools Schema）
  + 检索结果（RAG Documents）
  + 长期记忆（Memory）
  + 环境变量（Environment）
```

例如下面这个 Agent 看到的完整 Context：

```xml
<context>
  <system>
    你是餐厅订单助手，负责处理用户的订单查询。
    规则：1. 只能查询订单，不能修改；2. 返回格式 JSON；...
  </system>
  <tools>
    [getOrder, cancelOrder, refundOrder, queryUser]
  </tools>
  <history>
    User: 我要查询订单
    Assistant: 好的，请问订单号？
    User: 20260628001
  </history>
  <rag>
    [订单状态说明文档, 退款政策文档]
  </rag>
  <memory>
    用户偏好：使用中文，简洁风格
    之前对话：用户是 VIP 客户
  </memory>
  <environment>
    当前时间：2026-06-28 10:30
    用户 ID: user_123
  </environment>
</context>
```

---

## 三、Context Window 的限制

### 1. 长度限制

| 模型 | Context Window |
|------|----------------|
| GPT-3.5 | 4K tokens |
| GPT-4 | 8K / 32K tokens |
| GPT-4 Turbo | 128K tokens |
| Claude 3 | 200K tokens |
| Claude 4 | 1M tokens |
| Gemini 1.5 Pro | 1M-2M tokens |

### 2. "Lost in the Middle" 现象

LLM 对 Context **开头和结尾的信息记忆最准确**，**中间的信息容易被忽略**：

```
[最准确] 系统提示 → 历史最早 → ... → 历史最近 → 当前问题 [最准确]
              ← 容易被忽略 →
```

### 3. Context 越长，成本越高

- 输入 token 计费
- 推理时间与 Context 长度正相关
- 注意力机制复杂度 O(n²)

---

## 四、Context Engineering 的核心原则

### 1. 最小化原则（Minimum Context）

```python
# ❌ 把整个代码库塞进 Context
context = read_entire_codebase()  # 100K tokens

# ✅ 只给 LLM 当前需要的代码
context = get_relevant_files(query)  # 5K tokens
```

### 2. 相关性原则（Relevance）

- 用 Embedding 检索最相关的文档
- 过滤无关的历史消息
- 工具定义只暴露当前需要的

### 3. 时序原则（Recency）

- 最新的信息放最前面（System Prompt）或最后面（User Message）
- 旧的历史消息可以压缩或丢弃

### 4. 结构化原则（Structure）

```xml
<context>
  <system>...</system>
  <memory>...</memory>
  <tools>...</tools>
  <history>...</history>
  <current_task>...</current_task>
</context>
```

### 5. 引用原则（Citation）

- RAG 检索的文档要带引用 ID
- Agent 回答时要标注信息来源（避免幻觉）

---

## 五、Context Engineering vs Prompt Engineering

| 维度 | Prompt Engineering | Context Engineering |
|------|-------------------|-------------------|
| 范围 | 单条提示 | 完整上下文 |
| 主体 | 人类写 Prompt | Agent 自动管理 Context |
| 关注 | "怎么问" | "给什么信息" |
| 工具 | Prompt 模板 | Context 编排框架 |
| 评估 | 输出质量 | 上下文利用效率 |

**演进路径**：Prompt → Context → Harness → Loop

---

## 六、实战工具与框架

| 工具 | 用途 |
|------|------|
| LangChain | Context 编排框架 |
| LlamaIndex | RAG + Context 管理 |
| MemGPT | 长期记忆管理 |
| Cursor | IDE 级 Context（项目代码 + 文件 + 终端） |
| Claude Code | Agent 级 Context（代码 + 历史 + 工具） |

---

## 七、面试陷阱

### 陷阱 1：以为 Context Engineering = Prompt Engineering

- **真相**：Prompt 是 Context 的一部分，Context Engineering 包含 Prompt + Tools + Memory + RAG

### 陷阱 2：以为 Context 越长越好

- **真相**：Lost in the Middle 现象 + 成本 + 推理速度都制约 Context 长度

### 陷阱 3：以为 RAG 能解决所有 Context 问题

- **真相**：RAG 只解决"知识新鲜度"，不能解决"任务规划"和"工具调用"

---

## 八、面试话术模板

> Context Engineering 是 2026 年 AI 工程的核心范式之一，演进路径是 Prompt → Context → Harness → Loop。
>
> Context 不只是 Prompt，而是 LLM 看到的**所有信息**：系统提示 + 历史消息 + 工具定义 + RAG 检索结果 + 长期记忆 + 环境变量。
>
> 核心原则：最小化（只给当前需要的）、相关性（Embedding 检索过滤）、时序（最新放两端）、结构化（XML 标签）、引用（RAG 标注来源）。
>
> 关键挑战是 Context Window 限制和 "Lost in the Middle" 现象，所以需要 Agent 自动管理 Context，而不是人工写死。

---

## 九、相关章节

- 同栏目：[`prompt-engineering`](../prompt-engineering/README.md) — Prompt Engineering 基础
- 同栏目：[`harness-engineering`](../harness-engineering/README.md) — Harness Engineering
- 同栏目：[`loop-engineering`](../loop-engineering/README.md) — Loop Engineering
- 同栏目：[`agent-dag-vs-react`](../agent-dag-vs-react/README.md) — DAG vs ReAct
- 主模块：[`11.ai/02-technology-stack`](../../../../11.ai/02-technology-stack/README.md) — AI 技术栈

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（2026 面试热点）