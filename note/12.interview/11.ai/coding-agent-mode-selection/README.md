<!--
question:
  id: 11.ai-coding-agent-mode-selection
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 高频
  scenario_type: 架构决策困境
  tags: [11.ai, coding-agent, claude-code, codex, opencode, omp, plan-mode, goal-mode, handoff, mcp]
-->

# Coding Agent 选型与模式选择：4 大编程 Agent + 7 大模式决策框架

> 一句话定位：2026 年 AI 工程师面试必问 —— 4 个主流 coding agent（Claude Code / Codex / OpenCode / OMP）怎么选、7 种运行模式（Build / Accept Edits / Plan / Goal / Handoff / Session tree / Bypass）怎么配。深度对比见 [Coding Agents 横向对比](../../../09.ai-applications/agent/coding-agents/README.md) + [Coding Agents 运行模式详解](../../../09.ai-applications/agent/coding-agents/README.md)。

> **系列定位**：经典 AI 工程师面试题（高频、选型向必考）。考察的不是"哪个 agent 最好"，而是 **多维度选型决策框架** + **模式与场景匹配** + **团队标准化落地**。

---

⭐⭐⭐⭐ 深度级别（架构师级）
📚 前置知识：用过 1+ 个 Coding Agent、了解 MCP 协议、对 Anthropic / OpenAI 生态有基本认知

---

## 引子：架构师的"选型困境"

```text
CTO："我们要统一 AI Coding 工具了，4 个主流 coding agent（Claude Code / Codex / OpenCode / OMP）选哪个？"

你："按场景。Anthropic 生态选 Claude Code，OpenAI 生态选 Codex，多模型策略选 OpenCode，终端重度选 OMP。"

CTO："那 Plan Mode / Goal Mode / Handoff 这些模式怎么配？团队新人该用哪个模式？"

你："按自主程度。渐进权限用 Claude Code 3 档（Default → Accept Edits → Plan），长任务用 Goal Mode，多 Agent 流水线用 Handoff。"

CTO："听起来都对。给我一个能写在团队 Wiki 上的选型决策树 —— 不要再给我'看场景'。"

你："……"
```

**真相**：4 个 agent × 7 个 mode = 28 种组合，但**选型的本质是 3 个维度**：
1. **模型锁定 vs 多 provider**（决定能不能换底层）
2. **单 Agent vs 多 Agent 协作**（决定能不能并行）
3. **任务复杂度 vs 自主程度**（决定用 Plan / Goal / Accept Edits 哪种模式）

不会选 = 团队效率低下（不同人用不同 agent、不同 mode，Code Review 标准不一致）。
会选 = 一次决策节省 6 个月磨合期。

---

## 一、核心结论（TL;DR）

### 1.1 4 Agent 选型矩阵

| 维度 | Claude Code | Codex | OpenCode | OMP |
|------|------------|-------|----------|-----|
| **模型** | 🔒 Anthropic only | OpenAI 为主（`wire_api` 可改向） | ✅ 75+ providers | ✅ 40+ providers |
| **多角色模型** | ❌ | ❌ | ✅ `small_model` | ✅ **default/smol/slow/plan 4 角色** |
| **运行模式数** | 4（Default/Accept Edits/Plan/Bypass） | 3（命令/交互/approval-mode）+ 桌面端 Plan+Goal | 2（Plan/Build）+ ultrawork | 5（Build/Plan/Goal/Handoff/Session tree）|
| **MCP 支持** | `.mcp.json` | `config.toml` | `opencode.jsonc` + OAuth 自动注册 | `config.yml` |
| **最适合** | Anthropic 生态 + 大 monorepo | OpenAI 生态 + CI/CD | 多模型策略 + 多 Agent | 终端重度 + 长任务 |

### 1.2 7 模式 × 4 Agent 矩阵

