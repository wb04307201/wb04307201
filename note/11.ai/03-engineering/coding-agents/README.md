<!--
module:
  parent: ai
  slug: ai/coding-agents
  type: index
  category: 主模块子文章
  summary: Coding Agents 横向对比 — Claude Code / Codex / OpenCode / OMP 安装、模型配置、MCP 配置、选型决策树。
-->

# Coding Agents — 4 大编程 Agent 横向对比与选型

← 返回 [工程实践](../README.md)

> 2025-2026 年 AI 编程 Agent 四大主流工具对比。**Coding Agent**（Agent 本身）与 **Agent Spec Tools**（Agent 上的规范，正交）是两层 —— 本目录聚焦 Agent 本身：CLI / 模型配置 / MCP / 生态。

---

## 一、核心结论（TL;DR）

| 维度 | [Claude Code](claude-code.md) | [Codex](codex.md) | [OpenCode](opencode.md) | [OMP (oh my pi)](omp.md) |
|------|------|------|------|------|
| **创造者** | Anthropic（官方）| OpenAI（官方）| Anomaly（开源）| Can Bölük（开源，fork 自 Pi-mono）|
| **协议** | 商业 | Apache 2.0 + 商业 | MIT | MIT |
| **GitHub Stars** | 闭源 CLI | 33K+ | 160K+ | 17.7K+ |
| **安装方式** | `npm i -g @anthropic-ai/claude-code` | `npm i -g @openai/codex` / 桌面 App | `curl -fsSL https://opencode.ai/install \| bash` | `curl -fsSL https://omp.sh/install \| sh` |
| **支持平台** | macOS / Linux / Windows | macOS / Linux / Windows / IDE 插件 | macOS / Linux / Windows（推荐 WSL）| macOS / Linux / Windows（**原生无 WSL**）|
| **模型支持** | 🔒 锁定 Anthropic | OpenAI 为主 + `wire_api` 兼容 | ✅ **75+ providers** | ✅ **40+ providers** |
| **多角色模型** | ❌ | ❌ | ✅ `small_model` | ✅ **default/smol/slow/plan 4 角色** |
| **MCP 支持** | ✅ `.mcp.json` | ✅ `config.toml [mcp_servers]` | ✅ `opencode.jsonc mcp` + OAuth 自动 RFC 7591 | ✅ `config.yml` + 自带 Authoring 文档 |
| **核心杀手特性** | CLAUDE.md / Hooks / Skills / Plugins / LSP / Subagents | GPT-5 顶级代码模型 + 云端并行沙盒 | Zen 精选模型 + oh-my-opencode 多 Agent 团队 | Hashline 编辑 + Subagent IRC bus + 进程内 LSP/DAP + 100k 行 Rust 原生 |
| **适合谁** | 已经在 Anthropic 生态、追求代码质量 | OpenAI 生态、需要最强单模型性能 | 想用任意 LLM + 多 Agent 编排的工程师 | 终端深度用户、需要原生跨平台 + 强 Agent 协作 |

---

## 二、选型决策树

```text
你的核心诉求是什么？
│
├─ "我已经在用 Anthropic Claude / 需要官方支持 + 完整生态"
│   → Claude Code（锁定 Anthropic，CLAUDE.md + Skills 生态最成熟）
│
├─ "我要最强单模型代码能力 / GPT-5 优先"
│   → Codex（OpenAI 官方，GPT-5.3 Codex 顶级，云端沙盒）
│
├─ "我想用任意 LLM（Anthropic / OpenAI / DeepSeek / Ollama…）+ 多个 Agent 协作"
│   → OpenCode（75+ providers + oh-my-opencode 多 Agent 框架）
│
├─ "我每天 8 小时在终端 / 需要原生跨平台（Win 无 WSL）/ 需要 Subagent 互相 DM"
│   → OMP（100k Rust LOC + Hashline + IRC bus + 进程内 LSP/DAP）
│
├─ "我要企业级统一规范流程（35+ Agent 集成）"
│   → Claude Code + Spec-Kit 组合
│
└─ "我先试试 vibe coding 是什么感觉"
    → Claude Code / Codex（最简单上手；Claude Code 有免费额度，Codex 桌面版免费）
```

**关键洞察**：4 个 Agent **不是互斥**，而是按场景混搭 —— 大型项目常用 Claude Code + Spec-Kit（团队规范）+ OpenCode（自由探索）。

---

## 三、模型配置横向对比（重点）

