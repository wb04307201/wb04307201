<!--
module:
  parent: ai
  slug: ai/agent-spec-tools/spec-kit
  type: article
  category: 主模块子文章
  summary: Spec-Kit：GitHub 官方的 SDD 工具包，5 命令管线 + 30+ Agent 兼容 + 企业级规范。
-->

# Spec-Kit — GitHub 官方 SDD 管线

← 返回 [Agent Spec Tools 对比](README.md)

> [GitHub 官方开源](https://github.com/github/spec-kit)，2025 年 9 月发布。Spec-Driven Development（SDD）的企业级实现 —— 先写规范，再让 Agent 实现，支持 30+ AI 编码 Agent。

---
---

## 一、核心结论（TL;DR）

| 维度 | 内容 |
|------|------|
| **是什么** | GitHub 官方 SDD 工具包，5 个斜杠命令构成规范管线 |
| **核心理念** | Spec = 单一真实来源（人和 Agent 都从 Spec 获取信息） |
| **5 大命令** | `/speckit.constitution` → `specify` → `clarify` → `plan` → `tasks` |
| **Agent 支持** | 30+（Copilot / Claude Code / Cursor / Gemini CLI / Codex…） |
| **CLI 工具** | `specify-cli`（Python / uv 安装） |
| **适合谁** | 企业团队 + 多 Agent 标准化场景 |

---

## 二、安装与配置

### 2.1 安装 CLI

```bash
# 持久安装（推荐）
uv tool install specify-cli --from git+https://github.com/github/spec-kit

# 一次性运行（类似 npx）
uvx --from git+https://github.com/github/spec-kit specify-cli
```

> 前置条件：Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)。

### 2.2 项目初始化

```bash
cd your-project
specify init
```

`specify init` 创建 `.specify/` 目录，包含模板和配置。

### 2.3 Agent 配置

初始化后，斜杠命令（`/speckit.*`）自动在你的 AI 编码 Agent 中可用：

| Agent | 命令前缀 |
|-------|---------|
| Claude Code / Copilot / Cursor | `/speckit.*` |
| Codex CLI（Skills 模式） | `$speckit-*` |
| 通用 Agent | 直接引用 `.specify/` 目录下的模板 |

---

## 三、5 命令 SDD 管线

Spec-Kit 的核心是一条 5 步管线，从"项目原则"到"可执行 task"：

```text
┌───────────────────────────────────────────────────────────┐
│  1. /speckit.constitution                                 │
│     建立项目原则（非谈判项：代码风格 / 测试要求 / 架构约束） │
├───────────────────────────────────────────────────────────┤
│  2. /speckit.specify "Build a [feature]"                  │
│     定义功能规范（What + Why，不写 How）                    │
│     输出：用户目标 / 场景 / 验收标准                        │
├───────────────────────────────────────────────────────────┤
│  3. /speckit.clarify                                      │
│     Agent 提出澄清问题 → 答案烘焙进 Spec                   │
├───────────────────────────────────────────────────────────┤
│  4. /speckit.plan                                         │
│     读取 Spec，生成技术实现计划                             │
├───────────────────────────────────────────────────────────┤
│  5. /speckit.tasks                                        │
│     把计划拆成可执行的 task 列表                            │
│     → 交给 Agent 逐个实现                                 │
└───────────────────────────────────────────────────────────┘
```

### 每步详解

#### 1. `/speckit.constitution` — 项目原则

定义团队的"不可违反"规则，Agent 每次工作都会参考：

```markdown
# Project Constitution
- All public APIs must have TypeScript types
- Test coverage must exceed 80%
- No direct database access from frontend
- Follow existing code patterns
```

#### 2. `/speckit.specify` — 功能规范

写 What + Why，**不写 How**：

```text
/speckit.specify Build a user authentication system
  with JWT tokens, supporting login/logout/refresh,
  and role-based access control.
```

输出结构化 Spec：用户目标 → 使用场景 → 验收标准。

#### 3. `/speckit.clarify` — 澄清

Agent 自动识别 Spec 中的模糊点，逐个提问。答案直接烘焙进 Spec，避免后续歧义。

#### 4. `/speckit.plan` — 实现计划

Agent 读取 Spec + Constitution，生成技术实现计划（架构选型、模块拆分、依赖分析）。

#### 5. `/speckit.tasks` — 可执行任务

把计划拆成细粒度 task，每个 task 足够一个 Agent 单次完成：

```markdown
## Tasks
- [ ] Create User model with JWT fields
- [ ] Implement /auth/login endpoint
- [ ] Implement /auth/refresh endpoint
- [ ] Add RBAC middleware
- [ ] Write integration tests for auth flow
```

---

## 四、跨 Agent 兼容性

Spec-Kit 最大的企业优势 —— **同一个 Spec 文件，不同 Agent 都能用**：

| 场景 | Agent 选择 |
|------|-----------|
| 团队成员 A 用 Copilot | Copilot 读 `.specify/` 实现 task |
| 团队成员 B 用 Claude Code | Claude Code 读 `.specify/` 实现 task |
| CI 中用 Codex CLI | Codex 读 `.specify/` 自动执行 |

规范是 Agent-agnostic 的 —— 写一次，任何 Agent 都能消费。

---

## 五、典型使用流程

```bash
# 1. 初始化项目
specify init

# 2. 在 Claude Code / Copilot 中：
/speckit.constitution     # 设置项目原则
/speckit.specify "Build user auth with JWT"
/speckit.clarify          # 回答 Agent 的澄清问题
/speckit.plan             # 生成技术计划
/speckit.tasks            # 拆成可执行 task

# 3. Agent 逐个实现 task（可结合 Superpowers 强制 TDD）
```

---

## 六、相关章节

- 对比总览：[Agent Spec Tools 三工具对比](README.md)
- 同栏目：[Superpowers](superpowers.md) / [OpenSpec](openspec.md)
- 概念层：[Harness Engineering](../harness-engineering/README.md) — Spec-Kit 是"规范型 Harness"
- 论文：[Spec Kit Agents (arXiv)](https://arxiv.org/html/2604.05278v1) — 多 Agent 架构形式化

---

> 📅 2026-07-08 · AI 工程实践 · Spec-Kit · 实战工具

← [返回: Agent Spec Tools 对比](README.md)
