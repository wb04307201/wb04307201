<!--
question:
  id: 11.ai-harness-engineering
  topic: 11.ai
  difficulty: ⭐⭐⭐⭐
  frequency: 中频
  scenario_type: 性能对比
  tags: [11.ai, Harness, harness]
-->

# Harness Engineering — 给 Agent 套上缰绳面试深挖

> 一句话定位：Harness Engineering 是"用规范和流程约束 Agent"的工程实践，让 Agent 在可控轨道上发挥更强能力。完整概念见 [主模块 Harness Engineering](../../../11.ai/03-engineering/harness-engineering/README.md)。

---

## 引子：AI Agent 删了生产数据库

```text
2024 年某 SaaS 公司 Incident：
AI Agent 接到任务："清理重复订单"
Agent 直接执行：DELETE FROM orders WHERE created_at < 7 days
结果：3 万条真实订单被删（其中 8000 条是合法的、只是日期格式异常）
后果：备份冷备 4 小时前的，公司赔款 80 万。
```

**真相**：AI Agent 没有"刹车"。

Harness 是答案——**给 Agent 套上缰绳**：

- **规范**：项目里写 `.claude/rules.md`，Agent 启动强读
- **流程**：CI/CD、代码 review，必须有人 review 才能 merge
- **工具**：Hook 在"提交前"自动跑测试 / lint / 安全扫描
- **反馈**：每次任务结束收集效果，更新规则

**没有 Harness，Agent 只是更快的 Bug 制造机**。

## 一、4 大 Harness 类型速记

| 类型 | 例子 | 一句话 |
|------|------|--------|
| **规范型** | OpenSpec / Spec Kit / `.claude/rules.md` | Agent 启动时强制读项目规范 |
| **流程型** | CI/CD Pipeline | 强制走自动化测试 |
| **工具型** | Hooks / Callbacks | 关键节点自动触发检查 |
| **反馈型** | Evaluation Loop | 持续评估输出质量 |

```
Harness = 规范 + 流程 + 工具 + 反馈
```

---

## 二、面试陷阱

### 陷阱 1：以为 Harness = Prompt
- **真相**：Harness 是 Agent 工作环境的"基础设施"，比 Prompt 范围大得多 —— Prompt 只是 Harness 的输入之一。

### 陷阱 2：以为 Harness 限制 Agent 能力
- **真相**：好的 Harness **让 Agent 在约束下发挥更强能力**，而不是变弱。约束消除"幻觉/危险操作/不合规"。

### 陷阱 3：以为 OpenSpec 只是文档
- **真相**：OpenSpec 是 Agent **可读可校验**的规范协议，包含自动校验机制（CI 跑规范检查），不只是给人看的文档。

### 陷阱 4：忽视"可观测"
- **真相**：Trace / Logging / Evaluation 全程可观测是 Harness 的关键，Agent 自己跑任务看不到中间过程等于黑盒。

---

## 三、4 大原则速记

1. **显式优于隐式**：把规范写成文件，Agent 启动时强制读取，别让它"自己理解"
2. **自动化优于人工**：Linter + 单元测试 + AI Review 自动检查，别让人类 review 每行
3. **可观测优于黑盒**：Trace / Logging / Evaluation 全程记录
4. **渐进优于一步到位**：拆解任务 → 逐步执行 → 每步可检查

---

## 四、反直觉点

- **Harness 不是限制，而是赋能**：Claude Code / Cursor 的高效正是因为 Harness（OpenSpec + CI + Hooks + Eval）做得好，不是 Agent 本身。
- **"自动化测试"是 Harness 的脊柱**：没有测试兜底的 Agent 等于裸奔。

---

## 五、30 秒面试话术

> Harness Engineering 是 2026 年 AI 工程第三阶段，演进路径是 Prompt → Context → Harness → Loop。
>
> Harness 借喻"马具"，是"约束 Agent 行为的规范和工具"。包含 4 大类型：规范型（OpenSpec / Spec Kit）、流程型（CI/CD Pipeline）、工具型（Hooks / Callbacks）、反馈型（Evaluation Loop）。
>
> 核心原则：显式优于隐式、自动化优于人工、可观测优于黑盒、渐进优于一步到位。
>
> 我们团队用 OpenSpec + Cursor + GitHub Actions，让 AI 写代码时必须遵守项目规范、自动跑测试、AI 互相 review。

---

## 六、深度阅读

- 主模块：[Harness Engineering](../../../11.ai/03-engineering/harness-engineering/README.md)
- 上一步：[Context Engineering](../context-engineering/README.md)
- 关联：[Loop Engineering](../loop-engineering/README.md)
- 实战：[Claude Code 实践](../../../11.ai/03-engineering/claude-code-practices/README.md)

---

> 📅 2026-06-30 · 咬文嚼字 · 2026 面试热点 · ⭐⭐⭐⭐

← [返回: 咬文嚼字 · harness-engineering](README.md)
