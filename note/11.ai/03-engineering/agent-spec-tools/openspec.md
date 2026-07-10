<!--
module:
  parent: ai
  slug: ai/agent-spec-tools/openspec
  type: article
  category: 主模块子文章
  summary: OpenSpec：Fission AI 的轻量规范对齐框架，/opsx 命令 + AGENTS.md + 决策追溯。
-->

# OpenSpec — 轻量规范对齐协议

← 返回 [Agent Spec Tools 对比](README.md)

> [Fission AI 开源](https://github.com/Fission-AI/OpenSpec)。三个工具中最轻量的 —— npm 安装 + Markdown 规范 + 4 个核心命令，解决"需求只存在于聊天记录中丢失"的问题。

---
---

## 一、核心结论（TL;DR）

| 维度 | 内容 |
|------|------|
| **是什么** | 轻量 Spec-Driven Development 框架，Markdown 驱动 |
| **核心理念** | 人-Agent 先达成共识（propose），再实现（apply），再验证（verify） |
| **安装方式** | `npm install -g @fission-ai/openspec@latest` |
| **核心命令** | 9 个 `/opsx:*` 斜杠命令 |
| **目录结构** | `openspec/`（project / specs / changes / AGENTS.md） |
| **适合谁** | 小团队快速迭代 + 需要决策追溯的项目 |

---

## 二、安装与配置

### 2.1 安装

```bash
# 需要 Node.js 20.19.0+
npm install -g @fission-ai/openspec@latest
```

### 2.2 项目初始化

```bash
cd your-project
openspec init
```

`openspec init` 会：
1. 创建 `openspec/` 目录结构
2. 生成 `openspec/project.md`（项目上下文）
3. 生成 `AGENTS.md`（AI Agent 指令约定）
4. 根据你的 Agent 类型配置（Claude Code → `CLAUDE.md`，Cursor → 对应配置）

### 2.3 目录结构

```
openspec/
├── project/
│   └── project.md       # 项目全局上下文（架构 / 技术栈 / 约定）
├── specs/               # 规范源头（source of truth）
│   └── auth-spec.md     # 例：认证规范
├── changes/             # 变更提案（每个 change 一个目录）
│   └── add-jwt-auth/
│       ├── proposal.md  # 变更提案
│       ├── tasks.md     # 拆解的任务
│       └── spec.md      # 最终规范
└── AGENTS.md            # Agent 指令约定（格式 / 门禁 / 规则）
```

### 2.4 AGENTS.md

OpenSpec 的关键配置文件 —— 定义 Agent 必须遵守的约定：

```markdown
# Agent Conventions

## Workflow Gates
1. PROPOSE: 任何变更必须先写 proposal.md
2. APPLY: 只有 approved 的 proposal 才能实现
3. ARCHIVE: 实现完成后归档变更

## Spec Format
- proposal.md: 问题描述 + 方案 + 影响评估
- tasks.md: 可执行任务清单
- spec.md: 最终规范（归档后保留）

## Code Standards
- Follow existing patterns
- Add tests for new features
- Update documentation
```

---

## 三、9 个 `/opsx:*` 命令

| 命令 | 用途 | 频率 |
|------|------|------|
| `/opsx:propose` | 创建变更提案（proposal.md） | ⭐ 高频 |
| `/opsx:explore` | 探索代码库（propose 前先了解现状） | 中频 |
| `/opsx:apply` | 实现已批准的 spec | ⭐ 高频 |
| `/opsx:verify` | 验证实现是否符合 spec | ⭐ 高频 |
| `/opsx:archive` | 归档已完成的变更 | 中频 |
| `/opsx:new <name>` | 创建新变更目录 | 中频 |
| `/opsx:continue` | 继续已有的变更 | 中频 |
| `/opsx:ff` | 快进跳过中间步骤 | 低频 |
| `/opsx:sync` | 同步 spec 与当前实现 | 低频 |

### 核心工作流：4 步循环

```
1. /opsx:propose ──── 写变更提案（问题 + 方案 + 影响）
       ↓  人 review + 修改
2. /opsx:apply ────── Agent 按 spec 实现代码
       ↓
3. /opsx:verify ───── 对比实现 vs spec
       ↓  通过？
4. /opsx:archive ──── 归档变更（决策追溯保留）
```

---

## 四、典型使用流程

```bash
# 1. 安装 + 初始化
npm install -g @fission-ai/openspec@latest
openspec init

# 2. 在 Claude Code 中：
/opsx:explore                    # 先了解代码库现状
/opsx:propose                    # 写变更提案
# → 人 review proposal.md，提出修改意见
# → Agent 修改 proposal，达成共识

/opsx:apply                      # Agent 按 spec 实现
/opsx:verify                     # 验证实现 vs spec
/opsx:archive                    # 归档（决策历史保留）
```

---

## 五、OpenSpec 的独特优势

### 5.1 决策追溯

每个变更都有完整的 `proposal.md` → `tasks.md` → `spec.md` 记录。三个月后回看，能清楚知道**为什么做了这个决定**。

### 5.2 最轻量

| 对比 | OpenSpec | Spec-Kit | Superpowers |
|------|----------|----------|-------------|
| 安装 | `npm install` | `uv tool install` | 插件安装 |
| 依赖 | Node.js | Python + uv | Claude Code |
| 上手时间 | **5 分钟** | 15 分钟 | 10 分钟 |
| 学习曲线 | 4 个命令 | 5 个命令 + CLI | 14 个 Skill |

### 5.3 跨 Repo 支持

一个 change 可以跨多个 repo —— 适合微服务架构下跨服务变更。

### 5.4 Stores（Beta）

实验性功能：把 spec 保存到 AI 记忆框架中，跨会话保留上下文。

---

## 六、相关章节

- 对比总览：[Agent Spec Tools 三工具对比](README.md)
- 同栏目：[Superpowers](superpowers.md) / [Spec-Kit](spec-kit.md)
- 概念层：[Harness Engineering](../harness-engineering/README.md) — OpenSpec 是"反馈型 Harness"
- 训练材料：[training/lesson7/README6](../../training/lesson7/README6.md) — OpenSpec 实战训练
- Claude Code：[Claude Code 实践](../claude-code-practices/README.md) — CLAUDE.md + OpenSpec 配合使用

---

> 📅 2026-07-08 · AI 工程实践 · OpenSpec · 实战工具

← [返回: Agent Spec Tools 对比](README.md)
