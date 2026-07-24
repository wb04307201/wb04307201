<!--
module:
  parent: ai
  slug: ai/coding-agents/claude-code
  type: article
  category: 主模块子文章
  summary: Claude Code 速查版：Anthropic 官方 + 锁定 Claude 模型 + CLAUDE.md/Hooks/Skills/Plugins/LSP 五大 Harness 扩展点 + .mcp.json 配置。
-->

# Claude Code — Anthropic 官方编程 Agent（速查版）

← 返回 [Coding Agents 对比](README.md) · [工程实践](../README.md)

> Anthropic 官方 CLI（商业闭源）。**唯一锁定单一提供商**的 Coding Agent —— 只能用 Claude 模型，但换来 5 大 Harness 扩展点（CLAUDE.md / Hooks / Skills / Plugins / LSP / MCP）最成熟的生态。

> 📖 **深度版**：Claude Code 的 Harness 5 大扩展点完整细节见 [Claude Code Practices](../claude-code-practices/README.md)（112 行深度文）。本篇聚焦速查 + 模型/MCP 配置 + 与其他 agent 对比。

---

## 一、TL;DR

| 维度 | 内容 |
|------|------|
| **定位** | Anthropic 官方终端编程 Agent，Harness 生态最成熟 |
| **协议 / 平台** | 商业 / macOS + Linux + Windows |
| **安装** | `npm install -g @anthropic-ai/claude-code` 或官方桌面 App |
| **模型** | 🔒 **锁定 Anthropic Claude 系列**（Opus 4.5 / Sonnet 4.5 / Haiku 4.5）|
| **MCP** | ✅ `.mcp.json`（项目级）+ `~/.claude.json`（全局）+ `--mcp-config` 参数 |
| **杀手特性** | 5 大 Harness 扩展点 + Subagents + LSP 集成 + 官方 Skill marketplace |
| **适合谁** | 已在 Anthropic 生态、追求代码质量、需要成熟工具链 |

---

## 二、安装

### 2.1 NPM 安装（推荐）

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # 验证
```

### 2.2 桌面 App

```bash
# macOS / Windows / Linux 均可
# 从 https://claude.com/download 下载
```

### 2.3 启动

```bash
cd /path/to/your/project
claude                 # 启动交互式 TUI
claude -p "修复 login 函数 bug"  # 非交互模式
```

---

## 三、CLI 核心命令

| 命令 | 作用 |
|------|------|
| `claude` | 启动 TUI |
| `claude -p "任务"` | 非交互模式（CI 用） |
| `/init` | 扫描项目生成 CLAUDE.md |
| `/agents` | 管理 Subagents |
| `/mcp` | 查看 MCP 连接状态 |
| `/memory` | 编辑 CLAUDE.md |
| `/compact` | 压缩上下文 |
| `/clear` | 清空当前会话 |
| `/model opus/sonnet/haiku` | 切换模型（在 3 个 Claude 模型间）|

---

## 四、自定义模型配置（核心章节）

> ⚠️ **Claude Code 是 4 个 Coding Agent 中唯一锁定单一提供商的** —— 不能用 OpenAI / DeepSeek / Ollama 等其他模型。这是为换取官方生态深度做出的取舍。

### 4.1 配置位置

```text
~/.claude/
├── settings.json       # 全局配置
├── .mcp.json           # 全局 MCP
└── ...

<项目根>/
├── .claude/
│   ├── settings.json   # 项目级配置（覆盖全局）
│   ├── CLAUDE.md       # 自动加载的上下文（每次会话读取）
│   └── skills/         # 项目级 Skill
└── .mcp.json           # 项目级 MCP
```

### 4.2 配置文件

```json
// ~/.claude/settings.json
{
  "model": "claude-sonnet-4-5",
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-..."
  },
  "permissions": {
    "allow": ["Bash", "Edit", "Read"],
    "deny": ["WebFetch"]
  },
  "mcpServers": {}  // 也可在此定义 MCP（见下）
}
```

### 4.3 API Key vs OAuth

```bash
# 方式 1: API Key（推荐用于 CI/CD）
export ANTHROPIC_API_KEY="sk-ant-..."
claude

