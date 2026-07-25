<!--
question:
  id: 11.ai-acp-protocol
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频（2025 新兴，2026 起高频）
  scenario_type: 反直觉辨析
  tags: [11.ai, ACP, agent-client-protocol, zed, jetbrains, mcp, a2a, json-rpc]
-->

# ACP（Agent Client Protocol）面试题：4 大 Agent 通信协议辨析 + Zed 集成反直觉点

> 一句话定位：ACP（Zed 出品 Apache 2.0）是**编辑器 ↔ Coding Agent** 的标准化通信协议，类似 LSP 对语言服务器的角色。深度原理见 [协议层深度](../../../11.ai/02-technology-stack/context-engineering/acp-protocol/README.md) + [概念地图 ACP 条目](../../../11.ai/02-technology-stack/concept-map/README.md#四-核心组件)。

> **系列定位**：AI 工程面试新增考点（2025 新兴协议）。考察的不是"ACP 是什么"，而是 **Agent 通信协议家族辨析**（MCP vs ACP vs A2A vs ANP）+ **为什么 ACP 用 JSON-RPC 而不是 gRPC** + **与 LSP 角色类比的反直觉点**。

---

⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：JSON-RPC / LSP 基本概念、了解 1+ 个 Coding Agent（Claude Code / Codex / Cursor）

---

## 引子：面试官的"协议混淆"陷阱

阿明去面试某 AI IDE 公司，面试官问：

> "ACP 和 MCP 有什么区别？"

阿明答："都是 Agent 协议，差不多的东西……"

面试官追问："ACP 是 Agent ↔ 编辑器的协议，MCP 是 Agent ↔ 工具的协议——它们在架构栈中处于不同层。如果让你设计一个 AI IDE 的 Agent 集成，你会选 ACP 还是 MCP？"

阿明答："MCP 吧，因为它火……"

面试官："那 Cursor / Zed / JetBrains 用什么协议接 Coding Agent？答：ACP。如果选错协议，你的 Agent 只能跑在 Claude Desktop 里，跑不进编辑器。**协议错位 = 用户用不上**。"

阿明愣住。

**这道题的陷阱在于**：很多人把 ACP / MCP / A2A 当成竞争关系，实际上它们是 **架构栈中不同层的协议**。ACP 解决"编辑器 ↔ Agent 通信"，MCP 解决"Agent ↔ 工具调用"，A2A 解决"Agent ↔ Agent 通信"。

今天我们就讲清楚：
1. ACP 到底是什么，为什么 2025 才出现
2. ACP 和 MCP / A2A / ANP 的本质区别
3. ACP 为什么选 JSON-RPC 2.0 而不是 gRPC / REST
4. ACP 与 LSP 的"角色类比"反直觉点

## 一、核心结论（TL;DR）

| 协议 | 解决什么问题 | 通信双方 | 标准化组织 | 典型实现 |
|------|------------|---------|----------|---------|
| **LSP** | 编辑器 ↔ 语言服务器 | 编辑器 ↔ LSP Server | 微软（2016） | typescript-language-server |
| **MCP** | Agent ↔ 工具/数据源 | Agent ↔ Tool/数据 | Anthropic（2024） | Claude Desktop / Claude Code |
| **ACP** | 编辑器 ↔ Coding Agent | 编辑器/IDE ↔ Agent | Zed（2025，Apache 2.0） | Zed / JetBrains / Toad / Obsidian |
| **A2A** | Agent ↔ Agent | Agent ↔ Agent | Google（2025） | ADK / Vertex AI Agent Engine |
| **ANP** | 互联网级 Agent 发现 | Agent ↔ Agent（跨网络）| 社区 | AgentNetworkProtocol |

> 一句话：**ACP 是 LSP 对语言服务器的角色，在 AI Agent 时代对应"编辑器 ↔ Coding Agent"标准化**——"implement once, work everywhere"。

## 二、核心原理：3 大设计原则

### 2.1 为什么 ACP 用 JSON-RPC 2.0 而不是 gRPC / REST

参考 [OpenClaw 团队 ACP 协议设计哲学](https://cloud.tencent.com/developer/article/2637509)：

| 协议 | 优势 | 劣势（对 ACP 场景） |
|------|------|-------------------|
| **REST/HTTP** | 简单 | 不支持服务端主动推送（工具调用进度、思考过程）；难以表达流式输出；无会话上下文概念 |
| **gRPC** | 强类型、高效、双向流 | 依赖 Protobuf，前端（TS/JS）集成复杂；二进制格式不可读；iOS/Android 需生成 stub |
| **GraphQL** | 灵活查询 | 本质仍是请求-响应，不擅长异步事件；缺乏对命令式操作（exec/abort）建模 |
| **JSON-RPC 2.0** ✅ | 人类可读 + 机器可靠 + 无 schema 依赖 | 无强类型（需额外校验） |

**ACP 选择**：JSON-RPC 2.0 + WebSocket + AI 原生语义扩展。

### 2.2 ACP 三大设计原则

```text
1. 编辑器优先（Editor-First）
   └─ 协议围绕 IDE / 编辑器设计，不是 AI 厂商设计
2. 双向流（Bidirectional Stream）
   └─ 支持 Agent 主动推送（进度、思考、工具调用结果）
3. 多端一致（Multi-Client Consistency）
   └─ Zed / JetBrains / Neovim / Obsidian 等 8+ 客户端协议兼容
```

### 2.3 ACP 核心消息流

```
[Editor] ──initialize──> [Agent]
[Editor] <──capabilities── [Agent]
[Editor] ──session/new──> [Agent]
[Editor] <──session/id─── [Agent]
[Editor] ──prompt────────> [Agent]
[Agent] ────message.delta→ [Editor]  (流式)
[Agent] ────tool.call────→ [Editor]  (工具调用权限请求)
[Editor] ─tool.response──→ [Agent]
[Agent] ────message.done─→ [Editor]
```

所有请求遵循 JSON-RPC 2.0：
```json
{
  "jsonrpc": "2.0",
  "method": "session.prompt",
  "params": {
    "sessionId": "ses_abc123",
    "prompt": [{ "role": "user", "content": "..." }]
  },
  "id": 1
}
```

## 三、面试陷阱（5 道）

### 陷阱 1：把 ACP / MCP / A2A 当成竞争关系

**真相**：**三层架构的不同协议**，互补而非竞争：
- **ACP**（L7 应用层）：编辑器 ↔ Coding Agent
- **MCP**（资源连接层）：Agent ↔ 工具 / 数据源
- **A2A**（Agent 协作层）：Agent ↔ Agent

**面试话术**：
> "ACP 解决编辑器集成（Zed/JetBrains 用 ACP），MCP 解决工具调用（Claude Code 用 MCP），A2A 解决 Agent 协作。三者不是竞争，是架构栈中不同层的协议。一个生产级 Agent 通常三种协议都用：编辑器用 ACP 接它，工具用 MCP 调用，A2A 派发给其他 Agent。"

### 陷阱 2：ACP 是 Anthropic / OpenAI 出品

**真相**：**ACP 是 Zed Industries 出品，Apache 2.0**，与 Anthropic 的 MCP 完全不同源。
- Anthropic → MCP（2024-11）
- Google → A2A（2025-04）
- **Zed Industries → ACP（2025）**
- 社区 → ANP

**面试话术**：
> "ACP 是 Zed 出的开源协议（Apache 2.0），不是 Anthropic 的 MCP。Zed 是 Rust 写的代码编辑器，2025 年起 JetBrains 官方合作，Google Gemini CLI 作为 reference 实现。ACP 是给编辑器厂商用的，MCP 是给 AI 厂商用的。"

### 陷阱 3：ACP = LSP 的简单克隆

**真相**：**LSP 用 JSON-RPC 但用 HTTP/stdio 传输；ACP 用 JSON-RPC + WebSocket**，因为 ACP 需要：
- 服务端主动推送（工具调用进度）
- 流式输出（message.delta 事件流）
- 长会话保持（session 状态）

**面试话术**：
> "ACP 与 LSP 角色类似（都是'标准化编辑器 ↔ 后端'通信），但传输层不同：LSP 用 stdio/HTTP（请求-响应为主），ACP 用 WebSocket（双向流为主）。因为 AI Agent 需要服务端主动推送工具调用进度和流式思考过程，LSP 的请求-响应模型不够用。"

### 陷阱 4：ACP 客户端实现很少

**真相**：**截至 2026-07，ACP 客户端/Agent 实现已 18+**：
- **编辑器**：Zed、JetBrains IDEs、Neovim、Emacs、Obsidian（Agent Client 插件）
- **TUI**：Toad（Will McGugan，Rich/Textual 作者）
- **官方 SDK**：Python SDK（v0.9.0）、TypeScript SDK
- **Reference Agent**：Google Gemini CLI、Hermes Agent（Nous Research）
- **框架**：marimo、Jupyter AI

**面试话术**：
> "ACP 客户端已 18+，覆盖 IDE / TUI / Notebook 三大场景。JetBrains 2025-10 官方合作意味着 IntelliJ / PyCharm / WebStorm 等核心 IDE 都将原生支持 ACP——这相当于 LSP 在 2016 年被 VS Code 采纳的级别。"

### 陷阱 5：ACP 还在草案阶段，不能生产用

**真相**：**ACP 已稳定使用 + 持续演进**：
- 2025 公开协议（Apache 2.0）
- 2025-10 JetBrains 官方合作
- 2026 Python SDK v0.9.0
- 2026-03 多篇深度技术博客（Tencent Cloud / cnblogs / CSDN）
- 2026-07 Obsidian 推出基于 ACP 的 Agent Client 插件

**面试话术**：
> "ACP 是 Apache 2.0 开源协议，已在生产用：Zed 编辑器原生支持、JetBrains 官方合作、Google Gemini CLI 作为 reference、Python SDK v0.9.0 发布。ACP 的成熟度类比 2016 年的 LSP——刚发布 1 年，已经成为 Coding Agent 编辑器集成的'事实标准'。"

## 四、最佳实践（3 大应用场景）

### 4.1 场景 1：编辑器厂商集成 Coding Agent

**需求**：Zed、JetBrains IDEs、Neovim 都需要支持 Claude Code / Codex / Gemini CLI。

**传统做法**：每个 Agent 接每个编辑器，N×M 适配。

**ACP 方案**：Agent 只需实现 ACP 协议，所有 ACP 兼容编辑器自动支持。

### 4.2 场景 2：AI IDE 厂商集成多个 Coding Agent

**需求**：Cursor / Windsurf 类 IDE 想支持多个 Coding Agent。

**传统做法**：每个 Agent 接 IDE 一次。

**ACP 方案**：实现 ACP client，IDE 自动支持所有 ACP Agent。

### 4.3 场景 3：Coding Agent 厂商扩展分发

**需求**：Claude Code 想支持 Zed / JetBrains / Obsidian / Cursor 等所有编辑器。

**传统做法**：每个编辑器单独适配。

**ACP 方案**：实现 ACP agent 端（已有 Python/TS SDK），所有 ACP 编辑器自动可用。

> "implement once, work everywhere"——ACP 的核心价值。

## 五、面试话术（90 秒版本）

### 5.1 模板 1："ACP 和 MCP 的区别"

> "ACP 解决编辑器 ↔ Coding Agent 的标准化通信，类似 LSP 对语言服务器的角色；MCP 解决 Agent ↔ 工具/数据源连接。两者架构栈不同层，互补而非竞争。一个生产级 Coding Agent 通常三个协议都用：编辑器用 ACP 接，工具用 MCP 调用，A2A 派发给其他 Agent。ACP 由 Zed Industries 出品（Apache 2.0），2025-10 JetBrains 官方合作；MCP 由 Anthropic 2024 发布。"

### 5.2 模板 2："ACP 为什么用 JSON-RPC 而不是 gRPC"

> "JSON-RPC 人类可读 + 机器可靠 + 无 schema 依赖。ACP 选择 JSON-RPC 2.0 + WebSocket 而非 gRPC，因为 gRPC 依赖 Protobuf，前端集成复杂，二进制格式不可读。ACP 需要支持流式输出（message.delta）和服务端主动推送（工具调用进度），LSP 的 stdio/HTTP 不够。ACP 用 JSON-RPC + WebSocket 是 AI Agent 场景的最优解。"

### 5.3 模板 3："ACP 与 LSP 的关系"

> "ACP 与 LSP 角色类似——都是'标准化编辑器 ↔ 后端'通信协议。LSP 标准化编辑器 ↔ 语言服务器（2016 微软）；ACP 标准化编辑器 ↔ Coding Agent（2025 Zed）。区别是 LSP 用 stdio/HTTP 请求-响应，ACP 用 WebSocket 双向流——AI Agent 需要服务端主动推送工具调用进度和流式思考过程。ACP 是 LSP 模式在 AI 时代的扩展。"

### 5.4 模板 4："ACP 生态成熟度"

> "ACP 已 Apache 2.0 开源 1+ 年，客户端实现 18+（Zed、JetBrains IDEs、Neovim、Emacs、Obsidian、Toad 等），Python SDK v0.9.0 已发布，Google Gemini CLI 作为 reference，JetBrains 2025-10 官方合作——这是 LSP 级别的标准化进程。ACP 是 2026 年 AI IDE 的'事实标准'。"

## 六、相关章节

### 6.1 主模块（协议层深度 + 工具）

- **协议层深度**：[`acp-protocol.md`](../../../11.ai/02-technology-stack/context-engineering/acp-protocol/README.md) — ACP 架构 + JSON-RPC 2.0 扩展 + Python SDK 示例 + 与 MCP/A2A/ANP 完整对比
- **概念地图**：[`concept-map.md`](../../../11.ai/02-technology-stack/concept-map/README.md) — ACP 在 Agent 协议族中的位置
- **MCP 对比**：[`mcp`](../../../11.ai/02-technology-stack/context-engineering/README.md#mcp-model-context-protocol) — Agent ↔ 工具协议（在 context-engineering README 中描述）
- **A2A 对比**：[Google A2A](https://google.github.io/A2A/) — Agent ↔ Agent 协议

### 6.2 同栏目（11.ai 系列面试题）

- [`coding-agent-mode-selection`](../coding-agent-mode-selection/README.md) — 4 个 Coding Agent 怎么选
- [`claude-code-agentic-search`](../claude-code-agentic-search/README.md) — Claude Code 为什么放弃 RAG
- [`multi-agent-system-design`](../multi-agent-system-design/README.md) — 多 Agent 系统设计
- [`harness-engineering`](../harness-engineering/README.md) — Harness 工程

### 6.3 关联主模块

- **Agent 通信协议家族**：MCP（Anthropic）/ ACP（Zed）/ A2A（Google）/ ANP（社区）
- **Coding Agent 集成**：[`coding-agents`](../../../11.ai/03-engineering/coding-agents/README.md) — 4 个 Coding Agent 横向对比

---

> 📅 2026-07-25 · 咬文嚼字 · 11.ai ACP 协议 · ⭐⭐⭐⭐（架构师级 · 中频新增）

← [返回: 咬文嚼字 · 11.ai](../README.md)