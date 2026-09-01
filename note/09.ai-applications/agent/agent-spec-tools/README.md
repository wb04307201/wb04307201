<!--
module:
  parent: ai
  slug: ai/agent-spec-tools
  type: index
  category: 主模块子文章
  summary: Agent Spec Tools：Superpowers / Spec-Kit / OpenSpec 三工具安装、配置、使用与选型对比。
  depth: ⭐⭐⭐
-->

# Agent Spec Tools — 三工具对比与选型

← 返回 [Agent MOC](../README.md)

> 2025-2026 年 AI 编程三大规范工具：让 Agent 从"随意写代码"进化到"先规划再动手"。它们在不同层面解决不同问题，可以组合使用。

---
---

## 一、核心结论（TL;DR）

| 维度 | [Superpowers](superpowers.md) | [Spec-Kit](spec-kit.md) | [OpenSpec](openspec.md) |
|------|------|------|------|
| **创造者** | Jesse Vincent (obra) | GitHub 官方 | Fission AI |
| **一句话定位** | 工作流执行引擎（怎么干活） | 企业级规范管线（写什么规范） | 轻量规范对齐协议（确认写什么） |
| **安装方式** | Claude Code 插件 | Python CLI（uv） | npm CLI |
| **Agent 支持** | Claude Code / Cursor | 35 集成（Copilot / Claude / Cursor / Gemini…） | Claude Code / Cursor / 通用 |
| **核心命令数** | 14 个 Skill | 9 个 `/speckit.*`（短路径 5 / 全路径 9） | 9 个 `/opsx:*` 命令 |
| **TDD 强制** | ✅ 必须 RED→GREEN | ❌ 不强制 | ❌ 不强制 |
| **子 Agent 编排** | ✅ 内置并行分发 | ❌ | ❌ |
| **GitHub Stars** | 89K+ | GitHub 官方项目 | 社区增长中 |
| **适合谁** | 追求代码质量的个人/团队 | 企业团队 + 多 Agent 标准化 | 小团队快速迭代 + 决策追溯 |

---

## 二、分层架构 —— 它们不竞争，是互补

```text
┌────────────────────────────────────────────────────────┐
│  LAYER 3: 工作流执行（HOW）                             │
│  Superpowers — 约束 Agent 怎么干活                      │
│  （TDD 强制 · 并行子 Agent · 7 阶段流程 · Code Review） │
├────────────────────────────────────────────────────────┤
│  LAYER 2: 规范管线（WHAT）                              │
│  Spec-Kit — 结构化"要做什么"的规范                      │
│  （constitution → specify → clarify → plan → tasks）    │
├────────────────────────────────────────────────────────┤
│  LAYER 1: 规范对齐（AGREEMENT）                         │
│  OpenSpec — 确保人和 Agent 对"做什么"达成共识           │
│  （propose → apply → verify → archive）                 │
└────────────────────────────────────────────────────────┘
```

**关键洞察**：三个工具可以**组合使用** ——
- 用 Spec-Kit / OpenSpec 定义"做什么"
- 用 Superpowers 约束 Agent "怎么做"
- 最终实现 Spec-Driven Development（SDD）

---

## 三、选型决策树

```text
你的需求是什么？
│
├─ "我要 Agent 严格按 TDD 写代码"
│   → Superpowers（唯一强制 TDD 的工具）
│
├─ "我的团队用多种 Agent，需要统一规范流程"
│   → Spec-Kit（支持 35 集成，GitHub 生态集成）
│
├─ "我想最快上手，轻量就好"
│   → OpenSpec（npm install + 4 个核心命令）
│
├─ "我要最大程度的代码质量"
│   → Spec-Kit + Superpowers 组合
│     （Spec-Kit 定义规范 + Superpowers 强制 TDD 执行）
│
└─ "我先试试 SDD 是什么感觉"
    → OpenSpec（最简单，5 分钟上手）
```

---

## 四、三工具共同点：SDD 循环

三个工具都实现了同一个核心循环 —— **Spec-Driven Development（SDD）**：

```text
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Specify │────▶│   Plan   │────▶│  Execute │────▶│  Verify  │
│  定义规范 │     │  拆解计划 │     │  执行实现 │     │  验证对齐 │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      ▲                                               │
      └───────────────────────────────────────────────┘
```

