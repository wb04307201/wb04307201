<!--
module:
  parent: ai
  slug: ai/loop-engineering/ralph-wiggum-loop
  type: article
  category: 主模块子文章
  summary: Ralph Wiggum Loop：每轮 fresh context 的循环驱动模式——Agent 忘记一切，只靠磁盘文件重新理解世界。
-->

# Ralph Wiggum Loop — Fresh Context 循环模式

← 返回 [Loop Engineering](README.md)

> Loop Engineering 的**概念层**见 [README](README.md)。本文聚焦**一种特定的循环架构**：每轮 fresh context（Agent 忘记一切，只靠磁盘文件理解世界）。

---
---

## 一、为什么叫 Ralph Wiggum？

名字来自《辛普森一家》里的角色 **Ralph Wiggum** —— 警察局长 Clancy Wiggum 的儿子，一个执着但永远像第一次出场的迷糊小孩。

完美隐喻：

> 每一轮迭代，Agent **忘记一切**（fresh context window），只靠磁盘上的文件重新理解世界。
> 就像 Ralph Wiggum 每次出场都像第一次。

这个概念由 **Geoffrey Huntley**（2025 年 5 月）提出。他的核心洞察：

> *"Software development is dead. Software engineering is alive."*
>
> 软件开发已死（人写代码），软件工程永生（人指挥 Agent 写代码）。

---

## 二、核心问题：Context 累积退化

传统 Agent 在单个 session 中长时间运行时，会面临一个根本性问题：

```
传统 Agent（单 session 长跑）：

Turn 1:  context = [system prompt + task]              ← 清晰
Turn 10: context = [system prompt + task + 9 轮历史]   ← 开始膨胀
Turn 50: context = [system prompt + task + 49 轮历史]  ← 严重退化 ❌
```

Context 越长 → Agent 注意力分散 → 回答质量下降 → "lost in the middle"。

这是 LLM 的固有缺陷，无法通过"更好的 prompt"解决。

---

## 三、Ralph Wiggum 的解法：每轮 Fresh Context

```
Ralph Wiggum Loop（外循环驱动）：

Iteration 1: fresh context → 读 PROMPT.md + git state → 做 task 1 → commit → exit
Iteration 2: fresh context → 读 PROMPT.md + git state → 看 task 1 已完成 → 做 task 2 → commit → exit
Iteration N: fresh context → ... → 所有 task 完成 → 退出循环
```

**核心洞察**：状态不靠 conversation history，靠**磁盘文件**。

| 持久化载体 | 作用 |
|-----------|------|
| `PROMPT.md` | 任务说明 / 架构约束（每轮重新读入） |
| 任务清单文件 | 任务进度（勾选已完成项） |
| `git log / diff` | 已完成的工作（Agent 看 git 就知道做了什么） |
| 代码文件本身 | 当前代码状态 |

> 💡 **这正是 Loop Engineering「Context 要重置而非累积」原则的实战实现。**

---

## 四、两种循环架构对比

| 维度 | Ralph Wiggum Loop（Fresh Context） | 传统 Session Loop（Single Context） |
|------|-----------------------------------|-----------------------------------|
| **Context 管理** | 每轮 fresh，不累积 | 同一 session，持续累积 |
| **持久记忆** | 文件系统 + git | conversation history |
| **退化风险** | 低（每轮从零开始） | 高（context 膨胀 → lost in the middle） |
| **适用场景** | 长任务 / 大量独立 task | 需要多步推理的短时探索 |
| **每轮开销** | 需重新理解项目（读文件/git） | 无（上下文已在内存中） |
| **人类介入** | 前几轮 review 即可 | 通常需要全程监督 |
| **代表** | `while` 循环 + 任意 CLI | Claude Code `/goal`、Cursor Agent |

---

## 五、本地实操：4 种方案（从零脚本到零代码）

### 方案 1：一行 Bash（最原始）

Ralph Wiggum Loop 的本质极其简单——不需要任何框架：

```bash
while :; do cat PROMPT.md | claude ; done
```

`while :;` 是无限循环，每轮：读 `PROMPT.md` → 喂给 Agent → 工作 → commit → 退出 → 循环回来拿到全新 context。

