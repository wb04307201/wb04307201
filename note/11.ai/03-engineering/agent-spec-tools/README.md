<!--
module:
  parent: ai
  slug: ai/agent-spec-tools
  type: index
  category: 主模块子文章
  summary: Agent Spec Tools：Superpowers / Spec-Kit / OpenSpec 三工具安装、配置、使用与选型对比。
-->

# Agent Spec Tools — 三工具对比与选型

← 返回 [工程实践](../README.md)

> 2025-2026 年 AI 编程三大规范工具：让 Agent 从"随意写代码"进化到"先规划再动手"。它们在不同层面解决不同问题，可以组合使用。

---
---

## 一、核心结论（TL;DR）

| 维度 | [Superpowers](superpowers.md) | [Spec-Kit](spec-kit.md) | [OpenSpec](openspec.md) |
|------|------|------|------|
| **创造者** | Jesse Vincent (obra) | GitHub 官方 | Fission AI |
| **一句话定位** | 工作流执行引擎（怎么干活） | 企业级规范管线（写什么规范） | 轻量规范对齐协议（确认写什么） |
| **安装方式** | Claude Code 插件 | Python CLI（uv） | npm CLI |
| **Agent 支持** | Claude Code / Cursor | 30+ Agent（Copilot / Claude / Cursor / Gemini…） | Claude Code / Cursor / 通用 |
| **核心命令数** | 14 个 Skill | 5 个 `/speckit.*` 命令 | 9 个 `/opsx:*` 命令 |
| **TDD 强制** | ✅ 必须 RED→GREEN | ❌ 不强制 | ❌ 不强制 |
| **子 Agent 编排** | ✅ 内置并行分发 | ❌ | ❌ |
| **GitHub Stars** | 89K+ | GitHub 官方项目 | 社区增长中 |
| **适合谁** | 追求代码质量的个人/团队 | 企业团队 + 多 Agent 标准化 | 小团队快速迭代 + 决策追溯 |

---

## 二、分层架构 —— 它们不竞争，是互补

```
┌────────────────────────────────────────────────────────┐
│  LAYER 3: 工作流执行（HOW）                             │
│  Superpowers — 约束 Agent 怎么干活                      │
│  （TDD 强制 · 并行子 Agent · 7 阶段流程 · Code Review） │
├────────────────────────────────────────────────────────┤
│  LAYER 2: 规范管线（WHAT）                              │
│  Spec-Kit — 结构化"要做什么"的规范                      │
│  （constitution → specify → clarify → plan → tasks）    │
├────────────────────────────────────────────────────────┤
│  LAYER 1: 规范对齐（AGREEMENT）                         │
│  OpenSpec — 确保人和 Agent 对"做什么"达成共识           │
│  （propose → apply → verify → archive）                 │
└────────────────────────────────────────────────────────┘
```

**关键洞察**：三个工具可以**组合使用** ——
- 用 Spec-Kit / OpenSpec 定义"做什么"
- 用 Superpowers 约束 Agent "怎么做"
- 最终实现 Spec-Driven Development（SDD）

---

## 三、选型决策树

```
你的需求是什么？
│
├─ "我要 Agent 严格按 TDD 写代码"
│   → Superpowers（唯一强制 TDD 的工具）
│
├─ "我的团队用多种 Agent，需要统一规范流程"
│   → Spec-Kit（支持 30+ Agent，GitHub 生态集成）
│
├─ "我想最快上手，轻量就好"
│   → OpenSpec（npm install + 4 个核心命令）
│
├─ "我要最大程度的代码质量"
│   → Spec-Kit + Superpowers 组合
│     （Spec-Kit 定义规范 + Superpowers 强制 TDD 执行）
│
└─ "我先试试 SDD 是什么感觉"
    → OpenSpec（最简单，5 分钟上手）
```

---

## 四、三工具共同点：SDD 循环

三个工具都实现了同一个核心循环 —— **Spec-Driven Development（SDD）**：

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Specify │────▶│   Plan   │────▶│  Execute │────▶│  Verify  │
│  定义规范 │     │  拆解计划 │     │  执行实现 │     │  验证对齐 │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      ▲                                               │
      └───────────────────────────────────────────────┘
```

| 阶段 | Superpowers | Spec-Kit | OpenSpec |
|------|-------------|----------|----------|
| **Specify** | `brainstorming` skill | `/speckit.specify` | `/opsx:propose` |
| **Plan** | `writing-plans` skill | `/speckit.plan` | `/opsx:propose`（内含计划） |
| **Execute** | `dispatching-parallel-agents` + TDD | `/speckit.tasks` → Agent 实现 | `/opsx:apply` |
| **Verify** | `verification-before-completion` | （Agent 自验） | `/opsx:verify` |

---

## 五、各工具深度指南

| 工具 | 内容 | 链接 |
|------|------|------|
| **Superpowers** | 安装 + 14 内置 Skill + 7 阶段工作流 + 子 Agent 编排 | [→ superpowers.md](superpowers.md) |
| **Spec-Kit** | 安装 + 5 命令 SDD 管线 + 跨 Agent 兼容 + 企业用法 | [→ spec-kit.md](spec-kit.md) |
| **OpenSpec** | 安装 + /opsx 命令 + 目录结构 + AGENTS.md + 快速迭代 | [→ openspec.md](openspec.md) |

---

## 六、与其他章节的关系

- 概念层：[Harness Engineering](../harness-engineering/README.md) — 这三个工具都是 Harness 的具体实现
- 同栏目：[Claude Code 实践](../claude-code-practices/README.md) — Skill 设计方法论 + Hit Rate 优化
- 实战：[生产级 Agent](../production-agent/README.md) — 生产环境的 Agent 工程实践
- 循环：[Loop Engineering](../loop-engineering/README.md) — Agent 循环调用 + [Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md)
- 训练：[training/lesson7](../../training/lesson7/README.md) — Spec-Kit / OpenSpec 训练材料

← [返回: AI 知识体系 · agent-spec-tools](README.md)