| 阶段 | Superpowers | Spec-Kit | OpenSpec |
|------|-------------|----------|----------|
| **Specify** | `brainstorming` skill | `/speckit.specify` | `/opsx:propose` |
| **Plan** | `writing-plans` skill | `/speckit.plan` | `/opsx:propose`（内含计划） |
| **Execute** | `dispatching-parallel-agents` + TDD | `/speckit.tasks` → `/speckit.implement` | `/opsx:apply` |
| **Verify** | `verification-before-completion` | `/speckit.analyze` + `/speckit.converge` | `/opsx:verify` |

---

## 五、各工具深度指南

| 工具 | 内容 | 链接 |
|------|------|------|
| **Superpowers** | 安装 + 14 内置 Skill + 7 阶段工作流 + 子 Agent 编排 | [→ superpowers.md](superpowers.md) |
| **Spec-Kit** | 安装 + 5 命令 SDD 管线 + 跨 Agent 兼容 + 企业用法 | [→ spec-kit.md](spec-kit.md) |
| **OpenSpec** | 安装 + /opsx 命令 + 目录结构 + AGENTS.md + 快速迭代 | [→ openspec.md](openspec.md) |

---

## 六、与其他章节的关系

- 概念层：Harness Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../agent-execution-patterns/harness-engineering/]`） — 这三个工具都是 Harness 的具体实现
- 同栏目：Claude Code 实践（⚠️ 待 Phase 1+ 迁入；占位 `[../coding-agents/claude-code-practices/]`） — Skill 设计方法论 + Hit Rate 优化
- 实战：[生产级 Agent](../production-agent/README.md) — 生产环境的 Agent 工程实践
- 循环：Loop Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../agent-execution-patterns/loop-engineering/]`）— Agent 循环调用 + Ralph Wiggum Loop（pre-existing in `note/`，保持 unstaged）
- **正交关系**：[Coding Agents](../coding-agents/README.md) — Superpowers / Spec-Kit / OpenSpec 都**运行在** Coding Agent 上（Claude Code / Codex / OpenCode / OMP）

---

## 七、Function Calling 协议层 —— Agent 与 Tool 的契约规范

> 上一节讲的是「Agent 如何编排 Spec」（SDD 三工具），这一节切换到「Agent 如何调用 Tool」（Function Calling 协议层）。两者正交：SDD 决定「写什么规范」，Function Calling 决定「Tool 如何被调用」。Spec 落到执行时，必然经过 Function Calling 这层 wire protocol。

### 7.1 OpenAI Function Calling 演进史

```text
2023.06  GPT-4 function calling (gpt-4-0613 / gpt-3.5-turbo-0613)
            └─ 单次只允许 1 个 tool_call，parameters 用 JSON Schema 描述
2024.04  parallel tool calls（gpt-4-turbo / gpt-4o）
            └─ 一次 assistant 消息可包含多个 tool_calls，参数可相互独立
            └─ 新增 parallel_tool_calls=true 控制是否启用
2024.08  GPT-4o structured outputs
            └─ response_format 支持 json_schema 严格模式
2024.12  strict mode 全量开放（所有支持 function calling 的模型）
            └─ strict: true 时强制 schema 完整 + additionalProperties: false
2025.03  o-series reasoning 模型的 tool calls
            └─ reasoning_effort 与 tool_choice 联动（low/medium/high 影响决策深度）
```

#### OpenAI 严格模式三大铁律（strict: true）

1. **所有 object 类型必须声明 `additionalProperties: false`** —— 不写就 400
2. **所有字段必须出现在 `required` 数组中**（包括可选字段，标记为 nullable）
3. **不支持 `oneOf` / `anyOf` / `allOf` 的复杂 schema**（2025-09 仍未支持，部分限制可在 nested 嵌套用）

```python
# OpenAI strict mode JSON schema（Python SDK 1.50+）
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气",  # 50-100 token 最佳
            "strict": True,                            # ← 关键开关
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，如 'Beijing'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["city", "unit"],          # ← 必填全列
                "additionalProperties": False          # ← strict 必需
            }
        }
    }
]

# 三种 tool_choice 模式
resp1 = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": "北京今天多少度？"}],
    tools=tools,
    tool_choice="auto"          # 模型决定调不调（默认）
)

resp2 = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": "随便聊聊"}],
    tools=tools,
    tool_choice="required"      # 强制必须调（用于结构化抽取场景）
)

resp3 = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": "北京天气"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
    # 强制调指定函数（用于路由分发）
)
```