```bash
# 任意 Agent 通用
while :; do cat PROMPT.md | codex --full-auto ; done   # Codex
while :; do cat PROMPT.md | opencode ; done            # OpenCode
```

### 方案 2：结构化 Bash 脚本（推荐正式项目）

带最大轮次、进度追踪、退出信号、Docker 隔离（参考 [aihero.dev](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum)）：

```bash
#!/bin/bash
set -e
MAX=${1:-10}
for ((i=1; i<=$MAX; i++)); do
  echo "=== Iteration $i / $MAX ==="
  result=$(claude -p \
    "@plan.md @progress.txt
     1. 从 plan.md 选最高优先级 task
     2. 实现 + 跑测试
     3. 追加进度到 progress.txt
     4. git commit
     如果所有任务完成，输出 <promise>COMPLETE</promise>")

  echo "$result"
  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "✅ All done!"; exit 0
  fi
  sleep 2
done
echo "⚠️ Max iterations reached"
```

**进阶**：用 Docker sandbox 隔离 Agent，防止误操作：

```bash
result=$(docker sandbox run claude -p "@plan.md ...")
```

### 方案 3：内置 `/goal` 命令（零脚本，2026 新品）

Claude Code 和 Codex 都内置了 Ralph Loop 的官方实现——不需要写 bash：

```bash
# Claude Code
/goal "所有 auth 测试通过且 lint clean"

# Codex
/goal "API 返回 200 且 coverage > 80%"
```

**原理**：Agent 工作 → 每轮结束后**快速小模型**（evaluator）检查条件 → 不满足就继续 → 满足就停。

> Boris Cherny（Claude Code 负责人）：*"I don't prompt Claude anymore. I have loops running that prompt Claude. My job is to write loops."*

**注意**：`/goal` 是**同一 session**，有 context 累积退化风险；纯 bash 循环每轮 fresh context，不会退化。

### 方案 4：内置 `/loop`（时间驱动）

```bash
# Claude Code — 每 5 分钟跑一次
/loop every 5 minutes /check-ci-status
```

每轮独立 session（无退化），适合 CI 监控、定期巡检类任务。

### 4 种方案对比

| 方案 | 复杂度 | Context | 适合场景 | 安全隔离 |
|------|--------|---------|---------|---------|
| 一行 Bash | 极低 | Fresh | 快速实验 | 无 |
| 结构化脚本 | 低 | Fresh | 正式项目 | Docker 可选 |
| `/goal` | 零 | Shared（累积） | 有可验证终点 | 内置 sandbox |
| `/loop` | 零 | Fresh | 定期巡检 | 内置 sandbox |

详见 [内置循环命令对比](builtin-loop-commands.md)。

---

## 六、外置循环 3 层次（2026 全景）

Addy Osmani 总结：Loop 需要 5 大原语（Automations / Worktrees / Skills / Connectors / Sub-agents）+ 1 个持久状态。2026 年 Claude Code 和 Codex 都已内置这 5 个原语，但外置循环仍有 3 个层次：

### 层次 1：DIY 脚本（上面 4 种方案）

自己写 bash / 用内置命令。完全掌控，零依赖。

### 层次 2：Agent 内置编排

| 原语 | Claude Code | Codex |
|------|------------|-------|
| **定时任务** | `/loop` + hooks + cron | Automations tab |
| **并行隔离** | `git worktree` + `--worktree` | 内置 worktree per thread |
| **项目知识** | SKILL.md | SKILL.md |
| **工具集成** | MCP servers + plugins | MCP + connectors + plugins |
| **子 Agent** | `.claude/agents/` | `.codex/agents/` |
| **持久状态** | Markdown / Linear (via MCP) | Markdown / Linear (via connector) |

### 层次 3：外部编排平台

| 平台 | 定位 | 特点 |
|------|------|------|
| **GitHub Actions** | CI/CD 级循环 | Agent 跑在 CI 上，结果推 PR，关机也继续 |
| **Docker Sandbox** | 安全隔离 | 把 Agent 放在容器里，防止不可逆操作 |
| **Conductor**（macOS） | 外置编排器 | 包 Claude Code / Codex，Triage 收件箱 |

> 💡 **选型建议**：个人项目用层次 1（bash + `/goal`），团队项目用层次 2（Skills + Worktrees），持续集成用层次 3（GitHub Actions）。

---

