# 📝 Agent Harness 概念全景（合并版）

> 来源：Tony Kipkemboi 推文 + The Importance of Agent Harness in 2026 文章整理
> 合并原因：两篇都讲"Agent Harness 是什么"，按 single-topic 原则合成 1 篇

## 🔑 核心观点

Agent Harness 是 **2025-2026 AI 工程的核心抽象**：在原始代码（Raw Code）和 Agent Framework 之间架起的"控制层"。

### 概念谱系（来自 Tony Kipkemboi）

```
最左端：原始代码（Raw Code）
       ├─ 没有 LLM 参与
       └─ 人类开发者完全控制

中间层：Agent Framework（智能体框架）
       ├─ LangChain / AutoGPT / CrewAI
       ├─ 提供 LLM + 工具调用 + 链式逻辑
       └─ 适合实验和原型

最右端：Agent Harness（智能体管控框架）
       ├─ Claude Code / OpenAI Codex / OpenCode
       ├─ 在生产环境强制约束（上下文管理 / 工具权限 / 错误恢复）
       └─ 适合生产部署
```

## � 为什么需要 Agent Harness？

（来自 The Importance of Agent Harness in 2026）

### 基准测试的困境

传统 Agent 基准（如 SWE-bench）侧重"能不能完成任务"，但**忽略了生产环境的硬约束**：
- 上下文长度管理（防止 LLM 走偏）
- 工具调用的安全性（防止删除生产数据）
- 长时运行任务的可靠性（防止中途崩溃）

### 构建智能体的"苦涩教训"（The Bitter Lesson）

历史经验：
- 1960s AI：手工特征 → 失败
- 1990s：专家系统 → 失败
- 2010s：深度学习 → **通用方法 + 大算力 = 胜利**
- 2025s：**通用框架 + 强 Harness = 胜出**

→ Agent 工程要走"通用框架（GPT-4/Claude）+ 强 Harness"路线，不能只靠手工调 prompt

## � 实践意义

- 选择 Agent Framework 时考虑：**这个框架的 Harness 能力怎么样？**
- 不要被"功能多"迷惑，要看"生产约束"
- Claude Code / Codex 等"自带 Harness"的工具越来越主流

---

> 📚 知识来源：
> - README1.md（Tony Kipkemboi 推文整理）
> - README2.md（The Importance of Agent Harness in 2026）