### 7.2 Anthropic Tool Use 协议

Anthropic 的 tool use 与 OpenAI 在协议层有三大根本差异：

| 维度 | OpenAI | Anthropic |
|------|--------|-----------|
| **tool 定义位置** | `tools` 顶层参数 | `tools` 顶层参数（相同） |
| **tool 调用返回** | `message.tool_calls[i]` 数组 | `message.content` 内的 `tool_use` block |
| **停止原因** | `finish_reason="tool_calls"` | `stop_reason="tool_use"` |
| **schema draft** | JSON Schema Draft 2020-12（宽松） | JSON Schema Draft 2020-12（严格） |
| **流式增量** | SSE event `tool_calls.delta` | SSE event `content_block_start/delta/stop` |
| **prompt caching** | 不支持 tool 级别 cache | 支持 `cache_control` 标记（节省 90% input token） |

```python
# Anthropic Claude tool_use_block（Python SDK 0.40+）
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "查询指定城市的实时天气",
            "input_schema": {                         # ← 用 input_schema 而非 parameters
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["city", "unit"]
            },
            "cache_control": {"type": "ephemeral"}    # ← Anthropic 独有：缓存工具定义
        }
    ],
    messages=[{"role": "user", "content": "北京现在多少度？用摄氏度"}]
)

# 解析 tool_use block
for block in response.content:
    if block.type == "tool_use":
        print(f"调用函数: {block.name}")
        print(f"参数: {block.input}")
        tool_use_id = block.id           # 必须回传给 tool_result
```

#### Anthropic 流式 tool use 的特殊性

Anthropic 的 tool_use **block 必须等到 JSON 完整解析后才能拿到 input**（即使流式），因为它内部用增量 JSON parser 拼接。这意味着你无法在 `content_block_delta` 阶段就执行函数 —— 必须在 `content_block_stop` 之后才行动。OpenAI 同样如此（tool_calls 也需要等流结束）。

### 7.3 MCP（Model Context Protocol）

2024-11-25 Anthropic 发布的开放协议，目标：**让 LLM 与 Tool 的连接标准化、跨模型厂商可移植**。

#### MCP 三大原语（Primitives）

| 原语 | 类比 | 用途 |
|------|------|------|
| **Resources** | GET 端点 | 只读上下文（文件、数据库行、API 响应） |
| **Tools** | POST 端点 | 可执行动作（写入文件、发邮件、改 DB） |
| **Prompts** | 模板 | 预定义 prompt 模板（user-controlled slash command） |

#### 通信协议栈

```text
┌────────────────────────────────────────────────────┐
│  Host（Claude Desktop / Cursor / Cline）           │
│  ┌──────────────────────────────────────────────┐  │
│  │  MCP Client（JSON-RPC 2.0 客户端）            │  │
│  └──────────────────────────────────────────────┘  │
│         │                                          │
│         │ stdio（本地进程）                          │
│         │ HTTP+SSE（远程 v1）                       │
│         │ Streamable HTTP（远程 v2，2025 替换 SSE）│
│         ▼                                          │
│  ┌──────────────────────────────────────────────┐  │
│  │  MCP Server（JSON-RPC 2.0 服务端）            │  │
│  │  暴露 Resources / Tools / Prompts           │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

```python
# Python MCP server 最小实现（mcp>=1.0）
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> dict:
    """查询指定城市的实时天气（用于 LLM tool 调用）

    Args:
        city: 城市名，如 'Beijing'
        unit: 温度单位，可选 'celsius' 或 'fahrenheit'
    """
    # 实际调用天气 API（这里省略）
    return {"city": city, "temp": 22, "unit": unit, "condition": "sunny"}

@mcp.resource("weather://{city}")
def weather_resource(city: str) -> str:
    """只读资源：返回城市的天气快照"""
    return f"实时天气: {city} 22°C 晴"