> ⚠️ 这是 4 个 Agent 差异**最大**的维度。Claude Code 是唯一锁定的，其他 3 个都支持自定义 Provider。

| 维度 | Claude Code | Codex | OpenCode | OMP |
|------|------------|-------|----------|-----|
| **默认模型** | Claude Opus 4.5 / Sonnet 4.5 / Haiku | GPT-5.3 Codex / GPT-5 | 任意（首个启动选模型）| 任意（OAuth 自动检测）|
| **配置文件** | `~/.claude/settings.json` + 环境变量 | `~/.codex/config.toml` | `opencode.jsonc` + `~/.local/share/opencode/auth.json` | `~/.omp/agent/config.yml` |
| **自定义 Base URL** | ❌ | ✅ `wire_api = "chat_completions"` + `base_url` | ✅ `provider.options.baseURL` | ✅ 任意 OAuth 端点 |
| **多角色模型** | ❌ | ❌ | ✅ `small_model` 字段 | ✅ **default / smol / slow / plan 4 角色** |
| **OAuth 订阅** | ✅ Claude Pro/Max | ✅ ChatGPT Plus/Pro | ✅ Copilot / Cursor / Claude Pro | ✅ **Pro/Max/ChatGPT/Copilot/Cursor/Z.AI** |
| **API Key** | ✅ Anthropic Console | ✅ OpenAI Console + 兼容网关 | ✅ 任意 provider console | ✅ 任意 provider |
| **本地模型（Ollama）** | ❌ | ❌（可改 base_url） | ✅ Ollama / llama.cpp / LM Studio | ✅ 任意 OpenAI 兼容端点 |

**自定义模型代码示例对比**：

**Claude Code**（锁定，无法自定义）：
```json
// ~/.claude/settings.json —— 只能选 Anthropic 模型
{
  "model": "claude-sonnet-4-5",
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-..."
  }
}
```

**Codex**（用 `wire_api` + `base_url` 改向兼容网关）：
```toml
# ~/.codex/config.toml
model = "gpt-5.3-codex"
model_provider = "openai"

[model_providers.openai]
name = "OpenAI 兼容网关"
base_url = "https://your-openai-compatible-gateway.com/v1"
wire_api = "chat_completions"  # 关键：chat_completions 而不是 responses
env_key = "OPENAI_API_KEY"
```

**OpenCode**（最灵活，自定义 Base URL）：
```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"  // 可改向代理
      }
    }
  },
  "small_model": "anthropic/claude-haiku-4-5"  // 单独配置小模型
}
```

**OMP**（per-role 模型 + 任意 Provider）：
```yaml
# ~/.omp/agent/config.yml
models:
  default: anthropic/claude-sonnet-4-5    # 主对话
  smol:    anthropic/claude-haiku-4-5     # 标题生成/小任务
  slow:    openai/o1-pro                  # 深度推理
  plan:    anthropic/claude-opus-4-5      # /plan 沙盒
providers:
  - anthropic    # OAuth Pro/Max 或 API key
  - openai
  - copilot
  - zai
```

---

## 四、MCP 配置横向对比（重点）

| 维度 | Claude Code | Codex | OpenCode | OMP |
|------|------------|-------|----------|-----|
| **配置文件** | `.mcp.json`（项目级）+ `~/.claude.json`（全局）| `~/.codex/config.toml` 的 `[mcp_servers.*]` | `opencode.jsonc` 的 `mcp` 字段 | `~/.omp/agent/config.yml` 的 MCP 段 |
| **本地 MCP** | `--mcp-config <file>` 启动参数 | TOML 配置段（stdio）| `mcp.<name>.type: "local"`, `command` 数组 | YAML 配置段 |
| **远程 MCP** | ✅ | ✅ | ✅ `type: "remote"`, `url` + `headers` | ✅ |
| **OAuth 自动注册** | ❌ 手动配置 | ❌ 手动配置 | ✅ **自动 RFC 7591 动态客户端注册** | ✅ |
| **按 Agent 启用** | ❌ 全局 | ❌ 全局 | ✅ `agent.<name>.tools` + glob 模式 | ✅ |
| **官方 marketplace** | ✅ 官方 + Anthropic 生态 | ❌ | ✅ Plugins 市场 + Sentry/Context7/Grep 示例 | ✅ Marketplaces 段 |

**MCP 配置代码示例对比**：

**Claude Code**：
```json
// .mcp.json（项目根）
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${env:GITHUB_TOKEN}" }
    }
  }
}
```

