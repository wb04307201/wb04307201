<!--
module:
  parent: ai
  slug: ai/agent-spec-tools/superpowers
  type: article
  category: 主模块子文章
  summary: Superpowers：Claude Code 最热门的 Skill 插件，强制 TDD + 7 阶段工作流 + 子 Agent 编排。
-->

# Superpowers — 强制 TDD 的工作流执行引擎

← 返回 [Agent Spec Tools 对比](README.md)

> [Jesse Vincent (obra)](https://github.com/obra) 开发，[GitHub 89K+ Stars](https://github.com/obra/superpowers)。不构建 Agent，而是**约束 Agent 怎么干活** —— 用 14 个内置 Skill 强制执行 7 阶段开发流程。

---
---

## 一、核心结论（TL;DR）

| 维度 | 内容 |
|------|------|
| **是什么** | Claude Code 插件（也支持 Cursor），用 Skill 强制专业软件工程流程 |
| **核心理念** | 停止 "vibe coding"，Agent 必须：先规划 → 写测试 → 再实现 |
| **内置 Skill** | 14 个（brainstorming / writing-plans / TDD / parallel-agents / code-review…） |
| **7 阶段流程** | Brainstorm → Specify → Plan → TDD → Implement → Review → Finalize |
| **杀手特性** | 强制 RED→GREEN TDD 循环 + 并行子 Agent 分发 |
| **支持平台** | Claude Code（主）、Cursor |

---

## 二、安装与配置

### 2.1 安装

```bash
# 方式 1: 官方插件市场（推荐）
/plugin install superpowers@claude-plugins-official

# 方式 2: 通过 marketplace
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### 2.2 配置

安装后 Skill 自动注册。无需额外配置 —— Skill 通过关键词或斜杠命令自动触发。

**自定义 Skill**：放在项目的 `.claude/skills/` 目录下即可。

**社区 Skill 扩展包**：
```bash
# obra/superpowers-skills 仓库有社区贡献的额外 Skill
# https://github.com/obra/superpowers-skills
```

**中文本地化**：[jnMetaCode/superpowers-zh](https://github.com/jnMetaCode/superpowers-zh)（20 个 Skill 含中文说明）。

---

## 三、14 个内置 Skill

| Skill | 触发场景 | 做什么 |
|-------|---------|--------|
| `brainstorming` | "我想做 X" | 交互式探索想法，生成 mockup |
| `writing-plans` | 规划阶段 | 把工作拆成 ~11 个具体 task |
| `executing-plans` | 执行阶段 | 按计划逐个执行 task |
| `test-driven-development` | 实现阶段 | **强制 RED→GREEN TDD 循环** |
| `dispatching-parallel-agents` | 并行工作 | 分发子 Agent（每个 fresh context） |
| `subagent-driven-development` | 委派任务 | 把 task 委派给专门的子 Agent |
| `systematic-debugging` | 出 bug 时 | 结构化调试方法论 |
| `writing-skills` | 创建新 Skill | Meta-skill：怎么写 Skill |
| `requesting-code-review` | 请求 review | 发起结构化 code review |
| `receiving-code-review` | 收到 review | 处理 review 反馈 |
| `verification-before-completion` | 完成前 | 验证实现是否符合 spec |
| `using-git-worktrees` | 隔离工作 | Git worktree 隔离开发 |
| `finishing-a-development-branch` | 收尾 | 完成分支并合并 |
| `using-superpowers` | 会话开始 | 加载 Skill 系统本身 |

---

## 四、7 阶段工作流

Superpowers 的核心价值是**强制执行 7 阶段流程**，不让 Agent 跳过规划直接写代码：

```
1. Brainstorm ─── 交互式探索，生成 mockup
       ↓
2. Specify ────── 写出明确的功能规范
       ↓
3. Plan ────────── 拆分成 ~11 个具体 task
       ↓
4. TDD ─────────── 每个 task 先写失败测试（RED）
       ↓
5. Implement ──── 写最少代码让测试通过（GREEN）
       ↓
6. Review ──────── 结构化 code review
       ↓
7. Finalize ────── 验证 + 合并 + 收尾
```

### 关键：TDD 强制

这是 Superpowers 和其他工具最大的区别：

```
传统 Agent：  "请实现 LRU Cache" → Agent 直接写代码（可能写错）
Superpowers： "请实现 LRU Cache" → Agent 必须先写测试（RED）→ 写最小实现（GREEN）→ 继续下一个
```

---

## 五、子 Agent 并行编排

`dispatching-parallel-agents` Skill 让 Agent 可以分发子任务：

```
主 Agent
  ├── 子 Agent 1: 实现认证模块（fresh context + TDD）
  ├── 子 Agent 2: 实现数据库层（fresh context + TDD）
  └── 子 Agent 3: 写 API 测试（fresh context + TDD）
```

每个子 Agent 拿到干净的 context window，避免 context 累积退化 —— 类似 [Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md) 的 Fresh Context 架构。

---

## 六、典型使用流程

```bash
# 1. 开始新功能（触发 brainstorming）
你: "我想给项目加一个用户认证系统"
# → Superpowers 自动触发 brainstorming skill

# 2. 规划（触发 writing-plans）
# → Agent 把功能拆成 ~11 个 task

# 3. 分发（触发 dispatching-parallel-agents）
# → Agent 分发子 Agent 并行工作

# 4. 每个子 Agent 内部（触发 TDD）
# → 写失败测试 → 写最小实现 → 测试通过 → 下一个 task

# 5. 完成前（触发 verification-before-completion）
# → 验证所有实现是否符合 spec
```

---

## 七、相关章节

- 对比总览：[Agent Spec Tools 三工具对比](README.md)
- 同栏目：[Spec-Kit](spec-kit.md) / [OpenSpec](openspec.md)
- 概念层：[Harness Engineering](../harness-engineering/README.md) — Superpowers 是 Harness 的实战体现
- Skill 设计：[Skill 设计方法论](../claude-code-practices/skill-design.md) — 怎么写自己的 Skill
- 循环：[Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md) — 子 Agent 的 Fresh Context 架构

---

> 📅 2026-07-08 · AI 工程实践 · Superpowers · 实战工具

← [返回: Agent Spec Tools 对比](README.md)
