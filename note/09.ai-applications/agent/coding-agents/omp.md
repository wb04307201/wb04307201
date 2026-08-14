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

## 六、运行模式详解（核心章节）

> OMP 是 4 大 Coding Agent 中**唯一同时拥有 Build / Plan / Goal / Handoff + Session tree 五件套**的。模式间通过斜杠命令切换，会话可跨模式分支保留。

### 6.1 Build Mode（默认）

**功能**：正常对话 + 编辑文件 + 执行命令 + 调所有 32 内置工具。**全权限**模式。

**触发方式**：
```bash
$ omp                 # 不加任何参数，默认 Build 模式
> 帮我重构 src/auth.ts 里所有 JWT 验证逻辑

# 非交互模式（CI/脚本用）
$ omp -p "在当前项目加一个 /api/v2/users 接口"
# 输出结果后退出
```

**权限行为**：
- 文件编辑：Bash / Edit / Write 默认 ask（需用户批准）
- 网络请求：默认 allow
- Subagent 派发：默认 allow

### 6.2 Plan Mode（沙盒规划）

**功能**：把规划回合**隔离**到独立 planner 模型（config.yml 里 `models.plan`），**不修改任何文件**。用户审批后才执行。

**触发方式**：
```bash
$ omp
> /plan 我想给项目加 GraphQL 支持
# omp 切到 Plan Mode，问 planner 模型（默认 Claude Opus 4.5）
# 输出完整计划（不动文件）
# 等待你审批：
>   ✓ Approve and execute
>   ✗ Reject and revise
>   ✎ Edit the plan

# CLI 模式直接规划
$ omp -p --plan "把 Express 迁移到 Fastify"
```

**三种审批选项**：
1. **Execute and purge** — 执行规划，然后清空 plan transcript
2. **Keep transcript** — 执行规划，保留 transcript 作为上下文
3. **Compact context** — 执行规划 + 压缩当前上下文

**与其他 Agent 的 Plan 差异**：
| Agent | Plan Mode 行为 |
|-------|---------------|
| Claude Code | Shift+Tab 切；用同一个模型；审批选项 3 档 |
| Codex | 桌面端有"计划模式"；CLI 用 `--approval-mode` 模拟 |
| OpenCode | 默认 Plan；Tab 切到 Build；用同一个模型 |
| **OMP** | **`/plan` 触发；per-role planner 模型（独立配置）；3 档审批** |

**适用场景**：重大重构前 / 多文件改动前 / 探索性任务（先想清楚再动手）

### 6.3 Goal Mode（目标模式 / 长任务循环）

**功能**：长任务自动化 —— 把"目标"丢给 agent，**循环执行直到 verifier 通过**。类似 Ralph Wiggum Loop 的 Fresh Context 循环，但 goal mode 用同一个会话。

**触发方式**：
```bash
$ omp
> /goal 把这个项目的所有 TODO 解决掉，并确保 npm test 全绿
# omp 进入 Goal Mode：
#   1. 扫描所有 TODO
#   2. 规划修复顺序
#   3. 逐个修复 + 跑测试
#   4. 如果失败 → 重试（受 max_iterations 限制）
#   5. 所有 TODO 解决 + 测试通过 → Done
```

**核心机制**：
- 自动 Verifier（默认 `npm test` / 用户自定义命令）
- 失败时反馈错误信息给 agent 重试
- 支持 `max_iterations` / `max_duration` 终止条件
- 与 Subagent IRC bus 协作（子 agent 报告进度）

**适用场景**：
- "清空所有 TODO"
- "把所有测试补到 80% 覆盖"
- "迁移整个项目到 TypeScript"
- "修复所有 lint 错误"

### 6.4 Handoff（会话移交）

**功能**：把当前会话**移交**给另一个角色（agent 模式 / subagent / 人类协作者），保留上下文。

