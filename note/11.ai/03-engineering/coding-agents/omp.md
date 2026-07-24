<!--
module:
  parent: ai
  slug: ai/coding-agents/omp
  type: article
  category: 主模块子文章
  summary: OMP (oh-my-pi)：终端原生 + 100k Rust LOC + Hashline + Subagent IRC bus + per-role 4 角色模型 + 进程内 LSP/DAP。
-->

# OMP (oh-my-pi) — Terminal-First Coding Agent

← 返回 [Coding Agents 对比](README.md) · [工程实践](../README.md)

> [Can Bölük](https://github.com/can1357) fork 自 Mario Zechner 的 [Pi-mono](https://github.com/badlogic/pi-mono)，**GitHub 17.7K+ stars · MIT 协议**。"A coding agent with the IDE wired in" —— 完全开箱即用、不妥协的原生实现：Windows 原生无 WSL、100k+ 行 Rust、32 内置工具、进程内 LSP/DAP。

---

## 一、TL;DR

| 维度 | 内容 |
|------|------|
| **定位** | 终端优先的编程 Agent，IDE wired in，开箱即用 |
| **来源** | Can Bölük，Pi-mono 的 hard fork |
| **协议 / 平台** | MIT / macOS + Linux + Windows（**原生无 WSL 桥**）|
| **安装** | `curl -fsSL https://omp.sh/install \| sh` / brew / bun / powershell / mise |
| **生态规模** | **40+ 模型 providers** / **32 内置工具** / **14 LSP ops** / **28 DAP ops** / **100k+ 行 Rust LOC** |
| **杀手特性** | Hashline 编辑（xxHash32 锚点）+ Subagent 通过 in-process IRC bus 直接 DM + GitHub 是虚拟文件系统 + 进程内 LSP/DAP |
| **Benchmark** | Grok Code Fast `pass@1: 6.7% → 68.3%` / Grok 4 Fast `-61% output tokens` |

---

## 二、安装

### 2.1 一键安装脚本（推荐）

```bash
curl -fsSL https://omp.sh/install | sh
```

### 2.2 包管理器

```bash
# macOS / Linux
brew install omp

# Bun（任意平台）
bun install -g @oh-my-pi/pi-coding-agent

# Windows PowerShell
irm https://omp.sh/install | iex

# Mise（跨平台）
mise use -g github:can1357/oh-my-pi
```

### 2.3 验证

```bash
omp --version
# 输出类似 0.x.y 表示成功

# 配置目录
ls ~/.omp/agent/        # config.yml + sessions/ + caches/
```

---

## 三、CLI 核心命令

| 命令 | 作用 |
|------|------|
| `omp` | 启动交互式 TUI（默认） |
| `omp -p "任务"` | 非交互模式（脚本/CI 用） |
| `omp -c <session>` | 恢复会话（resume） |
| `omp -r` | 进入会话树选择器（resume 选择） |
| `/plan` | 沙盒规划（用独立 planner 模型，审批后执行） |
| `/branch` | 在当前 JSONL 会话文件分叉出新叶 |
| `/fork` | 派生完全独立的会话文件 |
| `/tree` | 展示会话树（git-like） |
| `/review` | 启动 P0-P3 优先级 + confidence 评分代码审查 |
| `/collab <user>` | 共享会话链接（read-write 或 view-only） |
| `/agents` | 列出 8 个 bundled subagents |
| `/connect` | 配置 provider（OAuth / API key） |

---

## 四、自定义模型配置（核心章节）

> ⚠️ **OMP 是 4 个 Coding Agent 中唯一支持 per-role 多模型**的 —— 同一会话中 4 种角色可用 4 个不同模型。

### 4.1 配置文件位置

```text
~/.omp/agent/
├── config.yml          # 主配置（providers / models / mcp / plugins…）
├── agent.db            # 凭据（OAuth Token + API key，SQLite）
├── sessions/           # JSONL 会话文件（git-like branch/fork/tree）
├── skills/             # 用户自定义 Skill
└── plugins/            # 插件目录
```

### 4.2 Per-Role 模型配置（独家）

OMP 把模型按**角色**分工，对应不同场景：

| 角色 | 用途 | 推荐模型 |
|------|------|---------|
| `default` | 主对话（绝大多数 prompt）| Claude Sonnet 4.5 / GPT-5 |
| `smol` | 标题生成 / 文件名建议 / 小改写 | Claude Haiku 4.5 / GPT-4.1 nano |
| `slow` | 深度推理 / 复杂规划 | Claude Opus 4.5 / OpenAI o1-pro |
| `plan` | `/plan` 模式沙盒（独立 planner）| Claude Opus 4.5 |

```yaml
# ~/.omp/agent/config.yml
models:
  default: anthropic/claude-sonnet-4-5    # 主对话
  smol:    anthropic/claude-haiku-4-5     # 小任务（成本控制）
  slow:    openai/o1-pro                  # 深度推理
  plan:    anthropic/claude-opus-4-5      # /plan 沙盒（独立推理）
```

### 4.3 配置 Provider（OAuth + API key 都支持）

```yaml
# ~/.omp/agent/config.yml
providers:
  # OAuth 订阅（推荐：免 API key 费用）
  - anthropic       # Claude Pro/Max
  - openai          # ChatGPT Plus/Pro
  - copilot         # GitHub Copilot
  - cursor          # Cursor Pro
  - zai             # Z.AI（GLM 系列）

  # API key（环境变量自动注入）
  # 设 OPENAI_API_KEY=sk-... 后，provider: openai 自动生效
  # 设 ANTHROPIC_API_KEY=sk-ant-... 后，provider: anthropic 自动生效
```

**OAuth 登录流程**（首次）：
```bash
/connect
# 弹出浏览器授权（Claude Pro/Max / ChatGPT / Cursor / Copilot 任选）
# 凭据加密存到 ~/.omp/agent/agent.db
```

**添加自定义 Provider**（任意 OpenAI 兼容端点）：
```yaml
providers:
  - id: my-custom-openai
    type: openai-compatible
    base_url: https://my-gateway.example.com/v1
    api_key: ${env:MY_GATEWAY_API_KEY}
    models:
      - id: my-model-v1
        name: My Custom Model V1
```

### 4.4 模型选择 CLI

```bash
# TUI 中实时切换主模型
/models
# 列出所有已认证 provider 的可用模型
# 选定后写入 config.yml 的 models.default
```

---

## 五、MCP 配置（核心章节）

### 5.1 配置文件

```yaml
# ~/.omp/agent/config.yml
mcp:
  servers:
    - name: github           # MCP 服务器名称（提示词中 @<name> 引用）
      type: local            # 本地：stdio
      command: ["npx", "-y", "@modelcontextprotocol/server-github"]
      enabled: true
      environment:
        GITHUB_TOKEN: ${env:GITHUB_TOKEN}
      timeout: 5000           # 默认 5 秒

    - name: sentry           # 远程 MCP（Sentry 官方）
      type: remote
      url: https://mcp.sentry.dev/mcp
      enabled: true
      # OAuth 自动处理（401 检测 + RFC 7591 动态注册）

    - name: context7         # 远程 MCP（文档搜索）
      type: remote
      url: https://mcp.context7.com/mcp
      headers:
        CONTEXT7_API_KEY: ${env:CONTEXT7_API_KEY}
```

### 5.2 MCP 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | MCP 服务器唯一名称 |
| `type` | `local` \| `remote` | ✅ | 本地 stdio 或远程 HTTP |
| `command` | string[] | 本地 | 启动命令 + 参数（数组）|
| `url` | string | 远程 | 远程 MCP URL |
| `enabled` | boolean | ❌ | 启动时启用（默认 true）|
| `environment` | object | ❌ | 本地模式环境变量 |
| `headers` | object | ❌ | 远程模式 HTTP 头 |
| `oauth` | object | ❌ | 远程 OAuth 配置（自动 401 检测）|
| `timeout` | number | ❌ | 获取工具超时（毫秒，默认 5000）|

### 5.3 自带 Authoring 文档

OMP 官方 docs 有完整 **Authoring MCP servers** 章节，教你写自定义 MCP server 接入 —— 比其他 3 个 Agent 文档都厚。

### 5.4 MCP 启用粒度

OMP 支持**全局 + per-agent**双层启用，参考 opencode 的 glob 模式。

---

## 六、13 大特性速览

| # | 特性 | 一句话 |
|---|------|--------|
| § 01 | **EVAL** | 持久 Python + Bun Worker 双向桥接（agent 可在 Python 中调自己的工具）|
| § 02 | **LSP wired into every write** | 14 语言 + 53 servers，rename 通过 `workspace/willRenameFiles` 重写 barrel/aliased import |
| § 03 | **DAP** | 28 ops + 14 bundled adapters（lldb-dap / dlv / debugpy / js-debug-adapter）|
| § 04 | **TTSR** | Time-Traveling Stream Rules：regex 触发中断 + 重试，0 token cost until match |
| § 05 | **SUBAGENTS** | task 工具 fan-out 到隔离 worktree，8 bundled agents + IRC bus 兄弟直 DM |
| § 06 | **ADVISOR** | 第二模型旁听每轮，aside/concern/blocker 3 级别 |
| § 07 | **COLLAB** | `/collab` 生成链接 + QR，read-write 或 view-only，AES-256-GCM 端到端加密 |
| § 08 | **WEB** | `web_search` 链 14 ranked providers（arxiv / github / so / registries） |
| § 09 | **NATIVE-RS** | 100k Rust LOC，链接 ripgrep/glob/find 进进程（无 fork-exec）|
| § 10 | **REVIEW** | `/review` 启动 P0-P3 + confidence 评分 reviewer subagents |
| § 11 | **HASHLINE** | 4-hex xxHash32 锚点编辑，stale anchor 自动拒绝（避免文件损坏）|
| § 12 | **GITHUB-FS** | `read pr://1428/diff/3` 把 GitHub 当虚拟文件系统 |
| § 13 | **MEMORY** | mnemopi：SQLite + 向量嵌入 + 图工具，retain/recall/reflect 跨会话记忆 |

---

## 七、与其他 3 个 Agent 的差异

| 维度 | OMP 优势 | 适用人群 |
|------|---------|----------|
| **vs Claude Code** | ✅ 多 provider · ✅ per-role 模型 · ✅ 原生 Windows · ✅ Hashline | 不锁定 Anthropic 的工程师 |
| **vs Codex** | ✅ 多 provider · ✅ MCP 更成熟 · ✅ 终端深度体验 · ✅ 进程内 LSP/DAP | 不仅用 OpenAI 模型、需要 MCP 扩展 |
| **vs OpenCode** | ✅ per-role 模型 · ✅ 进程内 DAP（28 ops）· ✅ Windows 原生无 WSL · ✅ Rust 原生性能 | 终端重度用户、Win 用户、需要 DAP |

---

## 八、适用场景

- ✅ **终端深度用户**：每天 8h 在 terminal，要 IDE 级代码智能
- ✅ **Windows 用户**：不想用 WSL，想要原生体验
- ✅ **多模型策略**：不同任务用不同模型（深度推理 vs 日常编码）
- ✅ **Subagent 编排**：需要 sibling agent 直接 DM 而非 parent round-trip
- ✅ **GitHub 集成**：把 PR / Issue / diff 当文件系统读
- ✅ **DAP 调试**：agent 自动 attach debugger（lldb / dlv / debugpy）而非 print

**不适合**：
- ❌ 想要 GUI IDE（用 Cursor / Cody / Windsurf）
- ❌ 锁定 OpenAI 生态（用 Codex）
- ❌ 想要 Anthropic 官方 Skill 生态（用 Claude Code）

---

## 九、相关章节

- 横向对比：[Coding Agents README](README.md) — 4 agent 选型决策树 + 模型/MCP 配置对比
- 单工具深度（Claude Code）：[Claude Code Practices](../claude-code-practices/README.md)
- 循环调用：[Loop Engineering](../loop-engineering/README.md) — Ralph Wiggum Loop（Fresh Context + 文件系统持久记忆）
- 规范工具：[Agent Spec Tools](../agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec
- 概念层：[Harness Engineering](../harness-engineering/README.md)

← [返回: Coding Agents 对比](README.md)