<!--
module:
  parent: ai
  slug: ai/function-calling
  type: article
  category: 主模块子文章
  summary: Function Calling / Tool Use：工具调用原理 + Schema 定义 + ReAct Agent。
-->

# Function Calling / Tool Use

← 返回 [技术栈](../README.md)

> LLM 本身不能执行代码、不能上网。通过 **Function Calling**，模型"声明"要调用的工具，由外部宿主程序执行后回传结果，让 LLM 继续推理 —— 这是 AI Agent 的核心机制。

---
---

## 一、核心原理

Function Calling 的本质不是让 LLM 直接执行代码，而是让模型**输出结构化的工具调用请求**。流程分为四个阶段：

```text
用户请求 → LLM 分析意图 → 输出 tool_calls(JSON) → 外部执行器解析并执行 → 结果回传 LLM → LLM 生成最终回答
```

**关键认知**：LLM 本身没有执行能力，它只是"知道"某个工具的存在和参数格式，然后按照约定格式输出调用描述。真正的执行发生在模型之外，由宿主程序完成。

这种设计带来了三个核心优势：

1. **安全性**：模型不能随意执行任意代码，只能调用预注册的工具集合
2. **可控性**：开发者可以精确控制每个工具的权限、超时、重试策略
3. **可观测性**：每次工具调用都是显式的 JSON 结构，便于日志记录和调试

**技术栈分层**：

| 层级 | 职责 | 示例 |
|------|------|------|
| Model Layer | 理解意图，输出 tool_calls | GPT-4, Claude 3, Qwen |
| Protocol Layer | 定义工具描述格式和消息协议 | OpenAI Tools API, Anthropic Tool Use |
| Execution Layer | 解析 JSON，实际调用工具，返回结果 | 宿主程序的 router/handler |
| Orchestration Layer | 管理多轮对话、循环限制、错误恢复 | LangChain, LlamaIndex, AutoGen |

---

## 二、OpenAI Function Calling

OpenAI 在 2023 年 6 月引入 Function Calling，2024 年演进为更通用的 Tool Use API。

### tools 定义结构

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气状况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
                },
                "required": ["city"]
            }
        }
    }
]
```

### 完整调用流程

```python
import openai, json

client = openai.OpenAI()
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]

response = client.chat.completions.create(
    model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
)

if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        args = json.loads(tc.function.arguments)
        result = get_weather(city=args["city"], unit=args.get("unit", "celsius"))
        messages.append(response.choices[0].message)
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})

    final = client.chat.completions.create(model="gpt-4o", messages=messages, tools=tools)
    print(final.choices[0].message.content)
```

### tool_choice 四种模式

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| `auto` | 模型自行判断 | 通用对话，工具可选 |
| `required` | 必须调用至少一个工具 | 严格任务型场景 |
| `none` | 禁止调用任何工具 | 纯聊天模式 |
| `{"type": "function", "function": {"name": "xxx"}}` | 强制调用指定工具 | 路由场景 |

### Parallel Tool Calls

GPT-4 支持单次响应返回多个 tool_calls，适用于独立查询的并行执行：

```json
{
    "tool_calls": [
        {"id": "call_1", "function": {"name": "get_weather", "arguments": '{"city": "北京"}'}},
        {"id": "call_2", "function": {"name": "get_weather", "arguments": '{"city": "上海"}'}}
    ]
}
```

宿主程序应当并行执行（如使用 `asyncio.gather`），然后将结果分别以 `role: tool` 回传。

---

## 三、Claude Tool Use

Anthropic 在 Claude 3 系列中引入 Tool Use，设计与 OpenAI 有显著差异。

### 核心差异对比

| 维度 | OpenAI | Claude |
|------|--------|--------|
| 消息结构 | `tool_calls` 字段嵌入 assistant 消息 | `content` 数组中包含 `type: tool_use` block |
| 结果角色 | 独立的 `role: "tool"` 消息 | `role: "user"` 消息中包含 `type: tool_result` block |
| 并行调用 | 原生支持，单次响应返回多个 | 支持，content 数组包含多个 tool_use block |
| 工具定义 | `tools` 数组在请求顶层 | `tools` 数组在请求顶层，用 `input_schema` |

### Claude Tool Use 定义与消息结构

```python
tools = [{
    "name": "get_weather",
    "description": "获取指定城市的天气信息",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}, "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}},
        "required": ["city"]
    }
}]

# 模型返回 tool_use
{"role": "assistant", "content": [
    {"type": "text", "text": "我来查询北京的天气。"},
    {"type": "tool_use", "id": "toolu_abc123", "name": "get_weather", "input": {"city": "北京"}}
]}

# 回传工具结果（注意：role 是 user）
{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "toolu_abc123", "content": "北京: 晴, 25°C"}
]}
```

### Claude 完整流程

```python
import anthropic

client = anthropic.Anthropic()
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]

response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages, tools=tools)

for block in response.content:
    if block.type == "tool_use":
        result = get_weather(**block.input)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": block.id, "content": str(result)}]})
        final = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1024, messages=messages, tools=tools)
        print(final.content[0].text)