**触发方式**：
```bash
# Agent → Agent 移交（接力）
> /handoff code-reviewer
# 当前 session 状态发给 code-reviewer subagent
# reviewer 接手审查刚才写的代码

# Agent → 人 移交（暂停 + 等人类介入）
> /handoff @teammate
# 生成可分享链接（用 /collab）
# 人类在浏览器接管

# Agent → Subagent 移交（任务分发）
> /handoff explorer "找一下项目里所有用 express 的地方"
# explorer subagent 接手执行

# 接回（resume）
$ omp -c <session-id>
```

**适用场景**：
- Agent 达到能力边界（需要业务确认）
- Subagent 接力（explorer → coder → reviewer）
- 人类临时介入（review 复杂改动）
- 长任务跨会话继续（handoff 后 `/tree` 看会话树）

### 6.5 Session Branch / Fork / Tree（git-like 会话管理）

不是独立 run mode，但和 modes 强耦合 —— 你可以在任何 mode 下用 `/branch` `/fork` 创建新分支。

**触发方式**：
```bash
# 当前会话卡住了，试试另一个思路
> /branch "试试用 RxJS 重构这段代码"
# 在同一个 JSONL 文件里分叉出新叶

# 完全独立的尝试
> /fork "尝试用 Rust 重写这个工具"
# 派生新 JSONL 文件

# 看会话树
> /tree
# 显示：
#   main
#   ├─ 01 原始任务
#   ├─ 02 /branch (RxJS 思路)
#   └─ 03 /fork (Rust 思路)

# 回到主线
$ omp -r  # 弹出选择器

# 合并分支
> /merge 02  # 把 RxJS 分支合回主线
```

**适用场景**：
- 多思路并行探索
- 长任务跨会话继续
- 失败回滚（`/branch` 后可丢弃）
- 与 Subagent 协作（fork 给子 agent 独立尝试）

### 6.6 OMP 模式组合最佳实践

| 场景 | 推荐组合 |
|------|---------|
| **日常编码** | Build Mode 默认 |
| **重大重构** | `/plan` → 审批 → Build 执行 |
| **长任务清理** | `/goal "..."` 让它循环到完成 |
| **多 Agent 流水线** | Build 主导 → `/handoff reviewer` 接力审查 |
| **探索未知需求** | Build + `/branch` 多思路并行 → 选最优合并 |
| **跨会话继续** | Build + `/handoff @human` 暂停 → 人类介入 → `/resume` 接回 |

---

## 七、13 大特性速览

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

## 八、与其他 3 个 Agent 的差异

| 维度 | OMP 优势 | 适用人群 |
|------|---------|----------|
| **vs Claude Code** | ✅ 多 provider · ✅ per-role 模型 · ✅ 原生 Windows · ✅ Hashline | 不锁定 Anthropic 的工程师 |
| **vs Codex** | ✅ 多 provider · ✅ MCP 更成熟 · ✅ 终端深度体验 · ✅ 进程内 LSP/DAP | 不仅用 OpenAI 模型、需要 MCP 扩展 |
| **vs OpenCode** | ✅ per-role 模型 · ✅ 进程内 DAP（28 ops）· ✅ Windows 原生无 WSL · ✅ Rust 原生性能 | 终端重度用户、Win 用户、需要 DAP |

---

## 九、适用场景

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

## 十、相关章节

- 横向对比：[Coding Agents README](README.md) — 4 agent 选型决策树 + 模型/MCP 配置对比
- 单工具深度（Claude Code）：Claude Code Practices（⚠️ 待 Phase 1+ 迁入；占位 `./claude-code-practices/README.md`）
- 循环调用：Loop Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../../agent-execution-patterns/loop-engineering/]`） — Ralph Wiggum Loop（Fresh Context + 文件系统持久记忆，pre-existing in `note/`，保持 unstaged）
- 规范工具：[Agent Spec Tools](../agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec
- 概念层：Harness Engineering（⚠️ 待 Phase 1+ 迁入；占位 `[../../agent-execution-patterns/harness-engineering/]`）

← [返回: Coding Agents 对比](README.md)