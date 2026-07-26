<!--
question:
  id: 11.ai-structured-output
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 工程实践
  tags: [11.ai, Structured Output, JSON Schema, Function Calling, Constrained Decoding]
-->

# Structured Output 面试题

> **一句话定位**：让 LLM 稳定输出合法 JSON 不是"prompt 里写一句'输出 JSON'"就够的——需要 **response_format + JSON Schema + Function Calling + 解析重试 + constrained decoding** 五层工程策略的组合。

> **同模块兄弟**：[Function Calling](../function-calling/) 讲工具调用原理；本文讲**结构化输出**的工程实现。

---

## 🎯 面试高频拷问

```text
Q：如何让 LLM 稳定输出 JSON？
Q：JSON Mode 和 Structured Outputs 有什么区别？
Q：为什么 JSON Mode 已经被淘汰了？
```

**回答框架（4 层递进）**：

1. **核心矛盾**：LLM 是概率模型，JSON 是确定性格式 → 需要外部约束
2. **5 层策略**：response_format → Function Calling → Prompt 指令 → 解析重试 → Constrained Decoding
3. **JSON Mode 过时**：2024-08 OpenAI 推出 Structured Outputs（100% Schema 合规），JSON Mode 不再推荐
4. **工程兜底**：不管用什么策略，必须有解析重试机制

---

## ⚠️ 陷阱 1：JSON Mode 已经过时

**错误**：还在用 `response_format={"type": "json_object"}`（JSON Mode）

**真相**：
- JSON Mode（2023-11 推出）：只保证输出合法 JSON，**不保证符合 Schema**
- Structured Outputs（2024-08 推出）：100% 符合 JSON Schema，**字段/类型/必填项全部保证**

**代价**：用 JSON Mode 仍需解析重试 + Schema 校验，Structured Outputs 直接省掉这些工程成本。

---

## ⚠️ 陷阱 2：只靠 prompt 约束

**错误**：在 prompt 里写"请严格按 JSON 格式输出"就完事

**真相**：成功率 ~90%，生产环境不够。常见问题：
- 漏了闭合括号
- 字段缺失（模型"觉得"不重要就省略）
- 类型错误（期望数字却输出字符串）
- 额外文本（JSON 外面包了 ```json``` 或"这是结果："）

**代价**：解析失败直接报错，用户体验崩塌。

---

## ⚠️ 陷阱 3：不做解析重试

**错误**：JSON 解析失败直接抛异常

**真相**：必须有兜底机制：
1. 尝试直接解析
2. 提取 ```json``` 代码块
3. 提取第一个 `{` 到最后一个 `}`
4. 让 LLM 修复格式（最多 3 次）

**代价**：一次格式错误就中断任务，Token 浪费。

---

## 💡 30 秒面试话术

> "让 LLM 稳定输出 JSON 需要 5 层工程策略：
> 
> **第一层**：response_format 参数（API 层面约束）。2024-08 OpenAI 推出 Structured Outputs，支持 JSON Schema，100% 合规。**JSON Mode 已过时**，因为它只保证合法 JSON，不保证符合 Schema。
> 
> **第二层**：Function Calling。把 JSON 格式伪装成'工具'，利用 FC 的 Schema 约束能力。
> 
> **第三层**：Prompt 指令 + 格式示例。灵活但不可靠（~90% 成功率）。
> 
> **第四层**：解析重试兜底。不管用什么策略，必须有 3 次重试机制：直接解析 → 提取代码块 → 提取 JSON 块 → 让 LLM 修复。
> 
> **第五层**：Constrained Decoding（自部署模型）。在推理层面强制每个 token 符合 Schema，100% 合法。
> 
> 框架选型：商业 API 用 Instructor（自动重试 + Pydantic 校验），自部署用 Outlines（Constrained Decoding）。"

---

## 📚 深度阅读

- [主模块深度文章](../../../11.ai/02-technology-stack/structured-output/README.md) — 5 种策略 + 框架对比 + 5 大反模式

---

← [返回: AI 咬文嚼字](../README.md)