@mcp.prompt()
def weather_report(city: str) -> str:
    """预定义 prompt：生成天气报告"""
    return f"请调用 get_weather 工具获取 {city} 的天气，并用 50 字总结"

if __name__ == "__main__":
    mcp.run()  # 默认 stdio 传输
```

MCP 与 Function Calling 的关系：**MCP 是 server 协议，function calling 是模型能力**，二者正交。一个 OpenAI 模型可以通过 MCP client 调用 Anthropic 发布的 MCP server；反之亦然。详见 §7.7 误区 #4。

### 7.4 JSON Schema 约束深度

#### 7.4.1 类型系统

| JSON Schema 类型 | Python 类型 | 示例 |
|------------------|-------------|------|
| `string` | `str` | `"hello"` |
| `integer` | `int` | `42` |
| `number` | `float` | `3.14` |
| `boolean` | `bool` | `true` |
| `array` | `list` | `[1, 2, 3]` |
| `object` | `dict` | `{"k": "v"}` |
| `null` | `None` | `null` |

#### 7.4.2 必填字段（required）

OpenAI strict mode 要求**所有字段都必须列在 `required` 数组中**，包括「概念上可选」的字段。可选字段通过 `nullable: true` 标记：

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "城市，必填"},
    "country": {"type": ["string", "null"], "description": "国家，可选"}
  },
  "required": ["city", "country"],
  "additionalProperties": false
}
```

#### 7.4.3 枚举（enum）

`enum` 用于「固定可选值」场景，能显著提升 tool call 的命中率（模型不用思考格式）：

```json
{"type": "string", "enum": ["low", "medium", "high"]}
```

⚠️ 反直觉：枚举值在 prompt 中**算 token**（每个值都会出现在 system prompt 的工具描述里）。50 个枚举值 ≈ 50 token 的固定成本 —— 慎用大枚举。

#### 7.4.4 嵌套对象与 $ref 引用

OpenAI strict mode **不支持跨字段 `$ref`**（只能内联展开）。Anthropic 与 MCP 支持但解析较慢：

```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "address": {"$ref": "#/$defs/Address"}
      },
      "required": ["name", "address"]
    }
  },
  "$defs": {
    "Address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"}
      },
      "required": ["street", "city"]
    }
  }
}
```

### 7.5 Tool Use Error Handling

#### 7.5.1 四大错误类型

| 错误类型 | 触发场景 | 可重试？ |
|----------|----------|----------|
| `invalid_arguments` | 模型输出不符合 schema（缺字段、类型错） | ❌ 重试无效（同样 prompt 同样错） |
| `tool_not_found` | 模型调用了不存在的工具（多 Agent 场景幻觉） | ⚠️ 部分可重试（修改 prompt 后） |
| `execution_error` | 函数内部抛异常（DB 断连、API 5xx） | ✅ 可重试（指数退避） |
| `timeout` | 函数执行超过 timeout（默认 30s） | ✅ 可重试（先调 timeout） |

#### 7.5.2 指数退避重试装饰器

```python
import time
import functools
from typing import Callable, Any

RETRYABLE_ERRORS = ("execution_error", "timeout", "rate_limit_exceeded")

def retry_tool(max_retries: int = 3, base_delay: float = 1.0):
    """指数退避：1s → 2s → 4s，封顶 3 次"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_type = classify_error(e)
                    if error_type not in RETRYABLE_ERRORS:
                        raise  # invalid_arguments 等不可重试
                    if attempt == max_retries:
                        raise
                    delay = base_delay * (2 ** attempt)  # 1 → 2 → 4
                    time.sleep(delay)
            raise last_error
        return wrapper
    return decorator

def classify_error(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return "invalid_arguments"
    if isinstance(exc, TimeoutError):
        return "timeout"
    if "rate limit" in str(exc).lower():
        return "rate_limit_exceeded"
    return "execution_error"

@retry_tool(max_retries=3)
def query_database(sql: str) -> list[dict]:
    # 实际数据库调用
    ...
```

#### 7.5.3 降级方案：Tool 失败回退到直接 LLM 推理

当所有重试都失败后，**不能让 Agent 直接 crash**。常见降级策略：

