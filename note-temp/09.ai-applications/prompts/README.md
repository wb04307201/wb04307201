# Prompts（Prompt 工程）

> **定位**：MOC——Prompt 工程主题索引，覆盖 Prompt 设计方法 / 模板 / 实战 / 系统提示词。
> **继承规范**：[../SPEC.md](../SPEC.md)

## 主题清单

| # | 子主题 | 路径 | 摘要 |
|---|--------|------|------|
| 1 | Prompt 工程综述 | [prompt-engineering/](prompt-engineering/README.md) | Prompt 设计方法论 + 模板库 + 代码注释风格 + Grok 系统提示词 |
| 2 | 模板修复实战 | [fix-prompt-templates.md](fix-prompt-templates.md) | Prompt 模板常见问题诊断与修复 |

## 子主题详情

### `prompt-engineering/`（综述 + 三子目录）

| 子目录 | 内容 | 入口 |
|--------|------|------|
| **README** | 综述 + 模板库 + 选型决策 | [README.md](prompt-engineering/README.md) |
| **code-comment-styles** | 代码注释风格化 Prompt（为 LLM 生成符合团队规范的代码注释） | [code-comment-styles/README.md](prompt-engineering/code-comment-styles/README.md) |
| **grok-system-prompt** | Grok 系统提示词分析 | [grok-system-prompt/README.md](prompt-engineering/grok-system-prompt/README.md) |
| **prompt-templates** | Prompt 模板库（任务分类 / 角色定义 / 输出格式） | [prompt-templates/README.md](prompt-engineering/prompt-templates/README.md) |

## 阅读路径

```text
先读综述             prompt-engineering/README（方法论 + 模板 + 选型）
    ↓
按需深入             code-comment-styles / grok-system-prompt / prompt-templates
    ↓
实战修复             fix-prompt-templates（常见问题诊断）
```

## 关联主题

- [../agent/](../agent/) — Agent 架构（Prompt 是 Agent 的输入）
- [../rag/](../rag/) — RAG（Prompt 与 RAG 的协同）
- [../eval/](../eval/) — 评估方法（Prompt 效果评估）
- [../../08.ai-foundations/](../../../note-temp/08.ai-foundations/) — AI 基础

## 尚未迁移的 Prompt 相关章节

以下 Prompt 相关主题仍在迁移前位置（Phase 8 后将切到 `note-temp/<planned-path>` 占位），待后续任务迁入本 MOC：

- ⚠️ Function Calling（结构化 Prompt 输出） — `[../agent/spec-tools/function-calling/](../agent/spec-tools/function-calling/README.md)`（待 Phase 1+ 迁入）
- ⚠️ Context Engineering（广义 Prompt 设计） — `[./context-engineering/](./context-engineering/README.md)`（待 Phase 1+ 迁入）

---

← [返回 09.ai-applications](../README.md)