```

---

## 四、多轮编排

Function Calling 的核心是多轮对话编排：模型调用工具 → 执行工具 → 结果回传 → 模型继续推理。

### 标准编排循环

```python
def run_agent(messages, tools, max_turns=5):
    for turn in range(max_turns):
        response = call_llm(messages, tools)
        tool_calls = extract_tool_calls(response)
        if not tool_calls:
            return response.content  # 模型给出最终回答

        for tc in tool_calls:
            try:
                result = execute_tool(tc)
            except Exception as e:
                result = f"工具执行失败: {str(e)}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})

    raise RuntimeError(f"超过最大工具调用次数 ({max_turns})")
```

### 循环调用问题与防御

当工具描述不清晰或模型推理出错时，可能出现无限循环。防御策略：

1. **设置 max_turns 上限**：通常 3-5 次足够
2. **去重检测**：检查最近 N 轮是否有相同的工具调用
3. **工具结果缓存**：相同参数的调用直接返回缓存
4. **明确的停止信号**：要求模型获得足够信息后输出最终回答

### 4.1 为什么 1 次 Tool Calling 已经不够？（5 大场景 + 6 大编排模式）

> 面试速查版见 [13.split-hairs · multi-turn-tool-reasoning](../../../13.split-hairs/11.ai/multi-turn-tool-reasoning/README.md)。

**核心区别**：

```text
1 轮：query → LLM → tool_calls → execute → final answer
                                  ↑
                            1 个意图

多轮：循环 N 次，每次回灌工具结果到 messages：
  query_1 → LLM_1 → tool_calls_1 → execute_1 → 回灌
                                              ↓
                                          LLM_2（基于结果再推理）→ tool_calls_2 → ...
                                              ...
                                          直到 LLM 输出 final answer
```

#### 5 大场景速查（1 turn 解决不了）

| # | 场景 | 例子 | 为什么需要多轮 |
|---|------|------|---------------|
| 1 | **多源信息聚合** | 订外卖 → 查店铺 + 位置 + 配送时间 | 多 query 结果拼装 |
| 2 | **复合操作依赖** | 写文章 → 搜索资料 → 大纲 → 填充 | 后一步依赖前一步 |
| 3 | **错误恢复** | API 失败 → 改参数 / 换工具 | 失败需要 LLM 决策下一步 |
| 4 | **探索性任务** | 查到关键未知字段 → 再深入 | 路径是动态发现 |
| 5 | **长链路审批** | 金融转账 / 多步授权 | 多工具结果需中间决策 |

#### 6 大编排模式选型

| # | 模式 | 核心思想 | 代表框架 | 适用 |
|---|------|---------|---------|------|
| 1 | **Sequential 串行** | 一个接一个 | LangChain AgentExecutor | 简单链式 |
| 2 | **Parallel 并行** | 独立工具同调 | RunnableMap | 多源聚合 |
| 3 | **ReAct loop** | 思考→行动→观察→循环 | BabyAGI / AutoGPT | 探索性 |
| 4 | **Plan-and-Execute** | 先规划 + 失败 RePlan | LangChain P&E / Devin | 5-20 步强依赖 |
| 5 | **Reflective** | 工具结果 + 自检 + 纠错 | ReAct + Reflection | 高准确度要求 |
| 6 | **DAG Workflow** | 节点 + 边的确定性图 | LangGraph / Temporal | 强结构化生产 |

#### 6 维度编排模式选型矩阵

| 维度 | Sequential | Parallel | ReAct | Plan-Exec | Reflective | DAG |
|------|-----------|---------|-------|-----------|-----------|-----|
| **步数** | 1-3 | 1 (并行) | 不定 | 5-20 | 不定 | 不定 |
| **依赖** | 强依赖 | 无依赖 | 弱依赖 | 强依赖 | 弱依赖 | 强依赖 |
| **预测性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Token 成本** | 低 | 低 | 高（探索多） | 中 | 高（自检） | 中 |
| **可复现** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **实现复杂度** | 低 | 低 | 中 | 中 | 高 | 高 |

#### 5 类 Fallback 实战（max_turns 用尽时）

```python
def fallback_chain(query, attempts=3):
    # 1. 重试参数（仅改参数）
    for _ in range(attempts):
        try:
            return execute(query)
        except (TimeoutError, RateLimitError):
            sleep(2 ** _)

    # 2. 换工具（语义最接近的备用）
    try:
        return execute_with_alternate(query)
    except Exception:
        pass

    # 3. 退化到更小的模型
    try:
        return invoke_small_model(query)
    except Exception:
        pass

    # 4. 兜底回复
    return "暂不可用，请稍后重试"

    # 5. 人工接管（生产关键决策，金融/医疗/法律）
    # escalate_to_human(query, results_so_far)