| 模式 | Claude Code | Codex | OpenCode | OMP |
|------|------------|-------|----------|-----|
| **Build（可编辑 + 执行）** | ✅ Default | ✅ 交互模式 | ✅ Build（Tab 切）| ✅ Build（默认）|
| **Accept Edits（自动接受文件）** | ✅ Shift+Tab | ❌ | ❌ | ❌ |
| **Plan Mode（只读规划）** | ✅ Shift+Tab | ✅ 桌面端 | ✅ 默认 + Tab 切 | ✅ `/plan` + per-role |
| **Goal Mode（长任务循环）** | ❌ | ✅ 桌面端 | ✅ ultrawork | ✅ `/goal` |
| **Handoff（会话移交）** | ❌ | ❌ | ❌ | ✅ `/handoff` |
| **Session branch/fork/tree** | ❌ | ❌ | ❌ | ✅ git-like JSONL |
| **Bypass Permissions** | ✅ `--dangerously-skip-permissions` | ✅ `--approval-mode full-auto` | ✅ `permissions.ask: false` | ❌（dry by default）|

### 1.3 一句话选型

> **看模型 → 看模式 → 看生态**：先定模型锁定还是多 provider，再定要不要 Goal Mode / Handoff，最后定 MCP + 生态成熟度。

---

## 二、4 Agent × 7 模式决策框架

### 2.1 第一维度：模型锁定 vs 多 Provider

```text
Q: 你能用任意 LLM（Claude / GPT / DeepSeek / Ollama）吗？
│
├─ 不能 / 不想换 → Claude Code（Anthropic 锁定，换来 Harness 生态深度）
├─ OpenAI 为主 + 偶尔兼容网关 → Codex（`wire_api=chat_completions` + `base_url`）
└─ 能 / 想 → OpenCode（75+ providers）或 OMP（40+ providers + per-role 4 模型）
```

**关键判断**：
- 如果公司**只用 Anthropic** → Claude Code（不要换别的）
- 如果公司**多模型策略**（成本优化 / 国产化备份）→ OpenCode 或 OMP
- OMP 比 OpenCode 多 per-role 模型（default/smol/slow/plan 4 角色），**适合"按任务类型自动切换模型"**

### 2.2 第二维度：单 Agent vs 多 Agent 协作

```text
Q: 需要多个 Agent 协作吗？
│
├─ 不需要 / 单人 → Claude Code / Codex（单 Agent 成熟）
├─ 需要并行（多任务同时跑）→ Codex 云端沙盒（独家）
└─ 需要 Subagent 接力（explorer → coder → reviewer）→ OMP `/handoff`（独家）
                      或 OpenCode ultrawork（Sisyphus 主 Agent）
```

**关键判断**：
- **OMP Handoff 是独家** —— 唯一一个能"agent → agent → 人"显式移交上下文的
- **OpenCode ultrawork** 适合"一键派发多 Agent 自动完成"（关键词触发）
- **Codex 云端沙盒** 适合"批量并发任务"（多 worktree 并行）

### 2.3 第三维度：任务复杂度 vs 自主程度

```text
Q: 任务需要多严格的权限控制？
│
├─ 渐进式权限（Default / Accept Edits / Plan / Bypass）→ Claude Code（Shift+Tab 3 档）
├─ 3 档 approval-mode（suggest / auto-edit / full-auto）→ Codex（CLI 友好）
├─ 最简（Plan + Build 二选一）→ OpenCode（Tab 切）
└─ 不需要权限分级 + 信任 agent → OMP（dry by default，所有命令都问）
```

**关键判断**：
- **Claude Code** 是**唯一 3 档渐进权限**（Default 手动 / Accept Edits 自动接受文件 / Plan 只读）
- **Codex** 用 `--approval-mode` 一次性定档（启动时决定）
- **OpenCode** 只 Plan + Build 二选一（最简单）
- **OMP** dry by default（每个命令都问），**没有 Bypass 模式**

### 2.4 综合决策矩阵

| 你的核心需求 | 第一选 | 第二选 |
|------------|--------|--------|
| 已在 Anthropic 生态 + 大 monorepo | Claude Code | OMP（解锁 per-role）|
| 已在 OpenAI 生态 + 云端并行 | Codex | — |
| 多 LLM 策略 + 多 Agent 协作 | OMP | OpenCode |
| 终端重度 + Windows 原生 + DAP 调试 | OMP | OpenCode（+ WSL）|
| CI/CD 全自动（最高自主）| Codex `--approval-mode full-auto` | Claude Code `--dangerously-skip-permissions` |
| 长任务循环到 verifier 通过 | OMP `/goal` | Codex 桌面端 Goal / OpenCode ultrawork |
| 多 Agent 流水线（显式移交）| OMP `/handoff`（独家）| — |
| 跨会话继续 + 多分支探索 | OMP `/branch` `/fork` `/tree`（独家）| — |

