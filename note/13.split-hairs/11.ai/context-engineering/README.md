<!--
question:
  id: 11.ai-context-engineering
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [11.ai, Context, context]
-->

# Context Engineering — 4 大范式之二面试深挖

> 一句话定位：Context Engineering 是"在 Context Window 限制下，把对的信息在对的时间给 LLM"。完整概念见 [主模块 Context Engineering](../../../11.ai/02-technology-stack/context-engineering/README.md)。

---

## 引子：客服 AI 答非所问，加了 10 段文档还是不行

```text
你：我要做一个客服 AI，让它懂公司的全部产品文档
你：把 1000 页 PDF 全塞进 Prompt（一字不漏）
你：用户："充电宝怎么保修？"
AI：……生成了一段流畅但**和你的产品完全无关**的回答
```

**真相**：塞文档 ≠ Context Engineering。

Context 是 LLM 看到的**所有信息**：

```text
Context = System Prompt + 历史消息 + Tools Schema + RAG 文档 + 长期记忆 + 环境变量
```

塞 1000 页 PDF 进来：

- 注意力 O(n²) → **推理慢、成本爆**
- "Lost in the Middle"——**中间信息被忽略**
- 上下文窗口被塞满，**真正重要的信息被挤到角落**

Context Engineering 是：**在有限的 Context Window 里，把对的信息在对的时间塞给 LLM**。

## 一、Context 是什么（一图记全）

```
Context = System Prompt + 历史消息 + Tools Schema + RAG 文档 + 长期记忆 + 环境变量
```

**Context ≠ Prompt**：Prompt 是用户输入的一句话，Context 是 LLM 看到的**所有信息**。

---

## 二、面试陷阱

### 陷阱 1：以为 Context Engineering = Prompt Engineering
- **真相**：Prompt 是 Context 的子集。Context Engineering 包含 Prompt + Tools + Memory + RAG + History + Environment。

### 陷阱 2：以为 Context 越长越好
- **真相**：存在 **Lost in the Middle** 现象 —— 中间信息容易被忽略；Context 越长成本越高（O(n²) 注意力）、推理越慢。

### 陷阱 3：以为 RAG 能解决所有 Context 问题
- **真相**：RAG 只解决"知识新鲜度"，不能解决"任务规划"和"工具调用"。任务规划靠 Loop / ReAct，工具调用靠 Function Calling。

### 陷阱 4：以为 System Prompt 没用
- **真相**：System Prompt 是 Context 中权重最高的部分（开头 + 系统级），约束必须放这里。

---

## 三、反直觉点

- **"结构化 XML 标签"效果显著**：用 `<system>...</system>` 等标签切分，比纯文本段落召回率提升 20%+。
- **历史消息要"重置"而非"累积"**：长对话 Context 会爆炸，应定期压缩或滑动窗口。
- **Embedding 检索过滤历史消息**：而非保留所有历史。

---

## 四、4 大原则速记

1. **最小化**：只给当前需要的，不要塞整个代码库
2. **相关性**：Embedding 检索过滤无关内容
3. **时序**：最新放最前（System）或最后（User），中间易忽略
4. **引用**：RAG 检索必须带引用 ID，避免幻觉

---

## 五、30 秒面试话术

> Context Engineering 是 2026 年 AI 工程的核心范式，演进路径是 Prompt → Context → Harness → Loop。
>
> Context 不只是 Prompt，而是 LLM 看到的**所有信息**：系统提示 + 历史消息 + 工具定义 + RAG 检索结果 + 长期记忆 + 环境变量。
>
> 核心原则：最小化（只给当前需要的）、相关性（Embedding 检索过滤）、时序（最新放两端）、结构化（XML 标签）、引用（RAG 标注来源）。
>
> 关键挑战是 Context Window 限制和 "Lost in the Middle" 现象，所以需要 Agent 自动管理 Context，而不是人工写死。

---

## 六、深度阅读

- 主模块：[Context Engineering](../../../11.ai/02-technology-stack/context-engineering/README.md)
- 上一步：[Prompt Engineering](../prompt-engineering/README.md)
- 下一步：[Harness Engineering](../harness-engineering/README.md)
- 工具调用：[Function Calling](../function-calling/README.md)

---

> 📅 2026-06-30 · 咬文嚼字 · 2026 面试热点 · ⭐⭐⭐⭐