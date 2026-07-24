<!--
module:
  parent: ai
  slug: ai/coding-agents/codex
  type: article
  category: 主模块子文章
  summary: Codex 速查版：OpenAI 官方 + GPT-5.3 Codex + wire_api/base_url 自定义 OpenAI 兼容网关 + config.toml MCP 配置。
-->

# Codex — OpenAI 官方编程 Agent（速查版）

← 返回 [Coding Agents 对比](README.md) · [工程实践](../README.md)

> OpenAI 官方 CLI / 桌面 App / IDE 插件三形态。**GPT-5.3 Codex 是当前最强单模型代码能力之一**，但通过 `wire_api` + `base_url` 可改向任意 OpenAI 兼容网关（关键转义点）。

---

## 一、TL;DR

| 维度 | 内容 |
|------|------|
| **定位** | OpenAI 官方编程 Agent，CLI / 桌面 App / IDE 插件三形态 |
| **协议 / 平台** | Apache 2.0（CLI）+ 商业 / macOS + Linux + Windows |
| **GitHub Stars** | 33K+（[openai/codex](https://github.com/openai/codex)）|
| **安装** | `npm install -g @openai/codex` / 桌面 App / IDE 插件 |
| **模型** | 默认 OpenAI（GPT-5.3 Codex / GPT-5）+ **`wire_api` + `base_url` 改向 OpenAI 兼容网关** |
| **MCP** | ✅ `~/.codex/config.toml` 的 `[mcp_servers.*]` 段 |
| **杀手特性** | GPT-5 顶级代码模型 + 云端并行沙盒 + wire_api 兼容网关转义 |
| **适合谁** | OpenAI 生态、需要最强单模型性能、需要 API 兼容网关 |

---

## 二、安装

### 2.1 NPM CLI（推荐）

```bash
npm install -g @openai/codex
codex --version  # 验证
```

### 2.2 桌面 App

```bash
# 从 https://openai.com/codex 下载
# macOS / Windows / Linux 都有原生安装包
```

### 2.3 IDE 插件

- **VS Code**：搜索 "OpenAI Codex" 扩展
- **JetBrains**：插件市场搜索 "Codex"

### 2.4 启动

```bash
cd /path/to/your/project
codex                  # 启动 TUI
codex -p "修复 login 函数 bug"  # 非交互模式
```

---

## 三、CLI 核心命令

| 命令 | 作用 |
|------|------|
| `codex` | 启动 TUI（interactive） |
| `codex -p "任务"` | 非交互模式 |
| `/init` | 扫描项目生成 AGENTS.md |
| `/compact` | 压缩上下文 |
| `/clear` | 清空会话 |
| `/model` | 切换模型（GPT-5.3 Codex / GPT-5 / GPT-4.1…）|
| `/approvals` | 配置权限审批模式 |
| `/reasoning` | 切换推理强度（low / medium / high）|

---

## 四、自定义模型配置（核心章节）

> ⚠️ **Codex 是 4 个 Coding Agent 中唯一原生支持 `wire_api` 字段**的 —— 可把请求改向任意 OpenAI 兼容网关，避免直接调 openai.com。

### 4.1 配置文件位置

```text
~/.codex/
├── config.toml          # 主配置（model / providers / mcp_servers / approvals）
├── auth.json            # OAuth 凭据（ChatGPT 登录）
├── sessions/            # JSONL 会话存储
└── logs/                # 调试日志
```

### 4.2 默认配置（OpenAI 直连）

```toml
# ~/.codex/config.toml
model = "gpt-5.3-codex"           # 或 "gpt-5" / "gpt-4.1"
model_provider = "openai"

[model_providers.openai]
name = "OpenAI"
base_url = "https://api.openai.com/v1"
# 默认 wire_api = "responses"（OpenAI 新 API）
env_key = "OPENAI_API_KEY"
```

### 4.3 自定义 OpenAI 兼容网关（关键差异点）

```toml
# ~/.codex/config.toml —— 把请求改向 ofox.io / 国内代理 / 自建网关
model = "gpt-5.3-codex"
model_provider = "openai-compatible"

[model_providers.openai-compatible]
name = "OpenAI 兼容网关"
base_url = "https://your-gateway.example.com/v1"
wire_api = "chat_completions"      # 关键：OpenAI 旧 API 兼容模式
env_key = "OPENAI_API_KEY"
request_timeout = 60
```

**为什么需要 `wire_api`**：
- OpenAI 新 API 用 `responses`（流式 + 工具调用新格式）
- 大多数第三方网关（DeepSeek / 智谱 / 月之暗面 / 自建）用旧 `chat_completions` API
- 改 `wire_api = "chat_completions"` 即可切换

### 4.4 API Key vs ChatGPT 登录

```bash
# 方式 1: API Key（推荐用于 CI / 多模型切换）
export OPENAI_API_KEY="sk-..."
codex

# 方式 2: ChatGPT Plus/Pro 登录（OAuth）
codex  # 首次启动浏览器登录 chat.openai.com
# 凭据存到 ~/.codex/auth.json
```

### 4.5 多角色模型

❌ **不支持 per-role 模型**。Codex 用单一模型（除非运行时 `/model` 切换）。

**理由**：OpenAI 把所有任务都交给 GPT 系列统一处理。`/reasoning` 强度可调但不分模型角色。

### 4.6 切换模型（运行时）

```bash
# TUI 中
/model gpt-5.3-codex   # 最新顶级代码模型
/model gpt-5           # 通用旗舰
/model gpt-4.1         # 备选

# 设置推理强度（仅 GPT-5 系列有效）
/reasoning high
```

---

## 五、MCP 配置（核心章节）

### 5.1 配置文件

```toml
# ~/.codex/config.toml
[mcp_servers.<name>]
command = "..."        # 本地 stdio（必填其一）
args = ["..."]
env = { KEY = "value" }

[mcp_servers.<name>]   # 远程
url = "https://..."
headers = { Authorization = "Bearer ..." }
```

### 5.2 本地 stdio MCP

```toml
# ~/.codex/config.toml
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "${env:GITHUB_TOKEN}" }

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
```

### 5.3 远程 MCP

```toml
# ~/.codex/config.toml
[mcp_servers.sentry]
url = "https://mcp.sentry.dev/mcp"

[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
headers = { CONTEXT7_API_KEY = "${env:CONTEXT7_API_KEY}" }
```

### 5.4 MCP 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | 本地 | 启动命令（stdio）|
| `args` | string[] | 本地 | 命令参数 |
| `env` | object | ❌ | 环境变量 |
| `url` | string | 远程 | 远程 MCP URL |
| `headers` | object | 远程 | HTTP 头（含认证）|

### 5.5 Codex MCP 特性

| 特性 | 支持 |
|------|------|
| 本地 stdio MCP | ✅ |
| 远程 HTTP MCP | ✅ |
| OAuth 自动检测 | ❌ 手动配置 headers |
| 按 Agent 启用 | ❌ 全局生效 |
| RFC 7591 动态客户端注册 | ❌ 手动 |

> 对比：OpenCode 的 MCP OAuth 自动 RFC 7591 注册比 Codex 自动化程度高。

---

## 六、特色能力

### 6.1 云端并行沙盒

Codex 可在 OpenAI 云端**并行启动多个沙盒**（每个沙盒独立 git worktree），并发执行多个子任务，最后合并结果。**这是 Codex 独有**的能力 —— 其他 3 个 Agent 都是本地执行。

### 6.2 IDE 深度集成

- VS Code 扩展：实时 inline diff + 修改建议
- JetBrains 插件：完整 IDE 集成
- 桌面 App：独立窗口 + 系统通知

### 6.3 与 ChatGPT 联动

Codex Pro 用户可在 ChatGPT 网页直接派发 Codex 任务，手机端也能启动 Agent。

---

## 七、与其他 3 个 Agent 的差异

| 维度 | Codex 优势 | Codex 劣势 |
|------|-----------|-----------|
| **vs Claude Code** | ✅ GPT-5 顶级代码模型 · ✅ 云端并行沙盒 · ✅ wire_api 转义 | ❌ 锁定 OpenAI · ❌ 无 CLAUDE.md/Skills 生态 · ❌ 无 DAP |
| **vs OMP** | ✅ OpenAI 生态最完整 · ✅ IDE 三形态（VS Code/JetBrains/桌面） | ❌ 无 per-role 模型 · ❌ 无 Hashline · ❌ 无 Subagent IRC bus |
| **vs OpenCode** | ✅ GPT-5.3 Codex 顶级代码 · ✅ ChatGPT Plus 联动 | ❌ 仅 OpenAI · ❌ 无 75+ providers · ❌ 无 oh-my-opencode 多 Agent |

---

## 八、适用场景

- ✅ **OpenAI 生态**：ChatGPT Plus/Pro / API Key 已有
- ✅ **最强单模型**：GPT-5.3 Codex 是当前代码能力顶级
- ✅ **云端并行**：需要并发多沙盒执行（Codex 独家）
- ✅ **IDE 深度集成**：VS Code / JetBrains 用户
- ✅ **API 兼容网关**：用国内代理 / 自建网关 / ofox.io 转 GPT-5
- ✅ **手机派发**：ChatGPT App 远程启动 Codex

**不适合**：
- ❌ 想用 Claude / DeepSeek / Ollama 等其他模型（用 OpenCode / OMP）
- ❌ 想要 Harness 5 扩展点（用 Claude Code）
- ❌ 想要 per-role 模型分工（用 OMP）

---

## 九、相关章节

- **横向对比**：[Coding Agents README](README.md) — 4 agent 选型决策树 + wire_api/base_url 全套配置对比
- **循环调用**：[Loop Engineering](../loop-engineering/README.md) — Ralph Wiggum Loop（Codex 也支持 `/goal` 长任务）
- **Harness 概念**：[Harness Engineering](../harness-engineering/README.md)
- **规范工具**：[Agent Spec Tools](../agent-spec-tools/README.md) — Spec-Kit 35 集成兼容 Codex

← [返回: Coding Agents 对比](README.md)