**Codex**：
```toml
# ~/.codex/config.toml
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "${env:GITHUB_TOKEN}" }

[mcp_servers.sentry]
url = "https://mcp.sentry.dev/mcp"
```

**OpenCode**（最完整）：
```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {},  // 自动 OAuth：检测 401 + 动态注册
      "enabled": true
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}" }
    },
    "gh_grep": {
      "type": "remote",
      "url": "https://mcp.grep.app"
    }
  },
  "tools": {
    "gh_*": false  // 全局禁用，按需启用
  },
  "agent": {
    "reviewer": {
      "tools": { "gh_*": true }  // 仅 reviewer agent 启用
    }
  }
}
```

**OMP**：
```yaml
# ~/.omp/agent/config.yml
mcp:
  servers:
    - name: github
      type: local
      command: ["npx", "-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_TOKEN: ${env:GITHUB_TOKEN}
    - name: sentry
      type: remote
      url: https://mcp.sentry.dev/mcp
```

---

## 五、4 大 Agent 运行模式横对比（重点）

> ⚠️ 这是 4 个 Coding Agent **架构差异最大**的维度。除了 Claude Code 有 3 档渐进权限模式、OMP 有 Build/Plan/Goal/Handoff/Session tree 五件套外，**Goal Mode、Handoff、Session tree 都是 OMP 独家**。

### 5.1 模式矩阵

| 模式 | [Claude Code](claude-code.md) | [Codex](codex.md) | [OpenCode](opencode.md) | [OMP](omp.md) |
|------|------------|-------|----------|-----|
| **Build（可编辑 + 执行）** | ✅ Default（手动批准）| ✅ 交互模式 | ✅ Build Mode（Tab 切）| ✅ Build（默认）|
| **Accept Edits（自动接受文件）** | ✅ Shift+Tab 2 档 | ❌ | ❌ | ❌ |
| **Plan Mode（只读规划）** | ✅ Shift+Tab 3 档 | ✅ 桌面端"计划模式" | ✅ 默认启动 + Tab 切 | ✅ `/plan` + per-role 模型 |
| **Goal Mode（长任务循环到 verifier）** | ❌ | ✅ 桌面端"追求目标" + `/goal` | ✅ oh-my-opencode ultrawork | ✅ `/goal` 内置 verifier |
| **Handoff（会话移交）** | ❌ | ❌ | ❌ | ✅ `/handoff` |
| **Session branch/fork/tree** | ❌ | ❌ | ❌ | ✅ git-like JSONL |
| **Bypass Permissions** | ✅ `--dangerously-skip-permissions` | ✅ `--approval-mode full-auto` | ✅ `permissions.ask: false` | ❌（dry by default）|

### 5.2 按模式选型决策树

```text
你需要哪种"自主程度"？
│
├─ "我要渐进式权限（Default → Accept Edits → Plan → Bypass）"
│   → Claude Code（Shift+Tab 平滑切换，独家）
│
├─ "我要最强 Goal Mode（长任务循环）+ Handoff + Session 分支"
│   → OMP（5 件套独家：/plan /goal /handoff /branch /fork）
│
├─ "我要 OpenAI 官方 + 命令/交互双模式 + 桌面端 Plan/Goal"
│   → Codex（命令模式 / 交互模式 / 桌面端 Plan+Goal）
│
└─ "我要最简明（Plan + Build Tab 切换）+ oh-my-opencode 多 Agent"
    → OpenCode（最简双模式 + ultrawork 多 Agent 插件）
```

### 5.3 模式组合最佳实践

| 任务类型 | 推荐 Agent + 模式组合 |
|---------|---------------------|
| **日常编码** | Claude Code Accept Edits 模式 / OMP Build / OpenCode Build |
| **架构设计** | Claude Code Plan Mode / OMP `/plan` / OpenCode Plan / Codex 桌面端 Plan |
| **批量重构** | Claude Code Bypass Permissions / OMP `/goal` / OpenCode ultrawork |
| **长任务自动化** | OMP `/goal`（独家）/ Codex 桌面端 Goal Mode |
| **多 Agent 流水线** | OMP `/handoff` / OpenCode ultrawork（Sisyphus 主 Agent + 4 子 Agent）|
| **跨会话继续** | OMP `/branch` `/fork` `/tree`（独家）|
| **CI/CD 自动化** | Claude Code `--dangerously-skip-permissions` / Codex `--approval-mode full-auto` |

