<!--
module:
  parent: ai
  slug: ai/llm-control-evolution
  type: article
  category: 主模块子文章
  summary: LLM 驾驭演进史：Prompt → Context → Harness → Loop 4 阶段叙事
-->

# LLM 驾驭演进史：从 Prompt 到 Loop 的 4 个阶段

← 返回 [架构设计](../README.md)

> 2023 → 2026+ AI 工程的演化主线：**自始自终都是在"驾驭"**。
> 每一次升级，都把"驾驭"的责任从人转交给更高级的抽象。

---

## 一、阶段全景

| 阶段 | 主导者 | 工具 | 何时需要升级 |
|------|--------|------|-------------|
| [Prompt Engineering](../../02-technology-stack/prompt-engineering/README.md) | 人类 | 提示词技巧（8 大核心） | 一句话能搞定时 |
| [Context Engineering](../../02-technology-stack/context-engineering/README.md) | Agent | RAG + Memory + Tools | 需要长期记忆/工具时 |
| [Harness Engineering](../../03-engineering/harness-engineering/README.md) | 规范/流程 | OpenSpec / Spec-Kit / CLAUDE.md | Agent 行为不可控时 |
| [Loop Engineering](../../03-engineering/loop-engineering/README.md) | 调度器 | 状态机 + 重试 + 终止条件 | 任务超长复杂时 |

> 一句话：**人类 → Agent → 规范 → 调度器**，驾驭责任逐级上移。

---

## 二、演进驱动力：为什么每次都要升级？

### 2.1 Prompt Engineering 的天花板

人类手写 Prompt 有 3 个难以突破的边界：

1. **单次性**：每条 Prompt 只对应当前一次对话，无法累积经验
2. **静态上下文**：无法动态注入知识库 / 记忆 / 工具结果
3. **无工具**：LLM 只能"动嘴"，不能"动手"

边界显现后，必须把"装配上下文"的责任转交给 Agent。

### 2.2 Context Engineering 的兴起

2024 年 Agent 时代到来：从单次对话到"持续上下文"。

```text
Prompt Engineering:   用户 → [一句话 Prompt] → LLM
Context Engineering:  Agent → [系统提示 + RAG + Memory + Tools] → LLM
```

**核心转变**：从"人写一句话"变成"Agent 自动编排所有信息"。但 Context Engineering 解决的是"给什么信息"，没解决"怎么约束 Agent 行为"。

### 2.3 Harness Engineering 的爆发

2025 年 Agent 能力 ↑ → 行为不可控 → 需要规范兜底。

当 Agent 强大到可以自己写代码、改文件、跑命令时，"行为不可预测"就成了生产环境的最大风险。Harness 通过 4 大手段约束 Agent：

| 手段 | 例子 |
|------|------|
| **规范型** | OpenSpec / `.claude/rules.md` / CLAUDE.md |
| **流程型** | CI/CD Pipeline / Code Review / Auto Test |
| **工具型** | Hooks / Callbacks / Sandbox |
| **反馈型** | LLM-as-Judge / Evaluation Loop |

Harness Engineering 解决"如何让 Agent 在可控轨道上发挥最大能力"。

### 2.4 Loop Engineering 的反直觉

2026+ 当任务超长：循环调用反而比"一次性大 Prompt"更可靠。

直觉上"把任务写在一段 Prompt 里一次完成"更高效，但实际生产中：

- **大 Prompt 容易失焦**：长 Context 中"Lost in the Middle"
- **失败难以调试**：一次性失败无法定位哪一步出问题
- **资源不可控**：单次调用消耗不可预测

Loop Engineering 反其道而行之：**小步快跑 + Harness 兜底 + 自动终止**。把"完成任务"分解为多轮"小 Agent 调用"，每轮验证、每轮反馈、每轮终止条件清晰。

🆕 **实战深度**（写代码 → 跑测试 → 自动修复闭环）：见 [loop-engineering/auto-fix-strategy](../../03-engineering/loop-engineering/auto-fix-strategy.md) —— 5 修复策略 + Verifier 5 大源 + Claude Code/Cursor/Devin/Aider 4 IDE 实战 + 修复 prompt 模板。

---

## 三、何时该升级到下一阶段（决策树）