```

#### 3 大 OSS 框架对比

| 维度 | LangChain | AutoGen | LangGraph |
|------|-----------|---------|-----------|
| **多轮机制** | AgentExecutor ReAct loop | GroupChat message passing | StateGraph 状态机 + DAG |
| **易用度** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **强结构化** | 中 | 弱 | ⭐⭐⭐⭐⭐ |
| **代表用户** | LangChain / Anthropic | Microsoft AutoGen | LangChain / LangGraph |

---

## 五、实战场景

### 场景 1：天气查询（基础工具调用）

```python
@tool
def get_weather(city: str, unit: str = "celsius") -> str:
    api_key = os.environ["WEATHER_API_KEY"]
    url = f"https://api.weather.com/v1/current?city={city}&key={api_key}"
    resp = requests.get(url, timeout=5)
    data = resp.json()
    temp = data["current"]["temp_c"] if unit == "celsius" else data["current"]["temp_f"]
    return f"{city}: {data['current']['condition']}, {temp}°"
```

### 场景 2：数据库查询（只读工具）

```python
@tool
def query_orders(user_id: str, days: int = 7) -> list:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "SELECT order_id, amount, created_at FROM orders WHERE user_id = %s AND created_at >= NOW() - INTERVAL '%s days' ORDER BY created_at DESC LIMIT 10",
        (user_id, days)
    )
    return [{"order_id": r[0], "amount": float(r[1])} for r in cur.fetchall()]
```

**安全要点**：数据库工具必须是只读账户，参数化查询防止 SQL 注入。

### 场景 3：知识库检索（RAG 本质）

```python
@tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    embeddings = openai.embeddings.create(input=query, model="text-embedding-3-small")
    results = vector_db.similarity_search(embeddings.data[0].embedding, top_k=top_k)
    return "\n".join([doc.text for doc in results])
```

**RAG 本质**：就是一个名为 "retrieve" 的工具，模型决定何时检索、用什么关键词。

### 场景 4：代码执行（沙箱环境）

```python
@tool
def execute_python(code: str) -> str:
    result = subprocess.run(["python", "-c", code], capture_output=True, text=True, timeout=10, cwd="/tmp/sandbox")
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
```

**警告**：必须在隔离环境中执行，沙箱隔离、网络隔离、资源限制缺一不可。

### 场景 5：多工具协作

用户提问："帮我分析一下上个月销售额最高的产品，并查一下它的库存情况"

```text
第 1 轮：query_sales_ranking(period="last_month", top_n=1) → {"product_id": "P12345", "revenue": 128000}
第 2 轮：get_inventory(product_id="P12345") → {"stock": 450, "warehouse": "WH-Shanghai"}
第 3 轮：模型综合生成回答
```

---

## 六、常见陷阱

### 1. 工具描述不精确

**错误**：`{"name": "search", "description": "搜索信息"}`

**正确**：明确说明适用场景、不适用场景、参数建议

```json
{
    "name": "search_web",
    "description": "在互联网上搜索最新信息，适用于新闻、事实核查。不适用于内部数据查询。",
    "parameters": {
        "query": {"type": "string", "description": "搜索关键词，建议使用英文"},
        "num_results": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5}
    }
}
```

### 2. 缺少参数校验

工具函数内部必须进行严格的参数校验，因为 LLM 可能输出无效值：

```python
def get_weather(city: str, unit: str = "celsius"):
    if not city or len(city) > 100:
        raise ValueError("城市名称不能为空或超过 100 字符")
    if unit not in ("celsius", "fahrenheit"):
        unit = "celsius"
```

### 3. 超时与错误处理

网络请求、数据库查询都可能失败，必须有完善的异常处理。将错误信息作为 tool 结果回传，让模型决定是重试、换工具还是告知用户。

### 4. 循环调用限制

必须设置 `max_turns`（建议 3-5），并在达到上限时主动中断。

### 5. 安全考虑

| 风险 | 缓解措施 |
|------|----------|
| 工具权限过大 | 最小权限原则：只读账户、限流、白名单 |
| 代码注入 | 沙箱执行、禁用危险模块、静态分析 |
| 敏感数据泄露 | 工具结果脱敏、审计日志、访问控制 |
| SSRF | 禁止工具访问内网地址、DNS 重绑定防护 |

---

## 七、面试陷阱速览

> 完整陷阱 + 反直觉 + 30 秒话术见 [13.split-hairs Function Calling](../../../13.split-hairs/11.ai/function-calling/README.md)

---

## 相关章节

- 🆕 关联：[结构化输出（JSON）](../structured-output/README.md) — FC 是实现稳定 JSON 输出的手段之一
- 关联：[Prompt Engineering](../prompt-engineering/README.md) — 工具描述本质是结构化 Prompt
- 关联：[Context Engineering](../context-engineering/README.md) — 工具定义是 Context 的重要组成
- 关联：[Agent 架构](../../04-architecture/agent-architecture/README.md) — Function Calling 是 Agent 的核心机制
- 关联：[RAG](../../08-llmops/01-rag-vs-finetuning/README.md) — RAG 本质是一个 retrieve 工具

← [返回: L2 技术栈](../README.md)