### 5.4 模式维度对比小结

- **唯一 3 档渐进权限**：**Claude Code**（Default / Accept Edits / Plan）
- **唯一 Bypass 模式**：**Claude Code**（`--dangerously-skip-permissions`）
- **唯一命令/交互双模式**：**Codex**（命令模式一次性 + 交互模式长期）
- **唯一 Plan + Build Tab 切**：**OpenCode**（最简双模式）
- **唯一 Goal Mode + Handoff + Session tree 五件套**：**OMP**（`/plan` `/goal` `/handoff` `/branch` `/fork`）

> 📖 **每个 Agent 详细页的 §六"运行模式详解"** 含完整使用示例： [Claude Code](claude-code.md#六运行模式详解核心章节) · [Codex](codex.md#六运行模式详解核心章节) · [OpenCode](opencode.md#六运行模式详解核心章节) · [OMP](omp.md#六运行模式详解核心章节)

---

## 六、与 spec 工具的关系

```text
┌──────────────────────────────────────────────────────────┐
│  Layer 1: Coding Agent（本目录）                          │
│  Claude Code · Codex · OpenCode · OMP                   │
│  （4 大编程 Agent 的横对比 + 模型/MCP 配置）              │
├──────────────────────────────────────────────────────────┤
│  Layer 2: Agent Spec Tools（[../agent-spec-tools]）       │
│  Superpowers · Spec-Kit · OpenSpec                       │
│  （在 Agent 上跑的规范/工作流约束）                        │
├──────────────────────────────────────────────────────────┤
│  Layer 3: Harness Engineering（[../harness-engineering]） │
│  4 大 Harness 类型（规范/流程/工具/反馈）+ 4 原则          │
└──────────────────────────────────────────────────────────┘
```

**组合建议**：
- **Claude Code + Spec-Kit + Superpowers** = 企业 SDD 流程（最完整）
- **OpenCode + oh-my-opencode** = 多 Agent 自由编排（最灵活）
- **OMP + 自定义 Subagent** = 终端深度用户 + 长任务自动化

---

## 七、4 个 Coding Agent 速查

| 工具 | 详情 |
|------|------|
| **Claude Code** | [→ claude-code.md](claude-code.md) — 锁定 Anthropic · CLAUDE.md/Hooks/Skills/Plugins · `.mcp.json` |
| **Codex** | [→ codex.md](codex.md) — OpenAI 官方 · `wire_api`/`base_url` 兼容网关 · `config.toml` MCP |
| **OpenCode** | [→ opencode.md](opencode.md) — 75+ providers · oh-my-opencode 多 Agent · OAuth 自动注册 MCP |
| **OMP (oh my pi)** | [→ omp.md](omp.md) — 100k Rust LOC · Hashline · IRC bus · per-role 模型 · 进程内 LSP/DAP |

---

## 八、与其他章节的关系

- 规范层：[Agent Spec Tools](../agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec 三件套（**与本目录正交**）
- 单工具深度：[Claude Code Practices](../claude-code-practices/README.md) — Claude Code 单工具深度（CLAUDE.md / Skills / Hooks / Plugins）
- 概念层：[Harness Engineering](../harness-engineering/README.md) — 4 大 Harness 类型
- 循环层：[Loop Engineering](../loop-engineering/README.md) — Agent 循环调用 + Ralph Wiggum Loop
- 实战层：[Production Agent](../production-agent/README.md) — 生产环境的 Agent 工程实践
- 编码质量：[AI Code Review](../ai-code-review/README.md) — AI 生成代码审核验收方法论

---

## 📚 参考来源

| 资料 | 来源 | 一句话说明 |
|------|------|-----------|
| omp 官方主页 + docs | https://omp.sh / https://omp.sh/docs | 13 大特性 + per-role 模型 + 配置 schema |
| omp GitHub | https://github.com/can1357/oh-my-pi | 17.7k stars, MIT 协议 |
| OpenCode 官方 docs | https://opencode.ai/zh/docs/providers + /mcp-servers | 75+ providers 配置 + OAuth 自动注册 |
| OpenCode GitHub | https://github.com/anomalyco/opencode | 160k stars, Apache 2.0 |
| Codex 官方 | https://github.com/openai/codex + 知乎/菜鸟教程 | wire_api + base_url 配置示例 |
| Claude Code 官方博客 | https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start | Harness 5 扩展点 |

---

← [返回: L3 工程实践](../README.md)