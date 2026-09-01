<!--
module:
  parent: ai
  slug: ai/coding-agents/opencode
  type: article
  category: 主模块子文章
  summary: OpenCode 速查版：开源 + 75+ providers + oh-my-opencode 多 Agent + MCP OAuth 自动 RFC 7591 注册。
  depth: ⭐⭐⭐
-->

# OpenCode — 开源跨平台编程 Agent（速查版）

← 返回 [Coding Agents 对比](README.md) · [工程实践](../README.md)

> Anomaly 出品，**GitHub 160K+ stars · MIT 协议**。**4 个 Coding Agent 中 provider 数量最多**（75+）+ **唯一支持 MCP OAuth 自动 RFC 7591 动态注册**。配套 **oh-my-opencode** 多 Agent 框架（Sisyphus / Oracle / Librarian / Frontend Engineer / Explore）。

---

## 一、TL;DR

| 维度 | 内容 |
|------|------|
| **定位** | 开源跨平台编程 Agent，75+ providers + 多 Agent 编排 |
| **协议 / 平台** | MIT / macOS + Linux + Windows（**推荐 WSL**）|
| **GitHub Stars** | **160K+**（[anomalyco/opencode](https://github.com/anomalyco/opencode)）|
| **安装** | `curl -fsSL https://opencode.ai/install \| bash` / npm / brew / mise |
| **模型** | ✅ **75+ providers**（Anthropic / OpenAI / DeepSeek / Ollama / Bedrock / Vertex…）+ 自定义 |
| **MCP** | ✅ `opencode.jsonc` + **OAuth 自动 RFC 7591 动态客户端注册** |
| **杀手特性** | 75+ providers + oh-my-opencode 多 Agent + MCP OAuth 自动注册 + Zen 精选模型 |
| **适合谁** | 想用任意 LLM + 多 Agent 编排 + 需要灵活 Provider |

---

## 二、安装

### 2.1 一键安装脚本（推荐）

```bash
curl -fsSL https://opencode.ai/install | bash
opencode --version  # 验证（输出类似 1.1.x）
```

### 2.2 NPM / Bun

```bash
npm install -g opencode-ai
# 或
bun install -g opencode-ai
```

### 2.3 包管理器

```bash
# macOS / Linux
brew install anomalyco/tap/opencode   # 推荐（最新版）
# 或 brew install opencode           # 官方（更新慢）

# Arch Linux
sudo pacman -S opencode               # 稳定版
paru -S opencode-bin                  # AUR 最新版

# Windows
choco install opencode
# 或 scoop install opencode

# Docker
docker run -it --rm ghcr.io/anomalyco/opencode
```

### 2.4 启动

```bash
cd /path/to/your/project
opencode                # 启动 TUI
opencode -p "修复 login bug"  # 非交互模式
opencode --cwd ~/my-app # 指定工作目录
```

---

## 三、CLI 核心命令

| 命令 | 作用 |
|------|------|
| `opencode` | 启动 TUI |
| `opencode -p "任务"` | 非交互模式 |
| `/init` | 生成项目 AGENTS.md |
| `/connect` | 配置 Provider API Key |
| `/models` | 切换模型 |
| `/share` | 分享当前会话（生成链接）|
| `/undo` / `/redo` | 撤销 / 重做（Git 仓库） |
| `/compact` | 压缩上下文 |
| `/sessions` | 列出 / 切换会话 |
| `/exit` | 退出 |

**两种 Agent 模式**：
- **Build**（默认）：全权限，可编辑 + 执行
- **Plan**：只读规划，Tab 键切换，需确认才执行

---

## 四、自定义模型配置（核心章节）

> ⚠️ **OpenCode 是 4 个 Coding Agent 中 provider 最多的**（75+），支持任意 OpenAI 兼容端点 + 自定义 Provider。

### 4.1 配置文件位置

```text
~/.local/share/opencode/
├── auth.json                 # API Key 凭据（所有 provider）
└── mcp-auth.json             # OAuth Token 凭据（远程 MCP）

<项目根>/
└── opencode.jsonc            # 主配置（provider / mcp / tools / agent）
```

### 4.2 OpenCode Zen（官方推荐入门）

OpenCode Zen 是官方精选模型集合（已测试验证），适合新用户：

```bash
# TUI 中
/connect
# 选择 "opencode" 选项
# 浏览器跳转到 opencode.ai/auth
# 登录 + 添加账单 + 复制 API Key
# 粘贴回终端
```

### 4.3 配置 75+ Provider

```bash
# 任意 Provider 通用流程
/connect
# 搜索 provider 名（DeepSeek / Groq / Cerebras / OpenAI / Anthropic…）
# 输入 API Key
```

**已内置 Provider**（不完整列表）：

| 类别 | Provider |
|------|----------|
| 商业主力 | Anthropic, OpenAI, Google Vertex AI, Amazon Bedrock |
| 国内 | DeepSeek, Moonshot AI, Z.AI, MiniMax |
| 聚合 | OpenRouter, Vercel AI Gateway, Cloudflare AI Gateway |
| 企业 | Azure OpenAI, SAP AI Core, OVHcloud, STACKIT, Scaleway |
| 性能 | Groq, Cerebras, Together AI, Fireworks AI |
| 开源/本地 | Ollama, Ollama Cloud, LM Studio, llama.cpp |
| 订阅 | GitHub Copilot, GitLab Duo, Cursor, Hugging Face |

### 4.4 自定义 Base URL

```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"  // 可改向代理
      }
    },
    "openai": {
      "options": {
        "baseURL": "https://your-openai-compatible-gateway.com/v1"
      }
    }
  }
}
```

### 4.5 自定义 Provider（任意 OpenAI 兼容端点）

```jsonc
// opencode.jsonc —— 完全自定义 Provider
{
  "provider": {
    "my-custom-provider": {
      "npm": "@ai-sdk/openai-compatible",       // 用 OpenAI 兼容 SDK
      "name": "My Custom Provider",
      "options": {
        "baseURL": "http://127.0.0.1:1337/v1"  // 本地 Atomic Chat 等
      },
      "models": {
        "<model-id-from-/v1/models>": {
          "name": "<display-name>"
        }
      }
    }
  }
}
```

### 4.6 多角色模型（小模型）

```jsonc
// opencode.jsonc —— 单独配置小模型
{
  "small_model": "anthropic/claude-haiku-4-5",   // 用于标题生成等小任务
  "provider": { ... }
}
```

OpenCode 用 `small_model` 字段配置小模型（用于标题生成、文件名建议等），主对话仍用 `/models` 选择。比 OMP 的 4 角色简单。

### 4.7 Amazon Bedrock / Vertex AI（企业级）

```jsonc
// opencode.jsonc
{
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile"           // ~/.aws/credentials
      }
    }
  }
}
// 也支持环境变量：AWS_BEARER_TOKEN_BEDROCK / AWS_PROFILE / GOOGLE_APPLICATION_CREDENTIALS
```

---

## 五、MCP 配置（核心章节）

> ⚠️ **OpenCode 是 4 个 Coding Agent 中唯一支持 MCP OAuth 自动 RFC 7591 动态注册**的 —— 检测到 401 自动启动 OAuth 流程 + 动态注册客户端 + 安全存储 Token。

### 5.1 配置文件

```jsonc
// opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "<server-name>": {
      "type": "local" | "remote",
      // ...其他字段
      "enabled": true
    }
  }
}
```

### 5.2 本地 stdio MCP

```jsonc
// opencode.jsonc
{
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      },
      "enabled": true,
      "timeout": 5000
    },
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    }
  }
}
```

### 5.3 远程 MCP（OAuth 自动检测）

```jsonc
// opencode.jsonc
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {},          // 空对象 = 启用自动 OAuth 检测
      "enabled": true
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

**OAuth 自动流程**（无需手动配置）：
1. Agent 调用 MCP 服务器遇到 401
2. 自动启动 OAuth 流程（打开浏览器）
3. 动态客户端注册（RFC 7591）—— 无需提前申请 client_id
4. Token 安全存储到 `~/.local/share/opencode/mcp-auth.json`

### 5.4 MCP 启用粒度（per-agent + glob）

```jsonc
// opencode.jsonc
{
  "mcp": {
    "my-mcp-foo": { "type": "local", "command": ["bun", "x", "my-mcp-foo"] },
    "my-mcp-bar": { "type": "local", "command": ["bun", "x", "my-mcp-bar"] }
  },
  "tools": {
    "my-mcp*": false        // 全局禁用所有 MCP（glob 模式）
  },
  "agent": {
    "reviewer": {
      "tools": {
        "my-mcp*": true     // 仅 reviewer agent 启用
      }
    }
  }
}
```

### 5.5 MCP 管理命令

```bash
opencode mcp list               # 列出所有 MCP + 认证状态
opencode mcp auth <name>        # 触发 OAuth 授权
opencode mcp logout <name>      # 删除 Token
opencode mcp debug <name>       # 调试连接 + OAuth 流程
```

### 5.6 官方 MCP 示例（Sentry / Context7 / Grep）

**Sentry**（错误监控）：
```jsonc
{ "mcp": { "sentry": { "type": "remote", "url": "https://mcp.sentry.dev/mcp", "oauth": {} } } }
# 用法：use sentry / Show me the latest unresolved issues
```

**Context7**（实时文档）：
```jsonc
{ "mcp": { "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp" } } }
# 用法：use context7 / search React Server Components docs
```

**Grep by Vercel**（GitHub 代码搜索）：
```jsonc
{ "mcp": { "gh_grep": { "type": "remote", "url": "https://mcp.grep.app" } } }
# 用法：use the gh_grep tool
```

### 5.7 OpenCode MCP 字段速查

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `"local"` \| `"remote"` | ✅ | 连接类型 |
| `command` | string[] | 本地 | 启动命令 + 参数 |
| `environment` | object | ❌ | 环境变量 |
| `url` | string | 远程 | MCP URL |
| `headers` | object | ❌ | HTTP 头 |
| `oauth` | object \| false | ❌ | OAuth 配置（或 false 禁用）|
| `enabled` | boolean | ❌ | 启动时启用 |
| `timeout` | number | ❌ | 获取工具超时（默认 5000ms）|

---

## 六、运行模式详解（核心章节）

> OpenCode 是 4 大 Agent 中**模式最简明**的 —— 仅 Plan / Build 两种模式，Tab 键一键切换。配合 oh-my-opencode 的 ultrawork 关键词实现多 Agent 协作。

### 6.1 Plan Mode（默认启动）

**功能**：不直接修改代码，只输出**自然语言形式的实施计划**。**架构师视角**。

**触发方式**：
```bash
$ opencode
# 默认进入 Plan Mode
> 在终端输入需求后，agent 分析 @src 中的文件，提出修改建议
# 不会立即修改文件