```text
项目复杂度 ↑ → 驾驭抽象 ↑
        │
   一句话搞定？
        │
   ├─ 是 → Prompt Engineering（停在这里）
        │
   └─ 否 → 需要记忆/工具？
              │
              ├─ 是 → Context Engineering
              │
              └─ 否 → Agent 行为不可控？
                        │
                        ├─ 是 → Harness Engineering
                        │
                        └─ 否 → 任务超长？
                                  │
                                  └─ 是 → Loop Engineering
```

**决策口诀**：

| 信号 | 升级到 |
|------|--------|
| 任务越写越长仍跑偏 | Context Engineering（补上下文） |
| Agent 自己跑飞、无据可循 | Harness Engineering（套规范） |
| 任务太长、Context 爆炸 | Loop Engineering（拆循环） |

---

## 四、与现有模块的关系

- **11.ai L2 技术栈** → 单一阶段的实现细节（如 Prompt 8 大技巧、Context 5 原则）
- **本 README** → 全局演化的架构视角（推荐先读）
- **11.ai L3 工程实践** → 工程化生产落地的具体抓手（Claude Code / Production Agent / Loop）
- **12.story 系列** → 餐厅叙事的实战案例（[38 RAG](../../../12.story/36-rag-retrieval-augmented-generation.md) / [41 私有化](../../../12.story/39-ai-private-deployment.md) / [42 Prompt 工程](../../../12.story/40-prompt-engineering.md) 等）

### 阅读路径建议

```text
先读本 README（5 分钟建立全景）
  ↓
按需跳读 4 个子 README（每个 10-15 分钟）
  ↓
再读 11.ai L4 架构 / 12.story 实战 / 13.split-hairs 面试深挖
```

---

## 五、反模式

- ❌ **一上来就 Loop / Harness 但 Prompt 没写好** → 过度工程
  - 错把"流程复杂度"当"Prompt 不行"的解药
  - 修复路径：先把 Prompt 打磨到能跑通 50% 案例
- ❌ **Prompt 写得很花但缺 Harness** → Agent 跑飞无据可循
  - 错把"提示词工程"当"万灵药"
  - 修复路径：补 OpenSpec + Hooks + 自动测试
- ❌ **只用 Context Engineering 不用 Loop** → 长任务必失败
  - 错把"塞更多 Context"当"解决长任务"
  - 修复路径：拆任务 + Loop + Harness 兜底

---

## 六、2026+ 趋势

- **Harness-as-Code**：规范本身可版本化、可测试
  - `.claude/rules.md` 进 Git / Harness 配置可单测 / CI 验证规范有效性
- **Multi-Agent Harness**：多个 Agent 互相约束（Harness 升级到群体层）
  - 编码 Agent 受测试 Agent 约束 / 规划 Agent 受执行 Agent 反馈约束
- **Self-Improving Loop**：Loop 调用结果反哺 Harness 规范
  - 失败案例自动提炼为 Harness 规则 / 成功的 prompt 模板自动沉淀到 Context

---

## 📊 本节统计

- **4 阶段对应**：4 个串联 README（Prompt / Context / Harness / Loop）
- **覆盖概念**：4 大 AI 工程范式
- **决策节点**：4 个升级触发条件
- **前置阅读**：建议先读本 README 再看 4 个子 README

---

## 相关章节

- 同分类：[Agent 架构（DAG vs ReAct）](../agent-architecture/README.md) — 4 阶段落地的具体架构
- 同分类：[Agent Memory 架构](../agent-memory/README.md) — Memory 演进（Prompt 期无 → Context 期短期 → Harness 期长期 → Loop 期自动分层）
- 同分类：[智能系统分层](../intelligent-system-layers/README.md) — Harness / Loop 在系统中的位置
- 兄弟子：[Harness Engineering](../../03-engineering/harness-engineering/README.md) · [Loop Engineering](../../03-engineering/loop-engineering/README.md)
- 上下文子：[Prompt Engineering](../../02-technology-stack/prompt-engineering/README.md) · [Context Engineering](../../02-technology-stack/context-engineering/README.md)
- 实战叙事：[12.story #42 Prompt 工程](../../../12.story/40-prompt-engineering.md) · [38 RAG](../../../12.story/36-rag-retrieval-augmented-generation.md)

← [返回: L4 架构设计](../README.md)
