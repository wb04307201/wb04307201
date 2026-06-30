# Function Calling / Tool Use — Agent 核心机制面试深挖

> 一句话定位：Function Calling 是让 LLM 输出结构化 JSON 来声明要调用的工具（而非直接执行），是 AI Agent 的核心机制。完整概念见 [主模块 Function Calling](../../../11.ai/02-technology-stack/function-calling/README.md)。

---

## 引子：让 AI 帮你订外卖，它怎么"下单"？

```text
你（对 AI）："帮我在美团上订一份黄焖鸡米饭，不要辣，送到公司。"

AI 脑子里转一圈：
1. 我得知道你想点哪一家
2. 我得知道送到哪里
3. 我得能调美团 API 下单
4. 我得把订单结果告诉你
```

**但 LLM 本身没有任何执行能力**——它只能"说话"，不能"下单"。

Function Calling 是答案：

```text
你     →  LLM（输出 JSON："调用 query_shop，传黄焖鸡米饭"）
LLM    →  宿主程序（执行 query_shop API）
宿主    →  LLM（回传 shop 数据："找到 3 家"）
LLM    →  宿主（选第一家："调用 create_order"）
宿主    →  用户（"已下单"）
```

**Function Calling = 让 LLM 通过 JSON 告诉宿主程序"该调哪个工具、传什么参数"**。
这是 AI Agent 的核心机制。

## 一、核心流程（一图记全）

```
用户请求 → LLM 分析意图 → 输出 tool_calls(JSON)
                                    ↓
                          宿主程序解析并执行
                                    ↓
                          结果以 role:tool 回传 LLM
                                    ↓
                          LLM 生成最终回答
```

**关键认知**：LLM 本身**没有执行能力**，它只是"知道"工具和参数格式，输出 JSON 调用描述，真正执行在模型之外。

---

## 二、面试陷阱

### 陷阱 1：以为 LLM 能"执行"工具
- **真相**：LLM 只是声明 `tool_calls`，执行由宿主程序完成；LLM 不能直接访问 API / 数据库 / 文件系统。

### 陷阱 2：以为 Function Calling 是 OpenAI 独有
- **真相**：OpenAI 2023 年 6 月首推，Anthropic Claude 3 也支持（用 `tool_use` block + `tool_result`），协议不同但本质一致。

### 陷阱 3：以为并行调用 OpenAI 才有
- **真相**：Claude 也支持并行调用（content 数组包含多个 tool_use block），OpenAI 用 `tool_calls` 数组实现。

### 陷阱 4：不设 `max_turns` 导致无限循环
- **真相**：必须设上限（建议 3-5）+ 去重检测 + 工具结果缓存，否则工具描述不清晰时 Agent 死循环。

---

## 三、OpenAI vs Claude 协议差异

| 维度 | OpenAI | Claude |
|------|--------|--------|
| 工具调用结构 | `tool_calls` 字段嵌入 assistant | `content` 数组中 `type: tool_use` block |
| 结果角色 | 独立 `role: "tool"` 消息 | `role: "user"` 消息中 `type: tool_result` |
| 工具 schema | `parameters` | `input_schema` |

---

## 四、5 大安全陷阱

| 风险 | 缓解措施 |
|------|----------|
| **工具权限过大** | 最小权限原则：只读账户、限流、白名单 |
| **代码注入** | 沙箱执行、禁用危险模块、静态分析 |
| **敏感数据泄露** | 工具结果脱敏、审计日志、访问控制 |
| **SSRF** | 禁止访问内网地址、DNS 重绑定防护 |
| **循环调用** | `max_turns=3-5` + 去重 + 缓存 |

---

## 五、反直觉点

- **RAG 本质是一个工具**：`search_knowledge_base(query, top_k)` 就是个 retrieve 工具，Agent 决定何时检索。
- **Agent = LLM + Tools + Planning + Memory**：Function Calling 是 Agent 的"手"，缺它 Agent 只能"说"不能"做"。
- **tool_choice 4 种模式**：`auto`（模型自决）/ `required`（必须调）/ `none`（禁调）/ 强制指定工具。

---

## 六、30 秒面试话术

> Function Calling 是让 LLM 输出结构化 JSON 来声明要调用的工具，而不是直接执行。流程是：用户提问 → 模型根据 tools 定义输出 tool_calls → 宿主程序解析 JSON 并实际执行 → 把结果以 role: tool 的消息回传 → 模型基于结果生成最终回答。
>
> 关键点有三：第一，LLM 本身不执行任何操作，只是做意图识别和参数提取；第二，多轮编排需要设置 max_turns 防止循环调用；第三，工具描述要精确，参数要用 JSON Schema 严格定义，执行要有超时和错误处理。
>
> RAG 本质上是一个 retrieval tool，Agent 则是 LLM + Tools + Planning + Memory 的组合体。

---

## 七、深度阅读

- 主模块：[Function Calling](../../../11.ai/02-technology-stack/function-calling/README.md)
- 关联：[Agent 架构](../agent-dag-vs-react/README.md)
- 关联：[RAG](../rag/README.md) — RAG 即 retrieve 工具
- 实战：[Loop Engineering](../loop-engineering/README.md) — 多轮编排的兜底

---

> 📅 2026-06-30 · 咬文嚼字 · Agent 核心机制 · ⭐⭐⭐⭐⭐