# 反复修正计划
> 继续对话修正，直到 Plan 完美
```

**适用场景**：
- 探索不熟悉的代码库
- 架构设计、项目方案讨论
- 重大改动前的计划确认

### 6.2 Build Mode（工程师视角）

**功能**：基于 Plan 阶段确定的路径，**执行具体的代码编写与文件修改**。

**触发方式**：
```bash
$ opencode
# 默认在 Plan Mode，按 Tab 键切到 Build Mode
# 状态栏右下角显示 "Build"

> 确认计划无误后，按下 Tab 键或输入 /build，将上下文切换至执行状态
# 上下文切换至执行状态

# agent 开始生成 Diff 并写入文件
```

**适用场景**：
- 已批准计划后的执行
- 日常编码、改 Bug
- 批量文件修改

### 6.3 标准 3 步工作流（SOP）

为了最大化 AI 的逻辑准确性，OpenCode 推荐"**三步走**"工作流：

```text
启动与规划（Plan）→ 模式切换（Tab → Build）→ 代码落地（Build）
```

**操作技巧**：
- 若发现 AI 理解有误，**继续在 Plan 模式对话修正**，直到 Plan 完美
- Plan 完美后才切到 Build，避免改完又回滚

### 6.4 oh-my-opencode ultrawork（多 Agent 模式）

OpenCode 配套 **oh-my-opencode** 插件，提供类似 Goal Mode 的多 Agent 自动化：

```bash
# 安装 oh-my-opencode（让 OpenCode 自动完成）
> 按照以下说明安装和配置 oh-my-opencode：
  https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/docs/guide/installation.md