1. **Tool → 自然语言兜底**：将 tool 错误信息塞回 prompt，让 LLM 用文本回答（牺牲准确性）
2. **Tool → 简化版本**：先用精简参数试一次（如去掉 optional 字段）
3. **Tool → 切换备用工具**：相同语义的另一个 tool（如 SerpAPI 失败 → DuckDuckGo）

### 7.6 并行 vs 串行调用

#### 何时并行？

- 工具之间**无数据依赖**（如同时查天气、汇率、日历）
- 下游 API 速率限制允许（注意 ❌ 误区 #3）
- 调用方可以并发（asyncio / Promise.all）

```python
# OpenAI parallel tool calls（单次 message 含多个 tool_calls）
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "查北京天气和上海天气"}],
    tools=[weather_tool],
    parallel_tool_calls=True   # ← 默认 true，允许一次返回多个
)

# 并发执行 tool_calls
results = await asyncio.gather(*[
    call_tool(tc.function.name, json.loads(tc.function.arguments))
    for tc in resp.choices[0].message.tool_calls
])
```

```python
# Anthropic 一次返回多个 tool_use block（content 数组）
for block in response.content:
    if block.type == "tool_use":
        # 每个 block 独立处理，可并行
        ...
```

#### 何时串行？

- 后一个 tool 的参数依赖前一个 tool 的输出（典型如「先查订单 ID → 再查订单详情」）
- Tool 内部有共享状态（如写入同一文件）
- 必须观察中间结果再决定下一步（如 ReAct pattern 的 Observe 阶段）

### 7.7 6 大反直觉 / 误区

#### ❌ 误区 #1：「Tool 描述越长越好」

实验数据（OpenAI Cookbook 2024-12 benchmark）：

| 描述长度 | Tool Call 命中率 | 平均延迟 |
|----------|------------------|----------|
| 0-50 token | 78% | 320ms |
| 50-100 token | **91%（峰值）** | 340ms |
| 100-200 token | 87% | 380ms |
| 200-500 token | 76% | 450ms |
| 500+ token | 61% | 580ms |

**结论**：50-100 token 是甜区。过长会「稀释关键参数」，模型注意力被无关信息分散。

#### ❌ 误区 #2：「JSON Schema 越严格越好」

strict mode 的代价：
- **延迟增加 10-30%**（模型需要解码完整的 JSON 并校验 schema）
- **不支持 `oneOf` / `anyOf`**（部分业务场景必须用，如「字符串或数组」二选一）
- **不支持 `$ref` 跨字段引用**（schema 必须内联展开，复杂业务 schema 会爆炸）

简单结构化抽取（如分类、情感分析）**不需要 strict mode**，用普通 prompt + JSON 解析器即可。

#### ❌ 误区 #3：「并行一定快」

当下游 API 有 rate limit 时（如 GitHub API 5000 req/h），并行 50 个 tool_calls 会触发 429，反而比串行慢 3-5 倍。**正确做法**：用 `asyncio.Semaphore(10)` 限制并发度，或用 batch API。

#### ❌ 误区 #4：「MCP 替代 Function Calling」

错。MCP 是 **server-side 协议**，让 tool 暴露方式标准化；Function Calling 是 **model-side 能力**，让 LLM 输出结构化 tool call。两者正交：

```text
MCP ≠ Function Calling 的替代品
MCP ≈ HTTP（传输协议标准化）
Function Calling ≈ RPC 协议（调用方式标准化）
```

一个 MCP server 可以同时被 OpenAI / Anthropic / Google 模型调用（通过各自的 MCP client 实现）；反过来一个 Function Calling 模型不一定用 MCP（可以用自定义 RPC、gRPC）。

#### ❌ 误区 #5：「Tool 失败重试 100% 有效」

`invalid_arguments` 和 `tool_not_found` 重试无效（同样的 prompt 会产出同样的错误）。生产环境必须：
1. 在 prompt 中加显式 schema 示例（few-shot）
2. 设置最大重试次数（3 次足够）
3. 重试失败后回退到 fallback 路径

#### ❌ 误区 #6：「Tool 返回 JSON 即可」

部分模型（尤其是 Claude 3 早期版本、Gemini 1.0）对 JSON 内的 **key 顺序敏感**。例如：

```json
// 模型预期：
{"city": "Beijing", "unit": "celsius"}

// 实际生成（key 顺序不同）：
{"unit": "celsius", "city": "Beijing"}
```

