<!--
question:
  id: 11.ai-function-calling
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 反直觉代码
  tags: [11.ai, Function Calling, function, tencent, aliyun, bytedance, tool-use, 一面高频]
-->

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

---

## 七、腾讯 / 字节 / 阿里一面实战（90 秒评分话术）

> 本节针对腾讯一面高频题"什么是 Function Calling？原理是什么？"补充 **90 秒完整评分答案**。前一节"30 秒话术"是骨架版（5 大要点速记），本节是满分展开版（4 层递进 + 5 反模式 + 完整代码示例）。

### 题目 A：什么是 Function Calling？原理是什么？（腾讯一面标准题）

**满分回答模板（4 层递进，60-90 秒）**：

```
1. 【一句话定义 · 10 秒】
"Function Calling 是让 LLM 输出结构化 JSON 来声明要调用的工具，
不是让模型直接执行代码 —— LLM 没有执行能力。"

2. 【4 阶段核心流程 · 30 秒】
"流程分 4 步：
① 用户提问 + 工具定义（tools 数组，JSON Schema）→ LLM
② LLM 分析意图，返回 tool_calls（结构化 JSON，含 tool name + args）
③ 宿主程序解析 JSON → 实际调用工具 → 拿到结果
④ 结果以 role: tool 的消息回传 LLM → LLM 基于结果生成最终回答

关键约束：LLM 只'声明'，不'执行'；host 负责执行 + 回传。"

3. 【关键设计 5 原则 · 30 秒】
"5 大设计原则：
① 安全：LLM 只能调预注册的工具，不能执行任意代码
② Schema 严格：用 JSON Schema 定义工具的参数和类型
③ Host 控制：执行由 host 程序完成，包括超时 + 重试 + 权限校验
④ Message 协议：tool 角色消息（OpenAI）/ content blocks（Claude）
⑤ 多轮编排：用 max_turns / Token budget 防止无限循环"

4. 【反模式与扩展 · 20 秒】
"3 大反模式：
- 工具描述含糊 → 模型参数错误
- 缺少 max_turns → 无限循环
- 并行调用未启用 → 延迟翻倍

扩展：RAG 本质是 retrieve tool；Agent = LLM + Tools + Planning + Memory。"
```

### 评分要点（面试官视角）

| 维度 | 5 分（初级）| 8 分（中级）| 10 分（满分）|
|------|----------|----------|----------|
| **定义清晰度** | 知道"调外部工具" | 能说清"LLM 输出 JSON 声明" | 能说清"LLM 不执行，只声明" |
| **流程完整度** | 只说 1-2 步 | 能说 4 步 | 能画"用户 → LLM → host → LLM → 用户"图 |
| **设计原则** | 不知道怎么设计 | 提 Schema / 权限 | 5 大原则全覆盖 |
| **安全意识** | 不知道 | 提到权限 | 能说 token 沙箱 / 限速 |
| **反模式** | 不提 | 提 1 个 | 提 3 个+ 实战 |

**面试官潜规则**：
- 90% 候选人能答到"定义"+"流程"
- 85% 答不到"LLM 不执行"
- 50% 答不到"5 大设计原则"
- 10% 答不到"max_turns 防循环"
- **加分项**：能主动提"并发调用" / "tool_choice 参数" / "实战反模式"

### 题目 B：Function Calling 和 Tool Use 是一回事吗？

**高分答案**（45 秒）：

```
"本质相同，都是 LLM 输出结构化工具调用请求。

但术语有差异：
- Function Calling：OpenAI 起的名字（2023-06）
- Tool Use：Anthropic Claude 起的名字
- 同一机制，不同 API 名字

技术上有 3 个关键差异：
1. Schema 定义方式：OpenAI 用 tools JSON 数组 + JSON Schema；Anthropic 用 tool_config + input_schema
2. 多模态返回：Claude 支持 image / PDF 作为 tool 返回；OpenAI 主要文本
3. 并行调用：两者都支持，但调用格式略有差异

反模式：当成两套机制 —— 实际是同一种思想的两种 API 命名。"
```

### 题目 C：Function Calling 的并发怎么实现？性能如何？

**高分答案**（45 秒）：

```
"Function Calling 支持并行——模型一次性输出多个 tool_calls，然后
host 程序并发执行（asyncio.gather / Promise.all）。

性能对比：
- 串行：3 个工具各 500ms → 总 1500ms
- 并行：3 个工具各 500ms → 总 500ms（3x 提升）

实战配置：
- OpenAI：tool_calls 数组中多个对象，host 用 asyncio.gather 并发执行
- Claude：同样支持，content blocks 多 tool_use

反模式：
- 默认串行执行（错失 3x 性能）
- 并发时没有隔离（一个失败影响全部）

实战 80% 场景可并发，特别是查询类工具（搜索多数据库 / 查订单详情）。"
```

### 题目 D：Function Calling 如何防止 prompt injection？

**高分答案**（40 秒）：