---

## 三、面试陷阱（5 道）

### 陷阱 1："Claude Code 是最好的" —— 错的

**陷阱症状**：把"5 大 Harness 扩展点 + 官方生态"等同于"最好"。

**真相**：
- Claude Code **锁定 Anthropic**，不能用 GPT-5 / DeepSeek / Ollama
- 多 LLM 策略场景下，OpenCode / OMP 更优
- 终端深度用户、Windows 原生、DAP 调试场景下，OMP 优于 Claude Code

**面试话术**：
> "没有'最好'，只有'最匹配'。Anthropic 生态 + 大 monorepo → Claude Code；多模型策略 → OpenCode / OMP；终端重度 + 长任务自动化 → OMP。"

### 陷阱 2："Plan Mode 是 Claude Code 独家" —— 错的

**陷阱症状**：以为 Shift+Tab Plan Mode 是 Claude Code 独有。

**真相**：4 个 Agent **都有 Plan Mode**：
- **Claude Code** Shift+Tab 第 3 档
- **Codex** 桌面端"计划模式"
- **OpenCode** 默认启动就在 Plan Mode
- **OMP** `/plan` + per-role planner 模型（用独立 planner 模型，**最彻底**）

**面试话术**：
> "4 个都有 Plan Mode，但 OMP 的 Plan 是最彻底的 —— 它用 per-role planner 模型（独立配置），审批后还能选 execute-and-purge / keep-transcript / compact-context 3 种执行策略。"

### 陷阱 3："Goal Mode = 长任务循环 = Ralph Wiggum Loop" —— 不完全对

**陷阱症状**：把 Goal Mode 和 Ralph Wiggum Loop 混为一谈。

**真相**：
- **OMP `/goal` / Codex 桌面端 Goal / OpenCode ultrawork** —— Goal Mode，**同一会话内循环**
- **Ralph Wiggum Loop** —— Fresh Context **每轮重启** + 文件系统持久记忆

两者都是"长任务循环到 verifier 通过"，但 Ralph Wiggum 是 **fresh context**（每轮新会话），Goal Mode 是 **同会话循环**（保留上下文）。

**面试话术**：
> "Goal Mode 是同会话内循环到 verifier 通过；Ralph Wiggum Loop 是 fresh context 每轮重启。前者保留上下文，后者避免上下文污染。两个思路解决不同问题。"

### 陷阱 4："MCP 配置都一样" —— 错的

**陷阱症状**：以为 `.mcp.json` 是 4 个 Agent 通用格式。

**真相**：4 个 Agent MCP 配置 schema **完全不同**：

| Agent | 配置文件 | MCP 字段位置 |
|-------|---------|------------|
| Claude Code | `.mcp.json` / `~/.claude.json` | `mcpServers.<name>` |
| Codex | `~/.codex/config.toml` | `[mcp_servers.<name>]` |
| OpenCode | `opencode.jsonc` | `mcp.<name>` + OAuth 自动 RFC 7591 |
| OMP | `~/.omp/agent/config.yml` | `mcp.servers[]` 数组 |

**MCP OAuth 自动注册**只有 OpenCode 默认启用（检测 401 + 动态客户端注册 + Token 安全存储）。

**面试话术**：
> "4 个 Agent MCP 配置 schema 不同：Claude Code 用 `.mcp.json`、Codex 用 TOML、OpenCode 用 JSONC（自动 OAuth）、OMP 用 YAML 数组。切换 Agent 时 MCP 配置**不能直接迁移**，要按新 Agent 的 schema 重写。"

### 陷阱 5："OMP 的 Hashline 编辑就是 RAG" —— 错的

**陷阱症状**：以为 Hashline 编辑是某种检索增强。

