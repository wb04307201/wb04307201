<!--
module:
  parent: ai
  slug: ai/agent-spec-tools/spec-kit
  type: article
  category: 主模块子文章
  summary: Spec-Kit：GitHub 官方的 SDD 工具包，9 命令管线（短/全两条路径）+ 35 集成 + 企业级规范。
-->

# Spec-Kit — GitHub 官方 SDD 管线

← 返回 [Agent Spec Tools 对比](README.md)

> [GitHub 官方开源](https://github.com/github/spec-kit)，2025 年 9 月发布。Spec-Driven Development（SDD）的企业级实现 —— 先写规范，再让 Agent 实现，支持 35 种 AI 编码 Agent 集成。

---
---

## 一、核心结论（TL;DR）

| 维度 | 内容 |
|------|------|
| **是什么** | GitHub 官方 SDD 工具包，斜杠命令构成规范管线 |
| **核心理念** | Spec = 单一真实来源（人和 Agent 都从 Spec 获取信息） |
| **两条路径** | 短路径（小功能）5 步 / 全路径（生产级）9 步含 3 道质量门 |
| **Agent 支持** | 35 集成（Copilot / Claude Code / Cursor / Gemini CLI / Codex / Zed / Kiro…） |
| **CLI 工具** | `specify-cli`（Python / uv 安装） |
| **适合谁** | 企业团队 + 多 Agent 标准化场景 |

---

## 二、安装与配置

### 2.1 安装 CLI

```bash
# 持久安装（推荐，已上 PyPI）
uv tool install specify-cli

# 一次性运行（类似 npx）
uvx --from git+https://github.com/github/spec-kit specify-cli
```

> 前置条件：Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。装完用 `specify check` 验证。

### 2.2 项目初始化

```bash
specify init taskify              # 或 specify init . 用当前目录
specify init . --integration copilot   # 显式指定 Agent（不传则交互式选择）
```

`specify init` 创建 `.specify/` 目录（含模板 + 配置），并用 `.specify/feature.json` 追踪当前活跃功能（**不依赖 git 分支**）。

### 2.3 Agent 配置

初始化后，斜杠命令（`/speckit.*`）自动在你的 AI 编码 Agent 中可用：

| Agent | 命令前缀 |
|-------|---------|
| Claude Code / Copilot / Cursor | `/speckit.*` |
| Codex CLI（Skills 模式） | `$speckit-*` |
| 通用 Agent | 直接引用 `.specify/` 目录下的模板 |

---

## 三、完整命令管线（短路径 vs 全路径）

Spec-Kit 的核心是一条从"项目原则"到"代码收敛"的命令管线。**按功能规模选路径**：

### 3.1 两条路径

```text
短路径（小功能，5 步）：
  specify → plan → tasks → implement → converge

全路径（生产级，9 步，+3 道质量门）：
  constitution → specify → clarify → plan → checklist → tasks → analyze → implement → converge
                          └质量门1┘          └质量门2┘        └质量门3┘
```

### 3.2 命令全集

| 命令 | 阶段 | 作用 | 路径 |
|------|------|------|------|
| `/speckit.constitution` | 治理 | 建立项目原则（不可谈判项：代码风格 / 测试 / 架构约束） | 全路径 |
| `/speckit.specify` | What/Why | 定义功能规范（用户目标 / 场景 / 验收标准，**不写 How**） | 两者 |
| `/speckit.clarify` | 质量门 1 | Agent 就 Spec 模糊点提问，答案烘焙进 Spec（**建议在 plan 前**） | 全路径 |
| `/speckit.plan` | How/Tech | 读 Spec + Constitution，生成技术实现计划（架构 / 选型 / 依赖） | 两者 |
| `/speckit.checklist` | 质量门 2 | 生成自定义质量检查清单（"需求的单元测试"） | 全路径 |
| `/speckit.tasks` | 拆解 | 把计划拆成可执行 task 列表 | 两者 |
| `/speckit.analyze` | 质量门 3 | 跨工件（spec/plan/tasks）一致性 + 覆盖率分析，**只读**（**tasks 后、implement 前**） | 全路径 |
| `/speckit.implement` | 执行 | 按 task 列表实际构建功能（生成代码） | 两者 |
| `/speckit.converge` | 收敛 | 校验代码 vs spec/plan/tasks，**有缺口就追加新 task 到 tasks.md，循环 implement + converge 直到报告 converged** | 两者 |

### 3.3 关键步骤详解

#### `/speckit.constitution` — 项目原则

定义团队"不可违反"规则，Agent 每次工作都参考：

```markdown
# Project Constitution
- All public APIs must have TypeScript types
- Test coverage must exceed 80%
- No direct database access from frontend
- Follow existing code patterns
```

#### `/speckit.specify` — 功能规范（What + Why，不写 How）

```text
/speckit.specify Build a user authentication system
  with JWT tokens, supporting login/logout/refresh,
  and role-based access control.
```

输出结构化 Spec：用户目标 → 使用场景 → 验收标准。

#### 三道质量门（全路径专属）

- **`/speckit.clarify`**：Agent 主动识别 Spec 模糊点逐个提问，答案直接烘焙进 Spec，避免后续歧义。
- **`/speckit.checklist`**：把规范本身当被测对象，生成"这个需求写全了吗"的检查清单。
- **`/speckit.analyze`**：在动手写代码前，对 spec / plan / tasks 三份工件做**一致性与覆盖率**交叉检查，报告冲突/遗漏/歧义。**只读** —— 发现问题回到源头修正后重跑。

#### `/speckit.tasks` — 可执行任务

把计划拆成细粒度 task，每个足够 Agent 单次完成：

```markdown
## Tasks
- [ ] Create User model with JWT fields
- [ ] Implement /auth/login endpoint
- [ ] Implement /auth/refresh endpoint
- [ ] Add RBAC middleware
- [ ] Write integration tests for auth flow
```

#### `/speckit.implement` + `/speckit.converge` — 执行与收敛

- `implement`：Agent 按依赖顺序遍历 `tasks.md` 逐个实现（可结合 Superpowers 强制 TDD）；大功能可分阶段 scope。
- `converge`：把代码与 spec/plan/tasks 对照，**发现缺口就把新 task 追加进 `tasks.md`，然后再跑 `implement` + `converge`，如此循环直到报告 `converged`** —— SDD"实现不漂移"的最后一道闭环保障。收敛后即可 review / 开 PR。

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
specify init            # 或 specify init taskify --integration copilot

# 2a. 短路径（小功能）——在 Claude Code / Copilot 中：
/speckit.specify "Build user auth with JWT"
/speckit.plan
/speckit.tasks
/speckit.implement        # Agent 逐个实现 task
/speckit.converge         # 校验实现与 Spec 对齐

# 2b. 全路径（生产级）——加 3 道质量门：
/speckit.constitution     # 设置项目原则
/speckit.specify "..."
/speckit.clarify          # 质量门1：回答 Agent 的澄清问题
/speckit.plan
/speckit.checklist        # 质量门2：生成质量检查清单
/speckit.tasks
/speckit.analyze          # 质量门3：跨工件一致性/覆盖率
/speckit.implement
/speckit.converge

# 3. implement 阶段可结合 Superpowers 强制 TDD
```

---

## 六、相关章节

- 对比总览：[Agent Spec Tools 三工具对比](README.md)
- 同栏目：[Superpowers](superpowers.md) / [OpenSpec](openspec.md)
- 概念层：[Harness Engineering](../harness-engineering/README.md) — Spec-Kit 是"规范型 Harness"
- 论文：[Spec Kit Agents (arXiv)](https://arxiv.org/html/2604.05278v1) — 多 Agent 架构形式化

---

## 📚 参考来源

- [GitHub Spec Kit 官方仓库](https://github.com/github/spec-kit) — 命令定义与 CLI
- [Spec Kit 官方文档站 · Quickstart](https://github.github.com/spec-kit/quickstart.html) — 短路径 vs 全路径 9 步命令序列（本次更新的一手来源）
- [AI 编程三剑客：Spec-Kit / OpenSpec / Superpowers 深度对比](https://juejin.cn/post/7605494530017165352) — 目录结构、安装流程交叉核实

---

> 📅 2026-07-08（2026-07-21 命令集更新为完整管线）· AI 工程实践 · Spec-Kit · 实战工具

← [返回: Agent Spec Tools 对比](README.md)