```
"Function Calling 本身有 3 层防护：
1. 结构化输出：模型只能生成 JSON，不是自然语言，无法'绕过'
2. Schema 验证：host 用 JSON Schema 严格校验参数
3. host 控制：实际执行由 host 完成，host 可加白名单 / 限速 / 审计

但仍有 3 大风险：
1. 间接 prompt injection：工具返回被污染（如搜索结果包含恶意指令）
2. 模型幻觉：模型可能错选工具或错传参数
3. Token 沙箱绕过：恶意参数可能引发异常

实战防御：
- 工具返回使用边界符（如 <tool_result>...</tool_result>）
- 不让工具返回参与系统提示（只作为 user/tool 消息）
- 参数白名单 / 长度限制 / 类型严格校验"
```

### 题目 E：Function Calling 和 MCP（Model Context Protocol）是什么关系？

**高分答案**（40 秒）：

```
"Function Calling 是 LLM 输出'调什么工具'的机制。
MCP 是 Anthropic 2024-11 提出的协议：标准化 LLM 与工具 / 数据源的连接。

关系：
- Function Calling：解决'LLM 怎么声明调用'（模型层）
- MCP：解决'工具怎么被发现 / 注册 / 描述'（传输层）

类比：
- Function Calling ≈ HTTP（请求格式）
- MCP ≈ OpenAPI（服务发现 + 文档）

2025 趋势：MCP 标准化让工具可跨模型（OpenAI / Claude / Qwen）复用，
类似 LSP（Language Server Protocol）统一 IDE 语言后端。"
```

### 4 大反模式（实战踩过的雷）

#### ⚠️ 反模式 1：工具描述含糊

```javascript
// 错：模型看不懂
{ name: "search", description: "搜索东西" }

// 对：精确描述参数 + 返回
{
  name: "search_orders",
  description: "查询用户订单列表。返回 JSON: [{order_id, status, amount}]",
  parameters: {
    type: "object",
    properties: {
      user_id: { type: "string", description: "用户 ID" },
      status: { type: "string", enum: ["pending", "paid", "shipped"] }
    },
    required: ["user_id"]
  }
}
```

#### ⚠️ 反模式 2：缺少 max_turns

```python
# 错：Agent 死循环
for tool_call in llm.tool_calls:
    result = execute(tool_call)
    response = llm.send(result)  # 可能再调 100 次

# 对：max_turns 上限
for i in range(max_turns=10):
    response = llm.send()
    if not response.tool_calls:
        break
```

#### ⚠️ 反模式 3：并发调用未启用

```python
# 错：串行
results = [execute(call) for call in tool_calls]  # 总耗时 = sum

# 对：异步并发
results = await asyncio.gather(*[execute(call) for call in tool_calls])  # 总耗时 = max
```

#### ⚠️ 反模式 4：工具权限过宽

```python
# 错：模型能调任意 shell
{ name: "execute_command", parameters: { cmd: "string" } }

# 对：白名单 + 输入验证
{ 
  name: "execute_safe_command",
  parameters: { cmd: "string", allowed_values: ["status", "logs"] }
}
```

### 5 大安全防护（生产必做）

```python
# 1. 输入验证（防注入）
def safe_invoke(tool_name, args):
    schema = TOOLS_REGISTRY[tool_name]
    validate(args, schema)  # JSON Schema 校验
    # 参数白名单 / 长度限制
    
# 2. 超时 + 重试
result = execute_with_timeout(tool_call, timeout=5s)

# 3. 限速（防滥用）
rate_limiter.check(user_id, tool_name)

# 4. 审计日志
log_tool_call(tool_name, args, result, user_id)

# 5. 错误隔离
try:
    result = execute(tool_call)
except Exception:
    result = {"error": str(e)}  # 不暴露 stack 给 LLM
```

### 实战配置（OpenAI 2026 + Spring AI Alibaba）

```python
# OpenAI 2026 推荐配置（GPT-4o-mini）
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_orders",
            "description": "查询用户订单",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "date_range": {"type": "string", "format": "date"}
                }
            }
        }
    }
]

# tool_choice 配置
tool_choice = "auto"  # 让模型自决
# 强制调用某工具：tool_choice = {"type": "function", "function": {"name": "query_orders"}}
```

### 跨模型协议对比（实战速查）

| 维度 | OpenAI Tools | Claude Tool Use | Google Function Calling |
|------|-------------|-----------------|-------------------------|
| **Schema** | tools 数组 | tools 数组 | tools 数组 |
| **并发** | ✅ tool_calls 数组 | ✅ content blocks | ✅ parallelCalls |
| **强制调用** | tool_choice | tool_choice | 不支持直接强制 |
| **多模态返回** | ❌ 主要是文本 | ✅ image/PDF | ❌ |
| **多轮编排** | manually | manually | manually |

### 一句话总结（腾讯一面满分版）

> **Function Calling 是让 LLM 通过结构化 JSON 声明工具调用（不是执行），4 阶段流程：用户→LLM→host→LLM→用户；5 原则：安全/Schema/Host 控制/消息协议/max_turns 防循环；3 反模式：描述含糊/无 max_turns/串行调用。腾讯 / 字节 / 阿里一面必问。**

← [返回: 咬文嚼字 · function-calling](../README.md)
