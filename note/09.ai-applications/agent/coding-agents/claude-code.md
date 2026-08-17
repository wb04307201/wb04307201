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

> 📖 **深度版**：Claude Code 的 Harness 5 大扩展点完整细节见 Claude Code Practices（⚠️ 待 Phase 1+ 迁入；占位 `./claude-code-practices/README.md`）（112 行深度文）。本篇聚焦速查 + 模型/MCP 配置 + 与其他 agent 对比。

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

## 六、运行模式详解（核心章节）

> Claude Code 是 4 大 Agent 中**唯一有 3 档渐进式权限模式**的 —— Shift+Tab 在 Default / Accept Edits / Plan Mode 间平滑循环。锁定 Anthropic 模型换来官方生态深度。

### 6.1 Default Mode（手动批准）

**功能**：每次文件编辑、命令执行前都需要你手动批准（Y/N/跳过）。**最安全、最谨慎**。

**触发方式**：
```bash
# 启动时默认就是 Default Mode
$ claude
> 帮我分析这个项目结构
# 每次 Edit / Write / Bash 都会弹确认：
#   Yes, and auto-accept edits
#   Yes, and manually approve edits
#   No, and provide feedback
```

**适用场景**：
- 学习阶段、不熟悉的项目
- 重要 / 敏感修改
- 需要精细控制

### 6.2 Accept Edits Mode（自动接受文件）

**功能**：自动接受所有文件读写修改，但 Shell 命令仍需手动批准。**效率高，适合批量生成**。

**触发方式**：
```bash
# Shift+Tab 循环切换：normal → accept edits → plan → normal
$ claude
# 按 Shift+Tab 一次，状态栏变 "accept edits on"
> 把整个 src/ 目录重构为 TypeScript
# 文件编辑自动接受，但 npm install / npm test 还会问
```

**适用场景**：
- 信任 AI 的日常开发
- 批量生成 / 修改代码
- 写测试、生成样板代码

### 6.3 Plan Mode（只读规划）

**功能**：只读、只讨论，不修改任何文件、不执行任何命令。**完全保护代码，只做头脑风暴**。

**触发方式**：
```bash
# Shift+Tab 循环到第 3 档 "plan mode on"
$ claude
# 按 Shift+Tab 两次
> 设计一个 Redis 缓存层架构
# Claude 只输出方案、代码示例、架构分析，不动文件

# 退出 Plan Mode 后可选：
#   ✓ Yes, and auto-accept edits → 直接执行
#   ✓ Yes, and manually approve edits → 执行但保留审批
#   ✎ Type here to tell Claude what to change → 修改方案
```

**适用场景**：
- 架构设计、项目方案讨论
- 复杂功能开发、数据库迁移
- 生产级关键文件变更

### 6.4 Bypass Permissions（黑客模式）

**功能**：完全跳过所有权限检查。**所有命令直接执行**。

**触发方式**：
```bash
# CLI 启动时
$ claude --dangerously-skip-permissions

# 或在交互模式中 Shift+Tab 到 "bypass permissions on"
```

**适用场景**：
- 完全自动化的 CI/CD 管道
- 容器环境（沙盒已隔离）
- ⚠️ **危险**：生产环境绝对不要用

### 6.5 Claude Code 模式对比

| 模式 | 文件编辑 | 命令执行 | 适用场景 |
|------|---------|---------|---------|
| **Default** | 每次 ask | 每次 ask | 学习、精细控制 |
| **Accept Edits** | 自动 | 每次 ask | 批量生成、信任 AI |
| **Plan Mode** | ❌ 不执行 | ❌ 不执行 | 架构设计、只讨论 |
| **Bypass** | 自动 | 自动 | CI/CD、容器沙盒 |

---

## 七、5 大 Harness 扩展点（速览）

| 维度 | Claude Code 优势 | Claude Code 劣势 |
|------|----------------|----------------|
| **vs OMP** | ✅ Harness 5 扩展点最成熟 · ✅ 官方 Skill marketplace · ✅ LSP 集成开箱 | ❌ 锁定 Anthropic · ❌ 无 per-role 模型 · ❌ 无 DAP |
| **vs Codex** | ✅ 多 provider 路径（CLAUDE.md/Hooks/Skills/Plugins）· ✅ MCP 生态更丰富 | ❌ 不能用 GPT-5 · ❌ 无云端并行沙盒 |
| **vs OpenCode** | ✅ 官方背书 · ✅ 文档最全 · ✅ 5 大 Harness 文档化最好 | ❌ 不能用 75+ providers · ❌ 无 OAuth 自动注册 |

---

## 八、与其他 3 个 Agent 的差异

| 维度 | Claude Code 优势 | Claude Code 劣势 |
|------|----------------|----------------|
| **vs OMP** | ✅ Harness 5 扩展点最成熟 · ✅ 官方 Skill marketplace · ✅ LSP 集成开箱 | ❌ 锁定 Anthropic · ❌ 无 per-role 模型 · ❌ 无 DAP |
| **vs Codex** | ✅ 多 provider 路径（CLAUDE.md/Hooks/Skills/Plugins）· ✅ MCP 生态更丰富 | ❌ 不能用 GPT-5 · ❌ 无云端并行沙盒 |
| **vs OpenCode** | ✅ 官方背书 · ✅ 文档最全 · ✅ 5 大 Harness 文档化最好 | ❌ 不能用 75+ providers · ❌ 无 OAuth 自动注册 |

---

## 九、适用场景

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

## 十、相关章节

- **深度版**：Claude Code Practices（⚠️ 待 Phase 1+ 迁入；占位 `./claude-code-practices/README.md`） — Harness 5 扩展点 + 3 大部署模式 + DRI 治理
- **Skill 设计**：Skill 设计方法论 / Skill 命中率（⚠️ 待 Phase 1+ 迁入；占位 `./claude-code-practices/skill-design.md` / `./claude-code-practices/skill-hit-rate.md`）
- **横向对比**：[Coding Agents README](README.md)
- **规范工具**：[Agent Spec Tools](../agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec（Claude Code 是这 3 工具的主要载体）
- **Harness 概念**：Harness Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../../agent-execution-patterns/harness-engineering/]`） — Claude Code 5 扩展点都是 Harness 实现
- **代码审核**：AI Code Review（⚠️ 待 Phase 1+ 迁入；占位 `./ai-code-review/README.md`） — Claude Code 生成的代码怎么审核

← [返回: Coding Agents 对比](README.md)