## 七、PROMPT.md —— Agent 唯一的"记忆"

Agent 每轮唯一能依赖的就是 `PROMPT.md`，所以它必须写得足够清楚：

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
Check `git log` to see what's been done.
Check `tasks.md` for remaining work.

## Rules
- Never delete existing tests
- Always run `npm test` before committing
- Follow the existing code style
```

**关键原则**：

| 原则 | 说明 |
|------|------|
| **写清架构** | Agent 每轮都要理解项目，写一次比每轮猜一次好 |
| **指向 git** | "Check git log" 比列出已完成任务更可靠 |
| **明确约束** | "不要删除测试"、"不要修改 config/" 这类负面规则最重要 |
| **可验证终点** | 告诉 Agent 什么算"完成" |

---

## 八、任务清单模式

对结构化工作，可以用任务清单文件让 Agent 逐条推进：

```markdown
<!-- tasks.md -->
# Tasks
- [x] Set up project structure
- [x] Implement user authentication
- [ ] Create REST API endpoints
- [ ] Add database migrations
- [ ] Write unit tests
```

Agent 每轮读这个文件 → 选一个未完成的 task → 实现 → commit → 打勾 → 退出。下一轮回来，看到进度继续推进。

---

## 九、安全边界

| 安全等级 | 说明 | 建议 |
|---------|------|------|
| 🟢 Repo-contained | Agent 只改 repo 内文件 | ✅ 放心用 |
| 🟡 Git-tracked | Agent 改的文件都有 git 追踪 | ✅ 用 `git diff` review |
| 🔴 Irreversible | API 调用 / DB 写入 / 部署 | ❌ 必须人工确认 |

**最佳实践**：

- **始终用 git** — Agent 依赖 git state 理解进度；没 git = Agent 每轮从零开始
- **前几轮人工 review** — 架构决策一旦 commit 就"永远留下"
- **设最大轮次** — 防止无限循环烧 token
- **PROMPT.md 写清楚** — 这是 Agent 每轮唯一的"记忆"

---

## 十、与其他模式的对比

| 维度 | Ralph Wiggum Loop | ReAct Agent | DAG Workflow |
|------|-------------------|-------------|--------------|
| **Context 管理** | 每轮 fresh（不累积） | 单 session 累积 | 每节点独立 |
| **持久记忆** | 文件系统 + git | Conversation history | 无（或外部存储） |
| **适用场景** | 长任务 / 大量独立 task | 需要多步推理的探索 | 步骤固定的流水线 |
| **退化风险** | 低（fresh context） | 高（context 膨胀） | 低 |
| **实现复杂度** | 极低（一行 bash） | 中（需 Agent 框架） | 高（需 DAG 引擎） |

---

## 十一、相关章节

- 概念层：[Loop Engineering — 循环调用的反直觉哲学](README.md) — Task / Verifier / Feedback 理论框架
- 内置循环：[内置循环命令对比](builtin-loop-commands.md) — `/goal` vs `/loop` vs Ralph Wiggum 架构差异
- 同栏目：[Harness Engineering](../harness-engineering/README.md) — Ralph Loop 需要 Harness 兜底
- 面试版：[13.split-hairs Loop Engineering](../../../13.split-hairs/11.ai/loop-engineering/README.md)
- 关联：[Agent 执行模式](../../04-architecture/agent-execution-patterns/README.md) — ReAct / DAG / Multi-Agent 对比

---

## 📚 参考来源

- [Addy Osmani: Loop Engineering](https://addyosmani.com/blog/loop-engineering/) — Loop 5 大原语 + Codex/Claude Code 映射
- [Decoding AI: Stop Orchestrating, Use Ralph Loops](https://www.decodingai.com/p/ralph-loops) — Fresh vs Shared context 深度对比
- [AIHero: 11 Tips for Ralph Wiggum](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum) — 结构化脚本 + HITL/AFK 两种模式
- [AI Architects: Ralph Loop + /goal](https://theaiarchitects.com/blog/claude-code-ralph-loop) — `/goal` 官方实现详解
- [Geoffrey Huntley: how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum) — 创始人原始指南

---

> 📅 2026-07-15 · AI 工程实践 · Ralph Wiggum Loop · Fresh Context 循环模式

← [返回: Loop Engineering](README.md)
