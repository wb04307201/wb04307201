# AI 知识体系

> 从基础概念到行业落地，系统化理解人工智能技术栈。

本目录按 **知识层级递进** 组织，从理论到实践，从底层算法到上层应用。

---

## 目录导航

| 层级 | 目录 | 内容 |
|------|------|------|
| **L1 基础概念** | [01-fundamentals](01-fundamentals/) | AI/ML/DL/LLM 基础定义、神经网络层次、架构对比 |
| **L2 技术栈** | [02-technology-stack](02-technology-stack/) | LLM 生态全景(61核心概念)、多模态、Prompt/Context/Harness/Loop 工程、显存估算 |
| **L3 工程实践** | [03-engineering](03-engineering/) | 深度学习框架、应用开发框架、计算平台、本地部署、[AI 编排平台](03-engineering/ai-platforms/)（Dify/Coze/LangGraph）、Agent 4 阶段工程演进 |
| **L4 架构设计** | [04-architecture](04-architecture/) | 智能系统分层架构、[AI + BPMN 融合](04-architecture/bpmn-ai-integration.md)、DAG vs ReAct Agent 架构选型、2026技术趋势 |
| **L5 行业应用** | [05-applications](05-applications/) | 汽车行业落地、具身智能、AI 编程研发效能度量 |
| **L6 前沿研究** | [06-research](06-research/) | 沉思模型(Rumination)等前沿探索 |
| **教学课程** | [training](training/) | Spring AI 实战教学课程 |

## 知识脉络

```mermaid
graph TD
    L1["L1 基础概念<br/>AI/ML/DL/LLM 定义"] --> L2["L2 技术栈全景<br/>61 核心概念 · 多模态 · Prompt/Context/Harness/Loop 工程"]
    L2 --> L3["L3 工程实践<br/>框架 · 计算平台 · 部署 · Agent 4 阶段"]
    L3 --> L4["L4 架构设计<br/>智能系统分层 · BPMN+AI"]
    L4 --> L5["L5 行业应用<br/>汽车 · 具身智能"]
    L5 --> L6["L6 前沿研究<br/>沉思模型 · 新方向"]
    L3 --> Training["Spring AI 实战<br/>16 课培训课程"]
```

## 速查表

| 概念 | 核心要点 | 典型场景 |
|------|---------|---------|
| **LLM** | 大语言模型，Transformer 架构，预训练 + 微调 | 文本生成、对话 |
| **Transformer** | Self-Attention + 位置编码，并行计算 | 所有现代 LLM 基座 |
| **Token** | 模型最小处理单元，BPE/WordPiece 分词 | 计费与上下文长度 |
| **Embedding** | 将文本映射到高维向量空间 | 语义搜索、RAG |
| **RAG** | 检索增强生成，向量检索 + LLM 生成 | 知识库问答 |
| **Prompt Engineering** | 通过提示词引导 LLM 输出（CoT/Few-shot/Role） | 无需微调的提升效果 |
| **Context Engineering** | 为 LLM 提供完整的"上下文"（系统提示+工具+历史+RAG+记忆） | Agent 时代的主流范式 |
| **Harness Engineering** | 用规范/流程/工具约束 Agent 行为（OpenSpec / CI/CD） | Agent 自我约束工程 |
| **Loop Engineering** | 循环调用 Agent 直到任务完成（Task+Verifier+Feedback） | 探索性任务自动化 |
| **Fine-tuning** | 在特定数据上继续训练（LoRA/QLoRA 高效微调） | 领域适配 |
| **Agent** | LLM + 工具调用 + 记忆 + 规划 | 自主完成任务 |
| **DAG vs ReAct** | ReAct 适合探索 / DAG 适合确定性流程 | Agent 架构选型 |
| **DORA 4 指标** | 部署频率/前置时间/失败率/MTTR | AI 时代的研发效能度量 |
| **SPACE 5 维度** | Satisfaction/Performance/Activity/Communication/Efficiency | 开发者生产力多维度量 |
| **代码流失率** | 6 周内被修改/重写/删除的代码比例 | AI 时代最被忽视的健康指标 |
| **MCP** | Model Context Protocol，标准化工具接入协议 | Agent 工具扩展 |
| **MoE** | Mixture of Experts，稀疏激活提升效率 | GPT-4 / Mixtral |

## 学习路径

- **初学者**：L1 → L2 建立认知框架
- **工程师**：L2 → L3 掌握落地能力
- **架构师**：L3 → L4 系统级设计
- **行业研究者**：L5 → L6 探索未来方向

## 相关章节

- 关联：[`04.system-design`](../04.system-design/) — 通用系统设计（AI 系统也遵循分布式/高可用原则）
- 关联：[`06.spring`](../06.spring/) — Spring 生态（Spring AI 的底层支撑）
- 关联：[`07.workflow`](../07.workflow/) — 工作流引擎（BPMN + AI Agent 融合）
- 面试：[`13.split-hairs/11.ai`](../13.split-hairs/11.ai/README.md) — 14 篇 AI 面试深挖（5 篇纯面试题 + 9 篇主模块配套精炼版）

## 开源参考

| 项目 | 说明 | 链接 |
|------|------|------|
| Spring AI | Spring 官方 AI 集成框架 | [spring.io/projects/spring-ai](https://spring.io/projects/spring-ai) |
| LangChain | LLM 应用开发框架（Python/JS） | [langchain.com](https://www.langchain.com) |
| Dify | AI 应用编排平台 | [dify.ai](https://dify.ai) |
| Ollama | 本地 LLM 运行工具 | [ollama.com](https://ollama.com) |
| Qdrant | 向量数据库 | [qdrant.tech](https://qdrant.tech) |
| Milvus | 开源向量数据库 | [milvus.io](https://milvus.io) |
| MCP | Model Context Protocol | [modelcontextprotocol.io](https://modelcontextprotocol.io) |

---

← [返回笔记目录](../README.md)