虽然 JSON 解析上等价，但部分模型的内部 representation 会影响后续 tool call 的稳定性。**解法**：在客户端用 `json.dumps(..., sort_keys=True)` 规范化。

### 7.8 真实源码 / 案例

#### 案例 1：LangChain `@tool` decorator 源码

LangChain 的 tool calling 在 `libs/langchain/langchain/tools/` 下：

- **`@tool` decorator**：`langchain_core/tools/convert.py` 中定义，本质是把 Python 函数包装成 `BaseTool` 子类
- **`StructuredTool`**：`langchain_core/tools/structured.py` —— 支持 Pydantic schema 自动生成 JSON Schema
- **`BaseTool._run()` 入口**：`langchain_core/tools/base.py` —— 所有 tool 调用的 dispatch 中心

```python
# LangChain @tool 的简化实现（langchain_core/tools/convert.py）
def tool(func_or_runnable=None, *, name=None, parse_docstring=True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        # 关键：自动从 docstring 推断 description
        if parse_docstring:
            description = parse_google_docstring(func)
        else:
            description = func.__doc__
        # 用 Pydantic 生成 JSON schema
        args_schema = create_schema_from_function(func)
        return BaseTool(
            name=name or func.__name__,
            description=description,
            args_schema=args_schema,
            func=func,
        )
    return wrapper
```

仓库路径：`github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/convert.py`（具体行号随版本变化）。

#### 案例 2：OpenAI Cookbook — strict mode 嵌套 JSON

官方示例：`github.com/openai/openai-cookbook/blob/main/examples/Structured_Outputs.ipynb`

展示了如何用 strict mode 实现**嵌套对象 + 数组 + 枚举**的复杂 schema，关键技巧：

```python
response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "research_paper",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "affiliation": {"type": "string"}
                            },
                            "required": ["name", "affiliation"],
                            "additionalProperties": False   # ← 嵌套也要声明
                        }
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title", "authors", "keywords"],
                "additionalProperties": False
            }
        }
    }
)
```

#### 案例 3：MCP 官方 Server 源码

Anthropic 官方维护的 MCP server 参考实现（`github.com/modelcontextprotocol/servers`）：

| Server | 暴露能力 | 关键文件 |
|--------|----------|----------|
| **filesystem** | Resources + Tools（读 / 写 / 搜索文件） | `src/filesystem/server.py` |
| **github** | Tools（PR / Issue / Repo 操作） | `src/github/server.py` |
| **postgres** | Resources + Tools（查询 / 修改 DB） | `src/postgres/server.py` |

所有 server 都遵循 `mcp.server.Server` 基类模式：注册 `list_tools()` / `call_tool()` 处理器，对应 JSON-RPC 的 `tools/list` 和 `tools/call` 方法。

#### 案例 4：Anthropic Claude Computer Use

2024-10 Anthropic 发布的 computer use 能力，本质是**tool use 的极端形态** —— 把整个 GUI 视为「一个超级工具」，每次返回鼠标坐标 + 键位事件：

```python
# Claude computer use 的 tool 定义
tools = [
    {
        "name": "computer",
        "description": "控制计算机：鼠标点击、键盘输入、截图",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "enum": ["left_click", "right_click", "type", "key", "screenshot"],
                    "type": "string"
                },
                "coordinate": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "[x, y] 坐标"
                },
                "text": {"type": "string", "description": "输入文本（type 动作）"}
            },
            "required": ["action"]
        }
    }
]

# 协议循环：
# 1. 用户给指令
# 2. Claude 调 computer(screenshot) 看当前屏幕
# 3. Claude 输出 computer(left_click, [500, 300])
# 4. 执行动作，返回新截图
# 5. 回到第 2 步，直到 Claude 调 computer(done) 或达到最大步数
```

这个案例展示了**Tool Use 协议的可扩展性** —— 任何 GUI 自动化、浏览器控制、IoT 设备都可以用 tool use 表达。

### 7.9 演进史时间线表

