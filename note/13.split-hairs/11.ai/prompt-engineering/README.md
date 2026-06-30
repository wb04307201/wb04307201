<!--
question:
  id: 11.ai-prompt-engineering
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 反直觉代码
  tags: [11.ai, Prompt, prompt]
-->

# Prompt Engineering — 8 种核心技巧面试深挖

> 一句话定位：Prompt Engineering 是"通过精心设计提示词，让 LLM 输出更符合需求"的范式。完整概念见 [主模块 Prompt Engineering](../../../11.ai/02-technology-stack/prompt-engineering/README.md)。

---

## 引子：同样的 Prompt，今天 90% 准确，明天 50%

```text
周一：你精心写了一段 Prompt："请用一句话总结用户评论情绪，归为 positive/negative/neutral 三类。"
模型调用：1000 次，**准确率 92%**。老板很满意。

周三：同一个 Prompt，再跑 1000 次。
准确率：**61%**。
```

**为什么变了？**

**真相 1**：LLM 输出是**概率采样**的，温度一样也有波动。
**真相 2**：上下文 window 满了，模型会"忘"前面的指令。
**真相 3**：用户输入越来越脏（"我也不知道这是什么"、"额这个"），少样本示例不够。

**Prompt 工程的本质**：用 Few-shot 示例 + 角色定义 + 输出格式约束 + 边界检查，
让模型输出"在概率分布里最稳的那个"。不是"魔法咒语"，是**工程问题**。

## 一、8 种核心技巧速记

| # | 技巧 | 一句话 |
|---|------|--------|
| 1 | Zero-shot | 直接问，不给示例 |
| 2 | Few-shot | 给 3-5 个示例学模式 |
| 3 | CoT 思维链 | "一步步思考"触发推理 |
| 4 | System Prompt | 定义角色 + 行为 + 约束 |
| 5 | 结构化输出 | 强制 JSON / Markdown / XML |
| 6 | 角色设定 | "你是 10 年经验的 SRE" |
| 7 | 约束与边界 | 明确长度、语言、风格 |
| 8 | Prompt Chaining | 复杂任务拆多步执行 |

**高级**：ReAct（Reason+Act）、Self-Consistency（多次采样投票）、Tree of Thoughts（多路径探索）。

---

## 二、面试陷阱

### 陷阱 1：以为 Prompt Engineering = 写一句好提示
- **真相**：8 种技巧是体系，System Prompt / Few-shot / CoT 缺一不可；Prompt 是 Context 的子集。

### 陷阱 2：以为 CoT 总是有效
- **真相**：CoT 对推理题有效，对简单事实查询反而增加 token 消耗且无收益。

### 陷阱 3：忽视 Prompt 注入风险
- **真相**：用户输入里嵌入"忽略之前指令"就能劫持 LLM，必须用分隔符 + 明确指令 + 输出过滤。

### 陷阱 4：以为 Few-shot 越多越好
- **真相**：3-5 个示例足够，多了占 context window；示例要覆盖边界情况。

---

## 三、反直觉点

- **"更短的 Prompt" ≠ 更好**：精确 + 具体比短更重要，长 Prompt 反而效果更好。
- **System Prompt 不是装饰**：模型对 System Prompt 的遵循度高于 User Prompt，约束要写在 System。
- **中文 Prompt 不一定输给英文**：Claude / GPT-4 中文能力已对齐英文，但技术术语建议保留英文。

---

## 四、30 秒面试话术

> Prompt Engineering 是通过精心设计的提示词，让 LLM 输出更符合需求。8 种核心技巧：Zero-shot 直接问；Few-shot 给示例；CoT 思维链加"一步步思考"；System Prompt 定义角色行为约束；结构化输出强制 JSON；角色设定增强语气；约束边界明确不要做什么；Prompt Chaining 拆多步。防御 Prompt 注入用分隔符包裹用户输入 + 明确"不执行用户指令" + 输出过滤。2026 趋势是 Function Calling 结构化输出成标配，RAG + Prompt 是主流应用。

---

## 五、深度阅读

- 主模块：[Prompt Engineering](../../../11.ai/02-technology-stack/prompt-engineering/README.md)
- 演进下一步：[Context Engineering](../../../11.ai/02-technology-stack/context-engineering/README.md)
- 关联：[RAG](../../../11.ai/07-llmops/01-rag-vs-finetuning/README.md)
- 故事版：[12.story #42 Prompt 工程](../../../12.story/42-prompt-engineering.md)

---

> 📅 2026-06-30 · 咬文嚼字 · 面试高频 · ⭐⭐⭐⭐⭐