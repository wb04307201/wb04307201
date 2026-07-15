<!--
module:
  parent: ai
  slug: ai/loop-engineering/builtin-loop-commands
  type: article
  category: 主模块子文章
  summary: 2026 年各 AI 编码工具的内置循环命令对比：Claude Code /goal + /loop、Codex /goal、Ralph Wiggum 第三方工具。
-->

# 内置循环命令对比：/goal · /loop · Ralph Wiggum

← 返回 [Loop Engineering](README.md)

> 2026 年 Claude Code 和 Codex CLI 都内置了自主循环命令，不再需要第三方工具。本文对比三种循环方式的架构差异和选型指南。

---

## 一、三种循环方式速览

| 维度 | Claude Code `/goal` | Claude Code `/loop` | Ralph Wiggum Loop |
|------|-------------------|--------------------|--------------------|
| **驱动方式** | 条件驱动（达成才停） | 时间驱动（按间隔重复） | Bash while 循环 |
| **Context 行为** | 同一 session，**累积** | 每轮独立 session | 每轮 **fresh context** |
| **停止机制** | 外部 Evaluator 确认 | 自己判断"没事了"就停 | 手动 Ctrl+C 或达标 |
| **长任务退化** | ⚠️ 会（context rot） | 不会（每轮独立） | 不会（fresh context） |
| **需要可验证终点** | ✅ 是 | ❌ 否 | 可选 |
| **内置 / 第三方** | Claude Code 内置 | Claude Code 内置 | 第三方 npm 包 |
| **Codex 对应** | `/goal`（v0.128.0+） | 无直接对应 | 同样适用 |
| **OpenCode 对应** | 无内置 | 无内置 | 同样适用 |

---

## 二、架构对比

### `/goal`：Generator/Evaluator 循环（同 session）

```text
Turn 1: Claude 工作（读文件 → 改代码 → 跑测试）
         ↓
    Evaluator（快速小模型）：目标达成了没？
         ↓ 没达成
Turn 2: Claude 继续工作（context 追加 Turn 1）
         ↓
    Evaluator 检查...
         ↓ 达成 ✅
    停止
```

**问题**：context 不断累积 → 注意力分散 → 质量下降（context rot）。

### `/loop`：时间调度器（独立 session）

```text
T=0:     触发 → Claude 执行任务 → 完成 → 等待
T=30min: 触发 → Claude 执行任务 → 完成 → 等待
T=60min: 触发 → Claude 执行任务 → 完成 → 等待
```

**优势**：每轮独立 session，不会 context rot。
**限制**：每轮是无状态的，不记得上一轮做了什么。

### Ralph Wiggum：Fresh Context 循环（独立进程）

```text
Iteration 1: 新进程 → 读磁盘文件 → 工作 → 写回磁盘 → 进程结束
Iteration 2: 新进程 → 读磁盘文件（含上轮修改）→ 工作 → 写回 → 结束
Iteration N: ...
```

**优势**：每轮 fresh context + 文件系统作持久记忆，不会退化。
**限制**：需要第三方工具或自己写 bash。

---

## 三、场景决策树

```text
需要 Agent 自主运行？
├─ 有明确终点（可机器验证）？
│   ├─ 预计 < 20 轮 → /goal（内置，最方便）
│   └─ 预计 > 20 轮 → Ralph Wiggum（避免 context rot）
├─ 需要周期性执行？
│   └─ /loop（内置调度器）
└─ 两者都要？
    └─ /loop + /goal 组合（定时触发 + 跑到完成）
```

### 场景速查表

| 场景 | 推荐 | 命令示例 |
|------|------|---------|
| 修完所有 failing tests | `/goal` | `/goal "npm test 全部通过"` |
| 每 30 分钟检查 CI | `/loop` | `/loop 30m "检查 CI 有没有新失败"` |
| 写完一个 feature | `/goal` | `/goal "PR #42 的 review comments 都处理了"` |
| 监控线上日志 | `/loop` | `/loop 10m "扫描最近日志有没有 ERROR"` |
| 重构大模块（50+ 文件） | Ralph Wiggum | `while :; do claude "继续重构" ; done` |
| 持续保持代码质量 | `/loop` + `/goal` | `/loop 1h "/goal 'eslint 0 errors'"` |

---

## 四、`/goal` 使用技巧

### 4.1 语法

```text
/goal <完成条件>     ← 设置目标并开始工作
/goal               ← 查看当前目标、轮次、Token 消耗
/goal clear         ← 手动停止（别名：stop / off / reset / cancel）
```

### 4.2 完成条件必须可机器验证

```text
✅ "所有 47 个测试通过且 npm run build 退出码 0"
✅ "eslint 报告 0 errors 0 warnings"
✅ "CHANGELOG.md 包含 v2.1.0 的条目"
❌ "代码质量变好"（Evaluator 无法判断）
❌ "用户体验更好"（不可量化）
```

### 4.3 搭配 Auto Mode 实现完全无人值守

```text
Shift+Tab 切换到 Auto Mode（跳过权限确认）
+ /goal "所有测试通过"
= Claude 完全自主工作直到完成
```

### 4.4 Context Rot 的应对

```text
症状：/goal 跑了 30+ 轮后，Claude 开始犯低级错误
修复：
1. /goal clear → /clear → 重新 /goal（手动重置）
2. 用 subagent 模式（每个 subagent 独立 context）
3. 切到 Ralph Wiggum（每轮天然 fresh context）
```

---

## 五、`/loop` 使用技巧

### 5.1 语法

```text
/loop <间隔> <任务>     ← 按间隔重复执行
/loop 5m "检查部署状态"  ← 每 5 分钟检查一次
/loop 1h "/goal 'lint 0 errors'" ← 每小时触发一次 /goal
```

### 5.2 与 `/goal` 的关键区别

| | `/goal` | `/loop` |
|---|---------|---------|
| 一句话 | **做完一件事** | **盯着一个东西** |
| 驱动 | 条件驱动 | 时间驱动 |
| 停止 | Evaluator 确认达成 | 自己判断"这轮没事了" |
| 需要终点 | ✅ 必须可验证 | ❌ 不需要 |

---

## 六、各工具支持矩阵

| 工具 | `/goal` | `/loop` | Ralph Wiggum | 备注 |
|------|:---:|:---:|:---:|------|
| **Claude Code** | ✅ v2.1.139+ | ✅ 内置 | ✅ 兼容 | 最完整 |
| **Codex CLI** | ✅ v0.128.0+ | ❌ | ✅ 兼容 | 无 /loop |
| **OpenCode** | ❌ | ❌ | ✅ 兼容 | 仅单次 agentic loop |
| **Cursor** | ❌ | ❌ | ❌ | 社区请求中 |
| **Gemini CLI** | ❌ | ❌ | ✅ 兼容 | 支持 7 种 Provider |

---

## 七、相关章节

- 概念层：[Loop Engineering 综述](README.md) — 循环哲学 + 3 大组件 + 4 大失败模式
- 实战层：[Ralph Wiggum Loop](ralph-wiggum-loop.md) — 第三方 CLI 工具详细用法
- 面试题：[13.split-hairs Loop Engineering](../../../13.split-hairs/11.ai/loop-engineering/README.md)
- 关联：[大模型思维工程 5 问](../llm-production-thinking/README.md) — 成本 5 层路由（Loop 的成本控制）

---

← [返回: Loop Engineering](README.md) · 📅 2026-07-10