# 方式 2: OAuth Pro/Max（个人订阅）
claude  # 首次启动弹出浏览器登录 Claude Pro/Max
```

### 4.4 多角色模型

❌ **不支持 per-role 模型**。Claude Code 只用单一模型（除非运行时 `/model` 切换）。

**理由**：Anthropic 把所有任务（标题生成 / 深度推理 / 工具调用）都交给 Claude 同一模型族，省去 per-role 调度的复杂度。如果需要 per-role，换 OMP。

### 4.5 切换模型（运行时）

```bash
# TUI 中实时切换
/model opus        # Claude Opus 4.5（最强大）
/model sonnet      # Claude Sonnet 4.5（默认，平衡）
/model haiku       # Claude Haiku 4.5（最快最便宜）
```

---

## 五、MCP 配置（核心章节）

### 5.1 配置文件

```text
项目级（推荐）：<项目根>/.mcp.json
全局级：       ~/.claude.json  或  ~/.claude/.mcp.json
启动覆盖：     --mcp-config <file>
```

### 5.2 基础 MCP 配置（项目级）

```json
// .mcp.json（项目根目录）
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    }
  }
}
```

### 5.3 远程 MCP + OAuth

```json
// .mcp.json
{
  "mcpServers": {
    "sentry": {
      "url": "https://mcp.sentry.dev/mcp",
      "auth": {
        "type": "oauth"
      }
    },
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

### 5.4 启动时指定 MCP 配置

```bash
claude --mcp-config /path/to/custom-mcp.json
```

### 5.5 Claude Code MCP 特性

| 特性 | 支持 |
|------|------|
| 本地 stdio MCP | ✅ |
| 远程 HTTP MCP | ✅ |
| OAuth 自动检测 | ✅（手动触发） |
| 按 Agent 启用 | ❌ 全局生效 |
| RFC 7591 动态客户端注册 | ❌ 手动配置 |

> 对比：OpenCode 的 MCP OAuth 自动 RFC 7591 注册比 Claude Code 自动化程度高。

### 5.6 官方 MCP Marketplace

Claude Code 有官方 **Plugin marketplace**，包含：

- 官方插件：github、filesystem、postgres、sqlite、puppeteer…
- 社区插件：sentry、linear、notion、slack…

通过 `/plugin marketplace` 浏览，`/plugin install <name>` 安装。

---

## 六、5 大 Harness 扩展点（速览）

> 深度版见 [Claude Code Practices](../claude-code-practices/README.md)

| # | 扩展点 | 是什么 | 何时加载 |
|---|--------|--------|----------|
| 1 | **CLAUDE.md** | 自动读取的上下文文件 | 每次会话 |
| 2 | **Hooks** | 关键时刻运行的脚本 | 事件触发 |
| 3 | **Skills** | 特定任务的打包指令 | 按需加载 |
| 4 | **Plugins** | skills/hooks/MCP 打包 | 配置后可用 |
| 5 | **LSP** | 语言服务器（符号级导航）| 配置后可用 |
| ⊕ | **Subagents** | 独立上下文窗口的子 Claude 实例 | 调用时 |
| ⊕ | **MCP** | 外部工具 / 数据源 | 配置后可用 |

---

## 七、与其他 3 个 Agent 的差异

| 维度 | Claude Code 优势 | Claude Code 劣势 |
|------|----------------|----------------|
| **vs OMP** | ✅ Harness 5 扩展点最成熟 · ✅ 官方 Skill marketplace · ✅ LSP 集成开箱 | ❌ 锁定 Anthropic · ❌ 无 per-role 模型 · ❌ 无 DAP |
| **vs Codex** | ✅ 多 provider 路径（CLAUDE.md/Hooks/Skills/Plugins）· ✅ MCP 生态更丰富 | ❌ 不能用 GPT-5 · ❌ 无云端并行沙盒 |
| **vs OpenCode** | ✅ 官方背书 · ✅ 文档最全 · ✅ 5 大 Harness 文档化最好 | ❌ 不能用 75+ providers · ❌ 无 OAuth 自动注册 |

---

## 八、适用场景

- ✅ **Anthropic 生态**：Claude Pro/Max / API 订阅已有，想深度用
- ✅ **大代码库 monorepo**：5 大 Harness 扩展点针对此优化（LSP + Skills + CLAUDE.md 分层）
- ✅ **团队标准化**：需要 Skills + Plugins 在团队内分发
- ✅ **配合 Spec-Kit / Superpowers**：Agent + 规范工具组合最完整
- ✅ **企业级 SDD**：GitHub Spec-Kit 35 集成原生兼容 Claude Code

**不适合**：
- ❌ 想用 GPT-5 / DeepSeek / Ollama（用 Codex / OpenCode / OMP）
- ❌ Windows 原生体验（OMP 更优）
- ❌ 需要 Subagent IRC bus 直 DM（OMP 优势）

---

## 九、相关章节

- **深度版**：[Claude Code Practices](../claude-code-practices/README.md) — Harness 5 扩展点 + 3 大部署模式 + DRI 治理
- **Skill 设计**：[Skill 设计方法论](../claude-code-practices/skill-design.md) / [Skill 命中率](../claude-code-practices/skill-hit-rate.md)
- **横向对比**：[Coding Agents README](README.md)
- **规范工具**：[Agent Spec Tools](../agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec（Claude Code 是这 3 工具的主要载体）
- **Harness 概念**：[Harness Engineering](../harness-engineering/README.md) — Claude Code 5 扩展点都是 Harness 实现
- **代码审核**：[AI Code Review](../ai-code-review/README.md) — Claude Code 生成的代码怎么审核

← [返回: Coding Agents 对比](README.md)