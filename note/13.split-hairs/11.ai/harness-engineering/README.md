# Harness Engineering：让 Agent 自我约束的工程范式

> 2026 年 AI 工程第三阶段：当 Agent 越来越强，怎么"驯服"它？Harness Engineering 是"用规范和流程约束 Agent"的工程实践。

## 一、核心结论（TL;DR）

| 阶段 | 关注点 | 主导者 |
|------|--------|--------|
| Prompt Engineering | 怎么写好一句提示 | 人类 |
| Context Engineering | 怎么管理上下文 | Agent |
| **Harness Engineering** | 怎么约束 Agent 行为 | 规范/流程 |
| Loop Engineering | 怎么循环调用 Agent | Agent + Harness |

> 一句话：**Harness Engineering 是"给 Agent 套上缰绳"——让它按照你期望的方式工作，但不限制它的能力**。

---

## 二、什么是 Harness？

**Harness** 本意是"马具"（套在马身上的缰绳、嚼子、马鞍）。在 AI 工程领域，借喻为"约束 Agent 行为的规范和工具"。

```
┌─────────────────────────────────────┐
│  Harness =                          │
│    + 规范（Rules / Specs）           │
│    + 流程（Workflow / Pipeline）     │
│    + 工具（Tools / Hooks）           │
│    + 反馈（Feedback / Evaluation）   │
└─────────────────────────────────────┘
```

---

## 三、Harness vs Prompt vs Context

| 维度 | Prompt | Context | Harness |
|------|--------|---------|---------|
| 关注点 | 怎么问 | 给什么信息 | 怎么约束 |
| 范围 | 单条输入 | LLM 看到的所有信息 | Agent 的工作环境 |
| 例子 | "请帮我写代码" | 系统提示 + 工具 + 历史 | OpenSpec 规范 + CI 流程 + 自动化测试 |
| 主体 | 用户 | Agent 编排 | 团队/组织 |

---

## 四、4 大 Harness 类型

### 1. 规范型 Harness（OpenSpec / Spec Kit）

让 Agent 在写代码前先读"项目规范"：

```
项目根目录/
  ├── .claude/
  │   ├── rules.md          # 编码规范
  │   ├── spec.md           # 功能规范
  │   ├── architecture.md   # 架构决策记录
  │   └── CLAUDE.md         # Agent 启动时读取的规则
```

**OpenSpec** 是 GitHub 推出的 Agent 规范协议，让团队统一管理 Agent 的工作准则。

### 2. 流程型 Harness（CI/CD Pipeline）

让 Agent 必须经过自动化流程：

```
Code Generate (Agent)
    ↓
Lint + Type Check
    ↓
Unit Test
    ↓
Code Review (AI 或人类)
    ↓
Integration Test
    ↓
Deploy
```

### 3. 工具型 Harness（Hooks / Callbacks）

让 Agent 在关键节点自动触发检查：

```python
@agent.before_tool_call("write_file")
def validate_code_change(tool, args):
    """写文件前检查是否违反编码规范"""
    if not linter.check(args['content']):
        raise Exception("代码违反规范")

@agent.after_tool_call("run_command")
def validate_command(tool, result):
    """运行命令后检查是否产生副作用"""
    if "rm -rf" in result.output:
        raise Exception("禁止危险命令")
```

### 4. 反馈型 Harness（Evaluation Loop）

让 Agent 持续评估自己的输出：

```
Agent 输出 → 自动评估（单元测试 + LLM-as-Judge）→ 不通过则重试
```

---

## 五、OpenSpec / Spec Kit 是什么？

**OpenSpec**（Open Specification）是一种 Agent 规范协议，让团队用标准化的方式定义：

- **功能规范**：每个 feature 的需求、接口、数据结构
- **编码规范**：命名、注释、测试覆盖率
- **架构决策**：技术选型、依赖、设计模式

**核心思想**：让 Agent 像新员工一样"入职"——读规范 → 理解项目 → 按规范工作。

```
新员工入职流程：
1. 读员工手册（OpenSpec）
2. 读项目文档（README / 架构图）
3. 理解代码规范（.claude/rules.md）
4. 在指导下完成任务
5. 提交 PR 接受 review

AI Agent 入职流程：
1. 读 OpenSpec 规范
2. 加载 CLAUDE.md
3. 理解 .claude/rules.md
4. 在 Harness 约束下完成任务
5. 通过 CI/CD 流水线
```

---

## 六、Harness Engineering 的 4 大原则

### 1. 显式优于隐式

- ❌ 让 Agent "自己理解"项目规范
- ✅ 把规范写成 `.claude/rules.md`，Agent 启动时强制读取

### 2. 自动化优于人工

- ❌ 让人类 review 每行 AI 代码
- ✅ 让 Linter + 单元测试 + AI Review 自动检查

### 3. 可观测优于黑盒

- ❌ Agent 自己跑任务，看不到中间过程
- ✅ Trace / Logging / Evaluation 全程可观测

### 4. 渐进优于一步到位

- ❌ 让 Agent 直接完成整个 feature
- ✅ 拆解任务 → 逐步执行 → 每步可检查

---

## 七、面试陷阱

### 陷阱 1：以为 Harness = Prompt

- **真相**：Harness 是 Agent 工作环境的"基础设施"，比 Prompt 范围大得多

### 陷阱 2：以为 Harness 限制 Agent 能力

- **真相**：好的 Harness 让 Agent 在约束下发挥更强能力，而不是变弱

### 陷阱 3：以为 OpenSpec 只是文档

- **真相**：OpenSpec 是 Agent 可读的规范协议，包含自动校验机制

---

## 八、面试话术模板

> Harness Engineering 是 2026 年 AI 工程第三阶段，演进路径是 Prompt → Context → Harness → Loop。
>
> Harness 借喻"马具"，是"约束 Agent 行为的规范和工具"。包含 4 大类型：
>
> 1. **规范型**：OpenSpec / Spec Kit，Agent 启动时读取项目规范
> 2. **流程型**：CI/CD Pipeline，强制走自动化测试
> 3. **工具型**：Hooks / Callbacks，在关键节点自动检查
> 4. **反馈型**：Evaluation Loop，持续评估输出质量
>
> 核心原则：显式优于隐式、自动化优于人工、可观测优于黑盒、渐进优于一步到位。
>
> 我们团队用 OpenSpec + Cursor + GitHub Actions，让 AI 写代码时必须遵守项目规范、自动跑测试、AI 互相 review。

---

## 九、相关章节

- 同栏目：[`prompt-engineering`](../prompt-engineering/README.md) — Prompt Engineering
- 同栏目：[`context-engineering`](../context-engineering/README.md) — Context Engineering
- 同栏目：[`loop-engineering`](../loop-engineering/README.md) — Loop Engineering
- 同栏目：[`agent-dag-vs-react`](../agent-dag-vs-react/README.md) — DAG vs ReAct
- 主模块：[`11.ai/03-engineering`](../../../../11.ai/03-engineering/README.md) — AI 工程实践

---

> 📅 2026-06-28 · 咬文嚼字 · AI 新概念 · ⭐⭐⭐⭐（2026 面试热点）