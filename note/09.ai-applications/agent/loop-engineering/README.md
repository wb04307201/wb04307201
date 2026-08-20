<!--module:
  parent: 09.ai-applications
  slug: 09.ai-applications/agent/loop-engineering
  type: index-only
  category: Agent 子模块索引
  summary: Agent Loop 工程——自动修复策略 / 内置循环命令 / IDE 案例 / 验证器设计 4 大主题。
-->

# Loop 工程（Loop Engineering）

> ⬅️ [返回 09.ai-applications Agent 目录](../README.md)

## 📍 一句话定位

**Loop 工程 = Agent 循环执行机制**——围绕"Generator → Verifier → 反馈 → 改进"的闭环，4 大主题构成完整的工程实践体系：自动修复策略（按错误类型选择 prompt）+ 验证器设计（5 大客观反馈源）+ 内置循环命令（/goal · /loop · Ralph Wiggum）+ IDE 实战案例（Claude Code / Cursor / Devin / Aider）。

## 🗂️ 文章清单

| # | 主题 | 难度 | 路径 | 核心内容 |
|---|------|------|------|---------|
| 1 | 自动修复策略 | ⭐⭐⭐ | [auto-fix-strategy.md](./auto-fix-strategy.md) | Auto-Fix Loop 5 种按错误类型（语法/类型/lint/测试/运行时）的修复策略 + 重试预算 + 终止条件 + Verifier 选型 |
| 2 | 内置循环命令 | ⭐⭐ | [builtin-loop-commands.md](./builtin-loop-commands.md) | 2026 年 Claude Code `/goal` + `/loop`、Codex `/goal`、Ralph Wiggum 第三方工具的架构差异与选型指南 |
| 3 | IDE 集成案例 | ⭐⭐⭐⭐ | [ide-case-studies.md](./ide-case-studies.md) | Claude Code / Cursor / Devin / Aider 4 大 AI IDE 的 Loop 工程 + Verifier + 自动修复策略对比 |
| 4 | 验证器设计 | ⭐⭐⭐⭐ | [verifier-design.md](./verifier-design.md) | Verifier 5 大设计（测试/类型检查/lint/编译/运行时 5 大客观反馈源）+ 评分函数 + Auto-Fix Loop 灵魂 |

## 🔗 关联主题

- [../agent-architecture/](../agent-architecture/) — Agent 系统级架构（BPMN+AI），是 Loop 在企业流程中的体现
- [../agent-execution-patterns/](../agent-execution-patterns/) — 4 大执行模式（ReAct / Plan-and-Execute / DAG / Multi-Agent），Loop 是 Plan-Execute 模式的核心实现
- [../agent-reliability/](../agent-reliability/) — Agent 可靠性（失败恢复 + 监控），与 Verifier 设计形成"反馈 + 兜底"双保险
- [../coding-agents/](../coding-agents/) — 编程 Agent（Claude Code / Codex / OpenCode / OMP），Loop 工程的实际战场
- [../production-stability/](../production-stability/) — 生产稳定性（超时/熔断/重试预算），是 Loop 在生产环境的边界控制

## 📚 学习路径

1. **先理解 Loop 基础**：从 [auto-fix-strategy.md](./auto-fix-strategy.md) 开始，掌握"按错误类型选择修复策略"的核心思想——不是"错了就改"，而是"针对性 prompt + 特定上下文"
2. **再学 Verifier 设计**：读 [verifier-design.md](./verifier-design.md)，5 大客观验证源（测试/类型/lint/编译/运行时）+ 评分函数，理解 Loop 的"客观反馈"如何构造
3. **横向对比循环命令**：读 [builtin-loop-commands.md](./builtin-loop-commands.md)，理解 `/goal`（条件驱动）vs `/loop`（时间驱动）vs Ralph Wiggum（fresh context）的差异
4. **实战看 IDE 案例**：读 [ide-case-studies.md](./ide-case-studies.md)，Claude Code 4 层 Verifier、Cursor / Devin / Aider 的不同工程哲学
5. **生产环境考量**：跳到 [../production-stability/](../production-stability/)，看 Loop 在超时/熔断/成本控制下的边界条件

## 🎯 为什么 Loop 是 Agent 的灵魂？

LLM 单次推理有两个根本局限：

- **首次输出不一定对**：编译/类型/测试都可能失败
- **无自我修正能力**：模型不知道自己的错误

→ Loop 通过"Generator + Verifier + 反馈"形成闭环，把单次推理变成**迭代改进**，是 Agent 区别于普通 LLM 调用的核心特征。

## 🧭 4 大主题的知识拓扑

```text
        auto-fix-strategy（修复策略：how to fix）
              ↓
        verifier-design（验证器：how to know it's wrong）
              ↓
        builtin-loop-commands（命令调度：when to stop）
              ↓
        ide-case-studies（实战落地：real-world Loop）
```

## 📊 本节统计

> 本目录当前收录 4 篇子文章（auto-fix / builtin-loop / ide-case-studies / verifier-design），由 `find` 在 `2026-08-20` 校对。

---

← [返回 Agent 目录](../README.md)