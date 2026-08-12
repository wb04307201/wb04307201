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

## 六、运行模式详解（核心章节）

> Codex 有**两种使用模式**（命令 / 交互）+ **`--approval-mode` 三档授权策略** + **桌面端独有的 Plan Mode + Goal Mode**。CLI 偏命令模式 + 交互模式，桌面 App 偏 Plan Mode + Goal Mode（长任务循环到 verifier 通过）。

### 6.1 命令模式（一次性调用）

**功能**：单次输入 → 单次输出 → 退出。**没有上下文，不能连续迭代**。本质是一次性 AI。

**触发方式**：
```bash
# 一次性 CLI 调用（适合 CI / 脚本）
$ codex "帮我写一个 FastAPI 接口"
# 输出代码 → 退出

# CI 自动化
$ codex exec "跑测试并修复失败用例"
# 执行 + 输出结果（无交互）

# 完全自动（full-auto 模式）
$ codex --approval-mode full-auto "生成一个带 UI 的 ML 应用"
# Codex 会：创建项目结构 / 写代码 / 安装依赖 / 生成可运行程序
```

**适用场景**：
- CI/CD 自动化管道
- 快速生成代码片段
- 简单一次性任务
- ⚠️ 缺点：无上下文、不能连续迭代、每次要重新解释需求

### 6.2 交互模式（长期 Agent）

**功能**：进入 TUI 后持续对话，**有上下文、能连续迭代、能执行命令 + 读项目 + 改文件**。**官方推荐**。

**触发方式**：
```bash
$ codex
# 进入交互 TUI（类似 ChatGPT 但能改文件 + 跑命令）

> 帮我分析这个项目结构
> 给这个服务加缓存
> 写单元测试
> 跑测试并修复错误
# Codex 会连续完成所有任务，保留上下文
```

**适用场景**：
- 真实开发流程
- 复杂工程任务
- 持续迭代
- 多步骤重构

### 6.3 Approval Mode（3 档授权策略）

Codex CLI 用 `--approval-mode` 控制 agent 的自主程度：

| Mode | 文件编辑 | 命令执行 | 网络访问 | 适用场景 |
|------|---------|---------|---------|---------|
| **suggest** | 每次 ask | 每次 ask | 每次 ask | 学习阶段（最谨慎）|
| **auto-edit** | 自动 | 每次 ask | 每次 ask | 批量生成 |
| **full-auto** | 自动 | 自动 | 自动 | CI/CD（最高效）|

**触发方式**：
```bash
# CLI 启动时指定
$ codex --approval-mode suggest "..."
$ codex --approval-mode auto-edit "..."
$ codex --approval-mode full-auto "..."

# 也可在交互模式中切
> /approvals
# 弹交互式选择面板
```

### 6.4 桌面端 Plan Mode + Goal Mode（独家）

Codex **桌面 App** 有两个独家模式（CLI 没有）：

**Plan Mode（计划模式）**：
```bash
# 桌面 App 配置
设置 → 工作区 → 启用"计划模式"
# agent 先输出完整方案 → 用户审批 → 才执行
```

**Goal Mode（追求目标 / 长任务循环）**：
```bash
# 桌面 App 配置
设置 → 工作区 → 启用"追求目标"
> 把这个项目的所有 TODO 解决掉
# agent 持续执行到 verifier 通过（类似 OMP /goal，但用同一个会话）
```

**与 OMP 对比**：

| 维度 | Codex 桌面端 | OMP |
|------|-------------|-----|
| Plan Mode | ✅ 桌面端配置 | ✅ `/plan` + per-role 模型 |
| Goal Mode | ✅ 桌面端"追求目标" | ✅ `/goal` |
| Handoff | ❌ | ✅ `/handoff` |
| Session tree | ❌ | ✅ |

### 6.5 Codex 模式对比

| 模式 | 触发方式 | 持续性 | 自主程度 | 适用 |
|------|---------|--------|---------|------|
| **命令模式 + suggest** | `codex "..."` | 一次性 | 最谨慎 | 学习 |
| **命令模式 + full-auto** | `codex --approval-mode full-auto "..."` | 一次性 | 最高 | CI/CD |
| **交互模式 + suggest** | `codex` + suggest | 长期 | 中 | 真实开发 |
| **交互模式 + full-auto** | `codex` + full-auto | 长期 | 最高 | 长任务自动化 |
| **桌面端 Plan Mode** | App 配置 | 长期 | 中 | 方案设计 |
| **桌面端 Goal Mode** | App 配置 | 长期 | 高 | 长任务循环 |

---

## 七、特色能力

### 6.1 云端并行沙盒

Codex 可在 OpenAI 云端**并行启动多个沙盒**（每个沙盒独立 git worktree），并发执行多个子任务，最后合并结果。**这是 Codex 独有**的能力 —— 其他 3 个 Agent 都是本地执行。

### 6.2 IDE 深度集成

- VS Code 扩展：实时 inline diff + 修改建议
- JetBrains 插件：完整 IDE 集成
- 桌面 App：独立窗口 + 系统通知

### 6.3 与 ChatGPT 联动

Codex Pro 用户可在 ChatGPT 网页直接派发 Codex 任务，手机端也能启动 Agent。

---

## 八、与其他 3 个 Agent 的差异

| 维度 | Codex 优势 | Codex 劣势 |
|------|-----------|-----------|
| **vs Claude Code** | ✅ GPT-5 顶级代码模型 · ✅ 云端并行沙盒 · ✅ wire_api 转义 | ❌ 锁定 OpenAI · ❌ 无 CLAUDE.md/Skills 生态 · ❌ 无 DAP |
| **vs OMP** | ✅ OpenAI 生态最完整 · ✅ IDE 三形态（VS Code/JetBrains/桌面） | ❌ 无 per-role 模型 · ❌ 无 Hashline · ❌ 无 Subagent IRC bus |
| **vs OpenCode** | ✅ GPT-5.3 Codex 顶级代码 · ✅ ChatGPT Plus 联动 | ❌ 仅 OpenAI · ❌ 无 75+ providers · ❌ 无 oh-my-opencode 多 Agent |

---

## 九、适用场景

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

## 十、相关章节

- **横向对比**：[Coding Agents README](README.md) — 4 agent 选型决策树 + wire_api/base_url 全套配置对比
- **循环调用**：[Loop Engineering](../../../../note/11.ai/03-engineering/loop-engineering/README.md) — Ralph Wiggum Loop（Codex 也支持 `/goal` 长任务）
- **Harness 概念**：[Harness Engineering](../../../../note/11.ai/03-engineering/harness-engineering/README.md)
- **规范工具**：[Agent Spec Tools](../agent-spec-tools/README.md) — Spec-Kit 35 集成兼容 Codex

← [返回: Coding Agents 对比](README.md)