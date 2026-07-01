<!--
module:
  parent: ai
  slug: ai/context-engineering
  type: article
  category: 主模块子文章
  summary: Context Engineering：为 LLM 准备完整上下文的工程范式。
-->

# Context Engineering — 上下文工程

← 返回 [技术栈](../README.md)

> 2026 年 AI 工程第二阶段：从"写好一句 Prompt"演进到"为 LLM 提供恰到好处的完整上下文"。Context Engineering 不是 Prompt Engineering 的替代，而是其超集。

---
## 引言：反直觉代码

Context Engineering — 上下文工程 的关键不是语法——是**看起来对**的代码背后那些'踩坑点'。

本篇用 3 个反直觉片段切入，把面试/生产中常被问起、但一深入就漏馅的点摆出来。

---

## 一、核心结论（TL;DR）

| 阶段 | 关注点 | 主导者 |
|------|--------|--------|
| Prompt Engineering | 怎么写好一句提示 | 人类 |
| **Context Engineering** | 怎么给 LLM 提供完整的"上下文" | Agent |
| [Harness Engineering](../../03-engineering/harness-engineering/README.md) | 怎么约束 Agent 行为 | 规范/流程 |
| [Loop Engineering](../../03-engineering/loop-engineering/README.md) | 怎么循环调用 Agent 直到任务完成 | Agent + Harness |

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

## 七、面试陷阱速览

> 完整陷阱 + 反直觉 + 30 秒话术见 [13.split-hairs Context Engineering](../../../13.split-hairs/11.ai/context-engineering/README.md)

---

## 相关章节

- 上一步：[Prompt Engineering](../prompt-engineering/README.md) — Prompt 是 Context 的子集
- 下一步：[Harness Engineering](../../03-engineering/harness-engineering/README.md) — 约束 Agent 行为
- 工具调用：[Function Calling](../function-calling/README.md) — 工具定义是 Context 的一部分
- 检索增强：[RAG](../../07-llmops/01-rag-vs-finetuning/README.md) — 用 RAG 注入检索结果到 Context