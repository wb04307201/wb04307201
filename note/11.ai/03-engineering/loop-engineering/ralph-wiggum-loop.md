<!--
module:
  parent: ai
  slug: ai/loop-engineering/ralph-wiggum-loop
  type: article
  category: 主模块子文章
  summary: Ralph Wiggum Loop：用 fresh context 循环驱动 AI 编码 Agent 的开源实战工具。
-->

# Ralph Wiggum Loop — Fresh Context 循环的实战工具

← 返回 [Loop Engineering](README.md)

> Loop Engineering 的**概念层**见 [README](README.md)。本文是**实战层**：用开源 CLI 工具 [open-ralph-wiggum](https://github.com/Th0rgal/open-ralph-wiggum) 把"循环调用 Agent"落地。

---
---

## 一、核心结论（TL;DR）

| 维度 | 内容 |
|------|------|
| **是什么** | 开源 CLI 工具，把 AI 编码 Agent 包在 `while` 循环里，每轮 fresh context |
| **核心洞察** | 文件系统 = 持久记忆（不是 conversation history） |
| **谁发明** | Geoffrey Huntley（2025.5），Th0rgal 做了多 Provider 开源实现 |
| **支持 Agent** | Claude Code / Codex / Copilot / Cursor / Gemini CLI / Amp / OpenCode |
| **一句话安装** | `npm install -g @th0rgal/ralph-wiggum` |
| **最小循环** | `while :; do cat PROMPT.md \| claude ; done` |

---

## 二、为什么叫 Ralph Wiggum？

名字来自《辛普森一家》里的角色 Ralph Wiggum —— 一个执着但有点迷糊的小孩。完美隐喻：

> 每一轮迭代，Agent **忘记一切**（fresh context window），只靠磁盘上的文件重新理解世界。
> 就像 Ralph Wiggum 每次出场都像第一次。

Geoffrey Huntley 的名言：

> *"Software development is dead. Software engineering is alive."*
>
> 软件开发已死（人写代码），软件工程永生（人指挥 Agent 写代码）。

---

## 三、Fresh Context 架构 —— 核心洞察

### 传统 Agent 的问题：Context 累积退化

```
传统 Agent（单 session 长跑）：

Turn 1: context = [system prompt + task]              ← 清晰
Turn 10: context = [system prompt + task + 9 轮历史]   ← 开始膨胀
Turn 50: context = [system prompt + task + 49 轮历史]  ← 严重退化 ❌
```

Context 越长 → Agent 注意力分散 → 回答质量下降 → "lost in the middle"。

### Ralph Loop 的解法：每轮 Fresh Context

```
Ralph Loop（外循环驱动）：

Iteration 1: fresh context → 读 PROMPT.md + git state → 做 task 1 → commit → exit
Iteration 2: fresh context → 读 PROMPT.md + git state → 看 task 1 已完成 → 做 task 2 → commit → exit
Iteration N: fresh context → ... → 所有 task 完成 → 退出循环
```

**关键**：状态不靠 conversation history，靠**磁盘文件**：

| 持久化载体 | 作用 |
|-----------|------|
| `PROMPT.md` | 任务说明 / 架构约束（每轮重新读入） |
| `.ralph/ralph-tasks.md` | 任务清单（勾选进度） |
| `git log / diff` | 已完成的工作（Agent 看 git 就知道做了什么） |
| 代码文件本身 | 当前代码状态 |

> 💡 **这正是 Loop Engineering §六.4「Context 要重置而非累积」的实战实现。**

---

## 四、两种架构对比

| 架构 | 机制 | 优点 | 缺点 |
|------|------|------|------|
| **Bash Loop（Fresh Context）** | 外部 `while` 循环重启 Agent，每轮 clean context | 不退化，适合长任务 | 每轮需重新理解项目 |
| **Plugin（Single Context）** | Agent 内部循环（如 Claude Code `/loop`） | 设置简单 | context 累积退化 |

Open Ralph Wiggum 用的是 **Bash Loop 架构** —— 每次 `ralph` 调用都是新进程。

---

## 五、安装

### 前置条件

| 依赖 | 要求 |
|------|------|
| Node.js | 18+ |
| Git | 必须（Agent 依赖 git state） |
| AI 编码 CLI | 至少装一个：Claude Code / Codex / Copilot / Cursor / Gemini CLI |

### 安装方式

```bash
# 方式 1: npm 全局安装（推荐）
npm install -g @th0rgal/ralph-wiggum

# 方式 2: Bun
bun add -g @th0rgal/ralph-wiggum

# 方式 3: 源码安装
git clone https://github.com/Th0rgal/open-ralph-wiggum.git
cd open-ralph-wiggum
./install.sh
```

---

## 六、基本用法

### 6.1 最简单的一行循环

```bash
# 最原始的 Ralph Loop（不需要任何工具）
while :; do cat PROMPT.md | claude ; done
```

### 6.2 使用 ralph CLI

```bash
# 默认 Agent（OpenCode）
ralph "Build a complete REST API with authentication"

# 指定 Claude Code
ralph "Fix all failing tests" --agent claude

# 指定 Codex + 模型
ralph "Refactor the database layer" --agent codex --model gpt-5-codex

# 限制最大迭代次数（安全护栏）
ralph "Add comprehensive error handling" --agent claude --max 10
```

### 6.3 Tasks Mode（结构化任务）

1. 创建任务清单 `.ralph/ralph-tasks.md`：

```markdown
# Tasks
- [ ] Set up project structure
- [ ] Implement user authentication
- [ ] Create REST API endpoints
- [ ] Add database migrations
- [ ] Write unit tests
```

2. 启动 Tasks Mode：

```bash
ralph "Build a web application" --tasks --agent claude --max 20
```

Agent 每轮选一个 task 完成 → commit → 勾选 → 下一轮。

### 6.4 监控进度

```bash
# 查看循环状态
ralph --status

# 查看状态 + 任务清单
ralph --status --tasks
```

---

## 七、支持的 AI Provider

| Agent | 参数 | Provider |
|-------|------|----------|
| Claude Code | `--agent claude` | Anthropic |
| Codex | `--agent codex` | OpenAI |
| GitHub Copilot | `--agent copilot` | GitHub/Microsoft |
| Cursor Agent | `--agent cursor` | Cursor/Anysphere |
| Gemini CLI | `--agent gemini` | Google |
| Amp | `--agent amp` | Amp |
| OpenCode | `--agent opencode` | 开源（默认） |

---

## 八、安全与最佳实践

### 8.1 安全边界

| 安全等级 | 说明 | 建议 |
|---------|------|------|
| 🟢 Repo-contained | Agent 只改 repo 内文件 | ✅ 放心用 |
| 🟡 Git-tracked | Agent 改的文件都有 git 追踪 | ✅ 用 git diff review |
| 🔴 Irreversible | API 调用 / DB 写入 / 部署 | ❌ 必须人工确认 |

### 8.2 最佳实践

| 实践 | 理由 |
|------|------|
| **始终用 git** | Agent 依赖 git state 理解进度；没 git = Agent 每轮从零开始 |
| **维护进度文件** | 避免 Agent 每轮重新探索整个 repo |
| **Tasks Mode 做结构化工作** | 每轮一个 task，可追踪 |
| **设 `--max` 上限** | 防止无限循环烧 token |
| **前几轮人工 review** | 架构决策一旦 commit 就"永远留下" |
| **PROMPT.md 写清楚** | 这是 Agent 每轮唯一的"记忆"，写得越清楚越好 |

### 8.3 PROMPT.md 模板

```markdown
# Project: My App

## Architecture
- Next.js frontend + Express backend
- PostgreSQL database
- REST API with JWT auth

## Coding Standards
- TypeScript strict mode
- All functions must have JSDoc
- Unit test coverage > 80%

## Current State
Check `git log` and `.ralph/ralph-tasks.md` for progress.

## Rules
- Never delete existing tests
- Always run `npm test` before committing
- Follow the existing code style
```

---

## 九、Ralph Wiggum vs 其他 Agent 模式

| 维度 | Ralph Wiggum Loop | ReAct Agent | DAG Workflow |
|------|-------------------|-------------|--------------|
| **Context 管理** | 每轮 fresh（不累积） | 单 session 累积 | 每节点独立 |
| **持久记忆** | 文件系统 + git | Conversation history | 无（或外部存储） |
| **适用场景** | 长任务 / 大量独立 task | 需要多步推理的探索 | 步骤固定的流水线 |
| **退化风险** | 低（fresh context） | 高（context 膨胀） | 低 |
| **人类介入** | 前几轮 review 即可 | 通常需要全程监督 | 设计后自动执行 |
| **代表工具** | open-ralph-wiggum | LangChain Agent | LangGraph / Prefect |

---

## 十、相关章节

- 概念层：[Loop Engineering — 循环调用的反直觉哲学](README.md) — Task / Verifier / Feedback 理论框架
- 同栏目：[Harness Engineering](../harness-engineering/README.md) — Ralph Loop 需要 Harness 兜底
- 实战：[生产级 Agent](../production-agent/README.md) — 生产环境的 Agent 工程实践
- 面试版：[13.split-hairs Loop Engineering](../../../13.split-hairs/11.ai/loop-engineering/README.md)
- 关联：[Agent 执行模式](../../04-architecture/agent-execution-patterns/README.md) — ReAct / DAG / Multi-Agent 对比

---

> 📅 2026-07-08 · AI 工程实践 · Ralph Wiggum Loop · 实战工具

← [返回: Loop Engineering](README.md)