# 用 ultrawork 关键词触发完整多 Agent 自动化
> ultrawork: 帮我实现一个 React 组件，支持暗黑模式

# 或简写
> ulw: 把整个项目迁移到 TypeScript
```

**与 Goal Mode 区别**：

| 维度 | OMP Goal Mode | OpenCode ultrawork |
|------|---------------|---------------------|
| 触发命令 | `/goal` | `ultrawork` / `ulw` 关键词 |
| 模式 | 内置 run mode | oh-my-opencode 插件 |
| Agent 派发 | 手动（subagent IRC bus）| 自动（Sisyphus 主 Agent + Oracle/Librarian/Frontend/Explore）|
| 多模型调度 | per-role 4 模型 | 自动分配（Gemini 前端 + Claude 规划）|

### 6.5 OpenCode 模式对比

| 模式 | 是否修改文件 | 切换方式 | 适用 |
|------|------------|---------|------|
| **Plan**（默认）| ❌ | 默认 | 探索、计划 |
| **Build** | ✅ | Tab 键或 `/build` | 执行、修改 |
| **ultrawork** | ✅（多 Agent 自动）| 关键词触发 | 复杂任务自动化 |

---

## 七、oh-my-opencode（多 Agent 插件）

**oh-my-opencode**（[code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)）是 OpenCode 的多 Agent 插件，**把单个 Agent 升级为多 Agent 协作团队**：

| Agent | 职责 |
|-------|------|
| **Sisyphus** | 主 Agent，持续执行复杂任务至完成 |
| **Oracle** | 战略规划、架构决策 |
| **Librarian** | 文档专家、代码搜索 |
| **Frontend Engineer** | 前端开发（自动分配 Gemini）|
| **Explore** | 探索代码库 |
| **…** | 更多专业 Agent |

**激活方式**：在 prompt 中用 `ultrawork`（或简写 `ulw`）关键词：
```text
ultrawork: 帮我实现一个 React 组件，支持暗黑模式
```

oh-my-opencode 会自动分配任务给最适合的 Agent（Gemini 处理前端、Claude 处理规划），并行执行（后台映射代码库、深度探索、自动重构），直至 100% 完成。

---

## 八、与其他 3 个 Agent 的差异

| 维度 | OpenCode 优势 | OpenCode 劣势 |
|------|--------------|--------------|
| **vs Claude Code** | ✅ 75+ providers · ✅ oh-my-opencode 多 Agent · ✅ MCP OAuth 自动注册 | ❌ 缺 CLAUDE.md/Skills 生态 · ❌ 无官方 marketplace 深度 |
| **vs Codex** | ✅ 75+ providers · ✅ oh-my-opencode 多 Agent · ✅ MCP OAuth 自动注册 | ❌ 无 GPT-5 顶级代码 · ❌ 无云端并行沙盒 · ❌ 无 IDE 三形态 |
| **vs OMP** | ✅ 75+ providers（比 OMP 多）· ✅ oh-my-opencode 多 Agent · ✅ WSL/非 WSL 都可 | ❌ 无 per-role 多模型 · ❌ Windows 推荐 WSL · ❌ 无 DAP · ❌ 非 Rust 原生 |

---

## 九、适用场景

- ✅ **多 LLM 策略**：想根据任务切换 Claude / GPT / DeepSeek / Ollama
- ✅ **多 Agent 协作**：需要 Sisyphus / Oracle / Frontend Engineer 等专业 Agent 分工
- ✅ **OAuth 远程 MCP**：希望 MCP OAuth 自动处理（不手动配置 Token）
- ✅ **本地模型 + 云端混合**：用 Ollama 跑本地 + OpenAI/Claude 处理云端
- ✅ **企业级 Bedrock / Vertex**：AWS / GCP 内部部署

**不适合**：
- ❌ 想要 GPT-5.3 Codex 顶级代码（用 Codex）
- ❌ 想要 Anthropic 官方 Harness 生态（用 Claude Code）
- ❌ 想要 per-role 4 模型分工（用 OMP）
- ❌ Windows 原生体验（OMP 更好）

---

## 十、相关章节

- **横向对比**：[Coding Agents README](README.md)
- **Harness 概念**：Harness Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../../agent-execution-patterns/harness-engineering/]`）
- **循环调用**：Loop Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../../agent-execution-patterns/loop-engineering/]`）
- **本地部署**：Local Deployment（⚠️ 待 Phase 1+ 迁入；占位 `./local-deployment/README.md`） — Ollama 与 OpenCode 集成
- **规范工具**：[Agent Spec Tools](../agent-spec-tools/README.md)

← [返回: Coding Agents 对比](README.md)

## 📚 参考来源

1. **官方文档**：Anthropic. *Claude Code Best Practices*（开源 Coding Agent 通用方法论参考）. 2025. https://www.anthropic.com/engineering/claude-code-best-practices
2. **SWE-bench 评测**：Jimenez et al. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024. https://arxiv.org/abs/2310.06770
3. **Agentless 框架**：Xia, Deng. *Agentless: Demystifying LLM-based Software Engineering Agents*. 2024. https://arxiv.org/abs/2407.01489