```text
2022.11  ChatGPT Plugins（OpenAI 首个 tool 接入尝试）
            └─ 需 web server 暴露 manifest 文件
            └─ 模型需要专门 fine-tune 才能调用
2023.06  OpenAI Function Calling（gpt-4-0613）
            └─ 不再需要 fine-tune，原生支持
            └─ JSON Schema 描述工具参数
2023.11  Anthropic Claude tool use（Claude 2.1）
            └─ 与 OpenAI 协议层相似但消息结构不同
2024.04  OpenAI parallel tool calls（gpt-4-turbo）
            └─ 单次响应可包含多个 tool_calls
2024.05  Google Gemini function calling（Gemini 1.5）
            └─ 支持 Python SDK + REST API
2024.08  OpenAI structured outputs（gpt-4o-2024-08-06）
            └─ response_format 支持 json_schema 严格模式
2024.10  Anthropic computer use（Claude 3.5 Sonnet 新能力）
            └─ tool use 扩展到 GUI 控制
2024.11  MCP（Model Context Protocol）发布
            └─ Anthropic 主导的开源协议
            └─ Resources / Tools / Prompts 三大原语
2024.12  OpenAI strict mode 全量开放
2025.03  MCP 生态爆发（数百个公开 server）
            └─ Cursor / Cline / Continue 全部集成 MCP client
2025.06  MCP Streamable HTTP 传输（替代 SSE）
2025.09  OpenAI o-series reasoning 模型 tool calling
            └─ reasoning_effort 与 tool_choice 联动
```

### 7.10 Function Calling 速查对照表

| 维度 | OpenAI | Anthropic | MCP（server 协议） |
|------|--------|-----------|---------------------|
| **协议名称** | function calling | tool use | Model Context Protocol |
| **首发时间** | 2023-06 | 2023-11 | 2024-11 |
| **schema 字段名** | `parameters` | `input_schema` | `inputSchema` |
| **返回字段** | `tool_calls[]` | `content[]` (含 tool_use) | JSON-RPC `result.content[]` |
| **stop_reason** | `tool_calls` | `tool_use` | 无（JSON-RPC 协议） |
| **并行支持** | `parallel_tool_calls` | content block 数组 | JSON-RPC 多请求并发 |
| **strict mode** | ✅ strict: true | ⚠️ 部分校验 | ❌ 不管 schema，由 client 校验 |
| **prompt caching** | ❌ | ✅ cache_control | ✅ 由 client 实现 |
| **传输层** | HTTPS | HTTPS | stdio / HTTP+SSE / Streamable HTTP |

### 7.11 跨模块反向链

> 「Agent Spec Tools」一文覆盖两个维度：上半部（§1-6）是 **Spec-Driven Development 工具**（决定写什么规范），下半部（§7）是 **Function Calling / Tool Use 协议**（决定 Tool 如何被调用）。两者通过 Agent 这个共同对象正交联动。

- **Prompt 协议**：→ note/09.ai-applications/prompts/prompt-engineering/README.md —— Tool 描述本质上是「结构化 prompt」，设计方法论一致
- **Agent 执行模式**：[→ note/09.ai-applications/agent/agent-execution-patterns/README.md](../agent-execution-patterns/README.md) —— ReAct / Plan-and-Execute 中 tool 调用是核心算子
- **Agent 架构**：[→ note/09.ai-applications/agent/architecture/README.md](../architecture/README.md) —— Tool Registry / Tool Sandbox / Tool Routing 在架构层的位置
- **面试题**：Function Calling 高频题（Tencent / 阿里 / 字节一面高频）→ [note/12.interview/11.ai/function-calling/README.md](../../../12.interview/11.ai/function-calling/README.md)
- **API Gateway 类比**：Tool 调用 ↔ API Gateway 的请求转发 → note/06.distributed-systems/02-distributed/api-gateway/README.md（类比：Tool Registry ≈ service registry；Tool Routing ≈ gateway routing）
- **生产级 Agent**：[→ note/09.ai-applications/agent/production-agent/README.md](../production-agent/README.md) —— Function Calling 在生产环境的可观测性 + 限流 + 熔断

---

⭐⭐⭐⭐⭐（高频面试 + 实战必会）

---

## 反向链

- [claude-code](../coding-agents/claude-code.md)
- [codex](../coding-agents/codex.md)
- [omp](../coding-agents/omp.md)
- [opencode](../coding-agents/opencode.md)

← [返回 Agent MOC](../README.md)