**真相**：Hashline 是**编辑格式**（4-hex xxHash32 内容哈希锚点），让模型用锚点而非 retyping 改代码：
- **优势**：stale anchor 自动拒绝、Grok Code Fast `pass@1: 6.7% → 68.3%`、Grok 4 Fast `-61% output tokens`
- **跟 RAG 无关**：Hashline 不检索，是**编辑格式**

**面试话术**：
> "Hashline 不是 RAG，是编辑格式。让模型用内容哈希锚点改代码，避免 whitespace battle 和 string-not-found 循环。stale anchor 自动拒绝能防止文件损坏。"

---

## 四、最佳实践（4 大场景决策树）

### 4.1 场景 1：新团队起步 / 标准化选型

```text
Q: 团队从 0 开始统一 Coding Agent？
│
├─ 已采购 Anthropic / OpenAI 企业版？
│   ├─ Anthropic → Claude Code（CLAUDE.md + Skills 团队内分发）
│   └─ OpenAI → Codex（云端并行 + IDE 三形态）
│
├─ 没有采购 / 想要灵活性
│   ├─ 多模型策略 + 多 Agent → OMP（per-role + Handoff）
│   └─ 只想要简单的 Plan + Build → OpenCode（最简双模式）
│
└─ 不确定 / 想先试
    → OpenCode（75+ providers + 最简双模式 + Zen 精选模型）
```

### 4.2 场景 2：长任务自动化

```text
Q: 长任务循环到完成 —— 用哪个 Agent？
│
├─ 同会话内循环（保留上下文）→ OMP `/goal`
├─ 多 Agent 派发（Sisyphus 主 + 4 子 Agent）→ OpenCode ultrawork
├─ 云端并行（多 worktree 并发）→ Codex 云端沙盒
└─ Fresh Context 每轮重启 → Ralph Wiggum Loop（任何 Agent 都能套）
```

### 4.3 场景 3：CI/CD 全自动

```text
Q: CI/CD 管道嵌入 Coding Agent —— 怎么配？
│
├─ 用 Codex → --approval-mode full-auto（最成熟的 CI 模式）
├─ 用 Claude Code → --dangerously-skip-permissions
├─ 用 OpenCode → 配置文件 permissions.ask: false
└─ 用 OMP → 不推荐（dry by default，CI 友好度低）
```

### 4.4 场景 4：多 Agent 流水线

