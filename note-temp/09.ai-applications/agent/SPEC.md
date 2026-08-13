# SPEC for note-temp/09.ai-applications/agent/

> **Inherits from**: [../../SPEC.md](../../SPEC.md)
> **Mode**: append + override
> **Updated**: 2026-08-13

---

## 子目录定位

Agent（智能体）MOC：覆盖架构 / 上下文 / 评测 / 执行模式 / 记忆 / 可靠性 / Spec 工具 / 案例 / 编程 Agent / 本体驱动 / 生产实践 / 系统设计 12 个子主题，强调「ReAct vs Plan-Execute 选型 + Memory 分层 + 多 Agent 协作」。

## 从 L1 继承

- G1-G6 通用 6 维度评分
- C4 实战部署指导（"X 场景用 Y 框架"）
- C5 框架对比（ReAct / Plan-Execute / DAG / Multi-Agent）
- C6 性能基准（成功率 / 步数 / Token 消耗）

## 本子目录规则（强特异性）

### 评估维度（追加 L1 维度后）

| # | 维度 | 2 分 | 1 分 | 0 分 |
|---|------|------|------|------|
| A1 | 框架选型 | ReAct vs Plan-Execute vs DAG vs Multi-Agent 四维度对比 + 选型决策树 | 有对比无决策树 | 只讲单一框架 |
| A2 | Memory 设计 | 短期（working）/ 长期（episodic + semantic + procedural）四层架构 + 共享 Memory 模式 | 只讲短期或长期 | 只有 Context Window |
| A3 | 多 Agent 协作 | Supervisor / Peer-to-Peer / Hierarchical 三种模式 + 通信协议 | 有协作无协议 | 单 Agent 为主 |

### 写作要求

- **MOC 索引必备**：MOC README 必须包含 12 个子主题清单表（编号 + 路径 + 一句话摘要）
- **执行模式四分类**：DAG / ReAct / Plan-and-Execute / Multi-Agent 必须给出 6 维度对比（可控性 / 灵活性 / 成本 / 可调试 / 适用任务 / 框架支持）
- **Memory 四层架构**：
  - Working Memory（当前任务上下文）
  - Episodic Memory（历史交互记录）
  - Semantic Memory（事实知识）
  - Procedural Memory（操作技能）
- **可靠性 4 大机制**：失败重试 / 状态回滚 / 超时控制 / 人机协同（Human-in-the-loop）
- **评测 6 维度**：任务完成率 / 步数效率 / Token 成本 / 幻觉率 / 工具调用准确率 / 用户满意度
- **生产级 Agent 系统设计**：高可用架构 + 容量评估 + 容灾 + 监控告警
- **编程 Agent 单独成类**：Claude Code / Codex / OpenCode / OMP 四大工具横评

### 互链要求

- 必须回链 `../prompts/`（Agent Prompt 是 System Prompt 的进化）
- 必须互链 `../rag/`（Agentic RAG 是 RAG 的延伸）
- 必须互链 `../llm-inference/`（Agent 推理性能基础设施）
- 必须互链 `../../08.ai-foundations/`（Transformer / LLM / Embedding 基础）
- Spec 工具类文章必须互链 `superpowers` / Spec-Kit / OpenSpec 三大规范工具

### 反模式

- ❌ 默认所有任务用 Multi-Agent（成本 + 复杂度爆炸）
- ❌ ReAct 用于「需要严格规划」的任务（应改 Plan-and-Execute）
- ❌ 不区分 Working Memory 和 Context Window
- ❌ 生产 Agent 无失败重试（容错缺失）
- ❌ 评测只看任务成功率（忽视成本 / 步数 / 幻觉）