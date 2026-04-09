# 长效智能体架构：如何让 AI Agent 跨多轮上下文持续高效工作
## —— Anthropic 工程团队技术解析

> 本文整理自 Anthropic 官方博客 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)，聚焦于解决 AI Agent 在长周期、多会话任务中的核心挑战。

---

## 🔍 核心问题：为什么长周期 Agent 容易"失忆"？

随着 AI Agent 能力不断提升，开发者开始让它们承担需要数小时甚至数天才能完成的复杂任务。然而，**让 Agent 在多个上下文窗口（context windows）之间持续、一致地推进工作，仍是一个未解难题**。

### 根本挑战
- 每次新会话开始时，Agent 都"失忆"了——无法记住之前会话的内容
- 类比：就像软件项目由轮班工程师协作，但每位新工程师都不了解上一班的工作进展
- 即使使用上下文压缩（compaction）技术，也无法完美传递清晰的指令给下一个 Agent

### 常见失败模式
1. **"一锅端"倾向**：Agent 试图一次性完成整个应用，结果在中途耗尽上下文，留下半成品和未文档化的代码
2. **过早宣告完成**：在部分功能已实现后，新会话的 Agent 看到已有进展，误判项目已完成
3. **测试不充分**：Agent 修改代码后，未能进行端到端验证，导致功能实际不可用

---

## 🛠️ 解决方案：双阶段架构设计

Anthropic 团队提出了一套受人类工程实践启发的**两阶段架构**，使 Claude Agent SDK 能够有效跨多轮上下文工作：

```
┌─────────────────────────┐
│  1️⃣ Initializer Agent   │
│  （初始化智能体）        │
│  • 创建基础环境          │
│  • 生成 feature_list.json│
│  • 编写 init.sh 脚本     │
│  • 初始化 git 仓库       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  2️⃣ Coding Agent        │
│  （编码智能体）          │
│  • 每次会话专注一个功能  │
│  • 增量开发 + 清晰提交   │
│  • 更新进度日志          │
│  • 保持代码库"干净状态"  │
└─────────────────────────┘
```

### 阶段一：初始化智能体（Initializer Agent）

首个会话使用专用提示词，要求模型完成以下任务：

| 产出物 | 作用 |
|--------|------|
| `init.sh` 脚本 | 一键启动开发环境，运行基础测试 |
| `claude-progress.txt` | 记录各 Agent 会话的工作日志 |
| `feature_list.json` | 详细功能清单，所有功能初始标记为"未通过" |
| 初始 git commit | 清晰记录项目起点和文件结构 |

#### 📋 功能清单设计（feature_list.json 示例）
```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [
    "Navigate to main interface",
    "Click the 'New Chat' button",
    "Verify a new conversation is created",
    "Check that chat area shows welcome state",
    "Verify conversation appears in sidebar"
  ],
  "passes": false
}
```

> 💡 关键设计：使用 JSON 格式（而非 Markdown），因为模型更不容易意外修改或覆盖结构化数据；严格禁止 Agent 删除或编辑测试用例。

### 阶段二：编码智能体（Coding Agent）

后续每个会话遵循"增量推进"原则：

1. **单功能聚焦**：每次只实现功能清单中的一个条目
2. **提交规范**：用描述性 git commit 记录变更，便于回溯
3. **进度同步**：在 `claude-progress.txt` 中撰写会话摘要
4. **状态清理**：确保代码可合并到主分支——无重大 bug、结构清晰、文档完整

---

## 🧪 关键实践：测试与启动协议

### 端到端测试至关重要
- 仅靠单元测试或 `curl` 命令不足以验证功能
- 显式提示 Agent 使用浏览器自动化工具（如 Puppeteer），模拟真实用户操作
- 实验表明：提供测试工具后，Agent 能识别并修复仅靠代码审查难以发现的 bug

### 每轮会话的"启动检查清单"
每个 Coding Agent 开始前执行：
```bash
1. pwd                    # 确认工作目录
2. git log + 读取进度文件  # 了解近期工作
3. 读取 feature_list.json # 选择下一个最高优先级功能
4. 运行 init.sh + 基础 E2E 测试 # 验证环境状态
5. 开始编码...
```

> ✅ 优势：节省 Token（无需重复推理测试策略），提升会话间连续性，降低"重复造轮子"风险

---

## 📈 效果与启示

采用该架构后，Claude Agent 能够：
- ✅ 跨数十个会话持续开发，最终构建出生产级 Web 应用
- ✅ 避免"一锅端"和"过早完成"两类典型失败
- ✅ 通过结构化日志和 git 历史实现"会话间知识传递"
- ✅ 在端到端测试支持下显著提升代码质量

---

## 🔮 未来方向

该方案虽有效，但仍有开放问题值得探索：

| 方向 | 潜在价值 |
|------|----------|
| **多智能体协作架构** | 专用测试 Agent、QA Agent、代码清理 Agent 可能比通用 Agent 更高效 |
| **领域泛化** | 将经验迁移到科研、金融建模等其他长周期任务场景 |
| **自动化程度提升** | 减少人工提示工程，让 Agent 自主规划功能拆解与测试策略 |
| **记忆机制增强** | 结合外部向量数据库或知识图谱，实现更鲁棒的跨会话记忆 |

---

## 💎 核心结论

> **长周期 Agent 的成功，不在于模型本身更"聪明"，而在于为其设计一套符合工程规律的"工作框架"（harness）**。

Anthropic 的实践表明：
1. **结构化上下文 > 原始上下文长度**：清晰的功能清单、进度日志、git 历史，比单纯扩大 context window 更有效
2. **人类工程智慧可迁移**：增量开发、代码审查、自动化测试等经典实践，对 AI Agent 同样关键
3. **提示工程即系统设计**：好的 prompt 不是"让模型猜"，而是"为模型搭建可执行的脚手架"

这套方法论不仅适用于 Web 开发，也为构建可靠、可维护的长周期 AI 系统提供了可复用的设计范式。

---

📌 **延伸资源**
- Claude Agent SDK 快速入门：[官方文档](https://docs.anthropic.com/claude/docs/claude-agent-sdk)
- 示例代码仓库：文中提及的 quickstart 可在 Anthropic GitHub 获取

> *整理说明：本文基于 Anthropic 官方博客内容提炼，保留核心技术观点，优化中文表达与结构呈现，便于工程团队快速理解与实践。*