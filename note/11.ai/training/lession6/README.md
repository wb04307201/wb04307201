# 📝 Google Cloud Tech 推文整理：5种每个ADK开发者都应掌握的Agent Skill设计模式

> 原文来源：Google Cloud Tech (@GoogleCloudTech)  
> 原文链接：https://x.com/GoogleCloudTech/status/2033953579824758855

---

## 🔍 背景：从"格式之争"到"内容设计"

随着超过30种主流智能体工具（如 Claude Code、Gemini CLI、Cursor 等）已统一采用 **SKILL.md + YAML元数据 + references/assets目录** 的标准化布局，"怎么写技能文件"的格式问题已基本解决。

**真正的挑战在于：内容如何设计？**

同样的 SKILL.md 外壳，内部逻辑可能千差万别。一个封装 FastAPI 规范的 Skill，与一个四步文档生成流水线，从外部看结构相同，但运作方式完全不同。

基于对生态系统的深入研究（涵盖 Anthropic、Vercel、Google 等机构的工程实践），本文提炼出 **5种可复用的Agent Skill设计模式**，帮助开发者构建更可靠、可维护的智能体工作流。

---

## 🎯 五种核心设计模式详解

### 1️⃣ Tool Wrapper（工具包装器）
> **核心价值**：让Agent按需加载专业知识，实现"即用即学"

**适用场景**：需要让智能体掌握特定库/框架的最佳实践

**工作原理**：
- `SKILL.md` 监听用户提示中的关键词
- 动态从 `references/` 目录加载内部文档
- 将加载的规则作为"绝对真理"执行

**示例：FastAPI专家技能**
```yaml
# skills/api-expert/SKILL.md
---
name: api-expert
description: FastAPI development best practices and conventions
metadata:
  pattern: tool-wrapper
  domain: fastapi
---

你是 FastAPI 开发专家。请将这些约定应用到用户的代码或问题中。

## 核心约定
加载 'references/conventions.md' 以获取完整的 FastAPI 最佳实践列表。

## 审查代码时
1. 加载约定参考文档
2. 用每一条约定检查用户的代码
3. 对于每一处违规，引用具体规则并给出修复建议
```

✅ **优势**：避免将大量规范硬编码到系统提示，实现上下文的高效管理

---

### 2️⃣ Generator（生成器）
> **核心价值**：通过模板化确保输出结构的一致性

**适用场景**：需要智能体生成格式统一的文档、报告或代码脚手架

**工作原理**：
- `assets/` 目录存放输出模板
- `references/` 目录存放风格指南
- 指令协调模板加载、变量收集、内容填充的全流程

**示例：技术报告生成器**
```yaml
# skills/report-generator/SKILL.md
---
name: report-generator
description: Generates structured technical reports in Markdown
metadata:
  pattern: generator
  output-format: markdown
---

你是一个技术报告生成器。请严格按照以下步骤执行：

Step 1: 加载 'references/style-guide.md' 获取语气和格式规则
Step 2: 加载 'assets/report-template.md' 获取所需的输出结构
Step 3: 向用户询问填充模板所需但缺失的信息
Step 4: 按照风格指南规则填写模板
Step 5: 将完成后的报告作为一份单独的 Markdown 文档返回
```

✅ **优势**：解决"每次输出格式不一致"的痛点，提升专业度与可复用性

---

### 3️⃣ Reviewer（审查器）
> **核心价值**：将"查什么"与"怎么查"解耦，实现评审标准的模块化

**适用场景**：代码审查、安全审计、质量检查等需要结构化反馈的任务

**工作原理**：
- 评审标准存储在 `references/review-checklist.md`
- Agent 加载清单后逐条评分，按严重程度分类输出
- 更换清单即可切换评审领域（如从代码风格→安全合规）

**示例：代码审查器**
```yaml
# skills/code-reviewer/SKILL.md
---
name: code-reviewer
description: Reviews Python code for quality, style, and common bugs
metadata:
  pattern: reviewer
  severity-levels: error,warning,info
---

你是一名 Python 代码审查员。请严格遵循以下审查协议：

Step 1: 加载 'references/review-checklist.md' 获取完整的审查标准
Step 2: 仔细阅读用户的代码，先理解用途再提出批评
Step 3: 将清单中的每条规则应用到代码，对每处违规：
  - 记录行号
  - 标注严重程度：error（必须修复）/warning（建议修复）/info（可考虑）
  - 解释原因并给出具体修复建议
Step 4: 输出结构化审查报告（摘要/发现/评分/前3条建议）
```

✅ **优势**：评审标准可独立维护更新，支持多领域复用，输出结果可量化