```text
Q: explorer → coder → reviewer 三段流水线 —— 怎么实现？
│
├─ OMP → /handoff code-reviewer（agent → agent 显式移交，独家）
├─ OpenCode → ultrawork 关键词（Sisyphus 主 Agent + Oracle / Librarian / Frontend / Explore 子 Agent）
└─ 其他 Agent → 拆 3 个独立会话，手动复制上下文（低效）

---

## 五、面试话术（90 秒版本）

### 5.1 模板 1："4 个 Agent 怎么选"

> "4 个 Coding Agent 不是互斥，是按场景混搭。**第一步看模型锁定**：Anthropic 生态选 Claude Code（锁定但生态深），OpenAI 生态选 Codex（`wire_api` 可改向兼容网关），多模型策略选 OpenCode / OMP。**第二步看模式需求**：要渐进权限选 Claude Code 3 档（Shift+Tab），要 Goal Mode 选 OMP / Codex / OpenCode ultrawork，要 Handoff + Session tree 只能选 OMP（独家）。**第三步看生态成熟度**：CLAUDE.md / Skills / Plugins 是 Claude Code 最深，Oh-my-opencode 多 Agent 框架是 OpenCode 最丰富，per-role 4 模型分工是 OMP 独家。"

### 5.2 模板 2："Plan Mode 怎么用"

> "4 个 Agent 都有 Plan Mode。Claude Code 用 Shift+Tab 第 3 档、Codex 用桌面端配置、OpenCode 默认就在 Plan Mode、OMP 用 `/plan` + per-role planner 模型（独立配置）。Plan 后选 3 种执行策略：execute-and-purge（清空 transcript）/ keep-transcript（保留上下文）/ compact-context（压缩）。"

### 5.3 模板 3："Goal Mode vs Ralph Wiggum Loop"

> "Goal Mode 是**同会话内循环**到 verifier 通过；Ralph Wiggum Loop 是 **fresh context 每轮重启** + 文件系统持久记忆。前者保留上下文（适合需要中间状态的任务），后者避免上下文污染（适合长任务避免上下文窗口爆掉）。OMP / Codex / OpenCode 用 Goal Mode；任何 Agent 都能套 Ralph Wiggum Loop。"

### 5.4 模板 4："为什么 OMP 模式最多"

> "OMP 是 4 个 Coding Agent 中唯一同时拥有 Build / Plan / Goal / Handoff / Session tree 五件套的。原因是它定位是'terminal-first + IDE wired in' —— 把 IDE 级能力（plan / debug / multi-agent）都内化。其他 Agent 要么是单 IDE 集成（Claude Code / Codex），要么是 CLI 优先（OpenCode），没有 OMP 那么完整的 run mode 体系。"

### 5.5 模板 5："MCP 配置怎么迁移"

> "MCP 配置**不能直接迁移** —— 4 个 Agent 的 MCP schema 不同：Claude Code 用 `.mcp.json` 的 `mcpServers` 字段、Codex 用 `config.toml` 的 `[mcp_servers]` 段、OpenCode 用 `opencode.jsonc` 的 `mcp` 字段（OAuth 自动注册）、OMP 用 `config.yml` 的 `mcp.servers` 数组。切换 Agent 时要按新 schema 重写 MCP 配置。OAuth 自动注册只有 OpenCode 默认启用。"

---

## 六、相关章节

### 6.1 主模块（Coding Agents 横向对比 + 运行模式详解）

- 横向对比（4 agent 选型 + 模型/MCP 配置）：[`coding-agents/README.md`](../../../09.ai-applications/agent/coding-agents/README.md)
- Claude Code 速查（含 Plan Mode / Bypass）：[`coding-agents/claude-code.md`](../../../09.ai-applications/agent/coding-agents/claude-code.md)
- Codex 速查（含命令/交互 + approval-mode + 桌面端 Plan/Goal）：[`coding-agents/codex.md`](../../../09.ai-applications/agent/coding-agents/codex.md)
- OpenCode 速查（含 Plan/Build + ultrawork）：[`coding-agents/opencode.md`](../../../09.ai-applications/agent/coding-agents/opencode.md)
- OMP 速查（含 5 件套运行模式）：[`coding-agents/omp.md`](../../../09.ai-applications/agent/coding-agents/omp.md)

### 6.2 同栏目（11.ai 系列面试题）

- 已有 Claude Code 主题：[`claude-code-agentic-search`](../claude-code-agentic-search/README.md) — 为什么放弃 RAG（agent 检索范式）
- AI 编码 ROI：[`ai-coding-roi`](../ai-coding-roi/README.md) — DORA + SPACE 框架
- AI 编码悖论：[`ai-coding-productivity-paradox`](../ai-coding-productivity-paradox/README.md)
- Token 经济性：[`ai-coding-token-economics`](../ai-coding-token-economics/README.md)
- 长任务循环（Loop Engineering）：[`loop-engineering`](../loop-engineering/README.md) — Ralph Wiggum Loop 深度
- 多 Agent 协作：[`multi-agent-system-design`](../multi-agent-system-design/README.md)
- Agent 记忆分类：[`agent-memory-classification`](../agent-memory-classification/README.md)

### 6.3 关联主模块

- Harness Engineering：[`harness-engineering`](./harness-engineering/README.md) — Claude Code 5 扩展点都是 Harness 实现
- Loop Engineering：[`loop-engineering`](./loop-engineering/README.md) — 长任务自动化循环
- Agent Spec Tools：[`agent-spec-tools`](../../../09.ai-applications/agent/agent-spec-tools/README.md) — Superpowers / Spec-Kit / OpenSpec（在 Agent 上跑的规范）

---

> 📅 2026-07-25 · 咬文嚼字 · 11.ai Coding Agents 选型 · ⭐⭐⭐⭐（架构师级 · 高频选型题）

← [返回: 咬文嚼字 · 11.ai](../README.md)