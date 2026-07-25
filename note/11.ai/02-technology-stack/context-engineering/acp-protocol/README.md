<!--
module:
  parent: ai
  slug: ai/context-engineering/acp
  type: article
  category: 主模块子文章
  summary: ACP（Agent Client Protocol）—— Zed 出品的"编辑器 ↔ Coding Agent" 标准化通信协议，类似 LSP 对语言服务器的角色。Apache 2.0，与 MCP / A2A / ANP 互补。
-->

# ACP（Agent Client Protocol）—— 编辑器 ↔ Coding Agent 标准化通信

> **一句话定位**：ACP 是 [Zed Industries](https://zed.dev/) 出品的 Apache 2.0 协议，规范**代码编辑器 / IDE 与 Coding Agent 之间的交互**。类似 LSP 在 2016 年统一"编辑器 ↔ 语言服务器"的角色，ACP 在 2025 年统一"编辑器 ↔ AI Agent"。面试精炼版：[`13.split-hairs/11.ai/acp-protocol`](../../../../13.split-hairs/11.ai/acp-protocol/README.md)

---

## 一、为什么需要 ACP

### 1.1 现状：N×M 适配噩梦

2024-2025 年 Coding Agent 爆发：Claude Code、Codex、Gemini CLI、Cody、Continue 等 30+ Agent。编辑器侧 Zed、JetBrains、VS Code、Cursor、Obsidian、Neovim 也在接入。

**传统做法**：每个 Agent × 每个编辑器写一次适配。N×M 适配成本。

```
Claude Code ── 适配 ──> Zed
Claude Code ── 适配 ──> JetBrains
Claude Code ── 适配 ──> Obsidian
Codex ────── 适配 ──> Zed
Codex ────── 适配 ──> JetBrains
...（30+ Agent × 10+ 编辑器 = 300+ 适配）
```

### 1.2 ACP 方案："Implement Once, Work Everywhere"

```
Agent 实现 ACP 协议 ──> 所有 ACP 兼容编辑器自动支持
编辑器实现 ACP 协议 ──> 所有 ACP 兼容 Agent 自动支持
```

类似 LSP 对语言服务器的角色：2016 年微软发布 LSP 后，VS Code、Sublime、Vim 等所有编辑器只要实现 LSP 客户端就能接入所有语言服务器。

### 1.3 行业里程碑（2025-2026）

| 时间 | 事件 |
|------|------|
| 2025 | Zed Industries 发布 ACP（Apache 2.0） |
| 2025-10 | JetBrains 与 Zed 官方合作 |
| 2025-11 | Google Gemini CLI 作为 reference 实现 |
| 2026 | Python SDK v0.9.0、TypeScript SDK |
| 2026-03 | Obsidian 推出基于 ACP 的 Agent Client 插件 |
| 2026 | Hermes Agent（Nous Research）实现 ACP server mode |

**截至 2026-07，ACP 客户端/Agent 实现已 18+**，覆盖 IDE / TUI / Notebook 三大场景。

---

## 二、ACP 协议架构

### 2.1 协议栈位置（与 MCP / A2A 对比）

| 协议 | 解决什么 | 通信双方 | 标准化组织 | 提出年份 |
|------|---------|---------|----------|---------|
| **LSP** | 编辑器 ↔ 语言服务器 | Editor ↔ LSP Server | 微软 | 2016 |
| **MCP** | Agent ↔ 工具/数据源 | Agent ↔ Tool | Anthropic | 2024-11 |
| **ACP** | 编辑器 ↔ Coding Agent | Editor/IDE ↔ Agent | **Zed** | **2025** |
| **A2A** | Agent ↔ Agent | Agent ↔ Agent | Google | 2025-04 |
| **ANP** | 互联网级 Agent 发现 | Agent ↔ Agent | 社区 | 2025 |

```
┌─────────────────────────────────────────────────┐
│  L7 应用层                                      │
│  ┌──────────────┐   ┌──────────────┐              │
│  │   编辑器     │←→│  Coding Agent │  ← ACP 层    │
│  │  (Zed等)    │   │ (Claude Code) │              │
│  └──────────────┘   └──────┬───────┘              │
│                            ↓ MCP / A2A            │
│  ┌──────────────┐   ┌──────────────┐              │
│  │    工具      │   │   其他 Agent  │              │
│  │  (DB / API)  │   │  (协作 Agent) │              │
│  └──────────────┘   └──────────────┘              │
│  L4 资源连接层 / Agent 协作层                     │
└─────────────────────────────────────────────────┘
```

**关键洞察**：ACP / MCP / A2A 是**架构栈中不同层**的协议，互补而非竞争。一个生产级 Coding Agent 通常三种协议都用：
- 编辑器用 **ACP** 接它
- 工具用 **MCP** 调用
- A2A 派发给其他 Agent

### 2.2 为什么 ACP 用 JSON-RPC 2.0 + WebSocket

参考 [OpenClaw 团队 ACP 协议设计哲学](https://cloud.tencent.com/developer/article/2637509)：

| 协议 | 优势 | 对 ACP 场景的劣势 |
|------|------|----------------|
| **REST/HTTP** | 简单 | 不支持服务端主动推送（工具调用进度、思考过程）；流式输出需 SSE；无会话上下文 |
| **gRPC** | 强类型、高效、双向流 | 依赖 Protobuf，前端集成复杂；二进制不可读；移动端需生成 stub |
| **GraphQL** | 灵活查询 | 本质仍是请求-响应；缺乏命令式操作（exec/abort）建模 |
| **JSON-RPC 2.0** ✅ | 人类可读 + 机器可靠 + 无 schema 依赖 | 无强类型（需额外校验） |

**ACP 选择 JSON-RPC 2.0 + WebSocket**：
- JSON-RPC 2.0 提供基础 RPC 语义
- WebSocket 支持双向流（服务端主动推送）
- 整体方案对前端友好（TS/JS 直接用）

### 2.3 ACP 三大设计原则

```text
1. 编辑器优先（Editor-First）
   └─ 协议围绕 IDE / 编辑器设计，而不是 AI 厂商设计

2. 双向流（Bidirectional Stream）
   └─ 支持 Agent 主动推送（进度、思考、工具调用结果）
   └─ 与 LSP 单向请求-响应形成对比

3. 多端一致（Multi-Client Consistency）
   └─ Zed / JetBrains / Neovim / Obsidian 等 8+ 客户端协议兼容
   └─ 类似 LSP 对所有编辑器的统一
```

---

## 三、ACP 核心消息流

### 3.1 标准请求/响应模式

所有请求遵循 JSON-RPC 2.0：

```json
// ── Editor → Agent：初始化 ──
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0",
    "clientInfo": { "name": "zed", "version": "0.150" },
    "capabilities": { "fs": { "read": true, "write": true } }
  },
  "id": 1
}

// ── Agent → Editor：响应能力 ──
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "1.0",
    "agentInfo": { "name": "claude-code", "version": "1.0.0" },
    "capabilities": { "tools": { "call": true }, "stream": true }
  },
  "id": 1
}
```

### 3.2 会话生命周期

```json
// 1. 创建会话
{ "jsonrpc": "2.0", "method": "session/new", "params": {}, "id": 2 }
// → { "result": { "sessionId": "ses_abc123" }, "id": 2 }

// 2. 发送 prompt
{ "jsonrpc": "2.0", "method": "session/prompt",
  "params": { "sessionId": "ses_abc123",
    "prompt": [{ "role": "user", "content": "重构 src/auth.ts 的 JWT 验证" }] },
  "id": 3 }

// 3. 流式响应（WebSocket 推送，NOT JSON-RPC）
event message.delta → { "type": "text", "delta": "我先读一下..." }
event tool.call   → { "tool": "read_file", "args": { "path": "src/auth.ts" } }
event tool.result → { "result": "...JWT 验证逻辑..." }
event message.done → { "usage": { "input": 1200, "output": 800 } }
```

### 3.3 工具调用权限（ACP 特有）

编辑器可拦截 Agent 的工具调用请求，做权限审批：

```json
// Agent → Editor：请求工具调用权限
{ "jsonrpc": "2.0", "method": "tool/call/request",
  "params": { "tool": "write_file", "args": { "path": "src/auth.ts", "content": "..." } },
  "id": 10 }

// Editor → Agent：用户审批结果
{ "jsonrpc": "2.0", "result": { "approved": true, "reason": "user clicked yes" },
  "id": 10 }
```

这是 ACP 与简单 RPC 协议的关键差异——**编辑器是权限边界**，而非 Agent 自己决定。

---

## 四、Python SDK 示例（v0.9.0）

参考 [agentclientprotocol/python-sdk](https://github.com/agentclientprotocol/python-sdk)：

### 4.1 实现一个 ACP Agent（接 Claude Code 类需求）

```python
# acp_agent.py —— 接 Claude Code 这类 Coding Agent 的 ACP 协议层
import asyncio
from acp import Agent, Session, Message, ToolCall

class ClaudeCodeACPAgent(Agent):
    """An ACP agent that wraps Claude Code-style coding behavior."""

    async def initialize(self, params):
        return {
            "protocolVersion": "1.0",
            "agentInfo": {"name": "claude-code-acp", "version": "1.0.0"},
            "capabilities": {"tools": {"call": True}, "stream": True},
        }

    async def session_new(self, params):
        session_id = f"ses_{uuid.uuid4().hex[:8]}"
        return {"sessionId": session_id}

    async def session_prompt(self, params):
        session_id = params["sessionId"]
        user_msg = params["prompt"][-1]["content"]

        # 流式推送
        async def stream():
            yield {"type": "message.delta", "delta": "我先分析项目结构...\n"}
            # 工具调用
            yield {"type": "tool.call", "tool": "read_file",
                   "args": {"path": "src/auth.ts"}}
            # 等待编辑器审批结果
            # （实际协议由 SDK 处理）
            yield {"type": "message.delta", "delta": "重构方案如下..."}
            yield {"type": "message.done", "usage": {"input": 1200, "output": 800}}
        return stream()

# 启动
asyncio.run(ClaudeCodeACPAgent().serve())
```

### 4.2 实现一个 ACP Client（编辑器侧）

```python
# acp_client.py —— 编辑器侧，接 ACP Agent
import asyncio
from acp import Client

class ZedACPBridge(Client):
    """An ACP client that bridges Zed editor to any ACP agent."""

    async def on_message_delta(self, event):
        # 流式输出到编辑器 UI
        await self.zed_buffer.insert(event["delta"])

    async def on_tool_call(self, event):
        # 弹权限审批框
        user_approved = await self.zed_prompt.show(
            f"Agent 想要调用 {event['tool']}，是否允许？"
        )
        return {"approved": user_approved}

asyncio.run(ZedACPBridge().connect("ws://localhost:8765"))
```

### 4.3 安装与运行

```bash
# 安装 Python SDK
pip install agentclientprotocol

# 启动一个 ACP Agent server
python -m acp_sdk.agent --name my-agent

# 启动一个 ACP Client (Zed / JetBrains / 自研)
python -m acp_sdk.client ws://localhost:8765
```

---

## 五、与 MCP / A2A / ANP 完整对比

### 5.1 协议栈分层对比

| 维度 | LSP | MCP | ACP | A2A | ANP |
|------|-----|-----|-----|-----|-----|
| **提出者** | 微软 | Anthropic | Zed Industries | Google | 社区 |
| **提出年份** | 2016 | 2024-11 | 2025 | 2025-04 | 2025 |
| **协议层** | 编辑器↔后端 | Agent↔Tool | 编辑器↔Agent | Agent↔Agent | Agent 网络发现 |
| **传输** | stdio/HTTP | stdio/HTTP | WebSocket | HTTP+SSE | HTTP+WBA-DID |
| **消息格式** | JSON-RPC | JSON-RPC | JSON-RPC | JSON | JSON+DID |
| **流式输出** | ❌ | ❌ | ✅ | ⚠️（SSE）| ✅ |
| **权限边界** | 编辑器 | Agent 自己 | **编辑器** | Agent 自己 | 协议层 |
| **典型场景** | VS Code 写 TS | Claude Code 读 DB | Zed 跑 Claude Code | Google ADK 派任务 | 跨组织 Agent |
| **生产实现数** | 100+ 语言服务器 | 1000+ MCP server | 18+ Agent/编辑器 | Google 内部 | 实验性 |

### 5.2 互补关系实战

**场景 1**：用户用 Zed 编辑 TypeScript 项目，让 Claude Code 重构

```
[Zed 编辑器] ─ACP→ [Claude Code Agent]
                  │
                  ├─ MCP ─→ [GitHub MCP server] (查 issue)
                  ├─ MCP ─→ [PostgreSQL MCP server] (查 schema)
                  └─ A2A ─→ [Code Review Agent] (派单审查)
```

**场景 2**：JetBrains IDE 集成多个 Coding Agent

```
[IntelliJ]
  ├─ ACP → Claude Code
  ├─ ACP → Codex
  └─ ACP → Gemini CLI
（每个 Agent 只需实现 ACP 一次，IntelliJ 全部支持）
```

### 5.3 何时选哪个

| 你的场景 | 推荐协议 |
|---------|---------|
| 编辑器厂商集成 Coding Agent | **ACP** |
| AI 厂商让 Agent 接工具 / 数据 | **MCP** |
| 让 Agent 之间派任务 | **A2A** |
| 跨组织 / 互联网级 Agent 发现 | **ANP** |
| 所有上述场景 | **ACP + MCP + A2A 组合** |

---

## 六、ACP 生态（2026-07 截至）

### 6.1 客户端实现（18+）

| 客户端 | 类型 | 状态 |
|--------|------|------|
| **Zed** | 编辑器（创始） | ✅ 原生支持 |
| **JetBrains IDEs** | IDE（IntelliJ/PyCharm/WebStorm） | ✅ 2025-10 官方合作 |
| **Neovim** | 编辑器 | ✅ 插件 |
| **Emacs** | 编辑器 | ✅ 插件 |
| **Obsidian** | 笔记 + AI（Agent Client 插件）| ✅ 2026-03 |
| **Toad** | TUI（Will McGugan, Rich/Textual 作者）| ✅ |
| **marimo** | Notebook | ✅ |
| **Jupyter AI** | Notebook | ✅ |

### 6.2 Agent 实现

| Agent | 状态 |
|-------|------|
| **Google Gemini CLI** | ✅ Reference 实现 |
| **Hermes Agent**（Nous Research）| ✅ 2026-03 ACP server mode |
| **Claude Code** | ✅ Zed 通过 ACP 集成 |
| **Cody** | ✅ ACP 客户端集成 |

### 6.3 官方 SDK

| SDK | 版本 | 仓库 |
|-----|------|------|
| **Python SDK** | v0.9.0 | github.com/agentclientprotocol/python-sdk |
| **TypeScript SDK** | beta | github.com/agentclientprotocol/typescript-sdk |

---

## 七、与 LSP 的反直觉类比

### 7.1 相同点

- **角色相同**：标准化"编辑器 ↔ 后端"通信
- **"Implement Once"哲学**：后端实现协议，所有编辑器支持
- **开源协议**：LSP 是 JSON-RPC over stdio/HTTP；ACP 是 JSON-RPC over WebSocket
- **协议中立**：不绑定特定编辑器或后端

### 7.2 关键差异（ACP 独有的设计）

| 维度 | LSP | ACP |
|------|-----|-----|
| **后端类型** | 无状态语言服务（语法解析）| **有状态 AI Agent**（多轮对话、记忆）|
| **传输** | stdio（本地）+ HTTP（远程）| WebSocket（双向流）|
| **流式输出** | ❌（LSP 用 PublishDiagnostics）| ✅（message.delta 事件流）|
| **权限边界** | 编辑器独占 | 编辑器独占（更复杂：审批 Agent 工具调用）|
| **会话状态** | 单次请求 | 多轮会话（sessionId 维持）|
| **推出背景** | 编辑器需要支持 100+ 语言 | 编辑器需要支持 30+ AI Agent |

### 7.3 为什么 ACP 必须用 WebSocket

AI Agent 工作流：
```
用户：帮我重构这段代码
  ↓
Agent: 我先读一下文件...    ← 流式思考过程
  ↓
Agent: 调用 read_file       ← 工具调用（需审批）
  ↓
用户：同意                   ← 权限审批
  ↓
Agent: 重构方案是...        ← 流式输出
  ↓
Agent: 调用 write_file      ← 工具调用（需审批）
  ↓
用户：同意
  ↓
Agent: 完成                  ← 结束
```

LSP 的 stdio/HTTP 请求-响应**无法表达**这种多轮流式 + 权限审批 + 工具调用进度推送的复杂交互。**WebSocket 是 ACP 的必备选择**。

---

## 八、应用场景（3 个）

### 8.1 编辑器厂商集成 Coding Agent

**问题**：Zed、JetBrains IDEs、Neovim 都要支持 Claude Code、Codex、Gemini CLI 等 30+ Agent。

**ACP 方案**：实现 ACP 客户端（参考 4.2 示例），所有 ACP 兼容 Agent 自动支持。

### 8.2 AI IDE 厂商扩展分发

**问题**：Cursor / Windsurf 类 IDE 想支持多个 Coding Agent。

**ACP 方案**：实现 ACP 客户端，IDE 自动支持所有 ACP Agent。

### 8.3 Coding Agent 厂商分发

**问题**：Claude Code 想支持所有编辑器（Zed、JetBrains、Obsidian、Cursor）。

**ACP 方案**：实现 ACP agent 端（参考 4.1 示例），所有 ACP 编辑器自动可用。

> "Implement Once, Work Everywhere"——ACP 的核心价值。

---

## 九、参考来源

| 来源 | 一句话说明 |
|------|-----------|
| [agentclientprotocol.com](https://agentclientprotocol.com/get-started/introduction) | ACP 官方文档 |
| [ACP Python SDK](https://github.com/agentclientprotocol/python-sdk) | Python SDK v0.9.0 |
| [ACP 协议设计哲学（OpenClaw 团队）](https://cloud.tencent.com/developer/article/2637509) | 为什么选 JSON-RPC 2.0 而非 gRPC |
| [Agent Client Protocol 全景解析](https://www.cnblogs.com/smartloli/p/19792150) | ACP 协议完整解读（2026-03）|
| [Obsidian Agent Client 完全指南](https://blog.csdn.net/m0_65555479/article/details/157584710) | ACP 在 Obsidian 的应用 |
| [Hermes Agent ACP Server Mode](https://github.com/NousResearch/hermes-agent/issues/569) | ACP server mode 实现案例 |
| [MCP vs A2A vs ACP vs ANP](https://www.katonic.ai/blog-agent-protocols) | 4 大 Agent 协议对比 |

---

## 十、相关章节

### 10.1 主模块

- [`concept-map.md`](../../concept-map/README.md) — ACP 在 Agent 协议族中的位置（line 260、232、235、263 等）
- [`context-engineering.md`](../../context-engineering/README.md) — 上下文工程总览（含 MCP 等协议）
- [`mcp.md`](../../context-engineering/mcp.md) — Agent ↔ 工具协议（MCP）
- [`multi-agent-system-design`](../../../03-engineering/multi-agent-system-design/README.md) — 多 Agent 协作（含 A2A）
- [`coding-agents`](../../../03-engineering/coding-agents/README.md) — 4 个 Coding Agent 横向对比（Claude Code / Codex / OpenCode / OMP）

### 10.2 面试精炼

- [`13.split-hairs/11.ai/acp-protocol`](../../../../13.split-hairs/11.ai/acp-protocol/README.md) — ACP 面试题（5 道陷阱 + 90 秒话术 × 4 模板）

---

← [返回: Context Engineering](../README.md)