---

### 4️⃣ Inversion（反转模式）
> **核心价值**：让Agent从"被动执行"变为"主动访谈"，先收集需求再行动

**适用场景**：需求不明确、需要多轮确认的复杂任务（如项目规划、方案设计）

**工作原理**：
- 通过"门控指令"强制Agent先提问、后执行
- 按预设顺序收集关键信息，避免遗漏
- 在获得完整上下文前，拒绝输出最终结果

**示例：项目规划器**
```yaml
# skills/project-planner/SKILL.md
---
name: project-planner
description: Plans a new software project by gathering requirements first
metadata:
  pattern: inversion
  interaction: multi-turn
---

你正在进行一次结构化需求访谈。在所有阶段完成之前，不要开始构建或设计。

## Phase 1 — 问题发现（一次问一个问题，等回答）
- Q1: "这个项目为用户解决什么问题？"
- Q2: "主要用户是谁？他们的技术水平如何？"
- Q3: "预期规模是多少？"

## Phase 2 — 技术约束（仅当Phase 1完成后）
- Q4: "你用什么部署环境？"
- Q5: "有没有技术栈要求或偏好？"
- ...

## Phase 3 — 综合（所有问题回答完后）
1. 加载模板填充需求
2. 呈现方案并征求反馈
3. 迭代直至用户确认
```

✅ **优势**：避免Agent"猜需求"导致的返工，提升任务完成质量与用户满意度

---

### 5️⃣ Pipeline（流水线）
> **核心价值**：通过硬检查点强制执行多步工作流，防止跳步或遗漏

**适用场景**：步骤严格、容错率低的复杂任务（如文档生成、数据处理流水线）

**工作原理**：
- 指令即工作流定义，明确每一步的输入/输出/校验条件
- 通过"钻石门控"（用户确认）确保关键节点可控
- 按需加载参考资料，保持上下文窗口高效

**示例：文档生成流水线**
```yaml
# skills/doc-pipeline/SKILL.md
---
name: doc-pipeline
description: Generates API documentation through a multi-step pipeline
metadata:
  pattern: pipeline
  steps: "4"
---

你正在运行一个文档生成流水线。请按顺序执行每一步，不要跳过。

## Step 1 — 解析与清单
分析代码提取公开API，呈现清单并请求用户确认

## Step 2 — 生成文档字符串
对每个函数生成符合规范的docstring，**必须经用户确认后才能继续**

## Step 3 — 组装文档
加载模板，编译所有内容为完整API参考文档

## Step 4 — 质量检查
对照检查清单审查，修复问题后再交付最终文档
```

✅ **优势**：确保复杂任务的执行可靠性，支持人工介入关键节点，便于调试与审计

---

## 🧭 如何选择适合的模式？

| 你的需求 | 推荐模式 |
|---------|---------|
| 注入特定库/框架的专业知识 | 🔧 Tool Wrapper |
| 保证输出文档结构一致 | 📄 Generator |
| 对代码进行可量化评审 | 🔍 Reviewer |
| 任务执行前需完整收集需求 | 🔄 Inversion |
| 多步骤任务需严格顺序执行 | ⚙️ Pipeline |

---

## 🔗 模式可组合：1+1>2

这五种模式**并非互斥**，而是可以灵活叠加的工程构件：

- 🔄 **Pipeline + Reviewer**：在流水线末尾添加自我审查步骤
- 📄 **Generator + Inversion**：先用反转模式收集变量，再用生成器填充模板
- 🔧 **Tool Wrapper + 任意模式**：为任何工作流注入领域专业知识

借助 ADK 的 `SkillToolset` 和渐进式加载机制，智能体在运行时只会为实际调用的模式消耗上下文 token，实现效率与能力的平衡。

---

## 💡 核心启示

> **格式只是起点，结构才是终点。**

1. **工程化思维**：将提示词逻辑模块化、可复用、可审计
2. **解耦设计**：分离"规则定义"与"执行逻辑"，提升维护性
3. **可控执行**：通过门控机制确保关键节点的人工介入
4. **组合复用**：像搭积木一样构建复杂智能体工作流

停止将复杂脆弱的指令塞进单个系统提示。分解工作流，应用正确的结构化模式，构建真正可靠的Agent。

---

> 📌 **立即开始**  
> Agent Skills 规范已开源，并在 Google Agent Development Kit (ADK) 中获得原生支持。掌握技能的打包方式与内容设计方法，使用 Google 智能体开发工具包，构建更智能的Agent。

*本文内容整理自 Google Cloud Tech 官方推文，旨在帮助开发者理解并应用先进的Agent Skill设计模式。*