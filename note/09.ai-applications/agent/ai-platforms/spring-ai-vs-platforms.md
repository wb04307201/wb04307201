# Spring AI vs 编排平台：代码优先与低代码的边界

> ⬅️ [返回 AI 平台](README.md) | [Dify](dify.md) | [Coze](coze.md) | [LangGraph](langgraph.md) | [BPMN+AI 融合](../../04-architecture/bpmn-ai-integration.md) | [深度对比长文](../../04-architecture/spring-ai-vs-dify.md) | [11 AI 知识体系](../../README.md)

## 🎯 一句话定位

**Spring AI 不是 Dify 的竞品，而是不同的抽象层级**——Dify 是"低代码 AI 应用平台"，Spring AI 是"Java 团队的 AI 框架"。本文讲清**何时用平台、何时自己写代码、何时混合**，深度版见 [04-architecture/spring-ai-vs-dify.md](../../04-architecture/spring-ai-vs-dify.md)。

---

## 一、定位差异

| 维度 | Dify / Coze | **Spring AI** |
|------|-------------|---------------|
| **形态** | 低代码平台 + DSL YAML | Java 框架 + 注解 + Spring Boot Starter |
| **目标用户** | 产品 / 运营 / 全栈 | Java 后端工程师 |
| **抽象层级** | UI 配置 + 工作流编排 | 业务代码 + Spring 容器 |
| **RAG 能力** | 内置完整管道（摄取/分段/检索/重排） | 组件化拼装（DocumentReader / Embedding / VectorStore / Retriever） |
| **私有化** | AGPL 免费 / 企业版付费 | Apache 2.0，自部署无限制 |
| **业务代码量** | 0 行业务代码 | 200-500 行 Java |
| **上线时间** | 1-3 天 MVP | 1-2 周 |
| **调试方式** | 平台 UI 单步追踪 | IDE + 日志 + Actuator + Langfuse |
| **业务系统集成** | API / Webhook | 直接调业务 Service（事务/权限/Saga 继承） |
| **典型代表** | Dify（国内）/ Coze（字节） | Spring AI（Spring 官方）/ Spring AI Alibaba（阿里） |

---

## 二、决策清单（速查版）

### ✅ 选 Dify / Coze 的场景

- 1-2 周内要上线 MVP
- 产品 / 运营主导，**无 Java 后端**
- 标准化客服 / 知识库问答
- 私有化但**不想写代码**
- 字节系生态深绑定（抖音/飞书/豆包）

### ✅ 选 Spring AI 的场景

- **已有 Spring Boot 微服务架构**
- 需要直接调业务 Service（订单/用户/库存/权限）
- **强权限 / 审计 / 合规**（金融/医疗/政务）
- 团队 Java 后端为主，不想跨语言栈
- 需要**完全可控的 RAG 流程**（自定义分段/重排/混合检索）

### ✅ 混合场景（推荐先看这条）

- **Dify 做前端 + Spring AI 做执行引擎**：Dify 工作流节点调 Spring AI HTTP API（外部 API 模式）
- **Spring AI 主流程 + Dify 知识库子流**：Spring AI 用 Dify Workflow API 调标准化知识库
- **MCP 互通**：Dify v1.9.2+ 原生 MCP Server/Client，Spring AI MCP 客户端对接

---

## 三、与 ai-platforms 6 平台的关系

| 平台 | 形态 | 业务代码量 | 何时选 |
|------|------|----------|--------|
| Dify | 低代码 DSL | 0 | 标准化 + 私有化 + 快速上线 |
| Coze | 表单 + 工作流 | 0 | 字节生态 + C 端分发 |
| LangGraph | Python 框架 | 300-800 行 Python | 复杂 Agent + 状态可回放 |
| n8n | 工作流自动化 | 0 | 系统集成 / 跨 SaaS |
| FastGPT | 知识库 + Flow | 少量配置 | 知识库问答为主 |
| RAGFlow | RAG 引擎 | 少量配置 | 深度文档理解 |
| **Spring AI** | **Java 框架** | **200-500 行 Java** | **Java 微服务 + 强业务集成** |

> Spring AI 与 LangGraph 是同一抽象层级（代码优先）的**Java vs Python** 双胞胎，选型看团队语言栈。

---

## 四、一句话答案

> **有 Dify 为什么还要 Spring AI？** 因为你的系统已经是 Spring Boot 微服务、知识库问答需要直接读订单/用户/权限等业务数据、合规审计要求全链路追踪——这些场景 Dify 的"平台抽象"反而是累赘，Spring AI 的"代码 + 容器"才是正解。
>
> **那 Dify 还有用吗？** 有。产品/运营自助搭建、知识库问答的快速原型、字节生态 C 端分发——Dify 仍然是最优解。**真正的错误是"非此即彼"——Java 团队完全可以用 Dify 做编辑器，Spring AI 做执行引擎，二者通过 API / MCP 互通。**

---

## 🤔 思考

1. **Dify vs Spring AI 是"非此即彼"吗？** 不是。两者抽象层级不同，可通过 Dify External API 或 MCP 互通。Java 团队最常见的组合是"Spring AI 主流程 + Dify 知识库子流"。
2. **Spring AI 比 LangChain4j 强在哪？** Spring 官方背书 + 标准化抽象（`ChatClient`）+ 阿里增强版（Spring AI Alibaba 提供 Agent Framework）。LangChain4j 更灵活但 Spring AI 更"Spring"。
3. **Dify 的知识库能力是否够用？** 80% 标准化场景够用。20% 需要：自定义文档结构（合同条款）、自定义分段（法律条文）、混合检索（关键词 + 向量 + 图谱）、细粒度权限——这些场景 Spring AI 更合适。
4. **团队到底该选哪个？** **Java 为主 + 复杂业务集成 → Spring AI**；**产品/运营为主 + 快速上线 → Dify**。不要为了"先进"硬上 LangGraph 或 Spring AI。

---

## 相关章节

- ⬅️ [返回 AI 平台](README.md) — 6 平台对比矩阵与决策树
- ➡️ [深度对比长文](../../04-architecture/spring-ai-vs-dify.md) — 7 维度决策 + 代码示例 + 混合架构
- [Dify](dify.md) — 低代码 DSL 优先 + 私有化首选
- [Coze](coze.md) — 字节系国内最强生态
- [LangGraph](langgraph.md) — Python 代码优先复杂 Agent 框架
- [BPMN+AI 融合](../../04-architecture/bpmn-ai-integration.md) — AI + BPMN 跨界决策范式
- [大模型应用框架](../frameworks/llm-app/README.md) — Spring AI / LangChain4j / LangChain / LlamaIndex 框架对比